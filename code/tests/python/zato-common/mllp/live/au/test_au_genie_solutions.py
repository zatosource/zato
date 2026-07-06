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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, EI, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, AdtA03Procedure, AdtA05Insurance, AdtA05NextOfKin, MdmT02Observation, OruR01CommonOrder, \
    OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, RefI12ProviderContact
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A03, ADT_A05, MDM_T02, ORU_R01, REF_I12
from zato.hl7v2.v2_9.segments import DG1, EVN, IN1, IN2, MSH, NK1, NTE, OBR, OBX, ORC, PID, PR1, PRD, PV1, RF1, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('au', 'au-genie-solutions.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/au/au-genie-solutions.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='QMLLIS')
        msh.sending_facility = HD(hd_1='QML', hd_2='2184', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='GENIE')
        msh.receiving_facility = HD(hd_1='SMITH_MEDICAL')
        msh.date_time_of_message = '20240315083000+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PA12345678', cx_4='QML', cx_5='MR')
        pid.patient_name = XPN(xpn_1='JONES', xpn_2='MARGARET', xpn_3='ANNE', xpn_5='MRS')
        pid.date_time_of_birth = '19580423'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='14 Jacaranda Drive', xad_3='TOOWOOMBA', xad_4='QLD', xad_5='4350', xad_6='AUS')
        pid.pid_13 = '0746551234'
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '4567890123'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='SMITH MEDICAL CENTRE')
        pv1.attending_doctor = XCN(xcn_1='0455678G', xcn_2='SMITH', xcn_3='DAVID', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V00012345')
        pv1.prior_temporary_location = PL(pl_1='20240315')

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
        orc.placer_order_number = EI(ei_1='ORD789012')
        orc.filler_order_number = EI(ei_1='QML240315001')
        orc.order_status = 'CM'
        orc.orc_12 = '0455678G^SMITH^DAVID^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD789012')
        obr.filler_order_number = EI(ei_1='QML240315001')
        obr.universal_service_identifier = CWE(cwe_1='26604007', cwe_2='Full Blood Count', cwe_3='SCT')
        obr.observation_date_time = '20240314120000+1000'
        obr.obr_16 = '0455678G^SMITH^DAVID^^^DR'
        obr.results_rpt_status_chng_date_time = '20240315080000+1000'
        obr.diagnostic_serv_sect_id = 'HM'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Haemoglobin', cwe_3='LN')
        obx.obx_5 = '128'
        obx.units = CWE(cwe_1='g/L')
        obx.reference_range = '115-165'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240315080000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6690-2', cwe_2='White Cell Count', cwe_3='LN')
        obx_2.obx_5 = '7.2'
        obx_2.obx_6 = 'x10\\S\\9/L'
        obx_2.reference_range = '4.0-11.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240315080000+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='777-3', cwe_2='Platelet Count', cwe_3='LN')
        obx_3.obx_5 = '245'
        obx_3.obx_6 = 'x10\\S\\9/L'
        obx_3.reference_range = '150-400'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240315080000+1000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='789-8', cwe_2='Red Cell Count', cwe_3='LN')
        obx_4.obx_5 = '4.35'
        obx_4.obx_6 = 'x10\\S\\12/L'
        obx_4.reference_range = '3.80-5.20'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240315080000+1000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Haematocrit', cwe_3='LN')
        obx_5.obx_5 = '0.39'
        obx_5.units = CWE(cwe_1='L/L')
        obx_5.reference_range = '0.36-0.46'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20240315080000+1000'

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
    """ Based on live/au/au-genie-solutions.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SNPLIS')
        msh.sending_facility = HD(hd_1='SNP', hd_2='2199', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='GENIE_SOLUTIONS')
        msh.receiving_facility = HD(hd_1='GREENSLOPES_SPEC')
        msh.date_time_of_message = '20240402141500+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PT99887766', cx_4='SNP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='CHEN', xpn_2='WILLIAM', xpn_3='LEE', xpn_5='MR')
        pid.date_time_of_birth = '19710915'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='88 Boundary Street', xad_3='SPRING HILL', xad_4='QLD', xad_5='4000', xad_6='AUS')
        pid.pid_13 = '0732211456'
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '1234567890'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='GREENSLOPES SPECIALISTS')
        pv1.attending_doctor = XCN(xcn_1='0412345H', xcn_2='WONG', xcn_3='JENNIFER', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V00056789')
        pv1.prior_temporary_location = PL(pl_1='20240402')

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
        orc.placer_order_number = EI(ei_1='ORD456789')
        orc.filler_order_number = EI(ei_1='SNP240402001')
        orc.order_status = 'CM'
        orc.orc_12 = '0412345H^WONG^JENNIFER^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD456789')
        obr.filler_order_number = EI(ei_1='SNP240402001')
        obr.universal_service_identifier = CWE(cwe_1='26958000', cwe_2='Liver Function Tests', cwe_3='SCT')
        obr.observation_date_time = '20240401093000+1000'
        obr.obr_16 = '0412345H^WONG^JENNIFER^^^DR'
        obr.results_rpt_status_chng_date_time = '20240402140000+1000'
        obr.diagnostic_serv_sect_id = 'CH'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT', cwe_3='LN')
        obx.obx_5 = '89'
        obx.units = CWE(cwe_1='U/L')
        obx.reference_range = '<41'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240402140000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST', cwe_3='LN')
        obx_2.obx_5 = '52'
        obx_2.units = CWE(cwe_1='U/L')
        obx_2.reference_range = '<40'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240402140000+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6768-6', cwe_2='ALP', cwe_3='LN')
        obx_3.obx_5 = '95'
        obx_3.units = CWE(cwe_1='U/L')
        obx_3.reference_range = '30-110'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240402140000+1000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1975-2', cwe_2='Bilirubin Total', cwe_3='LN')
        obx_4.obx_5 = '18'
        obx_4.units = CWE(cwe_1='umol/L')
        obx_4.reference_range = '<20'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240402140000+1000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2336-6', cwe_2='GGT', cwe_3='LN')
        obx_5.obx_5 = '78'
        obx_5.units = CWE(cwe_1='U/L')
        obx_5.reference_range = '<60'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20240402140000+1000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2885-2', cwe_2='Total Protein', cwe_3='LN')
        obx_6.obx_5 = '72'
        obx_6.units = CWE(cwe_1='g/L')
        obx_6.reference_range = '60-80'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20240402140000+1000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='1751-7', cwe_2='Albumin', cwe_3='LN')
        obx_7.obx_5 = '38'
        obx_7.units = CWE(cwe_1='g/L')
        obx_7.reference_range = '35-50'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20240402140000+1000'

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
    """ Based on live/au/au-genie-solutions.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GENIE')
        msh.sending_facility = HD(hd_1='RIVERSIDE_MED')
        msh.receiving_application = HD(hd_1='GENIE_SOLUTIONS')
        msh.receiving_facility = HD(hd_1='GASTRO_QLD')
        msh.date_time_of_message = '20240510100000+1000'
        msh.message_type = MSG(msg_1='REF', msg_2='I12', msg_3='REF_I12')
        msh.message_control_id = 'MSG00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build RF1 ..
        rf1 = RF1()
        rf1.referral_status = CWE(cwe_1='SS')
        rf1.referral_priority = CWE(cwe_1='RP')
        rf1.referral_type = CWE(cwe_1='GI', cwe_2='Gastroenterology')
        rf1.referral_disposition = CWE(cwe_1='OP')
        rf1.referral_category = CWE(cwe_1='R')
        rf1.originating_referral_identifier = EI(ei_1='20240510')
        rf1.effective_date = '20240610'
        rf1.process_date = 'Colonoscopy review - family history colorectal carcinoma'

        # .. build PRD ..
        prd = PRD()
        prd.provider_role = CWE(cwe_1='RP')
        prd.provider_name = XPN(xpn_1='SMITH', xpn_2='DAVID', xpn_5='DR')
        prd.provider_address = XAD(xad_1='14 Logan Road', xad_3='WOOLLOONGABBA', xad_4='QLD', xad_5='4102', xad_6='AUS')
        prd.provider_location = PL(pl_4='RIVERSIDE_MED')
        prd.preferred_method_of_contact = CWE(cwe_1='0455678G', cwe_2='AHPRA')

        # .. build the PROVIDER_CONTACT group ..
        provider_contact = RefI12ProviderContact()
        provider_contact.prd = prd

        # .. build PRD ..
        prd_2 = PRD()
        prd_2.provider_role = CWE(cwe_1='RT')
        prd_2.provider_name = XPN(xpn_1='PATEL', xpn_2='RAJESH', xpn_5='DR')
        prd_2.provider_address = XAD(xad_1='Suite 3, 145 Wickham Terrace', xad_3='SPRING HILL', xad_4='QLD', xad_5='4000', xad_6='AUS')
        prd_2.provider_location = PL(pl_4='GASTRO_QLD')
        prd_2.preferred_method_of_contact = CWE(cwe_1='0467890H', cwe_2='AHPRA')

        # .. build the PROVIDER_CONTACT group ..
        provider_contact_2 = RefI12ProviderContact()
        provider_contact_2.prd = prd_2

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='GP789456', cx_4='RIVERSIDE_MED', cx_5='MR')
        pid.patient_name = XPN(xpn_1='BROWN', xpn_2='PETER', xpn_3='JAMES', xpn_5='MR')
        pid.date_time_of_birth = '19650312'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='22 Vulture Street', xad_3='EAST BRISBANE', xad_4='QLD', xad_5='4169', xad_6='AUS')
        pid.pid_13 = '0412987654'
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '3456789012'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K63.5', cwe_2='Polyp of colon', cwe_3='I10AM')
        dg1.diagnosis_type = CWE(cwe_1='W')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = (
            '54 year old male, father diagnosed CRC age 58. Previous colonoscopy 2019 showed two tubular adenomas removed. Due for surveillance. Medicare'
            ' referral attached.'
        )

        # .. assemble the full message ..
        msg = REF_I12()
        msg.msh = msh
        msg.rf1 = rf1
        msg.provider_contact = [provider_contact, provider_contact_2]
        msg.pid = pid
        msg.dg1 = dg1
        msg.nte = nte

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
    """ Based on live/au/au-genie-solutions.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GENIE')
        msh.sending_facility = HD(hd_1='HEART_SPEC_BRIS')
        msh.receiving_application = HD(hd_1='GENIE_SOLUTIONS')
        msh.receiving_facility = HD(hd_1='RECEPTION')
        msh.date_time_of_message = '20240618090000+1000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20240618090000+1000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='CS345678', cx_4='HEART_SPEC', cx_5='MR')
        pid.patient_name = XPN(xpn_1='WILLIAMS', xpn_2='SARAH', xpn_3='LOUISE', xpn_5='MS')
        pid.date_time_of_birth = '19800729'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Unit 4, 67 Coronation Drive', xad_3='AUCHENFLOWER', xad_4='QLD', xad_5='4066', xad_6='AUS')
        pid.pid_13 = '0433876543'
        pid.primary_language = CWE(cwe_1='EN')
        pid.religion = CWE(cwe_1='S')
        pid.pid_20 = '2345678901'
        pid.multiple_birth_indicator = 'AUS'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='WILLIAMS', xpn_2='JAMES', xpn_5='MR')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse')
        nk1.address = XAD(xad_1='67 Coronation Drive', xad_3='AUCHENFLOWER', xad_4='QLD', xad_5='4066', xad_6='AUS')
        nk1.nk1_5 = '0433876544'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='HEART SPECIALISTS BRISBANE')
        pv1.attending_doctor = XCN(xcn_1='0478901G', xcn_2='NGUYEN', xcn_3='THANH', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='CAR')
        pv1.admit_source = CWE(cwe_1='3')
        pv1.admitting_doctor = XCN(xcn_1='0478901G', xcn_2='NGUYEN', xcn_3='THANH', xcn_6='DR')
        pv1.visit_number = CX(cx_1='EC456789')
        pv1.charge_price_indicator = CWE(cwe_1='MC')
        pv1.discharge_date_time = '20240618090000+1000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='MBSA', cwe_2='Medicare Australia')
        in1.insurance_company_id = CX(cx_1='HIC')
        in1.insurance_company_name = XON(xon_1='Medicare Australia')
        in1.name_of_insured = XPN(xpn_1='WILLIAMS', xpn_2='SARAH', xpn_3='LOUISE')
        in1.insureds_relationship_to_patient = CWE(cwe_1='SEL')
        in1.insureds_date_of_birth = '19800729'
        in1.policy_number = '2345678901 1'

        # .. build IN2 ..
        in2 = IN2()
        in2.insureds_employee_id = CX(cx_1='1')
        in2.protection_indicator = 'DVA'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1
        insurance.in2 = in2

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.insurance = insurance

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
    """ Based on live/au/au-genie-solutions.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PATHQLD')
        msh.sending_facility = HD(hd_1='PQ', hd_2='2100', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='GENIESOL')
        msh.receiving_facility = HD(hd_1='NORTH_LAKES_MED')
        msh.date_time_of_message = '20240722153000+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PQ456123', cx_4='PATHQLD', cx_5='MR')
        pid.patient_name = XPN(xpn_1='THOMPSON', xpn_2='KYLIE', xpn_3='MARIE', xpn_5='MRS')
        pid.date_time_of_birth = '19920814'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='31 Discovery Drive', xad_3='NORTH LAKES', xad_4='QLD', xad_5='4509', xad_6='AUS')
        pid.pid_13 = '0734821000'
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '5678901234'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='NORTH LAKES MEDICAL')
        pv1.attending_doctor = XCN(xcn_1='0423456G', xcn_2='MARSHALL', xcn_3='KAREN', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V00098765')
        pv1.prior_temporary_location = PL(pl_1='20240722')

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
        orc.placer_order_number = EI(ei_1='ORD112233')
        orc.filler_order_number = EI(ei_1='PQ240722001')
        orc.order_status = 'CM'
        orc.orc_12 = '0423456G^MARSHALL^KAREN^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD112233')
        obr.filler_order_number = EI(ei_1='PQ240722001')
        obr.universal_service_identifier = CWE(cwe_1='630-4', cwe_2='Urine Culture', cwe_3='LN')
        obr.observation_date_time = '20240721100000+1000'
        obr.obr_16 = '0423456G^MARSHALL^KAREN^^^DR'
        obr.results_rpt_status_chng_date_time = '20240722150000+1000'
        obr.diagnostic_serv_sect_id = 'MB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='630-4', cwe_2='Urine Culture', cwe_3='LN')
        obx.obx_5 = 'Escherichia coli >10\\S\\8 CFU/L'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240722150000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Sensitivity', cwe_3='LN')
        obx_2.obx_5 = 'Amoxicillin: Resistant'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240722150000+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Sensitivity', cwe_3='LN')
        obx_3.obx_5 = 'Trimethoprim: Resistant'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240722150000+1000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Sensitivity', cwe_3='LN')
        obx_4.obx_5 = 'Nitrofurantoin: Sensitive'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240722150000+1000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Sensitivity', cwe_3='LN')
        obx_5.obx_5 = 'Cephalexin: Sensitive'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20240722150000+1000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Sensitivity', cwe_3='LN')
        obx_6.obx_5 = 'Norfloxacin: Sensitive'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20240722150000+1000'

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
    """ Based on live/au/au-genie-solutions.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GENIE_SOLUTIONS')
        msh.sending_facility = HD(hd_1='DERMATOLOGY_QLD')
        msh.receiving_application = HD(hd_1='GENIE')
        msh.receiving_facility = HD(hd_1='SMITH_MEDICAL')
        msh.date_time_of_message = '20240830110000+1000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20240830110000+1000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='DQ112233', cx_4='DERMATOLOGY_QLD', cx_5='MR')
        pid.patient_name = XPN(xpn_1='FITZGERALD', xpn_2='THOMAS', xpn_3='EDWARD', xpn_5='MR')
        pid.date_time_of_birth = '19480605'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='8 Outlook Crescent', xad_3='BARDON', xad_4='QLD', xad_5='4065', xad_6='AUS')
        pid.pid_13 = '0738761234'
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '6789012345'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='DERMATOLOGY QLD')
        pv1.attending_doctor = XCN(xcn_1='0489012G', xcn_2='LEE', xcn_3='MICHAEL', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='DER')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='0489012G', xcn_2='LEE', xcn_3='MICHAEL', xcn_6='DR')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='SP', cwe_2='Specialist Letter')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20240830'
        txa.origination_date_time = '0489012G^LEE^MICHAEL^^^DR'
        txa.unique_document_number = EI(ei_1='DOC89012')
        txa.document_confidentiality_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='SP', cwe_2='Specialist Letter', cwe_3='LN')
        obx.obx_5 = (
            'Dear Dr Smith,\\.br\\\\.br\\Thank you for referring Thomas Fitzgerald for review of multiple solar keratoses on his forearms and scalp.\\.br\\\\.br'
            '\\On examination I identified 12 actinic keratoses on the dorsal forearms and 3 on the vertex of the scalp. I treated these with cryotherapy '
            'today.\\.br\\\\.br\\I have also noted a suspicious 8mm pigmented lesion on his left shoulder which I have performed a shave biopsy of. Histology'
            ' is pending and I will forward results when available.\\.br\\\\.br\\Please review in 3 months for follow-up skin check.\\.br\\\\.br\\Kind regards,\\.'
            'br\\Dr Michael Lee\\.br\\Dermatologist'
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
    """ Based on live/au/au-genie-solutions.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='QMLLIS')
        msh.sending_facility = HD(hd_1='QML', hd_2='2184', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='GENIE')
        msh.receiving_facility = HD(hd_1='IPSWICH_FAMILY_MED')
        msh.date_time_of_message = '20240911092000+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PA55667788', cx_4='QML', cx_5='MR')
        pid.patient_name = XPN(xpn_1='AHMED', xpn_2='FATIMA', xpn_3='ZAHRA', xpn_5='MRS')
        pid.date_time_of_birth = '19670219'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='45 Brisbane Street', xad_3='IPSWICH', xad_4='QLD', xad_5='4305', xad_6='AUS')
        pid.pid_13 = '0734121000'
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '7890123456'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='IPSWICH FAMILY MEDICAL')
        pv1.attending_doctor = XCN(xcn_1='0434567G', xcn_2="O'BRIEN", xcn_3='MICHAEL', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V00034567')
        pv1.prior_temporary_location = PL(pl_1='20240911')

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
        orc.placer_order_number = EI(ei_1='ORD998877')
        orc.filler_order_number = EI(ei_1='QML240911001')
        orc.order_status = 'CM'
        orc.orc_12 = "0434567G^O'BRIEN^MICHAEL^^^DR"

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD998877')
        obr.filler_order_number = EI(ei_1='QML240911001')
        obr.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obr.observation_date_time = '20240910140000+1000'
        obr.obr_16 = "0434567G^O'BRIEN^MICHAEL^^^DR"
        obr.results_rpt_status_chng_date_time = '20240911090000+1000'
        obr.diagnostic_serv_sect_id = 'CH'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obx.obx_5 = '8.2'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '<6.5'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240911090000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='59261-8', cwe_2='HbA1c IFCC', cwe_3='LN')
        obx_2.obx_5 = '66'
        obx_2.units = CWE(cwe_1='mmol/mol')
        obx_2.reference_range = '<48'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240911090000+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='14749-6', cwe_2='Glucose Fasting', cwe_3='LN')
        obx_3.obx_5 = '9.8'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '3.0-5.4'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240911090000+1000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine', cwe_3='LN')
        obx_4.obx_5 = '72'
        obx_4.units = CWE(cwe_1='umol/L')
        obx_4.reference_range = '45-90'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240911090000+1000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='33914-3', cwe_2='eGFR', cwe_3='LN')
        obx_5.obx_5 = '85'
        obx_5.units = CWE(cwe_1='mL/min/1.73m2')
        obx_5.reference_range = '>90'
        obx_5.interpretation_codes = CWE(cwe_1='L')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20240911090000+1000'

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
    """ Based on live/au/au-genie-solutions.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GENIE')
        msh.sending_facility = HD(hd_1='REDCLIFFE_GP')
        msh.receiving_application = HD(hd_1='GENIE_SOLUTIONS')
        msh.receiving_facility = HD(hd_1='CARDIAC_CARE_QLD')
        msh.date_time_of_message = '20240415140000+1000'
        msh.message_type = MSG(msg_1='REF', msg_2='I12', msg_3='REF_I12')
        msh.message_control_id = 'MSG00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build RF1 ..
        rf1 = RF1()
        rf1.referral_status = CWE(cwe_1='SS')
        rf1.referral_priority = CWE(cwe_1='RP')
        rf1.referral_type = CWE(cwe_1='CA', cwe_2='Cardiology')
        rf1.referral_disposition = CWE(cwe_1='OP')
        rf1.referral_category = CWE(cwe_1='U')
        rf1.originating_referral_identifier = EI(ei_1='20240415')
        rf1.effective_date = '20240515'
        rf1.process_date = 'Chest pain on exertion, abnormal ECG - urgent review requested'

        # .. build PRD ..
        prd = PRD()
        prd.provider_role = CWE(cwe_1='RP')
        prd.provider_name = XPN(xpn_1='JACKSON', xpn_2='PETER', xpn_5='DR')
        prd.provider_address = XAD(xad_1='12 Anzac Avenue', xad_3='REDCLIFFE', xad_4='QLD', xad_5='4020', xad_6='AUS')
        prd.provider_location = PL(pl_4='REDCLIFFE_GP')
        prd.preferred_method_of_contact = CWE(cwe_1='0445678G', cwe_2='AHPRA')

        # .. build the PROVIDER_CONTACT group ..
        provider_contact = RefI12ProviderContact()
        provider_contact.prd = prd

        # .. build PRD ..
        prd_2 = PRD()
        prd_2.provider_role = CWE(cwe_1='RT')
        prd_2.provider_name = XPN(xpn_1='KUMAR', xpn_2='ANIL', xpn_5='DR')
        prd_2.provider_address = XAD(xad_1='Level 5, 225 Wickham Terrace', xad_3='SPRING HILL', xad_4='QLD', xad_5='4000', xad_6='AUS')
        prd_2.provider_location = PL(pl_4='CARDIAC_CARE_QLD')
        prd_2.preferred_method_of_contact = CWE(cwe_1='0456789H', cwe_2='AHPRA')

        # .. build the PROVIDER_CONTACT group ..
        provider_contact_2 = RefI12ProviderContact()
        provider_contact_2.prd = prd_2

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='GP334455', cx_4='REDCLIFFE_GP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='MURRAY', xpn_2='ROBERT', xpn_3='JOHN', xpn_5='MR')
        pid.date_time_of_birth = '19560822'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='9 Hornibrook Esplanade', xad_3='CLONTARF', xad_4='QLD', xad_5='4019', xad_6='AUS')
        pid.pid_13 = '0412345678'
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '8901234567'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R07.9', cwe_2='Chest pain, unspecified', cwe_3='I10AM')
        dg1.diagnosis_type = CWE(cwe_1='W')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='R94.31', cwe_2='Abnormal ECG', cwe_3='I10AM')
        dg1_2.diagnosis_type = CWE(cwe_1='W')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = (
            '62 year old male smoker, BMI 32. Exertional chest tightness for 3 weeks. Resting ECG shows ST depression leads V4-V6. Family history: father'
            ' MI age 54. Current medications: Aspirin 100mg daily, Atorvastatin 40mg nocte.'
        )

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='ECG Report', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMg'
            'MCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5'
            'IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo='
        )
        obx.observation_result_status = 'F'

        # .. assemble the full message ..
        msg = REF_I12()
        msg.msh = msh
        msg.rf1 = rf1
        msg.provider_contact = [provider_contact, provider_contact_2]
        msg.pid = pid
        msg.dg1 = [dg1, dg1_2]
        msg.nte = nte
        msg.extra_segments = [obx]

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
    """ Based on live/au/au-genie-solutions.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GENIE')
        msh.sending_facility = HD(hd_1='SOUTHSIDE_ORTHO')
        msh.receiving_application = HD(hd_1='GENIE_SOLUTIONS')
        msh.receiving_facility = HD(hd_1='ADMIN')
        msh.date_time_of_message = '20240203160000+1000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20240203160000+1000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='SO778899', cx_4='SOUTHSIDE_ORTHO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='TAYLOR', xpn_2='JESSICA', xpn_3='ANNE', xpn_5='MS')
        pid.date_time_of_birth = '19850316'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Unit 12, 230 Gladstone Road', xad_3='DUTTON PARK', xad_4='QLD', xad_5='4102', xad_6='AUS')
        pid.pid_13 = '0421987654'
        pid.primary_language = CWE(cwe_1='EN')
        pid.religion = CWE(cwe_1='M')
        pid.pid_20 = '9012345678'
        pid.multiple_birth_indicator = 'AUS'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='TAYLOR', xpn_2='MARK', xpn_5='MR')
        nk1.relationship = CWE(cwe_1='BRO', cwe_2='Brother')
        nk1.address = XAD(xad_1='45 Park Road', xad_3='WOOLLOONGABBA', xad_4='QLD', xad_5='4102', xad_6='AUS')
        nk1.nk1_5 = '0421876543'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='SOUTHSIDE ORTHOPAEDICS')
        pv1.attending_doctor = XCN(xcn_1='0490123G', xcn_2='HARRIS', xcn_3='ANDREW', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='ORT')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='0490123G', xcn_2='HARRIS', xcn_3='ANDREW', xcn_6='DR')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
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
    """ Based on live/au/au-genie-solutions.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SNPLIS')
        msh.sending_facility = HD(hd_1='SNP', hd_2='2199', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='GENIE_SOLUTIONS')
        msh.receiving_facility = HD(hd_1='SUNSHINE_COAST_DERM')
        msh.date_time_of_message = '20240905143000+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PT44551203', cx_4='SNP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='LATU', xpn_2='TEVITA', xpn_3='FILIPE', xpn_5='MR')
        pid.date_time_of_birth = '19510924'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='16 Currimundi Road', xad_3='CALOUNDRA', xad_4='QLD', xad_5='4551', xad_6='AUS')
        pid.pid_13 = '0754910237'
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '6790183245'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='SUNSHINE COAST DERMATOLOGY')
        pv1.attending_doctor = XCN(xcn_1='0497128G', xcn_2='WHARTON', xcn_3='ANGUS', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V00045991')
        pv1.prior_temporary_location = PL(pl_1='20240905')

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
        orc.placer_order_number = EI(ei_1='ORD667081')
        orc.filler_order_number = EI(ei_1='SNP240905201')
        orc.order_status = 'CM'
        orc.orc_12 = '0497128G^WHARTON^ANGUS^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD667081')
        obr.filler_order_number = EI(ei_1='SNP240905201')
        obr.universal_service_identifier = CWE(cwe_1='88305', cwe_2='Surgical Pathology', cwe_3='CPT')
        obr.observation_date_time = '20240830120000+1000'
        obr.obr_16 = '0497128G^WHARTON^ANGUS^^^DR'
        obr.results_rpt_status_chng_date_time = '20240905140000+1000'
        obr.diagnostic_serv_sect_id = 'AP'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='22634-0', cwe_2='Pathology Report', cwe_3='LN')
        obx.obx_5 = (
            'CLINICAL NOTES: Pigmented lesion left shoulder\\.br\\\\.br\\MACROSCOPIC: Shave biopsy of skin, 10x8x2mm, tan-brown pigmented lesion centrally 8m'
            'm diameter.\\.br\\\\.br\\MICROSCOPIC: Sections show a compound melanocytic naevus with mild architectural atypia. No evidence of melanoma. Margi'
            'ns clear. Solar elastosis noted in adjacent dermis.\\.br\\\\.br\\DIAGNOSIS: Compound naevus with mild dysplasia (Clark naevus), left shoulder. E'
            'xcision margins clear.\\.br\\\\.br\\COMMENT: Low risk lesion. Recommend clinical surveillance.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240905140000+1000'

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
    """ Based on live/au/au-genie-solutions.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PATHQLD')
        msh.sending_facility = HD(hd_1='PQ', hd_2='2100', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='GENIE')
        msh.receiving_facility = HD(hd_1='CAIRNS_FAMILY_PRAC')
        msh.date_time_of_message = '20240128101500+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PQ667788', cx_4='PATHQLD', cx_5='MR')
        pid.patient_name = XPN(xpn_1='HANSEN', xpn_2='CRAIG', xpn_3='DAVID', xpn_5='MR')
        pid.date_time_of_birth = '19720430'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='17 Captain Cook Highway', xad_3='TRINITY BEACH', xad_4='QLD', xad_5='4879', xad_6='AUS')
        pid.pid_13 = '0740571200'
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '0123456789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='CAIRNS FAMILY PRACTICE')
        pv1.attending_doctor = XCN(xcn_1='0401234G', xcn_2='WEBB', xcn_3='SUSAN', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V00076543')
        pv1.prior_temporary_location = PL(pl_1='20240128')

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
        orc.placer_order_number = EI(ei_1='ORD334455')
        orc.filler_order_number = EI(ei_1='PQ240128001')
        orc.order_status = 'CM'
        orc.orc_12 = '0401234G^WEBB^SUSAN^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD334455')
        obr.filler_order_number = EI(ei_1='PQ240128001')
        obr.universal_service_identifier = CWE(cwe_1='24331-1', cwe_2='Lipid Panel', cwe_3='LN')
        obr.observation_date_time = '20240127080000+1000'
        obr.obr_16 = '0401234G^WEBB^SUSAN^^^DR'
        obr.results_rpt_status_chng_date_time = '20240128100000+1000'
        obr.diagnostic_serv_sect_id = 'CH'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2093-3', cwe_2='Total Cholesterol', cwe_3='LN')
        obx.obx_5 = '6.8'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '<5.5'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240128100000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2571-8', cwe_2='Triglycerides', cwe_3='LN')
        obx_2.obx_5 = '2.4'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '<2.0'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240128100000+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2085-9', cwe_2='HDL Cholesterol', cwe_3='LN')
        obx_3.obx_5 = '1.0'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '>1.0'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240128100000+1000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='13457-7', cwe_2='LDL Cholesterol', cwe_3='LN')
        obx_4.obx_5 = '4.7'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '<3.5'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240128100000+1000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='9830-1', cwe_2='Total/HDL Ratio', cwe_3='LN')
        obx_5.obx_5 = '6.8'
        obx_5.reference_range = '<4.5'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20240128100000+1000'

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
    """ Based on live/au/au-genie-solutions.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GENIE_SOLUTIONS')
        msh.sending_facility = HD(hd_1='RBWH_GASTRO')
        msh.receiving_application = HD(hd_1='GENIE')
        msh.receiving_facility = HD(hd_1='NORTHSIDE_MED')
        msh.date_time_of_message = '20240712160000+1000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20240712160000+1000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='RBW445566', cx_4='RBWH', cx_5='MR')
        pid.patient_name = XPN(xpn_1="O'CONNOR", xpn_2='BRENDAN', xpn_3='MICHAEL', xpn_5='MR')
        pid.date_time_of_birth = '19680911'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='56 Kedron Brook Road', xad_3='WILSTON', xad_4='QLD', xad_5='4051', xad_6='AUS')
        pid.pid_13 = '0736453000'
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '1234509876'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GASTRO', pl_2='4B', pl_3='12', pl_4='RBWH')
        pv1.attending_doctor = XCN(xcn_1='0401567G', xcn_2='REDDY', xcn_3='SANJAY', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='GAS')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='0401567G', xcn_2='REDDY', xcn_3='SANJAY', xcn_6='DR')
        pv1.visit_number = CX(cx_1='IP778899')
        pv1.charge_price_indicator = CWE(cwe_1='MC')
        pv1.discharge_date_time = '20240708'
        pv1.total_adjustments = '20240712160000+1000'

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='Discharge Summary')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20240712'
        txa.origination_date_time = '0401567G^REDDY^SANJAY^^^DR'
        txa.unique_document_number = EI(ei_1='DOC12345')
        txa.document_confidentiality_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='DS', cwe_2='Discharge Summary', cwe_3='LN')
        obx.obx_5 = (
            "DISCHARGE SUMMARY\\.br\\\\.br\\Admission: 08/07/2024 Discharge: 12/07/2024\\.br\\Admitting Diagnosis: Upper GI haemorrhage\\.br\\\\.br\\SUMMARY: Mr O'"
            'Connor presented with haematemesis and melaena. Hb on admission 78g/L. Received 3 units PRBC. OGD performed 09/07/2024 showing Forrest IIa d'
            'uodenal ulcer with visible vessel, treated with adrenaline injection and bipolar diathermy. H.pylori CLO test positive.\\.br\\\\.br\\DISCHARGE M'
            'EDICATIONS:\\.br\\1. Esomeprazole 40mg BD x 8 weeks\\.br\\2. Amoxicillin 1g BD x 14 days\\.br\\3. Clarithromycin 500mg BD x 14 days\\.br\\\\.br\\FOLLO'
            'W UP: Repeat OGD in 8 weeks. H.pylori breath test 4 weeks post antibiotics. Review with Dr Reddy in 2 weeks.\\.br\\\\.br\\GP actions: Please che'
            'ck FBC in 2 weeks.'
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
    """ Based on live/au/au-genie-solutions.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='QMLLIS')
        msh.sending_facility = HD(hd_1='QML', hd_2='2184', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='GENIE_SOLUTIONS')
        msh.receiving_facility = HD(hd_1='BUNDABERG_HEALTH')
        msh.date_time_of_message = '20240305111000+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PA33445566', cx_4='QML', cx_5='MR')
        pid.patient_name = XPN(xpn_1='PETERSEN', xpn_2='HELEN', xpn_3='RUTH', xpn_5='MRS')
        pid.date_time_of_birth = '19530817'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='23 Bargara Road', xad_3='BUNDABERG', xad_4='QLD', xad_5='4670', xad_6='AUS')
        pid.pid_13 = '0741522000'
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '2345609871'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='BUNDABERG HEALTH CENTRE')
        pv1.attending_doctor = XCN(xcn_1='0412890G', xcn_2='KELLY', xcn_3='FIONA', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V00023456')
        pv1.prior_temporary_location = PL(pl_1='20240305')

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
        orc.placer_order_number = EI(ei_1='ORD776655')
        orc.filler_order_number = EI(ei_1='QML240305001')
        orc.order_status = 'CM'
        orc.orc_12 = '0412890G^KELLY^FIONA^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD776655')
        obr.filler_order_number = EI(ei_1='QML240305001')
        obr.universal_service_identifier = CWE(cwe_1='24348-5', cwe_2='Thyroid Function', cwe_3='LN')
        obr.observation_date_time = '20240304090000+1000'
        obr.obr_16 = '0412890G^KELLY^FIONA^^^DR'
        obr.results_rpt_status_chng_date_time = '20240305110000+1000'
        obr.diagnostic_serv_sect_id = 'CH'
        obr.result_status = 'F'

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
        obx.date_time_of_the_observation = '20240305110000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3024-7', cwe_2='Free T4', cwe_3='LN')
        obx_2.obx_5 = '8.2'
        obx_2.units = CWE(cwe_1='pmol/L')
        obx_2.reference_range = '10.0-20.0'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240305110000+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3053-6', cwe_2='Free T3', cwe_3='LN')
        obx_3.obx_5 = '3.1'
        obx_3.units = CWE(cwe_1='pmol/L')
        obx_3.reference_range = '3.5-6.5'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240305110000+1000'

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
    """ Based on live/au/au-genie-solutions.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GENIE')
        msh.sending_facility = HD(hd_1='SUNNYBANK_DAY_SURG')
        msh.receiving_application = HD(hd_1='GENIE_SOLUTIONS')
        msh.receiving_facility = HD(hd_1='ADMIN')
        msh.date_time_of_message = '20240619153000+1000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20240619153000+1000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='SDS223344', cx_4='SUNNYBANK_DAY', cx_5='MR')
        pid.patient_name = XPN(xpn_1='LIM', xpn_2='GRACE', xpn_3='MEI', xpn_5='MS')
        pid.date_time_of_birth = '19900204'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='88 Hellawell Road', xad_3='SUNNYBANK HILLS', xad_4='QLD', xad_5='4109', xad_6='AUS')
        pid.pid_13 = '0478123456'
        pid.primary_language = CWE(cwe_1='EN')
        pid.religion = CWE(cwe_1='S')
        pid.pid_20 = '3456012789'
        pid.multiple_birth_indicator = 'AUS'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PROC', pl_2='1', pl_3='3', pl_4='SUNNYBANK_DAY')
        pv1.attending_doctor = XCN(xcn_1='0456123G', xcn_2='WONG', xcn_3='DAVID', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='GYN')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='0456123G', xcn_2='WONG', xcn_3='DAVID', xcn_6='DR')
        pv1.visit_number = CX(cx_1='DS889900')
        pv1.charge_price_indicator = CWE(cwe_1='MC')
        pv1.discharge_date_time = '20240619070000+1000'
        pv1.total_adjustments = '20240619153000+1000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='N84.0', cwe_2='Polyp of corpus uteri', cwe_3='I10AM')
        dg1.diagnosis_type = CWE(cwe_1='P')

        # .. build PR1 ..
        pr1 = PR1()
        pr1.set_id_pr1 = '1'
        pr1.procedure_code = CNE(cne_1='68.16', cne_2='Hysteroscopy with polypectomy', cne_3='ACHI')
        pr1.pr1_4 = 'Hysteroscopic polypectomy'
        pr1.procedure_date_time = '20240619093000+1000'
        pr1.pr1_11 = '0456123G^WONG^DAVID^^^DR'

        # .. build the PROCEDURE group ..
        procedure = AdtA03Procedure()
        procedure.pr1 = pr1

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = dg1
        msg.procedure = procedure

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
    """ Based on live/au/au-genie-solutions.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IMEDRIS')
        msh.sending_facility = HD(hd_1='IMED', hd_2='7890', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='GENIE')
        msh.receiving_facility = HD(hd_1='TOOWONG_MED')
        msh.date_time_of_message = '20240425093000+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='IM998877', cx_4='IMED', cx_5='MR')
        pid.patient_name = XPN(xpn_1='KAVANAGH', xpn_2='DECLAN', xpn_3='PATRICK', xpn_5='MR')
        pid.date_time_of_birth = '19780113'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='3 Jephson Street', xad_3='TOOWONG', xad_4='QLD', xad_5='4066', xad_6='AUS')
        pid.pid_13 = '0412654321'
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '4567098123'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='TOOWONG MEDICAL')
        pv1.attending_doctor = XCN(xcn_1='0467234G', xcn_2='RYAN', xcn_3='KATHLEEN', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V00067890')
        pv1.prior_temporary_location = PL(pl_1='20240425')

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
        orc.placer_order_number = EI(ei_1='ORD887766')
        orc.filler_order_number = EI(ei_1='IMED240425001')
        orc.order_status = 'CM'
        orc.orc_12 = '0467234G^RYAN^KATHLEEN^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD887766')
        obr.filler_order_number = EI(ei_1='IMED240425001')
        obr.universal_service_identifier = CWE(cwe_1='76700', cwe_2='US Abdomen Complete', cwe_3='CPT')
        obr.observation_date_time = '20240424140000+1000'
        obr.obr_16 = '0467234G^RYAN^KATHLEEN^^^DR'
        obr.filler_field_2 = '0523456R^TANAKA^YUKI^^^DR'
        obr.results_rpt_status_chng_date_time = '20240425090000+1000'
        obr.diagnostic_serv_sect_id = 'RAD'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='76700', cwe_2='US Abdomen', cwe_3='CPT')
        obx.obx_5 = (
            'ULTRASOUND ABDOMEN\\.br\\\\.br\\CLINICAL NOTES: RUQ pain, raised GGT\\.br\\\\.br\\FINDINGS:\\.br\\Liver: Mildly increased echogenicity consistent with'
            ' hepatic steatosis. No focal lesion. Liver span 16cm.\\.br\\Gallbladder: Multiple mobile gallstones, largest 12mm. No wall thickening or peric'
            'holecystic fluid. CBD 4mm.\\.br\\Pancreas: Normal.\\.br\\Spleen: Normal, 10cm.\\.br\\Kidneys: Normal size and echogenicity bilaterally. No hydrone'
            'phrosis or calculi.\\.br\\Aorta: Normal calibre.\\.br\\\\.br\\IMPRESSION:\\.br\\1. Cholelithiasis without cholecystitis\\.br\\2. Mild hepatic steatosi'
            's\\.br\\\\.br\\Dr Yuki Tanaka, Radiologist'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240425090000+1000'

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
    """ Based on live/au/au-genie-solutions.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GENIE')
        msh.sending_facility = HD(hd_1='TOOWOOMBA_RANGE_MED')
        msh.receiving_application = HD(hd_1='GENIE_SOLUTIONS')
        msh.receiving_facility = HD(hd_1='DOWNS_ENDOCRINOLOGY')
        msh.date_time_of_message = '20240920100000+1000'
        msh.message_type = MSG(msg_1='REF', msg_2='I12', msg_3='REF_I12')
        msh.message_control_id = 'MSG00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build RF1 ..
        rf1 = RF1()
        rf1.referral_status = CWE(cwe_1='SS')
        rf1.referral_priority = CWE(cwe_1='RP')
        rf1.referral_type = CWE(cwe_1='EN', cwe_2='Endocrinology')
        rf1.referral_disposition = CWE(cwe_1='OP')
        rf1.referral_category = CWE(cwe_1='R')
        rf1.originating_referral_identifier = EI(ei_1='20240920')
        rf1.effective_date = '20241120'
        rf1.process_date = 'Poorly controlled T2DM, HbA1c 8.2% despite triple therapy'

        # .. build PRD ..
        prd = PRD()
        prd.provider_role = CWE(cwe_1='RP')
        prd.provider_name = XPN(xpn_1='MCKINNON', xpn_2='DUNCAN', xpn_5='DR')
        prd.provider_address = XAD(xad_1='17 Margaret Street', xad_3='TOOWOOMBA', xad_4='QLD', xad_5='4350', xad_6='AUS')
        prd.provider_location = PL(pl_4='TOOWOOMBA_RANGE_MED')
        prd.preferred_method_of_contact = CWE(cwe_1='0461258G', cwe_2='AHPRA')

        # .. build the PROVIDER_CONTACT group ..
        provider_contact = RefI12ProviderContact()
        provider_contact.prd = prd

        # .. build PRD ..
        prd_2 = PRD()
        prd_2.provider_role = CWE(cwe_1='RT')
        prd_2.provider_name = XPN(xpn_1='VENKATARAMAN', xpn_2='DEEPIKA', xpn_5='DR')
        prd_2.provider_address = XAD(xad_1='Level 1, 102 Hume Street', xad_3='TOOWOOMBA', xad_4='QLD', xad_5='4350', xad_6='AUS')
        prd_2.provider_location = PL(pl_4='DOWNS_ENDOCRINOLOGY')
        prd_2.preferred_method_of_contact = CWE(cwe_1='0479016H', cwe_2='AHPRA')

        # .. build the PROVIDER_CONTACT group ..
        provider_contact_2 = RefI12ProviderContact()
        provider_contact_2.prd = prd_2

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='GP559013', cx_4='TOOWOOMBA_RANGE_MED', cx_5='MR')
        pid.patient_name = XPN(xpn_1='PEROVIC', xpn_2='STANISLAV', xpn_3='MILORAD', xpn_5='MR')
        pid.date_time_of_birth = '19620410'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='34 Holberton Street', xad_3='NEWTOWN', xad_4='QLD', xad_5='4350', xad_6='AUS')
        pid.pid_12 = '^^^^'
        pid.pid_13 = '0746328041'
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '7891046502'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='E11.65', cwe_2='Type 2 diabetes with hyperglycaemia', cwe_3='I10AM')
        dg1.diagnosis_type = CWE(cwe_1='W')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = (
            '62 year old male, T2DM diagnosed 2010. Current HbA1c 8.2% (66 mmol/mol). BMI 34. Current therapy: Metformin 1g BD, Gliclazide MR 120mg mane,'
            ' Empagliflozin 25mg daily. eGFR 85. Requesting consideration for GLP-1 RA or insulin initiation. Pathology attached.'
        )

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Pathology Results', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMg'
            'MCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5'
            'IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo='
        )
        obx.observation_result_status = 'F'

        # .. assemble the full message ..
        msg = REF_I12()
        msg.msh = msh
        msg.rf1 = rf1
        msg.provider_contact = [provider_contact, provider_contact_2]
        msg.pid = pid
        msg.dg1 = dg1
        msg.nte = nte
        msg.extra_segments = [obx]

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
    """ Based on live/au/au-genie-solutions.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SNPLIS')
        msh.sending_facility = HD(hd_1='SNP', hd_2='2199', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='GENIE')
        msh.receiving_facility = HD(hd_1='GOLD_COAST_CARDIO')
        msh.date_time_of_message = '20240811091500+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PT88990011', cx_4='SNP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='HARRISON', xpn_2='WALTER', xpn_3='GEORGE', xpn_5='MR')
        pid.date_time_of_birth = '19430318'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='27 Doreen Drive', xad_3='COOMBABAH', xad_4='QLD', xad_5='4216', xad_6='AUS')
        pid.pid_13 = '0755001234'
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '5670981234'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='GOLD COAST CARDIOLOGY')
        pv1.attending_doctor = XCN(xcn_1='0490567G', xcn_2='ADAMS', xcn_3='STUART', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V00054321')
        pv1.prior_temporary_location = PL(pl_1='20240811')

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
        orc.placer_order_number = EI(ei_1='ORD554433')
        orc.filler_order_number = EI(ei_1='SNP240811001')
        orc.order_status = 'CM'
        orc.orc_12 = '0490567G^ADAMS^STUART^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD554433')
        obr.filler_order_number = EI(ei_1='SNP240811001')
        obr.universal_service_identifier = CWE(cwe_1='5902-2', cwe_2='Coagulation', cwe_3='LN')
        obr.observation_date_time = '20240810073000+1000'
        obr.obr_16 = '0490567G^ADAMS^STUART^^^DR'
        obr.results_rpt_status_chng_date_time = '20240811090000+1000'
        obr.diagnostic_serv_sect_id = 'HM'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='PT INR', cwe_3='LN')
        obx.obx_5 = '3.8'
        obx.reference_range = '2.0-3.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240811090000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='5964-2', cwe_2='PT Seconds', cwe_3='LN')
        obx_2.obx_5 = '42.5'
        obx_2.units = CWE(cwe_1='seconds')
        obx_2.reference_range = '11.0-15.0'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240811090000+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3173-2', cwe_2='APTT', cwe_3='LN')
        obx_3.obx_5 = '38.2'
        obx_3.units = CWE(cwe_1='seconds')
        obx_3.reference_range = '25.0-37.0'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240811090000+1000'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'INR above therapeutic range. Please review Warfarin dose.'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3
        observation_3.nte = nte

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
    """ Based on live/au/au-genie-solutions.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GENIE')
        msh.sending_facility = HD(hd_1='ROCKY_MEDICAL')
        msh.receiving_application = HD(hd_1='GENIE_SOLUTIONS')
        msh.receiving_facility = HD(hd_1='ADMIN')
        msh.date_time_of_message = '20240507083000+1000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'MSG00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20240507083000+1000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='RM112233', cx_4='ROCKY_MEDICAL', cx_5='MR')
        pid.patient_name = XPN(xpn_1='NGUYEN', xpn_2='THANH', xpn_3='VAN', xpn_5='MR')
        pid.date_time_of_birth = '19880622'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Unit 3, 14 Archer Street', xad_3='ROCKHAMPTON', xad_4='QLD', xad_5='4700', xad_6='AUS')
        pid.pid_13 = '0749221567'
        pid.primary_language = CWE(cwe_1='VI')
        pid.religion = CWE(cwe_1='M')
        pid.pid_20 = '6789054321'
        pid.multiple_birth_indicator = 'VNM'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='NGUYEN', xpn_2='LINH', xpn_5='MRS')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse')
        nk1.address = XAD(xad_1='14 Archer Street', xad_3='ROCKHAMPTON', xad_4='QLD', xad_5='4700', xad_6='AUS')
        nk1.nk1_5 = '0749221568'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='ROCKHAMPTON MEDICAL CENTRE')
        pv1.attending_doctor = XCN(xcn_1='0401678G', xcn_2='CHEN', xcn_3='HENRY', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V00012378')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='MBSA', cwe_2='Medicare Australia')
        in1.insurance_company_id = CX(cx_1='HIC')
        in1.insurance_company_name = XON(xon_1='Medicare Australia')
        in1.name_of_insured = XPN(xpn_1='NGUYEN', xpn_2='THANH', xpn_3='VAN')
        in1.insureds_relationship_to_patient = CWE(cwe_1='SEL')
        in1.insureds_date_of_birth = '19880622'
        in1.policy_number = '6789054321 1'

        # .. build the INSURANCE group ..
        insurance = AdtA05Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.insurance = insurance

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
    """ Based on live/au/au-genie-solutions.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GENIE_SOLUTIONS')
        msh.sending_facility = HD(hd_1='RHEUMATOLOGY_QLD')
        msh.receiving_application = HD(hd_1='GENIE')
        msh.receiving_facility = HD(hd_1='TARINGA_MED')
        msh.date_time_of_message = '20241015140000+1000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20241015140000+1000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='RQ447128', cx_4='RHEUMATOLOGY_QLD', cx_5='MR')
        pid.patient_name = XPN(xpn_1='MOLONEY', xpn_2='FIONA', xpn_3='DEIRDRE', xpn_5='MRS')
        pid.date_time_of_birth = '19610719'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='5 Indooroopilly Road', xad_3='TARINGA', xad_4='QLD', xad_5='4068', xad_6='AUS')
        pid.pid_13 = '0733784091'
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '8901471329'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='RHEUMATOLOGY QLD')
        pv1.attending_doctor = XCN(xcn_1='0434890G', xcn_2='SINGH', xcn_3='HARPREET', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='RHE')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='0434890G', xcn_2='SINGH', xcn_3='HARPREET', xcn_6='DR')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='SP', cwe_2='Specialist Letter')
        txa.document_content_presentation = 'AP'
        txa.activity_date_time = '20241015'
        txa.origination_date_time = '0434890G^SINGH^HARPREET^^^DR'
        txa.unique_document_number = EI(ei_1='DOC67890')
        txa.document_confidentiality_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Specialist Report', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMg'
            'MCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5'
            'IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo='
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
    """ Based on live/au/au-genie-solutions.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='QMLLIS')
        msh.sending_facility = HD(hd_1='QML', hd_2='2184', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='GENIE')
        msh.receiving_facility = HD(hd_1='LOGAN_WOMENS_HEALTH')
        msh.date_time_of_message = '20240220102000+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PA77889900', cx_4='QML', cx_5='MR')
        pid.patient_name = XPN(xpn_1='WRIGHT', xpn_2='EMMA', xpn_3='JANE', xpn_5='MS')
        pid.date_time_of_birth = '19870614'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='42 Wembley Road', xad_3='LOGAN CENTRAL', xad_4='QLD', xad_5='4114', xad_6='AUS')
        pid.pid_13 = '0432109876'
        pid.marital_status = CWE(cwe_1='S')
        pid.pid_19 = '0987654321'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='LOGAN WOMENS HEALTH')
        pv1.attending_doctor = XCN(xcn_1='0445012G', xcn_2='DUFFY', xcn_3='CAROLINE', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V00089012')
        pv1.prior_temporary_location = PL(pl_1='20240220')

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
        orc.placer_order_number = EI(ei_1='ORD221133')
        orc.filler_order_number = EI(ei_1='QML240220001')
        orc.order_status = 'CM'
        orc.orc_12 = '0445012G^DUFFY^CAROLINE^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD221133')
        obr.filler_order_number = EI(ei_1='QML240220001')
        obr.universal_service_identifier = CWE(cwe_1='21440-3', cwe_2='HPV DNA', cwe_3='LN')
        obr.observation_date_time = '20240219100000+1000'
        obr.obr_16 = '0445012G^DUFFY^CAROLINE^^^DR'
        obr.results_rpt_status_chng_date_time = '20240220100000+1000'
        obr.diagnostic_serv_sect_id = 'CY'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='21440-3', cwe_2='HPV DNA Test', cwe_3='LN')
        obx.obx_5 = 'NOT DETECTED'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240220100000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='59420-0', cwe_2='HPV 16', cwe_3='LN')
        obx_2.obx_5 = 'NOT DETECTED'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240220100000+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='59263-4', cwe_2='HPV 18', cwe_3='LN')
        obx_3.obx_5 = 'NOT DETECTED'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240220100000+1000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='10524-7', cwe_2='Cytology', cwe_3='LN')
        obx_4.obx_5 = 'Negative for intraepithelial lesion or malignancy'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240220100000+1000'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Next cervical screening test due in 5 years as per NCSP guidelines.'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4
        observation_4.nte = nte

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
