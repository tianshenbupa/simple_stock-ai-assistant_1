from langchain_openai import ChatOpenAI
from config.settings import settings

def get_deepseek_llm() -> ChatOpenAI:
    """初始化 DeepSeek LLM"""
    return ChatOpenAI(
        model=settings.model_name,
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_api_base,
        temperature=settings.temperature,
        max_tokens=4096,
    )

llm = get_deepseek_llm()