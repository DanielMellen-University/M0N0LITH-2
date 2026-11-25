# Terminal

A command line over the desktop's filesystem (`std/vfs` from Relic), written in Relic. It starts no host processes. A path in a command is a vfs path, not a host path. Files, the Editor and the IDE work on the same filesystem, so a change made here shows there.

The filesystem starts with `/home`, `/tmp` and `/home/welcome.txt` (`vfs.new()` in Relic). The desktop commits it to the workspace after each command that changes a file or folder, and a later process reads that back. With no workspace open (the tests, unless one opens one), quitting still drops it. See [Workspace recovery](../workspace-recovery.md).

## Using it

Type a command and press Return. The prompt is the current folder and `> `; a new Terminal starts in `/home`. Left, Right, Home and End move the cursor (`_`) in the line, Ctrl+Left and Ctrl+Right by words as in the Editor, Ctrl+A and Ctrl+E go to the start and the end as in a shell, Ctrl+K removes the rest of the line, Delete removes the character after it and Ctrl+Delete on to the end of the next word, and typing, Backspace, Tab and Ctrl+V work where it is; A click on the line puts the cursor at the character clicked. Return runs the whole line. Backspace removes the character before the cursor, and Ctrl+Backspace the last word. Up and Down go back and forth through the commands run before (the last 50; a blank line, or the same command twice in a row, is kept once at most), and Down past the newest gives back what you were typing. `!!` runs the command before again, and shows it as it runs, as in a Unix shell; `!N` runs command N as `history` numbers it (`!3: not in history` when there is none). `!text` runs the newest remembered command that starts with that text (`!ec` runs the newest `echo ...`), and says `not in history` when none does. A line of digits stays `!N`, so a number too long to be one is still an unknown command. A miss is not kept. Ctrl+V adds the first line of the desktop's clipboard (what the Editor or the IDE copied). Ctrl+C gives up the line being typed: it shows with `^C` after it, and is not run or kept for Up. Ctrl+L empties the output, as `clear` does, and keeps the line being typed; Ctrl+U removes the line before the cursor instead (all of it at the end). Tab completes the word being typed: the first word from the command names, a later one from the names in its folder (`cat docs/pl` looks in `docs`). One match goes in whole, a folder with `/` after it and anything else with a space; several go in as far as they agree, and a Tab that adds nothing lists them. In that list a folder ends with `/`, and a name with a space is in quotes. A name with a space goes in quotes (a folder's quote stays open, so Tab can go on inside it), and a word begun with a quote completes from inside it. Paths may be absolute or relative to the current folder, and `.` and `..` work.

Commands split on spaces. A part in double or single quotes is one word with its spaces kept and the quotes dropped, so `cat "my notes.txt"` reads one file; the other kind of quote inside is plain text (`echo "it's"`). A quote opens only at the start of a word, so `echo don't` prints `don't`. A quote left open runs nothing and says `no closing "`. A quoted `>` or `>>` is text for `echo`, not a redirect. `ls` and `find` show a name with a space in quotes (single ones if it has a `"`), so it can be typed back as it shows. Ctrl+V of a path with a space that is there, such as one Files' Ctrl+C copied, puts it in quotes at the start of a word.

## Commands

