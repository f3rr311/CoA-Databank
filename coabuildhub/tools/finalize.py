"""Post-pass: decode talent strings into allocations, regenerate build MDs
with a readable Talents section, fix skills MDs, and write the README index."""
import base64
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"C:\Users\Byte\WOW\coabuildhub")
BASE = "https://coabuildhub.com"

classes = json.loads((ROOT / "classes.json").read_text(encoding="utf-8"))
class_by_id = {c["id"]: c for c in classes}

# node lookup: id -> node dict (with tree name)
node_lookup = {}
for c in classes:
    tal = json.loads((ROOT / "talents" / f"{c['slug']}.json").read_text(encoding="utf-8"))
    for tree in tal["trees"]:
        for n in tree["nodes"]:
            node_lookup[n["id"]] = {**n, "_tree": tree["name"]}


def decode_ts(ts):
    if not ts:
        return None
    try:
        pad = ts + "=" * (-len(ts) % 4)
        return json.loads(base64.b64decode(pad))
    except Exception:
        return None


# --- builds ---
n_dec = 0
n_total = 0
for jf in sorted((ROOT / "builds").rglob("*.json")):
    data = json.loads(jf.read_text(encoding="utf-8"))
    build = data["build"]
    n_total += 1
    alloc = decode_ts(build.get("talent_string"))
    data["allocations"] = alloc
    resolved = []
    if alloc:
        n_dec += 1
        for node_id, pts in alloc:
            nd = node_lookup.get(node_id)
            resolved.append({
                "id": node_id,
                "points": pts,
                "name": nd["name"] if nd else "(unknown node)",
                "maxPoints": nd["maxPoints"] if nd else None,
                "tree": nd["_tree"] if nd else None,
                "spellId": nd["spellId"] if nd else None,
            })
    data["allocationsResolved"] = resolved
    jf.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")

    cls = class_by_id.get(build.get("class_id"), {})
    spec = next((s["name"] for s in cls.get("specs", []) if s["id"] == build.get("spec_id")),
                str(build.get("spec_id")))
    author = (build.get("author") or {}).get("username") or (build.get("author") or {}).get(
        "display_name", "?")
    uuid = build.get("id", jf.stem)
    md = [
        f"# {build.get('title', uuid)}",
        "",
        f"- **Class/Spec:** {cls.get('name')} — {spec}",
        f"- **Author:** {author}",
        f"- **Role/Type:** {build.get('role')} / {build.get('content_type')}",
        f"- **Tags:** {', '.join(build.get('tags') or [])}",
        f"- **Score:** +{build.get('upvotes', 0)}/-{build.get('downvotes', 0)}"
        f" · {build.get('view_count', 0)} views · {build.get('comment_count', 0)} comments",
        f"- **Updated:** {build.get('updated_at')}",
        f"- **Patch:** {build.get('patch_version')}",
        f"- **URL:** {BASE}/build/{uuid}",
    ]
    if resolved:
        by_tree = defaultdict(list)
        for r in resolved:
            by_tree[r["tree"] or "?"].append(r)
        total_pts = sum(r["points"] for r in resolved)
        md += ["", f"## Talents ({total_pts} points, {len(resolved)} nodes)"]
        for tree, rs in by_tree.items():
            md += ["", f"### {tree} ({sum(r['points'] for r in rs)} pts)"]
            for r in rs:
                mx = f"/{r['maxPoints']}" if r["maxPoints"] else ""
                md.append(f"- {r['name']} {r['points']}{mx}")
    md += ["", "---", "", build.get("description") or "(no guide text)"]
    comments = data.get("comments") or []
    if comments:
        md += ["", "---", "", "## Comments", ""]
        for c in comments:
            if isinstance(c, dict):
                ca = (c.get("author") or {}).get("username", "?")
                md.append(f"**{ca}:** {c.get('content', '')}")
                md.append("")
    jf.with_suffix(".md").write_text("\n".join(md), encoding="utf-8")

print(f"builds: {n_total}, talent strings decoded: {n_dec}")

