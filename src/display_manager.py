import asyncio
from enum import Enum

from button_manager import ButtonManager
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
        self.buttons = ButtonManager(self.handle_button)

    async def start(self):
        self._running = True
        loop = asyncio.get_running_loop()
        self.buttons.start(loop)

        self._task = asyncio.create_task(self.views[self.current_view].render())
        print(f"[DisplayManager] Started with view: {self.current_view.value}")

        while self._running:
            await asyncio.sleep(1)

    def handle_button(self, label: str):
        print(f"[DisplayManager] Button pressed: {label}")
        if label == "A":
            asyncio.create_task(self.cycle_view())

    async def cycle_view(self):
        modes = list(DisplayMode)
        idx = modes.index(self.current_view)
        new_mode = modes[(idx + 1) % len(modes)]
        await self.set_view(new_mode.value)

    async def set_view(self, view: str):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        self.current_view = DisplayMode(view)
        print(f"[DisplayManager] Starting {self.current_view.value}")
        self._task = asyncio.create_task(self.views[self.current_view].render())

    async def stop(self):
        print("[DisplayManager] Stopping...")
        self._running = False
        self.buttons.stop()

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        print("[DisplayManager] Stopped.")
