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
/*!        \file  vss_provider.cpp
 *         \brief
 *
 *********************************************************************************************************************/

 #include "demo/vss_provider.h"

 namespace demo {
 
 
 /*
   Generated based on configuration in ../../model/vss_provider.py
 
   Provider interfaces
   ===================
     Data element API example for Lateral of type float
      - ::vaf::Result<::vaf::DataPtr<float>> Allocate_Lateral()
      - ::vaf::Result<void> SetAllocated_Lateral(::vaf::DataPtr<float>&& data)
      - ::vaf::Result<void> Set_Lateral(const float& data)
 
     - AccelerationProvider_ : vss::vehicle::Acceleration_IfProvider
       - Data elements
         - Lateral : float
         - Longitudinal : float
         - Vertical : float
     - DriverProvider_ : vss::vehicle::Driver_IfProvider
       - Data elements
         - AttentiveProbability : float
         - DistractionLevel : float
         - FatigueLevel : float
         - HeartRate : std::uint16_t
         - Identifier : vss::vehicle::driver::Identifier
         - IsEyesOnRoad : bool
         - IsHandsOnWheel : bool
 */
 
 /**********************************************************************************************************************
   Constructor
 **********************************************************************************************************************/
 VssProvider::VssProvider(ConstructorToken&& token)
     : VssProviderBase(std::move(token))
 {
   // Insert your code here...
 }
 
 /**********************************************************************************************************************
   1 periodic task(s)
 **********************************************************************************************************************/
 // Task with name PeriodicTask and a period of 200ms.
 void VssProvider::PeriodicTask() {
     // Acceleration
     static float value = 0;
     static float diff = 0.2f;
     AccelerationProvider_->Set_Lateral(value);
     AccelerationProvider_->Set_Longitudinal(value);
     AccelerationProvider_->Set_Vertical(value);
   
     if (value >= 10) {
       diff = -0.2f;
     } else if (value <= -10) {
       diff = 0.2f;
     }
     value += diff;
   
     // Driver
     vss::vehicle::driver::Identifier driverId = {"Issuer", "Driver1"};
     DriverProvider_->Set_Identifier(driverId);
   
     if (value > 5) {
       DriverProvider_->Set_IsEyesOnRoad(true);
     } else {
       DriverProvider_->Set_IsEyesOnRoad(false);
     }
 }
 
 
 } // namespace demo
 