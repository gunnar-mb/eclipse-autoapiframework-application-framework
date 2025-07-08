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
/*!        \file  app_module2.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "demo/app_module2.h"
#include <iostream>

namespace demo {


/*
  Generated based on configuration in ../../model/app_module2.py

  Consumer interfaces
  ===================
    Data element API example for Message of type vaf::string
      - ::vaf::Result<::vaf::ConstDataPtr<const vaf::string>> GetAllocated_Message()
      - vaf::string Get_Message()
      - void RegisterDataElementHandler_Message(std::string owner, std::function<void(const ::vaf::ConstDataPtr<const vaf::string>)>&& f)

    - HelloWorldConsumer_ : demo::HelloWorldIfConsumer
      - Data elements
        - Message : vaf::string
      - Operations
        - ::vaf::Future<void> SetMsgId(const std::uint8_t& MsgId)
*/

/**********************************************************************************************************************
  Constructor
**********************************************************************************************************************/
AppModule2::AppModule2(ConstructorToken&& token)
    : AppModule2Base(std::move(token))
{
  HelloWorldConsumer_->RegisterDataElementHandler_Message(
    GetName(),
    [](const auto& hello_text) { std::cout << "Received: " << *hello_text << std::endl; }
  );
}

/**********************************************************************************************************************
  1 periodic task(s)
**********************************************************************************************************************/
// Task with name PeriodicTask and a period of 1000ms.
void AppModule2::PeriodicTask() {
  static uint8_t msg_id = 0;
  HelloWorldConsumer_->SetMsgId(msg_id++);
}


} // namespace demo