| Command | What it does |
|---|---|
| `help` | lists the commands, and how `>`, `>>`, quotes, `!!`, `!N` and `!text` work |
| `clear` | empties the output |
| `history` | the commands Up and Down go through (the last 50), numbered from the oldest; `history` itself is the last |
| `echo text` | prints the text |
| `echo text > path` | replaces the file with the text and a newline |
| `echo text >> path` | adds the text and a newline to the end of the file |
| `apps` | lists the apps the Start menu has |
| `date` | the current time in UTC, as `2026-10-27 05:12:16 UTC` |
| `workspace` | the open store directory, committed and backup generations, held state and any notice; with no store, says this run is not saved |
| `pwd` | the current folder |
| `cd [path]` | changes folder; without a path, goes to `/home` |
| `ls [path]` | lists a folder (the current one without a path), folders with a `/` after them, packed into lines that fit the window; for a file, prints its name |
| `cat path...` | prints a file, or several one after another (only the last 200 lines are kept, like any output); a missing one is an error and the rest still print |
| `cp from to` | copies a file or a folder to a new name, or into `to` when it is a folder; what is inside a folder is copied too. A name already there is not written over, and a folder is not copied into itself (`/` is in everything, so it is never copied) |
| `wc path...` | each file's lines (its newlines, as Unix counts them), words and characters, then the path (in quotes when it has a space, as `ls` shows names). A folder counts every file under it, in the order `ls` gives, and a total line follows, as it does for more than one path. An empty folder is `0 0 0 total`. One file on its own has no total line. An error for one path does not stop the rest |
| `head path [lines]` | the first 10 lines of a file, or as many as `lines` says (a whole number in digits; 0 prints nothing). A shorter file prints only the lines it has: a final newline is not an extra blank line |
| `tail path [lines]` | the last 10 lines of a file, or as many as `lines` says |
| `find text` | every file and folder under the current folder whose own name has `text` in it, as paths from there (folders with a `/` after them), in the order `ls` gives, each folder followed by what is in it |
| `tree [path]` | the folder (the current one without a path) and everything under it, two spaces in per level, names as `ls` shows them, in the order `ls` gives; then how many folders and files, as `2 folders, 5 files`. A big tree keeps its end, as `find` does. On a file it gives the file's name |
| `du [path]` | for each name in the folder (the current one without a path), the characters in that file or in all the files under that folder, lined up on the right, in the order `ls` gives; then the total and the number of files, as `1221 characters, 3 files`. On a file, its count and name |
| `diff path path` | the lines that differ between two files: `-N text` for line N of the first that the second does not have, `+N text` for line N of the second, from a longest run of lines both share; `diff: same lines` when there are none. Past 250,000 line pairs (after the lines both start and end with) it gives only the first line that differs. Two folders instead name each file only in one of them (`only in first`, `only in second`) and each file whose bytes differ (`differ`), or `diff: same lines` when every file under both matches |
| `cmp path path` | `cmp: same` when the lines are the same, or `cmp: line N` for the first line that differs. When one file ends first, N is the next line |
| `stat path` | `file, N characters` (or `character`), or `folder, N entries` (or `entry`) for the names in that folder. The file is not changed |
| `basename path` | the last part of the path, as written. The file does not have to exist. `/` stays `/` |
| `dirname path` | the folder part of the path. A name with no folder is `.`, and `/` stays `/`. The file does not have to exist |
| `grep text [path]` | the lines that have `text` in them: plain text, not a pattern, and case counts; quote it to look for words with spaces (`grep "old pond" poem.txt`). A file prints those lines. A folder, or no path, searches every file under that folder (the current one when the path is left out), in the order `ls` gives, and each line is `path:line` with the path quoted when it has a space. A folder with no match prints nothing |
| `sort path` | the lines of a file in order, by character (capitals before small letters); the file is not changed |
| `uniq path` | the lines of a file, leaving out a line the same as the one just before it (so a repeat further on stays, as in Unix) |
| `nl path` | the lines of a file, each after its number from 1, as `history` numbers commands |
| `tac path` | the lines of a file, last to first. A final newline is not an extra blank line. A file that is only a newline prints one blank line. A long file keeps its end, the last lines of the file |
| `mkdir path...` | makes each folder, and any missing folders above it |
| `touch path...` | makes each an empty file; an existing file or folder is left as it is |
| `write path text` | replaces the file with the text and a newline |
| `rm path...` | removes each file or empty folder; an error for one (not found, not empty) does not stop the rest |
| `mv from to` | renames, or moves into `to` when it is a folder; the file the next Editor opens goes along with it, and so does the Terminal when it is in the folder moved |

`clear`, `history`, `apps`, `date`, `workspace` and `pwd` take no words, and a word too many is an error for every command but `cat`, `rm`, `mkdir` and `touch`, which take several paths and do each in turn (`rm a b` removes both); `head` and `tail` take a count after the path.

`workspace` reads the store state and notice without changing either. A finished command still gets the usual desktop snapshot.

## Rules for paths

- No command has options. `cd`, `ls`, `cat`, `head`, `tail`, `wc`, `grep`, `sort`, `uniq`, `nl`, `tree`, `du`, `diff`, `cmp`, `stat`, `basename`, `dirname`, `tac`, `mkdir`, `touch`, `rm`, `mv` and `cp` refuse any word starting with `-`, and so do the paths of `write` and `echo >`. To name such a file, write `./-x`.
- A path ending in `/` must be a folder: `cat notes.txt/` and `rm notes.txt/` are errors, and `touch new/` makes nothing.
- Errors say which part is wrong: `not found: /home/x`, `not a folder: /home/notes.txt` when a part of the path is a file, `no folder: /home/missing` when the folder to write into is not there.
- If another app removes or moves the folder a Terminal is in, it moves up to the nearest folder that still exists.

## Output

The Terminal keeps the last 200 lines of output; older ones fall off the top. Page Up scrolls back through them a window at a time (keeping one row from the page before), and Page Down forward again; Shift with either does the same. Ctrl+Home goes to the oldest kept line and Ctrl+End back to the prompt; neither changes the line being typed. The mouse wheel over the window scrolls three rows a notch, without bringing the window to the front. While scrolled back, the last row says how many rows are below, as `-- 6 more below: pagedown --`, a click does not move the cursor, and any other key goes back to the prompt before it does what it does. Scrolling stops at the oldest kept row. With a workspace open, the scroll comes back after a restart, cut to what the window can still show; at the prompt it is left out of the snapshot. A bad scroll value in a snapshot is not installed. Long lines wrap to the window's width, so one kept line can take several rows. Only the rows that fit the window are built each frame, so a big `cat` stays quick.

## In the code

`terminal` in `shell/wm.relic`, with `_term_run` dispatching the commands to `_term_*` helpers (one each for `ls`, `cat`, `head`, `tail`, `grep`, `sort`, `uniq`, `nl`, `wc`, `cp` and the rest) and `_term_key` handling the keys, `!!` included. Tests: the `shell_terminal*` goldens, `shell_help`, `shell_date` and `shell_apps_fuzz` (see [the test list](../TESTING.md)).
