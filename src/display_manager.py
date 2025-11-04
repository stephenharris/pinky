from enum import Enum
from PIL import Image

from views.agenda_view import AgendaView
from views.photo_view import PhotoView
from views.hello_world_view import HelloWorldView

class DisplayMode(Enum):
    HELLO_WORLD = "helloworld"
    AGENDA = "agenda"
    PHOTOS = "photos"

class DisplayManager:
    def __init__(self, display, config):
        
        self.display = display
        self.mode = DisplayMode(config.get('display'))
        self.views = {
            DisplayMode.HELLO_WORLD: HelloWorldView(self.display, config),
            DisplayMode.PHOTOS: PhotoView(self.display, config),
            DisplayMode.AGENDA: AgendaView(self.display, config),
        }

    def set_mode(self, mode: DisplayMode):
        if mode != self.mode:
            self.mode = mode
            self.refresh()

    def refresh(self):
        """ Clear and render the current view. """
        img = Image.new("P", (self.display.WIDTH, self.display.HEIGHT),
                        self.display.WHITE)
        self.display.render(img)
        self.views[self.mode].render()
        print('refreshed')

    def update(self):
        """Call this periodically (e.g. in a loop) to update the active view."""
        self.views[self.mode].update()
