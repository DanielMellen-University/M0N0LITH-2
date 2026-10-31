# Keyboard and mouse reference

Every key and click the desktop and its apps act on, checked against `shell/wm.relic` and `shell/desktop.relic`. Keys go to the window on top. On macOS, Cmd with a letter works as Ctrl with it (Cmd+S, Cmd+Z, Cmd+A, Cmd+R, Cmd+E). AltGr (Ctrl+Alt) characters are typed as text, not read as shortcuts.

## Desktop

| Input | What it does |
|---|---|
| Click Start | opens the Start menu, or closes it |
| Click a Start menu row | launches that app |
| Drag a title bar | moves the window |
| Drag the bottom-right corner | resizes the window |
| Click the _ box | minimizes the window |
| Click the x box | closes the window |
| Click a taskbar button | brings its window to the front, or minimizes it if it is already in front |
| Click the +N button | opens or closes the list of windows without a taskbar button |
| Click a row of the +N list | restores that window and brings it to the front |
| Escape | closes the Start menu or the +N list; else stops an IDE run that waits for input; else quits the desktop (the in-memory files are lost). A held, repeating Escape does not quit |

## Clicker

| Input | What it does |
|---|---|
| Click inside, or Space | adds one to the count |

## Notes

| Input | What it does |
|---|---|
| Typing | adds to the one line of text |
| Backspace | removes the last character |
| Ctrl+C, Ctrl+X | copies, or cuts, the whole line to the clipboard |
| Ctrl+Backspace | removes the last word |
| Ctrl+V | adds the first line of the clipboard |

## Terminal

| Input | What it does |
|---|---|
| Typing | adds to the command line |
| Backspace | removes the last character |
| Return | runs the command |
| Ctrl+V | adds the first line of the clipboard |
| Up, Down | the command before, or after, from the last 50 run; Down past the newest gives back the line being typed |
| Ctrl+C | gives up the line: shown with ^C, not run |
| Ctrl+Backspace | removes the last word |
| Ctrl+L | empties the output, like `clear` |

The commands are in [the Terminal doc](apps/TERMINAL.md).

## Files

| Input | What it does |
|---|---|
| Click a row | selects and opens it: a folder is entered, a file is set as the one the next Editor opens. The second click of a double-click is ignored |
| Up, Down | move the selection |
| Home, End | the first or last row |
| Page Up, Page Down | a window of rows up or down, stopping at the ends |
| A letter or digit | the next name that starts with it, any case, going round |
| Return | opens the selected row |
| Backspace | goes up a folder, with the folder you were in selected |

## Editor

| Input | What it does |
|---|---|
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
| Return | a new line with the same leading spaces (in the IDE 4 more after `if`, `else`, `for`, `while`, `fun`, `try`, `catch`) |
| Tab | spaces to the next multiple of 4 columns, over any selection |
| Shift+Tab | takes one indent (to the multiple of 4 before) off the line |
| Ctrl+A | selects everything |
| Ctrl+C, Ctrl+X | copies, or cuts, the selection to the desktop's clipboard (shared by all windows, not the system's) |
| Ctrl+V | pastes it, over any selection |
| Ctrl+Z | undoes the last edit (a cut or a paste is one), up to 500 |
| Ctrl+Y | redoes what Ctrl+Z undid, newest first; a new edit ends it |
| Ctrl+S | saves. If another app changed the file since it was opened or saved, the first Ctrl+S warns and writes nothing, and a second one right after overwrites |

## IDE

Every Editor key, plus:

| Input | What it does |
|---|---|
| Ctrl+R | runs the program in the buffer, saved or not. While a run waits for input, it starts the run again |
| Ctrl+E | puts the cursor at the start of the line of the last error in this file |

While a run waits for input:

| Input | What it does |
|---|---|
| Typing, Space, Backspace | edit the input line |
| Ctrl+Backspace | removes the last word of the input line |
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
| + or =, - | brush size 1 to 4 cells |
| f, b | the fill tool (a click fills the area of one color), and back to the brush |
| l, r, o | the line, rectangle and ellipse tools: press at one end or corner, drag to the other |
| R, O | the filled rectangle and filled ellipse |
| c | clears the canvas |
| Ctrl+Z | undoes the last stroke, fill, shape or clear, up to 20 |
| Ctrl+Y | redoes what Ctrl+Z undid, until the next change |
| Ctrl+S | saves the picture |
| n | save as: type a name on the status line, Return saves, Backspace deletes, Esc gives up |

With Shift or Caps Lock a letter works as its small one (`F` is the fill tool), except `R` and `O`, which are the filled shapes.

## Snake

| Input | What it does |
|---|---|
| Arrows or W, A, S, D | start the game and turn the snake (not straight back) |
| Space or P | pauses and goes on; also starts a game |
| R | plays again after a game ends |

The letters work the same with Shift or Caps Lock.
