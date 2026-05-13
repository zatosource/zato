from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import EhcE12
from zato.hl7v2.v2_9.segments import CTD, IVC, MSH, NTE, OBR, PID, PSG, PSS, RFI


class TestEhcE12:
    """Comprehensive tests for EhcE12 message."""

    def test_ehc_e12_create(self):
        msg = EhcE12()
        assert msg._structure_id == "EHC_E12"

    def test_ehc_e12_segment_access(self):
        msg = EhcE12()

        assert msg.msh._segment_id == "MSH"
        assert msg.rfi._segment_id == "RFI"
        assert msg.ivc._segment_id == "IVC"
        assert msg.pss._segment_id == "PSS"
        assert msg.psg._segment_id == "PSG"
        assert msg.pid._segment_id == "PID"
        assert msg.ctd._segment_id == "CTD"
        assert msg.obr._segment_id == "OBR"
        assert msg.nte._segment_id == "NTE"

    def test_ehc_e12_to_dict(self):
        msg = EhcE12()

        result = msg.to_dict()

        assert result["_structure_id"] == "EHC_E12"

    def test_ehc_e12_to_json(self):
        msg = EhcE12()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "EHC_E12"
