"""
Windsurf Configuration GUI - Настройка координат и горячих клавиш
Позволяет пользователю вручную настроить:
- Координаты элементов интерфейса Windsurf
- Горячие клавиши для различных действий
- Параметры поиска окна
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import threading
import time

try:
    import pyautogui
    import win32gui
    import win32con
    AUTOMATION_AVAILABLE = True
except ImportError:
    AUTOMATION_AVAILABLE = False


class ModernStyle:
    """Современные цвета и стили"""
    BG_DARK = "#1e1e2e"
    BG_CARD = "#2d2d3f"
    BG_BUTTON = "#4a4a6a"
    BG_BUTTON_HOVER = "#5a5a7a"
    BG_SUCCESS = "#4caf50"
    BG_WARNING = "#ff9800"
    BG_DANGER = "#f44336"
    BG_PRIMARY = "#7c3aed"
    
    FG_TEXT = "#ffffff"
    FG_MUTED = "#a0a0b0"
    FG_SUCCESS = "#4caf50"
    
    FONT_TITLE = ("Segoe UI", 14, "bold")
    FONT_SUBTITLE = ("Segoe UI", 11)
    FONT_BUTTON = ("Segoe UI", 10)
    FONT_TEXT = ("Segoe UI", 10)
    FONT_MONO = ("Consolas", 10)


class WindsurfConfigGUI:
    """
    GUI для настройки параметров автоматизации Windsurf.
    Позволяет захватывать координаты кликом и настраивать горячие клавиши.
    """
    
    DEFAULT_CONFIG = {
        "window": {
            "title_pattern": "Windsurf",
            "class_name": "Chrome_WidgetWin_1",
            "exclude_patterns": ["браузер", "browser", "explorer", "проводник"]
        },
        "hotkeys": {
            "open_cascade": "ctrl+l",
            "send_message": "enter",
            "paste": "ctrl+v",
            "select_model": "ctrl+shift+m",
            "new_chat": "ctrl+shift+n"
        },
        "coordinates": {
            "chat_input": {"x": 0, "y": 0, "description": "Поле ввода чата"},
            "send_button": {"x": 0, "y": 0, "description": "Кнопка отправки"},
            "model_selector": {"x": 0, "y": 0, "description": "Выбор модели"},
            "cascade_panel": {"x": 0, "y": 0, "description": "Панель Cascade"}
        },
        "delays": {
            "after_click": 0.1,
            "after_paste": 0.2,
            "after_hotkey": 0.3,
            "wait_response": 5.0
        }
    }
    
    def __init__(self, parent=None):
        """
        Инициализация GUI.
        
        Args:
            parent: Родительское окно (если None - создаётся новое)
        """
        if parent:
            self.root = tk.Toplevel(parent)
        else:
            self.root = tk.Tk()
        
        self.root.title("⚙️ Настройка Windsurf Automation")
        self.root.geometry("700x800")
        self.root.configure(bg=ModernStyle.BG_DARK)
        self.root.resizable(True, True)
        
        self.config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "windsurf_config.json"
        )
        self.config = self.load_config()
        
        self.capturing = False
        self.capture_target = None
        
        self.setup_ui()
        self.load_values_to_ui()
    
    def load_config(self) -> dict:
        """Загрузить конфигурацию из файла"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Объединяем с дефолтными значениями
                    config = self.DEFAULT_CONFIG.copy()
                    self._deep_update(config, loaded)
                    return config
            except Exception as e:
                print(f"Ошибка загрузки конфига: {e}")
        return self.DEFAULT_CONFIG.copy()
    
    def _deep_update(self, base: dict, update: dict):
        """Рекурсивное обновление словаря"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value
    
    def save_config(self):
        """Сохранить конфигурацию в файл"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")
            return False
    
    def setup_ui(self):
        """Настройка интерфейса"""
        # Главный контейнер с прокруткой
        canvas = tk.Canvas(self.root, bg=ModernStyle.BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        
        self.main_frame = tk.Frame(canvas, bg=ModernStyle.BG_DARK)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        canvas_frame = canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        
        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def configure_width(event):
            canvas.itemconfig(canvas_frame, width=event.width)
        
        self.main_frame.bind("<Configure>", configure_scroll)
        canvas.bind("<Configure>", configure_width)
        
        # Заголовок
        self._create_header()
        
        # Секция: Поиск окна
        self._create_window_section()
        
        # Секция: Горячие клавиши
        self._create_hotkeys_section()
        
        # Секция: Координаты
        self._create_coordinates_section()
        
        # Секция: Задержки
        self._create_delays_section()
        
        # Кнопки сохранения
        self._create_buttons()
    
    def _create_header(self):
        """Создать заголовок"""
        header = tk.Frame(self.main_frame, bg=ModernStyle.BG_DARK)
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        tk.Label(
            header,
            text="⚙️ Настройка Windsurf Automation",
            font=ModernStyle.FONT_TITLE,
            fg=ModernStyle.FG_TEXT,
            bg=ModernStyle.BG_DARK
        ).pack(anchor="w")
        
        tk.Label(
            header,
            text="Настройте координаты и горячие клавиши для автоматизации",
            font=ModernStyle.FONT_TEXT,
            fg=ModernStyle.FG_MUTED,
            bg=ModernStyle.BG_DARK
        ).pack(anchor="w")
    
    def _create_section(self, title: str) -> tk.Frame:
        """Создать секцию с заголовком"""
        section = tk.Frame(self.main_frame, bg=ModernStyle.BG_CARD)
        section.pack(fill="x", padx=20, pady=10)
        
        tk.Label(
            section,
            text=title,
            font=ModernStyle.FONT_SUBTITLE,
            fg=ModernStyle.FG_TEXT,
            bg=ModernStyle.BG_CARD
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        content = tk.Frame(section, bg=ModernStyle.BG_CARD)
        content.pack(fill="x", padx=15, pady=(0, 15))
        
        return content
    
    def _create_window_section(self):
        """Секция настройки поиска окна"""
        content = self._create_section("🔍 Поиск окна Windsurf")
        
        # Паттерн заголовка
        row1 = tk.Frame(content, bg=ModernStyle.BG_CARD)
        row1.pack(fill="x", pady=5)
        
        tk.Label(
            row1, text="Паттерн заголовка:",
            font=ModernStyle.FONT_TEXT, fg=ModernStyle.FG_TEXT, bg=ModernStyle.BG_CARD
        ).pack(side="left")
        
        self.title_pattern_var = tk.StringVar()
        tk.Entry(
            row1, textvariable=self.title_pattern_var,
            font=ModernStyle.FONT_MONO, width=30
        ).pack(side="left", padx=(10, 0))
        
        # Класс окна
        row2 = tk.Frame(content, bg=ModernStyle.BG_CARD)
        row2.pack(fill="x", pady=5)
        
        tk.Label(
            row2, text="Класс окна:",
            font=ModernStyle.FONT_TEXT, fg=ModernStyle.FG_TEXT, bg=ModernStyle.BG_CARD
        ).pack(side="left")
        
        self.class_name_var = tk.StringVar()
        tk.Entry(
            row2, textvariable=self.class_name_var,
            font=ModernStyle.FONT_MONO, width=30
        ).pack(side="left", padx=(10, 0))
        
        # Кнопка тестирования
        test_btn = tk.Button(
            content, text="🔎 Найти окно",
            font=ModernStyle.FONT_BUTTON,
            bg=ModernStyle.BG_PRIMARY,
            fg=ModernStyle.FG_TEXT,
            command=self.test_find_window
        )
        test_btn.pack(anchor="w", pady=(10, 0))
    
    def _create_hotkeys_section(self):
        """Секция настройки горячих клавиш"""
        content = self._create_section("⌨️ Горячие клавиши")
        
        self.hotkey_vars = {}
        
        hotkeys = [
            ("open_cascade", "Открыть Cascade:", "ctrl+l"),
            ("send_message", "Отправить сообщение:", "enter"),
            ("paste", "Вставить:", "ctrl+v"),
            ("select_model", "Выбор модели:", "ctrl+shift+m"),
            ("new_chat", "Новый чат:", "ctrl+shift+n")
        ]
        
        for key, label, default in hotkeys:
            row = tk.Frame(content, bg=ModernStyle.BG_CARD)
            row.pack(fill="x", pady=3)
            
            tk.Label(
                row, text=label, width=20, anchor="w",
                font=ModernStyle.FONT_TEXT, fg=ModernStyle.FG_TEXT, bg=ModernStyle.BG_CARD
            ).pack(side="left")
            
            var = tk.StringVar(value=default)
            self.hotkey_vars[key] = var
            
            entry = tk.Entry(row, textvariable=var, font=ModernStyle.FONT_MONO, width=20)
            entry.pack(side="left", padx=(10, 0))
            
            # Кнопка захвата
            capture_btn = tk.Button(
                row, text="📝",
                font=ModernStyle.FONT_BUTTON,
                bg=ModernStyle.BG_BUTTON,
                fg=ModernStyle.FG_TEXT,
                command=lambda k=key: self.capture_hotkey(k)
            )
            capture_btn.pack(side="left", padx=(5, 0))
    
    def _create_coordinates_section(self):
        """Секция настройки координат"""
        content = self._create_section("📍 Координаты (относительно окна)")
        
        self.coord_vars = {}
        
        coords = [
            ("chat_input", "Поле ввода чата"),
            ("send_button", "Кнопка отправки"),
            ("model_selector", "Выбор модели"),
            ("cascade_panel", "Панель Cascade")
        ]
        
        for key, label in coords:
            row = tk.Frame(content, bg=ModernStyle.BG_CARD)
            row.pack(fill="x", pady=5)
            
            tk.Label(
                row, text=f"{label}:", width=18, anchor="w",
                font=ModernStyle.FONT_TEXT, fg=ModernStyle.FG_TEXT, bg=ModernStyle.BG_CARD
            ).pack(side="left")
            
            # X координата
            tk.Label(
                row, text="X:",
                font=ModernStyle.FONT_TEXT, fg=ModernStyle.FG_MUTED, bg=ModernStyle.BG_CARD
            ).pack(side="left", padx=(10, 2))
            
            x_var = tk.IntVar(value=0)
            tk.Entry(row, textvariable=x_var, font=ModernStyle.FONT_MONO, width=6).pack(side="left")
            
            # Y координата
            tk.Label(
                row, text="Y:",
                font=ModernStyle.FONT_TEXT, fg=ModernStyle.FG_MUTED, bg=ModernStyle.BG_CARD
            ).pack(side="left", padx=(10, 2))
            
            y_var = tk.IntVar(value=0)
            tk.Entry(row, textvariable=y_var, font=ModernStyle.FONT_MONO, width=6).pack(side="left")
            
            self.coord_vars[key] = {"x": x_var, "y": y_var}
            
            # Кнопка захвата координат
            capture_btn = tk.Button(
                row, text="🎯 Захватить",
                font=ModernStyle.FONT_BUTTON,
                bg=ModernStyle.BG_WARNING,
                fg="#000000",
                command=lambda k=key: self.start_coordinate_capture(k)
            )
            capture_btn.pack(side="left", padx=(10, 0))
        
        # Инструкция
        tk.Label(
            content,
            text="💡 Нажмите 'Захватить' и кликните в нужное место в окне Windsurf",
            font=ModernStyle.FONT_TEXT,
            fg=ModernStyle.FG_MUTED,
            bg=ModernStyle.BG_CARD
        ).pack(anchor="w", pady=(10, 0))
    
    def _create_delays_section(self):
        """Секция настройки задержек"""
        content = self._create_section("⏱️ Задержки (секунды)")
        
        self.delay_vars = {}
        
        delays = [
            ("after_click", "После клика:", 0.1),
            ("after_paste", "После вставки:", 0.2),
            ("after_hotkey", "После горячей клавиши:", 0.3),
            ("wait_response", "Ожидание ответа:", 5.0)
        ]
        
        for key, label, default in delays:
            row = tk.Frame(content, bg=ModernStyle.BG_CARD)
            row.pack(fill="x", pady=3)
            
            tk.Label(
                row, text=label, width=22, anchor="w",
                font=ModernStyle.FONT_TEXT, fg=ModernStyle.FG_TEXT, bg=ModernStyle.BG_CARD
            ).pack(side="left")
            
            var = tk.DoubleVar(value=default)
            self.delay_vars[key] = var
            
            tk.Entry(row, textvariable=var, font=ModernStyle.FONT_MONO, width=8).pack(side="left", padx=(10, 0))
    
    def _create_buttons(self):
        """Создать кнопки сохранения"""
        buttons = tk.Frame(self.main_frame, bg=ModernStyle.BG_DARK)
        buttons.pack(fill="x", padx=20, pady=20)
        
        # Сохранить
        save_btn = tk.Button(
            buttons, text="💾 Сохранить",
            font=ModernStyle.FONT_BUTTON,
            bg=ModernStyle.BG_SUCCESS,
            fg=ModernStyle.FG_TEXT,
            width=15,
            command=self.save_all
        )
        save_btn.pack(side="left", padx=(0, 10))
        
        # Сбросить
        reset_btn = tk.Button(
            buttons, text="🔄 Сбросить",
            font=ModernStyle.FONT_BUTTON,
            bg=ModernStyle.BG_DANGER,
            fg=ModernStyle.FG_TEXT,
            width=15,
            command=self.reset_to_defaults
        )
        reset_btn.pack(side="left", padx=(0, 10))
        
        # Тест
        test_btn = tk.Button(
            buttons, text="🧪 Тест",
            font=ModernStyle.FONT_BUTTON,
            bg=ModernStyle.BG_PRIMARY,
            fg=ModernStyle.FG_TEXT,
            width=15,
            command=self.test_automation
        )
        test_btn.pack(side="left")
    
    def load_values_to_ui(self):
        """Загрузить значения из конфига в UI"""
        # Окно
        self.title_pattern_var.set(self.config["window"]["title_pattern"])
        self.class_name_var.set(self.config["window"]["class_name"])
        
        # Горячие клавиши
        for key, var in self.hotkey_vars.items():
            if key in self.config["hotkeys"]:
                var.set(self.config["hotkeys"][key])
        
        # Координаты
        for key, vars_dict in self.coord_vars.items():
            if key in self.config["coordinates"]:
                vars_dict["x"].set(self.config["coordinates"][key].get("x", 0))
                vars_dict["y"].set(self.config["coordinates"][key].get("y", 0))
        
        # Задержки
        for key, var in self.delay_vars.items():
            if key in self.config["delays"]:
                var.set(self.config["delays"][key])
    
    def save_all(self):
        """Сохранить все настройки"""
        # Окно
        self.config["window"]["title_pattern"] = self.title_pattern_var.get()
        self.config["window"]["class_name"] = self.class_name_var.get()
        
        # Горячие клавиши
        for key, var in self.hotkey_vars.items():
            self.config["hotkeys"][key] = var.get()
        
        # Координаты
        for key, vars_dict in self.coord_vars.items():
            if key not in self.config["coordinates"]:
                self.config["coordinates"][key] = {}
            self.config["coordinates"][key]["x"] = vars_dict["x"].get()
            self.config["coordinates"][key]["y"] = vars_dict["y"].get()
        
        # Задержки
        for key, var in self.delay_vars.items():
            self.config["delays"][key] = var.get()
        
        if self.save_config():
            messagebox.showinfo("Успех", "Настройки сохранены!")
    
    def reset_to_defaults(self):
        """Сбросить к значениям по умолчанию"""
        if messagebox.askyesno("Подтверждение", "Сбросить все настройки?"):
            self.config = self.DEFAULT_CONFIG.copy()
            self.load_values_to_ui()
            messagebox.showinfo("Готово", "Настройки сброшены")
    
    def test_find_window(self):
        """Тестировать поиск окна Windsurf"""
        if not AUTOMATION_AVAILABLE:
            messagebox.showerror("Ошибка", "Модули pyautogui/win32gui не установлены")
            return
        
        pattern = self.title_pattern_var.get()
        class_name = self.class_name_var.get()
        
        found_windows = []
        
        def enum_callback(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                wnd_class = win32gui.GetClassName(hwnd)
                
                if pattern.lower() in title.lower():
                    if not class_name or wnd_class == class_name:
                        # Проверяем исключения
                        exclude = self.config["window"].get("exclude_patterns", [])
                        if not any(ex.lower() in title.lower() for ex in exclude):
                            results.append((hwnd, title, wnd_class))
            return True
        
        win32gui.EnumWindows(enum_callback, found_windows)
        
        if found_windows:
            msg = f"Найдено окон: {len(found_windows)}\n\n"
            for hwnd, title, wnd_class in found_windows[:5]:
                msg += f"• {title[:50]}...\n  Класс: {wnd_class}\n\n"
            messagebox.showinfo("Результат поиска", msg)
        else:
            messagebox.showwarning("Не найдено", "Окна Windsurf не найдены")
    
    def start_coordinate_capture(self, target: str):
        """Начать захват координат"""
        if not AUTOMATION_AVAILABLE:
            messagebox.showerror("Ошибка", "Модули pyautogui/win32gui не установлены")
            return
        
        self.capture_target = target
        self.capturing = True
        
        # Создаём overlay окно
        self.capture_window = tk.Toplevel(self.root)
        self.capture_window.attributes("-fullscreen", True)
        self.capture_window.attributes("-alpha", 0.3)
        self.capture_window.attributes("-topmost", True)
        self.capture_window.configure(bg="blue")
        
        label = tk.Label(
            self.capture_window,
            text=f"🎯 Кликните в нужное место для '{target}'\n(ESC для отмены)",
            font=("Segoe UI", 24, "bold"),
            fg="white",
            bg="blue"
        )
        label.place(relx=0.5, rely=0.5, anchor="center")
        
        self.capture_window.bind("<Button-1>", self.on_capture_click)
        self.capture_window.bind("<Escape>", self.cancel_capture)
        self.capture_window.focus_force()
    
    def on_capture_click(self, event):
        """Обработка клика при захвате координат"""
        x, y = event.x_root, event.y_root
        
        # Находим окно Windsurf для вычисления относительных координат
        pattern = self.title_pattern_var.get()
        
        def find_windsurf():
            result = [None]
            def callback(hwnd, _):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if pattern.lower() in title.lower():
                        result[0] = hwnd
                        return False
                return True
            win32gui.EnumWindows(callback, None)
            return result[0]
        
        hwnd = find_windsurf()
        
        if hwnd:
            rect = win32gui.GetWindowRect(hwnd)
            rel_x = x - rect[0]
            rel_y = y - rect[1]
            
            self.coord_vars[self.capture_target]["x"].set(rel_x)
            self.coord_vars[self.capture_target]["y"].set(rel_y)
            
            messagebox.showinfo(
                "Координаты захвачены",
                f"Абсолютные: ({x}, {y})\nОтносительные: ({rel_x}, {rel_y})"
            )
        else:
            # Сохраняем абсолютные координаты
            self.coord_vars[self.capture_target]["x"].set(x)
            self.coord_vars[self.capture_target]["y"].set(y)
            messagebox.showwarning(
                "Окно не найдено",
                f"Сохранены абсолютные координаты: ({x}, {y})"
            )
        
        self.cancel_capture(None)
    
    def cancel_capture(self, event):
        """Отменить захват координат"""
        self.capturing = False
        self.capture_target = None
        if hasattr(self, 'capture_window'):
            self.capture_window.destroy()
    
    def capture_hotkey(self, key: str):
        """Захватить горячую клавишу"""
        messagebox.showinfo(
            "Захват клавиши",
            f"Введите комбинацию клавиш в поле '{key}'\n\n"
            "Формат: ctrl+shift+a, alt+f4, enter и т.д."
        )
    
    def test_automation(self):
        """Тестировать автоматизацию"""
        if not AUTOMATION_AVAILABLE:
            messagebox.showerror("Ошибка", "Модули автоматизации не установлены")
            return
        
        result = messagebox.askyesno(
            "Тест автоматизации",
            "Будет выполнен тест:\n"
            "1. Найти окно Windsurf\n"
            "2. Активировать его\n"
            "3. Открыть Cascade (если настроено)\n\n"
            "Продолжить?"
        )
        
        if result:
            threading.Thread(target=self._run_test, daemon=True).start()
    
    def _run_test(self):
        """Выполнить тест в отдельном потоке"""
        try:
            pattern = self.title_pattern_var.get()
            
            # Найти окно
            hwnd = None
            def callback(h, _):
                nonlocal hwnd
                if win32gui.IsWindowVisible(h):
                    title = win32gui.GetWindowText(h)
                    if pattern.lower() in title.lower():
                        hwnd = h
                        return False
                return True
            win32gui.EnumWindows(callback, None)
            
            if not hwnd:
                self.root.after(0, lambda: messagebox.showerror("Ошибка", "Окно не найдено"))
                return
            
            # Активировать окно
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
            
            # Открыть Cascade
            hotkey = self.hotkey_vars.get("open_cascade")
            if hotkey:
                pyautogui.hotkey(*hotkey.get().split("+"))
                time.sleep(0.3)
            
            self.root.after(0, lambda: messagebox.showinfo("Тест завершён", "Тест выполнен успешно!"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Ошибка теста", str(e)))
    
    def run(self):
        """Запустить GUI"""
        self.root.mainloop()


def main():
    """Точка входа"""
    app = WindsurfConfigGUI()
    app.run()


if __name__ == "__main__":
    main()
