from datetime import datetime
import os
from pathlib import Path
import threading
from time import sleep
from PIL import Image
import imgkit
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from googleclient.fetch_events import fetch_events

class AgendaView:
    def __init__(self, display, config):
        self.display = display
        self.current_photo = 0
        self.config = config
        self.running = threading.Event()
        self.running.set()

    def render(self):
        """Start both threads."""
        self.running.set()

        self.display_thread = threading.Thread(target=self.display_loop, daemon=True)
        self.display_thread.start()


    def handle_button_press(self):
        """Start both threads."""
        self._render_agenda()

    def display_loop(self):
        """Runs in a thread."""
        print("[Display] Thread started")
        while self.running.is_set():
            self._render_agenda()
            # interruptible sleep
            for _ in range(int(3600 * 10)):
                if not self.running.is_set():
                    return
                sleep(0.1)

        print("[Display] Thread exiting")
    
    def _render_agenda(self):

        os.makedirs(self.config.get('tmp_dir'), exist_ok=True)
                # --- Load events ---
        #with open("events.json") as f:
        #    events = json.load(f)
        events = fetch_events(self.config.get('calendar', 'google_calendar_id'))

        # --- Split all-day and timed events ---
        all_day_events = [e for e in events if e.get("all_day")]
        timed_events = [e for e in events if not e.get("all_day")]
        
        timed_events.sort(key=lambda e: self._parse_time(e.get("start", "23:59")))
        
        # --- Render template ---
        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("agenda.html")
        
        today_str = datetime.now().strftime("%A, %B %d")
        events = all_day_events + timed_events
        html = template.render(date=today_str, events=events)

        
        # --- Write rendered HTML (for debugging) ---
        with open("agenda_rendered.html", "w") as f:
            f.write(html)
        
        # --- Render HTML to PNG ---
        imgkit.from_file(
            "agenda_rendered.html",
            Path(self.config.get('tmp_dir')) / "agenda.png",
            options={"width": 800, "height": 480}
        )

        # Display
        img = Image.open(Path(self.config.get('tmp_dir')) / "agenda.png")
        img = img.resize((800, 480))
        self.display.render(img)

    def stop(self):
        """Signal threads to exit and join them."""
        print("[AgendaView] Stopping...")
        self.running.clear()

        if self.display_thread:
            self.display_thread.join()

        print("[AgendaView] All threads stopped.")

    # Sort timed events by start time if available
    def _parse_time(self, t):
        try:
            return datetime.strptime(t, "%H:%M")
        except Exception:
            return datetime.max
        
