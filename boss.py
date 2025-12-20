"""
WA Boss - Система управления рабочими GPT
Я (Claude в этом окне) - босс. Рабочие (GPT в других окнах) - исполнители.

Архитектура:
- Boss (это окно) - планирует задачи, проверяет результаты, итерирует
- Workers (другие окна) - выполняют задачи через бесплатные GPT модели

Использование:
1. Открой несколько окон Windsurf с проектом WA
2. Запусти: python boss.py
3. Boss отправит задачи рабочим и будет проверять результаты
"""

import sys
import os
import time
import subprocess
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from windsurf_automation import find_windsurf_windows, activate_window_by_hwnd, get_window_rect
import keyboard
import pyperclip

# Путь к проекту
PROJECT_PATH = r"C:\Users\bnex4\CascadeProjects\Windsurf-Automation"

# Модель для рабочих
WORKER_MODEL = "GPT-5.1-Codex"

# Задачи для улучшения WA (разбиты на маленькие части)
IMPROVEMENT_TASKS = [
    {
        "id": 1,
        "title": "Кнопка теста в GUI",
        "file": "gui.py",
        "prompt": """В файле gui.py найди класс или функцию с кнопками и добавь новую кнопку "🧪 Тест".
При нажатии она должна запускать subprocess.Popen(['python', 'tests/auto_test.py']).
Комментарии на русском. Изменяй ТОЛЬКО gui.py."""
    },
    {
        "id": 2, 
        "title": "Прогресс-бар в GUI",
        "file": "gui.py",
        "prompt": """В файле gui.py добавь ttk.Progressbar для отображения прогресса.
Прогресс должен обновляться методом update_progress(value) где value от 0 до 100.
Комментарии на русском. Изменяй ТОЛЬКО gui.py."""
    },
    {
        "id": 3,
        "title": "Звуковое уведомление",
        "file": "gui.py", 
        "prompt": """В файле gui.py добавь звуковое уведомление при завершении задачи.
Используй winsound.Beep(1000, 500). Добавь чекбокс для включения/выключения звука.
Комментарии на русском. Изменяй ТОЛЬКО gui.py."""
    },
    {
        "id": 4,
        "title": "Конфиг файл",
        "file": "config.json",
        "prompt": """Создай файл config.json с настройками:
{
  "model": "GPT-5.1-Codex",
  "delay": 2,
  "sound_enabled": true,
  "auto_commit": false
}
Создай ТОЛЬКО файл config.json."""
    },
    {
        "id": 5,
        "title": "Загрузка конфига",
        "file": "src/config.py",
        "prompt": """Создай файл src/config.py с функциями:
- load_config() -> dict - загружает config.json
- save_config(config: dict) - сохраняет config.json
- get_setting(key: str, default=None) - получает настройку
Комментарии на русском."""
    }
]


