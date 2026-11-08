"""Generates the animated SVGs for the GitHub profile README.
Run: python build_assets.py  -> writes assets/*.svg
"""
import os
from xml.sax.saxutils import escape

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(OUT, exist_ok=True)

# palette: ink on paper, one spectral data stream
BG, PANEL, INK, DIM, AMBER, LILAC, MINT = (
    "#FBFBF8", "#EFEFEA", "#111111", "#77777A", "#111111", "#9A9A9E", "#2D3BFF")
MONO = "ui-monospace, 'JetBrains Mono', 'Cascadia Code', Consolas, monospace"


SPECTRUM = ["#FF2E4D", "#FF8A00", "#FFD400", "#22C55E", "#00B8FF", "#2D3BFF", "#C026D3"]


def beam(x, y0, lh, cw, cols, rows, seed, fs):
    """rainbow data stream: rows of glyphs in spectral bands, flickering + drifting"""
    import random
    rnd = random.Random(seed)
    out = []
    for r in range(rows):
        spans = []
        for c in range(cols):
            ch = rnd.choice("=-_:#|/") if rnd.random() < .55 + .4 * (c / cols) else " "
            col = SPECTRUM[(r + c // 3) % len(SPECTRUM)]
            spans.append(f'<tspan fill="{col}">{escape(ch)}</tspan>')
        out.append(f'<text x="{x:.1f}" y="{y0 + r * lh:.1f}" font-size="{fs}" class="bm" textLength="{cols * cw:.1f}" '
                   f'lengthAdjust="spacingAndGlyphs" style="animation-delay:{r * .23:.2f}s">{"".join(spans)}</text>')
    return chr(10).join(out)

BEAM_CSS = ".bm{{animation:bm 1.8s steps(3) infinite}}@keyframes bm{{0%{{transform:translateX(0);opacity:1}}33%{{transform:translateX(-4px);opacity:.75}}66%{{transform:translateX(3px);opacity:.9}}}}"

FONT = {
    "D": ["####.", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "####.", "#....", "#####"],
    "B": ["####.", "#...#", "####.", "#...#", "####."],
    "J": ["#####", "...#.", "...#.", "#..#.", ".##.."],
    "I": ["#####", "..#..", "..#..", "..#..", "#####"],
    "T": ["#####", "..#..", "..#..", "..#..", "..#.."],
}


def pixel_word(word, x0, y0, px, gap=1, start=0.2, step=0.035):
    rects, col = [], 0
    for ch in word:
        g = FONT[ch]
        for c in range(5):
            for r in range(5):
                if g[r][c] == "#":
                    x, y = x0 + (col + c) * px, y0 + r * px
                    d = start + (col + c) * step
                    # shadow pixel + main pixel
                    rects.append(f'<rect x="{x+4}" y="{y+4}" width="{px-2}" height="{px-2}" fill="{LILAC}" opacity=".35" class="p" style="animation-delay:{d:.2f}s"/>')
                    rects.append(f'<rect x="{x}" y="{y}" width="{px-2}" height="{px-2}" fill="{AMBER}" class="p" style="animation-delay:{d:.2f}s"/>')
        col += 5 + gap
    return "\n".join(rects), col * px


def typed(text, x, y, delay, dur, color=INK, size=17, cid="t"):
    w = len(text) * size * 0.6 + 4
    steps = max(len(text), 1)
    return (f'<clipPath id="{cid}"><rect x="{x}" y="{y-size}" height="{size+8}" width="{w:.0f}" '
            f'class="type" style="animation:type {dur}s steps({steps}) {delay}s both"/></clipPath>'
            f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" textLength="{len(text) * size * 0.6:.1f}" lengthAdjust="spacingAndGlyphs" clip-path="url(#{cid})">{escape(text)}</text>')


def header():
    """ASCII dusk header: power lines over a dithered sky, name carved in characters."""
    import math, random
    rnd = random.Random(3)
    COLS, ROWS, CW, LH, FS = 150, 22, 5.6, 10, 9.3
    W, H = 900, 400
    grid = [[" "] * COLS for _ in range(ROWS)]
    tone = [[0.0] * COLS for _ in range(ROWS)]
    SKY = " .`,:;"
    for r in range(ROWS):
        for c in range(COLS):
            x, y = c / COLS, r / ROWS
            b = .55 * math.exp(-math.hypot((x - .18) * 1.5, y - .9) * 2.6) + rnd.random() * .12
            grid[r][c] = SKY[min(len(SKY) - 1, int(b * len(SKY) * 1.4))]
    # sagging power lines + one pole
    for k, (a, sag) in enumerate([(1, 7), (3, 6), (5, 8)]):
        for c in range(COLS):
            r = int(a + sag * ((c / COLS - .55) ** 2) * 4)
            if 0 <= r < ROWS and grid[r][c] in SKY:
                grid[r][c] = "-" if (c + k) % 9 else "~"
    # name, each font pixel = 3x2 characters, dithered edges
    sx, sy, x0, y0 = 3, 2, 4, 6
    col = 0
    for ch in "DEBJIT":
        g = FONT[ch]
        for gr in range(5):
            for gc in range(5):
                if g[gr][gc] != "#":
                    continue
                for dy in range(sy):
                    for dx in range(sx):
                        c, r = x0 + (col + gc) * sx + dx, y0 + gr * sy + dy
                        grid[r][c] = rnd.choice("@@#%") if dx < sx - 1 else rnd.choice("#%*+")
                        tone[r][c] = 1
                        if r + 1 < ROWS and grid[r + 1][c + 1] in SKY:
                            grid[r + 1][c + 1] = ":"  # drop shadow
        col += 6
    rows = []
    for r in range(ROWS):
        line = "".join(grid[r])
        # split into sky / name runs so the name can be amber
        out, cur, curt = [], "", None
        for c in range(COLS):
            t = tone[r][c]
            if t != curt and cur:
                out.append((cur, curt)); cur = ""
            cur += line[c]; curt = t
        out.append((cur, curt))
        spans = "".join(
            f'<tspan fill="{AMBER if t else LILAC}"{"" if t else ' opacity=".55"'}>{escape(s)}</tspan>' for s, t in out)
        rows.append(f'<text x="22" y="{24 + r * LH}" class="row" style="animation-delay:{r * .06:.2f}s">{spans}</text>')

    lines = [
        ("> query  ", "who is debjit?", 2.0, .9, INK),
        ("  fetch  ", "top_k=3 from github · linkedin · x", 3.1, 1.1, DIM),
        ("  answer ", "learning RAG + LangChain, building LLM apps in public.", 4.4, 1.6, INK),
        ("         ", "open to AI engineering roles.", 6.2, .9, MINT),
    ]
    body = []
    for i, (label, text, d, dur, colr) in enumerate(lines):
        y = 280 + i * 22
        body.append(f'<text x="22" y="{y}" fill="{AMBER}" font-size="13" class="f" style="animation-delay:{d - .2:.1f}s" xml:space="preserve">{escape(label)}</text>')
        body.append(typed(text, 100, y, d, dur, colr, size=13, cid=f"c{i}"))
    curx = 100 + len(lines[-1][1]) * 13 * .6 + 3
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{MONO}" font-size="{FS}" xml:space="preserve">
<style>text{{white-space:pre}}
{BEAM_CSS}
.row{{animation:fade .2s steps(2) both}}
.f{{animation:fade .3s both}}
.cur{{animation:show 0s 7.2s both,blink 1s steps(1) infinite 7.2s}}@keyframes show{{from{{opacity:0}}}}
@keyframes fade{{from{{opacity:0}}}}
@keyframes type{{from{{width:0}}}}
@keyframes blink{{0%{{opacity:1}}50%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important;opacity:1!important}}}}
</style>
<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>
{chr(10).join(rows)}
{beam(22 + 114 * CW, 24 + 9 * LH, LH, CW, 34, 4, 5, FS)}
<text x="22" y="252" fill="{DIM}" font-size="10" letter-spacing="3" class="f" style="animation-delay:1.4s">AI ENGINEER, IN TRAINING  ·  OPEN TO WORK</text>
<line x1="22" y1="262" x2="{W - 22}" y2="262" stroke="{DIM}" stroke-dasharray="2 4" opacity=".5"/>
{''.join(body)}
<rect x="{curx:.0f}" y="{280 + 3 * 22 - 11}" width="7" height="13" fill="{MINT}" class="cur"/>
</svg>'''


def divider():
    # quiet signal line: dim dashes, one amber packet drifting across
    W = 900
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} 20" width="{W}" height="20" font-family="{MONO}" font-size="12">
<style>.pk{{animation:mv 9s linear infinite}}@keyframes mv{{from{{transform:translateX(0)}}to{{transform:translateX({W - 30}px)}}}}
@media (prefers-reduced-motion:reduce){{.pk{{animation:none}}}}</style>
<line x1="0" y1="10" x2="{W}" y2="10" stroke="{DIM}" stroke-dasharray="3 6" opacity=".45"/>
<text x="0" y="14" fill="{AMBER}" class="pk">·•·</text></svg>'''


def bot():
    # 12x12 pixel robot that blinks and bobs
    art = [
        ".....##.....",
        ".....##.....",
        "..########..",
        ".#........#.",
        ".#.oo..oo.#.",
        ".#.oo..oo.#.",
        ".#........#.",
        ".#..####..#.",
        "..########..",
        "...#....#...",
        "..##....##..",
        "............",
    ]
    px, out = 10, []
    for r, row in enumerate(art):
        for c, ch in enumerate(row):
            if ch == "#":
                out.append(f'<rect x="{c*px}" y="{r*px}" width="{px}" height="{px}" fill="{LILAC}"/>')
            elif ch == "o":
                out.append(f'<rect x="{c*px}" y="{r*px}" width="{px}" height="{px}" fill="{MINT}" class="eye"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="120" height="120">
<style>g{{animation:bob 1.6s steps(2) infinite}}.eye{{animation:bl 4s steps(1) infinite}}
@keyframes bob{{50%{{transform:translateY(4px)}}}}@keyframes bl{{92%{{opacity:1}}96%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{g,.eye{{animation:none}}}}</style>
<g>{''.join(out)}</g></svg>'''


for name, fn in [("header", header), ("divider", divider)]:
    with open(os.path.join(OUT, f"{name}.svg"), "w", encoding="utf-8") as f:
        f.write(fn())
print("wrote", os.listdir(OUT))
