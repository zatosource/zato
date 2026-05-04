from __future__ import annotations

from zato_hl7v2.v2_9.primitives import *
from zato_hl7v2.v2_9.datatypes import *
from zato_hl7v2.v2_9.segments import *
from zato_hl7v2.v2_9.groups import *
from zato_hl7v2.v2_9.messages import *

from zato_hl7v2.base import HL7Message
from zato_hl7v2_rs import parse as _rust_parse, validate as _rust_validate, serialize as _rust_serialize, ValidationResult, ValidationError
from zato_hl7v2_rs import apply_parser_quirks as _apply_quirks, ParserQuirks
from zato_hl7v2.batch import parse_batch, parse_file, parse_batch_or_file


def parse_message(raw: str, validate: bool = True, quirks: 'ParserQuirks | None' = None) -> HL7Message:
    if quirks is not None:
        raw = _apply_quirks(raw, quirks)
    raw_msg = _rust_parse(raw)
    msg_class = HL7Message._registry.get(raw_msg.structure_id)
    if msg_class is None:
        raise ValueError(f"Unknown structure: {raw_msg.structure_id}")
    msg = msg_class.__new__(msg_class)
    msg._raw_message = raw_msg
    return msg


def serialize(msg: HL7Message) -> str:
    if msg._raw_message is not None:
        return _rust_serialize(msg._raw_message)
    from zato_hl7v2.base import HL7SegmentAttr, HL7GroupAttr
    lines = []
    for name in dir(msg.__class__):
        attr = getattr(msg.__class__, name)
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
    if not lines:
        raise ValueError("Message has no data to serialize")
    return "\r".join(lines)


def validate_message(raw: str) -> ValidationResult:
    return _rust_validate(raw)
