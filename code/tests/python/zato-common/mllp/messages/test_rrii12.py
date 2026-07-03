from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RRI_I12


class TestRriI12:
    """Comprehensive tests for RriI12 message."""

    def test_rri_i12_create(self):
        msg = RRI_I12()
        assert msg._structure_id == "RRI_I12"

    def test_rri_i12_segment_access(self):
        msg = RRI_I12()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.rf1._segment_id == "RF1"
        assert msg.pid._segment_id == "PID"
        assert msg.acc._segment_id == "ACC"

    def test_rri_i12_to_dict(self):
        msg = RRI_I12()

        result = msg.to_dict()

        assert result["_structure_id"] == "RRI_I12"

    def test_rri_i12_to_json(self):
        msg = RRI_I12()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RRI_I12"
