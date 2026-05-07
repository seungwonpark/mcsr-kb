---
title: Piglin Aggression Conditions
topic: entities
subtopic: hostility
tags: [piglin, aggression, gold, nether, hostility, bartering, guarded_by_piglins]
source_classes:
  - net.minecraft.world.entity.monster.piglin.PiglinAi
  - net.minecraft.world.entity.monster.piglin.Piglin
  - net.minecraft.world.entity.ai.sensing.PiglinSpecificSensor
  - net.minecraft.world.level.block.Block
  - net.minecraft.data.tags.BlockTagsProvider
mc_version: 1.16.1
summary: "Piglins target any visible player not wearing gold armor; opening or breaking a GUARDED_BY_PIGLINS block angers all idle piglins within 16 blocks regardless of armor."
confidence: complete
---

## Overview

Piglin hostility has two independent mechanisms:

1. **Passive sensor detection** — every tick, `PiglinSpecificSensor` scans visible entities and stores the nearest non-gold-wearing player in the `NEAREST_TARGETABLE_PLAYER_NOT_WEARING_GOLD` memory. During the IDLE activity, `StartAttacking` consumes this memory and sets the piglin to attack.
2. **Triggered block events** — specific player actions call `PiglinAi.angerNearbyPiglins()`, directly setting the attack target on nearby idle piglins regardless of their current sensor state.

## Passive detection: armor check

`PiglinAi.isWearingGold(LivingEntity)` iterates all four armor slots and returns `true` if any slot contains an `ArmorItem` made of `ArmorMaterials.GOLD`. One piece of gold armor in any slot (helmet, chestplate, leggings, or boots) is sufficient to suppress passive aggression.

The sensor only queues the player in `NEAREST_TARGETABLE_PLAYER_NOT_WEARING_GOLD` if:
- The player is in `VISIBLE_LIVING_ENTITIES` (i.e., the piglin has line of sight to the player), **and**
- `EntitySelector.ATTACK_ALLOWED` passes (player is not in creative/spectator), **and**
- `isWearingGold` returns `false`.

The actual attack starts only when the piglin is in **IDLE** activity — a piglin already in FIGHT, CELEBRATE, or another non-idle activity will not pick up the sensor result until it returns to IDLE.

## Triggered aggression: GUARDED_BY_PIGLINS blocks

`Block.playerWillDestroy` checks if the broken block is tagged `GUARDED_BY_PIGLINS` and calls `PiglinAi.angerNearbyPiglins(player, false)` — no line-of-sight check required.

Opening certain containers calls `PiglinAi.angerNearbyPiglins(player, true)` — line-of-sight **is** required.

**GUARDED_BY_PIGLINS block tag** (from `BlockTagsProvider`):

| Block | Trigger |
|---|---|
| `gold_block` | break only |
| `chest` | open **or** break |
| `trapped_chest` | open **or** break |
| `barrel` | open **or** break |
| `ender_chest` | open **or** break |
| All shulker boxes | open **or** break |
| `gilded_blackstone` | break only |
| `gold_ore` | break only |
| `nether_gold_ore` | break only |

*"Open" triggers come from the individual block classes with `requireLineOfSight=true`; "break" triggers come from `Block.playerWillDestroy` with `requireLineOfSight=false`.*

## How angerNearbyPiglins works

```
radius: player.getBoundingBox().inflate(16.0)   // ~16 blocks from player edge
filter: PiglinAi.isIdle(piglin)                 // only IDLE piglins are affected
filter: !requireLineOfSight || canSee(piglin, player)
action: setAngerTarget(piglin, player)
         → sets ANGRY_AT = player UUID, expiry 600 ticks (30 s)
         → if universalAnger gamerule: sets UNIVERSAL_ANGER, expiry 600 ticks
```

Only **idle** piglins are targeted by this call. Piglins already in FIGHT or other activities are not affected.

## ANGRY_AT memory and duration

`setAngerTarget` stores the player's UUID in the `ANGRY_AT` brain memory with an expiry of **600 ticks (30 seconds)**. After expiry, the piglin returns to IDLE and re-evaluates targets via the sensor on the next tick.

If the player puts on gold armor after being set as a `ANGRY_AT` target, the **already-angered** piglins will continue attacking until the memory expires. Gold armor only prevents NEW piglins from being attracted via the passive sensor; it does not clear existing `ANGRY_AT` memories.

## Anger broadcast

`broadcastAngerTarget` is called after `wasHurtBy` (when a piglin is attacked). It propagates the attack target to all adult piglins in `NEAREST_ADULT_PIGLINS` memory (populated from `LIVING_ENTITIES`, not limited to visible ones). This broadcast is not subject to the `inflate(16.0)` radius limit — it uses the sensor's pre-computed list.

## PIGLIN_REPELLENTS

`PiglinSpecificSensor` also scans within 8 horizontal and 4 vertical blocks for blocks tagged `PIGLIN_REPELLENTS`. A piglin with this memory set will flee regardless of player actions.

**PIGLIN_REPELLENTS block tag**:
- `soul_fire`
- `soul_torch`
- `soul_wall_torch`
- `soul_lantern`
- `soul_campfire` (only if lit, checked via `CampfireBlock.isLitCampfire`)

## Zombification

`Piglin.isConverting()` returns true if the piglin is not in a `piglinSafe` dimension and is not `immuneToZombification`. Each server tick that this is true increments `timeInOverworld`. When `timeInOverworld > 300` (15 seconds), `finishConversion` is called and the entity converts to `ZombifiedPiglin`.

Zombified piglins are a separate entity type and do not share aggression state with piglins.

## Conditions that do NOT aggravate Piglins

| Situation | Result |
|---|---|
| Wearing any one piece of gold armor | Passive sensor does not queue player |
| Picking up gold items from the ground | No trigger |
| Throwing gold ingots (bartering) | No trigger |
| Walking near (not opening/breaking) a chest | No trigger |
| Attacking a zombified piglin | Does not affect piglin aggression |
| Player in spectator mode | `ATTACK_ALLOWED` fails; not targeted |

## Speedrun relevance

- A **single piece of gold armor** in any slot fully suppresses passive detection. Runners use a gold helmet as the cheapest suppressor.
- **Opening a chest** in a bastion still aggravates piglins that can see the player — gold armor does not protect against container-interaction triggers.
- After the `ANGRY_AT` memory expires (30 seconds), the piglin returns to IDLE and will re-evaluate. If the player has since equipped gold armor, the piglin will not re-attack passively.
- Soul speed torches placed around a trading area will cause piglins to flee, preventing bartering.

## Caveats

- The exact range used by `VISIBLE_LIVING_ENTITIES` (populated by `SensorType.NEAREST_LIVING_ENTITIES`) is not read here; that sensor's maximum range should be checked separately to determine the maximum passive detection distance.
- The `angerNearbyPiglins` call uses `player.getBoundingBox().inflate(16.0)`, which is an axis-aligned box, not a sphere — the actual detection volume is approximately a 33×33 block area in X/Z.

## Source classes

`PiglinAi` contains `isWearingGold`, `angerNearbyPiglins`, `setAngerTarget`, `findNearestValidAttackTarget`, and `broadcastAngerTarget`. `PiglinSpecificSensor.doTick` populates `NEAREST_TARGETABLE_PLAYER_NOT_WEARING_GOLD` each tick. `BlockTagsProvider` defines the `GUARDED_BY_PIGLINS` and `PIGLIN_REPELLENTS` tags. `Block.playerWillDestroy` is the hook that fires on any block break.
