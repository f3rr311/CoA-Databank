# Chassis-Conflict Checklist — run before building ANY CoA class

Tool: `python analyze_deps.py <class>` — first-pass scan for spend/burn chains
and orphan consumers. Combine its output with this manual checklist.

## The 3 failure modes (and their fixed workarounds)

### 1. Missing producer (spender with no builder)
Symptom: an ability consumes/detonates a stack or resource nothing else grants.
Fix: teach the WHOLE chain, not cherry-picked spenders. Since we auto-learn the
full class kit, builders ship with spenders by default. The scanner flags any gap.

### 2. Chassis-foreign mechanic (the big one)
Symptom: ability "Requires <X>" or "consumes <X>" where X is another class's
native system, OR a CoA-custom aura that exists nowhere.
  - If X is native to a DIFFERENT chassis (e.g. "Enraged" = Warrior) and we're
    not on that chassis -> RECREATE X as a custom aura.
  - If X is CoA-custom (Crypt Plague, Deathchill, Parasites, Fill Level,
    Life Force) -> DEFINE it once as a serverside aura; all references then work.
Fix: author the missing aura. Expected work, not a blocker. Do the shared
mechanics FIRST so dependent abilities have something to reference.

### 3. Resource-economy collision (the subtle one)
Symptom: CoA kit generates/spends the SAME resource as the stock chassis
abilities (e.g. Necromancer + DK both use Runic Power) -> shared pool is over-
or under-fueled. Not a broken button, a BALANCE problem.
Fix (pick one):
  a) Retune CoA ability costs against the chassis economy, OR
  b) Give the CoA kit its OWN custom resource (Life Force) so it never competes.
     -> Recommended for casters/hybrids; keeps balance isolated.

## Per-chassis native mechanics (so you know what's "free")
  Death Knight : Runic Power, diseases, Army/ghoul summons
  Rogue/Feral  : Energy, combo points, stealth
  Monk         : Energy, Chi
  Warrior      : Rage, Enrage, shouts
  Shaman       : Mana/Maelstrom, totems (= deployables/turrets)
  Hunter       : Focus, pets (= bots/minions)
  Mage         : Mana, arcane charges
  Warlock      : Mana/soul shards, demon summons
  Evoker       : Essence, empowered casts, Preservation heals

## Necromancer (pilot) findings
Chassis: Death Knight. Native-covered: Runic Power, diseases, ghoul summons.
MUST CREATE as custom auras (shared mechanics - build these first):
  - Crypt Plague (custom disease; built by Lich Bolt, detonated by Foul Expedition)
  - Deathchill stacks (frost build -> Icequake consumes)
  - Parasites (-> Parasitical Experiments)
  - Life Force pool (minion-cap resource; recommend replacing Runic Power for the
    kit to avoid economy collision with stock DK)
Orphan to resolve: "Scourge Transporter" (Summoning Ritual) - provide object or reflavor.

## Build order implication
1. Define shared custom auras FIRST (Crypt Plague, Deathchill, Life Force).
2. THEN build abilities that reference them (spenders/burns work immediately).
3. Run analyze_deps.py again after each batch to catch new orphans.
