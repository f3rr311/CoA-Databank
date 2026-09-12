#!/usr/bin/env python3
"""
Download the actual icon images for every harvested CoA ability.

Reads archive/spell/*.json, collects unique "icon" names, and downloads
each as a .jpg (large + medium) into archive/icons/. Deduplicated and
resumable (skips icons already on disk). Run after / alongside harvest_coa.py.
"""
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
SPELLS = ROOT / "archive" / "spell"
ICONS = ROOT / "archive" / "icons"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
SIZES = ("large", "medium")


def collect_icons():
    names = set()
    for f in SPELLS.glob("*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        icon = d.get("icon")
        if icon:
            names.add(icon.lower())
    return sorted(names)


def download(icon, size):
    dest = ICONS / size / f"{icon}.jpg"
    if dest.exists():
        return "cached"
    url = f"https://db.ascension.gg/static/images/wow/icons/{size}/{icon}.jpg"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
    except Exception as e:
        return f"error {e}"
    dest.write_bytes(data)
    return "saved"


def main():
    for s in SIZES:
        (ICONS / s).mkdir(parents=True, exist_ok=True)
    icons = collect_icons()
    print(f"{len(icons)} unique icons referenced by harvested abilities")
    ok = 0
    for i, icon in enumerate(icons, 1):
        results = [download(icon, s) for s in SIZES]
        if "saved" in results:
            ok += 1
            time.sleep(0.5)   # only throttle on real downloads
        if i % 50 == 0:
            print(f"  [{i}/{len(icons)}] {ok} downloaded")
    print(f"\nDONE: {ok} new icons saved to {ICONS}")


if __name__ == "__main__":
    main()
