# Keyboard and mouse reference

Every key and click the desktop and its apps act on, checked against `shell/wm.relic` and `shell/desktop.relic`. Keys go to the window on top. On macOS, Cmd with a letter works as Ctrl with it (Cmd+S, Cmd+Z, Cmd+Y, Cmd+A, Cmd+C, Cmd+X, Cmd+V, Cmd+R, Cmd+E, Cmd+L, which selects a line in the Editor and clears the Terminal, Cmd+U, Cmd+D, Cmd+K, Cmd+J, and Cmd+W and Cmd+M for the window with focus). With any other key (Home, Backspace, Tab, the arrows) it is Ctrl on every system: only Cmd with a letter is read as Ctrl. AltGr (Ctrl+Alt) characters are typed as text, not read as shortcuts.

## Desktop

| Input | What it does |
|---|---|
| Click Start | opens the Start menu, or closes it |
| Click a Start menu row | launches that app |
| Up, Down, Return (menu open) | move the marked row of the Start menu, going round at the ends, and launch it; the first row is marked each time it opens |
| Drag a title bar | moves the window |
| Drag the bottom-right corner | resizes the window |
| Click the _ box | minimizes the window |
| Click the x box | closes the window |
| Click a taskbar button | brings its window to the front, or minimizes it if it is already in front |
| Click the +N button | opens or closes the list of windows without a taskbar button |
| Click a row of the +N list | restores that window and brings it to the front |
| Ctrl+Tab | brings the lowest window that is not minimized to the front; again and again goes round them |
| Ctrl+Shift+Tab | the other way: the window with focus goes to the bottom, so it undoes a Ctrl+Tab |
| Ctrl+W | closes the window with focus, as its x box does |
| Ctrl+M | minimizes the window with focus, as its _ box does |
| Ctrl+1 to Ctrl+9 | brings the window of that taskbar button (counting in the order opened) to the front, restoring it if minimized |
| Escape | closes the Start menu or the +N list; else gives up what the window on top is asking for (a find, replace or line number in the Editor or the IDE, a name in Paint or Files), stops an IDE run that waits for input, or drops a selection in the Editor or the IDE; else quits the desktop (the in-memory files are lost). A held, repeating Escape does not quit |

## Clicker

| Input | What it does |
|---|---|
| Click inside, Space, Return or + (or =) | adds one to the count |
| Backspace or - | takes one off, not below 0 |
| Delete | sets the count back to 0 |
| Ctrl+Z | right after a Delete, brings the count back (once) |
| Ctrl+C | copies the count, as a number, to the clipboard |

## Notes

| Input | What it does |
|---|---|
| Typing | adds to the one line of text at the cursor |
| Left, Right, Home, End, Ctrl+Left, Ctrl+Right | move the cursor |
| Delete | removes the character after the cursor |
| Ctrl+Delete | removes the word after the cursor |
| Backspace | removes the character before the cursor |
| Ctrl+C, Ctrl+X | copies, or cuts, the whole line to the clipboard |
| Ctrl+Backspace | removes the word before the cursor |
| Ctrl+U | empties the line |
| Ctrl+Z | brings back the line from before the last Ctrl+U, Ctrl+X, Ctrl+Backspace, Ctrl+Delete or Ctrl+V; again puts it back |
| Ctrl+V | adds the first line of the clipboard; a path with a space that is there goes in quotes |

## Terminal

| Input | What it does |
|---|---|
| Typing | adds to the command line at the cursor |
| Click the line being typed | puts the cursor there |
| Left, Right, Home, End | move the cursor in the line (Ctrl+A and Ctrl+E too, as in a shell) |
| Ctrl+K | removes the rest of the line after the cursor |
| Ctrl+Left, Ctrl+Right | move the cursor by words |
| Delete | removes the character after the cursor |
| Ctrl+Delete | removes on to the end of the next word |
| Backspace | removes the character before the cursor |
| Return | runs the command; `!!` runs the one before again, `!N` command N of `history` |
| Ctrl+V | adds the first line of the clipboard |
| Up, Down | the command before, or after, from the last 50 run; Down past the newest gives back the line being typed |
| Ctrl+C | gives up the line: shown with ^C, not run |
| Ctrl+Backspace | removes the last word |
| Ctrl+L | empties the output, like `clear` |
| Ctrl+U | empties the line being typed |
| Tab | completes a command name, or a file or folder name (in quotes when it has a space); lists the choices when it cannot add more |

The commands are in [the Terminal doc](apps/TERMINAL.md).

## Files

| Input | What it does |
|---|---|
| Click a row | selects and opens it: a folder is entered, a file is set as the one the next Editor opens. The second click of a double-click is ignored |
| Up, Down | move the selection |
| Home, End (or with Ctrl) | the first or last row |
| Page Up, Page Down | a window of rows up or down, stopping at the ends |
| A letter or digit | the next name that starts with it, any case, going round |
| Return | opens the selected row |
| F2 | renames the selected row: type the name, Return renames, Esc gives up |
| Backspace or Left | goes up a folder, with the folder you were in selected |
| Right | goes into the selected folder (a file or `..` stays put) |
| Ctrl+C | copies the selected row's full path to the clipboard (not for `..`) |
| Delete, Delete | removes the selected file or empty folder: the first asks in the title, the second removes, any other key gives up |

## Editor

