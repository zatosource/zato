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


def parse_message(raw:'str', validate:'bool' = True, quirks:'ParserQuirks | None' = None) -> 'HL7Message':

    # .. apply parser quirks (e.g. OBX-2 normalization) before parsing ..
    if quirks is not None:
        raw = _apply_quirks(raw, quirks)

    # .. parse the raw ER7 string through the Rust tokenizer and structure parser ..
    raw_msg = _rust_parse(raw)

    # .. look up the Python message class by structure ID (e.g. "ADT_A01") ..
    msg_class = HL7Message._registry.get(raw_msg.structure_id)
    if msg_class is None:
        raise ValueError(f"Unknown structure: {raw_msg.structure_id}")

    # .. instantiate the message class and attach the Rust-parsed raw data ..
    msg = msg_class.__new__(msg_class)
    msg._raw_message = raw_msg

    # .. optionally validate the message against HL7 rules and raise on errors ..
    if validate:
        result = _rust_validate(raw)
        if result.errors:
            error_lines = [f"{e.path}: {e.message}" for e in result.errors]
            raise ValueError(f"Validation failed:\n" + "\n".join(error_lines))

    return msg


def serialize(msg: HL7Message) -> str:

    # .. fast path - delegate to Rust serializer when a raw message is available ..
    if msg._raw_message is not None:
        return _rust_serialize(msg._raw_message)

    # .. slow path - serialize from Python descriptor values ..
    from zato_hl7v2.base import HL7SegmentAttr, HL7GroupAttr
    lines = []
    for name in dir(msg.__class__):
        attr = getattr(msg.__class__, name)
        if isinstance(attr, HL7SegmentAttr):
            seg = msg.__dict__.get(attr.attr_name)
            if seg is not None:

                # .. repeating segments - serialize each occurrence ..
                if isinstance(seg, list):
                    for s in seg:
                        line = s.serialize()
                        if line:
                            lines.append(line)

                # .. single segment ..
                else:
                    line = seg.serialize()
                    if line:
                        lines.append(line)

    if not lines:
        raise ValueError("Message has no data to serialize")

    return "\r".join(lines)


def validate_message(raw: str) -> ValidationResult:
    """ Validates a raw ER7 string against HL7 structure and field rules. """
    return _rust_validate(raw)
