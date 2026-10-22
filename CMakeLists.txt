cmake_minimum_required(VERSION 3.16)
project(m0n0lith2 VERSION 0.1.0 LANGUAGES NONE)

# M0N0LITH-2 is written in Relic. Build Relic from the relic/ submodule first
# (see README.md), or pass -DRELIC_EXE=/path/to/relic.
find_program(RELIC_EXE NAMES relic
  PATHS ${CMAKE_SOURCE_DIR}/relic/build/Release ${CMAKE_SOURCE_DIR}/relic/build
  NO_DEFAULT_PATH)
if(NOT RELIC_EXE)
  message(FATAL_ERROR "relic not found. Build it with: cmake -S relic -B relic/build -DRELIC_BUILD_HOST=ON && cmake --build relic/build")
endif()
message(STATUS "Using relic: ${RELIC_EXE}")

enable_testing()

# Golden tests: tests/name.relic runs and its stdout must match tests/name.out.
file(GLOB GOLDEN_TESTS ${CMAKE_SOURCE_DIR}/tests/*.relic)
foreach(t ${GOLDEN_TESTS})
  get_filename_component(name ${t} NAME_WE)
  add_test(NAME golden_${name}
    COMMAND ${CMAKE_COMMAND} -DRELIC=${RELIC_EXE} -DTEST=${t}
      -P ${CMAKE_SOURCE_DIR}/tools/run_golden.cmake)
endforeach()

# Every shell file must pass relic check (no syntax errors or undefined names).
# desktop.relic needs SDL to run, but check does not run it.
add_test(NAME check_shell
  COMMAND ${RELIC_EXE} check wm.relic desktop.relic
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/shell)
