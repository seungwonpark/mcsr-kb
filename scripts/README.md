# Generation Scripts

Scripts in this directory read from the local `mc1.16.1/` source tree and produce structured KB artifacts. They require a local copy of the decompiled source and are never committed to the public repo with raw source content.

## Prerequisites

- Python 3.9+
- `mc1.16.1/` present at the repo root (gitignored)

```bash
pip install -r scripts/requirements.txt
```

## Available scripts

| Script | Purpose |
|---|---|
| `extract_frontmatter.py` | Extract and validate YAML frontmatter from an article (used in CI schema checks) |
| `analyze_class.py` | Print a structured summary of a Java class's methods and constants — starting point for writing a new article |
| `find_class.py` | Search for a class by simple name across `mc1.16.1/src/` |

## Workflow for a new article

```bash
# 1. Find the relevant class
python3 scripts/find_class.py StrongholdFeature

# 2. Get a structured summary to inform article writing
python3 scripts/analyze_class.py net.minecraft.world.level.levelgen.feature.StrongholdFeature

# 3. Write the article manually in kb/<topic>/<slug>.md
# 4. Validate frontmatter
python3 scripts/extract_frontmatter.py kb/worldgen/stronghold.md
```

## Important

Scripts may read from `mc1.16.1/` but must **never write raw source** (class bodies, method implementations, string literals from source) into the `kb/` directory or any committed file. Derived facts, numeric constants, and behavior descriptions are fine.
