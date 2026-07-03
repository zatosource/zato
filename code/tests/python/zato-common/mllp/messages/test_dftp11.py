from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import DFT_P11


class TestDftP11:
    """Comprehensive tests for DftP11 message."""

    def test_dft_p11_create(self):
        msg = DFT_P11()
        assert msg._structure_id == "DFT_P11"

    def test_dft_p11_segment_access(self):
        msg = DFT_P11()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.drg._segment_id == "DRG"
        assert msg.acc._segment_id == "ACC"

    def test_dft_p11_to_dict(self):
        msg = DFT_P11()

        result = msg.to_dict()

        assert result["_structure_id"] == "DFT_P11"

    def test_dft_p11_to_json(self):
        msg = DFT_P11()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "DFT_P11"
