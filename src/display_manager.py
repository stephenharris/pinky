import asyncio
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
        self.current_view = DisplayMode(config.get('display'))
        self.views = {
            DisplayMode.HELLO_WORLD: HelloWorldView(self.display, config),
            DisplayMode.PHOTOS: GooglePhotoView(self.display, config),
            DisplayMode.AGENDA: AgendaView(self.display, config),
        }
        self._task = None
    
    async def start(self):
        self._task = asyncio.create_task(self.views[self.current_view].render())

    async def set_view(self, view: str):
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        self.current_view =  DisplayMode(view)
        # Start new view as a task
        print("Creating render task")
        self._task = asyncio.create_task(self.views[self.current_view].render())
        print("Render task created")

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
 
