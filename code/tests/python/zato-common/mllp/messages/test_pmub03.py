from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import PMU_B03


class TestPmuB03:
    """Comprehensive tests for PmuB03 message."""

    def test_pmu_b03_create(self):
        msg = PMU_B03()
        assert msg._structure_id == "PMU_B03"

    def test_pmu_b03_segment_access(self):
        msg = PMU_B03()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.stf._segment_id == "STF"

    def test_pmu_b03_to_dict(self):
        msg = PMU_B03()

        result = msg.to_dict()

        assert result["_structure_id"] == "PMU_B03"

    def test_pmu_b03_to_json(self):
        msg = PMU_B03()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "PMU_B03"
