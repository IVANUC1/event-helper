import tkinter as tk
from tkinter import messagebox
import webbrowser
import requests
import json
import sys
import os

from utils.helpers import check_github_update
from utils.config_manager import load_config, save_config, CONFIG_FILE
from ui.main_window import build_main_ui
from ui.app_state import state


def main():
    root = tk.Tk()
    root.title("Event helper")
    root.geometry("900x1000")
    state.root = root

    username_var = tk.StringVar()
    state.username_var = username_var

    update = check_github_update()

    config = load_config()

    update = check_github_update()
    config = load_config()

    if update is not None:
        try:
            version = None
            if os.path.exists('list.json'):
                with open('list.json', 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
                for key in data:
                    if key.strip().lower() == "version":
                        version = data[key]
                        break
            else:
                print("[Update] Файл list.json не найден")

            if not version:
                print("[Update] Не удалось найти версию в list.json")
            else:
                try:
                    current_version = float(version)
                    last_version = float(update)

                    if current_version < last_version:
                        webbrowser.open(
                            f"https://github.com/IVANUC1/event-helper/releases/tag/event_helper_{update}"
                        )
                except ValueError as e:
                    print(f"[Update] Ошибка сравнения версий (текущая: {version}, новая: {update}): {e}")
        except json.JSONDecodeError as e:
            print(f"[Update] Ошибка чтения list.json: {e}")
        except Exception as e:
            print(f"[Update] Непредвиденная ошибка: {e}")

    if config is None:
        setup_win = tk.Toplevel(root)
        setup_win.title("Добро пожаловать!")
        setup_win.geometry("400x300")
        setup_win.transient(root)
        setup_win.grab_set()

        tk.Label(setup_win, text="Привет! Как к тебе обращаться?", font=('Arial', 11)).pack(pady=10)
        username_entry = tk.Entry(setup_win, width=30)
        username_entry.pack(pady=5)
        tk.Label(setup_win, text="Напиши своё имя с @, например @ivanuc1", font=('Arial', 9)).pack()

        default_observers = ["@dr.how.to.play", "@d1ff123_52512"]
        default_assistants = []

        tk.Label(setup_win, text=f"Наблюдатели по умолчанию:\n{', '.join(default_observers)}",
                 font=('Arial', 9), justify='left').pack(pady=5)
        tk.Label(setup_win, text="Помощники пока пусты — добавишь позже в настройках",
                 font=('Arial', 9), justify='left').pack(pady=5)

        def save_and_continue():
            username = username_entry.get().strip()
            if not username:
                messagebox.showerror("Ошибка", "Имя не может быть пустым!")
                return
            if not username.startswith('@'):
                username = '@' + username
            save_config(username, default_observers, default_assistants)
            setup_win.destroy()
            build_main_ui()

        tk.Button(setup_win, text="Поехали!", command=save_and_continue,
                  bg="lightgreen", width=20).pack(pady=20)

        def on_setup_close():
            root.destroy()
            sys.exit(0)

        setup_win.protocol("WM_DELETE_WINDOW", on_setup_close)
        root.wait_window(setup_win)

        if not os.path.exists(CONFIG_FILE):
            root.destroy()
            sys.exit(0)
    else:
        if "assistants" not in config:
            config["assistants"] = []
            save_config(config["username"], config["observers"], config["assistants"])
        build_main_ui()

    root.mainloop()


if __name__ == "__main__":
    main()