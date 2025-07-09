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
/*!        \file  my_interface_provider.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef TEST_MY_INTERFACE_PROVIDER_H
#define TEST_MY_INTERFACE_PROVIDER_H

#include <functional>

#include "vaf/future.h"
#include "vaf/result.h"
#include "vaf/data_ptr.h"

#include "test/my_function.h"
#include <cstdint>

namespace test {

class MyInterfaceProvider {
public:
  virtual ~MyInterfaceProvider() = default;

  virtual ::vaf::Result<::vaf::DataPtr<std::uint64_t>> Allocate_my_data_element() = 0;
  virtual ::vaf::Result<void> SetAllocated_my_data_element(::vaf::DataPtr<std::uint64_t>&& data) = 0;
  virtual ::vaf::Result<void> Set_my_data_element(const std::uint64_t& data) = 0;

  virtual void RegisterOperationHandler_my_function(std::function<test::my_function::Output(const std::uint64_t&, const std::uint64_t&)>&& f) = 0;
  virtual void RegisterOperationHandler_my_function_void(std::function<void(const std::uint64_t&)>&& f) = 0;
};

} // namespace test

#endif // TEST_MY_INTERFACE_PROVIDER_H
