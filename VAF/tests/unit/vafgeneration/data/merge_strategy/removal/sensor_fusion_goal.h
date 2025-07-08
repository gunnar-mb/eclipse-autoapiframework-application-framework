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

#include "nsapplicationunit/nssensorfusion/sensor_fusion_base.h"

namespace NsApplicationUnit {
namespace NsSensorFusion {

class SensorFusion : public SensorFusionBase {
 public:
  SensorFusion(ConstructorToken&& token);


 private:
};

} // namespace NsSensorFusion
} // namespace NsApplicationUnit

#endif // NSAPPLICATIONUNIT_NSSENSORFUSION_SENSOR_FUSION_H
