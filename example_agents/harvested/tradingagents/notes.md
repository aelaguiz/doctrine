# Notes

This source is useful because it expresses agent behavior directly in code-shaped prompt functions. The repo uses distinct roles for bull, bear, neutral, research manager, and portfolio manager, and those roles exchange explicit state fields such as history, current responses, and investment plans.

The strongest Doctrine pressure here is debate orchestration plus final output normalization. The research manager and portfolio manager are good sources for examples where several upstream viewpoints are synthesized into one structured decision. The bull and bear researchers are useful for showing opposing role prompts that both read the same evidence but argue in different directions.

Selected artifacts:
- `raw/README.md`
- `raw/tradingagents/agents/researchers/bull_researcher.py`
- `raw/tradingagents/agents/researchers/bear_researcher.py`
- `raw/tradingagents/agents/managers/research_manager.py`
- `raw/tradingagents/agents/managers/portfolio_manager.py`
