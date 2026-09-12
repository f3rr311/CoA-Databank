# CoA Archive — Completeness Report (2026-07-21)

## Verdict: COMPLETE (99.8%)

- **21 / 21 classes** captured (IDs 12–32).
- **1,963 / 1,967 abilities** have full tooltip JSON (name, formula, cost,
  cooldown, scaling, icon reference).
- Per-class ability lists verified NOT truncated AGAINST THE SITE'S OWN
  client-rendered "X of Y" totals in-browser:
    Barbarian "1-50 of 100", Chronomancer "of 100", Guardian "of 100" - the
    round 100s are the genuine totals, not a cap.
    Decisive proof no 100-cap exists: Venomancer (112) and Witch Hunter (102)
    both exceed 100 in the archive, impossible under a cap.
- Class guide pages (specs/mechanics/resources): 21 / 21 (html + txt).

## The 4 gaps — broken on Ascension's server, not missed by us
These return HTTP 502 from db.ascension.gg's own power endpoint (corrupt source
records; the site is otherwise up). We HAVE their id + name + class; only the
formula tooltip is unavailable. Rebuild from name + convention when needed.

| ID | Name | Class |
|----|------|-------|
| 500118 | Frigid Blast | (frost) |
| 806307 | Eye of the Storm | Stormbringer |
| 800871 | Facemelter | (fire/pyro) |
| 804977 | Rotfang | Venomancer |

Retry anytime:  python fetch_ascension.py spell 500118 806307 800871 804977

## Is "Talents" the whole kit? Yes.
CoA delivers every player ability through talent trees (class tree from L1 +
spec tree from L10). "<Class> - Talents" IS the complete player-facing set.
NOT captured (by design, and not needed for the player kit):
  - Creature-side spells (what summoned minions cast) - authored on the creature.
  - A few internal-only trigger spells (most triggers ARE captured).

## What we hold, per class
  coa_spell_ids/<class>.json   - id -> name map (full ability list)
  archive/spell/<id>.json      - tooltip with formula, cost, cd, icon
  archive/coa_classes/<c>.txt  - spec/mechanic/resource guide
  archive/icons/               - deduplicated icon images (large + medium)
