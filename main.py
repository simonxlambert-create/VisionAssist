import os
import sys

# Safe logger for pythonw
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(log_dir, 'vision_assist.log')

class SafeWriter:
    def __init__(self, filepath):
        self.filepath = filepath
    def write(self, text):
        try:
            with open(self.filepath, 'a', encoding='utf-8') as f:
                f.write(text)
        except Exception:
            pass
    def flush(self):
        pass

if sys.stdout is None:
    sys.stdout = SafeWriter(log_file)
if sys.stderr is None:
    sys.stderr = SafeWriter(log_file)

import threading
import time
from config import Config
from cursor_manager import CursorManager
from audio_feedback import AudioFeedback
from hotkey_listener import HotkeyListener
from startup_manager import is_startup_enabled, set_startup
from tray_app import TrayApp
from red_radar import RedRadar

class VisionAssistApp:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config = Config(os.path.join(self.base_dir, 'config.json'))
        
        sound_on = self.config.get('sound_enabled', True)
        self.audio = AudioFeedback(enabled=sound_on)
        self.cursors = CursorManager(self.base_dir)
        self.radar = RedRadar()
        
        self.hotkeys = HotkeyListener(
            on_toggle_color=self.on_hotkey_toggle_color,
            on_toggle_size=self.on_hotkey_toggle_size,
            on_radar=self.on_trigger_radar
        )
        self.tray = TrayApp(self)

    def on_trigger_radar(self):
        """Spawns bright RED animated radar circle on cursor."""
        self.radar.show_radar()

    def on_hotkey_toggle_color(self):
        """Called when user presses Ctrl + * or F8."""
        if self.cursors.is_red_active():
            self.cursors.set_scheme_default()
            self.audio.play_default_on()
            self.config.set('last_color', 'default')
        else:
            self.cursors.set_scheme_red()
            self.audio.play_red_on()
            self.config.set('last_color', 'red')
        # Also flash red radar once to confirm position
        self.radar.show_radar()

    def on_hotkey_toggle_size(self):
        """Called when user presses Ctrl + / or F9."""
        current_size = self.cursors.get_current_size()
        sizes = self.config.get('sizes_cycle', [32, 64, 96])
        
        if current_size in sizes:
            idx = sizes.index(current_size)
            next_size = sizes[(idx + 1) % len(sizes)]
        else:
            next_size = 64 if current_size == 32 else 32

        self.cursors.set_cursor_size(next_size)
        if next_size > 32:
            self.audio.play_size_large()
        else:
            self.audio.play_size_normal()
        self.radar.show_radar()

    def toggle_color(self, color_name: str):
        if color_name == 'red':
            if self.cursors.is_red_active():
                self.cursors.set_scheme_default()
                self.audio.play_default_on()
            else:
                self.cursors.set_scheme_red()
                self.audio.play_red_on()

    def restore_default_color(self):
        self.cursors.set_scheme_default()
        self.audio.play_default_on()

    def set_size(self, size: int):
        self.cursors.set_cursor_size(size)
        if size > 32:
            self.audio.play_size_large()
        else:
            self.audio.play_size_normal()

    def get_current_size(self) -> int:
        return self.cursors.get_current_size()

    def is_red_active(self) -> bool:
        return self.cursors.is_red_active()

    def is_yellow_active(self) -> bool:
        return False

    def toggle_sound(self):
        cur = self.config.get('sound_enabled', True)
        new_val = not cur
        self.config.set('sound_enabled', new_val)
        self.audio.enabled = new_val
        if new_val:
            self.audio.play_size_large()

    def toggle_sonar(self):
        pass

    def is_startup_enabled(self) -> bool:
        return is_startup_enabled()

    def toggle_startup(self):
        cur = is_startup_enabled()
        set_startup(not cur, os.path.join(self.base_dir, 'main.py'))

    def exit_app(self):
        self.cursors.set_scheme_default()
        self.hotkeys.stop()
        self.tray.stop()
        sys.exit(0)

    def run(self):
        self.hotkeys.start()
        print("=======================================================")
        print("VisionAssist Accessibility Engine is Running!")
        print("  - Ctrl + * (or F8) : Instant Red Cursor")
        print("  - Ctrl + / (or F9) : Instant Cursor Size (32 / 64 / 96px)")
        print("  - Single tap Ctrl   : Glowing RED Radar Wave")
        print("=======================================================")
        self.tray.run()

if __name__ == '__main__':
    app = VisionAssistApp()
    app.run()
