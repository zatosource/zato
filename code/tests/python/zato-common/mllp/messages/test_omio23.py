from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import OMI_O23


class TestOmiO23:
    """Comprehensive tests for OmiO23 message."""

    def test_omi_o23_create(self):
        msg = OMI_O23()
        assert msg._structure_id == "OMI_O23"

    def test_omi_o23_segment_access(self):
        msg = OMI_O23()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_omi_o23_to_dict(self):
        msg = OMI_O23()

        result = msg.to_dict()

        assert result["_structure_id"] == "OMI_O23"

    def test_omi_o23_to_json(self):
        msg = OMI_O23()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OMI_O23"
