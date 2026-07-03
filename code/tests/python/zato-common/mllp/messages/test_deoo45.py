from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import DEO_O45


class TestDeoO45:
    """Comprehensive tests for DeoO45 message."""

    def test_deo_o45_create(self):
        msg = DEO_O45()
        assert msg._structure_id == "DEO_O45"

    def test_deo_o45_segment_access(self):
        msg = DEO_O45()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_deo_o45_to_dict(self):
        msg = DEO_O45()

        result = msg.to_dict()

        assert result["_structure_id"] == "DEO_O45"

    def test_deo_o45_to_json(self):
        msg = DEO_O45()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "DEO_O45"
