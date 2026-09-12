#!/usr/bin/env python3
"""
CoA ability dependency auditor.

For a given class, scans every ability tooltip and finds NAMED mechanics
(buffs / stacks / resources / diseases) that abilities either PRODUCE
(apply/generate/grant) or CONSUME (consume/require/spend/detonate/for each).

Flags:
  - ORPHAN CONSUMERS: ability needs X but no ability in the class produces X
    -> either a missing ability, OR a chassis mechanic we must recreate.
  - Producer/consumer pairs that must ship together (spend+burn chains).

Usage:  python analyze_deps.py necromancer
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
SPELLS = ROOT / "archive" / "spell"
IDS = ROOT / "coa_spell_ids"

# Resources that EXIST natively on common chassis (so not orphans if present).
CHASSIS_NATIVE = {
    "runic power": "Death Knight", "mana": "any caster", "energy": "Rogue/Monk/Feral",
    "rage": "Warrior/Guardian", "focus": "Hunter", "combo points": "Rogue/Feral",
    "chi": "Monk", "fury": "Demon Hunter", "maelstrom": "Shaman",
    "disease": "Death Knight", "diseases": "Death Knight",
    "essence": "Evoker", "holy power": "Paladin",
}

PRODUCE = re.compile(r"\b(appl(?:y|ies|ying)|generat\w*|grant\w*|gain\w*|inflict\w*|"
                     r"add\w*|summon\w*|places?|drops?|causes?)\b", re.I)
CONSUME = re.compile(r"\b(consum\w*|spend\w*|expend\w*|requires?|for each|"
                     r"detonat\w*|per stack|each stack|remov\w*)\b", re.I)


def strip(t):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t or "")).strip()


STOPWORDS = {"rank", "instant", "requires level", "melee", "lasts", "increases",
             "reduces", "deals", "additional", "consumes", "consume", "spend",
             "requires", "generating", "generate", "applies", "apply", "grant",
             "grants", "gain", "gains", "for each", "instantly", "causing",
             "damage", "healing", "target", "enemy", "enemies", "allies",
             "attack power", "spell power", "runic", "cast", "cooldown", "rage",
             "energy", "mana", "focus", "chi", "shadow damage", "frost damage",
             "fire damage", "nature damage", "plague damage", "shadow", "frost",
             "fire", "nature", "physical", "holy", "arcane", "rank 1", "points",
             "points per level"}
SCHOOLS = re.compile(r"^(shadow|frost|fire|nature|arcane|holy|physical|plague)"
                     r"(\s+damage)?$", re.I)


def named_mechanics(text, class_name, ability_names):
    """Named buffs/stacks the tooltip highlights, minus ability/class/school noise."""
    names = set()
    for m in re.finditer(r"\b([A-Z][a-z']+(?:\s+[A-Z][a-z']+){0,2})\b", text):
        p = m.group(1).strip()
        pl = p.lower()
        if pl in STOPWORDS or SCHOOLS.match(pl):
            continue
        if pl == class_name.lower():
            continue
        if pl in ability_names:            # it's the name of an ability, not a mechanic
            continue
        names.add(p)
    for kw in ("runic power", "diseases", "disease", "combo points"):
        if kw in text.lower():
            names.add(kw.title())
    return names


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: analyze_deps.py <classname>")
    cls = sys.argv[1].lower()
    idfile = IDS / f"{cls}.json"
    if not idfile.exists():
        raise SystemExit(f"no id file for {cls}")
    spells = json.loads(idfile.read_text(encoding="utf-8"))["spells"]
    ability_names = {n.lower().split(":")[0].strip() for n in spells.values()}
    ability_names |= {n.lower() for n in spells.values()}

    produced = defaultdict(list)   # mechanic -> [ability names that produce it]
    consumed = defaultdict(list)   # mechanic -> [ability names that consume it]

    for sid, name in spells.items():
        f = SPELLS / f"{sid}.json"
        if not f.exists():
            continue
        text = strip(json.loads(f.read_text(encoding="utf-8")).get("tooltip_enus"))
        low = text.lower()
        mechs = named_mechanics(text, cls, ability_names)
        for mech in mechs:
            ml = mech.lower()
            # find the clause mentioning this mechanic
            idx = low.find(ml)
            window = low[max(0, idx - 40): idx + len(ml) + 20]
            if CONSUME.search(window):
                consumed[mech].append(name)
            if PRODUCE.search(window):
                produced[mech].append(name)

    print(f"\n=== {cls.title()} dependency audit ===\n")
    print("SPEND/BURN CHAINS (mechanic produced AND consumed - must ship together):")
    both = sorted(set(produced) & set(consumed))
    for m in both:
        print(f"  [{m}]")
        print(f"      built by : {', '.join(sorted(set(produced[m]))[:6])}")
        print(f"      spent by : {', '.join(sorted(set(consumed[m]))[:6])}")

    print("\nORPHAN CONSUMERS (needs a mechanic NOTHING here produces):")
    orphans = sorted(set(consumed) - set(produced))
    for m in orphans:
        ml = m.lower()
        native = next((v for k, v in CHASSIS_NATIVE.items() if k in ml), None)
        tag = f"OK - native to {native} chassis" if native else "!! WORKAROUND NEEDED (create this aura ourselves)"
        print(f"  [{m}] needed by {', '.join(sorted(set(consumed[m]))[:4])}")
        print(f"      -> {tag}")

    print(f"\nsummary: {len(both)} spend/burn chains, {len(orphans)} orphan consumers")


if __name__ == "__main__":
    main()
