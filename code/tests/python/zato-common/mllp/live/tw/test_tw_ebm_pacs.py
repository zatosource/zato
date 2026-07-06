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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, DLD, EI, EIP, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, OrmO01Insurance, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, \
    OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12LocationResource, SiuS12Patient, \
    SiuS12PersonnelResource, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A03, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, DG1, EVN, IN1, MSH, NK1, OBR, OBX, ORC, PID, PV1, RGS, SCH

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('tw', 'tw-ebm-pacs.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/tw/tw-ebm-pacs.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-KMU')
        msh.sending_facility = HD(hd_1='KMU_HOSP')
        msh.receiving_application = HD(hd_1='EBM-PACS')
        msh.receiving_facility = HD(hd_1='KMU_RAD')
        msh.date_time_of_message = '20260301083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20260301083000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT600100', cx_4='KMU_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='莊', xpn_2='瑞麟')
        pid.date_time_of_birth = '19700805'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='高雄市左營區博愛二路368號', xad_3='高雄市', xad_4='81357', xad_5='TW')
        pid.pid_13 = '07-3468901'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'A382901567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='301', pl_3='01')
        pv1.pv1_7 = 'D600100^梁孟儒^^^^^KMU_HOSP'
        pv1.visit_number = CX(cx_1='V600100001')
        pv1.diet_type = CWE(cwe_1='KMU_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260301080000')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='NHI')
        in1.insurance_company_id = CX(cx_1='NHI_TW')
        in1.insurance_company_name = XON(xon_1='全民健康保險')
        in1.insureds_address = XAD(xad_1='A382901567')

        # .. build the INSURANCE group ..
        insurance = OrmO01Insurance()
        insurance.in1 = in1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit
        patient.insurance = insurance

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD600100001')
        orc.orc_7 = '1^^^20260301083000^^R'
        orc.date_time_of_order_event = '20260301083000'
        orc.orc_10 = 'N600100^護理師施芷晴'
        orc.orc_11 = 'D600100^梁孟儒'
        orc.order_control_code_reason = CWE(cwe_1='RAD', cwe_2='放射科')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600100001')
        obr.universal_service_identifier = CWE(cwe_1='33567-4', cwe_2='胸部電腦斷層', cwe_3='LN')
        obr.observation_date_time = '20260301083000'
        obr.obr_15 = 'D600100^梁孟儒'
        obr.result_status = '1^^^20260301083000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.9', cwe_2='肺炎,未明示者', cwe_3='I10')
        dg1.diagnosis_date_time = '20260301'

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
    """ Based on live/tw/tw-ebm-pacs.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-KMU')
        msh.sending_facility = HD(hd_1='KMU_HOSP')
        msh.receiving_application = HD(hd_1='EBM-PACS')
        msh.receiving_facility = HD(hd_1='KMU_RAD')
        msh.date_time_of_message = '20260302091500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20260302091500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT600200', cx_4='KMU_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='溫', xpn_2='筱涵')
        pid.date_time_of_birth = '19841122'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='高雄市苓雅區中正一路120號', xad_3='高雄市', xad_4='80264', xad_5='TW')
        pid.pid_13 = '07-2261234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'B493012678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEUR', pl_2='502', pl_3='03')
        pv1.pv1_7 = 'D600200^石育德^^^^^KMU_HOSP'
        pv1.visit_number = CX(cx_1='V600200001')
        pv1.diet_type = CWE(cwe_1='KMU_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260302080000')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='NHI')
        in1.insurance_company_id = CX(cx_1='NHI_TW')
        in1.insurance_company_name = XON(xon_1='全民健康保險')
        in1.insureds_address = XAD(xad_1='B493012678')

        # .. build the INSURANCE group ..
        insurance = OrmO01Insurance()
        insurance.in1 = in1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit
        patient.insurance = insurance

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD600200001')
        orc.orc_7 = '1^^^20260302091500^^R'
        orc.date_time_of_order_event = '20260302091500'
        orc.orc_10 = 'N600200^護理師廖佩珊'
        orc.orc_11 = 'D600200^石育德'
        orc.order_control_code_reason = CWE(cwe_1='RAD', cwe_2='放射科')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600200001')
        obr.universal_service_identifier = CWE(cwe_1='24558-9', cwe_2='腦部磁振造影', cwe_3='LN')
        obr.observation_date_time = '20260302091500'
        obr.obr_15 = 'D600200^石育德'
        obr.result_status = '1^^^20260302091500^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='G43.909', cwe_2='偏頭痛,未明示者', cwe_3='I10')
        dg1.diagnosis_date_time = '20260302'

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
    """ Based on live/tw/tw-ebm-pacs.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EBM-PACS')
        msh.sending_facility = HD(hd_1='KMU_RAD')
        msh.receiving_application = HD(hd_1='HIS-KMU')
        msh.receiving_facility = HD(hd_1='KMU_HOSP')
        msh.date_time_of_message = '20260301143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260301143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT600100', cx_4='KMU_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='莊', xpn_2='瑞麟')
        pid.date_time_of_birth = '19700805'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='高雄市左營區博愛二路368號', xad_3='高雄市', xad_4='81357', xad_5='TW')
        pid.pid_13 = '07-3468901'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'A382901567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='301', pl_3='01')
        pv1.pv1_7 = 'D600100^梁孟儒^^^^^KMU_HOSP'
        pv1.visit_number = CX(cx_1='V600100001')
        pv1.diet_type = CWE(cwe_1='KMU_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260301080000')

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
        orc.placer_order_number = EI(ei_1='ORD600100001')
        orc.placer_order_group_number = EI(ei_1='FIL600100001')
        orc.parent_order = EIP(eip_1='20260301143000')
        orc.orc_11 = 'D600100^梁孟儒'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600100001')
        obr.filler_order_number = EI(ei_1='FIL600100001')
        obr.universal_service_identifier = CWE(cwe_1='33567-4', cwe_2='胸部電腦斷層', cwe_3='LN')
        obr.observation_date_time = '20260301090000'
        obr.obr_16 = 'D600100^梁孟儒'
        obr.results_rpt_status_chng_date_time = '20260301143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='33567-4', cwe_2='胸部電腦斷層報告', cwe_3='LN')
        obx.obx_5 = '檢查所見：雙側肺野可見散在性斑塊狀浸潤影，以右下葉為著。心臟大小正常。縱膈腔無明顯淋巴結腫大。'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='33567-4', cwe_2='胸部電腦斷層報告', cwe_3='LN')
        obx_2.obx_5 = '結論：右下葉肺炎，建議臨床追蹤治療。'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ED'
        obx_3.observation_identifier = CWE(cwe_1='33567-4', cwe_2='胸部電腦斷層報告PDF', cwe_3='LN')
        obx_3.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQovQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAyMTAgPj4Kc3RyZWFtCkJUCi9GMSAxOCBUZgoxMDAgNzAwIFRkCijlpYfnvo7pm6vnmILkuK3l'
            'v4Mg6IOh6YOo6Zu76IWm5pat5bGk5aCx5ZGKKSBUZC0xOCBUZgoxMDAgNjUwIFRkCijmgqPogIU6IOisnOWul+e/sCBQQVQ2MDAxMDApIFRqCjEwMCA2MDAgVGQKKOaqouafpeaXpeac'
            'nzogMjAyNi8wMy8wMSkgVGoKMTAwIDU1MCBUZAoo57WQ6KuWOiDlj7PkuIvokYnogbrngI4pIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3Vi'
            'dHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAw'
            'MDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDMwNiAwMDAwMCBuIAowMDAwMDAwNTY4IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFy'
            'dHhyZWYKNjU1CiUlRU9GCg=='
        )
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
    """ Based on live/tw/tw-ebm-pacs.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EBM-PACS')
        msh.sending_facility = HD(hd_1='KMU_RAD')
        msh.receiving_application = HD(hd_1='HIS-KMU')
        msh.receiving_facility = HD(hd_1='KMU_HOSP')
        msh.date_time_of_message = '20260302163000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260302163000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT600200', cx_4='KMU_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='溫', xpn_2='筱涵')
        pid.date_time_of_birth = '19841122'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='高雄市苓雅區中正一路120號', xad_3='高雄市', xad_4='80264', xad_5='TW')
        pid.pid_13 = '07-2261234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'B493012678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEUR', pl_2='502', pl_3='03')
        pv1.pv1_7 = 'D600200^石育德^^^^^KMU_HOSP'
        pv1.visit_number = CX(cx_1='V600200001')
        pv1.diet_type = CWE(cwe_1='KMU_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260302080000')

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
        orc.placer_order_number = EI(ei_1='ORD600200001')
        orc.placer_order_group_number = EI(ei_1='FIL600200001')
        orc.parent_order = EIP(eip_1='20260302163000')
        orc.orc_11 = 'D600200^石育德'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600200001')
        obr.filler_order_number = EI(ei_1='FIL600200001')
        obr.universal_service_identifier = CWE(cwe_1='24558-9', cwe_2='腦部磁振造影', cwe_3='LN')
        obr.observation_date_time = '20260302100000'
        obr.obr_16 = 'D600200^石育德'
        obr.results_rpt_status_chng_date_time = '20260302163000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='24558-9', cwe_2='腦部磁振造影報告', cwe_3='LN')
        obx.obx_5 = '檢查所見：腦實質T1及T2訊號正常。腦室系統大小正常。中線結構無偏移。無異常顯影增強病灶。'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='24558-9', cwe_2='腦部磁振造影報告', cwe_3='LN')
        obx_2.obx_5 = '結論：腦部磁振造影未見明顯異常，建議定期追蹤。'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ED'
        obx_3.observation_identifier = CWE(cwe_1='24558-9', cwe_2='腦部磁振造影報告PDF', cwe_3='LN')
        obx_3.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQovQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAyMzAgPj4Kc3RyZWFtCkJUCi9GMSAxOCBUZgoxMDAgNzAwIFRkCijlpYfnvo7pm6vnmILkuK3l'
            'v4Mg6IWm6YOo56OB5oyv6YCg5b2x5aCx5ZGKKSBUZC0xOCBUZgoxMDAgNjUwIFRkCijmgqPogIU6IOabvum6l+mbsiBQQVQ2MDAyMDApIFRqCjEwMCA2MDAgVGQKKOaqouafpeaXpeac'
            'nzogMjAyNi8wMy8wMikgVGoKMTAwIDU1MCBUZAoo57WQ6KuWOiDmnKrog73pg6jno4HmjK/pgKDlvbHmnKrlj4rmmI7poa/nlbDluLgpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAw'
            'IG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAw'
            'OSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDMwNiAwMDAwMCBuIAowMDAwMDAwNTg4IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1Np'
            'emUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNjc1CiUlRU9GCg=='
        )
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
    """ Based on live/tw/tw-ebm-pacs.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-KMU')
        msh.sending_facility = HD(hd_1='KMU_HOSP')
        msh.receiving_application = HD(hd_1='EBM-PACS')
        msh.receiving_facility = HD(hd_1='KMU_RAD')
        msh.date_time_of_message = '20260303100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20260303100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT600100', cx_4='KMU_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='莊', xpn_2='瑞麟')
        pid.date_time_of_birth = '19700805'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='高雄市左營區博愛二路368號', xad_3='高雄市', xad_4='81357', xad_5='TW')
        pid.pid_13 = '07-3468901'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'A382901567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GI', pl_2='101', pl_3='01')
        pv1.pv1_7 = 'D600100^梁孟儒^^^^^KMU_HOSP'
        pv1.visit_number = CX(cx_1='V600100002')
        pv1.diet_type = CWE(cwe_1='KMU_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260303093000')

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
        orc.placer_order_number = EI(ei_1='ORD600100002')
        orc.orc_7 = '1^^^20260303100000^^R'
        orc.date_time_of_order_event = '20260303100000'
        orc.orc_10 = 'N600100^護理師施芷晴'
        orc.orc_11 = 'D600100^梁孟儒'
        orc.order_control_code_reason = CWE(cwe_1='RAD', cwe_2='放射科')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600100002')
        obr.universal_service_identifier = CWE(cwe_1='76770-6', cwe_2='腹部超音波', cwe_3='LN')
        obr.observation_date_time = '20260303100000'
        obr.obr_15 = 'D600100^梁孟儒'
        obr.result_status = '1^^^20260303100000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K76.0', cwe_2='脂肪肝,未分類於他處者', cwe_3='I10')
        dg1.diagnosis_date_time = '20260303'

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
    """ Based on live/tw/tw-ebm-pacs.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EBM-PACS')
        msh.sending_facility = HD(hd_1='KMU_RAD')
        msh.receiving_application = HD(hd_1='HIS-KMU')
        msh.receiving_facility = HD(hd_1='KMU_HOSP')
        msh.date_time_of_message = '20260303143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260303143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT600100', cx_4='KMU_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='莊', xpn_2='瑞麟')
        pid.date_time_of_birth = '19700805'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='高雄市左營區博愛二路368號', xad_3='高雄市', xad_4='81357', xad_5='TW')
        pid.pid_13 = '07-3468901'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'A382901567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GI', pl_2='101', pl_3='01')
        pv1.pv1_7 = 'D600100^梁孟儒^^^^^KMU_HOSP'
        pv1.visit_number = CX(cx_1='V600100002')
        pv1.diet_type = CWE(cwe_1='KMU_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260303093000')

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
        orc.placer_order_number = EI(ei_1='ORD600100002')
        orc.placer_order_group_number = EI(ei_1='FIL600100002')
        orc.parent_order = EIP(eip_1='20260303143000')
        orc.orc_11 = 'D600100^梁孟儒'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600100002')
        obr.filler_order_number = EI(ei_1='FIL600100002')
        obr.universal_service_identifier = CWE(cwe_1='76770-6', cwe_2='腹部超音波', cwe_3='LN')
        obr.observation_date_time = '20260303103000'
        obr.obr_16 = 'D600100^梁孟儒'
        obr.results_rpt_status_chng_date_time = '20260303143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='76770-6', cwe_2='腹部超音波報告', cwe_3='LN')
        obx.obx_5 = '檢查所見：肝臟回音增強，表面平整，大小正常。膽囊無結石。脾臟正常。雙側腎臟大小正常，無水腎。'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='76770-6', cwe_2='腹部超音波報告', cwe_3='LN')
        obx_2.obx_5 = '結論：中度脂肪肝，餘無明顯異常。'
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
    """ Based on live/tw/tw-ebm-pacs.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-KMU')
        msh.sending_facility = HD(hd_1='KMU_HOSP')
        msh.receiving_application = HD(hd_1='EBM-PACS')
        msh.receiving_facility = HD(hd_1='KMU_RAD')
        msh.date_time_of_message = '20260304090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20260304090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT600200', cx_4='KMU_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='溫', xpn_2='筱涵')
        pid.date_time_of_birth = '19841122'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='高雄市苓雅區中正一路120號', xad_3='高雄市', xad_4='80264', xad_5='TW')
        pid.pid_13 = '07-2261234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'B493012678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='201', pl_3='01')
        pv1.pv1_7 = 'D600200^石育德^^^^^KMU_HOSP'
        pv1.visit_number = CX(cx_1='V600200002')
        pv1.diet_type = CWE(cwe_1='KMU_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260304083000')

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
        orc.placer_order_number = EI(ei_1='ORD600200002')
        orc.orc_7 = '1^^^20260304090000^^R'
        orc.date_time_of_order_event = '20260304090000'
        orc.orc_10 = 'N600200^護理師廖佩珊'
        orc.orc_11 = 'D600200^石育德'
        orc.order_control_code_reason = CWE(cwe_1='RAD', cwe_2='放射科')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600200002')
        obr.universal_service_identifier = CWE(cwe_1='24606-6', cwe_2='乳房攝影', cwe_3='LN')
        obr.observation_date_time = '20260304090000'
        obr.obr_15 = 'D600200^石育德'
        obr.result_status = '1^^^20260304090000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='Z12.31', cwe_2='乳房篩檢', cwe_3='I10')
        dg1.diagnosis_date_time = '20260304'

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
    """ Based on live/tw/tw-ebm-pacs.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EBM-PACS')
        msh.sending_facility = HD(hd_1='KMU_RAD')
        msh.receiving_application = HD(hd_1='HIS-KMU')
        msh.receiving_facility = HD(hd_1='KMU_HOSP')
        msh.date_time_of_message = '20260304153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260304153000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT600200', cx_4='KMU_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='溫', xpn_2='筱涵')
        pid.date_time_of_birth = '19841122'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='高雄市苓雅區中正一路120號', xad_3='高雄市', xad_4='80264', xad_5='TW')
        pid.pid_13 = '07-2261234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'B493012678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='201', pl_3='01')
        pv1.pv1_7 = 'D600200^石育德^^^^^KMU_HOSP'
        pv1.visit_number = CX(cx_1='V600200002')
        pv1.diet_type = CWE(cwe_1='KMU_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260304083000')

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
        orc.placer_order_number = EI(ei_1='ORD600200002')
        orc.placer_order_group_number = EI(ei_1='FIL600200002')
        orc.parent_order = EIP(eip_1='20260304153000')
        orc.orc_11 = 'D600200^石育德'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600200002')
        obr.filler_order_number = EI(ei_1='FIL600200002')
        obr.universal_service_identifier = CWE(cwe_1='24606-6', cwe_2='乳房攝影', cwe_3='LN')
        obr.observation_date_time = '20260304093000'
        obr.obr_16 = 'D600200^石育德'
        obr.results_rpt_status_chng_date_time = '20260304153000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='24606-6', cwe_2='乳房攝影報告', cwe_3='LN')
        obx.obx_5 = '檢查所見：雙側乳房組織呈纖維腺體緻密型態。雙側乳房未見明顯腫塊、鈣化點或結構扭曲。腋下淋巴結未見異常。'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='24606-6', cwe_2='乳房攝影報告', cwe_3='LN')
        obx_2.obx_5 = 'BI-RADS分類：1類 - 陰性。結論：雙側乳房攝影正常，建議定期追蹤。'
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
    """ Based on live/tw/tw-ebm-pacs.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-KMU')
        msh.sending_facility = HD(hd_1='KMU_HOSP')
        msh.receiving_application = HD(hd_1='EBM-PACS')
        msh.receiving_facility = HD(hd_1='KMU_RAD')
        msh.date_time_of_message = '20260305080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20260305080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260305080000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT600100', cx_4='KMU_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='莊', xpn_2='瑞麟')
        pid.date_time_of_birth = '19700805'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='高雄市左營區博愛二路368號', xad_3='高雄市', xad_4='81357', xad_5='TW')
        pid.pid_13 = '07-3468901'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'A382901567'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='莊林雅芳')
        nk1.relationship = CWE(cwe_1='SPO')
        nk1.address = XAD(xad_1='高雄市左營區博愛二路368號', xad_3='高雄市', xad_4='81357', xad_5='TW')
        nk1.nk1_5 = '07-3468901'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='301', pl_3='02')
        pv1.pv1_7 = 'D600100^梁孟儒^^^^^KMU_HOSP'
        pv1.visit_number = CX(cx_1='V600100003')
        pv1.diet_type = CWE(cwe_1='KMU_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260305080000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='NHI')
        in1.insurance_company_id = CX(cx_1='NHI_TW')
        in1.insurance_company_name = XON(xon_1='全民健康保險')
        in1.insureds_address = XAD(xad_1='A382901567')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='C34.90', cwe_2='肺惡性腫瘤,未明示者', cwe_3='I10')
        dg1.diagnosis_date_time = '20260305'

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
    """ Based on live/tw/tw-ebm-pacs.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-KMU')
        msh.sending_facility = HD(hd_1='KMU_HOSP')
        msh.receiving_application = HD(hd_1='EBM-PACS')
        msh.receiving_facility = HD(hd_1='KMU_RAD')
        msh.date_time_of_message = '20260305093000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20260305093000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT600100', cx_4='KMU_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='莊', xpn_2='瑞麟')
        pid.date_time_of_birth = '19700805'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='高雄市左營區博愛二路368號', xad_3='高雄市', xad_4='81357', xad_5='TW')
        pid.pid_13 = '07-3468901'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'A382901567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='301', pl_3='02')
        pv1.pv1_7 = 'D600100^梁孟儒^^^^^KMU_HOSP'
        pv1.visit_number = CX(cx_1='V600100003')
        pv1.diet_type = CWE(cwe_1='KMU_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260305080000')

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
        orc.placer_order_number = EI(ei_1='ORD600100003')
        orc.orc_7 = '1^^^20260305100000^^R'
        orc.date_time_of_order_event = '20260305093000'
        orc.orc_10 = 'N600100^護理師施芷晴'
        orc.orc_11 = 'D600100^梁孟儒'
        orc.order_control_code_reason = CWE(cwe_1='RAD', cwe_2='放射科')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600100003')
        obr.universal_service_identifier = CWE(cwe_1='CTBX001', cwe_2='電腦斷層導引肺切片', cwe_3='LOCAL')
        obr.observation_date_time = '20260305093000'
        obr.obr_15 = 'D600100^梁孟儒'
        obr.result_status = '1^^^20260305100000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='C34.90', cwe_2='肺惡性腫瘤,未明示者', cwe_3='I10')
        dg1.diagnosis_date_time = '20260305'

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
    """ Based on live/tw/tw-ebm-pacs.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EBM-PACS')
        msh.sending_facility = HD(hd_1='KMU_RAD')
        msh.receiving_application = HD(hd_1='HIS-KMU')
        msh.receiving_facility = HD(hd_1='KMU_HOSP')
        msh.date_time_of_message = '20260305153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260305153000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT600100', cx_4='KMU_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='莊', xpn_2='瑞麟')
        pid.date_time_of_birth = '19700805'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='高雄市左營區博愛二路368號', xad_3='高雄市', xad_4='81357', xad_5='TW')
        pid.pid_13 = '07-3468901'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'A382901567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='301', pl_3='02')
        pv1.pv1_7 = 'D600100^梁孟儒^^^^^KMU_HOSP'
        pv1.visit_number = CX(cx_1='V600100003')
        pv1.diet_type = CWE(cwe_1='KMU_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260305080000')

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
        orc.placer_order_number = EI(ei_1='ORD600100003')
        orc.placer_order_group_number = EI(ei_1='FIL600100003')
        orc.parent_order = EIP(eip_1='20260305153000')
        orc.orc_11 = 'D600100^梁孟儒'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600100003')
        obr.filler_order_number = EI(ei_1='FIL600100003')
        obr.universal_service_identifier = CWE(cwe_1='CTBX001', cwe_2='電腦斷層導引肺切片', cwe_3='LOCAL')
        obr.observation_date_time = '20260305100000'
        obr.obr_16 = 'D600100^梁孟儒'
        obr.results_rpt_status_chng_date_time = '20260305153000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='CTBX001', cwe_2='電腦斷層導引肺切片報告', cwe_3='LOCAL')
        obx.obx_5 = '右下肺葉2.3公分結節，以20G切片針經皮穿刺，取得3條組織檢體送病理。術後即時胸部X光無氣胸。'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='CTBX001', cwe_2='電腦斷層導引肺切片報告PDF', cwe_3='LOCAL')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQovQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAyNDAgPj4Kc3RyZWFtCkJUCi9GMSAxOCBUZgoxMDAgNzAwIFRkCijlpYfnvo7pm6vnmILkuK3l'
            'v4Mg6Zu76IWm5bCO5byV6IK65YiH54mH5aCx5ZGKKSBUZC0xOCBUZgoxMDAgNjUwIFRkCijmgqPogIU6IOisnOWul+e/sCBQQVQ2MDAxMDApIFRqCjEwMCA2MDAgVGQKKOWPluW+lzPm'
            'op3ntYTnuZTmqqLpq5TpgIHnl4XnkIYpIFRqCjEwMCA1NTAgVGQKKOihk+W+jOWNs+aZguiDuOmDqFjlhYnnhKHmsKPog7gpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8'
            'PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAw'
            'MCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDMwNiAwMDAwMCBuIAowMDAwMDAwNTk4IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAv'
            'Um9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNjg1CiUlRU9GCg=='
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
    """ Based on live/tw/tw-ebm-pacs.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-KMU')
        msh.sending_facility = HD(hd_1='KMU_HOSP')
        msh.receiving_application = HD(hd_1='EBM-PACS')
        msh.receiving_facility = HD(hd_1='KMU_RAD')
        msh.date_time_of_message = '20260307100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG20260307100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260307100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT600100', cx_4='KMU_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='莊', xpn_2='瑞麟')
        pid.date_time_of_birth = '19700805'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='高雄市左營區博愛二路368號', xad_3='高雄市', xad_4='81357', xad_5='TW')
        pid.pid_13 = '07-3468901'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'A382901567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='301', pl_3='02')
        pv1.pv1_7 = 'D600100^梁孟儒^^^^^KMU_HOSP'
        pv1.visit_number = CX(cx_1='V600100003')
        pv1.discharged_to_location = DLD(dld_1='01')
        pv1.diet_type = CWE(cwe_1='KMU_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260305080000')
        pv1.current_patient_balance = '20260307100000'

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/tw/tw-ebm-pacs.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-KMU')
        msh.sending_facility = HD(hd_1='KMU_HOSP')
        msh.receiving_application = HD(hd_1='EBM-PACS')
        msh.receiving_facility = HD(hd_1='KMU_RAD')
        msh.date_time_of_message = '20260308141500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20260308141500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT600200', cx_4='KMU_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='溫', xpn_2='筱涵')
        pid.date_time_of_birth = '19841122'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='高雄市苓雅區中正一路120號', xad_3='高雄市', xad_4='80264', xad_5='TW')
        pid.pid_13 = '07-2261234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'B493012678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ORTHO', pl_2='102', pl_3='01')
        pv1.pv1_7 = 'D600200^石育德^^^^^KMU_HOSP'
        pv1.visit_number = CX(cx_1='V600200003')
        pv1.diet_type = CWE(cwe_1='KMU_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260308140000')

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
        orc.placer_order_number = EI(ei_1='ORD600200003')
        orc.orc_7 = '1^^^20260308141500^^R'
        orc.date_time_of_order_event = '20260308141500'
        orc.orc_10 = 'N600200^護理師廖佩珊'
        orc.orc_11 = 'D600200^石育德'
        orc.order_control_code_reason = CWE(cwe_1='RAD', cwe_2='放射科')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600200003')
        obr.universal_service_identifier = CWE(cwe_1='36554-4', cwe_2='腰薦椎X光', cwe_3='LN')
        obr.observation_date_time = '20260308141500'
        obr.obr_15 = 'D600200^石育德'
        obr.result_status = '1^^^20260308141500^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M54.5', cwe_2='下背痛', cwe_3='I10')
        dg1.diagnosis_date_time = '20260308'

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
    """ Based on live/tw/tw-ebm-pacs.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EBM-PACS')
        msh.sending_facility = HD(hd_1='KMU_RAD')
        msh.receiving_application = HD(hd_1='HIS-KMU')
        msh.receiving_facility = HD(hd_1='KMU_HOSP')
        msh.date_time_of_message = '20260308160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260308160000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT600200', cx_4='KMU_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='溫', xpn_2='筱涵')
        pid.date_time_of_birth = '19841122'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='高雄市苓雅區中正一路120號', xad_3='高雄市', xad_4='80264', xad_5='TW')
        pid.pid_13 = '07-2261234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'B493012678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ORTHO', pl_2='102', pl_3='01')
        pv1.pv1_7 = 'D600200^石育德^^^^^KMU_HOSP'
        pv1.visit_number = CX(cx_1='V600200003')
        pv1.diet_type = CWE(cwe_1='KMU_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260308140000')

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
        orc.placer_order_number = EI(ei_1='ORD600200003')
        orc.placer_order_group_number = EI(ei_1='FIL600200003')
        orc.parent_order = EIP(eip_1='20260308160000')
        orc.orc_11 = 'D600200^石育德'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600200003')
        obr.filler_order_number = EI(ei_1='FIL600200003')
        obr.universal_service_identifier = CWE(cwe_1='36554-4', cwe_2='腰薦椎X光', cwe_3='LN')
        obr.observation_date_time = '20260308143000'
        obr.obr_16 = 'D600200^石育德'
        obr.results_rpt_status_chng_date_time = '20260308160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='36554-4', cwe_2='腰薦椎X光報告', cwe_3='LN')
        obx.obx_5 = '檢查所見：腰椎排列正常，椎體高度及椎間距無明顯異常。L4-L5及L5-S1椎間盤間隙輕微狹窄。無滑脫或骨折。'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='36554-4', cwe_2='腰薦椎X光報告', cwe_3='LN')
        obx_2.obx_5 = '結論：腰椎輕度退化性變化，建議臨床相關追蹤。'
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
    """ Based on live/tw/tw-ebm-pacs.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-KMU')
        msh.sending_facility = HD(hd_1='KMU_HOSP')
        msh.receiving_application = HD(hd_1='EBM-PACS')
        msh.receiving_facility = HD(hd_1='KMU_RAD')
        msh.date_time_of_message = '20260309083000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'MSG20260309083000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='SCH600100001')
        sch.event_reason = CWE(cwe_1='CT_CHEST')
        sch.appointment_reason = CWE(cwe_1='33567-4', cwe_2='胸部電腦斷層', cwe_3='LN')
        sch.appointment_type = CWE(cwe_1='ROUTINE')
        sch.sch_9 = '30'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^30^20260315090000^20260315093000'
        sch.sch_13 = 'D600100^梁孟儒'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT600100', cx_4='KMU_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='莊', xpn_2='瑞麟')
        pid.date_time_of_birth = '19700805'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='高雄市左營區博愛二路368號', xad_3='高雄市', xad_4='81357', xad_5='TW')
        pid.pid_13 = '07-3468901'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='CT', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='D600100', xcn_2='梁孟儒')

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
        ais.universal_service_identifier = CWE(cwe_1='33567-4', cwe_2='胸部電腦斷層', cwe_3='LN')
        ais.start_date_time = '20260315090000'
        ais.start_date_time_offset = '30'
        ais.start_date_time_offset_units = CNE(cne_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='KMU_RAD', pl_2='CT_ROOM1', pl_3='CT掃描室1')
        ail.start_date_time_offset = '20260315090000'
        ail.start_date_time_offset_units = CNE(cne_1='30')
        ail.duration = 'MIN'

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='D600100', xcn_2='梁孟儒')
        aip.resource_type = CWE(cwe_1='RAD')
        aip.start_date_time_offset_units = CNE(cne_1='20260315090000')
        aip.duration = '30'
        aip.duration_units = CNE(cne_1='MIN')

        # .. build the PERSONNEL_RESOURCE group ..
        personnel_resource = SiuS12PersonnelResource()
        personnel_resource.aip = aip

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service
        resources.location_resource = location_resource
        resources.personnel_resource = personnel_resource

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources

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
    """ Based on live/tw/tw-ebm-pacs.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-KMU')
        msh.sending_facility = HD(hd_1='KMU_HOSP')
        msh.receiving_application = HD(hd_1='EBM-PACS')
        msh.receiving_facility = HD(hd_1='KMU_RAD')
        msh.date_time_of_message = '20260310100000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S14', msg_3='SIU_S12')
        msh.message_control_id = 'MSG20260310100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='SCH600100001')
        sch.event_reason = CWE(cwe_1='CT_CHEST')
        sch.appointment_reason = CWE(cwe_1='33567-4', cwe_2='胸部電腦斷層', cwe_3='LN')
        sch.appointment_type = CWE(cwe_1='ROUTINE')
        sch.sch_9 = '30'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^30^20260316090000^20260316093000'
        sch.sch_13 = 'D600100^梁孟儒'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT600100', cx_4='KMU_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='莊', xpn_2='瑞麟')
        pid.date_time_of_birth = '19700805'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='高雄市左營區博愛二路368號', xad_3='高雄市', xad_4='81357', xad_5='TW')
        pid.pid_13 = '07-3468901'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='CT', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='D600100', xcn_2='梁孟儒')

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
        ais.universal_service_identifier = CWE(cwe_1='33567-4', cwe_2='胸部電腦斷層', cwe_3='LN')
        ais.start_date_time = '20260316090000'
        ais.start_date_time_offset = '30'
        ais.start_date_time_offset_units = CNE(cne_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='KMU_RAD', pl_2='CT_ROOM1', pl_3='CT掃描室1')
        ail.start_date_time_offset = '20260316090000'
        ail.start_date_time_offset_units = CNE(cne_1='30')
        ail.duration = 'MIN'

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='D600100', xcn_2='梁孟儒')
        aip.resource_type = CWE(cwe_1='RAD')
        aip.start_date_time_offset_units = CNE(cne_1='20260316090000')
        aip.duration = '30'
        aip.duration_units = CNE(cne_1='MIN')

        # .. build the PERSONNEL_RESOURCE group ..
        personnel_resource = SiuS12PersonnelResource()
        personnel_resource.aip = aip

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service
        resources.location_resource = location_resource
        resources.personnel_resource = personnel_resource

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources

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
    """ Based on live/tw/tw-ebm-pacs.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-KMU')
        msh.sending_facility = HD(hd_1='KMU_HOSP')
        msh.receiving_application = HD(hd_1='EBM-PACS')
        msh.receiving_facility = HD(hd_1='KMU_RAD')
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
        pid.patient_identifier_list = CX(cx_1='PAT600200', cx_4='KMU_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='溫', xpn_2='筱涵')
        pid.date_time_of_birth = '19841122'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='高雄市苓雅區中正一路120號', xad_3='高雄市', xad_4='80264', xad_5='TW')
        pid.pid_13 = '07-2261234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'B493012678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='201', pl_3='01')
        pv1.pv1_7 = 'D600200^石育德^^^^^KMU_HOSP'
        pv1.visit_number = CX(cx_1='V600200003')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/tw/tw-ebm-pacs.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-KMU')
        msh.sending_facility = HD(hd_1='KMU_HOSP')
        msh.receiving_application = HD(hd_1='EBM-PACS')
        msh.receiving_facility = HD(hd_1='KMU_RAD')
        msh.date_time_of_message = '20260312090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20260312090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT600100', cx_4='KMU_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='莊', xpn_2='瑞麟')
        pid.date_time_of_birth = '19700805'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='高雄市左營區博愛二路368號', xad_3='高雄市', xad_4='81357', xad_5='TW')
        pid.pid_13 = '07-3468901'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'A382901567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='NM', pl_2='301', pl_3='01')
        pv1.pv1_7 = 'D600100^梁孟儒^^^^^KMU_HOSP'
        pv1.visit_number = CX(cx_1='V600100004')
        pv1.diet_type = CWE(cwe_1='KMU_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260312083000')

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
        orc.placer_order_number = EI(ei_1='ORD600100004')
        orc.orc_7 = '1^^^20260312100000^^R'
        orc.date_time_of_order_event = '20260312090000'
        orc.orc_10 = 'N600100^護理師施芷晴'
        orc.orc_11 = 'D600100^梁孟儒'
        orc.order_control_code_reason = CWE(cwe_1='NM', cwe_2='核醫科')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600100004')
        obr.universal_service_identifier = CWE(cwe_1='49509-7', cwe_2='正子電腦斷層掃描', cwe_3='LN')
        obr.observation_date_time = '20260312090000'
        obr.obr_15 = 'D600100^梁孟儒'
        obr.result_status = '1^^^20260312100000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='C34.90', cwe_2='肺惡性腫瘤,未明示者', cwe_3='I10')
        dg1.diagnosis_date_time = '20260312'

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
    """ Based on live/tw/tw-ebm-pacs.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EBM-PACS')
        msh.sending_facility = HD(hd_1='KMU_RAD')
        msh.receiving_application = HD(hd_1='HIS-KMU')
        msh.receiving_facility = HD(hd_1='KMU_HOSP')
        msh.date_time_of_message = '20260312170000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260312170000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT600100', cx_4='KMU_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='莊', xpn_2='瑞麟')
        pid.date_time_of_birth = '19700805'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='高雄市左營區博愛二路368號', xad_3='高雄市', xad_4='81357', xad_5='TW')
        pid.pid_13 = '07-3468901'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'A382901567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='NM', pl_2='301', pl_3='01')
        pv1.pv1_7 = 'D600100^梁孟儒^^^^^KMU_HOSP'
        pv1.visit_number = CX(cx_1='V600100004')
        pv1.diet_type = CWE(cwe_1='KMU_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260312083000')

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
        orc.placer_order_number = EI(ei_1='ORD600100004')
        orc.placer_order_group_number = EI(ei_1='FIL600100004')
        orc.parent_order = EIP(eip_1='20260312170000')
        orc.orc_11 = 'D600100^梁孟儒'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600100004')
        obr.filler_order_number = EI(ei_1='FIL600100004')
        obr.universal_service_identifier = CWE(cwe_1='49509-7', cwe_2='正子電腦斷層掃描', cwe_3='LN')
        obr.observation_date_time = '20260312100000'
        obr.obr_16 = 'D600100^梁孟儒'
        obr.results_rpt_status_chng_date_time = '20260312170000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='49509-7', cwe_2='正子電腦斷層掃描報告', cwe_3='LN')
        obx.obx_5 = '檢查所見：右下肺葉2.5公分結節FDG攝取增加（SUVmax 8.3）。右肺門及縱膈腔淋巴結FDG攝取增加。肝、脾、腎及骨骼未見異常攝取。'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='49509-7', cwe_2='正子電腦斷層掃描報告', cwe_3='LN')
        obx_2.obx_5 = '結論：右下肺葉惡性腫瘤併右肺門及縱膈腔淋巴結轉移，臨床分期建議T1cN2M0。'
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
    """ Based on live/tw/tw-ebm-pacs.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-KMU')
        msh.sending_facility = HD(hd_1='KMU_HOSP')
        msh.receiving_application = HD(hd_1='EBM-PACS')
        msh.receiving_facility = HD(hd_1='KMU_RAD')
        msh.date_time_of_message = '20260313023000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20260313023000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT600200', cx_4='KMU_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='溫', xpn_2='筱涵')
        pid.date_time_of_birth = '19841122'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='高雄市苓雅區中正一路120號', xad_3='高雄市', xad_4='80264', xad_5='TW')
        pid.pid_13 = '07-2261234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'B493012678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ER', pl_2='001', pl_3='01')
        pv1.pv1_7 = 'D600200^石育德^^^^^KMU_HOSP'
        pv1.visit_number = CX(cx_1='V600200004')
        pv1.diet_type = CWE(cwe_1='KMU_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260313020000')

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
        orc.placer_order_number = EI(ei_1='ORD600200004')
        orc.orc_7 = '1^^^20260313023000^^S'
        orc.date_time_of_order_event = '20260313023000'
        orc.orc_10 = 'N600300^護理師潘宜蓁'
        orc.orc_11 = 'D600200^石育德'
        orc.order_control_code_reason = CWE(cwe_1='RAD', cwe_2='放射科')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600200004')
        obr.universal_service_identifier = CWE(cwe_1='36643-5', cwe_2='胸部X光', cwe_3='LN')
        obr.observation_date_time = '20260313023000'
        obr.obr_14 = 'STAT'
        obr.obr_15 = 'D600200^石育德'
        obr.result_status = '1^^^20260313023000^^S'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R06.0', cwe_2='呼吸困難', cwe_3='I10')
        dg1.diagnosis_date_time = '20260313'

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
