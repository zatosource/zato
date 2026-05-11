from __future__ import annotations

from typing import Optional

from zato.hl7v2.base import HL7DataType, HL7Component
from zato.hl7v2.v2_9.primitives import (
    ST,
)

class AD(HL7DataType):
    ad_1: Optional[ST] = HL7Component(position=1)
    ad_2: Optional[ST] = HL7Component(position=2)
    ad_3: Optional[ST] = HL7Component(position=3)
    ad_4: Optional[ST] = HL7Component(position=4)
    ad_5: Optional[ST] = HL7Component(position=5)
    ad_6: Optional[ST] = HL7Component(position=6)
    ad_7: Optional[ST] = HL7Component(position=7)
    ad_8: Optional[ST] = HL7Component(position=8)
    street_address = ad_1
    other_designation = ad_2
    city = ad_3
    state_or_province = ad_4
    zip_or_postal_code = ad_5
    country = ad_6
    address_type = ad_7
    other_geographic_designation = ad_8

class AUI(HL7DataType):
    aui_1: Optional[ST] = HL7Component(position=1)
    aui_2: Optional[ST] = HL7Component(position=2)
    aui_3: Optional[ST] = HL7Component(position=3)
    authorization_number = aui_1
    date = aui_2
    source = aui_3

class CCD(HL7DataType):
    ccd_1: Optional[ST] = HL7Component(position=1)
    ccd_2: Optional[ST] = HL7Component(position=2)
    invocation_event = ccd_1
    datetime = ccd_2

class CCP(HL7DataType):
    ccp_1: Optional[ST] = HL7Component(position=1)
    ccp_2: Optional[ST] = HL7Component(position=2)
    ccp_3: Optional[ST] = HL7Component(position=3)
    channel_calibration_sensitivity_correction_factor = ccp_1
    channel_calibration_baseline = ccp_2
    channel_calibration_time_skew = ccp_3

class CD(HL7DataType):
    cd_1: Optional[ST] = HL7Component(position=1)
    cd_2: Optional[ST] = HL7Component(position=2)
    cd_3: Optional[ST] = HL7Component(position=3)
    cd_4: Optional[ST] = HL7Component(position=4)
    cd_5: Optional[ST] = HL7Component(position=5)
    cd_6: Optional[ST] = HL7Component(position=6)
    channel_identifier = cd_1
    waveform_source = cd_2
    channel_sensitivity_and_units = cd_3
    channel_calibration_parameters = cd_4
    channel_sampling_frequency = cd_5
    minimum_and_maximum_data_values = cd_6

class CF(HL7DataType):
    cf_1: Optional[ST] = HL7Component(position=1)
    cf_2: Optional[ST] = HL7Component(position=2)
    cf_3: Optional[ST] = HL7Component(position=3)
    cf_4: Optional[ST] = HL7Component(position=4)
    cf_5: Optional[ST] = HL7Component(position=5)
    cf_6: Optional[ST] = HL7Component(position=6)
    cf_7: Optional[ST] = HL7Component(position=7)
    cf_8: Optional[ST] = HL7Component(position=8)
    cf_9: Optional[ST] = HL7Component(position=9)
    cf_10: Optional[ST] = HL7Component(position=10)
    cf_11: Optional[ST] = HL7Component(position=11)
    cf_12: Optional[ST] = HL7Component(position=12)
    cf_13: Optional[ST] = HL7Component(position=13)
    cf_14: Optional[ST] = HL7Component(position=14)
    cf_15: Optional[ST] = HL7Component(position=15)
    cf_16: Optional[ST] = HL7Component(position=16)
    cf_17: Optional[ST] = HL7Component(position=17)
    cf_18: Optional[ST] = HL7Component(position=18)
    cf_19: Optional[ST] = HL7Component(position=19)
    cf_20: Optional[ST] = HL7Component(position=20)
    cf_21: Optional[ST] = HL7Component(position=21)
    cf_22: Optional[ST] = HL7Component(position=22)
    identifier = cf_1
    formatted_text = cf_2
    name_of_coding_system = cf_3
    alternate_identifier = cf_4
    alternate_formatted_text = cf_5
    name_of_alternate_coding_system = cf_6
    coding_system_version_id = cf_7
    alternate_coding_system_version_id = cf_8
    original_text = cf_9
    second_alternate_identifier = cf_10
    second_alternate_formatted_text = cf_11
    name_of_second_alternate_coding_system = cf_12
    second_alternate_coding_system_version_id = cf_13
    coding_system_oid = cf_14
    value_set_oid = cf_15
    value_set_version_id = cf_16
    alternate_coding_system_oid = cf_17
    alternate_value_set_oid = cf_18
    alternate_value_set_version_id = cf_19
    second_alternate_coding_system_oid = cf_20
    second_alternate_value_set_oid = cf_21
    second_alternate_value_set_version_id = cf_22

