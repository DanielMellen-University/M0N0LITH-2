# Tests

Every test is a Relic program in `tests/` that drives `shell/wm.relic` with fake clicks, keys and graphics events and prints what happened. None of them needs SDL.

## Running them

After building Relic (see [Building](BUILDING.md)):

```
cmake -S . -B build
ctest --test-dir build -C Release --output-on-failure
```

One test: `ctest --test-dir build -C Release -R golden_shell_ide`. Or run it straight from the `tests` folder, which is where the runner starts it: `cd tests && ../relic/build/relic shell_ide.relic`.

## How they are checked

CMake finds every `tests/*.relic` and adds it as `golden_<name>`. `tools/run_golden.cmake` runs it from `tests/`, and it passes when it exits with 0 and its standard output matches `<name>.out` exactly (Windows line endings are ignored). A test with no `.out` file must print nothing. One more test, `check_shell`, runs `relic check` on `wm.relic` and `desktop.relic`, which catches syntax errors and undefined names in the drawing code no test runs. That is 183 tests in all, and CI runs them on Linux, macOS and Windows.

None of them opens the SDL window. A passing run does not prove what the desktop draws. The Linux GUI pass, and what it did not try, is in the [roadmap](ROADMAP.md#accepted-nov-7-2026).

`shell_fuzz`, `shell_apps_fuzz` and `shell_events_fuzz` use fixed seeds, so their output is the same on every run. `shell_fuzz` checks the window model's invariants after every random step on two desktop sizes; `shell_apps_fuzz` sends random commands from two Terminals while Files and the Editor work on the same filesystem.

## Adding or changing one

Write `tests/shell_<topic>.relic`, run it, read its output, and save that as `tests/shell_<topic>.out` once it is right. To change an expected output on purpose, do the same and read the diff before committing. Add it to the list below.

## The list

### Windows and the Start menu

| Test | What it covers |
|---|---|
| `shell_wm` | drives wm.relic with fake clicks and keys; output must match shell_wm.out |
| `shell_lifecycle` | window ids, focus and tab order through lifecycle changes |
| `shell_minimize` | minimize and restore from the taskbar and the _ box |
| `shell_close_focus` | closing a focused window gives focus to the next window down, closing another leaves focus alone, closing the last leaves none |
| `shell_start_menu` | the Start button opens and closes the menu; Up, Down and Return on the open menu |
| `shell_menu_all_rows` | every Start menu row launches its app, in the documented order, with the first row marked on each open |
| `shell_menu_focus` | keyboard focus while the Start menu or the +N list is open |
| `shell_menu_edges` | Start menu row and taskbar hit boundaries |
| `shell_drag_resize` | dragging and resizing keep windows reachable |
| `shell_resize_offset` | resizing follows the point grabbed in the handle |
| `shell_resize_handle` | presses just left of or above the resize handle go to the app, presses on its corners start a resize that keeps the top-left corner |
| `shell_launch_small` | cascaded windows fit a small desktop |
| `shell_launch_sizes` | each of the eight apps opens at its documented size on a desktop big enough to fit it |
| `shell_cascade_gaps` | a new window does not open on top of another after closes |
| `shell_missed_release` | a lost mouse-up does not leave a drag running |
| `shell_outside_click` | presses outside the desktop do not hit its controls |
| `shell_title` | window titles fit beside the title bar buttons |
| `shell_escape` | Escape closes the Start menu or +N list before it quits, and gives up a find, a line number or a name once |

### Taskbar

| Test | What it covers |
|---|---|
| `shell_many_windows` | windows cascade and wrap, taskbar tabs shrink to fit |
| `shell_taskbar_overflow` | the +N button and hidden-windows list at 14 to 300 windows |
| `shell_taskbar_narrow` | taskbar tabs and the +N button on narrow desktops and with many windows |
| `shell_overflow_edges` | overflow threshold and list row boundaries |
| `shell_overflow_lifecycle` | focus and stacking as windows change with the list open |
| `shell_taskbar_focus_swap` | the focused hidden window takes the last shown tab, and picking the displaced window from the list gives it a button again |
| `shell_overflow_close_fit` | closing windows with the list open keeps it open while they overflow, and removes the +N button and the list once they all fit |
| `shell_overflow_short` | the hidden-windows list on a short desktop: fewer rows per column, a new column to the left, picking a second-column row |
| `shell_overflow_all_minimized` | overflow tabs and restore when no window is focused |
| `shell_overflow_limit` | the last visible row and the 200-row list limit |
| `shell_overflow_titles` | empty, long and non-ASCII window names in overflow |
| `shell_overflow_speed` | the hidden-windows list stays quick at 300 windows |

### Input events

| Test | What it covers |
|---|---|
| `shell_input` | graphics events turned into keys and clicks (ctrl+s, text, the mouse) |
| `shell_event_keys` | named keys, modifiers and ignored events |
| `shell_altgr` | AltGr (Ctrl+Alt) typing is text, not Ctrl+S |
| `shell_cmd_keys` | Cmd with a letter acts like Ctrl (Cmd+S, Cmd+Z, Cmd+A on macOS) |
| `shell_held_keys` | repeated key_down events from held keys, and key_up |
| `shell_window_cycle` | Ctrl+Tab brings the lowest visible window to the front and goes round, skips minimized ones, does nothing with no windows, and no app sees the key; Ctrl+Shift+Tab going the other way and undoing a Ctrl+Tab; Ctrl+W closing the window with focus and leaving a minimized one; Ctrl+M minimizing it; Ctrl+1 to Ctrl+9 picking a window by its taskbar place |
| `shell_window_digits` | Ctrl+9 picks by launch order after stacking changes and restores a minimized ninth window; Ctrl+0 changes nothing |
| `shell_mouse_buttons` | left and right mouse buttons during a drag |

### Drawing and clipping

| Test | What it covers |
|---|---|
| `shell_clip` | text cut to the window, Files scrolling to the selection |
| `shell_render_modes` | clipping and row selection for plain and tail apps |

### Clicker and Notes

| Test | What it covers |
|---|---|
| `shell_small_apps` | Editor, Notes and Clicker |
| `shell_clicker_edges` | rapid input and Clicker state after reopening; Return counts, Backspace and `-` take one off down to 0, Ctrl+C copies the number; Delete setting the count back to 0; + and = adding one |
| `shell_app_focus` | Notes and Clicker state across focus and window controls |
| `shell_notes_resize` | Notes text clipping and edits across resizes |
| `shell_notes_cursor` | Notes: Left, Right, Home, End and word jumps move the cursor, Delete, typing, Backspace, Ctrl+Backspace, Ctrl+Delete, Ctrl+K and Ctrl+U at it, and Ctrl+Z bringing back the whole line; a long line keeps the cursor in view |
| `shell_notes_input_edges` | single-line input and reopening Notes; Ctrl+Z bringing a cleared line back, or taking a paste back, one step |
| `shell_notes_two_windows` | Notes: two windows keep their own lines; typing in one leaves the other alone |
| `shell_notes_empty_clipboard` | Notes: Ctrl+X or Ctrl+C on an empty line leaves the clipboard as it was |
| `shell_clicker_two_windows` | Clicker: two windows count on their own, and undoing one leaves the other alone |
| `shell_clicker_title_click` | Clicker: a click on its title bar or on the empty desktop counts nothing; only a click inside the window does |

### Terminal

| Test | What it covers |
|---|---|
| `shell_terminal` | Terminal commands: extra spaces, folders, redirects, errors, `wc`, `cp` (to a name or into a folder, not a folder, not over a file) and `head`; `cat` with several files; `tail` and `grep`; `find` |
| `shell_terminal_history` | the Terminal keeps its last 200 lines; `!N` runs command N of history again, and says when there is none |
| `shell_terminal_recall` | Up and Down through earlier commands, the line being typed kept, blanks and repeats not kept, editing a recalled line, the last 50, and `history` listing them numbered |
| `shell_terminal_keys` | Ctrl+C gives up the line (shown with ^C, not run or kept, ends a recall), Ctrl+L empties the output and keeps the line, Ctrl+Backspace takes off the last word there and in Notes, Ctrl+U empties the line, `!!` runs the command before (or says there is none) |
| `shell_terminal_complete` | Tab: command names, names in the current folder and in a typed one (absolute, `..`, `.`), a folder gets `/`, several go as far as they agree or are listed, nothing for no match or a missing folder; every command `help` lists completes to itself; a name with a space goes in quotes, and a word begun with a quote completes from inside it |
| `shell_terminal_errors` | Terminal error messages (mv, mkdir, cat, paths through a file), and mv taking the Terminal along with the folder it is in; rm, mkdir and touch with several paths |
| `shell_terminal_touch` | touch preserves existing entries and creates empty files |
| `shell_terminal_write` | write replaces content and handles empty text |
| `shell_terminal_cat_blank` | cat preserves blank lines in files |
| `shell_terminal_cat_big` | cat of a 100,000-line file stays quick |
| `shell_terminal_extra_words` | clear, apps, date and pwd reject extra words |
| `shell_terminal_dash_paths` | write and echo > refuse paths starting with - |
| `shell_terminal_why` | errors name the missing folder or the part that is a file |
| `shell_terminal_slash` | a path ending in / must be a folder |
| `shell_terminal_redirect` | echo redirects and missing destinations |
| `shell_terminal_cursor` | Left, Right, Home and End move the cursor in the line, stopping at its ends; typing, Backspace, Tab and Ctrl+V at it; Return runs the whole line; Up and Ctrl+C put it back at the end; Ctrl+Left and Ctrl+Right by words, Delete and Ctrl+Delete, Ctrl+A, Ctrl+E and Ctrl+K; a click on the line, wrapped too, puts the cursor there and one on the output does nothing; Ctrl+U taking what is before the cursor |
| `shell_terminal_quotes` | quoted words keep their spaces for touch, cat, wc, mkdir, mv, cd, cp, rm and echo >; the other quote inside, a quote inside a word as a letter, an empty quoted word, a quote left open, and a quoted > that is not a redirect; ls, find and wc quoting a name with a space; grep and find with a quoted phrase; Ctrl+V putting a path with a space in quotes |
| `shell_terminal_redirect_errors` | failed redirects and output after clear |
| `shell_terminal_edges` | Terminal path and input boundaries; `sort`, `uniq` and `nl` (an empty file, a last line with no newline), and the line count of `head` and `tail` |
| `shell_terminal_root` | root and normalized path operations |
| `shell_terminal_stale` | Terminal recovers when its current folder is removed |
| `shell_terminal_ls` | Terminal packs directory listings to the window width |
| `shell_terminal_wrap` | Terminal wraps long lines to the window width |
| `shell_terminal_frame` | Terminal builds only the rows that fit, matching a full wrap |
| `shell_terminal_ctrl_backspace_midline` | Ctrl+Backspace in the middle of the line takes off the word before the cursor and keeps the rest; trailing spaces and punctuation after a word go with it |
| `shell_terminal_ctrl_l_cursor` | Ctrl+L in the middle of the line empties the output and keeps the line and the cursor where they were |
| `shell_terminal_recall_edit_down` | editing a recalled line and pressing Down gives back the line being typed, not the edit; Up again gives the newest command |
| `shell_terminal_bang_spaces` | `!!` and `!N` with spaces around them still run, shown as the command resolved; a number out of history is not kept, a longer one is not a bang number and runs as an unknown command |
| `shell_terminal_unknown_kept` | a command that fails is still kept, so `!!` runs it again and it fails again, kept once |
| `shell_terminal_recall_spacing` | the repeat check is on the exact line, so a command with an extra space is kept as a different line |
| `shell_terminal_tab_empty` | Tab on an empty or whitespace-only line changes nothing and lists nothing |
| `shell_terminal_ignored_keys` | Escape, Shift+arrows, Ctrl+W, Alt+Backspace and F1 do nothing in the Terminal, at the end or in the middle of the line |
| `shell_terminal_paste_empty` | Ctrl+V with an empty clipboard pastes nothing and leaves the cursor where it was |
| `shell_help` | Terminal help and app names match the available commands and apps; every command line of help is checked, not only the first three |
| `shell_date` | the date command and its UTC format |
| `shell_terminal_history_words` | history rejects extra words, while history itself still lists every kept command numbered |
| `shell_terminal_help_words` | help ignores extra words and prints the full help |
| `shell_terminal_echo_bare` | echo with no text, or an empty quoted word, prints an empty line |
| `shell_terminal_cp_folder_collision` | cp into a folder that already holds the name refuses and leaves it untouched |
| `shell_terminal_mv_folder_into` | mv moves a folder inside a folder, and refuses when the folder already holds that name |
| `shell_terminal_multipath_errors` | rm, mkdir and touch with several paths keep going after an error for one |
| `shell_terminal_sort_uniq_nl_errors` | sort, uniq and nl on a path ending in /, and nl on a missing file |
| `shell_terminal_head_tail_counts` | head and tail counts: tail 0, leading zeros, over six digits, a letter, a dash count, and a bad count on a missing file |
| `shell_terminal_head_end` | head of a short file prints the same lines as cat and tail, including a blank line in the file and a file that is only a newline, and no blank line after a final newline |
| `shell_terminal_complete_list` | when Tab cannot add more, the list marks a folder with / and quotes a name that has a space |
| `shell_terminal_wc_counts` | wc counts newlines, space-separated words and characters, including a last line with no newline |
| `shell_terminal_cd_home` | cd with no path returns to /home, cd . stays, and cd .. from / stays at / |
| `shell_terminal_ls_file` | ls of a file prints its base name, a quoted path keeps a space in the name, an unquoted space is an extra word, and a missing path is named |
| `shell_terminal_echo_words` | a > that is not the redirect is text, and echo refuses to write into a folder |
| `shell_terminal_append_new` | echo >> creates a missing file and then appends another line |
| `shell_terminal_mv_keep` | mv refuses to replace a file that is already there and leaves both unchanged |
| `shell_terminal_cp_bytes` | cp copies the exact bytes, adds no newline, and will not write over that copy |
| `shell_terminal_rm_full` | rm refuses a folder that is not empty, then removes it once it is empty |
| `shell_terminal_mkdir_deep` | mkdir creates missing parent folders, and a second time says the folder is already there |
| `shell_terminal_grep_dot` | grep matches characters as written: a dot is not a pattern, and case counts |
| `shell_terminal_find_own` | find matches an entry's own name, shows a folder with a slash, and does not match text only in a parent path |
| `shell_terminal_history_keep` | history keeps the last 50 commands, the oldest falls off, and !1 runs whatever is now first |
| `shell_terminal_bang_zero` | !0 is not in history, and !001 runs command 1 |
| `shell_terminal_case_kept` | Echo is unknown, it is kept, and !! runs that same failure again without keeping it twice |
| `shell_terminal_two` | two Terminals share the files and each keeps its own folder |
| `shell_terminal_clear_past` | clear empties the screen and leaves the remembered commands, including clear itself |
| `shell_terminal_cat_mix` | cat reports a folder and still prints a file named after it |
| `shell_terminal_wc_tab` | wc treats a tab as a break between words |
| `shell_terminal_sort_file` | sort orders by character, digits before letters, and does not change the file |
| `shell_terminal_uniq_case` | uniq drops only a line equal to the one just before it, so A and a both stay |
| `shell_terminal_nl_blank` | nl numbers a blank line |
| `shell_terminal_cd_stay` | cd of a file says it is not a folder and stays put |
| `shell_terminal_recall_dups` | a command repeated immediately is kept once, and the same command later is kept again |
| `shell_terminal_up_none` | Up and Down with an empty history leave the line being typed |
| `shell_terminal_delete_end` | Delete at the end of the Terminal line changes nothing, and in the middle removes the next character |
| `shell_terminal_word_ends` | Ctrl+Right at the end of the line and Ctrl+Left at the start leave the cursor there |
| `shell_terminal_quote_open` | a quote left open runs nothing and names the missing quote |
| `shell_terminal_write_join` | write joins the words after the path, needs a path, and a path with no words writes a blank line |
| `shell_terminal_paste_line` | Ctrl+V in the Terminal pastes only the first line of the clipboard |
| `shell_terminal_ls_dot` | ls . lists the current folder and ls .. lists the parent |
| `shell_terminal_root_ls` | cd / then pwd prints /, and ls shows home and tmp |

### Files

| Test | What it covers |
|---|---|
| `shell_files_click` | clicking rows in Files |
| `shell_files_back` | Backspace and ".." select the folder you came from |
| `shell_files_double_click` | the second click of a double-click is ignored |
| `shell_files_boundaries` | root, empty folders, unusual names and reopening Files |
| `shell_files_long_names` | clipped names open the full path and deleted selections do not open replacements |
| `shell_files_title` | Files keeps the end of a long folder path in its title |
| `shell_files_keys` | Home, End, and a letter or digit going to the next name with it (any case, round, never `..`), the root, an empty folder, Page Up and Page Down by a window of rows less one, Ctrl+Home and Ctrl+End, Left going up a folder and Right going into the selected one only; Ctrl+C copying the selected path; Delete asking, removing a file or an empty folder (not one with files in it, not `..`) and keeping the selection on its line; a long name cut in the question |
| `shell_files_hidden` | clicks below the visible Files rows do nothing |
| `shell_files_stale` | Files when another app removed the selected file |
| `shell_files_ancestor` | Files and Terminal recover after an ancestor folder moves |
| `shell_files_selection` | Files keeps its selection across directory changes |
| `shell_files_changed_click` | Files ignores a click on rows changed since drawing |
| `shell_files_rename` | F2 renames a file or a folder (with what is in it) and keeps it selected; not over a name that is there, not to a name with /, Esc, the same name and ..; a long name showing its end, a click or another key giving up a rename, a click a Delete question; the next Editor's file follows a rename or a Terminal mv |
| `shell_files_resize_click` | Files waits for a redraw after a resize before accepting a row click |
| `shell_files_up_down` | Up and Down move one row at a time and stop at the first and last row |
| `shell_files_scroll` | a long list scrolls just far enough to keep the selected row in view, the title stays first, and Home shows the first rows again |
| `shell_files_open_editor` | opening a file sets the next Editor's file without leaving the folder, and entering a folder leaves that file alone |
| `shell_files_rename_edit` | F2 rename editing: Ctrl+Backspace drops the last word, Ctrl+U clears, Backspace on empty does nothing, Space inserts, Ctrl+V pastes the clipboard line |
| `shell_files_rename_reject` | F2 rename refusals: an empty, dot, or dotdot name, a name that only differs by spaces, and a file removed meanwhile |
| `shell_files_delete_empty` | Delete removes an empty folder and keeps the selection on its line, next name or the one before for the last row |
| `shell_files_copy_file` | Ctrl+C copies a file's full path, to paste into Notes |
| `shell_files_click_scrolled` | a click on a visible row of a scrolled list opens the row shown there |
| `shell_files_jump_symbol` | jump-to-letter works for a name starting with a symbol, going round to the top |
| `shell_files_delete_esc` | Escape gives up a Delete question without removing the file, and a second Escape is not taken |
| `shell_files_empty_root` | an empty root has no rows, and letters, arrows, Delete, F2 and Return change nothing |
| `shell_files_delete_gone` | a second Delete after the file is already gone does not remove the row that took its place |
| `shell_files_two_windows` | two Files windows keep their own folders, and Down in one leaves the other alone |
| `shell_files_copy_dir` | Ctrl+C on a folder copies its path with no slash, and on .. it copies nothing |
| `shell_files_right_stay` | Right enters a folder and does nothing on a file or on .. |
| `shell_files_left_root` | Left at / does not move |
| `shell_files_f2_up` | F2 on .. does not start a rename |
| `shell_files_rename_dir` | renaming a folder keeps what is inside it and leaves that folder selected |
| `shell_files_delete_jump` | a letter gives up a Delete question and jumps to that name, and the file stays |
| `shell_files_page_ends` | Page Up on the first row and Page Down on the last row stay there |
| `shell_files_jump_same` | the only name starting with a letter stays selected when that letter is pressed again |
| `shell_files_sees_new` | a file written by another app shows up on the next draw, and the selection stays on its name |
| `shell_files_sorted` | names are shown in order, with .. first |
| `shell_files_dotfile` | a name that starts with a dot is listed |
| `shell_files_delete_last` | deleting the last row leaves the selection on the row before it |
| `shell_files_rename_title_click` | a click on the title gives up a rename and does not open a row |
| `shell_files_note_next` | the already-there note from a rename clears on the next key |

### Editor

| Test | What it covers |
|---|---|
| `shell_clipboard` | Ctrl+C, Ctrl+X and Ctrl+V in the Editor and the IDE (no selection, over a selection, one undo step each), and the first line pasted into Notes, the Terminal and an IDE run waiting for input; Notes copying and cutting its whole line |
| `shell_clipboard_keep` | Copying or cutting with nothing selected leaves the clipboard and the undo stack alone, and pasting an empty clipboard is no edit |
| `shell_editor_clipboard_ide` | Text copied in the Editor pastes in full into the IDE buffer, in one undo step |
| `shell_editor_paste_undo` | Pasting over a selection and cutting several lines are each one undo step, undone and redone whole |
| `shell_editor_redo_after_save` | Saving does not clear undo or redo: a save writes the undone text and Ctrl+Y still redoes it |
| `shell_editor_save_newfile_warn` | A new file saved once is then guarded like any other file against changes by another app |
| `shell_editor_find` | Ctrl+F and Return select the next match after the cursor and go round, case counts, not found, Esc and other keys stop finding, in the IDE too; F3 and Shift+F3 again, both ways round; a selection on one line as the text to find, replaced by typing; Ctrl+H replacing every match in one undo step, with nothing, not found, Esc halfway, and starting with a selection; Return with no text waits; a long text showing its end; a click giving up a find or a line number |
| `shell_editor_goto` | Ctrl+G and a number go to the start of that line, the last past the end, 0 as 1; digits only, Esc and other keys give up, a selection goes |
| `shell_editor_indent` | Return keeps leading spaces up to the cursor, the IDE adds a level after a block line but not after `fun f() = ...`, undo |
| `shell_editor_word_keys` | Ctrl+Home and Ctrl+End go to the start and end of the file and drop the selection; Ctrl+Backspace and Ctrl+Delete remove a word, the selection, or nothing at the ends; Home stops after the leading spaces, then goes to the very start; Page Up and Page Down by the shown lines less one, Shift selecting; Ctrl+L selecting lines, from a selection made upwards too; Ctrl+D copying a line or the selected lines, and Ctrl+K removing them, each one undo, and only the selected line after Ctrl+L, the copy staying selected; Ctrl+J joining lines, or all the selected ones; Ctrl+] and Ctrl+[ indenting and taking it off, on the selected lines too; Ctrl+Up and Ctrl+Down moving a line or the selected lines |
| `shell_editor_tab` | Tab types spaces to the next multiple of 4, over a selection, one undo step, in the IDE too; Shift+Tab takes an indent off and keeps the cursor on its character; Backspace in leading spaces goes back one indent, elsewhere one character |
| `shell_editor_title` | Editor title keeps the file name and the status in view |
| `shell_editor_open_status` | Editor status on opening: open, new file, or why not |
| `shell_editor_stale` | Editor reports a file removed before opening |
| `shell_editor_edges` | Editor empty buffers, line edges and failed saves |
| `shell_editor_disk_changed` | Ctrl+S warns once when another app changed the file |
| `shell_editor_disk_warn_keys` | Ctrl+S warns again when a cursor move or selection key comes between the warning and the next save |
| `shell_editor_disk_click` | a click or a drag between the warning and the next Ctrl+S makes that save warn again, and a second Ctrl+S with nothing in between still overwrites |
| `shell_editor_undo` | Ctrl+Z undoes edits one step at a time, up to 500, and Ctrl+Y redoes them until the next edit |
| `shell_editor_save_status` | Editor status through save, undo and redo: saved again with nothing new, undone, redone, and nothing to undo or redo past the end |
| `shell_editor_escape` | Esc drops a selection in the Editor and the IDE and is taken, with none it is not; the IDE stops a waiting run first |
| `shell_editor_select` | Shift+arrows and Ctrl+A select; typing and Backspace replace the selection |
| `shell_editor_click` | a click puts the cursor on the character clicked (the `_` not counted), at the end past a line's end, from what shows of a line cut on the left; the title, a click below the text, the IDE's pane and a waiting run do nothing; press and drag selects, above and below the text too; a double-click selects a word, a triple-click the line; in the IDE a click on the error or its header goes to its line; a key during a drag ends it |
| `shell_editor_cursor` | arrows, Home, End and Ctrl+arrow word jumps move the cursor, and which keys Ctrl and Shift together give |
| `shell_editor_delete` | Delete removes the next character or the selection; Ctrl+Z puts it back |
| `shell_editor_long_line` | long-line clipping, ignored movement and saving the full buffer |
| `shell_editor_replaced` | saving after a file is removed or replaced by a folder |
| `shell_editor_backspace_join` | Backspace at a line start joins it to the line before, at the file start it does nothing, and one Ctrl+Z puts the lines back |
| `shell_editor_word_across_lines` | Ctrl+Right and Ctrl+Left word jumps cross newlines and punctuation, and stay put at the ends of the file |
| `shell_editor_up_down_column` | Up and Down keep the column, go to the end of a shorter line, and do not remember the column when returning to a longer line; Up on the first line goes to its start, Down on the last line to its end |
| `shell_editor_shift_end_page` | Shift+End selects to the line end, a plain End drops the selection, and Shift+Page Up selects a page up |
| `shell_editor_replace_overlap` | Ctrl+H replaces non-overlapping matches in one pass, and a replacement containing the text does not get replaced again |
| `shell_editor_find_prev_selection` | Shift+F3 finds the match before the selection start and goes round to the last match, and before the cursor with no selection |
| `shell_editor_goto_leading_zeros` | Ctrl+G takes leading zeros in the line number and at most 7 digits, so a huge number lands on the last line |
| `shell_editor_type_over_multiline` | Typing, Return and Backspace over a selection spanning lines replace the whole selection |
| `shell_big_file` | the Editor on a file of thousands of lines stays quick |
| `shell_last_lines` | Editor line splitting at empty and trailing newline boundaries |
| `shell_last_lines_long` | the Editor on a 200,000-character line stays quick |
| `shell_editor_join_end` | Ctrl+J at the end of the file is not an edit |
| `shell_editor_move_ends` | Ctrl+Up on the first line and Ctrl+Down on the last line are not edits |
| `shell_editor_kill_only` | Ctrl+K removes the only line, and one Ctrl+Z puts it back |
| `shell_editor_dup_twice` | Ctrl+D again copies the copy |
| `shell_editor_home_twice` | Home goes to the first character after the indent, and Home again goes to the start |
| `shell_editor_word_hyphen` | a hyphen is not part of a word, so Ctrl+Left stops on each side of it |
| `shell_editor_word_unicode` | a character past ASCII is part of a word |
| `shell_editor_tab_stops` | Tab inserts spaces to the next multiple of 4 |
| `shell_editor_dedent_none` | Shift+Tab at column 0 is not an edit |
| `shell_editor_indent_empty` | Ctrl+] on an empty line inserts four spaces |
| `shell_editor_indent_blanks` | Ctrl+] with a selection skips empty lines and indents the others in one undo step |
| `shell_editor_replace_empty` | replacing with nothing removes every match, in one undo step |
| `shell_editor_f3_none` | F3 and Shift+F3 with no text found yet change nothing |
| `shell_editor_escape_sel` | Escape drops a selection and is taken, and with no selection it is not taken |
| `shell_editor_paste_all` | pasting in the Editor keeps every line of the clipboard |
| `shell_editor_two_buffers` | two Editor windows undo on their own |
| `shell_editor_save_fresh` | Ctrl+S creates a file that was not there |
| `shell_editor_save_noparent` | Ctrl+S says the folder is missing and writes nothing |
| `shell_editor_backspace_start` | Backspace at the start of the file is not an edit |
| `shell_editor_delete_end` | Delete at the end of the file is not an edit |

