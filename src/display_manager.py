from enum import Enum
import logging

from button_manager import ButtonManager
from mock_button_manager import MockButtonManager
from views.agenda_view import AgendaView
from views.google_photo_view import GooglePhotoView
from views.hello_world_view import HelloWorldView
from views.xmas_countdown_view import XmasCountdownView

SUPPORTED_VIEWS = {
    "xmas_countdown": XmasCountdownView,
    "agenda": AgendaView,
    "photos": GooglePhotoView
}

class DisplayManager:
    def __init__(self, display, config):
        self.display = display

        if not config.get("views"):
            raise Exception("No views specified")

        unsupported_views = [view for view in config.get("views") if view not in SUPPORTED_VIEWS.keys()]

        if len(unsupported_views) > 0:
            raise Exception(f"Unsupported views: {', '.join(unsupported_views)}")

        self.views = {
            view: SUPPORTED_VIEWS[view](display, config)
            for view in config.get("views")
        }
        self.current_view = next(iter(self.views))

        self._task = None
        self._running = False
        self.buttons = MockButtonManager(self.handle_button) if config.get("mockDisplay") else ButtonManager(self.handle_button)
        
    def start(self):
        self._running = True
        self.buttons.start()

        logging.info(f"[DisplayManager] Started with view: {self.current_view}")
        self.views[self.current_view].render()

    def handle_button(self, label: str):
        logging.info(f"[DisplayManager] Button pressed: {label}")
        if label == "D":
            self.cycle_view()
        else:
            self.views[self.current_view].handle_button_press(label)

    def cycle_view(self):
        view_keys = list(self.views.keys())
        index = view_keys.index(self.current_view)
        new_index = (index + 1) % len(view_keys)
        new_key = view_keys[new_index]
        self.set_view(new_key)

    def set_view(self, view: str):
        self.views[self.current_view].stop()
        self.current_view = view
        self.views[self.current_view].render()

    def stop(self):
        logging.info("[DisplayManager] Stopping...")
        self._running = False
        self.buttons.stop()
        self.views[self.current_view].stop()
        logging.info("[DisplayManager] Stopped.")
