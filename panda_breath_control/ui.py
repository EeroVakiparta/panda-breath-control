"""The tkinter window."""
import collections
import datetime as dt
import math
import os
import queue
import sys
import time
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, ttk

from . import __version__, config, i18n
from .device import Client, DemoClient
from .i18n import t
from .store import FilterState, KeepAwake, RunLog, TimerStore

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def ui_family():
    """A font that covers the current language (CJK needs its own on Windows)."""
    if i18n.language() == "zh" and sys.platform == "win32":
        return "Microsoft YaHei UI"
    if sys.platform == "win32":
        return "Segoe UI"
    return tkfont.nametofont("TkDefaultFont").actual()["family"]


# ---------------------------------------------------------------------------
# Status panel: the panda and the trend line
# ---------------------------------------------------------------------------
INK = "#2b2b30"
MUTED = "#86868c"
GRID = "#e2e2e6"
STALE = "#bdbdc2"
OFF = "#a4a4aa"
BLUE = "#3d85c3"
HEAT = "#e0702a"
HEAT_HI = "#f4a447"
BLUSH = "#ff8ea2"
BLUSH_LITE = "#ffd0d9"


class StatusPanel(tk.Canvas):
    """The middle of the window: a panda that shows the state, and a trend line.

    The panda sleeps when the heater is off, breathes calmly while it only
    filters (on and at the target), and puffs red cheeks while heating. Below
    it: the chamber reading, the target, and the readings of the last 30
    minutes against the target. The end of the line pulses with every reading;
    with no fresh data everything turns grey.
    """

    W, H = 240, 322
    WINDOW_S = 30 * 60
    COLUMNS = 98
    L, R, T, B = 22, 218, 186, 290

    def __init__(self, master, history, cap):
        bg = ttk.Style(master).lookup("TFrame", "background") or "#f0f0f0"
        super().__init__(master, width=self.W, height=self.H, highlightthickness=0, bg=bg)
        self.bg = bg
        self.history = history   # deque of (time.monotonic(), °C), owned by the App
        self.cap = cap
        self.on = False
        self.heating = False
        self.current = None
        self.target = None
        self.age = None
        self.stale = True
        self.flash = 0.0
        self.t0 = time.monotonic()
        self.after(60, self.tick)

    # --- inputs from the App --------------------------------------------------
    def set_state(self, on, heating):
        self.on, self.heating = bool(on), bool(heating)

    def set_reading(self, current, target):
        self.current, self.target = current, target

    def set_fresh(self, age, connected):
        """age = seconds since the last reading (None = none yet)."""
        self.age = age
        self.stale = age is None or not connected or age > 4
        self.flash = 0.0 if self.stale else max(0.0, 1 - age / 0.35)

    # --- drawing ------------------------------------------------------------------
    def state_color(self):
        if self.stale:
            return STALE
        if not self.on:
            return OFF
        return HEAT if self.heating else BLUE

    def status_text(self):
        if self.stale:
            return t("panel_stale", s="--" if self.age is None else f"{self.age:.0f}")
        if not self.on:
            return t("panel_off")
        return t("panel_heating") if self.heating else t("panel_filtering")

    def tick(self):
        try:
            self.redraw(time.monotonic() - self.t0)
        except tk.TclError:
            return  # the window is closing
        self.after(60, self.tick)

    def redraw(self, now_s):
        self.delete("all")
        self.draw_panda(120, 74, 0.62, now_s)
        self.draw_numbers()
        self.draw_trend()

    def oval(self, x, y, rx, ry, fill, outline="", width=0):
        self.create_oval(x - rx, y - ry, x + rx, y + ry, fill=fill, outline=outline, width=width)

    def draw_panda(self, cx, cy, k, now_s):
        grey = self.stale
        ink = "#a6a6ac" if grey else INK
        white = "#ffffff"
        puff, eyes, blush = 1.0, "open", None
        if not self.on:
            eyes = "sleep"
        elif self.heating:
            puff = 1.12 + 0.025 * math.sin(now_s * math.pi * 2 / 1.3)
            eyes, blush = "squeeze", BLUSH
        else:
            puff = 1.0 + 0.035 * math.sin(now_s * math.pi * 2 / 4)
            blush = BLUSH_LITE
        if grey:
            puff, blush = 1.0, None
        o = max(2.0, 4 * k)                       # outline thickness
        line_w = max(2, round(3.5 * k))
        cheeks = ((cx - 38 * k, cy + 28 * k), (cx + 38 * k, cy + 28 * k))
        cr = 36 * k * puff

        self.oval(cx - 50 * k, cy - 56 * k, 23 * k, 23 * k, ink)    # ears
        self.oval(cx + 50 * k, cy - 56 * k, 23 * k, 23 * k, ink)
        self.oval(cx, cy, 72 * k, 60 * k, ink)                       # outline
        for x, y in cheeks:
            self.oval(x, y, cr + o, cr * 0.88 + o, ink)
        self.oval(cx, cy, 72 * k - o, 60 * k - o, white)             # face
        for x, y in cheeks:
            self.oval(x, y, cr, cr * 0.88, white)
        if blush:
            for sx in (-1, 1):
                self.oval(cx + sx * 44 * k, cy + 36 * k, 14 * k * puff, 8 * k * puff, blush)
        for sx in (-1, 1):                                           # eye patches
            self.oval(cx + sx * 26 * k, cy - 8 * k, 16 * k, 21 * k, ink)
        if eyes == "open":
            for sx in (-1, 1):
                self.oval(cx + sx * 25 * k, cy - 8 * k, 5.5 * k, 5.5 * k, white)
        elif eyes == "sleep":
            for sx in (-1, 1):
                ex, ey, r = cx + sx * 26 * k, cy - 10 * k, 7 * k
                self.create_arc(ex - r, ey - r, ex + r, ey + r, start=200, extent=140,
                                style=tk.ARC, outline=white, width=line_w)
        else:  # squeezed shut: > <
            for sx in (-1, 1):
                self.create_line(cx + sx * 32 * k, cy - 16 * k, cx + sx * 21 * k, cy - 8 * k,
                                 cx + sx * 32 * k, cy, fill=white, width=line_w,
                                 capstyle=tk.ROUND, joinstyle=tk.ROUND)
        self.oval(cx, cy + 14 * k, 9 * k, 6 * k, ink)                # nose
        mouth_w = max(2, round(2.5 * k))
        if self.on and self.heating and not grey:                    # lips pressed
            pts = []
            for i, dx in enumerate((-13, -6, 0, 6, 13)):
                pts += [cx + dx * k, cy + (30 if i % 2 == 0 else 27) * k]
            self.create_line(*pts, fill=ink, width=mouth_w, capstyle=tk.ROUND, joinstyle=tk.ROUND)
        elif self.on and not grey:                                   # small smile
            r = 8 * k
            self.create_arc(cx - r, cy + 22 * k - r, cx + r, cy + 22 * k + r, start=210, extent=120,
                            style=tk.ARC, outline=ink, width=mouth_w)
        else:
            self.create_line(cx - 7 * k, cy + 29 * k, cx + 7 * k, cy + 29 * k, fill=ink,
                             width=mouth_w, capstyle=tk.ROUND)
        if self.on and self.heating and not grey:                    # heat above the head
            for i in (-1, 0, 1):
                x0 = cx + i * 20 * k
                sway = math.sin(now_s * 4 + i) * 3 * k
                ys = [cy - (62 + 8 * j) * k for j in range(4)]
                pts = []
                for j, y in enumerate(ys):
                    pts += [x0 + (sway if j % 2 == 0 else 5 * k - sway), y]
                self.create_line(*pts, fill=HEAT_HI, width=max(2, round(3 * k)), smooth=True,
                                 capstyle=tk.ROUND)
        if grey:
            self.create_text(cx + 78 * k, cy - 52 * k, text="?", fill=MUTED,
                             font=(ui_family(), 15, "bold"))

    def draw_numbers(self):
        fam = ui_family()
        cur = "--" if self.current is None else f"{self.current}°"
        self.create_text(self.L, 152, text=cur, anchor="w", font=(fam, 28, "bold"),
                         fill=STALE if self.stale else INK)
        if self.target is not None:
            self.create_text(self.R, 141, text=t("panel_target", t=self.target), anchor="e",
                             font=(fam, 9), fill=MUTED)
        item = self.create_text(self.R, 162, text=self.status_text(), anchor="e",
                                font=(fam, 9, "bold" if not self.stale else "normal"),
                                fill=MUTED if self.stale else INK)
        x0 = self.bbox(item)[0]
        self.create_rectangle(x0 - 13, 158, x0 - 5, 166, fill=self.state_color(), outline="")

    def draw_trend(self):
        fam = ui_family()
        lo, hi = config.DEVICE_MIN_TEMP, self.cap + 5

        def yv(v):
            v = min(max(v, lo), hi)
            return self.B - (v - lo) / (hi - lo) * (self.B - self.T)

        for v in range(20, hi + 1, 10):
            self.create_line(self.L, yv(v), self.R, yv(v), fill=GRID)
        if self.target is not None:
            ty = yv(self.target)
            self.create_line(self.L, ty, self.R, ty, fill=MUTED, dash=(5, 4))
            self.create_text(self.R, ty - 8, text=str(self.target), anchor="e",
                             font=(fam, 8, "bold"), fill=INK)
        self.create_text(self.L, 306, text=t("panel_window"), anchor="w", font=(fam, 8), fill=MUTED)
        self.create_text(self.R, 306, text=t("panel_now"), anchor="e", font=(fam, 8), fill=MUTED)

        now = time.monotonic()
        span = self.WINDOW_S / self.COLUMNS
        sums, counts = [0.0] * self.COLUMNS, [0] * self.COLUMNS
        for ts, v in self.history:
            age = now - ts
            if age > self.WINDOW_S:
                continue
            col = self.COLUMNS - 1 - int(age / span)
            if 0 <= col < self.COLUMNS:
                sums[col] += v
                counts[col] += 1
        runs, run = [], []
        width = self.R - self.L - 8
        for c in range(self.COLUMNS):
            if counts[c]:
                run += [self.L + width * c / (self.COLUMNS - 1), yv(sums[c] / counts[c])]
            elif run:
                runs.append(run)
                run = []
        if run:
            runs.append(run)
        if not runs:
            return
        col = self.state_color()
        for r in runs:
            if len(r) >= 4:
                self.create_line(*r, fill=col, width=2, capstyle=tk.ROUND, joinstyle=tk.ROUND)
        ex, ey = runs[-1][-2], runs[-1][-1]
        if self.stale:
            self.oval(ex, ey, 4.5, 4.5, self.bg, outline=STALE, width=2)
        else:
            r = 4 + 3 * self.flash
            self.oval(ex, ey, r, r, col, outline=self.bg, width=2)


