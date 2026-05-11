from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import EhcE13
from zato.hl7v2.v2_9.segments import CTD, IVC, MSA, MSH, NTE, OBR, OBX, PID, PSG, PSL, PSS, RFI, TXA


class TestEhcE13:
    """Comprehensive tests for EhcE13 message."""

    def test_ehc_e13_create(self):
        msg = EhcE13()
        assert msg._structure_id == "EHC_E13"

    def test_ehc_e13_segment_access(self):
        msg = EhcE13()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.rfi._segment_id == "RFI"
        assert msg.ivc._segment_id == "IVC"
        assert msg.pss._segment_id == "PSS"
        assert msg.psg._segment_id == "PSG"
        assert msg.pid._segment_id == "PID"
        assert msg.psl._segment_id == "PSL"
        assert msg.ctd._segment_id == "CTD"
        assert msg.obr._segment_id == "OBR"
        assert msg.nte._segment_id == "NTE"
        assert msg.obx._segment_id == "OBX"
        assert msg.nte._segment_id == "NTE"
        assert msg.txa._segment_id == "TXA"

    def test_ehc_e13_to_dict(self):
        msg = EhcE13()

        result = msg.to_dict()

        assert result["_structure_id"] == "EHC_E13"

    def test_ehc_e13_to_json(self):
        msg = EhcE13()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "EHC_E13"
