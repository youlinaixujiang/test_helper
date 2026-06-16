from app.agents.base_agent import BaseAgent
from app.core.llm_client import llm_client
from app.core.prompt_engine import prompt_engine


class ScriptAgent(BaseAgent):
    """脚本生成 Agent —— 生成 pytest/Selenium/JMeter 脚本"""

    TEMPLATES = {
        "api": "script_api",
        "ui": "script_ui",
        "jmeter": "script_jmeter",
    }

    def generate(self, script_type: str, testcases: list, base_url: str = "", page_url: str = "", api_hints: list = None, api_doc: str = "") -> str:
        """生成测试脚本，返回代码字符串"""
        if script_type not in self.TEMPLATES:
            raise ValueError(f"不支持的脚本类型: {script_type}，可选: {list(self.TEMPLATES.keys())}")

        template_name = self.TEMPLATES[script_type]
        messages = prompt_engine.build_messages(
            template_name,
            testcases=testcases,
            base_url=base_url,
            page_url=page_url,
            api_hints=api_hints or [],
            api_doc=api_doc or "",
        )
        raw = llm_client.chat(messages)
        return self._clean_code(raw)

    def _clean_code(self, raw: str) -> str:
        """清理 LLM 返回代码中的 markdown 标记"""
        raw = raw.strip()
        if raw.startswith("```"):
            lines = raw.split("\n")
            # 移除第一行的 ```python 或 ```xml
            if lines[0].startswith("```"):
                lines = lines[1:]
            # 移除最后一行的 ```
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            raw = "\n".join(lines)
        return raw


script_agent = ScriptAgent()
