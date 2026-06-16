import os
import json
from datetime import datetime
from app.config import settings
from app.agents.script_agent import script_agent


class ScriptGenerator:
    """脚本生成器 —— 负责调用 Agent 生成并保存脚本文件"""

    @staticmethod
    def generate_api_script(testcases: list, base_url: str, api_hints: list = None, api_doc: str = "") -> dict:
        """生成接口测试脚本"""
        code = script_agent.generate("api", testcases, base_url=base_url, api_hints=api_hints, api_doc=api_doc)
        filename = f"test_api_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        filepath = ScriptGenerator._save("scripts", filename, code)
        return {"filename": filename, "filepath": filepath, "code": code, "language": "python"}

    @staticmethod
    def generate_ui_script(testcases: list, page_url: str) -> dict:
        """生成 UI 自动化脚本"""
        code = script_agent.generate("ui", testcases, page_url=page_url)
        filename = f"test_ui_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        filepath = ScriptGenerator._save("scripts", filename, code)
        return {"filename": filename, "filepath": filepath, "code": code, "language": "python"}

    @staticmethod
    def generate_jmeter_script(testcases: list, base_url: str, api_hints: list = None, api_doc: str = "") -> dict:
        """生成 JMeter JMX 脚本"""
        code = script_agent.generate("jmeter", testcases, base_url=base_url, api_hints=api_hints, api_doc=api_doc)
        filename = f"test_jmeter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jmx"
        filepath = ScriptGenerator._save("scripts", filename, code)
        return {"filename": filename, "filepath": filepath, "code": code, "language": "xml"}

    @staticmethod
    def _save(subdir: str, filename: str, content: str) -> str:
        dir_path = os.path.join(settings.OUTPUT_DIR, subdir)
        os.makedirs(dir_path, exist_ok=True)
        filepath = os.path.join(dir_path, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath


script_generator = ScriptGenerator()
