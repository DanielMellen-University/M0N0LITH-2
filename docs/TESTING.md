# Tests

Every test is a Relic program in `tests/` that drives `shell/wm.relic` with fake clicks, keys and graphics events and prints what happened. None of them needs SDL.

## Running them

After building Relic (see [Building](BUILDING.md)):

```
cmake -S . -B build
ctest --test-dir build -C Release --output-on-failure
```

One test: `ctest --test-dir build -C Release -R golden_shell_ide`. Or run it straight from the `tests` folder, which is where the runner starts it: `cd tests && ../relic/build/relic shell_ide.relic`.

## How they are checked

CMake finds every `tests/*.relic` and adds it as `golden_<name>`. `tools/run_golden.cmake` runs it from `tests/`, and it passes when it exits with 0 and its standard output matches `<name>.out` exactly (Windows line endings are ignored). A test with no `.out` file must print nothing. One more test, `check_shell`, runs `relic check` on `wm.relic` and `desktop.relic`, which catches syntax errors and undefined names in the drawing code no test runs. That is 88 tests in all, and CI runs them on Linux, macOS and Windows.

`shell_fuzz` and `shell_apps_fuzz` use fixed seeds, so their output is the same on every run. `shell_fuzz` checks the window model's invariants after every random step on two desktop sizes; `shell_apps_fuzz` sends random commands from two Terminals while Files and the Editor work on the same filesystem.

## Adding or changing one

Write `tests/shell_<topic>.relic`, run it, read its output, and save that as `tests/shell_<topic>.out` once it is right. To change an expected output on purpose, do the same and read the diff before committing. Add it to the list below.

## The list

### Windows and the Start menu

| Test | What it covers |
|---|---|
| `shell_wm` | drives wm.relic with fake clicks and keys; output must match shell_wm.out |
| `shell_lifecycle` | window ids, focus and tab order through lifecycle changes |
| `shell_minimize` | minimize and restore from the taskbar and the _ box |
| `shell_start_menu` | the Start button opens and closes the menu |
| `shell_menu_focus` | keyboard focus while the Start menu or the +N list is open |
| `shell_menu_edges` | Start menu row and taskbar hit boundaries |
| `shell_drag_resize` | dragging and resizing keep windows reachable |
| `shell_resize_offset` | resizing follows the point grabbed in the handle |
| `shell_launch_small` | cascaded windows fit a small desktop |
| `shell_cascade_gaps` | a new window does not open on top of another after closes |
| `shell_missed_release` | a lost mouse-up does not leave a drag running |
| `shell_outside_click` | presses outside the desktop do not hit its controls |
| `shell_title` | window titles fit beside the title bar buttons |
| `shell_escape` | Escape closes the Start menu or +N list before it quits |

### Taskbar

| Test | What it covers |
|---|---|
| `shell_many_windows` | windows cascade and wrap, taskbar tabs shrink to fit |
| `shell_taskbar_overflow` | the +N button and hidden-windows list at 14 to 300 windows |
| `shell_taskbar_narrow` | taskbar tabs and the +N button on narrow desktops and with many windows |
| `shell_overflow_edges` | overflow threshold and list row boundaries |
| `shell_overflow_lifecycle` | focus and stacking as windows change with the list open |
| `shell_overflow_all_minimized` | overflow tabs and restore when no window is focused |
| `shell_overflow_limit` | the last visible row and the 200-row list limit |
| `shell_overflow_titles` | empty, long and non-ASCII window names in overflow |
| `shell_overflow_speed` | the hidden-windows list stays quick at 300 windows |

### Input events

| Test | What it covers |
|---|---|
| `shell_input` | graphics events turned into keys and clicks (ctrl+s, text, the mouse) |
| `shell_event_keys` | named keys, modifiers and ignored events |
| `shell_altgr` | AltGr (Ctrl+Alt) typing is text, not Ctrl+S |
| `shell_cmd_keys` | Cmd with a letter acts like Ctrl (Cmd+S, Cmd+Z, Cmd+A on macOS) |
| `shell_held_keys` | repeated key_down events from held keys, and key_up |
| `shell_mouse_buttons` | left and right mouse buttons during a drag |

### Drawing and clipping

| Test | What it covers |
|---|---|
| `shell_clip` | text cut to the window, Files scrolling to the selection |
| `shell_render_modes` | clipping and row selection for plain and tail apps |

### Clicker and Notes

