# IDE

The Editor on a Relic program, plus a way to run it inside the desktop. Its window is 320 by 200, with the program on top and an output pane under it. It opens the same file a new Editor would (the last file opened in Files). Ctrl+S commits the workspace the same way the Editor does. A `use` of one of your files reads the saved vfs text, which is what a new process loads. The run still cannot write the host disk. See [Workspace recovery](../workspace-recovery.md).

The title reads `IDE [status] path  (ctrl+s save, ctrl+r run)`. Every Editor key works the same way, including undo, selection and the changed-on-disk warning on Ctrl+S (see [the Editor](EDITOR.md)).

## Running

Ctrl+R (or F5, or Ctrl+Return) runs the text in the buffer, saved or not. The program runs in Relic's self-hosted interpreter (`selfhost/interp` from the pinned Relic), inside the desktop: there is no separate process.

- `print` and `eprint` lines go to the output pane. The pane shows the last 6 lines and keeps the last 200.
- The status becomes `ran`, `error`, `waiting for input` or `stopped`.
- An error in the program shows as `line L: message`, and the pane's header says `ctrl+e: to line L`. Ctrl+E puts the cursor at the start of that line, and so does a click on the error or on that header. An error inside a module the program used shows that module's path and line instead, and Ctrl+E does nothing then.
- Ctrl+/ comments out the line the cursor is on, putting `# ` after its leading spaces, or takes a `#` (and the space after it) back off. It is one undo step, and the cursor stays on the same character. With a selection it does every line the selection is on (not one it only ends at the start of, as after Ctrl+L): if they are all comments already (blank lines aside) it takes the `#` off each, else it puts one on each, in one undo step, and the lines stay selected.

## Modules

`use std/...` loads Relic's own standard library. Any other `use` reads the module from the desktop's files, relative to the file being edited, as last saved; only the edited file runs unsaved. A missing module gives the usual "cannot find module" error.

## Input

`os.read_line` and `os.prompt` pause the run. The pane's header becomes `-- input (return: send, esc: stop) --` and its last line is the prompt and what you have typed. A line wider than the window scrolls to keep the cursor in view.

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
| Escape, Ctrl+C | stops the run; the pane shows `stopped` |
| Ctrl+R, F5, Ctrl+Return | starts the run again from the top |

Ctrl+S saves the program and the run keeps waiting; the status reads `saved, waiting for input` (decided Oct 31 2026). Other keys are ignored while the run waits. Escape goes to the IDE while a run waits, and when text is selected (it drops the selection); at any other time it closes menus or quits the desktop as usual.

## Limits

- A run stops after 200,000 steps, and the pane shows `stopped: the program ran too long (200000 steps)`. The count starts again after each line of input, so a program can wait for input as long as it likes but cannot loop forever between inputs. `try` does not catch the stop.
- Some host built-ins are refused: exit, sleep, graphics and clipboard (the desktop owns the window), and writing, removing, renaming or making files on the real disk. Reading real files works.
- Parked with the Nov 7 2026 acceptance, not scheduled: programs that draw, and runs that keep going in the background while not waiting for input.

## In the code

`ide` in `shell/wm.relic`, `_ide_*`, using the hooks Relic 1.0.44 and 1.0.45 added to `selfhost/interp` (`rt.out`, `rt.steps`, `rt.denied`, `rt.load`, `rt.input` and `interp.resume`). Design calls are in [the roadmap](../ROADMAP.md). Tests: the `shell_ide*` goldens, `shell_editor_clipboard_ide`, and the Editor's tests, since the IDE shares its keys.
