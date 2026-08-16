import tkinter as tk
import ctypes
from ctypes import wintypes
import threading
import time

user32 = ctypes.windll.user32
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOPMOST = 0x00000008
WS_EX_TOOLWINDOW = 0x00000080

class RedRadar:
    def __init__(self):
        self._is_active = False
        self._lock = threading.Lock()

    def show_radar(self):
        """Spawns an animated, click-through glowing Red Radar circle around the mouse."""
        with self._lock:
            if self._is_active:
                return
            self._is_active = True

        def _run():
            try:
                root = tk.Tk()
                root.overrideredirect(True)
                root.attributes('-topmost', True)
                root.attributes('-transparentcolor', '#010101')
                root.config(bg='#010101')

                # Ensure non-intrusive click-through behavior
                hwnd = user32.GetParent(root.winfo_id())
                if hwnd:
                    ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                    user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_TOPMOST)

                pt = wintypes.POINT()
                user32.GetCursorPos(ctypes.byref(pt))

                size = 360
                x = pt.x - size // 2
                y = pt.y - size // 2
                root.geometry(f'{size}x{size}+{x}+{y}')

                canvas = tk.Canvas(root, width=size, height=size, bg='#010101', highlightthickness=0)
                canvas.pack()
                cx, cy = size // 2, size // 2

                frame = 0
                max_frames = 12

                def animate():
                    nonlocal frame
                    canvas.delete('all')
                    if frame > max_frames:
                        root.destroy()
                        with self._lock:
                            self._is_active = False
                        return

                    # Expanding vibrant red rings
                    r1 = int(22 + frame * 11)
                    r2 = max(10, int(10 + (frame - 3) * 11)) if frame >= 3 else 0

                    # Ring 1 (Outer pulse)
                    canvas.create_oval(cx - r1, cy - r1, cx + r1, cy + r1, outline='#FF0000', width=max(2, 6 - frame // 3))
                    # Center bullseye dot
                    canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill='#FF0000', outline='#FFFFFF', width=2)

                    # Ring 2 (Inner trailing pulse)
                    if r2 > 0:
                        canvas.create_oval(cx - r2, cy - r2, cx + r2, cy + r2, outline='#FF3333', width=max(2, 5 - frame // 3))

                    frame += 1
                    root.after(20, animate)

                animate()
                root.mainloop()
            except Exception as e:
                print(f"[RedRadar] Error: {e}")
            finally:
                with self._lock:
                    self._is_active = False

        threading.Thread(target=_run, daemon=True).start()
