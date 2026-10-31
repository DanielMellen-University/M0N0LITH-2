# Windows and the Start menu

The window manager part of the desktop: how windows open, stack, move, resize, minimize and close. It is all in `shell/wm.relic`, which draws nothing; `shell/desktop.relic` draws it on a 640 by 480 desktop. The API is in [How the shell is put together](../SHELL.md).

## The Start menu

The Start button sits at the left end of the taskbar. Clicking it opens the menu, and clicking it again closes it. The menu sits just above the taskbar with one row per app, top to bottom: Clicker, Notes, Terminal, Files, Editor and IDE. Picking a row launches that app. Any other click closes the menu and then does what it normally does, and so does Escape.

## Opening

A new window opens at its app's size, cascading down and to the right from the top left (24 pixels across and 20 down per step). After ten steps it starts over, and it skips a step another window is still sitting on, so a new window does not land exactly on top of an old one. On a small desktop the window is cut to fit.

| App | Size (width by height) |
|---|---|
| Clicker | 180 by 60 |
| Notes | 220 by 60 |
| Terminal | 280 by 120 |
| Files | 260 by 140 |
| Editor | 320 by 80 |
| IDE | 320 by 200 |

The height is the area under the 16 pixel title bar.

## Focus and stacking

The window on top that is not minimized has focus: its title bar is blue, and it gets the keys. Clicking anywhere in a window brings it to the front.

## Moving and resizing

- Drag the title bar to move a window. At least 40 pixels of the title bar stay on the desktop, so a window can always be grabbed again. Off the left edge, the part that stays also holds the _ and x boxes.
- Drag the 12 pixel box at the bottom-right corner to resize. Windows are at least 80 by 40, and resizing keeps the right and bottom edges inside the desktop and above the taskbar where that size allows. Resizing never moves the top-left corner.
- A press that comes after a lost mouse-up (the button let go outside the window) ends the old drag first.

## Minimizing and closing

The _ box minimizes a window: it keeps its taskbar button but is not drawn, takes no clicks or keys and never has focus. Focus goes to the next window down. Its taskbar button restores it. The x box closes the window, and the app's state goes with it. The filesystem stays, since it is shared by every app.

## Quitting

Escape quits the desktop when nothing else takes it (see [the keys](../KEYS.md)). Everything in the in-memory filesystem is lost then.

Tests: `shell_wm`, `shell_lifecycle`, `shell_minimize`, `shell_start_menu`, `shell_menu_*`, `shell_drag_resize`, `shell_resize_offset`, `shell_launch_small`, `shell_cascade_gaps`, `shell_missed_release`, `shell_outside_click`, `shell_title` and `shell_fuzz`.
