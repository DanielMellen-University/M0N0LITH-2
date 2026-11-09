# Persistent workspace recovery: acceptance cases

Status: run on Nov 9 2026 against PR #33 (window session snapshot). All
seven cases pass; see "Results" at the end for how each was run and what
was not tried. Cases 3a, 3b, 3c and 5 were reworded on that date, before
the results were recorded; the reasons are in "Wording changes".

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

No fixture assets were added. Faults were made the way the Results table
says: by the store's own fault hooks in the golden tests, by killing a
process, and by editing the saved files by hand between two processes.

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

Status: PASS (Nov 9 2026).

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

Status: PASS (Nov 9 2026).

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

Status: PASS (Nov 9 2026).

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

Status: PASS (Nov 9 2026).

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

Status: PASS (Nov 9 2026).

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

Status: PASS (Nov 9 2026).

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

Status: PASS (Nov 9 2026).

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

Specified cases: 7. Executed cases: 7.

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
