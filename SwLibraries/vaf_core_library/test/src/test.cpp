#include <iostream>
#include "vaf/future.h"
#include "vaf/internal/data_ptr_helper.h"
#include "vaf/result.h"
#include "vaf/logging.h"

int main() {
    vaf::Result<void> r1;
    vaf::Result<int> r2{1};

    vaf::Promise<int> p;
    vaf::Future<int> f{p.get_future()};
    p.set_value(1);

    std::unique_ptr<double> test_unique_ptr{new double(21.21)};
    vaf::DataPtr<double> myDataPtr{std::move(test_unique_ptr)};

    if (test_unique_ptr) std::cout << "1 - The result of test_unique_ptr is: " << *test_unique_ptr << std::endl;

    test_unique_ptr.release();

    if (test_unique_ptr) std::cout << "2 - The result of test_unique_ptr is: " << *test_unique_ptr << std::endl;

    test_unique_ptr = vaf::internal::DataPtrHelper<double>::getRawPtr(myDataPtr);

    if (test_unique_ptr) std::cout << "3 - The result of test_unique_ptr is: " << *test_unique_ptr << std::endl;

    vaf::LoggerSingleton::getInstance()->SetLogLevelVerbose();

    vaf::Logger &logger_ = vaf::CreateLogger("MyID", "MyLogger");

    logger_.LogFatal() << "This is my Test Logging1";

    logger_.LogDebug() << "This is my Test Logging2 " << 13 << " That is a number";

    std::cout << std::flush;

    vaf::LoggerSingleton::getInstance()->CleanLoggers();

    return 0;
}
