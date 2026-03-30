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


def parse_message(raw: str) -> HL7Message:
    from zato_hl7v2.v2_9 import parse_message as parse_v2_9
    return parse_v2_9(raw)


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
]
