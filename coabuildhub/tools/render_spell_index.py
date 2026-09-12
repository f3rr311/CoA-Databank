"""Render spells/master_index.json to a compact greppable markdown table."""
import json
from pathlib import Path

ROOT = Path(r"C:\Users\Byte\WOW\coabuildhub")
index = json.loads((ROOT / "spells" / "master_index.json").read_text(encoding="utf-8"))

lines = [
    "# Master Spell Index",
    "",
    f"{len(index)} unique spell ids merged from the site skills DB, talent trees,",
    "guide references, and db.ascension.gg lookups. Full data in `master_index.json`.",
    "",
    "| id | name | type | school | lvl | classes | sources |",
    "|---|---|---|---|---|---|---|",
]
for e in index:
    lines.append(
        f"| {e['id']} | {e['name'] or '?'} | {e['type'] or ''} | {e['school'] or ''} "
        f"| {e['level'] if e['level'] is not None else ''} "
        f"| {', '.join(e['classes'])} | {', '.join(e['sources'])} |"
    )
(ROOT / "spells" / "master_index.md").write_text("\n".join(lines), encoding="utf-8")
print(f"master_index.md: {len(index)} rows")
