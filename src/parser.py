import os
import json
from pathlib import Path
from typing import List
from groq import Groq
from src.config import LLM_MODEL
from src.schemas import FinancialContext


def _resolve_model(client: Groq) -> str:
    if LLM_MODEL:
        return LLM_MODEL

    preferred_models = (
        "openai/gpt-oss-120b",
        "llama-3.3-70b-versatile",
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "qwen/qwen3-32b",
    )
    available_models = {model.id for model in client.models.list().data}
    for model_id in preferred_models:
        if model_id in available_models:
            return model_id

    raise RuntimeError(
        "No supported Groq chat model is available. Set GROQ_MODEL to a model "
        "listed by your Groq account."
    )


def parse_request_context(prompt: str, media_paths: List[Path]) -> FinancialContext:
    """Parses text prompts using Groq."""
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Set it in PowerShell or add it to a .env file."
        )

    client = Groq(api_key=api_key)
    model = _resolve_model(client)

    system_prompt = (
        "You are a precise financial parser. Extract all numerical amounts, "
        "recurring commitments, income dates, pending bills, minimum balance floors, "
        "and requested expense details from the context.\n"
        "You MUST output raw valid JSON matching this schema:\n"
        "{\n"
        '  "current_balance": float,\n'
        '  "min_required_balance": float,\n'
        '  "requested_item_price": float,\n'
        '  "confirmed_incomes": [{"date": "YYYY-MM-DD", "amount": float}],\n'
        '  "recurring_expenses": [{"date": "YYYY-MM-DD", "amount": float, "category": "str", "essential": bool}],\n'
        '  "pending_payments": [{"date": "YYYY-MM-DD", "amount": float, "category": "str", "essential": bool}]\n'
        "}"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User Request Context:\n{prompt}"}
        ],
        response_format={"type": "json_object"},
        temperature=0.0
    )

    raw_json = response.choices[0].message.content
    parsed_dict = json.loads(raw_json)

    return FinancialContext(**parsed_dict)
