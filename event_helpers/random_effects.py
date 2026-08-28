import json
import random
import sys
import os


def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_random_effect():
    list_path = os.path.join(get_base_path(), "list.json")
    try:
        with open(list_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        # ищем ключ, игнорируя пробелы по краям
        effects = []
        for key in data:
            if key.strip() == "random_effects":
                effects = data[key]
                break
        if not effects:
            return "Нет эффектов в списке"
        return random.choice(effects)
    except Exception as e:
        return f"Ошибка загрузки эффектов: {e}"