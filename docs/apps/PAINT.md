# Paint

A small paint app. Its window is 256 by 190: a status line, a row of color swatches, and a canvas of 60 by 36 cells, each 4 pixels square.

The status line reads `Paint [status] color size file`, for example `Paint [edited] red 2 picture.paint`. The status is `new file`, `open`, `edited`, `saved`, `not a picture`, or why a save failed.

## Drawing

- Press on the canvas and drag to draw with the brush. A quick drag leaves no gaps: every cell on the way from one point to the next gets the brush.
- Dragging off the canvas pauses the stroke, and it goes on from where the pointer comes back. A press outside the canvas never draws, even if the drag then enters it.
- The brush is a square of 1 to 4 cells (`+` or `=` bigger, `-` smaller), centered on the cell under the pointer.
- Swatches, left to right: black, red, orange, yellow, green, blue, purple, brown, and the eraser (white) last. Click one, or press `1` to `8` for the colors and `e` or `0` for the eraser. The chosen one has a blue frame.
- `c` clears the canvas. Ctrl+Z undoes the last stroke or clear, up to 20.

## Files

A picture is a text file in the desktop's shared files: a line `paint 60 36`, then 36 lines of 60 digits, one per cell (`0` white, `1` to `8` the colors in swatch order).

- A new Paint window opens the file last opened in Files when its name ends in `.paint`, else `/home/picture.paint` (a new file until the first save).
- Ctrl+S saves. A file that is not a picture (`not a picture` when it opened) is never written over: Ctrl+S says `not saved: not a picture`.
- A picture of another size opens with the part that fits; unknown digits are white.

## Design calls

- Cells, not pixels: a 60 by 36 grid keeps the file small and readable and the drawing quick on the VM (the desktop draws a row's run of one color as one box).
- The app draws through two hooks any app can use: `paint(state)` gives colored boxes, and `on_drag(state, x, y)` gets the pointer while the button is held after a press inside the window (see [SHELL.md](../SHELL.md#an-app)).
- Not yet: fill, lines and shapes, more colors, a bigger or resizable canvas, and picking a file name to save as.

Tests: `shell_paint`.
