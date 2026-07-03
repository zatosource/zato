from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import CCI_I22


class TestCciI22:
    """Comprehensive tests for CciI22 message."""

    def test_cci_i22_create(self):
        msg = CCI_I22()
        assert msg._structure_id == "CCI_I22"

    def test_cci_i22_segment_access(self):
        msg = CCI_I22()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"

    def test_cci_i22_to_dict(self):
        msg = CCI_I22()

        result = msg.to_dict()

        assert result["_structure_id"] == "CCI_I22"

    def test_cci_i22_to_json(self):
        msg = CCI_I22()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "CCI_I22"
