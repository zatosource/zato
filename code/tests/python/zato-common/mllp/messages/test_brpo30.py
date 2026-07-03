from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import BRP_O30


class TestBrpO30:
    """Comprehensive tests for BrpO30 message."""

    def test_brp_o30_create(self):
        msg = BRP_O30()
        assert msg._structure_id == "BRP_O30"

    def test_brp_o30_segment_access(self):
        msg = BRP_O30()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.bpo._segment_id == "BPO"

    def test_brp_o30_to_dict(self):
        msg = BRP_O30()

        result = msg.to_dict()

        assert result["_structure_id"] == "BRP_O30"

    def test_brp_o30_to_json(self):
        msg = BRP_O30()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "BRP_O30"
