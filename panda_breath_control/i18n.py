"""UI strings in English, Finnish and Simplified Chinese.

English is the reference: every key must exist in every language with the same
{placeholders} (tests/test_i18n.py checks this). To add a language, copy the
"en" block, translate the values and add it to LANGUAGES.
"""
import locale
import sys

LANGUAGES = (("en", "English"), ("fi", "Suomi"), ("zh", "中文"))

STRINGS = {
    "en": {
        "connecting": "Connecting...",
        "reading_state": "Reading state...",
        "status_auto": "ON · Auto mode (heats only with a bound printer)",
        "status_heating": "ON · heating (estimate)",
        "status_at_target": "ON · at target, filtering only (estimate)",
        "status_off": "OFF · {mode}",
        "mode_1": "Auto",
        "mode_2": "Forced On",
        "mode_3": "Drying",
        "mode_unknown": "?",
        "materials": "Material (click to switch on)",
        "no_heat": "{materials}: no chamber heat",
        "target": "Target",
        "on": "On",
        "off": "Off",
        "timer": "Auto-off timer",
        "timer_pre": "Off in",
        "timer_post": "h",
        "timer_set": "Set",
        "timer_cancel": "Cancel",
        "timer_none": "no timer",
        "timer_firing": "switching off...",
        "timer_waiting": "switching off, waiting for connection",
        "timer_at": "off at {when}\n({h} h {m} min left)",
        "timer_keep_open": "Keep this window open. The computer\nstays awake while the timer runs.",
        "timer_bad_hours": "Enter hours between 0 and {max} (for example 12 or 1.5).",
        "close_with_timer": "The timer switches the heater off at {when} only while this window is open.\n\nClose anyway? The heater stays on.",
        "filter": "HEPA / carbon filter",
        "filter_status": "{pct} % left · {verdict}\n{raw} h used ({weighted} h weighted / {budget}) · {days} / {maxdays} days",
        "verdict_ok": "OK",
        "verdict_soon": "replace soon",
        "verdict_replace": "REPLACE",
        "filter_changed": "Filter replaced",
        "filter_reset_q": "Reset the filter counter?\n\nNow: {raw} h of use ({weighted} h weighted), {days} days since the last change.",
        "log": "Log (latest)",
        "conn_ok": "Connected: {host}",
        "conn_lost": "No connection ({host}), retrying...",
        "conn_demo": "Demo mode, no heater connected",
        "fresh_none": "no reading yet",
        "fresh_now": "updated just now",
        "fresh_age": "last reading {s} s ago",
        "panel_target": "target {t}°",
        "panel_heating": "Heating",
        "panel_filtering": "Filtering",
        "panel_off": "Off",
        "panel_stale": "No data · {s} s",
        "panel_window": "last 30 min",
        "panel_now": "now",
        "settings": "Settings",
        "settings_title": "Settings",
        "set_host": "Heater address",
        "set_host_hint": "Hostname or IP address, for example PandaBreath.local or 192.168.1.50",
        "set_language": "Language",
        "set_printer": "Printer",
        "set_ceiling": "Maximum chamber temperature (°C)",
        "save": "Save",
        "cancel": "Cancel",
        "profile_generic": "Generic enclosed printer",
        "profile_bambu": "Bambu Lab X1 / P1 / P2S",
        "profile_voron": "Voron and other Klipper printers",
        "profile_ecc2": "Elegoo Centauri Carbon 2 (unofficial)",
        "profile_custom": "Custom",
        "note_generic": "Unknown printer, so targets are capped at 50 °C. Check what your printer's motors, belts and electronics are rated for before going higher.",
        "note_bambu": "Supported by BIQU. Presets follow Bambu Lab's own filament profiles: 60 °C for ABS, ASA, PC and PA, 50 °C for PET-CF. Auto mode with a bound printer also works without this app.",
        "note_voron": "BIQU supports Klipper printers in manual mode (Forced On), which is what this app uses. Same presets as Bambu Lab.",
        "note_ecc2": "Not supported by BIQU or Elegoo. The ECC2 has no chamber heater and its motors, belts and electronics sit inside the chamber, so targets are capped at 55 °C.",
        "note_custom": "You choose the cap (15-60 °C). The heater itself stops at 60 °C.",
        "ceiling_label": "Cap {ceiling} °C",
        "disclaimer_title": "Before you start",
        "disclaimer": (
            "Panda Breath Control is an independent, unofficial program. It is not made, "
            "endorsed or supported by BIQU / BIGTREETECH or by any printer maker.\n\n"
            "It switches a 300 W mains-powered heater on and off. You use it at your own risk.\n\n"
            "- Supervise heated prints. Leaving a print running unattended is your decision "
            "and your responsibility.\n"
            "- The auto-off timer works only while this program is running and the computer is on.\n"
            "- Many printers were never designed for a heated chamber. Check that yours can "
            "take the temperature you choose.\n"
            "- The heater's own sensor usually reads higher than the real chamber temperature.\n\n"
            "The software is provided \"as is\", without warranty of any kind (MIT licence). "
            "The authors are not liable for any damage, injury or loss arising from its use."),
        "accept": "I understand",
        "quit": "Quit",
        "ev_on": "on",
        "ev_off": "off",
        "ev_off_timer": "off (timer)",
        "ev_seen_on": "on (at heater)",
        "ev_seen_off": "off (at heater)",
        "ev_target": "target",
        "ev_app_start": "app started",
        "ev_app_close": "app closed",
        "ev_filter_changed": "filter replaced",
        "ev_timer": "timer {h} h",
        "ev_timer_cancelled": "timer cancelled",
        "ev_timer_resumed": "timer resumed",
    },
    "fi": {
        "connecting": "Yhdistetään...",
        "reading_state": "Luetaan tilaa...",
        "status_auto": "PÄÄLLÄ · Auto-tila (lämmittää vain yhdistetyn tulostimen kanssa)",
        "status_heating": "PÄÄLLÄ · lämmittää (arvio)",
        "status_at_target": "PÄÄLLÄ · tavoitteessa, vain suodatus (arvio)",
        "status_off": "POIS · {mode}",
        "mode_1": "Auto",
        "mode_2": "Forced On",
        "mode_3": "Kuivaus",
        "mode_unknown": "?",
        "materials": "Materiaali (klikkaa = päälle)",
        "no_heat": "{materials}: ei kammiolämpöä",
        "target": "Tavoite",
        "on": "Päälle",
        "off": "Pois",
        "timer": "Sammutusajastin",
        "timer_pre": "Pois",
        "timer_post": "h päästä",
        "timer_set": "Aseta",
        "timer_cancel": "Peru",
        "timer_none": "ei ajastinta",
        "timer_firing": "sammutetaan...",
        "timer_waiting": "sammutetaan, odotetaan yhteyttä",
        "timer_at": "pois klo {when}\n({h} h {m} min jäljellä)",
        "timer_keep_open": "Pidä ikkuna auki. Kone pysyy\nhereillä ajastimen aikana.",
        "timer_bad_hours": "Anna tunnit väliltä 0-{max} (esim. 12 tai 1,5).",
        "close_with_timer": "Ajastin sammuttaa laitteen klo {when} vain, jos tämä ikkuna on auki.\n\nSuljetaanko silti? Laite jää päälle.",
        "filter": "HEPA/hiilisuodatin",
        "filter_status": "{pct} % jäljellä · {verdict}\n{raw} h käyttöä ({weighted} h painotettu / {budget}) · {days} / {maxdays} vrk",
        "verdict_ok": "OK",
        "verdict_soon": "vaihto lähestyy",
        "verdict_replace": "VAIHDA",
        "filter_changed": "Suodatin vaihdettu",
        "filter_reset_q": "Nollataanko suodattimen laskuri?\n\nNyt: {raw} h käyttöä ({weighted} h painotettu), {days} vrk edellisestä vaihdosta.",
        "log": "Loki (viimeisimmät)",
        "conn_ok": "Yhdistetty: {host}",
        "conn_lost": "Ei yhteyttä ({host}), yritetään uudelleen...",
        "conn_demo": "Demotila, laitetta ei ole yhdistetty",
        "fresh_none": "ei vielä lukemaa",
        "fresh_now": "päivitetty juuri nyt",
        "fresh_age": "viimeisin lukema {s} s sitten",
        "panel_target": "tavoite {t}°",
        "panel_heating": "Lämmittää",
        "panel_filtering": "Suodattaa",
        "panel_off": "Pois",
        "panel_stale": "Ei tietoa · {s} s",
        "panel_window": "viim. 30 min",
        "panel_now": "nyt",
        "settings": "Asetukset",
        "settings_title": "Asetukset",
        "set_host": "Laitteen osoite",
        "set_host_hint": "Nimi tai IP-osoite, esim. PandaBreath.local tai 192.168.1.50",
        "set_language": "Kieli",
        "set_printer": "Tulostin",
        "set_ceiling": "Kammion maksimilämpötila (°C)",
        "save": "Tallenna",
        "cancel": "Peruuta",
        "profile_generic": "Yleinen suljettu tulostin",
        "profile_bambu": "Bambu Lab X1 / P1 / P2S",
        "profile_voron": "Voron ja muut Klipper-tulostimet",
        "profile_ecc2": "Elegoo Centauri Carbon 2 (epävirallinen)",
        "profile_custom": "Oma",
        "note_generic": "Tuntematon tulostin, joten tavoite on enintään 50 °C. Tarkista, mitä tulostimesi moottorit, hihnat ja elektroniikka kestävät, ennen kuin nostat rajaa.",
        "note_bambu": "BIQU tukee virallisesti. Esiasetukset noudattavat Bambu Labin omia filamenttiprofiileja: ABS, ASA, PC ja PA 60 °C, PET-CF 50 °C. Auto-tila yhdistetyn tulostimen kanssa toimii myös ilman tätä ohjelmaa.",
        "note_voron": "BIQU tukee Klipper-tulostimia käsiohjauksella (Forced On), jota tämä ohjelma käyttää. Samat esiasetukset kuin Bambu Labilla.",
        "note_ecc2": "BIQU ja Elegoo eivät tue tätä. ECC2:ssa ei ole kammiolämmitintä, ja sen moottorit, hihnat ja elektroniikka ovat kammion sisällä, joten tavoite on enintään 55 °C.",
        "note_custom": "Valitset rajan itse (15-60 °C). Laite itse pysähtyy 60 °C:een.",
        "ceiling_label": "Raja {ceiling} °C",
        "disclaimer_title": "Ennen kuin aloitat",
        "disclaimer": (
            "Panda Breath Control on itsenäinen, epävirallinen ohjelma. BIQU / BIGTREETECH tai "
            "mikään tulostinvalmistaja ei ole tehnyt, hyväksynyt tai tue sitä.\n\n"
            "Ohjelma kytkee 300 W:n verkkovirtalämmittimen päälle ja pois. Käytät sitä omalla vastuullasi.\n\n"
            "- Valvo lämmitettyjä tulostuksia. Jos jätät tulostuksen käyntiin valvomatta, se on "
            "sinun päätöksesi ja vastuullasi.\n"
            "- Sammutusajastin toimii vain, kun tämä ohjelma on käynnissä ja tietokone päällä.\n"
            "- Monia tulostimia ei ole suunniteltu lämmitettävällä kammiolla. Tarkista, että omasi "
            "kestää valitsemasi lämpötilan.\n"
            "- Laitteen oma anturi näyttää yleensä enemmän kuin kammion todellinen lämpötila.\n\n"
            "Ohjelmisto toimitetaan \"sellaisenaan\" ilman minkäänlaista takuuta (MIT-lisenssi). "
            "Tekijät eivät vastaa sen käytöstä aiheutuvista vahingoista, vammoista tai menetyksistä."),
        "accept": "Ymmärrän",
        "quit": "Lopeta",
        "ev_on": "päälle",
        "ev_off": "pois",
        "ev_off_timer": "pois (ajastin)",
        "ev_seen_on": "päälle (laitteesta)",
        "ev_seen_off": "pois (laitteesta)",
        "ev_target": "tavoite",
        "ev_app_start": "ohjelma käynnistyi",
        "ev_app_close": "ohjelma suljettiin",
        "ev_filter_changed": "suodatin vaihdettu",
        "ev_timer": "ajastin {h} h",
        "ev_timer_cancelled": "ajastin peruttu",
        "ev_timer_resumed": "ajastin jatkuu",
    },
    "zh": {
        "connecting": "正在连接...",
        "reading_state": "正在读取状态...",
        "status_auto": "开启 · 自动模式（仅在绑定打印机时加热）",
        "status_heating": "开启 · 加热中（估计）",
        "status_at_target": "开启 · 已达目标，仅过滤（估计）",
        "status_off": "关闭 · {mode}",
        "mode_1": "自动",
        "mode_2": "强制开启",
        "mode_3": "烘干",
        "mode_unknown": "?",
        "materials": "材料（点击即开启）",
        "no_heat": "{materials}：无需腔体加热",
        "target": "目标温度",
        "on": "开启",
        "off": "关闭",
        "timer": "定时关闭",
        "timer_pre": "",
        "timer_post": "小时后关闭",
        "timer_set": "设定",
        "timer_cancel": "取消",
        "timer_none": "未设定定时",
        "timer_firing": "正在关闭...",
        "timer_waiting": "正在关闭，等待连接",
        "timer_at": "{when} 关闭\n（剩余 {h} 小时 {m} 分）",
        "timer_keep_open": "请保持此窗口打开。\n定时期间电脑不会休眠。",
        "timer_bad_hours": "请输入 0 到 {max} 之间的小时数（例如 12 或 1.5）。",
        "close_with_timer": "只有在此窗口打开时，定时器才会在 {when} 关闭加热器。\n\n仍要关闭吗？加热器将保持开启。",
        "filter": "HEPA / 活性炭滤网",
        "filter_status": "剩余 {pct} % · {verdict}\n已用 {raw} 小时（加权 {weighted} / {budget} 小时）· {days} / {maxdays} 天",
        "verdict_ok": "正常",
        "verdict_soon": "即将更换",
        "verdict_replace": "请更换",
        "filter_changed": "已更换滤网",
        "filter_reset_q": "重置滤网计数？\n\n当前：已用 {raw} 小时（加权 {weighted} 小时），距上次更换 {days} 天。",
        "log": "日志（最新）",
        "conn_ok": "已连接：{host}",
        "conn_lost": "未连接（{host}），正在重试...",
        "conn_demo": "演示模式，未连接加热器",
        "fresh_none": "尚无读数",
        "fresh_now": "刚刚更新",
        "fresh_age": "上次读数 {s} 秒前",
        "panel_target": "目标 {t}°",
        "panel_heating": "加热中",
        "panel_filtering": "过滤中",
        "panel_off": "关闭",
        "panel_stale": "无数据 · {s} 秒",
        "panel_window": "最近 30 分钟",
        "panel_now": "现在",
        "settings": "设置",
        "settings_title": "设置",
        "set_host": "加热器地址",
        "set_host_hint": "主机名或 IP 地址，例如 PandaBreath.local 或 192.168.1.50",
        "set_language": "语言",
        "set_printer": "打印机",
        "set_ceiling": "腔体最高温度 (°C)",
        "save": "保存",
        "cancel": "取消",
        "profile_generic": "通用封闭式打印机",
        "profile_bambu": "拓竹 Bambu Lab X1 / P1 / P2S",
        "profile_voron": "Voron 及其他 Klipper 打印机",
        "profile_ecc2": "Elegoo Centauri Carbon 2（非官方）",
        "profile_custom": "自定义",
        "note_generic": "打印机型号未知，目标温度上限为 50 °C。提高上限前，请确认打印机的电机、皮带和电子元件能承受该温度。",
        "note_bambu": "BIQU 官方支持。预设值参照拓竹自己的耗材配置：ABS、ASA、PC、PA 为 60 °C，PET-CF 为 50 °C。绑定打印机后的自动模式无需本程序也可使用。",
        "note_voron": "BIQU 支持 Klipper 打印机的手动模式（强制开启），本程序正是使用该模式。预设值与拓竹相同。",
        "note_ecc2": "BIQU 和 Elegoo 均不支持。ECC2 没有腔体加热器，其电机、皮带和电子元件都位于腔体内，因此目标温度上限为 55 °C。",
        "note_custom": "上限由您自行设定（15-60 °C）。加热器本身最高 60 °C。",
        "ceiling_label": "上限 {ceiling} °C",
        "disclaimer_title": "使用前须知",
        "disclaimer": (
            "Panda Breath Control 是一个独立的非官方程序，并非由 BIQU / BIGTREETECH 或任何打印机厂商"
            "开发、认可或提供支持。\n\n"
            "本程序会开关一台 300 W 的市电加热器。使用风险由您自行承担。\n\n"
            "- 加热打印时请有人看管。无人看管时继续打印由您自行决定并承担责任。\n"
            "- 定时关闭仅在本程序运行且电脑开机时有效。\n"
            "- 许多打印机并非为加热腔体而设计。请确认您的打印机能承受所选温度。\n"
            "- 加热器自带的传感器读数通常高于腔体的实际温度。\n\n"
            "本软件按“原样”提供，不附带任何形式的保证（MIT 许可证）。"
            "对于因使用本软件而造成的任何损坏、伤害或损失，作者概不负责。"),
        "accept": "我已了解",
        "quit": "退出",
        "ev_on": "开启",
        "ev_off": "关闭",
        "ev_off_timer": "关闭（定时）",
        "ev_seen_on": "开启（加热器端）",
        "ev_seen_off": "关闭（加热器端）",
        "ev_target": "目标温度",
        "ev_app_start": "程序启动",
        "ev_app_close": "程序关闭",
        "ev_filter_changed": "已更换滤网",
        "ev_timer": "定时 {h} 小时",
        "ev_timer_cancelled": "已取消定时",
        "ev_timer_resumed": "继续定时",
    },
}

