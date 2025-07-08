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
/*!        \file  executable_controller.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "executable_controller/executable_controller.h"

#include "test/my_module1.h"
#include "test/my_module2.h"
#include "test/my_module3.h"
#include "test/my_module4.h"
#include "test/my_app.h"


#include "vaf/result.h"

namespace executable_controller {

ExecutableController::ExecutableController()
  : ExecutableControllerBase(),
    executor_{} {
}

void ExecutableController::DoInitialize() {
  executor_ = std::make_unique<vaf::Executor>(std::chrono::milliseconds{ 10 });


  auto MyModule3 = std::make_shared<test::MyModule3>(
    *executor_,
    "MyModule3",
    *this);

  auto MyModule4 = std::make_shared<test::MyModule4>(
    *executor_,
    "MyModule4",
    *this);

  auto MyModule2 = std::make_shared<test::MyModule2>(
    *executor_,
    "MyModule2",
    *this);

  auto MyModule1 = std::make_shared<test::MyModule1>(
    *executor_,
    "MyModule1",
    std::vector<std::string>{},
    *this);

  auto MyApp = std::make_shared<test::MyApp>( test::MyApp::ConstructorToken{
    "MyApp",
    std::vector<std::string>{
      {"MyModule2"},
      {"MyModule3"}
    },
    *this,
    *executor_,
    MyModule3,
    MyModule4,
    MyModule1,
    MyModule2
,    0,
    std::chrono::nanoseconds{ 10000000 },
    1,
    std::chrono::nanoseconds{ 0 }
    });

  RegisterModule(MyModule3);

  RegisterModule(MyModule4);

  RegisterModule(MyModule1);

  RegisterModule(MyModule2);

  RegisterModule(MyApp);

  ExecutableControllerBase::DoInitialize();
}

void ExecutableController::DoStart() {
  ExecutableControllerBase::DoStart();
}

void ExecutableController::DoShutdown() {
  ExecutableControllerBase::DoShutdown();
}


} // namespace executable_controller
