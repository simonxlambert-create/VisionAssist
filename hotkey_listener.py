import ctypes
from ctypes import wintypes
import time
import threading

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

LRESULT = ctypes.c_longlong
HHOOK = ctypes.c_void_p
HOOKPROC = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

user32.SetWindowsHookExW.restype = HHOOK
user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD]

user32.CallNextHookEx.restype = LRESULT
user32.CallNextHookEx.argtypes = [HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]

user32.UnhookWindowsHookEx.restype = wintypes.BOOL
user32.UnhookWindowsHookEx.argtypes = [HHOOK]

user32.GetAsyncKeyState.restype = wintypes.SHORT
user32.GetAsyncKeyState.argtypes = [ctypes.c_int]

user32.GetKeyboardState.restype = wintypes.BOOL
user32.GetKeyboardState.argtypes = [ctypes.POINTER(ctypes.c_ubyte * 256)]

user32.GetKeyboardLayout.restype = wintypes.HKL
user32.GetKeyboardLayout.argtypes = [wintypes.DWORD]

user32.ToUnicodeEx.restype = ctypes.c_int
user32.ToUnicodeEx.argtypes = [
    wintypes.UINT, wintypes.UINT,
    ctypes.POINTER(ctypes.c_ubyte * 256),
    wintypes.LPWSTR, ctypes.c_int, wintypes.UINT, wintypes.HKL
]

class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ('vkCode', wintypes.DWORD),
        ('scanCode', wintypes.DWORD),
        ('flags', wintypes.DWORD),
        ('time', wintypes.DWORD),
        ('dwExtraInfo', ctypes.c_ulonglong)
    ]

# Win32 Constants
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105

# Virtual Keys
VK_CONTROL = 0x11
VK_SHIFT = 0x10
VK_F8 = 0x77
VK_F9 = 0x78
VK_MULTIPLY = 0x6A   # Numpad *
VK_DIVIDE = 0x6F     # Numpad /
VK_OEM_2 = 0xBF      # QWERTY /?
VK_OEM_8 = 0xDF      # AZERTY key near Enter
VK_OEM_5 = 0xDC      # AZERTY \ / | / *

class HotkeyListener:
    def __init__(self, on_toggle_color, on_toggle_size, on_radar=None):
        self.on_toggle_color = on_toggle_color
        self.on_toggle_size = on_toggle_size
        self.on_radar = on_radar
        
        self._thread = None
        self._stop_event = threading.Event()
        self._c_hook_proc = None
        self._last_trigger_time = {}
        
        # State tracking for Ctrl tap
        self._ctrl_press_time = 0
        self._combo_used = False

    def _is_ctrl_down(self):
        return (user32.GetAsyncKeyState(VK_CONTROL) & 0x8000) != 0

    def _is_shift_down(self):
        return (user32.GetAsyncKeyState(VK_SHIFT) & 0x8000) != 0

    def _debounce(self, key_id, cooldown=0.3):
        now = time.time()
        last = self._last_trigger_time.get(key_id, 0)
        if now - last >= cooldown:
            self._last_trigger_time[key_id] = now
            return True
        return False

    def _get_key_char(self, vk, scan):
        try:
            keyboard_state = (ctypes.c_ubyte * 256)()
            if self._is_ctrl_down():
                keyboard_state[VK_CONTROL] = 0x80
            if self._is_shift_down():
                keyboard_state[VK_SHIFT] = 0x80
                
            hkl = user32.GetKeyboardLayout(0)
            buff = ctypes.create_unicode_buffer(16)
            res = user32.ToUnicodeEx(vk, scan, ctypes.byref(keyboard_state), buff, 16, 0, hkl)
            if res > 0:
                return buff.value[:res]
        except Exception:
            pass
        return ''

    def _hook_callback(self, nCode, wParam, lParam):
        if nCode >= 0:
            try:
                kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                vk = kb.vkCode
                scan = kb.scanCode
                
                is_down = (wParam == WM_KEYDOWN or wParam == WM_SYSKEYDOWN)
                is_up = (wParam == WM_KEYUP or wParam == WM_SYSKEYUP)

                # Track single Ctrl tap for Red Radar
                if vk in (0x11, 0xA2, 0xA3):  # VK_CONTROL, VK_LCONTROL, VK_RCONTROL
                    if is_down and self._ctrl_press_time == 0:
                        self._ctrl_press_time = time.time()
                        self._combo_used = False
                    elif is_up:
                        duration = time.time() - self._ctrl_press_time
                        if not self._combo_used and 0.02 < duration < 0.5:
                            if self.on_radar and self._debounce('radar', 0.25):
                                threading.Thread(target=self.on_radar, daemon=True).start()
                        self._ctrl_press_time = 0
                    return user32.CallNextHookEx(None, nCode, wParam, lParam)

                if is_down:
                    ctrl = self._is_ctrl_down()
                    shift = self._is_shift_down()
                    char = self._get_key_char(vk, scan)

                    # 1. Toggle Red Cursor (Ctrl + * OR F8)
                    is_asterisk = (
                        (ctrl and vk == VK_MULTIPLY) or
                        (ctrl and '*' in char) or
                        (ctrl and vk == 0x38 and shift) or
                        (ctrl and vk == VK_OEM_8) or
                        (vk == VK_F8)
                    )
                    if is_asterisk:
                        self._combo_used = True
                        if self._debounce('color'):
                            print("[VisionAssist] >>> TOGGLE RED CURSOR (Ctrl+* / F8) <<<")
                            threading.Thread(target=self.on_toggle_color, daemon=True).start()
                        return user32.CallNextHookEx(None, nCode, wParam, lParam)

                    # 2. Toggle Cursor Size (Ctrl + / OR F9)
                    is_slash = (
                        (ctrl and vk == VK_DIVIDE) or
                        (ctrl and '/' in char) or
                        (ctrl and vk == VK_OEM_2) or
                        (ctrl and vk == 0xBE and shift) or
                        (ctrl and scan in (53, 181)) or
                        (vk == VK_F9)
                    )
                    if is_slash:
                        self._combo_used = True
                        if self._debounce('size'):
                            print("[VisionAssist] >>> TOGGLE CURSOR SIZE (Ctrl+/ / F9) <<<")
                            threading.Thread(target=self.on_toggle_size, daemon=True).start()
                        return user32.CallNextHookEx(None, nCode, wParam, lParam)

                    if ctrl:
                        self._combo_used = True

            except Exception as ex:
                print(f"[VisionAssist] Error in hook: {ex}")

        return user32.CallNextHookEx(None, nCode, wParam, lParam)

    def _loop(self):
        self._c_hook_proc = HOOKPROC(self._hook_callback)
        hHook = user32.SetWindowsHookExW(WH_KEYBOARD_LL, self._c_hook_proc, None, 0)
        if not hHook:
            print(f"[VisionAssist] Failed to install hook: error {kernel32.GetLastError()}")
            return
        
        print("[VisionAssist] Keyboard hook active!")
        msg = wintypes.MSG()
        while not self._stop_event.is_set():
            if user32.PeekMessageW(ctypes.byref(msg), 0, 0, 0, 1):
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
            time.sleep(0.005)
            
        user32.UnhookWindowsHookEx(hHook)

    def start(self):
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
