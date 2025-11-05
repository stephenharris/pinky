from datetime import datetime
from pathlib import Path
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

    def render(self):

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
        self.display.render(img)
       

    # Sort timed events by start time if available
    def _parse_time(self, t):
        try:
            return datetime.strptime(t, "%H:%M")
        except Exception:
            return datetime.max
        
