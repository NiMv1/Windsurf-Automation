"""
Windsurf Automation - Самоулучшение
Запускает задачи улучшения WA через бесплатные ИИ в отдельном окне Windsurf
"""

import sys
import os
import time
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from windsurf_automation import (
    WindsurfAutomation, 
    find_windsurf_windows, 
    activate_window_by_hwnd,
    get_window_rect
)
import pyautogui
import pyperclip
import keyboard

# Путь к проекту WA
WA_PROJECT = r"C:\Users\bnex4\CascadeProjects\Windsurf-Automation"

# Задачи для самоулучшения (5 разных задач для 5 окон)
IMPROVEMENT_TASKS = [
    {
        "id": 1,
        "title": "Кнопка запуска теста",
        "prompt": """Проект: C:\\Users\\bnex4\\CascadeProjects\\Windsurf-Automation

ЗАДАЧА: В gui.py добавь кнопку "🧪 Тест" после кнопки "Новое окно + Промпт".
Кнопка запускает tests/auto_test.py через subprocess.Popen.

ТРЕБОВАНИЯ: Изменяй ТОЛЬКО gui.py. Комментарии на русском.

ОТЧЁТ в конце: ## Сделано / ## Проблемы""",
        "model": "GPT-5.1-Codex"
    },
    {
        "id": 2,
        "title": "Прогресс-бар",
        "prompt": """Проект: C:\\Users\\bnex4\\CascadeProjects\\Windsurf-Automation

ЗАДАЧА: В gui.py добавь ttk.Progressbar который показывает прогресс задачи.
Прогресс обновляется при каждом шаге (0%, 25%, 50%, 75%, 100%).

ТРЕБОВАНИЯ: Изменяй ТОЛЬКО gui.py. Комментарии на русском.

ОТЧЁТ в конце: ## Сделано / ## Проблемы""",
        "model": "GPT-5.1-Codex"
    },
    {
        "id": 3,
        "title": "Звуковое уведомление",
        "prompt": """Проект: C:\\Users\\bnex4\\CascadeProjects\\Windsurf-Automation

ЗАДАЧА: В gui.py добавь звук при завершении задачи (winsound.Beep).
Добавь чекбокс "🔊 Звук" для включения/выключения.

ТРЕБОВАНИЯ: Изменяй ТОЛЬКО gui.py. Используй winsound. Комментарии на русском.

ОТЧЁТ в конце: ## Сделано / ## Проблемы""",
        "model": "GPT-5.1-Codex"
    },
    {
        "id": 4,
        "title": "Настройки в JSON",
        "prompt": """Проект: C:\\Users\\bnex4\\CascadeProjects\\Windsurf-Automation

ЗАДАЧА: Создай config.json с настройками (delay, model, sound).
Создай src/config.py для загрузки/сохранения. Интегрируй в gui.py.

ТРЕБОВАНИЯ: Создай config.json и src/config.py. Комментарии на русском.

ОТЧЁТ в конце: ## Сделано / ## Проблемы""",
        "model": "GPT-5.1-Codex"
    },
    {
        "id": 5,
        "title": "История задач",
        "prompt": """Проект: C:\\Users\\bnex4\\CascadeProjects\\Windsurf-Automation

ЗАДАЧА: В gui.py добавь вкладку "История" с listbox выполненных задач.
Сохраняй историю в tasks/history.json.

ТРЕБОВАНИЯ: Изменяй gui.py, создай tasks/history.json. Комментарии на русском.

ОТЧЁТ в конце: ## Сделано / ## Проблемы""",
        "model": "GPT-5.1-Codex"
    }
]


