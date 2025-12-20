# Windsurf Automation

Automation tool for Windsurf IDE to help with iterative coding tasks using free AI models.

## ⚠️ Current Mode

**Manual model selection required!**
1. WA opens a new Windsurf window
2. You manually select a FREE model (SWE-1, GPT-5.1-Codex, Grok Code Fast 1)
3. WA sends the prompt and closes the window after completion

Automatic model selection is planned for future releases.

## 🎯 Purpose

This tool helps offload routine tasks from your main AI by automating interactions with Windsurf IDE using free AI models:
- **SWE-1**
- **GPT-5.1-Codex**
- **Grok Code Fast 1**
- Other models when free access promotions are available

## 🚀 Features

### ✅ Feature 1: Window & Chat Automation (Working)
- Open new Windsurf window (`Ctrl+Shift+N`)
- Open Cascade sidebar (`Ctrl+L`)
- Send prompts to chat

### 🔄 Feature 2: Task Management (In Progress)
- Task list in `tasks/tasks.json`
- Add, view, and execute tasks
- Track task status

### 📋 Feature 3: Model Selection (Planned)
- Automatic model selection
- Model availability checking

## 📁 Project Structure

```
Windsurf-Automation/
├── run.py              # Main UI launcher
├── requirements.txt    # Dependencies
├── src/
│   └── windsurf_automation.py  # Core automation
├── tasks/
│   └── tasks.json      # Task list
└── tests/
    └── test_automation.py  # Tests
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

```bash
python run.py
```

Then use the menu:
1. **Quick Run** - Open new window + sidebar
2. **Show Tasks** - View task list
3. **Add Task** - Create new task
4. **Run Task** - Execute a task
5. **Show Windows** - List Windsurf windows

## 📋 Roadmap

- [x] **F1**: Basic window and chat automation
- [ ] **F2**: Model selection automation
- [ ] **F3**: Iteration management system
- [ ] **F4**: Project improvement suggestions

## 📄 License

MIT License
