import time
import sys


def _build_channel_map(channels):
    """
    Build a dict like:
    {
      "CH1": <PumpChannel>,
      "CH2": <PumpChannel>,
      ...
    }
    """
    m = {}
    for ch in channels:
        m[ch.name.upper()] = ch
    return m


def _parse_float(s):
    try:
        return float(s)
    except Exception:
        return None


def _print_ok(msg="OK"):
    print(msg)


def _print_err(msg="ERR"):
    print(msg)


def _handle_init(tokens, channel_map):
    """
    Supported:
    - INIT
    - CHx INIT
    """
    if len(tokens) == 1 and tokens[0] == "INIT":
        # Print all available channels
        names = sorted(channel_map.keys())
        print("OK INIT " + " ".join(names))
        return

    # CHx INIT
    if len(tokens) == 2 and tokens[1] == "INIT":
        ch_name = tokens[0]
        if ch_name in channel_map:
            print(f"OK {ch_name} INIT")
        else:
            print(f"ERR {ch_name} NOT_FOUND")
        return

    _print_err("ERR INIT BAD_FORMAT")


def _handle_home(tokens, channel_map):
    """
    Supported:
    - HOME ALL
    - CHx HOME
    """
    if len(tokens) == 2 and tokens[0] == "HOME" and tokens[1] == "ALL":
        for name in sorted(channel_map.keys()):
            ch = channel_map[name]
            ok = ch.home()
            if not ok:
                print(f"ERR {name} HOME_FAILED")
                return
        _print_ok("OK HOME ALL")
        return

    if len(tokens) == 2 and tokens[1] == "HOME":
        ch_name = tokens[0]
        ch = channel_map.get(ch_name)
        if ch is None:
            print(f"ERR {ch_name} NOT_FOUND")
            return
        ok = ch.home()
        if ok:
            print(f"OK {ch_name} HOME")
        else:
            print(f"ERR {ch_name} HOME_FAILED")
        return

    _print_err("ERR HOME BAD_FORMAT")


def _handle_channel_move(tokens, channel_map):
    """
    Supported:
    - CHx ASP <ml>
    - CHx DISP <ml>
    """
    if len(tokens) != 3:
        _print_err("ERR MOVE BAD_FORMAT")
        return

    ch_name = tokens[0]
    action = tokens[1]
    value = _parse_float(tokens[2])

    if ch_name not in channel_map:
        print(f"ERR {ch_name} NOT_FOUND")
        return

    if value is None or value <= 0:
        print(f"ERR {ch_name} BAD_VOLUME")
        return

    ch = channel_map[ch_name]

    if action == "ASP":
        ch.aspirate_ml(value)
        print(f"OK {ch_name} ASP {value}")
        return

    if action == "DISP":
        ch.dispense_ml(value)
        print(f"OK {ch_name} DISP {value}")
        return

    print(f"ERR {ch_name} UNKNOWN_ACTION")


def _handle_pump_solution(tokens, channel_map):
    """
    Supported:
    - PUMP SOLUTION v1 v2 v3 v4 v5

    This is a macro-command that applies volumes to CH1..CH5.
    At this stage we implement a conservative behavior:
    - for each channel with volume > 0:
        dispense_ml(volume)
    The exact real mixing sequence (valves, aspirate->dispense, flushing)
    can be refined later once hardware routing is finalized.
    """
    if len(tokens) < 2 or tokens[0] != "PUMP" or tokens[1] != "SOLUTION":
        _print_err("ERR PUMP BAD_FORMAT")
        return

    # Expect 5 volumes after "PUMP SOLUTION"
    vols = []
    for s in tokens[2:]:
        v = _parse_float(s)
        if v is None:
            _print_err("ERR PUMP BAD_VOLUME")
            return
        vols.append(v)

    if len(vols) != 5:
        _print_err("ERR PUMP EXPECT_5_VOLUMES")
        return

    # Apply to CH1..CH5 in order
    for i in range(1, 6):
        name = f"CH{i}"
        ch = channel_map.get(name)
        if ch is None:
            # If channel is not present/enabled, we just skip it
            continue

        v = vols[i - 1]
        if v <= 0:
            continue

        # TODO: refine macro sequence when plumbing is finalized:
        # Example alternative:
        # ch.open_valve(); ch.aspirate_ml(v); ch.close_valve()
        # ch.open_valve(); ch.dispense_ml(v); ch.close_valve()
        ch.dispense_ml(v)

    _print_ok("OK PUMP SOLUTION")


def _dispatch_line(line, channel_map):
    """
    Parse one incoming line and execute a command.
    """
    line = line.strip()
    if not line:
        return

    # Allow comments
    if line.startswith("#"):
        return

    tokens = line.upper().split()

    # INIT / CHx INIT
    if tokens[0] == "INIT" or (len(tokens) >= 2 and tokens[1] == "INIT"):
        _handle_init(tokens, channel_map)
        return

    # HOME ALL / CHx HOME
    if tokens[0] == "HOME" or (len(tokens) >= 2 and tokens[1] == "HOME"):
        _handle_home(tokens, channel_map)
        return

    # CHx ASP/DISP <ml>
    if tokens[0].startswith("CH") and len(tokens) >= 2 and tokens[1] in ("ASP", "DISP"):
        _handle_channel_move(tokens, channel_map)
        return

    # PUMP SOLUTION ...
    if len(tokens) >= 2 and tokens[0] == "PUMP" and tokens[1] == "SOLUTION":
        _handle_pump_solution(tokens, channel_map)
        return

    _print_err(f'ERR UNKNOWN_CMD "{line}"')


def run(channels):
    """
    Serial control loop.

    Reads commands from stdin (USB-serial REPL) line-by-line.
    This is the simplest and most reliable approach for early integration.
    Later, if needed, we can switch to machine.UART for a dedicated UART port.
    """
    channel_map = _build_channel_map(channels)

    # Announce system readiness and available channels
    print("OK READY")
    _handle_init(["INIT"], channel_map)

    while True:
        try:
            # sys.stdin.readline() blocks until a full line is received
            line = sys.stdin.readline()
            if not line:
                # In some environments empty reads may happen; avoid busy loop
                time.sleep_ms(10)
                continue

            _dispatch_line(line, channel_map)

        except KeyboardInterrupt:
            print("OK STOP")
            return

        except Exception as e:
            # Never crash the control loop; report and continue
            print("ERR EXCEPTION", repr(e))
            time.sleep_ms(50)
