"""Claude Code usage banner, built from the local logs in ~/.claude/projects.
Only totals leave this machine: no project names, prompts or file paths.
Run: python build_usage.py  -> assets/claude-usage.svg   (then commit + push)
"""
import glob, json, os
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from xml.sax.saxutils import escape

DAYS = 30
PAPER, INK, DIM, BLUE = "#FBFBF8", "#111111", "#77777A", "#2D3BFF"
SPECTRUM = ["#FF2E4D", "#FF8A00", "#FFD400", "#22C55E", "#00B8FF", "#2D3BFF", "#C026D3"]
MONO = "ui-monospace, Consolas, 'Courier New', monospace"

now = datetime.now(timezone.utc)
since = (now - timedelta(days=DAYS - 1)).date()
seen, per_day, sessions, models = set(), defaultdict(int), set(), Counter()
out_tokens = 0

for path in glob.glob(os.path.expanduser("~/.claude/projects/**/*.jsonl"), recursive=True):
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            if '"usage"' not in line:
                continue
            try:
                d = json.loads(line)
                u, ts = d["message"]["usage"], d["timestamp"]
            except (ValueError, KeyError, TypeError):
                continue
            key = d.get("requestId") or d.get("uuid")
            if key in seen:
                continue
            seen.add(key)
            day = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone().date()
            if day < since:
                continue
            tok = sum(u.get(k, 0) or 0 for k in ("input_tokens", "output_tokens",
                                                   "cache_creation_input_tokens", "cache_read_input_tokens"))
            per_day[day] += tok
            out_tokens += u.get("output_tokens", 0) or 0
            sessions.add(d.get("sessionId"))
            m = d["message"].get("model", "")
            if m.startswith("claude-"):
                models[m] += 1

days = [since + timedelta(days=i) for i in range(DAYS)]
total = sum(per_day.values())
active = sum(1 for x in days if per_day[x])
streak = 0
for x in reversed(days):
    if not per_day[x]:
        if x == days[-1]:
            continue  # today not started yet doesn't break the streak
        break
    streak += 1


def human(n):
    for unit, div in (("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if n >= div:
            return f"{n / div:.1f}{unit}"
    return str(n)


def model_name(m):
    parts = m.replace("claude-", "").split("-")
    return f"{parts[0]} {'.'.join(parts[1:3])}" if len(parts) >= 3 else m


fav = model_name(models.most_common(1)[0][0]) if models else "—"

# --- render
W, H = 900, 210
peak = max(per_day.values(), default=1) or 1
bars = []
bx, bw, base, maxh = 520, 10, 160, 100
for i, x in enumerate(days):
    h = max(2, per_day[x] / peak * maxh) if per_day[x] else 2
    col = SPECTRUM[i % len(SPECTRUM)] if per_day[x] else "#D9D9D6"
    bars.append(f'<rect x="{bx + i * (bw + 1.5):.1f}" y="{base - h:.1f}" width="{bw}" height="{h:.1f}" fill="{col}" '
                f'class="b" style="animation-delay:{i * .03:.2f}s"/>')

stats = [("tokens", human(total)), ("written", human(out_tokens)), ("sessions", str(len(sessions))),
         ("active days", f"{active}/{DAYS}"), ("streak", f"{streak}d"), ("main model", fav)]
cells = []
for i, (k, v) in enumerate(stats):
    x, y = 30 + (i % 3) * 160, 92 + (i // 3) * 62
    cells.append(f'<text x="{x}" y="{y}" fill="{INK}" font-size="24" font-weight="700">{escape(v)}</text>'
                 f'<text x="{x}" y="{y + 18}" fill="{DIM}" font-size="11" letter-spacing="2">{escape(k.upper())}</text>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{MONO}">
<style>
.b{{transform-box:fill-box;transform-origin:bottom;animation:grow .5s steps(4) both}}@keyframes grow{{from{{transform:scaleY(0)}}}}
.cur{{animation:bl 1s steps(1) infinite}}@keyframes bl{{50%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>
<rect width="{W}" height="{H}" rx="14" fill="{PAPER}"/>
<text x="30" y="40" fill="{INK}" font-size="14">$ claude --usage --last {DAYS}d<tspan class="cur" fill="{BLUE}"> _</tspan></text>
<line x1="30" y1="54" x2="{W - 30}" y2="54" stroke="{DIM}" stroke-dasharray="2 4" opacity=".5"/>
{"".join(cells)}
{"".join(bars)}
<line x1="{bx}" y1="{base + 1}" x2="{bx + DAYS * (bw + 1.5)}" y2="{base + 1}" stroke="{INK}"/>
<text x="{bx}" y="{base + 18}" fill="{DIM}" font-size="10">{since:%b %d}</text>
<text x="{bx + DAYS * (bw + 1.5)}" y="{base + 18}" fill="{DIM}" font-size="10" text-anchor="end">today</text>
<text x="{W - 30}" y="{H - 14}" fill="{DIM}" font-size="10" text-anchor="end">tokens / day · claude code · updated {now.astimezone():%Y-%m-%d}</text>
</svg>'''

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "claude-usage.svg")
with open(out, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"wrote {out}: {human(total)} tokens, {len(sessions)} sessions, {active} active days, streak {streak}d, {fav}")
