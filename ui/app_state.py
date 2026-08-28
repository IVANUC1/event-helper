"""
Хранилище общих ссылок на виджеты и переменные.
Все модули UI обращаются сюда вместо global.
"""

class AppState:
    def __init__(self):
        self.root = None
        self.username_var = None

        # Генератор ивентов
        self.listbox_left = None
        self.listbox_right = None
        self.observer_combobox = None
        self.text_output = None
        self.finish_button = None
        self.assistant_vars = {}
        self.assistant_check_frame = None
        self.special_frame = None
        self.description_text_widget = None
        self.descriptions_dict = {}


state = AppState()