
#include <vaf/controller_interface.h>

#include <string>
#include <vector>

class MyController final : public vaf::ControlInterface {
public:
  vaf::Result<void> Init() noexcept { return vaf::Result<void>{}; }
  void Start() noexcept {}
  void Stop() noexcept {}
  void DeInit() noexcept {}
};

int main() {

  std::vector<std::string> vec;
  vec.push_back("test_package");
}
