"""
Windsurf Automation - Main module
Automates Windsurf IDE interactions for iterative coding tasks
Uses win32gui for reliable window handling on Windows
"""

import pyautogui
import pyperclip
import keyboard
import time
import ctypes
from ctypes import wintypes
from typing import Optional, List, Tuple

# Windows API
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Constants
SW_RESTORE = 9
SW_SHOW = 5
SW_SHOWDEFAULT = 10
HWND_TOP = 0
SWP_SHOWWINDOW = 0x0040

# Settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2


def get_all_windows() -> List[Tuple[int, str]]:
    """Get all visible windows with their handles and titles"""
    windows = []
    
    def enum_callback(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                windows.append((hwnd, buff.value))
        return True
    
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(WNDENUMPROC(enum_callback), 0)
    return windows


def find_windsurf_windows(ide_only: bool = False) -> List[Tuple[int, str]]:
    """Find all Windsurf windows
    
    Args:
        ide_only: If True, filter only IDE windows (not browser, explorer)
    """
    all_windows = get_all_windows()
    windows = [(hwnd, title) for hwnd, title in all_windows if "Windsurf" in title]
    
    if ide_only:
        # Filter: must have " - Windsurf" pattern OR be "Windsurf" exactly (new empty window)
        # Exclude: browser, explorer
        filtered = []
        for hwnd, title in windows:
            # Skip browser windows
            if "Браузер" in title or "Browser" in title:
                continue
            # Skip explorer windows
            if "проводник" in title.lower():
                continue
            # Include IDE windows
            if " - Windsurf" in title or title == "Windsurf" or title.startswith("Windsurf"):
                filtered.append((hwnd, title))
        return filtered
    
    return windows


def activate_window_by_hwnd(hwnd: int) -> bool:
    """Activate window by its handle using Windows API"""
    try:
        # Get current foreground window's thread
        foreground_hwnd = user32.GetForegroundWindow()
        foreground_thread = user32.GetWindowThreadProcessId(foreground_hwnd, None)
        current_thread = kernel32.GetCurrentThreadId()
        
        # Attach input to foreground thread
        user32.AttachThreadInput(current_thread, foreground_thread, True)
        
        # Restore if minimized
        user32.ShowWindow(hwnd, SW_RESTORE)
        time.sleep(0.1)
        
        # Bring to foreground
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.1)
        
        # Force focus
        user32.BringWindowToTop(hwnd)
        
        # Set focus
        user32.SetFocus(hwnd)
        
        # Detach input
        user32.AttachThreadInput(current_thread, foreground_thread, False)
        
        time.sleep(0.2)
        return True
    except Exception as e:
        print(f"❌ Error activating window: {e}")
        return False


def get_window_rect(hwnd: int) -> Tuple[int, int, int, int]:
    """Get window rectangle (left, top, right, bottom)"""
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return (rect.left, rect.top, rect.right, rect.bottom)


