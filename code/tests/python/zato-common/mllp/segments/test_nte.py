from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import NTE


set_id_nte = "test_set_id_nte"
source_of_comment = "test_source_of_comment"
entered_date_time = "test_entered_date_time"
effective_start_date = "test_effective_start_date"
expiration_date = "test_expiration_date"


class TestNTE:
    """Comprehensive tests for NTE segment."""

    def test_nte_build_and_verify(self):
        seg = NTE()

        seg.set_id_nte = set_id_nte
        seg.source_of_comment = source_of_comment
        seg.entered_date_time = entered_date_time
        seg.effective_start_date = effective_start_date
        seg.expiration_date = expiration_date

        assert seg.set_id_nte == set_id_nte
        assert seg.source_of_comment == source_of_comment
        assert seg.entered_date_time == entered_date_time
        assert seg.effective_start_date == effective_start_date
        assert seg.expiration_date == expiration_date

    def test_nte_to_dict(self):
        seg = NTE()

        seg.set_id_nte = set_id_nte
        seg.source_of_comment = source_of_comment
        seg.entered_date_time = entered_date_time
        seg.effective_start_date = effective_start_date
        seg.expiration_date = expiration_date

        result = seg.to_dict()

        assert result["_segment_id"] == "NTE"
        assert result["set_id_nte"] == set_id_nte
        assert result["source_of_comment"] == source_of_comment
        assert result["entered_date_time"] == entered_date_time
        assert result["effective_start_date"] == effective_start_date
        assert result["expiration_date"] == expiration_date

    def test_nte_to_json(self):
        seg = NTE()

        seg.set_id_nte = set_id_nte
        seg.source_of_comment = source_of_comment
        seg.entered_date_time = entered_date_time
        seg.effective_start_date = effective_start_date
        seg.expiration_date = expiration_date

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "NTE"
        assert result["set_id_nte"] == set_id_nte
        assert result["source_of_comment"] == source_of_comment
        assert result["entered_date_time"] == entered_date_time
        assert result["effective_start_date"] == effective_start_date
        assert result["expiration_date"] == expiration_date
