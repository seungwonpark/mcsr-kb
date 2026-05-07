---
title: Stronghold Placement
topic: worldgen
subtopic: structures
tags: [stronghold, eye_of_ender, world_generation, seed, rings, biome]
source_classes:
  - net.minecraft.world.level.chunk.ChunkGenerator
  - net.minecraft.world.level.levelgen.feature.StrongholdFeature
  - net.minecraft.world.level.levelgen.feature.configurations.StrongholdConfiguration
  - net.minecraft.world.level.levelgen.StructureSettings
mc_version: 1.16.1
summary: "All 128 strongholds are placed in 8 concentric rings around (0,0) using a java.util.Random seeded directly from the world seed; their chunk positions are computed before any chunk generates."
confidence: complete
---

## Overview

Every overworld has exactly **128 strongholds** arranged in **8 rings** centered on (0, 0). The positions are computed once (lazily, on first need) by `ChunkGenerator.generateStrongholds()` using a `java.util.Random` seeded with the raw world seed. No chunks need to be generated for seed tools to compute all 128 positions.

The default configuration is defined in `StructureSettings`:
```
StrongholdConfiguration(distance=32, spread=3, count=128)
```

## Placement algorithm

The algorithm iterates over all 128 strongholds in ring order. For each stronghold it:

1. Computes a **radius** in chunk units: `(4·distance + distance·ringIndex·6) + (rnd − 0.5)·distance·2.5`, where `rnd = random.nextDouble()` and `ringIndex` is the 0-based ring number.
2. Computes **chunk X and Z** by projecting the radius along the current angle: `chunkX = round(cos(angle) · radius)`, `chunkZ = round(sin(angle) · radius)`.
3. Searches for the nearest **valid biome** within 112 blocks of that projected block position (via `BiomeSource.findBiomeHorizontal`). If found, the position is snapped to the biome location's chunk.
4. Adds the resulting `ChunkPos` to `strongholdPositions`.
5. Advances the angle by `2π / spread` (where `spread` is the number of strongholds in the current ring).
6. When the current ring is full, increments `ringIndex`, draws a new random angle offset, and recalculates `spread` for the next ring.

## Ring layout

The starting `spread` is 3 (the `spread` field of `StrongholdConfiguration`). After each ring completes, spread grows: `spread += 2·spread / (ringIndex + 1)`, then clamped to the remaining stronghold count.

| Ring | Strongholds | Center radius (chunks) | Radius range (chunks) | Radius range (blocks) |
|------|------------|----------------------|----------------------|----------------------|
| 0 | 3  | 128 | [88, 168] | [1408, 2688] |
| 1 | 6  | 320 | [280, 360] | [4480, 5760] |
| 2 | 10 | 512 | [472, 552] | [7552, 8832] |
| 3 | 15 | 704 | [664, 744] | [10624, 11904] |
| 4 | 21 | 896 | [856, 936] | [13696, 14976] |
| 5 | 28 | 1088 | [1048, 1128] | [16768, 18048] |
| 6 | 36 | 1280 | [1240, 1320] | [19840, 21120] |
| 7 | 9  | 1472 | [1432, 1512] | [22912, 24192] |

Radius is measured as Euclidean distance from (0, 0) to the stronghold's chunk center, in chunk units (multiply by 16 for blocks). The ±40-chunk spread on each ring comes from `(random.nextDouble() − 0.5) · distance · 2.5` = `(rnd − 0.5) · 80`.

Strongholds within a ring are **evenly spaced** in angle (`2π / spread`), all sharing the same random offset drawn at the start of that ring. A new random angle offset is added when transitioning between rings.

## Constants and values

| Parameter | Value | Source |
|---|---|---|
| Total strongholds | 128 | `StructureSettings.DEFAULT_STRONGHOLD` |
| Initial ring size (spread) | 3 | `StrongholdConfiguration(32, 3, 128)` |
| Distance parameter | 32 chunks | `StrongholdConfiguration(32, 3, 128)` |
| Random seed source | world seed (raw) | `ChunkGenerator` constructor 4th arg |
| Biome search radius | 112 blocks | `findBiomeHorizontal` call |
| Ring count | 8 | derived from algorithm |

## Biome filtering

After the geometric position is computed, the game calls `biomeSource.findBiomeHorizontal` to find the nearest valid biome within **112 blocks** of the computed position. Strongholds only generate in biomes where `Biome.isValidStart(StructureFeature.STRONGHOLD)` returns true (all land biomes in standard worldgen; not ocean, not nether/end). If no valid biome is found within 112 blocks the unshifted chunk coordinate is used anyway (this is rare in standard worldgen).

## Edge cases

- **Ring 7 is truncated**: the spread formula would yield 45 for ring 7, but only 9 strongholds remain (128 − 119), so spread is clamped to 9. The ring-7 strongholds are therefore not evenly spaced by 2π/9 — they use whatever spread was set.
- **Chunk alignment**: positions are stored as `ChunkPos` (chunk coordinates), so all strongholds are aligned to chunk boundaries (multiples of 16 blocks).
- **Y coordinate**: `generateStrongholds()` stores only X and Z chunk positions. The Y placement (the structure starts below sea level) is determined at chunk generation time by `StrongholdFeature.StrongholdStart.generatePieces`, which calls `moveBelowSeaLevel` with a margin of 10.

## Speedrun relevance

- **Eye of Ender** traces a 2D vector toward the nearest stronghold's chunk center. Two throws from different positions give two angles; the intersection locates the stronghold chunk.
- **Seed tools** (e.g., Ninjabrain Bot) compute all ring-0 positions directly from the world seed, bypassing the throw requirement.
- Ring 0 is always the Any% target: 3 strongholds within 1408–2688 blocks of spawn.
- Ring-0 strongholds are roughly 120° apart in angle, but the exact angles depend on the world seed's first `nextDouble()` draw.

## Caveats

- The decompiler replaces many identifiers with `☃` snowman symbols. The algorithm above was traced by following the control flow and matching against known constants in `StructureSettings.DEFAULT_STRONGHOLD`. The radius formula and ring-count progression are confirmed by the bytecode constants (`32`, `3`, `128`, `6`, `2.5`, `4`).
- The portal room's block position within the generated structure is determined at generation time by `StrongholdPieces`, not by this placement algorithm. The Eye of Ender targets the chunk center, not the portal room.

## Source classes

`ChunkGenerator.generateStrongholds()` contains the full placement loop and all ring arithmetic. `StructureSettings` holds the default `StrongholdConfiguration(32, 3, 128)`. `StrongholdConfiguration` defines the three parameters. `StrongholdFeature.StrongholdStart.generatePieces` handles the Y-level search and structure piece assembly.
