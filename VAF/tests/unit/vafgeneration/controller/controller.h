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
/*!        \file  executable_controller.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef EXECUTABLE_CONTROLLER_EXECUTABLE_CONTROLLER_H
#define EXECUTABLE_CONTROLLER_EXECUTABLE_CONTROLLER_H

#include <memory>

#include "vaf/executable_controller_base.h"
#include "vaf/executor.h"

namespace executable_controller {

class ExecutableController final : public vaf::ExecutableControllerBase {
 public:
  ExecutableController();
  ~ExecutableController() override = default;

 protected:
  void DoInitialize() override;
  void DoStart() override;
  void DoShutdown() override;

 private:
  std::unique_ptr<vaf::Executor> executor_;
};

} // namespace executable_controller

#endif // EXECUTABLE_CONTROLLER_EXECUTABLE_CONTROLLER_H