class CNE(HL7DataType):
    cne_1: Optional[ST] = HL7Component(position=1)
    cne_2: Optional[ST] = HL7Component(position=2)
    cne_3: Optional[ST] = HL7Component(position=3)
    cne_4: Optional[ST] = HL7Component(position=4)
    cne_5: Optional[ST] = HL7Component(position=5)
    cne_6: Optional[ST] = HL7Component(position=6)
    cne_7: Optional[ST] = HL7Component(position=7)
    cne_8: Optional[ST] = HL7Component(position=8)
    cne_9: Optional[ST] = HL7Component(position=9)
    cne_10: Optional[ST] = HL7Component(position=10)
    cne_11: Optional[ST] = HL7Component(position=11)
    cne_12: Optional[ST] = HL7Component(position=12)
    cne_13: Optional[ST] = HL7Component(position=13)
    cne_14: Optional[ST] = HL7Component(position=14)
    cne_15: Optional[ST] = HL7Component(position=15)
    cne_16: Optional[ST] = HL7Component(position=16)
    cne_17: Optional[ST] = HL7Component(position=17)
    cne_18: Optional[ST] = HL7Component(position=18)
    cne_19: Optional[ST] = HL7Component(position=19)
    cne_20: Optional[ST] = HL7Component(position=20)
    cne_21: Optional[ST] = HL7Component(position=21)
    cne_22: Optional[ST] = HL7Component(position=22)
    identifier = cne_1
    text = cne_2
    name_of_coding_system = cne_3
    alternate_identifier = cne_4
    alternate_text = cne_5
    name_of_alternate_coding_system = cne_6
    coding_system_version_id = cne_7
    alternate_coding_system_version_id = cne_8
    original_text = cne_9
    second_alternate_identifier = cne_10
    second_alternate_text = cne_11
    name_of_second_alternate_coding_system = cne_12
    second_alternate_coding_system_version_id = cne_13
    coding_system_oid = cne_14
    value_set_oid = cne_15
    value_set_version_id = cne_16
    alternate_coding_system_oid = cne_17
    alternate_value_set_oid = cne_18
    alternate_value_set_version_id = cne_19
    second_alternate_coding_system_oid = cne_20
    second_alternate_value_set_oid = cne_21
    second_alternate_value_set_version_id = cne_22

class CNN(HL7DataType):
    cnn_1: Optional[ST] = HL7Component(position=1)
    cnn_2: Optional[ST] = HL7Component(position=2)
    cnn_3: Optional[ST] = HL7Component(position=3)
    cnn_4: Optional[ST] = HL7Component(position=4)
    cnn_5: Optional[ST] = HL7Component(position=5)
    cnn_6: Optional[ST] = HL7Component(position=6)
    cnn_7: Optional[ST] = HL7Component(position=7)
    cnn_8: Optional[ST] = HL7Component(position=8)
    cnn_9: Optional[ST] = HL7Component(position=9)
    cnn_10: Optional[ST] = HL7Component(position=10)
    cnn_11: Optional[ST] = HL7Component(position=11)
    id_number = cnn_1
    family_name = cnn_2
    given_name = cnn_3
    second_and_further_given_names_or_initials_thereof = cnn_4
    suffix = cnn_5
    prefix = cnn_6
    degree = cnn_7
    source_table = cnn_8
    assigning_authority_namespace_id = cnn_9
    assigning_authority_universal_id = cnn_10
    assigning_authority_universal_id_type = cnn_11

class CP(HL7DataType):
    cp_1: Optional[ST] = HL7Component(position=1)
    cp_2: Optional[ST] = HL7Component(position=2)
    cp_3: Optional[ST] = HL7Component(position=3)
    cp_4: Optional[ST] = HL7Component(position=4)
    cp_5: Optional[ST] = HL7Component(position=5)
    cp_6: Optional[ST] = HL7Component(position=6)
    price = cp_1
    price_type = cp_2
    from_value = cp_3
    to_value = cp_4
    range_units = cp_5
    range_type = cp_6

class CQ(HL7DataType):
    cq_1: Optional[ST] = HL7Component(position=1)
    cq_2: Optional[ST] = HL7Component(position=2)
    quantity = cq_1
    units = cq_2

class CSU(HL7DataType):
    csu_1: Optional[ST] = HL7Component(position=1)
    csu_2: Optional[ST] = HL7Component(position=2)
    csu_3: Optional[ST] = HL7Component(position=3)
    csu_4: Optional[ST] = HL7Component(position=4)
    csu_5: Optional[ST] = HL7Component(position=5)
    csu_6: Optional[ST] = HL7Component(position=6)
    csu_7: Optional[ST] = HL7Component(position=7)
    csu_8: Optional[ST] = HL7Component(position=8)
    csu_9: Optional[ST] = HL7Component(position=9)
    csu_10: Optional[ST] = HL7Component(position=10)
    csu_11: Optional[ST] = HL7Component(position=11)
    csu_12: Optional[ST] = HL7Component(position=12)
    csu_13: Optional[ST] = HL7Component(position=13)
    csu_14: Optional[ST] = HL7Component(position=14)
    csu_15: Optional[ST] = HL7Component(position=15)
    csu_16: Optional[ST] = HL7Component(position=16)
    csu_17: Optional[ST] = HL7Component(position=17)
    csu_18: Optional[ST] = HL7Component(position=18)
    csu_19: Optional[ST] = HL7Component(position=19)
    csu_20: Optional[ST] = HL7Component(position=20)
    csu_21: Optional[ST] = HL7Component(position=21)
    csu_22: Optional[ST] = HL7Component(position=22)
    csu_23: Optional[ST] = HL7Component(position=23)
    channel_sensitivity = csu_1
    unit_of_measure_identifier = csu_2
    unit_of_measure_description = csu_3
    unit_of_measure_coding_system = csu_4
    alternate_unit_of_measure_identifier = csu_5
    alternate_unit_of_measure_description = csu_6
    alternate_unit_of_measure_coding_system = csu_7
    unit_of_measure_coding_system_version_id = csu_8
    alternate_unit_of_measure_coding_system_version_id = csu_9
    original_text = csu_10
    second_alternate_unit_of_measure_identifier = csu_11
    second_alternate_unit_of_measure_text = csu_12
    name_of_second_alternate_unit_of_measure_coding_system = csu_13
    second_alternate_unit_of_measure_coding_system_version_id = csu_14
    unit_of_measure_coding_system_oid = csu_15
    unit_of_measure_value_set_oid = csu_16
    unit_of_measure_value_set_version_id = csu_17
    alternate_unit_of_measure_coding_system_oid = csu_18
    alternate_unit_of_measure_value_set_oid = csu_19
    alternate_unit_of_measure_value_set_version_id = csu_20
    alternate_unit_of_measure_coding_system_oid = csu_21
    alternate_unit_of_measure_value_set_oid = csu_22
    alternate_unit_of_measure_value_set_version_id = csu_23

