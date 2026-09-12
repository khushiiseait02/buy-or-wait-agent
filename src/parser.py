import os
import base64
from pathlib import Path
from typing import List
from openai import OpenAI
from src.schemas import FinancialContext
from src.config import OPENAI_API_KEY, LLM_MODEL

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def encode_image(image_path: Path) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def parse_request_context(prompt: str, media_paths: List[Path]) -> FinancialContext:
    if not client:
        raise ValueError("OPENAI_API_KEY environment variable is missing.")

    messages = [
        {
            "role": "system",
            "content": (
                "You are a precise financial parser. Extract all numerical amounts, "
                "recurring commitments, income dates, pending bills, minimum balance floors, "
                "and requested expense details from the context and images."
            )
        }
    ]

    content = [{"type": "text", "text": f"User Request Context:\n{prompt}"}]

    for path in media_paths:
        if path.exists() and path.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
            base64_img = encode_image(path)
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
            })

    messages.append({"role": "user", "content": content})

    response = client.beta.chat.completions.parse(
        model=LLM_MODEL,
        messages=messages,
        response_format=FinancialContext,
        temperature=0.0
    )

    return response.parsed
