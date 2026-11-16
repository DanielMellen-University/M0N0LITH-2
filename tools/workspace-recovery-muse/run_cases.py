#!/usr/bin/env python3
"""D0134 workspace-recovery harness driver.

Runs cases 6-14 for real: separate relic processes share one store
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
import ast
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


def check_names(case, label, out, want):
    """Assert the store's file list, ignoring the order files.list returns."""
    for line in out.split("\n"):
        if line.startswith("names "):
            got = sorted(ast.literal_eval(line[len("names "):]))
            if got == sorted(want):
                print(f"  ok: {label}")
            else:
                print(f"  FAIL: {label}\n    want: {sorted(want)!r}\n    got: {got!r}")
                FAILURES.append(f"{case}: {label}")
            return
    print(f"  FAIL: {label}\n    no names line in output:\n{out}")
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


def parse_snaps(out):
    """Parse the release_check `snap <tag> <name> <escaped>` lines.

    Returns {tag: {name: escaped-content}}. Content is escaped by the
    Relic program (backslash first, then newline), so one file is one
    line and the driver can compare snapshots byte for byte.
    """
    snaps = {}
    for line in out.split("\n"):
        if line.startswith("snap "):
            parts = line.split(" ", 3)
            if len(parts) == 4:
                _, tag, name, esc = parts
                snaps.setdefault(tag, {})[name] = esc
    return snaps


def check_snaps_equal(case, label, out, tag_a, tag_b):
    """Assert two printed store snapshots hold identical bytes."""
    snaps = parse_snaps(out)
    a, b = snaps.get(tag_a), snaps.get(tag_b)
    if a is None or b is None:
        missing = tag_a if a is None else tag_b
        print(f"  FAIL: {label}\n    no {missing} snapshot in output")
        FAILURES.append(f"{case}: {label}")
        return
    if a == b:
        print(f"  ok: {label}")
        return
    only_a = sorted(set(a) - set(b))
    only_b = sorted(set(b) - set(a))
    changed = sorted(n for n in set(a) & set(b) if a[n] != b[n])
    print(f"  FAIL: {label}\n    only in {tag_a}: {only_a}\n    only in {tag_b}: {only_b}\n    changed: {changed}")
    FAILURES.append(f"{case}: {label}")


def check_snap_has(case, label, out, tag, name, want):
    """Assert one file's escaped bytes in a printed snapshot."""
    snaps = parse_snaps(out)
    got = snaps.get(tag, {}).get(name)
    if got == want:
        print(f"  ok: {label}")
    else:
        print(f"  FAIL: {label}\n    want {name}: {want!r}\n    got: {got!r}")
        FAILURES.append(f"{case}: {label}")


def check_snap_missing(case, label, out, tag, name):
    """Assert one file is absent from a printed snapshot."""
    snaps = parse_snaps(out)
    if name not in snaps.get(tag, {}):
        print(f"  ok: {label}")
    else:
        print(f"  FAIL: {label}\n    {name} present in {tag} snapshot")
        FAILURES.append(f"{case}: {label}")


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


def expect_case10_check(out):
    check("case10", "held notice", out,
          'notice ["workspace: committed image wrong version; store held; recovered g1"]')
    check("case10", "first save fails visibly", out,
          'save1 ["workspace: save failed; store held (wrong-version); not written"]')
    check_snaps_equal("case10", "failed save wrote nothing", out, "before", "after-save1")
    check_snaps_equal("case10", "release deleted nothing", out, "after-save1", "after-release")
    check_snap_has("case10", "wrong-version g2 survived the failed save", out,
                    "after-release", "g2.m2ws", "M2WS9\\n.\\n")
    check_snap_has("case10", "pointer still names g2 after release", out,
                    "after-release", "COMMITTED", "g2\\n")
    check("case10", "release notice", out, 'release-notice ["workspace: store hold released"]')
    check("case10", "save after release says saved", out, 'save2 ["saved"]')
    check("case10", "new generation committed", out, 'committed ["g3\\n"]')
    check("case10", "metadata names the new commit", out, 'meta ["committed g3\\nprevious g1\\n"]')
    check_names("case10", "prune keeps the new commit and the older generation", out,
                ["COMMITTED", "META", "g1.m2ws", "g3.m2ws"])


def expect_case10_verify(out):
    check("case10", "store quiet on reopen", out, 'notice [""]')
    check("case10", "older text still there", out, 'note ["first version\\n"]')
    check("case10", "released text survived the restart", out,
          'welcome ["Welcome to Relic.\\nreleased ten"]')


def expect_case11_check(out):
    check("case11", "notice", out, 'notice ["workspace: pointer invalid; recovered g2"]')
    check("case11", "newer text restored", out, 'note ["second version\\n"]')
    check("case11", "welcome file still shows original text", out, 'welcome ["Welcome to Relic.\\n"]')


