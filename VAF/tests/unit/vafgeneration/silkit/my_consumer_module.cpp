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
/*!        \file  my_consumer_module.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "test/my_consumer_module.h"

#include <chrono>

#include "vaf/error_domain.h"
#include "protobuf/interface/test/myinterface/protobuf_transformer.h"
namespace test {

MyConsumerModule::MyConsumerModule(::vaf::Executor& executor, std::string name, ::vaf::ExecutableControllerInterface& executable_controller_interface)
  : ::vaf::ControlInterface(std::move(name), {}, executable_controller_interface, executor),
    executor_{ControlInterface::executor_} {
}

::vaf::Result<void> MyConsumerModule::Init() noexcept {
  return ::vaf::Result<void>{};
}

void MyConsumerModule::Start() noexcept {
  const auto registry_uri = "silkit://localhost:8500";
  const std::string participant_config_text = R"(
  Description: My participant configuration
  Logging:
      Sinks:
      - Type: Stdout
        Level: Info
  )";
  auto config = SilKit::Config::ParticipantConfigurationFromString(participant_config_text);
  participant_ = SilKit::CreateParticipant(config, "test_MyConsumerModule", registry_uri);

  SilKit::Services::PubSub::PubSubSpec pubsubspec_test_my_data_element1{"MyInterface_my_data_element1", SilKit::Util::SerDes::MediaTypeData()};
  pubsubspec_test_my_data_element1.AddLabel("Instance", "MyInterface_my_data_element1", SilKit::Services::MatchingLabel::Kind::Mandatory);
  auto receptionHandler_test_my_data_element1 = [&](auto* subscriber, const auto& dataMessageEvent) {
    const std::lock_guard<std::mutex> lock(cached_test_my_data_element1_mutex_);
    SilKit::Util::SerDes::Deserializer deserializer(SilKit::Util::ToStdVector(dataMessageEvent.data));
    std::vector<std::uint8_t> eventData = deserializer.Deserialize<std::vector<uint8_t>>();

    std::unique_ptr< std::uint64_t > ptr;
    protobuf::interface::test::MyInterface::my_data_element1  deserialized;
    deserialized.ParseFromArray( eventData.data(), eventData.size() );
    ptr = std::make_unique< std::uint64_t >();
    ::protobuf::interface::test::MyInterface::my_data_element1ProtoToVaf(deserialized,*ptr);
    this->cached_test_my_data_element1_ = vaf::ConstDataPtr<const std::uint64_t>{std::move(ptr)};

    for(auto& handler_container : registered_test_my_data_element1_event_handlers_) {
      if(handler_container.is_active_) {
        handler_container.handler_(cached_test_my_data_element1_);
      }
    }
  };
  subscriber_test_my_data_element1_= participant_->CreateDataSubscriber("Subscriber_test_my_data_element1", pubsubspec_test_my_data_element1, receptionHandler_test_my_data_element1);

  SilKit::Services::PubSub::PubSubSpec pubsubspec_test_my_data_element2{"MyInterface_my_data_element2", SilKit::Util::SerDes::MediaTypeData()};
  pubsubspec_test_my_data_element2.AddLabel("Instance", "MyInterface_my_data_element2", SilKit::Services::MatchingLabel::Kind::Mandatory);
  auto receptionHandler_test_my_data_element2 = [&](auto* subscriber, const auto& dataMessageEvent) {
    const std::lock_guard<std::mutex> lock(cached_test_my_data_element2_mutex_);
    SilKit::Util::SerDes::Deserializer deserializer(SilKit::Util::ToStdVector(dataMessageEvent.data));
    std::vector<std::uint8_t> eventData = deserializer.Deserialize<std::vector<uint8_t>>();

    std::unique_ptr< std::uint64_t > ptr;
    protobuf::interface::test::MyInterface::my_data_element2  deserialized;
    deserialized.ParseFromArray( eventData.data(), eventData.size() );
    ptr = std::make_unique< std::uint64_t >();
    ::protobuf::interface::test::MyInterface::my_data_element2ProtoToVaf(deserialized,*ptr);
    this->cached_test_my_data_element2_ = vaf::ConstDataPtr<const std::uint64_t>{std::move(ptr)};

    for(auto& handler_container : registered_test_my_data_element2_event_handlers_) {
      if(handler_container.is_active_) {
        handler_container.handler_(cached_test_my_data_element2_);
      }
    }
  };
  subscriber_test_my_data_element2_= participant_->CreateDataSubscriber("Subscriber_test_my_data_element2", pubsubspec_test_my_data_element2, receptionHandler_test_my_data_element2);


  SilKit::Services::Rpc::RpcSpec rpcspec_test_MyVoidOperation{"MyInterface_MyVoidOperation", SilKit::Util::SerDes::MediaTypeRpc()};
  rpcspec_test_MyVoidOperation.AddLabel("Instance", "MyInterface_MyVoidOperation", SilKit::Services::MatchingLabel::Kind::Mandatory);
  auto ReturnFunc_test_MyVoidOperation = [&](auto* /*client*/, const auto& event) {
    ::vaf::Promise<void>*
        promise_pointer = static_cast<
          ::vaf::Promise<void>*>(
            event.userContext);
    if (event.callStatus == SilKit::Services::Rpc::RpcCallStatus::Success) {
      SilKit::Util::SerDes::Deserializer deserializer(SilKit::Util::ToStdVector(event.resultData));
      std::vector<std::uint8_t> result_vector = deserializer.Deserialize<std::vector<uint8_t>>();
      promise_pointer->set_value();
    } else {
      vaf::Error error_code{::vaf::ErrorCode::kDefaultErrorCode, "Rpc call failed"};
      promise_pointer->SetError(error_code);
    }
    delete promise_pointer;
  };
  rpc_client_test_MyVoidOperation_= participant_->CreateRpcClient("test_MyVoidOperation", rpcspec_test_MyVoidOperation, ReturnFunc_test_MyVoidOperation);

  SilKit::Services::Rpc::RpcSpec rpcspec_test_MyOperation{"MyInterface_MyOperation", SilKit::Util::SerDes::MediaTypeRpc()};
  rpcspec_test_MyOperation.AddLabel("Instance", "MyInterface_MyOperation", SilKit::Services::MatchingLabel::Kind::Mandatory);
  auto ReturnFunc_test_MyOperation = [&](auto* /*client*/, const auto& event) {
    ::vaf::Promise<test::MyOperation::Output>*
        promise_pointer = static_cast<
          ::vaf::Promise<test::MyOperation::Output>*>(
            event.userContext);
    if (event.callStatus == SilKit::Services::Rpc::RpcCallStatus::Success) {
      SilKit::Util::SerDes::Deserializer deserializer(SilKit::Util::ToStdVector(event.resultData));
      std::vector<std::uint8_t> result_vector = deserializer.Deserialize<std::vector<uint8_t>>();
      test::MyOperation::Output output;
      protobuf::interface::test::MyInterface::MyOperation_out deserialized;
      deserialized.ParseFromArray( result_vector.data(), result_vector.size() );
      ::protobuf::interface::test::MyInterface::MyOperationOutProtoToVaf(deserialized, output);
      promise_pointer->set_value(output);
    } else {
      vaf::Error error_code{::vaf::ErrorCode::kDefaultErrorCode, "Rpc call failed"};
      promise_pointer->SetError(error_code);
    }
    delete promise_pointer;
  };
  rpc_client_test_MyOperation_= participant_->CreateRpcClient("test_MyOperation", rpcspec_test_MyOperation, ReturnFunc_test_MyOperation);

  SilKit::Services::Rpc::RpcSpec rpcspec_test_MyGetter{"MyInterface_MyGetter", SilKit::Util::SerDes::MediaTypeRpc()};
  rpcspec_test_MyGetter.AddLabel("Instance", "MyInterface_MyGetter", SilKit::Services::MatchingLabel::Kind::Mandatory);
  auto ReturnFunc_test_MyGetter = [&](auto* /*client*/, const auto& event) {
    ::vaf::Promise<test::MyGetter::Output>*
        promise_pointer = static_cast<
          ::vaf::Promise<test::MyGetter::Output>*>(
            event.userContext);
    if (event.callStatus == SilKit::Services::Rpc::RpcCallStatus::Success) {
      SilKit::Util::SerDes::Deserializer deserializer(SilKit::Util::ToStdVector(event.resultData));
      std::vector<std::uint8_t> result_vector = deserializer.Deserialize<std::vector<uint8_t>>();
      test::MyGetter::Output output;
      protobuf::interface::test::MyInterface::MyGetter_out deserialized;
      deserialized.ParseFromArray( result_vector.data(), result_vector.size() );
      ::protobuf::interface::test::MyInterface::MyGetterOutProtoToVaf(deserialized, output);
      promise_pointer->set_value(output);
    } else {
      vaf::Error error_code{::vaf::ErrorCode::kDefaultErrorCode, "Rpc call failed"};
      promise_pointer->SetError(error_code);
    }
    delete promise_pointer;
  };
  rpc_client_test_MyGetter_= participant_->CreateRpcClient("test_MyGetter", rpcspec_test_MyGetter, ReturnFunc_test_MyGetter);

  SilKit::Services::Rpc::RpcSpec rpcspec_test_MySetter{"MyInterface_MySetter", SilKit::Util::SerDes::MediaTypeRpc()};
  rpcspec_test_MySetter.AddLabel("Instance", "MyInterface_MySetter", SilKit::Services::MatchingLabel::Kind::Mandatory);
  auto ReturnFunc_test_MySetter = [&](auto* /*client*/, const auto& event) {
    ::vaf::Promise<void>*
        promise_pointer = static_cast<
          ::vaf::Promise<void>*>(
            event.userContext);
    if (event.callStatus == SilKit::Services::Rpc::RpcCallStatus::Success) {
      SilKit::Util::SerDes::Deserializer deserializer(SilKit::Util::ToStdVector(event.resultData));
      std::vector<std::uint8_t> result_vector = deserializer.Deserialize<std::vector<uint8_t>>();
      promise_pointer->set_value();
    } else {
      vaf::Error error_code{::vaf::ErrorCode::kDefaultErrorCode, "Rpc call failed"};
      promise_pointer->SetError(error_code);
    }
    delete promise_pointer;
  };
  rpc_client_test_MySetter_= participant_->CreateRpcClient("test_MySetter", rpcspec_test_MySetter, ReturnFunc_test_MySetter);

  ReportOperational();
}

