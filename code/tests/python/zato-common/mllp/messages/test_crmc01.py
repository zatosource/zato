from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import CrmC01
from zato.hl7v2.v2_9.segments import CSR, MSH, PID, PV1, UAC


class TestCrmC01:
    """Comprehensive tests for CrmC01 message."""

    def test_crm_c01_create(self):
        msg = CrmC01()
        assert msg._structure_id == "CRM_C01"

    def test_crm_c01_segment_access(self):
        msg = CrmC01()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pv1._segment_id == "PV1"
        assert msg.csr._segment_id == "CSR"

    def test_crm_c01_to_dict(self):
        msg = CrmC01()

        result = msg.to_dict()

        assert result["_structure_id"] == "CRM_C01"

    def test_crm_c01_to_json(self):
        msg = CrmC01()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "CRM_C01"
