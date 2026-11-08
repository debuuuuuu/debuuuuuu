"""3 AM room: blinds, a CRT running a RAG script, cup noodles going cold.
Hand-drawn ASCII, late-90s / early-2000s Tokyo apartment mood.
Run: python build_room.py -> assets/room.svg
"""
import os
from xml.sax.saxutils import escape

BG, INK, DIM, AMBER, LILAC, MINT = "#FBFBF8", "#111111", "#77777A", "#2D3BFF", "#111111", "#22C55E"
FS, LH = 13, 17
CW = FS * 0.6
X0, Y0 = 34, 40

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


ART = r"""
 .--------------------------------.
 |================================|        .----------------------------------.
 |  .  :   . ||  .   .:  |  .  :  |        | .------------------------------. |
 |================================|        | |                              | |
 | .:  |  .  || : . | ||.  .  |:. |        | |                              | |
 |================================|        | |                              | |
 |  || .:|  .||. |  : |||  .:| |  |        | |                              | |
 |================================|        | |                              | |
 | ||||.||| :|||.||||  |||:.||| | |        | |                              | |
 |================================|        | |                              | |
 |__________________||____________|        | '------------------------------' |
                                           |  [o]                     ::::::  |
      _____                                '----------------------------------'
     (_____)                                       /______________\
     |NOODL|                          ____________________________________
     |     |                         [____________________________________]
_____|_____|___________________________________________________________________________
""".strip("\n").split("\n")

SCREEN_X, SCREEN_Y = 47, 3          # first interior column / row of the CRT
# the CRT loops through these sessions, one after another (max 28 chars a line)
SESSIONS = [
    [("$ python rag.py", INK), ("> loading 214 notes ...", DIM), ("> embedding ..... done", DIM),
     ('> q: "am i hireable?"', INK), ("> retrieving ...", AMBER), ("> a: working on it.", MINT)],
    [("$ python rag.py", INK), ('> q: "best chunk size?"', INK), ("> top_k=3 ..... ok", DIM),
     ("> a: 512 tokens, 50 overlap", MINT), ("> src: notes/chunking.md", DIM), ("> _", MINT)],
    [("$ python agent.py", INK), ("> tool: search_jobs()", DIM), ("> found 12 AI roles", AMBER),
     ("> tool: write_cover_letter", DIM), ("> status: 3 drafts saved", MINT), ("> _", MINT)],
    [("$ ollama run llama3", INK), ("> what time is it?", INK), ("> 03:12. go to sleep.", AMBER),
     ("> no.", INK), ("> ...", DIM), ("> fair.", MINT)],
]
SLOT = 9.0                     # seconds each session stays on screen
CYCLE = SLOT * len(SESSIONS)
KF = []
LIGHTS = [(r, c) for r, line in enumerate(ART) for c, ch in enumerate(line[:35]) if ch in ".:" and 2 <= r < 10]


def cx(c): return X0 + c * CW
def cy(r): return Y0 + r * LH


W = int(cx(max(map(len, ART)))) + 34
H = int(cy(len(ART))) + 50
parts = []
for r, line in enumerate(ART):
    parts.append(f'<text x="{X0}" y="{cy(r)}" fill="{LILAC}" opacity=".7" textLength="{len(line) * CW:.1f}" lengthAdjust="spacingAndGlyphs">{escape(line)}</text>')

# city lights through the blinds: a few flicker on their own clocks
for i, (r, c) in enumerate(LIGHTS):
    if i % 4 == 0:
        parts.append(f'<text x="{cx(c):.1f}" y="{cy(r)}" fill="{AMBER}" class="lt" style="animation-delay:{(i * .37) % 5:.2f}s">{ART[r][c]}</text>')

# CRT glow + content typed line by line
sx0, sy0 = cx(SCREEN_X - 1), cy(SCREEN_Y) - LH + 4
parts.append(f'<rect x="{sx0:.0f}" y="{sy0:.0f}" width="{30 * CW:.0f}" height="{7 * LH:.0f}" fill="{AMBER}" opacity=".06" class="glow"/>')
def pct(sec): return f"{sec / CYCLE * 100:.2f}%"


