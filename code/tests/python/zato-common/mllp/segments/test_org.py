from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import ORG


set_id_org = "test_set_id_org"
primary_org_unit_indicator = "test_primary_org_unit_ind"
board_approval_indicator = "test_board_approval_indic"
primary_care_physician_indicator = "test_primary_care_physici"


class TestORG:
    """Comprehensive tests for ORG segment."""

    def test_org_build_and_verify(self):
        seg = ORG()

        seg.set_id_org = set_id_org
        seg.primary_org_unit_indicator = primary_org_unit_indicator
        seg.board_approval_indicator = board_approval_indicator
        seg.primary_care_physician_indicator = primary_care_physician_indicator

        assert seg.set_id_org == set_id_org
        assert seg.primary_org_unit_indicator == primary_org_unit_indicator
        assert seg.board_approval_indicator == board_approval_indicator
        assert seg.primary_care_physician_indicator == primary_care_physician_indicator

    def test_org_to_dict(self):
        seg = ORG()

        seg.set_id_org = set_id_org
        seg.primary_org_unit_indicator = primary_org_unit_indicator
        seg.board_approval_indicator = board_approval_indicator
        seg.primary_care_physician_indicator = primary_care_physician_indicator

        result = seg.to_dict()

        assert result["_segment_id"] == "ORG"
        assert result["set_id_org"] == set_id_org
        assert result["primary_org_unit_indicator"] == primary_org_unit_indicator
        assert result["board_approval_indicator"] == board_approval_indicator
        assert result["primary_care_physician_indicator"] == primary_care_physician_indicator

    def test_org_to_json(self):
        seg = ORG()

        seg.set_id_org = set_id_org
        seg.primary_org_unit_indicator = primary_org_unit_indicator
        seg.board_approval_indicator = board_approval_indicator
        seg.primary_care_physician_indicator = primary_care_physician_indicator

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "ORG"
        assert result["set_id_org"] == set_id_org
        assert result["primary_org_unit_indicator"] == primary_org_unit_indicator
        assert result["board_approval_indicator"] == board_approval_indicator
        assert result["primary_care_physician_indicator"] == primary_care_physician_indicator
