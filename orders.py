"""WhatsApp Order Organizer
Turns an exported WhatsApp chat of customer orders into:
  - orders.csv   (one clean row per item ordered)
  - summary.txt  (per-day totals: what to pack/buy, who ordered)
Usage: python orders.py chat.txt --out output/
No third-party dependencies.
"""
import argparse
import csv
import os
import re
from collections import defaultdict

# Matches Android ("12/10/26, 9:15 AM - Name: msg") and iOS ("[12/10/26, 9:15:03 AM] Name: msg")
LINE_RE = re.compile(
    r"^\[?(?P<date>\d{1,2}/\d{1,2}/\d{2,4}),?\s+"
    r"(?P<time>\d{1,2}:\d{2}(?::\d{2})?\s?(?:[APap][Mm])?)\]?\s*-?\s*"
    r"(?P<sender>[^:]+?):\s(?P<msg>.*)$"
)

UNITS = r"kgs?|gms?|g|ltrs?|litres?|liters?|l|pcs?|packets?|dozen|dz"
ITEM_FIRST = re.compile(
    rf"^(?P<qty>\d+(?:\.\d+)?)\s*(?P<unit>{UNITS})?\s+(?P<item>[a-zA-Z][a-zA-Z ]*)$", re.I)
QTY_LAST = re.compile(
    rf"^(?P<item>[a-zA-Z][a-zA-Z ]*?)\s+(?P<qty>\d+(?:\.\d+)?)\s*(?P<unit>{UNITS})?$", re.I)

UNIT_MAP = {"kgs": "kg", "gm": "g", "gms": "g", "ltr": "l", "ltrs": "l", "litre": "l",
            "litres": "l", "liter": "l", "liters": "l", "pc": "pcs", "packets": "packet",
            "dz": "dozen"}
# Local-language / spelling variants -> one canonical name (extend per shop!)
SYNONYMS = {"tamatar": "tomato", "pyaz": "onion", "aloo": "potato", "dudh": "milk"}


def normalize_item(name):
    name = re.sub(r"\s+", " ", name.strip().lower())
    if name.endswith("oes"):
        name = name[:-2]
    elif name.endswith("s") and not name.endswith("ss"):
        name = name[:-1]
    return SYNONYMS.get(name, name)


def normalize_unit(unit):
    unit = (unit or "unit").lower()
    return UNIT_MAP.get(unit, unit)


def parse_item(part):
    part = part.strip(" .!")
    for rx in (ITEM_FIRST, QTY_LAST):
        m = rx.match(part)
        if m:
            return normalize_item(m["item"]), float(m["qty"]), normalize_unit(m["unit"])
    return None


def parse_chat(lines):
    """Return a list of order rows. Chatter without quantities is ignored."""
    rows, order_id = [], 0
    for line in lines:
        m = LINE_RE.match(line.strip())
        if not m:
            continue
        date, time, who, msg = m["date"], m["time"], m["sender"].strip(), m["msg"]
        if re.search(r"\bcancel", msg, re.I):  # cancel this customer's latest order that day
            ids = [r["order_id"] for r in rows if r["customer"] == who and r["date"] == date]
            if ids:
                last = max(ids)
                rows = [r for r in rows if r["order_id"] != last]
            continue
        items = [p for p in re.split(r",|\n|&|\+|\band\b", msg, flags=re.I) if p.strip()]
        parsed = [x for x in map(parse_item, items) if x]
        if not parsed:
            continue
        order_id += 1
        for item, qty, unit in parsed:
            rows.append({"order_id": order_id, "date": date, "time": time,
                         "customer": who, "item": item, "qty": qty, "unit": unit})
    return rows


def build_summary(rows):
    by_date = defaultdict(list)
    for r in rows:
        by_date[r["date"]].append(r)
    out = []
    for date, rs in by_date.items():
        totals = defaultdict(float)
        for r in rs:
            totals[(r["item"], r["unit"])] += r["qty"]
        customers = sorted({r["customer"] for r in rs})
        out.append(f"=== {date} | {len(customers)} customers | {len({r['order_id'] for r in rs})} orders ===")
        out.append("TO PACK / BUY:")
        for (item, unit), q in sorted(totals.items()):
            out.append(f"  {item:<15} {q:g} {unit}")
        out.append("BY CUSTOMER:")
        for c in customers:
            items = ", ".join(f"{r['qty']:g} {r['unit']} {r['item']}" for r in rs if r["customer"] == c)
            out.append(f"  {c}: {items}")
        out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Organize WhatsApp orders")
    ap.add_argument("chat", help="exported WhatsApp .txt file")
    ap.add_argument("--out", default="output", help="output folder")
    a = ap.parse_args()
    with open(a.chat, encoding="utf-8") as f:
        rows = parse_chat(f.readlines())
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "orders.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["order_id", "date", "time", "customer", "item", "qty", "unit"])
        w.writeheader()
        w.writerows(rows)
    summary = build_summary(rows)
    with open(os.path.join(a.out, "summary.txt"), "w", encoding="utf-8") as f:
        f.write(summary)
    print(summary)
    print(f"Saved {len(rows)} item rows to {a.out}/")


if __name__ == "__main__":
    main()
