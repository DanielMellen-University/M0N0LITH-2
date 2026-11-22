#!/usr/bin/env python3
"""Regenerate the committed fixture stores for D0122 cases 6-9, D0134 cases 10-14,
and D0142 cases 15-19.

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
from run_cases import RELIC, HARNESS, ROOT, damage_one_char, g3_uncommitted, hold_wrong_version, run

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

    # Case 10: wrong-version hold (case 8's damage) on a one-commit store.
    c10 = work / "case10"
    c10.mkdir()
    run("case8_setup.relic", c10)
    hold_wrong_version(c10)

    # Case 11: torn pointer (COMMITTED is the single byte `x`), META usable.
    c11 = work / "case11"
    c11.mkdir()
    run("case6_setup.relic", c11)
    (c11 / "COMMITTED").write_text("x")

    # Case 12: torn pointer with no usable META.
    c12 = work / "case12"
    c12.mkdir()
    run("case6_setup.relic", c12)
    (c12 / "COMMITTED").write_text("x")
    (c12 / "META").unlink()

    # Case 13: more than 32 generation names (g1 plus copies as g2..g33).
    c13 = work / "case13"
    c13.mkdir()
    run("case8_setup.relic", c13)
    g1 = (c13 / "g1.m2ws").read_bytes()
    for n in range(2, 34):
        (c13 / f"g{n}.m2ws").write_bytes(g1)

    # Case 14: newer uncommitted g3 plus a partial g4 leftover.
    c14 = work / "case14"
    c14.mkdir()
    run("case6_setup.relic", c14)
    (c14 / "g3.m2ws").write_text(g3_uncommitted())
    (c14 / "g4.m2ws.partial").write_text("M2WS1\n")

    # Case 15: wrong-version hold (case 10's store); the open alone must
    # write nothing.
    c15 = work / "case15"
    c15.mkdir()
    run("case8_setup.relic", c15)
    hold_wrong_version(c15)

    # Case 16: torn pointer with no usable META (case 12's store); the open
    # alone must write nothing.
    c16 = work / "case16"
    c16.mkdir()
    run("case6_setup.relic", c16)
    (c16 / "COMMITTED").write_text("x")
    (c16 / "META").unlink()

    # Case 17: more than 32 generation names (case 13's store); the open
    # alone must write nothing.
    c17 = work / "case17"
    c17.mkdir()
    run("case8_setup.relic", c17)
    g1 = (c17 / "g1.m2ws").read_bytes()
    for n in range(2, 34):
        (c17 / f"g{n}.m2ws").write_bytes(g1)

    # Case 18: COMMITTED missing, META names a parseable generation.
    c18 = work / "case18"
    c18.mkdir()
    run("case6_setup.relic", c18)
    (c18 / "COMMITTED").unlink()

    # Case 19: COMMITTED missing, exactly one valid generation, no META.
    c19 = work / "case19"
    c19.mkdir()
    run("case8_setup.relic", c19)
    (c19 / "COMMITTED").unlink()
    (c19 / "META").unlink()

    # Case 20: COMMITTED names g2, but g2.m2ws is gone. g3 is newer and
    # uncommitted. g1 is the older valid generation.
    c20 = work / "case20"
    c20.mkdir()
    run("case6_setup.relic", c20)
    (c20 / "g2.m2ws").unlink()
    (c20 / "g3.m2ws").write_text(g3_uncommitted())

    # Case 21: COMMITTED names a valid g2. META is not a metadata file.
    c21 = work / "case21"
    c21.mkdir()
    run("case6_setup.relic", c21)
    (c21 / "META").write_text("not a meta file\n")

    FIXTURES.mkdir(parents=True, exist_ok=True)
    for name in ("case6", "case7", "case8", "case10", "case11", "case12", "case13", "case14",
                 "case15", "case16", "case17", "case18", "case19", "case20", "case21"):
        dest = FIXTURES / name
        shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(work / name, dest)
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
