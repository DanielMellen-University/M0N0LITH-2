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
| Backspace | removes the selection, or the character before the cursor; in a line's leading spaces, back to the multiple of 4 before (one Tab) |
| Delete | removes the selection, or the character after the cursor |
| Left, Right, Up, Down | move the cursor. Up and Down keep the column, or go to the end of a shorter line. With a selection, Left and Right go to its start or end |
| Home, End | Home goes to the first character after the line's leading spaces, and from there to the very start; End goes to the end of the line |
| Ctrl+Left, Ctrl+Right | the start of the word before the cursor, or the end of the word after it. Letters, digits, `_` and anything past ASCII count as word characters |
| Ctrl+Home, Ctrl+End | the start or end of the file |
| Page Up, Page Down | as many lines up or down as the window shows less one, so one stays in view; with Shift they select |
| Ctrl+Backspace, Ctrl+Delete | removes the selection, or back to where Ctrl+Left goes, or on to where Ctrl+Right goes |
| Shift with an arrow, Home, End, Page Up or Page Down | selects from the cursor |
| Ctrl+Shift+Left, Ctrl+Shift+Right | selects to where Ctrl+Left or Ctrl+Right would go |
| Ctrl+Shift+Home, Ctrl+Shift+End | selects to the start or the end of the file |
| Return | a new line that starts with the same spaces as the one before (up to the cursor); in the IDE, 4 more after a line that opens a block (`if`, `else`, `for`, `while`, `fun` without `=`, `try`, `catch`) |
| Tab | spaces to the next multiple of 4 columns (Relic's indent), over any selection; never a tab character |
| Shift+Tab, Ctrl+[ | takes the line's leading spaces back to the multiple of 4 before; the cursor stays on its character. With a selection, every line it is on, in one undo step, the lines staying selected |
| Ctrl+] | puts 4 spaces at the start of the line, wherever the cursor is in it; the cursor stays on its character. With a selection, every line it is on but empty ones, in one undo step, the lines staying selected |
| Ctrl+A | selects everything |
| Ctrl+L | selects the cursor's line with its newline; pressed again it takes in the next line too |
| Ctrl+D | puts a copy of the cursor's line, or of every line the selection is on (not a line it only ends at the start of, as after Ctrl+L), under it; the cursor goes to the same column in the copy. One Ctrl+Z takes it back |
| Ctrl+J | joins the next line onto the cursor's: the newline and the next line's leading spaces become one space (none when either side is empty), and the cursor goes to the join |
| Ctrl+Up, Ctrl+Down | moves the cursor's line above the line before it, or below the line after it, the cursor going with it (Alt+Up and Alt+Down in VS Code); with a selection, the lines it is on move together and stay selected; one Ctrl+Z puts it back |
| Ctrl+K | removes the cursor's line, or every line the selection is on (as for Ctrl+D), with its newline (the last line takes the newline before it); the cursor goes to the start of what came after. One Ctrl+Z puts it back |
| Esc | drops the selection; with none, Esc quits the desktop as usual |
| Ctrl+C, Ctrl+X | copies, or cuts, the selection to the desktop's clipboard (nothing without a selection) |
| Ctrl+V | pastes the clipboard at the cursor, over any selection; a cut and a paste are one undo step each |
| Ctrl+Z | undoes the last edit |
| Ctrl+Y | does again what Ctrl+Z undid, until the next edit |
| Ctrl+S | saves |
| Ctrl+F | finds: type the text (the title shows `find: text_`), and Return selects the next place it is after the cursor, going round to the start; `(not found)` when it is nowhere. With no text yet, Return waits for some. A text too long for the title shows its end, `find: ...end_`. Case counts. With a selection on one line, Ctrl+F starts with it as the text, and typing replaces it (Backspace edits it). Backspace, Ctrl+Backspace, Ctrl+U and Ctrl+V edit the text; Esc, or any other key, stops finding, and that key then does what it always does; so does a click |
| Ctrl+H | replaces: type the text (`replace: text_`), Return, then what goes in its place (`with: text_`), and Return again replaces every place it is, in one undo step; the title says `replaced N`, or `not found: text`. The cursor goes to the start. As with Ctrl+F, a selection on one line is the text to start with, and typing replaces it. Esc, another key or a click gives up |
| Ctrl+G | goes to a line: type its number (`line: N_`, digits only), and Return puts the cursor at its start, or on the last line when the number is past the end; the title then says `line N`. Esc, another key or a click gives up |
| F3, Shift+F3 | the last text found again: the next place, or with Shift the one before (both go round); `not found: text` when it is gone |

On macOS, Cmd with a letter works as Ctrl with it.

A click on a line of text puts the cursor at the character clicked, or at the end of the line when the click is past it, and drops the selection. Pressing and dragging selects from where you pressed to the pointer; above or below the text it goes to the first or last line shown. A double-click selects the word under the pointer (word characters as for Ctrl+Left and Ctrl+Right), and a triple-click the whole line with its newline, as Ctrl+L does. A click on the title line does nothing. In the IDE a click on the output pane does nothing, and nor does any click while a run waits for input.

The selection is drawn as a light blue box behind its text.

## Undo

Each typed character, Backspace, Delete, new line, or replaced or removed selection is one step. The last 500 steps are kept, and saving does not clear them. A step stores only the part that changed, not a copy of the file, so undo stays cheap on a big file.

## Saving and other apps

Ctrl+S writes the whole buffer to the file. If the save fails, the status says why and the buffer stays as it was, so you can try again.

The Terminal, Files and the IDE can change the same file while the Editor has it open. The Editor remembers the file as it last read or saved it. If the file on disk is different when you press Ctrl+S, it writes nothing and shows `changed on disk: ctrl+s again`. A second Ctrl+S right after overwrites; any other key in between cancels that. A file removed meanwhile is simply written again.

## Long text

Only the lines that fit the window are built each frame, so a file of thousands of lines, or a single line of 200,000 characters, stays quick. A line wider than the window is cut at its edge; the line with the cursor scrolls sideways to keep the cursor in view. The cursor is drawn as `_`.

## In the code

`editor` in `shell/wm.relic`, `_editor_*`. The IDE reuses all of it. The line keys (Ctrl+L, Ctrl+D, Ctrl+K, Ctrl+J, Ctrl+Up and Ctrl+Down) go through `_editor_change` like typing, so each is one undo step. Tests: the `shell_editor_*` goldens, `shell_small_apps`, `shell_big_file` and `shell_last_lines*` (see [the test list](../TESTING.md)).

The clipboard is the desktop's own, one for all its windows, not the system's: what the Editor or the IDE copies, Notes, the Terminal and an IDE run waiting for input can paste (its first line).
