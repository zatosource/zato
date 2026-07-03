from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RRD_O14


class TestRrdO14:
    """Comprehensive tests for RrdO14 message."""

    def test_rrd_o14_create(self):
        msg = RRD_O14()
        assert msg._structure_id == "RRD_O14"

    def test_rrd_o14_segment_access(self):
        msg = RRD_O14()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.rxd._segment_id == "RXD"

    def test_rrd_o14_to_dict(self):
        msg = RRD_O14()

        result = msg.to_dict()

        assert result["_structure_id"] == "RRD_O14"

    def test_rrd_o14_to_json(self):
        msg = RRD_O14()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RRD_O14"
