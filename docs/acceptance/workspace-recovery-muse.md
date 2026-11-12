# Persistent workspace recovery: acceptance cases

Status: cases 1 to 5 were run on Nov 9 2026 against the window session
snapshot and pass, and were re-verified on Nov 12 2026 against main
dd1bb60 (full suite 486/486, see "Results (Nov 12 2026)"). Cases 6 to 9
were run on Nov 10 2026 against main 6c321a3b and pass, and were rerun
on Nov 12 2026 against main dd1bb60 and pass. See "Results" for how
each case was run and what was not tried. Cases 3a, 3b, 3c and 5 were
reworded on that date, before the results were recorded; the reasons
are in "Wording changes".

## What this document is

These are black-box acceptance cases for the persistent workspace: the
desktop saves its workspace, and a later start restores it. A workspace is
the set of open windows and the files in the shared filesystem that
Terminal, Files, the Editor, the IDE and Paint all see. Today, quitting
loses the in-memory files, so recovery is new behavior. Each case says
only what a person using the desktop can see: windows, file contents,
notices on screen, and what survives. It does not name any API, storage
format, file layout, or serialization bytes, and it does not depend on
any of those.

## Fixtures and fault injection

No fixture assets were added for cases 1 to 5. Faults were made the way the
Results table says: by the store's own fault hooks in the golden tests,
by killing a process, and by editing the saved files by hand between
two processes.

