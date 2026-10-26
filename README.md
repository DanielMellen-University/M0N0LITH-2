# M0N0LITH-2
M0N0LITH written in relic.

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
tools/
  run_golden.cmake  golden test runner (copied from Relic)
relic/            Relic, pinned as a git submodule
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

The tests run `shell_wm`, `shell_minimize` and `relic check` on every shell file. CI runs the same steps on Linux, macOS and Windows.

## Run the desktop

The desktop needs Relic built with SDL2 (`apt install libsdl2-dev`, `brew install sdl2`, or vcpkg on Windows). `-DRELIC_SDL=ON` turns on the C++ host too, so `relic` gets built:

```
cmake -S relic -B relic/build-sdl -DCMAKE_BUILD_TYPE=Release -DRELIC_SDL=ON
cmake --build relic/build-sdl --config Release
relic/build-sdl/relic shell/desktop.relic
```

With Visual Studio the program is `relic\build-sdl\Release\relic.exe`.

Click Start, pick an app, click inside it or type. Drag a title bar to move a window, drag its bottom-right corner to resize. The _ box minimizes a window and the x box closes it. A taskbar button brings its window to the front, or minimizes it if it is already in front; click it again to restore. Escape quits.

## Docs

- [Roadmap](docs/ROADMAP.md)
- Relic language docs: [Relic/docs](https://github.com/DanielMellen-University/Relic/tree/main/docs)

## License

MIT. See [LICENSE](LICENSE).
