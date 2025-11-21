import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

class PhotoView:
    def __init__(self, display, config):
        self.display = display
        self.current_photo = 0

    def render(self):
        logging.info(__file__)
        logging.info((Path(__file__).parents[2]))
        image_path = Path(__file__).parents[2] / "imgs" / "shipping-picture-inky7.jpg"

        logging.info(image_path)
        image = Image.open(image_path)
        resizedimage = image.resize((800, 480))        
        self.display.render(resizedimage)

    def handle_button_press(self, label):
        """Start both threads."""
        pass

    def stop(self):
        pass