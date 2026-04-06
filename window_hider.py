import sys
import os
import ctypes
import ctypes.wintypes
import traceback
import tkinter as tk
from tkinter import ttk
import win32gui
import win32process
import psutil
import json
import threading
import time
from datetime import datetime
import subprocess
import pystray
from PIL import Image, ImageDraw

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def hide_console():
    try:
        import win32console
        try:
            console = win32console.GetConsoleWindow()
            if console:
                win32gui.ShowWindow(console, 0)
                print("[OK] Console window hidden")
        except:
            user32 = ctypes.windll.user32
            console = user32.GetConsoleWindow()
            if console:
                user32.ShowWindow(console, 0)
                print("[OK] Console window hidden (alternative method)")
    except Exception as e:
        print(f"[ERROR] Failed to hide console: {e}")
                
    except Exception as e:
        print(f"[ERROR] Failed to hide console: {e}")

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(f'"{a}"' for a in sys.argv), None, 1
    )
    sys.exit()

print("[OK] Laeuft als Administrator")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DLL_PATH = os.path.join(SCRIPT_DIR, "hider.dll")
WDA_NONE = 0x00000000
WDA_EXCLUDEFROMCAPTURE = 0x00000011

k32 = ctypes.windll.kernel32
k32.OpenProcess.restype = ctypes.wintypes.HANDLE
k32.VirtualAllocEx.restype = ctypes.c_void_p
k32.CreateRemoteThread.restype = ctypes.wintypes.HANDLE
k32.GetModuleHandleW.restype = ctypes.wintypes.HMODULE
k32.GetProcAddress.restype = ctypes.c_void_p
k32.GetProcAddress.argtypes = [ctypes.wintypes.HMODULE, ctypes.c_char_p]
k32.LoadLibraryW.restype = ctypes.wintypes.HMODULE
k32.LoadLibraryW.argtypes = [ctypes.wintypes.LPCWSTR]

hidden_pids = {}
settings = {
    "auto_hide": False,
    "auto_hide_programs": [],
    "start_minimized": False,
    "theme": "dark",
    "animation_speed": 150,
    "window_opacity": 0.95,
    "self_hide": True,
    "hide_console": True,
    "minimize_to_tray": True
}
settings_file = os.path.join(SCRIPT_DIR, "settings.json")

def load_settings():
    global settings
    try:
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                settings.update(json.load(f))
    except:
        pass

def save_settings():
    try:
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
    except:
        pass

load_settings()

if settings.get('hide_console', True):
    hide_console()

def inject_and_call(pid, flag):
    try:
        dll_path_bytes = DLL_PATH.encode("utf-8") + b"\x00"
        h_process = k32.OpenProcess(0x1F0FFF, False, pid)
        if not h_process:
            return False
        remote_mem = k32.VirtualAllocEx(h_process, None, len(dll_path_bytes), 0x3000, 0x40)
        written = ctypes.c_size_t(0)
        k32.WriteProcessMemory(h_process, ctypes.c_void_p(remote_mem), dll_path_bytes, len(dll_path_bytes), ctypes.byref(written))
        kernel32_handle = k32.GetModuleHandleW("kernel32.dll")
        load_lib = k32.GetProcAddress(kernel32_handle, b"LoadLibraryA")
        h_thread = k32.CreateRemoteThread(h_process, None, 0, ctypes.c_void_p(load_lib), ctypes.c_void_p(remote_mem), 0, None)
        if not h_thread:
            return False
        k32.WaitForSingleObject(h_thread, 5000)
        k32.CloseHandle(h_thread)
        k32.VirtualFreeEx(h_process, ctypes.c_void_p(remote_mem), 0, 0x8000)
        k32.CloseHandle(h_process)

        h_process2 = k32.OpenProcess(0x1F0FFF, False, pid)
        modules = win32process.EnumProcessModules(h_process2)
        h_dll_remote = None
        for mod in modules:
            try:
                mod_name = win32process.GetModuleFileNameEx(h_process2, mod)
                if "hider.dll" in mod_name.lower():
                    h_dll_remote = mod
                    break
            except:
                continue
        if not h_dll_remote:
            k32.CloseHandle(h_process2)
            return False

        local_handle = k32.LoadLibraryW(DLL_PATH)
        local_func = k32.GetProcAddress(local_handle, b"SetExcludeCapture")
        offset = local_func - local_handle
        remote_func = h_dll_remote + offset

        h_thread2 = k32.CreateRemoteThread(h_process2, None, 0,
            ctypes.c_void_p(remote_func), ctypes.c_void_p(flag), 0, None)
        if h_thread2:
            k32.WaitForSingleObject(h_thread2, 3000)
            k32.CloseHandle(h_thread2)
            k32.CloseHandle(h_process2)
            print(f"[OK] Flag {hex(flag)} -> PID {pid}")
            return True
        k32.CloseHandle(h_process2)
        return False
    except Exception:
        print(f"[EXCEPTION] {traceback.format_exc()}")
        return False

