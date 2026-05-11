from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import EhcE15
from zato.hl7v2.v2_9.segments import ADJ, IPR, IVC, MSH, PMT, PRT, PSG, PSL, PSS, PYE


class TestEhcE15:
    """Comprehensive tests for EhcE15 message."""

    def test_ehc_e15_create(self):
        msg = EhcE15()
        assert msg._structure_id == "EHC_E15"

    def test_ehc_e15_segment_access(self):
        msg = EhcE15()

        assert msg.msh._segment_id == "MSH"
        assert msg.pmt._segment_id == "PMT"
        assert msg.pye._segment_id == "PYE"
        assert msg.ipr._segment_id == "IPR"
        assert msg.ivc._segment_id == "IVC"
        assert msg.pss._segment_id == "PSS"
        assert msg.psg._segment_id == "PSG"
        assert msg.psl._segment_id == "PSL"
        assert msg.adj._segment_id == "ADJ"
        assert msg.prt._segment_id == "PRT"

    def test_ehc_e15_to_dict(self):
        msg = EhcE15()

        result = msg.to_dict()

        assert result["_structure_id"] == "EHC_E15"

    def test_ehc_e15_to_json(self):
        msg = EhcE15()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "EHC_E15"
