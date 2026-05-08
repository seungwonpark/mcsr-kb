---
title: Structures at Chunk (0,0) That Leak the Stronghold RNG
topic: rng
subtopic: structures
tags: [zero_zero, divine_travel, stronghold, seedfinding, lcg, buried_treasure, shipwreck, pyramid, igloo, ocean_ruin, mineshaft, ruined_portal]
source_classes:
  - net.minecraft.world.level.levelgen.WorldgenRandom
  - net.minecraft.world.level.levelgen.feature.StructureFeature
  - net.minecraft.world.level.levelgen.structure.StructureStart
  - net.minecraft.world.level.levelgen.feature.BuriedTreasureFeature
  - net.minecraft.world.level.levelgen.feature.ShipwreckFeature
  - net.minecraft.world.level.levelgen.feature.DesertPyramidFeature
  - net.minecraft.world.level.levelgen.feature.JunglePyramidFeature
  - net.minecraft.world.level.levelgen.feature.IglooFeature
  - net.minecraft.world.level.levelgen.structure.OceanRuinFeature
  - net.minecraft.world.level.levelgen.feature.MineshaftFeature
  - net.minecraft.world.level.levelgen.feature.RuinedPortalFeature
mc_version: 1.16.1
summary: "Only a (0,0) nether fossil leaks a free divine-travel hint (22.5°) fine enough to beat the 120° ring-0 spacing. Every other (0,0) structure stops at 90°, too coarse without seedfinder compute."
confidence: complete
---

## Overview

Divine travel — the technique that produced the world's first sub-10 RSG record — works because a nether fossil at chunk (0, 0) shares an LCG state with the stronghold starting-angle RNG. The same identity applies to **every** structure whose start uses the default `StructureStart` constructor, since that constructor unconditionally runs `setLargeFeatureSeed(worldSeed, chunkX, chunkZ)` and the formula collapses to `setSeed(worldSeed)` at chunk (0, 0).

A natural follow-up question is whether the more common spawn-area structures — shipwrecks, igloos, ocean ruins, pyramids, villages, ruined portals — give the same trick. The bit-level identity says yes, the practical answer says **no**: the fossil is the only (0, 0) structure whose first random call leaks enough bits of `s1` to actually disambiguate strongholds without running a seedfinder.

This article documents both the universal identity (which holds for every structure) and the practical conclusion (which only the fossil clears).

For the underlying identity (`chunkX * a ^ chunkZ * b ^ worldSeed → worldSeed` when `chunkX = chunkZ = 0`), see [Stronghold RNG and the (0,0) Nether Fossil Identity](./stronghold-rng.md).

## The honest conclusion: only the fossil works for free divine travel

**The 60° threshold.** Ring 0 contains three strongholds at angles `θ`, `θ + 120°`, `θ + 240°`. To pin down which of the three is closest to a chosen direction, the player needs a wedge size of at most **60°** (half the inter-stronghold spacing). Anything coarser than 60° leaves at least two ring-0 strongholds inside the same wedge, defeating the purpose.

**The bit budget for free hints.** The angle's high half is the top 26 bits of `s1` (the LCG state after the first advancement of `setSeed(worldSeed)`). A wedge size of `360° / 2^k` requires `k` clean prefix bits of `s1`. The only way to read prefix bits cleanly is for the structure's **first** `this.random` call to be a power-of-two `nextInt(N)` with `N ≥ 2^k`.

| Wedge target | Bits of `s1` needed | First-call bound |
|---|---|---|
| 180° (half-plane) | 1 | `nextInt(2)` or `nextFloat() < 0.5` |
| 90° (quadrant) | 2 | `nextInt(4)` |
| **60° threshold for ring-0** | **≥ 3** | **`nextInt(8)` or larger** |
| 45° (octant) | 3 | `nextInt(8)` |
| 22.5° (Ninjabrain wedge) | 4 | `nextInt(16)` |

**Survey of every (0, 0)-eligible structure's first call.** The 1.16.1 source places exactly one structure above the 60° line:

