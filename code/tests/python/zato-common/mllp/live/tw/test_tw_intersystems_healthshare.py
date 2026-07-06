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
from zato.hl7v2.v2_9.datatypes import CWE, CX, DLD, EI, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, AdtA39Patient, MdmT02Observation, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A39, MDM_T02, ORU_R01, REF_I12
from zato.hl7v2.v2_9.segments import DG1, EVN, IN1, MRG, MSH, NK1, OBR, OBX, ORC, PID, PRD, PV1, PV2, RF1, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('tw', 'tw-intersystems-healthshare.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/tw/tw-intersystems-healthshare.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-CYGH')
        msh.sending_facility = HD(hd_1='CYGH_HOSP')
        msh.receiving_application = HD(hd_1='HealthShare')
        msh.receiving_facility = HD(hd_1='CYGH_HIE')
        msh.date_time_of_message = '20260301080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20260301080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260301080000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT800100', cx_4='CYGH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='賴', xpn_2='國華')
        pid.date_time_of_birth = '19631030'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='嘉義市西區民族路100號', xad_3='嘉義市', xad_4='60041', xad_5='TW')
        pid.pid_13 = '05-2765432'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'E614782935'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='賴陳秀英')
        nk1.relationship = CWE(cwe_1='SPO')
        nk1.address = XAD(xad_1='嘉義市西區民族路100號', xad_3='嘉義市', xad_4='60041', xad_5='TW')
        nk1.nk1_5 = '05-2765432'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='601', pl_3='01')
        pv1.pv1_7 = 'D800100^蕭志遠^^^^^CYGH_HOSP'
        pv1.visit_number = CX(cx_1='V800100001')
        pv1.diet_type = CWE(cwe_1='CYGH_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260301080000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='NHI')
        in1.insurance_company_id = CX(cx_1='NHI_TW')
        in1.insurance_company_name = XON(xon_1='全民健康保險')
        in1.insureds_address = XAD(xad_1='E614782935')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I25.10', cwe_2='冠狀動脈粥狀硬化性心臟病', cwe_3='I10')
        dg1.diagnosis_date_time = '20260301'

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
    """ Based on live/tw/tw-intersystems-healthshare.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-CYGH')
        msh.sending_facility = HD(hd_1='CYGH_HOSP')
        msh.receiving_application = HD(hd_1='HealthShare')
        msh.receiving_facility = HD(hd_1='CYGH_HIE')
        msh.date_time_of_message = '20260302090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20260302090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260302090000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT800200', cx_4='CYGH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='程', xpn_2='惠玲')
        pid.date_time_of_birth = '19800516'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='嘉義縣朴子市文化北路88號', xad_3='嘉義縣', xad_4='61341', xad_5='TW')
        pid.pid_13 = '05-3791234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'F725893046'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ENDO', pl_2='101', pl_3='01')
        pv1.pv1_7 = 'D800200^方筱雯^^^^^CYGH_HOSP'
        pv1.visit_number = CX(cx_1='V800200001')
        pv1.diet_type = CWE(cwe_1='CYGH_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260302090000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='NHI')
        in1.insurance_company_id = CX(cx_1='NHI_TW')
        in1.insurance_company_name = XON(xon_1='全民健康保險')
        in1.insureds_address = XAD(xad_1='F725893046')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='E11.9', cwe_2='第二型糖尿病', cwe_3='I10')
        dg1.diagnosis_date_time = '20260302'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.insurance = insurance
        msg.extra_segments = [dg1]

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
    """ Based on live/tw/tw-intersystems-healthshare.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS-CYGH')
        msh.sending_facility = HD(hd_1='CYGH_LAB')
        msh.receiving_application = HD(hd_1='HealthShare')
        msh.receiving_facility = HD(hd_1='CYGH_HIE')
        msh.date_time_of_message = '20260302143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260302143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT800200', cx_4='CYGH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='程', xpn_2='惠玲')
        pid.date_time_of_birth = '19800516'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='嘉義縣朴子市文化北路88號', xad_3='嘉義縣', xad_4='61341', xad_5='TW')
        pid.pid_13 = '05-3791234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'F725893046'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ENDO', pl_2='101', pl_3='01')
        pv1.pv1_7 = 'D800200^方筱雯^^^^^CYGH_HOSP'
        pv1.visit_number = CX(cx_1='V800200001')

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
        orc.placer_order_number = EI(ei_1='ORD800200001')
        orc.orc_10 = 'D800200^方筱雯'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800200001')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='基本代謝綜合檢驗', cwe_3='LN')
        obr.observation_date_time = '20260302100000'
        obr.obr_16 = 'D800200^方筱雯'
        obr.results_rpt_status_chng_date_time = '20260302140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='血糖(飯前)', cwe_3='LN')
        obx.obx_5 = '156'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '70-100'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4548-4', cwe_2='糖化血色素', cwe_3='LN')
        obx_2.obx_5 = '8.2'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '4.0-6.0'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2160-0', cwe_2='肌酸酐', cwe_3='LN')
        obx_3.obx_5 = '0.9'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '0.6-1.2'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='3094-0', cwe_2='尿素氮', cwe_3='LN')
        obx_4.obx_5 = '18'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '7-20'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2951-2', cwe_2='鈉', cwe_3='LN')
        obx_5.obx_5 = '140'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '136-145'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2823-3', cwe_2='鉀', cwe_3='LN')
        obx_6.obx_5 = '4.2'
        obx_6.units = CWE(cwe_1='mmol/L')
        obx_6.reference_range = '3.5-5.1'
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
    """ Based on live/tw/tw-intersystems-healthshare.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HealthShare')
        msh.sending_facility = HD(hd_1='CYGH_HIE')
        msh.receiving_application = HD(hd_1='EMR-Exchange')
        msh.receiving_facility = HD(hd_1='MOHW_HIE')
        msh.date_time_of_message = '20260308100000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG20260308100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260308100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT800100', cx_4='CYGH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='賴', xpn_2='國華')
        pid.date_time_of_birth = '19631030'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='嘉義市西區民族路100號', xad_3='嘉義市', xad_4='60041', xad_5='TW')
        pid.pid_13 = '05-2765432'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'E614782935'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='601', pl_3='01')
        pv1.pv1_7 = 'D800100^蕭志遠^^^^^CYGH_HOSP'
        pv1.visit_number = CX(cx_1='V800100001')
        pv1.discharged_to_location = DLD(dld_1='01')
        pv1.diet_type = CWE(cwe_1='CYGH_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260301080000')
        pv1.current_patient_balance = '20260308090000'

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='出院摘要')
        txa.document_content_presentation = 'AP'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20260308090000')
        txa.assigned_document_authenticator = XCN(xcn_1='D800100', xcn_2='蕭志遠')
        txa.unique_document_number = EI(ei_1='DOC800100001')
        txa.unique_document_file_name = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='18842-5', cwe_2='出院摘要CDA文件', cwe_3='LN')
        obx.obx_5 = (
            '^application^xml^Base64^'
            'PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIj4KICA8dGl0bGU+5b2w5YyW5Z+66Led5pWZ6Yar6ZmiIOWHuumZouaRmOimgTwvdGl0bGU+CiAgPGVmZmVjdGl2'
            'ZVRpbWUgdmFsdWU9IjIwMjYwMzA4MDkwMDAwIi8+CiAgPHJlY29yZFRhcmdldD4KICAgIDxwYXRpZW50Um9sZT4KICAgICAgPGlkIGV4dGVuc2lvbj0iUEFUODAwMTAwIiByb290PSIy'
            'LjE2Ljg0MC4xLjExMzg4My40LjUyNi4xMi4xIi8+CiAgICAgIDxwYXRpZW50PgogICAgICAgIDxuYW1lPjxnaXZlbj7nv4Hlv5fosao8L2dpdmVuPjwvbmFtZT4KICAgICAgICA8YWRt'
            'aW5pc3RyYXRpdmVHZW5kZXJDb2RlIGNvZGU9Ik0iLz4KICAgICAgICA8YmlydGhUaW1lIHZhbHVlPSIxOTYzMTAzMCIvPgogICAgICA8L3BhdGllbnQ+CiAgICA8L3BhdGllbnRSb2xl'
            'PgogIDwvcmVjb3JkVGFyZ2V0PgogIDxjb21wb25lbnQ+CiAgICA8c3RydWN0dXJlZEJvZHk+CiAgICAgIDxjb21wb25lbnQ+CiAgICAgICAgPHNlY3Rpb24+CiAgICAgICAgICA8dGl0'
            'bGU+6Ki65paw5oiQ5p6cPC90aXRsZT4KICAgICAgICAgIDx0ZXh0PuWGoOeLgOWLleS+i+eyp+eJgOWnoOWMluaAp+W/g+iHn+eXhTwvdGV4dD4KICAgICAgICA8L3NlY3Rpb24+CiAg'
            'ICAgIDwvY29tcG9uZW50PgogICAgPC9zdHJ1Y3R1cmVkQm9keT4KICA8L2NvbXBvbmVudD4KPC9DbGluaWNhbERvY3VtZW50Pg=='
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
    """ Based on live/tw/tw-intersystems-healthshare.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HealthShare')
        msh.sending_facility = HD(hd_1='CYGH_HIE')
        msh.receiving_application = HD(hd_1='HIS-CYGH')
        msh.receiving_facility = HD(hd_1='CYGH_HOSP')
        msh.date_time_of_message = '20260303100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'MSG20260303100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260303100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT800200', cx_4='CYGH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='程', xpn_2='惠玲')
        pid.date_time_of_birth = '19800516'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='嘉義縣朴子市文化北路88號', xad_3='嘉義縣', xad_4='61341', xad_5='TW')
        pid.pid_13 = '05-3791234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'F725893046'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='PAT800200_OLD', cx_4='CYGH_HOSP', cx_5='MR')

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
    """ Based on live/tw/tw-intersystems-healthshare.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HealthShare')
        msh.sending_facility = HD(hd_1='CYGH_HIE')
        msh.receiving_application = HD(hd_1='HealthShare')
        msh.receiving_facility = HD(hd_1='NTUH_HIE')
        msh.date_time_of_message = '20260304090000'
        msh.message_type = MSG(msg_1='REF', msg_2='I12', msg_3='REF_I12')
        msh.message_control_id = 'MSG20260304090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build RF1 ..
        rf1 = RF1()
        rf1.referral_status = CWE(cwe_1='A')
        rf1.referral_priority = CWE(cwe_1='RO')
        rf1.referral_disposition = CWE(cwe_1='20260304090000')
        rf1.referral_category = CWE(cwe_1='20260318')
        rf1.originating_referral_identifier = EI(ei_1='心臟外科評估')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT800100', cx_4='CYGH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='賴', xpn_2='國華')
        pid.date_time_of_birth = '19631030'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='嘉義市西區民族路100號', xad_3='嘉義市', xad_4='60041', xad_5='TW')
        pid.pid_13 = '05-2765432'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'E614782935'

        # .. build PRD ..
        prd = PRD()
        prd.provider_role = CWE(cwe_1='RP')
        prd.provider_name = XPN(xpn_1='蕭志遠', xpn_2='D800100')
        prd.provider_address = XAD(xad_1='嘉義市西區民生北路151號', xad_3='嘉義市', xad_4='60045', xad_5='TW')
        prd.preferred_method_of_contact = CWE(cwe_1='CYGH_HOSP')

        # .. build PRD ..
        prd_2 = PRD()
        prd_2.provider_role = CWE(cwe_1='RT')
        prd_2.provider_name = XPN(xpn_1='周泰成', xpn_2='D_NTUH001')
        prd_2.provider_address = XAD(xad_1='台北市中正區中山南路7號', xad_3='台北市', xad_4='10002', xad_5='TW')
        prd_2.preferred_method_of_contact = CWE(cwe_1='NTUH_HOSP')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I25.10', cwe_2='冠狀動脈粥狀硬化性心臟病', cwe_3='I10')
        dg1.diagnosis_date_time = '20260304'

        # .. assemble the full message ..
        msg = REF_I12()
        msg.msh = msh
        msg.rf1 = rf1
        msg.pid = pid
        msg.extra_segments = [prd, prd_2, dg1]

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
    """ Based on live/tw/tw-intersystems-healthshare.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CATH-CYGH')
        msh.sending_facility = HD(hd_1='CYGH_CATH')
        msh.receiving_application = HD(hd_1='HealthShare')
        msh.receiving_facility = HD(hd_1='CYGH_HIE')
        msh.date_time_of_message = '20260305160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260305160000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT800100', cx_4='CYGH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='賴', xpn_2='國華')
        pid.date_time_of_birth = '19631030'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='嘉義市西區民族路100號', xad_3='嘉義市', xad_4='60041', xad_5='TW')
        pid.pid_13 = '05-2765432'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'E614782935'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='601', pl_3='01')
        pv1.pv1_7 = 'D800100^蕭志遠^^^^^CYGH_HOSP'
        pv1.visit_number = CX(cx_1='V800100001')

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
        orc.placer_order_number = EI(ei_1='ORD800100001')
        orc.orc_10 = 'D800100^蕭志遠'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800100001')
        obr.universal_service_identifier = CWE(cwe_1='49569-1', cwe_2='心導管檢查', cwe_3='LN')
        obr.observation_date_time = '20260305100000'
        obr.obr_16 = 'D800100^蕭志遠'
        obr.results_rpt_status_chng_date_time = '20260305155000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='49569-1', cwe_2='心導管檢查報告', cwe_3='LN')
        obx.obx_5 = '左前降支近端狹窄70%。左迴旋支中段狹窄50%。右冠狀動脈未見明顯狹窄。左心室射出分率55%。'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='49569-1', cwe_2='心導管檢查報告', cwe_3='LN')
        obx_2.obx_5 = '結論：左前降支近端顯著狹窄，建議經皮冠狀動脈介入治療或轉介心臟外科評估。'
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
    """ Based on live/tw/tw-intersystems-healthshare.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HealthShare')
        msh.sending_facility = HD(hd_1='CYGH_HIE')
        msh.receiving_application = HD(hd_1='HealthShare')
        msh.receiving_facility = HD(hd_1='NTUH_HIE')
        msh.date_time_of_message = '20260306090000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG20260306090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260306090000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT800100', cx_4='CYGH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='賴', xpn_2='國華')
        pid.date_time_of_birth = '19631030'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='嘉義市西區民族路100號', xad_3='嘉義市', xad_4='60041', xad_5='TW')
        pid.pid_13 = '05-2765432'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'E614782935'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='601', pl_3='01')
        pv1.pv1_7 = 'D800100^蕭志遠^^^^^CYGH_HOSP'
        pv1.visit_number = CX(cx_1='V800100001')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='REF', cwe_2='轉診摘要')
        txa.document_content_presentation = 'AP'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20260306083000')
        txa.assigned_document_authenticator = XCN(xcn_1='D800100', xcn_2='蕭志遠')
        txa.unique_document_number = EI(ei_1='DOC800100002')
        txa.unique_document_file_name = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='57133-1', cwe_2='轉診摘要CDA文件', cwe_3='LN')
        obx.obx_5 = (
            '^application^xml^Base64^'
            'PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIj4KICA8dGl0bGU+5b2w5YyW5Z+66Lid5pWZ6Yar6ZmiIOi9ieiouu+8iOS7i++8ieaRmOimgTwvdGl0bGU+CiAg'
            'PGVmZmVjdGl2ZVRpbWUgdmFsdWU9IjIwMjYwMzA2MDgzMDAwIi8+CiAgPHJlY29yZFRhcmdldD4KICAgIDxwYXRpZW50Um9sZT4KICAgICAgPGlkIGV4dGVuc2lvbj0iUEFUODAwMTAw'
            'Ii8+CiAgICAgIDxwYXRpZW50PgogICAgICAgIDxuYW1lPjxnaXZlbj7nv4Hlv5fosao8L2dpdmVuPjwvbmFtZT4KICAgICAgPC9wYXRpZW50PgogICAgPC9wYXRpZW50Um9sZT4KICA8'
            'L3JlY29yZFRhcmdldD4KICA8Y29tcG9uZW50PgogICAgPHN0cnVjdHVyZWRCb2R5PgogICAgICA8Y29tcG9uZW50PgogICAgICAgIDxzZWN0aW9uPgogICAgICAgICAgPHRpdGxlPui9'
            'ieiouu+8iOS7i++8ieWOn+WboOWPiuiou+aWt+e1kOaenDwvdGl0bGU+CiAgICAgICAgICA8dGV4dD7lhqDni4Dli5Xmib7nsoflgannoobljJbmgKflv4PpiL3nl4UuIOW3puWJjemZ'
            'jeaUr+i/keerr+eLueerqDcwJS4g5bu66K2w6Lyt5LuL5b+D6Ie85aSW56eR6KmV5Lyw5YaQ54uA5YuV6ISI57e15YiG5rWB6KGTLjwvdGV4dD4KICAgICAgICA8L3NlY3Rpb24+CiAg'
            'ICAgIDwvY29tcG9uZW50PgogICAgPC9zdHJ1Y3R1cmVkQm9keT4KICA8L2NvbXBvbmVudD4KPC9DbGluaWNhbERvY3VtZW50Pg=='
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
    """ Based on live/tw/tw-intersystems-healthshare.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-CYGH')
        msh.sending_facility = HD(hd_1='CYGH_HOSP')
        msh.receiving_application = HD(hd_1='HealthShare')
        msh.receiving_facility = HD(hd_1='CYGH_HIE')
        msh.date_time_of_message = '20260307090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20260307090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260307090000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT800200', cx_4='CYGH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='程', xpn_2='惠玲')
        pid.date_time_of_birth = '19800516'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='嘉義縣朴子市文化北路88號', xad_3='嘉義縣', xad_4='61341', xad_5='TW')
        pid.pid_13 = '05-3791234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'F725893046'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ENDO', pl_2='101', pl_3='01')
        pv1.pv1_7 = 'D800200^方筱雯^^^^^CYGH_HOSP'
        pv1.visit_number = CX(cx_1='V800200002')

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/tw/tw-intersystems-healthshare.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS-CYGH')
        msh.sending_facility = HD(hd_1='CYGH_LAB')
        msh.receiving_application = HD(hd_1='HealthShare')
        msh.receiving_facility = HD(hd_1='CYGH_HIE')
        msh.date_time_of_message = '20260310143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260310143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT800200', cx_4='CYGH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='程', xpn_2='惠玲')
        pid.date_time_of_birth = '19800516'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='嘉義縣朴子市文化北路88號', xad_3='嘉義縣', xad_4='61341', xad_5='TW')
        pid.pid_13 = '05-3791234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'F725893046'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ENDO', pl_2='101', pl_3='01')
        pv1.pv1_7 = 'D800200^方筱雯^^^^^CYGH_HOSP'
        pv1.visit_number = CX(cx_1='V800200002')

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
        orc.placer_order_number = EI(ei_1='ORD800200002')
        orc.orc_10 = 'D800200^方筱雯'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800200002')
        obr.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='糖化血色素追蹤', cwe_3='LN')
        obr.observation_date_time = '20260310100000'
        obr.obr_16 = 'D800200^方筱雯'
        obr.results_rpt_status_chng_date_time = '20260310140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='糖化血色素', cwe_3='LN')
        obx.obx_5 = '7.5'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '4.0-6.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2345-7', cwe_2='血糖(飯前)', cwe_3='LN')
        obx_2.obx_5 = '138'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '70-100'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='14749-6', cwe_2='血糖(飯後2小時)', cwe_3='LN')
        obx_3.obx_5 = '198'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '<140'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

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
    """ Based on live/tw/tw-intersystems-healthshare.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-CYGH')
        msh.sending_facility = HD(hd_1='CYGH_HOSP')
        msh.receiving_application = HD(hd_1='HealthShare')
        msh.receiving_facility = HD(hd_1='CYGH_HIE')
        msh.date_time_of_message = '20260308100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG20260308100000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260308100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT800100', cx_4='CYGH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='賴', xpn_2='國華')
        pid.date_time_of_birth = '19631030'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='嘉義市西區民族路100號', xad_3='嘉義市', xad_4='60041', xad_5='TW')
        pid.pid_13 = '05-2765432'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'E614782935'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='601', pl_3='01')
        pv1.pv1_7 = 'D800100^蕭志遠^^^^^CYGH_HOSP'
        pv1.visit_number = CX(cx_1='V800100001')
        pv1.discharged_to_location = DLD(dld_1='01')
        pv1.diet_type = CWE(cwe_1='CYGH_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260301080000')
        pv1.current_patient_balance = '20260308100000'

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/tw/tw-intersystems-healthshare.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ECHO-CYGH')
        msh.sending_facility = HD(hd_1='CYGH_ECHO')
        msh.receiving_application = HD(hd_1='HealthShare')
        msh.receiving_facility = HD(hd_1='CYGH_HIE')
        msh.date_time_of_message = '20260311150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260311150000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT800100', cx_4='CYGH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='賴', xpn_2='國華')
        pid.date_time_of_birth = '19631030'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='嘉義市西區民族路100號', xad_3='嘉義市', xad_4='60041', xad_5='TW')
        pid.pid_13 = '05-2765432'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'E614782935'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='101', pl_3='01')
        pv1.pv1_7 = 'D800100^蕭志遠^^^^^CYGH_HOSP'
        pv1.visit_number = CX(cx_1='V800100002')

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
        orc.placer_order_number = EI(ei_1='ORD800100002')
        orc.orc_10 = 'D800100^蕭志遠'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800100002')
        obr.universal_service_identifier = CWE(cwe_1='34552-0', cwe_2='心臟超音波', cwe_3='LN')
        obr.observation_date_time = '20260311100000'
        obr.obr_16 = 'D800100^蕭志遠'
        obr.results_rpt_status_chng_date_time = '20260311145000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='10230-1', cwe_2='左心室射出分率', cwe_3='LN')
        obx.obx_5 = '54'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '55-70'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='29430-3', cwe_2='左心室舒張末期內徑', cwe_3='LN')
        obx_2.obx_5 = '52'
        obx_2.units = CWE(cwe_1='mm')
        obx_2.reference_range = '35-56'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'FT'
        obx_3.observation_identifier = CWE(cwe_1='34552-0', cwe_2='心臟超音波報告', cwe_3='LN')
        obx_3.obx_5 = '左心室壁運動：前壁及前中隔運動減弱。瓣膜：二尖瓣輕度逆流。心包膜：無積液。'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'FT'
        obx_4.observation_identifier = CWE(cwe_1='34552-0', cwe_2='心臟超音波報告', cwe_3='LN')
        obx_4.obx_5 = '結論：左心室收縮功能輕度下降(LVEF 54%)，前壁及前中隔運動減弱，符合冠心病變化。'
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
    """ Based on live/tw/tw-intersystems-healthshare.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HealthShare')
        msh.sending_facility = HD(hd_1='CYGH_HIE')
        msh.receiving_application = HD(hd_1='EMR-Exchange')
        msh.receiving_facility = HD(hd_1='MOHW_HIE')
        msh.date_time_of_message = '20260312100000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG20260312100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260312100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT800200', cx_4='CYGH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='程', xpn_2='惠玲')
        pid.date_time_of_birth = '19800516'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='嘉義縣朴子市文化北路88號', xad_3='嘉義縣', xad_4='61341', xad_5='TW')
        pid.pid_13 = '05-3791234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'F725893046'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GEN_SURG', pl_2='401', pl_3='01')
        pv1.pv1_7 = 'D800200^方筱雯^^^^^CYGH_HOSP'
        pv1.visit_number = CX(cx_1='V800200003')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='OP', cwe_2='手術紀錄')
        txa.document_content_presentation = 'AP'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20260312090000')
        txa.assigned_document_authenticator = XCN(xcn_1='D800200', xcn_2='方筱雯')
        txa.unique_document_number = EI(ei_1='DOC800200001')
        txa.unique_document_file_name = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='28570-0', cwe_2='手術紀錄CDA文件', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQovQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAyNjAgPj4Kc3RyZWFtCkJUCi9GMSAxOCBUZgoxMDAgNzAwIFRkCijlvbDljJbln7rnnaPlrZnm'
            'lZnphqvpmaIg5omL6KGT57SA6YyEKSBUZC0xOCBUZgoxMDAgNjUwIFRkCijmgqPogIU6IOmrmOa3keiKrCBQQVQ4MDAyMDApIFRqCjEwMCA2MDAgVGQKKOaJi+ihleiAhTogRDgwMDIw'
            'MOW7luW7uuWuiykgVGoKMTAwIDU1MCBUZAoo5omL6KGT5ZCN56ixOiDohqnlm4rnmoflvI/ohqnlm4rliIfpmaTooZMpIFRqCjEwMCA1MDAgVGQKKOihlOW+jOiouuaWtzog6IaP5Zun'
            '57WQ55+z55eSKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwgL1R5cGUgL0ZvbnQgL1N1YnR5cGUgL1R5cGUxIC9CYXNlRm9udCAvSGVsdmV0aWNhID4+CmVuZG9iagp4'
            'cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAzMDYgMDAwMDAg'
            'biAKMDAwMDAwMDYxOCAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDYgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4cmVmCjcwNQolJUVPRgo='
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
    """ Based on live/tw/tw-intersystems-healthshare.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS-CYGH')
        msh.sending_facility = HD(hd_1='CYGH_LAB')
        msh.receiving_application = HD(hd_1='HealthShare')
        msh.receiving_facility = HD(hd_1='CYGH_HIE')
        msh.date_time_of_message = '20260313143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260313143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT800100', cx_4='CYGH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='賴', xpn_2='國華')
        pid.date_time_of_birth = '19631030'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='嘉義市西區民族路100號', xad_3='嘉義市', xad_4='60041', xad_5='TW')
        pid.pid_13 = '05-2765432'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'E614782935'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='101', pl_3='01')
        pv1.pv1_7 = 'D800100^蕭志遠^^^^^CYGH_HOSP'
        pv1.visit_number = CX(cx_1='V800100002')

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
        orc.placer_order_number = EI(ei_1='ORD800100003')
        orc.orc_10 = 'D800100^蕭志遠'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800100003')
        obr.universal_service_identifier = CWE(cwe_1='24331-1', cwe_2='血脂肪檢驗', cwe_3='LN')
        obr.observation_date_time = '20260313100000'
        obr.obr_16 = 'D800100^蕭志遠'
        obr.results_rpt_status_chng_date_time = '20260313140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2093-3', cwe_2='總膽固醇', cwe_3='LN')
        obx.obx_5 = '218'
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
        obx_2.observation_identifier = CWE(cwe_1='2571-8', cwe_2='三酸甘油脂', cwe_3='LN')
        obx_2.obx_5 = '165'
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
        obx_3.observation_identifier = CWE(cwe_1='2085-9', cwe_2='高密度脂蛋白膽固醇', cwe_3='LN')
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
        obx_4.observation_identifier = CWE(cwe_1='13457-7', cwe_2='低密度脂蛋白膽固醇', cwe_3='LN')
        obx_4.obx_5 = '147'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '<100'
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
    """ Based on live/tw/tw-intersystems-healthshare.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-CYGH')
        msh.sending_facility = HD(hd_1='CYGH_HOSP')
        msh.receiving_application = HD(hd_1='HealthShare')
        msh.receiving_facility = HD(hd_1='CYGH_HIE')
        msh.date_time_of_message = '20260314090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'MSG20260314090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260314090000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT800200', cx_4='CYGH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='程', xpn_2='惠玲')
        pid.date_time_of_birth = '19800516'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='嘉義縣朴子市文化北路88號', xad_3='嘉義縣', xad_4='61341', xad_5='TW')
        pid.pid_13 = '05-3791234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'F725893046'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GEN_SURG', pl_2='401', pl_3='01')
        pv1.pv1_7 = 'D800200^方筱雯^^^^^CYGH_HOSP'
        pv1.visit_number = CX(cx_1='V800200003')
        pv1.diet_type = CWE(cwe_1='CYGH_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260311080000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='GEN_WARD', cwe_2='301', cwe_3='05')

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/tw/tw-intersystems-healthshare.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS-CYGH')
        msh.sending_facility = HD(hd_1='CYGH_LAB')
        msh.receiving_application = HD(hd_1='HealthShare')
        msh.receiving_facility = HD(hd_1='CYGH_HIE')
        msh.date_time_of_message = '20260314143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260314143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT800200', cx_4='CYGH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='程', xpn_2='惠玲')
        pid.date_time_of_birth = '19800516'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='嘉義縣朴子市文化北路88號', xad_3='嘉義縣', xad_4='61341', xad_5='TW')
        pid.pid_13 = '05-3791234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'F725893046'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GEN_WARD', pl_2='301', pl_3='05')
        pv1.pv1_7 = 'D800200^方筱雯^^^^^CYGH_HOSP'
        pv1.visit_number = CX(cx_1='V800200003')

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
        orc.placer_order_number = EI(ei_1='ORD800200003')
        orc.orc_10 = 'D800200^方筱雯'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800200003')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='全血球計數', cwe_3='LN')
        obr.observation_date_time = '20260314100000'
        obr.obr_16 = 'D800200^方筱雯'
        obr.results_rpt_status_chng_date_time = '20260314140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='白血球', cwe_3='LN')
        obx.obx_5 = '9.8'
        obx.units = CWE(cwe_1='10', cwe_2='3/uL')
        obx.reference_range = '4.5-11.0'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='紅血球', cwe_3='LN')
        obx_2.obx_5 = '3.8'
        obx_2.units = CWE(cwe_1='10', cwe_2='6/uL')
        obx_2.reference_range = '4.0-5.5'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='血色素', cwe_3='LN')
        obx_3.obx_5 = '10.5'
        obx_3.units = CWE(cwe_1='g/dL')
        obx_3.reference_range = '12.0-16.0'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='787-2', cwe_2='平均紅血球容積', cwe_3='LN')
        obx_4.obx_5 = '82'
        obx_4.units = CWE(cwe_1='fL')
        obx_4.reference_range = '80-100'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='血小板', cwe_3='LN')
        obx_5.obx_5 = '285'
        obx_5.units = CWE(cwe_1='10', cwe_2='3/uL')
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
    """ Based on live/tw/tw-intersystems-healthshare.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-CYGH')
        msh.sending_facility = HD(hd_1='CYGH_HOSP')
        msh.receiving_application = HD(hd_1='HealthShare')
        msh.receiving_facility = HD(hd_1='CYGH_HIE')
        msh.date_time_of_message = '20260315090000'
        msh.message_type = MSG(msg_1='REF', msg_2='I12', msg_3='REF_I12')
        msh.message_control_id = 'MSG20260315090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build RF1 ..
        rf1 = RF1()
        rf1.referral_status = CWE(cwe_1='A')
        rf1.referral_priority = CWE(cwe_1='RI')
        rf1.referral_disposition = CWE(cwe_1='20260315090000')
        rf1.referral_category = CWE(cwe_1='20260415')
        rf1.originating_referral_identifier = EI(ei_1='復健科評估')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT800100', cx_4='CYGH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='賴', xpn_2='國華')
        pid.date_time_of_birth = '19631030'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='嘉義市西區民族路100號', xad_3='嘉義市', xad_4='60041', xad_5='TW')
        pid.pid_13 = '05-2765432'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'E614782935'

        # .. build PRD ..
        prd = PRD()
        prd.provider_role = CWE(cwe_1='RP')
        prd.provider_name = XPN(xpn_1='蕭志遠', xpn_2='D800100')
        prd.provider_address = XAD(xad_1='嘉義市西區民生北路151號', xad_3='嘉義市', xad_4='60045', xad_5='TW')
        prd.preferred_method_of_contact = CWE(cwe_1='CYGH_HOSP')

        # .. build PRD ..
        prd_2 = PRD()
        prd_2.provider_role = CWE(cwe_1='RT')
        prd_2.provider_name = XPN(xpn_1='趙維新', xpn_2='D800300')
        prd_2.provider_address = XAD(xad_1='嘉義市西區民生北路151號', xad_3='嘉義市', xad_4='60045', xad_5='TW')
        prd_2.preferred_method_of_contact = CWE(cwe_1='CYGH_HOSP')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I25.10', cwe_2='冠狀動脈粥狀硬化性心臟病', cwe_3='I10')
        dg1.diagnosis_date_time = '20260315'

        # .. assemble the full message ..
        msg = REF_I12()
        msg.msh = msh
        msg.rf1 = rf1
        msg.pid = pid
        msg.extra_segments = [prd, prd_2, dg1]

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
    """ Based on live/tw/tw-intersystems-healthshare.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-CYGH')
        msh.sending_facility = HD(hd_1='CYGH_HOSP')
        msh.receiving_application = HD(hd_1='HealthShare')
        msh.receiving_facility = HD(hd_1='CYGH_HIE')
        msh.date_time_of_message = '20260316100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG20260316100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260316100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT800200', cx_4='CYGH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='程', xpn_2='惠玲')
        pid.date_time_of_birth = '19800516'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='嘉義縣朴子市文化北路88號', xad_3='嘉義縣', xad_4='61341', xad_5='TW')
        pid.pid_13 = '05-3791234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'F725893046'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GEN_WARD', pl_2='301', pl_3='05')
        pv1.pv1_7 = 'D800200^方筱雯^^^^^CYGH_HOSP'
        pv1.visit_number = CX(cx_1='V800200003')
        pv1.discharged_to_location = DLD(dld_1='01')
        pv1.diet_type = CWE(cwe_1='CYGH_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260311080000')
        pv1.current_patient_balance = '20260316100000'

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/tw/tw-intersystems-healthshare.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS-CYGH')
        msh.sending_facility = HD(hd_1='CYGH_LAB')
        msh.receiving_application = HD(hd_1='HealthShare')
        msh.receiving_facility = HD(hd_1='CYGH_HIE')
        msh.date_time_of_message = '20260317143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260317143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT800200', cx_4='CYGH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='程', xpn_2='惠玲')
        pid.date_time_of_birth = '19800516'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='嘉義縣朴子市文化北路88號', xad_3='嘉義縣', xad_4='61341', xad_5='TW')
        pid.pid_13 = '05-3791234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'F725893046'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ENDO', pl_2='101', pl_3='01')
        pv1.pv1_7 = 'D800200^方筱雯^^^^^CYGH_HOSP'
        pv1.visit_number = CX(cx_1='V800200004')

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
        orc.placer_order_number = EI(ei_1='ORD800200004')
        orc.orc_10 = 'D800200^方筱雯'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD800200004')
        obr.universal_service_identifier = CWE(cwe_1='24348-5', cwe_2='甲狀腺功能檢驗', cwe_3='LN')
        obr.observation_date_time = '20260317100000'
        obr.obr_16 = 'D800200^方筱雯'
        obr.results_rpt_status_chng_date_time = '20260317140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='促甲狀腺激素', cwe_3='LN')
        obx.obx_5 = '2.8'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.4-4.0'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3026-2', cwe_2='游離甲狀腺素', cwe_3='LN')
        obx_2.obx_5 = '1.2'
        obx_2.units = CWE(cwe_1='ng/dL')
        obx_2.reference_range = '0.8-1.8'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3053-6', cwe_2='游離三碘甲狀腺原氨酸', cwe_3='LN')
        obx_3.obx_5 = '3.1'
        obx_3.units = CWE(cwe_1='pg/mL')
        obx_3.reference_range = '2.3-4.2'
        obx_3.observation_result_status = 'F'

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
    """ Based on live/tw/tw-intersystems-healthshare.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HealthShare')
        msh.sending_facility = HD(hd_1='CYGH_HIE')
        msh.receiving_application = HD(hd_1='EMR-Exchange')
        msh.receiving_facility = HD(hd_1='MOHW_HIE')
        msh.date_time_of_message = '20260318090000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG20260318090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260318090000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT800100', cx_4='CYGH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='賴', xpn_2='國華')
        pid.date_time_of_birth = '19631030'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='嘉義市西區民族路100號', xad_3='嘉義市', xad_4='60041', xad_5='TW')
        pid.pid_13 = '05-2765432'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'E614782935'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='101', pl_3='01')
        pv1.pv1_7 = 'D800100^蕭志遠^^^^^CYGH_HOSP'
        pv1.visit_number = CX(cx_1='V800100002')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='PN', cwe_2='門診病程記錄')
        txa.document_content_presentation = 'AP'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20260318083000')
        txa.assigned_document_authenticator = XCN(xcn_1='D800100', xcn_2='蕭志遠')
        txa.unique_document_number = EI(ei_1='DOC800100003')
        txa.unique_document_file_name = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='34117-2', cwe_2='門診病程記錄', cwe_3='LN')
        obx.obx_5 = 'S: 胸悶已改善，活動耐受性增加。O: BP 128/78, HR 72 regular。A: 冠狀動脈粥狀硬化性心臟病，穩定。P: 繼續目前藥物，三個月後回診追蹤。'
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
