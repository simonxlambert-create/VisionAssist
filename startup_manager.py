import os
import sys
import win32com.client

def get_startup_dir() -> str:
    appdata = os.environ.get('APPDATA', '')
    return os.path.join(appdata, r'Microsoft\Windows\Start Menu\Programs\Startup')

def get_shortcut_path() -> str:
    return os.path.join(get_startup_dir(), 'VisionAssist.lnk')

def is_startup_enabled() -> bool:
    return os.path.exists(get_shortcut_path())

def set_startup(enabled: bool, main_script_path: str = None) -> bool:
    shortcut_path = get_shortcut_path()
    if not enabled:
        if os.path.exists(shortcut_path):
            try:
                os.remove(shortcut_path)
            except Exception as e:
                print(f"Error removing startup shortcut: {e}")
                return False
        return True
    
    # Enable startup
    if main_script_path is None:
        main_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main.py')
    
    python_dir = os.path.dirname(sys.executable)
    pythonw_exe = os.path.join(python_dir, 'pythonw.exe')
    if not os.path.exists(pythonw_exe):
        pythonw_exe = sys.executable

    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = pythonw_exe
        shortcut.Arguments = f'"{main_script_path}"'
        shortcut.WorkingDirectory = os.path.dirname(main_script_path)
        shortcut.Description = "VisionAssist Accessibility Cursors & Shortcuts"
        shortcut.Save()
        return True
    except Exception as e:
        print(f"Error creating startup shortcut: {e}")
        return False
