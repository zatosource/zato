from __future__ import annotations

from zato.hl7v2_rs import validate_cardinality



class TestACKCardinality:

    def test_ack_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        result = validate_cardinality("ACK", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ack_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        result = validate_cardinality("ACK", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ack_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ACK", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestDBCO41Cardinality:

    def test_dbc_o41_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("DBC_O41", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_dbc_o41_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("DBC_O41", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_dbc_o41_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("DBC_O41", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestDBCO42Cardinality:

    def test_dbc_o42_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("DBC_O42", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_dbc_o42_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("DBC_O42", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_dbc_o42_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("DBC_O42", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestDELO46Cardinality:

    def test_del_o46_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        segment_counts["DON"] = 1
        result = validate_cardinality("DEL_O46", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_del_o46_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        segment_counts["DON"] = 1
        result = validate_cardinality("DEL_O46", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_del_o46_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        segment_counts["DON"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("DEL_O46", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestDEOO45Cardinality:

    def test_deo_o45_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        group_counts["DEO_O45.DONATION_ORDER"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("DEO_O45", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_deo_o45_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        group_counts["DEO_O45.DONATION_ORDER"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("DEO_O45", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_deo_o45_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        group_counts["DEO_O45.DONATION_ORDER"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("DEO_O45", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestDERO44Cardinality:

    def test_der_o44_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        group_counts["DER_O44.DONOR_ORDER"] = 1
        segment_counts["OBR"] = 1
        result = validate_cardinality("DER_O44", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_der_o44_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        group_counts["DER_O44.DONOR_ORDER"] = 1
        segment_counts["OBR"] = 1
        result = validate_cardinality("DER_O44", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_der_o44_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        group_counts["DER_O44.DONOR_ORDER"] = 1
        segment_counts["OBR"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("DER_O44", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestDPRO48Cardinality:

    def test_dpr_o48_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        group_counts["DPR_O48.DONATION_ORDER"] = 1
        segment_counts["OBR"] = 1
        segment_counts["DON"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("DPR_O48", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_dpr_o48_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        group_counts["DPR_O48.DONATION_ORDER"] = 1
        segment_counts["OBR"] = 1
        segment_counts["DON"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("DPR_O48", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_dpr_o48_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        group_counts["DPR_O48.DONATION_ORDER"] = 1
        segment_counts["OBR"] = 1
        segment_counts["DON"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("DPR_O48", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestDRCO47Cardinality:

    def test_drc_o47_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        group_counts["DRC_O47.DONATION_ORDER"] = 1
        segment_counts["OBR"] = 1
        result = validate_cardinality("DRC_O47", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_drc_o47_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        group_counts["DRC_O47.DONATION_ORDER"] = 1
        segment_counts["OBR"] = 1
        result = validate_cardinality("DRC_O47", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_drc_o47_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        group_counts["DRC_O47.DONATION_ORDER"] = 1
        segment_counts["OBR"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("DRC_O47", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestDRGO43Cardinality:

    def test_drg_o43_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        result = validate_cardinality("DRG_O43", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_drg_o43_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        result = validate_cardinality("DRG_O43", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_drg_o43_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("DRG_O43", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestEHCE01Cardinality:

    def test_ehc_e01_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["IVC"] = 1
        choice_children["EHC_E01.INVOICE_INFORMATION_SUBMIT"] = ["IVC"]
        result = validate_cardinality("EHC_E01", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ehc_e01_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["IVC"] = 1
        choice_children["EHC_E01.INVOICE_INFORMATION_SUBMIT"] = ["IVC"]
        result = validate_cardinality("EHC_E01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ehc_e01_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["IVC"] = 1
        choice_children["EHC_E01.INVOICE_INFORMATION_SUBMIT"] = ["IVC"]
        segment_counts["MSH"] = 2
        result = validate_cardinality("EHC_E01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

    def test_ehc_e01_choice_none_ehc_e01_invoice_information_submit(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["EHC_E01.INVOICE_INFORMATION_SUBMIT"] = 1
        result = validate_cardinality("EHC_E01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_NONE" in e.code for e in result.errors)

    def test_ehc_e01_choice_multiple_ehc_e01_invoice_information_submit(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["IVC"] = 1
        segment_counts["PYE"] = 1
        choice_children["EHC_E01.INVOICE_INFORMATION_SUBMIT"] = ["IVC", "PYE"]
        result = validate_cardinality("EHC_E01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_MULTIPLE" in e.code for e in result.errors)

class TestEHCE02Cardinality:

    def test_ehc_e02_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["IVC"] = 1
        choice_children["EHC_E02.INVOICE_INFORMATION_CANCEL"] = ["IVC"]
        result = validate_cardinality("EHC_E02", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ehc_e02_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["IVC"] = 1
        choice_children["EHC_E02.INVOICE_INFORMATION_CANCEL"] = ["IVC"]
        result = validate_cardinality("EHC_E02", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ehc_e02_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["IVC"] = 1
        choice_children["EHC_E02.INVOICE_INFORMATION_CANCEL"] = ["IVC"]
        segment_counts["MSH"] = 2
        result = validate_cardinality("EHC_E02", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

    def test_ehc_e02_choice_none_ehc_e02_invoice_information_cancel(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["EHC_E02.INVOICE_INFORMATION_CANCEL"] = 1
        result = validate_cardinality("EHC_E02", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_NONE" in e.code for e in result.errors)

    def test_ehc_e02_choice_multiple_ehc_e02_invoice_information_cancel(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["IVC"] = 1
        segment_counts["PYE"] = 1
        choice_children["EHC_E02.INVOICE_INFORMATION_CANCEL"] = ["IVC", "PYE"]
        result = validate_cardinality("EHC_E02", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_MULTIPLE" in e.code for e in result.errors)

class TestEHCE04Cardinality:

    def test_ehc_e04_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["IVC"] = 1
        choice_children["EHC_E04.REASSESSMENT_REQUEST_INFO"] = ["IVC"]
        result = validate_cardinality("EHC_E04", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ehc_e04_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["IVC"] = 1
        choice_children["EHC_E04.REASSESSMENT_REQUEST_INFO"] = ["IVC"]
        result = validate_cardinality("EHC_E04", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ehc_e04_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["IVC"] = 1
        choice_children["EHC_E04.REASSESSMENT_REQUEST_INFO"] = ["IVC"]
        segment_counts["MSH"] = 2
        result = validate_cardinality("EHC_E04", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

    def test_ehc_e04_choice_none_ehc_e04_reassessment_request_info(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["EHC_E04.REASSESSMENT_REQUEST_INFO"] = 1
        result = validate_cardinality("EHC_E04", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_NONE" in e.code for e in result.errors)

    def test_ehc_e04_choice_multiple_ehc_e04_reassessment_request_info(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["IVC"] = 1
        segment_counts["NTE"] = 1
        choice_children["EHC_E04.REASSESSMENT_REQUEST_INFO"] = ["IVC", "NTE"]
        result = validate_cardinality("EHC_E04", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_MULTIPLE" in e.code for e in result.errors)

class TestEHCE10Cardinality:

    def test_ehc_e10_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        group_counts["EHC_E10.INVOICE_PROCESSING_RESULTS_INFO"] = 1
        segment_counts["IPR"] = 1
        segment_counts["PYE"] = 1
        segment_counts["IN1"] = 1
        segment_counts["IVC"] = 1
        group_counts["EHC_E10.PRODUCT_SERVICE_SECTION"] = 1
        segment_counts["PSS"] = 1
        group_counts["EHC_E10.PRODUCT_SERVICE_GROUP"] = 1
        segment_counts["PSG"] = 1
        group_counts["EHC_E10.PRODUCT_SERVICE_LINE_INFO"] = 1
        segment_counts["PSL"] = 1
        result = validate_cardinality("EHC_E10", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ehc_e10_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        group_counts["EHC_E10.INVOICE_PROCESSING_RESULTS_INFO"] = 1
        segment_counts["IPR"] = 1
        segment_counts["PYE"] = 1
        segment_counts["IN1"] = 1
        segment_counts["IVC"] = 1
        group_counts["EHC_E10.PRODUCT_SERVICE_SECTION"] = 1
        segment_counts["PSS"] = 1
        group_counts["EHC_E10.PRODUCT_SERVICE_GROUP"] = 1
        segment_counts["PSG"] = 1
        group_counts["EHC_E10.PRODUCT_SERVICE_LINE_INFO"] = 1
        segment_counts["PSL"] = 1
        result = validate_cardinality("EHC_E10", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ehc_e10_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        group_counts["EHC_E10.INVOICE_PROCESSING_RESULTS_INFO"] = 1
        segment_counts["IPR"] = 1
        segment_counts["PYE"] = 1
        segment_counts["IN1"] = 1
        segment_counts["IVC"] = 1
        group_counts["EHC_E10.PRODUCT_SERVICE_SECTION"] = 1
        segment_counts["PSS"] = 1
        group_counts["EHC_E10.PRODUCT_SERVICE_GROUP"] = 1
        segment_counts["PSG"] = 1
        group_counts["EHC_E10.PRODUCT_SERVICE_LINE_INFO"] = 1
        segment_counts["PSL"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("EHC_E10", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestEHCE12Cardinality:

    def test_ehc_e12_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["RFI"] = 1
        segment_counts["IVC"] = 1
        segment_counts["PSS"] = 1
        segment_counts["PSG"] = 1
        group_counts["EHC_E12.REQUEST"] = 1
        segment_counts["OBR"] = 1
        result = validate_cardinality("EHC_E12", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ehc_e12_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["RFI"] = 1
        segment_counts["IVC"] = 1
        segment_counts["PSS"] = 1
        segment_counts["PSG"] = 1
        group_counts["EHC_E12.REQUEST"] = 1
        segment_counts["OBR"] = 1
        result = validate_cardinality("EHC_E12", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ehc_e12_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["RFI"] = 1
        segment_counts["IVC"] = 1
        segment_counts["PSS"] = 1
        segment_counts["PSG"] = 1
        group_counts["EHC_E12.REQUEST"] = 1
        segment_counts["OBR"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("EHC_E12", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestEHCE13Cardinality:

    def test_ehc_e13_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["RFI"] = 1
        segment_counts["IVC"] = 1
        segment_counts["PSS"] = 1
        segment_counts["PSG"] = 1
        group_counts["EHC_E13.REQUEST"] = 1
        segment_counts["OBR"] = 1
        group_counts["EHC_E13.RESPONSE"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("EHC_E13", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ehc_e13_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["RFI"] = 1
        segment_counts["IVC"] = 1
        segment_counts["PSS"] = 1
        segment_counts["PSG"] = 1
        group_counts["EHC_E13.REQUEST"] = 1
        segment_counts["OBR"] = 1
        group_counts["EHC_E13.RESPONSE"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("EHC_E13", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ehc_e13_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["RFI"] = 1
        segment_counts["IVC"] = 1
        segment_counts["PSS"] = 1
        segment_counts["PSG"] = 1
        group_counts["EHC_E13.REQUEST"] = 1
        segment_counts["OBR"] = 1
        group_counts["EHC_E13.RESPONSE"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("EHC_E13", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestEHCE15Cardinality:

    def test_ehc_e15_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["IPR"] = 1
        segment_counts["IVC"] = 1
        group_counts["EHC_E15.PRODUCT_SERVICE_SECTION"] = 1
        segment_counts["PSS"] = 1
        group_counts["EHC_E15.PRODUCT_SERVICE_GROUP"] = 1
        segment_counts["PSG"] = 1
        group_counts["EHC_E15.PSL_ITEM_INFO"] = 1
        segment_counts["PSL"] = 1
        segment_counts["ADJ"] = 1
        segment_counts["PMT"] = 1
        choice_children["EHC_E15.PAYMENT_REMITTANCE_HEADER_INFO"] = ["PMT"]
        result = validate_cardinality("EHC_E15", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ehc_e15_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["IPR"] = 1
        segment_counts["IVC"] = 1
        group_counts["EHC_E15.PRODUCT_SERVICE_SECTION"] = 1
        segment_counts["PSS"] = 1
        group_counts["EHC_E15.PRODUCT_SERVICE_GROUP"] = 1
        segment_counts["PSG"] = 1
        group_counts["EHC_E15.PSL_ITEM_INFO"] = 1
        segment_counts["PSL"] = 1
        segment_counts["ADJ"] = 1
        segment_counts["PMT"] = 1
        choice_children["EHC_E15.PAYMENT_REMITTANCE_HEADER_INFO"] = ["PMT"]
        result = validate_cardinality("EHC_E15", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ehc_e15_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["IPR"] = 1
        segment_counts["IVC"] = 1
        group_counts["EHC_E15.PRODUCT_SERVICE_SECTION"] = 1
        segment_counts["PSS"] = 1
        group_counts["EHC_E15.PRODUCT_SERVICE_GROUP"] = 1
        segment_counts["PSG"] = 1
        group_counts["EHC_E15.PSL_ITEM_INFO"] = 1
        segment_counts["PSL"] = 1
        segment_counts["ADJ"] = 1
        segment_counts["PMT"] = 1
        choice_children["EHC_E15.PAYMENT_REMITTANCE_HEADER_INFO"] = ["PMT"]
        segment_counts["MSH"] = 2
        result = validate_cardinality("EHC_E15", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

    def test_ehc_e15_choice_none_ehc_e15_payment_remittance_header_info(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["IPR"] = 1
        segment_counts["IVC"] = 1
        group_counts["EHC_E15.PRODUCT_SERVICE_SECTION"] = 1
        segment_counts["PSS"] = 1
        group_counts["EHC_E15.PRODUCT_SERVICE_GROUP"] = 1
        segment_counts["PSG"] = 1
        group_counts["EHC_E15.PSL_ITEM_INFO"] = 1
        segment_counts["PSL"] = 1
        segment_counts["ADJ"] = 1
        group_counts["EHC_E15.PAYMENT_REMITTANCE_HEADER_INFO"] = 1
        result = validate_cardinality("EHC_E15", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_NONE" in e.code for e in result.errors)

    def test_ehc_e15_choice_multiple_ehc_e15_payment_remittance_header_info(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["IPR"] = 1
        segment_counts["IVC"] = 1
        group_counts["EHC_E15.PRODUCT_SERVICE_SECTION"] = 1
        segment_counts["PSS"] = 1
        group_counts["EHC_E15.PRODUCT_SERVICE_GROUP"] = 1
        segment_counts["PSG"] = 1
        group_counts["EHC_E15.PSL_ITEM_INFO"] = 1
        segment_counts["PSL"] = 1
        segment_counts["ADJ"] = 1
        segment_counts["PMT"] = 1
        segment_counts["PYE"] = 1
        choice_children["EHC_E15.PAYMENT_REMITTANCE_HEADER_INFO"] = ["PMT", "PYE"]
        result = validate_cardinality("EHC_E15", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_MULTIPLE" in e.code for e in result.errors)

class TestEHCE20Cardinality:

    def test_ehc_e20_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["IVC"] = 1
        choice_children["EHC_E20.AUTHORIZATION_REQUEST"] = ["IVC"]
        result = validate_cardinality("EHC_E20", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ehc_e20_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["IVC"] = 1
        choice_children["EHC_E20.AUTHORIZATION_REQUEST"] = ["IVC"]
        result = validate_cardinality("EHC_E20", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ehc_e20_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["IVC"] = 1
        choice_children["EHC_E20.AUTHORIZATION_REQUEST"] = ["IVC"]
        segment_counts["MSH"] = 2
        result = validate_cardinality("EHC_E20", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

    def test_ehc_e20_choice_none_ehc_e20_authorization_request(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["EHC_E20.AUTHORIZATION_REQUEST"] = 1
        result = validate_cardinality("EHC_E20", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_NONE" in e.code for e in result.errors)

    def test_ehc_e20_choice_multiple_ehc_e20_authorization_request(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["IVC"] = 1
        segment_counts["CTD"] = 1
        choice_children["EHC_E20.AUTHORIZATION_REQUEST"] = ["IVC", "CTD"]
        result = validate_cardinality("EHC_E20", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_MULTIPLE" in e.code for e in result.errors)

class TestEHCE21Cardinality:

    def test_ehc_e21_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["IVC"] = 1
        choice_children["EHC_E21.AUTHORIZATION_REQUEST"] = ["IVC"]
        result = validate_cardinality("EHC_E21", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ehc_e21_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["IVC"] = 1
        choice_children["EHC_E21.AUTHORIZATION_REQUEST"] = ["IVC"]
        result = validate_cardinality("EHC_E21", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ehc_e21_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["IVC"] = 1
        choice_children["EHC_E21.AUTHORIZATION_REQUEST"] = ["IVC"]
        segment_counts["MSH"] = 2
        result = validate_cardinality("EHC_E21", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

    def test_ehc_e21_choice_none_ehc_e21_authorization_request(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["EHC_E21.AUTHORIZATION_REQUEST"] = 1
        result = validate_cardinality("EHC_E21", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_NONE" in e.code for e in result.errors)

    def test_ehc_e21_choice_multiple_ehc_e21_authorization_request(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["IVC"] = 1
        group_counts["EHC_E21.PSL_ITEM_INFO"] = 1
        choice_children["EHC_E21.AUTHORIZATION_REQUEST"] = ["IVC", "EHC_E21.PSL_ITEM_INFO"]
        result = validate_cardinality("EHC_E21", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_MULTIPLE" in e.code for e in result.errors)

class TestEHCE24Cardinality:

    def test_ehc_e24_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["IVC"] = 1
        choice_children["EHC_E24.AUTHORIZATION_RESPONSE_INFO"] = ["IVC"]
        result = validate_cardinality("EHC_E24", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ehc_e24_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["IVC"] = 1
        choice_children["EHC_E24.AUTHORIZATION_RESPONSE_INFO"] = ["IVC"]
        result = validate_cardinality("EHC_E24", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ehc_e24_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["IVC"] = 1
        choice_children["EHC_E24.AUTHORIZATION_RESPONSE_INFO"] = ["IVC"]
        segment_counts["MSH"] = 2
        result = validate_cardinality("EHC_E24", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

    def test_ehc_e24_choice_none_ehc_e24_authorization_response_info(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        group_counts["EHC_E24.AUTHORIZATION_RESPONSE_INFO"] = 1
        result = validate_cardinality("EHC_E24", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_NONE" in e.code for e in result.errors)

    def test_ehc_e24_choice_multiple_ehc_e24_authorization_response_info(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["IVC"] = 1
        group_counts["EHC_E24.PSL_ITEM_INFO"] = 1
        choice_children["EHC_E24.AUTHORIZATION_RESPONSE_INFO"] = ["IVC", "EHC_E24.PSL_ITEM_INFO"]
        result = validate_cardinality("EHC_E24", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_MULTIPLE" in e.code for e in result.errors)

class TestNMDN02Cardinality:

    def test_nmd_n02_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["NMD_N02.CLOCK_AND_STATS_WITH_NOTES"] = 1
        segment_counts["NCK"] = 1
        segment_counts["NST"] = 1
        segment_counts["NSC"] = 1
        result = validate_cardinality("NMD_N02", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_nmd_n02_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        group_counts["NMD_N02.CLOCK_AND_STATS_WITH_NOTES"] = 1
        segment_counts["NCK"] = 1
        segment_counts["NST"] = 1
        segment_counts["NSC"] = 1
        result = validate_cardinality("NMD_N02", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_nmd_n02_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["NMD_N02.CLOCK_AND_STATS_WITH_NOTES"] = 1
        segment_counts["NCK"] = 1
        segment_counts["NST"] = 1
        segment_counts["NSC"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("NMD_N02", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestPEXP07Cardinality:

    def test_pex_p07_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["PEX_P07.EXPERIENCE"] = 1
        segment_counts["PES"] = 1
        group_counts["PEX_P07.PEX_OBSERVATION"] = 1
        segment_counts["PEO"] = 1
        group_counts["PEX_P07.PEX_CAUSE"] = 1
        segment_counts["PCR"] = 1
        segment_counts["RXE"] = 1
        group_counts["PEX_P07.TIMING_QTY"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXA"] = 1
        segment_counts["OBX"] = 1
        segment_counts["NK1"] = 1
        segment_counts["RXE"] = 1
        group_counts["PEX_P07.NK1_TIMING_QTY"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXA"] = 1
        segment_counts["OBX"] = 1
        segment_counts["CSR"] = 1
        result = validate_cardinality("PEX_P07", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_pex_p07_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["PEX_P07.EXPERIENCE"] = 1
        segment_counts["PES"] = 1
        group_counts["PEX_P07.PEX_OBSERVATION"] = 1
        segment_counts["PEO"] = 1
        group_counts["PEX_P07.PEX_CAUSE"] = 1
        segment_counts["PCR"] = 1
        segment_counts["RXE"] = 1
        group_counts["PEX_P07.TIMING_QTY"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXA"] = 1
        segment_counts["OBX"] = 1
        segment_counts["NK1"] = 1
        segment_counts["RXE"] = 1
        group_counts["PEX_P07.NK1_TIMING_QTY"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXA"] = 1
        segment_counts["OBX"] = 1
        segment_counts["CSR"] = 1
        result = validate_cardinality("PEX_P07", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_pex_p07_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["PEX_P07.EXPERIENCE"] = 1
        segment_counts["PES"] = 1
        group_counts["PEX_P07.PEX_OBSERVATION"] = 1
        segment_counts["PEO"] = 1
        group_counts["PEX_P07.PEX_CAUSE"] = 1
        segment_counts["PCR"] = 1
        segment_counts["RXE"] = 1
        group_counts["PEX_P07.TIMING_QTY"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXA"] = 1
        segment_counts["OBX"] = 1
        segment_counts["NK1"] = 1
        segment_counts["RXE"] = 1
        group_counts["PEX_P07.NK1_TIMING_QTY"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXA"] = 1
        segment_counts["OBX"] = 1
        segment_counts["CSR"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("PEX_P07", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRCVO59Cardinality:

    def test_rcv_o59_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["RCV_O59.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["NTE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        group_counts["RCV_O59.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXD"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("RCV_O59", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rcv_o59_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["RCV_O59.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["NTE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        group_counts["RCV_O59.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXD"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("RCV_O59", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rcv_o59_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["RCV_O59.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["NTE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        group_counts["RCV_O59.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXD"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RCV_O59", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRDRRDRCardinality:

    def test_rdr_rdr_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        group_counts["RDR_RDR.DEFINITION"] = 1
        segment_counts["QRD"] = 1
        segment_counts["PID"] = 1
        group_counts["RDR_RDR.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXE"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        group_counts["RDR_RDR.DISPENSE"] = 1
        segment_counts["RXD"] = 1
        segment_counts["RXR"] = 1
        result = validate_cardinality("RDR_RDR", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rdr_rdr_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        group_counts["RDR_RDR.DEFINITION"] = 1
        segment_counts["QRD"] = 1
        segment_counts["PID"] = 1
        group_counts["RDR_RDR.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXE"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        group_counts["RDR_RDR.DISPENSE"] = 1
        segment_counts["RXD"] = 1
        segment_counts["RXR"] = 1
        result = validate_cardinality("RDR_RDR", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rdr_rdr_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        group_counts["RDR_RDR.DEFINITION"] = 1
        segment_counts["QRD"] = 1
        segment_counts["PID"] = 1
        group_counts["RDR_RDR.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXE"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        group_counts["RDR_RDR.DISPENSE"] = 1
        segment_counts["RXD"] = 1
        segment_counts["RXR"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RDR_RDR", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestSDRS31Cardinality:

    def test_sdr_s31_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["SDD"] = 1
        choice_children["SDR_S31.ANTI-MICROBIAL_DEVICE_DATA"] = ["SDD"]
        result = validate_cardinality("SDR_S31", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_sdr_s31_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["SDD"] = 1
        choice_children["SDR_S31.ANTI-MICROBIAL_DEVICE_DATA"] = ["SDD"]
        result = validate_cardinality("SDR_S31", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_sdr_s31_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["SDD"] = 1
        choice_children["SDR_S31.ANTI-MICROBIAL_DEVICE_DATA"] = ["SDD"]
        segment_counts["MSH"] = 2
        result = validate_cardinality("SDR_S31", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

    def test_sdr_s31_choice_none_sdr_s31_anti_microbial_device_data(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["SDR_S31.ANTI-MICROBIAL_DEVICE_DATA"] = 1
        result = validate_cardinality("SDR_S31", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_NONE" in e.code for e in result.errors)

    def test_sdr_s31_choice_multiple_sdr_s31_anti_microbial_device_data(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["SDD"] = 1
        segment_counts["SCD"] = 1
        choice_children["SDR_S31.ANTI-MICROBIAL_DEVICE_DATA"] = ["SDD", "SCD"]
        result = validate_cardinality("SDR_S31", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_MULTIPLE" in e.code for e in result.errors)

class TestSDRS32Cardinality:

    def test_sdr_s32_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["SDD"] = 1
        choice_children["SDR_S32.ANTI-MICROBIAL_DEVICE_CYCLE_DATA"] = ["SDD"]
        result = validate_cardinality("SDR_S32", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_sdr_s32_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["SDD"] = 1
        choice_children["SDR_S32.ANTI-MICROBIAL_DEVICE_CYCLE_DATA"] = ["SDD"]
        result = validate_cardinality("SDR_S32", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_sdr_s32_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["SDD"] = 1
        choice_children["SDR_S32.ANTI-MICROBIAL_DEVICE_CYCLE_DATA"] = ["SDD"]
        segment_counts["MSH"] = 2
        result = validate_cardinality("SDR_S32", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

    def test_sdr_s32_choice_none_sdr_s32_anti_microbial_device_cycle_data(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["SDR_S32.ANTI-MICROBIAL_DEVICE_CYCLE_DATA"] = 1
        result = validate_cardinality("SDR_S32", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_NONE" in e.code for e in result.errors)

    def test_sdr_s32_choice_multiple_sdr_s32_anti_microbial_device_cycle_data(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["SDD"] = 1
        segment_counts["SCD"] = 1
        choice_children["SDR_S32.ANTI-MICROBIAL_DEVICE_CYCLE_DATA"] = ["SDD", "SCD"]
        result = validate_cardinality("SDR_S32", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_MULTIPLE" in e.code for e in result.errors)

class TestSLRS28Cardinality:

    def test_slr_s28_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["SLT"] = 1
        result = validate_cardinality("SLR_S28", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_slr_s28_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["SLT"] = 1
        result = validate_cardinality("SLR_S28", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_slr_s28_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["SLT"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("SLR_S28", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestSTCS33Cardinality:

    def test_stc_s33_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["SCP"] = 1
        result = validate_cardinality("STC_S33", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_stc_s33_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["SCP"] = 1
        result = validate_cardinality("STC_S33", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_stc_s33_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["SCP"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("STC_S33", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestUDMQ05Cardinality:

    def test_udm_q05_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["URD"] = 1
        segment_counts["DSP"] = 1
        result = validate_cardinality("UDM_Q05", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_udm_q05_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["URD"] = 1
        segment_counts["DSP"] = 1
        result = validate_cardinality("UDM_Q05", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_udm_q05_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["URD"] = 1
        segment_counts["DSP"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("UDM_Q05", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)
