import json
import os
from utils.helpers import get_base_path

CONFIG_FILE = os.path.join(get_base_path(), "config.json")


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_config(username, observers, assistants):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"username": username, "observers": observers, "assistants": assistants},
                  f, indent=2, ensure_ascii=False)