"""
Windsurf Automation - Main module
Automates Windsurf IDE interactions for iterative coding tasks
"""

import pyautogui
import pygetwindow as gw
import pyperclip
import time
from typing import Optional

# Settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3


class WindsurfAutomation:
    """Main class for Windsurf IDE automation"""
    
    def __init__(self):
        self.window: Optional[gw.Win32Window] = None
    
    def find_windsurf_window(self) -> bool:
        """Find and store Windsurf window reference"""
        windows = gw.getWindowsWithTitle("Windsurf")
        if windows:
            self.window = windows[0]
            return True
        return False
    
    def activate_window(self) -> bool:
        """Activate Windsurf window"""
        if not self.window:
            if not self.find_windsurf_window():
                print("❌ Windsurf window not found")
                return False
        
        try:
            # Click on window center to focus
            center_x = self.window.left + self.window.width // 2
            center_y = self.window.top + self.window.height // 2
            pyautogui.click(center_x, center_y)
            time.sleep(0.3)
            return True
        except Exception as e:
            print(f"❌ Error activating window: {e}")
            return False
    
    def open_new_window(self) -> bool:
        """Open new Windsurf window (Ctrl+Shift+N)"""
        if not self.activate_window():
            return False
        
        pyautogui.hotkey('ctrl', 'shift', 'n')
        time.sleep(2)
        
        # Update window reference to new window
        self.find_windsurf_window()
        return True
    
    def open_chat(self) -> bool:
        """Open AI chat sidebar (Ctrl+L)"""
        if not self.activate_window():
            return False
        
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.5)
        return True
    
    def paste_prompt(self, prompt: str) -> bool:
        """Paste prompt into chat"""
        if not self.activate_window():
            return False
        
        # Open chat first
        self.open_chat()
        time.sleep(0.3)
        
        # Paste text via clipboard
        pyperclip.copy(prompt)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.2)
        return True
    
    def send_prompt(self, prompt: str) -> bool:
        """Paste and send prompt"""
        if not self.paste_prompt(prompt):
            return False
        
        pyautogui.press('enter')
        return True
    
    def close_palettes(self):
        """Close any open palettes with Escape"""
        for _ in range(3):
            pyautogui.press('escape')
            time.sleep(0.1)


def main():
    """Main entry point"""
    print("=" * 60)
    print("Windsurf Automation")
    print("=" * 60)
    
    wa = WindsurfAutomation()
    
    if wa.find_windsurf_window():
        print(f"✅ Found Windsurf: {wa.window.title}")
    else:
        print("❌ Windsurf not found. Please open Windsurf IDE first.")
        return
    
    print("\nAvailable actions:")
    print("1. Open new window")
    print("2. Open chat")
    print("3. Send test prompt")
    print("0. Exit")
    
    while True:
        choice = input("\nChoice: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            wa.open_new_window()
            print("✅ New window opened")
        elif choice == "2":
            wa.open_chat()
            print("✅ Chat opened")
        elif choice == "3":
            wa.send_prompt("Hello from Windsurf Automation!")
            print("✅ Prompt sent")
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