class CWE(HL7DataType):
    cwe_1: Optional[ST] = HL7Component(position=1)
    cwe_2: Optional[ST] = HL7Component(position=2)
    cwe_3: Optional[ST] = HL7Component(position=3)
    cwe_4: Optional[ST] = HL7Component(position=4)
    cwe_5: Optional[ST] = HL7Component(position=5)
    cwe_6: Optional[ST] = HL7Component(position=6)
    cwe_7: Optional[ST] = HL7Component(position=7)
    cwe_8: Optional[ST] = HL7Component(position=8)
    cwe_9: Optional[ST] = HL7Component(position=9)
    cwe_10: Optional[ST] = HL7Component(position=10)
    cwe_11: Optional[ST] = HL7Component(position=11)
    cwe_12: Optional[ST] = HL7Component(position=12)
    cwe_13: Optional[ST] = HL7Component(position=13)
    cwe_14: Optional[ST] = HL7Component(position=14)
    cwe_15: Optional[ST] = HL7Component(position=15)
    cwe_16: Optional[ST] = HL7Component(position=16)
    cwe_17: Optional[ST] = HL7Component(position=17)
    cwe_18: Optional[ST] = HL7Component(position=18)
    cwe_19: Optional[ST] = HL7Component(position=19)
    cwe_20: Optional[ST] = HL7Component(position=20)
    cwe_21: Optional[ST] = HL7Component(position=21)
    cwe_22: Optional[ST] = HL7Component(position=22)
    identifier = cwe_1
    text = cwe_2
    name_of_coding_system = cwe_3
    alternate_identifier = cwe_4
    alternate_text = cwe_5
    name_of_alternate_coding_system = cwe_6
    coding_system_version_id = cwe_7
    alternate_coding_system_version_id = cwe_8
    original_text = cwe_9
    second_alternate_identifier = cwe_10
    second_alternate_text = cwe_11
    name_of_second_alternate_coding_system = cwe_12
    second_alternate_coding_system_version_id = cwe_13
    coding_system_oid = cwe_14
    value_set_oid = cwe_15
    value_set_version_id = cwe_16
    alternate_coding_system_oid = cwe_17
    alternate_value_set_oid = cwe_18
    alternate_value_set_version_id = cwe_19
    second_alternate_coding_system_oid = cwe_20
    second_alternate_value_set_oid = cwe_21
    second_alternate_value_set_version_id = cwe_22

class CX(HL7DataType):
    cx_1: Optional[ST] = HL7Component(position=1)
    cx_2: Optional[ST] = HL7Component(position=2)
    cx_3: Optional[ST] = HL7Component(position=3)
    cx_4: Optional[ST] = HL7Component(position=4)
    cx_5: Optional[ST] = HL7Component(position=5)
    cx_6: Optional[ST] = HL7Component(position=6)
    cx_7: Optional[ST] = HL7Component(position=7)
    cx_8: Optional[ST] = HL7Component(position=8)
    cx_9: Optional[ST] = HL7Component(position=9)
    cx_10: Optional[ST] = HL7Component(position=10)
    cx_11: Optional[ST] = HL7Component(position=11)
    cx_12: Optional[ST] = HL7Component(position=12)
    id_number = cx_1
    identifier_check_digit = cx_2
    check_digit_scheme = cx_3
    assigning_authority = cx_4
    identifier_type_code = cx_5
    assigning_facility = cx_6
    effective_date = cx_7
    expiration_date = cx_8
    assigning_jurisdiction = cx_9
    assigning_agency_or_department = cx_10
    security_check = cx_11
    security_check_scheme = cx_12

class DDI(HL7DataType):
    ddi_1: Optional[ST] = HL7Component(position=1)
    ddi_2: Optional[ST] = HL7Component(position=2)
    ddi_3: Optional[ST] = HL7Component(position=3)
    delay_days = ddi_1
    monetary_amount = ddi_2
    number_of_days = ddi_3

class DIN(HL7DataType):
    din_1: Optional[ST] = HL7Component(position=1)
    din_2: Optional[ST] = HL7Component(position=2)
    date = din_1
    institution_name = din_2

class DLD(HL7DataType):
    dld_1: Optional[ST] = HL7Component(position=1)
    dld_2: Optional[ST] = HL7Component(position=2)
    discharge_to_location = dld_1
    effective_date = dld_2

class DLN(HL7DataType):
    dln_1: Optional[ST] = HL7Component(position=1)
    dln_2: Optional[ST] = HL7Component(position=2)
    dln_3: Optional[ST] = HL7Component(position=3)
    drivers_license_number = dln_1
    issuing_state_province_country = dln_2
    expiration_date = dln_3

class DLT(HL7DataType):
    dlt_1: Optional[ST] = HL7Component(position=1)
    dlt_2: Optional[ST] = HL7Component(position=2)
    dlt_3: Optional[ST] = HL7Component(position=3)
    dlt_4: Optional[ST] = HL7Component(position=4)
    normal_range = dlt_1
    numeric_threshold = dlt_2
    change_computation = dlt_3
    days_retained = dlt_4

class DR(HL7DataType):
    dr_1: Optional[ST] = HL7Component(position=1)
    dr_2: Optional[ST] = HL7Component(position=2)
    range_start_date_time = dr_1
    range_end_date_time = dr_2

