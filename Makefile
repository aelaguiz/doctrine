.PHONY: verify verify-examples verify-diagnostics

verify-examples:
	uv run --locked python -m pyprompt.verify_corpus

verify-diagnostics:
	uv run --locked python -m pyprompt.diagnostic_smoke

verify: verify-examples verify-diagnostics
