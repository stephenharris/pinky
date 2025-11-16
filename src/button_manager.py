from datetime import time
import threading
import gpiod
import gpiodevice
from gpiod.line import Bias, Direction, Edge

# GPIO pins for each button (from top to bottom)
# These will vary depending on platform and the ones
# below should be correct for Raspberry Pi 5.
# Run "gpioinfo" to find out what yours might be.
#
# Raspberry Pi 5 Header pins used by Inky Impression:
#    PIN29, PIN31, PIN36, PIN18.
# These header pins correspond to BCM GPIO numbers:
#    GPIO05, GPIO06, GPIO16, GPIO24.
# These GPIO numbers are what is used below and not the
# header pin numbers.

SW_A = 5
SW_B = 6
SW_C = 16  # Set this value to '25' if you're using a Impression 13.3"
SW_D = 24
BUTTONS = [SW_A, SW_B, SW_C, SW_D]
LABELS = ["A", "B", "C", "D"]

DEBOUNCE_MS = 150

class ButtonManager:
    """Handles GPIO button input in a background thread and calls a handler."""

    def __init__(self, callback):
        """
        button_ids: list of BCM GPIO numbers (e.g., [5, 6, 16, 24])
        labels: same-length list of labels (e.g., ["A", "B", "C", "D"])
        callback: function(label: str) -> None
        """
        self.button_ids = BUTTONS
        self.labels = LABELS
        self.callback = callback

        self._running = False
        self._thread = None
        self._request = None
        self.OFFSETS = None

    def start(self):
        """Start GPIO monitoring in a background thread."""
        self._running = True
        print("[ButtonManager] Starting")

        INPUT = gpiod.LineSettings(
            direction=Direction.INPUT,
            bias=Bias.PULL_UP,
            edge_detection=Edge.FALLING,
        )

        chip = gpiodevice.find_chip_by_platform()
        self.OFFSETS = [chip.line_offset_from_id(id) for id in self.button_ids]
        line_config = dict.fromkeys(self.OFFSETS, INPUT)
        self._request = chip.request_lines(
            consumer="spectra6-buttons", config=line_config
        )

        self._thread = threading.Thread(target=self._loop_thread, daemon=True, name="Buttons")
        self._thread.start()
    
    def _loop_thread(self):
        """Run in a background thread; blocks on read_edge_events()."""
        print("[ButtonManager] Thread loop started")

        last_time = {label: 0 for label in self.labels}

        while self._running:
            try:
                for event in self._request.read_edge_events():
                    index = self.OFFSETS.index(event.line_offset)
                    label = self.labels[index]

                    now = time.monotonic() * 1000
                    if now - last_time[label] < DEBOUNCE_MS:
                        print(f"debounce {label}")
                        # Too soon → ignore as bounce
                        continue

                    last_time[label] = now

                    print(f"[ButtonManager] Button {label} pressed")
                    # Call the callback directly (thread-safe)
                    self.callback(label)
            except Exception as e:
                print(f"[ButtonManager] Thread error: {e}")
        print("[ButtonManager] Thread loop stopped")

    def stop(self):
        """Stop GPIO thread and release resources."""
        print("[ButtonManager] Stopping...")
        self._running = False
        if self._request:
            try:
                self._request.release()
            except Exception:
                pass
        print("[ButtonManager] Stopped.")