| Structure | First call | Bits of `s1` | Free wedge | Beats 60°? |
|---|---|---|---|---|
| **Nether fossil** | `nextInt(16)` for x | **4** | **22.5°** | **yes** |
| Shipwreck | `nextInt(4)` rotation | 2 | 90° | no |
| Desert / jungle pyramid | `nextInt(4)` orientation | 2 | 90° | no |
| Igloo | `nextInt(4)` rotation | 2 | 90° | no |
| Ocean ruin | `nextInt(4)` rotation | 2 | 90° | no |
| Village / bastion / outpost | `nextInt(4)` jigsaw rotation | 2 | 90° | no |
| Ruined portal (jungle/standard/mountain/nether) | `nextFloat() < 0.5F` | 1 | 180° | no |
| Buried treasure | (no call) | 0 | none | no |

**Why only the fossil clears the bar.** Every other speedrun-relevant structure starts at a fixed in-chunk position and uses its first random call for an N-of-4 rotation pick. The fossil is the lone exception because its position-within-chunk is itself randomised: the `nextInt(16)` for x-coordinate is a side effect of "where in this chunk does the fossil go," and 16 happens to be the next power-of-two boundary above 4. That single accident in `NetherFossilFeature.FeatureStart.generatePieces` is the entire reason divine travel is a thing.

**Why stacking does not save the others.** Every (0, 0) structure gets a fresh `WorldgenRandom` re-seeded with the same `setSeed(worldSeed)`. Every one's first call therefore reads from the same `s1`. A shipwreck's 2 prefix bits are a strict subset of a fossil's 4. Observing a (0, 0) shipwreck *and* a (0, 0) fossil tells you nothing the fossil did not already tell you. There is no second free observation hiding elsewhere.

**Two non-free escape hatches.** If the player accepts seedfinder computation, two doors open:

1. **Mineshaft jackpot.** Mineshaft's placement check at chunk (0, 0) is `nextDouble() < 0.004` reading directly from `setSeed(worldSeed)` (because mineshaft uses the un-salted `setLargeFeatureSeed` for its filter — the only structure that does so). If a mineshaft *exists* at (0, 0), the top ~8 bits of `s1` are zero and the angle is pinned to about 1.4°. Prior probability ≈ 0.4%, so this is opportunistic.
2. **Compute the rest.** A shipwreck's full observation (rotation 2 bits + template 3.5–4.3 bits via modular constraint on `s2`) is enough to brute-force the world seed in finite time. This crosses out of "free wedge" territory and into seedfinder-tool territory.

The rest of this article documents the bit-level mapping for completeness — useful if you want to write a (0, 0)-shipwreck seedfinder, or you are doing a seed analysis after the fact. **It is not a list of techniques players can use mid-run without a tool.**

## Two RNG layers, one structure

Every chunk-aligned structure goes through two seeded `WorldgenRandom` streams:

1. **Placement-region RNG** (`StructureFeature.getPotentialFeatureChunk`). Decides which chunk inside a `spacing × spacing` region holds the structure. Seeded with `setLargeFeatureWithSalt(worldSeed, regionX, regionZ, salt)`. At region (0, 0) this collapses to `setSeed(worldSeed + salt)` — **not** `setSeed(worldSeed)`. The `salt` is structure-specific (e.g. buried treasure uses `10387320`).
2. **Piece RNG** (`StructureStart` constructor). Seeded with `setLargeFeatureSeed(worldSeed, chunkX, chunkZ)`. At chunk (0, 0) collapses to `setSeed(worldSeed)`. **Every** structure at chunk (0, 0) shares this starting LCG state.

A few structures have a third per-chunk filter (`isFeatureChunk`) with its own seeding rule. Mineshafts are the only common one whose filter uses the un-salted `setLargeFeatureSeed` and therefore also collapses at (0, 0).

The stronghold starting angle is the **first `nextDouble()`** out of `setSeed(worldSeed)`. Any (0, 0) piece-RNG observation that constrains those first few `next(31)` outputs constrains the angle.

## Per-structure leak inventory (for seedfinder authors)

The total observable bits below describe the full piece-generation RNG that a (0, 0) structure exposes. **None of these except the fossil's first call translate to a useful free wedge** — they all require a seedfinder pass to extract angle predictions.

