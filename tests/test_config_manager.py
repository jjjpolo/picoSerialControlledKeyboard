import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from config_manager import ConfigManager
from logger import Log

class DummyLog(Log):
    def __init__(self):
        super().__init__(debug_level=0)
        self.messages = []
    def info(self, *args):
        self.messages.append(('info', args))
    def error(self, *args):
        self.messages.append(('error', args))
    def debug(self, *args):
        self.messages.append(('debug', args))

def test_config():
    log = DummyLog()
    config = ConfigManager(log=log)
    assert isinstance(config.get_config('debug', 0), int)
    config.set_config('test_key', 123)
    assert config.get_config('test_key') == 123
    config.reload_config()
    # After reload, test_key may not persist (depends on implementation)

if __name__ == "__main__":
    test_config()
    print("ConfigManager tests passed.")