def open_new_windsurf_window():
    """Открыть НОВОЕ окно Windsurf с проектом WA (не трогая текущее!)"""
    print("1️⃣ Открываю НОВОЕ окно Windsurf...")
    print("   ⚠️ Твоё текущее окно НЕ будет затронуто!")
    
    # Запоминаем ВСЕ текущие окна (их hwnd)
    windows_before = find_windsurf_windows(ide_only=False)  # Все окна, не только IDE
    old_hwnds = {w[0] for w in windows_before}
    print(f"   Окон Windsurf до: {len(windows_before)}")
    
    # Запускаем НОВЫЙ экземпляр Windsurf
    windsurf_path = r"C:\Users\bnex4\AppData\Local\Programs\windsurf\Windsurf.exe"
    
    # Используем start для запуска в отдельном процессе
    subprocess.Popen(
        f'start "" "{windsurf_path}" --new-window "{WA_PROJECT}"',
        shell=True
    )
    
    print("   Ждём появления НОВОГО окна (10 сек)...")
    
    # Ждём появления нового окна (до 10 секунд)
    for i in range(20):
        time.sleep(0.5)
        windows_after = find_windsurf_windows(ide_only=False)
        
        # Ищем окно которого НЕ БЫЛО раньше
        for hwnd, title in windows_after:
            if hwnd not in old_hwnds:
                print(f"✅ НОВОЕ окно найдено: [{hwnd}] {title[:40]}...")
                time.sleep(2)  # Даём окну загрузиться
                return hwnd, title
    
    print("❌ Новое окно не появилось за 10 секунд")
    print("   Попробуй открыть Windsurf вручную с проектом WA")
    return None, None


def select_model(hwnd, model_name="GPT-5.1-Codex"):
    """Выбрать модель через Ctrl+/ и поиск"""
    print(f"   Выбираю модель: {model_name}...")
    
    # Ctrl+/ открывает Model Selector
    keyboard.send('ctrl+/')
    time.sleep(1)
    
    # Вводим название модели для поиска
    pyperclip.copy(model_name)
    keyboard.send('ctrl+v')
    time.sleep(0.5)
    
    # Enter для выбора
    keyboard.send('enter')
    time.sleep(0.5)
    
    print(f"   ✅ Модель {model_name} выбрана")


def send_task_to_window(hwnd, prompt, model="GPT-5.1-Codex"):
    """Отправить задачу в указанное окно Windsurf (только hotkeys, без кликов)"""
    print(f"\n2️⃣ Отправляю задачу в окно {hwnd}...")
    
    # Активируем окно
    activate_window_by_hwnd(hwnd)
    time.sleep(1)
    
    # Ctrl+L открывает Cascade и ставит фокус в поле ввода
    print("   Ctrl+L (открыть Cascade + фокус)...")
    keyboard.send('ctrl+l')
    time.sleep(2)
    
    # Выбираем модель через Ctrl+/
    select_model(hwnd, model)
    time.sleep(0.5)
    
    # Вставляем промпт через clipboard
    print("   Вставляю промпт (Ctrl+V)...")
    pyperclip.copy(prompt)
    keyboard.send('ctrl+v')
    time.sleep(0.5)
    
    # Отправляем Enter
    print("   Отправляю (Enter)...")
    keyboard.send('enter')
    time.sleep(1)
    
    print(f"✅ Задача отправлена с моделью {model}!")
    
    return True


def check_git_changes():
    """Проверить изменения через git"""
    print("\n📊 Проверяю изменения в git...")
    
    result = subprocess.run(
        ["git", "diff", "--stat"],
        cwd=WA_PROJECT,
        capture_output=True,
        text=True
    )
    
    if result.stdout.strip():
        print("📝 Изменённые файлы:")
        print(result.stdout)
        return True
    else:
        print("   Нет изменений")
        return False


