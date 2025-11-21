import logging


class MockButtonManager:

    def __init__(self, callback):
        pass
    
    def start(self):
        logging.info("[MockButtonManager] Start")

    def stop(self):
        logging.info("[MockButtonManager] Stop")