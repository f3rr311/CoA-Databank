#!/usr/bin/env python3
"""
Ascension DB archiver — save spell/item/quest JSON before shutdown.

Usage:
  python fetch_ascension.py spell 1234 5678 90123
  python fetch_ascension.py item 19019 917400
  python fetch_ascension.py spell 100000-100200      (inclusive ID range)

Output: one .json per entity under ./archive/<type>/<id>.json
Throttled to 1 request/second — be kind, they're shutting down, not a CDN.
"""

import json
import re
import sys
import time
import urllib.request
from pathlib import Path

BASE = "https://db.ascension.gg/?{kind}={id}&power"
OUT = Path(__file__).parent / "archive"
UA = "BytesMidnight-preservation/1.0 (personal archive of a shutting-down DB)"


def parse_power(raw: str):
    """$WowheadPower.registerX(id, n, {...})  ->  dict"""
    m = re.search(r"\(\s*\d+\s*,\s*\d+\s*,\s*(\{.*\})\s*\)\s*;?\s*$", raw, re.S)
    if not m:
        return None
    obj = m.group(1)
    # keys are unquoted JS identifiers -> quote them for JSON
    obj = re.sub(r"([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:", r'\1"\2":', obj)
    try:
        return json.loads(obj)
    except json.JSONDecodeError:
        return {"_raw": raw}  # keep the original even if parsing fails


def fetch(kind: str, entity_id: int):
    url = BASE.format(kind=kind, id=entity_id)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", errors="replace")


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    kind = sys.argv[1].lower()
    if kind not in ("spell", "item", "quest", "npc"):
        raise SystemExit("kind must be spell/item/quest/npc")

    ids = []
    for arg in sys.argv[2:]:
        if "-" in arg:
            a, b = arg.split("-", 1)
            ids.extend(range(int(a), int(b) + 1))
        else:
            ids.append(int(arg))

    outdir = OUT / kind
    outdir.mkdir(parents=True, exist_ok=True)
    ok = missing = 0

    for i, eid in enumerate(ids, 1):
        dest = outdir / f"{eid}.json"
        if dest.exists():
            print(f"[{i}/{len(ids)}] {kind} {eid}: already archived")
            continue
        try:
            raw = fetch(kind, eid)
        except Exception as e:
            print(f"[{i}/{len(ids)}] {kind} {eid}: FETCH ERROR {e}")
            time.sleep(2)
            continue
        data = parse_power(raw)
        if data is None or "name_enus" not in json.dumps(data)[:2000]:
            missing += 1
            print(f"[{i}/{len(ids)}] {kind} {eid}: no data (id unused?)")
        else:
            dest.write_text(json.dumps(data, indent=2, ensure_ascii=False),
                            encoding="utf-8")
            ok += 1
            name = data.get("name_enus", "?")
            print(f"[{i}/{len(ids)}] {kind} {eid}: saved ({name})")
        time.sleep(1.0)  # politeness throttle

    print(f"\ndone: {ok} saved, {missing} empty, output in {outdir}")


if __name__ == "__main__":
    main()