| Structure | First piece-RNG calls | Total observable bits (with compute) |
|---|---|---|
| **Nether fossil** | `nextInt(16)`, `nextInt(16)`, `nextInt(94)`, then rotation and template | ~14.5 |
| **Mineshaft** | placement `nextDouble()` then full piece tree | dozens |
| **Ruined portal** | many `nextFloat() < 0.5`, several `nextInt(array)` | 15+ |
| **Ocean ruin** | rotation, `nextFloat()` for large/small, template index, optional cluster sub-rolls | 10–20 |
| **Shipwreck** | rotation (`nextInt(4)`), template index (`nextInt(11)` or `nextInt(20)`) | 6–7 |
| **Igloo** | rotation, `nextDouble() < 0.5` for lab, `nextInt(8) + 4` for lab depth | 7 |
| **Village** | jigsaw rotation, root template index, jigsaw expansion | medium-many |
| **Pillager outpost** | jigsaw rotation, root template index, jigsaw expansion | medium |
| **Desert pyramid** | `Direction.Plane.HORIZONTAL.getRandomDirection` only | 2 |
| **Jungle pyramid** | same | 2 |
| **Buried treasure** | none | 0 |
| **Nether fortress** | `nextInt` for piece tree | many |

These bit counts feed seedfinder tools (Ninjabrain Bot, SeedcrackerX) — they are not directly readable as wedges. The free wedge each structure offers is in the table further up; see "The honest conclusion" above.

## Reading the bits — for completeness

For seedfinder authors and post-hoc seed analysis. The same identity can be expressed as a one-line rule: **the top bits of `s1`** (the LCG state after the first advancement of `setSeed(worldSeed)`) **are the top bits of the stronghold angle's high half `a_hi`**. Any first `this.random` call that exposes the top `k` bits of `s1` narrows the angle to `360° / 2^k`.

The visible signal each structure exposes (for use in a tool, not as a free wedge):

| Structure at (0, 0) | First `this.random` call | Top bits of `s1` revealed | Wedge if used directly | Visible signal |
|---|---|---|---|---|
| **Nether fossil** | `nextInt(16)` for x-coord | 4 | **22.5°** (1 of 16) | fossil's x within the chunk |
| Shipwreck | `nextInt(4)` for rotation | 2 | 90° | mast/hull orientation |
| Desert pyramid | `nextInt(4)` for orientation | 2 | 90° | front-face direction |
| Jungle pyramid | `nextInt(4)` for orientation | 2 | 90° | front-face direction |
| Igloo | `nextInt(4)` for rotation | 2 | 90° | door direction |
| Ocean ruin | `nextInt(4)` for rotation | 2 | 90° | template orientation |
| Village | `nextInt(4)` for jigsaw rotation | 2 | 90° | central building rotation |
| Bastion | `nextInt(4)` for jigsaw rotation | 2 | 90° | layout orientation |
| Pillager outpost | `nextInt(4)` for jigsaw rotation | 2 | 90° | watchtower orientation |
| Ruined portal (jungle/standard/mountain/nether) | `nextFloat() < 0.5F` for airPocket / underground | 1 | 180° | visible airpocket / underground placement |
| Buried treasure | (no call) | 0 | — | — |

### Quadrant decoder (only of analytical interest)

Every rotation-based row above resolves the same way, because each one's first random call is `Util.getRandom(values, this.random) = values[nextInt(4)]` with the four values stored in a fixed N/E/S/W order:

| Visible orientation | Top 2 bits of `s1` | Implied first-ring direction from (0, 0) |
|---|---|---|
| NORTH / NONE | `00` | NE quadrant (0° – 90°) |
| EAST / CW 90° | `01` | SE quadrant (90° – 180°) |
| SOUTH / CW 180° | `10` | SW quadrant (180° – 270°) |
| WEST / CCW 90° | `11` | NW quadrant (270° – 360°) |

This table is correct, but a 90° quadrant on its own does not help a player choose a direction — see the honest conclusion above.

### Why stacking different (0, 0) structures does not help

