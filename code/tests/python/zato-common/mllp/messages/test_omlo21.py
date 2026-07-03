from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import OML_O21


class TestOmlO21:
    """Comprehensive tests for OmlO21 message."""

    def test_oml_o21_create(self):
        msg = OML_O21()
        assert msg._structure_id == "OML_O21"

    def test_oml_o21_segment_access(self):
        msg = OML_O21()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_oml_o21_to_dict(self):
        msg = OML_O21()

        result = msg.to_dict()

        assert result["_structure_id"] == "OML_O21"

    def test_oml_o21_to_json(self):
        msg = OML_O21()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OML_O21"
