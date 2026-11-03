from pathlib import Path

import fitz


def extract_pdf_text(file_path: str | Path) -> str:
    path = Path(file_path)
    text_chunks: list[str] = []

    with fitz.open(path) as document:
        for page in document:
            page_text = page.get_text("text").strip()
            if page_text:
                text_chunks.append(page_text)

    return "\n\n".join(text_chunks).strip()
