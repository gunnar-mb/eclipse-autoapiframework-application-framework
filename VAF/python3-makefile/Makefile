# utility functions (OS dependent if necessary)
OS ?= $(shell uname)
PYTHON_VERSION ?= 3.12
ifeq ($(OS),Windows_NT)
	rm_if_exist = if exist $(1) rm -rf $(1)
endif
ifeq ($(OS),Linux)
	rm_if_exist = if [ -e $(1) ] ; then rm -rf $(1) ; fi ;
endif
rwildcard=$(foreach d,$(wildcard $1*),$(call rwildcard,$d/,$2) $(filter $(subst *,%,$2),$d))


# fail test job if branch coverage is below a specific value
# should be set via CI-variables
ifeq ($(COV_FAIL_UNDER),)
	COV_FAIL_UNDER=100
endif

.PHONY: staging-version release-version install install-extras-test check-format format lint test traceability remove build release clean


.venv:
ifdef CI
# In CI we want to make use of the specified interpreter
	pdm venv create ${PYTHON_VERSION}
else
# Locally we want to use the Python interpreter at hand
	pdm venv create
endif

.pdm.toml: .venv
	pdm use --ignore-remembered --first ./.venv

staging-version:
	@echo "This function is deprecated. Just used as placeholder for the pipeline-template"

release-version:
	@echo "This function is deprecated. Just used as placeholder for the pipeline-template"

install:
# SHELL=sh.exe only inside Makefile on Windows cmd/powershell
ifeq ($(SHELL), sh.exe)
	@powershell Write-Host "Testing package installation in venv install-deploy. To create a development venv, please use " -ForegroundColor Red; Write-Host "make install-all" -ForegroundColor Green;
	@powershell 'if (pdm venv list | Select-String -Pattern "install-deploy") { pdm venv remove install-deploy -y }'
# Git Bash/Linux Shell
else
	@echo -e "\e[31mTesting package installation in venv install-deploy\e[m. To create a development venv, please use \e[32mmake install-all\e[m"
	@if pdm venv list | grep -q "install-deploy"; then \
		pdm venv remove install-deploy -y; \
	fi
endif
	pdm venv create --with-pip --name install-deploy ${PYTHON_VERSION}
	pdm run --venv install-deploy pip install .

install-all: .pdm.toml
	pdm install

install-coverage: .pdm.toml
	pdm export --format requirements --without-hashes --output requirements.tmp
	cat requirements.tmp | grep coverage | xargs pdm run pip --python $(shell pdm run python -c 'import sys;print(sys.executable)')  install
	rm requirements.tmp

install-extras-test:
	@echo "Call to deprecated target install-extras-test"

check-format: install-all
	pdm run ruff format --check --diff

format: install-all
	pdm run ruff format
	pdm run ruff check --fix

lint: install-all
	@EXIT_CODE=0; \
	pdm run ruff check || EXIT_CODE=$$?; \
	pdm run pylint src/ || EXIT_CODE=$$?; \
	pdm run pylint tests/ || EXIT_CODE=$$?; \
	pdm run mypy --install-types --non-interactive || EXIT_CODE=$$?; \
	if [ $$EXIT_CODE -ne 0 ]; then exit 1; fi

remove:
	@echo "This function is deprecated. Just used as placeholder for the pipeline-template"

build:
	pdm install --plugins
	pdm build

coverage-verify: install-coverage
	@echo "This target verifies the latest coverage result against COV_FAIL_UNDER. However, only on CI the merged coverage from all Python versions and platforms is considered."
	pdm run coverage report --precision 2 --fail-under ${COV_FAIL_UNDER}

coverage-report: install-coverage
	pdm run coverage combine $(wildcard .coverage.*)
	pdm run coverage xml
	# the following sed hack ensures that coverage.xml is parsed correctly by GitLab
	# [tool.coverage.run] relative_files=true breaks GitLab's automatic path correction otherwise
	# see here: https://docs.gitlab.com/ee/ci/testing/test_coverage_visualization.html#automatic-class-path-correction
	sed -iE "s%<source>\(.*\)</source>%<source>${CI_PROJECT_DIR}/\1</source>%" coverage.xml
	pdm run coverage html --precision 2
	pdm run coverage report --precision 2

release:
	pdm publish --username ${ARTIFACTORY_USER} --password ${ARTIFACTORY_PASSWORD} --repository ${PYPI_REPOSITORY} --no-build

clean:
	@$(foreach path, $(call rwildcard, *, *.py[co]), $(call rm_if_exist, ${path}))
	@$(foreach path, $(call rwildcard, *, *__pycache__), $(call rm_if_exist, ${path}))
	@$(call rm_if_exist, __pypackages__)
	@$(call rm_if_exist, dist)
	@$(call rm_if_exist, report.xml)
	@$(call rm_if_exist, htmlcov)
	@$(call rm_if_exist, .pdm.toml)
	@$(call rm_if_exist, .pypy_cache)
	@$(call rm_if_exist, .pytest_cache)
	@$(call rm_if_exist, .mypy_cache)
	@$(call rm_if_exist, .coverage)
	@$(call rm_if_exist, .venv)
	@$(call rm_if_exist, .tox)
