from threading import Thread, Event
from time import sleep
import gpiod
import gpiodevice
from gpiod.line import Bias, Direction, Value

class LEDManager:
    def __init__(self):
        LED_PIN = 13  # adjust to your board's LED pin

        # Find the gpiochip device we need, we'll use
        # gpiodevice for this, since it knows the right device
        # for its supported platforms.
        chip = gpiodevice.find_chip_by_platform()

        # Setup for the LED pin
        self.led = chip.line_offset_from_id(LED_PIN)
        self.gpio = chip.request_lines(consumer="inky", config={self.led: gpiod.LineSettings(direction=Direction.OUTPUT, bias=Bias.DISABLED)})

        self._stop_event = Event()
        self._thread = None

    def blink_led(self, interval=0.5):
        self._stop_event.clear()
        self._thread = Thread(target=self._blink_loop, args=(interval,), name="LEDBlink")
        self._thread.start()

    def _blink_loop(self, interval):
        while not self._stop_event.is_set():
            self.gpio.set_value(self.led, Value.ACTIVE)
            sleep(interval)
            self.gpio.set_value(self.led, Value.INACTIVE)
            sleep(interval)

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        print("[LEDManager] Stopped.")