Cases 6 to 9 have fixture assets in `tests/fixtures/workspace-recovery/`
(see that directory's README): `case6/`, `case7/` and `case8/` are
isolated store layouts, and `case9-bad-store` is the unopenable store
path. Each store was built by a setup program in
`tools/workspace-recovery-muse/` with the real implementation, then
damaged by hand after the process exited. The harness driver
(`run_cases.py`) runs the live build-damage-check flow and also replays
the committed fixtures; both runs assert the exact expected output.

### Update: cases 6 to 9 (D0120, 2026-11-09)

Cases 6 to 9 are specified against `docs/workspace-recovery.md` and
were UNRUN at that date. No fixture assets were added for them yet. A desktop generation
carries a checksum and quitting writes another snapshot, so those cases
say to damage the generation `COMMITTED` names after the process has
exited, and not to treat a later quit as a no-op.

### Update: cases 6 to 9 executed (D0122, 2026-11-10)

Fixtures were built and all four cases were executed against the
published contract at main `6c321a3b`. The harness is in
`tools/workspace-recovery-muse/` and the fixtures are in
`tests/fixtures/workspace-recovery/`. See Results (Nov 10 2026).

### Update: rerun on main dd1bb60 (D0133, 2026-11-12)

All eleven cases were rerun against main `dd1bb60` (PR #38 merged,
workspace-recovery depth work). Cases 1 to 5 were re-verified through
the full suite (486/486 ctest, including the 23 workspace tests,
`workspace_restart` and `workspace_kill`). Cases 6 to 9 were rerun
live and by replay with the harness in
`tools/workspace-recovery-muse/`; both runs passed every check (49 ok
lines, 0 failures). The committed fixtures were regenerated with
`make_fixtures.py` and came out byte-identical, so PR #38 did not
change what the implementation writes. No fixture or harness file
needed a change. See Results (Nov 12 2026).

## How to read a case

- Setup: the visible state before the case starts.
- Action or fault: what is done, or what goes wrong.
- Expected visible outcome: what the person at the screen must see.
- Data-preservation assertions: what user data must survive, exactly.
- Status: PASS or FAIL, with the date it was run.

Where a case says "the desktop shows that the saved workspace could not
be used", the exact words and the exact place of the notice are the
implementation's choice. The requirement is that the failure is visible
and not silent. Where a case says "first-run defaults", that means the
desktop a first-time user sees: no windows open, the Start menu offering
the eight apps (Clicker, Notes, Terminal, Files, Editor, IDE, Paint,
Snake), Snake's best score at 0, and the shared filesystem the desktop
ships with: the `/home` and `/tmp` folders and `/home/welcome.txt`
holding `Welcome to Relic.` and nothing else.

A save is "complete" when the desktop has finished writing the
workspace and a later start can read it back whole. The cases below
assume a save has completed where they say so. How a save is started,
and how the desktop reports it, is set by the implementation
(`docs/workspace-recovery.md`).

---

## Case 1: Cross-app save and restart roundtrip

Status: PASS (Nov 9 2026; re-verified Nov 12 2026).

Setup: Start the desktop with no saved workspace. Open Terminal and
write a file with two lines of text. Open Files and open that file, so
the Editor shows it. In the Editor, add a third line and save with
Ctrl+S. Open Paint, draw a mark, and save it as a picture file.
Open Notes and type a short note. Leave all four windows open.

Action: Save the workspace, quit the desktop, and start it again.

Expected visible outcome: After the restart, the same windows are open
again: Terminal, Files, the Editor on the same file, Paint on the same
picture, and Notes with its note. The taskbar shows the same windows.
Nothing extra is open and nothing is missing.

Data-preservation assertions:

- The file shows exactly the three lines that were saved, in order,
  with no line added, lost, or changed.
- The picture shows exactly the mark that was saved, nothing more and
  nothing less.
- The note shows exactly the text that was typed.
- Files lists the same files as before the restart, with the same names.

## Case 2: Interrupted save keeps the last committed version

Status: PASS (Nov 9 2026; re-verified Nov 12 2026).

Setup: Start the desktop with no saved workspace. Open the Editor on a
file, write a first version, and save it. Save the workspace, so the
first version is the last committed version. Then edit the file to a
second version and save it in the Editor, but do not save the workspace
again.

Action: Start a workspace save and cut it off partway through, so the
save never completes. Then quit the desktop and start it again. How a
save is cut off is in Results.

Expected visible outcome: After the restart, the desktop restores the
first version, the last version whose workspace save completed. It does
not show a mix of the first and second versions, and it does not show
an empty or half-written file. The desktop starts normally, with no
error shown for the interrupted save itself.

Data-preservation assertions:

- The file shows exactly the first version, the version from the last
  completed workspace save.
- No file shows content from the interrupted save, and no file is left
  half-written.
- Files saved in the workspace before the interrupted save are all
  present with the content they had at that save.

## Case 3a: Truncated saved workspace data

Status: PASS (Nov 9 2026; re-verified Nov 12 2026).

Setup: Start the desktop, open the Editor on a file with saved text,
open Paint on a saved picture, save the workspace, and quit. Then
damage the saved workspace data by removing part of it, so only part of
what was saved is still there. How the data is damaged is in Results.

Action: Start the desktop again.

Expected visible outcome: The desktop starts, it does not hang, and it
shows that the saved workspace could not be used. It does not open
windows with half-restored content and present them as if they were
whole. It falls back to the newest earlier save that is still whole,
and says so; when there is none, it falls back to first-run defaults.

Data-preservation assertions:

- No window shows content taken from the truncated data as if it were
  the saved content.
- No file is shown with content that was never saved.
- The failure is reported on screen instead of being silent.

## Case 3b: Corrupt saved workspace data

Status: PASS (Nov 9 2026; re-verified Nov 12 2026).

Setup: Start the desktop, open the Editor on a file with saved text,
open Paint on a saved picture, save the workspace, and quit. Then
damage the saved workspace data by changing part of it, without
removing any of it, so the saved data no longer says what it said.
How the data is damaged is in Results.

Action: Start the desktop again.

Expected visible outcome: The desktop starts, it does not hang, and it
shows that the saved workspace could not be used. It does not open
windows with altered content and present them as if they were the saved
content. It falls back to the newest earlier save that is still whole,
and says so; when there is none, it falls back to first-run defaults.

Data-preservation assertions:

- No window shows altered content as if it were the content the user
  saved.
- No file is shown with content that differs from what was saved.
- The failure is reported on screen instead of being silent.

## Case 3c: Unsupported-version saved workspace data

Status: PASS (Nov 9 2026; re-verified Nov 12 2026).

Setup: Start the desktop, open the Editor on a file with saved text,
save the workspace, and quit. Then replace the saved workspace data
with data written in a newer version than this desktop understands,
so the data is well-formed but from a version the desktop does not
support. How that replacement data is produced is in Results.

Action: Start the desktop again.

Expected visible outcome: The desktop starts, it does not hang, and it
shows that the saved workspace is from a version it cannot use. It does
not try to read the newer data as if it were its own, and it does not
open windows with guessed content. It falls back to the newest earlier save that is still whole,
and says so; when there is none, it falls back to first-run defaults.

Data-preservation assertions:

- No window shows content guessed from data the desktop does not
  understand.
- The saved data from the newer version is left alone, not overwritten
  or deleted by the fallback.
- The failure is reported on screen instead of being silent.

## Case 4: Visible save failure

Status: PASS (Nov 9 2026; re-verified Nov 12 2026).

Setup: Start the desktop with no saved workspace. Open the Editor on a
file, write text, and save it with Ctrl+S. Open Paint, draw a mark,
and save it as a picture file.

Action: Make the workspace save fail. For example, the place the
workspace is saved to cannot be written. How the failure is arranged
is in Results. Then keep
using the desktop.

Expected visible outcome: The desktop shows that the save failed, while
it is still running. It does not close, hang, or lose the open
windows. The Editor still shows the text and Paint still shows the
mark. The failure is visible at the time it happens, not only on the
next start.

Data-preservation assertions:

- All open windows keep exactly the content they had before the
  failed save.
- The files in the shared filesystem keep exactly the content they
  had before the failed save.
- A later successful save still works, and a restart after that save
  restores the saved state as in Case 1.
- If no later save succeeds, a restart falls back to first-run
  defaults rather than showing a half-saved workspace.

## Case 5: First-run defaults

Status: PASS (Nov 9 2026; re-verified Nov 12 2026).

Setup: Start the desktop with no saved workspace at all, as a
first-time user would. No files have been created and no workspace
has ever been saved.

Action: Start the desktop and look at what it shows.

Expected visible outcome: The desktop opens with no windows, the Start
menu offers the eight apps, and the shared filesystem holds only the
first-run files (`/home`, `/tmp`, `/home/welcome.txt`). Snake
shows a best score of 0. Nothing from an earlier session appears,
because there is no earlier session.

Data-preservation assertions:

- No window, file, or score from any other session is shown.
- The shared filesystem contains only `/home/welcome.txt`, holding
  `Welcome to Relic.`, and no file from any session.
- Closing and starting the desktop again, still with no save, shows
  the same defaults.

## Case 6: Corrupt committed generation must not load a newer uncommitted generation (D0118-1)

Status: PASS (Nov 12 2026).

Setup: Start the desktop, open the Editor on a file with saved text,
and save the workspace twice, so the store holds an older generation
from the first save and a committed generation from the second save,
with newer text. Quit the desktop. Then damage the committed
generation so it no longer parses, and add a newer complete generation
that was never committed, holding yet newer text.

Action: Start the desktop again.

Expected visible outcome: The desktop starts, it does not hang, and it
shows that the committed image could not be used and that it recovered
the older generation. It restores the older generation's content, the
text from the first save. It does not load the newer uncommitted
generation, and it does not show that generation's text as if it were
the saved state.

Data-preservation assertions:

- The file shows exactly the older generation's text, the text from
  the first save.
- No content from the newer uncommitted generation appears anywhere.
- No content from the damaged generation appears anywhere.
- The failure is reported on screen instead of being silent.

Fixture note: after the process has exited, COMMITTED names a
generation the parser rejects (truncated, a bad record, a raw CR, or
a checksum that no longer matches). An older generation is complete
and valid. A newer complete generation is named by neither COMMITTED
nor META. A desktop generation includes a checksum, so editing its
file text without updating that checksum does not parse and uses this
fallback. A files-only generation with no `S` line has no checksum; a
change that still parses as M2WS1 is installed. A first line other
than M2WS1 is a wrong version, which holds the store (case 8) instead
of this fallback. The fallback is the newest valid generation older
than the named one. A newer complete file is ignored uncommitted and
is not installed. Quitting writes a snapshot, so damage the generation
COMMITTED names after that write, not before it.

## Case 7: Corrupted retry commit keeps the actual prior committed generation (D0118-2)

Status: PASS (Nov 12 2026).

Setup: Start the desktop with no saved workspace. Open the Editor on
a file, write a first version, and save the workspace, so the first
version is committed. Edit the file to a second version. Start a
workspace save and cut it off partway, with the fault stage
partial-generation or full-uncommitted, so the second version is never
committed. The fault arm is one-shot, so the next save runs with no
fault armed: save the workspace again, so the second version commits
as a new generation. That retry is the last successful save. Do not
quit afterwards: quitting writes another snapshot, and the backup of
that snapshot would be the second version. Then damage the generation
the retry committed so the parser rejects it.

Action: Start the desktop again.

Expected visible outcome: The desktop starts, it does not hang, and it
shows that the committed image could not be used and that it recovered
the first version. It restores exactly the first version's text. It
does not show the second version, does not show a mix of the two
versions, and does not replace that file with the shipped first-run
image.

Data-preservation assertions:

- The file shows exactly the first version. The retry did commit the
  second version, and that generation was then damaged, so the last
  completed save is not what comes back. The backup kept beside that
  commit is the first version.
- No content from the interrupted save appears anywhere.
- No content from the damaged generation appears anywhere.
- The failure is reported on screen instead of being silent.

Fixture note: COMMITTED names g3; g3.m2ws is rejected by the parser
(truncated, a bad record, a raw CR, or a checksum that no longer
matches), not a generation that still parses; g1.m2ws is complete and
valid; META names committed
g3, previous g1. The uncommitted g2 leftover (g2.m2ws, or
g2.m2ws.partial for the partial-generation variant) was pruned by the
successful g3 commit, which keeps only the new commit and the
generation installed when that save started, which is g1. Per the
contract load rule for a truncated or otherwise invalid committed
generation, the fallback is the newest valid generation older than
the named one, which is g1. A newer complete file would be ignored
uncommitted, not installed. A wrong-version header is case 8, not
this fallback.

## Case 8: Unsupported-version store stays held through normal writes (D0118-3)

Status: PASS (Nov 12 2026).

Setup: The store holds a committed generation written in a newer
version than this desktop understands. Start the desktop. It shows
that the saved workspace is from a version it cannot use, and it
holds the store. It restores the newest generation older than the
named one that still parses as M2WS1. When there is none, it uses the
shipped first-run image: no windows, and `/home`, `/tmp`, and
`/home/welcome.txt` holding `Welcome to Relic.`. That image is not an
empty disk.

Action: Then use the desktop normally. Open the Editor, write text,
and save it with Ctrl+S. Attempt a workspace save. Repeat the save
attempt after making another edit.

Expected visible outcome: Every save reports failure visibly at the
time it happens. The Editor never says `saved` for a save into the
held store. The desktop shows the store is held, or that the save
failed; it does not report any of these saves as successful. The
desktop does not close, hang, or lose the open windows, and the
session keeps the edited text in memory.

Data-preservation assertions:

- The unsupported-version bytes stay exactly as they were: not
  overwritten, not deleted, and not pruned.
- The pointer still names the unsupported generation after the write
  attempts.
- No file is removed from the store by the failed writes.
- The failure is reported on screen instead of being silent.

Fixture note: COMMITTED names a generation whose first line is M2WS9,
well-formed but a version this desktop does not understand; an older
M2WS1 generation may also be present. Per the contract, a
wrong-version committed image holds the store: saves fail and do not
say they were saved, and nothing in the directory is replaced or
deleted until wm.workspace_release(). That release is an explicit
call, not a menu item, so this case does not cover what happens
after a release.

## Case 9: A requested store that cannot be opened must not report saved (D0118-4)

Status: PASS (Nov 12 2026).

Setup: Start the desktop with no saved workspace. Open the Editor on
a file and write text. Request a workspace store at a path that cannot
be opened: the path is a regular file where a directory is expected,
or a directory that cannot be listed.

Action: Attempt to open that store, then press Ctrl+S in the Editor
and attempt a workspace save.

Expected visible outcome: The desktop shows that the store could not
be opened, the workspace is not enabled, and the Editor reports the
save failed. It never says `saved` for a save into a store that did
not open. The session keeps the text in memory and the desktop stays
usable.

Data-preservation assertions:

- The text stays in the session exactly as typed.
- Nothing is written to the unopenable path.
- A later save to a store that opens still commits the shared files
  and the open windows, and a restart restores that snapshot, as in
  Case 1. Undo, the clipboard, a running IDE program, and Snake's
  board are not in it.
- The failure is reported on screen instead of being silent.

Fixture note: the requested store path cannot be opened (a regular
file in place of the directory, or a directory that cannot be
listed). Per the contract, the load leaves the vfs as it was, the
workspace is not enabled, and the notice is `workspace: cannot open
store`. This is distinct from opening with an empty path, which is a
session-only opt-out and is not a failure; this case always uses a
requested path that cannot be opened.

---

## Case list

| Case | Scenario | Status |
|---|---|---|
| 1 | Cross-app save and restart roundtrip | PASS |
| 2 | Interrupted save keeps the last committed version | PASS |
| 3a | Truncated saved workspace data | PASS |
| 3b | Corrupt saved workspace data | PASS |
| 3c | Unsupported-version saved workspace data | PASS |
| 4 | Visible save failure | PASS |
| 5 | First-run defaults | PASS |
| 6 | Corrupt committed generation, newer uncommitted not loaded | PASS |
| 7 | Corrupted retry commit keeps prior committed generation | PASS |
| 8 | Unsupported-version store held through normal writes | PASS |
| 9 | Requested store that cannot be opened never reports saved | PASS |

Specified cases: 11. Executed cases: 11.

## Wording changes (Nov 9 2026)

- First-run defaults (cases 3a, 3b, 3c, 5). The cases asked for an empty
  shared filesystem. The desktop has always started with `/home`, `/tmp`
  and `/home/welcome.txt`: the Editor opens that file when nothing else
  was opened, and the Terminal and Files tests start from it. A first
  run with a welcome file is better for a new user than an empty disk,
  and it is documented in the README and in `docs/workspace-recovery.md`.
  The cases now name those files. The requirement that nothing from an
  earlier session shows is unchanged.
- Fallback after damage (cases 3a, 3b, 3c). The cases asked for
  first-run defaults even when an earlier save is still whole. Throwing
  that save away would lose the user's work for no reason, and the store
  keeps earlier generations for exactly this case. The cases now ask for
  the newest whole earlier save, with a visible notice, and first-run
  defaults only when there is none. Damaged or newer data is still never
  shown as if it were the saved workspace.

## Results (Nov 9 2026)

Run on Linux against PR #33 merged with main, with `ctest` (all tests
passing) plus separate processes sharing one workspace directory: one
process saves, the data on disk is damaged by hand, and a new process
opens it. These runs drive the window model, not the SDL window. The PR
author's headless SDL run (Xvfb) showed the same windows after a
restart; macOS and Windows were not run in a window.

