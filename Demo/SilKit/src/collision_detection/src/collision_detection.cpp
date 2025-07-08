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
/*!        \file  collision_detection.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "nsapplicationunit/nscollisiondetection/collision_detection.h"

namespace NsApplicationUnit {
namespace NsCollisionDetection {

/*
  Generated based on configuration in ../../model/collision_detection.py

  Consumer interfaces
  ===================
    Data element API example for object_detection_list of type adas::interfaces::ObjectDetectionList
      - ::vaf::Result<::vaf::ConstDataPtr<const adas::interfaces::ObjectDetectionList>>
  GetAllocated_object_detection_list()
      - adas::interfaces::ObjectDetectionList Get_object_detection_list()
      - void RegisterDataElementHandler_object_detection_list(std::string owner, std::function<void(const
  ::vaf::ConstDataPtr<const adas::interfaces::ObjectDetectionList>)>&& f)

    - ObjectDetectionListModule_ :
  nsapplicationunit::nsmoduleinterface::nsobjectdetectionlist::ObjectDetectionListInterfaceConsumer
      - Data elements
        - object_detection_list : adas::interfaces::ObjectDetectionList

  Provider interfaces
  ===================
    Data element API example for brake_action of type datatypes::BrakePressure
     - ::vaf::Result<::vaf::DataPtr<datatypes::BrakePressure>> Allocate_brake_action()
     - ::vaf::Result<void> SetAllocated_brake_action(::vaf::DataPtr<datatypes::BrakePressure>&& data)
     - ::vaf::Result<void> Set_brake_action(const datatypes::BrakePressure& data)

    - BrakeServiceProvider_ : af::adas_demo_app::services::BrakeServiceProvider
      - Data elements
        - brake_action : datatypes::BrakePressure
      - Operations
        - void
  RegisterOperationHandler_SumTwoSummands(std::function<af::adas_demo_app::services::SumTwoSummands::Output(const
  std::uint16_t&, const std::uint16_t&)>&& f)
*/

/**********************************************************************************************************************
  Constructor
**********************************************************************************************************************/
CollisionDetection::CollisionDetection(ConstructorToken&& token) : CollisionDetectionBase(std::move(token)) {
  ObjectDetectionListModule_->RegisterDataElementHandler_object_detection_list(
      GetName(), [this](vaf::ConstDataPtr<const ::adas::interfaces::ObjectDetectionList> object_detection_list) {
        OnObjectList(object_detection_list);
      });
  BrakeServiceProvider_->RegisterOperationHandler_SumTwoSummands(
      [](std::uint16_t const& summand_one, std::uint16_t const& summand_two) {
        af::adas_demo_app::services::SumTwoSummands::Output output{};
        output.sum = summand_one + summand_two;
        return output;
      });
}

/**********************************************************************************************************************
  1 periodic task(s)
**********************************************************************************************************************/
// Task with name PeriodicTask and a period of 200ms.
void CollisionDetection::PeriodicTask() { std::cout << "Collision detection is active\n"; }

::datatypes::BrakePressure CollisionDetection::ComputeBrakePressure(
    vaf::ConstDataPtr<const ::adas::interfaces::ObjectDetectionList>& object_list) {
  static_cast<void>(object_list);
  return ::datatypes::BrakePressure{11, 22};
}

void CollisionDetection::OnError(const vaf::Error& error) {
  static_cast<void>(error);
  ReportError(vaf::ErrorCode::kDefaultErrorCode, "Unknown error", true);
}

void CollisionDetection::OnObjectList(vaf::ConstDataPtr<const ::adas::interfaces::ObjectDetectionList>& object_list) {
  std::cout << "Collision onObjectList\n";
  ::datatypes::BrakePressure brake_pressure = ComputeBrakePressure(object_list);
  BrakeServiceProvider_->Set_brake_action(brake_pressure);
}

}  // namespace NsCollisionDetection
}  // namespace NsApplicationUnit
