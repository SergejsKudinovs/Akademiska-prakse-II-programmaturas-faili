from machine import Pin


class MosfetDriver:
    """Simple on/off driver for a MOSFET-controlled load (e.g. valve)."""

    def __init__(self, pin_num: int, active_high: bool = True):
        self.pin = Pin(pin_num, Pin.OUT, value=0 if active_high else 1)
        self.active_high = active_high

    def on(self):
        """Enable the MOSFET output."""
        self.pin.value(1 if self.active_high else 0)

    def off(self):
        """Disable the MOSFET output."""
        self.pin.value(0 if self.active_high else 1)