def get_all_windows():
    own_pid = os.getpid()
    results = []
    seen_pids = set()
    def callback(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        title = win32gui.GetWindowText(hwnd)
        if not title.strip():
            return
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid == own_pid or pid in seen_pids:
                return
            seen_pids.add(pid)
            proc = psutil.Process(pid)
            name = proc.name()
        except:
            return
        results.append((pid, title, name))
    win32gui.EnumWindows(callback, None)
    return results

BG         = "#0a0a0a"
PANEL_BG   = "#151515"
TILE_ACT   = "#1a1a1a"
TILE_INACT = "#0f0f0f"
BORDER_ACT = "#333333"
BORDER_IN  = "#1a1a1a"
TEXT_MAIN  = "#ffffff"
TEXT_SUB   = "#888888"
TEXT_ACT   = "#ffffff"
BTN_HIDE   = "#ff4444"
BTN_SHOW   = "#44ff44"
BTN_REF    = "#1a1a1a"
ACCENT     = "#ffffff"
GLASS_BG   = "#121212"
GLASS_BORDER = "#1a1a1a"
CARD_BG    = "#0f0f0f"
HOVER_BG   = "#252525"
SETTINGS_BG = "#0d0d0d"

root = tk.Tk()
root.title("◈ Window Hider")
root.geometry("650x850")
root.configure(bg=BG)
root.resizable(True, True)
root.attributes('-alpha', 0.9)

def hide_self():
    own_pid = os.getpid()
    if inject_and_call(own_pid, WDA_EXCLUDEFROMCAPTURE):
        print("[OK] Window Hider hidden from capture")
        status_label.config(text="◈ Self hidden from stream")
        return True
    return False

def create_compact_panel(parent):
    panel = tk.Frame(parent, bg=GLASS_BORDER, relief=tk.FLAT, bd=0)
    panel.pack(fill=tk.BOTH, expand=True)
    
    glass1 = tk.Frame(panel, bg=GLASS_BG, relief=tk.FLAT, bd=0)
    glass1.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
    
    glass2 = tk.Frame(glass1, bg=CARD_BG, relief=tk.FLAT, bd=0)
    glass2.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
    
    canvas = tk.Canvas(glass2, bg=CARD_BG, bd=0, highlightthickness=0)
    scrollbar = tk.Scrollbar(glass2, orient=tk.VERTICAL, command=canvas.yview,
                             bg=CARD_BG, troughcolor=GLASS_BORDER,
                             activebackground=ACCENT, width=8)
    canvas.configure(yscrollcommand=scrollbar.set)
    
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    inner = tk.Frame(canvas, bg=CARD_BG)
    cw = canvas.create_window((0, 0), window=inner, anchor="nw")
    
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(cw, width=e.width))
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
    
    return inner

settings_panel = None
settings_visible = False

def toggle_settings():
    global settings_panel, settings_visible
    
    if settings_visible:
        hide_settings()
    else:
        show_settings()

