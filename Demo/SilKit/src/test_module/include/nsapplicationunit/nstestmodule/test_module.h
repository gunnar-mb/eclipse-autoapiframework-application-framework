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
/*!        \file  test_module.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef NSAPPLICATIONUNIT_NSTESTMODULE_TEST_MODULE_H
#define NSAPPLICATIONUNIT_NSTESTMODULE_TEST_MODULE_H

#include "nsapplicationunit/nstestmodule/test_module_base.h"

namespace NsApplicationUnit {
namespace NsTestModule {

class TestModule : public TestModuleBase {
 public:
  TestModule(ConstructorToken&& token);

  void BrakeTask() override;
  void ImageTask() override;
  void SteeringAngleTask() override;
  void VelocityTask() override;

 private:
  datatypes::Image image{};
};

}  // namespace NsTestModule
}  // namespace NsApplicationUnit

#endif  // NSAPPLICATIONUNIT_NSTESTMODULE_TEST_MODULE_H
