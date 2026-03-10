import board
import busio
import json
import time
import usb_hid

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

__version__ = "1.0.0 - DEV"

# Load macros from JSON
try:
    with open("macros.json", "r") as f:
        macros = json.load(f)
except Exception as e:
    print("Error loading macros:", e)
    macros = {}

# --- UART CONFIG ---
uart = busio.UART(board.GP0, board.GP1, baudrate=115200, timeout=0.1) // RX=GP0, TX=GP1

# --- HID KEYBOARD ---
keyboard = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(keyboard)

# --- HELPER: hotkey press ---
def send_hotkey(keys):
    keycodes = []
    for k in keys:
        try:
            keycodes.append(getattr(Keycode, k))
        except AttributeError:
            print("Key no reconocida:", k)
            return False

    for kc in keycodes:
        keyboard.press(kc)
    keyboard.release_all()
    return True

# --- HELPER: execute action sequence ---
def execute_sequence(actions):
    for action in actions:
        action_type = action.get("type")
        if action_type == "hotkey":
            keys = action.get("keys", [])
            send_hotkey(keys)
        elif action_type == "write":
            text = action.get("text", "")
            layout.write(text)
        elif action_type == "press":
            key = action.get("key", "")
            try:
                kc = getattr(Keycode, key)
                keyboard.press(kc)
                keyboard.release_all()
            except AttributeError:
                print("Key not recognized:", key)
        elif action_type == "delay":
            seconds = action.get("seconds", 0)
            time.sleep(seconds)
        else:
            print("Unknown action type:", action_type)

# --- HELPER: definir macros ---
def run_macro(name):
    if name in macros:
        execute_sequence(macros[name])
        return True
    else:
        print("Macro desconocida:", name)
        return False

# --- Command Router ---
def handle_command(data):
    cmd = data.get("cmd")

    if cmd == "type":
        text = data.get("text", "")
        layout.write(text)
        return True

    elif cmd == "hotkey":
        keys = data.get("keys", [])
        return send_hotkey(keys)

    elif cmd == "macro":
        name = data.get("name", "")
        return run_macro(name)

    else:
        print("Comando no reconocido:", cmd)
        return False

# --- MAIN LOOP ---
buffer = b""

while True:
    chunk = uart.read()
    if chunk:
        buffer += chunk

        # procesar línea por línea
        while b"\n" in buffer:
            line, buffer = buffer.split(b"\n", 1)
            try:
                text = line.decode().strip()
                if not text:
                    continue

                print("RX:", text)

                # parse JSON
                data = json.loads(text)
                ok = handle_command(data)

                # respuesta inmediata al ESP32
                if ok:
                    uart.write(b'{"status":"ok"}\n')
                else:
                    uart.write(b'{"status":"error"}\n')

            except Exception as e:
                print("ERROR:", e)
                uart.write(b'{"status":"invalid_json"}\n')
