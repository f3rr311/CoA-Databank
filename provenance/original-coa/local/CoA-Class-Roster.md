# Conquest of Azeroth — Complete Class Roster (archived 2026-07-21)

Source: conquest-of-azeroth.wiki/classes/ (preserved before Ascension shutdown)
System: class at creation → spec at level 10 (class tree + spec tree, DF-style)
→ Ability Essences at 30+ unlock spec-tree skills. 21 classes / 69 specs.

| Class | Roles | Identity |
|---|---|---|
| Necromancer | Ranged DPS | Commands hordes of undead minions (skeletons, wraiths, abominations, ghouls); plague + frost. Life Force resource. |
| Pyromancer | Ranged DPS / Healer | Destructive fire magic or phoenix healing. |
| Cultist | Tank / DPS / Healer | Old Gods fanatic balancing forbidden power vs madness. |
| Starcaller | Tank / DPS / Healer | Astral knight of Elune — blade, bow, or moon magic. Specs incl. Moon Priest (heal). |
| Sun Cleric | Tank / DPS / Healer | Solar paladin: righteous fire heals/protects/smites. Specs incl. Seraphim (tank), Blessings (heal). |
| Tinker | Ranged DPS / Healer | Bombs, turrets, mechs, arsenal of bullet types; intellect guns. |
| Runemaster | Ranged DPS | Rune-inscribing arcanist, wild magic glyphs + bonded familiar. |
| Primalist | Tank / Healer / DPS | Geomancy, mountain spirits, wild gods, Earthmother life magic. Specs incl. Restoration. |
| Reaper | Tank / DPS | Shadowy soul collector with grim scythe, darkness-slip. |
| Venomancer | Tank / Healer / DPS | Poison Loa Shadra disciple; shapeshifts into poisonous insects. |
| Chronomancer | Ranged DPS / Healer | Time mage: unmake foes, remake (heal) allies, powerful slows. |
| Bloodmage | Tank / Healer / DPS | Sanguine Worgen curse: feral bloodlust vs crimson blood magic. |
| Guardian | Tank / DPS / Support | Stoic knight; Vanguard (tank), Inspiration (support buffs). |
| Stormbringer | Ranged DPS / Support | Lightning mage — wind, thunder, storm support. |
| Felsworn | Tank / DPS | Ex-Legion agent: agile cleaver or chaos caster. Tyrant (tank). |
| Barbarian | Melee DPS / Support | Axe/spear berserker; shares ale buffs with allies. |
| Witch Doctor | Ranged DPS / Healer | Troll voodoo: potions, hexes, dinosaur spirits. Brewing (heal). |
| Witch Hunter | Tank / DPS | Dual crossbows, muskets, glazed blades; monster purger. |
| Knight of Xoroth | Tank / DPS | Hell Knight on dark steed: blades, chains, hooks, hellfire. |
| Templar | Tank / DPS | Martial artist: combo strikes → finishers (blade/staff/fists). |
| Ranger | Ranged DPS / Support | Bow + blade outlaw; war falcons, hunting horns. Farstrider (support). |

## Recreation notes for Bytes Midnight (12.0.7 playerbot server)
- Individual spells: serverside_spell tables (hotfixes DB) + scripted effects — achievable.
- Client-visible names/icons: Arctium --mods db2 injection.
- "Class flavor kits" on existing class chassis is the pragmatic route
  (e.g., Necromancer on Warlock, Chronomancer on Mage, Reaper on DK).
- Spell data source: db.ascension.gg ?spell=ID&power JSON (archiver:
  fetch_ascension.py) — grab formulas from tooltips while site lives.

## Official design pillars (ascension.gg/en/features/new-wow-classes-coa, archived 2026-07-21)
- Dual talent trees (class + spec), spec chosen at level 10, Dragonflight-inspired.
- CC identity per class: Necromancer = fears, Chronomancer = slows; stealth mechanics fitted per class.
- Class counters are lore-driven: Witch Hunter counters Necromancer; Tinker builds defenses; Cultist risks madness from power.
- Itemization: intellect guns, strength throwing weapons, mail tanking gear - thousands of CoA-specific items.
- Each class: unique resource, mechanics, spell visuals, signature abilities.
