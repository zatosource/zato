from __future__ import annotations

from zato.hl7v2.base import HL7Segment, HL7Field, Usage
from zato.hl7v2.v2_9.primitives import (
    DT,
    DTM,
    FT,
    ID,
    IS,
    NM,
    SI,
    ST,
    TM,
    TX,
    Varies,
)
from zato.hl7v2.v2_9.datatypes import (
    AUI,
    CCD,
    CNE,
    CP,
    CQ,
    CWE,
    CX,
    DDI,
    DIN,
    DLD,
    DLN,
    DLT,
    DR,
    DTN,
    ED,
    EI,
    EIP,
    ERL,
    FC,
    HD,
    ICD,
    JCC,
    MO,
    MOC,
    MOP,
    MSG,
    NA,
    NR,
    OCD,
    OG,
    OSP,
    PIP,
    PL,
    PLN,
    PPN,
    PRL,
    PT,
    PTA,
    RCD,
    RFR,
    RI,
    RMC,
    RPT,
    SCV,
    SN,
    SPD,
    SRT,
    UVC,
    VH,
    VID,
    XAD,
    XCN,
    XON,
    XPN,
    XTN,
    varies,
)

class ABS(HL7Segment):
    _segment_id = "ABS"

    discharge_care_provider = HL7Field[XCN | str | None](
        position=1,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70010",    )
    transfer_medical_service_code = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70069",    )
    severity_of_illness_code = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70421",    )
    date_time_of_attestation = HL7Field[DTM | str | None](
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    attested_by = HL7Field[XCN | str | None](
        position=5,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    triage_code = HL7Field[CWE | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70422",    )
    abstract_completion_date_time = HL7Field[DTM | str | None](
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    abstracted_by = HL7Field[XCN | str | None](
        position=8,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    case_category_code = HL7Field[CWE | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70423",    )
    caesarian_section_indicator = HL7Field[ID | str | None](
        position=10,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    gestation_category_code = HL7Field[CWE | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70424",    )
    gestation_period_weeks = HL7Field[NM | str | None](
        position=12,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    newborn_code = HL7Field[CWE | str | None](
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70425",    )
    stillborn_indicator = HL7Field[ID | str | None](
        position=14,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )

class ACC(HL7Segment):
    _segment_id = "ACC"

    accident_date_time = HL7Field[DTM | str | None](
        position=1,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    accident_code = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70050",    )
    accident_location = HL7Field[ST | str | None](
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    auto_accident_state = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70347",    )
    accident_job_related_indicator = HL7Field[ID | str | None](
        position=5,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    accident_death_indicator = HL7Field[ID | str | None](
        position=6,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    entered_by = HL7Field[XCN | str | None](
        position=7,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    accident_description = HL7Field[ST | str | None](
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    brought_in_by = HL7Field[ST | str | None](
        position=9,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    police_notified_indicator = HL7Field[ID | str | None](
        position=10,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    accident_address = HL7Field[XAD | str | None](
        position=11,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    degree_of_patient_liability = HL7Field[NM | str | None](
        position=12,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    accident_identifier = HL7Field[list[EI] | EI | list[str] | str | None](
        position=13,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,    )

class ADD(HL7Segment):
    _segment_id = "ADD"

    addendum_continuation_pointer = HL7Field[ST | str | None](
        position=1,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class ADJ(HL7Segment):
    _segment_id = "ADJ"

    provider_adjustment_number = HL7Field[EI | str](
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    payer_adjustment_number = HL7Field[EI | str](
        position=2,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    adjustment_sequence_number = HL7Field[SI | str](
        position=3,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    adjustment_category = HL7Field[CWE | str](
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70564",    )
    adjustment_amount = HL7Field[CP | str | None](
        position=5,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    adjustment_quantity = HL7Field[CQ | str | None](
        position=6,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70560",    )
    adjustment_reason_pa = HL7Field[CWE | str | None](
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70565",    )
    adjustment_description = HL7Field[ST | str | None](
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    original_value = HL7Field[NM | str | None](
        position=9,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    substitute_value = HL7Field[NM | str | None](
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    adjustment_action = HL7Field[CWE | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70569",    )
    provider_adjustment_number_cross_reference = HL7Field[EI | str | None](
        position=12,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    provider_product_service_line_item_number_cross_reference = HL7Field[EI | str | None](
        position=13,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    adjustment_date = HL7Field[DTM | str](
        position=14,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    responsible_organization = HL7Field[XON | str | None](
        position=15,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class AFF(HL7Segment):
    _segment_id = "AFF"

    set_id_aff = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    professional_organization = HL7Field[XON | str](
        position=2,
        datatype="XON",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    professional_organization_address = HL7Field[XAD | str | None](
        position=3,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    professional_organization_affiliation_date_range = HL7Field[list[DR] | DR | list[str] | str | None](
        position=4,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    professional_affiliation_additional_information = HL7Field[ST | str | None](
        position=5,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class AIG(HL7Segment):
    _segment_id = "AIG"

    set_id_aig = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    segment_action_code = HL7Field[ID | str | None](
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70206",    )
    resource_id = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    resource_type = HL7Field[CWE | str](
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    resource_group = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    resource_quantity = HL7Field[NM | str | None](
        position=6,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    resource_quantity_units = HL7Field[CNE | str | None](
        position=7,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    start_date_time = HL7Field[DTM | str | None](
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    start_date_time_offset = HL7Field[NM | str | None](
        position=9,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    start_date_time_offset_units = HL7Field[CNE | str | None](
        position=10,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    duration = HL7Field[NM | str | None](
        position=11,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    duration_units = HL7Field[CNE | str | None](
        position=12,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    allow_substitution_code = HL7Field[CWE | str | None](
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70279",    )
    filler_status_code = HL7Field[CWE | str | None](
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70278",    )

class AIL(HL7Segment):
    _segment_id = "AIL"

    set_id_ail = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    segment_action_code = HL7Field[ID | str | None](
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70206",    )
    location_resource_id = HL7Field[list[PL] | PL | list[str] | str | None](
        position=3,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    location_type_ail = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70305",    )
    location_group = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    start_date_time = HL7Field[DTM | str | None](
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    start_date_time_offset = HL7Field[NM | str | None](
        position=7,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    start_date_time_offset_units = HL7Field[CNE | str | None](
        position=8,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    duration = HL7Field[NM | str | None](
        position=9,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    duration_units = HL7Field[CNE | str | None](
        position=10,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    allow_substitution_code = HL7Field[CWE | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70279",    )
    filler_status_code = HL7Field[CWE | str | None](
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70278",    )

class AIP(HL7Segment):
    _segment_id = "AIP"

    set_id_aip = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    segment_action_code = HL7Field[ID | str | None](
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70206",    )
    personnel_resource_id = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=3,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    resource_type = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70182",    )
    resource_group = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    start_date_time = HL7Field[DTM | str | None](
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    start_date_time_offset = HL7Field[NM | str | None](
        position=7,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    start_date_time_offset_units = HL7Field[CNE | str | None](
        position=8,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    duration = HL7Field[NM | str | None](
        position=9,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    duration_units = HL7Field[CNE | str | None](
        position=10,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    allow_substitution_code = HL7Field[CWE | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70279",    )
    filler_status_code = HL7Field[CWE | str | None](
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70278",    )

class AIS(HL7Segment):
    _segment_id = "AIS"

    set_id_ais = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    segment_action_code = HL7Field[ID | str | None](
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70206",    )
    universal_service_identifier = HL7Field[CWE | str](
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    start_date_time = HL7Field[DTM | str | None](
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    start_date_time_offset = HL7Field[NM | str | None](
        position=5,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    start_date_time_offset_units = HL7Field[CNE | str | None](
        position=6,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    duration = HL7Field[NM | str | None](
        position=7,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    duration_units = HL7Field[CNE | str | None](
        position=8,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    allow_substitution_code = HL7Field[CWE | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70279",    )
    filler_status_code = HL7Field[CWE | str | None](
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70278",    )
    placer_supplemental_service_information = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70411",    )
    filler_supplemental_service_information = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70411",    )

class AL1(HL7Segment):
    _segment_id = "AL1"

    set_id_al1 = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    allergen_type_code = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70127",    )
    allergen_code_mnemonic_description = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    allergy_severity_code = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70128",    )
    allergy_reaction_code = HL7Field[list[ST] | ST | list[str] | str | None](
        position=5,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )

class APR(HL7Segment):
    _segment_id = "APR"

    time_selection_criteria = HL7Field[list[SCV] | SCV | list[str] | str | None](
        position=1,
        datatype="SCV",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70294",    )
    resource_selection_criteria = HL7Field[list[SCV] | SCV | list[str] | str | None](
        position=2,
        datatype="SCV",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70294",    )
    location_selection_criteria = HL7Field[list[SCV] | SCV | list[str] | str | None](
        position=3,
        datatype="SCV",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70294",    )
    slot_spacing_criteria = HL7Field[NM | str | None](
        position=4,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    filler_override_criteria = HL7Field[list[SCV] | SCV | list[str] | str | None](
        position=5,
        datatype="SCV",
        usage=Usage.OPTIONAL,
        repeatable=True,    )

class ARQ(HL7Segment):
    _segment_id = "ARQ"

    placer_appointment_id = HL7Field[EI | str](
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    filler_appointment_id = HL7Field[EI | str | None](
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    occurrence_number = HL7Field[NM | str | None](
        position=3,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    placer_order_group_number = HL7Field[EI | str | None](
        position=4,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    schedule_id = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    request_event_reason = HL7Field[CWE | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    appointment_reason = HL7Field[CWE | str | None](
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70276",    )
    appointment_type = HL7Field[CWE | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70277",    )
    appointment_duration = HL7Field[NM | str | None](
        position=9,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    appointment_duration_units = HL7Field[CNE | str | None](
        position=10,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    requested_start_date_time_range = HL7Field[list[DR] | DR | list[str] | str | None](
        position=11,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    priority_arq = HL7Field[ST | str | None](
        position=12,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    repeating_interval = HL7Field[RI | str | None](
        position=13,
        datatype="RI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    repeating_interval_duration = HL7Field[ST | str | None](
        position=14,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    placer_contact_person = HL7Field[list[XCN] | XCN | list[str] | str](
        position=15,
        datatype="XCN",
        usage=Usage.REQUIRED,
        repeatable=True,    )
    placer_contact_phone_number = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=16,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    placer_contact_address = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=17,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    placer_contact_location = HL7Field[PL | str | None](
        position=18,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    entered_by_person = HL7Field[list[XCN] | XCN | list[str] | str](
        position=19,
        datatype="XCN",
        usage=Usage.REQUIRED,
        repeatable=True,    )
    entered_by_phone_number = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=20,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    entered_by_location = HL7Field[PL | str | None](
        position=21,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    parent_placer_appointment_id = HL7Field[EI | str | None](
        position=22,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    parent_filler_appointment_id = HL7Field[EI | str | None](
        position=23,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    placer_order_number = HL7Field[list[EI] | EI | list[str] | str | None](
        position=24,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    filler_order_number = HL7Field[list[EI] | EI | list[str] | str | None](
        position=25,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    alternate_placer_order_group_number = HL7Field[EIP | str | None](
        position=26,
        datatype="EIP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class ARV(HL7Segment):
    _segment_id = "ARV"

    set_id = HL7Field[SI | str | None](
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    access_restriction_action_code = HL7Field[CNE | str](
        position=2,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70206",    )
    access_restriction_value = HL7Field[CWE | str](
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70717",    )
    access_restriction_reason = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70719",    )
    special_access_restriction_instructions = HL7Field[list[ST] | ST | list[str] | str | None](
        position=5,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    access_restriction_date_range = HL7Field[DR | str | None](
        position=6,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    security_classification_tag = HL7Field[CWE | str](
        position=7,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70952",    )
    security_handling_instructions = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70953",    )
    access_restriction_message_location = HL7Field[list[ERL] | ERL | list[str] | str | None](
        position=9,
        datatype="ERL",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    access_restriction_instance_identifier = HL7Field[EI | str | None](
        position=10,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class AUT(HL7Segment):
    _segment_id = "AUT"

    authorizing_payor_plan_id = HL7Field[CWE | str | None](
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70072",    )
    authorizing_payor_company_id = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70285",    )
    authorizing_payor_company_name = HL7Field[ST | str | None](
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    authorization_effective_date = HL7Field[DTM | str | None](
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    authorization_expiration_date = HL7Field[DTM | str | None](
        position=5,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    authorization_identifier = HL7Field[EI | str | None](
        position=6,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    reimbursement_limit = HL7Field[CP | str | None](
        position=7,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    requested_number_of_treatments = HL7Field[CQ | str | None](
        position=8,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    authorized_number_of_treatments = HL7Field[CQ | str | None](
        position=9,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    process_date = HL7Field[DTM | str | None](
        position=10,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    requested_disciplines = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70522",    )
    authorized_disciplines = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70546",    )
    authorization_referral_type = HL7Field[CWE | str](
        position=13,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70551",    )
    approval_status = HL7Field[CWE | str | None](
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70563",    )
    planned_treatment_stop_date = HL7Field[DTM | str | None](
        position=15,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    clinical_service = HL7Field[CWE | str | None](
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70573",    )
    reason_text = HL7Field[ST | str | None](
        position=17,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    number_of_authorized_treatments_units = HL7Field[CQ | str | None](
        position=18,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    number_of_used_treatments_units = HL7Field[CQ | str | None](
        position=19,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    number_of_schedule_treatments_units = HL7Field[CQ | str | None](
        position=20,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    encounter_type = HL7Field[CWE | str | None](
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70574",    )
    remaining_benefit_amount = HL7Field[MO | str | None](
        position=22,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    authorized_provider = HL7Field[XON | str | None](
        position=23,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    authorized_health_professional = HL7Field[XCN | str | None](
        position=24,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    source_text = HL7Field[ST | str | None](
        position=25,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    source_date = HL7Field[DTM | str | None](
        position=26,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    source_phone = HL7Field[XTN | str | None](
        position=27,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    comment = HL7Field[ST | str | None](
        position=28,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    action_code = HL7Field[ID | str | None](
        position=29,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70206",    )

class BHS(HL7Segment):
    _segment_id = "BHS"

    batch_field_separator = HL7Field[ST | str](
        position=1,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    batch_encoding_characters = HL7Field[ST | str](
        position=2,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    batch_sending_application = HL7Field[HD | str | None](
        position=3,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    batch_sending_facility = HL7Field[HD | str | None](
        position=4,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    batch_receiving_application = HL7Field[HD | str | None](
        position=5,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    batch_receiving_facility = HL7Field[HD | str | None](
        position=6,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    batch_creation_date_time = HL7Field[DTM | str | None](
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    batch_security = HL7Field[ST | str | None](
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    batch_name_id_type = HL7Field[ST | str | None](
        position=9,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    batch_comment = HL7Field[ST | str | None](
        position=10,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    batch_control_id = HL7Field[ST | str | None](
        position=11,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    reference_batch_control_id = HL7Field[ST | str | None](
        position=12,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    batch_sending_network_address = HL7Field[HD | str | None](
        position=13,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    batch_receiving_network_address = HL7Field[HD | str | None](
        position=14,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    security_classification_tag = HL7Field[CWE | str | None](
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70952",    )
    security_handling_instructions = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70953",    )
    special_access_restriction_instructions = HL7Field[list[ST] | ST | list[str] | str | None](
        position=17,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )

class BLC(HL7Segment):
    _segment_id = "BLC"

    blood_product_code = HL7Field[CWE | str | None](
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70426",    )
    blood_amount = HL7Field[CQ | str | None](
        position=2,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class BLG(HL7Segment):
    _segment_id = "BLG"

    when_to_charge = HL7Field[CCD | str | None](
        position=1,
        datatype="CCD",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70100",    )
    charge_type = HL7Field[ID | str | None](
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70122",    )
    account_id = HL7Field[CX | str | None](
        position=3,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    charge_type_reason = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70475",    )

class BPO(HL7Segment):
    _segment_id = "BPO"

    set_id_bpo = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    bp_universal_service_identifier = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70575",    )
    bp_processing_requirements = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70508",    )
    bp_quantity = HL7Field[NM | str](
        position=4,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    bp_amount = HL7Field[NM | str | None](
        position=5,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bp_units = HL7Field[CWE | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70576",    )
    bp_intended_use_date_time = HL7Field[DTM | str | None](
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bp_intended_dispense_from_location = HL7Field[PL | str | None](
        position=8,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bp_intended_dispense_from_address = HL7Field[XAD | str | None](
        position=9,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bp_requested_dispense_date_time = HL7Field[DTM | str | None](
        position=10,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bp_requested_dispense_to_location = HL7Field[PL | str | None](
        position=11,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bp_requested_dispense_to_address = HL7Field[XAD | str | None](
        position=12,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bp_indication_for_use = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70509",    )
    bp_informed_consent_indicator = HL7Field[ID | str | None](
        position=14,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )

class BPX(HL7Segment):
    _segment_id = "BPX"

    set_id_bpx = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    bp_dispense_status = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70510",    )
    bp_status = HL7Field[ID | str](
        position=3,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70511",    )
    bp_date_time_of_status = HL7Field[DTM | str](
        position=4,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    bc_donation_id = HL7Field[EI | str | None](
        position=5,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bc_component = HL7Field[CNE | str | None](
        position=6,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70577",    )
    bc_donation_type_intended_use = HL7Field[CNE | str | None](
        position=7,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70578",    )
    cp_commercial_product = HL7Field[CWE | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70512",    )
    cp_manufacturer = HL7Field[XON | str | None](
        position=9,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    cp_lot_number = HL7Field[EI | str | None](
        position=10,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bp_blood_group = HL7Field[CNE | str | None](
        position=11,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70579",    )
    bc_special_testing = HL7Field[list[CNE] | CNE | list[str] | str | None](
        position=12,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70580",    )
    bp_expiration_date_time = HL7Field[DTM | str | None](
        position=13,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bp_quantity = HL7Field[NM | str](
        position=14,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    bp_amount = HL7Field[NM | str | None](
        position=15,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bp_units = HL7Field[CWE | str | None](
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70581",    )
    bp_unique_id = HL7Field[EI | str | None](
        position=17,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bp_actual_dispensed_to_location = HL7Field[PL | str | None](
        position=18,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bp_actual_dispensed_to_address = HL7Field[XAD | str | None](
        position=19,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bp_dispensed_to_receiver = HL7Field[XCN | str | None](
        position=20,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bp_dispensing_individual = HL7Field[XCN | str | None](
        position=21,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    action_code = HL7Field[ID | str | None](
        position=22,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class BTS(HL7Segment):
    _segment_id = "BTS"

    batch_message_count = HL7Field[ST | str | None](
        position=1,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    batch_comment = HL7Field[ST | str | None](
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    batch_totals = HL7Field[list[NM] | NM | list[str] | str | None](
        position=3,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=True,    )

class BTX(HL7Segment):
    _segment_id = "BTX"

    set_id_btx = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    bc_donation_id = HL7Field[EI | str | None](
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bc_component = HL7Field[CNE | str | None](
        position=3,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70582",    )
    bc_blood_group = HL7Field[CNE | str | None](
        position=4,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70583",    )
    cp_commercial_product = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70512",    )
    cp_manufacturer = HL7Field[XON | str | None](
        position=6,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    cp_lot_number = HL7Field[EI | str | None](
        position=7,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bp_quantity = HL7Field[NM | str](
        position=8,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    bp_amount = HL7Field[NM | str | None](
        position=9,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bp_units = HL7Field[CWE | str | None](
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70584",    )
    bp_transfusion_disposition_status = HL7Field[CWE | str](
        position=11,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70513",    )
    bp_message_status = HL7Field[ID | str](
        position=12,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70511",    )
    bp_date_time_of_status = HL7Field[DTM | str](
        position=13,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    bp_transfusion_administrator = HL7Field[XCN | str | None](
        position=14,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bp_transfusion_verifier = HL7Field[XCN | str | None](
        position=15,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bp_transfusion_start_date_time_of_status = HL7Field[DTM | str | None](
        position=16,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bp_transfusion_end_date_time_of_status = HL7Field[DTM | str | None](
        position=17,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bp_adverse_reaction_type = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70514",    )
    bp_transfusion_interrupted_reason = HL7Field[CWE | str | None](
        position=19,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70515",    )
    bp_unique_id = HL7Field[EI | str | None](
        position=20,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    action_code = HL7Field[ID | str | None](
        position=21,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class BUI(HL7Segment):
    _segment_id = "BUI"

    set_id_bui = HL7Field[SI | str | None](
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    blood_unit_identifier = HL7Field[EI | str](
        position=2,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    blood_unit_type = HL7Field[CWE | str](
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70566",    )
    blood_unit_weight = HL7Field[NM | str](
        position=4,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    weight_units = HL7Field[CNE | str](
        position=5,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70929",    )
    blood_unit_volume = HL7Field[NM | str](
        position=6,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    volume_units = HL7Field[CNE | str](
        position=7,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70930",    )
    container_catalog_number = HL7Field[ST | str](
        position=8,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    container_lot_number = HL7Field[ST | str](
        position=9,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    container_manufacturer = HL7Field[XON | str](
        position=10,
        datatype="XON",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    transport_temperature = HL7Field[NR | str](
        position=11,
        datatype="NR",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    transport_temperature_units = HL7Field[CNE | str](
        position=12,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70931",    )
    action_code = HL7Field[ID | str | None](
        position=13,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class CDM(HL7Segment):
    _segment_id = "CDM"

    primary_key_value_cdm = HL7Field[CWE | str](
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    charge_code_alias = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70132",    )
    charge_description_short = HL7Field[ST | str](
        position=3,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    charge_description_long = HL7Field[ST | str | None](
        position=4,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    description_override_indicator = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70268",    )
    exploding_charges = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70132",    )
    procedure_code = HL7Field[list[CNE] | CNE | list[str] | str | None](
        position=7,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70088",    )
    active_inactive_flag = HL7Field[ID | str | None](
        position=8,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70183",    )
    inventory_number = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70463",    )
    resource_load = HL7Field[NM | str | None](
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    contract_number = HL7Field[list[CX] | CX | list[str] | str | None](
        position=11,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    contract_organization = HL7Field[list[XON] | XON | list[str] | str | None](
        position=12,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    room_fee_indicator = HL7Field[ID | str | None](
        position=13,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )

class CDO(HL7Segment):
    _segment_id = "CDO"

    set_id_cdo = HL7Field[SI | str | None](
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    action_code = HL7Field[ID | str | None](
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    cumulative_dosage_limit = HL7Field[CQ | str | None](
        position=3,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    cumulative_dosage_limit_time_interval = HL7Field[CQ | str | None](
        position=4,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70924",    )

class CER(HL7Segment):
    _segment_id = "CER"

    set_id_cer = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    serial_number = HL7Field[ST | str | None](
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    version = HL7Field[ST | str | None](
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    granting_authority = HL7Field[XON | str | None](
        position=4,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    issuing_authority = HL7Field[XCN | str | None](
        position=5,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    signature = HL7Field[ED | str | None](
        position=6,
        datatype="ED",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    granting_country = HL7Field[ID | str | None](
        position=7,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70399",    )
    granting_state_province = HL7Field[CWE | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70347",    )
    granting_county_parish = HL7Field[CWE | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70289",    )
    certificate_type = HL7Field[CWE | str | None](
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    certificate_domain = HL7Field[CWE | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    subject_id = HL7Field[EI | str | None](
        position=12,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    subject_name = HL7Field[ST | str](
        position=13,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    subject_directory_attribute_extension = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    subject_public_key_info = HL7Field[CWE | str | None](
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    authority_key_identifier = HL7Field[CWE | str | None](
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    basic_constraint = HL7Field[ID | str | None](
        position=17,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    crl_distribution_point = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    jurisdiction_country = HL7Field[ID | str | None](
        position=19,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70399",    )
    jurisdiction_state_province = HL7Field[CWE | str | None](
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70347",    )
    jurisdiction_county_parish = HL7Field[CWE | str | None](
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70289",    )
    jurisdiction_breadth = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=22,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70547",    )
    granting_date = HL7Field[DTM | str | None](
        position=23,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    issuing_date = HL7Field[DTM | str | None](
        position=24,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    activation_date = HL7Field[DTM | str | None](
        position=25,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inactivation_date = HL7Field[DTM | str | None](
        position=26,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    expiration_date = HL7Field[DTM | str | None](
        position=27,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    renewal_date = HL7Field[DTM | str | None](
        position=28,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    revocation_date = HL7Field[DTM | str | None](
        position=29,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    revocation_reason_code = HL7Field[CWE | str | None](
        position=30,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    certificate_status_code = HL7Field[CWE | str | None](
        position=31,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70536",    )

class CM0(HL7Segment):
    _segment_id = "CM0"

    set_id_cm0 = HL7Field[SI | str | None](
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    sponsor_study_id = HL7Field[EI | str](
        position=2,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    alternate_study_id = HL7Field[EI | str | None](
        position=3,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    title_of_study = HL7Field[ST | str](
        position=4,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    chairman_of_study = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=5,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    last_irb_approval_date = HL7Field[DT | str | None](
        position=6,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    total_accrual_to_date = HL7Field[NM | str | None](
        position=7,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    last_accrual_date = HL7Field[DT | str | None](
        position=8,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    contact_for_study = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=9,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    contacts_telephone_number = HL7Field[XTN | str | None](
        position=10,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    contacts_address = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=11,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )

class CM1(HL7Segment):
    _segment_id = "CM1"

    set_id_cm1 = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    study_phase_identifier = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    description_of_study_phase = HL7Field[ST | str](
        position=3,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )

class CM2(HL7Segment):
    _segment_id = "CM2"

    set_id_cm2 = HL7Field[SI | str | None](
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    scheduled_time_point = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    description_of_time_point = HL7Field[ST | str | None](
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    events_scheduled_this_time_point = HL7Field[CWE | str](
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,    )

class CNS(HL7Segment):
    _segment_id = "CNS"

    starting_notification_reference_number = HL7Field[NM | str | None](
        position=1,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    ending_notification_reference_number = HL7Field[NM | str | None](
        position=2,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    starting_notification_date_time = HL7Field[DTM | str | None](
        position=3,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    ending_notification_date_time = HL7Field[DTM | str | None](
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    starting_notification_code = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70585",    )
    ending_notification_code = HL7Field[CWE | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70586",    )

class CON(HL7Segment):
    _segment_id = "CON"

    set_id_con = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    consent_type = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70496",    )
    consent_form_id_and_version = HL7Field[ST | str | None](
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    consent_form_number = HL7Field[EI | str | None](
        position=4,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    consent_text = HL7Field[list[FT] | FT | list[str] | str | None](
        position=5,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    subject_specific_consent_text = HL7Field[list[FT] | FT | list[str] | str | None](
        position=6,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    consent_background_information = HL7Field[list[FT] | FT | list[str] | str | None](
        position=7,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    subject_specific_consent_background_text = HL7Field[list[FT] | FT | list[str] | str | None](
        position=8,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    consenter_imposed_limitations = HL7Field[list[FT] | FT | list[str] | str | None](
        position=9,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    consent_mode = HL7Field[CNE | str | None](
        position=10,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70497",    )
    consent_status = HL7Field[CNE | str](
        position=11,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70498",    )
    consent_discussion_date_time = HL7Field[DTM | str | None](
        position=12,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    consent_decision_date_time = HL7Field[DTM | str | None](
        position=13,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    consent_effective_date_time = HL7Field[DTM | str | None](
        position=14,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    consent_end_date_time = HL7Field[DTM | str | None](
        position=15,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    subject_competence_indicator = HL7Field[ID | str | None](
        position=16,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    translator_assistance_indicator = HL7Field[ID | str | None](
        position=17,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    language_translated_to = HL7Field[CWE | str | None](
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70296",    )
    informational_material_supplied_indicator = HL7Field[ID | str | None](
        position=19,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    consent_bypass_reason = HL7Field[CWE | str | None](
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70499",    )
    consent_disclosure_level = HL7Field[ID | str | None](
        position=21,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70500",    )
    consent_non_disclosure_reason = HL7Field[CWE | str | None](
        position=22,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70501",    )
    non_subject_consenter_reason = HL7Field[CWE | str | None](
        position=23,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70502",    )
    consenter_id = HL7Field[list[XPN] | XPN | list[str] | str](
        position=24,
        datatype="XPN",
        usage=Usage.REQUIRED,
        repeatable=True,    )
    relationship_to_subject = HL7Field[list[CWE] | CWE | list[str] | str](
        position=25,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=True, table="HL70548",    )

class CSP(HL7Segment):
    _segment_id = "CSP"

    study_phase_identifier = HL7Field[CWE | str](
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    datetime_study_phase_began = HL7Field[DTM | str](
        position=2,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    datetime_study_phase_ended = HL7Field[DTM | str | None](
        position=3,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    study_phase_evaluability = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70588",    )

class CSR(HL7Segment):
    _segment_id = "CSR"

    sponsor_study_id = HL7Field[EI | str](
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    alternate_study_id = HL7Field[EI | str | None](
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    institution_registering_the_patient = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70589",    )
    sponsor_patient_id = HL7Field[CX | str](
        position=4,
        datatype="CX",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    alternate_patient_id_csr = HL7Field[CX | str | None](
        position=5,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    date_time_of_patient_study_registration = HL7Field[DTM | str](
        position=6,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    person_performing_study_registration = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=7,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    study_authorizing_provider = HL7Field[list[XCN] | XCN | list[str] | str](
        position=8,
        datatype="XCN",
        usage=Usage.REQUIRED,
        repeatable=True,    )
    date_time_patient_study_consent_signed = HL7Field[DTM | str | None](
        position=9,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    patient_study_eligibility_status = HL7Field[CWE | str | None](
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70590",    )
    study_randomization_datetime = HL7Field[DTM | str | None](
        position=11,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    randomized_study_arm = HL7Field[CWE | str | None](
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70591",    )
    stratum_for_study_randomization = HL7Field[CWE | str | None](
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70592",    )
    patient_evaluability_status = HL7Field[CWE | str | None](
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70593",    )
    date_time_ended_study = HL7Field[DTM | str | None](
        position=15,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    reason_ended_study = HL7Field[CWE | str | None](
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70594",    )
    action_code = HL7Field[ID | str | None](
        position=17,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class CSS(HL7Segment):
    _segment_id = "CSS"

    study_scheduled_time_point = HL7Field[CWE | str](
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70595",    )
    study_scheduled_patient_time_point = HL7Field[DTM | str | None](
        position=2,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    study_quality_control_codes = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70596",    )

class CTD(HL7Segment):
    _segment_id = "CTD"

    contact_role = HL7Field[list[CWE] | CWE | list[str] | str](
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=True, table="HL70131",    )
    contact_name = HL7Field[list[XPN] | XPN | list[str] | str | None](
        position=2,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    contact_address = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=3,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    contact_location = HL7Field[PL | str | None](
        position=4,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    contact_communication_information = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=5,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    preferred_method_of_contact = HL7Field[CWE | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70185",    )
    contact_identifiers = HL7Field[list[PLN] | PLN | list[str] | str | None](
        position=7,
        datatype="PLN",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70338",    )

class CTI(HL7Segment):
    _segment_id = "CTI"

    sponsor_study_id = HL7Field[EI | str](
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    study_phase_identifier = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    study_scheduled_time_point = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70595",    )
    action_code = HL7Field[ID | str | None](
        position=4,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class CTR(HL7Segment):
    _segment_id = "CTR"

    contract_identifier = HL7Field[EI | str](
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    contract_description = HL7Field[ST | str | None](
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    contract_status = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70536",    )
    effective_date = HL7Field[DTM | str](
        position=4,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    expiration_date = HL7Field[DTM | str](
        position=5,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    contract_owner_name = HL7Field[XPN | str | None](
        position=6,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    contract_originator_name = HL7Field[XPN | str | None](
        position=7,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    supplier_type = HL7Field[CWE | str](
        position=8,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70946",    )
    contract_type = HL7Field[CWE | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70965",    )
    free_on_board_freight_terms = HL7Field[CNE | str | None](
        position=10,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    price_protection_date = HL7Field[DTM | str | None](
        position=11,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    fixed_price_contract_indicator = HL7Field[CNE | str | None](
        position=12,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    group_purchasing_organization = HL7Field[XON | str | None](
        position=13,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    maximum_markup = HL7Field[MOP | str | None](
        position=14,
        datatype="MOP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    actual_markup = HL7Field[MOP | str | None](
        position=15,
        datatype="MOP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    corporation = HL7Field[list[XON] | XON | list[str] | str | None](
        position=16,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    parent_of_corporation = HL7Field[XON | str | None](
        position=17,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    pricing_tier_level = HL7Field[CWE | str | None](
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70966",    )
    contract_priority = HL7Field[ST | str | None](
        position=19,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    class_of_trade = HL7Field[CWE | str | None](
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70947",    )
    associated_contract_id = HL7Field[EI | str | None](
        position=21,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class DB1(HL7Segment):
    _segment_id = "DB1"

    set_id_db1 = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    disabled_person_code = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70334",    )
    disabled_person_identifier = HL7Field[list[CX] | CX | list[str] | str | None](
        position=3,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    disability_indicator = HL7Field[ID | str | None](
        position=4,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    disability_start_date = HL7Field[DT | str | None](
        position=5,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    disability_end_date = HL7Field[DT | str | None](
        position=6,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    disability_return_to_work_date = HL7Field[DT | str | None](
        position=7,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    disability_unable_to_work_date = HL7Field[DT | str | None](
        position=8,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class DEV(HL7Segment):
    _segment_id = "DEV"

    action_code = HL7Field[ID | str](
        position=1,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    unique_device_identifier = HL7Field[EI | str | None](
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    device_type = HL7Field[list[CNE] | CNE | list[str] | str | None](
        position=3,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70961",    )
    device_status = HL7Field[list[CNE] | CNE | list[str] | str | None](
        position=4,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70962",    )
    manufacturer_distributor = HL7Field[XON | str | None](
        position=5,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    brand_name = HL7Field[ST | str | None](
        position=6,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    model_identifier = HL7Field[ST | str | None](
        position=7,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    catalogue_identifier = HL7Field[ST | str | None](
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    udi_device_identifier = HL7Field[EI | str | None](
        position=9,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    device_lot_number = HL7Field[ST | str | None](
        position=10,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    device_serial_number = HL7Field[ST | str | None](
        position=11,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    device_manufacture_date = HL7Field[DTM | str | None](
        position=12,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    device_expiry_date = HL7Field[DTM | str | None](
        position=13,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    safety_characteristics = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70963",    )
    device_donation_identification = HL7Field[EI | str | None](
        position=15,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    software_version_number = HL7Field[ST | str | None](
        position=16,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    implantation_status = HL7Field[CNE | str | None](
        position=17,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70795",    )

class DG1(HL7Segment):
    _segment_id = "DG1"

    set_id_dg1 = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    diagnosis_code_dg1 = HL7Field[CWE | str](
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70051",    )
    diagnosis_date_time = HL7Field[DTM | str | None](
        position=5,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    diagnosis_type = HL7Field[CWE | str](
        position=6,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70052",    )
    diagnosis_priority = HL7Field[NM | str | None](
        position=15,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70359",    )
    diagnosing_clinician = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=16,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    diagnosis_classification = HL7Field[CWE | str | None](
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70228",    )
    confidential_indicator = HL7Field[ID | str | None](
        position=18,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    attestation_date_time = HL7Field[DTM | str | None](
        position=19,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    diagnosis_identifier = HL7Field[EI | str | None](
        position=20,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    diagnosis_action_code = HL7Field[ID | str | None](
        position=21,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70206",    )
    parent_diagnosis = HL7Field[EI | str | None](
        position=22,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    drg_ccl_value_code = HL7Field[CWE | str | None](
        position=23,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70728",    )
    drg_grouping_usage = HL7Field[ID | str | None](
        position=24,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    drg_diagnosis_determination_status = HL7Field[CWE | str | None](
        position=25,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70731",    )
    present_on_admission_poa_indicator = HL7Field[CWE | str | None](
        position=26,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70895",    )

class DMI(HL7Segment):
    _segment_id = "DMI"

    diagnostic_related_group = HL7Field[CNE | str | None](
        position=1,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70055",    )
    major_diagnostic_category = HL7Field[CNE | str | None](
        position=2,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70118",    )
    lower_and_upper_trim_points = HL7Field[NR | str | None](
        position=3,
        datatype="NR",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    average_length_of_stay = HL7Field[NM | str | None](
        position=4,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    relative_weight = HL7Field[NM | str | None](
        position=5,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class DON(HL7Segment):
    _segment_id = "DON"

    donation_identification_number_din = HL7Field[EI | str | None](
        position=1,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    donation_type = HL7Field[CNE | str | None](
        position=2,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    phlebotomy_start_date_time = HL7Field[DTM | str](
        position=3,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    phlebotomy_end_date_time = HL7Field[DTM | str](
        position=4,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    donation_duration = HL7Field[NM | str](
        position=5,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    donation_duration_units = HL7Field[CNE | str](
        position=6,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70932",    )
    intended_procedure_type = HL7Field[list[CNE] | CNE | list[str] | str](
        position=7,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=True, table="HL70933",    )
    actual_procedure_type = HL7Field[list[CNE] | CNE | list[str] | str](
        position=8,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=True, table="HL70933",    )
    donor_eligibility_flag = HL7Field[ID | str](
        position=9,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70136",    )
    donor_eligibility_procedure_type = HL7Field[list[CNE] | CNE | list[str] | str](
        position=10,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=True, table="HL70933",    )
    donor_eligibility_date = HL7Field[DTM | str](
        position=11,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    process_interruption = HL7Field[CNE | str](
        position=12,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70923",    )
    process_interruption_reason = HL7Field[CNE | str](
        position=13,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70935",    )
    phlebotomy_issue = HL7Field[list[CNE] | CNE | list[str] | str](
        position=14,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=True, table="HL70925",    )
    intended_recipient_blood_relative = HL7Field[ID | str](
        position=15,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70136",    )
    intended_recipient_name = HL7Field[XPN | str](
        position=16,
        datatype="XPN",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    intended_recipient_dob = HL7Field[DTM | str](
        position=17,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    intended_recipient_facility = HL7Field[XON | str](
        position=18,
        datatype="XON",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    intended_recipient_procedure_date = HL7Field[DTM | str](
        position=19,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    intended_recipient_ordering_provider = HL7Field[XPN | str](
        position=20,
        datatype="XPN",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    phlebotomy_status = HL7Field[CNE | str](
        position=21,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70926",    )
    arm_stick = HL7Field[CNE | str](
        position=22,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70927",    )
    bleed_start_phlebotomist = HL7Field[XPN | str](
        position=23,
        datatype="XPN",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    bleed_end_phlebotomist = HL7Field[XPN | str](
        position=24,
        datatype="XPN",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    aphaeresis_type_machine = HL7Field[ST | str](
        position=25,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    aphaeresis_machine_serial_number = HL7Field[ST | str](
        position=26,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    donor_reaction = HL7Field[ID | str](
        position=27,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70136",    )
    final_review_staff_id = HL7Field[XPN | str](
        position=28,
        datatype="XPN",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    final_review_date_time = HL7Field[DTM | str](
        position=29,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    number_of_tubes_collected = HL7Field[NM | str](
        position=30,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    donation_sample_identifier = HL7Field[list[EI] | EI | list[str] | str](
        position=31,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=True,    )
    donation_accept_staff = HL7Field[XCN | str](
        position=32,
        datatype="XCN",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    donation_material_review_staff = HL7Field[list[XCN] | XCN | list[str] | str](
        position=33,
        datatype="XCN",
        usage=Usage.REQUIRED,
        repeatable=True,    )
    action_code = HL7Field[ID | str | None](
        position=34,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class DPS(HL7Segment):
    _segment_id = "DPS"

    diagnosis_code_mcp = HL7Field[CWE | str](
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70051",    )
    procedure_code = HL7Field[list[CWE] | CWE | list[str] | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=True, table="HL70941",    )
    effective_date_time = HL7Field[DTM | str | None](
        position=3,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    expiration_date_time = HL7Field[DTM | str | None](
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    type_of_limitation = HL7Field[CNE | str | None](
        position=5,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70940",    )

class DRG(HL7Segment):
    _segment_id = "DRG"

    diagnostic_related_group = HL7Field[CNE | str | None](
        position=1,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70055",    )
    drg_assigned_date_time = HL7Field[DTM | str | None](
        position=2,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    drg_approval_indicator = HL7Field[ID | str | None](
        position=3,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    drg_grouper_review_code = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70056",    )
    outlier_type = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70083",    )
    outlier_days = HL7Field[NM | str | None](
        position=6,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    outlier_cost = HL7Field[CP | str | None](
        position=7,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    drg_payor = HL7Field[CWE | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70229",    )
    outlier_reimbursement = HL7Field[CP | str | None](
        position=9,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    confidential_indicator = HL7Field[ID | str | None](
        position=10,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    drg_transfer_type = HL7Field[CWE | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70415",    )
    name_of_coder = HL7Field[XPN | str | None](
        position=12,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    grouper_status = HL7Field[CWE | str | None](
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70734",    )
    pccl_value_code = HL7Field[CWE | str | None](
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70728",    )
    effective_weight = HL7Field[NM | str | None](
        position=15,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    monetary_amount = HL7Field[MO | str | None](
        position=16,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    status_patient = HL7Field[CWE | str | None](
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70739",    )
    grouper_software_name = HL7Field[ST | str | None](
        position=18,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    grouper_software_version = HL7Field[ST | str | None](
        position=19,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    status_financial_calculation = HL7Field[CWE | str | None](
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70742",    )
    relative_discount_surcharge = HL7Field[MO | str | None](
        position=21,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    basic_charge = HL7Field[MO | str | None](
        position=22,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    total_charge = HL7Field[MO | str | None](
        position=23,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    discount_surcharge = HL7Field[MO | str | None](
        position=24,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    calculated_days = HL7Field[NM | str | None](
        position=25,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    status_gender = HL7Field[CWE | str | None](
        position=26,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70749",    )
    status_age = HL7Field[CWE | str | None](
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70749",    )
    status_length_of_stay = HL7Field[CWE | str | None](
        position=28,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70749",    )
    status_same_day_flag = HL7Field[CWE | str | None](
        position=29,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70749",    )
    status_separation_mode = HL7Field[CWE | str | None](
        position=30,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70749",    )
    status_weight_at_birth = HL7Field[CWE | str | None](
        position=31,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70755",    )
    status_respiration_minutes = HL7Field[CWE | str | None](
        position=32,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70757",    )
    status_admission = HL7Field[CWE | str | None](
        position=33,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70759",    )

class DSC(HL7Segment):
    _segment_id = "DSC"

    continuation_pointer = HL7Field[ST | str | None](
        position=1,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    continuation_style = HL7Field[ID | str | None](
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70398",    )

class DSP(HL7Segment):
    _segment_id = "DSP"

    set_id_dsp = HL7Field[SI | str | None](
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    display_level = HL7Field[SI | str | None](
        position=2,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    data_line = HL7Field[TX | str](
        position=3,
        datatype="TX",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    logical_break_point = HL7Field[ST | str | None](
        position=4,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    result_id = HL7Field[TX | str | None](
        position=5,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class DST(HL7Segment):
    _segment_id = "DST"

    destination = HL7Field[CWE | str](
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70943",    )
    route = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70944",    )

class ECD(HL7Segment):
    _segment_id = "ECD"

    reference_command_number = HL7Field[NM | str](
        position=1,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    remote_control_command = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70368",    )
    response_required = HL7Field[ID | str | None](
        position=3,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    parameters = HL7Field[list[TX] | TX | list[str] | str | None](
        position=5,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=True,    )

class ECR(HL7Segment):
    _segment_id = "ECR"

    command_response = HL7Field[CWE | str](
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70387",    )
    date_time_completed = HL7Field[DTM | str](
        position=2,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    command_response_parameters = HL7Field[list[TX] | TX | list[str] | str | None](
        position=3,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=True,    )

class EDU(HL7Segment):
    _segment_id = "EDU"

    set_id_edu = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    academic_degree = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70360",    )
    academic_degree_program_date_range = HL7Field[DR | str | None](
        position=3,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    academic_degree_program_participation_date_range = HL7Field[DR | str | None](
        position=4,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    academic_degree_granted_date = HL7Field[DT | str | None](
        position=5,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    school = HL7Field[XON | str | None](
        position=6,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    school_type_code = HL7Field[CWE | str | None](
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70402",    )
    school_address = HL7Field[XAD | str | None](
        position=8,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    major_field_of_study = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,    )

class EQP(HL7Segment):
    _segment_id = "EQP"

    event_type = HL7Field[CWE | str](
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70450",    )
    file_name = HL7Field[ST | str | None](
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    start_date_time = HL7Field[DTM | str](
        position=3,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    end_date_time = HL7Field[DTM | str | None](
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    transaction_data = HL7Field[FT | str](
        position=5,
        datatype="FT",
        usage=Usage.REQUIRED,
        repeatable=False,    )

class EQU(HL7Segment):
    _segment_id = "EQU"

    equipment_instance_identifier = HL7Field[list[EI] | EI | list[str] | str](
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=True,    )
    event_date_time = HL7Field[DTM | str](
        position=2,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    equipment_state = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70365",    )
    local_remote_control_state = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70366",    )
    alert_level = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70367",    )
    expected_datetime_of_the_next_status_change = HL7Field[DTM | str | None](
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class ERR(HL7Segment):
    _segment_id = "ERR"

    error_location = HL7Field[list[ERL] | ERL | list[str] | str | None](
        position=2,
        datatype="ERL",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    hl7_error_code = HL7Field[CWE | str](
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70357",    )
    severity = HL7Field[ID | str](
        position=4,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70516",    )
    application_error_code = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70533",    )
    application_error_parameter = HL7Field[ST | str | None](
        position=6,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    diagnostic_information = HL7Field[TX | str | None](
        position=7,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    user_message = HL7Field[TX | str | None](
        position=8,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inform_person_indicator = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70517",    )
    override_type = HL7Field[CWE | str | None](
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70518",    )
    override_reason_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70519",    )
    help_desk_contact_point = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=12,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )

class EVN(HL7Segment):
    _segment_id = "EVN"

    recorded_date_time = HL7Field[DTM | str](
        position=2,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    date_time_planned_event = HL7Field[DTM | str | None](
        position=3,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    event_reason_code = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70062",    )
    operator_id = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=5,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70188",    )
    event_occurred = HL7Field[DTM | str | None](
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    event_facility = HL7Field[HD | str | None](
        position=7,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class FAC(HL7Segment):
    _segment_id = "FAC"

    facility_id_fac = HL7Field[EI | str](
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    facility_type = HL7Field[ID | str | None](
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70331",    )
    facility_address = HL7Field[list[XAD] | XAD | list[str] | str](
        position=3,
        datatype="XAD",
        usage=Usage.REQUIRED,
        repeatable=True,    )
    facility_telecommunication = HL7Field[XTN | str](
        position=4,
        datatype="XTN",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    contact_person = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=5,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    contact_title = HL7Field[list[ST] | ST | list[str] | str | None](
        position=6,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    contact_address = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=7,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    contact_telecommunication = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=8,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    signature_authority = HL7Field[list[XCN] | XCN | list[str] | str](
        position=9,
        datatype="XCN",
        usage=Usage.REQUIRED,
        repeatable=True,    )
    signature_authority_title = HL7Field[ST | str | None](
        position=10,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    signature_authority_address = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=11,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    signature_authority_telecommunication = HL7Field[XTN | str | None](
        position=12,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class FHS(HL7Segment):
    _segment_id = "FHS"

    file_field_separator = HL7Field[ST | str](
        position=1,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    file_encoding_characters = HL7Field[ST | str](
        position=2,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    file_sending_application = HL7Field[HD | str | None](
        position=3,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    file_sending_facility = HL7Field[HD | str | None](
        position=4,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    file_receiving_application = HL7Field[HD | str | None](
        position=5,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    file_receiving_facility = HL7Field[HD | str | None](
        position=6,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    file_creation_date_time = HL7Field[DTM | str | None](
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    file_security = HL7Field[ST | str | None](
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    file_name_id = HL7Field[ST | str | None](
        position=9,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    file_header_comment = HL7Field[ST | str | None](
        position=10,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    file_control_id = HL7Field[ST | str | None](
        position=11,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    reference_file_control_id = HL7Field[ST | str | None](
        position=12,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    file_sending_network_address = HL7Field[HD | str | None](
        position=13,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    file_receiving_network_address = HL7Field[HD | str | None](
        position=14,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    security_classification_tag = HL7Field[CWE | str | None](
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70952",    )
    security_handling_instructions = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70953",    )
    special_access_restriction_instructions = HL7Field[list[ST] | ST | list[str] | str | None](
        position=17,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )

class FT1(HL7Segment):
    _segment_id = "FT1"

    set_id_ft1 = HL7Field[SI | str | None](
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    transaction_id = HL7Field[CX | str | None](
        position=2,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    transaction_batch_id = HL7Field[ST | str | None](
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    transaction_date = HL7Field[DR | str](
        position=4,
        datatype="DR",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    transaction_posting_date = HL7Field[DTM | str | None](
        position=5,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    transaction_type = HL7Field[CWE | str](
        position=6,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70017",    )
    transaction_code = HL7Field[CWE | str](
        position=7,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70132",    )
    transaction_quantity = HL7Field[NM | str | None](
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    transaction_amount_extended = HL7Field[CP | str | None](
        position=11,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    transaction_amount_unit = HL7Field[CP | str | None](
        position=12,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    department_code = HL7Field[CWE | str | None](
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70049",    )
    health_plan_id = HL7Field[CWE | str | None](
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70072",    )
    insurance_amount = HL7Field[CP | str | None](
        position=15,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    assigned_patient_location = HL7Field[PL | str | None](
        position=16,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    fee_schedule = HL7Field[CWE | str | None](
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70024",    )
    patient_type = HL7Field[CWE | str | None](
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70018",    )
    diagnosis_code_ft1 = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=19,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70051",    )
    performed_by_code = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=20,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70084",    )
    ordered_by_code = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=21,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    unit_cost = HL7Field[CP | str | None](
        position=22,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    filler_order_number = HL7Field[EI | str | None](
        position=23,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    entered_by_code = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=24,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    procedure_code = HL7Field[CNE | str | None](
        position=25,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70088",    )
    procedure_code_modifier = HL7Field[list[CNE] | CNE | list[str] | str | None](
        position=26,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70340",    )
    advanced_beneficiary_notice_code = HL7Field[CWE | str | None](
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70339",    )
    medically_necessary_duplicate_procedure_reason = HL7Field[CWE | str | None](
        position=28,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70476",    )
    ndc_code = HL7Field[CWE | str | None](
        position=29,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70549",    )
    payment_reference_id = HL7Field[CX | str | None](
        position=30,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    transaction_reference_key = HL7Field[list[SI] | SI | list[str] | str | None](
        position=31,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    performing_facility = HL7Field[list[XON] | XON | list[str] | str | None](
        position=32,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    ordering_facility = HL7Field[XON | str | None](
        position=33,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    item_number = HL7Field[CWE | str | None](
        position=34,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    model_number = HL7Field[ST | str | None](
        position=35,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    special_processing_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=36,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    clinic_code = HL7Field[CWE | str | None](
        position=37,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    referral_number = HL7Field[CX | str | None](
        position=38,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    authorization_number = HL7Field[CX | str | None](
        position=39,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    service_provider_taxonomy_code = HL7Field[CWE | str | None](
        position=40,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    revenue_code = HL7Field[CWE | str | None](
        position=41,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70456",    )
    prescription_number = HL7Field[ST | str | None](
        position=42,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    ndc_qty_and_uom = HL7Field[CQ | str | None](
        position=43,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    dme_certificate_of_medical_necessity_transmission_code = HL7Field[CWE | str | None](
        position=44,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    dme_certification_type_code = HL7Field[CWE | str | None](
        position=45,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    dme_duration_value = HL7Field[NM | str | None](
        position=46,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    dme_certification_revision_date = HL7Field[DT | str | None](
        position=47,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    dme_initial_certification_date = HL7Field[DT | str | None](
        position=48,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    dme_last_certification_date = HL7Field[DT | str | None](
        position=49,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    dme_length_of_medical_necessity_days = HL7Field[NM | str | None](
        position=50,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    dme_rental_price = HL7Field[MO | str | None](
        position=51,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    dme_purchase_price = HL7Field[MO | str | None](
        position=52,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    dme_frequency_code = HL7Field[CWE | str | None](
        position=53,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    dme_certification_condition_indicator = HL7Field[ID | str | None](
        position=54,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    dme_condition_indicator_code = HL7Field[CWE | str | None](
        position=55,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    service_reason_code = HL7Field[CWE | str | None](
        position=56,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70964",    )

class FTS(HL7Segment):
    _segment_id = "FTS"

    file_batch_count = HL7Field[NM | str | None](
        position=1,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    file_trailer_comment = HL7Field[ST | str | None](
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class GOL(HL7Segment):
    _segment_id = "GOL"

    action_code = HL7Field[ID | str](
        position=1,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    action_date_time = HL7Field[DTM | str](
        position=2,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    goal_id = HL7Field[CWE | str](
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    goal_instance_id = HL7Field[EI | str](
        position=4,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    episode_of_care_id = HL7Field[EI | str | None](
        position=5,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    goal_list_priority = HL7Field[NM | str | None](
        position=6,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    goal_established_date_time = HL7Field[DTM | str | None](
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    expected_goal_achieve_date_time = HL7Field[DTM | str | None](
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    goal_classification = HL7Field[CWE | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    goal_management_discipline = HL7Field[CWE | str | None](
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    current_goal_review_status = HL7Field[CWE | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    current_goal_review_date_time = HL7Field[DTM | str | None](
        position=12,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    next_goal_review_date_time = HL7Field[DTM | str | None](
        position=13,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    previous_goal_review_date_time = HL7Field[DTM | str | None](
        position=14,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    goal_evaluation = HL7Field[CWE | str | None](
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    goal_evaluation_comment = HL7Field[list[ST] | ST | list[str] | str | None](
        position=17,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    goal_life_cycle_status = HL7Field[CWE | str | None](
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    goal_life_cycle_status_date_time = HL7Field[DTM | str | None](
        position=19,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    goal_target_type = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    goal_target_name = HL7Field[list[XPN] | XPN | list[str] | str | None](
        position=21,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    mood_code = HL7Field[CNE | str | None](
        position=22,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70725",    )

class GP1(HL7Segment):
    _segment_id = "GP1"

    type_of_bill_code = HL7Field[CWE | str](
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70455",    )
    revenue_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70456",    )
    overall_claim_disposition_code = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70457",    )
    oce_edits_per_visit_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70458",    )
    outlier_cost = HL7Field[CP | str | None](
        position=5,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class GP2(HL7Segment):
    _segment_id = "GP2"

    revenue_code = HL7Field[CWE | str | None](
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70456",    )
    number_of_service_units = HL7Field[NM | str | None](
        position=2,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    charge = HL7Field[CP | str | None](
        position=3,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    reimbursement_action_code = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70459",    )
    denial_or_rejection_code = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70460",    )
    oce_edit_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70458",    )
    ambulatory_payment_classification_code = HL7Field[CWE | str | None](
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70466",    )
    modifier_edit_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70467",    )
    payment_adjustment_code = HL7Field[CWE | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70468",    )
    packaging_status_code = HL7Field[CWE | str | None](
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70469",    )
    expected_cms_payment_amount = HL7Field[CP | str | None](
        position=11,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    reimbursement_type_code = HL7Field[CWE | str | None](
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70470",    )
    co_pay_amount = HL7Field[CP | str | None](
        position=13,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    pay_rate_per_service_unit = HL7Field[NM | str | None](
        position=14,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class GT1(HL7Segment):
    _segment_id = "GT1"

    set_id_gt1 = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    guarantor_number = HL7Field[list[CX] | CX | list[str] | str | None](
        position=2,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    guarantor_name = HL7Field[list[XPN] | XPN | list[str] | str](
        position=3,
        datatype="XPN",
        usage=Usage.REQUIRED,
        repeatable=True,    )
    guarantor_spouse_name = HL7Field[list[XPN] | XPN | list[str] | str | None](
        position=4,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    guarantor_address = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=5,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    guarantor_ph_num_home = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=6,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    guarantor_ph_num_business = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=7,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    guarantor_date_time_of_birth = HL7Field[DTM | str | None](
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    guarantor_administrative_sex = HL7Field[CWE | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70001",    )
    guarantor_type = HL7Field[CWE | str | None](
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70068",    )
    guarantor_relationship = HL7Field[CWE | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70063",    )
    guarantor_ssn = HL7Field[ST | str | None](
        position=12,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    guarantor_date_begin = HL7Field[DT | str | None](
        position=13,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    guarantor_date_end = HL7Field[DT | str | None](
        position=14,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    guarantor_priority = HL7Field[NM | str | None](
        position=15,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    guarantor_employer_name = HL7Field[list[XPN] | XPN | list[str] | str | None](
        position=16,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    guarantor_employer_address = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=17,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    guarantor_employer_phone_number = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=18,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    guarantor_employee_id_number = HL7Field[list[CX] | CX | list[str] | str | None](
        position=19,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    guarantor_employment_status = HL7Field[CWE | str | None](
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70066",    )
    guarantor_organization_name = HL7Field[list[XON] | XON | list[str] | str | None](
        position=21,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    guarantor_billing_hold_flag = HL7Field[ID | str | None](
        position=22,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    guarantor_credit_rating_code = HL7Field[CWE | str | None](
        position=23,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70341",    )
    guarantor_death_date_and_time = HL7Field[DTM | str | None](
        position=24,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    guarantor_death_flag = HL7Field[ID | str | None](
        position=25,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    guarantor_charge_adjustment_code = HL7Field[CWE | str | None](
        position=26,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70218",    )
    guarantor_household_annual_income = HL7Field[CP | str | None](
        position=27,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    guarantor_household_size = HL7Field[NM | str | None](
        position=28,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    guarantor_employer_id_number = HL7Field[list[CX] | CX | list[str] | str | None](
        position=29,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    guarantor_marital_status_code = HL7Field[CWE | str | None](
        position=30,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70002",    )
    guarantor_hire_effective_date = HL7Field[DT | str | None](
        position=31,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    employment_stop_date = HL7Field[DT | str | None](
        position=32,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    living_dependency = HL7Field[CWE | str | None](
        position=33,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70223",    )
    ambulatory_status = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=34,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70009",    )
    citizenship = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=35,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70171",    )
    primary_language = HL7Field[CWE | str | None](
        position=36,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70296",    )
    living_arrangement = HL7Field[CWE | str | None](
        position=37,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70220",    )
    publicity_code = HL7Field[CWE | str | None](
        position=38,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70215",    )
    protection_indicator = HL7Field[ID | str | None](
        position=39,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    student_indicator = HL7Field[CWE | str | None](
        position=40,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70231",    )
    religion = HL7Field[CWE | str | None](
        position=41,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70006",    )
    mothers_maiden_name = HL7Field[list[XPN] | XPN | list[str] | str | None](
        position=42,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    nationality = HL7Field[CWE | str | None](
        position=43,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70212",    )
    ethnic_group = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=44,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70189",    )
    contact_persons_name = HL7Field[list[XPN] | XPN | list[str] | str | None](
        position=45,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    contact_persons_telephone_number = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=46,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    contact_reason = HL7Field[CWE | str | None](
        position=47,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70222",    )
    contact_relationship = HL7Field[CWE | str | None](
        position=48,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70063",    )
    job_title = HL7Field[ST | str | None](
        position=49,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    job_code_class = HL7Field[JCC | str | None](
        position=50,
        datatype="JCC",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    guarantor_employers_organization_name = HL7Field[list[XON] | XON | list[str] | str | None](
        position=51,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    handicap = HL7Field[CWE | str | None](
        position=52,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70295",    )
    job_status = HL7Field[CWE | str | None](
        position=53,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70311",    )
    guarantor_financial_class = HL7Field[FC | str | None](
        position=54,
        datatype="FC",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    guarantor_race = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=55,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70005",    )
    guarantor_birth_place = HL7Field[ST | str | None](
        position=56,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    vip_indicator = HL7Field[CWE | str | None](
        position=57,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70099",    )

class Hxx(HL7Segment):
    _segment_id = "Hxx"

    pass

class IAM(HL7Segment):
    _segment_id = "IAM"

    set_id_iam = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    allergen_type_code = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70127",    )
    allergen_code_mnemonic_description = HL7Field[CWE | str](
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    allergy_severity_code = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70128",    )
    allergy_reaction_code = HL7Field[list[ST] | ST | list[str] | str | None](
        position=5,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    allergy_action_code = HL7Field[CNE | str](
        position=6,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70206",    )
    allergy_unique_identifier = HL7Field[EI | str | None](
        position=7,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    action_reason = HL7Field[ST | str | None](
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    sensitivity_to_causative_agent_code = HL7Field[CWE | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70436",    )
    allergen_group_code_mnemonic_description = HL7Field[CWE | str | None](
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    onset_date = HL7Field[DT | str | None](
        position=11,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    onset_date_text = HL7Field[ST | str | None](
        position=12,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    reported_date_time = HL7Field[DTM | str | None](
        position=13,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    reported_by = HL7Field[XPN | str | None](
        position=14,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    relationship_to_patient_code = HL7Field[CWE | str | None](
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70063",    )
    alert_device_code = HL7Field[CWE | str | None](
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70437",    )
    allergy_clinical_status_code = HL7Field[CWE | str | None](
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70438",    )
    statused_by_person = HL7Field[XCN | str | None](
        position=18,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    statused_by_organization = HL7Field[XON | str | None](
        position=19,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    statused_at_date_time = HL7Field[DTM | str | None](
        position=20,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inactivated_by_person = HL7Field[XCN | str | None](
        position=21,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inactivated_date_time = HL7Field[DTM | str | None](
        position=22,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    initially_recorded_by_person = HL7Field[XCN | str | None](
        position=23,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    initially_recorded_date_time = HL7Field[DTM | str | None](
        position=24,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    modified_by_person = HL7Field[XCN | str | None](
        position=25,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    modified_date_time = HL7Field[DTM | str | None](
        position=26,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    clinician_identified_code = HL7Field[CWE | str | None](
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    initially_recorded_by_organization = HL7Field[XON | str | None](
        position=28,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    modified_by_organization = HL7Field[XON | str | None](
        position=29,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inactivated_by_organization = HL7Field[XON | str | None](
        position=30,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class IAR(HL7Segment):
    _segment_id = "IAR"

    allergy_reaction_code = HL7Field[CWE | str](
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    allergy_severity_code = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70128",    )
    sensitivity_to_causative_agent_code = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70436",    )
    management = HL7Field[ST | str | None](
        position=4,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class IIM(HL7Segment):
    _segment_id = "IIM"

    primary_key_value_iim = HL7Field[CWE | str](
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    service_item_code = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    inventory_lot_number = HL7Field[ST | str | None](
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inventory_expiration_date = HL7Field[DTM | str | None](
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inventory_manufacturer_name = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inventory_location = HL7Field[CWE | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inventory_received_date = HL7Field[DTM | str | None](
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inventory_received_quantity = HL7Field[NM | str | None](
        position=8,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inventory_received_quantity_unit = HL7Field[CWE | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inventory_received_item_cost = HL7Field[MO | str | None](
        position=10,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inventory_on_hand_date = HL7Field[DTM | str | None](
        position=11,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inventory_on_hand_quantity = HL7Field[NM | str | None](
        position=12,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inventory_on_hand_quantity_unit = HL7Field[CWE | str | None](
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    procedure_code = HL7Field[CNE | str | None](
        position=14,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70088",    )
    procedure_code_modifier = HL7Field[list[CNE] | CNE | list[str] | str | None](
        position=15,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70340",    )

class ILT(HL7Segment):
    _segment_id = "ILT"

    set_id_ilt = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    inventory_lot_number = HL7Field[ST | str](
        position=2,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    inventory_expiration_date = HL7Field[DTM | str | None](
        position=3,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inventory_received_date = HL7Field[DTM | str | None](
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inventory_received_quantity = HL7Field[NM | str | None](
        position=5,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inventory_received_quantity_unit = HL7Field[CWE | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inventory_received_item_cost = HL7Field[MO | str | None](
        position=7,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inventory_on_hand_date = HL7Field[DTM | str | None](
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inventory_on_hand_quantity = HL7Field[NM | str | None](
        position=9,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inventory_on_hand_quantity_unit = HL7Field[CWE | str | None](
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class IN1(HL7Segment):
    _segment_id = "IN1"

    set_id_in1 = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    health_plan_id = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70072",    )
    insurance_company_id = HL7Field[list[CX] | CX | list[str] | str](
        position=3,
        datatype="CX",
        usage=Usage.REQUIRED,
        repeatable=True,    )
    insurance_company_name = HL7Field[list[XON] | XON | list[str] | str | None](
        position=4,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    insurance_company_address = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=5,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    insurance_co_contact_person = HL7Field[list[XPN] | XPN | list[str] | str | None](
        position=6,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    insurance_co_phone_number = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=7,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    group_number = HL7Field[ST | str | None](
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    group_name = HL7Field[list[XON] | XON | list[str] | str | None](
        position=9,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    insureds_group_emp_id = HL7Field[list[CX] | CX | list[str] | str | None](
        position=10,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    insureds_group_emp_name = HL7Field[list[XON] | XON | list[str] | str | None](
        position=11,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    plan_effective_date = HL7Field[DT | str | None](
        position=12,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    plan_expiration_date = HL7Field[DT | str | None](
        position=13,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    authorization_information = HL7Field[AUI | str | None](
        position=14,
        datatype="AUI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    plan_type = HL7Field[CWE | str | None](
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70086",    )
    name_of_insured = HL7Field[list[XPN] | XPN | list[str] | str | None](
        position=16,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    insureds_relationship_to_patient = HL7Field[CWE | str | None](
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70063",    )
    insureds_date_of_birth = HL7Field[DTM | str | None](
        position=18,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    insureds_address = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=19,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    assignment_of_benefits = HL7Field[CWE | str | None](
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70135",    )
    coordination_of_benefits = HL7Field[CWE | str | None](
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70173",    )
    coord_of_ben_priority = HL7Field[ST | str | None](
        position=22,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    notice_of_admission_flag = HL7Field[ID | str | None](
        position=23,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    notice_of_admission_date = HL7Field[DT | str | None](
        position=24,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    report_of_eligibility_flag = HL7Field[ID | str | None](
        position=25,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    report_of_eligibility_date = HL7Field[DT | str | None](
        position=26,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    release_information_code = HL7Field[CWE | str | None](
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70093",    )
    pre_admit_cert_pac = HL7Field[ST | str | None](
        position=28,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    verification_date_time = HL7Field[DTM | str | None](
        position=29,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    verification_by = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=30,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    type_of_agreement_code = HL7Field[CWE | str | None](
        position=31,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70098",    )
    billing_status = HL7Field[CWE | str | None](
        position=32,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70022",    )
    lifetime_reserve_days = HL7Field[NM | str | None](
        position=33,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    delay_before_lr_day = HL7Field[NM | str | None](
        position=34,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    company_plan_code = HL7Field[CWE | str | None](
        position=35,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70042",    )
    policy_number = HL7Field[ST | str | None](
        position=36,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    policy_deductible = HL7Field[CP | str | None](
        position=37,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    policy_limit_days = HL7Field[NM | str | None](
        position=39,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    insureds_employment_status = HL7Field[CWE | str | None](
        position=42,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70066",    )
    insureds_administrative_sex = HL7Field[CWE | str | None](
        position=43,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70001",    )
    insureds_employers_address = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=44,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    verification_status = HL7Field[ST | str | None](
        position=45,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    prior_insurance_plan_id = HL7Field[CWE | str | None](
        position=46,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70072",    )
    coverage_type = HL7Field[CWE | str | None](
        position=47,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70309",    )
    handicap = HL7Field[CWE | str | None](
        position=48,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70295",    )
    insureds_id_number = HL7Field[list[CX] | CX | list[str] | str | None](
        position=49,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    signature_code = HL7Field[CWE | str | None](
        position=50,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70535",    )
    signature_code_date = HL7Field[DT | str | None](
        position=51,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    insureds_birth_place = HL7Field[ST | str | None](
        position=52,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    vip_indicator = HL7Field[CWE | str | None](
        position=53,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70099",    )
    external_health_plan_identifiers = HL7Field[list[CX] | CX | list[str] | str | None](
        position=54,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    insurance_action_code = HL7Field[ID | str | None](
        position=55,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70206",    )

class IN2(HL7Segment):
    _segment_id = "IN2"

    insureds_employee_id = HL7Field[list[CX] | CX | list[str] | str | None](
        position=1,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    insureds_social_security_number = HL7Field[ST | str | None](
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    insureds_employers_name_and_id = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=3,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    employer_information_data = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70139",    )
    mail_claim_party = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70137",    )
    medicare_health_ins_card_number = HL7Field[ST | str | None](
        position=6,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    medicaid_case_name = HL7Field[list[XPN] | XPN | list[str] | str | None](
        position=7,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    medicaid_case_number = HL7Field[ST | str | None](
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    military_sponsor_name = HL7Field[list[XPN] | XPN | list[str] | str | None](
        position=9,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    military_id_number = HL7Field[ST | str | None](
        position=10,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    dependent_of_military_recipient = HL7Field[CWE | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70342",    )
    military_organization = HL7Field[ST | str | None](
        position=12,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    military_station = HL7Field[ST | str | None](
        position=13,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    military_service = HL7Field[CWE | str | None](
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70140",    )
    military_rank_grade = HL7Field[CWE | str | None](
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70141",    )
    military_status = HL7Field[CWE | str | None](
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70142",    )
    military_retire_date = HL7Field[DT | str | None](
        position=17,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    military_non_avail_cert_on_file = HL7Field[ID | str | None](
        position=18,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    baby_coverage = HL7Field[ID | str | None](
        position=19,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    combine_baby_bill = HL7Field[ID | str | None](
        position=20,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    blood_deductible = HL7Field[ST | str | None](
        position=21,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    special_coverage_approval_name = HL7Field[list[XPN] | XPN | list[str] | str | None](
        position=22,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    special_coverage_approval_title = HL7Field[ST | str | None](
        position=23,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    non_covered_insurance_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70143",    )
    payor_id = HL7Field[list[CX] | CX | list[str] | str | None](
        position=25,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    payor_subscriber_id = HL7Field[list[CX] | CX | list[str] | str | None](
        position=26,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    eligibility_source = HL7Field[CWE | str | None](
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70144",    )
    room_coverage_type_amount = HL7Field[list[RMC] | RMC | list[str] | str | None](
        position=28,
        datatype="RMC",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    policy_type_amount = HL7Field[list[PTA] | PTA | list[str] | str | None](
        position=29,
        datatype="PTA",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    daily_deductible = HL7Field[DDI | str | None](
        position=30,
        datatype="DDI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    living_dependency = HL7Field[CWE | str | None](
        position=31,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70223",    )
    ambulatory_status = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=32,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70009",    )
    citizenship = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=33,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70171",    )
    primary_language = HL7Field[CWE | str | None](
        position=34,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70296",    )
    living_arrangement = HL7Field[CWE | str | None](
        position=35,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70220",    )
    publicity_code = HL7Field[CWE | str | None](
        position=36,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70215",    )
    protection_indicator = HL7Field[ID | str | None](
        position=37,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    student_indicator = HL7Field[CWE | str | None](
        position=38,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70231",    )
    religion = HL7Field[CWE | str | None](
        position=39,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70006",    )
    mothers_maiden_name = HL7Field[list[XPN] | XPN | list[str] | str | None](
        position=40,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    nationality = HL7Field[CWE | str | None](
        position=41,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70212",    )
    ethnic_group = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=42,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70189",    )
    marital_status = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=43,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70002",    )
    insureds_employment_start_date = HL7Field[DT | str | None](
        position=44,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    employment_stop_date = HL7Field[DT | str | None](
        position=45,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    job_title = HL7Field[ST | str | None](
        position=46,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    job_code_class = HL7Field[JCC | str | None](
        position=47,
        datatype="JCC",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    job_status = HL7Field[CWE | str | None](
        position=48,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70311",    )
    employer_contact_person_name = HL7Field[list[XPN] | XPN | list[str] | str | None](
        position=49,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    employer_contact_person_phone_number = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=50,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    employer_contact_reason = HL7Field[CWE | str | None](
        position=51,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70222",    )
    insureds_contact_persons_name = HL7Field[list[XPN] | XPN | list[str] | str | None](
        position=52,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    insureds_contact_person_phone_number = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=53,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    insureds_contact_person_reason = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=54,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70222",    )
    relationship_to_the_patient_start_date = HL7Field[DT | str | None](
        position=55,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    relationship_to_the_patient_stop_date = HL7Field[list[DT] | DT | list[str] | str | None](
        position=56,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    insurance_co_contact_reason = HL7Field[CWE | str | None](
        position=57,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70232",    )
    insurance_co_contact_phone_number = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=58,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    policy_scope = HL7Field[CWE | str | None](
        position=59,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70312",    )
    policy_source = HL7Field[CWE | str | None](
        position=60,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70313",    )
    patient_member_number = HL7Field[CX | str | None](
        position=61,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    guarantors_relationship_to_insured = HL7Field[CWE | str | None](
        position=62,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70063",    )
    insureds_phone_number_home = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=63,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    insureds_employer_phone_number = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=64,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    military_handicapped_program = HL7Field[CWE | str | None](
        position=65,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70343",    )
    suspend_flag = HL7Field[ID | str | None](
        position=66,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    copay_limit_flag = HL7Field[ID | str | None](
        position=67,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    stoploss_limit_flag = HL7Field[ID | str | None](
        position=68,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    insured_organization_name_and_id = HL7Field[list[XON] | XON | list[str] | str | None](
        position=69,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    insured_employer_organization_name_and_id = HL7Field[list[XON] | XON | list[str] | str | None](
        position=70,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    race = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=71,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70005",    )
    patients_relationship_to_insured = HL7Field[CWE | str | None](
        position=72,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70344",    )
    co_pay_amount = HL7Field[CP | str | None](
        position=73,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class IN3(HL7Segment):
    _segment_id = "IN3"

    set_id_in3 = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    certification_number = HL7Field[CX | str | None](
        position=2,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    certified_by = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=3,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    certification_required = HL7Field[ID | str | None](
        position=4,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    penalty = HL7Field[MOP | str | None](
        position=5,
        datatype="MOP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    certification_date_time = HL7Field[DTM | str | None](
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    certification_modify_date_time = HL7Field[DTM | str | None](
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    operator = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=8,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    certification_begin_date = HL7Field[DT | str | None](
        position=9,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    certification_end_date = HL7Field[DT | str | None](
        position=10,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    days = HL7Field[DTN | str | None](
        position=11,
        datatype="DTN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    non_concur_code_description = HL7Field[CWE | str | None](
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70233",    )
    non_concur_effective_date_time = HL7Field[DTM | str | None](
        position=13,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    physician_reviewer = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=14,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70010",    )
    certification_contact = HL7Field[ST | str | None](
        position=15,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    certification_contact_phone_number = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=16,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    appeal_reason = HL7Field[CWE | str | None](
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70345",    )
    certification_agency = HL7Field[CWE | str | None](
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70346",    )
    certification_agency_phone_number = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=19,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    pre_certification_requirement = HL7Field[list[ICD] | ICD | list[str] | str | None](
        position=20,
        datatype="ICD",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70136",    )
    case_manager = HL7Field[ST | str | None](
        position=21,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    second_opinion_date = HL7Field[DT | str | None](
        position=22,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    second_opinion_status = HL7Field[CWE | str | None](
        position=23,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70151",    )
    second_opinion_documentation_received = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70152",    )
    second_opinion_physician = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=25,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70010",    )
    certification_type = HL7Field[CWE | str | None](
        position=26,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70921",    )
    certification_category = HL7Field[CWE | str | None](
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70922",    )
    online_verification_date_time = HL7Field[DTM | str | None](
        position=28,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    online_verification_result = HL7Field[CWE | str | None](
        position=29,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70970",    )
    online_verification_result_error_code = HL7Field[CWE | str | None](
        position=30,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70971",    )
    online_verification_result_check_digit = HL7Field[ST | str | None](
        position=31,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class INV(HL7Segment):
    _segment_id = "INV"

    substance_identifier = HL7Field[CWE | str | None](
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70451",    )
    substance_status = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70383",    )
    substance_type = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70384",    )
    inventory_container_identifier = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70599",    )
    container_carrier_identifier = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70600",    )
    position_on_carrier = HL7Field[CWE | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70601",    )
    initial_quantity = HL7Field[NM | str | None](
        position=7,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    current_quantity = HL7Field[NM | str | None](
        position=8,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    available_quantity = HL7Field[NM | str | None](
        position=9,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    consumption_quantity = HL7Field[NM | str | None](
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    quantity_units = HL7Field[CWE | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70602",    )
    expiration_date_time = HL7Field[DTM | str | None](
        position=12,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    first_used_date_time = HL7Field[DTM | str | None](
        position=13,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    test_fluid_identifiers = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70603",    )
    manufacturer_lot_number = HL7Field[ST | str | None](
        position=16,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    manufacturer_identifier = HL7Field[CWE | str | None](
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70385",    )
    supplier_identifier = HL7Field[CWE | str | None](
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70386",    )
    on_board_stability_time = HL7Field[CQ | str | None](
        position=19,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    target_value = HL7Field[CQ | str | None](
        position=20,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    equipment_state_indicator_type_code = HL7Field[CWE | str | None](
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70942",    )
    equipment_state_indicator_value = HL7Field[CQ | str | None](
        position=22,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class IPC(HL7Segment):
    _segment_id = "IPC"

    accession_identifier = HL7Field[EI | str](
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    requested_procedure_id = HL7Field[EI | str](
        position=2,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    study_instance_uid = HL7Field[EI | str](
        position=3,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    scheduled_procedure_step_id = HL7Field[EI | str](
        position=4,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    modality = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70604",    )
    protocol_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70605",    )
    scheduled_station_name = HL7Field[EI | str | None](
        position=7,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    scheduled_procedure_step_location = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70606",    )
    scheduled_station_ae_title = HL7Field[ST | str | None](
        position=9,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    action_code = HL7Field[ID | str | None](
        position=10,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class IPR(HL7Segment):
    _segment_id = "IPR"

    ipr_identifier = HL7Field[EI | str](
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    provider_cross_reference_identifier = HL7Field[EI | str](
        position=2,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    payer_cross_reference_identifier = HL7Field[EI | str](
        position=3,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    ipr_status = HL7Field[CWE | str](
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70571",    )
    ipr_date_time = HL7Field[DTM | str](
        position=5,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    adjudicated_paid_amount = HL7Field[CP | str | None](
        position=6,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    expected_payment_date_time = HL7Field[DTM | str | None](
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    ipr_checksum = HL7Field[ST | str](
        position=8,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )

class ISD(HL7Segment):
    _segment_id = "ISD"

    reference_interaction_number = HL7Field[NM | str](
        position=1,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    interaction_type_identifier = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70368",    )
    interaction_active_state = HL7Field[CWE | str](
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70387",    )

class ITM(HL7Segment):
    _segment_id = "ITM"

    item_identifier = HL7Field[EI | str](
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    item_description = HL7Field[ST | str | None](
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    item_status = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70776",    )
    item_type = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70778",    )
    item_category = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    subject_to_expiration_indicator = HL7Field[CNE | str | None](
        position=6,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    manufacturer_identifier = HL7Field[EI | str | None](
        position=7,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    manufacturer_name = HL7Field[ST | str | None](
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    manufacturer_catalog_number = HL7Field[ST | str | None](
        position=9,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    manufacturer_labeler_identification_code = HL7Field[CWE | str | None](
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    patient_chargeable_indicator = HL7Field[CNE | str | None](
        position=11,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    transaction_code = HL7Field[CWE | str | None](
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70132",    )
    transaction_amount_unit = HL7Field[CP | str | None](
        position=13,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    stocked_item_indicator = HL7Field[CNE | str | None](
        position=14,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    supply_risk_codes = HL7Field[CWE | str | None](
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70871",    )
    approving_regulatory_agency = HL7Field[list[XON] | XON | list[str] | str | None](
        position=16,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70790",    )
    latex_indicator = HL7Field[CNE | str | None](
        position=17,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    ruling_act = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70793",    )
    item_natural_account_code = HL7Field[CWE | str | None](
        position=19,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70320",    )
    approved_to_buy_quantity = HL7Field[NM | str | None](
        position=20,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    approved_to_buy_price = HL7Field[MO | str | None](
        position=21,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    taxable_item_indicator = HL7Field[CNE | str | None](
        position=22,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    freight_charge_indicator = HL7Field[CNE | str | None](
        position=23,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    item_set_indicator = HL7Field[CNE | str | None](
        position=24,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    item_set_identifier = HL7Field[EI | str | None](
        position=25,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    track_department_usage_indicator = HL7Field[CNE | str | None](
        position=26,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    procedure_code = HL7Field[CNE | str | None](
        position=27,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70088",    )
    procedure_code_modifier = HL7Field[list[CNE] | CNE | list[str] | str | None](
        position=28,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70340",    )
    special_handling_code = HL7Field[CWE | str | None](
        position=29,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70376",    )
    hazardous_indicator = HL7Field[CNE | str | None](
        position=30,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    sterile_indicator = HL7Field[CNE | str | None](
        position=31,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    material_data_safety_sheet_number = HL7Field[EI | str | None](
        position=32,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    united_nations_standard_products_and_services_code_unspsc = HL7Field[CWE | str | None](
        position=33,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70396",    )
    contract_date = HL7Field[DR | str | None](
        position=34,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    manufacturer_contact_name = HL7Field[XPN | str | None](
        position=35,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    manufacturer_contact_information = HL7Field[XTN | str | None](
        position=36,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    class_of_trade = HL7Field[ST | str | None](
        position=37,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    field_level_event_code = HL7Field[ID | str | None](
        position=38,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70180",    )

class IVC(HL7Segment):
    _segment_id = "IVC"

    provider_invoice_number = HL7Field[EI | str](
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    payer_invoice_number = HL7Field[EI | str | None](
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    contract_agreement_number = HL7Field[EI | str | None](
        position=3,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    invoice_control = HL7Field[CWE | str](
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70553",    )
    invoice_reason = HL7Field[CWE | str](
        position=5,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70554",    )
    invoice_type = HL7Field[CWE | str](
        position=6,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70555",    )
    invoice_date_time = HL7Field[DTM | str](
        position=7,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    invoice_amount = HL7Field[CP | str](
        position=8,
        datatype="CP",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    payment_terms = HL7Field[ST | str | None](
        position=9,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    provider_organization = HL7Field[XON | str](
        position=10,
        datatype="XON",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    payer_organization = HL7Field[XON | str](
        position=11,
        datatype="XON",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    attention = HL7Field[XCN | str | None](
        position=12,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    last_invoice_indicator = HL7Field[ID | str | None](
        position=13,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    invoice_booking_period = HL7Field[DTM | str | None](
        position=14,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    origin = HL7Field[ST | str | None](
        position=15,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    invoice_fixed_amount = HL7Field[CP | str | None](
        position=16,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    special_costs = HL7Field[CP | str | None](
        position=17,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    amount_for_doctors_treatment = HL7Field[CP | str | None](
        position=18,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    responsible_physician = HL7Field[XCN | str | None](
        position=19,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    cost_center = HL7Field[CX | str | None](
        position=20,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    invoice_prepaid_amount = HL7Field[CP | str | None](
        position=21,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    total_invoice_amount_without_prepaid_amount = HL7Field[CP | str | None](
        position=22,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    total_amount_of_vat = HL7Field[CP | str | None](
        position=23,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    vat_rates_applied = HL7Field[list[NM] | NM | list[str] | str | None](
        position=24,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    benefit_group = HL7Field[CWE | str](
        position=25,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70556",    )
    provider_tax_id = HL7Field[ST | str | None](
        position=26,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    payer_tax_id = HL7Field[ST | str | None](
        position=27,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    provider_tax_status = HL7Field[CWE | str | None](
        position=28,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70572",    )
    payer_tax_status = HL7Field[CWE | str | None](
        position=29,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70572",    )
    sales_tax_id = HL7Field[ST | str | None](
        position=30,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class IVT(HL7Segment):
    _segment_id = "IVT"

    set_id_ivt = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    inventory_location_identifier = HL7Field[EI | str](
        position=2,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    inventory_location_name = HL7Field[ST | str | None](
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    source_location_identifier = HL7Field[EI | str | None](
        position=4,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    source_location_name = HL7Field[ST | str | None](
        position=5,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    item_status = HL7Field[CWE | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70625",    )
    bin_location_identifier = HL7Field[list[EI] | EI | list[str] | str | None](
        position=7,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    order_packaging = HL7Field[CWE | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70818",    )
    issue_packaging = HL7Field[CWE | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    default_inventory_asset_account = HL7Field[EI | str | None](
        position=10,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    patient_chargeable_indicator = HL7Field[CNE | str | None](
        position=11,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    transaction_code = HL7Field[CWE | str | None](
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70132",    )
    transaction_amount_unit = HL7Field[CP | str | None](
        position=13,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    item_importance_code = HL7Field[CWE | str | None](
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70634",    )
    stocked_item_indicator = HL7Field[CNE | str | None](
        position=15,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    consignment_item_indicator = HL7Field[CNE | str | None](
        position=16,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    reusable_item_indicator = HL7Field[CNE | str | None](
        position=17,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    reusable_cost = HL7Field[CP | str | None](
        position=18,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    substitute_item_identifier = HL7Field[list[EI] | EI | list[str] | str | None](
        position=19,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    latex_free_substitute_item_identifier = HL7Field[EI | str | None](
        position=20,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    recommended_reorder_theory = HL7Field[CWE | str | None](
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70642",    )
    recommended_safety_stock_days = HL7Field[NM | str | None](
        position=22,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    recommended_maximum_days_inventory = HL7Field[NM | str | None](
        position=23,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    recommended_order_point = HL7Field[NM | str | None](
        position=24,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    recommended_order_amount = HL7Field[NM | str | None](
        position=25,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    operating_room_par_level_indicator = HL7Field[CNE | str | None](
        position=26,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )

class LAN(HL7Segment):
    _segment_id = "LAN"

    set_id_lan = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    language_code = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70296",    )
    language_ability_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70403",    )
    language_proficiency_code = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70404",    )

class LCC(HL7Segment):
    _segment_id = "LCC"

    primary_key_value_lcc = HL7Field[PL | str](
        position=1,
        datatype="PL",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    location_department = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70264",    )
    accommodation_type = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70129",    )
    charge_code = HL7Field[list[CWE] | CWE | list[str] | str](
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=True, table="HL70132",    )

class LCH(HL7Segment):
    _segment_id = "LCH"

    primary_key_value_lch = HL7Field[PL | str](
        position=1,
        datatype="PL",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    segment_action_code = HL7Field[ID | str | None](
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70206",    )
    segment_unique_key = HL7Field[EI | str | None](
        position=3,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    location_characteristic_id = HL7Field[CWE | str](
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70324",    )
    location_characteristic_value_lch = HL7Field[CWE | str](
        position=5,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70136",    )

class LDP(HL7Segment):
    _segment_id = "LDP"

    primary_key_value_ldp = HL7Field[PL | str](
        position=1,
        datatype="PL",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    location_department = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70264",    )
    location_service = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70069",    )
    specialty_type = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70265",    )
    valid_patient_classes = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70004",    )
    active_inactive_flag = HL7Field[ID | str | None](
        position=6,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70183",    )
    activation_date_ldp = HL7Field[DTM | str | None](
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inactivation_date_ldp = HL7Field[DTM | str | None](
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inactivated_reason = HL7Field[ST | str | None](
        position=9,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    visiting_hours = HL7Field[list[VH] | VH | list[str] | str | None](
        position=10,
        datatype="VH",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70267",    )
    contact_phone = HL7Field[XTN | str | None](
        position=11,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    location_cost_center = HL7Field[CWE | str | None](
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70462",    )

class LOC(HL7Segment):
    _segment_id = "LOC"

    primary_key_value_loc = HL7Field[PL | str](
        position=1,
        datatype="PL",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    location_description = HL7Field[ST | str | None](
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    location_type_loc = HL7Field[list[CWE] | CWE | list[str] | str](
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=True, table="HL70260",    )
    organization_name_loc = HL7Field[list[XON] | XON | list[str] | str | None](
        position=4,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    location_address = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=5,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    location_phone = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=6,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    license_number = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70461",    )
    location_equipment = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70261",    )
    location_service_code = HL7Field[CWE | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70442",    )

class LRL(HL7Segment):
    _segment_id = "LRL"

    primary_key_value_lrl = HL7Field[PL | str](
        position=1,
        datatype="PL",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    segment_action_code = HL7Field[ID | str | None](
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70206",    )
    segment_unique_key = HL7Field[EI | str | None](
        position=3,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    location_relationship_id = HL7Field[CWE | str](
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70325",    )
    organizational_location_relationship_value = HL7Field[list[XON] | XON | list[str] | str | None](
        position=5,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    patient_location_relationship_value = HL7Field[PL | str | None](
        position=6,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class MCP(HL7Segment):
    _segment_id = "MCP"

    set_id_mcp = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    producers_service_test_observation_id = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    universal_service_price_range_low_value = HL7Field[MO | str | None](
        position=3,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    universal_service_price_range_high_value = HL7Field[MO | str | None](
        position=4,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    reason_for_universal_service_cost_range = HL7Field[ST | str | None](
        position=5,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class MFA(HL7Segment):
    _segment_id = "MFA"

    record_level_event_code = HL7Field[ID | str](
        position=1,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70180",    )
    mfn_control_id = HL7Field[ST | str | None](
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    event_completion_date_time = HL7Field[DTM | str | None](
        position=3,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    mfn_record_level_error_return = HL7Field[CWE | str](
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70181",    )
    primary_key_value_mfa = HL7Field[list[Varies] | Varies | list[str] | str](
        position=5,
        datatype="Varies",
        usage=Usage.REQUIRED,
        repeatable=True, table="HL70607",    )
    primary_key_value_type_mfa = HL7Field[list[ID] | ID | list[str] | str](
        position=6,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=True, table="HL70355",    )

class MFE(HL7Segment):
    _segment_id = "MFE"

    record_level_event_code = HL7Field[ID | str](
        position=1,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70180",    )
    mfn_control_id = HL7Field[ST | str | None](
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    effective_date_time = HL7Field[DTM | str | None](
        position=3,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    primary_key_value_mfe = HL7Field[list[Varies] | Varies | list[str] | str](
        position=4,
        datatype="Varies",
        usage=Usage.REQUIRED,
        repeatable=True, table="HL70608",    )
    primary_key_value_type = HL7Field[list[ID] | ID | list[str] | str](
        position=5,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=True, table="HL70355",    )
    entered_date_time = HL7Field[DTM | str | None](
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    entered_by = HL7Field[XCN | str | None](
        position=7,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class MFI(HL7Segment):
    _segment_id = "MFI"

    master_file_identifier = HL7Field[CWE | str](
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70175",    )
    master_file_application_identifier = HL7Field[list[HD] | HD | list[str] | str | None](
        position=2,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70361",    )
    file_level_event_code = HL7Field[ID | str](
        position=3,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70178",    )
    entered_date_time = HL7Field[DTM | str | None](
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    effective_date_time = HL7Field[DTM | str | None](
        position=5,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    response_level_code = HL7Field[ID | str](
        position=6,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70179",    )

class MRG(HL7Segment):
    _segment_id = "MRG"

    prior_patient_identifier_list = HL7Field[list[CX] | CX | list[str] | str](
        position=1,
        datatype="CX",
        usage=Usage.REQUIRED,
        repeatable=True, table="HL70061",    )
    prior_patient_account_number = HL7Field[CX | str | None](
        position=3,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70061",    )
    prior_visit_number = HL7Field[CX | str | None](
        position=5,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70061",    )
    prior_alternate_visit_id = HL7Field[list[CX] | CX | list[str] | str | None](
        position=6,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70061",    )
    prior_patient_name = HL7Field[list[XPN] | XPN | list[str] | str | None](
        position=7,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70200",    )

class MSA(HL7Segment):
    _segment_id = "MSA"

    acknowledgment_code = HL7Field[ID | str](
        position=1,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70008",    )
    message_control_id = HL7Field[ST | str](
        position=2,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    expected_sequence_number = HL7Field[NM | str | None](
        position=4,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    message_waiting_number = HL7Field[NM | str | None](
        position=7,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    message_waiting_priority = HL7Field[ID | str | None](
        position=8,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70520",    )

class MSH(HL7Segment):
    _segment_id = "MSH"

    field_separator = HL7Field[ST | str](
        position=1,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    encoding_characters = HL7Field[ST | str](
        position=2,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    sending_application = HL7Field[HD | str | None](
        position=3,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70361",    )
    sending_facility = HL7Field[HD | str | None](
        position=4,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70362",    )
    receiving_application = HL7Field[HD | str | None](
        position=5,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70361",    )
    receiving_facility = HL7Field[list[HD] | HD | list[str] | str | None](
        position=6,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70362",    )
    date_time_of_message = HL7Field[DTM | str](
        position=7,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    security = HL7Field[ST | str | None](
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    message_type = HL7Field[MSG | str](
        position=9,
        datatype="MSG",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    message_control_id = HL7Field[ST | str](
        position=10,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    processing_id = HL7Field[PT | str](
        position=11,
        datatype="PT",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    version_id = HL7Field[VID | str](
        position=12,
        datatype="VID",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    sequence_number = HL7Field[NM | str | None](
        position=13,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    continuation_pointer = HL7Field[ST | str | None](
        position=14,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    accept_acknowledgment = HL7Field[ID | str | None](
        position=15,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70155",    )
    application_acknowledgment_type = HL7Field[ID | str | None](
        position=16,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70155",    )
    country_code = HL7Field[ID | str | None](
        position=17,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70399",    )
    character_set = HL7Field[list[ID] | ID | list[str] | str | None](
        position=18,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70211",    )
    principal_language_of_message = HL7Field[CWE | str | None](
        position=19,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70609",    )
    alternate_character_set_handling_scheme = HL7Field[ID | str | None](
        position=20,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70356",    )
    message_profile_identifier = HL7Field[list[EI] | EI | list[str] | str | None](
        position=21,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    sending_responsible_organization = HL7Field[XON | str | None](
        position=22,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    receiving_responsible_organization = HL7Field[XON | str | None](
        position=23,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    sending_network_address = HL7Field[HD | str | None](
        position=24,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    receiving_network_address = HL7Field[HD | str | None](
        position=25,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    security_classification_tag = HL7Field[CWE | str | None](
        position=26,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70952",    )
    security_handling_instructions = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70953",    )
    special_access_restriction_instructions = HL7Field[list[ST] | ST | list[str] | str | None](
        position=28,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )

class NCK(HL7Segment):
    _segment_id = "NCK"

    system_date_time = HL7Field[DTM | str](
        position=1,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )

class NDS(HL7Segment):
    _segment_id = "NDS"

    notification_reference_number = HL7Field[NM | str](
        position=1,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    notification_date_time = HL7Field[DTM | str](
        position=2,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    notification_alert_severity = HL7Field[CWE | str](
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70367",    )
    notification_code = HL7Field[CWE | str](
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70610",    )

class NK1(HL7Segment):
    _segment_id = "NK1"

    set_id_nk1 = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    name = HL7Field[list[XPN] | XPN | list[str] | str | None](
        position=2,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70200",    )
    relationship = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70063",    )
    address = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=4,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    contact_role = HL7Field[CWE | str | None](
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70131",    )
    start_date = HL7Field[DT | str | None](
        position=8,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    end_date = HL7Field[DT | str | None](
        position=9,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    next_of_kin_associated_parties_job_title = HL7Field[ST | str | None](
        position=10,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    next_of_kin_associated_parties_job_code_class = HL7Field[JCC | str | None](
        position=11,
        datatype="JCC",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    next_of_kin_associated_parties_employee_number = HL7Field[CX | str | None](
        position=12,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    organization_name_nk1 = HL7Field[list[XON] | XON | list[str] | str | None](
        position=13,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    marital_status = HL7Field[CWE | str | None](
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70002",    )
    administrative_sex = HL7Field[CWE | str | None](
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70001",    )
    date_time_of_birth = HL7Field[DTM | str | None](
        position=16,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    living_dependency = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70223",    )
    ambulatory_status = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70009",    )
    citizenship = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=19,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70171",    )
    primary_language = HL7Field[CWE | str | None](
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70296",    )
    living_arrangement = HL7Field[CWE | str | None](
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70220",    )
    publicity_code = HL7Field[CWE | str | None](
        position=22,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70215",    )
    protection_indicator = HL7Field[ID | str | None](
        position=23,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    student_indicator = HL7Field[CWE | str | None](
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70231",    )
    religion = HL7Field[CWE | str | None](
        position=25,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70006",    )
    mothers_maiden_name = HL7Field[list[XPN] | XPN | list[str] | str | None](
        position=26,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    nationality = HL7Field[CWE | str | None](
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70212",    )
    ethnic_group = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=28,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70189",    )
    contact_reason = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=29,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70222",    )
    contact_persons_name = HL7Field[list[XPN] | XPN | list[str] | str | None](
        position=30,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    contact_persons_address = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=32,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    next_of_kin_associated_partys_identifiers = HL7Field[list[CX] | CX | list[str] | str | None](
        position=33,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    job_status = HL7Field[CWE | str | None](
        position=34,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70311",    )
    race = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=35,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70005",    )
    handicap = HL7Field[CWE | str | None](
        position=36,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70295",    )
    contact_person_social_security_number = HL7Field[ST | str | None](
        position=37,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    next_of_kin_birth_place = HL7Field[ST | str | None](
        position=38,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    vip_indicator = HL7Field[CWE | str | None](
        position=39,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70099",    )
    next_of_kin_telecommunication_information = HL7Field[XTN | str | None](
        position=40,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    contact_persons_telecommunication_information = HL7Field[XTN | str | None](
        position=41,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class NPU(HL7Segment):
    _segment_id = "NPU"

    bed_location = HL7Field[PL | str](
        position=1,
        datatype="PL",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    bed_status = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70116",    )

class NSC(HL7Segment):
    _segment_id = "NSC"

    application_change_type = HL7Field[CWE | str](
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70409",    )
    current_cpu = HL7Field[ST | str | None](
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    current_fileserver = HL7Field[ST | str | None](
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    current_application = HL7Field[HD | str | None](
        position=4,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70361",    )
    current_facility = HL7Field[HD | str | None](
        position=5,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70362",    )
    new_cpu = HL7Field[ST | str | None](
        position=6,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    new_fileserver = HL7Field[ST | str | None](
        position=7,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    new_application = HL7Field[HD | str | None](
        position=8,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70361",    )
    new_facility = HL7Field[HD | str | None](
        position=9,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70362",    )

class NST(HL7Segment):
    _segment_id = "NST"

    statistics_available = HL7Field[ID | str](
        position=1,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70136",    )
    source_identifier = HL7Field[ST | str | None](
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    source_type = HL7Field[ID | str | None](
        position=3,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70332",    )
    statistics_start = HL7Field[DTM | str | None](
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    statistics_end = HL7Field[DTM | str | None](
        position=5,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    receive_character_count = HL7Field[NM | str | None](
        position=6,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    send_character_count = HL7Field[NM | str | None](
        position=7,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    messages_received = HL7Field[NM | str | None](
        position=8,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    messages_sent = HL7Field[NM | str | None](
        position=9,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    checksum_errors_received = HL7Field[NM | str | None](
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    length_errors_received = HL7Field[NM | str | None](
        position=11,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    other_errors_received = HL7Field[NM | str | None](
        position=12,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    connect_timeouts = HL7Field[NM | str | None](
        position=13,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    receive_timeouts = HL7Field[NM | str | None](
        position=14,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    application_control_level_errors = HL7Field[NM | str | None](
        position=15,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class NTE(HL7Segment):
    _segment_id = "NTE"

    set_id_nte = HL7Field[SI | str | None](
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    source_of_comment = HL7Field[ID | str | None](
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70105",    )
    comment = HL7Field[list[FT] | FT | list[str] | str | None](
        position=3,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    comment_type = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70364",    )
    entered_by = HL7Field[XCN | str | None](
        position=5,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    entered_date_time = HL7Field[DTM | str | None](
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    effective_start_date = HL7Field[DTM | str | None](
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    expiration_date = HL7Field[DTM | str | None](
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    coded_comment = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70611",    )

class OBR(HL7Segment):
    _segment_id = "OBR"

    set_id_obr = HL7Field[SI | str | None](
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    placer_order_number = HL7Field[EI | str | None](
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    filler_order_number = HL7Field[EI | str | None](
        position=3,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    universal_service_identifier = HL7Field[CWE | str](
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    observation_date_time = HL7Field[DTM | str | None](
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    observation_end_date_time = HL7Field[DTM | str | None](
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    collection_volume = HL7Field[CQ | str | None](
        position=9,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    collector_identifier = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=10,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    specimen_action_code = HL7Field[ID | str | None](
        position=11,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70065",    )
    danger_code = HL7Field[CWE | str | None](
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70613",    )
    relevant_clinical_information = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70916",    )
    order_callback_phone_number = HL7Field[XTN | str | None](
        position=17,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    placer_field_1 = HL7Field[ST | str | None](
        position=18,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    placer_field_2 = HL7Field[ST | str | None](
        position=19,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    filler_field_1 = HL7Field[ST | str | None](
        position=20,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    filler_field_2 = HL7Field[ST | str | None](
        position=21,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    results_rpt_status_chng_date_time = HL7Field[DTM | str | None](
        position=22,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    charge_to_practice = HL7Field[MOC | str | None](
        position=23,
        datatype="MOC",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    diagnostic_serv_sect_id = HL7Field[ID | str | None](
        position=24,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70074",    )
    result_status = HL7Field[ID | str | None](
        position=25,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70123",    )
    parent_result = HL7Field[PRL | str | None](
        position=26,
        datatype="PRL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    parent_results_observation_identifier = HL7Field[EIP | str | None](
        position=29,
        datatype="EIP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    transportation_mode = HL7Field[ID | str | None](
        position=30,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70124",    )
    reason_for_study = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=31,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70951",    )
    scheduled_date_time = HL7Field[DTM | str | None](
        position=36,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    number_of_sample_containers = HL7Field[NM | str | None](
        position=37,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    transport_logistics_of_collected_sample = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=38,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70614",    )
    collectors_comment = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=39,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70619",    )
    transport_arrangement_responsibility = HL7Field[CWE | str | None](
        position=40,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70620",    )
    transport_arranged = HL7Field[ID | str | None](
        position=41,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70224",    )
    escort_required = HL7Field[ID | str | None](
        position=42,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70225",    )
    planned_patient_transport_comment = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=43,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70621",    )
    procedure_code = HL7Field[CNE | str | None](
        position=44,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70088",    )
    procedure_code_modifier = HL7Field[list[CNE] | CNE | list[str] | str | None](
        position=45,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70340",    )
    placer_supplemental_service_information = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=46,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70411",    )
    filler_supplemental_service_information = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=47,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70411",    )
    medically_necessary_duplicate_procedure_reason = HL7Field[CWE | str | None](
        position=48,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70476",    )
    result_handling = HL7Field[CWE | str | None](
        position=49,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70507",    )
    observation_group_id = HL7Field[EI | str | None](
        position=51,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    parent_observation_group_id = HL7Field[EI | str | None](
        position=52,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    alternate_placer_order_number = HL7Field[list[CX] | CX | list[str] | str | None](
        position=53,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    parent_order = HL7Field[list[EIP] | EIP | list[str] | str | None](
        position=54,
        datatype="EIP",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    action_code = HL7Field[ID | str | None](
        position=55,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class OBX(HL7Segment):
    _segment_id = "OBX"

    set_id_obx = HL7Field[SI | str | None](
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    value_type = HL7Field[ID | str | None](
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70125",    )
    observation_identifier = HL7Field[CWE | str](
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70622",    )
    observation_sub_id = HL7Field[OG | str | None](
        position=4,
        datatype="OG",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    observation_value = HL7Field[list[varies] | varies | list[str] | str | None](
        position=5,
        datatype="varies",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    units = HL7Field[CWE | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70623",    )
    reference_range = HL7Field[ST | str | None](
        position=7,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    interpretation_codes = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70078",    )
    probability = HL7Field[NM | str | None](
        position=9,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    nature_of_abnormal_test = HL7Field[list[ID] | ID | list[str] | str | None](
        position=10,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70080",    )
    observation_result_status = HL7Field[ID | str](
        position=11,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70085",    )
    effective_date_of_reference_range = HL7Field[DTM | str | None](
        position=12,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    user_defined_access_checks = HL7Field[ST | str | None](
        position=13,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    date_time_of_the_observation = HL7Field[DTM | str | None](
        position=14,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    producers_id = HL7Field[CWE | str | None](
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70624",    )
    responsible_observer = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=16,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    observation_method = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70626",    )
    equipment_instance_identifier = HL7Field[list[EI] | EI | list[str] | str | None](
        position=18,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    date_time_of_the_analysis = HL7Field[DTM | str | None](
        position=19,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    observation_site = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70163",    )
    observation_instance_identifier = HL7Field[EI | str | None](
        position=21,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    mood_code = HL7Field[CNE | str | None](
        position=22,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70725",    )
    performing_organization_name = HL7Field[XON | str | None](
        position=23,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    performing_organization_address = HL7Field[XAD | str | None](
        position=24,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    performing_organization_medical_director = HL7Field[XCN | str | None](
        position=25,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    patient_results_release_category = HL7Field[ID | str | None](
        position=26,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70909",    )
    root_cause = HL7Field[CWE | str | None](
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70914",    )
    local_process_control = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=28,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70915",    )
    observation_type = HL7Field[ID | str | None](
        position=29,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70936",    )
    observation_sub_type = HL7Field[ID | str | None](
        position=30,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70937",    )
    action_code = HL7Field[ID | str | None](
        position=31,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    observation_value_absent_reason = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=32,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70960",    )
    observation_related_specimen_identifier = HL7Field[list[EIP] | EIP | list[str] | str | None](
        position=33,
        datatype="EIP",
        usage=Usage.OPTIONAL,
        repeatable=True,    )

class ODS(HL7Segment):
    _segment_id = "ODS"

    type_ = HL7Field[ID | str](
        position=1,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70159",    )
    service_period = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70627",    )
    diet_supplement_or_preference_code = HL7Field[CWE | str](
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70628",    )
    text_instruction = HL7Field[ST | str | None](
        position=4,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class ODT(HL7Segment):
    _segment_id = "ODT"

    tray_type = HL7Field[CWE | str](
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70160",    )
    service_period = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70627",    )
    text_instruction = HL7Field[ST | str | None](
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class OH1(HL7Segment):
    _segment_id = "OH1"

    set_id = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    action_code = HL7Field[ID | str | None](
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    employment_status = HL7Field[CWE | str](
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70957",    )
    employment_status_start_date = HL7Field[DT | str | None](
        position=4,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    employment_status_end_date = HL7Field[DT | str | None](
        position=5,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    entered_date = HL7Field[DT | str](
        position=6,
        datatype="DT",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    employment_status_unique_identifier = HL7Field[EI | str | None](
        position=7,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class OH2(HL7Segment):
    _segment_id = "OH2"

    set_id = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    action_code = HL7Field[ID | str | None](
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    entered_date = HL7Field[DT | str | None](
        position=3,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    occupation = HL7Field[CWE | str](
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70958",    )
    industry = HL7Field[CWE | str](
        position=5,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70955",    )
    work_classification = HL7Field[CWE | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70959",    )
    job_start_date = HL7Field[DT | str | None](
        position=7,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    job_end_date = HL7Field[DT | str | None](
        position=8,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    work_schedule = HL7Field[CWE | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70954",    )
    average_hours_worked_per_day = HL7Field[NM | str | None](
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    average_days_worked_per_week = HL7Field[NM | str | None](
        position=11,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    employer_organization = HL7Field[XON | str | None](
        position=12,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    employer_address = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=13,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    supervisory_level = HL7Field[CWE | str | None](
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70956",    )
    job_duties = HL7Field[list[ST] | ST | list[str] | str | None](
        position=15,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    occupational_hazards = HL7Field[list[FT] | FT | list[str] | str | None](
        position=16,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    job_unique_identifier = HL7Field[EI | str | None](
        position=17,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    current_job_indicator = HL7Field[CWE | str | None](
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )

class OH3(HL7Segment):
    _segment_id = "OH3"

    set_id = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    action_code = HL7Field[ID | str | None](
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    occupation = HL7Field[CWE | str](
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70958",    )
    industry = HL7Field[CWE | str](
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70955",    )
    usual_occupation_duration_years = HL7Field[NM | str | None](
        position=5,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    start_year = HL7Field[DT | str | None](
        position=6,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    entered_date = HL7Field[DT | str | None](
        position=7,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    work_unique_identifier = HL7Field[EI | str | None](
        position=8,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class OH4(HL7Segment):
    _segment_id = "OH4"

    set_id = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    action_code = HL7Field[ID | str | None](
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    combat_zone_start_date = HL7Field[DT | str](
        position=3,
        datatype="DT",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    combat_zone_end_date = HL7Field[DT | str | None](
        position=4,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    entered_date = HL7Field[DT | str | None](
        position=5,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    combat_zone_unique_identifier = HL7Field[EI | str | None](
        position=6,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class OM1(HL7Segment):
    _segment_id = "OM1"

    sequence_number_test_observation_master_file = HL7Field[NM | str](
        position=1,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    producers_service_test_observation_id = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    permitted_data_types = HL7Field[list[ID] | ID | list[str] | str | None](
        position=3,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70125",    )
    specimen_required = HL7Field[ID | str](
        position=4,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70136",    )
    producer_id = HL7Field[CWE | str](
        position=5,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70631",    )
    observation_description = HL7Field[TX | str | None](
        position=6,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    other_service_test_observation_i_ds_for_the_observation = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70632",    )
    other_names = HL7Field[list[ST] | ST | list[str] | str | None](
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    preferred_report_name_for_the_observation = HL7Field[ST | str | None](
        position=9,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    preferred_short_name_or_mnemonic_for_the_observation = HL7Field[ST | str | None](
        position=10,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    preferred_long_name_for_the_observation = HL7Field[ST | str | None](
        position=11,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    orderability = HL7Field[ID | str | None](
        position=12,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    identity_of_instrument_used_to_perform_this_study = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70633",    )
    coded_representation_of_method = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70635",    )
    portable_device_indicator = HL7Field[ID | str | None](
        position=15,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    observation_producing_department_section = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70636",    )
    telephone_number_of_section = HL7Field[XTN | str | None](
        position=17,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    nature_of_service_test_observation = HL7Field[CWE | str](
        position=18,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70174",    )
    report_subheader = HL7Field[CWE | str | None](
        position=19,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70637",    )
    report_display_order = HL7Field[ST | str | None](
        position=20,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    date_time_stamp_for_any_change_in_definition_for_the_observation = HL7Field[DTM | str | None](
        position=21,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    effective_date_time_of_change = HL7Field[DTM | str | None](
        position=22,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    typical_turn_around_time = HL7Field[NM | str | None](
        position=23,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    processing_time = HL7Field[NM | str | None](
        position=24,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    processing_priority = HL7Field[list[ID] | ID | list[str] | str | None](
        position=25,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70168",    )
    reporting_priority = HL7Field[ID | str | None](
        position=26,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70169",    )
    outside_sites_where_observation_may_be_performed = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70638",    )
    address_of_outside_sites = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=28,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    phone_number_of_outside_site = HL7Field[XTN | str | None](
        position=29,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    confidentiality_code = HL7Field[CWE | str | None](
        position=30,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70177",    )
    observations_required_to_interpret_this_observation = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=31,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70639",    )
    interpretation_of_observations = HL7Field[TX | str | None](
        position=32,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    contraindications_to_observations = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=33,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70640",    )
    reflex_tests_observations = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=34,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70641",    )
    rules_that_trigger_reflex_testing = HL7Field[list[TX] | TX | list[str] | str | None](
        position=35,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    fixed_canned_message = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=36,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70643",    )
    patient_preparation = HL7Field[list[TX] | TX | list[str] | str | None](
        position=37,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    procedure_medication = HL7Field[CWE | str | None](
        position=38,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70644",    )
    factors_that_may_affect_the_observation = HL7Field[TX | str | None](
        position=39,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    service_test_observation_performance_schedule = HL7Field[list[ST] | ST | list[str] | str | None](
        position=40,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    description_of_test_methods = HL7Field[TX | str | None](
        position=41,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    kind_of_quantity_observed = HL7Field[CWE | str | None](
        position=42,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70254",    )
    point_versus_interval = HL7Field[CWE | str | None](
        position=43,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70255",    )
    challenge_information = HL7Field[TX | str | None](
        position=44,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70256",    )
    relationship_modifier = HL7Field[CWE | str | None](
        position=45,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70258",    )
    target_anatomic_site_of_test = HL7Field[CWE | str | None](
        position=46,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70645",    )
    modality_of_imaging_measurement = HL7Field[CWE | str | None](
        position=47,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70910",    )
    exclusive_test = HL7Field[ID | str | None](
        position=48,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70919",    )
    diagnostic_serv_sect_id = HL7Field[ID | str | None](
        position=49,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70074",    )
    taxonomic_classification_code = HL7Field[CWE | str | None](
        position=50,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    other_names_51 = HL7Field[list[ST] | ST | list[str] | str | None](
        position=51,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    replacement_producers_service_test_observation_id = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=52,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70646",    )
    prior_resuts_instructions = HL7Field[list[TX] | TX | list[str] | str | None](
        position=53,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    special_instructions = HL7Field[TX | str | None](
        position=54,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    test_category = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=55,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    observation_identifier_associated_with_producers_service_test_observation_id = HL7Field[CWE | str | None](
        position=56,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70647",    )
    typical_turn_around_time_57 = HL7Field[CQ | str | None](
        position=57,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    gender_restriction = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=58,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70001",    )
    age_restriction = HL7Field[list[NR] | NR | list[str] | str | None](
        position=59,
        datatype="NR",
        usage=Usage.OPTIONAL,
        repeatable=True,    )

class OM2(HL7Segment):
    _segment_id = "OM2"

    sequence_number_test_observation_master_file = HL7Field[NM | str | None](
        position=1,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    units_of_measure = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70648",    )
    range_of_decimal_precision = HL7Field[list[NM] | NM | list[str] | str | None](
        position=3,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    corresponding_si_units_of_measure = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70649",    )
    si_conversion_factor = HL7Field[TX | str | None](
        position=5,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    reference_normal_range_for_ordinal_and_continuous_observations = HL7Field[list[RFR] | RFR | list[str] | str | None](
        position=6,
        datatype="RFR",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    critical_range_for_ordinal_and_continuous_observations = HL7Field[list[RFR] | RFR | list[str] | str | None](
        position=7,
        datatype="RFR",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    absolute_range_for_ordinal_and_continuous_observations = HL7Field[RFR | str | None](
        position=8,
        datatype="RFR",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    delta_check_criteria = HL7Field[list[DLT] | DLT | list[str] | str | None](
        position=9,
        datatype="DLT",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    minimum_meaningful_increments = HL7Field[NM | str | None](
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class OM3(HL7Segment):
    _segment_id = "OM3"

    sequence_number_test_observation_master_file = HL7Field[NM | str | None](
        position=1,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    preferred_coding_system = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70650",    )
    valid_coded_answers = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70652",    )
    normal_text_codes_for_categorical_observations = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70654",    )
    abnormal_text_codes_for_categorical_observations = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70655",    )
    critical_text_codes_for_categorical_observations = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70656",    )
    value_type = HL7Field[ID | str | None](
        position=7,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70125",    )

class OM4(HL7Segment):
    _segment_id = "OM4"

    sequence_number_test_observation_master_file = HL7Field[NM | str | None](
        position=1,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    derived_specimen = HL7Field[ID | str | None](
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70170",    )
    container_description = HL7Field[list[TX] | TX | list[str] | str | None](
        position=3,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    container_volume = HL7Field[list[NM] | NM | list[str] | str | None](
        position=4,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    container_units = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70658",    )
    specimen = HL7Field[CWE | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70660",    )
    additive = HL7Field[CWE | str | None](
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70371",    )
    preparation = HL7Field[TX | str | None](
        position=8,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    special_handling_requirements = HL7Field[TX | str | None](
        position=9,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    normal_collection_volume = HL7Field[CQ | str | None](
        position=10,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    minimum_collection_volume = HL7Field[CQ | str | None](
        position=11,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    specimen_requirements = HL7Field[TX | str | None](
        position=12,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    specimen_priorities = HL7Field[list[ID] | ID | list[str] | str | None](
        position=13,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70027",    )
    specimen_retention_time = HL7Field[CQ | str | None](
        position=14,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    specimen_handling_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70376",    )
    specimen_preference = HL7Field[ID | str | None](
        position=16,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70920",    )
    preferred_specimen_attribture_sequence_id = HL7Field[NM | str | None](
        position=17,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    taxonomic_classification_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,    )

class OM5(HL7Segment):
    _segment_id = "OM5"

    sequence_number_test_observation_master_file = HL7Field[NM | str | None](
        position=1,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    test_observations_included_within_an_ordered_test_battery = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70662",    )
    observation_id_suffixes = HL7Field[ST | str | None](
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class OM6(HL7Segment):
    _segment_id = "OM6"

    sequence_number_test_observation_master_file = HL7Field[NM | str | None](
        position=1,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    derivation_rule = HL7Field[TX | str | None](
        position=2,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class OM7(HL7Segment):
    _segment_id = "OM7"

    sequence_number_test_observation_master_file = HL7Field[NM | str](
        position=1,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    universal_service_identifier = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    category_identifier = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70412",    )
    category_description = HL7Field[TX | str | None](
        position=4,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    category_synonym = HL7Field[list[ST] | ST | list[str] | str | None](
        position=5,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    effective_test_service_start_date_time = HL7Field[DTM | str | None](
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    effective_test_service_end_date_time = HL7Field[DTM | str | None](
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    test_service_default_duration_quantity = HL7Field[NM | str | None](
        position=8,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    test_service_default_duration_units = HL7Field[CWE | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70663",    )
    test_service_default_frequency = HL7Field[CWE | str | None](
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    consent_indicator = HL7Field[ID | str | None](
        position=11,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    consent_identifier = HL7Field[CWE | str | None](
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70413",    )
    consent_effective_start_date_time = HL7Field[DTM | str | None](
        position=13,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    consent_effective_end_date_time = HL7Field[DTM | str | None](
        position=14,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    consent_interval_quantity = HL7Field[NM | str | None](
        position=15,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    consent_interval_units = HL7Field[CWE | str | None](
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70414",    )
    consent_waiting_period_quantity = HL7Field[NM | str | None](
        position=17,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    consent_waiting_period_units = HL7Field[CWE | str | None](
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70414",    )
    effective_date_time_of_change = HL7Field[DTM | str | None](
        position=19,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    entered_by = HL7Field[XCN | str | None](
        position=20,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    orderable_at_location = HL7Field[list[PL] | PL | list[str] | str | None](
        position=21,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    formulary_status = HL7Field[CWE | str | None](
        position=22,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70473",    )
    special_order_indicator = HL7Field[ID | str | None](
        position=23,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    primary_key_value_cdm = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,    )

class OMC(HL7Segment):
    _segment_id = "OMC"

    sequence_number_test_observation_master_file = HL7Field[NM | str | None](
        position=1,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    segment_action_code = HL7Field[ID | str | None](
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70206",    )
    segment_unique_key = HL7Field[EI | str | None](
        position=3,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    clinical_information_request = HL7Field[CWE | str](
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70664",    )
    collection_event_process_step = HL7Field[list[CWE] | CWE | list[str] | str](
        position=5,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=True, table="HL70938",    )
    communication_location = HL7Field[CWE | str](
        position=6,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70939",    )
    answer_required = HL7Field[ID | str | None](
        position=7,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    hint_help_text = HL7Field[ST | str | None](
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    type_of_answer = HL7Field[ID | str | None](
        position=9,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70125",    )
    multiple_answers_allowed = HL7Field[ID | str | None](
        position=10,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    answer_choices = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70665",    )
    character_limit = HL7Field[NM | str | None](
        position=12,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    number_of_decimals = HL7Field[NM | str | None](
        position=13,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class ORC(HL7Segment):
    _segment_id = "ORC"

    order_control = HL7Field[ID | str](
        position=1,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70119",    )
    placer_order_number = HL7Field[EI | str | None](
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    filler_order_number = HL7Field[EI | str | None](
        position=3,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    placer_order_group_number = HL7Field[EI | str | None](
        position=4,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    order_status = HL7Field[ID | str | None](
        position=5,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70038",    )
    response_flag = HL7Field[ID | str | None](
        position=6,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70121",    )
    parent_order = HL7Field[list[EIP] | EIP | list[str] | str | None](
        position=8,
        datatype="EIP",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    date_time_of_order_event = HL7Field[DTM | str | None](
        position=9,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    enterers_location = HL7Field[PL | str | None](
        position=13,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    call_back_phone_number = HL7Field[XTN | str | None](
        position=14,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    order_effective_date_time = HL7Field[DTM | str | None](
        position=15,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    order_control_code_reason = HL7Field[CWE | str | None](
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70949",    )
    advanced_beneficiary_notice_code = HL7Field[CWE | str | None](
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70339",    )
    order_status_modifier = HL7Field[CWE | str | None](
        position=25,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70950",    )
    advanced_beneficiary_notice_override_reason = HL7Field[CWE | str | None](
        position=26,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70552",    )
    fillers_expected_availability_date_time = HL7Field[DTM | str | None](
        position=27,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    confidentiality_code = HL7Field[CWE | str | None](
        position=28,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70177",    )
    order_type = HL7Field[CWE | str | None](
        position=29,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70482",    )
    enterer_authorization_mode = HL7Field[CNE | str | None](
        position=30,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70483",    )
    advanced_beneficiary_notice_date = HL7Field[DT | str | None](
        position=32,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    alternate_placer_order_number = HL7Field[list[CX] | CX | list[str] | str | None](
        position=33,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    order_workflow_profile = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=34,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70934",    )
    action_code = HL7Field[ID | str | None](
        position=35,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    order_status_date_range = HL7Field[DR | str | None](
        position=36,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    order_creation_date_time = HL7Field[DTM | str | None](
        position=37,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    filler_order_group_number = HL7Field[EI | str | None](
        position=38,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class ORG(HL7Segment):
    _segment_id = "ORG"

    set_id_org = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    organization_unit_code = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70405",    )
    organization_unit_type_code = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70474",    )
    primary_org_unit_indicator = HL7Field[ID | str | None](
        position=4,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    practitioner_org_unit_identifier = HL7Field[CX | str | None](
        position=5,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    health_care_provider_type_code = HL7Field[CWE | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70452",    )
    health_care_provider_classification_code = HL7Field[CWE | str | None](
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70453",    )
    health_care_provider_area_of_specialization_code = HL7Field[CWE | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70454",    )
    effective_date_range = HL7Field[DR | str | None](
        position=9,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    employment_status_code = HL7Field[CWE | str | None](
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70066",    )
    board_approval_indicator = HL7Field[ID | str | None](
        position=11,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    primary_care_physician_indicator = HL7Field[ID | str | None](
        position=12,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    cost_center_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70539",    )

class OVR(HL7Segment):
    _segment_id = "OVR"

    business_rule_override_type = HL7Field[CWE | str | None](
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70518",    )
    business_rule_override_code = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70521",    )
    override_comments = HL7Field[TX | str | None](
        position=3,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    override_entered_by = HL7Field[XCN | str | None](
        position=4,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    override_authorized_by = HL7Field[XCN | str | None](
        position=5,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class PAC(HL7Segment):
    _segment_id = "PAC"

    set_id_pac = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    package_id = HL7Field[EI | str | None](
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    parent_package_id = HL7Field[EI | str | None](
        position=3,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    position_in_parent_package = HL7Field[NA | str | None](
        position=4,
        datatype="NA",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    package_type = HL7Field[CWE | str](
        position=5,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70908",    )
    package_condition = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70544",    )
    package_handling_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70376",    )
    package_risk_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70489",    )
    action_code = HL7Field[ID | str | None](
        position=9,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class PCE(HL7Segment):
    _segment_id = "PCE"

    set_id_pce = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    cost_center_account_number = HL7Field[CX | str | None](
        position=2,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70319",    )
    transaction_code = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70132",    )
    transaction_amount_unit = HL7Field[CP | str | None](
        position=4,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class PCR(HL7Segment):
    _segment_id = "PCR"

    implicated_product = HL7Field[CWE | str](
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70670",    )
    generic_product = HL7Field[IS | str | None](
        position=2,
        datatype="IS",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70249",    )
    product_class = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70671",    )
    total_duration_of_therapy = HL7Field[CQ | str | None](
        position=4,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    product_manufacture_date = HL7Field[DTM | str | None](
        position=5,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    product_expiration_date = HL7Field[DTM | str | None](
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    product_implantation_date = HL7Field[DTM | str | None](
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    product_explantation_date = HL7Field[DTM | str | None](
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    single_use_device = HL7Field[CWE | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70244",    )
    indication_for_product_use = HL7Field[CWE | str | None](
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70672",    )
    product_problem = HL7Field[CWE | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70245",    )
    product_serial_lot_number = HL7Field[ST | str | None](
        position=12,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    product_available_for_inspection = HL7Field[CWE | str | None](
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70246",    )
    product_evaluation_performed = HL7Field[CWE | str | None](
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70673",    )
    product_evaluation_status = HL7Field[CWE | str | None](
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70247",    )
    product_evaluation_results = HL7Field[CWE | str | None](
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70674",    )
    evaluated_product_source = HL7Field[ID | str | None](
        position=17,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70248",    )
    date_product_returned_to_manufacturer = HL7Field[DTM | str | None](
        position=18,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    device_operator_qualifications = HL7Field[ID | str | None](
        position=19,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70242",    )
    relatedness_assessment = HL7Field[ID | str | None](
        position=20,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70250",    )
    action_taken_in_response_to_the_event = HL7Field[ID | str | None](
        position=21,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70251",    )
    event_causality_observations = HL7Field[ID | str | None](
        position=22,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70252",    )
    indirect_exposure_mechanism = HL7Field[ID | str | None](
        position=23,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70253",    )

class PD1(HL7Segment):
    _segment_id = "PD1"

    living_dependency = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70223",    )
    living_arrangement = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70220",    )
    patient_primary_facility = HL7Field[list[XON] | XON | list[str] | str | None](
        position=3,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70204",    )
    student_indicator = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70231",    )
    handicap = HL7Field[CWE | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70295",    )
    living_will_code = HL7Field[CWE | str | None](
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70315",    )
    organ_donor_code = HL7Field[CWE | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70316",    )
    separate_bill = HL7Field[ID | str | None](
        position=9,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    duplicate_patient = HL7Field[list[CX] | CX | list[str] | str | None](
        position=10,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    publicity_code = HL7Field[CWE | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70215",    )
    protection_indicator = HL7Field[ID | str | None](
        position=12,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    protection_indicator_effective_date = HL7Field[DT | str | None](
        position=13,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    place_of_worship = HL7Field[list[XON] | XON | list[str] | str | None](
        position=14,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    advance_directive_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70435",    )
    immunization_registry_status = HL7Field[CWE | str | None](
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70441",    )
    immunization_registry_status_effective_date = HL7Field[DT | str | None](
        position=17,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    publicity_code_effective_date = HL7Field[DT | str | None](
        position=18,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    military_branch = HL7Field[CWE | str | None](
        position=19,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70140",    )
    military_rank_grade = HL7Field[CWE | str | None](
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70141",    )
    military_status = HL7Field[CWE | str | None](
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70142",    )
    advance_directive_last_verified_date = HL7Field[DT | str | None](
        position=22,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    retirement_date = HL7Field[DT | str | None](
        position=23,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class PDA(HL7Segment):
    _segment_id = "PDA"

    death_cause_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    death_location = HL7Field[PL | str | None](
        position=2,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    death_certified_indicator = HL7Field[ID | str | None](
        position=3,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    death_certificate_signed_date_time = HL7Field[DTM | str | None](
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    death_certified_by = HL7Field[XCN | str | None](
        position=5,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    autopsy_indicator = HL7Field[ID | str | None](
        position=6,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    autopsy_start_and_end_date_time = HL7Field[DR | str | None](
        position=7,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    autopsy_performed_by = HL7Field[XCN | str | None](
        position=8,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    coroner_indicator = HL7Field[ID | str | None](
        position=9,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )

class PDC(HL7Segment):
    _segment_id = "PDC"

    manufacturer_distributor = HL7Field[list[XON] | XON | list[str] | str](
        position=1,
        datatype="XON",
        usage=Usage.REQUIRED,
        repeatable=True,    )
    country = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70675",    )
    brand_name = HL7Field[ST | str](
        position=3,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    device_family_name = HL7Field[ST | str | None](
        position=4,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    generic_name = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70676",    )
    model_identifier = HL7Field[list[ST] | ST | list[str] | str | None](
        position=6,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    catalogue_identifier = HL7Field[ST | str | None](
        position=7,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    other_identifier = HL7Field[list[ST] | ST | list[str] | str | None](
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    product_code = HL7Field[CWE | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70677",    )
    marketing_basis = HL7Field[ID | str | None](
        position=10,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70330",    )
    marketing_approval_id = HL7Field[ST | str | None](
        position=11,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    labeled_shelf_life = HL7Field[CQ | str | None](
        position=12,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    expected_shelf_life = HL7Field[CQ | str | None](
        position=13,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    date_first_marketed = HL7Field[DTM | str | None](
        position=14,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    date_last_marketed = HL7Field[DTM | str | None](
        position=15,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class PEO(HL7Segment):
    _segment_id = "PEO"

    event_identifiers_used = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70678",    )
    event_symptom_diagnosis_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70679",    )
    event_onset_date_time = HL7Field[DTM | str](
        position=3,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    event_exacerbation_date_time = HL7Field[DTM | str | None](
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    event_improved_date_time = HL7Field[DTM | str | None](
        position=5,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    event_ended_data_time = HL7Field[DTM | str | None](
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    event_location_occurred_address = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=7,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    event_qualification = HL7Field[list[ID] | ID | list[str] | str | None](
        position=8,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70237",    )
    event_serious = HL7Field[ID | str | None](
        position=9,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70238",    )
    event_expected = HL7Field[ID | str | None](
        position=10,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70239",    )
    event_outcome = HL7Field[list[ID] | ID | list[str] | str | None](
        position=11,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70240",    )
    patient_outcome = HL7Field[ID | str | None](
        position=12,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70241",    )
    event_description_from_others = HL7Field[list[FT] | FT | list[str] | str | None](
        position=13,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    event_description_from_original_reporter = HL7Field[list[FT] | FT | list[str] | str | None](
        position=14,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    event_description_from_patient = HL7Field[list[FT] | FT | list[str] | str | None](
        position=15,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    event_description_from_practitioner = HL7Field[list[FT] | FT | list[str] | str | None](
        position=16,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    event_description_from_autopsy = HL7Field[list[FT] | FT | list[str] | str | None](
        position=17,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    cause_of_death = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70680",    )
    primary_observer_name = HL7Field[list[XPN] | XPN | list[str] | str | None](
        position=19,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    primary_observer_address = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=20,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    primary_observer_telephone = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=21,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    primary_observers_qualification = HL7Field[ID | str | None](
        position=22,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70242",    )
    confirmation_provided_by = HL7Field[ID | str | None](
        position=23,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70242",    )
    primary_observer_aware_date_time = HL7Field[DTM | str | None](
        position=24,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    primary_observers_identity_may_be_divulged = HL7Field[ID | str | None](
        position=25,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70243",    )

class PES(HL7Segment):
    _segment_id = "PES"

    sender_organization_name = HL7Field[list[XON] | XON | list[str] | str | None](
        position=1,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    sender_individual_name = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=2,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    sender_address = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=3,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    sender_telephone = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=4,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    sender_event_identifier = HL7Field[EI | str | None](
        position=5,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    sender_sequence_number = HL7Field[NM | str | None](
        position=6,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    sender_event_description = HL7Field[list[FT] | FT | list[str] | str | None](
        position=7,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    sender_comment = HL7Field[FT | str | None](
        position=8,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    sender_aware_date_time = HL7Field[DTM | str | None](
        position=9,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    event_report_date = HL7Field[DTM | str](
        position=10,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    event_report_timing_type = HL7Field[ID | str | None](
        position=11,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70234",    )
    event_report_source = HL7Field[ID | str | None](
        position=12,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70235",    )
    event_reported_to = HL7Field[list[ID] | ID | list[str] | str | None](
        position=13,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70236",    )

class PID(HL7Segment):
    _segment_id = "PID"

    set_id_pid = HL7Field[SI | str | None](
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    patient_identifier_list = HL7Field[list[CX] | CX | list[str] | str](
        position=3,
        datatype="CX",
        usage=Usage.REQUIRED,
        repeatable=True,    )
    patient_name = HL7Field[list[XPN] | XPN | list[str] | str](
        position=5,
        datatype="XPN",
        usage=Usage.REQUIRED,
        repeatable=True, table="HL70200",    )
    mothers_maiden_name = HL7Field[list[XPN] | XPN | list[str] | str | None](
        position=6,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    date_time_of_birth = HL7Field[DTM | str | None](
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    administrative_sex = HL7Field[CWE | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70001",    )
    race = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70005",    )
    patient_address = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=11,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    primary_language = HL7Field[CWE | str | None](
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70296",    )
    marital_status = HL7Field[CWE | str | None](
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70002",    )
    religion = HL7Field[CWE | str | None](
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70006",    )
    patient_account_number = HL7Field[CX | str | None](
        position=18,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70061",    )
    mothers_identifier = HL7Field[list[CX] | CX | list[str] | str | None](
        position=21,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70061",    )
    ethnic_group = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=22,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70189",    )
    birth_place = HL7Field[ST | str | None](
        position=23,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    multiple_birth_indicator = HL7Field[ID | str | None](
        position=24,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    birth_order = HL7Field[NM | str | None](
        position=25,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    citizenship = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=26,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70171",    )
    veterans_military_status = HL7Field[CWE | str | None](
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70172",    )
    patient_death_date_and_time = HL7Field[DTM | str | None](
        position=29,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    patient_death_indicator = HL7Field[ID | str | None](
        position=30,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    identity_unknown_indicator = HL7Field[ID | str | None](
        position=31,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    identity_reliability_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=32,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70445",    )
    last_update_date_time = HL7Field[DTM | str | None](
        position=33,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    last_update_facility = HL7Field[HD | str | None](
        position=34,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    taxonomic_classification_code = HL7Field[CWE | str | None](
        position=35,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    breed_code = HL7Field[CWE | str | None](
        position=36,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70447",    )
    strain = HL7Field[ST | str | None](
        position=37,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    production_class_code = HL7Field[CWE | str | None](
        position=38,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70429",    )
    tribal_citizenship = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=39,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70171",    )
    patient_telecommunication_information = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=40,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )

class PKG(HL7Segment):
    _segment_id = "PKG"

    set_id_pkg = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    packaging_units = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70818",    )
    default_order_unit_of_measure_indicator = HL7Field[CNE | str | None](
        position=3,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    package_quantity = HL7Field[NM | str | None](
        position=4,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    price = HL7Field[CP | str | None](
        position=5,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    future_item_price = HL7Field[CP | str | None](
        position=6,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    future_item_price_effective_date = HL7Field[DTM | str | None](
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    global_trade_item_number = HL7Field[CWE | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    contract_price = HL7Field[MO | str | None](
        position=9,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    quantity_of_each = HL7Field[NM | str | None](
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    vendor_catalog_number = HL7Field[EI | str | None](
        position=11,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class PM1(HL7Segment):
    _segment_id = "PM1"

    health_plan_id = HL7Field[CWE | str](
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70072",    )
    insurance_company_id = HL7Field[list[CX] | CX | list[str] | str](
        position=2,
        datatype="CX",
        usage=Usage.REQUIRED,
        repeatable=True,    )
    insurance_company_name = HL7Field[list[XON] | XON | list[str] | str | None](
        position=3,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    insurance_company_address = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=4,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    insurance_co_contact_person = HL7Field[list[XPN] | XPN | list[str] | str | None](
        position=5,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    insurance_co_phone_number = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=6,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    group_number = HL7Field[ST | str | None](
        position=7,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    group_name = HL7Field[list[XON] | XON | list[str] | str | None](
        position=8,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    plan_effective_date = HL7Field[DT | str | None](
        position=9,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    plan_expiration_date = HL7Field[DT | str | None](
        position=10,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    patient_dob_required = HL7Field[ID | str | None](
        position=11,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    patient_gender_required = HL7Field[ID | str | None](
        position=12,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    patient_relationship_required = HL7Field[ID | str | None](
        position=13,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    patient_signature_required = HL7Field[ID | str | None](
        position=14,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    diagnosis_required = HL7Field[ID | str | None](
        position=15,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    service_required = HL7Field[ID | str | None](
        position=16,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    patient_name_required = HL7Field[ID | str | None](
        position=17,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    patient_address_required = HL7Field[ID | str | None](
        position=18,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    subscribers_name_required = HL7Field[ID | str | None](
        position=19,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    workmans_comp_indicator = HL7Field[ID | str | None](
        position=20,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    bill_type_required = HL7Field[ID | str | None](
        position=21,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    commercial_carrier_name_and_address_required = HL7Field[ID | str | None](
        position=22,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    policy_number_pattern = HL7Field[ST | str | None](
        position=23,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    group_number_pattern = HL7Field[ST | str | None](
        position=24,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class PMT(HL7Segment):
    _segment_id = "PMT"

    payment_remittance_advice_number = HL7Field[EI | str](
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    payment_remittance_effective_date_time = HL7Field[DTM | str](
        position=2,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    payment_remittance_expiration_date_time = HL7Field[DTM | str](
        position=3,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    payment_method = HL7Field[CWE | str](
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70570",    )
    payment_remittance_date_time = HL7Field[DTM | str](
        position=5,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    payment_remittance_amount = HL7Field[CP | str](
        position=6,
        datatype="CP",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    check_number = HL7Field[EI | str | None](
        position=7,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    payee_bank_identification = HL7Field[XON | str | None](
        position=8,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    payee_transit_number = HL7Field[ST | str | None](
        position=9,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    payee_bank_account_id = HL7Field[CX | str | None](
        position=10,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    payment_organization = HL7Field[XON | str](
        position=11,
        datatype="XON",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    esr_code_line = HL7Field[ST | str | None](
        position=12,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class PR1(HL7Segment):
    _segment_id = "PR1"

    set_id_pr1 = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    procedure_code = HL7Field[CNE | str](
        position=3,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70088",    )
    procedure_date_time = HL7Field[DTM | str](
        position=5,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    procedure_functional_type = HL7Field[CWE | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70230",    )
    procedure_minutes = HL7Field[NM | str | None](
        position=7,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    anesthesia_code = HL7Field[CWE | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70019",    )
    anesthesia_minutes = HL7Field[NM | str | None](
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    consent_code = HL7Field[CWE | str | None](
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70059",    )
    procedure_priority = HL7Field[NM | str | None](
        position=14,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70418",    )
    associated_diagnosis_code = HL7Field[CWE | str | None](
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70051",    )
    procedure_code_modifier = HL7Field[list[CNE] | CNE | list[str] | str | None](
        position=16,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70340",    )
    procedure_drg_type = HL7Field[CWE | str | None](
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70416",    )
    tissue_type_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70417",    )
    procedure_identifier = HL7Field[EI | str | None](
        position=19,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    procedure_action_code = HL7Field[ID | str | None](
        position=20,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70206",    )
    drg_procedure_determination_status = HL7Field[CWE | str | None](
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70761",    )
    drg_procedure_relevance = HL7Field[CWE | str | None](
        position=22,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70763",    )
    treating_organizational_unit = HL7Field[list[PL] | PL | list[str] | str | None](
        position=23,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    respiratory_within_surgery = HL7Field[ID | str | None](
        position=24,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    parent_procedure_id = HL7Field[EI | str | None](
        position=25,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class PRA(HL7Segment):
    _segment_id = "PRA"

    primary_key_value_pra = HL7Field[CWE | str | None](
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70681",    )
    practitioner_group = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70358",    )
    practitioner_category = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70186",    )
    provider_billing = HL7Field[ID | str | None](
        position=4,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70187",    )
    specialty = HL7Field[list[SPD] | SPD | list[str] | str | None](
        position=5,
        datatype="SPD",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70337",    )
    practitioner_id_numbers = HL7Field[list[PLN] | PLN | list[str] | str | None](
        position=6,
        datatype="PLN",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70338",    )
    privileges = HL7Field[list[PIP] | PIP | list[str] | str | None](
        position=7,
        datatype="PIP",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    date_entered_practice = HL7Field[DT | str | None](
        position=8,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    institution = HL7Field[CWE | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70537",    )
    date_left_practice = HL7Field[DT | str | None](
        position=10,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    government_reimbursement_billing_eligibility = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70401",    )
    set_id_pra = HL7Field[SI | str | None](
        position=12,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class PRB(HL7Segment):
    _segment_id = "PRB"

    action_code = HL7Field[ID | str](
        position=1,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    action_date_time = HL7Field[DTM | str](
        position=2,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    problem_id = HL7Field[CWE | str](
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    problem_instance_id = HL7Field[EI | str](
        position=4,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    episode_of_care_id = HL7Field[EI | str | None](
        position=5,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    problem_list_priority = HL7Field[NM | str | None](
        position=6,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    problem_established_date_time = HL7Field[DTM | str | None](
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    anticipated_problem_resolution_date_time = HL7Field[DTM | str | None](
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    actual_problem_resolution_date_time = HL7Field[DTM | str | None](
        position=9,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    problem_classification = HL7Field[CWE | str | None](
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    problem_management_discipline = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    problem_persistence = HL7Field[CWE | str | None](
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    problem_confirmation_status = HL7Field[CWE | str | None](
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    problem_life_cycle_status = HL7Field[CWE | str | None](
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    problem_life_cycle_status_date_time = HL7Field[DTM | str | None](
        position=15,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    problem_date_of_onset = HL7Field[DTM | str | None](
        position=16,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    problem_onset_text = HL7Field[ST | str | None](
        position=17,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    problem_ranking = HL7Field[CWE | str | None](
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    certainty_of_problem = HL7Field[CWE | str | None](
        position=19,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    probability_of_problem_0_1 = HL7Field[NM | str | None](
        position=20,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    individual_awareness_of_problem = HL7Field[CWE | str | None](
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    problem_prognosis = HL7Field[CWE | str | None](
        position=22,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    individual_awareness_of_prognosis = HL7Field[CWE | str | None](
        position=23,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    family_significant_other_awareness_of_problem_prognosis = HL7Field[ST | str | None](
        position=24,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    security_sensitivity = HL7Field[CWE | str | None](
        position=25,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    problem_severity = HL7Field[CWE | str | None](
        position=26,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70836",    )
    problem_perspective = HL7Field[CWE | str | None](
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70838",    )
    mood_code = HL7Field[CNE | str | None](
        position=28,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70725",    )

class PRC(HL7Segment):
    _segment_id = "PRC"

    primary_key_value_prc = HL7Field[CWE | str](
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70132",    )
    facility_id_prc = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70464",    )
    department = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70184",    )
    valid_patient_classes = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70004",    )
    price = HL7Field[list[CP] | CP | list[str] | str | None](
        position=5,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    formula = HL7Field[list[ST] | ST | list[str] | str | None](
        position=6,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    minimum_quantity = HL7Field[NM | str | None](
        position=7,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    maximum_quantity = HL7Field[NM | str | None](
        position=8,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    minimum_price = HL7Field[MO | str | None](
        position=9,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    maximum_price = HL7Field[MO | str | None](
        position=10,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    effective_start_date = HL7Field[DTM | str | None](
        position=11,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    effective_end_date = HL7Field[DTM | str | None](
        position=12,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    price_override_flag = HL7Field[CWE | str | None](
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70268",    )
    billing_category = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70293",    )
    chargeable_flag = HL7Field[ID | str | None](
        position=15,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    active_inactive_flag = HL7Field[ID | str | None](
        position=16,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70183",    )
    cost = HL7Field[MO | str | None](
        position=17,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    charge_on_indicator = HL7Field[CWE | str | None](
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70269",    )

class PRD(HL7Segment):
    _segment_id = "PRD"

    provider_role = HL7Field[list[CWE] | CWE | list[str] | str](
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=True, table="HL70286",    )
    provider_name = HL7Field[list[XPN] | XPN | list[str] | str | None](
        position=2,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    provider_address = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=3,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    provider_location = HL7Field[PL | str | None](
        position=4,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    provider_communication_information = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=5,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    preferred_method_of_contact = HL7Field[CWE | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70185",    )
    provider_identifiers = HL7Field[list[PLN] | PLN | list[str] | str | None](
        position=7,
        datatype="PLN",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70338",    )
    effective_start_date_of_provider_role = HL7Field[DTM | str | None](
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    effective_end_date_of_provider_role = HL7Field[list[DTM] | DTM | list[str] | str | None](
        position=9,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    provider_organization_name_and_identifier = HL7Field[XON | str | None](
        position=10,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    provider_organization_address = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=11,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    provider_organization_location_information = HL7Field[list[PL] | PL | list[str] | str | None](
        position=12,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    provider_organization_communication_information = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=13,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    provider_organization_method_of_contact = HL7Field[CWE | str | None](
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70185",    )

class PRT(HL7Segment):
    _segment_id = "PRT"

    participation_instance_id = HL7Field[EI | str | None](
        position=1,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    action_code = HL7Field[ID | str](
        position=2,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    action_reason = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    role_of_participation = HL7Field[CWE | str](
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70912",    )
    person = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=5,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    person_provider_type = HL7Field[CWE | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    organization_unit_type = HL7Field[CWE | str | None](
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70406",    )
    organization = HL7Field[list[XON] | XON | list[str] | str | None](
        position=8,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    location = HL7Field[list[PL] | PL | list[str] | str | None](
        position=9,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    device = HL7Field[list[EI] | EI | list[str] | str | None](
        position=10,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    begin_date_time_arrival_time = HL7Field[DTM | str | None](
        position=11,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    end_date_time_departure_time = HL7Field[DTM | str | None](
        position=12,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    qualitative_duration = HL7Field[CWE | str | None](
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    address = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=14,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    telecommunication_address = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=15,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    udi_device_identifier = HL7Field[EI | str | None](
        position=16,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    device_manufacture_date = HL7Field[DTM | str | None](
        position=17,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    device_expiry_date = HL7Field[DTM | str | None](
        position=18,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    device_lot_number = HL7Field[ST | str | None](
        position=19,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    device_serial_number = HL7Field[ST | str | None](
        position=20,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    device_donation_identification = HL7Field[EI | str | None](
        position=21,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    device_type = HL7Field[CNE | str | None](
        position=22,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70961",    )
    preferred_method_of_contact = HL7Field[CWE | str | None](
        position=23,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70185",    )
    contact_identifiers = HL7Field[list[PLN] | PLN | list[str] | str | None](
        position=24,
        datatype="PLN",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70338",    )

class PSG(HL7Segment):
    _segment_id = "PSG"

    provider_product_service_group_number = HL7Field[EI | str](
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    payer_product_service_group_number = HL7Field[EI | str | None](
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    product_service_group_sequence_number = HL7Field[SI | str](
        position=3,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    adjudicate_as_group = HL7Field[ID | str](
        position=4,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70136",    )
    product_service_group_billed_amount = HL7Field[CP | str](
        position=5,
        datatype="CP",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    product_service_group_description = HL7Field[ST | str](
        position=6,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )

class PSH(HL7Segment):
    _segment_id = "PSH"

    report_type = HL7Field[ST | str](
        position=1,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    report_form_identifier = HL7Field[ST | str | None](
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    report_date = HL7Field[DTM | str](
        position=3,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    report_interval_start_date = HL7Field[DTM | str | None](
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    report_interval_end_date = HL7Field[DTM | str | None](
        position=5,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    quantity_manufactured = HL7Field[CQ | str | None](
        position=6,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    quantity_distributed = HL7Field[CQ | str | None](
        position=7,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    quantity_distributed_method = HL7Field[ID | str | None](
        position=8,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70329",    )
    quantity_distributed_comment = HL7Field[FT | str | None](
        position=9,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    quantity_in_use = HL7Field[CQ | str | None](
        position=10,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    quantity_in_use_method = HL7Field[ID | str | None](
        position=11,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70329",    )
    quantity_in_use_comment = HL7Field[FT | str | None](
        position=12,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    number_of_product_experience_reports_filed_by_facility = HL7Field[NM | str | None](
        position=13,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    number_of_product_experience_reports_filed_by_distributor = HL7Field[NM | str | None](
        position=14,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class PSL(HL7Segment):
    _segment_id = "PSL"

    provider_product_service_line_item_number = HL7Field[EI | str](
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    payer_product_service_line_item_number = HL7Field[EI | str | None](
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    product_service_line_item_sequence_number = HL7Field[SI | str](
        position=3,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    provider_tracking_id = HL7Field[EI | str | None](
        position=4,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    payer_tracking_id = HL7Field[EI | str | None](
        position=5,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    product_service_line_item_status = HL7Field[CWE | str](
        position=6,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70559",    )
    product_service_code = HL7Field[CWE | str](
        position=7,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70879",    )
    product_service_code_modifier = HL7Field[CWE | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70880",    )
    product_service_code_description = HL7Field[ST | str | None](
        position=9,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    product_service_effective_date = HL7Field[DTM | str | None](
        position=10,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    product_service_expiration_date = HL7Field[DTM | str | None](
        position=11,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    product_service_quantity = HL7Field[CQ | str | None](
        position=12,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70560",    )
    product_service_unit_cost = HL7Field[CP | str | None](
        position=13,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    number_of_items_per_unit = HL7Field[NM | str | None](
        position=14,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    product_service_gross_amount = HL7Field[CP | str | None](
        position=15,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    product_service_billed_amount = HL7Field[CP | str | None](
        position=16,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    product_service_clarification_code_type = HL7Field[CWE | str | None](
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70561",    )
    product_service_clarification_code_value = HL7Field[ST | str | None](
        position=18,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    health_document_reference_identifier = HL7Field[EI | str | None](
        position=19,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    processing_consideration_code = HL7Field[CWE | str | None](
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70562",    )
    restricted_disclosure_indicator = HL7Field[ID | str](
        position=21,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70532",    )
    related_product_service_code_indicator = HL7Field[CWE | str | None](
        position=22,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70879",    )
    product_service_amount_for_physician = HL7Field[CP | str | None](
        position=23,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    product_service_cost_factor = HL7Field[NM | str | None](
        position=24,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    cost_center = HL7Field[CX | str | None](
        position=25,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    billing_period = HL7Field[DR | str | None](
        position=26,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    days_without_billing = HL7Field[NM | str | None](
        position=27,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    session_no = HL7Field[NM | str | None](
        position=28,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    executing_physician_id = HL7Field[XCN | str | None](
        position=29,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    responsible_physician_id = HL7Field[XCN | str | None](
        position=30,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    role_executing_physician = HL7Field[CWE | str | None](
        position=31,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70881",    )
    medical_role_executing_physician = HL7Field[CWE | str | None](
        position=32,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70882",    )
    side_of_body = HL7Field[CWE | str | None](
        position=33,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70894",    )
    number_of_t_ps_pp = HL7Field[NM | str | None](
        position=34,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    tp_value_pp = HL7Field[CP | str | None](
        position=35,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    internal_scaling_factor_pp = HL7Field[NM | str | None](
        position=36,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    external_scaling_factor_pp = HL7Field[NM | str | None](
        position=37,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    amount_pp = HL7Field[CP | str | None](
        position=38,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    number_of_t_ps_technical_part = HL7Field[NM | str | None](
        position=39,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    tp_value_technical_part = HL7Field[CP | str | None](
        position=40,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    internal_scaling_factor_technical_part = HL7Field[NM | str | None](
        position=41,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    external_scaling_factor_technical_part = HL7Field[NM | str | None](
        position=42,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    amount_technical_part = HL7Field[CP | str | None](
        position=43,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    total_amount_professional_part_technical_part = HL7Field[CP | str | None](
        position=44,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    vat_rate = HL7Field[NM | str | None](
        position=45,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    main_service = HL7Field[ID | str | None](
        position=46,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    validation = HL7Field[ID | str | None](
        position=47,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    comment = HL7Field[ST | str | None](
        position=48,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class PSS(HL7Segment):
    _segment_id = "PSS"

    provider_product_service_section_number = HL7Field[EI | str](
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    payer_product_service_section_number = HL7Field[EI | str | None](
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    product_service_section_sequence_number = HL7Field[SI | str](
        position=3,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    billed_amount = HL7Field[CP | str](
        position=4,
        datatype="CP",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    section_description_or_heading = HL7Field[ST | str](
        position=5,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )

class PTH(HL7Segment):
    _segment_id = "PTH"

    action_code = HL7Field[ID | str](
        position=1,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    pathway_id = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    pathway_instance_id = HL7Field[EI | str](
        position=3,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    pathway_established_date_time = HL7Field[DTM | str](
        position=4,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    pathway_life_cycle_status = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    change_pathway_life_cycle_status_date_time = HL7Field[DTM | str | None](
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    mood_code = HL7Field[CNE | str | None](
        position=7,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70725",    )

class PV1(HL7Segment):
    _segment_id = "PV1"

    set_id_pv1 = HL7Field[SI | str | None](
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    patient_class = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70004",    )
    assigned_patient_location = HL7Field[PL | str | None](
        position=3,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    admission_type = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70007",    )
    preadmit_number = HL7Field[CX | str | None](
        position=5,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    prior_patient_location = HL7Field[PL | str | None](
        position=6,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    attending_doctor = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=7,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70010",    )
    referring_doctor = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=8,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70010",    )
    consulting_doctor = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=9,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    hospital_service = HL7Field[CWE | str | None](
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70069",    )
    temporary_location = HL7Field[PL | str | None](
        position=11,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    preadmit_test_indicator = HL7Field[CWE | str | None](
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70087",    )
    re_admission_indicator = HL7Field[CWE | str | None](
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70092",    )
    admit_source = HL7Field[CWE | str | None](
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70023",    )
    ambulatory_status = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70009",    )
    vip_indicator = HL7Field[CWE | str | None](
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70099",    )
    admitting_doctor = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=17,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70010",    )
    patient_type = HL7Field[CWE | str | None](
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70018",    )
    visit_number = HL7Field[CX | str | None](
        position=19,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    financial_class = HL7Field[list[FC] | FC | list[str] | str | None](
        position=20,
        datatype="FC",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70064",    )
    charge_price_indicator = HL7Field[CWE | str | None](
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70032",    )
    courtesy_code = HL7Field[CWE | str | None](
        position=22,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70045",    )
    credit_rating = HL7Field[CWE | str | None](
        position=23,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70046",    )
    contract_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70044",    )
    contract_effective_date = HL7Field[list[DT] | DT | list[str] | str | None](
        position=25,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    contract_amount = HL7Field[list[NM] | NM | list[str] | str | None](
        position=26,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    contract_period = HL7Field[list[NM] | NM | list[str] | str | None](
        position=27,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    interest_code = HL7Field[CWE | str | None](
        position=28,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70073",    )
    transfer_to_bad_debt_code = HL7Field[CWE | str | None](
        position=29,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70110",    )
    transfer_to_bad_debt_date = HL7Field[DT | str | None](
        position=30,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bad_debt_agency_code = HL7Field[CWE | str | None](
        position=31,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70021",    )
    bad_debt_transfer_amount = HL7Field[NM | str | None](
        position=32,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bad_debt_recovery_amount = HL7Field[NM | str | None](
        position=33,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    delete_account_indicator = HL7Field[CWE | str | None](
        position=34,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70111",    )
    delete_account_date = HL7Field[DT | str | None](
        position=35,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    discharge_disposition = HL7Field[CWE | str | None](
        position=36,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70112",    )
    discharged_to_location = HL7Field[DLD | str | None](
        position=37,
        datatype="DLD",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70113",    )
    diet_type = HL7Field[CWE | str | None](
        position=38,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70114",    )
    servicing_facility = HL7Field[CWE | str | None](
        position=39,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70115",    )
    account_status = HL7Field[CWE | str | None](
        position=41,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70117",    )
    pending_location = HL7Field[PL | str | None](
        position=42,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    prior_temporary_location = HL7Field[PL | str | None](
        position=43,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    admit_date_time = HL7Field[DTM | str | None](
        position=44,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    discharge_date_time = HL7Field[DTM | str | None](
        position=45,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    current_patient_balance = HL7Field[NM | str | None](
        position=46,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    total_charges = HL7Field[NM | str | None](
        position=47,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    total_adjustments = HL7Field[NM | str | None](
        position=48,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    total_payments = HL7Field[NM | str | None](
        position=49,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    alternate_visit_id = HL7Field[list[CX] | CX | list[str] | str | None](
        position=50,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70203",    )
    visit_indicator = HL7Field[CWE | str | None](
        position=51,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70326",    )
    service_episode_description = HL7Field[ST | str | None](
        position=53,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    service_episode_identifier = HL7Field[CX | str | None](
        position=54,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class PV2(HL7Segment):
    _segment_id = "PV2"

    prior_pending_location = HL7Field[PL | str | None](
        position=1,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    accommodation_code = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70129",    )
    admit_reason = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    transfer_reason = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    patient_valuables = HL7Field[list[ST] | ST | list[str] | str | None](
        position=5,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    patient_valuables_location = HL7Field[ST | str | None](
        position=6,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    visit_user_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70130",    )
    expected_admit_date_time = HL7Field[DTM | str | None](
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    expected_discharge_date_time = HL7Field[DTM | str | None](
        position=9,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    estimated_length_of_inpatient_stay = HL7Field[NM | str | None](
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    actual_length_of_inpatient_stay = HL7Field[NM | str | None](
        position=11,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    visit_description = HL7Field[ST | str | None](
        position=12,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    referral_source_code = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=13,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    previous_service_date = HL7Field[DT | str | None](
        position=14,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    employment_illness_related_indicator = HL7Field[ID | str | None](
        position=15,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    purge_status_code = HL7Field[CWE | str | None](
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70213",    )
    purge_status_date = HL7Field[DT | str | None](
        position=17,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    special_program_code = HL7Field[CWE | str | None](
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70214",    )
    retention_indicator = HL7Field[ID | str | None](
        position=19,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    expected_number_of_insurance_plans = HL7Field[NM | str | None](
        position=20,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    visit_publicity_code = HL7Field[CWE | str | None](
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70215",    )
    visit_protection_indicator = HL7Field[ID | str | None](
        position=22,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    clinic_organization_name = HL7Field[list[XON] | XON | list[str] | str | None](
        position=23,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    patient_status_code = HL7Field[CWE | str | None](
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70216",    )
    visit_priority_code = HL7Field[CWE | str | None](
        position=25,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70217",    )
    previous_treatment_date = HL7Field[DT | str | None](
        position=26,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    expected_discharge_disposition = HL7Field[CWE | str | None](
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70112",    )
    signature_on_file_date = HL7Field[DT | str | None](
        position=28,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    first_similar_illness_date = HL7Field[DT | str | None](
        position=29,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    patient_charge_adjustment_code = HL7Field[CWE | str | None](
        position=30,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70218",    )
    recurring_service_code = HL7Field[CWE | str | None](
        position=31,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70219",    )
    billing_media_code = HL7Field[ID | str | None](
        position=32,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    expected_surgery_date_and_time = HL7Field[DTM | str | None](
        position=33,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    military_partnership_code = HL7Field[ID | str | None](
        position=34,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    military_non_availability_code = HL7Field[ID | str | None](
        position=35,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    newborn_baby_indicator = HL7Field[ID | str | None](
        position=36,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    baby_detained_indicator = HL7Field[ID | str | None](
        position=37,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    mode_of_arrival_code = HL7Field[CWE | str | None](
        position=38,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70430",    )
    recreational_drug_use_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=39,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70431",    )
    admission_level_of_care_code = HL7Field[CWE | str | None](
        position=40,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70432",    )
    precaution_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=41,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70433",    )
    patient_condition_code = HL7Field[CWE | str | None](
        position=42,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70434",    )
    living_will_code = HL7Field[CWE | str | None](
        position=43,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70315",    )
    organ_donor_code = HL7Field[CWE | str | None](
        position=44,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70316",    )
    advance_directive_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=45,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70435",    )
    patient_status_effective_date = HL7Field[DT | str | None](
        position=46,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    expected_loa_return_date_time = HL7Field[DTM | str | None](
        position=47,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    expected_pre_admission_testing_date_time = HL7Field[DTM | str | None](
        position=48,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    notify_clergy_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=49,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70534",    )
    advance_directive_last_verified_date = HL7Field[DT | str | None](
        position=50,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class PYE(HL7Segment):
    _segment_id = "PYE"

    set_id_pye = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    payee_type = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70557",    )
    payee_relationship_to_invoice_patient = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70558",    )
    payee_identification_list = HL7Field[XON | str | None](
        position=4,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    payee_person_name = HL7Field[XPN | str | None](
        position=5,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    payee_address = HL7Field[XAD | str | None](
        position=6,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    payment_method = HL7Field[CWE | str | None](
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70570",    )

class QAK(HL7Segment):
    _segment_id = "QAK"

    query_tag = HL7Field[ST | str | None](
        position=1,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    query_response_status = HL7Field[ID | str | None](
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70208",    )
    message_query_name = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70471",    )
    hit_count_total = HL7Field[NM | str | None](
        position=4,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    this_payload = HL7Field[NM | str | None](
        position=5,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    hits_remaining = HL7Field[NM | str | None](
        position=6,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class QID(HL7Segment):
    _segment_id = "QID"

    query_tag = HL7Field[ST | str](
        position=1,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    message_query_name = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70471",    )

class QPD(HL7Segment):
    _segment_id = "QPD"

    message_query_name = HL7Field[CWE | str](
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70471",    )
    query_tag = HL7Field[ST | str | None](
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    user_parameters_in_successive_fields = HL7Field[varies | str | None](
        position=3,
        datatype="varies",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class QRD(HL7Segment):
    _segment_id = "QRD"

    pass

class QRF(HL7Segment):
    _segment_id = "QRF"

    pass

class QRI(HL7Segment):
    _segment_id = "QRI"

    candidate_confidence = HL7Field[NM | str | None](
        position=1,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    match_reason_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70392",    )
    algorithm_descriptor = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70393",    )

class RCP(HL7Segment):
    _segment_id = "RCP"

    query_priority = HL7Field[ID | str | None](
        position=1,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70091",    )
    quantity_limited_request = HL7Field[CQ | str | None](
        position=2,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70126",    )
    response_modality = HL7Field[CNE | str | None](
        position=3,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70394",    )
    execution_and_delivery_time = HL7Field[DTM | str | None](
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    modify_indicator = HL7Field[ID | str | None](
        position=5,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70395",    )
    sort_by_field = HL7Field[list[SRT] | SRT | list[str] | str | None](
        position=6,
        datatype="SRT",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    segment_group_inclusion = HL7Field[list[ID] | ID | list[str] | str | None](
        position=7,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70391",    )

class RDF(HL7Segment):
    _segment_id = "RDF"

    number_of_columns_per_row = HL7Field[NM | str](
        position=1,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    column_description = HL7Field[list[RCD] | RCD | list[str] | str](
        position=2,
        datatype="RCD",
        usage=Usage.REQUIRED,
        repeatable=True, table="HL70440",    )

class RDT(HL7Segment):
    _segment_id = "RDT"

    column_value = HL7Field[varies | str](
        position=1,
        datatype="varies",
        usage=Usage.REQUIRED,
        repeatable=False,    )

class REL(HL7Segment):
    _segment_id = "REL"

    set_id_rel = HL7Field[SI | str | None](
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    relationship_type = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70948",    )
    this_relationship_instance_identifier = HL7Field[EI | str](
        position=3,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    source_information_instance_identifier = HL7Field[EI | str](
        position=4,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    target_information_instance_identifier = HL7Field[EI | str](
        position=5,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    asserting_entity_instance_id = HL7Field[EI | str | None](
        position=6,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    asserting_person = HL7Field[XCN | str | None](
        position=7,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    asserting_organization = HL7Field[XON | str | None](
        position=8,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    assertor_address = HL7Field[XAD | str | None](
        position=9,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    assertor_contact = HL7Field[XTN | str | None](
        position=10,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    assertion_date_range = HL7Field[DR | str | None](
        position=11,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    negation_indicator = HL7Field[ID | str | None](
        position=12,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    certainty_of_relationship = HL7Field[CWE | str | None](
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    priority_no = HL7Field[NM | str | None](
        position=14,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    priority_sequence_no_rel_preference_for_consideration = HL7Field[NM | str | None](
        position=15,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    separability_indicator = HL7Field[ID | str | None](
        position=16,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    source_information_instance_object_type = HL7Field[ID | str | None](
        position=17,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70203",    )
    target_information_instance_object_type = HL7Field[ID | str | None](
        position=18,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70203",    )

class RF1(HL7Segment):
    _segment_id = "RF1"

    referral_status = HL7Field[CWE | str | None](
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70283",    )
    referral_priority = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70280",    )
    referral_type = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70281",    )
    referral_disposition = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70282",    )
    referral_category = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70284",    )
    originating_referral_identifier = HL7Field[EI | str](
        position=6,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    effective_date = HL7Field[DTM | str | None](
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    expiration_date = HL7Field[DTM | str | None](
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    process_date = HL7Field[DTM | str | None](
        position=9,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    referral_reason = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70336",    )
    external_referral_identifier = HL7Field[list[EI] | EI | list[str] | str | None](
        position=11,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    referral_documentation_completion_status = HL7Field[CWE | str | None](
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70865",    )
    planned_treatment_stop_date = HL7Field[DTM | str | None](
        position=13,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    referral_reason_text = HL7Field[ST | str | None](
        position=14,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    number_of_authorized_treatments_units = HL7Field[CQ | str | None](
        position=15,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    number_of_used_treatments_units = HL7Field[CQ | str | None](
        position=16,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    number_of_schedule_treatments_units = HL7Field[CQ | str | None](
        position=17,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    remaining_benefit_amount = HL7Field[MO | str | None](
        position=18,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    authorized_provider = HL7Field[XON | str | None](
        position=19,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    authorized_health_professional = HL7Field[XCN | str | None](
        position=20,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    source_text = HL7Field[ST | str | None](
        position=21,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    source_date = HL7Field[DTM | str | None](
        position=22,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    source_phone = HL7Field[XTN | str | None](
        position=23,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    comment = HL7Field[ST | str | None](
        position=24,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    action_code = HL7Field[ID | str | None](
        position=25,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70206",    )

class RFI(HL7Segment):
    _segment_id = "RFI"

    request_date = HL7Field[DTM | str](
        position=1,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    response_due_date = HL7Field[DTM | str](
        position=2,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    patient_consent = HL7Field[ID | str | None](
        position=3,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    date_additional_information_was_submitted = HL7Field[DTM | str | None](
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class RGS(HL7Segment):
    _segment_id = "RGS"

    set_id_rgs = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    segment_action_code = HL7Field[ID | str | None](
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70206",    )
    resource_group_id = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class RMI(HL7Segment):
    _segment_id = "RMI"

    risk_management_incident_code = HL7Field[CWE | str | None](
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70427",    )
    date_time_incident = HL7Field[DTM | str | None](
        position=2,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    incident_type_code = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70428",    )

class ROL(HL7Segment):
    _segment_id = "ROL"

    pass

class RQ1(HL7Segment):
    _segment_id = "RQ1"

    anticipated_price = HL7Field[ST | str | None](
        position=1,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    manufacturer_identifier = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70385",    )
    manufacturers_catalog = HL7Field[ST | str | None](
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    vendor_id = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70683",    )
    vendor_catalog = HL7Field[ST | str | None](
        position=5,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    taxable = HL7Field[ID | str | None](
        position=6,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    substitute_allowed = HL7Field[ID | str | None](
        position=7,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )

class RQD(HL7Segment):
    _segment_id = "RQD"

    requisition_line_number = HL7Field[SI | str | None](
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    item_code_internal = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70684",    )
    item_code_external = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70685",    )
    hospital_item_code = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70686",    )
    requisition_quantity = HL7Field[NM | str | None](
        position=5,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    requisition_unit_of_measure = HL7Field[CWE | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70687",    )
    cost_center_account_number = HL7Field[CX | str | None](
        position=7,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70319",    )
    item_natural_account_code = HL7Field[CWE | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70320",    )
    deliver_to_id = HL7Field[CWE | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70688",    )
    date_needed = HL7Field[DT | str | None](
        position=10,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class RXA(HL7Segment):
    _segment_id = "RXA"

    give_sub_id_counter = HL7Field[NM | str](
        position=1,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    administration_sub_id_counter = HL7Field[NM | str](
        position=2,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    date_time_start_of_administration = HL7Field[DTM | str](
        position=3,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    date_time_end_of_administration = HL7Field[DTM | str](
        position=4,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    administered_code = HL7Field[CWE | str](
        position=5,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70292",    )
    administered_amount = HL7Field[NM | str](
        position=6,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    administered_units = HL7Field[CWE | str | None](
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70689",    )
    administered_dosage_form = HL7Field[CWE | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70690",    )
    administration_notes = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70691",    )
    administering_provider = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=10,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    administered_per_time_unit = HL7Field[ST | str | None](
        position=12,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    administered_strength = HL7Field[NM | str | None](
        position=13,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    administered_strength_units = HL7Field[CWE | str | None](
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70692",    )
    substance_lot_number = HL7Field[list[ST] | ST | list[str] | str | None](
        position=15,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    substance_expiration_date = HL7Field[list[DTM] | DTM | list[str] | str | None](
        position=16,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    substance_manufacturer_name = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    substance_treatment_refusal_reason = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70693",    )
    indication = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=19,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70694",    )
    completion_status = HL7Field[ID | str | None](
        position=20,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70322",    )
    action_code_rxa = HL7Field[ID | str | None](
        position=21,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70206",    )
    system_entry_date_time = HL7Field[DTM | str | None](
        position=22,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    administered_drug_strength_volume = HL7Field[NM | str | None](
        position=23,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    administered_drug_strength_volume_units = HL7Field[CWE | str | None](
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70695",    )
    administered_barcode_identifier = HL7Field[CWE | str | None](
        position=25,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70696",    )
    pharmacy_order_type = HL7Field[ID | str | None](
        position=26,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70480",    )
    administer_at = HL7Field[PL | str | None](
        position=27,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    administered_at_address = HL7Field[XAD | str | None](
        position=28,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    administered_tag_identifier = HL7Field[list[EI] | EI | list[str] | str | None](
        position=29,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,    )

class RXC(HL7Segment):
    _segment_id = "RXC"

    rx_component_type = HL7Field[ID | str](
        position=1,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70166",    )
    component_code = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70697",    )
    component_amount = HL7Field[NM | str](
        position=3,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    component_units = HL7Field[CWE | str](
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70698",    )
    component_strength = HL7Field[NM | str | None](
        position=5,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    component_strength_units = HL7Field[CWE | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70699",    )
    supplementary_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70700",    )
    component_drug_strength_volume = HL7Field[NM | str | None](
        position=8,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    component_drug_strength_volume_units = HL7Field[CWE | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70701",    )
    dispense_amount = HL7Field[NM | str | None](
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    dispense_units = HL7Field[CWE | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70703",    )

class RXD(HL7Segment):
    _segment_id = "RXD"

    dispense_sub_id_counter = HL7Field[NM | str](
        position=1,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    dispense_give_code = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70292",    )
    date_time_dispensed = HL7Field[DTM | str](
        position=3,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    actual_dispense_amount = HL7Field[NM | str](
        position=4,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    actual_dispense_units = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70704",    )
    actual_dosage_form = HL7Field[CWE | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70705",    )
    prescription_number = HL7Field[ST | str](
        position=7,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    number_of_refills_remaining = HL7Field[NM | str | None](
        position=8,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    dispense_notes = HL7Field[list[ST] | ST | list[str] | str | None](
        position=9,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    dispensing_provider = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=10,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    substitution_status = HL7Field[ID | str | None](
        position=11,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70167",    )
    total_daily_dose = HL7Field[CQ | str | None](
        position=12,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    needs_human_review = HL7Field[ID | str | None](
        position=14,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    special_dispensing_instructions = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70706",    )
    actual_strength = HL7Field[NM | str | None](
        position=16,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    actual_strength_unit = HL7Field[CWE | str | None](
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70707",    )
    substance_lot_number = HL7Field[list[ST] | ST | list[str] | str | None](
        position=18,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    substance_expiration_date = HL7Field[list[DTM] | DTM | list[str] | str | None](
        position=19,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    substance_manufacturer_name = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    indication = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70694",    )
    dispense_package_size = HL7Field[NM | str | None](
        position=22,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    dispense_package_size_unit = HL7Field[CWE | str | None](
        position=23,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70709",    )
    dispense_package_method = HL7Field[ID | str | None](
        position=24,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70321",    )
    supplementary_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=25,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70700",    )
    initiating_location = HL7Field[CWE | str | None](
        position=26,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70711",    )
    packaging_assembly_location = HL7Field[CWE | str | None](
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70712",    )
    actual_drug_strength_volume = HL7Field[NM | str | None](
        position=28,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    actual_drug_strength_volume_units = HL7Field[CWE | str | None](
        position=29,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70713",    )
    dispense_to_pharmacy = HL7Field[CWE | str | None](
        position=30,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70714",    )
    dispense_to_pharmacy_address = HL7Field[XAD | str | None](
        position=31,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    pharmacy_order_type = HL7Field[ID | str | None](
        position=32,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70480",    )
    dispense_type = HL7Field[CWE | str | None](
        position=33,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70484",    )
    pharmacy_phone_number = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=34,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    dispense_tag_identifier = HL7Field[list[EI] | EI | list[str] | str | None](
        position=35,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,    )

class RXE(HL7Segment):
    _segment_id = "RXE"

    give_code = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70292",    )
    give_amount_minimum = HL7Field[NM | str](
        position=3,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    give_amount_maximum = HL7Field[NM | str | None](
        position=4,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    give_units = HL7Field[CWE | str](
        position=5,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70715",    )
    give_dosage_form = HL7Field[CWE | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70716",    )
    providers_administration_instructions = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70718",    )
    substitution_status = HL7Field[ID | str | None](
        position=9,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70167",    )
    dispense_amount = HL7Field[NM | str | None](
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    dispense_units = HL7Field[CWE | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70720",    )
    number_of_refills = HL7Field[NM | str | None](
        position=12,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    ordering_providers_dea_number = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=13,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    pharmacist_treatment_suppliers_verifier_id = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=14,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    prescription_number = HL7Field[ST | str | None](
        position=15,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    number_of_refills_remaining = HL7Field[NM | str | None](
        position=16,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    number_of_refills_doses_dispensed = HL7Field[NM | str | None](
        position=17,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    dt_of_most_recent_refill_or_dose_dispensed = HL7Field[DTM | str | None](
        position=18,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    total_daily_dose = HL7Field[CQ | str | None](
        position=19,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    needs_human_review = HL7Field[ID | str | None](
        position=20,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    special_dispensing_instructions = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70706",    )
    give_per_time_unit = HL7Field[ST | str | None](
        position=22,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    give_rate_amount = HL7Field[ST | str | None](
        position=23,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    give_rate_units = HL7Field[CWE | str | None](
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70722",    )
    give_strength = HL7Field[NM | str | None](
        position=25,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    give_strength_units = HL7Field[CWE | str | None](
        position=26,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70723",    )
    give_indication = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70724",    )
    dispense_package_size = HL7Field[NM | str | None](
        position=28,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    dispense_package_size_unit = HL7Field[CWE | str | None](
        position=29,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70709",    )
    dispense_package_method = HL7Field[ID | str | None](
        position=30,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70321",    )
    supplementary_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=31,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70700",    )
    original_order_date_time = HL7Field[DTM | str | None](
        position=32,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    give_drug_strength_volume = HL7Field[NM | str | None](
        position=33,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    give_drug_strength_volume_units = HL7Field[CWE | str | None](
        position=34,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70729",    )
    controlled_substance_schedule = HL7Field[CWE | str | None](
        position=35,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70477",    )
    formulary_status = HL7Field[ID | str | None](
        position=36,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70478",    )
    pharmaceutical_substance_alternative = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=37,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70730",    )
    pharmacy_of_most_recent_fill = HL7Field[CWE | str | None](
        position=38,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70732",    )
    initial_dispense_amount = HL7Field[NM | str | None](
        position=39,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    dispensing_pharmacy = HL7Field[CWE | str | None](
        position=40,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70733",    )
    dispensing_pharmacy_address = HL7Field[XAD | str | None](
        position=41,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    deliver_to_patient_location = HL7Field[PL | str | None](
        position=42,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    deliver_to_address = HL7Field[XAD | str | None](
        position=43,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    pharmacy_order_type = HL7Field[ID | str | None](
        position=44,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70480",    )
    pharmacy_phone_number = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=45,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )

class RXG(HL7Segment):
    _segment_id = "RXG"

    give_sub_id_counter = HL7Field[NM | str](
        position=1,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    dispense_sub_id_counter = HL7Field[NM | str | None](
        position=2,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    give_code = HL7Field[CWE | str](
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70292",    )
    give_amount_minimum = HL7Field[NM | str](
        position=5,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    give_amount_maximum = HL7Field[NM | str | None](
        position=6,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    give_units = HL7Field[CWE | str](
        position=7,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70715",    )
    give_dosage_form = HL7Field[CWE | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70716",    )
    administration_notes = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70691",    )
    substitution_status = HL7Field[ID | str | None](
        position=10,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70167",    )
    needs_human_review = HL7Field[ID | str | None](
        position=12,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    special_administration_instructions = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70738",    )
    give_per_time_unit = HL7Field[ST | str | None](
        position=14,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    give_rate_amount = HL7Field[ST | str | None](
        position=15,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    give_rate_units = HL7Field[CWE | str | None](
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70722",    )
    give_strength = HL7Field[NM | str | None](
        position=17,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    give_strength_units = HL7Field[CWE | str | None](
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70723",    )
    substance_lot_number = HL7Field[list[ST] | ST | list[str] | str | None](
        position=19,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    substance_expiration_date = HL7Field[list[DTM] | DTM | list[str] | str | None](
        position=20,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    substance_manufacturer_name = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    indication = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=22,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70694",    )
    give_drug_strength_volume = HL7Field[NM | str | None](
        position=23,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    give_drug_strength_volume_units = HL7Field[CWE | str | None](
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70744",    )
    give_barcode_identifier = HL7Field[CWE | str | None](
        position=25,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70745",    )
    pharmacy_order_type = HL7Field[ID | str | None](
        position=26,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70480",    )
    deliver_to_patient_location = HL7Field[PL | str | None](
        position=29,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    deliver_to_address = HL7Field[XAD | str | None](
        position=30,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    give_tag_identifier = HL7Field[list[EI] | EI | list[str] | str | None](
        position=31,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    dispense_amount = HL7Field[NM | str | None](
        position=32,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    dispense_units = HL7Field[CWE | str | None](
        position=33,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70746",    )

class RXO(HL7Segment):
    _segment_id = "RXO"

    requested_give_code = HL7Field[CWE | str | None](
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70747",    )
    requested_give_amount_minimum = HL7Field[NM | str | None](
        position=2,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    requested_give_amount_maximum = HL7Field[NM | str | None](
        position=3,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    requested_give_units = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70748",    )
    requested_dosage_form = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70750",    )
    providers_pharmacy_treatment_instructions = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70751",    )
    providers_administration_instructions = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70718",    )
    allow_substitutions = HL7Field[ID | str | None](
        position=9,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70161",    )
    requested_dispense_code = HL7Field[CWE | str | None](
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70753",    )
    requested_dispense_amount = HL7Field[NM | str | None](
        position=11,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    requested_dispense_units = HL7Field[CWE | str | None](
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70754",    )
    number_of_refills = HL7Field[NM | str | None](
        position=13,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    pharmacist_treatment_suppliers_verifier_id = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=15,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    needs_human_review = HL7Field[ID | str | None](
        position=16,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    requested_give_per_time_unit = HL7Field[ST | str | None](
        position=17,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    requested_give_strength = HL7Field[NM | str | None](
        position=18,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    requested_give_strength_units = HL7Field[CWE | str | None](
        position=19,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70756",    )
    indication = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70694",    )
    requested_give_rate_amount = HL7Field[ST | str | None](
        position=21,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    requested_give_rate_units = HL7Field[CWE | str | None](
        position=22,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70760",    )
    total_daily_dose = HL7Field[CQ | str | None](
        position=23,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    supplementary_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70700",    )
    requested_drug_strength_volume = HL7Field[NM | str | None](
        position=25,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    requested_drug_strength_volume_units = HL7Field[CWE | str | None](
        position=26,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70764",    )
    pharmacy_order_type = HL7Field[ID | str | None](
        position=27,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70480",    )
    dispensing_interval = HL7Field[NM | str | None](
        position=28,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    medication_instance_identifier = HL7Field[EI | str | None](
        position=29,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    segment_instance_identifier = HL7Field[EI | str | None](
        position=30,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    mood_code = HL7Field[CNE | str | None](
        position=31,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70725",    )
    dispensing_pharmacy = HL7Field[CWE | str | None](
        position=32,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70733",    )
    dispensing_pharmacy_address = HL7Field[XAD | str | None](
        position=33,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    deliver_to_patient_location = HL7Field[PL | str | None](
        position=34,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    deliver_to_address = HL7Field[XAD | str | None](
        position=35,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    pharmacy_phone_number = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=36,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )

class RXR(HL7Segment):
    _segment_id = "RXR"

    route = HL7Field[CWE | str](
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70162",    )
    administration_site = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70550",    )
    administration_device = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70164",    )
    administration_method = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70165",    )
    routing_instruction = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70766",    )
    administration_site_modifier = HL7Field[CWE | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70495",    )

class RXV(HL7Segment):
    _segment_id = "RXV"

    set_id_rxv = HL7Field[SI | str | None](
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bolus_type = HL7Field[ID | str](
        position=2,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70917",    )
    bolus_dose_amount = HL7Field[NM | str | None](
        position=3,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bolus_dose_amount_units = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70767",    )
    bolus_dose_volume = HL7Field[NM | str | None](
        position=5,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bolus_dose_volume_units = HL7Field[CWE | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70768",    )
    pca_type = HL7Field[ID | str](
        position=7,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70918",    )
    pca_dose_amount = HL7Field[NM | str | None](
        position=8,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    pca_dose_amount_units = HL7Field[CWE | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70769",    )
    pca_dose_amount_volume = HL7Field[NM | str | None](
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    pca_dose_amount_volume_units = HL7Field[CWE | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70770",    )
    max_dose_amount = HL7Field[NM | str | None](
        position=12,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    max_dose_amount_units = HL7Field[CWE | str | None](
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70772",    )
    max_dose_amount_volume = HL7Field[NM | str | None](
        position=14,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    max_dose_amount_volume_units = HL7Field[CWE | str | None](
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70773",    )
    max_dose_per_time = HL7Field[CQ | str](
        position=16,
        datatype="CQ",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    lockout_interval = HL7Field[CQ | str | None](
        position=17,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    syringe_manufacturer = HL7Field[CWE | str | None](
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    syringe_model_number = HL7Field[CWE | str | None](
        position=19,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    syringe_size = HL7Field[NM | str | None](
        position=20,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    syringe_size_units = HL7Field[CWE | str | None](
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    action_code = HL7Field[ID | str | None](
        position=22,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class SAC(HL7Segment):
    _segment_id = "SAC"

    external_accession_identifier = HL7Field[EI | str | None](
        position=1,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    accession_identifier = HL7Field[EI | str | None](
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    container_identifier = HL7Field[EI | str | None](
        position=3,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    primary_parent_container_identifier = HL7Field[EI | str | None](
        position=4,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    equipment_container_identifier = HL7Field[EI | str | None](
        position=5,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    registration_date_time = HL7Field[DTM | str | None](
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    container_status = HL7Field[CWE | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70370",    )
    carrier_type = HL7Field[CWE | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70378",    )
    carrier_identifier = HL7Field[EI | str | None](
        position=10,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    position_in_carrier = HL7Field[NA | str | None](
        position=11,
        datatype="NA",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    tray_type_sac = HL7Field[CWE | str | None](
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70379",    )
    tray_identifier = HL7Field[EI | str | None](
        position=13,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    position_in_tray = HL7Field[NA | str | None](
        position=14,
        datatype="NA",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    location = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70774",    )
    container_height = HL7Field[NM | str | None](
        position=16,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    container_diameter = HL7Field[NM | str | None](
        position=17,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    barrier_delta = HL7Field[NM | str | None](
        position=18,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bottom_delta = HL7Field[NM | str | None](
        position=19,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    container_height_diameter_delta_units = HL7Field[CWE | str | None](
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70775",    )
    container_volume = HL7Field[NM | str | None](
        position=21,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    available_specimen_volume = HL7Field[NM | str | None](
        position=22,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    initial_specimen_volume = HL7Field[NM | str | None](
        position=23,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    volume_units = HL7Field[CWE | str | None](
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70777",    )
    separator_type = HL7Field[CWE | str | None](
        position=25,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70380",    )
    cap_type = HL7Field[CWE | str | None](
        position=26,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70381",    )
    additive = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70371",    )
    specimen_component = HL7Field[CWE | str | None](
        position=28,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70372",    )
    dilution_factor = HL7Field[SN | str | None](
        position=29,
        datatype="SN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    treatment = HL7Field[CWE | str | None](
        position=30,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70373",    )
    temperature = HL7Field[SN | str | None](
        position=31,
        datatype="SN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    hemolysis_index = HL7Field[NM | str | None](
        position=32,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    hemolysis_index_units = HL7Field[CWE | str | None](
        position=33,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70779",    )
    lipemia_index = HL7Field[NM | str | None](
        position=34,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    lipemia_index_units = HL7Field[CWE | str | None](
        position=35,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70780",    )
    icterus_index = HL7Field[NM | str | None](
        position=36,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    icterus_index_units = HL7Field[CWE | str | None](
        position=37,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70781",    )
    fibrin_index = HL7Field[NM | str | None](
        position=38,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    fibrin_index_units = HL7Field[CWE | str | None](
        position=39,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70782",    )
    system_induced_contaminants = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=40,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70374",    )
    drug_interference = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=41,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70382",    )
    artificial_blood = HL7Field[CWE | str | None](
        position=42,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70375",    )
    special_handling_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=43,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70376",    )
    other_environmental_factors = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=44,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70377",    )
    container_length = HL7Field[CQ | str | None](
        position=45,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    container_width = HL7Field[CQ | str | None](
        position=46,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    container_form = HL7Field[CWE | str | None](
        position=47,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70967",    )
    container_material = HL7Field[CWE | str | None](
        position=48,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70968",    )
    container_common_name = HL7Field[CWE | str | None](
        position=49,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70969",    )

class SCD(HL7Segment):
    _segment_id = "SCD"

    cycle_start_time = HL7Field[TM | str | None](
        position=1,
        datatype="TM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    cycle_count = HL7Field[NM | str | None](
        position=2,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    temp_max = HL7Field[CQ | str | None](
        position=3,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    temp_min = HL7Field[CQ | str | None](
        position=4,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    load_number = HL7Field[NM | str | None](
        position=5,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    condition_time = HL7Field[CQ | str | None](
        position=6,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    sterilize_time = HL7Field[CQ | str | None](
        position=7,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    exhaust_time = HL7Field[CQ | str | None](
        position=8,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    total_cycle_time = HL7Field[CQ | str | None](
        position=9,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    device_status = HL7Field[CWE | str | None](
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70682",    )
    cycle_start_date_time = HL7Field[DTM | str | None](
        position=11,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    dry_time = HL7Field[CQ | str | None](
        position=12,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    leak_rate = HL7Field[CQ | str | None](
        position=13,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    control_temperature = HL7Field[CQ | str | None](
        position=14,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    sterilizer_temperature = HL7Field[CQ | str | None](
        position=15,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    cycle_complete_time = HL7Field[TM | str | None](
        position=16,
        datatype="TM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    under_temperature = HL7Field[CQ | str | None](
        position=17,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    over_temperature = HL7Field[CQ | str | None](
        position=18,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    abort_cycle = HL7Field[CNE | str | None](
        position=19,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    alarm = HL7Field[CNE | str | None](
        position=20,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    long_in_charge_phase = HL7Field[CNE | str | None](
        position=21,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    long_in_exhaust_phase = HL7Field[CNE | str | None](
        position=22,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    long_in_fast_exhaust_phase = HL7Field[CNE | str | None](
        position=23,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    reset = HL7Field[CNE | str | None](
        position=24,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    operator_unload = HL7Field[XCN | str | None](
        position=25,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    door_open = HL7Field[CNE | str | None](
        position=26,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    reading_failure = HL7Field[CNE | str | None](
        position=27,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    cycle_type = HL7Field[CWE | str | None](
        position=28,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70702",    )
    thermal_rinse_time = HL7Field[CQ | str | None](
        position=29,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    wash_time = HL7Field[CQ | str | None](
        position=30,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    injection_rate = HL7Field[CQ | str | None](
        position=31,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    procedure_code = HL7Field[CNE | str | None](
        position=32,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70088",    )
    patient_identifier_list = HL7Field[list[CX] | CX | list[str] | str | None](
        position=33,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    attending_doctor = HL7Field[XCN | str | None](
        position=34,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70010",    )
    dilution_factor = HL7Field[SN | str | None](
        position=35,
        datatype="SN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    fill_time = HL7Field[CQ | str | None](
        position=36,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inlet_temperature = HL7Field[CQ | str | None](
        position=37,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class SCH(HL7Segment):
    _segment_id = "SCH"

    placer_appointment_id = HL7Field[EI | str | None](
        position=1,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    filler_appointment_id = HL7Field[EI | str | None](
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    occurrence_number = HL7Field[NM | str | None](
        position=3,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    placer_order_group_number = HL7Field[EI | str | None](
        position=4,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    schedule_id = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    event_reason = HL7Field[CWE | str](
        position=6,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    appointment_reason = HL7Field[CWE | str | None](
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70276",    )
    appointment_type = HL7Field[CWE | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70277",    )
    appointment_duration_units = HL7Field[CNE | str | None](
        position=10,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    placer_contact_person = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=12,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    placer_contact_phone_number = HL7Field[XTN | str | None](
        position=13,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    placer_contact_address = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=14,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    placer_contact_location = HL7Field[PL | str | None](
        position=15,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    filler_contact_person = HL7Field[list[XCN] | XCN | list[str] | str](
        position=16,
        datatype="XCN",
        usage=Usage.REQUIRED,
        repeatable=True,    )
    filler_contact_phone_number = HL7Field[XTN | str | None](
        position=17,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    filler_contact_address = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=18,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    filler_contact_location = HL7Field[PL | str | None](
        position=19,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    entered_by_person = HL7Field[list[XCN] | XCN | list[str] | str](
        position=20,
        datatype="XCN",
        usage=Usage.REQUIRED,
        repeatable=True,    )
    entered_by_phone_number = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=21,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    entered_by_location = HL7Field[PL | str | None](
        position=22,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    parent_placer_appointment_id = HL7Field[EI | str | None](
        position=23,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    parent_filler_appointment_id = HL7Field[EI | str | None](
        position=24,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    filler_status_code = HL7Field[CWE | str | None](
        position=25,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70278",    )
    placer_order_number = HL7Field[list[EI] | EI | list[str] | str | None](
        position=26,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    filler_order_number = HL7Field[list[EI] | EI | list[str] | str | None](
        position=27,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    alternate_placer_order_group_number = HL7Field[EIP | str | None](
        position=28,
        datatype="EIP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class SCP(HL7Segment):
    _segment_id = "SCP"

    number_of_decontamination_sterilization_devices = HL7Field[NM | str | None](
        position=1,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    labor_calculation_type = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70651",    )
    date_format = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70653",    )
    device_number = HL7Field[EI | str | None](
        position=4,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    device_name = HL7Field[ST | str | None](
        position=5,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    device_model_name = HL7Field[ST | str | None](
        position=6,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    device_type = HL7Field[CWE | str | None](
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70657",    )
    lot_control = HL7Field[CWE | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70659",    )

class SDD(HL7Segment):
    _segment_id = "SDD"

    lot_number = HL7Field[EI | str | None](
        position=1,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    device_number = HL7Field[EI | str | None](
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    device_name = HL7Field[ST | str | None](
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    device_data_state = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70667",    )
    load_status = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70669",    )
    control_code = HL7Field[NM | str | None](
        position=6,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    operator_name = HL7Field[ST | str | None](
        position=7,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class SFT(HL7Segment):
    _segment_id = "SFT"

    software_vendor_organization = HL7Field[XON | str](
        position=1,
        datatype="XON",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    software_certified_version_or_release_number = HL7Field[ST | str](
        position=2,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    software_product_name = HL7Field[ST | str](
        position=3,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    software_binary_id = HL7Field[ST | str](
        position=4,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    software_product_information = HL7Field[TX | str | None](
        position=5,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    software_install_date = HL7Field[DTM | str | None](
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class SGH(HL7Segment):
    _segment_id = "SGH"

    set_id_sgh = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    segment_group_name = HL7Field[ST | str | None](
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class SGT(HL7Segment):
    _segment_id = "SGT"

    set_id_sgt = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    segment_group_name = HL7Field[ST | str | None](
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class SHP(HL7Segment):
    _segment_id = "SHP"

    shipment_id = HL7Field[EI | str](
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    internal_shipment_id = HL7Field[list[EI] | EI | list[str] | str | None](
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    shipment_status = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70905",    )
    shipment_status_date_time = HL7Field[DTM | str](
        position=4,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    shipment_status_reason = HL7Field[TX | str | None](
        position=5,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    shipment_priority = HL7Field[CWE | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70906",    )
    shipment_confidentiality = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70907",    )
    number_of_packages_in_shipment = HL7Field[NM | str | None](
        position=8,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    shipment_condition = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70544",    )
    shipment_handling_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70376",    )
    shipment_risk_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70489",    )
    action_code = HL7Field[ID | str | None](
        position=12,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class SID(HL7Segment):
    _segment_id = "SID"

    application_method_identifier = HL7Field[CWE | str | None](
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70783",    )
    substance_lot_number = HL7Field[ST | str | None](
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    substance_container_identifier = HL7Field[ST | str | None](
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    substance_manufacturer_identifier = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70385",    )

class SLT(HL7Segment):
    _segment_id = "SLT"

    device_number = HL7Field[EI | str | None](
        position=1,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    device_name = HL7Field[ST | str | None](
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    lot_number = HL7Field[EI | str | None](
        position=3,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    item_identifier = HL7Field[EI | str | None](
        position=4,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    bar_code = HL7Field[ST | str | None](
        position=5,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class SPM(HL7Segment):
    _segment_id = "SPM"

    set_id_spm = HL7Field[SI | str | None](
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    specimen_identifier = HL7Field[EIP | str | None](
        position=2,
        datatype="EIP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    specimen_parent_i_ds = HL7Field[list[EIP] | EIP | list[str] | str | None](
        position=3,
        datatype="EIP",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    specimen_type = HL7Field[CWE | str](
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70487",    )
    specimen_type_modifier = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70541",    )
    specimen_additives = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70371",    )
    specimen_collection_method = HL7Field[CWE | str | None](
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70488",    )
    specimen_source_site = HL7Field[CWE | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70784",    )
    specimen_source_site_modifier = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70542",    )
    specimen_collection_site = HL7Field[CWE | str | None](
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70543",    )
    specimen_role = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70369",    )
    specimen_collection_amount = HL7Field[CQ | str | None](
        position=12,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    grouped_specimen_count = HL7Field[NM | str | None](
        position=13,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    specimen_description = HL7Field[list[ST] | ST | list[str] | str | None](
        position=14,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    specimen_handling_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70376",    )
    specimen_risk_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70489",    )
    specimen_collection_date_time = HL7Field[DR | str | None](
        position=17,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    specimen_received_date_time = HL7Field[DTM | str | None](
        position=18,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    specimen_expiration_date_time = HL7Field[DTM | str | None](
        position=19,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    specimen_availability = HL7Field[ID | str | None](
        position=20,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    specimen_reject_reason = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70490",    )
    specimen_quality = HL7Field[CWE | str | None](
        position=22,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70491",    )
    specimen_appropriateness = HL7Field[CWE | str | None](
        position=23,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70492",    )
    specimen_condition = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70493",    )
    specimen_current_quantity = HL7Field[CQ | str | None](
        position=25,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    number_of_specimen_containers = HL7Field[NM | str | None](
        position=26,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    container_type = HL7Field[CWE | str | None](
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70785",    )
    container_condition = HL7Field[CWE | str | None](
        position=28,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70544",    )
    specimen_child_role = HL7Field[CWE | str | None](
        position=29,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70494",    )
    accession_id = HL7Field[list[CX] | CX | list[str] | str | None](
        position=30,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    other_specimen_id = HL7Field[list[CX] | CX | list[str] | str | None](
        position=31,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    shipment_id = HL7Field[EI | str | None](
        position=32,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    culture_start_date_time = HL7Field[DTM | str | None](
        position=33,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    culture_final_date_time = HL7Field[DTM | str | None](
        position=34,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    action_code = HL7Field[ID | str | None](
        position=35,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class STF(HL7Segment):
    _segment_id = "STF"

    primary_key_value_stf = HL7Field[CWE | str | None](
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70786",    )
    staff_identifier_list = HL7Field[list[CX] | CX | list[str] | str | None](
        position=2,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70061",    )
    staff_name = HL7Field[list[XPN] | XPN | list[str] | str | None](
        position=3,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    staff_type = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70182",    )
    administrative_sex = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70001",    )
    date_time_of_birth = HL7Field[DTM | str | None](
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    active_inactive_flag = HL7Field[ID | str | None](
        position=7,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70183",    )
    department = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70184",    )
    hospital_service_stf = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70069",    )
    phone = HL7Field[list[XTN] | XTN | list[str] | str | None](
        position=10,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    office_home_address_birthplace = HL7Field[list[XAD] | XAD | list[str] | str | None](
        position=11,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    institution_activation_date = HL7Field[list[DIN] | DIN | list[str] | str | None](
        position=12,
        datatype="DIN",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70537",    )
    institution_inactivation_date = HL7Field[list[DIN] | DIN | list[str] | str | None](
        position=13,
        datatype="DIN",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70537",    )
    backup_person_id = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    e_mail_address = HL7Field[list[ST] | ST | list[str] | str | None](
        position=15,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    preferred_method_of_contact = HL7Field[CWE | str | None](
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70185",    )
    marital_status = HL7Field[CWE | str | None](
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70002",    )
    job_title = HL7Field[ST | str | None](
        position=18,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    job_code_class = HL7Field[JCC | str | None](
        position=19,
        datatype="JCC",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    employment_status_code = HL7Field[CWE | str | None](
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70066",    )
    additional_insured_on_auto = HL7Field[ID | str | None](
        position=21,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    drivers_license_number_staff = HL7Field[DLN | str | None](
        position=22,
        datatype="DLN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    copy_auto_ins = HL7Field[ID | str | None](
        position=23,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    auto_ins_expires = HL7Field[DT | str | None](
        position=24,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    date_last_dmv_review = HL7Field[DT | str | None](
        position=25,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    date_next_dmv_review = HL7Field[DT | str | None](
        position=26,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    race = HL7Field[CWE | str | None](
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70005",    )
    ethnic_group = HL7Field[CWE | str | None](
        position=28,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70189",    )
    re_activation_approval_indicator = HL7Field[ID | str | None](
        position=29,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    citizenship = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=30,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70171",    )
    date_time_of_death = HL7Field[DTM | str | None](
        position=31,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    death_indicator = HL7Field[ID | str | None](
        position=32,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    institution_relationship_type_code = HL7Field[CWE | str | None](
        position=33,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70538",    )
    institution_relationship_period = HL7Field[DR | str | None](
        position=34,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    expected_return_date = HL7Field[DT | str | None](
        position=35,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    cost_center_code = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=36,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70539",    )
    generic_classification_indicator = HL7Field[ID | str | None](
        position=37,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    inactive_reason_code = HL7Field[CWE | str | None](
        position=38,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70540",    )
    generic_resource_type_or_category = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=39,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70771",    )
    religion = HL7Field[CWE | str | None](
        position=40,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70006",    )
    signature = HL7Field[ED | str | None](
        position=41,
        datatype="ED",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class STZ(HL7Segment):
    _segment_id = "STZ"

    sterilization_type = HL7Field[CWE | str | None](
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70806",    )
    sterilization_cycle = HL7Field[CWE | str | None](
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70702",    )
    maintenance_cycle = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70809",    )
    maintenance_type = HL7Field[CWE | str | None](
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70811",    )

class TCC(HL7Segment):
    _segment_id = "TCC"

    universal_service_identifier = HL7Field[CWE | str](
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    equipment_test_application_identifier = HL7Field[EI | str](
        position=2,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    auto_dilution_factor_default = HL7Field[SN | str | None](
        position=4,
        datatype="SN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    rerun_dilution_factor_default = HL7Field[SN | str | None](
        position=5,
        datatype="SN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    pre_dilution_factor_default = HL7Field[SN | str | None](
        position=6,
        datatype="SN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    endogenous_content_of_pre_dilution_diluent = HL7Field[SN | str | None](
        position=7,
        datatype="SN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    inventory_limits_warning_level = HL7Field[NM | str | None](
        position=8,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    automatic_rerun_allowed = HL7Field[ID | str | None](
        position=9,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    automatic_repeat_allowed = HL7Field[ID | str | None](
        position=10,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    automatic_reflex_allowed = HL7Field[ID | str | None](
        position=11,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    equipment_dynamic_range = HL7Field[SN | str | None](
        position=12,
        datatype="SN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    units = HL7Field[CWE | str | None](
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70623",    )
    processing_type = HL7Field[CWE | str | None](
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70388",    )
    test_criticality = HL7Field[CWE | str | None](
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class TCD(HL7Segment):
    _segment_id = "TCD"

    universal_service_identifier = HL7Field[CWE | str](
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    auto_dilution_factor = HL7Field[SN | str | None](
        position=2,
        datatype="SN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    rerun_dilution_factor = HL7Field[SN | str | None](
        position=3,
        datatype="SN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    pre_dilution_factor = HL7Field[SN | str | None](
        position=4,
        datatype="SN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    endogenous_content_of_pre_dilution_diluent = HL7Field[SN | str | None](
        position=5,
        datatype="SN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    automatic_repeat_allowed = HL7Field[ID | str | None](
        position=6,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    reflex_allowed = HL7Field[ID | str | None](
        position=7,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70136",    )
    analyte_repeat_status = HL7Field[CWE | str | None](
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70389",    )
    specimen_consumption_quantity = HL7Field[CQ | str | None](
        position=9,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    pool_size = HL7Field[NM | str | None](
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    auto_dilution_type = HL7Field[CWE | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70945",    )

class TQ1(HL7Segment):
    _segment_id = "TQ1"

    set_id_tq1 = HL7Field[SI | str | None](
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    quantity = HL7Field[CQ | str | None](
        position=2,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    repeat_pattern = HL7Field[list[RPT] | RPT | list[str] | str | None](
        position=3,
        datatype="RPT",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    explicit_time = HL7Field[list[TM] | TM | list[str] | str | None](
        position=4,
        datatype="TM",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    relative_time_and_units = HL7Field[list[CQ] | CQ | list[str] | str | None](
        position=5,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    service_duration = HL7Field[CQ | str | None](
        position=6,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    start_datetime = HL7Field[DTM | str | None](
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    end_datetime = HL7Field[DTM | str | None](
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    priority = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70485",    )
    condition_text = HL7Field[TX | str | None](
        position=10,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    text_instruction = HL7Field[TX | str | None](
        position=11,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    conjunction = HL7Field[ID | str | None](
        position=12,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70472",    )
    occurrence_duration = HL7Field[CQ | str | None](
        position=13,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    total_occurrences = HL7Field[NM | str | None](
        position=14,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class TQ2(HL7Segment):
    _segment_id = "TQ2"

    set_id_tq2 = HL7Field[SI | str | None](
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    sequence_results_flag = HL7Field[ID | str | None](
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70503",    )
    related_placer_number = HL7Field[list[EI] | EI | list[str] | str | None](
        position=3,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    related_filler_number = HL7Field[list[EI] | EI | list[str] | str | None](
        position=4,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    related_placer_group_number = HL7Field[list[EI] | EI | list[str] | str | None](
        position=5,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    sequence_condition_code = HL7Field[ID | str | None](
        position=6,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70504",    )
    cyclic_entry_exit_indicator = HL7Field[ID | str | None](
        position=7,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70505",    )
    sequence_condition_time_interval = HL7Field[CQ | str | None](
        position=8,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    cyclic_group_maximum_number_of_repeats = HL7Field[NM | str | None](
        position=9,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    special_service_request_relationship = HL7Field[ID | str | None](
        position=10,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70506",    )

class TXA(HL7Segment):
    _segment_id = "TXA"

    set_id_txa = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    document_type = HL7Field[CWE | str](
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70270",    )
    document_content_presentation = HL7Field[ID | str | None](
        position=3,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70191",    )
    activity_date_time = HL7Field[DTM | str | None](
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    primary_activity_provider_code_name = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=5,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    origination_date_time = HL7Field[DTM | str | None](
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    transcription_date_time = HL7Field[DTM | str | None](
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    edit_date_time = HL7Field[list[DTM] | DTM | list[str] | str | None](
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    originator_code_name = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=9,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    assigned_document_authenticator = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=10,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    transcriptionist_code_name = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=11,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    unique_document_number = HL7Field[EI | str](
        position=12,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    parent_document_number = HL7Field[EI | str | None](
        position=13,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    placer_order_number = HL7Field[list[EI] | EI | list[str] | str | None](
        position=14,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    filler_order_number = HL7Field[EI | str | None](
        position=15,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    unique_document_file_name = HL7Field[ST | str | None](
        position=16,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    document_completion_status = HL7Field[ID | str](
        position=17,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70271",    )
    document_confidentiality_status = HL7Field[ID | str | None](
        position=18,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70272",    )
    document_availability_status = HL7Field[ID | str | None](
        position=19,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70273",    )
    document_storage_status = HL7Field[ID | str | None](
        position=20,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70275",    )
    document_change_reason = HL7Field[ST | str | None](
        position=21,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    authentication_person_time_stamp_set = HL7Field[list[PPN] | PPN | list[str] | str | None](
        position=22,
        datatype="PPN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    distributed_copies_code_and_name_of_recipients = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=23,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    folder_assignment = HL7Field[list[CWE] | CWE | list[str] | str | None](
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True, table="HL70791",    )
    document_title = HL7Field[list[ST] | ST | list[str] | str | None](
        position=25,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    agreed_due_date_time = HL7Field[DTM | str | None](
        position=26,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    creating_facility = HL7Field[HD | str | None](
        position=27,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    creating_specialty = HL7Field[CWE | str | None](
        position=28,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70792",    )

class UAC(HL7Segment):
    _segment_id = "UAC"

    user_authentication_credential_type_code = HL7Field[CWE | str](
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False, table="HL70615",    )
    user_authentication_credential = HL7Field[ED | str](
        position=2,
        datatype="ED",
        usage=Usage.REQUIRED,
        repeatable=False,    )

class UB1(HL7Segment):
    _segment_id = "UB1"

    pass

class UB2(HL7Segment):
    _segment_id = "UB2"

    set_id_ub2 = HL7Field[SI | str | None](
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    co_insurance_days_9 = HL7Field[ST | str | None](
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    condition_code_24_30 = HL7Field[CWE | str | None](
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70043",    )
    covered_days_7 = HL7Field[ST | str | None](
        position=4,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    non_covered_days_8 = HL7Field[ST | str | None](
        position=5,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    value_amount_code_39_41 = HL7Field[UVC | str | None](
        position=6,
        datatype="UVC",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    occurrence_code_date_32_35 = HL7Field[OCD | str | None](
        position=7,
        datatype="OCD",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    occurrence_span_code_dates_36 = HL7Field[OSP | str | None](
        position=8,
        datatype="OSP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    uniform_billing_locator_2_state = HL7Field[ST | str | None](
        position=9,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    uniform_billing_locator_11_state = HL7Field[ST | str | None](
        position=10,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    uniform_billing_locator_31_national = HL7Field[ST | str | None](
        position=11,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    document_control_number = HL7Field[ST | str | None](
        position=12,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    uniform_billing_locator_49_national = HL7Field[ST | str | None](
        position=13,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    uniform_billing_locator_56_state = HL7Field[ST | str | None](
        position=14,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    uniform_billing_locator_57_sational = HL7Field[ST | str | None](
        position=15,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    uniform_billing_locator_78_state = HL7Field[ST | str | None](
        position=16,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    special_visit_count = HL7Field[NM | str | None](
        position=17,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class URD(HL7Segment):
    _segment_id = "URD"

    pass

class URS(HL7Segment):
    _segment_id = "URS"

    pass

class VAR(HL7Segment):
    _segment_id = "VAR"

    variance_instance_id = HL7Field[EI | str](
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    documented_date_time = HL7Field[DTM | str](
        position=2,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    stated_variance_date_time = HL7Field[DTM | str | None](
        position=3,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    variance_originator = HL7Field[list[XCN] | XCN | list[str] | str | None](
        position=4,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    variance_classification = HL7Field[CWE | str | None](
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    variance_description = HL7Field[list[ST] | ST | list[str] | str | None](
        position=6,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )

class VND(HL7Segment):
    _segment_id = "VND"

    set_id_vnd = HL7Field[SI | str](
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    vendor_identifier = HL7Field[EI | str | None](
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    vendor_name = HL7Field[ST | str | None](
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    vendor_catalog_number = HL7Field[EI | str | None](
        position=4,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    primary_vendor_indicator = HL7Field[CNE | str | None](
        position=5,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False, table="HL70532",    )
    corporation = HL7Field[list[EI] | EI | list[str] | str | None](
        position=6,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    primary_contact = HL7Field[XCN | str | None](
        position=7,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    contract_adjustment = HL7Field[MOP | str | None](
        position=8,
        datatype="MOP",
        usage=Usage.OPTIONAL,
        repeatable=False,    )
    associated_contract_id = HL7Field[list[EI] | EI | list[str] | str | None](
        position=9,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    class_of_trade = HL7Field[list[ST] | ST | list[str] | str | None](
        position=10,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,    )
    pricing_tier_level = HL7Field[CWE | str | None](
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,    )

class ZL7(HL7Segment):
    _segment_id = "ZL7"

    display_sort_key = HL7Field[NM | str](
        position=1,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,    )
    display_sort_key_2 = HL7Field[NM | str](
        position=2,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,    )

class Zxx(HL7Segment):
    _segment_id = "Zxx"

    pass

