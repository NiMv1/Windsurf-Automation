"""
Windsurf Automation - Автоматическое тестирование со скриншотами
Запускает полный цикл и делает скриншоты на каждом шаге
"""

import sys
import os
import time
from datetime import datetime

# Добавляем путь к src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pyautogui
from windsurf_automation import (
    WindsurfAutomation, 
    find_windsurf_windows, 
    activate_window_by_hwnd,
    get_window_rect
)

# Папка для скриншотов
SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'test_screenshots')
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


class AutoTester:
    """Автоматическое тестирование WA со скриншотами"""
    
    def __init__(self):
        self.wa = WindsurfAutomation()
        self.test_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = []
        self.screenshot_count = 0
    
    def screenshot(self, name: str) -> str:
        """Сделать скриншот и сохранить"""
        self.screenshot_count += 1
        filename = f"{self.test_id}_{self.screenshot_count:02d}_{name}.png"
        filepath = os.path.join(SCREENSHOTS_DIR, filename)
        
        # Делаем скриншот
        img = pyautogui.screenshot()
        img.save(filepath)
        
        print(f"📸 Скриншот: {filename}")
        return filepath
    
    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Записать результат теста"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "time": datetime.now().isoformat()
        }
        self.results.append(result)
        
        icon = "✅" if success else "❌"
        print(f"{icon} {test_name}: {details}")
    
    def test_find_windows(self) -> bool:
        """Тест 1: Поиск окон Windsurf"""
        print("\n" + "="*50)
        print("🧪 ТЕСТ 1: Поиск окон Windsurf")
        print("="*50)
        
        self.screenshot("01_before_find")
        
        windows = find_windsurf_windows(ide_only=True)
        
        if windows:
            self.log_result("find_windows", True, f"Найдено {len(windows)} окон")
            for hwnd, title in windows:
                print(f"   [{hwnd}] {title[:60]}")
            
            # Выбираем первое окно
            self.wa.hwnd, self.wa.title = windows[0]
            return True
        else:
            self.log_result("find_windows", False, "Окна не найдены")
            return False
    
    def test_activate_window(self) -> bool:
        """Тест 2: Активация окна"""
        print("\n" + "="*50)
        print("🧪 ТЕСТ 2: Активация окна")
        print("="*50)
        
        if not self.wa.hwnd:
            self.log_result("activate_window", False, "Нет выбранного окна")
            return False
        
        self.screenshot("02_before_activate")
        
        success = activate_window_by_hwnd(self.wa.hwnd)
        time.sleep(0.5)
        
        self.screenshot("02_after_activate")
        
        if success:
            self.log_result("activate_window", True, f"Окно активировано: {self.wa.title[:40]}")
            return True
        else:
            self.log_result("activate_window", False, "Не удалось активировать")
            return False
    
    def test_open_new_window(self) -> bool:
        """Тест 3: Открытие нового окна"""
        print("\n" + "="*50)
        print("🧪 ТЕСТ 3: Открытие нового окна (Ctrl+Shift+N)")
        print("="*50)
        
        windows_before = find_windsurf_windows(ide_only=True)
        count_before = len(windows_before)
        print(f"   Окон до: {count_before}")
        
        self.screenshot("03_before_new_window")
        
        # Активируем текущее окно
        if self.wa.hwnd:
            activate_window_by_hwnd(self.wa.hwnd)
            time.sleep(0.5)
        
        # Отправляем Ctrl+Shift+N
        import keyboard
        keyboard.send('ctrl+shift+n')
        
        # Ждём открытия
        time.sleep(3)
        
        self.screenshot("03_after_new_window")
        
        windows_after = find_windsurf_windows(ide_only=True)
        count_after = len(windows_after)
        print(f"   Окон после: {count_after}")
        
        if count_after > count_before:
            # Находим новое окно
            old_hwnds = {w[0] for w in windows_before}
            for hwnd, title in windows_after:
                if hwnd not in old_hwnds:
                    self.wa.hwnd = hwnd
                    self.wa.title = title
                    self.log_result("open_new_window", True, f"Новое окно: {title[:40]}")
                    return True
        
        self.log_result("open_new_window", False, f"Окон не прибавилось ({count_before} -> {count_after})")
        return False
    
    def test_open_sidebar(self) -> bool:
        """Тест 4: Открытие Cascade sidebar"""
        print("\n" + "="*50)
        print("🧪 ТЕСТ 4: Закрытие Welcome + Открытие sidebar")
        print("="*50)
        
        if not self.wa.hwnd:
            self.log_result("open_sidebar", False, "Нет окна")
            return False
        
        self.screenshot("04_before_sidebar")
        
        # Активируем окно
        activate_window_by_hwnd(self.wa.hwnd)
        time.sleep(0.5)
        
        # Закрываем Welcome вкладку через Ctrl+W
        print("   Закрываю Welcome вкладку (Ctrl+W)...")
        import keyboard
        keyboard.send('ctrl+w')
        time.sleep(0.5)
        
        self.screenshot("04_after_escape")
        
        # Отправляем Ctrl+L
        import keyboard
        keyboard.send('ctrl+l')
        time.sleep(1.5)
        
        self.screenshot("04_after_sidebar")
        
        self.log_result("open_sidebar", True, "Welcome закрыт, sidebar открыт")
        return True
    
    def test_send_prompt(self) -> bool:
        """Тест 5: Отправка тестового промпта"""
        print("\n" + "="*50)
        print("🧪 ТЕСТ 5: Отправка тестового промпта")
        print("="*50)
        
        if not self.wa.hwnd:
            self.log_result("send_prompt", False, "Нет окна")
            return False
        
        test_prompt = "Привет! Это тестовое сообщение от Windsurf Automation. Ответь коротко: OK"
        
        self.screenshot("05_before_prompt")
        
        # Активируем окно
        activate_window_by_hwnd(self.wa.hwnd)
        time.sleep(0.5)
        
        # Кликаем в область чата (правая часть окна, внизу)
        rect = get_window_rect(self.wa.hwnd)
        chat_x = rect[2] - 200  # 200px от правого края
        chat_y = rect[3] - 80   # 80px от низа
        
        print(f"   Окно: {rect}")
        print(f"   Клик в ({chat_x}, {chat_y})")
        pyautogui.click(chat_x, chat_y)
        time.sleep(0.3)
        
        self.screenshot("05_after_click")
        
        # Вставляем текст
        import pyperclip
        pyperclip.copy(test_prompt)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        
        self.screenshot("05_after_paste")
        
        # Отправляем
        pyautogui.press('enter')
        time.sleep(1)
        
        self.screenshot("05_after_send")
        
        self.log_result("send_prompt", True, "Промпт отправлен (проверь скриншоты)")
        return True
    
    def generate_report(self) -> str:
        """Генерация отчёта о тестировании"""
        print("\n" + "="*50)
        print("📊 ОТЧЁТ О ТЕСТИРОВАНИИ")
        print("="*50)
        
        report_lines = [
            f"# Отчёт автотестирования WA",
            f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**ID теста:** {self.test_id}",
            f"**Скриншотов:** {self.screenshot_count}",
            "",
            "## Результаты:",
            ""
        ]
        
        passed = 0
        failed = 0
        
        for r in self.results:
            icon = "✅" if r['success'] else "❌"
            report_lines.append(f"- {icon} **{r['test']}**: {r['details']}")
            if r['success']:
                passed += 1
            else:
                failed += 1
        
        report_lines.extend([
            "",
            f"## Итого: {passed} пройдено, {failed} провалено",
            "",
            f"## Скриншоты:",
            f"Папка: `test_screenshots/`",
            f"Файлы начинаются с `{self.test_id}_`"
        ])
        
        report = "\n".join(report_lines)
        
        # Сохраняем отчёт
        report_file = os.path.join(SCREENSHOTS_DIR, f"{self.test_id}_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(report)
        print(f"\n📄 Отчёт сохранён: {report_file}")
        
        return report_file
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("\n" + "="*60)
        print("🚀 WINDSURF AUTOMATION - АВТОТЕСТИРОВАНИЕ")
        print("="*60)
        print(f"ID теста: {self.test_id}")
        print(f"Папка скриншотов: {SCREENSHOTS_DIR}")
        print("\n⚠️ Не двигай мышь и не нажимай клавиши во время теста!")
        print("   Тест начнётся через 3 секунды...")
        time.sleep(3)
        
        # Тест 1: Поиск окон
        if not self.test_find_windows():
            print("\n❌ КРИТИЧЕСКАЯ ОШИБКА: Windsurf не найден!")
            self.generate_report()
            return
        
        # Тест 2: Активация окна
        self.test_activate_window()
        
        # Тест 3: Открытие нового окна
        self.test_open_new_window()
        
        # Тест 4: Открытие sidebar
        self.test_open_sidebar()
        
        # Тест 5: Отправка промпта
        self.test_send_prompt()
        
        # Финальный скриншот
        time.sleep(2)
        self.screenshot("99_final_state")
        
        # Генерация отчёта
        report_file = self.generate_report()
        
        return report_file


def main():
    tester = AutoTester()
    report = tester.run_all_tests()
    
    print("\n" + "="*60)
    print("✅ Тестирование завершено!")
    print(f"   Скриншоты: test_screenshots/")
    print("="*60)
    
    return report


if __name__ == "__main__":
    main()
