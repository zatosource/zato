# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.hl7v2 import parse_hl7
from zato.hl7v2.testing.live_util import load_message, md_path_for
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, EIP, HD, MSG, PL, PT, VID, XAD, XCN, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, AdtA05Insurance, AdtA05NextOfKin, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, \
    OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A05, ORM_O01, ORU_R01, REF_I12
from zato.hl7v2.v2_9.segments import DG1, EVN, IN1, MSH, NK1, NTE, OBR, OBX, ORC, PID, PRD, PV1, RF1

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('au', 'au-medicaldirector.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/au/au-medicaldirector.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='QML_PATHOLOGY')
        msh.sending_facility = HD(hd_1='QML', hd_2='2184', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='MEDICALDIRECTOR')
        msh.receiving_facility = HD(hd_1='GREENSLOPES FAMILY PRACTICE')
        msh.date_time_of_message = '20250314090000+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT20251001', cx_4='QML', cx_5='MR'), CX(cx_1='6789012345', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='NGUYEN', xpn_2='LINH', xpn_3='THI')
        pid.date_time_of_birth = '19870315'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='42 Caxton St', xad_3='PADDINGTON', xad_4='QLD', xad_5='4064', xad_6='AU')
        pid.pid_13 = '0412345678'
        pid.patient_account_number = CX(cx_1='6789012345')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='GREENSLOPES FAMILY PRACTICE')
        pv1.attending_doctor = XCN(xcn_1='8901234T', xcn_2='MORRISON', xcn_3='JAMES', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V100001')
        pv1.prior_temporary_location = PL(pl_1='20250314')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD-2025-0042')
        orc.filler_order_number = EI(ei_1='QML-2025-10042')
        orc.order_status = 'CM'
        orc.orc_12 = '8901234T^MORRISON^JAMES^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-0042')
        obr.filler_order_number = EI(ei_1='QML-2025-10042')
        obr.universal_service_identifier = CWE(cwe_1='26604007', cwe_2='Full blood count', cwe_3='SCT')
        obr.observation_date_time = '20250313153000+1000'
        obr.obr_15 = '8901234T^MORRISON^JAMES^^^DR'
        obr.filler_field_2 = '20250314085500+1000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Haemoglobin', cwe_3='LN')
        obx.obx_5 = '138'
        obx.units = CWE(cwe_1='g/L')
        obx.reference_range = '120-160'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250314085500+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='Red cell count', cwe_3='LN')
        obx_2.obx_5 = '4.52'
        obx_2.obx_6 = 'x10\\S\\12/L'
        obx_2.reference_range = '3.80-5.20'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250314085500+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='787-2', cwe_2='MCV', cwe_3='LN')
        obx_3.obx_5 = '88.0'
        obx_3.units = CWE(cwe_1='fL')
        obx_3.reference_range = '80.0-100.0'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250314085500+1000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='6690-2', cwe_2='White cell count', cwe_3='LN')
        obx_4.obx_5 = '7.2'
        obx_4.obx_6 = 'x10\\S\\9/L'
        obx_4.reference_range = '4.0-11.0'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250314085500+1000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='Platelet count', cwe_3='LN')
        obx_5.obx_5 = '245'
        obx_5.obx_6 = 'x10\\S\\9/L'
        obx_5.reference_range = '150-400'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250314085500+1000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2
        order_observation.observation_3 = observation_3
        order_observation.observation_4 = observation_4
        order_observation.observation_5 = observation_5

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 1)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 1)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg02(unittest.TestCase):
    """ Based on live/au/au-medicaldirector.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SONIC_PATH')
        msh.sending_facility = HD(hd_1='SONIC', hd_2='2092', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='MD_CLINICAL')
        msh.receiving_facility = HD(hd_1='BONDI JUNCTION MEDICAL CENTRE')
        msh.date_time_of_message = '20250422110000+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT30052001', cx_4='SONIC', cx_5='MR'), CX(cx_1='2345678901', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='SMITH', xpn_2='MARGARET', xpn_3='ANNE')
        pid.date_time_of_birth = '19651220'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='15 Oxford St', xad_3='BONDI JUNCTION', xad_4='NSW', xad_5='2022', xad_6='AU')
        pid.pid_13 = '0298765432'
        pid.patient_account_number = CX(cx_1='2345678901')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='BONDI JUNCTION MEDICAL CENTRE')
        pv1.attending_doctor = XCN(xcn_1='4567890T', xcn_2='CHEN', xcn_3='DAVID', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V200002')
        pv1.prior_temporary_location = PL(pl_1='20250422')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD-2025-1180')
        orc.filler_order_number = EI(ei_1='SONIC-2025-30421')
        orc.order_status = 'CM'
        orc.orc_12 = '4567890T^CHEN^DAVID^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-1180')
        obr.filler_order_number = EI(ei_1='SONIC-2025-30421')
        obr.universal_service_identifier = CWE(cwe_1='24331-1', cwe_2='Lipid panel', cwe_3='LN')
        obr.observation_date_time = '20250421140000+1000'
        obr.obr_15 = '4567890T^CHEN^DAVID^^^DR'
        obr.filler_field_2 = '20250422105000+1000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2093-3', cwe_2='Total cholesterol', cwe_3='LN')
        obx.obx_5 = '5.8'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '<5.5'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250422105000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2571-8', cwe_2='Triglycerides', cwe_3='LN')
        obx_2.obx_5 = '1.9'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '<2.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250422105000+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2085-9', cwe_2='HDL cholesterol', cwe_3='LN')
        obx_3.obx_5 = '1.3'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '>1.0'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250422105000+1000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='13457-7', cwe_2='LDL cholesterol (calc)', cwe_3='LN')
        obx_4.obx_5 = '3.6'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '<3.4'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250422105000+1000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='13458-5', cwe_2='TC/HDL ratio', cwe_3='LN')
        obx_5.obx_5 = '4.5'
        obx_5.reference_range = '<4.5'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250422105000+1000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2
        order_observation.observation_3 = observation_3
        order_observation.observation_4 = observation_4
        order_observation.observation_5 = observation_5

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 2)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 2)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg03(unittest.TestCase):
    """ Based on live/au/au-medicaldirector.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAVERTY_PATH')
        msh.sending_facility = HD(hd_1='LAVERTY', hd_2='2350', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='MEDICALDIRECTOR')
        msh.receiving_facility = HD(hd_1='PARRAMATTA GP CLINIC')
        msh.date_time_of_message = '20250510143000+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT40078923', cx_4='LAVERTY', cx_5='MR'), CX(cx_1='3456789012', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='PATEL', xpn_2='RAJAN', xpn_3='KUMAR')
        pid.date_time_of_birth = '19780503'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='88 Church St', xad_3='PARRAMATTA', xad_4='NSW', xad_5='2150', xad_6='AU')
        pid.pid_13 = '0423456789'
        pid.patient_account_number = CX(cx_1='3456789012')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='PARRAMATTA GP CLINIC')
        pv1.attending_doctor = XCN(xcn_1='5678901T', xcn_2="O'BRIEN", xcn_3='FIONA', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V300003')
        pv1.prior_temporary_location = PL(pl_1='20250510')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD-2025-2201')
        orc.filler_order_number = EI(ei_1='LAV-2025-55034')
        orc.order_status = 'CM'
        orc.orc_12 = "5678901T^O'BRIEN^FIONA^^^DR"

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-2201')
        obr.filler_order_number = EI(ei_1='LAV-2025-55034')
        obr.universal_service_identifier = CWE(cwe_1='24348-5', cwe_2='Thyroid function tests', cwe_3='LN')
        obr.observation_date_time = '20250509100000+1000'
        obr.obr_15 = "5678901T^O'BRIEN^FIONA^^^DR"
        obr.filler_field_2 = '20250510142000+1000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='TSH', cwe_3='LN')
        obx.obx_5 = '8.45'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.40-4.00'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250510142000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3024-7', cwe_2='Free T4', cwe_3='LN')
        obx_2.obx_5 = '10.2'
        obx_2.units = CWE(cwe_1='pmol/L')
        obx_2.reference_range = '10.0-25.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250510142000+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3053-6', cwe_2='Free T3', cwe_3='LN')
        obx_3.obx_5 = '4.1'
        obx_3.units = CWE(cwe_1='pmol/L')
        obx_3.reference_range = '3.5-6.5'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250510142000+1000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'FT'
        obx_4.observation_identifier = CWE(cwe_1='8251-1', cwe_2='Comment', cwe_3='LN')
        obx_4.obx_5 = 'TSH is elevated with borderline low Free T4. Suggest clinical correlation and consider repeat testing in 6-8 weeks.'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250510142000+1000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2
        order_observation.observation_3 = observation_3
        order_observation.observation_4 = observation_4

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 3)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 3)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg04(unittest.TestCase):
    """ Based on live/au/au-medicaldirector.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MELB_PATH')
        msh.sending_facility = HD(hd_1='MELBPATH', hd_2='2220', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='MDCLINICAL')
        msh.receiving_facility = HD(hd_1='CARLTON FAMILY MEDICAL')
        msh.date_time_of_message = '20250305160000+1100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT50034891', cx_4='MELBPATH', cx_5='MR'), CX(cx_1='4567890123', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='WILLIAMS', xpn_2='GARY', xpn_3='ROBERT')
        pid.date_time_of_birth = '19580910'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='7 Lygon St', xad_3='CARLTON', xad_4='VIC', xad_5='3053', xad_6='AU')
        pid.pid_13 = '0434567890'
        pid.patient_account_number = CX(cx_1='4567890123')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='CARLTON FAMILY MEDICAL')
        pv1.attending_doctor = XCN(xcn_1='6789012T', xcn_2='KELLY', xcn_3='SARAH', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V400004')
        pv1.prior_temporary_location = PL(pl_1='20250305')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD-2025-0315')
        orc.filler_order_number = EI(ei_1='MP-2025-41023')
        orc.order_status = 'CM'
        orc.orc_12 = '6789012T^KELLY^SARAH^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-0315')
        obr.filler_order_number = EI(ei_1='MP-2025-41023')
        obr.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obr.observation_date_time = '20250304083000+1100'
        obr.obr_15 = '6789012T^KELLY^SARAH^^^DR'
        obr.filler_field_2 = '20250305155000+1100'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obx.obx_5 = '7.8'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '<6.5'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250305155000+1100'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='59261-8', cwe_2='HbA1c (IFCC)', cwe_3='LN')
        obx_2.obx_5 = '62'
        obx_2.units = CWE(cwe_1='mmol/mol')
        obx_2.reference_range = '<48'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250305155000+1100'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'FT'
        obx_3.observation_identifier = CWE(cwe_1='8251-1', cwe_2='Comment', cwe_3='LN')
        obx_3.obx_5 = 'HbA1c above target. Consistent with suboptimal glycaemic control. Please correlate clinically.'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250305155000+1100'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2
        order_observation.observation_3 = observation_3

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 4)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 4)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg05(unittest.TestCase):
    """ Based on live/au/au-medicaldirector.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IMED_RAD')
        msh.sending_facility = HD(hd_1='IMED', hd_2='8901', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='MEDICALDIRECTOR')
        msh.receiving_facility = HD(hd_1='SOUTHBANK MEDICAL CENTRE')
        msh.date_time_of_message = '20250218140000+1100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT60091234', cx_4='IMED', cx_5='MR'), CX(cx_1='5678901234', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='JONES', xpn_2='ELIZABETH', xpn_3='MARY')
        pid.date_time_of_birth = '19720618'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='200 Clarendon St', xad_3='SOUTHBANK', xad_4='VIC', xad_5='3006', xad_6='AU')
        pid.pid_13 = '0445678901'
        pid.patient_account_number = CX(cx_1='5678901234')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='SOUTHBANK MEDICAL CENTRE')
        pv1.attending_doctor = XCN(xcn_1='7890123T', xcn_2='ANDERSON', xcn_3='PETER', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V500005')
        pv1.prior_temporary_location = PL(pl_1='20250218')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD-2025-0890')
        orc.filler_order_number = EI(ei_1='IMED-2025-12567')
        orc.order_status = 'CM'
        orc.orc_12 = '7890123T^ANDERSON^PETER^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-0890')
        obr.filler_order_number = EI(ei_1='IMED-2025-12567')
        obr.universal_service_identifier = CWE(cwe_1='36643-5', cwe_2='Chest X-ray', cwe_3='LN')
        obr.observation_date_time = '20250217110000+1100'
        obr.obr_15 = '7890123T^ANDERSON^PETER^^^DR'
        obr.filler_field_2 = '20250218133000+1100'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='36643-5', cwe_2='Chest X-ray report', cwe_3='LN')
        obx.obx_5 = (
            'Chest X-ray PA and lateral. Heart size normal. Lungs are clear. No focal consolidation, pleural effusion or pneumothorax. Bony structures ar'
            'e unremarkable. Impression: Normal chest X-ray.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250218133000+1100'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Radiology Report', cwe_3='LN')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMg'
            'MCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5'
            'IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250218133000+1100'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 5)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 5)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg06(unittest.TestCase):
    """ Based on live/au/au-medicaldirector.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SNP_PATH')
        msh.sending_facility = HD(hd_1='SNP', hd_2='2203', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='MD_CLINICAL')
        msh.receiving_facility = HD(hd_1='TOOWOOMBA FAMILY PRACTICE')
        msh.date_time_of_message = '20250611080000+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT70023456', cx_4='SNP', cx_5='MR'), CX(cx_1='6789012345', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='BROWN', xpn_2='DAVID', xpn_3='JAMES')
        pid.date_time_of_birth = '19831127'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='33 Ruthven St', xad_3='TOOWOOMBA', xad_4='QLD', xad_5='4350', xad_6='AU')
        pid.pid_13 = '0456789012'
        pid.patient_account_number = CX(cx_1='6789012345')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='TOOWOOMBA FAMILY PRACTICE')
        pv1.attending_doctor = XCN(xcn_1='2345678T', xcn_2='WONG', xcn_3='MICHAEL', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V600006')
        pv1.prior_temporary_location = PL(pl_1='20250611')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD-2025-3401')
        orc.filler_order_number = EI(ei_1='SNP-2025-78234')
        orc.order_status = 'CM'
        orc.orc_12 = '2345678T^WONG^MICHAEL^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-3401')
        obr.filler_order_number = EI(ei_1='SNP-2025-78234')
        obr.universal_service_identifier = CWE(cwe_1='630-4', cwe_2='Urine MCS', cwe_3='LN')
        obr.observation_date_time = '20250610090000+1000'
        obr.obr_15 = '2345678T^WONG^MICHAEL^^^DR'
        obr.filler_field_2 = '20250611075000+1000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='5767-9', cwe_2='Appearance', cwe_3='LN')
        obx.obx_5 = 'Cloudy'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250611075000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='5803-2', cwe_2='pH', cwe_3='LN')
        obx_2.obx_5 = '6.0'
        obx_2.reference_range = '5.0-8.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250611075000+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='5811-5', cwe_2='Specific gravity', cwe_3='LN')
        obx_3.obx_5 = '1.025'
        obx_3.reference_range = '1.005-1.030'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250611075000+1000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='20405-7', cwe_2='White cells', cwe_3='LN')
        obx_4.obx_5 = '120'
        obx_4.obx_6 = 'x10\\S\\6/L'
        obx_4.reference_range = '<10'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250611075000+1000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='30364-4', cwe_2='Red cells', cwe_3='LN')
        obx_5.obx_5 = '15'
        obx_5.obx_6 = 'x10\\S\\6/L'
        obx_5.reference_range = '<10'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250611075000+1000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='630-4', cwe_2='Culture', cwe_3='LN')
        obx_6.obx_5 = 'Escherichia coli >10\\S\\8 CFU/L'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250611075000+1000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'FT'
        obx_7.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Sensitivities', cwe_3='LN')
        obx_7.obx_5 = 'Amoxycillin: S\\R\\Trimethoprim: R\\R\\Cefalexin: S\\R\\Nitrofurantoin: S'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250611075000+1000'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2
        order_observation.observation_3 = observation_3
        order_observation.observation_4 = observation_4
        order_observation.observation_5 = observation_5
        order_observation.observation_6 = observation_6
        order_observation.observation_7 = observation_7

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 6)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 6)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg07(unittest.TestCase):
    """ Based on live/au/au-medicaldirector.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDICALDIRECTOR')
        msh.sending_facility = HD(hd_1='NORWOOD GP SURGERY')
        msh.receiving_application = HD(hd_1='SPECIALIST_RECV')
        msh.receiving_facility = HD(hd_1='ADELAIDE HEART CLINIC')
        msh.date_time_of_message = '20250720100000+0930'
        msh.message_type = MSG(msg_1='REF', msg_2='I12', msg_3='REF_I12')
        msh.message_control_id = 'MSG00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build RF1 ..
        rf1 = RF1()
        rf1.referral_status = CWE(cwe_1='SS')
        rf1.referral_priority = CWE(cwe_1='OU')
        rf1.referral_type = CWE(cwe_1='CARD')
        rf1.referral_disposition = CWE(cwe_1='NM')
        rf1.referral_category = CWE(cwe_1='20250720')
        rf1.originating_referral_identifier = EI(ei_1='20251020')
        rf1.referral_reason = CWE(cwe_1='Referral for cardiology review')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT80098765', cx_4='NORWOOD', cx_5='MR'), CX(cx_1='7890123456', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='TAYLOR', xpn_2='JOHN', xpn_3='WILLIAM')
        pid.date_time_of_birth = '19600422'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='12 The Parade', xad_3='NORWOOD', xad_4='SA', xad_5='5067', xad_6='AU')
        pid.pid_13 = '0467890123'
        pid.patient_account_number = CX(cx_1='7890123456')

        # .. build PRD ..
        prd = PRD()
        prd.provider_role = CWE(cwe_1='RP')
        prd.provider_name = XPN(xpn_1='HARRIS', xpn_2='AMANDA', xpn_5='DR')
        prd.provider_address = XAD(xad_1='NORWOOD GP SURGERY', xad_3='18 Osmond Tce', xad_5='NORWOOD', xad_6='SA', xad_7='5067', xad_8='AU')
        prd.effective_start_date_of_provider_role = '3456789T'

        # .. build PRD ..
        prd_2 = PRD()
        prd_2.provider_role = CWE(cwe_1='RT')
        prd_2.provider_name = XPN(xpn_1='KUMAR', xpn_2='RAJESH', xpn_5='DR')
        prd_2.provider_address = XAD(xad_1='ADELAIDE HEART CLINIC', xad_3='45 Greenhill Rd', xad_5='WAYVILLE', xad_6='SA', xad_7='5034', xad_8='AU')
        prd_2.effective_start_date_of_provider_role = '4567890T'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I25.1', cwe_2='Atherosclerotic heart disease', cwe_3='I10')
        dg1.diagnosis_date_time = '20250710'
        dg1.diagnosis_type = CWE(cwe_1='F')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = (
            'This 65-year-old male presents with exertional chest tightness over the past 4 weeks. Stress ECG shows ST depression in leads V4-V6. Family '
            'history of IHD. Currently on aspirin 100mg, atorvastatin 40mg. Please review and advise regarding coronary angiography. Thank you.'
        )

        # .. assemble the full message ..
        msg = REF_I12()
        msg.msh = msh
        msg.rf1 = rf1
        msg.pid = pid
        msg.extra_segments = [prd, prd_2, dg1, nte]

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 7)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 7)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg08(unittest.TestCase):
    """ Based on live/au/au-medicaldirector.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MDCLINICAL')
        msh.sending_facility = HD(hd_1='COOGEE BEACH MEDICAL')
        msh.receiving_application = HD(hd_1='SPECIALIST_RECV')
        msh.receiving_facility = HD(hd_1='SYDNEY GASTRO SPECIALISTS')
        msh.date_time_of_message = '20250815093000+1000'
        msh.message_type = MSG(msg_1='REF', msg_2='I12', msg_3='REF_I12')
        msh.message_control_id = 'MSG00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build RF1 ..
        rf1 = RF1()
        rf1.referral_status = CWE(cwe_1='SS')
        rf1.referral_priority = CWE(cwe_1='OU')
        rf1.referral_type = CWE(cwe_1='GI')
        rf1.referral_disposition = CWE(cwe_1='NM')
        rf1.referral_category = CWE(cwe_1='20250815')
        rf1.originating_referral_identifier = EI(ei_1='20251115')
        rf1.referral_reason = CWE(cwe_1='Referral for gastroenterology review - iron deficiency anaemia')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT90045678', cx_4='COOGEE', cx_5='MR'), CX(cx_1='8901234567', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='GARCIA', xpn_2='MARIA', xpn_3='ELENA')
        pid.date_time_of_birth = '19750809'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='5 Carr St', xad_3='COOGEE', xad_4='NSW', xad_5='2034', xad_6='AU')
        pid.pid_13 = '0478901234'
        pid.patient_account_number = CX(cx_1='8901234567')

        # .. build PRD ..
        prd = PRD()
        prd.provider_role = CWE(cwe_1='RP')
        prd.provider_name = XPN(xpn_1='THOMPSON', xpn_2='RICHARD', xpn_5='DR')
        prd.provider_address = XAD(xad_1='COOGEE BEACH MEDICAL', xad_3='230 Coogee Bay Rd', xad_5='COOGEE', xad_6='NSW', xad_7='2034', xad_8='AU')
        prd.effective_start_date_of_provider_role = '5678901T'

        # .. build PRD ..
        prd_2 = PRD()
        prd_2.provider_role = CWE(cwe_1='RT')
        prd_2.provider_name = XPN(xpn_1='LIM', xpn_2='ANDREW', xpn_5='DR')
        prd_2.provider_address = XAD(xad_1='SYDNEY GASTRO SPECIALISTS', xad_3='120 Pacific Hwy', xad_5='ST LEONARDS', xad_6='NSW', xad_7='2065', xad_8='AU')
        prd_2.effective_start_date_of_provider_role = '6789012T'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='D50.9', cwe_2='Iron deficiency anaemia, unspecified', cwe_3='I10')
        dg1.diagnosis_date_time = '20250801'
        dg1.diagnosis_type = CWE(cwe_1='F')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = (
            '49-year-old female with persistent iron deficiency anaemia. Ferritin 8 ug/L, Hb 105 g/L. No obvious source of blood loss. Coeliac serology n'
            'egative. Please assess for colonoscopy and upper endoscopy. Recent FBC and iron studies enclosed.'
        )

        # .. assemble the full message ..
        msg = REF_I12()
        msg.msh = msh
        msg.rf1 = rf1
        msg.pid = pid
        msg.extra_segments = [prd, prd_2, dg1, nte]

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 8)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 8)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg09(unittest.TestCase):
    """ Based on live/au/au-medicaldirector.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDICALDIRECTOR')
        msh.sending_facility = HD(hd_1='DARWIN FAMILY MEDICAL')
        msh.receiving_application = HD(hd_1='PMS_RECV')
        msh.receiving_facility = HD(hd_1='DARWIN FAMILY MEDICAL')
        msh.date_time_of_message = '20250903081500+0930'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250903081500+0930'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT10056789', cx_4='DARWIN', cx_5='MR'), CX(cx_1='9012345678', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='COOPER', xpn_2='SARAH', xpn_3='JANE')
        pid.date_time_of_birth = '19900214'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='8 Mitchell St', xad_3='DARWIN', xad_4='NT', xad_5='0800', xad_6='AU')
        pid.pid_13 = '0489012345'
        pid.patient_account_number = CX(cx_1='9012345678')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='COOPER', xpn_2='MARK', xpn_3='THOMAS')
        nk1.relationship = CWE(cwe_1='SPO')
        nk1.address = XAD(xad_1='8 Mitchell St', xad_3='DARWIN', xad_4='NT', xad_5='0800', xad_6='AU')
        nk1.nk1_5 = '0489012346'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSULT', pl_2='ROOM3', pl_3='DARWIN FAMILY MEDICAL')
        pv1.attending_doctor = XCN(xcn_1='8901234T', xcn_2='MARSHALL', xcn_3='BRUCE', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='GEN')
        pv1.patient_type = CWE(cwe_1='V700009')
        pv1.prior_temporary_location = PL(pl_1='20250903')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='MEDIBANK')
        in1.insurance_company_id = CX(cx_1='MEDIBANK PRIVATE')
        in1.insureds_group_emp_id = CX(cx_1='MEDIBANK PRIVATE')
        in1.in1_40 = '34567890'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.insurance = insurance

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 9)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 9)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg10(unittest.TestCase):
    """ Based on live/au/au-medicaldirector.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDICALDIRECTOR')
        msh.sending_facility = HD(hd_1='FREMANTLE MEDICAL CENTRE')
        msh.receiving_application = HD(hd_1='PMS_RECV')
        msh.receiving_facility = HD(hd_1='FREMANTLE MEDICAL CENTRE')
        msh.date_time_of_message = '20250415141200+0800'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250415141200+0800'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT11087654', cx_4='FREMANTLE', cx_5='MR'), CX(cx_1='0123456789', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='MCLEOD', xpn_2='ANGUS', xpn_3='IAN')
        pid.date_time_of_birth = '19451103'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='27 South Tce', xad_3='FREMANTLE', xad_4='WA', xad_5='6160', xad_6='AU')
        pid.pid_13 = '0890123456'
        pid.patient_account_number = CX(cx_1='0123456789')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='FREMANTLE MEDICAL CENTRE')
        pv1.attending_doctor = XCN(xcn_1='9012345T', xcn_2='GIBSON', xcn_3='LAURA', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V800010')
        pv1.prior_temporary_location = PL(pl_1='20250415')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 10)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 10)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg11(unittest.TestCase):
    """ Based on live/au/au-medicaldirector.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDICALDIRECTOR')
        msh.sending_facility = HD(hd_1='HOBART CBD MEDICAL')
        msh.receiving_application = HD(hd_1='ROYAL_HOBART_PATH')
        msh.receiving_facility = HD(hd_1='ROYAL HOBART HOSPITAL PATHOLOGY')
        msh.date_time_of_message = '20250128090000+1100'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT12012345', cx_4='HOBART', cx_5='MR'), CX(cx_1='1234509876', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='FITZGERALD', xpn_2='NORA', xpn_3='PATRICIA')
        pid.date_time_of_birth = '19680729'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='55 Liverpool St', xad_3='HOBART', xad_4='TAS', xad_5='7000', xad_6='AU')
        pid.pid_13 = '0401234567'
        pid.patient_account_number = CX(cx_1='1234509876')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='HOBART CBD MEDICAL')
        pv1.attending_doctor = XCN(xcn_1='0123456T', xcn_2='BURKE', xcn_3='THOMAS', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V900011')
        pv1.prior_temporary_location = PL(pl_1='20250128')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD-2025-4501')
        orc.parent_order = EIP(eip_1='20250128090000+1100')
        orc.orc_11 = '0123456T^BURKE^THOMAS^^^DR'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-4501')
        obr.universal_service_identifier = CWE(cwe_1='24325-3', cwe_2='Liver function tests', cwe_3='LN')
        obr.observation_date_time = '20250128'
        obr.specimen_action_code = 'N'
        obr.obr_17 = '0123456T^BURKE^THOMAS^^^DR'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Patient on methotrexate for rheumatoid arthritis. Routine monitoring LFTs please.'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.nte = nte

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 11)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 11)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg12(unittest.TestCase):
    """ Based on live/au/au-medicaldirector.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MD_CLINICAL')
        msh.sending_facility = HD(hd_1='CAIRNS CENTRAL MEDICAL')
        msh.receiving_application = HD(hd_1='NQ_PATHOLOGY')
        msh.receiving_facility = HD(hd_1='NORTH QLD PATHOLOGY')
        msh.date_time_of_message = '20250509103000+1000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT13045678', cx_4='CAIRNS', cx_5='MR'), CX(cx_1='2345601234', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='WALKER', xpn_2='BENJAMIN', xpn_3='THOMAS')
        pid.date_time_of_birth = '19950315'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='10 Shields St', xad_3='CAIRNS', xad_4='QLD', xad_5='4870', xad_6='AU')
        pid.pid_13 = '0412340567'
        pid.patient_account_number = CX(cx_1='2345601234')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='CAIRNS CENTRAL MEDICAL')
        pv1.attending_doctor = XCN(xcn_1='1234567T', xcn_2='RUSSO', xcn_3='ANGELA', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V010012')
        pv1.prior_temporary_location = PL(pl_1='20250509')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD-2025-5678')
        orc.parent_order = EIP(eip_1='20250509103000+1000')
        orc.orc_11 = '1234567T^RUSSO^ANGELA^^^DR'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-5678')
        obr.universal_service_identifier = CWE(cwe_1='2498-4', cwe_2='Iron studies', cwe_3='LN')
        obr.observation_date_time = '20250509'
        obr.specimen_action_code = 'N'
        obr.obr_17 = '1234567T^RUSSO^ANGELA^^^DR'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='ORD-2025-5678')
        obr_2.universal_service_identifier = CWE(cwe_1='26604007', cwe_2='Full blood count', cwe_3='SCT')
        obr_2.observation_date_time = '20250509'
        obr_2.specimen_action_code = 'N'
        obr_2.obr_17 = '1234567T^RUSSO^ANGELA^^^DR'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Fatigue and pallor. ?Iron deficiency. Please perform FBC and iron studies.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, nte]

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 12)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 12)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg13(unittest.TestCase):
    """ Based on live/au/au-medicaldirector.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DOREVITCH')
        msh.sending_facility = HD(hd_1='DOREVITCH', hd_2='2115', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='MEDICALDIRECTOR')
        msh.receiving_facility = HD(hd_1='GEELONG WEST MEDICAL')
        msh.date_time_of_message = '20250203170000+1100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT14078901', cx_4='DOREVITCH', cx_5='MR'), CX(cx_1='3456712345', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='HENDERSON', xpn_2='BRUCE', xpn_3='ALLAN')
        pid.date_time_of_birth = '19550812'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='14 Pakington St', xad_3='GEELONG WEST', xad_4='VIC', xad_5='3218', xad_6='AU')
        pid.pid_13 = '0423450678'
        pid.patient_account_number = CX(cx_1='3456712345')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='GEELONG WEST MEDICAL')
        pv1.attending_doctor = XCN(xcn_1='2345678T', xcn_2='DUFFY', xcn_3='CATHERINE', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V020013')
        pv1.prior_temporary_location = PL(pl_1='20250203')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD-2025-0102')
        orc.filler_order_number = EI(ei_1='DOR-2025-23456')
        orc.order_status = 'CM'
        orc.orc_12 = '2345678T^DUFFY^CATHERINE^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-0102')
        obr.filler_order_number = EI(ei_1='DOR-2025-23456')
        obr.universal_service_identifier = CWE(cwe_1='2857-1', cwe_2='PSA', cwe_3='LN')
        obr.observation_date_time = '20250202090000+1100'
        obr.obr_15 = '2345678T^DUFFY^CATHERINE^^^DR'
        obr.filler_field_2 = '20250203163000+1100'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2857-1', cwe_2='PSA total', cwe_3='LN')
        obx.obx_5 = '8.7'
        obx.units = CWE(cwe_1='ug/L')
        obx.reference_range = '0.0-4.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250203163000+1100'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='10886-0', cwe_2='Free PSA', cwe_3='LN')
        obx_2.obx_5 = '1.1'
        obx_2.units = CWE(cwe_1='ug/L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250203163000+1100'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='12841-3', cwe_2='Free/Total PSA ratio', cwe_3='LN')
        obx_3.obx_5 = '13'
        obx_3.units = CWE(cwe_1='%')
        obx_3.reference_range = '>25'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250203163000+1100'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'FT'
        obx_4.observation_identifier = CWE(cwe_1='8251-1', cwe_2='Comment', cwe_3='LN')
        obx_4.obx_5 = 'PSA is elevated with a low free/total ratio. Urology referral is recommended for further evaluation.'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250203163000+1100'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2
        order_observation.observation_3 = observation_3
        order_observation.observation_4 = observation_4

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 13)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 13)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg14(unittest.TestCase):
    """ Based on live/au/au-medicaldirector.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ACT_PATH')
        msh.sending_facility = HD(hd_1='ACTPATH', hd_2='2601', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='MDCLINICAL')
        msh.receiving_facility = HD(hd_1='WODEN VALLEY MEDICAL')
        msh.date_time_of_message = '20250711153000+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT15034567', cx_4='ACTPATH', cx_5='MR'), CX(cx_1='4567823456', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='ROBERTSON', xpn_2='EILEEN', xpn_3='MAY')
        pid.date_time_of_birth = '19440317'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='3 Callam St', xad_3='WODEN', xad_4='ACT', xad_5='2606', xad_6='AU')
        pid.pid_13 = '0234567890'
        pid.patient_account_number = CX(cx_1='4567823456')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='WODEN VALLEY MEDICAL')
        pv1.attending_doctor = XCN(xcn_1='3456789T', xcn_2='NGUYEN', xcn_3='TRAN', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V030014')
        pv1.prior_temporary_location = PL(pl_1='20250711')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD-2025-6701')
        orc.filler_order_number = EI(ei_1='ACT-2025-34567')
        orc.order_status = 'CM'
        orc.orc_12 = '3456789T^NGUYEN^TRAN^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-6701')
        obr.filler_order_number = EI(ei_1='ACT-2025-34567')
        obr.universal_service_identifier = CWE(cwe_1='5902-2', cwe_2='PT/INR', cwe_3='LN')
        obr.observation_date_time = '20250711080000+1000'
        obr.obr_15 = '3456789T^NGUYEN^TRAN^^^DR'
        obr.filler_field_2 = '20250711150000+1000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='Prothrombin time', cwe_3='LN')
        obx.obx_5 = '22.5'
        obx.units = CWE(cwe_1='sec')
        obx.reference_range = '11.0-15.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250711150000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx_2.obx_5 = '2.8'
        obx_2.reference_range = '2.0-3.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250711150000+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'FT'
        obx_3.observation_identifier = CWE(cwe_1='8251-1', cwe_2='Comment', cwe_3='LN')
        obx_3.obx_5 = 'INR within therapeutic range for atrial fibrillation. Continue current warfarin dose.'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250711150000+1000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2
        order_observation.observation_3 = observation_3

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 14)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 14)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg15(unittest.TestCase):
    """ Based on live/au/au-medicaldirector.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DHM_PATH')
        msh.sending_facility = HD(hd_1='DHM', hd_2='2191', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='MEDICALDIRECTOR')
        msh.receiving_facility = HD(hd_1='CHATSWOOD GP CENTRE')
        msh.date_time_of_message = '20250922120000+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT16023456', cx_4='DHM', cx_5='MR'), CX(cx_1='5678934567', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='CAMPBELL', xpn_2='JESSICA', xpn_3='LOUISE')
        pid.date_time_of_birth = '19880625'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='22 Victoria Ave', xad_3='CHATSWOOD', xad_4='NSW', xad_5='2067', xad_6='AU')
        pid.pid_13 = '0434560789'
        pid.patient_account_number = CX(cx_1='5678934567')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='CHATSWOOD GP CENTRE')
        pv1.attending_doctor = XCN(xcn_1='4567890T', xcn_2='PARK', xcn_3='SUJIN', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V040015')
        pv1.prior_temporary_location = PL(pl_1='20250922')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD-2025-7802')
        orc.filler_order_number = EI(ei_1='DHM-2025-56789')
        orc.order_status = 'CM'
        orc.orc_12 = '4567890T^PARK^SUJIN^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-7802')
        obr.filler_order_number = EI(ei_1='DHM-2025-56789')
        obr.universal_service_identifier = CWE(cwe_1='21440-3', cwe_2='HPV DNA', cwe_3='LN')
        obr.observation_date_time = '20250920100000+1000'
        obr.obr_15 = '4567890T^PARK^SUJIN^^^DR'
        obr.filler_field_2 = '20250922115000+1000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='21440-3', cwe_2='HPV DNA test', cwe_3='LN')
        obx.obx_5 = 'Not detected'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250922115000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='10524-7', cwe_2='Cytology', cwe_3='LN')
        obx_2.obx_5 = 'Negative for intraepithelial lesion or malignancy'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250922115000+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'FT'
        obx_3.observation_identifier = CWE(cwe_1='8251-1', cwe_2='Comment', cwe_3='LN')
        obx_3.obx_5 = 'HPV not detected. LBC satisfactory. Recommend routine recall in 5 years as per National Cervical Screening Program guidelines.'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250922115000+1000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2
        order_observation.observation_3 = observation_3

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 15)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 15)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg16(unittest.TestCase):
    """ Based on live/au/au-medicaldirector.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CAPITAL_RAD')
        msh.sending_facility = HD(hd_1='CAPRAD', hd_2='8567', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='MD_CLINICAL')
        msh.receiving_facility = HD(hd_1='HEIDELBERG MEDICAL CENTRE')
        msh.date_time_of_message = '20250407163000+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT17034567', cx_4='CAPRAD', cx_5='MR'), CX(cx_1='6789045678', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='MURPHY', xpn_2='CLAIRE', xpn_3='ELIZABETH')
        pid.date_time_of_birth = '19821115'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='9 Burgundy St', xad_3='HEIDELBERG', xad_4='VIC', xad_5='3084', xad_6='AU')
        pid.pid_13 = '0445670891'
        pid.patient_account_number = CX(cx_1='6789045678')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='HEIDELBERG MEDICAL CENTRE')
        pv1.attending_doctor = XCN(xcn_1='5678901T', xcn_2='TRAN', xcn_3='HIEN', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V050016')
        pv1.prior_temporary_location = PL(pl_1='20250407')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD-2025-3340')
        orc.filler_order_number = EI(ei_1='CAPRAD-2025-22345')
        orc.order_status = 'CM'
        orc.orc_12 = '5678901T^TRAN^HIEN^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-3340')
        obr.filler_order_number = EI(ei_1='CAPRAD-2025-22345')
        obr.universal_service_identifier = CWE(cwe_1='76856-9', cwe_2='Pelvic ultrasound', cwe_3='LN')
        obr.observation_date_time = '20250406140000+1000'
        obr.obr_15 = '5678901T^TRAN^HIEN^^^DR'
        obr.filler_field_2 = '20250407162000+1000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='76856-9', cwe_2='Pelvic ultrasound report', cwe_3='LN')
        obx.obx_5 = (
            'Transabdominal and transvaginal pelvic ultrasound. Uterus is anteverted, normal size 7.5 x 4.2 x 3.8 cm. Endometrial thickness 6mm. Right ov'
            'ary contains a simple cyst 32mm diameter. Left ovary normal. No free fluid. Impression: Simple right ovarian cyst, likely follicular. Sugges'
            't follow-up ultrasound in 6-8 weeks.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250407162000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Radiology Report', cwe_3='LN')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMg'
            'MCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5'
            'IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250407162000+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 16)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 16)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg17(unittest.TestCase):
    """ Based on live/au/au-medicaldirector.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SA_PATH')
        msh.sending_facility = HD(hd_1='SAPATH', hd_2='4301', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='MEDICALDIRECTOR')
        msh.receiving_facility = HD(hd_1='GLENELG MEDICAL PRACTICE')
        msh.date_time_of_message = '20250519111500+0930'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT18056789', cx_4='SAPATH', cx_5='MR'), CX(cx_1='7890156789', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='EDWARDS', xpn_2='PETER', xpn_3='MICHAEL')
        pid.date_time_of_birth = '19710203'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='15 Jetty Rd', xad_3='GLENELG', xad_4='SA', xad_5='5045', xad_6='AU')
        pid.pid_13 = '0456780912'
        pid.patient_account_number = CX(cx_1='7890156789')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='GLENELG MEDICAL PRACTICE')
        pv1.attending_doctor = XCN(xcn_1='6789012T', xcn_2='HALL', xcn_3='JENNIFER', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V060017')
        pv1.prior_temporary_location = PL(pl_1='20250519')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD-2025-4403')
        orc.filler_order_number = EI(ei_1='SAP-2025-67890')
        orc.order_status = 'CM'
        orc.orc_12 = '6789012T^HALL^JENNIFER^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-4403')
        obr.filler_order_number = EI(ei_1='SAP-2025-67890')
        obr.universal_service_identifier = CWE(cwe_1='24362-6', cwe_2='Renal function', cwe_3='LN')
        obr.observation_date_time = '20250518080000+0930'
        obr.obr_15 = '6789012T^HALL^JENNIFER^^^DR'
        obr.filler_field_2 = '20250519110000+0930'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine', cwe_3='LN')
        obx.obx_5 = '142'
        obx.units = CWE(cwe_1='umol/L')
        obx.reference_range = '60-110'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250519110000+0930'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='33914-3', cwe_2='eGFR', cwe_3='LN')
        obx_2.obx_5 = '48'
        obx_2.units = CWE(cwe_1='mL/min/1.73m2')
        obx_2.reference_range = '>60'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250519110000+0930'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea', cwe_3='LN')
        obx_3.obx_5 = '12.5'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '2.5-8.0'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250519110000+0930'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium', cwe_3='LN')
        obx_4.obx_5 = '5.3'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '3.5-5.2'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250519110000+0930'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodium', cwe_3='LN')
        obx_5.obx_5 = '139'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '135-145'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250519110000+0930'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'FT'
        obx_6.observation_identifier = CWE(cwe_1='8251-1', cwe_2='Comment', cwe_3='LN')
        obx_6.obx_5 = 'eGFR 48 mL/min consistent with CKD Stage 3b. Elevated potassium noted. Recommend nephrology review.'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250519110000+0930'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2
        order_observation.observation_3 = observation_3
        order_observation.observation_4 = observation_4
        order_observation.observation_5 = observation_5
        order_observation.observation_6 = observation_6

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 17)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 17)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg18(unittest.TestCase):
    """ Based on live/au/au-medicaldirector.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HEALTHLINK')
        msh.sending_facility = HD(hd_1='HEALTHLINK_NET')
        msh.receiving_application = HD(hd_1='MEDICALDIRECTOR')
        msh.receiving_facility = HD(hd_1='MANUKA MEDICAL CENTRE')
        msh.date_time_of_message = '20250130090000+1100'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'MSG00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250130090000+1100'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT19067890', cx_4='MANUKA', cx_5='MR'), CX(cx_1='8901267890', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='SINGH', xpn_2='PRIYA', xpn_3='DEVI')
        pid.date_time_of_birth = '19930521'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='4 Flinders Way', xad_3='MANUKA', xad_4='ACT', xad_5='2603', xad_6='AU')
        pid.pid_13 = '0467891234'
        pid.patient_account_number = CX(cx_1='8901267890')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='SINGH', xpn_2='ARJUN', xpn_3='KUMAR')
        nk1.relationship = CWE(cwe_1='SPO')
        nk1.address = XAD(xad_1='4 Flinders Way', xad_3='MANUKA', xad_4='ACT', xad_5='2603', xad_6='AU')
        nk1.nk1_5 = '0467891235'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='MANUKA MEDICAL CENTRE')
        pv1.attending_doctor = XCN(xcn_1='7890123T', xcn_2='FRASER', xcn_3='DUNCAN', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='GEN')
        pv1.patient_type = CWE(cwe_1='V070018')
        pv1.prior_temporary_location = PL(pl_1='20250130')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='BUPA')
        in1.insurance_company_id = CX(cx_1='BUPA HEALTH INSURANCE')
        in1.insureds_group_emp_id = CX(cx_1='BUPA')
        in1.in1_40 = '45678901'

        # .. build the INSURANCE group ..
        insurance = AdtA05Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.insurance = insurance

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 18)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 18)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg19(unittest.TestCase):
    """ Based on live/au/au-medicaldirector.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WDP_PATH')
        msh.sending_facility = HD(hd_1='WDP', hd_2='4502', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='MDCLINICAL')
        msh.receiving_facility = HD(hd_1='SUBIACO MEDICAL CENTRE')
        msh.date_time_of_message = '20250623145000+0800'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT20034567', cx_4='WDP', cx_5='MR'), CX(cx_1='9012378901', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='CLARKE', xpn_2='WENDY', xpn_3='ANNE')
        pid.date_time_of_birth = '19800911'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='22 Rokeby Rd', xad_3='SUBIACO', xad_4='WA', xad_5='6008', xad_6='AU')
        pid.pid_13 = '0478902345'
        pid.patient_account_number = CX(cx_1='9012378901')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='SUBIACO MEDICAL CENTRE')
        pv1.attending_doctor = XCN(xcn_1='8901234T', xcn_2='AHMED', xcn_3='FARID', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V080019')
        pv1.prior_temporary_location = PL(pl_1='20250623')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD-2025-5504')
        orc.filler_order_number = EI(ei_1='WDP-2025-89012')
        orc.order_status = 'CM'
        orc.orc_12 = '8901234T^AHMED^FARID^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-5504')
        obr.filler_order_number = EI(ei_1='WDP-2025-89012')
        obr.universal_service_identifier = CWE(cwe_1='62292-8', cwe_2='25-OH Vitamin D and Calcium', cwe_3='LN')
        obr.observation_date_time = '20250622090000+0800'
        obr.obr_15 = '8901234T^AHMED^FARID^^^DR'
        obr.filler_field_2 = '20250623143000+0800'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1989-3', cwe_2='25-OH Vitamin D', cwe_3='LN')
        obx.obx_5 = '32'
        obx.units = CWE(cwe_1='nmol/L')
        obx.reference_range = '50-150'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250623143000+0800'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='17861-6', cwe_2='Calcium (corrected)', cwe_3='LN')
        obx_2.obx_5 = '2.38'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '2.10-2.60'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250623143000+0800'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'FT'
        obx_3.observation_identifier = CWE(cwe_1='8251-1', cwe_2='Comment', cwe_3='LN')
        obx_3.obx_5 = 'Vitamin D deficient. Recommend supplementation with cholecalciferol 1000 IU daily and repeat in 3 months.'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250623143000+0800'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2
        order_observation.observation_3 = observation_3

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 19)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 19)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

