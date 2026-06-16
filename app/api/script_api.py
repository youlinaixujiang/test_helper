import os
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.config import settings
from app.generators.script_generator import script_generator

router = APIRouter(prefix="/api/v1/script", tags=["脚本生成"])


class ScriptGenerateRequest(BaseModel):
    script_type: str  # api / ui / jmeter
    testcases: list
    base_url: Optional[str] = "http://localhost:8080"
    page_url: Optional[str] = "http://localhost:8080"
    api_hints: Optional[list] = []
    api_doc: Optional[str] = ""


class ScriptSaveRequest(BaseModel):
    code: str
    script_type: str
    filename: Optional[str] = None


class RunJmeterRequest(BaseModel):
    jmx_filepath: str
    base_url: Optional[str] = "http://localhost:8080"


@router.post("/generate")
async def generate_script(req: ScriptGenerateRequest):
    """生成测试脚本"""
    try:
        # 类型校验
        if req.script_type == "api" and not req.api_doc:
            raise HTTPException(status_code=400, detail="接口测试需要提供接口文档（api_doc）")
        if req.script_type == "ui" and not req.page_url:
            raise HTTPException(status_code=400, detail="UI 测试需要提供页面 URL（page_url）")

        if req.script_type == "api":
            result = script_generator.generate_api_script(
                req.testcases, req.base_url, api_hints=req.api_hints, api_doc=req.api_doc
            )
        elif req.script_type == "ui":
            result = script_generator.generate_ui_script(req.testcases, req.page_url)
        elif req.script_type == "jmeter":
            result = script_generator.generate_jmeter_script(
                req.testcases, req.base_url, api_hints=req.api_hints, api_doc=req.api_doc
            )
        else:
            raise HTTPException(status_code=400, detail=f"不支持的脚本类型: {req.script_type}")
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save")
async def save_script(req: ScriptSaveRequest):
    """保存脚本到本地"""
    try:
        dir_path = os.path.join(settings.OUTPUT_DIR, "scripts")
        os.makedirs(dir_path, exist_ok=True)

        if req.filename:
            filename = req.filename
        else:
            ext_map = {"api": ".py", "ui": ".py", "jmeter": ".jmx"}
            ext = ext_map.get(req.script_type, ".txt")
            filename = f"script_{req.script_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"

        filepath = os.path.join(dir_path, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(req.code)
        return {"success": True, "filepath": filepath}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-jmeter")
async def run_jmeter(req: RunJmeterRequest):
    """使用本地 JMeter 运行 JMX 脚本，返回结构化的测试结果"""
    try:
        jmeter_exe = settings.get_jmeter_executable()
        if not os.path.isfile(jmeter_exe):
            raise HTTPException(
                status_code=400,
                detail=f"JMeter 未找到。请将 JMeter 安装到项目目录，或设置 JMETER_HOME 环境变量。\n查找路径: {jmeter_exe}",
            )

        jmx_path = req.jmx_filepath
        if not os.path.isfile(jmx_path):
            raise HTTPException(status_code=400, detail=f"JMX 文件不存在: {jmx_path}")

        # 结果输出路径
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_dir = os.path.join(settings.OUTPUT_DIR, "jmeter_results")
        os.makedirs(result_dir, exist_ok=True)
        jtl_path = os.path.join(result_dir, f"result_{timestamp}.jtl")
        report_dir = os.path.join(result_dir, f"report_{timestamp}")

        # 清理已存在的报告目录（JMeter 要求 -o 目录不存在）
        if os.path.exists(report_dir):
            shutil.rmtree(report_dir)

        # 构建 JMeter CLI 命令
        cmd = [
            jmeter_exe,
            "-n",
            "-t", jmx_path,
            "-l", jtl_path,
            "-e",
            "-o", report_dir,
        ]

        # 运行 JMeter
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=settings.PROJECT_ROOT,
        )

        # 检查 JTL 是否生成
        if not os.path.isfile(jtl_path):
            return {
                "success": True,
                "data": {
                    "exit_code": proc.returncode,
                    "stderr": proc.stderr[-2000:] if proc.stderr else "",
                    "stdout": proc.stdout[-2000:] if proc.stdout else "",
                    "summary": f"JMeter 执行完成（退出码: {proc.returncode}），但未生成 JTL 文件",
                    "samples": [],
                },
            }

        # 解析 JTL 结果
        samples = _parse_jtl(jtl_path)
        summary = _build_summary(samples)

        return {
            "success": True,
            "data": {
                "jtl_path": jtl_path,
                "report_dir": report_dir,
                "exit_code": proc.returncode,
                "summary": summary,
                "samples": samples,
            },
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="JMeter 执行超时（超过 5 分钟）")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- JTL 解析工具 ----