Every structure at (0, 0) gets a fresh `WorldgenRandom` seeded with the same `setSeed(worldSeed)` and starts at state_0. Each one's first call reads from the same `s1`. A fossil reads 4 prefix bits of `s1`; a shipwreck at (0, 0) reads 2 prefix bits of the same `s1`. The shipwreck's bits are a subset of the fossil's. Multiple (0, 0) structures **do not stack** for free wedge narrowing.

What can stack is information from *different RNG advancements*. The fossil's three calls each hit a different state (`s1`, `s2`, `s3`), so its three observations are independent. A second structure at (0, 0) would only help if its observable RNG calls hit advancements *not* used by the fossil — none of the surveyed structures do this in their first few calls.

## Mapping a (0,0) shipwreck to the stronghold angle

Worked example. Both the shipwreck and the stronghold ring placement read from the same `setSeed(worldSeed)` LCG. Let `s1` be the 48-bit state after the first advancement and `s2` after the second.

**Stronghold starting angle** = `nextDouble() · 2π`. `nextDouble()` consumes two advancements:

- `next(26)` → top 26 bits of `s1` (call this `a_hi`).
- `next(27)` → top 27 bits of `s2` (call this `a_lo`).

The angle is `((a_hi << 27) | a_lo) / 2^53 · 2π`.

**Shipwreck observation** consumes the same two advancements with different bit widths:

- `nextInt(4)` (rotation) → top 2 bits of `next(31)` of `s1` = **top 2 bits of `s1`** = top 2 bits of `a_hi`.
- `nextInt(11)` (beached) or `nextInt(20)` (ocean) for the template → `next(31) mod N` of `s2`. Rejection probability ≈ 5 × 10⁻⁹, so effectively `s2.top31 mod N`.

### Rotation → quadrant (clean and free)

The top 2 bits of `a_hi` partition `[0, 2π)` into four equal arcs:

| Rotation | `s1` top-2 | Angle range | First-stronghold direction from origin |
|---|---|---|---|
| `NONE` | `00` | 0° – 90° | NE |
| `CLOCKWISE_90` | `01` | 90° – 180° | SE |
| `CLOCKWISE_180` | `10` | 180° – 270° | SW |
| `COUNTERCLOCKWISE_90` | `11` | 270° – 360° | NW |

Just spotting a (0,0) shipwreck's mast orientation pins down which quadrant the first-ring strongholds are in. The other two ring-0 strongholds are at +120° and +240° from the first (the per-stronghold angle increment is `2π / spread = 2π / 3` plus radial jitter), so the whole first-ring layout's quadrant pattern follows.

### Template → modular constraint on the low half

Observing beached template index `T ∈ [0, 11)` constrains `s2.top31 ≡ T (mod 11)`. Since `a_lo = s2.top27 = s2.top31 >>> 4`, the allowed values of `a_lo` form a "comb": `s2.top31` lies on a residue class mod 11, and `a_lo` is a contiguous block of 16 values per accepted `s2.top31`. The result is a non-contiguous set of angle fine-positions within each rotation-determined quadrant.

This second observation does not map to a clean angle wedge. To use it, a seedfinder enumerates `(s1, s2)` pairs consistent with the rotation and template, then walks the LCG step backwards to recover candidate `worldSeed` values.

### Bit budget vs the canonical fossil

| Observation | Constraint | Effective bits | Maps to angle? |
|---|---|---|---|
| Fossil x (`nextInt(16)`) | top 4 bits of `s1` | 4 | yes — refines `a_hi` directly |
| Fossil z (`nextInt(16)`) | top 4 bits of `s2` | 4 | yes — refines `a_lo` directly |
| Fossil y (`nextInt(94)`) | `s3.top31 mod 94` | ~6.5 | partial (third advancement, no angle effect) |
| **Shipwreck rotation** | top 2 bits of `s1` | 2 | **yes — direct quadrant** |
| Shipwreck template (beached) | `s2.top31 mod 11` | ~3.5 | comb on `a_lo` |
| Shipwreck template (ocean) | `s2.top31 mod 20` | ~4.3 | comb on `a_lo` |

