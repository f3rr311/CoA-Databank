#!/usr/bin/env python3
"""Archive all 21 Conquest of Azeroth class pages (HTML + extracted text)."""
import re
import time
import urllib.request
from pathlib import Path

OUT = Path(__file__).parent / "archive" / "coa_classes"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

CLASSES = ["necromancer", "pyromancer", "cultist", "starcaller", "sun-cleric",
           "tinker", "runemaster", "primalist", "reaper", "venomancer",
           "chronomancer", "son-of-arugal", "guardian", "stormbringer",
           "felsworn", "barbarian", "witch-doctor", "witch-hunter",
           "knight-of-xoroth", "templar", "ranger"]


def strip_html(h):
    h = re.sub(r"(?is)<(script|style|nav|footer|header)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?is)<br\s*/?>", "\n", h)
    h = re.sub(r"(?is)</(p|div|li|h[1-6]|tr)>", "\n", h)
    h = re.sub(r"(?is)<[^>]+>", " ", h)
    import html as _html
    h = _html.unescape(h)
    return re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t]{2,}", " ", h)).strip()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for i, slug in enumerate(CLASSES, 1):
        url = f"https://conquest-of-azeroth.wiki/classes/{slug}/"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=25) as r:
                raw = r.read().decode("utf-8", errors="replace")
        except Exception as e:
            print(f"[{i}/21] {slug}: ERROR {e}")
            time.sleep(2)
            continue
        (OUT / f"{slug}.html").write_text(raw, encoding="utf-8")
        (OUT / f"{slug}.txt").write_text(strip_html(raw), encoding="utf-8")
        print(f"[{i}/21] {slug}: saved ({len(raw):,} bytes)")
        time.sleep(1.5)
    print(f"\ndone -> {OUT}")


if __name__ == "__main__":
    main()
