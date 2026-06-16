import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    AGNES_API_KEY: str = os.getenv("AGNES_API_KEY", "")
    AGNES_BASE_URL: str = os.getenv("AGNES_BASE_URL", "https://api.agnes-ai.com/v1")
    AGNES_MODEL: str = os.getenv("AGNES_MODEL", "agnes-ai-latest")

    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 16384

    OUTPUT_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
    PROJECT_ROOT: str = os.path.dirname(os.path.dirname(__file__))

    JMETER_HOME: str = os.getenv("JMETER_HOME", "")

    @classmethod
    def get_jmeter_path(cls) -> str:
        """获取 JMeter 安装路径（绝对路径）"""
        jmeter_home = cls.JMETER_HOME
        if not jmeter_home:
            # 默认尝试常见目录
            for candidate in ["apache-jmeter-5.6.3", "jmeter", "apache-jmeter"]:
                p = os.path.join(cls.PROJECT_ROOT, candidate)
                if os.path.isdir(p):
                    jmeter_home = p
                    break
        elif not os.path.isabs(jmeter_home):
            jmeter_home = os.path.join(cls.PROJECT_ROOT, jmeter_home)
        return jmeter_home

    @classmethod
    def get_jmeter_executable(cls) -> str:
        """获取 JMeter CLI 可执行文件路径"""
        jmeter_home = cls.get_jmeter_path()
        if os.name == "nt":
            return os.path.join(jmeter_home, "bin", "jmeter.bat")
        return os.path.join(jmeter_home, "bin", "jmeter")

    @classmethod
    def ensure_output_dirs(cls):
        for sub in ["testcases", "scripts", "reports", "jmeter_results"]:
            os.makedirs(os.path.join(cls.OUTPUT_DIR, sub), exist_ok=True)


settings = Settings()
