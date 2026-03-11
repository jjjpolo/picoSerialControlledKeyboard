import board
import busio
import digitalio
import json
from config_manager import ConfigManager
import time
import usb_hid

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.mouse import Mouse

__version__ = "1.0.0 - DEV"

# --- Simple logging class ---
class Log:
    def __init__(self, debug_level=0):
        self.debug_level = debug_level
    def debug(self, *args, **kwargs):
        if self.debug_level >= 1:
            print(*args, **kwargs)
    def info(self, *args, **kwargs):
        if self.debug_level >= 0:
            print(*args, **kwargs)

# Set log level for 1st use as debug since config is loaded later and may override it
log = Log(debug_level=1)

# Load macros from JSON
try:
    with open("macros.json", "r") as f:
        macros = json.load(f)
except Exception as e:
    log.error("Error loading macros:", e)
    macros = {}


# Instantiate config manager
config = ConfigManager(log=log)
# Reset log level to config value after loading config
log = Log(debug_level=config.get_config("debug", 0))
config.log = log


# --- UART CONFIG ---
uart = busio.UART(board.GP0, board.GP1, baudrate=115200, timeout=0.01)  # RX=GP0, TX=GP1


# --- BUTTON for boot sequence interrupt (developer-defined, GP15) ---
try:
    boot_btn = digitalio.DigitalInOut(board.GP15)
    boot_btn.direction = digitalio.Direction.INPUT
    boot_btn.pull = digitalio.Pull.DOWN
    log.debug("Boot interrupt button initialized on GP15")
except Exception as e:
    log.error("Boot button init error:", e)
    boot_btn = None

# --- HELPER: check if button pressed ---
def is_boot_btn_pressed():
    return boot_btn and boot_btn.value

# --- HELPER: special LED pattern for boot delay ---
def boot_delay_led_pattern(duration_s):
    if not led:
        time.sleep(duration_s)
        return
    end_time = time.monotonic() + duration_s
    while time.monotonic() < end_time:
        led.value = True
        time.sleep(0.1)
        led.value = False
        time.sleep(0.1)

# --- LED for testing ---
try:
    led = digitalio.DigitalInOut(board.GP25)
    led.direction = digitalio.Direction.OUTPUT
    log.debug("LED initialized on GP25")
except Exception as e:
    log.error("LED init error:", e)
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
    log.debug("Keyboard initialized")
except Exception as e:
    log.error("Keyboard init error:", e)
    keyboard = None
    layout = None

# --- HID MOUSE ---
try:
    mouse = Mouse(usb_hid.devices)
    log.debug("Mouse initialized")
except Exception as e:
    log.error("Mouse init error:", e)
    mouse = None

# --- HELPER: hotkey press ---
def send_hotkey(keys):
    if not keyboard:
        log.debug("Keyboard not initialized")
        return False
    
    keycodes = []
    for k in keys:
        try:
            keycodes.append(getattr(Keycode, k))
        except AttributeError:
            log.error("Unrecognized key:", k)
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
                    log.error("Write error:", e)
        elif action_type == "press":
            key = action.get("key", "")
            if keyboard:
                try:
                    kc = getattr(Keycode, key)
                    keyboard.press(kc)
                    keyboard.release_all()
                except AttributeError:
                    log.error("Unrecognized key:", key)
            else:
                log.error("Keyboard not initialized")
        elif action_type == "delay":
            seconds = action.get("seconds", 0)
            time.sleep(seconds)
        else:
            log.error("Unknown action type:", action_type)

# --- HELPER: definir macros ---
def run_macro(name):
    if name in macros:
        execute_sequence(macros[name])
        return True
    else:
        log.error("Unknown macro:", name)
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
                log.error("Write error:", e)
                return False
        return True

    elif cmd == "hotkey":
        keys = data.get("keys", [])
        return send_hotkey(keys)

    elif cmd == "macro":
        name = data.get("name", "")
        return run_macro(name)

    else:
        log.debug("Unknown command:", cmd)
        return False

# --- MAIN LOOP ---
buffer = b""
log.info(f"=== Pico Serial Keyboard Started V{__version__} ===")


# LED heartbeat counter (for delay management)
led_counter = 0
led_counter_max = 100  # 0.01s * 100 = 1 second
led_state = False


# Mouse jiggler counter (for delay management)
jiggle_counter = 0
jiggle_counter_max = config.get_config("mouse_jiggler_interval_ms", 60000)  # default 60 seconds



# --- Boot sequence with interruptible delay (counter-based) ---
boot_macro = config.get_config("boot_macro")
boot_delay_ms = config.get_config("boot_delay_ms", 3000)  # default 3 seconds
if boot_macro:
    log.info(f"Boot sequence will start in {boot_delay_ms/1000:.1f}s. Press button to cancel.")
    # LED pattern and button check during delay
    delay_loops = int(boot_delay_ms / 10)  # 0.01s per loop
    cancelled = False
    for _ in range(delay_loops):
        if led:
            led.value = not led.value
        time.sleep(0.01)
        if is_boot_btn_pressed():
            cancelled = True
            break
    if led:
        led.value = False
    if cancelled:
        log.info("Boot sequence cancelled by user.")
    else:
        log.info(f"Executing boot macro: {boot_macro}")
        run_macro(boot_macro)

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

                log.debug("RX:", text)

                # parse JSON
                data = json.loads(text)
                ok = handle_command(data)

                # immediate response to serial controller (E.g. ESP32, prolific USB-Serial)
                if ok:
                    uart.write(b'{"status":"ok"}\n')
                else:
                    uart.write(b'{"status":"error"}\n')

            except Exception as e:
                log.error("ERROR:", e)
                uart.write(b'{"status":"invalid_json"}\n')

    # LED heartbeat using a simple counter
    led_counter += 1
    if led_counter >= led_counter_max:
        if led:
            led_state = not led_state
            led.value = led_state
        led_counter = 0
        log.debug("Heartbeat LED:", "ON" if led_state else "OFF")

    # Mouse jiggler: use a simple counter for timing
    if config.get_config("mouse_jiggler_enabled", True):
        jiggle_counter += 1
        if jiggle_counter >= jiggle_counter_max / 10:  # convert ms to counter units (0.01s)
            if mouse:
                # Save LED state to restore heartbeat after jiggler blinks
                prev_led_state = led.value if led else False
                mouse.move(1, 0)  # move right (DEBUG: larger movement)
                time.sleep(0.05)
                mouse.move(-1, 0) # move left (DEBUG: larger movement)
                log.info(f"Mouse jiggled")
                blink_led(times=3, duration=0.08)  # blink 3 times for jiggler
                # Restore LED state so heartbeat pattern is not affected
                if led:
                    led.value = prev_led_state
            jiggle_counter = 0

    # small pause to avoid busy-wait
    time.sleep(0.01)