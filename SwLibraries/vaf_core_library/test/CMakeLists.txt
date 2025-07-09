add_executable(test)
target_sources(test PRIVATE "${CMAKE_CURRENT_LIST_DIR}/src/test.cpp")
target_link_libraries(test PRIVATE vaf_core)