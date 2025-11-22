import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

from src.core.models import StockAnalysisRequest, StockAnalysisResponse, HealthResponse
from src.agents.supervisor import analyze_stock_investment, quick_analyze
from src.rag.retriever import rag_system
from config.settings import settings

# ============ 日志配置 ============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============ 应用启动和关闭事件 ============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    - 启动时初始化 RAG 系统
    - 关闭时清理资源
    """
    # ===== 启动事件 =====
    logger.info("=" * 50)
    logger.info("🚀 股票投资 AI 助手 启动中...")
    logger.info("=" * 50)

    try:
        # 初始化 RAG 系统
        logger.info("📚 初始化 RAG 系统...")
        rag_init_message = rag_system.initialize()
        logger.info(f"✅ {rag_init_message}")

        logger.info("✅ 应用启动完成")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"❌ 启动失败: {e}", exc_info=True)
        raise

    yield

    # ===== 关闭事件 =====
    logger.info("=" * 50)
    logger.info("🛑 应用关闭中...")
    logger.info("=" * 50)

    try:
        logger.info("✅ 资源清理完成")
    except Exception as e:
        logger.error(f"❌ 关闭失败: {e}", exc_info=True)


# ============ 创建 FastAPI 应用 ============

app = FastAPI(
    title="股票投资 AI 助手",
    description="使用 LangChain 1.0.5 和 DeepSeek 构建的多代理股票投资分析系统",
    version="1.0.0",
    lifespan=lifespan
)

# ============ CORS 配置 ============

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（生产环境建议限制）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 根路由 ============

@app.get("/")
async def root():
    """
    API 根路由 - 提供基本信息
    """
    return {
        "name": "股票投资 AI 助手",
        "version": "1.0.0",
        "description": "使用 LangChain 1.0.5 和 DeepSeek 构建的多代理股票投资分析系统",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# ============ 健康检查 ============

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    健康检查端点

    Returns:
        应用状态和版本信息
    """
    return HealthResponse(
        status="ok",
        version="1.0.0"
    )


# ============ 主要分析接口 ============

@app.post("/api/analyze", response_model=StockAnalysisResponse)
async def analyze_stock(request: StockAnalysisRequest):
    """
    分析股票投资机会（完整分析）

    这是核心 API 端点，执行完整的多代理分析流程：
    1. 财务分析 - 分析公司财务报表和财务指标
    2. 市场分析 - 评估股票价格和市场情绪
    3. 估值分析 - 计算股票内在价值
    4. 综合建议 - 生成最终投资建议

    Args:
        request (StockAnalysisRequest): 包含以下字段：
            - stock_ticker (str): 股票代码，例如 AAPL、MSFT、GOOGL
            - query (str): 分析问题，例如 "这支股票值得买入吗？"

    Returns:
        StockAnalysisResponse: 包含以下字段：
            - stock_ticker (str): 股票代码
            - query (str): 原始问题
            - timestamp (datetime): 分析时间
            - analysis (str): 详细的分析结果
            - recommendation (str): 投资建议（买入/持有/卖出）
            - target_price (float): 目标价格

    Raises:
        HTTPException: 如果分析过程中出现错误

    Example:
        >>> import requests
        >>> response = requests.post(
        ...     "http://localhost:8000/api/analyze",
        ...     json={
        ...         "stock_ticker": "AAPL",
        ...         "query": "苹果公司是否值得投资？"
        ...     }
        ... )
        >>> print(response.json())
    """
    try:
        logger.info(f"📊 开始分析 {request.stock_ticker}")
        logger.info(f"   问题: {request.query}")

        # 调用多代理系统进行综合分析
        analysis_result = await analyze_stock_investment(
            stock_ticker=request.stock_ticker,
            user_query=request.query,
            include_financial=True,
            include_market=True,
            include_valuation=True
        )

        logger.info(f"✅ {request.stock_ticker} 分析完成")

        # 返回结构化响应
        return StockAnalysisResponse(
            stock_ticker=request.stock_ticker,
            query=request.query,
            timestamp=datetime.now(),
            analysis=analysis_result,
            recommendation="买入" if "买入" in analysis_result else "持有",
            target_price=None
        )

    except Exception as e:
        logger.error(f"❌ 分析失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"分析失败: {str(e)}"
        )


# ============ 财务分析接口 ============

@app.post("/api/analyze/financial")
async def analyze_financial(stock_ticker: str, query: str):
    """
    仅进行财务分析

    Args:
        stock_ticker (str): 股票代码
        query (str): 分析问题

    Returns:
        财务分析结果

    Example:
        >>> curl -X POST "http://localhost:8000/api/analyze/financial?stock_ticker=AAPL&query=收入增长怎么样？"
    """
    try:
        logger.info(f"💰 进行财务分析: {stock_ticker}")

        analysis_result = await analyze_stock_investment(
            stock_ticker=stock_ticker,
            user_query=query,
            include_financial=True,
            include_market=False,
            include_valuation=False
        )

        return {
            "stock_ticker": stock_ticker,
            "analysis_type": "financial",
            "query": query,
            "result": analysis_result,
            "timestamp": datetime.now()
        }

    except Exception as e:
        logger.error(f"❌ 财务分析失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"财务分析失败: {str(e)}"
        )


# ============ 市场分析接口 ============