class TestMsg20(unittest.TestCase):
    """ Based on live/au/au-medicaldirector.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINIPATH')
        msh.sending_facility = HD(hd_1='CLINIPATH', hd_2='4510', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='MEDICALDIRECTOR')
        msh.receiving_facility = HD(hd_1='JOONDALUP FAMILY PRACTICE')
        msh.date_time_of_message = '20250812101500+0800'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT21045678', cx_4='CLINIPATH', cx_5='MR'), CX(cx_1='0123489012', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='KELLY', xpn_2='BROOKE', xpn_3='MARIE')
        pid.date_time_of_birth = '19960730'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='40 Grand Bvd', xad_3='JOONDALUP', xad_4='WA', xad_5='6027', xad_6='AU')
        pid.pid_13 = '0489013456'
        pid.patient_account_number = CX(cx_1='0123489012')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='JOONDALUP FAMILY PRACTICE')
        pv1.attending_doctor = XCN(xcn_1='9012345T', xcn_2='WATKINS', xcn_3='EMMA', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V090020')
        pv1.prior_temporary_location = PL(pl_1='20250812')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD-2025-6605')
        orc.filler_order_number = EI(ei_1='CLIN-2025-90123')
        orc.order_status = 'CM'
        orc.orc_12 = '9012345T^WATKINS^EMMA^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2025-6605')
        obr.filler_order_number = EI(ei_1='CLIN-2025-90123')
        obr.universal_service_identifier = CWE(cwe_1='80426-2', cwe_2='Antenatal serology', cwe_3='LN')
        obr.observation_date_time = '20250811083000+0800'
        obr.obr_15 = '9012345T^WATKINS^EMMA^^^DR'
        obr.filler_field_2 = '20250812100000+0800'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='882-1', cwe_2='ABO group', cwe_3='LN')
        obx.obx_5 = 'A'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250812100000+0800'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='10331-7', cwe_2='Rh type', cwe_3='LN')
        obx_2.obx_5 = 'Positive'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250812100000+0800'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='890-4', cwe_2='Antibody screen', cwe_3='LN')
        obx_3.obx_5 = 'No antibodies detected'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250812100000+0800'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='22322-2', cwe_2='Hepatitis B sAg', cwe_3='LN')
        obx_4.obx_5 = 'Negative'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250812100000+0800'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='7905-3', cwe_2='Hepatitis C Ab', cwe_3='LN')
        obx_5.obx_5 = 'Negative'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250812100000+0800'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='22461-8', cwe_2='HIV 1+2 Ab/Ag', cwe_3='LN')
        obx_6.obx_5 = 'Negative'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20250812100000+0800'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='22462-6', cwe_2='Syphilis EIA', cwe_3='LN')
        obx_7.obx_5 = 'Negative'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20250812100000+0800'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'ST'
        obx_8.observation_identifier = CWE(cwe_1='5334-8', cwe_2='Rubella IgG', cwe_3='LN')
        obx_8.obx_5 = 'Immune (>10 IU/mL)'
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20250812100000+0800'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'NM'
        obx_9.observation_identifier = CWE(cwe_1='718-7', cwe_2='Haemoglobin', cwe_3='LN')
        obx_9.obx_5 = '126'
        obx_9.units = CWE(cwe_1='g/L')
        obx_9.reference_range = '115-160'
        obx_9.observation_result_status = 'F'
        obx_9.date_time_of_the_observation = '20250812100000+0800'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

        # .. build OBX ..
        obx_10 = OBX()
        obx_10.set_id_obx = '10'
        obx_10.value_type = 'NM'
        obx_10.observation_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obx_10.obx_5 = '5.2'
        obx_10.units = CWE(cwe_1='%')
        obx_10.reference_range = '<5.5'
        obx_10.observation_result_status = 'F'
        obx_10.date_time_of_the_observation = '20250812100000+0800'

        # .. build the OBSERVATION group ..
        observation_10 = OruR01Observation()
        observation_10.obx = obx_10

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation
        order_observation.observation_2 = observation_2
        order_observation.observation_3 = observation_3
        order_observation.observation_4 = observation_4
        order_observation.observation_5 = observation_5
        order_observation.observation_6 = observation_6
        order_observation.observation_7 = observation_7
        order_observation.observation_8 = observation_8
        order_observation.observation_9 = observation_9
        order_observation.observation_10 = observation_10

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result

        built_er7 = msg.to_hl7v2()

        # .. and assert exact match against the .md file.
        expected_er7 = load_message(_md_path, 20)

        self.assertEqual(built_er7, expected_er7)

# ################################################################################################################################

    def test_parse(self) -> 'None':

        raw = load_message(_md_path, 20)

        # Parse ..
        parsed = parse_hl7(raw, validate=False)

        # .. serialize and reparse ..
        serialized = parsed.to_hl7v2()
        reparsed = parse_hl7(serialized, validate=False)

        # .. and assert roundtrip fidelity.
        reparsed_er7 = reparsed.to_hl7v2()
        self.assertEqual(serialized, reparsed_er7)

        parsed_dict = parsed.to_dict(include_empty=False)
        reparsed_dict = reparsed.to_dict(include_empty=False)
        self.assertEqual(parsed_dict, reparsed_dict)

        parsed_dict_full = parsed.to_dict(include_empty=True)
        reparsed_dict_full = reparsed.to_dict(include_empty=True)
        self.assertEqual(parsed_dict_full, reparsed_dict_full)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
