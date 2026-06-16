"""Macro loading and execution helpers for keyboard automation.

Parses macros.json, converts key names to HID keycodes, and runs action
sequences such as write, hotkey, press, and delay.
"""

import json
from adafruit_hid.keycode import Keycode

def load_macros(log=None):
    try:
        with open("macros.json", "r") as f:
            macros = json.load(f)
        if log:
            log.debug("Macros loaded successfully.")
        return macros
    except Exception as e:
        if log:
            log.error("Error loading macros:", e)
        return {}

def send_hotkey(keys, keyboard, log=None):
    if not keyboard:
        if log:
            log.debug("Keyboard not initialized")
        return False
    keycodes = []
    for k in keys:
        try:
            keycodes.append(getattr(Keycode, k))
        except AttributeError:
            if log:
                log.error("Unrecognized key:", k)
            return False
    for kc in keycodes:
        keyboard.press(kc)
    keyboard.release_all()
    return True

def execute_sequence(actions, keyboard, layout, log=None):
    for action in actions:
        action_type = action.get("type")
        if action_type == "hotkey":
            keys = action.get("keys", [])
            send_hotkey(keys, keyboard, log)
        elif action_type == "write":
            text = action.get("text", "")
            if layout:
                try:
                    layout.write(text)
                except Exception as e:
                    if log:
                        log.error("Write error:", e)
        elif action_type == "press":
            key = action.get("key", "")
            if keyboard:
                try:
                    kc = getattr(Keycode, key)
                    keyboard.press(kc)
                    keyboard.release_all()
                except AttributeError:
                    if log:
                        log.error("Unrecognized key:", key)
            else:
                if log:
                    log.error("Keyboard not initialized")
        elif action_type == "delay":
            seconds = action.get("seconds", 0)
            import time
            time.sleep(seconds)
        else:
            if log:
                log.error("Unknown action type:", action_type)

def run_macro(name, macros, keyboard, layout, log=None):
    if name in macros:
        execute_sequence(macros[name], keyboard, layout, log)
        return True
    else:
        if log:
            log.error("Unknown macro:", name)
        return False
