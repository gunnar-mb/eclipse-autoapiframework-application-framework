
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

MyApplicationModuleBase::MyApplicationModuleBase(ConstructorToken&& token):
      c_interface_instance_1_{std::move(token.c_interface_instance_1_)},
      c_interface_instance_2_{std::move(token.c_interface_instance_2_)},
      p_interface_instance_1_{std::move(token.p_interface_instance_1_)},
      p_interface_instance_2_{std::move(token.p_interface_instance_2_)} {}

} // namespace apps
