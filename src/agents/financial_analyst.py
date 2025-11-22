from langchain.agents import create_agent
from src.core.llm import llm
from src.tools.financial import analyze_financial_statements, extract_key_metrics
from config.prompts import FINANCIAL_ANALYST_PROMPT

def create_financial_analyst():
    return create_agent(
        model=llm,
        tools=[analyze_financial_statements, extract_key_metrics],
        system_prompt=FINANCIAL_ANALYST_PROMPT,
    )

_analyst = None

def get_financial_analyst():
    global _analyst
    if _analyst is None:
        _analyst = create_financial_analyst()
    return _analyst