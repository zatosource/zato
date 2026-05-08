from __future__ import annotations

from zato_hl7v2.base import (
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
from zato_hl7v2.validator import validate_message, ValidationResult, ValidationError
from zato_hl7v2.batch import HL7Batch, HL7File, parse_batch, parse_file, parse_batch_or_file, create_batch, create_file
from zato_hl7v2_rs import ParserQuirks


def parse_message(raw:'str', validate:'bool' = True, quirks:'ParserQuirks | None' = None) -> 'HL7Message':
    from zato_hl7v2.v2_9 import parse_message as parse_v2_9
    return parse_v2_9(raw, validate=validate, quirks=quirks or ParserQuirks())


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
    "parse_message",
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
    "ParserQuirks",
]
