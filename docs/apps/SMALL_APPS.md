# Clicker and Notes

The two smallest apps. They do not use the filesystem, and their state goes when the window closes.

## Clicker

Shows `Clicks: N`. A click anywhere inside the window, or Space or Return while it has focus, adds one. Backspace or `-` takes one back off, stopping at 0. Each Clicker window counts on its own.

## Notes

One line of text under `Type something:`, with `_` as the cursor at its end. Typing adds to it, keeping case, symbols and AltGr characters, and Backspace removes the last character, Ctrl+Backspace the last word, and Ctrl+U all of it. Ctrl+V adds the first line of the desktop's clipboard (see [Editor](EDITOR.md)). Ctrl+C copies the whole line to it and Ctrl+X cuts it (an empty line leaves the clipboard as it was). Return does nothing: Notes is a single line. When the line is wider than the window, its end stays in view. Nothing is saved.

Tests: `shell_small_apps`, `shell_clicker_edges`, `shell_app_focus`, `shell_notes_resize` and `shell_notes_input_edges`; Notes' Ctrl keys are also in `shell_clipboard` (copy, cut and paste) and `shell_terminal_keys` (Ctrl+Backspace).
