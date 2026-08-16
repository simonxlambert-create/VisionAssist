import os
import sys
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

class TrayApp:
    def __init__(self, app_controller):
        self.controller = app_controller
        self.icon = None

    def _create_tray_image(self):
        """Generates a high-contrast eye/pointer icon for the tray."""
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Outer dark ring
        draw.ellipse([4, 4, 60, 60], fill=(25, 25, 30, 255), outline=(255, 255, 255, 255), width=2)
        # Inner vivid red pointer
        draw.polygon([(20, 14), (20, 46), (30, 36), (42, 48), (48, 42), (36, 30), (48, 30)], fill=(255, 40, 40, 255), outline=(255, 255, 255, 255))
        return img

    def build_menu(self):
        def on_toggle_red(icon, item):
            self.controller.toggle_color('red')

        def on_toggle_yellow(icon, item):
            self.controller.toggle_color('yellow')

        def on_toggle_default(icon, item):
            self.controller.restore_default_color()

        def on_set_size(size):
            def handler(icon, item):
                self.controller.set_size(size)
            return handler

        def on_toggle_sound(icon, item):
            self.controller.toggle_sound()

        def on_toggle_sonar(icon, item):
            self.controller.toggle_sonar()

        def on_toggle_startup(icon, item):
            self.controller.toggle_startup()

        def on_open_folder(icon, item):
            os.system(f'explorer "{self.controller.base_dir}"')

        def on_exit(icon, item):
            self.controller.exit_app()

        menu = pystray.Menu(
            item('VisionAssist (RP Helper)', None, enabled=False),
            pystray.Menu.SEPARATOR,
            item('🔴 Red High-Contrast Cursor (Ctrl + *)', on_toggle_red, checked=lambda item: self.controller.is_red_active()),
            item('🟡 Neon Yellow Cursor', on_toggle_yellow, checked=lambda item: self.controller.is_yellow_active()),
            item('⚪ Default Windows Cursor', on_toggle_default, checked=lambda item: not (self.controller.is_red_active() or self.controller.is_yellow_active())),
            pystray.Menu.SEPARATOR,
            item('🔍 Size: Standard 32px', on_set_size(32), checked=lambda item: self.controller.get_current_size() == 32),
            item('🔍 Size: Large 64px (Ctrl + /)', on_set_size(64), checked=lambda item: self.controller.get_current_size() == 64),
            item('🔍 Size: Extra Large 96px', on_set_size(96), checked=lambda item: self.controller.get_current_size() == 96),
            pystray.Menu.SEPARATOR,
            item('🔊 Audio Feedback', on_toggle_sound, checked=lambda item: self.controller.config.get('sound_enabled', True)),
            item('📍 Ctrl Key Locator (Mouse Sonar)', on_toggle_sonar, checked=lambda item: self.controller.config.get('enable_mouse_sonar', True)),
            item('🚀 Start with Windows', on_toggle_startup, checked=lambda item: self.controller.is_startup_enabled()),
            pystray.Menu.SEPARATOR,
            item('📁 Open Folder', on_open_folder),
            item('❌ Exit', on_exit)
        )
        return menu

    def run(self):
        image = self._create_tray_image()
        self.icon = pystray.Icon("VisionAssist", image, "VisionAssist (RP Shortcuts)", self.build_menu())
        self.icon.run()

    def stop(self):
        if self.icon:
            self.icon.stop()
