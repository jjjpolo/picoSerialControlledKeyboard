"""Command routing layer for incoming serial JSON commands.

Maps command names to handlers and executes typing, hotkey, macro, and
shutdown actions for the main firmware loop.
"""
from macros import run_macro, send_hotkey, send_mouse_action

class CommandHandler:
    def __init__(self, keyboard, layout, macros, log, mouse=None):
        self.keyboard = keyboard
        self.layout = layout
        self.macros = macros
        self.log = log
        self.mouse = mouse
        self._shutdown_requested = False
        self.dispatch = {
            "type": self.cmd_type,
            "hotkey": self.cmd_hotkey,
            "macro": self.cmd_macro,
            "mouse": self.cmd_mouse,
            "shutdown": self.cmd_shutdown,
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

    @property
    def shutdown_requested(self):
        return self._shutdown_requested

    def cmd_shutdown(self, data):
        self.log.info("Shutdown command received. Exiting main loop.")
        self._shutdown_requested = True
        return True

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
        return run_macro(name, self.macros, self.keyboard, self.layout, self.mouse, self.log)

    def cmd_mouse(self, data):
        self.log.info(f"Mouse command: {data}")
        action = {"type": "mouse"}
        action.update({key: value for key, value in data.items() if key != "cmd"})
        return send_mouse_action(action, self.mouse, self.log)
