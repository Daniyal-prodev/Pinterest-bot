import time
import logging
from urllib.parse import urlparse
from pathlib import Path
from .config import load_config
from .tts import speak, prompt_inputs
from .chat_generator import generate_content
from .browser import get_driver, ensure_logged_in
from .image_picker import pick_random_image
from .pinterest import open_pin_creator, fill_title_description_tags, upload_image, select_board, set_link, publish

def _setup_logging(log_file: str):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

def _startup_validation(cfg) -> None:
    problems = []
    if not cfg.openrouter_api_key:
        problems.append("Missing OPENROUTER_API_KEY (or OPENAI_API_KEY).")
    if not Path(cfg.images_dir).exists():
        problems.append(f"IMAGES_DIR does not exist: {cfg.images_dir}")
    if problems:
        raise RuntimeError("Startup validation failed: " + "; ".join(problems))

def _valid_url(u: str) -> bool:
    try:
        p = urlparse(u)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False

def _valid_board(name: str) -> bool:
    return 0 < len(name.strip()) <= 100

def run_once():
    cfg = load_config()
    _setup_logging(cfg.log_file)
    _startup_validation(cfg)
    prompt_text, board_name, destination_link = prompt_inputs()
    if not _valid_board(board_name):
        raise ValueError("Invalid board name.")
    if not _valid_url(destination_link):
        raise ValueError("Invalid destination URL.")
    logging.info("Generating content with OpenRouter.")
    content = generate_content(prompt_text)
    speak("Generating content complete. Opening Pinterest.")
    with get_driver(cfg.chrome_user_data_dir, cfg.chrome_profile_directory) as driver:
        ensure_logged_in(driver)
        open_pin_creator(driver)
        fill_title_description_tags(driver, content.title, content.description, content.tags)
        speak("Uploading image.")
        img = pick_random_image()
        logging.info(f"Uploading image: {img}")
        upload_image(driver, img)
        select_board(driver, board_name)
        set_link(driver, destination_link)
        publish(driver)
    speak("Pin published.")
    logging.info("Pin published successfully.")

def main():
    cfg = load_config()
    _setup_logging(cfg.log_file)
    while True:
        try:
            run_once()
        except Exception:
            logging.exception("Run failed")
            speak("An error occurred.")
        time.sleep(cfg.rate_limit_seconds)
        again = input("Do you want to create another pin? (y/n): ").strip().lower()
        if again != "y":
            break

if __name__ == "__main__":
    main()
