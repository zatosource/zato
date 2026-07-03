from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import SIU_S12


class TestSiuS12:
    """Comprehensive tests for SiuS12 message."""

    def test_siu_s12_create(self):
        msg = SIU_S12()
        assert msg._structure_id == "SIU_S12"

    def test_siu_s12_segment_access(self):
        msg = SIU_S12()

        assert msg.msh._segment_id == "MSH"
        assert msg.sch._segment_id == "SCH"

    def test_siu_s12_to_dict(self):
        msg = SIU_S12()

        result = msg.to_dict()

        assert result["_structure_id"] == "SIU_S12"

    def test_siu_s12_to_json(self):
        msg = SIU_S12()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "SIU_S12"
