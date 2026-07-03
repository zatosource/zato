from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import BPS_O29


class TestBpsO29:
    """Comprehensive tests for BpsO29 message."""

    def test_bps_o29_create(self):
        msg = BPS_O29()
        assert msg._structure_id == "BPS_O29"

    def test_bps_o29_segment_access(self):
        msg = BPS_O29()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_bps_o29_to_dict(self):
        msg = BPS_O29()

        result = msg.to_dict()

        assert result["_structure_id"] == "BPS_O29"

    def test_bps_o29_to_json(self):
        msg = BPS_O29()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "BPS_O29"
