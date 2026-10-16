"""Talking to the heater: its WebSocket JSON protocol, plus a simulated heater.

The Panda Breath has no REST API. Its web UI is a single page that talks to
ws://<host>/ws. On connect the heater sends one full state dump, then a
{"settings": {"warehouse_temper": N}} frame about once a second. Commands are
{"settings": {<key>: <value>}}; there is no reply. See docs/PROTOCOL.md.
"""
import asyncio
import json
import queue
import random
import threading
import time

import websockets

# The heater never pushes setting changes (its own buttons, the stock web UI,
# another client) to connected clients. Reconnecting is the only way to read
# them, so the client starts a fresh connection this often.
REFRESH_S = 30


class Client(threading.Thread):
    """WebSocket connection in its own thread; state goes to the UI via `inbox`.

    Inbox items: ("conn", True) / ("conn", False, reason) / ("state", {...}).
    """

    def __init__(self, inbox: queue.Queue, host: str):
        super().__init__(daemon=True)
        self.inbox = inbox
        self.host = host
        self.loop = None
        self.outbox = None
        self.ws = None

    @property
    def url(self):
        return f"ws://{self.host}/ws"

    def send(self, **settings):
        if self.loop and self.outbox:
            self.loop.call_soon_threadsafe(self.outbox.put_nowait, {"settings": settings})

    def set_host(self, host):
        """Switch to another address; the current connection is dropped."""
        self.host = host
        if self.loop and self.ws is not None:
            ws = self.ws
            self.loop.call_soon_threadsafe(lambda: asyncio.ensure_future(ws.close()))

    def run(self):
        asyncio.run(self.main())

    async def main(self):
        self.loop = asyncio.get_running_loop()
        self.outbox = asyncio.Queue()
        while True:
            try:
                async with websockets.connect(self.url, open_timeout=5, ping_interval=None) as ws:
                    self.ws = ws
                    self.inbox.put(("conn", True))
                    pump = asyncio.create_task(self.pump(ws))
                    started = self.loop.time()
                    try:
                        async for raw in ws:
                            try:
                                data = json.loads(raw)
                            except ValueError:
                                continue
                            if isinstance(data, dict) and isinstance(data.get("settings"), dict):
                                self.inbox.put(("state", data["settings"]))
                            if self.loop.time() - started > REFRESH_S:
                                break
                    finally:
                        pump.cancel()
                        self.ws = None
                    continue
            except Exception as exc:  # network down, heater off, DNS failure...
                self.ws = None
                self.inbox.put(("conn", False, str(exc)))
            await asyncio.sleep(3)

    async def pump(self, ws):
        while True:
            msg = await self.outbox.get()
            await ws.send(json.dumps(msg))


class DemoClient(threading.Thread):
    """A simulated heater for trying the app (and taking screenshots) without one.

    Same interface as Client. The chamber warms about 1 C every 8 s towards
    the target while on and cools towards 23 C while off.
    """

    AMBIENT = 23.0

    def __init__(self, inbox: queue.Queue, host: str = "demo"):
        super().__init__(daemon=True)
        self.inbox = inbox
        self.host = host
        self.lock = threading.Lock()
        self.state = {"work_on": False, "work_mode": 2, "set_temp": 45}
        self.chamber = self.AMBIENT

    def send(self, **settings):
        with self.lock:
            for key, value in settings.items():
                if key == "work_on" and not isinstance(value, bool):
                    continue  # the real firmware ignores 1/0 too
                self.state[key] = value

    def set_host(self, host):
        self.host = host

    def run(self):
        self.inbox.put(("conn", True))
        last_dump = 0.0
        while True:
            with self.lock:
                on = self.state["work_on"]
                goal = float(self.state["set_temp"]) if on else self.AMBIENT
                step = 0.125 if on else 0.05
                if abs(self.chamber - goal) > step:
                    self.chamber += step if goal > self.chamber else -step
                reading = int(round(self.chamber + random.choice((0, 0, 0.4, -0.4))))
                if time.monotonic() - last_dump > REFRESH_S or last_dump == 0.0:
                    self.inbox.put(("state", dict(self.state, warehouse_temper=reading)))
                    last_dump = time.monotonic()
                else:
                    self.inbox.put(("state", {"warehouse_temper": reading}))
            time.sleep(1)