def show_settings():
    global settings_panel, settings_visible
    
    if settings_visible:
        return
    
    content_frame.pack_forget()
    
    settings_panel = tk.Frame(main_container, bg=SETTINGS_BG, relief=tk.FLAT, bd=0,
                              highlightbackground=TEXT_MAIN, highlightthickness=1)
    settings_panel.pack(fill=tk.BOTH, expand=True)
    
    pass
    
    header = tk.Frame(settings_panel, bg=SETTINGS_BG, height=70, relief=tk.RAISED, bd=1)
    header.pack(fill=tk.X, padx=0, pady=0)
    header.pack_propagate(False)
    
    header_content = tk.Frame(header, bg=SETTINGS_BG)
    header_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
    
    tk.Label(header_content, text="⚙ SETTINGS", font=("Segoe UI", 18, "bold"),
             bg=SETTINGS_BG, fg=TEXT_MAIN).pack(side=tk.LEFT, pady=10)
    
    close_btn = tk.Button(header_content, text="✕", font=("Segoe UI", 14, "bold"),
                         bg=BTN_HIDE, fg=TEXT_MAIN, bd=0, padx=12, pady=8, cursor="hand2",
                         activebackground="#ff6666", relief=tk.FLAT, borderwidth=0,
                         command=hide_settings)
    close_btn.pack(side=tk.RIGHT, pady=10)
    
    content_canvas = tk.Canvas(settings_panel, bg=SETTINGS_BG, bd=0, highlightthickness=0)
    content_scrollbar = tk.Scrollbar(settings_panel, orient=tk.VERTICAL, command=content_canvas.yview,
                                   bg=SETTINGS_BG, troughcolor=GLASS_BG, activebackground=TEXT_MAIN,
                                   width=15)
    content_canvas.configure(yscrollcommand=content_scrollbar.set)
    
    content_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    content_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    content = tk.Frame(content_canvas, bg=SETTINGS_BG)
    content_window = content_canvas.create_window((0, 0), window=content, anchor="nw", width=content_canvas.winfo_reqwidth())
    
    def configure_canvas(event):
        canvas_width = event.width
        content_canvas.itemconfig(content_window, width=canvas_width)
        content_canvas.configure(scrollregion=content_canvas.bbox("all"))
    
    content.bind("<Configure>", lambda e: content_canvas.configure(scrollregion=content_canvas.bbox("all")))
    content_canvas.bind("<Configure>", configure_canvas)
    
    content_frame_inner = tk.Frame(content, bg=SETTINGS_BG)
    content_frame_inner.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
    
    auto_frame = tk.Frame(content_frame_inner, bg=CARD_BG, relief=tk.RAISED, bd=1)
    auto_frame.pack(fill=tk.X, pady=(0, 20))
    
    section_header = tk.Frame(auto_frame, bg=CARD_BG, height=50)
    section_header.pack(fill=tk.X, padx=0, pady=0)
    section_header.pack_propagate(False)
    
    tk.Label(section_header, text="🔄 AUTO-HIDE", font=("Segoe UI", 14, "bold"),
             bg=CARD_BG, fg=TEXT_MAIN).pack(side=tk.LEFT, padx=20, pady=15)
    
    toggle_frame = tk.Frame(auto_frame, bg=CARD_BG)
    toggle_frame.pack(fill=tk.X, padx=20, pady=(10, 15))
    
    tk.Label(toggle_frame, text="Enable Auto-Hide", font=("Segoe UI", 11),
             bg=CARD_BG, fg=TEXT_SUB).pack(side=tk.LEFT)
    
    auto_hide_var = tk.BooleanVar(value=settings.get('auto_hide', False))
    auto_toggle = tk.Checkbutton(toggle_frame, variable=auto_hide_var,
                                bg=CARD_BG, fg=TEXT_MAIN, selectcolor=CARD_BG,
                                activebackground=CARD_BG, activeforeground=TEXT_MAIN,
                                font=("Segoe UI", 11),
                                command=lambda: update_setting('auto_hide', auto_hide_var.get()))
    auto_toggle.pack(side=tk.RIGHT)
    
    list_frame = tk.Frame(auto_frame, bg="#0a0a0a", relief=tk.SUNKEN, bd=1)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
    
    tk.Label(list_frame, text="📋 Auto-Hide Programs", font=("Segoe UI", 11, "bold"),
             bg="#0a0a0a", fg=TEXT_MAIN).pack(anchor=tk.W, padx=10, pady=(8, 5))
    
    list_container = tk.Frame(list_frame, bg=GLASS_BG, relief=tk.FLAT, bd=0)
    list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    
    program_listbox = tk.Listbox(list_container, bg=GLASS_BG, fg=TEXT_MAIN,
                                font=("Segoe UI", 10), selectbackground=HOVER_BG,
                                selectforeground=TEXT_MAIN, bd=0, highlightthickness=0)
    program_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
    
    list_scrollbar = tk.Scrollbar(list_container, orient=tk.VERTICAL,
                                 bg=GLASS_BG, troughcolor=SETTINGS_BG,
                                 activebackground=TEXT_MAIN, width=10)
    list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    program_listbox.config(yscrollcommand=list_scrollbar.set)
    list_scrollbar.config(command=program_listbox.yview)
    
    btn_frame = tk.Frame(list_frame, bg="#0a0a0a")
    btn_frame.pack(fill=tk.X, pady=(0, 10))
    
    tk.Button(btn_frame, text="+ Add Current", font=("Segoe UI", 10, "bold"),
             bg=BTN_SHOW, fg=BG, bd=0, padx=12, pady=6, cursor="hand2",
             activebackground="#00cc66", relief=tk.FLAT, borderwidth=0,
             command=lambda: add_auto_hide_program_inline(program_listbox)).pack(side=tk.LEFT, padx=(10, 5))
    
    tk.Button(btn_frame, text="- Remove", font=("Segoe UI", 10, "bold"),
             bg=BTN_HIDE, fg=TEXT_MAIN, bd=0, padx=12, pady=6, cursor="hand2",
             activebackground="#ff6666", relief=tk.FLAT, borderwidth=0,
             command=lambda: remove_auto_hide_program_inline(program_listbox)).pack(side=tk.LEFT, padx=5)
    
    other_frame = tk.Frame(content_frame_inner, bg=CARD_BG, relief=tk.RAISED, bd=1)
    other_frame.pack(fill=tk.X, pady=(0, 20))
    
    general_header = tk.Frame(other_frame, bg=CARD_BG, height=50)
    general_header.pack(fill=tk.X, padx=0, pady=0)
    general_header.pack_propagate(False)
    
    tk.Label(general_header, text="⚙ GENERAL", font=("Segoe UI", 14, "bold"),
             bg=CARD_BG, fg=TEXT_MAIN).pack(side=tk.LEFT, padx=20, pady=15)
    
    settings_options = [
        ("Hide Self from Stream", "self_hide"),
        ("Start Minimized", "start_minimized"),
        ("Hide Console Window", "hide_console"),
        ("Minimize to Tray", "minimize_to_tray")
    ]
    
    for label_text, setting_key in settings_options:
        option_frame = tk.Frame(other_frame, bg=CARD_BG)
        option_frame.pack(fill=tk.X, padx=20, pady=(8, 8))
        
        tk.Label(option_frame, text=label_text, font=("Segoe UI", 11),
                 bg=CARD_BG, fg=TEXT_SUB).pack(side=tk.LEFT)
        
        var = tk.BooleanVar(value=settings.get(setting_key, False))
        
        toggle = tk.Checkbutton(option_frame, variable=var,
                              bg=CARD_BG, fg=TEXT_MAIN, selectcolor=CARD_BG,
                              activebackground=CARD_BG, activeforeground=TEXT_MAIN,
                              font=("Segoe UI", 11),
                              command=lambda key=setting_key, v=var: update_setting(key, v.get()))
        toggle.pack(side=tk.RIGHT)
    
    opacity_frame = tk.Frame(other_frame, bg="#0a0a0a", relief=tk.SUNKEN, bd=1)
    opacity_frame.pack(fill=tk.X, padx=20, pady=(8, 20))
    
    tk.Label(opacity_frame, text="🔧 Window Opacity", font=("Segoe UI", 11, "bold"),
             bg="#0a0a0a", fg=TEXT_MAIN).pack(anchor=tk.W, padx=10, pady=(8, 5))
    
    opacity_control = tk.Frame(opacity_frame, bg="#0a0a0a")
    opacity_control.pack(fill=tk.X, padx=10, pady=(0, 10))
    
    tk.Label(opacity_control, text="Opacity", font=("Segoe UI", 11),
             bg="#0a0a0a", fg=TEXT_SUB).pack(side=tk.LEFT)
    
    opacity_var = tk.DoubleVar(value=settings.get('window_opacity', 0.95) * 100)
    opacity_scale = tk.Scale(opacity_control, from_=50, to=100, orient=tk.HORIZONTAL,
                             variable=opacity_var, bg="#0a0a0a", fg=TEXT_MAIN,
                             troughcolor=GLASS_BG, activebackground=HOVER_BG,
                             highlightthickness=0, bd=0, length=200,
                             command=lambda v: update_setting('window_opacity', float(v) / 100))
    opacity_scale.pack(side=tk.RIGHT, padx=(20, 0))
    
    save_btn_frame = tk.Frame(content_frame_inner, bg=SETTINGS_BG)
    save_btn_frame.pack(fill=tk.X, pady=(10, 0))
    
    save_btn = tk.Button(save_btn_frame, text="💾 SAVE SETTINGS", font=("Segoe UI", 12, "bold"),
                        bg=BTN_SHOW, fg=BG, bd=0, padx=25, pady=12, cursor="hand2",
                        activebackground="#00cc66", relief=tk.FLAT, borderwidth=0,
                        command=save_settings_inline)
    save_btn.pack(pady=10)
    
    for program in settings.get('auto_hide_programs', []):
        program_listbox.insert(tk.END, program)
    
    settings_visible = True
    print("[OK] Settings panel opened")

