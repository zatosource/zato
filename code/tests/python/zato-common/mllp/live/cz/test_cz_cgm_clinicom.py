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
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, AdtA39Patient, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, \
    OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12Patient, \
    SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIS, DG1, EVN, IN1, MRG, MSA, MSH, NK1, OBR, OBX, ORC, PID, PV1, RGS, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('cz', 'cz-cgm-clinicom.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/cz/cz-cgm-clinicom.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINICOM')
        msh.sending_facility = HD(hd_1='NEM_PRIBRAM')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='NEM_PRIBRAM')
        msh.date_time_of_message = '20250410081200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        msh.message_control_id = 'CGM00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250410081200'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='4009033240', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Marek', xpn_2='Petr')
        pid.date_time_of_birth = '19400903'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Nerudova 88', xad_3='Cheb', xad_5='350 02', xad_6='CZ')
        pid.pid_13 = '+420705314756'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='50001', cx_4='NEM_PRIBRAM', cx_5='VN')
        pid.pid_19 = '4009033240'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Marková', xpn_2='Markéta')
        nk1.address = XAD(xad_1='+420720333444')
        nk1.nk1_6 = 'EC'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GAST', pl_2='201', pl_3='1')
        pv1.hospital_service = CWE(cwe_1='GAST')
        pv1.vip_indicator = CWE(cwe_1='N')
        pv1.visit_number = CX(cx_1='20250410081200')
        pv1.diet_type = CWE(cwe_1='NEM_PRIBRAM')
        pv1.pending_location = PL(pl_1='20250410081200')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='111')
        in1.insurance_company_id = CX(cx_1='VZP', cx_2='Všeobecná zdravotní pojišťovna')
        in1.delay_before_lr_day = '111'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'K25.0'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K25.0', cwe_2='Žaludeční vřed akutní s krvácením', cwe_3='ICD10CZ')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.insurance = insurance
        msg.extra_segments = [dg1]

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
    """ Based on live/cz/cz-cgm-clinicom.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINICOM')
        msh.sending_facility = HD(hd_1='NEM_KLADNO')
        msh.receiving_application = HD(hd_1='AMB')
        msh.receiving_facility = HD(hd_1='NEM_KLADNO')
        msh.date_time_of_message = '20250410093000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04')
        msh.message_control_id = 'CGM00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250410093000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='7010048560', cx_4='CPZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Hruška', xpn_2='Vojtěch')
        pid.date_time_of_birth = '19701004'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Budějovická 165', xad_3='Příbram', xad_5='261 01', xad_6='CZ')
        pid.pid_13 = '+420711484632'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='50002', cx_4='NEM_KLADNO', cx_5='VN')
        pid.pid_19 = '7010048560'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='DERM', pl_2='AMB1')
        pv1.temporary_location = PL(pl_1='DERM')
        pv1.admitting_doctor = XCN(xcn_1='R')
        pv1.financial_class = FC(fc_1='20250410093000')
        pv1.servicing_facility = CWE(cwe_1='NEM_KLADNO')
        pv1.prior_temporary_location = PL(pl_1='20250410093000')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'L40.0'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='L40.0', cwe_2='Psoriáza vulgární', cwe_3='ICD10CZ')
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
    """ Based on live/cz/cz-cgm-clinicom.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINICOM')
        msh.sending_facility = HD(hd_1='NEM_PRIBRAM')
        msh.receiving_application = HD(hd_1='LIS')
        msh.receiving_facility = HD(hd_1='NEM_PRIBRAM')
        msh.date_time_of_message = '20250410100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'CGM00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='7356119648', cx_4='OZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Marečková', xpn_2='Jana')
        pid.date_time_of_birth = '19730611'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Pařížská 154', xad_3='České Budějovice', xad_5='370 01', xad_6='CZ')
        pid.pid_13 = '+420601966384'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='50003', cx_4='NEM_PRIBRAM', cx_5='VN')
        pid.pid_19 = '7356119648'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT', pl_2='102', pl_3='2')
        pv1.hospital_service = CWE(cwe_1='INT')

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
        orc.placer_order_number = EI(ei_1='CORD001')
        orc.orc_7 = '^^^20250410110000^^R'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='CORD001')
        obr.universal_service_identifier = CWE(cwe_1='24326-1', cwe_2='Biochemie kompletní', cwe_3='LN')
        obr.observation_date_time = '20250410100000'
        obr.obr_16 = '22001^Čermák^Adam^MUDr.'
        obr.obr_27 = '1^^^20250410110000^^R'

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
    """ Based on live/cz/cz-cgm-clinicom.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='NEM_PRIBRAM')
        msh.receiving_application = HD(hd_1='CLINICOM')
        msh.receiving_facility = HD(hd_1='NEM_PRIBRAM')
        msh.date_time_of_message = '20250410133000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'CGM00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='7356119648', cx_4='OZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Marečková', xpn_2='Jana')
        pid.date_time_of_birth = '19730611'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Pařížská 154', xad_3='České Budějovice', xad_5='370 01', xad_6='CZ')
        pid.pid_13 = '+420601966384'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='50003', cx_4='NEM_PRIBRAM', cx_5='VN')
        pid.pid_19 = '7356119648'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT', pl_2='102', pl_3='2')
        pv1.hospital_service = CWE(cwe_1='INT')

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
        orc.placer_order_number = EI(ei_1='CORD001')
        orc.orc_12 = '22001^Čermák^Adam^MUDr.'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='CORD001')
        obr.universal_service_identifier = CWE(cwe_1='24326-1', cwe_2='Biochemie kompletní', cwe_3='LN')
        obr.observation_date_time = '20250410100000'
        obr.results_rpt_status_chng_date_time = '20250410133000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glukóza', cwe_3='LN')
        obx.obx_5 = '7.2'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.9-5.6'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Kreatinin', cwe_3='LN')
        obx_2.obx_5 = '112'
        obx_2.units = CWE(cwe_1='umol/L')
        obx_2.reference_range = '62-106'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT', cwe_3='LN')
        obx_3.obx_5 = '0.45'
        obx_3.units = CWE(cwe_1='ukat/L')
        obx_3.reference_range = '0.10-0.75'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST', cwe_3='LN')
        obx_4.obx_5 = '0.38'
        obx_4.units = CWE(cwe_1='ukat/L')
        obx_4.reference_range = '0.10-0.72'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ED'
        obx_5.observation_identifier = CWE(cwe_1='11502-2', cwe_2='Laboratorní zpráva', cwe_3='LN')
        obx_5.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoK'
            'PDwgL0xlbmd0aCA1MCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKExhYm9yYXRvcm5pIHpwcmF2YSkgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAw'
            'MDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA3NCAwMDAwMCBuIAowMDAwMDAwMTQyIDAwMDAwIG4gCjAwMDAwMDAyNDIgMDAwMDAgbiAKdHJhaWxlcgo8'
            'PCAvU2l6ZSA1IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozNDIKJSVFT0YK'
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
    """ Based on live/cz/cz-cgm-clinicom.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINICOM')
        msh.sending_facility = HD(hd_1='NEM_KLADNO')
        msh.receiving_application = HD(hd_1='ADT')
        msh.receiving_facility = HD(hd_1='NEM_KLADNO')
        msh.date_time_of_message = '20250411080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08')
        msh.message_control_id = 'CGM00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250411080000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='9062180097', cx_4='CPZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Marková', xpn_2='Lucie')
        pid.date_time_of_birth = '19901218'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Bezručova 13', xad_3='Olomouc', xad_5='779 00', xad_6='CZ')
        pid.pid_13 = '+420692579030'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='50004', cx_4='NEM_KLADNO', cx_5='VN')
        pid.pid_19 = '9062180097'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='INT', pl_2='AMB2')
        pv1.temporary_location = PL(pl_1='INT')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='205')
        in1.insurance_company_id = CX(cx_1='CPZP', cx_2='Česká průmyslová zdravotní pojišťovna')
        in1.delay_before_lr_day = '205'

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
    """ Based on live/cz/cz-cgm-clinicom.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINICOM')
        msh.sending_facility = HD(hd_1='NEM_PRIBRAM')
        msh.receiving_application = HD(hd_1='ADT')
        msh.receiving_facility = HD(hd_1='NEM_PRIBRAM')
        msh.date_time_of_message = '20250412140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03')
        msh.message_control_id = 'CGM00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250412140000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='4009033240', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Marek', xpn_2='Petr')
        pid.date_time_of_birth = '19400903'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Nerudova 88', xad_3='Cheb', xad_5='350 02', xad_6='CZ')
        pid.pid_13 = '+420705314756'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='50001', cx_4='NEM_PRIBRAM', cx_5='VN')
        pid.pid_19 = '4009033240'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GAST', pl_2='201', pl_3='1')
        pv1.hospital_service = CWE(cwe_1='GAST')
        pv1.vip_indicator = CWE(cwe_1='N')
        pv1.visit_number = CX(cx_1='20250410081200')
        pv1.diet_type = CWE(cwe_1='NEM_PRIBRAM')
        pv1.pending_location = PL(pl_1='20250412140000')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'K25.0'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K25.0', cwe_2='Žaludeční vřed akutní s krvácením', cwe_3='ICD10CZ')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = dg1

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
    """ Based on live/cz/cz-cgm-clinicom.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINICOM')
        msh.sending_facility = HD(hd_1='NEM_PRIBRAM')
        msh.receiving_application = HD(hd_1='ENDO')
        msh.receiving_facility = HD(hd_1='NEM_PRIBRAM')
        msh.date_time_of_message = '20250412150000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12')
        msh.message_control_id = 'CGM00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT002')
        sch.event_reason = CWE(cwe_1='KOLO', cwe_2='Kolonoskopie')
        sch.sch_9 = '45'
        sch.appointment_duration_units = CNE(cne_1='min')
        sch.sch_11 = '^^45^20250420080000^20250420084500'
        sch.filler_contact_person = XCN(xcn_1='22002', xcn_2='Janda', xcn_3='Antonín', xcn_4='MUDr.')
        sch.entered_by_person = XCN(xcn_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='0053089933', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Marečková', xpn_2='Renata')
        pid.date_time_of_birth = '20000308'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Třída Svobody 182', xad_3='Třebíč', xad_5='674 01', xad_6='CZ')
        pid.pid_13 = '+420610008245'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='50005', cx_4='NEM_PRIBRAM', cx_5='VN')
        pid.pid_19 = '0053089933'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GAST', pl_2='ENDO1')
        pv1.temporary_location = PL(pl_1='GAST')

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
        ais.universal_service_identifier = CWE(cwe_1='COLONOSCOPY', cwe_2='Kolonoskopie')
        ais.start_date_time_offset = '20250420080000'
        ais.start_date_time_offset_units = CNE(cne_1='45')
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
    """ Based on live/cz/cz-cgm-clinicom.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINICOM')
        msh.sending_facility = HD(hd_1='NEM_KLADNO')
        msh.receiving_application = HD(hd_1='MIKRO')
        msh.receiving_facility = HD(hd_1='NEM_KLADNO')
        msh.date_time_of_message = '20250413070000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'CGM00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='4755057673', cx_4='ZPMV', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Soukupová', xpn_2='Gabriela')
        pid.date_time_of_birth = '19470505'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Kvítková 143', xad_3='Hradec Králové', xad_5='500 02', xad_6='CZ')
        pid.pid_13 = '+420780213018'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='50006', cx_4='NEM_KLADNO', cx_5='VN')
        pid.pid_19 = '4755057673'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INF', pl_2='301', pl_3='2')
        pv1.hospital_service = CWE(cwe_1='INF')

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
        orc.placer_order_number = EI(ei_1='CORD002')
        orc.orc_7 = '^^^20250413120000^^R'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='CORD002')
        obr.universal_service_identifier = CWE(cwe_1='87040', cwe_2='Hemokultivace', cwe_3='CPT')
        obr.observation_date_time = '20250413070000'
        obr.obr_16 = '22003^Marková^Zdeňka^MUDr.'
        obr.obr_27 = '1^^^20250413120000^^R'

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
    """ Based on live/cz/cz-cgm-clinicom.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINICOM')
        msh.sending_facility = HD(hd_1='NEM_PRIBRAM')
        msh.receiving_application = HD(hd_1='ADT')
        msh.receiving_facility = HD(hd_1='NEM_PRIBRAM')
        msh.date_time_of_message = '20250413143000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02')
        msh.message_control_id = 'CGM00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250413143000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='4357033218', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Dvořáková', xpn_2='Monika')
        pid.date_time_of_birth = '19430703'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Spálená 221', xad_3='Vsetín', xad_5='755 01', xad_6='CZ')
        pid.pid_13 = '+420638706079'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='W')
        pid.patient_account_number = CX(cx_1='50007', cx_4='NEM_PRIBRAM', cx_5='VN')
        pid.pid_19 = '4357033218'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='JIP', pl_2='J01', pl_3='1')
        pv1.prior_patient_location = PL(pl_1='CHIR', pl_2='401', pl_3='2')
        pv1.vip_indicator = CWE(cwe_1='N')
        pv1.visit_number = CX(cx_1='20250413100000')
        pv1.diet_type = CWE(cwe_1='NEM_PRIBRAM')
        pv1.pending_location = PL(pl_1='20250413143000')

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/cz/cz-cgm-clinicom.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='NEM_KLADNO')
        msh.receiving_application = HD(hd_1='CLINICOM')
        msh.receiving_facility = HD(hd_1='NEM_KLADNO')
        msh.date_time_of_message = '20250414080000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'CGM00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='6203043847', cx_4='CPZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Růžička', xpn_2='Karel')
        pid.date_time_of_birth = '19620304'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Gočárova 45', xad_3='Praha 2', xad_5='120 00', xad_6='CZ')
        pid.pid_13 = '+420728704344'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='50008', cx_4='NEM_KLADNO', cx_5='VN')
        pid.pid_19 = '6203043847'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HEM', pl_2='101', pl_3='1')
        pv1.hospital_service = CWE(cwe_1='HEM')

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
        orc.placer_order_number = EI(ei_1='CORD003')
        orc.orc_12 = '22004^Urbanová^Petra^MUDr.'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='CORD003')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Krevní obraz', cwe_3='LN')
        obr.observation_date_time = '20250414060000'
        obr.results_rpt_status_chng_date_time = '20250414080000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukocyty', cwe_3='LN')
        obx.obx_5 = '8.2'
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
        obx_2.obx_5 = '4.85'
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
        obx_3.obx_5 = '148'
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
        obx_4.obx_5 = '0.44'
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
        obx_5.obx_5 = '245'
        obx_5.units = CWE(cwe_1='10*9/L')
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
    """ Based on live/cz/cz-cgm-clinicom.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINICOM')
        msh.sending_facility = HD(hd_1='NEM_KLADNO')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='NEM_KLADNO')
        msh.date_time_of_message = '20250414100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28')
        msh.message_control_id = 'CGM00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250414100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='6354044758', cx_4='OZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Soukupová', xpn_2='Jitka')
        pid.date_time_of_birth = '19630404'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Tylova 47', xad_3='Ostrava', xad_5='702 00', xad_6='CZ')
        pid.pid_13 = '+420672872533'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='50009', cx_4='NEM_KLADNO', cx_5='VN')
        pid.pid_19 = '6354044758'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid

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
    """ Based on live/cz/cz-cgm-clinicom.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINICOM')
        msh.sending_facility = HD(hd_1='NEM_PRIBRAM')
        msh.receiving_application = HD(hd_1='EHR')
        msh.receiving_facility = HD(hd_1='NEM_PRIBRAM')
        msh.date_time_of_message = '20250414143000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02')
        msh.message_control_id = 'CGM00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20250414143000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='4009033240', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Marek', xpn_2='Petr')
        pid.date_time_of_birth = '19400903'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Nerudova 88', xad_3='Cheb', xad_5='350 02', xad_6='CZ')
        pid.pid_13 = '+420705314756'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='50001', cx_4='NEM_PRIBRAM', cx_5='VN')
        pid.pid_19 = '4009033240'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GAST', pl_2='201', pl_3='1')
        pv1.hospital_service = CWE(cwe_1='GAST')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS')
        txa.document_content_presentation = 'FT'
        txa.activity_date_time = '20250414140000'
        txa.origination_date_time = '22001^Čermák^Adam^MUDr.'
        txa.unique_document_number = EI(ei_1='DOC002')
        txa.document_confidentiality_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='18842-5', cwe_2='Propouštěcí zpráva', cwe_3='LN')
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
    """ Based on live/cz/cz-cgm-clinicom.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINICOM')
        msh.sending_facility = HD(hd_1='NEM_KLADNO')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='NEM_KLADNO')
        msh.date_time_of_message = '20250415090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40')
        msh.message_control_id = 'CGM00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20250415090000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='6203043847', cx_4='CPZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Růžička', xpn_2='Karel')
        pid.date_time_of_birth = '19620304'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Gočárova 45', xad_3='Praha 2', xad_5='120 00', xad_6='CZ')
        pid.pid_13 = '+420728704344'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='50008', cx_4='NEM_KLADNO', cx_5='VN')
        pid.pid_19 = '6203043847'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='4957688173', cx_4='CPZP', cx_5='NI')
        mrg.prior_patient_account_number = CX(cx_1='50088', cx_4='NEM_KLADNO', cx_5='VN')

        # .. build the PATIENT group ..
        patient = AdtA39Patient()
        patient.pid = pid
        patient.mrg = mrg

        # .. assemble the full message ..
        msg = ADT_A39()
        msg.msh = msh
        msg.evn = evn
        msg.patient = patient

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
    """ Based on live/cz/cz-cgm-clinicom.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINICOM')
        msh.sending_facility = HD(hd_1='NEM_PRIBRAM')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='NEM_PRIBRAM')
        msh.date_time_of_message = '20250415100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'CGM00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='8901151308', cx_4='ZPMV', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Čermák', xpn_2='Radek')
        pid.date_time_of_birth = '19890115'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Třída Svobody 143', xad_3='Plzeň', xad_5='301 00', xad_6='CZ')
        pid.pid_13 = '+420779801848'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='50010', cx_4='NEM_PRIBRAM', cx_5='VN')
        pid.pid_19 = '8901151308'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='402', pl_3='1')
        pv1.hospital_service = CWE(cwe_1='CHIR')

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
        orc.placer_order_number = EI(ei_1='CORD004')
        orc.orc_7 = '^^^20250415130000^^R'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='CORD004')
        obr.universal_service_identifier = CWE(cwe_1='74177', cwe_2='CT břicho s kontrastem', cwe_3='CPT')
        obr.observation_date_time = '20250415100000'
        obr.obr_16 = '22005^Matoušková^Barbora^MUDr.'
        obr.obr_27 = '1^^^20250415130000^^R'

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
    """ Based on live/cz/cz-cgm-clinicom.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS')
        msh.sending_facility = HD(hd_1='NEM_KLADNO')
        msh.receiving_application = HD(hd_1='CLINICOM')
        msh.receiving_facility = HD(hd_1='NEM_KLADNO')
        msh.date_time_of_message = '20250415140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'CGM00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='7010048560', cx_4='CPZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Hruška', xpn_2='Vojtěch')
        pid.date_time_of_birth = '19701004'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Budějovická 165', xad_3='Příbram', xad_5='261 01', xad_6='CZ')
        pid.pid_13 = '+420711484632'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='50002', cx_4='NEM_KLADNO', cx_5='VN')
        pid.pid_19 = '7010048560'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='DERM', pl_2='AMB1')
        pv1.temporary_location = PL(pl_1='DERM')

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
        orc.placer_order_number = EI(ei_1='CORD005')
        orc.orc_12 = '22006^Vacek^Václav^MUDr.'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='CORD005')
        obr.universal_service_identifier = CWE(cwe_1='24357-6', cwe_2='Moč chemicky', cwe_3='LN')
        obr.observation_date_time = '20250415120000'
        obr.results_rpt_status_chng_date_time = '20250415140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='5767-9', cwe_2='pH moči', cwe_3='LN')
        obx.obx_5 = '6.0'
        obx.reference_range = '5.0-7.0'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='2965-2', cwe_2='Specifická hmotnost', cwe_3='LN')
        obx_2.obx_5 = '1.018'
        obx_2.reference_range = '1.005-1.030'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='5794-3', cwe_2='Glukóza v moči', cwe_3='LN')
        obx_3.obx_5 = 'Negativní'
        obx_3.reference_range = 'Negativní'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='5804-0', cwe_2='Protein v moči', cwe_3='LN')
        obx_4.obx_5 = 'Stopy'
        obx_4.reference_range = 'Negativní'
        obx_4.interpretation_codes = CWE(cwe_1='A')
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
    """ Based on live/cz/cz-cgm-clinicom.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MPI')
        msh.sending_facility = HD(hd_1='NEM_KLADNO')
        msh.receiving_application = HD(hd_1='CLINICOM')
        msh.receiving_facility = HD(hd_1='NEM_KLADNO')
        msh.date_time_of_message = '20250415090100'
        msh.message_type = MSG(msg_1='ACK')
        msh.message_control_id = 'CGM00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'CGM00013'
        msa.msa_4 = ''

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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
    """ Based on live/cz/cz-cgm-clinicom.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINICOM')
        msh.sending_facility = HD(hd_1='NEM_PRIBRAM')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='NEM_PRIBRAM')
        msh.date_time_of_message = '20250416080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31')
        msh.message_control_id = 'CGM00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20250416080000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='0053089933', cx_4='VZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Marečková', xpn_2='Renata')
        pid.date_time_of_birth = '20000308'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Třída Svobody 182', xad_3='Třebíč', xad_5='674 01', xad_6='CZ')
        pid.pid_13 = '+420610008245'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='50005', cx_4='NEM_PRIBRAM', cx_5='VN')
        pid.pid_19 = '0053089933'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid

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
    """ Based on live/cz/cz-cgm-clinicom.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIKRO')
        msh.sending_facility = HD(hd_1='NEM_KLADNO')
        msh.receiving_application = HD(hd_1='CLINICOM')
        msh.receiving_facility = HD(hd_1='NEM_KLADNO')
        msh.date_time_of_message = '20250416150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'CGM00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='4755057673', cx_4='ZPMV', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Soukupová', xpn_2='Gabriela')
        pid.date_time_of_birth = '19470505'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Kvítková 143', xad_3='Hradec Králové', xad_5='500 02', xad_6='CZ')
        pid.pid_13 = '+420780213018'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='50006', cx_4='NEM_KLADNO', cx_5='VN')
        pid.pid_19 = '4755057673'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INF', pl_2='301', pl_3='2')
        pv1.hospital_service = CWE(cwe_1='INF')

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
        orc.placer_order_number = EI(ei_1='CORD002')
        orc.orc_12 = '22003^Marková^Zdeňka^MUDr.'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='CORD002')
        obr.universal_service_identifier = CWE(cwe_1='87040', cwe_2='Hemokultivace', cwe_3='CPT')
        obr.observation_date_time = '20250413070000'
        obr.results_rpt_status_chng_date_time = '20250416150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Bakterie identifikace', cwe_3='LN')
        obx.obx_5 = 'Staphylococcus aureus'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18907-6', cwe_2='Citlivost ATB', cwe_3='LN')
        obx_2.obx_5 = 'Oxacilin-S; Vankomycin-S; Klindamycin-S; Kotrimoxazol-S; Ciprofloxacin-R'
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
    """ Based on live/cz/cz-cgm-clinicom.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CLINICOM')
        msh.sending_facility = HD(hd_1='NEM_KLADNO')
        msh.receiving_application = HD(hd_1='ADT')
        msh.receiving_facility = HD(hd_1='NEM_KLADNO')
        msh.date_time_of_message = '20250417060000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        msh.message_control_id = 'CGM00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250417060000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='4757094125', cx_4='VoZP', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Soukupová', xpn_2='Magdalena')
        pid.date_time_of_birth = '19470709'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Tylova 19', xad_3='Vsetín', xad_5='755 01', xad_6='CZ')
        pid.pid_13 = '+420729866312'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='W')
        pid.patient_account_number = CX(cx_1='50011', cx_4='NEM_KLADNO', cx_5='VN')
        pid.pid_19 = '4757094125'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Soukupová', xpn_2='Petra')
        nk1.address = XAD(xad_1='+420732333444')
        nk1.nk1_6 = 'EC'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEU', pl_2='201', pl_3='3')
        pv1.hospital_service = CWE(cwe_1='NEU')
        pv1.vip_indicator = CWE(cwe_1='N')
        pv1.visit_number = CX(cx_1='20250417060000')
        pv1.diet_type = CWE(cwe_1='NEM_KLADNO')
        pv1.pending_location = PL(pl_1='20250417060000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='207')
        in1.insurance_company_id = CX(cx_1='VoZP', cx_2='Vojenská zdravotní pojišťovna')
        in1.delay_before_lr_day = '207'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I63.5'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I63.5', cwe_2='Mozkový infarkt', cwe_3='ICD10CZ')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.insurance = insurance
        msg.extra_segments = [dg1]

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
    """ Based on live/cz/cz-cgm-clinicom.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='NEM_PRIBRAM')
        msh.receiving_application = HD(hd_1='CLINICOM')
        msh.receiving_facility = HD(hd_1='NEM_PRIBRAM')
        msh.date_time_of_message = '20250417100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'CGM00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CZE'
        msh.character_set = '8859/2'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='8901151308', cx_4='ZPMV', cx_5='NI')
        pid.patient_name = XPN(xpn_1='Čermák', xpn_2='Radek')
        pid.date_time_of_birth = '19890115'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Třída Svobody 143', xad_3='Plzeň', xad_5='301 00', xad_6='CZ')
        pid.pid_13 = '+420779801848'
        pid.primary_language = CWE(cwe_1='CZE')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='50010', cx_4='NEM_PRIBRAM', cx_5='VN')
        pid.pid_19 = '8901151308'
        pid.ethnic_group = CWE(cwe_1='CZE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='402', pl_3='1')
        pv1.hospital_service = CWE(cwe_1='CHIR')

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
        orc.placer_order_number = EI(ei_1='CORD004')
        orc.orc_12 = '22007^Hrubý^Josef^MUDr.'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='CORD004')
        obr.universal_service_identifier = CWE(cwe_1='74177', cwe_2='CT břicho s kontrastem', cwe_3='CPT')
        obr.observation_date_time = '20250415130000'
        obr.results_rpt_status_chng_date_time = '20250417100000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='74177', cwe_2='CT nález břicho', cwe_3='CPT')
        obx.obx_5 = (
            'Játra bez ložiskových změn. Žlučník bez konkrementů. Pankreas přiměřený. Ledviny symetrické bez městnání. Bez volné tekutiny v dutině břišní.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='11502-2', cwe_2='Radiologická zpráva', cwe_3='LN')
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
