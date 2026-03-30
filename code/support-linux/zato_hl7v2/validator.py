from __future__ import annotations

from zato_hl7v2.v2_9 import validate_message as _validate_v2_9, ValidationResult, ValidationError

__all__ = ["validate_message", "ValidationResult", "ValidationError"]


def validate_message(raw: str) -> ValidationResult:
    return _validate_v2_9(raw)
