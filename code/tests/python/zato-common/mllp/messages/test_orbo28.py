from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ORB_O28


class TestOrbO28:
    """Comprehensive tests for OrbO28 message."""

    def test_orb_o28_create(self):
        msg = ORB_O28()
        assert msg._structure_id == "ORB_O28"

    def test_orb_o28_segment_access(self):
        msg = ORB_O28()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.bpo._segment_id == "BPO"

    def test_orb_o28_to_dict(self):
        msg = ORB_O28()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORB_O28"

    def test_orb_o28_to_json(self):
        msg = ORB_O28()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORB_O28"
