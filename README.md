# Windsurf Automation v2.0.0

🧠 **Самоулучшающаяся система** для автоматизации Windsurf IDE с бесплатными ИИ моделями.

## 🎯 Основные возможности

### ✅ Автоматизация Windsurf
- **Умный поиск окна** - Находит Windsurf, игнорируя браузеры и проводник
- **Отправка промптов** - Автоматическая вставка в Cascade чат
- **Очередь задач** - Выполнение задач последовательно
- **GUI настройки** - Захват координат и горячих клавиш

### 🧠 AI Brain (Новое!)
- **Самоанализ** - Программа анализирует свой код и находит улучшения
- **Планирование** - Автоматическое создание задач
- **Память** - Краткосрочная и долгосрочная память
- **Обучение** - Учится на результатах выполнения

### 🐙 GitHub автоматизация
- **Поиск issues** - Находит "good first issue" для PR
- **Создание PR** - Автоматическое создание pull requests
- **Ответы на ревью** - Обработка комментариев ревьюеров

### 🎮 Разработка проектов
- **Игры** - Поддержка разработки игр
- **Сайты** - Веб-разработка
- **Приложения** - Любые проекты

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
├── gui.py                    # Modern GUI (recommended)
├── boss.py                   # Boss/Worker system
├── self_improve.py           # Self-improvement runner
├── config.json               # Settings
├── windsurf_config.json      # Windsurf coordinates & hotkeys
├── memory.db                 # AI Brain memory (SQLite)
├── CHANGELOG.md              # Version history
├── run.bat                   # Quick launcher
├── requirements.txt          # Dependencies
├── src/
│   ├── ai_brain.py           # 🧠 AI Brain - мозг системы
│   ├── window_finder.py      # 🔍 Умный поиск окна Windsurf
│   ├── windsurf_config_gui.py # ⚙️ GUI настройки координат
│   ├── windsurf_automation.py # Core automation
│   └── config.py             # Config loader
├── docs/
│   └── SELF_IMPROVEMENT_ARCHITECTURE.md  # Архитектура системы
├── tasks/
│   └── tasks.json            # Task list
├── logs/                     # Log files
└── tests/
    └── auto_test.py          # Automated tests
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
