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
/*!        \file  user_controller.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef USER_CONTROLLER_H
#define USER_CONTROLLER_H

#include "vaf/user_controller_interface.h"


class UserController : public vaf::UserControllerInterface {
public:
  void PreInitialize() override;
  void PostInitialize() override;
  void PreStart() override;
  void PostStart() override;
  void PreShutdown() override;
  void PostShutdown() override;

  void OnError(vaf::Error error, std::string name, bool critical) override;

private:
};


#endif // USER_CONTROLLER_H
