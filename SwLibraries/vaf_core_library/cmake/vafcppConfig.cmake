# vafcppConfig.cmake

# Load the target export set
include("${CMAKE_CURRENT_LIST_DIR}/vafcppTargets.cmake")

# Optional: Set variables that point to installed directories
set(vafcpp_INCLUDE_DIRS "${CMAKE_CURRENT_LIST_DIR}/../../include")
set(vafcpp_LIBRARIES vafcpp::vaf_core)