Fossil total ≈ 14.5 bits of constraint on the 2⁴⁸-state seed space → typically ~10 candidate seeds remain after brute force. Shipwreck total ≈ 5.5–6.3 bits → ~10¹² candidate seeds remain — still tractable on modern hardware but no longer "instant" like the fossil case.

Two big practical wins of the shipwreck mapping anyway:

- The **rotation alone** narrows the angle to a 90° quadrant with no computation — no seedfinder needed, just look at the mast.
- A (0,0) shipwreck plus another (0,0) observation (e.g. a nearby buried treasure that confirms the placement-RNG salt, or a visible biome boundary) compounds well with the fossil-style approach when the player happens to be near both.

### Edge case — the fossil's third advancement is "free" angle constraint

A subtle reason the fossil is so good: its third call (`nextInt(94)` for y) constrains `s3`, but `s3` is the *third* advancement, after `nextDouble()` has already consumed `s1` and `s2`. `s3` doesn't directly affect the angle — but it indirectly restricts the seed space because the LCG transition `seed → s1 → s2 → s3` is deterministic. Knowing `s3` modulo 94 narrows `seed` candidates beyond what `s1` and `s2` constrain alone. Shipwrecks have no equivalent third call, so they cannot exploit this extra constraint.

## Notes on individual structures

### Buried treasure — the false friend

Speedrunners encounter buried treasure constantly, and the chunk it sits in is small and recognisable. But `BuriedTreasureStart.generatePieces` adds **a single piece at a fixed offset** (`(chunkX*16 + 9, 90, chunkZ*16 + 9)`) and never reads `this.random`. Its loot table is rolled later from a separate per-chest seed.

So a (0, 0) buried treasure leaks **no piece-RNG bits**. Knowing it exists at (0, 0) only confirms `setSeed(worldSeed + 10387320).nextFloat() < 1.0`, which is true for every seed (its probability is 1.0). It does not narrow the world seed.

### Shipwreck — the practical alternative to the fossil

`ShipwreckFeature.FeatureStart.generatePieces` calls `Rotation.getRandom(this.random)` (a `nextInt(4)`) and then `ShipwreckPieces.addPieces` picks a template via `nextInt(11)` (beached pool) or `nextInt(20)` (ocean pool). That's six to seven observable bits from a structure that is small, walkable in seconds, and very common at spawn.

Caveat: an ocean shipwreck sits underwater, but the rotation and template are visible from above by the silhouette of the mast/hull.

### Ocean ruin — the richest "natural" source

`OceanRuinPieces.addPieces` reads rotation, then `nextFloat() <= largeProbability` for size, then a template index. If the cluster roll passes, several more sub-ruins are placed, each consuming additional rotation and `Mth.nextInt` calls. A single (0, 0) ocean ruin can fix the LCG state to a tiny candidate set on its own.

### Mineshaft — both layers collapse

Mineshaft is unique among 1.16.1 structures: its `isFeatureChunk` calls `setLargeFeatureSeed(worldSeed, chunkX, chunkZ)` (the *un-salted* form) and then a `nextDouble() < probability` check. At chunk (0, 0) the placement check itself reads from `setSeed(worldSeed)`. Combined with the piece RNG (also `setSeed(worldSeed)`), a (0, 0) mineshaft leaks RNG from two independent draws of the same starting LCG. The mineshaft maze that follows consumes a great deal of additional RNG.

The catch is that surface-mineshafts at chunk (0, 0) require a mesa biome at spawn and are rare. Mineshafts in caves are abundant but their layout is harder to read directly.

### Pyramids — orientation only

Both desert and jungle pyramids inherit `ScatteredFeaturePiece`, whose constructor calls `Direction.Plane.HORIZONTAL.getRandomDirection(random)` once. That is the only `this.random` read before placement; everything afterward uses fixed coordinates. So a (0, 0) pyramid only leaks two bits (which of N/E/S/W the entrance faces). On its own that is far too few to seedfind from.

A pyramid plus an independent observation (e.g. a nearby fossil, a visible biome boundary) might still be useful in combination, but a pyramid alone is not.

### Pillager outpost — non-standard placement seeding

