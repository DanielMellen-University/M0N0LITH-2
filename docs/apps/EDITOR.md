# Editor

A text editor for files in the desktop's in-memory filesystem. A new Editor window opens the file last opened in Files, or `/home/welcome.txt` if none was.

## The title line

`Editor [status] path  (ctrl+s save)`. The status comes first because a window is often too narrow for the whole line. When it does not fit, the Ctrl+S hint goes first, then the start of the path gives way to `...` so the file name stays in view.

The status is one of:

- `open`, `new file` (the file does not exist yet; Ctrl+S makes it), or why it cannot be opened or saved, such as `is a folder`, `not a folder: /home/notes.txt` or `no folder: /home/missing`
- `edited`, `undone` or `saved` after those actions
- `changed on disk: ctrl+s again` (see below)

## Keys

| Input | What it does |
|---|---|
| Typing, Return | insert at the cursor, replacing any selection |
| Backspace | removes the selection, or the character before the cursor |
| Delete | removes the selection, or the character after the cursor |
| Left, Right, Up, Down | move the cursor. Up and Down keep the column, or go to the end of a shorter line. With a selection, Left and Right go to its start or end |
| Home, End | the start or end of the line |
| Ctrl+Left, Ctrl+Right | the start of the word before the cursor, or the end of the word after it. Letters, digits, `_` and anything past ASCII count as word characters |
| Shift with an arrow, Home or End | selects from the cursor |
| Ctrl+A | selects everything |
| Ctrl+Z | undoes the last edit |
| Ctrl+S | saves |

On macOS, Cmd with a letter works as Ctrl with it. Clicks inside the window do not move the cursor.

The selection is drawn as a light blue box behind its text.

## Undo

Each typed character, Backspace, Delete, new line, or replaced or removed selection is one step. The last 500 steps are kept, and saving does not clear them. A step stores only the part that changed, not a copy of the file, so undo stays cheap on a big file.

## Saving and other apps

Ctrl+S writes the whole buffer to the file. If the save fails, the status says why and the buffer stays as it was, so you can try again.

The Terminal, Files and the IDE can change the same file while the Editor has it open. The Editor remembers the file as it last read or saved it. If the file on disk is different when you press Ctrl+S, it writes nothing and shows `changed on disk: ctrl+s again`. A second Ctrl+S right after overwrites; any other key in between cancels that. A file removed meanwhile is simply written again.

## Long text

Only the lines that fit the window are built each frame, so a file of thousands of lines, or a single line of 200,000 characters, stays quick. A line wider than the window is cut at its edge; the line with the cursor scrolls sideways to keep the cursor in view. The cursor is drawn as `_`.

## In the code

`editor` in `shell/wm.relic`, `_editor_*`. The IDE reuses all of it. Tests: the `shell_editor_*` goldens, `shell_small_apps`, `shell_big_file` and `shell_last_lines*` (see [the test list](../TESTING.md)).
