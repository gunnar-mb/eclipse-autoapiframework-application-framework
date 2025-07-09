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
/*!        \file  app_module1.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "demo/app_module1.h"

namespace demo {


/*
  Generated based on configuration in ../../model/app_module1.py

  Provider interfaces
  ===================
    Data element API example for Message of type vaf::string
     - ::vaf::Result<::vaf::DataPtr<vaf::string>> Allocate_Message()
     - ::vaf::Result<void> SetAllocated_Message(::vaf::DataPtr<vaf::string>&& data)
     - ::vaf::Result<void> Set_Message(const vaf::string& data)

    - HelloWorldProvider_ : demo::HelloWorldIfProvider
      - Data elements
        - Message : vaf::string
      - Operations
        - void RegisterOperationHandler_SetMsgId(std::function<void(const std::uint8_t&)>&& f)
*/

/**********************************************************************************************************************
  Constructor
**********************************************************************************************************************/
AppModule1::AppModule1(ConstructorToken&& token)
    : AppModule1Base(std::move(token))
{
  HelloWorldProvider_->RegisterOperationHandler_SetMsgId(
    [this](const std::uint8_t& msg_id) { msg_id_ = static_cast<uint8_t>(msg_id); }
  );
}

/**********************************************************************************************************************
  1 periodic task(s)
**********************************************************************************************************************/
// Task with name PeriodicTask and a period of 500ms.
void AppModule1::PeriodicTask() {
  std::string myMsg = "Hello, VAF! - MsgID: " + std::to_string(msg_id_);
  HelloWorldProvider_->Set_Message(myMsg.c_str());
}


} // namespace demo
