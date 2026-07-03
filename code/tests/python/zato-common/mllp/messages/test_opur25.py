from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import OPU_R25


class TestOpuR25:
    """Comprehensive tests for OpuR25 message."""

    def test_opu_r25_create(self):
        msg = OPU_R25()
        assert msg._structure_id == "OPU_R25"

    def test_opu_r25_segment_access(self):
        msg = OPU_R25()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.nte._segment_id == "NTE"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"

    def test_opu_r25_to_dict(self):
        msg = OPU_R25()

        result = msg.to_dict()

        assert result["_structure_id"] == "OPU_R25"

    def test_opu_r25_to_json(self):
        msg = OPU_R25()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OPU_R25"
