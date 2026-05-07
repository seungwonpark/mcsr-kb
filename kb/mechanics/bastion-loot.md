---
title: Bastion Remnant Loot Tables
topic: mechanics
subtopic: loot
tags: [bastion, loot, crying_obsidian, obsidian, gold, iron, arrows, string, nether]
source_classes:
  - net.minecraft.data.loot.ChestLoot
  - net.minecraft.world.level.storage.loot.BuiltInLootTables
  - net.minecraft.world.level.levelgen.feature.BastionPieces
mc_version: 1.16.1
summary: "Every bastion type contains generic chests (bastion_other loot table) alongside at most one type-specific chest; generic chests are the only source of regular Obsidian and appear in all four variants."
---

## Overview

Bastion Remnants come in four structural variants: **Bridge**, **Hoglin Stable**, **Housing Units**, and **Treasure Room**. All four variants share one crucial mechanic: every bastion generates **generic chests** using the `chests/bastion_other` loot table throughout its structure, in addition to (at most) one type-specific specialty chest type. `BuiltInLootTables` registers four bastion-specific IDs, all defined in `ChestLoot`:

| Loot table ID | Chest label | Appears in |
|---|---|---|
| `chests/bastion_other` | Generic | **All 4 variants** (primary chest in Housing Units; secondary in the other three) |
| `chests/bastion_bridge` | Bridge | Bridge bastions only |
| `chests/bastion_hoglin_stable` | Hoglin Stable | Hoglin Stable bastions only |
| `chests/bastion_treasure` | Treasure | Treasure Room bastions only |

This is why regular Obsidian appears in all bastion types — it comes from the generic (`bastion_other`) chests, not from any specialty table.

## Chest distribution by bastion type

Exact counts come from the NBT structure templates (not readable from Java source), but the Minecraft Wiki's structure documentation confirms the following approximate counts:

| Bastion type | Generic chests | Specialty chests | Total |
|---|---|---|---|
| Bridge | ~3–4 | 1 (bridge) | ~4–5 |
| Hoglin Stable | ~6 | 2–3 (stable) | ~8–9 |
| Housing Units | ~all | 0 | varies |
| Treasure Room | some | 1–2 (treasure) | varies |

Housing Units is the bastion type with no specialty chest — every chest in it uses the generic table.

## Loot table contents (1.16.1)

All pool data is sourced from `ChestLoot.java`. Items without an explicit `setWeight` call have weight 1. `EmptyLootItem` entries are noted as *empty*. Expected value = avg\_rolls × (weight / total\_weight) × avg\_count.

---

### Generic (`chests/bastion_other`) — in every bastion variant

**Pool A** — 1 roll (fixed), total weight 100:

| Item | Count | Weight | P(picked) | Expected per chest |
|---|---|---|---|---|
| Enchanted Crossbow (10–50% dmg) | 1 | 12 | 12% | 0.12 |
| Ancient Debris | 1 | 2 | 2% | 0.02 |
| Netherite Scrap | 1 | 2 | 2% | 0.02 |
| **Spectral Arrow** | **2–15** | **16** | **16%** | **1.36** |
| Piglin Banner Pattern | 1 | 5 | 5% | 0.05 |
| Music Disc Pigstep | 1 | 3 | 3% | 0.03 |
| Soul Speed Enchanted Book | 1 | 10 | 10% | 0.10 |
| *Empty* | — | 50 | 50% | — |

**Pool B** — 2 rolls (fixed), total weight 12:

| Item | Count | Weight | Expected per chest |
|---|---|---|---|
| Soul Speed Golden Boots | 1 | 1 | 0.17 |
| Gold Block | 1 | 1 | 0.17 |
| Crossbow | 1 | 1 | 0.17 |
| **Gold Ingot** | **1–6** | **1** | **0.58** |
| **Iron Ingot** | **1–6** | **1** | **0.58** |
| Golden Sword | 1 | 1 | 0.17 |
| Golden Chestplate | 1 | 1 | 0.17 |
| Golden Helmet | 1 | 1 | 0.17 |
| Golden Leggings | 1 | 1 | 0.17 |
| Golden Boots | 1 | 1 | 0.17 |
| *Empty* | — | 2 | — |

**Pool C** — 3–5 rolls (avg 4), total weight 11 (Arrow has weight 2; all others weight 1):

| Item | Count | Weight | Expected per chest |
|---|---|---|---|
| **Crying Obsidian** | **1–5** | **1** | **1.09** |
| Gilded Blackstone | 1–5 | 1 | 1.09 |
| Chain | 2–10 | 1 | 2.18 |
| Magma Cream | 2–6 | 1 | 1.45 |
| Bone Block | 3–6 | 1 | 1.64 |
| Iron Nugget | 2–8 | 1 | 2.18 |
| **Obsidian** | **4–6** | **1** | **1.82** |
| Gold Nugget | 2–8 | 1 | 2.18 |
| **String** | **4–6** | **1** | **1.82** |
| **Arrow** | **5–17** | **2** | **8.00** |

