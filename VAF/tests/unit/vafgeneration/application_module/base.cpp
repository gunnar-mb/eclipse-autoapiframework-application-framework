
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
/*!        \file  my_application_module_base.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "apps/my_application_module_base.h"

namespace apps {

MyApplicationModuleBase::MyApplicationModuleBase(ConstructorToken&& token)
    : vaf::ControlInterface(token.name_, std::move(token.dependencies_), token.executable_controller_interface_, token.executor_),
      executor_{vaf::ControlInterface::executor_},
      c_interface_instance_1_{std::move(token.c_interface_instance_1_)},
      c_interface_instance_2_{std::move(token.c_interface_instance_2_)},
      p_interface_instance_1_{std::move(token.p_interface_instance_1_)},
      p_interface_instance_2_{std::move(token.p_interface_instance_2_)}
  {
  executor_.RunPeriodic("task1", std::chrono::milliseconds{ 10 }, [this]() { task1(); }, {}, token.task_offset_task1_, token.task_budget_task1_);
  executor_.RunPeriodic("task2", std::chrono::milliseconds{ 20 }, [this]() { task2(); }, {"task1"}, token.task_offset_task2_, token.task_budget_task2_);
}

} // namespace apps