# --- skills MD (fixed for dict wrapper) ---
strip_tags = re.compile(r"<[^>]+>")
for f in sorted((ROOT / "skills").glob("*.json")):
    if f.stem == "manifest":
        continue
    d = json.loads(f.read_text(encoding="utf-8"))
    skills = d.get("skills", []) if isinstance(d, dict) else d
    title = f.stem.replace("-", " ").title()
    lines = [f"# {title} — Skills & Abilities", "",
             f"Source: {d.get('source', '?')} · Count: {d.get('count', len(skills))}", ""]
    for sk in sorted(skills, key=lambda s: (s.get("name") or "")):
        bits = [sk.get("type") or "?", sk.get("school") or ""]
        if sk.get("level") is not None:
            bits.append(f"Lvl {sk['level']}")
        if sk.get("rank"):
            bits.append(sk["rank"])
        bits.append(f"spell {sk.get('id')}")
        if sk.get("icon"):
            bits.append(f"icon `{sk['icon']}`")
        lines += [f"### {sk.get('name', '?')}",
                  f"*{' · '.join(b for b in bits if b)}*", ""]
        desc = sk.get("description") or strip_tags.sub(" ", sk.get("tooltip") or "")
        lines += [desc.strip(), ""]
    f.with_suffix(".md").write_text("\n".join(lines), encoding="utf-8")
print("skills MDs rewritten")

# --- README ---
n_builds_by_class = {d.name: len(list(d.glob("*.json"))) for d in sorted((ROOT / "builds").iterdir()) if d.is_dir()}
total_nodes = sum(
    json.loads((ROOT / "talents" / f"{c['slug']}.json").read_text(encoding="utf-8"))["nodeCount"]
    for c in classes)
total_skills = 0
for c in classes:
    d = json.loads((ROOT / "skills" / f"{c['slug']}.json").read_text(encoding="utf-8"))
    total_skills += d.get("count", 0)

readme = f"""# CoA Build Hub — Full Archive

Scraped from https://coabuildhub.com on 2026-07-31.
Community talent-build hub for Conquest of Azeroth (Project Ascension's classless expansion).
robots.txt allows all public pages; per-user API endpoints were not touched.

## Contents

| Folder | What | Count |
|---|---|---|
| `classes.json` | Class/spec/tab-id metadata for all 21 classes | 21 classes |
| `talents/` | Full talent trees per class (`.json` data + `.md` readable) | {total_nodes} nodes |
| `skills/` | Full spell/ability DB per class (`.json` + `.md`), incl. HTML tooltips | {total_skills} skills |
| `builds/<class>/` | Every published community build: metadata, full guide text, comments, decoded talent picks | {sum(n_builds_by_class.values())} builds |
| `pages/` | Site guides (essence system, beginner guide, how to read a build, ...) as markdown | 8 pages |
| `assets/` | Icon sprite sheet (`coa-builder-icon.webp`, 3205 icons) + `coa-icons.css` position map | |
| `raw/` | Raw HTML/JS/chunks as fetched (re-parse anytime) | |
| `tools/` | The scraper/parsers used (Python) | |

## Data notes

- **Talent node id** format: `classId-tabId-x-y` (e.g. `27-90-4-0`). Class ids 12-32; tab 87 = shared class tree, other tabs = specs (see `classes.json`).
- **talent_string** on a build = base64 of JSON `[[nodeId, points], ...]` — already decoded into `allocations`/`allocationsResolved` in each build JSON and a Talents section in each MD.
- **Skills** are sourced by the site from `db.ascension.gg` (source URL in each skills JSON). `id` is the real spell id; `tooltip` is the full db HTML tooltip.
- Icon rendering: `.coa-icon` + `._<iconname>` class pair from `assets/coa-icons.css` against the sprite sheet.

## Builds per class

{chr(10).join(f"- {k}: {v}" for k, v in n_builds_by_class.items())}
"""
(ROOT / "README.md").write_text(readme, encoding="utf-8")
print("README.md written")
