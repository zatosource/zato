from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import EsrU02
from zato.hl7v2.v2_9.segments import EQU, MSH, UAC


class TestEsrU02:
    """Comprehensive tests for EsrU02 message."""

    def test_esr_u02_create(self):
        msg = EsrU02()
        assert msg._structure_id == "ESR_U02"

    def test_esr_u02_segment_access(self):
        msg = EsrU02()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.equ._segment_id == "EQU"

    def test_esr_u02_to_dict(self):
        msg = EsrU02()

        result = msg.to_dict()

        assert result["_structure_id"] == "ESR_U02"

    def test_esr_u02_to_json(self):
        msg = EsrU02()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ESR_U02"