def hide_settings():
    global settings_panel, settings_visible
    
    if settings_panel and settings_visible:
        settings_panel.destroy()
        settings_visible = False
        
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        print("[OK] Settings panel closed")

def add_auto_hide_program_inline(listbox):
    windows = get_all_windows()
    if windows:
        dialog = tk.Frame(settings_panel, bg=CARD_BG, relief=tk.FLAT, bd=0)
        dialog.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=300, height=400)
        
        tk.Label(dialog, text="Select program to auto-hide:", font=("Segoe UI", 10),
                 bg=CARD_BG, fg=TEXT_MAIN).pack(pady=10)
        
        prog_list = tk.Listbox(dialog, bg=GLASS_BG, fg=TEXT_MAIN,
                              font=("Segoe UI", 9), selectbackground=HOVER_BG,
                              selectforeground=TEXT_MAIN, bd=0, highlightthickness=0)
        prog_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for _, title, name in windows:
            prog_list.insert(tk.END, f"{name} - {title[:30]}")
        
        def select():
            selection = prog_list.curselection()
            if selection:
                program_text = prog_list.get(selection[0])
                program_name = program_text.split(' - ')[0]
                if program_name not in settings['auto_hide_programs']:
                    settings['auto_hide_programs'].append(program_name)
                    listbox.insert(tk.END, program_name)
            dialog.destroy()
        
        def close_dialog():
            dialog.destroy()
        
        btn_frame = tk.Frame(dialog, bg=CARD_BG)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Select", font=("Segoe UI", 10),
                 bg=HOVER_BG, fg=TEXT_MAIN, bd=0, padx=15, pady=5, cursor="hand2",
                 command=select).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Cancel", font=("Segoe UI", 10),
                 bg=HOVER_BG, fg=TEXT_MAIN, bd=0, padx=15, pady=5, cursor="hand2",
                 command=close_dialog).pack(side=tk.LEFT)

