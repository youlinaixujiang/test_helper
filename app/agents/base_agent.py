import json
import re
from app.core.llm_client import llm_client
from app.core.prompt_engine import prompt_engine


class BaseAgent:
    """Agent 基类，提供 LLM 调用和 JSON 解析的通用逻辑"""

    template_name: str = ""

    def call_llm(self, **kwargs) -> dict:
        messages = prompt_engine.build_messages(self.template_name, **kwargs)
        raw = llm_client.chat(messages)
        return self._parse_json(raw)

    def _parse_json(self, raw: str):
        """从 LLM 返回值中提取 JSON，支持 dict 和 list"""
        raw = raw.strip()

        # 去除 markdown 代码块标记
        if raw.startswith("```"):
            lines = raw.split("\n")
            # 移除首行 ```
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            # 如果首行是纯语言标记（如 json、python），也移除
            if lines and lines[0].strip() and "{" not in lines[0] and "[" not in lines[0]:
                if len(lines[0].strip()) < 20:
                    lines = lines[1:]
            # 移除尾行 ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            raw = "\n".join(lines).strip()

        # 去除非 JSON 的前导文本（找到第一个 { 或 [ 的位置）
        json_start = -1
        for char in ("{", "["):
            idx = raw.find(char)
            if idx != -1 and (json_start == -1 or idx < json_start):
                json_start = idx
        if json_start > 0:
            raw = raw[json_start:]

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # 正则提取，按 JSON 类型分别匹配
            if raw.startswith("["):
                match = re.search(r"\[.*\]", raw, re.DOTALL)
            else:
                match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise ValueError(f"无法解析 LLM 返回的 JSON，原始内容前500字符: {raw[:500]}")
