import board
import busio
import digitalio
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
uart = busio.UART(board.GP0, board.GP1, baudrate=115200, timeout=0.01)  # RX=GP0, TX=GP1

# --- LED for testing ---
try:
    led = digitalio.DigitalInOut(board.GP25)
    led.direction = digitalio.Direction.OUTPUT
    print("LED initialized on GP25")
except Exception as e:
    print("LED init error:", e)
    led = None

# --- HELPER: blink LED ---
def blink_led(times=1, duration=0.1):
    """Blink the onboard LED a number of times.
    times: how many on/off cycles
    duration: seconds each state lasts
    """
    if not led:
        return
    for _ in range(times):
        led.value = True
        time.sleep(duration)
        led.value = False
        time.sleep(duration)

# --- HID KEYBOARD ---
try:
    keyboard = Keyboard(usb_hid.devices)
    layout = KeyboardLayoutUS(keyboard)
    print("Keyboard initialized")
except Exception as e:
    print("Keyboard init error:", e)
    keyboard = None
    layout = None

# --- HELPER: hotkey press ---
def send_hotkey(keys):
    if not keyboard:
        print("Keyboard not initialized")
        return False
    
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
            if layout:
                try:
                    layout.write(text)
                except Exception as e:
                    print("Write error:", e)
        elif action_type == "press":
            key = action.get("key", "")
            if keyboard:
                try:
                    kc = getattr(Keycode, key)
                    keyboard.press(kc)
                    keyboard.release_all()
                except AttributeError:
                    print("Key not recognized:", key)
            else:
                print("Keyboard not initialized")
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
        if layout:
            try:
                layout.write(text)
            except Exception as e:
                print("Write error:", e)
                return False
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
print("=== Pico Serial Keyboard Started ===")

# LED blink timing
led_timer = time.monotonic() # Monotonic timer for non-blocking LED toggle
led_state = False

while True:
    chunk = uart.read()
    if chunk:
        buffer += chunk

        # process line by line
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

    # non-blocking LED toggle every 1 second
    now = time.monotonic()
    if now - led_timer >= 1.0:
        if led:
            led_state = not led_state
            led.value = led_state
        led_timer = now

    # small pause to avoid busy-wait
    time.sleep(0.01)