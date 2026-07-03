from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RPA_I08


class TestRpaI08:
    """Comprehensive tests for RpaI08 message."""

    def test_rpa_i08_create(self):
        msg = RPA_I08()
        assert msg._structure_id == "RPA_I08"

    def test_rpa_i08_segment_access(self):
        msg = RPA_I08()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.rf1._segment_id == "RF1"
        assert msg.pid._segment_id == "PID"
        assert msg.acc._segment_id == "ACC"

    def test_rpa_i08_to_dict(self):
        msg = RPA_I08()

        result = msg.to_dict()

        assert result["_structure_id"] == "RPA_I08"

    def test_rpa_i08_to_json(self):
        msg = RPA_I08()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RPA_I08"
