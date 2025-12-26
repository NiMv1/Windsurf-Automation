"""
Модуль управления Windsurf через горячие клавиши
Контроллер для автоматизации действий в Windsurf IDE
"""

import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .logger import get_logger
from .exceptions import AutomationError, WindowNotFoundError


@dataclass
class WindowInfo:
    """Информация об окне Windsurf"""
    hwnd: int
    title: str
    process_id: Optional[int] = None


class WindsurfController:
    """Контроллер для управления Windsurf через горячие клавиши"""
    
    def __init__(self, config):
        """
        Инициализация контроллера
        
        Args:
            config: Объект конфигурации
        """
        self.config = config
        self.logger = get_logger()
        self.running = False
        self.current_window: Optional[WindowInfo] = None
        
        # Проверка доступности библиотек
        self._check_dependencies()
    
    def _check_dependencies(self) -> None:
        """Проверка доступности необходимых библиотек"""
        try:
            import pyautogui
            import pyperclip
            self.autopy_available = True
        except ImportError:
            self.autopy_available = False
            self.logger.warning("pyautogui/pyperclip не установлены. pip install pyautogui pyperclip")
        
        try:
            import win32gui
            import win32con
            self.win32_available = True
        except ImportError:
            self.win32_available = False
            self.logger.warning("pywin32 не установлен. pip install pywin32")
    
    def find_windsurf_windows(self) -> List[WindowInfo]:
        """
        Найти все окна Windsurf
        
        Returns:
            Список информации об окнах Windsurf
        """
        if not self.win32_available:
            self.logger.error("win32 библиотеки недоступны")
            return []
        
        import win32gui
        
        windows = []
        
        def callback(hwnd, results):
            """Callback для перечисления окон"""
            try:
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if "windsurf" in title.lower() and "browser" not in title.lower():
                        window_info = WindowInfo(
                            hwnd=hwnd,
                            title=title[:60] + "..." if len(title) > 60 else title
                        )
                        results.append(window_info)
            except Exception as e:
                self.logger.debug(f"Ошибка при обработке окна {hwnd}: {e}")
            return True
        
        try:
            win32gui.EnumWindows(callback, windows)
            self.logger.info(f"Найдено окон Windsurf: {len(windows)}")
        except Exception as e:
            self.logger.error(f"Ошибка при поиске окон: {e}")
        
        return windows
    
    def activate_window(self, hwnd: int) -> bool:
        """
        Активировать окно
        
        Args:
            hwnd: Дескриптор окна
            
        Returns:
            True если активация успешна
        """
        if not self.win32_available:
            self.logger.error("win32 библиотеки недоступны")
            return False
        
        import win32gui
        import win32con
        
        try:
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.3)
            
            self.logger.info(f"Окно {hwnd} активировано")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка активации окна {hwnd}: {e}")
            return False
    
    def press_hotkey(self, keys: List[str]) -> None:
        """
        Нажать комбинацию клавиш
        
        Args:
            keys: Список клавиш
        """
        if not self.autopy_available:
            self.logger.warning("Библиотеки автоматизации недоступны")
            return
        
        try:
            import pyautogui
            pyautogui.hotkey(*keys)
            delay = self.config.get("delays.after_hotkey", 0.5)
            time.sleep(delay)
            self.logger.debug(f"Нажата комбинация: {'+'.join(keys)}")
        except Exception as e:
            self.logger.error(f"Ошибка нажатия клавиш {keys}: {e}")
            raise AutomationError(f"Не удалось нажать комбинацию клавиш: {e}")
    
    def paste_text(self, text: str) -> None:
        """
        Вставить текст через буфер обмена
        
        Args:
            text: Текст для вставки
        """
        if not self.autopy_available:
            self.logger.warning("Библиотеки автоматизации недоступны")
            return
        
        try:
            import pyautogui
            import pyperclip
            
            pyperclip.copy(text)
            time.sleep(0.1)
            pyautogui.hotkey("ctrl", "v")
            
            delay = self.config.get("delays.after_paste", 0.3)
            time.sleep(delay)
            
            self.logger.debug(f"Вставлен текст ({len(text)} символов)")
        except Exception as e:
            self.logger.error(f"Ошибка вставки текста: {e}")
            raise AutomationError(f"Не удалось вставить текст: {e}")
    
    def open_new_window(self) -> None:
        """Открыть новое окно Windsurf"""
        self.logger.info("Открытие нового окна (Ctrl+Shift+N)...")
        keys = self.config.get("hotkeys.new_window", ["ctrl", "shift", "n"])
        self.press_hotkey(keys)
    
    def open_cascade(self) -> None:
        """Открыть панель Cascade"""
        self.logger.info("Открытие Cascade (Ctrl+L)...")
        keys = self.config.get("hotkeys.open_cascade", ["ctrl", "l"])
        self.press_hotkey(keys)
    
    def select_model(self, model_name: str) -> None:
        """
        Выбрать модель AI
        
        Args:
            model_name: Название модели
        """
        self.logger.info(f"Выбор модели: {model_name}")
        
        try:
            # Ctrl+/ для открытия выбора модели
            keys = self.config.get("hotkeys.select_model", ["ctrl", "/"])
            self.press_hotkey(keys)
            time.sleep(0.5)
            
            # Вставляем название модели
            self.paste_text(model_name)
            time.sleep(0.3)
            
            # Стрелка вниз и Enter для выбора
            import pyautogui
            pyautogui.press("down")
            time.sleep(0.2)
            pyautogui.press("enter")
            time.sleep(0.5)
            
            self.logger.info(f"Модель {model_name} выбрана")
        except Exception as e:
            self.logger.error(f"Ошибка выбора модели: {e}")
            raise AutomationError(f"Не удалось выбрать модель: {e}")
    
    def send_message(self, message: str) -> None:
        """
        Отправить сообщение в чат
        
        Args:
            message: Сообщение для отправки
        """
        self.logger.info(f"Отправка сообщения ({len(message)} символов)...")
        
        try:
            # Открываем Cascade для фокуса на чате
            self.open_cascade()
            time.sleep(0.3)
            
            # Вставляем сообщение
            self.paste_text(message)
            
            # Отправляем
            keys = self.config.get("hotkeys.send", ["enter"])
            self.press_hotkey(keys)
            
            self.logger.info("Сообщение отправлено")
        except Exception as e:
            self.logger.error(f"Ошибка отправки сообщения: {e}")
            raise AutomationError(f"Не удалось отправить сообщение: {e}")
    
    def start_session(self, hwnd: Optional[int] = None, model: Optional[str] = None) -> bool:
        """
        Начать новую сессию работы
        
        Args:
            hwnd: Дескриптор окна (опционально)
            model: Название модели (опционально)
            
        Returns:
            True если сессия запущена успешно
        """
        self.running = True
        model = model or self.config.get("model", "claude-3.5-sonnet")
        warmup_time = self.config.get("delays.cascade_warmup", 20)
        
        try:
            self.logger.log_operation("Запуск сессии", "STARTED", f"модель: {model}")
            
            # 1. Активируем окно если указано
            if hwnd:
                self.logger.info("Активация окна Windsurf...")
                if not self.activate_window(hwnd):
                    raise WindowNotFoundError(f"Не удалось активировать окно {hwnd}")
            
            # 2. Открываем новое окно
            self.open_new_window()
            time.sleep(2)  # Ждём открытия окна
            
            # 3. Открываем Cascade и ждём прогрева
            self.open_cascade()
            self.logger.info(f"Ожидание прогрева Cascade ({warmup_time} сек)...")
            time.sleep(warmup_time)
            
            # 4. Выбираем модель
            self.select_model(model)
            
            self.logger.log_operation("Запуск сессии", "SUCCESS", "сессия готова к работе")
            return True
            
        except Exception as e:
            self.logger.log_operation("Запуск сессии", "FAILED", str(e))
            return False
        finally:
            self.running = False
    
    def stop(self) -> None:
        """Остановить выполнение"""
        self.running = False
        self.logger.info("Выполнение остановлено")
    
    def is_running(self) -> bool:
        """
        Проверить статус выполнения
        
        Returns:
            True если выполняется операция
        """
        return self.running
    
    def get_current_window(self) -> Optional[WindowInfo]:
        """
        Получить информацию о текущем окне
        
        Returns:
            Информация о текущем окне
        """
        return self.current_window
