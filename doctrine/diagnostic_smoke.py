from __future__ import annotations

from doctrine._diagnostic_smoke.compile_checks import run_compile_checks
from doctrine._diagnostic_smoke.emit_checks import run_emit_checks
from doctrine._diagnostic_smoke.fixtures import SmokeFailure
from doctrine._diagnostic_smoke.flow_checks import run_flow_checks
from doctrine._diagnostic_smoke.parse_checks import run_parse_checks
from doctrine._diagnostic_smoke.patch_checks import run_patch_checks
from doctrine._diagnostic_smoke.review_checks import run_review_checks
from doctrine._diagnostic_smoke.team_checks import run_team_checks
from doctrine._diagnostic_smoke.home_checks import run_home_checks


def main() -> int:
    run_parse_checks()
    run_patch_checks()
    run_team_checks()
    run_home_checks()
    run_compile_checks()
    run_review_checks()
    run_flow_checks()
    run_emit_checks()
    print("diagnostic smoke checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
