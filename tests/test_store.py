import datetime as dt
import os
import tempfile
import unittest

from panda_breath_control import config
from panda_breath_control.store import FilterState, RunLog, TimerStore

T0 = dt.datetime(2026, 10, 1, 12, 0, 0)


class RunLogTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "log.csv")
        self.log = RunLog(self.path)

    def tearDown(self):
        self.dir.cleanup()

    def test_run_duration_and_material(self):
        self.log.event("on:ASA", 60, 25, now=T0)
        ended = self.log.event("off", 60, 58, now=T0 + dt.timedelta(minutes=90))
        self.assertEqual(ended, (90.0, "ASA"))
        runs = self.log.runs_since(T0 - dt.timedelta(days=1))
        self.assertEqual(runs, [(90.0, "ASA")])

    def test_timer_off_ends_a_run(self):
        self.log.event("on", 45, now=T0)
        self.log.event("timer:2h", now=T0)
        self.log.event("off:timer", now=T0 + dt.timedelta(hours=2))
        self.assertEqual(self.log.runs_since(T0), [(120.0, None)])

    def test_runs_are_clipped_to_the_filter_change(self):
        self.log.event("seen_on", now=T0)
        self.log.event("filter_changed", now=T0 + dt.timedelta(minutes=30))
        self.log.event("on:PC", now=T0 + dt.timedelta(minutes=40))
        self.log.event("app_close", now=T0 + dt.timedelta(minutes=100))
        runs = self.log.runs_since(T0 + dt.timedelta(minutes=30))
        self.assertEqual(runs, [(60.0, "PC")])

    def test_header_written_once(self):
        RunLog(self.path)
        with open(self.path, encoding="utf-8") as f:
            self.assertEqual(f.read().count("time;event"), 1)


class FilterTest(unittest.TestCase):
    def test_weighted_hours_and_calendar(self):
        with tempfile.TemporaryDirectory() as d:
            log = RunLog(os.path.join(d, "log.csv"))
            fs = FilterState(os.path.join(d, "filter.json"), log)
            fs.changed_at = T0
            log.event("on:ASA", now=T0)
            log.event("off", now=T0 + dt.timedelta(hours=10))
            h = fs.health(now=T0 + dt.timedelta(hours=10))
            self.assertAlmostEqual(h["raw_h"], 10)
            self.assertAlmostEqual(h["weighted_h"], 10 * config.MATERIALS["ASA"]["weight"])
            self.assertEqual(h["pct"], 99)
            old = fs.health(now=T0 + dt.timedelta(days=config.FILTER_DAYS))
            self.assertEqual(old["pct"], 0)


class TimerStoreTest(unittest.TestCase):
    def test_save_load_clear(self):
        with tempfile.TemporaryDirectory() as d:
            ts = TimerStore(os.path.join(d, "timer.json"))
            self.assertIsNone(ts.load())
            ts.save(T0)
            self.assertEqual(ts.load(), T0)
            ts.save(None)
            self.assertIsNone(ts.load())
            self.assertFalse(os.path.exists(os.path.join(d, "timer.json")))


if __name__ == "__main__":
    unittest.main()
