from machine import Pin
import time


class StepperTB6600:
    """
    Low-level driver for a single TB6600 stepper channel.

    This class only knows how to:
    - set DIR level
    - generate step pulses on PUL pin

    It does NOT know:
    - what "up" or "down" means physically
    - how many steps correspond to 1 ml
    - homing logic or safety limits

    All high-level decisions (direction, step counts, speeds)
    are handled by higher-level code (e.g. PumpChannel).
    """

    def __init__(self, dir_pin_num, pul_pin_num, default_pulse_us):
        """
        dir_pin_num: GPIO number used for DIR+ on TB6600.
        pul_pin_num: GPIO number used for PUL+ on TB6600.
        default_pulse_us: default pulse width in microseconds.
        """
        # Configure direction and pulse pins
        self.dir = Pin(dir_pin_num, Pin.OUT, value=0)
        self.pul = Pin(pul_pin_num, Pin.OUT, value=0)

        # Default pulse length (HIGH or LOW half-period)
        self.default_pulse_us = int(default_pulse_us)

    def set_default_pulse_us(self, pulse_us):
        """
        Update the default pulse width (speed).

        Smaller pulse_us -> faster movement.
        """
        self.default_pulse_us = int(pulse_us)

    def step(self, direction, steps, pulse_us=None):
        """
        Perform a given number of steps at constant speed.

        direction: 0 or 1, directly written to DIR pin.
                   Higher level decides which value means "up" or "down".
        steps: positive integer number of steps to execute.
        pulse_us: custom pulse width; if None, uses self.default_pulse_us.

        One full step is:
        - set DIR
        - PUL HIGH for pulse_us
        - PUL LOW  for pulse_us
        """
        if steps <= 0:
            # Nothing to do
            return

        if pulse_us is None:
            pulse_us = self.default_pulse_us
        pulse_us = int(pulse_us)

        # Set direction and let it settle a bit
        self.dir.value(1 if direction else 0)
        time.sleep_us(50)  # small setup time for DIR

        # Generate "steps" pulses
        for _ in range(steps):
            # Rising edge
            self.pul.value(1)
            time.sleep_us(pulse_us)

            # Falling edge
            self.pul.value(0)
            time.sleep_us(pulse_us)