class DTN(HL7DataType):
    dtn_1: Optional[ST] = HL7Component(position=1)
    dtn_2: Optional[ST] = HL7Component(position=2)
    day_type = dtn_1
    number_of_days = dtn_2

class ED(HL7DataType):
    ed_1: Optional[ST] = HL7Component(position=1)
    ed_2: Optional[ST] = HL7Component(position=2)
    ed_3: Optional[ST] = HL7Component(position=3)
    ed_4: Optional[ST] = HL7Component(position=4)
    ed_5: Optional[ST] = HL7Component(position=5)
    source_application = ed_1
    type_of_data = ed_2
    data_subtype = ed_3
    encoding = ed_4
    data = ed_5

class EI(HL7DataType):
    ei_1: Optional[ST] = HL7Component(position=1)
    ei_2: Optional[ST] = HL7Component(position=2)
    ei_3: Optional[ST] = HL7Component(position=3)
    ei_4: Optional[ST] = HL7Component(position=4)
    entity_identifier = ei_1
    namespace_id = ei_2
    universal_id = ei_3
    universal_id_type = ei_4

class EIP(HL7DataType):
    eip_1: Optional[ST] = HL7Component(position=1)
    eip_2: Optional[ST] = HL7Component(position=2)
    placer_assigned_identifier = eip_1
    filler_assigned_identifier = eip_2

class ERL(HL7DataType):
    erl_1: Optional[ST] = HL7Component(position=1)
    erl_2: Optional[ST] = HL7Component(position=2)
    erl_3: Optional[ST] = HL7Component(position=3)
    erl_4: Optional[ST] = HL7Component(position=4)
    erl_5: Optional[ST] = HL7Component(position=5)
    erl_6: Optional[ST] = HL7Component(position=6)
    segment_id = erl_1
    segment_sequence = erl_2
    field_position = erl_3
    field_repetition = erl_4
    component_number = erl_5
    sub_component_number = erl_6

class FC(HL7DataType):
    fc_1: Optional[ST] = HL7Component(position=1)
    fc_2: Optional[ST] = HL7Component(position=2)
    financial_class_code = fc_1
    effective_date = fc_2

class FN(HL7DataType):
    fn_1: Optional[ST] = HL7Component(position=1)
    fn_2: Optional[ST] = HL7Component(position=2)
    fn_3: Optional[ST] = HL7Component(position=3)
    fn_4: Optional[ST] = HL7Component(position=4)
    fn_5: Optional[ST] = HL7Component(position=5)
    surname = fn_1
    own_surname_prefix = fn_2
    own_surname = fn_3
    surname_prefix_from_partner_spouse = fn_4
    surname_from_partner_spouse = fn_5

class HD(HL7DataType):
    hd_1: Optional[ST] = HL7Component(position=1)
    hd_2: Optional[ST] = HL7Component(position=2)
    hd_3: Optional[ST] = HL7Component(position=3)
    namespace_id = hd_1
    universal_id = hd_2
    universal_id_type = hd_3

class ICD(HL7DataType):
    icd_1: Optional[ST] = HL7Component(position=1)
    icd_2: Optional[ST] = HL7Component(position=2)
    icd_3: Optional[ST] = HL7Component(position=3)
    certification_patient_type = icd_1
    certification_required = icd_2
    date_time_certification_required = icd_3

class JCC(HL7DataType):
    jcc_1: Optional[ST] = HL7Component(position=1)
    jcc_2: Optional[ST] = HL7Component(position=2)
    jcc_3: Optional[ST] = HL7Component(position=3)
    job_code = jcc_1
    job_class = jcc_2
    job_description_text = jcc_3

class MA(HL7DataType):
    ma_1: Optional[ST] = HL7Component(position=1)
    ma_2: Optional[ST] = HL7Component(position=2)
    ma_3: Optional[ST] = HL7Component(position=3)
    ma_4: Optional[ST] = HL7Component(position=4)
    ma_5: Optional[ST] = HL7Component(position=5)
    sample_y_from_channel_1 = ma_1
    sample_y_from_channel_2 = ma_2
    sample_y_from_channel_3 = ma_3
    sample_y_from_channel_4 = ma_4

class MO(HL7DataType):
    mo_1: Optional[ST] = HL7Component(position=1)
    mo_2: Optional[ST] = HL7Component(position=2)
    quantity = mo_1
    denomination = mo_2

class MOC(HL7DataType):
    moc_1: Optional[ST] = HL7Component(position=1)
    moc_2: Optional[ST] = HL7Component(position=2)
    monetary_amount = moc_1
    charge_code = moc_2

class MOP(HL7DataType):
    mop_1: Optional[ST] = HL7Component(position=1)
    mop_2: Optional[ST] = HL7Component(position=2)
    mop_3: Optional[ST] = HL7Component(position=3)
    money_or_percentage_indicator = mop_1
    money_or_percentage_quantity = mop_2
    monetary_denomination = mop_3

class MSG(HL7DataType):
    msg_1: Optional[ST] = HL7Component(position=1)
    msg_2: Optional[ST] = HL7Component(position=2)
    msg_3: Optional[ST] = HL7Component(position=3)
    message_code = msg_1
    trigger_event = msg_2
    message_structure = msg_3

class NA(HL7DataType):
    na_1: Optional[ST] = HL7Component(position=1)
    na_2: Optional[ST] = HL7Component(position=2)
    na_3: Optional[ST] = HL7Component(position=3)
    na_4: Optional[ST] = HL7Component(position=4)
    na_5: Optional[ST] = HL7Component(position=5)
    value1 = na_1
    value2 = na_2
    value3 = na_3
    value4 = na_4

