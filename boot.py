"""Boot sequence for Pico Serial Keyboard.

Runs before main code. Reads config.json and disables USB mass storage
if usb_mass_storage_enabled is set to false.
"""

import json
import storage

# Read config
try:
    with open("config.json", "r") as f:
        config = json.load(f)
except Exception as e:
    print(f"[BOOT] Error reading config.json: {e}")
    config = {}

# Disable USB mass storage if configured
usb_mass_storage_enabled = config.get("usb_mass_storage_enabled", True)
if not usb_mass_storage_enabled:
    try:
        storage.disable_usb_drive()
        print("[BOOT] USB mass storage disabled")
    except Exception as e:
        print(f"[BOOT] Error disabling USB mass storage: {e}")
else:
    print("[BOOT] USB mass storage enabled")
