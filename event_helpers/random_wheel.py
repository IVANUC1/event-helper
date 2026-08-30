import math
import random
import tkinter as tk
from tkinter import messagebox


def create_wheel(parent):
    """Создает и размещает колесо фортуны в указанном родительском виджете."""

    # --- СОСТОЯНИЕ КОЛЕСА ---
    state = {
        'current_angle': 0,
        'is_spinning': False,
        'winner_index': 0,
        'current_step': 0,
        'total_steps': 50,
        'total_rotation': 0,
        'start_rotation_angle': 0,
        'chance_a': 50,
        'chance_b': 50,
    }

    SIZE = 400
    CENTER = SIZE / 2
    RADIUS = 160

    # --- ФУНКЦИИ РИСОВАНИЯ ---
    def draw_text_in_sector(start_angle, extent, text):
        """Рисует текст ровно по центру сектора"""
        rad = math.radians(start_angle + extent / 2)
        tx = CENTER + (RADIUS * 0.5) * math.cos(rad)
        ty = CENTER - (RADIUS * 0.5) * math.sin(rad)
        canvas.create_text(tx, ty, text=text, font=("Arial", 11, "bold"), tags="wheel")

    def draw_wheel(start_angle):
        """Очищает и заново рисует колесо с новым углом поворота"""
        canvas.delete("wheel")

        extent_a = (state['chance_a'] / 100) * 360
        extent_b = (state['chance_b'] / 100) * 360

        canvas.create_arc(
            CENTER - RADIUS, CENTER - RADIUS, CENTER + RADIUS, CENTER + RADIUS,
            start=start_angle, extent=extent_a,
            fill="#99ff99", outline="black", width=2, tags="wheel"
        )
        if extent_a > 15:  # рисуем текст только если сектор достаточно большой
            draw_text_in_sector(start_angle, extent_a, f"Победа ({state['chance_a']}%)")

        start_angle_b = start_angle + extent_a
        canvas.create_arc(
            CENTER - RADIUS, CENTER - RADIUS, CENTER + RADIUS, CENTER + RADIUS,
            start=start_angle_b, extent=extent_b,
            fill="#ff9999", outline="black", width=2, tags="wheel"
        )
        if extent_b > 15:
            draw_text_in_sector(start_angle_b, extent_b, f"Проигрыш ({state['chance_b']}%)")

    def draw_pointer():
        """Рисует неподвижную стрелку-указатель сверху"""
        canvas.delete("pointer")
        canvas.create_polygon(
            CENTER - 12, 20,
            CENTER + 12, 20,
            CENTER, 45,
            fill="red", outline="black", tags="pointer"
        )

    # --- ЛОГИКА АНИМАЦИИ ---
    def animate_spin():
        """Функция покадровой анимации вращения"""
        if state['current_step'] < state['total_steps']:
            state['current_step'] += 1
            t = state['current_step'] / state['total_steps']
            factor = 1 - (1 - t) ** 3
            state['current_angle'] = state['start_rotation_angle'] + (state['total_rotation'] * factor)
            draw_wheel(state['current_angle'])
            draw_pointer()
            parent.after(25, animate_spin)
        else:
            state['is_spinning'] = False
            btn.config(state=tk.NORMAL)
            result_text = (
                f"Победа! ({state['chance_a']}%)"
                if state['winner_index'] == 0
                else f"Проигрыш ({state['chance_b']}%)"
            )
            result_label.config(text=f"Результат: {result_text}")
            # messagebox.showinfo("Результат", f"Выпал сектор:\n{result_text}")

    def spin():
        """Инициализация запуска кручения"""
        if state['is_spinning']:
            return
        state['is_spinning'] = True
        btn.config(state=tk.DISABLED)

        extent_a = (state['chance_a'] / 100) * 360
        extent_b = (state['chance_b'] / 100) * 360

        state['winner_index'] = random.choices(
            [0, 1], weights=[state['chance_a'], state['chance_b']], k=1
        )[0]

        if state['winner_index'] == 0:
            target_inside_sector = random.uniform(
                min(10, extent_a / 2),
                max(10, extent_a - 10)
            )
            target_angle = 90 - target_inside_sector
        else:
            target_inside_sector = random.uniform(
                min(10, extent_b / 2),
                max(10, extent_b - 10)
            )
            target_angle = 90 - (extent_a + target_inside_sector)

        target_angle = target_angle % 360
        state['total_rotation'] = target_angle - (state['current_angle'] % 360) + (360 * random.randint(3, 5))
        state['current_step'] = 0
        state['start_rotation_angle'] = state['current_angle']
        animate_spin()

    # --- ОБНОВЛЕНИЕ ШАНСОВ ---
    def update_chance(value):
        """Вызывается при изменении значения слайдера"""
        chance_a = int(float(value))
        chance_b = 100 - chance_a
        state['chance_a'] = chance_a
        state['chance_b'] = chance_b

        # Обновляем подпись с текущими шансами
        chance_label.config(
            text=f"Шанс победы: {chance_a}%  |  Шанс проигрыша: {chance_b}%"
        )

        # Перерисовываем колесо, если оно не крутится
        if not state['is_spinning']:
            draw_wheel(state['current_angle'])
            draw_pointer()

    # --- СОЗДАНИЕ ИНТЕРФЕЙСА ---
    canvas = tk.Canvas(parent, width=SIZE, height=SIZE, bg="white")
    canvas.pack(pady=10)

    btn = tk.Button(parent, text="Крутить!", font=("Arial", 14),
                    command=spin, bg="#d9ead3", width=25)
    btn.pack(pady=10)

    # --- БЛОК НАСТРОЙКИ ШАНСА ---
    chance_frame = tk.Frame(parent)
    chance_frame.pack(pady=10, padx=20, fill=tk.X)

    tk.Label(chance_frame, text="Настройка шанса победы:",
             font=('Arial', 10, 'bold')).pack()

    chance_scale = tk.Scale(
        chance_frame,
        from_=1, to=99,
        orient=tk.HORIZONTAL,
        length=350,
        command=update_chance
    )
    chance_scale.set(state['chance_a'])
    chance_scale.pack(pady=5)

    chance_label = tk.Label(
        chance_frame,
        text=f"Шанс победы: {state['chance_a']}%  |  Шанс проигрыша: {state['chance_b']}%",
        font=('Arial', 11),
        fg="#333333"
    )
    chance_label.pack()

    result_label = tk.Label(
        parent,
        text="Результат: —",
        font=('Arial', 12, 'bold'),
        fg="#333333"
    )
    result_label.pack(pady=10)

    # --- НАЧАЛЬНЫЙ РЕНДЕРИНГ ---
    draw_wheel(state['current_angle'])
    draw_pointer()

    return canvas, btn