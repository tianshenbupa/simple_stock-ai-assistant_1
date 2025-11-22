from langchain.agents import create_agent
from src.core.llm import llm
from src.tools.market import get_current_stock_price, get_market_sentiment
from config.prompts import MARKET_ANALYST_PROMPT

def create_market_analyst():
    return create_agent(
        model=llm,
        tools=[get_current_stock_price, get_market_sentiment],
        system_prompt=MARKET_ANALYST_PROMPT,
    )

_analyst = None

def get_market_analyst():
    global _analyst
    if _analyst is None:
        _analyst = create_market_analyst()
    return _analyst