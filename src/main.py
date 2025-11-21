import sys
import logging
from time import sleep
from display.mock import Mock
from display.inky import Inky
from display_manager import DisplayManager
from util.config import Config

def main():
    config = Config()
    display = Mock(config) if config.get("mockDisplay") else Inky()
    manager = DisplayManager(display, config)
    
    manager.start();

    try:
        while True:
            sleep(0.5)

    except KeyboardInterrupt:
        logging.info("Stopping…")
        manager.stop()
    


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        handlers=[logging.StreamHandler(sys.stdout)],
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
         force=True
    )
    main()