"""
Structure-Preserving Document Extractor for Aegis.
Extracts text, pages, and section context from PDF, TXT, and images.
"""

import io
import re
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

try:
    import pymupdf as fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    try:
        import fitz
        HAS_PYMUPDF = True
    except ImportError:
        HAS_PYMUPDF = False

try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

logger = logging.getLogger("aegis.extractor")


class ExtractedPage(BaseModel):
    page_number: int
    text: str
    headings: List[str] = Field(default_factory=list)
    char_count: int = 0


class ExtractedDocument(BaseModel):
    document_id: str
    filename: str
    file_type: str
    total_pages: int
    pages: List[ExtractedPage]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentExtractor:
    """
    Extracts text and page-level structural provenance from multi-format files.
    """

    def extract(self, document_id: str, filename: str, content: bytes, file_type: str) -> ExtractedDocument:
        normalized_ext = file_type.lower().replace(".", "")

        if normalized_ext == "pdf":
            return self._extract_pdf(document_id, filename, content)
        elif normalized_ext == "txt":
            return self._extract_txt(document_id, filename, content)
        elif normalized_ext in {"png", "jpg", "jpeg"}:
            return self._extract_image(document_id, filename, content, normalized_ext)
        else:
            raise ValueError(f"Unsupported extraction format: {file_type}")

    def _extract_pdf(self, document_id: str, filename: str, content: bytes) -> ExtractedDocument:
        pages: List[ExtractedPage] = []

        if HAS_PYMUPDF:
            doc = fitz.open(stream=content, filetype="pdf")
            total_pages = len(doc)
            for page_idx in range(total_pages):
                page = doc[page_idx]
                text = page.get_text("text").strip()
                headings = self._identify_headings(text)
                pages.append(
                    ExtractedPage(
                        page_number=page_idx + 1,
                        text=text,
                        headings=headings,
                        char_count=len(text),
                    )
                )
            doc.close()
        elif HAS_PYPDF:
            reader = pypdf.PdfReader(io.BytesIO(content))
            total_pages = len(reader.pages)
            for page_idx, page in enumerate(reader.pages):
                text = (page.extract_text() or "").strip()
                headings = self._identify_headings(text)
                pages.append(
                    ExtractedPage(
                        page_number=page_idx + 1,
                        text=text,
                        headings=headings,
                        char_count=len(text),
                    )
                )
        else:
            raise RuntimeError("Neither PyMuPDF nor pypdf is installed for PDF parsing")

        return ExtractedDocument(
            document_id=document_id,
            filename=filename,
            file_type="pdf",
            total_pages=len(pages),
            pages=pages,
            metadata={"parser": "pymupdf" if HAS_PYMUPDF else "pypdf"},
        )

    def _extract_txt(self, document_id: str, filename: str, content: bytes) -> ExtractedDocument:
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = content.decode("latin-1", errors="replace")

        text = text.strip()
        headings = self._identify_headings(text)

        # Logical page representation for text documents
        pages = [
            ExtractedPage(
                page_number=1,
                text=text,
                headings=headings,
                char_count=len(text),
            )
        ]

        return ExtractedDocument(
            document_id=document_id,
            filename=filename,
            file_type="txt",
            total_pages=1,
            pages=pages,
            metadata={"parser": "text-plain"},
        )

    def _extract_image(self, document_id: str, filename: str, content: bytes, file_type: str) -> ExtractedDocument:
        """
        Extract text from images using Amazon Textract OCR.
        """
        logger.info(f"Extracting image document {filename} using Amazon Textract")
        extracted_text = ""
        try:
            import boto3
            textract = boto3.client("textract", region_name="ap-south-1")
            response = textract.detect_document_text(Document={"Bytes": content})
            lines = [
                item["Text"]
                for item in response.get("Blocks", [])
                if item.get("BlockType") == "LINE"
            ]
            extracted_text = "\n".join(lines)
            logger.info(f"Amazon Textract successfully extracted {len(lines)} lines from {filename}")
        except Exception as e:
            logger.warning(f"Amazon Textract extraction fallback for {filename}: {e}")
            extracted_text = f"[Image Document: {filename}]"

        headings = self._identify_headings(extracted_text)
        pages = [
            ExtractedPage(
                page_number=1,
                text=extracted_text,
                headings=headings,
                char_count=len(extracted_text),
            )
        ]
        return ExtractedDocument(
            document_id=document_id,
            filename=filename,
            file_type=file_type,
            total_pages=1,
            pages=pages,
            metadata={"parser": "amazon-textract"},
        )

    def _identify_headings(self, text: str) -> List[str]:
        """
        Heuristic detection of headings and section markers.
        """
        headings = []
        for line in text.splitlines():
            line = line.strip()
            # Markdown header #, or numbered section 1.1, or short uppercase line
            if re.match(r"^#{1,4}\s+.+", line) or re.match(r"^\d+(\.\d+)*\s+[A-Z].+", line):
                headings.append(line)
            elif line.isupper() and 3 < len(line) < 60:
                headings.append(line)
        return headings[:5]  # Keep top salient headings
