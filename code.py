import board
import busio
import json
import time
import usb_hid

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

__version__ = "1.0.0 - DEV"

# --- UART CONFIG ---
uart = busio.UART(board.GP0, board.GP1, baudrate=115200, timeout=0.1)

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

# --- HELPER: definir macros ---
def run_macro(name):
    if name == "shutdown_windows":
        # WIN+R → escribir comando → ENTER
        send_hotkey(["WINDOWS"])
        time.sleep(0.2)
        layout.write("shutdown /s /t 0")
        time.sleep(0.1)
        keyboard.press(Keycode.ENTER)
        keyboard.release_all()
        return True

    elif name == "abrir_terminal":
        send_hotkey(["CTRL", "ALT", "T"])
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