# ---------------------------------------------------------------------------
# Dialogs
# ---------------------------------------------------------------------------
class Disclaimer(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.accepted = False
        self.title(t("disclaimer_title"))
        self.resizable(False, False)
        self.transient(master)
        fam = ui_family()
        ttk.Label(self, text=t("disclaimer_title"), font=(fam, 13, "bold")).pack(
            anchor="w", padx=16, pady=(14, 6))
        ttk.Label(self, text=t("disclaimer"), wraplength=460, justify="left",
                  font=(fam, 10)).pack(padx=16)
        row = ttk.Frame(self)
        row.pack(fill="x", padx=16, pady=14)
        ttk.Button(row, text=t("quit"), command=self.destroy).pack(side="right")
        ttk.Button(row, text=t("accept"), command=self.accept).pack(side="right", padx=(0, 6))
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.grab_set()

    def accept(self):
        self.accepted = True
        self.destroy()


class SettingsDialog(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.title(t("settings_title"))
        self.resizable(False, False)
        self.transient(app)
        s = app.settings
        fam = ui_family()
        body = ttk.Frame(self)
        body.pack(padx=16, pady=12, fill="both")

        ttk.Label(body, text=t("set_host")).grid(row=0, column=0, sticky="w")
        self.host = tk.StringVar(value=s.get("host", config.DEFAULT_HOST))
        ttk.Entry(body, textvariable=self.host, width=34).grid(row=1, column=0, columnspan=2, sticky="ew")
        ttk.Label(body, text=t("set_host_hint"), foreground="#777", font=(fam, 8)).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(0, 8))

        ttk.Label(body, text=t("set_language")).grid(row=3, column=0, sticky="w")
        self.langs = [code for code, _ in i18n.LANGUAGES]
        self.lang = ttk.Combobox(body, state="readonly", width=32,
                                 values=[name for _, name in i18n.LANGUAGES])
        self.lang.current(self.langs.index(i18n.language()))
        self.lang.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        ttk.Label(body, text=t("set_printer")).grid(row=5, column=0, sticky="w")
        self.profiles = list(config.PROFILE_ORDER)
        self.printer = ttk.Combobox(body, state="readonly", width=32,
                                    values=[t("profile_" + p) for p in self.profiles])
        self.printer.current(self.profiles.index(s.get("printer", "generic")))
        self.printer.grid(row=6, column=0, columnspan=2, sticky="ew")
        self.printer.bind("<<ComboboxSelected>>", lambda e: self.refresh())
        self.note = ttk.Label(body, wraplength=300, justify="left", foreground="#555", font=(fam, 9))
        self.note.grid(row=7, column=0, columnspan=2, sticky="w", pady=(4, 8))

        ttk.Label(body, text=t("set_ceiling")).grid(row=8, column=0, sticky="w")
        self.ceiling = tk.StringVar(value=str(config.profile_ceiling(s)))
        self.ceiling_box = ttk.Spinbox(body, from_=config.DEVICE_MIN_TEMP, to=config.DEVICE_MAX_TEMP,
                                       increment=config.STEP, textvariable=self.ceiling, width=6)
        self.ceiling_box.grid(row=8, column=1, sticky="e")

        row = ttk.Frame(self)
        row.pack(fill="x", padx=16, pady=(0, 12))
        ttk.Button(row, text=t("cancel"), command=self.destroy).pack(side="right")
        ttk.Button(row, text=t("save"), command=self.save).pack(side="right", padx=(0, 6))
        self.refresh()
        self.grab_set()

    def selected_profile(self):
        return self.profiles[self.printer.current()]

    def refresh(self):
        key = self.selected_profile()
        self.note.configure(text=t("note_" + key))
        if key == "custom":
            self.ceiling_box.state(["!disabled"])
            self.ceiling.set(str(self.app.settings.get("custom_ceiling", 50)))
        else:
            self.ceiling_box.state(["disabled"])
            self.ceiling.set(str(config.PROFILES[key]["ceiling"]))

    def save(self):
        s = dict(self.app.settings)
        s["host"] = self.host.get().strip() or config.DEFAULT_HOST
        s["language"] = self.langs[self.lang.current()]
        s["printer"] = self.selected_profile()
        if s["printer"] == "custom":
            try:
                c = int(float(self.ceiling.get()))
            except ValueError:
                c = 50
            s["custom_ceiling"] = max(config.DEVICE_MIN_TEMP, min(config.DEVICE_MAX_TEMP, c))
        self.destroy()
        self.app.apply_settings(s)


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------
class App(tk.Tk):
    def __init__(self, demo=False, paths=None):
        super().__init__()
        self.withdraw()
        self.demo = demo
        self.paths = paths or config.Paths(os.path.join(config.data_dir(), "demo") if demo else None)
        self.settings = config.load_settings(self.paths)
        if not self.settings.get("language"):
            self.settings["language"] = i18n.system_language()
            config.save_settings(self.paths, self.settings)
        i18n.set_language(self.settings["language"])
        self.title(config.APP_NAME + (" (demo)" if demo else ""))
        self.resizable(False, False)
        self.set_app_icon()

        self.inbox = queue.Queue()
        self.host = "demo" if demo else config.effective_host(self.settings)
        self.client = (DemoClient if demo else Client)(self.inbox, self.host)
        self.state_ = {}
        self._sliding = False
        self.last_frame = None      # time.monotonic() of the last chamber reading
        self.connected = False
        self.awake = KeepAwake()
        self.timer_store = TimerStore(self.paths.timer)
        self.timer_at = None        # datetime the heater gets switched off
        self.timer_fired = False    # deadline passed: keep sending off until confirmed
        self.target = tk.IntVar(value=min(45, self.ceiling()))
        self.readings = collections.deque()  # (time.monotonic(), °C), for the trend line

        self.log = RunLog(self.paths.log, on_line=self.feed_line)
        self.filter = FilterState(self.paths.filter, self.log)
        self.build_ui()
        self.log.event("app_start")
        self.timer_load()

        if not self.settings.get("disclaimer_accepted"):
            self.deiconify()
            dlg = Disclaimer(self)
            self.wait_window(dlg)
            if not dlg.accepted:
                self.after(0, self.destroy)
                return
            self.settings["disclaimer_accepted"] = True
            config.save_settings(self.paths, self.settings)
        self.deiconify()
        self.after(0, self.set_taskbar_icon)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.client.start()
        self.after(200, self.poll)
        self.after(250, self.update_freshness)
        self.after(30000, self.update_filter_periodic)
        self.after(1000, self.timer_tick)

    def ceiling(self):
        return config.profile_ceiling(self.settings)

    def set_app_icon(self):
        try:
            self.iconbitmap(os.path.join(ASSETS, "icon.ico"))
        except tk.TclError:  # not Windows
            try:
                self._icon_img = tk.PhotoImage(file=os.path.join(ASSETS, "icon-64.png"))
                self.iconphoto(True, self._icon_img)
            except tk.TclError:
                pass

    def set_taskbar_icon(self):
        """Hand Windows the icon frames at the sizes it draws them.

        Tk passes only 16 and 32 px icons, and the Windows 11 taskbar shrinks
        the 32 px one to 24 px with a jagged result. The .ico has a frame
        drawn for each size, so load the exact ones and set them directly.
        """
        if sys.platform != "win32":
            return
        try:
            import ctypes
            from ctypes import wintypes
            user32 = ctypes.windll.user32
            user32.LoadImageW.restype = ctypes.c_void_p
            user32.LoadImageW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT,
                                          ctypes.c_int, ctypes.c_int, wintypes.UINT]
            user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, ctypes.c_void_p]
            scale = user32.GetDpiForSystem() / 96 if hasattr(user32, "GetDpiForSystem") else 1.0
            win11 = sys.getwindowsversion().build >= 22000
            big = round((24 if win11 else 32) * scale)
            small = round(16 * scale)
            hwnd = int(self.wm_frame(), 16)
            path = os.path.join(ASSETS, "icon.ico")
            IMAGE_ICON, LR_LOADFROMFILE, WM_SETICON = 1, 0x10, 0x80
            for which, size in ((1, big), (0, small)):  # ICON_BIG, ICON_SMALL
                handle = user32.LoadImageW(None, path, IMAGE_ICON, size, size, LR_LOADFROMFILE)
                if handle:
                    user32.SendMessageW(hwnd, WM_SETICON, which, handle)
        except (AttributeError, OSError, ValueError, tk.TclError):
            pass

    # --- layout ---------------------------------------------------------------
    def build_ui(self):
        """Builds every widget. Called again after a language or printer change."""
        for w in self.winfo_children():
            if not isinstance(w, tk.Toplevel):
                w.destroy()
        fam = ui_family()
        style = ttk.Style(self)
        for name in ("TLabel", "TButton", "TLabelframe.Label", "TCombobox", "TEntry", "TSpinbox"):
            style.configure(name, font=(fam, 9))
        style.configure("Status.TLabel", font=(fam, 11))
        style.configure("On.TButton", font=(fam, 11, "bold"))
        style.configure("Preset.TButton", font=(fam, 10))
        style.configure("Filter.Horizontal.TProgressbar", thickness=14)

        top = ttk.Frame(self)
        top.grid(row=0, column=0, columnspan=3, sticky="ew", padx=12, pady=(10, 0))
        self.status_var = tk.StringVar(value=t("connecting"))
        ttk.Label(top, textvariable=self.status_var, style="Status.TLabel").pack(side="left")
        ttk.Button(top, text=t("settings"), command=lambda: SettingsDialog(self)).pack(side="right")
        ttk.Label(top, text="%s · %s" % (t("profile_" + self.settings["printer"]),
                                         t("ceiling_label", ceiling=self.ceiling())),
                  foreground="#777").pack(side="right", padx=8)

        # left: presets, target slider, on/off, timer
        left = ttk.Frame(self)
        left.grid(row=1, column=0, sticky="n", padx=(12, 6), pady=8)
        box = ttk.LabelFrame(left, text=t("materials"))
        box.pack(fill="x")
        presets = config.profile_presets(self.settings)
        for i, (name, temp) in enumerate(presets):
            ttk.Button(box, text=f"{name}\n{temp} °C", style="Preset.TButton", width=9,
                       command=lambda n=name, tp=temp: self.turn_on(tp, n)
                       ).grid(row=i // 2, column=i % 2, sticky="ew", padx=3, pady=3)
        for c in range(2):
            box.columnconfigure(c, weight=1)
        ttk.Label(box, text=t("no_heat", materials=" · ".join(config.profile_no_heat(self.settings))),
                  foreground="#777").grid(row=(len(presets) + 1) // 2, column=0, columnspan=2, pady=(2, 4))

        tbox = ttk.LabelFrame(left, text=t("target"))
        tbox.pack(fill="x", pady=(8, 0))
        ceiling = self.ceiling()
        self.scale = ttk.Scale(tbox, from_=config.DEVICE_MIN_TEMP, to=ceiling, orient="horizontal",
                               length=210, command=self.on_slide)
        self.scale.set(min(self.target.get(), ceiling))
        self.scale.pack(padx=6)
        self.scale.bind("<ButtonRelease-1>", lambda e: self.slide_done())
        ticks = ttk.Frame(tbox)
        ticks.pack(fill="x", padx=6, pady=(0, 4))
        tick_vals = list(range(config.DEVICE_MIN_TEMP, ceiling + 1, config.STEP * 2))
        if tick_vals[-1] != ceiling:
            tick_vals.append(ceiling)
        for i, v in enumerate(tick_vals):
            anchor = "w" if i == 0 else ("e" if i == len(tick_vals) - 1 else "center")
            ttk.Label(ticks, text=str(v), foreground="#777", font=(fam, 8),
                      anchor=anchor).grid(row=0, column=i, sticky="ew")
            ticks.columnconfigure(i, weight=1)

        btns = ttk.Frame(left)
        btns.pack(fill="x", pady=(10, 0))
        ttk.Button(btns, text=t("on"), style="On.TButton", command=self.turn_on).pack(
            side="left", expand=True, fill="x", padx=(0, 3))
        ttk.Button(btns, text=t("off"), command=self.turn_off).pack(
            side="left", expand=True, fill="x", padx=(3, 0))

        abox = ttk.LabelFrame(left, text=t("timer"))
        abox.pack(fill="x", pady=(10, 0))
        arow = ttk.Frame(abox)
        arow.pack(padx=6, pady=(4, 2))
        if t("timer_pre"):
            ttk.Label(arow, text=t("timer_pre")).pack(side="left")
        old = getattr(self, "timer_h", None)
        self.timer_h = tk.StringVar(value=old.get() if old else "12")
        ttk.Combobox(arow, textvariable=self.timer_h, width=5,
                     values=[str(h) for h in config.TIMER_CHOICES_H]).pack(side="left", padx=4)
        ttk.Label(arow, text=t("timer_post")).pack(side="left")
        trow = ttk.Frame(abox)
        trow.pack(fill="x", padx=6, pady=2)
        ttk.Button(trow, text=t("timer_set"), command=self.timer_arm).pack(
            side="left", expand=True, fill="x", padx=(0, 3))
        ttk.Button(trow, text=t("timer_cancel"), command=self.timer_cancel).pack(
            side="left", expand=True, fill="x", padx=(3, 0))
        self.timer_var = tk.StringVar(value=t("timer_none"))
        ttk.Label(abox, textvariable=self.timer_var, font=(fam, 9), justify="center").pack(pady=(2, 4))
        ttk.Label(abox, text=t("timer_keep_open"), foreground="#777", font=(fam, 8),
                  justify="center").pack(pady=(0, 4))

        # middle: drawing + filter gauge
        mid = ttk.Frame(self)
        mid.grid(row=1, column=1, sticky="n", padx=6, pady=8)
        self.pic = StatusPanel(mid, self.readings, self.ceiling())
        self.pic.pack()
        fbox = ttk.LabelFrame(mid, text=t("filter"))
        fbox.pack(fill="x", pady=(6, 0))
        self.filter_bar = ttk.Progressbar(fbox, length=224, maximum=100,
                                          style="Filter.Horizontal.TProgressbar")
        self.filter_bar.pack(padx=6, pady=(6, 2))
        self.filter_var = tk.StringVar(value="")
        ttk.Label(fbox, textvariable=self.filter_var, font=(fam, 9), justify="center").pack()
        ttk.Button(fbox, text=t("filter_changed"), command=self.filter_changed).pack(pady=(4, 6))

        # right: log feed
        right = ttk.LabelFrame(self, text=t("log"))
        right.grid(row=1, column=2, sticky="ns", padx=(6, 12), pady=8)
        self.feed = tk.Text(right, width=37, height=22, font=("Consolas" if sys.platform == "win32"
                                                              else "TkFixedFont", 9),
                            state="disabled", relief="flat", bg="#fafafa", wrap="none")
        self.feed.pack(padx=4, pady=4, fill="both", expand=True)
        for line in self.log.tail(30):
            self.feed_line(line)

        self.conn_var = tk.StringVar(value="")
        bottom = ttk.Frame(self)
        bottom.grid(row=2, column=0, columnspan=3, sticky="ew", padx=12, pady=(0, 8))
        ttk.Label(bottom, textvariable=self.conn_var, foreground="#777").pack(side="left")
        ttk.Label(bottom, text="v" + __version__, foreground="#aaa").pack(side="right")

        self.update_filter()
        self.timer_show()
        self.render()

    def apply_settings(self, new):
        host_changed = new.get("host") != self.settings.get("host")
        self.settings = new
        config.save_settings(self.paths, new)
        i18n.set_language(new["language"])
        if self.target.get() > self.ceiling():
            self.target.set(self.ceiling())
            if self.state_.get("work_on"):
                self.apply_temp()  # never leave the heater above a lowered cap
        if host_changed and not self.demo:
            self.host = config.effective_host(new)
            self.connected = False
            self.state_.clear()
            self.client.set_host(self.host)
        self.build_ui()

    # --- auto-off timer -------------------------------------------------------
    def timer_load(self):
        at = self.timer_store.load()
        if at is None:
            return
        self.timer_at = at  # a deadline already in the past fires on the first tick
        self.awake.set(True)
        self.log.event("timer_resumed")
        self.timer_show()

    def timer_arm(self):
        try:
            hours = float(self.timer_h.get().replace(",", "."))
        except ValueError:
            hours = 0
        if not 0 < hours <= config.TIMER_MAX_H:
            messagebox.showerror(t("timer"), t("timer_bad_hours", max=config.TIMER_MAX_H), parent=self)
            return
        self.timer_at = dt.datetime.now().replace(microsecond=0) + dt.timedelta(hours=hours)
        self.timer_fired = False
        self.timer_store.save(self.timer_at)
        self.awake.set(True)
        self.log.event("timer:%gh" % hours, self.state_.get("set_temp"), self.state_.get("warehouse_temper"))
        self.timer_show()

    def timer_cancel(self, log=True):
        if self.timer_at is None:
            return
        self.timer_at = None
        self.timer_fired = False
        self.timer_store.save(None)
        self.awake.set(False)
        if log:
            self.log.event("timer_cancelled")
        self.timer_show()

    def timer_show(self):
        if self.timer_at is None:
            self.timer_var.set(t("timer_none"))
            return
        left = (self.timer_at - dt.datetime.now()).total_seconds()
        if left <= 0:
            self.timer_var.set(t("timer_firing") if self.connected else t("timer_waiting"))
            return
        h, m = int(left // 3600), int(left % 3600 // 60)
        day = "" if self.timer_at.date() == dt.date.today() else self.timer_at.strftime("%d.%m. ")
        self.timer_var.set(t("timer_at", when=f"{day}{self.timer_at:%H:%M}", h=h, m=f"{m:02d}"))

    def timer_tick(self):
        if self.timer_at is not None and dt.datetime.now() >= self.timer_at and not self.timer_fired:
            self.timer_fired = True
            self.client.send(work_on=False)
            self.state_["work_on"] = 0
            self.log.event("off:timer", self.state_.get("set_temp"), self.state_.get("warehouse_temper"))
            self.update_filter()
            self.render()
            # poll() confirms it: the next state dump from the heater either says
            # off (the timer clears) or still on (off is sent again).
        self.timer_show()
        self.after(1000, self.timer_tick)

    def update_freshness(self):
        age = None if self.last_frame is None else time.monotonic() - self.last_frame
        self.pic.set_fresh(age, self.connected)
        if age is None:
            txt = t("fresh_none")
        elif age < 2:
            txt = t("fresh_now")
        else:
            txt = t("fresh_age", s=f"{age:.0f}")
        if self.demo:
            head = t("conn_demo")
        else:
            head = t("conn_ok", host=self.host) if self.connected else t("conn_lost", host=self.host)
        self.conn_var.set(f"{head} · {txt}")
        self.after(250, self.update_freshness)

    # --- slider -------------------------------------------------------------------
    def on_slide(self, value):
        if self._sliding:
            return
        snap = int(round(float(value) / config.STEP) * config.STEP)
        snap = max(config.DEVICE_MIN_TEMP, min(self.ceiling(), snap))
        self._sliding = True
        self.scale.set(snap)
        self._sliding = False
        self.target.set(snap)
        if hasattr(self, "pic"):
            self.pic.set_reading(self.state_.get("warehouse_temper"), snap)

    def slide_done(self):
        if self.state_.get("work_on"):
            self.apply_temp()

    # --- actions --------------------------------------------------------------
    def turn_on(self, temp=None, preset=None):
        if temp is not None:
            self.on_slide(temp)
        if self.timer_fired:  # switched on by hand after the timer fired
            self.timer_cancel(log=False)
        tgt = min(self.target.get(), self.ceiling())
        self.client.send(work_mode=2)
        self.client.send(set_temp=tgt)
        self.client.send(work_on=True)  # the firmware accepts only a JSON boolean, not 1/0
        self.state_.update(work_mode=2, set_temp=tgt, work_on=1)
        self.log.event("on" if preset is None else f"on:{preset}", tgt, self.state_.get("warehouse_temper"))
        self.render()

    def turn_off(self):
        self.client.send(work_on=False)
        self.state_["work_on"] = 0
        self.log.event("off", self.state_.get("set_temp"), self.state_.get("warehouse_temper"))
        self.update_filter()
        self.timer_cancel()
        self.render()

    def apply_temp(self):
        tgt = min(self.target.get(), self.ceiling())
        self.client.send(set_temp=tgt)
        self.state_["set_temp"] = tgt
        self.log.event("target", tgt, self.state_.get("warehouse_temper"))
        self.render()

    def filter_changed(self):
        h = self.filter.health(self.log.pending())
        if not messagebox.askyesno(t("filter_changed"), t(
                "filter_reset_q", raw=f"{h['raw_h']:.0f}", weighted=f"{h['weighted_h']:.0f}",
                days=f"{h['days']:.0f}"), parent=self):
            return
        self.filter.reset()
        self.log.event("filter_changed")
        self.update_filter()

    def on_close(self):
        if self.timer_at is not None and not messagebox.askyesno(
                t("timer"), t("close_with_timer", when=f"{self.timer_at:%H:%M}"), parent=self):
            return
        self.awake.set(False)
        if self.log.on_since is not None:  # the heater stays on; close the run here
            self.log.event("app_close", self.state_.get("set_temp"), self.state_.get("warehouse_temper"))
        else:
            self.log.event("app_close")
        self.destroy()

    # --- view -----------------------------------------------------------------------
    def feed_line(self, line):
        if not hasattr(self, "feed") or not self.feed.winfo_exists():
            return
        parts = line.split(";")
        if len(parts) < 5:
            return
        when, ev, tgt, cham, dur = parts[:5]
        try:
            when = dt.datetime.strptime(when, "%Y-%m-%d %H:%M:%S").strftime("%d.%m %H:%M")
        except ValueError:
            pass
        extra = ""
        if tgt:
            extra += f" {tgt}°"
        if cham:
            extra += f" ({cham}°)"
        if dur:
            extra += f" {dur} min"
        self.feed.configure(state="normal")
        self.feed.insert("end", f"{when}  {i18n.event_label(ev)}{extra}\n")
        if int(self.feed.index("end-1c").split(".")[0]) > 200:
            self.feed.delete("1.0", "2.0")
        self.feed.see("end")
        self.feed.configure(state="disabled")

    def update_filter(self):
        h = self.filter.health(self.log.pending())
        self.filter_bar["value"] = h["pct"]
        verdict = t("verdict_replace") if h["pct"] <= 0 else (
            t("verdict_soon") if h["pct"] <= 15 else t("verdict_ok"))
        self.filter_var.set(t("filter_status", pct=h["pct"], verdict=verdict,
                              raw=f"{h['raw_h']:.0f}", weighted=f"{h['weighted_h']:.0f}",
                              budget=config.FILTER_HOURS, days=f"{h['days']:.0f}",
                              maxdays=config.FILTER_DAYS))

    def update_filter_periodic(self):
        self.update_filter()
        self.after(30000, self.update_filter_periodic)

    def poll(self):
        try:
            while True:
                item = self.inbox.get_nowait()
                if item[0] == "conn":
                    self.connected = bool(item[1])
                    if not self.connected:
                        self.state_.pop("warehouse_temper", None)
                        self.render()
                    continue
                s = item[1]
                if "warehouse_temper" in s:
                    self.last_frame = time.monotonic()
                    self.add_reading(s["warehouse_temper"])
                if "work_on" in s and self.timer_fired:
                    # the timer already switched off; the heater's own word decides
                    if s["work_on"]:
                        self.client.send(work_on=False)  # the message was lost: again
                        s = dict(s, work_on=0)
                    else:
                        self.timer_cancel(log=False)
                if "work_on" in s and ("work_on" not in self.state_
                                       or bool(s["work_on"]) != bool(self.state_["work_on"])):
                    # A change seen on the heater (startup, its buttons, the stock
                    # web UI). This app's own clicks are logged as on/off.
                    name = "seen_on" if s["work_on"] else "seen_off"
                    self.log.event(name, s.get("set_temp", self.state_.get("set_temp")),
                                   self.state_.get("warehouse_temper"))
                    self.update_filter()
                    if not s["work_on"] and "work_on" in self.state_:
                        self.timer_cancel()  # switched off on the heater itself
                self.state_.update(s)
                if "set_temp" in s:
                    try:
                        dev_t = int(s["set_temp"])
                    except (TypeError, ValueError):
                        dev_t = None
                    if dev_t is not None and dev_t != self.target.get():
                        self.on_slide(dev_t)  # the slider follows the heater
                self.render()
        except queue.Empty:
            pass
        self.after(300, self.poll)

    def add_reading(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            return
        now = time.monotonic()
        self.readings.append((now, value))
        while self.readings and now - self.readings[0][0] > StatusPanel.WINDOW_S + 60:
            self.readings.popleft()

    def render(self):
        s = self.state_
        temp = s.get("warehouse_temper")
        on = s.get("work_on")
        target = s.get("set_temp")
        heating = bool(on) and temp is not None and target is not None and temp < target
        self.pic.set_state(on, heating)
        self.pic.set_reading(temp, target if target is not None else self.target.get())
        if on is None:
            self.status_var.set(t("reading_state") if self.connected else t("connecting"))
        elif on:
            if s.get("work_mode") == 1:
                self.status_var.set(t("status_auto"))
            elif heating:
                self.status_var.set(t("status_heating"))
            else:
                self.status_var.set(t("status_at_target"))
        else:
            mode = s.get("work_mode")
            self.status_var.set(t("status_off", mode=t("mode_%s" % mode) if mode in (1, 2, 3)
                                  else t("mode_unknown")))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--version" in argv:
        print(config.APP_NAME, __version__)
        return 0
    app = App(demo="--demo" in argv)
    try:
        app.mainloop()
    except KeyboardInterrupt:
        pass
    return 0
