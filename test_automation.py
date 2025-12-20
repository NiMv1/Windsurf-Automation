"""
Автоматический тест Windsurf Automation
Запускается без интерактивного ввода
"""

import time
import sys
sys.path.insert(0, 'src')

from windsurf_automation import WindsurfAutomation, find_windsurf_windows

def run_test():
    print("=" * 60)
    print("🧪 Windsurf Automation - Автоматический тест")
    print("=" * 60)
    print("\n⚠️ Тест начнётся через 3 секунды...")
    print("   Убедитесь что Windsurf открыт!")
    time.sleep(3)
    
    wa = WindsurfAutomation()
    
    # Шаг 1: Найти окна Windsurf
    print("\n" + "=" * 40)
    print("📋 Шаг 1: Поиск окон Windsurf")
    print("=" * 40)
    
    windows = find_windsurf_windows()
    
    # Используем встроенную фильтрацию IDE окон
    windsurf_windows = find_windsurf_windows(ide_only=True)
    
    if not windsurf_windows:
        print("❌ Окна Windsurf не найдены!")
        print("   Найденные окна с 'Windsurf' в названии:")
        for h, t in windows:
            print(f"     - {t}")
        return False
    
    print(f"✅ Найдено {len(windsurf_windows)} окон Windsurf:")
    for i, (hwnd, title) in enumerate(windsurf_windows):
        print(f"   [{i}] HWND={hwnd}: {title[:60]}...")
    
    # Выбираем первое окно Windsurf
    wa.hwnd, wa.title = windsurf_windows[0]
    print(f"\n✅ Выбрано окно: HWND={wa.hwnd}")
    
    # Шаг 2: Активация окна
    print("\n" + "=" * 40)
    print("🔄 Шаг 2: Активация окна")
    print("=" * 40)
    
    if wa.activate_window():
        print("✅ Окно активировано")
    else:
        print("❌ Не удалось активировать окно")
        return False
    
    time.sleep(1)
    
    # Шаг 3: Открытие нового окна
    print("\n" + "=" * 40)
    print("🔄 Шаг 3: Открытие нового окна (Ctrl+Shift+N)")
    print("=" * 40)
    
    if wa.open_new_window():
        print("✅ Новое окно открыто")
    else:
        print("❌ Не удалось открыть новое окно")
        return False
    
    time.sleep(1)
    
    # Шаг 4: Открытие sidebar
    print("\n" + "=" * 40)
    print("🔄 Шаг 4: Открытие Cascade sidebar (Ctrl+L)")
    print("=" * 40)
    
    if wa.open_sidebar():
        print("✅ Sidebar открыт")
    else:
        print("❌ Не удалось открыть sidebar")
        return False
    
    time.sleep(1)
    
    # Шаг 5: Отправка тестового сообщения
    print("\n" + "=" * 40)
    print("🔄 Шаг 5: Отправка тестового сообщения")
    print("=" * 40)
    
    test_message = "Hello from Windsurf Automation! 🚀 This is a test message."
    if wa.send_message(test_message):
        print(f"✅ Сообщение отправлено: {test_message}")
    else:
        print("❌ Не удалось отправить сообщение")
        return False
    
    # Итог
    print("\n" + "=" * 60)
    print("🎉 ТЕСТ ЗАВЕРШЁН УСПЕШНО!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
