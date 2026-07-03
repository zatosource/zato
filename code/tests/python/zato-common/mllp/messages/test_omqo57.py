from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import OMQ_O57


class TestOmqO57:
    """Comprehensive tests for OmqO57 message."""

    def test_omq_o57_create(self):
        msg = OMQ_O57()
        assert msg._structure_id == "OMQ_O57"

    def test_omq_o57_segment_access(self):
        msg = OMQ_O57()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_omq_o57_to_dict(self):
        msg = OMQ_O57()

        result = msg.to_dict()

        assert result["_structure_id"] == "OMQ_O57"

    def test_omq_o57_to_json(self):
        msg = OMQ_O57()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OMQ_O57"
