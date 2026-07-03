from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RDR_RDR


class TestRdrRdr:
    """Comprehensive tests for RdrRdr message."""

    def test_rdr_rdr_create(self):
        msg = RDR_RDR()
        assert msg._structure_id == "RDR_RDR"

    def test_rdr_rdr_segment_access(self):
        msg = RDR_RDR()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.sft._segment_id == "SFT"
        assert msg.uac._segment_id == "UAC"
        assert msg.dsc._segment_id == "DSC"

    def test_rdr_rdr_to_dict(self):
        msg = RDR_RDR()

        result = msg.to_dict()

        assert result["_structure_id"] == "RDR_RDR"

    def test_rdr_rdr_to_json(self):
        msg = RDR_RDR()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RDR_RDR"
