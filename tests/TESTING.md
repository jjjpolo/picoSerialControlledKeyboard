# Unit Testing for Pico Serial Controlled Keyboard

This project includes basic unit tests for core logic (config, macros, command handler) that can be run on your development machine (not on the Pico).

## Structure

- `test_config_manager.py`: Tests config loading, setting, and reload logic.
- `test_macros.py`: Tests macro execution and hotkey/text logic with dummy keyboard/layout.
- `test_command_handler.py`: Tests command dispatch, shutdown, and error handling.

## How to Run the Tests

1. Make sure you have Python 3.x installed on your computer (not the Pico).
2. From the project root, run each test script directly:

   ```sh
   python tests/test_config_manager.py
   python tests/test_macros.py
   python tests/test_command_handler.py
   ```

   Or run all at once (Linux/macOS):
   ```sh
   for f in tests/test_*.py; do python "$f"; done
   ```

3. Each test will print a success message if it passes. Any assertion failure or error will be shown in the terminal.

## Notes
- These tests use dummy/mock classes for hardware and logging.
- They do not require CircuitPython or actual hardware.
- For more advanced testing, consider using `pytest` and expanding the dummy classes.
- These tests are for development logic only; they do not test hardware I/O or USB HID behavior.
