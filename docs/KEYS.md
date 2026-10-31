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

## Terminal

| Input | What it does |
|---|---|
| Typing | adds to the command line |
| Backspace | removes the last character |
| Return | runs the command |

The commands are in [the Terminal doc](apps/TERMINAL.md).

## Files

| Input | What it does |
|---|---|
| Click a row | selects and opens it: a folder is entered, a file is set as the one the next Editor opens. The second click of a double-click is ignored |
| Up, Down | move the selection |
| Return | opens the selected row |
| Backspace | goes up a folder, with the folder you were in selected |

## Editor

| Input | What it does |
|---|---|
| Typing, Return | insert at the cursor, replacing any selection |
| Backspace | removes the selection, or the character before the cursor |
| Delete | removes the selection, or the character after the cursor |
| Left, Right, Up, Down | move the cursor; with a selection, Left and Right go to its start or end |
| Home, End | the start or end of the line |
| Ctrl+Left, Ctrl+Right | the start of the word before, or the end of the word after |
| Shift with an arrow, Home or End | selects from the cursor |
| Ctrl+A | selects everything |
| Ctrl+Z | undoes the last edit, up to 500 |
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
| Return | sends the line, and the run goes on |
| Escape | stops the run |
| Other keys | ignored until the run ends (Ctrl+S included: press Escape first) |
