#!/usr/bin/env python3
"""D0122 workspace-recovery harness driver.

Runs cases 6-9 for real: separate relic processes share one store
directory per case, the driver damages files by hand between processes
(exactly as a user-facing fault would), and every expected line is
asserted against the actual program output. Nothing here edits an
expected outcome to get a pass: a mismatch fails the case.

Modes:
    run_cases.py            live run: setup with the real implementation,
                            hand damage, then check
    run_cases.py --replay   replay run: copy the committed fixtures from
                            tests/fixtures/workspace-recovery/ and run
                            only the check phases against them
    run_cases.py --live --replay   both, in that order

Stores live under /tmp and are removed on success unless --keep is given.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELIC = ROOT / "relic" / "build" / "relic"
HARNESS = ROOT / "tools" / "workspace-recovery-muse"
FIXTURES = ROOT / "tests" / "fixtures" / "workspace-recovery"

FAILURES = []


def run(program, *args):
    cmd = [str(RELIC), str(HARNESS / program), *[str(a) for a in args]]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=120)
    print("$ " + " ".join(cmd))
    print(proc.stdout, end="")
    if proc.stderr:
        print("stderr:", proc.stderr, end="")
    if proc.returncode != 0:
        raise RuntimeError(f"{program} exited {proc.returncode}")
    return proc.stdout


def check(case, label, out, want):
    if want in out:
        print(f"  ok: {label}")
    else:
        print(f"  FAIL: {label}\n    want: {want!r}\n    in output:\n{out}")
        FAILURES.append(f"{case}: {label}")


def damage_one_char(store, gen):
    """Change one character of the note.txt F record in gN.m2ws.

    The generation carries a session snapshot and a checksum, so a text
    edit without a checksum update no longer parses: reason invalid.
    """
    path = store / f"g{gen}.m2ws"
    lines = path.read_text().split("\n")
    hit = False
    for i, line in enumerate(lines):
        if line.startswith("F /home/note.txt ") and "second" in line:
            lines[i] = line.replace("second", "seconD", 1)
            hit = True
    assert hit, f"note.txt F record not found in {path}"
    path.write_text("\n".join(lines))


def g3_uncommitted():
    """A valid files-only generation holding yet newer text, never committed."""
    return (
        "M2WS1\n"
        "D /home\n"
        "F /home/note.txt third\\sversion\\n\n"
        "F /home/welcome.txt Welcome\\sto\\sRelic.\\n\n"
        "D /tmp\n"
        ".\n"
    )


def snapshot(store):
    return {p.name: p.read_bytes() for p in sorted(store.iterdir()) if p.is_file()}


def expect_case6_check(out):
    check("case6", "notice", out,
          'notice ["workspace: committed image invalid; recovered g1; ignored uncommitted g3"]')
    check("case6", "older text restored", out, 'note ["first version\\n"]')
    check("case6", "welcome file still shows original text", out, 'welcome ["Welcome to Relic.\\n"]')


def expect_case7_check(out):
    check("case7", "notice", out,
          'notice ["workspace: committed image invalid; recovered g1"]')
    check("case7", "first version restored", out, 'note ["first version\\n"]')


def expect_case8_check(out):
    check("case8", "notice", out,
          'notice ["workspace: committed image wrong version; store held; recovered g1"]')
    check("case8", "older text restored", out, 'note ["first version\\n"]')
    check("case8", "first save fails visibly", out,
          'save1 ["workspace: save failed; store held (wrong-version); not written"]')
    check("case8", "second save fails visibly", out,
          'save2 ["workspace: save failed; store held (wrong-version); not written"]')


def expect_case9_check(out):
    check("case9", "bad store not enabled", out, "bad-enabled false")
    check("case9", "bad notice", out, 'bad-notice ["workspace: cannot open store"]')
    check("case9", "bad save never says saved", out, 'bad-save ["workspace: cannot open store"]')
    check("case9", "editor still holds the typed text", out, 'editor-text ["Welcome to Relic.\\nhello"]')
    check("case9", "good store enabled", out, "good-enabled true")
    check("case9", "good notice quiet", out, 'good-notice [""]')
    check("case9", "disk-change prompt on first good save", out,
          'good-save-1 ["changed on disk: ctrl+s again"]')
    check("case9", "second good save says saved", out, 'good-save-2 ["saved"]')


def expect_case9_verify(out):
    check("case9", "good store enabled on reopen", out, "enabled true")
    check("case9", "text survived the restart", out, 'welcome ["Welcome to Relic.\\nhello"]')


def live_case6(tmp):
    print("== case 6: corrupt committed must not load a newer uncommitted ==")
    store = Path(tmp) / "case6"
    store.mkdir()
    out = run("case6_setup.relic", store)
    check("case6", "v1 save quiet", out, 'after v1 [""]')
    check("case6", "v2 save quiet", out, 'after v2 [""]')
    check("case6", "v2 installed", out, 'note ["second version\\n"]')
    assert (store / "COMMITTED").read_text() == "g2\n", "COMMITTED is not g2"
    assert (store / "META").read_text() == "committed g2\nprevious g1\n", "META mismatch"
    damage_one_char(store, 2)
    (store / "g3.m2ws").write_text(g3_uncommitted())
    expect_case6_check(run("check_store.relic", store))
    print("case6 done")


def live_case7(tmp):
    print("== case 7: corrupted retry commit keeps the prior committed generation ==")
    store = Path(tmp) / "case7"
    store.mkdir()
    out = run("case7_setup.relic", store)
    check("case7", "v1 save quiet", out, 'after v1 [""]')
    check("case7", "faulted save kept g1", out,
          'after faulted v2 ["workspace: save failed (partial-generation); kept g1"]')
    check("case7", "retry save quiet", out, 'after retry [""]')
    names = sorted(p.name for p in store.iterdir())
    assert names == ["COMMITTED", "META", "g1.m2ws", "g3.m2ws"], f"leftover not pruned: {names}"
    assert (store / "COMMITTED").read_text() == "g3\n", "COMMITTED is not g3"
    assert (store / "META").read_text() == "committed g3\nprevious g1\n", "META mismatch"
    damage_one_char(store, 3)
    expect_case7_check(run("check_store.relic", store))
    print("case7 done")


def live_case8(tmp):
    print("== case 8: unsupported-version store stays held through normal writes ==")
    store = Path(tmp) / "case8"
    store.mkdir()
    out = run("case8_setup.relic", store)
    check("case8", "v1 save quiet", out, 'after v1 [""]')
    assert (store / "COMMITTED").read_text() == "g1\n", "COMMITTED is not g1"
    (store / "g2.m2ws").write_text("M2WS9\n.\n")
    (store / "COMMITTED").write_text("g2\n")
    (store / "META").write_text("committed g2\nprevious g1\n")
    before = snapshot(store)
    expect_case8_check(run("case8_check.relic", store))
    after = snapshot(store)
    if before == after:
        print("  ok: store bytes unchanged by the failed writes")
    else:
        print(f"  FAIL: store changed\n    before: {sorted(before)}\n    after: {sorted(after)}")
        FAILURES.append("case8: store bytes changed")
    print("case8 done")


def live_case9(tmp):
    print("== case 9: a requested store that cannot be opened must not report saved ==")
    bad = Path(tmp) / "case9-bad"
    bad.write_text("not-a-directory\n")
    good = Path(tmp) / "case9-good"
    good.mkdir()
    bad_before = bad.read_bytes()
    expect_case9_check(run("case9_check.relic", bad, good))
    if bad.read_bytes() == bad_before:
        print("  ok: nothing written to the unopenable path")
    else:
        print("  FAIL: unopenable path changed")
        FAILURES.append("case9: unopenable path changed")
    expect_case9_verify(run("case9_verify.relic", good))
    print("case9 done")


def replay_case6(tmp):
    print("== replay case 6 from the committed fixture ==")
    store = Path(tmp) / "replay-case6"
    shutil.copytree(FIXTURES / "case6", store)
    expect_case6_check(run("check_store.relic", store))
    print("case6 replay done")


def replay_case7(tmp):
    print("== replay case 7 from the committed fixture ==")
    store = Path(tmp) / "replay-case7"
    shutil.copytree(FIXTURES / "case7", store)
    expect_case7_check(run("check_store.relic", store))
    print("case7 replay done")


def replay_case8(tmp):
    print("== replay case 8 from the committed fixture ==")
    store = Path(tmp) / "replay-case8"
    shutil.copytree(FIXTURES / "case8", store)
    before = snapshot(store)
    expect_case8_check(run("case8_check.relic", store))
    after = snapshot(store)
    if before == after:
        print("  ok: store bytes unchanged by the failed writes")
    else:
        print("  FAIL: store changed")
        FAILURES.append("case8 replay: store bytes changed")
    print("case8 replay done")


def replay_case9(tmp):
    print("== replay case 9 from the committed fixture ==")
    bad = Path(tmp) / "replay-case9-bad"
    shutil.copy2(FIXTURES / "case9-bad-store", bad)
    good = Path(tmp) / "replay-case9-good"
    good.mkdir()
    bad_before = bad.read_bytes()
    expect_case9_check(run("case9_check.relic", bad, good))
    if bad.read_bytes() == bad_before:
        print("  ok: nothing written to the unopenable path")
    else:
        print("  FAIL: unopenable path changed")
        FAILURES.append("case9 replay: unopenable path changed")
    expect_case9_verify(run("case9_verify.relic", good))
    print("case9 replay done")


def main():
    if not RELIC.exists():
        print(f"relic not built: {RELIC}")
        print("Build it first: cmake -S relic -B relic/build -DRELIC_BUILD_HOST=ON && cmake --build relic/build")
        return 2
    live = "--replay" not in sys.argv
    replay = "--replay" in sys.argv
    if "--live" in sys.argv:
        live = True
    tmp = tempfile.mkdtemp(prefix="d0122-")
    print(f"stores under {tmp}")
    try:
        if live:
            live_case6(tmp)
            live_case7(tmp)
            live_case8(tmp)
            live_case9(tmp)
        if replay:
            for fixture in ("case6", "case7", "case8", "case9-bad-store"):
                assert (FIXTURES / fixture).exists(), f"missing fixture: {fixture}"
            replay_case6(tmp)
            replay_case7(tmp)
            replay_case8(tmp)
            replay_case9(tmp)
    except (RuntimeError, AssertionError) as exc:
        print(f"ERROR: {exc}")
        FAILURES.append(str(exc))
    print()
    if FAILURES:
        print(f"RESULT: FAIL ({len(FAILURES)} failure(s)), stores kept under {tmp}")
        for failure in FAILURES:
            print(" - " + failure)
        return 1
    print("RESULT: PASS, all four cases")
    if "--keep" not in sys.argv:
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"stores under {tmp} removed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
