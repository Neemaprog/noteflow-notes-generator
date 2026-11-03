from io import BytesIO
from pathlib import Path
import re

from docx import Document as WordDocument
from fastapi.responses import StreamingResponse
from pptx import Presentation
from pptx.util import Inches
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def _safe_filename(title: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", title).strip("-.")
    return cleaned or "note"


def _plain_text(note) -> str:
    return f"{note.title}\n\n{note.summary or ''}\n\n{note.content}".strip()


def export_note_response(note, output_format: str) -> StreamingResponse:
    base_name = _safe_filename(note.title)

    if output_format == "plain_text":
        content = _plain_text(note).encode("utf-8")
        return StreamingResponse(
            BytesIO(content),
            media_type="text/plain; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{base_name}.txt"'},
        )

    if output_format == "docx":
        document = WordDocument()
        document.add_heading(note.title, level=1)
        if note.summary:
            document.add_paragraph(note.summary)
        for line in note.content.splitlines():
            if line.strip():
                document.add_paragraph(line.lstrip("# ").strip())
        buffer = BytesIO()
        document.save(buffer)
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{base_name}.docx"'},
        )

    if output_format == "pptx":
        presentation = Presentation()
        title_slide = presentation.slides.add_slide(presentation.slide_layouts[0])
        title_slide.shapes.title.text = note.title
        if note.summary:
            title_slide.placeholders[1].text = note.summary
        lines = [line.strip().lstrip("#- ").strip() for line in note.content.splitlines() if line.strip()]
        for start in range(0, len(lines), 7):
            slide = presentation.slides.add_slide(presentation.slide_layouts[1])
            slide.shapes.title.text = note.title
            text_frame = slide.placeholders[1].text_frame
            text_frame.clear()
            for line in lines[start : start + 7]:
                paragraph = text_frame.add_paragraph()
                paragraph.text = line
                paragraph.level = 0
        buffer = BytesIO()
        presentation.save(buffer)
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": f'attachment; filename="{base_name}.pptx"'},
        )

    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=inch, leftMargin=inch)
    styles = getSampleStyleSheet()
    story = [Paragraph(note.title, styles["Title"]), Spacer(1, 0.2 * inch)]
    if note.summary:
        story.extend([Paragraph(note.summary, styles["BodyText"]), Spacer(1, 0.15 * inch)])
    for line in note.content.splitlines():
        if line.strip():
            story.extend([Paragraph(line.replace("&", "&amp;"), styles["BodyText"]), Spacer(1, 0.08 * inch)])
    pdf.build(story)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{base_name}.pdf"'},
    )
