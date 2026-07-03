from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import REF_I12


class TestRefI12:
    """Comprehensive tests for RefI12 message."""

    def test_ref_i12_create(self):
        msg = REF_I12()
        assert msg._structure_id == "REF_I12"

    def test_ref_i12_segment_access(self):
        msg = REF_I12()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.rf1._segment_id == "RF1"
        assert msg.pid._segment_id == "PID"
        assert msg.acc._segment_id == "ACC"

    def test_ref_i12_to_dict(self):
        msg = REF_I12()

        result = msg.to_dict()

        assert result["_structure_id"] == "REF_I12"

    def test_ref_i12_to_json(self):
        msg = REF_I12()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "REF_I12"