@app.post("/api/analyze/market")
async def analyze_market(stock_ticker: str, query: str):
    """
    仅进行市场分析

    Args:
        stock_ticker (str): 股票代码
        query (str): 分析问题

    Returns:
        市场分析结果

    Example:
        >>> curl -X POST "http://localhost:8000/api/analyze/market?stock_ticker=AAPL&query=市场情绪如何？"
    """
    try:
        logger.info(f"📈 进行市场分析: {stock_ticker}")

        analysis_result = await analyze_stock_investment(
            stock_ticker=stock_ticker,
            user_query=query,
            include_financial=False,
            include_market=True,
            include_valuation=False
        )

        return {
            "stock_ticker": stock_ticker,
            "analysis_type": "market",
            "query": query,
            "result": analysis_result,
            "timestamp": datetime.now()
        }

    except Exception as e:
        logger.error(f"❌ 市场分析失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"市场分析失败: {str(e)}"
        )


# ============ 估值分析接口 ============

@app.post("/api/analyze/valuation")
async def analyze_valuation(stock_ticker: str, query: str):
    """
    仅进行估值分析

    Args:
        stock_ticker (str): 股票代码
        query (str): 分析问题

    Returns:
        估值分析结果

    Example:
        >>> curl -X POST "http://localhost:8000/api/analyze/valuation?stock_ticker=AAPL&query=内在价值是多少？"
    """
    try:
        logger.info(f"💎 进行估值分析: {stock_ticker}")

        analysis_result = await analyze_stock_investment(
            stock_ticker=stock_ticker,
            user_query=query,
            include_financial=False,
            include_market=False,
            include_valuation=True
        )

        return {
            "stock_ticker": stock_ticker,
            "analysis_type": "valuation",
            "query": query,
            "result": analysis_result,
            "timestamp": datetime.now()
        }

    except Exception as e:
        logger.error(f"❌ 估值分析失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"估值分析失败: {str(e)}"
        )


# ============ RAG 查询接口 ============

@app.post("/api/rag/query")
async def rag_query(query: str, stock_ticker: str = None):
    """
    直接查询财报 RAG 系统

    不调用代理，直接从向量数据库检索相关财报信息。

    Args:
        query (str): 搜索查询（例如："收入增长"）
        stock_ticker (str, optional): 股票代码，用于过滤

    Returns:
        检索到的相关财报内容

    Example:
        >>> curl -X POST "http://localhost:8000/api/rag/query?query=收入增长&stock_ticker=AAPL"
    """
    try:
        logger.info(f"🔍 RAG 查询: {query}")

        # 构建查询字符串
        rag_query_str = f"{stock_ticker} {query}" if stock_ticker else query

        # 检索相关内容
        context = rag_system.retrieve(rag_query_str)

        return {
            "query": query,
            "stock_ticker": stock_ticker,
            "results": context if context else "未找到相关财报信息",
            "timestamp": datetime.now()
        }

    except Exception as e:
        logger.error(f"❌ RAG 查询失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"RAG 查询失败: {str(e)}"
        )


# ============ RAG 初始化接口 ============

@app.post("/api/rag/initialize")
async def rag_initialize():
    """
    初始化 RAG 系统（加载和索引所有 PDF）

    这个接口用于：
    1. 加载所有财报 PDF 文件
    2. 分割成文本块
    3. 生成向量嵌入
    4. 存储到向量数据库

    Returns:
        初始化结果信息

    Example:
        >>> curl -X POST "http://localhost:8000/api/rag/initialize"
    """
    try:
        logger.info("🔄 初始化 RAG 系统...")

        # 初始化 RAG 系统
        result = rag_system.initialize()

        logger.info(f"✅ {result}")

        return {
            "status": "success",
            "message": result,
            "timestamp": datetime.now()
        }

    except Exception as e:
        logger.error(f"❌ RAG 初始化失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"RAG 初始化失败: {str(e)}"
        )


# ============ 信息接口 ============

@app.get("/api/info")
async def get_info():
    """
    获取应用配置信息

    Returns:
        应用配置和运行信息
    """
    return {
        "app_name": "股票投资 AI 助手",
        "version": "1.0.0",
        "llm_model": settings.model_name,
        "llm_temperature": settings.temperature,
        "vector_store_path": settings.vector_store_path,
        "pdf_directory": settings.pdf_directory,
        "debug": settings.debug,
        "timestamp": datetime.now()
    }


# ============ 错误处理 ============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """自定义 HTTP 异常处理"""
    logger.error(f"HTTP 异常: {exc.detail}")
    return {
        "error": True,
        "status_code": exc.status_code,
        "detail": exc.detail,
        "timestamp": datetime.now()
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return {
        "error": True,
        "status_code": 500,
        "detail": "内部服务器错误",
        "timestamp": datetime.now()
    }


# ============ 启动命令 ============

if __name__ == "__main__":
    """
    运行应用

    开发模式（带自动重载）：
        python main.py
        或
        uvicorn main:app --reload

    生产模式（带多个工作进程）：
        uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

    指定主机和端口：
        uvicorn main:app --host 127.0.0.1 --port 8000
    """
    import uvicorn

    print("=" * 60)
    print("🚀 股票投资 AI 助手")
    print("=" * 60)
    print(f"📍 访问地址: http://{settings.host}:{settings.port}")
    print(f"📚 API 文档: http://{settings.host}:{settings.port}/docs")
    print(f"🔄 ReDoc: http://{settings.host}:{settings.port}/redoc")
    print("=" * 60)

    uvicorn.run(
        "main:app",  # 改为导入字符串格式
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )