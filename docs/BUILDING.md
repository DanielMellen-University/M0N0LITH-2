# Building and running

M0N0LITH-2 has no build of its own: it is Relic source that the `relic` program runs. Building means building the pinned Relic in `relic/`, then pointing CMake at this repo to run the tests.

## What you need

- A C compiler and a C++17 compiler (the `relic` program is Relic's C++ host)
- CMake 3.16 or newer, and a build tool CMake can use (Make, Ninja, or Visual Studio)
- Git, to fetch the `relic/` submodule
- SDL2, only to open the desktop window (not for the tests)

## Build and test

```
git clone --recurse-submodules https://github.com/DanielMellen-University/M0N0LITH-2
cd M0N0LITH-2
cmake -S relic -B relic/build -DCMAKE_BUILD_TYPE=Release -DRELIC_BUILD_HOST=ON
cmake --build relic/build --config Release
cmake -S . -B build
ctest --test-dir build -C Release --output-on-failure
```

Already cloned without the submodule? Run `git submodule update --init`.

Checked on Nov 7 2026 on Linux (Clang 18.1, CMake 3.28, Make) at Relic 1.0.53 (`f97ad87`): all 183 tests pass. CI runs the same steps on Linux, macOS and Windows. Those tests do not open the SDL window.

### Why `-DRELIC_BUILD_HOST=ON`

Since Relic 1.0.7 the default Relic build is C only. It makes `relicc`, the compiler to C, and not `relic`, which runs the shell, the tests and `relic check`. The flag adds the C++ host. Without it, configuring this repo stops with `relic not found`.

### Using a `relic` built somewhere else

The top-level CMake looks for `relic` in `relic/build/Release` and `relic/build`. To use another one, pass its path: `cmake -S . -B build -DRELIC_EXE=/path/to/relic`. It should be built from the pinned commit, since the shell uses the `std/` and `selfhost/` files in `relic/`.

## Run the desktop

This part needs SDL2 (`apt install libsdl2-dev`, `brew install sdl2`, or vcpkg on Windows). Checked on Nov 7 2026 on Linux (SDL 2.30, on a real display, with the mouse and the keyboard): the steps below open the 640 by 480 desktop, and the walkthrough in the [roadmap](ROADMAP.md#accepted-nov-7-2026) was done there. macOS and Windows were not tried. The steps are the ones in the README:

```
cmake -S relic -B relic/build-sdl -DCMAKE_BUILD_TYPE=Release -DRELIC_SDL=ON
cmake --build relic/build-sdl --config Release
relic/build-sdl/relic shell/desktop.relic
```

`-DRELIC_SDL=ON` turns on the C++ host as well. With Visual Studio the program is `relic\build-sdl\Release\relic.exe`. A `relic` built without SDL prints `this relic was built without graphics; rebuild with -DRELIC_SDL=ON` and exits.

## Moving to a newer Relic

Do not move the pin as a matter of course. As of the Nov 7 2026 acceptance it stays at 1.0.53 (`f97ad87`) unless a defect in that accepted scope cannot be fixed here. When a move is actually needed:

```
cd relic
git fetch
git checkout <commit or tag>
cd ..
```

Rebuild Relic, run the tests, then commit the `relic` change with the version and what it brings, like `Pin Relic 1.0.45 (ef22fd0): ...`. Update the pin in the README and the roadmap in the same commit.
