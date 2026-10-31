# Taskbar

The 24 pixel bar along the bottom of the desktop: the Start button at the left, then one button per window, in the order the windows were opened. The functions behind it are in [How the shell is put together](../SHELL.md#the-taskbar).

## Window buttons

- Clicking a button brings its window to the front. If that window is already in front, the click minimizes it, and clicking again restores it.
- The focused window's button is drawn lighter than the others.
- Buttons are 90 pixels wide while they all fit, then shrink together down to 40 pixels, which is four letters of the window's name. A name that does not fit its button is cut.

## The +N button

When even 40 pixel buttons would run off the bar, the extra windows go behind a `+N` button at the right end, where N is how many have no button of their own. On the 640 pixel desktop that happens from the 14th window on, and then 12 windows keep a button, since the +N button takes the room of one.

- The windows that keep a button are the first ones opened. The focused window always keeps one: if it is not among them, it takes the place of the last.
- Clicking `+N` opens a list of the other windows, stacked upward from the bar at the right edge. A new column starts to the left when the list reaches the top of the desktop. Picking a row restores that window and brings it to the front, so it gets a button.
- The list shows as many rows as fit across the desktop: 200 on 640 by 480. Windows past that have no row.
- Any other click, or Escape, closes the list. Closing windows until they all fit removes the button and the list.
- The button is 40 pixels wide, and wider from 1,000 windows on so its label still fits.
- On a bar too narrow for one 40 pixel button beside `+N` (under about 150 pixels), the one shown button gets whatever room is left and never overlaps `+N`.

Tests: `shell_taskbar_*`, `shell_overflow_*`, `shell_many_windows` and `shell_menu_edges`.
