# Golden test runner. Usage:
#   cmake -DRELIC=path/to/relic -DTEST=tests/name.relic -P tools/run_golden.cmake
# Runs the program from its own folder, and its stdout must match name.out
# (empty if there is none) with exit code 0. Based on Relic's runner, without
# the REPL, .args and .err cases, which no test here uses.
get_filename_component(dir ${TEST} DIRECTORY)
get_filename_component(name ${TEST} NAME_WE)
set(run_dir "${dir}")
if(name MATCHES "^shell_workspace_")
  include(${CMAKE_CURRENT_LIST_DIR}/workspace_temp.cmake)
  workspace_temp(run_dir)
endif()
set(run_test "${TEST}")
if(name MATCHES "^shell_workspace_io_")
  # Exercise the production module with deterministic host I/O failures.
  # Only its std/files import changes; the module itself has no test hooks.
  get_filename_component(root "${dir}" DIRECTORY)
  file(MAKE_DIRECTORY "${run_dir}/shell" "${run_dir}/tests" "${run_dir}/tools/workspace")
  file(READ "${root}/shell/workspace.relic" source)
  string(REPLACE "use std/files\n" "use ../tools/workspace/io_files as files\n" source "${source}")
  file(WRITE "${run_dir}/shell/workspace.relic" "${source}")
  configure_file("${root}/tools/workspace/io_files.relic" "${run_dir}/tools/workspace/io_files.relic" COPYONLY)
  set(run_test "${run_dir}/tests/${name}.relic")
  configure_file("${TEST}" "${run_test}" COPYONLY)
endif()
if(name STREQUAL "shell_workspace_environment")
  include(${CMAKE_CURRENT_LIST_DIR}/run_workspace_environment.cmake)
else()
  execute_process(
    COMMAND ${RELIC} ${run_test}
    WORKING_DIRECTORY ${run_dir}
    OUTPUT_VARIABLE out
    ERROR_VARIABLE err
    RESULT_VARIABLE code)
endif()
if(name MATCHES "^shell_workspace_")
  file(REMOVE_RECURSE "${run_dir}")
endif()
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
