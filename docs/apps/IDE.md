# IDE

The Editor on a Relic program, plus a way to run it inside the desktop. Its window is 320 by 200, with the program on top and an output pane under it. It opens the same file a new Editor would (the last file opened in Files). Ctrl+S commits the workspace the same way the Editor does. A `use` of one of your files reads the saved vfs text, which is what a new process loads. The run still cannot write the host disk. See [Workspace recovery](../workspace-recovery.md).

The title reads `IDE [status] path  (ctrl+s save, ctrl+r run)`. Every Editor key works the same way, including undo, selection and the changed-on-disk warning on Ctrl+S (see [the Editor](EDITOR.md)). Ctrl+R, F5, Ctrl+E, Ctrl+/ and a key typed while a run waits for input cancel that warning too; only a second Ctrl+S with nothing in between overwrites.

## Running

Ctrl+R (or F5, or Ctrl+Return) runs the text in the buffer, saved or not. The program runs in Relic's self-hosted interpreter (`selfhost/interp` from the pinned Relic), inside the desktop: there is no separate process.

- `print` and `eprint` lines go to the output pane. The pane shows the last 6 lines and keeps the last 200, plus the run line under the header. Page Up and Page Down move by the program lines on show above that pane, not by the rows the pane takes.
- The status becomes `ran`, `error`, `waiting for input` or `stopped`.
- Under the pane's header, a run line says how it ended and how long it took: `-- run exit 0 12ms --` when it finished, `-- stop exit 1 12ms --` when it failed or was cut off at 200,000 steps, `-- run 12ms --` while it waits for input, and `-- stop exit 130 12ms --` when Escape or Ctrl+C stops it. The time is milliseconds from the start of that Ctrl+R.
- A compile error or a runtime error is a row of that pane, `file:line:col message`, the same place Relic's tools report (`file:line:col: error: message`). A file with more than one syntax error lists them, up to 8. The header reads `ctrl+e: line L col C`. Ctrl+E puts the cursor on that column, and so does a click on the error row or on that header. F6 focuses the list: Up and Down move, Enter jumps. Alt+Down and Alt+Up move to the next or previous error and jump. The error's line is highlighted in the editor. An error inside a module the program used names that module's path, and Ctrl+E does nothing then. A click on a printed line that is not an error moves nothing.
- While a run waits for input, the pane's header begins with `[stop]`. Clicking those six characters stops the run, as Escape and Ctrl+C do. The program itself runs between frames, so a loop that has not asked for input cannot be clicked until it stops or waits.
- Ctrl+/ comments out the line the cursor is on, putting `# ` after its leading spaces, or takes a `#` (and the space after it) back off. It is one undo step, and the cursor stays on the same character, including a cursor still in the indent before the `#`. With a selection it does every line the selection is on (not one it only ends at the start of, as after Ctrl+L): if they are all comments already (blank lines aside) it takes the `#` off each, else it puts one on each, in one undo step, and the lines stay selected. A selection of only blank lines changes nothing and is not an undo step.

## Modules

`use std/...` loads Relic's own standard library. Any other `use` reads the module from the desktop's files, relative to the file being edited, as last saved; only the edited file runs unsaved. A missing module gives the usual "cannot find module" error.

## Input

`os.read_line` and `os.prompt` pause the run. The pane's header becomes `[stop] return: send, esc: stop` and its last line is the prompt and what you have typed. A line wider than the window scrolls to keep the cursor in view. Clicking `[stop]` stops the run.

| Input | What it does |
|---|---|
| Typing, Space, Backspace | edit the input line at its cursor |
| Left, Right, Home, End | move the cursor in the input line |
| Ctrl+Left, Ctrl+Right | move it by words |
| Delete, Ctrl+Delete | remove the character, or the word, after the cursor |
| Ctrl+Backspace | removes the word before the cursor |
| Ctrl+K | removes the rest of the line after the cursor |
| Ctrl+U | removes everything before the cursor (all of it at the end) |
| Ctrl+V | adds the first line of the desktop's clipboard to it |
| Return | sends the line, and the run goes on |
| Escape, Ctrl+C | stops the run; the pane shows `stopped` and `-- stop exit 130 …ms --` |
| Ctrl+R, F5, Ctrl+Return | starts the run again from the top |

Ctrl+S saves the program and the run keeps waiting; the status reads `saved, waiting for input` (decided Oct 31 2026). Other keys are ignored while the run waits. Escape goes to the IDE while a run waits, and when text is selected (it drops the selection); at any other time it closes menus or quits the desktop as usual.

## Limits

- A run stops after 200,000 steps, and the pane shows `stopped: the program ran too long (200000 steps)`. The count starts again after each line of input, so a program can wait for input as long as it likes but cannot loop forever between inputs. `try` does not catch the stop.
- Some host built-ins are refused: exit, sleep, graphics and clipboard (the desktop owns the window), and writing, removing, renaming or making files on the real disk. Reading real files works.
- Parked with the Nov 7 2026 acceptance, not scheduled: programs that draw, and runs that keep going in the background while not waiting for input.

## In the code

`ide` in `shell/wm.relic`, `_ide_*`, and `shell/ide_diag.relic` for the error list (`file:line:col message`), the jump to a column, and parsing the toolchain's `file:line:col: error: message` lines. The run uses the hooks Relic 1.0.44 and 1.0.45 added to `selfhost/interp` (`rt.out`, `rt.steps`, `rt.denied`, `rt.load`, `rt.input` and `interp.resume`). Design calls are in [the roadmap](../ROADMAP.md). Tests: `shell_ide_diag` for parsing and navigation, the other `shell_ide*` goldens, `shell_editor_clipboard_ide`, and the Editor's tests, since the IDE shares its keys.
