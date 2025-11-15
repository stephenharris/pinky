import asyncio
import hashlib
from pathlib import Path
import random
from PIL import Image, ImageOps

from googleclient.drive import sync_with_drive_loop
from concurrent.futures import ThreadPoolExecutor

class GooglePhotoView:
    def __init__(self, display, config):
        self.display = display
        self.local_path = Path(config.get('photos', 'dir'))
        self.image_queue = [] # queue of images to display
        self.image_list_hash = None # hash of images directory
        self.display_interval = config.get('photos', 'display_interval')
        self.sync_interval = config.get('photos', 'sync_interval')
        self.google_drive_id = config.get('photos', 'drive_folder_id');
        self._running = False
        self.executor = ThreadPoolExecutor(max_workers=2)

    def maybe_refill_image_queue(self):
        """Shuffle all available images and refill the queue."""
        images = self.list_local_files()
        new_hash = self.hash_images(images)

        if new_hash != self.image_list_hash:
            self.image_list_hash = new_hash
            random.shuffle(images)
            self.image_queue = images.copy()
            print(f"[Display] Changes in images detected. Refilled queue with {len(self.image_queue)} images.")

        elif not self.image_queue:        
            random.shuffle(images)
            self.image_queue = images.copy()
            print(f"[Display] Queue empty, reshuffled with {len(self.image_queue)} images.")

    def list_local_files(self):
        return [ p for p in self.local_path.glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png")]

    def hash_images(self, files):
        sorted_files = sorted(files)
        m = hashlib.md5()
        for f in sorted_files:
            # Use filename + last modification time
            info = f"{f.name}-{f.stat().st_mtime}".encode()
            m.update(info)
        return m.hexdigest()


    async def render(self):
        self._running = True
        try:
            self.sync_task = asyncio.create_task(
                asyncio.to_thread(
                    sync_with_drive_loop(self.google_drive_id, self.local_path, self.sync_interval)
                )
            )
                    
            while self._running:
                self.maybe_refill_image_queue()
                if self.image_queue:
                    next_image = self.image_queue.pop()
                    print("display image")
                    loop = asyncio.get_running_loop()
                    print("aquired running loop")
                    await loop.run_in_executor(self.executor, self.display_image, next_image)

                await asyncio.sleep(self.display_interval)
        except asyncio.CancelledError:
            print("[Display] Render loop cancelled")
            self.stop()

    def display_image(self, img):
        image = self.prepare_image(img)
        #resizedimage = image.resize((800, 480))        
        self.display.render(image)

    def prepare_image(self, img_path, size=(800, 480)):
        # Open the image
        image = Image.open(img_path)

        # Remove EXIF-based rotation (normalize orientation)
        image = ImageOps.exif_transpose(image)

        # Center-crop and scale to the desired size, preserving aspect ratio
        image = ImageOps.fit(image, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))

        return image

    def stop(self):
        """Call this to stop the render loop."""
        self._running = False
        # Optionally cancel sync task too
        if hasattr(self, "sync_task"):
            self.sync_task.cancel()