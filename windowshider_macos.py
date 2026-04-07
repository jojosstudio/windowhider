#!/usr/bin/env python3
"""
Window Hider for macOS
Hides windows from screen capture on macOS using Quartz APIs
"""

import tkinter as tk
from tkinter import ttk
import subprocess
import json
import os
import sys
from typing import List, Dict, Optional

try:
    from Cocoa import NSWorkspace, NSRunningApplication
    import Quartz
    MACOS_AVAILABLE = True
except ImportError:
    MACOS_AVAILABLE = False
    print("[WARNING] macOS frameworks not available. Install: pip install pyobjc-framework-Cocoa pyobjc-framework-Quartz")

# Constants
SETTINGS_FILE = "settings_mac.json"
VERSION = "1.0.0-macOS"

# Colors (matching Windows version)
BG = "#0a0a0a"
CARD_BG = "#0f0f0f"
GLASS_BG = "#121212"
TEXT_MAIN = "#ffffff"
TEXT_SUB = "#888888"
BTN_HIDE = "#ff4444"
BTN_SHOW = "#44ff44"
HOVER_BG = "#1a1a1a"
ACCENT_GREEN = "#44ff44"
ACCENT_RED = "#ff4444"

class WindowHiderMac:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Window Hider macOS v{VERSION}")
        self.root.geometry("450x700")
        self.root.configure(bg=BG)
        
        self.settings = self.load_settings()
        self.windows: List[Dict] = []
        self.hidden_pids: set = set()
        
        self.setup_ui()
        self.refresh_windows()
        
        # Auto-refresh every 3 seconds
        self.schedule_refresh()
    
    def load_settings(self) -> dict:
        """Load settings from JSON file"""
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'auto_hide': False,
            'auto_hide_programs': [],
            'start_minimized': False,
            'minimize_to_dock': False,
        }
    
    def save_settings(self):
        """Save settings to JSON file"""
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def get_window_list(self) -> List[Dict]:
        """Get list of all windows using Quartz"""
        if not MACOS_AVAILABLE:
            return []
        
        windows = []
        try:
            # Get window list from Quartz
            window_list = Quartz.CGWindowListCopyWindowInfo(
                Quartz.kCGWindowListOptionAll,
                Quartz.kCGNullWindowID
            )
            
            for window in window_list:
                pid = window.get(Quartz.kCGWindowOwnerPID, 0)
                owner_name = window.get(Quartz.kCGWindowOwnerName, "Unknown")
                window_name = window.get(Quartz.kCGWindowName, "")
                window_id = window.get(Quartz.kCGWindowNumber, 0)
                
                # Skip system windows
                if owner_name in ["Window Server", "loginwindow", "Dock"]:
                    continue
                
                # Skip our own app
                if owner_name == "Python" or pid == os.getpid():
                    continue
                
                if window_name or owner_name:
                    display_name = f"{owner_name} - {window_name}" if window_name else owner_name
                    windows.append({
                        'id': window_id,
                        'pid': pid,
                        'name': display_name,
                        'owner': owner_name
                    })
        except Exception as e:
            print(f"[ERROR] Failed to get window list: {e}")
        
        return windows
    
    def hide_window(self, pid: int):
        """Hide window from screen capture by minimizing or using Quartz"""
        try:
            # On macOS, we can use AppleScript to hide/minimize
            # For screen capture hiding, we would need to minimize or move off-screen
            script = f'''
                tell application "System Events"
                    set frontApp to first application process whose unix id is {pid}
                    set visible of frontApp to false
                end tell
            '''
            subprocess.run(['osascript', '-e', script], capture_output=True)
            self.hidden_pids.add(pid)
            print(f"[OK] Hidden PID {pid}")
        except Exception as e:
            print(f"[ERROR] Failed to hide window: {e}")
    
    def show_window(self, pid: int):
        """Show window again"""
        try:
            script = f'''
                tell application "System Events"
                    set frontApp to first application process whose unix id is {pid}
                    set visible of frontApp to true
                end tell
            '''
            subprocess.run(['osascript', '-e', script], capture_output=True)
            self.hidden_pids.discard(pid)
            print(f"[OK] Shown PID {pid}")
        except Exception as e:
            print(f"[ERROR] Failed to show window: {e}")
    
    def show_all_windows(self):
        """Show all hidden windows"""
        for pid in list(self.hidden_pids):
            self.show_window(pid)
        self.hidden_pids.clear()
        self.update_list()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = tk.Frame(self.root, bg=BG)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = tk.Frame(main_frame, bg=CARD_BG, height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg=CARD_BG)
        header_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        tk.Label(header_content, text="◈ Window Hider", font=("SF Pro", 20, "bold"),
                bg=CARD_BG, fg=TEXT_MAIN).pack(side=tk.LEFT)
        
        tk.Label(header_content, text="macOS", font=("SF Pro", 12),
                bg=CARD_BG, fg=ACCENT_GREEN).pack(side=tk.LEFT, padx=(10, 0))
        
        # Status label
        self.status_label = tk.Label(header_content, text="Ready", font=("SF Pro", 10),
                                     bg=CARD_BG, fg=TEXT_SUB)
        self.status_label.pack(side=tk.RIGHT)
        
        # Window list frame
        list_frame = tk.Frame(main_frame, bg=GLASS_BG, relief=tk.FLAT, bd=1,
                              highlightbackground="#1a1a1a", highlightthickness=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # List header
        list_header = tk.Frame(list_frame, bg=GLASS_BG, height=40)
        list_header.pack(fill=tk.X)
        list_header.pack_propagate(False)
        
        tk.Label(list_header, text="WINDOWS", font=("SF Pro", 10, "bold"),
                bg=GLASS_BG, fg=TEXT_SUB).pack(side=tk.LEFT, padx=15, pady=10)
        
        # Refresh button
        refresh_btn = tk.Button(list_header, text="↻", font=("SF Pro", 12),
                               bg=GLASS_BG, fg=TEXT_MAIN, bd=0, cursor="hand2",
                               command=self.refresh_windows)
        refresh_btn.pack(side=tk.RIGHT, padx=10)
        
        # Window listbox with scrollbar
        list_container = tk.Frame(list_frame, bg=GLASS_BG)
        list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(list_container, bg=GLASS_BG, troughcolor=BG)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(list_container, bg=GLASS_BG, fg=TEXT_MAIN,
                                  font=("SF Pro", 11), selectbackground=HOVER_BG,
                                  selectforeground=TEXT_MAIN, bd=0, highlightthickness=0,
                                  yscrollcommand=scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # Buttons frame
        btn_frame = tk.Frame(main_frame, bg=BG)
        btn_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        self.hide_btn = tk.Button(btn_frame, text="HIDE", font=("SF Pro", 12, "bold"),
                                 bg=BTN_HIDE, fg=TEXT_MAIN, bd=0, padx=30, pady=12,
                                 cursor="hand2", activebackground="#ff6666",
                                 command=self.on_hide_clicked)
        self.hide_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        self.show_btn = tk.Button(btn_frame, text="SHOW", font=("SF Pro", 12, "bold"),
                                 bg=BTN_SHOW, fg=BG, bd=0, padx=30, pady=12,
                                 cursor="hand2", activebackground="#00cc66",
                                 command=self.on_show_clicked)
        self.show_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        
        # Show All button
        show_all_btn = tk.Button(main_frame, text="SHOW ALL", font=("SF Pro", 11),
                                bg=CARD_BG, fg=TEXT_MAIN, bd=0, padx=20, pady=10,
                                cursor="hand2", activebackground=HOVER_BG,
                                command=self.show_all_windows)
        show_all_btn.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Footer
        footer = tk.Frame(main_frame, bg=BG, height=30)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        
        tk.Label(footer, text=f"v{VERSION} • macOS Edition", font=("SF Pro", 9),
                bg=BG, fg=TEXT_SUB).pack(pady=5)
        
        if not MACOS_AVAILABLE:
            tk.Label(footer, text="⚠️ macOS frameworks not installed",
                    font=("SF Pro", 9), bg=BG, fg=ACCENT_RED).pack(pady=5)
    
    def refresh_windows(self):
        """Refresh the window list"""
        self.windows = self.get_window_list()
        self.update_list()
        self.status_label.config(text=f"{len(self.windows)} windows found")
    
    def update_list(self):
        """Update the listbox with current windows"""
        self.listbox.delete(0, tk.END)
        for window in self.windows:
            hidden_marker = " [HIDDEN]" if window['pid'] in self.hidden_pids else ""
            self.listbox.insert(tk.END, window['name'] + hidden_marker)
            
            # Color hidden items
            if window['pid'] in self.hidden_pids:
                self.listbox.itemconfig(tk.END, {'fg': ACCENT_RED})
    
    def schedule_refresh(self):
        """Schedule periodic refresh"""
        self.refresh_windows()
        self.root.after(3000, self.schedule_refresh)
    
    def on_hide_clicked(self):
        """Handle hide button click"""
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.windows):
                window = self.windows[index]
                self.hide_window(window['pid'])
                self.update_list()
                self.status_label.config(text=f"Hidden: {window['name']}")
    
    def on_show_clicked(self):
        """Handle show button click"""
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.windows):
                window = self.windows[index]
                self.show_window(window['pid'])
                self.update_list()
                self.status_label.config(text=f"Shown: {window['name']}")

def main():
    root = tk.Tk()
    
    # Set macOS-specific styling
    if sys.platform == 'darwin':
        root.tk.call('tk', 'scaling', 2.0)
    
    app = WindowHiderMac(root)
    
    # Handle quit properly
    def on_closing():
        app.show_all_windows()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
