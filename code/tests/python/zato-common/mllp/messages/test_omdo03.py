from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import OMD_O03


class TestOmdO03:
    """Comprehensive tests for OmdO03 message."""

    def test_omd_o03_create(self):
        msg = OMD_O03()
        assert msg._structure_id == "OMD_O03"

    def test_omd_o03_segment_access(self):
        msg = OMD_O03()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_omd_o03_to_dict(self):
        msg = OMD_O03()

        result = msg.to_dict()

        assert result["_structure_id"] == "OMD_O03"

    def test_omd_o03_to_json(self):
        msg = OMD_O03()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OMD_O03"
