import json
import random
import sys
import os

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        # Если запущено как скрипт, возвращаем родительскую папку (где лежит main.py)
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_random_effect():
    list_path = os.path.join(get_base_path(), "list.json")
    try:
        with open(list_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        effects = data.get("random_effects", [])
        if not effects:
            return "Нет эффектов в списке"
        return random.choice(effects)
    except Exception as e:
        return f"Ошибка загрузки эффектов: {e}"