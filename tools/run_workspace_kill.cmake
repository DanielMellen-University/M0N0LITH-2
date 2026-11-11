# A committed workspace, then a second process killed after it has written a
# partial and before it can publish. The third process must see the commit.
if(NOT RELIC OR NOT ROOT OR NOT BUILD)
  message(FATAL_ERROR "RELIC, ROOT and BUILD are required")
endif()
include(${CMAKE_CURRENT_LIST_DIR}/workspace_temp.cmake)
workspace_temp(dir)

execute_process(
  COMMAND ${RELIC} ${ROOT}/tools/workspace/kill_setup.relic ${dir}
  WORKING_DIRECTORY ${ROOT}
  OUTPUT_VARIABLE setup_out
  ERROR_VARIABLE setup_err
  RESULT_VARIABLE setup_code)
if(NOT setup_code EQUAL 0)
  message(FATAL_ERROR "kill_setup: exit ${setup_code}\n${setup_err}\n${setup_out}")
endif()
if(NOT setup_out STREQUAL "setup [\"kept\\n\"] [\"\"]\n")
  message(FATAL_ERROR "kill_setup:\n${setup_out}")
endif()

execute_process(
  COMMAND ${RELIC} ${ROOT}/tools/workspace/kill_hang.relic ${dir}
  WORKING_DIRECTORY ${ROOT}
  TIMEOUT 5
  OUTPUT_VARIABLE hang_out
  ERROR_VARIABLE hang_err
  RESULT_VARIABLE hang_code)
if(NOT EXISTS "${dir}/HUNG")
  message(FATAL_ERROR "kill_hang did not write HUNG (code ${hang_code})\n${hang_err}\n${hang_out}")
endif()

execute_process(
  COMMAND ${RELIC} ${ROOT}/tools/workspace/kill_read.relic ${dir}
  WORKING_DIRECTORY ${ROOT}
  OUTPUT_VARIABLE read_out
  ERROR_VARIABLE read_err
  RESULT_VARIABLE read_code)
if(NOT read_code EQUAL 0)
  message(FATAL_ERROR "kill_read: exit ${read_code}\n${read_err}\n${read_out}")
endif()
set(want "notice [\"workspace: ignored partial g99\"]
file [\"kept\\n\"]
partial true
windows 1
")
if(NOT read_out STREQUAL want)
  message(FATAL_ERROR "kill_read:\n--- got\n${read_out}--- want\n${want}")
endif()
file(REMOVE_RECURSE "${dir}")
