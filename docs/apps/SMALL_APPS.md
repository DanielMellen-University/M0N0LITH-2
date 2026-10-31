# Clicker and Notes

The two smallest apps. They do not use the filesystem, and their state goes when the window closes.

## Clicker

Shows `Clicks: N`. A click anywhere inside the window, or Space while it has focus, adds one. Each Clicker window counts on its own.

## Notes

One line of text under `Type something:`, with `_` as the cursor at its end. Typing adds to it, keeping case, symbols and AltGr characters, and Backspace removes the last character. Return does nothing: Notes is a single line. When the line is wider than the window, its end stays in view. Nothing is saved.

Tests: `shell_small_apps`, `shell_clicker_edges`, `shell_app_focus`, `shell_notes_resize` and `shell_notes_input_edges`.
