from fastapi import APIRouter, HTTPException
from app.models.defect import DefectAnalyzeRequest
from app.agents.defect_agent import defect_agent
from app.generators.report_generator import report_generator

router = APIRouter(prefix="/api/v1/defect", tags=["缺陷分析"])


@router.post("/analyze")
async def analyze_defects(req: DefectAnalyzeRequest):
    """缺陷分类与根因分析"""
    try:
        result = defect_agent.analyze(
            test_results=req.test_results,
            feedback=req.feedback,
            previous_result=req.previous_result,
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save-report")
async def save_report(data: dict):
    """保存缺陷分析报告到本地"""
    try:
        md_content = report_generator.defect_to_markdown(data)
        filepath = report_generator.save_markdown(md_content, "reports", "defect_report")
        return {"success": True, "filepath": filepath}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
