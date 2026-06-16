"""Minimal logging utility with debug/info/error levels for firmware output."""

class Log:
    def __init__(self, debug_level=0):
        self.debug_level = debug_level
    def debug(self, *args, **kwargs):
        if self.debug_level >= 1:
            print("[DEBUG]", *args, **kwargs)
    def info(self, *args, **kwargs):
        if self.debug_level >= 0:
            print("[INFO]", *args, **kwargs)
    def error(self, *args, **kwargs):
        print("[ERROR]", *args, **kwargs)
