from __future__ import annotations

from typing import Any

from zato_fhir_r4_0_1_core import (
    ValidationError as _ValidationError,
    ValidationResult as _ValidationResult,
    validate as _validate,
    validate_valueset_binding as _validate_valueset_binding,
    rs_validate_to_outcome as _validate_to_outcome,
)

ValidationError = _ValidationError
ValidationResult = _ValidationResult


def validate(obj: 'Any', path: 'str' = '') -> 'ValidationResult':
    return _validate(obj, path or None)


def validate_valueset_binding(
    obj: 'Any',
    path: 'str' = '',
    include_extensible: 'bool' = True,
) -> 'ValidationResult':
    return _validate_valueset_binding(obj, path or None, include_extensible)


def validate_to_outcome(
    obj: 'Any',
    *,
    include_valueset: 'bool' = True,
) -> 'Any':
    """Run validation and return a typed ``OperationOutcome``.

    Parameters
    ----------
    obj:
        A FHIR resource instance (e.g. ``Patient``, ``Observation``).
    include_valueset:
        Whether to include valueset binding checks (default ``True``).

    Returns
    -------
    OperationOutcome
        A fully typed ``OperationOutcome`` with ``issue`` entries.
        If the resource is valid, a single ``information``-level issue
        with ``diagnostics = "Validation successful"`` is returned.
    """
    return _validate_to_outcome(obj, include_valueset)
