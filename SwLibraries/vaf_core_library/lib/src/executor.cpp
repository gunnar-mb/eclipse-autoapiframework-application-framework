#include "vaf/executor.h"

#include <iostream>

namespace vaf {

    RunnableHandle::RunnableHandle(std::string name, uint64_t period, std::function<void(void)> runnable,
                                   const std::string &owner, const std::vector<std::string> &run_after, uint64_t offset,
                                   std::chrono::nanoseconds budget)
            : name_{std::move(name)},
              period_{period},
              runnable_{std::move(runnable)},
              owner_{owner},
              run_after_{run_after},
              offset_{offset},
              budget_{budget} {
    }

    const std::string &RunnableHandle::Name() const { return name_; }

    bool RunnableHandle::IsActive() const { return is_active_; }

    void RunnableHandle::Execute() const { runnable_(); }

    uint64_t RunnableHandle::Period() const { return period_; }

    void RunnableHandle::Start() { is_active_ = true; }

    void RunnableHandle::Stop() { is_active_ = false; }

    const std::string &RunnableHandle::Owner() { return owner_; }

    const std::vector<std::string> &RunnableHandle::RunAfter() { return run_after_; }

    uint64_t RunnableHandle::Offset() const { return offset_; }

    std::chrono::nanoseconds RunnableHandle::Budget() const { return budget_; }

    Executor::Executor(std::chrono::milliseconds running_period)
            : running_period_{running_period},
              thread_{[this]() { ExecutorThread(); }},
              logger_{vaf::CreateLogger("E", "Executor")} {
    }

    Executor::~Executor() {
        exit_requested_ = true;
        thread_.join();
    }

    void Executor::ExecutorThread() {
        uint64_t counter{0};
        std::chrono::steady_clock::time_point next_run{std::chrono::steady_clock::now()};
        while (!exit_requested_) {
            next_run += running_period_;

            for (std::shared_ptr<RunnableHandle> &runnable: runnables_) {
                if (runnable->IsActive()) {
                    if (counter >= runnable->Offset()) {
                        if (((counter - runnable->Offset()) % runnable->Period()) == 0) {
                            ExecuteRunnable(*runnable);
                        }
                    }
                }
            }

            if (std::chrono::steady_clock::now() > next_run) {
                logger_.LogWarn() << "Executor could no execute all runnables in time.";
            }

            ++counter;

            std::this_thread::sleep_until(next_run);
        }
    }

    void Executor::ExecuteRunnable(RunnableHandle &runnable) {
        std::chrono::nanoseconds budget = runnable.Budget();
        if (budget.count() == 0) {
            runnable.Execute();
        } else {
            auto start{std::chrono::high_resolution_clock::now()};
            runnable.Execute();
            auto end{std::chrono::high_resolution_clock::now()};
            if ((end - start) > budget) {
                logger_.LogWarn() << "Budget violation of runnable from " << runnable.Owner().c_str();
            }
        }
    }

    ModuleExecutor::ModuleExecutor(Executor &executor, std::string name, std::vector<std::string> dependencies)
            : executor_{executor},
              handles_{},
              started_{false},
              name_{std::move(name)},
              dependencies_{std::move(dependencies)} {
    }

    void ModuleExecutor::Start() {
        for (std::shared_ptr<RunnableHandle> &handle: handles_) {
            handle->Start();
        }

        started_ = true;
    }

    void ModuleExecutor::Stop() {
        for (std::shared_ptr<RunnableHandle> &handle: handles_) {
            handle->Stop();
        }

        started_ = false;
    }

} // namespace vaf
