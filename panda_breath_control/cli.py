"""Command-line control, for scripts and quick checks.

    panda-breath status          current state and chamber reading
    panda-breath on [TEMP]       Forced On, optionally with a new target
    panda-breath off             switch off
    panda-breath temp TEMP       change the target

Uses the address and printer cap saved by the desktop app (settings.json);
PANDA_BREATH_HOST overrides the address. Not written to the app's run log.
"""
import asyncio
import json
import sys

import websockets

from . import config

MODES = {1: "Auto", 2: "Forced On", 3: "Drying"}


async def talk(url, make_commands):
    async with websockets.connect(url, open_timeout=5) as ws:
        first = json.loads(await ws.recv())  # full state dump on connect
        commands = make_commands(first.get("settings", {}))
        for cmd in commands:
            await ws.send(json.dumps({"settings": cmd}))
        chamber = None
        try:
            for _ in range(5):
                msg = json.loads(await asyncio.wait_for(ws.recv(), 3))
                s = msg.get("settings", {})
                if "warehouse_temper" in s:
                    chamber = s["warehouse_temper"]
                    break
        except asyncio.TimeoutError:
            pass
        return first.get("settings", {}), chamber, commands


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv else 2
    settings = config.load_settings(config.Paths())
    host = config.effective_host(settings)
    ceiling = config.profile_ceiling(settings)
    verb, *rest = argv
    cmds = []
    if verb == "on":
        cmds += [{"work_mode": 2}, {"work_on": True}]  # work_on must be a JSON boolean
    elif verb == "off":
        cmds.append({"work_on": False})
    elif verb == "temp" and not rest:
        print("temp needs a value")
        return 2
    elif verb not in ("status", "temp"):
        print(f"unknown command {verb!r}")
        return 2
    if rest and verb in ("on", "temp"):
        try:
            temp = int(rest[0])
        except ValueError:
            print(f"not a temperature: {rest[0]!r}")
            return 2
        if not config.DEVICE_MIN_TEMP <= temp <= ceiling:
            print(f"target must be {config.DEVICE_MIN_TEMP}..{ceiling} C "
                  f"(cap of the '{settings['printer']}' printer profile)")
            return 2
        cmds.insert(0, {"set_temp": temp})

    def make_commands(state):
        out = list(cmds)
        if verb == "on" and not rest:
            stored = state.get("set_temp")
            if isinstance(stored, int) and stored > ceiling:
                out.insert(0, {"set_temp": ceiling})  # never heat above the cap
        return out

    try:
        before, chamber, cmds = asyncio.run(talk(f"ws://{host}/ws", make_commands))
    except (OSError, asyncio.TimeoutError, websockets.WebSocketException) as exc:
        print(f"cannot reach the heater at {host}: {exc}")
        return 1
    if cmds:
        print("sent:", cmds)
    print("before: work_on=%s mode=%s target=%s C" % (
        before.get("work_on"), MODES.get(before.get("work_mode"), "?"), before.get("set_temp")))
    print("chamber now: %s C (the heater's own sensor, reads high)" % chamber)
    return 0


if __name__ == "__main__":
    sys.exit(main())
