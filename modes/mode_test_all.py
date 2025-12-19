from devices.pump_channel import PumpChannel
import time


def _test_channel(ch: PumpChannel, test_volume_ml: float = 0.5):
    """
    Basic test sequence for a single channel:
    - home the axis
    - toggle valve
    - aspirate a small volume
    - dispense the same volume back
    """
    print("=== Test start for", ch.name, "===")

    ok = ch.home()
    if not ok:
        print("  Homing FAILED for", ch.name, "- skipping this channel.")
        print("=== Test aborted for", ch.name, "===")
        return

    print("  Valve test for", ch.name)
    ch.open_valve()
    time.sleep_ms(200)
    ch.close_valve()
    time.sleep_ms(200)

    print("  Motion test for", ch.name, "volume_ml =", test_volume_ml)
    ch.aspirate_ml(test_volume_ml)
    time.sleep_ms(200)
    ch.dispense_ml(test_volume_ml)

    print("=== Test finished for", ch.name, "===\n")


def run(channels: list[PumpChannel]):
    """
    Test mode for all provided channels.

    Simply iterates over the list and runs the basic test sequence
    on each channel in order.
    """
    if not channels:
        print("mode_test_all: no channels provided.")
        return

    print("=== mode_test_all: starting tests for all channels ===")
    for ch in channels:
        _test_channel(ch)
    print("=== mode_test_all: done ===")
