import os
import tempfile
import unittest

from panda_breath_control import config


class ProfileTest(unittest.TestCase):
    def test_presets_never_exceed_the_cap(self):
        for key in config.PROFILES:
            for custom in (15, 40, 55, 60, 99):
                s = {"printer": key, "custom_ceiling": custom}
                ceiling = config.profile_ceiling(s)
                self.assertLessEqual(ceiling, config.DEVICE_MAX_TEMP)
                for name, temp in config.profile_presets(s):
                    with self.subTest(profile=key, material=name):
                        self.assertLessEqual(temp, ceiling)
                        self.assertGreaterEqual(temp, config.DEVICE_MIN_TEMP)
                        self.assertEqual(temp % config.STEP, 0)

    def test_ecc2_keeps_55(self):
        s = {"printer": "ecc2"}
        self.assertEqual(config.profile_ceiling(s), 55)
        self.assertIn(("ASA", 55), config.profile_presets(s))

    def test_generic_is_conservative(self):
        presets = dict(config.profile_presets({"printer": "generic"}))
        self.assertEqual(presets["ABS"], 50)
        self.assertEqual(presets["PET-CF"], 50)

    def test_every_profile_has_a_name_and_note(self):
        from panda_breath_control import i18n
        for key in config.PROFILE_ORDER:
            self.assertIn("profile_" + key, i18n.STRINGS["en"])
            self.assertIn("note_" + key, i18n.STRINGS["en"])


class SettingsTest(unittest.TestCase):
    def test_round_trip_and_bad_printer(self):
        with tempfile.TemporaryDirectory() as d:
            paths = config.Paths(d)
            s = config.load_settings(paths)
            self.assertEqual(s["host"], config.DEFAULT_HOST)
            s["printer"] = "nonexistent"
            config.save_settings(paths, s)
            self.assertEqual(config.load_settings(paths)["printer"], "generic")

    def test_env_host_overrides_without_saving(self):
        os.environ["PANDA_BREATH_HOST"] = "10.0.0.9"
        try:
            self.assertEqual(config.effective_host({"host": "x.local"}), "10.0.0.9")
        finally:
            del os.environ["PANDA_BREATH_HOST"]
        self.assertEqual(config.effective_host({"host": "x.local"}), "x.local")


if __name__ == "__main__":
    unittest.main()