def remove_auto_hide_program_inline(listbox):
    selection = listbox.curselection()
    if selection:
        program = listbox.get(selection[0])
        if program in settings['auto_hide_programs']:
            settings['auto_hide_programs'].remove(program)
        listbox.delete(selection[0])

def save_settings_inline():
    save_settings()
    print("[OK] Settings saved")
    hide_settings()

def update_setting(key, value):
    settings[key] = value
    if key == 'window_opacity':
        root.attributes('-alpha', value)
    elif key == 'hide_console':
        if value:
            hide_console()
        else:
            try:
                import win32console
                console = win32console.GetConsoleWindow()
                if console:
                    win32gui.ShowWindow(console, 1)
            except:
                user32 = ctypes.windll.user32
                console = user32.GetConsoleWindow()
                if console:
                    user32.ShowWindow(console, 1)

    elif key == 'self_hide':
        if value:
            hide_self()

def auto_hide_monitor():
    while True:
        if settings.get('auto_hide', False):
            windows = get_all_windows()
            for pid, title, name in windows:
                if name in settings.get('auto_hide_programs', []):
                    if pid not in hidden_pids:
                        if inject_and_call(pid, WDA_EXCLUDEFROMCAPTURE):
                            hidden_pids[pid] = (title, name)
        time.sleep(2)

