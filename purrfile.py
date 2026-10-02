#!/usr/bin/env python3
"""PurrFileGenerator - generate a clean animated SVG stats card for any GitHub profile.

No third-party dependencies: only the Python standard library.
Features: 15 themes · 15 palettes · dark/light mode · animations · streak counter · compact mode
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from html import escape

API = "https://api.github.com"

# ══════════════════════════════════════════════════════════════════════════════
# Icon themes  (all use style= so CSS variables work)
# ══════════════════════════════════════════════════════════════════════════════

def _icon_cat(x, y, s, c):
    return (f'<g transform="translate({x},{y}) scale({s})" style="fill:{c}">'
            '<ellipse cx="0" cy="6" rx="6.5" ry="5.5"/>'
            '<ellipse cx="-6.5" cy="-2.5" rx="2.4" ry="3"/>'
            '<ellipse cx="-2.5" cy="-6.5" rx="2.4" ry="3"/>'
            '<ellipse cx="2.5" cy="-6.5" rx="2.4" ry="3"/>'
            '<ellipse cx="6.5" cy="-2.5" rx="2.4" ry="3"/></g>')

def _icon_robot(x, y, s, c):
    return (f'<g transform="translate({x},{y}) scale({s})" style="fill:none;stroke:{c};stroke-width:1.6">'
            '<rect x="-7" y="-4" width="14" height="11" rx="3"/>'
            f'<circle cx="-3" cy="1" r="1.4" style="fill:{c}"/>'
            f'<circle cx="3" cy="1" r="1.4" style="fill:{c}"/>'
            '<line x1="0" y1="-4" x2="0" y2="-8"/>'
            f'<circle cx="0" cy="-9" r="1.4" style="fill:{c}"/></g>')

def _icon_space(x, y, s, c):
    return (f'<g transform="translate({x},{y}) scale({s})" style="fill:{c}">'
            '<path d="M0,-9 L2.2,-2.6 L9,-2.2 L3.6,2 L5.4,8.6 L0,4.8 L-5.4,8.6 L-3.6,2 L-9,-2.2 L-2.2,-2.6 Z"/></g>')

def _icon_wave(x, y, s, c):
    return (f'<g transform="translate({x},{y}) scale({s})" style="fill:none;stroke:{c};stroke-width:2;stroke-linecap:round">'
            '<path d="M-9,2 Q-5,-6 0,2 T9,2"/>'
            f'<path d="M-9,7 Q-5,-1 0,7 T9,7" stroke-opacity="0.5"/></g>')

def _icon_terminal(x, y, s, c):
    return (f'<g transform="translate({x},{y}) scale({s})" style="fill:none;stroke:{c};stroke-width:1.8;stroke-linecap:round">'
            '<path d="M-8,-6 L-2,0 L-8,6"/>'
            '<line x1="1" y1="6" x2="8" y2="6"/></g>')

def _icon_leaf(x, y, s, c):
    return (f'<g transform="translate({x},{y}) scale({s})" style="fill:{c}">'
            '<path d="M0,9 C-9,7 -9,-7 0,-9 C9,-7 9,7 0,9 Z"/>'
            '<line x1="0" y1="9" x2="0" y2="-9" stroke="#0006" stroke-width="1" style="fill:none"/></g>')

def _icon_coffee(x, y, s, c):
    return (f'<g transform="translate({x},{y}) scale({s})" style="fill:none;stroke:{c};stroke-width:1.7">'
            '<path d="M-7,-3 h11 v6 a5.5,5.5 0 0 1 -5.5,5.5 h0 A5.5,5.5 0 0 1 -7,3 Z"/>'
            '<path d="M4,-1 q4,0 4,3 q0,3 -4,3"/>'
            '<path d="M-3,-6 q1,-2 0,-4" stroke-linecap="round"/>'
            '<path d="M1,-6 q1,-2 0,-4" stroke-linecap="round"/></g>')

def _icon_pixel(x, y, s, c):
    coords = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]
    r = 2.6
    rects = "".join(f'<rect x="{cx*6-r}" y="{cy*6-r}" width="{r*2}" height="{r*2}"/>' for cx, cy in coords)
    return f'<g transform="translate({x},{y}) scale({s})" style="fill:{c}">{rects}</g>'

def _icon_music(x, y, s, c):
    bars = [(-8,4),(-3,8),(2,3),(7,7)]
    rects = "".join(f'<rect x="{bx-1.5}" y="{-h}" width="3" height="{h*2}" rx="1.5"/>' for bx, h in bars)
    return f'<g transform="translate({x},{y}) scale({s})" style="fill:{c}">{rects}</g>'

def _icon_weather(x, y, s, c):
    return (f'<g transform="translate({x},{y}) scale({s})">'
            f'<g style="fill:{c}"><ellipse cx="-3" cy="0" rx="5" ry="4"/>'
            f'<ellipse cx="3" cy="-1" rx="6" ry="5"/><ellipse cx="8" cy="1" rx="4" ry="3.2"/></g>'
            '<path d="M1,7 L-2,13 L1,13 L-1,18" style="fill:none;stroke:#facc15;stroke-width:1.8;stroke-linecap:round"/></g>')

def _icon_book(x, y, s, c):
    return (f'<g transform="translate({x},{y}) scale({s})" style="fill:none;stroke:{c};stroke-width:1.7">'
            '<path d="M0,-6 C-3,-8 -8,-8 -9,-6 L-9,7 C-8,5 -3,5 0,7 Z"/>'
            '<path d="M0,-6 C3,-8 8,-8 9,-6 L9,7 C8,5 3,5 0,7 Z"/></g>')

def _icon_fire(x, y, s, c):
    return (f'<g transform="translate({x},{y}) scale({s})" style="fill:{c}">'
            '<path d="M0,-9 C4,-4 6,-1 4,3 C7,1 8,-2 8,-2 C9,4 5,9 -1,9 C-7,9 -9,3 -6,-1 '
            'C-5,1 -3,1 -3,-1 C-4,-4 -2,-7 0,-9 Z"/></g>')

def _icon_snow(x, y, s, c):
    lines = "".join(
        f'<line x1="0" y1="-9" x2="0" y2="9" transform="rotate({a})"/>'
        for a in (0, 60, 120)
    )
    return f'<g transform="translate({x},{y}) scale({s})" style="fill:none;stroke:{c};stroke-width:1.6">{lines}</g>'

def _icon_dragon(x, y, s, c):
    return (f'<g transform="translate({x},{y}) scale({s})" style="fill:{c}">'
            '<path d="M-9,4 L-4,-8 L-1,-1 L3,-9 L6,0 L9,-6 L7,5 C3,8 -5,8 -9,4 Z"/></g>')

def _icon_rainbow(x, y, s, c):  # noqa: ARG001  (c ignored – rainbow uses own colors)
    cols = ["#f87171","#fbbf24","#4ade80","#38bdf8","#a78bfa"]
    arcs = "".join(
        f'<path d="M-9,{4-i*2} A{9-i*1.5},{9-i*1.5} 0 0 1 9,{4-i*2}" '
        f'style="fill:none;stroke:{col};stroke-width:1.8"/>'
        for i, col in enumerate(cols)
    )
    return f'<g transform="translate({x},{y}) scale({s})">{arcs}</g>'

THEMES = {
    "cat": _icon_cat, "robot": _icon_robot, "space": _icon_space,
    "ocean": _icon_wave, "terminal": _icon_terminal, "plant": _icon_leaf,
    "coffee": _icon_coffee, "gaming": _icon_pixel, "music": _icon_music,
    "weather": _icon_weather, "book": _icon_book, "fire": _icon_fire,
    "ice": _icon_snow, "dragon": _icon_dragon, "rainbow": _icon_rainbow,
}

# ══════════════════════════════════════════════════════════════════════════════
# Palettes  (dark + light variants + palette-matched language bar colors)
# ══════════════════════════════════════════════════════════════════════════════

# Format per palette:
#   "dark":  (bg1, bg2, ac1, ac2, text_main, text_dim)
#   "light": (bg1, bg2, ac1, ac2, text_main, text_dim)
#   "langs": [color0, color1, color2, color3, color4]
PALETTES = {
    "lavender": {
        "dark":  ("#150f23","#0d1117","#c084fc","#f472b6","#f5f3ff","#a78bfa"),
        "light": ("#f5f3ff","#ede9fe","#7c3aed","#be185d","#1e1b4b","#5b21b6"),
        "langs": ["#c084fc","#f472b6","#818cf8","#e879f9","#a78bfa"],
    },
    "tuxedo": {
        "dark":  ("#1a1a1a","#0a0a0a","#e6e6e6","#9e9e9e","#ffffff","#bdbdbd"),
        "light": ("#ffffff","#f5f5f5","#1a1a1a","#616161","#0a0a0a","#424242"),
        "langs": ["#e6e6e6","#a3a3a3","#737373","#d4d4d4","#525252"],
    },
    "tabby": {
        "dark":  ("#3a1f0f","#1f1008","#fb923c","#fbbf24","#fff7ed","#fdba74"),
        "light": ("#fff7ed","#ffedd5","#c2410c","#b45309","#431407","#9a3412"),
        "langs": ["#fb923c","#fbbf24","#f97316","#facc15","#ea580c"],
    },
    "calico": {
        "dark":  ("#241a12","#0f0a06","#f97316","#111827","#fef3e2","#e2b98a"),
        "light": ("#fef3e2","#fed7aa","#c2410c","#374151","#431407","#7c2d12"),
        "langs": ["#f97316","#fb923c","#ea580c","#fbbf24","#c2410c"],
    },
    "siamese": {
        "dark":  ("#2b241c","#171310","#d6a06b","#8b5e34","#fdf6ec","#c9a274"),
        "light": ("#fdf6ec","#fde8c8","#92400e","#78350f","#1c0a00","#713f12"),
        "langs": ["#d6a06b","#c9a274","#b45309","#f59e0b","#92400e"],
    },
    "neon": {
        "dark":  ("#0a0018","#020009","#22d3ee","#e879f9","#f0f9ff","#67e8f9"),
        "light": ("#f0f9ff","#e0f2fe","#0891b2","#a21caf","#0c0a1e","#0e7490"),
        "langs": ["#22d3ee","#e879f9","#34d399","#f472b6","#818cf8"],
    },
    "midnight": {
        "dark":  ("#0b1020","#05070f","#facc15","#eab308","#fff9e6","#fde68a"),
        "light": ("#fff9e6","#fef9c3","#a16207","#92400e","#0b1020","#854d0e"),
        "langs": ["#facc15","#eab308","#fbbf24","#f59e0b","#d97706"],
    },
    "pastel": {
        "dark":  ("#241b2e","#150f1c","#f9a8d4","#6ee7b7","#fdf2f8","#f5c2dd"),
        "light": ("#fdf2f8","#fce7f3","#be185d","#059669","#1a0311","#9d174d"),
        "langs": ["#f9a8d4","#6ee7b7","#c4b5fd","#fde68a","#a5f3fc"],
    },
    "autumn": {
        "dark":  ("#2c1508","#170a03","#ea580c","#f59e0b","#fff1e6","#fdba74"),
        "light": ("#fff1e6","#ffedd5","#c2410c","#b45309","#3b0a00","#9a3412"),
        "langs": ["#ea580c","#f59e0b","#dc2626","#d97706","#b45309"],
    },
    "grayscale": {
        "dark":  ("#1c1c1c","#0e0e0e","#d4d4d4","#8a8a8a","#f5f5f5","#b0b0b0"),
        "light": ("#f5f5f5","#e5e5e5","#404040","#525252","#0a0a0a","#525252"),
        "langs": ["#d4d4d4","#a3a3a3","#737373","#e5e5e5","#525252"],
    },
    "ocean": {
        "dark":  ("#031826","#010d16","#22d3ee","#0ea5e9","#ecfeff","#7dd3fc"),
        "light": ("#ecfeff","#cffafe","#0e7490","#0369a1","#0c1a2e","#0891b2"),
        "langs": ["#22d3ee","#0ea5e9","#38bdf8","#06b6d4","#0284c7"],
    },
    "sakura": {
        "dark":  ("#241019","#12080d","#fda4c7","#f472b6","#fff0f5","#f9c9d9"),
        "light": ("#fff0f5","#fce7f3","#be185d","#9d174d","#1a0311","#831843"),
        "langs": ["#fda4c7","#f472b6","#fb7185","#e879f9","#f9a8d4"],
    },
    "forest": {
        "dark":  ("#0f1f14","#08120c","#4ade80","#a3e635","#f0fdf4","#86efac"),
        "light": ("#f0fdf4","#dcfce7","#15803d","#4d7c0f","#052e16","#166534"),
        "langs": ["#4ade80","#a3e635","#34d399","#86efac","#22c55e"],
    },
    "sunset": {
        "dark":  ("#2a1030","#160819","#fb7185","#f59e0b","#fff1f2","#fda4af"),
        "light": ("#fff1f2","#ffe4e6","#be123c","#b45309","#1a0311","#9f1239"),
        "langs": ["#fb7185","#f59e0b","#f472b6","#fbbf24","#e11d48"],
    },
    "classic": {
        "dark":  ("#0d1117","#0d1117","#58a6ff","#3fb950","#e6edf3","#8b949e"),
        "light": ("#ffffff","#f6f8fa","#0969da","#1a7f37","#1f2328","#636c76"),
        "langs": ["#58a6ff","#3fb950","#f78166","#d2a8ff","#ffa657"],
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# Data fetching
# ══════════════════════════════════════════════════════════════════════════════

def fetch_json(url, token=None):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "purrfile"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as err:
        if err.code == 404:
            sys.exit("User not found.")
        if err.code == 403:
            sys.exit("Rate limit reached. Set a GITHUB_TOKEN environment variable.")
        sys.exit(f"GitHub API error {err.code}: {err.reason}")
    except urllib.error.URLError as err:
        sys.exit(f"Network error: {err.reason}")
    except OSError as err:
        sys.exit(f"Connection error: {err}")


def fetch_repos(username, token=None):
    repos, page = [], 1
    while True:
        batch = fetch_json(
            f"{API}/users/{username}/repos?per_page=100&page={page}&type=owner", token
        )
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return repos


def fetch_streak(username, token=None):
    """Current commit streak (days) via events API — max ~90 days history."""
    try:
        events = fetch_json(f"{API}/users/{username}/events?per_page=100", token) or []
    except SystemExit:
        return 0
    push_dates = {
        e["created_at"][:10]
        for e in events
        if e.get("type") == "PushEvent"
    }
    today = date.today()
    # Start from today; if no commit today, start from yesterday
    start = today if str(today) in push_dates else today - timedelta(days=1)
    streak, day = 0, start
    while str(day) in push_dates:
        streak += 1
        day -= timedelta(days=1)
    return streak


def summarize(repos, streak=0, include_forks=False):
    if not include_forks:
        repos = [r for r in repos if not r.get("fork")]
    langs = Counter(r["language"] for r in repos if r.get("language"))
    return {
        "repos":     len(repos),
        "stars":     sum(r.get("stargazers_count", 0) for r in repos),
        "forks":     sum(r.get("forks_count", 0) for r in repos),
        "issues":    sum(r.get("open_issues_count", 0) for r in repos),
        "streak":    streak,
        "languages": langs.most_common(5),
    }

# ══════════════════════════════════════════════════════════════════════════════
# SVG rendering helpers
# ══════════════════════════════════════════════════════════════════════════════

def _css(dark, light, langs):
    """CSS block: variables for dark/light mode + keyframe animations."""
    d, l, lc = dark, light, langs
    return (
        "<style>"
        ":root{"
        f"--bg1:{d[0]};--bg2:{d[1]};--ac1:{d[2]};--ac2:{d[3]};--tm:{d[4]};--td:{d[5]};"
        f"--lc0:{lc[0]};--lc1:{lc[1]};--lc2:{lc[2]};--lc3:{lc[3]};--lc4:{lc[4]};"
        "}"
        "@media(prefers-color-scheme:light){"
        ":root{"
        f"--bg1:{l[0]};--bg2:{l[1]};--ac1:{l[2]};--ac2:{l[3]};--tm:{l[4]};--td:{l[5]};"
        "}"
        "}"
        ".tm{fill:var(--tm)}.td{fill:var(--td)}"
        ".lc0{fill:var(--lc0)}.lc1{fill:var(--lc1)}.lc2{fill:var(--lc2)}"
        ".lc3{fill:var(--lc3)}.lc4{fill:var(--lc4)}"
        "@keyframes fadeUp{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}"
        "@keyframes fadeIn{from{opacity:0}to{opacity:1}}"
        ".s0{animation:fadeUp .5s ease .05s}"
        ".s1{animation:fadeUp .5s ease .15s}"
        ".s2{animation:fadeUp .5s ease .25s}"
        ".s3{animation:fadeUp .5s ease .38s}"
        ".s4{animation:fadeUp .5s ease .50s}"
        ".ll{animation:fadeIn .6s ease .9s}"
        ".ft{animation:fadeIn .6s ease 1.1s}"
        "</style>"
    )


def _today():
    d = datetime.now(timezone.utc)
    return f"{d.day} {d.strftime('%b %Y')}"

# ══════════════════════════════════════════════════════════════════════════════
# Full card (495 × 280)
# ══════════════════════════════════════════════════════════════════════════════

def render_svg(username, stats, theme="cat", palette="lavender", accent=None):
    icon = THEMES.get(theme, _icon_cat)
    pal  = PALETTES.get(palette, PALETTES["lavender"])
    dark  = list(pal["dark"])
    light = list(pal["light"])
    langs = pal["langs"]

    if accent:
        dark[2] = dark[3] = accent
        light[2] = light[3] = accent

    F    = "Segoe UI, Arial, sans-serif"
    W, H = 495, 295
    BX, BW, BY = 30, 435, 200   # bar x, width, y

    lang_data = stats["languages"]
    total = sum(c for _, c in lang_data) or 1

    defs = [
        "<defs>",
        _css(dark, light, langs),
        '<linearGradient id="g-bg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" style="stop-color:var(--bg1)"/>'
        '<stop offset="1" style="stop-color:var(--bg2)"/></linearGradient>',
        '<linearGradient id="g-ac" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" style="stop-color:var(--ac1)"/>'
        '<stop offset="1" style="stop-color:var(--ac2)"/></linearGradient>',
        # clip: rounds bar corners
        f'<clipPath id="bc"><rect x="{BX}" y="{BY}" width="{BW}" height="10" rx="5"/></clipPath>',
        # animated clip: bar grows left→right
        f'<clipPath id="ba"><rect x="{BX}" y="{BY}" height="10">'
        f'<animate attributeName="width" from="0" to="{BW}" dur="1.2s" begin="0.6s" fill="freeze" '
        f'calcMode="spline" keySplines="0.4 0 0.2 1" keyTimes="0;1"/></rect></clipPath>',
        "</defs>",
    ]

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"'
        f' viewBox="0 0 {W} {H}" role="img" aria-label="{escape(username)} GitHub stats">',
        f'<title>{escape(username)} on GitHub — purrfile</title>',
        *defs,
        # card background + border
        f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="url(#g-bg)"'
        ' style="stroke:var(--ac1)" stroke-opacity=".28"/>',
        # theme icon top-right
        icon(453, 34, 1.3, "var(--ac1)"),
        # username heading
        f'<text x="30" y="42" font-family="{F}" font-size="19" font-weight="700" class="tm">'
        f'{escape(username)} on GitHub</text>',
        f'<rect x="30" y="54" width="46" height="3" rx="1.5" fill="url(#g-ac)"/>',
    ]

    # ── Stats row 1: Repos · Stars · Forks ──────────────────────────────────
    for i, (lbl, val) in enumerate([("Repos", stats["repos"]),
                                     ("Stars", stats["stars"]),
                                     ("Forks", stats["forks"])]):
        x = 30 + i * 150
        p += [
            f'<text x="{x}" y="100" font-family="{F}" font-size="28" font-weight="700" class="tm s{i}">{val}</text>',
            f'<text x="{x}" y="118" font-family="{F}" font-size="12" class="td s{i}">{lbl}</text>',
        ]

    # ── Stats row 2: Issues · Streak ────────────────────────────────────────
    for i, (lbl, val) in enumerate([("Open Issues", stats["issues"]),
                                     ("Commit Streak", f'{stats["streak"]}d')]):
        x = 30 + i * 218
        p += [
            f'<text x="{x}" y="148" font-family="{F}" font-size="22" font-weight="700" class="tm s{i+3}">{val}</text>',
            f'<text x="{x}" y="163" font-family="{F}" font-size="11" class="td s{i+3}">{lbl}</text>',
        ]

    # ── Language bar ─────────────────────────────────────────────────────────
    p += [
        f'<text x="{BX}" y="{BY-10}" font-family="{F}" font-size="12" class="td">Languages</text>',
        '<g clip-path="url(#bc)"><g clip-path="url(#ba)">',
        f'<rect x="{BX}" y="{BY}" width="{BW}" height="10" style="fill:var(--bg1)"/>',
    ]
    cum = 0.0
    for i, (_, cnt) in enumerate(lang_data):
        frac = cnt / total
        xs   = BX + BW * cum
        w    = BW * frac
        p.append(f'<rect x="{xs:.2f}" y="{BY}" width="{w:.2f}" height="10" class="lc{i%5}"/>')
        cum += frac
    p.append("</g></g>")

    # ── Language legend ───────────────────────────────────────────────────────
    p.append('<g class="ll">')
    for i, (name, cnt) in enumerate(lang_data):
        x  = 30 + (i % 3) * 150
        y  = BY + 32 + (i // 3) * 24
        pct = round(100 * cnt / total)
        p.append(icon(x + 6, y - 4, 0.55, f"var(--lc{i%5})"))
        p.append(f'<text x="{x+18}" y="{y}" font-family="{F}" font-size="12" class="td">'
                 f'{escape(name)} {pct}%</text>')
    p.append("</g>")

    # ── Footer ────────────────────────────────────────────────────────────────
    p.append(
        f'<text x="{W-14}" y="{H-10}" font-family="{F}" font-size="10"'
        f' class="td ft" text-anchor="end" opacity=".6">purrfile · {_today()}</text>'
    )
    p.append("</svg>")
    return "\n".join(p)

# ══════════════════════════════════════════════════════════════════════════════
# Compact card (300 × 155) — side-by-side README layout
# ══════════════════════════════════════════════════════════════════════════════

def render_compact(username, stats, theme="cat", palette="lavender", accent=None):
    icon = THEMES.get(theme, _icon_cat)
    pal  = PALETTES.get(palette, PALETTES["lavender"])
    dark  = list(pal["dark"])
    light = list(pal["light"])
    langs = pal["langs"]

    if accent:
        dark[2] = dark[3] = accent
        light[2] = light[3] = accent

    F    = "Segoe UI, Arial, sans-serif"
    W, H = 300, 155
    BX, BW, BY = 18, 264, 96

    lang_data = stats["languages"]
    total = sum(c for _, c in lang_data) or 1

    defs = [
        "<defs>",
        _css(dark, light, langs),
        '<linearGradient id="g-bg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" style="stop-color:var(--bg1)"/>'
        '<stop offset="1" style="stop-color:var(--bg2)"/></linearGradient>',
        '<linearGradient id="g-ac" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" style="stop-color:var(--ac1)"/>'
        '<stop offset="1" style="stop-color:var(--ac2)"/></linearGradient>',
        f'<clipPath id="bc"><rect x="{BX}" y="{BY}" width="{BW}" height="8" rx="4"/></clipPath>',
        f'<clipPath id="ba"><rect x="{BX}" y="{BY}" height="8">'
        f'<animate attributeName="width" from="0" to="{BW}" dur="1.1s" begin="0.4s" fill="freeze"/>'
        '</rect></clipPath>',
        "</defs>",
    ]

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"'
        f' viewBox="0 0 {W} {H}" role="img" aria-label="{escape(username)} GitHub stats compact">',
        f'<title>{escape(username)} on GitHub — purrfile compact</title>',
        *defs,
        f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="url(#g-bg)"'
        ' style="stroke:var(--ac1)" stroke-opacity=".28"/>',
        icon(272, 20, 1.0, "var(--ac1)"),
        f'<text x="18" y="26" font-family="{F}" font-size="14" font-weight="700" class="tm">'
        f'{escape(username)}</text>',
        f'<rect x="18" y="32" width="30" height="2.5" rx="1.2" fill="url(#g-ac)"/>',
    ]

    # 4 compact stats in one row
    col_w = (W - 36) // 4
    for i, (lbl, val) in enumerate([
        ("Repos",  stats["repos"]),
        ("Stars",  stats["stars"]),
        ("Forks",  stats["forks"]),
        ("Streak", f'{stats["streak"]}d'),
    ]):
        x = 18 + i * col_w
        p += [
            f'<text x="{x}" y="60" font-family="{F}" font-size="17" font-weight="700" class="tm s{i}">{val}</text>',
            f'<text x="{x}" y="73" font-family="{F}" font-size="9.5" class="td s{i}">{lbl}</text>',
        ]

    # bar
    p += [
        f'<text x="{BX}" y="{BY-6}" font-family="{F}" font-size="9.5" class="td">Languages</text>',
        '<g clip-path="url(#bc)"><g clip-path="url(#ba)">',
        f'<rect x="{BX}" y="{BY}" width="{BW}" height="8" style="fill:var(--bg1)"/>',
    ]
    cum = 0.0
    for i, (_, cnt) in enumerate(lang_data):
        frac = cnt / total
        xs, w = BX + BW * cum, BW * frac
        p.append(f'<rect x="{xs:.2f}" y="{BY}" width="{w:.2f}" height="8" class="lc{i%5}"/>')
        cum += frac
    p.append("</g></g>")

    # compact legend: up to 3, circles instead of icons
    p.append('<g class="ll">')
    for i, (name, cnt) in enumerate(lang_data[:3]):
        x   = 18 + i * 90
        y   = BY + 24
        pct = round(100 * cnt / total)
        p.append(f'<circle cx="{x+4}" cy="{y-3}" r="3.5" class="lc{i%5}"/>')
        p.append(f'<text x="{x+12}" y="{y}" font-family="{F}" font-size="9.5" class="td">'
                 f'{escape(name)} {pct}%</text>')
    p.append("</g>")

    p.append(
        f'<text x="{W-10}" y="{H-6}" font-family="{F}" font-size="8"'
        f' class="td ft" text-anchor="end" opacity=".55">purrfile · {_today()}</text>'
    )
    p.append("</svg>")
    return "\n".join(p)

# ══════════════════════════════════════════════════════════════════════════════
# Markdown fallback
# ══════════════════════════════════════════════════════════════════════════════

def render_markdown(username, stats):
    lines = [
        f"### {username} on GitHub",
        "",
        f"- Repos: **{stats['repos']}** · Stars: **{stats['stars']}** · "
        f"Forks: **{stats['forks']}** · Issues: **{stats['issues']}** · "
        f"Streak: **{stats['streak']}d**",
    ]
    if stats["languages"]:
        lines.append("- Top languages: " + ", ".join(n for n, _ in stats["languages"]))
    return "\n".join(lines)

# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

def main(argv=None):
    p = argparse.ArgumentParser(
        description="Generate an animated SVG stats card for a GitHub profile."
    )
    p.add_argument("username", nargs="?", help="GitHub username")
    p.add_argument("-o", "--output",  default="purrfile.svg",
                   help="Output SVG file (default: purrfile.svg)")
    p.add_argument("--theme",   choices=sorted(THEMES),   default="cat",
                   help="Icon theme (default: cat)")
    p.add_argument("--palette", choices=sorted(PALETTES), default="lavender",
                   help="Color palette (default: lavender)")
    p.add_argument("--accent",  metavar="#RRGGBB",
                   help="Override accent color with a custom hex value")
    p.add_argument("--compact", action="store_true",
                   help="Generate compact 300×155 card instead of full 495×280")
    p.add_argument("--include-forks", action="store_true",
                   help="Include forked repositories in stats")
    p.add_argument("--markdown", action="store_true",
                   help="Also print a Markdown summary to stdout")
    p.add_argument("--save-cache", metavar="FILE", default=None,
                   help="Save fetched stats as JSON for offline use")
    p.add_argument("--from-cache", metavar="FILE", default=None,
                   help="Load stats from a previously saved JSON cache")
    p.add_argument("--list-themes",   action="store_true",
                   help="List all available themes and exit")
    p.add_argument("--list-palettes", action="store_true",
                   help="List all available palettes and exit")
    args = p.parse_args(argv)

    if args.list_themes:
        print("Available themes:\n  " + "  ".join(sorted(THEMES)))
        return
    if args.list_palettes:
        print("Available palettes:\n  " + "  ".join(sorted(PALETTES)))
        return

    if not args.username:
        p.error("username is required unless using --list-themes or --list-palettes")

    token = os.environ.get("GITHUB_TOKEN")

    # ── Load or fetch stats ──────────────────────────────────────────────────
    if args.from_cache:
        with open(args.from_cache, encoding="utf-8") as f:
            stats = json.load(f)
        print(f"Stats loaded from cache: {args.from_cache}")
    else:
        repos  = fetch_repos(args.username, token)
        streak = fetch_streak(args.username, token)
        stats  = summarize(repos, streak, args.include_forks)

    if args.save_cache:
        with open(args.save_cache, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
        print(f"Stats saved to cache: {args.save_cache}")

    # ── Render ───────────────────────────────────────────────────────────────
    if args.compact:
        svg = render_compact(args.username, stats,
                             theme=args.theme, palette=args.palette, accent=args.accent)
    else:
        svg = render_svg(args.username, stats,
                         theme=args.theme, palette=args.palette, accent=args.accent)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Card saved → {args.output}")

    if args.markdown:
        print()
        print(render_markdown(args.username, stats))


if __name__ == "__main__":
    main()
