"""
AI Brain - Модуль для самоанализа и самоулучшения кода.
Использует Groq API (бесплатный) или Ollama (локальный).
"""

import json
import os
import re
import subprocess
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import logging

logger = logging.getLogger('WA.AIBrain')

# Попытка импорта HTTP клиента
try:
    import httpx
    HTTP_AVAILABLE = True
except ImportError:
    try:
        import requests as httpx
        HTTP_AVAILABLE = True
    except ImportError:
        HTTP_AVAILABLE = False


@dataclass
class Task:
    """Задача для улучшения"""
    id: str
    title: str
    description: str
    priority: int  # 1-5, где 5 - высший
    status: str  # pending, in_progress, completed, failed
    file_path: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    result: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "file_path": self.file_path,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "result": self.result
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        return cls(**data)


@dataclass
class ImprovementResult:
    """Результат улучшения"""
    success: bool
    task: Task
    changes_made: List[str]
    tests_passed: bool
    error: Optional[str] = None
    duration_seconds: float = 0.0


class CodeAnalyzer:
    """Анализатор кода для поиска улучшений"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
    
    def get_python_files(self) -> List[str]:
        """Получить список Python файлов"""
        files = []
        for root, _, filenames in os.walk(self.project_path):
            # Пропускаем служебные папки
            if any(skip in root for skip in ['.git', '__pycache__', 'venv', '.venv', 'node_modules']):
                continue
            for filename in filenames:
                if filename.endswith('.py'):
                    files.append(os.path.join(root, filename))
        return files
    
    def analyze_file(self, filepath: str) -> Dict:
        """Анализ одного файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {"error": str(e)}
        
        lines = content.split('\n')
        
        return {
            "path": filepath,
            "lines": len(lines),
            "size_bytes": len(content),
            "has_docstring": '"""' in content or "'''" in content,
            "has_type_hints": ': ' in content and '->' in content,
            "imports_count": len([l for l in lines if l.strip().startswith('import') or l.strip().startswith('from')]),
            "functions_count": len(re.findall(r'^\s*def\s+\w+', content, re.MULTILINE)),
            "classes_count": len(re.findall(r'^\s*class\s+\w+', content, re.MULTILINE)),
            "todo_count": len(re.findall(r'#\s*TODO', content, re.IGNORECASE)),
            "fixme_count": len(re.findall(r'#\s*FIXME', content, re.IGNORECASE)),
            "long_lines": len([l for l in lines if len(l) > 120]),
            "empty_except": len(re.findall(r'except\s*:', content)),
        }
    
    def get_project_stats(self) -> Dict:
        """Статистика по всему проекту"""
        files = self.get_python_files()
        stats = {
            "total_files": len(files),
            "total_lines": 0,
            "total_size": 0,
            "total_functions": 0,
            "total_classes": 0,
            "total_todos": 0,
            "files_without_docstrings": 0,
            "files_without_type_hints": 0,
            "issues": []
        }
        
        for filepath in files:
            analysis = self.analyze_file(filepath)
            if "error" in analysis:
                continue
            
            stats["total_lines"] += analysis["lines"]
            stats["total_size"] += analysis["size_bytes"]
            stats["total_functions"] += analysis["functions_count"]
            stats["total_classes"] += analysis["classes_count"]
            stats["total_todos"] += analysis["todo_count"]
            
            if not analysis["has_docstring"]:
                stats["files_without_docstrings"] += 1
            if not analysis["has_type_hints"]:
                stats["files_without_type_hints"] += 1
            
            # Собираем проблемы
            if analysis["empty_except"] > 0:
                stats["issues"].append(f"{filepath}: {analysis['empty_except']} пустых except блоков")
            if analysis["long_lines"] > 5:
                stats["issues"].append(f"{filepath}: {analysis['long_lines']} строк длиннее 120 символов")
            if analysis["todo_count"] > 0:
                stats["issues"].append(f"{filepath}: {analysis['todo_count']} TODO комментариев")
        
        return stats
    
    def find_improvements(self) -> List[Dict]:
        """Найти возможные улучшения"""
        improvements = []
        files = self.get_python_files()
        
        for filepath in files:
            analysis = self.analyze_file(filepath)
            if "error" in analysis:
                continue
            
            rel_path = os.path.relpath(filepath, self.project_path)
            
            # Проверяем различные проблемы
            if not analysis["has_docstring"]:
                improvements.append({
                    "type": "documentation",
                    "priority": 2,
                    "file": rel_path,
                    "description": f"Добавить docstrings в {rel_path}"
                })
            
            if not analysis["has_type_hints"] and analysis["functions_count"] > 0:
                improvements.append({
                    "type": "type_hints",
                    "priority": 3,
                    "file": rel_path,
                    "description": f"Добавить type hints в {rel_path}"
                })
            
            if analysis["empty_except"] > 0:
                improvements.append({
                    "type": "error_handling",
                    "priority": 4,
                    "file": rel_path,
                    "description": f"Исправить пустые except блоки в {rel_path}"
                })
            
            if analysis["todo_count"] > 0:
                improvements.append({
                    "type": "todo",
                    "priority": 3,
                    "file": rel_path,
                    "description": f"Реализовать TODO в {rel_path}"
                })
        
        # Сортируем по приоритету
        improvements.sort(key=lambda x: -x["priority"])
        return improvements


