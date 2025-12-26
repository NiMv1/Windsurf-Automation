"""Основные сущности Windsurf Automation."""

from __future__ import annotations

import json
import logging
import os
import time
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

try:
    import pyautogui
    import pyperclip
    AUTOMATION_AVAILABLE = True
except ImportError:  # pragma: no cover - внешние зависимости
    AUTOMATION_AVAILABLE = False

try:
    import win32gui
    import win32con
    WIN32_AVAILABLE = True
except ImportError:  # pragma: no cover
    WIN32_AVAILABLE = False

logger = logging.getLogger('WA')


@dataclass
class Config:
    """Работа с конфигурационным файлом."""

    path: str = "config.json"
    data: Dict = field(default_factory=dict)

    DEFAULT = {
        "model": "claude-3.5-sonnet",
        "iterations": 1,
        "work_folders": [],
        "prompts_folder": "",
        "delays": {
            "cascade_warmup": 25,
            "after_hotkey": 0.5,
            "after_paste": 0.3,
            "between_messages": 2,
        },
        "hotkeys": {
            "new_window": ["ctrl", "shift", "n"],
            "open_cascade": ["ctrl", "l"],
            "select_model": ["ctrl", "/"],
            "send": ["enter"],
        },
    }

    def __post_init__(self):
        self.data = self.load()

    def load(self) -> Dict:
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    loaded = self._migrate_legacy(loaded)
                    return self._deep_merge(self.DEFAULT, loaded)
            except Exception as e:  # pragma: no cover - логирование
                logger.error(f"Ошибка загрузки конфига: {e}")
        return deepcopy(self.DEFAULT)

    def save(self):
        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:  # pragma: no cover - логирование
            logger.error(f"Ошибка сохранения конфига: {e}")

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def set(self, key: str, value):
        self.data[key] = value
        self.save()

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        result = deepcopy(base)
        for key, value in override.items():
            if isinstance(value, dict) and isinstance(result.get(key), dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _migrate_legacy(self, data: Dict) -> Dict:
        if not isinstance(data, dict):
            return {}

        migrated = dict(data)
        if "delay" in migrated:
            delays = migrated.get("delays") or {}
            if "between_messages" not in delays:
                delays["between_messages"] = migrated["delay"]
                migrated["delays"] = delays
                logger.info("Сконвертировано устаревшее поле delay -> delays.between_messages")
            migrated.pop("delay", None)

        return migrated


class WindsurfController:
    """Контроллер для управления IDE."""

    def __init__(self, config: Config):
        self.config = config
        self.running = False

    def find_windsurf_windows(self) -> List[Dict]:
        if not WIN32_AVAILABLE:
            return []

        windows: List[Dict] = []

        def callback(hwnd, results):  # pragma: no cover - win32 зависимость
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "windsurf" in title.lower() and "browser" not in title.lower():
                    results.append({"hwnd": hwnd, "title": title[:60] + "..." if len(title) > 60 else title})
            return True

        win32gui.EnumWindows(callback, windows)
        return windows

    def activate_window(self, hwnd: int) -> bool:
        if not WIN32_AVAILABLE:
            return False
        try:
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.3)
            return True
        except Exception as e:  # pragma: no cover - win32 зависимость
            logger.error(f"Ошибка активации окна: {e}")
            return False

    def press_hotkey(self, keys: List[str]):
        if not AUTOMATION_AVAILABLE:
            return
        pyautogui.hotkey(*keys)
        time.sleep(self.config.get("delays", {}).get("after_hotkey", 0.5))

    def paste_text(self, text: str):
        if not AUTOMATION_AVAILABLE:
            return
        pyperclip.copy(text)
        time.sleep(0.1)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(self.config.get("delays", {}).get("after_paste", 0.3))

    def open_new_window(self):
        logger.info("Открытие нового окна (Ctrl+Shift+N)...")
        self.press_hotkey(self.config.get("hotkeys", {}).get("new_window", ["ctrl", "shift", "n"]))

    def open_cascade(self):
        logger.info("Открытие Cascade (Ctrl+L)...")
        self.press_hotkey(self.config.get("hotkeys", {}).get("open_cascade", ["ctrl", "l"]))

    def select_model(self, model_name: str):
        logger.info(f"Выбор модели: {model_name}")
        self.press_hotkey(self.config.get("hotkeys", {}).get("select_model", ["ctrl", "/"]))
        time.sleep(0.5)
        self.paste_text(model_name)
        time.sleep(0.3)
        pyautogui.press("down")
        time.sleep(0.2)
        pyautogui.press("enter")
        time.sleep(0.5)

    def send_message(self, message: str):
        logger.info(f"Отправка сообщения ({len(message)} символов)...")
        self.open_cascade()
        time.sleep(0.3)
        self.paste_text(message)
        self.press_hotkey(self.config.get("hotkeys", {}).get("send", ["enter"]))

    def start_session(self, hwnd: Optional[int] = None, model: Optional[str] = None) -> bool:
        self.running = True
        model = model or self.config.get("model", "claude-3.5-sonnet")
        warmup_time = self.config.get("delays", {}).get("cascade_warmup", 20)

        try:
            if hwnd:
                logger.info("Активация окна Windsurf...")
                if not self.activate_window(hwnd):
                    logger.error("Не удалось активировать окно")
                    return False
                if not self.running:
                    logger.info("Запуск прерван пользователем")
                    return False

            self.open_new_window()
            time.sleep(2)
            if not self.running:
                logger.info("Запуск новой сессии остановлен")
                return False

            self.open_cascade()
            logger.info(f"Ожидание прогрева Cascade ({warmup_time} сек)...")
            waited = 0
            while waited < warmup_time:
                if not self.running:
                    logger.info("Прогрев Cascade прерван пользователем")
                    return False
                time.sleep(0.5)
                waited += 0.5

            if not self.running:
                logger.info("Выбор модели отменён")
                return False

            self.select_model(model)
            logger.info("Сессия готова к работе!")
            return True

        except Exception as e:  # pragma: no cover - логирование
            logger.error(f"Ошибка запуска сессии: {e}")
            return False
        finally:
            self.running = False

    def stop(self):
        self.running = False
        logger.info("Выполнение остановлено вручную")
