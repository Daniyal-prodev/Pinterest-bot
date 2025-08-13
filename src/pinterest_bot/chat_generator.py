import os
import json
import re
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pydantic import BaseModel, Field
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

@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1, min=1, max=10), reraise=True, retry=retry_if_exception_type(Exception))
def _call_openrouter(headers: dict, body: dict, url: str) -> dict:
    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=60)
    if resp.status_code >= 500:
        raise requests.HTTPError(f"Server error {resp.status_code}")
    resp.raise_for_status()
    return resp.json()

def _extract_json_block(text: str) -> str:
    text = text.strip().strip("`").strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text

def _sanitize_tags(tags: list[str]) -> list[str]:
    clean = []
    for t in tags:
        t = t.strip().strip("#").replace("\u200b", "").replace("\u2060", "")
        t = re.sub(r"[^A-Za-z0-9\-\s]", "", t)
        t = re.sub(r"\s+", " ", t).strip()
        if t:
            clean.append(t[:30])
    return clean[:10]

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
    data = _call_openrouter(headers, body, url)
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    json_str = _extract_json_block(content)
    try:
        parsed = json.loads(json_str)
    except Exception:
        cleaned = (json_str or "").replace("\n", " ").replace("\r", " ")
        parsed = {"title": cleaned[:100] or "Title", "description": cleaned[:500] or "Description", "tags": []}
    if "tags" in parsed and isinstance(parsed["tags"], str):
        parsed["tags"] = [t.strip() for t in parsed["tags"].split(",") if t.strip()]
    parsed["tags"] = _sanitize_tags(parsed.get("tags") or [])
    gc = GeneratedContent(**parsed)
    if len(gc.title) > 100:
        gc.title = gc.title[:100].rstrip()
    if len(gc.description) > 500:
        gc.description = gc.description[:500].rstrip()
    return gc
