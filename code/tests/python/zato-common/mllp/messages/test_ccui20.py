from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import CCU_I20


class TestCcuI20:
    """Comprehensive tests for CcuI20 message."""

    def test_ccu_i20_create(self):
        msg = CCU_I20()
        assert msg._structure_id == "CCU_I20"

    def test_ccu_i20_segment_access(self):
        msg = CCU_I20()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.rf1._segment_id == "RF1"

    def test_ccu_i20_to_dict(self):
        msg = CCU_I20()

        result = msg.to_dict()

        assert result["_structure_id"] == "CCU_I20"

    def test_ccu_i20_to_json(self):
        msg = CCU_I20()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "CCU_I20"
