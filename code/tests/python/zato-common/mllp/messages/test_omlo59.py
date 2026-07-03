from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import OML_O59


class TestOmlO59:
    """Comprehensive tests for OmlO59 message."""

    def test_oml_o59_create(self):
        msg = OML_O59()
        assert msg._structure_id == "OML_O59"

    def test_oml_o59_segment_access(self):
        msg = OML_O59()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_oml_o59_to_dict(self):
        msg = OML_O59()

        result = msg.to_dict()

        assert result["_structure_id"] == "OML_O59"

    def test_oml_o59_to_json(self):
        msg = OML_O59()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OML_O59"
