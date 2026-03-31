from __future__ import annotations

from typing import Optional

from zato_hl7v2.base import HL7Segment, HL7Field, Usage
from zato_hl7v2.v2_9.primitives import (
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
from zato_hl7v2.v2_9.datatypes import (
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

    discharge_care_provider: Optional[XCN] = HL7Field(
        position=1,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70010",
    )
    transfer_medical_service_code: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70069",
    )
    severity_of_illness_code: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70421",
    )
    date_time_of_attestation: Optional[DTM] = HL7Field(
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    attested_by: Optional[XCN] = HL7Field(
        position=5,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    triage_code: Optional[CWE] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70422",
    )
    abstract_completion_date_time: Optional[DTM] = HL7Field(
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    abstracted_by: Optional[XCN] = HL7Field(
        position=8,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    case_category_code: Optional[CWE] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70423",
    )
    caesarian_section_indicator: Optional[ID] = HL7Field(
        position=10,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    gestation_category_code: Optional[CWE] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70424",
    )
    gestation_period_weeks: Optional[NM] = HL7Field(
        position=12,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    newborn_code: Optional[CWE] = HL7Field(
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70425",
    )
    stillborn_indicator: Optional[ID] = HL7Field(
        position=14,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )


class ACC(HL7Segment):
    _segment_id = "ACC"

    accident_date_time: Optional[DTM] = HL7Field(
        position=1,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    accident_code: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70050",
    )
    accident_location: Optional[ST] = HL7Field(
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    auto_accident_state: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70347",
    )
    accident_job_related_indicator: Optional[ID] = HL7Field(
        position=5,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    accident_death_indicator: Optional[ID] = HL7Field(
        position=6,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    entered_by: Optional[XCN] = HL7Field(
        position=7,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    accident_description: Optional[ST] = HL7Field(
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    brought_in_by: Optional[ST] = HL7Field(
        position=9,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    police_notified_indicator: Optional[ID] = HL7Field(
        position=10,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    accident_address: Optional[XAD] = HL7Field(
        position=11,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    degree_of_patient_liability: Optional[NM] = HL7Field(
        position=12,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    accident_identifier: Optional[list[EI]] = HL7Field(
        position=13,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )


class ADD(HL7Segment):
    _segment_id = "ADD"

    addendum_continuation_pointer: Optional[ST] = HL7Field(
        position=1,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class ADJ(HL7Segment):
    _segment_id = "ADJ"

    provider_adjustment_number: EI = HL7Field(
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    payer_adjustment_number: EI = HL7Field(
        position=2,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    adjustment_sequence_number: SI = HL7Field(
        position=3,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    adjustment_category: CWE = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70564",
    )
    adjustment_amount: Optional[CP] = HL7Field(
        position=5,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    adjustment_quantity: Optional[CQ] = HL7Field(
        position=6,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70560",
    )
    adjustment_reason_pa: Optional[CWE] = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70565",
    )
    adjustment_description: Optional[ST] = HL7Field(
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    original_value: Optional[NM] = HL7Field(
        position=9,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    substitute_value: Optional[NM] = HL7Field(
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    adjustment_action: Optional[CWE] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70569",
    )
    provider_adjustment_number_cross_reference: Optional[EI] = HL7Field(
        position=12,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    provider_product_service_line_item_number_cross_reference: Optional[EI] = HL7Field(
        position=13,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    adjustment_date: DTM = HL7Field(
        position=14,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    responsible_organization: Optional[XON] = HL7Field(
        position=15,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class AFF(HL7Segment):
    _segment_id = "AFF"

    set_id_aff: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    professional_organization: XON = HL7Field(
        position=2,
        datatype="XON",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    professional_organization_address: Optional[XAD] = HL7Field(
        position=3,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    professional_organization_affiliation_date_range: Optional[list[DR]] = HL7Field(
        position=4,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    professional_affiliation_additional_information: Optional[ST] = HL7Field(
        position=5,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class AIG(HL7Segment):
    _segment_id = "AIG"

    set_id_aig: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    segment_action_code: Optional[ID] = HL7Field(
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70206",
    )
    resource_id: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    resource_type: CWE = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    resource_group: Optional[list[CWE]] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    resource_quantity: Optional[NM] = HL7Field(
        position=6,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    resource_quantity_units: Optional[CNE] = HL7Field(
        position=7,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    start_date_time: Optional[DTM] = HL7Field(
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    start_date_time_offset: Optional[NM] = HL7Field(
        position=9,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    start_date_time_offset_units: Optional[CNE] = HL7Field(
        position=10,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    duration: Optional[NM] = HL7Field(
        position=11,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    duration_units: Optional[CNE] = HL7Field(
        position=12,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    allow_substitution_code: Optional[CWE] = HL7Field(
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70279",
    )
    filler_status_code: Optional[CWE] = HL7Field(
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70278",
    )


class AIL(HL7Segment):
    _segment_id = "AIL"

    set_id_ail: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    segment_action_code: Optional[ID] = HL7Field(
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70206",
    )
    location_resource_id: Optional[list[PL]] = HL7Field(
        position=3,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    location_type_ail: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70305",
    )
    location_group: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    start_date_time: Optional[DTM] = HL7Field(
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    start_date_time_offset: Optional[NM] = HL7Field(
        position=7,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    start_date_time_offset_units: Optional[CNE] = HL7Field(
        position=8,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    duration: Optional[NM] = HL7Field(
        position=9,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    duration_units: Optional[CNE] = HL7Field(
        position=10,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    allow_substitution_code: Optional[CWE] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70279",
    )
    filler_status_code: Optional[CWE] = HL7Field(
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70278",
    )


class AIP(HL7Segment):
    _segment_id = "AIP"

    set_id_aip: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    segment_action_code: Optional[ID] = HL7Field(
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70206",
    )
    personnel_resource_id: Optional[list[XCN]] = HL7Field(
        position=3,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    resource_type: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70182",
    )
    resource_group: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    start_date_time: Optional[DTM] = HL7Field(
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    start_date_time_offset: Optional[NM] = HL7Field(
        position=7,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    start_date_time_offset_units: Optional[CNE] = HL7Field(
        position=8,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    duration: Optional[NM] = HL7Field(
        position=9,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    duration_units: Optional[CNE] = HL7Field(
        position=10,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    allow_substitution_code: Optional[CWE] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70279",
    )
    filler_status_code: Optional[CWE] = HL7Field(
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70278",
    )


class AIS(HL7Segment):
    _segment_id = "AIS"

    set_id_ais: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    segment_action_code: Optional[ID] = HL7Field(
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70206",
    )
    universal_service_identifier: CWE = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    start_date_time: Optional[DTM] = HL7Field(
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    start_date_time_offset: Optional[NM] = HL7Field(
        position=5,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    start_date_time_offset_units: Optional[CNE] = HL7Field(
        position=6,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    duration: Optional[NM] = HL7Field(
        position=7,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    duration_units: Optional[CNE] = HL7Field(
        position=8,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    allow_substitution_code: Optional[CWE] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70279",
    )
    filler_status_code: Optional[CWE] = HL7Field(
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70278",
    )
    placer_supplemental_service_information: Optional[list[CWE]] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70411",
    )
    filler_supplemental_service_information: Optional[list[CWE]] = HL7Field(
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70411",
    )


class AL1(HL7Segment):
    _segment_id = "AL1"

    set_id_al1: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    allergen_type_code: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70127",
    )
    allergen_code_mnemonic_description: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    allergy_severity_code: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70128",
    )
    allergy_reaction_code: Optional[list[ST]] = HL7Field(
        position=5,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )


class APR(HL7Segment):
    _segment_id = "APR"

    time_selection_criteria: Optional[list[SCV]] = HL7Field(
        position=1,
        datatype="SCV",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70294",
    )
    resource_selection_criteria: Optional[list[SCV]] = HL7Field(
        position=2,
        datatype="SCV",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70294",
    )
    location_selection_criteria: Optional[list[SCV]] = HL7Field(
        position=3,
        datatype="SCV",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70294",
    )
    slot_spacing_criteria: Optional[NM] = HL7Field(
        position=4,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    filler_override_criteria: Optional[list[SCV]] = HL7Field(
        position=5,
        datatype="SCV",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )


class ARQ(HL7Segment):
    _segment_id = "ARQ"

    placer_appointment_id: EI = HL7Field(
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    filler_appointment_id: Optional[EI] = HL7Field(
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    occurrence_number: Optional[NM] = HL7Field(
        position=3,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    placer_order_group_number: Optional[EI] = HL7Field(
        position=4,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    schedule_id: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    request_event_reason: Optional[CWE] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    appointment_reason: Optional[CWE] = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70276",
    )
    appointment_type: Optional[CWE] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70277",
    )
    appointment_duration: Optional[NM] = HL7Field(
        position=9,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    appointment_duration_units: Optional[CNE] = HL7Field(
        position=10,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    requested_start_date_time_range: Optional[list[DR]] = HL7Field(
        position=11,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    priority_arq: Optional[ST] = HL7Field(
        position=12,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    repeating_interval: Optional[RI] = HL7Field(
        position=13,
        datatype="RI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    repeating_interval_duration: Optional[ST] = HL7Field(
        position=14,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    placer_contact_person: list[XCN] = HL7Field(
        position=15,
        datatype="XCN",
        usage=Usage.REQUIRED,
        repeatable=True,
    )
    placer_contact_phone_number: Optional[list[XTN]] = HL7Field(
        position=16,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    placer_contact_address: Optional[list[XAD]] = HL7Field(
        position=17,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    placer_contact_location: Optional[PL] = HL7Field(
        position=18,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    entered_by_person: list[XCN] = HL7Field(
        position=19,
        datatype="XCN",
        usage=Usage.REQUIRED,
        repeatable=True,
    )
    entered_by_phone_number: Optional[list[XTN]] = HL7Field(
        position=20,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    entered_by_location: Optional[PL] = HL7Field(
        position=21,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    parent_placer_appointment_id: Optional[EI] = HL7Field(
        position=22,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    parent_filler_appointment_id: Optional[EI] = HL7Field(
        position=23,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    placer_order_number: Optional[list[EI]] = HL7Field(
        position=24,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    filler_order_number: Optional[list[EI]] = HL7Field(
        position=25,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    alternate_placer_order_group_number: Optional[EIP] = HL7Field(
        position=26,
        datatype="EIP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class ARV(HL7Segment):
    _segment_id = "ARV"

    set_id: Optional[SI] = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    access_restriction_action_code: CNE = HL7Field(
        position=2,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70206",
    )
    access_restriction_value: CWE = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70717",
    )
    access_restriction_reason: Optional[list[CWE]] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70719",
    )
    special_access_restriction_instructions: Optional[list[ST]] = HL7Field(
        position=5,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    access_restriction_date_range: Optional[DR] = HL7Field(
        position=6,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    security_classification_tag: CWE = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70952",
    )
    security_handling_instructions: Optional[list[CWE]] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70953",
    )
    access_restriction_message_location: Optional[list[ERL]] = HL7Field(
        position=9,
        datatype="ERL",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    access_restriction_instance_identifier: Optional[EI] = HL7Field(
        position=10,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class AUT(HL7Segment):
    _segment_id = "AUT"

    authorizing_payor_plan_id: Optional[CWE] = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70072",
    )
    authorizing_payor_company_id: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70285",
    )
    authorizing_payor_company_name: Optional[ST] = HL7Field(
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    authorization_effective_date: Optional[DTM] = HL7Field(
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    authorization_expiration_date: Optional[DTM] = HL7Field(
        position=5,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    authorization_identifier: Optional[EI] = HL7Field(
        position=6,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    reimbursement_limit: Optional[CP] = HL7Field(
        position=7,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    requested_number_of_treatments: Optional[CQ] = HL7Field(
        position=8,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    authorized_number_of_treatments: Optional[CQ] = HL7Field(
        position=9,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    process_date: Optional[DTM] = HL7Field(
        position=10,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    requested_disciplines: Optional[list[CWE]] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70522",
    )
    authorized_disciplines: Optional[list[CWE]] = HL7Field(
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70546",
    )
    authorization_referral_type: CWE = HL7Field(
        position=13,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70551",
    )
    approval_status: Optional[CWE] = HL7Field(
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70563",
    )
    planned_treatment_stop_date: Optional[DTM] = HL7Field(
        position=15,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    clinical_service: Optional[CWE] = HL7Field(
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70573",
    )
    reason_text: Optional[ST] = HL7Field(
        position=17,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    number_of_authorized_treatments_units: Optional[CQ] = HL7Field(
        position=18,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    number_of_used_treatments_units: Optional[CQ] = HL7Field(
        position=19,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    number_of_schedule_treatments_units: Optional[CQ] = HL7Field(
        position=20,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    encounter_type: Optional[CWE] = HL7Field(
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70574",
    )
    remaining_benefit_amount: Optional[MO] = HL7Field(
        position=22,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    authorized_provider: Optional[XON] = HL7Field(
        position=23,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    authorized_health_professional: Optional[XCN] = HL7Field(
        position=24,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    source_text: Optional[ST] = HL7Field(
        position=25,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    source_date: Optional[DTM] = HL7Field(
        position=26,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    source_phone: Optional[XTN] = HL7Field(
        position=27,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    comment: Optional[ST] = HL7Field(
        position=28,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    action_code: Optional[ID] = HL7Field(
        position=29,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70206",
    )


class BHS(HL7Segment):
    _segment_id = "BHS"

    batch_field_separator: ST = HL7Field(
        position=1,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    batch_encoding_characters: ST = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    batch_sending_application: Optional[HD] = HL7Field(
        position=3,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    batch_sending_facility: Optional[HD] = HL7Field(
        position=4,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    batch_receiving_application: Optional[HD] = HL7Field(
        position=5,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    batch_receiving_facility: Optional[HD] = HL7Field(
        position=6,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    batch_creation_date_time: Optional[DTM] = HL7Field(
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    batch_security: Optional[ST] = HL7Field(
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    batch_name_id_type: Optional[ST] = HL7Field(
        position=9,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    batch_comment: Optional[ST] = HL7Field(
        position=10,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    batch_control_id: Optional[ST] = HL7Field(
        position=11,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    reference_batch_control_id: Optional[ST] = HL7Field(
        position=12,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    batch_sending_network_address: Optional[HD] = HL7Field(
        position=13,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    batch_receiving_network_address: Optional[HD] = HL7Field(
        position=14,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    security_classification_tag: Optional[CWE] = HL7Field(
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70952",
    )
    security_handling_instructions: Optional[list[CWE]] = HL7Field(
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70953",
    )
    special_access_restriction_instructions: Optional[list[ST]] = HL7Field(
        position=17,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )


class BLC(HL7Segment):
    _segment_id = "BLC"

    blood_product_code: Optional[CWE] = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70426",
    )
    blood_amount: Optional[CQ] = HL7Field(
        position=2,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class BLG(HL7Segment):
    _segment_id = "BLG"

    when_to_charge: Optional[CCD] = HL7Field(
        position=1,
        datatype="CCD",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70100",
    )
    charge_type: Optional[ID] = HL7Field(
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70122",
    )
    account_id: Optional[CX] = HL7Field(
        position=3,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    charge_type_reason: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70475",
    )


class BPO(HL7Segment):
    _segment_id = "BPO"

    set_id_bpo: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    bp_universal_service_identifier: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70575",
    )
    bp_processing_requirements: Optional[list[CWE]] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70508",
    )
    bp_quantity: NM = HL7Field(
        position=4,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    bp_amount: Optional[NM] = HL7Field(
        position=5,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bp_units: Optional[CWE] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70576",
    )
    bp_intended_use_date_time: Optional[DTM] = HL7Field(
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bp_intended_dispense_from_location: Optional[PL] = HL7Field(
        position=8,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bp_intended_dispense_from_address: Optional[XAD] = HL7Field(
        position=9,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bp_requested_dispense_date_time: Optional[DTM] = HL7Field(
        position=10,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bp_requested_dispense_to_location: Optional[PL] = HL7Field(
        position=11,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bp_requested_dispense_to_address: Optional[XAD] = HL7Field(
        position=12,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bp_indication_for_use: Optional[list[CWE]] = HL7Field(
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70509",
    )
    bp_informed_consent_indicator: Optional[ID] = HL7Field(
        position=14,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )


class BPX(HL7Segment):
    _segment_id = "BPX"

    set_id_bpx: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    bp_dispense_status: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70510",
    )
    bp_status: ID = HL7Field(
        position=3,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70511",
    )
    bp_date_time_of_status: DTM = HL7Field(
        position=4,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    bc_donation_id: Optional[EI] = HL7Field(
        position=5,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bc_component: Optional[CNE] = HL7Field(
        position=6,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70577",
    )
    bc_donation_type_intended_use: Optional[CNE] = HL7Field(
        position=7,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70578",
    )
    cp_commercial_product: Optional[CWE] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70512",
    )
    cp_manufacturer: Optional[XON] = HL7Field(
        position=9,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    cp_lot_number: Optional[EI] = HL7Field(
        position=10,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bp_blood_group: Optional[CNE] = HL7Field(
        position=11,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70579",
    )
    bc_special_testing: Optional[list[CNE]] = HL7Field(
        position=12,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70580",
    )
    bp_expiration_date_time: Optional[DTM] = HL7Field(
        position=13,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bp_quantity: NM = HL7Field(
        position=14,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    bp_amount: Optional[NM] = HL7Field(
        position=15,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bp_units: Optional[CWE] = HL7Field(
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70581",
    )
    bp_unique_id: Optional[EI] = HL7Field(
        position=17,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bp_actual_dispensed_to_location: Optional[PL] = HL7Field(
        position=18,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bp_actual_dispensed_to_address: Optional[XAD] = HL7Field(
        position=19,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bp_dispensed_to_receiver: Optional[XCN] = HL7Field(
        position=20,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bp_dispensing_individual: Optional[XCN] = HL7Field(
        position=21,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    action_code: Optional[ID] = HL7Field(
        position=22,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class BTS(HL7Segment):
    _segment_id = "BTS"

    batch_message_count: Optional[ST] = HL7Field(
        position=1,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    batch_comment: Optional[ST] = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    batch_totals: Optional[list[NM]] = HL7Field(
        position=3,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )


class BTX(HL7Segment):
    _segment_id = "BTX"

    set_id_btx: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    bc_donation_id: Optional[EI] = HL7Field(
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bc_component: Optional[CNE] = HL7Field(
        position=3,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70582",
    )
    bc_blood_group: Optional[CNE] = HL7Field(
        position=4,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70583",
    )
    cp_commercial_product: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70512",
    )
    cp_manufacturer: Optional[XON] = HL7Field(
        position=6,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    cp_lot_number: Optional[EI] = HL7Field(
        position=7,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bp_quantity: NM = HL7Field(
        position=8,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    bp_amount: Optional[NM] = HL7Field(
        position=9,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bp_units: Optional[CWE] = HL7Field(
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70584",
    )
    bp_transfusion_disposition_status: CWE = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70513",
    )
    bp_message_status: ID = HL7Field(
        position=12,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70511",
    )
    bp_date_time_of_status: DTM = HL7Field(
        position=13,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    bp_transfusion_administrator: Optional[XCN] = HL7Field(
        position=14,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bp_transfusion_verifier: Optional[XCN] = HL7Field(
        position=15,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bp_transfusion_start_date_time_of_status: Optional[DTM] = HL7Field(
        position=16,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bp_transfusion_end_date_time_of_status: Optional[DTM] = HL7Field(
        position=17,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bp_adverse_reaction_type: Optional[list[CWE]] = HL7Field(
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70514",
    )
    bp_transfusion_interrupted_reason: Optional[CWE] = HL7Field(
        position=19,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70515",
    )
    bp_unique_id: Optional[EI] = HL7Field(
        position=20,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    action_code: Optional[ID] = HL7Field(
        position=21,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class BUI(HL7Segment):
    _segment_id = "BUI"

    set_id_bui: Optional[SI] = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    blood_unit_identifier: EI = HL7Field(
        position=2,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    blood_unit_type: CWE = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70566",
    )
    blood_unit_weight: NM = HL7Field(
        position=4,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    weight_units: CNE = HL7Field(
        position=5,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70929",
    )
    blood_unit_volume: NM = HL7Field(
        position=6,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    volume_units: CNE = HL7Field(
        position=7,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70930",
    )
    container_catalog_number: ST = HL7Field(
        position=8,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    container_lot_number: ST = HL7Field(
        position=9,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    container_manufacturer: XON = HL7Field(
        position=10,
        datatype="XON",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    transport_temperature: NR = HL7Field(
        position=11,
        datatype="NR",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    transport_temperature_units: CNE = HL7Field(
        position=12,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70931",
    )
    action_code: Optional[ID] = HL7Field(
        position=13,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class CDM(HL7Segment):
    _segment_id = "CDM"

    primary_key_value_cdm: CWE = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    charge_code_alias: Optional[list[CWE]] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70132",
    )
    charge_description_short: ST = HL7Field(
        position=3,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    charge_description_long: Optional[ST] = HL7Field(
        position=4,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    description_override_indicator: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70268",
    )
    exploding_charges: Optional[list[CWE]] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70132",
    )
    procedure_code: Optional[list[CNE]] = HL7Field(
        position=7,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70088",
    )
    active_inactive_flag: Optional[ID] = HL7Field(
        position=8,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70183",
    )
    inventory_number: Optional[list[CWE]] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70463",
    )
    resource_load: Optional[NM] = HL7Field(
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    contract_number: Optional[list[CX]] = HL7Field(
        position=11,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    contract_organization: Optional[list[XON]] = HL7Field(
        position=12,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    room_fee_indicator: Optional[ID] = HL7Field(
        position=13,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )


class CDO(HL7Segment):
    _segment_id = "CDO"

    set_id_cdo: Optional[SI] = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    action_code: Optional[ID] = HL7Field(
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    cumulative_dosage_limit: Optional[CQ] = HL7Field(
        position=3,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    cumulative_dosage_limit_time_interval: Optional[CQ] = HL7Field(
        position=4,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70924",
    )


class CER(HL7Segment):
    _segment_id = "CER"

    set_id_cer: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    serial_number: Optional[ST] = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    version: Optional[ST] = HL7Field(
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    granting_authority: Optional[XON] = HL7Field(
        position=4,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    issuing_authority: Optional[XCN] = HL7Field(
        position=5,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    signature: Optional[ED] = HL7Field(
        position=6,
        datatype="ED",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    granting_country: Optional[ID] = HL7Field(
        position=7,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70399",
    )
    granting_state_province: Optional[CWE] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70347",
    )
    granting_county_parish: Optional[CWE] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70289",
    )
    certificate_type: Optional[CWE] = HL7Field(
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    certificate_domain: Optional[CWE] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    subject_id: Optional[EI] = HL7Field(
        position=12,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    subject_name: ST = HL7Field(
        position=13,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    subject_directory_attribute_extension: Optional[list[CWE]] = HL7Field(
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    subject_public_key_info: Optional[CWE] = HL7Field(
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    authority_key_identifier: Optional[CWE] = HL7Field(
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    basic_constraint: Optional[ID] = HL7Field(
        position=17,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    crl_distribution_point: Optional[list[CWE]] = HL7Field(
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    jurisdiction_country: Optional[ID] = HL7Field(
        position=19,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70399",
    )
    jurisdiction_state_province: Optional[CWE] = HL7Field(
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70347",
    )
    jurisdiction_county_parish: Optional[CWE] = HL7Field(
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70289",
    )
    jurisdiction_breadth: Optional[list[CWE]] = HL7Field(
        position=22,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70547",
    )
    granting_date: Optional[DTM] = HL7Field(
        position=23,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    issuing_date: Optional[DTM] = HL7Field(
        position=24,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    activation_date: Optional[DTM] = HL7Field(
        position=25,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inactivation_date: Optional[DTM] = HL7Field(
        position=26,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    expiration_date: Optional[DTM] = HL7Field(
        position=27,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    renewal_date: Optional[DTM] = HL7Field(
        position=28,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    revocation_date: Optional[DTM] = HL7Field(
        position=29,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    revocation_reason_code: Optional[CWE] = HL7Field(
        position=30,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    certificate_status_code: Optional[CWE] = HL7Field(
        position=31,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70536",
    )


class CM0(HL7Segment):
    _segment_id = "CM0"

    set_id_cm0: Optional[SI] = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    sponsor_study_id: EI = HL7Field(
        position=2,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    alternate_study_id: Optional[EI] = HL7Field(
        position=3,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    title_of_study: ST = HL7Field(
        position=4,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    chairman_of_study: Optional[list[XCN]] = HL7Field(
        position=5,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    last_irb_approval_date: Optional[DT] = HL7Field(
        position=6,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    total_accrual_to_date: Optional[NM] = HL7Field(
        position=7,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    last_accrual_date: Optional[DT] = HL7Field(
        position=8,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    contact_for_study: Optional[list[XCN]] = HL7Field(
        position=9,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    contacts_telephone_number: Optional[XTN] = HL7Field(
        position=10,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    contacts_address: Optional[list[XAD]] = HL7Field(
        position=11,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )


class CM1(HL7Segment):
    _segment_id = "CM1"

    set_id_cm1: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    study_phase_identifier: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    description_of_study_phase: ST = HL7Field(
        position=3,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )


class CM2(HL7Segment):
    _segment_id = "CM2"

    set_id_cm2: Optional[SI] = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    scheduled_time_point: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    description_of_time_point: Optional[ST] = HL7Field(
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    events_scheduled_this_time_point: CWE = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
    )


class CNS(HL7Segment):
    _segment_id = "CNS"

    starting_notification_reference_number: Optional[NM] = HL7Field(
        position=1,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    ending_notification_reference_number: Optional[NM] = HL7Field(
        position=2,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    starting_notification_date_time: Optional[DTM] = HL7Field(
        position=3,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    ending_notification_date_time: Optional[DTM] = HL7Field(
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    starting_notification_code: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70585",
    )
    ending_notification_code: Optional[CWE] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70586",
    )


class CON(HL7Segment):
    _segment_id = "CON"

    set_id_con: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    consent_type: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70496",
    )
    consent_form_id_and_version: Optional[ST] = HL7Field(
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    consent_form_number: Optional[EI] = HL7Field(
        position=4,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    consent_text: Optional[list[FT]] = HL7Field(
        position=5,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    subject_specific_consent_text: Optional[list[FT]] = HL7Field(
        position=6,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    consent_background_information: Optional[list[FT]] = HL7Field(
        position=7,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    subject_specific_consent_background_text: Optional[list[FT]] = HL7Field(
        position=8,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    consenter_imposed_limitations: Optional[list[FT]] = HL7Field(
        position=9,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    consent_mode: Optional[CNE] = HL7Field(
        position=10,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70497",
    )
    consent_status: CNE = HL7Field(
        position=11,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70498",
    )
    consent_discussion_date_time: Optional[DTM] = HL7Field(
        position=12,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    consent_decision_date_time: Optional[DTM] = HL7Field(
        position=13,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    consent_effective_date_time: Optional[DTM] = HL7Field(
        position=14,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    consent_end_date_time: Optional[DTM] = HL7Field(
        position=15,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    subject_competence_indicator: Optional[ID] = HL7Field(
        position=16,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    translator_assistance_indicator: Optional[ID] = HL7Field(
        position=17,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    language_translated_to: Optional[CWE] = HL7Field(
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70296",
    )
    informational_material_supplied_indicator: Optional[ID] = HL7Field(
        position=19,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    consent_bypass_reason: Optional[CWE] = HL7Field(
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70499",
    )
    consent_disclosure_level: Optional[ID] = HL7Field(
        position=21,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70500",
    )
    consent_non_disclosure_reason: Optional[CWE] = HL7Field(
        position=22,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70501",
    )
    non_subject_consenter_reason: Optional[CWE] = HL7Field(
        position=23,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70502",
    )
    consenter_id: list[XPN] = HL7Field(
        position=24,
        datatype="XPN",
        usage=Usage.REQUIRED,
        repeatable=True,
    )
    relationship_to_subject: list[CWE] = HL7Field(
        position=25,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=True,
        table="HL70548",
    )


class CSP(HL7Segment):
    _segment_id = "CSP"

    study_phase_identifier: CWE = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    datetime_study_phase_began: DTM = HL7Field(
        position=2,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    datetime_study_phase_ended: Optional[DTM] = HL7Field(
        position=3,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    study_phase_evaluability: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70588",
    )


class CSR(HL7Segment):
    _segment_id = "CSR"

    sponsor_study_id: EI = HL7Field(
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    alternate_study_id: Optional[EI] = HL7Field(
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    institution_registering_the_patient: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70589",
    )
    sponsor_patient_id: CX = HL7Field(
        position=4,
        datatype="CX",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    alternate_patient_id_csr: Optional[CX] = HL7Field(
        position=5,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    date_time_of_patient_study_registration: DTM = HL7Field(
        position=6,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    person_performing_study_registration: Optional[list[XCN]] = HL7Field(
        position=7,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    study_authorizing_provider: list[XCN] = HL7Field(
        position=8,
        datatype="XCN",
        usage=Usage.REQUIRED,
        repeatable=True,
    )
    date_time_patient_study_consent_signed: Optional[DTM] = HL7Field(
        position=9,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    patient_study_eligibility_status: Optional[CWE] = HL7Field(
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70590",
    )
    study_randomization_datetime: Optional[DTM] = HL7Field(
        position=11,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    randomized_study_arm: Optional[CWE] = HL7Field(
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70591",
    )
    stratum_for_study_randomization: Optional[CWE] = HL7Field(
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70592",
    )
    patient_evaluability_status: Optional[CWE] = HL7Field(
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70593",
    )
    date_time_ended_study: Optional[DTM] = HL7Field(
        position=15,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    reason_ended_study: Optional[CWE] = HL7Field(
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70594",
    )
    action_code: Optional[ID] = HL7Field(
        position=17,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class CSS(HL7Segment):
    _segment_id = "CSS"

    study_scheduled_time_point: CWE = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70595",
    )
    study_scheduled_patient_time_point: Optional[DTM] = HL7Field(
        position=2,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    study_quality_control_codes: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70596",
    )


class CTD(HL7Segment):
    _segment_id = "CTD"

    contact_role: list[CWE] = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=True,
        table="HL70131",
    )
    contact_name: Optional[list[XPN]] = HL7Field(
        position=2,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    contact_address: Optional[list[XAD]] = HL7Field(
        position=3,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    contact_location: Optional[PL] = HL7Field(
        position=4,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    contact_communication_information: Optional[list[XTN]] = HL7Field(
        position=5,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    preferred_method_of_contact: Optional[CWE] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70185",
    )
    contact_identifiers: Optional[list[PLN]] = HL7Field(
        position=7,
        datatype="PLN",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70338",
    )


class CTI(HL7Segment):
    _segment_id = "CTI"

    sponsor_study_id: EI = HL7Field(
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    study_phase_identifier: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    study_scheduled_time_point: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70595",
    )
    action_code: Optional[ID] = HL7Field(
        position=4,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class CTR(HL7Segment):
    _segment_id = "CTR"

    contract_identifier: EI = HL7Field(
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    contract_description: Optional[ST] = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    contract_status: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70536",
    )
    effective_date: DTM = HL7Field(
        position=4,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    expiration_date: DTM = HL7Field(
        position=5,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    contract_owner_name: Optional[XPN] = HL7Field(
        position=6,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    contract_originator_name: Optional[XPN] = HL7Field(
        position=7,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    supplier_type: CWE = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70946",
    )
    contract_type: Optional[CWE] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70965",
    )
    free_on_board_freight_terms: Optional[CNE] = HL7Field(
        position=10,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    price_protection_date: Optional[DTM] = HL7Field(
        position=11,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    fixed_price_contract_indicator: Optional[CNE] = HL7Field(
        position=12,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    group_purchasing_organization: Optional[XON] = HL7Field(
        position=13,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    maximum_markup: Optional[MOP] = HL7Field(
        position=14,
        datatype="MOP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    actual_markup: Optional[MOP] = HL7Field(
        position=15,
        datatype="MOP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    corporation: Optional[list[XON]] = HL7Field(
        position=16,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    parent_of_corporation: Optional[XON] = HL7Field(
        position=17,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    pricing_tier_level: Optional[CWE] = HL7Field(
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70966",
    )
    contract_priority: Optional[ST] = HL7Field(
        position=19,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    class_of_trade: Optional[CWE] = HL7Field(
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70947",
    )
    associated_contract_id: Optional[EI] = HL7Field(
        position=21,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class DB1(HL7Segment):
    _segment_id = "DB1"

    set_id_db1: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    disabled_person_code: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70334",
    )
    disabled_person_identifier: Optional[list[CX]] = HL7Field(
        position=3,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    disability_indicator: Optional[ID] = HL7Field(
        position=4,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    disability_start_date: Optional[DT] = HL7Field(
        position=5,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    disability_end_date: Optional[DT] = HL7Field(
        position=6,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    disability_return_to_work_date: Optional[DT] = HL7Field(
        position=7,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    disability_unable_to_work_date: Optional[DT] = HL7Field(
        position=8,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class DEV(HL7Segment):
    _segment_id = "DEV"

    action_code: ID = HL7Field(
        position=1,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    unique_device_identifier: Optional[EI] = HL7Field(
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    device_type: Optional[list[CNE]] = HL7Field(
        position=3,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70961",
    )
    device_status: Optional[list[CNE]] = HL7Field(
        position=4,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70962",
    )
    manufacturer_distributor: Optional[XON] = HL7Field(
        position=5,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    brand_name: Optional[ST] = HL7Field(
        position=6,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    model_identifier: Optional[ST] = HL7Field(
        position=7,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    catalogue_identifier: Optional[ST] = HL7Field(
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    udi_device_identifier: Optional[EI] = HL7Field(
        position=9,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    device_lot_number: Optional[ST] = HL7Field(
        position=10,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    device_serial_number: Optional[ST] = HL7Field(
        position=11,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    device_manufacture_date: Optional[DTM] = HL7Field(
        position=12,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    device_expiry_date: Optional[DTM] = HL7Field(
        position=13,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    safety_characteristics: Optional[list[CWE]] = HL7Field(
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70963",
    )
    device_donation_identification: Optional[EI] = HL7Field(
        position=15,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    software_version_number: Optional[ST] = HL7Field(
        position=16,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    implantation_status: Optional[CNE] = HL7Field(
        position=17,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70795",
    )


class DG1(HL7Segment):
    _segment_id = "DG1"

    set_id_dg1: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    diagnosis_code_dg1: CWE = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70051",
    )
    diagnosis_date_time: Optional[DTM] = HL7Field(
        position=5,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    diagnosis_type: CWE = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70052",
    )
    diagnosis_priority: Optional[NM] = HL7Field(
        position=15,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70359",
    )
    diagnosing_clinician: Optional[list[XCN]] = HL7Field(
        position=16,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    diagnosis_classification: Optional[CWE] = HL7Field(
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70228",
    )
    confidential_indicator: Optional[ID] = HL7Field(
        position=18,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    attestation_date_time: Optional[DTM] = HL7Field(
        position=19,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    diagnosis_identifier: Optional[EI] = HL7Field(
        position=20,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    diagnosis_action_code: Optional[ID] = HL7Field(
        position=21,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70206",
    )
    parent_diagnosis: Optional[EI] = HL7Field(
        position=22,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    drg_ccl_value_code: Optional[CWE] = HL7Field(
        position=23,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70728",
    )
    drg_grouping_usage: Optional[ID] = HL7Field(
        position=24,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    drg_diagnosis_determination_status: Optional[CWE] = HL7Field(
        position=25,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70731",
    )
    present_on_admission_poa_indicator: Optional[CWE] = HL7Field(
        position=26,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70895",
    )


class DMI(HL7Segment):
    _segment_id = "DMI"

    diagnostic_related_group: Optional[CNE] = HL7Field(
        position=1,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70055",
    )
    major_diagnostic_category: Optional[CNE] = HL7Field(
        position=2,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70118",
    )
    lower_and_upper_trim_points: Optional[NR] = HL7Field(
        position=3,
        datatype="NR",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    average_length_of_stay: Optional[NM] = HL7Field(
        position=4,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    relative_weight: Optional[NM] = HL7Field(
        position=5,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class DON(HL7Segment):
    _segment_id = "DON"

    donation_identification_number_din: Optional[EI] = HL7Field(
        position=1,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    donation_type: Optional[CNE] = HL7Field(
        position=2,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    phlebotomy_start_date_time: DTM = HL7Field(
        position=3,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    phlebotomy_end_date_time: DTM = HL7Field(
        position=4,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    donation_duration: NM = HL7Field(
        position=5,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    donation_duration_units: CNE = HL7Field(
        position=6,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70932",
    )
    intended_procedure_type: list[CNE] = HL7Field(
        position=7,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=True,
        table="HL70933",
    )
    actual_procedure_type: list[CNE] = HL7Field(
        position=8,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=True,
        table="HL70933",
    )
    donor_eligibility_flag: ID = HL7Field(
        position=9,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70136",
    )
    donor_eligibility_procedure_type: list[CNE] = HL7Field(
        position=10,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=True,
        table="HL70933",
    )
    donor_eligibility_date: DTM = HL7Field(
        position=11,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    process_interruption: CNE = HL7Field(
        position=12,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70923",
    )
    process_interruption_reason: CNE = HL7Field(
        position=13,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70935",
    )
    phlebotomy_issue: list[CNE] = HL7Field(
        position=14,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=True,
        table="HL70925",
    )
    intended_recipient_blood_relative: ID = HL7Field(
        position=15,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70136",
    )
    intended_recipient_name: XPN = HL7Field(
        position=16,
        datatype="XPN",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    intended_recipient_dob: DTM = HL7Field(
        position=17,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    intended_recipient_facility: XON = HL7Field(
        position=18,
        datatype="XON",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    intended_recipient_procedure_date: DTM = HL7Field(
        position=19,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    intended_recipient_ordering_provider: XPN = HL7Field(
        position=20,
        datatype="XPN",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    phlebotomy_status: CNE = HL7Field(
        position=21,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70926",
    )
    arm_stick: CNE = HL7Field(
        position=22,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70927",
    )
    bleed_start_phlebotomist: XPN = HL7Field(
        position=23,
        datatype="XPN",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    bleed_end_phlebotomist: XPN = HL7Field(
        position=24,
        datatype="XPN",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    aphaeresis_type_machine: ST = HL7Field(
        position=25,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    aphaeresis_machine_serial_number: ST = HL7Field(
        position=26,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    donor_reaction: ID = HL7Field(
        position=27,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70136",
    )
    final_review_staff_id: XPN = HL7Field(
        position=28,
        datatype="XPN",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    final_review_date_time: DTM = HL7Field(
        position=29,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    number_of_tubes_collected: NM = HL7Field(
        position=30,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    donation_sample_identifier: list[EI] = HL7Field(
        position=31,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=True,
    )
    donation_accept_staff: XCN = HL7Field(
        position=32,
        datatype="XCN",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    donation_material_review_staff: list[XCN] = HL7Field(
        position=33,
        datatype="XCN",
        usage=Usage.REQUIRED,
        repeatable=True,
    )
    action_code: Optional[ID] = HL7Field(
        position=34,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class DPS(HL7Segment):
    _segment_id = "DPS"

    diagnosis_code_mcp: CWE = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70051",
    )
    procedure_code: list[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=True,
        table="HL70941",
    )
    effective_date_time: Optional[DTM] = HL7Field(
        position=3,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    expiration_date_time: Optional[DTM] = HL7Field(
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    type_of_limitation: Optional[CNE] = HL7Field(
        position=5,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70940",
    )


class DRG(HL7Segment):
    _segment_id = "DRG"

    diagnostic_related_group: Optional[CNE] = HL7Field(
        position=1,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70055",
    )
    drg_assigned_date_time: Optional[DTM] = HL7Field(
        position=2,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    drg_approval_indicator: Optional[ID] = HL7Field(
        position=3,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    drg_grouper_review_code: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70056",
    )
    outlier_type: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70083",
    )
    outlier_days: Optional[NM] = HL7Field(
        position=6,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    outlier_cost: Optional[CP] = HL7Field(
        position=7,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    drg_payor: Optional[CWE] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70229",
    )
    outlier_reimbursement: Optional[CP] = HL7Field(
        position=9,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    confidential_indicator: Optional[ID] = HL7Field(
        position=10,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    drg_transfer_type: Optional[CWE] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70415",
    )
    name_of_coder: Optional[XPN] = HL7Field(
        position=12,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    grouper_status: Optional[CWE] = HL7Field(
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70734",
    )
    pccl_value_code: Optional[CWE] = HL7Field(
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70728",
    )
    effective_weight: Optional[NM] = HL7Field(
        position=15,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    monetary_amount: Optional[MO] = HL7Field(
        position=16,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    status_patient: Optional[CWE] = HL7Field(
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70739",
    )
    grouper_software_name: Optional[ST] = HL7Field(
        position=18,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    grouper_software_version: Optional[ST] = HL7Field(
        position=19,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    status_financial_calculation: Optional[CWE] = HL7Field(
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70742",
    )
    relative_discount_surcharge: Optional[MO] = HL7Field(
        position=21,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    basic_charge: Optional[MO] = HL7Field(
        position=22,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    total_charge: Optional[MO] = HL7Field(
        position=23,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    discount_surcharge: Optional[MO] = HL7Field(
        position=24,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    calculated_days: Optional[NM] = HL7Field(
        position=25,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    status_gender: Optional[CWE] = HL7Field(
        position=26,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70749",
    )
    status_age: Optional[CWE] = HL7Field(
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70749",
    )
    status_length_of_stay: Optional[CWE] = HL7Field(
        position=28,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70749",
    )
    status_same_day_flag: Optional[CWE] = HL7Field(
        position=29,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70749",
    )
    status_separation_mode: Optional[CWE] = HL7Field(
        position=30,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70749",
    )
    status_weight_at_birth: Optional[CWE] = HL7Field(
        position=31,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70755",
    )
    status_respiration_minutes: Optional[CWE] = HL7Field(
        position=32,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70757",
    )
    status_admission: Optional[CWE] = HL7Field(
        position=33,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70759",
    )


class DSC(HL7Segment):
    _segment_id = "DSC"

    continuation_pointer: Optional[ST] = HL7Field(
        position=1,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    continuation_style: Optional[ID] = HL7Field(
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70398",
    )


class DSP(HL7Segment):
    _segment_id = "DSP"

    set_id_dsp: Optional[SI] = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    display_level: Optional[SI] = HL7Field(
        position=2,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    data_line: TX = HL7Field(
        position=3,
        datatype="TX",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    logical_break_point: Optional[ST] = HL7Field(
        position=4,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    result_id: Optional[TX] = HL7Field(
        position=5,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class DST(HL7Segment):
    _segment_id = "DST"

    destination: CWE = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70943",
    )
    route: Optional[list[CWE]] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70944",
    )


class ECD(HL7Segment):
    _segment_id = "ECD"

    reference_command_number: NM = HL7Field(
        position=1,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    remote_control_command: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70368",
    )
    response_required: Optional[ID] = HL7Field(
        position=3,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    parameters: Optional[list[TX]] = HL7Field(
        position=5,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )


class ECR(HL7Segment):
    _segment_id = "ECR"

    command_response: CWE = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70387",
    )
    date_time_completed: DTM = HL7Field(
        position=2,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    command_response_parameters: Optional[list[TX]] = HL7Field(
        position=3,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )


class EDU(HL7Segment):
    _segment_id = "EDU"

    set_id_edu: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    academic_degree: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70360",
    )
    academic_degree_program_date_range: Optional[DR] = HL7Field(
        position=3,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    academic_degree_program_participation_date_range: Optional[DR] = HL7Field(
        position=4,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    academic_degree_granted_date: Optional[DT] = HL7Field(
        position=5,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    school: Optional[XON] = HL7Field(
        position=6,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    school_type_code: Optional[CWE] = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70402",
    )
    school_address: Optional[XAD] = HL7Field(
        position=8,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    major_field_of_study: Optional[list[CWE]] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )


class EQP(HL7Segment):
    _segment_id = "EQP"

    event_type: CWE = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70450",
    )
    file_name: Optional[ST] = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    start_date_time: DTM = HL7Field(
        position=3,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    end_date_time: Optional[DTM] = HL7Field(
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    transaction_data: FT = HL7Field(
        position=5,
        datatype="FT",
        usage=Usage.REQUIRED,
        repeatable=False,
    )


class EQU(HL7Segment):
    _segment_id = "EQU"

    equipment_instance_identifier: list[EI] = HL7Field(
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=True,
    )
    event_date_time: DTM = HL7Field(
        position=2,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    equipment_state: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70365",
    )
    local_remote_control_state: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70366",
    )
    alert_level: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70367",
    )
    expected_datetime_of_the_next_status_change: Optional[DTM] = HL7Field(
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class ERR(HL7Segment):
    _segment_id = "ERR"

    error_location: Optional[list[ERL]] = HL7Field(
        position=2,
        datatype="ERL",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    hl7_error_code: CWE = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70357",
    )
    severity: ID = HL7Field(
        position=4,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70516",
    )
    application_error_code: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70533",
    )
    application_error_parameter: Optional[ST] = HL7Field(
        position=6,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    diagnostic_information: Optional[TX] = HL7Field(
        position=7,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    user_message: Optional[TX] = HL7Field(
        position=8,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inform_person_indicator: Optional[list[CWE]] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70517",
    )
    override_type: Optional[CWE] = HL7Field(
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70518",
    )
    override_reason_code: Optional[list[CWE]] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70519",
    )
    help_desk_contact_point: Optional[list[XTN]] = HL7Field(
        position=12,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )


class EVN(HL7Segment):
    _segment_id = "EVN"

    recorded_date_time: DTM = HL7Field(
        position=2,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    date_time_planned_event: Optional[DTM] = HL7Field(
        position=3,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    event_reason_code: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70062",
    )
    operator_id: Optional[list[XCN]] = HL7Field(
        position=5,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70188",
    )
    event_occurred: Optional[DTM] = HL7Field(
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    event_facility: Optional[HD] = HL7Field(
        position=7,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class FAC(HL7Segment):
    _segment_id = "FAC"

    facility_id_fac: EI = HL7Field(
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    facility_type: Optional[ID] = HL7Field(
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70331",
    )
    facility_address: list[XAD] = HL7Field(
        position=3,
        datatype="XAD",
        usage=Usage.REQUIRED,
        repeatable=True,
    )
    facility_telecommunication: XTN = HL7Field(
        position=4,
        datatype="XTN",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    contact_person: Optional[list[XCN]] = HL7Field(
        position=5,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    contact_title: Optional[list[ST]] = HL7Field(
        position=6,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    contact_address: Optional[list[XAD]] = HL7Field(
        position=7,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    contact_telecommunication: Optional[list[XTN]] = HL7Field(
        position=8,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    signature_authority: list[XCN] = HL7Field(
        position=9,
        datatype="XCN",
        usage=Usage.REQUIRED,
        repeatable=True,
    )
    signature_authority_title: Optional[ST] = HL7Field(
        position=10,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    signature_authority_address: Optional[list[XAD]] = HL7Field(
        position=11,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    signature_authority_telecommunication: Optional[XTN] = HL7Field(
        position=12,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class FHS(HL7Segment):
    _segment_id = "FHS"

    file_field_separator: ST = HL7Field(
        position=1,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    file_encoding_characters: ST = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    file_sending_application: Optional[HD] = HL7Field(
        position=3,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    file_sending_facility: Optional[HD] = HL7Field(
        position=4,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    file_receiving_application: Optional[HD] = HL7Field(
        position=5,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    file_receiving_facility: Optional[HD] = HL7Field(
        position=6,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    file_creation_date_time: Optional[DTM] = HL7Field(
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    file_security: Optional[ST] = HL7Field(
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    file_name_id: Optional[ST] = HL7Field(
        position=9,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    file_header_comment: Optional[ST] = HL7Field(
        position=10,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    file_control_id: Optional[ST] = HL7Field(
        position=11,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    reference_file_control_id: Optional[ST] = HL7Field(
        position=12,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    file_sending_network_address: Optional[HD] = HL7Field(
        position=13,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    file_receiving_network_address: Optional[HD] = HL7Field(
        position=14,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    security_classification_tag: Optional[CWE] = HL7Field(
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70952",
    )
    security_handling_instructions: Optional[list[CWE]] = HL7Field(
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70953",
    )
    special_access_restriction_instructions: Optional[list[ST]] = HL7Field(
        position=17,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )


class FT1(HL7Segment):
    _segment_id = "FT1"

    set_id_ft1: Optional[SI] = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    transaction_id: Optional[CX] = HL7Field(
        position=2,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    transaction_batch_id: Optional[ST] = HL7Field(
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    transaction_date: DR = HL7Field(
        position=4,
        datatype="DR",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    transaction_posting_date: Optional[DTM] = HL7Field(
        position=5,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    transaction_type: CWE = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70017",
    )
    transaction_code: CWE = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70132",
    )
    transaction_quantity: Optional[NM] = HL7Field(
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    transaction_amount_extended: Optional[CP] = HL7Field(
        position=11,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    transaction_amount_unit: Optional[CP] = HL7Field(
        position=12,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    department_code: Optional[CWE] = HL7Field(
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70049",
    )
    health_plan_id: Optional[CWE] = HL7Field(
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70072",
    )
    insurance_amount: Optional[CP] = HL7Field(
        position=15,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    assigned_patient_location: Optional[PL] = HL7Field(
        position=16,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    fee_schedule: Optional[CWE] = HL7Field(
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70024",
    )
    patient_type: Optional[CWE] = HL7Field(
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70018",
    )
    diagnosis_code_ft1: Optional[list[CWE]] = HL7Field(
        position=19,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70051",
    )
    performed_by_code: Optional[list[XCN]] = HL7Field(
        position=20,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70084",
    )
    ordered_by_code: Optional[list[XCN]] = HL7Field(
        position=21,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    unit_cost: Optional[CP] = HL7Field(
        position=22,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    filler_order_number: Optional[EI] = HL7Field(
        position=23,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    entered_by_code: Optional[list[XCN]] = HL7Field(
        position=24,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    procedure_code: Optional[CNE] = HL7Field(
        position=25,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70088",
    )
    procedure_code_modifier: Optional[list[CNE]] = HL7Field(
        position=26,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70340",
    )
    advanced_beneficiary_notice_code: Optional[CWE] = HL7Field(
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70339",
    )
    medically_necessary_duplicate_procedure_reason: Optional[CWE] = HL7Field(
        position=28,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70476",
    )
    ndc_code: Optional[CWE] = HL7Field(
        position=29,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70549",
    )
    payment_reference_id: Optional[CX] = HL7Field(
        position=30,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    transaction_reference_key: Optional[list[SI]] = HL7Field(
        position=31,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    performing_facility: Optional[list[XON]] = HL7Field(
        position=32,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    ordering_facility: Optional[XON] = HL7Field(
        position=33,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    item_number: Optional[CWE] = HL7Field(
        position=34,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    model_number: Optional[ST] = HL7Field(
        position=35,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    special_processing_code: Optional[list[CWE]] = HL7Field(
        position=36,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    clinic_code: Optional[CWE] = HL7Field(
        position=37,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    referral_number: Optional[CX] = HL7Field(
        position=38,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    authorization_number: Optional[CX] = HL7Field(
        position=39,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    service_provider_taxonomy_code: Optional[CWE] = HL7Field(
        position=40,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    revenue_code: Optional[CWE] = HL7Field(
        position=41,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70456",
    )
    prescription_number: Optional[ST] = HL7Field(
        position=42,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    ndc_qty_and_uom: Optional[CQ] = HL7Field(
        position=43,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    dme_certificate_of_medical_necessity_transmission_code: Optional[CWE] = HL7Field(
        position=44,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    dme_certification_type_code: Optional[CWE] = HL7Field(
        position=45,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    dme_duration_value: Optional[NM] = HL7Field(
        position=46,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    dme_certification_revision_date: Optional[DT] = HL7Field(
        position=47,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    dme_initial_certification_date: Optional[DT] = HL7Field(
        position=48,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    dme_last_certification_date: Optional[DT] = HL7Field(
        position=49,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    dme_length_of_medical_necessity_days: Optional[NM] = HL7Field(
        position=50,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    dme_rental_price: Optional[MO] = HL7Field(
        position=51,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    dme_purchase_price: Optional[MO] = HL7Field(
        position=52,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    dme_frequency_code: Optional[CWE] = HL7Field(
        position=53,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    dme_certification_condition_indicator: Optional[ID] = HL7Field(
        position=54,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    dme_condition_indicator_code: Optional[CWE] = HL7Field(
        position=55,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    service_reason_code: Optional[CWE] = HL7Field(
        position=56,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70964",
    )


class FTS(HL7Segment):
    _segment_id = "FTS"

    file_batch_count: Optional[NM] = HL7Field(
        position=1,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    file_trailer_comment: Optional[ST] = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class GOL(HL7Segment):
    _segment_id = "GOL"

    action_code: ID = HL7Field(
        position=1,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    action_date_time: DTM = HL7Field(
        position=2,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    goal_id: CWE = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    goal_instance_id: EI = HL7Field(
        position=4,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    episode_of_care_id: Optional[EI] = HL7Field(
        position=5,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    goal_list_priority: Optional[NM] = HL7Field(
        position=6,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    goal_established_date_time: Optional[DTM] = HL7Field(
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    expected_goal_achieve_date_time: Optional[DTM] = HL7Field(
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    goal_classification: Optional[CWE] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    goal_management_discipline: Optional[CWE] = HL7Field(
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    current_goal_review_status: Optional[CWE] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    current_goal_review_date_time: Optional[DTM] = HL7Field(
        position=12,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    next_goal_review_date_time: Optional[DTM] = HL7Field(
        position=13,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    previous_goal_review_date_time: Optional[DTM] = HL7Field(
        position=14,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    goal_evaluation: Optional[CWE] = HL7Field(
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    goal_evaluation_comment: Optional[list[ST]] = HL7Field(
        position=17,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    goal_life_cycle_status: Optional[CWE] = HL7Field(
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    goal_life_cycle_status_date_time: Optional[DTM] = HL7Field(
        position=19,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    goal_target_type: Optional[list[CWE]] = HL7Field(
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    goal_target_name: Optional[list[XPN]] = HL7Field(
        position=21,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    mood_code: Optional[CNE] = HL7Field(
        position=22,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70725",
    )


class GP1(HL7Segment):
    _segment_id = "GP1"

    type_of_bill_code: CWE = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70455",
    )
    revenue_code: Optional[list[CWE]] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70456",
    )
    overall_claim_disposition_code: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70457",
    )
    oce_edits_per_visit_code: Optional[list[CWE]] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70458",
    )
    outlier_cost: Optional[CP] = HL7Field(
        position=5,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class GP2(HL7Segment):
    _segment_id = "GP2"

    revenue_code: Optional[CWE] = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70456",
    )
    number_of_service_units: Optional[NM] = HL7Field(
        position=2,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    charge: Optional[CP] = HL7Field(
        position=3,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    reimbursement_action_code: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70459",
    )
    denial_or_rejection_code: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70460",
    )
    oce_edit_code: Optional[list[CWE]] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70458",
    )
    ambulatory_payment_classification_code: Optional[CWE] = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70466",
    )
    modifier_edit_code: Optional[list[CWE]] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70467",
    )
    payment_adjustment_code: Optional[CWE] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70468",
    )
    packaging_status_code: Optional[CWE] = HL7Field(
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70469",
    )
    expected_cms_payment_amount: Optional[CP] = HL7Field(
        position=11,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    reimbursement_type_code: Optional[CWE] = HL7Field(
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70470",
    )
    co_pay_amount: Optional[CP] = HL7Field(
        position=13,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    pay_rate_per_service_unit: Optional[NM] = HL7Field(
        position=14,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class GT1(HL7Segment):
    _segment_id = "GT1"

    set_id_gt1: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    guarantor_number: Optional[list[CX]] = HL7Field(
        position=2,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    guarantor_name: list[XPN] = HL7Field(
        position=3,
        datatype="XPN",
        usage=Usage.REQUIRED,
        repeatable=True,
    )
    guarantor_spouse_name: Optional[list[XPN]] = HL7Field(
        position=4,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    guarantor_address: Optional[list[XAD]] = HL7Field(
        position=5,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    guarantor_ph_num_home: Optional[list[XTN]] = HL7Field(
        position=6,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    guarantor_ph_num_business: Optional[list[XTN]] = HL7Field(
        position=7,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    guarantor_date_time_of_birth: Optional[DTM] = HL7Field(
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    guarantor_administrative_sex: Optional[CWE] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70001",
    )
    guarantor_type: Optional[CWE] = HL7Field(
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70068",
    )
    guarantor_relationship: Optional[CWE] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70063",
    )
    guarantor_ssn: Optional[ST] = HL7Field(
        position=12,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    guarantor_date_begin: Optional[DT] = HL7Field(
        position=13,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    guarantor_date_end: Optional[DT] = HL7Field(
        position=14,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    guarantor_priority: Optional[NM] = HL7Field(
        position=15,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    guarantor_employer_name: Optional[list[XPN]] = HL7Field(
        position=16,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    guarantor_employer_address: Optional[list[XAD]] = HL7Field(
        position=17,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    guarantor_employer_phone_number: Optional[list[XTN]] = HL7Field(
        position=18,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    guarantor_employee_id_number: Optional[list[CX]] = HL7Field(
        position=19,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    guarantor_employment_status: Optional[CWE] = HL7Field(
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70066",
    )
    guarantor_organization_name: Optional[list[XON]] = HL7Field(
        position=21,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    guarantor_billing_hold_flag: Optional[ID] = HL7Field(
        position=22,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    guarantor_credit_rating_code: Optional[CWE] = HL7Field(
        position=23,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70341",
    )
    guarantor_death_date_and_time: Optional[DTM] = HL7Field(
        position=24,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    guarantor_death_flag: Optional[ID] = HL7Field(
        position=25,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    guarantor_charge_adjustment_code: Optional[CWE] = HL7Field(
        position=26,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70218",
    )
    guarantor_household_annual_income: Optional[CP] = HL7Field(
        position=27,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    guarantor_household_size: Optional[NM] = HL7Field(
        position=28,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    guarantor_employer_id_number: Optional[list[CX]] = HL7Field(
        position=29,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    guarantor_marital_status_code: Optional[CWE] = HL7Field(
        position=30,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70002",
    )
    guarantor_hire_effective_date: Optional[DT] = HL7Field(
        position=31,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    employment_stop_date: Optional[DT] = HL7Field(
        position=32,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    living_dependency: Optional[CWE] = HL7Field(
        position=33,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70223",
    )
    ambulatory_status: Optional[list[CWE]] = HL7Field(
        position=34,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70009",
    )
    citizenship: Optional[list[CWE]] = HL7Field(
        position=35,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70171",
    )
    primary_language: Optional[CWE] = HL7Field(
        position=36,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70296",
    )
    living_arrangement: Optional[CWE] = HL7Field(
        position=37,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70220",
    )
    publicity_code: Optional[CWE] = HL7Field(
        position=38,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70215",
    )
    protection_indicator: Optional[ID] = HL7Field(
        position=39,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    student_indicator: Optional[CWE] = HL7Field(
        position=40,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70231",
    )
    religion: Optional[CWE] = HL7Field(
        position=41,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70006",
    )
    mothers_maiden_name: Optional[list[XPN]] = HL7Field(
        position=42,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    nationality: Optional[CWE] = HL7Field(
        position=43,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70212",
    )
    ethnic_group: Optional[list[CWE]] = HL7Field(
        position=44,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70189",
    )
    contact_persons_name: Optional[list[XPN]] = HL7Field(
        position=45,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    contact_persons_telephone_number: Optional[list[XTN]] = HL7Field(
        position=46,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    contact_reason: Optional[CWE] = HL7Field(
        position=47,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70222",
    )
    contact_relationship: Optional[CWE] = HL7Field(
        position=48,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70063",
    )
    job_title: Optional[ST] = HL7Field(
        position=49,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    job_code_class: Optional[JCC] = HL7Field(
        position=50,
        datatype="JCC",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    guarantor_employers_organization_name: Optional[list[XON]] = HL7Field(
        position=51,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    handicap: Optional[CWE] = HL7Field(
        position=52,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70295",
    )
    job_status: Optional[CWE] = HL7Field(
        position=53,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70311",
    )
    guarantor_financial_class: Optional[FC] = HL7Field(
        position=54,
        datatype="FC",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    guarantor_race: Optional[list[CWE]] = HL7Field(
        position=55,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70005",
    )
    guarantor_birth_place: Optional[ST] = HL7Field(
        position=56,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    vip_indicator: Optional[CWE] = HL7Field(
        position=57,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70099",
    )


class Hxx(HL7Segment):
    _segment_id = "Hxx"

    pass


class IAM(HL7Segment):
    _segment_id = "IAM"

    set_id_iam: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    allergen_type_code: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70127",
    )
    allergen_code_mnemonic_description: CWE = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    allergy_severity_code: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70128",
    )
    allergy_reaction_code: Optional[list[ST]] = HL7Field(
        position=5,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    allergy_action_code: CNE = HL7Field(
        position=6,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70206",
    )
    allergy_unique_identifier: Optional[EI] = HL7Field(
        position=7,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    action_reason: Optional[ST] = HL7Field(
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    sensitivity_to_causative_agent_code: Optional[CWE] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70436",
    )
    allergen_group_code_mnemonic_description: Optional[CWE] = HL7Field(
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    onset_date: Optional[DT] = HL7Field(
        position=11,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    onset_date_text: Optional[ST] = HL7Field(
        position=12,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    reported_date_time: Optional[DTM] = HL7Field(
        position=13,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    reported_by: Optional[XPN] = HL7Field(
        position=14,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    relationship_to_patient_code: Optional[CWE] = HL7Field(
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70063",
    )
    alert_device_code: Optional[CWE] = HL7Field(
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70437",
    )
    allergy_clinical_status_code: Optional[CWE] = HL7Field(
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70438",
    )
    statused_by_person: Optional[XCN] = HL7Field(
        position=18,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    statused_by_organization: Optional[XON] = HL7Field(
        position=19,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    statused_at_date_time: Optional[DTM] = HL7Field(
        position=20,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inactivated_by_person: Optional[XCN] = HL7Field(
        position=21,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inactivated_date_time: Optional[DTM] = HL7Field(
        position=22,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    initially_recorded_by_person: Optional[XCN] = HL7Field(
        position=23,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    initially_recorded_date_time: Optional[DTM] = HL7Field(
        position=24,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    modified_by_person: Optional[XCN] = HL7Field(
        position=25,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    modified_date_time: Optional[DTM] = HL7Field(
        position=26,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    clinician_identified_code: Optional[CWE] = HL7Field(
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    initially_recorded_by_organization: Optional[XON] = HL7Field(
        position=28,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    modified_by_organization: Optional[XON] = HL7Field(
        position=29,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inactivated_by_organization: Optional[XON] = HL7Field(
        position=30,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class IAR(HL7Segment):
    _segment_id = "IAR"

    allergy_reaction_code: CWE = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    allergy_severity_code: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70128",
    )
    sensitivity_to_causative_agent_code: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70436",
    )
    management: Optional[ST] = HL7Field(
        position=4,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class IIM(HL7Segment):
    _segment_id = "IIM"

    primary_key_value_iim: CWE = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    service_item_code: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    inventory_lot_number: Optional[ST] = HL7Field(
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inventory_expiration_date: Optional[DTM] = HL7Field(
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inventory_manufacturer_name: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inventory_location: Optional[CWE] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inventory_received_date: Optional[DTM] = HL7Field(
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inventory_received_quantity: Optional[NM] = HL7Field(
        position=8,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inventory_received_quantity_unit: Optional[CWE] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inventory_received_item_cost: Optional[MO] = HL7Field(
        position=10,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inventory_on_hand_date: Optional[DTM] = HL7Field(
        position=11,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inventory_on_hand_quantity: Optional[NM] = HL7Field(
        position=12,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inventory_on_hand_quantity_unit: Optional[CWE] = HL7Field(
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    procedure_code: Optional[CNE] = HL7Field(
        position=14,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70088",
    )
    procedure_code_modifier: Optional[list[CNE]] = HL7Field(
        position=15,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70340",
    )


class ILT(HL7Segment):
    _segment_id = "ILT"

    set_id_ilt: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    inventory_lot_number: ST = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    inventory_expiration_date: Optional[DTM] = HL7Field(
        position=3,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inventory_received_date: Optional[DTM] = HL7Field(
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inventory_received_quantity: Optional[NM] = HL7Field(
        position=5,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inventory_received_quantity_unit: Optional[CWE] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inventory_received_item_cost: Optional[MO] = HL7Field(
        position=7,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inventory_on_hand_date: Optional[DTM] = HL7Field(
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inventory_on_hand_quantity: Optional[NM] = HL7Field(
        position=9,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inventory_on_hand_quantity_unit: Optional[CWE] = HL7Field(
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class IN1(HL7Segment):
    _segment_id = "IN1"

    set_id_in1: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    health_plan_id: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70072",
    )
    insurance_company_id: list[CX] = HL7Field(
        position=3,
        datatype="CX",
        usage=Usage.REQUIRED,
        repeatable=True,
    )
    insurance_company_name: Optional[list[XON]] = HL7Field(
        position=4,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    insurance_company_address: Optional[list[XAD]] = HL7Field(
        position=5,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    insurance_co_contact_person: Optional[list[XPN]] = HL7Field(
        position=6,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    insurance_co_phone_number: Optional[list[XTN]] = HL7Field(
        position=7,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    group_number: Optional[ST] = HL7Field(
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    group_name: Optional[list[XON]] = HL7Field(
        position=9,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    insureds_group_emp_id: Optional[list[CX]] = HL7Field(
        position=10,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    insureds_group_emp_name: Optional[list[XON]] = HL7Field(
        position=11,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    plan_effective_date: Optional[DT] = HL7Field(
        position=12,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    plan_expiration_date: Optional[DT] = HL7Field(
        position=13,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    authorization_information: Optional[AUI] = HL7Field(
        position=14,
        datatype="AUI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    plan_type: Optional[CWE] = HL7Field(
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70086",
    )
    name_of_insured: Optional[list[XPN]] = HL7Field(
        position=16,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    insureds_relationship_to_patient: Optional[CWE] = HL7Field(
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70063",
    )
    insureds_date_of_birth: Optional[DTM] = HL7Field(
        position=18,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    insureds_address: Optional[list[XAD]] = HL7Field(
        position=19,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    assignment_of_benefits: Optional[CWE] = HL7Field(
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70135",
    )
    coordination_of_benefits: Optional[CWE] = HL7Field(
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70173",
    )
    coord_of_ben_priority: Optional[ST] = HL7Field(
        position=22,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    notice_of_admission_flag: Optional[ID] = HL7Field(
        position=23,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    notice_of_admission_date: Optional[DT] = HL7Field(
        position=24,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    report_of_eligibility_flag: Optional[ID] = HL7Field(
        position=25,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    report_of_eligibility_date: Optional[DT] = HL7Field(
        position=26,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    release_information_code: Optional[CWE] = HL7Field(
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70093",
    )
    pre_admit_cert_pac: Optional[ST] = HL7Field(
        position=28,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    verification_date_time: Optional[DTM] = HL7Field(
        position=29,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    verification_by: Optional[list[XCN]] = HL7Field(
        position=30,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    type_of_agreement_code: Optional[CWE] = HL7Field(
        position=31,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70098",
    )
    billing_status: Optional[CWE] = HL7Field(
        position=32,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70022",
    )
    lifetime_reserve_days: Optional[NM] = HL7Field(
        position=33,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    delay_before_lr_day: Optional[NM] = HL7Field(
        position=34,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    company_plan_code: Optional[CWE] = HL7Field(
        position=35,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70042",
    )
    policy_number: Optional[ST] = HL7Field(
        position=36,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    policy_deductible: Optional[CP] = HL7Field(
        position=37,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    policy_limit_days: Optional[NM] = HL7Field(
        position=39,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    insureds_employment_status: Optional[CWE] = HL7Field(
        position=42,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70066",
    )
    insureds_administrative_sex: Optional[CWE] = HL7Field(
        position=43,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70001",
    )
    insureds_employers_address: Optional[list[XAD]] = HL7Field(
        position=44,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    verification_status: Optional[ST] = HL7Field(
        position=45,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    prior_insurance_plan_id: Optional[CWE] = HL7Field(
        position=46,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70072",
    )
    coverage_type: Optional[CWE] = HL7Field(
        position=47,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70309",
    )
    handicap: Optional[CWE] = HL7Field(
        position=48,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70295",
    )
    insureds_id_number: Optional[list[CX]] = HL7Field(
        position=49,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    signature_code: Optional[CWE] = HL7Field(
        position=50,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70535",
    )
    signature_code_date: Optional[DT] = HL7Field(
        position=51,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    insureds_birth_place: Optional[ST] = HL7Field(
        position=52,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    vip_indicator: Optional[CWE] = HL7Field(
        position=53,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70099",
    )
    external_health_plan_identifiers: Optional[list[CX]] = HL7Field(
        position=54,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    insurance_action_code: Optional[ID] = HL7Field(
        position=55,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70206",
    )


class IN2(HL7Segment):
    _segment_id = "IN2"

    insureds_employee_id: Optional[list[CX]] = HL7Field(
        position=1,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    insureds_social_security_number: Optional[ST] = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    insureds_employers_name_and_id: Optional[list[XCN]] = HL7Field(
        position=3,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    employer_information_data: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70139",
    )
    mail_claim_party: Optional[list[CWE]] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70137",
    )
    medicare_health_ins_card_number: Optional[ST] = HL7Field(
        position=6,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    medicaid_case_name: Optional[list[XPN]] = HL7Field(
        position=7,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    medicaid_case_number: Optional[ST] = HL7Field(
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    military_sponsor_name: Optional[list[XPN]] = HL7Field(
        position=9,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    military_id_number: Optional[ST] = HL7Field(
        position=10,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    dependent_of_military_recipient: Optional[CWE] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70342",
    )
    military_organization: Optional[ST] = HL7Field(
        position=12,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    military_station: Optional[ST] = HL7Field(
        position=13,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    military_service: Optional[CWE] = HL7Field(
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70140",
    )
    military_rank_grade: Optional[CWE] = HL7Field(
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70141",
    )
    military_status: Optional[CWE] = HL7Field(
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70142",
    )
    military_retire_date: Optional[DT] = HL7Field(
        position=17,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    military_non_avail_cert_on_file: Optional[ID] = HL7Field(
        position=18,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    baby_coverage: Optional[ID] = HL7Field(
        position=19,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    combine_baby_bill: Optional[ID] = HL7Field(
        position=20,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    blood_deductible: Optional[ST] = HL7Field(
        position=21,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    special_coverage_approval_name: Optional[list[XPN]] = HL7Field(
        position=22,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    special_coverage_approval_title: Optional[ST] = HL7Field(
        position=23,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    non_covered_insurance_code: Optional[list[CWE]] = HL7Field(
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70143",
    )
    payor_id: Optional[list[CX]] = HL7Field(
        position=25,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    payor_subscriber_id: Optional[list[CX]] = HL7Field(
        position=26,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    eligibility_source: Optional[CWE] = HL7Field(
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70144",
    )
    room_coverage_type_amount: Optional[list[RMC]] = HL7Field(
        position=28,
        datatype="RMC",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    policy_type_amount: Optional[list[PTA]] = HL7Field(
        position=29,
        datatype="PTA",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    daily_deductible: Optional[DDI] = HL7Field(
        position=30,
        datatype="DDI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    living_dependency: Optional[CWE] = HL7Field(
        position=31,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70223",
    )
    ambulatory_status: Optional[list[CWE]] = HL7Field(
        position=32,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70009",
    )
    citizenship: Optional[list[CWE]] = HL7Field(
        position=33,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70171",
    )
    primary_language: Optional[CWE] = HL7Field(
        position=34,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70296",
    )
    living_arrangement: Optional[CWE] = HL7Field(
        position=35,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70220",
    )
    publicity_code: Optional[CWE] = HL7Field(
        position=36,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70215",
    )
    protection_indicator: Optional[ID] = HL7Field(
        position=37,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    student_indicator: Optional[CWE] = HL7Field(
        position=38,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70231",
    )
    religion: Optional[CWE] = HL7Field(
        position=39,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70006",
    )
    mothers_maiden_name: Optional[list[XPN]] = HL7Field(
        position=40,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    nationality: Optional[CWE] = HL7Field(
        position=41,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70212",
    )
    ethnic_group: Optional[list[CWE]] = HL7Field(
        position=42,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70189",
    )
    marital_status: Optional[list[CWE]] = HL7Field(
        position=43,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70002",
    )
    insureds_employment_start_date: Optional[DT] = HL7Field(
        position=44,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    employment_stop_date: Optional[DT] = HL7Field(
        position=45,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    job_title: Optional[ST] = HL7Field(
        position=46,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    job_code_class: Optional[JCC] = HL7Field(
        position=47,
        datatype="JCC",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    job_status: Optional[CWE] = HL7Field(
        position=48,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70311",
    )
    employer_contact_person_name: Optional[list[XPN]] = HL7Field(
        position=49,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    employer_contact_person_phone_number: Optional[list[XTN]] = HL7Field(
        position=50,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    employer_contact_reason: Optional[CWE] = HL7Field(
        position=51,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70222",
    )
    insureds_contact_persons_name: Optional[list[XPN]] = HL7Field(
        position=52,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    insureds_contact_person_phone_number: Optional[list[XTN]] = HL7Field(
        position=53,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    insureds_contact_person_reason: Optional[list[CWE]] = HL7Field(
        position=54,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70222",
    )
    relationship_to_the_patient_start_date: Optional[DT] = HL7Field(
        position=55,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    relationship_to_the_patient_stop_date: Optional[list[DT]] = HL7Field(
        position=56,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    insurance_co_contact_reason: Optional[CWE] = HL7Field(
        position=57,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70232",
    )
    insurance_co_contact_phone_number: Optional[list[XTN]] = HL7Field(
        position=58,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    policy_scope: Optional[CWE] = HL7Field(
        position=59,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70312",
    )
    policy_source: Optional[CWE] = HL7Field(
        position=60,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70313",
    )
    patient_member_number: Optional[CX] = HL7Field(
        position=61,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    guarantors_relationship_to_insured: Optional[CWE] = HL7Field(
        position=62,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70063",
    )
    insureds_phone_number_home: Optional[list[XTN]] = HL7Field(
        position=63,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    insureds_employer_phone_number: Optional[list[XTN]] = HL7Field(
        position=64,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    military_handicapped_program: Optional[CWE] = HL7Field(
        position=65,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70343",
    )
    suspend_flag: Optional[ID] = HL7Field(
        position=66,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    copay_limit_flag: Optional[ID] = HL7Field(
        position=67,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    stoploss_limit_flag: Optional[ID] = HL7Field(
        position=68,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    insured_organization_name_and_id: Optional[list[XON]] = HL7Field(
        position=69,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    insured_employer_organization_name_and_id: Optional[list[XON]] = HL7Field(
        position=70,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    race: Optional[list[CWE]] = HL7Field(
        position=71,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70005",
    )
    patients_relationship_to_insured: Optional[CWE] = HL7Field(
        position=72,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70344",
    )
    co_pay_amount: Optional[CP] = HL7Field(
        position=73,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class IN3(HL7Segment):
    _segment_id = "IN3"

    set_id_in3: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    certification_number: Optional[CX] = HL7Field(
        position=2,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    certified_by: Optional[list[XCN]] = HL7Field(
        position=3,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    certification_required: Optional[ID] = HL7Field(
        position=4,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    penalty: Optional[MOP] = HL7Field(
        position=5,
        datatype="MOP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    certification_date_time: Optional[DTM] = HL7Field(
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    certification_modify_date_time: Optional[DTM] = HL7Field(
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    operator: Optional[list[XCN]] = HL7Field(
        position=8,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    certification_begin_date: Optional[DT] = HL7Field(
        position=9,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    certification_end_date: Optional[DT] = HL7Field(
        position=10,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    days: Optional[DTN] = HL7Field(
        position=11,
        datatype="DTN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    non_concur_code_description: Optional[CWE] = HL7Field(
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70233",
    )
    non_concur_effective_date_time: Optional[DTM] = HL7Field(
        position=13,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    physician_reviewer: Optional[list[XCN]] = HL7Field(
        position=14,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70010",
    )
    certification_contact: Optional[ST] = HL7Field(
        position=15,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    certification_contact_phone_number: Optional[list[XTN]] = HL7Field(
        position=16,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    appeal_reason: Optional[CWE] = HL7Field(
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70345",
    )
    certification_agency: Optional[CWE] = HL7Field(
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70346",
    )
    certification_agency_phone_number: Optional[list[XTN]] = HL7Field(
        position=19,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    pre_certification_requirement: Optional[list[ICD]] = HL7Field(
        position=20,
        datatype="ICD",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70136",
    )
    case_manager: Optional[ST] = HL7Field(
        position=21,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    second_opinion_date: Optional[DT] = HL7Field(
        position=22,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    second_opinion_status: Optional[CWE] = HL7Field(
        position=23,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70151",
    )
    second_opinion_documentation_received: Optional[list[CWE]] = HL7Field(
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70152",
    )
    second_opinion_physician: Optional[list[XCN]] = HL7Field(
        position=25,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70010",
    )
    certification_type: Optional[CWE] = HL7Field(
        position=26,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70921",
    )
    certification_category: Optional[CWE] = HL7Field(
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70922",
    )
    online_verification_date_time: Optional[DTM] = HL7Field(
        position=28,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    online_verification_result: Optional[CWE] = HL7Field(
        position=29,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70970",
    )
    online_verification_result_error_code: Optional[CWE] = HL7Field(
        position=30,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70971",
    )
    online_verification_result_check_digit: Optional[ST] = HL7Field(
        position=31,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class INV(HL7Segment):
    _segment_id = "INV"

    substance_identifier: Optional[CWE] = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70451",
    )
    substance_status: Optional[list[CWE]] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70383",
    )
    substance_type: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70384",
    )
    inventory_container_identifier: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70599",
    )
    container_carrier_identifier: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70600",
    )
    position_on_carrier: Optional[CWE] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70601",
    )
    initial_quantity: Optional[NM] = HL7Field(
        position=7,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    current_quantity: Optional[NM] = HL7Field(
        position=8,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    available_quantity: Optional[NM] = HL7Field(
        position=9,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    consumption_quantity: Optional[NM] = HL7Field(
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    quantity_units: Optional[CWE] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70602",
    )
    expiration_date_time: Optional[DTM] = HL7Field(
        position=12,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    first_used_date_time: Optional[DTM] = HL7Field(
        position=13,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    test_fluid_identifiers: Optional[list[CWE]] = HL7Field(
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70603",
    )
    manufacturer_lot_number: Optional[ST] = HL7Field(
        position=16,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    manufacturer_identifier: Optional[CWE] = HL7Field(
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70385",
    )
    supplier_identifier: Optional[CWE] = HL7Field(
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70386",
    )
    on_board_stability_time: Optional[CQ] = HL7Field(
        position=19,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    target_value: Optional[CQ] = HL7Field(
        position=20,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    equipment_state_indicator_type_code: Optional[CWE] = HL7Field(
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70942",
    )
    equipment_state_indicator_value: Optional[CQ] = HL7Field(
        position=22,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class IPC(HL7Segment):
    _segment_id = "IPC"

    accession_identifier: EI = HL7Field(
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    requested_procedure_id: EI = HL7Field(
        position=2,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    study_instance_uid: EI = HL7Field(
        position=3,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    scheduled_procedure_step_id: EI = HL7Field(
        position=4,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    modality: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70604",
    )
    protocol_code: Optional[list[CWE]] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70605",
    )
    scheduled_station_name: Optional[EI] = HL7Field(
        position=7,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    scheduled_procedure_step_location: Optional[list[CWE]] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70606",
    )
    scheduled_station_ae_title: Optional[ST] = HL7Field(
        position=9,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    action_code: Optional[ID] = HL7Field(
        position=10,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class IPR(HL7Segment):
    _segment_id = "IPR"

    ipr_identifier: EI = HL7Field(
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    provider_cross_reference_identifier: EI = HL7Field(
        position=2,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    payer_cross_reference_identifier: EI = HL7Field(
        position=3,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    ipr_status: CWE = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70571",
    )
    ipr_date_time: DTM = HL7Field(
        position=5,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    adjudicated_paid_amount: Optional[CP] = HL7Field(
        position=6,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    expected_payment_date_time: Optional[DTM] = HL7Field(
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    ipr_checksum: ST = HL7Field(
        position=8,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )


class ISD(HL7Segment):
    _segment_id = "ISD"

    reference_interaction_number: NM = HL7Field(
        position=1,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    interaction_type_identifier: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70368",
    )
    interaction_active_state: CWE = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70387",
    )


class ITM(HL7Segment):
    _segment_id = "ITM"

    item_identifier: EI = HL7Field(
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    item_description: Optional[ST] = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    item_status: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70776",
    )
    item_type: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70778",
    )
    item_category: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    subject_to_expiration_indicator: Optional[CNE] = HL7Field(
        position=6,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    manufacturer_identifier: Optional[EI] = HL7Field(
        position=7,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    manufacturer_name: Optional[ST] = HL7Field(
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    manufacturer_catalog_number: Optional[ST] = HL7Field(
        position=9,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    manufacturer_labeler_identification_code: Optional[CWE] = HL7Field(
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    patient_chargeable_indicator: Optional[CNE] = HL7Field(
        position=11,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    transaction_code: Optional[CWE] = HL7Field(
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70132",
    )
    transaction_amount_unit: Optional[CP] = HL7Field(
        position=13,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    stocked_item_indicator: Optional[CNE] = HL7Field(
        position=14,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    supply_risk_codes: Optional[CWE] = HL7Field(
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70871",
    )
    approving_regulatory_agency: Optional[list[XON]] = HL7Field(
        position=16,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70790",
    )
    latex_indicator: Optional[CNE] = HL7Field(
        position=17,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    ruling_act: Optional[list[CWE]] = HL7Field(
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70793",
    )
    item_natural_account_code: Optional[CWE] = HL7Field(
        position=19,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70320",
    )
    approved_to_buy_quantity: Optional[NM] = HL7Field(
        position=20,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    approved_to_buy_price: Optional[MO] = HL7Field(
        position=21,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    taxable_item_indicator: Optional[CNE] = HL7Field(
        position=22,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    freight_charge_indicator: Optional[CNE] = HL7Field(
        position=23,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    item_set_indicator: Optional[CNE] = HL7Field(
        position=24,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    item_set_identifier: Optional[EI] = HL7Field(
        position=25,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    track_department_usage_indicator: Optional[CNE] = HL7Field(
        position=26,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    procedure_code: Optional[CNE] = HL7Field(
        position=27,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70088",
    )
    procedure_code_modifier: Optional[list[CNE]] = HL7Field(
        position=28,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70340",
    )
    special_handling_code: Optional[CWE] = HL7Field(
        position=29,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70376",
    )
    hazardous_indicator: Optional[CNE] = HL7Field(
        position=30,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    sterile_indicator: Optional[CNE] = HL7Field(
        position=31,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    material_data_safety_sheet_number: Optional[EI] = HL7Field(
        position=32,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    united_nations_standard_products_and_services_code_unspsc: Optional[CWE] = HL7Field(
        position=33,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70396",
    )
    contract_date: Optional[DR] = HL7Field(
        position=34,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    manufacturer_contact_name: Optional[XPN] = HL7Field(
        position=35,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    manufacturer_contact_information: Optional[XTN] = HL7Field(
        position=36,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    class_of_trade: Optional[ST] = HL7Field(
        position=37,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    field_level_event_code: Optional[ID] = HL7Field(
        position=38,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70180",
    )


class IVC(HL7Segment):
    _segment_id = "IVC"

    provider_invoice_number: EI = HL7Field(
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    payer_invoice_number: Optional[EI] = HL7Field(
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    contract_agreement_number: Optional[EI] = HL7Field(
        position=3,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    invoice_control: CWE = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70553",
    )
    invoice_reason: CWE = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70554",
    )
    invoice_type: CWE = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70555",
    )
    invoice_date_time: DTM = HL7Field(
        position=7,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    invoice_amount: CP = HL7Field(
        position=8,
        datatype="CP",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    payment_terms: Optional[ST] = HL7Field(
        position=9,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    provider_organization: XON = HL7Field(
        position=10,
        datatype="XON",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    payer_organization: XON = HL7Field(
        position=11,
        datatype="XON",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    attention: Optional[XCN] = HL7Field(
        position=12,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    last_invoice_indicator: Optional[ID] = HL7Field(
        position=13,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    invoice_booking_period: Optional[DTM] = HL7Field(
        position=14,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    origin: Optional[ST] = HL7Field(
        position=15,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    invoice_fixed_amount: Optional[CP] = HL7Field(
        position=16,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    special_costs: Optional[CP] = HL7Field(
        position=17,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    amount_for_doctors_treatment: Optional[CP] = HL7Field(
        position=18,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    responsible_physician: Optional[XCN] = HL7Field(
        position=19,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    cost_center: Optional[CX] = HL7Field(
        position=20,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    invoice_prepaid_amount: Optional[CP] = HL7Field(
        position=21,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    total_invoice_amount_without_prepaid_amount: Optional[CP] = HL7Field(
        position=22,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    total_amount_of_vat: Optional[CP] = HL7Field(
        position=23,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    vat_rates_applied: Optional[list[NM]] = HL7Field(
        position=24,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    benefit_group: CWE = HL7Field(
        position=25,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70556",
    )
    provider_tax_id: Optional[ST] = HL7Field(
        position=26,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    payer_tax_id: Optional[ST] = HL7Field(
        position=27,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    provider_tax_status: Optional[CWE] = HL7Field(
        position=28,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70572",
    )
    payer_tax_status: Optional[CWE] = HL7Field(
        position=29,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70572",
    )
    sales_tax_id: Optional[ST] = HL7Field(
        position=30,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class IVT(HL7Segment):
    _segment_id = "IVT"

    set_id_ivt: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    inventory_location_identifier: EI = HL7Field(
        position=2,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    inventory_location_name: Optional[ST] = HL7Field(
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    source_location_identifier: Optional[EI] = HL7Field(
        position=4,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    source_location_name: Optional[ST] = HL7Field(
        position=5,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    item_status: Optional[CWE] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70625",
    )
    bin_location_identifier: Optional[list[EI]] = HL7Field(
        position=7,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    order_packaging: Optional[CWE] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70818",
    )
    issue_packaging: Optional[CWE] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    default_inventory_asset_account: Optional[EI] = HL7Field(
        position=10,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    patient_chargeable_indicator: Optional[CNE] = HL7Field(
        position=11,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    transaction_code: Optional[CWE] = HL7Field(
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70132",
    )
    transaction_amount_unit: Optional[CP] = HL7Field(
        position=13,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    item_importance_code: Optional[CWE] = HL7Field(
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70634",
    )
    stocked_item_indicator: Optional[CNE] = HL7Field(
        position=15,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    consignment_item_indicator: Optional[CNE] = HL7Field(
        position=16,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    reusable_item_indicator: Optional[CNE] = HL7Field(
        position=17,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    reusable_cost: Optional[CP] = HL7Field(
        position=18,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    substitute_item_identifier: Optional[list[EI]] = HL7Field(
        position=19,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    latex_free_substitute_item_identifier: Optional[EI] = HL7Field(
        position=20,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    recommended_reorder_theory: Optional[CWE] = HL7Field(
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70642",
    )
    recommended_safety_stock_days: Optional[NM] = HL7Field(
        position=22,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    recommended_maximum_days_inventory: Optional[NM] = HL7Field(
        position=23,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    recommended_order_point: Optional[NM] = HL7Field(
        position=24,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    recommended_order_amount: Optional[NM] = HL7Field(
        position=25,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    operating_room_par_level_indicator: Optional[CNE] = HL7Field(
        position=26,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )


class LAN(HL7Segment):
    _segment_id = "LAN"

    set_id_lan: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    language_code: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70296",
    )
    language_ability_code: Optional[list[CWE]] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70403",
    )
    language_proficiency_code: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70404",
    )


class LCC(HL7Segment):
    _segment_id = "LCC"

    primary_key_value_lcc: PL = HL7Field(
        position=1,
        datatype="PL",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    location_department: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70264",
    )
    accommodation_type: Optional[list[CWE]] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70129",
    )
    charge_code: list[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=True,
        table="HL70132",
    )


class LCH(HL7Segment):
    _segment_id = "LCH"

    primary_key_value_lch: PL = HL7Field(
        position=1,
        datatype="PL",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    segment_action_code: Optional[ID] = HL7Field(
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70206",
    )
    segment_unique_key: Optional[EI] = HL7Field(
        position=3,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    location_characteristic_id: CWE = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70324",
    )
    location_characteristic_value_lch: CWE = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70136",
    )


class LDP(HL7Segment):
    _segment_id = "LDP"

    primary_key_value_ldp: PL = HL7Field(
        position=1,
        datatype="PL",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    location_department: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70264",
    )
    location_service: Optional[list[CWE]] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70069",
    )
    specialty_type: Optional[list[CWE]] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70265",
    )
    valid_patient_classes: Optional[list[CWE]] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70004",
    )
    active_inactive_flag: Optional[ID] = HL7Field(
        position=6,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70183",
    )
    activation_date_ldp: Optional[DTM] = HL7Field(
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inactivation_date_ldp: Optional[DTM] = HL7Field(
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inactivated_reason: Optional[ST] = HL7Field(
        position=9,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    visiting_hours: Optional[list[VH]] = HL7Field(
        position=10,
        datatype="VH",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70267",
    )
    contact_phone: Optional[XTN] = HL7Field(
        position=11,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    location_cost_center: Optional[CWE] = HL7Field(
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70462",
    )


class LOC(HL7Segment):
    _segment_id = "LOC"

    primary_key_value_loc: PL = HL7Field(
        position=1,
        datatype="PL",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    location_description: Optional[ST] = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    location_type_loc: list[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=True,
        table="HL70260",
    )
    organization_name_loc: Optional[list[XON]] = HL7Field(
        position=4,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    location_address: Optional[list[XAD]] = HL7Field(
        position=5,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    location_phone: Optional[list[XTN]] = HL7Field(
        position=6,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    license_number: Optional[list[CWE]] = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70461",
    )
    location_equipment: Optional[list[CWE]] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70261",
    )
    location_service_code: Optional[CWE] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70442",
    )


class LRL(HL7Segment):
    _segment_id = "LRL"

    primary_key_value_lrl: PL = HL7Field(
        position=1,
        datatype="PL",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    segment_action_code: Optional[ID] = HL7Field(
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70206",
    )
    segment_unique_key: Optional[EI] = HL7Field(
        position=3,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    location_relationship_id: CWE = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70325",
    )
    organizational_location_relationship_value: Optional[list[XON]] = HL7Field(
        position=5,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    patient_location_relationship_value: Optional[PL] = HL7Field(
        position=6,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class MCP(HL7Segment):
    _segment_id = "MCP"

    set_id_mcp: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    producers_service_test_observation_id: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    universal_service_price_range_low_value: Optional[MO] = HL7Field(
        position=3,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    universal_service_price_range_high_value: Optional[MO] = HL7Field(
        position=4,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    reason_for_universal_service_cost_range: Optional[ST] = HL7Field(
        position=5,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class MFA(HL7Segment):
    _segment_id = "MFA"

    record_level_event_code: ID = HL7Field(
        position=1,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70180",
    )
    mfn_control_id: Optional[ST] = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    event_completion_date_time: Optional[DTM] = HL7Field(
        position=3,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    mfn_record_level_error_return: CWE = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70181",
    )
    primary_key_value_mfa: list[Varies] = HL7Field(
        position=5,
        datatype="Varies",
        usage=Usage.REQUIRED,
        repeatable=True,
        table="HL70607",
    )
    primary_key_value_type_mfa: list[ID] = HL7Field(
        position=6,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=True,
        table="HL70355",
    )


class MFE(HL7Segment):
    _segment_id = "MFE"

    record_level_event_code: ID = HL7Field(
        position=1,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70180",
    )
    mfn_control_id: Optional[ST] = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    effective_date_time: Optional[DTM] = HL7Field(
        position=3,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    primary_key_value_mfe: list[Varies] = HL7Field(
        position=4,
        datatype="Varies",
        usage=Usage.REQUIRED,
        repeatable=True,
        table="HL70608",
    )
    primary_key_value_type: list[ID] = HL7Field(
        position=5,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=True,
        table="HL70355",
    )
    entered_date_time: Optional[DTM] = HL7Field(
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    entered_by: Optional[XCN] = HL7Field(
        position=7,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class MFI(HL7Segment):
    _segment_id = "MFI"

    master_file_identifier: CWE = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70175",
    )
    master_file_application_identifier: Optional[list[HD]] = HL7Field(
        position=2,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70361",
    )
    file_level_event_code: ID = HL7Field(
        position=3,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70178",
    )
    entered_date_time: Optional[DTM] = HL7Field(
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    effective_date_time: Optional[DTM] = HL7Field(
        position=5,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    response_level_code: ID = HL7Field(
        position=6,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70179",
    )


class MRG(HL7Segment):
    _segment_id = "MRG"

    prior_patient_identifier_list: list[CX] = HL7Field(
        position=1,
        datatype="CX",
        usage=Usage.REQUIRED,
        repeatable=True,
        table="HL70061",
    )
    prior_patient_account_number: Optional[CX] = HL7Field(
        position=3,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70061",
    )
    prior_visit_number: Optional[CX] = HL7Field(
        position=5,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70061",
    )
    prior_alternate_visit_id: Optional[list[CX]] = HL7Field(
        position=6,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70061",
    )
    prior_patient_name: Optional[list[XPN]] = HL7Field(
        position=7,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70200",
    )


class MSA(HL7Segment):
    _segment_id = "MSA"

    acknowledgment_code: ID = HL7Field(
        position=1,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70008",
    )
    message_control_id: ST = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    expected_sequence_number: Optional[NM] = HL7Field(
        position=4,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    message_waiting_number: Optional[NM] = HL7Field(
        position=7,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    message_waiting_priority: Optional[ID] = HL7Field(
        position=8,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70520",
    )


class MSH(HL7Segment):
    _segment_id = "MSH"

    field_separator: ST = HL7Field(
        position=1,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    encoding_characters: ST = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    sending_application: Optional[HD] = HL7Field(
        position=3,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70361",
    )
    sending_facility: Optional[HD] = HL7Field(
        position=4,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70362",
    )
    receiving_application: Optional[HD] = HL7Field(
        position=5,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70361",
    )
    receiving_facility: Optional[list[HD]] = HL7Field(
        position=6,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70362",
    )
    date_time_of_message: DTM = HL7Field(
        position=7,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    security: Optional[ST] = HL7Field(
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    message_type: MSG = HL7Field(
        position=9,
        datatype="MSG",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    message_control_id: ST = HL7Field(
        position=10,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    processing_id: PT = HL7Field(
        position=11,
        datatype="PT",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    version_id: VID = HL7Field(
        position=12,
        datatype="VID",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    sequence_number: Optional[NM] = HL7Field(
        position=13,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    continuation_pointer: Optional[ST] = HL7Field(
        position=14,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    accept_acknowledgment: Optional[ID] = HL7Field(
        position=15,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70155",
    )
    application_acknowledgment_type: Optional[ID] = HL7Field(
        position=16,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70155",
    )
    country_code: Optional[ID] = HL7Field(
        position=17,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70399",
    )
    character_set: Optional[list[ID]] = HL7Field(
        position=18,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70211",
    )
    principal_language_of_message: Optional[CWE] = HL7Field(
        position=19,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70609",
    )
    alternate_character_set_handling_scheme: Optional[ID] = HL7Field(
        position=20,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70356",
    )
    message_profile_identifier: Optional[list[EI]] = HL7Field(
        position=21,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    sending_responsible_organization: Optional[XON] = HL7Field(
        position=22,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    receiving_responsible_organization: Optional[XON] = HL7Field(
        position=23,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    sending_network_address: Optional[HD] = HL7Field(
        position=24,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    receiving_network_address: Optional[HD] = HL7Field(
        position=25,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    security_classification_tag: Optional[CWE] = HL7Field(
        position=26,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70952",
    )
    security_handling_instructions: Optional[list[CWE]] = HL7Field(
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70953",
    )
    special_access_restriction_instructions: Optional[list[ST]] = HL7Field(
        position=28,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )


class NCK(HL7Segment):
    _segment_id = "NCK"

    system_date_time: DTM = HL7Field(
        position=1,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )


class NDS(HL7Segment):
    _segment_id = "NDS"

    notification_reference_number: NM = HL7Field(
        position=1,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    notification_date_time: DTM = HL7Field(
        position=2,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    notification_alert_severity: CWE = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70367",
    )
    notification_code: CWE = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70610",
    )


class NK1(HL7Segment):
    _segment_id = "NK1"

    set_id_nk1: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    name: Optional[list[XPN]] = HL7Field(
        position=2,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70200",
    )
    relationship: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70063",
    )
    address: Optional[list[XAD]] = HL7Field(
        position=4,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    contact_role: Optional[CWE] = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70131",
    )
    start_date: Optional[DT] = HL7Field(
        position=8,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    end_date: Optional[DT] = HL7Field(
        position=9,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    next_of_kin_associated_parties_job_title: Optional[ST] = HL7Field(
        position=10,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    next_of_kin_associated_parties_job_code_class: Optional[JCC] = HL7Field(
        position=11,
        datatype="JCC",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    next_of_kin_associated_parties_employee_number: Optional[CX] = HL7Field(
        position=12,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    organization_name_nk1: Optional[list[XON]] = HL7Field(
        position=13,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    marital_status: Optional[CWE] = HL7Field(
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70002",
    )
    administrative_sex: Optional[CWE] = HL7Field(
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70001",
    )
    date_time_of_birth: Optional[DTM] = HL7Field(
        position=16,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    living_dependency: Optional[list[CWE]] = HL7Field(
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70223",
    )
    ambulatory_status: Optional[list[CWE]] = HL7Field(
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70009",
    )
    citizenship: Optional[list[CWE]] = HL7Field(
        position=19,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70171",
    )
    primary_language: Optional[CWE] = HL7Field(
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70296",
    )
    living_arrangement: Optional[CWE] = HL7Field(
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70220",
    )
    publicity_code: Optional[CWE] = HL7Field(
        position=22,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70215",
    )
    protection_indicator: Optional[ID] = HL7Field(
        position=23,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    student_indicator: Optional[CWE] = HL7Field(
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70231",
    )
    religion: Optional[CWE] = HL7Field(
        position=25,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70006",
    )
    mothers_maiden_name: Optional[list[XPN]] = HL7Field(
        position=26,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    nationality: Optional[CWE] = HL7Field(
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70212",
    )
    ethnic_group: Optional[list[CWE]] = HL7Field(
        position=28,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70189",
    )
    contact_reason: Optional[list[CWE]] = HL7Field(
        position=29,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70222",
    )
    contact_persons_name: Optional[list[XPN]] = HL7Field(
        position=30,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    contact_persons_address: Optional[list[XAD]] = HL7Field(
        position=32,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    next_of_kin_associated_partys_identifiers: Optional[list[CX]] = HL7Field(
        position=33,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    job_status: Optional[CWE] = HL7Field(
        position=34,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70311",
    )
    race: Optional[list[CWE]] = HL7Field(
        position=35,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70005",
    )
    handicap: Optional[CWE] = HL7Field(
        position=36,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70295",
    )
    contact_person_social_security_number: Optional[ST] = HL7Field(
        position=37,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    next_of_kin_birth_place: Optional[ST] = HL7Field(
        position=38,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    vip_indicator: Optional[CWE] = HL7Field(
        position=39,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70099",
    )
    next_of_kin_telecommunication_information: Optional[XTN] = HL7Field(
        position=40,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    contact_persons_telecommunication_information: Optional[XTN] = HL7Field(
        position=41,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class NPU(HL7Segment):
    _segment_id = "NPU"

    bed_location: PL = HL7Field(
        position=1,
        datatype="PL",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    bed_status: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70116",
    )


class NSC(HL7Segment):
    _segment_id = "NSC"

    application_change_type: CWE = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70409",
    )
    current_cpu: Optional[ST] = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    current_fileserver: Optional[ST] = HL7Field(
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    current_application: Optional[HD] = HL7Field(
        position=4,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70361",
    )
    current_facility: Optional[HD] = HL7Field(
        position=5,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70362",
    )
    new_cpu: Optional[ST] = HL7Field(
        position=6,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    new_fileserver: Optional[ST] = HL7Field(
        position=7,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    new_application: Optional[HD] = HL7Field(
        position=8,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70361",
    )
    new_facility: Optional[HD] = HL7Field(
        position=9,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70362",
    )


class NST(HL7Segment):
    _segment_id = "NST"

    statistics_available: ID = HL7Field(
        position=1,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70136",
    )
    source_identifier: Optional[ST] = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    source_type: Optional[ID] = HL7Field(
        position=3,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70332",
    )
    statistics_start: Optional[DTM] = HL7Field(
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    statistics_end: Optional[DTM] = HL7Field(
        position=5,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    receive_character_count: Optional[NM] = HL7Field(
        position=6,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    send_character_count: Optional[NM] = HL7Field(
        position=7,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    messages_received: Optional[NM] = HL7Field(
        position=8,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    messages_sent: Optional[NM] = HL7Field(
        position=9,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    checksum_errors_received: Optional[NM] = HL7Field(
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    length_errors_received: Optional[NM] = HL7Field(
        position=11,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    other_errors_received: Optional[NM] = HL7Field(
        position=12,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    connect_timeouts: Optional[NM] = HL7Field(
        position=13,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    receive_timeouts: Optional[NM] = HL7Field(
        position=14,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    application_control_level_errors: Optional[NM] = HL7Field(
        position=15,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class NTE(HL7Segment):
    _segment_id = "NTE"

    set_id_nte: Optional[SI] = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    source_of_comment: Optional[ID] = HL7Field(
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70105",
    )
    comment: Optional[list[FT]] = HL7Field(
        position=3,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    comment_type: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70364",
    )
    entered_by: Optional[XCN] = HL7Field(
        position=5,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    entered_date_time: Optional[DTM] = HL7Field(
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    effective_start_date: Optional[DTM] = HL7Field(
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    expiration_date: Optional[DTM] = HL7Field(
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    coded_comment: Optional[list[CWE]] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70611",
    )


class OBR(HL7Segment):
    _segment_id = "OBR"

    set_id_obr: Optional[SI] = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    placer_order_number: Optional[EI] = HL7Field(
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    filler_order_number: Optional[EI] = HL7Field(
        position=3,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    universal_service_identifier: CWE = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    observation_date_time: Optional[DTM] = HL7Field(
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    observation_end_date_time: Optional[DTM] = HL7Field(
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    collection_volume: Optional[CQ] = HL7Field(
        position=9,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    collector_identifier: Optional[list[XCN]] = HL7Field(
        position=10,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    specimen_action_code: Optional[ID] = HL7Field(
        position=11,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70065",
    )
    danger_code: Optional[CWE] = HL7Field(
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70613",
    )
    relevant_clinical_information: Optional[list[CWE]] = HL7Field(
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70916",
    )
    order_callback_phone_number: Optional[XTN] = HL7Field(
        position=17,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    placer_field_1: Optional[ST] = HL7Field(
        position=18,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    placer_field_2: Optional[ST] = HL7Field(
        position=19,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    filler_field_1: Optional[ST] = HL7Field(
        position=20,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    filler_field_2: Optional[ST] = HL7Field(
        position=21,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    results_rpt_status_chng_date_time: Optional[DTM] = HL7Field(
        position=22,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    charge_to_practice: Optional[MOC] = HL7Field(
        position=23,
        datatype="MOC",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    diagnostic_serv_sect_id: Optional[ID] = HL7Field(
        position=24,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70074",
    )
    result_status: Optional[ID] = HL7Field(
        position=25,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70123",
    )
    parent_result: Optional[PRL] = HL7Field(
        position=26,
        datatype="PRL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    parent_results_observation_identifier: Optional[EIP] = HL7Field(
        position=29,
        datatype="EIP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    transportation_mode: Optional[ID] = HL7Field(
        position=30,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70124",
    )
    reason_for_study: Optional[list[CWE]] = HL7Field(
        position=31,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70951",
    )
    scheduled_date_time: Optional[DTM] = HL7Field(
        position=36,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    number_of_sample_containers: Optional[NM] = HL7Field(
        position=37,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    transport_logistics_of_collected_sample: Optional[list[CWE]] = HL7Field(
        position=38,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70614",
    )
    collectors_comment: Optional[list[CWE]] = HL7Field(
        position=39,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70619",
    )
    transport_arrangement_responsibility: Optional[CWE] = HL7Field(
        position=40,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70620",
    )
    transport_arranged: Optional[ID] = HL7Field(
        position=41,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70224",
    )
    escort_required: Optional[ID] = HL7Field(
        position=42,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70225",
    )
    planned_patient_transport_comment: Optional[list[CWE]] = HL7Field(
        position=43,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70621",
    )
    procedure_code: Optional[CNE] = HL7Field(
        position=44,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70088",
    )
    procedure_code_modifier: Optional[list[CNE]] = HL7Field(
        position=45,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70340",
    )
    placer_supplemental_service_information: Optional[list[CWE]] = HL7Field(
        position=46,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70411",
    )
    filler_supplemental_service_information: Optional[list[CWE]] = HL7Field(
        position=47,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70411",
    )
    medically_necessary_duplicate_procedure_reason: Optional[CWE] = HL7Field(
        position=48,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70476",
    )
    result_handling: Optional[CWE] = HL7Field(
        position=49,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70507",
    )
    observation_group_id: Optional[EI] = HL7Field(
        position=51,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    parent_observation_group_id: Optional[EI] = HL7Field(
        position=52,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    alternate_placer_order_number: Optional[list[CX]] = HL7Field(
        position=53,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    parent_order: Optional[list[EIP]] = HL7Field(
        position=54,
        datatype="EIP",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    action_code: Optional[ID] = HL7Field(
        position=55,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class OBX(HL7Segment):
    _segment_id = "OBX"

    set_id_obx: Optional[SI] = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    value_type: Optional[ID] = HL7Field(
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70125",
    )
    observation_identifier: CWE = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70622",
    )
    observation_sub_id: Optional[OG] = HL7Field(
        position=4,
        datatype="OG",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    observation_value: Optional[list[varies]] = HL7Field(
        position=5,
        datatype="varies",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    units: Optional[CWE] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70623",
    )
    reference_range: Optional[ST] = HL7Field(
        position=7,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    interpretation_codes: Optional[list[CWE]] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70078",
    )
    probability: Optional[NM] = HL7Field(
        position=9,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    nature_of_abnormal_test: Optional[list[ID]] = HL7Field(
        position=10,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70080",
    )
    observation_result_status: ID = HL7Field(
        position=11,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70085",
    )
    effective_date_of_reference_range: Optional[DTM] = HL7Field(
        position=12,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    user_defined_access_checks: Optional[ST] = HL7Field(
        position=13,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    date_time_of_the_observation: Optional[DTM] = HL7Field(
        position=14,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    producers_id: Optional[CWE] = HL7Field(
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70624",
    )
    responsible_observer: Optional[list[XCN]] = HL7Field(
        position=16,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    observation_method: Optional[list[CWE]] = HL7Field(
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70626",
    )
    equipment_instance_identifier: Optional[list[EI]] = HL7Field(
        position=18,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    date_time_of_the_analysis: Optional[DTM] = HL7Field(
        position=19,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    observation_site: Optional[list[CWE]] = HL7Field(
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70163",
    )
    observation_instance_identifier: Optional[EI] = HL7Field(
        position=21,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    mood_code: Optional[CNE] = HL7Field(
        position=22,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70725",
    )
    performing_organization_name: Optional[XON] = HL7Field(
        position=23,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    performing_organization_address: Optional[XAD] = HL7Field(
        position=24,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    performing_organization_medical_director: Optional[XCN] = HL7Field(
        position=25,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    patient_results_release_category: Optional[ID] = HL7Field(
        position=26,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70909",
    )
    root_cause: Optional[CWE] = HL7Field(
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70914",
    )
    local_process_control: Optional[list[CWE]] = HL7Field(
        position=28,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70915",
    )
    observation_type: Optional[ID] = HL7Field(
        position=29,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70936",
    )
    observation_sub_type: Optional[ID] = HL7Field(
        position=30,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70937",
    )
    action_code: Optional[ID] = HL7Field(
        position=31,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    observation_value_absent_reason: Optional[list[CWE]] = HL7Field(
        position=32,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70960",
    )
    observation_related_specimen_identifier: Optional[list[EIP]] = HL7Field(
        position=33,
        datatype="EIP",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )


class ODS(HL7Segment):
    _segment_id = "ODS"

    type_: ID = HL7Field(
        position=1,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70159",
    )
    service_period: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70627",
    )
    diet_supplement_or_preference_code: CWE = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70628",
    )
    text_instruction: Optional[ST] = HL7Field(
        position=4,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class ODT(HL7Segment):
    _segment_id = "ODT"

    tray_type: CWE = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70160",
    )
    service_period: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70627",
    )
    text_instruction: Optional[ST] = HL7Field(
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class OH1(HL7Segment):
    _segment_id = "OH1"

    set_id: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    action_code: Optional[ID] = HL7Field(
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    employment_status: CWE = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70957",
    )
    employment_status_start_date: Optional[DT] = HL7Field(
        position=4,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    employment_status_end_date: Optional[DT] = HL7Field(
        position=5,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    entered_date: DT = HL7Field(
        position=6,
        datatype="DT",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    employment_status_unique_identifier: Optional[EI] = HL7Field(
        position=7,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class OH2(HL7Segment):
    _segment_id = "OH2"

    set_id: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    action_code: Optional[ID] = HL7Field(
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    entered_date: Optional[DT] = HL7Field(
        position=3,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    occupation: CWE = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70958",
    )
    industry: CWE = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70955",
    )
    work_classification: Optional[CWE] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70959",
    )
    job_start_date: Optional[DT] = HL7Field(
        position=7,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    job_end_date: Optional[DT] = HL7Field(
        position=8,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    work_schedule: Optional[CWE] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70954",
    )
    average_hours_worked_per_day: Optional[NM] = HL7Field(
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    average_days_worked_per_week: Optional[NM] = HL7Field(
        position=11,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    employer_organization: Optional[XON] = HL7Field(
        position=12,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    employer_address: Optional[list[XAD]] = HL7Field(
        position=13,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    supervisory_level: Optional[CWE] = HL7Field(
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70956",
    )
    job_duties: Optional[list[ST]] = HL7Field(
        position=15,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    occupational_hazards: Optional[list[FT]] = HL7Field(
        position=16,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    job_unique_identifier: Optional[EI] = HL7Field(
        position=17,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    current_job_indicator: Optional[CWE] = HL7Field(
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )


class OH3(HL7Segment):
    _segment_id = "OH3"

    set_id: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    action_code: Optional[ID] = HL7Field(
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    occupation: CWE = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70958",
    )
    industry: CWE = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70955",
    )
    usual_occupation_duration_years: Optional[NM] = HL7Field(
        position=5,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    start_year: Optional[DT] = HL7Field(
        position=6,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    entered_date: Optional[DT] = HL7Field(
        position=7,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    work_unique_identifier: Optional[EI] = HL7Field(
        position=8,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class OH4(HL7Segment):
    _segment_id = "OH4"

    set_id: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    action_code: Optional[ID] = HL7Field(
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    combat_zone_start_date: DT = HL7Field(
        position=3,
        datatype="DT",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    combat_zone_end_date: Optional[DT] = HL7Field(
        position=4,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    entered_date: Optional[DT] = HL7Field(
        position=5,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    combat_zone_unique_identifier: Optional[EI] = HL7Field(
        position=6,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class OM1(HL7Segment):
    _segment_id = "OM1"

    sequence_number_test_observation_master_file: NM = HL7Field(
        position=1,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    producers_service_test_observation_id: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    permitted_data_types: Optional[list[ID]] = HL7Field(
        position=3,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70125",
    )
    specimen_required: ID = HL7Field(
        position=4,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70136",
    )
    producer_id: CWE = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70631",
    )
    observation_description: Optional[TX] = HL7Field(
        position=6,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    other_service_test_observation_i_ds_for_the_observation: Optional[list[CWE]] = (
        HL7Field(
            position=7,
            datatype="CWE",
            usage=Usage.OPTIONAL,
            repeatable=True,
            table="HL70632",
        )
    )
    other_names: Optional[list[ST]] = HL7Field(
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    preferred_report_name_for_the_observation: Optional[ST] = HL7Field(
        position=9,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    preferred_short_name_or_mnemonic_for_the_observation: Optional[ST] = HL7Field(
        position=10,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    preferred_long_name_for_the_observation: Optional[ST] = HL7Field(
        position=11,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    orderability: Optional[ID] = HL7Field(
        position=12,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    identity_of_instrument_used_to_perform_this_study: Optional[list[CWE]] = HL7Field(
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70633",
    )
    coded_representation_of_method: Optional[list[CWE]] = HL7Field(
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70635",
    )
    portable_device_indicator: Optional[ID] = HL7Field(
        position=15,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    observation_producing_department_section: Optional[list[CWE]] = HL7Field(
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70636",
    )
    telephone_number_of_section: Optional[XTN] = HL7Field(
        position=17,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    nature_of_service_test_observation: CWE = HL7Field(
        position=18,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70174",
    )
    report_subheader: Optional[CWE] = HL7Field(
        position=19,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70637",
    )
    report_display_order: Optional[ST] = HL7Field(
        position=20,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    date_time_stamp_for_any_change_in_definition_for_the_observation: Optional[DTM] = (
        HL7Field(
            position=21,
            datatype="DTM",
            usage=Usage.OPTIONAL,
            repeatable=False,
        )
    )
    effective_date_time_of_change: Optional[DTM] = HL7Field(
        position=22,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    typical_turn_around_time: Optional[NM] = HL7Field(
        position=23,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    processing_time: Optional[NM] = HL7Field(
        position=24,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    processing_priority: Optional[list[ID]] = HL7Field(
        position=25,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70168",
    )
    reporting_priority: Optional[ID] = HL7Field(
        position=26,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70169",
    )
    outside_sites_where_observation_may_be_performed: Optional[list[CWE]] = HL7Field(
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70638",
    )
    address_of_outside_sites: Optional[list[XAD]] = HL7Field(
        position=28,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    phone_number_of_outside_site: Optional[XTN] = HL7Field(
        position=29,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    confidentiality_code: Optional[CWE] = HL7Field(
        position=30,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70177",
    )
    observations_required_to_interpret_this_observation: Optional[list[CWE]] = HL7Field(
        position=31,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70639",
    )
    interpretation_of_observations: Optional[TX] = HL7Field(
        position=32,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    contraindications_to_observations: Optional[list[CWE]] = HL7Field(
        position=33,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70640",
    )
    reflex_tests_observations: Optional[list[CWE]] = HL7Field(
        position=34,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70641",
    )
    rules_that_trigger_reflex_testing: Optional[list[TX]] = HL7Field(
        position=35,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    fixed_canned_message: Optional[list[CWE]] = HL7Field(
        position=36,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70643",
    )
    patient_preparation: Optional[list[TX]] = HL7Field(
        position=37,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    procedure_medication: Optional[CWE] = HL7Field(
        position=38,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70644",
    )
    factors_that_may_affect_the_observation: Optional[TX] = HL7Field(
        position=39,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    service_test_observation_performance_schedule: Optional[list[ST]] = HL7Field(
        position=40,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    description_of_test_methods: Optional[TX] = HL7Field(
        position=41,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    kind_of_quantity_observed: Optional[CWE] = HL7Field(
        position=42,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70254",
    )
    point_versus_interval: Optional[CWE] = HL7Field(
        position=43,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70255",
    )
    challenge_information: Optional[TX] = HL7Field(
        position=44,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70256",
    )
    relationship_modifier: Optional[CWE] = HL7Field(
        position=45,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70258",
    )
    target_anatomic_site_of_test: Optional[CWE] = HL7Field(
        position=46,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70645",
    )
    modality_of_imaging_measurement: Optional[CWE] = HL7Field(
        position=47,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70910",
    )
    exclusive_test: Optional[ID] = HL7Field(
        position=48,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70919",
    )
    diagnostic_serv_sect_id: Optional[ID] = HL7Field(
        position=49,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70074",
    )
    taxonomic_classification_code: Optional[CWE] = HL7Field(
        position=50,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    other_names: Optional[list[ST]] = HL7Field(
        position=51,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    replacement_producers_service_test_observation_id: Optional[list[CWE]] = HL7Field(
        position=52,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70646",
    )
    prior_resuts_instructions: Optional[list[TX]] = HL7Field(
        position=53,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    special_instructions: Optional[TX] = HL7Field(
        position=54,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    test_category: Optional[list[CWE]] = HL7Field(
        position=55,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    observation_identifier_associated_with_producers_service_test_observation_id: (
        Optional[CWE]
    ) = HL7Field(
        position=56,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70647",
    )
    typical_turn_around_time: Optional[CQ] = HL7Field(
        position=57,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    gender_restriction: Optional[list[CWE]] = HL7Field(
        position=58,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70001",
    )
    age_restriction: Optional[list[NR]] = HL7Field(
        position=59,
        datatype="NR",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )


class OM2(HL7Segment):
    _segment_id = "OM2"

    sequence_number_test_observation_master_file: Optional[NM] = HL7Field(
        position=1,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    units_of_measure: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70648",
    )
    range_of_decimal_precision: Optional[list[NM]] = HL7Field(
        position=3,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    corresponding_si_units_of_measure: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70649",
    )
    si_conversion_factor: Optional[TX] = HL7Field(
        position=5,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    reference_normal_range_for_ordinal_and_continuous_observations: Optional[
        list[RFR]
    ] = HL7Field(
        position=6,
        datatype="RFR",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    critical_range_for_ordinal_and_continuous_observations: Optional[list[RFR]] = (
        HL7Field(
            position=7,
            datatype="RFR",
            usage=Usage.OPTIONAL,
            repeatable=True,
        )
    )
    absolute_range_for_ordinal_and_continuous_observations: Optional[RFR] = HL7Field(
        position=8,
        datatype="RFR",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    delta_check_criteria: Optional[list[DLT]] = HL7Field(
        position=9,
        datatype="DLT",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    minimum_meaningful_increments: Optional[NM] = HL7Field(
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class OM3(HL7Segment):
    _segment_id = "OM3"

    sequence_number_test_observation_master_file: Optional[NM] = HL7Field(
        position=1,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    preferred_coding_system: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70650",
    )
    valid_coded_answers: Optional[list[CWE]] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70652",
    )
    normal_text_codes_for_categorical_observations: Optional[list[CWE]] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70654",
    )
    abnormal_text_codes_for_categorical_observations: Optional[list[CWE]] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70655",
    )
    critical_text_codes_for_categorical_observations: Optional[list[CWE]] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70656",
    )
    value_type: Optional[ID] = HL7Field(
        position=7,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70125",
    )


class OM4(HL7Segment):
    _segment_id = "OM4"

    sequence_number_test_observation_master_file: Optional[NM] = HL7Field(
        position=1,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    derived_specimen: Optional[ID] = HL7Field(
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70170",
    )
    container_description: Optional[list[TX]] = HL7Field(
        position=3,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    container_volume: Optional[list[NM]] = HL7Field(
        position=4,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    container_units: Optional[list[CWE]] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70658",
    )
    specimen: Optional[CWE] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70660",
    )
    additive: Optional[CWE] = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70371",
    )
    preparation: Optional[TX] = HL7Field(
        position=8,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    special_handling_requirements: Optional[TX] = HL7Field(
        position=9,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    normal_collection_volume: Optional[CQ] = HL7Field(
        position=10,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    minimum_collection_volume: Optional[CQ] = HL7Field(
        position=11,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    specimen_requirements: Optional[TX] = HL7Field(
        position=12,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    specimen_priorities: Optional[list[ID]] = HL7Field(
        position=13,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70027",
    )
    specimen_retention_time: Optional[CQ] = HL7Field(
        position=14,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    specimen_handling_code: Optional[list[CWE]] = HL7Field(
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70376",
    )
    specimen_preference: Optional[ID] = HL7Field(
        position=16,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70920",
    )
    preferred_specimen_attribture_sequence_id: Optional[NM] = HL7Field(
        position=17,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    taxonomic_classification_code: Optional[list[CWE]] = HL7Field(
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )


class OM5(HL7Segment):
    _segment_id = "OM5"

    sequence_number_test_observation_master_file: Optional[NM] = HL7Field(
        position=1,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    test_observations_included_within_an_ordered_test_battery: Optional[list[CWE]] = (
        HL7Field(
            position=2,
            datatype="CWE",
            usage=Usage.OPTIONAL,
            repeatable=True,
            table="HL70662",
        )
    )
    observation_id_suffixes: Optional[ST] = HL7Field(
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class OM6(HL7Segment):
    _segment_id = "OM6"

    sequence_number_test_observation_master_file: Optional[NM] = HL7Field(
        position=1,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    derivation_rule: Optional[TX] = HL7Field(
        position=2,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class OM7(HL7Segment):
    _segment_id = "OM7"

    sequence_number_test_observation_master_file: NM = HL7Field(
        position=1,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    universal_service_identifier: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    category_identifier: Optional[list[CWE]] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70412",
    )
    category_description: Optional[TX] = HL7Field(
        position=4,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    category_synonym: Optional[list[ST]] = HL7Field(
        position=5,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    effective_test_service_start_date_time: Optional[DTM] = HL7Field(
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    effective_test_service_end_date_time: Optional[DTM] = HL7Field(
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    test_service_default_duration_quantity: Optional[NM] = HL7Field(
        position=8,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    test_service_default_duration_units: Optional[CWE] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70663",
    )
    test_service_default_frequency: Optional[CWE] = HL7Field(
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    consent_indicator: Optional[ID] = HL7Field(
        position=11,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    consent_identifier: Optional[CWE] = HL7Field(
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70413",
    )
    consent_effective_start_date_time: Optional[DTM] = HL7Field(
        position=13,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    consent_effective_end_date_time: Optional[DTM] = HL7Field(
        position=14,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    consent_interval_quantity: Optional[NM] = HL7Field(
        position=15,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    consent_interval_units: Optional[CWE] = HL7Field(
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70414",
    )
    consent_waiting_period_quantity: Optional[NM] = HL7Field(
        position=17,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    consent_waiting_period_units: Optional[CWE] = HL7Field(
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70414",
    )
    effective_date_time_of_change: Optional[DTM] = HL7Field(
        position=19,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    entered_by: Optional[XCN] = HL7Field(
        position=20,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    orderable_at_location: Optional[list[PL]] = HL7Field(
        position=21,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    formulary_status: Optional[CWE] = HL7Field(
        position=22,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70473",
    )
    special_order_indicator: Optional[ID] = HL7Field(
        position=23,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    primary_key_value_cdm: Optional[list[CWE]] = HL7Field(
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )


class OMC(HL7Segment):
    _segment_id = "OMC"

    sequence_number_test_observation_master_file: Optional[NM] = HL7Field(
        position=1,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    segment_action_code: Optional[ID] = HL7Field(
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70206",
    )
    segment_unique_key: Optional[EI] = HL7Field(
        position=3,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    clinical_information_request: CWE = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70664",
    )
    collection_event_process_step: list[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=True,
        table="HL70938",
    )
    communication_location: CWE = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70939",
    )
    answer_required: Optional[ID] = HL7Field(
        position=7,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    hint_help_text: Optional[ST] = HL7Field(
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    type_of_answer: Optional[ID] = HL7Field(
        position=9,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70125",
    )
    multiple_answers_allowed: Optional[ID] = HL7Field(
        position=10,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    answer_choices: Optional[list[CWE]] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70665",
    )
    character_limit: Optional[NM] = HL7Field(
        position=12,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    number_of_decimals: Optional[NM] = HL7Field(
        position=13,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class ORC(HL7Segment):
    _segment_id = "ORC"

    order_control: ID = HL7Field(
        position=1,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70119",
    )
    placer_order_number: Optional[EI] = HL7Field(
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    filler_order_number: Optional[EI] = HL7Field(
        position=3,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    placer_order_group_number: Optional[EI] = HL7Field(
        position=4,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    order_status: Optional[ID] = HL7Field(
        position=5,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70038",
    )
    response_flag: Optional[ID] = HL7Field(
        position=6,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70121",
    )
    parent_order: Optional[list[EIP]] = HL7Field(
        position=8,
        datatype="EIP",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    date_time_of_order_event: Optional[DTM] = HL7Field(
        position=9,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    enterers_location: Optional[PL] = HL7Field(
        position=13,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    call_back_phone_number: Optional[XTN] = HL7Field(
        position=14,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    order_effective_date_time: Optional[DTM] = HL7Field(
        position=15,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    order_control_code_reason: Optional[CWE] = HL7Field(
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70949",
    )
    advanced_beneficiary_notice_code: Optional[CWE] = HL7Field(
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70339",
    )
    order_status_modifier: Optional[CWE] = HL7Field(
        position=25,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70950",
    )
    advanced_beneficiary_notice_override_reason: Optional[CWE] = HL7Field(
        position=26,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70552",
    )
    fillers_expected_availability_date_time: Optional[DTM] = HL7Field(
        position=27,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    confidentiality_code: Optional[CWE] = HL7Field(
        position=28,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70177",
    )
    order_type: Optional[CWE] = HL7Field(
        position=29,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70482",
    )
    enterer_authorization_mode: Optional[CNE] = HL7Field(
        position=30,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70483",
    )
    advanced_beneficiary_notice_date: Optional[DT] = HL7Field(
        position=32,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    alternate_placer_order_number: Optional[list[CX]] = HL7Field(
        position=33,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    order_workflow_profile: Optional[list[CWE]] = HL7Field(
        position=34,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70934",
    )
    action_code: Optional[ID] = HL7Field(
        position=35,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    order_status_date_range: Optional[DR] = HL7Field(
        position=36,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    order_creation_date_time: Optional[DTM] = HL7Field(
        position=37,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    filler_order_group_number: Optional[EI] = HL7Field(
        position=38,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class ORG(HL7Segment):
    _segment_id = "ORG"

    set_id_org: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    organization_unit_code: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70405",
    )
    organization_unit_type_code: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70474",
    )
    primary_org_unit_indicator: Optional[ID] = HL7Field(
        position=4,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    practitioner_org_unit_identifier: Optional[CX] = HL7Field(
        position=5,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    health_care_provider_type_code: Optional[CWE] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70452",
    )
    health_care_provider_classification_code: Optional[CWE] = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70453",
    )
    health_care_provider_area_of_specialization_code: Optional[CWE] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70454",
    )
    effective_date_range: Optional[DR] = HL7Field(
        position=9,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    employment_status_code: Optional[CWE] = HL7Field(
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70066",
    )
    board_approval_indicator: Optional[ID] = HL7Field(
        position=11,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    primary_care_physician_indicator: Optional[ID] = HL7Field(
        position=12,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    cost_center_code: Optional[list[CWE]] = HL7Field(
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70539",
    )


class OVR(HL7Segment):
    _segment_id = "OVR"

    business_rule_override_type: Optional[CWE] = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70518",
    )
    business_rule_override_code: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70521",
    )
    override_comments: Optional[TX] = HL7Field(
        position=3,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    override_entered_by: Optional[XCN] = HL7Field(
        position=4,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    override_authorized_by: Optional[XCN] = HL7Field(
        position=5,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class PAC(HL7Segment):
    _segment_id = "PAC"

    set_id_pac: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    package_id: Optional[EI] = HL7Field(
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    parent_package_id: Optional[EI] = HL7Field(
        position=3,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    position_in_parent_package: Optional[NA] = HL7Field(
        position=4,
        datatype="NA",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    package_type: CWE = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70908",
    )
    package_condition: Optional[list[CWE]] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70544",
    )
    package_handling_code: Optional[list[CWE]] = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70376",
    )
    package_risk_code: Optional[list[CWE]] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70489",
    )
    action_code: Optional[ID] = HL7Field(
        position=9,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class PCE(HL7Segment):
    _segment_id = "PCE"

    set_id_pce: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    cost_center_account_number: Optional[CX] = HL7Field(
        position=2,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70319",
    )
    transaction_code: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70132",
    )
    transaction_amount_unit: Optional[CP] = HL7Field(
        position=4,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class PCR(HL7Segment):
    _segment_id = "PCR"

    implicated_product: CWE = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70670",
    )
    generic_product: Optional[IS] = HL7Field(
        position=2,
        datatype="IS",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70249",
    )
    product_class: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70671",
    )
    total_duration_of_therapy: Optional[CQ] = HL7Field(
        position=4,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    product_manufacture_date: Optional[DTM] = HL7Field(
        position=5,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    product_expiration_date: Optional[DTM] = HL7Field(
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    product_implantation_date: Optional[DTM] = HL7Field(
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    product_explantation_date: Optional[DTM] = HL7Field(
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    single_use_device: Optional[CWE] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70244",
    )
    indication_for_product_use: Optional[CWE] = HL7Field(
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70672",
    )
    product_problem: Optional[CWE] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70245",
    )
    product_serial_lot_number: Optional[ST] = HL7Field(
        position=12,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    product_available_for_inspection: Optional[CWE] = HL7Field(
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70246",
    )
    product_evaluation_performed: Optional[CWE] = HL7Field(
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70673",
    )
    product_evaluation_status: Optional[CWE] = HL7Field(
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70247",
    )
    product_evaluation_results: Optional[CWE] = HL7Field(
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70674",
    )
    evaluated_product_source: Optional[ID] = HL7Field(
        position=17,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70248",
    )
    date_product_returned_to_manufacturer: Optional[DTM] = HL7Field(
        position=18,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    device_operator_qualifications: Optional[ID] = HL7Field(
        position=19,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70242",
    )
    relatedness_assessment: Optional[ID] = HL7Field(
        position=20,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70250",
    )
    action_taken_in_response_to_the_event: Optional[ID] = HL7Field(
        position=21,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70251",
    )
    event_causality_observations: Optional[ID] = HL7Field(
        position=22,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70252",
    )
    indirect_exposure_mechanism: Optional[ID] = HL7Field(
        position=23,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70253",
    )


class PD1(HL7Segment):
    _segment_id = "PD1"

    living_dependency: Optional[list[CWE]] = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70223",
    )
    living_arrangement: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70220",
    )
    patient_primary_facility: Optional[list[XON]] = HL7Field(
        position=3,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70204",
    )
    student_indicator: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70231",
    )
    handicap: Optional[CWE] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70295",
    )
    living_will_code: Optional[CWE] = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70315",
    )
    organ_donor_code: Optional[CWE] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70316",
    )
    separate_bill: Optional[ID] = HL7Field(
        position=9,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    duplicate_patient: Optional[list[CX]] = HL7Field(
        position=10,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    publicity_code: Optional[CWE] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70215",
    )
    protection_indicator: Optional[ID] = HL7Field(
        position=12,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    protection_indicator_effective_date: Optional[DT] = HL7Field(
        position=13,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    place_of_worship: Optional[list[XON]] = HL7Field(
        position=14,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    advance_directive_code: Optional[list[CWE]] = HL7Field(
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70435",
    )
    immunization_registry_status: Optional[CWE] = HL7Field(
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70441",
    )
    immunization_registry_status_effective_date: Optional[DT] = HL7Field(
        position=17,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    publicity_code_effective_date: Optional[DT] = HL7Field(
        position=18,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    military_branch: Optional[CWE] = HL7Field(
        position=19,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70140",
    )
    military_rank_grade: Optional[CWE] = HL7Field(
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70141",
    )
    military_status: Optional[CWE] = HL7Field(
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70142",
    )
    advance_directive_last_verified_date: Optional[DT] = HL7Field(
        position=22,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    retirement_date: Optional[DT] = HL7Field(
        position=23,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class PDA(HL7Segment):
    _segment_id = "PDA"

    death_cause_code: Optional[list[CWE]] = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    death_location: Optional[PL] = HL7Field(
        position=2,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    death_certified_indicator: Optional[ID] = HL7Field(
        position=3,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    death_certificate_signed_date_time: Optional[DTM] = HL7Field(
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    death_certified_by: Optional[XCN] = HL7Field(
        position=5,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    autopsy_indicator: Optional[ID] = HL7Field(
        position=6,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    autopsy_start_and_end_date_time: Optional[DR] = HL7Field(
        position=7,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    autopsy_performed_by: Optional[XCN] = HL7Field(
        position=8,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    coroner_indicator: Optional[ID] = HL7Field(
        position=9,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )


class PDC(HL7Segment):
    _segment_id = "PDC"

    manufacturer_distributor: list[XON] = HL7Field(
        position=1,
        datatype="XON",
        usage=Usage.REQUIRED,
        repeatable=True,
    )
    country: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70675",
    )
    brand_name: ST = HL7Field(
        position=3,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    device_family_name: Optional[ST] = HL7Field(
        position=4,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    generic_name: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70676",
    )
    model_identifier: Optional[list[ST]] = HL7Field(
        position=6,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    catalogue_identifier: Optional[ST] = HL7Field(
        position=7,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    other_identifier: Optional[list[ST]] = HL7Field(
        position=8,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    product_code: Optional[CWE] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70677",
    )
    marketing_basis: Optional[ID] = HL7Field(
        position=10,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70330",
    )
    marketing_approval_id: Optional[ST] = HL7Field(
        position=11,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    labeled_shelf_life: Optional[CQ] = HL7Field(
        position=12,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    expected_shelf_life: Optional[CQ] = HL7Field(
        position=13,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    date_first_marketed: Optional[DTM] = HL7Field(
        position=14,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    date_last_marketed: Optional[DTM] = HL7Field(
        position=15,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class PEO(HL7Segment):
    _segment_id = "PEO"

    event_identifiers_used: Optional[list[CWE]] = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70678",
    )
    event_symptom_diagnosis_code: Optional[list[CWE]] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70679",
    )
    event_onset_date_time: DTM = HL7Field(
        position=3,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    event_exacerbation_date_time: Optional[DTM] = HL7Field(
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    event_improved_date_time: Optional[DTM] = HL7Field(
        position=5,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    event_ended_data_time: Optional[DTM] = HL7Field(
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    event_location_occurred_address: Optional[list[XAD]] = HL7Field(
        position=7,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    event_qualification: Optional[list[ID]] = HL7Field(
        position=8,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70237",
    )
    event_serious: Optional[ID] = HL7Field(
        position=9,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70238",
    )
    event_expected: Optional[ID] = HL7Field(
        position=10,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70239",
    )
    event_outcome: Optional[list[ID]] = HL7Field(
        position=11,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70240",
    )
    patient_outcome: Optional[ID] = HL7Field(
        position=12,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70241",
    )
    event_description_from_others: Optional[list[FT]] = HL7Field(
        position=13,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    event_description_from_original_reporter: Optional[list[FT]] = HL7Field(
        position=14,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    event_description_from_patient: Optional[list[FT]] = HL7Field(
        position=15,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    event_description_from_practitioner: Optional[list[FT]] = HL7Field(
        position=16,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    event_description_from_autopsy: Optional[list[FT]] = HL7Field(
        position=17,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    cause_of_death: Optional[list[CWE]] = HL7Field(
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70680",
    )
    primary_observer_name: Optional[list[XPN]] = HL7Field(
        position=19,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    primary_observer_address: Optional[list[XAD]] = HL7Field(
        position=20,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    primary_observer_telephone: Optional[list[XTN]] = HL7Field(
        position=21,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    primary_observers_qualification: Optional[ID] = HL7Field(
        position=22,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70242",
    )
    confirmation_provided_by: Optional[ID] = HL7Field(
        position=23,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70242",
    )
    primary_observer_aware_date_time: Optional[DTM] = HL7Field(
        position=24,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    primary_observers_identity_may_be_divulged: Optional[ID] = HL7Field(
        position=25,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70243",
    )


class PES(HL7Segment):
    _segment_id = "PES"

    sender_organization_name: Optional[list[XON]] = HL7Field(
        position=1,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    sender_individual_name: Optional[list[XCN]] = HL7Field(
        position=2,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    sender_address: Optional[list[XAD]] = HL7Field(
        position=3,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    sender_telephone: Optional[list[XTN]] = HL7Field(
        position=4,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    sender_event_identifier: Optional[EI] = HL7Field(
        position=5,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    sender_sequence_number: Optional[NM] = HL7Field(
        position=6,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    sender_event_description: Optional[list[FT]] = HL7Field(
        position=7,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    sender_comment: Optional[FT] = HL7Field(
        position=8,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    sender_aware_date_time: Optional[DTM] = HL7Field(
        position=9,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    event_report_date: DTM = HL7Field(
        position=10,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    event_report_timing_type: Optional[ID] = HL7Field(
        position=11,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70234",
    )
    event_report_source: Optional[ID] = HL7Field(
        position=12,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70235",
    )
    event_reported_to: Optional[list[ID]] = HL7Field(
        position=13,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70236",
    )


class PID(HL7Segment):
    _segment_id = "PID"

    set_id_pid: Optional[SI] = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    patient_identifier_list: list[CX] = HL7Field(
        position=3,
        datatype="CX",
        usage=Usage.REQUIRED,
        repeatable=True,
    )
    patient_name: list[XPN] = HL7Field(
        position=5,
        datatype="XPN",
        usage=Usage.REQUIRED,
        repeatable=True,
        table="HL70200",
    )
    mothers_maiden_name: Optional[list[XPN]] = HL7Field(
        position=6,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    date_time_of_birth: Optional[DTM] = HL7Field(
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    administrative_sex: Optional[CWE] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70001",
    )
    race: Optional[list[CWE]] = HL7Field(
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70005",
    )
    patient_address: Optional[list[XAD]] = HL7Field(
        position=11,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    primary_language: Optional[CWE] = HL7Field(
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70296",
    )
    marital_status: Optional[CWE] = HL7Field(
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70002",
    )
    religion: Optional[CWE] = HL7Field(
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70006",
    )
    patient_account_number: Optional[CX] = HL7Field(
        position=18,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70061",
    )
    mothers_identifier: Optional[list[CX]] = HL7Field(
        position=21,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70061",
    )
    ethnic_group: Optional[list[CWE]] = HL7Field(
        position=22,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70189",
    )
    birth_place: Optional[ST] = HL7Field(
        position=23,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    multiple_birth_indicator: Optional[ID] = HL7Field(
        position=24,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    birth_order: Optional[NM] = HL7Field(
        position=25,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    citizenship: Optional[list[CWE]] = HL7Field(
        position=26,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70171",
    )
    veterans_military_status: Optional[CWE] = HL7Field(
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70172",
    )
    patient_death_date_and_time: Optional[DTM] = HL7Field(
        position=29,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    patient_death_indicator: Optional[ID] = HL7Field(
        position=30,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    identity_unknown_indicator: Optional[ID] = HL7Field(
        position=31,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    identity_reliability_code: Optional[list[CWE]] = HL7Field(
        position=32,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70445",
    )
    last_update_date_time: Optional[DTM] = HL7Field(
        position=33,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    last_update_facility: Optional[HD] = HL7Field(
        position=34,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    taxonomic_classification_code: Optional[CWE] = HL7Field(
        position=35,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    breed_code: Optional[CWE] = HL7Field(
        position=36,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70447",
    )
    strain: Optional[ST] = HL7Field(
        position=37,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    production_class_code: Optional[CWE] = HL7Field(
        position=38,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70429",
    )
    tribal_citizenship: Optional[list[CWE]] = HL7Field(
        position=39,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70171",
    )
    patient_telecommunication_information: Optional[list[XTN]] = HL7Field(
        position=40,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )


class PKG(HL7Segment):
    _segment_id = "PKG"

    set_id_pkg: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    packaging_units: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70818",
    )
    default_order_unit_of_measure_indicator: Optional[CNE] = HL7Field(
        position=3,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    package_quantity: Optional[NM] = HL7Field(
        position=4,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    price: Optional[CP] = HL7Field(
        position=5,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    future_item_price: Optional[CP] = HL7Field(
        position=6,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    future_item_price_effective_date: Optional[DTM] = HL7Field(
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    global_trade_item_number: Optional[CWE] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    contract_price: Optional[MO] = HL7Field(
        position=9,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    quantity_of_each: Optional[NM] = HL7Field(
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    vendor_catalog_number: Optional[EI] = HL7Field(
        position=11,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class PM1(HL7Segment):
    _segment_id = "PM1"

    health_plan_id: CWE = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70072",
    )
    insurance_company_id: list[CX] = HL7Field(
        position=2,
        datatype="CX",
        usage=Usage.REQUIRED,
        repeatable=True,
    )
    insurance_company_name: Optional[list[XON]] = HL7Field(
        position=3,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    insurance_company_address: Optional[list[XAD]] = HL7Field(
        position=4,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    insurance_co_contact_person: Optional[list[XPN]] = HL7Field(
        position=5,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    insurance_co_phone_number: Optional[list[XTN]] = HL7Field(
        position=6,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    group_number: Optional[ST] = HL7Field(
        position=7,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    group_name: Optional[list[XON]] = HL7Field(
        position=8,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    plan_effective_date: Optional[DT] = HL7Field(
        position=9,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    plan_expiration_date: Optional[DT] = HL7Field(
        position=10,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    patient_dob_required: Optional[ID] = HL7Field(
        position=11,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    patient_gender_required: Optional[ID] = HL7Field(
        position=12,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    patient_relationship_required: Optional[ID] = HL7Field(
        position=13,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    patient_signature_required: Optional[ID] = HL7Field(
        position=14,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    diagnosis_required: Optional[ID] = HL7Field(
        position=15,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    service_required: Optional[ID] = HL7Field(
        position=16,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    patient_name_required: Optional[ID] = HL7Field(
        position=17,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    patient_address_required: Optional[ID] = HL7Field(
        position=18,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    subscribers_name_required: Optional[ID] = HL7Field(
        position=19,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    workmans_comp_indicator: Optional[ID] = HL7Field(
        position=20,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    bill_type_required: Optional[ID] = HL7Field(
        position=21,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    commercial_carrier_name_and_address_required: Optional[ID] = HL7Field(
        position=22,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    policy_number_pattern: Optional[ST] = HL7Field(
        position=23,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    group_number_pattern: Optional[ST] = HL7Field(
        position=24,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class PMT(HL7Segment):
    _segment_id = "PMT"

    payment_remittance_advice_number: EI = HL7Field(
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    payment_remittance_effective_date_time: DTM = HL7Field(
        position=2,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    payment_remittance_expiration_date_time: DTM = HL7Field(
        position=3,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    payment_method: CWE = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70570",
    )
    payment_remittance_date_time: DTM = HL7Field(
        position=5,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    payment_remittance_amount: CP = HL7Field(
        position=6,
        datatype="CP",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    check_number: Optional[EI] = HL7Field(
        position=7,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    payee_bank_identification: Optional[XON] = HL7Field(
        position=8,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    payee_transit_number: Optional[ST] = HL7Field(
        position=9,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    payee_bank_account_id: Optional[CX] = HL7Field(
        position=10,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    payment_organization: XON = HL7Field(
        position=11,
        datatype="XON",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    esr_code_line: Optional[ST] = HL7Field(
        position=12,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class PR1(HL7Segment):
    _segment_id = "PR1"

    set_id_pr1: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    procedure_code: CNE = HL7Field(
        position=3,
        datatype="CNE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70088",
    )
    procedure_date_time: DTM = HL7Field(
        position=5,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    procedure_functional_type: Optional[CWE] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70230",
    )
    procedure_minutes: Optional[NM] = HL7Field(
        position=7,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    anesthesia_code: Optional[CWE] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70019",
    )
    anesthesia_minutes: Optional[NM] = HL7Field(
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    consent_code: Optional[CWE] = HL7Field(
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70059",
    )
    procedure_priority: Optional[NM] = HL7Field(
        position=14,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70418",
    )
    associated_diagnosis_code: Optional[CWE] = HL7Field(
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70051",
    )
    procedure_code_modifier: Optional[list[CNE]] = HL7Field(
        position=16,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70340",
    )
    procedure_drg_type: Optional[CWE] = HL7Field(
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70416",
    )
    tissue_type_code: Optional[list[CWE]] = HL7Field(
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70417",
    )
    procedure_identifier: Optional[EI] = HL7Field(
        position=19,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    procedure_action_code: Optional[ID] = HL7Field(
        position=20,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70206",
    )
    drg_procedure_determination_status: Optional[CWE] = HL7Field(
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70761",
    )
    drg_procedure_relevance: Optional[CWE] = HL7Field(
        position=22,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70763",
    )
    treating_organizational_unit: Optional[list[PL]] = HL7Field(
        position=23,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    respiratory_within_surgery: Optional[ID] = HL7Field(
        position=24,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    parent_procedure_id: Optional[EI] = HL7Field(
        position=25,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class PRA(HL7Segment):
    _segment_id = "PRA"

    primary_key_value_pra: Optional[CWE] = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70681",
    )
    practitioner_group: Optional[list[CWE]] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70358",
    )
    practitioner_category: Optional[list[CWE]] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70186",
    )
    provider_billing: Optional[ID] = HL7Field(
        position=4,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70187",
    )
    specialty: Optional[list[SPD]] = HL7Field(
        position=5,
        datatype="SPD",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70337",
    )
    practitioner_id_numbers: Optional[list[PLN]] = HL7Field(
        position=6,
        datatype="PLN",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70338",
    )
    privileges: Optional[list[PIP]] = HL7Field(
        position=7,
        datatype="PIP",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    date_entered_practice: Optional[DT] = HL7Field(
        position=8,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    institution: Optional[CWE] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70537",
    )
    date_left_practice: Optional[DT] = HL7Field(
        position=10,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    government_reimbursement_billing_eligibility: Optional[list[CWE]] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70401",
    )
    set_id_pra: Optional[SI] = HL7Field(
        position=12,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class PRB(HL7Segment):
    _segment_id = "PRB"

    action_code: ID = HL7Field(
        position=1,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    action_date_time: DTM = HL7Field(
        position=2,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    problem_id: CWE = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    problem_instance_id: EI = HL7Field(
        position=4,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    episode_of_care_id: Optional[EI] = HL7Field(
        position=5,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    problem_list_priority: Optional[NM] = HL7Field(
        position=6,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    problem_established_date_time: Optional[DTM] = HL7Field(
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    anticipated_problem_resolution_date_time: Optional[DTM] = HL7Field(
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    actual_problem_resolution_date_time: Optional[DTM] = HL7Field(
        position=9,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    problem_classification: Optional[CWE] = HL7Field(
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    problem_management_discipline: Optional[list[CWE]] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    problem_persistence: Optional[CWE] = HL7Field(
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    problem_confirmation_status: Optional[CWE] = HL7Field(
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    problem_life_cycle_status: Optional[CWE] = HL7Field(
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    problem_life_cycle_status_date_time: Optional[DTM] = HL7Field(
        position=15,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    problem_date_of_onset: Optional[DTM] = HL7Field(
        position=16,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    problem_onset_text: Optional[ST] = HL7Field(
        position=17,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    problem_ranking: Optional[CWE] = HL7Field(
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    certainty_of_problem: Optional[CWE] = HL7Field(
        position=19,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    probability_of_problem_0_1: Optional[NM] = HL7Field(
        position=20,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    individual_awareness_of_problem: Optional[CWE] = HL7Field(
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    problem_prognosis: Optional[CWE] = HL7Field(
        position=22,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    individual_awareness_of_prognosis: Optional[CWE] = HL7Field(
        position=23,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    family_significant_other_awareness_of_problem_prognosis: Optional[ST] = HL7Field(
        position=24,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    security_sensitivity: Optional[CWE] = HL7Field(
        position=25,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    problem_severity: Optional[CWE] = HL7Field(
        position=26,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70836",
    )
    problem_perspective: Optional[CWE] = HL7Field(
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70838",
    )
    mood_code: Optional[CNE] = HL7Field(
        position=28,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70725",
    )


class PRC(HL7Segment):
    _segment_id = "PRC"

    primary_key_value_prc: CWE = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70132",
    )
    facility_id_prc: Optional[list[CWE]] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70464",
    )
    department: Optional[list[CWE]] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70184",
    )
    valid_patient_classes: Optional[list[CWE]] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70004",
    )
    price: Optional[list[CP]] = HL7Field(
        position=5,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    formula: Optional[list[ST]] = HL7Field(
        position=6,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    minimum_quantity: Optional[NM] = HL7Field(
        position=7,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    maximum_quantity: Optional[NM] = HL7Field(
        position=8,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    minimum_price: Optional[MO] = HL7Field(
        position=9,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    maximum_price: Optional[MO] = HL7Field(
        position=10,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    effective_start_date: Optional[DTM] = HL7Field(
        position=11,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    effective_end_date: Optional[DTM] = HL7Field(
        position=12,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    price_override_flag: Optional[CWE] = HL7Field(
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70268",
    )
    billing_category: Optional[list[CWE]] = HL7Field(
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70293",
    )
    chargeable_flag: Optional[ID] = HL7Field(
        position=15,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    active_inactive_flag: Optional[ID] = HL7Field(
        position=16,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70183",
    )
    cost: Optional[MO] = HL7Field(
        position=17,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    charge_on_indicator: Optional[CWE] = HL7Field(
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70269",
    )


class PRD(HL7Segment):
    _segment_id = "PRD"

    provider_role: list[CWE] = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=True,
        table="HL70286",
    )
    provider_name: Optional[list[XPN]] = HL7Field(
        position=2,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    provider_address: Optional[list[XAD]] = HL7Field(
        position=3,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    provider_location: Optional[PL] = HL7Field(
        position=4,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    provider_communication_information: Optional[list[XTN]] = HL7Field(
        position=5,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    preferred_method_of_contact: Optional[CWE] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70185",
    )
    provider_identifiers: Optional[list[PLN]] = HL7Field(
        position=7,
        datatype="PLN",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70338",
    )
    effective_start_date_of_provider_role: Optional[DTM] = HL7Field(
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    effective_end_date_of_provider_role: Optional[list[DTM]] = HL7Field(
        position=9,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    provider_organization_name_and_identifier: Optional[XON] = HL7Field(
        position=10,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    provider_organization_address: Optional[list[XAD]] = HL7Field(
        position=11,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    provider_organization_location_information: Optional[list[PL]] = HL7Field(
        position=12,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    provider_organization_communication_information: Optional[list[XTN]] = HL7Field(
        position=13,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    provider_organization_method_of_contact: Optional[CWE] = HL7Field(
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70185",
    )


class PRT(HL7Segment):
    _segment_id = "PRT"

    participation_instance_id: Optional[EI] = HL7Field(
        position=1,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    action_code: ID = HL7Field(
        position=2,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    action_reason: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    role_of_participation: CWE = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70912",
    )
    person: Optional[list[XCN]] = HL7Field(
        position=5,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    person_provider_type: Optional[CWE] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    organization_unit_type: Optional[CWE] = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70406",
    )
    organization: Optional[list[XON]] = HL7Field(
        position=8,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    location: Optional[list[PL]] = HL7Field(
        position=9,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    device: Optional[list[EI]] = HL7Field(
        position=10,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    begin_date_time_arrival_time: Optional[DTM] = HL7Field(
        position=11,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    end_date_time_departure_time: Optional[DTM] = HL7Field(
        position=12,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    qualitative_duration: Optional[CWE] = HL7Field(
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    address: Optional[list[XAD]] = HL7Field(
        position=14,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    telecommunication_address: Optional[list[XTN]] = HL7Field(
        position=15,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    udi_device_identifier: Optional[EI] = HL7Field(
        position=16,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    device_manufacture_date: Optional[DTM] = HL7Field(
        position=17,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    device_expiry_date: Optional[DTM] = HL7Field(
        position=18,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    device_lot_number: Optional[ST] = HL7Field(
        position=19,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    device_serial_number: Optional[ST] = HL7Field(
        position=20,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    device_donation_identification: Optional[EI] = HL7Field(
        position=21,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    device_type: Optional[CNE] = HL7Field(
        position=22,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70961",
    )
    preferred_method_of_contact: Optional[CWE] = HL7Field(
        position=23,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70185",
    )
    contact_identifiers: Optional[list[PLN]] = HL7Field(
        position=24,
        datatype="PLN",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70338",
    )


class PSG(HL7Segment):
    _segment_id = "PSG"

    provider_product_service_group_number: EI = HL7Field(
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    payer_product_service_group_number: Optional[EI] = HL7Field(
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    product_service_group_sequence_number: SI = HL7Field(
        position=3,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    adjudicate_as_group: ID = HL7Field(
        position=4,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70136",
    )
    product_service_group_billed_amount: CP = HL7Field(
        position=5,
        datatype="CP",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    product_service_group_description: ST = HL7Field(
        position=6,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )


class PSH(HL7Segment):
    _segment_id = "PSH"

    report_type: ST = HL7Field(
        position=1,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    report_form_identifier: Optional[ST] = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    report_date: DTM = HL7Field(
        position=3,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    report_interval_start_date: Optional[DTM] = HL7Field(
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    report_interval_end_date: Optional[DTM] = HL7Field(
        position=5,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    quantity_manufactured: Optional[CQ] = HL7Field(
        position=6,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    quantity_distributed: Optional[CQ] = HL7Field(
        position=7,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    quantity_distributed_method: Optional[ID] = HL7Field(
        position=8,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70329",
    )
    quantity_distributed_comment: Optional[FT] = HL7Field(
        position=9,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    quantity_in_use: Optional[CQ] = HL7Field(
        position=10,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    quantity_in_use_method: Optional[ID] = HL7Field(
        position=11,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70329",
    )
    quantity_in_use_comment: Optional[FT] = HL7Field(
        position=12,
        datatype="FT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    number_of_product_experience_reports_filed_by_facility: Optional[NM] = HL7Field(
        position=13,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    number_of_product_experience_reports_filed_by_distributor: Optional[NM] = HL7Field(
        position=14,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class PSL(HL7Segment):
    _segment_id = "PSL"

    provider_product_service_line_item_number: EI = HL7Field(
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    payer_product_service_line_item_number: Optional[EI] = HL7Field(
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    product_service_line_item_sequence_number: SI = HL7Field(
        position=3,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    provider_tracking_id: Optional[EI] = HL7Field(
        position=4,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    payer_tracking_id: Optional[EI] = HL7Field(
        position=5,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    product_service_line_item_status: CWE = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70559",
    )
    product_service_code: CWE = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70879",
    )
    product_service_code_modifier: Optional[CWE] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70880",
    )
    product_service_code_description: Optional[ST] = HL7Field(
        position=9,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    product_service_effective_date: Optional[DTM] = HL7Field(
        position=10,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    product_service_expiration_date: Optional[DTM] = HL7Field(
        position=11,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    product_service_quantity: Optional[CQ] = HL7Field(
        position=12,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70560",
    )
    product_service_unit_cost: Optional[CP] = HL7Field(
        position=13,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    number_of_items_per_unit: Optional[NM] = HL7Field(
        position=14,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    product_service_gross_amount: Optional[CP] = HL7Field(
        position=15,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    product_service_billed_amount: Optional[CP] = HL7Field(
        position=16,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    product_service_clarification_code_type: Optional[CWE] = HL7Field(
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70561",
    )
    product_service_clarification_code_value: Optional[ST] = HL7Field(
        position=18,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    health_document_reference_identifier: Optional[EI] = HL7Field(
        position=19,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    processing_consideration_code: Optional[CWE] = HL7Field(
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70562",
    )
    restricted_disclosure_indicator: ID = HL7Field(
        position=21,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70532",
    )
    related_product_service_code_indicator: Optional[CWE] = HL7Field(
        position=22,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70879",
    )
    product_service_amount_for_physician: Optional[CP] = HL7Field(
        position=23,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    product_service_cost_factor: Optional[NM] = HL7Field(
        position=24,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    cost_center: Optional[CX] = HL7Field(
        position=25,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    billing_period: Optional[DR] = HL7Field(
        position=26,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    days_without_billing: Optional[NM] = HL7Field(
        position=27,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    session_no: Optional[NM] = HL7Field(
        position=28,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    executing_physician_id: Optional[XCN] = HL7Field(
        position=29,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    responsible_physician_id: Optional[XCN] = HL7Field(
        position=30,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    role_executing_physician: Optional[CWE] = HL7Field(
        position=31,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70881",
    )
    medical_role_executing_physician: Optional[CWE] = HL7Field(
        position=32,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70882",
    )
    side_of_body: Optional[CWE] = HL7Field(
        position=33,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70894",
    )
    number_of_t_ps_pp: Optional[NM] = HL7Field(
        position=34,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    tp_value_pp: Optional[CP] = HL7Field(
        position=35,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    internal_scaling_factor_pp: Optional[NM] = HL7Field(
        position=36,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    external_scaling_factor_pp: Optional[NM] = HL7Field(
        position=37,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    amount_pp: Optional[CP] = HL7Field(
        position=38,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    number_of_t_ps_technical_part: Optional[NM] = HL7Field(
        position=39,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    tp_value_technical_part: Optional[CP] = HL7Field(
        position=40,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    internal_scaling_factor_technical_part: Optional[NM] = HL7Field(
        position=41,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    external_scaling_factor_technical_part: Optional[NM] = HL7Field(
        position=42,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    amount_technical_part: Optional[CP] = HL7Field(
        position=43,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    total_amount_professional_part_technical_part: Optional[CP] = HL7Field(
        position=44,
        datatype="CP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    vat_rate: Optional[NM] = HL7Field(
        position=45,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    main_service: Optional[ID] = HL7Field(
        position=46,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    validation: Optional[ID] = HL7Field(
        position=47,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    comment: Optional[ST] = HL7Field(
        position=48,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class PSS(HL7Segment):
    _segment_id = "PSS"

    provider_product_service_section_number: EI = HL7Field(
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    payer_product_service_section_number: Optional[EI] = HL7Field(
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    product_service_section_sequence_number: SI = HL7Field(
        position=3,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    billed_amount: CP = HL7Field(
        position=4,
        datatype="CP",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    section_description_or_heading: ST = HL7Field(
        position=5,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )


class PTH(HL7Segment):
    _segment_id = "PTH"

    action_code: ID = HL7Field(
        position=1,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    pathway_id: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    pathway_instance_id: EI = HL7Field(
        position=3,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    pathway_established_date_time: DTM = HL7Field(
        position=4,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    pathway_life_cycle_status: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    change_pathway_life_cycle_status_date_time: Optional[DTM] = HL7Field(
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    mood_code: Optional[CNE] = HL7Field(
        position=7,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70725",
    )


class PV1(HL7Segment):
    _segment_id = "PV1"

    set_id_pv1: Optional[SI] = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    patient_class: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70004",
    )
    assigned_patient_location: Optional[PL] = HL7Field(
        position=3,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    admission_type: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70007",
    )
    preadmit_number: Optional[CX] = HL7Field(
        position=5,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    prior_patient_location: Optional[PL] = HL7Field(
        position=6,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    attending_doctor: Optional[list[XCN]] = HL7Field(
        position=7,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70010",
    )
    referring_doctor: Optional[list[XCN]] = HL7Field(
        position=8,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70010",
    )
    consulting_doctor: Optional[list[XCN]] = HL7Field(
        position=9,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    hospital_service: Optional[CWE] = HL7Field(
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70069",
    )
    temporary_location: Optional[PL] = HL7Field(
        position=11,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    preadmit_test_indicator: Optional[CWE] = HL7Field(
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70087",
    )
    re_admission_indicator: Optional[CWE] = HL7Field(
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70092",
    )
    admit_source: Optional[CWE] = HL7Field(
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70023",
    )
    ambulatory_status: Optional[list[CWE]] = HL7Field(
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70009",
    )
    vip_indicator: Optional[CWE] = HL7Field(
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70099",
    )
    admitting_doctor: Optional[list[XCN]] = HL7Field(
        position=17,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70010",
    )
    patient_type: Optional[CWE] = HL7Field(
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70018",
    )
    visit_number: Optional[CX] = HL7Field(
        position=19,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    financial_class: Optional[list[FC]] = HL7Field(
        position=20,
        datatype="FC",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70064",
    )
    charge_price_indicator: Optional[CWE] = HL7Field(
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70032",
    )
    courtesy_code: Optional[CWE] = HL7Field(
        position=22,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70045",
    )
    credit_rating: Optional[CWE] = HL7Field(
        position=23,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70046",
    )
    contract_code: Optional[list[CWE]] = HL7Field(
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70044",
    )
    contract_effective_date: Optional[list[DT]] = HL7Field(
        position=25,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    contract_amount: Optional[list[NM]] = HL7Field(
        position=26,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    contract_period: Optional[list[NM]] = HL7Field(
        position=27,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    interest_code: Optional[CWE] = HL7Field(
        position=28,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70073",
    )
    transfer_to_bad_debt_code: Optional[CWE] = HL7Field(
        position=29,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70110",
    )
    transfer_to_bad_debt_date: Optional[DT] = HL7Field(
        position=30,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bad_debt_agency_code: Optional[CWE] = HL7Field(
        position=31,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70021",
    )
    bad_debt_transfer_amount: Optional[NM] = HL7Field(
        position=32,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bad_debt_recovery_amount: Optional[NM] = HL7Field(
        position=33,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    delete_account_indicator: Optional[CWE] = HL7Field(
        position=34,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70111",
    )
    delete_account_date: Optional[DT] = HL7Field(
        position=35,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    discharge_disposition: Optional[CWE] = HL7Field(
        position=36,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70112",
    )
    discharged_to_location: Optional[DLD] = HL7Field(
        position=37,
        datatype="DLD",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70113",
    )
    diet_type: Optional[CWE] = HL7Field(
        position=38,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70114",
    )
    servicing_facility: Optional[CWE] = HL7Field(
        position=39,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70115",
    )
    account_status: Optional[CWE] = HL7Field(
        position=41,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70117",
    )
    pending_location: Optional[PL] = HL7Field(
        position=42,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    prior_temporary_location: Optional[PL] = HL7Field(
        position=43,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    admit_date_time: Optional[DTM] = HL7Field(
        position=44,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    discharge_date_time: Optional[DTM] = HL7Field(
        position=45,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    current_patient_balance: Optional[NM] = HL7Field(
        position=46,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    total_charges: Optional[NM] = HL7Field(
        position=47,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    total_adjustments: Optional[NM] = HL7Field(
        position=48,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    total_payments: Optional[NM] = HL7Field(
        position=49,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    alternate_visit_id: Optional[list[CX]] = HL7Field(
        position=50,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70203",
    )
    visit_indicator: Optional[CWE] = HL7Field(
        position=51,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70326",
    )
    service_episode_description: Optional[ST] = HL7Field(
        position=53,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    service_episode_identifier: Optional[CX] = HL7Field(
        position=54,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class PV2(HL7Segment):
    _segment_id = "PV2"

    prior_pending_location: Optional[PL] = HL7Field(
        position=1,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    accommodation_code: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70129",
    )
    admit_reason: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    transfer_reason: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    patient_valuables: Optional[list[ST]] = HL7Field(
        position=5,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    patient_valuables_location: Optional[ST] = HL7Field(
        position=6,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    visit_user_code: Optional[list[CWE]] = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70130",
    )
    expected_admit_date_time: Optional[DTM] = HL7Field(
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    expected_discharge_date_time: Optional[DTM] = HL7Field(
        position=9,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    estimated_length_of_inpatient_stay: Optional[NM] = HL7Field(
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    actual_length_of_inpatient_stay: Optional[NM] = HL7Field(
        position=11,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    visit_description: Optional[ST] = HL7Field(
        position=12,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    referral_source_code: Optional[list[XCN]] = HL7Field(
        position=13,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    previous_service_date: Optional[DT] = HL7Field(
        position=14,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    employment_illness_related_indicator: Optional[ID] = HL7Field(
        position=15,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    purge_status_code: Optional[CWE] = HL7Field(
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70213",
    )
    purge_status_date: Optional[DT] = HL7Field(
        position=17,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    special_program_code: Optional[CWE] = HL7Field(
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70214",
    )
    retention_indicator: Optional[ID] = HL7Field(
        position=19,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    expected_number_of_insurance_plans: Optional[NM] = HL7Field(
        position=20,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    visit_publicity_code: Optional[CWE] = HL7Field(
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70215",
    )
    visit_protection_indicator: Optional[ID] = HL7Field(
        position=22,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    clinic_organization_name: Optional[list[XON]] = HL7Field(
        position=23,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    patient_status_code: Optional[CWE] = HL7Field(
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70216",
    )
    visit_priority_code: Optional[CWE] = HL7Field(
        position=25,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70217",
    )
    previous_treatment_date: Optional[DT] = HL7Field(
        position=26,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    expected_discharge_disposition: Optional[CWE] = HL7Field(
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70112",
    )
    signature_on_file_date: Optional[DT] = HL7Field(
        position=28,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    first_similar_illness_date: Optional[DT] = HL7Field(
        position=29,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    patient_charge_adjustment_code: Optional[CWE] = HL7Field(
        position=30,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70218",
    )
    recurring_service_code: Optional[CWE] = HL7Field(
        position=31,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70219",
    )
    billing_media_code: Optional[ID] = HL7Field(
        position=32,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    expected_surgery_date_and_time: Optional[DTM] = HL7Field(
        position=33,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    military_partnership_code: Optional[ID] = HL7Field(
        position=34,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    military_non_availability_code: Optional[ID] = HL7Field(
        position=35,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    newborn_baby_indicator: Optional[ID] = HL7Field(
        position=36,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    baby_detained_indicator: Optional[ID] = HL7Field(
        position=37,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    mode_of_arrival_code: Optional[CWE] = HL7Field(
        position=38,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70430",
    )
    recreational_drug_use_code: Optional[list[CWE]] = HL7Field(
        position=39,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70431",
    )
    admission_level_of_care_code: Optional[CWE] = HL7Field(
        position=40,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70432",
    )
    precaution_code: Optional[list[CWE]] = HL7Field(
        position=41,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70433",
    )
    patient_condition_code: Optional[CWE] = HL7Field(
        position=42,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70434",
    )
    living_will_code: Optional[CWE] = HL7Field(
        position=43,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70315",
    )
    organ_donor_code: Optional[CWE] = HL7Field(
        position=44,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70316",
    )
    advance_directive_code: Optional[list[CWE]] = HL7Field(
        position=45,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70435",
    )
    patient_status_effective_date: Optional[DT] = HL7Field(
        position=46,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    expected_loa_return_date_time: Optional[DTM] = HL7Field(
        position=47,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    expected_pre_admission_testing_date_time: Optional[DTM] = HL7Field(
        position=48,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    notify_clergy_code: Optional[list[CWE]] = HL7Field(
        position=49,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70534",
    )
    advance_directive_last_verified_date: Optional[DT] = HL7Field(
        position=50,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class PYE(HL7Segment):
    _segment_id = "PYE"

    set_id_pye: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    payee_type: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70557",
    )
    payee_relationship_to_invoice_patient: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70558",
    )
    payee_identification_list: Optional[XON] = HL7Field(
        position=4,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    payee_person_name: Optional[XPN] = HL7Field(
        position=5,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    payee_address: Optional[XAD] = HL7Field(
        position=6,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    payment_method: Optional[CWE] = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70570",
    )


class QAK(HL7Segment):
    _segment_id = "QAK"

    query_tag: Optional[ST] = HL7Field(
        position=1,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    query_response_status: Optional[ID] = HL7Field(
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70208",
    )
    message_query_name: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70471",
    )
    hit_count_total: Optional[NM] = HL7Field(
        position=4,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    this_payload: Optional[NM] = HL7Field(
        position=5,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    hits_remaining: Optional[NM] = HL7Field(
        position=6,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class QID(HL7Segment):
    _segment_id = "QID"

    query_tag: ST = HL7Field(
        position=1,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    message_query_name: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70471",
    )


class QPD(HL7Segment):
    _segment_id = "QPD"

    message_query_name: CWE = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70471",
    )
    query_tag: Optional[ST] = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    user_parameters_in_successive_fields: Optional[varies] = HL7Field(
        position=3,
        datatype="varies",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class QRD(HL7Segment):
    _segment_id = "QRD"

    pass


class QRF(HL7Segment):
    _segment_id = "QRF"

    pass


class QRI(HL7Segment):
    _segment_id = "QRI"

    candidate_confidence: Optional[NM] = HL7Field(
        position=1,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    match_reason_code: Optional[list[CWE]] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70392",
    )
    algorithm_descriptor: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70393",
    )


class RCP(HL7Segment):
    _segment_id = "RCP"

    query_priority: Optional[ID] = HL7Field(
        position=1,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70091",
    )
    quantity_limited_request: Optional[CQ] = HL7Field(
        position=2,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70126",
    )
    response_modality: Optional[CNE] = HL7Field(
        position=3,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70394",
    )
    execution_and_delivery_time: Optional[DTM] = HL7Field(
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    modify_indicator: Optional[ID] = HL7Field(
        position=5,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70395",
    )
    sort_by_field: Optional[list[SRT]] = HL7Field(
        position=6,
        datatype="SRT",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    segment_group_inclusion: Optional[list[ID]] = HL7Field(
        position=7,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70391",
    )


class RDF(HL7Segment):
    _segment_id = "RDF"

    number_of_columns_per_row: NM = HL7Field(
        position=1,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    column_description: list[RCD] = HL7Field(
        position=2,
        datatype="RCD",
        usage=Usage.REQUIRED,
        repeatable=True,
        table="HL70440",
    )


class RDT(HL7Segment):
    _segment_id = "RDT"

    column_value: varies = HL7Field(
        position=1,
        datatype="varies",
        usage=Usage.REQUIRED,
        repeatable=False,
    )


class REL(HL7Segment):
    _segment_id = "REL"

    set_id_rel: Optional[SI] = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    relationship_type: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70948",
    )
    this_relationship_instance_identifier: EI = HL7Field(
        position=3,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    source_information_instance_identifier: EI = HL7Field(
        position=4,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    target_information_instance_identifier: EI = HL7Field(
        position=5,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    asserting_entity_instance_id: Optional[EI] = HL7Field(
        position=6,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    asserting_person: Optional[XCN] = HL7Field(
        position=7,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    asserting_organization: Optional[XON] = HL7Field(
        position=8,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    assertor_address: Optional[XAD] = HL7Field(
        position=9,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    assertor_contact: Optional[XTN] = HL7Field(
        position=10,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    assertion_date_range: Optional[DR] = HL7Field(
        position=11,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    negation_indicator: Optional[ID] = HL7Field(
        position=12,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    certainty_of_relationship: Optional[CWE] = HL7Field(
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    priority_no: Optional[NM] = HL7Field(
        position=14,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    priority_sequence_no_rel_preference_for_consideration: Optional[NM] = HL7Field(
        position=15,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    separability_indicator: Optional[ID] = HL7Field(
        position=16,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    source_information_instance_object_type: Optional[ID] = HL7Field(
        position=17,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70203",
    )
    target_information_instance_object_type: Optional[ID] = HL7Field(
        position=18,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70203",
    )


class RF1(HL7Segment):
    _segment_id = "RF1"

    referral_status: Optional[CWE] = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70283",
    )
    referral_priority: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70280",
    )
    referral_type: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70281",
    )
    referral_disposition: Optional[list[CWE]] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70282",
    )
    referral_category: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70284",
    )
    originating_referral_identifier: EI = HL7Field(
        position=6,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    effective_date: Optional[DTM] = HL7Field(
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    expiration_date: Optional[DTM] = HL7Field(
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    process_date: Optional[DTM] = HL7Field(
        position=9,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    referral_reason: Optional[list[CWE]] = HL7Field(
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70336",
    )
    external_referral_identifier: Optional[list[EI]] = HL7Field(
        position=11,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    referral_documentation_completion_status: Optional[CWE] = HL7Field(
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70865",
    )
    planned_treatment_stop_date: Optional[DTM] = HL7Field(
        position=13,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    referral_reason_text: Optional[ST] = HL7Field(
        position=14,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    number_of_authorized_treatments_units: Optional[CQ] = HL7Field(
        position=15,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    number_of_used_treatments_units: Optional[CQ] = HL7Field(
        position=16,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    number_of_schedule_treatments_units: Optional[CQ] = HL7Field(
        position=17,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    remaining_benefit_amount: Optional[MO] = HL7Field(
        position=18,
        datatype="MO",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    authorized_provider: Optional[XON] = HL7Field(
        position=19,
        datatype="XON",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    authorized_health_professional: Optional[XCN] = HL7Field(
        position=20,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    source_text: Optional[ST] = HL7Field(
        position=21,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    source_date: Optional[DTM] = HL7Field(
        position=22,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    source_phone: Optional[XTN] = HL7Field(
        position=23,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    comment: Optional[ST] = HL7Field(
        position=24,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    action_code: Optional[ID] = HL7Field(
        position=25,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70206",
    )


class RFI(HL7Segment):
    _segment_id = "RFI"

    request_date: DTM = HL7Field(
        position=1,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    response_due_date: DTM = HL7Field(
        position=2,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    patient_consent: Optional[ID] = HL7Field(
        position=3,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    date_additional_information_was_submitted: Optional[DTM] = HL7Field(
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class RGS(HL7Segment):
    _segment_id = "RGS"

    set_id_rgs: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    segment_action_code: Optional[ID] = HL7Field(
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70206",
    )
    resource_group_id: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class RMI(HL7Segment):
    _segment_id = "RMI"

    risk_management_incident_code: Optional[CWE] = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70427",
    )
    date_time_incident: Optional[DTM] = HL7Field(
        position=2,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    incident_type_code: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70428",
    )


class ROL(HL7Segment):
    _segment_id = "ROL"

    pass


class RQ1(HL7Segment):
    _segment_id = "RQ1"

    anticipated_price: Optional[ST] = HL7Field(
        position=1,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    manufacturer_identifier: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70385",
    )
    manufacturers_catalog: Optional[ST] = HL7Field(
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    vendor_id: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70683",
    )
    vendor_catalog: Optional[ST] = HL7Field(
        position=5,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    taxable: Optional[ID] = HL7Field(
        position=6,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    substitute_allowed: Optional[ID] = HL7Field(
        position=7,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )


class RQD(HL7Segment):
    _segment_id = "RQD"

    requisition_line_number: Optional[SI] = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    item_code_internal: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70684",
    )
    item_code_external: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70685",
    )
    hospital_item_code: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70686",
    )
    requisition_quantity: Optional[NM] = HL7Field(
        position=5,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    requisition_unit_of_measure: Optional[CWE] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70687",
    )
    cost_center_account_number: Optional[CX] = HL7Field(
        position=7,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70319",
    )
    item_natural_account_code: Optional[CWE] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70320",
    )
    deliver_to_id: Optional[CWE] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70688",
    )
    date_needed: Optional[DT] = HL7Field(
        position=10,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class RXA(HL7Segment):
    _segment_id = "RXA"

    give_sub_id_counter: NM = HL7Field(
        position=1,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    administration_sub_id_counter: NM = HL7Field(
        position=2,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    date_time_start_of_administration: DTM = HL7Field(
        position=3,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    date_time_end_of_administration: DTM = HL7Field(
        position=4,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    administered_code: CWE = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70292",
    )
    administered_amount: NM = HL7Field(
        position=6,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    administered_units: Optional[CWE] = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70689",
    )
    administered_dosage_form: Optional[CWE] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70690",
    )
    administration_notes: Optional[list[CWE]] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70691",
    )
    administering_provider: Optional[list[XCN]] = HL7Field(
        position=10,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    administered_per_time_unit: Optional[ST] = HL7Field(
        position=12,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    administered_strength: Optional[NM] = HL7Field(
        position=13,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    administered_strength_units: Optional[CWE] = HL7Field(
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70692",
    )
    substance_lot_number: Optional[list[ST]] = HL7Field(
        position=15,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    substance_expiration_date: Optional[list[DTM]] = HL7Field(
        position=16,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    substance_manufacturer_name: Optional[list[CWE]] = HL7Field(
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    substance_treatment_refusal_reason: Optional[list[CWE]] = HL7Field(
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70693",
    )
    indication: Optional[list[CWE]] = HL7Field(
        position=19,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70694",
    )
    completion_status: Optional[ID] = HL7Field(
        position=20,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70322",
    )
    action_code_rxa: Optional[ID] = HL7Field(
        position=21,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70206",
    )
    system_entry_date_time: Optional[DTM] = HL7Field(
        position=22,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    administered_drug_strength_volume: Optional[NM] = HL7Field(
        position=23,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    administered_drug_strength_volume_units: Optional[CWE] = HL7Field(
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70695",
    )
    administered_barcode_identifier: Optional[CWE] = HL7Field(
        position=25,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70696",
    )
    pharmacy_order_type: Optional[ID] = HL7Field(
        position=26,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70480",
    )
    administer_at: Optional[PL] = HL7Field(
        position=27,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    administered_at_address: Optional[XAD] = HL7Field(
        position=28,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    administered_tag_identifier: Optional[list[EI]] = HL7Field(
        position=29,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )


class RXC(HL7Segment):
    _segment_id = "RXC"

    rx_component_type: ID = HL7Field(
        position=1,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70166",
    )
    component_code: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70697",
    )
    component_amount: NM = HL7Field(
        position=3,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    component_units: CWE = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70698",
    )
    component_strength: Optional[NM] = HL7Field(
        position=5,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    component_strength_units: Optional[CWE] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70699",
    )
    supplementary_code: Optional[list[CWE]] = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70700",
    )
    component_drug_strength_volume: Optional[NM] = HL7Field(
        position=8,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    component_drug_strength_volume_units: Optional[CWE] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70701",
    )
    dispense_amount: Optional[NM] = HL7Field(
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    dispense_units: Optional[CWE] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70703",
    )


class RXD(HL7Segment):
    _segment_id = "RXD"

    dispense_sub_id_counter: NM = HL7Field(
        position=1,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    dispense_give_code: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70292",
    )
    date_time_dispensed: DTM = HL7Field(
        position=3,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    actual_dispense_amount: NM = HL7Field(
        position=4,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    actual_dispense_units: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70704",
    )
    actual_dosage_form: Optional[CWE] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70705",
    )
    prescription_number: ST = HL7Field(
        position=7,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    number_of_refills_remaining: Optional[NM] = HL7Field(
        position=8,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    dispense_notes: Optional[list[ST]] = HL7Field(
        position=9,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    dispensing_provider: Optional[list[XCN]] = HL7Field(
        position=10,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    substitution_status: Optional[ID] = HL7Field(
        position=11,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70167",
    )
    total_daily_dose: Optional[CQ] = HL7Field(
        position=12,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    needs_human_review: Optional[ID] = HL7Field(
        position=14,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    special_dispensing_instructions: Optional[list[CWE]] = HL7Field(
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70706",
    )
    actual_strength: Optional[NM] = HL7Field(
        position=16,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    actual_strength_unit: Optional[CWE] = HL7Field(
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70707",
    )
    substance_lot_number: Optional[list[ST]] = HL7Field(
        position=18,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    substance_expiration_date: Optional[list[DTM]] = HL7Field(
        position=19,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    substance_manufacturer_name: Optional[list[CWE]] = HL7Field(
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    indication: Optional[list[CWE]] = HL7Field(
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70694",
    )
    dispense_package_size: Optional[NM] = HL7Field(
        position=22,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    dispense_package_size_unit: Optional[CWE] = HL7Field(
        position=23,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70709",
    )
    dispense_package_method: Optional[ID] = HL7Field(
        position=24,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70321",
    )
    supplementary_code: Optional[list[CWE]] = HL7Field(
        position=25,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70700",
    )
    initiating_location: Optional[CWE] = HL7Field(
        position=26,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70711",
    )
    packaging_assembly_location: Optional[CWE] = HL7Field(
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70712",
    )
    actual_drug_strength_volume: Optional[NM] = HL7Field(
        position=28,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    actual_drug_strength_volume_units: Optional[CWE] = HL7Field(
        position=29,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70713",
    )
    dispense_to_pharmacy: Optional[CWE] = HL7Field(
        position=30,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70714",
    )
    dispense_to_pharmacy_address: Optional[XAD] = HL7Field(
        position=31,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    pharmacy_order_type: Optional[ID] = HL7Field(
        position=32,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70480",
    )
    dispense_type: Optional[CWE] = HL7Field(
        position=33,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70484",
    )
    pharmacy_phone_number: Optional[list[XTN]] = HL7Field(
        position=34,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    dispense_tag_identifier: Optional[list[EI]] = HL7Field(
        position=35,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )


class RXE(HL7Segment):
    _segment_id = "RXE"

    give_code: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70292",
    )
    give_amount_minimum: NM = HL7Field(
        position=3,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    give_amount_maximum: Optional[NM] = HL7Field(
        position=4,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    give_units: CWE = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70715",
    )
    give_dosage_form: Optional[CWE] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70716",
    )
    providers_administration_instructions: Optional[list[CWE]] = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70718",
    )
    substitution_status: Optional[ID] = HL7Field(
        position=9,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70167",
    )
    dispense_amount: Optional[NM] = HL7Field(
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    dispense_units: Optional[CWE] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70720",
    )
    number_of_refills: Optional[NM] = HL7Field(
        position=12,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    ordering_providers_dea_number: Optional[list[XCN]] = HL7Field(
        position=13,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    pharmacist_treatment_suppliers_verifier_id: Optional[list[XCN]] = HL7Field(
        position=14,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    prescription_number: Optional[ST] = HL7Field(
        position=15,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    number_of_refills_remaining: Optional[NM] = HL7Field(
        position=16,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    number_of_refills_doses_dispensed: Optional[NM] = HL7Field(
        position=17,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    dt_of_most_recent_refill_or_dose_dispensed: Optional[DTM] = HL7Field(
        position=18,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    total_daily_dose: Optional[CQ] = HL7Field(
        position=19,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    needs_human_review: Optional[ID] = HL7Field(
        position=20,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    special_dispensing_instructions: Optional[list[CWE]] = HL7Field(
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70706",
    )
    give_per_time_unit: Optional[ST] = HL7Field(
        position=22,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    give_rate_amount: Optional[ST] = HL7Field(
        position=23,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    give_rate_units: Optional[CWE] = HL7Field(
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70722",
    )
    give_strength: Optional[NM] = HL7Field(
        position=25,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    give_strength_units: Optional[CWE] = HL7Field(
        position=26,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70723",
    )
    give_indication: Optional[list[CWE]] = HL7Field(
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70724",
    )
    dispense_package_size: Optional[NM] = HL7Field(
        position=28,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    dispense_package_size_unit: Optional[CWE] = HL7Field(
        position=29,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70709",
    )
    dispense_package_method: Optional[ID] = HL7Field(
        position=30,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70321",
    )
    supplementary_code: Optional[list[CWE]] = HL7Field(
        position=31,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70700",
    )
    original_order_date_time: Optional[DTM] = HL7Field(
        position=32,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    give_drug_strength_volume: Optional[NM] = HL7Field(
        position=33,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    give_drug_strength_volume_units: Optional[CWE] = HL7Field(
        position=34,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70729",
    )
    controlled_substance_schedule: Optional[CWE] = HL7Field(
        position=35,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70477",
    )
    formulary_status: Optional[ID] = HL7Field(
        position=36,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70478",
    )
    pharmaceutical_substance_alternative: Optional[list[CWE]] = HL7Field(
        position=37,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70730",
    )
    pharmacy_of_most_recent_fill: Optional[CWE] = HL7Field(
        position=38,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70732",
    )
    initial_dispense_amount: Optional[NM] = HL7Field(
        position=39,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    dispensing_pharmacy: Optional[CWE] = HL7Field(
        position=40,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70733",
    )
    dispensing_pharmacy_address: Optional[XAD] = HL7Field(
        position=41,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    deliver_to_patient_location: Optional[PL] = HL7Field(
        position=42,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    deliver_to_address: Optional[XAD] = HL7Field(
        position=43,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    pharmacy_order_type: Optional[ID] = HL7Field(
        position=44,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70480",
    )
    pharmacy_phone_number: Optional[list[XTN]] = HL7Field(
        position=45,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )


class RXG(HL7Segment):
    _segment_id = "RXG"

    give_sub_id_counter: NM = HL7Field(
        position=1,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    dispense_sub_id_counter: Optional[NM] = HL7Field(
        position=2,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    give_code: CWE = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70292",
    )
    give_amount_minimum: NM = HL7Field(
        position=5,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    give_amount_maximum: Optional[NM] = HL7Field(
        position=6,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    give_units: CWE = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70715",
    )
    give_dosage_form: Optional[CWE] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70716",
    )
    administration_notes: Optional[list[CWE]] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70691",
    )
    substitution_status: Optional[ID] = HL7Field(
        position=10,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70167",
    )
    needs_human_review: Optional[ID] = HL7Field(
        position=12,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    special_administration_instructions: Optional[list[CWE]] = HL7Field(
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70738",
    )
    give_per_time_unit: Optional[ST] = HL7Field(
        position=14,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    give_rate_amount: Optional[ST] = HL7Field(
        position=15,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    give_rate_units: Optional[CWE] = HL7Field(
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70722",
    )
    give_strength: Optional[NM] = HL7Field(
        position=17,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    give_strength_units: Optional[CWE] = HL7Field(
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70723",
    )
    substance_lot_number: Optional[list[ST]] = HL7Field(
        position=19,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    substance_expiration_date: Optional[list[DTM]] = HL7Field(
        position=20,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    substance_manufacturer_name: Optional[list[CWE]] = HL7Field(
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    indication: Optional[list[CWE]] = HL7Field(
        position=22,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70694",
    )
    give_drug_strength_volume: Optional[NM] = HL7Field(
        position=23,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    give_drug_strength_volume_units: Optional[CWE] = HL7Field(
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70744",
    )
    give_barcode_identifier: Optional[CWE] = HL7Field(
        position=25,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70745",
    )
    pharmacy_order_type: Optional[ID] = HL7Field(
        position=26,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70480",
    )
    deliver_to_patient_location: Optional[PL] = HL7Field(
        position=29,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    deliver_to_address: Optional[XAD] = HL7Field(
        position=30,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    give_tag_identifier: Optional[list[EI]] = HL7Field(
        position=31,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    dispense_amount: Optional[NM] = HL7Field(
        position=32,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    dispense_units: Optional[CWE] = HL7Field(
        position=33,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70746",
    )


class RXO(HL7Segment):
    _segment_id = "RXO"

    requested_give_code: Optional[CWE] = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70747",
    )
    requested_give_amount_minimum: Optional[NM] = HL7Field(
        position=2,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    requested_give_amount_maximum: Optional[NM] = HL7Field(
        position=3,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    requested_give_units: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70748",
    )
    requested_dosage_form: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70750",
    )
    providers_pharmacy_treatment_instructions: Optional[list[CWE]] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70751",
    )
    providers_administration_instructions: Optional[list[CWE]] = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70718",
    )
    allow_substitutions: Optional[ID] = HL7Field(
        position=9,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70161",
    )
    requested_dispense_code: Optional[CWE] = HL7Field(
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70753",
    )
    requested_dispense_amount: Optional[NM] = HL7Field(
        position=11,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    requested_dispense_units: Optional[CWE] = HL7Field(
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70754",
    )
    number_of_refills: Optional[NM] = HL7Field(
        position=13,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    pharmacist_treatment_suppliers_verifier_id: Optional[list[XCN]] = HL7Field(
        position=15,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    needs_human_review: Optional[ID] = HL7Field(
        position=16,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    requested_give_per_time_unit: Optional[ST] = HL7Field(
        position=17,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    requested_give_strength: Optional[NM] = HL7Field(
        position=18,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    requested_give_strength_units: Optional[CWE] = HL7Field(
        position=19,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70756",
    )
    indication: Optional[list[CWE]] = HL7Field(
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70694",
    )
    requested_give_rate_amount: Optional[ST] = HL7Field(
        position=21,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    requested_give_rate_units: Optional[CWE] = HL7Field(
        position=22,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70760",
    )
    total_daily_dose: Optional[CQ] = HL7Field(
        position=23,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    supplementary_code: Optional[list[CWE]] = HL7Field(
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70700",
    )
    requested_drug_strength_volume: Optional[NM] = HL7Field(
        position=25,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    requested_drug_strength_volume_units: Optional[CWE] = HL7Field(
        position=26,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70764",
    )
    pharmacy_order_type: Optional[ID] = HL7Field(
        position=27,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70480",
    )
    dispensing_interval: Optional[NM] = HL7Field(
        position=28,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    medication_instance_identifier: Optional[EI] = HL7Field(
        position=29,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    segment_instance_identifier: Optional[EI] = HL7Field(
        position=30,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    mood_code: Optional[CNE] = HL7Field(
        position=31,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70725",
    )
    dispensing_pharmacy: Optional[CWE] = HL7Field(
        position=32,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70733",
    )
    dispensing_pharmacy_address: Optional[XAD] = HL7Field(
        position=33,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    deliver_to_patient_location: Optional[PL] = HL7Field(
        position=34,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    deliver_to_address: Optional[XAD] = HL7Field(
        position=35,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    pharmacy_phone_number: Optional[list[XTN]] = HL7Field(
        position=36,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )


class RXR(HL7Segment):
    _segment_id = "RXR"

    route: CWE = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70162",
    )
    administration_site: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70550",
    )
    administration_device: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70164",
    )
    administration_method: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70165",
    )
    routing_instruction: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70766",
    )
    administration_site_modifier: Optional[CWE] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70495",
    )


class RXV(HL7Segment):
    _segment_id = "RXV"

    set_id_rxv: Optional[SI] = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bolus_type: ID = HL7Field(
        position=2,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70917",
    )
    bolus_dose_amount: Optional[NM] = HL7Field(
        position=3,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bolus_dose_amount_units: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70767",
    )
    bolus_dose_volume: Optional[NM] = HL7Field(
        position=5,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bolus_dose_volume_units: Optional[CWE] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70768",
    )
    pca_type: ID = HL7Field(
        position=7,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70918",
    )
    pca_dose_amount: Optional[NM] = HL7Field(
        position=8,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    pca_dose_amount_units: Optional[CWE] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70769",
    )
    pca_dose_amount_volume: Optional[NM] = HL7Field(
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    pca_dose_amount_volume_units: Optional[CWE] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70770",
    )
    max_dose_amount: Optional[NM] = HL7Field(
        position=12,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    max_dose_amount_units: Optional[CWE] = HL7Field(
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70772",
    )
    max_dose_amount_volume: Optional[NM] = HL7Field(
        position=14,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    max_dose_amount_volume_units: Optional[CWE] = HL7Field(
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70773",
    )
    max_dose_per_time: CQ = HL7Field(
        position=16,
        datatype="CQ",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    lockout_interval: Optional[CQ] = HL7Field(
        position=17,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    syringe_manufacturer: Optional[CWE] = HL7Field(
        position=18,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    syringe_model_number: Optional[CWE] = HL7Field(
        position=19,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    syringe_size: Optional[NM] = HL7Field(
        position=20,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    syringe_size_units: Optional[CWE] = HL7Field(
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    action_code: Optional[ID] = HL7Field(
        position=22,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class SAC(HL7Segment):
    _segment_id = "SAC"

    external_accession_identifier: Optional[EI] = HL7Field(
        position=1,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    accession_identifier: Optional[EI] = HL7Field(
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    container_identifier: Optional[EI] = HL7Field(
        position=3,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    primary_parent_container_identifier: Optional[EI] = HL7Field(
        position=4,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    equipment_container_identifier: Optional[EI] = HL7Field(
        position=5,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    registration_date_time: Optional[DTM] = HL7Field(
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    container_status: Optional[CWE] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70370",
    )
    carrier_type: Optional[CWE] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70378",
    )
    carrier_identifier: Optional[EI] = HL7Field(
        position=10,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    position_in_carrier: Optional[NA] = HL7Field(
        position=11,
        datatype="NA",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    tray_type_sac: Optional[CWE] = HL7Field(
        position=12,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70379",
    )
    tray_identifier: Optional[EI] = HL7Field(
        position=13,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    position_in_tray: Optional[NA] = HL7Field(
        position=14,
        datatype="NA",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    location: Optional[list[CWE]] = HL7Field(
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70774",
    )
    container_height: Optional[NM] = HL7Field(
        position=16,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    container_diameter: Optional[NM] = HL7Field(
        position=17,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    barrier_delta: Optional[NM] = HL7Field(
        position=18,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bottom_delta: Optional[NM] = HL7Field(
        position=19,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    container_height_diameter_delta_units: Optional[CWE] = HL7Field(
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70775",
    )
    container_volume: Optional[NM] = HL7Field(
        position=21,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    available_specimen_volume: Optional[NM] = HL7Field(
        position=22,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    initial_specimen_volume: Optional[NM] = HL7Field(
        position=23,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    volume_units: Optional[CWE] = HL7Field(
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70777",
    )
    separator_type: Optional[CWE] = HL7Field(
        position=25,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70380",
    )
    cap_type: Optional[CWE] = HL7Field(
        position=26,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70381",
    )
    additive: Optional[list[CWE]] = HL7Field(
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70371",
    )
    specimen_component: Optional[CWE] = HL7Field(
        position=28,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70372",
    )
    dilution_factor: Optional[SN] = HL7Field(
        position=29,
        datatype="SN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    treatment: Optional[CWE] = HL7Field(
        position=30,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70373",
    )
    temperature: Optional[SN] = HL7Field(
        position=31,
        datatype="SN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    hemolysis_index: Optional[NM] = HL7Field(
        position=32,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    hemolysis_index_units: Optional[CWE] = HL7Field(
        position=33,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70779",
    )
    lipemia_index: Optional[NM] = HL7Field(
        position=34,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    lipemia_index_units: Optional[CWE] = HL7Field(
        position=35,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70780",
    )
    icterus_index: Optional[NM] = HL7Field(
        position=36,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    icterus_index_units: Optional[CWE] = HL7Field(
        position=37,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70781",
    )
    fibrin_index: Optional[NM] = HL7Field(
        position=38,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    fibrin_index_units: Optional[CWE] = HL7Field(
        position=39,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70782",
    )
    system_induced_contaminants: Optional[list[CWE]] = HL7Field(
        position=40,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70374",
    )
    drug_interference: Optional[list[CWE]] = HL7Field(
        position=41,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70382",
    )
    artificial_blood: Optional[CWE] = HL7Field(
        position=42,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70375",
    )
    special_handling_code: Optional[list[CWE]] = HL7Field(
        position=43,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70376",
    )
    other_environmental_factors: Optional[list[CWE]] = HL7Field(
        position=44,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70377",
    )
    container_length: Optional[CQ] = HL7Field(
        position=45,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    container_width: Optional[CQ] = HL7Field(
        position=46,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    container_form: Optional[CWE] = HL7Field(
        position=47,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70967",
    )
    container_material: Optional[CWE] = HL7Field(
        position=48,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70968",
    )
    container_common_name: Optional[CWE] = HL7Field(
        position=49,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70969",
    )


class SCD(HL7Segment):
    _segment_id = "SCD"

    cycle_start_time: Optional[TM] = HL7Field(
        position=1,
        datatype="TM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    cycle_count: Optional[NM] = HL7Field(
        position=2,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    temp_max: Optional[CQ] = HL7Field(
        position=3,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    temp_min: Optional[CQ] = HL7Field(
        position=4,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    load_number: Optional[NM] = HL7Field(
        position=5,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    condition_time: Optional[CQ] = HL7Field(
        position=6,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    sterilize_time: Optional[CQ] = HL7Field(
        position=7,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    exhaust_time: Optional[CQ] = HL7Field(
        position=8,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    total_cycle_time: Optional[CQ] = HL7Field(
        position=9,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    device_status: Optional[CWE] = HL7Field(
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70682",
    )
    cycle_start_date_time: Optional[DTM] = HL7Field(
        position=11,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    dry_time: Optional[CQ] = HL7Field(
        position=12,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    leak_rate: Optional[CQ] = HL7Field(
        position=13,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    control_temperature: Optional[CQ] = HL7Field(
        position=14,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    sterilizer_temperature: Optional[CQ] = HL7Field(
        position=15,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    cycle_complete_time: Optional[TM] = HL7Field(
        position=16,
        datatype="TM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    under_temperature: Optional[CQ] = HL7Field(
        position=17,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    over_temperature: Optional[CQ] = HL7Field(
        position=18,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    abort_cycle: Optional[CNE] = HL7Field(
        position=19,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    alarm: Optional[CNE] = HL7Field(
        position=20,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    long_in_charge_phase: Optional[CNE] = HL7Field(
        position=21,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    long_in_exhaust_phase: Optional[CNE] = HL7Field(
        position=22,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    long_in_fast_exhaust_phase: Optional[CNE] = HL7Field(
        position=23,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    reset: Optional[CNE] = HL7Field(
        position=24,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    operator_unload: Optional[XCN] = HL7Field(
        position=25,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    door_open: Optional[CNE] = HL7Field(
        position=26,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    reading_failure: Optional[CNE] = HL7Field(
        position=27,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    cycle_type: Optional[CWE] = HL7Field(
        position=28,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70702",
    )
    thermal_rinse_time: Optional[CQ] = HL7Field(
        position=29,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    wash_time: Optional[CQ] = HL7Field(
        position=30,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    injection_rate: Optional[CQ] = HL7Field(
        position=31,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    procedure_code: Optional[CNE] = HL7Field(
        position=32,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70088",
    )
    patient_identifier_list: Optional[list[CX]] = HL7Field(
        position=33,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    attending_doctor: Optional[XCN] = HL7Field(
        position=34,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70010",
    )
    dilution_factor: Optional[SN] = HL7Field(
        position=35,
        datatype="SN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    fill_time: Optional[CQ] = HL7Field(
        position=36,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inlet_temperature: Optional[CQ] = HL7Field(
        position=37,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class SCH(HL7Segment):
    _segment_id = "SCH"

    placer_appointment_id: Optional[EI] = HL7Field(
        position=1,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    filler_appointment_id: Optional[EI] = HL7Field(
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    occurrence_number: Optional[NM] = HL7Field(
        position=3,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    placer_order_group_number: Optional[EI] = HL7Field(
        position=4,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    schedule_id: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    event_reason: CWE = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    appointment_reason: Optional[CWE] = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70276",
    )
    appointment_type: Optional[CWE] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70277",
    )
    appointment_duration_units: Optional[CNE] = HL7Field(
        position=10,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    placer_contact_person: Optional[list[XCN]] = HL7Field(
        position=12,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    placer_contact_phone_number: Optional[XTN] = HL7Field(
        position=13,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    placer_contact_address: Optional[list[XAD]] = HL7Field(
        position=14,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    placer_contact_location: Optional[PL] = HL7Field(
        position=15,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    filler_contact_person: list[XCN] = HL7Field(
        position=16,
        datatype="XCN",
        usage=Usage.REQUIRED,
        repeatable=True,
    )
    filler_contact_phone_number: Optional[XTN] = HL7Field(
        position=17,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    filler_contact_address: Optional[list[XAD]] = HL7Field(
        position=18,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    filler_contact_location: Optional[PL] = HL7Field(
        position=19,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    entered_by_person: list[XCN] = HL7Field(
        position=20,
        datatype="XCN",
        usage=Usage.REQUIRED,
        repeatable=True,
    )
    entered_by_phone_number: Optional[list[XTN]] = HL7Field(
        position=21,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    entered_by_location: Optional[PL] = HL7Field(
        position=22,
        datatype="PL",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    parent_placer_appointment_id: Optional[EI] = HL7Field(
        position=23,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    parent_filler_appointment_id: Optional[EI] = HL7Field(
        position=24,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    filler_status_code: Optional[CWE] = HL7Field(
        position=25,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70278",
    )
    placer_order_number: Optional[list[EI]] = HL7Field(
        position=26,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    filler_order_number: Optional[list[EI]] = HL7Field(
        position=27,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    alternate_placer_order_group_number: Optional[EIP] = HL7Field(
        position=28,
        datatype="EIP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class SCP(HL7Segment):
    _segment_id = "SCP"

    number_of_decontamination_sterilization_devices: Optional[NM] = HL7Field(
        position=1,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    labor_calculation_type: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70651",
    )
    date_format: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70653",
    )
    device_number: Optional[EI] = HL7Field(
        position=4,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    device_name: Optional[ST] = HL7Field(
        position=5,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    device_model_name: Optional[ST] = HL7Field(
        position=6,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    device_type: Optional[CWE] = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70657",
    )
    lot_control: Optional[CWE] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70659",
    )


class SDD(HL7Segment):
    _segment_id = "SDD"

    lot_number: Optional[EI] = HL7Field(
        position=1,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    device_number: Optional[EI] = HL7Field(
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    device_name: Optional[ST] = HL7Field(
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    device_data_state: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70667",
    )
    load_status: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70669",
    )
    control_code: Optional[NM] = HL7Field(
        position=6,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    operator_name: Optional[ST] = HL7Field(
        position=7,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class SFT(HL7Segment):
    _segment_id = "SFT"

    software_vendor_organization: XON = HL7Field(
        position=1,
        datatype="XON",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    software_certified_version_or_release_number: ST = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    software_product_name: ST = HL7Field(
        position=3,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    software_binary_id: ST = HL7Field(
        position=4,
        datatype="ST",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    software_product_information: Optional[TX] = HL7Field(
        position=5,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    software_install_date: Optional[DTM] = HL7Field(
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class SGH(HL7Segment):
    _segment_id = "SGH"

    set_id_sgh: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    segment_group_name: Optional[ST] = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class SGT(HL7Segment):
    _segment_id = "SGT"

    set_id_sgt: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    segment_group_name: Optional[ST] = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class SHP(HL7Segment):
    _segment_id = "SHP"

    shipment_id: EI = HL7Field(
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    internal_shipment_id: Optional[list[EI]] = HL7Field(
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    shipment_status: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70905",
    )
    shipment_status_date_time: DTM = HL7Field(
        position=4,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    shipment_status_reason: Optional[TX] = HL7Field(
        position=5,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    shipment_priority: Optional[CWE] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70906",
    )
    shipment_confidentiality: Optional[list[CWE]] = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70907",
    )
    number_of_packages_in_shipment: Optional[NM] = HL7Field(
        position=8,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    shipment_condition: Optional[list[CWE]] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70544",
    )
    shipment_handling_code: Optional[list[CWE]] = HL7Field(
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70376",
    )
    shipment_risk_code: Optional[list[CWE]] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70489",
    )
    action_code: Optional[ID] = HL7Field(
        position=12,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class SID(HL7Segment):
    _segment_id = "SID"

    application_method_identifier: Optional[CWE] = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70783",
    )
    substance_lot_number: Optional[ST] = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    substance_container_identifier: Optional[ST] = HL7Field(
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    substance_manufacturer_identifier: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70385",
    )


class SLT(HL7Segment):
    _segment_id = "SLT"

    device_number: Optional[EI] = HL7Field(
        position=1,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    device_name: Optional[ST] = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    lot_number: Optional[EI] = HL7Field(
        position=3,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    item_identifier: Optional[EI] = HL7Field(
        position=4,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    bar_code: Optional[ST] = HL7Field(
        position=5,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class SPM(HL7Segment):
    _segment_id = "SPM"

    set_id_spm: Optional[SI] = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    specimen_identifier: Optional[EIP] = HL7Field(
        position=2,
        datatype="EIP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    specimen_parent_i_ds: Optional[list[EIP]] = HL7Field(
        position=3,
        datatype="EIP",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    specimen_type: CWE = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70487",
    )
    specimen_type_modifier: Optional[list[CWE]] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70541",
    )
    specimen_additives: Optional[list[CWE]] = HL7Field(
        position=6,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70371",
    )
    specimen_collection_method: Optional[CWE] = HL7Field(
        position=7,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70488",
    )
    specimen_source_site: Optional[CWE] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70784",
    )
    specimen_source_site_modifier: Optional[list[CWE]] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70542",
    )
    specimen_collection_site: Optional[CWE] = HL7Field(
        position=10,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70543",
    )
    specimen_role: Optional[list[CWE]] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70369",
    )
    specimen_collection_amount: Optional[CQ] = HL7Field(
        position=12,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    grouped_specimen_count: Optional[NM] = HL7Field(
        position=13,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    specimen_description: Optional[list[ST]] = HL7Field(
        position=14,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    specimen_handling_code: Optional[list[CWE]] = HL7Field(
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70376",
    )
    specimen_risk_code: Optional[list[CWE]] = HL7Field(
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70489",
    )
    specimen_collection_date_time: Optional[DR] = HL7Field(
        position=17,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    specimen_received_date_time: Optional[DTM] = HL7Field(
        position=18,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    specimen_expiration_date_time: Optional[DTM] = HL7Field(
        position=19,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    specimen_availability: Optional[ID] = HL7Field(
        position=20,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    specimen_reject_reason: Optional[list[CWE]] = HL7Field(
        position=21,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70490",
    )
    specimen_quality: Optional[CWE] = HL7Field(
        position=22,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70491",
    )
    specimen_appropriateness: Optional[CWE] = HL7Field(
        position=23,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70492",
    )
    specimen_condition: Optional[list[CWE]] = HL7Field(
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70493",
    )
    specimen_current_quantity: Optional[CQ] = HL7Field(
        position=25,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    number_of_specimen_containers: Optional[NM] = HL7Field(
        position=26,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    container_type: Optional[CWE] = HL7Field(
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70785",
    )
    container_condition: Optional[CWE] = HL7Field(
        position=28,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70544",
    )
    specimen_child_role: Optional[CWE] = HL7Field(
        position=29,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70494",
    )
    accession_id: Optional[list[CX]] = HL7Field(
        position=30,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    other_specimen_id: Optional[list[CX]] = HL7Field(
        position=31,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    shipment_id: Optional[EI] = HL7Field(
        position=32,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    culture_start_date_time: Optional[DTM] = HL7Field(
        position=33,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    culture_final_date_time: Optional[DTM] = HL7Field(
        position=34,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    action_code: Optional[ID] = HL7Field(
        position=35,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class STF(HL7Segment):
    _segment_id = "STF"

    primary_key_value_stf: Optional[CWE] = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70786",
    )
    staff_identifier_list: Optional[list[CX]] = HL7Field(
        position=2,
        datatype="CX",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70061",
    )
    staff_name: Optional[list[XPN]] = HL7Field(
        position=3,
        datatype="XPN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    staff_type: Optional[list[CWE]] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70182",
    )
    administrative_sex: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70001",
    )
    date_time_of_birth: Optional[DTM] = HL7Field(
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    active_inactive_flag: Optional[ID] = HL7Field(
        position=7,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70183",
    )
    department: Optional[list[CWE]] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70184",
    )
    hospital_service_stf: Optional[list[CWE]] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70069",
    )
    phone: Optional[list[XTN]] = HL7Field(
        position=10,
        datatype="XTN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    office_home_address_birthplace: Optional[list[XAD]] = HL7Field(
        position=11,
        datatype="XAD",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    institution_activation_date: Optional[list[DIN]] = HL7Field(
        position=12,
        datatype="DIN",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70537",
    )
    institution_inactivation_date: Optional[list[DIN]] = HL7Field(
        position=13,
        datatype="DIN",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70537",
    )
    backup_person_id: Optional[list[CWE]] = HL7Field(
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    e_mail_address: Optional[list[ST]] = HL7Field(
        position=15,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    preferred_method_of_contact: Optional[CWE] = HL7Field(
        position=16,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70185",
    )
    marital_status: Optional[CWE] = HL7Field(
        position=17,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70002",
    )
    job_title: Optional[ST] = HL7Field(
        position=18,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    job_code_class: Optional[JCC] = HL7Field(
        position=19,
        datatype="JCC",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    employment_status_code: Optional[CWE] = HL7Field(
        position=20,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70066",
    )
    additional_insured_on_auto: Optional[ID] = HL7Field(
        position=21,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    drivers_license_number_staff: Optional[DLN] = HL7Field(
        position=22,
        datatype="DLN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    copy_auto_ins: Optional[ID] = HL7Field(
        position=23,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    auto_ins_expires: Optional[DT] = HL7Field(
        position=24,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    date_last_dmv_review: Optional[DT] = HL7Field(
        position=25,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    date_next_dmv_review: Optional[DT] = HL7Field(
        position=26,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    race: Optional[CWE] = HL7Field(
        position=27,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70005",
    )
    ethnic_group: Optional[CWE] = HL7Field(
        position=28,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70189",
    )
    re_activation_approval_indicator: Optional[ID] = HL7Field(
        position=29,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    citizenship: Optional[list[CWE]] = HL7Field(
        position=30,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70171",
    )
    date_time_of_death: Optional[DTM] = HL7Field(
        position=31,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    death_indicator: Optional[ID] = HL7Field(
        position=32,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    institution_relationship_type_code: Optional[CWE] = HL7Field(
        position=33,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70538",
    )
    institution_relationship_period: Optional[DR] = HL7Field(
        position=34,
        datatype="DR",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    expected_return_date: Optional[DT] = HL7Field(
        position=35,
        datatype="DT",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    cost_center_code: Optional[list[CWE]] = HL7Field(
        position=36,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70539",
    )
    generic_classification_indicator: Optional[ID] = HL7Field(
        position=37,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    inactive_reason_code: Optional[CWE] = HL7Field(
        position=38,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70540",
    )
    generic_resource_type_or_category: Optional[list[CWE]] = HL7Field(
        position=39,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70771",
    )
    religion: Optional[CWE] = HL7Field(
        position=40,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70006",
    )
    signature: Optional[ED] = HL7Field(
        position=41,
        datatype="ED",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class STZ(HL7Segment):
    _segment_id = "STZ"

    sterilization_type: Optional[CWE] = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70806",
    )
    sterilization_cycle: Optional[CWE] = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70702",
    )
    maintenance_cycle: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70809",
    )
    maintenance_type: Optional[CWE] = HL7Field(
        position=4,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70811",
    )


class TCC(HL7Segment):
    _segment_id = "TCC"

    universal_service_identifier: CWE = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    equipment_test_application_identifier: EI = HL7Field(
        position=2,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    auto_dilution_factor_default: Optional[SN] = HL7Field(
        position=4,
        datatype="SN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    rerun_dilution_factor_default: Optional[SN] = HL7Field(
        position=5,
        datatype="SN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    pre_dilution_factor_default: Optional[SN] = HL7Field(
        position=6,
        datatype="SN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    endogenous_content_of_pre_dilution_diluent: Optional[SN] = HL7Field(
        position=7,
        datatype="SN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    inventory_limits_warning_level: Optional[NM] = HL7Field(
        position=8,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    automatic_rerun_allowed: Optional[ID] = HL7Field(
        position=9,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    automatic_repeat_allowed: Optional[ID] = HL7Field(
        position=10,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    automatic_reflex_allowed: Optional[ID] = HL7Field(
        position=11,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    equipment_dynamic_range: Optional[SN] = HL7Field(
        position=12,
        datatype="SN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    units: Optional[CWE] = HL7Field(
        position=13,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70623",
    )
    processing_type: Optional[CWE] = HL7Field(
        position=14,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70388",
    )
    test_criticality: Optional[CWE] = HL7Field(
        position=15,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class TCD(HL7Segment):
    _segment_id = "TCD"

    universal_service_identifier: CWE = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    auto_dilution_factor: Optional[SN] = HL7Field(
        position=2,
        datatype="SN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    rerun_dilution_factor: Optional[SN] = HL7Field(
        position=3,
        datatype="SN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    pre_dilution_factor: Optional[SN] = HL7Field(
        position=4,
        datatype="SN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    endogenous_content_of_pre_dilution_diluent: Optional[SN] = HL7Field(
        position=5,
        datatype="SN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    automatic_repeat_allowed: Optional[ID] = HL7Field(
        position=6,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    reflex_allowed: Optional[ID] = HL7Field(
        position=7,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70136",
    )
    analyte_repeat_status: Optional[CWE] = HL7Field(
        position=8,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70389",
    )
    specimen_consumption_quantity: Optional[CQ] = HL7Field(
        position=9,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    pool_size: Optional[NM] = HL7Field(
        position=10,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    auto_dilution_type: Optional[CWE] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70945",
    )


class TQ1(HL7Segment):
    _segment_id = "TQ1"

    set_id_tq1: Optional[SI] = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    quantity: Optional[CQ] = HL7Field(
        position=2,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    repeat_pattern: Optional[list[RPT]] = HL7Field(
        position=3,
        datatype="RPT",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    explicit_time: Optional[list[TM]] = HL7Field(
        position=4,
        datatype="TM",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    relative_time_and_units: Optional[list[CQ]] = HL7Field(
        position=5,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    service_duration: Optional[CQ] = HL7Field(
        position=6,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    start_datetime: Optional[DTM] = HL7Field(
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    end_datetime: Optional[DTM] = HL7Field(
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    priority: Optional[list[CWE]] = HL7Field(
        position=9,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70485",
    )
    condition_text: Optional[TX] = HL7Field(
        position=10,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    text_instruction: Optional[TX] = HL7Field(
        position=11,
        datatype="TX",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    conjunction: Optional[ID] = HL7Field(
        position=12,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70472",
    )
    occurrence_duration: Optional[CQ] = HL7Field(
        position=13,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    total_occurrences: Optional[NM] = HL7Field(
        position=14,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class TQ2(HL7Segment):
    _segment_id = "TQ2"

    set_id_tq2: Optional[SI] = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    sequence_results_flag: Optional[ID] = HL7Field(
        position=2,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70503",
    )
    related_placer_number: Optional[list[EI]] = HL7Field(
        position=3,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    related_filler_number: Optional[list[EI]] = HL7Field(
        position=4,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    related_placer_group_number: Optional[list[EI]] = HL7Field(
        position=5,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    sequence_condition_code: Optional[ID] = HL7Field(
        position=6,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70504",
    )
    cyclic_entry_exit_indicator: Optional[ID] = HL7Field(
        position=7,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70505",
    )
    sequence_condition_time_interval: Optional[CQ] = HL7Field(
        position=8,
        datatype="CQ",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    cyclic_group_maximum_number_of_repeats: Optional[NM] = HL7Field(
        position=9,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    special_service_request_relationship: Optional[ID] = HL7Field(
        position=10,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70506",
    )


class TXA(HL7Segment):
    _segment_id = "TXA"

    set_id_txa: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    document_type: CWE = HL7Field(
        position=2,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70270",
    )
    document_content_presentation: Optional[ID] = HL7Field(
        position=3,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70191",
    )
    activity_date_time: Optional[DTM] = HL7Field(
        position=4,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    primary_activity_provider_code_name: Optional[list[XCN]] = HL7Field(
        position=5,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    origination_date_time: Optional[DTM] = HL7Field(
        position=6,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    transcription_date_time: Optional[DTM] = HL7Field(
        position=7,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    edit_date_time: Optional[list[DTM]] = HL7Field(
        position=8,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    originator_code_name: Optional[list[XCN]] = HL7Field(
        position=9,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    assigned_document_authenticator: Optional[list[XCN]] = HL7Field(
        position=10,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    transcriptionist_code_name: Optional[list[XCN]] = HL7Field(
        position=11,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    unique_document_number: EI = HL7Field(
        position=12,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    parent_document_number: Optional[EI] = HL7Field(
        position=13,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    placer_order_number: Optional[list[EI]] = HL7Field(
        position=14,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    filler_order_number: Optional[EI] = HL7Field(
        position=15,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    unique_document_file_name: Optional[ST] = HL7Field(
        position=16,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    document_completion_status: ID = HL7Field(
        position=17,
        datatype="ID",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70271",
    )
    document_confidentiality_status: Optional[ID] = HL7Field(
        position=18,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70272",
    )
    document_availability_status: Optional[ID] = HL7Field(
        position=19,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70273",
    )
    document_storage_status: Optional[ID] = HL7Field(
        position=20,
        datatype="ID",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70275",
    )
    document_change_reason: Optional[ST] = HL7Field(
        position=21,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    authentication_person_time_stamp_set: Optional[list[PPN]] = HL7Field(
        position=22,
        datatype="PPN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    distributed_copies_code_and_name_of_recipients: Optional[list[XCN]] = HL7Field(
        position=23,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    folder_assignment: Optional[list[CWE]] = HL7Field(
        position=24,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=True,
        table="HL70791",
    )
    document_title: Optional[list[ST]] = HL7Field(
        position=25,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    agreed_due_date_time: Optional[DTM] = HL7Field(
        position=26,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    creating_facility: Optional[HD] = HL7Field(
        position=27,
        datatype="HD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    creating_specialty: Optional[CWE] = HL7Field(
        position=28,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70792",
    )


class UAC(HL7Segment):
    _segment_id = "UAC"

    user_authentication_credential_type_code: CWE = HL7Field(
        position=1,
        datatype="CWE",
        usage=Usage.REQUIRED,
        repeatable=False,
        table="HL70615",
    )
    user_authentication_credential: ED = HL7Field(
        position=2,
        datatype="ED",
        usage=Usage.REQUIRED,
        repeatable=False,
    )


class UB1(HL7Segment):
    _segment_id = "UB1"

    pass


class UB2(HL7Segment):
    _segment_id = "UB2"

    set_id_ub2: Optional[SI] = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    co_insurance_days_9: Optional[ST] = HL7Field(
        position=2,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    condition_code_24_30: Optional[CWE] = HL7Field(
        position=3,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70043",
    )
    covered_days_7: Optional[ST] = HL7Field(
        position=4,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    non_covered_days_8: Optional[ST] = HL7Field(
        position=5,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    value_amount_code_39_41: Optional[UVC] = HL7Field(
        position=6,
        datatype="UVC",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    occurrence_code_date_32_35: Optional[OCD] = HL7Field(
        position=7,
        datatype="OCD",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    occurrence_span_code_dates_36: Optional[OSP] = HL7Field(
        position=8,
        datatype="OSP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    uniform_billing_locator_2_state: Optional[ST] = HL7Field(
        position=9,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    uniform_billing_locator_11_state: Optional[ST] = HL7Field(
        position=10,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    uniform_billing_locator_31_national: Optional[ST] = HL7Field(
        position=11,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    document_control_number: Optional[ST] = HL7Field(
        position=12,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    uniform_billing_locator_49_national: Optional[ST] = HL7Field(
        position=13,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    uniform_billing_locator_56_state: Optional[ST] = HL7Field(
        position=14,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    uniform_billing_locator_57_sational: Optional[ST] = HL7Field(
        position=15,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    uniform_billing_locator_78_state: Optional[ST] = HL7Field(
        position=16,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    special_visit_count: Optional[NM] = HL7Field(
        position=17,
        datatype="NM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class URD(HL7Segment):
    _segment_id = "URD"

    pass


class URS(HL7Segment):
    _segment_id = "URS"

    pass


class VAR(HL7Segment):
    _segment_id = "VAR"

    variance_instance_id: EI = HL7Field(
        position=1,
        datatype="EI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    documented_date_time: DTM = HL7Field(
        position=2,
        datatype="DTM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    stated_variance_date_time: Optional[DTM] = HL7Field(
        position=3,
        datatype="DTM",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    variance_originator: Optional[list[XCN]] = HL7Field(
        position=4,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    variance_classification: Optional[CWE] = HL7Field(
        position=5,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    variance_description: Optional[list[ST]] = HL7Field(
        position=6,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )


class VND(HL7Segment):
    _segment_id = "VND"

    set_id_vnd: SI = HL7Field(
        position=1,
        datatype="SI",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    vendor_identifier: Optional[EI] = HL7Field(
        position=2,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    vendor_name: Optional[ST] = HL7Field(
        position=3,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    vendor_catalog_number: Optional[EI] = HL7Field(
        position=4,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    primary_vendor_indicator: Optional[CNE] = HL7Field(
        position=5,
        datatype="CNE",
        usage=Usage.OPTIONAL,
        repeatable=False,
        table="HL70532",
    )
    corporation: Optional[list[EI]] = HL7Field(
        position=6,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    primary_contact: Optional[XCN] = HL7Field(
        position=7,
        datatype="XCN",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    contract_adjustment: Optional[MOP] = HL7Field(
        position=8,
        datatype="MOP",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )
    associated_contract_id: Optional[list[EI]] = HL7Field(
        position=9,
        datatype="EI",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    class_of_trade: Optional[list[ST]] = HL7Field(
        position=10,
        datatype="ST",
        usage=Usage.OPTIONAL,
        repeatable=True,
    )
    pricing_tier_level: Optional[CWE] = HL7Field(
        position=11,
        datatype="CWE",
        usage=Usage.OPTIONAL,
        repeatable=False,
    )


class ZL7(HL7Segment):
    _segment_id = "ZL7"

    display_sort_key: NM = HL7Field(
        position=1,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )
    display_sort_key: NM = HL7Field(
        position=2,
        datatype="NM",
        usage=Usage.REQUIRED,
        repeatable=False,
    )


class Zxx(HL7Segment):
    _segment_id = "Zxx"

    pass
