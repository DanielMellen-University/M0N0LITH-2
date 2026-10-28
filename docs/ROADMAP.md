# Roadmap

M0N0LITH-2 is the MONOLITH 2 desktop written in Relic. The language roadmap is in the [Relic repo](https://github.com/DanielMellen-University/Relic/blob/main/docs/ROADMAP.md). When an app here needs something the language or std does not have, that work goes to Relic, and this repo moves its pin once it lands.

## Phase 1: Move in

- [x] Shell moved from Relic with its history (`shell/wm.relic`, `shell/desktop.relic`, `shell_wm` test)
- [x] Relic pinned as a submodule; CI builds it (with the host, `-DRELIC_BUILD_HOST=ON`) and runs the tests on Linux, macOS and Windows. Pin at Relic 1.0.39 (`a729524`)

## Phase 2: Desktop shell

- [x] Window manager, taskbar and Start menu: windows raise, close, drag, resize and minimize (the _ box, or the front window's taskbar button; click the button again to restore); taskbar buttons raise, and on the 640 pixel desktop, past 13 windows the extra ones go behind a +N button with a list; Start menu launches the apps. Tests `shell_wm`, `shell_minimize` and `shell_taskbar_overflow`
- [x] Apps share one in-memory filesystem (`std/vfs` from Relic)

## Phase 3: Apps as proof

- [ ] Terminal (started: help, clear, echo, apps, date, pwd, cd, ls, cat, mkdir, touch, write, rm, mv, and `echo text > file` or `>>`; it keeps the last 200 lines of output)
- [ ] Text editor (started: edits and saves VFS files with ctrl+s, which the desktop now delivers; a file opened in Files opens in the next Editor; a big file stays quick)
- [ ] File browser (started: browses the VFS with keys or clicks; a long list follows the selected row, and opening a file selects it for the next Editor)
- [ ] Drawing app
- [ ] At least one game
- [ ] Relic IDE (planned, not started; moved here from Relic's roadmap. Needs Daniel's approval before any building starts)

Next ideas carried over from Relic (not approved yet): Terminal scrollback, Editor open by path, host-backed mounts if needed. Parked window ideas (not approved): the desktop following the real window size, and maximize.
