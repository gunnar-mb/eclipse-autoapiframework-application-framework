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
/*!        \file  my_consumer_module.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef TEST_MY_CONSUMER_MODULE_H
#define TEST_MY_CONSUMER_MODULE_H

#include <atomic>
#include <mutex>
#include <memory>
#include <string>
#include <vector>

#include "vaf/receiver_handler_container.h"
#include "vaf/controller_interface.h"
#include "vaf/data_ptr.h"
#include "vaf/executable_controller_interface.h"
#include "vaf/result.h"

#include "silkit/SilKit.hpp"
#include "silkit/services/all.hpp"
#include "silkit/services/orchestration/string_utils.hpp"
#include "silkit/util/serdes/Serialization.hpp"
#include "protobuf_interface_test_MyInterface.pb.h"

#include "test/my_interface_consumer.h"


namespace test {

class MyConsumerModule final : public test::MyInterfaceConsumer, public vaf::ControlInterface {
 public:
  MyConsumerModule(vaf::Executor& executor, std::string name, vaf::ExecutableControllerInterface& executable_controller_interface);
  ~MyConsumerModule() override = default;

  MyConsumerModule(const MyConsumerModule&) = delete;
  MyConsumerModule(MyConsumerModule&&) = delete;
  MyConsumerModule& operator=(const MyConsumerModule&) = delete;
  MyConsumerModule& operator=(MyConsumerModule&&) = delete;

  // Management related operations
  vaf::Result<void> Init() noexcept override;
  void Start() noexcept override;
  void Stop() noexcept override;
  void DeInit() noexcept override;
  void StartEventHandlerForModule(const std::string& module) override;
  void StopEventHandlerForModule(const std::string& module) override;

  ::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>> GetAllocated_my_data_element1() override;
  std::uint64_t Get_my_data_element1() override;
  void RegisterDataElementHandler_my_data_element1(std::string owner, std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>&& f) override;
  ::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>> GetAllocated_my_data_element2() override;
  std::uint64_t Get_my_data_element2() override;
  void RegisterDataElementHandler_my_data_element2(std::string owner, std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>&& f) override;

  ::vaf::Future<void> MyVoidOperation(const std::uint64_t& in) override;
  ::vaf::Future<test::MyOperation::Output> MyOperation(const std::uint64_t& in, const std::uint64_t& inout) override;
  ::vaf::Future<test::MyGetter::Output> MyGetter() override;
  ::vaf::Future<void> MySetter(const std::uint64_t& a) override;

 private:
  vaf::ModuleExecutor& executor_;
  std::vector<std::string> active_modules_;
  std::unique_ptr<SilKit::IParticipant> participant_;

  ::vaf::ConstDataPtr<const std::uint64_t> cached_test_my_data_element1_{};
  std::vector<::vaf::ReceiverHandlerContainer<std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>>> registered_test_my_data_element1_event_handlers_{};
  std::mutex cached_test_my_data_element1_mutex_;
  SilKit::Services::PubSub::IDataSubscriber* subscriber_test_my_data_element1_;
  ::vaf::ConstDataPtr<const std::uint64_t> cached_test_my_data_element2_{std::make_unique<const std::uint64_t>(std::uint64_t{64})};
  std::vector<::vaf::ReceiverHandlerContainer<std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>>> registered_test_my_data_element2_event_handlers_{};
  std::mutex cached_test_my_data_element2_mutex_;
  SilKit::Services::PubSub::IDataSubscriber* subscriber_test_my_data_element2_;
  SilKit::Services::Rpc::IRpcClient* rpc_client_test_MyVoidOperation_;
  SilKit::Services::Rpc::IRpcClient* rpc_client_test_MyOperation_;
  SilKit::Services::Rpc::IRpcClient* rpc_client_test_MyGetter_;
  SilKit::Services::Rpc::IRpcClient* rpc_client_test_MySetter_;
};


} // namespace test

#endif // TEST_MY_CONSUMER_MODULE_H
