#!/usr/bin/env python3
"""Search mc1.16.1/ for Java source files matching a simple class name."""

import sys
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent / "mc1.16.1"


def find(simple_name: str) -> list[Path]:
    filename = simple_name if simple_name.endswith(".java") else f"{simple_name}.java"
    return sorted(ROOT.rglob(filename))


def fqn_from_file(path: Path) -> str:
    """Derive fully-qualified name from the file's package declaration."""
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("package "):
                pkg = line.removeprefix("package ").rstrip(";").strip()
                return f"{pkg}.{path.stem}"
            if line and not line.startswith("//") and not line.startswith("/*"):
                break
    except (OSError, UnicodeDecodeError):
        pass
    return path.stem


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <SimpleClassName>", file=sys.stderr)
        sys.exit(1)

    name = sys.argv[1]
    matches = find(name)

    if not matches:
        print(f"No match for '{name}' under {ROOT}", file=sys.stderr)
        sys.exit(1)

    for path in matches:
        rel = path.relative_to(ROOT.parent)
        fqn = fqn_from_file(path)
        print(f"{rel}  →  {fqn}")


if __name__ == "__main__":
    main()