### IDE

| Test | What it covers |
|---|---|
| `shell_ide` | IDE: run with Ctrl+R, output pane, error line and Ctrl+E, stopped loops, refused host calls, `use` of desktop files, input lines, Ctrl+Backspace there, Esc or Ctrl+C to stop, F5 like Ctrl+R; Ctrl+Return running like Ctrl+R; the input line's cursor (Left, Right, Home, End, Delete), Return sending the whole line, word keys and Ctrl+K, a wide line keeping the cursor in view |
| `shell_ide_comment` | Ctrl+/ puts `# ` in after the leading spaces and takes it (or a bare `#`) out, the cursor staying on its character, one undo step each; the Editor ignores it; with a selection, every line it is on in one step, not the line after a Ctrl+L |
| `shell_ide_comment_indent` | uncommenting keeps a cursor that is still in the indent on that space, and a cursor on a later character stays on it |
| `shell_ide_comment_blank` | a selection of only blank lines is not an undo step and does not mark the buffer edited; a blank line with no selection still gets a comment |
| `shell_ide_error_click` | IDE: a click on the error line or on the pane header goes to the error's line, as Ctrl+E does; a click on a plain output line moves nothing |
| `shell_ide_input_paste` | IDE input: Ctrl+V adds the first line of the clipboard only, and with an empty clipboard it adds nothing |
| `shell_ide_denied` | IDE: refused host calls beyond exit and writing: sleeping, removing, renaming and making folders, and opening a graphics window; a refused remove leaves the file, a refused make_dir makes nothing |
| `shell_ide_module_saved` | IDE: a `use` of another file reads it as last saved; an unsaved edit in another window changes nothing until it is saved |
| `shell_ide_syntax_jump` | IDE: Ctrl+E goes to a syntax error's line too, and after a good run, when there is no error, Ctrl+E moves nothing |
| `shell_ide_module_error` | an error inside a module the program used shows that module's path and line, and Ctrl+E leaves the cursor where it was |
| `shell_ide_page_pane` | Page Down moves by the editor rows above the output pane, and Page Up comes back |
| `shell_ide_disk_keys` | Ctrl+R, F5, Ctrl+E, Ctrl+/ and a key typed while a run waits cancel the changed-on-disk warning; two Ctrl+S presses with nothing between them still overwrite |