_lang = "en"


def system_language():
    """Best guess from the OS: 'fi', 'zh' or 'en'."""
    if sys.platform == "win32":
        try:
            import ctypes
            primary = ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF
            return {0x0B: "fi", 0x04: "zh"}.get(primary, "en")
        except (AttributeError, OSError):
            pass
    name = (locale.getlocale()[0] or "").lower()
    if name.startswith(("fi", "finnish")):
        return "fi"
    if name.startswith(("zh", "chinese")):
        return "zh"
    return "en"


def set_language(lang):
    global _lang
    _lang = lang if lang in STRINGS else "en"


def language():
    return _lang


def t(key, **kw):
    text = STRINGS[_lang].get(key, STRINGS["en"].get(key, key))
    text = text.format(**kw) if kw else text
    return text.replace(" °C", "\u00a0°C")  # keep "60 °C" on one line when wrapped


def event_label(ev):
    """Log event code -> display text, e.g. 'on:ASA' -> 'on ASA'."""
    base, _, arg = ev.partition(":")
    if base == "timer" and arg.endswith("h"):
        return t("ev_timer", h=arg[:-1])
    if base == "off" and arg == "timer":
        return t("ev_off_timer")
    key = "ev_" + base
    if key not in STRINGS["en"]:
        return ev
    return t(key) + (" " + arg if arg else "")