class AIProvider:
    """Базовый класс для AI провайдеров"""
    
    def generate(self, prompt: str, system: str = "") -> str:
        raise NotImplementedError


class GroqProvider(AIProvider):
    """Провайдер Groq API (бесплатный)"""
    
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    def __init__(self, api_key: str, model: str = "llama-3.1-70b-versatile"):
        self.api_key = api_key
        self.model = model
    
    def generate(self, prompt: str, system: str = "") -> str:
        if not HTTP_AVAILABLE:
            raise RuntimeError("httpx или requests не установлен")
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 4096
        }
        
        try:
            if hasattr(httpx, 'Client'):
                # httpx
                with httpx.Client(timeout=60) as client:
                    response = client.post(self.API_URL, headers=headers, json=data)
                    response.raise_for_status()
                    return response.json()["choices"][0]["message"]["content"]
            else:
                # requests
                response = httpx.post(self.API_URL, headers=headers, json=data, timeout=60)
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise


class OllamaProvider(AIProvider):
    """Провайдер Ollama (локальный)"""
    
    def __init__(self, model: str = "llama3.1", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host
    
    def generate(self, prompt: str, system: str = "") -> str:
        if not HTTP_AVAILABLE:
            raise RuntimeError("httpx или requests не установлен")
        
        url = f"{self.host}/api/generate"
        data = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False
        }
        
        try:
            if hasattr(httpx, 'Client'):
                with httpx.Client(timeout=120) as client:
                    response = client.post(url, json=data)
                    response.raise_for_status()
                    return response.json()["response"]
            else:
                response = httpx.post(url, json=data, timeout=120)
                response.raise_for_status()
                return response.json()["response"]
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise


