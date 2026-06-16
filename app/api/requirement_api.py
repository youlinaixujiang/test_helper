import os
import re
import tempfile
import urllib.request
import urllib.error
from fastapi import APIRouter, HTTPException, UploadFile, File
from app.models.requirement import RequirementRequest, URLCheckRequest
from app.agents.requirement_agent import requirement_agent
from app.generators.report_generator import report_generator
from app.core.doc_parser import doc_parser

# Selenium 用于渲染 SPA 页面
_selenium_available = False
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    _selenium_available = True
except ImportError:
    pass

router = APIRouter(prefix="/api/v1/requirement", tags=["需求解析"])


def _fetch_page(url: str) -> dict:
    """抓取网页，提取标题、文本内容，并发现 API 路径。
    对于 SPA 页面会自动使用 Selenium 渲染获取内容。"""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            content_type = resp.headers.get("Content-Type", "")
            html = resp.read().decode("utf-8", errors="ignore")

        # 解析 base URL
        parsed_base = urllib.request.urlparse(url)
        base_origin = f"{parsed_base.scheme}://{parsed_base.netloc}"

        # 提取 title
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else "未知标题"

        # ---- 发现 API 路径 ----
        api_hints = _discover_api_paths(html, base_origin)

        # 提取纯文本
        text_html = html
        text_html = re.sub(r"<script[^>]*>.*?</script>", "", text_html, flags=re.IGNORECASE | re.DOTALL)
        text_html = re.sub(r"<style[^>]*>.*?</style>", "", text_html, flags=re.IGNORECASE | re.DOTALL)
        text_html = re.sub(r"<head[^>]*>.*?</head>", "", text_html, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text_html)
        text = re.sub(r"\s+", " ", text).strip()

        # SPA 检测：静态文本为空或极少（如只有 <div id="app"></div>）
        if len(text) < 200 and _selenium_available:
            rendered = _fetch_rendered_page(url)
            if rendered.get("text"):
                text = rendered["text"]
                # 合并 Selenium 发现的 API 路径
                rendered_hints = rendered.get("api_hints", [])
                existing_paths = {h["path"] for h in api_hints}
                for h in rendered_hints:
                    if h["path"] not in existing_paths:
                        api_hints.append(h)

        text = text[:8000]

        return {
            "accessible": True,
            "title": title,
            "text": text,
            "url": url,
            "api_hints": api_hints,
        }
    except urllib.error.HTTPError as e:
        return {"accessible": False, "error": f"HTTP {e.code}: 页面无法访问"}
    except urllib.error.URLError as e:
        return {"accessible": False, "error": f"连接失败: {str(e.reason)}"}
    except Exception as e:
        return {"accessible": False, "error": f"请求异常: {str(e)}"}


def _fetch_rendered_page(url: str) -> dict:
    """使用 Selenium Headless Chrome 渲染 SPA 页面，提取可见文本和 API 路径"""
    result = {"text": "", "api_hints": []}
    driver = None
    try:
        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        driver = webdriver.Chrome(options=opts)
        driver.set_page_load_timeout(20)
        driver.get(url)

        # 等待页面渲染完成
        WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # 额外等待 JS 渲染
        import time
        time.sleep(2)

        # 获取可见文本
        body = driver.find_element(By.TAG_NAME, "body")
        text = body.text.strip()
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        result["text"] = text[:8000]

        # 从渲染后的页面中提取 API 路径
        rendered_html = driver.page_source
        parsed_base = urllib.request.urlparse(url)
        base_origin = f"{parsed_base.scheme}://{parsed_base.netloc}"
        result["api_hints"] = _discover_api_paths(rendered_html, base_origin)

    except Exception:
        pass
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

    return result


