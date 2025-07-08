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
/*!        \file  sensor_fusion.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef NSAPPLICATIONUNIT_NSSENSORFUSION_SENSOR_FUSION_H
#define NSAPPLICATIONUNIT_NSSENSORFUSION_SENSOR_FUSION_H

#include <iostream>
#include "easylogging++.h"
#include "nsapplicationunit/nssensorfusion/sensor_fusion_base.h"
#include "mock.h"
#include "sleep.h"

namespace NsApplicationUnit {
namespace NsSensorFusion {

class SensorFusion : public SensorFusionBase {
 public:
  SensorFusion(ConstructorToken&& token);

<<<<<<< {TMP_PATH}/SensorFusion/implementation/include/nsapplicationunit/nssensorfusion/sensor_fusion.h
  void Step1() override;
  void RepeatSomething(std::string& repeat_id, const int& task_id);
  void Step2() override;
  void Step2a() override;
  int GetTaskId();
  void Step2b() override;
=======
  void Steppe() override;
  void Estepo() override;
  void Staipo() override;
  void Finales() override;
>>>>>>> {TMP_PATH}/SensorFusion/implementation/include/nsapplicationunit/nssensorfusion/sensor_fusion.h.new~

 private:
  bool _status{false};
  int sensor_id;
  int current_task_id;
  std::string nada{"Gellow"};
};

} // namespace NsSensorFusion
} // namespace NsApplicationUnit

#endif // NSAPPLICATIONUNIT_NSSENSORFUSION_SENSOR_FUSION_H
