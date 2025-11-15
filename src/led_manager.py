import asyncio

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


    async def blink_led(self, duration=60, interval=0.5):
        """Blink LED asynchronously for <duration> seconds."""
        end_time = asyncio.get_event_loop().time() + duration
        while asyncio.get_event_loop().time() < end_time:
            self.gpio.set_value(self.led, Value.ACTIVE)
            await asyncio.sleep(interval)
            self.gpio.set_value(self.led, Value.INACTIVE)
            await asyncio.sleep(interval)