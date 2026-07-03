from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ESU_U01


class TestEsuU01:
    """Comprehensive tests for EsuU01 message."""

    def test_esu_u01_create(self):
        msg = ESU_U01()
        assert msg._structure_id == "ESU_U01"

    def test_esu_u01_segment_access(self):
        msg = ESU_U01()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.equ._segment_id == "EQU"

    def test_esu_u01_to_dict(self):
        msg = ESU_U01()

        result = msg.to_dict()

        assert result["_structure_id"] == "ESU_U01"

    def test_esu_u01_to_json(self):
        msg = ESU_U01()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ESU_U01"
