# Paint

A small paint app. Its window is 256 by 190: a status line, a row of color swatches, and a canvas of 60 by 36 cells, each 4 pixels square.

The status line reads `Paint [status] color tool file` (the tool is the brush size, `fill`, `line 2`, `rect 2`, `oval 2`, `filled rect` or `filled oval`), for example `Paint [edited] red 2 picture.paint`. The status is `new file`, `open`, `edited`, `saved`, `not a picture`, or why a save failed.

## Drawing

- Press on the canvas and drag to draw with the brush. A quick drag leaves no gaps: every cell on the way from one point to the next gets the brush.
- Dragging off the canvas pauses the stroke, and it goes on from where the pointer comes back. A press outside the canvas never draws, even if the drag then enters it.
- The brush is a square of 1 to 4 cells (`+`, `=` or `]` bigger, `-` or `[` smaller), centered on the cell under the pointer.
- Swatches, left to right: black, red, orange, yellow, green, blue, purple, brown, and the eraser (white) last. Click one, or press `1` to `8` for the colors and `e` or `0` for the eraser. The chosen one has a blue frame.
- `f` picks the fill tool: a click fills the area of one color under it with the chosen color (cells joined side by side, not corner to corner). `b` goes back to the brush. The status line shows `fill` in place of the brush size.
- `x` swaps to the color chosen before and back again, so two colors, or a color and the eraser, are one key apart. A new Paint starts with the eraser as the one before.
- `i` is the color picker: the next click on the canvas takes the color of that cell (white is the eraser) and the tool before comes back. It changes no cell, so it is not an undo step. The status line shows `pick` until then.
- `l` picks the line tool and `r` the rectangle tool. Press at one end (or corner) and drag to the other: until the button is let go the shape follows the pointer, drawn over the picture as it was at the press. Past the canvas, the far end stays on the nearest edge. Lines and rectangle outlines use the brush size, and the status line shows `line 2` or `rect 2`.
- `o` picks the ellipse tool: the ellipse that fits the box from the press to the pointer, as an outline in the brush size (`oval 2`). Shift with the letter fills the shape: `R` a filled rectangle and `O` a filled ellipse (`filled rect`, `filled oval`; the brush size does not matter). They follow the drag and undo the same way.
- With Shift or Caps Lock a letter key works as its small one (`F` the fill tool, `E` the eraser), except `R` and `O`.
- `c` clears the canvas. Ctrl+Z undoes the last stroke, fill, shape or clear, up to 20, and Ctrl+Y puts back what it took, newest first, until the next change. A fill that would change nothing is not an undo step. A key pressed while the button is still held ends the stroke or shape, so a Ctrl+Z in the middle of one is not drawn over by the next move.

## Files

A picture is a text file in the desktop's shared files: a line `paint 60 36`, then 36 lines of 60 digits, one per cell (`0` white, `1` to `8` the colors in swatch order).

- A new Paint window opens the file last opened in Files when its name ends in `.paint`, else `/home/picture.paint` (a new file until the first save).
- Ctrl+S saves. `n` saves as: the status line reads `Paint save as: name_`, letters and digits type the name (not tools), Backspace deletes, Return saves and Esc gives up. A plain name is a file in `/home`, with `.paint` added when it has no ending; a name starting with `/` is a whole path. The window then works on the new file. Save as never writes over a folder or a file that is not a picture (`not saved: notes.txt is not a picture`), an empty name is `not saved: no name`, and when the save fails (a folder that is not there) the window keeps its old file.
- A file that is not a picture (`not a picture` when it opened) is never written over: Ctrl+S says `not saved: not a picture`.
- A picture of another size opens with the part that fits; unknown digits are white.

## Design calls

- Cells, not pixels: a 60 by 36 grid keeps the file small and readable and the drawing quick on the VM (the desktop draws a row's run of one color as one box).
- The app draws through two hooks any app can use: `paint(state)` gives colored boxes, and `on_drag(state, x, y)` gets the pointer while the button is held after a press inside the window (see [SHELL.md](../SHELL.md#an-app)).
- Not yet: more colors, and a bigger or resizable canvas.

Tests: `shell_paint`, and `shell_events_fuzz` for random input.
