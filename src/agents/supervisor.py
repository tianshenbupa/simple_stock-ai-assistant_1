from langchain.agents import create_agent
from langchain.tools import tool
from src.core.llm import llm
from src.agents.financial_analyst import get_financial_analyst
from src.agents.market_analyst import get_market_analyst
from src.agents.valuation_expert import get_valuation_expert
from config.prompts import SUPERVISOR_PROMPT
import logging

logger = logging.getLogger(__name__)


# ============ 定义工具来调用子代理 ============

@tool
def call_financial_analyst(stock_ticker: str, query: str) -> str:
    """
    调用财务分析代理进行财务分析

    Args:
        stock_ticker: 股票代码（如 AAPL、MSFT）
        query: 分析问题

    Returns:
        财务分析结果
    """
    try:
        analyst = get_financial_analyst()
        result = analyst.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": f"对 {stock_ticker} 进行财务分析：{query}"
                }
            ]
        })

        messages = result.get("messages", [])
        if messages:
            return messages[-1].content
        return "财务分析无结果"

    except Exception as e:
        logger.error(f"财务分析失败: {e}")
        return f"错误：财务分析失败 - {str(e)}"


@tool
def call_market_analyst(stock_ticker: str, query: str) -> str:
    """
    调用市场分析代理进行市场分析

    Args:
        stock_ticker: 股票代码
        query: 分析问题

    Returns:
        市场分析结果
    """
    try:
        analyst = get_market_analyst()
        result = analyst.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": f"分析 {stock_ticker} 的市场情况：{query}"
                }
            ]
        })

        messages = result.get("messages", [])
        if messages:
            return messages[-1].content
        return "市场分析无结果"

    except Exception as e:
        logger.error(f"市场分析失败: {e}")
        return f"错误：市场分析失败 - {str(e)}"


@tool
def call_valuation_expert(stock_ticker: str, query: str) -> str:
    """
    调用估值专家进行价值评估

    Args:
        stock_ticker: 股票代码
        query: 估值问题

    Returns:
        估值分析结果
    """
    try:
        expert = get_valuation_expert()
        result = expert.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": f"评估 {stock_ticker} 的价值：{query}"
                }
            ]
        })

        messages = result.get("messages", [])
        if messages:
            return messages[-1].content
        return "估值分析无结果"

    except Exception as e:
        logger.error(f"估值分析失败: {e}")
        return f"错误：估值分析失败 - {str(e)}"


# ============ 创建主管理代理 ============

def create_supervisor_agent():
    """
    创建投资决策主管代理

    使用 Tool Calling 模式，通过调用三个专家代理来协调综合分析
    """
    return create_agent(
        model=llm,
        tools=[
            call_financial_analyst,
            call_market_analyst,
            call_valuation_expert
        ],
        system_prompt=SUPERVISOR_PROMPT,
    )


# 单例模式 - 缓存主管理代理
_supervisor = None


def get_supervisor():
    """
    获取主管理代理实例（单例）

    Returns:
        主管理代理实例
    """
    global _supervisor
    if _supervisor is None:
        logger.info("初始化投资决策主管代理...")
        _supervisor = create_supervisor_agent()
        logger.info("✅ 主管理代理初始化完成")
    return _supervisor


async def analyze_stock_investment(
        stock_ticker: str,
        user_query: str,
        include_financial: bool = True,
        include_market: bool = True,
        include_valuation: bool = True
) -> str:
    """
    进行综合股票投资分析

    这是主要的分析入口函数，流程如下：
    1. 主管理代理接收用户的投资问题
    2. 根据分析偏好调用相应的专家代理
    3. 财务分析代理：分析公司财务状况
    4. 市场分析代理：分析市场动向和情绪
    5. 估值专家代理：评估股票价值
    6. 主管理代理综合所有信息生成最终建议

    Args:
        stock_ticker: 股票代码（例如：AAPL）
        user_query: 用户的投资问题（例如：这支股票值得买入吗？）
        include_financial: 是否包含财务分析（默认 True）
        include_market: 是否包含市场分析（默认 True）
        include_valuation: 是否包含估值分析（默认 True）

    Returns:
        综合投资分析建议字符串

    Raises:
        Exception: 如果分析过程中出现错误

    Example:
        >>> result = await analyze_stock_investment(
        ...     stock_ticker="AAPL",
        ...     user_query="苹果公司是否值得投资？"
        ... )
        >>> print(result)
    """
    try:
        supervisor = get_supervisor()

        # 构建分析偏好列表
        analysis_preferences = []
        if include_financial:
            analysis_preferences.append("财务状况分析")
        if include_market:
            analysis_preferences.append("市场动向分析")
        if include_valuation:
            analysis_preferences.append("价值评估分析")

        # 构建完整的分析请求提示
        full_prompt = f"""
========================================
股票投资分析请求
========================================

股票代码: {stock_ticker}
用户问题: {user_query}

分析范围: {', '.join(analysis_preferences) if analysis_preferences else '全面分析'}

========================================
请根据用户偏好调用相应的分析代理，然后综合所有信息提供投资建议。

最终建议应包含以下内容：
1. 财务评分（1-10分）
2. 市场评分（1-10分）
3. 估值评分（1-10分）
4. 综合建议（强烈买入/买入/持有/卖出/强烈卖出）
5. 目标价格范围
6. 关键风险
7. 投资时间框架建议
========================================
"""

        logger.info(f"开始分析 {stock_ticker}，用户问题: {user_query}")

        # 调用主管理代理进行综合分析
        response = supervisor.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": full_prompt
                }
            ]
        })

        # 提取响应内容
        messages = response.get("messages", [])
        if messages:
            result = messages[-1].content
            logger.info(f"✅ 成功完成 {stock_ticker} 的分析")
            return result

        # 如果没有返回消息，记录警告
        logger.warning(f"{stock_ticker} 分析未返回结果")
        return "分析失败：没有得到响应"

    except Exception as e:
        # 记录错误并重新抛出异常
        logger.error(f"❌ 综合分析失败: {e}", exc_info=True)
        raise


# 便捷函数 - 用于简化 API 调用
async def quick_analyze(stock_ticker: str, query: str) -> str:
    """
    快速分析股票（包含所有分析类型）

    Args:
        stock_ticker: 股票代码
        query: 分析问题

    Returns:
        分析结果
    """
    return await analyze_stock_investment(
        stock_ticker=stock_ticker,
        user_query=query,
        include_financial=True,
        include_market=True,
        include_valuation=True
    )