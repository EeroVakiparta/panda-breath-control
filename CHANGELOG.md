# Changelog

## Unreleased

- Sharper icon: the 16, 20, 24 and 32 px sizes are drawn on the pixel grid,
  and a thin white edge keeps the black ears visible on a dark taskbar.
- Windows: the taskbar gets the 24 px icon frame directly; Tk only passed a
  32 px icon, which Windows shrank to a jagged 24 px.

## 0.1.0 - 2026-10-16

First public release.

- Material presets, target slider, on / off (Forced On mode).
- Printer profiles with a temperature cap: generic enclosed printer, Bambu Lab
  X1 / P1 / P2S, Voron and other Klipper printers, Elegoo Centauri Carbon 2,
  custom.
- Auto-off timer that survives a restart, keeps the computer awake and
  re-sends "off" until the heater confirms it.
- HEPA + carbon filter wear gauge and a CSV run log.
- English, Finnish and Simplified Chinese.
- Demo mode without a heater, and a command-line tool (`panda-breath`).
