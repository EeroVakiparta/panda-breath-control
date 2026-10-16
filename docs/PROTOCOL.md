# Panda Breath local protocol notes

What this program relies on, as observed on a Panda Breath V1.0 with firmware
V1.0.4 (September-October 2026). BIQU does not document any of this, so treat
it as subject to change with firmware updates.

## HTTP

| Request | What |
|---|---|
| `GET /` | the stock web page (one HTML file with its own JavaScript) |
| `POST /ota` | firmware upload from the web page |
| `GET /ws` (WebSocket upgrade) | everything else |

There is no REST API.

## WebSocket `ws://<host>/ws`

- On connect the heater sends one message with its full state:
  `{"settings": {...}}` plus other top-level keys (`wifi`, `sta`, `ap`,
  `printer`, `ha`) mirroring the pages of the web UI. **These include saved
  Wi-Fi passwords in plain text** (see [SECURITY.md](../SECURITY.md)).
- After that it sends `{"settings": {"warehouse_temper": N}}` about once a
  second: the chamber reading in °C from its own sensor, which sits near the
  heating element and reads high.
- Commands are `{"settings": {<key>: <value>}}`, one key per message works
  fine. There is no reply or acknowledgement.
- **Changes are not broadcast.** If the state changes through the heater's
  buttons, the web page or another client, connected clients are not told.
  The only way to see it is to reconnect and read the first message again.
  This program reconnects every 30 seconds for that reason.
- No authentication.

### `settings` keys

| Key | Values | Meaning |
|---|---|---|
| `work_on` | send `true` / `false` | Master on/off ("Work Mode" toggle). **Commands must be JSON booleans**: `1` / `0` are silently ignored. The heater itself reports the value as `1` / `0`. |
| `work_mode` | `1` Auto, `2` Forced On, `3` Drying | Mode, same as the coloured buttons on the unit |
| `set_temp` | integer °C | Chamber target for Forced On (the web UI slider allows 15-60) |
| `warehouse_temper` | integer °C | Chamber reading (read only) |
| `filtertemp`, `hotbedtemp` | integer °C | Auto mode thresholds: the filter fans start when the bound printer's bed exceeds `filtertemp`, heating starts above `hotbedtemp` |
| `filament_drying_mode` | `1` PLA, `2` PETG, `3` custom | Drying preset |
| `filament_temp`, `filament_timer` | °C, hours | Custom drying temperature and time |
| `isrunning` | | Drying in progress |
| `language`, `printer_type` | | Settings page |
| `factory_reset`, `reset` | `1` | Settings page actions. This program never sends them. |

Things the heater does not report: whether the heating element or the fans
are running at a given moment. "Heating" in this program is an estimate
(switched on and reading below target).

Auto mode follows a Bambu Lab printer bound on the web page. BIQU's wiki says
Klipper printers currently need manual control, with automatic operation to
come. On a printer that is not bound, Auto mode never heats; use Forced On.

## Home Assistant / MQTT

Firmware V1.0.4 added MQTT with Home Assistant discovery. You enter a broker
address, port (default 1883), user and password on the web page (HA tab).
The options are plain MQTT only, without TLS. Strings in the V1.0.4 firmware
suggest:

- topics `<prefix>/<id>/state` (JSON), `<prefix>/<id>/command` (JSON, one key)
  and `<prefix>/<id>/availability` (`online` / `offline`)
- discovery under `homeassistant/{switch,number,select,sensor}/<id>/.../config`
- command keys such as `{"work_on": "ON"}`, `{"mode": "power on"}`,
  `{"target_temp": 45}`

These were not tested with a broker. Read the real topic names from your
broker once the heater is connected to it.

## Known firmware issues (upstream)

- Heater switching itself off after a while:
  [bigtreetech/Panda_Breath#29](https://github.com/bigtreetech/Panda_Breath/issues/29)
- "PTC Heater Abnormal" message:
  [bigtreetech/Panda_Breath#5](https://github.com/bigtreetech/Panda_Breath/issues/5)
- A firmware update over the web page erases all settings, including Wi-Fi:
  [bigtreetech/Panda_Breath#20](https://github.com/bigtreetech/Panda_Breath/issues/20)
- The `.bin` files in the BIQU repository are update images, not full flash
  images, so flashing them over USB does not work:
  [bigtreetech/Panda_Breath#25](https://github.com/bigtreetech/Panda_Breath/issues/25)

## Other projects using the same protocol

- [justinh-rahb/pandabreath-klipper](https://github.com/justinh-rahb/pandabreath-klipper):
  Klipper extras module. Its notes list newer status fields such as
  `cal_warehouse_temp`, `drying_remaining_min`.
- [plastikman/DragonBreath](https://github.com/plastikman/DragonBreath):
  replacement open firmware with its own REST API. This program has not been
  tested with it.
