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
/*!        \file  my_application_module.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef APPS_MY_APPLICATION_MODULE_H
#define APPS_MY_APPLICATION_MODULE_H

#include "apps/my_application_module_base.h"

namespace apps {

class MyApplicationModule : public MyApplicationModuleBase {
 public:
  MyApplicationModule(ConstructorToken&& token);

  void task1() override;
  void task2() override;

 private:
};

} // namespace apps

#endif // APPS_MY_APPLICATION_MODULE_H
