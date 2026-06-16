"""Unit tests for command dispatch behavior in CommandHandler."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from command_handler import CommandHandler
from logger import Log

def test_command_handler():
    class DummyKeyboard:
        def __init__(self): self.sent = []
        def send(self, *args): self.sent.append(args)
    class DummyLayout:
        def __init__(self): self.written = []
        def write(self, text): self.written.append(text)
    class DummyLog(Log):
        def __init__(self): super().__init__(debug_level=0); self.messages = []
        def info(self, *args): self.messages.append(('info', args))
        def error(self, *args): self.messages.append(('error', args))
        def debug(self, *args): self.messages.append(('debug', args))
    macros = {"macro1": [ {"type": "write", "text": "hi"} ]}
    handler = CommandHandler(DummyKeyboard(), DummyLayout(), macros, DummyLog())
    # Test type
    assert handler.handle({"cmd": "type", "text": "hello"})
    # Test macro
    assert handler.handle({"cmd": "macro", "name": "macro1"})
    # Test hotkey
    assert handler.handle({"cmd": "hotkey", "keys": ["CTRL", "A"]})
    # Test shutdown
    assert handler.handle({"cmd": "shutdown"})
    assert handler.shutdown_requested
    # Test unknown
    assert not handler.handle({"cmd": "unknown"})

if __name__ == "__main__":
    test_command_handler()
    print("CommandHandler tests passed.")

# Patch Keycode for desktop testing
import types
import sys
class DummyKeycode:
    CTRL = 'CTRL'
    C = 'C'
    A = 'A'
    # Add more as needed for your tests
sys.modules['adafruit_hid.keycode'] = types.SimpleNamespace(Keycode=DummyKeycode)
