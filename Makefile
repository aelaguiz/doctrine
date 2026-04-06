.PHONY: verify-examples

verify-examples:
	uv run --locked python -m pyprompt.verify_corpus
