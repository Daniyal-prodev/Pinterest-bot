# Pinterest-bot

Windows 10 automation tool that:
- Opens regular Google Chrome (default profile, not incognito)
- Goes to https://www.pinterest.com/pin-creation-tool/
- Speaks a prompt asking you to type:
  - ChatGPT prompt
  - Board name
  - Destination link
- Uses OpenRouter OpenAI API to generate only useful data: Title, Description, Tags
- Fills the fields on Pinterest, uploads a random image from your folder without repeating until all are used, selects the board, sets the link, and publishes
- Repeats in a loop

## Prerequisites

- Windows 10 with Google Chrome installed
- You are logged into Pinterest in Chrome’s Default profile
- An OpenRouter API key
- An images folder at `Z:\family` (or set `IMAGES_DIR` to your path)

## Setup

1) Create a `.env` file in the repo root:
```
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openrouter/auto
IMAGES_DIR=Z:\family
```

2) Install Python dependencies (optional if using the .exe):
```
pip install -r requirements.txt
```

## Run from source

```
python -m pinterest_bot
```

- The app will speak a message asking you to type your prompt, board name, and link.
- If Chrome is not logged in to Pinterest, log in in the opened window, then press Enter in the console to continue.
- The tool will generate content, fill the fields, click image upload, wait ~10 seconds, upload a random non-repeated image from your images folder, select the board, set the link, and publish.
- It will then ask if you want to run again.

## Windows executable

This repo contains a GitHub Actions workflow that builds a Windows .exe.
- On push or PR, an artifact `PinterestBot.exe` is produced.
- Download it from the Actions run artifacts and place it on your Windows machine.
- Ensure `.env` exists in the same folder as the exe, or in the working directory where you run it.
- Ensure Chrome is logged in on the Default profile.

## Image reuse prevention

State is stored at `%APPDATA%\PinterestBot\state.json`. It tracks used image paths. When all images have been used, it resets and starts over.

## Notes

- Tags are comma-separated. If Pinterest’s tags input is not present, hashtags are appended at the end of the description.
- This tool does not automate chat.openai.com; it uses the OpenRouter API.
- The API key is loaded from `.env` and is not committed.

## Troubleshooting

- If selectors change on Pinterest, fields may not be found. Open an issue with details.
- If you see login pages, complete login and press Enter in the console to continue.
- If no images are found in your folder, set `IMAGES_DIR` to the correct path in `.env`.
