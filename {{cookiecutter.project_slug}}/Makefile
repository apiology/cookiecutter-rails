.PHONY: build build-typecheck bundle_install cicoverage citypecheck citest citypecoverage clean clean-coverage clean-typecheck clean-typecoverage coverage default gem_dependencies help ngrok overcommit quality repl report-coverage rubocop rubocop-ratchet spec test typecheck typecoverage update_from_cookiecutter
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

default: clean-typecoverage build typecheck typecoverage clean-coverage test coverage overcommit_branch quality rubocop-ratchet ## run default typechecking, tests and quality

SOURCE_FILE_GLOBS = ['{config,lib,app,script}/**/*.rb', 'ext/**/*.{c,rb}']

SOURCE_FILES := $(shell ruby -e "puts Dir.glob($(SOURCE_FILE_GLOBS))")

start: ## run code continously and watch files for changes
	echo "Teach me how to 'make start'"
	exit 1

rbi/{{cookiecutter.project_slug}}.rbi: yardoc.installed ## Generate Sorbet types from Yard docs
	rm -f rbi/{{cookiecutter.project_slug}}.rbi
	bundle exec sord --replace-errors-with-untyped --exclude-messages OMIT --no-regenerate rbi/{{cookiecutter.project_slug}}.rbi

types.installed: tapioca.installed Gemfile.lock Gemfile.lock.installed rbi/{{cookiecutter.project_slug}}.rbi sorbet/tapioca/require.rb sorbet/config ## Ensure typechecking dependencies are in place
	bundle exec yard gems 2>&1 || bundle exec yard gems --safe 2>&1 || bundle exec yard gems 2>&1
	# bundle exec solargraph scan 2>&1
	touch types.installed

build: bundle_install pip_install build-typecheck ## Update 3rd party packages as well and produce any artifacts needed from code

sorbet/machine_specific_config:
	echo "--cache-dir=$$HOME/.sorbet-cache" > sorbet/machine_specific_config

build-typecheck: Gemfile.lock.installed types.installed  ## Fetch information that type checking depends on

sorbet/tapioca/require.rb: sorbet/machine_specific_config
	bin/tapioca init

tapioca.installed: sorbet/machine_specific_config sorbet/tapioca/require.rb Gemfile.lock.installed db/schema.rb ## Install Tapioca-generated type information
	bin/tapioca gems
	bin/tapioca annotations
	if [ -f db/schema.rb ]; then \
	  RAILS_ENV=development bin/rails db:create; \
	  RAILS_ENV=development bin/rails db:migrate; \
	  bin/tapioca dsl; \
	fi
	bin/tapioca todo
	bin/spoom srb bump
	touch tapioca.installed

db/schema.rb:

yardoc.installed: $(wildcard config/annotations_*.rb) $(SOURCE_FILES) ## Generate YARD documentation
	bin/yard doc $?
	touch yardoc.installed

clean-typecheck: ## Refresh the easily-regenerated information that type checking depends on
	bin/solargraph clear || true
	rm -fr .yardoc/ rbi/{{cookiecutter.project_slug}}.rbi types.installed yardoc.installed
{% if cookiecutter.use_checkoff %}	rm -fr ../checkoff/.yardoc || true
{% endif %}	echo all clear

realclean-typecheck: clean-typecheck ## Remove all type checking artifacts
	rm -fr ~/.cache/solargraph
	rm tapioca.installed

realclean: clean realclean-typecheck
	rm -fr vendor/bundle .bundle
	rm -f .make/*
	rm -f *.installed

typecheck: build-typecheck ## validate types in code and configuration
	bin/srb tc
	bin/solargraph typecheck --level strong

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

config/env: config/env.1p  ## Create file suitable for docker-compose usage
	cat config/env.1p | cut -d= -f1 > config/env

config/env.rails: config/env.rails.1p
	cat config/env.rails.1p | cut -d= -f1 > config/env.rails

requirements_dev.txt.installed: requirements_dev.txt
	pip install -q --disable-pip-version-check -r requirements_dev.txt
	touch requirements_dev.txt.installed

pip_install: requirements_dev.txt.installed ## Install Python dependencies

Gemfile.lock: Gemfile
	make .bundle/config
	bundle lock

.make/pg_gem_dependencies:
	for possible_pg_config_path in /opt/homebrew/Cellar/postgresql@16/16.*/bin/pg_config /opt/homebrew/opt/libpq/bin/pg_config ; \
	do \
	  if [ -f "$${possible_pg_config_path}" ]; \
	  then \
	    bundle config set build.pg --with-pg-config="$${possible_pg_config_path}"; \
	  fi \
	done
	touch .make/pg_gem_dependencies

