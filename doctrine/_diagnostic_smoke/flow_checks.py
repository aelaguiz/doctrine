from __future__ import annotations

from doctrine._diagnostic_smoke.flow_emit_checks import run_flow_emit_checks
from doctrine._diagnostic_smoke.flow_graph_checks import run_flow_graph_checks
from doctrine._diagnostic_smoke.flow_route_checks import run_route_flow_checks


def run_flow_checks() -> None:
    run_route_flow_checks()
    run_flow_graph_checks()
    run_flow_emit_checks()
