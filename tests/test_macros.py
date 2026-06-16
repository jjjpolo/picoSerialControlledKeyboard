"""Unit tests for macro loading, hotkeys, and macro execution flow."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from macros import run_macro, send_hotkey, load_macros
from logger import Log

# Patch Keycode for desktop testing
import types
class DummyKeycode:
    CTRL = 'CTRL'
    C = 'C'
    # Add more as needed for your tests
sys.modules['adafruit_hid.keycode'] = types.SimpleNamespace(Keycode=DummyKeycode)

class DummyKeyboard:
    def __init__(self):
        self.sent = []
    def send(self, *args):
        self.sent.append(args)

class DummyLayout:
    def __init__(self):
        self.written = []
    def write(self, text):
        self.written.append(text)

def test_macros():
    log = Log(debug_level=0)
    macros = {"test_macro": [
        {"type": "write", "text": "abc"},
        {"type": "hotkey", "keys": ["CTRL", "C"]}
    ]}
    keyboard = DummyKeyboard()
    layout = DummyLayout()
    assert run_macro("test_macro", macros, keyboard, layout, log)
    assert layout.written == ["abc"]
    assert keyboard.sent == [("CTRL", "C")]

if __name__ == "__main__":
    test_macros()
    print("Macros tests passed.")
