BOOT_BTN_PIN = 15  # board.GP15
LED_PIN = 25      # board.GP25
import board
import busio
import digitalio

def setup_uart():
    return busio.UART(board.GP0, board.GP1, baudrate=115200, timeout=0.01)

def setup_button(log=None):
    try:
        boot_btn = digitalio.DigitalInOut(getattr(board, f"GP{BOOT_BTN_PIN}"))
        boot_btn.direction = digitalio.Direction.INPUT
        boot_btn.pull = digitalio.Pull.DOWN
        if log:
            log.debug(f"Boot interrupt button initialized on GP{BOOT_BTN_PIN}")
        return boot_btn
    except Exception as e:
        if log:
            log.error("Boot button init error:", e)
        return None

def is_boot_btn_pressed(boot_btn):
    return boot_btn and boot_btn.value

def setup_led(log=None):
    try:
        led = digitalio.DigitalInOut(getattr(board, f"GP{LED_PIN}"))
        led.direction = digitalio.Direction.OUTPUT
        if log:
            log.debug(f"LED initialized on GP{LED_PIN}")
        return led
    except Exception as e:
        if log:
            log.error("LED init error:", e)
        return None

def blink_led(led, times=1, duration=0.1):
    import time
    if not led:
        return
    for _ in range(times):
        led.value = True
        time.sleep(duration)
        led.value = False
        time.sleep(duration)

def boot_delay_led_pattern(led, duration_s):
    import time
    if not led:
        time.sleep(duration_s)
        return
    end_time = time.monotonic() + duration_s
    while time.monotonic() < end_time:
        led.value = True
        time.sleep(0.1)
        led.value = False
        time.sleep(0.1)
