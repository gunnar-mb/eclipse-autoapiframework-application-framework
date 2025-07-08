/*!********************************************************************************************************************
 *  COPYRIGHT
 *  -------------------------------------------------------------------------------------------------------------------
 *  \verbatim
 *  Copyright (c) 2025 by Vector Informatik GmbH. All rights reserved.
 *
 *                This software is copyright protected and proprietary to Vector Informatik GmbH.
 *                Vector Informatik GmbH grants to you only those rights as set out in the license conditions.
 *                All other rights remain with Vector Informatik GmbH.
 *  \endverbatim
 *  -------------------------------------------------------------------------------------------------------------------
 *  FILE DESCRIPTION
 *  -----------------------------------------------------------------------------------------------------------------*/
/*!        \file  main.cpp
 *         \brief
 *
 *********************************************************************************************************************/
#include "gtest/gtest.h"
#include <iostream>
#include <fstream>

int main(int argc, char **argv) {
  int gtest_ret{0};
  ::testing::InitGoogleTest(&argc, argv);

  // Set death tests to threadsafe globally because logging uses a separate thread.
  //::testing::FLAGS_gtest_death_test_style = "threadsafe";

  // Execute tests via gtest
  gtest_ret = RUN_ALL_TESTS();

  return gtest_ret;
}
