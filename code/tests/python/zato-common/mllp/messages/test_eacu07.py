from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import EAC_U07


class TestEacU07:
    """Comprehensive tests for EacU07 message."""

    def test_eac_u07_create(self):
        msg = EAC_U07()
        assert msg._structure_id == "EAC_U07"

    def test_eac_u07_segment_access(self):
        msg = EAC_U07()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.equ._segment_id == "EQU"
        assert msg.ecd._segment_id == "ECD"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.sac._segment_id == "SAC"
        assert msg.cns._segment_id == "CNS"

    def test_eac_u07_to_dict(self):
        msg = EAC_U07()

        result = msg.to_dict()

        assert result["_structure_id"] == "EAC_U07"

    def test_eac_u07_to_json(self):
        msg = EAC_U07()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "EAC_U07"
