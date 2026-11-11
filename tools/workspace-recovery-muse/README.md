# Workspace recovery harness (D0122)

Runs acceptance cases 6 to 9 for real, against the implementation in
`shell/workspace.relic`. Separate `relic` processes share one store
directory per case, and the driver damages files by hand between
processes, the way the Results section of
`docs/acceptance/workspace-recovery-muse.md` describes. No expected
outcome is edited to get a pass: a mismatch fails the case.

## Layout

- `case6_setup.relic` - two committed session generations, v1 then v2.
- `case7_setup.relic` - commit v1, fault a v2 save, retry commits v2 as g3.
- `case8_setup.relic` - one committed generation holding v1.
- `check_store.relic` - open a store and report what installed. Used by
  cases 6 and 7. It never saves.
- `case8_check.relic` - open the wrong-version store, try to save twice
  from the Editor.
- `case9_check.relic` - open a store path that is a regular file, try to
  save, then open a good store and save there.
- `case9_verify.relic` - a fresh process opens the good store.
- `run_cases.py` - the driver: runs the phases, applies the hand damage,
  asserts the exact expected output, and reports PASS or FAIL per case.
  `run_cases.py --replay` skips the setup and damage and runs only the
  check phases against the committed fixtures in
  `tests/fixtures/workspace-recovery/`, proving the fixtures themselves
  reproduce the results.

## What the driver damages, and why

- Case 6: after the setup exits, the committed g2 has one character of
  its note.txt record changed (`second` to `seconD`). A session
  generation carries a checksum, so the edit no longer parses and the
  loader falls back to g1. A newer complete generation g3, holding
  yet newer text, is added by hand; it was never committed.
- Case 7: the same one-character damage, applied to the retry's g3.
  The faulted g2 leftover was pruned by the successful g3 commit, so
  the only older generation is g1.
- Case 8: the driver writes g2 as `M2WS9` and points COMMITTED at it,
  with META naming committed g2 and previous g1. The older valid g1 is
  what the desktop falls back to, while the store stays held.
- Case 9: the bad store path is a regular file. Nothing is written to
  it. The good store is a fresh directory.

## Run it

Build Relic first (see `docs/BUILDING.md`), then from the repo root:

```console
python3 tools/workspace-recovery-muse/run_cases.py
python3 tools/workspace-recovery-muse/run_cases.py --replay
```

Stores live under `/tmp` and are removed on success. Pass `--keep` to
leave them for inspection after a failure. Exit code is 0 only when
all four cases pass.
