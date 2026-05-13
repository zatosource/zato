from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import RDF


number_of_columns_per_row = "test_number_of_columns_pe"


class TestRDF:
    """Comprehensive tests for RDF segment."""

    def test_rdf_build_and_verify(self):
        seg = RDF()

        seg.number_of_columns_per_row = number_of_columns_per_row

        assert seg.number_of_columns_per_row == number_of_columns_per_row

    def test_rdf_to_dict(self):
        seg = RDF()

        seg.number_of_columns_per_row = number_of_columns_per_row

        result = seg.to_dict()

        assert result["_segment_id"] == "RDF"
        assert result["number_of_columns_per_row"] == number_of_columns_per_row

    def test_rdf_to_json(self):
        seg = RDF()

        seg.number_of_columns_per_row = number_of_columns_per_row

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "RDF"
        assert result["number_of_columns_per_row"] == number_of_columns_per_row
