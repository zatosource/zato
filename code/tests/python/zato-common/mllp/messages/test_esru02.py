from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ESR_U02


class TestEsrU02:
    """Comprehensive tests for EsrU02 message."""

    def test_esr_u02_create(self):
        msg = ESR_U02()
        assert msg._structure_id == "ESR_U02"

    def test_esr_u02_segment_access(self):
        msg = ESR_U02()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.equ._segment_id == "EQU"

    def test_esr_u02_to_dict(self):
        msg = ESR_U02()

        result = msg.to_dict()

        assert result["_structure_id"] == "ESR_U02"

    def test_esr_u02_to_json(self):
        msg = ESR_U02()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ESR_U02"
