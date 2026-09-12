# Necromancer Pilot — Level Progression & Minion Design

Chassis: Death Knight (start 8, no starter zone) OR Warlock (start 1).
Recommend **Death Knight** — undead theme, plague/frost already, runes reflavor
to Life Force, Army-of-the-Dead plumbing exists for minions.

Life Force = reflavored resource pool. Minions RESERVE Life Force while alive;
pool caps simultaneous minions. Costs below are assumptions (⚑) tuned by minion power.
All spell IDs are real Ascension spells we archived (formulas on disk).

## Minion cap model
- Total Life Force pool grows with level: 100 at L10 → 300 at L60 (⚑).
- Each active minion reserves its cost; run dry = can't summon more.
- Hard engine backstop: SummonProperties slot limits per minion type
  (e.g. max 1 Frost Wyrm, max 4 Ghouls) so nothing runaway.

## Progression (assumptions ⚑, anchored to CoA "pet army unlocks 30–60")

| Level | Unlock | Spell ID | LF cost | Notes |
|------:|--------|---------|--------:|-------|
| 1  | Lich Bolt (core nuke) | 801942 | — | 64 + ShaP×0.785 Shadow, +50%/disease |
| 4  | Crypt Plague (disease DoT) | 800108 | — | the disease Lich Bolt scales off |
| 8  | Raise: Ghoul (first minion) | 500971 | 40 ⚑ | basic melee pet, cap 4 |
| 10 | **Spec choice** (Death/Animation/Rime) | — | — | opens the tree |
| 14 | Plaguebomb (AoE) | 500340 | — | sustained AoE per class fantasy |
| 18 | Raise: Skeletal Mage | 500331 | 50 ⚑ | ranged caster minion |
| 22 | Bonefreeze / Icequake (control) | 500326/500191 | — | frost CC |
| 26 | Raise: Abomination (tank pet) | 500335 | 70 ⚑ | beefy, cap 1 |
| 30 | Animate: Skeletal Archer | 805040 | 50 ⚑ | Essence bracket begins |
| 34 | Raise: Gargoyle | 500329 | 60 ⚑ | flying DPS, cap 2 |
| 38 | Animate: Crypt Fiend | 801941 | 60 ⚑ | web/slow utility minion |
| 42 | Animate: Bone Wraith | 805032 | 70 ⚑ | elite melee |
| 46 | Animate: Plaguefather | 805048 | 90 ⚑ | 79+1.0/lvl+SP×0.1 plague aura pet |
| 50 | Raise: Decaying Colossus | 500989 | 110 ⚑ | big single elite, cap 1 |
| 54 | Animate: Tomb King | 805044 | 110 ⚑ | commander minion, buffs others ⚑ |
| 58 | **Lich Form** (capstone transform) | 500981 | — | you BECOME the lich; model swap |
| 60 | **Animate: Frost Wyrm** (capstone summon) | 805428 | 150 ⚑ | skeletal dragon, cap 1 — the "dragon" |

## The dragon question (your idea)
Animate: Frost Wyrm (805428) = the level-60 capstone minion — a skeletal
dragon summon (Sindragosa-family DisplayID, full flight animations in client).
Two flavors we can ship, both easy:
  A) COMBAT MINION (canonical CoA): summoned Frost Wyrm fights for ~30s, cap 1,
     heavy Life Force. Faithful.
  B) MOUNT REWARD (your idea): also grant a rideable Frost Wyrm mount at 60 as
     a class capstone — pure cosmetic, trivial (one mount spell + creature).
  → Do BOTH: minion for combat, matching mount as the "you made it" trophy.

## Passives (auto-granted, not summoned)
Death L15 passive (806151), Master of Death (806328), Necrosis (802990),
Blightweaver (806329), Summoning Mastery (805042) — apply as permanent auras
at their level via the trainer.

## Delivery: AUTO-UNLOCK (no trainers — Midnight removed them)
Modern WoW auto-grants class spells on level-up. We replicate exactly:
- Each spell → its own "Necromancy" skill_line (tidy spellbook grouping).
- skill_line_ability row: SkillLine=Necromancy, Spell=<id>, ClassMask=DK,
  AcquireMethod = auto-learn.
- Unlock level = the spell's SpellLevels.BaseLevel (the "Level" column above).
- On ding, TrinityCore's level-up code grants it automatically — same path
  playerbots use, so bot DKs auto-learn the kit too. Zero NPC interaction.

## Build order for the pilot
1. Lich Bolt + Crypt Plague (L1–4): proves damage + disease scaling.
2. Raise: Ghoul + Life Force cap (L8): proves summon + minion limit.
3. Skill-line + skill_line_ability auto-learn wiring (levels from table).
4. Then fill the ladder from the table, formulas already archived.
