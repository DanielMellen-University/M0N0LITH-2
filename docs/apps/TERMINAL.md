# Terminal

A command line over the desktop's in-memory filesystem (`std/vfs` from Relic), written in Relic. It starts no host processes and never touches the real disk. Files, the Editor and the IDE work on the same filesystem, so a change made here shows there.

The filesystem starts with `/home`, `/tmp` and `/home/welcome.txt` (`vfs.new()` in Relic). It lives only while the desktop runs: quitting loses it.

## Using it

Type a command and press Return. The prompt is the current folder and `> `; a new Terminal starts in `/home`. Left, Right, Home and End move the cursor (`_`) in the line, Ctrl+Left and Ctrl+Right by words as in the Editor, Ctrl+A and Ctrl+E go to the start and the end as in a shell, Ctrl+K removes the rest of the line, Delete removes the character after it and Ctrl+Delete on to the end of the next word, and typing, Backspace, Tab and Ctrl+V work where it is; A click on the line puts the cursor at the character clicked. Return runs the whole line. Backspace removes the character before the cursor, and Ctrl+Backspace the last word. Up and Down go back and forth through the commands run before (the last 50; a blank line, or the same command twice in a row, is kept once at most), and Down past the newest gives back what you were typing. `!!` runs the command before again, and shows it as it runs, as in a Unix shell; `!N` runs command N as `history` numbers it (`!3: not in history` when there is none). Ctrl+V adds the first line of the desktop's clipboard (what the Editor or the IDE copied). Ctrl+C gives up the line being typed: it shows with `^C` after it, and is not run or kept for Up. Ctrl+L empties the output, as `clear` does, and keeps the line being typed; Ctrl+U removes the line before the cursor instead (all of it at the end). Tab completes the word being typed: the first word from the command names, a later one from the names in its folder (`cat docs/pl` looks in `docs`). One match goes in whole, a folder with `/` after it and anything else with a space; several go in as far as they agree, and a Tab that adds nothing lists them. A name with a space goes in quotes (a folder's quote stays open, so Tab can go on inside it), and a word begun with a quote completes from inside it. Paths may be absolute or relative to the current folder, and `.` and `..` work.

Commands split on spaces. A part in double or single quotes is one word with its spaces kept and the quotes dropped, so `cat "my notes.txt"` reads one file; the other kind of quote inside is plain text (`echo "it's"`). A quote opens only at the start of a word, so `echo don't` prints `don't`. A quote left open runs nothing and says `no closing "`. A quoted `>` or `>>` is text for `echo`, not a redirect. `ls` and `find` show a name with a space in quotes (single ones if it has a `"`), so it can be typed back as it shows. Ctrl+V of a path with a space that is there, such as one Files' Ctrl+C copied, puts it in quotes at the start of a word.

## Commands

| Command | What it does |
|---|---|
| `help` | lists the commands, and how `>`, `>>`, quotes, `!!` and `!N` work |
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
| `cat path...` | prints a file, or several one after another (only the last 200 lines are kept, like any output); a missing one is an error and the rest still print |
| `cp from to` | copies a file to a new name, or into `to` when it is a folder; a folder is not copied, and a file already there is not written over |
| `wc path` | the file's lines (its newlines, as Unix counts them), words and characters, then the path (in quotes when it has a space, as `ls` shows names) |
| `head path [lines]` | the first 10 lines of a file, or as many as `lines` says (a whole number in digits; 0 prints nothing) |
| `tail path [lines]` | the last 10 lines of a file, or as many as `lines` says |
| `find text` | every file and folder under the current folder whose own name has `text` in it, as paths from there (folders with a `/` after them), in the order `ls` gives, each folder followed by what is in it |
| `grep text path` | the lines of a file that have `text` in them: plain text, not a pattern, and case counts; quote it to look for words with spaces (`grep "old pond" poem.txt`) |
| `sort path` | the lines of a file in order, by character (capitals before small letters); the file is not changed |
| `uniq path` | the lines of a file, leaving out a line the same as the one just before it (so a repeat further on stays, as in Unix) |
| `nl path` | the lines of a file, each after its number from 1, as `history` numbers commands |
| `mkdir path...` | makes each folder, and any missing folders above it |
| `touch path...` | makes each an empty file; an existing file or folder is left as it is |
| `write path text` | replaces the file with the text and a newline |
| `rm path...` | removes each file or empty folder; an error for one (not found, not empty) does not stop the rest |
| `mv from to` | renames, or moves into `to` when it is a folder; the file the next Editor opens goes along with it, and so does the Terminal when it is in the folder moved |

`clear`, `history`, `apps`, `date` and `pwd` take no words, and a word too many is an error for every command but `cat`, `rm`, `mkdir` and `touch`, which take several paths and do each in turn (`rm a b` removes both); `head` and `tail` take a count after the path.

## Rules for paths

- No command has options. `cd`, `ls`, `cat`, `head`, `tail`, `wc`, `grep`, `sort`, `uniq`, `nl`, `mkdir`, `touch`, `rm`, `mv` and `cp` refuse any word starting with `-`, and so do the paths of `write` and `echo >`. To name such a file, write `./-x`.
- A path ending in `/` must be a folder: `cat notes.txt/` and `rm notes.txt/` are errors, and `touch new/` makes nothing.
- Errors say which part is wrong: `not found: /home/x`, `not a folder: /home/notes.txt` when a part of the path is a file, `no folder: /home/missing` when the folder to write into is not there.
- If another app removes or moves the folder a Terminal is in, it moves up to the nearest folder that still exists.

## Output

The Terminal keeps the last 200 lines of output; older ones fall off the top. Scrollback is parked with the Nov 7 2026 acceptance, not scheduled. Long lines wrap to the window's width, so one kept line can take several rows. Only the rows that fit the window are built each frame, so a big `cat` stays quick.

## In the code

`terminal` in `shell/wm.relic`, with `_term_run` dispatching the commands to `_term_*` helpers (one each for `ls`, `cat`, `head`, `tail`, `grep`, `sort`, `uniq`, `nl`, `wc`, `cp` and the rest) and `_term_key` handling the keys, `!!` included. Tests: the `shell_terminal*` goldens, `shell_help`, `shell_date` and `shell_apps_fuzz` (see [the test list](../TESTING.md)).
