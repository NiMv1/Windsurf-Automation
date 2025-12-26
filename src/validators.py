"""
Модуль валидации Windsurf Automation
Проверка корректности данных и настроек
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from .exceptions import ValidationError


class PathValidator:
    """Валидатор путей файловой системы"""
    
    @staticmethod
    def validate_path_exists(path: str, path_type: str = "папка") -> str:
        """
        Проверить существование пути
        
        Args:
            path: Путь для проверки
            path_type: Тип пути (файл/папка)
            
        Returns:
            Валидный путь
            
        Raises:
            ValidationError: Если путь не существует
        """
        if not path:
            raise ValidationError(f"Путь к {path_type} не указан")
        
        path_obj = Path(path)
        
        if not path_obj.exists():
            raise ValidationError(f"{path_type.capitalize()} не существует: {path}")
        
        return str(path_obj.absolute())
    
    @staticmethod
    def validate_directory(path: str) -> str:
        """
        Проверить что путь является директорией
        
        Args:
            path: Путь для проверки
            
        Returns:
            Валидный путь к директории
        """
        validated_path = PathValidator.validate_path_exists(path, "папка")
        
        if not Path(validated_path).is_dir():
            raise ValidationError(f"Путь не является папкой: {validated_path}")
        
        return validated_path
    
    @staticmethod
    def validate_file(path: str, extensions: Optional[List[str]] = None) -> str:
        """
        Проверить что путь является файлом
        
        Args:
            path: Путь для проверки
            extensions: Допустимые расширения
            
        Returns:
            Валидный путь к файлу
        """
        validated_path = PathValidator.validate_path_exists(path, "файл")
        
        if not Path(validated_path).is_file():
            raise ValidationError(f"Путь не является файлом: {validated_path}")
        
        if extensions:
            file_ext = Path(validated_path).suffix.lower()
            if file_ext not in [ext.lower() for ext in extensions]:
                raise ValidationError(f"Недопустимое расширение файла: {file_ext}")
        
        return validated_path


class ConfigValidator:
    """Валидатор конфигурации"""
    
    @staticmethod
    def validate_model_name(model: str) -> str:
        """
        Проверить корректность названия модели
        
        Args:
            model: Название модели
            
        Returns:
            Валидное название модели
        """
        if not model or not isinstance(model, str):
            raise ValidationError("Название модели должно быть непустой строкой")
        
        model = model.strip()
        if len(model) < 2:
            raise ValidationError("Название модели слишком короткое")
        
        if len(model) > 100:
            raise ValidationError("Название модели слишком длинное")
        
        # Проверка на недопустимые символы
        if re.search(r'[<>:"/\\|?*]', model):
            raise ValidationError("Название модели содержит недопустимые символы")
        
        return model
    
    @staticmethod
    def validate_iterations(iterations: int) -> int:
        """
        Проверить корректность количества итераций
        
        Args:
            iterations: Количество итераций
            
        Returns:
            Валидное количество итераций
        """
        if not isinstance(iterations, int):
            raise ValidationError("Количество итераций должно быть числом")
        
        if iterations < 1:
            raise ValidationError("Количество итераций должно быть не менее 1")
        
        if iterations > 1000:
            raise ValidationError("Количество итераций не должно превышать 1000")
        
        return iterations
    
    @staticmethod
    def validate_delay(delay: float, delay_name: str = "задержка") -> float:
        """
        Проверить корректность задержки
        
        Args:
            delay: Значение задержки
            delay_name: Название задержки для сообщения об ошибке
            
        Returns:
            Валидное значение задержки
        """
        if not isinstance(delay, (int, float)):
            raise ValidationError(f"{delay_name.capitalize()} должна быть числом")
        
        if delay < 0:
            raise ValidationError(f"{delay_name.capitalize()} не может быть отрицательной")
        
        if delay > 300:  # 5 минут максимум
            raise ValidationError(f"{delay_name.capitalize()} слишком большая (максимум 300 сек)")
        
        return float(delay)
    
    @staticmethod
    def validate_hotkeys(hotkeys: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Проверить корректность горячих клавиш
        
        Args:
            hotkeys: Словарь горячих клавиш
            
        Returns:
            Валидный словарь горячих клавиш
        """
        if not isinstance(hotkeys, dict):
            raise ValidationError("Горячие клавиши должны быть словарем")
        
        valid_keys = ["ctrl", "alt", "shift", "win", "enter", "escape", "space", 
                     "tab", "backspace", "delete", "home", "end", "pageup", "pagedown",
                     "up", "down", "left", "right", "f1", "f2", "f3", "f4", "f5", 
                     "f6", "f7", "f8", "f9", "f10", "f11", "f12"]
        
        valid_keys.extend([str(i) for i in range(10)])  # Цифры
        valid_keys.extend([chr(i) for i in range(ord('a'), ord('z') + 1)])  # Буквы
        
        for action, keys in hotkeys.items():
            if not isinstance(keys, list):
                raise ValidationError(f"Клавиши для действия '{action}' должны быть списком")
            
            if len(keys) == 0:
                raise ValidationError(f"Для действия '{action}' не указаны клавиши")
            
            for key in keys:
                if not isinstance(key, str):
                    raise ValidationError(f"Клавиша должна быть строкой: {key}")
                
                if key.lower() not in valid_keys:
                    raise ValidationError(f"Недопустимая клавиша: {key}")
        
        return hotkeys


