from __future__ import annotations

from zato_hl7v2.v2_9.primitives import *
from zato_hl7v2.v2_9.datatypes import *
from zato_hl7v2.v2_9.segments import *
from zato_hl7v2.v2_9.groups import *
from zato_hl7v2.v2_9.messages import *

from zato_hl7v2.base import HL7Message


def parse_message(raw: str) -> HL7Message:
    try:
        from zato_hl7v2_rs import parse as rust_parse
        raw_msg = rust_parse(raw)
        msg_class = HL7Message._registry.get(raw_msg.structure_id)
        if msg_class is None:
            raise ValueError(f"Unknown structure: {raw_msg.structure_id}")
        msg = msg_class.__new__(msg_class)
        msg._raw_message = raw_msg
        return msg
    except ImportError:
        raise ImportError("zato_hl7v2_rs extension not available")
