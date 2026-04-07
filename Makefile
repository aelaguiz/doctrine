.PHONY: verify verify-examples verify-diagnostics

verify-examples:
	uv run --locked python -m doctrine.verify_corpus

verify-diagnostics:
	uv run --locked python -m doctrine.diagnostic_smoke

verify: verify-examples verify-diagnostics
