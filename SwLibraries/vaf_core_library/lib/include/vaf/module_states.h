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
/*!        file  module_states.h
 *         brief
 *
 *********************************************************************************************************************/
#ifndef INCLUDE_VAF_MODULE_STATES_H
#define INCLUDE_VAF_MODULE_STATES_H

#include <string>

namespace vaf {

enum class ModuleStates {
  kNotInitialized,
  kNotOperational,
  kStarting,
  kOperational,
  kShutdown
};

inline std::string ModuleStateToString(ModuleStates state) {
  switch (state) {
    case ModuleStates::kNotInitialized: return "kNotInitialized";
    case ModuleStates::kNotOperational: return "kNotOperational";
    case ModuleStates::kStarting: return "kStarting";
    case ModuleStates::kOperational: return "kOperational";
    case ModuleStates::kShutdown: return "kShutdown";
  }
  return "Unknow state";
}

} // namespace vaf

#endif // INCLUDE_VAF_MODULE_STATES_H