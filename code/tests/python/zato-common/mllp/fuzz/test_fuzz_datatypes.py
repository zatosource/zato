from __future__ import annotations

from hypothesis import given, strategies as st, settings, HealthCheck

from zato.hl7v2_rs import validate_datatype


hl7_safe_text = st.text(
    alphabet=st.characters(
        blacklist_categories=("Cs",),
        blacklist_characters="\r\n|^~\\&"
    ),
    min_size=0,
    max_size=100
)


def make_components(num_components: int, values: list[str]) -> list[list[str]]:
    result = []
    for i in range(num_components):
        if i < len(values):
            result.append([values[i]])
        else:
            result.append([""])
    return result


class TestFuzzAD:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_ad_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("AD", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_ad_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("AD", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzAUI:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_aui_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("AUI", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_aui_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("AUI", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzCCD:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_ccd_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("CCD", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_ccd_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("CCD", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzCCP:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_ccp_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("CCP", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_ccp_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("CCP", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzCD:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_cd_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("CD", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_cd_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("CD", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzCF:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_cf_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("CF", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_cf_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("CF", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzCNE:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_cne_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("CNE", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_cne_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("CNE", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzCNN:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_cnn_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("CNN", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_cnn_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("CNN", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzCP:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_cp_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("CP", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_cp_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("CP", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzCQ:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_cq_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("CQ", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_cq_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("CQ", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzCSU:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_csu_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("CSU", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_csu_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("CSU", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzCWE:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_cwe_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("CWE", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_cwe_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("CWE", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzCX:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_cx_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("CX", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_cx_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("CX", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzDDI:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_ddi_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("DDI", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_ddi_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("DDI", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzDIN:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_din_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("DIN", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_din_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("DIN", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzDLD:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_dld_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("DLD", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_dld_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("DLD", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzDLN:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_dln_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("DLN", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_dln_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("DLN", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzDLT:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_dlt_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("DLT", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_dlt_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("DLT", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzDR:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_dr_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("DR", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_dr_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("DR", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzDT:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_dt_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("DT", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_dt_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("DT", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzDTM:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_dtm_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("DTM", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_dtm_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("DTM", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzDTN:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_dtn_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("DTN", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_dtn_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("DTN", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzED:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_ed_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("ED", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_ed_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("ED", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzEI:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_ei_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("EI", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_ei_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("EI", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzEIP:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_eip_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("EIP", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_eip_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("EIP", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzERL:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_erl_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("ERL", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_erl_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("ERL", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzFC:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_fc_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("FC", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_fc_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("FC", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzFN:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_fn_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("FN", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_fn_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("FN", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzFT:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_ft_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("FT", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_ft_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("FT", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzGTS:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_gts_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("GTS", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_gts_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("GTS", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzHD:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_hd_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("HD", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_hd_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("HD", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzICD:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_icd_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("ICD", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_icd_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("ICD", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzID:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_id_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("ID", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_id_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("ID", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzIS:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_is_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("IS", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_is_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("IS", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzJCC:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_jcc_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("JCC", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_jcc_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("JCC", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzMA:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_ma_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("MA", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_ma_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("MA", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzMO:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_mo_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("MO", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_mo_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("MO", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzMOC:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_moc_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("MOC", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_moc_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("MOC", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzMOP:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_mop_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("MOP", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_mop_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("MOP", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzMSG:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_msg_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("MSG", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_msg_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("MSG", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzNA:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_na_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("NA", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_na_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("NA", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzNDL:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_ndl_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("NDL", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_ndl_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("NDL", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzNM:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_nm_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("NM", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_nm_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("NM", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzNR:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_nr_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("NR", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_nr_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("NR", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzOCD:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_ocd_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("OCD", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_ocd_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("OCD", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzOG:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_og_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("OG", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_og_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("OG", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzOSP:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_osp_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("OSP", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_osp_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("OSP", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzPIP:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_pip_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("PIP", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_pip_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("PIP", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzPL:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_pl_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("PL", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_pl_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("PL", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzPLN:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_pln_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("PLN", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_pln_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("PLN", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzPPN:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_ppn_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("PPN", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_ppn_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("PPN", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzPRL:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_prl_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("PRL", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_prl_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("PRL", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzPT:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_pt_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("PT", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_pt_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("PT", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzPTA:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_pta_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("PTA", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_pta_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("PTA", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzQIP:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_qip_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("QIP", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_qip_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("QIP", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzQSC:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_qsc_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("QSC", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_qsc_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("QSC", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzRCD:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_rcd_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("RCD", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_rcd_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("RCD", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzRFR:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_rfr_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("RFR", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_rfr_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("RFR", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzRI:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_ri_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("RI", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_ri_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("RI", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzRMC:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_rmc_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("RMC", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_rmc_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("RMC", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzRP:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_rp_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("RP", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_rp_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("RP", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzRPT:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_rpt_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("RPT", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_rpt_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("RPT", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzSAD:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_sad_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("SAD", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_sad_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("SAD", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzSCV:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_scv_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("SCV", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_scv_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("SCV", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzSI:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_si_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("SI", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_si_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("SI", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzSN:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_sn_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("SN", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_sn_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("SN", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzSNM:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_snm_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("SNM", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_snm_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("SNM", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzSPD:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_spd_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("SPD", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_spd_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("SPD", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzSRT:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_srt_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("SRT", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_srt_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("SRT", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzST:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_st_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("ST", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_st_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("ST", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzTM:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_tm_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("TM", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_tm_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("TM", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzTX:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_tx_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("TX", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_tx_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("TX", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzUVC:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_uvc_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("UVC", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_uvc_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("UVC", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzVH:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_vh_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("VH", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_vh_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("VH", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzVID:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_vid_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("VID", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_vid_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("VID", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzVR:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_vr_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("VR", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_vr_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("VR", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzWVI:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_wvi_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("WVI", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_wvi_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("WVI", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzWVS:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_wvs_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("WVS", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_wvs_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("WVS", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzXAD:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_xad_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("XAD", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_xad_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("XAD", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzXCN:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_xcn_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("XCN", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_xcn_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("XCN", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzXON:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_xon_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("XON", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_xon_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("XON", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzXPN:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_xpn_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("XPN", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_xpn_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("XPN", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzXTN:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_xtn_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("XTN", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_xtn_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("XTN", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")


class TestFuzzvaries:

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_varies_no_crash(self, values):
        components = make_components(20, values)
        result = validate_datatype("varies", components, "TEST.1")
        assert result is not None

    @given(st.lists(hl7_safe_text, min_size=1, max_size=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_varies_result_has_attributes(self, values):
        components = make_components(20, values)
        result = validate_datatype("varies", components, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")

