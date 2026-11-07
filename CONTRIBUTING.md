# Contributing

These are the habits the project's history follows.

## Where a change goes

- Desktop, window manager and app changes go here, in `shell/`.
- Language, std and self-hosted interpreter changes go to [Relic](https://github.com/DanielMellen-University/Relic). Landing there does not move the pin in this repo.
- New apps and features follow [the roadmap](docs/ROADMAP.md). The Nov 7 2026 acceptance is the scope. Items listed there as parked stay parked. Do not move the Relic pin unless a defect in that scope cannot be fixed on `f97ad87`. If that move is required, it is its own commit (see [Building](docs/BUILDING.md#moving-to-a-newer-relic)).

## Before a commit

1. Build Relic and run the tests ([Building](docs/BUILDING.md)). All of them pass, `check_shell` included.
2. A behavior change comes with a test in `tests/` that shows it, or a changed `.out` file whose diff you have read ([Tests](docs/TESTING.md)).
3. Keep `wm.relic` free of drawing, so the tests stay runnable without SDL. Only `desktop.relic` uses `std/graphics`.
4. Update the docs the change touches: the README, the page in `docs/apps/`, [the keys](docs/KEYS.md), the test list in [Tests](docs/TESTING.md), and the roadmap.

## Commits

- One topic per commit, with a message that says what changed and, when it is not obvious, why: `Files: the second click of a double-click is ignored`, `Pin Relic 1.0.45 (ef22fd0): ...`.
- Push to `main` and check that CI passes on Linux, macOS and Windows. No force pushes; fix forward with a new commit.
- No secrets, tokens or machine-specific paths in the repo.

## Writing docs

Short, plain sentences, in the same voice as the rest. Say what the code does now, checked against the code, and mark anything not tried (for example the SDL steps on a machine without SDL). Use the app names as the Start menu shows them (Clicker, Notes, Terminal, Files, Editor, IDE), and "taskbar button" for what the code calls a tab.
