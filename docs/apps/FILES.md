# Files

A file browser over the desktop's in-memory filesystem, the same one the Terminal, the Editor and the IDE use. A new Files window opens `/home`.

## What it shows

The first line is `Files: ` and the current folder. In a narrow window the start of the path gives way to `...`, so the end of it, the folder you are in, stays readable. Below it is one row per entry, with `..` first everywhere but `/`. Folders end in `/`. The selected row starts with `> `.

A long list scrolls just far enough to keep the selected row in view; the title line always stays.

## Keys and clicks

| Input | What it does |
|---|---|
| Up, Down | move the selection |
| Return | opens the selected row |
| Backspace | goes up a folder, with the folder you were in selected, so going back down is one key |
| Click a row | selects and opens it |

Opening a folder enters it. Opening `..` is the same as Backspace. Opening a file does not show it: it sets the file the next Editor window opens.

A row opens on a single click, and the second press of a double-click is ignored, so double-clicking a folder enters it once instead of also opening whatever row lands under the pointer.

## When another app changes things

Files reads the folder again on every frame and every key, so it follows changes made in the Terminal or the Editor.

- If the selected entry is gone, the selection goes back to the first row, and a Return pressed right then opens nothing, so it never opens a row you did not pick.
- If the folder itself is removed or moved, Files goes to the nearest folder above it that still exists, with the first row selected.
- A click on a row that changed since the window was last drawn, or after a resize, is ignored until the next frame shows what is really there. Keys are not affected.

## In the code

`files_app` in `shell/wm.relic`, `_files_*`. The folder flags come from `vfs.entries` (Relic 1.0.42), so a big folder is read once per frame. Tests: the `shell_files_*` goldens (see [the test list](../TESTING.md)).
