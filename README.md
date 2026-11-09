# M0N0LITH-2
M0N0LITH written in [Relic](https://github.com/DanielMellen-University/Relic).

This repo is the MONOLITH 2 desktop environment: the window manager, taskbar, Start menu and the apps, all written in [Relic](https://github.com/DanielMellen-University/Relic). The language itself (host, std, self-host) lives in the Relic repo. Language changes go there, desktop and app changes go here.

> Status: a 640 by 480 SDL demo, accepted on Linux on Nov 7 2026 for the behavior the walkthrough showed on all eight apps. For Snake that shown slice is launch, the board, clock-driven movement, one turn, a wall (`game over`, score 0, best 0), and `r` starting again. Pause, eating, hitting itself, and a win were not exercised in the window. Not a bootable OS or a sandbox. The shell started inside the Relic repo during its M11 milestone and moved here with its history in Relic 1.0.1. It has a window model with drag, resize and minimize, a taskbar with a +N button for windows that do not fit, a Start menu, and eight apps: Clicker, Notes, Terminal, Files, Editor, IDE, Paint and Snake. Those file apps share one in-memory filesystem (`std/vfs` from Relic), and Snake keeps its best score there. The desktop commits that filesystem, and the open windows, to a workspace directory so a new process sees them again; the crash rules and the limits are in [Workspace recovery](docs/workspace-recovery.md). The IDE is the Editor plus Ctrl+R to run a Relic program in an output pane, with input, `use` of your own files and Ctrl+E to jump to an error. The Relic pin stays at 1.0.53 (`f97ad87`). What is accepted, and what is parked, is in the [roadmap](docs/ROADMAP.md).

## Layout

```
  shell/
  wm.relic        desktop model: windows, taskbar, Start menu, the apps. No drawing, runs without SDL
  workspace.relic commits the shared vfs and the open windows to a directory of generations
  desktop.relic   draws the model with std/graphics and runs the event loop
tests/
  shell_*.relic   182 programs that drive wm.relic with fake clicks and keys; each one's output must match its .out file
tools/
  run_golden.cmake  golden test runner (Relic's, cut down to what these tests use)
relic/            Relic, pinned as a git submodule
  docs/
  SHELL.md       the model, the input calls, what an app is
  workspace-recovery.md  the store format, crash rules and fault stages
  ARCHITECTURE.md  how the desktop, Relic and the self-hosted interpreter fit together
  KEYS.md        every key and click
  BUILDING.md    build, test, run, and moving the Relic pin
  TESTING.md     how the tests work, and the list of them by area
  ROADMAP.md     what is done and what is next, with the design calls
  apps/          one page per part: WINDOWS, TASKBAR, TERMINAL, FILES, EDITOR, IDE, PAINT, SNAKE, SMALL_APPS
CONTRIBUTING.md  how changes are made here
```

## How it depends on Relic

Relic is a git submodule at `relic/`, pinned to one commit, now Relic 1.0.53 (`f97ad87`). Building that commit gives the `relic` program, and its `std/` folder comes with it. To move to a newer Relic, check out the new commit inside `relic/`, run the tests, and commit the submodule change.

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

CMake discovers every `tests/*.relic` program and compares its standard output with the matching `.out` file (or empty output if there is no `.out`). It also runs `relic check` on the three shell files, 459 tests in all. CI runs the same steps on Linux, macOS and Windows. More in [Building](docs/BUILDING.md) and [Tests](docs/TESTING.md).

## Run the desktop

The desktop needs Relic built with SDL2 (`apt install libsdl2-dev`, `brew install sdl2`, or vcpkg on Windows). `-DRELIC_SDL=ON` turns on the C++ host too, so `relic` gets built:

```
cmake -S relic -B relic/build-sdl -DCMAKE_BUILD_TYPE=Release -DRELIC_SDL=ON
cmake --build relic/build-sdl --config Release
relic/build-sdl/relic shell/desktop.relic
```

With Visual Studio the program is `relic\build-sdl\Release\relic.exe`.

Checked on Nov 7 2026 on Linux with SDL 2.30, on a real display, with the mouse and the keyboard: Start, the taskbar (including +N), drag, resize, minimize and close, and all eight apps, for the behavior named in the [roadmap](docs/ROADMAP.md). Snake moved right on the clock after one Right, Down turned it, it stopped on the bottom row with `game over: r to play` at score 0 best 0, and `r` restored `arrows or space to start` at the start cells. Pause, eating, hitting itself, and a win were not part of that GUI pass. Terminal, Files and the Editor shared one file inside the session; the IDE ran, read a line, showed an error and stopped a loop at 200,000 steps; Paint saved a picture and opened it again; quitting dropped the files. That pass had no workspace. On Nov 9 2026, on the same kind of Linux display (SDL 2.30), a later check used an isolated workspace directory: Terminal created and appended a file, Files renamed and deleted, the Editor saved, and the IDE saved with Ctrl+S and, after a new process, opened that same file and ran it. A failed save showed a notice and did not say saved. An interrupted partial and a truncated committed generation showed their notices and did not replace the last good files. Notes text and window layout are not part of that store. The Muse acceptance note is a specification and was not marked passed. macOS and Windows GUI were not tried. There is no fsync. The model tests are not that check. See [Building](docs/BUILDING.md) and [Workspace recovery](docs/workspace-recovery.md).

### Using it

- **Windows:** click Start, pick an app. Drag a title bar to move a window and its bottom-right corner to resize it; the _ box minimizes and the x box closes (Ctrl+W closes the window with focus). Ctrl+Tab and Ctrl+Shift+Tab go round the windows. New windows cascade from the top left. See [Windows and the Start menu](docs/apps/WINDOWS.md).
- **Taskbar:** a button brings its window to the front, or minimizes it if it is already there. Buttons shrink as windows open; from the 14th window on the 640 pixel bar, the extra ones go behind a +N button with a list. See [Taskbar](docs/apps/TASKBAR.md).
- **Terminal:** `help`, `clear`, `history`, `echo`, `apps`, `date`, `pwd`, `cd`, `ls`, `cat`, `head`, `tail`, `wc`, `grep`, `find`, `sort`, `uniq`, `nl`, `mkdir`, `touch`, `write`, `rm`, `mv` and `cp` on the shared files (`head` and `tail` take a count of lines), plus `echo text > path` and `>>`, and `!!` for the command before. Quotes keep the spaces in a path (`cat "my notes.txt"`), and the line has a cursor (Left, Right, Home, End, or a click). See [Terminal](docs/apps/TERMINAL.md).
- **Files:** click a row, or use Up, Down and Return; Backspace or Left goes up a folder and Right goes into one; a letter jumps to the next name starting with it; Ctrl+C copies the selected path, F2 renames, and Delete pressed twice removes a file or empty folder. Opening a file picks it for the next Editor or IDE window, or Paint for a `.paint` file. See [Files](docs/apps/FILES.md).
- **Editor:** a click, arrows, Home, End and Ctrl+arrow move; Shift or a drag selects, a double-click selects a word, Ctrl+A selects all; Ctrl+F finds and F3 finds again, Ctrl+H replaces and Ctrl+G goes to a line; Ctrl+D copies a line, Ctrl+K removes it and Ctrl+J joins the next one on, Ctrl+Up and Ctrl+Down move it, and Ctrl+] and Ctrl+[ indent it (or every selected line); Ctrl+Z undoes up to 500 edits; Ctrl+S saves and warns once if another app changed the file. See [Editor](docs/apps/EDITOR.md).
- **IDE:** the Editor plus Ctrl+R (or F5, or Ctrl+Return) to run the program in an output pane, Ctrl+E (or a click on the error) to jump to it, and an input line when the program reads one (Return sends, Escape stops). Runs stop after 200,000 steps between inputs and cannot change files on the real disk. See [IDE](docs/apps/IDE.md).
- **Paint:** drag on the canvas to draw; swatches or `1` to `8` pick a color, `e` the eraser, `+` and `-` the brush size, `f` fills, `l`, `r` and `o` draw lines, rectangles and ellipses (`R` and `O` filled), `i` picks a color from the canvas, `c` clears, Ctrl+Z undoes, Ctrl+S saves a `.paint` file and `n` saves it as a name you type. See [Paint](docs/apps/PAINT.md).
- **Snake:** arrows or W A S D start and turn, Space pauses, R plays again; it moves only while its window is focused, and the best score is saved in `/home/snake-best.txt`. See [Snake](docs/apps/SNAKE.md).
- **Clicker and Notes:** a click counter (Space or Return counts, Backspace takes one off, Delete starts again and Ctrl+Z right after brings the count back) and a one-line note with a cursor (Ctrl+C, Ctrl+X and Ctrl+V with the desktop clipboard, Ctrl+Z for the last clear). See [Clicker and Notes](docs/apps/SMALL_APPS.md).

On macOS, Cmd with a letter works as Ctrl with it. Escape closes the Start menu or the +N list, gives up a find or a name being typed, stops an IDE run that waits for input, drops a selection, and otherwise quits. All the keys are in [Keyboard and mouse](docs/KEYS.md).

## Workspace

Quitting writes the shared files and the open windows to `$HOME/.m0n0lith2/workspace` (or `$USERPROFILE/.m0n0lith2/workspace` when `HOME` is unset). Set `M0N0LITH_WORKSPACE` to another directory, or to an empty value to keep nothing between runs.

The next start opens the same windows in the same places. That includes Terminal's folder, output, and command history; the folder Files was in; Editor and IDE text, including text not yet saved with Ctrl+S; Notes' line; Clicker's count; Paint's picture, including a stroke not yet saved; and Snake's best score. Snake itself starts a new game.

A save that is cut off keeps the previous snapshot. A workspace file that is cut short, no longer matches its checksum, or is a newer version than this desktop understands is not opened as if it were whole. The screen says so. A newer version is left on disk until you release it. When an older snapshot still reads, that one comes back. When nothing does, you get the first-run files, which are `/home`, `/tmp`, and `/home/welcome.txt`, and no windows.

Not kept: undo, the clipboard, an IDE program that was still running, and where Snake was on the board. Letters you typed after the last snapshot are written when you quit, and also when a file is saved, a Terminal command finishes, or a window is moved or closed. A kill before that keeps the last snapshot, not those letters. There is no fsync, so pulling the power is not covered. The rules are in [Workspace recovery](docs/workspace-recovery.md).

## Docs

- [Architecture](docs/ARCHITECTURE.md): how the pieces fit together
- [How the shell is put together](docs/SHELL.md): the model's functions and what an app is
- [Keyboard and mouse](docs/KEYS.md)
- The parts: [Windows and the Start menu](docs/apps/WINDOWS.md), [Taskbar](docs/apps/TASKBAR.md), [Terminal](docs/apps/TERMINAL.md), [Files](docs/apps/FILES.md), [Editor](docs/apps/EDITOR.md), [IDE](docs/apps/IDE.md), [Paint](docs/apps/PAINT.md), [Snake](docs/apps/SNAKE.md), [Clicker and Notes](docs/apps/SMALL_APPS.md)
- [Building and running](docs/BUILDING.md) and [Tests](docs/TESTING.md)
- [Roadmap](docs/ROADMAP.md)
- [Contributing](CONTRIBUTING.md)
- Relic language docs: [Relic/docs](https://github.com/DanielMellen-University/Relic/tree/main/docs)

## License

MIT. See [LICENSE](LICENSE).
