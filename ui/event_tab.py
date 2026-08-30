import tkinter as tk
from tkinter import messagebox

from ui.app_state import state
from utils.helpers import time_detector, text_generator
from utils.event_loader import render_description, get_description
from event_helpers.random_items import get_random_item_by_phase
from event_helpers.random_effects import get_random_effect
from event_helpers.random_wheel import create_wheel


def generate_event():
    selected = None
    if state.listbox_left.curselection():
        selected = state.listbox_left.get(state.listbox_left.curselection()[0])
    elif state.listbox_right.curselection():
        selected = state.listbox_right.get(state.listbox_right.curselection()[0])
    else:
        messagebox.showwarning("Внимание", "Сначала выберите ивент из списка!")
        return

    watcher = state.observer_combobox.get()
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

    state.text_output.delete(1.0, tk.END)
    state.text_output.insert(tk.END, generated)
    state.finish_button.current_event = current_event_data


def finish_event():
    if not hasattr(state.finish_button, 'current_event') or not state.finish_button.current_event:
        messagebox.showwarning("Внимание", "Нет активного ивента. Сначала сгенерируйте текст!")
        return

    end_time = time_detector()
    event_data = state.finish_button.current_event
    lines = event_data["original_text"].split('\n')

    for i, line in enumerate(lines):
        if line.startswith("3."):
            lines[i] = f"3. {end_time}"
            break

    updated_text = '\n'.join(lines)
    state.text_output.delete(1.0, tk.END)
    state.text_output.insert(tk.END, updated_text)

    event_data["original_text"] = updated_text
    state.finish_button.current_event = event_data


def copy_to_clipboard():
    text = state.text_output.get(1.0, tk.END).strip()
    if text:
        state.root.clipboard_clear()
        state.root.clipboard_append(text)
        state.root.update()
        messagebox.showinfo("Готово", "Текст скопирован в буфер обмена!")
    else:
        messagebox.showwarning("Внимание", "Нечего копировать. Сначала сгенерируйте ивент.")


def on_event_select(event):
    selected = None
    if state.listbox_left.curselection():
        selected = state.listbox_left.get(state.listbox_left.curselection()[0])
    elif state.listbox_right.curselection():
        selected = state.listbox_right.get(state.listbox_right.curselection()[0])
    else:
        return

    # Сравниваем БЕЗ пробелов — теперь спец-функции найдутся в любом случае
    selected_clean = selected.strip()

    # Очищаем спецфрейм
    for widget in state.special_frame.winfo_children():
        widget.destroy()

    if selected_clean == "Случайные эффекты":
        tk.Label(state.special_frame, text="Генератор случайного эффекта:",
                 font=('Arial', 10, 'bold')).pack(pady=5)
        effect_display = tk.Label(state.special_frame, text="", font=('Arial', 12), fg="blue")
        effect_display.pack(pady=5)

        def generate_random_effect():
            effect = get_random_effect()
            effect_display.config(text=f"Эффект: {effect}")

        btn = tk.Button(state.special_frame, text="Получить случайный эффект",
                        command=generate_random_effect, bg="#d9ead3", width=25)
        btn.pack(pady=10)

    elif selected_clean == "Случайные предметы":
        tk.Label(state.special_frame,
                 text="Генератор случайного предмета в зависимости от этапа игры:",
                 font=('Arial', 10, 'bold')).pack(pady=5)

        phase_var = tk.StringVar(value="лейтгейм (до 8 мин)")
        phase_frame = tk.Frame(state.special_frame)
        phase_frame.pack(pady=5)

        phases = [
            ("лейтгейм (до 8 мин)", "лейтгейм (до 8 мин)"),
            ("Мидгейм (8-18 мин)", "мидгейм (8-18 мин)"),
            ("эндгейм (после 18 мин)", "эндгейм (после 18 мин)")
        ]
        for text, value in phases:
            tk.Radiobutton(phase_frame, text=text, variable=phase_var,
                           value=value).pack(side=tk.LEFT, padx=10)

        item_display = tk.Label(state.special_frame, text="", font=('Arial', 12), fg="green")
        item_display.pack(pady=10)

        def generate_random_item():
            phase = phase_var.get()
            item = get_random_item_by_phase(phase)
            item_display.config(text=f"Предмет: {item}")

        btn = tk.Button(state.special_frame, text="Получить случайный предмет",
                        command=generate_random_item, bg="#d9ead3", width=25)
        btn.pack(pady=10)
    elif selected_clean == "Апгрейдер":
        tk.Label(state.special_frame, text="Колесо фортуны", font=('Arial', 10, 'bold')).pack(pady=5)
        create_wheel(state.special_frame)
    else:
        tk.Label(state.special_frame,
                 text=f"Специальный функционал для ивента '{selected}' пока не реализован.",
                 font=('Arial', 10)).pack(pady=20)

    desc = get_description(state.descriptions_dict, selected)
    render_description(state.description_text_widget, desc)