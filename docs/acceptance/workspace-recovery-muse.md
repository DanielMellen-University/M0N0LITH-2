# Persistent workspace recovery: acceptance cases

Status: specification only. Every case below is UNRUN. No case has been
executed against any build, and no result is claimed here.

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

## Blocked: fixtures and fault injection

Fixture assets under `tests/fixtures/workspace-recovery/` are blocked.
The fixture and fault-injection contract from Engineer has not arrived,
so this batch creates no fixtures. Until that contract is handed over,
there is no agreed way to drive a save, to cut a save off partway, or
to damage saved workspace data in a repeatable way. Execution cannot
start until the interface is ready. When the contract lands, each case
gains a fixture note naming the assets it uses, and its status moves
from UNRUN to PASS or FAIL with the date and the build it ran on.

### Update: the contract is now on main (D0120, 2026-11-09)

Engineer's implementation PR #28 has since merged (head d520a17f,
merge 625dcc8a, merged by DanielMellen-University 2026-11-09), so
docs/workspace-recovery.md now exists on main. That contract replaces
the rejected head c94f809: it adds the META backup file,
wm.workspace_release(), and the fallback and hold rules. Cases 6 to 9
below are specified against that contract as it stands on main. No
fixture assets are created in this batch, and every case in this
document is still UNRUN. Whether the merged contract is the published
fixture contract Engineer meant in D0118 is for Engineer to confirm;
until then, no fixtures are built. The seven earlier cases still
carry no fixture notes; those are added when the cases are first
executed.

## How to read a case

- Setup: the visible state before the case starts.
- Action or fault: what is done, or what goes wrong.
- Expected visible outcome: what the person at the screen must see.
- Data-preservation assertions: what user data must survive, exactly.
- Status: UNRUN until the case is actually executed.

Where a case says "the desktop shows that the saved workspace could not
be used", the exact words and the exact place of the notice are the
implementation's choice. The requirement is that the failure is visible
and not silent. Where a case says "first-run defaults", that means the
desktop a first-time user sees: no windows open, the Start menu offering
the eight apps (Clicker, Notes, Terminal, Files, Editor, IDE, Paint,
Snake), an empty shared filesystem, and Snake's best score at 0.

A save is "complete" when the desktop has finished writing the
workspace and a later start can read it back whole. The cases below
assume a save has completed where they say so. How a save is started,
and how the desktop reports it, is set by the implementation and will
be pinned down by the fixture contract.

---

## Case 1: Cross-app save and restart roundtrip

Status: UNRUN.

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

Status: UNRUN.

Setup: Start the desktop with no saved workspace. Open the Editor on a
file, write a first version, and save it. Save the workspace, so the
first version is the last committed version. Then edit the file to a
second version and save it in the Editor, but do not save the workspace
again.

Action: Start a workspace save and cut it off partway through, so the
save never completes. Then quit the desktop and start it again. How a
save is cut off is defined by the fixture contract, which is still
blocked.

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

Status: UNRUN.

Setup: Start the desktop, open the Editor on a file with saved text,
open Paint on a saved picture, save the workspace, and quit. Then
damage the saved workspace data by removing part of it, so only part of
what was saved is still there. How the data is damaged is defined by
the fixture contract, which is still blocked.

Action: Start the desktop again.

Expected visible outcome: The desktop starts, it does not hang, and it
shows that the saved workspace could not be used. It does not open
windows with half-restored content and present them as if they were
whole. It falls back to first-run defaults: no windows open, the Start
menu offering the eight apps, an empty shared filesystem.

Data-preservation assertions:

- No window shows content taken from the truncated data as if it were
  the saved content.
- No file is shown with content that was never saved.
- The failure is reported on screen instead of being silent.

## Case 3b: Corrupt saved workspace data

Status: UNRUN.

Setup: Start the desktop, open the Editor on a file with saved text,
open Paint on a saved picture, save the workspace, and quit. Then
damage the saved workspace data by changing part of it, without
removing any of it, so the saved data no longer says what it said.
How the data is damaged is defined by the fixture contract, which is
still blocked.

Action: Start the desktop again.

Expected visible outcome: The desktop starts, it does not hang, and it
shows that the saved workspace could not be used. It does not open
windows with altered content and present them as if they were the saved
content. It falls back to first-run defaults: no windows open, the
Start menu offering the eight apps, an empty shared filesystem.

Data-preservation assertions:

- No window shows altered content as if it were the content the user
  saved.
- No file is shown with content that differs from what was saved.
- The failure is reported on screen instead of being silent.

## Case 3c: Unsupported-version saved workspace data