void MyConsumerModule::Stop() noexcept {
}

void MyConsumerModule::DeInit() noexcept {
}

void MyConsumerModule::StartEventHandlerForModule(const std::string& module) {
  for(auto& handler_container : registered_test_my_data_element1_event_handlers_) {
    if(handler_container.owner_ == module) {
      handler_container.is_active_ = true;
    }
  }
  for(auto& handler_container : registered_test_my_data_element2_event_handlers_) {
    if(handler_container.owner_ == module) {
      handler_container.is_active_ = true;
    }
  }
  active_modules_.push_back(module);
}

void MyConsumerModule::StopEventHandlerForModule(const std::string& module) {
  for(auto& handler_container : registered_test_my_data_element1_event_handlers_) {
    if(handler_container.owner_ == module) {
      handler_container.is_active_ = false;
    }
  }
  for(auto& handler_container : registered_test_my_data_element2_event_handlers_) {
    if(handler_container.owner_ == module) {
      handler_container.is_active_ = false;
    }
  }
  static_cast<void>(std::remove(active_modules_.begin(), active_modules_.end(), module));
}


::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>> MyConsumerModule::GetAllocated_my_data_element1() {
  ::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>> result_value{
      ::vaf::Error{::vaf::ErrorCode::kNoSampleAvailable, "No sample available"}};
  const std::lock_guard<std::mutex> lock(cached_test_my_data_element1_mutex_);
  if (cached_test_my_data_element1_) {
    result_value = ::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>>{cached_test_my_data_element1_};
  }
  return result_value;
}

