PYTHON ?= python

.PHONY: hello-world verify-examples

hello-world:
	$(PYTHON) -m pyprompt.verify_corpus --manifest examples/01_hello_world/cases.toml

verify-examples:
	$(PYTHON) -m pyprompt.verify_corpus
