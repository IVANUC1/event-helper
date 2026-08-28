import tkinter as tk
from tkinter import messagebox, simpledialog

from ui.app_state import state
from utils.config_manager import load_config, save_config


def open_settings():
    root = state.root
    settings_win = tk.Toplevel(root)
    settings_win.title("Настройки")
    settings_win.geometry("500x500")
    settings_win.transient(root)
    settings_win.grab_set()

    current_username = state.username_var.get()
    config_data = load_config()
    current_observers = config_data["observers"] if config_data else []
    current_assistants = config_data["assistants"] if config_data else []

    # Имя
    tk.Label(settings_win, text="Ваше имя:", font=('Arial', 10, 'bold')).pack(
        anchor='w', padx=10, pady=(10, 0))
    username_frame = tk.Frame(settings_win)
    username_frame.pack(fill='x', padx=10, pady=5)
    username_entry = tk.Entry(username_frame, width=30)
    username_entry.insert(0, current_username)
    username_entry.pack(side='left')
    tk.Label(username_frame, text=" (например @ivanuc1)", font=('Arial', 9)).pack(
        side='left', padx=5)

    # Наблюдатели
    tk.Label(settings_win, text="Наблюдатели:", font=('Arial', 10, 'bold')).pack(
        anchor='w', padx=10, pady=(10, 0))
    obs_frame = tk.Frame(settings_win)
    obs_frame.pack(fill='both', expand=True, padx=10, pady=5)
    obs_listbox = tk.Listbox(obs_frame, height=4)
    obs_listbox.pack(side='left', fill='both', expand=True)
    obs_scroll = tk.Scrollbar(obs_frame, orient='vertical', command=obs_listbox.yview)
    obs_scroll.pack(side='right', fill='y')
    obs_listbox.config(yscrollcommand=obs_scroll.set)
    for obs in current_observers:
        obs_listbox.insert(tk.END, obs)

    obs_btn_frame = tk.Frame(settings_win)
    obs_btn_frame.pack(fill='x', padx=10, pady=5)

    def add_observer():
        new_obs = simpledialog.askstring("Добавить наблюдателя",
                                         "Введите имя (начинается с @):",
                                         parent=settings_win)
        if new_obs:
            if not new_obs.startswith('@'):
                new_obs = '@' + new_obs
            if new_obs in obs_listbox.get(0, tk.END):
                messagebox.showwarning("Предупреждение", "Такой наблюдатель уже есть!")
                return
            obs_listbox.insert(tk.END, new_obs)

    def remove_observer():
        selected = obs_listbox.curselection()
        if selected:
            obs_listbox.delete(selected[0])

    tk.Button(obs_btn_frame, text="Добавить", command=add_observer, width=10).pack(
        side='left', padx=5)
    tk.Button(obs_btn_frame, text="Удалить", command=remove_observer, width=10).pack(
        side='left', padx=5)

    # Помощники
    tk.Label(settings_win, text="Помощники (co-hosts):", font=('Arial', 10, 'bold')).pack(
        anchor='w', padx=10, pady=(10, 0))
    asst_frame = tk.Frame(settings_win)
    asst_frame.pack(fill='both', expand=True, padx=10, pady=5)
    asst_listbox = tk.Listbox(asst_frame, height=4, selectmode=tk.SINGLE)
    asst_listbox.pack(side='left', fill='both', expand=True)
    asst_scroll = tk.Scrollbar(asst_frame, orient='vertical', command=asst_listbox.yview)
    asst_scroll.pack(side='right', fill='y')
    asst_listbox.config(yscrollcommand=asst_scroll.set)
    for asst in current_assistants:
        asst_listbox.insert(tk.END, asst)

    asst_btn_frame = tk.Frame(settings_win)
    asst_btn_frame.pack(fill='x', padx=10, pady=5)

    def add_assistant():
        new_asst = simpledialog.askstring("Добавить помощника",
                                          "Введите имя (начинается с @):",
                                          parent=settings_win)
        if new_asst:
            if not new_asst.startswith('@'):
                new_asst = '@' + new_asst
            if new_asst in asst_listbox.get(0, tk.END):
                messagebox.showwarning("Предупреждение", "Такой помощник уже есть!")
                return
            asst_listbox.insert(tk.END, new_asst)

    def remove_assistant():
        selected = asst_listbox.curselection()
        if selected:
            asst_listbox.delete(selected[0])

    tk.Button(asst_btn_frame, text="Добавить", command=add_assistant, width=10).pack(
        side='left', padx=5)
    tk.Button(asst_btn_frame, text="Удалить", command=remove_assistant, width=10).pack(
        side='left', padx=5)

    # Сохранение
    def save_settings():
        new_username = username_entry.get().strip()
        if not new_username:
            messagebox.showerror("Ошибка", "Имя не может быть пустым!")
            return
        if not new_username.startswith('@'):
            new_username = '@' + new_username

        new_observers = list(obs_listbox.get(0, tk.END))
        new_assistants = list(asst_listbox.get(0, tk.END))

        if len(new_observers) != len(set(new_observers)) or \
           len(new_assistants) != len(set(new_assistants)):
            messagebox.showerror("Ошибка", "Не должно быть повторяющихся имён!")
            return

        save_config(new_username, new_observers, new_assistants)
        state.username_var.set(new_username)
        state.observer_combobox['values'] = new_observers + ["Нет"]
        state.observer_combobox.set("Нет")
        refresh_assistant_checkboxes(new_assistants)
        settings_win.destroy()
        messagebox.showinfo("Успех", "Настройки сохранены!")

    tk.Button(settings_win, text="Сохранить", command=save_settings,
              bg="lightgreen", width=15).pack(pady=15)


def refresh_assistant_checkboxes(assistants_list):
    for widget in state.assistant_check_frame.winfo_children():
        widget.destroy()
    state.assistant_vars.clear()

    for assistant in assistants_list:
        var = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(state.assistant_check_frame, text=assistant,
                            variable=var, anchor='w')
        cb.pack(fill='x', padx=5, pady=2)
        state.assistant_vars[assistant] = var