# Pico Serial Controlled Keyboard

This project turns a Raspberry Pi Pico into a programmable USB keyboard that is controlled by serial commands. The Pico receives commands over UART (serial) and translates them into USB keyboard actions on the connected computer.

## What is this for?
- **Automate keyboard input**: Send keystrokes, hotkeys, or macros to a PC or other USB host.
- **Remote control**: Use another device (like an ESP32, Arduino, or any microcontroller with UART) to send commands to the Pico, which then acts as a USB keyboard.
- **Server integration**: For example, an ESP device can run a web server or REST API, receive HTTP requests, and convert those into serial commands for the Pico. The Pico then performs the requested keyboard actions on the host computer.
- **Testing, automation, accessibility, or IoT**: Useful for kiosks, automated testing, accessibility devices, or any project where you want to control a computer via serial or networked commands.

## How it works
- The Pico runs CircuitPython and listens for JSON-formatted commands on its UART (default: GP0/GP1, 115200 baud).
- When a valid command is received, the Pico executes the corresponding keyboard action (type text, press hotkeys, or run macros defined in `macros.json`).
- The Pico appears as a standard USB keyboard to the host computer.

## Prerequisites

- Raspberry Pi Pico with CircuitPython firmware
- CMake (for build automation)
- PowerShell (for deployment scripts)

## Setup

1. Clone or download this repository.
2. Ensure your Pico is mounted (default drive: D:). Adjust `PICO_DRIVE` in CMakeLists.txt if needed.
3. Load required libraries (Pico has limited storage, so only copy what you need):
   - Download the Adafruit CircuitPython bundle from https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases
   - Extract and copy **only** these folders to `lib/` on your Pico:
     - `adafruit_hid/`
     - `adafruit_bus_device/`
   - **Don't copy the entire `lib/` folder** — it's too large for the Pico's storage

## Using CMake

This project uses CMake for automation tasks. After installing CMake:

1. Generate build files:
   ```
   cmake .
   ```

2. Run targets:
   - Install dependencies (downloads Adafruit CircuitPython bundle):
     ```
     cmake --build . --target install-deps
     ```
   - Deploy code to Pico:
     ```
     cmake --build . --target deploy
     ```
   - Clean project files:
     ```
     cmake --build . --target clean-all
     ```

## Customization

Macros are defined in `macros.json`. Each macro is a list of actions:

- `{"type": "hotkey", "keys": ["KEY1", "KEY2"]}` - Press multiple keys simultaneously
- `{"type": "write", "text": "string"}` - Type text
- `{"type": "press", "key": "KEY"}` - Press a single key
- `{"type": "delay", "seconds": 0.5}` - Wait for specified seconds

Example:
```json
{
  "my_macro": [
    {"type": "hotkey", "keys": ["CTRL", "C"]},
    {"type": "delay", "seconds": 0.1},
    {"type": "write", "text": "Hello World"}
  ]
}
```

## Manual Library Installation (if CMake is not working)

If you can't use CMake, you can manually install the required libraries:

1. Download the [Adafruit CircuitPython Bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases) matching your CircuitPython version.
2. Unzip the bundle on your computer.
3. Copy the following folders from the bundle's `lib/` directory to the `lib/` folder on your Pico:
   - `adafruit_hid/`
   - `adafruit_bus_device/`
4. Your Pico's `lib/` folder should now contain only the folders you need (not the entire bundle).

## Serial Command Usage Examples

You can control the Pico by sending JSON commands over UART (GP0/GP1, 115200 baud). Each command must be a single line of valid JSON.

### Type Text
```
{"cmd": "type", "text": "hello world"}
```

### Send Hotkey
```
{"cmd": "hotkey", "keys": ["LEFT_CONTROL", "C"]}
```

### Run a Macro
```
{"cmd": "macro", "name": "abrir_terminal"}
```

### Shutdown PC Macro (Windows)
```
{"cmd": "macro", "name": "shutdown_pc"}
```

- Macros are defined in `macros.json`. See that file for available macro names and key options.
- For Windows key, use `"GUI"`. For Ctrl, use `"LEFT_CONTROL"` or `"RIGHT_CONTROL"`.
- All key names must match those in [adafruit_hid.keycode.Keycode](https://circuitpython.readthedocs.io/projects/hid/en/latest/api.html#adafruit_hid.keycode.Keycode).

## Mouse Jiggler (Prevent Sleep)

This project includes a configurable mouse jiggler feature. When enabled, the Pico will move the mouse cursor right and then left by 2 pixels every 60 seconds. This subtle movement prevents your computer from locking or going to sleep due to inactivity, without disturbing your work.

- The jiggler is controlled by the `config.json` file:
  ```json
  {
    "mouse_jiggler_enabled": true
  }
  ```
- Set `mouse_jiggler_enabled` to `false` to disable the feature.
- Make sure `adafruit_hid/mouse.py` is present in your Pico's `lib/` folder.

No serial command is needed; the jiggler runs automatically if enabled in the config.

## Troubleshooting
- If macros or hotkeys don't work, check your key names in `macros.json`.
- Make sure your serial terminal sends a newline (\n) at the end of each command.
- If CMake fails, use the manual library installation steps above.

## Version

Current version: 1.0.0