if settings.get('auto_hide', False):
    monitor_thread = threading.Thread(target=auto_hide_monitor, daemon=True)
    monitor_thread.start()

icon = None
tray_thread = None

def create_icon_image():
    image = Image.new('RGB', (64, 64), color='black')
    draw = ImageDraw.Draw(image)
    
    draw.rectangle([10, 10, 20, 54], fill='white')
    draw.rectangle([44, 10, 54, 54], fill='white')
    draw.rectangle([10, 27, 54, 37], fill='white')
    
    return image

def setup_tray():
    global icon
    
    def show_window(icon_item, item_id):
        root.deiconify()
        root.lift()
        root.focus_force()
    
    def hide_window(icon_item, item_id):
        if settings.get('minimize_to_tray', True):
            root.withdraw()
    
    def quit_app(icon_item, item_id):
        save_settings()
        icon.stop()
        root.quit()
    
    image = create_icon_image()
    
    menu = pystray.Menu(
        pystray.MenuItem("Show", show_window, default=True),
        pystray.MenuItem("Hide", hide_window),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", quit_app)
    )
    
    icon = pystray.Icon("window_hider", image, "Window Hider", menu)
    return icon

def start_tray():
    global icon
    icon = setup_tray()
    icon.run()

def minimize_to_tray():
    if settings.get('minimize_to_tray', True):
        root.withdraw()
    else:
        root.iconify()

def initialize_tray():
    global tray_thread
    tray_thread = threading.Thread(target=start_tray, daemon=True)
    tray_thread.start()

root.after(1000, initialize_tray)

# Auto-hide self if enabled
if settings.get('self_hide', False):
    root.after(1500, lambda: hide_self())

main_container = tk.Frame(root, bg=BG)
main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

header = tk.Frame(main_container, bg=BG)
header.pack(fill=tk.X, pady=(0, 15))

tk.Label(header, text="◈ WINDOW HIDER", font=("Segoe UI", 18, "bold"),
         bg=BG, fg=TEXT_ACT).pack(side=tk.LEFT)

settings_btn = tk.Button(header, text="⚙",
          font=("Segoe UI", 12, "bold"), bg=GLASS_BG, fg=TEXT_MAIN,
          bd=0, padx=12, pady=8, cursor="hand2",
          activebackground=HOVER_BG, activeforeground=TEXT_ACT,
          relief=tk.FLAT, borderwidth=0,
          command=toggle_settings)
settings_btn.pack(side=tk.RIGHT, padx=(5, 0))

refresh_btn = tk.Button(header, text="⟳",
          font=("Segoe UI", 12, "bold"), bg=GLASS_BG, fg=TEXT_MAIN,
          bd=0, padx=12, pady=8, cursor="hand2",
          activebackground=HOVER_BG, activeforeground=TEXT_ACT,
          relief=tk.FLAT, borderwidth=0,
          command=lambda: refresh_all())
refresh_btn.pack(side=tk.RIGHT, padx=(5, 0))

show_all_btn = tk.Button(header, text="✓ All",
          font=("Segoe UI", 12, "bold"), bg=BTN_SHOW, fg=BG,
          bd=0, padx=12, pady=8, cursor="hand2",
          activebackground="#00cc66", activeforeground=BG,
          relief=tk.FLAT, borderwidth=0,
          command=lambda: show_all())


status_label = tk.Label(main_container, text="◈ Ready", font=("Segoe UI", 9, "bold"), 
                        bg=BG, fg=TEXT_SUB)
status_label.pack(anchor=tk.W, pady=(0, 10))

content_frame = tk.Frame(main_container, bg=BG)
content_frame.pack(fill=tk.BOTH, expand=True)