---

### Bridge specialty (`chests/bastion_bridge`) — Bridge bastions only, ~1 per bastion

**Pool A** — 1 roll (fixed): always **Lodestone ×1** (only entry, 100% guaranteed).

**Pool B** — 1–2 rolls (avg 1.5), total weight 12 (all items weight 1):

| Item | Count | Expected per chest |
|---|---|---|
| Enchanted Crossbow (10–50% dmg) | 1 | 0.13 |
| **Spectral Arrow** | **2–12** | **0.88** |
| Gilded Blackstone | 5–8 | 0.79 |
| **Crying Obsidian** | **3–8** | **0.69** |
| Gold Block | 1 | 0.13 |
| **Gold Ingot** | **2–8** | **0.63** |
| **Iron Ingot** | **2–8** | **0.63** |
| Golden Sword | 1 | 0.13 |
| Enchanted Golden Chestplate | 1 | 0.13 |
| Enchanted Golden Helmet | 1 | 0.13 |
| Enchanted Golden Leggings | 1 | 0.13 |
| Enchanted Golden Boots | 1 | 0.13 |

**Pool C** — 2–4 rolls (avg 3), total weight 5 (all items weight 1):

| Item | Count | Expected per chest |
|---|---|---|
| **String** | **1–6** | **2.10** |
| Leather | 1–3 | 1.20 |
| **Arrow** | **5–17** | **6.60** |
| Iron Nugget | 2–6 | 2.40 |
| Gold Nugget | 2–6 | 2.40 |

---

### Hoglin Stable specialty (`chests/bastion_hoglin_stable`) — Hoglin Stable bastions only, ~2–3 per bastion

**Pool A** — 1 roll (fixed), total weight 105:

| Item | Count | Weight | Expected per chest |
|---|---|---|---|
| Diamond Shovel (ench, 15–45% dmg) | 1 | 5 | 0.048 |
| Netherite Scrap | 1 | 2 | 0.019 |
| Ancient Debris | 1 | 3 | 0.029 |
| Saddle | 1 | 10 | 0.095 |
| Gold Block | 2–4 | 25 | 0.714 |
| Enchanted Golden Hoe | 1 | 15 | 0.143 |
| *Empty* | — | 45 | — |

**Pool B** — 3–4 rolls (avg 3.5), total weight 12 (all items weight 1):

| Item | Count | Expected per chest |
|---|---|---|
| Glowstone | 1–5 | 0.875 |
| Gilded Blackstone | 1–5 | 0.875 |
| Soul Sand | 2–7 | 1.313 |
| Crimson Nylium | 2–7 | 1.313 |
| Gold Nugget | 2–8 | 1.458 |
| Leather | 1–3 | 0.583 |
| **Arrow** | **5–17** | **3.21** |
| **String** | **3–8** | **1.60** |
| Porkchop | 2–5 | 1.021 |
| Cooked Porkchop | 2–5 | 1.021 |
| Crimson Fungus | 2–7 | 1.313 |
| Crimson Roots | 2–7 | 1.313 |

*No Obsidian, Crying Obsidian, Gold Ingot, or Iron Ingot in this table.*

---

### Treasure specialty (`chests/bastion_treasure`) — Treasure Room bastions only, 1–2 per bastion

**Pool A** — 1–2 rolls (avg 1.5), total weight 100:

| Item | Count | Weight | Expected per chest |
|---|---|---|---|
| Netherite Ingot | 1 | 10 | 0.15 |
| Ancient Debris | 1 | 14 | 0.21 |
| Netherite Scrap | 1 | 10 | 0.15 |
| Ancient Debris | 2 | 1 | 0.03 |
| Enchanted Diamond Sword (20–65% dmg) | 1 | 10 | 0.15 |
| Enchanted Diamond Chestplate | 1 | 6 | 0.09 |
| Enchanted Diamond Helmet | 1 | 6 | 0.09 |
| Enchanted Diamond Leggings | 1 | 6 | 0.09 |
| Enchanted Diamond Boots | 1 | 6 | 0.09 |
| Diamond Sword (unenchanted) | 1 | 6 | 0.09 |
| Diamond Chestplate (unenchanted) | 1 | 5 | 0.075 |
| Diamond Helmet (unenchanted) | 1 | 5 | 0.075 |
| Diamond Boots (unenchanted) | 1 | 5 | 0.075 |
| Diamond Leggings (unenchanted) | 1 | 5 | 0.075 |
| Diamond | 1–3 | 5 | 0.15 |

**Pool B** — 2–4 rolls (avg 3), total weight 9 (all items weight 1):

