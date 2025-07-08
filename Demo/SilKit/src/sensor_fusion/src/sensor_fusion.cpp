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
/*!        \file  sensor_fusion.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "nsapplicationunit/nssensorfusion/sensor_fusion.h"

namespace NsApplicationUnit {
namespace NsSensorFusion {

/*
  Generated based on configuration in ../../model/sensor_fusion.py

  Consumer interfaces
  ===================
    Data element API example for camera_image of type datatypes::Image
      - ::vaf::Result<::vaf::ConstDataPtr<const datatypes::Image>> GetAllocated_camera_image()
      - datatypes::Image Get_camera_image()
      - void RegisterDataElementHandler_camera_image(std::string owner, std::function<void(const
  ::vaf::ConstDataPtr<const datatypes::Image>)>&& f)

    - ImageServiceConsumer1_ : af::adas_demo_app::services::ImageServiceConsumer
      - Data elements
        - camera_image : datatypes::Image
      - Operations
        - ::vaf::Future<af::adas_demo_app::services::GetImageSize::Output> GetImageSize()
    - ImageServiceConsumer2_ : af::adas_demo_app::services::ImageServiceConsumer
      - Data elements
        - camera_image : datatypes::Image
      - Operations
        - ::vaf::Future<af::adas_demo_app::services::GetImageSize::Output> GetImageSize()
    - SteeringAngleServiceConsumer_ : af::adas_demo_app::services::SteeringAngleServiceConsumer
      - Data elements
        - steering_angle : datatypes::SteeringAngle
    - VelocityServiceConsumer_ : af::adas_demo_app::services::VelocityServiceConsumer
      - Data elements
        - car_velocity : datatypes::Velocity

  Provider interfaces
  ===================
    Data element API example for object_detection_list of type adas::interfaces::ObjectDetectionList
     - ::vaf::Result<::vaf::DataPtr<adas::interfaces::ObjectDetectionList>> Allocate_object_detection_list()
     - ::vaf::Result<void> SetAllocated_object_detection_list(::vaf::DataPtr<adas::interfaces::ObjectDetectionList>&&
  data)
     - ::vaf::Result<void> Set_object_detection_list(const adas::interfaces::ObjectDetectionList& data)

    - ObjectDetectionListModule_ :
  nsapplicationunit::nsmoduleinterface::nsobjectdetectionlist::ObjectDetectionListInterfaceProvider
      - Data elements
        - object_detection_list : adas::interfaces::ObjectDetectionList
*/

/**********************************************************************************************************************
  Constructor
**********************************************************************************************************************/
SensorFusion::SensorFusion(ConstructorToken&& token) : SensorFusionBase(std::move(token)) {
  VelocityServiceConsumer_->RegisterDataElementHandler_car_velocity(
      GetName(), [this](vaf::ConstDataPtr<const ::datatypes::Velocity> velocity) { OnVelocity(std::move(velocity)); });
}

/**********************************************************************************************************************
  4 periodic task(s)
**********************************************************************************************************************/
// Task with name Step1 and a period of 200ms.
void SensorFusion::Step1() {
  if (is_enabled_) {
    std::cout << "SensorFusion::step\n";
    bool no_new_image{false};

    auto image1 = ImageServiceConsumer1_->GetAllocated_camera_image().InspectError(
        [&no_new_image](const vaf::Error&) { no_new_image = true; });
    auto image2 = ImageServiceConsumer2_->GetAllocated_camera_image().InspectError(
        [&no_new_image](const vaf::Error&) { no_new_image = true; });
    auto steering_angle = SteeringAngleServiceConsumer_->Get_steering_angle();
    auto velocity = VelocityServiceConsumer_->Get_car_velocity();

    if (!no_new_image) {
      std::cout << "Received new images" << "\n";
      ::adas::interfaces::ObjectDetectionList object_list =
          DoDetection(*image1.Value(), *image2.Value(), steering_angle, velocity);
      std::cout << "SensorFusion sending detection list\n";
      ObjectDetectionListModule_->Set_object_detection_list(object_list);
    }
  }
}

// Task with name Step2 and a period of 200ms.
void SensorFusion::Step2() {
  // Insert your code for periodic execution here...
}

// Task with name Step3 and a period of 200ms.
void SensorFusion::Step3() {
  // Insert your code for periodic execution here...
}

// Task with name Step4 and a period of 200ms.
void SensorFusion::Step4() {
  // Insert your code for periodic execution here...
}

void SensorFusion::OnVelocity(vaf::ConstDataPtr<const ::datatypes::Velocity> velocity) {
  std::cout << "Received Velocity: " << velocity->value << "\n";
  is_enabled_ = (velocity->value < kMaxVelocity);
}

::adas::interfaces::ObjectDetectionList SensorFusion::DoDetection(const ::datatypes::Image& image1,
                                                                  const ::datatypes::Image& image2,
                                                                  ::datatypes::SteeringAngle, ::datatypes::Velocity) {
  static_cast<void>(image1);
  static_cast<void>(image2);

  vaf::Future<af::adas_demo_app::services::GetImageSize::Output> answer = ImageServiceConsumer1_->GetImageSize();
  if (vaf::is_future_ready(answer)) {
    auto result = answer.GetResult();
    if (result.HasValue())
      std::cout << "GetImageSize() yields: " << result.Value().width << "x" << result.Value().height << "\n";
  }
  return ::adas::interfaces::ObjectDetectionList{};
}

void SensorFusion::OnError(const vaf::Error& error) {
  std::cout << "Error in sensor fusion: " << error.Message() << ", " << error.UserMessage() << "\n";
  ReportError(vaf::ErrorCode::kDefaultErrorCode, "Unknown error", true);
}

}  // namespace NsSensorFusion
}  // namespace NsApplicationUnit
