from threading import Thread, Event
from time import sleep

class LEDManager:
    def __init__(self, led):
        self.led = led
        self._stop_event = Event()
        self._thread = None

    def blink_led(self, interval=0.5):
        self._stop_event.clear()
        self._thread = Thread(target=self._blink_loop, args=(interval,), name="LEDBlink")
        self._thread.start()

    def _blink_loop(self, interval):
        while not self._stop_event.is_set():
            self.led.on()
            sleep(interval)
            self.led.off()
            sleep(interval)

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        print("[LEDManager] Stopped.")