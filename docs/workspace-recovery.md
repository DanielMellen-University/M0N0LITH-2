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
| `wm.workspace_fault(stage)` | the next save stops at `stage` and then the arm is cleared. `""` clears it. Any other string fails as `workspace: unknown fault {stage}` |
| `wm.workspace_release()` | drop a hold. Does not delete files. The next successful save may replace them |

`workspace_fault` is how a test produces a torn save without killing the process. A fixture can instead be written as files; the loader does not care which writer made them.

## On-disk layout

Flat directory. Unknown names are ignored and are not deleted.

| Name | Meaning |
|---|---|
| `COMMITTED` | the committed generation. Exactly `g` + decimal + `\n`, such as `g3\n`. No leading zeros, no other bytes. Longer than 16 bytes is invalid. The publication is the successful rename of `COMMITTED.next` onto this file. A later readback confirms the bytes for this process; it does not define the commit. If that readback fails, the result is uncertain |
| `META` | two lines, `committed gN` or `committed none`, then `previous gP` or `previous none`, each ending in `\n`. At most 64 bytes. Written only after `COMMITTED` has been renamed and read back as the new id. It is a backup, not a commit. A readable `COMMITTED` wins over it. If this write fails after that readback, the save still committed |
| `gN.m2ws` | generation N, N from 1 to 9 digits, no leading zeros |
| `gN.m2ws.partial` | a write that did not finish. Never installed |
| `COMMITTED.next`, `META.next` | staged pointer and metadata. Never installed |

At most 32 names matching the two generation patterns are accepted. More than that: nothing is installed, and the notice is `workspace: too many generation files; using defaults`.

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

Any other backslash is invalid. The first raw space in an `F` record separates the path from the text. No space means the text is empty. Paths do not contain a raw space.

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
| generation file | 1,500,000 bytes (`files.size` first; the read is discarded when larger) |
| entries (files plus directories) | 2,000 |
| one file's text | 262,144 characters |
| one path | 240 characters |

`std/files.read` still loads a generation that passed the size check into one string. That is a bound on what we will install, not a claim that a hostile file cannot make the host allocate. This is not a sandbox.

An empty image is legal and means the root has no children:

```
M2WS1
.
```

The first-run image is not that. With no `COMMITTED` and no generation names, the session keeps `vfs.new()`: `/home`, `/tmp`, and `/home/welcome.txt` holding `Welcome to Relic.\n`. `save` on its own writes a file when the vfs changes. The desktop also writes when a window opens, closes, moves, resizes, or is minimized, when a Terminal command finishes, and when the window quits.

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

`S` lines come after the `D` and `F` lines. `Z` is the last line before `.`, and only when there is an `S` line.

| Line | Meaning |
|---|---|
| `S -` | the desktop was saved with no windows. It is the only `S` line |
| `S W <App> <id> <x> <y> <width> <height> <0 or 1>` | one window, back to front. App is Clicker, Notes, Terminal, Files, Editor, IDE, Paint, or Snake. `1` means minimized. id is unique, from 1 |
| `S F <key> <escaped value>` | one field of the window started by the previous `W`. The value uses the same escapes as a file. No raw space |

A missing field, an extra field, a bad number, a duplicate id, or anything else in an `S` line is `invalid`. The vfs in that same file is not installed either.

| App | Fields |
|---|---|
| Terminal | `cwd`, `input`, `draft`, `buf`, `past`, `left`, `back`. `buf` and `past` are length-prefixed lines (a decimal length, a newline, then that many characters), at most 200 and 50 |
| Files | `path`, `sel` |
| Editor | `path`, `text`, `back`, `mark` (`-` or a count from the end of the text), `disk_set` (`0` or `1`), `disk` |
| IDE | the Editor fields, plus `out` (length-prefixed lines, at most 200) and `err` (`-` or a line number) |
| Notes | `text`, `left` |
| Clicker | `count` |
| Paint | `path`, `cells` (2160 digits, each `0` to `8`), `color`, `size`, `tool`, `status`, `foreign` (`0` or `1`) |
| Snake | none. The window opens on a new game. The best score is the vfs file |

