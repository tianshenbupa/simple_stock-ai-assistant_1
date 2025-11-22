from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # DeepSeek API 配置
    deepseek_api_key: str
    deepseek_api_base: str = "https://api.deepseek.com"  # ✅ 去掉 /v1
    model_name: str = "deepseek-chat"
    temperature: float = 0.0

    # 添加属性别名，兼容不同的命名
    @property
    def api_key(self):
        """API Key 的别名"""
        return self.deepseek_api_key

    @property
    def base_url(self):
        """Base URL 的别名"""
        return self.deepseek_api_base

    # RAG 配置
    vector_store_path: str = "data/vector_store"
    pdf_directory: str = "data/financial_reports"
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # 服务器配置
    host: str = "127.0.0.1"  # ✅ 改为 127.0.0.1，WSL 中更好用
    port: int = 8000
    debug: bool = True  # ✅ 开发时设为 True

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()