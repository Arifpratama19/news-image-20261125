#!/usr/bin/env python3
"""THE WORLD TODAY - Wednesday 25 November 2026.
Pure-stdlib newspaper front page: draws a 1024x1024 PNG with its own
PNG encoder and its own 5x7 bitmap font. No network, deterministic.
Writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).
"""
import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (18, 18, 18)
RED = (178, 34, 34)
BLUE = (23, 68, 128)
NAVY = (16, 32, 64)
GOLD = (198, 142, 32)
TEAL = (14, 110, 110)
GREY = (90, 90, 88)
LIGHT = (232, 226, 210)
SKY = (168, 205, 232)
SEA = (38, 98, 158)

# ---------------------------------------------------------------- PNG writer
def _chunk(typ, data):
    c = struct.pack(">I", len(data)) + typ + data
    c += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return c

def write_png(path, px):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw.extend(px[y * W * 3:(y + 1) * W * 3])
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits ('1' = ink). Lowercase maps to uppercase.
FONT = {
"A": ["01110","10001","10001","11111","10001","10001","10001"],
"B": ["11110","10001","10001","11110","10001","10001","11110"],
"C": ["01110","10001","10000","10000","10000","10001","01110"],
"D": ["11110","10001","10001","10001","10001","10001","11110"],
"E": ["11111","10000","10000","11110","10000","10000","11111"],
"F": ["11111","10000","10000","11110","10000","10000","10000"],
"G": ["01110","10001","10000","10111","10001","10001","01111"],
"H": ["10001","10001","10001","11111","10001","10001","10001"],
"I": ["01110","00100","00100","00100","00100","00100","01110"],
"J": ["00111","00010","00010","00010","00010","10010","01100"],
"K": ["10001","10010","10100","11000","10100","10010","10001"],
"L": ["10000","10000","10000","10000","10000","10000","11111"],
"M": ["10001","11011","10101","10101","10001","10001","10001"],
"N": ["10001","11001","10101","10011","10001","10001","10001"],
"O": ["01110","10001","10001","10001","10001","10001","01110"],
"P": ["11110","10001","10001","11110","10000","10000","10000"],
"Q": ["01110","10001","10001","10001","10101","10010","01101"],
"R": ["11110","10001","10001","11110","10100","10010","10001"],
"S": ["01111","10000","10000","01110","00001","00001","11110"],
"T": ["11111","00100","00100","00100","00100","00100","00100"],
"U": ["10001","10001","10001","10001","10001","10001","01110"],
"V": ["10001","10001","10001","10001","10001","01010","00100"],
"W": ["10001","10001","10001","10101","10101","11011","10001"],
"X": ["10001","10001","01010","00100","01010","10001","10001"],
"Y": ["10001","10001","01010","00100","00100","00100","00100"],
"Z": ["11111","00001","00010","00100","01000","10000","11111"],
"0": ["01110","10001","10011","10101","11001","10001","01110"],
"1": ["00100","01100","00100","00100","00100","00100","01110"],
"2": ["01110","10001","00001","00110","01000","10000","11111"],
"3": ["11110","00001","00001","01110","00001","00001","11110"],
"4": ["00010","00110","01010","10010","11111","00010","00010"],
"5": ["11111","10000","11110","00001","00001","10001","01110"],
"6": ["01110","10000","10000","11110","10001","10001","01110"],
"7": ["11111","00001","00010","00100","01000","01000","01000"],
"8": ["01110","10001","10001","01110","10001","10001","01110"],
"9": ["01110","10001","10001","01111","00001","00001","01110"],
" ": ["00000","00000","00000","00000","00000","00000","00000"],
".": ["00000","00000","00000","00000","00000","01100","01100"],
",": ["00000","00000","00000","00000","01100","00100","01000"],
":": ["00000","01100","01100","00000","01100","01100","00000"],
";": ["00000","01100","01100","00000","01100","00100","01000"],
"!": ["00100","00100","00100","00100","00100","00000","00100"],
"?": ["01110","10001","00001","00110","00100","00000","00100"],
"-": ["00000","00000","00000","01110","00000","00000","00000"],
"'": ["00100","00100","01000","00000","00000","00000","00000"],
'"': ["01010","01010","00000","00000","00000","00000","00000"],
"(": ["00010","00100","01000","01000","01000","00100","00010"],
")": ["01000","00100","00010","00010","00010","00100","01000"],
"/": ["00001","00010","00010","00100","01000","01000","10000"],
"%": ["11001","11010","00010","00100","01000","01011","10011"],
"$": ["00100","01111","10100","01110","00101","11110","00100"],
"&": ["01100","10010","10100","01000","10101","10010","01101"],
"+": ["00000","00100","00100","01110","00100","00100","00000"],
"=": ["00000","00000","11111","00000","11111","00000","00000"],
"*": ["00000","10101","01110","10101","00000","00000","00000"],
"#": ["01010","01010","11111","01010","11111","01010","01010"],
"@": ["01110","10001","10111","10101","10110","10000","01110"],
"_": ["00000","00000","00000","00000","00000","00000","11111"],
">": ["10000","01000","00100","00010","00100","01000","10000"],
"<": ["00001","00010","00100","01000","00100","00010","00001"],
"|": ["00100","00100","00100","00100","00100","00100","00100"],
}

