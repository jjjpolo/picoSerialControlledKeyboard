# Pico Serial Controlled Keyboard

A CircuitPython project for controlling a keyboard via serial on Raspberry Pi Pico.

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

## Usage

- Connect to the Pico via serial (UART on GP0/GP1 at 115200 baud).
- Send commands to trigger keyboard macros (e.g., "shutdown_windows", "abrir_terminal").

## Version

Current version: 1.0.0