for s, lines in enumerate(SESSIONS):
    a, b = s * SLOT, (s + 1) * SLOT
    # session group is visible only during its slot; first one is the static fallback
    KF.append(f"@keyframes g{s}{{0%,{pct(max(a - .01, 0))}{{opacity:0}}{pct(a)},{pct(b - .3)}{{opacity:1}}{pct(b - .01)},100%{{opacity:0}}}}")
    grp = []
    t = a + .5
    for i, (txt, col) in enumerate(lines):
        w = len(txt) * CW + 4
        dur = len(txt) * .035
        # width 0 until this line starts, types out, then stays
        KF.append(f"@keyframes l{s}_{i}{{0%,{pct(t)}{{width:0}}{pct(t + dur)},100%{{width:{w:.0f}px}}}}")
        grp.append(f'<clipPath id="s{s}_{i}"><rect x="{cx(SCREEN_X)}" y="{cy(SCREEN_Y + i) - FS}" height="{LH}" width="{w:.0f}" '
                   f'style="animation:l{s}_{i} {CYCLE}s steps({len(txt)}) infinite"/></clipPath>')
        grp.append(f'<text x="{cx(SCREEN_X)}" y="{cy(SCREEN_Y + i)}" fill="{col}" textLength="{len(txt) * CW:.1f}" lengthAdjust="spacingAndGlyphs" clip-path="url(#s{s}_{i})">{escape(txt)}</text>')
        t += dur + .5
    base = "" if s == 0 else ' opacity="0"'
    parts.append(f'<g{base} style="animation:g{s} {CYCLE}s steps(1) infinite">{"".join(grp)}</g>')
# scanlines over the screen
for k in range(0, 7 * LH, 3):
    parts.append(f'<rect x="{sx0:.0f}" y="{sy0 + k:.0f}" width="{30 * CW:.0f}" height="1" fill="{BG}" opacity=".35"/>')
# steam off the noodles
for i, (dx, dr) in enumerate([(7, 11), (9, 11), (11, 11)]):
    parts.append(f'<text x="{cx(dx)}" y="{cy(dr)}" fill="{DIM}" class="st" style="animation-delay:{i * .8}s">~</text>')
# the kid at the desk: headphones on, typing, blinking at 3 AM
CX = 24
KID = {11: "  .^^^^^.", 13: r"  \_ _/", 15: "|__|__|"}
for r, t in KID.items():
    parts.append(f'<text x="{cx(CX):.1f}" y="{cy(r)}" fill="{INK}" textLength="{len(t) * CW:.1f}" lengthAdjust="spacingAndGlyphs">{escape(t)}</text>')
# two-frame parts: face (blink) and arm (typing)
for r, frames, klass in [(12, ["[( o_o )]", "[( -_- )]"], "eye"), (14, [r" __|  |\__---", r" __|  |\_--__"], "tap")]:
    for k, t in enumerate(frames):
        op = "" if k == 0 else ' opacity="0"'
        parts.append(f'<text x="{cx(CX):.1f}" y="{cy(r)}" fill="{INK}" class="{klass}{k}"{op} textLength="{len(t) * CW:.1f}" lengthAdjust="spacingAndGlyphs">{escape(t)}</text>')
# power LED
parts.append(f'<text x="{cx(47):.1f}" y="{cy(11)}" fill="{MINT}" class="led">o</text>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"
 font-family="ui-monospace, Consolas, 'Courier New', monospace" font-size="{FS}" xml:space="preserve">
<style>text{{white-space:pre}}
.eye0{{animation:e0 5s steps(1) infinite}}.eye1{{animation:e1 5s steps(1) infinite}}@keyframes e0{{80%{{opacity:0}}88%{{opacity:1}}}}@keyframes e1{{0%{{opacity:0}}80%{{opacity:1}}88%{{opacity:0}}}}
.tap0{{animation:t0 .5s steps(1) infinite}}.tap1{{animation:t1 .5s steps(1) infinite}}@keyframes t0{{50%{{opacity:0}}}}@keyframes t1{{0%{{opacity:0}}50%{{opacity:1}}}}

{BEAM_CSS}
@keyframes type{{from{{width:0}}}}{''.join(KF)}
.lt{{animation:lt 4.3s steps(1) infinite}}@keyframes lt{{0%,70%{{opacity:1}}71%,78%{{opacity:.15}}}}
.glow{{animation:gl 3s ease-in-out infinite}}@keyframes gl{{50%{{opacity:.1}}}}
.st{{opacity:.6;animation:st 2.4s ease-out infinite}}@keyframes st{{0%{{opacity:0}}30%{{opacity:.8}}100%{{opacity:0;transform:translateY(-8px)}}}}
.led{{animation:led 2s steps(1) infinite}}@keyframes led{{50%{{opacity:.3}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.st{{opacity:.6}}}}
</style>
<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>
{chr(10).join(parts)}
{beam(cx(35), cy(4), LH, CW, 8, 5, 9, FS)}
<text x="{X0}" y="{H - 18}" fill="{DIM}" font-size="11" letter-spacing="2">03:12 AM  ·  ROOM 201  ·  STILL RETRIEVING</text>
</svg>'''

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "room.svg")
with open(out, "w", encoding="utf-8") as f:
    f.write(svg)
print("wrote", out, W, H)
