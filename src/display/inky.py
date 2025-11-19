from inky.auto import auto

from led_manager import LEDManager       # library from Pimoroni for Inky

class Inky:
    def __init__(self):
        # initialize the Inky display
        self.inky_display = auto()   # automatically picks the connected Inky board. :contentReference[oaicite:3]{index=3}
        self.WIDTH = self.inky_display.width
        self.HEIGHT = self.inky_display.height
        self.WHITE = self.inky_display.WHITE
        self.BLACK = self.inky_display.BLACK
        self.RED = self.inky_display.RED
        self.YELLOW = self.inky_display.YELLOW

        self.led = LEDManager()
        self.led.on()

    def render(self, image):
        self.led.on()
        self.inky_display.set_image(image)
        self.inky_display.show()
        self.led.off()