| Input | What it does |
|---|---|
| Click a line of text | puts the cursor there (at the line's end past it) and drops the selection |
| Press and drag over text | selects from the press to the pointer |
| Double-click, triple-click | selects the word, or the line with its newline |
| Typing, Return | insert at the cursor, replacing any selection |
| Backspace | removes the selection, or the character before the cursor; in a line's leading spaces, back to the multiple of 4 before (one Tab) |
| Delete | removes the selection, or the character after the cursor |
| Left, Right, Up, Down | move the cursor; with a selection, Left and Right go to its start or end |
| Home, End | the first character after the leading spaces (Home again: the very start), or the end of the line |
| Ctrl+Left, Ctrl+Right | the start of the word before, or the end of the word after |
| Ctrl+Home, Ctrl+End | the start or end of the file |
| Page Up, Page Down | a window of lines less one, up or down |
| Ctrl+Backspace, Ctrl+Delete | removes the selection, or the word before or after the cursor |
| Shift with an arrow, Home, End, Page Up or Page Down | selects from the cursor |
| Ctrl+Shift+Left, Ctrl+Shift+Right, Ctrl+Shift+Home, Ctrl+Shift+End | selects to the word before or after, or to the start or end of the file |
| Return | a new line with the same leading spaces (in the IDE 4 more after `if`, `else`, `for`, `while`, `fun`, `try`, `catch`) |
| Tab | spaces to the next multiple of 4 columns, over any selection |
| Shift+Tab, Ctrl+[ | takes one indent (to the multiple of 4 before) off the line |
| Ctrl+] | puts one indent (4 spaces) at the start of the line, wherever the cursor is |
| Ctrl+A | selects everything |
| Ctrl+L | selects the line with its newline; again adds the next line |
| Ctrl+D | puts a copy of the line, or of the selected lines, under it |
| Ctrl+K | removes the line, or the selected lines, with the newline |
| Ctrl+J | joins the next line onto this one with a space |
| Ctrl+Up, Ctrl+Down | moves the line above the one before, or below the one after |
| Ctrl+C, Ctrl+X | copies, or cuts, the selection to the desktop's clipboard (shared by all windows, not the system's) |
| Ctrl+V | pastes it, over any selection |
| Ctrl+Z | undoes the last edit (a cut or a paste is one), up to 500 |
| Ctrl+Y | redoes what Ctrl+Z undid, newest first; a new edit ends it |
| Ctrl+S | saves. If another app changed the file since it was opened or saved, the first Ctrl+S warns and writes nothing, and a second one right after overwrites |
| Ctrl+F | find: type the text, Return selects the next match after the cursor (going round to the start); Esc or another key stops. With a selection on one line it starts with that, and typing replaces it |
| F3, Shift+F3 | finds the last text again, the next or the one before |
| Ctrl+G | go to a line: type its number, Return |
| Ctrl+H | replace: the text, Return, what goes in its place, Return replaces every one (one undo step); starts with a selection on one line, as Ctrl+F does |

## IDE

Every Editor key, plus:

| Input | What it does |
|---|---|
| Ctrl+R, F5, Ctrl+Return | runs the program in the buffer, saved or not. While a run waits for input, it starts the run again |
| Ctrl+E, or a click on the error in the pane | puts the cursor at the start of the line of the last error in this file |
| Ctrl+/ | comments the line out with `# ` after its leading spaces, or takes the `#` back off; with a selection, every line it is on |

While a run waits for input:

| Input | What it does |
|---|---|
| Typing, Space, Backspace | edit the input line at its cursor |
| Left, Right, Home, End | move the cursor in the input line |
| Ctrl+Left, Ctrl+Right | move it by words |
| Delete, Ctrl+Delete | remove the character, or the word, after the cursor |
| Ctrl+Backspace | removes the word before the cursor |
| Ctrl+U | empties the input line |
| Ctrl+V | adds the first line of the clipboard |
| Return | sends the line, and the run goes on |
| Escape, Ctrl+C | stops the run |
| Ctrl+S | saves the program; the run keeps waiting |
| Other keys | ignored until the run ends |

## Paint

| Input | What it does |
|---|---|
| Press and drag on the canvas | draws with the brush; off the canvas the stroke pauses |
| Click a swatch | picks that color, or the eraser (the last one) |
| 1 to 8 | black, red, orange, yellow, green, blue, purple, brown |
| e or 0 | the eraser |
| x | swaps to the color picked before, and back (the eraser at first) |
| + or = or ], - or [ | brush size 1 to 4 cells |
| f, b | the fill tool (a click fills the area of one color), and back to the brush |
| i | the color picker: the next click on the canvas takes its color, then the tool before comes back |
| l, r, o | the line, rectangle and ellipse tools: press at one end or corner, drag to the other |
| R, O | the filled rectangle and filled ellipse |
| c | clears the canvas |
| Ctrl+Z | undoes the last stroke, fill, shape or clear, up to 20 |
| Ctrl+Y | redoes what Ctrl+Z undid, until the next change |
| Ctrl+S | saves the picture |
| n | save as: type a name on the status line, Return saves, Backspace deletes, Ctrl+Backspace a word, Ctrl+U all of it, Ctrl+V pastes, Esc gives up |

With Shift or Caps Lock a letter works as its small one (`F` is the fill tool), except `R` and `O`, which are the filled shapes.

## Snake

| Input | What it does |
|---|---|
| Arrows or W, A, S, D | start the game and turn the snake (not straight back) |
| Space or P | pauses and goes on; also starts a game |
| R or Return | plays again after a game ends |
| N | a new game at any time, giving up the one going on |

The letters work the same with Shift or Caps Lock.
