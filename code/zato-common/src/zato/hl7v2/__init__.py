from __future__ import annotations

from zato.hl7v2.base import (
    HL7Component,
    HL7DataType,
    HL7Field,
    HL7Fragment,
    HL7Group,
    HL7GroupAttr,
    HL7Message,
    HL7RawLine,
    HL7Segment,
    HL7SegmentAttr,
    HL7ValidationError,
    Usage,
)
from zato.hl7v2.validator import validate_message, ValidationResult, ValidationError  # pyright: ignore[reportAttributeAccessIssue]
from zato.hl7v2.batch import HL7Batch, HL7File, parse_batch, parse_file, parse_batch_or_file, create_batch, create_file
from zato.hl7v2.z_segments import ZAU, ZBE, ZDS, ZFD
from zato.hl7v2_rs import ToleranceConfig

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # For static analysis only - IDE completion and type checking see every
    # segment and data type on the package root, while the interpreter loads
    # them lazily through __getattr__ below.
    from zato.hl7v2.v2_9.datatypes import * # noqa: F403
    from zato.hl7v2.v2_9.segments import * # noqa: F403


def __getattr__(name:'str') -> 'type':
    # Segments and data types resolve lazily, so that importing the package
    # stays cheap while user code can still import any of them from the root,
    # e.g. from zato.hl7v2 import PID, XPN.
    from zato.hl7v2.v2_9 import datatypes, segments
    if name in segments.__all__:
        return getattr(segments, name)
    if name in datatypes.__all__:
        return getattr(datatypes, name)
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')


def parse_hl7(raw:'str', validate:'bool'=True, tolerance:'ToleranceConfig | None'=None) -> 'HL7Message':
    from zato.hl7v2.v2_9 import parse_hl7 as _parse_v2_9
    if tolerance is None:
        tolerance = ToleranceConfig()
    return _parse_v2_9(raw, validate=validate, tolerance=tolerance)


__all__ = [
    'HL7Component',
    'HL7DataType',
    'HL7Field',
    'HL7Fragment',
    'HL7Group',
    'HL7GroupAttr',
    'HL7Message',
    'HL7Segment',
    'HL7SegmentAttr',
    'HL7ValidationError',
    'Usage',
    'parse_hl7',
    'validate_message',
    'ValidationResult',
    'ValidationError',
    'HL7Batch',
    'HL7File',
    'parse_batch',
    'parse_file',
    'parse_batch_or_file',
    'create_batch',
    'create_file',
    'ToleranceConfig',
    'HL7RawLine',
    'ZAU',
    'ZBE',
    'ZDS',
    'ZFD',
]
