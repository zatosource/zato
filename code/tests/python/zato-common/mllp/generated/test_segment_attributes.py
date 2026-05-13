from __future__ import annotations

import pytest

from zato.hl7v2.v2_9.segments import (
    ABS,
    ACC,
    ADD,
    ADJ,
    AFF,
    AIG,
    AIL,
    AIP,
    AIS,
    AL1,
    APR,
    ARQ,
    ARV,
    AUT,
    BHS,
    BLC,
    BLG,
    BPO,
    BPX,
    BTS,
    BTX,
    BUI,
    CDM,
    CDO,
    CER,
    CM0,
    CM1,
    CM2,
    CNS,
    CON,
    CSP,
    CSR,
    CSS,
    CTD,
    CTI,
    CTR,
    DB1,
    DEV,
    DG1,
    DMI,
    DON,
    DPS,
    DRG,
    DSC,
    DSP,
    DST,
    ECD,
    ECR,
    EDU,
    EQP,
    EQU,
    ERR,
    EVN,
    FAC,
    FHS,
    FT1,
    FTS,
    GOL,
    GP1,
    GP2,
    GT1,
    IAM,
    IAR,
    IIM,
    ILT,
    IN1,
    IN2,
    IN3,
    INV,
    IPC,
    IPR,
    ISD,
    ITM,
    IVC,
    IVT,
    LAN,
    LCC,
    LCH,
    LDP,
    LOC,
    LRL,
    MCP,
    MFA,
    MFE,
    MFI,
    MRG,
    MSA,
    MSH,
    NCK,
    NDS,
    NK1,
    NPU,
    NSC,
    NST,
    NTE,
    OBR,
    OBX,
    ODS,
    ODT,
    OH1,
    OH2,
    OH3,
    OH4,
    OM1,
    OM2,
    OM3,
    OM4,
    OM5,
    OM6,
    OM7,
    OMC,
    ORC,
    ORG,
    OVR,
    PAC,
    PCE,
    PCR,
    PD1,
    PDA,
    PDC,
    PEO,
    PES,
    PID,
    PKG,
    PM1,
    PMT,
    PR1,
    PRA,
    PRB,
    PRC,
    PRD,
    PRT,
    PSG,
    PSH,
    PSL,
    PSS,
    PTH,
    PV1,
    PV2,
    PYE,
    QAK,
    QID,
    QPD,
    QRI,
    RCP,
    RDF,
    RDT,
    REL,
    RF1,
    RFI,
    RGS,
    RMI,
    RQ1,
    RQD,
    RXA,
    RXC,
    RXD,
    RXE,
    RXG,
    RXO,
    RXR,
    RXV,
    SAC,
    SCD,
    SCH,
    SCP,
    SDD,
    SFT,
    SGH,
    SGT,
    SHP,
    SID,
    SLT,
    SPM,
    STF,
    STZ,
    TCC,
    TCD,
    TQ1,
    TQ2,
    TXA,
    UAC,
    UB2,
    VAR,
    VND,
    ZL7,
)


