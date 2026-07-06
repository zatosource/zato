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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, DLD, EI, EIP, HD, MSG, OG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, OrmO01Insurance, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, \
    OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12LocationResource, SiuS12Patient, \
    SiuS12PersonnelResource, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A03, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, DG1, EVN, IN1, MSH, NK1, OBR, OBX, ORC, PID, PV1, RGS, SCH

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('tw', 'tw-philips-intellisite.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/tw/tw-philips-intellisite.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-CATHAY')
        msh.sending_facility = HD(hd_1='CATHAY_HOSP')
        msh.receiving_application = HD(hd_1='IntelliSite')
        msh.receiving_facility = HD(hd_1='CATHAY_RAD')
        msh.date_time_of_message = '20260301091000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20260301091000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT700100', cx_4='CATHAY_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='段', xpn_2='振宇')
        pid.date_time_of_birth = '19670218'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新北市三重區重新路五段600號', xad_3='新北市', xad_4='24158', xad_5='TW')
        pid.pid_13 = '02-29821234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'C401267893'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='IM', pl_2='201', pl_3='01')
        pv1.pv1_7 = 'D700100^顏淑美^^^^^CATHAY_HOSP'
        pv1.visit_number = CX(cx_1='V700100001')
        pv1.diet_type = CWE(cwe_1='CATHAY_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260301083000')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='NHI')
        in1.insurance_company_id = CX(cx_1='NHI_TW')
        in1.insurance_company_name = XON(xon_1='全民健康保險')
        in1.insureds_address = XAD(xad_1='C401267893')

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
        orc.placer_order_number = EI(ei_1='ORD700100001')
        orc.orc_7 = '1^^^20260301091000^^R'
        orc.date_time_of_order_event = '20260301091000'
        orc.orc_10 = 'N700100^護理師唐雅婷'
        orc.orc_11 = 'D700100^顏淑美'
        orc.order_control_code_reason = CWE(cwe_1='RAD', cwe_2='放射科')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700100001')
        obr.universal_service_identifier = CWE(cwe_1='36643-5', cwe_2='胸部X光', cwe_3='LN')
        obr.observation_date_time = '20260301091000'
        obr.obr_15 = 'D700100^顏淑美'
        obr.result_status = '1^^^20260301091000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J06.9', cwe_2='急性上呼吸道感染', cwe_3='I10')
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
    """ Based on live/tw/tw-philips-intellisite.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IntelliSite')
        msh.sending_facility = HD(hd_1='CATHAY_RAD')
        msh.receiving_application = HD(hd_1='HIS-CATHAY')
        msh.receiving_facility = HD(hd_1='CATHAY_HOSP')
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
        pid.patient_identifier_list = CX(cx_1='PAT700100', cx_4='CATHAY_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='段', xpn_2='振宇')
        pid.date_time_of_birth = '19670218'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新北市三重區重新路五段600號', xad_3='新北市', xad_4='24158', xad_5='TW')
        pid.pid_13 = '02-29821234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'C401267893'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='IM', pl_2='201', pl_3='01')
        pv1.pv1_7 = 'D700100^顏淑美^^^^^CATHAY_HOSP'
        pv1.visit_number = CX(cx_1='V700100001')
        pv1.diet_type = CWE(cwe_1='CATHAY_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260301083000')

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
        orc.placer_order_number = EI(ei_1='ORD700100001')
        orc.placer_order_group_number = EI(ei_1='FIL700100001')
        orc.parent_order = EIP(eip_1='20260301143000')
        orc.orc_11 = 'D700100^顏淑美'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700100001')
        obr.filler_order_number = EI(ei_1='FIL700100001')
        obr.universal_service_identifier = CWE(cwe_1='36643-5', cwe_2='胸部X光', cwe_3='LN')
        obr.observation_date_time = '20260301093000'
        obr.obr_16 = 'D700100^顏淑美'
        obr.results_rpt_status_chng_date_time = '20260301143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='36643-5', cwe_2='胸部X光報告', cwe_3='LN')
        obx.obx_5 = '檢查所見：心臟大小正常。雙側肺野清晰，無明顯浸潤影。肋膈角銳利。縱膈腔無增寬。'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='36643-5', cwe_2='胸部X光報告', cwe_3='LN')
        obx_2.obx_5 = '結論：胸部X光正常。'
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
    """ Based on live/tw/tw-philips-intellisite.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-CATHAY')
        msh.sending_facility = HD(hd_1='CATHAY_HOSP')
        msh.receiving_application = HD(hd_1='IntelliSite')
        msh.receiving_facility = HD(hd_1='CATHAY_RAD')
        msh.date_time_of_message = '20260302100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20260302100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT700200', cx_4='CATHAY_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='沈', xpn_2='佩珊')
        pid.date_time_of_birth = '19890709'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市汐止區大同路二段168號', xad_3='新北市', xad_4='22161', xad_5='TW')
        pid.pid_13 = '02-26421234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'D512378904'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GI', pl_2='401', pl_3='02')
        pv1.pv1_7 = 'D700200^柯彥廷^^^^^CATHAY_HOSP'
        pv1.visit_number = CX(cx_1='V700200001')
        pv1.diet_type = CWE(cwe_1='CATHAY_HOSP')
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
        in1.insureds_address = XAD(xad_1='D512378904')

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
        orc.placer_order_number = EI(ei_1='ORD700200001')
        orc.orc_7 = '1^^^20260302100000^^R'
        orc.date_time_of_order_event = '20260302100000'
        orc.orc_10 = 'N700200^護理師吳芷彤'
        orc.orc_11 = 'D700200^柯彥廷'
        orc.order_control_code_reason = CWE(cwe_1='RAD', cwe_2='放射科')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700200001')
        obr.universal_service_identifier = CWE(cwe_1='79103-8', cwe_2='腹部電腦斷層含顯影劑', cwe_3='LN')
        obr.observation_date_time = '20260302100000'
        obr.obr_15 = 'D700200^柯彥廷'
        obr.result_status = '1^^^20260302100000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K80.20', cwe_2='膽囊結石不伴有膽囊炎', cwe_3='I10')
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
    """ Based on live/tw/tw-philips-intellisite.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IntelliSite')
        msh.sending_facility = HD(hd_1='CATHAY_RAD')
        msh.receiving_application = HD(hd_1='HIS-CATHAY')
        msh.receiving_facility = HD(hd_1='CATHAY_HOSP')
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
        pid.patient_identifier_list = CX(cx_1='PAT700200', cx_4='CATHAY_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='沈', xpn_2='佩珊')
        pid.date_time_of_birth = '19890709'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市汐止區大同路二段168號', xad_3='新北市', xad_4='22161', xad_5='TW')
        pid.pid_13 = '02-26421234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'D512378904'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GI', pl_2='401', pl_3='02')
        pv1.pv1_7 = 'D700200^柯彥廷^^^^^CATHAY_HOSP'
        pv1.visit_number = CX(cx_1='V700200001')
        pv1.diet_type = CWE(cwe_1='CATHAY_HOSP')
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
        orc.placer_order_number = EI(ei_1='ORD700200001')
        orc.placer_order_group_number = EI(ei_1='FIL700200001')
        orc.parent_order = EIP(eip_1='20260302163000')
        orc.orc_11 = 'D700200^柯彥廷'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700200001')
        obr.filler_order_number = EI(ei_1='FIL700200001')
        obr.universal_service_identifier = CWE(cwe_1='79103-8', cwe_2='腹部電腦斷層含顯影劑', cwe_3='LN')
        obr.observation_date_time = '20260302103000'
        obr.obr_16 = 'D700200^柯彥廷'
        obr.results_rpt_status_chng_date_time = '20260302163000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='79103-8', cwe_2='腹部電腦斷層報告', cwe_3='LN')
        obx.obx_5 = '檢查所見：肝臟大小正常，無局部性病灶。膽囊內可見多顆結石，最大約1.2公分。膽總管未擴張。胰臟、脾臟及雙側腎臟正常。'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='79103-8', cwe_2='腹部電腦斷層報告', cwe_3='LN')
        obx_2.obx_5 = '結論：膽囊結石症，餘腹部臟器未見明顯異常。'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ED'
        obx_3.observation_identifier = CWE(cwe_1='79103-8', cwe_2='腹部電腦斷層報告PDF', cwe_3='LN')
        obx_3.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQovQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAyNTAgPj4Kc3RyZWFtCkJUCi9GMSAxOCBUZgoxMDAgNzAwIFRkCijlnIvms7Dnt5zlkIjphqvp'
            'maIg6IW56YOo6Zu76IWm5pat5bGk5aCx5ZGKKSBUZC0xOCBUZgoxMDAgNjUwIFRkCijmgqPogIU6IOaWvemdnOWunCBQQVQ3MDAyMDApIFRqCjEwMCA2MDAgVGQKKOaqouafpeaXpeac'
            'nzogMjAyNi8wMy8wMikgVGoKMTAwIDU1MCBUZAoo57WQ6KuWOiDona/lm4rntoLnn7Pnl4cpIFRqCjEwMCA1MDAgVGQKKOmkkOiFuOmDqOiHn+WZqOacquimi+aYjumhr+eVsOW4uCkg'
            'VGoKRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8IC9UeXBlIC9Gb250IC9TdWJ0eXBlIC9UeXBlMSAvQmFzZUZvbnQgL0hlbHZldGljYSA+PgplbmRvYmoKeHJlZgowIDYKMDAw'
            'MDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDExNSAwMDAwMCBuIAowMDAwMDAwMzA2IDAwMDAwIG4gCjAwMDAwMDA2'
            'MDggMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA2IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgo2OTUKJSVFTwZ=='
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
    """ Based on live/tw/tw-philips-intellisite.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-CATHAY')
        msh.sending_facility = HD(hd_1='CATHAY_HOSP')
        msh.receiving_application = HD(hd_1='IntelliSite')
        msh.receiving_facility = HD(hd_1='CATHAY_RAD')
        msh.date_time_of_message = '20260303090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20260303090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT700100', cx_4='CATHAY_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='段', xpn_2='振宇')
        pid.date_time_of_birth = '19670218'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新北市三重區重新路五段600號', xad_3='新北市', xad_4='24158', xad_5='TW')
        pid.pid_13 = '02-29821234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'C401267893'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ORTHO', pl_2='102', pl_3='01')
        pv1.pv1_7 = 'D700100^顏淑美^^^^^CATHAY_HOSP'
        pv1.visit_number = CX(cx_1='V700100002')
        pv1.diet_type = CWE(cwe_1='CATHAY_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260303083000')

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
        orc.placer_order_number = EI(ei_1='ORD700100002')
        orc.orc_7 = '1^^^20260303090000^^R'
        orc.date_time_of_order_event = '20260303090000'
        orc.orc_10 = 'N700100^護理師唐雅婷'
        orc.orc_11 = 'D700100^顏淑美'
        orc.order_control_code_reason = CWE(cwe_1='RAD', cwe_2='放射科')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700100002')
        obr.universal_service_identifier = CWE(cwe_1='36557-7', cwe_2='膝關節磁振造影', cwe_3='LN')
        obr.observation_date_time = '20260303090000'
        obr.obr_15 = 'D700100^顏淑美'
        obr.result_status = '1^^^20260303090000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M23.91', cwe_2='膝內障,未明示者', cwe_3='I10')
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
    """ Based on live/tw/tw-philips-intellisite.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IntelliSite')
        msh.sending_facility = HD(hd_1='CATHAY_RAD')
        msh.receiving_application = HD(hd_1='HIS-CATHAY')
        msh.receiving_facility = HD(hd_1='CATHAY_HOSP')
        msh.date_time_of_message = '20260303170000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260303170000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT700100', cx_4='CATHAY_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='段', xpn_2='振宇')
        pid.date_time_of_birth = '19670218'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新北市三重區重新路五段600號', xad_3='新北市', xad_4='24158', xad_5='TW')
        pid.pid_13 = '02-29821234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'C401267893'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ORTHO', pl_2='102', pl_3='01')
        pv1.pv1_7 = 'D700100^顏淑美^^^^^CATHAY_HOSP'
        pv1.visit_number = CX(cx_1='V700100002')
        pv1.diet_type = CWE(cwe_1='CATHAY_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260303083000')

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
        orc.placer_order_number = EI(ei_1='ORD700100002')
        orc.placer_order_group_number = EI(ei_1='FIL700100002')
        orc.parent_order = EIP(eip_1='20260303170000')
        orc.orc_11 = 'D700100^顏淑美'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700100002')
        obr.filler_order_number = EI(ei_1='FIL700100002')
        obr.universal_service_identifier = CWE(cwe_1='36557-7', cwe_2='膝關節磁振造影', cwe_3='LN')
        obr.observation_date_time = '20260303100000'
        obr.obr_16 = 'D700100^顏淑美'
        obr.results_rpt_status_chng_date_time = '20260303170000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='36557-7', cwe_2='膝關節磁振造影報告', cwe_3='LN')
        obx.obx_5 = '檢查所見：右膝內側半月板後角可見高訊號延伸至關節面，符合第三級撕裂。前十字韌帶完整。關節腔少量積液。'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='36557-7', cwe_2='膝關節磁振造影報告', cwe_3='LN')
        obx_2.obx_5 = '結論：右膝內側半月板後角撕裂，建議骨科評估。'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ED'
        obx_3.observation_identifier = CWE(cwe_1='36557-7', cwe_2='膝關節磁振造影報告PDF', cwe_3='LN')
        obx_3.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQovQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAyMzUgPj4Kc3RyZWFtCkJUCi9GMSAxOCBUZgoxMDAgNzAwIFRkCijlnIvms7Dnt5zlkIjphqvp'
            'maIg6Iag6Zec56+A56OB5oyv6YCg5b2x5aCx5ZGKKSBUZC0xOCBUZgoxMDAgNjUwIFRkCijmgqPogIU6IOmBuOW7uuW/lyBQQVQ3MDAxMDApIFRqCjEwMCA2MDAgVGQKKOaqouafpeaX'
            'peacnzogMjAyNi8wMy8wMykgVGoKMTAwIDU1MCBUZAoo57WQ6KuWOiDlj7PohJ3lhafgvrXljYrmnIjmnb/lr4zop5Lmkpjoo4IpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9i'
            'ago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAw'
            'MDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4gCjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDMwNiAwMDAwMCBuIAowMDAwMDAwNTkzIDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUg'
            'NiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKNjgwCiUlRU9GCg=='
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
    """ Based on live/tw/tw-philips-intellisite.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-CATHAY')
        msh.sending_facility = HD(hd_1='CATHAY_HOSP')
        msh.receiving_application = HD(hd_1='IntelliSite')
        msh.receiving_facility = HD(hd_1='CATHAY_RAD')
        msh.date_time_of_message = '20260304083000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'MSG20260304083000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='SCH700200001')
        sch.event_reason = CWE(cwe_1='US_ABD')
        sch.appointment_reason = CWE(cwe_1='76770-6', cwe_2='腹部超音波', cwe_3='LN')
        sch.appointment_type = CWE(cwe_1='ROUTINE')
        sch.sch_9 = '20'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^20^20260310100000^20260310102000'
        sch.sch_13 = 'D700200^柯彥廷'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT700200', cx_4='CATHAY_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='沈', xpn_2='佩珊')
        pid.date_time_of_birth = '19890709'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市汐止區大同路二段168號', xad_3='新北市', xad_4='22161', xad_5='TW')
        pid.pid_13 = '02-26421234'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='US', pl_3='01')
        pv1.attending_doctor = XCN(xcn_1='D700200', xcn_2='柯彥廷')

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
        ais.universal_service_identifier = CWE(cwe_1='76770-6', cwe_2='腹部超音波', cwe_3='LN')
        ais.start_date_time = '20260310100000'
        ais.start_date_time_offset = '20'
        ais.start_date_time_offset_units = CNE(cne_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='CATHAY_RAD', pl_2='US_ROOM2', pl_3='超音波室2')
        ail.start_date_time_offset = '20260310100000'
        ail.start_date_time_offset_units = CNE(cne_1='20')
        ail.duration = 'MIN'

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='D700200', xcn_2='柯彥廷')
        aip.resource_type = CWE(cwe_1='RAD')
        aip.start_date_time_offset_units = CNE(cne_1='20260310100000')
        aip.duration = '20'
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
    """ Based on live/tw/tw-philips-intellisite.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-CATHAY')
        msh.sending_facility = HD(hd_1='CATHAY_HOSP')
        msh.receiving_application = HD(hd_1='IntelliSite')
        msh.receiving_facility = HD(hd_1='CATHAY_RAD')
        msh.date_time_of_message = '20260305023000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20260305023000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT700100', cx_4='CATHAY_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='段', xpn_2='振宇')
        pid.date_time_of_birth = '19670218'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新北市三重區重新路五段600號', xad_3='新北市', xad_4='24158', xad_5='TW')
        pid.pid_13 = '02-29821234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'C401267893'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ER', pl_2='001', pl_3='03')
        pv1.pv1_7 = 'D700100^顏淑美^^^^^CATHAY_HOSP'
        pv1.visit_number = CX(cx_1='V700100003')
        pv1.diet_type = CWE(cwe_1='CATHAY_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260305020000')

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
        orc.placer_order_number = EI(ei_1='ORD700100003')
        orc.orc_7 = '1^^^20260305023000^^S'
        orc.date_time_of_order_event = '20260305023000'
        orc.orc_10 = 'N700300^護理師楊佩琪'
        orc.orc_11 = 'D700100^顏淑美'
        orc.order_control_code_reason = CWE(cwe_1='RAD', cwe_2='放射科')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700100003')
        obr.universal_service_identifier = CWE(cwe_1='30799-1', cwe_2='頭部電腦斷層', cwe_3='LN')
        obr.observation_date_time = '20260305023000'
        obr.obr_14 = 'STAT'
        obr.obr_15 = 'D700100^顏淑美'
        obr.result_status = '1^^^20260305023000^^S'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I63.9', cwe_2='腦梗塞,未明示者', cwe_3='I10')
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
    """ Based on live/tw/tw-philips-intellisite.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IntelliSite')
        msh.sending_facility = HD(hd_1='CATHAY_RAD')
        msh.receiving_application = HD(hd_1='HIS-CATHAY')
        msh.receiving_facility = HD(hd_1='CATHAY_HOSP')
        msh.date_time_of_message = '20260305033000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260305033000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT700100', cx_4='CATHAY_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='段', xpn_2='振宇')
        pid.date_time_of_birth = '19670218'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新北市三重區重新路五段600號', xad_3='新北市', xad_4='24158', xad_5='TW')
        pid.pid_13 = '02-29821234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'C401267893'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ER', pl_2='001', pl_3='03')
        pv1.pv1_7 = 'D700100^顏淑美^^^^^CATHAY_HOSP'
        pv1.visit_number = CX(cx_1='V700100003')
        pv1.diet_type = CWE(cwe_1='CATHAY_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260305020000')

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
        orc.placer_order_number = EI(ei_1='ORD700100003')
        orc.placer_order_group_number = EI(ei_1='FIL700100003')
        orc.parent_order = EIP(eip_1='20260305033000')
        orc.orc_11 = 'D700100^顏淑美'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700100003')
        obr.filler_order_number = EI(ei_1='FIL700100003')
        obr.universal_service_identifier = CWE(cwe_1='30799-1', cwe_2='頭部電腦斷層', cwe_3='LN')
        obr.observation_date_time = '20260305024500'
        obr.obr_16 = 'D700100^顏淑美'
        obr.results_rpt_status_chng_date_time = '20260305033000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='30799-1', cwe_2='頭部電腦斷層報告', cwe_3='LN')
        obx.obx_5 = '檢查所見：右側大腦中動脈供血區可見低密度區，範圍約3x4公分，符合急性缺血性梗塞。中線結構無偏移。腦室系統正常。'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='30799-1', cwe_2='頭部電腦斷層報告', cwe_3='LN')
        obx_2.obx_5 = '結論：右側大腦中動脈區急性缺血性梗塞，建議緊急神經內科處置。'
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
    """ Based on live/tw/tw-philips-intellisite.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-CATHAY')
        msh.sending_facility = HD(hd_1='CATHAY_HOSP')
        msh.receiving_application = HD(hd_1='IntelliSite')
        msh.receiving_facility = HD(hd_1='CATHAY_RAD')
        msh.date_time_of_message = '20260305040000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20260305040000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260305040000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT700100', cx_4='CATHAY_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='段', xpn_2='振宇')
        pid.date_time_of_birth = '19670218'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新北市三重區重新路五段600號', xad_3='新北市', xad_4='24158', xad_5='TW')
        pid.pid_13 = '02-29821234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'C401267893'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='段周淑華')
        nk1.relationship = CWE(cwe_1='SPO')
        nk1.address = XAD(xad_1='新北市三重區重新路五段600號', xad_3='新北市', xad_4='24158', xad_5='TW')
        nk1.nk1_5 = '02-29821234'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEUR', pl_2='501', pl_3='02')
        pv1.pv1_7 = 'D700100^顏淑美^^^^^CATHAY_HOSP'
        pv1.visit_number = CX(cx_1='V700100004')
        pv1.diet_type = CWE(cwe_1='CATHAY_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260305040000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='NHI')
        in1.insurance_company_id = CX(cx_1='NHI_TW')
        in1.insurance_company_name = XON(xon_1='全民健康保險')
        in1.insureds_address = XAD(xad_1='C401267893')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I63.9', cwe_2='腦梗塞,未明示者', cwe_3='I10')
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
    """ Based on live/tw/tw-philips-intellisite.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-CATHAY')
        msh.sending_facility = HD(hd_1='CATHAY_HOSP')
        msh.receiving_application = HD(hd_1='IntelliSite')
        msh.receiving_facility = HD(hd_1='CATHAY_RAD')
        msh.date_time_of_message = '20260306090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20260306090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT700100', cx_4='CATHAY_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='段', xpn_2='振宇')
        pid.date_time_of_birth = '19670218'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新北市三重區重新路五段600號', xad_3='新北市', xad_4='24158', xad_5='TW')
        pid.pid_13 = '02-29821234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'C401267893'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEUR', pl_2='501', pl_3='02')
        pv1.pv1_7 = 'D700100^顏淑美^^^^^CATHAY_HOSP'
        pv1.visit_number = CX(cx_1='V700100004')
        pv1.diet_type = CWE(cwe_1='CATHAY_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260305040000')

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
        orc.placer_order_number = EI(ei_1='ORD700100004')
        orc.orc_7 = '1^^^20260306100000^^R'
        orc.date_time_of_order_event = '20260306090000'
        orc.orc_10 = 'N700100^護理師唐雅婷'
        orc.orc_11 = 'D700100^顏淑美'
        orc.order_control_code_reason = CWE(cwe_1='RAD', cwe_2='放射科')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700100004')
        obr.universal_service_identifier = CWE(cwe_1='24558-9', cwe_2='腦部磁振造影', cwe_3='LN')
        obr.observation_date_time = '20260306090000'
        obr.obr_15 = 'D700100^顏淑美'
        obr.result_status = '1^^^20260306100000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I63.9', cwe_2='腦梗塞,未明示者', cwe_3='I10')
        dg1.diagnosis_date_time = '20260306'

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
    """ Based on live/tw/tw-philips-intellisite.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IntelliSite')
        msh.sending_facility = HD(hd_1='CATHAY_RAD')
        msh.receiving_application = HD(hd_1='HIS-CATHAY')
        msh.receiving_facility = HD(hd_1='CATHAY_HOSP')
        msh.date_time_of_message = '20260306170000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260306170000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT700100', cx_4='CATHAY_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='段', xpn_2='振宇')
        pid.date_time_of_birth = '19670218'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新北市三重區重新路五段600號', xad_3='新北市', xad_4='24158', xad_5='TW')
        pid.pid_13 = '02-29821234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'C401267893'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEUR', pl_2='501', pl_3='02')
        pv1.pv1_7 = 'D700100^顏淑美^^^^^CATHAY_HOSP'
        pv1.visit_number = CX(cx_1='V700100004')
        pv1.diet_type = CWE(cwe_1='CATHAY_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260305040000')

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
        orc.placer_order_number = EI(ei_1='ORD700100004')
        orc.placer_order_group_number = EI(ei_1='FIL700100004')
        orc.parent_order = EIP(eip_1='20260306170000')
        orc.orc_11 = 'D700100^顏淑美'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700100004')
        obr.filler_order_number = EI(ei_1='FIL700100004')
        obr.universal_service_identifier = CWE(cwe_1='24558-9', cwe_2='腦部磁振造影', cwe_3='LN')
        obr.observation_date_time = '20260306103000'
        obr.obr_16 = 'D700100^顏淑美'
        obr.results_rpt_status_chng_date_time = '20260306170000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='24558-9', cwe_2='腦部磁振造影報告', cwe_3='LN')
        obx.obx_5 = '檢查所見：DWI序列顯示右側大腦中動脈供血區高訊號，ADC map對應低訊號，符合急性缺血性梗塞。FLAIR序列顯示同區域高訊號。無出血性轉化。'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='24558-9', cwe_2='腦部磁振造影報告', cwe_3='LN')
        obx_2.obx_5 = '結論：右側MCA區急性缺血性梗塞，範圍約3x4公分，無出血性轉化。'
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
    """ Based on live/tw/tw-philips-intellisite.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-CATHAY')
        msh.sending_facility = HD(hd_1='CATHAY_HOSP')
        msh.receiving_application = HD(hd_1='IntelliSite')
        msh.receiving_facility = HD(hd_1='CATHAY_RAD')
        msh.date_time_of_message = '20260307090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20260307090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT700100', cx_4='CATHAY_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='段', xpn_2='振宇')
        pid.date_time_of_birth = '19670218'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新北市三重區重新路五段600號', xad_3='新北市', xad_4='24158', xad_5='TW')
        pid.pid_13 = '02-29821234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'C401267893'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEUR', pl_2='501', pl_3='02')
        pv1.pv1_7 = 'D700100^顏淑美^^^^^CATHAY_HOSP'
        pv1.visit_number = CX(cx_1='V700100004')
        pv1.diet_type = CWE(cwe_1='CATHAY_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260305040000')

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
        orc.placer_order_number = EI(ei_1='ORD700100005')
        orc.orc_7 = '1^^^20260307100000^^R'
        orc.date_time_of_order_event = '20260307090000'
        orc.orc_10 = 'N700100^護理師唐雅婷'
        orc.orc_11 = 'D700100^顏淑美'
        orc.order_control_code_reason = CWE(cwe_1='RAD', cwe_2='放射科')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700100005')
        obr.universal_service_identifier = CWE(cwe_1='93880-4', cwe_2='頸動脈超音波', cwe_3='LN')
        obr.observation_date_time = '20260307090000'
        obr.obr_15 = 'D700100^顏淑美'
        obr.result_status = '1^^^20260307100000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I63.9', cwe_2='腦梗塞,未明示者', cwe_3='I10')
        dg1.diagnosis_date_time = '20260307'

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
    """ Based on live/tw/tw-philips-intellisite.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IntelliSite')
        msh.sending_facility = HD(hd_1='CATHAY_RAD')
        msh.receiving_application = HD(hd_1='HIS-CATHAY')
        msh.receiving_facility = HD(hd_1='CATHAY_HOSP')
        msh.date_time_of_message = '20260307143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260307143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT700100', cx_4='CATHAY_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='段', xpn_2='振宇')
        pid.date_time_of_birth = '19670218'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新北市三重區重新路五段600號', xad_3='新北市', xad_4='24158', xad_5='TW')
        pid.pid_13 = '02-29821234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'C401267893'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEUR', pl_2='501', pl_3='02')
        pv1.pv1_7 = 'D700100^顏淑美^^^^^CATHAY_HOSP'
        pv1.visit_number = CX(cx_1='V700100004')
        pv1.diet_type = CWE(cwe_1='CATHAY_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260305040000')

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
        orc.placer_order_number = EI(ei_1='ORD700100005')
        orc.placer_order_group_number = EI(ei_1='FIL700100005')
        orc.parent_order = EIP(eip_1='20260307143000')
        orc.orc_11 = 'D700100^顏淑美'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700100005')
        obr.filler_order_number = EI(ei_1='FIL700100005')
        obr.universal_service_identifier = CWE(cwe_1='93880-4', cwe_2='頸動脈超音波', cwe_3='LN')
        obr.observation_date_time = '20260307103000'
        obr.obr_16 = 'D700100^顏淑美'
        obr.results_rpt_status_chng_date_time = '20260307143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='93880-4', cwe_2='頸動脈超音波報告', cwe_3='LN')
        obx.obx_5 = (
            '檢查所見：雙側頸總動脈內膜中膜厚度正常（右側0.7mm，左側0.6mm）。右側頸內動脈起始處可見一不規則斑塊，管腔狹窄約40%。左側頸內動脈未見明顯狹窄。'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='93880-4', cwe_2='頸動脈超音波報告', cwe_3='LN')
        obx_2.obx_5 = '結論：右側頸內動脈中度狹窄（40%），建議藥物治療及定期追蹤。'
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
    """ Based on live/tw/tw-philips-intellisite.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-CATHAY')
        msh.sending_facility = HD(hd_1='CATHAY_HOSP')
        msh.receiving_application = HD(hd_1='IntelliSite')
        msh.receiving_facility = HD(hd_1='CATHAY_RAD')
        msh.date_time_of_message = '20260312100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG20260312100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260312100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT700100', cx_4='CATHAY_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='段', xpn_2='振宇')
        pid.date_time_of_birth = '19670218'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新北市三重區重新路五段600號', xad_3='新北市', xad_4='24158', xad_5='TW')
        pid.pid_13 = '02-29821234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'C401267893'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEUR', pl_2='501', pl_3='02')
        pv1.pv1_7 = 'D700100^顏淑美^^^^^CATHAY_HOSP'
        pv1.visit_number = CX(cx_1='V700100004')
        pv1.discharged_to_location = DLD(dld_1='01')
        pv1.diet_type = CWE(cwe_1='CATHAY_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260305040000')
        pv1.current_patient_balance = '20260312100000'

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/tw/tw-philips-intellisite.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-CATHAY')
        msh.sending_facility = HD(hd_1='CATHAY_HOSP')
        msh.receiving_application = HD(hd_1='IntelliSite')
        msh.receiving_facility = HD(hd_1='CATHAY_RAD')
        msh.date_time_of_message = '20260313100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20260313100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT700200', cx_4='CATHAY_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='沈', xpn_2='佩珊')
        pid.date_time_of_birth = '19890709'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市汐止區大同路二段168號', xad_3='新北市', xad_4='22161', xad_5='TW')
        pid.pid_13 = '02-26421234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'D512378904'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GYN', pl_2='201', pl_3='01')
        pv1.pv1_7 = 'D700200^柯彥廷^^^^^CATHAY_HOSP'
        pv1.visit_number = CX(cx_1='V700200002')
        pv1.diet_type = CWE(cwe_1='CATHAY_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260313093000')

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
        orc.placer_order_number = EI(ei_1='ORD700200002')
        orc.orc_7 = '1^^^20260313100000^^R'
        orc.date_time_of_order_event = '20260313100000'
        orc.orc_10 = 'N700200^護理師吳芷彤'
        orc.orc_11 = 'D700200^柯彥廷'
        orc.order_control_code_reason = CWE(cwe_1='RAD', cwe_2='放射科')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700200002')
        obr.universal_service_identifier = CWE(cwe_1='76857-5', cwe_2='骨盆腔超音波', cwe_3='LN')
        obr.observation_date_time = '20260313100000'
        obr.obr_15 = 'D700200^柯彥廷'
        obr.result_status = '1^^^20260313100000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='N94.6', cwe_2='痛經,未明示者', cwe_3='I10')
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
    """ Based on live/tw/tw-philips-intellisite.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IntelliSite')
        msh.sending_facility = HD(hd_1='CATHAY_RAD')
        msh.receiving_application = HD(hd_1='HIS-CATHAY')
        msh.receiving_facility = HD(hd_1='CATHAY_HOSP')
        msh.date_time_of_message = '20260313133000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260313133000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT700200', cx_4='CATHAY_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='沈', xpn_2='佩珊')
        pid.date_time_of_birth = '19890709'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市汐止區大同路二段168號', xad_3='新北市', xad_4='22161', xad_5='TW')
        pid.pid_13 = '02-26421234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'D512378904'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GYN', pl_2='201', pl_3='01')
        pv1.pv1_7 = 'D700200^柯彥廷^^^^^CATHAY_HOSP'
        pv1.visit_number = CX(cx_1='V700200002')
        pv1.diet_type = CWE(cwe_1='CATHAY_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260313093000')

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
        orc.placer_order_number = EI(ei_1='ORD700200002')
        orc.placer_order_group_number = EI(ei_1='FIL700200002')
        orc.parent_order = EIP(eip_1='20260313133000')
        orc.orc_11 = 'D700200^柯彥廷'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700200002')
        obr.filler_order_number = EI(ei_1='FIL700200002')
        obr.universal_service_identifier = CWE(cwe_1='76857-5', cwe_2='骨盆腔超音波', cwe_3='LN')
        obr.observation_date_time = '20260313103000'
        obr.obr_16 = 'D700200^柯彥廷'
        obr.results_rpt_status_chng_date_time = '20260313133000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='76857-5', cwe_2='骨盆腔超音波報告', cwe_3='LN')
        obx.obx_5 = '檢查所見：子宮前傾前屈位，大小約8.2x5.1x4.8公分。子宮肌層可見一低回音結節，約2.3公分，位於後壁。雙側卵巢正常，無異常囊腫。'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='76857-5', cwe_2='骨盆腔超音波報告', cwe_3='LN')
        obx_2.obx_5 = '結論：子宮肌瘤（後壁，約2.3公分），建議定期追蹤。'
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
    """ Based on live/tw/tw-philips-intellisite.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-CATHAY')
        msh.sending_facility = HD(hd_1='CATHAY_HOSP')
        msh.receiving_application = HD(hd_1='IntelliSite')
        msh.receiving_facility = HD(hd_1='CATHAY_RAD')
        msh.date_time_of_message = '20260314090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20260314090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260314090000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT700200', cx_4='CATHAY_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='沈', xpn_2='佩珊')
        pid.date_time_of_birth = '19890709'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市汐止區大同路二段168號', xad_3='新北市', xad_4='22161', xad_5='TW')
        pid.pid_13 = '02-26421234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'D512378904'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GYN', pl_2='201', pl_3='01')
        pv1.pv1_7 = 'D700200^柯彥廷^^^^^CATHAY_HOSP'
        pv1.visit_number = CX(cx_1='V700200002')

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/tw/tw-philips-intellisite.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-CATHAY')
        msh.sending_facility = HD(hd_1='CATHAY_HOSP')
        msh.receiving_application = HD(hd_1='IntelliSite')
        msh.receiving_facility = HD(hd_1='CATHAY_RAD')
        msh.date_time_of_message = '20260315090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG20260315090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT700200', cx_4='CATHAY_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='沈', xpn_2='佩珊')
        pid.date_time_of_birth = '19890709'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市汐止區大同路二段168號', xad_3='新北市', xad_4='22161', xad_5='TW')
        pid.pid_13 = '02-26421234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'D512378904'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='IM', pl_2='201', pl_3='01')
        pv1.pv1_7 = 'D700200^柯彥廷^^^^^CATHAY_HOSP'
        pv1.visit_number = CX(cx_1='V700200003')
        pv1.diet_type = CWE(cwe_1='CATHAY_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260315083000')

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
        orc.placer_order_number = EI(ei_1='ORD700200003')
        orc.orc_7 = '1^^^20260315090000^^R'
        orc.date_time_of_order_event = '20260315090000'
        orc.orc_10 = 'N700200^護理師吳芷彤'
        orc.orc_11 = 'D700200^柯彥廷'
        orc.order_control_code_reason = CWE(cwe_1='RAD', cwe_2='放射科')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700200003')
        obr.universal_service_identifier = CWE(cwe_1='38269-7', cwe_2='骨密度檢查', cwe_3='LN')
        obr.observation_date_time = '20260315090000'
        obr.obr_15 = 'D700200^柯彥廷'
        obr.result_status = '1^^^20260315090000^^R'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M81.0', cwe_2='骨質疏鬆症', cwe_3='I10')
        dg1.diagnosis_date_time = '20260315'

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
    """ Based on live/tw/tw-philips-intellisite.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IntelliSite')
        msh.sending_facility = HD(hd_1='CATHAY_RAD')
        msh.receiving_application = HD(hd_1='HIS-CATHAY')
        msh.receiving_facility = HD(hd_1='CATHAY_HOSP')
        msh.date_time_of_message = '20260315143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260315143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT700200', cx_4='CATHAY_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='沈', xpn_2='佩珊')
        pid.date_time_of_birth = '19890709'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市汐止區大同路二段168號', xad_3='新北市', xad_4='22161', xad_5='TW')
        pid.pid_13 = '02-26421234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'D512378904'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='IM', pl_2='201', pl_3='01')
        pv1.pv1_7 = 'D700200^柯彥廷^^^^^CATHAY_HOSP'
        pv1.visit_number = CX(cx_1='V700200003')
        pv1.diet_type = CWE(cwe_1='CATHAY_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260315083000')

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
        orc.placer_order_number = EI(ei_1='ORD700200003')
        orc.placer_order_group_number = EI(ei_1='FIL700200003')
        orc.parent_order = EIP(eip_1='20260315143000')
        orc.orc_11 = 'D700200^柯彥廷'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700200003')
        obr.filler_order_number = EI(ei_1='FIL700200003')
        obr.universal_service_identifier = CWE(cwe_1='38269-7', cwe_2='骨密度檢查', cwe_3='LN')
        obr.observation_date_time = '20260315100000'
        obr.obr_16 = 'D700200^柯彥廷'
        obr.results_rpt_status_chng_date_time = '20260315143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='38265-5', cwe_2='腰椎骨密度T值', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='L1-L4')
        obx.obx_5 = '-1.8'
        obx.units = CWE(cwe_1='g/cm2')
        obx.reference_range = '>-1.0'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='38267-1', cwe_2='髖部骨密度T值', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='Total Hip')
        obx_2.obx_5 = '-1.2'
        obx_2.units = CWE(cwe_1='g/cm2')
        obx_2.reference_range = '>-1.0'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'FT'
        obx_3.observation_identifier = CWE(cwe_1='38269-7', cwe_2='骨密度檢查報告', cwe_3='LN')
        obx_3.obx_5 = '檢查所見：腰椎（L1-L4）T值為-1.8，屬骨質減少範圍。髖部T值為-1.2，屬骨質減少範圍。'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'FT'
        obx_4.observation_identifier = CWE(cwe_1='38269-7', cwe_2='骨密度檢查報告', cwe_3='LN')
        obx_4.obx_5 = '結論：腰椎及髖部骨質減少，建議鈣質補充及定期追蹤。'
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
