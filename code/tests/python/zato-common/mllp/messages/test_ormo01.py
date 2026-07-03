from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ORM_O01


class TestOrmO01:
    """Comprehensive tests for OrmO01 message."""

    def test_orm_o01_create(self):
        msg = ORM_O01()
        assert msg._structure_id == "ORM_O01"

    def test_orm_o01_segment_access(self):
        msg = ORM_O01()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_orm_o01_to_dict(self):
        msg = ORM_O01()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORM_O01"

    def test_orm_o01_to_json(self):
        msg = ORM_O01()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORM_O01"