| Item | Count | Expected per chest |
|---|---|---|
| **Spectral Arrow** | **5–21** | **4.33** |
| Gold Block | 2–5 | 1.17 |
| **Gold Ingot** | **3–9** | **2.00** |
| **Iron Ingot** | **3–9** | **2.00** |
| **Crying Obsidian** | **1–5** | **1.00** |
| Quartz | 8–23 | 5.17 |
| Gilded Blackstone | 1–5 | 1.00 |
| Magma Cream | 2–8 | 1.67 |
| Iron Nugget | 8–16 | 4.00 |

*No regular Arrow, no String in this table.*

---

## Summary: key items across all chest types

Expected values are **per single chest of that type**. Multiply by the chest count per bastion to get per-bastion totals.

| Item | Generic (all types) | Bridge specialty | Stable specialty | Treasure specialty |
|---|---|---|---|---|
| **Obsidian** | **1.82** | 0 | 0 | 0 |
| **Crying Obsidian** | **1.09** | 0.69 | 0 | 1.00 |
| Arrow (regular) | **8.00** | 6.60 | 3.21 | 0 |
| Spectral Arrow | 1.36 | 0.88 | 0 | **4.33** |
| Gold Ingot | 0.58 | 0.63 | 0 | **2.00** |
| Iron Ingot | 0.58 | 0.63 | 0 | **2.00** |
| String | 1.82 | 2.10 | 1.60 | 0 |

Because every bastion has multiple generic chests, the generic column is the most important in practice — multiply by 3–6 depending on the variant and layout.

## Edge cases

- Pool A of the Bridge specialty always yields Lodestone ×1 (single-entry pool with a fixed roll of exactly 1 — no RNG).
- Hoglin Stable Pool A has a 45/105 ≈ 42.9% chance of producing nothing.
- Generic Pool A has a 50% chance of producing nothing.
- Regular Obsidian appears **only in the generic table** (Pool C, 4–6 per stack). No other bastion table contains it.
- The Treasure specialty has no regular Arrow and no String at all.
- Arrow in Generic Pool C has weight 2 while everything else is weight 1, giving it a 2/11 ≈ 18% pick rate per roll — roughly double any other entry in that pool.

## Speedrun relevance

- **Obsidian availability**: Regular Obsidian comes exclusively from generic chests (`bastion_other`), which appear in all 4 bastion types. Every bastion visit can yield Obsidian regardless of type — Housing Units has the most such chests, but Bridge and Hoglin Stable also have 3–6 generic chests.
- **Crying Obsidian**: Generic chests (all types), Bridge specialty, and Treasure specialty all provide it. The highest single-chest expected count is the Bridge specialty (3–8 per stack), but generic chests are more numerous.
- **Arrows**: Generic chests are the best source (avg 8.0 per chest from Pool C). Hoglin Stable has many generic chests on top of its 3.2-per-chest stable specialty, making it the best variant for total arrow count.
- **Gold/Iron Ingots**: Treasure specialty dominates (avg 2.0 each per chest); generic and bridge specialty give under 1 per chest. Housing Units variants, despite having no specialty chest, offer ingots from their many generic chests.
- **String**: Generic chests (1.82), Bridge specialty (2.10), Stable specialty (1.60). Treasure has none.
- **Netherite/Ancient Debris**: Only in specialty chests (Treasure Pool A, Hoglin Stable Pool A) — not in generic chests.

## Caveats

- **This is 1.16.1 data from `ChestLoot.java`**. Bastion loot tables were updated in later 1.16.x patches. The current Minecraft Wiki shows more pools per table (5 for Bridge, 4 for Stable) than are present in 1.16.1 (3 for Bridge, 2 for Stable). Do not use wiki loot table data for 1.16.1 runs.
- **Exact generic chest counts per bastion** come from the NBT structure templates (binary `.nbt` files in the vanilla jar, not in the decompiled source). Figures in the distribution table above are approximate, sourced from the Minecraft Wiki's structure documentation for the Bridge (~3–4 generic) and Hoglin Stable (~6 generic) variants. Housing Units and Treasure Room generic counts are unconfirmed from source.
- The four bastion variants are selected with equal probability (weight 60 each in `BastionPieces.POOLS`).
- Chest layout within a variant is jigsaw-assembled from randomly chosen sub-templates, so actual chest counts can vary by layout.

## Source classes

`ChestLoot` contains the complete loot pool definitions for all four bastion chest tables. `BuiltInLootTables` registers the four `ResourceLocation` IDs. `BastionPieces` confirms the four structural start pools. The mapping from "generic chest" to `chests/bastion_other` and its presence across all variants is documented on the Minecraft Wiki's Bastion Remnant/Structure page; the NBT templates encoding this are not present in the decompiled source.
