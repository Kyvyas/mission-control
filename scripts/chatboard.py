#!/usr/bin/env python3
"""Render board.json as a colour-coded monospace board grid for chat.

Usage: python3 chatboard.py <board.json> [today YYYY-MM-DD]
       python3 chatboard.py --list <board.json>   (one "#n<TAB>id<TAB>title" per card)
Colour comes from emoji (terminals render them in colour); alignment is
kept by padding on display width (emoji count as two cells).
Cards are numbered #1..#n in display order so the user can refer to them
by number; --list prints the same numbering for resolving "#n".
"""
import json, sys, textwrap, datetime, unicodedata

W = 24
GAP = "   "
SHIPPED_SHOWN = 3
COLS = [("idea", "\U0001F535", "IDEAS"), ("active", "\U0001F7E2", "ACTIVE"),
        ("shipped", "\U0001F680", "SHIPPED"), ("parked", "\U0001F7E1", "PARKED"),
        ("dropped", "\u26AB", "DROPPED")]

def cw(ch):
    o = ord(ch)
    if 0x1F000 <= o <= 0x1FAFF or o in (0x2705, 0x26AB, 0x2B50):
        return 2
    if unicodedata.combining(ch):
        return 0
    return 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1

def dw(s):
    return sum(cw(c) for c in s)

def wrap(text, lines, prefix=""):
    out = textwrap.wrap(prefix + text, W, max_lines=lines, placeholder="…")
    return out or [""]

def bar(done, total, seg=6):
    filled = round(seg * done / total) if total else 0
    return "\u2593" * filled + "\u2591" * (seg - filled)

def grouped(b):
    """Projects by status in display order: file order, except Shipped newest first."""
    by = {}
    for p in b["projects"]:
        by.setdefault(p["status"], []).append(p)
    by.get("shipped", []).sort(key=lambda p: p.get("shipped_on", ""), reverse=True)
    return by

def numbered(by):
    order = [p for k, *_ in COLS for p in by.get(k, [])]
    return {id(p): i for i, p in enumerate(order, 1)}, order

def main():
    if sys.argv[1] == "--list":
        _, order = numbered(grouped(json.load(open(sys.argv[2]))))
        for i, p in enumerate(order, 1):
            print(f"#{i}\t{p['id']}\t{p['title']}")
        return
    b = json.load(open(sys.argv[1]))
    today = datetime.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else datetime.date.today()
    days = lambda iso: (today - datetime.date.fromisoformat(iso)).days
    by = grouped(b)
    num, _ = numbered(by)

    cols = [(k, dot, label, by.get(k, [])) for k, dot, label in COLS if k != "dropped" or by.get(k)]
    total_w = W * len(cols) + len(GAP) * (len(cols) - 1)

    name = b["config"]["name"].upper()
    # status keys double as tally nouns; only "idea" takes a plural
    tally = " \u00B7 ".join(f"{len(items)} {k}{'s' if k == 'idea' and len(items) != 1 else ''}"
                            for k, dot, label, items in cols if items)
    print(f"\U0001F680 {name}  \u00B7  {tally}")
    print("\u2550" * total_w)

    parked = sorted((p for p in by.get("parked", []) if p.get("parked_since")), key=lambda p: p["parked_since"])
    if parked and days(parked[0]["parked_since"]) > 21:
        p = parked[0]
        print(f"\U0001F525 LONGEST HOLD  {p['title']} \u2014 {days(p['parked_since'])}d \u00B7 resume: {p.get('unblock','')}")
        print("\u2500" * total_w)

    def card_lines(p):
        ls = wrap(p["title"], 2, f"#{num[id(p)]} ")
        st = p["status"]
        if st == "parked" and p.get("parked_since"):
            d = days(p["parked_since"])
            flame = "\U0001F525 " if d > 45 else "\U0001F552 "
            ls += wrap(f"{d}d \u00B7 {p.get('parked_reason','')}", 2, flame)
            if p.get("unblock"):
                ls += wrap(p["unblock"], 2, "\u21B3 ")
        elif st == "shipped":
            ls += [f"\u2705 {p.get('shipped_on','')}"]
        elif p.get("next_action"):
            # the active next action is the board's headline \u2014 never truncate it
            ls += wrap(p["next_action"], None if st == "active" else 2, "\u2192 ")
        extras = []
        if p.get("tasks"):
            done = sum(t["done"] for t in p["tasks"])
            extras.append(f"{bar(done, len(p['tasks']))} {done}/{len(p['tasks'])}")
        if p.get("notes"):
            extras.append(f"\U0001F4DD{len(p['notes'])}")
        if extras:
            ls += [" \u00B7 ".join(extras)]
        return ls

    rendered = []
    for k, dot, label, items in cols:
        cl = [f"{dot} {label} \u00B7 {len(items)}", "\u2500" * W]
        shown = items[:SHIPPED_SHOWN] if k == "shipped" else items
        for i, p in enumerate(shown):
            if i:
                cl.append("")
            cl += card_lines(p)
        if len(shown) < len(items):
            rest = items[len(shown):]
            cl += ["", f"+{len(rest)} earlier · #{num[id(rest[0])]}–#{num[id(rest[-1])]}"
                   if len(rest) > 1 else f"+1 earlier · #{num[id(rest[0])]}"]
        if not items:
            cl.append("\u00B7 nothing")
        rendered.append(cl)

    height = max(len(c) for c in rendered)
    for row in range(height):
        cells = []
        for c in rendered:
            cell = c[row] if row < len(c) else ""
            cells.append(cell + " " * max(0, W - dw(cell)))
        print(GAP.join(cells).rstrip())

if __name__ == "__main__":
    main()
