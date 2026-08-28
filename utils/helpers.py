import sys
import os
import time


def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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