panel = create_compact_panel(content_frame)

panel_inactive = panel
panel_active = panel

def make_tile(parent, pid, title, name, is_hidden):
    bg = TILE_ACT if is_hidden else TILE_INACT
    text_color = TEXT_ACT if is_hidden else TEXT_MAIN
    
    tile = tk.Frame(parent, bg=bg, relief=tk.FLAT, bd=0)
    tile.pack(fill=tk.X, pady=1, padx=8)
    
    content = tk.Frame(tile, bg=bg)
    content.pack(fill=tk.X, padx=12, pady=6)
    
    status = "◉" if is_hidden else "○"
    status_color = TEXT_ACT if is_hidden else TEXT_SUB
    tk.Label(content, text=status, font=("Segoe UI", 10, "bold"),
             bg=bg, fg=status_color).pack(side=tk.LEFT)
    
    short_title = title[:40] + "..." if len(title) > 40 else title
    tk.Label(content, text=short_title, font=("Segoe UI", 9),
             bg=bg, fg=text_color, anchor=tk.W).pack(side=tk.LEFT, padx=(8, 0))
    
    tk.Label(content, text=f"·{name}", font=("Segoe UI", 8),
             bg=bg, fg=TEXT_SUB, anchor=tk.W).pack(side=tk.LEFT, padx=(4, 0))
    
    if is_hidden:
        btn = tk.Button(content, text="SHOW",
                  font=("Segoe UI", 8, "bold"), bg=BTN_SHOW, fg=BG,
                  bd=0, padx=8, pady=2, cursor="hand2",
                  activebackground="#00cc66", activeforeground=BG,
                  relief=tk.FLAT, borderwidth=0,
                  command=lambda p=pid: do_show(p))
    else:
        btn = tk.Button(content, text="HIDE",
                  font=("Segoe UI", 8, "bold"), bg=BTN_HIDE, fg=TEXT_MAIN,
                  bd=0, padx=8, pady=2, cursor="hand2",
                  activebackground="#ff6b6b", activeforeground=TEXT_MAIN,
                  relief=tk.FLAT, borderwidth=0,
                  command=lambda p=pid: do_hide(p))
    btn.pack(side=tk.RIGHT)
    
    def on_enter(e):
        tile.config(bg=HOVER_BG)
        content.config(bg=HOVER_BG)
    
    def on_leave(e):
        tile.config(bg=bg)
        content.config(bg=bg)
    
    tile.bind("<Enter>", on_enter)
    tile.bind("<Leave>", on_leave)
    content.bind("<Enter>", on_enter)
    content.bind("<Leave>", on_leave)

def clear_panel(panel):
    for w in panel.winfo_children():
        w.destroy()
        
def add_separator(parent):
    separator = tk.Frame(parent, bg=GLASS_BORDER, height=1)
    separator.pack(fill=tk.X, padx=20, pady=4)

def refresh_all():
    windows = get_all_windows()
    clear_panel(panel)
    active_pids = set(hidden_pids.keys())
    inactive_count = 0
    active_count = 0
    
    for pid, title, name in windows:
        if pid not in active_pids:
            make_tile(panel, pid, title, name, False)
            inactive_count += 1
    
    for pid, title, name in windows:
        if pid in active_pids:
            make_tile(panel, pid, title, name, True)
            active_count += 1
    
    status_label.config(text=f"◈ {inactive_count} visible, {active_count} hidden")

def do_hide(pid):
    windows = get_all_windows()
    info = next(((t, n) for p, t, n in windows if p == pid), None)
    if not info:
        return
    title, name = info
    if inject_and_call(pid, WDA_EXCLUDEFROMCAPTURE):
        hidden_pids[pid] = (title, name)
    refresh_all()

def do_show(pid):
    if inject_and_call(pid, WDA_NONE):
        hidden_pids.pop(pid, None)
    refresh_all()

def show_all():
    for pid in list(hidden_pids.keys()):
        inject_and_call(pid, WDA_NONE)
    hidden_pids.clear()
    refresh_all()

def on_closing():
    show_all()
    save_settings()
    if icon:
        icon.stop()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
refresh_all()
root.mainloop()
