/*!********************************************************************************************************************
 *  COPYRIGHT
 *  -------------------------------------------------------------------------------------------------------------------
 *
 *  Copyright (c) 2025 by Vector Informatik GmbH. All rights reserved.
 *
 *                This software is copyright protected and proprietary to Vector Informatik GmbH.
 *                Vector Informatik GmbH grants to you only those rights as set out in the license conditions.
 *                All other rights remain with Vector Informatik GmbH.
 *
 *  -------------------------------------------------------------------------------------------------------------------
 *  FILE DESCRIPTION
 *  -----------------------------------------------------------------------------------------------------------------*/
/*!        file  data_ptr_helper.h
 *         brief
 *
 *********************************************************************************************************************/
#ifndef INCLUDE_VAF_DATA_PTR_HELPER_H
#define INCLUDE_VAF_DATA_PTR_HELPER_H

#include "vaf/data_ptr.h"

namespace vaf {
    namespace internal {

        template<typename T>
        class DataPtrHelper {
        public:
            DataPtrHelper() = delete;

            DataPtrHelper(const DataPtrHelper &) = delete;

            DataPtrHelper &operator=(const DataPtrHelper &) = delete;

            static std::unique_ptr<T> getRawPtr(::vaf::DataPtr<T> &ptr) { return std::move(ptr.container_->raw_ptr_); };
        };

    }  // namespace internal
}  // namespace vaf

#endif  // INCLUDE_VAF_DATA_PTR_H