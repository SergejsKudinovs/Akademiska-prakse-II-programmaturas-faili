from machine import Pin
import time
import config


class LimitBus:
    """
    Represents a shared limit-switch bus.

    Physically this is a single GPIO connected to several mechanical
    limit switches. This class only answers the question:
    "Is ANY limit switch currently pressed?"

    Important assumptions:
    - All limit switches are wired together to the same signal line.
    - Active level (low or high) is configured in config.LIMIT_BUS_ACTIVE_LOW.
    """

    def __init__(
        self,
        pin_num: int | None = None,
        pull_up: bool = True,
        active_low: bool | None = None,
        debounce_ms: int | None = None,
    ):
        """
        pin_num: GPIO number used for the limit bus input.
                 If None, uses config.LIMIT_BUS_PIN.
        pull_up: whether to enable internal pull-up on this pin.
        active_low: if True, "pressed" means pin reads 0.
                    if False, "pressed" means pin reads 1.
                    If None, uses config.LIMIT_BUS_ACTIVE_LOW.
        debounce_ms: debounce time in milliseconds for stable detection.
                     If None, uses config.LIMIT_DEBOUNCE_MS.
        """
        if pin_num is None:
            pin_num = config.LIMIT_BUS_PIN

        if active_low is None:
            active_low = config.LIMIT_BUS_ACTIVE_LOW

        if debounce_ms is None:
            debounce_ms = config.LIMIT_DEBOUNCE_MS

        # Configure input pin
        if pull_up:
            self.pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)
        else:
            self.pin = Pin(pin_num, Pin.IN)

        self.active_low = active_low
        self.debounce_ms = int(debounce_ms)

    # ---------- Low-level reading helpers ----------

    def _raw_level(self) -> int:
        """
        Return the raw digital level from the pin (0 or 1).
        No interpretation is applied here.
        """
        return self.pin.value()

    def is_active_raw(self) -> bool:
        """
        Check if the bus is active WITHOUT debounce.

        "Active" means that at least one limit switch is pressed,
        according to the active_low flag.
        """
        level = self._raw_level()
        if self.active_low:
            # Active when pin is pulled low (0)
            return level == 0
        else:
            # Active when pin is pulled high (1)
            return level == 1

    # ---------- Debounced checks ----------

    def is_any_pressed(self, debounce: bool = True) -> bool:
        """
        Return True if any limit switch is pressed.

        If debounce=True, a simple time-based debounce is applied:
        - read once
        - if active, wait debounce_ms
        - read again and confirm
        """
        if not debounce:
            return self.is_active_raw()

        # First check
        if not self.is_active_raw():
            return False

        # Wait debounce interval and confirm
        time.sleep_ms(self.debounce_ms)
        return self.is_active_raw()

    # ---------- Blocking wait helpers (optional but useful) ----------

    def wait_until_pressed(
        self,
        timeout_ms: int | None = None,
        poll_ms: int = 1,
        debounce: bool = True,
    ) -> bool:
        """
        Block until the bus becomes active (a limit switch is pressed),
        or until timeout_ms is exceeded.

        Returns:
            True  if pressed before timeout,
            False if timeout was reached (or timeout_ms is None and never pressed).
        """
        start = time.ticks_ms()
        while True:
            if self.is_any_pressed(debounce=debounce):
                return True

            if timeout_ms is not None:
                now = time.ticks_ms()
                if time.ticks_diff(now, start) >= timeout_ms:
                    return False

            time.sleep_ms(poll_ms)

    def wait_until_released(
        self,
        timeout_ms: int | None = None,
        poll_ms: int = 1,
        debounce: bool = True,
    ) -> bool:
        """
        Block until the bus becomes inactive (no limit pressed),
        or until timeout_ms is exceeded.

        Returns:
            True  if released before timeout,
            False if timeout was reached.
        """
        start = time.ticks_ms()
        while True:
            if not self.is_any_pressed(debounce=debounce):
                return True

            if timeout_ms is not None:
                now = time.ticks_ms()
                if time.ticks_diff(now, start) >= timeout_ms:
                    return False

            time.sleep_ms(poll_ms)
