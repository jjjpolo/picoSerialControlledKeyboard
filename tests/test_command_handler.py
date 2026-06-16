"""Unit tests for command dispatch behavior in CommandHandler."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import types

# Patch Keycode before importing command_handler for desktop testing
class DummyKeycode:
    CTRL = 'CTRL'
    C = 'C'
    A = 'A'

sys.modules['adafruit_hid.keycode'] = types.SimpleNamespace(Keycode=DummyKeycode)

from command_handler import CommandHandler
from logger import Log

def test_command_handler():
    class DummyKeyboard:
        def __init__(self):
            self.sent = []
            self._pressed = []

        def press(self, *args):
            self._pressed.extend(args)

        def release_all(self):
            self.sent.append(tuple(self._pressed))
            self._pressed = []
    class DummyLayout:
        def __init__(self): self.written = []
        def write(self, text): self.written.append(text)
    class DummyMouse:
        LEFT_BUTTON = 1
        RIGHT_BUTTON = 2
        MIDDLE_BUTTON = 4

        def __init__(self):
            self.moves = []
            self.clicks = []
            self._position = (0, 0)

        @property
        def position(self):
            return self._position

        @position.setter
        def position(self, value):
            self._position = value

        def move(self, x=0, y=0, wheel=0):
            self.moves.append((x, y, wheel))

        def click(self, button):
            self.clicks.append(button)
    class DummyLog(Log):
        def __init__(self): super().__init__(debug_level=0); self.messages = []
        def info(self, *args): self.messages.append(('info', args))
        def error(self, *args): self.messages.append(('error', args))
        def debug(self, *args): self.messages.append(('debug', args))
    macros = {"macro1": [ {"type": "write", "text": "hi"} ]}
    mouse = DummyMouse()
    handler = CommandHandler(DummyKeyboard(), DummyLayout(), macros, DummyLog(), mouse=mouse)
    # Test type
    assert handler.handle({"cmd": "type", "text": "hello"})
    # Test macro
    assert handler.handle({"cmd": "macro", "name": "macro1"})
    # Test hotkey
    assert handler.handle({"cmd": "hotkey", "keys": ["CTRL", "A"]})
    # Test mouse move
    assert handler.handle({"cmd": "mouse", "moveX": 7})
    assert mouse.moves == [(7, 0, 0)]
    # Test mouse position
    assert handler.handle({"cmd": "mouse", "setXY": [50, 50]})
    assert mouse.position == (50, 50)
    # Test mouse click
    assert handler.handle({"cmd": "mouse", "click": "left"})
    assert mouse.clicks == [DummyMouse.LEFT_BUTTON]
    # Test shutdown
    assert handler.handle({"cmd": "shutdown"})
    assert handler.shutdown_requested
    # Test unknown
    assert not handler.handle({"cmd": "unknown"})

if __name__ == "__main__":
    test_command_handler()
    print("CommandHandler tests passed.")
