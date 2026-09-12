# CoA Databank

Archived data harvested from Project Ascension's Conquest of Azeroth (CoA) and
its community sites. Reference material for the ByteCOA rebuild. No runtime
code lives here.

| Folder | Source | Contents |
|---|---|---|
| `coabuildhub/` | https://coabuildhub.com, scraped 2026-07-31 | 21 classes, 3612 talent nodes, 2909 skills, 128 community builds, icons, raw page payloads |
| `provenance/original-coa/palette/` | CoA / Ascension client MPQs, captured 2026-07-29 | Compressed JSONL: 238,888 spells and their dependencies, 621,960 Ascension asset paths, 241,850 client asset paths, 178,795 loose extracted asset paths, 119,084 client DBC rows (AnimationData, SpellVisual, SpellIcon, CreatureDisplayInfo, ...), 117,638 donor DBC rows, 5,269 creatures. See `palette-manifest.json` for hashes. |
| `provenance/original-coa/local/` | Local harvest | Harvest and fetch scripts, class roster, completeness reports, archived class/spell/item/icon captures, legacy CoA QA data |
| `provenance/original-coa/web/` | Web captures | Saved pages and `web-sources.json` index |
| `provenance/ascension/inventory/` | Ascension source snapshot | Table counts, attribution counts, semantic adjudication, unknown register |
| `databank/` | ByteCOA archived commit `7a8c735e` | `manifest.json` (SHA-256 per file), 21-class/70-spec `roster.json`, `native-class-map.json`, `creative-authority.json`, curated Necromancer animation/class/death data, copy of the palette and inventory |

The 781 MB raw extraction of models, textures and sounds (20 files, SHA-256
`daa1147211d0ef75f6fdcc89015f967f003b5f3c5dd0fa27b71a2427ebd45a37`) is not in
this repository; `databank/manifest.json` records its identity.
