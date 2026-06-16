"""Unit tests for macro loading, hotkeys, mouse actions, and execution flow."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import types

# Patch Keycode before importing macros for desktop testing
class DummyKeycode:
    CTRL = 'CTRL'
    C = 'C'

sys.modules['adafruit_hid.keycode'] = types.SimpleNamespace(Keycode=DummyKeycode)

import unittest
from macros import run_macro, send_hotkey, send_mouse_action, load_macros
from logger import Log

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
    def __init__(self):
        self.written = []
    def write(self, text):
        self.written.append(text)

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

def test_macros():
    log = Log(debug_level=0)
    macros = {"test_macro": [
        {"type": "write", "text": "abc"},
        {"type": "hotkey", "keys": ["CTRL", "C"]},
        {"type": "mouse", "moveY": -10},
        {"type": "mouse", "moveX": 5},
        {"type": "mouse", "setXY": [100, 200]},
        {"type": "mouse", "click": "right"},
        {"type": "mouse", "click": "left"}
    ]}
    keyboard = DummyKeyboard()
    layout = DummyLayout()
    mouse = DummyMouse()
    assert run_macro("test_macro", macros, keyboard, layout, mouse, log)
    assert layout.written == ["abc"]
    assert keyboard.sent == [("CTRL", "C")]
    assert mouse.moves == [(0, -10, 0), (5, 0, 0)]
    assert mouse.position == (100, 200)
    assert mouse.clicks == [DummyMouse.RIGHT_BUTTON, DummyMouse.LEFT_BUTTON]

def test_send_mouse_action_invalid_click():
    log = Log(debug_level=0)
    mouse = DummyMouse()
    assert not send_mouse_action({"type": "mouse", "click": "unsupported"}, mouse, log)

def test_send_mouse_action_missing_payload():
    log = Log(debug_level=0)
    mouse = DummyMouse()
    assert not send_mouse_action({"type": "mouse"}, mouse, log)

def test_send_mouse_action_setxy():
    log = Log(debug_level=0)
    mouse = DummyMouse()
    assert send_mouse_action({"type": "mouse", "setXY": [150, 75]}, mouse, log)
    assert mouse.position == (150, 75)

def test_send_mouse_action_invalid_setxy():
    log = Log(debug_level=0)
    mouse = DummyMouse()
    assert not send_mouse_action({"type": "mouse", "setXY": [150]}, mouse, log)
    assert not send_mouse_action({"type": "mouse", "setXY": "150,75"}, mouse, log)

if __name__ == "__main__":
    test_macros()
    print("Macros tests passed.")
