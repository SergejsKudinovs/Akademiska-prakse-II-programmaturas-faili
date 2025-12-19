PUMP_COUNT = 5

DEFAULT_PULSE_US = 1000  # base pulse width for step impulses
MIN_PULSE_US = 400           # fastest allowed (smaller = faster)
MAX_PULSE_US = 3000          # slowest allowed

# Steps limit during homing to avoid endless movement if limit switch fails
HOMING_MAX_STEPS = 15000     # safety limit for homing travel
HOMING_BACKOFF_STEPS = 50    # small backoff after hitting limit

# Direction convention for homing:
# Value written to DIR pin that moves the plunger "up" (towards limit switch)
HOMING_DIR_UP_VALUE = 0      # set to 0 or 1 depending on your wiring
HOMING_DIR_DOWN_VALUE = 1    # opposite direction
# Example calibration: how many steps per 1 ml (to be tuned experimentally)
DEFAULT_STEPS_PER_ML = 362

# GPIO numbers for the shared limit switch bus
LIMIT_BUS_PIN = 20  # TODO: set real pin number
LIMIT_BUS_ACTIVE_LOW = True
LIMIT_DEBOUNCE_MS = 5

MAIN_PUMP_PIN = 17
SERVO_PIN = 16 
GLOBAL_SOLENOID_PIN = 5

CHANNEL_CONFIGS = [
    {
        "name": "CH1",
        "enabled": True,
        "dir_pin": 28,
        "pul_pin": 6,
        "valve_pin": 0,
        "dir_up": HOMING_DIR_UP_VALUE,
        "dir_down": HOMING_DIR_DOWN_VALUE,
        "steps_per_ml": DEFAULT_STEPS_PER_ML,
    },
    {
        "name": "CH2",
        "enabled": True,
        "dir_pin": 27,
        "pul_pin": 7,
        "valve_pin": 1,
        "dir_up": HOMING_DIR_UP_VALUE,
        "dir_down": HOMING_DIR_DOWN_VALUE,
        "steps_per_ml": DEFAULT_STEPS_PER_ML,
    },
    {
        "name": "CH3",
        "enabled": True,
        "dir_pin": 26,
        "pul_pin": 8,
        "valve_pin": 2,
        "dir_up": HOMING_DIR_UP_VALUE,
        "dir_down": HOMING_DIR_DOWN_VALUE,
        "steps_per_ml": DEFAULT_STEPS_PER_ML,
    },
    {
        "name": "CH4",
        "enabled": True,
        "dir_pin": 22,
        "pul_pin": 9,
        "valve_pin": 3,
        "dir_up": HOMING_DIR_UP_VALUE,
        "dir_down": HOMING_DIR_DOWN_VALUE,
        "steps_per_ml": DEFAULT_STEPS_PER_ML,
    },
    {
        "name": "CH5",
        "enabled": True,
        "dir_pin": 21,
        "pul_pin": 10,
        "valve_pin": 4,
        "dir_up": HOMING_DIR_UP_VALUE,
        "dir_down": HOMING_DIR_DOWN_VALUE,
        "steps_per_ml": DEFAULT_STEPS_PER_ML,
    },
]
