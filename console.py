"""
Windsurf Automation - Главный исполнительный файл
Простой UI для управления автоматизацией
"""

import sys
import os
import json
import time

# Добавляем путь к src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from windsurf_automation import WindsurfAutomation, find_windsurf_windows

# Цвета для консоли (Windows)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def clear_screen():
    """Очистка экрана"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """Вывод заголовка"""
    print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║                   WINDSURF AUTOMATION                        ║
║                        v0.2.0                                ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}
""")


def print_warning():
    """Предупреждение о текущем режиме работы"""
    print(f"""{Colors.WARNING}
⚠️  ВНИМАНИЕ! Текущий режим работы:
    1. Открывается новое окно Windsurf
    2. Нужно ВРУЧНУЮ выбрать модель (Free: SWE-1, GPT-5.1-Codex, Grok)
    3. После выполнения задачи окно закрывается
    
    Автоматический выбор модели пока не реализован!
{Colors.END}""")


def load_tasks():
    """Загрузка задач из файла"""
    tasks_file = os.path.join(os.path.dirname(__file__), 'tasks', 'tasks.json')
    if os.path.exists(tasks_file):
        with open(tasks_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"tasks": [], "models": {"free": [], "default": "SWE-1"}}


def save_tasks(data):
    """Сохранение задач в файл"""
    tasks_file = os.path.join(os.path.dirname(__file__), 'tasks', 'tasks.json')
    with open(tasks_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def show_tasks(data):
    """Показать список задач"""
    tasks = data.get('tasks', [])
    if not tasks:
        print(f"\n{Colors.CYAN}📋 Список задач пуст{Colors.END}")
        return
    
    print(f"\n{Colors.CYAN}📋 Список задач:{Colors.END}")
    print("-" * 60)
    for task in tasks:
        status_icon = "✅" if task['status'] == 'completed' else "⏳" if task['status'] == 'in_progress' else "📌"
        print(f"  {status_icon} [{task['id']}] {task['title']}")
        print(f"      Модель: {task['model']} | Приоритет: {task['priority']}")
        print(f"      Промпт: {task['prompt'][:50]}...")
        print()


def add_task(data):
    """Добавить новую задачу"""
    print(f"\n{Colors.GREEN}➕ Добавление новой задачи{Colors.END}")
    
    title = input("  Название: ").strip()
    if not title:
        print(f"{Colors.FAIL}❌ Название не может быть пустым{Colors.END}")
        return
    
    prompt = input("  Промпт для ИИ: ").strip()
    if not prompt:
        print(f"{Colors.FAIL}❌ Промпт не может быть пустым{Colors.END}")
        return
    
    models = data.get('models', {}).get('free', ['SWE-1'])
    print(f"  Доступные модели: {', '.join(models)}")
    model = input(f"  Модель [{models[0]}]: ").strip() or models[0]
    
    priority = input("  Приоритет (low/medium/high) [medium]: ").strip() or "medium"
    
    # Генерируем ID
    tasks = data.get('tasks', [])
    new_id = max([t['id'] for t in tasks], default=0) + 1
    
    new_task = {
        "id": new_id,
        "title": title,
        "prompt": prompt,
        "model": model,
        "status": "pending",
        "priority": priority,
        "created": time.strftime("%Y-%m-%d")
    }
    
    tasks.append(new_task)
    data['tasks'] = tasks
    save_tasks(data)
    
    print(f"\n{Colors.GREEN}✅ Задача #{new_id} добавлена!{Colors.END}")


def run_task(data, wa):
    """Выполнить задачу"""
    tasks = [t for t in data.get('tasks', []) if t['status'] == 'pending']
    
    if not tasks:
        print(f"\n{Colors.WARNING}⚠️ Нет задач для выполнения{Colors.END}")
        return
    
    print(f"\n{Colors.CYAN}📋 Задачи для выполнения:{Colors.END}")
    for t in tasks:
        print(f"  [{t['id']}] {t['title']} ({t['model']})")
    
    task_id = input("\n  Введите ID задачи (или Enter для первой): ").strip()
    
    if task_id:
        task = next((t for t in tasks if t['id'] == int(task_id)), None)
    else:
        task = tasks[0]
    
    if not task:
        print(f"{Colors.FAIL}❌ Задача не найдена{Colors.END}")
        return
    
    print(f"\n{Colors.CYAN}🚀 Выполнение задачи #{task['id']}: {task['title']}{Colors.END}")
    print_warning()
    
    input("\n  Нажмите Enter когда будете готовы...")
    
    # Выполняем
    print("\n  1️⃣ Открываю новое окно...")
    if not wa.open_new_window():
        print(f"{Colors.FAIL}❌ Не удалось открыть окно{Colors.END}")
        return
    
    print("  2️⃣ Открываю Cascade sidebar...")
    time.sleep(1)
    if not wa.open_sidebar():
        print(f"{Colors.FAIL}❌ Не удалось открыть sidebar{Colors.END}")
        return
    
    print(f"\n{Colors.WARNING}  ⚠️ ВЫБЕРИТЕ МОДЕЛЬ: {task['model']}{Colors.END}")
    input("  Нажмите Enter после выбора модели...")
    
    print("  3️⃣ Отправляю промпт...")
    if not wa.send_message(task['prompt']):
        print(f"{Colors.FAIL}❌ Не удалось отправить промпт{Colors.END}")
        return
    
    print(f"\n{Colors.GREEN}✅ Задача отправлена на выполнение!{Colors.END}")
    
    # Обновляем статус
    for t in data['tasks']:
        if t['id'] == task['id']:
            t['status'] = 'in_progress'
    save_tasks(data)


def quick_run(wa):
    """Быстрый запуск - открыть окно и sidebar"""
    print(f"\n{Colors.CYAN}🚀 Быстрый запуск{Colors.END}")
    print_warning()
    
    input("\n  Нажмите Enter для запуска...")
    
    print("\n  1️⃣ Открываю новое окно...")
    if not wa.open_new_window():
        print(f"{Colors.FAIL}❌ Не удалось открыть окно{Colors.END}")
        return
    
    print("  2️⃣ Открываю Cascade sidebar...")
    time.sleep(1)
    wa.open_sidebar()
    
    print(f"\n{Colors.GREEN}✅ Готово! Выберите модель и начинайте работу.{Colors.END}")


def show_windows(wa):
    """Показать окна Windsurf"""
    windows = find_windsurf_windows(ide_only=True)
    print(f"\n{Colors.CYAN}🪟 Окна Windsurf IDE:{Colors.END}")
    if not windows:
        print("  Нет открытых окон")
        return
    
    for i, (hwnd, title) in enumerate(windows):
        marker = " ← текущее" if hwnd == wa.hwnd else ""
        print(f"  [{i}] {title[:60]}...{marker}")


def main_menu():
    """Главное меню"""
    clear_screen()
    print_header()
    
    wa = WindsurfAutomation()
    data = load_tasks()
    
    # Инициализация - найти окно Windsurf
    windows = find_windsurf_windows(ide_only=True)
    if windows:
        wa.hwnd, wa.title = windows[0]
        print(f"{Colors.GREEN}✅ Windsurf найден: {wa.title[:50]}...{Colors.END}")
    else:
        print(f"{Colors.WARNING}⚠️ Windsurf не найден. Откройте IDE.{Colors.END}")
    
    while True:
        print(f"""
{Colors.BOLD}═══════════════════════════════════════════════════════════════{Colors.END}
  {Colors.CYAN}[1]{Colors.END} 🚀 Быстрый запуск (новое окно + sidebar)
  {Colors.CYAN}[2]{Colors.END} 📋 Показать задачи
  {Colors.CYAN}[3]{Colors.END} ➕ Добавить задачу
  {Colors.CYAN}[4]{Colors.END} ▶️  Выполнить задачу
  {Colors.CYAN}[5]{Colors.END} 🪟 Показать окна Windsurf
  {Colors.CYAN}[6]{Colors.END} 🔄 Обновить подключение
  {Colors.CYAN}[0]{Colors.END} ❌ Выход
{Colors.BOLD}═══════════════════════════════════════════════════════════════{Colors.END}""")
        
        choice = input(f"\n{Colors.CYAN}>{Colors.END} Выбор: ").strip()
        
        if choice == "0":
            print(f"\n{Colors.CYAN}👋 До свидания!{Colors.END}\n")
            break
        elif choice == "1":
            quick_run(wa)
        elif choice == "2":
            show_tasks(data)
        elif choice == "3":
            add_task(data)
            data = load_tasks()  # Перезагрузить
        elif choice == "4":
            run_task(data, wa)
            data = load_tasks()
        elif choice == "5":
            show_windows(wa)
        elif choice == "6":
            windows = find_windsurf_windows(ide_only=True)
            if windows:
                wa.hwnd, wa.title = windows[0]
                print(f"{Colors.GREEN}✅ Подключено: {wa.title[:50]}...{Colors.END}")
            else:
                print(f"{Colors.WARNING}⚠️ Windsurf не найден{Colors.END}")
        else:
            print(f"{Colors.FAIL}❌ Неверный выбор{Colors.END}")
        
        input(f"\n{Colors.CYAN}Нажмите Enter для продолжения...{Colors.END}")
        clear_screen()
        print_header()


if __name__ == "__main__":
    # Включаем поддержку ANSI цветов в Windows
    os.system('')
    main_menu()