class TestSegmentAttributes:
    """Test that all segment attributes are accessible."""

    def test_abs_attributes(self):
        seg = ABS()
        _ = seg.discharge_care_provider
        _ = seg.transfer_medical_service_code
        _ = seg.severity_of_illness_code
        _ = seg.date_time_of_attestation
        _ = seg.attested_by
        _ = seg.triage_code
        _ = seg.abstract_completion_date_time
        _ = seg.abstracted_by
        _ = seg.case_category_code
        _ = seg.caesarian_section_indicator
        _ = seg.gestation_category_code
        _ = seg.gestation_period_weeks
        _ = seg.newborn_code
        _ = seg.stillborn_indicator

    def test_acc_attributes(self):
        seg = ACC()
        _ = seg.accident_date_time
        _ = seg.accident_code
        _ = seg.accident_location
        _ = seg.auto_accident_state
        _ = seg.accident_job_related_indicator
        _ = seg.accident_death_indicator
        _ = seg.entered_by
        _ = seg.accident_description
        _ = seg.brought_in_by
        _ = seg.police_notified_indicator
        _ = seg.accident_address
        _ = seg.degree_of_patient_liability
        _ = seg.accident_identifier

    def test_add_attributes(self):
        seg = ADD()
        _ = seg.addendum_continuation_pointer

    def test_adj_attributes(self):
        seg = ADJ()
        _ = seg.provider_adjustment_number
        _ = seg.payer_adjustment_number
        _ = seg.adjustment_sequence_number
        _ = seg.adjustment_category
        _ = seg.adjustment_amount
        _ = seg.adjustment_quantity
        _ = seg.adjustment_reason_pa
        _ = seg.adjustment_description
        _ = seg.original_value
        _ = seg.substitute_value
        _ = seg.adjustment_action
        _ = seg.provider_adjustment_number_cross_reference
        _ = seg.provider_product_service_line_item_number_cross_reference
        _ = seg.adjustment_date
        _ = seg.responsible_organization

    def test_aff_attributes(self):
        seg = AFF()
        _ = seg.set_id_aff
        _ = seg.professional_organization
        _ = seg.professional_organization_address
        _ = seg.professional_organization_affiliation_date_range
        _ = seg.professional_affiliation_additional_information

    def test_aig_attributes(self):
        seg = AIG()
        _ = seg.set_id_aig
        _ = seg.segment_action_code
        _ = seg.resource_id
        _ = seg.resource_type
        _ = seg.resource_group
        _ = seg.resource_quantity
        _ = seg.resource_quantity_units
        _ = seg.start_date_time
        _ = seg.start_date_time_offset
        _ = seg.start_date_time_offset_units
        _ = seg.duration
        _ = seg.duration_units
        _ = seg.allow_substitution_code
        _ = seg.filler_status_code

    def test_ail_attributes(self):
        seg = AIL()
        _ = seg.set_id_ail
        _ = seg.segment_action_code
        _ = seg.location_resource_id
        _ = seg.location_type_ail
        _ = seg.location_group
        _ = seg.start_date_time
        _ = seg.start_date_time_offset
        _ = seg.start_date_time_offset_units
        _ = seg.duration
        _ = seg.duration_units
        _ = seg.allow_substitution_code
        _ = seg.filler_status_code

    def test_aip_attributes(self):
        seg = AIP()
        _ = seg.set_id_aip
        _ = seg.segment_action_code
        _ = seg.personnel_resource_id
        _ = seg.resource_type
        _ = seg.resource_group
        _ = seg.start_date_time
        _ = seg.start_date_time_offset
        _ = seg.start_date_time_offset_units
        _ = seg.duration
        _ = seg.duration_units
        _ = seg.allow_substitution_code
        _ = seg.filler_status_code

    def test_ais_attributes(self):
        seg = AIS()
        _ = seg.set_id_ais
        _ = seg.segment_action_code
        _ = seg.universal_service_identifier
        _ = seg.start_date_time
        _ = seg.start_date_time_offset
        _ = seg.start_date_time_offset_units
        _ = seg.duration
        _ = seg.duration_units
        _ = seg.allow_substitution_code
        _ = seg.filler_status_code
        _ = seg.placer_supplemental_service_information
        _ = seg.filler_supplemental_service_information

    def test_al1_attributes(self):
        seg = AL1()
        _ = seg.set_id_al1
        _ = seg.allergen_type_code
        _ = seg.allergen_code_mnemonic_description
        _ = seg.allergy_severity_code
        _ = seg.allergy_reaction_code

    def test_apr_attributes(self):
        seg = APR()
        _ = seg.time_selection_criteria
        _ = seg.resource_selection_criteria
        _ = seg.location_selection_criteria
        _ = seg.slot_spacing_criteria
        _ = seg.filler_override_criteria

    def test_arq_attributes(self):
        seg = ARQ()
        _ = seg.placer_appointment_id
        _ = seg.filler_appointment_id
        _ = seg.occurrence_number
        _ = seg.placer_order_group_number
        _ = seg.schedule_id
        _ = seg.request_event_reason
        _ = seg.appointment_reason
        _ = seg.appointment_type
        _ = seg.appointment_duration
        _ = seg.appointment_duration_units
        _ = seg.requested_start_date_time_range
        _ = seg.priority_arq
        _ = seg.repeating_interval
        _ = seg.repeating_interval_duration
        _ = seg.placer_contact_person
        _ = seg.placer_contact_phone_number
        _ = seg.placer_contact_address
        _ = seg.placer_contact_location
        _ = seg.entered_by_person
        _ = seg.entered_by_phone_number
        _ = seg.entered_by_location
        _ = seg.parent_placer_appointment_id
        _ = seg.parent_filler_appointment_id
        _ = seg.placer_order_number
        _ = seg.filler_order_number
        _ = seg.alternate_placer_order_group_number

    def test_arv_attributes(self):
        seg = ARV()
        _ = seg.set_id
        _ = seg.access_restriction_action_code
        _ = seg.access_restriction_value
        _ = seg.access_restriction_reason
        _ = seg.special_access_restriction_instructions
        _ = seg.access_restriction_date_range
        _ = seg.security_classification_tag
        _ = seg.security_handling_instructions
        _ = seg.access_restriction_message_location
        _ = seg.access_restriction_instance_identifier

    def test_aut_attributes(self):
        seg = AUT()
        _ = seg.authorizing_payor_plan_id
        _ = seg.authorizing_payor_company_id
        _ = seg.authorizing_payor_company_name
        _ = seg.authorization_effective_date
        _ = seg.authorization_expiration_date
        _ = seg.authorization_identifier
        _ = seg.reimbursement_limit
        _ = seg.requested_number_of_treatments
        _ = seg.authorized_number_of_treatments
        _ = seg.process_date
        _ = seg.requested_disciplines
        _ = seg.authorized_disciplines
        _ = seg.authorization_referral_type
        _ = seg.approval_status
        _ = seg.planned_treatment_stop_date
        _ = seg.clinical_service
        _ = seg.reason_text
        _ = seg.number_of_authorized_treatments_units
        _ = seg.number_of_used_treatments_units
        _ = seg.number_of_schedule_treatments_units
        _ = seg.encounter_type
        _ = seg.remaining_benefit_amount
        _ = seg.authorized_provider
        _ = seg.authorized_health_professional
        _ = seg.source_text
        _ = seg.source_date
        _ = seg.source_phone
        _ = seg.comment
        _ = seg.action_code

    def test_bhs_attributes(self):
        seg = BHS()
        _ = seg.batch_field_separator
        _ = seg.batch_encoding_characters
        _ = seg.batch_sending_application
        _ = seg.batch_sending_facility
        _ = seg.batch_receiving_application
        _ = seg.batch_receiving_facility
        _ = seg.batch_creation_date_time
        _ = seg.batch_security
        _ = seg.batch_name_id_type
        _ = seg.batch_comment
        _ = seg.batch_control_id
        _ = seg.reference_batch_control_id
        _ = seg.batch_sending_network_address
        _ = seg.batch_receiving_network_address
        _ = seg.security_classification_tag
        _ = seg.security_handling_instructions
        _ = seg.special_access_restriction_instructions

    def test_blc_attributes(self):
        seg = BLC()
        _ = seg.blood_product_code
        _ = seg.blood_amount

    def test_blg_attributes(self):
        seg = BLG()
        _ = seg.when_to_charge
        _ = seg.charge_type
        _ = seg.account_id
        _ = seg.charge_type_reason

    def test_bpo_attributes(self):
        seg = BPO()
        _ = seg.set_id_bpo
        _ = seg.bp_universal_service_identifier
        _ = seg.bp_processing_requirements
        _ = seg.bp_quantity
        _ = seg.bp_amount
        _ = seg.bp_units
        _ = seg.bp_intended_use_date_time
        _ = seg.bp_intended_dispense_from_location
        _ = seg.bp_intended_dispense_from_address
        _ = seg.bp_requested_dispense_date_time
        _ = seg.bp_requested_dispense_to_location
        _ = seg.bp_requested_dispense_to_address
        _ = seg.bp_indication_for_use
        _ = seg.bp_informed_consent_indicator

    def test_bpx_attributes(self):
        seg = BPX()
        _ = seg.set_id_bpx
        _ = seg.bp_dispense_status
        _ = seg.bp_status
        _ = seg.bp_date_time_of_status
        _ = seg.bc_donation_id
        _ = seg.bc_component
        _ = seg.bc_donation_type_intended_use
        _ = seg.cp_commercial_product
        _ = seg.cp_manufacturer
        _ = seg.cp_lot_number
        _ = seg.bp_blood_group
        _ = seg.bc_special_testing
        _ = seg.bp_expiration_date_time
        _ = seg.bp_quantity
        _ = seg.bp_amount
        _ = seg.bp_units
        _ = seg.bp_unique_id
        _ = seg.bp_actual_dispensed_to_location
        _ = seg.bp_actual_dispensed_to_address
        _ = seg.bp_dispensed_to_receiver
        _ = seg.bp_dispensing_individual
        _ = seg.action_code

    def test_bts_attributes(self):
        seg = BTS()
        _ = seg.batch_message_count
        _ = seg.batch_comment
        _ = seg.batch_totals

    def test_btx_attributes(self):
        seg = BTX()
        _ = seg.set_id_btx
        _ = seg.bc_donation_id
        _ = seg.bc_component
        _ = seg.bc_blood_group
        _ = seg.cp_commercial_product
        _ = seg.cp_manufacturer
        _ = seg.cp_lot_number
        _ = seg.bp_quantity
        _ = seg.bp_amount
        _ = seg.bp_units
        _ = seg.bp_transfusion_disposition_status
        _ = seg.bp_message_status
        _ = seg.bp_date_time_of_status
        _ = seg.bp_transfusion_administrator
        _ = seg.bp_transfusion_verifier
        _ = seg.bp_transfusion_start_date_time_of_status
        _ = seg.bp_transfusion_end_date_time_of_status
        _ = seg.bp_adverse_reaction_type
        _ = seg.bp_transfusion_interrupted_reason
        _ = seg.bp_unique_id
        _ = seg.action_code

    def test_bui_attributes(self):
        seg = BUI()
        _ = seg.set_id_bui
        _ = seg.blood_unit_identifier
        _ = seg.blood_unit_type
        _ = seg.blood_unit_weight
        _ = seg.weight_units
        _ = seg.blood_unit_volume
        _ = seg.volume_units
        _ = seg.container_catalog_number
        _ = seg.container_lot_number
        _ = seg.container_manufacturer
        _ = seg.transport_temperature
        _ = seg.transport_temperature_units
        _ = seg.action_code

    def test_cdm_attributes(self):
        seg = CDM()
        _ = seg.primary_key_value_cdm
        _ = seg.charge_code_alias
        _ = seg.charge_description_short
        _ = seg.charge_description_long
        _ = seg.description_override_indicator
        _ = seg.exploding_charges
        _ = seg.procedure_code
        _ = seg.active_inactive_flag
        _ = seg.inventory_number
        _ = seg.resource_load
        _ = seg.contract_number
        _ = seg.contract_organization
        _ = seg.room_fee_indicator

    def test_cdo_attributes(self):
        seg = CDO()
        _ = seg.set_id_cdo
        _ = seg.action_code
        _ = seg.cumulative_dosage_limit
        _ = seg.cumulative_dosage_limit_time_interval

    def test_cer_attributes(self):
        seg = CER()
        _ = seg.set_id_cer
        _ = seg.serial_number
        _ = seg.version
        _ = seg.granting_authority
        _ = seg.issuing_authority
        _ = seg.signature
        _ = seg.granting_country
        _ = seg.granting_state_province
        _ = seg.granting_county_parish
        _ = seg.certificate_type
        _ = seg.certificate_domain
        _ = seg.subject_id
        _ = seg.subject_name
        _ = seg.subject_directory_attribute_extension
        _ = seg.subject_public_key_info
        _ = seg.authority_key_identifier
        _ = seg.basic_constraint
        _ = seg.crl_distribution_point
        _ = seg.jurisdiction_country
        _ = seg.jurisdiction_state_province
        _ = seg.jurisdiction_county_parish
        _ = seg.jurisdiction_breadth
        _ = seg.granting_date
        _ = seg.issuing_date
        _ = seg.activation_date
        _ = seg.inactivation_date
        _ = seg.expiration_date
        _ = seg.renewal_date
        _ = seg.revocation_date
        _ = seg.revocation_reason_code
        _ = seg.certificate_status_code

    def test_cm0_attributes(self):
        seg = CM0()
        _ = seg.set_id_cm0
        _ = seg.sponsor_study_id
        _ = seg.alternate_study_id
        _ = seg.title_of_study
        _ = seg.chairman_of_study
        _ = seg.last_irb_approval_date
        _ = seg.total_accrual_to_date
        _ = seg.last_accrual_date
        _ = seg.contact_for_study
        _ = seg.contacts_telephone_number
        _ = seg.contacts_address

    def test_cm1_attributes(self):
        seg = CM1()
        _ = seg.set_id_cm1
        _ = seg.study_phase_identifier
        _ = seg.description_of_study_phase

    def test_cm2_attributes(self):
        seg = CM2()
        _ = seg.set_id_cm2
        _ = seg.scheduled_time_point
        _ = seg.description_of_time_point
        _ = seg.events_scheduled_this_time_point

    def test_cns_attributes(self):
        seg = CNS()
        _ = seg.starting_notification_reference_number
        _ = seg.ending_notification_reference_number
        _ = seg.starting_notification_date_time
        _ = seg.ending_notification_date_time
        _ = seg.starting_notification_code
        _ = seg.ending_notification_code

    def test_con_attributes(self):
        seg = CON()
        _ = seg.set_id_con
        _ = seg.consent_type
        _ = seg.consent_form_id_and_version
        _ = seg.consent_form_number
        _ = seg.consent_text
        _ = seg.subject_specific_consent_text
        _ = seg.consent_background_information
        _ = seg.subject_specific_consent_background_text
        _ = seg.consenter_imposed_limitations
        _ = seg.consent_mode
        _ = seg.consent_status
        _ = seg.consent_discussion_date_time
        _ = seg.consent_decision_date_time
        _ = seg.consent_effective_date_time
        _ = seg.consent_end_date_time
        _ = seg.subject_competence_indicator
        _ = seg.translator_assistance_indicator
        _ = seg.language_translated_to
        _ = seg.informational_material_supplied_indicator
        _ = seg.consent_bypass_reason
        _ = seg.consent_disclosure_level
        _ = seg.consent_non_disclosure_reason
        _ = seg.non_subject_consenter_reason
        _ = seg.consenter_id
        _ = seg.relationship_to_subject

    def test_csp_attributes(self):
        seg = CSP()
        _ = seg.study_phase_identifier
        _ = seg.datetime_study_phase_began
        _ = seg.datetime_study_phase_ended
        _ = seg.study_phase_evaluability

    def test_csr_attributes(self):
        seg = CSR()
        _ = seg.sponsor_study_id
        _ = seg.alternate_study_id
        _ = seg.institution_registering_the_patient
        _ = seg.sponsor_patient_id
        _ = seg.alternate_patient_id_csr
        _ = seg.date_time_of_patient_study_registration
        _ = seg.person_performing_study_registration
        _ = seg.study_authorizing_provider
        _ = seg.date_time_patient_study_consent_signed
        _ = seg.patient_study_eligibility_status
        _ = seg.study_randomization_datetime
        _ = seg.randomized_study_arm
        _ = seg.stratum_for_study_randomization
        _ = seg.patient_evaluability_status
        _ = seg.date_time_ended_study
        _ = seg.reason_ended_study
        _ = seg.action_code

    def test_css_attributes(self):
        seg = CSS()
        _ = seg.study_scheduled_time_point
        _ = seg.study_scheduled_patient_time_point
        _ = seg.study_quality_control_codes

    def test_ctd_attributes(self):
        seg = CTD()
        _ = seg.contact_role
        _ = seg.contact_name
        _ = seg.contact_address
        _ = seg.contact_location
        _ = seg.contact_communication_information
        _ = seg.preferred_method_of_contact
        _ = seg.contact_identifiers

    def test_cti_attributes(self):
        seg = CTI()
        _ = seg.sponsor_study_id
        _ = seg.study_phase_identifier
        _ = seg.study_scheduled_time_point
        _ = seg.action_code

    def test_ctr_attributes(self):
        seg = CTR()
        _ = seg.contract_identifier
        _ = seg.contract_description
        _ = seg.contract_status
        _ = seg.effective_date
        _ = seg.expiration_date
        _ = seg.contract_owner_name
        _ = seg.contract_originator_name
        _ = seg.supplier_type
        _ = seg.contract_type
        _ = seg.free_on_board_freight_terms
        _ = seg.price_protection_date
        _ = seg.fixed_price_contract_indicator
        _ = seg.group_purchasing_organization
        _ = seg.maximum_markup
        _ = seg.actual_markup
        _ = seg.corporation
        _ = seg.parent_of_corporation
        _ = seg.pricing_tier_level
        _ = seg.contract_priority
        _ = seg.class_of_trade
        _ = seg.associated_contract_id

    def test_db1_attributes(self):
        seg = DB1()
        _ = seg.set_id_db1
        _ = seg.disabled_person_code
        _ = seg.disabled_person_identifier
        _ = seg.disability_indicator
        _ = seg.disability_start_date
        _ = seg.disability_end_date
        _ = seg.disability_return_to_work_date
        _ = seg.disability_unable_to_work_date

    def test_dev_attributes(self):
        seg = DEV()
        _ = seg.action_code
        _ = seg.unique_device_identifier
        _ = seg.device_type
        _ = seg.device_status
        _ = seg.manufacturer_distributor
        _ = seg.brand_name
        _ = seg.model_identifier
        _ = seg.catalogue_identifier
        _ = seg.udi_device_identifier
        _ = seg.device_lot_number
        _ = seg.device_serial_number
        _ = seg.device_manufacture_date
        _ = seg.device_expiry_date
        _ = seg.safety_characteristics
        _ = seg.device_donation_identification
        _ = seg.software_version_number
        _ = seg.implantation_status

    def test_dg1_attributes(self):
        seg = DG1()
        _ = seg.set_id_dg1
        _ = seg.diagnosis_code_dg1
        _ = seg.diagnosis_date_time
        _ = seg.diagnosis_type
        _ = seg.diagnosis_priority
        _ = seg.diagnosing_clinician
        _ = seg.diagnosis_classification
        _ = seg.confidential_indicator
        _ = seg.attestation_date_time
        _ = seg.diagnosis_identifier
        _ = seg.diagnosis_action_code
        _ = seg.parent_diagnosis
        _ = seg.drg_ccl_value_code
        _ = seg.drg_grouping_usage
        _ = seg.drg_diagnosis_determination_status
        _ = seg.present_on_admission_poa_indicator

    def test_dmi_attributes(self):
        seg = DMI()
        _ = seg.diagnostic_related_group
        _ = seg.major_diagnostic_category
        _ = seg.lower_and_upper_trim_points
        _ = seg.average_length_of_stay
        _ = seg.relative_weight

    def test_don_attributes(self):
        seg = DON()
        _ = seg.donation_identification_number_din
        _ = seg.donation_type
        _ = seg.phlebotomy_start_date_time
        _ = seg.phlebotomy_end_date_time
        _ = seg.donation_duration
        _ = seg.donation_duration_units
        _ = seg.intended_procedure_type
        _ = seg.actual_procedure_type
        _ = seg.donor_eligibility_flag
        _ = seg.donor_eligibility_procedure_type
        _ = seg.donor_eligibility_date
        _ = seg.process_interruption
        _ = seg.process_interruption_reason
        _ = seg.phlebotomy_issue
        _ = seg.intended_recipient_blood_relative
        _ = seg.intended_recipient_name
        _ = seg.intended_recipient_dob
        _ = seg.intended_recipient_facility
        _ = seg.intended_recipient_procedure_date
        _ = seg.intended_recipient_ordering_provider
        _ = seg.phlebotomy_status
        _ = seg.arm_stick
        _ = seg.bleed_start_phlebotomist
        _ = seg.bleed_end_phlebotomist
        _ = seg.aphaeresis_type_machine
        _ = seg.aphaeresis_machine_serial_number
        _ = seg.donor_reaction
        _ = seg.final_review_staff_id
        _ = seg.final_review_date_time
        _ = seg.number_of_tubes_collected
        _ = seg.donation_sample_identifier
        _ = seg.donation_accept_staff
        _ = seg.donation_material_review_staff
        _ = seg.action_code

    def test_dps_attributes(self):
        seg = DPS()
        _ = seg.diagnosis_code_mcp
        _ = seg.procedure_code
        _ = seg.effective_date_time
        _ = seg.expiration_date_time
        _ = seg.type_of_limitation

    def test_drg_attributes(self):
        seg = DRG()
        _ = seg.diagnostic_related_group
        _ = seg.drg_assigned_date_time
        _ = seg.drg_approval_indicator
        _ = seg.drg_grouper_review_code
        _ = seg.outlier_type
        _ = seg.outlier_days
        _ = seg.outlier_cost
        _ = seg.drg_payor
        _ = seg.outlier_reimbursement
        _ = seg.confidential_indicator
        _ = seg.drg_transfer_type
        _ = seg.name_of_coder
        _ = seg.grouper_status
        _ = seg.pccl_value_code
        _ = seg.effective_weight
        _ = seg.monetary_amount
        _ = seg.status_patient
        _ = seg.grouper_software_name
        _ = seg.grouper_software_version
        _ = seg.status_financial_calculation
        _ = seg.relative_discount_surcharge
        _ = seg.basic_charge
        _ = seg.total_charge
        _ = seg.discount_surcharge
        _ = seg.calculated_days
        _ = seg.status_gender
        _ = seg.status_age
        _ = seg.status_length_of_stay
        _ = seg.status_same_day_flag
        _ = seg.status_separation_mode
        _ = seg.status_weight_at_birth
        _ = seg.status_respiration_minutes
        _ = seg.status_admission

    def test_dsc_attributes(self):
        seg = DSC()
        _ = seg.continuation_pointer
        _ = seg.continuation_style

    def test_dsp_attributes(self):
        seg = DSP()
        _ = seg.set_id_dsp
        _ = seg.display_level
        _ = seg.data_line
        _ = seg.logical_break_point
        _ = seg.result_id

    def test_dst_attributes(self):
        seg = DST()
        _ = seg.destination
        _ = seg.route

    def test_ecd_attributes(self):
        seg = ECD()
        _ = seg.reference_command_number
        _ = seg.remote_control_command
        _ = seg.response_required
        _ = seg.parameters

    def test_ecr_attributes(self):
        seg = ECR()
        _ = seg.command_response
        _ = seg.date_time_completed
        _ = seg.command_response_parameters

    def test_edu_attributes(self):
        seg = EDU()
        _ = seg.set_id_edu
        _ = seg.academic_degree
        _ = seg.academic_degree_program_date_range
        _ = seg.academic_degree_program_participation_date_range
        _ = seg.academic_degree_granted_date
        _ = seg.school
        _ = seg.school_type_code
        _ = seg.school_address
        _ = seg.major_field_of_study

    def test_eqp_attributes(self):
        seg = EQP()
        _ = seg.event_type
        _ = seg.file_name
        _ = seg.start_date_time
        _ = seg.end_date_time
        _ = seg.transaction_data

    def test_equ_attributes(self):
        seg = EQU()
        _ = seg.equipment_instance_identifier
        _ = seg.event_date_time
        _ = seg.equipment_state
        _ = seg.local_remote_control_state
        _ = seg.alert_level
        _ = seg.expected_datetime_of_the_next_status_change

    def test_err_attributes(self):
        seg = ERR()
        _ = seg.error_location
        _ = seg.hl7_error_code
        _ = seg.severity
        _ = seg.application_error_code
        _ = seg.application_error_parameter
        _ = seg.diagnostic_information
        _ = seg.user_message
        _ = seg.inform_person_indicator
        _ = seg.override_type
        _ = seg.override_reason_code
        _ = seg.help_desk_contact_point

    def test_evn_attributes(self):
        seg = EVN()
        _ = seg.recorded_date_time
        _ = seg.date_time_planned_event
        _ = seg.event_reason_code
        _ = seg.operator_id
        _ = seg.event_occurred
        _ = seg.event_facility

    def test_fac_attributes(self):
        seg = FAC()
        _ = seg.facility_id_fac
        _ = seg.facility_type
        _ = seg.facility_address
        _ = seg.facility_telecommunication
        _ = seg.contact_person
        _ = seg.contact_title
        _ = seg.contact_address
        _ = seg.contact_telecommunication
        _ = seg.signature_authority
        _ = seg.signature_authority_title
        _ = seg.signature_authority_address
        _ = seg.signature_authority_telecommunication

    def test_fhs_attributes(self):
        seg = FHS()
        _ = seg.file_field_separator
        _ = seg.file_encoding_characters
        _ = seg.file_sending_application
        _ = seg.file_sending_facility
        _ = seg.file_receiving_application
        _ = seg.file_receiving_facility
        _ = seg.file_creation_date_time
        _ = seg.file_security
        _ = seg.file_name_id
        _ = seg.file_header_comment
        _ = seg.file_control_id
        _ = seg.reference_file_control_id
        _ = seg.file_sending_network_address
        _ = seg.file_receiving_network_address
        _ = seg.security_classification_tag
        _ = seg.security_handling_instructions
        _ = seg.special_access_restriction_instructions

    def test_ft1_attributes(self):
        seg = FT1()
        _ = seg.set_id_ft1
        _ = seg.transaction_id
        _ = seg.transaction_batch_id
        _ = seg.transaction_date
        _ = seg.transaction_posting_date
        _ = seg.transaction_type
        _ = seg.transaction_code
        _ = seg.transaction_quantity
        _ = seg.transaction_amount_extended
        _ = seg.transaction_amount_unit
        _ = seg.department_code
        _ = seg.health_plan_id
        _ = seg.insurance_amount
        _ = seg.assigned_patient_location
        _ = seg.fee_schedule
        _ = seg.patient_type
        _ = seg.diagnosis_code_ft1
        _ = seg.performed_by_code
        _ = seg.ordered_by_code
        _ = seg.unit_cost
        _ = seg.filler_order_number
        _ = seg.entered_by_code
        _ = seg.procedure_code
        _ = seg.procedure_code_modifier
        _ = seg.advanced_beneficiary_notice_code
        _ = seg.medically_necessary_duplicate_procedure_reason
        _ = seg.ndc_code
        _ = seg.payment_reference_id
        _ = seg.transaction_reference_key
        _ = seg.performing_facility
        _ = seg.ordering_facility
        _ = seg.item_number
        _ = seg.model_number
        _ = seg.special_processing_code
        _ = seg.clinic_code
        _ = seg.referral_number
        _ = seg.authorization_number
        _ = seg.service_provider_taxonomy_code
        _ = seg.revenue_code
        _ = seg.prescription_number
        _ = seg.ndc_qty_and_uom
        _ = seg.dme_certificate_of_medical_necessity_transmission_code
        _ = seg.dme_certification_type_code
        _ = seg.dme_duration_value
        _ = seg.dme_certification_revision_date
        _ = seg.dme_initial_certification_date
        _ = seg.dme_last_certification_date
        _ = seg.dme_length_of_medical_necessity_days
        _ = seg.dme_rental_price
        _ = seg.dme_purchase_price
        _ = seg.dme_frequency_code
        _ = seg.dme_certification_condition_indicator
        _ = seg.dme_condition_indicator_code
        _ = seg.service_reason_code

    def test_fts_attributes(self):
        seg = FTS()
        _ = seg.file_batch_count
        _ = seg.file_trailer_comment

    def test_gol_attributes(self):
        seg = GOL()
        _ = seg.action_code
        _ = seg.action_date_time
        _ = seg.goal_id
        _ = seg.goal_instance_id
        _ = seg.episode_of_care_id
        _ = seg.goal_list_priority
        _ = seg.goal_established_date_time
        _ = seg.expected_goal_achieve_date_time
        _ = seg.goal_classification
        _ = seg.goal_management_discipline
        _ = seg.current_goal_review_status
        _ = seg.current_goal_review_date_time
        _ = seg.next_goal_review_date_time
        _ = seg.previous_goal_review_date_time
        _ = seg.goal_evaluation
        _ = seg.goal_evaluation_comment
        _ = seg.goal_life_cycle_status
        _ = seg.goal_life_cycle_status_date_time
        _ = seg.goal_target_type
        _ = seg.goal_target_name
        _ = seg.mood_code

    def test_gp1_attributes(self):
        seg = GP1()
        _ = seg.type_of_bill_code
        _ = seg.revenue_code
        _ = seg.overall_claim_disposition_code
        _ = seg.oce_edits_per_visit_code
        _ = seg.outlier_cost

    def test_gp2_attributes(self):
        seg = GP2()
        _ = seg.revenue_code
        _ = seg.number_of_service_units
        _ = seg.charge
        _ = seg.reimbursement_action_code
        _ = seg.denial_or_rejection_code
        _ = seg.oce_edit_code
        _ = seg.ambulatory_payment_classification_code
        _ = seg.modifier_edit_code
        _ = seg.payment_adjustment_code
        _ = seg.packaging_status_code
        _ = seg.expected_cms_payment_amount
        _ = seg.reimbursement_type_code
        _ = seg.co_pay_amount
        _ = seg.pay_rate_per_service_unit

    def test_gt1_attributes(self):
        seg = GT1()
        _ = seg.set_id_gt1
        _ = seg.guarantor_number
        _ = seg.guarantor_name
        _ = seg.guarantor_spouse_name
        _ = seg.guarantor_address
        _ = seg.guarantor_ph_num_home
        _ = seg.guarantor_ph_num_business
        _ = seg.guarantor_date_time_of_birth
        _ = seg.guarantor_administrative_sex
        _ = seg.guarantor_type
        _ = seg.guarantor_relationship
        _ = seg.guarantor_ssn
        _ = seg.guarantor_date_begin
        _ = seg.guarantor_date_end
        _ = seg.guarantor_priority
        _ = seg.guarantor_employer_name
        _ = seg.guarantor_employer_address
        _ = seg.guarantor_employer_phone_number
        _ = seg.guarantor_employee_id_number
        _ = seg.guarantor_employment_status
        _ = seg.guarantor_organization_name
        _ = seg.guarantor_billing_hold_flag
        _ = seg.guarantor_credit_rating_code
        _ = seg.guarantor_death_date_and_time
        _ = seg.guarantor_death_flag
        _ = seg.guarantor_charge_adjustment_code
        _ = seg.guarantor_household_annual_income
        _ = seg.guarantor_household_size
        _ = seg.guarantor_employer_id_number
        _ = seg.guarantor_marital_status_code
        _ = seg.guarantor_hire_effective_date
        _ = seg.employment_stop_date
        _ = seg.living_dependency
        _ = seg.ambulatory_status
        _ = seg.citizenship
        _ = seg.primary_language
        _ = seg.living_arrangement
        _ = seg.publicity_code
        _ = seg.protection_indicator
        _ = seg.student_indicator
        _ = seg.religion
        _ = seg.mothers_maiden_name
        _ = seg.nationality
        _ = seg.ethnic_group
        _ = seg.contact_persons_name
        _ = seg.contact_persons_telephone_number
        _ = seg.contact_reason
        _ = seg.contact_relationship
        _ = seg.job_title
        _ = seg.job_code_class
        _ = seg.guarantor_employers_organization_name
        _ = seg.handicap
        _ = seg.job_status
        _ = seg.guarantor_financial_class
        _ = seg.guarantor_race
        _ = seg.guarantor_birth_place
        _ = seg.vip_indicator

    def test_iam_attributes(self):
        seg = IAM()
        _ = seg.set_id_iam
        _ = seg.allergen_type_code
        _ = seg.allergen_code_mnemonic_description
        _ = seg.allergy_severity_code
        _ = seg.allergy_reaction_code
        _ = seg.allergy_action_code
        _ = seg.allergy_unique_identifier
        _ = seg.action_reason
        _ = seg.sensitivity_to_causative_agent_code
        _ = seg.allergen_group_code_mnemonic_description
        _ = seg.onset_date
        _ = seg.onset_date_text
        _ = seg.reported_date_time
        _ = seg.reported_by
        _ = seg.relationship_to_patient_code
        _ = seg.alert_device_code
        _ = seg.allergy_clinical_status_code
        _ = seg.statused_by_person
        _ = seg.statused_by_organization
        _ = seg.statused_at_date_time
        _ = seg.inactivated_by_person
        _ = seg.inactivated_date_time
        _ = seg.initially_recorded_by_person
        _ = seg.initially_recorded_date_time
        _ = seg.modified_by_person
        _ = seg.modified_date_time
        _ = seg.clinician_identified_code
        _ = seg.initially_recorded_by_organization
        _ = seg.modified_by_organization
        _ = seg.inactivated_by_organization

    def test_iar_attributes(self):
        seg = IAR()
        _ = seg.allergy_reaction_code
        _ = seg.allergy_severity_code
        _ = seg.sensitivity_to_causative_agent_code
        _ = seg.management

    def test_iim_attributes(self):
        seg = IIM()
        _ = seg.primary_key_value_iim
        _ = seg.service_item_code
        _ = seg.inventory_lot_number
        _ = seg.inventory_expiration_date
        _ = seg.inventory_manufacturer_name
        _ = seg.inventory_location
        _ = seg.inventory_received_date
        _ = seg.inventory_received_quantity
        _ = seg.inventory_received_quantity_unit
        _ = seg.inventory_received_item_cost
        _ = seg.inventory_on_hand_date
        _ = seg.inventory_on_hand_quantity
        _ = seg.inventory_on_hand_quantity_unit
        _ = seg.procedure_code
        _ = seg.procedure_code_modifier

    def test_ilt_attributes(self):
        seg = ILT()
        _ = seg.set_id_ilt
        _ = seg.inventory_lot_number
        _ = seg.inventory_expiration_date
        _ = seg.inventory_received_date
        _ = seg.inventory_received_quantity
        _ = seg.inventory_received_quantity_unit
        _ = seg.inventory_received_item_cost
        _ = seg.inventory_on_hand_date
        _ = seg.inventory_on_hand_quantity
        _ = seg.inventory_on_hand_quantity_unit

    def test_in1_attributes(self):
        seg = IN1()
        _ = seg.set_id_in1
        _ = seg.health_plan_id
        _ = seg.insurance_company_id
        _ = seg.insurance_company_name
        _ = seg.insurance_company_address
        _ = seg.insurance_co_contact_person
        _ = seg.insurance_co_phone_number
        _ = seg.group_number
        _ = seg.group_name
        _ = seg.insureds_group_emp_id
        _ = seg.insureds_group_emp_name
        _ = seg.plan_effective_date
        _ = seg.plan_expiration_date
        _ = seg.authorization_information
        _ = seg.plan_type
        _ = seg.name_of_insured
        _ = seg.insureds_relationship_to_patient
        _ = seg.insureds_date_of_birth
        _ = seg.insureds_address
        _ = seg.assignment_of_benefits
        _ = seg.coordination_of_benefits
        _ = seg.coord_of_ben_priority
        _ = seg.notice_of_admission_flag
        _ = seg.notice_of_admission_date
        _ = seg.report_of_eligibility_flag
        _ = seg.report_of_eligibility_date
        _ = seg.release_information_code
        _ = seg.pre_admit_cert_pac
        _ = seg.verification_date_time
        _ = seg.verification_by
        _ = seg.type_of_agreement_code
        _ = seg.billing_status
        _ = seg.lifetime_reserve_days
        _ = seg.delay_before_lr_day
        _ = seg.company_plan_code
        _ = seg.policy_number
        _ = seg.policy_deductible
        _ = seg.policy_limit_days
        _ = seg.insureds_employment_status
        _ = seg.insureds_administrative_sex
        _ = seg.insureds_employers_address
        _ = seg.verification_status
        _ = seg.prior_insurance_plan_id
        _ = seg.coverage_type
        _ = seg.handicap
        _ = seg.insureds_id_number
        _ = seg.signature_code
        _ = seg.signature_code_date
        _ = seg.insureds_birth_place
        _ = seg.vip_indicator
        _ = seg.external_health_plan_identifiers
        _ = seg.insurance_action_code

    def test_in2_attributes(self):
        seg = IN2()
        _ = seg.insureds_employee_id
        _ = seg.insureds_social_security_number
        _ = seg.insureds_employers_name_and_id
        _ = seg.employer_information_data
        _ = seg.mail_claim_party
        _ = seg.medicare_health_ins_card_number
        _ = seg.medicaid_case_name
        _ = seg.medicaid_case_number
        _ = seg.military_sponsor_name
        _ = seg.military_id_number
        _ = seg.dependent_of_military_recipient
        _ = seg.military_organization
        _ = seg.military_station
        _ = seg.military_service
        _ = seg.military_rank_grade
        _ = seg.military_status
        _ = seg.military_retire_date
        _ = seg.military_non_avail_cert_on_file
        _ = seg.baby_coverage
        _ = seg.combine_baby_bill
        _ = seg.blood_deductible
        _ = seg.special_coverage_approval_name
        _ = seg.special_coverage_approval_title
        _ = seg.non_covered_insurance_code
        _ = seg.payor_id
        _ = seg.payor_subscriber_id
        _ = seg.eligibility_source
        _ = seg.room_coverage_type_amount
        _ = seg.policy_type_amount
        _ = seg.daily_deductible
        _ = seg.living_dependency
        _ = seg.ambulatory_status
        _ = seg.citizenship
        _ = seg.primary_language
        _ = seg.living_arrangement
        _ = seg.publicity_code
        _ = seg.protection_indicator
        _ = seg.student_indicator
        _ = seg.religion
        _ = seg.mothers_maiden_name
        _ = seg.nationality
        _ = seg.ethnic_group
        _ = seg.marital_status
        _ = seg.insureds_employment_start_date
        _ = seg.employment_stop_date
        _ = seg.job_title
        _ = seg.job_code_class
        _ = seg.job_status
        _ = seg.employer_contact_person_name
        _ = seg.employer_contact_person_phone_number
        _ = seg.employer_contact_reason
        _ = seg.insureds_contact_persons_name
        _ = seg.insureds_contact_person_phone_number
        _ = seg.insureds_contact_person_reason
        _ = seg.relationship_to_the_patient_start_date
        _ = seg.relationship_to_the_patient_stop_date
        _ = seg.insurance_co_contact_reason
        _ = seg.insurance_co_contact_phone_number
        _ = seg.policy_scope
        _ = seg.policy_source
        _ = seg.patient_member_number
        _ = seg.guarantors_relationship_to_insured
        _ = seg.insureds_phone_number_home
        _ = seg.insureds_employer_phone_number
        _ = seg.military_handicapped_program
        _ = seg.suspend_flag
        _ = seg.copay_limit_flag
        _ = seg.stoploss_limit_flag
        _ = seg.insured_organization_name_and_id
        _ = seg.insured_employer_organization_name_and_id
        _ = seg.race
        _ = seg.patients_relationship_to_insured
        _ = seg.co_pay_amount

    def test_in3_attributes(self):
        seg = IN3()
        _ = seg.set_id_in3
        _ = seg.certification_number
        _ = seg.certified_by
        _ = seg.certification_required
        _ = seg.penalty
        _ = seg.certification_date_time
        _ = seg.certification_modify_date_time
        _ = seg.operator
        _ = seg.certification_begin_date
        _ = seg.certification_end_date
        _ = seg.days
        _ = seg.non_concur_code_description
        _ = seg.non_concur_effective_date_time
        _ = seg.physician_reviewer
        _ = seg.certification_contact
        _ = seg.certification_contact_phone_number
        _ = seg.appeal_reason
        _ = seg.certification_agency
        _ = seg.certification_agency_phone_number
        _ = seg.pre_certification_requirement
        _ = seg.case_manager
        _ = seg.second_opinion_date
        _ = seg.second_opinion_status
        _ = seg.second_opinion_documentation_received
        _ = seg.second_opinion_physician
        _ = seg.certification_type
        _ = seg.certification_category
        _ = seg.online_verification_date_time
        _ = seg.online_verification_result
        _ = seg.online_verification_result_error_code
        _ = seg.online_verification_result_check_digit

    def test_inv_attributes(self):
        seg = INV()
        _ = seg.substance_identifier
        _ = seg.substance_status
        _ = seg.substance_type
        _ = seg.inventory_container_identifier
        _ = seg.container_carrier_identifier
        _ = seg.position_on_carrier
        _ = seg.initial_quantity
        _ = seg.current_quantity
        _ = seg.available_quantity
        _ = seg.consumption_quantity
        _ = seg.quantity_units
        _ = seg.expiration_date_time
        _ = seg.first_used_date_time
        _ = seg.test_fluid_identifiers
        _ = seg.manufacturer_lot_number
        _ = seg.manufacturer_identifier
        _ = seg.supplier_identifier
        _ = seg.on_board_stability_time
        _ = seg.target_value
        _ = seg.equipment_state_indicator_type_code
        _ = seg.equipment_state_indicator_value

    def test_ipc_attributes(self):
        seg = IPC()
        _ = seg.accession_identifier
        _ = seg.requested_procedure_id
        _ = seg.study_instance_uid
        _ = seg.scheduled_procedure_step_id
        _ = seg.modality
        _ = seg.protocol_code
        _ = seg.scheduled_station_name
        _ = seg.scheduled_procedure_step_location
        _ = seg.scheduled_station_ae_title
        _ = seg.action_code

    def test_ipr_attributes(self):
        seg = IPR()
        _ = seg.ipr_identifier
        _ = seg.provider_cross_reference_identifier
        _ = seg.payer_cross_reference_identifier
        _ = seg.ipr_status
        _ = seg.ipr_date_time
        _ = seg.adjudicated_paid_amount
        _ = seg.expected_payment_date_time
        _ = seg.ipr_checksum

    def test_isd_attributes(self):
        seg = ISD()
        _ = seg.reference_interaction_number
        _ = seg.interaction_type_identifier
        _ = seg.interaction_active_state

    def test_itm_attributes(self):
        seg = ITM()
        _ = seg.item_identifier
        _ = seg.item_description
        _ = seg.item_status
        _ = seg.item_type
        _ = seg.item_category
        _ = seg.subject_to_expiration_indicator
        _ = seg.manufacturer_identifier
        _ = seg.manufacturer_name
        _ = seg.manufacturer_catalog_number
        _ = seg.manufacturer_labeler_identification_code
        _ = seg.patient_chargeable_indicator
        _ = seg.transaction_code
        _ = seg.transaction_amount_unit
        _ = seg.stocked_item_indicator
        _ = seg.supply_risk_codes
        _ = seg.approving_regulatory_agency
        _ = seg.latex_indicator
        _ = seg.ruling_act
        _ = seg.item_natural_account_code
        _ = seg.approved_to_buy_quantity
        _ = seg.approved_to_buy_price
        _ = seg.taxable_item_indicator
        _ = seg.freight_charge_indicator
        _ = seg.item_set_indicator
        _ = seg.item_set_identifier
        _ = seg.track_department_usage_indicator
        _ = seg.procedure_code
        _ = seg.procedure_code_modifier
        _ = seg.special_handling_code
        _ = seg.hazardous_indicator
        _ = seg.sterile_indicator
        _ = seg.material_data_safety_sheet_number
        _ = seg.united_nations_standard_products_and_services_code_unspsc
        _ = seg.contract_date
        _ = seg.manufacturer_contact_name
        _ = seg.manufacturer_contact_information
        _ = seg.class_of_trade
        _ = seg.field_level_event_code

    def test_ivc_attributes(self):
        seg = IVC()
        _ = seg.provider_invoice_number
        _ = seg.payer_invoice_number
        _ = seg.contract_agreement_number
        _ = seg.invoice_control
        _ = seg.invoice_reason
        _ = seg.invoice_type
        _ = seg.invoice_date_time
        _ = seg.invoice_amount
        _ = seg.payment_terms
        _ = seg.provider_organization
        _ = seg.payer_organization
        _ = seg.attention
        _ = seg.last_invoice_indicator
        _ = seg.invoice_booking_period
        _ = seg.origin
        _ = seg.invoice_fixed_amount
        _ = seg.special_costs
        _ = seg.amount_for_doctors_treatment
        _ = seg.responsible_physician
        _ = seg.cost_center
        _ = seg.invoice_prepaid_amount
        _ = seg.total_invoice_amount_without_prepaid_amount
        _ = seg.total_amount_of_vat
        _ = seg.vat_rates_applied
        _ = seg.benefit_group
        _ = seg.provider_tax_id
        _ = seg.payer_tax_id
        _ = seg.provider_tax_status
        _ = seg.payer_tax_status
        _ = seg.sales_tax_id

    def test_ivt_attributes(self):
        seg = IVT()
        _ = seg.set_id_ivt
        _ = seg.inventory_location_identifier
        _ = seg.inventory_location_name
        _ = seg.source_location_identifier
        _ = seg.source_location_name
        _ = seg.item_status
        _ = seg.bin_location_identifier
        _ = seg.order_packaging
        _ = seg.issue_packaging
        _ = seg.default_inventory_asset_account
        _ = seg.patient_chargeable_indicator
        _ = seg.transaction_code
        _ = seg.transaction_amount_unit
        _ = seg.item_importance_code
        _ = seg.stocked_item_indicator
        _ = seg.consignment_item_indicator
        _ = seg.reusable_item_indicator
        _ = seg.reusable_cost
        _ = seg.substitute_item_identifier
        _ = seg.latex_free_substitute_item_identifier
        _ = seg.recommended_reorder_theory
        _ = seg.recommended_safety_stock_days
        _ = seg.recommended_maximum_days_inventory
        _ = seg.recommended_order_point
        _ = seg.recommended_order_amount
        _ = seg.operating_room_par_level_indicator

    def test_lan_attributes(self):
        seg = LAN()
        _ = seg.set_id_lan
        _ = seg.language_code
        _ = seg.language_ability_code
        _ = seg.language_proficiency_code

    def test_lcc_attributes(self):
        seg = LCC()
        _ = seg.primary_key_value_lcc
        _ = seg.location_department
        _ = seg.accommodation_type
        _ = seg.charge_code

    def test_lch_attributes(self):
        seg = LCH()
        _ = seg.primary_key_value_lch
        _ = seg.segment_action_code
        _ = seg.segment_unique_key
        _ = seg.location_characteristic_id
        _ = seg.location_characteristic_value_lch

    def test_ldp_attributes(self):
        seg = LDP()
        _ = seg.primary_key_value_ldp
        _ = seg.location_department
        _ = seg.location_service
        _ = seg.specialty_type
        _ = seg.valid_patient_classes
        _ = seg.active_inactive_flag
        _ = seg.activation_date_ldp
        _ = seg.inactivation_date_ldp
        _ = seg.inactivated_reason
        _ = seg.visiting_hours
        _ = seg.contact_phone
        _ = seg.location_cost_center

    def test_loc_attributes(self):
        seg = LOC()
        _ = seg.primary_key_value_loc
        _ = seg.location_description
        _ = seg.location_type_loc
        _ = seg.organization_name_loc
        _ = seg.location_address
        _ = seg.location_phone
        _ = seg.license_number
        _ = seg.location_equipment
        _ = seg.location_service_code

    def test_lrl_attributes(self):
        seg = LRL()
        _ = seg.primary_key_value_lrl
        _ = seg.segment_action_code
        _ = seg.segment_unique_key
        _ = seg.location_relationship_id
        _ = seg.organizational_location_relationship_value
        _ = seg.patient_location_relationship_value

    def test_mcp_attributes(self):
        seg = MCP()
        _ = seg.set_id_mcp
        _ = seg.producers_service_test_observation_id
        _ = seg.universal_service_price_range_low_value
        _ = seg.universal_service_price_range_high_value
        _ = seg.reason_for_universal_service_cost_range

    def test_mfa_attributes(self):
        seg = MFA()
        _ = seg.record_level_event_code
        _ = seg.mfn_control_id
        _ = seg.event_completion_date_time
        _ = seg.mfn_record_level_error_return
        _ = seg.primary_key_value_mfa
        _ = seg.primary_key_value_type_mfa

    def test_mfe_attributes(self):
        seg = MFE()
        _ = seg.record_level_event_code
        _ = seg.mfn_control_id
        _ = seg.effective_date_time
        _ = seg.primary_key_value_mfe
        _ = seg.primary_key_value_type
        _ = seg.entered_date_time
        _ = seg.entered_by

    def test_mfi_attributes(self):
        seg = MFI()
        _ = seg.master_file_identifier
        _ = seg.master_file_application_identifier
        _ = seg.file_level_event_code
        _ = seg.entered_date_time
        _ = seg.effective_date_time
        _ = seg.response_level_code

    def test_mrg_attributes(self):
        seg = MRG()
        _ = seg.prior_patient_identifier_list
        _ = seg.prior_patient_account_number
        _ = seg.prior_visit_number
        _ = seg.prior_alternate_visit_id
        _ = seg.prior_patient_name

    def test_msa_attributes(self):
        seg = MSA()
        _ = seg.acknowledgment_code
        _ = seg.message_control_id
        _ = seg.expected_sequence_number
        _ = seg.message_waiting_number
        _ = seg.message_waiting_priority

    def test_msh_attributes(self):
        seg = MSH()
        _ = seg.field_separator
        _ = seg.encoding_characters
        _ = seg.sending_application
        _ = seg.sending_facility
        _ = seg.receiving_application
        _ = seg.receiving_facility
        _ = seg.date_time_of_message
        _ = seg.security
        _ = seg.message_type
        _ = seg.message_control_id
        _ = seg.processing_id
        _ = seg.version_id
        _ = seg.sequence_number
        _ = seg.continuation_pointer
        _ = seg.accept_acknowledgment
        _ = seg.application_acknowledgment_type
        _ = seg.country_code
        _ = seg.character_set
        _ = seg.principal_language_of_message
        _ = seg.alternate_character_set_handling_scheme
        _ = seg.message_profile_identifier
        _ = seg.sending_responsible_organization
        _ = seg.receiving_responsible_organization
        _ = seg.sending_network_address
        _ = seg.receiving_network_address
        _ = seg.security_classification_tag
        _ = seg.security_handling_instructions
        _ = seg.special_access_restriction_instructions

    def test_nck_attributes(self):
        seg = NCK()
        _ = seg.system_date_time

    def test_nds_attributes(self):
        seg = NDS()
        _ = seg.notification_reference_number
        _ = seg.notification_date_time
        _ = seg.notification_alert_severity
        _ = seg.notification_code

    def test_nk1_attributes(self):
        seg = NK1()
        _ = seg.set_id_nk1
        _ = seg.name
        _ = seg.relationship
        _ = seg.address
        _ = seg.contact_role
        _ = seg.start_date
        _ = seg.end_date
        _ = seg.next_of_kin_associated_parties_job_title
        _ = seg.next_of_kin_associated_parties_job_code_class
        _ = seg.next_of_kin_associated_parties_employee_number
        _ = seg.organization_name_nk1
        _ = seg.marital_status
        _ = seg.administrative_sex
        _ = seg.date_time_of_birth
        _ = seg.living_dependency
        _ = seg.ambulatory_status
        _ = seg.citizenship
        _ = seg.primary_language
        _ = seg.living_arrangement
        _ = seg.publicity_code
        _ = seg.protection_indicator
        _ = seg.student_indicator
        _ = seg.religion
        _ = seg.mothers_maiden_name
        _ = seg.nationality
        _ = seg.ethnic_group
        _ = seg.contact_reason
        _ = seg.contact_persons_name
        _ = seg.contact_persons_address
        _ = seg.next_of_kin_associated_partys_identifiers
        _ = seg.job_status
        _ = seg.race
        _ = seg.handicap
        _ = seg.contact_person_social_security_number
        _ = seg.next_of_kin_birth_place
        _ = seg.vip_indicator
        _ = seg.next_of_kin_telecommunication_information
        _ = seg.contact_persons_telecommunication_information

    def test_npu_attributes(self):
        seg = NPU()
        _ = seg.bed_location
        _ = seg.bed_status

    def test_nsc_attributes(self):
        seg = NSC()
        _ = seg.application_change_type
        _ = seg.current_cpu
        _ = seg.current_fileserver
        _ = seg.current_application
        _ = seg.current_facility
        _ = seg.new_cpu
        _ = seg.new_fileserver
        _ = seg.new_application
        _ = seg.new_facility

    def test_nst_attributes(self):
        seg = NST()
        _ = seg.statistics_available
        _ = seg.source_identifier
        _ = seg.source_type
        _ = seg.statistics_start
        _ = seg.statistics_end
        _ = seg.receive_character_count
        _ = seg.send_character_count
        _ = seg.messages_received
        _ = seg.messages_sent
        _ = seg.checksum_errors_received
        _ = seg.length_errors_received
        _ = seg.other_errors_received
        _ = seg.connect_timeouts
        _ = seg.receive_timeouts
        _ = seg.application_control_level_errors

    def test_nte_attributes(self):
        seg = NTE()
        _ = seg.set_id_nte
        _ = seg.source_of_comment
        _ = seg.comment
        _ = seg.comment_type
        _ = seg.entered_by
        _ = seg.entered_date_time
        _ = seg.effective_start_date
        _ = seg.expiration_date
        _ = seg.coded_comment

    def test_obr_attributes(self):
        seg = OBR()
        _ = seg.set_id_obr
        _ = seg.placer_order_number
        _ = seg.filler_order_number
        _ = seg.universal_service_identifier
        _ = seg.observation_date_time
        _ = seg.observation_end_date_time
        _ = seg.collection_volume
        _ = seg.collector_identifier
        _ = seg.specimen_action_code
        _ = seg.danger_code
        _ = seg.relevant_clinical_information
        _ = seg.order_callback_phone_number
        _ = seg.placer_field_1
        _ = seg.placer_field_2
        _ = seg.filler_field_1
        _ = seg.filler_field_2
        _ = seg.results_rpt_status_chng_date_time
        _ = seg.charge_to_practice
        _ = seg.diagnostic_serv_sect_id
        _ = seg.result_status
        _ = seg.parent_result
        _ = seg.parent_results_observation_identifier
        _ = seg.transportation_mode
        _ = seg.reason_for_study
        _ = seg.scheduled_date_time
        _ = seg.number_of_sample_containers
        _ = seg.transport_logistics_of_collected_sample
        _ = seg.collectors_comment
        _ = seg.transport_arrangement_responsibility
        _ = seg.transport_arranged
        _ = seg.escort_required
        _ = seg.planned_patient_transport_comment
        _ = seg.procedure_code
        _ = seg.procedure_code_modifier
        _ = seg.placer_supplemental_service_information
        _ = seg.filler_supplemental_service_information
        _ = seg.medically_necessary_duplicate_procedure_reason
        _ = seg.result_handling
        _ = seg.observation_group_id
        _ = seg.parent_observation_group_id
        _ = seg.alternate_placer_order_number
        _ = seg.parent_order
        _ = seg.action_code

    def test_obx_attributes(self):
        seg = OBX()
        _ = seg.set_id_obx
        _ = seg.value_type
        _ = seg.observation_identifier
        _ = seg.observation_sub_id
        _ = seg.observation_value
        _ = seg.units
        _ = seg.reference_range
        _ = seg.interpretation_codes
        _ = seg.probability
        _ = seg.nature_of_abnormal_test
        _ = seg.observation_result_status
        _ = seg.effective_date_of_reference_range
        _ = seg.user_defined_access_checks
        _ = seg.date_time_of_the_observation
        _ = seg.producers_id
        _ = seg.responsible_observer
        _ = seg.observation_method
        _ = seg.equipment_instance_identifier
        _ = seg.date_time_of_the_analysis
        _ = seg.observation_site
        _ = seg.observation_instance_identifier
        _ = seg.mood_code
        _ = seg.performing_organization_name
        _ = seg.performing_organization_address
        _ = seg.performing_organization_medical_director
        _ = seg.patient_results_release_category
        _ = seg.root_cause
        _ = seg.local_process_control
        _ = seg.observation_type
        _ = seg.observation_sub_type
        _ = seg.action_code
        _ = seg.observation_value_absent_reason
        _ = seg.observation_related_specimen_identifier

    def test_ods_attributes(self):
        seg = ODS()
        _ = seg.type_
        _ = seg.service_period
        _ = seg.diet_supplement_or_preference_code
        _ = seg.text_instruction

    def test_odt_attributes(self):
        seg = ODT()
        _ = seg.tray_type
        _ = seg.service_period
        _ = seg.text_instruction

    def test_oh1_attributes(self):
        seg = OH1()
        _ = seg.set_id
        _ = seg.action_code
        _ = seg.employment_status
        _ = seg.employment_status_start_date
        _ = seg.employment_status_end_date
        _ = seg.entered_date
        _ = seg.employment_status_unique_identifier

    def test_oh2_attributes(self):
        seg = OH2()
        _ = seg.set_id
        _ = seg.action_code
        _ = seg.entered_date
        _ = seg.occupation
        _ = seg.industry
        _ = seg.work_classification
        _ = seg.job_start_date
        _ = seg.job_end_date
        _ = seg.work_schedule
        _ = seg.average_hours_worked_per_day
        _ = seg.average_days_worked_per_week
        _ = seg.employer_organization
        _ = seg.employer_address
        _ = seg.supervisory_level
        _ = seg.job_duties
        _ = seg.occupational_hazards
        _ = seg.job_unique_identifier
        _ = seg.current_job_indicator

    def test_oh3_attributes(self):
        seg = OH3()
        _ = seg.set_id
        _ = seg.action_code
        _ = seg.occupation
        _ = seg.industry
        _ = seg.usual_occupation_duration_years
        _ = seg.start_year
        _ = seg.entered_date
        _ = seg.work_unique_identifier

    def test_oh4_attributes(self):
        seg = OH4()
        _ = seg.set_id
        _ = seg.action_code
        _ = seg.combat_zone_start_date
        _ = seg.combat_zone_end_date
        _ = seg.entered_date
        _ = seg.combat_zone_unique_identifier

    def test_om1_attributes(self):
        seg = OM1()
        _ = seg.sequence_number_test_observation_master_file
        _ = seg.producers_service_test_observation_id
        _ = seg.permitted_data_types
        _ = seg.specimen_required
        _ = seg.producer_id
        _ = seg.observation_description
        _ = seg.other_service_test_observation_i_ds_for_the_observation
        _ = seg.other_names
        _ = seg.preferred_report_name_for_the_observation
        _ = seg.preferred_short_name_or_mnemonic_for_the_observation
        _ = seg.preferred_long_name_for_the_observation
        _ = seg.orderability
        _ = seg.identity_of_instrument_used_to_perform_this_study
        _ = seg.coded_representation_of_method
        _ = seg.portable_device_indicator
        _ = seg.observation_producing_department_section
        _ = seg.telephone_number_of_section
        _ = seg.nature_of_service_test_observation
        _ = seg.report_subheader
        _ = seg.report_display_order
        _ = seg.date_time_stamp_for_any_change_in_definition_for_the_observation
        _ = seg.effective_date_time_of_change
        _ = seg.typical_turn_around_time
        _ = seg.processing_time
        _ = seg.processing_priority
        _ = seg.reporting_priority
        _ = seg.outside_sites_where_observation_may_be_performed
        _ = seg.address_of_outside_sites
        _ = seg.phone_number_of_outside_site
        _ = seg.confidentiality_code
        _ = seg.observations_required_to_interpret_this_observation
        _ = seg.interpretation_of_observations
        _ = seg.contraindications_to_observations
        _ = seg.reflex_tests_observations
        _ = seg.rules_that_trigger_reflex_testing
        _ = seg.fixed_canned_message
        _ = seg.patient_preparation
        _ = seg.procedure_medication
        _ = seg.factors_that_may_affect_the_observation
        _ = seg.service_test_observation_performance_schedule
        _ = seg.description_of_test_methods
        _ = seg.kind_of_quantity_observed
        _ = seg.point_versus_interval
        _ = seg.challenge_information
        _ = seg.relationship_modifier
        _ = seg.target_anatomic_site_of_test
        _ = seg.modality_of_imaging_measurement
        _ = seg.exclusive_test
        _ = seg.diagnostic_serv_sect_id
        _ = seg.taxonomic_classification_code
        _ = seg.other_names_51
        _ = seg.replacement_producers_service_test_observation_id
        _ = seg.prior_resuts_instructions
        _ = seg.special_instructions
        _ = seg.test_category
        _ = seg.observation_identifier_associated_with_producers_service_test_observation_id
        _ = seg.typical_turn_around_time_57
        _ = seg.gender_restriction
        _ = seg.age_restriction

    def test_om2_attributes(self):
        seg = OM2()
        _ = seg.sequence_number_test_observation_master_file
        _ = seg.units_of_measure
        _ = seg.range_of_decimal_precision
        _ = seg.corresponding_si_units_of_measure
        _ = seg.si_conversion_factor
        _ = seg.reference_normal_range_for_ordinal_and_continuous_observations
        _ = seg.critical_range_for_ordinal_and_continuous_observations
        _ = seg.absolute_range_for_ordinal_and_continuous_observations
        _ = seg.delta_check_criteria
        _ = seg.minimum_meaningful_increments

    def test_om3_attributes(self):
        seg = OM3()
        _ = seg.sequence_number_test_observation_master_file
        _ = seg.preferred_coding_system
        _ = seg.valid_coded_answers
        _ = seg.normal_text_codes_for_categorical_observations
        _ = seg.abnormal_text_codes_for_categorical_observations
        _ = seg.critical_text_codes_for_categorical_observations
        _ = seg.value_type

    def test_om4_attributes(self):
        seg = OM4()
        _ = seg.sequence_number_test_observation_master_file
        _ = seg.derived_specimen
        _ = seg.container_description
        _ = seg.container_volume
        _ = seg.container_units
        _ = seg.specimen
        _ = seg.additive
        _ = seg.preparation
        _ = seg.special_handling_requirements
        _ = seg.normal_collection_volume
        _ = seg.minimum_collection_volume
        _ = seg.specimen_requirements
        _ = seg.specimen_priorities
        _ = seg.specimen_retention_time
        _ = seg.specimen_handling_code
        _ = seg.specimen_preference
        _ = seg.preferred_specimen_attribture_sequence_id
        _ = seg.taxonomic_classification_code

    def test_om5_attributes(self):
        seg = OM5()
        _ = seg.sequence_number_test_observation_master_file
        _ = seg.test_observations_included_within_an_ordered_test_battery
        _ = seg.observation_id_suffixes

    def test_om6_attributes(self):
        seg = OM6()
        _ = seg.sequence_number_test_observation_master_file
        _ = seg.derivation_rule

    def test_om7_attributes(self):
        seg = OM7()
        _ = seg.sequence_number_test_observation_master_file
        _ = seg.universal_service_identifier
        _ = seg.category_identifier
        _ = seg.category_description
        _ = seg.category_synonym
        _ = seg.effective_test_service_start_date_time
        _ = seg.effective_test_service_end_date_time
        _ = seg.test_service_default_duration_quantity
        _ = seg.test_service_default_duration_units
        _ = seg.test_service_default_frequency
        _ = seg.consent_indicator
        _ = seg.consent_identifier
        _ = seg.consent_effective_start_date_time
        _ = seg.consent_effective_end_date_time
        _ = seg.consent_interval_quantity
        _ = seg.consent_interval_units
        _ = seg.consent_waiting_period_quantity
        _ = seg.consent_waiting_period_units
        _ = seg.effective_date_time_of_change
        _ = seg.entered_by
        _ = seg.orderable_at_location
        _ = seg.formulary_status
        _ = seg.special_order_indicator
        _ = seg.primary_key_value_cdm

    def test_omc_attributes(self):
        seg = OMC()
        _ = seg.sequence_number_test_observation_master_file
        _ = seg.segment_action_code
        _ = seg.segment_unique_key
        _ = seg.clinical_information_request
        _ = seg.collection_event_process_step
        _ = seg.communication_location
        _ = seg.answer_required
        _ = seg.hint_help_text
        _ = seg.type_of_answer
        _ = seg.multiple_answers_allowed
        _ = seg.answer_choices
        _ = seg.character_limit
        _ = seg.number_of_decimals

    def test_orc_attributes(self):
        seg = ORC()
        _ = seg.order_control
        _ = seg.placer_order_number
        _ = seg.filler_order_number
        _ = seg.placer_order_group_number
        _ = seg.order_status
        _ = seg.response_flag
        _ = seg.parent_order
        _ = seg.date_time_of_order_event
        _ = seg.enterers_location
        _ = seg.call_back_phone_number
        _ = seg.order_effective_date_time
        _ = seg.order_control_code_reason
        _ = seg.advanced_beneficiary_notice_code
        _ = seg.order_status_modifier
        _ = seg.advanced_beneficiary_notice_override_reason
        _ = seg.fillers_expected_availability_date_time
        _ = seg.confidentiality_code
        _ = seg.order_type
        _ = seg.enterer_authorization_mode
        _ = seg.advanced_beneficiary_notice_date
        _ = seg.alternate_placer_order_number
        _ = seg.order_workflow_profile
        _ = seg.action_code
        _ = seg.order_status_date_range
        _ = seg.order_creation_date_time
        _ = seg.filler_order_group_number

    def test_org_attributes(self):
        seg = ORG()
        _ = seg.set_id_org
        _ = seg.organization_unit_code
        _ = seg.organization_unit_type_code
        _ = seg.primary_org_unit_indicator
        _ = seg.practitioner_org_unit_identifier
        _ = seg.health_care_provider_type_code
        _ = seg.health_care_provider_classification_code
        _ = seg.health_care_provider_area_of_specialization_code
        _ = seg.effective_date_range
        _ = seg.employment_status_code
        _ = seg.board_approval_indicator
        _ = seg.primary_care_physician_indicator
        _ = seg.cost_center_code

    def test_ovr_attributes(self):
        seg = OVR()
        _ = seg.business_rule_override_type
        _ = seg.business_rule_override_code
        _ = seg.override_comments
        _ = seg.override_entered_by
        _ = seg.override_authorized_by

    def test_pac_attributes(self):
        seg = PAC()
        _ = seg.set_id_pac
        _ = seg.package_id
        _ = seg.parent_package_id
        _ = seg.position_in_parent_package
        _ = seg.package_type
        _ = seg.package_condition
        _ = seg.package_handling_code
        _ = seg.package_risk_code
        _ = seg.action_code

    def test_pce_attributes(self):
        seg = PCE()
        _ = seg.set_id_pce
        _ = seg.cost_center_account_number
        _ = seg.transaction_code
        _ = seg.transaction_amount_unit

    def test_pcr_attributes(self):
        seg = PCR()
        _ = seg.implicated_product
        _ = seg.generic_product
        _ = seg.product_class
        _ = seg.total_duration_of_therapy
        _ = seg.product_manufacture_date
        _ = seg.product_expiration_date
        _ = seg.product_implantation_date
        _ = seg.product_explantation_date
        _ = seg.single_use_device
        _ = seg.indication_for_product_use
        _ = seg.product_problem
        _ = seg.product_serial_lot_number
        _ = seg.product_available_for_inspection
        _ = seg.product_evaluation_performed
        _ = seg.product_evaluation_status
        _ = seg.product_evaluation_results
        _ = seg.evaluated_product_source
        _ = seg.date_product_returned_to_manufacturer
        _ = seg.device_operator_qualifications
        _ = seg.relatedness_assessment
        _ = seg.action_taken_in_response_to_the_event
        _ = seg.event_causality_observations
        _ = seg.indirect_exposure_mechanism

    def test_pd1_attributes(self):
        seg = PD1()
        _ = seg.living_dependency
        _ = seg.living_arrangement
        _ = seg.patient_primary_facility
        _ = seg.student_indicator
        _ = seg.handicap
        _ = seg.living_will_code
        _ = seg.organ_donor_code
        _ = seg.separate_bill
        _ = seg.duplicate_patient
        _ = seg.publicity_code
        _ = seg.protection_indicator
        _ = seg.protection_indicator_effective_date
        _ = seg.place_of_worship
        _ = seg.advance_directive_code
        _ = seg.immunization_registry_status
        _ = seg.immunization_registry_status_effective_date
        _ = seg.publicity_code_effective_date
        _ = seg.military_branch
        _ = seg.military_rank_grade
        _ = seg.military_status
        _ = seg.advance_directive_last_verified_date
        _ = seg.retirement_date

    def test_pda_attributes(self):
        seg = PDA()
        _ = seg.death_cause_code
        _ = seg.death_location
        _ = seg.death_certified_indicator
        _ = seg.death_certificate_signed_date_time
        _ = seg.death_certified_by
        _ = seg.autopsy_indicator
        _ = seg.autopsy_start_and_end_date_time
        _ = seg.autopsy_performed_by
        _ = seg.coroner_indicator

    def test_pdc_attributes(self):
        seg = PDC()
        _ = seg.manufacturer_distributor
        _ = seg.country
        _ = seg.brand_name
        _ = seg.device_family_name
        _ = seg.generic_name
        _ = seg.model_identifier
        _ = seg.catalogue_identifier
        _ = seg.other_identifier
        _ = seg.product_code
        _ = seg.marketing_basis
        _ = seg.marketing_approval_id
        _ = seg.labeled_shelf_life
        _ = seg.expected_shelf_life
        _ = seg.date_first_marketed
        _ = seg.date_last_marketed

    def test_peo_attributes(self):
        seg = PEO()
        _ = seg.event_identifiers_used
        _ = seg.event_symptom_diagnosis_code
        _ = seg.event_onset_date_time
        _ = seg.event_exacerbation_date_time
        _ = seg.event_improved_date_time
        _ = seg.event_ended_data_time
        _ = seg.event_location_occurred_address
        _ = seg.event_qualification
        _ = seg.event_serious
        _ = seg.event_expected
        _ = seg.event_outcome
        _ = seg.patient_outcome
        _ = seg.event_description_from_others
        _ = seg.event_description_from_original_reporter
        _ = seg.event_description_from_patient
        _ = seg.event_description_from_practitioner
        _ = seg.event_description_from_autopsy
        _ = seg.cause_of_death
        _ = seg.primary_observer_name
        _ = seg.primary_observer_address
        _ = seg.primary_observer_telephone
        _ = seg.primary_observers_qualification
        _ = seg.confirmation_provided_by
        _ = seg.primary_observer_aware_date_time
        _ = seg.primary_observers_identity_may_be_divulged

    def test_pes_attributes(self):
        seg = PES()
        _ = seg.sender_organization_name
        _ = seg.sender_individual_name
        _ = seg.sender_address
        _ = seg.sender_telephone
        _ = seg.sender_event_identifier
        _ = seg.sender_sequence_number
        _ = seg.sender_event_description
        _ = seg.sender_comment
        _ = seg.sender_aware_date_time
        _ = seg.event_report_date
        _ = seg.event_report_timing_type
        _ = seg.event_report_source
        _ = seg.event_reported_to

    def test_pid_attributes(self):
        seg = PID()
        _ = seg.set_id_pid
        _ = seg.patient_identifier_list
        _ = seg.patient_name
        _ = seg.mothers_maiden_name
        _ = seg.date_time_of_birth
        _ = seg.administrative_sex
        _ = seg.race
        _ = seg.patient_address
        _ = seg.primary_language
        _ = seg.marital_status
        _ = seg.religion
        _ = seg.patient_account_number
        _ = seg.mothers_identifier
        _ = seg.ethnic_group
        _ = seg.birth_place
        _ = seg.multiple_birth_indicator
        _ = seg.birth_order
        _ = seg.citizenship
        _ = seg.veterans_military_status
        _ = seg.patient_death_date_and_time
        _ = seg.patient_death_indicator
        _ = seg.identity_unknown_indicator
        _ = seg.identity_reliability_code
        _ = seg.last_update_date_time
        _ = seg.last_update_facility
        _ = seg.taxonomic_classification_code
        _ = seg.breed_code
        _ = seg.strain
        _ = seg.production_class_code
        _ = seg.tribal_citizenship
        _ = seg.patient_telecommunication_information

    def test_pkg_attributes(self):
        seg = PKG()
        _ = seg.set_id_pkg
        _ = seg.packaging_units
        _ = seg.default_order_unit_of_measure_indicator
        _ = seg.package_quantity
        _ = seg.price
        _ = seg.future_item_price
        _ = seg.future_item_price_effective_date
        _ = seg.global_trade_item_number
        _ = seg.contract_price
        _ = seg.quantity_of_each
        _ = seg.vendor_catalog_number

    def test_pm1_attributes(self):
        seg = PM1()
        _ = seg.health_plan_id
        _ = seg.insurance_company_id
        _ = seg.insurance_company_name
        _ = seg.insurance_company_address
        _ = seg.insurance_co_contact_person
        _ = seg.insurance_co_phone_number
        _ = seg.group_number
        _ = seg.group_name
        _ = seg.plan_effective_date
        _ = seg.plan_expiration_date
        _ = seg.patient_dob_required
        _ = seg.patient_gender_required
        _ = seg.patient_relationship_required
        _ = seg.patient_signature_required
        _ = seg.diagnosis_required
        _ = seg.service_required
        _ = seg.patient_name_required
        _ = seg.patient_address_required
        _ = seg.subscribers_name_required
        _ = seg.workmans_comp_indicator
        _ = seg.bill_type_required
        _ = seg.commercial_carrier_name_and_address_required
        _ = seg.policy_number_pattern
        _ = seg.group_number_pattern

    def test_pmt_attributes(self):
        seg = PMT()
        _ = seg.payment_remittance_advice_number
        _ = seg.payment_remittance_effective_date_time
        _ = seg.payment_remittance_expiration_date_time
        _ = seg.payment_method
        _ = seg.payment_remittance_date_time
        _ = seg.payment_remittance_amount
        _ = seg.check_number
        _ = seg.payee_bank_identification
        _ = seg.payee_transit_number
        _ = seg.payee_bank_account_id
        _ = seg.payment_organization
        _ = seg.esr_code_line

    def test_pr1_attributes(self):
        seg = PR1()
        _ = seg.set_id_pr1
        _ = seg.procedure_code
        _ = seg.procedure_date_time
        _ = seg.procedure_functional_type
        _ = seg.procedure_minutes
        _ = seg.anesthesia_code
        _ = seg.anesthesia_minutes
        _ = seg.consent_code
        _ = seg.procedure_priority
        _ = seg.associated_diagnosis_code
        _ = seg.procedure_code_modifier
        _ = seg.procedure_drg_type
        _ = seg.tissue_type_code
        _ = seg.procedure_identifier
        _ = seg.procedure_action_code
        _ = seg.drg_procedure_determination_status
        _ = seg.drg_procedure_relevance
        _ = seg.treating_organizational_unit
        _ = seg.respiratory_within_surgery
        _ = seg.parent_procedure_id

    def test_pra_attributes(self):
        seg = PRA()
        _ = seg.primary_key_value_pra
        _ = seg.practitioner_group
        _ = seg.practitioner_category
        _ = seg.provider_billing
        _ = seg.specialty
        _ = seg.practitioner_id_numbers
        _ = seg.privileges
        _ = seg.date_entered_practice
        _ = seg.institution
        _ = seg.date_left_practice
        _ = seg.government_reimbursement_billing_eligibility
        _ = seg.set_id_pra

    def test_prb_attributes(self):
        seg = PRB()
        _ = seg.action_code
        _ = seg.action_date_time
        _ = seg.problem_id
        _ = seg.problem_instance_id
        _ = seg.episode_of_care_id
        _ = seg.problem_list_priority
        _ = seg.problem_established_date_time
        _ = seg.anticipated_problem_resolution_date_time
        _ = seg.actual_problem_resolution_date_time
        _ = seg.problem_classification
        _ = seg.problem_management_discipline
        _ = seg.problem_persistence
        _ = seg.problem_confirmation_status
        _ = seg.problem_life_cycle_status
        _ = seg.problem_life_cycle_status_date_time
        _ = seg.problem_date_of_onset
        _ = seg.problem_onset_text
        _ = seg.problem_ranking
        _ = seg.certainty_of_problem
        _ = seg.probability_of_problem_0_1
        _ = seg.individual_awareness_of_problem
        _ = seg.problem_prognosis
        _ = seg.individual_awareness_of_prognosis
        _ = seg.family_significant_other_awareness_of_problem_prognosis
        _ = seg.security_sensitivity
        _ = seg.problem_severity
        _ = seg.problem_perspective
        _ = seg.mood_code

    def test_prc_attributes(self):
        seg = PRC()
        _ = seg.primary_key_value_prc
        _ = seg.facility_id_prc
        _ = seg.department
        _ = seg.valid_patient_classes
        _ = seg.price
        _ = seg.formula
        _ = seg.minimum_quantity
        _ = seg.maximum_quantity
        _ = seg.minimum_price
        _ = seg.maximum_price
        _ = seg.effective_start_date
        _ = seg.effective_end_date
        _ = seg.price_override_flag
        _ = seg.billing_category
        _ = seg.chargeable_flag
        _ = seg.active_inactive_flag
        _ = seg.cost
        _ = seg.charge_on_indicator

    def test_prd_attributes(self):
        seg = PRD()
        _ = seg.provider_role
        _ = seg.provider_name
        _ = seg.provider_address
        _ = seg.provider_location
        _ = seg.provider_communication_information
        _ = seg.preferred_method_of_contact
        _ = seg.provider_identifiers
        _ = seg.effective_start_date_of_provider_role
        _ = seg.effective_end_date_of_provider_role
        _ = seg.provider_organization_name_and_identifier
        _ = seg.provider_organization_address
        _ = seg.provider_organization_location_information
        _ = seg.provider_organization_communication_information
        _ = seg.provider_organization_method_of_contact

    def test_prt_attributes(self):
        seg = PRT()
        _ = seg.participation_instance_id
        _ = seg.action_code
        _ = seg.action_reason
        _ = seg.role_of_participation
        _ = seg.person
        _ = seg.person_provider_type
        _ = seg.organization_unit_type
        _ = seg.organization
        _ = seg.location
        _ = seg.device
        _ = seg.begin_date_time_arrival_time
        _ = seg.end_date_time_departure_time
        _ = seg.qualitative_duration
        _ = seg.address
        _ = seg.telecommunication_address
        _ = seg.udi_device_identifier
        _ = seg.device_manufacture_date
        _ = seg.device_expiry_date
        _ = seg.device_lot_number
        _ = seg.device_serial_number
        _ = seg.device_donation_identification
        _ = seg.device_type
        _ = seg.preferred_method_of_contact
        _ = seg.contact_identifiers

    def test_psg_attributes(self):
        seg = PSG()
        _ = seg.provider_product_service_group_number
        _ = seg.payer_product_service_group_number
        _ = seg.product_service_group_sequence_number
        _ = seg.adjudicate_as_group
        _ = seg.product_service_group_billed_amount
        _ = seg.product_service_group_description

    def test_psh_attributes(self):
        seg = PSH()
        _ = seg.report_type
        _ = seg.report_form_identifier
        _ = seg.report_date
        _ = seg.report_interval_start_date
        _ = seg.report_interval_end_date
        _ = seg.quantity_manufactured
        _ = seg.quantity_distributed
        _ = seg.quantity_distributed_method
        _ = seg.quantity_distributed_comment
        _ = seg.quantity_in_use
        _ = seg.quantity_in_use_method
        _ = seg.quantity_in_use_comment
        _ = seg.number_of_product_experience_reports_filed_by_facility
        _ = seg.number_of_product_experience_reports_filed_by_distributor

    def test_psl_attributes(self):
        seg = PSL()
        _ = seg.provider_product_service_line_item_number
        _ = seg.payer_product_service_line_item_number
        _ = seg.product_service_line_item_sequence_number
        _ = seg.provider_tracking_id
        _ = seg.payer_tracking_id
        _ = seg.product_service_line_item_status
        _ = seg.product_service_code
        _ = seg.product_service_code_modifier
        _ = seg.product_service_code_description
        _ = seg.product_service_effective_date
        _ = seg.product_service_expiration_date
        _ = seg.product_service_quantity
        _ = seg.product_service_unit_cost
        _ = seg.number_of_items_per_unit
        _ = seg.product_service_gross_amount
        _ = seg.product_service_billed_amount
        _ = seg.product_service_clarification_code_type
        _ = seg.product_service_clarification_code_value
        _ = seg.health_document_reference_identifier
        _ = seg.processing_consideration_code
        _ = seg.restricted_disclosure_indicator
        _ = seg.related_product_service_code_indicator
        _ = seg.product_service_amount_for_physician
        _ = seg.product_service_cost_factor
        _ = seg.cost_center
        _ = seg.billing_period
        _ = seg.days_without_billing
        _ = seg.session_no
        _ = seg.executing_physician_id
        _ = seg.responsible_physician_id
        _ = seg.role_executing_physician
        _ = seg.medical_role_executing_physician
        _ = seg.side_of_body
        _ = seg.number_of_t_ps_pp
        _ = seg.tp_value_pp
        _ = seg.internal_scaling_factor_pp
        _ = seg.external_scaling_factor_pp
        _ = seg.amount_pp
        _ = seg.number_of_t_ps_technical_part
        _ = seg.tp_value_technical_part
        _ = seg.internal_scaling_factor_technical_part
        _ = seg.external_scaling_factor_technical_part
        _ = seg.amount_technical_part
        _ = seg.total_amount_professional_part_technical_part
        _ = seg.vat_rate
        _ = seg.main_service
        _ = seg.validation
        _ = seg.comment

    def test_pss_attributes(self):
        seg = PSS()
        _ = seg.provider_product_service_section_number
        _ = seg.payer_product_service_section_number
        _ = seg.product_service_section_sequence_number
        _ = seg.billed_amount
        _ = seg.section_description_or_heading

    def test_pth_attributes(self):
        seg = PTH()
        _ = seg.action_code
        _ = seg.pathway_id
        _ = seg.pathway_instance_id
        _ = seg.pathway_established_date_time
        _ = seg.pathway_life_cycle_status
        _ = seg.change_pathway_life_cycle_status_date_time
        _ = seg.mood_code

    def test_pv1_attributes(self):
        seg = PV1()
        _ = seg.set_id_pv1
        _ = seg.patient_class
        _ = seg.assigned_patient_location
        _ = seg.admission_type
        _ = seg.preadmit_number
        _ = seg.prior_patient_location
        _ = seg.attending_doctor
        _ = seg.referring_doctor
        _ = seg.consulting_doctor
        _ = seg.hospital_service
        _ = seg.temporary_location
        _ = seg.preadmit_test_indicator
        _ = seg.re_admission_indicator
        _ = seg.admit_source
        _ = seg.ambulatory_status
        _ = seg.vip_indicator
        _ = seg.admitting_doctor
        _ = seg.patient_type
        _ = seg.visit_number
        _ = seg.financial_class
        _ = seg.charge_price_indicator
        _ = seg.courtesy_code
        _ = seg.credit_rating
        _ = seg.contract_code
        _ = seg.contract_effective_date
        _ = seg.contract_amount
        _ = seg.contract_period
        _ = seg.interest_code
        _ = seg.transfer_to_bad_debt_code
        _ = seg.transfer_to_bad_debt_date
        _ = seg.bad_debt_agency_code
        _ = seg.bad_debt_transfer_amount
        _ = seg.bad_debt_recovery_amount
        _ = seg.delete_account_indicator
        _ = seg.delete_account_date
        _ = seg.discharge_disposition
        _ = seg.discharged_to_location
        _ = seg.diet_type
        _ = seg.servicing_facility
        _ = seg.account_status
        _ = seg.pending_location
        _ = seg.prior_temporary_location
        _ = seg.admit_date_time
        _ = seg.discharge_date_time
        _ = seg.current_patient_balance
        _ = seg.total_charges
        _ = seg.total_adjustments
        _ = seg.total_payments
        _ = seg.alternate_visit_id
        _ = seg.visit_indicator
        _ = seg.service_episode_description
        _ = seg.service_episode_identifier

    def test_pv2_attributes(self):
        seg = PV2()
        _ = seg.prior_pending_location
        _ = seg.accommodation_code
        _ = seg.admit_reason
        _ = seg.transfer_reason
        _ = seg.patient_valuables
        _ = seg.patient_valuables_location
        _ = seg.visit_user_code
        _ = seg.expected_admit_date_time
        _ = seg.expected_discharge_date_time
        _ = seg.estimated_length_of_inpatient_stay
        _ = seg.actual_length_of_inpatient_stay
        _ = seg.visit_description
        _ = seg.referral_source_code
        _ = seg.previous_service_date
        _ = seg.employment_illness_related_indicator
        _ = seg.purge_status_code
        _ = seg.purge_status_date
        _ = seg.special_program_code
        _ = seg.retention_indicator
        _ = seg.expected_number_of_insurance_plans
        _ = seg.visit_publicity_code
        _ = seg.visit_protection_indicator
        _ = seg.clinic_organization_name
        _ = seg.patient_status_code
        _ = seg.visit_priority_code
        _ = seg.previous_treatment_date
        _ = seg.expected_discharge_disposition
        _ = seg.signature_on_file_date
        _ = seg.first_similar_illness_date
        _ = seg.patient_charge_adjustment_code
        _ = seg.recurring_service_code
        _ = seg.billing_media_code
        _ = seg.expected_surgery_date_and_time
        _ = seg.military_partnership_code
        _ = seg.military_non_availability_code
        _ = seg.newborn_baby_indicator
        _ = seg.baby_detained_indicator
        _ = seg.mode_of_arrival_code
        _ = seg.recreational_drug_use_code
        _ = seg.admission_level_of_care_code
        _ = seg.precaution_code
        _ = seg.patient_condition_code
        _ = seg.living_will_code
        _ = seg.organ_donor_code
        _ = seg.advance_directive_code
        _ = seg.patient_status_effective_date
        _ = seg.expected_loa_return_date_time
        _ = seg.expected_pre_admission_testing_date_time
        _ = seg.notify_clergy_code
        _ = seg.advance_directive_last_verified_date

    def test_pye_attributes(self):
        seg = PYE()
        _ = seg.set_id_pye
        _ = seg.payee_type
        _ = seg.payee_relationship_to_invoice_patient
        _ = seg.payee_identification_list
        _ = seg.payee_person_name
        _ = seg.payee_address
        _ = seg.payment_method

    def test_qak_attributes(self):
        seg = QAK()
        _ = seg.query_tag
        _ = seg.query_response_status
        _ = seg.message_query_name
        _ = seg.hit_count_total
        _ = seg.this_payload
        _ = seg.hits_remaining

    def test_qid_attributes(self):
        seg = QID()
        _ = seg.query_tag
        _ = seg.message_query_name

    def test_qpd_attributes(self):
        seg = QPD()
        _ = seg.message_query_name
        _ = seg.query_tag
        _ = seg.user_parameters_in_successive_fields

    def test_qri_attributes(self):
        seg = QRI()
        _ = seg.candidate_confidence
        _ = seg.match_reason_code
        _ = seg.algorithm_descriptor

    def test_rcp_attributes(self):
        seg = RCP()
        _ = seg.query_priority
        _ = seg.quantity_limited_request
        _ = seg.response_modality
        _ = seg.execution_and_delivery_time
        _ = seg.modify_indicator
        _ = seg.sort_by_field
        _ = seg.segment_group_inclusion

    def test_rdf_attributes(self):
        seg = RDF()
        _ = seg.number_of_columns_per_row
        _ = seg.column_description

    def test_rdt_attributes(self):
        seg = RDT()
        _ = seg.column_value

    def test_rel_attributes(self):
        seg = REL()
        _ = seg.set_id_rel
        _ = seg.relationship_type
        _ = seg.this_relationship_instance_identifier
        _ = seg.source_information_instance_identifier
        _ = seg.target_information_instance_identifier
        _ = seg.asserting_entity_instance_id
        _ = seg.asserting_person
        _ = seg.asserting_organization
        _ = seg.assertor_address
        _ = seg.assertor_contact
        _ = seg.assertion_date_range
        _ = seg.negation_indicator
        _ = seg.certainty_of_relationship
        _ = seg.priority_no
        _ = seg.priority_sequence_no_rel_preference_for_consideration
        _ = seg.separability_indicator
        _ = seg.source_information_instance_object_type
        _ = seg.target_information_instance_object_type

    def test_rf1_attributes(self):
        seg = RF1()
        _ = seg.referral_status
        _ = seg.referral_priority
        _ = seg.referral_type
        _ = seg.referral_disposition
        _ = seg.referral_category
        _ = seg.originating_referral_identifier
        _ = seg.effective_date
        _ = seg.expiration_date
        _ = seg.process_date
        _ = seg.referral_reason
        _ = seg.external_referral_identifier
        _ = seg.referral_documentation_completion_status
        _ = seg.planned_treatment_stop_date
        _ = seg.referral_reason_text
        _ = seg.number_of_authorized_treatments_units
        _ = seg.number_of_used_treatments_units
        _ = seg.number_of_schedule_treatments_units
        _ = seg.remaining_benefit_amount
        _ = seg.authorized_provider
        _ = seg.authorized_health_professional
        _ = seg.source_text
        _ = seg.source_date
        _ = seg.source_phone
        _ = seg.comment
        _ = seg.action_code

    def test_rfi_attributes(self):
        seg = RFI()
        _ = seg.request_date
        _ = seg.response_due_date
        _ = seg.patient_consent
        _ = seg.date_additional_information_was_submitted

    def test_rgs_attributes(self):
        seg = RGS()
        _ = seg.set_id_rgs
        _ = seg.segment_action_code
        _ = seg.resource_group_id

    def test_rmi_attributes(self):
        seg = RMI()
        _ = seg.risk_management_incident_code
        _ = seg.date_time_incident
        _ = seg.incident_type_code

    def test_rq1_attributes(self):
        seg = RQ1()
        _ = seg.anticipated_price
        _ = seg.manufacturer_identifier
        _ = seg.manufacturers_catalog
        _ = seg.vendor_id
        _ = seg.vendor_catalog
        _ = seg.taxable
        _ = seg.substitute_allowed

    def test_rqd_attributes(self):
        seg = RQD()
        _ = seg.requisition_line_number
        _ = seg.item_code_internal
        _ = seg.item_code_external
        _ = seg.hospital_item_code
        _ = seg.requisition_quantity
        _ = seg.requisition_unit_of_measure
        _ = seg.cost_center_account_number
        _ = seg.item_natural_account_code
        _ = seg.deliver_to_id
        _ = seg.date_needed

    def test_rxa_attributes(self):
        seg = RXA()
        _ = seg.give_sub_id_counter
        _ = seg.administration_sub_id_counter
        _ = seg.date_time_start_of_administration
        _ = seg.date_time_end_of_administration
        _ = seg.administered_code
        _ = seg.administered_amount
        _ = seg.administered_units
        _ = seg.administered_dosage_form
        _ = seg.administration_notes
        _ = seg.administering_provider
        _ = seg.administered_per_time_unit
        _ = seg.administered_strength
        _ = seg.administered_strength_units
        _ = seg.substance_lot_number
        _ = seg.substance_expiration_date
        _ = seg.substance_manufacturer_name
        _ = seg.substance_treatment_refusal_reason
        _ = seg.indication
        _ = seg.completion_status
        _ = seg.action_code_rxa
        _ = seg.system_entry_date_time
        _ = seg.administered_drug_strength_volume
        _ = seg.administered_drug_strength_volume_units
        _ = seg.administered_barcode_identifier
        _ = seg.pharmacy_order_type
        _ = seg.administer_at
        _ = seg.administered_at_address
        _ = seg.administered_tag_identifier

    def test_rxc_attributes(self):
        seg = RXC()
        _ = seg.rx_component_type
        _ = seg.component_code
        _ = seg.component_amount
        _ = seg.component_units
        _ = seg.component_strength
        _ = seg.component_strength_units
        _ = seg.supplementary_code
        _ = seg.component_drug_strength_volume
        _ = seg.component_drug_strength_volume_units
        _ = seg.dispense_amount
        _ = seg.dispense_units

    def test_rxd_attributes(self):
        seg = RXD()
        _ = seg.dispense_sub_id_counter
        _ = seg.dispense_give_code
        _ = seg.date_time_dispensed
        _ = seg.actual_dispense_amount
        _ = seg.actual_dispense_units
        _ = seg.actual_dosage_form
        _ = seg.prescription_number
        _ = seg.number_of_refills_remaining
        _ = seg.dispense_notes
        _ = seg.dispensing_provider
        _ = seg.substitution_status
        _ = seg.total_daily_dose
        _ = seg.needs_human_review
        _ = seg.special_dispensing_instructions
        _ = seg.actual_strength
        _ = seg.actual_strength_unit
        _ = seg.substance_lot_number
        _ = seg.substance_expiration_date
        _ = seg.substance_manufacturer_name
        _ = seg.indication
        _ = seg.dispense_package_size
        _ = seg.dispense_package_size_unit
        _ = seg.dispense_package_method
        _ = seg.supplementary_code
        _ = seg.initiating_location
        _ = seg.packaging_assembly_location
        _ = seg.actual_drug_strength_volume
        _ = seg.actual_drug_strength_volume_units
        _ = seg.dispense_to_pharmacy
        _ = seg.dispense_to_pharmacy_address
        _ = seg.pharmacy_order_type
        _ = seg.dispense_type
        _ = seg.pharmacy_phone_number
        _ = seg.dispense_tag_identifier

    def test_rxe_attributes(self):
        seg = RXE()
        _ = seg.give_code
        _ = seg.give_amount_minimum
        _ = seg.give_amount_maximum
        _ = seg.give_units
        _ = seg.give_dosage_form
        _ = seg.providers_administration_instructions
        _ = seg.substitution_status
        _ = seg.dispense_amount
        _ = seg.dispense_units
        _ = seg.number_of_refills
        _ = seg.ordering_providers_dea_number
        _ = seg.pharmacist_treatment_suppliers_verifier_id
        _ = seg.prescription_number
        _ = seg.number_of_refills_remaining
        _ = seg.number_of_refills_doses_dispensed
        _ = seg.dt_of_most_recent_refill_or_dose_dispensed
        _ = seg.total_daily_dose
        _ = seg.needs_human_review
        _ = seg.special_dispensing_instructions
        _ = seg.give_per_time_unit
        _ = seg.give_rate_amount
        _ = seg.give_rate_units
        _ = seg.give_strength
        _ = seg.give_strength_units
        _ = seg.give_indication
        _ = seg.dispense_package_size
        _ = seg.dispense_package_size_unit
        _ = seg.dispense_package_method
        _ = seg.supplementary_code
        _ = seg.original_order_date_time
        _ = seg.give_drug_strength_volume
        _ = seg.give_drug_strength_volume_units
        _ = seg.controlled_substance_schedule
        _ = seg.formulary_status
        _ = seg.pharmaceutical_substance_alternative
        _ = seg.pharmacy_of_most_recent_fill
        _ = seg.initial_dispense_amount
        _ = seg.dispensing_pharmacy
        _ = seg.dispensing_pharmacy_address
        _ = seg.deliver_to_patient_location
        _ = seg.deliver_to_address
        _ = seg.pharmacy_order_type
        _ = seg.pharmacy_phone_number

    def test_rxg_attributes(self):
        seg = RXG()
        _ = seg.give_sub_id_counter
        _ = seg.dispense_sub_id_counter
        _ = seg.give_code
        _ = seg.give_amount_minimum
        _ = seg.give_amount_maximum
        _ = seg.give_units
        _ = seg.give_dosage_form
        _ = seg.administration_notes
        _ = seg.substitution_status
        _ = seg.needs_human_review
        _ = seg.special_administration_instructions
        _ = seg.give_per_time_unit
        _ = seg.give_rate_amount
        _ = seg.give_rate_units
        _ = seg.give_strength
        _ = seg.give_strength_units
        _ = seg.substance_lot_number
        _ = seg.substance_expiration_date
        _ = seg.substance_manufacturer_name
        _ = seg.indication
        _ = seg.give_drug_strength_volume
        _ = seg.give_drug_strength_volume_units
        _ = seg.give_barcode_identifier
        _ = seg.pharmacy_order_type
        _ = seg.deliver_to_patient_location
        _ = seg.deliver_to_address
        _ = seg.give_tag_identifier
        _ = seg.dispense_amount
        _ = seg.dispense_units

    def test_rxo_attributes(self):
        seg = RXO()
        _ = seg.requested_give_code
        _ = seg.requested_give_amount_minimum
        _ = seg.requested_give_amount_maximum
        _ = seg.requested_give_units
        _ = seg.requested_dosage_form
        _ = seg.providers_pharmacy_treatment_instructions
        _ = seg.providers_administration_instructions
        _ = seg.allow_substitutions
        _ = seg.requested_dispense_code
        _ = seg.requested_dispense_amount
        _ = seg.requested_dispense_units
        _ = seg.number_of_refills
        _ = seg.pharmacist_treatment_suppliers_verifier_id
        _ = seg.needs_human_review
        _ = seg.requested_give_per_time_unit
        _ = seg.requested_give_strength
        _ = seg.requested_give_strength_units
        _ = seg.indication
        _ = seg.requested_give_rate_amount
        _ = seg.requested_give_rate_units
        _ = seg.total_daily_dose
        _ = seg.supplementary_code
        _ = seg.requested_drug_strength_volume
        _ = seg.requested_drug_strength_volume_units
        _ = seg.pharmacy_order_type
        _ = seg.dispensing_interval
        _ = seg.medication_instance_identifier
        _ = seg.segment_instance_identifier
        _ = seg.mood_code
        _ = seg.dispensing_pharmacy
        _ = seg.dispensing_pharmacy_address
        _ = seg.deliver_to_patient_location
        _ = seg.deliver_to_address
        _ = seg.pharmacy_phone_number

    def test_rxr_attributes(self):
        seg = RXR()
        _ = seg.route
        _ = seg.administration_site
        _ = seg.administration_device
        _ = seg.administration_method
        _ = seg.routing_instruction
        _ = seg.administration_site_modifier

    def test_rxv_attributes(self):
        seg = RXV()
        _ = seg.set_id_rxv
        _ = seg.bolus_type
        _ = seg.bolus_dose_amount
        _ = seg.bolus_dose_amount_units
        _ = seg.bolus_dose_volume
        _ = seg.bolus_dose_volume_units
        _ = seg.pca_type
        _ = seg.pca_dose_amount
        _ = seg.pca_dose_amount_units
        _ = seg.pca_dose_amount_volume
        _ = seg.pca_dose_amount_volume_units
        _ = seg.max_dose_amount
        _ = seg.max_dose_amount_units
        _ = seg.max_dose_amount_volume
        _ = seg.max_dose_amount_volume_units
        _ = seg.max_dose_per_time
        _ = seg.lockout_interval
        _ = seg.syringe_manufacturer
        _ = seg.syringe_model_number
        _ = seg.syringe_size
        _ = seg.syringe_size_units
        _ = seg.action_code

    def test_sac_attributes(self):
        seg = SAC()
        _ = seg.external_accession_identifier
        _ = seg.accession_identifier
        _ = seg.container_identifier
        _ = seg.primary_parent_container_identifier
        _ = seg.equipment_container_identifier
        _ = seg.registration_date_time
        _ = seg.container_status
        _ = seg.carrier_type
        _ = seg.carrier_identifier
        _ = seg.position_in_carrier
        _ = seg.tray_type_sac
        _ = seg.tray_identifier
        _ = seg.position_in_tray
        _ = seg.location
        _ = seg.container_height
        _ = seg.container_diameter
        _ = seg.barrier_delta
        _ = seg.bottom_delta
        _ = seg.container_height_diameter_delta_units
        _ = seg.container_volume
        _ = seg.available_specimen_volume
        _ = seg.initial_specimen_volume
        _ = seg.volume_units
        _ = seg.separator_type
        _ = seg.cap_type
        _ = seg.additive
        _ = seg.specimen_component
        _ = seg.dilution_factor
        _ = seg.treatment
        _ = seg.temperature
        _ = seg.hemolysis_index
        _ = seg.hemolysis_index_units
        _ = seg.lipemia_index
        _ = seg.lipemia_index_units
        _ = seg.icterus_index
        _ = seg.icterus_index_units
        _ = seg.fibrin_index
        _ = seg.fibrin_index_units
        _ = seg.system_induced_contaminants
        _ = seg.drug_interference
        _ = seg.artificial_blood
        _ = seg.special_handling_code
        _ = seg.other_environmental_factors
        _ = seg.container_length
        _ = seg.container_width
        _ = seg.container_form
        _ = seg.container_material
        _ = seg.container_common_name

    def test_scd_attributes(self):
        seg = SCD()
        _ = seg.cycle_start_time
        _ = seg.cycle_count
        _ = seg.temp_max
        _ = seg.temp_min
        _ = seg.load_number
        _ = seg.condition_time
        _ = seg.sterilize_time
        _ = seg.exhaust_time
        _ = seg.total_cycle_time
        _ = seg.device_status
        _ = seg.cycle_start_date_time
        _ = seg.dry_time
        _ = seg.leak_rate
        _ = seg.control_temperature
        _ = seg.sterilizer_temperature
        _ = seg.cycle_complete_time
        _ = seg.under_temperature
        _ = seg.over_temperature
        _ = seg.abort_cycle
        _ = seg.alarm
        _ = seg.long_in_charge_phase
        _ = seg.long_in_exhaust_phase
        _ = seg.long_in_fast_exhaust_phase
        _ = seg.reset
        _ = seg.operator_unload
        _ = seg.door_open
        _ = seg.reading_failure
        _ = seg.cycle_type
        _ = seg.thermal_rinse_time
        _ = seg.wash_time
        _ = seg.injection_rate
        _ = seg.procedure_code
        _ = seg.patient_identifier_list
        _ = seg.attending_doctor
        _ = seg.dilution_factor
        _ = seg.fill_time
        _ = seg.inlet_temperature

    def test_sch_attributes(self):
        seg = SCH()
        _ = seg.placer_appointment_id
        _ = seg.filler_appointment_id
        _ = seg.occurrence_number
        _ = seg.placer_order_group_number
        _ = seg.schedule_id
        _ = seg.event_reason
        _ = seg.appointment_reason
        _ = seg.appointment_type
        _ = seg.appointment_duration_units
        _ = seg.placer_contact_person
        _ = seg.placer_contact_phone_number
        _ = seg.placer_contact_address
        _ = seg.placer_contact_location
        _ = seg.filler_contact_person
        _ = seg.filler_contact_phone_number
        _ = seg.filler_contact_address
        _ = seg.filler_contact_location
        _ = seg.entered_by_person
        _ = seg.entered_by_phone_number
        _ = seg.entered_by_location
        _ = seg.parent_placer_appointment_id
        _ = seg.parent_filler_appointment_id
        _ = seg.filler_status_code
        _ = seg.placer_order_number
        _ = seg.filler_order_number
        _ = seg.alternate_placer_order_group_number

    def test_scp_attributes(self):
        seg = SCP()
        _ = seg.number_of_decontamination_sterilization_devices
        _ = seg.labor_calculation_type
        _ = seg.date_format
        _ = seg.device_number
        _ = seg.device_name
        _ = seg.device_model_name
        _ = seg.device_type
        _ = seg.lot_control

    def test_sdd_attributes(self):
        seg = SDD()
        _ = seg.lot_number
        _ = seg.device_number
        _ = seg.device_name
        _ = seg.device_data_state
        _ = seg.load_status
        _ = seg.control_code
        _ = seg.operator_name

    def test_sft_attributes(self):
        seg = SFT()
        _ = seg.software_vendor_organization
        _ = seg.software_certified_version_or_release_number
        _ = seg.software_product_name
        _ = seg.software_binary_id
        _ = seg.software_product_information
        _ = seg.software_install_date

    def test_sgh_attributes(self):
        seg = SGH()
        _ = seg.set_id_sgh
        _ = seg.segment_group_name

    def test_sgt_attributes(self):
        seg = SGT()
        _ = seg.set_id_sgt
        _ = seg.segment_group_name

    def test_shp_attributes(self):
        seg = SHP()
        _ = seg.shipment_id
        _ = seg.internal_shipment_id
        _ = seg.shipment_status
        _ = seg.shipment_status_date_time
        _ = seg.shipment_status_reason
        _ = seg.shipment_priority
        _ = seg.shipment_confidentiality
        _ = seg.number_of_packages_in_shipment
        _ = seg.shipment_condition
        _ = seg.shipment_handling_code
        _ = seg.shipment_risk_code
        _ = seg.action_code

    def test_sid_attributes(self):
        seg = SID()
        _ = seg.application_method_identifier
        _ = seg.substance_lot_number
        _ = seg.substance_container_identifier
        _ = seg.substance_manufacturer_identifier

    def test_slt_attributes(self):
        seg = SLT()
        _ = seg.device_number
        _ = seg.device_name
        _ = seg.lot_number
        _ = seg.item_identifier
        _ = seg.bar_code

    def test_spm_attributes(self):
        seg = SPM()
        _ = seg.set_id_spm
        _ = seg.specimen_identifier
        _ = seg.specimen_parent_i_ds
        _ = seg.specimen_type
        _ = seg.specimen_type_modifier
        _ = seg.specimen_additives
        _ = seg.specimen_collection_method
        _ = seg.specimen_source_site
        _ = seg.specimen_source_site_modifier
        _ = seg.specimen_collection_site
        _ = seg.specimen_role
        _ = seg.specimen_collection_amount
        _ = seg.grouped_specimen_count
        _ = seg.specimen_description
        _ = seg.specimen_handling_code
        _ = seg.specimen_risk_code
        _ = seg.specimen_collection_date_time
        _ = seg.specimen_received_date_time
        _ = seg.specimen_expiration_date_time
        _ = seg.specimen_availability
        _ = seg.specimen_reject_reason
        _ = seg.specimen_quality
        _ = seg.specimen_appropriateness
        _ = seg.specimen_condition
        _ = seg.specimen_current_quantity
        _ = seg.number_of_specimen_containers
        _ = seg.container_type
        _ = seg.container_condition
        _ = seg.specimen_child_role
        _ = seg.accession_id
        _ = seg.other_specimen_id
        _ = seg.shipment_id
        _ = seg.culture_start_date_time
        _ = seg.culture_final_date_time
        _ = seg.action_code

    def test_stf_attributes(self):
        seg = STF()
        _ = seg.primary_key_value_stf
        _ = seg.staff_identifier_list
        _ = seg.staff_name
        _ = seg.staff_type
        _ = seg.administrative_sex
        _ = seg.date_time_of_birth
        _ = seg.active_inactive_flag
        _ = seg.department
        _ = seg.hospital_service_stf
        _ = seg.phone
        _ = seg.office_home_address_birthplace
        _ = seg.institution_activation_date
        _ = seg.institution_inactivation_date
        _ = seg.backup_person_id
        _ = seg.e_mail_address
        _ = seg.preferred_method_of_contact
        _ = seg.marital_status
        _ = seg.job_title
        _ = seg.job_code_class
        _ = seg.employment_status_code
        _ = seg.additional_insured_on_auto
        _ = seg.drivers_license_number_staff
        _ = seg.copy_auto_ins
        _ = seg.auto_ins_expires
        _ = seg.date_last_dmv_review
        _ = seg.date_next_dmv_review
        _ = seg.race
        _ = seg.ethnic_group
        _ = seg.re_activation_approval_indicator
        _ = seg.citizenship
        _ = seg.date_time_of_death
        _ = seg.death_indicator
        _ = seg.institution_relationship_type_code
        _ = seg.institution_relationship_period
        _ = seg.expected_return_date
        _ = seg.cost_center_code
        _ = seg.generic_classification_indicator
        _ = seg.inactive_reason_code
        _ = seg.generic_resource_type_or_category
        _ = seg.religion
        _ = seg.signature

    def test_stz_attributes(self):
        seg = STZ()
        _ = seg.sterilization_type
        _ = seg.sterilization_cycle
        _ = seg.maintenance_cycle
        _ = seg.maintenance_type

    def test_tcc_attributes(self):
        seg = TCC()
        _ = seg.universal_service_identifier
        _ = seg.equipment_test_application_identifier
        _ = seg.auto_dilution_factor_default
        _ = seg.rerun_dilution_factor_default
        _ = seg.pre_dilution_factor_default
        _ = seg.endogenous_content_of_pre_dilution_diluent
        _ = seg.inventory_limits_warning_level
        _ = seg.automatic_rerun_allowed
        _ = seg.automatic_repeat_allowed
        _ = seg.automatic_reflex_allowed
        _ = seg.equipment_dynamic_range
        _ = seg.units
        _ = seg.processing_type
        _ = seg.test_criticality

    def test_tcd_attributes(self):
        seg = TCD()
        _ = seg.universal_service_identifier
        _ = seg.auto_dilution_factor
        _ = seg.rerun_dilution_factor
        _ = seg.pre_dilution_factor
        _ = seg.endogenous_content_of_pre_dilution_diluent
        _ = seg.automatic_repeat_allowed
        _ = seg.reflex_allowed
        _ = seg.analyte_repeat_status
        _ = seg.specimen_consumption_quantity
        _ = seg.pool_size
        _ = seg.auto_dilution_type

    def test_tq1_attributes(self):
        seg = TQ1()
        _ = seg.set_id_tq1
        _ = seg.quantity
        _ = seg.repeat_pattern
        _ = seg.explicit_time
        _ = seg.relative_time_and_units
        _ = seg.service_duration
        _ = seg.start_datetime
        _ = seg.end_datetime
        _ = seg.priority
        _ = seg.condition_text
        _ = seg.text_instruction
        _ = seg.conjunction
        _ = seg.occurrence_duration
        _ = seg.total_occurrences

    def test_tq2_attributes(self):
        seg = TQ2()
        _ = seg.set_id_tq2
        _ = seg.sequence_results_flag
        _ = seg.related_placer_number
        _ = seg.related_filler_number
        _ = seg.related_placer_group_number
        _ = seg.sequence_condition_code
        _ = seg.cyclic_entry_exit_indicator
        _ = seg.sequence_condition_time_interval
        _ = seg.cyclic_group_maximum_number_of_repeats
        _ = seg.special_service_request_relationship

    def test_txa_attributes(self):
        seg = TXA()
        _ = seg.set_id_txa
        _ = seg.document_type
        _ = seg.document_content_presentation
        _ = seg.activity_date_time
        _ = seg.primary_activity_provider_code_name
        _ = seg.origination_date_time
        _ = seg.transcription_date_time
        _ = seg.edit_date_time
        _ = seg.originator_code_name
        _ = seg.assigned_document_authenticator
        _ = seg.transcriptionist_code_name
        _ = seg.unique_document_number
        _ = seg.parent_document_number
        _ = seg.placer_order_number
        _ = seg.filler_order_number
        _ = seg.unique_document_file_name
        _ = seg.document_completion_status
        _ = seg.document_confidentiality_status
        _ = seg.document_availability_status
        _ = seg.document_storage_status
        _ = seg.document_change_reason
        _ = seg.authentication_person_time_stamp_set
        _ = seg.distributed_copies_code_and_name_of_recipients
        _ = seg.folder_assignment
        _ = seg.document_title
        _ = seg.agreed_due_date_time
        _ = seg.creating_facility
        _ = seg.creating_specialty

    def test_uac_attributes(self):
        seg = UAC()
        _ = seg.user_authentication_credential_type_code
        _ = seg.user_authentication_credential

    def test_ub2_attributes(self):
        seg = UB2()
        _ = seg.set_id_ub2
        _ = seg.co_insurance_days_9
        _ = seg.condition_code_24_30
        _ = seg.covered_days_7
        _ = seg.non_covered_days_8
        _ = seg.value_amount_code_39_41
        _ = seg.occurrence_code_date_32_35
        _ = seg.occurrence_span_code_dates_36
        _ = seg.uniform_billing_locator_2_state
        _ = seg.uniform_billing_locator_11_state
        _ = seg.uniform_billing_locator_31_national
        _ = seg.document_control_number
        _ = seg.uniform_billing_locator_49_national
        _ = seg.uniform_billing_locator_56_state
        _ = seg.uniform_billing_locator_57_sational
        _ = seg.uniform_billing_locator_78_state
        _ = seg.special_visit_count

    def test_var_attributes(self):
        seg = VAR()
        _ = seg.variance_instance_id
        _ = seg.documented_date_time
        _ = seg.stated_variance_date_time
        _ = seg.variance_originator
        _ = seg.variance_classification
        _ = seg.variance_description

    def test_vnd_attributes(self):
        seg = VND()
        _ = seg.set_id_vnd
        _ = seg.vendor_identifier
        _ = seg.vendor_name
        _ = seg.vendor_catalog_number
        _ = seg.primary_vendor_indicator
        _ = seg.corporation
        _ = seg.primary_contact
        _ = seg.contract_adjustment
        _ = seg.associated_contract_id
        _ = seg.class_of_trade
        _ = seg.pricing_tier_level

    def test_zl7_attributes(self):
        seg = ZL7()
        _ = seg.display_sort_key
        _ = seg.display_sort_key_2
