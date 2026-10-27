# How the shell is put together

Two files in `shell/`:

- `wm.relic` is the model: windows, the taskbar, the Start menu and the five apps. It draws nothing, so the tests run it without SDL.
- `desktop.relic` draws the model with `std/graphics` and runs the event loop. It is the only file that needs SDL.

## The model

`new_desktop(width, height, apps)` gives a map with `windows` (running apps, the last one on top), `apps` (what Start can launch), `menu_open` and `drag`. A window is `{id, app, state, x, y, width, height, minimized}`. `state` belongs to the app.

Input goes in through four calls, or through `handle(d, e)`, which takes one `graphics.next_event()` map and calls the right one:

| Call | What it does |
|---|---|
| `click(d, x, y)` | a press: Start, a tab, a window's x or _ box, its title (starts a move), its corner (starts a resize), or the app inside. Gives a word for what it hit: `launch`, `start`, `tab`, `minimize`, `bar`, `close`, `title`, `resize`, `app`, `desktop` |
| `motion(d, x, y)` | moves or resizes the window being dragged, if any |
| `release(d)` | ends a drag |
| `key(d, name)` | a key for the window on top; `space` for the space bar, `ctrl+s` for Ctrl+S |

Windows are kept on the desktop: `launch` and drags keep part of the title bar in view, and a resize keeps a window inside the desktop and above the taskbar.

## An app

An app is a map: `name`, `width`, `height`, `init()`, `lines(state)`, `on_click(state, x, y)` and `on_key(state, key)`. `lines` gives the text rows. `visible_lines(w)` cuts them to what fits the window, which is what `desktop.relic` draws, so no text leaves its window. Two optional fields change how rows are chosen:

- `tail: true` and `pinned: n` for an app you type into at the end (Terminal, Editor, Notes): the first `n` lines stay, then the last ones that fit.
- `selected(state)` for a list (Files): the title line stays and the list scrolls just far enough to show the selected line.

Terminal, Files and Editor work on one in-memory filesystem (`std/vfs`), so a change in one shows in the others. An app has to cope with that: a folder or file can be gone between two frames.

## Tests

Each `tests/shell_*.relic` drives `wm.relic` with fake input and prints what happened; the output must match the `.out` file next to it. `shell_fuzz` throws random input at the model and checks the invariants above after every step. To change an expected output on purpose, run the test, read the diff, and save the new output.
