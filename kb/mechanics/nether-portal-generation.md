---
title: Nether Portal Generation (Destination Placement)
topic: mechanics
subtopic: portal
tags: [nether_portal, portal_linking, y_coordinate, blind_travel, calculated_travel, dimension]
source_classes:
  - net.minecraft.world.level.PortalForcer
  - net.minecraft.world.entity.Entity
  - net.minecraft.server.level.ServerPlayer
mc_version: 1.16.1
summary: "When a new destination portal is created, the game searches a ±16 XZ radius top-to-bottom for the best-fitting spot, selecting the candidate closest in 3D distance to the arriving entity — and Y is never scaled between dimensions, so your nether Y directly controls how deep the overworld portal spawns."
---

## Overview

When a player crosses a nether portal and no existing portal is found within 128 blocks at the destination, the game runs `PortalForcer.createPortal` to build one. The algorithm does a column-by-column top-to-bottom sweep across a ±16-block horizontal square, collects candidate spots, and picks the one with the smallest 3D distance to the arriving entity. Because only X and Z are scaled by 8× between dimensions — Y is carried over unchanged — the height at which you build your nether-side portal directly determines the height at which the overworld portal spawns.

## Step-by-step logic

1. **Scale X/Z, keep Y.** When crossing the nether boundary, X and Z are multiplied or divided by 8. Y stays the same. The entity used for all subsequent distance calculations is positioned at these scaled coordinates.
2. **Phase 1 — natural fit scan.** For each XZ column within ±16 blocks, sweep from the world ceiling downward. When an air block is found, descend further while air continues — this lands at the *bottom of the topmost contiguous air pocket* in that column (i.e., the surface in open terrain, or the floor of the highest cave). Check whether a standard 4-wide × 5-tall portal frame fits there (solid floor, empty interior). Try all 4 possible orientations, starting from a world-seed-derived offset. Score each valid fit as squared 3D distance to the entity; keep the global minimum.
3. **Phase 2 — reduced fit scan.** If Phase 1 found no valid spot, repeat the same column sweep but check a smaller 2-wide footprint and only 2 orientations. This succeeds in tighter spaces.
4. **Phase 3 — forced placement.** If both scans fail, place the portal at the entity's exact XZ position with Y clamped to **[70, world_height − 10]** (nether: [70, 118]; overworld: [70, 246]).
5. **Build.** Place an obsidian frame (4 wide, 5 tall outer dimensions) and light the portal blocks inside.

## Conditions / Rules

- Existing portal search radius: **128 blocks** (XZ square). `createPortal` is only called if this finds nothing.
- New portal search radius: **±16 blocks XZ** from entity destination.
- Column scan direction: **top to bottom** — each column yields at most one candidate (the bottom of the topmost air gap).
- Winning candidate: **minimum squared 3D distance** from entity. When two candidates tie on distance, lower Y wins (secondary sort).
- Y is **not** scaled: `entity.getY()` at destination = player's Y in source dimension.

## Constants and values

| Parameter | Value |
|---|---|
| Existing portal search radius | 128 blocks (XZ) |
| New portal search radius | ±16 blocks (XZ) |
| Phase 3 forced Y range (nether) | 70 – 118 |
| Phase 3 forced Y range (overworld) | 70 – 246 |
| Coordinate scale factor (overworld ↔ nether) | 8× (X and Z only) |
| Portal interior size | 2 wide × 3 tall |
| Portal frame outer size | 4 wide × 5 tall |

## Edge cases

- **Fully enclosed columns** (no air at all in the 16-block square): Phase 3 triggers; portal is forced at Y 70–118, often inside solid rock. This is rare in normal nether terrain.
- **Bedrock ceiling area (nether y ≈ 117–127)**: The top-down scan immediately lands here for some columns. If these happen to be the closest in 3D, the portal appears near the ceiling — typically inaccessible and considered a "bad" portal.
- **Orientation**: The first orientation tried is `random.nextInt(4)` drawn from a `Random` seeded with the world seed once per dimension. Subsequent portals draw from the same sequence, so orientation is deterministic per seed but not easily predicted in-run.

## Speedrun relevance

### Y is the key lever

Because Y does not scale, **building your nether portal at Y = N causes the overworld portal to prefer candidates near Y = N**.

- In the overworld, open sky columns all yield a candidate at the surface (≈ y 64–100). A cave with a solid ceiling yields a candidate at the cave floor.
- If your entity Y is close to the surface (≈ 64), surface candidates are scored low → **portal appears at ground level**.
- If your entity Y is low (≈ 15–30), a deep cave candidate at y 30 beats a surface candidate at y 80 in squared-distance → **portal appears underground**.

### Blind travel

Goal: arrive in the overworld near the surface to throw ender eyes without wasting time navigating out of a cave.

**Optimal nether build height: y 64–70.** At this height, surface candidates (also ≈ y 64–70) are within a few blocks in Y, beating any deeper cave candidate unless the cave is unusually close in XZ.

### Calculated travel

Goal: arrive inside or immediately above the stronghold so you do not need to dig down.

Stronghold portal rooms generate roughly at overworld y 30–50. To make the portal appear there instead of at the surface, **build your nether portal at the same Y as your target room** (e.g., y 40). The stronghold's hollow rooms create air pockets with solid ceilings, which the top-down scan will find as candidates below the surface candidate. With entity Y ≈ 40, dy to the surface (≈ y 70) ≈ 30, while dy to the stronghold room (≈ y 40) ≈ 0 — the stronghold cavity wins.

Because the exact stronghold room Y varies by seed, runners who know the seed precisely can target the portal room; others typically aim for y 40–50 as a middle estimate.

### General decision framework

| Travel type | Target OW destination | Recommended nether build Y |
|---|---|---|
| Blind travel | Surface (open sky, ender eyes) | 64–70 |
| Calculated travel (approx) | Stronghold interior | 40–50 |
| Calculated travel (known seed) | Exact portal room Y | Match that Y exactly |

## Caveats

- The stronghold portal room Y is not guaranteed — it depends on world generation. Without a seed tool, y 40–50 is a heuristic.
- Terrain irregularities (ravines, lava lakes) affect which surface Y is the actual surface for nearby columns. The portal may still appear a few blocks off your target Y.
- The orientation of the generated portal is deterministic per seed but practically uncontrollable in a normal run.

## Source classes

`PortalForcer` (net.minecraft.world.level) contains the entire search and build logic — `findPortal` for reuse of existing portals, `createPortal` for new portal construction. `Entity.changeDimension` and `ServerPlayer.changeDimension` handle the coordinate scaling: only X and Z are multiplied/divided by 8; Y is passed through verbatim as the entity's destination Y before `createPortal` is called.
