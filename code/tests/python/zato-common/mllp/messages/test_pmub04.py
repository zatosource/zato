from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import PmuB04
from zato.hl7v2.v2_9.segments import EVN, MSH, STF, UAC


class TestPmuB04:
    """Comprehensive tests for PmuB04 message."""

    def test_pmu_b04_create(self):
        msg = PmuB04()
        assert msg._structure_id == "PMU_B04"

    def test_pmu_b04_segment_access(self):
        msg = PmuB04()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.stf._segment_id == "STF"

    def test_pmu_b04_to_dict(self):
        msg = PmuB04()

        result = msg.to_dict()

        assert result["_structure_id"] == "PMU_B04"

    def test_pmu_b04_to_json(self):
        msg = PmuB04()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "PMU_B04"
