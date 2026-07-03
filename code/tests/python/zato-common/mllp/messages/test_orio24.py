from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ORI_O24


class TestOriO24:
    """Comprehensive tests for OriO24 message."""

    def test_ori_o24_create(self):
        msg = ORI_O24()
        assert msg._structure_id == "ORI_O24"

    def test_ori_o24_segment_access(self):
        msg = ORI_O24()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.obr._segment_id == "OBR"

    def test_ori_o24_to_dict(self):
        msg = ORI_O24()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORI_O24"

    def test_ori_o24_to_json(self):
        msg = ORI_O24()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORI_O24"
