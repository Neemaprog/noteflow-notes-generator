from pathlib import Path

from pptx import Presentation


def extract_pptx_text(file_path: str | Path) -> str:
    presentation = Presentation(str(file_path))
    text_chunks: list[str] = []

    for slide in presentation.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                shape_text = shape.text.strip()
                if shape_text:
                    text_chunks.append(shape_text)

    return "\n\n".join(text_chunks).strip()
