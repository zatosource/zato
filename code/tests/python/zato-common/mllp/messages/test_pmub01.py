from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import PmuB01
from zato.hl7v2.v2_9.segments import EVN, MSH, STF, UAC


class TestPmuB01:
    """Comprehensive tests for PmuB01 message."""

    def test_pmu_b01_create(self):
        msg = PmuB01()
        assert msg._structure_id == "PMU_B01"

    def test_pmu_b01_segment_access(self):
        msg = PmuB01()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.stf._segment_id == "STF"

    def test_pmu_b01_to_dict(self):
        msg = PmuB01()

        result = msg.to_dict()

        assert result["_structure_id"] == "PMU_B01"

    def test_pmu_b01_to_json(self):
        msg = PmuB01()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "PMU_B01"
