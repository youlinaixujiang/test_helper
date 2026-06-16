from pydantic import BaseModel, Field
from typing import Optional


class TestStep(BaseModel):
    step_num: int
    action: str
    expected: str


class TestCase(BaseModel):
    case_id: str
    module: str = ""
    title: str
    precondition: str = "无"
    steps: list[TestStep] = []
    expected: str = ""
    priority: str = "P1"
    type: str = "功能"


class TestCaseRequest(BaseModel):
    requirement_result: dict = Field(..., description="需求解析结果（RequirementResult 的 dict）")
    base_url: Optional[str] = Field(None, description="被测系统 API 基础 URL")
    page_text: Optional[str] = Field(None, description="被测网站的页面文本内容，用于消除用例幻觉")
    feedback: Optional[str] = Field(None, description="用户反馈，用于多轮修改")
    previous_result: Optional[dict] = Field(None, description="上一轮结果")
