import os
import random
import json
from pathlib import Path
from typing import List
from .config import load_config

def _read_state(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"images_dir": "", "used": []}

def _write_state(path: str, state: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f)

def _all_images(images_dir: str) -> List[str]:
    p = Path(images_dir)
    if not p.exists():
        return []
    exts = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    files = [str(fp) for fp in p.iterdir() if fp.is_file() and fp.suffix.lower() in exts]
    return files

def pick_random_image() -> str:
    cfg = load_config()
    state = _read_state(cfg.app_state_file)
    imgs = _all_images(cfg.images_dir)
    used_set = set(state.get("used", []))
    candidates = [i for i in imgs if i not in used_set]
    if not imgs:
        raise RuntimeError("No images found in IMAGES_DIR.")
    if not candidates:
        state["used"] = []
        _write_state(cfg.app_state_file, state)
        candidates = imgs
    choice = random.choice(candidates)
    state["images_dir"] = cfg.images_dir
    state_used = set(state.get("used", []))
    state_used.add(choice)
    state["used"] = list(state_used)
    _write_state(cfg.app_state_file, state)
    return choice
