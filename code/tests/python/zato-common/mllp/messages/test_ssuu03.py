from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import SSU_U03


class TestSsuU03:
    """Comprehensive tests for SsuU03 message."""

    def test_ssu_u03_create(self):
        msg = SSU_U03()
        assert msg._structure_id == "SSU_U03"

    def test_ssu_u03_segment_access(self):
        msg = SSU_U03()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.equ._segment_id == "EQU"

    def test_ssu_u03_to_dict(self):
        msg = SSU_U03()

        result = msg.to_dict()

        assert result["_structure_id"] == "SSU_U03"

    def test_ssu_u03_to_json(self):
        msg = SSU_U03()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "SSU_U03"
