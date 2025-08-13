import os
import random
import json
import time
from pathlib import Path
from typing import List
from .config import load_config

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

def _norm(p: str) -> str:
    try:
        return os.path.normpath(p)
    except Exception:
        return p

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
    files = []
    for fp in p.iterdir():
        try:
            if fp.is_file() and fp.suffix.lower() in SUPPORTED_EXTS:
                files.append(_norm(str(fp)))
        except Exception:
            continue
    return files

def _refresh_state_for_dir(state: dict, images_dir: str) -> dict:
    if _norm(state.get("images_dir", "")) != _norm(images_dir):
        state["images_dir"] = _norm(images_dir)
        state["used"] = []
    else:
        state["used"] = [u for u in state.get("used", []) if Path(u).exists()]
    return state

def pick_random_image() -> str:
    cfg = load_config()
    state = _read_state(cfg.app_state_file)
    state = _refresh_state_for_dir(state, cfg.images_dir)
    imgs = _all_images(cfg.images_dir)
    if not imgs:
        raise RuntimeError("No images found in IMAGES_DIR.")
    used_set = set(_norm(u) for u in state.get("used", []))
    candidates = [i for i in imgs if _norm(i) not in used_set]
    if not candidates:
        state["used"] = []
        candidates = imgs
    choice = random.choice(candidates)
    used_set.add(_norm(choice))
    state["used"] = list(used_set)
    state["last_run_ts"] = time.time()
    _write_state(cfg.app_state_file, state)
    return choice
