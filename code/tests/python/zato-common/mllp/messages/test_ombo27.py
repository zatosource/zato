from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import OMB_O27


class TestOmbO27:
    """Comprehensive tests for OmbO27 message."""

    def test_omb_o27_create(self):
        msg = OMB_O27()
        assert msg._structure_id == "OMB_O27"

    def test_omb_o27_segment_access(self):
        msg = OMB_O27()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_omb_o27_to_dict(self):
        msg = OMB_O27()

        result = msg.to_dict()

        assert result["_structure_id"] == "OMB_O27"

    def test_omb_o27_to_json(self):
        msg = OMB_O27()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OMB_O27"