class WindsurfAutomation:
    """Main class for Windsurf IDE automation"""
    
    def __init__(self):
        self.hwnd: Optional[int] = None
        self.title: str = ""
    
    def list_windows(self) -> List[Tuple[int, str]]:
        """List all Windsurf windows"""
        return find_windsurf_windows()
    
    def select_window(self, hwnd: int) -> bool:
        """Select specific Windsurf window by handle"""
        windows = find_windsurf_windows()
        for h, title in windows:
            if h == hwnd:
                self.hwnd = hwnd
                self.title = title
                return True
        return False
    
    def find_windsurf_window(self, index: int = 0) -> bool:
        """Find Windsurf window by index (0 = first found)"""
        windows = find_windsurf_windows()
        if windows and index < len(windows):
            self.hwnd, self.title = windows[index]
            return True
        return False
    
    def activate_window(self) -> bool:
        """Activate current Windsurf window"""
        if not self.hwnd:
            if not self.find_windsurf_window():
                print("❌ Windsurf window not found")
                return False
        
        # Activate using Windows API
        if not activate_window_by_hwnd(self.hwnd):
            return False
        
        # Click on window to ensure focus
        rect = get_window_rect(self.hwnd)
        center_x = (rect[0] + rect[2]) // 2
        center_y = (rect[1] + rect[3]) // 2
        
        # Click on editor area (avoid title bar)
        click_y = rect[1] + 100  # 100px from top
        pyautogui.click(center_x, click_y)
        time.sleep(0.3)
        
        return True
    
    def close_palettes(self):
        """Close any open palettes with Escape"""
        for _ in range(2):
            pyautogui.press('escape')
            time.sleep(0.1)
    
    def open_new_window(self) -> bool:
        """Open new Windsurf window using keyboard library"""
        if not self.activate_window():
            return False
        
        self.close_palettes()
        time.sleep(0.3)
        
        # Count windows before (IDE windows only)
        windows_before = find_windsurf_windows(ide_only=True)
        count_before = len(windows_before)
        print(f"   Windows before: {count_before}")
        
        # Use keyboard library for reliable hotkey
        print("   Sending Ctrl+Shift+N...")
        keyboard.send('ctrl+shift+n')
        time.sleep(3)
        
        # Check if new window appeared
        windows_after = find_windsurf_windows(ide_only=True)
        if len(windows_after) > count_before:
            # Find the new window (one that wasn't in before)
            old_hwnds = {w[0] for w in windows_before}
            for hwnd, title in windows_after:
                if hwnd not in old_hwnds:
                    self.hwnd = hwnd
                    self.title = title
                    print(f"✅ New window: {title[:50]}...")
                    return True
            # Fallback - take last one
            self.hwnd, self.title = windows_after[-1]
            print(f"✅ New window: {self.title[:50]}...")
            return True
        
        print(f"⚠️ Window count unchanged ({len(windows_after)})")
        return False
    
    def open_sidebar(self) -> bool:
        """Open Cascade sidebar (Ctrl+L)"""
        if not self.activate_window():
            return False
        
        self.close_palettes()
        time.sleep(0.2)
        
        keyboard.send('ctrl+l')
        time.sleep(0.5)
        return True
    
    def send_message(self, message: str) -> bool:
        """Send message to Cascade chat"""
        if not self.activate_window():
            return False
        
        # Open sidebar first
        self.open_sidebar()
        time.sleep(0.3)
        
        # Paste message via clipboard
        pyperclip.copy(message)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.2)
        
        # Send with Enter
        pyautogui.press('enter')
        time.sleep(0.3)
        
        return True


def main():
    """Main entry point - interactive test"""
    print("=" * 60)
    print("Windsurf Automation - Test Mode")
    print("=" * 60)
    
    wa = WindsurfAutomation()
    
    # List all Windsurf windows
    windows = wa.list_windows()
    if not windows:
        print("❌ No Windsurf windows found. Please open Windsurf IDE first.")
        return
    
    print(f"\n📋 Found {len(windows)} Windsurf window(s):")
    for i, (hwnd, title) in enumerate(windows):
        print(f"  [{i}] HWND={hwnd}: {title}")
    
    # Select first window
    wa.find_windsurf_window(0)
    print(f"\n✅ Selected: {wa.title} (HWND={wa.hwnd})")
    
    print("\n📌 Available actions:")
    print("  1. Activate window")
    print("  2. Open new window (Ctrl+Shift+N)")
    print("  3. Open sidebar (Ctrl+L)")
    print("  4. Send test message")
    print("  5. Full test (new window + sidebar + message)")
    print("  L. List windows")
    print("  S. Select window by index")
    print("  0. Exit")
    
    while True:
        choice = input("\n> Choice: ").strip().lower()
        
        if choice == "0":
            break
        elif choice == "1":
            if wa.activate_window():
                print("✅ Window activated")
        elif choice == "2":
            wa.open_new_window()
        elif choice == "3":
            if wa.open_sidebar():
                print("✅ Sidebar opened")
        elif choice == "4":
            if wa.send_message("Hello from Windsurf Automation! 🚀"):
                print("✅ Message sent")
        elif choice == "5":
            print("\n🔄 Running full test...")
            print("  Step 1: Opening new window...")
            if wa.open_new_window():
                time.sleep(1)
                print("  Step 2: Opening sidebar...")
                if wa.open_sidebar():
                    time.sleep(0.5)
                    print("  Step 3: Sending test message...")
                    if wa.send_message("Test message from Windsurf Automation! 🎉"):
                        print("✅ Full test completed!")
                    else:
                        print("❌ Failed to send message")
                else:
                    print("❌ Failed to open sidebar")
            else:
                print("❌ Failed to open new window")
        elif choice == "l":
            windows = wa.list_windows()
            print(f"\n📋 Found {len(windows)} window(s):")
            for i, (hwnd, title) in enumerate(windows):
                marker = " <-- current" if hwnd == wa.hwnd else ""
                print(f"  [{i}] HWND={hwnd}: {title}{marker}")
        elif choice == "s":
            idx = input("  Enter index: ").strip()
            if idx.isdigit():
                if wa.find_windsurf_window(int(idx)):
                    print(f"✅ Selected: {wa.title}")
                else:
                    print("❌ Invalid index")
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