std::uint64_t MyConsumerModule::Get_my_data_element1() {
  std::uint64_t return_value{};
  const std::lock_guard<std::mutex> lock(cached_test_my_data_element1_mutex_);
  if (cached_test_my_data_element1_) {
    return_value = *cached_test_my_data_element1_;
  }
  return return_value;
}

void MyConsumerModule::RegisterDataElementHandler_my_data_element1(std::string owner, std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>&& f) {
  registered_test_my_data_element1_event_handlers_.emplace_back(owner, std::move(f));
  if(std::find(active_modules_.begin(), active_modules_.end(), owner) != active_modules_.end()) {
    registered_test_my_data_element1_event_handlers_.back().is_active_ = true;
  }
}


::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>> MyConsumerModule::GetAllocated_my_data_element2() {
  ::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>> result_value{
      ::vaf::Error{::vaf::ErrorCode::kNoSampleAvailable, "No sample available"}};
  const std::lock_guard<std::mutex> lock(cached_test_my_data_element2_mutex_);
  if (cached_test_my_data_element2_) {
    result_value = ::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>>{cached_test_my_data_element2_};
  }
  return result_value;
}

std::uint64_t MyConsumerModule::Get_my_data_element2() {
  std::uint64_t return_value{};
  const std::lock_guard<std::mutex> lock(cached_test_my_data_element2_mutex_);
  if (cached_test_my_data_element2_) {
    return_value = *cached_test_my_data_element2_;
  }
  return return_value;
}