def _parse_jtl(jtl_path: str) -> list[dict]:
    """解析 JMeter JTL 结果文件，提取每个样本的关键信息"""
    samples = []
    try:
        tree = ET.parse(jtl_path)
        root = tree.getroot()
        for elem in root.iter():
            if elem.tag in ("httpSample", "sample"):
                attrs = elem.attrib
                success = attrs.get("s", "false").lower() == "true"
                samples.append({
                    "label": attrs.get("lb", "Unknown"),
                    "success": success,
                    "response_code": attrs.get("rc", ""),
                    "response_message": attrs.get("rm", "")[:200],
                    "elapsed_ms": int(attrs.get("t", 0)),
                    "latency_ms": int(attrs.get("lt", 0)),
                    "bytes": int(attrs.get("by", 0)),
                    "thread": attrs.get("tn", ""),
                    "timestamp": attrs.get("ts", ""),
                })
    except ET.ParseError:
        # 尝试作为 CSV 格式解析（JMeter 5.x 默认可能是 CSV）
        try:
            with open(jtl_path, "r", encoding="utf-8") as f:
                header_line = f.readline().strip()
                if header_line:
                    headers = header_line.split(",")
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        values = line.split(",")
                        if len(values) >= len(headers):
                            row = dict(zip(headers, values))
                            success = row.get("success", "false").lower() == "true"
                            samples.append({
                                "label": row.get("label", "Unknown"),
                                "success": success,
                                "response_code": row.get("responseCode", ""),
                                "response_message": row.get("responseMessage", "")[:200],
                                "elapsed_ms": int(float(row.get("elapsed", 0))),
                                "latency_ms": int(float(row.get("Latency", 0))),
                                "bytes": int(float(row.get("bytes", 0))),
                                "thread": row.get("threadName", ""),
                                "timestamp": row.get("timeStamp", ""),
                            })
        except Exception:
            pass
    return samples


def _build_summary(samples: list[dict]) -> dict:
    """根据样本数据生成汇总信息"""
    if not samples:
        return {"total": 0, "passed": 0, "failed": 0, "error_rate": "0%", "avg_time_ms": 0}

    total = len(samples)
    passed = sum(1 for s in samples if s["success"])
    failed = total - passed
    times = [s["elapsed_ms"] for s in samples]
    avg_time = int(sum(times) / total) if total > 0 else 0
    max_time = max(times) if times else 0
    min_time = min(times) if times else 0
    error_rate = f"{round(failed / total * 100, 1)}%" if total > 0 else "0%"

    # 按 label 分组统计
    by_label = {}
    for s in samples:
        lbl = s["label"]
        if lbl not in by_label:
            by_label[lbl] = {"total": 0, "passed": 0, "failed": 0}
        by_label[lbl]["total"] += 1
        if s["success"]:
            by_label[lbl]["passed"] += 1
        else:
            by_label[lbl]["failed"] += 1

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "error_rate": error_rate,
        "avg_time_ms": avg_time,
        "max_time_ms": max_time,
        "min_time_ms": min_time,
        "by_label": by_label,
    }
