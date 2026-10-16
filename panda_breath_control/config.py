"""Paths, settings and the printer / material presets."""
import json
import os
import sys

APP_NAME = "Panda Breath Control"
DEFAULT_HOST = "PandaBreath.local"  # the heater's factory hostname

# Hardware limits of the Panda Breath V1.x (BIQU spec sheet).
DEVICE_MIN_TEMP = 15
DEVICE_MAX_TEMP = 60
STEP = 5

TIMER_CHOICES_H = (2, 4, 6, 8, 12, 16, 24)
TIMER_MAX_H = 48

# Filter replacement: Bambu Lab's carbon-filter interval is 1440 print hours;
# BIQU says 3-6 months for the Panda Breath filter. Whichever runs out first.
FILTER_HOURS = 1440
FILTER_DAYS = 180

# Chamber targets per material. Values follow the chamber temperatures in the
# Bambu Lab system filament profiles that ship with Bambu Studio / OrcaSlicer
# (ABS, ASA, PC, PA and PPS families 60 C, PET-CF 50 C, PLA / PETG / TPU none).
# `weight` is how hard the material loads the HEPA + carbon filter relative to
# PETG (a judgement, not a measurement): ASA/ABS give off styrene, nylons give
# off caprolactam and ultrafine particles, CF grades shed fibre dust.
MATERIALS = {
    "PETG":    {"temp": None, "weight": 1.0},
    "PETG-CF": {"temp": None, "weight": 1.3},
    "PET-CF":  {"temp": 50, "weight": 1.5},
    "ABS":     {"temp": 60, "weight": 2.0},
    "ASA":     {"temp": 60, "weight": 2.0},
    "PC":      {"temp": 60, "weight": 1.5},
    "PA-CF":   {"temp": 60, "weight": 1.8},
    "PAHT-CF": {"temp": 60, "weight": 1.8},
    "PPS-CF":  {"temp": 60, "weight": 1.8},
}
NO_HEAT = ("PLA", "PETG", "TPU")

# Printer profiles. `ceiling` caps every target the app will send; `presets`
# lists (material, temp) and is clipped to the ceiling. A profile without its
# own presets uses DEFAULT_PRESETS.
DEFAULT_PRESETS = ("PET-CF", "ABS", "ASA", "PC", "PA-CF", "PPS-CF")

PROFILES = {
    "generic": {"ceiling": 50},
    "bambu": {"ceiling": 60},
    "voron": {"ceiling": 60},
    "ecc2": {
        # Elegoo's product pages give 45-60 C for ASA/PC/PET-CF/PAHT-CF and
        # 25-50 C for the PETG family. The ECC2 has no chamber heater of its own
        # and its motors, belts and electronics sit inside, so 55 C is the cap.
        "ceiling": 55,
        "presets": (("PETG", 35), ("PETG-CF", 40), ("PET-CF", 50),
                    ("ASA", 55), ("PC", 55), ("PAHT-CF", 55)),
        "no_heat": ("PLA", "TPU"),
    },
    "custom": {"ceiling": None},  # ceiling comes from settings["custom_ceiling"]
}
PROFILE_ORDER = ("generic", "bambu", "voron", "ecc2", "custom")


def profile_ceiling(settings):
    key = settings.get("printer", "generic")
    ceiling = PROFILES.get(key, PROFILES["generic"])["ceiling"]
    if ceiling is None:
        ceiling = settings.get("custom_ceiling", 50)
    return max(DEVICE_MIN_TEMP, min(DEVICE_MAX_TEMP, int(ceiling)))


def profile_presets(settings):
    """[(material, temp)] for the selected printer, clipped to its ceiling."""
    prof = PROFILES.get(settings.get("printer", "generic"), PROFILES["generic"])
    ceiling = profile_ceiling(settings)
    pairs = prof.get("presets") or [(m, MATERIALS[m]["temp"]) for m in DEFAULT_PRESETS]
    out = []
    for name, temp in pairs:
        temp = min(temp, ceiling)
        temp = max(DEVICE_MIN_TEMP, temp - temp % STEP)
        out.append((name, temp))
    return out


def profile_no_heat(settings):
    prof = PROFILES.get(settings.get("printer", "generic"), PROFILES["generic"])
    return prof.get("no_heat", NO_HEAT)


def filter_weight(material):
    return MATERIALS.get(material or "", {}).get("weight", 1.0)


# ---------------------------------------------------------------------------
# Files
# ---------------------------------------------------------------------------
def data_dir():
    """Per-user folder for settings, the run log, filter and timer state."""
    override = os.environ.get("PBC_DATA_DIR")
    if override:
        path = override
    elif sys.platform == "win32":
        path = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "PandaBreathControl")
    elif sys.platform == "darwin":
        path = os.path.expanduser("~/Library/Application Support/PandaBreathControl")
    else:
        base = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        path = os.path.join(base, "panda-breath-control")
    os.makedirs(path, exist_ok=True)
    return path


class Paths:
    def __init__(self, root=None):
        self.root = root or data_dir()
        os.makedirs(self.root, exist_ok=True)
        self.settings = os.path.join(self.root, "settings.json")
        self.log = os.path.join(self.root, "panda_breath_log.csv")
        self.filter = os.path.join(self.root, "filter.json")
        self.timer = os.path.join(self.root, "timer.json")


DEFAULT_SETTINGS = {
    "host": DEFAULT_HOST,
    "language": None,       # None = pick from the system locale on first run
    "printer": "generic",
    "custom_ceiling": 50,
    "disclaimer_accepted": False,
}


def load_settings(paths):
    settings = dict(DEFAULT_SETTINGS)
    try:
        with open(paths.settings, encoding="utf-8") as f:
            settings.update(json.load(f))
    except (OSError, ValueError):
        pass
    if settings.get("printer") not in PROFILES:
        settings["printer"] = "generic"
    return settings


def effective_host(settings):
    """PANDA_BREATH_HOST overrides the saved address without being saved."""
    return os.environ.get("PANDA_BREATH_HOST") or settings.get("host") or DEFAULT_HOST


def save_settings(paths, settings):
    try:
        with open(paths.settings, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except OSError:
        pass
