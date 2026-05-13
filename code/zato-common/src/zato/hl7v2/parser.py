from __future__ import annotations

from zato.hl7v2.base import HL7Message
from zato.hl7v2_rs import ToleranceConfig  # pyright: ignore[reportAttributeAccessIssue]
from zato.hl7v2.v2_9 import parse_message as _parse_v2_9


def parse_message(raw:'str', tolerance:'ToleranceConfig'=None) -> 'HL7Message':
    return _parse_v2_9(raw, tolerance=tolerance or ToleranceConfig())
