from __future__ import annotations

from doctrine._compiler.validate.review_agreement import ValidateReviewAgreementMixin
from doctrine._compiler.validate.review_branches import ValidateReviewBranchesMixin
from doctrine._compiler.validate.review_gate_observation import (
    ValidateReviewGateObservationMixin,
)
from doctrine._compiler.validate.review_preflight import ValidateReviewPreflightMixin
from doctrine._compiler.validate.review_semantics import ValidateReviewSemanticsMixin


class ValidateReviewsMixin(
    ValidateReviewAgreementMixin,
    ValidateReviewBranchesMixin,
    ValidateReviewGateObservationMixin,
    ValidateReviewPreflightMixin,
    ValidateReviewSemanticsMixin,
):
    """Stable review helper boundary for ValidateMixin."""
