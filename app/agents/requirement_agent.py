from app.agents.base_agent import BaseAgent


class RequirementAgent(BaseAgent):
    """需求解析 Agent —— 将自然语言需求拆解为结构化测试点"""

    template_name = "requirement"

    def parse(
        self,
        content: str,
        feedback: str = None,
        previous_result: dict = None,
        url: str = None,
        page_context: dict = None,
    ) -> dict:
        """解析测试需求，支持多轮修改和基于 URL 的页面上下文"""
        return self.call_llm(
            content=content,
            feedback=feedback,
            previous_result=previous_result,
            url=url,
            page_context=page_context,
        )


requirement_agent = RequirementAgent()
