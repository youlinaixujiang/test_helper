from pydantic import BaseModel, Field
from typing import Optional


class TestPoint(BaseModel):
    id: str
    scene: str
    priority: str = "P1"
    precondition: str = "无"


class RequirementResult(BaseModel):
    feature: str
    test_points: list[TestPoint] = []


class URLCheckRequest(BaseModel):
    url: str = Field(..., description="要检测的网址")


class RequirementRequest(BaseModel):
    content: str = Field(..., description="自然语言测试需求描述")
    url: Optional[str] = Field(None, description="被测网站 URL，用于获取页面上下文")
    feedback: Optional[str] = Field(None, description="用户反馈，用于多轮修改")
    previous_result: Optional[dict] = Field(None, description="上一轮结果，用于多轮修改")
