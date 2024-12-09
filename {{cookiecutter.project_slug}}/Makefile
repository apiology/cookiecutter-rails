.PHONY: build-typecheck bundle_install cicoverage citypecheck citest citypecoverage clean clean-coverage clean-typecheck clean-typecoverage coverage default feature help localtest overcommit quality repl report-coverage report-coverage-to-codecov rubocop spec test typecheck typecoverage update_from_cookiecutter
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

default: clean-coverage test coverage clean-typecoverage typecheck typecoverage quality ## run default typechecking, tests and quality

build-typecheck: types.installed ## Fetch information that type checking depends on

types.installed: Gemfile.lock Gemfile.lock.installed ## Install Ruby dependencies
	bundle exec yard gems 2>&1 || bundle exec yard gems --safe 2>&1 || bundle exec yard gems 2>&1
	# bundle exec solargraph scan 2>&1
	touch types.installed

clean-typecheck: ## Refresh information that type checking depends on
	bundle exec solargraph clear
	rm -fr .yardoc/
	echo all clear

typecheck: ## validate types in code and configuration
	bundle exec solargraph typecheck --level strong

citypecheck: typecheck ## Run type check from CircleCI

typecoverage: typecheck ## Run type checking and then ratchet coverage in metrics/

clean-typecoverage: ## Clean out type-related coverage previous results to avoid flaky results

citypecoverage: typecoverage ## Run type checking, ratchet coverage, and then complain if ratchet needs to be committed

docker-start:
	@if [ "$$(uname)" == Darwin ]; then open /Applications/Docker.app; fi
	@while ! docker pull ubuntu; do sleep 1; done

docker-all: config/env config/env.rails  ## bring up docker compose with full application (including job processing) and databases running
	docker build --platform linux/amd64 . -t apiology/{{cookiecutter.project_slug}}:latest
	DOCKER_DEFAULT_PLATFORM=linux/amd64 docker compose build
	docker compose up

docker-web: config/env config/env.rails  ## bring up docker compose with web application and databases running
	rake build_docker_precache
	docker build --platform linux/amd64 . -t apiology/{{cookiecutter.project_slug}}:latest
	DOCKER_DEFAULT_PLATFORM=linux/amd64 docker compose build
	docker compose up dev_database test_database jobs web

docker: config/env config/env.rails docker-start  ## bring up docker compose with databases running
	@docker compose up -d dev_database test_database

config/env: config/env.1p
	cat config/env.1p | cut -d= -f1 > config/env

config/env.rails: config/env.rails.1p
	cat config/env.rails.1p | cut -d= -f1 > config/env.rails

requirements_dev.txt.installed: requirements_dev.txt
	pip install -q --disable-pip-version-check -r requirements_dev.txt
	touch requirements_dev.txt.installed

pip_install: requirements_dev.txt.installed ## Install Python dependencies

Gemfile.lock: Gemfile

# Ensure any Gemfile.lock changes ensure a bundle is installed.
Gemfile.lock.installed: Gemfile.lock
	bundle install
	touch Gemfile.lock.installed

bundle_install: Gemfile.lock.installed ## Install Ruby dependencies

clear_metrics: ## remove or reset result artifacts created by tests and quality tools
	bundle exec rake clear_metrics

clean: clear_metrics ## remove all built artifacts

test: spec ## run tests quickly

citest: test ## Run unit tests from CircleCI

overcommit: ## run precommit quality checks
	bundle exec overcommit --run

quality: overcommit ## run precommit quality checks

rubocop: ## Run rubocop
	@bundle exec rubocop

test: spec ## run tests quickly

spec: ## Run lower-level tests
	@bundle exec rake spec

feature: ## Run higher-level tests
	@bundle exec rake feature

localtest: ## run default local actions
	@bundle exec rake localtest

repl:
	rails c

clean-coverage:
	@bundle exec rake clear_metrics

coverage: test report-coverage ## check code coverage
	@bundle exec rake undercover

report-coverage: test ## Report summary of coverage to stdout, and generate HTML, XML coverage report

cicoverage: coverage ## check code coverage

update_from_cookiecutter: ## Bring in changes from template project used to create this repo
	bundle exec overcommit --uninstall
	# cookiecutter_project_upgrader does its work in
	# .git/cookiecutter/{{cookiecutter.project_slug}}, but RuboCop wants to inherit
	# config from all directories above it - avoid config
	# mismatches by moving this out of the way
	mv .rubocop.yml .rubocop-renamed.yml || true
	cookiecutter_project_upgrader --help >/dev/null
	IN_COOKIECUTTER_PROJECT_UPGRADER=1 cookiecutter_project_upgrader || true
	mv .rubocop-renamed.yml .rubocop.yml
	git checkout cookiecutter-template && git push --no-verify
	git checkout main; overcommit --sign && overcommit --sign pre-commit && git checkout main && git pull && git checkout -b update-from-cookiecutter-$$(date +%Y-%m-%d-%H%M)
	git merge cookiecutter-template || true
	git checkout --ours config/credentials.yml.enc Gemfile.lock || true
	git add config/credentials.yml.enc Gemfile.lock || true
	# update frequently security-flagged gems while we're here
	bundle update --conservative rexml || true
	git add Gemfile.lock || true
	bundle install || true
	bundle exec overcommit --install || true
	@echo
	@echo "Please resolve any merge conflicts below and push up a PR with:"
	@echo
	@echo '   gh pr create --title "Update from cookiecutter" --body "Automated PR to update from cookiecutter boilerplate"'
	@echo
	@echo
