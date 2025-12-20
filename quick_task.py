"""
Быстрая отправка задачи в существующее окно Windsurf
Без открытия новых окон - просто Ctrl+L и вставка промпта
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from windsurf_automation import find_windsurf_windows, activate_window_by_hwnd
import keyboard
import pyperclip

# Простая задача
TASK = """Проект: C:\\Users\\bnex4\\CascadeProjects\\Windsurf-Automation

ЗАДАЧА: В gui.py добавь кнопку "🧪 Тест" которая запускает tests/auto_test.py

ТРЕБОВАНИЯ: 
- Изменяй ТОЛЬКО gui.py
- Используй subprocess.Popen
- Комментарии на русском

ОТЧЁТ: ## Сделано / ## Проблемы"""


def main():
    print("=" * 50)
    print("🚀 БЫСТРАЯ ОТПРАВКА ЗАДАЧИ")
    print("=" * 50)
    
    # Находим окно Windsurf
    windows = find_windsurf_windows(ide_only=True)
    if not windows:
        print("❌ Windsurf не найден!")
        return
    
    # Берём первое окно
    hwnd, title = windows[0]
    print(f"✅ Окно: {title[:50]}...")
    
    print("\n⚠️ Через 3 сек отправлю задачу в это окно!")
    print("   Не трогай мышь и клавиатуру...")
    time.sleep(3)
    
    # Активируем окно
    print("\n1. Активирую окно...")
    activate_window_by_hwnd(hwnd)
    time.sleep(0.5)
    
    # Ctrl+L - открыть Cascade
    print("2. Ctrl+L (Cascade)...")
    keyboard.send('ctrl+l')
    time.sleep(1.5)
    
    # Вставляем промпт
    print("3. Вставляю промпт...")
    pyperclip.copy(TASK)
    keyboard.send('ctrl+v')
    time.sleep(0.3)
    
    # Enter
    print("4. Enter...")
    keyboard.send('enter')
    time.sleep(0.5)
    
    print("\n✅ Готово! Выбери модель в Windsurf.")


if __name__ == "__main__":
    main()
