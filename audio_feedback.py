import threading
import winsound

class AudioFeedback:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    def _play_tones(self, tones):
        if not self.enabled:
            return
        def run():
            try:
                for freq, duration in tones:
                    winsound.Beep(int(freq), int(duration))
            except Exception:
                try:
                    winsound.MessageBeep(0)
                except Exception:
                    pass
        threading.Thread(target=run, daemon=True).start()

    def play_red_on(self):
        """Rising double chime for Red Cursor enabled."""
        self._play_tones([(600, 100), (900, 150)])

    def play_default_on(self):
        """Falling double chime for Default Cursor restored."""
        self._play_tones([(900, 100), (600, 150)])

    def play_size_large(self):
        """High tone for Large cursor."""
        self._play_tones([(1000, 120), (1250, 150)])

    def play_size_normal(self):
        """Calm tone for Normal size."""
        self._play_tones([(500, 150)])
