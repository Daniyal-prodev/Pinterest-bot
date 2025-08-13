import time
from .config import load_config
from .tts import speak, prompt_inputs
from .chat_generator import generate_content
from .browser import get_driver, ensure_logged_in
from .image_picker import pick_random_image
from .pinterest import open_pin_creator, fill_title_description_tags, upload_image, select_board, set_link, publish

def run_once():
    cfg = load_config()
    prompt_text, board_name, destination_link = prompt_inputs()
    content = generate_content(prompt_text)
    speak("Generating content complete. Opening Pinterest.")
    with get_driver(cfg.chrome_user_data_dir, cfg.chrome_profile_directory) as driver:
        ensure_logged_in(driver)
        open_pin_creator(driver)
        fill_title_description_tags(driver, content.title, content.description, content.tags)
        speak("Uploading image.")
        img = pick_random_image()
        upload_image(driver, img)
        select_board(driver, board_name)
        set_link(driver, destination_link)
        publish(driver)
    speak("Pin published.")

def main():
    while True:
        try:
            run_once()
        except Exception as e:
            print(f"Error: {e}")
            speak("An error occurred.")
        again = input("Do you want to create another pin? (y/n): ").strip().lower()
        if again != "y":
            break

if __name__ == "__main__":
    main()
