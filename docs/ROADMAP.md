# Roadmap

M0N0LITH-2 is the MONOLITH 2 desktop written in Relic. The language roadmap is in the [Relic repo](https://github.com/DanielMellen-University/Relic/blob/main/docs/ROADMAP.md). When an app here needs something the language or std does not have, that work goes to Relic. Moving the pin is in [Building](BUILDING.md#moving-to-a-newer-relic). The Nov 7 2026 acceptance leaves it at 1.0.53 (`f97ad87`) unless a defect in the accepted scope cannot be fixed on that commit.

## Phase 1: Move in

- [x] Shell moved from Relic with its history (`shell/wm.relic`, `shell/desktop.relic`, `shell_wm` test)
- [x] Relic pinned as a submodule; CI builds it (with the host, `-DRELIC_BUILD_HOST=ON`) and runs the tests on Linux, macOS and Windows. Pin at Relic 1.0.53 (`f97ad87`); the pin moved six times on Oct 30 2026 alone (1.0.40 to 1.0.45), each in a `Pin Relic` commit that names what it brings. How to move it: [Building](BUILDING.md#moving-to-a-newer-relic)

## Phase 2: Desktop shell

- [x] Window manager, taskbar and Start menu: windows raise, close, drag, resize and minimize (the _ box, or the front window's taskbar button; click the button again to restore); taskbar buttons raise, and on the 640 pixel desktop, past 13 windows the extra ones go behind a +N button with a list; Start menu launches the apps. Tests `shell_wm`, `shell_minimize`, `shell_taskbar_*` and `shell_overflow_*`; on narrow desktops the buttons and the +N button never overlap (Oct 30). See [Windows](apps/WINDOWS.md) and [Taskbar](apps/TASKBAR.md)
- [x] Apps share one in-memory filesystem (`std/vfs` from Relic); Terminal, Files, the Editor and the IDE all use it

## Phase 3: Apps as proof

Closed Nov 7 2026 for the behavior the Linux GUI walkthrough demonstrated. See [Accepted](#accepted-nov-7-2026). The notes in each entry are what the model tests cover. Passing those tests is not, by itself, a GUI pass. Anything marked parked was not part of the pass.

- [x] Terminal (started: help, clear, history, echo, apps, date, pwd, cd, ls, cat, head, tail, wc, grep, find, sort, uniq, nl, mkdir, touch, write, rm, mv, cp, and `echo text > file` or `>>`, and `!!`; it keeps the last 200 lines of output and wraps to the window. Keys added Oct 31 2026: Up and Down bring back the last 50 commands, Tab completes command, file and folder names, Ctrl+C gives up the line, Ctrl+L clears, Ctrl+V pastes, Ctrl+Backspace removes a word; later the same day, sort, uniq and nl, and a count of lines for head and tail. On Nov 2 2026, quoted words, so a path may have spaces: Tab, ls, find, wc and Ctrl+V put such a name in quotes, and a quote inside a word (don't) is a letter; a cursor in the line (Left, Right, Home, End). Parked, not part of the pass: scrollback. See [Terminal](apps/TERMINAL.md))
- [x] Text editor (started: edits and saves VFS files with Ctrl+S, or Cmd+S on macOS, and warns first when another app changed the file; Ctrl+Z undo up to 500 steps; Delete; arrows, Home/End and Ctrl+arrow word jumps move the cursor; Shift+arrows and Ctrl+A select; a file opened in Files opens in the next Editor; a big file stays quick; on Oct 31 2026 copy, cut and paste with the desktop's own clipboard, Ctrl+Y redo, Tab and Shift+Tab indents, Return keeping the indent, Home past the leading spaces, Ctrl+Home and Ctrl+End, Page Up and Page Down, Ctrl+Backspace and Ctrl+Delete by word, and Esc dropping a selection; later on Oct 31, Ctrl+L, Ctrl+D, Ctrl+K and Ctrl+J for lines, Ctrl+] and Ctrl+[ for indents, and Ctrl+Shift with the word and file moves to select. On Nov 2 2026 a click moves the cursor and a drag selects, Ctrl+F finds (F3 and Shift+F3 again), Ctrl+H replaces, Ctrl+G goes to a line, and the line keys work on every selected line. Parked, not part of the pass: opening a file by path. See [Editor](apps/EDITOR.md))
- [x] File browser (started: browses the VFS with keys or clicks, folders marked with `/`; a double-click enters a folder once; Backspace goes up with the old folder selected; a long list follows the selected row, and opening a file selects it for the next Editor. Keys added Oct 31 2026: Home and End, Page Up and Page Down, and a letter or digit to jump to the next name starting with it; then Ctrl+Home and Ctrl+End, Left and Right to go up and into folders, and Ctrl+C to copy the selected path; on Nov 2 2026, F2 to rename. See [Files](apps/FILES.md))
- [x] Drawing app (started Oct 31 2026, Daniel approved: Paint, a 60 by 36 cell canvas with 8 colors, an eraser, brush sizes 1 to 4, fill, line, rectangle and ellipse tools (outline or filled), a color picker (`i`), clear, undo and redo, and save, save as and open as `.paint` text files in the desktop's files; see [Paint](apps/PAINT.md) for the design calls)
- [x] At least one game (started Oct 31 2026, Daniel approved: Snake on a 24 by 16 board, moving on the clock of its focused window; see [Snake](apps/SNAKE.md) for the design calls)
- [x] Relic IDE (started Oct 30 2026, Daniel approved with "your design calls": the Editor on a .relic file, Ctrl+R runs the text, saved or not, with an output pane under it, an error shows as `line L: message` and Ctrl+E puts the cursor on that line). Design calls:
  - It is the Editor's state and keys plus two keys, in `wm.relic` like the other apps, so editing, undo, selection and Ctrl+S work the same.
  - A run uses Relic's own `selfhost/interp` inside the desktop, not a separate process (the host has no way to start one). Relic 1.0.44 added the hooks: output goes to a list, a run stops after 200,000 steps (a loop that never ends cannot hang the desktop; `try` does not catch the stop), and named host built-ins are refused.
  - Refused: exit, sleep, graphics and clipboard (the desktop owns the window), and writing, removing, renaming or making files on the real disk. Reading real files and `use std/...` (from Relic's std) work.
  - `use` of the user's own files (approved Oct 30): any other `use` reads the module from the desktop's files, relative to the file being edited, as last saved (only the edited file runs unsaved). A missing module is the usual "cannot find module" error; an error inside one shows its path and line (Relic 1.0.45, `rt.load`).
  - Input (approved Oct 30): `os.read_line` and `os.prompt` pause the run, and the pane ends in an input line with the prompt. While it waits, typing goes to that line (Backspace, Space), Return sends it and the run goes on, Esc stops the run, and Ctrl+R starts it again; Ctrl+S saves (since Oct 31), and the other Editor keys wait until the run ends. The pane shows each prompt and line sent, as a terminal would. The 200,000 steps start again after each line sent, so a program may wait for input as long as it likes but cannot spin between inputs (Relic 1.0.45, `rt.input` and `interp.resume`). Esc goes to the IDE only while a run waits; otherwise it closes menus or quits the desktop as before.
  - The pane shows the last 6 lines (5 and the input line while waiting) and keeps 200. An error inside a std module shows that module's file and line, and Ctrl+E does nothing then.
  - Clicking the error, or the header naming Ctrl+E, jumps to its line (Nov 2 2026).
  - Parked, not part of the pass: programs that draw, and a run that goes on in the background while not waiting for input.
  - Decided Oct 31 2026 (approved through CoS): Ctrl+S saves while a run waits for input, and the run keeps waiting; the 200,000 steps start again after each input line, so they are per line, not per run.
  - User docs: [IDE](apps/IDE.md).

## Accepted (Nov 7 2026)

The desktop is a 640 by 480 SDL demo. It is not a bootable operating system, a production desktop, a durable filesystem, or a security sandbox. Relic stays pinned at 1.0.53 (`f97ad87`) unless a defect in this list cannot be fixed here.

Checked on Linux (Clang 18.1, CMake 3.28, SDL 2.30) from `f76aa2f`. `ctest` reported 183 tests passed. A display-backed walkthrough, with real mouse and keyboard events and screenshots of the SDL window, showed:

- Start opens the eight apps. Snake was also launched from the keyboard (Down, Return).
- Dragging Terminal's title bar moved it. The _ box minimized Notes, and its taskbar button restored the same line. The x box closed Notes. Dragging Clicker's bottom-right corner resized it. With 14 Clicker windows the bar showed +2 and a list of the two without a button.
- Terminal wrote `note.txt` (`echo` with `>`), made `docs`, appended `docs/plan.txt` (`alpha`, then `beta`), and wrote `hello.relic` with a quoted `print`. `ls` and Files showed those names. In Files, Down landed on `note.txt` and Return made the next Editor open `/home/note.txt` with `session-note`. Typing and Ctrl+S saved, and `cat note.txt` in that same Terminal showed the new line. Return on `hello.relic` made the next IDE open that file, and Ctrl+R printed `ide-out`.
- In the IDE, a program that reads a line took `ada` and printed `got ada`. `print(1` showed `line 1: unclosed '('`, and Ctrl+E put the cursor at the start of that line. `while true` with `let y = 1` stopped, the pane said `the program ran too long (200000 steps)`, and the desktop kept running.
- Paint drew a red stroke, Ctrl+S said saved, and a new Paint window opened `/home/picture.paint` with that stroke and status open.
- Snake, after an arrow, showed the board, the food, and score 0. Clicker went from 1 to 2 to 1 on a click, Space, and Backspace. Notes kept `keep this note` across minimize and restore.
- Escape quit. Files in a new desktop showed only `..` and `welcome.txt`.

Commands and keys not named here were not pressed in the window. The 183 tests still cover them, and they do not open SDL. macOS and Windows GUI were not tried. CI on `f76aa2f` ([run 42250126049](https://github.com/DanielMellen-University/M0N0LITH-2/actions/runs/42250126049)) built and passed the same 183 tests on Ubuntu, macOS and Windows. That run is not a GUI pass.

### Parked (not next work)

- Terminal scrollback
- Editor open by path
- Host mounts
- The desktop following the real window size, and maximize
- IDE programs that draw, and a run that continues in the background while it is not waiting for input

### Limits that are part of the pass

- The shared files last for one run. Quitting drops them. That was seen: after Escape, a new Files had only `welcome.txt`.
- New windows open at fixed sizes. Resize of a window works. The desktop stays 640 by 480.
- The clipboard is the desktop's own.
- An IDE run stops after 200,000 steps between inputs. Reading a real file is allowed. The run is not a sandbox.

### What would still block a release

A documented workflow in the list above that fails, a file changed inside one session when nothing wrote it, or a loop that does not stop inside the step budget. A newer Relic, and the parked items, are not that list.

Next work is maintenance of this list only.
