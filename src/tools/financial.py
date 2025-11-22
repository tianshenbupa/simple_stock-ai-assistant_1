from langchain.tools import tool
from src.rag.retriever import rag_system

@tool
def analyze_financial_statements(stock_ticker: str, query: str) -> str:
    """分析公司财务报表"""
    context = rag_system.retrieve(f"{stock_ticker} {query}")
    return f"财务分析\n{stock_ticker}\n问题: {query}\n\n相关数据:\n{context}"

@tool
def extract_key_metrics(stock_ticker: str, metric_type: str) -> str:
    """提取关键财务指标"""
    context = rag_system.retrieve(f"{stock_ticker} {metric_type}")
    return f"关键指标\n{stock_ticker} {metric_type}\n\n数据:\n{context}"