# ---------------------------------------------------------------- canvas
px = bytearray(PAPER[0] for _ in range(W * H * 3))
# fill properly (bytearray trick above repeats R only); do it explicitly
for _i in range(W * H):
    px[_i * 3] = PAPER[0]
    px[_i * 3 + 1] = PAPER[1]
    px[_i * 3 + 2] = PAPER[2]

def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = c

def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            set_px(xx, yy, c)

def hline(x, y, w, c):
    rect(x, y, w, 1, c)

def vline(x, y, h, c):
    rect(x, y, 1, h, c)

def line(x0, y0, x1, y1, c):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        set_px(x0, y0, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

def circle(cx, cy, r, c, fill=True):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d = (xx - cx) ** 2 + (yy - cy) ** 2
            if fill:
                if d <= r * r:
                    set_px(xx, yy, c)
            else:
                if r * r - 2 * r <= d <= r * r:
                    set_px(xx, yy, c)

def tri(x0, y0, x1, y1, x2, y2, c):
    # scanline fill
    ys = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
    (ax, ay), (bx, by), (cx_, cy_) = ys
    def edge(xa, ya, xb, yb, y):
        if yb == ya:
            return xa
        return xa + (xb - xa) * (y - ya) / (yb - ya)
    for y in range(ay, cy_ + 1):
        if y < by:
            xa = edge(ax, ay, bx, by, y)
            xb = edge(ax, ay, cx_, cy_, y)
        else:
            xa = edge(bx, by, cx_, cy_, y)
            xb = edge(ax, ay, cx_, cy_, y)
        for xx in range(int(min(xa, xb)), int(max(xa, xb)) + 1):
            set_px(xx, y, c)

# ---------------------------------------------------------------- text
def char_w(scale):
    return 6 * scale

def text_w(s, scale):
    return len(s) * char_w(scale) - scale

def draw_text(x, y, s, scale, c):
    s = s.upper()
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[" "])
        for r in range(7):
            row = g[r]
            for col in range(5):
                if row[col] == "1":
                    rect(cx + col * scale, y + r * scale, scale, scale, c)
        cx += char_w(scale)
    return cx

