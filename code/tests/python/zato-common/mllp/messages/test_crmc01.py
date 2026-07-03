from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import CRM_C01


class TestCrmC01:
    """Comprehensive tests for CrmC01 message."""

    def test_crm_c01_create(self):
        msg = CRM_C01()
        assert msg._structure_id == "CRM_C01"

    def test_crm_c01_segment_access(self):
        msg = CRM_C01()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_crm_c01_to_dict(self):
        msg = CRM_C01()

        result = msg.to_dict()

        assert result["_structure_id"] == "CRM_C01"

    def test_crm_c01_to_json(self):
        msg = CRM_C01()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "CRM_C01"