class AIBrain:
    """Главный мозг для самоулучшения"""
    
    SYSTEM_PROMPT = """Ты - AI ассистент для улучшения Python кода.
Твоя задача - анализировать код и предлагать конкретные улучшения.
Отвечай ТОЛЬКО кодом или конкретными инструкциями.
Не добавляй лишних объяснений.
Формат ответа для изменения файла:
```python
# filepath: <путь к файлу>
<новый код>
```
"""
    
    def __init__(self, project_path: str, provider: Optional[AIProvider] = None):
        self.project_path = project_path
        self.provider = provider
        self.analyzer = CodeAnalyzer(project_path)
        self.tasks: List[Task] = []
        self.history: List[ImprovementResult] = []
        self.tasks_file = os.path.join(project_path, "tasks", "improvement_tasks.json")
        self.history_file = os.path.join(project_path, "tasks", "improvement_history.json")
        
        # Создаём папку tasks если нет
        os.makedirs(os.path.dirname(self.tasks_file), exist_ok=True)
        
        self.load_state()
    
    def load_state(self):
        """Загрузить состояние из файлов"""
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(t) for t in data]
            except Exception as e:
                logger.error(f"Ошибка загрузки задач: {e}")
        
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception as e:
                logger.error(f"Ошибка загрузки истории: {e}")
    
    def save_state(self):
        """Сохранить состояние"""
        try:
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump([t.to_dict() for t in self.tasks], f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Ошибка сохранения задач: {e}")
        
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history[-100:], f, indent=2, ensure_ascii=False)  # Храним последние 100
        except Exception as e:
            logger.error(f"Ошибка сохранения истории: {e}")
    
    def generate_task_id(self, title: str) -> str:
        """Генерация уникального ID задачи"""
        return hashlib.md5(f"{title}{datetime.now().isoformat()}".encode()).hexdigest()[:8]
    
    def scan_for_improvements(self) -> List[Task]:
        """Сканировать проект и создать задачи"""
        improvements = self.analyzer.find_improvements()
        new_tasks = []
        
        for imp in improvements:
            # Проверяем, нет ли уже такой задачи
            existing = [t for t in self.tasks if t.file_path == imp["file"] and t.status == "pending"]
            if existing:
                continue
            
            task = Task(
                id=self.generate_task_id(imp["description"]),
                title=imp["description"],
                description=f"Тип: {imp['type']}\nФайл: {imp['file']}",
                priority=imp["priority"],
                status="pending",
                file_path=imp["file"]
            )
            new_tasks.append(task)
            self.tasks.append(task)
        
        self.save_state()
        return new_tasks
    
    def get_pending_tasks(self) -> List[Task]:
        """Получить невыполненные задачи"""
        return [t for t in self.tasks if t.status == "pending"]
    
    def get_next_task(self) -> Optional[Task]:
        """Получить следующую задачу по приоритету"""
        pending = self.get_pending_tasks()
        if not pending:
            return None
        pending.sort(key=lambda x: -x.priority)
        return pending[0]
    
    def generate_improvement_prompt(self, task: Task) -> str:
        """Создать промпт для улучшения"""
        if not task.file_path:
            return f"Задача: {task.title}\n{task.description}"
        
        filepath = os.path.join(self.project_path, task.file_path)
        if not os.path.exists(filepath):
            return f"Файл не найден: {task.file_path}"
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return f"""Задача: {task.title}

Файл: {task.file_path}
```python
{content}
```

Внеси необходимые улучшения в код. Верни ПОЛНЫЙ обновлённый файл.
"""
    
    def run_tests(self) -> Tuple[bool, str]:
        """Запустить тесты"""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            success = result.returncode == 0
            output = result.stdout + result.stderr
            return success, output
        except subprocess.TimeoutExpired:
            return False, "Тесты превысили таймаут"
        except FileNotFoundError:
            return True, "pytest не найден, пропускаем тесты"
        except Exception as e:
            return False, str(e)
    
    def apply_improvement(self, task: Task, new_code: str) -> bool:
        """Применить улучшение к файлу"""
        if not task.file_path:
            return False
        
        filepath = os.path.join(self.project_path, task.file_path)
        
        # Извлекаем код из ответа AI
        code_match = re.search(r'```python\n(.*?)```', new_code, re.DOTALL)
        if code_match:
            new_code = code_match.group(1)
        
        # Создаём бэкап
        backup_path = filepath + ".bak"
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original)
        except Exception as e:
            logger.error(f"Ошибка создания бэкапа: {e}")
            return False
        
        # Применяем изменения
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_code)
            
            # Проверяем синтаксис
            result = subprocess.run(
                ["python", "-m", "py_compile", filepath],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # Откатываем
                with open(backup_path, 'r', encoding='utf-8') as f:
                    original = f.read()
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(original)
                logger.error(f"Синтаксическая ошибка: {result.stderr}")
                return False
            
            # Удаляем бэкап
            os.remove(backup_path)
            return True
            
        except Exception as e:
            logger.error(f"Ошибка применения изменений: {e}")
            # Пытаемся откатить
            if os.path.exists(backup_path):
                with open(backup_path, 'r', encoding='utf-8') as f:
                    original = f.read()
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(original)
            return False
    
    def execute_task(self, task: Task) -> ImprovementResult:
        """Выполнить задачу улучшения"""
        start_time = datetime.now()
        task.status = "in_progress"
        self.save_state()
        
        result = ImprovementResult(
            success=False,
            task=task,
            changes_made=[],
            tests_passed=False
        )
        
        if not self.provider:
            result.error = "AI провайдер не настроен"
            task.status = "failed"
            task.result = result.error
            self.save_state()
            return result
        
        try:
            # Генерируем промпт
            prompt = self.generate_improvement_prompt(task)
            
            # Получаем ответ от AI
            logger.info(f"Запрос к AI для задачи: {task.title}")
            response = self.provider.generate(prompt, self.SYSTEM_PROMPT)
            
            # Применяем изменения
            if task.file_path:
                if self.apply_improvement(task, response):
                    result.changes_made.append(f"Обновлён файл: {task.file_path}")
                    
                    # Запускаем тесты
                    tests_ok, test_output = self.run_tests()
                    result.tests_passed = tests_ok
                    
                    if tests_ok:
                        result.success = True
                        task.status = "completed"
                        task.completed_at = datetime.now().isoformat()
                        task.result = "Успешно улучшено"
                    else:
                        result.error = f"Тесты не прошли: {test_output[:500]}"
                        task.status = "failed"
                        task.result = result.error
                else:
                    result.error = "Не удалось применить изменения"
                    task.status = "failed"
                    task.result = result.error
            else:
                result.success = True
                task.status = "completed"
                task.completed_at = datetime.now().isoformat()
                task.result = response[:500]
        
        except Exception as e:
            result.error = str(e)
            task.status = "failed"
            task.result = str(e)
            logger.error(f"Ошибка выполнения задачи: {e}")
        
        result.duration_seconds = (datetime.now() - start_time).total_seconds()
        
        # Сохраняем в историю
        self.history.append({
            "task_id": task.id,
            "task_title": task.title,
            "success": result.success,
            "duration": result.duration_seconds,
            "timestamp": datetime.now().isoformat(),
            "error": result.error
        })
        
        self.save_state()
        return result
    
    def get_stats(self) -> Dict:
        """Получить статистику"""
        project_stats = self.analyzer.get_project_stats()
        
        completed = len([t for t in self.tasks if t.status == "completed"])
        failed = len([t for t in self.tasks if t.status == "failed"])
        pending = len([t for t in self.tasks if t.status == "pending"])
        
        success_rate = (completed / (completed + failed) * 100) if (completed + failed) > 0 else 0
        
        return {
            "project": project_stats,
            "tasks": {
                "total": len(self.tasks),
                "completed": completed,
                "failed": failed,
                "pending": pending,
                "success_rate": round(success_rate, 1)
            },
            "history_count": len(self.history)
        }