def open_worker_window():
    """Открыть рабочее окно через текущее окно пользователя"""
    windows = find_windsurf_windows(ide_only=True)
    if not windows:
        print("❌ Windsurf не найден")
        return None, None
    
    # Запоминаем текущее окно пользователя
    user_hwnd, user_title = windows[0]
    old_hwnds = {w[0] for w in windows}
    print(f"   Твоё окно: {user_title[:40]}...")
    print(f"   Окон до: {len(windows)}")
    
    # Активируем окно пользователя и открываем новое через Ctrl+Shift+N
    print("   Открываю новое окно через Ctrl+Shift+N...")
    activate_window_by_hwnd(user_hwnd)
    time.sleep(0.5)
    keyboard.send('ctrl+shift+n')
    time.sleep(4)
    
    # Ищем новое окно
    windows_after = find_windsurf_windows(ide_only=False)
    print(f"   Окон после: {len(windows_after)}")
    
    for hwnd, title in windows_after:
        if hwnd not in old_hwnds:
            print(f"✅ Новое окно: [{hwnd}] {title[:40]}...")
            
            # Открываем проект WA через Ctrl+O (Open Folder)
            print("   Открываю проект WA (Ctrl+O)...")
            activate_window_by_hwnd(hwnd)
            time.sleep(1)
            
            # Ctrl+O = Open Folder в Windsurf
            keyboard.send('ctrl+o')
            time.sleep(1.5)
            
            # В диалоге: Alt+D = адресная строка, вставляем путь
            keyboard.send('alt+d')
            time.sleep(0.3)
            pyperclip.copy(WA_PROJECT)
            keyboard.send('ctrl+v')
            time.sleep(0.3)
            keyboard.send('enter')
            time.sleep(1)
            
            # Enter для Select Folder
            keyboard.send('enter')
            time.sleep(2)
            
            # Enter для Trust authors
            keyboard.send('enter')
            time.sleep(2)
            
            # Возвращаем фокус пользователю
            print("   Возвращаю фокус в твоё окно...")
            activate_window_by_hwnd(user_hwnd)
            
            return hwnd, title
    
    print("❌ Новое окно не появилось")
    return None, None


def run_multiple_workers(num_workers=5):
    """Запустить несколько рабочих окон с разными задачами"""
    print("=" * 60)
    print(f"🤖 ЗАПУСК {num_workers} РАБОЧИХ ОКОН")
    print("=" * 60)
    
    workers = []  # [(hwnd, task), ...]
    
    for i in range(min(num_workers, len(IMPROVEMENT_TASKS))):
        task = IMPROVEMENT_TASKS[i]
        print(f"\n{'='*40}")
        print(f"🔧 Рабочий #{i+1}: {task['title']}")
        print(f"{'='*40}")
        
        # Открываем новое окно
        hwnd, title = open_worker_window()
        
        if hwnd:
            # Отправляем задачу
            time.sleep(1)
            send_task_to_window(hwnd, task['prompt'], task['model'])
            workers.append((hwnd, task))
            print(f"✅ Рабочий #{i+1} запущен!")
        else:
            print(f"❌ Не удалось запустить рабочего #{i+1}")
        
        time.sleep(2)  # Пауза между запусками
    
    print("\n" + "=" * 60)
    print(f"✅ Запущено {len(workers)} рабочих окон!")
    print("=" * 60)
    print("\n⚠️ В КАЖДОМ окне выбери модель GPT-5.1-Codex!")
    print("\nРабочие:")
    for i, (hwnd, task) in enumerate(workers):
        print(f"   #{i+1} [{hwnd}] {task['title']}")
    
    return workers


def main():
    print("=" * 60)
    print("🤖 WINDSURF AUTOMATION - САМОУЛУЧШЕНИЕ")
    print("=" * 60)
    print(f"Проект: {WA_PROJECT}")
    print(f"Задач: {len(IMPROVEMENT_TASKS)}")
    
    # Проверяем аргументы
    if "--workers" in sys.argv or "-w" in sys.argv:
        # Запуск нескольких рабочих
        try:
            idx = sys.argv.index("--workers") if "--workers" in sys.argv else sys.argv.index("-w")
            num = int(sys.argv[idx + 1])
        except:
            num = 5
        run_multiple_workers(num)
        return
    
    print("\n1️⃣ Открываю новое окно через твоё...")
    
    # Открываем рабочее окно
    hwnd, title = open_worker_window()
    
    if not hwnd:
        return
    
    # Отправляем первую задачу
    task = IMPROVEMENT_TASKS[0]
    print(f"\n📌 Задача: {task['title']}")
    
    send_task_to_window(hwnd, task['prompt'], task['model'])
    
    print("\n" + "=" * 60)
    print("✅ Задача отправлена!")
    print("=" * 60)
    print("\nКоманды:")
    print("   python self_improve.py --workers 5  # Запустить 5 рабочих")
    print("   python self_improve.py --check      # Проверить изменения")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check_git_changes()
    else:
        main()
