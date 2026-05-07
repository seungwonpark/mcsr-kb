#!/usr/bin/env python3
"""
Print a structured summary of a Java class in mc1.16.1/:
  - Class declaration and hierarchy
  - Static final constants with values
  - Method signatures (no bodies)
  - Inner class/enum/interface names
  - Obfuscation note if ☃ identifiers are present

Usage:
  python3 scripts/analyze_class.py StrongholdFeature
  python3 scripts/analyze_class.py net.minecraft.world.level.levelgen.feature.StrongholdFeature
"""

import sys
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent / "mc1.16.1"
SNOWMAN = "☃"

# Visibility modifiers we care about
VISIBILITY = {"public", "protected", "private"}
MODIFIERS = VISIBILITY | {"static", "final", "abstract", "native", "synchronized", "default"}

# Patterns
_CLASS_DECL = re.compile(
    r"^\s*((?:(?:public|protected|private|abstract|final|static)\s+)*)"
    r"(class|interface|enum|@interface)\s+(\w+)"
)
_FIELD = re.compile(
    r"^\s*((?:(?:public|protected|private|static|final|volatile|transient)\s+)+)"
    r"([\w<>\[\]?,\s]+?)\s+(\w+)\s*(?:=\s*(.+?))?\s*;"
)
_METHOD = re.compile(
    r"^\s*((?:(?:public|protected|private|static|final|abstract|native|synchronized|default|override|@Override)\s+)*)"
    r"(?:<[^>]+>\s+)?"                     # optional type params
    r"([\w<>\[\]?,\s.@]+?)\s+"            # return type
    r"(\w+)\s*\(([^)]*)\)"               # name(params)
    r"(?:\s*throws\s+[\w,\s]+)?"          # optional throws
    r"\s*[\{;]"                            # body open or abstract semicolon
)
_INNER = re.compile(
    r"^\s+(?:(?:public|protected|private|static|final|abstract)\s+)*"
    r"(class|interface|enum)\s+(\w+)"
)


def find_file(name: str) -> Path:
    """Accept either a simple name or FQN; return the .java path."""
    if "." in name:
        # Fully qualified: convert dots to path separators
        rel = name.replace(".", "/") + ".java"
        candidate = ROOT / rel
        if candidate.exists():
            return candidate
        # Maybe the name includes the class but the file is nested
        simple = name.split(".")[-1]
    else:
        simple = name

    matches = sorted(ROOT.rglob(f"{simple}.java"))
    if not matches:
        raise FileNotFoundError(f"No file found for '{name}' under {ROOT}")
    if len(matches) > 1:
        print(f"Warning: multiple matches, using first:\n" +
              "\n".join(f"  {m.relative_to(ROOT)}" for m in matches), file=sys.stderr)
    return matches[0]


def strip_body(lines: list[str]) -> list[str]:
    """Remove method bodies, keeping signatures and top-level declarations.

    Emits a line if brace depth is 0 or 1 (top level / class body) at the
    START of that line, then updates depth by counting { and } on the line.
    This preserves method signature lines (which open a { at the end) while
    discarding everything inside the body.
    """
    result = []
    depth = 0
    for line in lines:
        if depth <= 1:
            result.append(line.rstrip())
        depth += line.count("{") - line.count("}")
    return result


def analyze(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    lines = source.splitlines()

    obfuscated = SNOWMAN in source
    fqn_parts: list[str] = []
    constants: list[str] = []
    methods: list[str] = []
    inner_types: list[str] = []
    class_decl: str = ""
    package = ""

    # Package
    for line in lines:
        m = re.match(r"^\s*package\s+([\w.]+)\s*;", line)
        if m:
            package = m.group(1)
            break

    # Strip bodies for cleaner parsing
    skeleton = strip_body(lines)

    top_class_found = False
    for line in skeleton:
        # Class/interface/enum declaration
        m = _CLASS_DECL.match(line)
        if m:
            if not top_class_found:
                class_decl = line.strip()
                top_class_found = True
            else:
                inner_types.append(line.strip())
            continue

        # Static final constants (likely to have meaningful values)
        m = _FIELD.match(line)
        if m:
            mods = m.group(1)
            if "static" in mods and "final" in mods:
                constants.append(line.strip())
            continue

        # Method signatures
        m = _METHOD.match(line)
        if m:
            sig = line.strip()
            # Drop constructor-only noise and annotation-only lines
            if not sig.startswith("@") and "(" in sig:
                methods.append(sig.rstrip("{").strip())

    # Print report
    print(f"=== {path.relative_to(ROOT)} ===")
    print()
    if package:
        print(f"Package : {package}")
    if class_decl:
        print(f"Class   : {class_decl}")
    print()

    if obfuscated:
        snowman_count = source.count(SNOWMAN)
        print(f"⚠ Obfuscation: {snowman_count} ☃ identifier(s) present — "
              f"some names are not recoverable from this decompiled output.")
        print()

    if constants:
        print(f"--- Constants ({len(constants)}) ---")
        for c in constants:
            print(f"  {c}")
        print()

    if methods:
        print(f"--- Methods ({len(methods)}) ---")
        for sig in methods:
            print(f"  {sig}")
        print()

    if inner_types:
        print(f"--- Inner types ({len(inner_types)}) ---")
        for t in inner_types:
            print(f"  {t}")
        print()


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <ClassName|fully.qualified.ClassName>", file=sys.stderr)
        sys.exit(1)

    name = sys.argv[1]
    try:
        path = find_file(name)
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    analyze(path)


if __name__ == "__main__":
    main()
