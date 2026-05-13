from __future__ import annotations

from typing import Any


class ValidationError(Exception):
    def __init__(self, message: str, path: str = "") -> None:
        super().__init__(message)
        self.path = path


def validate_required(value: Any, field_name: str) -> None:
    if value is None:
        raise ValidationError(f"Required field {field_name} is missing", field_name)


def validate_length(value: str, max_length: int, field_name: str) -> None:
    if len(value) > max_length:
        raise ValidationError(
            f"Field {field_name} exceeds max length {max_length}", field_name
        )