void MyConsumerModule::RegisterDataElementHandler_my_data_element2(std::string owner, std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>&& f) {
  registered_test_my_data_element2_event_handlers_.emplace_back(owner, std::move(f));
  if(std::find(active_modules_.begin(), active_modules_.end(), owner) != active_modules_.end()) {
    registered_test_my_data_element2_event_handlers_.back().is_active_ = true;
  }
}



::vaf::Future<void> MyConsumerModule::MyVoidOperation(const std::uint64_t& in) {
  ::vaf::Future<void> return_value;
  ::vaf::Promise<void>* promise_pointer =
                  new ::vaf::Promise<void>();
  return_value = promise_pointer->get_future();
  protobuf::interface::test::MyInterface::MyVoidOperation_in request;
  protobuf::interface::test::MyInterface::MyVoidOperationInVafToProto(in, request);
  size_t nbytes = request.ByteSizeLong();
  std::vector<std::uint8_t> serialized(nbytes);
  if (nbytes) {
    request.SerializeToArray(serialized.data(), nbytes);
  }
  SilKit::Util::SerDes::Serializer serializer;
  serializer.Serialize(serialized);

  rpc_client_test_MyVoidOperation_->Call(serializer.ReleaseBuffer(), promise_pointer);

  return return_value;
}
::vaf::Future<test::MyOperation::Output> MyConsumerModule::MyOperation(const std::uint64_t& in, const std::uint64_t& inout) {
  ::vaf::Future<test::MyOperation::Output> return_value;
  ::vaf::Promise<test::MyOperation::Output>* promise_pointer =
                  new ::vaf::Promise<test::MyOperation::Output>();
  return_value = promise_pointer->get_future();
  protobuf::interface::test::MyInterface::MyOperation_in request;
  protobuf::interface::test::MyInterface::MyOperationInVafToProto(in, inout, request);
  size_t nbytes = request.ByteSizeLong();
  std::vector<std::uint8_t> serialized(nbytes);
  if (nbytes) {
    request.SerializeToArray(serialized.data(), nbytes);
  }
  SilKit::Util::SerDes::Serializer serializer;
  serializer.Serialize(serialized);

  rpc_client_test_MyOperation_->Call(serializer.ReleaseBuffer(), promise_pointer);

  return return_value;
}
::vaf::Future<test::MyGetter::Output> MyConsumerModule::MyGetter() {
  ::vaf::Future<test::MyGetter::Output> return_value;
  ::vaf::Promise<test::MyGetter::Output>* promise_pointer =
                  new ::vaf::Promise<test::MyGetter::Output>();
  return_value = promise_pointer->get_future();
  protobuf::interface::test::MyInterface::MyGetter_in request;
  size_t nbytes = request.ByteSizeLong();
  std::vector<std::uint8_t> serialized(nbytes);
  if (nbytes) {
    request.SerializeToArray(serialized.data(), nbytes);
  }
  SilKit::Util::SerDes::Serializer serializer;
  serializer.Serialize(serialized);

  rpc_client_test_MyGetter_->Call(serializer.ReleaseBuffer(), promise_pointer);

  return return_value;
}
::vaf::Future<void> MyConsumerModule::MySetter(const std::uint64_t& a) {
  ::vaf::Future<void> return_value;
  ::vaf::Promise<void>* promise_pointer =
                  new ::vaf::Promise<void>();
  return_value = promise_pointer->get_future();
  protobuf::interface::test::MyInterface::MySetter_in request;
  protobuf::interface::test::MyInterface::MySetterInVafToProto(a, request);
  size_t nbytes = request.ByteSizeLong();
  std::vector<std::uint8_t> serialized(nbytes);
  if (nbytes) {
    request.SerializeToArray(serialized.data(), nbytes);
  }
  SilKit::Util::SerDes::Serializer serializer;
  serializer.Serialize(serialized);

  rpc_client_test_MySetter_->Call(serializer.ReleaseBuffer(), promise_pointer);

  return return_value;
}

} // namespace test
