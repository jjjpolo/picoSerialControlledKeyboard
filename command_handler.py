"""
CommandHandler class for Pico Serial Keyboard
Handles command dispatch and execution.
"""
from macros import run_macro, send_hotkey

class CommandHandler:
    def __init__(self, keyboard, layout, macros, log):
        self.keyboard = keyboard
        self.layout = layout
        self.macros = macros
        self.log = log
        self.dispatch = {
            "type": self.cmd_type,
            "hotkey": self.cmd_hotkey,
            "macro": self.cmd_macro,
        }

    def handle(self, data: dict) -> bool:
        """
        Handle a command dictionary received from serial input using a dispatch table.
        Args:
            data (dict): The parsed JSON command.
        Returns:
            bool: True if command handled successfully, False otherwise.
        """
        cmd = data.get("cmd")
        handler = self.dispatch.get(cmd)
        if handler:
            return handler(data)
        else:
            self.log.debug(f"Unknown command: {cmd}")
            return False

    def cmd_type(self, data):
        text = data.get("text", "")
        if self.layout:
            try:
                self.layout.write(text)
            except Exception as e:
                self.log.error("Write error:", e)
                return False
        self.log.info(f"Typed text: {text}")
        return True

    def cmd_hotkey(self, data):
        keys = data.get("keys", [])
        self.log.info(f"Hotkey command: {keys}")
        return send_hotkey(keys, self.keyboard, self.log)

    def cmd_macro(self, data):
        name = data.get("name", "")
        self.log.info(f"Macro command: {name}")
        return run_macro(name, self.macros, self.keyboard, self.layout, self.log)
