from __future__ import annotations

from doctrine._compiler.validate.route_semantics_context import (
    ValidateRouteSemanticsContextMixin,
)
from doctrine._compiler.validate.route_semantics_reads import ValidateRouteSemanticsReadsMixin


class ValidateRouteSemanticsMixin(
    ValidateRouteSemanticsReadsMixin,
    ValidateRouteSemanticsContextMixin,
):
    """Stable route-semantic helper boundary for ValidateMixin."""
