# -*- coding: utf-8 -*-

from __future__ import annotations

from zato.hl7v2 import parse_message
from zato.hl7v2.v2_9.groups import OrmO01Order, OrmO01Patient
from zato.hl7v2.v2_9.messages import ORM_O01
from zato.hl7v2.v2_9.segments import DG1, MSH, OBR, ORC, PID, PV1
from zato.hl7v2.v2_9.datatypes import CWE, CX, MSG, PL, XAD, XCN, XPN

from zato.hl7v2.testing.live_util import load_message, md_path_for

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ar', 'ar-agfa-enterprise.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01:
    """ Based on live/ar/ar-agfa-enterprise.md, message no. 1
    """

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = 'HIS_HIGA'
        msh.sending_facility = 'HIGA_SAN_MARTIN'
        msh.receiving_application = 'AGFA_EI'
        msh.receiving_facility = 'HIGA_SAN_MARTIN_RAD'
        msh.date_time_of_message = '20250312091500'

        message_type = MSG()
        message_type.message_code = 'ORM'
        message_type.trigger_event = 'O01'
        message_type.message_structure = 'ORM_O01'
        msh.message_type = message_type

        msh.message_control_id = 'MSG00001'
        msh.processing_id = 'P'
        msh.version_id = '2.5'
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'

        patient_id = CX()
        patient_id.id_number = '28456712'
        patient_id.assigning_authority = 'RENAPER'
        patient_id.identifier_type_code = 'NI'
        pid.patient_identifier_list = patient_id

        patient_name = XPN()
        patient_name.family_name = 'GARCIA'
        patient_name.given_name = 'MARIA ELENA'
        pid.patient_name = patient_name

        pid.date_time_of_birth = '19780315'
        pid.administrative_sex = 'F'

        patient_address = XAD()
        patient_address.street_address = 'AV CENTENARIO 1250'
        patient_address.city = 'LA PLATA'
        patient_address.state_or_province = 'BUENOS AIRES'
        patient_address.zip_or_postal_code = '1900'
        patient_address.country = 'AR'
        pid.patient_address = patient_address

        pid.pid_13 = '0221-4523890'  # Retired in v2.9, no semantic name
        pid.patient_account_number = '28456712'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = 'O'

        patient_location = PL()
        patient_location.point_of_care = 'RAD'
        patient_location.room = '001'
        patient_location.bed = '01'
        pv1.assigned_patient_location = patient_location

        attending_doctor = XCN()
        attending_doctor.person_identifier = '34567890'
        attending_doctor.family_name = 'FERNANDEZ'
        attending_doctor.given_name = 'CARLOS'
        attending_doctor.prefix = 'DR'
        pv1.attending_doctor = attending_doctor

        pv1.hospital_service = 'RAD'
        pv1.patient_type = 'V00012345'
        pv1.prior_temporary_location = '20250312'

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = 'ORD-2025-00891'
        orc.orc_7 = '1^^^20250312091500^^R'  # Retired in v2.9, no semantic name
        orc.date_time_of_order_event = '20250312091500'

        orc_entered_by = XCN()
        orc_entered_by.person_identifier = '34567890'
        orc_entered_by.family_name = 'FERNANDEZ'
        orc_entered_by.given_name = 'CARLOS'
        orc_entered_by.prefix = 'DR'
        orc.orc_10 = orc_entered_by  # Retired in v2.9, no semantic name

        orc_ordering_provider = XCN()
        orc_ordering_provider.person_identifier = '34567890'
        orc_ordering_provider.family_name = 'FERNANDEZ'
        orc_ordering_provider.given_name = 'CARLOS'
        orc_ordering_provider.prefix = 'DR'
        orc.orc_12 = orc_ordering_provider  # Retired in v2.9, no semantic name

        orc.enterers_location = 'RAD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = 'ORD-2025-00891'

        service_identifier = CWE()
        service_identifier.identifier = '74177'
        service_identifier.text = 'CT ABDOMEN AND PELVIS WITH CONTRAST'
        service_identifier.name_of_coding_system = 'CPT'
        obr.universal_service_identifier = service_identifier

        obr.observation_date_time = '20250312091500'

        obr_ordering_provider = XCN()
        obr_ordering_provider.person_identifier = '34567890'
        obr_ordering_provider.family_name = 'FERNANDEZ'
        obr_ordering_provider.given_name = 'CARLOS'
        obr_ordering_provider.prefix = 'DR'
        obr.obr_15 = obr_ordering_provider  # Retired in v2.9, no semantic name

        obr.result_status = '1^^^20250312091500^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'

        diagnosis_code = CWE()
        diagnosis_code.identifier = 'R10.9'
        diagnosis_code.text = 'DOLOR ABDOMINAL NO ESPECIFICADO'
        diagnosis_code.name_of_coding_system = 'ICD10AR'
        dg1.diagnosis_code_dg1 = diagnosis_code

        dg1.diagnosis_type = 'A'

        patient = OrmO01Patient()
        patient.pid = pid
        patient.pv1 = pv1

        order = OrmO01Order()
        order.orc = orc
        order.obr = obr
        order.dg1 = dg1

        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 1)

        assert built_er7 == expected_er7

# ################################################################################################################################
# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 1)

        # Parse ..
        parsed = parse_message(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_message(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        assert serialized == reparsed.to_hl7v2()

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        assert parsed_dict == reparsed_dict

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        assert parsed_dict_full == reparsed_dict_full

# ################################################################################################################################
# ################################################################################################################################
