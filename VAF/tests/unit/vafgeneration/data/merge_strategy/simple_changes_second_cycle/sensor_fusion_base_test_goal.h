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
/*!        \file  sensor_fusion_base.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef NSAPPLICATIONUNIT_NSSENSORFUSION_SENSOR_FUSION_BASE_H
#define NSAPPLICATIONUNIT_NSSENSORFUSION_SENSOR_FUSION_BASE_H

#include <iostream>
#include <memory>
#include "vaf/controller_interface.h"

#include "af/adas_demo_app/services/image_service_consumer.h"
#include "af/adas_demo_app/services/steering_angle_service_consumer.h"
#include "af/adas_demo_app/services/new_nada.h"
#include "af/adas_demo_app/services/velocity_service_consumer.h"
#include "nsapplicationunit/nsmoduleinterface/nsobjectdetectionlist/object_detection_list_interface_provider.h"
#include "sleep.h"

namespace NsApplicationUnit {
namespace NsSensorFusion {

class SensorFusionBase {
 public:
  struct ConstructorToken {
    std::shared_ptr<af::adas_demo_app::services::ImageServiceConsumer> ImageServiceConsumer1_;
    std::shared_ptr<af::adas_demo_app::services::ImageServiceConsumer> ImageServiceConsumer2_;
    std::shared_ptr<af::adas_demo_app::services::SteeringAngleServiceConsumer> SteeringAngleServiceConsumer_;
    std::shared_ptr<af::adas_demo_app::services::VelocityServiceConsumer> VelocityServiceConsumer_;
    std::shared_ptr<nsapplicationunit::nsmoduleinterface::nsobjectdetectionlist::ObjectDetectionListInterfaceProvider> ObjectDetectionListModule_;
  };

  SensorFusionBase(ConstructorToken&& token);
  virtual ~SensorFusionBase() = default;

  void ReportError(vaf::ErrorCode, std::string, bool) {}
  virtual void OnError(const vaf::Error&) {}
  std::string GetName() { return ""; }
  bool GetStatus() {return _mock_status};
  std::string GetMockId() {return _mock_id};

<<<<<<< {TMP_PATH}/SensorFusion/implementation/test/unittest/include/nsapplicationunit/nssensorfusion/sensor_fusion_base.h
  virtual void Step1() = 0;
  void TestHelper(std::string& mock_str, bool mock_status);
  virtual void Step2() = 0;
  virtual void Step2a() = 0;
  int GetTestNumber(std::string& test_name);
  virtual void Step2b() = 0;
=======
  virtual void Steppe() = 0;
  virtual void Estepo() = 0;
  virtual void Staipo() = 0;
  virtual void Finales() = 0;
>>>>>>> {TMP_PATH}/SensorFusion/implementation/test/unittest/include/nsapplicationunit/nssensorfusion/sensor_fusion_base.h.new~

 private:
  bool _mock_status{false};
  int _mock_sensor_id{22};
  std::string _mock_id{"mecorino"};

 protected:
  std::shared_ptr<af::adas_demo_app::services::ImageServiceConsumer> ImageServiceConsumer1_;
  std::shared_ptr<af::adas_demo_app::services::ImageServiceConsumer> ImageServiceConsumer2_;
  std::shared_ptr<af::adas_demo_app::services::SteeringAngleServiceConsumer> SteeringAngleServiceConsumer_;
  std::shared_ptr<af::adas_demo_app::services::VelocityServiceConsumer> VelocityServiceConsumer_;
  std::shared_ptr<nsapplicationunit::nsmoduleinterface::nsobjectdetectionlist::ObjectDetectionListInterfaceProvider> ObjectDetectionListModule_;
};

} // namespace NsSensorFusion
} // namespace NsApplicationUnit

#endif // NSAPPLICATIONUNIT_NSSENSORFUSION_SENSOR_FUSION_BASE_H
