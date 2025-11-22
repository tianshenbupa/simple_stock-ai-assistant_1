from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import settings


class PDFLoader:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

    def load_all_pdfs(self):
        """加载所有 PDF 文件"""
        documents = []
        pdf_dir = Path(settings.pdf_directory)

        if not pdf_dir.exists():
            return documents

        for pdf_file in pdf_dir.glob("**/*.pdf"):
            try:
                loader = PyPDFLoader(str(pdf_file))
                docs = loader.load()

                # 添加元数据
                for doc in docs:
                    doc.metadata["company"] = pdf_file.stem.split("_")[0]

                documents.extend(docs)
            except Exception as e:
                print(f"加载失败 {pdf_file}: {e}")

        return self.splitter.split_documents(documents)