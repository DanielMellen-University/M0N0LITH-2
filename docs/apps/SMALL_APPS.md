# Clicker and Notes

The two smallest apps. They do not use the filesystem, and their state goes when the window closes.

## Clicker

Shows `Clicks: N`. A click anywhere inside the window, or Space, Return or `+` (or `=`, the same key without Shift) while it has focus, adds one. Backspace or `-` takes one back off, stopping at 0, and Delete sets the count back to 0. Ctrl+Z right after a Delete (before any other click or key that counts) brings the count back, once. Ctrl+C copies the count, the number alone, to the desktop's clipboard. Each Clicker window counts on its own.

## Notes

One line of text under `Type something:`, with `_` as the cursor, at its end to start with. Left, Right, Home, End, and Ctrl+Left and Ctrl+Right by words, move it, Delete removes the character after it, Ctrl+Delete the word after it and Ctrl+K the rest of the line, and typing and the keys below work where it is. Typing adds to it, keeping case, symbols and AltGr characters, and Backspace removes the last character, Ctrl+Backspace the last word, and Ctrl+U all of it (at the cursor: the character, word or everything before it). Ctrl+V adds the first line of the desktop's clipboard (see [Editor](EDITOR.md)). Ctrl+C copies the whole line to it and Ctrl+X cuts it (an empty line leaves the clipboard as it was). Ctrl+Z brings back the line from before the last Ctrl+U, Ctrl+X, Ctrl+Backspace, Ctrl+Delete, Ctrl+K or Ctrl+V, and a second Ctrl+Z puts it back as it was after (one step, not a history). Return does nothing: Notes is a single line. When the line is wider than the window, it scrolls to keep the cursor in view. Nothing is saved.

Tests: `shell_small_apps`, `shell_app_focus`, and the `shell_clicker_*` and `shell_notes_*` goldens; Notes' Ctrl keys are also in `shell_clipboard` (copy, cut and paste) and `shell_terminal_keys` (Ctrl+Backspace).
