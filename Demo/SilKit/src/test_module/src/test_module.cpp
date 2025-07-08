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
/*!        \file  test_module.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "nsapplicationunit/nstestmodule/test_module.h"

namespace NsApplicationUnit {
namespace NsTestModule {

/*
  Generated based on configuration in ../../model/test_module.py

  Consumer interfaces
  ===================
    Data element API example for brake_action of type datatypes::BrakePressure
      - ::vaf::Result<::vaf::ConstDataPtr<const datatypes::BrakePressure>> GetAllocated_brake_action()
      - datatypes::BrakePressure Get_brake_action()
      - void RegisterDataElementHandler_brake_action(std::string owner, std::function<void(const
  ::vaf::ConstDataPtr<const datatypes::BrakePressure>)>&& f)

    - BrakeServiceConsumer_ : af::adas_demo_app::services::BrakeServiceConsumer
      - Data elements
        - brake_action : datatypes::BrakePressure
      - Operations
        - ::vaf::Future<af::adas_demo_app::services::SumTwoSummands::Output> SumTwoSummands(const std::uint16_t&
  summand_one, const std::uint16_t& summand_two)

  Provider interfaces
  ===================
    Data element API example for camera_image of type datatypes::Image
     - ::vaf::Result<::vaf::DataPtr<datatypes::Image>> Allocate_camera_image()
     - ::vaf::Result<void> SetAllocated_camera_image(::vaf::DataPtr<datatypes::Image>&& data)
     - ::vaf::Result<void> Set_camera_image(const datatypes::Image& data)

    - ImageServiceProvider1_ : af::adas_demo_app::services::ImageServiceProvider
      - Data elements
        - camera_image : datatypes::Image
      - Operations
        - void
  RegisterOperationHandler_GetImageSize(std::function<af::adas_demo_app::services::GetImageSize::Output()>&& f)
    - ImageServiceProvider2_ : af::adas_demo_app::services::ImageServiceProvider
      - Data elements
        - camera_image : datatypes::Image
      - Operations
        - void
  RegisterOperationHandler_GetImageSize(std::function<af::adas_demo_app::services::GetImageSize::Output()>&& f)
    - SteeringAngleServiceProvider_ : af::adas_demo_app::services::SteeringAngleServiceProvider
      - Data elements
        - steering_angle : datatypes::SteeringAngle
    - VelocityServiceProvider_ : af::adas_demo_app::services::VelocityServiceProvider
      - Data elements
        - car_velocity : datatypes::Velocity
*/

/**********************************************************************************************************************
  Constructor
**********************************************************************************************************************/
TestModule::TestModule(ConstructorToken&& token) : TestModuleBase(std::move(token)) {
  // Init image
  image.height = 1080;
  image.width = 1920;
  image.timestamp = 0;

  image.R.push_back(10);
  image.R.push_back(11);
  image.R.push_back(12);
  image.R.push_back(13);

  image.G.push_back(20);
  image.G.push_back(21);
  image.G.push_back(22);
  image.G.push_back(23);
  image.G.push_back(24);

  image.B.push_back(30);
  image.B.push_back(31);
  image.B.push_back(32);
  image.B.push_back(33);
  image.B.push_back(34);
  image.B.push_back(35);

  ImageServiceProvider1_->RegisterOperationHandler_GetImageSize(
      [this]() -> af::adas_demo_app::services::GetImageSize::Output {
        af::adas_demo_app::services::GetImageSize::Output output{};
        std::cout << "ImageServiceProvider1::GetImageSize handler called" << std::endl;
        output.width = image.width;
        output.height = image.height;
        return output;
      });
  ImageServiceProvider2_->RegisterOperationHandler_GetImageSize(
      [this]() -> af::adas_demo_app::services::GetImageSize::Output {
        af::adas_demo_app::services::GetImageSize::Output output{};
        std::cout << "ImageServiceProvider2::GetImageSize handler called" << std::endl;
        output.width = image.width;
        output.height = image.height;
        return output;
      });

  BrakeServiceConsumer_->RegisterDataElementHandler_brake_action(
      GetName(), [this](vaf::ConstDataPtr<const datatypes::BrakePressure> brake_pressure) {
        std::cout << "Received brake_action call with timestamp: " << brake_pressure->timestamp
                  << " and value: " << static_cast<int>(brake_pressure->value) << std::endl;
      });
}

/**********************************************************************************************************************
  4 periodic task(s)
**********************************************************************************************************************/
// Task with name BrakeTask and a period of 100ms.
void TestModule::BrakeTask() {
  // Insert your code for periodic execution here...
}

// Task with name ImageTask and a period of 100ms.
void TestModule::ImageTask() {
  static uint64_t counter = 0;
  static uint8_t step = 0;

  if (0 == step) {
    image.timestamp = static_cast<uint64_t>(
        std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch())
            .count());
    ImageServiceProvider1_->Set_camera_image(image);
    ImageServiceProvider2_->Set_camera_image(image);
  } else {
    counter++;
  }
  step = 1 - step;
}

// Task with name SteeringAngleTask and a period of 1000ms.
void TestModule::SteeringAngleTask() {
  static uint16_t counter = 0;

  auto steering_angle = datatypes::SteeringAngle();
  steering_angle.timestamp = static_cast<uint64_t>(
      std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch())
          .count());
  steering_angle.value = counter;
  SteeringAngleServiceProvider_->Set_steering_angle(steering_angle);

  counter += 1000;
}

// Task with name VelocityTask and a period of 1000ms.
void TestModule::VelocityTask() {
  static uint16_t counter = 0;

  auto velocity = datatypes::Velocity();
  velocity.timestamp = static_cast<uint64_t>(
      std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch())
          .count());
  velocity.value = counter++;
  VelocityServiceProvider_->Set_car_velocity(velocity);
}

}  // namespace NsTestModule
}  // namespace NsApplicationUnit
