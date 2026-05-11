from __future__ import annotations

from zato.hl7v2_rs import validate_cardinality



class TestQBPE03Cardinality:

    def test_qbp_e03_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        choice_children["QBP_E03.QUERY_INFORMATION"] = ["QPD"]
        result = validate_cardinality("QBP_E03", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_qbp_e03_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["QPD"] = 1
        choice_children["QBP_E03.QUERY_INFORMATION"] = ["QPD"]
        result = validate_cardinality("QBP_E03", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_qbp_e03_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        choice_children["QBP_E03.QUERY_INFORMATION"] = ["QPD"]
        segment_counts["MSH"] = 2
        result = validate_cardinality("QBP_E03", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

    def test_qbp_e03_choice_none_qbp_e03_query_information(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["QBP_E03.QUERY_INFORMATION"] = 1
        result = validate_cardinality("QBP_E03", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_NONE" in e.code for e in result.errors)

    def test_qbp_e03_choice_multiple_qbp_e03_query_information(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        choice_children["QBP_E03.QUERY_INFORMATION"] = ["QPD", "RCP"]
        result = validate_cardinality("QBP_E03", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_MULTIPLE" in e.code for e in result.errors)

class TestQBPE22Cardinality:

    def test_qbp_e22_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        choice_children["QBP_E22.QUERY"] = ["QPD"]
        result = validate_cardinality("QBP_E22", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_qbp_e22_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["QPD"] = 1
        choice_children["QBP_E22.QUERY"] = ["QPD"]
        result = validate_cardinality("QBP_E22", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_qbp_e22_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        choice_children["QBP_E22.QUERY"] = ["QPD"]
        segment_counts["MSH"] = 2
        result = validate_cardinality("QBP_E22", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

    def test_qbp_e22_choice_none_qbp_e22_query(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["QBP_E22.QUERY"] = 1
        result = validate_cardinality("QBP_E22", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_NONE" in e.code for e in result.errors)

    def test_qbp_e22_choice_multiple_qbp_e22_query(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        choice_children["QBP_E22.QUERY"] = ["QPD", "RCP"]
        result = validate_cardinality("QBP_E22", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_MULTIPLE" in e.code for e in result.errors)

class TestQBPO33Cardinality:

    def test_qbp_o33_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        result = validate_cardinality("QBP_O33", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_qbp_o33_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        result = validate_cardinality("QBP_O33", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_qbp_o33_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("QBP_O33", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestQBPO34Cardinality:

    def test_qbp_o34_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        result = validate_cardinality("QBP_O34", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_qbp_o34_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        result = validate_cardinality("QBP_O34", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_qbp_o34_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("QBP_O34", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestQBPQ11Cardinality:

    def test_qbp_q11_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        result = validate_cardinality("QBP_Q11", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_qbp_q11_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        result = validate_cardinality("QBP_Q11", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_qbp_q11_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("QBP_Q11", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestQBPQ13Cardinality:

    def test_qbp_q13_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        result = validate_cardinality("QBP_Q13", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_qbp_q13_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        result = validate_cardinality("QBP_Q13", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_qbp_q13_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("QBP_Q13", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestQBPQ15Cardinality:

    def test_qbp_q15_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        result = validate_cardinality("QBP_Q15", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_qbp_q15_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        result = validate_cardinality("QBP_Q15", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_qbp_q15_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("QBP_Q15", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestQBPQ21Cardinality:

    def test_qbp_q21_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        result = validate_cardinality("QBP_Q21", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_qbp_q21_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        result = validate_cardinality("QBP_Q21", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_qbp_q21_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("QBP_Q21", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestQBPQnnCardinality:

    def test_qbp_qnn_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        result = validate_cardinality("QBP_Qnn", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_qbp_qnn_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        result = validate_cardinality("QBP_Qnn", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_qbp_qnn_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("QBP_Qnn", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestQBPZ73Cardinality:

    def test_qbp_z73_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        result = validate_cardinality("QBP_Z73", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_qbp_z73_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        result = validate_cardinality("QBP_Z73", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_qbp_z73_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("QBP_Z73", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestQCNJ01Cardinality:

    def test_qcn_j01_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QID"] = 1
        result = validate_cardinality("QCN_J01", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_qcn_j01_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["QID"] = 1
        result = validate_cardinality("QCN_J01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_qcn_j01_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QID"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("QCN_J01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestQSBQ16Cardinality:

    def test_qsb_q16_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        result = validate_cardinality("QSB_Q16", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_qsb_q16_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        result = validate_cardinality("QSB_Q16", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_qsb_q16_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("QSB_Q16", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestQVRQ17Cardinality:

    def test_qvr_q17_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        result = validate_cardinality("QVR_Q17", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_qvr_q17_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        result = validate_cardinality("QVR_Q17", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_qvr_q17_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("QVR_Q17", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRDYK15Cardinality:

    def test_rdy_k15_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        result = validate_cardinality("RDY_K15", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rdy_k15_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        result = validate_cardinality("RDY_K15", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rdy_k15_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RDY_K15", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRDYZ80Cardinality:

    def test_rdy_z80_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        result = validate_cardinality("RDY_Z80", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rdy_z80_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        result = validate_cardinality("RDY_Z80", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rdy_z80_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RDY_Z80", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRSPE03Cardinality:

    def test_rsp_e03_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        choice_children["RSP_E03.QUERY_ACK_IPR"] = ["QAK"]
        result = validate_cardinality("RSP_E03", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rsp_e03_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        choice_children["RSP_E03.QUERY_ACK_IPR"] = ["QAK"]
        result = validate_cardinality("RSP_E03", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rsp_e03_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        choice_children["RSP_E03.QUERY_ACK_IPR"] = ["QAK"]
        segment_counts["MSH"] = 2
        result = validate_cardinality("RSP_E03", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

    def test_rsp_e03_choice_none_rsp_e03_query_ack_ipr(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        group_counts["RSP_E03.QUERY_ACK_IPR"] = 1
        result = validate_cardinality("RSP_E03", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_NONE" in e.code for e in result.errors)

    def test_rsp_e03_choice_multiple_rsp_e03_query_ack_ipr(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        choice_children["RSP_E03.QUERY_ACK_IPR"] = ["QAK", "QPD"]
        result = validate_cardinality("RSP_E03", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_MULTIPLE" in e.code for e in result.errors)

class TestRSPE22Cardinality:

    def test_rsp_e22_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        choice_children["RSP_E22.QUERY_ACK"] = ["QAK"]
        result = validate_cardinality("RSP_E22", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rsp_e22_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        choice_children["RSP_E22.QUERY_ACK"] = ["QAK"]
        result = validate_cardinality("RSP_E22", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rsp_e22_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        choice_children["RSP_E22.QUERY_ACK"] = ["QAK"]
        segment_counts["MSH"] = 2
        result = validate_cardinality("RSP_E22", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

    def test_rsp_e22_choice_none_rsp_e22_query_ack(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        group_counts["RSP_E22.QUERY_ACK"] = 1
        result = validate_cardinality("RSP_E22", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_NONE" in e.code for e in result.errors)

    def test_rsp_e22_choice_multiple_rsp_e22_query_ack(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        choice_children["RSP_E22.QUERY_ACK"] = ["QAK", "QPD"]
        result = validate_cardinality("RSP_E22", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_MULTIPLE" in e.code for e in result.errors)

class TestRSPK11Cardinality:

    def test_rsp_k11_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["anyHL7Segment"] = 1
        result = validate_cardinality("RSP_K11", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rsp_k11_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["anyHL7Segment"] = 1
        result = validate_cardinality("RSP_K11", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rsp_k11_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["anyHL7Segment"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RSP_K11", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRSPK21Cardinality:

    def test_rsp_k21_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["PID"] = 1
        segment_counts["QRI"] = 1
        result = validate_cardinality("RSP_K21", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rsp_k21_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["PID"] = 1
        segment_counts["QRI"] = 1
        result = validate_cardinality("RSP_K21", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rsp_k21_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["PID"] = 1
        segment_counts["QRI"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RSP_K21", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRSPK22Cardinality:

    def test_rsp_k22_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["PID"] = 1
        result = validate_cardinality("RSP_K22", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rsp_k22_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["PID"] = 1
        result = validate_cardinality("RSP_K22", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rsp_k22_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["PID"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RSP_K22", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRSPK23Cardinality:

    def test_rsp_k23_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["PID"] = 1
        result = validate_cardinality("RSP_K23", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rsp_k23_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["PID"] = 1
        result = validate_cardinality("RSP_K23", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rsp_k23_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["PID"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RSP_K23", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRSPK25Cardinality:

    def test_rsp_k25_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        group_counts["RSP_K25.STAFF"] = 1
        segment_counts["STF"] = 1
        result = validate_cardinality("RSP_K25", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rsp_k25_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        group_counts["RSP_K25.STAFF"] = 1
        segment_counts["STF"] = 1
        result = validate_cardinality("RSP_K25", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rsp_k25_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        group_counts["RSP_K25.STAFF"] = 1
        segment_counts["STF"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RSP_K25", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRSPK31Cardinality:

    def test_rsp_k31_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        group_counts["RSP_K31.RESPONSE"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["RSP_K31.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        group_counts["RSP_K31.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXD"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("RSP_K31", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rsp_k31_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        group_counts["RSP_K31.RESPONSE"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["RSP_K31.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        group_counts["RSP_K31.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXD"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("RSP_K31", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rsp_k31_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        group_counts["RSP_K31.RESPONSE"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["RSP_K31.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        group_counts["RSP_K31.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXD"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RSP_K31", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRSPK32Cardinality:

    def test_rsp_k32_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        result = validate_cardinality("RSP_K32", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rsp_k32_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        result = validate_cardinality("RSP_K32", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rsp_k32_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RSP_K32", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRSPO33Cardinality:

    def test_rsp_o33_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["PID"] = 1
        result = validate_cardinality("RSP_O33", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rsp_o33_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["PID"] = 1
        result = validate_cardinality("RSP_O33", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rsp_o33_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["PID"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RSP_O33", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRSPO34Cardinality:

    def test_rsp_o34_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        segment_counts["DON"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("RSP_O34", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rsp_o34_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        segment_counts["DON"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("RSP_O34", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rsp_o34_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        segment_counts["DON"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RSP_O34", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRSPZ82Cardinality:

    def test_rsp_z82_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        group_counts["RSP_Z82.QUERY_RESPONSE"] = 1
        segment_counts["PID"] = 1
        segment_counts["AL1"] = 1
        segment_counts["PV1"] = 1
        group_counts["RSP_Z82.COMMON_ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXD"] = 1
        segment_counts["RXR"] = 1
        group_counts["RSP_Z82.OBSERVATION"] = 1
        result = validate_cardinality("RSP_Z82", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rsp_z82_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        group_counts["RSP_Z82.QUERY_RESPONSE"] = 1
        segment_counts["PID"] = 1
        segment_counts["AL1"] = 1
        segment_counts["PV1"] = 1
        group_counts["RSP_Z82.COMMON_ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXD"] = 1
        segment_counts["RXR"] = 1
        group_counts["RSP_Z82.OBSERVATION"] = 1
        result = validate_cardinality("RSP_Z82", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rsp_z82_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        group_counts["RSP_Z82.QUERY_RESPONSE"] = 1
        segment_counts["PID"] = 1
        segment_counts["AL1"] = 1
        segment_counts["PV1"] = 1
        group_counts["RSP_Z82.COMMON_ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXD"] = 1
        segment_counts["RXR"] = 1
        group_counts["RSP_Z82.OBSERVATION"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RSP_Z82", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRSPZ84Cardinality:

    def test_rsp_z84_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RDF"] = 1
        result = validate_cardinality("RSP_Z84", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rsp_z84_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RDF"] = 1
        result = validate_cardinality("RSP_Z84", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rsp_z84_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RDF"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RSP_Z84", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRSPZ86Cardinality:

    def test_rsp_z86_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        group_counts["RSP_Z86.QUERY_RESPONSE"] = 1
        segment_counts["PID"] = 1
        group_counts["RSP_Z86.COMMON_ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXE"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXD"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXG"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        group_counts["RSP_Z86.OBSERVATION"] = 1
        result = validate_cardinality("RSP_Z86", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rsp_z86_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        group_counts["RSP_Z86.QUERY_RESPONSE"] = 1
        segment_counts["PID"] = 1
        group_counts["RSP_Z86.COMMON_ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXE"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXD"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXG"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        group_counts["RSP_Z86.OBSERVATION"] = 1
        result = validate_cardinality("RSP_Z86", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rsp_z86_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        group_counts["RSP_Z86.QUERY_RESPONSE"] = 1
        segment_counts["PID"] = 1
        group_counts["RSP_Z86.COMMON_ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXE"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXD"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXG"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        group_counts["RSP_Z86.OBSERVATION"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RSP_Z86", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRSPZ88Cardinality:

    def test_rsp_z88_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        group_counts["RSP_Z88.QUERY_RESPONSE"] = 1
        segment_counts["PID"] = 1
        segment_counts["AL1"] = 1
        segment_counts["PV1"] = 1
        group_counts["RSP_Z88.COMMON_ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXD"] = 1
        segment_counts["RXR"] = 1
        group_counts["RSP_Z88.OBSERVATION"] = 1
        segment_counts["DSC"] = 1
        result = validate_cardinality("RSP_Z88", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rsp_z88_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        group_counts["RSP_Z88.QUERY_RESPONSE"] = 1
        segment_counts["PID"] = 1
        segment_counts["AL1"] = 1
        segment_counts["PV1"] = 1
        group_counts["RSP_Z88.COMMON_ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXD"] = 1
        segment_counts["RXR"] = 1
        group_counts["RSP_Z88.OBSERVATION"] = 1
        segment_counts["DSC"] = 1
        result = validate_cardinality("RSP_Z88", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rsp_z88_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        group_counts["RSP_Z88.QUERY_RESPONSE"] = 1
        segment_counts["PID"] = 1
        segment_counts["AL1"] = 1
        segment_counts["PV1"] = 1
        group_counts["RSP_Z88.COMMON_ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXD"] = 1
        segment_counts["RXR"] = 1
        group_counts["RSP_Z88.OBSERVATION"] = 1
        segment_counts["DSC"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RSP_Z88", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRSPZ90Cardinality:

    def test_rsp_z90_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        group_counts["RSP_Z90.QUERY_RESPONSE"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["RSP_Z90.COMMON_ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        group_counts["RSP_Z90.OBSERVATION"] = 1
        segment_counts["SPM"] = 1
        segment_counts["DSC"] = 1
        result = validate_cardinality("RSP_Z90", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rsp_z90_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        group_counts["RSP_Z90.QUERY_RESPONSE"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["RSP_Z90.COMMON_ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        group_counts["RSP_Z90.OBSERVATION"] = 1
        segment_counts["SPM"] = 1
        segment_counts["DSC"] = 1
        result = validate_cardinality("RSP_Z90", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rsp_z90_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RCP"] = 1
        group_counts["RSP_Z90.QUERY_RESPONSE"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["RSP_Z90.COMMON_ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        group_counts["RSP_Z90.OBSERVATION"] = 1
        segment_counts["SPM"] = 1
        segment_counts["DSC"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RSP_Z90", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRSPZnnCardinality:

    def test_rsp_znn_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        result = validate_cardinality("RSP_Znn", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rsp_znn_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        result = validate_cardinality("RSP_Znn", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rsp_znn_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RSP_Znn", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRTBK13Cardinality:

    def test_rtb_k13_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RDF"] = 1
        result = validate_cardinality("RTB_K13", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rtb_k13_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RDF"] = 1
        result = validate_cardinality("RTB_K13", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rtb_k13_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RDF"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RTB_K13", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRTBKnnCardinality:

    def test_rtb_knn_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["anyHL7Segment"] = 1
        result = validate_cardinality("RTB_Knn", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rtb_knn_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["anyHL7Segment"] = 1
        result = validate_cardinality("RTB_Knn", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rtb_knn_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["anyHL7Segment"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RTB_Knn", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRTBZ74Cardinality:

    def test_rtb_z74_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RDF"] = 1
        result = validate_cardinality("RTB_Z74", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rtb_z74_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RDF"] = 1
        result = validate_cardinality("RTB_Z74", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rtb_z74_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["QAK"] = 1
        segment_counts["QPD"] = 1
        segment_counts["RDF"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RTB_Z74", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)
