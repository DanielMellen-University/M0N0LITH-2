# M0N0LITH-2
M0N0LITH written in [Relic](https://github.com/DanielMellen-University/Relic).

This repo is the MONOLITH 2 desktop environment: the window manager, taskbar, Start menu and the apps, all written in [Relic](https://github.com/DanielMellen-University/Relic). The language itself (host, std, self-host) lives in the Relic repo. Language changes go there, desktop and app changes go here.

> Status: early. The shell started inside the Relic repo during its M11 milestone and moved here with its history in Relic 1.0.1. It has a window model with drag, resize and minimize, a taskbar with a +N button for windows that do not fit, a Start menu, and eight apps: Clicker, Notes, Terminal, Files, Editor, IDE, Paint and Snake. Terminal, Files, the Editor, the IDE and Paint share one in-memory filesystem (`std/vfs` from Relic), and Snake keeps its best score there. The IDE is the Editor plus Ctrl+R to run a Relic program in an output pane, with input, `use` of your own files and Ctrl+E to jump to an error. Next up is in the [roadmap](docs/ROADMAP.md).

## Layout

```
shell/
  wm.relic        desktop model: windows, taskbar, Start menu, the apps. No drawing, runs without SDL
  desktop.relic   draws the model with std/graphics and runs the event loop
tests/
  shell_*.relic   101 programs that drive wm.relic with fake clicks and keys; each one's output must match its .out file
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
  apps/          one page per part: WINDOWS, TASKBAR, TERMINAL, FILES, EDITOR, IDE, PAINT, SNAKE, SMALL_APPS
CONTRIBUTING.md  how changes are made here
```

## How it depends on Relic

Relic is a git submodule at `relic/`, pinned to one commit, now Relic 1.0.51 (`ab69da4`). Building that commit gives the `relic` program, and its `std/` folder comes with it. To move to a newer Relic, check out the new commit inside `relic/`, run the tests, and commit the submodule change.

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

CMake discovers every `tests/*.relic` program and compares its standard output with the matching `.out` file (or empty output if there is no `.out`). It also runs `relic check` on both shell files, 103 tests in all. CI runs the same steps on Linux, macOS and Windows. More in [Building](docs/BUILDING.md) and [Tests](docs/TESTING.md).

## Run the desktop

The desktop needs Relic built with SDL2 (`apt install libsdl2-dev`, `brew install sdl2`, or vcpkg on Windows). `-DRELIC_SDL=ON` turns on the C++ host too, so `relic` gets built:

```
cmake -S relic -B relic/build-sdl -DCMAKE_BUILD_TYPE=Release -DRELIC_SDL=ON
cmake --build relic/build-sdl --config Release
relic/build-sdl/relic shell/desktop.relic
```

With Visual Studio the program is `relic\build-sdl\Release\relic.exe`.

The machine these docs were last checked on has no SDL2, so these run steps were not re-run then (the build and test steps were). See [Building](docs/BUILDING.md).

### Using it

- **Windows:** click Start, pick an app. Drag a title bar to move a window and its bottom-right corner to resize it; the _ box minimizes and the x box closes (Ctrl+W closes the window with focus). Ctrl+Tab and Ctrl+Shift+Tab go round the windows. New windows cascade from the top left. See [Windows and the Start menu](docs/apps/WINDOWS.md).
- **Taskbar:** a button brings its window to the front, or minimizes it if it is already there. Buttons shrink as windows open; from the 14th window on the 640 pixel bar, the extra ones go behind a +N button with a list. See [Taskbar](docs/apps/TASKBAR.md).
- **Terminal:** `help`, `clear`, `history`, `echo`, `apps`, `date`, `pwd`, `cd`, `ls`, `cat`, `head`, `tail`, `wc`, `grep`, `find`, `sort`, `uniq`, `nl`, `mkdir`, `touch`, `write`, `rm`, `mv` and `cp` on the shared files (`head` and `tail` take a count of lines), plus `echo text > path` and `>>`, and `!!` for the command before. See [Terminal](docs/apps/TERMINAL.md).
- **Files:** click a row, or use Up, Down and Return; Backspace or Left goes up a folder and Right goes into one; a letter jumps to the next name starting with it; Ctrl+C copies the selected path, and Delete pressed twice removes a file or empty folder. Opening a file picks it for the next Editor or IDE window, or Paint for a `.paint` file. See [Files](docs/apps/FILES.md).
- **Editor:** a click, arrows, Home, End and Ctrl+arrow move; Shift selects, Ctrl+A selects all; Ctrl+D copies a line, Ctrl+K removes it and Ctrl+J joins the next one on; Ctrl+Z undoes up to 500 edits; Ctrl+S saves and warns once if another app changed the file. See [Editor](docs/apps/EDITOR.md).
- **IDE:** the Editor plus Ctrl+R (or F5, or Ctrl+Return) to run the program in an output pane, Ctrl+E to jump to an error, and an input line when the program reads one (Return sends, Escape stops). Runs stop after 200,000 steps between inputs and cannot change files on the real disk. See [IDE](docs/apps/IDE.md).
- **Paint:** drag on the canvas to draw; swatches or `1` to `8` pick a color, `e` the eraser, `+` and `-` the brush size, `f` fills, `l`, `r` and `o` draw lines, rectangles and ellipses (`R` and `O` filled), `i` picks a color from the canvas, `c` clears, Ctrl+Z undoes, Ctrl+S saves a `.paint` file and `n` saves it as a name you type. See [Paint](docs/apps/PAINT.md).
- **Snake:** arrows or W A S D start and turn, Space pauses, R plays again; it moves only while its window is focused, and the best score is saved in `/home/snake-best.txt`. See [Snake](docs/apps/SNAKE.md).
- **Clicker and Notes:** a click counter (Space or Return counts, Backspace takes one off, Delete starts again and Ctrl+Z right after brings the count back) and a one-line note (Ctrl+C, Ctrl+X and Ctrl+V with the desktop clipboard, Ctrl+Z for the last clear). See [Clicker and Notes](docs/apps/SMALL_APPS.md).

On macOS, Cmd with a letter works as Ctrl with it. Escape closes the Start menu or the +N list, stops an IDE run that waits for input, and otherwise quits, which loses the in-memory files. All the keys are in [Keyboard and mouse](docs/KEYS.md).

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
