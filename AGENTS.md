# AGENTS.md — Instructions for AI Agents

This file tells AI agents how to navigate and use this knowledge base to answer Minecraft speedrunning questions.

## What this KB covers

Minecraft Java Edition **1.16.1** game logic relevant to speedrunning. Content is derived from decompiled source and is organized to answer precise technical questions — not gameplay tips.

## Directory structure

| Path | Contents |
|---|---|
| `kb/index.md` | Master topic index; start here for discovery |
| `kb/worldgen/` | Structure placement (strongholds, fortresses, bastions, villages) and terrain |
| `kb/entities/` | Mob AI, aggression conditions, targeting, pathfinding |
| `kb/rng/` | Java `Random` mechanics, seed derivation, manipulable RNG chains |
| `kb/physics/` | Player velocity, collision, water/lava movement, elytra |
| `kb/mechanics/` | Portal linking, loot tables, enchanting, fire resistance, etc. |

## Article format

Every article is a Markdown file with YAML frontmatter:

```yaml
---
title: <human-readable title>
topic: <worldgen|entities|rng|physics|mechanics>
subtopic: <optional finer category>
tags: [<relevant keywords>]
source_classes:
  - <fully.qualified.ClassName>   # Java class(es) this article is derived from
mc_version: 1.16.1
summary: <one-sentence answer — read this first>
---
```

The `summary` field is a direct, one-sentence answer to the implied question. Read it first; read the body only if you need detail or edge cases.

## How to answer a user question

1. **Check `kb/index.md`** for the relevant topic. Each entry links to the article and shows its `summary`.
2. **Read the linked article**. The `summary` field answers the question at a glance; the article body provides conditions, edge cases, and implementation details.
3. **Translate to plain language**. Users are speedrunners, not Java programmers — describe behavior, not code. You may name the source class (e.g., "according to `StrongholdStructure`") to establish credibility, but do not quote Java.
4. **Flag gaps**. If a topic has no article, say so explicitly and indicate what the article would need to cover. Do not invent mechanics.

## Reading the source classes field

`source_classes` lists the Java classes that were analyzed to write the article. If a user asks a follow-up not covered in the article, these are the right classes to examine in `mc1.16.1/` to extend coverage.

## Topic quick-reference

### World generation questions
- "Where are strongholds?" → `kb/worldgen/stronghold.md`
- "Where do nether fortresses spawn?" → `kb/worldgen/nether-fortress.md`
- "How are bastions placed?" → `kb/worldgen/bastion.md`
- "How does biome affect structure placement?" → `kb/worldgen/biome-structure-filter.md`

### Entity behavior questions
- "When do piglins attack?" → `kb/entities/piglin.md`
- "When do endermen become hostile?" → `kb/entities/enderman.md`
- "How does piglin bartering work?" → `kb/entities/piglin-bartering.md`

### RNG questions
- "How does Java Random work?" → `kb/rng/java-random.md`
- "How is the world seed used for structure placement?" → `kb/rng/structure-seed-derivation.md`
- "Can loot be manipulated?" → `kb/rng/loot-table-rng.md`

### Physics questions
- "What is the max sprint speed?" → `kb/physics/player-movement.md`
- "How does water affect velocity?" → `kb/physics/water-movement.md`

### Mechanics questions
- "How does nether portal linking work?" → `kb/mechanics/portal-linking.md`
- "How does ender pearl landing work?" → `kb/mechanics/ender-pearl.md`

## Confidence and version notes

- All articles are pinned to **1.16.1**. Behavior in other versions may differ.
- Where article confidence is partial (e.g., a field was obfuscated), the article body notes it explicitly under a **Caveats** section.
- If an article's `mc_version` does not match the version being asked about, state the version mismatch before answering.

## What this KB does not cover

- Bedrock Edition (different codebase)
- Versions other than 1.16.1 (unless a `mc_version` field says otherwise)
- Subjective routing decisions (use community resources for those)
- Mods or external tools
