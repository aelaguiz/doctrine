PYTHON ?= python

.PHONY: hello-world

hello-world:
	$(PYTHON) -m pyprompt.check_hello_world
