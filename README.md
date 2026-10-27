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
  shell_many_windows.relic  windows cascade and wrap, taskbar tabs shrink to fit
  shell_launch_small.relic  cascaded windows fit a small desktop
  shell_files_click.relic  clicking rows in Files
  shell_files_hidden.relic  clicks below the visible Files rows do nothing
  shell_drag_resize.relic  dragging and resizing keep windows reachable
  shell_resize_offset.relic  resizing follows the point grabbed in the handle
  shell_small_apps.relic  Editor, Notes and Clicker
  shell_app_focus.relic  Notes and Clicker state across focus and window controls
  shell_notes_resize.relic  Notes text clipping and edits across resizes
  shell_editor_stale.relic  Editor reports a file removed before opening
  shell_editor_edges.relic  Editor empty buffers, line edges and failed saves
  shell_files_stale.relic  Files when another app removed the selected file
  shell_files_ancestor.relic  Files and Terminal recover after an ancestor folder moves
  shell_files_selection.relic  Files keeps its selection across directory changes
  shell_files_changed_click.relic  Files ignores a click on rows changed since drawing
  shell_files_resize_click.relic  Files waits for a redraw after a resize before accepting a row click
  shell_input.relic  graphics events turned into keys and clicks (ctrl+s, text, the mouse)
  shell_mouse_buttons.relic  left and right mouse buttons during a drag
  shell_clip.relic  text cut to the window, Files scrolling to the selection
  shell_big_file.relic  the Editor on a file of thousands of lines stays quick
  shell_terminal_history.relic  the Terminal keeps its last 200 lines
  shell_terminal_errors.relic  Terminal error messages (mv, mkdir, cat, paths through a file)
  shell_terminal_cat_blank.relic  cat preserves blank lines in files
  shell_terminal_redirect.relic  echo redirects and missing destinations
  shell_terminal_edges.relic  Terminal path and input boundaries
  shell_terminal_stale.relic  Terminal recovers when its current folder is removed
  shell_terminal_ls.relic  Terminal packs directory listings to the window width
  shell_terminal_wrap.relic  Terminal wraps long lines to the window width
  shell_help.relic  Terminal help and app names match the available commands and apps
  shell_title.relic  window titles fit beside the title bar buttons
  shell_date.relic  the date command and its UTC format
  shell_missed_release.relic  a lost mouse-up does not leave a drag running
  shell_outside_click.relic  presses outside the desktop do not hit its controls
  shell_fuzz.relic  random input against the window model, checking invariants each step
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

The tests run every `tests/shell_*.relic` program against its `.out` file, and `relic check` on every shell file. CI runs the same steps on Linux, macOS and Windows.

## Run the desktop

The desktop needs Relic built with SDL2 (`apt install libsdl2-dev`, `brew install sdl2`, or vcpkg on Windows). `-DRELIC_SDL=ON` turns on the C++ host too, so `relic` gets built:

```
cmake -S relic -B relic/build-sdl -DCMAKE_BUILD_TYPE=Release -DRELIC_SDL=ON
cmake --build relic/build-sdl --config Release
relic/build-sdl/relic shell/desktop.relic
```

With Visual Studio the program is `relic\build-sdl\Release\relic.exe`.

Click Start (again to close the menu), pick an app, click inside it or type. Drag a title bar to move a window, drag its bottom-right corner to resize. The _ box minimizes a window and the x box closes it. A taskbar button brings its window to the front, or minimizes it if it is already in front; click it again to restore. With many windows open the buttons get narrower and their names shorter, and new windows cascade from the top left again after ten. Escape quits.

Keys go to the window on top. Typing keeps its case and symbols, Ctrl+S saves in the Editor, Backspace works in Terminal, Notes and Editor, and Return runs a Terminal command or starts a new Editor line (Notes is one line). Up, Down and Return move through Files, and Backspace goes up a folder. Text that does not fit a window is cut at its edge: Terminal, Editor and Notes show their last lines, and Files follows the selected row. The Terminal wraps long lines to its window; the other apps cut them.

Terminal splits commands on spaces; quotes are literal characters and do not group words, so paths containing spaces cannot be entered as one argument. Editor typing and Backspace work at the end of the text; arrow keys do not move its cursor. Its status shows the last edit, save, or file error, and a failed save leaves the buffer available for another attempt.

## Docs

- [How the shell is put together](docs/SHELL.md)
- [Roadmap](docs/ROADMAP.md)
- Relic language docs: [Relic/docs](https://github.com/DanielMellen-University/Relic/tree/main/docs)

## License

MIT. See [LICENSE](LICENSE).
