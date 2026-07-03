from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import NMD_N02


class TestNmdN02:
    """Comprehensive tests for NmdN02 message."""

    def test_nmd_n02_create(self):
        msg = NMD_N02()
        assert msg._structure_id == "NMD_N02"

    def test_nmd_n02_segment_access(self):
        msg = NMD_N02()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_nmd_n02_to_dict(self):
        msg = NMD_N02()

        result = msg.to_dict()

        assert result["_structure_id"] == "NMD_N02"

    def test_nmd_n02_to_json(self):
        msg = NMD_N02()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "NMD_N02"
