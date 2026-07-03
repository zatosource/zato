from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import CCM_I21


class TestCcmI21:
    """Comprehensive tests for CcmI21 message."""

    def test_ccm_i21_create(self):
        msg = CCM_I21()
        assert msg._structure_id == "CCM_I21"

    def test_ccm_i21_segment_access(self):
        msg = CCM_I21()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"

    def test_ccm_i21_to_dict(self):
        msg = CCM_I21()

        result = msg.to_dict()

        assert result["_structure_id"] == "CCM_I21"

    def test_ccm_i21_to_json(self):
        msg = CCM_I21()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "CCM_I21"
