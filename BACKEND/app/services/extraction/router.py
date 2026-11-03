from pathlib import Path

from .docx_extractor import extract_docx_text
from .pdf_extractor import extract_pdf_text
from .pptx_extractor import extract_pptx_text


def extract_document_text(file_path: str | Path, file_type: str) -> str:
    extractor_map = {
        "pdf": extract_pdf_text,
        "docx": extract_docx_text,
        "pptx": extract_pptx_text,
    }

    normalized_type = (file_type or "").strip().lower()
    extractor = extractor_map.get(normalized_type)
    if extractor is None:
        raise ValueError(f"Unsupported document type for extraction: {file_type}")

    return extractor(file_path)
