import os
import json
import requests
from pydantic import BaseModel, Field, ValidationError
from .config import load_config

class GeneratedContent(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=500)
    tags: list[str] = Field(min_length=1)

def _build_messages(user_prompt: str) -> list[dict]:
    system = "You produce ONLY strict JSON with keys: title (string, <=100 chars), description (string, <=500 chars), tags (array of 3-8 short strings). Output only JSON."
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_prompt},
    ]

def generate_content(user_prompt: str) -> GeneratedContent:
    cfg = load_config()
    headers = {
        "Authorization": f"Bearer {cfg.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/Daniyal-prodev/Pinterest-bot",
        "X-Title": "PinterestBot",
    }
    body = {
        "model": cfg.openrouter_model,
        "messages": _build_messages(user_prompt),
        "temperature": 0.3,
    }
    url = f"{cfg.openrouter_base_url.rstrip('/')}/chat/completions"
    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=60)
    resp.raise_for_status()
    data = resp.json()
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    content_str = content.strip().strip("`").strip()
    try:
        parsed = json.loads(content_str)
    except json.JSONDecodeError:
        cleaned = content_str.replace("\n", " ").replace("\r", " ")
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            parsed = json.loads(cleaned[start : end + 1])
        else:
            raise
    if "tags" in parsed and isinstance(parsed["tags"], str):
        parsed["tags"] = [t.strip() for t in parsed["tags"].split(",") if t.strip()]
    gc = GeneratedContent(**parsed)
    if len(gc.title) > 100:
        gc.title = gc.title[:100].rstrip()
    if len(gc.description) > 500:
        gc.description = gc.description[:500].rstrip()
    gc.tags = [t for t in gc.tags if t]
    return gc
