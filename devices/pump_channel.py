from drivers.stepper_tb6600 import StepperTB6600
from drivers.mosfet_driver import MosfetDriver
from drivers.limit_bus import LimitBus
import config


class PumpChannel:
    """
    High-level abstraction for one syringe channel:
    - one stepper motor (via TB6600)
    - one valve MOSFET
    - shared limit bus for homing
    """

    def __init__(
        self,
        name: str,
        dir_pin_num: int,
        pul_pin_num: int,
        valve_pin_num: int,
        limit_bus: LimitBus,
        limit_id: int,
        dir_up: int | None = None,
        dir_down: int | None = None,
        steps_per_ml: float | None = None,
    ):
        self.name = name
        self.limit_id = limit_id  # logical id, reserved for future use
        self.limit_bus = limit_bus

        # Direction convention for this channel
        # (values written directly into DIR pin)
        if dir_up is None:
            dir_up = config.HOMING_DIR_UP_VALUE
        if dir_down is None:
            dir_down = config.HOMING_DIR_DOWN_VALUE

        self.dir_up = 1 if dir_up else 0
        self.dir_down = 1 if dir_down else 0

        # Calibration (steps per milliliter)
        if steps_per_ml is None:
            steps_per_ml = config.DEFAULT_STEPS_PER_ML
        self.steps_per_ml = float(steps_per_ml)

        # Low-level drivers
        self.stepper = StepperTB6600(
            dir_pin_num=dir_pin_num,
            pul_pin_num=pul_pin_num,
            default_pulse_us=config.DEFAULT_PULSE_US,
        )
        self.valve = MosfetDriver(pin_num=valve_pin_num, active_high=True)

        # Internal state flags
        self.homed = False

    # -------- Valve control --------

    def open_valve(self):
        """Open the valve for this channel."""
        self.valve.on()

    def close_valve(self):
        """Close the valve for this channel."""
        self.valve.off()

    # -------- Homing logic --------

    def home(self) -> bool:
        """
        Move the plunger towards the mechanical top until the limit bus is active,
        then back off slightly.

        Returns:
            True  on successful homing
            False if homing failed (no limit detected within max steps)
        """
        print("Homing:", self.name)

        max_steps = config.HOMING_MAX_STEPS
        backoff_steps = config.HOMING_BACKOFF_STEPS

        # Use default speed for homing (can be adjusted later if needed)
        self.stepper.set_default_pulse_us(config.DEFAULT_PULSE_US)

        steps_done = 0

        # Safety: if the bus is already pressed, we can either back off first
        # or treat it as already at the limit. For now we try to move away
        # a little if active at start.
        if self.limit_bus.is_any_pressed(debounce=True):
            print("  Warning:", self.name, "limit bus already active at start of homing.")
            # Optional: small move away from limit before going up again
            # self.stepper.step(self.dir_down, backoff_steps)

        # Move towards the limit (UP) step-by-step,
        # checking the shared bus after each step.
        while not self.limit_bus.is_any_pressed(debounce=False):
            self.stepper.step(self.dir_up, 1)
            steps_done += 1

            if steps_done >= max_steps:
                print("  ERROR:", self.name, "homing max steps reached without hitting limit.")
                self.homed = False
                return False

        # Confirm with debounce that the bus is really active
        if not self.limit_bus.is_any_pressed(debounce=True):
            print("  ERROR:", self.name, "limit signal not stable during homing.")
            self.homed = False
            return False

        # Small backoff in the opposite direction to release mechanical stress
        if backoff_steps > 0:
            self.stepper.step(self.dir_down, backoff_steps)

        self.homed = True
        print("  Homing OK for", self.name, "- steps taken:", steps_done)
        return True

    # -------- Volume-based moves --------

    def _volume_to_steps(self, volume_ml: float) -> int:
        """
        Convert volume in milliliters to a whole number of motor steps.
        """
        steps = int(round(volume_ml * self.steps_per_ml))
        if steps < 0:
            steps = -steps  # ensure non-negative; direction is handled separately
        return steps

    def aspirate_ml(self, volume_ml: float) -> int:
        """
        Pull the plunger to aspirate a given volume in ml.

        By default we assume:
        - "aspirate" = move AWAY from the homing limit (dir_down).
        If your mechanical setup is different, swap dir_up/dir_down
        in config or adjust this method accordingly.

        Returns:
            number of steps actually performed.
        """
        if volume_ml <= 0:
            return 0

        steps = self._volume_to_steps(volume_ml)
        print("Aspirate:", self.name, "volume_ml =", volume_ml, "steps =", steps)
        self.stepper.step(self.dir_down, steps)
        return steps

    def dispense_ml(self, volume_ml: float) -> int:
        """
        Push the plunger to dispense a given volume in ml.

        By default we assume:
        - "dispense" = move TOWARDS the homing limit (dir_up).

        Returns:
            number of steps actually performed.
        """
        if volume_ml <= 0:
            return 0

        steps = self._volume_to_steps(volume_ml)
        print("Dispense:", self.name, "volume_ml =", volume_ml, "steps =", steps)
        self.stepper.step(self.dir_up, steps)
        return steps
