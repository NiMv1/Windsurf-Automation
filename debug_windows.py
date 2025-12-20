"""
Отладка - показать все окна с Windsurf в названии
"""

import sys
sys.path.insert(0, 'src')

from windsurf_automation import find_windsurf_windows, get_all_windows

print("=" * 70)
print("🔍 Все окна с 'Windsurf' в названии:")
print("=" * 70)

windows = find_windsurf_windows()

for i, (hwnd, title) in enumerate(windows):
    print(f"\n[{i}] HWND={hwnd}")
    print(f"    Title: {title}")
    print(f"    Contains ' - Windsurf - ': {' - Windsurf - ' in title}")

print("\n" + "=" * 70)
print(f"Всего найдено: {len(windows)} окон")
