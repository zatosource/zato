from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import PEX_P07


class TestPexP07:
    """Comprehensive tests for PexP07 message."""

    def test_pex_p07_create(self):
        msg = PEX_P07()
        assert msg._structure_id == "PEX_P07"

    def test_pex_p07_segment_access(self):
        msg = PEX_P07()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"

    def test_pex_p07_to_dict(self):
        msg = PEX_P07()

        result = msg.to_dict()

        assert result["_structure_id"] == "PEX_P07"

    def test_pex_p07_to_json(self):
        msg = PEX_P07()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "PEX_P07"
