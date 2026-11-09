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

`workspace_fault` is how a test produces a torn save without killing the process. A fixture can instead be written as files; the loader does not care which writer made them.

## On-disk layout

Flat directory. Unknown names are ignored and are not deleted.

| Name | Meaning |
|---|---|
| `COMMITTED` | the committed generation. Exactly `g` + decimal + `\n`, such as `g3\n`. No leading zeros, no other bytes. Longer than 16 bytes is invalid |
| `gN.m2ws` | generation N, N from 1 to 9 digits, no leading zeros |
| `gN.m2ws.partial` | a write that did not finish. Never installed |
| `COMMITTED.next` | the pointer staged for the next commit. Never installed |

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

The first-run image is not that. With no `COMMITTED` and no generation names, the session keeps `vfs.new()`: `/home`, `/tmp`, and `/home/welcome.txt` holding `Welcome to Relic.\n`. No file is written until an app changes the vfs.

Example, after `echo hi > a.txt` on a fresh workspace (`Welcome to Relic.` is the default file):

```
M2WS1
D /home
F /home/a.txt hi\n
F /home/welcome.txt Welcome\sto\sRelic.\n
D /tmp
.
```

## What a save does

Each successful change made by Terminal, Files, the Editor, the IDE's Ctrl+S, Paint's save, or Snake writing its best score builds a new generation from the whole vfs and then:

1. Write `gN.m2ws.partial` and read it back. A mismatch stops here. `COMMITTED` is unchanged.
2. Rename that file to `gN.m2ws`. N is one past the committed generation and past any generation name already in the directory.
3. Write `COMMITTED.next` as `gN\n` and read it back.
4. Rename `COMMITTED.next` onto `COMMITTED`. On POSIX that replace is one rename. On Windows, `std::filesystem::rename` will not replace, so the publisher removes `COMMITTED` and then renames. A crash in that gap leaves no pointer; it does not delete the generation files.
5. Delete `gM.m2ws` for M < N-1, every `gM.m2ws.partial`, and a leftover `COMMITTED.next`. Invalid names and the newest two generations stay.

`host_write_file` does not report a short write and does not fsync. The read-back is the check we have. A kill after it returns, and before the pointer names the new file, keeps the previous commit. A power loss before the operating system flushes is outside what Relic 1.0.53 can promise.

The session vfs keeps the change even when the save fails. The notice says the save failed. The next process installs the store, not that unsaved session. Editor, IDE, and Paint do not say `saved` when the store did not commit. Terminal prints the notice. Files puts it in the title line until the next key. The desktop draws `wm.workspace_notice()` under the title when it is not empty.

## What a load does

The vfs is replaced only after a generation has fully parsed.

| Pointer | Other files | Installed | Notice |
|---|---|---|---|
| absent, and no generation names | | defaults, quiet | `""` |
| valid, and that generation parses | a newer complete `gM.m2ws` | the named generation | `workspace: ignored uncommitted gM` (highest such M) |
| valid, and that generation parses | a `gM.m2ws.partial` | the named generation | `workspace: ignored partial gM` (highest such M) |
| both of those leftovers | | the named generation | `workspace: ignored uncommitted gM; ignored partial gK` |
| valid, generation truncated | an older valid generation | the older one, the highest that parses | `workspace: committed image truncated; recovered gN` |
| valid, generation `M2WS` but not `M2WS1` | an older valid generation | that older one | `workspace: committed image wrong version; recovered gN` |
| valid, generation otherwise bad or missing | an older valid generation | that older one | `workspace: committed image invalid; recovered gN` |
| missing | at least one valid generation | the highest valid generation | `workspace: pointer missing; recovered gN` |
| invalid | at least one valid generation | the highest valid generation | `workspace: pointer invalid; recovered gN` |
| unusable, and nothing valid | a partial may exist | defaults | `workspace: no valid generation; using defaults` or the same plus `; ignored partial gN` |
| the directory cannot be listed | | the vfs is left as it was, and the workspace is not enabled | `workspace: cannot open store` |

A valid pointer wins over a newer complete generation. That newer file is an uncommitted save, and the notice names it. The previous generation, kept so a bad newer file can fall back, is not announced. A missing or invalid pointer cannot say which generation was committed, so the highest file that fully parses is installed and the notice says the pointer was the problem. Partials and files that do not parse are never installed. Corrupt files are left in the directory.

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

`full-uncommitted` on a store that already has a valid pointer leaves that pointer, so the next load ignores the new file. On a store with no pointer, a later load sees a missing pointer and a complete generation and installs it, with `workspace: pointer missing; recovered gN`. That is the same rule as the Windows gap between removing `COMMITTED` and renaming `COMMITTED.next`. To fixture "ignore this complete file", `COMMITTED` must still name an older valid generation.

Other save failures use `workspace: save failed; {reason}; kept gK` with reason `image too large`, `store readback mismatch`, or `cannot write store`.

## Guarantees

- After `workspace.save` returns `""`, a new process that opens the same directory installs that generation, or a newer one that a later successful save committed.
- A crash before that return does not replace `COMMITTED`. The previous generation file is still the one a valid pointer names, except in the Windows remove-then-rename gap, where the pointer may be missing and the highest valid generation is installed and named in the notice.
- A truncated, wrong-version, or otherwise invalid committed generation is not installed. An older generation that still parses is installed and the notice says recovery. With none, the defaults are installed and the notice says there was no valid generation. The bad bytes stay on disk.
- The first successful commit has no older generation. Losing that only file, with the pointer aimed at it, falls back to defaults. From the second successful commit on, the previous generation is kept until the one after next succeeds.
- Two processes must not write one store. The format has no lock.
- Unsaved Editor, IDE, and Paint buffers, Notes, Clicker, and window layout are not in the store.
- A program run in the IDE still cannot write the host disk. The store is written by the desktop, not by that program.

## Not promised

- Power-loss durability. There is no fsync in Relic 1.0.53.
- A bound on host memory beyond refusing to install a generation `files.size` says is over the cap, and refusing one that parses over the caps.
- That a missing pointer can tell an uncommitted complete generation from one whose pointer rename did not finish.
- Host mounts, extra apps, or a general operating system.
