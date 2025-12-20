"""
Windsurf Automation - Современный GUI v1.0
Полная версия с автоматическим выбором модели и очередью задач
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import sys
import os
import json
import time
import threading
import logging
import subprocess
import winsound
from datetime import datetime

# Добавляем путь к src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from windsurf_automation import WindsurfAutomation, find_windsurf_windows
from config import load_config, save_config, get_setting, set_setting

# Настройка логирования в файл
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"wa_{datetime.now().strftime('%Y%m%d')}.log")

# Настройка логирования с уровнями DEBUG/INFO (как в JabRef PR #14649)
logger = logging.getLogger('WA')
logger.setLevel(logging.DEBUG)  # DEBUG для детальной информации

# Файловый handler - DEBUG уровень (всё логируется)
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

# Консольный handler - INFO уровень (меньше шума)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))

logger.addHandler(file_handler)
logger.addHandler(console_handler)


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
    BG_PRIMARY_HOVER = "#8b5cf6"
    
    FG_TEXT = "#ffffff"
    FG_MUTED = "#a0a0b0"
    FG_SUCCESS = "#4caf50"
    FG_WARNING = "#ff9800"
    
    FONT_TITLE = ("Segoe UI", 18, "bold")
    FONT_SUBTITLE = ("Segoe UI", 12)
    FONT_BUTTON = ("Segoe UI", 11)
    FONT_TEXT = ("Segoe UI", 10)
    FONT_MONO = ("Consolas", 10)


class WindsurfAutomationGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Windsurf Automation v1.2.2")
        self.root.geometry("800x600")
        self.root.configure(bg=ModernStyle.BG_DARK)
        self.root.resizable(True, True)
        
        # Иконка (если есть)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        self.wa = WindsurfAutomation()
        self.tasks_file = os.path.join(os.path.dirname(__file__), 'tasks', 'tasks.json')
        self.config = load_config()  # Загружаем настройки
        
        self.setup_ui()
        self.apply_config()  # Применяем настройки к GUI
        self.refresh_windows()
        self.load_tasks()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        # Главный контейнер
        main_frame = tk.Frame(self.root, bg=ModernStyle.BG_DARK)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Заголовок
        header = tk.Frame(main_frame, bg=ModernStyle.BG_DARK)
        header.pack(fill=tk.X, pady=(0, 20))
        
        title = tk.Label(header, text="🚀 Windsurf Automation", 
                        font=ModernStyle.FONT_TITLE, 
                        fg=ModernStyle.FG_TEXT, bg=ModernStyle.BG_DARK)
        title.pack(side=tk.LEFT)
        
        version = tk.Label(header, text="v1.2.2", 
                          font=ModernStyle.FONT_SUBTITLE,
                          fg=ModernStyle.FG_MUTED, bg=ModernStyle.BG_DARK)
        version.pack(side=tk.LEFT, padx=10)
        
        # Статус подключения
        self.status_label = tk.Label(header, text="⚪ Не подключено",
                                    font=ModernStyle.FONT_TEXT,
                                    fg=ModernStyle.FG_MUTED, bg=ModernStyle.BG_DARK)
        self.status_label.pack(side=tk.RIGHT)
        
        # Панель выбора модели
        model_frame = tk.Frame(main_frame, bg=ModernStyle.BG_CARD, padx=10, pady=8)
        model_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(model_frame, text="🤖 Модель:",
                font=ModernStyle.FONT_TEXT,
                fg=ModernStyle.FG_TEXT, bg=ModernStyle.BG_CARD).pack(side=tk.LEFT)
        
        self.model_var = tk.StringVar(value="SWE-1")
        model_combo = ttk.Combobox(model_frame, textvariable=self.model_var,
                                   values=["SWE-1", "GPT-5.1-Codex", "Grok Code Fast 1"],
                                   font=ModernStyle.FONT_TEXT, width=20, state="readonly")
        model_combo.pack(side=tk.LEFT, padx=10)
        
        self.auto_model_var = tk.BooleanVar(value=True)
        auto_check = tk.Checkbutton(model_frame, text="Авто-выбор модели",
                                   variable=self.auto_model_var,
                                   font=ModernStyle.FONT_TEXT,
                                   fg=ModernStyle.FG_TEXT, bg=ModernStyle.BG_CARD,
                                   selectcolor=ModernStyle.BG_DARK,
                                   activebackground=ModernStyle.BG_CARD)
        auto_check.pack(side=tk.LEFT, padx=20)
        
        # Основной контент - две колонки
        content = tk.Frame(main_frame, bg=ModernStyle.BG_DARK)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Левая колонка - Окна и запуск
        left_col = tk.Frame(content, bg=ModernStyle.BG_DARK, width=350)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Карточка "Окна Windsurf"
        windows_card = self.create_card(left_col, "🪟 Окна Windsurf (двойной клик = фокус)")
        
        self.windows_listbox = tk.Listbox(windows_card, 
                                          font=ModernStyle.FONT_MONO,
                                          bg=ModernStyle.BG_DARK,
                                          fg=ModernStyle.FG_TEXT,
                                          selectbackground=ModernStyle.BG_PRIMARY,
                                          height=6,
                                          borderwidth=0,
                                          highlightthickness=1,
                                          highlightbackground=ModernStyle.BG_BUTTON)
        self.windows_listbox.pack(fill=tk.X, pady=5)
        self.windows_listbox.bind('<<ListboxSelect>>', self.on_window_select)
        self.windows_listbox.bind('<Double-Button-1>', self.on_window_double_click)
        
        btn_refresh = self.create_button(windows_card, "🔄 Обновить список", 
                                        self.refresh_windows, ModernStyle.BG_BUTTON)
        btn_refresh.pack(fill=tk.X, pady=5)
        
        # Карточка "Запуск задачи"
        run_card = self.create_card(left_col, "🚀 Запуск задачи")
        
        self.btn_full_task = self.create_button(run_card, "⚡ Новое окно + Промпт", 
                                               self.full_task_dialog, ModernStyle.BG_SUCCESS)
        self.btn_full_task.pack(fill=tk.X, pady=5)
        
        # Кнопка запуска теста (как в JabRef)
        self.btn_test = self.create_button(run_card, "🧪 Запустить тест", 
                                          self.run_test, ModernStyle.BG_WARNING)
        self.btn_test.pack(fill=tk.X, pady=5)
        
        # Прогресс-бар
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(run_card, variable=self.progress_var, 
                                            maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Чекбокс звука
        self.sound_var = tk.BooleanVar(value=True)
        sound_check = tk.Checkbutton(run_card, text="🔊 Звук при завершении",
                                    variable=self.sound_var,
                                    font=ModernStyle.FONT_TEXT,
                                    fg=ModernStyle.FG_TEXT, bg=ModernStyle.BG_CARD,
                                    selectcolor=ModernStyle.BG_DARK,
                                    activebackground=ModernStyle.BG_CARD)
        sound_check.pack(anchor=tk.W, pady=5)
        
        # Правая колонка - Задачи
        right_col = tk.Frame(content, bg=ModernStyle.BG_DARK, width=350)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Карточка "Задачи"
        tasks_card = self.create_card(right_col, "📋 Задачи")
        
        self.tasks_listbox = tk.Listbox(tasks_card,
                                        font=ModernStyle.FONT_TEXT,
                                        bg=ModernStyle.BG_DARK,
                                        fg=ModernStyle.FG_TEXT,
                                        selectbackground=ModernStyle.BG_PRIMARY,
                                        height=8,
                                        borderwidth=0,
                                        highlightthickness=1,
                                        highlightbackground=ModernStyle.BG_BUTTON)
        self.tasks_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tasks_buttons = tk.Frame(tasks_card, bg=ModernStyle.BG_CARD)
        tasks_buttons.pack(fill=tk.X, pady=5)
        
        btn_add_task = self.create_button(tasks_buttons, "➕ Добавить", 
                                         self.add_task_dialog, ModernStyle.BG_SUCCESS)
        btn_add_task.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        btn_run_task = self.create_button(tasks_buttons, "▶️ Выполнить", 
                                         self.run_selected_task, ModernStyle.BG_PRIMARY)
        btn_run_task.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))
        
        # Кнопка запуска очереди
        btn_run_queue = self.create_button(tasks_card, "🔄 Запустить все задачи", 
                                          self.run_all_tasks, ModernStyle.BG_WARNING)
        btn_run_queue.pack(fill=tk.X, pady=5)
        
        # Кнопка удаления задачи
        btn_delete_task = self.create_button(tasks_card, "🗑️ Удалить выбранную", 
                                            self.delete_selected_task, ModernStyle.BG_DANGER)
        btn_delete_task.pack(fill=tk.X, pady=5)
        
        # Карточка "История"
        history_card = self.create_card(right_col, "📜 История выполненных")
        
        self.history_listbox = tk.Listbox(history_card,
                                          font=ModernStyle.FONT_TEXT,
                                          bg=ModernStyle.BG_DARK,
                                          fg=ModernStyle.FG_MUTED,
                                          height=4,
                                          borderwidth=0,
                                          highlightthickness=1,
                                          highlightbackground=ModernStyle.BG_BUTTON)
        self.history_listbox.pack(fill=tk.X, pady=5)
        
        btn_clear_history = self.create_button(history_card, "🗑️ Очистить историю", 
                                              self.clear_history, ModernStyle.BG_BUTTON)
        btn_clear_history.pack(fill=tk.X, pady=5)
        
        # Карточка "Boss/Worker"
        boss_card = self.create_card(left_col, "👔 Boss/Worker")
        
        btn_boss = self.create_button(boss_card, "👔 Запустить Boss", 
                                     self.run_boss, ModernStyle.BG_PRIMARY)
        btn_boss.pack(fill=tk.X, pady=5)
        
        btn_boss_check = self.create_button(boss_card, "🔍 Проверить результаты", 
                                           self.check_boss_results, ModernStyle.BG_BUTTON)
        btn_boss_check.pack(fill=tk.X, pady=5)
        
        # Лог
        log_card = self.create_card(main_frame, "📝 Лог")
        log_card.pack(fill=tk.X, pady=(15, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_card,
                                                  font=ModernStyle.FONT_MONO,
                                                  bg=ModernStyle.BG_DARK,
                                                  fg=ModernStyle.FG_TEXT,
                                                  height=6,
                                                  borderwidth=0,
                                                  highlightthickness=1,
                                                  highlightbackground=ModernStyle.BG_BUTTON)
        self.log_text.pack(fill=tk.X, pady=5)
        
        self.log("Windsurf Automation v1.0 запущен")
        
        # Подключаем callback для логирования из WA
        self.wa.log_callback = self.log
    
    def create_card(self, parent, title):
        """Создать карточку с заголовком"""
        card = tk.Frame(parent, bg=ModernStyle.BG_CARD, padx=15, pady=10)
        card.pack(fill=tk.X, pady=5)
        
        title_label = tk.Label(card, text=title,
                              font=ModernStyle.FONT_SUBTITLE,
                              fg=ModernStyle.FG_TEXT, bg=ModernStyle.BG_CARD)
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        return card
    
    def create_button(self, parent, text, command, bg_color):
        """Создать стилизованную кнопку"""
        btn = tk.Button(parent, text=text,
                       font=ModernStyle.FONT_BUTTON,
                       fg=ModernStyle.FG_TEXT,
                       bg=bg_color,
                       activebackground=ModernStyle.BG_PRIMARY_HOVER,
                       activeforeground=ModernStyle.FG_TEXT,
                       borderwidth=0,
                       padx=15, pady=8,
                       cursor="hand2",
                       command=command)
        
        # Hover эффект
        def on_enter(e):
            btn.configure(bg=ModernStyle.BG_PRIMARY_HOVER)
        def on_leave(e):
            btn.configure(bg=bg_color)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def apply_config(self):
        """Применить настройки из config.json к GUI"""
        try:
            # Модель
            model = self.config.get('model', 'GPT-5.1-Codex')
            self.model_var.set(model)
            
            # Звук
            sound = self.config.get('sound_enabled', True)
            self.sound_var.set(sound)
            
            logger.debug(f"Config applied: model={model}, sound={sound}")
        except Exception as e:
            logger.error(f"Error applying config: {e}")
    
    def save_current_config(self):
        """Сохранить текущие настройки GUI в config.json"""
        self.config['model'] = self.model_var.get()
        self.config['sound_enabled'] = self.sound_var.get()
        save_config(self.config)
        logger.debug("Config saved")
    
    def log(self, message):
        """Добавить сообщение в лог"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        # Логируем в файл через logger (INFO уровень для GUI сообщений)
        logger.info(message)
        
        # Обновляем GUI (thread-safe)
        def update():
            self.log_text.insert(tk.END, f"{log_message}\n")
            self.log_text.see(tk.END)
        
        try:
            self.root.after(0, update)
        except:
            pass  # GUI может быть закрыт
    
    def refresh_windows(self):
        """Обновить список окон"""
        self.windows_listbox.delete(0, tk.END)
        windows = find_windsurf_windows(ide_only=True)
        
        if windows:
            for hwnd, title in windows:
                short_title = title[:50] + "..." if len(title) > 50 else title
                self.windows_listbox.insert(tk.END, f"[{hwnd}] {short_title}")
            
            # Выбрать первое окно
            self.windows_listbox.selection_set(0)
            self.wa.hwnd, self.wa.title = windows[0]
            self.log(f"Найдено {len(windows)} окон Windsurf")
            self.status_label.configure(text="🟢 Подключено", fg=ModernStyle.FG_SUCCESS)
        else:
            self.windows_listbox.insert(tk.END, "Нет открытых окон")
            self.log("⚠️ Окна Windsurf не найдены")
            self.status_label.configure(text="🔴 Не подключено", fg=ModernStyle.BG_DANGER)
    
    def on_window_select(self, event):
        """Обработка выбора окна"""
        selection = self.windows_listbox.curselection()
        if selection:
            windows = find_windsurf_windows(ide_only=True)
            if selection[0] < len(windows):
                self.wa.hwnd, self.wa.title = windows[selection[0]]
                self.log(f"Выбрано окно: {self.wa.title[:40]}...")
    
    def on_window_double_click(self, event):
        """Двойной клик - переключить фокус на окно"""
        selection = self.windows_listbox.curselection()
        if selection:
            windows = find_windsurf_windows(ide_only=True)
            if selection[0] < len(windows):
                self.wa.hwnd, self.wa.title = windows[selection[0]]
                self.log(f"🔄 Переключаюсь на: {self.wa.title[:40]}...")
                
                def activate():
                    from windsurf_automation import activate_window_by_hwnd
                    activate_window_by_hwnd(self.wa.hwnd)
                    self.log("✅ Окно активировано")
                
                threading.Thread(target=activate, daemon=True).start()
    
    def load_tasks(self):
        """Загрузить задачи"""
        self.tasks_listbox.delete(0, tk.END)
        
        if os.path.exists(self.tasks_file):
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                tasks = data.get('tasks', [])
                
                for task in tasks:
                    status_icon = "✅" if task['status'] == 'completed' else "⏳" if task['status'] == 'in_progress' else "📌"
                    self.tasks_listbox.insert(tk.END, f"{status_icon} [{task['id']}] {task['title']} ({task['model']})")
    
    def add_task_dialog(self):
        """Диалог добавления задачи"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить задачу")
        dialog.geometry("500x350")
        dialog.configure(bg=ModernStyle.BG_DARK)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Название
        tk.Label(dialog, text="Название:",
                font=ModernStyle.FONT_TEXT,
                fg=ModernStyle.FG_TEXT, bg=ModernStyle.BG_DARK).pack(anchor=tk.W, padx=20, pady=(15, 5))
        
        title_entry = tk.Entry(dialog, font=ModernStyle.FONT_TEXT,
                              bg=ModernStyle.BG_CARD, fg=ModernStyle.FG_TEXT,
                              insertbackground=ModernStyle.FG_TEXT)
        title_entry.pack(fill=tk.X, padx=20)
        
        # Промпт
        tk.Label(dialog, text="Промпт для ИИ:",
                font=ModernStyle.FONT_TEXT,
                fg=ModernStyle.FG_TEXT, bg=ModernStyle.BG_DARK).pack(anchor=tk.W, padx=20, pady=(15, 5))
        
        prompt_entry = tk.Text(dialog, height=4,
                              font=ModernStyle.FONT_TEXT,
                              bg=ModernStyle.BG_CARD, fg=ModernStyle.FG_TEXT,
                              insertbackground=ModernStyle.FG_TEXT)
        prompt_entry.pack(fill=tk.X, padx=20)
        
        # Модель
        tk.Label(dialog, text="Модель:",
                font=ModernStyle.FONT_TEXT,
                fg=ModernStyle.FG_TEXT, bg=ModernStyle.BG_DARK).pack(anchor=tk.W, padx=20, pady=(15, 5))
        
        model_var = tk.StringVar(value="SWE-1")
        model_combo = ttk.Combobox(dialog, textvariable=model_var,
                                   values=["SWE-1", "GPT-5.1-Codex", "Grok Code Fast 1"],
                                   font=ModernStyle.FONT_TEXT)
        model_combo.pack(fill=tk.X, padx=20)
        
        def save():
            title = title_entry.get().strip()
            prompt = prompt_entry.get("1.0", tk.END).strip()
            model = model_var.get()
            
            if not title or not prompt:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return
            
            # Загрузить и обновить
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            tasks = data.get('tasks', [])
            new_id = max([t['id'] for t in tasks], default=0) + 1
            
            tasks.append({
                "id": new_id,
                "title": title,
                "prompt": prompt,
                "model": model,
                "status": "pending",
                "priority": "medium",
                "created": time.strftime("%Y-%m-%d")
            })
            
            data['tasks'] = tasks
            
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            dialog.destroy()
            self.load_tasks()
            self.log(f"✅ Задача #{new_id} добавлена")
        
        btn = self.create_button(dialog, "💾 Сохранить", save, ModernStyle.BG_SUCCESS)
        btn.pack(pady=20)
    
    def run_selected_task(self):
        """Выполнить выбранную задачу с автоматическим выбором модели"""
        selection = self.tasks_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите задачу")
            return
        
        # Получить ID задачи из текста
        text = self.tasks_listbox.get(selection[0])
        try:
            task_id = int(text.split('[')[1].split(']')[0])
        except:
            return
        
        # Найти задачу
        with open(self.tasks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        task = next((t for t in data['tasks'] if t['id'] == task_id), None)
        if not task:
            return
        
        self.log(f"🚀 Выполняю задачу #{task_id}: {task['title']}")
        
        def run():
            # Используем полный цикл run_task
            model = task.get('model', self.model_var.get())
            success = self.wa.run_task(task['prompt'], model, close_after=False)
            
            if success:
                # Обновить статус
                for t in data['tasks']:
                    if t['id'] == task_id:
                        t['status'] = 'in_progress'
                
                with open(self.tasks_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                self.root.after(0, self.load_tasks)
                # Добавляем в историю
                self.root.after(0, lambda: self.add_to_history(task['title']))
                # Звук при успехе
                self.play_sound()
            else:
                self.log("❌ Не удалось отправить промпт")
            
            self.root.after(0, self.refresh_windows)
        
        threading.Thread(target=run, daemon=True).start()
    
    def full_task_dialog(self):
        """Диалог полного цикла задачи (окно + модель + промпт)"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Полный цикл задачи")
        dialog.geometry("550x300")
        dialog.configure(bg=ModernStyle.BG_DARK)
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="⚡ Полный цикл: открытие окна + выбор модели + отправка промпта",
                font=ModernStyle.FONT_SUBTITLE,
                fg=ModernStyle.FG_TEXT, bg=ModernStyle.BG_DARK).pack(pady=15)
        
        # Модель
        model_frame = tk.Frame(dialog, bg=ModernStyle.BG_DARK)
        model_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(model_frame, text="Модель:",
                font=ModernStyle.FONT_TEXT,
                fg=ModernStyle.FG_TEXT, bg=ModernStyle.BG_DARK).pack(side=tk.LEFT)
        
        model_var = tk.StringVar(value=self.model_var.get())
        model_combo = ttk.Combobox(model_frame, textvariable=model_var,
                                   values=["SWE-1", "GPT-5.1-Codex", "Grok Code Fast 1"],
                                   font=ModernStyle.FONT_TEXT, width=20)
        model_combo.pack(side=tk.LEFT, padx=10)
        
        # Промпт
        tk.Label(dialog, text="Промпт:",
                font=ModernStyle.FONT_TEXT,
                fg=ModernStyle.FG_TEXT, bg=ModernStyle.BG_DARK).pack(anchor=tk.W, padx=20, pady=(10, 5))
        
        prompt_entry = tk.Text(dialog, height=6,
                              font=ModernStyle.FONT_TEXT,
                              bg=ModernStyle.BG_CARD, fg=ModernStyle.FG_TEXT,
                              insertbackground=ModernStyle.FG_TEXT)
        prompt_entry.pack(fill=tk.X, padx=20, pady=5)
        
        def execute():
            prompt = prompt_entry.get("1.0", tk.END).strip()
            model = model_var.get()
            
            if not prompt:
                messagebox.showerror("Ошибка", "Введите промпт")
                return
            
            dialog.destroy()
            
            def run():
                self.wa.run_task(prompt, model, close_after=False)
                self.root.after(0, self.refresh_windows)
            
            threading.Thread(target=run, daemon=True).start()
        
        btn = self.create_button(dialog, "🚀 Выполнить", execute, ModernStyle.BG_SUCCESS)
        btn.pack(pady=15)
    
    def run_all_tasks(self):
        """Запустить все pending задачи"""
        with open(self.tasks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        pending_tasks = [t for t in data.get('tasks', []) if t['status'] == 'pending']
        
        if not pending_tasks:
            messagebox.showinfo("Информация", "Нет задач для выполнения")
            return
        
        if not messagebox.askyesno("Подтверждение", 
                                   f"Запустить {len(pending_tasks)} задач?\n\n" +
                                   "Задачи будут выполняться последовательно."):
            return
        
        self.log(f"🔄 Запуск очереди из {len(pending_tasks)} задач")
        
        def run():
            results = self.wa.run_tasks_queue(pending_tasks, delay_between=3)
            
            # Обновляем статусы
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for result in results['results']:
                if result['success']:
                    task_id = result['task']['id']
                    for t in data['tasks']:
                        if t['id'] == task_id:
                            t['status'] = 'in_progress'
            
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.root.after(0, self.load_tasks)
            self.root.after(0, self.refresh_windows)
            
            self.root.after(0, lambda: messagebox.showinfo(
                "Готово",
                f"Выполнено: {results['completed']}\nОшибок: {results['failed']}"
            ))
        
        threading.Thread(target=run, daemon=True).start()
    
    def run_test(self):
        """Запустить автоматический тест (tests/auto_test.py)"""
        self.log("🧪 Запускаю тест...")
        logger.debug("Starting auto_test.py")  # DEBUG уровень для детальной информации
        
        def run():
            try:
                self.update_progress(25)
                test_path = os.path.join(os.path.dirname(__file__), 'tests', 'auto_test.py')
                
                if not os.path.exists(test_path):
                    self.log("❌ Файл теста не найден: tests/auto_test.py")
                    logger.error(f"Test file not found: {test_path}")
                    return
                
                self.update_progress(50)
                logger.debug(f"Running test: {test_path}")
                
                # Запускаем тест в отдельном процессе
                process = subprocess.Popen(
                    ['python', test_path],
                    cwd=os.path.dirname(__file__),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                self.update_progress(75)
                stdout, stderr = process.communicate(timeout=60)
                
                if process.returncode == 0:
                    self.log("✅ Тест завершён успешно")
                    logger.info("Test completed successfully")
                    self.play_sound()
                else:
                    self.log(f"❌ Тест завершён с ошибкой (код {process.returncode})")
                    logger.error(f"Test failed with code {process.returncode}")
                    if stderr:
                        logger.debug(f"Test stderr: {stderr[:500]}")
                
                self.update_progress(100)
                
            except subprocess.TimeoutExpired:
                self.log("⏱️ Тест превысил время ожидания (60 сек)")
                logger.warning("Test timeout after 60 seconds")
            except Exception as e:
                self.log(f"❌ Ошибка запуска теста: {e}")
                logger.exception("Test execution error")
            finally:
                self.root.after(1000, lambda: self.update_progress(0))
        
        threading.Thread(target=run, daemon=True).start()
    
    def update_progress(self, value):
        """Обновить прогресс-бар (thread-safe)"""
        def update():
            self.progress_var.set(value)
        self.root.after(0, update)
    
    def play_sound(self):
        """Воспроизвести звук завершения"""
        if self.sound_var.get():
            try:
                winsound.Beep(1000, 300)  # 1000 Hz, 300 ms
                winsound.Beep(1500, 200)  # 1500 Hz, 200 ms
                logger.debug("Sound notification played")
            except Exception as e:
                logger.debug(f"Sound error: {e}")
    
    def add_to_history(self, task_title):
        """Добавить задачу в историю"""
        timestamp = time.strftime("%H:%M")
        self.history_listbox.insert(0, f"[{timestamp}] {task_title}")
        # Ограничиваем историю 20 записями
        while self.history_listbox.size() > 20:
            self.history_listbox.delete(tk.END)
        logger.debug(f"Added to history: {task_title}")
    
    def clear_history(self):
        """Очистить историю"""
        self.history_listbox.delete(0, tk.END)
        self.log("📜 История очищена")
    
    def run_boss(self):
        """Запустить Boss для управления рабочими GPT"""
        self.log("👔 Запускаю Boss...")
        
        def run():
            try:
                boss_path = os.path.join(os.path.dirname(__file__), 'boss.py')
                process = subprocess.Popen(
                    ['python', boss_path],
                    cwd=os.path.dirname(__file__),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate(timeout=120)
                
                if stdout:
                    for line in stdout.strip().split('\n')[-5:]:  # Последние 5 строк
                        self.log(f"   {line}")
                
                if process.returncode == 0:
                    self.log("✅ Boss завершил работу")
                    self.play_sound()
                else:
                    self.log(f"⚠️ Boss завершился с кодом {process.returncode}")
                    
            except subprocess.TimeoutExpired:
                self.log("⏱️ Boss превысил время ожидания")
            except Exception as e:
                self.log(f"❌ Ошибка Boss: {e}")
        
        threading.Thread(target=run, daemon=True).start()
    
    def check_boss_results(self):
        """Проверить результаты работы Boss через git diff"""
        self.log("🔍 Проверяю изменения в git...")
        
        try:
            result = subprocess.run(
                ['git', 'diff', '--stat'],
                cwd=os.path.dirname(__file__),
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                self.log("📝 Изменения:")
                for line in result.stdout.strip().split('\n'):
                    self.log(f"   {line}")
            else:
                self.log("   Нет изменений в файлах")
                
        except Exception as e:
            self.log(f"❌ Ошибка проверки: {e}")
    
    def delete_selected_task(self):
        """Удалить выбранную задачу"""
        selection = self.tasks_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите задачу")
            return
        
        text = self.tasks_listbox.get(selection[0])
        try:
            task_id = int(text.split('[')[1].split(']')[0])
        except:
            return
        
        if not messagebox.askyesno("Подтверждение", f"Удалить задачу #{task_id}?"):
            return
        
        with open(self.tasks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data['tasks'] = [t for t in data['tasks'] if t['id'] != task_id]
        
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.load_tasks()
        self.log(f"🗑️ Задача #{task_id} удалена")
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()


if __name__ == "__main__":
    # Включаем поддержку ANSI цветов в Windows
    os.system('')
    app = WindsurfAutomationGUI()
    app.run()
