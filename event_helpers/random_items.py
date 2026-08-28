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
        with open(list_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)

        items_dict = {}
        for key in data:
            if key.strip() == "random_items":
                items_dict = data[key]
                break

        # ищем фазу, игнорируя пробелы и регистр
        items = []
        clean = phase_key.strip().lower()
        for key, value in items_dict.items():
            if key.strip().lower() == clean:
                items = value
                break

        if not items:
            return f"Нет предметов для этапа '{phase_key}'"
        return random.choice(items)
    except Exception as e:
        return f"Ошибка загрузки предметов: {e}"