# M0N0LITH-2
M0N0LITH written in relic.

This repo is the MONOLITH 2 desktop environment: the window manager, taskbar, Start menu and the apps, all written in [Relic](https://github.com/DanielMellen-University/Relic). The language itself (host, std, self-host) lives in the Relic repo. Language changes go there, desktop and app changes go here.

> Status: early. The shell started inside the Relic repo during its M11 milestone and moved here with its history in Relic 1.0.1. It has a window model with drag and resize, a taskbar, a Start menu, and Clicker, Notes, Terminal, Files and Editor apps. Terminal, Files and Editor share one in-memory filesystem (`std/vfs` from Relic).

## Layout

```
shell/
  wm.relic        desktop model: windows, taskbar, Start menu, the apps. No drawing, runs without SDL
  desktop.relic   draws the model with std/graphics and runs the event loop
tests/
  shell_wm.relic  drives wm.relic with fake clicks and keys; output must match shell_wm.out
tools/
  run_golden.cmake  golden test runner (copied from Relic)
relic/            Relic, pinned as a git submodule
docs/ROADMAP.md
```

## How it depends on Relic

Relic is a git submodule at `relic/`, pinned to one commit. Building that commit gives the `relic` program, and its `std/` folder comes with it. To move to a newer Relic, check out the new commit inside `relic/`, run the tests, and commit the submodule change.

## Build and test

Needs a C++17 compiler and CMake 3.16 or newer (for Relic).

```
git clone --recurse-submodules https://github.com/DanielMellen-University/M0N0LITH-2
cd M0N0LITH-2
cmake -S relic -B relic/build -DCMAKE_BUILD_TYPE=Release
cmake --build relic/build --config Release
cmake -S . -B build
ctest --test-dir build -C Release --output-on-failure
```

Already cloned without submodules? Run `git submodule update --init`.

The tests run `shell_wm` and `relic check` on every shell file. CI runs the same steps on Linux, macOS and Windows.

## Run the desktop

The desktop needs Relic built with SDL2:

```
cmake -S relic -B relic/build-sdl -DRELIC_SDL=ON
cmake --build relic/build-sdl
relic/build-sdl/relic shell/desktop.relic
```

Click Start, pick an app, click inside it or type. Drag a title bar to move a window, drag its bottom-right corner to resize. Escape quits.

## Docs

- [Roadmap](docs/ROADMAP.md)
- Relic language docs: [Relic/docs](https://github.com/DanielMellen-University/Relic/tree/main/docs)

## License

MIT. See [LICENSE](LICENSE).