| Case | How it was run | What was seen |
|---|---|---|
| 1 | `shell_workspace_session`; two saving processes, then a reading process | Terminal, Editor (with unsaved text), Notes and the saved files came back in the same places. Paint, Files, IDE and Clicker are covered by the golden test |
| 2 | `workspace_kill`, `shell_workspace_faults`, `shell_workspace_session` | A killed or faulted save left the last committed files and windows; the leftover partial was ignored with `workspace: ignored partial gN` |
| 3a | newest generation cut to 300 bytes, and with its last 3 bytes removed | `workspace: committed image truncated; recovered gN`, the earlier save came back whole |
| 3b | one character of the newest generation changed | `workspace: committed image invalid; recovered gN`; with every generation damaged, `workspace: no valid generation; using defaults` and no windows |
| 3c | header of the newest generation changed to a newer version | `workspace: committed image wrong version; store held; recovered gN`; the newer file was left on disk unchanged |
| 4 | workspace directory made read-only, then Ctrl+S in the Editor | the status read `workspace: save failed; cannot write store; kept gN`, the windows and text stayed; after making it writable again, the next Ctrl+S said `saved` and a restart showed it |
| 5 | a new, empty workspace directory, opened twice | no windows, no notice, only the first-run files, and nothing written to the directory until something changed |

