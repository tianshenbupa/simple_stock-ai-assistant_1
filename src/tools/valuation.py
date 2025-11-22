from langchain.tools import tool

@tool
def calculate_pe_ratio(stock_ticker: str, price: float, eps: float) -> str:
    """计算市盈率"""
    if eps <= 0:
        return "无法计算：每股收益为负"
    pe = price / eps
    return f"{stock_ticker} PE比率: {pe:.2f}"

@tool
def calculate_intrinsic_value(fcf: float, growth_rate: float, discount_rate: float) -> str:
    """计算内在价值（DCF）"""
    if discount_rate <= growth_rate:
        return "折现率必须大于增长率"
    value = fcf * (1 + growth_rate) / (discount_rate - growth_rate)
    return f"内在价值: ${value:.2f}"