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
#include <iostream>

namespace NsApplicationUnit {
namespace NsSensorFusion {


/*
  Data element API example for MyDataElement of type std::uint64_t
  ================================================================
  - Provider
    ::vaf::Result<::vaf::DataPtr<std::uint64_t>> Allocate_MyDataElement()
    ::vaf::Result<void> SetAllocated_MyDataElement(::vaf::DataPtr<std::uint64_t>&& data)
    ::vaf::Result<void> Set_MyDataElement(const std::uint64_t& data)
  - Consumer
    ::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>> GetAllocated_MyDataElement()
    std::uint64_t Get_MyDataElement()
    std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>
    void RegisterDataElementHandler_MyDataElement(std::string owner, std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>&& f)

  Consumer interfaces
  ===================
    - ImageServiceConsumer1 : af::adas_demo_app::services::ImageServiceConsumer
      - Data elements
        - camera_image : datatypes::Image
        - image_scaling_factor_FieldNotifier : std::uint64_t

      - Operations
        - ::vaf::Future<af::adas_demo_app::services::internal::methods::GetImageSize::Output> GetImageSize()
        - ::vaf::Future<af::adas_demo_app::services::internal::methods::image_scaling_factor_FieldGetter::Output> image_scaling_factor_FieldGetter()
        - ::vaf::Future<void> image_scaling_factor_FieldSetter(const std::uint64_t& data)

    - ImageServiceConsumer2 : af::adas_demo_app::services::ImageServiceConsumer
      - Data elements
        - camera_image : datatypes::Image
        - image_scaling_factor_FieldNotifier : std::uint64_t

      - Operations
        - ::vaf::Future<af::adas_demo_app::services::internal::methods::GetImageSize::Output> GetImageSize()
        - ::vaf::Future<af::adas_demo_app::services::internal::methods::image_scaling_factor_FieldGetter::Output> image_scaling_factor_FieldGetter()
        - ::vaf::Future<void> image_scaling_factor_FieldSetter(const std::uint64_t& data)

    - SteeringAngleServiceConsumer : af::adas_demo_app::services::SteeringAngleServiceConsumer
      - Data elements
        - steering_angle : datatypes::SteeringAngle


    - VelocityServiceConsumer : af::adas_demo_app::services::VelocityServiceConsumer
      - Data elements
        - car_velocity : datatypes::Velocity


  Provider interfaces
  ===================
    - ObjectDetectionListModule : nsapplicationunit::nsmoduleinterface::nsobjectdetectionlist::ObjectDetectionListInterfaceProvider
      - Data elements
        - object_detection_list : adas::interfaces::ObjectDetectionList


*/

SensorFusion::SensorFusion(ConstructorToken&& token)
    : SensorFusionBase(std::move(token))
{
  std::string marker{"MARK-2"};
  bool constructed_{true};
  std::cout << marker << ": Construction of SensorFusion is " << constructed_ << std::endl;
}

void SensorFusion::Step1() {
  std::cout << "Step1 is performed: Clapton likes to clap" << std::endl;
}

void SensorFusion::Step2() {
  std::cout << "Step2 is performed: Mayo is naise" << std::endl;
}

void SensorFusion::Step3() {
  std::cout << "Step3 is performed: Penultimate is not Penaldo" << std::endl;
  _status = true;
}

void SensorFusion::Step4() {
  std::cout << "Sensor Fusion successfully run all periodic tasks!" << std::endl;
  nada = "Pico-Bello";
}


} // namespace NsSensorFusion
} // namespace NsApplicationUnit
