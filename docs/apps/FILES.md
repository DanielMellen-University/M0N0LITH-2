# Files

A file browser over the desktop's in-memory filesystem, the same one the Terminal, the Editor and the IDE use. A new Files window opens `/home`.

## What it shows

The first line is `Files: ` and the current folder. In a narrow window the start of the path gives way to `...`, so the end of it, the folder you are in, stays readable. Below it is one row per entry, with `..` first everywhere but `/`. Folders end in `/`. The selected row starts with `> `.

A long list scrolls just far enough to keep the selected row in view; the title line always stays.

## Keys and clicks

| Input | What it does |
|---|---|
| Up, Down | move the selection |
| Home, End | the first or last row; with Ctrl the same, as in the Editor |
| Page Up, Page Down | as many rows as the window shows less one, so one row stays in view; they stop at the first and last row |
| A letter or digit | the next name that starts with it, in any case, going round to the top (never `..`) |
| Return | opens the selected row |
| F2 | renames the selected row: the title reads `rename: name_` with its name to edit (Backspace, Ctrl+Backspace, Ctrl+U, Ctrl+V), Return renames it in the same folder and Esc gives up. Not over a name that is there (`already there: name`), and not to a name with a `/` |
| Backspace or Left | goes up a folder, with the folder you were in selected, so going back down is one key (Right) |
| Delete | asks first, in the title (`Delete notes.txt? Delete again`); a second Delete removes the file, or the folder if it is empty (a folder with anything in it says `not empty`), and any other key gives up. `..` cannot be removed. After a removal the selection stays on its line, now the next name (the one before when it was the last) |
| Ctrl+C | copies the selected row's full path, such as `/home/docs/plan.txt`, to the desktop's clipboard, to paste into the Terminal or Notes; on `..` it copies nothing |
| Right | goes into the selected folder, as in a folder tree; on a file or `..` it does nothing |
| Click a row | selects and opens it |

Opening a folder enters it. Opening `..` is the same as Backspace. Opening a file does not show it: it sets the file the next Editor window opens. Renaming that file, or its folder, here or with `mv` in the Terminal, takes it along.

A row opens on a single click, and the second press of a double-click is ignored, so double-clicking a folder enters it once instead of also opening whatever row lands under the pointer.

## When another app changes things

Files reads the folder again on every frame and every key, so it follows changes made in the Terminal or the Editor.

- If the selected entry is gone, the selection goes back to the first row, and a Return pressed right then opens nothing, so it never opens a row you did not pick.
- If the folder itself is removed or moved, Files goes to the nearest folder above it that still exists, with the first row selected.
- A click on a row that changed since the window was last drawn, or after a resize, is ignored until the next frame shows what is really there. Keys are not affected.

## In the code

`files_app` in `shell/wm.relic`, `_files_*`. The folder flags come from `vfs.entries` (Relic 1.0.42), so a big folder is read once per frame. Left, Right and Ctrl+C reuse `_files_up`, `_files_open` and `_files_full`, so they behave as Backspace, Return and the Editor's path do. Tests: the `shell_files_*` goldens (see [the test list](../TESTING.md)).
