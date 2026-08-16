import os
import sys
import winreg
import win32com.client

def setup_startup():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    vbs_path = os.path.join(base_dir, 'Start_VisionAssist.vbs')
    
    # 1. Setup Windows Startup Folder Shortcut
    startup_dir = os.path.join(os.environ.get('APPDATA', ''), r'Microsoft\Windows\Start Menu\Programs\Startup')
    shortcut_path = os.path.join(startup_dir, 'VisionAssist.lnk')
    
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = r"C:\Windows\System32\wscript.exe"
        shortcut.Arguments = f'"{vbs_path}"'
        shortcut.WorkingDirectory = base_dir
        shortcut.Description = "VisionAssist Low Vision Helper"
        shortcut.Save()
        print(f"[OK] Startup folder shortcut saved at: {shortcut_path}")
    except Exception as e:
        print(f"[Error] Failed to create Startup folder shortcut: {e}")

    # 2. Setup Windows Registry Run Key (Automatic Logon Launch)
    run_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, run_key, 0, winreg.KEY_WRITE) as key:
            cmd = f'"C:\\Windows\\System32\\wscript.exe" "{vbs_path}"'
            winreg.SetValueEx(key, "VisionAssist", 0, winreg.REG_SZ, cmd)
        print(f"[OK] Windows Registry Run key configured: VisionAssist -> {cmd}")
    except Exception as e:
        print(f"[Error] Failed to set Registry Run key: {e}")

    print("\nVisionAssist is now configured to start automatically on Windows boot every single time!")

if __name__ == '__main__':
    setup_startup()
