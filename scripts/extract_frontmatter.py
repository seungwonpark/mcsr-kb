#!/usr/bin/env python3
"""
Extract and validate YAML frontmatter from a KB article.

Without --validate: prints frontmatter as JSON (pipe to ajv-cli for schema validation).
With --validate: checks required fields inline and exits non-zero on failure.

Usage:
  python3 scripts/extract_frontmatter.py kb/worldgen/stronghold.md
  python3 scripts/extract_frontmatter.py --validate kb/worldgen/stronghold.md
  python3 scripts/extract_frontmatter.py kb/  # validate all articles in a directory
"""

import sys
import json
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML not installed. Run: pip install PyYAML", file=sys.stderr)
    sys.exit(1)

REQUIRED_FIELDS = ["title", "topic", "tags", "source_classes", "mc_version", "summary"]
VALID_TOPICS = {"worldgen", "entities", "rng", "physics", "mechanics"}
VALID_CONFIDENCE = {"complete", "partial", "stub"}


def extract_frontmatter(path: Path) -> dict:
    """Return parsed frontmatter dict, or raise ValueError if not found."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError("No frontmatter found (file does not start with ---)")
    end = text.index("\n---", 3)
    raw = text[3:end].strip()
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise ValueError("Frontmatter did not parse as a YAML mapping")
    return data


def validate(data: dict, path: Path) -> list[str]:
    errors: list[str] = []

    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"missing required field '{field}'")

    topic = data.get("topic")
    if topic and topic not in VALID_TOPICS:
        errors.append(f"invalid topic '{topic}' (expected one of {sorted(VALID_TOPICS)})")

    confidence = data.get("confidence")
    if confidence and confidence not in VALID_CONFIDENCE:
        errors.append(f"invalid confidence '{confidence}' (expected one of {sorted(VALID_CONFIDENCE)})")

    tags = data.get("tags")
    if isinstance(tags, list):
        bad = [t for t in tags if not re.fullmatch(r"[a-z0-9_\-]+", str(t))]
        if bad:
            errors.append(f"tags must be lowercase snake_case, bad: {bad}")

    summary = data.get("summary", "")
    if isinstance(summary, str) and len(summary) > 200:
        errors.append(f"summary is {len(summary)} chars (max 200)")

    return errors


def process_file(path: Path, do_validate: bool) -> bool:
    try:
        data = extract_frontmatter(path)
    except (ValueError, yaml.YAMLError) as e:
        print(f"ERROR {path}: {e}", file=sys.stderr)
        return False

    if do_validate:
        errors = validate(data, path)
        if errors:
            for e in errors:
                print(f"FAIL  {path}: {e}")
            return False
        else:
            print(f"OK    {path}")
            return True
    else:
        # JSON output for piping to ajv
        print(json.dumps(data, indent=2, default=str))
        return True


def main() -> None:
    args = sys.argv[1:]
    do_validate = "--validate" in args
    paths_raw = [a for a in args if not a.startswith("-")]

    if not paths_raw:
        print(f"Usage: {sys.argv[0]} [--validate] <file.md|directory> ...", file=sys.stderr)
        sys.exit(1)

    files: list[Path] = []
    for raw in paths_raw:
        p = Path(raw)
        if p.is_dir():
            files.extend(sorted(p.rglob("*.md")))
        elif p.is_file():
            files.append(p)
        else:
            print(f"Not found: {raw}", file=sys.stderr)
            sys.exit(1)

    # Filter out index.md and non-article files
    files = [f for f in files if f.name != "index.md"]

    ok = True
    for f in files:
        if not process_file(f, do_validate):
            ok = False

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
