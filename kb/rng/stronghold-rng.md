---
title: Stronghold RNG and the (0,0) Nether Fossil Identity
topic: rng
subtopic: structures
tags: [stronghold, rng, world_seed, nether_fossil, seedfinding, lcg, starting_angle]
source_classes:
  - net.minecraft.world.level.chunk.ChunkGenerator
  - net.minecraft.world.level.levelgen.WorldgenRandom
  - net.minecraft.world.level.levelgen.feature.StrongholdFeature
  - net.minecraft.world.level.levelgen.structure.StructureStart
  - net.minecraft.world.level.levelgen.structure.NetherFossilFeature
mc_version: 1.16.1
summary: "Stronghold ring placement seeds a Random directly from the world seed; at chunk (0,0), setLargeFeatureSeed collapses to setSeed(worldSeed), so a (0,0) nether fossil shares the LCG stream."
confidence: complete
---

## Overview

Stronghold generation runs three independent RNG streams with very different seeding rules. Knowing which is which matters for seedfinding, for understanding why ring positions shift when biomes change, and for the well-known result that a **nether fossil at chunk (0, 0) leaks information about the stronghold starting angle**.

The three streams, in order of when the game uses them:

1. **Ring placement RNG** — fixes where strongholds sit on the eight rings around (0, 0).
2. **Per-stronghold start RNG** — created by `StructureStart`, but immediately discarded for strongholds.
3. **Maze RNG** — drives the piece-by-piece dungeon layout, including the portal room.

## Layer 1 — Ring placement RNG

Lives in `ChunkGenerator.generateStrongholds()`. It uses a freshly constructed `java.util.Random` (not `WorldgenRandom`), seeded with one line:

```
random.setSeed(this.strongholdSeed)
```

`strongholdSeed` is the raw world seed passed to the `ChunkGenerator` constructor. There is no salt, no chunk-coord scrambling, no codec — it is the simplest possible seeding.

The first random call is the famous **starting angle**:

```
double startAngle = random.nextDouble() * 2π
```

For each of the 128 strongholds the algorithm then draws:

1. `random.nextDouble()` for the radial jitter `(rnd − 0.5) · distance · 2.5`.
2. RNG calls inside `BiomeSource.findBiomeHorizontal(...)` — **the same `Random` is passed in**, so biome sampling consumes RNG and shifts every later stronghold's position. This is why "what biome ate the search" matters.

After every `spread` strongholds the angle is reset with another `random.nextDouble() * 2π` offset.

Because there is exactly one `setSeed(worldSeed)` and no further reseeding, every byte of the 128-stronghold layout is a deterministic function of the world seed and the biome map.

## Layer 2 — Per-stronghold start RNG (discarded)

