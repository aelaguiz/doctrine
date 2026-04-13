.DEFAULT_GOAL := help

UV ?= uv
NPM ?= npm
PYTHON ?= python

UV_RUN := $(UV) run --locked $(PYTHON)
VSCODE_MAKE := $(MAKE) -C editors/vscode

.PHONY: help setup test tests check verify verify-examples verify-diagnostics vscode-tests vscode-package

help:
	@printf '%s\n' \
		'make setup             Sync Python deps and install the pinned D2 dependency.' \
		'make tests             Run the Python unittest suite under tests/.' \
		'make test              Alias for make tests.' \
		'make verify-examples   Run the shipped manifest-backed corpus.' \
		'make verify-diagnostics Run the diagnostic smoke checks.' \
		'make verify            Run the shipped verify targets.' \
		'make check             Run unit tests plus shipped verify targets.' \
		'make vscode-tests      Run the VS Code extension test suite.' \
		'make vscode-package    Build the VS Code extension VSIX.'

setup:
	$(UV) sync
	$(NPM) ci

tests:
	$(UV_RUN) -m unittest discover -s tests -p 'test_*.py'

test: tests

verify-examples:
	$(UV_RUN) -m doctrine.verify_corpus

verify-diagnostics:
	$(UV_RUN) -m doctrine.diagnostic_smoke

verify: verify-examples verify-diagnostics

check: tests verify

vscode-tests:
	$(VSCODE_MAKE) test

vscode-package:
	$(VSCODE_MAKE) package