The IDE rebuilds its diagnostics and error column from `out` on restore, and its error highlight on the first frame. If an older snapshot names an error line without a matching diagnostic, Ctrl+E uses column 1.

`Z <checksum>` covers every character before that line, including the newline after the previous line. Start two integers, `running` and `weighted`, at zero. For each character in order, set `running = (running + code_point) % 1000000007`, then `weighted = (weighted + running) % 1000000007`. The checksum is the final `weighted` value: a position-weighted sum modulo the prime 1,000,000,007, always from 0 through 1,000,000,006, written with no leading zeros. The writer and reader use the same helper. Within the generation size limit, this detects a single changed code point, a swap of two different code points, or equal-and-opposite changes to two code points. Other changes can collide; this is not cryptographic and does not protect against deliberate tampering. A checksum that does not match is `invalid`, so the generation is not installed. A generation with no `S` line has no `Z` line.

The desktop writes this snapshot when a window opens, closes, moves, resizes, or is minimized or restored, when a Terminal command finishes, when a file change is committed, and when the window quits. Typing in the Editor, the IDE, Notes, or Paint is included in the next one of those, and on quit. It is not its own commit. A kill between those keystrokes keeps the previous snapshot.

Not in the snapshot: undo and redo, a find or a rename still being typed, the clipboard, an IDE run (including one that is waiting for a line), and Snake's board. After a restart, Ctrl+Z has nothing to undo until the next edit, and an IDE program does not keep running.

## What a save does

Each change made by Terminal, Files, the Editor, the IDE's Ctrl+S, Paint's save, or Snake writing its best score builds a new generation from the whole vfs. When a desktop is bound, that generation includes the window session above. Typing in the Editor is not, by itself, one of these changes. N is one past every generation id already in the directory and every id named by `COMMITTED` or `META`. An existing `gN.m2ws` is never rewritten.

1. Write `gN.m2ws.partial` and read it back. A mismatch stops here. `COMMITTED` and `META` are unchanged.
2. Rename that partial to `gN.m2ws`. This creates the image. It does not commit it. If that rename fails, stop. `COMMITTED` is unchanged.
3. Write `COMMITTED.next` as `gN\n` and read it back. If this file cannot be written (it is a directory, for example), stop. `META` is unchanged. The new `gN.m2ws` is an uncommitted leftover.
4. Rename `COMMITTED.next` onto `COMMITTED`. On Linux this replace is the publication: after `rename` returns, the new id is the commit even if this process has not read it back yet. On Windows, `std::filesystem::rename` will not replace, so the publisher removes `COMMITTED` and then renames. A crash in that gap leaves no pointer. `META` is still the previous success, so the load keeps that generation and does not install the leftover.
5. Read `COMMITTED` back. If it is `gN\n`, write `META` (`committed gN`, `previous` the generation that was installed when the save started) and then prune. Prune removes partials and generation files other than gN and that previous generation. If that `META` write fails, the commit still stands: `save` returns success, the Editor says `saved`, and the notice is `workspace: saved; metadata backup not updated`. It does not say the save failed and it does not say the previous generation was kept. The next open follows `COMMITTED`.
6. If the readback does not match, the notice is `workspace: save failed; pointer publish uncertain` with no `kept` generation. The rename may already have published, so the previous id is not known to be what a new process will install. `META` is not updated.
7. `save` returns success only when the readback matches. A crash after the rename and before the return can still leave `COMMITTED` naming gN.

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
| valid, generation truncated or otherwise bad | an older valid generation, and maybe a newer complete file | the newest valid generation **older than the named one** | `workspace: committed image truncated; recovered gN` (or `invalid`). A newer file is `ignored uncommitted`, not installed |
| valid, generation `M2WS` but not `M2WS1` | | defaults, or an older generation this desktop can parse | `workspace: committed image wrong version; store held; ...` The store is not written or deleted until `wm.workspace_release()` |
| named generation missing or bad, and nothing older parses | | defaults | `workspace: no valid generation; using defaults` |
| missing or invalid | `META` names a generation that parses | that generation, not a newer one | `workspace: pointer missing; recovered gN` or `pointer invalid` |
| missing or invalid | exactly one valid generation and no `META` | that generation | the same recovered notice |
| missing or invalid | two or more valid generations and no usable `META` | defaults, store held | `workspace: pointer invalid; store held; using defaults; ignored uncommitted gN` |
| more than 32 generation names | | defaults, store held | `workspace: too many generation files; store held; using defaults` |
| the directory cannot be listed, or the path cannot be opened | | the vfs is left as it was, and the workspace is not enabled | `workspace: cannot open store` |

