import threading
import hashlib
from pathlib import Path
import random
from PIL import Image
from time import sleep
from googleclient.client import authenticate
from googleclient.drive import sync_drive_folder
from googleapiclient.discovery import build
import logging

class GooglePhotoView:
    def __init__(self, display, config):
        self.display = display
        self.local_path = Path(config.get('photos', 'dir'))
        self.image_queue = []
        self.image_list_hash = None

        self.display_interval = config.get('photos', 'display_interval')
        self.sync_interval = config.get('photos', 'sync_interval')
        self.google_drive_id = config.get('photos', 'drive_folder_id')

        self.running = threading.Event()
        self.running.set()

        self.force_next_event = threading.Event()

        self.display_thread = None
        self.sync_thread = None

    # -------------------------
    # Image / queue utilities
    # -------------------------

    def list_local_files(self):
        return [
            p for p in self.local_path.glob("*")
            if p.suffix.lower() in (".jpg", ".jpeg", ".png")
        ]

    def hash_images(self, files):
        sorted_files = sorted(files)
        m = hashlib.md5()
        for f in sorted_files:
            info = f"{f.name}-{f.stat().st_mtime}".encode()
            m.update(info)
        return m.hexdigest()

    def maybe_refill_image_queue(self):
        images = self.list_local_files()
        new_hash = self.hash_images(images)

        if new_hash != self.image_list_hash:
            self.image_list_hash = new_hash
            random.shuffle(images)
            self.image_queue = images.copy()
            logging.info(f"[Display] Changes detected. Refilled queue ({len(images)})")

        elif not self.image_queue:
            random.shuffle(images)
            self.image_queue = images.copy()
            logging.info(f"[Display] Queue empty, reshuffled ({len(images)})")

    # -------------------------
    # Display loop (thread)
    # -------------------------

    def display_loop(self):
        """Runs in a thread."""
        logging.info("[Display] Thread started")

        while self.running.is_set():
            logging.info("[Display] Running...")
            try:
                self.maybe_refill_image_queue()
                if self.image_queue:
                    img_path = self.image_queue.pop()
                    logging.info(f"[Display] Showing: {img_path}")
                    self.display.render(Image.open(img_path))
            except Exception as e:
                logging.info(f"[Display] ERROR: {e}")

            # interruptible sleep
            for _ in range(int(self.display_interval * 10)):

                # if event triggered, break immediately
                if self.force_next_event.wait(timeout=0.1):
                    logging.info("[Photos] Forced next image")
                    self.force_next_event.clear()
                    break

                if not self.running.is_set():
                    return
                sleep(0.1)

        logging.info("[Display] Thread exiting")

    def handle_button_press(self, label):
        """Responds to button A click by cycling through image."""

        if label == "A":
            #if self.rendering:
            #    logging.info("[Photos] Busy — ignoring button press")
            #    return
    
            logging.info("[Photos] Forcing next image")
            self.force_next_event.set()

    # -------------------------
    # Google Drive sync thread
    # -------------------------

    def sync_loop(self):
        """Runs in a thread."""
        logging.info("[Sync] Thread started")

        try:
            creds = authenticate()
            service = build('drive', 'v3', credentials=creds)

            while self.running.is_set():
                logging.info(f"[Sync] Checking Google Drive folder {self.google_drive_id}")
                sync_drive_folder(service, self.google_drive_id, self.local_path)
                logging.info("[Sync] Sync complete")

                # interruptible sleep
                for _ in range(self.sync_interval * 10):
                    if not self.running.is_set():
                        return
                    sleep(0.1)

        except Exception as e:
            logging.info(f"[Sync] ERROR: {e}")

        logging.info("[Sync] Thread exiting")

    # -------------------------
    # Control
    # -------------------------

    def render(self):
        """Start both threads."""
        self.running.set()

        self.display_thread = threading.Thread(target=self.display_loop, daemon=True)
        self.sync_thread = threading.Thread(target=self.sync_loop, daemon=True)

        self.display_thread.start()
        self.sync_thread.start()

    def stop(self):
        """Signal threads to exit and join them."""
        logging.info("[Manager] Stopping...")
        self.running.clear()

        if self.display_thread:
            self.display_thread.join()
        if self.sync_thread:
            self.sync_thread.join()

        logging.info("[Manager] All threads stopped.")
