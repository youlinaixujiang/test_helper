from openai import OpenAI, APIError, APIConnectionError
from app.config import settings


class LLMClient:
    """LLM API 调用封装，兼容 OpenAI 格式"""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.AGNES_API_KEY,
            base_url=settings.AGNES_BASE_URL,
        )
        self.model = settings.AGNES_MODEL

    def chat(self, messages: list, temperature: float = None, max_tokens: int = None) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or settings.LLM_TEMPERATURE,
                max_tokens=max_tokens or settings.LLM_MAX_TOKENS,
            )
            return response.choices[0].message.content
        except APIConnectionError as e:
            raise RuntimeError(f"无法连接 LLM 服务 ({settings.AGNES_BASE_URL}): {e}")
        except APIError as e:
            raise RuntimeError(f"LLM API 错误 (code={e.status_code}): {e.body.get('message', str(e)) if hasattr(e, 'body') and e.body else str(e)}")
        except Exception as e:
            raise RuntimeError(f"LLM 调用失败: {e}")


llm_client = LLMClient()
