#!/usr/bin/env python3
"""
Full CoA class-ability harvester.

Phase 1: probe ?spells=-2.N to discover all 21 custom class category IDs
         (reads <title> "ClassName - Talents").
Phase 2: for each class, pull the embedded spell id/name array from the
         category HTML.
Phase 3: fetch ?spell=ID&power tooltip JSON for every ability (formulas!).

All via curl-equivalent urllib with a browser UA. Throttled, resumable
(skips already-saved files). Output:
  coa_spell_ids/<class>.json          (id -> name map per class)
  archive/spell/<id>.json             (full tooltip JSON per ability)
"""
import json
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
IDS = ROOT / "coa_spell_ids"
SPELLS = ROOT / "archive" / "spell"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

# Custom CoA classes only (base WoW classes occupy the low IDs 1-11).
KNOWN_BASE = {"Warrior", "Paladin", "Hunter", "Rogue", "Priest",
              "Death Knight", "Shaman", "Mage", "Warlock", "Druid",
              "Monk", "Demon Hunter", "Evoker"}
PROBE_RANGE = range(12, 45)   # CoA custom class category IDs live here


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", errors="replace")


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def discover_classes():
    found = {}
    for n in PROBE_RANGE:
        try:
            html = get(f"https://db.ascension.gg/?spells=-2.{n}")
        except Exception as e:
            print(f"  probe {n}: error {e}")
            time.sleep(1.5)
            continue
        m = re.search(r"<title>([^<]+?)\s*-\s*Talents", html)
        if m:
            name = m.group(1).strip()
            if name and name not in KNOWN_BASE:
                found[n] = name
                print(f"  class {n}: {name}")
        time.sleep(1.0)
    return found


def spells_from_category(cat_id):
    html = get(f"https://db.ascension.gg/?spells=-2.{cat_id}")
    pairs = {}
    for m in re.finditer(r'"id":(\d+),"name":"((?:[^"\\]|\\.)*)"', html):
        sid, name = m.group(1), m.group(2)
        if sid != "0":
            pairs[sid] = name.lstrip("@").replace("\\'", "'")
    return pairs


def fetch_tooltip(sid):
    raw = get(f"https://db.ascension.gg/?spell={sid}&power")
    m = re.search(r"\(\s*\d+\s*,\s*\d+\s*,\s*(\{.*\})\s*\)\s*;?\s*$", raw, re.S)
    if not m:
        return None
    obj = re.sub(r"([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:", r'\1"\2":', m.group(1))
    try:
        return json.loads(obj)
    except json.JSONDecodeError:
        return {"_raw": raw}


def main():
    IDS.mkdir(parents=True, exist_ok=True)
    SPELLS.mkdir(parents=True, exist_ok=True)

    print("Phase 1: discovering CoA class category IDs...")
    classes = discover_classes()
    (IDS / "_class_map.json").write_text(json.dumps(classes, indent=2), encoding="utf-8")
    print(f"  -> {len(classes)} custom classes found\n")

    print("Phase 2: harvesting ability id/name lists per class...")
    all_ids = {}
    for cat, name in classes.items():
        dest = IDS / f"{slug(name)}.json"
        if dest.exists():
            data = json.loads(dest.read_text(encoding="utf-8"))
            all_ids.update(data["spells"])
            print(f"  {name}: cached ({data['count']})")
            continue
        try:
            spells = spells_from_category(cat)
        except Exception as e:
            print(f"  {name}: error {e}")
            continue
        dest.write_text(json.dumps(
            {"class": name, "categoryId": int(cat), "count": len(spells),
             "spells": spells}, indent=2, ensure_ascii=False), encoding="utf-8")
        all_ids.update(spells)
        print(f"  {name}: {len(spells)} abilities")
        time.sleep(1.0)

    print(f"\nPhase 3: fetching {len(all_ids)} ability tooltips (formulas)...")
    done = ok = 0
    for sid, name in all_ids.items():
        done += 1
        dest = SPELLS / f"{sid}.json"
        if dest.exists():
            continue
        try:
            data = fetch_tooltip(sid)
        except Exception as e:
            print(f"  [{done}/{len(all_ids)}] {sid} {name}: error {e}")
            time.sleep(2)
            continue
        if data:
            dest.write_text(json.dumps(data, indent=2, ensure_ascii=False),
                            encoding="utf-8")
            ok += 1
        if done % 50 == 0:
            print(f"  [{done}/{len(all_ids)}] ...{ok} saved")
        time.sleep(1.0)

    print(f"\nDONE: {len(classes)} classes, {len(all_ids)} abilities, "
          f"{ok} new tooltips saved.\nOutput: {IDS} and {SPELLS}")


if __name__ == "__main__":
    main()
