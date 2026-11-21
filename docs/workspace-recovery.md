# Workspace recovery

The desktop's files (Terminal, Files, the Editor, the IDE, Paint, and Snake's best score) live in one in-memory filesystem, `std/vfs`. Quitting used to drop it. A workspace is a directory on the host that holds generations of that filesystem. It is not a mount: nothing in the image is opened as a host path, and the apps still only see the vfs.

Tests and any other `use` of `wm.relic` do not open a workspace. The session then behaves as it did before this milestone. `shell/desktop.relic` opens one. Muse's fixture directory and acceptance note are not read by this code. Those paths stay empty of our files:

- `tests/fixtures/workspace-recovery/`
- `docs/acceptance/workspace-recovery-muse.md`

A fixture is an ordinary directory in the layout below. Open it with `wm.workspace_open(path)` from a Relic program. No production or build file has to change.

## Where the desktop stores it

`wm.workspace_open_default()` (what the window calls):

| `M0N0LITH_WORKSPACE` | Directory |
|---|---|
| unset | `$HOME/.m0n0lith2/workspace`, or `$USERPROFILE/.m0n0lith2/workspace` when `HOME` is unset |
| a path | that directory, created on open |
| set, but empty | persistence stays off, and no notice is shown |

No `HOME` and no `USERPROFILE`, and the variable unset: persistence stays off and the notice is `workspace: no store path; this run is not saved`.

## Calls

| Call | What it does |
|---|---|
| `wm.workspace_open(path)` | enable `path` and install its image into the session vfs, replacing what was there |
| `wm.workspace_open_default()` | the table above, then the same install when a directory was chosen |
| `wm.workspace_enabled()` | true after a directory was opened |
| `wm.workspace_notice()` | `""` when there is nothing to report, otherwise the text below |
| `wm.workspace_status()` | read-only store directory, committed generation, META backup generation and hold reason, or `none` when no store is open |
| `wm.workspace_fault(stage)` | the next save stops at `stage` and then the arm is cleared. `""` clears it. Any other string fails as `workspace: unknown fault {stage}` |
| `wm.workspace_release()` | drop a hold. Does not delete files. The next successful save may replace them |

`workspace_fault` is how a test produces a torn save without killing the process. A fixture can instead be written as files; the loader does not care which writer made them. `shell_workspace_io_publication` tests host I/O failures through a test-only adapter, including a mismatching or unreadable pointer after its rename. It adds no production fault stages.

## On-disk layout

Flat directory. Unknown names are ignored and are not deleted.

| Name | Meaning |
|---|---|
| `COMMITTED` | the committed generation. Exactly `g` + decimal + `\n`, such as `g3\n`. No leading zeros, no other bytes. Longer than 16 bytes is invalid. The publication is the successful rename of `COMMITTED.next` onto this file. A later readback confirms the bytes for this process; it does not define the commit. If that readback fails, the result is uncertain |
| `META` | two lines, `committed gN` or `committed none`, then `previous gP` or `previous none`, each ending in `\n`. At most 64 bytes. Written only after `COMMITTED` has been renamed and read back as the new id. It is a backup, not a commit. A readable `COMMITTED` wins over it. If this write fails after that readback, the save still committed |
| `gN.m2ws` | generation N, N from 1 to 9 digits, no leading zeros |
| `gN.m2ws.partial` | a write that did not finish. Never installed |
| `gN.m2ws.damaged` | a bad or uncommitted generation kept by prune, with its bytes unchanged. Never installed. Its id still reserves a generation number |
| `COMMITTED.next`, `META.next` | staged pointer and metadata. Never installed |

At most 32 names matching `gN.m2ws` or `gN.m2ws.partial` are accepted. More than that: nothing is installed, the store is held, and the notice is `workspace: too many generation files; store held; using defaults`. Damaged names do not count toward this limit or cause a hold. Prune keeps at most 4 damaged files, removing the lowest ids first. A held store touches none of them, even when there are more than 4.

## Generation file

UTF-8, `\n` only. A raw CR byte (the generation is not a text-mode file) makes the generation invalid. There is no count and no length field. A number in a file's text is text.

```
M2WS1
D <escaped path>
F <escaped path><one space><escaped text>
.
```

