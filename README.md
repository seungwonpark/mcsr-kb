# mcsr-kb — Minecraft Speedrunning Knowledge Base

A structured, agent-queryable knowledge base about Minecraft 1.16.1 game logic, derived from decompiled Java source. Covers mechanics relevant to Any% and category speedruns: world generation, RNG, entity behavior, physics, and more.

## Who this is for

- **AI agents** answering speedrunner questions (see [AGENTS.md](AGENTS.md) for navigation instructions)
- **Speedrunners** looking for precise technical explanations of game behavior
- **Route researchers** investigating seed-dependent mechanics

## What's here

```
kb/
├── index.md              ← full topic index with coverage status
├── worldgen/             ← structure placement and terrain generation
├── entities/             ← mob AI, targeting, and hostility rules
├── rng/                  ← Java Random behavior, seed derivation
├── physics/              ← player and entity movement
└── mechanics/            ← specific gameplay systems (portals, loot, etc.)

schemas/
└── article.schema.json   ← frontmatter schema for KB articles

scripts/
└── README.md             ← how to run source-analysis generation scripts
```

## Source material

Articles are derived from decompiled Minecraft 1.16.1 source analyzed with [MinecraftDecompiler](https://github.com/MaxPixelStudios/MinecraftDecompiler). The raw source tree (`mc1.16.1/`) is kept locally and is gitignored — this repo contains only transformed derivative content.

All articles cite the relevant Java class(es) in their frontmatter so claims can be traced back to the source.

## Contributing

1. Run the appropriate script from `scripts/` against your local `mc1.16.1/` tree to extract structured data.
2. Write or update a KB article following the [schema](schemas/article.schema.json) and the conventions in [CLAUDE.md](CLAUDE.md).
3. Add the article to [kb/index.md](kb/index.md).
4. Open a PR — do not commit anything from `mc1.16.1/`.

## Version

All content targets **Minecraft Java Edition 1.16.1**. Article frontmatter records `mc_version` for future multi-version support.

## Disclaimer

This project is an unofficial fan resource and is not affiliated with, endorsed by, or connected to Mojang Studios or Microsoft. Minecraft is a trademark of Mojang Studios. All content is derived from independently decompiled game code for educational and research purposes only.
