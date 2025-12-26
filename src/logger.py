"""
Модуль логирования Windsurf Automation
Централизованная система логирования с уровнями
"""

import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


class Logger:
    """Класс для управления логированием приложения"""
    
    # Уровни логирования
    LEVELS = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    def __init__(self, name: str = "WA", log_dir: str = "logs"):
        """
        Инициализация логгера
        
        Args:
            name: Имя логгера
            log_dir: Директория для хранения логов
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """Настройка логгера"""
        # Создаем директорию для логов
        self.log_dir.mkdir(exist_ok=True)
        
        # Очищаем существующие обработчики
        self.logger.handlers.clear()
        
        # Устанавливаем уровень логирования
        self.logger.setLevel(logging.INFO)
        
        # Формат логов
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Обработчик для файла
        file_handler = logging.FileHandler(
            self.log_dir / f"{self.name.lower()}_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Обработчик для консоли
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def set_level(self, level: str) -> None:
        """
        Установка уровня логирования
        
        Args:
            level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        if level.upper() in self.LEVELS:
            self.logger.setLevel(self.LEVELS[level.upper()])
        else:
            self.warning(f"Неверный уровень логирования: {level}")
    
    def debug(self, message: str) -> None:
        """Логирование отладочного сообщения"""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Логирование информационного сообщения"""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Логирование предупреждения"""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Логирование ошибки"""
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """Логирование критической ошибки"""
        self.logger.critical(message)
    
    def exception(self, message: str) -> None:
        """Логирование исключения с traceback"""
        self.logger.exception(message)
    
    def log_operation(self, operation: str, status: str, details: Optional[str] = None) -> None:
        """
        Логирование операции с статусом
        
        Args:
            operation: Название операции
            status: Статус (SUCCESS, FAILED, STARTED, COMPLETED)
            details: Дополнительные детали
        """
        message = f"{operation} - {status}"
        if details:
            message += f": {details}"
        
        if status in ["SUCCESS", "COMPLETED"]:
            self.info(message)
        elif status == "FAILED":
            self.error(message)
        elif status == "STARTED":
            self.info(message)
        else:
            self.debug(message)


# Глобальный экземпляр логгера
app_logger = Logger()


def get_logger() -> Logger:
    """
    Получение глобального логгера
    
    Returns:
        Экземпляр логгера
    """
    return app_logger
