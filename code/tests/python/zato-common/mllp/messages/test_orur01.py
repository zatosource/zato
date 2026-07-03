from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ORU_R01


class TestOruR01:
    """Comprehensive tests for OruR01 message."""

    def test_oru_r01_create(self):
        msg = ORU_R01()
        assert msg._structure_id == "ORU_R01"

    def test_oru_r01_segment_access(self):
        msg = ORU_R01()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.dsc._segment_id == "DSC"

    def test_oru_r01_to_dict(self):
        msg = ORU_R01()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORU_R01"

    def test_oru_r01_to_json(self):
        msg = ORU_R01()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORU_R01"
