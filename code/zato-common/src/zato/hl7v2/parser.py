from __future__ import annotations

from zato.hl7v2.base import HL7Message
from zato.hl7v2_rs import ToleranceConfig  # pyright: ignore[reportAttributeAccessIssue]
from zato.hl7v2.v2_9 import parse_hl7 as _parse_hl7


def parse_hl7(raw:'str', tolerance:'ToleranceConfig'=None) -> 'HL7Message':
    return _parse_hl7(raw, tolerance=tolerance or ToleranceConfig())
