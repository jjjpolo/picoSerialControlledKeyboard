import board
import digitalio
import time

print("=== LED Blink Test ===")

try:
    led = digitalio.DigitalInOut(board.GP25)
    led.direction = digitalio.Direction.OUTPUT
    print("LED initialized on GP25")
except Exception as e:
    print("LED init error:", e)
    led = None

if led:
    print("Starting blink loop...")
    while True:
        led.value = True
        print("LED ON")
        time.sleep(1)
        
        led.value = False
        print("LED OFF")
        time.sleep(1)
else:
    print("ERROR: Could not initialize LED")
