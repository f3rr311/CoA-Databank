# CoA Build Hub — Full Archive

Scraped from https://coabuildhub.com on 2026-07-31.
Community talent-build hub for Conquest of Azeroth (Project Ascension's classless expansion).
robots.txt allows all public pages; per-user API endpoints were not touched.

## Contents

| Folder | What | Count |
|---|---|---|
| `classes.json` | Class/spec/tab-id metadata for all 21 classes | 21 classes |
| `talents/` | Full talent trees per class (`.json` data + `.md` readable) | 3612 nodes |
| `skills/` | Full spell/ability DB per class (`.json` + `.md`), incl. HTML tooltips | 2909 skills |
| `builds/<class>/` | Every published community build: metadata, full guide text, comments, decoded talent picks | 128 builds |
| `spells/` | Master spell index merged from skills DB + talent trees + guide refs + db.ascension.gg lookups (`master_index.json`/`.md`, `missing_from_skills_db.json`) | 5172 unique spell ids |
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

- barbarian: 6
- bloodmage: 6
- chronomancer: 3
- cultist: 8
- felsworn: 7
- guardian: 3
- knight-of-xoroth: 7
- necromancer: 9
- primalist: 8
- pyromancer: 3
- ranger: 6
- reaper: 6
- runemaster: 6
- starcaller: 6
- stormbringer: 3
- sun-cleric: 8
- templar: 5
- tinker: 7
- venomancer: 6
- witch-doctor: 7
- witch-hunter: 8
