###############################
# Constants and Defaults      #
###############################
UART_RX_PIN = 0  # board.GP0
UART_TX_PIN = 1  # board.GP1
BOOT_BTN_PIN = 15  # board.GP15
LED_PIN = 25  # board.GP25
UART_BAUDRATE = 115200
UART_TIMEOUT = 0.01
LED_HEARTBEAT_INTERVAL_MS = 1000  # 1 second
MOUSE_JIGGLER_DEFAULT_INTERVAL_MS = 60000  # 60 seconds
BOOT_DELAY_DEFAULT_MS = 3000


import time
import json
import usb_hid
from config_manager import ConfigManager
from logger import Log
from macros import load_macros, run_macro, execute_sequence, send_hotkey
from command_handler import CommandHandler
from hardware import setup_uart, setup_button, setup_led, blink_led, boot_delay_led_pattern, is_boot_btn_pressed
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.mouse import Mouse

__version__ = "1.0.0 - DEV"

# Set log level for 1st use as debug since config is loaded later and may override it
log = Log(debug_level=1)

# Load macros using macros.py
macros = load_macros(log)

# Instantiate config manager
config = ConfigManager(log=log)
# Reset log level to config value after loading config
log = Log(debug_level=config.get_config("debug", 0))
config.log = log

# --- UART CONFIG ---
uart = setup_uart()

# --- BUTTON and LED setup ---
boot_btn = setup_button(log)
led = setup_led(log)

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



###############################
# Command Handler Setup        #
###############################
# Instantiate the command handler
command_handler = CommandHandler(keyboard, layout, macros, log)


def main() -> None:
    """
    Main application loop. Handles UART input, macro execution, mouse jiggler, and LED heartbeat.
    """
    buffer = b""
    log.info(f"=== Pico Serial Keyboard Started V{__version__} ===")

    # LED heartbeat counter (for delay management)
    led_counter: int = 0
    led_counter_max: int = int(LED_HEARTBEAT_INTERVAL_MS / 10)  # 0.01s * N = interval
    led_state: bool = False

    # Mouse jiggler counter (for delay management)
    jiggle_counter: int = 0
    jiggle_counter_max: int = config.get_config("mouse_jiggler_interval_ms", MOUSE_JIGGLER_DEFAULT_INTERVAL_MS)

    # --- Boot sequence with interruptible delay (counter-based) ---
    boot_macro = config.get_config("boot_macro")
    boot_delay_ms = config.get_config("boot_delay_ms", BOOT_DELAY_DEFAULT_MS)
    if boot_macro:
        log.info(f"Boot sequence will start in {boot_delay_ms/1000:.1f}s. Press button to cancel.")
        # LED pattern and button check during delay
        delay_loops = int(boot_delay_ms / 10)  # 0.01s per loop
        cancelled = False
        for _ in range(delay_loops):
            if led:
                led.value = not led.value
            time.sleep(0.01)
            if is_boot_btn_pressed(boot_btn):
                cancelled = True
                break
        if led:
            led.value = False
        if cancelled:
            log.info("Boot sequence cancelled by user.")
        else:
            log.info(f"Executing boot macro: {boot_macro}")
            run_macro(boot_macro, macros, keyboard, layout, log)

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
                    ok = command_handler.handle(data)

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
                    blink_led(led, times=3, duration=0.08)  # blink 3 times for jiggler
                    # Restore LED state so heartbeat pattern is not affected
                    if led:
                        led.value = prev_led_state
                jiggle_counter = 0

        # small pause to avoid busy-wait
        time.sleep(0.01)

if __name__ == "__main__":
    main()