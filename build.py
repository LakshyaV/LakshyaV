#!/usr/bin/env python3
"""Generate the SVG assets for the profile README.

    python3 build.py

Every image is written twice, for GitHub's light and dark themes; the README
picks one with <picture> and prefers-color-scheme. To change a card, edit
CARDS below and run this again.
"""
import json
import math
import os
import random

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

THEMES = {
    "dark": dict(text="#f0f6fc", soft="#9198a1", faint="#3d444d", line="#30363d", accent="#ff7b54", card="#0d1117"),
    "light": dict(text="#1f2328", soft="#59636e", faint="#c8d1da", line="#d1d9e0", accent="#cf4a1c", card="#ffffff"),
}

CARDS = [
    dict(slug="compiler", kind="compilers", title="self-hosting-compiler",
         lines=["A language whose compiler compiles itself to x86-64.",
                "Type inference, SSA, graph-colouring register",
                "allocation, raw ELF output. No LLVM."],
         tags="x86-64 / SSA / ELF"),
    dict(slug="inference", kind="inference", title="llm-inference-engine",
         lines=["LLM inference for Apple GPUs, from scratch: C++ and",
                "hand-written Metal kernels. Runs int4 Qwen2.5 at",
                "speeds comparable to llama.cpp."],
         tags="C++ / Metal"),
    dict(slug="speech", kind="wearables", title="silent-speech-jaw",
         lines=["Mouth a sentence without a sound. Two IMUs on the",
                "jaw, a phoneme recogniser and a local LLM turn the",
                "movement into text, down to an Arduino."],
         tags="Python / ONNX / Arduino"),
    dict(slug="bitwidth", kind="research", title="critical bit-width of superposition",
         lines=["Does packing more features per dimension need more",
                "bits? A preregistered closed-form law, tested in toy",
                "models and bridged to GPT-2 small."],
         tags="PyTorch / TeX"),
    dict(slug="morphos", kind="artificial life", title="MORPHOS",
         lines=["Neural cellular automata grow from one cell, invent",
                "a symbol protocol, then get cut open. Does the",
                "convention come back with the body?"],
         tags="Python"),
    dict(slug="wheelchair", kind="brain-computer interfaces", title="neuro-wheelchair",
         lines=["A wheelchair steered by EEG. Signals from a Muse",
                "headset are classified in real time and drive the",
                "motors through an Arduino."],
         tags="Python / Arduino"),
]


def trace(width, mid, seed=7):
    """A decorative line: a noisy wave that settles into steps and then flat."""
    rng = random.Random(seed)
    pts = []
    x = 0.0
    analog_end = width * 0.46
    digital_end = width * 0.80
    phase = rng.random() * 6
    while x < analog_end:
        fade = 1 - (x / analog_end) ** 2.2
        y = (math.sin(x * 0.055 + phase) * 9 + math.sin(x * 0.19) * 6 + rng.uniform(-7, 7)) * fade
        if rng.random() < 0.035:
            y -= rng.uniform(14, 24) * fade          # the occasional spike
        pts.append((x, mid + y))
        x += 4.0
    d = "M" + " L".join("%.1f %.1f" % p for p in pts)
    # square wave with shrinking amplitude
    amp = 11.0
    step = 26.0
    up = True
    x = analog_end
    d += " L%.1f %.1f" % (x, mid)
    while x + step < digital_end:
        y = mid - amp if up else mid
        d += " V%.1f H%.1f" % (y, x + step)
        x += step
        if not up:
            amp *= 0.82
        up = not up
        step = rng.choice([26.0, 26.0, 52.0])
    d += " V%.1f H%.1f" % (mid, width - 14)
    return d, width - 14


DAYS = 182      # how much history the header line covers
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "contributions.json")


def activity(width, base, height):
    """The header line drawn from real data: one point per day, height from
    that day's contribution count. Returns None when there is no data file
    (run fetch.sh to make one), and the decorative trace is used instead."""
    if not os.path.exists(DATA):
        return None
    with open(DATA) as f:
        counts = [d["count"] for d in json.load(f)][-DAYS:]
    if len(counts) < 2 or max(counts) == 0:
        return None
    # Square-root scale, clipped at the 90th percentile, so a few huge days
    # do not flatten all the others.
    busy = sorted(n for n in counts if n > 0)
    top = math.sqrt(busy[int(len(busy) * 0.9)])
    ys = [base - min(1.0, math.sqrt(n) / top) * height for n in counts]
    end_x = width - 14
    step = end_x / (len(counts) - 1)
    pts = ["%.1f %.1f" % (i * step, y) for i, y in enumerate(ys)]
    return "M" + " L".join(pts), end_x, ys[-1]