Status: UNRUN.

Setup: Start the desktop, open the Editor on a file with saved text,
save the workspace, and quit. Then replace the saved workspace data
with data written in a newer version than this desktop understands,
so the data is well-formed but from a version the desktop does not
support. How that replacement data is produced is defined by the
fixture contract, which is still blocked.

Action: Start the desktop again.

Expected visible outcome: The desktop starts, it does not hang, and it
shows that the saved workspace is from a version it cannot use. It does
not try to read the newer data as if it were its own, and it does not
open windows with guessed content. It falls back to first-run defaults:
no windows open, the Start menu offering the eight apps, an empty
shared filesystem.

Data-preservation assertions:

- No window shows content guessed from data the desktop does not
  understand.
- The saved data from the newer version is left alone, not overwritten
  or deleted by the fallback.
- The failure is reported on screen instead of being silent.

## Case 4: Visible save failure

Status: UNRUN.

Setup: Start the desktop with no saved workspace. Open the Editor on a
file, write text, and save it with Ctrl+S. Open Paint, draw a mark,
and save it as a picture file.

Action: Make the workspace save fail. For example, the place the
workspace is saved to cannot be written. How the failure is arranged
is defined by the fixture contract, which is still blocked. Then keep
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

Status: UNRUN.

Setup: Start the desktop with no saved workspace at all, as a
first-time user would. No files have been created and no workspace
has ever been saved.

Action: Start the desktop and look at what it shows.

Expected visible outcome: The desktop opens with no windows, the Start
menu offers the eight apps, and the shared filesystem is empty. Snake
shows a best score of 0. Nothing from an earlier session appears,
because there is no earlier session.

Data-preservation assertions:

- No window, file, or score from any other session is shown.
- The shared filesystem contains no files.
- Closing and starting the desktop again, still with no save, shows
  the same defaults.

## Case 6: Corrupt committed generation must not load a newer uncommitted generation (D0118-1)

Status: UNRUN.

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

Fixture note: COMMITTED names g2; g2.m2ws is rejected by the parser
(truncated, a bad record, or a raw CR); g1.m2ws is complete and valid;
g3.m2ws is complete and valid and is named by neither COMMITTED nor
META. A change that still parses as M2WS1 is installed, including
edited file text: this desktop has no checksum. A first line other
than M2WS1 is a wrong version, which holds the store (case 8) instead
of this fallback. Per the contract load rule for a truncated or
otherwise invalid committed generation, the fallback is the newest
valid generation older than the named one, which is g1. A newer
complete file is ignored uncommitted and is not installed. Quitting
does not publish another generation, so the damaged g2 is what the
next start opens.

## Case 7: Corrupted retry commit keeps the actual prior committed generation (D0118-2)

Status: UNRUN.

Setup: Start the desktop with no saved workspace. Open the Editor on
a file, write a first version, and save the workspace, so the first
version is committed. Edit the file to a second version. Start a
workspace save and cut it off partway, with the fault stage
partial-generation or full-uncommitted, so the second version is never
committed. The fault arm is one-shot, so the next save runs with no
fault armed: save the workspace again, so the second version commits
as a new generation. Quit. This desktop does not publish another
generation on the way out. Then damage that committed generation so
the parser rejects it.

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
(truncated, a bad record, or a raw CR), not merely edited into another
valid M2WS1 image; g1.m2ws is complete and valid; META names committed
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

Status: UNRUN.

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

Status: UNRUN.

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
- A later save to a store that opens still commits the shared files,
  and a restart restores those files. Open windows, Notes, Clicker,
  and unsaved Editor, IDE, and Paint buffers are not in this store, so
  a restart does not bring them back.
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
| 1 | Cross-app save and restart roundtrip | UNRUN |
| 2 | Interrupted save keeps the last committed version | UNRUN |
| 3a | Truncated saved workspace data | UNRUN |
| 3b | Corrupt saved workspace data | UNRUN |
| 3c | Unsupported-version saved workspace data | UNRUN |
| 4 | Visible save failure | UNRUN |
| 5 | First-run defaults | UNRUN |
| 6 | Corrupt committed generation, newer uncommitted not loaded | UNRUN |
| 7 | Corrupted retry commit keeps prior committed generation | UNRUN |
| 8 | Unsupported-version store held through normal writes | UNRUN |
| 9 | Requested store that cannot be opened never reports saved | UNRUN |

Specified cases: 11. Executed cases: 0. Fixture assets: none built in
this batch. The contract is now on main (docs/workspace-recovery.md,
PR #28 merged 2026-11-09); fixture notes for the earlier cases are
still pending.
