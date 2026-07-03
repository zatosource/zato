from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RDY_Z80


class TestRdyZ80:
    """Comprehensive tests for RdyZ80 message."""

    def test_rdy_z80_create(self):
        msg = RDY_Z80()
        assert msg._structure_id == "RDY_Z80"

    def test_rdy_z80_segment_access(self):
        msg = RDY_Z80()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.err._segment_id == "ERR"
        assert msg.qak._segment_id == "QAK"
        assert msg.qpd._segment_id == "QPD"
        assert msg.dsc._segment_id == "DSC"

    def test_rdy_z80_to_dict(self):
        msg = RDY_Z80()

        result = msg.to_dict()

        assert result["_structure_id"] == "RDY_Z80"

    def test_rdy_z80_to_json(self):
        msg = RDY_Z80()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RDY_Z80"
