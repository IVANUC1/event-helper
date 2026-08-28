import tkinter as tk
import time
import requests

from ui.app_state import state


def fetch_server_stats(server_ids):
    ids_str = ",".join(str(sid) for sid in server_ids)
    url = f"https://api.scplist.kr/api/v2/servers/players?serverIds={ids_str}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"Ошибка запроса к API: {e}")
        return None


def create_server_stats_tab(notebook):
    server_tab = tk.Frame(notebook)
    notebook.add(server_tab, text="Статистика серверов")

    main_frame = tk.Frame(server_tab)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    tk.Label(main_frame, text="Статус серверов", font=('Arial', 14, 'bold')).pack(
        anchor='w', pady=(0, 10))

    info_frame = tk.Frame(main_frame)
    info_frame.pack(fill=tk.BOTH, expand=True)

    stats_text = tk.Text(info_frame, height=10, width=50, font=('Courier', 11), wrap=tk.WORD)
    stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = tk.Scrollbar(info_frame, orient=tk.VERTICAL, command=stats_text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    stats_text.config(yscrollcommand=scrollbar.set)

    last_update_label = tk.Label(main_frame, text="Последнее обновление: никогда",
                                 font=('Arial', 9), fg='gray')
    last_update_label.pack(anchor='w', pady=(5, 0))

    btn_frame = tk.Frame(main_frame)
    btn_frame.pack(anchor='w', pady=10)

    status_label = tk.Label(btn_frame, text="", font=('Arial', 9))

    server_ids = [65180, 78851]

    def update_stats():
        data = fetch_server_stats(server_ids)
        if data:
            stats_text.delete(1.0, tk.END)
            for server in data:
                server_id = server.get('serverId', 'N/A')
                current = server.get('current', 0)
                max_players = server.get('max', 0)
                stats_text.insert(tk.END, f"Сервер ID: {server_id}\n")
                stats_text.insert(tk.END, f"Игроков: {current} / {max_players}\n")
                stats_text.insert(tk.END,
                                  f"Статус: {'🟢 Онлайн' if current > 0 else '🔴 Офлайн'}\n")
                stats_text.insert(tk.END, "-" * 30 + "\n")
            last_update_label.config(
                text=f"Последнее обновление: {time.strftime('%H:%M:%S')}")
        else:
            stats_text.delete(1.0, tk.END)
            stats_text.insert(tk.END,
                              "⚠️ Не удалось получить данные о серверах.\n"
                              "Проверьте подключение к интернету.")

    def do_refresh(text_widget, button, label):
        status_label.config(text="🔄 Обновление...", fg='blue')
        state.root.update()
        update_stats()
        status_label.config(text="✅ Обновлено!", fg='green')
        button.config(state=tk.NORMAL, text="Обновить вручную")
        state.root.after(2000, lambda: status_label.config(text=""))

    def manual_refresh(text_widget, button, label):
        button.config(state=tk.DISABLED, text="Обновление...")
        status_label.config(text="⏳ Ожидание 5 секунд...", fg='orange')
        state.root.update()
        state.root.after(5000, lambda: do_refresh(text_widget, button, label))

    refresh_btn = tk.Button(
        btn_frame,
        text="Обновить вручную",
        command=lambda: manual_refresh(stats_text, refresh_btn, last_update_label),
        bg="#cfe2f3",
        width=20
    )
    refresh_btn.pack(side=tk.LEFT, padx=5)
    status_label.pack(side=tk.LEFT, padx=10)

    def auto_update():
        update_stats()
        state.root.after(90000, auto_update)

    update_stats()
    state.root.after(90000, auto_update)