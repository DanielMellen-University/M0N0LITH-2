# Terminal

A command line over the desktop's in-memory filesystem (`std/vfs` from Relic), written in Relic. It starts no host processes and never touches the real disk. Files, the Editor and the IDE work on the same filesystem, so a change made here shows there.

The filesystem starts with `/home`, `/tmp` and `/home/welcome.txt` (`vfs.new()` in Relic). It lives only while the desktop runs: quitting loses it.

## Using it

Type a command and press Return. The prompt is the current folder and `> `; a new Terminal starts in `/home`. Backspace removes the last character, and Ctrl+Backspace the last word. Up and Down go back and forth through the commands run before (the last 50; a blank line, or the same command twice in a row, is kept once at most), and Down past the newest gives back what you were typing. `!!` runs the command before again, and shows it as it runs, as in a Unix shell. Ctrl+V adds the first line of the desktop's clipboard (what the Editor or the IDE copied). Ctrl+C gives up the line being typed: it shows with `^C` after it, and is not run or kept for Up. Ctrl+L empties the output, as `clear` does, and keeps the line being typed; Ctrl+U empties the line instead. Tab completes the word being typed: the first word from the command names, a later one from the names in its folder (`cat docs/pl` looks in `docs`). One match goes in whole, a folder with `/` after it and anything else with a space; several go in as far as they agree, and a Tab that adds nothing lists them. Paths may be absolute or relative to the current folder, and `.` and `..` work.

Commands split on spaces. Quotes are ordinary characters and do not group words, so a path with a space in it cannot be given as one argument.

## Commands

| Command | What it does |
|---|---|
| `help` | lists the commands |
| `clear` | empties the output |
| `history` | the commands Up and Down go through (the last 50), numbered from the oldest; `history` itself is the last |
| `echo text` | prints the text |
| `echo text > path` | replaces the file with the text and a newline |
| `echo text >> path` | adds the text and a newline to the end of the file |
| `apps` | lists the apps the Start menu has |
| `date` | the current time in UTC, as `2026-10-27 05:12:16 UTC` |
| `pwd` | the current folder |
| `cd [path]` | changes folder; without a path, goes to `/home` |
| `ls [path]` | lists a folder (the current one without a path), folders with a `/` after them, packed into lines that fit the window; for a file, prints its name |
| `cat path` | prints a file (only its last 200 lines are kept, like any output) |
| `cp from to` | copies a file to a new name, or into `to` when it is a folder; a folder is not copied, and a file already there is not written over |
| `wc path` | the file's lines (its newlines, as Unix counts them), words and characters, then the path |
| `head path` | the first 10 lines of a file |
| `mkdir path` | makes a folder, and any missing folders above it |
| `touch path` | makes an empty file; an existing file or folder is left as it is |
| `write path text` | replaces the file with the text and a newline |
| `rm path` | removes a file or an empty folder |
| `mv from to` | renames, or moves into `to` when it is a folder |

`clear`, `history`, `apps`, `date` and `pwd` take no words, and a word too many is an error for every command (`rm a b` removes nothing).

## Rules for paths

- No command has options. `cd`, `ls`, `cat`, `head`, `wc`, `mkdir`, `touch`, `rm`, `mv` and `cp` refuse any word starting with `-`, and so do the paths of `write` and `echo >`. To name such a file, write `./-x`.
- A path ending in `/` must be a folder: `cat notes.txt/` and `rm notes.txt/` are errors, and `touch new/` makes nothing.
- Errors say which part is wrong: `not found: /home/x`, `not a folder: /home/notes.txt` when a part of the path is a file, `no folder: /home/missing` when the folder to write into is not there.
- If another app removes or moves the folder a Terminal is in, it moves up to the nearest folder that still exists.

## Output

The Terminal keeps the last 200 lines of output; older ones fall off the top. Long lines wrap to the window's width, so one kept line can take several rows. Only the rows that fit the window are built each frame, so a big `cat` stays quick.

## In the code

`terminal` in `shell/wm.relic`, with `_term_run` dispatching the commands. Tests: the `shell_terminal*` goldens, `shell_help`, `shell_date` and `shell_apps_fuzz` (see [the test list](../TESTING.md)).