`PillagerOutpostFeature.isFeatureChunk` does **not** use `setLargeFeatureWithSalt`. It seeds with `setSeed((regionX ^ regionZ << 4) ^ worldSeed)`, calls `nextInt()`, then `nextInt(5) != 0`. At region (0, 0) the outer XOR collapses too: `(0 ^ (0 << 4)) ^ worldSeed = worldSeed`, so this also reduces to `setSeed(worldSeed)` followed by `nextInt(); nextInt(5)`. That is **another** independent leak of the same LCG state (different bits than the piece RNG draws), even before piece generation begins.

The piece RNG itself, via the standard `StructureStart` path, then again starts from `setSeed(worldSeed)`. A (0, 0) outpost is therefore an unusually rich source — though outposts at exactly chunk (0, 0) are uncommon.

### Village — JigsawPlacement RNG

Villages use `BeardedStructureStart` whose constructor still calls `setLargeFeatureSeed(worldSeed, 0, 0) → setSeed(worldSeed)` at the origin chunk. `VillagePieces.addPieces` calls `JigsawPlacement.addPieces` which consumes a rotation and a starting-template index, then expands the jigsaw graph with many further `nextInt`s. The first few draws are the most useful because they are easiest to read (rotation of the central piece, identity of the central building).

### Nether fortress — same identity, nether decoration

Nether fortresses use the standard `StructureStart` constructor, so a (0, 0) fortress's piece RNG starts at `setSeed(worldSeed)`. The fortress maze consumes `this.random.nextInt(piecePool.size())` calls heavily. The catch is that a fortress chunk-spacing region containing chunk (0, 0) does occur, and within that region `nextInt(5) < 2` (the per-chunk filter) again reads from a `setSeed(worldSeed + salt)`-derived stream. So the same leak applies in the nether.

## Constants and values

| Item | Value | Where |
|---|---|---|
| Stronghold-angle LCG seed | `worldSeed` | `ChunkGenerator.generateStrongholds` |
| Piece-RNG seed at any chunk (0, 0) | `worldSeed` | `StructureStart` constructor + `WorldgenRandom.setLargeFeatureSeed` |
| Buried treasure placement salt | `10387320` | `BuriedTreasureFeature.isFeatureChunk` |
| Mineshaft placement seeding | `setLargeFeatureSeed(worldSeed, cx, cz)` (un-salted!) | `MineshaftFeature.isFeatureChunk` |
| Pillager outpost placement seeding | `setSeed((regionX ^ regionZ << 4) ^ worldSeed)` | `PillagerOutpostFeature.isFeatureChunk` |
| Stronghold-angle first call | `nextDouble()` (= `next(26)` then `next(27)`) | `ChunkGenerator.generateStrongholds` |
| Nether fossil first calls | `nextInt(16)`, `nextInt(16)`, `nextInt(94)` | `NetherFossilFeature.FeatureStart.generatePieces` |
| Shipwreck first calls | `nextInt(4)` rotation, `nextInt(11)` or `nextInt(20)` template | `ShipwreckFeature.FeatureStart` + `ShipwreckPieces.addPieces` |
| Igloo first calls | `nextInt(4)` rotation, `nextDouble()`, `nextInt(8)` (lab depth) | `IglooFeature.FeatureStart` + `IglooPieces.addPieces` |

## Edge cases

- **The structure must actually exist at chunk (0, 0).** Most seeds do not place any specific structure at exactly that chunk; the spacing of villages, shipwrecks, etc. means a structure typically appears once per `~24–32` chunk region. The (0, 0) leak is rare per structure but cumulative across structure types.
- **The salts in `setLargeFeatureWithSalt` decouple structures' placement RNG from `setSeed(worldSeed)`.** Two different (0, 0) structures' *placement* checks therefore read from `setSeed(worldSeed + saltA)` and `setSeed(worldSeed + saltB)` — different LCG streams. Their *piece* RNGs both start at `setSeed(worldSeed)` and so produce correlated observations (offset by the bits already consumed before any observable call).
- **Strongholds at chunk (0, 0).** Cannot happen — the inner ring starts ~88 chunks out — so the maze RNG is never observable through the (0, 0) identity. The (0, 0) trick only links to the *ring-placement* RNG (and thus the starting angle), never to any specific stronghold's interior.
- **Decoration features (ores, plants, lakes) at chunk (0, 0)** use `WorldgenRandom.setDecorationSeed` and `setFeatureSeed`, not `setLargeFeatureSeed`. Those formulas do **not** collapse at chunk (0, 0); they have their own salts and chunk-coord scrambling.
- **Buried treasure cannot itself be used for divine travel** despite being the most common (0, 0) candidate. Players who happen to stand on a (0, 0) buried treasure should look for a nearby (0, 0) shipwreck or fossil instead.