A readable pointer that names a generation which parses wins. A newer complete file is an uncommitted save and is not installed, including when the named generation is truncated or otherwise bad: the fallback is an **older** generation, never a newer one. Partials do not install. A wrong version, too many generation names, or a torn pointer with more than one valid generation and no usable `META` holds the store. Saves then fail and do not say they were saved, and nothing in the directory is replaced or deleted until `wm.workspace_release()`. That call does not delete files. The next successful save may. An empty `workspace_open("")` is a session-only opt-out and is not a failure. A path that was requested and could not be opened is a failure, and Ctrl+S says so.

The boot notice stays for the rest of the process, including after a later successful save. A failed save is appended after ` | ` until a save succeeds.

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

The next generation number is one past every id already stored or named. A failed save does not reuse the id of a truncated, wrong-version, or uncommitted file. After a confirmed pointer readback, prune keeps the new commit and the generation that was installed when the save started.

`wm.workspace_release()` is not a menu item. It is the explicit release of a hold.

## Guarantees

- On Linux the publication is `rename` of `COMMITTED.next` onto `COMMITTED`. After that call returns, the new id is committed even if this process is killed before it reads the pointer back. A readback that then fails is an uncertain result: `save` does not report success, and `META` is not moved to the new id. The next open trusts whatever `COMMITTED` actually contains.
- `META` is written only after that readback matches. A failed pointer publish does not update `META`. A later torn pointer therefore still names the last confirmed commit, not the failed generation.
- On Windows, replacing `COMMITTED` is remove-then-rename. A crash in that gap can leave no pointer. `META` still names the previous confirmed commit, so that generation is what loads. The generation file written for the interrupted save is not installed.
- A torn or missing pointer with a `META` whose committed id parses as this version installs that generation. A newer complete file is ignored and named in the notice. It is not treated as the commit. If that id is a wrong version, the store is held and the bytes stay.
- A torn or missing pointer with no usable `META` and exactly one valid generation installs that one. With two or more, it installs none, holds the store, and does not delete those files.
- A truncated or otherwise unreadable committed generation is not installed. The newest **older** generation that parses is installed. A newer complete generation is not. With no older generation, the defaults are installed and the notice says so. The bad bytes stay on disk.
- A wrong-version committed file, more than 32 generation names, or an ambiguous torn pointer holds the store. Continued use does not overwrite or delete it. `workspace_release` then a later successful save may.
- The first successful commit has no older generation. From the second on, the generation that was installed when the save started is kept until the save after next replaces it as the backup.
- Two processes must not write one store. The format has no lock.
- Open windows are in the snapshot the desktop writes: place, size, minimized, the Terminal's folder, output and command history, Files' folder, Editor and IDE text (saved or not), Notes' line, Clicker's count, and Paint's cells. Undo, the clipboard, a running IDE program, and Snake's board are not. A files-only `save` does not write them. Keystrokes since the last snapshot are not on disk until the next snapshot or quit.
- A program run in the IDE still cannot write the host disk. The store is written by the desktop, not by that program.
- There is no fsync. This is not a promise about power loss.

## Not promised

- Power-loss durability. There is no fsync in Relic 1.0.53. A commit that `save` has not yet published in `COMMITTED` is not durable across a kill, and a commit that has been published is still only as durable as the kernel's write-back.
- A bound on host memory beyond refusing to install a generation `files.size` says is over the cap, and refusing one that parses over the caps.
- Host mounts, extra apps, or a general operating system.
