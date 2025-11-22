from langchain.tools import tool

@tool
def get_current_stock_price(stock_ticker: str) -> str:
    """获取股票当前价格"""
    # 实际应调用 API，这里只是示例
    return f"{stock_ticker} 当前价格: $150.50"

@tool
def get_market_sentiment(stock_ticker: str) -> str:
    """获取市场情绪"""
    return f"{stock_ticker} 市场情绪: 看涨"