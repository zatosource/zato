from __future__ import annotations

from zato.hl7v2.v2_9.primitives import *
from zato.hl7v2.v2_9.datatypes import *
from zato.hl7v2.v2_9.segments import *
from zato.hl7v2.v2_9.groups import *
from zato.hl7v2.v2_9.messages import *

from zato.hl7v2.base import HL7Message
from zato.hl7v2_rs import parse as _rust_parse, validate as _rust_validate, serialize as _rust_serialize, ValidationResult, ValidationError  # noqa: F401  # pyright: ignore[reportAttributeAccessIssue, reportUnusedImport]
from zato.hl7v2_rs import apply_tolerance as _apply_tolerance, ToleranceConfig  # pyright: ignore[reportAttributeAccessIssue]
from zato.hl7v2.batch import parse_batch, parse_file, parse_batch_or_file  # noqa: F401  # pyright: ignore[reportUnusedImport]


def parse_message(raw: str, validate: bool = True, tolerance: 'ToleranceConfig | None' = None) -> HL7Message:
    if tolerance is not None:
        raw = _apply_tolerance(raw, tolerance)
    raw_msg = _rust_parse(raw)
    msg_class = HL7Message._registry.get(raw_msg.structure_id)
    if msg_class is None:
        raise ValueError(f"Unknown structure: {raw_msg.structure_id}")
    msg = msg_class.__new__(msg_class)  # pyright: ignore[reportCallIssue]
    msg._raw_message = raw_msg
    return msg


def serialize(msg: HL7Message) -> str:
    if msg._raw_message is not None:
        return _rust_serialize(msg._raw_message)
    from zato.hl7v2.base import HL7SegmentAttr, HL7GroupAttr

    lines: list[str] = []

    for name in msg.__class__.__annotations__:
        attr = getattr(msg.__class__, name, None)

        if isinstance(attr, HL7SegmentAttr):
            seg = msg.__dict__.get(attr.attr_name)
            if seg is not None:
                if isinstance(seg, list):
                    for s in seg:
                        line = s.serialize()
                        if line:
                            lines.append(line)
                else:
                    line = seg.serialize()
                    if line:
                        lines.append(line)

        elif isinstance(attr, HL7GroupAttr):
            group = msg.__dict__.get(attr.attr_name)
            if group is not None:
                if isinstance(group, list):
                    for g in group:
                        line = g.serialize()
                        if line:
                            lines.append(line)
                else:
                    line = group.serialize()
                    if line:
                        lines.append(line)

    if not lines:
        raise ValueError("Message has no data to serialize")
    return "\r".join(lines)


def validate_message(raw: str) -> ValidationResult:
    return _rust_validate(raw)
