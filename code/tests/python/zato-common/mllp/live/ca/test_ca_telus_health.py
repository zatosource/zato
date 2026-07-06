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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, EIP, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OruR01Observation, OruR01OrderObservation, OruR01Patient, \
    OruR01PatientResult
from zato.hl7v2.v2_9.messages import ADT_A01, ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import EVN, IN1, MSH, OBR, OBX, ORC, PID, PV1

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ca', 'ca-telus-health.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ca/ca-telus-health.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TELUS_PSSUITE')
        msh.sending_facility = HD(hd_1='MAPLE LEAF FAMILY CLINIC')
        msh.receiving_application = HD(hd_1='HIS_RCV')
        msh.receiving_facility = HD(hd_1='TORONTO GENERAL')
        msh.date_time_of_message = '20260501080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'TH00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260501080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1234567890', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Bouchard', xpn_2='Marie', xpn_3='Claire', xpn_5='Mme')
        pid.date_time_of_birth = '19750612'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='88 Bloor St W', xad_3='Toronto', xad_4='ON', xad_5='M5S 1M4', xad_6='CA')
        pid.pid_13 = '^^PH^4165551234~^^CP^4165559876'
        pid.primary_language = CWE(cwe_1='F')
        pid.marital_status = CWE(cwe_1='CAT')
        pid.pid_36 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='402', pl_3='A', pl_4='Toronto General')
        pv1.attending_doctor = XCN(xcn_1='54321', xcn_2='Patel', xcn_3='Anita', xcn_6='Dr.', xcn_8='CPSO')
        pv1.referring_doctor = XCN(xcn_1='67890', xcn_2='Liu', xcn_3='Wei', xcn_6='Dr.', xcn_8='CPSO')
        pv1.temporary_location = PL(pl_1='MED')
        pv1.visit_number = CX(cx_1='VN20260501001')
        pv1.current_patient_balance = '20260501080000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.insurance_company_id = CX(cx_1='OHIP')
        in1.insurance_company_name = XON(xon_1='Ontario Health Insurance Plan')
        in1.insurance_company_address = XAD(xad_1="49 Place d'Armes", xad_3='Kingston', xad_4='ON', xad_5='K7L 5J2', xad_6='CA')
        in1.verification_status = '1234567890'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.insurance = insurance

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
    """ Based on live/ca/ca-telus-health.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WOLF_EMR')
        msh.sending_facility = HD(hd_1='QUEEN ST WALK-IN')
        msh.receiving_application = HD(hd_1='HIS_RCV')
        msh.receiving_facility = HD(hd_1='VANCOUVER GENERAL')
        msh.date_time_of_message = '20260502093000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'TH00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260502093000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='9876543210', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Chan', xpn_2='David', xpn_3='Wei', xpn_5='Mr')
        pid.date_time_of_birth = '19880304'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='250 Robson St', xad_3='Vancouver', xad_4='BC', xad_5='V6B 1A6', xad_6='CA')
        pid.pid_13 = '^^PH^6045551234~^^CP^6045559876'
        pid.primary_language = CWE(cwe_1='M')
        pid.pid_35 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='WALKIN', pl_2='RM1', pl_3='1', pl_4='Queen St Walk-In')
        pv1.attending_doctor = XCN(xcn_1='78901', xcn_2='Singh', xcn_3='Gurpreet', xcn_6='Dr.', xcn_8='CPSBC')
        pv1.hospital_service = CWE(cwe_1='GEN')
        pv1.patient_type = CWE(cwe_1='VN20260502001')
        pv1.discharge_date_time = '20260502093000'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/ca/ca-telus-health.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TELUS_PSSUITE')
        msh.sending_facility = HD(hd_1='RIDEAU FAMILY MEDICINE')
        msh.receiving_application = HD(hd_1='HIS_RCV')
        msh.receiving_facility = HD(hd_1='OTTAWA CIVIC')
        msh.date_time_of_message = '20260503140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'TH00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260503140000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3456789012', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lavoie', xpn_2='Jean-Pierre', xpn_5='Mr')
        pid.date_time_of_birth = '19700918'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='55 Sparks St', xad_3='Ottawa', xad_4='ON', xad_5='K1P 5A5', xad_6='CA')
        pid.pid_13 = '^^PH^6135553456~^^CP^6135558765~^^Internet^jp.lavoie@mail.ca'
        pid.primary_language = CWE(cwe_1='M')
        pid.marital_status = CWE(cwe_1='CAT')
        pid.pid_36 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_2='RM4', pl_3='1', pl_4='Rideau Family Medicine')
        pv1.attending_doctor = XCN(xcn_1='12345', xcn_2='Morin', xcn_3='Catherine', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='FAM')
        pv1.patient_type = CWE(cwe_1='VN20260503001')
        pv1.discharge_date_time = '20260503140000'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/ca/ca-telus-health.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TELUS_PSSUITE')
        msh.sending_facility = HD(hd_1='PRAIRIE HEALTH CLINIC')
        msh.receiving_application = HD(hd_1='LIFELABS')
        msh.receiving_facility = HD(hd_1='LIFELABS_AB')
        msh.date_time_of_message = '20260504101500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'TH00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='4567890123', cx_4='AB_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Olsen', xpn_2='Karen', xpn_3='Marie', xpn_5='Ms')
        pid.date_time_of_birth = '19820207'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='320 4th Ave SW', xad_3='Calgary', xad_4='AB', xad_5='T2P 0H5', xad_6='CA')
        pid.pid_13 = '^^PH^4035554567~^^CP^4035558901'
        pid.primary_language = CWE(cwe_1='F')
        pid.pid_35 = ''

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD20260504001', ei_2='TELUS_PSSUITE')
        orc.parent_order = EIP(eip_1='20260504101500')
        orc.orc_11 = '23456^Hansen^Erik^^^Dr.^^CPSA'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260504001', ei_2='TELUS_PSSUITE')
        obr.universal_service_identifier = CWE(cwe_1='BMP', cwe_2='Basic Metabolic Panel', cwe_3='LN')
        obr.observation_date_time = '20260504101500'
        obr.specimen_action_code = 'N'
        obr.obr_16 = '23456^Hansen^Erik^^^Dr.^^CPSA'

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
    """ Based on live/ca/ca-telus-health.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TELUS_PSSUITE')
        msh.sending_facility = HD(hd_1='COASTAL MEDICAL')
        msh.receiving_application = HD(hd_1='LIFELABS')
        msh.receiving_facility = HD(hd_1='LIFELABS_BC')
        msh.date_time_of_message = '20260505113000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TH00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='5678901234', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Nakamura', xpn_2='Yuki', xpn_5='Ms')
        pid.date_time_of_birth = '19930815'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='1420 West 12th Ave', xad_3='Vancouver', xad_4='BC', xad_5='V6H 1M8', xad_6='CA')
        pid.pid_13 = '^^PH^6045555678'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260505001', ei_2='TELUS_PSSUITE')
        obr.filler_order_number = EI(ei_1='SPE20260505001', ei_2='LIFELABS_BC')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Complete Blood Count', cwe_3='LN')
        obr.observation_date_time = '20260505080000'
        obr.obr_16 = '5678901234^Nakamura^Yuki^^^^'
        obr.results_rpt_status_chng_date_time = '20260505113000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='WBC', cwe_3='LN')
        obx.obx_5 = '6.8'
        obx.units = CWE(cwe_1='x10*9/L')
        obx.reference_range = '4.0-11.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='RBC', cwe_3='LN')
        obx_2.obx_5 = '4.25'
        obx_2.units = CWE(cwe_1='x10*12/L')
        obx_2.reference_range = '3.80-5.80'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin', cwe_3='LN')
        obx_3.obx_5 = '128'
        obx_3.units = CWE(cwe_1='g/L')
        obx_3.reference_range = '120-160'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocrit', cwe_3='LN')
        obx_4.obx_5 = '0.38'
        obx_4.units = CWE(cwe_1='L/L')
        obx_4.reference_range = '0.36-0.46'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='Platelets', cwe_3='LN')
        obx_5.obx_5 = '198'
        obx_5.units = CWE(cwe_1='x10*9/L')
        obx_5.reference_range = '150-400'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ca/ca-telus-health.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WOLF_EMR')
        msh.sending_facility = HD(hd_1='FOOTHILLS MEDICAL')
        msh.receiving_application = HD(hd_1='DLM')
        msh.receiving_facility = HD(hd_1='DLM_AB')
        msh.date_time_of_message = '20260506140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TH00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='6789012345', cx_4='AB_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='MacDougall', xpn_2='Ian', xpn_3='Robert', xpn_5='Mr')
        pid.date_time_of_birth = '19580330'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='78 Centre St N', xad_3='Calgary', xad_4='AB', xad_5='T2E 2P8', xad_6='CA')
        pid.pid_13 = '^^PH^4035556789'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260506001', ei_2='WOLF_EMR')
        obr.filler_order_number = EI(ei_1='SPE20260506001', ei_2='DLM_AB')
        obr.universal_service_identifier = CWE(cwe_1='CHEM', cwe_2='Chemistry Panel', cwe_3='LN')
        obr.observation_date_time = '20260506074500'
        obr.obr_16 = '6789012345^MacDougall^Ian R^^^^'
        obr.results_rpt_status_chng_date_time = '20260506140000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose', cwe_3='LN')
        obx.obx_5 = '5.1'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.3-5.5'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine', cwe_3='LN')
        obx_2.obx_5 = '98'
        obx_2.units = CWE(cwe_1='umol/L')
        obx_2.reference_range = '62-115'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea', cwe_3='LN')
        obx_3.obx_5 = '6.8'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '2.1-8.5'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodium', cwe_3='LN')
        obx_4.obx_5 = '141'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '136-145'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium', cwe_3='LN')
        obx_5.obx_5 = '4.2'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '3.5-5.1'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ca/ca-telus-health.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TELUS_PSSUITE')
        msh.sending_facility = HD(hd_1="WOMEN'S HEALTH CLINIC")
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ONTARIO_HIS')
        msh.date_time_of_message = '20260507090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'TH00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7890123456', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Giroux', xpn_2='Amelie', xpn_3='Rose', xpn_5='Mme')
        pid.date_time_of_birth = '19950614'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='33 Laurier Ave', xad_3='Ottawa', xad_4='ON', xad_5='K1N 6N5', xad_6='CA')
        pid.pid_13 = '^^PH^6135557890~^^CP^6135551234'
        pid.primary_language = CWE(cwe_1='F')
        pid.pid_35 = ''

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD20260507001', ei_2='TELUS_PSSUITE')
        orc.parent_order = EIP(eip_1='20260507090000')
        orc.orc_11 = '34567^Cote^Brigitte^^^Dr.^^CPSO'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260507001', ei_2='TELUS_PSSUITE')
        obr.universal_service_identifier = CWE(cwe_1='PNS', cwe_2='Prenatal Screening', cwe_3='LN')
        obr.observation_date_time = '20260507090000'
        obr.specimen_action_code = 'N'
        obr.obr_16 = '34567^Cote^Brigitte^^^Dr.^^CPSO'

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
    """ Based on live/ca/ca-telus-health.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TELUS_PSSUITE')
        msh.sending_facility = HD(hd_1='DOWNTOWN MEDICAL')
        msh.receiving_application = HD(hd_1='GAMMA_DYNACARE')
        msh.receiving_facility = HD(hd_1='DYNACARE_ON')
        msh.date_time_of_message = '20260508103000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TH00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='8901234567', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Tremblay', xpn_2='Louis', xpn_3='Andre', xpn_5='Mr')
        pid.date_time_of_birth = '19630425'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='100 King St W', xad_3='Hamilton', xad_4='ON', xad_5='L8P 4S6', xad_6='CA')
        pid.pid_13 = '^^PH^9055558901'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260508001', ei_2='TELUS_PSSUITE')
        obr.filler_order_number = EI(ei_1='SPE20260508001', ei_2='DYNACARE_ON')
        obr.universal_service_identifier = CWE(cwe_1='HBA1C', cwe_2='Hemoglobin A1c', cwe_3='LN')
        obr.observation_date_time = '20260508080000'
        obr.obr_16 = '8901234567^Tremblay^Louis A^^^^'
        obr.results_rpt_status_chng_date_time = '20260508103000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='Hemoglobin A1c', cwe_3='LN')
        obx.obx_5 = '0.068'
        obx.units = CWE(cwe_1='fraction')
        obx.reference_range = '<=0.070'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose Fasting', cwe_3='LN')
        obx_2.obx_5 = '6.2'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '3.3-5.5'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ED'
        obx_3.observation_identifier = CWE(cwe_1='PDF', cwe_2='Lab Summary Report', cwe_3='LN')
        obx_3.obx_5 = (
            '^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2Jq'
        )
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ca/ca-telus-health.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WOLF_EMR')
        msh.sending_facility = HD(hd_1='PORTAGE FAMILY HEALTH')
        msh.receiving_application = HD(hd_1='HIS_RCV')
        msh.receiving_facility = HD(hd_1='ST BONIFACE GENERAL')
        msh.date_time_of_message = '20260509071500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'TH00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260509071500'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='9012345678', cx_4='MB_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Flett', xpn_2='Thomas', xpn_3='James', xpn_5='Mr')
        pid.date_time_of_birth = '19550728'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='45 Main St', xad_3='Winnipeg', xad_4='MB', xad_5='R3C 1A3', xad_6='CA')
        pid.pid_13 = '^^PH^2045559012~^^CP^2045558765'
        pid.primary_language = CWE(cwe_1='M')
        pid.pid_35 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='201', pl_3='A', pl_4='St Boniface General')
        pv1.attending_doctor = XCN(xcn_1='45678', xcn_2='Fehr', xcn_3='Marcus', xcn_6='Dr.', xcn_8='CPSM')
        pv1.hospital_service = CWE(cwe_1='CARD')
        pv1.patient_type = CWE(cwe_1='VN20260509001')
        pv1.discharge_date_time = '20260509071500'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.insurance_company_id = CX(cx_1='MB_HEALTH')
        in1.insurance_company_name = XON(xon_1='Manitoba Health, Seniors and Long-Term Care')
        in1.insurance_company_address = XAD(xad_1='300 Carlton St', xad_3='Winnipeg', xad_4='MB', xad_5='R3B 3M9', xad_6='CA')
        in1.verification_status = '9012345678'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
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
    """ Based on live/ca/ca-telus-health.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TELUS_PSSUITE')
        msh.sending_facility = HD(hd_1='LAKE SHORE CLINIC')
        msh.receiving_application = HD(hd_1='LIFELABS')
        msh.receiving_facility = HD(hd_1='LIFELABS_ON')
        msh.date_time_of_message = '20260510091500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TH00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0123456789', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Beauchemin', xpn_2='Danielle', xpn_3='Helene', xpn_5='Mme')
        pid.date_time_of_birth = '19780213'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='160 Lakeshore Rd', xad_3='Burlington', xad_4='ON', xad_5='L7S 1E1', xad_6='CA')
        pid.pid_13 = '^^PH^9055550123'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260510001', ei_2='TELUS_PSSUITE')
        obr.filler_order_number = EI(ei_1='SPE20260510001', ei_2='LIFELABS_ON')
        obr.universal_service_identifier = CWE(cwe_1='LIPID', cwe_2='Lipid Panel', cwe_3='LN')
        obr.observation_date_time = '20260510074500'
        obr.obr_16 = '0123456789^Beauchemin^Danielle H^^^^'
        obr.results_rpt_status_chng_date_time = '20260510091500'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2093-3', cwe_2='Total Cholesterol', cwe_3='LN')
        obx.obx_5 = '5.0'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '<5.2'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2571-8', cwe_2='Triglycerides', cwe_3='LN')
        obx_2.obx_5 = '1.3'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '<1.7'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2085-9', cwe_2='HDL Cholesterol', cwe_3='LN')
        obx_3.obx_5 = '1.55'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '>1.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='13457-7', cwe_2='LDL Cholesterol', cwe_3='LN')
        obx_4.obx_5 = '2.86'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '<3.4'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ca/ca-telus-health.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TELUS_PSSUITE')
        msh.sending_facility = HD(hd_1='MAIN ST MEDICAL')
        msh.receiving_application = HD(hd_1='RIS_RCV')
        msh.receiving_facility = HD(hd_1='KINGSTON GENERAL RAD')
        msh.date_time_of_message = '20260511100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'TH00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1122334455', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Gervais', xpn_2='Simon', xpn_3='Paul', xpn_5='Mr')
        pid.date_time_of_birth = '19690401'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='22 Princess St', xad_3='Kingston', xad_4='ON', xad_5='K7L 1A4', xad_6='CA')
        pid.pid_13 = '^^PH^6135551122'

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD20260511001', ei_2='TELUS_PSSUITE')
        orc.parent_order = EIP(eip_1='20260511100000')
        orc.orc_11 = '56789^Roy^Genevieve^^^Dr.^^CPSO'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260511001', ei_2='TELUS_PSSUITE')
        obr.universal_service_identifier = CWE(cwe_1='XCHEST', cwe_2='Chest Xray PA and Lateral', cwe_3='LN')
        obr.observation_date_time = '20260511100000'
        obr.specimen_action_code = 'N'
        obr.obr_16 = '56789^Roy^Genevieve^^^Dr.^^CPSO'
        obr.obr_27 = '^Persistent cough x 3 weeks'

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
    """ Based on live/ca/ca-telus-health.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WOLF_EMR')
        msh.sending_facility = HD(hd_1='PRAIRIE HEALTH CENTRE')
        msh.receiving_application = HD(hd_1='PROV_LAB')
        msh.receiving_facility = HD(hd_1='SK_PROV_LAB')
        msh.date_time_of_message = '20260512133000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TH00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2233445566', cx_4='SK_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Fehr', xpn_2='Margaret', xpn_3='Ann', xpn_5='Ms')
        pid.date_time_of_birth = '19850520'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='410 Spadina Cres', xad_3='Saskatoon', xad_4='SK', xad_5='S7K 3G9', xad_6='CA')
        pid.pid_13 = '^^PH^3065552233'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260512001', ei_2='WOLF_EMR')
        obr.filler_order_number = EI(ei_1='SPE20260512001', ei_2='SK_PROV_LAB')
        obr.universal_service_identifier = CWE(cwe_1='THYR', cwe_2='Thyroid Panel', cwe_3='LN')
        obr.observation_date_time = '20260512080000'
        obr.obr_16 = '2233445566^Fehr^Margaret A^^^^'
        obr.results_rpt_status_chng_date_time = '20260512133000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='TSH', cwe_3='LN')
        obx.obx_5 = '2.15'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.35-5.50'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3026-2', cwe_2='Free T4', cwe_3='LN')
        obx_2.obx_5 = '16.8'
        obx_2.units = CWE(cwe_1='pmol/L')
        obx_2.reference_range = '10.0-25.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ca/ca-telus-health.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TELUS_PSSUITE')
        msh.sending_facility = HD(hd_1='BAYVIEW CLINIC')
        msh.receiving_application = HD(hd_1='HIS_RCV')
        msh.receiving_facility = HD(hd_1='SUNNYBROOK HSC')
        msh.date_time_of_message = '20260513150000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'TH00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260513150000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3344556677', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Kim', xpn_2='Soo-Yeon', xpn_5='Ms')
        pid.date_time_of_birth = '19910814'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='200 Bayview Ave', xad_3='Toronto', xad_4='ON', xad_5='M4G 3E8', xad_6='CA')
        pid.pid_13 = '^^PH^4165553344~^^CP^4165557890~^^Internet^sooyeon.kim@mail.ca'
        pid.primary_language = CWE(cwe_1='F')
        pid.pid_35 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_2='RM2', pl_3='1', pl_4='Bayview Clinic')
        pv1.attending_doctor = XCN(xcn_1='67890', xcn_2='Lee', xcn_3='Michael', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='FAM')
        pv1.patient_type = CWE(cwe_1='VN20260513001')
        pv1.discharge_date_time = '20260513150000'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/ca/ca-telus-health.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TELUS_PSSUITE')
        msh.sending_facility = HD(hd_1='RIVERSIDE MEDICAL')
        msh.receiving_application = HD(hd_1='RAD_RCV')
        msh.receiving_facility = HD(hd_1='CIVIC RAD DEPT')
        msh.date_time_of_message = '20260514141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TH00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='4455667788', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Pelletier', xpn_2='Jacques', xpn_3='Michel', xpn_5='Mr')
        pid.date_time_of_birth = '19720508'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='340 Richmond Rd', xad_3='Ottawa', xad_4='ON', xad_5='K2A 0E5', xad_6='CA')
        pid.pid_13 = '^^PH^6135554455'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260514001', ei_2='TELUS_PSSUITE')
        obr.filler_order_number = EI(ei_1='RAD20260514001', ei_2='CIVIC_RAD')
        obr.universal_service_identifier = CWE(cwe_1='XHAND', cwe_2='Hand Xray', cwe_3='LN')
        obr.observation_date_time = '20260514110000'
        obr.obr_16 = '4455667788^Pelletier^Jacques M^^^^'
        obr.results_rpt_status_chng_date_time = '20260514141500'
        obr.diagnostic_serv_sect_id = 'RAD'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic Imaging Report', cwe_3='LN')
        obx.obx_5 = (
            'AP and oblique views of the right hand. Comminuted fracture of the 5th metacarpal neck. No other fractures. Soft tissue swelling over the ul'
            'nar aspect.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='Hand Xray Image', cwe_3='LN')
        obx_2.obx_5 = (
            '^IM^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgy'
            'IRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL'
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ca/ca-telus-health.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TELUS_PSSUITE')
        msh.sending_facility = HD(hd_1='CENTRETOWN CHC')
        msh.receiving_application = HD(hd_1='LIFELABS')
        msh.receiving_facility = HD(hd_1='LIFELABS_ON')
        msh.date_time_of_message = '20260515160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TH00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='5566778899', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Duval', xpn_2='Monique', xpn_3='Rose', xpn_5='Mme')
        pid.date_time_of_birth = '19450917'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='180 Metcalfe St', xad_3='Ottawa', xad_4='ON', xad_5='K2P 1P5', xad_6='CA')
        pid.pid_13 = '^^PH^6135555566'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260515001', ei_2='TELUS_PSSUITE')
        obr.filler_order_number = EI(ei_1='SPE20260515001', ei_2='LIFELABS_ON')
        obr.universal_service_identifier = CWE(cwe_1='UCUL', cwe_2='Urine Culture', cwe_3='LN')
        obr.observation_date_time = '20260515083000'
        obr.obr_16 = '5566778899^Duval^Monique R^^^^'
        obr.results_rpt_status_chng_date_time = '20260515160000'
        obr.diagnostic_serv_sect_id = 'MB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='630-4', cwe_2='Bacteria identified', cwe_3='LN')
        obx.obx_5 = 'Klebsiella pneumoniae'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18900-1', cwe_2='Colony count', cwe_3='LN')
        obx_2.obx_5 = '>100,000 CFU/mL'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18864-9', cwe_2='Ampicillin', cwe_3='LN')
        obx_3.obx_5 = 'Resistant'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18865-6', cwe_2='Ciprofloxacin', cwe_3='LN')
        obx_4.obx_5 = 'Susceptible'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18906-8', cwe_2='Ceftriaxone', cwe_3='LN')
        obx_5.obx_5 = 'Susceptible'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ca/ca-telus-health.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WOLF_EMR')
        msh.sending_facility = HD(hd_1='HALIFAX FAMILY PRACTICE')
        msh.receiving_application = HD(hd_1='HIS_RCV')
        msh.receiving_facility = HD(hd_1='QEII HSC')
        msh.date_time_of_message = '20260516090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'TH00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260516090000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='6677889900', cx_4='NS_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='MacLeod', xpn_2='Fiona', xpn_3='Elizabeth', xpn_5='Ms')
        pid.date_time_of_birth = '19830322'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='55 Spring Garden Rd', xad_3='Halifax', xad_4='NS', xad_5='B3J 1G1', xad_6='CA')
        pid.pid_13 = '^^PH^9025556677~^^CP^9025558899'
        pid.primary_language = CWE(cwe_1='F')
        pid.pid_35 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_2='RM1', pl_3='1', pl_4='Halifax Family Practice')
        pv1.attending_doctor = XCN(xcn_1='78901', xcn_2='MacDonald', xcn_3='Angus', xcn_6='Dr.', xcn_8='CPSNS')
        pv1.hospital_service = CWE(cwe_1='FAM')
        pv1.patient_type = CWE(cwe_1='VN20260516001')
        pv1.discharge_date_time = '20260516090000'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/ca/ca-telus-health.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TELUS_PSSUITE')
        msh.sending_facility = HD(hd_1='HEART HEALTH CLINIC')
        msh.receiving_application = HD(hd_1='LIFELABS')
        msh.receiving_facility = HD(hd_1='LIFELABS_ON')
        msh.date_time_of_message = '20260517111500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TH00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7788990011', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Arsenault', xpn_2='Roger', xpn_3='Paul', xpn_5='Mr')
        pid.date_time_of_birth = '19500811'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='72 Elgin St', xad_3='Ottawa', xad_4='ON', xad_5='K1P 5K6', xad_6='CA')
        pid.pid_13 = '^^PH^6135557788'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260517001', ei_2='TELUS_PSSUITE')
        obr.filler_order_number = EI(ei_1='SPE20260517001', ei_2='LIFELABS_ON')
        obr.universal_service_identifier = CWE(cwe_1='COAG', cwe_2='Coagulation Panel', cwe_3='LN')
        obr.observation_date_time = '20260517074500'
        obr.obr_16 = '7788990011^Arsenault^Roger P^^^^'
        obr.results_rpt_status_chng_date_time = '20260517111500'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='PT', cwe_3='LN')
        obx.obx_5 = '15.2'
        obx.units = CWE(cwe_1='s')
        obx.reference_range = '11.0-13.5'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx_2.obx_5 = '2.3'
        obx_2.reference_range = '2.0-3.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3173-2', cwe_2='aPTT', cwe_3='LN')
        obx_3.obx_5 = '32'
        obx_3.units = CWE(cwe_1='s')
        obx_3.reference_range = '25-38'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ca/ca-telus-health.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TELUS_PSSUITE')
        msh.sending_facility = HD(hd_1='NEPEAN MEDICAL')
        msh.receiving_application = HD(hd_1='REPO')
        msh.receiving_facility = HD(hd_1='DOC_REPO')
        msh.date_time_of_message = '20260518150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TH00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='8899001122', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Desrosiers', xpn_2='Helene', xpn_3='Marie', xpn_5='Mme')
        pid.date_time_of_birth = '19680910'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='400 Hunt Club Rd', xad_3='Ottawa', xad_4='ON', xad_5='K1V 1C1', xad_6='CA')
        pid.pid_13 = '^^PH^6135558899'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260518001', ei_2='TELUS_PSSUITE')
        obr.filler_order_number = EI(ei_1='DOC20260518001', ei_2='DOC_REPO')
        obr.universal_service_identifier = CWE(cwe_1='SPEC', cwe_2='Specialist Letter', cwe_3='LN')
        obr.observation_date_time = '20260518120000'
        obr.obr_16 = '8899001122^Desrosiers^Helene M^^^^'
        obr.results_rpt_status_chng_date_time = '20260518150000'
        obr.diagnostic_serv_sect_id = 'DOC'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='11488-4', cwe_2='Consultation Note', cwe_3='LN')
        obx.obx_5 = 'Rheumatology assessment for polyarthralgia. Exam findings consistent with early rheumatoid arthritis. Starting methotrexate 15mg weekly.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Specialist Report PDF', cwe_3='LN')
        obx_2.obx_5 = (
            '^AP^^Base64^'
            'JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKL01hcmtJbmZvIDw8IC9NYXJrZWQgdHJ1ZSA+PgovU3RydWN0VHJlZVJvb3QgMyAwIFIK'
            'Pj4KZW5kb2Jq'
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ca/ca-telus-health.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WOLF_EMR')
        msh.sending_facility = HD(hd_1='MONCTON MEDICAL')
        msh.receiving_application = HD(hd_1='HIS_RCV')
        msh.receiving_facility = HD(hd_1='DR EVERETT CHALMERS')
        msh.date_time_of_message = '20260519063000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'TH00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260519063000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='9900112233', cx_4='NB_MCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='LeBlanc', xpn_2='Andre', xpn_3='Joseph', xpn_5='Mr')
        pid.date_time_of_birth = '19680115'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='120 Main St', xad_3='Moncton', xad_4='NB', xad_5='E1C 1B8', xad_6='CA')
        pid.pid_13 = '^^PH^5065559900~^^CP^5065558811'
        pid.primary_language = CWE(cwe_1='M')
        pid.pid_35 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SURG', pl_2='301', pl_3='A', pl_4='Dr Everett Chalmers')
        pv1.attending_doctor = XCN(xcn_1='89012', xcn_2='Landry', xcn_3='Lise', xcn_6='Dr.', xcn_8='CPSNB')
        pv1.hospital_service = CWE(cwe_1='SURG')
        pv1.patient_type = CWE(cwe_1='VN20260519001')
        pv1.discharge_date_time = '20260519063000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.insurance_company_id = CX(cx_1='NB_MEDICARE')
        in1.insurance_company_name = XON(xon_1='New Brunswick Medicare')
        in1.insurance_company_address = XAD(xad_1='520 King St', xad_3='Fredericton', xad_4='NB', xad_5='E3B 6G3', xad_6='CA')
        in1.verification_status = '9900112233'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.insurance = insurance

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
    """ Based on live/ca/ca-telus-health.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TELUS_PSSUITE')
        msh.sending_facility = HD(hd_1='URGENCE CLINIC')
        msh.receiving_application = HD(hd_1='LIFELABS')
        msh.receiving_facility = HD(hd_1='LIFELABS_ON')
        msh.date_time_of_message = '20260520161500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'TH00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0011223344', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Nadeau', xpn_2='Claude', xpn_3='Pierre', xpn_5='Mr')
        pid.date_time_of_birth = '19470603'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='85 Somerset St', xad_3='Ottawa', xad_4='ON', xad_5='K1R 6R1', xad_6='CA')
        pid.pid_13 = '^^PH^6135550011'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260520001', ei_2='TELUS_PSSUITE')
        obr.filler_order_number = EI(ei_1='SPE20260520001', ei_2='LIFELABS_ON')
        obr.universal_service_identifier = CWE(cwe_1='ELEC', cwe_2='Electrolyte Panel', cwe_3='LN')
        obr.observation_date_time = '20260520081000'
        obr.obr_16 = '0011223344^Nadeau^Claude P^^^^'
        obr.results_rpt_status_chng_date_time = '20260520161500'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodium', cwe_3='LN')
        obx.obx_5 = '139'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '136-145'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium', cwe_3='LN')
        obx_2.obx_5 = '6.1'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '3.5-5.1'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2075-0', cwe_2='Chloride', cwe_3='LN')
        obx_3.obx_5 = '101'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '98-106'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1963-8', cwe_2='Bicarbonate', cwe_3='LN')
        obx_4.obx_5 = '23'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '22-29'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='17861-6', cwe_2='Calcium', cwe_3='LN')
        obx_5.obx_5 = '2.35'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '2.15-2.55'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
