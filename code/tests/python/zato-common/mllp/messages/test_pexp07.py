from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import PexP07
from zato.hl7v2.v2_9.segments import CSR, EVN, MSH, NK1, OBX, PCR, PD1, PEO, PES, PID, PV1, PV2, RXA, RXE, RXR, TQ1, UAC


class TestPexP07:
    """Comprehensive tests for PexP07 message."""

    def test_pex_p07_create(self):
        msg = PexP07()
        assert msg._structure_id == "PEX_P07"

    def test_pex_p07_segment_access(self):
        msg = PexP07()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.pes._segment_id == "PES"
        assert msg.peo._segment_id == "PEO"
        assert msg.pcr._segment_id == "PCR"
        assert msg.rxe._segment_id == "RXE"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.rxa._segment_id == "RXA"
        assert msg.rxr._segment_id == "RXR"
        assert msg.obx._segment_id == "OBX"
        assert msg.nk1._segment_id == "NK1"
        assert msg.rxe._segment_id == "RXE"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.rxa._segment_id == "RXA"
        assert msg.rxr._segment_id == "RXR"
        assert msg.obx._segment_id == "OBX"
        assert msg.csr._segment_id == "CSR"

    def test_pex_p07_to_dict(self):
        msg = PexP07()

        result = msg.to_dict()

        assert result["_structure_id"] == "PEX_P07"

    def test_pex_p07_to_json(self):
        msg = PexP07()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "PEX_P07"
