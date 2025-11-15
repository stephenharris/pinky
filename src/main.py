import asyncio
from display.mock import Mock
from display_manager import DisplayManager
from led_manager import LEDManager
from util.config import Config

async def main():
    config = Config()
    display = Mock(config)

    manager = DisplayManager(display, config)
    led = LEDManager()
    
    asyncio.create_task(led.blink_led())
    
    await manager.start();
    
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())