### Paint

| Test | What it covers |
|---|---|
| `shell_paint_edges` | Paint: a key while a stroke or shape is held ends it, so Ctrl+Z then a move draws nothing back; `c` on a blank canvas is not an undo step; Ctrl+V, Ctrl+Backspace and Ctrl+U while typing a name, a long name showing its end, and a click giving up the name |
| `shell_paint` | Paint: a drag with no gaps, the fill tool (side by side only, no-op fills, undo), the line, rectangle and ellipse tools, outline and filled (the shape follows the drag, its end stays on the canvas, one undo step, brush size), save as (a typed name, `.paint` added, whole paths, Esc, no name, a folder, a file that is not a picture, a folder that is not there), swatches and keys, brush sizes (also with [ and ]), the eraser, undo, redo and clear, a stroke off the canvas and back, boxes cut to the window, save and open again from Files, a file that is not a picture, another size, a failed save; the i color picker (the tool before comes back, no undo step); x swapping back to the color before |
| `shell_paint_default_file` | Paint: after Files opens a file that is not a picture, a new Paint window falls back to /home/picture.paint as a new file |
| `shell_paint_unknown_digits` | Paint: digits outside 0 to 8 in a picture file read as white, while valid digits keep their colors |
| `shell_paint_equal_size` | Paint: = grows the brush like + and ], stopping at size 4 |
| `shell_paint_brush_centering` | Paint: a size 2 brush dot covers its cell and the ones right and below, a size 4 dot one up and left and two right and below |
| `shell_paint_undo_cap` | Paint: undo keeps at most 20 steps |
| `shell_paint_large_picture` | Paint: a picture bigger than the canvas opens with only the part that fits |
| `shell_paint_pick_white` | Paint: the picker on a white cell picks the eraser, with the tool before back and no undo step |
| `shell_paint_line_thick` | Paint: a line with a bigger brush is that many cells thick, still one undo step |

