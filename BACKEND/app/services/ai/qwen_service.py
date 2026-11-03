import json
import re
from typing import Any

import httpx

from app.config import settings


class QwenGenerationError(RuntimeError):
    """Raised when Qwen cannot generate a valid notes response."""


def _extract_json(content: str) -> dict[str, str]:
    parsed = _parse_json_object(content)
    title = parsed.get("title")
    summary = parsed.get("summary")
    note_content = parsed.get("content")
    if not all(
        isinstance(value, str) and value.strip()
        for value in (title, summary, note_content)
    ):
        raise QwenGenerationError("Qwen response is missing title, summary, or content")

    return {
        "title": title.strip(),
        "summary": summary.strip(),
        "content": note_content.strip(),
    }


def _parse_json_object(content: str) -> dict[str, Any]:
    candidate = content.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if len(lines) >= 3:
            candidate = "\n".join(lines[1:-1]).strip()

    try:
        parsed: Any = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise QwenGenerationError("Qwen returned invalid JSON") from exc

    if not isinstance(parsed, dict):
        raise QwenGenerationError("Qwen returned an invalid notes object")
    return parsed


def generate_notes(
    extracted_text: str,
    *,
    style: str,
    language: str,
    output_format: str,
    custom_instruction: str | None = None,
) -> dict[str, str]:
    if not settings.DASHSCOPE_API_KEY:
        raise QwenGenerationError("DASHSCOPE_API_KEY is not configured")

    system_prompt = (
        "You create accurate study notes from source text. Do not invent facts. "
        "Return only a JSON object with exactly these string fields: title, summary, content. "
        "The content must be useful, well-structured notes in the requested format. "
        "When the requested format is plain_text, never use Markdown or HTML syntax. "
        "Use clear plain-text headings, numbered lists, and simple line breaks only."
    )
    instruction_block = (
        f"ADDITIONAL INSTRUCTION:\n{custom_instruction.strip()}\n\n"
        if custom_instruction and custom_instruction.strip()
        else ""
    )
    user_prompt = (
        f"Create {style} in {language} using {output_format} format.\n"
        "Keep the title concise, the summary to 2-4 sentences, and preserve important "
        "definitions, steps, formulas, examples, and headings from the source.\n\n"
        f"{instruction_block}"
        f"SOURCE TEXT:\n{extracted_text}"
    )
    payload = {
        "model": settings.QWEN_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }

    try:
        response = httpx.post(
            f"{settings.DASHSCOPE_BASE_URL.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=120.0,
        )
        response.raise_for_status()
        response_data = response.json()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:500]
        raise QwenGenerationError(f"Qwen API request failed: {detail}") from exc
    except (httpx.RequestError, ValueError) as exc:
        raise QwenGenerationError("Could not reach Qwen or parse its response") from exc

    choices = response_data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise QwenGenerationError("Qwen response did not contain a completion")
    message = choices[0].get("message")
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str):
        raise QwenGenerationError("Qwen response did not contain message content")

    return _extract_json(content)


def continue_conversation(messages: list[dict[str, str]]) -> str:
    if not settings.DASHSCOPE_API_KEY:
        raise QwenGenerationError("DASHSCOPE_API_KEY is not configured")

    payload = {
        "model": settings.QWEN_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful study assistant. Continue the conversation accurately and concisely. Use the conversation context, do not invent facts, and return only the assistant reply as plain text.",
            },
            *messages,
        ],
        "temperature": 0.3,
    }

    try:
        response = httpx.post(
            f"{settings.DASHSCOPE_BASE_URL.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=120.0,
        )
        response.raise_for_status()
        response_data = response.json()
    except httpx.HTTPStatusError as exc:
        raise QwenGenerationError(f"Qwen API request failed: {exc.response.text[:500]}") from exc
    except (httpx.RequestError, ValueError) as exc:
        raise QwenGenerationError("Could not reach Qwen or parse its response") from exc

    choices = response_data.get("choices")
    message = choices[0].get("message") if isinstance(choices, list) and choices else None
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str) or not content.strip():
        raise QwenGenerationError("Qwen response did not contain an assistant reply")
    return content.strip()


