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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, EI, FC, HD, MSG, PL, PT, VID, XAD, XCN, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA05NextOfKin, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, \
    OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12Patient, SiuS12Resources, \
    SiuS12Service
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A05, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIS, DG1, EVN, IN1, MSA, MSH, NK1, OBR, OBX, ORC, PID, PV1, RGS, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('cz', 'cz-nis-medea.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/cz/cz-nis-medea.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDEA')
        msh.sending_facility = HD(hd_1='PRAKT_PRAHA5')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='SYNLAB_CZ')
        msh.date_time_of_message = '20250401080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04')
        msh.message_control_id = 'MED00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250401080000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='0112097797', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Štěpán', xpn_2='Martin')
        pid.date_time_of_birth = '20011209'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vinohradská 159', xad_3='Karviná', xad_5='733 01', xad_6='CZ')
        pid.pid_13 = '+420742301938'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='P001', cx_4='PRAKT_PRAHA5', cx_5='VN')
        pid.pid_19 = '0112097797'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PRAKT', pl_2='ORD1')
        pv1.temporary_location = PL(pl_1='PRAKT')
        pv1.admitting_doctor = XCN(xcn_1='R')
        pv1.financial_class = FC(fc_1='20250401080000')
        pv1.servicing_facility = CWE(cwe_1='PRAKT_PRAHA5')
        pv1.prior_temporary_location = PL(pl_1='20250401080000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='111')
        in1.insurance_company_id = CX(cx_1='VZP', cx_2='Všeobecná zdravotní pojišťovna')
        in1.delay_before_lr_day = '111'

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
    """ Based on live/cz/cz-nis-medea.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDEA')
        msh.sending_facility = HD(hd_1='PRAKT_PRAHA5')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='SYNLAB_CZ')
        msh.date_time_of_message = '20250401081500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MED00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='0112097797', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Štěpán', xpn_2='Martin')
        pid.date_time_of_birth = '20011209'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vinohradská 159', xad_3='Karviná', xad_5='733 01', xad_6='CZ')
        pid.pid_13 = '+420742301938'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='P001', cx_4='PRAKT_PRAHA5', cx_5='VN')
        pid.pid_19 = '0112097797'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PRAKT', pl_2='ORD1')
        pv1.temporary_location = PL(pl_1='PRAKT')

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
        orc.placer_order_number = EI(ei_1='MORD001')
        orc.orc_7 = '^^^20250401120000^^R'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MORD001')
        obr.universal_service_identifier = CWE(cwe_1='24326-1', cwe_2='Preventivní biochemie', cwe_3='LN')
        obr.observation_date_time = '20250401081500'
        obr.obr_16 = '40001^Kopecký^Vlastimil^MUDr.'
        obr.obr_27 = '1^^^20250401120000^^R'

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
        obr_2.placer_order_number = EI(ei_1='MORD001')
        obr_2.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Krevní obraz', cwe_3='LN')
        obr_2.observation_date_time = '20250401081500'
        obr_2.obr_16 = '40001^Kopecký^Vlastimil^MUDr.'
        obr_2.obr_27 = '1^^^20250401120000^^R'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2]

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
    """ Based on live/cz/cz-nis-medea.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB')
        msh.sending_facility = HD(hd_1='SYNLAB_CZ')
        msh.receiving_application = HD(hd_1='MEDEA')
        msh.receiving_facility = HD(hd_1='PRAKT_PRAHA5')
        msh.date_time_of_message = '20250401153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MED00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='0112097797', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Štěpán', xpn_2='Martin')
        pid.date_time_of_birth = '20011209'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vinohradská 159', xad_3='Karviná', xad_5='733 01', xad_6='CZ')
        pid.pid_13 = '+420742301938'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='P001', cx_4='PRAKT_PRAHA5', cx_5='VN')
        pid.pid_19 = '0112097797'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PRAKT', pl_2='ORD1')
        pv1.temporary_location = PL(pl_1='PRAKT')

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
        orc.placer_order_number = EI(ei_1='MORD001')
        orc.orc_12 = '40001^Kopecký^Vlastimil^MUDr.'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MORD001')
        obr.universal_service_identifier = CWE(cwe_1='24326-1', cwe_2='Preventivní biochemie', cwe_3='LN')
        obr.observation_date_time = '20250401081500'
        obr.results_rpt_status_chng_date_time = '20250401153000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glukóza', cwe_3='LN')
        obx.obx_5 = '5.2'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.9-5.6'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2093-3', cwe_2='Celkový cholesterol', cwe_3='LN')
        obx_2.obx_5 = '5.8'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '<5.0'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='13457-7', cwe_2='LDL cholesterol', cwe_3='LN')
        obx_3.obx_5 = '3.6'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '<3.0'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2571-8', cwe_2='HDL cholesterol', cwe_3='LN')
        obx_4.obx_5 = '1.4'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '>1.0'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2571-8', cwe_2='Triglyceridy', cwe_3='LN')
        obx_5.obx_5 = '1.7'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '<1.7'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT', cwe_3='LN')
        obx_6.obx_5 = '0.52'
        obx_6.units = CWE(cwe_1='ukat/L')
        obx_6.reference_range = '0.10-0.75'
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Kreatinin', cwe_3='LN')
        obx_7.obx_5 = '88'
        obx_7.units = CWE(cwe_1='umol/L')
        obx_7.reference_range = '62-106'
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
    """ Based on live/cz/cz-nis-medea.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB')
        msh.sending_facility = HD(hd_1='SYNLAB_CZ')
        msh.receiving_application = HD(hd_1='MEDEA')
        msh.receiving_facility = HD(hd_1='PRAKT_PRAHA5')
        msh.date_time_of_message = '20250401154500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MED00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='0112097797', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Štěpán', xpn_2='Martin')
        pid.date_time_of_birth = '20011209'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vinohradská 159', xad_3='Karviná', xad_5='733 01', xad_6='CZ')
        pid.pid_13 = '+420742301938'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='P001', cx_4='PRAKT_PRAHA5', cx_5='VN')
        pid.pid_19 = '0112097797'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PRAKT', pl_2='ORD1')
        pv1.temporary_location = PL(pl_1='PRAKT')

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
        orc.placer_order_number = EI(ei_1='MORD001')
        orc.orc_12 = '40001^Kopecký^Vlastimil^MUDr.'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MORD001')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Krevní obraz', cwe_3='LN')
        obr.observation_date_time = '20250401081500'
        obr.results_rpt_status_chng_date_time = '20250401154500'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukocyty', cwe_3='LN')
        obx.obx_5 = '6.8'
        obx.units = CWE(cwe_1='10*9/L')
        obx.reference_range = '4.0-10.0'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erytrocyty', cwe_3='LN')
        obx_2.obx_5 = '5.12'
        obx_2.units = CWE(cwe_1='10*12/L')
        obx_2.reference_range = '4.0-5.8'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin', cwe_3='LN')
        obx_3.obx_5 = '152'
        obx_3.units = CWE(cwe_1='g/L')
        obx_3.reference_range = '130-170'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematokrit', cwe_3='LN')
        obx_4.obx_5 = '0.45'
        obx_4.units = CWE(cwe_1='L/L')
        obx_4.reference_range = '0.39-0.50'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='Trombocyty', cwe_3='LN')
        obx_5.obx_5 = '220'
        obx_5.units = CWE(cwe_1='10*9/L')
        obx_5.reference_range = '150-400'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ED'
        obx_6.observation_identifier = CWE(cwe_1='11502-2', cwe_2='Laboratorní zpráva', cwe_3='LN')
        obx_6.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoK'
            'PDwgL0xlbmd0aCA1MCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKExhYm9yYXRvcm5pIHpwcmF2YSkgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAw'
            'MDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA3NCAwMDAwMCBuIAowMDAwMDAwMTQyIDAwMDAwIG4gCjAwMDAwMDAyNDIgMDAwMDAgbiAKdHJhaWxlcgo8'
            'PCAvU2l6ZSA1IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozNDIKJSVFT0YK'
        )
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
    """ Based on live/cz/cz-nis-medea.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDEA')
        msh.sending_facility = HD(hd_1='DIAB_BRNO')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='SYNLAB_CZ')
        msh.date_time_of_message = '20250402090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04')
        msh.message_control_id = 'MED00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250402090000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='7610092462', cx_4='OZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Sedláček', xpn_2='Adam')
        pid.date_time_of_birth = '19761009'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Bezručova 140', xad_3='Praha 2', xad_5='120 00', xad_6='CZ')
        pid.pid_13 = '+420649483750'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='P002', cx_4='DIAB_BRNO', cx_5='VN')
        pid.pid_19 = '7610092462'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='DIAB', pl_2='ORD1')
        pv1.temporary_location = PL(pl_1='DIAB')
        pv1.admitting_doctor = XCN(xcn_1='R')
        pv1.financial_class = FC(fc_1='20250402090000')
        pv1.servicing_facility = CWE(cwe_1='DIAB_BRNO')
        pv1.prior_temporary_location = PL(pl_1='20250402090000')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'E11.6'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='E11.6', cwe_2='DM 2. typu s jinými komplikacemi', cwe_3='ICD10CZ')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = dg1

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
    """ Based on live/cz/cz-nis-medea.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDEA')
        msh.sending_facility = HD(hd_1='DIAB_BRNO')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='SYNLAB_CZ')
        msh.date_time_of_message = '20250402091000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MED00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='7610092462', cx_4='OZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Sedláček', xpn_2='Adam')
        pid.date_time_of_birth = '19761009'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Bezručova 140', xad_3='Praha 2', xad_5='120 00', xad_6='CZ')
        pid.pid_13 = '+420649483750'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='P002', cx_4='DIAB_BRNO', cx_5='VN')
        pid.pid_19 = '7610092462'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='DIAB', pl_2='ORD1')
        pv1.temporary_location = PL(pl_1='DIAB')

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
        orc.placer_order_number = EI(ei_1='MORD002')
        orc.orc_7 = '^^^20250402130000^^R'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MORD002')
        obr.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obr.observation_date_time = '20250402091000'
        obr.obr_16 = '40002^Tomek^Radek^MUDr.'
        obr.obr_27 = '1^^^20250402130000^^R'

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
    """ Based on live/cz/cz-nis-medea.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB')
        msh.sending_facility = HD(hd_1='SYNLAB_CZ')
        msh.receiving_application = HD(hd_1='MEDEA')
        msh.receiving_facility = HD(hd_1='DIAB_BRNO')
        msh.date_time_of_message = '20250402143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MED00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='7610092462', cx_4='OZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Sedláček', xpn_2='Adam')
        pid.date_time_of_birth = '19761009'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Bezručova 140', xad_3='Praha 2', xad_5='120 00', xad_6='CZ')
        pid.pid_13 = '+420649483750'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='P002', cx_4='DIAB_BRNO', cx_5='VN')
        pid.pid_19 = '7610092462'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='DIAB', pl_2='ORD1')
        pv1.temporary_location = PL(pl_1='DIAB')

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
        orc.placer_order_number = EI(ei_1='MORD002')
        orc.orc_12 = '40002^Tomek^Radek^MUDr.'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MORD002')
        obr.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obr.observation_date_time = '20250402091000'
        obr.results_rpt_status_chng_date_time = '20250402143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obx.obx_5 = '58'
        obx.units = CWE(cwe_1='mmol/mol')
        obx.reference_range = '<42'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glukóza', cwe_3='LN')
        obx_2.obx_5 = '8.9'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '3.9-5.6'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

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
    """ Based on live/cz/cz-nis-medea.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDEA')
        msh.sending_facility = HD(hd_1='PRAKT_PRAHA5')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='PRAKT_PRAHA5')
        msh.date_time_of_message = '20250403080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08')
        msh.message_control_id = 'MED00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250403080000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='0112097797', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Štěpán', xpn_2='Martin')
        pid.date_time_of_birth = '20011209'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vinohradská 159', xad_3='Karviná', xad_5='733 01', xad_6='CZ')
        pid.pid_13 = '+420742301938'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='P001', cx_4='PRAKT_PRAHA5', cx_5='VN')
        pid.pid_19 = '0112097797'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PRAKT', pl_2='ORD1')
        pv1.temporary_location = PL(pl_1='PRAKT')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'E78.0'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='E78.0', cwe_2='Čistá hypercholesterolémie', cwe_3='ICD10CZ')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = dg1

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
    """ Based on live/cz/cz-nis-medea.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDEA')
        msh.sending_facility = HD(hd_1='ORL_OSTRAVA')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='FN_OSTRAVA')
        msh.date_time_of_message = '20250404090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04')
        msh.message_control_id = 'MED00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250404090000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='8457152592', cx_4='CPZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Kolářová', xpn_2='Adéla')
        pid.date_time_of_birth = '19840715'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Gočárova 19', xad_3='Praha 6', xad_5='160 00', xad_6='CZ')
        pid.pid_13 = '+420765092167'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='P003', cx_4='ORL_OSTRAVA', cx_5='VN')
        pid.pid_19 = '8457152592'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ORL', pl_2='ORD1')
        pv1.temporary_location = PL(pl_1='ORL')
        pv1.admitting_doctor = XCN(xcn_1='R')
        pv1.financial_class = FC(fc_1='20250404090000')
        pv1.servicing_facility = CWE(cwe_1='ORL_OSTRAVA')
        pv1.prior_temporary_location = PL(pl_1='20250404090000')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'J32.0'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J32.0', cwe_2='Chronická sinusitida maxilární', cwe_3='ICD10CZ')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = dg1

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
    """ Based on live/cz/cz-nis-medea.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDEA')
        msh.sending_facility = HD(hd_1='ORL_OSTRAVA')
        msh.receiving_application = HD(hd_1='SCHED')
        msh.receiving_facility = HD(hd_1='ORL_OSTRAVA')
        msh.date_time_of_message = '20250404091500'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12')
        msh.message_control_id = 'MED00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT004')
        sch.event_reason = CWE(cwe_1='AUDIO', cwe_2='Audiometrie')
        sch.sch_9 = '20'
        sch.appointment_duration_units = CNE(cne_1='min')
        sch.sch_11 = '^^20^20250410100000^20250410102000'
        sch.filler_contact_person = XCN(xcn_1='40003', xcn_2='Kratochvíl', xcn_3='Jiří', xcn_4='MUDr.')
        sch.entered_by_person = XCN(xcn_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='8457152592', cx_4='CPZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Kolářová', xpn_2='Adéla')
        pid.date_time_of_birth = '19840715'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Gočárova 19', xad_3='Praha 6', xad_5='160 00', xad_6='CZ')
        pid.pid_13 = '+420765092167'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='P003', cx_4='ORL_OSTRAVA', cx_5='VN')
        pid.pid_19 = '8457152592'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ORL', pl_2='ORD1')
        pv1.temporary_location = PL(pl_1='ORL')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='AUDIOMETRY', cwe_2='Audiometrie')
        ais.start_date_time_offset = '20250410100000'
        ais.start_date_time_offset_units = CNE(cne_1='20')
        ais.duration = 'min'

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources

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
    """ Based on live/cz/cz-nis-medea.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDEA')
        msh.sending_facility = HD(hd_1='PED_LIBEREC')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='PED_LIBEREC')
        msh.date_time_of_message = '20250405080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28')
        msh.message_control_id = 'MED00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250405080000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='6406133062', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Pavlík', xpn_2='Dalibor')
        pid.date_time_of_birth = '19640613'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Pařížská 5', xad_3='Vsetín', xad_5='755 01', xad_6='CZ')
        pid.pid_13 = '+420708696909'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='P004', cx_4='PED_LIBEREC', cx_5='VN')
        pid.pid_19 = '6406133062'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Pavlíková', xpn_2='Eliška')
        nk1.address = XAD(xad_1='+420773444555')
        nk1.nk1_6 = 'MTH'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin

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
    """ Based on live/cz/cz-nis-medea.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDEA')
        msh.sending_facility = HD(hd_1='ALERG_PRAHA')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='SYNLAB_CZ')
        msh.date_time_of_message = '20250406090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MED00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='8457152592', cx_4='CPZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Kolářová', xpn_2='Adéla')
        pid.date_time_of_birth = '19840715'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Gočárova 19', xad_3='Praha 6', xad_5='160 00', xad_6='CZ')
        pid.pid_13 = '+420765092167'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='P003', cx_4='ORL_OSTRAVA', cx_5='VN')
        pid.pid_19 = '8457152592'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ALERG', pl_2='ORD1')
        pv1.temporary_location = PL(pl_1='ALERG')

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
        orc.placer_order_number = EI(ei_1='MORD003')
        orc.orc_7 = '^^^20250406140000^^R'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MORD003')
        obr.universal_service_identifier = CWE(cwe_1='21232-4', cwe_2='Alergenový panel', cwe_3='LN')
        obr.observation_date_time = '20250406090000'
        obr.obr_16 = '40004^Soukupová^Monika^MUDr.'
        obr.obr_27 = '1^^^20250406140000^^R'

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
    """ Based on live/cz/cz-nis-medea.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB')
        msh.sending_facility = HD(hd_1='SYNLAB_CZ')
        msh.receiving_application = HD(hd_1='MEDEA')
        msh.receiving_facility = HD(hd_1='ALERG_PRAHA')
        msh.date_time_of_message = '20250407100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MED00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='8457152592', cx_4='CPZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Kolářová', xpn_2='Adéla')
        pid.date_time_of_birth = '19840715'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Gočárova 19', xad_3='Praha 6', xad_5='160 00', xad_6='CZ')
        pid.pid_13 = '+420765092167'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='P003', cx_4='ORL_OSTRAVA', cx_5='VN')
        pid.pid_19 = '8457152592'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ALERG', pl_2='ORD1')
        pv1.temporary_location = PL(pl_1='ALERG')

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
        orc.placer_order_number = EI(ei_1='MORD003')
        orc.orc_12 = '40004^Soukupová^Monika^MUDr.'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MORD003')
        obr.universal_service_identifier = CWE(cwe_1='21232-4', cwe_2='Alergenový panel', cwe_3='LN')
        obr.observation_date_time = '20250406090000'
        obr.results_rpt_status_chng_date_time = '20250407100000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='19113-0', cwe_2='IgE celkové', cwe_3='LN')
        obx.obx_5 = '245'
        obx.units = CWE(cwe_1='kU/L')
        obx.reference_range = '<100'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6833-8', cwe_2='IgE spec. d1 roztoči', cwe_3='LN')
        obx_2.obx_5 = '18.5'
        obx_2.units = CWE(cwe_1='kU/L')
        obx_2.reference_range = '<0.35'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6812-2', cwe_2='IgE spec. e1 kočka', cwe_3='LN')
        obx_3.obx_5 = '0.12'
        obx_3.units = CWE(cwe_1='kU/L')
        obx_3.reference_range = '<0.35'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='6158-0', cwe_2='IgE spec. g6 trávy', cwe_3='LN')
        obx_4.obx_5 = '42.3'
        obx_4.units = CWE(cwe_1='kU/L')
        obx_4.reference_range = '<0.35'
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
    """ Based on live/cz/cz-nis-medea.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDEA')
        msh.sending_facility = HD(hd_1='PRAKT_PRAHA5')
        msh.receiving_application = HD(hd_1='EHR')
        msh.receiving_facility = HD(hd_1='FN_MOTOL')
        msh.date_time_of_message = '20250407140000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02')
        msh.message_control_id = 'MED00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20250407140000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='0112097797', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Štěpán', xpn_2='Martin')
        pid.date_time_of_birth = '20011209'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vinohradská 159', xad_3='Karviná', xad_5='733 01', xad_6='CZ')
        pid.pid_13 = '+420742301938'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='P001', cx_4='PRAKT_PRAHA5', cx_5='VN')
        pid.pid_19 = '0112097797'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PRAKT', pl_2='ORD1')
        pv1.temporary_location = PL(pl_1='PRAKT')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='REF')
        txa.document_content_presentation = 'FT'
        txa.activity_date_time = '20250407135000'
        txa.origination_date_time = '40001^Kopecký^Vlastimil^MUDr.'
        txa.unique_document_number = EI(ei_1='DOC004')
        txa.document_confidentiality_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='57133-1', cwe_2='Žádanka o vyšetření', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoK'
            'PDwgL0xlbmd0aCA1MCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKExhYm9yYXRvcm5pIHpwcmF2YSkgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAw'
            'MDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA3NCAwMDAwMCBuIAowMDAwMDAwMTQyIDAwMDAwIG4gCjAwMDAwMDAyNDIgMDAwMDAgbiAKdHJhaWxlcgo8'
            'PCAvU2l6ZSA1IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozNDIKJSVFT0YK'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx

        # .. assemble the full message ..
        msg = MDM_T02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.txa = txa
        msg.observation = observation

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
    """ Based on live/cz/cz-nis-medea.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB')
        msh.sending_facility = HD(hd_1='SYNLAB_CZ')
        msh.receiving_application = HD(hd_1='MEDEA')
        msh.receiving_facility = HD(hd_1='PRAKT_PRAHA5')
        msh.date_time_of_message = '20250401082000'
        msh.message_type = MSG(msg_1='ACK')
        msh.message_control_id = 'MED00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'MED00002'
        msa.msa_4 = ''

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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
    """ Based on live/cz/cz-nis-medea.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDEA')
        msh.sending_facility = HD(hd_1='PRAKT_PRAHA5')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='PRAKT_PRAHA5')
        msh.date_time_of_message = '20250408080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31')
        msh.message_control_id = 'MED00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20250408080000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='7610092462', cx_4='OZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Sedláček', xpn_2='Adam')
        pid.date_time_of_birth = '19761009'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Bezručova 140', xad_3='Praha 2', xad_5='120 00', xad_6='CZ')
        pid.pid_13 = '+420649483750'
        pid.pid_14 = 'adam.sedlacek@email.cz'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='P002', cx_4='DIAB_BRNO', cx_5='VN')
        pid.pid_19 = '7610092462'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid

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
    """ Based on live/cz/cz-nis-medea.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDEA')
        msh.sending_facility = HD(hd_1='OCNI_PLZEN')
        msh.receiving_application = HD(hd_1='AMB')
        msh.receiving_facility = HD(hd_1='OCNI_PLZEN')
        msh.date_time_of_message = '20250408100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04')
        msh.message_control_id = 'MED00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250408100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='8356140714', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Pavlíková', xpn_2='Petra')
        pid.date_time_of_birth = '19830614'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Mendelovo náměstí 91', xad_3='Praha 1', xad_5='110 00', xad_6='CZ')
        pid.pid_13 = '+420610823300'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='P005', cx_4='OCNI_PLZEN', cx_5='VN')
        pid.pid_19 = '8356140714'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OCNI', pl_2='ORD1')
        pv1.temporary_location = PL(pl_1='OCNI')
        pv1.admitting_doctor = XCN(xcn_1='R')
        pv1.financial_class = FC(fc_1='20250408100000')
        pv1.servicing_facility = CWE(cwe_1='OCNI_PLZEN')
        pv1.prior_temporary_location = PL(pl_1='20250408100000')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'H40.1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='H40.1', cwe_2='Primární glaukom s otevřeným úhlem', cwe_3='ICD10CZ')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = dg1

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
    """ Based on live/cz/cz-nis-medea.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDEA')
        msh.sending_facility = HD(hd_1='OCNI_PLZEN')
        msh.receiving_application = HD(hd_1='DIAG')
        msh.receiving_facility = HD(hd_1='OCNI_PLZEN')
        msh.date_time_of_message = '20250408101000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MED00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='8356140714', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Pavlíková', xpn_2='Petra')
        pid.date_time_of_birth = '19830614'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Mendelovo náměstí 91', xad_3='Praha 1', xad_5='110 00', xad_6='CZ')
        pid.pid_13 = '+420610823300'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='P005', cx_4='OCNI_PLZEN', cx_5='VN')
        pid.pid_19 = '8356140714'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OCNI', pl_2='ORD1')
        pv1.temporary_location = PL(pl_1='OCNI')

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
        orc.placer_order_number = EI(ei_1='MORD004')
        orc.orc_7 = '^^^20250408103000^^R'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MORD004')
        obr.universal_service_identifier = CWE(cwe_1='IOP', cwe_2='Tonometrie', cwe_3='LOCAL')
        obr.observation_date_time = '20250408101000'
        obr.obr_16 = '40005^Vacková^Bohuslava^MUDr.'
        obr.obr_27 = '1^^^20250408103000^^R'

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
    """ Based on live/cz/cz-nis-medea.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DIAG')
        msh.sending_facility = HD(hd_1='OCNI_PLZEN')
        msh.receiving_application = HD(hd_1='MEDEA')
        msh.receiving_facility = HD(hd_1='OCNI_PLZEN')
        msh.date_time_of_message = '20250408104500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MED00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='8356140714', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Pavlíková', xpn_2='Petra')
        pid.date_time_of_birth = '19830614'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Mendelovo náměstí 91', xad_3='Praha 1', xad_5='110 00', xad_6='CZ')
        pid.pid_13 = '+420610823300'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='P005', cx_4='OCNI_PLZEN', cx_5='VN')
        pid.pid_19 = '8356140714'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OCNI', pl_2='ORD1')
        pv1.temporary_location = PL(pl_1='OCNI')

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
        orc.placer_order_number = EI(ei_1='MORD004')
        orc.orc_12 = '40005^Vacková^Bohuslava^MUDr.'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MORD004')
        obr.universal_service_identifier = CWE(cwe_1='IOP', cwe_2='Tonometrie', cwe_3='LOCAL')
        obr.observation_date_time = '20250408101000'
        obr.results_rpt_status_chng_date_time = '20250408104500'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='IOP_R', cwe_2='Nitrooční tlak pravé oko', cwe_3='LOCAL')
        obx.obx_5 = '22'
        obx.units = CWE(cwe_1='mmHg')
        obx.reference_range = '10-21'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='IOP_L', cwe_2='Nitrooční tlak levé oko', cwe_3='LOCAL')
        obx_2.obx_5 = '19'
        obx_2.units = CWE(cwe_1='mmHg')
        obx_2.reference_range = '10-21'
        obx_2.observation_result_status = 'F'

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
    """ Based on live/cz/cz-nis-medea.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDEA')
        msh.sending_facility = HD(hd_1='OCNI_PLZEN')
        msh.receiving_application = HD(hd_1='EHR')
        msh.receiving_facility = HD(hd_1='OCNI_PLZEN')
        msh.date_time_of_message = '20250408110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MED00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='8356140714', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Pavlíková', xpn_2='Petra')
        pid.date_time_of_birth = '19830614'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Mendelovo náměstí 91', xad_3='Praha 1', xad_5='110 00', xad_6='CZ')
        pid.pid_13 = '+420610823300'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='P005', cx_4='OCNI_PLZEN', cx_5='VN')
        pid.pid_19 = '8356140714'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OCNI', pl_2='ORD1')
        pv1.temporary_location = PL(pl_1='OCNI')

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
        orc.placer_order_number = EI(ei_1='MORD004')
        orc.orc_12 = '40005^Vacková^Bohuslava^MUDr.'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='MORD004')
        obr.universal_service_identifier = CWE(cwe_1='IOP', cwe_2='Oční vyšetření', cwe_3='LOCAL')
        obr.observation_date_time = '20250408101000'
        obr.results_rpt_status_chng_date_time = '20250408110000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='IOP', cwe_2='Závěr oční vyšetření', cwe_3='LOCAL')
        obx.obx_5 = 'Glaukom s otevřeným úhlem bilat., NOT pod kontrolou vpravo. Doporučena úprava terapie - přidání prostaglandinového analogu.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='11502-2', cwe_2='Oční nález', cwe_3='LN')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoK'
            'PDwgL0xlbmd0aCA1MCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKExhYm9yYXRvcm5pIHpwcmF2YSkgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAw'
            'MDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA3NCAwMDAwMCBuIAowMDAwMDAwMTQyIDAwMDAwIG4gCjAwMDAwMDAyNDIgMDAwMDAgbiAKdHJhaWxlcgo8'
            'PCAvU2l6ZSA1IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozNDIKJSVFT0YK'
        )
        obx_2.observation_result_status = 'F'

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
