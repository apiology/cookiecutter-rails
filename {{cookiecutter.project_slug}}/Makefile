.PHONY: build build-typecheck bundle_install cicoverage citypecheck citest citypecoverage clean clean-coverage clean-typecheck clean-typecoverage coverage default docs gem_dependencies help ngrok overcommit quality repl report-coverage rubocop rubocop-ratchet spec test typecheck typecoverage update_from_cookiecutter yard

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

SOURCE_FILE_GLOBS = ['{config,lib,app,script,spec}/**/*.rb', 'ext/**/*.{c,rb}']

SOURCE_FILES := $(shell ruby -e "puts Dir.glob($(SOURCE_FILE_GLOBS))")

start: ## run code continously and watch files for changes
	echo "Teach me how to 'make start'"
	exit 1

SORD_GEN_OPTIONS = --replace-errors-with-untyped --exclude-messages OMIT --no-regenerate #  --hide-private

rbi/{{cookiecutter.project_slug}}.rbi: tapioca.installed yardoc.installed sorbet/config .gem_rbs_collection/.keepme ## Generate Sorbet types from Yard docs
	bin/parlour run --trace # creates RBI file from from RBI inline annotations in code
	bin/sord gen $(SORD_GEN_OPTIONS) rbi/{{cookiecutter.project_slug}}-sord.rbi # YARD to RBI
	cat rbi/{{cookiecutter.project_slug}}-parlour.rbi rbi/{{cookiecutter.project_slug}}-sord.rbi > rbi/{{cookiecutter.project_slug}}.rbi
	rm -f rbi/{{cookiecutter.project_slug}}-sord.rbi rbi/{{cookiecutter.project_slug}}-parlour.rbi
#	sed -i.bak -e 's/^# typed: strong/# typed: ignore/' rbi/{{cookiecutter.project_slug}}.rbi
	rm -f rbi/{{cookiecutter.project_slug}}.rbi.bak
	touch rbi/{{cookiecutter.project_slug}}.rbi

sig/{{cookiecutter.project_slug}}.rbs: yardoc.installed gem_rbs_collection/.keepme ## Generate RBS file
	rm -f rbi/{{cookiecutter.project_slug}}.rbs
	bin/sord gen $(SORD_GEN_OPTIONS) sig/{{cookiecutter.project_slug}}.rbs # YARD to RBS

YARD_PLUGIN_OPTS = --plugin yard-sorbet --plugin yard-solargraph

YARD_OPTS = $(YARD_PLUGIN_OPTS) -c .yardoc --output-dir yardoc --backtrace --exclude '^config/' '{lib,app,spec,feature}/**/*.rb' 'ext/**/*.{c,rb}'

types.installed: tapioca.installed Gemfile.lock Gemfile.lock.installed rbi/{{cookiecutter.project_slug}}.rbi sorbet/tapioca/require.rb sorbet/config ## Ensure typechecking dependencies are in place
	bin/solargraph gems
	bin/yard gems $(YARD_PLUGIN_OPTS) 2>&1 || bin/yard gems --safe $(YARD_PLUGIN_OPTS) 2>&1 || bin/yard gems $(YARD_PLUGIN_OPTS) 2>&1
	# bin/solargraph scan 2>&1
	bin/spoom srb bump || true
	# spoom rudely updates timestamps on files, so let's keep up by
	# touching yardoc.installed so we don't end up in a vicious
	# cycle
	touch yardoc.installed rbi/{{cookiecutter.project_slug}}.rbi
	# bin/solargraph scan 2>&1
	touch types.installed

build: bundle_install pip_install build-typecheck ## Update 3rd party packages as well and produce any artifacts needed from code

sorbet/machine_specific_config:
	echo "--cache-dir=$$HOME/.sorbet-cache" > sorbet/machine_specific_config

sorbet/rbi/todo.rbi: sorbet/tapioca/require.rb rbi/{{cookiecutter.project_slug}}.rbi tapioca.installed
	bin/tapioca todo

build-typecheck: Gemfile.lock.installed rbs_collection.lock.yaml types.installed sorbet/machine_specific_config sorbet/rbi/todo.rbi ## Fetch information that type checking depends on

rbs_collection.lock.yaml: Gemfile.lock rbs_collection.yaml
	bin/rbs collection update
	touch rbs_collection.lock.yaml

rbs_collection.yaml:
	bin/rbs collection init

.gem_rbs_collection/.keepme: rbs_collection.lock.yaml
	# Ensure that the gem rbs collection is installed
	bin/rbs collection install
	touch .gem_rbs_collection/.keepme

ci-build-typecheck: build-typecheck  ## Ensure cache is filled for CI to save regardless of actions run
	bundle exec solargraph gems

# Only create this once, so no dependencies
sorbet/tapioca/require.rb:
	make sorbet/machine_specific_config vendor/.keep
	bin/tapioca init

tapioca.installed: sorbet/tapioca/require.rb Gemfile.lock.installed db/schema.rb ## Install Tapioca-generated type information
	make sorbet/machine_specific_config
	bin/tapioca gems
	bin/tapioca annotations
	if [ -f db/schema.rb ]; then \
	  set -e; \
	  RAILS_ENV=development bin/rails db:create; \
	  RAILS_ENV=development bin/rails db:migrate; \
	  if ! bin/tapioca dsl 2>/dev/null; \
	  then \
	    echo "Tapioca parallel dsl failed, retrying with single worker"; \
	    bin/tapioca dsl --workers 1; \
	  fi; \
	fi
	touch tapioca.installed

db/schema.rb:

