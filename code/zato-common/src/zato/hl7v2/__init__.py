from __future__ import annotations

from zato.hl7v2.base import (
    HL7Component,
    HL7DataType,
    HL7Field,
    HL7Group,
    HL7GroupAttr,
    HL7Message,
    HL7Segment,
    HL7SegmentAttr,
    Usage,
)
from zato.hl7v2.validator import validate_message, ValidationResult, ValidationError  # pyright: ignore[reportAttributeAccessIssue]
from zato.hl7v2.batch import HL7Batch, HL7File, parse_batch, parse_file, parse_batch_or_file, create_batch, create_file
from zato.hl7v2_rs import ToleranceConfig


def parse_hl7(raw:'str', validate:'bool'=True, tolerance:'ToleranceConfig | None'=None) -> 'HL7Message':
    from zato.hl7v2.v2_9 import parse_hl7 as _parse_v2_9
    if tolerance is None:
        tolerance = ToleranceConfig()
    return _parse_v2_9(raw, validate=validate, tolerance=tolerance)


__all__ = [
    "HL7Component",
    "HL7DataType",
    "HL7Field",
    "HL7Group",
    "HL7GroupAttr",
    "HL7Message",
    "HL7Segment",
    "HL7SegmentAttr",
    "Usage",
    "parse_hl7",
    "validate_message",
    "ValidationResult",
    "ValidationError",
    "HL7Batch",
    "HL7File",
    "parse_batch",
    "parse_file",
    "parse_batch_or_file",
    "create_batch",
    "create_file",
    "ToleranceConfig",
]
