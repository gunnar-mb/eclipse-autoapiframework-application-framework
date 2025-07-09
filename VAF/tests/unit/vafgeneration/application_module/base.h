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
/*!        \file  my_application_module_base.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef APPS_MY_APPLICATION_MODULE_BASE_H
#define APPS_MY_APPLICATION_MODULE_BASE_H

#include <memory>

#include "vaf/executor.h"
#include "vaf/executable_controller_interface.h"
#include "vaf/controller_interface.h"

#include "test/my_interface_consumer.h"
#include "test/my_interface_provider.h"

namespace apps {

class MyApplicationModuleBase : public vaf::ControlInterface {
 public:
  struct ConstructorToken {
    std::string name_;
    std::vector<std::string> dependencies_;
    vaf::ExecutableControllerInterface& executable_controller_interface_;
    vaf::Executor& executor_;
    std::shared_ptr<test::MyInterfaceConsumer> c_interface_instance_1_;
    std::shared_ptr<test::MyInterfaceConsumer> c_interface_instance_2_;
    std::shared_ptr<test::MyInterfaceProvider> p_interface_instance_1_;
    std::shared_ptr<test::MyInterfaceProvider> p_interface_instance_2_;
    uint64_t task_offset_task1_;
    std::chrono::nanoseconds task_budget_task1_;
    uint64_t task_offset_task2_;
    std::chrono::nanoseconds task_budget_task2_;
  };

  MyApplicationModuleBase(ConstructorToken&& token);
  virtual ~MyApplicationModuleBase() = default;

  virtual vaf::Result<void> Init() noexcept { return vaf::Result<void>{}; }
  virtual void Start() noexcept { ReportOperational(); }
  virtual void Stop() noexcept {}
  virtual void DeInit() noexcept {}

  virtual void OnError(const vaf::Error& error) override { static_cast<void>(error); }

  virtual void task1() = 0;
  virtual void task2() = 0;

 protected:
  vaf::ModuleExecutor& executor_;
  std::shared_ptr<test::MyInterfaceConsumer> c_interface_instance_1_;
  std::shared_ptr<test::MyInterfaceConsumer> c_interface_instance_2_;
  std::shared_ptr<test::MyInterfaceProvider> p_interface_instance_1_;
  std::shared_ptr<test::MyInterfaceProvider> p_interface_instance_2_;
};

} // namespace apps

#endif // APPS_MY_APPLICATION_MODULE_BASE_H
