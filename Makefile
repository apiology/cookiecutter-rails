.PHONY: clean test help typecheck quality
.DEFAULT_GOAL := default

BAKE_OPTIONS=--no-input

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

default: clean-coverage test coverage clean-typecoverage typecheck typecoverage quality ## run default typechecking, tests and quality

typecheck: ## validate types in code and configuration

citypecheck: typecheck ## Run type check from CircleCI

typecoverage: typecheck ## Run type checking and then ratchet coverage in metrics/

clean-typecoverage: ## Clean out type-related coverage previous results to avoid flaky results

citypecoverage: typecoverage ## Run type checking, ratchet coverage, and then complain if ratchet needs to be committed

requirements_dev.txt.installed: requirements_dev.txt
	pip install -q --disable-pip-version-check -r requirements_dev.txt
	touch requirements_dev.txt.installed

pip_install: requirements_dev.txt.installed ## Install Python dependencies

# bundle install doesn't get run here so that we can catch it below in
# fresh-checkout and fresh-rbenv cases
Gemfile.lock: Gemfile

# Ensure any Gemfile.lock changes ensure a bundle is installed.
Gemfile.lock.installed: Gemfile.lock
	bundle install
	touch Gemfile.lock.installed

bundle_install: Gemfile.lock.installed ## Install Ruby dependencies

clean: ## remove all built artifacts

test: ## run tests quickly
	pytest --maxfail=0

citest: test ## Run unit tests from CircleCI

overcommit: ## run precommit quality checks
	bundle exec overcommit --run

quality: overcommit ## run precommit quality checks

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

bake: ## generate project using defaults
	cookiecutter $(BAKE_OPTIONS) . --overwrite-if-exists

watch: bake ## generate project using defaults and watch for changes
	watchmedo shell-command -p '*.*' -c 'make bake -e BAKE_OPTIONS=$(BAKE_OPTIONS)' -W -R -D \cookiecutter-rails/

replay: BAKE_OPTIONS=--replay ## replay last cookiecutter run and watch for changes
replay: watch
	;

clean-coverage: ## Clean out previous output of test coverage to avoid flaky results from previous runs

coverage: test report-coverage ## check code coverage

report-coverage: test ## Report summary of coverage to stdout, and generate HTML, XML coverage report

report-coverage-to-codecov: report-coverage ## use codecov.io for PR-scoped code coverage reports

cicoverage: report-coverage-to-codecov ## check code coverage, then report to codecov

update_from_cookiecutter: ## Bring in changes from template project used to create this repo
	bundle exec overcommit --uninstall
	git checkout main && git pull && git checkout -b update-from-upstream-cookiecutter-$$(date +%Y-%m-%d-%H%M)
	git fetch cookiecutter-upstream
	git fetch -a
	git merge cookiecutter-upstream/main --allow-unrelated-histories || true
	bundle exec overcommit --install || true
	@echo
	@echo "Please resolve any merge conflicts below and push up a PR with:"
	@echo
	@echo '   gh pr create --title "Update from upstream" --body "Automated PR to update from upstream"'
	@echo
	@echo