class NDL(HL7DataType):
    ndl_1: Optional[ST] = HL7Component(position=1)
    ndl_2: Optional[ST] = HL7Component(position=2)
    ndl_3: Optional[ST] = HL7Component(position=3)
    ndl_4: Optional[ST] = HL7Component(position=4)
    ndl_5: Optional[ST] = HL7Component(position=5)
    ndl_6: Optional[ST] = HL7Component(position=6)
    ndl_7: Optional[ST] = HL7Component(position=7)
    ndl_8: Optional[ST] = HL7Component(position=8)
    ndl_9: Optional[ST] = HL7Component(position=9)
    ndl_10: Optional[ST] = HL7Component(position=10)
    ndl_11: Optional[ST] = HL7Component(position=11)
    name = ndl_1
    start_date_time = ndl_2
    end_date_time = ndl_3
    point_of_care = ndl_4
    room = ndl_5
    bed = ndl_6
    facility = ndl_7
    location_status = ndl_8
    patient_location_type = ndl_9
    building = ndl_10
    floor = ndl_11

class NR(HL7DataType):
    nr_1: Optional[ST] = HL7Component(position=1)
    nr_2: Optional[ST] = HL7Component(position=2)
    low_value = nr_1
    high_value = nr_2

class OCD(HL7DataType):
    ocd_1: Optional[ST] = HL7Component(position=1)
    ocd_2: Optional[ST] = HL7Component(position=2)
    occurrence_code = ocd_1
    occurrence_date = ocd_2

class OG(HL7DataType):
    og_1: Optional[ST] = HL7Component(position=1)
    og_2: Optional[ST] = HL7Component(position=2)
    og_3: Optional[ST] = HL7Component(position=3)
    og_4: Optional[ST] = HL7Component(position=4)
    original_sub_identifier = og_1
    group = og_2
    sequence = og_3
    identifier = og_4

class OSP(HL7DataType):
    osp_1: Optional[ST] = HL7Component(position=1)
    osp_2: Optional[ST] = HL7Component(position=2)
    osp_3: Optional[ST] = HL7Component(position=3)
    occurrence_span_code = osp_1
    occurrence_span_start_date = osp_2
    occurrence_span_stop_date = osp_3

class PIP(HL7DataType):
    pip_1: Optional[ST] = HL7Component(position=1)
    pip_2: Optional[ST] = HL7Component(position=2)
    pip_3: Optional[ST] = HL7Component(position=3)
    pip_4: Optional[ST] = HL7Component(position=4)
    pip_5: Optional[ST] = HL7Component(position=5)
    privilege = pip_1
    privilege_class = pip_2
    expiration_date = pip_3
    activation_date = pip_4
    facility = pip_5

class PL(HL7DataType):
    pl_1: Optional[ST] = HL7Component(position=1)
    pl_2: Optional[ST] = HL7Component(position=2)
    pl_3: Optional[ST] = HL7Component(position=3)
    pl_4: Optional[ST] = HL7Component(position=4)
    pl_5: Optional[ST] = HL7Component(position=5)
    pl_6: Optional[ST] = HL7Component(position=6)
    pl_7: Optional[ST] = HL7Component(position=7)
    pl_8: Optional[ST] = HL7Component(position=8)
    pl_9: Optional[ST] = HL7Component(position=9)
    pl_10: Optional[ST] = HL7Component(position=10)
    pl_11: Optional[ST] = HL7Component(position=11)
    point_of_care = pl_1
    room = pl_2
    bed = pl_3
    facility = pl_4
    location_status = pl_5
    person_location_type = pl_6
    building = pl_7
    floor = pl_8
    location_description = pl_9
    comprehensive_location_identifier = pl_10
    assigning_authority_for_location = pl_11

class PLN(HL7DataType):
    pln_1: Optional[ST] = HL7Component(position=1)
    pln_2: Optional[ST] = HL7Component(position=2)
    pln_3: Optional[ST] = HL7Component(position=3)
    pln_4: Optional[ST] = HL7Component(position=4)
    id_number = pln_1
    type_of_id_number = pln_2
    stateother_qualifying_information = pln_3
    expiration_date = pln_4

class PPN(HL7DataType):
    ppn_1: Optional[ST] = HL7Component(position=1)
    ppn_2: Optional[ST] = HL7Component(position=2)
    ppn_3: Optional[ST] = HL7Component(position=3)
    ppn_4: Optional[ST] = HL7Component(position=4)
    ppn_5: Optional[ST] = HL7Component(position=5)
    ppn_6: Optional[ST] = HL7Component(position=6)
    ppn_9: Optional[ST] = HL7Component(position=7)
    ppn_10: Optional[ST] = HL7Component(position=8)
    ppn_11: Optional[ST] = HL7Component(position=9)
    ppn_12: Optional[ST] = HL7Component(position=10)
    ppn_13: Optional[ST] = HL7Component(position=11)
    ppn_14: Optional[ST] = HL7Component(position=12)
    ppn_15: Optional[ST] = HL7Component(position=13)
    ppn_16: Optional[ST] = HL7Component(position=14)
    ppn_17: Optional[ST] = HL7Component(position=15)
    ppn_19: Optional[ST] = HL7Component(position=16)
    ppn_20: Optional[ST] = HL7Component(position=17)
    ppn_21: Optional[ST] = HL7Component(position=18)
    ppn_22: Optional[ST] = HL7Component(position=19)
    ppn_23: Optional[ST] = HL7Component(position=20)
    ppn_24: Optional[ST] = HL7Component(position=21)
    ppn_25: Optional[ST] = HL7Component(position=22)
    ppn_26: Optional[ST] = HL7Component(position=23)
    person_identifier = ppn_1
    family_name = ppn_2
    given_name = ppn_3
    second_and_further_given_names_or_initials_thereof = ppn_4
    suffix = ppn_5
    prefix = ppn_6
    assigning_authority = ppn_9
    name_type_code = ppn_10
    identifier_check_digit = ppn_11
    check_digit_scheme = ppn_12
    identifier_type_code = ppn_13
    assigning_facility = ppn_14
    date_time_action_performed = ppn_15
    name_representation_code = ppn_16
    name_context = ppn_17
    name_assembly_order = ppn_19
    effective_date = ppn_20
    expiration_date = ppn_21
    professional_suffix = ppn_22
    assigning_jurisdiction = ppn_23
    assigning_agency_or_department = ppn_24
    security_check = ppn_25
    security_check_scheme = ppn_26

