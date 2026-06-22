#!/usr/bin/env python3
"""Structural validator for ``writing/eval.tex`` (CMP-05, SC3).

A stdlib-only stand-in for a ``pdflatex`` build (no local LaTeX toolchain). It
follows the ``\\input``/``\\include`` graph from ``writing/eval.tex`` and checks
two things that would otherwise only surface at compile time:

  1. **Reference resolution** — every ``\\ref``/``\\Cref``/``\\cref``/``\\autoref``/
     ``\\eqref``/``\\pageref`` target has a matching ``\\label`` somewhere in the
     document graph (comma lists like ``\\cref{a,b}`` are expanded).
  2. **Input existence** — every ``\\input{...}``/``\\include{...}`` resolves to a
     file on disk (``.tex`` appended when no extension is given).

LaTeX comments (text after an unescaped ``%``) are stripped before scanning, so
commented-out labels/refs do not count. Exits 0 when clean, 1 with a readable
report otherwise.

Run:  python3 src/paper/check_eval_structure.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WRITING = ROOT / "writing"
ENTRY = WRITING / "eval.tex"

REF_CMDS = ("ref", "Cref", "cref", "autoref", "eqref", "pageref", "labelcref")
_LABEL_RE = re.compile(r"\\label\{([^}]*)\}")
_REF_RE = re.compile(r"\\(?:%s)\{([^}]*)\}" % "|".join(REF_CMDS))
_INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]*)\}")
_COMMENT_RE = re.compile(r"(?<!\\)%.*$")


def _strip_comments(text: str) -> str:
    return "\n".join(_COMMENT_RE.sub("", line) for line in text.splitlines())


def _resolve(name: str, base: Path) -> Path:
    p = (base / name)
    if p.suffix:
        return p
    return p.with_suffix(".tex")


def collect(entry: Path):
    """Walk the input graph; return (labels, refs, missing_inputs)."""
    labels: set[str] = set()
    refs: list[tuple[str, Path]] = []
    missing: list[tuple[str, Path]] = []
    inputs: list[str] = []
    seen: set[Path] = set()

    def visit(path: Path):
        rp = path.resolve()
        if rp in seen:
            return
        seen.add(rp)
        if not path.exists():
            return
        text = _strip_comments(path.read_text(encoding="utf-8"))
        for m in _LABEL_RE.finditer(text):
            labels.add(m.group(1).strip())
        for m in _REF_RE.finditer(text):
            for tgt in m.group(1).split(","):
                tgt = tgt.strip()
                if tgt:
                    refs.append((tgt, path))
        for m in _INPUT_RE.finditer(text):
            name = m.group(1).strip()
            inputs.append(name)
            child = _resolve(name, WRITING)
            if not child.exists():
                missing.append((name, path))
            else:
                visit(child)

    visit(entry)
    return labels, refs, missing, inputs


def main() -> int:
    if not ENTRY.exists():
        print("FAIL: entry file not found:", ENTRY)
        return 1
    labels, refs, missing, inputs = collect(ENTRY)

    dangling = sorted({t for (t, _src) in refs if t not in labels})
    ok = True

    if missing:
        ok = False
        print("MISSING \\input/\\include targets:")
        for name, src in missing:
            print("  - {%s} referenced in %s" % (name, src.relative_to(ROOT)))

    if dangling:
        ok = False
        print("DANGLING references (no matching \\label):")
        for t in dangling:
            print("  - %s" % t)

    print(
        "STRUCTURE: %d labels, %d references, %d \\input targets; %s"
        % (
            len(labels),
            len(refs),
            len(inputs),
            "OK" if ok else "FAILURES above",
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
