
/*!********************************************************************************************************************
 *  COPYRIGHT
 *  -------------------------------------------------------------------------------------------------------------------
 *
 *  Copyright (c) 2025 by Vector Informatik GmbH. All rights reserved.
 *
 *                This software is copyright protected and proprietary to Vector Informatik GmbH.
 *                Vector Informatik GmbH grants to you only those rights as set out in the license conditions.
 *                All other rights remain with Vector Informatik GmbH.
 *
 *  -------------------------------------------------------------------------------------------------------------------
 *  FILE DESCRIPTION
 *  -----------------------------------------------------------------------------------------------------------------*/
/*!        file  executable_controller_interface.h
 *         brief
 *
 *********************************************************************************************************************/
#ifndef VAF_EXECUTABLE_CONTROLLER_INTERFACE_H_
#define VAF_EXECUTABLE_CONTROLLER_INTERFACE_H_

/*!********************************************************************************************************************
 *  INCLUDES
 *********************************************************************************************************************/

#include <string>
#include "vaf/error_domain.h"
#include "vaf/module_states.h"

namespace vaf {

class ExecutableControllerInterface {
public:
  virtual ~ExecutableControllerInterface() = default;
  virtual void ReportOperationalOfModule(std::string name) = 0;
  virtual void ReportErrorOfModule(vaf::Error error, std::string name, bool critical) = 0;
};

} // namespace vaf

#endif // VAF_EXECUTABLE_CONTROLLER_INTERFACE_H_