class PRL(HL7DataType):
    prl_1: Optional[ST] = HL7Component(position=1)
    prl_2: Optional[ST] = HL7Component(position=2)
    prl_3: Optional[ST] = HL7Component(position=3)
    parent_observation_identifier = prl_1
    parent_observation_subidentifier = prl_2
    parent_observation_value_descriptor = prl_3

class PT(HL7DataType):
    pt_1: Optional[ST] = HL7Component(position=1)
    pt_2: Optional[ST] = HL7Component(position=2)
    processing_id = pt_1
    processing_mode = pt_2

class PTA(HL7DataType):
    pta_1: Optional[ST] = HL7Component(position=1)
    pta_2: Optional[ST] = HL7Component(position=2)
    pta_4: Optional[ST] = HL7Component(position=3)
    policy_type = pta_1
    amount_class = pta_2
    money_or_percentage = pta_4

class QIP(HL7DataType):
    qip_1: Optional[ST] = HL7Component(position=1)
    qip_2: Optional[ST] = HL7Component(position=2)
    segment_field_name = qip_1
    values = qip_2

class QSC(HL7DataType):
    qsc_1: Optional[ST] = HL7Component(position=1)
    qsc_2: Optional[ST] = HL7Component(position=2)
    qsc_3: Optional[ST] = HL7Component(position=3)
    qsc_4: Optional[ST] = HL7Component(position=4)
    segment_field_name = qsc_1
    relational_operator = qsc_2
    value = qsc_3
    relational_conjunction = qsc_4

class RCD(HL7DataType):
    rcd_1: Optional[ST] = HL7Component(position=1)
    rcd_2: Optional[ST] = HL7Component(position=2)
    rcd_3: Optional[ST] = HL7Component(position=3)
    segment_field_name = rcd_1
    hl7_data_type = rcd_2
    maximum_column_width = rcd_3

class RFR(HL7DataType):
    rfr_1: Optional[ST] = HL7Component(position=1)
    rfr_2: Optional[ST] = HL7Component(position=2)
    rfr_3: Optional[ST] = HL7Component(position=3)
    rfr_4: Optional[ST] = HL7Component(position=4)
    rfr_5: Optional[ST] = HL7Component(position=5)
    rfr_6: Optional[ST] = HL7Component(position=6)
    rfr_7: Optional[ST] = HL7Component(position=7)
    numeric_range = rfr_1
    sex = rfr_2
    age_range = rfr_3
    gestational_age_range = rfr_4
    species = rfr_5
    racesubspecies = rfr_6
    conditions = rfr_7

class RI(HL7DataType):
    ri_1: Optional[ST] = HL7Component(position=1)
    ri_2: Optional[ST] = HL7Component(position=2)
    repeat_pattern = ri_1
    explicit_time_interval = ri_2

class RMC(HL7DataType):
    rmc_1: Optional[ST] = HL7Component(position=1)
    rmc_2: Optional[ST] = HL7Component(position=2)
    rmc_4: Optional[ST] = HL7Component(position=3)
    room_type = rmc_1
    amount_type = rmc_2
    money_or_percentage = rmc_4

class RP(HL7DataType):
    rp_1: Optional[ST] = HL7Component(position=1)
    rp_2: Optional[ST] = HL7Component(position=2)
    rp_3: Optional[ST] = HL7Component(position=3)
    rp_4: Optional[ST] = HL7Component(position=4)
    pointer = rp_1
    application_id = rp_2
    type_of_data = rp_3
    subtype = rp_4

class RPT(HL7DataType):
    rpt_1: Optional[ST] = HL7Component(position=1)
    rpt_2: Optional[ST] = HL7Component(position=2)
    rpt_3: Optional[ST] = HL7Component(position=3)
    rpt_4: Optional[ST] = HL7Component(position=4)
    rpt_5: Optional[ST] = HL7Component(position=5)
    rpt_6: Optional[ST] = HL7Component(position=6)
    rpt_7: Optional[ST] = HL7Component(position=7)
    rpt_8: Optional[ST] = HL7Component(position=8)
    rpt_9: Optional[ST] = HL7Component(position=9)
    rpt_10: Optional[ST] = HL7Component(position=10)
    rpt_11: Optional[ST] = HL7Component(position=11)
    repeat_pattern_code = rpt_1
    calendar_alignment = rpt_2
    phase_range_begin_value = rpt_3
    phase_range_end_value = rpt_4
    period_quantity = rpt_5
    period_units = rpt_6
    institution_specified_time = rpt_7
    event = rpt_8
    event_offset_quantity = rpt_9
    event_offset_units = rpt_10
    general_timing_specification = rpt_11

class SAD(HL7DataType):
    sad_1: Optional[ST] = HL7Component(position=1)
    sad_2: Optional[ST] = HL7Component(position=2)
    sad_3: Optional[ST] = HL7Component(position=3)
    street_or_mailing_address = sad_1
    street_name = sad_2
    dwelling_number = sad_3