## Speedrun relevance

- **For free, no-tool divine travel: only the nether fossil works.** This is the practical bottom line. A (0, 0) fossil's x-coordinate-within-chunk pins the stronghold angle to a 22.5° wedge; that is finer than the 60° threshold needed to disambiguate ring-0 strongholds at 120° spacing. No other (0, 0) structure clears that bar without computation.
- **Other (0, 0) structures are dead ends without a seedfinder.** Shipwrecks, igloos, ocean ruins, villages, pyramids, bastions, and outposts all stop at a 90° quadrant. A 90° wedge contains either one or two ring-0 strongholds depending on `θ`, so the player still does not know which direction to walk. Spotting a (0, 0) shipwreck does not give actionable angle information mid-run.
- **The (0, 0) mineshaft jackpot.** A mineshaft at chunk (0, 0) is a ~1-in-250 event but provides the strongest possible single observation, pinning the angle to about 1.4°. Worth recognising if it ever happens, but not something to plan around.
- **Seedfinder pipeline.** Tools like Ninjabrain Bot / SeedcrackerX can take any of the (0, 0) observations in this article, brute-force the LCG state, recover the world seed, and derive every ring-0 angle. This crosses out of "free wedge" territory; with a tool, every (0, 0) structure becomes useful, ranked roughly: mineshaft > ruined portal ≈ ocean ruin > shipwreck > village > igloo > nether fortress > pyramid > buried treasure (zero bits).
- **Players cannot "force" a structure to (0, 0).** The placement decision is fixed by the seed long before the player joins. Divine travel is opportunistic: you exploit it when it happens, not on demand.

## Caveats

- This article describes 1.16.1 only. The salts of individual structures, the spacing/separation defaults, and the exact piece-RNG draw order all drift across versions. The (0, 0) collapse of `setLargeFeatureSeed` itself is a generic property and survives in every version that keeps the `chunkX * a ^ chunkZ * b ^ worldSeed` formula.
- Bit counts in the per-structure table are **observable upper bounds** based on the first few RNG draws. Real seedfinding tools may use fewer or more depending on which features are easy to read in-game without breaking blocks.
- Decompiler artifacts in `WorldgenRandom` mean the formula reading was reconstructed from operator structure (see the [stronghold-rng article](./stronghold-rng.md) caveats). The formula matches Mojang's published behaviour in 1.14+.
- "Region (0, 0)" for placement-RNG purposes means `floorDiv(chunkX, spacing) = floorDiv(chunkZ, spacing) = 0`, i.e. chunks 0 through `spacing-1` along each axis. Only chunks where `regionX = regionZ = 0` collapse the placement RNG; the *piece* RNG collapse is stricter and requires the chunk itself to be exactly (0, 0).

## Source classes

`WorldgenRandom.setLargeFeatureSeed` is the single method whose XOR formula collapses at chunk (0, 0); reading it makes every leak in this article obvious. `StructureStart`'s constructor is the universal seeding point — every structure that subclasses it inherits the (0, 0) identity for its piece RNG. `StructureFeature.getPotentialFeatureChunk` is where placement-region RNG is seeded with `setLargeFeatureWithSalt`, which does **not** collapse at (0, 0); the per-structure salts are listed in their respective `*Configuration` classes. The per-structure piece classes (`BuriedTreasurePieces`, `ShipwreckPieces`, `OceanRuinPieces`, `IglooPieces`, `MineShaftPieces`, etc.) are where the actual piece-RNG draws happen and govern how many observable bits each structure leaks.
