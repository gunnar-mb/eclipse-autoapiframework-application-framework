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
/*!        file  receiver_handler_container.h
 *         brief
 *
 *********************************************************************************************************************/
#ifndef INCLUDE_VAF_RECEIVER_HANDLER_CONTAINER_H
#define INCLUDE_VAF_RECEIVER_HANDLER_CONTAINER_H

#include <string>

namespace vaf {
template<typename T>

class ReceiverHandlerContainer {
public:
  ReceiverHandlerContainer(std::string owner, T&& handler) 
    : owner_{std::move(owner)}, handler_{std::move(handler)}, is_active_{false} {
  }

  std::string owner_;
  T handler_;
  bool is_active_;
};

} // namespace vaf

#endif // INCLUDE_VAF_RECEIVER_HANDLER_CONTAINER_H