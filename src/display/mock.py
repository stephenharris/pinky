from datetime import datetime
import os

class Mock:
    def __init__(self, config):
        self.WIDTH = 800
        self.HEIGHT = 480
        self.WHITE = 0
        self.BLACK = 1
        self.RED = self.YELLOW = 2

        self.output_dir = config.get('tmp_dir')
        

    def render(self, image):
        os.makedirs(self.output_dir, exist_ok=True)

        # Save image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.output_dir, f"display_{timestamp}.png")
        image.save(filepath, "PNG")
        image.save(os.path.join(self.output_dir, "latest.png"), "PNG")
        print(f"[MockDisplay] Saved image to {filepath}")