def expect_case12_check(out):
    check("case12", "held notice", out,
          'notice ["workspace: pointer invalid; store held; using defaults; ignored uncommitted g2"]')
    check("case12", "first save fails visibly", out,
          'save1 ["workspace: save failed; store held (ambiguous); not written"]')
    check_snaps_equal("case12", "failed save wrote nothing", out, "before", "after-save1")
    check_snaps_equal("case12", "release deleted nothing", out, "after-save1", "after-release")
    check_snap_has("case12", "torn pointer still torn after release", out,
                    "after-release", "COMMITTED", "x")
    check_snap_missing("case12", "no META was created by the failed save or release", out,
                        "after-release", "META")
    check("case12", "release notice", out, 'release-notice ["workspace: store hold released"]')
    check("case12", "save after release says saved", out, 'save2 ["saved"]')
    check("case12", "new generation committed", out, 'committed ["g3\\n"]')
    check("case12", "metadata names no previous generation", out,
          'meta ["committed g3\\nprevious none\\n"]')
    check_names("case12", "prune keeps only the new commit", out,
                ["COMMITTED", "META", "g3.m2ws"])


def expect_case12_verify(out):
    check("case12", "store quiet on reopen", out, 'notice [""]')
    check("case12", "no note file in the defaults image", out, "note-exists false")
    check("case12", "released text survived the restart", out,
          'welcome ["Welcome to Relic.\\nreleased twelve"]')


def expect_case13_check(out):
    check("case13", "held notice", out,
          'notice ["workspace: too many generation files; store held; using defaults"]')
    check("case13", "first save fails visibly", out,
          'save1 ["workspace: save failed; store held (too-many); not written"]')
    check_snaps_equal("case13", "failed save wrote nothing", out, "before", "after-save1")
    check_snaps_equal("case13", "release deleted nothing", out, "after-save1", "after-release")
    snaps = parse_snaps(out)
    want_names = sorted(["COMMITTED", "META"] + [f"g{n}.m2ws" for n in range(1, 34)])
    got_names = sorted(snaps.get("after-release", {}))
    if got_names == want_names:
        print("  ok: release kept all 33 generations")
    else:
        print(f"  FAIL: release kept all 33 generations\n    want: {want_names}\n    got: {got_names}")
        FAILURES.append("case13: release kept all 33 generations")
    check("case13", "release notice", out, 'release-notice ["workspace: store hold released"]')
    check("case13", "save after release says saved", out, 'save2 ["saved"]')
    check("case13", "new generation committed", out, 'committed ["g34\\n"]')
    check("case13", "metadata names no previous generation", out,
          'meta ["committed g34\\nprevious none\\n"]')
    check_names("case13", "prune keeps only the new commit", out,
                ["COMMITTED", "META", "g34.m2ws"])


def expect_case13_verify(out):
    check("case13", "store quiet on reopen", out, 'notice [""]')
    check("case13", "no note file in the defaults image", out, "note-exists false")
    check("case13", "released text survived the restart", out,
          'welcome ["Welcome to Relic.\\nreleased thirteen"]')


def expect_case14_check(out):
    check("case14", "notice names both leftovers", out,
          'notice ["workspace: ignored uncommitted g3; ignored partial g4"]')
    check("case14", "committed text restored", out, 'note ["second version\\n"]')
    check("case14", "welcome file still shows original text", out, 'welcome ["Welcome to Relic.\\n"]')


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


def hold_wrong_version(store):
    """Turn a one-commit store into a wrong-version hold (case 8's damage)."""
    (store / "g2.m2ws").write_text("M2WS9\n.\n")
    (store / "COMMITTED").write_text("g2\n")
    (store / "META").write_text("committed g2\nprevious g1\n")


def live_case10(tmp):
    print("== case 10: release of a held store, then a save succeeds ==")
    store = Path(tmp) / "case10"
    store.mkdir()
    out = run("case8_setup.relic", store)
    check("case10", "v1 save quiet", out, 'after v1 [""]')
    assert (store / "COMMITTED").read_text() == "g1\n", "COMMITTED is not g1"
    hold_wrong_version(store)
    expect_case10_check(run("release_check.relic", store, "released ten"))
    expect_case10_verify(run("check_store.relic", store))
    print("case10 done")


def live_case11(tmp):
    print("== case 11: torn pointer with a usable META recovers the named generation ==")
    store = Path(tmp) / "case11"
    store.mkdir()
    out = run("case6_setup.relic", store)
    check("case11", "v1 save quiet", out, 'after v1 [""]')
    check("case11", "v2 save quiet", out, 'after v2 [""]')
    assert (store / "COMMITTED").read_text() == "g2\n", "COMMITTED is not g2"
    assert (store / "META").read_text() == "committed g2\nprevious g1\n", "META mismatch"
    (store / "COMMITTED").write_text("x")
    expect_case11_check(run("check_store.relic", store))
    print("case11 done")


