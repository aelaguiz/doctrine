from __future__ import annotations

# Stable public boundary; real compiler implementation lives under doctrine._compiler.
from doctrine._compiler.shared import *  # noqa: F401,F403
from doctrine._compiler.session import CompilationSession, compile_prompt, extract_target_flow_graph
