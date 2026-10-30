# M0N0LITH-2
M0N0LITH written in [Relic](https://github.com/DanielMellen-University/Relic).

This repo is the MONOLITH 2 desktop environment: the window manager, taskbar, Start menu and the apps, all written in [Relic](https://github.com/DanielMellen-University/Relic). The language itself (host, std, self-host) lives in the Relic repo. Language changes go there, desktop and app changes go here.

> Status: early. The shell started inside the Relic repo during its M11 milestone and moved here with its history in Relic 1.0.1. It has a window model with drag, resize and minimize, a taskbar, a Start menu, and Clicker, Notes, Terminal, Files and Editor apps. Terminal, Files and Editor share one in-memory filesystem (`std/vfs` from Relic). A Relic IDE is planned as an app here but not started; see the [roadmap](docs/ROADMAP.md).

## Layout

```
shell/
  wm.relic        desktop model: windows, taskbar, Start menu, the apps. No drawing, runs without SDL
  desktop.relic   draws the model with std/graphics and runs the event loop
tests/
  shell_wm.relic  drives wm.relic with fake clicks and keys; output must match shell_wm.out
  shell_minimize.relic  minimize and restore from the taskbar and the _ box
  shell_lifecycle.relic  window ids, focus and tab order through lifecycle changes
  shell_terminal.relic  Terminal commands: extra spaces, folders, redirects, errors
  shell_start_menu.relic  the Start button opens and closes the menu
  shell_menu_focus.relic  keyboard focus while the Start menu or the +N list is open
  shell_menu_edges.relic  Start menu row and taskbar hit boundaries
  shell_many_windows.relic  windows cascade and wrap, taskbar tabs shrink to fit
  shell_taskbar_overflow.relic  the +N button and hidden-windows list at 14 to 300 windows
  shell_overflow_edges.relic  overflow threshold and list row boundaries
  shell_overflow_lifecycle.relic  focus and stacking as windows change with the list open
  shell_overflow_all_minimized.relic  overflow tabs and restore when no window is focused
  shell_overflow_limit.relic  the last visible row and the 200-row list limit
  shell_overflow_titles.relic  empty, long and non-ASCII window names in overflow
  shell_overflow_speed.relic  the hidden-windows list stays quick at 300 windows
  shell_launch_small.relic  cascaded windows fit a small desktop
  shell_cascade_gaps.relic  a new window does not open on top of another after closes
  shell_files_click.relic  clicking rows in Files
  shell_files_boundaries.relic  root, empty folders, unusual names and reopening Files
  shell_files_long_names.relic  clipped names open the full path and deleted selections do not open replacements
  shell_files_title.relic  Files keeps the end of a long folder path in its title
  shell_files_hidden.relic  clicks below the visible Files rows do nothing
  shell_drag_resize.relic  dragging and resizing keep windows reachable
  shell_resize_offset.relic  resizing follows the point grabbed in the handle
  shell_small_apps.relic  Editor, Notes and Clicker
  shell_clicker_edges.relic  rapid input and Clicker state after reopening
  shell_app_focus.relic  Notes and Clicker state across focus and window controls
  shell_shared_desktops.relic  shared filesystem and Editor path across desktop maps
  shell_notes_resize.relic  Notes text clipping and edits across resizes
  shell_notes_input_edges.relic  single-line input and reopening Notes
  shell_editor_title.relic  Editor title keeps the file name and the status in view
  shell_editor_open_status.relic  Editor status on opening: open, new file, or why not
  shell_editor_stale.relic  Editor reports a file removed before opening
  shell_editor_edges.relic  Editor empty buffers, line edges and failed saves
  shell_editor_long_line.relic  long-line clipping, ignored movement and saving the full buffer
  shell_editor_replaced.relic  saving after a file is removed or replaced by a folder
  shell_files_stale.relic  Files when another app removed the selected file
  shell_files_ancestor.relic  Files and Terminal recover after an ancestor folder moves
  shell_files_selection.relic  Files keeps its selection across directory changes
  shell_files_changed_click.relic  Files ignores a click on rows changed since drawing
  shell_files_resize_click.relic  Files waits for a redraw after a resize before accepting a row click
  shell_input.relic  graphics events turned into keys and clicks (ctrl+s, text, the mouse)
  shell_event_keys.relic  named keys, modifiers and ignored events
  shell_altgr.relic  AltGr (Ctrl+Alt) typing is text, not Ctrl+S
  shell_escape.relic  Escape closes the Start menu or +N list before it quits
  shell_held_keys.relic  repeated key_down events from held keys, and key_up
  shell_mouse_buttons.relic  left and right mouse buttons during a drag
  shell_clip.relic  text cut to the window, Files scrolling to the selection
  shell_render_modes.relic  clipping and row selection for plain and tail apps
  shell_big_file.relic  the Editor on a file of thousands of lines stays quick
  shell_last_lines.relic  Editor line splitting at empty and trailing newline boundaries
  shell_last_lines_long.relic  the Editor on a 200,000-character line stays quick
  shell_terminal_history.relic  the Terminal keeps its last 200 lines
  shell_terminal_errors.relic  Terminal error messages (mv, mkdir, cat, paths through a file)
  shell_terminal_touch.relic  touch preserves existing entries and creates empty files
  shell_terminal_write.relic  write replaces content and handles empty text
  shell_terminal_cat_blank.relic  cat preserves blank lines in files
  shell_terminal_cat_big.relic  cat of a 100,000-line file stays quick
  shell_terminal_extra_words.relic  clear, apps, date and pwd reject extra words
  shell_terminal_dash_paths.relic  write and echo > refuse paths starting with -
  shell_terminal_why.relic  errors name the missing folder or the part that is a file
  shell_terminal_slash.relic  a path ending in / must be a folder
  shell_terminal_redirect.relic  echo redirects and missing destinations
  shell_terminal_redirect_errors.relic  failed redirects and output after clear
  shell_terminal_edges.relic  Terminal path and input boundaries
  shell_terminal_root.relic  root and normalized path operations
  shell_terminal_stale.relic  Terminal recovers when its current folder is removed
  shell_terminal_ls.relic  Terminal packs directory listings to the window width
  shell_terminal_wrap.relic  Terminal wraps long lines to the window width
  shell_terminal_frame.relic  Terminal builds only the rows that fit, matching a full wrap
  shell_help.relic  Terminal help and app names match the available commands and apps
  shell_title.relic  window titles fit beside the title bar buttons
  shell_date.relic  the date command and its UTC format
  shell_missed_release.relic  a lost mouse-up does not leave a drag running
  shell_outside_click.relic  presses outside the desktop do not hit its controls
  shell_fuzz.relic  random input against the window model, checking invariants each step
  shell_apps_fuzz.relic  random Terminal commands with Files and Editor on the same filesystem
tools/
  run_golden.cmake  golden test runner (Relic's, cut down to what these tests use)
relic/            Relic, pinned as a git submodule
docs/SHELL.md  the model, the input calls, what an app is
docs/ROADMAP.md
```

## How it depends on Relic

Relic is a git submodule at `relic/`, pinned to one commit. Building that commit gives the `relic` program, and its `std/` folder comes with it. To move to a newer Relic, check out the new commit inside `relic/`, run the tests, and commit the submodule change.

## Build and test

Needs a C compiler, a C++17 compiler (for Relic's host) and CMake 3.16 or newer.

```
git clone --recurse-submodules https://github.com/DanielMellen-University/M0N0LITH-2
cd M0N0LITH-2
cmake -S relic -B relic/build -DCMAKE_BUILD_TYPE=Release -DRELIC_BUILD_HOST=ON
cmake --build relic/build --config Release
cmake -S . -B build
ctest --test-dir build -C Release --output-on-failure
```

Already cloned without submodules? Run `git submodule update --init`.

`-DRELIC_BUILD_HOST=ON` matters. Since Relic 1.0.7 the default Relic build is C only and makes `relicc` (the compiler to C), not the `relic` program the tests and `relic check` use. The flag builds the C++ host that provides `relic`.

CMake discovers every `tests/*.relic` program and compares its standard output with the matching `.out` file (or empty output if there is no `.out`). It also runs `relic check` on both shell files. CI runs the same steps on Linux, macOS and Windows.

## Run the desktop

The desktop needs Relic built with SDL2 (`apt install libsdl2-dev`, `brew install sdl2`, or vcpkg on Windows). `-DRELIC_SDL=ON` turns on the C++ host too, so `relic` gets built:

```
cmake -S relic -B relic/build-sdl -DCMAKE_BUILD_TYPE=Release -DRELIC_SDL=ON
cmake --build relic/build-sdl --config Release
relic/build-sdl/relic shell/desktop.relic
```

With Visual Studio the program is `relic\build-sdl\Release\relic.exe`.

Click Start (again to close the menu), pick an app, click inside it or type. Drag a title bar to move a window, drag its bottom-right corner to resize. The _ box minimizes a window and the x box closes it. A taskbar button brings its window to the front, or minimizes it if it is already in front; click it again to restore. With many windows open the buttons get narrower and their names shorter, down to four letters. Up to 13 windows fit the 640 pixel bar. From 14 on, 12 keep a button (the +N button takes the room of one) and the rest go behind a +N button at the end of the bar: click it for a list of those windows and pick one to bring it to the front. The focused window always keeps its button. The list shows up to 200 hidden windows on the 640 by 480 desktop; additional hidden windows have no list row. New windows cascade from the top left again after ten, skipping a step another window is still sitting on. Escape closes the Start menu or the +N list when one is open, and otherwise quits (which loses the in-memory files).

Keys go to the window on top. Typing keeps its case and symbols (AltGr characters too), Ctrl+S saves in the Editor, Backspace works in Terminal, Notes and Editor, and Return runs a Terminal command or starts a new Editor line (Notes is one line). A click opens a Files row (a double-click counts once). Up, Down and Return move through Files, and Backspace goes up a folder with the one you were in selected (opening `..` does the same). Text that does not fit a window is cut at its edge: Terminal, Editor and Notes show their last lines, and Files follows the selected row and shortens a long folder path in its title to its end. The Terminal wraps long lines to its window; the other apps cut them.

Terminal splits commands on spaces; quotes are literal characters and do not group words, so paths containing spaces cannot be entered as one argument. Editor typing and Backspace work at the end of the text; arrow keys do not move its cursor. Its title shows the status first, then the path (the start of a long path gives way to `...` so the file name stays), then the Ctrl+S hint when there is room. The status shows the last edit, save, or file error, and a failed save leaves the buffer available for another attempt. If another app changed the file since the Editor opened or last saved it, Ctrl+S shows `changed on disk: ctrl+s again` and writes nothing; a second Ctrl+S right after overwrites. A file removed meanwhile is simply written again.

Terminal commands are `help`, `clear`, `echo`, `apps`, `date`, `pwd`, `cd`, `ls`, `cat`, `mkdir`, `touch`, `write`, `rm` and `mv`. `clear`, `apps`, `date` and `pwd` take no words. `cd` without a path goes to `/home`; `ls` without one lists the current folder. `write path text` replaces a file and adds a newline; `echo text > path` does the same, while `>>` appends. `cd`, `ls`, `cat`, `mkdir`, `touch`, `rm` and `mv` reject arguments beginning with `-`, and so do the paths of `write` and `echo >` (write `./-x` to mean such a name); `rm` removes only files or empty folders. A path ending in `/` names a folder, so `cat notes.txt/` or `rm notes.txt/` is an error and `touch new/` makes nothing. Output keeps the last 200 logical lines, which may wrap into more screen rows.

## Docs

- [How the shell is put together](docs/SHELL.md)
- [Roadmap](docs/ROADMAP.md)
- Relic language docs: [Relic/docs](https://github.com/DanielMellen-University/Relic/tree/main/docs)

## License

MIT. See [LICENSE](LICENSE).
