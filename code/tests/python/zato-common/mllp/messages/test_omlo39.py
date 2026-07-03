from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import OML_O39


class TestOmlO39:
    """Comprehensive tests for OmlO39 message."""

    def test_oml_o39_create(self):
        msg = OML_O39()
        assert msg._structure_id == "OML_O39"

    def test_oml_o39_segment_access(self):
        msg = OML_O39()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_oml_o39_to_dict(self):
        msg = OML_O39()

        result = msg.to_dict()

        assert result["_structure_id"] == "OML_O39"

    def test_oml_o39_to_json(self):
        msg = OML_O39()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OML_O39"
