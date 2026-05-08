# KB Index

All articles, their one-sentence summaries, and coverage status.

## World Generation (`worldgen/`)

| Article | Summary | Status |
|---|---|---|
| [Stronghold Placement](./worldgen/stronghold.md) | All 128 strongholds are placed in 8 concentric rings around (0,0) using a Random seeded from the world seed. | complete |

## Entities (`entities/`)

| Article | Summary | Status |
|---|---|---|
| [Piglin Aggression Conditions](./entities/piglin.md) | A piglin targets a player who is visible and not wearing gold armor; block interactions tagged GUARDED_BY_PIGLINS anger idle piglins within 16 blocks. | complete |

## RNG (`rng/`)

| Article | Summary | Status |
|---|---|---|
| [Stronghold RNG and the (0,0) Nether Fossil Identity](./rng/stronghold-rng.md) | Stronghold ring placement seeds a Random directly from the world seed; at chunk (0,0), setLargeFeatureSeed collapses to setSeed(worldSeed), so a (0,0) nether fossil shares the LCG stream. | complete |
| [Structures at Chunk (0,0) That Leak the Stronghold RNG](./rng/zero-zero-chunk-leaks.md) | Only a (0,0) nether fossil leaks a free divine-travel hint (22.5°) fine enough to beat the 120° ring-0 spacing. Every other (0,0) structure stops at 90°, too coarse without seedfinder compute. | complete |

## Physics (`physics/`)

| Article | Summary | Status |
|---|---|---|
| *(none yet)* | | |

## Mechanics (`mechanics/`)

| Article | Summary | Status |
|---|---|---|
| [Nether Portal Generation](./mechanics/nether-portal-generation.md) | When a new destination portal is created, the game searches a ±16 XZ radius top-to-bottom for the best-fitting spot, selecting the candidate closest in 3D distance to the arriving entity — and Y is never scaled between dimensions, so your nether Y directly controls how deep the overworld portal spawns. | complete |
| [Bastion Remnant Loot Tables](./mechanics/bastion-loot.md) | Every bastion type contains generic chests (bastion_other loot table) alongside at most one type-specific chest; generic chests are the only source of regular Obsidian and appear in all four variants. | complete |
