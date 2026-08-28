import tkinter as tk
from tkinter import ttk

from ui.app_state import state
from utils.config_manager import load_config
from utils.event_loader import load_events
from ui.event_tab import on_event_select
from ui.prizes_tab import create_prizes_tab
from ui.server_stats_tab import create_server_stats_tab


def build_main_ui():
    events_left, events_right, descriptions_dict = load_events()
    state.descriptions_dict = descriptions_dict

    root = state.root
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # ─── Вкладка 1: Генератор ивентов ───
    main_tab = tk.Frame(notebook)
    notebook.add(main_tab, text="Генератор ивентов")

    top_frame = tk.Frame(main_tab)
    top_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Левый список
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
    state.listbox_left = listbox_left

    # Правый список
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
    state.listbox_right = listbox_right

    # Панель управления
    control_panel = tk.Frame(main_tab)
    control_panel.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

    left_controls = tk.Frame(control_panel)
    left_controls.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Наблюдатель
    observer_frame = tk.Frame(left_controls)
    observer_frame.pack(anchor='w', pady=5)
    tk.Label(observer_frame, text="Наблюдатель:").pack(side=tk.LEFT, padx=5)

    config_data = load_config()
    if config_data:
        observers = config_data["observers"]
        state.username_var.set(config_data["username"])
        assistants = config_data.get("assistants", [])
    else:
        observers = ["@dr.how.to.play", "@d1ff123_52512"]
        state.username_var.set("@unknown")
        assistants = []

    observer_combobox = ttk.Combobox(observer_frame, values=observers + ["Нет"],
                                     state="readonly", width=20)
    observer_combobox.set("Нет")
    observer_combobox.pack(side=tk.LEFT, padx=5)
    state.observer_combobox = observer_combobox

    # Помощники
    assistant_frame = tk.LabelFrame(left_controls, text="Помощники (отметьте галочками)",
                                    padx=5, pady=5)
    assistant_frame.pack(fill=tk.BOTH, expand=True, pady=5)

    canvas = tk.Canvas(assistant_frame, highlightthickness=0)
    scrollbar = tk.Scrollbar(assistant_frame, orient=tk.VERTICAL, command=canvas.yview)
    assistant_check_frame = tk.Frame(canvas)
    assistant_check_frame.bind("<Configure>",
                               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=assistant_check_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    state.assistant_check_frame = assistant_check_frame

    state.assistant_vars = {}
    for assistant in assistants:
        var = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(assistant_check_frame, text=assistant, variable=var, anchor='w')
        cb.pack(fill='x', padx=5, pady=2)
        state.assistant_vars[assistant] = var

    # Кнопки справа
    right_controls = tk.Frame(control_panel)
    right_controls.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

    from ui.event_tab import generate_event, finish_event, copy_to_clipboard
    from ui.settings_window import open_settings

    generate_btn = tk.Button(right_controls, text="Создать текст", command=generate_event,
                             bg="#d9ead3", width=20, height=2)
    generate_btn.pack(pady=5)

    finish_button = tk.Button(right_controls, text="Ивент завершён", command=finish_event,
                              bg="#ffe599", width=20, height=2)
    finish_button.pack(pady=5)
    state.finish_button = finish_button

    copy_btn = tk.Button(right_controls, text="Скопировать", command=copy_to_clipboard,
                         bg="#cfe2f3", width=20, height=2)
    copy_btn.pack(pady=5)

    settings_btn = tk.Button(right_controls, text="Настройки", command=open_settings,
                             width=20, height=2)
    settings_btn.pack(pady=5)

    # Текстовый вывод
    text_output = tk.Text(main_tab, height=10, wrap=tk.WORD, font=("Courier", 11))
    text_output.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)
    state.text_output = text_output

    # ─── Вкладка 2: Специальные функции ───
    special_tab = tk.Frame(notebook)
    notebook.add(special_tab, text="Специальные функции")
    special_frame = tk.Frame(special_tab)
    special_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    state.special_frame = special_frame

    # ─── Вкладка 3: Описание ивента ───
    desc_tab = tk.Frame(notebook)
    notebook.add(desc_tab, text="Описание ивента")
    desc_frame = tk.Frame(desc_tab)
    desc_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    description_text_widget = tk.Text(desc_frame, wrap=tk.WORD, font=("Arial", 10))
    description_text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    desc_scroll = tk.Scrollbar(desc_frame, orient=tk.VERTICAL,
                               command=description_text_widget.yview)
    desc_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    description_text_widget.config(yscrollcommand=desc_scroll.set)

    description_text_widget.tag_configure("desc_normal", font=("Arial", 10))
    description_text_widget.tag_configure("desc_medium", font=("Arial", 12, "bold"))
    description_text_widget.tag_configure("desc_large", font=("Arial", 16, "bold"))
    description_text_widget.tag_configure("desc_xlarge", font=("Arial", 20, "bold"))
    state.description_text_widget = description_text_widget

    # ─── Вкладка 4: Управление призами ───
    prizes_tab = tk.Frame(notebook)
    notebook.add(prizes_tab, text="Управление призами")
    create_prizes_tab(prizes_tab)

    # ─── Вкладка 5: Статистика серверов ───
    create_server_stats_tab(notebook)