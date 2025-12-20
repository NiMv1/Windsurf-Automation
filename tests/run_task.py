"""
Запуск одной задачи через WA
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from windsurf_automation import WindsurfAutomation, find_windsurf_windows

def main():
    print("=" * 60)
    print("🚀 WINDSURF AUTOMATION - ЗАПУСК ЗАДАЧИ")
    print("=" * 60)
    
    # Проверяем что Windsurf открыт
    windows = find_windsurf_windows(ide_only=True)
    if not windows:
        print("❌ Windsurf не найден! Открой Windsurf и попробуй снова.")
        return
    
    print(f"✅ Найдено {len(windows)} окон Windsurf")
    
    wa = WindsurfAutomation()
    wa.hwnd, wa.title = windows[0]
    
    # Задача для улучшения WA
    prompt = """Ты работаешь над проектом Windsurf Automation.
Путь: C:\\Users\\bnex4\\CascadeProjects\\Windsurf-Automation

ЗАДАЧА: Добавь в файл gui.py кнопку "🧪 Запустить тест" которая запускает tests/auto_test.py

ТРЕБОВАНИЯ:
1. Изменяй только gui.py
2. Кнопка должна быть в карточке "Запуск задачи"
3. Используй threading для запуска теста
4. Комментарии на русском

ОТЧЁТ (обязательно в конце):
## Сделано:
- ...

## Не сделано:
- ...

## Проблемы:
- ..."""

    print("\n⚠️ ВНИМАНИЕ!")
    print("   1. После открытия окна ВРУЧНУЮ выбери модель GPT-5.1-Codex")
    print("   2. Тест начнётся через 5 секунд...")
    print("\n   Нажми Ctrl+C чтобы отменить")
    
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        print("\n❌ Отменено")
        return
    
    print("\n🚀 Запускаю задачу...")
    success = wa.run_task(prompt, model="GPT-5.1-Codex", close_after=False)
    
    if success:
        print("\n✅ Задача отправлена!")
        print("   Теперь выбери модель и дождись ответа ИИ")
    else:
        print("\n❌ Не удалось отправить задачу")


if __name__ == "__main__":
    main()
