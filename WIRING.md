```
Wiring Diagram (Text Version)
----------------------------

Raspberry Pi Pico Pinout:

- GP0  (Pin 1)  → UART RX (connect to TX of controller, e.g. ESP32/Arduino)
- GP1  (Pin 2)  → UART TX (connect to RX of controller)
- GP15 (Pin 20) → Boot sequence cancel button (one side to GP15, other side to GND)
- GP25 (Pin 37) → Onboard LED (used for status/heartbeat)
- GND  (Pin 38) → Ground (connect to controller GND and button)
- RUN  (Pin 30) → Reset button (one side to RUN, other side to GND)
- USB  (micro-B) → Connect to host computer (for keyboard emulation)

Buttons:
- Boot cancel: simple pushbutton between GP15 and GND.
- Reset: simple pushbutton between RUN (Pin 30) and GND. Resets the Pico instantly.

Minimal Example:

  [Controller TX] ----> [Pico GP0]
  [Controller RX] <---- [Pico GP1]
  [Boot Btn] ---------- [Pico GP15] ---+--- [GND]
                                      |
                                   [Pico GND]
  [Reset Btn] --------- [Pico RUN]  ---+--- [GND]

- No external pull-up resistor is needed; the code enables the internal pull-up on GP15.
- The RUN pin has an internal pull-up; pulling it LOW resets the board.
- Power the Pico via USB.

For a graphical pinout, see: https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html#pinout-and-schematics
```
