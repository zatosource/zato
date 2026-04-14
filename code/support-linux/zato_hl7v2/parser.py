from __future__ import annotations

from zato_hl7v2.base import HL7Message
from zato_hl7v2.v2_9 import parse_message as _parse_v2_9


def parse_message(raw: str) -> HL7Message:
    return _parse_v2_9(raw)