def header(theme):
    c = THEMES[theme]
    w, h = 840, 262
    mid = 232
    real = activity(w, mid, 50)
    if real:
        d, end_x, end_y = real
        caption = f'<text class="cap rise" x="2" y="{h - 6}" style="animation-delay:.6s">my commits per day, last 6 months</text>'
    else:
        d, end_x = trace(w, mid - 10)
        end_y = mid - 10
        caption = ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Lakshya Vasudeva. Started coding at 7 and teaching at 8. Interned at Zebra Technologies, worked with Interac, researched at Harvard. Now building Origin, a wearable to talk to your AI agents telepathically.">
  <style>
    .name {{ font: 600 54px {SANS}; letter-spacing: -1.6px; fill: {c['text']}; }}
    .bio {{ font: 400 17px {SANS}; fill: {c['soft']}; }}
    .bio tspan {{ fill: {c['text']}; }}
    .cap {{ font: 400 11px {MONO}; letter-spacing: 0.3px; fill: {c['soft']}; }}
    .trace {{ fill: none; stroke: {c['accent']}; stroke-width: 1.5; stroke-linejoin: round; stroke-linecap: round;
             stroke-dasharray: 6000; animation: draw 3.2s cubic-bezier(.3,.1,.2,1) .2s backwards; }}
    .rise {{ animation: rise .9s ease-out backwards; }}
    .dot {{ fill: {c['accent']}; animation: show .3s linear 3.3s backwards, pulse 1.8s ease-in-out 3.6s infinite; }}
    /* Everything rests in its final state, so a renderer that does not
       animate still shows the finished picture. */
    @keyframes draw {{ from {{ stroke-dashoffset: 6000; }} to {{ stroke-dashoffset: 0; }} }}
    @keyframes rise {{ from {{ opacity: 0; transform: translateY(8px); }} }}
    @keyframes show {{ from {{ opacity: 0; }} }}
    @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: .25; }} }}
    @media (prefers-reduced-motion: reduce) {{
      .trace, .rise, .dot {{ animation: none; }}
    }}
  </style>
  <text class="name rise" x="0" y="58">Lakshya Vasudeva</text>
  <text class="bio rise" x="2" y="100" style="animation-delay:.2s">Started coding at 7 and teaching at 8.</text>
  <text class="bio rise" x="2" y="127" style="animation-delay:.35s">Interned at <tspan>Zebra Technologies</tspan>, worked with <tspan>Interac</tspan>, researched at <tspan>Harvard</tspan>.</text>
  <text class="bio rise" x="2" y="154" style="animation-delay:.5s">Now building <tspan>Origin</tspan> -- a wearable to talk to your AI agents telepathically.</text>
  <path class="trace" d="{d}"/>
  <circle class="dot" cx="{end_x + 6:.1f}" cy="{end_y:.1f}" r="3.2"/>
  {caption}
</svg>
"""


def card(theme, item):
    c = THEMES[theme]
    w, h = 412, 178
    lines = "".join(f'<text class="body" x="22" y="{86 + i * 19}">{t}</text>' for i, t in enumerate(item["lines"]))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{item['title']}">
  <style>
    .kind {{ font: 500 10.5px {MONO}; letter-spacing: 1.3px; text-transform: uppercase; fill: {c['accent']}; }}
    .title {{ font: 600 17px {SANS}; letter-spacing: -0.2px; fill: {c['text']}; }}
    .body {{ font: 400 13px {SANS}; fill: {c['soft']}; }}
    .tags {{ font: 400 11px {MONO}; fill: {c['soft']}; }}
    .arrow {{ font: 400 15px {SANS}; fill: {c['soft']}; }}
  </style>
  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" fill="{c['card']}" stroke="{c['line']}"/>
  <text class="kind" x="22" y="32">{item['kind']}</text>
  <text class="arrow" x="{w - 22}" y="33" text-anchor="end">↗</text>
  <text class="title" x="22" y="59">{item['title']}</text>
  {lines}
  <line x1="22" y1="{h - 36}" x2="{w - 22}" y2="{h - 36}" stroke="{c['line']}" stroke-dasharray="1 4" stroke-linecap="round"/>
  <text class="tags" x="22" y="{h - 16}">{item['tags']}</text>
</svg>
"""


def rule(theme):
    c = THEMES[theme]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 12" width="840" height="12" role="presentation">
  <line x1="0" y1="6" x2="840" y2="6" stroke="{c['line']}" stroke-dasharray="1 5" stroke-linecap="round"/>
</svg>
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    for theme in THEMES:
        files = {"header": header(theme), "rule": rule(theme)}
        for item in CARDS:
            files["card-%s" % item["slug"]] = card(theme, item)
        for name, svg in files.items():
            with open(os.path.join(OUT, "%s-%s.svg" % (name, theme)), "w") as f:
                f.write(svg)
    print("wrote %d files to %s" % (len(THEMES) * (2 + len(CARDS)), OUT))


if __name__ == "__main__":
    main()
