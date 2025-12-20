# Windsurf Automation v1.2.3

Автоматизация Windsurf IDE для итеративных задач с бесплатными ИИ моделями.

## ✅ Возможности

- **Управление окнами** - Открытие новых окон Windsurf
- **Отправка промптов** - Автоматическая вставка в Cascade чат
- **Очередь задач** - Выполнение задач последовательно
- **Современный GUI** - Тёмная тема, удобное управление
- **Логирование** - DEBUG/INFO уровни в `logs/`
- **Кнопка теста** - Запуск tests/auto_test.py из GUI
- **Прогресс-бар** - Визуализация выполнения задач
- **Звуковые уведомления** - При завершении задачи
- **Конфигурация** - Настройки в config.json
- **Boss/Worker система** - Управление GPT рабочими

## ⚠️ Ограничения

- Автоматическое открытие окон нестабильно на мульти-мониторе
- Рекомендуется открывать рабочие окна вручную

## 🎯 Purpose

This tool helps offload routine tasks from your main AI by automating interactions with Windsurf IDE using free AI models:
- **SWE-1**
- **GPT-5.1-Codex**
- **Grok Code Fast 1**
- Other models when free access promotions are available

## 🚀 Capabilities

### ✅ Window & Chat Automation
- Open new Windsurf window (`Ctrl+Shift+N`)
- Open Cascade sidebar (`Ctrl+L`)
- Send prompts to chat

### ✅ Task Management
- Task list in `tasks/tasks.json`
- Add, view, and execute tasks
- Run all tasks in queue
- Track task status

### ✅ Model Selection
- Automatic model selection via `Ctrl+/`
- Support for free models

## 📁 Project Structure

```
Windsurf-Automation/
├── gui.py              # Modern GUI (recommended)
├── boss.py             # Boss/Worker system for GPT management
├── hire_workers.py     # Send tasks to multiple windows
├── quick_task.py       # Quick task sender
├── self_improve.py     # Self-improvement system
├── config.json         # Settings
├── CHANGELOG.md        # Version history
├── run.bat             # Quick launcher
├── requirements.txt    # Dependencies
├── src/
│   ├── windsurf_automation.py  # Core automation
│   └── config.py       # Config loader
├── tasks/
│   └── tasks.json      # Task list
├── logs/               # Log files (DEBUG level)
└── tests/
    ├── auto_test.py    # Automated tests
    └── test_automation.py
```

## 🛠️ Requirements

- Python 3.10+
- Windows 10/11
- Windsurf IDE installed

## 📦 Installation

```bash
git clone https://github.com/NiMv1/Windsurf-Automation.git
cd Windsurf-Automation
pip install -r requirements.txt
```

## 🔧 Usage

### GUI (Recommended)
```bash
python gui.py
```
Or double-click `run.bat`

### Console Mode
```bash
python run.py
```

### Features:
- **Quick Run** - Open new window + sidebar
- **Task Management** - Add, view, execute tasks
- **Window Selection** - Choose which Windsurf window to control
- **Message Sending** - Send prompts to Cascade chat

## 📋 Roadmap

- [x] **F1**: Basic window and chat automation
- [x] **F2**: Model selection automation
- [x] **F3**: Task queue system
- [ ] **F4**: Project improvement suggestions
- [ ] **F5**: Auto-detect task completion

## 📄 License

MIT License
