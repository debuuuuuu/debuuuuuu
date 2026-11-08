"""Original ASCII scene: a lonely figure on an abandoned station platform,
dusk over ruined towers. Mood reference only — no copied characters.
Run: python build_station.py -> assets/station.svg
"""
import math, os, random
from xml.sax.saxutils import escape

random.seed(7)
COLS, ROWS, CW, LH, FS = 150, 58, 5.6, 10, 9.3
W, H = int(COLS * CW) + 40, ROWS * LH + 40
RAMP = " .`,:;-~=+*o#%@"


def noise(x, y):
    return (math.sin(x * 23.1 + y * 7.7) + math.sin(x * 9.3 - y * 17.9) + math.sin((x + y) * 41.0)) / 6 + .5


# ruined towers: (x0, x1, top, ruin)
TOWERS = [(.06, .17, .30, .5), (.15, .27, .22, .3), (.27, .33, .52, .6), (.33, .44, .46, .4),
          (.55, .62, .35, .5), (.62, .70, .50, .3), (.80, .92, .18, .45), (.92, .97, .40, .5)]
JAG = [random.uniform(-.04, .04) for _ in range(COLS)]
HOLES = {(c, r) for c in range(COLS) for r in range(ROWS) if random.random() < .18}


def bright(c, r):
    x, y = c / COLS, r / ROWS
    # sky + sun glow + clouds
    d = math.hypot((x - .40) * 1.6, y - .30)
    b = .30 + .65 * math.exp(-d * 4.2) + .12 * (noise(x * 1.3, y * 3) - .5) - y * .15
    for x0, x1, top, ruin in TOWERS:
        t = top + JAG[c] * (1 + ruin)
        if x0 <= x < x1 and y > t:
            b = .16
            # window grid, some blown out
            if c % 3 == 1 and r % 3 == 1:
                b = .55 if (c, r) not in HOLES else .05
            if (c, r) in HOLES and random.random() < ruin * .3:
                b = .9 * math.exp(-d * 2)  # sky seen through holes
    # overgrowth at ground
    if y > .80 - .06 * noise(x * 4, 0):
        b = .12 + .35 * noise(x * 6, y * 9)
    # station roof, sign and pillars
    if y < .09 or (y < .14 and (x < .12 or x > .88)):
        b = .07 + .05 * (c % 6 == 0)
    if .33 < x < .67 and .015 < y < .085:
        b = .78
    if x < .035 or x > .965:
        b = .07
    # original figure: hooded silhouette seen from behind, headphones cord
    fx, fy = .74, .64
    if math.hypot((x - fx) * 2.3, y - fy) < .06:
        b = .03
    if y > fy + .04 and abs(x - fx) < .03 + (y - fy) * .12:
        b = .03 if not (abs(x - fx + .012) < .004 and y < .86) else .5
    return max(0, min(.999, b))


def row_color(r):
    # lilac roof -> peach horizon -> blue overgrowth
    stops = [(0, (183, 166, 255)), (.35, (255, 196, 150)), (.62, (199, 180, 240)), (1, (110, 150, 230))]
    y = r / ROWS
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if a <= y <= b:
            t = (y - a) / (b - a)
            return "#%02x%02x%02x" % tuple(int(p + (q - p) * t) for p, q in zip(ca, cb))


lines = []
for r in range(ROWS):
    s = "".join(RAMP[int(bright(c, r) * len(RAMP))] for c in range(COLS))
    if r == 2:  # hand-lettered station sign
        sign = "|  索 引  -  s a k u i n  |"
        mid = COLS // 2 - len(sign) // 2 + 3
        s = s[:mid] + " " * len(sign) + s[mid + len(sign):]
    lines.append(s)

glitch_rows = random.sample(range(12, 48), 4)
out = []
for r, s in enumerate(lines):
    cls = ' class="g"' if r in glitch_rows else ""
    out.append(f'<text x="20" y="{30 + r * LH}" fill="{row_color(r)}"{cls} style="animation-delay:{r % 7 * 1.3:.1f}s">{escape(s)}</text>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"
 font-family="ui-monospace, Consolas, monospace" font-size="{FS}" xml:space="preserve">
<defs><radialGradient id="sun"><stop offset="0" stop-color="#FFD9A8" stop-opacity=".45"/><stop offset="1" stop-color="#FFD9A8" stop-opacity="0"/></radialGradient></defs>
<style>
.sun{{animation:pulse 5s ease-in-out infinite}}
.g{{animation:glitch 7s steps(1) infinite}}
.cur{{animation:blink 1s steps(1) infinite}}
@keyframes pulse{{50%{{opacity:.55}}}}
@keyframes glitch{{0%,92%,100%{{transform:none;opacity:1}}94%{{transform:translateX(6px);opacity:.6}}97%{{transform:translateX(-3px)}}}}
@keyframes blink{{50%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>
<rect width="{W}" height="{H}" rx="14" fill="#14112B"/>
<circle cx="{20 + COLS * CW * .40:.0f}" cy="{30 + ROWS * LH * .30:.0f}" r="150" fill="url(#sun)" class="sun"/>
{chr(10).join(out)}
<text x="{W // 2 + 15}" y="{30 + 2 * LH}" fill="#14112B" font-size="10.5" font-weight="700" text-anchor="middle">索 引  ·  s a k u i n</text>
<text x="{W // 2 + 15}" y="{30 + 6 * LH + 2}" fill="#7D76A8" font-size="9" text-anchor="middle">next train → AI engineering  ·  boarding soon<tspan class="cur" fill="#6EE7C8">_</tspan></text>
</svg>'''

os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets"), exist_ok=True)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "station.svg"), "w", encoding="utf-8") as f:
    f.write(svg)
print("\n".join(lines[::2]))
