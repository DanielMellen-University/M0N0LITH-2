# M0N0LITH-2
M0N0LITH written in [Relic](https://github.com/DanielMellen-University/Relic).

This repo is the MONOLITH 2 desktop environment: the window manager, taskbar, Start menu and the apps, all written in [Relic](https://github.com/DanielMellen-University/Relic). The language itself (host, std, self-host) lives in the Relic repo. Language changes go there, desktop and app changes go here.

> Status: early. The shell started inside the Relic repo during its M11 milestone and moved here with its history in Relic 1.0.1. It has a window model with drag, resize and minimize, a taskbar with a +N button for windows that do not fit, a Start menu, and six apps: Clicker, Notes, Terminal, Files, Editor and IDE. Terminal, Files, the Editor and the IDE share one in-memory filesystem (`std/vfs` from Relic). The IDE is the Editor plus Ctrl+R to run a Relic program in an output pane, with input, `use` of your own files and Ctrl+E to jump to an error. Next up is in the [roadmap](docs/ROADMAP.md).

## Layout

```
shell/
  wm.relic        desktop model: windows, taskbar, Start menu, the apps. No drawing, runs without SDL
  desktop.relic   draws the model with std/graphics and runs the event loop
tests/
  shell_*.relic   87 programs that drive wm.relic with fake clicks and keys; each one's output must match its .out file
tools/
  run_golden.cmake  golden test runner (Relic's, cut down to what these tests use)
relic/            Relic, pinned as a git submodule
docs/
  SHELL.md       the model, the input calls, what an app is
  ARCHITECTURE.md  how the desktop, Relic and the self-hosted interpreter fit together
  KEYS.md        every key and click
  BUILDING.md    build, test, run, and moving the Relic pin
  TESTING.md     how the tests work, and the list of them by area
  ROADMAP.md     what is done and what is next, with the design calls
  apps/          one page per part: WINDOWS, TASKBAR, TERMINAL, FILES, EDITOR, IDE, SMALL_APPS
CONTRIBUTING.md  how changes are made here
```

## How it depends on Relic

Relic is a git submodule at `relic/`, pinned to one commit, now Relic 1.0.45 (`ef22fd0`). Building that commit gives the `relic` program, and its `std/` folder comes with it. To move to a newer Relic, check out the new commit inside `relic/`, run the tests, and commit the submodule change.

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

Keys go to the window on top. Typing keeps its case and symbols (AltGr characters too), Ctrl+S saves in the Editor (Cmd+S on macOS: Cmd with a letter works as Ctrl with it), Backspace works in Terminal, Notes and Editor, and Return runs a Terminal command or starts a new Editor line (Notes is one line). A click opens a Files row (a double-click counts once). Up, Down and Return move through Files, and Backspace goes up a folder with the one you were in selected (opening `..` does the same). Text that does not fit a window is cut at its edge: Terminal and Notes show their last lines, the Editor the lines up to the one with its cursor (its last lines while the cursor is at the end), and Files follows the selected row and shortens a long folder path in its title to its end. The Terminal wraps long lines to its window; the other apps cut them.

Terminal splits commands on spaces; quotes are literal characters and do not group words, so paths containing spaces cannot be entered as one argument. In the Editor, Shift with the arrow keys selects from the cursor and Ctrl+A selects everything; typing replaces the selection and Backspace removes it. The arrow keys, Home and End move its cursor, and Ctrl+Left and Ctrl+Right jump by words; typing, Backspace, Delete and Return work at the cursor, and Delete also removes a selection. Ctrl+Z undoes the last edit (a character, a Backspace, a new line or a replaced selection), up to 500 steps back. Its title shows the status first, then the path (the start of a long path gives way to `...` so the file name stays), then the Ctrl+S hint when there is room. The status shows the last edit, save, or file error, and a failed save leaves the buffer available for another attempt. If another app changed the file since the Editor opened or last saved it, Ctrl+S shows `changed on disk: ctrl+s again` and writes nothing; a second Ctrl+S right after overwrites. A file removed meanwhile is simply written again.

Terminal commands are `help`, `clear`, `echo`, `apps`, `date`, `pwd`, `cd`, `ls`, `cat`, `mkdir`, `touch`, `write`, `rm` and `mv`. `clear`, `apps`, `date` and `pwd` take no words. `cd` without a path goes to `/home`; `ls` without one lists the current folder. `write path text` replaces a file and adds a newline; `echo text > path` does the same, while `>>` appends. `cd`, `ls`, `cat`, `mkdir`, `touch`, `rm` and `mv` reject arguments beginning with `-`, and so do the paths of `write` and `echo >` (write `./-x` to mean such a name); `rm` removes only files or empty folders. A path ending in `/` names a folder, so `cat notes.txt/` or `rm notes.txt/` is an error and `touch new/` makes nothing. Output keeps the last 200 logical lines, which may wrap into more screen rows.

## Docs

- [How the shell is put together](docs/SHELL.md)
- [Roadmap](docs/ROADMAP.md)
- Relic language docs: [Relic/docs](https://github.com/DanielMellen-University/Relic/tree/main/docs)

## License

MIT. See [LICENSE](LICENSE).
