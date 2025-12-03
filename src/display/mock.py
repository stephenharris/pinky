from datetime import datetime
import logging
import os

class Mock:
    def __init__(self, config):
        self.WIDTH = 800
        self.HEIGHT = 480
        self.WHITE = 0
        self.BLACK = 1
        self.RED = self.YELLOW = 2

        self.output_dir = config.get('tmp_dir')
        
    def is_busy(self):
        return False

    def led_on(self):
        logging.info(f"[MockDisplay] LED on")

    def led_off(self):
        logging.info(f"[MockDisplay] LED off")

    def render(self, image):
        os.makedirs(self.output_dir, exist_ok=True)

        # Save image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.output_dir, f"display_{timestamp}.png")
        image.save(filepath, "PNG")
        image.save(os.path.join(self.output_dir, "latest.png"), "PNG")
        logging.info(f"[MockDisplay] Saved image to {filepath}")



