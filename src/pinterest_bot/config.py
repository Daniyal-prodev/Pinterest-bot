import os
import json
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator

class Config(BaseModel):
    openrouter_api_key: str = Field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY", ""))
    openrouter_base_url: str = Field(default_factory=lambda: os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"))
    openrouter_model: str = Field(default_factory=lambda: os.getenv("OPENROUTER_MODEL", "openrouter/auto"))
    images_dir: str = Field(default_factory=lambda: os.getenv("IMAGES_DIR", "Z:\\family"))
    chrome_user_data_dir: str = Field(default_factory=lambda: os.path.join(os.getenv("LOCALAPPDATA", ""), "Google", "Chrome", "User Data"))
    chrome_profile_directory: str = Field(default_factory=lambda: "Default")
    app_state_dir: str = Field(default_factory=lambda: os.path.join(os.getenv("APPDATA", str(Path.home() / "AppData" / "Roaming")), "PinterestBot"))
    app_state_file: str = ""

    @validator("app_state_file", always=True)
    def set_state_file(cls, v, values):
        state_dir = values.get("app_state_dir")
        return os.path.join(state_dir, "state.json")

def load_config() -> Config:
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    if not os.getenv("OPENROUTER_API_KEY") and os.getenv("OPENAI_API_KEY"):
        os.environ["OPENROUTER_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
    cfg = Config()
    Path(cfg.app_state_dir).mkdir(parents=True, exist_ok=True)
    if not Path(cfg.app_state_file).exists():
        with open(cfg.app_state_file, "w", encoding="utf-8") as f:
            json.dump({"images_dir": cfg.images_dir, "used": []}, f)
    return cfg
