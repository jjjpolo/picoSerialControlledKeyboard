```
Wiring Diagram (Text Version)
----------------------------

Raspberry Pi Pico Pinout:

- GP0  (Pin 1)  → UART RX (connect to TX of controller, e.g. ESP32/Arduino)
- GP1  (Pin 2)  → UART TX (connect to RX of controller)
- GP15 (Pin 21) → Boot sequence cancel button (one side to GP15, other side to GND)
- GP25 (Pin 37) → Onboard LED (used for status/heartbeat)
- GND  (Pin 38) → Ground (connect to controller GND and button)
- USB  (micro-B) → Connect to host computer (for keyboard emulation)

Button:
- Use a simple pushbutton between GP15 and GND.

Minimal Example:

  [Controller TX] ----> [Pico GP0]
  [Controller RX] <---- [Pico GP1]
  [Button] ------------ [Pico GP15] ---+--- [GND]
                                      |
                                   [Pico GND]

- No external pull-down resistor is needed; the code enables the internal pull-down on GP15.
- Power the Pico via USB.

For a graphical pinout, see: https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html#pinout-and-schematics
```
