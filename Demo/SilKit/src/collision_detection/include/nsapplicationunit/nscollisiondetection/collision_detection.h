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
/*!        \file  collision_detection.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef NSAPPLICATIONUNIT_NSCOLLISIONDETECTION_COLLISION_DETECTION_H
#define NSAPPLICATIONUNIT_NSCOLLISIONDETECTION_COLLISION_DETECTION_H

#include "nsapplicationunit/nscollisiondetection/collision_detection_base.h"

namespace NsApplicationUnit {
namespace NsCollisionDetection {

class CollisionDetection : public CollisionDetectionBase {
 public:
  CollisionDetection(ConstructorToken&& token);

  void PeriodicTask() override;

  ::datatypes::BrakePressure ComputeBrakePressure(
      vaf::ConstDataPtr<const ::adas::interfaces::ObjectDetectionList>& object_list);
  void OnError(const vaf::Error& error) override;
  void OnObjectList(vaf::ConstDataPtr<const ::adas::interfaces::ObjectDetectionList>& object_list);

 private:
};

}  // namespace NsCollisionDetection
}  // namespace NsApplicationUnit

#endif  // NSAPPLICATIONUNIT_NSCOLLISIONDETECTION_COLLISION_DETECTION_H
