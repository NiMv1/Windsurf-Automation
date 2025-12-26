"""
Window Finder - Автоматическое нахождение окна Windsurf IDE
Игнорирует браузеры, проводник, другие приложения
"""

import re
import logging
from typing import Optional, List, Tuple, NamedTuple
from dataclasses import dataclass

try:
    import win32gui
    import win32process
    import win32con
    import psutil
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

logger = logging.getLogger('WA.WindowFinder')


@dataclass
class WindowInfo:
    """Информация об окне"""
    hwnd: int
    title: str
    class_name: str
    process_name: str
    process_id: int
    rect: Tuple[int, int, int, int]  # left, top, right, bottom
    
    @property
    def width(self) -> int:
        return self.rect[2] - self.rect[0]
    
    @property
    def height(self) -> int:
        return self.rect[3] - self.rect[1]
    
    def __str__(self):
        return f"Window('{self.title[:40]}...', process={self.process_name}, size={self.width}x{self.height})"


class WindowFinder:
    """
    Находит окно Windsurf IDE среди всех открытых окон.
    Использует множество критериев для точного определения.
    """
    
    # Паттерны для определения Windsurf
    WINDSURF_PATTERNS = [
        r".*windsurf.*",
        r".*- windsurf$",
        r"windsurf\s*-\s*.*",
    ]
    
    # Исключаемые паттерны (браузеры, проводник и т.д.)
    EXCLUDE_PATTERNS = [
        # Браузеры
        r".*google chrome.*",
        r".*mozilla firefox.*",
        r".*microsoft edge.*",
        r".*opera.*",
        r".*brave.*",
        r".*yandex.*",
        r".*vivaldi.*",
        
        # Проводник Windows
        r".*проводник.*",
        r".*explorer.*",
        r".*file explorer.*",
        r".*this pc.*",
        r".*этот компьютер.*",
        
        # Другие IDE (чтобы не путать)
        r".*visual studio code.*",
        r".*vscode.*",
        r".*intellij.*",
        r".*pycharm.*",
        r".*webstorm.*",
        
        # Системные окна
        r".*task manager.*",
        r".*диспетчер задач.*",
        r".*settings.*",
        r".*параметры.*",
    ]
    
    # Процессы Windsurf
    WINDSURF_PROCESSES = [
        "windsurf.exe",
        "windsurf",
    ]
    
    # Исключаемые процессы
    EXCLUDE_PROCESSES = [
        "chrome.exe",
        "firefox.exe",
        "msedge.exe",
        "opera.exe",
        "brave.exe",
        "explorer.exe",
        "code.exe",  # VS Code
    ]
    
    def __init__(self):
        if not WIN32_AVAILABLE:
            raise ImportError("Модули win32gui, win32process, psutil не установлены")
        
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Компилировать регулярные выражения"""
        self._windsurf_re = [re.compile(p, re.IGNORECASE) for p in self.WINDSURF_PATTERNS]
        self._exclude_re = [re.compile(p, re.IGNORECASE) for p in self.EXCLUDE_PATTERNS]
    
    def get_all_windows(self) -> List[WindowInfo]:
        """Получить список всех видимых окон"""
        windows = []
        
        def enum_callback(hwnd, results):
            if not win32gui.IsWindowVisible(hwnd):
                return True
            
            # Получаем информацию об окне
            try:
                title = win32gui.GetWindowText(hwnd)
                if not title:  # Пропускаем окна без заголовка
                    return True
                
                class_name = win32gui.GetClassName(hwnd)
                rect = win32gui.GetWindowRect(hwnd)
                
                # Получаем процесс
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    process = psutil.Process(pid)
                    process_name = process.name()
                except:
                    process_name = "unknown"
                
                info = WindowInfo(
                    hwnd=hwnd,
                    title=title,
                    class_name=class_name,
                    process_name=process_name,
                    process_id=pid,
                    rect=rect
                )
                results.append(info)
                
            except Exception as e:
                logger.debug(f"Ошибка получения информации об окне {hwnd}: {e}")
            
            return True
        
        win32gui.EnumWindows(enum_callback, windows)
        return windows
    
    def is_windsurf_window(self, window: WindowInfo) -> bool:
        """Проверить, является ли окно Windsurf IDE"""
        title_lower = window.title.lower()
        process_lower = window.process_name.lower()
        
        # Проверка по процессу (самый надёжный способ)
        if any(p in process_lower for p in self.WINDSURF_PROCESSES):
            logger.debug(f"Найден Windsurf по процессу: {window}")
            return True
        
        # Исключаем по процессу
        if any(p in process_lower for p in self.EXCLUDE_PROCESSES):
            logger.debug(f"Исключено по процессу: {window.process_name}")
            return False
        
        # Исключаем по заголовку
        for pattern in self._exclude_re:
            if pattern.match(window.title):
                logger.debug(f"Исключено по заголовку: {window.title[:50]}")
                return False
        
        # Проверяем по заголовку
        for pattern in self._windsurf_re:
            if pattern.match(window.title):
                logger.debug(f"Найден Windsurf по заголовку: {window}")
                return True
        
        # Проверяем класс окна (Electron приложения используют Chrome_WidgetWin_1)
        if window.class_name == "Chrome_WidgetWin_1":
            # Дополнительная проверка для Electron окон
            if "windsurf" in title_lower:
                logger.debug(f"Найден Windsurf по классу + заголовку: {window}")
                return True
        
        return False
    
    def find_windsurf(self) -> Optional[WindowInfo]:
        """
        Найти окно Windsurf IDE.
        
        Returns:
            WindowInfo если найдено, None если не найдено
        """
        windows = self.get_all_windows()
        
        # Фильтруем окна Windsurf
        windsurf_windows = [w for w in windows if self.is_windsurf_window(w)]
        
        if not windsurf_windows:
            logger.warning("Окно Windsurf не найдено")
            return None
        
        if len(windsurf_windows) > 1:
            logger.info(f"Найдено несколько окон Windsurf: {len(windsurf_windows)}")
            # Выбираем самое большое окно (обычно это основное окно IDE)
            windsurf_windows.sort(key=lambda w: w.width * w.height, reverse=True)
        
        result = windsurf_windows[0]
        logger.info(f"Выбрано окно Windsurf: {result}")
        return result
    
    def find_all_windsurf(self) -> List[WindowInfo]:
        """Найти все окна Windsurf"""
        windows = self.get_all_windows()
        return [w for w in windows if self.is_windsurf_window(w)]
    
    def activate_window(self, window: WindowInfo) -> bool:
        """
        Активировать (вывести на передний план) окно.
        
        Args:
            window: Информация об окне
            
        Returns:
            True если успешно
        """
        try:
            hwnd = window.hwnd
            
            # Если окно свёрнуто - разворачиваем
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
            # Выводим на передний план
            win32gui.SetForegroundWindow(hwnd)
            
            logger.info(f"Окно активировано: {window.title[:50]}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка активации окна: {e}")
            return False
    
    def get_window_screenshot_region(self, window: WindowInfo) -> Tuple[int, int, int, int]:
        """
        Получить регион для скриншота окна.
        
        Returns:
            (left, top, width, height)
        """
        return (
            window.rect[0],
            window.rect[1],
            window.width,
            window.height
        )


class WindsurfWindowManager:
    """
    Менеджер окон Windsurf - высокоуровневый интерфейс.
    """
    
    def __init__(self):
        self.finder = WindowFinder()
        self._current_window: Optional[WindowInfo] = None
    
    @property
    def current_window(self) -> Optional[WindowInfo]:
        """Текущее активное окно Windsurf"""
        return self._current_window
    
    def find_and_activate(self) -> bool:
        """
        Найти и активировать окно Windsurf.
        
        Returns:
            True если окно найдено и активировано
        """
        window = self.finder.find_windsurf()
        if window:
            if self.finder.activate_window(window):
                self._current_window = window
                return True
        return False
    
    def refresh(self) -> bool:
        """Обновить информацию о текущем окне"""
        if self._current_window:
            # Проверяем что окно ещё существует
            try:
                if win32gui.IsWindow(self._current_window.hwnd):
                    # Обновляем rect
                    rect = win32gui.GetWindowRect(self._current_window.hwnd)
                    self._current_window.rect = rect
                    return True
            except:
                pass
        
        # Окно не существует - ищем заново
        self._current_window = self.finder.find_windsurf()
        return self._current_window is not None
    
    def list_all(self) -> List[WindowInfo]:
        """Получить список всех окон Windsurf"""
        return self.finder.find_all_windsurf()
    
    def get_relative_coords(self, abs_x: int, abs_y: int) -> Tuple[int, int]:
        """
        Преобразовать абсолютные координаты в относительные (относительно окна).
        
        Args:
            abs_x: Абсолютная X координата
            abs_y: Абсолютная Y координата
            
        Returns:
            (rel_x, rel_y) относительные координаты
        """
        if not self._current_window:
            return abs_x, abs_y
        
        return (
            abs_x - self._current_window.rect[0],
            abs_y - self._current_window.rect[1]
        )
    
    def get_absolute_coords(self, rel_x: int, rel_y: int) -> Tuple[int, int]:
        """
        Преобразовать относительные координаты в абсолютные.
        
        Args:
            rel_x: Относительная X координата
            rel_y: Относительная Y координата
            
        Returns:
            (abs_x, abs_y) абсолютные координаты
        """
        if not self._current_window:
            return rel_x, rel_y
        
        return (
            rel_x + self._current_window.rect[0],
            rel_y + self._current_window.rect[1]
        )


def main():
    """Тестирование модуля"""
    logging.basicConfig(level=logging.DEBUG)
    
    finder = WindowFinder()
    
    print("=== Все окна ===")
    for w in finder.get_all_windows()[:10]:
        print(f"  {w}")
    
    print("\n=== Поиск Windsurf ===")
    windsurf = finder.find_windsurf()
    if windsurf:
        print(f"Найден: {windsurf}")
        print(f"Размер: {windsurf.width}x{windsurf.height}")
        print(f"Позиция: {windsurf.rect[:2]}")
    else:
        print("Windsurf не найден")


if __name__ == "__main__":
    main()
