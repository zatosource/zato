from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PRA


provider_billing = "test_provider_billing"
date_entered_practice = "test_date_entered_practic"
date_left_practice = "test_date_left_practice"
set_id_pra = "test_set_id_pra"


class TestPRA:
    """Comprehensive tests for PRA segment."""

    def test_pra_build_and_verify(self):
        seg = PRA()

        seg.provider_billing = provider_billing
        seg.date_entered_practice = date_entered_practice
        seg.date_left_practice = date_left_practice
        seg.set_id_pra = set_id_pra

        assert seg.provider_billing == provider_billing
        assert seg.date_entered_practice == date_entered_practice
        assert seg.date_left_practice == date_left_practice
        assert seg.set_id_pra == set_id_pra

    def test_pra_to_dict(self):
        seg = PRA()

        seg.provider_billing = provider_billing
        seg.date_entered_practice = date_entered_practice
        seg.date_left_practice = date_left_practice
        seg.set_id_pra = set_id_pra

        result = seg.to_dict()

        assert result["_segment_id"] == "PRA"
        assert result["provider_billing"] == provider_billing
        assert result["date_entered_practice"] == date_entered_practice
        assert result["date_left_practice"] == date_left_practice
        assert result["set_id_pra"] == set_id_pra

    def test_pra_to_json(self):
        seg = PRA()

        seg.provider_billing = provider_billing
        seg.date_entered_practice = date_entered_practice
        seg.date_left_practice = date_left_practice
        seg.set_id_pra = set_id_pra

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PRA"
        assert result["provider_billing"] == provider_billing
        assert result["date_entered_practice"] == date_entered_practice
        assert result["date_left_practice"] == date_left_practice
        assert result["set_id_pra"] == set_id_pra
