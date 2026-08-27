import json
import random
import sys
import os

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_random_item_by_phase(phase_key):
    list_path = os.path.join(get_base_path(), "list.json")
    try:
        with open(list_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        items_dict = data.get("random_items", {})
        items = items_dict.get(phase_key, [])
        if not items:
            return f"Нет предметов для этапа '{phase_key}'"
        return random.choice(items)
    except Exception as e:
        return f"Ошибка загрузки предметов: {e}"