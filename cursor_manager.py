import os
import sys
import winreg
import ctypes
from ctypes import wintypes
from typing import Optional

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

IMAGE_CURSOR = 2
LR_LOADFROMFILE = 0x00000010

# OCR System Cursor Constants
OCR_NORMAL = 32512
OCR_IBEAM = 32513
OCR_WAIT = 32514
OCR_CROSS = 32515
OCR_UP = 32516
OCR_SIZENWSE = 32642
OCR_SIZENESW = 32643
OCR_SIZEWE = 32644
OCR_SIZENS = 32645
OCR_SIZEALL = 32646
OCR_NO = 32648
OCR_HAND = 32649
OCR_APPSTARTING = 32650

ALL_OCR_IDS = [
    OCR_NORMAL, OCR_IBEAM, OCR_WAIT, OCR_CROSS, OCR_UP,
    OCR_SIZENWSE, OCR_SIZENESW, OCR_SIZEWE, OCR_SIZENS, OCR_SIZEALL,
    OCR_NO, OCR_HAND, OCR_APPSTARTING
]

# Set up Win32 prototypes
user32.LoadImageW.restype = wintypes.HANDLE
user32.LoadImageW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT, ctypes.c_int, ctypes.c_int, wintypes.UINT]

user32.SetSystemCursor.restype = wintypes.BOOL
user32.SetSystemCursor.argtypes = [wintypes.HANDLE, wintypes.DWORD]

user32.CopyIcon.restype = wintypes.HICON
user32.CopyIcon.argtypes = [wintypes.HICON]

user32.SystemParametersInfoW.restype = wintypes.BOOL
user32.SystemParametersInfoW.argtypes = [wintypes.UINT, wintypes.UINT, ctypes.c_void_p, wintypes.UINT]

class CursorManager:
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = base_dir
        self.cursors_dir = os.path.join(base_dir, 'cursors')
        self.red_cursors_dir = os.path.join(self.cursors_dir, 'red')
        self.yellow_cursors_dir = os.path.join(self.cursors_dir, 'yellow')
        self._is_red = False
        self._current_size = 32
        self._ensure_cursors_exist()

    def _ensure_cursors_exist(self):
        red_arrow = os.path.join(self.red_cursors_dir, 'red_arrow.cur')
        if not os.path.exists(red_arrow):
            from generate_cursors import generate_red_cursors, generate_yellow_cursors
            generate_red_cursors(self.red_cursors_dir, 64)
            generate_yellow_cursors(self.yellow_cursors_dir, 64)

    def _apply_live_cursor(self, ocr_id: int, cur_path: str, size: int):
        """Loads and sets a live cursor handle via Win32 SetSystemCursor."""
        if not os.path.exists(cur_path):
            return
        hCur = user32.LoadImageW(0, cur_path, IMAGE_CURSOR, int(size), int(size), LR_LOADFROMFILE)
        if hCur:
            hCopy = user32.CopyIcon(hCur)
            if hCopy:
                user32.SetSystemCursor(hCopy, ocr_id)

    def set_scheme_red(self, size: int = None) -> bool:
        """Instantly replaces all system cursors with high-contrast Red pointers."""
        if size is None:
            size = self._current_size
        self._current_size = size
        self._is_red = True
        
        mapping = {
            OCR_NORMAL: os.path.join(self.red_cursors_dir, 'red_arrow.cur'),
            OCR_HAND: os.path.join(self.red_cursors_dir, 'red_hand.cur'),
            OCR_IBEAM: os.path.join(self.red_cursors_dir, 'red_ibeam.cur'),
            OCR_CROSS: os.path.join(self.red_cursors_dir, 'red_cross.cur'),
            OCR_NO: os.path.join(self.red_cursors_dir, 'red_no.cur'),
            OCR_SIZEALL: os.path.join(self.red_cursors_dir, 'red_move.cur'),
            OCR_SIZENS: os.path.join(self.red_cursors_dir, 'red_sizens.cur'),
            OCR_SIZEWE: os.path.join(self.red_cursors_dir, 'red_sizewe.cur'),
            OCR_SIZENWSE: os.path.join(self.red_cursors_dir, 'red_sizenwse.cur'),
            OCR_SIZENESW: os.path.join(self.red_cursors_dir, 'red_sizenesw.cur'),
            OCR_UP: os.path.join(self.red_cursors_dir, 'red_arrow.cur'),
            OCR_WAIT: os.path.join(self.red_cursors_dir, 'red_arrow.cur'),
            OCR_APPSTARTING: os.path.join(self.red_cursors_dir, 'red_arrow.cur')
        }
        
        for ocr_id, path in mapping.items():
            self._apply_live_cursor(ocr_id, path, size)
            
        print(f"[VisionAssist] Applied Red Cursor Scheme (Size: {size}px)")
        return True

    def set_scheme_default(self) -> bool:
        """Instantly restores default Windows cursors."""
        self._is_red = False
        user32.SystemParametersInfoW(0x0057, 0, None, 0)
        print("[VisionAssist] Restored Default Windows Cursor Scheme")
        return True

    def set_cursor_size(self, size: int) -> bool:
        """Changes cursor size and updates the display immediately."""
        self._current_size = size
        if self._is_red:
            return self.set_scheme_red(size)
        else:
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Control Panel\Cursors', 0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, 'CursorBaseSize', 0, winreg.REG_DWORD, int(size))
            except Exception:
                pass
            
            if size > 32:
                arrow_path = r'C:\Windows\Cursors\aero_arrow_xl.cur' if size >= 80 else r'C:\Windows\Cursors\aero_arrow_l.cur'
                if not os.path.exists(arrow_path):
                    arrow_path = r'C:\Windows\Cursors\aero_arrow.cur'
                self._apply_live_cursor(OCR_NORMAL, arrow_path, size)
                self._apply_live_cursor(OCR_HAND, r'C:\Windows\Cursors\aero_link.cur', size)
            else:
                user32.SystemParametersInfoW(0x0057, 0, None, 0)
                
            print(f"[VisionAssist] Cursor size set to {size}px")
            return True

    def is_red_active(self) -> bool:
        return self._is_red

    def get_current_size(self) -> int:
        return self._current_size
