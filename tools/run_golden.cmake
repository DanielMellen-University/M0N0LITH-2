# Golden test runner. Usage:
#   cmake -DRELIC=path/to/relic -DTEST=tests/name.relic -P tools/run_golden.cmake
# Runs the program from its own folder, and its stdout must match name.out
# (empty if there is none) with exit code 0. Based on Relic's runner, without
# the REPL, .args and .err cases, which no test here uses.
get_filename_component(dir ${TEST} DIRECTORY)
get_filename_component(name ${TEST} NAME_WE)
execute_process(
  COMMAND ${RELIC} ${TEST}
  WORKING_DIRECTORY ${dir}
  OUTPUT_VARIABLE out
  ERROR_VARIABLE err
  RESULT_VARIABLE code)
string(REPLACE "\r\n" "\n" out "${out}")
set(want "")
if(EXISTS ${dir}/${name}.out)
  file(READ ${dir}/${name}.out want)
  string(REPLACE "\r\n" "\n" want "${want}")
endif()
if(NOT code EQUAL 0)
  message(FATAL_ERROR "${name}: exit ${code}\n${err}")
endif()
if(NOT out STREQUAL want)
  message(FATAL_ERROR "${name}: stdout mismatch\n--- want\n${want}--- got\n${out}")
endif()
