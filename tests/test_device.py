"""The WebSocket client against a fake heater on localhost."""
import asyncio
import json
import queue
import threading
import time
import unittest

import websockets

from panda_breath_control.device import Client, DemoClient


class FakeHeater:
    def __init__(self):
        self.state = {"work_on": False, "work_mode": 2, "set_temp": 40}
        self.received = []
        self.port = None
        self.ready = threading.Event()
        threading.Thread(target=lambda: asyncio.run(self.serve()), daemon=True).start()
        self.ready.wait(5)

    async def handler(self, ws):
        await ws.send(json.dumps({"settings": dict(self.state, warehouse_temper=25)}))
        async for raw in ws:
            settings = json.loads(raw)["settings"]
            self.received.append(settings)
            if "work_on" in settings and isinstance(settings["work_on"], bool):
                self.state.update(settings)

    async def serve(self):
        async with websockets.serve(self.handler, "127.0.0.1", 0) as server:
            self.port = server.sockets[0].getsockname()[1]
            self.ready.set()
            await asyncio.Future()


def wait_for(pred, timeout=5):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if pred():
            return True
        time.sleep(0.05)
    return False


class ClientTest(unittest.TestCase):
    def test_state_and_commands(self):
        heater = FakeHeater()
        inbox = queue.Queue()
        client = Client(inbox, f"127.0.0.1:{heater.port}")
        client.start()
        first = inbox.get(timeout=5)
        self.assertEqual(first, ("conn", True))
        kind, state = inbox.get(timeout=5)
        self.assertEqual(kind, "state")
        self.assertEqual(state["set_temp"], 40)
        client.send(work_on=True)
        self.assertTrue(wait_for(lambda: heater.state["work_on"] is True))
        self.assertEqual(heater.received[-1], {"work_on": True})

    def test_unreachable_host_reports_disconnected(self):
        inbox = queue.Queue()
        Client(inbox, "127.0.0.1:1").start()
        item = inbox.get(timeout=10)
        self.assertEqual(item[0], "conn")
        self.assertFalse(item[1])


class DemoTest(unittest.TestCase):
    def test_demo_ignores_numeric_work_on_like_the_firmware(self):
        demo = DemoClient(queue.Queue())
        demo.send(work_on=1)
        self.assertFalse(demo.state["work_on"])
        demo.send(work_on=True, set_temp=50)
        self.assertTrue(demo.state["work_on"])
        self.assertEqual(demo.state["set_temp"], 50)


if __name__ == "__main__":
    unittest.main()
