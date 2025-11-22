"""
RAG 检索系统
使用 HuggingFace embeddings（免费、本地运行）
"""

from langchain_chroma import Chroma  # ✅ 更新导入
from langchain_huggingface import HuggingFaceEmbeddings # ✅ 使用免费的
from src.rag.loader import PDFLoader
from config.settings import settings
import logging
import os

logger = logging.getLogger(__name__)


class RAGSystem:
    def __init__(self):
        """初始化 RAG 系统"""
        logger.info("🔧 初始化 RAG 系统...")

        # ✅ 使用 HuggingFace 免费 embeddings（本地运行，不需要 API）
        logger.info("📦 加载 HuggingFace embeddings 模型...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",  # 轻量级、高质量
            model_kwargs={'device': 'cpu'},  # CPU 运行
            encode_kwargs={'normalize_embeddings': True}  # 标准化向量
        )
        logger.info("✅ Embeddings 模型加载成功")

        self.vectorstore = None
        self.retriever = None

    def initialize(self):
        """初始化向量数据库"""
        try:
            logger.info("📚 开始加载 PDF 文档...")

            loader = PDFLoader()
            documents = loader.load_all_pdfs()

            if documents:
                logger.info(f"📄 成功加载 {len(documents)} 个文档块")
                logger.info("🔄 正在生成向量嵌入...")

                # 创建向量数据库
                self.vectorstore = Chroma.from_documents(
                    documents,
                    self.embeddings,
                    persist_directory=settings.vector_store_path
                )

                # 创建检索器
                self.retriever = self.vectorstore.as_retriever(
                    search_kwargs={"k": 5}
                )

                logger.info("✅ 向量数据库创建成功")
                return f"已加载 {len(documents)} 个文档块"
            else:
                logger.warning("⚠️ 没有找到 PDF 文件")
                return "没有可用的 PDF 文件"

        except Exception as e:
            logger.error(f"❌ RAG 初始化失败: {e}", exc_info=True)
            return f"初始化失败: {str(e)}"

    def retrieve(self, query: str) -> str:
        """检索相关财报"""
        try:
            # 如果检索器未初始化，尝试从持久化存储加载
            if not self.retriever:
                logger.info("🔄 从持久化存储加载向量数据库...")

                if os.path.exists(settings.vector_store_path):
                    self.vectorstore = Chroma(
                        embedding_function=self.embeddings,
                        persist_directory=settings.vector_store_path
                    )
                    self.retriever = self.vectorstore.as_retriever(
                        search_kwargs={"k": 5}
                    )
                    logger.info("✅ 向量数据库加载成功")
                else:
                    logger.warning("⚠️ 向量数据库不存在，请先初始化")
                    return ""

            # 执行检索
            logger.info(f"🔍 检索查询: {query}")
            docs = self.retriever.invoke(query)

            if not docs:
                logger.info("📭 未找到相关文档")
                return ""

            # 构建上下文
            context = ""
            for i, doc in enumerate(docs, 1):
                company = doc.metadata.get("company", "Unknown")
                context += f"\n=== 文档 {i} [{company}] ===\n{doc.page_content}\n"

            logger.info(f"✅ 检索到 {len(docs)} 个相关文档")
            return context

        except Exception as e:
            logger.error(f"❌ 检索失败: {e}", exc_info=True)
            return ""


# 创建全局实例
rag_system = RAGSystem()