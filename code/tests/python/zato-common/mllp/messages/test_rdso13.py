from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RDS_O13


class TestRdsO13:
    """Comprehensive tests for RdsO13 message."""

    def test_rds_o13_create(self):
        msg = RDS_O13()
        assert msg._structure_id == "RDS_O13"

    def test_rds_o13_segment_access(self):
        msg = RDS_O13()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_rds_o13_to_dict(self):
        msg = RDS_O13()

        result = msg.to_dict()

        assert result["_structure_id"] == "RDS_O13"

    def test_rds_o13_to_json(self):
        msg = RDS_O13()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RDS_O13"
