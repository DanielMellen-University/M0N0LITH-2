# Roadmap

M0N0LITH-2 is the MONOLITH 2 desktop written in Relic. The language roadmap is in the [Relic repo](https://github.com/DanielMellen-University/Relic/blob/main/docs/ROADMAP.md). When an app here needs something the language or std does not have, that work goes to Relic, and this repo moves its pin once it lands.

## Phase 1: Move in

- [x] Shell moved from Relic with its history (`shell/wm.relic`, `shell/desktop.relic`, `shell_wm` test)
- [x] Relic pinned as a submodule; CI builds it (with the host, `-DRELIC_BUILD_HOST=ON`) and runs the tests on Linux, macOS and Windows. Pin at Relic 1.0.45 (`ef22fd0`)

## Phase 2: Desktop shell

- [x] Window manager, taskbar and Start menu: windows raise, close, drag, resize and minimize (the _ box, or the front window's taskbar button; click the button again to restore); taskbar buttons raise, and on the 640 pixel desktop, past 13 windows the extra ones go behind a +N button with a list; Start menu launches the apps. Tests `shell_wm`, `shell_minimize` and `shell_taskbar_overflow`
- [x] Apps share one in-memory filesystem (`std/vfs` from Relic)

## Phase 3: Apps as proof

- [ ] Terminal (started: help, clear, echo, apps, date, pwd, cd, ls, cat, mkdir, touch, write, rm, mv, and `echo text > file` or `>>`; it keeps the last 200 lines of output)
- [ ] Text editor (started: edits and saves VFS files with ctrl+s, which the desktop now delivers, and warns first when another app changed the file; ctrl+z undo; Delete; arrows, home/end and ctrl+arrow word jumps move the cursor; shift+arrows and ctrl+a select; a file opened in Files opens in the next Editor; a big file stays quick)
- [ ] File browser (started: browses the VFS with keys or clicks; a long list follows the selected row, and opening a file selects it for the next Editor)
- [ ] Drawing app
- [ ] At least one game
- [ ] Relic IDE (started Oct 30 2026, Daniel approved with "your design calls": the Editor on a .relic file, Ctrl+R runs the text, saved or not, with an output pane under it, an error shows as `line L: message` and Ctrl+E puts the cursor on that line). Design calls:
  - It is the Editor's state and keys plus two keys, in `wm.relic` like the other apps, so editing, undo, selection and Ctrl+S work the same.
  - A run uses Relic's own `selfhost/interp` inside the desktop, not a separate process (the host has no way to start one). Relic 1.0.44 added the hooks: output goes to a list, a run stops after 200,000 steps (a loop that never ends cannot hang the desktop; `try` does not catch the stop), and named host built-ins are refused.
  - Refused: exit, sleep, graphics and clipboard (the desktop owns the window), and writing, removing, renaming or making files on the real disk. Reading real files and `use std/...` (from Relic's std) work.
  - `use` of the user's own files (approved Oct 30): any other `use` reads the module from the desktop's files, relative to the file being edited, as last saved (only the edited file runs unsaved). A missing module is the usual "cannot find module" error; an error inside one shows its path and line (Relic 1.0.45, `rt.load`).
  - Input (approved Oct 30): `os.read_line` and `os.prompt` pause the run, and the pane ends in an input line with the prompt. While it waits, typing goes to that line (Backspace, Space), Return sends it and the run goes on, Esc stops the run, and Ctrl+R starts it again; the other Editor keys wait until the run ends. The pane shows each prompt and line sent, as a terminal would. The 200,000 steps start again after each line sent, so a program may wait for input as long as it likes but cannot spin between inputs (Relic 1.0.45, `rt.input` and `interp.resume`). Esc goes to the IDE only while a run waits; otherwise it closes menus or quits the desktop as before.
  - The pane shows the last 6 lines (5 and the input line while waiting) and keeps 200. An error inside a std module shows that module's file and line, and Ctrl+E does nothing then.
  - Not yet: programs that draw, clicking an error to jump, and a run that goes on in the background while not waiting for input.

Next ideas carried over from Relic (not approved yet): Terminal scrollback, Editor open by path, host-backed mounts if needed. Parked window ideas (not approved): the desktop following the real window size, and maximize.