class Boss:
    """Босс - управляет рабочими GPT"""
    
    def __init__(self):
        self.workers = []  # [(hwnd, title, task_id), ...]
        self.completed_tasks = []
        self.failed_tasks = []
        self.my_hwnd = None  # Окно босса (это окно)
        
    def find_my_window(self):
        """Найти окно босса (первое окно с проектом)"""
        windows = find_windsurf_windows(ide_only=False)
        for h, t in windows:
            if "Windsurf" in t and ("CascadeProjects" in t or "GITHUB" in t):
                self.my_hwnd = h
                print(f"👔 Моё окно (Boss): {t[:40]}...")
                return True
        return False
    
    def find_worker_windows(self):
        """Найти окна рабочих (все кроме моего)"""
        windows = find_windsurf_windows(ide_only=False)
        worker_windows = []
        
        for h, t in windows:
            # Пропускаем браузерные окна
            if "Яндекс" in t or "Подписка" in t or "Usage" in t:
                continue
            # Пропускаем моё окно
            if h == self.my_hwnd:
                continue
            # Это рабочее окно
            worker_windows.append((h, t))
        
        return worker_windows
    
    def send_task_to_worker(self, hwnd, task):
        """Отправить задачу рабочему"""
        print(f"\n📤 Отправляю задачу #{task['id']} в окно {hwnd}...")
        
        # Активируем окно рабочего
        activate_window_by_hwnd(hwnd)
        time.sleep(0.5)
        
        # Ctrl+L - открыть Cascade
        keyboard.send('ctrl+l')
        time.sleep(1.5)
        
        # Ctrl+/ - выбор модели
        keyboard.send('ctrl+/')
        time.sleep(0.8)
        pyperclip.copy(WORKER_MODEL)
        keyboard.send('ctrl+v')
        time.sleep(0.3)
        keyboard.send('enter')
        time.sleep(0.5)
        
        # Формируем промпт
        prompt = f"""Проект: {PROJECT_PATH}

{task['prompt']}

После выполнения напиши:
## Готово
- что сделал

## Проблемы  
- если были"""
        
        # Вставляем задачу
        pyperclip.copy(prompt)
        keyboard.send('ctrl+v')
        time.sleep(0.3)
        
        # Enter - отправить
        keyboard.send('enter')
        time.sleep(0.5)
        
        print(f"   ✅ Задача отправлена!")
        return True
    
    def check_git_changes(self):
        """Проверить изменения в git"""
        result = subprocess.run(
            ["git", "diff", "--stat"],
            cwd=PROJECT_PATH,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    
    def commit_changes(self, message):
        """Закоммитить изменения"""
        subprocess.run(["git", "add", "-A"], cwd=PROJECT_PATH)
        subprocess.run(["git", "commit", "-m", message], cwd=PROJECT_PATH)
        print(f"📝 Коммит: {message}")
    
    def run(self, num_tasks=3):
        """Запустить босса"""
        print("=" * 60)
        print("👔 WA BOSS - УПРАВЛЕНИЕ РАБОЧИМИ GPT")
        print("=" * 60)
        
        # Находим своё окно
        if not self.find_my_window():
            print("❌ Не могу найти своё окно!")
            return
        
        # Находим рабочих
        workers = self.find_worker_windows()
        print(f"\n🔧 Найдено рабочих: {len(workers)}")
        for h, t in workers:
            print(f"   [{h}] {t[:40]}...")
        
        if not workers:
            print("\n❌ Нет рабочих окон!")
            print("   Открой ещё окна Windsurf с проектом WA:")
            print("   File -> New Window, затем File -> Open Folder")
            return
        
        # Распределяем задачи
        tasks_to_run = IMPROVEMENT_TASKS[:min(num_tasks, len(workers))]
        
        print(f"\n📋 Задачи для выполнения: {len(tasks_to_run)}")
        for task in tasks_to_run:
            print(f"   #{task['id']}: {task['title']}")
        
        print("\n⚠️ Через 3 сек начну отправлять задачи!")
        time.sleep(3)
        
        # Отправляем задачи рабочим
        for i, (hwnd, title) in enumerate(workers[:len(tasks_to_run)]):
            task = tasks_to_run[i]
            print(f"\n{'='*40}")
            print(f"🔧 Рабочий #{i+1}: {title[:30]}...")
            print(f"📌 Задача: {task['title']}")
            
            self.send_task_to_worker(hwnd, task)
            self.workers.append((hwnd, title, task['id']))
            time.sleep(1)
        
        # Возвращаем фокус боссу
        print(f"\n   Возвращаю фокус боссу...")
        activate_window_by_hwnd(self.my_hwnd)
        
        print("\n" + "=" * 60)
        print(f"✅ Задачи отправлены {len(self.workers)} рабочим!")
        print("=" * 60)
        print("\n🔍 Рабочие выполняют задачи...")
        print("   Проверяй изменения: git diff")
        print("   Или запусти: python boss.py --check")
        
        # Сохраняем состояние
        self.save_state()
    
    def save_state(self):
        """Сохранить состояние босса"""
        state = {
            "timestamp": datetime.now().isoformat(),
            "workers": [(h, t, tid) for h, t, tid in self.workers],
            "completed": self.completed_tasks,
            "failed": self.failed_tasks
        }
        with open(os.path.join(PROJECT_PATH, "boss_state.json"), "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def check_results(self):
        """Проверить результаты работы"""
        print("=" * 60)
        print("🔍 ПРОВЕРКА РЕЗУЛЬТАТОВ")
        print("=" * 60)
        
        changes = self.check_git_changes()
        if changes:
            print("\n📝 Изменения в git:")
            print(changes)
            
            # Спрашиваем про коммит
            print("\n   Закоммитить? (y/n)")
        else:
            print("\n   Нет изменений в файлах.")
            print("   Рабочие ещё работают или не внесли изменения.")


def main():
    boss = Boss()
    
    if "--check" in sys.argv:
        boss.check_results()
    elif "--tasks" in sys.argv:
        # Показать все задачи
        print("📋 Доступные задачи:")
        for task in IMPROVEMENT_TASKS:
            print(f"   #{task['id']}: {task['title']} ({task['file']})")
    else:
        # Запуск с количеством задач
        try:
            idx = sys.argv.index("-n") if "-n" in sys.argv else -1
            num = int(sys.argv[idx + 1]) if idx >= 0 else 3
        except:
            num = 3
        boss.run(num_tasks=num)


if __name__ == "__main__":
    main()
