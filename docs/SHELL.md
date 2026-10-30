# How the shell is put together

Two files in `shell/`:

- `wm.relic` is the model: windows, the taskbar, the Start menu and the five apps. It draws nothing, so the tests run it without SDL.
- `desktop.relic` draws the model with `std/graphics` and runs the event loop. It is the only file that needs SDL.

## The model

`new_desktop(width, height, apps)` gives a map with `windows` (running apps, the last one on top), `apps` (what Start can launch), `menu_open`, `overflow_open` (the hidden-windows list below), `drag` and `clicks` (1, or the `clicks` count of the `mouse_down` that `handle` is passing on, so 2 for the second press of a double-click). A window is `{id, app, state, x, y, width, height, minimized}`. `state` belongs to the app.

Input goes in through four calls, or through `handle(d, e)`, which takes one `graphics.next_event()` map and calls the right one:

| Call | What it does |
|---|---|
| `click(d, x, y)` | a press: Start, a tab, a window's x or _ box, its title (starts a move), its corner (starts a resize), or the app inside. Gives a word for what it hit: `launch`, `start`, `overflow`, `tab`, `minimize`, `bar`, `close`, `title`, `resize`, `app`, `desktop` |
| `motion(d, x, y)` | moves or resizes the window being dragged, if any |
| `release(d)` | ends a drag |
| `dismiss(d)` | closes the Start menu and the hidden-windows list; true if one was open (desktop.relic quits on an Escape that closed nothing) |
| `key(d, name)` | a key for the window on top; `space` for the space bar, `ctrl+s` for Ctrl+S |

Launch fits the initial window to the desktop, and moving it keeps 40 pixels of the title bar on screen to grab (beside the _ and x boxes when it is off the left edge). Resizing limits its right and bottom edges to the desktop and taskbar where the minimum size permits. A moved window can extend beyond those edges; resizing does not move its top-left corner.

## The taskbar

Every window has a tab in launch order (`tabs(d)`). Tabs are `tab_width` (90) pixels wide while they fit, then shrink together down to `min_tab` (40, four letters of the name). `tab_box(d, i)` is the box of shown tab `i`.

When even `min_tab` tabs would run off the bar (more than 13 windows on a 640 pixel desktop), `tab_capacity(d)` tabs are shown (12 there, since the button needs room too) and the rest are hidden behind a button at the right end of the bar:

- `shown_tabs(d)` is the tabs that get a button: the first ones in launch order. If the focused window is not among them it takes the place of the last one, so the focused window always has a tab. `hidden_tabs(d)` is the others, in launch order.
- `overflow_box(d)` is the `+N` button (`overflow_label(d)` is its text), or `none` when every window has a tab. It is 40 pixels wide, wider from 1,000 windows on so the label fits. Pressing it toggles `d.overflow_open` and gives `overflow`.
- On a bar too narrow for one `min_tab` tab beside the button (under about 150 pixels), the one shown tab gets the room that is left, so it never overlaps the button; its label is cut to what fits, or empty.
- While the list is open, `overflow_item_box(d, i)` is the row for `hidden_tabs(d)[i]`. It stacks upward from the bar at the right edge, like the Start menu, and starts a new column to the left when it reaches the top of the desktop. Pressing a row restores that window and brings it to the front (so it gets a tab) and gives `tab`. Rows are drawn and take presses up to `overflow_shown(d)`, which is what fits across the desktop (200 at 640 by 480).
- Any other press closes the list and then does what it normally does. Closing windows until everything fits removes the button and the list.

## An app

An app is a map: `name`, `width`, `height`, `init()`, `lines(state)`, `on_click(state, x, y)` and `on_key(state, key)`. `lines` gives the text rows. `visible_lines(w)` cuts them to what fits the window, which is what `desktop.relic` draws, so no text leaves its window. Two optional fields change how rows are chosen:

- `tail: true` and `pinned: n` for an app you type into at the end (Terminal, Editor, Notes): the first `n` lines stay, then the last ones that fit. Before it asks an app of this kind for `lines`, `visible_lines` puts the window's `rows` and `cols` in the app's state; Editor builds only `rows` lines of a big file, and Terminal wraps its output to `cols` and builds only the last `rows` rows.
- `selected(state)` for a list (Files): the title line stays and the list scrolls just far enough to show the selected line. `visible_lines` puts the window's `cols` in its state too, and Files shortens a long folder path in its title to fit.

Terminal, Files and Editor work on one in-memory filesystem (`std/vfs`), so a change in one shows in the others. An app has to cope with that: a folder or file can be gone between two frames. Editor keeps the text it last read or saved (`disk`) and warns before a Ctrl+S would overwrite a change another app made (a second Ctrl+S in a row writes).

Files opens a row on a single click and ignores the second press of a double-click (`_click_in` puts `d.clicks` in its state), so double-clicking a folder enters it once. Files remembers the last row content and available row count when drawn. Once it has been drawn, a row click after a directory change or resize is ignored until the next draw supplies the current layout; keyboard navigation refreshes the directory independently. Opening a file in Files sets the path used by the next Editor window. The filesystem and that path are module-level state, shared even across desktop maps created in the same process.

## Tests

CMake discovers every `tests/*.relic` program. Each current test drives `wm.relic` and prints what happened; its standard output must match the `.out` file next to it (or be empty if that file is absent). `shell_fuzz` uses fixed seeds on two desktop sizes and checks model invariants after every step. `shell_apps_fuzz` does the same for the apps: random commands from two Terminals while Files and Editor work on the same filesystem. CTest also runs `relic check` on both shell files. To change an expected output on purpose, run the test, read the diff, and save the new output.
