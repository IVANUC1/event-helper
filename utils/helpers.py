import sys
import time
import requests
import json
import os

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



def check_github_update():
    url = 'https://api.github.com/repos/IVANUC1/event-helper/releases/latest'
    try:
        response = requests.get(url, timeout=7)
        if response.status_code != 200:
            print(f"[Update] GitHub вернул статус {response.status_code}")
            return None
        data = response.json()
        if not isinstance(data, dict):
            print("[Update] Неожиданный формат ответа GitHub")
            return None
        name = data.get('name')
        if not name or not isinstance(name, str):
            print("[Update] В ответе GitHub нет поля 'name'")
            return None
        return name.lstrip('vV')

    except requests.exceptions.Timeout:
        print("[Update] Таймаут при запросе к GitHub")
        return None
    except requests.exceptions.ConnectionError:
        print("[Update] Нет подключения к интернету")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[Update] Ошибка сети: {e}")
        return None
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        print(f"[Update] Ошибка разбора ответа GitHub: {e}")
        return None

def time_detector():
    now = int(time.time())
    return f'<t:{now}:f>'


def text_generator(start_time, event_type, watcher='', end_time=''):
    from ui.app_state import state

    full_username = state.username_var.get()
    selected_assistants = [name for name, var in state.assistant_vars.items() if var.get()]

    if selected_assistants:
        full_username += " " + " ".join(selected_assistants)

    text = f'1. {event_type}\n2. {start_time}\n3. {end_time}\n4. {full_username}'
    if watcher:
        text += f'\n5. {watcher}'
    return text