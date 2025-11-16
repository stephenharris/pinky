from enum import Enum

from button_manager import ButtonManager
from mock_button_manager import MockButtonManager
from views.agenda_view import AgendaView
from views.google_photo_view import GooglePhotoView
from views.hello_world_view import HelloWorldView

class DisplayMode(Enum):
    HELLO_WORLD = "helloworld"
    AGENDA = "agenda"
    PHOTOS = "photos"

class DisplayManager:
    def __init__(self, display, config):
        self.display = display
        self.current_view = DisplayMode(config.get("display"))
        self.views = {
            DisplayMode.HELLO_WORLD: HelloWorldView(self.display, config),
            DisplayMode.PHOTOS: GooglePhotoView(self.display, config),
            DisplayMode.AGENDA: AgendaView(self.display, config),
        }

        self._task = None
        self._running = False
        self.buttons = MockButtonManager(self.handle_button) if config.get("mockDisplay") else ButtonManager(self.handle_button)
        
    def start(self):
        self._running = True
        self.buttons.start()

        print(f"[DisplayManager] Started with view: {self.current_view.value}")
        self.views[self.current_view].render()


    def handle_button(self, label: str):
        print(f"[DisplayManager] Button pressed: {label}")
        if label == "D":
            self.cycle_view()
        else:
            self.views[self.current_view].handle_button(label)

    def cycle_view(self):
        modes = list(DisplayMode)
        idx = modes.index(self.current_view)
        new_mode = modes[(idx + 1) % len(modes)]
        self.set_view(new_mode.value)

    def set_view(self, view: str):
        self.views[self.current_view].stop()
        self.current_view = DisplayMode(view)
        self.views[self.current_view].render()

    def stop(self):
        print("[DisplayManager] Stopping...")
        self._running = False
        self.buttons.stop()
        self.views[self.current_view].stop()
        print("[DisplayManager] Stopped.")
