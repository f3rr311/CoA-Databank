"""Build a master spell index from every source in the archive.

Sources:
  A. skills/<slug>.json      -- site's per-class skill DB (real spell ids)
  B. talents/<slug>.json     -- talent nodes carry spellId + description
  C. builds/**/*.json        -- guide texts reference coa-skill:<class>:<id>
                                and db.ascension.gg/?spell=<id> links
Output:
  spells/master_index.json   -- one entry per unique spell id, all sources merged
  spells/missing_from_skills_db.json -- ids we know exist but have no skill entry
"""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"C:\Users\Byte\WOW\coabuildhub")

classes = json.loads((ROOT / "classes.json").read_text(encoding="utf-8"))
slugs = [c["slug"] for c in classes]

index = {}  # spellId -> entry


def entry(sid):
    if sid not in index:
        index[sid] = {"id": sid, "name": None, "classes": set(), "sources": set(),
                      "type": None, "school": None, "level": None, "rank": None,
                      "icon": None, "description": None, "tooltip": None}
    return index[sid]


# A. skills DB
n_skill_rows = 0
for slug in slugs:
    d = json.loads((ROOT / "skills" / f"{slug}.json").read_text(encoding="utf-8"))
    for sk in d.get("skills", []):
        sid = sk.get("id")
        if not sid:
            continue
        n_skill_rows += 1
        e = entry(sid)
        e["classes"].add(slug)
        e["sources"].add("skills-db")
        for k in ("name", "type", "school", "level", "rank", "icon", "description", "tooltip"):
            if e[k] is None and sk.get(k) not in (None, ""):
                e[k] = sk[k]

# B. talent nodes
n_talent_nodes = 0
for slug in slugs:
    d = json.loads((ROOT / "talents" / f"{slug}.json").read_text(encoding="utf-8"))
    for tree in d["trees"]:
        for n in tree["nodes"]:
            sid = n.get("spellId")
            if not sid:
                continue
            n_talent_nodes += 1
            e = entry(sid)
            e["classes"].add(slug)
            e["sources"].add("talent-tree")
            if e["name"] is None:
                e["name"] = n.get("name")
            if e["description"] is None:
                e["description"] = n.get("description")
            if e["icon"] is None:
                e["icon"] = n.get("icon")
            if e["type"] is None:
                e["type"] = "Talent"

# C. guide references
ref_re = re.compile(r"coa-skill:([a-z\-]+):(\d+)")
db_re = re.compile(r"db\.ascension\.gg/\?spell=(\d+)")
n_refs = 0
for jf in (ROOT / "builds").rglob("*.json"):
    d = json.loads(jf.read_text(encoding="utf-8"))
    text = (d["build"].get("description") or "") + json.dumps(d.get("comments") or [])
    for m in ref_re.finditer(text):
        slug2, sid = m.group(1), int(m.group(2))
        e = entry(sid)
        e["classes"].add(slug2)
        e["sources"].add("guide-ref")
        n_refs += 1
    for m in db_re.finditer(text):
        e = entry(int(m.group(1)))
        e["sources"].add("guide-ref")
        n_refs += 1

# finalize
out = []
for sid, e in sorted(index.items()):
    e["classes"] = sorted(e["classes"])
    e["sources"] = sorted(e["sources"])
    out.append(e)

sdir = ROOT / "spells"
sdir.mkdir(exist_ok=True)
(sdir / "master_index.json").write_text(
    json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")

missing = [e for e in out if "skills-db" not in e["sources"]]
(sdir / "missing_from_skills_db.json").write_text(
    json.dumps(missing, indent=1, ensure_ascii=False), encoding="utf-8")

by_src = defaultdict(int)
for e in out:
    by_src[",".join(e["sources"])] += 1
print(f"skill rows: {n_skill_rows}, talent nodes with spellId: {n_talent_nodes}, guide refs: {n_refs}")
print(f"unique spell ids: {len(out)}")
for k, v in sorted(by_src.items()):
    print(f"  {k}: {v}")
print(f"missing from skills-db: {len(missing)} (of which named: {sum(1 for e in missing if e['name'])})")
no_name = [e["id"] for e in missing if not e["name"]]
print(f"unnamed ids (guide-ref only): {len(no_name)}: {no_name[:20]}")
