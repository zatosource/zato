from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import OrgO20
from zato.hl7v2.v2_9.segments import MSA, MSH, OBR, ORC, PID, SPM, TQ1, UAC


class TestOrgO20:
    """Comprehensive tests for OrgO20 message."""

    def test_org_o20_create(self):
        msg = OrgO20()
        assert msg._structure_id == "ORG_O20"

    def test_org_o20_segment_access(self):
        msg = OrgO20()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.obr._segment_id == "OBR"
        assert msg.spm._segment_id == "SPM"

    def test_org_o20_to_dict(self):
        msg = OrgO20()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORG_O20"

    def test_org_o20_to_json(self):
        msg = OrgO20()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORG_O20"
