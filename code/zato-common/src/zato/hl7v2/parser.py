from __future__ import annotations

from zato.hl7v2.base import HL7Message
from zato.hl7v2_rs import ToleranceConfig
from zato.hl7v2.v2_9 import parse_hl7 as _parse_hl7


def parse_hl7(raw:'str', tolerance:'ToleranceConfig | None'=None) -> 'HL7Message':
    if tolerance is None:
        tolerance = ToleranceConfig()
    return _parse_hl7(raw, tolerance=tolerance)