yardoc.installed: $(wildcard config/annotations_*.rb) $(SOURCE_FILES) ## Generate YARD documentation
	bin/yard doc $(YARD_OPTS)
	touch yardoc.installed

yard: yardoc.installed ## Generate YARD documentation

docs: ## Generate YARD documentation
	@rake doc

clean-typecheck: ## Refresh the easily-regenerated information that type checking depends on
	rm -fr .yardoc/ rbi/{{cookiecutter.project_slug}}.rbi types.installed yardoc.installed sig/{{cookiecutter.project_slug}}.rbs || true
{% if cookiecutter.use_checkoff %}	rm -fr ../checkoff/.yardoc || true
{% endif %}	echo all clear

realclean-typecheck: clean-typecheck ## Remove all type checking artifacts
	bin/solargraph clear || true
	rm -fr rbi/*.rbi
	rm -fr ~/.cache/solargraph
	rm -f tapioca.installed

realclean: clean realclean-typecheck
	rm -fr vendor/bundle .bundle/config
	rm -f .make/*
	rm -f *.installed

SORBET_TC_OPTIONS = --suppress-error-code 4010 # --suppress-error-code 4002

srb: build-typecheck ## Run Sorbet typechecker
	bin/srb tc $(SORBET_TC_OPTIONS)

solargraph: solargraph-strong ## Run Solargraph typechecker

solargraph-normal: build-typecheck ## Run Solargraph typechecker
	bin/solargraph typecheck --level normal

solargraph-typed: build-typecheck ## Run Solargraph typechecker
	bin/solargraph typecheck --level typed

solargraph-strict: build-typecheck ## Run Solargraph typechecker
	bin/solargraph typecheck --level strict

solargraph-strong: build-typecheck ## Run Solargraph typechecker
	bin/solargraph typecheck --level strong

typecheck: build-typecheck srb solargraph ## validate types in code and configuration

citypecheck: ci-build-typecheck srb solargraph ## Run type check from CircleCI

typecoverage: typecheck ## Run type checking and then ratchet coverage in metrics/

clean-typecoverage: ## Clean out type-related coverage previous results to avoid flaky results

citypecoverage: citypecheck ## Run type checking, ratchet coverage, and then complain if ratchet needs to be committed

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

Gemfile.lock: Gemfile .bundle/config
	if [ ! -f Gemfile.lock ]; then \
	  bundle install; \
	else \
	  bundle lock; \
	fi

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
	bundle install
	touch Gemfile.lock.installed

vendor/.keep: Gemfile.lock .ruby-version
	make gem_dependencies
	bundle install
	touch vendor/.keep

.bundle/config:
	touch .bundle/config

bundle_install: Gemfile.lock.installed ## Install Ruby dependencies

clear_metrics: ## remove or reset result artifacts created by tests and quality tools
	bin/rake clear_metrics || true

clean: clear_metrics clean-typecoverage clean-typecheck clean-coverage ## remove all built artifacts

test: spec ## run tests quickly

citest: test ## Run unit tests from CircleCI

overcommit: ## run precommit quality checks
	bin/overcommit --run

overcommit_branch: ## run precommit quality checks only on changed files
	bin/overcommit --run --diff origin/main

quality: overcommit ## run precommit quality checks

rubocop: ## Run rubocop
	@bin/rubocop

rubocop-ratchet: rubocop ## Run rubocop and then ratchet numbers of errors in todo file
	@bin/rubocop --regenerate-todo --no-exclude-limit --auto-gen-only-exclude --no-auto-gen-timestamp
	@if [ -f .rubocop_todo.yml ]; \
	  then \
	    git diff --exit-code .rubocop.yml; \
	    git diff --exit-code .rubocop_todo.yml; \
	fi

spec: ## Run lower-level tests
	@bin/rake spec

repl: bundle_install ## Launch an interactive development shell
	rails c

clean-coverage: clear_metrics ## Clean out previous output of test coverage to avoid flaky results from previous runs

coverage: test report-coverage ## check code coverage
	@bin/rake undercover

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
	bin/overcommit --uninstall
	# cookiecutter_project_upgrader does its work in
	# .git/cookiecutter/{{cookiecutter.project_slug}}, but RuboCop wants to inherit
	# config from all directories above it - avoid config
	# mismatches by moving this out of the way
	mv .rubocop.yml .rubocop-renamed.yml || true
	cookiecutter_project_upgrader --help >/dev/null
	IN_COOKIECUTTER_PROJECT_UPGRADER=1 cookiecutter_project_upgrader || true
	mv .rubocop-renamed.yml .rubocop.yml
	git checkout cookiecutter-template && git push --no-verify
	git checkout main; overcommit --sign && overcommit --sign pre-commit && overcommit --sign pre-push && git checkout main && git pull && git checkout -b update-from-cookiecutter-$$(date +%Y-%m-%d-%H%M)
	git merge cookiecutter-template || true
	git checkout --ours config/credentials.yml.enc Gemfile.lock || true
	git checkout --theirs sorbet/rbi/gems || true
	# update frequently security-flagged gems while we're here
	bundle update --conservative json nokogiri rexml yard rails-html-sanitizer brakeman || true
	( make build && git add Gemfile.lock config/credentials.yml.enc ) || true
	bin/spoom srb bump || true
	bin/overcommit --install || true
	@echo
	@echo "Please resolve any merge conflicts below and push up a PR with:"
	@echo
	@echo '   gh pr create --title "Update from cookiecutter" --body "Automated PR to update from cookiecutter boilerplate"'
	@echo
	@echo
