from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import NmdN02
from zato.hl7v2.v2_9.segments import MSH, NCK, NSC, NST, UAC


class TestNmdN02:
    """Comprehensive tests for NmdN02 message."""

    def test_nmd_n02_create(self):
        msg = NmdN02()
        assert msg._structure_id == "NMD_N02"

    def test_nmd_n02_segment_access(self):
        msg = NmdN02()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.nck._segment_id == "NCK"
        assert msg.nst._segment_id == "NST"
        assert msg.nsc._segment_id == "NSC"

    def test_nmd_n02_to_dict(self):
        msg = NmdN02()

        result = msg.to_dict()

        assert result["_structure_id"] == "NMD_N02"

    def test_nmd_n02_to_json(self):
        msg = NmdN02()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "NMD_N02"
