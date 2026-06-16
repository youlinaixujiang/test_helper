from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os

from app.config import settings
from app.api.requirement_api import router as requirement_router
from app.api.testcase_api import router as testcase_router
from app.api.script_api import router as script_router
from app.api.defect_api import router as defect_router

settings.ensure_output_dirs()

app = FastAPI(
    title="AI 测试 Agent 平台",
    description="基于大模型的智能测试平台 —— 需求解析、用例生成、脚本生成、缺陷分析",
    version="1.0.0",
)

# 静态文件
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# API 路由
app.include_router(requirement_router)
app.include_router(testcase_router)
app.include_router(script_router)
app.include_router(defect_router)


@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "service": "AI 测试 Agent 平台"}


@app.get("/", response_class=HTMLResponse)
async def index():
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    with open(os.path.join(templates_dir, "index.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
