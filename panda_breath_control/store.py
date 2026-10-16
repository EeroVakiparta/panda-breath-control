"""Run log, filter wear, the auto-off timer state and keeping the PC awake."""
import datetime as dt
import json
import os
import subprocess
import sys

from . import config

LOG_HEADER = "time;event;target_c;chamber_c;duration_min"
TIME_FMT = "%Y-%m-%d %H:%M:%S"

# A run starts on one of these events and ends on one of the others.
RUN_START = ("on", "seen_on")
RUN_END = ("off", "seen_off", "app_close")


class RunLog:
    """Semicolon-separated CSV (opens directly in a European-locale Excel).

    Events: on / on:<material> (this app), off / off:timer, seen_on / seen_off
    (a change made on the heater itself or in another client), target,
    app_start, app_close, filter_changed, timer:<h>h, timer_cancelled.
    """

    def __init__(self, path, on_line=None):
        self.path = path
        self.on_since = None
        self.run_preset = None
        self.on_line = on_line
        if not os.path.exists(path):
            self._append(LOG_HEADER)

    def _append(self, line):
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except OSError:
            pass

    def write_line(self, line):
        self._append(line)
        if self.on_line:
            self.on_line(line)

    def tail(self, n=40):
        try:
            with open(self.path, encoding="utf-8") as f:
                rows = [r.rstrip("\n") for r in f if r.strip()]
        except OSError:
            return []
        return [r for r in rows if not r.startswith("time;")][-n:]

    def event(self, name, target=None, chamber=None, now=None):
        """Log an event. Returns (minutes, material) when it ended a run."""
        now = now or dt.datetime.now()
        dur, ended = "", None
        base = name.split(":")[0]
        if base in RUN_START:
            if self.on_since is None:
                self.on_since = now
                self.run_preset = name.split(":")[1] if ":" in name else None
            elif ":" in name:
                self.run_preset = name.split(":")[1]
        elif base in RUN_END and self.on_since is not None:
            minutes = (now - self.on_since).total_seconds() / 60
            dur = str(round(minutes))
            ended = (minutes, self.run_preset)
            self.on_since = None
            self.run_preset = None
        self.write_line("%s;%s;%s;%s;%s" % (
            now.strftime(TIME_FMT), name,
            "" if target is None else target, "" if chamber is None else chamber, dur))
        return ended

    def pending(self, now=None):
        """(minutes, material) of the run in progress, or None."""
        if self.on_since is None:
            return None
        now = now or dt.datetime.now()
        return ((now - self.on_since).total_seconds() / 60, self.run_preset)

    def runs_since(self, since):
        """Finished runs after `since` as [(minutes, material)]."""
        runs, start, preset = [], None, None
        try:
            with open(self.path, encoding="utf-8") as f:
                rows = [r.rstrip("\n").split(";") for r in f if r.strip()]
        except OSError:
            return runs
        for row in rows:
            if len(row) < 2:
                continue
            try:
                when = dt.datetime.strptime(row[0], TIME_FMT)
            except ValueError:
                continue  # header or a damaged line
            ev = row[1]
            base = ev.split(":")[0]
            if base in RUN_START:
                if start is None:
                    start, preset = when, (ev.split(":")[1] if ":" in ev else None)
                elif ":" in ev:
                    preset = ev.split(":")[1]
            elif base in RUN_END or base == "filter_changed":
                if start is not None and base != "filter_changed":
                    s0 = max(start, since)
                    if when > s0:
                        runs.append(((when - s0).total_seconds() / 60, preset))
                start, preset = None, None
        return runs


class FilterState:
    """HEPA + carbon filter wear: weighted hours from the log plus calendar age.

    filter.json stores only the change date; the hours are recomputed from the
    log every time, so closing the app mid-run or trimming the log loses nothing.
    """

    def __init__(self, path, log):
        self.path = path
        self.log = log
        self.changed_at = dt.datetime.now().replace(microsecond=0)
        self.load()

    def load(self):
        try:
            with open(self.path, encoding="utf-8") as f:
                self.changed_at = dt.datetime.fromisoformat(json.load(f)["changed_at"])
        except (OSError, ValueError, KeyError, TypeError):
            self.save()

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump({"changed_at": self.changed_at.isoformat(timespec="seconds")}, f, indent=2)
        except OSError:
            pass

    def reset(self):
        self.changed_at = dt.datetime.now().replace(microsecond=0)
        self.save()

    def health(self, pending=None, now=None):
        now = now or dt.datetime.now()
        runs = self.log.runs_since(self.changed_at)
        if pending:
            runs.append(pending)
        raw_h = sum(m for m, _ in runs) / 60
        weighted_h = sum(m * config.filter_weight(p) for m, p in runs) / 60
        days = (now - self.changed_at).total_seconds() / 86400
        used = max(weighted_h / config.FILTER_HOURS, days / config.FILTER_DAYS)
        pct = max(0, min(100, round(100 * (1 - used))))
        return {"pct": pct, "weighted_h": weighted_h, "raw_h": raw_h, "days": days}


class TimerStore:
    """The armed auto-off deadline, as wall-clock time in timer.json.

    Wall-clock (not monotonic) on purpose: a deadline that passed while the PC
    slept or the app was closed must still switch the heater off on resume.
    """

    def __init__(self, path):
        self.path = path

    def load(self):
        try:
            with open(self.path, encoding="utf-8") as f:
                return dt.datetime.fromisoformat(json.load(f)["off_at"])
        except (OSError, ValueError, KeyError, TypeError):
            return None

    def save(self, off_at):
        try:
            if off_at is None:
                if os.path.exists(self.path):
                    os.remove(self.path)
            else:
                with open(self.path, "w", encoding="utf-8") as f:
                    json.dump({"off_at": off_at.isoformat(timespec="seconds")}, f, indent=2)
        except OSError:
            pass


class KeepAwake:
    """Stops the computer from sleeping while a timer is armed.

    The display may still turn off. Windows: SetThreadExecutionState (call from
    the UI thread). macOS: caffeinate. Linux: systemd-inhibit. Anything else:
    no-op, which the README points out.
    """

    def __init__(self):
        self.proc = None
        self.active = False

    def set(self, on):
        if on == self.active:
            return
        self.active = on
        if sys.platform == "win32":
            try:
                import ctypes
                ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001
                ctypes.windll.kernel32.SetThreadExecutionState(
                    ES_CONTINUOUS | (ES_SYSTEM_REQUIRED if on else 0))
            except (AttributeError, OSError):
                pass
            return
        if on:
            if sys.platform == "darwin":
                cmd = ["caffeinate", "-i", "-w", str(os.getpid())]
            else:
                cmd = ["systemd-inhibit", "--what=idle:sleep", "--who=" + config.APP_NAME,
                       "--why=Auto-off timer armed", "sleep", "infinity"]
            try:
                self.proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except OSError:
                self.proc = None
        elif self.proc is not None:
            self.proc.terminate()
            self.proc = None
