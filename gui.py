"""
Windsurf Automation - Современный GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import os
import json
import time
import threading

# Добавляем путь к src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from windsurf_automation import WindsurfAutomation, find_windsurf_windows


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
        self.root.title("Windsurf Automation v0.3.0")
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
        
        self.setup_ui()
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
        
        version = tk.Label(header, text="v0.3.0", 
                          font=ModernStyle.FONT_SUBTITLE,
                          fg=ModernStyle.FG_MUTED, bg=ModernStyle.BG_DARK)
        version.pack(side=tk.LEFT, padx=10)
        
        # Предупреждение
        warning_frame = tk.Frame(main_frame, bg=ModernStyle.BG_WARNING, padx=10, pady=8)
        warning_frame.pack(fill=tk.X, pady=(0, 15))
        
        warning_text = tk.Label(warning_frame, 
                               text="⚠️ Ручной выбор модели: После открытия окна выберите FREE модель (SWE-1, GPT-5.1-Codex, Grok)",
                               font=ModernStyle.FONT_TEXT,
                               fg="#000000", bg=ModernStyle.BG_WARNING,
                               wraplength=700)
        warning_text.pack()
        
        # Основной контент - две колонки
        content = tk.Frame(main_frame, bg=ModernStyle.BG_DARK)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Левая колонка - Действия
        left_col = tk.Frame(content, bg=ModernStyle.BG_DARK, width=350)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Карточка "Быстрые действия"
        actions_card = self.create_card(left_col, "⚡ Быстрые действия")
        
        self.btn_quick = self.create_button(actions_card, "🚀 Открыть окно + Sidebar", 
                                           self.quick_run, ModernStyle.BG_PRIMARY)
        self.btn_quick.pack(fill=tk.X, pady=5)
        
        self.btn_sidebar = self.create_button(actions_card, "📋 Открыть Sidebar", 
                                             self.open_sidebar, ModernStyle.BG_BUTTON)
        self.btn_sidebar.pack(fill=tk.X, pady=5)
        
        self.btn_send = self.create_button(actions_card, "💬 Отправить сообщение", 
                                          self.send_message_dialog, ModernStyle.BG_BUTTON)
        self.btn_send.pack(fill=tk.X, pady=5)
        
        # Карточка "Окна Windsurf"
        windows_card = self.create_card(left_col, "🪟 Окна Windsurf")
        
        self.windows_listbox = tk.Listbox(windows_card, 
                                          font=ModernStyle.FONT_MONO,
                                          bg=ModernStyle.BG_DARK,
                                          fg=ModernStyle.FG_TEXT,
                                          selectbackground=ModernStyle.BG_PRIMARY,
                                          height=5,
                                          borderwidth=0,
                                          highlightthickness=1,
                                          highlightbackground=ModernStyle.BG_BUTTON)
        self.windows_listbox.pack(fill=tk.X, pady=5)
        self.windows_listbox.bind('<<ListboxSelect>>', self.on_window_select)
        
        btn_refresh = self.create_button(windows_card, "🔄 Обновить", 
                                        self.refresh_windows, ModernStyle.BG_BUTTON)
        btn_refresh.pack(fill=tk.X, pady=5)
        
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
        
        self.log("Windsurf Automation запущен")
    
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
    
    def log(self, message):
        """Добавить сообщение в лог"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
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
        else:
            self.windows_listbox.insert(tk.END, "Нет открытых окон")
            self.log("⚠️ Окна Windsurf не найдены")
    
    def on_window_select(self, event):
        """Обработка выбора окна"""
        selection = self.windows_listbox.curselection()
        if selection:
            windows = find_windsurf_windows(ide_only=True)
            if selection[0] < len(windows):
                self.wa.hwnd, self.wa.title = windows[selection[0]]
                self.log(f"Выбрано окно: {self.wa.title[:40]}...")
    
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
    
    def quick_run(self):
        """Быстрый запуск - новое окно + sidebar"""
        def run():
            self.log("🚀 Открываю новое окно...")
            self.btn_quick.configure(state=tk.DISABLED)
            
            if self.wa.open_new_window():
                self.log("✅ Окно открыто")
                time.sleep(1)
                
                self.log("📋 Открываю sidebar...")
                if self.wa.open_sidebar():
                    self.log("✅ Sidebar открыт")
                    self.log("⚠️ Выберите модель вручную!")
                else:
                    self.log("❌ Не удалось открыть sidebar")
            else:
                self.log("❌ Не удалось открыть окно")
            
            self.btn_quick.configure(state=tk.NORMAL)
            self.refresh_windows()
        
        threading.Thread(target=run, daemon=True).start()
    
    def open_sidebar(self):
        """Открыть sidebar"""
        def run():
            self.log("📋 Открываю sidebar...")
            if self.wa.open_sidebar():
                self.log("✅ Sidebar открыт")
            else:
                self.log("❌ Не удалось открыть sidebar")
        
        threading.Thread(target=run, daemon=True).start()
    
    def send_message_dialog(self):
        """Диалог отправки сообщения"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Отправить сообщение")
        dialog.geometry("500x200")
        dialog.configure(bg=ModernStyle.BG_DARK)
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Введите сообщение:",
                font=ModernStyle.FONT_TEXT,
                fg=ModernStyle.FG_TEXT, bg=ModernStyle.BG_DARK).pack(pady=10)
        
        text_entry = tk.Text(dialog, height=4,
                            font=ModernStyle.FONT_TEXT,
                            bg=ModernStyle.BG_CARD,
                            fg=ModernStyle.FG_TEXT,
                            insertbackground=ModernStyle.FG_TEXT)
        text_entry.pack(fill=tk.X, padx=20, pady=10)
        
        def send():
            message = text_entry.get("1.0", tk.END).strip()
            if message:
                dialog.destroy()
                self.log(f"💬 Отправляю: {message[:50]}...")
                
                def run():
                    if self.wa.send_message(message):
                        self.log("✅ Сообщение отправлено")
                    else:
                        self.log("❌ Не удалось отправить")
                
                threading.Thread(target=run, daemon=True).start()
        
        btn = self.create_button(dialog, "📤 Отправить", send, ModernStyle.BG_PRIMARY)
        btn.pack(pady=10)
    
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
        """Выполнить выбранную задачу"""
        selection = self.tasks_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите задачу")
            return
        
        # Получить ID задачи из текста
        text = self.tasks_listbox.get(selection[0])
        # Формат: "📌 [1] Название (Модель)"
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
            # Открыть окно
            self.log("1️⃣ Открываю окно...")
            if not self.wa.open_new_window():
                self.log("❌ Не удалось открыть окно")
                return
            
            time.sleep(1)
            
            # Открыть sidebar
            self.log("2️⃣ Открываю sidebar...")
            if not self.wa.open_sidebar():
                self.log("❌ Не удалось открыть sidebar")
                return
            
            time.sleep(0.5)
            
            # Показать напоминание о модели
            self.root.after(0, lambda: messagebox.showinfo(
                "Выберите модель",
                f"Выберите модель: {task['model']}\n\nПосле выбора нажмите OK"
            ))
            
            # Отправить промпт
            self.log("3️⃣ Отправляю промпт...")
            if self.wa.send_message(task['prompt']):
                self.log("✅ Задача отправлена!")
                
                # Обновить статус
                for t in data['tasks']:
                    if t['id'] == task_id:
                        t['status'] = 'in_progress'
                
                with open(self.tasks_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                self.root.after(0, self.load_tasks)
            else:
                self.log("❌ Не удалось отправить промпт")
            
            self.root.after(0, self.refresh_windows)
        
        threading.Thread(target=run, daemon=True).start()
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()


if __name__ == "__main__":
    app = WindsurfAutomationGUI()
    app.run()
