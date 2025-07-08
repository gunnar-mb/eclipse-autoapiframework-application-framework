namespace :dev do

  desc "DEV: Initialize Project"
  namespace :init do
    task_name = ["install-all", "format", "lint"]
    descriptions = ["Installing", "Formatting", "Run Linters in"]

    task_name.each_with_index do |dev_task, index|
      desc "DEV: #{descriptions[index]} VAF Python Project"
      task dev_task.split("-")[0] do
        Dir.chdir("VAF") do
          sh "make #{dev_task}"
        end
      end
    end

    desc "DEV: #{descriptions[1]} and #{descriptions[2]} VAF Python Project"
    task precommit: %i[format lint]
  end

  desc "DEV: Run test suites in Project"
  namespace :test do

    namespace :unit do
      unit_tests = ["cli-core", "vafarxmltojson", "vafgeneration", "vafjsontoarxml", "vafmodel", "vafpy", "vafvssimport"]
      unit_tests.each do |ut|
        desc "DEV: Run Unit Test for #{ut} in Project"
        task ut do
          Dir.chdir("VAF") do
            sh "make test-unit-#{ut}"
          end
        end
      end

      desc "DEV: Run ALL Unit Test in Project"
      task :all do
        Dir.chdir("VAF") do
          sh "make test-unit"
        end
      end
    end

    namespace :component do
      comp_tests = ["cli"]
      comp_tests.each do |ct|
        desc "DEV: Run Component Test for #{ct} in Project"
        task ct do
          Dir.chdir("VAF") do
            sh "make test-component-#{ct}"
          end
        end
      end

      desc "DEV: Run ALL Component Test in Project"
      task :all do
        Dir.chdir("VAF") do
          sh "make test-component"
        end
      end
    end

    desc "DEV: Run ALL test suites in Project"
    task all: %i[unit:all component:all]
  end

  desc "DEV: Rake job for Pipeline"
  task pipeline: %i[init:precommit test:all]
end

namespace :prod do
  namespace :patch do
    desc 'Patches the vafcpp in project conanfile'
    task :project_vafcpp_version, [:version] do |t, args|
      if args[:version].nil?
        # Retrieve the current vafcpp version installed, we need that version later
        # to patch the conanfile.py
        vafcpp_version_info = `conan list vafcpp -f json`
        vafcpp_version = JSON.parse(vafcpp_version_info)['Local Cache'].keys.first
      else
        vafcpp_version = "vafcpp/#{args[:version]}"
      end
      puts "#{vafcpp_version}"

      files_to_patch = ["project/default/{{project_name}}/conanfile.py", "application_module/{{module_dir_name}}/conanfile.py"]
      files_to_patch.each do |file|
        location = "./VAF/src/vaf/cli_core/bootstrap/templates/#{file}"
        conanfile = IO.read(location)
        conanfile.gsub!(%r{"vafcpp/.+"}, "\"#{vafcpp_version}\"")
        File.open(location, 'w') do |fh|
          fh.write(conanfile)
        end
      end
    end

    desc 'Patches the container version in project devcontainer.json'
    task :project_dev_container_json, [:version] do |t, args|
      unless args[:version].nil?
        files_to_patch = ["workspace/{{workspace_name}}/.devcontainer/devcontainer.json.jinja"]

        files_to_patch.each do |file|
          location = "./VAF/src/vaf/cli_core/bootstrap/templates/#{file}"
          devcontainer = IO.read(location)
          devcontainer.gsub!(/devcontainer:latest"/, "devcontainer:#{args[:version]}\"")
          File.open(location, 'w') do |fh|
            fh.write(devcontainer)
          end
        end
      end
    end
  end

  namespace :install do
    desc 'PROD: Install vaf wheel with pip'
    task :vafcli do
      path_to_vafinstall = "_vafinstall"
      FileUtils.rm_rf(path_to_vafinstall)
      FileUtils.mkdir_p(path_to_vafinstall)

      Dir.chdir("VAF") do
        sh 'make clean build'
      end
      wheel = Dir.glob('VAF/dist/*.whl')[0]
      cp wheel, path_to_vafinstall
      sh 'pip3 install _vafinstall/vaf-*.whl --force-reinstall --break-system-packages'
    end

    desc 'PROD: Install vafcpp'
    task :vafcpp, [:version] do |t, args|
      Dir.chdir('SwLibraries/vaf_core_library') do
        conan_cmd = []
        conan_cmd << 'conan create .'
        conan_cmd << '--profile:host=test_package/gcc12__x86_64-pc-linux-elf'
        conan_cmd << '--profile:build=test_package/gcc12__x86_64-pc-linux-elf'
        conan_cmd << "--version #{args[:version]}" unless args[:version].nil?

        #sh (conan_cmd + ['-s build_type=Debug']).join(' ')
        sh (conan_cmd + ['-s build_type=Release']).join(' ')
      end
    end
  end
end
