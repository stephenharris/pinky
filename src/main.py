from display.mock import Mock
from display_manager import DisplayManager
from util.config import Config

def main():
    display = Mock()
    config = Config()

    manager = DisplayManager(display, config)

    # Initial full render of default mode
    manager.refresh()

if __name__ == "__main__":
    main()