def text_center(x, y, w, s, scale, c):
    draw_text(x + (w - text_w(s, scale)) // 2, y, s, scale, c)

def wrap(s, width, scale):
    """Wrap uppercased text to lines fitting width px."""
    maxch = max(1, width // char_w(scale))
    words, lines, cur = s.upper().split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if len(trial) <= maxch:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            # hard-split overlong word
            while len(wd) > maxch:
                lines.append(wd[:maxch])
                wd = wd[maxch:]
            cur = wd
    if cur:
        lines.append(cur)
    return lines

def para(x, y, s, width, scale, c, max_lines=None, lh=None):
    lines = wrap(s, width, scale)
    if max_lines:
        lines = lines[:max_lines]
    if lh is None:
        lh = 7 * scale + 2
    for i, ln in enumerate(lines):
        draw_text(x, y + i * lh, ln, scale, c)
    return y + len(lines) * lh

# ---------------------------------------------------------------- scenes
def scene_baltic(x, y, w, h):
    """Baltic Sea: grey cargo ship, drone above, orange blast."""
    rect(x, y, w, h, SKY)
    rect(x, y + h - 42, w, 42, SEA)
    for i in range(0, w, 26):
        line(x + i, y + h - 42, x + i + 12, y + h - 36, (120, 180, 215))
    # ship hull
    rect(x + 62, y + h - 62, 150, 22, (52, 58, 66))
    rect(x + 62, y + h - 62, 150, 4, (90, 96, 104))
    rect(x + 92, y + h - 82, 46, 20, (210, 210, 205))
    rect(x + 148, y + h - 74, 34, 12, (178, 34, 34))
    rect(x + 170, y + h - 96, 5, 22, (52, 58, 66))
    # containers
    rect(x + 196, y + h - 78, 22, 16, GOLD)
    rect(x + 220, y + h - 78, 22, 16, TEAL)
    # drone
    dx, dy = x + w - 78, y + 26
    rect(dx - 14, dy - 3, 28, 6, INK)
    rect(dx - 20, dy - 6, 12, 3, INK)
    rect(dx + 8, dy - 6, 12, 3, INK)
    circle(dx, dy, 4, RED)
    line(dx - 8, dy + 4, x + 150, y + h - 66, RED)
    # blast star
    bx, by = x + 150, y + h - 66
    for ang in range(0, 360, 45):
        import math as _m
        ex = int(bx + 16 * _m.cos(_m.radians(ang)))
        ey = int(by + 16 * _m.sin(_m.radians(ang)))
        line(bx, by, ex, ey, (255, 140, 0))
    circle(bx, by, 9, (255, 180, 40))
    circle(bx, by, 4, (255, 240, 160))

def scene_riyadh(x, y, w, h):
    """Riyadh night: tallest tower, orange strike flash, city lights."""
    rect(x, y, w, h, NAVY)
    for i in range(6):
        circle(x + 18 + i * 46, y + 14 + (i % 3) * 9, 2, (240, 240, 220))
    circle(x + w - 34, y + 22, 12, (240, 230, 180))
    # tower: straight shaft with a spire, lit windows
    tx = x + w // 2 - 16
    rect(tx + 4, y + 38, 24, h - 46, (200, 205, 215))
    rect(tx + 14, y + 24, 4, 16, (200, 205, 215))
    rect(tx + 4, y + 38, 24, 3, (230, 233, 238))
    # blast beside the spire
    circle(tx + 30, y + 32, 10, (255, 140, 0))
    circle(tx + 30, y + 32, 5, (255, 210, 90))
    # lit windows
    for yy in range(y + 48, y + h - 14, 12):
        for xx in range(tx + 8, tx + 24, 8):
            rect(xx, yy, 3, 5, (255, 210, 90))
    # city base
    rect(x, y + h - 16, w, 16, (10, 20, 44))
    for i in range(0, w, 18):
        rect(x + i, y + h - 26, 10, 10, (30, 48, 80))
        rect(x + i + 3, y + h - 23, 2, 2, (255, 210, 90))

def scene_pacific(x, y, w, h):
    """Pacific: globe, treaty document with seal, island dots."""
    rect(x, y, w, h, (178, 216, 238))
    cx, cy, r = x + 92, y + h // 2 + 4, 52
    circle(cx, cy, r, (38, 110, 180))
    # land blobs (stylised Australia + islands)
    circle(cx - 6, cy + 16, 16, (74, 160, 90))
    circle(cx + 12, cy + 20, 10, (74, 160, 90))
    circle(cx + 26, cy - 14, 7, (120, 190, 110))
    circle(cx - 24, cy - 18, 6, (120, 190, 110))
    circle(cx, cy - 26, 5, (120, 190, 110))
    # latitude lines
    for dy in (-26, 0, 26):
        line(cx - r + 8, cy + dy, cx + r - 8, cy + dy, (120, 180, 220))
    circle(cx, cy, r, (20, 60, 110), fill=False)
    # treaty paper
    px0, py0 = x + w - 108, y + 18
    rect(px0, py0, 88, h - 36, (255, 255, 250))
    rect(px0, py0, 88, h - 36, INK)  # outline via border trick below
    rect(px0 + 1, py0 + 1, 86, h - 38, (255, 255, 250))
    rect(px0, py0, 88, 3, RED)
    for i in range(5):
        rect(px0 + 10, py0 + 14 + i * 11, 56 - (i % 2) * 12, 3, (120, 120, 115))
    circle(px0 + 62, py0 + h - 62, 11, RED)
    circle(px0 + 62, py0 + h - 62, 6, GOLD)
    draw_text(px0 + 8, py0 + h - 30, "TREATY", 1, INK)

def scene_climate(x, y, w, h):
    """COP31 aftermath: cracked dry earth under a harsh sun."""
    rect(x, y, w, h, (242, 214, 160))
    circle(x + w - 30, y + 22, 15, (255, 150, 30))
    for ang in range(0, 360, 30):
        import math as _m
        line(x + w - 30 + int(19 * _m.cos(_m.radians(ang))),
             y + 22 + int(19 * _m.sin(_m.radians(ang))),
             x + w - 30 + int(26 * _m.cos(_m.radians(ang))),
             y + 22 + int(26 * _m.sin(_m.radians(ang))), (255, 150, 30))
    rect(x, y + h - 46, w, 46, (196, 148, 92))
    line(x + 10, y + h - 46, x + 60, y + h - 18, (120, 80, 40))
    line(x + 60, y + h - 18, x + 110, y + h - 40, (120, 80, 40))
    line(x + 150, y + h - 46, x + 190, y + h - 12, (120, 80, 40))
    line(x + 210, y + h - 46, x + 250, y + h - 24, (120, 80, 40))
    # dry grass tufts on the cracked earth
    for gx in (30, 120, 200):
        line(x + gx, y + h - 46, x + gx - 4, y + h - 58, (120, 90, 40))
        line(x + gx, y + h - 46, x + gx + 4, y + h - 58, (120, 90, 40))

# ---------------------------------------------------------------- stories
# (section, headline, one-line summary) -- all reported 25 Nov 2026
COL1 = [
 ("EUROPE", "ZELENSKIY CONFIRMS UKRAINE HIT RUSSIAN SHIP",
  "Kyiv takes blame for Gulf of Finland strike."),
 ("EUROPE", "RUSSIA CALLS SHIP STRIKES 'TERRORISM'",
  "Moscow warns of severe response to attacks."),
 ("EUROPE", "UKRAINE SANK RUSSIAN WARSHIP OFF LIBYA",
  "Drones hit Sparta II, said to carry arms."),
 ("EUROPE", "PUTIN VOWS REPLY TO REFINERY STRIKES",
  "Kremlin orders officials to shield power plants."),
 ("EUROPE", "MISSILE ON ZELENSKIY HOMETOWN KILLS 2",
  "Kryvyi Rih hit; 60 wounded in the Russian strike."),
 ("EUROPE", "ZAPORIZHZHIA: 7 KILLED, 80 HURT IN A DAY",
  "Odesa: 80,000 homes without heat as winter bites."),
 ("EUROPE", "NATO TO SEND EARLY-WARNING JETS TO POLAND",
  "Move follows missiles landing in Poland in raid."),
 ("EUROPE", "EU READIES NEW RUSSIA SANCTIONS",
  "Package targets banks, crypto and shadow fleet."),
 ("EUROPE", "SARKOZY CORRUPTION CASE GOES TO TRIAL",
  "Ex-president and wife face hearing on 1 Apr 2027."),
 ("EUROPE", "UK TO PROBE NUCLEAR TEST VETERANS' HEALTH",
  "PM Burnham orders review of Cold War atomic tests."),
]
COL2 = [
 ("MIDDLE EAST", "ISRAEL KILLS HAMAS SECURITY CHIEF IN GAZA",
  "Airstrike kills Naeem Abu Nahel in Gaza Strip."),
 ("MIDDLE EAST", "UNRWA WORKER KILLED IN GAZA STRIKE",
  "Three more aid staff hurt near a Jabalya well."),
 ("MIDDLE EAST", "GAZA DEATH TOLL REACHES 74,746",
  "Oxfam: pollution risks across over 99% of Gaza."),
 ("MIDDLE EAST", "HOUTHIS HIT RIYADH'S TALLEST TOWER",
  "Saudi civil defence: 11 wounded in drone strike."),
 ("MIDDLE EAST", "HOUTHIS 60 KM FROM ADEN, ARMY SAYS",
  "Yemen forces vow rebels will not seize capital."),
 ("MIDDLE EAST", "THREE TANKERS HIT BY MINES IN HORMUZ",
  "Iran navy blames mines; US suspects Iran hackers."),
 ("MIDDLE EAST", "YEMEN: 350,000 CHILDREN MISS SHOTS IN TAIZ",
  "UN: vaccines cannot reach the encircled city."),
 ("ASIA-PACIFIC", "SOLOMONS SIGNS AUSTRALIA TREATY",
  "Canberra is primary partner; no foreign bases."),
 ("ASIA-PACIFIC", "FIJI DROUGHT COULD STRETCH INTO 2027",
  "Pacific islands 'tired of waiting' on climate."),
 ("ASIA-PACIFIC", "INDIA: BJP AND SAD REUNITE FOR PUNJAB",
  "Alliance revived after six years; SAD rejoins NDA."),
]
COL3 = [
 ("AMERICAS", "CIA AND ODNI HIT BY CYBER BREACH",
  "Unclassified data hit, CNN reports; latest US hack."),
 ("AMERICAS", "HUAWEI GUILTY OF STEALING US SECRETS",
  "New York jury convicts on 10 of 12 counts."),
 ("AMERICAS", "US BLACKLISTS MEGASPEED OVER CHIPS",
  "Singapore firm cut off from advanced AI chips."),
 ("AMERICAS", "TRUMP GIVES GIULIANI MEDAL OF FREEDOM",
  "Ex-New York mayor honoured by the president."),
 ("AMERICAS", "FORT HOOD GUNMAN SEEKS STAY OF EXECUTION",
  "Killer of 13 in 2009 asks court to halt execution."),
 ("AFRICA", "WHO EVACUATES EBOLA STAFF IN CONGO",
  "Team fled Akwe hospital after 3 days of fighting."),
 ("AFRICA", "175 MIGRANTS MISSING OFF SENEGAL",
  "Contact lost at sea; fears grow for all aboard."),
 ("AFRICA", "SUDAN: RSF COMMANDER DEFECTS TO ARMY",
  "Rebel officer switches sides with his troops."),
 ("MARKETS / TECH", "ASIAN STOCKS TUMBLE ON TARIFF THREAT",
  "Seoul -5.3%, Taiwan -5.1%, Nikkei -2.9%."),
 ("MARKETS / TECH", "DELL BEATS ON AI, LIFTS FORECAST TO $202BN",
  "Q3 sales $54.94bn; $25bn buyback announced."),
]
TICKER = [
 "SANOFI TO BUY INSMED FOR $41BN IN CASH",
 "NETFLIX BUYS RADFORD STUDIO FOR $380M",
 "SHEIN PAYS $100M TO SETTLE FTC CLAIMS",
 "ENGLAND BEAT AUSTRALIA BY 8 WICKETS IN 2ND T20I",
 "QUASAR FOUND 630M YEARS AFTER BIG BANG",
]

# ---------------------------------------------------------------- layout
def draw_column(x, w, y0, y1, title, stories):
    rect(x, y0, w, 20, NAVY)
    draw_text(x + 6, y0 + 4, title, 1, (255, 255, 255))
    y = y0 + 28
    for section, head, summ in stories:
        if y > y1 - 52:
            break
        draw_text(x, y, section + " - 25 NOV", 1, RED)
        y += 9
        y = para(x, y, head, w, 2, INK, max_lines=2, lh=14)
        y = para(x, y + 1, summ, w, 1, (60, 60, 58), max_lines=1, lh=8)
        y += 4
        hline(x, y, w, (200, 194, 178))
        y += 4
    return y

def main():
    # ---- masthead
    hline(24, 10, 976, INK)
    rect(24, 13, 976, 3, INK)
    text_center(24, 26, 976, "THE WORLD TODAY", 6, INK)
    text_center(24, 74, 976, "WEDNESDAY 25 NOVEMBER 2026", 2, RED)
    draw_text(24, 96, "ONE DAY. THE WHOLE WORLD.", 1, GREY)
    tw = text_w("36 STORIES - 8 REGIONS - ALL DATED 25 NOV 2026", 1)
    draw_text(1000 - tw, 96, "36 STORIES - 8 REGIONS - ALL DATED 25 NOV 2026", 1, GREY)
    hline(24, 110, 976, INK)
    # ---- hero: four illustrated scenes
    panels = [
        ("BALTIC SEA", "UKRAINE CONFIRMS DRONE STRIKES ON RUSSIAN SHIPS", scene_baltic),
        ("RIYADH", "HOUTHI DRONE HITS TALLEST TOWER; 11 HURT", scene_riyadh),
        ("PACIFIC", "SOLOMONS PICKS AUSTRALIA OVER CHINA PACT", scene_pacific),
        ("CLIMATE", "COP31 COLLAPSES: NO FOSSIL-FUEL DEAL", scene_climate),
    ]
    px0, pw, gap = 24, 238, 8
    for i, (title, cap, fn) in enumerate(panels):
        x = px0 + i * (pw + gap)
        fn(x, 118, pw, 108)
        draw_text(x, 232, title, 1, RED)
        para(x, 244, cap, pw, 1, INK, max_lines=2, lh=9)
    hline(24, 268, 976, INK)
    # ---- lead story
    draw_text(24, 278, "LEAD STORY - EUROPE - 25 NOV 2026", 1, RED)
    para(24, 292, "UKRAINE CONFIRMS IT SANK RUSSIAN SHIPS IN THE BALTIC AND OFF LIBYA",
         976, 3, INK, max_lines=2, lh=23)
    para(24, 342, "PRESIDENT ZELENSKIY SAYS KYIV STRUCK A RUSSIAN CARGO SHIP IN THE GULF OF "
         "FINLAND AND A WARSHIP OFF BENGHAZI CARRYING ARMS. MOSCOW CALLS THE ATTACKS "
         "TERRORISM AND VOWS A SEVERE RESPONSE AS THE WAR SPREADS BEYOND EUROPE.",
         976, 1, (60, 60, 58), max_lines=2, lh=9)
    hline(24, 362, 976, INK)
    # ---- three columns, 30 stories
    draw_column(24, 312, 370, 950, "EUROPE AND THE WAR", COL1)
    draw_column(356, 312, 370, 950, "MIDDLE EAST AND ASIA-PACIFIC", COL2)
    draw_column(688, 312, 370, 950, "AMERICAS, AFRICA AND MARKETS", COL3)
    vline(348, 370, 580, (200, 194, 178))
    vline(680, 370, 580, (200, 194, 178))
    # ---- ticker: 5 more stories
    hline(24, 952, 976, INK)
    draw_text(24, 962, "ALSO TODAY:", 1, RED)
    tx = 24 + text_w("ALSO TODAY: ", 1) + 6
    ticker = "  -  ".join(TICKER)
    para(tx, 962, ticker, 976 - tx, 1, INK, max_lines=2, lh=9)
    # ---- footer
    hline(24, 988, 976, INK)
    text_center(24, 996, 976,
                "SOURCES: REUTERS, AP, UN NEWS, BBC, CNN - ALL STORIES REPORTED 25 NOVEMBER 2026",
                1, GREY)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    n = write_png(path, px)
    print("wrote", path, n, "bytes")

if __name__ == "__main__":
    main()
