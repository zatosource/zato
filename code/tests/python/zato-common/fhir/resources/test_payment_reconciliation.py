from __future__ import annotations

from zato.fhir.r4_0_1 import PaymentReconciliation


class TestPaymentReconciliation:

    def test_create(self):
        obj = PaymentReconciliation()
        assert obj._resource_type == "PaymentReconciliation"

    def test_to_dict(self):
        obj = PaymentReconciliation()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "PaymentReconciliation"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = PaymentReconciliation()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "PaymentReconciliation" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = PaymentReconciliation()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "PaymentReconciliation", "id": "from-dict-id"}
        obj = PaymentReconciliation.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "PaymentReconciliation", "id": "from-json-id"}'
        obj = PaymentReconciliation.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = PaymentReconciliation()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = PaymentReconciliation.from_json(json_str)
        assert obj2.id == "roundtrip-id"