class PromptValidator:
    """Валидатор промптов"""
    
    @staticmethod
    def validate_prompt_content(content: str) -> str:
        """
        Проверить содержимое промпта
        
        Args:
            content: Содержимое промпта
            
        Returns:
            Валидное содержимое
        """
        if not isinstance(content, str):
            raise ValidationError("Промпт должен быть строкой")
        
        content = content.strip()
        if len(content) == 0:
            raise ValidationError("Промпт не может быть пустым")
        
        if len(content) > 100000:  # 100KB максимум
            raise ValidationError("Промпт слишком большой (максимум 100KB)")
        
        return content
    
    @staticmethod
    def validate_prompt_file(filepath: str) -> str:
        """
        Проверить файл промпта
        
        Args:
            filepath: Путь к файлу промпта
            
        Returns:
            Валидный путь к файлу
        """
        path = PathValidator.validate_file(filepath, ['.txt', '.md'])
        
        # Проверка размера файла
        file_size = Path(path).stat().st_size
        if file_size > 100000:  # 100KB
            raise ValidationError(f"Файл промпта слишком большой: {file_size} байт")
        
        return path


class ValidationManager:
    """Менеджер валидации"""
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Полная валидация конфигурации
        
        Args:
            config: Словарь конфигурации
            
        Returns:
            Валидированная конфигурация
        """
        validated = config.copy()
        
        # Валидация модели
        if 'model' in validated:
            validated['model'] = ConfigValidator.validate_model_name(validated['model'])
        
        # Валидация итераций
        if 'iterations' in validated:
            validated['iterations'] = ConfigValidator.validate_iterations(validated['iterations'])
        
        # Валидация задержек
        if 'delays' in validated and isinstance(validated['delays'], dict):
            delays = validated['delays'].copy()
            for delay_name, delay_value in delays.items():
                delays[delay_name] = ConfigValidator.validate_delay(delay_value, delay_name)
            validated['delays'] = delays
        
        # Валидация горячих клавиш
        if 'hotkeys' in validated:
            validated['hotkeys'] = ConfigValidator.validate_hotkeys(validated['hotkeys'])
        
        # Валидация папок
        if 'prompts_folder' in validated and validated['prompts_folder']:
            validated['prompts_folder'] = PathValidator.validate_directory(validated['prompts_folder'])
        
        if 'work_folders' in validated and isinstance(validated['work_folders'], list):
            work_folders = []
            for folder in validated['work_folders']:
                if folder:  # Пропускаем пустые строки
                    work_folders.append(PathValidator.validate_directory(folder))
            validated['work_folders'] = work_folders
        
        return validated
