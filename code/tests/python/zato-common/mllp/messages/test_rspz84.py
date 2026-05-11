from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RspZ84
from zato.hl7v2.v2_9.segments import DSC, ERR, MSA, MSH, QAK, QPD, RDF, UAC


class TestRspZ84:
    """Comprehensive tests for RspZ84 message."""

    def test_rsp_z84_create(self):
        msg = RspZ84()
        assert msg._structure_id == "RSP_Z84"

    def test_rsp_z84_segment_access(self):
        msg = RspZ84()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.err._segment_id == "ERR"
        assert msg.qak._segment_id == "QAK"
        assert msg.qpd._segment_id == "QPD"
        assert msg.rdf._segment_id == "RDF"
        assert msg.dsc._segment_id == "DSC"

    def test_rsp_z84_to_dict(self):
        msg = RspZ84()

        result = msg.to_dict()

        assert result["_structure_id"] == "RSP_Z84"

    def test_rsp_z84_to_json(self):
        msg = RspZ84()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RSP_Z84"
