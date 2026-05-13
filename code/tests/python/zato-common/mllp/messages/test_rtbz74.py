from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RtbZ74
from zato.hl7v2.v2_9.segments import DSC, MSA, MSH, QAK, QPD, RDF, UAC


class TestRtbZ74:
    """Comprehensive tests for RtbZ74 message."""

    def test_rtb_z74_create(self):
        msg = RtbZ74()
        assert msg._structure_id == "RTB_Z74"

    def test_rtb_z74_segment_access(self):
        msg = RtbZ74()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"
        assert msg.qak._segment_id == "QAK"
        assert msg.qpd._segment_id == "QPD"
        assert msg.rdf._segment_id == "RDF"
        assert msg.dsc._segment_id == "DSC"

    def test_rtb_z74_to_dict(self):
        msg = RtbZ74()

        result = msg.to_dict()

        assert result["_structure_id"] == "RTB_Z74"

    def test_rtb_z74_to_json(self):
        msg = RtbZ74()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RTB_Z74"
