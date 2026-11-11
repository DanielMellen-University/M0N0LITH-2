#!/usr/bin/env python3
"""Regenerate the committed fixture stores for D0122 cases 6-9.

Each fixture is a real store: the setup program builds it with the
actual implementation, then the driver applies the same hand damage the
live run uses (see run_cases.py). Output goes to
tests/fixtures/workspace-recovery/. Run from the repo root:

    python3 tools/workspace-recovery-muse/make_fixtures.py

Verify with: python3 tools/workspace-recovery-muse/run_cases.py --replay
"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_cases import RELIC, HARNESS, ROOT, damage_one_char, g3_uncommitted, run

FIXTURES = ROOT / "tests" / "fixtures" / "workspace-recovery"


def main():
    if not RELIC.exists():
        print(f"relic not built: {RELIC}")
        return 2
    work = Path("/tmp/d0122-make-fixtures")
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)

    # Case 6: committed g2 damaged, older valid g1, newer uncommitted g3.
    c6 = work / "case6"
    c6.mkdir()
    run("case6_setup.relic", c6)
    damage_one_char(c6, 2)
    (c6 / "g3.m2ws").write_text(g3_uncommitted())

    # Case 7: retry committed g3 damaged, older valid g1, g2 leftover pruned.
    c7 = work / "case7"
    c7.mkdir()
    run("case7_setup.relic", c7)
    damage_one_char(c7, 3)

    # Case 8: committed g2 is M2WS9, older valid g1 present.
    c8 = work / "case8"
    c8.mkdir()
    run("case8_setup.relic", c8)
    (c8 / "g2.m2ws").write_text("M2WS9\n.\n")
    (c8 / "COMMITTED").write_text("g2\n")
    (c8 / "META").write_text("committed g2\nprevious g1\n")

    # Case 9: the unopenable store path is a regular file.
    bad = work / "case9-bad-store"
    bad.write_text("not-a-directory\n")

    FIXTURES.mkdir(parents=True, exist_ok=True)
    for name in ("case6", "case7", "case8"):
        dest = FIXTURES / name
        shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(work / name, dest)
    shutil.copy2(bad, FIXTURES / "case9-bad-store")
    print(f"fixtures written to {FIXTURES}")
    for p in sorted(FIXTURES.rglob("*")):
        print(" ", p.relative_to(FIXTURES), p.stat().st_size if p.is_file() else "")
    shutil.rmtree(work, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