.make/psych_gem_dependencies:
	set -e; \
	if (bin/bundle check --dry-run 2>&1 || true) | grep ' \* psych' >/dev/null; \
	then \
	  echo "Installing requirements for psych"; \
	  bin/ensure_dev_library yaml.h libyaml libyaml-dev; \
	  bin/ensure_package pkg-config; \
	fi
	touch .make/psych_gem_dependencies

gem_dependencies: .bundle/config .make/psych_gem_dependencies .make/pg_gem_dependencies

# Ensure any Gemfile.lock changes, even pulled from git, ensure a
# bundle is installed.
Gemfile.lock.installed: Gemfile vendor/.keep
	touch Gemfile.lock.installed

vendor/.keep: Gemfile.lock
	make gem_dependencies
	bundle install
	touch vendor/.keep

.bundle/config: .make/pg_gem_dependencies
	touch .bundle/config

bundle_install: Gemfile.lock.installed ## Install Ruby dependencies

clear_metrics: ## remove or reset result artifacts created by tests and quality tools
	bundle exec rake clear_metrics || true

clean: clear_metrics clean-typecoverage clean-typecheck clean-coverage ## remove all built artifacts

test: spec ## run tests quickly

citest: test ## Run unit tests from CircleCI

overcommit: ## run precommit quality checks
	bundle exec overcommit --run

overcommit_branch: ## run precommit quality checks only on changed files
	@bundle exec overcommit_branch

quality: overcommit ## run precommit quality checks

rubocop: ## Run rubocop
	@bundle exec rubocop

rubocop-ratchet: rubocop ## Run rubocop and then ratchet numbers of errors in todo file
	@bundle exec rubocop --regenerate-todo --no-exclude-limit --auto-gen-only-exclude --no-auto-gen-timestamp
	@if [ -f .rubocop_todo.yml ]; \
	  then \
	    git diff --exit-code .rubocop.yml; \
	    git diff --exit-code .rubocop_todo.yml; \
	fi

test: spec ## run tests quickly

spec: ## Run lower-level tests
	@bundle exec rake spec

repl: bundle_install ## Launch an interactive development shell
	rails c

clean-coverage: clear_metrics ## Clean out previous output of test coverage to avoid flaky results from previous runs

coverage: test report-coverage ## check code coverage
	@bundle exec rake undercover

report-coverage: test ## Report summary of coverage to stdout, and generate HTML, XML coverage report

update_apt: .make/apt_updated

.make/apt_updated:
	sudo DEBIAN_FRONTEND=noninteractive apt-get update -y
	touch .make/apt_updated

cicoverage: citest coverage ## check code coverage

ngrok: ## Start ngrok to expose local server to the internet
	@ngrok http http://localhost:3000 >/dev/null 2>&1 || true # brew install ngrok/ngrok/ngrok
	@sleep 2
	@echo "Configure [app components](https://app.asana.com/0/my-apps/895499885393836/rule-actions) with the URL provided:" >&2
	@curl --silent http://127.0.0.1:4040/api/tunnels | jq -r '.tunnels[] | select(.config.addr == "http://localhost:3000") | .public_url'


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
	bundle update --conservative json nokogiri rexml yard rails-html-sanitizer || true
	( make build && git add Gemfile.lock ) || true
	bundle exec overcommit --install || true
	@echo
	@echo "Please resolve any merge conflicts below and push up a PR with:"
	@echo
	@echo '   gh pr create --title "Update from cookiecutter" --body "Automated PR to update from cookiecutter boilerplate"'
	@echo
	@echo
