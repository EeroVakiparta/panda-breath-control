import string
import unittest

from panda_breath_control import i18n


def fields(text):
    return {f for _, f, _, _ in string.Formatter().parse(text) if f}


class TranslationTest(unittest.TestCase):
    def test_every_language_has_every_key(self):
        ref = set(i18n.STRINGS["en"])
        for code, _ in i18n.LANGUAGES:
            with self.subTest(lang=code):
                self.assertEqual(set(i18n.STRINGS[code]), ref)

    def test_placeholders_match_english(self):
        for code, _ in i18n.LANGUAGES:
            for key, text in i18n.STRINGS[code].items():
                with self.subTest(lang=code, key=key):
                    self.assertEqual(fields(text), fields(i18n.STRINGS["en"][key]))

    def test_event_labels(self):
        i18n.set_language("en")
        self.assertEqual(i18n.event_label("on:ASA"), "on ASA")
        self.assertEqual(i18n.event_label("off:timer"), "off (timer)")
        self.assertEqual(i18n.event_label("timer:12h"), "timer 12 h")
        self.assertEqual(i18n.event_label("something_new"), "something_new")

    def test_unknown_language_falls_back_to_english(self):
        i18n.set_language("xx")
        self.assertEqual(i18n.language(), "en")


if __name__ == "__main__":
    unittest.main()
