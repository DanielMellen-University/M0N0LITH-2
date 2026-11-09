# Two relic processes, then a torn pointer and a fourth process.
# The expected text is what read_session and recover_session print.
if(NOT RELIC OR NOT ROOT OR NOT BUILD)
  message(FATAL_ERROR "RELIC, ROOT and BUILD are required")
endif()
set(dir "${BUILD}/workspace-restart")
file(REMOVE_RECURSE "${dir}")
file(MAKE_DIRECTORY "${dir}")

function(run_phase script)
  execute_process(
    COMMAND ${RELIC} ${ROOT}/tools/workspace/${script}.relic ${dir}
    WORKING_DIRECTORY ${ROOT}
    OUTPUT_VARIABLE out
    ERROR_VARIABLE err
    RESULT_VARIABLE code)
  if(NOT code EQUAL 0)
    message(FATAL_ERROR "${script}: exit ${code}\n${err}\n${out}")
  endif()
  set(phase_out "${out}" PARENT_SCOPE)
endfunction()

run_phase(write_session)
if(NOT phase_out STREQUAL "wrote saved [\"\"]\n")
  message(FATAL_ERROR "write_session:\n${phase_out}")
endif()

run_phase(read_session)
set(want_read "notice [\"\"]
Terminal. Type help.
/home> cat note.txt
session-note
!
/home> cat docs/plan.txt
alpha
beta
/home> cat hello.relic
print(\"ide-out\")
/home> ls
docs/  hello.relic  note.txt
renamed.txt
files [\"Files: /home\", \"> ..\", \"  docs/\", \"  hello.relic\", \"  note.txt\", \"  renamed.txt\"]
editor open [\"session-note\\n!\"]
ide ran [\"ide-out\"]
notes [\"Type something:\", \"_\"]
clicker Clicks: 0
")
if(NOT phase_out STREQUAL want_read)
  message(FATAL_ERROR "read_session:\n--- got\n${phase_out}--- want\n${want_read}")
endif()

run_phase(fault_session)
if(NOT phase_out STREQUAL "fault [\"workspace: save failed (torn-pointer); kept g9\"]\n")
  message(FATAL_ERROR "fault_session:\n${phase_out}")
endif()

run_phase(recover_session)
set(want_recover "notice [\"workspace: pointer invalid; recovered g9\"]
Terminal. Type help.
/home> cat note.txt
session-note
!
/home> cat lost.txt
cat: not found: /home/lost.txt
lost false
")
if(NOT phase_out STREQUAL want_recover)
  message(FATAL_ERROR "recover_session:\n--- got\n${phase_out}--- want\n${want_recover}")
endif()