class SCV(HL7DataType):
    scv_1: Optional[ST] = HL7Component(position=1)
    scv_2: Optional[ST] = HL7Component(position=2)
    parameter_class = scv_1
    parameter_value = scv_2

class SN(HL7DataType):
    sn_1: Optional[ST] = HL7Component(position=1)
    sn_2: Optional[ST] = HL7Component(position=2)
    sn_3: Optional[ST] = HL7Component(position=3)
    sn_4: Optional[ST] = HL7Component(position=4)
    comparator = sn_1
    num1 = sn_2
    separator_suffix = sn_3
    num2 = sn_4

class SPD(HL7DataType):
    spd_1: Optional[ST] = HL7Component(position=1)
    spd_2: Optional[ST] = HL7Component(position=2)
    spd_3: Optional[ST] = HL7Component(position=3)
    spd_4: Optional[ST] = HL7Component(position=4)
    specialty_name = spd_1
    governing_board = spd_2
    eligible_or_certified = spd_3
    date_of_certification = spd_4

class SRT(HL7DataType):
    srt_1: Optional[ST] = HL7Component(position=1)
    srt_2: Optional[ST] = HL7Component(position=2)
    sortby_field = srt_1
    sequencing = srt_2

class UVC(HL7DataType):
    uvc_1: Optional[ST] = HL7Component(position=1)
    uvc_2: Optional[ST] = HL7Component(position=2)
    uvc_3: Optional[ST] = HL7Component(position=3)
    uvc_4: Optional[ST] = HL7Component(position=4)
    value_code = uvc_1
    value_amount = uvc_2
    non_monetary_value_amount_quantity = uvc_3
    non_monetary_value_amount_units = uvc_4

class VH(HL7DataType):
    vh_1: Optional[ST] = HL7Component(position=1)
    vh_2: Optional[ST] = HL7Component(position=2)
    vh_3: Optional[ST] = HL7Component(position=3)
    vh_4: Optional[ST] = HL7Component(position=4)
    start_day_range = vh_1
    end_day_range = vh_2
    start_hour_range = vh_3
    end_hour_range = vh_4

class VID(HL7DataType):
    vid_1: Optional[ST] = HL7Component(position=1)
    vid_2: Optional[ST] = HL7Component(position=2)
    vid_3: Optional[ST] = HL7Component(position=3)
    version_id = vid_1
    internationalization_code = vid_2
    international_version_id = vid_3

class VR(HL7DataType):
    vr_1: Optional[ST] = HL7Component(position=1)
    vr_2: Optional[ST] = HL7Component(position=2)
    first_data_code_value = vr_1
    last_data_code_value = vr_2

class WVI(HL7DataType):
    wvi_1: Optional[ST] = HL7Component(position=1)
    wvi_2: Optional[ST] = HL7Component(position=2)
    channel_number = wvi_1
    channel_name = wvi_2

class WVS(HL7DataType):
    wvs_1: Optional[ST] = HL7Component(position=1)
    wvs_2: Optional[ST] = HL7Component(position=2)
    source_one_name = wvs_1
    source_two_name = wvs_2

class XAD(HL7DataType):
    xad_1: Optional[ST] = HL7Component(position=1)
    xad_2: Optional[ST] = HL7Component(position=2)
    xad_3: Optional[ST] = HL7Component(position=3)
    xad_4: Optional[ST] = HL7Component(position=4)
    xad_5: Optional[ST] = HL7Component(position=5)
    xad_6: Optional[ST] = HL7Component(position=6)
    xad_7: Optional[ST] = HL7Component(position=7)
    xad_8: Optional[ST] = HL7Component(position=8)
    xad_9: Optional[ST] = HL7Component(position=9)
    xad_10: Optional[ST] = HL7Component(position=10)
    xad_11: Optional[ST] = HL7Component(position=11)
    xad_13: Optional[ST] = HL7Component(position=12)
    xad_14: Optional[ST] = HL7Component(position=13)
    xad_15: Optional[ST] = HL7Component(position=14)
    xad_16: Optional[ST] = HL7Component(position=15)
    xad_17: Optional[ST] = HL7Component(position=16)
    xad_18: Optional[ST] = HL7Component(position=17)
    xad_19: Optional[ST] = HL7Component(position=18)
    xad_20: Optional[ST] = HL7Component(position=19)
    xad_21: Optional[ST] = HL7Component(position=20)
    xad_22: Optional[ST] = HL7Component(position=21)
    xad_23: Optional[ST] = HL7Component(position=22)
    street_address = xad_1
    other_designation = xad_2
    city = xad_3
    state_or_province = xad_4
    zip_or_postal_code = xad_5
    country = xad_6
    address_type = xad_7
    other_geographic_designation = xad_8
    county_parish_code = xad_9
    census_tract = xad_10
    address_representation_code = xad_11
    effective_date = xad_13
    expiration_date = xad_14
    expiration_reason = xad_15
    temporary_indicator = xad_16
    bad_address_indicator = xad_17
    address_usage = xad_18
    addressee = xad_19
    comment = xad_20
    preference_order = xad_21
    protection_code = xad_22
    address_identifier = xad_23

