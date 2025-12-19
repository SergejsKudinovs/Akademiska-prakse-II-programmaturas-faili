import config
from drivers.limit_bus import LimitBus
from devices.pump_channel import PumpChannel
from modes import mode_serial_control


def build_channels(limit_bus: LimitBus) -> list[PumpChannel]:
    """
    Create PumpChannel instances based on configuration.
    Channels with enabled=False are skipped.
    """
    channels: list[PumpChannel] = []

    for ch_conf in config.CHANNEL_CONFIGS:

        # Skip disabled channels (enabled = False)
        if not ch_conf.get("enabled", True):
            print("Skipping disabled channel:", ch_conf.get("name"))
            continue

        ch = PumpChannel(
            name=ch_conf["name"],
            dir_pin_num=ch_conf["dir_pin"],
            pul_pin_num=ch_conf["pul_pin"],
            valve_pin_num=ch_conf["valve_pin"],
            limit_bus=limit_bus,
            limit_id=ch_conf["limit_id"],
            dir_up=ch_conf.get("dir_up", config.HOMING_DIR_UP_VALUE),
            dir_down=ch_conf.get("dir_down", config.HOMING_DIR_DOWN_VALUE),
            steps_per_ml=ch_conf.get("steps_per_ml", config.DEFAULT_STEPS_PER_ML),
        )
        channels.append(ch)

    return channels



def main():
    print("=== Mixing system startup ===")

    limit_bus = LimitBus(pin_num=config.LIMIT_BUS_PIN, pull_up=True)

    channels = build_channels(limit_bus)

    # Choose which mode to run:
    # 1) Only CH1/CH2:
    # mode_test_ch1_ch2.run(channels)

    # 2) All channels:
    mode_serial_control.run(channels)

    print("=== Mixing system finished ===")