def live_case12(tmp):
    print("== case 12: ambiguous torn pointer holds the store until release ==")
    store = Path(tmp) / "case12"
    store.mkdir()
    out = run("case6_setup.relic", store)
    check("case12", "v1 save quiet", out, 'after v1 [""]')
    check("case12", "v2 save quiet", out, 'after v2 [""]')
    assert (store / "COMMITTED").read_text() == "g2\n", "COMMITTED is not g2"
    (store / "COMMITTED").write_text("x")
    (store / "META").unlink()
    expect_case12_check(run("release_check.relic", store, "released twelve"))
    expect_case12_verify(run("check_store.relic", store))
    print("case12 done")


def live_case13(tmp):
    print("== case 13: too many generation files hold the store until release ==")
    store = Path(tmp) / "case13"
    store.mkdir()
    out = run("case8_setup.relic", store)
    check("case13", "v1 save quiet", out, 'after v1 [""]')
    assert (store / "COMMITTED").read_text() == "g1\n", "COMMITTED is not g1"
    g1 = (store / "g1.m2ws").read_bytes()
    for n in range(2, 34):
        (store / f"g{n}.m2ws").write_bytes(g1)
    names = [p.name for p in store.iterdir() if p.name.startswith("g")]
    assert len(names) == 33, f"expected 33 generation names, got {len(names)}"
    expect_case13_check(run("release_check.relic", store, "released thirteen"))
    expect_case13_verify(run("check_store.relic", store))
    print("case13 done")


def live_case14(tmp):
    print("== case 14: uncommitted and partial leftovers are named, not installed ==")
    store = Path(tmp) / "case14"
    store.mkdir()
    out = run("case6_setup.relic", store)
    check("case14", "v1 save quiet", out, 'after v1 [""]')
    check("case14", "v2 save quiet", out, 'after v2 [""]')
    assert (store / "COMMITTED").read_text() == "g2\n", "COMMITTED is not g2"
    (store / "g3.m2ws").write_text(g3_uncommitted())
    (store / "g4.m2ws.partial").write_text("M2WS1\n")
    expect_case14_check(run("check_store.relic", store))
    print("case14 done")


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


def replay_case10(tmp):
    print("== replay case 10 from the committed fixture ==")
    store = Path(tmp) / "replay-case10"
    shutil.copytree(FIXTURES / "case10", store)
    expect_case10_check(run("release_check.relic", store, "released ten"))
    expect_case10_verify(run("check_store.relic", store))
    print("case10 replay done")


def replay_case11(tmp):
    print("== replay case 11 from the committed fixture ==")
    store = Path(tmp) / "replay-case11"
    shutil.copytree(FIXTURES / "case11", store)
    expect_case11_check(run("check_store.relic", store))
    print("case11 replay done")


def replay_case12(tmp):
    print("== replay case 12 from the committed fixture ==")
    store = Path(tmp) / "replay-case12"
    shutil.copytree(FIXTURES / "case12", store)
    expect_case12_check(run("release_check.relic", store, "released twelve"))
    expect_case12_verify(run("check_store.relic", store))
    print("case12 replay done")


def replay_case13(tmp):
    print("== replay case 13 from the committed fixture ==")
    store = Path(tmp) / "replay-case13"
    shutil.copytree(FIXTURES / "case13", store)
    expect_case13_check(run("release_check.relic", store, "released thirteen"))
    expect_case13_verify(run("check_store.relic", store))
    print("case13 replay done")


def replay_case14(tmp):
    print("== replay case 14 from the committed fixture ==")
    store = Path(tmp) / "replay-case14"
    shutil.copytree(FIXTURES / "case14", store)
    expect_case14_check(run("check_store.relic", store))
    print("case14 replay done")


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
            live_case10(tmp)
            live_case11(tmp)
            live_case12(tmp)
            live_case13(tmp)
            live_case14(tmp)
        if replay:
            for fixture in ("case6", "case7", "case8", "case9-bad-store",
                            "case10", "case11", "case12", "case13", "case14"):
                assert (FIXTURES / fixture).exists(), f"missing fixture: {fixture}"
            replay_case6(tmp)
            replay_case7(tmp)
            replay_case8(tmp)
            replay_case9(tmp)
            replay_case10(tmp)
            replay_case11(tmp)
            replay_case12(tmp)
            replay_case13(tmp)
            replay_case14(tmp)
    except (RuntimeError, AssertionError) as exc:
        print(f"ERROR: {exc}")
        FAILURES.append(str(exc))
    print()
    if FAILURES:
        print(f"RESULT: FAIL ({len(FAILURES)} failure(s)), stores kept under {tmp}")
        for failure in FAILURES:
            print(" - " + failure)
        return 1
    print("RESULT: PASS, all nine cases")
    if "--keep" not in sys.argv:
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"stores under {tmp} removed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
