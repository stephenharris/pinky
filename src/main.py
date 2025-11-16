from time import sleep
from display.mock import Mock
from display.inky import Inky
from display_manager import DisplayManager
from led_manager import LEDManager
from util.config import Config

def main():
    config = Config()
    display = Mock(config) if config.get("mockDisplay") else Inky()
    manager = DisplayManager(display, config)
    
    if not config.get("mockDisplay"):
        led = LEDManager()
        led.blink_led()
    
    manager.start();
    
    try:
        while True:
            sleep(0.5)

    except KeyboardInterrupt:
        print("Stopping…")
        manager.stop()
    


if __name__ == "__main__":
    main()