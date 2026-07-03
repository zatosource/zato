from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import CCF_I22


class TestCcfI22:
    """Comprehensive tests for CcfI22 message."""

    def test_ccf_i22_create(self):
        msg = CCF_I22()
        assert msg._structure_id == "CCF_I22"

    def test_ccf_i22_segment_access(self):
        msg = CCF_I22()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"

    def test_ccf_i22_to_dict(self):
        msg = CCF_I22()

        result = msg.to_dict()

        assert result["_structure_id"] == "CCF_I22"

    def test_ccf_i22_to_json(self):
        msg = CCF_I22()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "CCF_I22"
