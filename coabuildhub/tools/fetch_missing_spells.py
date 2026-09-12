"""Resolve guide-referenced spell ids with no local data via db.ascension.gg
(?spell=<id>&power endpoint), merge results into spells/master_index.json."""
import json
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(r"C:\Users\Byte\WOW\coabuildhub")
UA = {"User-Agent": "Mozilla/5.0 (personal archive; contact: site user)"}

idx_path = ROOT / "spells" / "master_index.json"
index = json.loads(idx_path.read_text(encoding="utf-8"))
by_id = {e["id"]: e for e in index}
missing = [e for e in index if not e["name"]]
print(f"resolving {len(missing)} ids from db.ascension.gg")

rx = re.compile(r"registerSpell\(\d+,\s*\d+,\s*(\{.*\})\s*\)\s*;?\s*$", re.S)
fetched = {}
for e in missing:
    sid = e["id"]
    url = f"https://db.ascension.gg/?spell={sid}&power"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
            body = r.read().decode("utf-8", "replace")
        m = rx.search(body)
        if m:
            data = json.loads(m.group(1))
            e["name"] = data.get("name_enus")
            e["icon"] = e["icon"] or data.get("icon")
            e["tooltip"] = data.get("tooltip_enus")
            e["sources"].append("ascension-db")
            fetched[sid] = e["name"]
            print(f"  {sid}: {e['name']}")
        else:
            print(f"  {sid}: no registerSpell in response ({len(body)} bytes)")
    except Exception as ex:
        print(f"  {sid}: ERROR {ex}")
    time.sleep(0.4)

idx_path.write_text(json.dumps(index, indent=1, ensure_ascii=False), encoding="utf-8")

# refresh missing_from_skills_db too (names may have filled in)
missing_db = [e for e in index if "skills-db" not in e["sources"]]
(ROOT / "spells" / "missing_from_skills_db.json").write_text(
    json.dumps(missing_db, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"resolved {len(fetched)}/{len(missing)}")
