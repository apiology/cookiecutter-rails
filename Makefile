.PHONY: build-typecheck bundle_install cicoverage citypecheck citest citypecoverage clean clean-build clean-coverage clean-pyc clean-typecheck clean-typecoverage coverage default gem_dependencies help overcommit quality report-coverage report-coverage-to-codecov test typecheck typecoverage update_from_cookiecutter
.DEFAULT_GOAL := default

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

default: clean-typecoverage typecheck typecoverage clean-coverage test coverage overcommit_branch quality ## run default typechecking, tests and quality

SOURCE_FILE_GLOBS = ['{tests,hooks}/**/*.py']

SOURCE_FILES := $(shell ruby -e "puts Dir.glob($(SOURCE_FILE_GLOBS))")

types.installed: Gemfile.lock Gemfile.lock.installed ## Ensure typechecking dependencies are in place
	touch types.installed

build-typecheck: types.installed  ## Fetch information that type checking depends on

clean-typecheck: ## Refresh the easily-regenerated information that type checking depends on
	rm -fr .mypy_cache
	rm -f types.installed
	echo all clear

realclean-typecheck: clean-typecheck ## Remove all type checking artifacts

realclean: clean realclean-typecheck
	rm -fr vendor .bundle
	rm .make/*
	rm *.installed

# https://app.circleci.com/pipelines/github/apiology/cookiecutter-pypackage/281/workflows/b85985a9-16d0-42c4-93d4-f965a111e090/jobs/366
typecheck: build-typecheck ## run mypy against project
	mypy --cobertura-xml-report typecover --html-report typecover hooks tests

citypecheck: typecheck ## Run type check from CircleCI

typecoverage: typecheck ## Run type checking and then ratchet coverage in metrics/mypy_high_water_mark
	@python setup.py mypy_ratchet

clean-typecoverage: ## Clean out mypy previous results to avoid flaky results

ratchet-typecoverage: ## Run type checking, ratchet coverage, and then complain if ratchet needs to be committed
	@echo "Looking for un-checked-in type coverage metrics..."
	@git status --porcelain metrics/mypy_high_water_mark
	@test -z "$$(git status --porcelain metrics/mypy_high_water_mark)"

citypecoverage: ratchet-typecoverage ## Run type checking, ratchet coverage, and then complain if ratchet needs to be committed

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

config/env: config/env.1p  ## Create file suitable for docker-compose usage
	cat config/env.1p | cut -d= -f1 > config/env

requirements_dev.txt.installed: requirements_dev.txt
	pip install -q --disable-pip-version-check -r requirements_dev.txt
	touch requirements_dev.txt.installed

pip_install: requirements_dev.txt.installed ## Install Python dependencies

Gemfile.lock: Gemfile
	make .bundle/config
	bundle lock

.bundle/config:
	touch .bundle/config

gem_dependencies: .bundle/config

# Ensure any Gemfile.lock changes, even pulled from git, ensure a
# bundle is installed.
Gemfile.lock.installed: Gemfile vendor/.keep
	touch Gemfile.lock.installed

vendor/.keep: Gemfile.lock
	make gem_dependencies
	bundle install
	touch vendor/.keep

bundle_install: Gemfile.lock.installed ## Install Ruby dependencies

lint: ## check style with flake8
	flake8 hooks tests

test-all: ## run tests on every Python version with tox
	tox

clean: clean-build clean-pyc clean-test clean-typecoverage clean-typecheck clean-coverage ## remove all build, test, coverage and Python artifacts

test: ## run tests quickly
	pytest --maxfail=1 tests/test_bake_project.py --capture=no -v

citest:  ## Run unit tests from CircleCI
	pytest --maxfail=1 tests/test_bake_project.py -v

overcommit: ## run precommit quality checks
	bundle exec overcommit --run

overcommit_branch: ## run precommit quality checks only on changed files
	@bundle exec overcommit_branch

quality: lint overcommit ## run precommit quality checks

bake: ## generate project using defaults
	cookiecutter $(BAKE_OPTIONS) . --overwrite-if-exists

watch: bake ## generate project using defaults and watch for changes
	watchmedo shell-command -p '*.*' -c 'make bake -e BAKE_OPTIONS=$(BAKE_OPTIONS)' -W -R -D \cookiecutter-rails/

replay: BAKE_OPTIONS=--replay ## replay last cookiecutter run and watch for changes
replay: watch
	;

repl: ## Launch an interactive development shell
	python

clean-coverage: ## Clean out previous output of test coverage to avoid flaky results from previous runs

coverage: test report-coverage ## check code coverage

report-coverage: citest ## Report summary of coverage to stdout, and generate HTML, XML coverage report

update_apt: .make/apt_updated

.make/apt_updated:
	sudo DEBIAN_FRONTEND=noninteractive apt-get update -y
	touch .make/apt_updated

cicoverage: citest ## check code coverage

update_from_cookiecutter: ## Bring in changes from template project used to create this repo
	bundle exec overcommit --uninstall
	git checkout main && git pull && git checkout -b update-from-upstream-cookiecutter-$$(date +%Y-%m-%d-%H%M)
	git fetch cookiecutter-upstream
	git fetch -a
	git merge cookiecutter-upstream/main --allow-unrelated-histories || true
	# update frequently security-flagged gems while we're here
	bundle update --conservative rexml || true
	make build-typecheck
	bundle install || true
	git add Gemfile.lock || true
	bundle exec overcommit --install || true
	@echo
	@echo "Please resolve any merge conflicts below and push up a PR with:"
	@echo
	@echo '   gh pr create --title "Update from upstream" --body "Automated PR to update from upstream"'
	@echo
	@echo
