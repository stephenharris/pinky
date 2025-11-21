from datetime import date
import logging
import os
from pathlib import Path
import threading
from time import sleep
from PIL import Image
import imgkit
from jinja2 import Environment, FileSystemLoader

class XmasCountdownView:
    def __init__(self, display, config):
        self.display = display
        self.days_remaining = None
        self.config = config
        self.running = threading.Event()
        self.running.set()

    def render(self):
        """Start display loop."""
        self.running.set()

        self.display_thread = threading.Thread(target=self.display_loop, daemon=True)
        self.display_thread.start()


    def display_loop(self):
        """Runs in a thread."""
        logging.info("[Display] Thread started")
        while self.running.is_set():
            self._render_agenda()
            # interruptible sleep
            for _ in range(int(60 * 10)):
                if not self.running.is_set():
                    return
                sleep(0.1)

        logging.info("[Display] Thread exiting")

    def days_until_christmas(self):
        today = date.today()
        year = today.year
        christmas = date(year, 12, 25)

        if today > christmas:
            christmas = date(year + 1, 12, 25)

        return (christmas - today).days

    
    def _render_agenda(self):

        os.makedirs(self.config.get('tmp_dir'), exist_ok=True)

        if self.days_remaining == self.days_until_christmas():
            logging.info("[christmas] remaining days unchanged")
            return
        
        self.days_remaining = self.days_until_christmas();
        logging.info(f"[christmas] remaining days {self.days_remaining}")

        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("xmas-countdown.html")
        
        html = template.render(days_remaining=self.days_remaining)

        
        # --- Write rendered HTML (for debugging) ---
        with open("xmas-countdown_rendered.html", "w") as f:
            f.write(html)
        
        # --- Render HTML to PNG ---
        imgkit.from_file(
            "xmas-countdown_rendered.html",
            Path(self.config.get('tmp_dir')) / "xmas-countdown.png",
            options={"width": 800, "height": 480, 'enable-local-file-access': None}
        )

        # Display
        img = Image.open(Path(self.config.get('tmp_dir')) / "xmas-countdown.png")
        img = img.resize((800, 480))
        self.display.render(img)

    def stop(self):
        """Signal threads to exit and join them."""
        logging.info("[AgendaView] Stopping...")
        self.running.clear()

        if self.display_thread:
            self.display_thread.join()

        logging.info("[AgendaView] All threads stopped.")