| Test | What it covers |
|---|---|
| `shell_small_apps` | Editor, Notes and Clicker |
| `shell_clicker_edges` | rapid input and Clicker state after reopening |
| `shell_app_focus` | Notes and Clicker state across focus and window controls |
| `shell_notes_resize` | Notes text clipping and edits across resizes |
| `shell_notes_input_edges` | single-line input and reopening Notes |

### Terminal

| Test | What it covers |
|---|---|
| `shell_terminal` | Terminal commands: extra spaces, folders, redirects, errors |
| `shell_terminal_history` | the Terminal keeps its last 200 lines |
| `shell_terminal_errors` | Terminal error messages (mv, mkdir, cat, paths through a file) |
| `shell_terminal_touch` | touch preserves existing entries and creates empty files |
| `shell_terminal_write` | write replaces content and handles empty text |
| `shell_terminal_cat_blank` | cat preserves blank lines in files |
| `shell_terminal_cat_big` | cat of a 100,000-line file stays quick |
| `shell_terminal_extra_words` | clear, apps, date and pwd reject extra words |
| `shell_terminal_dash_paths` | write and echo > refuse paths starting with - |
| `shell_terminal_why` | errors name the missing folder or the part that is a file |
| `shell_terminal_slash` | a path ending in / must be a folder |
| `shell_terminal_redirect` | echo redirects and missing destinations |
| `shell_terminal_redirect_errors` | failed redirects and output after clear |
| `shell_terminal_edges` | Terminal path and input boundaries |
| `shell_terminal_root` | root and normalized path operations |
| `shell_terminal_stale` | Terminal recovers when its current folder is removed |
| `shell_terminal_ls` | Terminal packs directory listings to the window width |
| `shell_terminal_wrap` | Terminal wraps long lines to the window width |
| `shell_terminal_frame` | Terminal builds only the rows that fit, matching a full wrap |
| `shell_help` | Terminal help and app names match the available commands and apps |
| `shell_date` | the date command and its UTC format |

### Files

| Test | What it covers |
|---|---|
| `shell_files_click` | clicking rows in Files |
| `shell_files_back` | Backspace and ".." select the folder you came from |
| `shell_files_double_click` | the second click of a double-click is ignored |
| `shell_files_boundaries` | root, empty folders, unusual names and reopening Files |
| `shell_files_long_names` | clipped names open the full path and deleted selections do not open replacements |
| `shell_files_title` | Files keeps the end of a long folder path in its title |
| `shell_files_hidden` | clicks below the visible Files rows do nothing |
| `shell_files_stale` | Files when another app removed the selected file |
| `shell_files_ancestor` | Files and Terminal recover after an ancestor folder moves |
| `shell_files_selection` | Files keeps its selection across directory changes |
| `shell_files_changed_click` | Files ignores a click on rows changed since drawing |
| `shell_files_resize_click` | Files waits for a redraw after a resize before accepting a row click |

### Editor

| Test | What it covers |
|---|---|
| `shell_editor_title` | Editor title keeps the file name and the status in view |
| `shell_editor_open_status` | Editor status on opening: open, new file, or why not |
| `shell_editor_stale` | Editor reports a file removed before opening |
| `shell_editor_edges` | Editor empty buffers, line edges and failed saves |
| `shell_editor_disk_changed` | Ctrl+S warns once when another app changed the file |
| `shell_editor_undo` | Ctrl+Z undoes edits one step at a time, up to 500 |
| `shell_editor_select` | Shift+arrows and Ctrl+A select; typing and Backspace replace the selection |
| `shell_editor_cursor` | arrows, Home, End and Ctrl+arrow word jumps move the cursor |
| `shell_editor_delete` | Delete removes the next character or the selection; Ctrl+Z puts it back |
| `shell_editor_long_line` | long-line clipping, ignored movement and saving the full buffer |
| `shell_editor_replaced` | saving after a file is removed or replaced by a folder |
| `shell_big_file` | the Editor on a file of thousands of lines stays quick |
| `shell_last_lines` | Editor line splitting at empty and trailing newline boundaries |
| `shell_last_lines_long` | the Editor on a 200,000-character line stays quick |

### IDE

| Test | What it covers |
|---|---|
| `shell_ide` | IDE: run with Ctrl+R, output pane, error line and Ctrl+E, stopped loops, refused host calls, `use` of desktop files, input lines and Esc |

### Shared filesystem and fuzzing

| Test | What it covers |
|---|---|
| `shell_shared_desktops` | shared filesystem and Editor path across desktop maps |
| `shell_fuzz` | random input against the window model, checking invariants each step |
| `shell_apps_fuzz` | random Terminal commands with Files and Editor on the same filesystem |
