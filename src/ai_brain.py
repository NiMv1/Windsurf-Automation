"""
AI Brain - Мозг самоулучшающейся системы
Принимает решения, планирует задачи, обучается на результатах
"""

import os
import json
import sqlite3
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path

logger = logging.getLogger('WA.AIBrain')


class TaskType(Enum):
    """Типы задач"""
    SELF_IMPROVE = "self_improve"      # Улучшение себя
    GITHUB_PR = "github_pr"            # Работа с PR
    GITHUB_ISSUE = "github_issue"      # Работа с issues
    CODE_REVIEW = "code_review"        # Ревью кода
    BUG_FIX = "bug_fix"               # Исправление багов
    FEATURE_DEV = "feature_dev"        # Разработка фич
    TEST_WRITE = "test_write"          # Написание тестов
    DOCS_UPDATE = "docs_update"        # Обновление документации
    GAME_DEV = "game_dev"             # Разработка игр
    WEB_DEV = "web_dev"               # Веб-разработка


class TaskPriority(Enum):
    """Приоритеты задач"""
    CRITICAL = 0   # Критические баги, падения
    HIGH = 1       # PR ревью, срочные задачи
    MEDIUM = 2     # Обычная разработка
    LOW = 3        # Улучшения, рефакторинг
    BACKGROUND = 4 # Фоновые задачи


class TaskStatus(Enum):
    """Статусы задач"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Задача для выполнения"""
    id: str
    type: TaskType
    priority: TaskPriority
    title: str
    description: str
    prompt: str = ""
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None
    retries: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            **asdict(self),
            'type': self.type.value,
            'priority': self.priority.value,
            'status': self.status.value
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        data['type'] = TaskType(data['type'])
        data['priority'] = TaskPriority(data['priority'])
        data['status'] = TaskStatus(data['status'])
        return cls(**data)


@dataclass
class MemoryItem:
    """Элемент памяти"""
    id: str
    key: str
    value: Any
    category: str
    importance: float  # 0.0 - 1.0
    created_at: str
    accessed_at: str
    access_count: int = 0
    
    def to_dict(self) -> dict:
        return asdict(self)


