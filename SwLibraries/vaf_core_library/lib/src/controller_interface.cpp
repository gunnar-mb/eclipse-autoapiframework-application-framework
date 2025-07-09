#include "vaf/controller_interface.h"
#include <iostream>
#include "vaf/error_domain.h"

namespace vaf {

ControlInterface::ControlInterface(std::string name, std::vector<std::string> dependencies, ExecutableControllerInterface& executable_controller_interface, vaf::Executor& executor) 
  : name_{std::move(name)},
    dependencies_{std::move(dependencies)},
    executable_controller_interface_{executable_controller_interface},
    executor_{vaf::ModuleExecutor{executor, name_, dependencies_}} {
}

void ControlInterface::ReportOperational() {
  executable_controller_interface_.ReportOperationalOfModule(name_);
}

void ControlInterface::ReportError(ErrorCode error_code, std::string msg, bool critical) {
  std::cout << "ReportError of module " << name_ << " (msg: " << msg << ")\n";
  Error error{error_code, msg.c_str()};
  executable_controller_interface_.ReportErrorOfModule(std::move(error), name_, critical);
}

void ControlInterface::OnError(const vaf::Error& error) {
  static_cast<void>(error);
  ReportError(ErrorCode::kDefaultErrorCode, "Unhandled error", true);
}

std::string ControlInterface::GetName() {
  return name_;
}

std::vector<std::string> ControlInterface::GetDependencies() {
  return dependencies_;
}

void ControlInterface::StartExecutor() {
  executor_.Start();
}

void ControlInterface::StopExecutor() {
  executor_.Stop();
}

void ControlInterface::StartEventHandlerForModule(const std::string& module_name) { 
  static_cast<void>(module_name); 
};

void ControlInterface::StopEventHandlerForModule(const std::string& module_name) { 
  static_cast<void>(module_name); 
};

} // namespace vaf
