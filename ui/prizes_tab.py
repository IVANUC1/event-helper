
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

from ui.app_state import state
from utils.helpers import get_base_path


def create_prizes_tab(parent):
    total_items = 59
    rows_layout = [13, 14, 5, 2, 3, 15, 3, 4]
    item_status = [
        0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1,
        2, 2, 2, 2, 2,
        0, 1,
        0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 2, 2,
        0, 0, 0,
        0, 0, 0, 0
    ]
    item_id_map = {
        1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 8, 10: 9,
        11: 10, 12: 11, 13: 61, 14: 13, 15: 21, 16: 23, 17: 24, 18: 39,
        19: 40, 20: 41, 21: 52, 22: 53, 23: 20, 24: 47, 25: 48, 26: 50,
        27: 30, 28: 19, 29: 27, 30: 28, 31: 29, 32: 22, 33: 26, 34: 25,
        35: 36, 36: 37, 37: 38, 38: 17, 39: 18, 40: 51, 41: 46, 42: 31,
        43: 43, 44: 44, 45: 45, 46: 16, 47: 42, 48: 32, 49: 49, 50: 55,
        51: 62, 52: 68, 53: 14, 54: 33, 55: 34, 56: 44, 57: 15, 58: 12,
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
    scrollable_frame.bind("<Configure>",
                          lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
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

        img = Image.new('RGB', size, color='lightgray')
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 10)
        except Exception:
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
                relief=tk.RAISED, bd=2
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

    # SCP кнопки
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
            width=12, height=2,
            relief=tk.RAISED, bd=2
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

    # Ввод ID
    input_frame = tk.Frame(scrollable_frame)
    input_frame.pack(anchor='w', pady=10)
    tk.Label(input_frame, text="ID игрока:").pack(side=tk.LEFT, padx=5)
    player_entry = tk.Entry(input_frame, textvariable=player_id_var, width=10)
    player_entry.pack(side=tk.LEFT, padx=5)

    # Команды
    commands_frame = tk.Frame(scrollable_frame)
    commands_frame.pack(anchor='w', pady=10, fill=tk.X)

    main_cmd_frame = tk.Frame(commands_frame)
    main_cmd_frame.pack(fill=tk.X, pady=2)
    tk.Label(main_cmd_frame, text="Команда выдачи:", font=('Arial', 10)).pack(
        side=tk.LEFT, padx=5)
    command_text = tk.Text(main_cmd_frame, height=3, width=50, font=('Courier', 10), wrap=tk.WORD)
    command_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    copy_btn_main = tk.Button(main_cmd_frame, text="Копировать",
                              command=lambda: copy_text(command_text), bg="#cfe2f3")
    copy_btn_main.pack(side=tk.RIGHT, padx=5)

    hp_cmd_frame = tk.Frame(commands_frame)
    hp_cmd_frame.pack(fill=tk.X, pady=2)
    tk.Label(hp_cmd_frame, text="Команда HP (SCP):", font=('Arial', 10)).pack(
        side=tk.LEFT, padx=5)
    command_text_hp = tk.Text(hp_cmd_frame, height=3, width=50, font=('Courier', 10),
                              wrap=tk.WORD, state=tk.NORMAL)
    command_text_hp.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    copy_btn_hp = tk.Button(hp_cmd_frame, text="Копировать",
                            command=lambda: copy_text(command_text_hp), bg="#cfe2f3")
    copy_btn_hp.pack(side=tk.RIGHT, padx=5)

    def copy_text(text_widget):
        cmd = text_widget.get(1.0, tk.END).strip()
        if cmd and cmd != "—" and cmd != "Выберите SCP для HP команды":
            state.root.clipboard_clear()
            state.root.clipboard_append(cmd)
            state.root.update()
            messagebox.showinfo("Успех", "Команда скопирована в буфер обмена!")
        else:
            messagebox.showwarning("Внимание", "Нет команды для копирования.")

    # Легенда
    legend_frame = tk.Frame(parent)
    legend_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
    tk.Label(legend_frame, text="Легенда:", font=('Arial', 10, 'bold')).pack(
        side=tk.LEFT, padx=10)
    tk.Label(legend_frame, text="🟢 можно сразу", bg='#a8e6cf', padx=5).pack(
        side=tk.LEFT, padx=2)
    tk.Label(legend_frame, text="🟡 через минуту", bg='#ffd3b4', padx=5).pack(
        side=tk.LEFT, padx=2)
    tk.Label(legend_frame, text="🔴 нельзя (ошибка при выборе)", bg='#ff8a8a', padx=5).pack(
        side=tk.LEFT, padx=2)
    tk.Label(legend_frame, text=" | SCP (серый)", bg='#D3D3D3', padx=5).pack(
        side=tk.LEFT, padx=5)

    # Обновление команд
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
            sl_id = item_id_map.get(item_idx, item_idx)
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