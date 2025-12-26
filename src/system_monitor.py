"""
Мониторинг системных ресурсов - CPU, RAM, GPU
"""

import os
import platform
import subprocess
from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger('WA.Monitor')

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


@dataclass
class SystemStats:
    """Статистика системы"""
    cpu_percent: float = 0.0
    cpu_cores: int = 0
    ram_total_gb: float = 0.0
    ram_used_gb: float = 0.0
    ram_percent: float = 0.0
    gpu_name: str = "N/A"
    gpu_memory_total_mb: int = 0
    gpu_memory_used_mb: int = 0
    gpu_utilization: float = 0.0
    disk_total_gb: float = 0.0
    disk_used_gb: float = 0.0
    disk_percent: float = 0.0
    python_version: str = ""
    os_name: str = ""


class SystemMonitor:
    """Мониторинг системных ресурсов"""
    
    def __init__(self):
        self.has_nvidia = self._check_nvidia()
    
    def _check_nvidia(self) -> bool:
        """Проверить наличие NVIDIA GPU"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def get_gpu_stats(self) -> dict:
        """Получить статистику GPU"""
        if not self.has_nvidia:
            return {
                "name": "N/A",
                "memory_total": 0,
                "memory_used": 0,
                "utilization": 0
            }
        
        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total,memory.used,utilization.gpu",
                    "--format=csv,noheader,nounits"
                ],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                parts = result.stdout.strip().split(", ")
                if len(parts) >= 4:
                    return {
                        "name": parts[0],
                        "memory_total": int(parts[1]),
                        "memory_used": int(parts[2]),
                        "utilization": float(parts[3])
                    }
        except Exception as e:
            logger.debug(f"GPU stats error: {e}")
        
        return {
            "name": "N/A",
            "memory_total": 0,
            "memory_used": 0,
            "utilization": 0
        }
    
    def get_stats(self) -> SystemStats:
        """Получить полную статистику системы"""
        stats = SystemStats()
        
        # Python и OS
        stats.python_version = platform.python_version()
        stats.os_name = f"{platform.system()} {platform.release()}"
        
        if PSUTIL_AVAILABLE:
            # CPU
            stats.cpu_percent = psutil.cpu_percent(interval=0.1)
            stats.cpu_cores = psutil.cpu_count()
            
            # RAM
            mem = psutil.virtual_memory()
            stats.ram_total_gb = round(mem.total / (1024**3), 1)
            stats.ram_used_gb = round(mem.used / (1024**3), 1)
            stats.ram_percent = mem.percent
            
            # Disk
            disk = psutil.disk_usage('/')
            stats.disk_total_gb = round(disk.total / (1024**3), 1)
            stats.disk_used_gb = round(disk.used / (1024**3), 1)
            stats.disk_percent = disk.percent
        
        # GPU
        gpu = self.get_gpu_stats()
        stats.gpu_name = gpu["name"]
        stats.gpu_memory_total_mb = gpu["memory_total"]
        stats.gpu_memory_used_mb = gpu["memory_used"]
        stats.gpu_utilization = gpu["utilization"]
        
        return stats
    
    def get_formatted_stats(self) -> str:
        """Получить форматированную строку статистики"""
        stats = self.get_stats()
        
        lines = [
            f"🖥️ OS: {stats.os_name}",
            f"🐍 Python: {stats.python_version}",
            f"",
            f"⚡ CPU: {stats.cpu_percent}% ({stats.cpu_cores} cores)",
            f"💾 RAM: {stats.ram_used_gb}/{stats.ram_total_gb} GB ({stats.ram_percent}%)",
            f"💿 Disk: {stats.disk_used_gb}/{stats.disk_total_gb} GB ({stats.disk_percent}%)",
        ]
        
        if stats.gpu_name != "N/A":
            lines.extend([
                f"",
                f"🎮 GPU: {stats.gpu_name}",
                f"   Memory: {stats.gpu_memory_used_mb}/{stats.gpu_memory_total_mb} MB",
                f"   Load: {stats.gpu_utilization}%"
            ])
        
        return "\n".join(lines)
