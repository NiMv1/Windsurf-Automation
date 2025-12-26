"""
Модуль конфигурации Windsurf Automation
Управление настройками приложения
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Класс для управления конфигурацией приложения"""
    
    DEFAULT_CONFIG = {
        "model": "claude-3.5-sonnet",
        "iterations": 1,
        "work_folders": [],
        "prompts_folder": "",
        "delays": {
            "cascade_warmup": 25,
            "after_hotkey": 0.5,
            "after_paste": 0.3,
            "between_messages": 2
        },
        "hotkeys": {
            "new_window": ["ctrl", "shift", "n"],
            "open_cascade": ["ctrl", "l"],
            "select_model": ["ctrl", "/"],
            "send": ["enter"]
        },
        "gui": {
            "theme": "dark",
            "sound_enabled": True,
            "auto_save": True,
            "window_size": "600x700"
        },
        "logging": {
            "level": "INFO",
            "file_enabled": True,
            "console_enabled": True
        }
    }
    
    def __init__(self, config_path: str = "config.json"):
        """
        Инициализация конфигурации
        
        Args:
            config_path: Путь к файлу конфигурации
        """
        self.config_path = Path(config_path)
        self._data = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Загрузка конфигурации из файла
        
        Returns:
            Словарь с настройками
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Объединяем с настройками по умолчанию
                    config = self.DEFAULT_CONFIG.copy()
                    self._deep_update(config, loaded_config)
                    return config
            except (json.JSONDecodeError, IOError) as e:
                print(f"Ошибка загрузки конфигурации: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Создаем файл конфигурации с настройками по умолчанию
            self.save_config()
            return self.DEFAULT_CONFIG.copy()
    
    def _deep_update(self, base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
        """
        Рекурсивное обновление словаря
        
        Args:
            base_dict: Базовый словарь
            update_dict: Словарь с обновлениями
        """
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def save_config(self) -> bool:
        """
        Сохранение конфигурации в файл
        
        Returns:
            True если сохранение успешно
        """
        try:
            # Создаем директорию если не существует
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=4, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Ошибка сохранения конфигурации: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Получение значения по ключу
        
        Args:
            key: Ключ (можно использовать точечную нотацию, например 'gui.theme')
            default: Значение по умолчанию
            
        Returns:
            Значение настройки
        """
        keys = key.split('.')
        value = self._data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Установка значения по ключу
        
        Args:
            key: Ключ (можно использовать точечную нотацию)
            value: Новое значение
        """
        keys = key.split('.')
        data = self._data
        
        # Навигация к родительскому словарю
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        
        # Установка значения
        data[keys[-1]] = value
        
        # Автосохранение если включено
        if self.get('gui.auto_save', True):
            self.save_config()
    
    def get_all(self) -> Dict[str, Any]:
        """
        Получение всех настроек
        
        Returns:
            Словарь со всеми настройками
        """
        return self._data.copy()
    
    def reset_to_defaults(self) -> None:
        """Сброс настроек к значениям по умолчанию"""
        self._data = self.DEFAULT_CONFIG.copy()
        self.save_config()
    
    def validate(self) -> bool:
        """
        Валидация конфигурации
        
        Returns:
            True если конфигурация валидна
        """
        required_keys = ['model', 'delays', 'hotkeys']
        
        for key in required_keys:
            if key not in self._data:
                return False
        
        # Проверка типов
        if not isinstance(self._data['delays'], dict):
            return False
        
        if not isinstance(self._data['hotkeys'], dict):
            return False
        
        return True
