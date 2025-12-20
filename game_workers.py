"""
Game Workers - Рабочие GPT для создания игры мечты (slime-rpg)
Автоматически открывает окна Windsurf и отправляет задачи рабочим
"""

import sys
import os
import time
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from windsurf_automation import find_windsurf_windows, activate_window_by_hwnd, get_all_windows
import keyboard
import pyperclip

# Путь к проекту игры
GAME_PROJECT = r"C:\Users\bnex4\Documents\slime-rpg"

# Модель для рабочих
WORKER_MODEL = "GPT-5.1-Codex"

# Задачи для улучшения игры slime-rpg
GAME_TASKS = [
    {
        "id": 1,
        "title": "Новый враг - Огненный элементаль",
        "prompt": f"""Проект: {GAME_PROJECT}

ЗАДАЧА: Создай нового врага "Огненный элементаль" для игры slime-rpg на Godot 4.

ТРЕБОВАНИЯ:
1. Создай файл game/enemies/fire_elemental.gd
2. Наследуй от базового врага (если есть) или CharacterBody2D
3. Способности:
   - Огненный шар (дальняя атака)
   - Взрыв при смерти (AOE урон)
   - Иммунитет к огню, слабость к воде
4. Визуал: красно-оранжевый цвет, анимация пламени
5. Комментарии на русском

ОТЧЁТ:
## Сделано
## Проблемы"""
    },
    {
        "id": 2,
        "title": "Новая способность - Ледяной щит",
        "prompt": f"""Проект: {GAME_PROJECT}

ЗАДАЧА: Создай новую способность "Ледяной щит" для игрока.

ТРЕБОВАНИЯ:
1. Добавь в систему способностей (game/abilities/)
2. Эффект: создаёт щит на 5 секунд, поглощает 50 урона
3. Замедляет врагов при касании на 30%
4. Кулдаун: 15 секунд
5. Элемент: Лёд (синергия с водой)
6. Комментарии на русском

ОТЧЁТ:
## Сделано
## Проблемы"""
    },
    {
        "id": 3,
        "title": "Улучшение UI - Панель здоровья босса",
        "prompt": f"""Проект: {GAME_PROJECT}

ЗАДАЧА: Создай красивую панель здоровья для боссов.

ТРЕБОВАНИЯ:
1. Создай scenes/ui/boss_health_bar.tscn и скрипт
2. Большая полоса HP вверху экрана
3. Имя босса над полосой
4. Анимация при получении урона (тряска, красная вспышка)
5. Фазы босса (разные цвета при 75%, 50%, 25% HP)
6. Комментарии на русском

ОТЧЁТ:
## Сделано
## Проблемы"""
    },
    {
        "id": 4,
        "title": "Новая локация - Вулканическая пещера",
        "prompt": f"""Проект: {GAME_PROJECT}

ЗАДАЧА: Создай новую локацию "Вулканическая пещера".

ТРЕБОВАНИЯ:
1. Создай scenes/levels/volcanic_cave.tscn
2. Опасности: лавовые ямы (урон при касании), падающие камни
3. Враги: огненные элементали, лавовые слизни
4. Босс в конце: Лорд Пламени
5. Визуал: тёмно-красный, оранжевое свечение лавы
6. Комментарии на русском

ОТЧЁТ:
## Сделано
## Проблемы"""
    },
    {
        "id": 5,
        "title": "Система достижений",
        "prompt": f"""Проект: {GAME_PROJECT}

ЗАДАЧА: Создай систему достижений для игры.

ТРЕБОВАНИЯ:
1. Создай game/core/achievement_system.gd (Autoload)
2. Достижения:
   - "Первая кровь" - убить первого врага
   - "Поглотитель" - поглотить 10 способностей
   - "Богач" - накопить 1000 золота
   - "Исследователь" - посетить все локации
3. UI уведомление при получении достижения
4. Сохранение в SaveSystem
5. Комментарии на русском

ОТЧЁТ:
## Сделано
## Проблемы"""
    }
]


def find_my_window():
    """Найти моё окно (Boss)"""
    windows = find_windsurf_windows(ide_only=False)
    for h, t in windows:
        if "CascadeProjects" in t or "Windsurf-Automation" in t:
            return h, t
    return None, None


def find_worker_windows():
    """Найти рабочие окна (с проектом slime-rpg)"""
    all_windows = get_all_windows()
    workers = []
    
    for h, t in all_windows:
        # Пропускаем браузерные окна
        if "Яндекс" in t or "Chrome" in t or "Подписка" in t or "Usage" in t:
            continue
        # Ищем окна с проектом slime-rpg
        if "slime-rpg" in t.lower() or "slime_rpg" in t.lower():
            workers.append((h, t))
    
    return workers


