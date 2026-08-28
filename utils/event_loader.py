import json
import os
import sys
import tkinter as tk
from tkinter import messagebox
from utils.helpers import get_base_path


def _find_key(data, name):
    """Ищет ключ в словаре, игнорируя пробелы по краям и BOM."""
    clean = name.strip().lstrip('\ufeff')
    for key in data:
        if key.strip().lstrip('\ufeff') == clean:
            return data[key]
    raise KeyError(name)


def get_description(descriptions_dict, event_name):
    """Ищет описание ивента, игнорируя пробелы по краям."""
    if event_name in descriptions_dict:
        return descriptions_dict[event_name]
    clean = event_name.strip()
    for key, value in descriptions_dict.items():
        if key.strip() == clean:
            return value
    return ""


def load_events():
    list_path = os.path.join(get_base_path(), "list.json")
    try:
        # utf-8-sig автоматически убирает BOM, если он есть в файле
        with open(list_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        events_left = _find_key(data, "дополнения обычного раунда")
        events_right = _find_key(data, "вне обычного раунда")
        try:
            descriptions = _find_key(data, "descriptions")
        except KeyError:
            descriptions = {}
        return events_left, events_right, descriptions
    except FileNotFoundError:
        messagebox.showerror("Ошибка", f"Файл list.json не найден в папке с программой.\n{list_path}")
        sys.exit(1)
    except KeyError as e:
        messagebox.showerror("Ошибка", f"В файле list.json нет раздела {e}")
        sys.exit(1)
    except json.JSONDecodeError:
        messagebox.showerror("Ошибка", "Файл list.json повреждён. Проверьте его формат.")
        sys.exit(1)


def render_description(text_widget, raw_text):
    text_widget.delete(1.0, tk.END)

    if not raw_text:
        text_widget.insert(tk.END, "Описание отсутствует.")
        return

    lines = raw_text.split("/n")
    for line in lines:
        pos = 0
        while pos < len(line):
            if line.startswith(".///", pos):
                end = line.find("///.", pos + 4)
                if end != -1:
                    inner = line[pos + 4:end]
                    text_widget.insert(tk.END, inner, "desc_xlarge")
                    pos = end + 4
                    continue
            if line.startswith(".//", pos):
                end = line.find("//.", pos + 3)
                if end != -1:
                    inner = line[pos + 3:end]
                    text_widget.insert(tk.END, inner, "desc_large")
                    pos = end + 3
                    continue
            if line.startswith("./", pos):
                end = line.find("/.", pos + 2)
                if end != -1:
                    inner = line[pos + 2:end]
                    text_widget.insert(tk.END, inner, "desc_medium")
                    pos = end + 2
                    continue

            next_marker = len(line)
            for marker in [".///", ".//", "./"]:
                idx = line.find(marker, pos)
                if idx != -1 and idx < next_marker:
                    next_marker = idx

            if next_marker > pos:
                text_widget.insert(tk.END, line[pos:next_marker], "desc_normal")
                pos = next_marker
            else:
                text_widget.insert(tk.END, line[pos:], "desc_normal")
                break
        text_widget.insert(tk.END, "\n")