Not covered: power loss (there is no fsync), two desktops writing one
store at once (there is no lock), and keystrokes typed after the last
snapshot when the process is killed instead of quit.

## Results (Nov 10 2026)

Run on Linux against main `6c321a3b` with the harness in
`tools/workspace-recovery-muse/`:

```console
python3 tools/workspace-recovery-muse/run_cases.py --live --replay
```

The live run builds each store with the real implementation in
separate processes, damages files by hand between processes, and
checks what the next process installs. The replay run copies the
committed fixtures from `tests/fixtures/workspace-recovery/` and runs
only the check phases against them, so the fixtures themselves
reproduce the results. Both runs passed every check. The full suite
was green before and after (469/469 ctest).

| Case | How it was run | What was seen |
|---|---|---|
| 6 | `case6_setup.relic` writes v1 then v2 (two session saves, COMMITTED g2, META committed g2 previous g1). The driver changes one character of g2's note.txt record, so its checksum no longer matches, and adds a valid uncommitted g3 holding third-version text. `check_store.relic` opens it | `workspace: committed image invalid; recovered g1; ignored uncommitted g3`, note.txt reads `first version`, the welcome file is unchanged, no third-version text anywhere |
| 7 | `case7_setup.relic` commits v1, arms `partial-generation`, saves v2 (fails, `workspace: save failed (partial-generation); kept g1`), then retries and commits v2 as g3. The driver checks the faulted g2 leftover was pruned (only g1, g3, COMMITTED and META remain), then damages g3 the same way as case 6. `check_store.relic` opens it | `workspace: committed image invalid; recovered g1`, note.txt reads `first version` |
| 8 | `case8_setup.relic` commits v1. The driver replaces the committed generation with `M2WS9` and points COMMITTED at g2, with META committed g2 previous g1. `case8_check.relic` opens it and tries Ctrl+S twice from the Editor | `workspace: committed image wrong version; store held; recovered g1`, note.txt reads `first version`, both saves report `workspace: save failed; store held (wrong-version); not written`, and every byte in the store is unchanged afterwards |
| 9 | The bad store path is a regular file. `case9_check.relic` opens it, types in the Editor, and presses Ctrl+S, then opens a fresh good store and presses Ctrl+S twice. `case9_verify.relic` reopens the good store | `workspace: cannot open store`, the workspace is not enabled, the Editor never says `saved` for the bad store, nothing is written to the bad path. The first good-store Ctrl+S reports the disk change the store switch caused (`changed on disk: ctrl+s again`); the second says `saved`. A fresh process reads the saved text back |