`StructureStart` (the base class for every structure's start object) seeds its `this.random` field in its constructor:

```
this.random.setLargeFeatureSeed(worldSeed, chunkX, chunkZ)
```

For most structures (fossils, mineshafts, fortresses, ruined portals, etc.) this is the RNG used to lay out their pieces. For strongholds it is **immediately overwritten** on the next line of `StrongholdFeature.StrongholdStart.generatePieces`, so this layer effectively does not exist for strongholds.

## Layer 3 — Stronghold maze RNG

`StrongholdFeature.StrongholdStart.generatePieces` retries the entire maze layout in a `do…while` loop until a portal room appears. Each retry reseeds:

```
this.random.setLargeFeatureSeed(worldSeed + iter, strongholdChunkX, strongholdChunkZ)
```

where `iter` increments per retry. This RNG drives:

- The weighted piece picker (`StrongholdPieces.generatePieceFromSmallDoor`) — its 5-attempt retry loop.
- Random orientation, door type, and child-piece spawning for every corridor, library, and five-way crossing.
- Whether and where the portal room piece is added; if no portal room appears, the start re-runs with `iter + 1`.

Because the seed depends on `chunkX`, `chunkZ`, and `iter`, every stronghold gets a unique-but-deterministic maze. The chunk coordinates are nonzero (rings 0–7 are 88–1512 chunks from origin), so the maze RNG is **not** equal to a plain `setSeed(worldSeed)`.

## How `setLargeFeatureSeed` works

The function is in `WorldgenRandom`:

```
setSeed(worldSeed)
long a = nextLong()
long b = nextLong()
long finalSeed = chunkX * a ⊕ chunkZ * b ⊕ worldSeed
setSeed(finalSeed)
```

Two important properties:

- The intermediate `nextLong()` calls are wiped out by the final `setSeed(finalSeed)`. The output state is **purely** a function of `finalSeed`.
- When `chunkX = chunkZ = 0`, both `chunkX · a` and `chunkZ · b` are zero, so `finalSeed = worldSeed`. The whole transformation collapses to a no-op: `setSeed(worldSeed) … setSeed(worldSeed)`.

## The (0, 0) chunk identity

The community discovery referenced by speedrunners follows directly from the property above.

**Nether fossil at chunk (0, 0).** `NetherFossilFeature.FeatureStart`'s `this.random` is seeded by the `StructureStart` constructor as `setLargeFeatureSeed(worldSeed, 0, 0)`. By the identity above, after this call the Random's internal state is **bit-identical** to a freshly constructed `new Random()` followed by `setSeed(worldSeed)` — including Java's internal `^ 0x5DEECE66DL` scramble, since both code paths apply it.

**Stronghold ring placement.** `ChunkGenerator.generateStrongholds()` does exactly `new Random()` then `setSeed(worldSeed)` and starts pulling.

**The two RNG streams therefore step the same LCG sequence from the same starting state.** They differ only in how many bits each call consumes:

| Call site | Method | Underlying `next()` calls |
|---|---|---|
| Stronghold first call | `nextDouble()` | `next(26)` then `next(27)` (2 steps) |
| Fossil first call | `nextInt(16)` | `next(31)` (1 step, since 16 is a power of two) |
| Fossil second call | `nextInt(16)` | `next(31)` (1 step) |
| Fossil third call | `nextInt(buildHeight − 2 − seaLevel)` = `nextInt(94)` | `next(31)`, possibly with rejection-sampling retries |

Observing a (0, 0) fossil's local `(x, y, z)` therefore constrains the LCG state, which in turn constrains the stronghold starting angle (and every subsequent stronghold draw) for the same world seed.

## Constants and values

| Symbol | Value | Where |
|---|---|---|
| `setLargeFeatureSeed` reduction at chunkX=chunkZ=0 | `setSeed(worldSeed)` | `WorldgenRandom.setLargeFeatureSeed` |
| Stronghold ring placement seed | raw world seed | `ChunkGenerator.generateStrongholds`, line `setSeed(this.strongholdSeed)` |
| Stronghold maze seed | `setLargeFeatureSeed(worldSeed + iter, cx, cz)` | `StrongholdFeature.StrongholdStart.generatePieces` |
| Java `Random` internal scramble | `seed ^ 0x5DEECE66DL & ((1L << 48) − 1)` | `java.util.Random.setSeed` |
| `Random.nextDouble()` consumption | `next(26)` then `next(27)` | `java.util.Random.nextDouble` |
| `Random.nextInt(2^k)` consumption | one `next(31)` | `java.util.Random.nextInt` |

## Edge cases

- **Only `setLargeFeatureSeed`-seeded structures benefit from the (0, 0) identity.** Structures that use `setLargeFeatureWithSalt` (villages, pillager outposts, ruined portals, etc., for their *placement* check) include an additive salt and a different formula, so even at chunk (0, 0) they do **not** collapse to `setSeed(worldSeed)`.
- **Strongholds themselves are never at chunk (0, 0).** Ring 0 starts roughly 88 chunks out, so the (0, 0) identity links the *fossil's* RNG to the *stronghold ring placement* RNG, not to a stronghold's maze RNG.
- **Any structure start at chunk (0, 0) leaks the same information.** Buried treasure, shipwreck, ocean ruin, etc. all use `StructureStart`'s constructor and inherit the identity. Nether fossils were just the canonical example because they are small, place their seed-sensitive layout in one chunk, and expose coordinates directly.
- **The biome-search step inside ring placement consumes additional RNG.** A bit-perfect prediction of layer-1 RNG draws past the starting angle requires modeling those biome-source calls; tools like Ninjabrain Bot do.

## Speedrun relevance

- **Seedfinding from a (0, 0) fossil:** observing the fossil's chunk-local coordinates yields a small set of LCG states consistent with three or four `next(31)` outputs, which then determine the world seed (with help from a small lattice / brute-force step). Once the seed is known, every stronghold ring position is computable.
- **Same trick for any (0, 0) `setLargeFeatureSeed` structure.** Buried treasure, shipwreck, ocean ruin at chunk (0, 0) work identically. Nether fossils are convenient because they are visible, common in the nether, and trivial to coordinate-read.
- **Stronghold maze RNG is *not* leaked by the (0, 0) identity.** The maze depends on the stronghold's actual chunk coordinates (far from origin), so its piece layout is a separate problem from ring placement. The two are linked only through the shared world seed.
- **The starting angle is the most valuable layer-1 output.** It is the very first `nextDouble()` after `setSeed(worldSeed)`, so it is the easiest stronghold quantity to predict from any (0, 0) leak.

## Caveats

- Decompiler artifacts (`☃` placeholders) prevented direct reading of variable names in `setLargeFeatureSeed`; the formula was reconstructed from the operator structure and the constants `0`, `0xFFFFFFFFFFFFL`, plus the call to `setSeed`. The reconstruction matches the published Mojang behavior in 1.14+.
- The exact bit-width of `nextInt(94)` consumption depends on rejection sampling and may consume more than one `next(31)` step on some seeds.
- This article describes 1.16.1 only. The algorithm is unchanged through 1.17 but salts and constants drift in later versions; the (0, 0) identity itself is a generic property of `setLargeFeatureSeed` and survives across versions that keep the same formula.

## Source classes

`ChunkGenerator.generateStrongholds()` contains the layer-1 ring placement loop and is where the world seed is fed to a fresh `java.util.Random`. `WorldgenRandom.setLargeFeatureSeed` is the ten-line method that contains the identity at the heart of the (0, 0) discovery; reading it makes the result obvious. `StructureStart`'s constructor is where the layer-2 reseeding happens for every structure, including nether fossils. `StrongholdFeature.StrongholdStart.generatePieces` is where layer-3 (maze RNG) reseeds and where the portal-room retry loop lives. `NetherFossilFeature.FeatureStart.generatePieces` is the consumer of the (0, 0)-collapsed Random and is the structure that historically exposed the leak.
