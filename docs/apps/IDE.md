# IDE

The Editor on a Relic program, plus a way to run it inside the desktop. Its window is 320 by 200, with the program on top and an output pane under it. It opens the same file a new Editor would (the last file opened in Files).

The title reads `IDE [status] path  (ctrl+s save, ctrl+r run)`. Every Editor key works the same way, including undo, selection and the changed-on-disk warning on Ctrl+S (see [the Editor](EDITOR.md)).

## Running

Ctrl+R runs the text in the buffer, saved or not. The program runs in Relic's self-hosted interpreter (`selfhost/interp` from the pinned Relic), inside the desktop: there is no separate process.

- `print` and `eprint` lines go to the output pane. The pane shows the last 6 lines and keeps the last 200.
- The status becomes `ran`, `error`, `waiting for input` or `stopped`.
- An error in the program shows as `line L: message`, and the pane's header says `ctrl+e: to line L`. Ctrl+E puts the cursor at the start of that line. An error inside a module the program used shows that module's path and line instead, and Ctrl+E does nothing then.

## Modules

`use std/...` loads Relic's own standard library. Any other `use` reads the module from the desktop's files, relative to the file being edited, as last saved; only the edited file runs unsaved. A missing module gives the usual "cannot find module" error.

## Input

`os.read_line` and `os.prompt` pause the run. The pane's header becomes `-- input (return: send, esc: stop) --` and its last line is the prompt and what you have typed.

| Input | What it does |
|---|---|
| Typing, Space, Backspace | edit the input line |
| Return | sends the line, and the run goes on |
| Escape | stops the run; the pane shows `stopped` |
| Ctrl+R | starts the run again from the top |

Other keys, Ctrl+S among them, are ignored while the run waits. Press Escape first to save. Escape goes to the IDE only while a run waits; at any other time it closes menus or quits the desktop as usual.

## Limits

- A run stops after 200,000 steps, and the pane shows `stopped: the program ran too long (200000 steps)`. The count starts again after each line of input, so a program can wait for input as long as it likes but cannot loop forever between inputs. `try` does not catch the stop.
- Some host built-ins are refused: exit, sleep, graphics and clipboard (the desktop owns the window), and writing, removing, renaming or making files on the real disk. Reading real files works.
- Not yet: programs that draw, clicking an error to jump to it, and runs that keep going in the background while not waiting for input.

## In the code

`ide` in `shell/wm.relic`, `_ide_*`, using the hooks Relic 1.0.44 and 1.0.45 added to `selfhost/interp` (`rt.out`, `rt.steps`, `rt.denied`, `rt.load`, `rt.input` and `interp.resume`). Design calls are in [the roadmap](../ROADMAP.md). Test: `shell_ide`.