def open_new_window_with_project():
    """Открыть новое окно Windsurf с проектом slime-rpg"""
    print("📂 Открываю новое окно с проектом slime-rpg...")
    
    # Находим любое окно Windsurf
    windows = find_windsurf_windows(ide_only=True)
    if not windows:
        print("❌ Windsurf не найден!")
        return None
    
    hwnd, title = windows[0]
    activate_window_by_hwnd(hwnd)
    time.sleep(0.5)
    
    # Открываем новое окно
    keyboard.send('ctrl+shift+n')
    time.sleep(3)
    
    # Находим новое пустое окно
    all_win = get_all_windows()
    new_hwnd = None
    for h, t in all_win:
        if t == "Windsurf" or t == "Welcome - Windsurf":
            new_hwnd = h
            break
    
    if not new_hwnd:
        print("⚠️ Новое окно не найдено")
        return None
    
    # Открываем проект в новом окне
    activate_window_by_hwnd(new_hwnd)
    time.sleep(0.5)
    
    keyboard.send('ctrl+o')
    time.sleep(1.5)
    
    keyboard.send('alt+d')
    time.sleep(0.3)
    pyperclip.copy(GAME_PROJECT)
    keyboard.send('ctrl+v')
    time.sleep(0.3)
    keyboard.send('enter')
    time.sleep(1)
    keyboard.send('enter')  # Select Folder
    time.sleep(2)
    keyboard.send('enter')  # Trust authors
    time.sleep(3)
    
    print(f"✅ Окно с проектом slime-rpg открыто")
    return new_hwnd


def send_task_to_worker(hwnd, task):
    """Отправить задачу рабочему"""
    print(f"\n📤 Отправляю задачу #{task['id']}: {task['title']}...")
    
    activate_window_by_hwnd(hwnd)
    time.sleep(0.5)
    
    # Ctrl+L - открыть Cascade
    keyboard.send('ctrl+l')
    time.sleep(1.5)
    
    # Ctrl+/ - выбор модели
    keyboard.send('ctrl+/')
    time.sleep(0.8)
    pyperclip.copy(WORKER_MODEL)
    keyboard.send('ctrl+v')
    time.sleep(0.3)
    keyboard.send('enter')
    time.sleep(0.5)
    
    # Вставляем задачу
    pyperclip.copy(task['prompt'])
    keyboard.send('ctrl+v')
    time.sleep(0.3)
    
    # Enter - отправить
    keyboard.send('enter')
    time.sleep(0.5)
    
    print(f"   ✅ Задача отправлена!")
    return True


def main():
    print("=" * 60)
    print("🎮 GAME WORKERS - СОЗДАНИЕ ИГРЫ МЕЧТЫ")
    print("=" * 60)
    print(f"\n📁 Проект: {GAME_PROJECT}")
    print(f"🤖 Модель: {WORKER_MODEL}")
    print(f"📋 Задач: {len(GAME_TASKS)}")
    
    # Находим своё окно
    my_hwnd, my_title = find_my_window()
    if my_hwnd:
        print(f"\n👔 Моё окно (Boss): {my_title[:40]}...")
    
    # Находим рабочие окна
    workers = find_worker_windows()
    print(f"\n🔧 Найдено рабочих окон с slime-rpg: {len(workers)}")
    
    # Если нет рабочих окон - открываем новые
    if len(workers) < len(GAME_TASKS):
        needed = min(len(GAME_TASKS), 3) - len(workers)  # Максимум 3 рабочих
        print(f"\n📂 Нужно открыть {needed} новых окон...")
        
        for i in range(needed):
            print(f"\n   Открываю окно {i+1}/{needed}...")
            new_hwnd = open_new_window_with_project()
            if new_hwnd:
                workers.append((new_hwnd, "slime-rpg"))
            time.sleep(2)
    
    # Обновляем список рабочих
    workers = find_worker_windows()
    print(f"\n🔧 Рабочих окон: {len(workers)}")
    
    if not workers:
        print("\n❌ Нет рабочих окон!")
        print("   Открой вручную окна Windsurf с проектом slime-rpg:")
        print(f"   File -> Open Folder -> {GAME_PROJECT}")
        return
    
    print("\n⚠️ Через 3 сек начну отправлять задачи!")
    print("   Не трогай мышь и клавиатуру...")
    time.sleep(3)
    
    # Отправляем задачи рабочим
    tasks_sent = 0
    for i, (hwnd, title) in enumerate(workers):
        if i >= len(GAME_TASKS):
            break
        
        task = GAME_TASKS[i]
        print(f"\n{'='*40}")
        print(f"🔧 Рабочий #{i+1}: {title[:30]}...")
        
        if send_task_to_worker(hwnd, task):
            tasks_sent += 1
        
        time.sleep(1)
    
    # Возвращаем фокус боссу
    if my_hwnd:
        print(f"\n   Возвращаю фокус в моё окно...")
        activate_window_by_hwnd(my_hwnd)
    
    print("\n" + "=" * 60)
    print(f"✅ Задачи отправлены {tasks_sent} рабочим!")
    print("=" * 60)
    print("\n🎮 GPT рабочие создают игру мечты!")
    print("   Проверяй изменения: git diff")
    print(f"   Проект: {GAME_PROJECT}")


if __name__ == "__main__":
    main()
