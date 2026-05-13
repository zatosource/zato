from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import PmuB07
from zato.hl7v2.v2_9.segments import CER, EVN, MSH, PRA, STF, UAC


class TestPmuB07:
    """Comprehensive tests for PmuB07 message."""

    def test_pmu_b07_create(self):
        msg = PmuB07()
        assert msg._structure_id == "PMU_B07"

    def test_pmu_b07_segment_access(self):
        msg = PmuB07()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.stf._segment_id == "STF"
        assert msg.pra._segment_id == "PRA"
        assert msg.cer._segment_id == "CER"

    def test_pmu_b07_to_dict(self):
        msg = PmuB07()

        result = msg.to_dict()

        assert result["_structure_id"] == "PMU_B07"

    def test_pmu_b07_to_json(self):
        msg = PmuB07()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "PMU_B07"
