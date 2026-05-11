from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PDA


death_certified_indicator = "test_death_certified_indi"
death_certificate_signed_date_time = "test_death_certificate_si"
autopsy_indicator = "test_autopsy_indicator"
coroner_indicator = "test_coroner_indicator"


class TestPDA:
    """Comprehensive tests for PDA segment."""

    def test_pda_build_and_verify(self):
        seg = PDA()

        seg.death_certified_indicator = death_certified_indicator
        seg.death_certificate_signed_date_time = death_certificate_signed_date_time
        seg.autopsy_indicator = autopsy_indicator
        seg.coroner_indicator = coroner_indicator

        assert seg.death_certified_indicator == death_certified_indicator
        assert seg.death_certificate_signed_date_time == death_certificate_signed_date_time
        assert seg.autopsy_indicator == autopsy_indicator
        assert seg.coroner_indicator == coroner_indicator

    def test_pda_to_dict(self):
        seg = PDA()

        seg.death_certified_indicator = death_certified_indicator
        seg.death_certificate_signed_date_time = death_certificate_signed_date_time
        seg.autopsy_indicator = autopsy_indicator
        seg.coroner_indicator = coroner_indicator

        result = seg.to_dict()

        assert result["_segment_id"] == "PDA"
        assert result["death_certified_indicator"] == death_certified_indicator
        assert result["death_certificate_signed_date_time"] == death_certificate_signed_date_time
        assert result["autopsy_indicator"] == autopsy_indicator
        assert result["coroner_indicator"] == coroner_indicator

    def test_pda_to_json(self):
        seg = PDA()

        seg.death_certified_indicator = death_certified_indicator
        seg.death_certificate_signed_date_time = death_certificate_signed_date_time
        seg.autopsy_indicator = autopsy_indicator
        seg.coroner_indicator = coroner_indicator

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PDA"
        assert result["death_certified_indicator"] == death_certified_indicator
        assert result["death_certificate_signed_date_time"] == death_certificate_signed_date_time
        assert result["autopsy_indicator"] == autopsy_indicator
        assert result["coroner_indicator"] == coroner_indicator
