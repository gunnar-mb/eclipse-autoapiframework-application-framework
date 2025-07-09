find_package(Threads)

include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

set(TARGET vaf_core)
add_library(${TARGET} STATIC)
target_sources(
        ${TARGET}
        PRIVATE "${CMAKE_CURRENT_LIST_DIR}/include/vaf/receiver_handler_container.h"
        "${CMAKE_CURRENT_LIST_DIR}/include/vaf/controller_interface.h"
        "${CMAKE_CURRENT_LIST_DIR}/include/vaf/executable_controller_base.h"
        "${CMAKE_CURRENT_LIST_DIR}/include/vaf/future.h"
        "${CMAKE_CURRENT_LIST_DIR}/include/vaf/result.h"
        "${CMAKE_CURRENT_LIST_DIR}/include/vaf/data_ptr.h"
        "${CMAKE_CURRENT_LIST_DIR}/src/controller_interface.cpp"
        "${CMAKE_CURRENT_LIST_DIR}/src/executable_controller_base.cpp"
        "${CMAKE_CURRENT_LIST_DIR}/src/executor.cpp"
        "${CMAKE_CURRENT_LIST_DIR}/src/logging.cpp"
        "${CMAKE_CURRENT_LIST_DIR}/src/runtime.cpp")

target_include_directories(
        ${TARGET} PUBLIC "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
        "$<INSTALL_INTERFACE:include>")

install(
        TARGETS ${TARGET}
        EXPORT ${PROJECT_NAME}Targets
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})

install(
        DIRECTORY "${CMAKE_CURRENT_LIST_DIR}/include/"
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
        FILES_MATCHING
        PATTERN "*.h*")

install(
        EXPORT ${PROJECT_NAME}Targets
        FILE ${PROJECT_NAME}Targets.cmake
        NAMESPACE vafcpp::
        DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/${PROJECT_NAME})

install(FILES "${CMAKE_CURRENT_LIST_DIR}/../cmake/${PROJECT_NAME}Config.cmake"
        DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/${PROJECT_NAME})
