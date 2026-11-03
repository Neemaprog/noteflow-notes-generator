from pathlib import Path

from docx import Document


def extract_docx_text(file_path: str | Path) -> str:
    document = Document(str(file_path))
    text_chunks: list[str] = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:
            text_chunks.append(text)

    for table in document.tables:
        for row in table.rows:
            values = [cell.text.strip() for cell in row.cells]
            combined = " | ".join(value for value in values if value)
            if combined:
                text_chunks.append(combined)

    return "\n\n".join(text_chunks).strip()
