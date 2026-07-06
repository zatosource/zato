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
from zato.hl7v2.v2_9.groups import OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01Observation, OruR01OrderObservation, \
    OruR01Patient, OruR01PatientResult
from zato.hl7v2.v2_9.messages import ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import MSH, OBR, OBX, ORC, PID, PV1

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ca', 'ca-sunquest.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ca/ca-sunquest.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_ED')
        msh.sending_facility = HD(hd_1='OTTAWA_CIVIC')
        msh.receiving_application = HD(hd_1='SUNQUEST_LIS')
        msh.receiving_facility = HD(hd_1='TOH_LAB')
        msh.date_time_of_message = '20260401041500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SQ00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1234567890', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Bernier', xpn_2='Marc', xpn_3='Andre', xpn_5='Mr')
        pid.date_time_of_birth = '19680412'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='22 Carling Ave', xad_3='Ottawa', xad_4='ON', xad_5='K1S 2E1', xad_6='CA')
        pid.pid_13 = '^^PH^6135551234'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='EMERG', pl_2='BAY3', pl_3='1', pl_4='Ottawa Civic')
        pv1.attending_doctor = XCN(xcn_1='12345', xcn_2='Lapointe', xcn_3='Julie', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='EMER')
        pv1.patient_type = CWE(cwe_1='VN20260401001')
        pv1.discharge_date_time = '20260401041500'

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
        orc.placer_order_number = EI(ei_1='ORD20260401001', ei_2='HIS_ED')
        orc.orc_7 = '^^^^^R'
        orc.date_time_of_order_event = '20260401041500'
        orc.orc_12 = '12345^Lapointe^Julie^^^Dr.^^CPSO'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260401001', ei_2='HIS_ED')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Complete Blood Count', cwe_3='LN')
        obr.observation_date_time = '20260401041500'
        obr.specimen_action_code = 'S'
        obr.obr_16 = '12345^Lapointe^Julie^^^Dr.^^CPSO'

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
    """ Based on live/ca/ca-sunquest.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_ICU')
        msh.sending_facility = HD(hd_1='KINGSTON_GEN')
        msh.receiving_application = HD(hd_1='SUNQUEST_LIS')
        msh.receiving_facility = HD(hd_1='KGH_LAB')
        msh.date_time_of_message = '20260402060000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SQ00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2345678901', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Michaud', xpn_2='Sylvie', xpn_3='Helene', xpn_5='Mme')
        pid.date_time_of_birth = '19750830'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='88 Princess St', xad_3='Kingston', xad_4='ON', xad_5='K7L 1A5', xad_6='CA')
        pid.pid_13 = '^^PH^6135552345'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='101', pl_3='A', pl_4='Kingston General')
        pv1.attending_doctor = XCN(xcn_1='23456', xcn_2='Bhatt', xcn_3='Rajesh', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='IMED')
        pv1.patient_type = CWE(cwe_1='VN20260402001')
        pv1.discharge_date_time = '20260402060000'

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
        orc.placer_order_number = EI(ei_1='ORD20260402001', ei_2='HIS_ICU')
        orc.orc_7 = '^^^^^S'
        orc.date_time_of_order_event = '20260402060000'
        orc.orc_12 = '23456^Bhatt^Rajesh^^^Dr.^^CPSO'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260402001', ei_2='HIS_ICU')
        obr.universal_service_identifier = CWE(cwe_1='BMP', cwe_2='Basic Metabolic Panel', cwe_3='LN')
        obr.observation_date_time = '20260402060000'
        obr.specimen_action_code = 'S'
        obr.obr_16 = '23456^Bhatt^Rajesh^^^Dr.^^CPSO'

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
    """ Based on live/ca/ca-sunquest.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SUNQUEST_LIS')
        msh.sending_facility = HD(hd_1='TOH_LAB')
        msh.receiving_application = HD(hd_1='HIS_ED')
        msh.receiving_facility = HD(hd_1='OTTAWA_CIVIC')
        msh.date_time_of_message = '20260401053000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SQ00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1234567890', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Bernier', xpn_2='Marc', xpn_3='Andre', xpn_5='Mr')
        pid.date_time_of_birth = '19680412'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='22 Carling Ave', xad_3='Ottawa', xad_4='ON', xad_5='K1S 2E1', xad_6='CA')
        pid.pid_13 = '^^PH^6135551234'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260401001', ei_2='HIS_ED')
        obr.filler_order_number = EI(ei_1='SPE20260401001', ei_2='TOH_LAB')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Complete Blood Count', cwe_3='LN')
        obr.observation_date_time = '20260401041500'
        obr.obr_16 = '1234567890^Bernier^Marc A^^^^'
        obr.results_rpt_status_chng_date_time = '20260401053000'
        obr.diagnostic_serv_sect_id = 'HEM'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='WBC', cwe_3='LN')
        obx.obx_5 = '14.5'
        obx.units = CWE(cwe_1='x10*9/L')
        obx.reference_range = '4.0-11.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='RBC', cwe_3='LN')
        obx_2.obx_5 = '4.82'
        obx_2.units = CWE(cwe_1='x10*12/L')
        obx_2.reference_range = '4.50-6.00'
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
        obx_3.obx_5 = '148'
        obx_3.units = CWE(cwe_1='g/L')
        obx_3.reference_range = '130-170'
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
        obx_4.obx_5 = '0.44'
        obx_4.units = CWE(cwe_1='L/L')
        obx_4.reference_range = '0.38-0.52'
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
        obx_5.obx_5 = '312'
        obx_5.units = CWE(cwe_1='x10*9/L')
        obx_5.reference_range = '150-400'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='770-8', cwe_2='Neutrophils', cwe_3='LN')
        obx_6.obx_5 = '82'
        obx_6.units = CWE(cwe_1='%')
        obx_6.reference_range = '40-70'
        obx_6.interpretation_codes = CWE(cwe_1='H')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='736-9', cwe_2='Lymphocytes', cwe_3='LN')
        obx_7.obx_5 = '12'
        obx_7.units = CWE(cwe_1='%')
        obx_7.reference_range = '20-45'
        obx_7.interpretation_codes = CWE(cwe_1='L')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='5905-5', cwe_2='Monocytes', cwe_3='LN')
        obx_8.obx_5 = '4'
        obx_8.units = CWE(cwe_1='%')
        obx_8.reference_range = '2-10'
        obx_8.interpretation_codes = CWE(cwe_1='N')
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'NM'
        obx_9.observation_identifier = CWE(cwe_1='713-8', cwe_2='Eosinophils', cwe_3='LN')
        obx_9.obx_5 = '1'
        obx_9.units = CWE(cwe_1='%')
        obx_9.reference_range = '1-6'
        obx_9.interpretation_codes = CWE(cwe_1='N')
        obx_9.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

        # .. build OBX ..
        obx_10 = OBX()
        obx_10.set_id_obx = '10'
        obx_10.value_type = 'NM'
        obx_10.observation_identifier = CWE(cwe_1='706-2', cwe_2='Basophils', cwe_3='LN')
        obx_10.obx_5 = '1'
        obx_10.units = CWE(cwe_1='%')
        obx_10.reference_range = '0-2'
        obx_10.interpretation_codes = CWE(cwe_1='N')
        obx_10.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_10 = OruR01Observation()
        observation_10.obx = obx_10

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ca/ca-sunquest.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SUNQUEST_LIS')
        msh.sending_facility = HD(hd_1='KGH_LAB')
        msh.receiving_application = HD(hd_1='HIS_ICU')
        msh.receiving_facility = HD(hd_1='KINGSTON_GEN')
        msh.date_time_of_message = '20260402070000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SQ00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2345678901', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Michaud', xpn_2='Sylvie', xpn_3='Helene', xpn_5='Mme')
        pid.date_time_of_birth = '19750830'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='88 Princess St', xad_3='Kingston', xad_4='ON', xad_5='K7L 1A5', xad_6='CA')
        pid.pid_13 = '^^PH^6135552345'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260402001', ei_2='HIS_ICU')
        obr.filler_order_number = EI(ei_1='SPE20260402001', ei_2='KGH_LAB')
        obr.universal_service_identifier = CWE(cwe_1='BMP', cwe_2='Basic Metabolic Panel', cwe_3='LN')
        obr.observation_date_time = '20260402060000'
        obr.obr_16 = '2345678901^Michaud^Sylvie H^^^^'
        obr.results_rpt_status_chng_date_time = '20260402070000'
        obr.diagnostic_serv_sect_id = 'CHEM'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose', cwe_3='LN')
        obx.obx_5 = '2.1'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.3-5.5'
        obx.interpretation_codes = CWE(cwe_1='LL')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine', cwe_3='LN')
        obx_2.obx_5 = '245'
        obx_2.units = CWE(cwe_1='umol/L')
        obx_2.reference_range = '50-98'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea', cwe_3='LN')
        obx_3.obx_5 = '28.5'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '2.1-8.5'
        obx_3.interpretation_codes = CWE(cwe_1='HH')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodium', cwe_3='LN')
        obx_4.obx_5 = '126'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '136-145'
        obx_4.interpretation_codes = CWE(cwe_1='LL')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium', cwe_3='LN')
        obx_5.obx_5 = '6.4'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '3.5-5.1'
        obx_5.interpretation_codes = CWE(cwe_1='HH')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2075-0', cwe_2='Chloride', cwe_3='LN')
        obx_6.obx_5 = '94'
        obx_6.units = CWE(cwe_1='mmol/L')
        obx_6.reference_range = '98-106'
        obx_6.interpretation_codes = CWE(cwe_1='L')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='1963-8', cwe_2='Bicarbonate', cwe_3='LN')
        obx_7.obx_5 = '16'
        obx_7.units = CWE(cwe_1='mmol/L')
        obx_7.reference_range = '22-29'
        obx_7.interpretation_codes = CWE(cwe_1='LL')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='2532-0', cwe_2='Lactate', cwe_3='LN')
        obx_8.obx_5 = '5.8'
        obx_8.units = CWE(cwe_1='mmol/L')
        obx_8.reference_range = '0.5-2.2'
        obx_8.interpretation_codes = CWE(cwe_1='HH')
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ca/ca-sunquest.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_MED')
        msh.sending_facility = HD(hd_1='HAMILTON_GEN')
        msh.receiving_application = HD(hd_1='SUNQUEST_LIS')
        msh.receiving_facility = HD(hd_1='HHS_LAB')
        msh.date_time_of_message = '20260403082000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SQ00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3456789012', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Caron', xpn_2='Francois', xpn_3='Joseph', xpn_5='Mr')
        pid.date_time_of_birth = '19800614'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='14 Main St E', xad_3='Hamilton', xad_4='ON', xad_5='L8N 1E8', xad_6='CA')
        pid.pid_13 = '^^PH^9055553456'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='504', pl_3='A', pl_4='Hamilton General')
        pv1.attending_doctor = XCN(xcn_1='34567', xcn_2='Okafor', xcn_3='Chidi', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='IMED')
        pv1.patient_type = CWE(cwe_1='VN20260403001')
        pv1.discharge_date_time = '20260403082000'

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
        orc.placer_order_number = EI(ei_1='ORD20260403001', ei_2='HIS_MED')
        orc.orc_7 = '^^^^^S'
        orc.date_time_of_order_event = '20260403082000'
        orc.orc_12 = '34567^Okafor^Chidi^^^Dr.^^CPSO'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260403001', ei_2='HIS_MED')
        obr.universal_service_identifier = CWE(cwe_1='BCULT', cwe_2='Blood Culture', cwe_3='LN')
        obr.observation_date_time = '20260403082000'
        obr.specimen_action_code = 'S'
        obr.obr_16 = '34567^Okafor^Chidi^^^Dr.^^CPSO'
        obr.obr_27 = '^Fever 39.2C, rigors, suspected bacteremia'

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
    """ Based on live/ca/ca-sunquest.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SUNQUEST_LIS')
        msh.sending_facility = HD(hd_1='HHS_LAB')
        msh.receiving_application = HD(hd_1='HIS_MED')
        msh.receiving_facility = HD(hd_1='HAMILTON_GEN')
        msh.date_time_of_message = '20260404150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SQ00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3456789012', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Caron', xpn_2='Francois', xpn_3='Joseph', xpn_5='Mr')
        pid.date_time_of_birth = '19800614'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='14 Main St E', xad_3='Hamilton', xad_4='ON', xad_5='L8N 1E8', xad_6='CA')
        pid.pid_13 = '^^PH^9055553456'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260403001', ei_2='HIS_MED')
        obr.filler_order_number = EI(ei_1='SPE20260403001', ei_2='HHS_LAB')
        obr.universal_service_identifier = CWE(cwe_1='BCULT', cwe_2='Blood Culture', cwe_3='LN')
        obr.observation_date_time = '20260403082000'
        obr.obr_16 = '3456789012^Caron^Francois J^^^^'
        obr.results_rpt_status_chng_date_time = '20260404150000'
        obr.diagnostic_serv_sect_id = 'MB'
        obr.result_status = 'P'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Bacteria identified', cwe_3='LN')
        obx.obx_5 = 'Gram positive cocci in clusters'
        obx.observation_result_status = 'P'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='11475-1', cwe_2='Culture status', cwe_3='LN')
        obx_2.obx_5 = 'Growth detected at 18 hours, aerobic bottle'
        obx_2.observation_result_status = 'P'

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
    """ Based on live/ca/ca-sunquest.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SUNQUEST_LIS')
        msh.sending_facility = HD(hd_1='HHS_LAB')
        msh.receiving_application = HD(hd_1='HIS_MED')
        msh.receiving_facility = HD(hd_1='HAMILTON_GEN')
        msh.date_time_of_message = '20260406091500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SQ00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3456789012', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Caron', xpn_2='Francois', xpn_3='Joseph', xpn_5='Mr')
        pid.date_time_of_birth = '19800614'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='14 Main St E', xad_3='Hamilton', xad_4='ON', xad_5='L8N 1E8', xad_6='CA')
        pid.pid_13 = '^^PH^9055553456'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260403001', ei_2='HIS_MED')
        obr.filler_order_number = EI(ei_1='SPE20260403001', ei_2='HHS_LAB')
        obr.universal_service_identifier = CWE(cwe_1='BCULT', cwe_2='Blood Culture', cwe_3='LN')
        obr.observation_date_time = '20260403082000'
        obr.obr_16 = '3456789012^Caron^Francois J^^^^'
        obr.results_rpt_status_chng_date_time = '20260406091500'
        obr.diagnostic_serv_sect_id = 'MB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Bacteria identified', cwe_3='LN')
        obx.obx_5 = 'Staphylococcus aureus (MSSA)'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18900-1', cwe_2='Colony count', cwe_3='LN')
        obx_2.obx_5 = '2/2 bottles positive'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18964-0', cwe_2='Oxacillin', cwe_3='LN')
        obx_3.obx_5 = 'Susceptible'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18878-2', cwe_2='Cefazolin', cwe_3='LN')
        obx_4.obx_5 = 'Susceptible'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18993-9', cwe_2='Vancomycin', cwe_3='LN')
        obx_5.obx_5 = 'Susceptible'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='18886-5', cwe_2='Clindamycin', cwe_3='LN')
        obx_6.obx_5 = 'Susceptible'
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='18919-4', cwe_2='Gentamicin', cwe_3='LN')
        obx_7.obx_5 = 'Susceptible'
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'ST'
        obx_8.observation_identifier = CWE(cwe_1='18996-2', cwe_2='Trimethoprim-Sulfamethoxazole', cwe_3='LN')
        obx_8.obx_5 = 'Susceptible'
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ca/ca-sunquest.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SURG')
        msh.sending_facility = HD(hd_1='SUNNYBROOK_HSC')
        msh.receiving_application = HD(hd_1='SUNQUEST_LIS')
        msh.receiving_facility = HD(hd_1='SBK_BLOODBANK')
        msh.date_time_of_message = '20260407054500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SQ00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='4567890123', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Nguyen', xpn_2='Thi', xpn_3='Lan', xpn_5='Ms')
        pid.date_time_of_birth = '19870423'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='320 Bloor St W', xad_3='Toronto', xad_4='ON', xad_5='M5S 1W5', xad_6='CA')
        pid.pid_13 = '^^PH^4165554567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SURG', pl_2='OR3', pl_3='1', pl_4='Sunnybrook HSC')
        pv1.attending_doctor = XCN(xcn_1='45678', xcn_2='Desjardins', xcn_3='Francois', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='SURG')
        pv1.patient_type = CWE(cwe_1='VN20260407001')
        pv1.discharge_date_time = '20260407054500'

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
        orc.placer_order_number = EI(ei_1='ORD20260407001', ei_2='HIS_SURG')
        orc.orc_7 = '^^^^^S'
        orc.date_time_of_order_event = '20260407054500'
        orc.orc_12 = '45678^Desjardins^Francois^^^Dr.^^CPSO'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260407001', ei_2='HIS_SURG')
        obr.universal_service_identifier = CWE(cwe_1='XMATCH', cwe_2='Crossmatch 2 Units pRBC', cwe_3='LN')
        obr.observation_date_time = '20260407054500'
        obr.specimen_action_code = 'S'
        obr.obr_16 = '45678^Desjardins^Francois^^^Dr.^^CPSO'
        obr.obr_27 = '^Pre-op hip arthroplasty, Hgb 98 g/L'

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
    """ Based on live/ca/ca-sunquest.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SUNQUEST_LIS')
        msh.sending_facility = HD(hd_1='SBK_BLOODBANK')
        msh.receiving_application = HD(hd_1='HIS_SURG')
        msh.receiving_facility = HD(hd_1='SUNNYBROOK_HSC')
        msh.date_time_of_message = '20260407063000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SQ00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='4567890123', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Nguyen', xpn_2='Thi', xpn_3='Lan', xpn_5='Ms')
        pid.date_time_of_birth = '19870423'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='320 Bloor St W', xad_3='Toronto', xad_4='ON', xad_5='M5S 1W5', xad_6='CA')
        pid.pid_13 = '^^PH^4165554567'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260407001', ei_2='HIS_SURG')
        obr.filler_order_number = EI(ei_1='SPE20260407001', ei_2='SBK_BLOODBANK')
        obr.universal_service_identifier = CWE(cwe_1='XMATCH', cwe_2='Crossmatch', cwe_3='LN')
        obr.observation_date_time = '20260407054500'
        obr.obr_16 = '4567890123^Nguyen^Thi L^^^^'
        obr.results_rpt_status_chng_date_time = '20260407063000'
        obr.diagnostic_serv_sect_id = 'BB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='882-1', cwe_2='ABO Group', cwe_3='LN')
        obx.obx_5 = 'A'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='10331-7', cwe_2='Rh Type', cwe_3='LN')
        obx_2.obx_5 = 'Positive'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='890-4', cwe_2='Antibody Screen', cwe_3='LN')
        obx_3.obx_5 = 'Negative'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='50599-1', cwe_2='Crossmatch', cwe_3='LN')
        obx_4.obx_5 = 'Compatible, 2 units pRBC available'
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
    """ Based on live/ca/ca-sunquest.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SUNQUEST_LIS')
        msh.sending_facility = HD(hd_1='TOH_LAB')
        msh.receiving_application = HD(hd_1='HIS_SURG')
        msh.receiving_facility = HD(hd_1='OTTAWA_GENERAL')
        msh.date_time_of_message = '20260408091000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SQ00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='5678901234', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Pelletier', xpn_2='Martin', xpn_3='Philippe', xpn_5='Mr')
        pid.date_time_of_birth = '19590827'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='67 Bank St', xad_3='Ottawa', xad_4='ON', xad_5='K1P 5N2', xad_6='CA')
        pid.pid_13 = '^^PH^6135555678'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260408001', ei_2='HIS_SURG')
        obr.filler_order_number = EI(ei_1='SPE20260408001', ei_2='TOH_LAB')
        obr.universal_service_identifier = CWE(cwe_1='COAG', cwe_2='Coagulation Panel', cwe_3='LN')
        obr.observation_date_time = '20260408074500'
        obr.obr_16 = '5678901234^Pelletier^Martin P^^^^'
        obr.results_rpt_status_chng_date_time = '20260408091000'
        obr.diagnostic_serv_sect_id = 'HEM'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='PT', cwe_3='LN')
        obx.obx_5 = '12.5'
        obx.units = CWE(cwe_1='s')
        obx.reference_range = '11.0-13.5'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx_2.obx_5 = '1.1'
        obx_2.reference_range = '<1.3'
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
        obx_3.obx_5 = '30'
        obx_3.units = CWE(cwe_1='s')
        obx_3.reference_range = '25-38'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='3255-7', cwe_2='Fibrinogen', cwe_3='LN')
        obx_4.obx_5 = '3.2'
        obx_4.units = CWE(cwe_1='g/L')
        obx_4.reference_range = '2.0-4.0'
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
    """ Based on live/ca/ca-sunquest.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SUNQUEST_LIS')
        msh.sending_facility = HD(hd_1='KGH_LAB')
        msh.receiving_application = HD(hd_1='HIS_MED')
        msh.receiving_facility = HD(hd_1='KINGSTON_GEN')
        msh.date_time_of_message = '20260409113000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SQ00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='6789012345', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Roy', xpn_2='Genevieve', xpn_3='Marie', xpn_5='Mme')
        pid.date_time_of_birth = '19910315'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='22 Clergy St', xad_3='Kingston', xad_4='ON', xad_5='K7K 3N3', xad_6='CA')
        pid.pid_13 = '^^PH^6135556789'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260409001', ei_2='HIS_MED')
        obr.filler_order_number = EI(ei_1='SPE20260409001', ei_2='KGH_LAB')
        obr.universal_service_identifier = CWE(cwe_1='UA', cwe_2='Urinalysis with Microscopy', cwe_3='LN')
        obr.observation_date_time = '20260409081000'
        obr.obr_16 = '6789012345^Roy^Genevieve M^^^^'
        obr.results_rpt_status_chng_date_time = '20260409113000'
        obr.diagnostic_serv_sect_id = 'CHEM'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='5778-6', cwe_2='Color', cwe_3='LN')
        obx.obx_5 = 'Dark Yellow'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='5767-9', cwe_2='Appearance', cwe_3='LN')
        obx_2.obx_5 = 'Hazy'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='5803-2', cwe_2='pH', cwe_3='LN')
        obx_3.obx_5 = '5.5'
        obx_3.reference_range = '5.0-8.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='5811-5', cwe_2='Specific Gravity', cwe_3='LN')
        obx_4.obx_5 = '1.028'
        obx_4.reference_range = '1.005-1.030'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='20454-5', cwe_2='Leukocyte Esterase', cwe_3='LN')
        obx_5.obx_5 = '2+'
        obx_5.reference_range = 'Negative'
        obx_5.interpretation_codes = CWE(cwe_1='A')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='5802-4', cwe_2='Nitrite', cwe_3='LN')
        obx_6.obx_5 = 'Positive'
        obx_6.reference_range = 'Negative'
        obx_6.interpretation_codes = CWE(cwe_1='A')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='5821-4', cwe_2='WBC Micro', cwe_3='LN')
        obx_7.obx_5 = '85'
        obx_7.units = CWE(cwe_1='/HPF')
        obx_7.reference_range = '0-5'
        obx_7.interpretation_codes = CWE(cwe_1='HH')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='13945-1', cwe_2='RBC Micro', cwe_3='LN')
        obx_8.obx_5 = '15'
        obx_8.units = CWE(cwe_1='/HPF')
        obx_8.reference_range = '0-3'
        obx_8.interpretation_codes = CWE(cwe_1='H')
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'ST'
        obx_9.observation_identifier = CWE(cwe_1='25145-4', cwe_2='Bacteria', cwe_3='LN')
        obx_9.obx_5 = 'Many'
        obx_9.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ca/ca-sunquest.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SURG')
        msh.sending_facility = HD(hd_1='LHSC_UNIVERSITY')
        msh.receiving_application = HD(hd_1='SUNQUEST_LIS')
        msh.receiving_facility = HD(hd_1='LHSC_LAB')
        msh.date_time_of_message = '20260410093000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SQ00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7890123456', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lavoie', xpn_2='Pierre', xpn_3='Jean', xpn_5='Mr')
        pid.date_time_of_birth = '19720809'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='200 Richmond St', xad_3='London', xad_4='ON', xad_5='N6A 3L4', xad_6='CA')
        pid.pid_13 = '^^PH^5195557890'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SURG', pl_2='302', pl_3='A', pl_4='London Health Sciences University')
        pv1.attending_doctor = XCN(xcn_1='56789', xcn_2='Chen', xcn_3='Li', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='SURG')
        pv1.patient_type = CWE(cwe_1='VN20260410001')
        pv1.discharge_date_time = '20260410093000'

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
        orc.placer_order_number = EI(ei_1='ORD20260410001', ei_2='HIS_SURG')
        orc.parent_order = EIP(eip_1='20260410093000')
        orc.orc_11 = '56789^Chen^Li^^^Dr.^^CPSO'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260410001', ei_2='HIS_SURG')
        obr.universal_service_identifier = CWE(cwe_1='WCULT', cwe_2='Wound Culture', cwe_3='LN')
        obr.observation_date_time = '20260410093000'
        obr.specimen_action_code = 'R'
        obr.obr_16 = '56789^Chen^Li^^^Dr.^^CPSO'
        obr.obr_27 = '^Post-op wound dehiscence, left lower quadrant'

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
    """ Based on live/ca/ca-sunquest.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SUNQUEST_LIS')
        msh.sending_facility = HD(hd_1='LHSC_LAB')
        msh.receiving_application = HD(hd_1='HIS_SURG')
        msh.receiving_facility = HD(hd_1='LHSC_UNIVERSITY')
        msh.date_time_of_message = '20260412153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SQ00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7890123456', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lavoie', xpn_2='Pierre', xpn_3='Jean', xpn_5='Mr')
        pid.date_time_of_birth = '19720809'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='200 Richmond St', xad_3='London', xad_4='ON', xad_5='N6A 3L4', xad_6='CA')
        pid.pid_13 = '^^PH^5195557890'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260410001', ei_2='HIS_SURG')
        obr.filler_order_number = EI(ei_1='SPE20260410001', ei_2='LHSC_LAB')
        obr.universal_service_identifier = CWE(cwe_1='WCULT', cwe_2='Wound Culture', cwe_3='LN')
        obr.observation_date_time = '20260410093000'
        obr.obr_16 = '7890123456^Lavoie^Pierre J^^^^'
        obr.results_rpt_status_chng_date_time = '20260412153000'
        obr.diagnostic_serv_sect_id = 'MB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Bacteria identified', cwe_3='LN')
        obx.obx_5 = 'Escherichia coli'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='600-7', cwe_2='Bacteria identified', cwe_3='LN')
        obx_2.obx_5 = 'Bacteroides fragilis'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18864-9', cwe_2='Ampicillin (E. coli)', cwe_3='LN')
        obx_3.obx_5 = 'Resistant'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18906-8', cwe_2='Ceftriaxone (E. coli)', cwe_3='LN')
        obx_4.obx_5 = 'Susceptible'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18865-6', cwe_2='Ciprofloxacin (E. coli)', cwe_3='LN')
        obx_5.obx_5 = 'Susceptible'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='18928-5', cwe_2='Metronidazole (B. fragilis)', cwe_3='LN')
        obx_6.obx_5 = 'Susceptible'
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='18943-4', cwe_2='Piperacillin-Tazobactam (B. fragilis)', cwe_3='LN')
        obx_7.obx_5 = 'Susceptible'
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ca/ca-sunquest.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SUNQUEST_LIS')
        msh.sending_facility = HD(hd_1='TOH_LAB')
        msh.receiving_application = HD(hd_1='HIS_ED')
        msh.receiving_facility = HD(hd_1='OTTAWA_CIVIC')
        msh.date_time_of_message = '20260413044500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SQ00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='8901234567', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Poirier', xpn_2='Jacques', xpn_3='Philippe', xpn_5='Mr')
        pid.date_time_of_birth = '19650221'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='500 University Ave', xad_3='Ottawa', xad_4='ON', xad_5='K1N 6N5', xad_6='CA')
        pid.pid_13 = '^^PH^6135558901'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260413001', ei_2='HIS_ED')
        obr.filler_order_number = EI(ei_1='SPE20260413001', ei_2='TOH_LAB')
        obr.universal_service_identifier = CWE(cwe_1='TROP', cwe_2='High-Sensitivity Troponin', cwe_3='LN')
        obr.observation_date_time = '20260413020000'
        obr.obr_16 = '8901234567^Poirier^Jacques P^^^^'
        obr.results_rpt_status_chng_date_time = '20260413044500'
        obr.diagnostic_serv_sect_id = 'CHEM'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='89579-7', cwe_2='hs-Troponin I Baseline', cwe_3='LN')
        obx.obx_5 = '28'
        obx.units = CWE(cwe_1='ng/L')
        obx.reference_range = '<26'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.nature_of_abnormal_test = 'A'
        obx.effective_date_of_reference_range = 'F'
        obx.producers_id = CWE(cwe_1='20260413023000')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='89579-7', cwe_2='hs-Troponin I 3hr', cwe_3='LN')
        obx_2.obx_5 = '145'
        obx_2.units = CWE(cwe_1='ng/L')
        obx_2.reference_range = '<26'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.nature_of_abnormal_test = 'A'
        obx_2.effective_date_of_reference_range = 'F'
        obx_2.producers_id = CWE(cwe_1='20260413050000')

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
    """ Based on live/ca/ca-sunquest.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SUNQUEST_LIS')
        msh.sending_facility = HD(hd_1='HHS_LAB')
        msh.receiving_application = HD(hd_1='HIS_MED')
        msh.receiving_facility = HD(hd_1='HAMILTON_GEN')
        msh.date_time_of_message = '20260414110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SQ00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='9012345678', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Desjardins', xpn_2='Amelie', xpn_3='Rose', xpn_5='Mme')
        pid.date_time_of_birth = '19951118'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='45 James St N', xad_3='Hamilton', xad_4='ON', xad_5='L8R 2K5', xad_6='CA')
        pid.pid_13 = '^^PH^9055559012'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260414001', ei_2='HIS_MED')
        obr.filler_order_number = EI(ei_1='SPE20260414001', ei_2='HHS_LAB')
        obr.universal_service_identifier = CWE(cwe_1='CSF', cwe_2='Cerebrospinal Fluid Analysis', cwe_3='LN')
        obr.observation_date_time = '20260414083000'
        obr.obr_16 = '9012345678^Desjardins^Amelie R^^^^'
        obr.results_rpt_status_chng_date_time = '20260414110000'
        obr.diagnostic_serv_sect_id = 'CHEM'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='26449-9', cwe_2='CSF WBC', cwe_3='LN')
        obx.obx_5 = '850'
        obx.units = CWE(cwe_1='cells/uL')
        obx.reference_range = '0-5'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='26450-7', cwe_2='CSF Neutrophils', cwe_3='LN')
        obx_2.obx_5 = '90'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '0-6'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2342-4', cwe_2='CSF Glucose', cwe_3='LN')
        obx_3.obx_5 = '1.5'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '2.5-4.5'
        obx_3.interpretation_codes = CWE(cwe_1='LL')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2880-3', cwe_2='CSF Protein', cwe_3='LN')
        obx_4.obx_5 = '2.8'
        obx_4.units = CWE(cwe_1='g/L')
        obx_4.reference_range = '0.15-0.45'
        obx_4.interpretation_codes = CWE(cwe_1='HH')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='630-4', cwe_2='CSF Gram Stain', cwe_3='LN')
        obx_5.obx_5 = 'Gram negative diplococci'
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
    """ Based on live/ca/ca-sunquest.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SUNQUEST_LIS')
        msh.sending_facility = HD(hd_1='KGH_LAB')
        msh.receiving_application = HD(hd_1='HIS_ICU')
        msh.receiving_facility = HD(hd_1='KINGSTON_GEN')
        msh.date_time_of_message = '20260415063000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SQ00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0123456789', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lessard', xpn_2='Bruno', xpn_3='Michel', xpn_5='Mr')
        pid.date_time_of_birth = '19530718'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='330 Johnson St', xad_3='Kingston', xad_4='ON', xad_5='K7L 1Y2', xad_6='CA')
        pid.pid_13 = '^^PH^6135550123'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260415001', ei_2='HIS_ICU')
        obr.filler_order_number = EI(ei_1='SPE20260415001', ei_2='KGH_LAB')
        obr.universal_service_identifier = CWE(cwe_1='ABG', cwe_2='Arterial Blood Gas', cwe_3='LN')
        obr.observation_date_time = '20260415060000'
        obr.obr_16 = '0123456789^Lessard^Bruno M^^^^'
        obr.results_rpt_status_chng_date_time = '20260415063000'
        obr.diagnostic_serv_sect_id = 'CHEM'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2744-1', cwe_2='pH', cwe_3='LN')
        obx.obx_5 = '7.28'
        obx.reference_range = '7.35-7.45'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2019-8', cwe_2='pCO2', cwe_3='LN')
        obx_2.obx_5 = '58'
        obx_2.units = CWE(cwe_1='mmHg')
        obx_2.reference_range = '35-45'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2703-7', cwe_2='pO2', cwe_3='LN')
        obx_3.obx_5 = '62'
        obx_3.units = CWE(cwe_1='mmHg')
        obx_3.reference_range = '80-100'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1960-4', cwe_2='Bicarbonate', cwe_3='LN')
        obx_4.obx_5 = '27'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '22-26'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2713-6', cwe_2='Base Excess', cwe_3='LN')
        obx_5.obx_5 = '-1'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '-2 to +2'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2708-6', cwe_2='O2 Saturation', cwe_3='LN')
        obx_6.obx_5 = '89'
        obx_6.units = CWE(cwe_1='%')
        obx_6.reference_range = '95-100'
        obx_6.interpretation_codes = CWE(cwe_1='L')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='2532-0', cwe_2='Lactate', cwe_3='LN')
        obx_7.obx_5 = '3.5'
        obx_7.units = CWE(cwe_1='mmol/L')
        obx_7.reference_range = '0.5-2.2'
        obx_7.interpretation_codes = CWE(cwe_1='H')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ca/ca-sunquest.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SUNQUEST_LIS')
        msh.sending_facility = HD(hd_1='TOH_PATH')
        msh.receiving_application = HD(hd_1='HIS_SURG')
        msh.receiving_facility = HD(hd_1='OTTAWA_GENERAL')
        msh.date_time_of_message = '20260416161500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SQ00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1122334455', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Girard', xpn_2='Monique', xpn_3='Helene', xpn_5='Mme')
        pid.date_time_of_birth = '19680910'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='140 Bay St', xad_3='Ottawa', xad_4='ON', xad_5='K1R 7S8', xad_6='CA')
        pid.pid_13 = '^^PH^6135551122'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260416001', ei_2='HIS_SURG')
        obr.filler_order_number = EI(ei_1='SPE20260416001', ei_2='TOH_PATH')
        obr.universal_service_identifier = CWE(cwe_1='PATH', cwe_2='Surgical Pathology', cwe_3='LN')
        obr.observation_date_time = '20260414090000'
        obr.obr_16 = '1122334455^Girard^Monique H^^^^'
        obr.results_rpt_status_chng_date_time = '20260416161500'
        obr.diagnostic_serv_sect_id = 'AP'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='22637-3', cwe_2='Pathology Report', cwe_3='LN')
        obx.obx_5 = (
            'Specimen: Right hemicolectomy. Diagnosis: Moderately differentiated adenocarcinoma of the ascending colon, 4.2 cm. Invasion through muscular'
            'is propria into pericolonic fat (pT3). 0 of 22 lymph nodes positive (pN0). Margins clear.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Pathology Report PDF', cwe_3='LN')
        obx_2.obx_5 = (
            '^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2Jq'
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
    """ Based on live/ca/ca-sunquest.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SUNQUEST_LIS')
        msh.sending_facility = HD(hd_1='HHS_LAB')
        msh.receiving_application = HD(hd_1='HIS_MED')
        msh.receiving_facility = HD(hd_1='HAMILTON_GEN')
        msh.date_time_of_message = '20260417150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SQ00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2233445566', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Morin', xpn_2='Catherine', xpn_3='Joanne', xpn_5='Mme')
        pid.date_time_of_birth = '19780525'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='85 King St W', xad_3='Hamilton', xad_4='ON', xad_5='L8P 1A2', xad_6='CA')
        pid.pid_13 = '^^PH^9055552233'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260417001', ei_2='HIS_MED')
        obr.filler_order_number = EI(ei_1='SPE20260417001', ei_2='HHS_LAB')
        obr.universal_service_identifier = CWE(cwe_1='BMA', cwe_2='Bone Marrow Aspirate', cwe_3='LN')
        obr.observation_date_time = '20260417093000'
        obr.obr_16 = '2233445566^Morin^Catherine J^^^^'
        obr.results_rpt_status_chng_date_time = '20260417150000'
        obr.diagnostic_serv_sect_id = 'HEM'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='33721-2', cwe_2='Bone Marrow Report', cwe_3='LN')
        obx.obx_5 = (
            'Hypercellular marrow (90%) for age. Myeloid to erythroid ratio 8:1. Marked granulocytic hyperplasia. Blast count 2%. Megakaryocytes adequate'
            '. Iron stores present. No evidence of lymphoma or metastatic disease.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='Bone Marrow Aspirate Image', cwe_3='LN')
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
    """ Based on live/ca/ca-sunquest.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_MED')
        msh.sending_facility = HD(hd_1='LHSC_UNIVERSITY')
        msh.receiving_application = HD(hd_1='SUNQUEST_LIS')
        msh.receiving_facility = HD(hd_1='LHSC_LAB')
        msh.date_time_of_message = '20260418053000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SQ00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3344556677', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Gagnon', xpn_2='Pierre', xpn_3='Louis', xpn_5='Mr')
        pid.date_time_of_birth = '19850617'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='89 Elgin St', xad_3='London', xad_4='ON', xad_5='N5Y 3L5', xad_6='CA')
        pid.pid_13 = '^^PH^5195553344'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='601', pl_3='A', pl_4='London Health Sciences University')
        pv1.attending_doctor = XCN(xcn_1='67890', xcn_2='Patel', xcn_3='Ravi', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='IMED')
        pv1.patient_type = CWE(cwe_1='VN20260418001')
        pv1.discharge_date_time = '20260418053000'

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
        orc.placer_order_number = EI(ei_1='ORD20260418001', ei_2='HIS_MED')
        orc.parent_order = EIP(eip_1='20260418053000')
        orc.orc_11 = '67890^Patel^Ravi^^^Dr.^^CPSO'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260418001', ei_2='HIS_MED')
        obr.universal_service_identifier = CWE(cwe_1='VANC', cwe_2='Vancomycin Trough Level', cwe_3='LN')
        obr.observation_date_time = '20260418053000'
        obr.specimen_action_code = 'S'
        obr.obr_16 = '67890^Patel^Ravi^^^Dr.^^CPSO'
        obr.obr_27 = '^Trough level, next dose at 0600'

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
    """ Based on live/ca/ca-sunquest.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SUNQUEST_LIS')
        msh.sending_facility = HD(hd_1='LHSC_LAB')
        msh.receiving_application = HD(hd_1='HIS_MED')
        msh.receiving_facility = HD(hd_1='LHSC_UNIVERSITY')
        msh.date_time_of_message = '20260418070000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SQ00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3344556677', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Gagnon', xpn_2='Pierre', xpn_3='Louis', xpn_5='Mr')
        pid.date_time_of_birth = '19850617'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='89 Elgin St', xad_3='London', xad_4='ON', xad_5='N5Y 3L5', xad_6='CA')
        pid.pid_13 = '^^PH^5195553344'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260418001', ei_2='HIS_MED')
        obr.filler_order_number = EI(ei_1='SPE20260418001', ei_2='LHSC_LAB')
        obr.universal_service_identifier = CWE(cwe_1='VANC', cwe_2='Vancomycin Trough Level', cwe_3='LN')
        obr.observation_date_time = '20260418053000'
        obr.obr_16 = '3344556677^Gagnon^Pierre L^^^^'
        obr.results_rpt_status_chng_date_time = '20260418070000'
        obr.diagnostic_serv_sect_id = 'CHEM'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4090-7', cwe_2='Vancomycin Trough', cwe_3='LN')
        obx.obx_5 = '22.5'
        obx.units = CWE(cwe_1='mg/L')
        obx.reference_range = '15.0-20.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Lab Worksheet Scan', cwe_3='LN')
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
