"""
Модуль исключений Windsurf Automation
Специфические исключения для приложения
"""


class WindsurfAutomationError(Exception):
    """Базовый класс исключений Windsurf Automation"""
    pass


class AutomationError(WindsurfAutomationError):
    """Ошибка при выполнении автоматизации"""
    pass


class WindowNotFoundError(WindsurfAutomationError):
    """Ошибка - окно не найдено"""
    pass


class ConfigurationError(WindsurfAutomationError):
    """Ошибка конфигурации"""
    pass


class ValidationError(WindsurfAutomationError):
    """Ошибка валидации данных"""
    pass


class FileOperationError(WindsurfAutomationError):
    """Ошибка при работе с файлами"""
    pass


class HotkeyError(WindsurfAutomationError):
    """Ошибка при работе с горячими клавишами"""
    pass


class ClipboardError(WindsurfAutomationError):
    """Ошибка при работе с буфером обмена"""
    pass


class SessionError(WindsurfAutomationError):
    """Ошибка сессии"""
    pass
