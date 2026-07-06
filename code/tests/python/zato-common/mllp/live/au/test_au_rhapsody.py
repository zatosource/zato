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
from zato.hl7v2.v2_9.datatypes import CNE, CQ, CWE, CX, EI, ERL, FC, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA05NextOfKin, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, \
    OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, RspK22QueryResponse, SiuS12Patient
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A03, ADT_A05, MDM_T02, ORM_O01, ORU_R01, QBP_Q21, RSP_K22, SIU_S12
from zato.hl7v2.v2_9.segments import AIG, AIL, DG1, ERR, EVN, IN1, MSA, MSH, NK1, OBR, OBX, ORC, PD1, PID, PV1, QAK, QPD, RCP, RXO, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('au', 'au-rhapsody.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/au/au-rhapsody.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RHAPSODY')
        msh.sending_facility = HD(hd_1='ROYAL_MELBOURNE', hd_2='2340')
        msh.receiving_application = HD(hd_1='HOMER')
        msh.receiving_facility = HD(hd_1='RMH_ADT', hd_2='2340')
        msh.date_time_of_message = '20240315083022'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20240315083000'
        evn.operator_id = XCN(xcn_1='JSMITH', xcn_2='Smith', xcn_3='Jane', xcn_6='Dr')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN123456', cx_4='RMH', cx_5='MR'), CX(cx_1='3245678901', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1="O'Brien", xpn_2='Patrick', xpn_3='James', xpn_5='Mr')
        pid.date_time_of_birth = '19670423'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='42 Collins Street', xad_3='Melbourne', xad_4='VIC', xad_5='3000', xad_6='AU')
        pid.pid_13 = '+61398765432^^^patrick.obrien@email.com.au'
        pid.pid_14 = '+61398765433'
        pid.primary_language = CWE(cwe_1='ENG')
        pid.marital_status = CWE(cwe_1='M')
        pid.religion = CWE(cwe_1='CHR')
        pid.patient_account_number = CX(cx_1='AN00012345')
        pid.mothers_identifier = CX(cx_1='N')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4W', pl_2='412', pl_3='1', pl_4='RMH', pl_8='N')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='DKHAN', xcn_2='Khan', xcn_3='Deepak', xcn_6='Dr', xcn_9='AUSHICPR')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.financial_class = FC(fc_1='PBS')
        pv1.servicing_facility = CWE(cwe_1='RMH')
        pv1.pv1_40 = 'A'
        pv1.prior_temporary_location = PL(pl_1='20240315083000')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1="O'Brien", xpn_2='Margaret', xpn_4='Mrs')
        nk1.relationship = CWE(cwe_1='SPO')
        nk1.address = XAD(xad_1='42 Collins Street', xad_3='Melbourne', xad_4='VIC', xad_5='3000', xad_6='AU')
        nk1.nk1_5 = '+61398765434'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='PBS')
        in1.insurance_company_id = CX(cx_1='PBS', cx_2='Pharmaceutical Benefits Scheme')
        in1.insurance_company_name = XON(xon_1='Medicare Australia')
        in1.name_of_insured = XPN(xpn_1="O'Brien", xpn_2='Patrick', xpn_3='James')
        in1.insureds_relationship_to_patient = CWE(cwe_1='SELF')
        in1.insureds_date_of_birth = '19670423'
        in1.insureds_address = XAD(xad_1='42 Collins Street', xad_3='Melbourne', xad_4='VIC', xad_5='3000', xad_6='AU')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [nk1, in1]

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
    """ Based on live/au/au-rhapsody.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIE')
        msh.sending_facility = HD(hd_1='QLD_HEALTH', hd_2='7890')
        msh.receiving_application = HD(hd_1='HBCIS')
        msh.receiving_facility = HD(hd_1='PAH', hd_2='7890')
        msh.date_time_of_message = '20240412141530'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'QH20240412141530001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20240412141500'
        evn.operator_id = XCN(xcn_1='ADMIN01')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '}1'
        pid.patient_identifier_list = [CX(cx_1='PAH4456789', cx_4='PAH', cx_5='MR'), CX(cx_1='6123456789', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='Williams', xpn_2='Sarah', xpn_3='Louise', xpn_5='Ms')
        pid.date_time_of_birth = '19880912'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='17 Boundary Road', xad_3='South Brisbane', xad_4='QLD', xad_5='4101', xad_6='AU')
        pid.pid_13 = '+61732456789^^^s.williams@health.qld.gov.au'
        pid.religion = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='NON')
        pid.pid_28 = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OPD', pl_2='CLINIC3', pl_3='1', pl_4='PAH', pl_8='N')
        pv1.hospital_service = CWE(cwe_1='GP')
        pv1.admit_source = CWE(cwe_1='2')
        pv1.admitting_doctor = XCN(xcn_1='DLEE', xcn_2='Lee', xcn_3='David', xcn_6='Dr', xcn_9='AUSHICPR')
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.financial_class = FC(fc_1='MBS')
        pv1.servicing_facility = CWE(cwe_1='PAH')
        pv1.pv1_40 = 'A'
        pv1.prior_temporary_location = PL(pl_1='20240412090000')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = 'GPLEE^Lee Family Practice^^^^^AUSHICPR'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [pd1]

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
    """ Based on live/au/au-rhapsody.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RHAPSODY')
        msh.sending_facility = HD(hd_1='WESTMEAD', hd_2='1234')
        msh.receiving_application = HD(hd_1='KARISMA')
        msh.receiving_facility = HD(hd_1='RAD_DEPT', hd_2='1234')
        msh.date_time_of_message = '20240520102345'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'WMH2024052000123'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='WMH789012', cx_4='WMH', cx_5='MR'), CX(cx_1='2198765432', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='Nguyen', xpn_2='Thi Minh', xpn_3='Lan', xpn_5='Mrs')
        pid.date_time_of_birth = '19750301'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='8 Pitt Street', xad_3='Parramatta', xad_4='NSW', xad_5='2150', xad_6='AU')
        pid.pid_13 = '+61296543210'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADOL', pl_2='RAD1', pl_3='1', pl_4='WMH')
        pv1.attending_doctor = XCN(xcn_1='DCHEN', xcn_2='Chen', xcn_3='William', xcn_6='Dr', xcn_9='AUSHICPR')
        pv1.referring_doctor = XCN(xcn_1='RDJONES', xcn_2='Jones', xcn_3='Rebecca', xcn_6='Dr', xcn_9='AUSHICPR')
        pv1.hospital_service = CWE(cwe_1='RAD')
        pv1.admit_source = CWE(cwe_1='3')
        pv1.vip_indicator = CWE(cwe_1='DCHEN', cwe_2='Chen', cwe_3='William', cwe_6='Dr', cwe_9='AUSHICPR')
        pv1.admitting_doctor = XCN(xcn_1='OP')
        pv1.visit_number = CX(cx_1='MBS')

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
        orc.placer_order_number = EI(ei_1='RAD20240520001')
        orc.orc_7 = '^^^20240520103000^^R'
        orc.date_time_of_order_event = '20240520102345'
        orc.orc_10 = 'NSMITH^Smith^Nancy^^^RN'
        orc.enterers_location = PL(pl_1='RADOL', pl_2='RAD1', pl_3='1', pl_4='WMH')
        orc.orc_14 = '+61296540001'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20240520001')
        obr.universal_service_identifier = CWE(cwe_1='XCHEST', cwe_2='Chest Xray PA and Lateral', cwe_3='RADLEX')
        obr.observation_date_time = '20240520103000'
        obr.obr_15 = 'DCHEN^Chen^William^^^Dr^^^AUSHICPR'
        obr.result_status = '1^^^20240520150000^^S'

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
    """ Based on live/au/au-rhapsody.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIE')
        msh.sending_facility = HD(hd_1='DOREVITCH', hd_2='5678')
        msh.receiving_application = HD(hd_1='BEST_PRACTICE')
        msh.receiving_facility = HD(hd_1='GPSITE01', hd_2='5678')
        msh.date_time_of_message = '20240601153012'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'DPL20240601153012001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='DPL345678', cx_4='DPL', cx_5='MR'), CX(cx_1='4567890123', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='Kumar', xpn_2='Rajesh', xpn_3='Anand', xpn_5='Mr')
        pid.date_time_of_birth = '19820715'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='23 Chapel Street', xad_3='St Kilda', xad_4='VIC', xad_5='3182', xad_6='AU')
        pid.pid_13 = '+61395678901'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.attending_doctor = XCN(xcn_1='GPTAYLOR', xcn_2='Taylor', xcn_3='Margaret', xcn_6='Dr', xcn_9='AUSHICPR')

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
        orc.placer_order_number = EI(ei_1='GP2024060100045')
        orc.filler_order_number = EI(ei_1='DPL2024060100045')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20240601'
        orc.orc_10 = 'LABTECH01'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='GP2024060100045')
        obr.filler_order_number = EI(ei_1='DPL2024060100045')
        obr.universal_service_identifier = CWE(cwe_1='FBE', cwe_2='Full Blood Examination', cwe_3='NATA')
        obr.obr_6 = '20240530080000'
        obr.observation_date_time = '20240530081500'
        obr.obr_14 = '20240530081500'
        obr.obr_15 = 'BLD&Blood&HL70070'
        obr.obr_16 = 'GPTAYLOR^Taylor^Margaret^^^Dr^^^AUSHICPR'
        obr.results_rpt_status_chng_date_time = '20240601150000'
        obr.diagnostic_serv_sect_id = 'HM'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='HGB', cwe_2='Haemoglobin', cwe_3='LN')
        obx.obx_5 = '145'
        obx.units = CWE(cwe_1='g/L')
        obx.reference_range = '130-175'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='WBC', cwe_2='White Cell Count', cwe_3='LN')
        obx_2.obx_5 = '7.2'
        obx_2.units = CWE(cwe_1='x10*9/L')
        obx_2.reference_range = '4.0-11.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='PLT', cwe_2='Platelet Count', cwe_3='LN')
        obx_3.obx_5 = '234'
        obx_3.units = CWE(cwe_1='x10*9/L')
        obx_3.reference_range = '150-400'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ED'
        obx_4.observation_identifier = CWE(cwe_1='PDF', cwe_2='Lab Report', cwe_3='LN')
        obx_4.obx_5 = (
            '^application^pdf^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgy'
            'IRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL'
            '/8QAFBABAAAAAAAAAAAAAAAAAAAACf/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AKoA/9k='
        )
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
    """ Based on live/au/au-rhapsody.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RHAPSODY')
        msh.sending_facility = HD(hd_1='RNSH', hd_2='4567')
        msh.receiving_application = HD(hd_1='CERNER')
        msh.receiving_facility = HD(hd_1='RNSH_EMR', hd_2='4567')
        msh.date_time_of_message = '20240618091500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RNSH20240618091500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='RNSH234567', cx_4='RNSH', cx_5='MR'), CX(cx_1='5432109876', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='Fitzgerald', xpn_2='Emma', xpn_3='Rose', xpn_5='Ms')
        pid.date_time_of_birth = '19930208'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='5 Military Road', xad_3='Neutral Bay', xad_4='NSW', xad_5='2089', xad_6='AU')
        pid.pid_13 = '+61294567890'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='6E', pl_2='605', pl_3='1', pl_4='RNSH')
        pv1.attending_doctor = XCN(xcn_1='DWRIGHT', xcn_2='Wright', xcn_3='Thomas', xcn_6='Dr', xcn_9='AUSHICPR')
        pv1.consulting_doctor = XCN(xcn_1='RAD')

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
        orc.placer_order_number = EI(ei_1='RAD20240617001')
        orc.filler_order_number = EI(ei_1='RNSH-RAD-20240617-001')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20240618091500'
        orc.orc_10 = 'RADTECH02'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20240617001')
        obr.filler_order_number = EI(ei_1='RNSH-RAD-20240617-001')
        obr.universal_service_identifier = CWE(cwe_1='XCHEST', cwe_2='Chest Xray', cwe_3='RADLEX')
        obr.obr_6 = '20240617143000'
        obr.observation_date_time = '20240617143500'
        obr.obr_14 = '20240617143500'
        obr.obr_16 = 'DWRIGHT^Wright^Thomas^^^Dr^^^AUSHICPR'
        obr.results_rpt_status_chng_date_time = '20240618090000'
        obr.diagnostic_serv_sect_id = 'RAD'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='RADRPT', cwe_2='Radiology Report', cwe_3='LN')
        obx.obx_5 = 'Heart size normal. Lungs clear. No pleural effusion. No pneumothorax.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='Chest Xray', cwe_3='LN')
        obx_2.obx_5 = (
            '^image^jpeg^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgy'
            'IRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL'
            '/8QAFBABAAAAAAAAAAAAAAAAAAAACf/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AKoA/9k='
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
    """ Based on live/au/au-rhapsody.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIE')
        msh.sending_facility = HD(hd_1='ALFRED', hd_2='3456')
        msh.receiving_application = HD(hd_1='APPOINTMATE')
        msh.receiving_facility = HD(hd_1='ALFRED_SCHED', hd_2='3456')
        msh.date_time_of_message = '20240703090015'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'ALF20240703090015001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT20240703001')
        sch.filler_appointment_id = EI(ei_1='APT20240703001')
        sch.schedule_id = CWE(cwe_1='ROUTINE')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine', cwe_4='ROUTINE', cwe_5='Routine')
        sch.appointment_reason = CWE(cwe_1='REASON', cwe_2='Follow-up consultation', cwe_3='L')
        sch.appointment_type = CWE(cwe_1='NORMAL')
        sch.sch_9 = '30'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^30^20240710093000^20240710100000'
        sch.placer_contact_person = XCN(xcn_1='SBOOK', xcn_2='Booking', xcn_3='Susan', xcn_6='Ms')
        sch.placer_contact_address = XAD(xad_1='+61390001234')
        sch.entered_by_person = XCN(xcn_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='ALF567890', cx_4='ALF', cx_5='MR'), CX(cx_1='7654321098', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='Patel', xpn_2='Anisha', xpn_3='Devi', xpn_5='Ms')
        pid.date_time_of_birth = '19910520'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='101 Commercial Road', xad_3='Prahran', xad_4='VIC', xad_5='3181', xad_6='AU')
        pid.pid_13 = '+61412345678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='CLINIC2', pl_3='1', pl_4='ALF', pl_8='N')
        pv1.hospital_service = CWE(cwe_1='CAR')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='DPATEL', xcn_2='Patel', xcn_3='Suresh', xcn_6='Dr', xcn_9='AUSHICPR')
        pv1.patient_type = CWE(cwe_1='OP')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build AIG ..
        aig = AIG()
        aig.set_id_aig = '1'
        aig.resource_id = CWE(cwe_1='DPATEL', cwe_2='Patel', cwe_3='Suresh', cwe_6='Dr', cwe_9='AUSHICPR')
        aig.resource_type = CWE(cwe_1='CAR', cwe_2='Cardiology', cwe_3='HL70069')

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='CARD', pl_2='CLINIC2', pl_3='1', pl_4='ALF', pl_8='N')
        ail.location_type_ail = CWE(cwe_1='ROOM')

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.extra_segments = [aig, ail]

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
    """ Based on live/au/au-rhapsody.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RHAPSODY')
        msh.sending_facility = HD(hd_1='RAH', hd_2='6789')
        msh.receiving_application = HD(hd_1='OACIS')
        msh.receiving_facility = HD(hd_1='RAH_PAS', hd_2='6789')
        msh.date_time_of_message = '20240715140000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S14', msg_3='SIU_S14')
        msh.message_control_id = 'RAH20240715140000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT20240715002')
        sch.filler_appointment_id = EI(ei_1='APT20240715002')
        sch.schedule_id = CWE(cwe_1='ROUTINE')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine', cwe_4='ROUTINE', cwe_5='Routine')
        sch.appointment_reason = CWE(cwe_1='REASON', cwe_2='Post-operative review', cwe_3='L')
        sch.appointment_type = CWE(cwe_1='NORMAL')
        sch.sch_9 = '45'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^45^20240722100000^20240722104500'
        sch.placer_contact_person = XCN(xcn_1='JMURPHY', xcn_2='Murphy', xcn_3='Jennifer', xcn_6='Ms')
        sch.placer_contact_address = XAD(xad_1='+61882001234')
        sch.entered_by_person = XCN(xcn_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='RAH890123', cx_4='RAH', cx_5='MR'), CX(cx_1='8901234567', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='Thompson', xpn_2='Bruce', xpn_3='William', xpn_5='Mr')
        pid.date_time_of_birth = '19560818'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='14 Rundle Mall', xad_3='Adelaide', xad_4='SA', xad_5='5000', xad_6='AU')
        pid.pid_13 = '+61883456789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ORTH', pl_2='CLINIC1', pl_3='1', pl_4='RAH', pl_8='N')
        pv1.hospital_service = CWE(cwe_1='ORT')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='DMARTIN', xcn_2='Martin', xcn_3='Christopher', xcn_6='Dr', xcn_9='AUSHICPR')
        pv1.patient_type = CWE(cwe_1='OP')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build AIG ..
        aig = AIG()
        aig.set_id_aig = '1'
        aig.resource_id = CWE(cwe_1='DMARTIN', cwe_2='Martin', cwe_3='Christopher', cwe_6='Dr', cwe_9='AUSHICPR')
        aig.resource_type = CWE(cwe_1='ORT', cwe_2='Orthopaedics', cwe_3='HL70069')

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.extra_segments = [aig]

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
    """ Based on live/au/au-rhapsody.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIE')
        msh.sending_facility = HD(hd_1='SCGH', hd_2='2345')
        msh.receiving_application = HD(hd_1='EMR_CENTRAL')
        msh.receiving_facility = HD(hd_1='SCGH_DOC', hd_2='2345')
        msh.date_time_of_message = '20240801110030'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'SCGH20240801110030001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20240801110000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='SCGH456789', cx_4='SCGH', cx_5='MR'), CX(cx_1='1234567890', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='McAllister', xpn_2='Fiona', xpn_3='Grace', xpn_5='Mrs')
        pid.date_time_of_birth = '19780614'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='28 Stirling Highway', xad_3='Nedlands', xad_4='WA', xad_5='6009', xad_6='AU')
        pid.pid_13 = '+61893456789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3N', pl_2='302', pl_3='1', pl_4='SCGH')
        pv1.attending_doctor = XCN(xcn_1='DBROWN', xcn_2='Brown', xcn_3='Andrew', xcn_6='Dr', xcn_9='AUSHICPR')
        pv1.consulting_doctor = XCN(xcn_1='MED')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='Discharge Summary', cwe_3='HL70270')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20240801100000'
        txa.origination_date_time = '20240801110000'
        txa.transcriptionist_code_name = XCN(xcn_1='DBROWN', xcn_2='Brown', xcn_3='Andrew', xcn_6='Dr', xcn_9='AUSHICPR')
        txa.parent_document_number = EI(ei_1='DOC20240801001')
        txa.document_completion_status = 'AU'
        txa.document_availability_status = 'AV'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='DSUM', cwe_2='Discharge Summary', cwe_3='LN')
        obx.obx_5 = (
            'Patient admitted 28/07/2024 with community-acquired pneumonia. Treated with IV amoxicillin/clavulanate. Improved clinically. Discharge on or'
            'al amoxicillin/clavulanate for 5 days. Follow-up with GP in 1 week.'
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
    """ Based on live/au/au-rhapsody.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RHAPSODY')
        msh.sending_facility = HD(hd_1='RBWH', hd_2='8901')
        msh.receiving_application = HD(hd_1='EDMS')
        msh.receiving_facility = HD(hd_1='RBWH_DOCS', hd_2='8901')
        msh.date_time_of_message = '20240812153045'
        msh.message_type = MSG(msg_1='MDM', msg_2='T06', msg_3='MDM_T06')
        msh.message_control_id = 'RBWH20240812153045001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T06'
        evn.recorded_date_time = '20240812153000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='RBWH678901', cx_4='RBWH', cx_5='MR'), CX(cx_1='9012345678', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='Garcia', xpn_2='Isabella', xpn_3='Maria', xpn_5='Ms')
        pid.date_time_of_birth = '19850927'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='45 Coronation Drive', xad_3='Milton', xad_4='QLD', xad_5='4064', xad_6='AU')
        pid.pid_13 = '+61732109876'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='BED4', pl_3='1', pl_4='RBWH')
        pv1.attending_doctor = XCN(xcn_1='DWONG', xcn_2='Wong', xcn_3='Michael', xcn_6='Dr', xcn_9='AUSHICPR')
        pv1.consulting_doctor = XCN(xcn_1='ICU')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='AD', cwe_2='Addendum', cwe_3='HL70270')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20240812150000'
        txa.origination_date_time = '20240812153000'
        txa.transcriptionist_code_name = XCN(xcn_1='DWONG', xcn_2='Wong', xcn_3='Michael', xcn_6='Dr', xcn_9='AUSHICPR')
        txa.parent_document_number = EI(ei_1='DOC20240812002')
        txa.placer_order_number = EI(ei_1='DOC20240810001')
        txa.document_completion_status = 'AU'
        txa.document_availability_status = 'AV'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='ADDENDUM', cwe_2='Clinical Addendum', cwe_3='LN')
        obx.obx_5 = (
            'Addendum to admission note 10/08/2024: CT angiogram performed 12/08/2024 shows no pulmonary embolism. Continue current management plan. Pati'
            'ent improving on non-invasive ventilation.'
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
    """ Based on live/au/au-rhapsody.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HOMER')
        msh.sending_facility = HD(hd_1='RMH_ADT', hd_2='2340')
        msh.receiving_application = HD(hd_1='RHAPSODY')
        msh.receiving_facility = HD(hd_1='ROYAL_MELBOURNE', hd_2='2340')
        msh.date_time_of_message = '20240315083025'
        msh.message_type = MSG(msg_1='ACK', msg_2='A01', msg_3='ACK')
        msh.message_control_id = 'ACK00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'MSG00001'
        msa.expected_sequence_number = '0'

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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
    """ Based on live/au/au-rhapsody.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KARISMA')
        msh.sending_facility = HD(hd_1='RAD_DEPT', hd_2='1234')
        msh.receiving_application = HD(hd_1='RHAPSODY')
        msh.receiving_facility = HD(hd_1='WESTMEAD', hd_2='1234')
        msh.date_time_of_message = '20240520102400'
        msh.message_type = MSG(msg_1='ACK', msg_2='O01', msg_3='ACK')
        msh.message_control_id = 'ACK00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AE'
        msa.message_control_id = 'WMH2024052000123'
        msa.expected_sequence_number = '207'

        # .. build ERR ..
        err = ERR()
        err.err_1 = '^^^207^Application internal error&HL70357'
        err.error_location = ERL(erl_1='PID', erl_2='1', erl_3='3')
        err.hl7_error_code = CWE(cwe_1='101', cwe_2='Required field missing', cwe_3='HL70357')
        err.severity = 'E'
        err.user_message = 'Patient identifier not found in master index'

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa
        msg.err = err

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
    """ Based on live/au/au-rhapsody.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIE')
        msh.sending_facility = HD(hd_1='RPAH', hd_2='5432')
        msh.receiving_application = HD(hd_1='POWERCHART')
        msh.receiving_facility = HD(hd_1='RPAH_EMR', hd_2='5432')
        msh.date_time_of_message = '20240905081500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A04')
        msh.message_control_id = 'RPAH20240905081500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20240905081500'
        evn.operator_id = XCN(xcn_1='REG001')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='RPAH123456', cx_4='RPAH', cx_5='MR'), CX(cx_1='2345678901', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='Campbell', xpn_2='Heather', xpn_3='Ann', xpn_5='Mrs')
        pid.date_time_of_birth = '19630312'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='7 King Street', xad_3='Newtown', xad_4='NSW', xad_5='2042', xad_6='AU')
        pid.pid_13 = '+61295671234'
        pid.marital_status = CWE(cwe_1='M')
        pid.religion = CWE(cwe_1='ANG')
        pid.veterans_military_status = CWE(cwe_1='N')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='DERM', pl_2='CLINIC1', pl_3='1', pl_4='RPAH', pl_8='N')
        pv1.hospital_service = CWE(cwe_1='DER')
        pv1.admit_source = CWE(cwe_1='2')
        pv1.admitting_doctor = XCN(xcn_1='DJONES', xcn_2='Jones', xcn_3='Patricia', xcn_6='Dr', xcn_9='AUSHICPR')
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.financial_class = FC(fc_1='MBS')
        pv1.servicing_facility = CWE(cwe_1='RPAH')
        pv1.pv1_40 = 'A'
        pv1.prior_temporary_location = PL(pl_1='20240905081500')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = 'GPMURPHY^Murphy Street Medical^^^^^AUSHICPR'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Campbell', xpn_2='Robert', xpn_4='Mr')
        nk1.relationship = CWE(cwe_1='SPO')
        nk1.address = XAD(xad_1='7 King Street', xad_3='Newtown', xad_4='NSW', xad_5='2042', xad_6='AU')
        nk1.nk1_5 = '+61295671235'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [pd1, nk1]

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
    """ Based on live/au/au-rhapsody.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RHAPSODY')
        msh.sending_facility = HD(hd_1='AUSTIN', hd_2='7890')
        msh.receiving_application = HD(hd_1='AUSLAB')
        msh.receiving_facility = HD(hd_1='AUSTIN_PATH', hd_2='7890')
        msh.date_time_of_message = '20240918143000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'AUS20240918143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='AUS345678', cx_4='AUS', cx_5='MR'), CX(cx_1='3456789012', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='Dawson', xpn_2='Craig', xpn_3='Michael', xpn_5='Mr')
        pid.date_time_of_birth = '19790605'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='92 Bell Street', xad_3='Heidelberg', xad_4='VIC', xad_5='3084', xad_6='AU')
        pid.pid_13 = '+61394561234'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='5S', pl_2='508', pl_3='1', pl_4='AUS')
        pv1.attending_doctor = XCN(xcn_1='DSINHA', xcn_2='Sinha', xcn_3='Priya', xcn_6='Dr', xcn_9='AUSHICPR')
        pv1.consulting_doctor = XCN(xcn_1='MED')
        pv1.re_admission_indicator = CWE(cwe_1='1')

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
        orc.placer_order_number = EI(ei_1='PATH20240918001')
        orc.orc_7 = '^^^20240918150000^^R'
        orc.date_time_of_order_event = '20240918143000'
        orc.orc_10 = 'NWILSON^Wilson^Natalie^^^RN'
        orc.enterers_location = PL(pl_1='5S', pl_2='508', pl_3='1', pl_4='AUS')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PATH20240918001')
        obr.universal_service_identifier = CWE(cwe_1='FBE', cwe_2='Full Blood Examination', cwe_3='NATA')
        obr.observation_date_time = '20240918150000'
        obr.specimen_action_code = 'N'
        obr.obr_16 = 'DSINHA^Sinha^Priya^^^Dr^^^AUSHICPR'

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
        obr_2.placer_order_number = EI(ei_1='PATH20240918001')
        obr_2.universal_service_identifier = CWE(cwe_1='UEC', cwe_2='Urea Electrolytes Creatinine', cwe_3='NATA')
        obr_2.observation_date_time = '20240918150000'
        obr_2.specimen_action_code = 'N'
        obr_2.obr_16 = 'DSINHA^Sinha^Priya^^^Dr^^^AUSHICPR'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='PATH20240918001')
        obr_3.universal_service_identifier = CWE(cwe_1='LFT', cwe_2='Liver Function Tests', cwe_3='NATA')
        obr_3.observation_date_time = '20240918150000'
        obr_3.specimen_action_code = 'N'
        obr_3.obr_16 = 'DSINHA^Sinha^Priya^^^Dr^^^AUSHICPR'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3]

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
    """ Based on live/au/au-rhapsody.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIE')
        msh.sending_facility = HD(hd_1='MELBOURNE_PATH', hd_2='3456')
        msh.receiving_application = HD(hd_1='MEDICAL_DIRECTOR')
        msh.receiving_facility = HD(hd_1='GPSITE02', hd_2='3456')
        msh.date_time_of_message = '20241002120000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MP20241002120000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MP901234', cx_4='MP', cx_5='MR'), CX(cx_1='4567890123', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='Andersen', xpn_2='Lars', xpn_3='Erik', xpn_5='Mr')
        pid.date_time_of_birth = '19880219'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='55 Lygon Street', xad_3='Carlton', xad_4='VIC', xad_5='3053', xad_6='AU')
        pid.pid_13 = '+61393456789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.attending_doctor = XCN(xcn_1='GPREDDY', xcn_2='Reddy', xcn_3='Vikram', xcn_6='Dr', xcn_9='AUSHICPR')

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
        orc.placer_order_number = EI(ei_1='GP2024100200012')
        orc.filler_order_number = EI(ei_1='MP2024100200012')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20241002'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='GP2024100200012')
        obr.filler_order_number = EI(ei_1='MP2024100200012')
        obr.universal_service_identifier = CWE(cwe_1='UCMCS', cwe_2='Urine MCS', cwe_3='NATA')
        obr.obr_6 = '20240930100000'
        obr.observation_date_time = '20240930101000'
        obr.obr_14 = '20240930101000'
        obr.obr_15 = 'UR&Urine&HL70070'
        obr.obr_16 = 'GPREDDY^Reddy^Vikram^^^Dr^^^AUSHICPR'
        obr.results_rpt_status_chng_date_time = '20241002110000'
        obr.diagnostic_serv_sect_id = 'MB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='MICRO', cwe_2='Microscopy', cwe_3='LN')
        obx.obx_5 = 'WBC >100 x10*6/L. RBC 10-50 x10*6/L. Epithelial cells <10 x10*6/L.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='CULT', cwe_2='Culture', cwe_3='LN')
        obx_2.obx_5 = 'Escherichia coli - heavy growth'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'TX'
        obx_3.observation_identifier = CWE(cwe_1='SENS', cwe_2='Sensitivities', cwe_3='LN')
        obx_3.obx_5 = 'Amoxicillin: R, Trimethoprim: R, Nitrofurantoin: S, Cefalexin: S, Norfloxacin: S'
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
    """ Based on live/au/au-rhapsody.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RHAPSODY')
        msh.sending_facility = HD(hd_1='MONASH', hd_2='4567')
        msh.receiving_application = HD(hd_1='PIX_MGR')
        msh.receiving_facility = HD(hd_1='MONASH_MPI', hd_2='4567')
        msh.date_time_of_message = '20241015094500'
        msh.message_type = MSG(msg_1='QBP', msg_2='Q22', msg_3='QBP_Q21')
        msh.message_control_id = 'MON20241015094500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build QPD ..
        qpd = QPD()
        qpd.message_query_name = CWE(cwe_1='Q22', cwe_2='Find Candidates', cwe_3='HL7nnnn')
        qpd.query_tag = 'Q1015001'
        qpd.qpd_3 = '@PID.5.1^Henderson~@PID.7^19850401~@PID.8^F'

        # .. build RCP ..
        rcp = RCP()
        rcp.query_priority = 'I'
        rcp.quantity_limited_request = CQ(cq_1='10', cq_2='RD')

        # .. assemble the full message ..
        msg = QBP_Q21()
        msg.msh = msh
        msg.qpd = qpd
        msg.rcp = rcp

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
    """ Based on live/au/au-rhapsody.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PIX_MGR')
        msh.sending_facility = HD(hd_1='MONASH_MPI', hd_2='4567')
        msh.receiving_application = HD(hd_1='RHAPSODY')
        msh.receiving_facility = HD(hd_1='MONASH', hd_2='4567')
        msh.date_time_of_message = '20241015094502'
        msh.message_type = MSG(msg_1='RSP', msg_2='K22', msg_3='RSP_K22')
        msh.message_control_id = 'MON20241015094502001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'MON20241015094500001'

        # .. build QAK ..
        qak = QAK()
        qak.query_tag = 'Q1015001'
        qak.query_response_status = 'OK'
        qak.message_query_name = CWE(cwe_1='Q22', cwe_2='Find Candidates', cwe_3='HL7nnnn')
        qak.hit_count_total = '1'

        # .. build QPD ..
        qpd = QPD()
        qpd.message_query_name = CWE(cwe_1='Q22', cwe_2='Find Candidates', cwe_3='HL7nnnn')
        qpd.query_tag = 'Q1015001'
        qpd.qpd_3 = '@PID.5.1^Henderson~@PID.7^19850401~@PID.8^F'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MON789012', cx_4='MON', cx_5='MR'), CX(cx_1='5678901234', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='Henderson', xpn_2='Claire', xpn_3='Elizabeth', xpn_5='Ms')
        pid.date_time_of_birth = '19850401'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='33 Dandenong Road', xad_3='Caulfield', xad_4='VIC', xad_5='3162', xad_6='AU')
        pid.pid_13 = '+61395432100'

        # .. build the QUERY_RESPONSE group ..
        query_response = RspK22QueryResponse()
        query_response.pid = pid

        # .. assemble the full message ..
        msg = RSP_K22()
        msg.msh = msh
        msg.msa = msa
        msg.qak = qak
        msg.qpd = qpd
        msg.query_response = query_response

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
    """ Based on live/au/au-rhapsody.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIE')
        msh.sending_facility = HD(hd_1='BOX_HILL', hd_2='6789')
        msh.receiving_application = HD(hd_1='IPMS')
        msh.receiving_facility = HD(hd_1='EASTERN_HEALTH', hd_2='6789')
        msh.date_time_of_message = '20241101163000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'EH20241101163000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20241101163000'
        evn.operator_id = XCN(xcn_1='DHOWARD', xcn_2='Howard', xcn_3='Steven', xcn_6='Dr')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='BXH234567', cx_4='BXH', cx_5='MR'), CX(cx_1='6789012345', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='Jackson', xpn_2='Timothy', xpn_3='James', xpn_5='Mr')
        pid.date_time_of_birth = '19710830'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='19 Whitehorse Road', xad_3='Box Hill', xad_4='VIC', xad_5='3128', xad_6='AU')
        pid.pid_13 = '+61398901234'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3W', pl_2='315', pl_3='1', pl_4='BXH', pl_8='N')
        pv1.consulting_doctor = XCN(xcn_1='MED')
        pv1.re_admission_indicator = CWE(cwe_1='1')
        pv1.vip_indicator = CWE(cwe_1='DHOWARD', cwe_2='Howard', cwe_3='Steven', cwe_6='Dr', cwe_9='AUSHICPR')
        pv1.admitting_doctor = XCN(xcn_1='IP')
        pv1.visit_number = CX(cx_1='MBS')
        pv1.diet_type = CWE(cwe_1='BXH')
        pv1.servicing_facility = CWE(cwe_1='A')
        pv1.pending_location = PL(pl_1='20241028090000')
        pv1.prior_temporary_location = PL(pl_1='20241101160000')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I10', cwe_2='Essential hypertension', cwe_3='ICD10AM')
        dg1.diagnosis_type = CWE(cwe_1='F')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.dg1_2 = 'I10'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='J18.9', cwe_2='Pneumonia unspecified', cwe_3='ICD10AM')
        dg1_2.diagnosis_type = CWE(cwe_1='F')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = [dg1, dg1_2]

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
    """ Based on live/au/au-rhapsody.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RHAPSODY')
        msh.sending_facility = HD(hd_1='FLINDERS', hd_2='8901')
        msh.receiving_application = HD(hd_1='PHARMACY')
        msh.receiving_facility = HD(hd_1='FMC_PHARM', hd_2='8901')
        msh.date_time_of_message = '20241115091500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'FMC20241115091500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='FMC456789', cx_4='FMC', cx_5='MR'), CX(cx_1='7890123456', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='Robinson', xpn_2='Karen', xpn_3='Marie', xpn_5='Mrs')
        pid.date_time_of_birth = '19640722'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='61 South Road', xad_3='Bedford Park', xad_4='SA', xad_5='5042', xad_6='AU')
        pid.pid_13 = '+61882345678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4E', pl_2='401', pl_3='1', pl_4='FMC')
        pv1.attending_doctor = XCN(xcn_1='DWHITE', xcn_2='White', xcn_3='Jonathan', xcn_6='Dr', xcn_9='AUSHICPR')
        pv1.consulting_doctor = XCN(xcn_1='MED')
        pv1.re_admission_indicator = CWE(cwe_1='1')

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
        orc.placer_order_number = EI(ei_1='PHARM20241115001')
        orc.orc_7 = '^^^20241115100000^^R'
        orc.date_time_of_order_event = '20241115091500'
        orc.orc_10 = 'JBAKER^Baker^Julie^^^RN'
        orc.enterers_location = PL(pl_1='4E', pl_2='401', pl_3='1', pl_4='FMC')

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='AMT', cwe_2='21415011000036108', cwe_3='Amoxicillin 500 mg capsule', cwe_4='AMT')
        rxo.requested_give_amount_minimum = '500'
        rxo.requested_give_amount_maximum = 'mg'
        rxo.requested_dosage_form = CWE(cwe_1='ORAL')
        rxo.providers_pharmacy_treatment_instructions = CWE(cwe_1='PO')
        rxo.requested_dispense_code = CWE(cwe_1='3')
        rxo.requested_dispense_units = CWE(cwe_1='caps')
        rxo.requested_give_strength_units = CWE(cwe_1='QID')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [rxo]

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
    """ Based on live/au/au-rhapsody.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIE')
        msh.sending_facility = HD(hd_1='SYDPATH', hd_2='2345')
        msh.receiving_application = HD(hd_1='GENIE')
        msh.receiving_facility = HD(hd_1='GPSITE03', hd_2='2345')
        msh.date_time_of_message = '20241201080000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SP20241201080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='SP567890', cx_4='SP', cx_5='MR'), CX(cx_1='8901234567', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='Taylor', xpn_2='Michelle', xpn_3='Louise', xpn_5='Ms')
        pid.date_time_of_birth = '19920317'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='12 Oxford Street', xad_3='Paddington', xad_4='NSW', xad_5='2021', xad_6='AU')
        pid.pid_13 = '+61293456789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.attending_doctor = XCN(xcn_1='GPCHEN', xcn_2='Chen', xcn_3='Li', xcn_6='Dr', xcn_9='AUSHICPR')

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
        orc.placer_order_number = EI(ei_1='GP2024120100034')
        orc.filler_order_number = EI(ei_1='SP2024120100034')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20241201'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='GP2024120100034')
        obr.filler_order_number = EI(ei_1='SP2024120100034')
        obr.universal_service_identifier = CWE(cwe_1='TFT', cwe_2='Thyroid Function Tests', cwe_3='NATA')
        obr.obr_6 = '20241129090000'
        obr.observation_date_time = '20241129091000'
        obr.obr_14 = '20241129091000'
        obr.obr_15 = 'BLD&Blood&HL70070'
        obr.obr_16 = 'GPCHEN^Chen^Li^^^Dr^^^AUSHICPR'
        obr.results_rpt_status_chng_date_time = '20241201070000'
        obr.diagnostic_serv_sect_id = 'CH'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='TSH', cwe_2='Thyroid Stimulating Hormone', cwe_3='LN')
        obx.obx_5 = '2.35'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.40-4.00'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='FT4', cwe_2='Free T4', cwe_3='LN')
        obx_2.obx_5 = '14.2'
        obx_2.units = CWE(cwe_1='pmol/L')
        obx_2.reference_range = '9.0-19.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='FT3', cwe_2='Free T3', cwe_3='LN')
        obx_3.obx_5 = '4.8'
        obx_3.units = CWE(cwe_1='pmol/L')
        obx_3.reference_range = '2.6-6.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/au/au-rhapsody.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RHAPSODY')
        msh.sending_facility = HD(hd_1='WA_HEALTH', hd_2='9012')
        msh.receiving_application = HD(hd_1='TOPAS')
        msh.receiving_facility = HD(hd_1='WAHMPI', hd_2='9012')
        msh.date_time_of_message = '20241218141500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A28')
        msh.message_control_id = 'WAH20241218141500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AU'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20241218141500'
        evn.operator_id = XCN(xcn_1='SYSADMIN')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='WAHMPI890123', cx_4='WAHMPI', cx_5='MR'),
            CX(cx_1='9012345678', cx_4='AUSHIC', cx_5='MC'),
            CX(cx_1='WAHAU890123', cx_4='WAHAU', cx_5='PI'),
        ]
        pid.patient_name = XPN(xpn_1='Stewart', xpn_2='Megan', xpn_3='Elizabeth', xpn_5='Dr')
        pid.date_time_of_birth = '19830910'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='4 St Georges Terrace', xad_3='Perth', xad_4='WA', xad_5='6000', xad_6='AU')
        pid.pid_13 = '+61892345678^^^m.stewart@westnet.com.au'
        pid.religion = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='NON')
        pid.pid_28 = 'N'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = 'GPWILSON^Wilson Medical Centre^^^^^AUSHICPR'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Stewart', xpn_2='David', xpn_4='Mr')
        nk1.relationship = CWE(cwe_1='FTH')
        nk1.address = XAD(xad_1='4 St Georges Terrace', xad_3='Perth', xad_4='WA', xad_5='6000', xad_6='AU')
        nk1.nk1_5 = '+61892345679'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin

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
