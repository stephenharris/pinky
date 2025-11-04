from font_fredoka_one import FredokaOne
from PIL import Image, ImageDraw, ImageFont

class HelloWorldView:
    def __init__(self, display, config):
        self.display = display
        self.current_photo = 0

    def render(self):
        image = Image.new("RGB", (self.display.WIDTH, self.display.HEIGHT), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        font = ImageFont.truetype(FredokaOne, 72)

        # Draw shapes
        draw.rectangle((50, 50, 200, 200), fill=(255, 255, 0))  # Yellow
        draw.ellipse((150, 150, 300, 300), fill=(255, 0, 0))    # Red

        # Draw text
        draw.text((0, 0), "Hello, World!", fill=(255, 0, 0), font=font)

        self.display.render(image)