class XCN(HL7DataType):
    xcn_1: Optional[ST] = HL7Component(position=1)
    xcn_2: Optional[ST] = HL7Component(position=2)
    xcn_3: Optional[ST] = HL7Component(position=3)
    xcn_4: Optional[ST] = HL7Component(position=4)
    xcn_5: Optional[ST] = HL7Component(position=5)
    xcn_6: Optional[ST] = HL7Component(position=6)
    xcn_8: Optional[ST] = HL7Component(position=7)
    xcn_9: Optional[ST] = HL7Component(position=8)
    xcn_10: Optional[ST] = HL7Component(position=9)
    xcn_11: Optional[ST] = HL7Component(position=10)
    xcn_12: Optional[ST] = HL7Component(position=11)
    xcn_13: Optional[ST] = HL7Component(position=12)
    xcn_14: Optional[ST] = HL7Component(position=13)
    xcn_15: Optional[ST] = HL7Component(position=14)
    xcn_16: Optional[ST] = HL7Component(position=15)
    xcn_18: Optional[ST] = HL7Component(position=16)
    xcn_19: Optional[ST] = HL7Component(position=17)
    xcn_20: Optional[ST] = HL7Component(position=18)
    xcn_21: Optional[ST] = HL7Component(position=19)
    xcn_22: Optional[ST] = HL7Component(position=20)
    xcn_23: Optional[ST] = HL7Component(position=21)
    xcn_24: Optional[ST] = HL7Component(position=22)
    xcn_25: Optional[ST] = HL7Component(position=23)
    person_identifier = xcn_1
    family_name = xcn_2
    given_name = xcn_3
    second_and_further_given_names_or_initials_thereof = xcn_4
    suffix = xcn_5
    prefix = xcn_6
    source_table = xcn_8
    assigning_authority = xcn_9
    name_type_code = xcn_10
    identifier_check_digit = xcn_11
    check_digit_scheme = xcn_12
    identifier_type_code = xcn_13
    assigning_facility = xcn_14
    name_representation_code = xcn_15
    name_context = xcn_16
    name_assembly_order = xcn_18
    effective_date = xcn_19
    expiration_date = xcn_20
    professional_suffix = xcn_21
    assigning_jurisdiction = xcn_22
    assigning_agency_or_department = xcn_23
    security_check = xcn_24
    security_check_scheme = xcn_25

class XON(HL7DataType):
    xon_1: Optional[ST] = HL7Component(position=1)
    xon_2: Optional[ST] = HL7Component(position=2)
    xon_6: Optional[ST] = HL7Component(position=3)
    xon_7: Optional[ST] = HL7Component(position=4)
    xon_8: Optional[ST] = HL7Component(position=5)
    xon_9: Optional[ST] = HL7Component(position=6)
    xon_10: Optional[ST] = HL7Component(position=7)
    organization_name = xon_1
    organization_name_type_code = xon_2
    assigning_authority = xon_6
    identifier_type_code = xon_7
    assigning_facility = xon_8
    name_representation_code = xon_9
    organization_identifier = xon_10

class XPN(HL7DataType):
    xpn_1: Optional[ST] = HL7Component(position=1)
    xpn_2: Optional[ST] = HL7Component(position=2)
    xpn_3: Optional[ST] = HL7Component(position=3)
    xpn_4: Optional[ST] = HL7Component(position=4)
    xpn_5: Optional[ST] = HL7Component(position=5)
    xpn_7: Optional[ST] = HL7Component(position=6)
    xpn_8: Optional[ST] = HL7Component(position=7)
    xpn_9: Optional[ST] = HL7Component(position=8)
    xpn_11: Optional[ST] = HL7Component(position=9)
    xpn_12: Optional[ST] = HL7Component(position=10)
    xpn_13: Optional[ST] = HL7Component(position=11)
    xpn_14: Optional[ST] = HL7Component(position=12)
    xpn_15: Optional[ST] = HL7Component(position=13)
    family_name = xpn_1
    given_name = xpn_2
    second_and_further_given_names_or_initials_thereof = xpn_3
    suffix = xpn_4
    prefix = xpn_5
    name_type_code = xpn_7
    name_representation_code = xpn_8
    name_context = xpn_9
    name_assembly_order = xpn_11
    effective_date = xpn_12
    expiration_date = xpn_13
    professional_suffix = xpn_14
    called_by = xpn_15

class XTN(HL7DataType):
    xtn_2: Optional[ST] = HL7Component(position=1)
    xtn_3: Optional[ST] = HL7Component(position=2)
    xtn_4: Optional[ST] = HL7Component(position=3)
    xtn_5: Optional[ST] = HL7Component(position=4)
    xtn_6: Optional[ST] = HL7Component(position=5)
    xtn_7: Optional[ST] = HL7Component(position=6)
    xtn_8: Optional[ST] = HL7Component(position=7)
    xtn_9: Optional[ST] = HL7Component(position=8)
    xtn_10: Optional[ST] = HL7Component(position=9)
    xtn_11: Optional[ST] = HL7Component(position=10)
    xtn_12: Optional[ST] = HL7Component(position=11)
    xtn_13: Optional[ST] = HL7Component(position=12)
    xtn_14: Optional[ST] = HL7Component(position=13)
    xtn_15: Optional[ST] = HL7Component(position=14)
    xtn_16: Optional[ST] = HL7Component(position=15)
    xtn_17: Optional[ST] = HL7Component(position=16)
    xtn_18: Optional[ST] = HL7Component(position=17)
    telecommunication_use_code = xtn_2
    telecommunication_equipment_type = xtn_3
    communication_address = xtn_4
    country_code = xtn_5
    area_city_code = xtn_6
    local_number = xtn_7
    extension = xtn_8
    any_text = xtn_9
    extension_prefix = xtn_10
    speed_dial_code = xtn_11
    unformatted_telephone_number = xtn_12
    effective_start_date = xtn_13
    expiration_date = xtn_14
    expiration_reason = xtn_15
    protection_code = xtn_16
    shared_telecommunication_identifier = xtn_17
    preference_order = xtn_18

class varies(HL7DataType):
    pass

