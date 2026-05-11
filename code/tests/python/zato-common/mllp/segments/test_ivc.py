from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import IVC


invoice_date_time = "test_invoice_date_time"
payment_terms = "test_payment_terms"
last_invoice_indicator = "test_last_invoice_indicat"
invoice_booking_period = "test_invoice_booking_peri"
origin = "test_origin"
provider_tax_id = "test_provider_tax_id"
payer_tax_id = "test_payer_tax_id"
sales_tax_id = "test_sales_tax_id"


class TestIVC:
    """Comprehensive tests for IVC segment."""

    def test_ivc_build_and_verify(self):
        seg = IVC()

        seg.invoice_date_time = invoice_date_time
        seg.payment_terms = payment_terms
        seg.last_invoice_indicator = last_invoice_indicator
        seg.invoice_booking_period = invoice_booking_period
        seg.origin = origin
        seg.provider_tax_id = provider_tax_id
        seg.payer_tax_id = payer_tax_id
        seg.sales_tax_id = sales_tax_id

        assert seg.invoice_date_time == invoice_date_time
        assert seg.payment_terms == payment_terms
        assert seg.last_invoice_indicator == last_invoice_indicator
        assert seg.invoice_booking_period == invoice_booking_period
        assert seg.origin == origin
        assert seg.provider_tax_id == provider_tax_id
        assert seg.payer_tax_id == payer_tax_id
        assert seg.sales_tax_id == sales_tax_id

    def test_ivc_to_dict(self):
        seg = IVC()

        seg.invoice_date_time = invoice_date_time
        seg.payment_terms = payment_terms
        seg.last_invoice_indicator = last_invoice_indicator
        seg.invoice_booking_period = invoice_booking_period
        seg.origin = origin
        seg.provider_tax_id = provider_tax_id
        seg.payer_tax_id = payer_tax_id
        seg.sales_tax_id = sales_tax_id

        result = seg.to_dict()

        assert result["_segment_id"] == "IVC"
        assert result["invoice_date_time"] == invoice_date_time
        assert result["payment_terms"] == payment_terms
        assert result["last_invoice_indicator"] == last_invoice_indicator
        assert result["invoice_booking_period"] == invoice_booking_period
        assert result["origin"] == origin
        assert result["provider_tax_id"] == provider_tax_id
        assert result["payer_tax_id"] == payer_tax_id
        assert result["sales_tax_id"] == sales_tax_id

    def test_ivc_to_json(self):
        seg = IVC()

        seg.invoice_date_time = invoice_date_time
        seg.payment_terms = payment_terms
        seg.last_invoice_indicator = last_invoice_indicator
        seg.invoice_booking_period = invoice_booking_period
        seg.origin = origin
        seg.provider_tax_id = provider_tax_id
        seg.payer_tax_id = payer_tax_id
        seg.sales_tax_id = sales_tax_id

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "IVC"
        assert result["invoice_date_time"] == invoice_date_time
        assert result["payment_terms"] == payment_terms
        assert result["last_invoice_indicator"] == last_invoice_indicator
        assert result["invoice_booking_period"] == invoice_booking_period
        assert result["origin"] == origin
        assert result["provider_tax_id"] == provider_tax_id
        assert result["payer_tax_id"] == payer_tax_id
        assert result["sales_tax_id"] == sales_tax_id