class Memory:
    """
    Система памяти AI Brain.
    Хранит краткосрочную и долгосрочную память.
    """
    
    def __init__(self, db_path: str = "memory.db"):
        self.db_path = db_path
        self.short_term: Dict[str, Any] = {}  # RAM память
        self._init_db()
    
    def _init_db(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица памяти
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory (
                id TEXT PRIMARY KEY,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                category TEXT NOT NULL,
                importance REAL DEFAULT 0.5,
                created_at TEXT NOT NULL,
                accessed_at TEXT NOT NULL,
                access_count INTEGER DEFAULT 0
            )
        ''')
        
        # Таблица истории задач
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_history (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                priority INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                prompt TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                result TEXT,
                error TEXT,
                retries INTEGER DEFAULT 0,
                metadata TEXT
            )
        ''')
        
        # Индексы
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_key ON memory(key)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_category ON memory(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_status ON task_history(status)')
        
        conn.commit()
        conn.close()
    
    def remember(self, key: str, value: Any, category: str = "general", 
                 importance: float = 0.5, long_term: bool = True) -> str:
        """
        Запомнить информацию.
        
        Args:
            key: Ключ для поиска
            value: Значение для сохранения
            category: Категория памяти
            importance: Важность (0.0 - 1.0)
            long_term: Сохранять в долгосрочную память
            
        Returns:
            ID записи
        """
        item_id = hashlib.md5(f"{key}:{category}".encode()).hexdigest()[:16]
        now = datetime.now().isoformat()
        
        # Краткосрочная память
        self.short_term[key] = value
        
        if long_term:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO memory 
                (id, key, value, category, importance, created_at, accessed_at, access_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, 
                    COALESCE((SELECT access_count FROM memory WHERE id = ?), 0) + 1)
            ''', (item_id, key, json.dumps(value), category, importance, now, now, item_id))
            
            conn.commit()
            conn.close()
        
        logger.debug(f"Запомнено: {key} (категория: {category})")
        return item_id
    
    def recall(self, query: str = None, category: str = None, 
               limit: int = 10) -> List[MemoryItem]:
        """
        Вспомнить информацию.
        
        Args:
            query: Поисковый запрос (по ключу)
            category: Фильтр по категории
            limit: Максимум записей
            
        Returns:
            Список найденных записей
        """
        # Сначала проверяем краткосрочную память
        if query and query in self.short_term:
            return [MemoryItem(
                id="short_term",
                key=query,
                value=self.short_term[query],
                category="short_term",
                importance=1.0,
                created_at=datetime.now().isoformat(),
                accessed_at=datetime.now().isoformat()
            )]
        
        # Ищем в долгосрочной памяти
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sql = "SELECT * FROM memory WHERE 1=1"
        params = []
        
        if query:
            sql += " AND key LIKE ?"
            params.append(f"%{query}%")
        
        if category:
            sql += " AND category = ?"
            params.append(category)
        
        sql += " ORDER BY importance DESC, access_count DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        # Обновляем время доступа
        now = datetime.now().isoformat()
        for row in rows:
            cursor.execute(
                "UPDATE memory SET accessed_at = ?, access_count = access_count + 1 WHERE id = ?",
                (now, row[0])
            )
        
        conn.commit()
        conn.close()
        
        return [MemoryItem(
            id=row[0],
            key=row[1],
            value=json.loads(row[2]),
            category=row[3],
            importance=row[4],
            created_at=row[5],
            accessed_at=row[6],
            access_count=row[7]
        ) for row in rows]
    
    def forget(self, key: str = None, category: str = None, 
               older_than_days: int = None):
        """
        Забыть информацию.
        
        Args:
            key: Ключ для удаления
            category: Категория для удаления
            older_than_days: Удалить записи старше N дней
        """
        # Краткосрочная память
        if key and key in self.short_term:
            del self.short_term[key]
        
        # Долгосрочная память
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if key:
            cursor.execute("DELETE FROM memory WHERE key = ?", (key,))
        elif category:
            cursor.execute("DELETE FROM memory WHERE category = ?", (category,))
        elif older_than_days:
            cutoff = (datetime.now() - timedelta(days=older_than_days)).isoformat()
            cursor.execute("DELETE FROM memory WHERE accessed_at < ?", (cutoff,))
        
        conn.commit()
        conn.close()
    
    def save_task(self, task: Task):
        """Сохранить задачу в историю"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO task_history 
            (id, type, priority, title, description, prompt, status, 
             created_at, started_at, completed_at, result, error, retries, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task.id, task.type.value, task.priority.value, task.title,
            task.description, task.prompt, task.status.value,
            task.created_at, task.started_at, task.completed_at,
            task.result, task.error, task.retries, json.dumps(task.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def get_task_history(self, status: TaskStatus = None, 
                         task_type: TaskType = None,
                         limit: int = 50) -> List[Task]:
        """Получить историю задач"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sql = "SELECT * FROM task_history WHERE 1=1"
        params = []
        
        if status:
            sql += " AND status = ?"
            params.append(status.value)
        
        if task_type:
            sql += " AND type = ?"
            params.append(task_type.value)
        
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        tasks = []
        for row in rows:
            tasks.append(Task(
                id=row[0],
                type=TaskType(row[1]),
                priority=TaskPriority(row[2]),
                title=row[3],
                description=row[4] or "",
                prompt=row[5] or "",
                status=TaskStatus(row[6]),
                created_at=row[7],
                started_at=row[8],
                completed_at=row[9],
                result=row[10],
                error=row[11],
                retries=row[12],
                metadata=json.loads(row[13]) if row[13] else {}
            ))
        
        return tasks


class TaskPlanner:
    """
    Планировщик задач.
    Анализирует текущее состояние и создаёт план действий.
    """
    
    def __init__(self, memory: Memory):
        self.memory = memory
    
    def analyze_self(self, project_path: str) -> List[Dict[str, Any]]:
        """
        Анализировать свой код и найти возможности улучшения.
        
        Args:
            project_path: Путь к проекту
            
        Returns:
            Список найденных проблем/возможностей
        """
        issues = []
        
        # Сканируем Python файлы
        for root, dirs, files in os.walk(project_path):
            # Пропускаем служебные папки
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'venv', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    issues.extend(self._analyze_file(filepath))
        
        return issues
    
    def _analyze_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Анализировать один файл"""
        issues = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Проверка длины файла
            if len(lines) > 500:
                issues.append({
                    'type': 'refactor',
                    'file': filepath,
                    'message': f'Файл слишком большой ({len(lines)} строк), рассмотреть разделение',
                    'priority': TaskPriority.LOW
                })
            
            # Проверка TODO/FIXME
            for i, line in enumerate(lines, 1):
                if 'TODO' in line or 'FIXME' in line:
                    issues.append({
                        'type': 'todo',
                        'file': filepath,
                        'line': i,
                        'message': line.strip(),
                        'priority': TaskPriority.MEDIUM
                    })
            
            # Проверка отсутствия docstring
            if 'def ' in content and '"""' not in content[:500]:
                issues.append({
                    'type': 'docs',
                    'file': filepath,
                    'message': 'Отсутствует docstring в начале файла',
                    'priority': TaskPriority.LOW
                })
            
            # Проверка импортов
            if 'import *' in content:
                issues.append({
                    'type': 'style',
                    'file': filepath,
                    'message': 'Использование import * не рекомендуется',
                    'priority': TaskPriority.LOW
                })
            
        except Exception as e:
            logger.warning(f"Ошибка анализа {filepath}: {e}")
        
        return issues
    
    def create_improvement_tasks(self, issues: List[Dict[str, Any]]) -> List[Task]:
        """Создать задачи на основе найденных проблем"""
        tasks = []
        
        for issue in issues:
            task_id = hashlib.md5(
                f"{issue['file']}:{issue['message']}".encode()
            ).hexdigest()[:12]
            
            task = Task(
                id=task_id,
                type=TaskType.SELF_IMPROVE,
                priority=issue.get('priority', TaskPriority.MEDIUM),
                title=f"[{issue['type'].upper()}] {Path(issue['file']).name}",
                description=issue['message'],
                metadata={'file': issue['file'], 'issue_type': issue['type']}
            )
            tasks.append(task)
        
        return tasks


class AIBrain:
    """
    Главный класс - мозг системы.
    Координирует все компоненты и принимает решения.
    """
    
    def __init__(self, project_path: str = None):
        self.project_path = project_path or os.path.dirname(os.path.dirname(__file__))
        
        # Инициализация компонентов
        db_path = os.path.join(self.project_path, "memory.db")
        self.memory = Memory(db_path)
        self.planner = TaskPlanner(self.memory)
        
        # Очередь задач
        self.task_queue: List[Task] = []
        self.current_task: Optional[Task] = None
        
        # Статистика
        self.stats = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'improvements_made': 0,
            'session_start': datetime.now().isoformat()
        }
        
        logger.info("AI Brain инициализирован")
    
    def think(self) -> Optional[Task]:
        """
        Основной цикл мышления.
        Анализирует ситуацию и выбирает следующую задачу.
        
        Returns:
            Следующая задача для выполнения
        """
        # Если есть задачи в очереди - берём следующую
        if self.task_queue:
            # Сортируем по приоритету
            self.task_queue.sort(key=lambda t: t.priority.value)
            return self.task_queue.pop(0)
        
        # Иначе - анализируем что можно улучшить
        logger.info("Анализ возможностей улучшения...")
        issues = self.planner.analyze_self(self.project_path)
        
        if issues:
            tasks = self.planner.create_improvement_tasks(issues)
            self.task_queue.extend(tasks)
            logger.info(f"Найдено {len(tasks)} задач для улучшения")
            
            if self.task_queue:
                return self.task_queue.pop(0)
        
        return None
    
    def add_task(self, task: Task):
        """Добавить задачу в очередь"""
        self.task_queue.append(task)
        logger.info(f"Задача добавлена: {task.title}")
    
    def start_task(self, task: Task):
        """Начать выполнение задачи"""
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now().isoformat()
        self.current_task = task
        self.memory.save_task(task)
        logger.info(f"Начата задача: {task.title}")
    
    def complete_task(self, task: Task, result: str):
        """Завершить задачу успешно"""
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now().isoformat()
        task.result = result
        self.current_task = None
        
        self.memory.save_task(task)
        self.stats['tasks_completed'] += 1
        
        if task.type == TaskType.SELF_IMPROVE:
            self.stats['improvements_made'] += 1
        
        logger.info(f"Задача завершена: {task.title}")
    
    def fail_task(self, task: Task, error: str):
        """Отметить задачу как проваленную"""
        task.retries += 1
        
        if task.retries < task.max_retries:
            task.status = TaskStatus.PENDING
            task.error = error
            self.task_queue.append(task)
            logger.warning(f"Задача будет повторена ({task.retries}/{task.max_retries}): {task.title}")
        else:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now().isoformat()
            task.error = error
            self.stats['tasks_failed'] += 1
            logger.error(f"Задача провалена: {task.title} - {error}")
        
        self.current_task = None
        self.memory.save_task(task)
    
    def generate_prompt(self, task: Task) -> str:
        """
        Сгенерировать промпт для Windsurf на основе задачи.
        
        Args:
            task: Задача
            
        Returns:
            Промпт для отправки в Windsurf
        """
        # Базовый контекст
        context = f"""Ты работаешь над проектом Windsurf Automation.
Путь: {self.project_path}

ЗАДАЧА: {task.title}
ОПИСАНИЕ: {task.description}

"""
        
        # Добавляем специфичный контекст в зависимости от типа задачи
        if task.type == TaskType.SELF_IMPROVE:
            file_path = task.metadata.get('file', '')
            context += f"""ФАЙЛ: {file_path}

ТРЕБОВАНИЯ:
1. Изменяй только указанный файл
2. Не ломай существующий функционал
3. Добавляй комментарии на русском
4. Следуй PEP 8

"""
        
        elif task.type == TaskType.GITHUB_PR:
            context += """ТРЕБОВАНИЯ:
1. Изучи CONTRIBUTING.md проекта
2. Следуй стилю кода проекта
3. Добавь тесты если нужно
4. Обнови CHANGELOG если нужно

"""
        
        elif task.type == TaskType.TEST_WRITE:
            context += """ТРЕБОВАНИЯ:
1. Используй pytest
2. Покрой основные сценарии
3. Добавь edge cases
4. Используй моки где нужно

"""
        
        # Формат отчёта
        context += """ОТЧЁТ (обязательно в конце):
## Сделано:
- ...

## Не сделано:
- ...

## Проблемы:
- ...
"""
        
        task.prompt = context
        return context
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику"""
        return {
            **self.stats,
            'tasks_in_queue': len(self.task_queue),
            'current_task': self.current_task.title if self.current_task else None
        }
    
    def learn(self, task: Task, feedback: str):
        """
        Обучение на результатах выполнения задачи.
        
        Args:
            task: Выполненная задача
            feedback: Обратная связь (успех/ошибка/комментарии)
        """
        # Сохраняем опыт в память
        self.memory.remember(
            key=f"experience:{task.type.value}:{task.id}",
            value={
                'task': task.to_dict(),
                'feedback': feedback,
                'success': task.status == TaskStatus.COMPLETED
            },
            category="experience",
            importance=0.7 if task.status == TaskStatus.COMPLETED else 0.9
        )
        
        logger.info(f"Опыт сохранён: {task.title}")


def main():
    """Тестирование AI Brain"""
    logging.basicConfig(level=logging.DEBUG)
    
    brain = AIBrain()
    
    print("=== AI Brain Test ===")
    print(f"Project path: {brain.project_path}")
    
    # Думаем
    task = brain.think()
    if task:
        print(f"\nСледующая задача: {task.title}")
        print(f"Приоритет: {task.priority.name}")
        print(f"Описание: {task.description}")
        
        # Генерируем промпт
        prompt = brain.generate_prompt(task)
        print(f"\nПромпт:\n{prompt[:500]}...")
    else:
        print("\nНет задач для выполнения")
    
    # Статистика
    print(f"\nСтатистика: {brain.get_stats()}")


if __name__ == "__main__":
    main()
