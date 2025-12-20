"""
Найм рабочих для улучшения WA
Работает с УЖЕ ОТКРЫТЫМИ окнами Windsurf (не открывает новые)
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from windsurf_automation import find_windsurf_windows, activate_window_by_hwnd
import keyboard
import pyperclip

# Задачи для рабочих
TASKS = [
    "В gui.py добавь кнопку 'Тест' которая запускает tests/auto_test.py через subprocess.Popen. Комментарии на русском.",
    "В gui.py добавь ttk.Progressbar для отображения прогресса задачи. Комментарии на русском.",
    "В gui.py добавь звуковое уведомление (winsound.Beep) при завершении задачи. Комментарии на русском.",
    "Создай config.json с настройками (delay, model) и src/config.py для загрузки. Комментарии на русском.",
    "В gui.py добавь вкладку История с listbox выполненных задач. Комментарии на русском.",
]


def send_task(hwnd, task_text, model="GPT-5.1-Codex"):
    """Отправить задачу в окно"""
    print(f"   Активирую окно {hwnd}...")
    activate_window_by_hwnd(hwnd)
    time.sleep(0.5)
    
    # Ctrl+L - открыть Cascade
    print("   Ctrl+L...")
    keyboard.send('ctrl+l')
    time.sleep(1.5)
    
    # Ctrl+/ - выбор модели
    print(f"   Выбираю модель {model}...")
    keyboard.send('ctrl+/')
    time.sleep(0.8)
    pyperclip.copy(model)
    keyboard.send('ctrl+v')
    time.sleep(0.3)
    keyboard.send('enter')
    time.sleep(0.5)
    
    # Вставляем задачу
    print("   Вставляю задачу...")
    pyperclip.copy(task_text)
    keyboard.send('ctrl+v')
    time.sleep(0.3)
    
    # Enter
    print("   Отправляю...")
    keyboard.send('enter')
    time.sleep(0.5)
    
    print("   ✅ Готово!")


def main():
    print("=" * 50)
    print("🤖 НАЙМ РАБОЧИХ ДЛЯ УЛУЧШЕНИЯ WA")
    print("=" * 50)
    
    # Находим все окна Windsurf (включая не-IDE)
    all_windows = find_windsurf_windows(ide_only=False)
    
    # Фильтруем только IDE окна (не браузер)
    wa_windows = []
    for h, t in all_windows:
        # Пропускаем браузерные окна
        if "Яндекс" in t or "Chrome" in t or "Подписка" in t or "Usage" in t:
            continue
        wa_windows.append((h, t))
    
    print(f"\n📋 Найдено {len(wa_windows)} окон с проектом WA:")
    for i, (h, t) in enumerate(wa_windows):
        print(f"   [{i}] {t[:50]}...")
    
    if len(wa_windows) < 2:
        print("\n❌ Нужно минимум 2 окна с проектом WA!")
        print("   1. Твоё рабочее окно (не трогаем)")
        print("   2+ Рабочие окна для задач")
        print("\n   Открой ещё окна Windsurf с проектом WA:")
        print("   File -> New Window, затем File -> Open Folder")
        return
    
    # Первое окно - рабочее пользователя, остальные - для задач
    user_hwnd = wa_windows[0][0]
    worker_windows = wa_windows[1:]
    
    print(f"\n👤 Твоё окно: {wa_windows[0][1][:40]}...")
    print(f"🔧 Рабочих окон: {len(worker_windows)}")
    
    print("\n⚠️ Через 3 сек начну отправлять задачи!")
    print("   Не трогай мышь и клавиатуру...")
    time.sleep(3)
    
    # Отправляем задачи в рабочие окна
    for i, (hwnd, title) in enumerate(worker_windows):
        if i >= len(TASKS):
            break
        
        task = TASKS[i]
        print(f"\n{'='*40}")
        print(f"🔧 Рабочий #{i+1}: {title[:30]}...")
        print(f"   Задача: {task[:50]}...")
        
        send_task(hwnd, task)
        time.sleep(1)
    
    # Возвращаем фокус пользователю
    print(f"\n   Возвращаю фокус в твоё окно...")
    activate_window_by_hwnd(user_hwnd)
    
    print("\n" + "=" * 50)
    print(f"✅ Задачи отправлены в {min(len(worker_windows), len(TASKS))} рабочих окон!")
    print("=" * 50)
    print("\nИИ работают над улучшением WA.")
    print("Проверь изменения: git diff gui.py")


if __name__ == "__main__":
    main()
