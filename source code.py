import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from event_helpers.random_items import get_random_item_by_phase
from event_helpers.random_effects import get_random_effect
from PIL import Image, ImageTk
import json
import time
import os
import sys
import requests

# ------------------- Вспомогательные функции -------------------
def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def time_detector():
    now = int(time.time())
    return f'<t:{now}:f>'

def text_generator(start_time, event_type, watcher='', end_time=''):
    full_username = username_var.get()
    selected_assistants = [name for name, var in assistant_vars.items() if var.get()]
    if selected_assistants:
        full_username += " " + " ".join(selected_assistants)
    text = f'1. {event_type}\n2. {start_time}\n3. {end_time}\n4. {full_username}'
    if watcher:
        text += f'\n5. {watcher}'
    return text

# ------------------- Загрузка / сохранение конфигов -------------------
CONFIG_FILE = os.path.join(get_base_path(), "config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_config(username, observers, assistants):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"username": username, "observers": observers, "assistants": assistants}, f, indent=2, ensure_ascii=False)

# ------------------- Загрузка событий и описаний -------------------
def load_events():
    list_path = os.path.join(get_base_path(), "list.json")
    try:
        with open(list_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        events_left = data["дополнения обычного раунда"]
        events_right = data["вне обычного раунда"]
        descriptions = data.get("descriptions", {})
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

# ------------------- Форматирование описания -------------------
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

# ------------------- Окно настроек -------------------
def open_settings():
    settings_win = tk.Toplevel(root)
    settings_win.title("Настройки")
    settings_win.geometry("500x500")
    settings_win.transient(root)
    settings_win.grab_set()

    current_username = username_var.get()
    config_data = load_config()
    current_observers = config_data["observers"] if config_data else []
    current_assistants = config_data["assistants"] if config_data else []

    tk.Label(settings_win, text="Ваше имя:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=(10,0))
    username_frame = tk.Frame(settings_win)
    username_frame.pack(fill='x', padx=10, pady=5)
    username_entry = tk.Entry(username_frame, width=30)
    username_entry.insert(0, current_username)
    username_entry.pack(side='left')
    tk.Label(username_frame, text=" (например @ivanuc1)", font=('Arial', 9)).pack(side='left', padx=5)

    tk.Label(settings_win, text="Наблюдатели:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=(10,0))
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
        new_obs = simpledialog.askstring("Добавить наблюдателя", "Введите имя (начинается с @):", parent=settings_win)
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

    tk.Button(obs_btn_frame, text="Добавить", command=add_observer, width=10).pack(side='left', padx=5)
    tk.Button(obs_btn_frame, text="Удалить", command=remove_observer, width=10).pack(side='left', padx=5)

    tk.Label(settings_win, text="Помощники (co-hosts):", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=(10,0))
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
        new_asst = simpledialog.askstring("Добавить помощника", "Введите имя (начинается с @):", parent=settings_win)
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

    tk.Button(asst_btn_frame, text="Добавить", command=add_assistant, width=10).pack(side='left', padx=5)
    tk.Button(asst_btn_frame, text="Удалить", command=remove_assistant, width=10).pack(side='left', padx=5)

    def save_settings():
        new_username = username_entry.get().strip()
        if not new_username:
            messagebox.showerror("Ошибка", "Имя не может быть пустым!")
            return
        if not new_username.startswith('@'):
            new_username = '@' + new_username
        new_observers = list(obs_listbox.get(0, tk.END))
        new_assistants = list(asst_listbox.get(0, tk.END))
        if len(new_observers) != len(set(new_observers)) or len(new_assistants) != len(set(new_assistants)):
            messagebox.showerror("Ошибка", "Не должно быть повторяющихся имён!")
            return
        save_config(new_username, new_observers, new_assistants)
        username_var.set(new_username)
        observer_combobox['values'] = new_observers + ["Нет"]
        observer_combobox.set("Нет")
        refresh_assistant_checkboxes(new_assistants)
        settings_win.destroy()
        messagebox.showinfo("Успех", "Настройки сохранены!")

    tk.Button(settings_win, text="Сохранить", command=save_settings, bg="lightgreen", width=15).pack(pady=15)

def refresh_assistant_checkboxes(assistants_list):
    for widget in assistant_check_frame.winfo_children():
        widget.destroy()
    assistant_vars.clear()
    for assistant in assistants_list:
        var = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(assistant_check_frame, text=assistant, variable=var, anchor='w')
        cb.pack(fill='x', padx=5, pady=2)
        assistant_vars[assistant] = var

# ------------------- Основные функции генерации -------------------
def generate_event():
    selected = None
    if listbox_left.curselection():
        selected = listbox_left.get(listbox_left.curselection()[0])
    elif listbox_right.curselection():
        selected = listbox_right.get(listbox_right.curselection()[0])
    else:
        messagebox.showwarning("Внимание", "Сначала выберите ивент из списка!")
        return

    watcher = observer_combobox.get()
    if watcher == "Нет":
        watcher = ""
    start_time = time_detector()
    generated = text_generator(start_time, selected, watcher, end_time="")
    current_event_data = {
        "original_text": generated,
        "start_time": start_time,
        "event_type": selected,
        "watcher": watcher
    }
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, generated)
    finish_button.current_event = current_event_data

def finish_event():
    if not hasattr(finish_button, 'current_event') or not finish_button.current_event:
        messagebox.showwarning("Внимание", "Нет активного ивента. Сначала сгенерируйте текст!")
        return
    end_time = time_detector()
    event_data = finish_button.current_event
    lines = event_data["original_text"].split('\n')
    for i, line in enumerate(lines):
        if line.startswith("3."):
            lines[i] = f"3. {end_time}"
            break
    updated_text = '\n'.join(lines)
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, updated_text)
    event_data["original_text"] = updated_text
    finish_button.current_event = event_data

def copy_to_clipboard():
    text = text_output.get(1.0, tk.END).strip()
    if text:
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        messagebox.showinfo("Готово", "Текст скопирован в буфер обмена!")
    else:
        messagebox.showwarning("Внимание", "Нечего копировать. Сначала сгенерируйте ивент.")

# ------------------- Обработчик выбора ивента -------------------
def on_event_select(event):
    selected = None
    if listbox_left.curselection():
        selected = listbox_left.get(listbox_left.curselection()[0])
    elif listbox_right.curselection():
        selected = listbox_right.get(listbox_right.curselection()[0])
    else:
        return

    for widget in special_frame.winfo_children():
        widget.destroy()

    if selected == "Случайные эффекты":
        tk.Label(special_frame, text="Генератор случайного эффекта:", font=('Arial', 10, 'bold')).pack(pady=5)
        effect_display = tk.Label(special_frame, text="", font=('Arial', 12), fg="blue")
        effect_display.pack(pady=5)

        def generate_random_effect():
            effect = get_random_effect()
            effect_display.config(text=f"Эффект: {effect}")

        btn = tk.Button(special_frame, text="Получить случайный эффект", command=generate_random_effect, bg="#d9ead3", width=25)
        btn.pack(pady=10)

    elif selected == "Случайные предметы":
        tk.Label(special_frame, text="Генератор случайного предмета в зависимости от этапа игры:",
                 font=('Arial', 10, 'bold')).pack(pady=5)

        phase_var = tk.StringVar(value="лейтгейм (до 8 мин)")
        phase_frame = tk.Frame(special_frame)
        phase_frame.pack(pady=5)

        phases = [
            ("лейтгейм (до 8 мин)", "лейтгейм (до 8 мин)"),
            ("Мидгейм (8-18 мин)", "мидгейм (8-18 мин)"),
            ("эндгейм (после 18 мин)", "эндгейм (после 18 мин)")
        ]

        for text, value in phases:
            tk.Radiobutton(phase_frame, text=text, variable=phase_var, value=value).pack(side=tk.LEFT, padx=10)

        item_display = tk.Label(special_frame, text="", font=('Arial', 12), fg="green")
        item_display.pack(pady=10)

        def generate_random_item():
            phase = phase_var.get()
            item = get_random_item_by_phase(phase)
            item_display.config(text=f"Предмет: {item}")

        btn = tk.Button(special_frame, text="Получить случайный предмет", command=generate_random_item, bg="#d9ead3",
                        width=25)
        btn.pack(pady=10)
    else:
        tk.Label(special_frame, text=f"Специальный функционал для ивента '{selected}' пока не реализован.", font=('Arial', 10)).pack(pady=20)

    desc = descriptions_dict.get(selected, "")
    render_description(description_text_widget, desc)

# ------------------- Вкладка "Управление призами" -------------------
def create_prizes_tab(parent):
    total_items = 59
    rows_layout = [13, 14, 5, 2, 3, 15, 3, 4]

    item_status = [
        0,0,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,2,2,2,2,2,2,2,2,2,2,1,
        2,2,2,2,2,
        0,1,
        0,0,0,
        0,0,0,0,0,0,0,0,2,0,0,0,0,2,2,
        0,0,0,
        0,0,0,0
    ]

    item_id_map = {
        1: 0,
        2: 1,
        3: 2,
        4: 3,
        5: 4,
        6: 5,
        7: 6,
        8: 7,
        9: 8,
        10: 9,
        11: 10,
        12: 11,
        13: 61,
        14: 13,
        15: 21,
        16: 23,
        17: 24,
        18: 39,
        19: 40,
        20: 41,
        21: 52,
        22: 53,
        23: 20,
        24: 47,
        25: 48,
        26: 50,
        27: 30,
        28: 19,
        29: 27,
        30: 28,
        31: 29,
        32: 22,
        33: 26,
        34: 25,
        35: 36,
        36: 37,
        37: 38,
        38: 17,
        39: 18,
        40: 51,
        41: 46,
        42: 31,
        43: 43,
        44: 44,
        45: 45,
        46: 16,
        47: 42,
        48: 32,
        49: 49,
        50: 55,
        51: 62,
        52: 68,
        53: 14,
        54: 33,
        55: 34,
        56: 44,
        57: 15,
        58: 12,
        59: 35,
    }

    scp_list = [
        {'name': 'SCP-939', 'hp': 2500, 'scp_id': 'Scp939'},
        {'name': 'SCP-173', 'hp': 4500, 'scp_id': 'Scp173'},
        {'name': 'SCP-106', 'hp': 2300, 'scp_id': 'Scp106'},
        {'name': 'SCP-049', 'hp': 2500, 'scp_id': 'Scp049'},
        {'name': 'SCP-096', 'hp': 3000, 'scp_id': 'Scp096'},
        {'name': 'SCP-079', 'hp': 0, 'scp_id': 'Scp079'},
    ]

    images_dir = os.path.join(get_base_path(), "itemimages")
    if not os.path.exists(images_dir):
        os.makedirs(images_dir, exist_ok=True)

    selected_item = tk.IntVar(value=-1)
    selected_scp = tk.IntVar(value=-1)
    player_id_var = tk.StringVar()

    container = tk.Frame(parent)
    container.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(container)
    scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_item_image(item_index, size=(30, 30)):
        base_name = f"item{item_index}"
        found_path = None
        if os.path.exists(images_dir):
            for fname in os.listdir(images_dir):
                name_no_ext, ext = os.path.splitext(fname)
                if name_no_ext.lower() == base_name.lower():
                    found_path = os.path.join(images_dir, fname)
                    break
        if found_path:
            try:
                img = Image.open(found_path)
                try:
                    img_resized = img.resize(size, Image.Resampling.LANCZOS)
                except AttributeError:
                    img_resized = img.resize(size, Image.ANTIALIAS)
                return ImageTk.PhotoImage(img_resized)
            except Exception as e:
                print(f"Ошибка загрузки {found_path}: {e}")
        # Заглушка
        img = Image.new('RGB', size, color='lightgray')
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 10)
        except:
            font = ImageFont.load_default()
        draw.text((5, 10), str(item_index), fill='black', font=font)
        return ImageTk.PhotoImage(img)

    item_buttons = {}
    photo_refs = {}

    item_index = 1
    for row_idx, count in enumerate(rows_layout):
        row_frame = tk.Frame(scrollable_frame)
        row_frame.pack(anchor='w', pady=5)

        for _ in range(count):
            if item_index > total_items:
                break

            img = load_item_image(item_index)
            if img:
                photo_refs[item_index] = img
            else:
                print(f"Не удалось загрузить изображение для item{item_index}")

            color_map = {0: '#a8e6cf', 1: '#ffd3b4', 2: '#ff8a8a'}
            current_status = item_status[item_index - 1]
            bg_color = color_map[current_status]

            btn = tk.Button(
                row_frame,
                image=img if img else '',
                text=str(item_index) if not img else '',
                font=('Arial', 6),
                bg=bg_color,
                width=30, height=30,
                relief=tk.RAISED,
                bd=2
            )
            if img:
                btn.image = img
            btn.pack(side=tk.LEFT, padx=2, pady=2)

            item_buttons[item_index] = btn

            def make_item_callback(idx, button):
                def callback():
                    if item_status[idx - 1] == 2:
                        messagebox.showerror("Ошибка", f"Предмет {idx} нельзя выдавать (красный статус)!")
                        return
                    if selected_item.get() != -1:
                        prev_btn = item_buttons[selected_item.get()]
                        prev_btn.config(relief=tk.RAISED, bd=2)
                    button.config(relief=tk.SUNKEN, bd=4)
                    selected_item.set(idx)
                    if selected_scp.get() != -1:
                        scp_buttons[selected_scp.get()].config(relief=tk.RAISED, bd=2)
                        selected_scp.set(-1)
                    update_commands()
                return callback

            btn.config(command=make_item_callback(item_index, btn))

            def make_status_switch(idx, button):
                def switch(event):
                    current = item_status[idx - 1]
                    new_status = (current + 1) % 3
                    item_status[idx - 1] = new_status
                    color_map = {0: '#a8e6cf', 1: '#ffd3b4', 2: '#ff8a8a'}
                    button.config(bg=color_map[new_status])
                    if selected_item.get() == idx:
                        selected_item.set(-1)
                        button.config(relief=tk.RAISED, bd=2)
                        update_commands()
                return switch

            btn.bind("<Button-3>", make_status_switch(item_index, btn))

            item_index += 1

    scp_label = tk.Label(scrollable_frame, text="--- Выбор SCP ---", font=('Arial', 10, 'bold'))
    scp_label.pack(anchor='w', pady=(10, 5))

    scp_frame = tk.Frame(scrollable_frame)
    scp_frame.pack(anchor='w', pady=5)

    scp_buttons = {}
    for i, scp in enumerate(scp_list):
        btn = tk.Button(
            scp_frame,
            text=f"{scp['name']}\nHP: {scp['hp']}",
            font=('Arial', 8),
            bg='#D3D3D3',
            width=12,
            height=2,
            relief=tk.RAISED,
            bd=2
        )
        btn.pack(side=tk.LEFT, padx=5, pady=2)

        def make_scp_callback(idx, button):
            def callback():
                if selected_scp.get() != -1:
                    prev_btn = scp_buttons[selected_scp.get()]
                    prev_btn.config(relief=tk.RAISED, bd=2)
                button.config(relief=tk.SUNKEN, bd=4)
                selected_scp.set(idx)
                if selected_item.get() != -1:
                    prev_item_btn = item_buttons[selected_item.get()]
                    prev_item_btn.config(relief=tk.RAISED, bd=2)
                    selected_item.set(-1)
                update_commands()
            return callback

        btn.config(command=make_scp_callback(i, btn))
        scp_buttons[i] = btn

    input_frame = tk.Frame(scrollable_frame)
    input_frame.pack(anchor='w', pady=10)

    tk.Label(input_frame, text="ID игрока:").pack(side=tk.LEFT, padx=5)
    player_entry = tk.Entry(input_frame, textvariable=player_id_var, width=10)
    player_entry.pack(side=tk.LEFT, padx=5)

    commands_frame = tk.Frame(scrollable_frame)
    commands_frame.pack(anchor='w', pady=10, fill=tk.X)

    main_cmd_frame = tk.Frame(commands_frame)
    main_cmd_frame.pack(fill=tk.X, pady=2)
    tk.Label(main_cmd_frame, text="Команда выдачи:", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
    command_text = tk.Text(main_cmd_frame, height=3, width=50, font=('Courier', 10), wrap=tk.WORD)
    command_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    copy_btn_main = tk.Button(main_cmd_frame, text="Копировать", command=lambda: copy_text(command_text), bg="#cfe2f3")
    copy_btn_main.pack(side=tk.RIGHT, padx=5)

    hp_cmd_frame = tk.Frame(commands_frame)
    hp_cmd_frame.pack(fill=tk.X, pady=2)
    tk.Label(hp_cmd_frame, text="Команда HP (SCP):", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
    command_text_hp = tk.Text(hp_cmd_frame, height=3, width=50, font=('Courier', 10), wrap=tk.WORD, state=tk.NORMAL)
    command_text_hp.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    copy_btn_hp = tk.Button(hp_cmd_frame, text="Копировать", command=lambda: copy_text(command_text_hp), bg="#cfe2f3")
    copy_btn_hp.pack(side=tk.RIGHT, padx=5)

    def copy_text(text_widget):
        cmd = text_widget.get(1.0, tk.END).strip()
        if cmd and cmd != "—" and cmd != "Выберите SCP для HP команды":
            root.clipboard_clear()
            root.clipboard_append(cmd)
            root.update()
            messagebox.showinfo("Успех", "Команда скопирована в буфер обмена!")
        else:
            messagebox.showwarning("Внимание", "Нет команды для копирования.")

    # ---------- ЛЕГЕНДА ----------
    legend_frame = tk.Frame(parent)
    legend_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

    tk.Label(legend_frame, text="Легенда:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)
    tk.Label(legend_frame, text="🟢 можно сразу", bg='#a8e6cf', padx=5).pack(side=tk.LEFT, padx=2)
    tk.Label(legend_frame, text="🟡 через минуту", bg='#ffd3b4', padx=5).pack(side=tk.LEFT, padx=2)
    tk.Label(legend_frame, text="🔴 нельзя (ошибка при выборе)", bg='#ff8a8a', padx=5).pack(side=tk.LEFT, padx=2)
    tk.Label(legend_frame, text=" | SCP (серый)", bg='#D3D3D3', padx=5).pack(side=tk.LEFT, padx=5)

    # ---------- ФУНКЦИЯ ОБНОВЛЕНИЯ КОМАНД ----------
    def update_commands():
        player_id = player_id_var.get().strip()
        if not player_id.isdigit():
            command_text.delete(1.0, tk.END)
            command_text.insert(tk.END, "Введите корректный ID игрока (число)")
            command_text_hp.delete(1.0, tk.END)
            command_text_hp.insert(tk.END, "—")
            return

        if selected_item.get() != -1:
            item_idx = selected_item.get()
            if item_status[item_idx - 1] == 2:
                command_text.delete(1.0, tk.END)
                command_text.insert(tk.END, "Ошибка: красный статус (нельзя выдавать)!")
                command_text_hp.delete(1.0, tk.END)
                command_text_hp.insert(tk.END, "—")
                return
            sl_id = item_id_map.get(item_idx, item_idx)  # если нет в словаре, используем номер
            cmd = f"give {player_id} {sl_id}"
            command_text.delete(1.0, tk.END)
            command_text.insert(tk.END, cmd)
            command_text_hp.delete(1.0, tk.END)
            command_text_hp.insert(tk.END, "—")

        elif selected_scp.get() != -1:
            scp_idx = selected_scp.get()
            scp = scp_list[scp_idx]
            new_hp = int(scp['hp'] * 0.7) if scp['hp'] > 0 else 0
            cmd_force = f"forceclass {player_id} {scp['scp_id']}"
            cmd_hp = f"maxhp {player_id} {new_hp}"
            command_text.delete(1.0, tk.END)
            command_text.insert(tk.END, cmd_force)
            command_text_hp.delete(1.0, tk.END)
            command_text_hp.insert(tk.END, cmd_hp)

        else:
            command_text.delete(1.0, tk.END)
            command_text.insert(tk.END, "Выберите предмет или SCP")
            command_text_hp.delete(1.0, tk.END)
            command_text_hp.insert(tk.END, "—")

    player_id_var.trace_add('write', lambda *args: update_commands())
    update_commands()

    create_prizes_tab.player_id_var = player_id_var
    create_prizes_tab.command_text = command_text
    create_prizes_tab.command_text_hp = command_text_hp

# ------------------- Вкладка "Статистика серверов" -------------------
def fetch_server_stats(server_ids):
    """Запрашивает данные о нескольких серверах через API."""
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

    tk.Label(main_frame, text="Статус серверов", font=('Arial', 14, 'bold')).pack(anchor='w', pady=(0, 10))

    info_frame = tk.Frame(main_frame)
    info_frame.pack(fill=tk.BOTH, expand=True)

    stats_text = tk.Text(info_frame, height=10, width=50, font=('Courier', 11), wrap=tk.WORD)
    stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(info_frame, orient=tk.VERTICAL, command=stats_text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    stats_text.config(yscrollcommand=scrollbar.set)

    last_update_label = tk.Label(main_frame, text="Последнее обновление: никогда", font=('Arial', 9), fg='gray')
    last_update_label.pack(anchor='w', pady=(5, 0))

    btn_frame = tk.Frame(main_frame)
    btn_frame.pack(anchor='w', pady=10)

    refresh_btn = tk.Button(
        btn_frame,
        text="Обновить вручную",
        command=lambda: manual_refresh(stats_text, refresh_btn, last_update_label),
        bg="#cfe2f3",
        width=20
    )
    refresh_btn.pack(side=tk.LEFT, padx=5)

    status_label = tk.Label(btn_frame, text="", font=('Arial', 9))
    status_label.pack(side=tk.LEFT, padx=10)

    # Список ID серверов
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
                stats_text.insert(tk.END, f"Статус: {'🟢 Онлайн' if current > 0 else '🔴 Офлайн'}\n")
                stats_text.insert(tk.END, "-" * 30 + "\n")
            last_update_label.config(text=f"Последнее обновление: {time.strftime('%H:%M:%S')}")
        else:
            stats_text.delete(1.0, tk.END)
            stats_text.insert(tk.END, "⚠️ Не удалось получить данные о серверах.\nПроверьте подключение к интернету.")

    def manual_refresh(text_widget, button, label):
        button.config(state=tk.DISABLED, text="Обновление...")
        status_label.config(text="⏳ Ожидание 5 секунд...", fg='orange')
        root.update()
        root.after(5000, lambda: do_refresh(text_widget, button, label))

    def do_refresh(text_widget, button, label):
        status_label.config(text="🔄 Обновление...", fg='blue')
        root.update()
        update_stats()
        status_label.config(text="✅ Обновлено!", fg='green')
        button.config(state=tk.NORMAL, text="Обновить вручную")
        root.after(2000, lambda: status_label.config(text=""))

    def auto_update():
        update_stats()
        root.after(90000, auto_update)

    update_stats()

    root.after(90000, auto_update)

# ------------------- Построение главного интерфейса -------------------
def build_main_ui():
    global listbox_left, listbox_right, observer_combobox, text_output, finish_button, assistant_vars, assistant_check_frame, special_frame, description_text_widget, descriptions_dict

    events_left, events_right, descriptions_dict = load_events()

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # ------------- Вкладка 1: Генератор ивентов -------------
    main_tab = tk.Frame(notebook)
    notebook.add(main_tab, text="Генератор ивентов")

    top_frame = tk.Frame(main_tab)
    top_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    left_frame = tk.LabelFrame(top_frame, text="Дополнения обычного раунда", padx=5, pady=5)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    listbox_left = tk.Listbox(left_frame, height=20, width=40)
    listbox_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scroll_left = tk.Scrollbar(left_frame, orient=tk.VERTICAL, command=listbox_left.yview)
    scroll_left.pack(side=tk.RIGHT, fill=tk.Y)
    listbox_left.config(yscrollcommand=scroll_left.set)
    for item in events_left:
        listbox_left.insert(tk.END, item)
    listbox_left.bind("<<ListboxSelect>>", on_event_select)

    right_frame = tk.LabelFrame(top_frame, text="Вне обычного раунда", padx=5, pady=5)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    listbox_right = tk.Listbox(right_frame, height=20, width=40)
    listbox_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scroll_right = tk.Scrollbar(right_frame, orient=tk.VERTICAL, command=listbox_right.yview)
    scroll_right.pack(side=tk.RIGHT, fill=tk.Y)
    listbox_right.config(yscrollcommand=scroll_right.set)
    for item in events_right:
        listbox_right.insert(tk.END, item)
    listbox_right.bind("<<ListboxSelect>>", on_event_select)

    control_panel = tk.Frame(main_tab)
    control_panel.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

    left_controls = tk.Frame(control_panel)
    left_controls.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    observer_frame = tk.Frame(left_controls)
    observer_frame.pack(anchor='w', pady=5)
    tk.Label(observer_frame, text="Наблюдатель:").pack(side=tk.LEFT, padx=5)
    config_data = load_config()
    if config_data:
        observers = config_data["observers"]
        username_var.set(config_data["username"])
        assistants = config_data.get("assistants", [])
    else:
        observers = ["@dr.how.to.play", "@d1ff123_52512"]
        username_var.set("@unknown")
        assistants = []
    observer_combobox = ttk.Combobox(observer_frame, values=observers + ["Нет"], state="readonly", width=20)
    observer_combobox.set("Нет")
    observer_combobox.pack(side=tk.LEFT, padx=5)

    assistant_frame = tk.LabelFrame(left_controls, text="Помощники (отметьте галочками)", padx=5, pady=5)
    assistant_frame.pack(fill=tk.BOTH, expand=True, pady=5)
    canvas = tk.Canvas(assistant_frame, highlightthickness=0)
    scrollbar = tk.Scrollbar(assistant_frame, orient=tk.VERTICAL, command=canvas.yview)
    assistant_check_frame = tk.Frame(canvas)
    assistant_check_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0,0), window=assistant_check_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    assistant_vars = {}
    for assistant in assistants:
        var = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(assistant_check_frame, text=assistant, variable=var, anchor='w')
        cb.pack(fill='x', padx=5, pady=2)
        assistant_vars[assistant] = var

    right_controls = tk.Frame(control_panel)
    right_controls.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

    generate_btn = tk.Button(right_controls, text="Создать текст", command=generate_event, bg="#d9ead3", width=20, height=2)
    generate_btn.pack(pady=5)
    finish_button = tk.Button(right_controls, text="Ивент завершён", command=finish_event, bg="#ffe599", width=20, height=2)
    finish_button.pack(pady=5)
    copy_btn = tk.Button(right_controls, text="Скопировать", command=copy_to_clipboard, bg="#cfe2f3", width=20, height=2)
    copy_btn.pack(pady=5)
    settings_btn = tk.Button(right_controls, text="Настройки", command=open_settings, width=20, height=2)
    settings_btn.pack(pady=5)

    text_output = tk.Text(main_tab, height=10, wrap=tk.WORD, font=("Courier", 11))
    text_output.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

    # ------------- Вкладка 2: Специальные функции -------------
    special_tab = tk.Frame(notebook)
    notebook.add(special_tab, text="Специальные функции")
    special_frame = tk.Frame(special_tab)
    special_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # ------------- Вкладка 3: Описание ивента -------------
    desc_tab = tk.Frame(notebook)
    notebook.add(desc_tab, text="Описание ивента")
    desc_frame = tk.Frame(desc_tab)
    desc_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    description_text_widget = tk.Text(desc_frame, wrap=tk.WORD, font=("Arial", 10))
    description_text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    desc_scroll = tk.Scrollbar(desc_frame, orient=tk.VERTICAL, command=description_text_widget.yview)
    desc_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    description_text_widget.config(yscrollcommand=desc_scroll.set)
    description_text_widget.tag_configure("desc_normal", font=("Arial", 10))
    description_text_widget.tag_configure("desc_medium", font=("Arial", 12, "bold"))
    description_text_widget.tag_configure("desc_large", font=("Arial", 16, "bold"))
    description_text_widget.tag_configure("desc_xlarge", font=("Arial", 20, "bold"))

    # ------------- Вкладка 4: Управление призами -------------
    prizes_tab = tk.Frame(notebook)
    notebook.add(prizes_tab, text="Управление призами")
    create_prizes_tab(prizes_tab)

    # ------------- Вкладка 5: Статистика серверов -------------
    create_server_stats_tab(notebook)

# ------------------- Точка входа -------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Генератор ивентов")
    root.geometry("900x1000")
    username_var = tk.StringVar()

    config = load_config()
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
        tk.Label(setup_win, text=f"Наблюдатели по умолчанию:\n{', '.join(default_observers)}", font=('Arial', 9), justify='left').pack(pady=5)
        tk.Label(setup_win, text="Помощники пока пусты — добавишь позже в настройках", font=('Arial', 9), justify='left').pack(pady=5)

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

        tk.Button(setup_win, text="Поехали!", command=save_and_continue, bg="lightgreen", width=20).pack(pady=20)

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