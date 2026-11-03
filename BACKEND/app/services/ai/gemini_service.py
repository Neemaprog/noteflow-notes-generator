from google import genai

from app.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY.strip())


def extract_text_from_image(file_path: str) -> str:
    prompt = (
        "Extract all readable text from this image or scanned document. "
        "Return only the extracted text, with no extra commentary."
    )

    uploaded_file = client.files.upload(file=file_path)
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[prompt, uploaded_file],
    )
    return (response.text or "").strip()