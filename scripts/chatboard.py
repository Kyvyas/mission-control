#!/usr/bin/env python3
"""Render board.json as a monospace board grid for chat.

Usage: python3 chatboard.py <board.json> [today YYYY-MM-DD]
Prints a fixed-width four-column board; paste the output verbatim
into a fenced code block in chat.
"""
import json, sys, textwrap, datetime

W = 24          # column width
GAP = "   "     # column gap
COLS = [("idea", "IDEAS"), ("active", "ACTIVE"), ("shipped", "SHIPPED"), ("parked", "PARKED"), ("dropped", "DROPPED")]

def wrap(text, lines, prefix=""):
    out = textwrap.wrap(prefix + text, W, max_lines=lines, placeholder="…")
    return out or [""]

def main():
    b = json.load(open(sys.argv[1]))
    today = datetime.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else datetime.date.today()
    days = lambda iso: (today - datetime.date.fromisoformat(iso)).days
    by = {}
    for p in b["projects"]:
        by.setdefault(p["status"], []).append(p)

    cols = [(k, label, by.get(k, [])) for k, label in COLS if k != "dropped" or by.get(k)]

    # header
    name = b["config"]["name"].upper()
    tally = " · ".join(f"{len(items)} {label.lower()}" for k, label, items in cols if items)
    total_w = W * len(cols) + len(GAP) * (len(cols) - 1)
    print(f"{name}  ·  {tally}"[:total_w])
    print("═" * total_w)

    # longest-hold nag (> 21 days)
    parked = sorted((p for p in by.get("parked", []) if p.get("parked_since")), key=lambda p: p["parked_since"])
    if parked and days(parked[0]["parked_since"]) > 21:
        p = parked[0]
        print(f"⚠ LONGEST HOLD  {p['title']} — {days(p['parked_since'])}d · resume: {p.get('unblock','')}"[:total_w])
        print("─" * total_w)

    # build each column as a list of lines
    def card_lines(p):
        ls = wrap(p["title"], 2)
        st = p["status"]
        if st == "parked" and p.get("parked_since"):
            ls += wrap(f"{days(p['parked_since'])}d · {p.get('parked_reason','')}", 2, "⏸ ")
            if p.get("unblock"): ls += wrap(p["unblock"], 2, "↳ ")
        elif st == "shipped":
            ls += [f"✓ {p.get('shipped_on','')}"]
        elif p.get("next_action"):
            ls += wrap(p["next_action"], 2, "→ ")
        extras = []
        if p.get("tasks"):
            extras.append(f"▣ {sum(t['done'] for t in p['tasks'])}/{len(p['tasks'])}")
        if p.get("notes"):
            extras.append(f"✎ {len(p['notes'])}")
        if extras: ls += [" · ".join(extras)]
        return ls

    rendered = []
    for k, label, items in cols:
        cl = [f"{label}  {len(items)}", "─" * W]
        for i, p in enumerate(items):
            if i: cl.append("")
            cl += card_lines(p)
        if not items:
            cl.append("· nothing")
        rendered.append(cl)

    height = max(len(c) for c in rendered)
    for row in range(height):
        cells = []
        for c in rendered:
            cell = c[row] if row < len(c) else ""
            pad = W - len(cell)  # wide glyphs are close enough at these widths
            cells.append(cell + " " * max(0, pad))
        print(GAP.join(cells).rstrip())

if __name__ == "__main__":
    main()
