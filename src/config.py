"""
Модуль конфигурации WA
Загрузка и сохранение настроек из config.json
"""

import os
import json
import logging

logger = logging.getLogger('WA')

# Путь к файлу конфигурации
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')

# Настройки по умолчанию
DEFAULT_CONFIG = {
    "model": "GPT-5.1-Codex",
    "delay": 2,
    "sound_enabled": True,
    "auto_commit": False,
    "log_level": "DEBUG",
    "project_path": os.path.dirname(os.path.dirname(__file__))
}


def load_config() -> dict:
    """Загрузить конфигурацию из config.json
    
    Returns:
        dict: Словарь с настройками
    """
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logger.debug(f"Config loaded from {CONFIG_FILE}")
                return config
        else:
            logger.warning(f"Config file not found, using defaults")
            save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> bool:
    """Сохранить конфигурацию в config.json
    
    Args:
        config: Словарь с настройками
        
    Returns:
        bool: True если успешно сохранено
    """
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        logger.debug(f"Config saved to {CONFIG_FILE}")
        return True
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False


def get_setting(key: str, default=None):
    """Получить значение настройки
    
    Args:
        key: Ключ настройки
        default: Значение по умолчанию если ключ не найден
        
    Returns:
        Значение настройки или default
    """
    config = load_config()
    return config.get(key, default)


def set_setting(key: str, value) -> bool:
    """Установить значение настройки
    
    Args:
        key: Ключ настройки
        value: Новое значение
        
    Returns:
        bool: True если успешно сохранено
    """
    config = load_config()
    config[key] = value
    return save_config(config)


# Удобные функции для частых настроек
def get_model() -> str:
    """Получить текущую модель"""
    return get_setting('model', 'GPT-5.1-Codex')


def get_delay() -> int:
    """Получить задержку между действиями"""
    return get_setting('delay', 2)


def is_sound_enabled() -> bool:
    """Проверить включён ли звук"""
    return get_setting('sound_enabled', True)


def get_project_path() -> str:
    """Получить путь к проекту"""
    return get_setting('project_path', os.path.dirname(os.path.dirname(__file__)))