def _discover_api_paths(html: str, base_origin: str) -> list[dict]:
    """从 HTML 中发现可能的 API 路径"""
    found = {}  # path → {method, sources}

    # 1. 提取 href/src 属性中的路径
    for m in re.finditer(r"""(?:href|src)\s*=\s*["']([^"']+)["']""", html, re.IGNORECASE):
        path = m.group(1)
        if _is_api_like(path):
            method = _guess_method(path)
            if path not in found:
                found[path] = {"path": path, "method": method, "sources": []}
            found[path]["sources"].append("href/src")

    # 2. 在 <script> 块中查找 fetch/axios/ajax URL
    script_blocks = re.findall(r"<script[^>]*>(.*?)</script>", html, re.IGNORECASE | re.DOTALL)
    for block in script_blocks:
        # fetch("/api/xxx") 或 fetch('/api/xxx')
        for m in re.finditer(r"""fetch\s*\(\s*["']([^"']+)["']""", block):
            path = m.group(1)
            if _is_api_like(path) and path not in found:
                method = _guess_method(path)
                found[path] = {"path": path, "method": method, "sources": ["fetch"]}

        # axios.get("/api/xxx") / axios.post("/api/xxx")
        for m in re.finditer(r"""axios\.(get|post|put|delete|patch)\s*\(\s*["']([^"']+)["']""", block):
            method = m.group(1).upper()
            path = m.group(2)
            if _is_api_like(path) and path not in found:
                found[path] = {"path": path, "method": method, "sources": ["axios"]}

        # $.ajax / $.get / $.post
        for m in re.finditer(r"""\$\.(?:ajax|get|post|put|delete)\s*\(\s*\{?\s*url\s*:\s*["']([^"']+)["']""", block):
            path = m.group(1)
            if _is_api_like(path) and path not in found:
                method_map = {"get": "GET", "post": "POST", "put": "PUT", "delete": "DELETE"}
                method = method_map.get(re.search(r"\$\.(\w+)", block).group(1), "GET") if re.search(r"\$\.(\w+)", block) else "GET"
                found[path] = {"path": path, "method": method, "sources": ["jquery"]}

        # 普通 URL 字符串模式："/api/xxx", "/v1/xxx"
        for m in re.finditer(r"""["']((?:/api/|/v\d+/|/graphql)[^"'\s]+)["']""", block):
            path = m.group(1)
            if path not in found:
                found[path] = {"path": path, "method": "GET", "sources": ["string-literal"]}

    # 3. 尝试探测常见 API 文档端点
    common_docs = ["/api-docs", "/swagger.json", "/openapi.json", "/swagger-resources", "/v2/api-docs", "/v3/api-docs"]
    for doc_path in common_docs:
        full_url = base_origin + doc_path
        try:
            doc_req = urllib.request.Request(full_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(doc_req, timeout=5) as doc_resp:
                if doc_resp.status == 200:
                    doc_data = doc_resp.read().decode("utf-8", errors="ignore")
                    # 从 Swagger/OpenAPI 文档中提取路径
                    _extract_swagger_paths(doc_data, found)
                    break  # 找到一个就够了
        except Exception:
            continue

    # 排序：API 路径优先，按路径名排序
    result = sorted(found.values(), key=lambda x: (0 if "/api/" in x["path"] else 1, x["path"]))
    return result[:30]  # 最多 30 条


def _is_api_like(path: str) -> bool:
    """判断路径是否像 API 端点"""
    path = path.strip()
    # 排除明显不是 API 的
    if not path or path.startswith("#") or path.startswith("javascript:") or path.startswith("mailto:"):
        return False
    if path.startswith("http") and "api" not in path.lower() and "/v" not in path:
        return False
    # 匹配 API 特征
    api_patterns = [r"/api/", r"/v\d+/", r"/graphql", r"\.json$", r"\.xml$", r"/rest/", r"/service/"]
    return any(re.search(p, path, re.IGNORECASE) for p in api_patterns)


def _guess_method(path: str) -> str:
    """根据路径名推测 HTTP 方法"""
    path_lower = path.lower()
    if any(w in path_lower for w in ["login", "auth", "register", "save", "create", "add", "update", "upload", "submit", "post"]):
        return "POST"
    if any(w in path_lower for w in ["delete", "remove"]):
        return "DELETE"
    if any(w in path_lower for w in ["put", "edit", "modify"]):
        return "PUT"
    return "GET"


def _extract_swagger_paths(doc_text: str, found: dict):
    """从 Swagger/OpenAPI JSON 中提取 API 路径"""
    try:
        import json
        spec = json.loads(doc_text)
        paths = spec.get("paths", {})
        for path, methods in paths.items():
            if isinstance(methods, dict):
                for method, detail in methods.items():
                    if method in ("get", "post", "put", "delete", "patch"):
                        if path not in found:
                            found[path] = {"path": path, "method": method.upper(), "sources": ["swagger"]}
    except Exception:
        pass


@router.post("/parse")
async def parse_requirement(req: RequirementRequest):
    """解析测试需求，支持基于 URL 的上下文分析"""
    try:
        # 如果提供了 URL 且可访问，将页面内容作为附加上下文
        page_context = None
        if req.url:
            page_info = _fetch_page(req.url)
            if page_info["accessible"]:
                page_context = {
                    "url": page_info["url"],
                    "title": page_info["title"],
                    "content": page_info["text"][:3000],
                    "api_hints": page_info.get("api_hints", []),
                }

        result = requirement_agent.parse(
            content=req.content,
            feedback=req.feedback,
            previous_result=req.previous_result,
            url=req.url,
            page_context=page_context,
        )
        return {"success": True, "data": result, "page_context": page_context}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    """上传需求文档，返回解析后的文本内容"""
    try:
        content_bytes = await file.read()
        size_mb = len(content_bytes) / (1024 * 1024)
        if size_mb > doc_parser.MAX_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制（最大 {doc_parser.MAX_SIZE_MB} MB）",
            )

        suffix = os.path.splitext(file.filename or "unknown.txt")[1].lower()
        if suffix not in doc_parser.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式: {suffix}，支持: {', '.join(doc_parser.ALLOWED_EXTENSIONS)}",
            )

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(content_bytes)
            tmp_path = tmp.name

        try:
            text = doc_parser.parse(tmp_path, file.filename)
        finally:
            os.unlink(tmp_path)

        return {
            "success": True,
            "data": {
                "filename": file.filename,
                "size_mb": round(size_mb, 2),
                "content": text,
                "char_count": len(text),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-url")
async def check_url(req: URLCheckRequest):
    """检测 URL 是否可访问，返回页面摘要"""
    try:
        result = _fetch_page(req.url)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save")
async def save_requirement(data: dict):
    """保存需求解析结果到本地"""
    try:
        filepath = report_generator.save_json(data, "testcases", "requirement")
        return {"success": True, "filepath": filepath}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
