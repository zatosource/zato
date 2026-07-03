from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import UDM_Q05


class TestUdmQ05:
    """Comprehensive tests for UdmQ05 message."""

    def test_udm_q05_create(self):
        msg = UDM_Q05()
        assert msg._structure_id == "UDM_Q05"

    def test_udm_q05_segment_access(self):
        msg = UDM_Q05()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.dsc._segment_id == "DSC"

    def test_udm_q05_to_dict(self):
        msg = UDM_Q05()

        result = msg.to_dict()

        assert result["_structure_id"] == "UDM_Q05"

    def test_udm_q05_to_json(self):
        msg = UDM_Q05()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "UDM_Q05"
