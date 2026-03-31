from __future__ import annotations

from zato_hl7v2.v2_9.primitives import *
from zato_hl7v2.v2_9.datatypes import *
from zato_hl7v2.v2_9.segments import *
from zato_hl7v2.v2_9.groups import *
from zato_hl7v2.v2_9.messages import *

from zato_hl7v2.base import HL7Message
from zato_hl7v2.batch import (
    HL7Batch,
    HL7File,
    parse_batch,
    parse_file,
    parse_batch_or_file,
    create_batch,
    create_file,
)
from zato_hl7v2_rs import parse as _rust_parse, validate as _rust_validate, ValidationResult, ValidationError


def parse_message(raw: str, validate: bool = True) -> HL7Message:
    raw_msg = _rust_parse(raw)
    msg_class = HL7Message._registry.get(raw_msg.structure_id)
    if msg_class is None:
        raise ValueError(f"Unknown structure: {raw_msg.structure_id}")
    msg = msg_class.__new__(msg_class)
    msg._raw_message = raw_msg
    return msg


def serialize(msg) -> str:
    from zato_hl7v2_rs import serialize as _serialize
    if hasattr(msg, '_raw_message'):
        return _serialize(msg._raw_message)
    return _serialize(msg)


def to_hl7(raw_msg) -> str:
    return serialize(raw_msg)


def to_er7(raw_msg) -> str:
    return serialize(raw_msg)


def validate_message(raw: str) -> ValidationResult:
    return _rust_validate(raw)
