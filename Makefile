.DEFAULT_GOAL := help

UV ?= uv
NPM ?= npm
PYTHON ?= python

UV_RUN := $(UV) run --locked $(PYTHON)
VERIFY_FLOW_PREREQ := $(UV_RUN) -m doctrine.verify_prereqs --require-flow-renderer
VSCODE_MAKE := $(MAKE) -C editors/vscode

.PHONY: help setup test tests check verify verify-examples verify-diagnostics verify-skill-examples build-dist verify-skill-install verify-package verify-package-wheel verify-package-sdist release-prepare release-tag release-draft release-publish vscode-tests vscode-package skills

help:
	@printf '%s\n' \
		'make setup             Sync Python deps and install the pinned D2 dependency.' \
		'make tests             Run the Python unittest suite under tests/.' \
		'make test              Alias for make tests.' \
		'make verify-examples   Run the shipped manifest-backed corpus.' \
		'make verify-diagnostics Run the diagnostic smoke checks.' \
		'make verify-skill-examples Parse every fenced ```prompt block in skill-bundled Markdown.' \
		'make verify-skill-install Run the pinned skills CLI smoke tests for the public install surface.' \
		'make build-dist        Build the sdist and wheel artifacts.' \
		'make verify-package    Smoke test wheel and sdist installs outside the repo root.' \
		'make release-prepare  Validate release inputs and print the release worksheet.' \
		'make release-tag      Create and push one signed annotated public release tag.' \
		'make release-draft    Create one GitHub draft release from an existing pushed tag.' \
		'make release-publish  Publish one reviewed GitHub draft release.' \
		'make verify            Run the shipped verify targets.' \
		'make check             Run unit tests plus shipped verify targets.' \
		'make vscode-tests      Run the VS Code extension test suite.' \
		'make vscode-package    Build the VS Code extension VSIX.' \
		'make skills            Emit the first-party curated skill trees and install them with npx skills add .'

setup:
	$(UV) sync
	$(NPM) ci

tests:
	$(UV_RUN) -m unittest discover -s tests -p 'test_*.py'

test: tests

verify-examples:
	$(VERIFY_FLOW_PREREQ)
	$(UV_RUN) -m doctrine.verify_corpus

verify-diagnostics:
	$(VERIFY_FLOW_PREREQ)
	$(UV_RUN) -m doctrine.diagnostic_smoke

verify-skill-examples:
	$(UV_RUN) -m doctrine.verify_skill_examples

verify: verify-examples verify-diagnostics verify-skill-examples

check: tests verify

build-dist:
	rm -rf dist
	$(UV) build

verify-skill-install:
	@test -x node_modules/.bin/skills || { printf '%s\n' 'Run npm ci first to install the pinned skills CLI.'; exit 2; }
	$(UV_RUN) -m unittest tests.test_emit_skill

verify-package-wheel:
	$(UV_RUN) -m doctrine._package_release smoke --artifact-type wheel

verify-package-sdist:
	$(UV_RUN) -m doctrine._package_release smoke --artifact-type sdist

verify-package: verify-skill-install build-dist verify-package-wheel verify-package-sdist

release-prepare:
	@test -n "$(RELEASE)" || { printf '%s\n' 'RELEASE is required.'; exit 2; }
	@test -n "$(CLASS)" || { printf '%s\n' 'CLASS is required.'; exit 2; }
	@test -n "$(LANGUAGE_VERSION)" || { printf '%s\n' 'LANGUAGE_VERSION is required.'; exit 2; }
	@test -n "$(CHANNEL)" || { printf '%s\n' 'CHANNEL is required.'; exit 2; }
	$(UV_RUN) -m doctrine.release_flow prepare --release "$(RELEASE)" --class "$(CLASS)" --language-version "$(LANGUAGE_VERSION)" --channel "$(CHANNEL)"

release-tag:
	@test -n "$(RELEASE)" || { printf '%s\n' 'RELEASE is required.'; exit 2; }
	@test -n "$(CHANNEL)" || { printf '%s\n' 'CHANNEL is required.'; exit 2; }
	$(UV_RUN) -m doctrine.release_flow tag --release "$(RELEASE)" --channel "$(CHANNEL)"

release-draft:
	@test -n "$(RELEASE)" || { printf '%s\n' 'RELEASE is required.'; exit 2; }
	@test -n "$(CHANNEL)" || { printf '%s\n' 'CHANNEL is required.'; exit 2; }
	$(UV_RUN) -m doctrine.release_flow draft --release "$(RELEASE)" --channel "$(CHANNEL)" --previous-tag "$(or $(PREVIOUS_TAG),auto)"

release-publish:
	@test -n "$(RELEASE)" || { printf '%s\n' 'RELEASE is required.'; exit 2; }
	$(UV_RUN) -m doctrine.release_flow publish --release "$(RELEASE)"

vscode-tests:
	$(VSCODE_MAKE) test

vscode-package:
	$(VSCODE_MAKE) package

skills:
	$(UV_RUN) -m doctrine.emit_skill --target doctrine_agent_linter_public_skill
	$(UV_RUN) -m doctrine.emit_skill --target doctrine_learn_public_skill
	npx skills add .
