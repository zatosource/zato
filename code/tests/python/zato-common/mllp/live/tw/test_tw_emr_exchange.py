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
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A03, ADT_A39, MDM_T02, ORU_R01, REF_I12
from zato.hl7v2.v2_9.segments import DG1, EVN, IN1, MRG, MSH, NK1, OBR, OBX, ORC, PID, PRD, PV1, RF1, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('tw', 'tw-emr-exchange.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/tw/tw-emr-exchange.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMR-Exchange')
        msh.sending_facility = HD(hd_1='MOHW_HIE')
        msh.receiving_application = HD(hd_1='HIS-TARGET')
        msh.receiving_facility = HD(hd_1='TARGET_HOSP')
        msh.date_time_of_message = '20260301100000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG20260301100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260301100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT900100', cx_4='MOHW_HIE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='范', xpn_2='宏毅')
        pid.date_time_of_birth = '19551208'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台南市安平區建平路55號', xad_3='台南市', xad_4='70846', xad_5='TW')
        pid.pid_13 = '06-2954321'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'G835671249'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='501', pl_3='01')
        pv1.pv1_7 = 'D900100^郭慧珊^^^^^TAINAN_MUNI'
        pv1.visit_number = CX(cx_1='V900100001')
        pv1.discharged_to_location = DLD(dld_1='01')
        pv1.diet_type = CWE(cwe_1='TAINAN_MUNI')
        pv1.prior_temporary_location = PL(pl_1='20260220080000')
        pv1.current_patient_balance = '20260228100000'

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='出院摘要')
        txa.document_content_presentation = 'AP'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20260228100000')
        txa.assigned_document_authenticator = XCN(xcn_1='D900100', xcn_2='郭慧珊')
        txa.txa_12 = 'DOC900100001^^^^TAINAN_MUNI'
        txa.unique_document_file_name = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='18842-5', cwe_2='出院摘要CDA文件', cwe_3='LN')
        obx.obx_5 = (
            '^application^xml^Base64^'
            'PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIj4KICA8dGl0bGU+6KGb55Sf56aP5Yip6YOo6Zu75a2Q55eF5q2355iy5Lqk5o+b5Lit5b+DIOWHuumZouaRmOim'
            'gTwvdGl0bGU+CiAgPGVmZmVjdGl2ZVRpbWUgdmFsdWU9IjIwMjYwMjI4MTAwMDAwIi8+CiAgPHJlY29yZFRhcmdldD4KICAgIDxwYXRpZW50Um9sZT4KICAgICAgPGlkIGV4dGVuc2lv'
            'bj0iUEFUOTAwMTAwIiByb290PSIyLjE2Ljg0MC4xLjExMzg4My40LjUyNi4xMi4xIi8+CiAgICAgIDxwYXRpZW50PgogICAgICAgIDxuYW1lPjxnaXZlbj7nvo3lnIvmhbY8L2dpdmVu'
            'PjwvbmFtZT4KICAgICAgICA8YWRtaW5pc3RyYXRpdmVHZW5kZXJDb2RlIGNvZGU9Ik0iLz4KICAgICAgICA8YmlydGhUaW1lIHZhbHVlPSIxOTU1MTIwOCIvPgogICAgICA8L3BhdGll'
            'bnQ+CiAgICA8L3BhdGllbnRSb2xlPgogIDwvcmVjb3JkVGFyZ2V0PgogIDxjb21wb25lbnQ+CiAgICA8c3RydWN0dXJlZEJvZHk+CiAgICAgIDxjb21wb25lbnQ+CiAgICAgICAgPHNl'
            'Y3Rpb24+CiAgICAgICAgICA8dGl0bGU+6Ki65pa35oiQ5p6cPC90aXRsZT4KICAgICAgICAgIDx0ZXh0PuWGoOeLgOWLleS+i+eyp+eJgOehoOWMluaAp+W/g+iHn+eXhSzlhqXlmKjo'
            'm4Hnmb3ooYDnrqHmlK/mnrblsKTnhafooYM8L3RleHQ+CiAgICAgICAgPC9zZWN0aW9uPgogICAgICA8L2NvbXBvbmVudD4KICAgIDwvc3RydWN0dXJlZEJvZHk+CiAgPC9jb21wb25l'
            'bnQ+CjwvQ2xpbmljYWxEb2N1bWVudD4='
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
    """ Based on live/tw/tw-emr-exchange.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMR-Exchange')
        msh.sending_facility = HD(hd_1='MOHW_HIE')
        msh.receiving_application = HD(hd_1='HIS-TARGET')
        msh.receiving_facility = HD(hd_1='TARGET_HOSP')
        msh.date_time_of_message = '20260302100000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG20260302100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260302100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT900200', cx_4='MOHW_HIE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='盧', xpn_2='雅萱')
        pid.date_time_of_birth = '19760422'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='桃園市中壢區中北路二段100號', xad_3='桃園市', xad_4='32070', xad_5='TW')
        pid.pid_13 = '03-4281234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'H946782350'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GYN', pl_2='301', pl_3='01')
        pv1.pv1_7 = 'D900200^韓志宏^^^^^TAOYUAN_GH'
        pv1.visit_number = CX(cx_1='V900200001')
        pv1.discharged_to_location = DLD(dld_1='01')
        pv1.diet_type = CWE(cwe_1='TAOYUAN_GH')
        pv1.prior_temporary_location = PL(pl_1='20260225080000')
        pv1.current_patient_balance = '20260301100000'

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='OP', cwe_2='手術紀錄')
        txa.document_content_presentation = 'AP'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20260227100000')
        txa.assigned_document_authenticator = XCN(xcn_1='D900200', xcn_2='韓志宏')
        txa.txa_12 = 'DOC900200001^^^^TAOYUAN_GH'
        txa.unique_document_file_name = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='28570-0', cwe_2='手術紀錄CDA文件', cwe_3='LN')
        obx.obx_5 = (
            '^application^xml^Base64^'
            'PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIj4KICA8dGl0bGU+6KGb55Sf56aP5Yip6YOo6Zu75a2Q55eF5q2355iy5Lqk5o+b5Lit5b+DIOaJi+ihlOe0gOmM'
            'hDwvdGl0bGU+CiAgPGVmZmVjdGl2ZVRpbWUgdmFsdWU9IjIwMjYwMjI3MTAwMDAwIi8+CiAgPHJlY29yZFRhcmdldD4KICAgIDxwYXRpZW50Um9sZT4KICAgICAgPGlkIGV4dGVuc2lv'
            'bj0iUEFUOTAwMjAwIi8+CiAgICAgIDxwYXRpZW50PgogICAgICAgIDxuYW1lPjxnaXZlbj7ps5jpm4Xpm688L2dpdmVuPjwvbmFtZT4KICAgICAgPC9wYXRpZW50PgogICAgPC9wYXRp'
            'ZW50Um9sZT4KICA8L3JlY29yZFRhcmdldD4KICA8Y29tcG9uZW50PgogICAgPHN0cnVjdHVyZWRCb2R5PgogICAgICA8Y29tcG9uZW50PgogICAgICAgIDxzZWN0aW9uPgogICAgICAg'
            'ICAgPHRpdGxlPuaJi+ihlOe0gOmMhDwvdGl0bGU+CiAgICAgICAgICA8dGV4dD7ohbnlm4rplqHlvI/ohbnlm4rliIfpmaTooYMs6IW556iu5byP5a2Q5a6u5YiH6Zmk6KGTPC90ZXh0'
            'PgogICAgICAgIDwvc2VjdGlvbj4KICAgICAgPC9jb21wb25lbnQ+CiAgICA8L3N0cnVjdHVyZWRCb2R5PgogIDwvY29tcG9uZW50Pgo8L0NsaW5pY2FsRG9jdW1lbnQ+'
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
    """ Based on live/tw/tw-emr-exchange.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMR-Exchange')
        msh.sending_facility = HD(hd_1='MOHW_HIE')
        msh.receiving_application = HD(hd_1='HIS-ALL')
        msh.receiving_facility = HD(hd_1='BROADCAST')
        msh.date_time_of_message = '20260303080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20260303080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260303080000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT900100', cx_4='MOHW_HIE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='范', xpn_2='宏毅')
        pid.date_time_of_birth = '19551208'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台南市安平區建平路55號', xad_3='台南市', xad_4='70846', xad_5='TW')
        pid.pid_13 = '06-2954321'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'G835671249'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IM', pl_2='601', pl_3='02')
        pv1.pv1_7 = 'D900100^郭慧珊^^^^^TAINAN_MUNI'
        pv1.visit_number = CX(cx_1='V900100002')
        pv1.diet_type = CWE(cwe_1='TAINAN_MUNI')
        pv1.prior_temporary_location = PL(pl_1='20260303080000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='NHI')
        in1.insurance_company_id = CX(cx_1='NHI_TW')
        in1.insurance_company_name = XON(xon_1='全民健康保險')
        in1.insureds_address = XAD(xad_1='G835671249')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I50.9', cwe_2='心臟衰竭,未明示者', cwe_3='I10')
        dg1.diagnosis_date_time = '20260303'

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
    """ Based on live/tw/tw-emr-exchange.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMR-Exchange')
        msh.sending_facility = HD(hd_1='MOHW_HIE')
        msh.receiving_application = HD(hd_1='HIS-TARGET')
        msh.receiving_facility = HD(hd_1='TARGET_HOSP')
        msh.date_time_of_message = '20260304100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260304100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT900100', cx_4='MOHW_HIE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='范', xpn_2='宏毅')
        pid.date_time_of_birth = '19551208'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台南市安平區建平路55號', xad_3='台南市', xad_4='70846', xad_5='TW')
        pid.pid_13 = '06-2954321'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'G835671249'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IM', pl_2='601', pl_3='02')
        pv1.pv1_7 = 'D900100^郭慧珊^^^^^TAINAN_MUNI'
        pv1.visit_number = CX(cx_1='V900100002')

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
        orc.placer_order_number = EI(ei_1='ORD900100001')
        orc.orc_10 = 'D900100^郭慧珊'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD900100001')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='基本代謝綜合檢驗', cwe_3='LN')
        obr.observation_date_time = '20260304080000'
        obr.obr_16 = 'D900100^郭慧珊'
        obr.results_rpt_status_chng_date_time = '20260304140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='33762-6', cwe_2='BNP', cwe_3='LN')
        obx.obx_5 = '1250'
        obx.units = CWE(cwe_1='pg/mL')
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
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='肌酸酐', cwe_3='LN')
        obx_2.obx_5 = '1.8'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '0.6-1.2'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='尿素氮', cwe_3='LN')
        obx_3.obx_5 = '32'
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
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='鈉', cwe_3='LN')
        obx_4.obx_5 = '132'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '136-145'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='鉀', cwe_3='LN')
        obx_5.obx_5 = '5.3'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '3.5-5.1'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='718-7', cwe_2='血色素', cwe_3='LN')
        obx_6.obx_5 = '10.2'
        obx_6.units = CWE(cwe_1='g/dL')
        obx_6.reference_range = '13.5-17.5'
        obx_6.interpretation_codes = CWE(cwe_1='L')
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
    """ Based on live/tw/tw-emr-exchange.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMR-Exchange')
        msh.sending_facility = HD(hd_1='MOHW_HIE')
        msh.receiving_application = HD(hd_1='HIS-ALL')
        msh.receiving_facility = HD(hd_1='BROADCAST')
        msh.date_time_of_message = '20260305100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'MSG20260305100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260305100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT900200', cx_4='MOHW_HIE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='盧', xpn_2='雅萱')
        pid.date_time_of_birth = '19760422'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='桃園市中壢區中北路二段100號', xad_3='桃園市', xad_4='32070', xad_5='TW')
        pid.pid_13 = '03-4281234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'H946782350'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='PAT900200_DUP', cx_4='TAOYUAN_GH', cx_5='MR')

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
    """ Based on live/tw/tw-emr-exchange.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMR-Exchange')
        msh.sending_facility = HD(hd_1='MOHW_HIE')
        msh.receiving_application = HD(hd_1='HIS-TARGET')
        msh.receiving_facility = HD(hd_1='TARGET_HOSP')
        msh.date_time_of_message = '20260306100000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG20260306100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260306100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT900100', cx_4='MOHW_HIE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='范', xpn_2='宏毅')
        pid.date_time_of_birth = '19551208'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台南市安平區建平路55號', xad_3='台南市', xad_4='70846', xad_5='TW')
        pid.pid_13 = '06-2954321'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'G835671249'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IM', pl_2='601', pl_3='02')
        pv1.pv1_7 = 'D900100^郭慧珊^^^^^TAINAN_MUNI'
        pv1.visit_number = CX(cx_1='V900100002')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='RAD', cwe_2='影像報告')
        txa.document_content_presentation = 'AP'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20260305160000')
        txa.assigned_document_authenticator = XCN(xcn_1='D900100', xcn_2='郭慧珊')
        txa.txa_12 = 'DOC900100002^^^^TAINAN_MUNI'
        txa.unique_document_file_name = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='36643-5', cwe_2='胸部X光報告', cwe_3='LN')
        obx.obx_5 = '檢查所見：心臟擴大(CTR 0.62)。雙側肺野可見血管紋路增粗及柯里氏B線。右側少量肋膜積液。'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='36643-5', cwe_2='胸部X光報告', cwe_3='LN')
        obx_2.obx_5 = '結論：心臟擴大併肺鬱血及右側肋膜積液，符合心臟衰竭表現。'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = MdmT02Observation()
        observation_2.obx = obx_2

        # .. assemble the full message ..
        msg = MDM_T02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.txa = txa
        msg.observation = [observation, observation_2]

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
    """ Based on live/tw/tw-emr-exchange.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMR-Exchange')
        msh.sending_facility = HD(hd_1='MOHW_HIE')
        msh.receiving_application = HD(hd_1='HIS-CMUH')
        msh.receiving_facility = HD(hd_1='CMUH_HOSP')
        msh.date_time_of_message = '20260307090000'
        msh.message_type = MSG(msg_1='REF', msg_2='I12', msg_3='REF_I12')
        msh.message_control_id = 'MSG20260307090000001'
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
        rf1.referral_disposition = CWE(cwe_1='20260307090000')
        rf1.referral_category = CWE(cwe_1='20260321')
        rf1.originating_referral_identifier = EI(ei_1='心臟外科評估 - 冠狀動脈繞道手術')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT900100', cx_4='MOHW_HIE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='范', xpn_2='宏毅')
        pid.date_time_of_birth = '19551208'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台南市安平區建平路55號', xad_3='台南市', xad_4='70846', xad_5='TW')
        pid.pid_13 = '06-2954321'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'G835671249'

        # .. build PRD ..
        prd = PRD()
        prd.provider_role = CWE(cwe_1='RP')
        prd.provider_name = XPN(xpn_1='郭慧珊', xpn_2='D900100')
        prd.provider_address = XAD(xad_1='台南市東區崇德路862號', xad_3='台南市', xad_4='70151', xad_5='TW')
        prd.preferred_method_of_contact = CWE(cwe_1='TAINAN_MUNI')

        # .. build PRD ..
        prd_2 = PRD()
        prd_2.provider_role = CWE(cwe_1='RT')
        prd_2.provider_name = XPN(xpn_1='朱偉倫', xpn_2='D_CMUH100')
        prd_2.provider_address = XAD(xad_1='台中市北區學士路91號', xad_3='台中市', xad_4='40402', xad_5='TW')
        prd_2.preferred_method_of_contact = CWE(cwe_1='CMUH_HOSP')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I25.10', cwe_2='冠狀動脈粥狀硬化性心臟病', cwe_3='I10')
        dg1.diagnosis_date_time = '20260307'

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.dg1_2 = 'ICD10'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='I50.9', cwe_2='心臟衰竭,未明示者', cwe_3='I10')
        dg1_2.diagnosis_date_time = '20260307'

        # .. assemble the full message ..
        msg = REF_I12()
        msg.msh = msh
        msg.rf1 = rf1
        msg.pid = pid
        msg.extra_segments = [prd, prd_2, dg1, dg1_2]

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
    """ Based on live/tw/tw-emr-exchange.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMR-Exchange')
        msh.sending_facility = HD(hd_1='MOHW_HIE')
        msh.receiving_application = HD(hd_1='HIS-CMUH')
        msh.receiving_facility = HD(hd_1='CMUH_HOSP')
        msh.date_time_of_message = '20260307093000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG20260307093000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260307093000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT900100', cx_4='MOHW_HIE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='范', xpn_2='宏毅')
        pid.date_time_of_birth = '19551208'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台南市安平區建平路55號', xad_3='台南市', xad_4='70846', xad_5='TW')
        pid.pid_13 = '06-2954321'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'G835671249'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IM', pl_2='601', pl_3='02')
        pv1.pv1_7 = 'D900100^郭慧珊^^^^^TAINAN_MUNI'
        pv1.visit_number = CX(cx_1='V900100002')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='REF', cwe_2='轉診摘要')
        txa.document_content_presentation = 'AP'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20260307090000')
        txa.assigned_document_authenticator = XCN(xcn_1='D900100', xcn_2='郭慧珊')
        txa.txa_12 = 'DOC900100003^^^^TAINAN_MUNI'
        txa.unique_document_file_name = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='57133-1', cwe_2='轉診摘要CDA文件', cwe_3='LN')
        obx.obx_5 = (
            '^application^xml^Base64^'
            'PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIj4KICA8dGl0bGU+6KGb55Sf56aP5Yip6YOoIOi9ieiouu+8iOS7i++8ieaRmOimgTwvdGl0bGU+CiAgPGVmZmVj'
            'dGl2ZVRpbWUgdmFsdWU9IjIwMjYwMzA3MDkwMDAwIi8+CiAgPHJlY29yZFRhcmdldD4KICAgIDxwYXRpZW50Um9sZT4KICAgICAgPGlkIGV4dGVuc2lvbj0iUEFUOTAwMTAwIi8+CiAg'
            'ICAgIDxwYXRpZW50PgogICAgICAgIDxuYW1lPjxnaXZlbj7nvo3lnIvmhbY8L2dpdmVuPjwvbmFtZT4KICAgICAgPC9wYXRpZW50PgogICAgPC9wYXRpZW50Um9sZT4KICA8L3JlY29y'
            'ZFRhcmdldD4KICA8Y29tcG9uZW50PgogICAgPHN0cnVjdHVyZWRCb2R5PgogICAgICA8Y29tcG9uZW50PgogICAgICAgIDxzZWN0aW9uPgogICAgICAgICAgPHRpdGxlPui9ieiouu+8'
            'iOS7i++8ieWOn+WboDwvdGl0bGU+CiAgICAgICAgICA8dGV4dD7lhqDni4Dli5Xmib7nsoflgannoobljJbmgKflv4PpiL3nl4UsIOW/g+iHn+ihluerrywg5bu66K2w5b+D6Ie95aSW'
            '56eR6KmV5LywQ0FCRzwvdGV4dD4KICAgICAgICA8L3NlY3Rpb24+CiAgICAgIDwvY29tcG9uZW50PgogICAgPC9zdHJ1Y3R1cmVkQm9keT4KICA8L2NvbXBvbmVudD4KPC9DbGluaWNh'
            'bERvY3VtZW50Pg=='
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
    """ Based on live/tw/tw-emr-exchange.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMR-Exchange')
        msh.sending_facility = HD(hd_1='MOHW_HIE')
        msh.receiving_application = HD(hd_1='HIS-ALL')
        msh.receiving_facility = HD(hd_1='BROADCAST')
        msh.date_time_of_message = '20260308100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG20260308100000001'
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
        pid.patient_identifier_list = CX(cx_1='PAT900100', cx_4='MOHW_HIE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='范', xpn_2='宏毅')
        pid.date_time_of_birth = '19551208'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台南市安平區建平路55號', xad_3='台南市', xad_4='70846', xad_5='TW')
        pid.pid_13 = '06-2954321'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'G835671249'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='IM', pl_2='601', pl_3='02')
        pv1.pv1_7 = 'D900100^郭慧珊^^^^^TAINAN_MUNI'
        pv1.visit_number = CX(cx_1='V900100002')
        pv1.discharged_to_location = DLD(dld_1='01')
        pv1.diet_type = CWE(cwe_1='TAINAN_MUNI')
        pv1.prior_temporary_location = PL(pl_1='20260303080000')
        pv1.current_patient_balance = '20260308100000'

        # .. assemble the full message ..
        msg = ADT_A03()
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
    """ Based on live/tw/tw-emr-exchange.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMR-Exchange')
        msh.sending_facility = HD(hd_1='MOHW_HIE')
        msh.receiving_application = HD(hd_1='HIS-TARGET')
        msh.receiving_facility = HD(hd_1='TARGET_HOSP')
        msh.date_time_of_message = '20260309100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260309100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT900100', cx_4='MOHW_HIE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='范', xpn_2='宏毅')
        pid.date_time_of_birth = '19551208'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台南市安平區建平路55號', xad_3='台南市', xad_4='70846', xad_5='TW')
        pid.pid_13 = '06-2954321'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'G835671249'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='101', pl_3='01')
        pv1.pv1_7 = 'D900100^郭慧珊^^^^^TAINAN_MUNI'
        pv1.visit_number = CX(cx_1='V900100003')

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
        orc.placer_order_number = EI(ei_1='ORD900100002')
        orc.orc_10 = 'D900100^郭慧珊'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD900100002')
        obr.universal_service_identifier = CWE(cwe_1='57833-6', cwe_2='用藥摘要', cwe_3='LN')
        obr.observation_date_time = '20260309090000'
        obr.obr_16 = 'D900100^郭慧珊'
        obr.results_rpt_status_chng_date_time = '20260309100000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='57833-6', cwe_2='用藥摘要', cwe_3='LN')
        obx.obx_5 = (
            '1. Furosemide 40mg QD PO~2. Spironolactone 25mg QD PO~3. Carvedilol 12.5mg BID PO~4. Enalapril 10mg BID PO~5. Aspirin 100mg QD PO~6. Atorvas'
            'tatin 20mg QD PO'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.common_order = common_order
        order_observation.obr = obr
        order_observation.observation = observation

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
    """ Based on live/tw/tw-emr-exchange.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMR-Exchange')
        msh.sending_facility = HD(hd_1='MOHW_HIE')
        msh.receiving_application = HD(hd_1='HIS-TARGET')
        msh.receiving_facility = HD(hd_1='TARGET_HOSP')
        msh.date_time_of_message = '20260310100000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG20260310100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260310100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT900200', cx_4='MOHW_HIE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='盧', xpn_2='雅萱')
        pid.date_time_of_birth = '19760422'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='桃園市中壢區中北路二段100號', xad_3='桃園市', xad_4='32070', xad_5='TW')
        pid.pid_13 = '03-4281234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'H946782350'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GYN', pl_2='101', pl_3='01')
        pv1.pv1_7 = 'D900200^韓志宏^^^^^TAOYUAN_GH'
        pv1.visit_number = CX(cx_1='V900200002')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='LAB', cwe_2='檢驗報告')
        txa.document_content_presentation = 'AP'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20260310083000')
        txa.assigned_document_authenticator = XCN(xcn_1='D900200', xcn_2='韓志宏')
        txa.txa_12 = 'DOC900200002^^^^TAOYUAN_GH'
        txa.unique_document_file_name = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='26464-8', cwe_2='全血球計數報告', cwe_3='LN')
        obx.obx_5 = 'WBC: 6.5 10^3/uL, RBC: 4.2 10^6/uL, Hgb: 12.8 g/dL, Plt: 245 10^3/uL'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='24323-8', cwe_2='生化報告', cwe_3='LN')
        obx_2.obx_5 = 'BUN: 15 mg/dL, Cr: 0.7 mg/dL, GOT: 22 U/L, GPT: 18 U/L'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = MdmT02Observation()
        observation_2.obx = obx_2

        # .. assemble the full message ..
        msg = MDM_T02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.txa = txa
        msg.observation = [observation, observation_2]

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
    """ Based on live/tw/tw-emr-exchange.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMR-Exchange')
        msh.sending_facility = HD(hd_1='MOHW_HIE')
        msh.receiving_application = HD(hd_1='HIS-ALL')
        msh.receiving_facility = HD(hd_1='BROADCAST')
        msh.date_time_of_message = '20260311090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20260311090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260311090000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT900200', cx_4='MOHW_HIE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='盧', xpn_2='雅萱')
        pid.date_time_of_birth = '19760422'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='桃園市中壢區中北路二段88號', xad_3='桃園市', xad_4='32070', xad_5='TW')
        pid.pid_13 = '03-4289876'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'H946782350'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid

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
    """ Based on live/tw/tw-emr-exchange.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMR-Exchange')
        msh.sending_facility = HD(hd_1='MOHW_HIE')
        msh.receiving_application = HD(hd_1='HIS-TARGET')
        msh.receiving_facility = HD(hd_1='TARGET_HOSP')
        msh.date_time_of_message = '20260312100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260312100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT900200', cx_4='MOHW_HIE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='盧', xpn_2='雅萱')
        pid.date_time_of_birth = '19760422'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='桃園市中壢區中北路二段88號', xad_3='桃園市', xad_4='32070', xad_5='TW')
        pid.pid_13 = '03-4289876'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'H946782350'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GYN', pl_2='101', pl_3='01')
        pv1.pv1_7 = 'D900200^韓志宏^^^^^TAOYUAN_GH'
        pv1.visit_number = CX(cx_1='V900200002')

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
        orc.placer_order_number = EI(ei_1='ORD900200001')
        orc.orc_10 = 'D900200^韓志宏'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD900200001')
        obr.universal_service_identifier = CWE(cwe_1='22637-3', cwe_2='病理報告', cwe_3='LN')
        obr.observation_date_time = '20260228100000'
        obr.obr_16 = 'D900200^韓志宏'
        obr.results_rpt_status_chng_date_time = '20260310090000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='22637-3', cwe_2='病理報告', cwe_3='LN')
        obx.obx_5 = '標本：子宮及雙側附件。肉眼所見：子宮重量380克，子宮體可見一直徑5.5公分肌壁間平滑肌瘤。'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='22637-3', cwe_2='病理報告', cwe_3='LN')
        obx_2.obx_5 = '鏡檢所見：平滑肌瘤，無異型性。子宮內膜呈增殖期變化。雙側卵巢及輸卵管未見異常。'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'FT'
        obx_3.observation_identifier = CWE(cwe_1='22637-3', cwe_2='病理報告', cwe_3='LN')
        obx_3.obx_5 = '病理診斷：子宮平滑肌瘤（良性），子宮內膜增殖期。'
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
    """ Based on live/tw/tw-emr-exchange.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMR-Exchange')
        msh.sending_facility = HD(hd_1='MOHW_HIE')
        msh.receiving_application = HD(hd_1='HIS-TARGET')
        msh.receiving_facility = HD(hd_1='TARGET_HOSP')
        msh.date_time_of_message = '20260313100000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG20260313100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260313100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT900100', cx_4='MOHW_HIE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='范', xpn_2='宏毅')
        pid.date_time_of_birth = '19551208'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台南市安平區建平路55號', xad_3='台南市', xad_4='70846', xad_5='TW')
        pid.pid_13 = '06-2954321'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'G835671249'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ER', pl_2='001', pl_3='01')
        pv1.pv1_7 = 'D900100^郭慧珊^^^^^TAINAN_MUNI'
        pv1.visit_number = CX(cx_1='V900100004')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='ER', cwe_2='急診病歷摘要')
        txa.document_content_presentation = 'AP'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20260313083000')
        txa.assigned_document_authenticator = XCN(xcn_1='D900100', xcn_2='郭慧珊')
        txa.txa_12 = 'DOC900100004^^^^TAINAN_MUNI'
        txa.unique_document_file_name = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='34878-9', cwe_2='急診病歷摘要', cwe_3='LN')
        obx.obx_5 = '主訴：呼吸困難加劇兩天。理學檢查：BP 160/95, HR 110, RR 28, SpO2 88%。雙側肺底濕囉音。雙下肢水腫(+++)。'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='34878-9', cwe_2='急診病歷摘要', cwe_3='LN')
        obx_2.obx_5 = '診斷：急性心臟衰竭惡化。處置：Furosemide 40mg IV stat, O2 mask 10L/min。收治加護病房。'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = MdmT02Observation()
        observation_2.obx = obx_2

        # .. assemble the full message ..
        msg = MDM_T02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.txa = txa
        msg.observation = [observation, observation_2]

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
    """ Based on live/tw/tw-emr-exchange.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMR-Exchange')
        msh.sending_facility = HD(hd_1='MOHW_HIE')
        msh.receiving_application = HD(hd_1='HIS-ALL')
        msh.receiving_facility = HD(hd_1='BROADCAST')
        msh.date_time_of_message = '20260313120000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20260313120000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260313120000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT900100', cx_4='MOHW_HIE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='范', xpn_2='宏毅')
        pid.date_time_of_birth = '19551208'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台南市安平區建平路55號', xad_3='台南市', xad_4='70846', xad_5='TW')
        pid.pid_13 = '06-2954321'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'G835671249'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='范張秋月')
        nk1.relationship = CWE(cwe_1='SPO')
        nk1.address = XAD(xad_1='台南市安平區建平路55號', xad_3='台南市', xad_4='70846', xad_5='TW')
        nk1.nk1_5 = '06-2954321'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='101', pl_3='01')
        pv1.pv1_7 = 'D900100^郭慧珊^^^^^TAINAN_MUNI'
        pv1.visit_number = CX(cx_1='V900100004')
        pv1.diet_type = CWE(cwe_1='TAINAN_MUNI')
        pv1.prior_temporary_location = PL(pl_1='20260313120000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='NHI')
        in1.insurance_company_id = CX(cx_1='NHI_TW')
        in1.insurance_company_name = XON(xon_1='全民健康保險')
        in1.insureds_address = XAD(xad_1='G835671249')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I50.21', cwe_2='急性收縮性心臟衰竭', cwe_3='I10')
        dg1.diagnosis_date_time = '20260313'

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
    """ Based on live/tw/tw-emr-exchange.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMR-Exchange')
        msh.sending_facility = HD(hd_1='MOHW_HIE')
        msh.receiving_application = HD(hd_1='HIS-TARGET')
        msh.receiving_facility = HD(hd_1='TARGET_HOSP')
        msh.date_time_of_message = '20260314100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260314100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT900100', cx_4='MOHW_HIE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='范', xpn_2='宏毅')
        pid.date_time_of_birth = '19551208'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台南市安平區建平路55號', xad_3='台南市', xad_4='70846', xad_5='TW')
        pid.pid_13 = '06-2954321'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'G835671249'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='101', pl_3='01')
        pv1.pv1_7 = 'D900100^郭慧珊^^^^^TAINAN_MUNI'
        pv1.visit_number = CX(cx_1='V900100004')

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
        orc.placer_order_number = EI(ei_1='ORD900100003')
        orc.orc_10 = 'D900100^郭慧珊'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD900100003')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='基本代謝綜合檢驗', cwe_3='LN')
        obr.observation_date_time = '20260314060000'
        obr.obr_16 = 'D900100^郭慧珊'
        obr.results_rpt_status_chng_date_time = '20260314080000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='33762-6', cwe_2='BNP', cwe_3='LN')
        obx.obx_5 = '2580'
        obx.units = CWE(cwe_1='pg/mL')
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
        obx_2.observation_identifier = CWE(cwe_1='49563-0', cwe_2='心肌旋轉蛋白I', cwe_3='LN')
        obx_2.obx_5 = '0.08'
        obx_2.units = CWE(cwe_1='ng/mL')
        obx_2.reference_range = '<0.04'
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
        obx_3.obx_5 = '2.1'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '0.6-1.2'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2823-3', cwe_2='鉀', cwe_3='LN')
        obx_4.obx_5 = '5.6'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '3.5-5.1'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2345-7', cwe_2='血糖', cwe_3='LN')
        obx_5.obx_5 = '165'
        obx_5.units = CWE(cwe_1='mg/dL')
        obx_5.reference_range = '70-100'
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
    """ Based on live/tw/tw-emr-exchange.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMR-Exchange')
        msh.sending_facility = HD(hd_1='MOHW_HIE')
        msh.receiving_application = HD(hd_1='HIS-TARGET')
        msh.receiving_facility = HD(hd_1='TARGET_HOSP')
        msh.date_time_of_message = '20260315090000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG20260315090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260315090000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT900100', cx_4='MOHW_HIE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='范', xpn_2='宏毅')
        pid.date_time_of_birth = '19551208'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台南市安平區建平路55號', xad_3='台南市', xad_4='70846', xad_5='TW')
        pid.pid_13 = '06-2954321'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'G835671249'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='101', pl_3='01')
        pv1.pv1_7 = 'D900100^郭慧珊^^^^^TAINAN_MUNI'
        pv1.visit_number = CX(cx_1='V900100004')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='AL', cwe_2='過敏紀錄')
        txa.document_content_presentation = 'AP'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20260315083000')
        txa.assigned_document_authenticator = XCN(xcn_1='D900100', xcn_2='郭慧珊')
        txa.txa_12 = 'DOC900100005^^^^TAINAN_MUNI'
        txa.unique_document_file_name = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='48765-2', cwe_2='過敏紀錄', cwe_3='LN')
        obx.obx_5 = '1. Penicillin類 - 皮膚紅疹、搔癢 (中度)~2. Aspirin - 氣喘發作 (重度)~3. 碘顯影劑 - 蕁麻疹 (輕度)'
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
    """ Based on live/tw/tw-emr-exchange.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMR-Exchange')
        msh.sending_facility = HD(hd_1='MOHW_HIE')
        msh.receiving_application = HD(hd_1='HIS-TARGET')
        msh.receiving_facility = HD(hd_1='TARGET_HOSP')
        msh.date_time_of_message = '20260318100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260318100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT900100', cx_4='MOHW_HIE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='范', xpn_2='宏毅')
        pid.date_time_of_birth = '19551208'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台南市安平區建平路55號', xad_3='台南市', xad_4='70846', xad_5='TW')
        pid.pid_13 = '06-2954321'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'G835671249'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='601', pl_3='01')
        pv1.pv1_7 = 'D900100^郭慧珊^^^^^TAINAN_MUNI'
        pv1.visit_number = CX(cx_1='V900100004')

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
        orc.placer_order_number = EI(ei_1='ORD900100004')
        orc.orc_10 = 'D900100^郭慧珊'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD900100004')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='出院前檢驗', cwe_3='LN')
        obr.observation_date_time = '20260317060000'
        obr.obr_16 = 'D900100^郭慧珊'
        obr.results_rpt_status_chng_date_time = '20260317140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='33762-6', cwe_2='BNP', cwe_3='LN')
        obx.obx_5 = '450'
        obx.units = CWE(cwe_1='pg/mL')
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
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='肌酸酐', cwe_3='LN')
        obx_2.obx_5 = '1.5'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '0.6-1.2'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2823-3', cwe_2='鉀', cwe_3='LN')
        obx_3.obx_5 = '4.5'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '3.5-5.1'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='鈉', cwe_3='LN')
        obx_4.obx_5 = '138'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '136-145'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='718-7', cwe_2='血色素', cwe_3='LN')
        obx_5.obx_5 = '11.5'
        obx_5.units = CWE(cwe_1='g/dL')
        obx_5.reference_range = '13.5-17.5'
        obx_5.interpretation_codes = CWE(cwe_1='L')
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
    """ Based on live/tw/tw-emr-exchange.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMR-Exchange')
        msh.sending_facility = HD(hd_1='MOHW_HIE')
        msh.receiving_application = HD(hd_1='HIS-ALL')
        msh.receiving_facility = HD(hd_1='BROADCAST')
        msh.date_time_of_message = '20260320100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG20260320100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260320100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT900100', cx_4='MOHW_HIE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='范', xpn_2='宏毅')
        pid.date_time_of_birth = '19551208'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台南市安平區建平路55號', xad_3='台南市', xad_4='70846', xad_5='TW')
        pid.pid_13 = '06-2954321'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'G835671249'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='601', pl_3='01')
        pv1.pv1_7 = 'D900100^郭慧珊^^^^^TAINAN_MUNI'
        pv1.visit_number = CX(cx_1='V900100004')
        pv1.discharged_to_location = DLD(dld_1='01')
        pv1.diet_type = CWE(cwe_1='TAINAN_MUNI')
        pv1.prior_temporary_location = PL(pl_1='20260313120000')
        pv1.current_patient_balance = '20260320100000'

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/tw/tw-emr-exchange.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMR-Exchange')
        msh.sending_facility = HD(hd_1='MOHW_HIE')
        msh.receiving_application = HD(hd_1='HIS-TARGET')
        msh.receiving_facility = HD(hd_1='TARGET_HOSP')
        msh.date_time_of_message = '20260320110000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG20260320110000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260320110000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT900100', cx_4='MOHW_HIE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='范', xpn_2='宏毅')
        pid.date_time_of_birth = '19551208'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='台南市安平區建平路55號', xad_3='台南市', xad_4='70846', xad_5='TW')
        pid.pid_13 = '06-2954321'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'G835671249'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='101', pl_3='01')
        pv1.pv1_7 = 'D900100^郭慧珊^^^^^TAINAN_MUNI'
        pv1.visit_number = CX(cx_1='V900100005')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='CP', cwe_2='出院照護計畫')
        txa.document_content_presentation = 'AP'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20260320090000')
        txa.assigned_document_authenticator = XCN(xcn_1='D900100', xcn_2='郭慧珊')
        txa.txa_12 = 'DOC900100006^^^^TAINAN_MUNI'
        txa.unique_document_file_name = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='18776-5', cwe_2='出院照護計畫', cwe_3='LN')
        obx.obx_5 = '照護計畫：1.每日體重監測 2.限鈉飲食(<2g/day) 3.限水(<1500ml/day) 4.心臟復健運動處方 5.門診追蹤：心臟內科(2週)及心臟外科評估'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='18776-5', cwe_2='出院照護計畫', cwe_3='LN')
        obx_2.obx_5 = (
            '用藥提醒：Furosemide 40mg QD, Spironolactone 25mg QD, Carvedilol 12.5mg BID, Enalapril 10mg BID, Atorvastatin 20mg QD。注意事項：Aspirin已停用('
            '過敏史)。'
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = MdmT02Observation()
        observation_2.obx = obx_2

        # .. assemble the full message ..
        msg = MDM_T02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.txa = txa
        msg.observation = [observation, observation_2]

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
