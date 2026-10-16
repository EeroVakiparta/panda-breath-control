# Security

## Reporting a problem in this program

Open a GitHub issue, or if the problem should not be public until it is fixed,
use GitHub's private vulnerability reporting on this repository (Security tab,
"Report a vulnerability").

## What this program does on your network

- It opens one WebSocket connection, to the heater address you configure, on
  port 80. It connects to nothing else: no update checks, no telemetry.
- Settings, the run log, filter date and timer state are plain files in your
  user folder (see the README). Nothing is uploaded.

## A property of the heater you should know about

The Panda Breath's own firmware (tested on V1.0.4) has no authentication on
its WebSocket. Any device on the same network can switch the heater on or off,
and when a client connects, the heater sends its full saved configuration,
which includes the Wi-Fi password of your router and of its own access point,
in plain text.

This program does not display, log or store those passwords, but it cannot
stop the heater from sending them. To limit the exposure:

- Keep the heater on a home network you trust. Avoid guest networks and
  shared networks.
- Never forward port 80 of the heater to the internet.
- If your router supports it, put smart-home devices on their own network.

This is a firmware matter for BIQU / BIGTREETECH; see their repository at
https://github.com/bigtreetech/Panda_Breath.
