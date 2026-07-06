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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, EIP, HD, MSG, OG, PL, PT, VID, XAD, XCN, XPN
from zato.hl7v2.v2_9.groups import OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import DG1, MSH, OBR, OBX, ORC, PID, PV1

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ar', 'ar-hl7-lis-unlp.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ar/ar-hl7-lis-unlp.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_HSM')
        msh.sending_facility = HD(hd_1='HOSP_SAN_MARTIN_LP')
        msh.receiving_application = HD(hd_1='LIS_UNLP')
        msh.receiving_facility = HD(hd_1='HOSP_SAN_MARTIN_LAB')
        msh.date_time_of_message = '20250310073000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG10001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='32456789', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='FERNANDEZ', xpn_2='MARIANA SOLEDAD')
        pid.date_time_of_birth = '19880614'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CALLE 51 NRO 890', xad_3='LA PLATA', xad_4='BUENOS AIRES', xad_5='1900', xad_6='AR')
        pid.pid_13 = '0221-4234567'
        pid.patient_account_number = CX(cx_1='32456789')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='34567123', xcn_2='QUIROGA', xcn_3='PABLO', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='CLI')
        pv1.patient_type = CWE(cwe_1='V00020001')
        pv1.prior_temporary_location = PL(pl_1='20250310')

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
        orc.placer_order_number = EI(ei_1='LAB-2025-00100')
        orc.orc_7 = '1^^^20250310073000^^R'
        orc.date_time_of_order_event = '20250310073000'
        orc.orc_10 = '34567123^QUIROGA^PABLO^^^DR'
        orc.orc_12 = '34567123^QUIROGA^PABLO^^^DR'
        orc.enterers_location = PL(pl_1='LAB')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB-2025-00100')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC W AUTO DIFFERENTIAL PANEL', cwe_3='LN')
        obr.observation_date_time = '20250310073000'
        obr.specimen_action_code = 'A'
        obr.obr_16 = '34567123^QUIROGA^PABLO^^^DR'
        obr.obr_26 = '1^^^20250310073000^^R'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

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
    """ Based on live/ar/ar-hl7-lis-unlp.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_HSM')
        msh.sending_facility = HD(hd_1='HOSP_SAN_MARTIN_LP')
        msh.receiving_application = HD(hd_1='LIS_UNLP')
        msh.receiving_facility = HD(hd_1='HOSP_SAN_MARTIN_LAB')
        msh.date_time_of_message = '20250310073100'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG10002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='28901234', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='GARCIA', xpn_2='ROBERTO DANIEL')
        pid.date_time_of_birth = '19760320'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='DIAGONAL 73 NRO 1456', xad_3='LA PLATA', xad_4='BUENOS AIRES', xad_5='1900', xad_6='AR')
        pid.pid_13 = '0221-4567890'
        pid.patient_account_number = CX(cx_1='28901234')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CLI', pl_2='301', pl_3='02')
        pv1.attending_doctor = XCN(xcn_1='33456789', xcn_2='MENDOZA', xcn_3='GRACIELA', xcn_6='DRA')
        pv1.hospital_service = CWE(cwe_1='CLI')
        pv1.patient_type = CWE(cwe_1='V00020050')
        pv1.prior_temporary_location = PL(pl_1='20250310')

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
        orc.placer_order_number = EI(ei_1='LAB-2025-00101')
        orc.orc_7 = '1^^^20250310073100^^R'
        orc.date_time_of_order_event = '20250310073100'
        orc.orc_10 = '33456789^MENDOZA^GRACIELA^^^DRA'
        orc.orc_12 = '33456789^MENDOZA^GRACIELA^^^DRA'
        orc.enterers_location = PL(pl_1='LAB')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB-2025-00101')
        obr.universal_service_identifier = CWE(cwe_1='24320-4', cwe_2='BASIC METABOLIC PANEL', cwe_3='LN')
        obr.observation_date_time = '20250310073100'
        obr.specimen_action_code = 'A'
        obr.obr_16 = '33456789^MENDOZA^GRACIELA^^^DRA'
        obr.obr_26 = '1^^^20250310073100^^R'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

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
    """ Based on live/ar/ar-hl7-lis-unlp.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS_UNLP')
        msh.sending_facility = HD(hd_1='HOSP_SAN_MARTIN_LAB')
        msh.receiving_application = HD(hd_1='HIS_HSM')
        msh.receiving_facility = HD(hd_1='HOSP_SAN_MARTIN_LP')
        msh.date_time_of_message = '20250310143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG10003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='32456789', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='FERNANDEZ', xpn_2='MARIANA SOLEDAD')
        pid.date_time_of_birth = '19880614'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CALLE 51 NRO 890', xad_3='LA PLATA', xad_4='BUENOS AIRES', xad_5='1900', xad_6='AR')
        pid.pid_13 = '0221-4234567'
        pid.patient_account_number = CX(cx_1='32456789')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='34567123', xcn_2='QUIROGA', xcn_3='PABLO', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='CLI')
        pv1.patient_type = CWE(cwe_1='V00020001')
        pv1.prior_temporary_location = PL(pl_1='20250310')

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
        orc.placer_order_number = EI(ei_1='LAB-2025-00100')
        orc.placer_order_group_number = EI(ei_1='LAB-2025-00100-R')
        orc.parent_order = EIP(eip_1='20250310143000')
        orc.date_time_of_order_event = '34567123^QUIROGA^PABLO^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB-2025-00100')
        obr.filler_order_number = EI(ei_1='LAB-2025-00100-R')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC W AUTO DIFFERENTIAL PANEL', cwe_3='LN')
        obr.observation_date_time = '20250310073000'
        obr.obr_14 = '34567123^QUIROGA^PABLO^^^DR'
        obr.placer_field_2 = 'HEM'
        obr.result_status = 'F'
        obr.obr_32 = '34567123^QUIROGA^PABLO^^^DR'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='HEMOGLOBIN', cwe_3='LN')
        obx.obx_5 = '9.8'
        obx.units = CWE(cwe_1='g/dL')
        obx.reference_range = '12.0-16.0'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4544-3', cwe_2='HEMATOCRIT', cwe_3='LN')
        obx_2.obx_5 = '31.2'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '36.0-46.0'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='789-8', cwe_2='ERYTHROCYTES', cwe_3='LN')
        obx_3.obx_5 = '3.45'
        obx_3.units = CWE(cwe_1='10*6/uL')
        obx_3.reference_range = '3.80-5.10'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='787-2', cwe_2='MCV', cwe_3='LN')
        obx_4.obx_5 = '90.4'
        obx_4.units = CWE(cwe_1='fL')
        obx_4.reference_range = '80.0-100.0'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='785-6', cwe_2='MCH', cwe_3='LN')
        obx_5.obx_5 = '28.4'
        obx_5.units = CWE(cwe_1='pg')
        obx_5.reference_range = '27.0-33.0'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='786-4', cwe_2='MCHC', cwe_3='LN')
        obx_6.obx_5 = '31.4'
        obx_6.units = CWE(cwe_1='g/dL')
        obx_6.reference_range = '32.0-36.0'
        obx_6.interpretation_codes = CWE(cwe_1='L')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='6690-2', cwe_2='LEUKOCYTES', cwe_3='LN')
        obx_7.obx_5 = '7.2'
        obx_7.units = CWE(cwe_1='10*3/uL')
        obx_7.reference_range = '4.0-10.0'
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='777-3', cwe_2='PLATELETS', cwe_3='LN')
        obx_8.obx_5 = '245'
        obx_8.units = CWE(cwe_1='10*3/uL')
        obx_8.reference_range = '150-400'
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

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
    """ Based on live/ar/ar-hl7-lis-unlp.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS_UNLP')
        msh.sending_facility = HD(hd_1='HOSP_SAN_MARTIN_LAB')
        msh.receiving_application = HD(hd_1='HIS_HSM')
        msh.receiving_facility = HD(hd_1='HOSP_SAN_MARTIN_LP')
        msh.date_time_of_message = '20250310151500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG10004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='28901234', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='GARCIA', xpn_2='ROBERTO DANIEL')
        pid.date_time_of_birth = '19760320'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='DIAGONAL 73 NRO 1456', xad_3='LA PLATA', xad_4='BUENOS AIRES', xad_5='1900', xad_6='AR')
        pid.pid_13 = '0221-4567890'
        pid.patient_account_number = CX(cx_1='28901234')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CLI', pl_2='301', pl_3='02')
        pv1.attending_doctor = XCN(xcn_1='33456789', xcn_2='MENDOZA', xcn_3='GRACIELA', xcn_6='DRA')
        pv1.hospital_service = CWE(cwe_1='CLI')
        pv1.patient_type = CWE(cwe_1='V00020050')
        pv1.prior_temporary_location = PL(pl_1='20250310')

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
        orc.placer_order_number = EI(ei_1='LAB-2025-00101')
        orc.placer_order_group_number = EI(ei_1='LAB-2025-00101-R')
        orc.parent_order = EIP(eip_1='20250310151500')
        orc.date_time_of_order_event = '33456789^MENDOZA^GRACIELA^^^DRA'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB-2025-00101')
        obr.filler_order_number = EI(ei_1='LAB-2025-00101-R')
        obr.universal_service_identifier = CWE(cwe_1='24320-4', cwe_2='BASIC METABOLIC PANEL', cwe_3='LN')
        obr.observation_date_time = '20250310073100'
        obr.obr_14 = '33456789^MENDOZA^GRACIELA^^^DRA'
        obr.placer_field_2 = 'BIO'
        obr.result_status = 'F'
        obr.obr_32 = '33456789^MENDOZA^GRACIELA^^^DRA'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='GLUCOSE', cwe_3='LN')
        obx.obx_5 = '248'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '70-110'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='CREATININE', cwe_3='LN')
        obx_2.obx_5 = '1.1'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '0.7-1.3'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='BUN', cwe_3='LN')
        obx_3.obx_5 = '22'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '7-20'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='SODIUM', cwe_3='LN')
        obx_4.obx_5 = '141'
        obx_4.units = CWE(cwe_1='mEq/L')
        obx_4.reference_range = '136-145'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='POTASSIUM', cwe_3='LN')
        obx_5.obx_5 = '4.6'
        obx_5.units = CWE(cwe_1='mEq/L')
        obx_5.reference_range = '3.5-5.1'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2075-0', cwe_2='CHLORIDE', cwe_3='LN')
        obx_6.obx_5 = '103'
        obx_6.units = CWE(cwe_1='mEq/L')
        obx_6.reference_range = '98-106'
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='1963-8', cwe_2='BICARBONATE', cwe_3='LN')
        obx_7.obx_5 = '24'
        obx_7.units = CWE(cwe_1='mEq/L')
        obx_7.reference_range = '22-29'
        obx_7.observation_result_status = 'F'

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
    """ Based on live/ar/ar-hl7-lis-unlp.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_HITALIANO')
        msh.sending_facility = HD(hd_1='HOSP_ITALIANO_LP')
        msh.receiving_application = HD(hd_1='LIS_UNLP')
        msh.receiving_facility = HD(hd_1='HOSP_ITALIANO_LP_LAB')
        msh.date_time_of_message = '20250312080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG10005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='30789456', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='MARTINEZ', xpn_2='CLAUDIA ELENA')
        pid.date_time_of_birth = '19850911'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CALLE 4 NRO 567', xad_3='LA PLATA', xad_4='BUENOS AIRES', xad_5='1900', xad_6='AR')
        pid.pid_13 = '0221-4891234'
        pid.patient_account_number = CX(cx_1='30789456')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='31234567', xcn_2='ORTIZ', xcn_3='VALENTINA', xcn_6='DRA')
        pv1.hospital_service = CWE(cwe_1='CLI')
        pv1.patient_type = CWE(cwe_1='V00020200')
        pv1.prior_temporary_location = PL(pl_1='20250312')

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
        orc.placer_order_number = EI(ei_1='LAB-2025-00200')
        orc.orc_7 = '1^^^20250312080000^^R'
        orc.date_time_of_order_event = '20250312080000'
        orc.orc_10 = '31234567^ORTIZ^VALENTINA^^^DRA'
        orc.orc_12 = '31234567^ORTIZ^VALENTINA^^^DRA'
        orc.enterers_location = PL(pl_1='LAB')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB-2025-00200')
        obr.universal_service_identifier = CWE(cwe_1='24331-1', cwe_2='LIPID PANEL', cwe_3='LN')
        obr.observation_date_time = '20250312080000'
        obr.specimen_action_code = 'A'
        obr.obr_16 = '31234567^ORTIZ^VALENTINA^^^DRA'
        obr.obr_26 = '1^^^20250312080000^^R'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

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
    """ Based on live/ar/ar-hl7-lis-unlp.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS_UNLP')
        msh.sending_facility = HD(hd_1='HOSP_ITALIANO_LP_LAB')
        msh.receiving_application = HD(hd_1='HIS_HITALIANO')
        msh.receiving_facility = HD(hd_1='HOSP_ITALIANO_LP')
        msh.date_time_of_message = '20250312140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG10006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='30789456', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='MARTINEZ', xpn_2='CLAUDIA ELENA')
        pid.date_time_of_birth = '19850911'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CALLE 4 NRO 567', xad_3='LA PLATA', xad_4='BUENOS AIRES', xad_5='1900', xad_6='AR')
        pid.pid_13 = '0221-4891234'
        pid.patient_account_number = CX(cx_1='30789456')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='31234567', xcn_2='ORTIZ', xcn_3='VALENTINA', xcn_6='DRA')
        pv1.hospital_service = CWE(cwe_1='CLI')
        pv1.patient_type = CWE(cwe_1='V00020200')
        pv1.prior_temporary_location = PL(pl_1='20250312')

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
        orc.placer_order_number = EI(ei_1='LAB-2025-00200')
        orc.placer_order_group_number = EI(ei_1='LAB-2025-00200-R')
        orc.parent_order = EIP(eip_1='20250312140000')
        orc.date_time_of_order_event = '31234567^ORTIZ^VALENTINA^^^DRA'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB-2025-00200')
        obr.filler_order_number = EI(ei_1='LAB-2025-00200-R')
        obr.universal_service_identifier = CWE(cwe_1='24331-1', cwe_2='LIPID PANEL', cwe_3='LN')
        obr.observation_date_time = '20250312080000'
        obr.obr_14 = '31234567^ORTIZ^VALENTINA^^^DRA'
        obr.placer_field_2 = 'BIO'
        obr.result_status = 'F'
        obr.obr_32 = '31234567^ORTIZ^VALENTINA^^^DRA'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2093-3', cwe_2='CHOLESTEROL TOTAL', cwe_3='LN')
        obx.obx_5 = '267'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '<200'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2571-8', cwe_2='TRIGLYCERIDES', cwe_3='LN')
        obx_2.obx_5 = '312'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '<150'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2085-9', cwe_2='HDL CHOLESTEROL', cwe_3='LN')
        obx_3.obx_5 = '38'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '>40'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='13457-7', cwe_2='LDL CHOLESTEROL CALC', cwe_3='LN')
        obx_4.obx_5 = '166'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '<130'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='13458-5', cwe_2='VLDL CHOLESTEROL CALC', cwe_3='LN')
        obx_5.obx_5 = '62.4'
        obx_5.units = CWE(cwe_1='mg/dL')
        obx_5.reference_range = '<30'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'

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
    """ Based on live/ar/ar-hl7-lis-unlp.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_HSM')
        msh.sending_facility = HD(hd_1='HOSP_SAN_MARTIN_LP')
        msh.receiving_application = HD(hd_1='LIS_UNLP')
        msh.receiving_facility = HD(hd_1='HOSP_SAN_MARTIN_LAB')
        msh.date_time_of_message = '20250315090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG10007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='27345678', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='SUAREZ', xpn_2='ALICIA MABEL')
        pid.date_time_of_birth = '19720508'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CALLE 12 NRO 1890', xad_3='LA PLATA', xad_4='BUENOS AIRES', xad_5='1900', xad_6='AR')
        pid.pid_13 = '0221-4256789'
        pid.patient_account_number = CX(cx_1='27345678')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='30987654', xcn_2='PERALTA', xcn_3='ESTEBAN', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='END')
        pv1.patient_type = CWE(cwe_1='V00020350')
        pv1.prior_temporary_location = PL(pl_1='20250315')

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
        orc.placer_order_number = EI(ei_1='LAB-2025-00350')
        orc.orc_7 = '1^^^20250315090000^^R'
        orc.date_time_of_order_event = '20250315090000'
        orc.orc_10 = '30987654^PERALTA^ESTEBAN^^^DR'
        orc.orc_12 = '30987654^PERALTA^ESTEBAN^^^DR'
        orc.enterers_location = PL(pl_1='LAB')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB-2025-00350')
        obr.universal_service_identifier = CWE(cwe_1='34015-4', cwe_2='THYROID FUNCTION PANEL', cwe_3='LN')
        obr.observation_date_time = '20250315090000'
        obr.specimen_action_code = 'A'
        obr.obr_16 = '30987654^PERALTA^ESTEBAN^^^DR'
        obr.obr_26 = '1^^^20250315090000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='E03.9', cwe_2='HIPOTIROIDISMO NO ESPECIFICADO', cwe_3='ICD10AR')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

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
    """ Based on live/ar/ar-hl7-lis-unlp.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS_UNLP')
        msh.sending_facility = HD(hd_1='HOSP_SAN_MARTIN_LAB')
        msh.receiving_application = HD(hd_1='HIS_HSM')
        msh.receiving_facility = HD(hd_1='HOSP_SAN_MARTIN_LP')
        msh.date_time_of_message = '20250315163000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG10008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='27345678', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='SUAREZ', xpn_2='ALICIA MABEL')
        pid.date_time_of_birth = '19720508'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CALLE 12 NRO 1890', xad_3='LA PLATA', xad_4='BUENOS AIRES', xad_5='1900', xad_6='AR')
        pid.pid_13 = '0221-4256789'
        pid.patient_account_number = CX(cx_1='27345678')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='30987654', xcn_2='PERALTA', xcn_3='ESTEBAN', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='END')
        pv1.patient_type = CWE(cwe_1='V00020350')
        pv1.prior_temporary_location = PL(pl_1='20250315')

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
        orc.placer_order_number = EI(ei_1='LAB-2025-00350')
        orc.placer_order_group_number = EI(ei_1='LAB-2025-00350-R')
        orc.parent_order = EIP(eip_1='20250315163000')
        orc.date_time_of_order_event = '30987654^PERALTA^ESTEBAN^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB-2025-00350')
        obr.filler_order_number = EI(ei_1='LAB-2025-00350-R')
        obr.universal_service_identifier = CWE(cwe_1='34015-4', cwe_2='THYROID FUNCTION PANEL', cwe_3='LN')
        obr.observation_date_time = '20250315090000'
        obr.obr_14 = '30987654^PERALTA^ESTEBAN^^^DR'
        obr.placer_field_2 = 'INM'
        obr.result_status = 'F'
        obr.obr_32 = '30987654^PERALTA^ESTEBAN^^^DR'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='TSH', cwe_3='LN')
        obx.obx_5 = '12.8'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.4-4.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3026-2', cwe_2='FREE T4', cwe_3='LN')
        obx_2.obx_5 = '0.6'
        obx_2.units = CWE(cwe_1='ng/dL')
        obx_2.reference_range = '0.8-1.8'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3053-6', cwe_2='FREE T3', cwe_3='LN')
        obx_3.obx_5 = '1.9'
        obx_3.units = CWE(cwe_1='pg/mL')
        obx_3.reference_range = '2.3-4.2'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='5384-6', cwe_2='ANTI-TPO ANTIBODIES', cwe_3='LN')
        obx_4.obx_5 = '385'
        obx_4.units = CWE(cwe_1='IU/mL')
        obx_4.reference_range = '<35'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

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
    """ Based on live/ar/ar-hl7-lis-unlp.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_HSM')
        msh.sending_facility = HD(hd_1='HOSP_SAN_MARTIN_LP')
        msh.receiving_application = HD(hd_1='LIS_UNLP')
        msh.receiving_facility = HD(hd_1='HOSP_SAN_MARTIN_MICRO')
        msh.date_time_of_message = '20250318100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG10009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='35123456', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='ROJAS', xpn_2='LUCIANA BELEN')
        pid.date_time_of_birth = '19930217'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CALLE 60 NRO 234', xad_3='LA PLATA', xad_4='BUENOS AIRES', xad_5='1900', xad_6='AR')
        pid.pid_13 = '0221-4678901'
        pid.patient_account_number = CX(cx_1='35123456')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='GUA', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='32678901', xcn_2='DIAZ', xcn_3='ALEJANDRO', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='URO')
        pv1.patient_type = CWE(cwe_1='V00020500')
        pv1.prior_temporary_location = PL(pl_1='20250318')

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
        orc.placer_order_number = EI(ei_1='LAB-2025-00500')
        orc.orc_7 = '1^^^20250318100000^^R'
        orc.date_time_of_order_event = '20250318100000'
        orc.orc_10 = '32678901^DIAZ^ALEJANDRO^^^DR'
        orc.orc_12 = '32678901^DIAZ^ALEJANDRO^^^DR'
        orc.enterers_location = PL(pl_1='MICRO')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB-2025-00500')
        obr.universal_service_identifier = CWE(cwe_1='630-4', cwe_2='BACTERIA IDENTIFIED URINE CULTURE', cwe_3='LN')
        obr.observation_date_time = '20250318100000'
        obr.specimen_action_code = 'A'
        obr.obr_16 = '32678901^DIAZ^ALEJANDRO^^^DR'
        obr.obr_26 = '1^^^20250318100000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='N39.0', cwe_2='INFECCION DE VIAS URINARIAS SITIO NO ESPECIFICADO', cwe_3='ICD10AR')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

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
    """ Based on live/ar/ar-hl7-lis-unlp.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS_UNLP')
        msh.sending_facility = HD(hd_1='HOSP_SAN_MARTIN_MICRO')
        msh.receiving_application = HD(hd_1='HIS_HSM')
        msh.receiving_facility = HD(hd_1='HOSP_SAN_MARTIN_LP')
        msh.date_time_of_message = '20250320160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG10010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='35123456', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='ROJAS', xpn_2='LUCIANA BELEN')
        pid.date_time_of_birth = '19930217'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CALLE 60 NRO 234', xad_3='LA PLATA', xad_4='BUENOS AIRES', xad_5='1900', xad_6='AR')
        pid.pid_13 = '0221-4678901'
        pid.patient_account_number = CX(cx_1='35123456')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='GUA', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='32678901', xcn_2='DIAZ', xcn_3='ALEJANDRO', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='URO')
        pv1.patient_type = CWE(cwe_1='V00020500')
        pv1.prior_temporary_location = PL(pl_1='20250320')

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
        orc.placer_order_number = EI(ei_1='LAB-2025-00500')
        orc.placer_order_group_number = EI(ei_1='LAB-2025-00500-R')
        orc.parent_order = EIP(eip_1='20250320160000')
        orc.date_time_of_order_event = '32678901^DIAZ^ALEJANDRO^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB-2025-00500')
        obr.filler_order_number = EI(ei_1='LAB-2025-00500-R')
        obr.universal_service_identifier = CWE(cwe_1='630-4', cwe_2='BACTERIA IDENTIFIED URINE CULTURE', cwe_3='LN')
        obr.observation_date_time = '20250318100000'
        obr.obr_14 = '32678901^DIAZ^ALEJANDRO^^^DR'
        obr.placer_field_2 = 'MICRO'
        obr.result_status = 'F'
        obr.obr_32 = '32678901^DIAZ^ALEJANDRO^^^DR'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='630-4', cwe_2='BACTERIA IDENTIFIED', cwe_3='LN')
        obx.obx_5 = 'Escherichia coli'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='564-5', cwe_2='COLONY COUNT', cwe_3='LN')
        obx_2.obx_5 = '>100000'
        obx_2.units = CWE(cwe_1='UFC/mL')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18862-3', cwe_2='AMPICILLIN SUSC', cwe_3='LN')
        obx_3.obx_5 = 'R'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18878-9', cwe_2='CIPROFLOXACIN SUSC', cwe_3='LN')
        obx_4.obx_5 = 'S'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18932-4', cwe_2='NITROFURANTOIN SUSC', cwe_3='LN')
        obx_5.obx_5 = 'S'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='18964-7', cwe_2='TMP-SMX SUSC', cwe_3='LN')
        obx_6.obx_5 = 'R'
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='18886-2', cwe_2='CEFTRIAXONE SUSC', cwe_3='LN')
        obx_7.obx_5 = 'S'
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'ST'
        obx_8.observation_identifier = CWE(cwe_1='18906-8', cwe_2='GENTAMICIN SUSC', cwe_3='LN')
        obx_8.obx_5 = 'S'
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

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
    """ Based on live/ar/ar-hl7-lis-unlp.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_HITALIANO')
        msh.sending_facility = HD(hd_1='HOSP_ITALIANO_LP')
        msh.receiving_application = HD(hd_1='LIS_UNLP')
        msh.receiving_facility = HD(hd_1='HOSP_ITALIANO_LP_LAB')
        msh.date_time_of_message = '20250322070000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG10011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='26789012', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='PONCE', xpn_2='EDUARDO NICOLAS')
        pid.date_time_of_birth = '19680825'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CALLE 48 NRO 678', xad_3='LA PLATA', xad_4='BUENOS AIRES', xad_5='1900', xad_6='AR')
        pid.pid_13 = '0221-4345678'
        pid.patient_account_number = CX(cx_1='26789012')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CIR', pl_2='205', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='29876543', xcn_2='COLOMBO', xcn_3='FEDERICO', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='CIR')
        pv1.patient_type = CWE(cwe_1='V00020700')
        pv1.prior_temporary_location = PL(pl_1='20250322')

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
        orc.placer_order_number = EI(ei_1='LAB-2025-00700')
        orc.orc_7 = '1^^^20250322070000^^R'
        orc.date_time_of_order_event = '20250322070000'
        orc.orc_10 = '29876543^COLOMBO^FEDERICO^^^DR'
        orc.orc_12 = '29876543^COLOMBO^FEDERICO^^^DR'
        orc.enterers_location = PL(pl_1='LAB')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB-2025-00700')
        obr.universal_service_identifier = CWE(cwe_1='62388-4', cwe_2='COAGULATION PANEL', cwe_3='LN')
        obr.observation_date_time = '20250322070000'
        obr.specimen_action_code = 'A'
        obr.obr_16 = '29876543^COLOMBO^FEDERICO^^^DR'
        obr.obr_26 = '1^^^20250322070000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='Z01.818', cwe_2='EXAMEN PREOPERATORIO', cwe_3='ICD10AR')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

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
    """ Based on live/ar/ar-hl7-lis-unlp.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS_UNLP')
        msh.sending_facility = HD(hd_1='HOSP_ITALIANO_LP_LAB')
        msh.receiving_application = HD(hd_1='HIS_HITALIANO')
        msh.receiving_facility = HD(hd_1='HOSP_ITALIANO_LP')
        msh.date_time_of_message = '20250322120000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG10012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='26789012', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='PONCE', xpn_2='EDUARDO NICOLAS')
        pid.date_time_of_birth = '19680825'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CALLE 48 NRO 678', xad_3='LA PLATA', xad_4='BUENOS AIRES', xad_5='1900', xad_6='AR')
        pid.pid_13 = '0221-4345678'
        pid.patient_account_number = CX(cx_1='26789012')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CIR', pl_2='205', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='29876543', xcn_2='COLOMBO', xcn_3='FEDERICO', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='CIR')
        pv1.patient_type = CWE(cwe_1='V00020700')
        pv1.prior_temporary_location = PL(pl_1='20250322')

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
        orc.placer_order_number = EI(ei_1='LAB-2025-00700')
        orc.placer_order_group_number = EI(ei_1='LAB-2025-00700-R')
        orc.parent_order = EIP(eip_1='20250322120000')
        orc.date_time_of_order_event = '29876543^COLOMBO^FEDERICO^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB-2025-00700')
        obr.filler_order_number = EI(ei_1='LAB-2025-00700-R')
        obr.universal_service_identifier = CWE(cwe_1='62388-4', cwe_2='COAGULATION PANEL', cwe_3='LN')
        obr.observation_date_time = '20250322070000'
        obr.obr_14 = '29876543^COLOMBO^FEDERICO^^^DR'
        obr.placer_field_2 = 'HEM'
        obr.result_status = 'F'
        obr.obr_32 = '29876543^COLOMBO^FEDERICO^^^DR'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='PROTHROMBIN TIME', cwe_3='LN')
        obx.obx_5 = '13.2'
        obx.units = CWE(cwe_1='seconds')
        obx.reference_range = '11.0-14.5'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx_2.obx_5 = '1.05'
        obx_2.reference_range = '0.8-1.2'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3173-2', cwe_2='APTT', cwe_3='LN')
        obx_3.obx_5 = '32.1'
        obx_3.units = CWE(cwe_1='seconds')
        obx_3.reference_range = '25.0-38.0'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='3255-7', cwe_2='FIBRINOGEN', cwe_3='LN')
        obx_4.obx_5 = '285'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '200-400'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='PLATELETS', cwe_3='LN')
        obx_5.obx_5 = '198'
        obx_5.units = CWE(cwe_1='10*3/uL')
        obx_5.reference_range = '150-400'
        obx_5.observation_result_status = 'F'

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
    """ Based on live/ar/ar-hl7-lis-unlp.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_HSM')
        msh.sending_facility = HD(hd_1='HOSP_SAN_MARTIN_LP')
        msh.receiving_application = HD(hd_1='LIS_UNLP')
        msh.receiving_facility = HD(hd_1='HOSP_SAN_MARTIN_LAB')
        msh.date_time_of_message = '20250325080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG10013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='28901234', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='GARCIA', xpn_2='ROBERTO DANIEL')
        pid.date_time_of_birth = '19760320'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='DIAGONAL 73 NRO 1456', xad_3='LA PLATA', xad_4='BUENOS AIRES', xad_5='1900', xad_6='AR')
        pid.pid_13 = '0221-4567890'
        pid.patient_account_number = CX(cx_1='28901234')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='33456789', xcn_2='MENDOZA', xcn_3='GRACIELA', xcn_6='DRA')
        pv1.hospital_service = CWE(cwe_1='CLI')
        pv1.patient_type = CWE(cwe_1='V00020900')
        pv1.prior_temporary_location = PL(pl_1='20250325')

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
        orc.placer_order_number = EI(ei_1='LAB-2025-00900')
        orc.orc_7 = '1^^^20250325080000^^R'
        orc.date_time_of_order_event = '20250325080000'
        orc.orc_10 = '33456789^MENDOZA^GRACIELA^^^DRA'
        orc.orc_12 = '33456789^MENDOZA^GRACIELA^^^DRA'
        orc.enterers_location = PL(pl_1='LAB')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB-2025-00900')
        obr.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='HEMOGLOBIN A1C', cwe_3='LN')
        obr.observation_date_time = '20250325080000'
        obr.specimen_action_code = 'A'
        obr.obr_16 = '33456789^MENDOZA^GRACIELA^^^DRA'
        obr.obr_26 = '1^^^20250325080000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='E11.9', cwe_2='DIABETES MELLITUS TIPO 2 SIN COMPLICACIONES', cwe_3='ICD10AR')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

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
    """ Based on live/ar/ar-hl7-lis-unlp.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS_UNLP')
        msh.sending_facility = HD(hd_1='HOSP_SAN_MARTIN_LAB')
        msh.receiving_application = HD(hd_1='HIS_HSM')
        msh.receiving_facility = HD(hd_1='HOSP_SAN_MARTIN_LP')
        msh.date_time_of_message = '20250325143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG10014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='28901234', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='GARCIA', xpn_2='ROBERTO DANIEL')
        pid.date_time_of_birth = '19760320'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='DIAGONAL 73 NRO 1456', xad_3='LA PLATA', xad_4='BUENOS AIRES', xad_5='1900', xad_6='AR')
        pid.pid_13 = '0221-4567890'
        pid.patient_account_number = CX(cx_1='28901234')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='33456789', xcn_2='MENDOZA', xcn_3='GRACIELA', xcn_6='DRA')
        pv1.hospital_service = CWE(cwe_1='CLI')
        pv1.patient_type = CWE(cwe_1='V00020900')
        pv1.prior_temporary_location = PL(pl_1='20250325')

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
        orc.placer_order_number = EI(ei_1='LAB-2025-00900')
        orc.placer_order_group_number = EI(ei_1='LAB-2025-00900-R')
        orc.parent_order = EIP(eip_1='20250325143000')
        orc.date_time_of_order_event = '33456789^MENDOZA^GRACIELA^^^DRA'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB-2025-00900')
        obr.filler_order_number = EI(ei_1='LAB-2025-00900-R')
        obr.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='HEMOGLOBIN A1C', cwe_3='LN')
        obr.observation_date_time = '20250325080000'
        obr.obr_14 = '33456789^MENDOZA^GRACIELA^^^DRA'
        obr.placer_field_2 = 'BIO'
        obr.result_status = 'F'
        obr.obr_32 = '33456789^MENDOZA^GRACIELA^^^DRA'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='HEMOGLOBIN A1C', cwe_3='LN')
        obx.obx_5 = '9.2'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '<7.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2345-7', cwe_2='GLUCOSE FASTING', cwe_3='LN')
        obx_2.obx_5 = '198'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '70-110'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='14749-6', cwe_2='GLUCOSE 2HR POST 75G GLUCOSE', cwe_3='LN')
        obx_3.obx_5 = '312'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '<140'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'TX'
        obx_4.observation_identifier = CWE(cwe_1='4548-4', cwe_2='HEMOGLOBIN A1C', cwe_3='LN')
        obx_4.obx_5 = 'Control glicemico deficiente. Se recomienda ajuste de tratamiento y control nutricional.'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ED'
        obx_5.observation_identifier = CWE(cwe_1='PDF', cwe_2='Informe Completo Laboratorio Diabetologico', cwe_3='AUSPDI')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = (
            'LIS_UNLP^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4K'
        )
        obx_5.observation_result_status = 'F'

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
    """ Based on live/ar/ar-hl7-lis-unlp.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_HSM')
        msh.sending_facility = HD(hd_1='HOSP_SAN_MARTIN_LP')
        msh.receiving_application = HD(hd_1='LIS_UNLP')
        msh.receiving_facility = HD(hd_1='HOSP_SAN_MARTIN_MICRO')
        msh.date_time_of_message = '20250328060000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG10015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='24567890', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='MOLINA', xpn_2='JUAN CARLOS')
        pid.date_time_of_birth = '19600415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CALLE 44 NRO 1200', xad_3='LA PLATA', xad_4='BUENOS AIRES', xad_5='1900', xad_6='AR')
        pid.pid_13 = '0221-4123456'
        pid.patient_account_number = CX(cx_1='24567890')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='UTI', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='31890123', xcn_2='VEGA', xcn_3='SUSANA', xcn_6='DRA')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='V00021100')
        pv1.prior_temporary_location = PL(pl_1='20250328')

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
        orc.placer_order_number = EI(ei_1='LAB-2025-01100')
        orc.orc_7 = '1^^^20250328060000^^S'
        orc.date_time_of_order_event = '20250328060000'
        orc.orc_10 = '31890123^VEGA^SUSANA^^^DRA'
        orc.orc_12 = '31890123^VEGA^SUSANA^^^DRA'
        orc.enterers_location = PL(pl_1='MICRO')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB-2025-01100')
        obr.universal_service_identifier = CWE(cwe_1='600-7', cwe_2='BACTERIA IDENTIFIED BLOOD CULTURE', cwe_3='LN')
        obr.observation_date_time = '20250328060000'
        obr.specimen_action_code = 'A'
        obr.obr_16 = '31890123^VEGA^SUSANA^^^DRA'
        obr.obr_26 = '1^^^20250328060000^^S'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='A41.9', cwe_2='SEPTICEMIA NO ESPECIFICADA', cwe_3='ICD10AR')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

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
    """ Based on live/ar/ar-hl7-lis-unlp.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS_UNLP')
        msh.sending_facility = HD(hd_1='HOSP_SAN_MARTIN_MICRO')
        msh.receiving_application = HD(hd_1='HIS_HSM')
        msh.receiving_facility = HD(hd_1='HOSP_SAN_MARTIN_LP')
        msh.date_time_of_message = '20250330180000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG10016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='24567890', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='MOLINA', xpn_2='JUAN CARLOS')
        pid.date_time_of_birth = '19600415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CALLE 44 NRO 1200', xad_3='LA PLATA', xad_4='BUENOS AIRES', xad_5='1900', xad_6='AR')
        pid.pid_13 = '0221-4123456'
        pid.patient_account_number = CX(cx_1='24567890')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='UTI', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='31890123', xcn_2='VEGA', xcn_3='SUSANA', xcn_6='DRA')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='V00021100')
        pv1.prior_temporary_location = PL(pl_1='20250330')

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
        orc.placer_order_number = EI(ei_1='LAB-2025-01100')
        orc.placer_order_group_number = EI(ei_1='LAB-2025-01100-R')
        orc.parent_order = EIP(eip_1='20250330180000')
        orc.date_time_of_order_event = '31890123^VEGA^SUSANA^^^DRA'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB-2025-01100')
        obr.filler_order_number = EI(ei_1='LAB-2025-01100-R')
        obr.universal_service_identifier = CWE(cwe_1='600-7', cwe_2='BACTERIA IDENTIFIED BLOOD CULTURE', cwe_3='LN')
        obr.observation_date_time = '20250328060000'
        obr.obr_14 = '31890123^VEGA^SUSANA^^^DRA'
        obr.placer_field_2 = 'MICRO'
        obr.result_status = 'F'
        obr.obr_32 = '31890123^VEGA^SUSANA^^^DRA'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='BACTERIA IDENTIFIED', cwe_3='LN')
        obx.obx_5 = 'Staphylococcus aureus'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='6462-6', cwe_2='OXACILLIN SUSC', cwe_3='LN')
        obx_2.obx_5 = 'S'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18878-9', cwe_2='CIPROFLOXACIN SUSC', cwe_3='LN')
        obx_3.obx_5 = 'S'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18906-8', cwe_2='GENTAMICIN SUSC', cwe_3='LN')
        obx_4.obx_5 = 'S'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18996-9', cwe_2='VANCOMYCIN SUSC', cwe_3='LN')
        obx_5.obx_5 = 'S'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='18886-2', cwe_2='CEFTRIAXONE SUSC', cwe_3='LN')
        obx_6.obx_5 = 'S'
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='18964-7', cwe_2='TMP-SMX SUSC', cwe_3='LN')
        obx_7.obx_5 = 'S'
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'ST'
        obx_8.observation_identifier = CWE(cwe_1='18862-3', cwe_2='CLINDAMYCIN SUSC', cwe_3='LN')
        obx_8.obx_5 = 'S'
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

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
    """ Based on live/ar/ar-hl7-lis-unlp.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_HITALIANO')
        msh.sending_facility = HD(hd_1='HOSP_ITALIANO_LP')
        msh.receiving_application = HD(hd_1='LIS_UNLP')
        msh.receiving_facility = HD(hd_1='HOSP_ITALIANO_LP_LAB')
        msh.date_time_of_message = '20250401090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG10017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='31456789', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='AGUIRRE', xpn_2='DANIELA PAOLA')
        pid.date_time_of_birth = '19870630'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CALLE 8 NRO 1045', xad_3='LA PLATA', xad_4='BUENOS AIRES', xad_5='1900', xad_6='AR')
        pid.pid_13 = '0221-4789012'
        pid.patient_account_number = CX(cx_1='31456789')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='30345678', xcn_2='LUNA', xcn_3='VICTORIA', xcn_6='DRA')
        pv1.hospital_service = CWE(cwe_1='GAS')
        pv1.patient_type = CWE(cwe_1='V00021300')
        pv1.prior_temporary_location = PL(pl_1='20250401')

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
        orc.placer_order_number = EI(ei_1='LAB-2025-01300')
        orc.orc_7 = '1^^^20250401090000^^R'
        orc.date_time_of_order_event = '20250401090000'
        orc.orc_10 = '30345678^LUNA^VICTORIA^^^DRA'
        orc.orc_12 = '30345678^LUNA^VICTORIA^^^DRA'
        orc.enterers_location = PL(pl_1='LAB')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB-2025-01300')
        obr.universal_service_identifier = CWE(cwe_1='24362-6', cwe_2='HEPATIC FUNCTION PANEL', cwe_3='LN')
        obr.observation_date_time = '20250401090000'
        obr.specimen_action_code = 'A'
        obr.obr_16 = '30345678^LUNA^VICTORIA^^^DRA'
        obr.obr_26 = '1^^^20250401090000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K73.9', cwe_2='HEPATITIS CRONICA NO ESPECIFICADA', cwe_3='ICD10AR')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

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
    """ Based on live/ar/ar-hl7-lis-unlp.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS_UNLP')
        msh.sending_facility = HD(hd_1='HOSP_ITALIANO_LP_LAB')
        msh.receiving_application = HD(hd_1='HIS_HITALIANO')
        msh.receiving_facility = HD(hd_1='HOSP_ITALIANO_LP')
        msh.date_time_of_message = '20250401160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG10018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='31456789', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='AGUIRRE', xpn_2='DANIELA PAOLA')
        pid.date_time_of_birth = '19870630'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CALLE 8 NRO 1045', xad_3='LA PLATA', xad_4='BUENOS AIRES', xad_5='1900', xad_6='AR')
        pid.pid_13 = '0221-4789012'
        pid.patient_account_number = CX(cx_1='31456789')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='30345678', xcn_2='LUNA', xcn_3='VICTORIA', xcn_6='DRA')
        pv1.hospital_service = CWE(cwe_1='GAS')
        pv1.patient_type = CWE(cwe_1='V00021300')
        pv1.prior_temporary_location = PL(pl_1='20250401')

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
        orc.placer_order_number = EI(ei_1='LAB-2025-01300')
        orc.placer_order_group_number = EI(ei_1='LAB-2025-01300-R')
        orc.parent_order = EIP(eip_1='20250401160000')
        orc.date_time_of_order_event = '30345678^LUNA^VICTORIA^^^DRA'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB-2025-01300')
        obr.filler_order_number = EI(ei_1='LAB-2025-01300-R')
        obr.universal_service_identifier = CWE(cwe_1='24362-6', cwe_2='HEPATIC FUNCTION PANEL', cwe_3='LN')
        obr.observation_date_time = '20250401090000'
        obr.obr_14 = '30345678^LUNA^VICTORIA^^^DRA'
        obr.placer_field_2 = 'INM'
        obr.result_status = 'F'
        obr.obr_32 = '30345678^LUNA^VICTORIA^^^DRA'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='5196-1', cwe_2='HBsAg', cwe_3='LN')
        obx.obx_5 = 'No Reactivo'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='16933-4', cwe_2='ANTI-HBs', cwe_3='LN')
        obx_2.obx_5 = 'Reactivo (>100 mIU/mL)'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='13955-0', cwe_2='ANTI-HBc TOTAL', cwe_3='LN')
        obx_3.obx_5 = 'No Reactivo'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='16128-1', cwe_2='ANTI-HCV', cwe_3='LN')
        obx_4.obx_5 = 'Reactivo'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='11259-9', cwe_2='HCV RNA QUANT', cwe_3='LN')
        obx_5.obx_5 = '1.85E6'
        obx_5.units = CWE(cwe_1='IU/mL')
        obx_5.reference_range = '<15 (no detectado)'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='32286-7', cwe_2='HCV GENOTYPE', cwe_3='LN')
        obx_6.obx_5 = 'Genotipo 1b'
        obx_6.observation_result_status = 'F'

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
    """ Based on live/ar/ar-hl7-lis-unlp.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_HSM')
        msh.sending_facility = HD(hd_1='HOSP_SAN_MARTIN_LP')
        msh.receiving_application = HD(hd_1='LIS_UNLP')
        msh.receiving_facility = HD(hd_1='HOSP_SAN_MARTIN_LAB')
        msh.date_time_of_message = '20250405100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG10019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='33890123', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='CAMPOS', xpn_2='NATALIA INES')
        pid.date_time_of_birth = '19910803'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CALLE 13 NRO 456', xad_3='LA PLATA', xad_4='BUENOS AIRES', xad_5='1900', xad_6='AR')
        pid.pid_13 = '0221-4901234'
        pid.patient_account_number = CX(cx_1='33890123')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='32123456', xcn_2='IRIARTE', xcn_3='MARIANO', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='REU')
        pv1.patient_type = CWE(cwe_1='V00021500')
        pv1.prior_temporary_location = PL(pl_1='20250405')

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
        orc.placer_order_number = EI(ei_1='LAB-2025-01500')
        orc.orc_7 = '1^^^20250405100000^^R'
        orc.date_time_of_order_event = '20250405100000'
        orc.orc_10 = '32123456^IRIARTE^MARIANO^^^DR'
        orc.orc_12 = '32123456^IRIARTE^MARIANO^^^DR'
        orc.enterers_location = PL(pl_1='LAB')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB-2025-01500')
        obr.universal_service_identifier = CWE(cwe_1='57021-8', cwe_2='ANA PANEL', cwe_3='LN')
        obr.observation_date_time = '20250405100000'
        obr.specimen_action_code = 'A'
        obr.obr_16 = '32123456^IRIARTE^MARIANO^^^DR'
        obr.obr_26 = '1^^^20250405100000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M32.9', cwe_2='LUPUS ERITEMATOSO SISTEMICO NO ESPECIFICADO', cwe_3='ICD10AR')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

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
    """ Based on live/ar/ar-hl7-lis-unlp.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS_UNLP')
        msh.sending_facility = HD(hd_1='HOSP_SAN_MARTIN_LAB')
        msh.receiving_application = HD(hd_1='HIS_HSM')
        msh.receiving_facility = HD(hd_1='HOSP_SAN_MARTIN_LP')
        msh.date_time_of_message = '20250405170000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG10020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'AR'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='33890123', cx_4='RENAPER', cx_5='NI')
        pid.patient_name = XPN(xpn_1='CAMPOS', xpn_2='NATALIA INES')
        pid.date_time_of_birth = '19910803'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CALLE 13 NRO 456', xad_3='LA PLATA', xad_4='BUENOS AIRES', xad_5='1900', xad_6='AR')
        pid.pid_13 = '0221-4901234'
        pid.patient_account_number = CX(cx_1='33890123')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='LAB', pl_2='001', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='32123456', xcn_2='IRIARTE', xcn_3='MARIANO', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='REU')
        pv1.patient_type = CWE(cwe_1='V00021500')
        pv1.prior_temporary_location = PL(pl_1='20250405')

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
        orc.placer_order_number = EI(ei_1='LAB-2025-01500')
        orc.placer_order_group_number = EI(ei_1='LAB-2025-01500-R')
        orc.parent_order = EIP(eip_1='20250405170000')
        orc.date_time_of_order_event = '32123456^IRIARTE^MARIANO^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB-2025-01500')
        obr.filler_order_number = EI(ei_1='LAB-2025-01500-R')
        obr.universal_service_identifier = CWE(cwe_1='57021-8', cwe_2='ANA PANEL', cwe_3='LN')
        obr.observation_date_time = '20250405100000'
        obr.obr_14 = '32123456^IRIARTE^MARIANO^^^DR'
        obr.placer_field_2 = 'INM'
        obr.result_status = 'F'
        obr.obr_32 = '32123456^IRIARTE^MARIANO^^^DR'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='8061-4', cwe_2='ANA PATTERN', cwe_3='LN')
        obx.obx_5 = 'Positivo 1:640 patron homogeneo'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='35879-8', cwe_2='ANTI-dsDNA', cwe_3='LN')
        obx_2.obx_5 = '185'
        obx_2.units = CWE(cwe_1='IU/mL')
        obx_2.reference_range = '<30'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='14079-9', cwe_2='ANTI-SM', cwe_3='LN')
        obx_3.obx_5 = 'Positivo'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4498-2', cwe_2='COMPLEMENT C3', cwe_3='LN')
        obx_4.obx_5 = '62'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '90-180'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='4499-0', cwe_2='COMPLEMENT C4', cwe_3='LN')
        obx_5.obx_5 = '8'
        obx_5.units = CWE(cwe_1='mg/dL')
        obx_5.reference_range = '10-40'
        obx_5.interpretation_codes = CWE(cwe_1='L')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='33762-6', cwe_2='ANTI-RNP', cwe_3='LN')
        obx_6.obx_5 = '95'
        obx_6.units = CWE(cwe_1='U/mL')
        obx_6.reference_range = '<20'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ED'
        obx_7.observation_identifier = CWE(cwe_1='IMG', cwe_2='Patron IFI ANA Homogeneo', cwe_3='LOCAL')
        obx_7.observation_sub_id = OG(og_1='1')
        obx_7.obx_5 = (
            'LIS_UNLP^IMAGE^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgy'
            'IRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCABAAEADASIAAhEBAxEB'
        )
        obx_7.observation_result_status = 'F'

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
