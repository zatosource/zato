from __future__ import annotations

from zato.hl7v2.v2_9 import validate_message as _validate_v2_9, ValidationResult, ValidationError  # type: ignore[attr-defined]

__all__ = ["validate_message", "ValidationResult", "ValidationError"]


def validate_message(raw: str) -> ValidationResult:
    return _validate_v2_9(raw)
