from app.agents.base_agent import BaseAgent


class TestCaseAgent(BaseAgent):
    """用例生成 Agent —— 基于需求分析结果生成标准化测试用例"""

    template_name = "testcase"
    BATCH_SIZE = 5  # 每批最多生成 5 个用例，避免 LLM 输出超限

    def generate(self, requirement_result: dict, base_url: str = None, page_text: str = None, feedback: str = None, previous_result: dict = None) -> list:
        """生成测试用例，返回用例列表。大批量时自动分批处理。"""
        test_points = requirement_result.get("test_points", [])

        # 小批量直接生成
        if len(test_points) <= self.BATCH_SIZE:
            return self.call_llm(
                requirement_result=requirement_result,
                base_url=base_url,
                page_text=page_text,
                feedback=feedback,
                previous_result=previous_result,
            )

        # 大批量分批处理
        all_cases = []
        total_batches = (len(test_points) + self.BATCH_SIZE - 1) // self.BATCH_SIZE
        for i in range(0, len(test_points), self.BATCH_SIZE):
            batch_points = test_points[i:i + self.BATCH_SIZE]
            batch_num = i // self.BATCH_SIZE + 1
            batch_result = {
                "feature": requirement_result.get("feature", ""),
                "test_points": batch_points,
                "_batch_info": f"第 {batch_num}/{total_batches} 批",
            }

            cases = self.call_llm(requirement_result=batch_result, base_url=base_url, page_text=page_text)
            if isinstance(cases, list):
                all_cases.extend(cases)

        # 重新编号 case_id
        for idx, case in enumerate(all_cases, 1):
            case["case_id"] = f"TC-{idx:03d}"

        return all_cases


testcase_agent = TestCaseAgent()