def _escape_svg(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _build_visual_svg(
    name: str,
    description: str,
    labels: list[str],
    visual_type: str,
    prompt: str,
    color_scheme: str,
) -> str:
    palette = {
        "light": ("#eef2ff", "#172554", ["#4f46e5", "#0f766e", "#d97706", "#db2777"]),
        "dark": ("#172554", "#f8fafc", ["#818cf8", "#2dd4bf", "#fbbf24", "#f472b6"]),
        "colorful": ("#fdf2f8", "#172554", ["#0f766e", "#7c3aed", "#ea580c", "#2563eb"]),
    }
    background, text_color, accents = palette.get(color_scheme, palette["light"])
    accent = accents[0]
    safe_name = _escape_svg(name)
    safe_description = _escape_svg(description or "AI-generated study visual")
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800">',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#172554"/></marker></defs>',
        f'<rect width="1200" height="800" rx="28" fill="{background}"/>',
        f'<rect x="55" y="55" width="1090" height="690" rx="24" fill="white" opacity="0.78" stroke="{accent}" stroke-width="4"/>',
        f'<text x="95" y="125" font-family="Arial, sans-serif" font-size="32" font-weight="700" fill="{text_color}">{safe_name[:55]}</text>',
        f'<line x1="95" y1="155" x2="1105" y2="155" stroke="{accent}" stroke-width="4"/>',
    ]

    safe_labels = [label[:38] for label in labels]
    is_flowchart = any(
        term in prompt.lower()
        for term in ("flowchart", "flow chart", "process flow", "workflow")
    )
    if is_flowchart:
        count = len(safe_labels)
        start_x, gap, box_width = 105, 30, 210
        row_y = [270, 480]
        for index, label in enumerate(safe_labels):
            row = 0 if index < 4 else 1
            column = index if row == 0 else count - 1 - index
            x = start_x + column * (box_width + gap)
            y = row_y[row]
            color = accents[index % len(accents)]
            if row == 1:
                x = start_x + column * (box_width + gap)
            parts.append(f'<rect x="{x}" y="{y}" width="{box_width}" height="92" rx="18" fill="{color}"/>')
            parts.append(f'<text x="{x + box_width / 2}" y="{y + 54}" text-anchor="middle" font-family="Arial, sans-serif" font-size="19" font-weight="700" fill="white">{_escape_svg(label)}</text>')
            if index < count - 1:
                next_row = 0 if index + 1 < 4 else 1
                next_column = index + 1 if next_row == 0 else count - 2 - index
                next_x = start_x + next_column * (box_width + gap)
                if row == next_row:
                    x1, x2 = (x + box_width, next_x) if row == 0 else (next_x + box_width, x)
                    direction = 1 if row == 0 else -1
                    parts.append(f'<line x1="{x1 + 4 * direction}" y1="{y + 46}" x2="{x2 - 8 * direction}" y2="{y + 46}" stroke="{text_color}" stroke-width="4" marker-end="url(#arrow)"/>')
                else:
                    parts.append(f'<path d="M {x + box_width / 2} {y + 96} V 420 H {next_x + box_width / 2} V {row_y[1] - 8}" fill="none" stroke="{text_color}" stroke-width="4" marker-end="url(#arrow)"/>')
    elif visual_type == "chart":
        for index, label in enumerate(safe_labels):
            column = index % 4
            row = index // 4
            x = 105 + column * 250
            y = 225 + row * 205
            color = accents[index % len(accents)]
            parts.append(f'<rect x="{x}" y="{y}" width="215" height="160" rx="18" fill="{color}" opacity="0.13" stroke="{color}" stroke-width="3"/>')
            parts.append(f'<circle cx="{x + 42}" cy="{y + 42}" r="23" fill="{color}"/>')
            parts.append(f'<text x="{x + 42}" y="{y + 50}" text-anchor="middle" font-family="Arial, sans-serif" font-size="20" font-weight="700" fill="white">{index + 1}</text>')
            parts.append(f'<text x="{x + 22}" y="{y + 92}" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="{text_color}">{_escape_svg(label[:22])}</text>')
            if len(label) > 22:
                parts.append(f'<text x="{x + 22}" y="{y + 120}" font-family="Arial, sans-serif" font-size="17" fill="{text_color}">{_escape_svg(label[22:38])}</text>')
    elif visual_type == "graph":
        count = len(safe_labels)
        points = []
        for index, label in enumerate(safe_labels):
            x = 145 + index * (910 / max(count - 1, 1))
            y = 430 - (index % 2) * 115 - ((index // 2) % 2) * 35
            points.append((x, y, label))
        parts.extend([
            '<line x1="120" y1="600" x2="1080" y2="600" stroke="#94a3b8" stroke-width="3"/>',
            '<line x1="120" y1="230" x2="120" y2="600" stroke="#94a3b8" stroke-width="3"/>',
        ])
        for index in range(len(points) - 1):
            x1, y1, _ = points[index]
            x2, y2, _ = points[index + 1]
            parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{accents[index % len(accents)]}" stroke-width="6"/>')
        for index, (x, y, label) in enumerate(points):
            color = accents[index % len(accents)]
            parts.append(f'<circle cx="{x}" cy="{y}" r="18" fill="{color}" stroke="white" stroke-width="5"/>')
            parts.append(f'<text x="{x}" y="{y + 48}" text-anchor="middle" font-family="Arial, sans-serif" font-size="17" font-weight="700" fill="{text_color}">{_escape_svg(label[:22])}</text>')
    elif visual_type == "infographic":
        for index, label in enumerate(safe_labels):
            column = index % 4
            row = index // 4
            x = 175 + column * 285
            y = 260 + row * 220
            color = accents[index % len(accents)]
            parts.append(f'<rect x="{x - 110}" y="{y}" width="220" height="150" rx="18" fill="{color}" opacity="0.13" stroke="{color}" stroke-width="3"/>')
            parts.append(f'<circle cx="{x}" cy="{y + 42}" r="24" fill="{color}"/>')
            parts.append(f'<text x="{x}" y="{y + 50}" text-anchor="middle" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="white">{index + 1}</text>')
            parts.append(f'<text x="{x}" y="{y + 100}" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="{text_color}">{_escape_svg(label[:24])}</text>')
    else:
        center_x, top_y = 600, 265
        parts.append(f'<rect x="415" y="{top_y}" width="370" height="90" rx="20" fill="{accent}"/>')
        parts.append(f'<text x="{center_x}" y="{top_y + 55}" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" font-weight="700" fill="white">{_escape_svg(safe_labels[0][:32])}</text>')
        for index, label in enumerate(safe_labels[1:]):
            column = index % 3
            row = index // 3
            x = 105 + column * 370
            y = 475 + row * 115
            color = accents[(index + 1) % len(accents)]
            parts.append(f'<line x1="{center_x}" y1="{top_y + 92}" x2="{x + 145}" y2="{y}" stroke="{color}" stroke-width="4"/>')
            parts.append(f'<rect x="{x}" y="{y}" width="290" height="70" rx="16" fill="{color}" opacity="0.9"/>')
            parts.append(f'<text x="{x + 145}" y="{y + 43}" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="white">{_escape_svg(label)}</text>')

    parts.append(f'<text x="95" y="700" font-family="Arial, sans-serif" font-size="18" fill="{text_color}">{safe_description[:150]}</text>')
    parts.append("</svg>")
    return "".join(parts)


def generate_visual(
    notes_content: str,
    *,
    visual_type: str,
    prompt: str,
    color_scheme: str,
) -> dict[str, str]:
    if not settings.DASHSCOPE_API_KEY:
        raise QwenGenerationError("DASHSCOPE_API_KEY is not configured")

    system_prompt = (
        "You design accurate study visual layouts from notes and a user's request. "
        "Do not invent facts. Return only a JSON object with exactly these string fields: "
        "name, description, and labels. The labels field must be a JSON array of 3 to 8 "
        "short strings in the correct reading order for the requested visual. For flowcharts, "
        "return the actual steps in sequence; for graphs, return related concepts in a useful "
        "left-to-right order. Do not return SVG, Markdown, or HTML."
    )
    user_prompt = (
        f"Create a {visual_type} with a {color_scheme} color scheme.\n"
        f"USER REQUEST:\n{prompt.strip()}\n\n"
        f"NOTES:\n{notes_content}"
    )
    payload = {
        "model": settings.QWEN_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
    }

    try:
        response = httpx.post(
            f"{settings.DASHSCOPE_BASE_URL.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=120.0,
        )
        response.raise_for_status()
        response_data = response.json()
    except httpx.HTTPStatusError as exc:
        raise QwenGenerationError(f"Qwen API request failed: {exc.response.text[:500]}") from exc
    except httpx.TimeoutException as exc:
        raise QwenGenerationError("Fail to generate, please try again.") from exc
    except httpx.RequestError as exc:
        raise QwenGenerationError("Fail to generate, please try again.") from exc
    except ValueError as exc:
        raise QwenGenerationError("Fail to generate, please try again.") from exc

    choices = response_data.get("choices")
    message = choices[0].get("message") if isinstance(choices, list) and choices else None
    content = message.get("content") if isinstance(message, dict) else None
    if isinstance(content, list):
        content = "".join(
            item.get("text", "") for item in content if isinstance(item, dict)
        )
    if not isinstance(content, str):
        raise QwenGenerationError("Qwen response did not contain visual content")

    parsed = _parse_json_object(content)
    name = parsed.get("name")
    description = parsed.get("description", "")
    labels = parsed.get("labels")
    if not isinstance(name, str) or not isinstance(description, str) or not isinstance(labels, list):
        raise QwenGenerationError("Qwen returned incomplete visual data")
    safe_labels = [str(label).strip() for label in labels if str(label).strip()][:8]
    if not name.strip() or not safe_labels:
        raise QwenGenerationError("Qwen returned invalid visual labels")
    return {
        "name": name.strip(),
        "description": description.strip(),
        "svg": _build_visual_svg(
            name.strip(), description.strip(), safe_labels, visual_type, prompt, color_scheme
        ),
    }
