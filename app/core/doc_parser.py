import os
from typing import Optional


class DocumentParser:
    """文档解析器 —— 支持 .txt / .md / .docx / .pdf"""

    MAX_SIZE_MB = 10
    ALLOWED_EXTENSIONS = {".txt", ".md", ".docx", ".doc", ".pdf"}

    @classmethod
    def parse(cls, filepath: str, filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise ValueError(f"不支持的文件格式: {ext}，支持: {', '.join(cls.ALLOWED_EXTENSIONS)}")

        if ext in (".txt", ".md"):
            return cls._parse_text(filepath)
        elif ext in (".docx", ".doc"):
            return cls._parse_docx(filepath)
        elif ext == ".pdf":
            return cls._parse_pdf(filepath)

        return ""

    @staticmethod
    def _parse_text(filepath: str) -> str:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    @staticmethod
    def _parse_docx(filepath: str) -> str:
        try:
            from docx import Document
        except ImportError:
            raise ImportError("请安装 python-docx: pip install python-docx")

        doc = Document(filepath)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)

    @staticmethod
    def _parse_pdf(filepath: str) -> str:
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            raise ImportError("请安装 PyPDF2: pip install PyPDF2")

        reader = PdfReader(filepath)
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())
        return "\n".join(pages)


doc_parser = DocumentParser()
