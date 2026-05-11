from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import PmuB08
from zato.hl7v2.v2_9.segments import EVN, MSH, PRA, STF, UAC


class TestPmuB08:
    """Comprehensive tests for PmuB08 message."""

    def test_pmu_b08_create(self):
        msg = PmuB08()
        assert msg._structure_id == "PMU_B08"

    def test_pmu_b08_segment_access(self):
        msg = PmuB08()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.stf._segment_id == "STF"
        assert msg.pra._segment_id == "PRA"

    def test_pmu_b08_to_dict(self):
        msg = PmuB08()

        result = msg.to_dict()

        assert result["_structure_id"] == "PMU_B08"

    def test_pmu_b08_to_json(self):
        msg = PmuB08()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "PMU_B08"
