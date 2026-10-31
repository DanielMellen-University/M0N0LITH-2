# Snake

The game. Its window is 210 by 170: a score line, a help line, and a board of 24 by 16 cells, each 8 pixels square.

## Playing

- An arrow key or W, A, S, D starts the game and turns the snake. It cannot turn straight back. Two turns pressed within one step both count, one step each, so a quick U-turn works. Capital letters (Shift or Caps Lock) work the same.
- The snake moves one cell a step: every 150 ms at first, 5 ms quicker for each food eaten, down to 70 ms.
- Eating the red food makes it one cell longer. New food goes on a free cell.
- Running into a wall or into itself ends the game, with the snake left where it was. Filling the whole board wins.
- Space pauses and goes on (it also starts a new game). R starts again after a game ends.
- The best score is saved in `/home/snake-best.txt` in the desktop's files (one whole number) whenever it is beaten, and read when a Snake window opens and when a new game starts, so two Snake windows share it. A file that holds no whole number counts as 0. Like all the desktop's files, it is lost when the desktop quits.

The score line reads `Snake  score N  best M`. The help line says what to press next.

## Design calls

- The game moves only on the clock of its own window: `desktop.relic` calls `wm.tick(d, graphics.ticks())` every frame, and only the focused window's app gets it. Another window on top, or a minimized Snake, pauses it without a key.
- After a pause or a slow frame the beat starts again instead of catching up, so the snake never jumps several cells at once.
- Food comes from a small seeded generator mixed with the clock when a game starts, so a test can replay a game exactly.
- Walls end the game (no wrapping), which keeps the rules plain.
- Not yet: levels or obstacles, and sound.

Tests: `shell_snake`.
