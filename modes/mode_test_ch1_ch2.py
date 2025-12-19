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

    # 1) Homing
    ok = ch.home()
    if not ok:
        print("  Homing FAILED for", ch.name, "- skipping this channel.")
        print("=== Test aborted for", ch.name, "===")
        return

    # 2) Valve toggle test
    print("  Valve test for", ch.name)
    ch.open_valve()
    time.sleep_ms(200)
    ch.close_valve()
    time.sleep_ms(200)

    # 3) Small aspirate + dispense test
    print("  Motion test for", ch.name, "volume_ml =", test_volume_ml)
    ch.aspirate_ml(test_volume_ml)
    time.sleep_ms(200)
    ch.dispense_ml(test_volume_ml)

    print("=== Test finished for", ch.name, "===\n")


def run(channels: list[PumpChannel]):
    """
    Test mode for CH1 and CH2 only.

    It looks for channels with names "CH1" and "CH2" in the provided list
    and runs the basic test sequence on each of them (if present).
    """
    # Filter only CH1 and CH2 (if they exist in the list)
    target_names = ("CH1", "CH2")
    selected = [ch for ch in channels if ch.name in target_names]

    if not selected:
        print("mode_test_ch1_ch2: no CH1/CH2 channels found in the list.")
        return

    print("=== mode_test_ch1_ch2: starting tests for CH1/CH2 ===")
    for ch in selected:
        _test_channel(ch)
    print("=== mode_test_ch1_ch2: done ===")
