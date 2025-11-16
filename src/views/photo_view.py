from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

class PhotoView:
    def __init__(self, display, config):
        self.display = display
        self.current_photo = 0

    def render(self):
        print(__file__)
        print((Path(__file__).parents[2]))
        image_path = Path(__file__).parents[2] / "imgs" / "shipping-picture-inky7.jpg"

        print(image_path)
        image = Image.open(image_path)
        resizedimage = image.resize((800, 480))        
        self.display.render(resizedimage)

    def stop(self):
        pass