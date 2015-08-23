cmake_minimum_required (VERSION 2.6)
project (logger)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Release")
endif(NOT CMAKE_BUILD_TYPE)

include(FindPkgConfig)
pkg_check_modules(LIBGPS REQUIRED libgps)
include_directories(${LIBGPS_INCLUDE_DIRS})
link_directories(${LIBGPS_LIBRARY_DIRS})

add_executable (logger logger.cpp)
target_link_libraries(logger ${LIBGPS_LIBRARIES})

#Messages
message("")
message("-- Summary:")
message("* Compilation type: CMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}")
message("")