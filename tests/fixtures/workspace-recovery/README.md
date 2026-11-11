# Workspace recovery fixtures

Isolated store layouts for acceptance cases 6 to 9, each loadable by
`wm.workspace_open(path)`. Each one is a real store: the setup program
in `tools/workspace-recovery-muse/` built it with the actual
implementation, then the hand damage described below was applied after
the process exited. Regenerate them with:

```console
python3 tools/workspace-recovery-muse/make_fixtures.py
```

Verify them with:

```console
python3 tools/workspace-recovery-muse/run_cases.py --replay
```

## case6

COMMITTED names g2, which has one character of its note.txt record
changed (`second` to `seconD`). The generation carries a session
snapshot and a checksum, so the edit no longer parses. g1 is complete
and valid and holds the first version. g3 is a complete files-only
generation holding yet newer text; it was never committed. Opening
this store recovers g1 and reports the uncommitted g3 as ignored.

## case7

COMMITTED names g3, damaged the same way as case6's g2. g1 is complete
and valid and holds the first version. The faulted g2 leftover was
pruned by the successful g3 commit, so no g2 file is here. Opening
this store recovers g1.

## case8

COMMITTED names g2, whose whole file is `M2WS9`, a version this
desktop does not understand. g1 is complete and valid and holds the
first version. Opening this store recovers g1 and holds the store:
saves fail and nothing in the directory is replaced or deleted until
an explicit release.

## case9-bad-store

A regular file, not a directory. Opening it as a store fails with
`workspace: cannot open store`, and nothing is written to it.
