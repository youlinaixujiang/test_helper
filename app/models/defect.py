from pydantic import BaseModel, Field
from typing import Optional


class DefectItem(BaseModel):
    test_case: str = ""
    error_message: str = ""
    category: str = ""
    root_cause: str = ""
    suggestion: str = ""


class DefectAnalysisResult(BaseModel):
    summary: str = ""
    total_failures: int = 0
    defects: list[DefectItem] = []
    overall_suggestion: str = ""


class DefectAnalyzeRequest(BaseModel):
    test_results: str = Field(..., description="测试执行结果（失败日志或 pytest 输出）")
    feedback: Optional[str] = Field(None, description="用户反馈，用于多轮修改")
    previous_result: Optional[dict] = Field(None, description="上一轮结果")
