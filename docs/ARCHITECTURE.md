# Architecture

M0N0LITH-2 is two Relic files and a pinned Relic. This page is the map; [How the shell is put together](SHELL.md) has the details of the model's functions.

```
SDL2 window
   |  graphics events
   v
shell/desktop.relic   opens the window, runs the event loop, draws
   |  wm.handle(d, e), wm.dismiss(d)  ->  boxes and visible_lines back
   v
shell/wm.relic        the model and the six apps
   |  use std/vfs, std/strings, std/paths ...  (the shared files and helpers)
   |  use ../relic/selfhost/lexer, parser, interp  (the IDE's runs)
   v
relic/                the pinned Relic: the relic program, std/ and selfhost/
```

## The two files

- `shell/wm.relic` is the whole desktop as data: the windows, the taskbar, the Start menu, and the six apps. It never draws. Input goes in as `click`, `motion`, `release`, `key` and `dismiss`, or as raw graphics events through `handle`. Output comes out as boxes (`tab_box`, `close_box`, `menu_item_box` and so on) and the text rows each window shows (`visible_lines`). This is what the tests drive, with no SDL and no window.
- `shell/desktop.relic` is about a hundred lines. It opens a 640 by 480 window with `std/graphics`, reads events, hands them to `wm.handle` (Escape goes to `wm.dismiss`, and quits when nothing took it), and draws the model about 60 times a second. It is the only file that needs SDL, and no test runs it; `relic check` covers it.

## Apps

An app is a map of functions (`init`, `lines`, `on_click`, `on_key` and some optional ones), and a window holds the app and its own `state` map. The model calls the app; the app never calls the model. So an app has no idea where it is drawn, and the same app can have any number of windows.

## Shared state

Two things in `wm.relic` are module-level, so every window and even every desktop map in the same process shares them:

- `_shell_fs`, one in-memory filesystem from Relic's `std/vfs`. Terminal, Files, the Editor and the IDE all read and write it, so a change in one shows in the others, and each app checks again what is there rather than trusting what it saw last frame. Nothing reaches the real disk.
- `_shell_open`, the path the next Editor or IDE window opens. Files sets it.

## The IDE's runs

The IDE runs Relic programs with Relic's own self-hosted interpreter: `wm.relic` loads `relic/selfhost/lexer`, `parser` and `interp` with `use`, so the program runs inside the desktop process, between two frames. The runtime map has hooks that the IDE fills in (Relic 1.0.44 and 1.0.45): `out` collects printed lines, `steps` caps the work per run or per input line, `denied` names host built-ins to refuse, `load` reads `use`d modules from the shared filesystem, and `input` with `interp.resume` lets a run stop for a line of input and continue after it. See [the IDE](apps/IDE.md).

## Relic

`relic/` is a git submodule pinned to one Relic commit (1.0.45 now). The `relic` program built from it runs everything, and the shell's `use std/...` and `use ../relic/selfhost/...` lines read files from that checkout. When the shell needs something the language or std lacks, the change goes into Relic first, and this repo moves its pin after it lands. See [Building](BUILDING.md#moving-to-a-newer-relic).
