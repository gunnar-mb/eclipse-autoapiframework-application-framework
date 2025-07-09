#[=======================================================================[
  COPYRIGHT
  -------------------------------------------------------------------------------------------------------------------

  Copyright (c) 2025 by Vector Informatik GmbH. All rights reserved.

                This software is copyright protected and proprietary to Vector Informatik GmbH.
                Vector Informatik GmbH grants to you only those rights as set out in the license conditions.
                All other rights remain with Vector Informatik GmbH.

  -------------------------------------------------------------------------------------------------------------------
  FILE DESCRIPTION
  -------------------------------------------------------------------------------------------------------------------
        \file    CMakeLists.txt
#]=======================================================================]
cmake_minimum_required(VERSION 3.21)

find_package(Threads)
find_package(GTest)

set(TARGET sensor_fusion)

add_library(${TARGET} STATIC "")

target_compile_options(${TARGET}
  PRIVATE
    $<$<AND:$<PLATFORM_ID:Linux>,$<C_COMPILER_ID:GNU>>:-Wall>
    $<$<AND:$<PLATFORM_ID:Linux>,$<C_COMPILER_ID:GNU>>:-Wextra>
    $<$<AND:$<PLATFORM_ID:Linux>,$<C_COMPILER_ID:GNU>>:-Wshadow>
    $<$<AND:$<PLATFORM_ID:Linux>,$<C_COMPILER_ID:GNU>>:-Wnon-virtual-dtor>
    $<$<AND:$<PLATFORM_ID:Linux>,$<C_COMPILER_ID:GNU>>:-Wold-style-cast>
    $<$<AND:$<PLATFORM_ID:Linux>,$<C_COMPILER_ID:GNU>>:-Wcast-align>
    $<$<AND:$<PLATFORM_ID:Linux>,$<C_COMPILER_ID:GNU>>:-Wunused>
    $<$<AND:$<PLATFORM_ID:Linux>,$<C_COMPILER_ID:GNU>>:-Woverloaded-virtual>
    $<$<AND:$<PLATFORM_ID:Linux>,$<C_COMPILER_ID:GNU>>:-pedantic>
    $<$<AND:$<PLATFORM_ID:Linux>,$<C_COMPILER_ID:GNU>>:-Wconversion>
    $<$<AND:$<PLATFORM_ID:Linux>,$<C_COMPILER_ID:GNU>>:-Wsign-conversion>)

target_compile_features(${TARGET} PUBLIC cxx_std_14)

target_compile_definitions(${TARGET} PUBLIC)

target_include_directories(${TARGET}
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
    $<INSTALL_INTERFACE:include>
  PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src)

target_sources(${TARGET}
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/include/nsapplicationunit/nssensorfusion/sensor_fusion.h
        ${CMAKE_CURRENT_SOURCE_DIR}/src/sensor_fusion.cpp
    )

# cmake-format: off
target_link_libraries(${TARGET}
  PUBLIC
    Threads::Threads
    $<IF:$<TARGET_EXISTS:vafcpp::vaf_core>,vafcpp::vaf_core,vaf_core>
    vaf_module_interfaces

    vaf_new_target_1
    vaf_new_target_2
)
# cmake-format: on

if(VAF_BUILD_TESTS)
add_subdirectory(test)
endif()
