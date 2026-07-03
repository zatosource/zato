from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ORG_O20


class TestOrgO20:
    """Comprehensive tests for OrgO20 message."""

    def test_org_o20_create(self):
        msg = ORG_O20()
        assert msg._structure_id == "ORG_O20"

    def test_org_o20_segment_access(self):
        msg = ORG_O20()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"

    def test_org_o20_to_dict(self):
        msg = ORG_O20()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORG_O20"

    def test_org_o20_to_json(self):
        msg = ORG_O20()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORG_O20"
