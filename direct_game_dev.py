"""
Direct Game Development - Прямое создание файлов для игры
Без использования нестабильной автоматизации окон
"""

import os
import json
from datetime import datetime

# Путь к проекту игры
GAME_PROJECT = r"C:\Users\bnex4\Documents\slime-rpg"

# Шаблоны для создания файлов
TEMPLATES = {
    "enemy": '''# {name} - враг
# {description}
extends CharacterBody2D
class_name {class_name}

signal died
signal damaged(amount: int)

@export var max_hp: int = {hp}
@export var current_hp: int = {hp}
@export var move_speed: float = {speed}
@export var attack_damage: int = {damage}

var target: Node2D = null
var is_dead: bool = false

func _ready() -> void:
    add_to_group("enemies")
    modulate = Color({color})

func _physics_process(delta: float) -> void:
    if is_dead:
        return
    
    if target == null:
        _find_target()
    
    if target:
        var direction = (target.global_position - global_position).normalized()
        velocity = direction * move_speed
        move_and_slide()

func _find_target() -> void:
    var players = get_tree().get_nodes_in_group("player")
    if players.size() > 0:
        target = players[0]

func take_damage(amount: int, element: String = "physical") -> void:
    if is_dead:
        return
    
    current_hp -= amount
    damaged.emit(amount)
    
    if current_hp <= 0:
        _die()

func _die() -> void:
    is_dead = true
    died.emit()
    queue_free()

func get_hp_percent() -> float:
    return float(current_hp) / float(max_hp)
''',

    "ability": '''# {name} - способность
# {description}
extends Node
class_name {class_name}

signal activated
signal cooldown_finished

@export var damage: int = {damage}
@export var cooldown: float = {cooldown}
@export var mana_cost: int = {mana_cost}

var can_use: bool = true
var cooldown_timer: Timer

func _ready() -> void:
    cooldown_timer = Timer.new()
    cooldown_timer.one_shot = true
    cooldown_timer.timeout.connect(_on_cooldown_finished)
    add_child(cooldown_timer)

func activate(caster: Node2D, target_pos: Vector2) -> bool:
    if not can_use:
        return false
    
    can_use = false
    cooldown_timer.wait_time = cooldown
    cooldown_timer.start()
    
    _execute(caster, target_pos)
    activated.emit()
    return true

func _execute(caster: Node2D, target_pos: Vector2) -> void:
    # Переопределить в наследниках
    pass

func _on_cooldown_finished() -> void:
    can_use = true
    cooldown_finished.emit()

func get_cooldown_percent() -> float:
    if can_use:
        return 1.0
    return 1.0 - (cooldown_timer.time_left / cooldown)
''',

    "ui_panel": '''# {name} - UI панель
# {description}
extends Control
class_name {class_name}

func _ready() -> void:
    _setup_ui()

func _setup_ui() -> void:
    # Настройка UI элементов
    pass

func show_panel() -> void:
    visible = true
    var tween = create_tween()
    tween.tween_property(self, "modulate:a", 1.0, 0.3)

func hide_panel() -> void:
    var tween = create_tween()
    tween.tween_property(self, "modulate:a", 0.0, 0.3)
    tween.tween_callback(func(): visible = false)
'''
}


def create_enemy(name: str, class_name: str, hp: int = 50, speed: float = 80.0, 
                 damage: int = 10, color: str = "1.0, 1.0, 1.0", description: str = "") -> str:
    """Создать файл врага"""
    content = TEMPLATES["enemy"].format(
        name=name,
        class_name=class_name,
        hp=hp,
        speed=speed,
        damage=damage,
        color=color,
        description=description
    )
    
    filepath = os.path.join(GAME_PROJECT, "game", "enemies", f"{class_name.lower()}.gd")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Создан враг: {filepath}")
    return filepath


def create_ability(name: str, class_name: str, damage: int = 20, 
                   cooldown: float = 5.0, mana_cost: int = 10, description: str = "") -> str:
    """Создать файл способности"""
    content = TEMPLATES["ability"].format(
        name=name,
        class_name=class_name,
        damage=damage,
        cooldown=cooldown,
        mana_cost=mana_cost,
        description=description
    )
    
    filepath = os.path.join(GAME_PROJECT, "game", "abilities", f"{class_name.lower()}.gd")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Создана способность: {filepath}")
    return filepath


def create_ui_panel(name: str, class_name: str, description: str = "") -> str:
    """Создать файл UI панели"""
    content = TEMPLATES["ui_panel"].format(
        name=name,
        class_name=class_name,
        description=description
    )
    
    filepath = os.path.join(GAME_PROJECT, "scenes", "ui", f"{class_name.lower()}.gd")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Создана UI панель: {filepath}")
    return filepath


def list_game_files() -> dict:
    """Показать структуру файлов игры"""
    result = {
        "enemies": [],
        "abilities": [],
        "ui": [],
        "core": []
    }
    
    enemies_dir = os.path.join(GAME_PROJECT, "game", "enemies")
    if os.path.exists(enemies_dir):
        result["enemies"] = [f for f in os.listdir(enemies_dir) if f.endswith('.gd')]
    
    abilities_dir = os.path.join(GAME_PROJECT, "game", "abilities")
    if os.path.exists(abilities_dir):
        result["abilities"] = [f for f in os.listdir(abilities_dir) if f.endswith('.gd')]
    
    ui_dir = os.path.join(GAME_PROJECT, "scenes", "ui")
    if os.path.exists(ui_dir):
        result["ui"] = [f for f in os.listdir(ui_dir) if f.endswith('.gd')]
    
    core_dir = os.path.join(GAME_PROJECT, "game", "core")
    if os.path.exists(core_dir):
        result["core"] = [f for f in os.listdir(core_dir) if f.endswith('.gd')]
    
    return result


def main():
    print("=" * 50)
    print("🎮 DIRECT GAME DEVELOPMENT")
    print("=" * 50)
    print(f"\n📁 Проект: {GAME_PROJECT}")
    
    # Показываем текущие файлы
    files = list_game_files()
    print("\n📂 Текущие файлы:")
    for category, file_list in files.items():
        if file_list:
            print(f"  {category}: {', '.join(file_list)}")
    
    # Пример создания нового врага
    print("\n🔧 Пример создания врага:")
    print("  create_enemy('Ледяной голем', 'IceGolem', hp=120, speed=60, damage=25, color='0.5, 0.8, 1.0')")
    
    print("\n✅ Готово!")


if __name__ == "__main__":
    main()