### Snake

| Test | What it covers |
|---|---|
| `shell_snake` | Snake: no move before a key, the beat, no turning back, two turns in one step, pause without catching up (Space or P), no move while another window is focused, eating and growing, speed, the wall, its own body, keys after the end, a new game (R or Return), the best score saved in the files and read back (junk reads as 0); N starting a new game mid-game or paused |
| `shell_snake_speed_floor` | Snake: at score 20 the step interval stays at its 70 ms floor, with no move at 69 ms and one move at 70 ms |
| `shell_snake_win` | Snake: eating the last free cell fills the board and wins, with no food left and the win help line |
| `shell_snake_lowercase_wasd` | Snake: lowercase w, a, s, d turn like the arrows, and a turn straight back is ignored |
| `shell_snake_best_empty` | Snake: an empty best-score file reads as 0, a padded number as that number |
| `shell_snake_minimized` | Snake: a minimized window does not move, and the beat restarts on return instead of catching up |

### Shared filesystem and fuzzing

| Test | What it covers |
|---|---|
| `shell_shared_desktops` | shared filesystem and Editor path across desktop maps |
| `shell_fuzz` | random input against the window model, checking invariants each step |
| `shell_apps_fuzz` | random Terminal commands with Files and Editor on the same filesystem |
| `shell_events_fuzz` | random input for all eight apps (their keys, find, replace, go-to, the Editor line keys, Files rename and the Terminal line keys among them, double and triple clicks, drags, clock ticks, Escape): nothing fails, lines fit, boxes stay in the window, and the Editor and IDE cursor and selection stay in their text |
