from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import STC_S33


class TestStcS33:
    """Comprehensive tests for StcS33 message."""

    def test_stc_s33_create(self):
        msg = STC_S33()
        assert msg._structure_id == "STC_S33"

    def test_stc_s33_segment_access(self):
        msg = STC_S33()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_stc_s33_to_dict(self):
        msg = STC_S33()

        result = msg.to_dict()

        assert result["_structure_id"] == "STC_S33"

    def test_stc_s33_to_json(self):
        msg = STC_S33()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "STC_S33"
