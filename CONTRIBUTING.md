# Contributing

Bug reports, printer profiles and translations are welcome.

## Reports that help most

- Your printer model, heater version (V1.0 / V1.1) and heater firmware version
  (shown on the heater's web page under Settings).
- Your operating system and Python version (`python --version`).
- What you did, what you expected, what happened. The last lines of
  `panda_breath_log.csv` help with timer or log problems.

## Printer profiles

A new profile needs a source for its temperature cap: the printer maker's
documentation, BIQU's compatibility list, or measurements you can describe.
Profiles live in `panda_breath_control/config.py` (`PROFILES`), with a name
and a one-paragraph note in every language in `panda_breath_control/i18n.py`.

## Translations

Copy the `"en"` block in `panda_breath_control/i18n.py`, translate the values,
keep every `{placeholder}` and add the language to `LANGUAGES`. A native
speaker's review of the existing Finnish and Chinese text is also welcome.

## Code

- Python 3.9+, standard library plus `websockets`. Keep it that way unless
  there is a strong reason.
- Run the tests before sending a pull request:

      python -m unittest discover -s tests -t .

- Try UI changes in demo mode: `python -m panda_breath_control --demo`.
- Never send a target above the profile cap, and send `work_on` only as a
  JSON boolean (see docs/PROTOCOL.md).

By contributing you agree that your contribution is licensed under the MIT
licence of this project.