The first line is exactly `M2WS1`. The last line is exactly `.`. The file ends with `\n` after that dot. A file that does not end in that `.` line is truncated, including one that keeps going after the dot. `M2WS` plus any other version is `wrong version`. A raw CR byte, or anything else in the first line, is `invalid`.

Records may arrive in any order. The writer sorts them by path, bytewise, directories and files together.

Escapes, in paths and in file text:

| Bytes | Meaning |
|---|---|
| `\\` | one backslash |
| `\n` | newline |
| `\r` | CR |
| `\t` | tab |
| `\s` | space |
| `\u` + 4 lowercase hex digits | a code 0 to 31 that is not already `\n`, `\r` or `\t` |

Any other backslash is invalid. Raw control characters are invalid inside records; use their escapes. `\u0009`, `\u000a` and `\u000d` are invalid too: use `\t`, `\n` and `\r`. The first raw space in an `F` record separates the path from the text. No space means the text is empty. Paths do not contain a raw space.

A path, after unescaping, must be a vfs path and nothing else:

- it starts with `/`, does not end with `/`, and is 2 to 240 characters
- components are split on `/`, and none is empty, `.` or `..`
- no backslash, and no character below 32
- it is not used with `std/files`. A `..` component is rejected, not normalized away

A vfs path that does not pass those rules (a newline in a name, for example) is not written. The save fails with `path cannot be stored` and the previous generation stays. `std/vfs` treats `\` as a separator, so a stored name does not contain one.

Parents must be present as `D` records. `/` is implied and is not written. A path cannot be both a file and a directory. A second record for the same path is invalid.

Caps, applied while parsing, before the session vfs is changed:

| Cap | Value |
|---|---|
| generation file | 1,500,000 bytes (`files.size` before reading, then a byte check on the text read) |
| entries (files plus directories) | 2,000 |
| one file's text | 262,144 characters |
| one path | 240 characters |
| one Editor, IDE or Paint window's history | 100 undo steps and 100 redo steps |
| removed plus added text in one Editor or IDE window's history | 65,536 characters across both stacks |
| canvas cells in one Paint window's history | 65,536 cells across both stacks, at most 30 full canvases |

The reader checks the UTF-8 byte cap again after reading, in case the file grew after `files.size`. The writer checks the same cap before writing a partial. A Unicode image that would be too large to reload fails with `image too large`; the pointer and metadata stay unchanged.

`std/files.read` still loads a generation that passed the size check into one string. That is a bound on what we will install, not a claim that a hostile file cannot make the host allocate. This is not a sandbox.

An empty image is legal and means the root has no children:

```
M2WS1
.
```

The first-run image is not that. With no `COMMITTED` and no generation names, the session keeps `vfs.new()`: `/home`, `/tmp`, and `/home/welcome.txt` holding `Welcome to Relic.\n`. `save` on its own writes a file when the vfs changes. The desktop also writes on window events, when a Terminal command finishes, after a pause in window input, and when the window quits. The timing is below.

Example, after `echo hi > a.txt` on a fresh workspace (`Welcome to Relic.` is the default file):

```
M2WS1
D /home
F /home/a.txt hi\n
F /home/welcome.txt Welcome\sto\sRelic.\n
D /tmp
.
```

## Window session

A generation written by the desktop records the open windows in the same file as the vfs. The rename of `COMMITTED` publishes both. A generation written by `save` with no session, which is what a test does when it never binds a desktop, has no window records. A file from before windows were stored still loads: the files come back and no windows open.

`S` lines come after all the `D` and `F` lines. A file or directory record after the first `S` line invalidates the whole generation, even with a matching checksum. `Z` is the last line before `.`, and only when there is an `S` line.

| Line | Meaning |
|---|---|
| `S -` | the desktop was saved with no windows. It is the only `S` line |
| `S W <App> <id> <x> <y> <width> <height> <0 to 3>` | one window, back to front. App is Clicker, Notes, Terminal, Files, Editor, IDE, Paint, or Snake. `1` means minimized, `2` maximized and `3` both. For a maximized window x to height are the place it goes back to, and a new desktop maximizes it again at its own size. id is unique, from 1 |
| `S F <key> <escaped value>` | one field of the window started by the previous `W`. The value uses the same escapes as a file. No raw space |

A session has at most 64 windows. The Editor, IDE and Paint `undo` and `redo` fields are optional independently. Snake fields may all be absent for an older snapshot, but a stored game must include every Snake field. These additions keep `M2WS1` and accept older snapshots without changing their meaning. A missing required field, an extra field, a bad number, a duplicate id, or anything else malformed in an `S` line is `invalid`. The vfs in that same file is not installed either.

| App | Fields |
|---|---|
| Terminal | `cwd`, `input`, `draft`, `buf`, `past`, `left`, `back`. `buf` and `past` are length-prefixed lines (a decimal length, a newline, then that many characters), at most 200 and 50 |
| Files | `path`, `sel` |
| Editor | `path`, `text`, `back`, `mark` (`-` or a count from the end of the text), `disk_set` (`0` or `1`), `disk`, optional `undo` and `redo` |
| IDE | the Editor fields, plus `out` (length-prefixed lines, at most 200) and `err` (`-` or a line number) |
| Notes | `text`, `left` |
| Clicker | `count` |
| Paint | `path`, `cells` (2160 digits, each `0` to `8`), `color`, `size`, `tool`, `status`, `foreign` (`0` or `1`), optional `undo` and `redo` |
| Snake | `body`, `dir`, `turns`, `food`, `score`, `state`, `seed`, all present or all absent. Best score remains only in the vfs file |

Editor and IDE `undo` and `redo` are length-prefixed records, using the same packing as `buf`. Each record contains exactly three length-prefixed strings: `at` (a decimal character index from 0 through 262,144, with no sign or leading zeros), `removed`, and `added`. Records stay in stack order, oldest first. Missing fields restore as empty stacks. A bad length, number, record shape, or history over either cap makes the generation `invalid`.

Editor and IDE snapshots keep the newest 100 steps in each stack, then drop oldest undo steps followed by oldest redo steps until their combined removed and added text fits 65,536 characters. Taking a snapshot does not shorten the live history. Restored Ctrl+Z and Ctrl+Y use the usual cursor placement and clear the selection. If a step does not fit the buffer or the text it would remove does not match, both stacks clear and the text stays unchanged; the status is `nothing to undo` or `nothing to redo`.

Paint `undo` and `redo` use length-prefixed records too. Each record is a whole canvas of exactly 2160 digits, each `0` to `8`, in stack order, oldest first. Snapshots retain the newest 100 steps per stack, then drop oldest undo steps followed by oldest redo steps until the combined canvases fit 65,536 cells. That fits 30 full canvases. Taking a snapshot leaves live history unchanged, including the existing 20-step drawing limit. A missing stack restores empty. Bad packing, a malformed canvas, or either cap being exceeded invalidates the whole generation. Restored Ctrl+Z and Ctrl+Y exchange canvases as usual; an active stroke or shape drag does not resume.

Snake `body` packs decimal cell indices as length-prefixed strings, tail first and head last. Indices run from 0 to 383 (`y * 24 + x`) without duplicates. `dir` is one of `1,0`, `0,1`, `-1,0`, `0,-1`. `turns` packs at most two such directions, each perpendicular to the preceding direction. `food` is a free cell index, or `-` for a won game. `score` is 0 to 381 and the body has `score + 3` cells. `state` is `ready`, `playing`, `paused`, `over` or `won`; `won` requires all 384 cells and no food. `seed` is the food generator state, 0 to 2,147,483,646. Cell indices, score and seed are canonical decimals without signs or leading zeros. Invalid values or a partial field group invalidate the generation.

Snake restores the board, head, queued turns, food, score, run state and food generator together. Best score is read from `/home/snake-best.txt`, with no second store. An older snapshot without Snake fields opens a new ready game. Absolute process clock values are omitted: the first focused tick starts a fresh movement beat, without catching up across the restart. There is no mid-step animation to save. A best-score commit records the complete eating step, including its next food or win.

The Snake and Paint recovery additions have model tests only. The GUI was not walked through; this does not extend the Nov 7 GUI pass.

The IDE rebuilds its diagnostics and error column from `out` on restore, and its error highlight on the first frame. If an older snapshot names an error line without a matching diagnostic, Ctrl+E uses column 1.

`Z <checksum>` covers every character before that line, including the newline after the previous line. Start two integers, `running` and `weighted`, at zero. For each character in order, set `running = (running + code_point) % 1000000007`, then `weighted = (weighted + running) % 1000000007`. The checksum is the final `weighted` value: a position-weighted sum modulo the prime 1,000,000,007, always from 0 through 1,000,000,006, written with no leading zeros. The writer and reader use the same helper. Within the generation size limit, this detects a single changed code point, a swap of two different code points, or equal-and-opposite changes to two code points. Other changes can collide; this is not cryptographic and does not protect against deliberate tampering. A checksum that does not match is `invalid`, so the generation is not installed. A generation with no `S` line has no `Z` line.

The desktop writes this snapshot when a window opens, closes, moves, resizes, or is minimized or restored, when a Terminal command finishes, when a file change is committed, and when the window quits. It also writes once after a pause in window input, including typing in the Editor, the IDE and Notes, and drawing in Paint.

With a workspace open and a desktop bound by `wm.workspace_bind`, key or mouse input sent to a window marks the session pending unless a snapshot or file commit already follows it. Input has no timestamp: it clears the idle start, and the first `wm.tick(d, ms)` after that input records `ms`. A tick at least 2000 ms later writes the normal window snapshot once. New input restarts that interval. Further ticks write nothing until more input arrives. A failed attempt keeps its failure notice and waits for new input instead of retrying every frame. Ticks on another desktop, an unbound desktop, or with no workspace enabled do not write. Snake moving on the clock does not mark input pending; its best score still commits as before.

The idle snapshot records unsaved buffers with the current vfs. It does not save Editor or IDE text into a vfs file, or save Paint's cells into its picture file. Ctrl+S and the interrupted-save fallback rules below stay the same.

Not in the snapshot: a find or a rename still being typed, the clipboard, and an IDE run (including one that is waiting for a line). Editor, IDE and Paint undo and redo return within their history caps. An IDE program does not keep running after a restart.

## What a save does

Each change made by Terminal, Files, the Editor, the IDE's Ctrl+S, Paint's save, or Snake writing its best score builds a new generation from the whole vfs. When a desktop is bound, that generation includes the window session above. Typing in the Editor is not, by itself, one of these changes. N is one past every generation id already in the directory, including partial and damaged files, and every id named by `COMMITTED` or `META`. An existing `gN.m2ws` is never rewritten.

1. Write `gN.m2ws.partial` and read it back. A mismatch stops here. `COMMITTED` and `META` are unchanged.
2. Rename that partial to `gN.m2ws`. This creates the image. It does not commit it. If that rename fails, stop. `COMMITTED` is unchanged.
3. Write `COMMITTED.next` as `gN\n` and read it back. If this file cannot be written (it is a directory, for example), stop. `META` is unchanged. The new `gN.m2ws` is an uncommitted leftover.
4. Rename `COMMITTED.next` onto `COMMITTED`. On Linux this replace is the publication: after `rename` returns, the new id is the commit even if this process has not read it back yet. On Windows, `std::filesystem::rename` will not replace, so the publisher removes `COMMITTED` and then renames. A crash in that gap leaves no pointer. `META` is still the previous success, so the load keeps that generation and does not install the leftover.
5. Read `COMMITTED` back. If it is `gN\n`, write `META` (`committed gN`, `previous` the generation that was installed when the save started) and then prune as below. If that `META` write fails, the commit still stands: `save` returns success, the Editor says `saved`, and the notice is `workspace: saved; metadata backup not updated`. It does not say the save failed and it does not say the previous generation was kept. The next open follows `COMMITTED`.
6. If the readback does not match, the notice is `workspace: save failed; pointer publish uncertain` with no `kept` generation. The rename may already have published, so the previous id is not known to be what a new process will install. `META` is not updated.
7. `save` returns success only when the readback matches. A crash after the rename and before the return can still leave `COMMITTED` naming gN.

Prune keeps the new commit and the generation that was installed when the save started. For every other `gM.m2ws`, it renames the file to `gM.m2ws.damaged` if that generation failed to parse at the last load, or if M is newer than the installed generation. With defaults installed, every leftover complete generation is kept this way. Rename keeps the bytes exactly. If the destination already exists or the rename fails, the source stays. Old valid superseded generations and partials are removed. Prune also removes staged pointer and metadata files. It then removes the lowest damaged ids until at most 4 remain. A held store does not write, rename or prune anything.

Each successful move adds a save notice such as `workspace: kept damaged g4 as g4.m2ws.damaged`. It follows the boot notice or metadata warning after ` | `, in the same style as other save notices. The next save replaces that save notice; reopening clears it. Damaged files are ignored quietly on load, even if `COMMITTED` or `META` names their id.

`host_write_file` does not report a short write and does not fsync. A power loss before the operating system flushes is outside what Relic 1.0.53 can promise. `META` is a backup written after the pointer rename. It is not a commit. A readable `COMMITTED` wins over it. A torn pointer uses `META` only for a generation this desktop can parse; a wrong-version file named there holds the store and is not overwritten.

The session vfs keeps the change even when the save fails. The notice says the save failed. The next process installs the store, not that unsaved session. Editor, IDE, and Paint do not say `saved` when the store did not commit. Terminal prints the notice. Files puts it in the title line until the next key. The desktop draws `wm.workspace_notice()` under the title when it is not empty.

## What a load does

The vfs is replaced only after a generation has fully parsed.

| Pointer | Other files | Installed | Notice |
|---|---|---|---|
| absent, and no generation names | | defaults, quiet | `""` |
| valid, and that generation parses | a newer complete `gM.m2ws` | the named generation | `workspace: ignored uncommitted gM` (highest such M) |
| valid, and that generation parses | a `gM.m2ws.partial` | the named generation | `workspace: ignored partial gM` (highest such M) |
| both of those leftovers | | the named generation | `workspace: ignored uncommitted gM; ignored partial gK` |
| any | `gM.m2ws.damaged` files | unchanged by those files; only ordinary generations can install | no notice about damaged files; their ids only reserve numbers for the next save |
| valid, generation truncated or otherwise bad | an older valid generation, and maybe a newer complete file | the newest valid generation **older than the named one** | `workspace: committed image truncated; recovered gN` (or `invalid`). A newer file is `ignored uncommitted`, not installed |
| valid, generation `M2WS` but not `M2WS1` | | defaults, or an older generation this desktop can parse | `workspace: committed image wrong version; store held; ...` The store is not written or deleted until `wm.workspace_release()` |
| named generation missing or bad, and nothing older parses | | defaults | `workspace: no valid generation; using defaults` |
| missing or invalid | `META` names a generation that parses | that generation, not a newer one | `workspace: pointer missing; recovered gN` or `pointer invalid` |
| missing or invalid | exactly one valid generation and no `META` | that generation | the same recovered notice |
| missing or invalid | two or more valid generations and no usable `META` | defaults, store held | `workspace: pointer invalid; store held; using defaults; ignored uncommitted gN` |
| more than 32 generation names | | defaults, store held | `workspace: too many generation files; store held; using defaults` |
| the directory cannot be listed, or the path cannot be opened | | the vfs is left as it was, and the workspace is not enabled | `workspace: cannot open store` |

A readable pointer that names a generation which parses wins. A newer complete file is an uncommitted save and is not installed, including when the named generation is truncated or otherwise bad: the fallback is an **older** generation, never a newer one. Partials and damaged files do not install. Damaged files do not count toward any hold rule. A wrong version, too many generation names, or a torn pointer with more than one valid generation and no usable `META` holds the store. Saves then fail and do not say they were saved, and nothing in the directory is replaced or deleted until `wm.workspace_release()`. That call does not delete files. The next successful save follows the prune rules above. An empty `workspace_open("")` is a session-only opt-out and is not a failure. A path that was requested and could not be opened is a failure, and Ctrl+S says so.

The boot notice stays for the rest of the process, including after a later successful save. The latest save notice is appended after ` | ` until the next save replaces or clears it.

## Fault stages

One shot, then the arm clears. The save returns the notice and does not say it succeeded.

| Stage | What it leaves | Notice from the save |
|---|---|---|
| `partial-generation` | `gN.m2ws.partial` is exactly `M2WS1\n`. No `gN.m2ws`. Pointer unchanged | `workspace: save failed (partial-generation); kept gK` |
| `full-uncommitted` | `gN.m2ws` is the full image of the vfs after the change. Pointer unchanged | `workspace: save failed (full-uncommitted); kept gK` |
| `staged-pointer` | that full `gN.m2ws`, and `COMMITTED.next` is exactly `gN\n`. Pointer unchanged | `workspace: save failed (staged-pointer); kept gK` |
| `torn-pointer` | no new generation. `COMMITTED` is exactly the byte `x` | `workspace: save failed (torn-pointer); kept gK` |
| `corrupt-committed` | `gN.m2ws` is exactly `M2WS1\n` and `COMMITTED` is `gN\n`. The previous generation file is not deleted | `workspace: save failed (corrupt-committed); kept gK` |

`gK` is the generation a load would have installed before this save, or `defaults` when there was none. `kept` means the recoverable store, not that the session vfs was rolled back.

`full-uncommitted` on a store that already has a valid pointer leaves that pointer, so the next load ignores the new file. A missing pointer does not install that leftover. `META` still names the last confirmed commit, and that generation loads when it parses. That is the Windows gap after `COMMITTED` is removed and the replacement rename has not finished. The in-flight generation is not the commit. A missing pointer installs a generation `META` does not name only when there is no usable `META` and exactly one valid generation.

Other save failures use `workspace: save failed; {reason}; kept gK` with reason `image too large`, `store readback mismatch`, or `cannot write store`.

The next generation number is one past every id already stored or named, including damaged files. A failed save does not reuse the id of a truncated, wrong-version, or uncommitted file. After a confirmed pointer readback, prune keeps the new commit and the generation that was installed when the save started, and keeps damaged or newer uncommitted leftovers under the separate 4-file limit.

`wm.workspace_release()` is not a menu item. It is the explicit release of a hold.

## Guarantees

- On Linux the publication is `rename` of `COMMITTED.next` onto `COMMITTED`. After that call returns, the new id is committed even if this process is killed before it reads the pointer back. A readback that then fails is an uncertain result: `save` does not report success, and `META` is not moved to the new id. The next open trusts whatever `COMMITTED` actually contains.
- `META` is written only after that readback matches. A failed pointer publish does not update `META`. A later torn pointer therefore still names the last confirmed commit, not the failed generation.
- On Windows, replacing `COMMITTED` is remove-then-rename. A crash in that gap can leave no pointer. `META` still names the previous confirmed commit, so that generation is what loads. The generation file written for the interrupted save is not installed.
- A torn or missing pointer with a `META` whose committed id parses as this version installs that generation. A newer complete file is ignored and named in the notice. It is not treated as the commit. If that id is a wrong version, the store is held and the bytes stay.
- A torn or missing pointer with no usable `META` and exactly one valid generation installs that one. With two or more, it installs none, holds the store, and does not delete those files.
- A truncated or otherwise unreadable committed generation is not installed. The newest **older** generation that parses is installed. A newer complete generation is not. With no older generation, the defaults are installed and the notice says so. The next successful save renames the bad and newer uncommitted files as damaged, keeping their bytes under the 4-file limit.
- A wrong-version committed file, more than 32 generation names, or an ambiguous torn pointer holds the store. Continued use does not overwrite or delete it. `workspace_release` then a later successful save may.
- The first successful commit has no older generation. From the second on, the generation that was installed when the save started is kept until the save after next replaces it as the backup.
- Two processes must not write one store. The format has no lock.
- Open windows are in the snapshot the desktop writes: place, size, minimized, maximized, the Terminal's folder, output and command history, Files' folder, Editor and IDE text (saved or not) with bounded undo and redo, Notes' line, Clicker's count, Paint's cells with bounded undo and redo, and Snake's board and run state. The clipboard and a running IDE program stay outside the snapshot. A files-only `save` does not write them. Window input is included after 2000 ms of idle tick time, or at the next snapshot or quit. The idle snapshot leaves the vfs files unchanged.
- A program run in the IDE still cannot write the host disk. The store is written by the desktop, not by that program.
- There is no fsync. This is not a promise about power loss.

## Not promised

- Recovery of input since the last successful snapshot. Continuous input postpones the idle snapshot, a stopped frame loop cannot write it, and a failed attempt waits for new input. A kill before a successful snapshot keeps the previous one.
- Power-loss durability. There is no fsync in Relic 1.0.53. A commit that `save` has not yet published in `COMMITTED` is not durable across a kill, and a commit that has been published is still only as durable as the kernel's write-back.
- A bound on host memory beyond refusing to install a generation `files.size` says is over the cap, and refusing one that parses over the caps.
- Host mounts, extra apps, or a general operating system.
