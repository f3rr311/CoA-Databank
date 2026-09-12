"""Split the extracted talent payload into per-class JSON + Markdown files.

Inputs:
  raw/payloads/000.json        -- {classId: [node, ...]} for all 21 classes
  raw/chunks/9473-*.js         -- contains the class/spec metadata array
Outputs:
  classes.json                 -- class/spec metadata (parsed from chunk)
  talents/<slug>.json          -- class meta + nodes grouped per tab
  talents/<slug>.md            -- human-readable talent listing
"""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"C:\Users\Byte\WOW\coabuildhub")

# --- 1. class metadata from chunk 9473 ---
chunk = next((ROOT / "raw" / "chunks").glob("9473-*.js")).read_text(encoding="utf-8")
m = re.search(r"let t=(\[\{id:12,.*?\])\s*[,;]\s*(?:let|var|const)? ?[a-z]=", chunk, re.S)
if not m:
    # fall back: capture from `let t=[` to the `]` before `,s=` style
    start = chunk.index("let t=[")
    m2 = re.search(r"let t=(\[.*?\}\])(?=[,;])", chunk[start:], re.S)
    raw = m2.group(1)
else:
    raw = m.group(1)

# JS object literal -> JSON: quote bare keys, strip trailing commas
jsonish = re.sub(r"([{,])([A-Za-z_][A-Za-z0-9_]*):", r'\1"\2":', raw)
classes = json.loads(jsonish)
(ROOT / "classes.json").write_text(
    json.dumps(classes, indent=1, ensure_ascii=False), encoding="utf-8"
)
print(f"classes.json: {len(classes)} classes")

# --- 2. split payload per class ---
payload = json.load(open(ROOT / "raw" / "payloads" / "000.json", encoding="utf-8"))
tdir = ROOT / "talents"
tdir.mkdir(exist_ok=True)

all_keys = set()
for cls in classes:
    cid = str(cls["id"])
    nodes = payload.get(cid, [])
    for n in nodes:
        all_keys.update(n.keys())
    tab_names = {s["tabId"]: s["name"] for s in cls["specs"]}
    tab_names[cls["classTabId"]] = f"{cls['name']} (class tree)"
    by_tab = defaultdict(list)
    for n in nodes:
        by_tab[n["tabId"]].append(n)
    out = {
        "class": {k: cls[k] for k in ("id", "name", "slug", "color")},
        "specs": cls["specs"],
        "classTabId": cls["classTabId"],
        "nodeCount": len(nodes),
        "trees": [
            {
                "tabId": tab,
                "name": tab_names.get(tab, f"tab {tab}"),
                "nodeCount": len(ns),
                "nodes": sorted(ns, key=lambda n: (n["y"], n["x"])),
            }
            for tab, ns in sorted(by_tab.items(), key=lambda kv: kv[0] != cls["classTabId"])
        ],
    }
    (tdir / f"{cls['slug']}.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8"
    )

    # markdown
    lines = [f"# {cls['name']} — Talents", ""]
    lines.append(f"Specs: {', '.join(s['name'] for s in cls['specs'])}")
    lines.append(f"Total nodes: {len(nodes)}")
    for tree in out["trees"]:
        lines += ["", f"## {tree['name']} ({tree['nodeCount']} nodes)", ""]
        for n in tree["nodes"]:
            kind = "Passive" if n.get("isPassive") else "Active"
            cost = []
            if n.get("teCost"):
                cost.append(f"{n['teCost']} TE")
            if n.get("aeCost"):
                cost.append(f"{n['aeCost']} AE")
            cost_s = "/".join(cost) or "free"
            lines.append(
                f"### {n['name']}  \n"
                f"*{kind} · {n.get('nodeType','?')} · max {n.get('maxPoints',1)} pt · "
                f"cost {cost_s} · pos ({n['x']},{n['y']}) · spell {n.get('spellId')} · "
                f"icon `{n.get('icon')}`*  \n"
                f"{n.get('description','(no description)')}"
            )
            lines.append("")
    (tdir / f"{cls['slug']}.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"  {cls['slug']}: {len(nodes)} nodes, {len(out['trees'])} trees")

print("node keys seen:", sorted(all_keys))
