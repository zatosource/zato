from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import EanU09
from zato.hl7v2.v2_9.segments import EQU, MSH, NDS, NTE, UAC


class TestEanU09:
    """Comprehensive tests for EanU09 message."""

    def test_ean_u09_create(self):
        msg = EanU09()
        assert msg._structure_id == "EAN_U09"

    def test_ean_u09_segment_access(self):
        msg = EanU09()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.equ._segment_id == "EQU"
        assert msg.nds._segment_id == "NDS"
        assert msg.nte._segment_id == "NTE"

    def test_ean_u09_to_dict(self):
        msg = EanU09()

        result = msg.to_dict()

        assert result["_structure_id"] == "EAN_U09"

    def test_ean_u09_to_json(self):
        msg = EanU09()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "EAN_U09"
