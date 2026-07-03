from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import TCU_U10


class TestTcuU10:
    """Comprehensive tests for TcuU10 message."""

    def test_tcu_u10_create(self):
        msg = TCU_U10()
        assert msg._structure_id == "TCU_U10"

    def test_tcu_u10_segment_access(self):
        msg = TCU_U10()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.equ._segment_id == "EQU"
        assert msg.spm._segment_id == "SPM"

    def test_tcu_u10_to_dict(self):
        msg = TCU_U10()

        result = msg.to_dict()

        assert result["_structure_id"] == "TCU_U10"

    def test_tcu_u10_to_json(self):
        msg = TCU_U10()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "TCU_U10"
