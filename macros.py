"""Macro loading and execution helpers for keyboard automation.

Parses macros.json, converts key names to HID keycodes, and runs action
sequences such as write, hotkey, press, delay, and mouse actions.
"""

import json
from adafruit_hid.keycode import Keycode


def send_mouse_action(action, mouse, log=None):
    if not mouse:
        if log:
            log.error("Mouse not initialized")
        return False

    move_x = action.get("moveX", 0)
    move_y = action.get("moveY", 0)
    wheel = action.get("wheel", 0)
    click = action.get("click")
    set_xy = action.get("setXY")

    has_move = any(value != 0 for value in (move_x, move_y, wheel))
    has_click = click is not None
    has_set_xy = set_xy is not None
    if not has_move and not has_click and not has_set_xy:
        if log:
            log.error("Mouse action requires moveX, moveY, wheel, setXY, or click")
        return False

    if has_set_xy:
        try:
            if not isinstance(set_xy, (list, tuple)) or len(set_xy) != 2:
                if log:
                    log.error("setXY must be a list/tuple with [x, y]")
                return False
            x, y = set_xy
            mouse.position = (x, y)
        except Exception as e:
            if log:
                log.error("Mouse position error:", e)
            return False

    if has_move:
        try:
            mouse.move(x=move_x, y=move_y, wheel=wheel)
        except Exception as e:
            if log:
                log.error("Mouse move error:", e)
            return False

    if has_click:
        button_map = {
            "left": mouse.LEFT_BUTTON,
            "right": mouse.RIGHT_BUTTON,
            "middle": mouse.MIDDLE_BUTTON,
        }
        button = button_map.get(str(click).lower())
        if button is None:
            if log:
                log.error("Unsupported mouse click:", click)
            return False
        try:
            mouse.click(button)
        except Exception as e:
            if log:
                log.error("Mouse click error:", e)
            return False

    return True

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

def execute_sequence(actions, keyboard, layout, mouse=None, log=None):
    ok = True
    for action in actions:
        action_type = action.get("type")
        if action_type == "hotkey":
            keys = action.get("keys", [])
            ok = send_hotkey(keys, keyboard, log) and ok
        elif action_type == "write":
            text = action.get("text", "")
            if layout:
                try:
                    layout.write(text)
                except Exception as e:
                    if log:
                        log.error("Write error:", e)
                    ok = False
            else:
                ok = False
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
                    ok = False
            else:
                if log:
                    log.error("Keyboard not initialized")
                ok = False
        elif action_type == "delay":
            seconds = action.get("seconds", 0)
            import time
            time.sleep(seconds)
        elif action_type == "mouse":
            ok = send_mouse_action(action, mouse, log) and ok
        else:
            if log:
                log.error("Unknown action type:", action_type)
            ok = False

    return ok

def run_macro(name, macros, keyboard, layout, mouse=None, log=None):
    if name in macros:
        return execute_sequence(macros[name], keyboard, layout, mouse, log)
    else:
        if log:
            log.error("Unknown macro:", name)
        return False
