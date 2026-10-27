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

Launch fits the initial window to the desktop, and moving it keeps part of the title bar reachable. Resizing limits its right and bottom edges to the desktop and taskbar where the minimum size permits. A moved window can extend beyond those edges; resizing does not move its top-left corner.

## An app

An app is a map: `name`, `width`, `height`, `init()`, `lines(state)`, `on_click(state, x, y)` and `on_key(state, key)`. `lines` gives the text rows. `visible_lines(w)` cuts them to what fits the window, which is what `desktop.relic` draws, so no text leaves its window. Two optional fields change how rows are chosen:

- `tail: true` and `pinned: n` for an app you type into at the end (Terminal, Editor, Notes): the first `n` lines stay, then the last ones that fit. Before it asks an app of this kind for `lines`, `visible_lines` puts the window's `rows` and `cols` in the app's state; Editor builds only `rows` lines of a big file, and Terminal wraps its output to `cols`.
- `selected(state)` for a list (Files): the title line stays and the list scrolls just far enough to show the selected line.

Terminal, Files and Editor work on one in-memory filesystem (`std/vfs`), so a change in one shows in the others. An app has to cope with that: a folder or file can be gone between two frames.

Files remembers the last row content and available row count when drawn. Once it has been drawn, a row click after a directory change or resize is ignored until the next draw supplies the current layout; keyboard navigation refreshes the directory independently. Opening a file in Files sets the path used by the next Editor window. The filesystem and that path are module-level state, shared even across desktop maps created in the same process.

## Tests

CMake discovers every `tests/*.relic` program. Each current test drives `wm.relic` and prints what happened; its standard output must match the `.out` file next to it (or be empty if that file is absent). `shell_fuzz` uses fixed seeds on two desktop sizes and checks model invariants after every step. CTest also runs `relic check` on both shell files. To change an expected output on purpose, run the test, read the diff, and save the new output.
