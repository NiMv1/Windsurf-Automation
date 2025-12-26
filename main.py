"""
Windsurf Automation v3.0 - Простая версия
Работает только через горячие клавиши, без координат
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import time
import threading
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(f"logs/wa_{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('WA')

# Создаём папку logs если нет
os.makedirs('logs', exist_ok=True)

try:
    import pyautogui
    import pyperclip
    AUTOMATION_AVAILABLE = True
except ImportError:
    AUTOMATION_AVAILABLE = False
    logger.warning("pyautogui/pyperclip не установлены. pip install pyautogui pyperclip")

try:
    import win32gui
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    logger.warning("pywin32 не установлен. pip install pywin32")


class Config:
    """Конфигурация программы"""
    
    DEFAULT = {
        "model": "claude-3.5-sonnet",
        "iterations": 1,
        "work_folders": [],
        "prompts_folder": "",
        "delays": {
            "cascade_warmup": 20,  # Ожидание прогрева Cascade
            "after_hotkey": 0.5,
            "after_paste": 0.3,
            "between_messages": 2
        },
        "hotkeys": {
            "new_window": ["ctrl", "shift", "n"],
            "open_cascade": ["ctrl", "l"],
            "select_model": ["ctrl", "/"],
            "send": ["enter"]
        }
    }
    
    def __init__(self, path: str = "config.json"):
        self.path = path
        self.data = self.load()
    
    def load(self) -> dict:
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Объединяем с дефолтными значениями
                    result = self.DEFAULT.copy()
                    result.update(loaded)
                    return result
            except Exception as e:
                logger.error(f"Ошибка загрузки конфига: {e}")
        return self.DEFAULT.copy()
    
    def save(self):
        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Ошибка сохранения конфига: {e}")
    
    def get(self, key: str, default=None):
        return self.data.get(key, default)
    
    def set(self, key: str, value):
        self.data[key] = value
        self.save()


class WindsurfController:
    """Контроллер для управления Windsurf через горячие клавиши"""
    
    def __init__(self, config: Config):
        self.config = config
        self.running = False
        self.current_window = None
    
    def find_windsurf_windows(self) -> list:
        """Найти все окна Windsurf"""
        if not WIN32_AVAILABLE:
            return []
        
        windows = []
        
        def callback(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "windsurf" in title.lower() and "browser" not in title.lower():
                    results.append({
                        "hwnd": hwnd,
                        "title": title[:60] + "..." if len(title) > 60 else title
                    })
            return True
        
        win32gui.EnumWindows(callback, windows)
        return windows
    
    def activate_window(self, hwnd: int) -> bool:
        """Активировать окно"""
        if not WIN32_AVAILABLE:
            return False
        
        try:
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.3)
            return True
        except Exception as e:
            logger.error(f"Ошибка активации окна: {e}")
            return False
    
    def press_hotkey(self, keys: list):
        """Нажать комбинацию клавиш"""
        if not AUTOMATION_AVAILABLE:
            return
        
        pyautogui.hotkey(*keys)
        time.sleep(self.config.get("delays", {}).get("after_hotkey", 0.5))
    
    def paste_text(self, text: str):
        """Вставить текст через буфер обмена"""
        if not AUTOMATION_AVAILABLE:
            return
        
        pyperclip.copy(text)
        time.sleep(0.1)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(self.config.get("delays", {}).get("after_paste", 0.3))
    
    def open_new_window(self):
        """Открыть новое окно Windsurf"""
        logger.info("Открытие нового окна (Ctrl+Shift+N)...")
        self.press_hotkey(self.config.get("hotkeys", {}).get("new_window", ["ctrl", "shift", "n"]))
    
    def open_cascade(self):
        """Открыть панель Cascade"""
        logger.info("Открытие Cascade (Ctrl+L)...")
        self.press_hotkey(self.config.get("hotkeys", {}).get("open_cascade", ["ctrl", "l"]))
    
    def select_model(self, model_name: str):
        """Выбрать модель AI"""
        logger.info(f"Выбор модели: {model_name}")
        
        # Ctrl+/ для открытия выбора модели
        self.press_hotkey(self.config.get("hotkeys", {}).get("select_model", ["ctrl", "/"]))
        time.sleep(0.5)
        
        # Вставляем название модели
        self.paste_text(model_name)
        time.sleep(0.3)
        
        # Стрелка вниз и Enter для выбора
        pyautogui.press("down")
        time.sleep(0.2)
        pyautogui.press("enter")
        time.sleep(0.5)
    
    def send_message(self, message: str):
        """Отправить сообщение в чат"""
        logger.info(f"Отправка сообщения ({len(message)} символов)...")
        
        # Открываем Cascade для фокуса на чате
        self.open_cascade()
        time.sleep(0.3)
        
        # Вставляем сообщение
        self.paste_text(message)
        
        # Отправляем
        self.press_hotkey(self.config.get("hotkeys", {}).get("send", ["enter"]))
    
    def start_session(self, hwnd: int = None, model: str = None):
        """
        Начать новую сессию работы.
        
        Последовательность:
        1. Активировать окно Windsurf (или открыть новое)
        2. Ctrl+Shift+N (новое окно)
        3. Ctrl+L (открыть Cascade) + ждать 20 сек
        4. Ctrl+/ (выбор модели) + ввести модель + стрелка вниз + Enter
        """
        self.running = True
        model = model or self.config.get("model", "claude-3.5-sonnet")
        warmup_time = self.config.get("delays", {}).get("cascade_warmup", 20)
        
        try:
            # 1. Активируем окно если указано
            if hwnd:
                logger.info("Активация окна Windsurf...")
                if not self.activate_window(hwnd):
                    logger.error("Не удалось активировать окно")
                    return False
            
            # 2. Открываем новое окно
            self.open_new_window()
            time.sleep(2)  # Ждём открытия окна
            
            # 3. Открываем Cascade и ждём прогрева
            self.open_cascade()
            logger.info(f"Ожидание прогрева Cascade ({warmup_time} сек)...")
            time.sleep(warmup_time)
            
            # 4. Выбираем модель
            self.select_model(model)
            
            logger.info("Сессия готова к работе!")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска сессии: {e}")
            return False
        finally:
            self.running = False
    
    def stop(self):
        """Остановить выполнение"""
        self.running = False


class SimpleGUI:
    """Простой и лёгкий GUI"""
    
    # Цвета
    BG = "#1a1a2e"
    BG_CARD = "#16213e"
    BG_BUTTON = "#0f3460"
    BG_ACCENT = "#e94560"
    FG = "#ffffff"
    FG_MUTED = "#a0a0a0"
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Windsurf Automation v3.0")
        self.root.geometry("600x700")
        self.root.configure(bg=self.BG)
        self.root.resizable(True, True)
        
        self.config = Config()
        self.controller = WindsurfController(self.config)
        
        self.setup_ui()
        self.refresh_windows()
        self.load_prompts()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        # Заголовок
        tk.Label(
            self.root,
            text="🌊 Windsurf Automation",
            font=("Segoe UI", 16, "bold"),
            fg=self.FG,
            bg=self.BG
        ).pack(pady=(15, 5))
        
        tk.Label(
            self.root,
            text="Автоматизация через горячие клавиши",
            font=("Segoe UI", 10),
            fg=self.FG_MUTED,
            bg=self.BG
        ).pack(pady=(0, 15))
        
        # === Секция: Окна Windsurf ===
        self._create_section("📋 Окна Windsurf")
        
        # Список окон
        self.windows_listbox = tk.Listbox(
            self.root,
            height=4,
            font=("Consolas", 10),
            bg=self.BG_CARD,
            fg=self.FG,
            selectbackground=self.BG_ACCENT,
            borderwidth=0
        )
        self.windows_listbox.pack(fill="x", padx=20, pady=(0, 5))
        
        # Кнопка обновления
        tk.Button(
            self.root,
            text="🔄 Обновить список",
            font=("Segoe UI", 10),
            bg=self.BG_BUTTON,
            fg=self.FG,
            borderwidth=0,
            command=self.refresh_windows
        ).pack(pady=(0, 15))
        
        # === Секция: Настройки ===
        self._create_section("⚙️ Настройки")
        
        settings_frame = tk.Frame(self.root, bg=self.BG)
        settings_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Модель
        row1 = tk.Frame(settings_frame, bg=self.BG)
        row1.pack(fill="x", pady=3)
        tk.Label(row1, text="Модель:", width=15, anchor="w", font=("Segoe UI", 10), fg=self.FG, bg=self.BG).pack(side="left")
        self.model_var = tk.StringVar(value=self.config.get("model", "claude-3.5-sonnet"))
        tk.Entry(row1, textvariable=self.model_var, font=("Consolas", 10), width=30).pack(side="left", padx=(5, 0))
        
        # Итерации
        row2 = tk.Frame(settings_frame, bg=self.BG)
        row2.pack(fill="x", pady=3)
        tk.Label(row2, text="Итерации:", width=15, anchor="w", font=("Segoe UI", 10), fg=self.FG, bg=self.BG).pack(side="left")
        self.iterations_var = tk.IntVar(value=self.config.get("iterations", 1))
        tk.Spinbox(row2, textvariable=self.iterations_var, from_=1, to=100, width=10, font=("Consolas", 10)).pack(side="left", padx=(5, 0))
        
        # Время прогрева Cascade
        row3 = tk.Frame(settings_frame, bg=self.BG)
        row3.pack(fill="x", pady=3)
        tk.Label(row3, text="Прогрев (сек):", width=15, anchor="w", font=("Segoe UI", 10), fg=self.FG, bg=self.BG).pack(side="left")
        self.warmup_var = tk.IntVar(value=self.config.get("delays", {}).get("cascade_warmup", 20))
        tk.Spinbox(row3, textvariable=self.warmup_var, from_=5, to=60, width=10, font=("Consolas", 10)).pack(side="left", padx=(5, 0))
        
        # === Секция: Папки ===
        self._create_section("📁 Папки")
        
        folders_frame = tk.Frame(self.root, bg=self.BG)
        folders_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Папка с промптами
        row4 = tk.Frame(folders_frame, bg=self.BG)
        row4.pack(fill="x", pady=3)
        tk.Label(row4, text="Промпты:", width=15, anchor="w", font=("Segoe UI", 10), fg=self.FG, bg=self.BG).pack(side="left")
        self.prompts_folder_var = tk.StringVar(value=self.config.get("prompts_folder", ""))
        tk.Entry(row4, textvariable=self.prompts_folder_var, font=("Consolas", 9), width=25).pack(side="left", padx=(5, 0))
        tk.Button(row4, text="📂", command=self.browse_prompts_folder, bg=self.BG_BUTTON, fg=self.FG, borderwidth=0).pack(side="left", padx=(5, 0))
        
        # Рабочие папки
        row5 = tk.Frame(folders_frame, bg=self.BG)
        row5.pack(fill="x", pady=3)
        tk.Label(row5, text="Рабочие папки:", width=15, anchor="w", font=("Segoe UI", 10), fg=self.FG, bg=self.BG).pack(side="left")
        tk.Button(row5, text="➕ Добавить", command=self.add_work_folder, bg=self.BG_BUTTON, fg=self.FG, borderwidth=0).pack(side="left", padx=(5, 0))
        
        self.work_folders_listbox = tk.Listbox(
            folders_frame,
            height=3,
            font=("Consolas", 9),
            bg=self.BG_CARD,
            fg=self.FG,
            borderwidth=0
        )
        self.work_folders_listbox.pack(fill="x", pady=(5, 0))
        
        # Загружаем рабочие папки
        for folder in self.config.get("work_folders", []):
            self.work_folders_listbox.insert(tk.END, folder)
        
        # === Секция: Промпты ===
        self._create_section("💬 Промпты")
        
        self.prompts_listbox = tk.Listbox(
            self.root,
            height=4,
            font=("Consolas", 10),
            bg=self.BG_CARD,
            fg=self.FG,
            selectbackground=self.BG_ACCENT,
            borderwidth=0
        )
        self.prompts_listbox.pack(fill="x", padx=20, pady=(0, 15))
        
        # === Кнопки управления ===
        buttons_frame = tk.Frame(self.root, bg=self.BG)
        buttons_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Button(
            buttons_frame,
            text="🚀 Запустить сессию",
            font=("Segoe UI", 12, "bold"),
            bg=self.BG_ACCENT,
            fg=self.FG,
            borderwidth=0,
            width=20,
            command=self.start_session
        ).pack(side="left", padx=(0, 10))
        
        tk.Button(
            buttons_frame,
            text="📤 Отправить промпт",
            font=("Segoe UI", 12),
            bg=self.BG_BUTTON,
            fg=self.FG,
            borderwidth=0,
            width=20,
            command=self.send_selected_prompt
        ).pack(side="left")
        
        # Кнопка сохранения
        tk.Button(
            self.root,
            text="💾 Сохранить настройки",
            font=("Segoe UI", 10),
            bg=self.BG_BUTTON,
            fg=self.FG,
            borderwidth=0,
            command=self.save_settings
        ).pack(pady=10)
        
        # Статус
        self.status_var = tk.StringVar(value="Готов к работе")
        tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Segoe UI", 10),
            fg=self.FG_MUTED,
            bg=self.BG
        ).pack(pady=10)
    
    def _create_section(self, title: str):
        """Создать заголовок секции"""
        tk.Label(
            self.root,
            text=title,
            font=("Segoe UI", 11, "bold"),
            fg=self.FG,
            bg=self.BG,
            anchor="w"
        ).pack(fill="x", padx=20, pady=(10, 5))
    
    def refresh_windows(self):
        """Обновить список окон Windsurf"""
        self.windows_listbox.delete(0, tk.END)
        
        windows = self.controller.find_windsurf_windows()
        self.windows = windows
        
        if windows:
            for w in windows:
                self.windows_listbox.insert(tk.END, f"[{w['hwnd']}] {w['title']}")
        else:
            self.windows_listbox.insert(tk.END, "(Окна Windsurf не найдены)")
        
        self.status_var.set(f"Найдено окон: {len(windows)}")
    
    def load_prompts(self):
        """Загрузить список промптов из папки"""
        self.prompts_listbox.delete(0, tk.END)
        
        folder = self.prompts_folder_var.get()
        if folder and os.path.isdir(folder):
            for file in os.listdir(folder):
                if file.endswith(('.txt', '.md')):
                    self.prompts_listbox.insert(tk.END, file)
    
    def browse_prompts_folder(self):
        """Выбрать папку с промптами"""
        folder = filedialog.askdirectory(title="Выберите папку с промптами")
        if folder:
            self.prompts_folder_var.set(folder)
            self.load_prompts()
    
    def add_work_folder(self):
        """Добавить рабочую папку"""
        folder = filedialog.askdirectory(title="Выберите рабочую папку")
        if folder:
            self.work_folders_listbox.insert(tk.END, folder)
    
    def save_settings(self):
        """Сохранить настройки"""
        self.config.set("model", self.model_var.get())
        self.config.set("iterations", self.iterations_var.get())
        self.config.set("prompts_folder", self.prompts_folder_var.get())
        
        # Сохраняем delays
        delays = self.config.get("delays", {})
        delays["cascade_warmup"] = self.warmup_var.get()
        self.config.set("delays", delays)
        
        # Сохраняем рабочие папки
        work_folders = list(self.work_folders_listbox.get(0, tk.END))
        self.config.set("work_folders", work_folders)
        
        self.config.save()
        self.status_var.set("Настройки сохранены!")
    
    def start_session(self):
        """Запустить новую сессию"""
        # Получаем выбранное окно
        selection = self.windows_listbox.curselection()
        hwnd = None
        
        if selection and self.windows:
            idx = selection[0]
            if idx < len(self.windows):
                hwnd = self.windows[idx]["hwnd"]
        
        model = self.model_var.get()
        
        self.status_var.set("Запуск сессии...")
        
        # Запускаем в отдельном потоке
        def run():
            success = self.controller.start_session(hwnd, model)
            if success:
                self.root.after(0, lambda: self.status_var.set("Сессия готова!"))
            else:
                self.root.after(0, lambda: self.status_var.set("Ошибка запуска сессии"))
        
        threading.Thread(target=run, daemon=True).start()
    
    def send_selected_prompt(self):
        """Отправить выбранный промпт"""
        selection = self.prompts_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите промпт из списка")
            return
        
        filename = self.prompts_listbox.get(selection[0])
        folder = self.prompts_folder_var.get()
        filepath = os.path.join(folder, filename)
        
        if not os.path.exists(filepath):
            messagebox.showerror("Ошибка", f"Файл не найден: {filepath}")
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                prompt = f.read()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл: {e}")
            return
        
        self.status_var.set(f"Отправка: {filename}...")
        
        def run():
            self.controller.send_message(prompt)
            self.root.after(0, lambda: self.status_var.set(f"Отправлено: {filename}"))
        
        threading.Thread(target=run, daemon=True).start()
    
    def run(self):
        """Запустить GUI"""
        self.root.mainloop()


def main():
    """Точка входа"""
    if not AUTOMATION_AVAILABLE:
        print("ОШИБКА: Установите зависимости: pip install pyautogui pyperclip")
        return
    
    if not WIN32_AVAILABLE:
        print("ОШИБКА: Установите pywin32: pip install pywin32")
        return
    
    app = SimpleGUI()
    app.run()


if __name__ == "__main__":
    main()
