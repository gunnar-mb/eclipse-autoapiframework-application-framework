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
/*!        \file  user_controller.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "user_controller.h"

#include <iostream>

std::unique_ptr<vaf::UserControllerInterface> CreateUserController() {
  return std::make_unique<UserController>();
}

void UserController::PreInitialize() {
 std::cout << "UserController::PreInitialize\n";
}

void UserController::PostInitialize() {
  std::cout << "UserController::PostInitialize\n";
}

void UserController::PreStart() {
  std::cout << "UserController::PreStart\n";
}

void UserController::PostStart() {
  std::cout << "UserController::PostStart\n";
}

void UserController::PreShutdown() {
  std::cout << "UserController::PreShutdown\n";
}

void UserController::PostShutdown() {
  std::cout << "UserController::PostShutdown\n";
}

void UserController::OnError(vaf::Error error, std::string name, bool critical) {
  std::cout << "UserController::OnError: name: " << name << ", Message: " << error.Message() << ", critical: " << critical << "\n";
  if(critical){
    std::cout << "UserController::OnError: Critical call, aborting execution!" << std::endl;
    std::abort();
  }
}
