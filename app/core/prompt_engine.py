import yaml
import os
from jinja2 import Template


class PromptEngine:
    """Prompt 模板引擎：加载 YAML 模板并用 Jinja2 渲染"""

    def __init__(self, prompts_dir: str = None):
        if prompts_dir is None:
            prompts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
        self.prompts_dir = prompts_dir
        self._cache = {}

    def _load_template(self, name: str) -> dict:
        if name not in self._cache:
            path = os.path.join(self.prompts_dir, f"{name}.yaml")
            if not os.path.exists(path):
                raise FileNotFoundError(f"Prompt 模板不存在: {path}")
            with open(path, "r", encoding="utf-8") as f:
                self._cache[name] = yaml.safe_load(f)
        return self._cache[name]

    def build_messages(self, template_name: str, **kwargs) -> list:
        """构建 messages 列表，返回 [{"role": "system", "content": ...}, {"role": "user", "content": ...}]"""
        tmpl = self._load_template(template_name)
        messages = []

        system_tmpl = tmpl.get("system", "")
        if system_tmpl:
            messages.append({
                "role": "system",
                "content": Template(system_tmpl).render(**kwargs)
            })

        # Few-shot examples
        examples = tmpl.get("examples", [])
        for ex in examples:
            messages.append({"role": "user", "content": Template(ex["user"]).render(**kwargs)})
            messages.append({"role": "assistant", "content": Template(ex["assistant"]).render(**kwargs)})

        # Actual user prompt
        user_tmpl = tmpl.get("user", "")
        messages.append({
            "role": "user",
            "content": Template(user_tmpl).render(**kwargs)
        })

        return messages


prompt_engine = PromptEngine()