Not covered: the release of a held store (`wm.workspace_release()`),
which case 8 does not try; power loss; and two desktops writing one
store at once.

## Results (Nov 12 2026)

Rerun on Linux against main `dd1bb60` (PR #38 merged). Cases 1 to 5
were re-verified through the full suite, cases 6 to 9 through the
harness. No case changed outcome; every case still passes.

Full suite, from the repo root:

```console
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j4
ctest --test-dir build -C Release
```

Result: 486/486 passed, 0 failed, including all 23 workspace tests,
`check_shell`, `workspace_restart` and `workspace_kill`. That is the
evidence for cases 1 to 5: the golden tests that drove them on Nov 9
(`shell_workspace_session`, `workspace_kill`, `shell_workspace_faults`
and the rest) are in that suite and green at the new head, together
with the new PR #38 workspace tests.

Harness, from the repo root (Relic built from the pinned submodule
first: `cmake -S relic -B relic/build -DRELIC_BUILD_HOST=ON &&
cmake --build relic/build`):

```console
python3 tools/workspace-recovery-muse/run_cases.py --live --replay
```

Result: `RESULT: PASS, all four cases`, 49 ok lines, 0 failures.
The live run builds each store with the real implementation in
separate processes, damages files by hand between processes, and
checks what the next process installs. The replay run copies the
committed fixtures from `tests/fixtures/workspace-recovery/` and runs
only the check phases against them. Both runs passed every check.

| Case | How it was run | What was seen |
|---|---|---|
| 1 | full suite at dd1bb60 (`shell_workspace_session` and the workspace goldens) | same windows and files came back after a restart, as on Nov 9 |
| 2 | full suite at dd1bb60 (`workspace_kill`, `shell_workspace_faults`, `shell_workspace_session`) | a killed or faulted save left the last committed files and windows; the leftover partial was ignored |
| 3a | full suite at dd1bb60 (workspace goldens) | truncated committed image fell back to the earlier whole save with a visible notice |
| 3b | full suite at dd1bb60 (workspace goldens) | corrupt committed image fell back to the earlier whole save with a visible notice |
| 3c | full suite at dd1bb60 (workspace goldens) | wrong-version committed image held the store and fell back with a visible notice |
| 4 | full suite at dd1bb60 (workspace goldens) | a failed save was reported visibly and the windows and text stayed |
| 5 | full suite at dd1bb60 (workspace goldens) | a new, empty workspace directory opened with first-run defaults twice |
| 6 | harness live and replay at dd1bb60 | `workspace: committed image invalid; recovered g1; ignored uncommitted g3`, note.txt reads `first version` |
| 7 | harness live and replay at dd1bb60 | faulted save reports `workspace: save failed (partial-generation); kept g1`; retry commits v2 as g3; damaged g3 falls back with `workspace: committed image invalid; recovered g1`, note.txt reads `first version` |
| 8 | harness live and replay at dd1bb60 | `workspace: committed image wrong version; store held; recovered g1`; both Editor Ctrl+S attempts report `workspace: save failed; store held (wrong-version); not written`; every store byte unchanged afterwards |
| 9 | harness live and replay at dd1bb60 | `workspace: cannot open store`, workspace not enabled, Editor never says `saved` for the bad store, nothing written to the bad path; the first good-store Ctrl+S reports the disk-change guard (`changed on disk: ctrl+s again`); the second says `saved`; a fresh process reads the saved text back |

Fixture check: `make_fixtures.py` was run against dd1bb60 and the
regenerated fixtures came out byte-identical to the committed ones,
so PR #38 did not change what the implementation writes, and no
fixture or harness file needed a change.

Not covered: the release of a held store (`wm.workspace_release()`),
which case 8 does not try; power loss; and two desktops writing one
store at once.
