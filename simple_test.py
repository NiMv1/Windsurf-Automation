"""
Простой тест - только sidebar и сообщение (без нового окна)
"""

import time
import sys
sys.path.insert(0, 'src')

from windsurf_automation import WindsurfAutomation, find_windsurf_windows

def simple_test():
    print("=" * 60)
    print("🧪 Простой тест - Sidebar + Сообщение")
    print("=" * 60)
    print("\n⚠️ Тест начнётся через 3 секунды...")
    time.sleep(3)
    
    wa = WindsurfAutomation()
    
    # Найти окна Windsurf IDE
    windows = find_windsurf_windows()
    windsurf_windows = [(h, t) for h, t in windows if " - Windsurf - " in t]
    
    if not windsurf_windows:
        print("❌ Окна Windsurf IDE не найдены!")
        return False
    
    print(f"✅ Найдено {len(windsurf_windows)} окон:")
    for i, (hwnd, title) in enumerate(windsurf_windows):
        print(f"   [{i}] {title[:60]}...")
    
    wa.hwnd, wa.title = windsurf_windows[0]
    print(f"\n✅ Выбрано: HWND={wa.hwnd}")
    
    # Активация
    print("\n🔄 Активирую окно...")
    if not wa.activate_window():
        print("❌ Не удалось активировать")
        return False
    print("✅ Окно активировано")
    
    time.sleep(1)
    
    # Sidebar
    print("\n🔄 Открываю sidebar (Ctrl+L)...")
    if not wa.open_sidebar():
        print("❌ Не удалось открыть sidebar")
        return False
    print("✅ Sidebar открыт")
    
    time.sleep(1)
    
    # Сообщение
    print("\n🔄 Отправляю тестовое сообщение...")
    if not wa.send_message("Hello from Windsurf Automation! 🚀"):
        print("❌ Не удалось отправить сообщение")
        return False
    print("✅ Сообщение отправлено")
    
    print("\n" + "=" * 60)
    print("🎉 ТЕСТ ЗАВЕРШЁН!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = simple_test()
    sys.exit(0 if success else 1)
