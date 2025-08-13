import pyttsx3

def speak(text: str):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass

def prompt_inputs():
    speak("Please type your ChatGPT prompt, the board name, and the destination link.")
    prompt_text = input("Enter ChatGPT prompt: ").strip()
    board_name = input("Enter Pinterest Board name: ").strip()
    destination_link = input("Enter destination link (URL): ").strip()
    return prompt_text, board_name, destination_link
