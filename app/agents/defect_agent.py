from app.agents.base_agent import BaseAgent


class DefectAgent(BaseAgent):
    """缺陷分析 Agent —— 分类缺陷并给出根因分析"""

    template_name = "defect"

    def analyze(self, test_results: str, feedback: str = None, previous_result: dict = None) -> dict:
        """分析测试结果，返回缺陷分析报告"""
        return self.call_llm(
            test_results=test_results,
            feedback=feedback,
            previous_result=previous_result,
        )


defect_agent = DefectAgent()
