from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import OrdO04
from zato.hl7v2.v2_9.segments import MSA, MSH, ORC, PID, TQ1, UAC


class TestOrdO04:
    """Comprehensive tests for OrdO04 message."""

    def test_ord_o04_create(self):
        msg = OrdO04()
        assert msg._structure_id == "ORD_O04"

    def test_ord_o04_segment_access(self):
        msg = OrdO04()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"

    def test_ord_o04_to_dict(self):
        msg = OrdO04()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORD_O04"

    def test_ord_o04_to_json(self):
        msg = OrdO04()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORD_O04"
