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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, FC, HD, MSG, OG, PL, PT, VID, XAD, XCN, XPN
from zato.hl7v2.v2_9.groups import AdtA01NextOfKin, MdmT02Observation, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, \
    OruR01PatientResult, OruR01Visit, RefI12ProviderContact
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A03, MDM_T02, ORU_R01, REF_I12
from zato.hl7v2.v2_9.segments import DG1, EVN, MSH, NK1, NTE, OBR, OBX, ORC, PID, PRD, PV1, RF1, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('au', 'au-healthlink.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/au/au-healthlink.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SNPLAB')
        msh.sending_facility = HD(hd_1='SNP', hd_2='2184', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='HEALTHLINK')
        msh.receiving_facility = HD(hd_1='HLMSG')
        msh.date_time_of_message = '20240315083022+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00001234'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='4567891234', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='THOMPSON', xpn_2='WILLIAM', xpn_3='JAMES')
        pid.date_time_of_birth = '19580412'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='14 Boundary Street', xad_3='TOOWOOMBA', xad_4='QLD', xad_5='4350', xad_6='AUS')
        pid.pid_13 = '0412345678'
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.attending_doctor = XCN(xcn_1='0455678B', xcn_2='CHEN', xcn_3='DAVID', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V00012345')
        pv1.prior_temporary_location = PL(pl_1='20240314')

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
        orc.placer_order_number = EI(ei_1='ORD20240315-001')
        orc.filler_order_number = EI(ei_1='SNP240315-5678')
        orc.order_status = 'CM'
        orc.orc_12 = '0455678B^CHEN^DAVID^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20240315-001')
        obr.filler_order_number = EI(ei_1='SNP240315-5678')
        obr.universal_service_identifier = CWE(cwe_1='26604007', cwe_2='Full Blood Count', cwe_3='SCT')
        obr.observation_date_time = '20240314103000+1000'
        obr.obr_16 = '0455678B^CHEN^DAVID^^^DR'
        obr.results_rpt_status_chng_date_time = '20240315080000+1000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Haemoglobin', cwe_3='LN')
        obx.obx_5 = '148'
        obx.units = CWE(cwe_1='g/L')
        obx.reference_range = '130-175'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240315080000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='Red Cell Count', cwe_3='LN')
        obx_2.obx_5 = '4.9'
        obx_2.obx_6 = 'x10\\S\\12/L'
        obx_2.reference_range = '4.5-6.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240315080000+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Haematocrit', cwe_3='LN')
        obx_3.obx_5 = '0.44'
        obx_3.units = CWE(cwe_1='L/L')
        obx_3.reference_range = '0.40-0.52'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240315080000+1000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='787-2', cwe_2='MCV', cwe_3='LN')
        obx_4.obx_5 = '89.8'
        obx_4.units = CWE(cwe_1='fL')
        obx_4.reference_range = '80-100'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240315080000+1000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='785-6', cwe_2='MCH', cwe_3='LN')
        obx_5.obx_5 = '30.2'
        obx_5.units = CWE(cwe_1='pg')
        obx_5.reference_range = '27-33'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20240315080000+1000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='6690-2', cwe_2='White Cell Count', cwe_3='LN')
        obx_6.obx_5 = '7.2'
        obx_6.obx_6 = 'x10\\S\\9/L'
        obx_6.reference_range = '4.0-11.0'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20240315080000+1000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='777-3', cwe_2='Platelet Count', cwe_3='LN')
        obx_7.obx_5 = '245'
        obx_7.obx_6 = 'x10\\S\\9/L'
        obx_7.reference_range = '150-400'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20240315080000+1000'

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
    """ Based on live/au/au-healthlink.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='QMLPATH')
        msh.sending_facility = HD(hd_1='QML', hd_2='2102', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='HL_MSG')
        msh.receiving_facility = HD(hd_1='HEALTHLINK')
        msh.date_time_of_message = '20240508141530+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'QML2024050800456'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='3216549870', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1="O'BRIEN", xpn_2='SARAH', xpn_3='LOUISE')
        pid.date_time_of_birth = '19760923'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='27 Pacific Highway', xad_3='COFFS HARBOUR', xad_4='NSW', xad_5='2450', xad_6='AUS')
        pid.pid_13 = '0298765432'
        pid.marital_status = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.attending_doctor = XCN(xcn_1='0234567A', xcn_2='PATEL', xcn_3='RAVI', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V00098765')
        pv1.prior_temporary_location = PL(pl_1='20240507')

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
        orc.placer_order_number = EI(ei_1='ORD20240508-099')
        orc.filler_order_number = EI(ei_1='QML240508-1234')
        orc.order_status = 'CM'
        orc.orc_12 = '0234567A^PATEL^RAVI^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20240508-099')
        obr.filler_order_number = EI(ei_1='QML240508-1234')
        obr.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='Lipid Panel', cwe_3='LN')
        obr.observation_date_time = '20240507090000+1000'
        obr.obr_16 = '0234567A^PATEL^RAVI^^^DR'
        obr.results_rpt_status_chng_date_time = '20240508140000+1000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2093-3', cwe_2='Total Cholesterol', cwe_3='LN')
        obx.obx_5 = '5.8'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '<5.5'
        obx.observation_result_status = 'A'
        obx.date_time_of_the_observation = '20240508140000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2571-8', cwe_2='Triglycerides', cwe_3='LN')
        obx_2.obx_5 = '1.9'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '<2.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240508140000+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2085-9', cwe_2='HDL Cholesterol', cwe_3='LN')
        obx_3.obx_5 = '1.3'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '>1.0'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240508140000+1000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='13457-7', cwe_2='LDL Cholesterol', cwe_3='LN')
        obx_4.obx_5 = '3.6'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '<3.4'
        obx_4.observation_result_status = 'A'
        obx_4.date_time_of_the_observation = '20240508140000+1000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='13458-5', cwe_2='Total/HDL Ratio', cwe_3='LN')
        obx_5.obx_5 = '4.5'
        obx_5.reference_range = '<4.5'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20240508140000+1000'

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
    """ Based on live/au/au-healthlink.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IMEDRIS')
        msh.sending_facility = HD(hd_1='IMED', hd_2='9901', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='HEALTHLINK')
        msh.receiving_facility = HD(hd_1='HL_MSG')
        msh.date_time_of_message = '20240220102345+1100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'IMED20240220-789'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='1234567890', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='NGUYEN', xpn_2='THI', xpn_3='HONG')
        pid.date_time_of_birth = '19850617'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='5/42 George Street', xad_3='PARRAMATTA', xad_4='NSW', xad_5='2150', xad_6='AUS')
        pid.pid_13 = '0411223344'
        pid.marital_status = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.attending_doctor = XCN(xcn_1='0198765C', xcn_2='WILLIAMS', xcn_3='JOHN', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V00054321')
        pv1.prior_temporary_location = PL(pl_1='20240219')

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
        orc.placer_order_number = EI(ei_1='RAD20240220-001')
        orc.filler_order_number = EI(ei_1='IMED240220-456')
        orc.order_status = 'CM'
        orc.orc_12 = '0198765C^WILLIAMS^JOHN^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20240220-001')
        obr.filler_order_number = EI(ei_1='IMED240220-456')
        obr.universal_service_identifier = CWE(cwe_1='24627-2', cwe_2='CT Chest', cwe_3='LN')
        obr.observation_date_time = '20240219143000+1100'
        obr.obr_16 = '0198765C^WILLIAMS^JOHN^^^DR'
        obr.results_rpt_status_chng_date_time = '20240220100000+1100'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='24627-2', cwe_2='CT Chest Report', cwe_3='LN')
        obx.obx_5 = (
            'CT CHEST WITHOUT CONTRAST\\.br\\\\.br\\CLINICAL NOTES: Persistent cough 6 weeks. Smoker.\\.br\\\\.br\\FINDINGS:\\.br\\Lungs: No focal consolidation or'
            ' mass lesion identified. Minor dependent atelectasis in both lower lobes.\\.br\\Mediastinum: No lymphadenopathy. Heart size normal.\\.br\\Pleura'
            ': No effusion.\\.br\\Bones: Degenerative changes thoracic spine. No suspicious lesion.\\.br\\\\.br\\CONCLUSION: No significant pulmonary abnormali'
            'ty demonstrated.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240220100000+1100'

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
    """ Based on live/au/au-healthlink.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BPSMED')
        msh.sending_facility = HD(hd_1='BESTPRACTICE')
        msh.receiving_application = HD(hd_1='HEALTHLINK')
        msh.receiving_facility = HD(hd_1='HL_MSG')
        msh.date_time_of_message = '20240410153012+1000'
        msh.message_type = MSG(msg_1='REF', msg_2='I12', msg_3='REF_I12')
        msh.message_control_id = 'BP20240410-REF001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build RF1 ..
        rf1 = RF1()
        rf1.referral_status = CWE(cwe_1='SS')
        rf1.referral_priority = CWE(cwe_1='RP')
        rf1.referral_type = CWE(cwe_1='GI')
        rf1.referral_disposition = CWE(cwe_1='20240425')
        rf1.originating_referral_identifier = EI(ei_1='R')
        rf1.effective_date = '20240410'

        # .. build PRD ..
        prd = PRD()
        prd.provider_role = CWE(cwe_1='RP')
        prd.provider_name = XPN(xpn_1='MORRISON', xpn_2='KAREN', xpn_5='DR')
        prd.provider_location = PL(pl_3='BRISBANE', pl_4='QLD', pl_5='4000', pl_6='AUS')
        prd.prd_5 = '0456789B'
        prd.prd_9 = 'HEALTHLINK^EDI001234'

        # .. build the PROVIDER_CONTACT group ..
        provider_contact = RefI12ProviderContact()
        provider_contact.prd = prd

        # .. build PRD ..
        prd_2 = PRD()
        prd_2.provider_role = CWE(cwe_1='RT')
        prd_2.provider_name = XPN(xpn_1='GUPTA', xpn_2='ANIL', xpn_5='DR')
        prd_2.provider_location = PL(pl_1='Suite 3, 100 Wickham Terrace', pl_3='BRISBANE', pl_4='QLD', pl_5='4000', pl_6='AUS')
        prd_2.prd_5 = '0478901D'
        prd_2.prd_9 = 'HEALTHLINK^EDI005678'

        # .. build the PROVIDER_CONTACT group ..
        provider_contact_2 = RefI12ProviderContact()
        provider_contact_2.prd = prd_2

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='8765432109', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='FITZGERALD', xpn_2='MARK', xpn_3='PETER')
        pid.date_time_of_birth = '19690803'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='88 Vulture Street', xad_3='WOOLLOONGABBA', xad_4='QLD', xad_5='4102', xad_6='AUS')
        pid.pid_13 = '0423456789'
        pid.marital_status = CWE(cwe_1='M')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K21.0', cwe_2='Gastro-oesophageal reflux disease', cwe_3='I10AM')
        dg1.diagnosis_type = CWE(cwe_1='W')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = (
            'Patient has 3 month history of worsening reflux symptoms not responding to PPI therapy. Please assess for endoscopy. PMHx: HTN, T2DM. Medica'
            'tions: Ramipril 5mg daily, Metformin 1g BD, Esomeprazole 40mg daily.'
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
    """ Based on live/au/au-healthlink.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MELBPATH')
        msh.sending_facility = HD(hd_1='MELP', hd_2='2011', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='HL_MSG')
        msh.receiving_facility = HD(hd_1='HEALTHLINK')
        msh.date_time_of_message = '20240612091500+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MELP20240612-234'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='5432167890', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='JENKINS', xpn_2='ALICE', xpn_3='MARY')
        pid.date_time_of_birth = '19920115'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='9 Chapel Street', xad_3='WINDSOR', xad_4='VIC', xad_5='3181', xad_6='AUS')
        pid.pid_13 = '0399876543'
        pid.marital_status = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.attending_doctor = XCN(xcn_1='0312456F', xcn_2='KUMAR', xcn_3='PRIYA', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V00087654')
        pv1.prior_temporary_location = PL(pl_1='20240610')

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
        orc.placer_order_number = EI(ei_1='ORD20240612-077')
        orc.filler_order_number = EI(ei_1='MELP240612-891')
        orc.order_status = 'CM'
        orc.orc_12 = '0312456F^KUMAR^PRIYA^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20240612-077')
        obr.filler_order_number = EI(ei_1='MELP240612-891')
        obr.universal_service_identifier = CWE(cwe_1='630-4', cwe_2='Urine Culture', cwe_3='LN')
        obr.observation_date_time = '20240610140000+1000'
        obr.obr_16 = '0312456F^KUMAR^PRIYA^^^DR'
        obr.results_rpt_status_chng_date_time = '20240612090000+1000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='630-4', cwe_2='Urine Culture', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'SPECIMEN: Mid-stream urine\\.br\\\\.br\\MICROSCOPY:\\.br\\WBC: >100 x10\\S\\6/L\\.br\\RBC: 5-10 x10\\S\\6/L\\.br\\Epithelial cells: Occasional\\.br\\\\.br\\CU'
            'LTURE:\\.br\\Escherichia coli - heavy growth (>10\\S\\8 cfu/L)\\.br\\\\.br\\SENSITIVITIES:\\.br\\Amoxicillin: Resistant\\.br\\Trimethoprim: Resistant\\.b'
            'r\\Cefalexin: Sensitive\\.br\\Nitrofurantoin: Sensitive\\.br\\Norfloxacin: Sensitive'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240612090000+1000'

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
    """ Based on live/au/au-healthlink.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HOMER')
        msh.sending_facility = HD(hd_1='RMH', hd_2='0301', hd_3='AUSHIC')
        msh.receiving_application = HD(hd_1='HEALTHLINK')
        msh.receiving_facility = HD(hd_1='HL_MSG')
        msh.date_time_of_message = '20240718160500+1000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'RMH20240718-DS001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20240718160500+1000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='9876543210', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='BROWN', xpn_2='ROBERT', xpn_3='JAMES')
        pid.date_time_of_birth = '19450322'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='3 Collins Street', xad_3='MELBOURNE', xad_4='VIC', xad_5='3000', xad_6='AUS')
        pid.pid_13 = '0398765432'
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4EAST', pl_2='401', pl_3='A')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.attending_doctor = XCN(xcn_1='0567890G', xcn_2='SINGH', xcn_3='HARPREET', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='A')
        pv1.admitting_doctor = XCN(xcn_1='0567890G', xcn_2='SINGH', xcn_3='HARPREET', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.visit_number = CX(cx_1='V00011234')
        pv1.diet_type = CWE(cwe_1='RMH')
        pv1.pv1_40 = '20240712'
        pv1.account_status = CWE(cwe_1='20240718')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='Discharge Summary')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20240718150000+1000'
        txa.primary_activity_provider_code_name = XCN(xcn_1='0567890G', xcn_2='SINGH', xcn_3='HARPREET', xcn_6='DR')
        txa.transcription_date_time = '20240718160000+1000'
        txa.parent_document_number = EI(ei_1='DOC20240718-001')
        txa.document_completion_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Discharge Summary', cwe_3='LN')
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
    """ Based on live/au/au-healthlink.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DORPATH')
        msh.sending_facility = HD(hd_1='DORE', hd_2='2009', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='HEALTHLINK')
        msh.receiving_facility = HD(hd_1='HL_MSG')
        msh.date_time_of_message = '20240125104500+1100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'DORE20240125-567'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='6543217890', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='SMITH', xpn_2='JENNIFER', xpn_3='ANN')
        pid.date_time_of_birth = '19710408'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='22 High Street', xad_3='KEW', xad_4='VIC', xad_5='3101', xad_6='AUS')
        pid.pid_13 = '0412987654'
        pid.marital_status = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.attending_doctor = XCN(xcn_1='0234890H', xcn_2='TAYLOR', xcn_3='SIMON', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V00034567')
        pv1.prior_temporary_location = PL(pl_1='20240118')

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
        orc.placer_order_number = EI(ei_1='ORD20240125-045')
        orc.filler_order_number = EI(ei_1='DORE240125-2345')
        orc.order_status = 'CM'
        orc.orc_12 = '0234890H^TAYLOR^SIMON^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20240125-045')
        obr.filler_order_number = EI(ei_1='DORE240125-2345')
        obr.universal_service_identifier = CWE(cwe_1='66121-5', cwe_2='Tissue Pathology', cwe_3='LN')
        obr.observation_date_time = '20240118110000+1100'
        obr.obr_16 = '0234890H^TAYLOR^SIMON^^^DR'
        obr.results_rpt_status_chng_date_time = '20240125100000+1100'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='66121-5', cwe_2='Histopathology Report', cwe_3='LN')
        obx.obx_5 = (
            'SPECIMEN: Excision biopsy left breast lesion (wire localised)\\.br\\\\.br\\MACROSCOPIC:\\.br\\Specimen 45 x 30 x 25mm with wire entering from supe'
            'rior aspect. Firm area 12mm identified on serial sectioning.\\.br\\\\.br\\MICROSCOPIC:\\.br\\Sections show a grade 2 invasive ductal carcinoma NST'
            ', measuring 11mm in maximum extent.\\.br\\Margins: Superior 8mm, inferior 12mm, medial 5mm, lateral 15mm, deep 6mm, superficial 10mm.\\.br\\Lymp'
            'hovascular invasion: Not identified.\\.br\\DCIS: Present, low grade, solid pattern, confined within invasive tumour.\\.br\\\\.br\\ER: Positive (Al'
            'lred 8/8)\\.br\\PR: Positive (Allred 7/8)\\.br\\HER2: Negative (1+)\\.br\\Ki67: 15%'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240125100000+1100'

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
    """ Based on live/au/au-healthlink.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='POWERCHART')
        msh.sending_facility = HD(hd_1='WESTMEAD', hd_2='8123', hd_3='AUSHIC')
        msh.receiving_application = HD(hd_1='HEALTHLINK')
        msh.receiving_facility = HD(hd_1='HL_MSG')
        msh.date_time_of_message = '20240903123000+1000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'WMH20240903-ADT456'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20240903120000+1000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='2345678901', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='KELLY', xpn_2='PATRICK', xpn_3='JOHN')
        pid.date_time_of_birth = '19530918'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='17 Church Street', xad_3='PARRAMATTA', xad_4='NSW', xad_5='2150', xad_6='AUS')
        pid.pid_13 = '0287654321'
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='12', pl_3='A')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.attending_doctor = XCN(xcn_1='0876543J', xcn_2='LEE', xcn_3='MICHAEL', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='CAR')
        pv1.admit_source = CWE(cwe_1='A')
        pv1.admitting_doctor = XCN(xcn_1='0876543J', xcn_2='LEE', xcn_3='MICHAEL', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.visit_number = CX(cx_1='V00022345')
        pv1.diet_type = CWE(cwe_1='WESTMEAD')
        pv1.pv1_40 = '20240828'
        pv1.account_status = CWE(cwe_1='20240903')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I21.0', cwe_2='Acute ST elevation myocardial infarction', cwe_3='I10AM')
        dg1.diagnosis_type = CWE(cwe_1='W')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='I25.1', cwe_2='Atherosclerotic heart disease', cwe_3='I10AM')
        dg1_2.diagnosis_type = CWE(cwe_1='S')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = [dg1, dg1_2]

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
    """ Based on live/au/au-healthlink.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABSYS')
        msh.sending_facility = HD(hd_1='LAVERTY', hd_2='2027', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='HL_MSG')
        msh.receiving_facility = HD(hd_1='HEALTHLINK')
        msh.date_time_of_message = '20240801155000+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAV20240801-3456'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='7654321098', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='WALSH', xpn_2='MEGAN', xpn_3='CATHERINE')
        pid.date_time_of_birth = '19880529'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Unit 4, 88 Oxford Street', xad_3='PADDINGTON', xad_4='NSW', xad_5='2021', xad_6='AUS')
        pid.pid_13 = '0421876543'
        pid.marital_status = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.attending_doctor = XCN(xcn_1='0543210K', xcn_2='ZHAO', xcn_3='LING', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V00045678')
        pv1.prior_temporary_location = PL(pl_1='20240731')

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
        orc.placer_order_number = EI(ei_1='ORD20240801-011')
        orc.filler_order_number = EI(ei_1='LAV240801-7890')
        orc.order_status = 'CM'
        orc.orc_12 = '0543210K^ZHAO^LING^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20240801-011')
        obr.filler_order_number = EI(ei_1='LAV240801-7890')
        obr.universal_service_identifier = CWE(cwe_1='24348-5', cwe_2='Thyroid Function', cwe_3='LN')
        obr.observation_date_time = '20240731083000+1000'
        obr.obr_16 = '0543210K^ZHAO^LING^^^DR'
        obr.results_rpt_status_chng_date_time = '20240801150000+1000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='TSH', cwe_3='LN')
        obx.obx_5 = '8.7'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.4-4.0'
        obx.observation_result_status = 'H'
        obx.date_time_of_the_observation = '20240801150000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3024-7', cwe_2='Free T4', cwe_3='LN')
        obx_2.obx_5 = '9.2'
        obx_2.units = CWE(cwe_1='pmol/L')
        obx_2.reference_range = '10.0-20.0'
        obx_2.observation_result_status = 'L'
        obx_2.date_time_of_the_observation = '20240801150000+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3053-6', cwe_2='Free T3', cwe_3='LN')
        obx_3.obx_5 = '3.8'
        obx_3.units = CWE(cwe_1='pmol/L')
        obx_3.reference_range = '3.5-6.5'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240801150000+1000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'FT'
        obx_4.observation_identifier = CWE(cwe_1='24348-5', cwe_2='Thyroid Function Comment', cwe_3='LN')
        obx_4.obx_5 = 'Results consistent with subclinical hypothyroidism. Recommend repeat in 6-8 weeks with thyroid antibodies if not previously performed.'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240801150000+1000'

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
    """ Based on live/au/au-healthlink.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDICALDIRECTOR')
        msh.sending_facility = HD(hd_1='MDGP')
        msh.receiving_application = HD(hd_1='HEALTHLINK')
        msh.receiving_facility = HD(hd_1='HL_MSG')
        msh.date_time_of_message = '20240522091500+1000'
        msh.message_type = MSG(msg_1='REF', msg_2='I12', msg_3='REF_I12')
        msh.message_control_id = 'MD20240522-REF045'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build RF1 ..
        rf1 = RF1()
        rf1.referral_status = CWE(cwe_1='SS')
        rf1.referral_priority = CWE(cwe_1='RP')
        rf1.referral_type = CWE(cwe_1='CARD')
        rf1.referral_disposition = CWE(cwe_1='20240605')
        rf1.originating_referral_identifier = EI(ei_1='U')
        rf1.effective_date = '20240522'

        # .. build PRD ..
        prd = PRD()
        prd.provider_role = CWE(cwe_1='RP')
        prd.provider_name = XPN(xpn_1='ANDERSON', xpn_2='BRUCE', xpn_5='DR')
        prd.provider_location = PL(pl_1='12 Station Road', pl_3='HORNSBY', pl_4='NSW', pl_5='2077', pl_6='AUS')
        prd.prd_5 = '0345678L'
        prd.prd_9 = 'HEALTHLINK^EDI009876'

        # .. build the PROVIDER_CONTACT group ..
        provider_contact = RefI12ProviderContact()
        provider_contact.prd = prd

        # .. build PRD ..
        prd_2 = PRD()
        prd_2.provider_role = CWE(cwe_1='RT')
        prd_2.provider_name = XPN(xpn_1='RAHMAN', xpn_2='FARID', xpn_5='DR')
        prd_2.provider_location = PL(pl_1='Level 2, 201 Pacific Highway', pl_3='ST LEONARDS', pl_4='NSW', pl_5='2065', pl_6='AUS')
        prd_2.prd_5 = '0789012M'
        prd_2.prd_9 = 'HEALTHLINK^EDI004321'

        # .. build the PROVIDER_CONTACT group ..
        provider_contact_2 = RefI12ProviderContact()
        provider_contact_2.prd = prd_2

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='3456789012', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='DAVIS', xpn_2='PETER', xpn_3='ALAN')
        pid.date_time_of_birth = '19610214'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='45 Galston Road', xad_3='HORNSBY', xad_4='NSW', xad_5='2077', xad_6='AUS')
        pid.pid_13 = '0418765432'
        pid.marital_status = CWE(cwe_1='M')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I48.0', cwe_2='Paroxysmal atrial fibrillation', cwe_3='I10AM')
        dg1.diagnosis_type = CWE(cwe_1='W')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = (
            '67yo male with new paroxysmal AF detected on Holter monitor. 3 episodes lasting 2-15 minutes. Asymptomatic during events. CHA2DS2-VASc score'
            ' 2 (age, hypertension). Currently on Metoprolol 25mg BD. BP well controlled on Perindopril 5mg. Please review for anticoagulation and rhythm'
            ' management.'
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
    """ Based on live/au/au-healthlink.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ACLLAB')
        msh.sending_facility = HD(hd_1='ACL', hd_2='2034', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='HEALTHLINK')
        msh.receiving_facility = HD(hd_1='HL_MSG')
        msh.date_time_of_message = '20240419112000+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ACL20240419-890'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='4321987650', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='HARRIS', xpn_2='GEORGE', xpn_3='EDWARD')
        pid.date_time_of_birth = '19480712'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='6 Marine Parade', xad_3='SOUTHPORT', xad_4='QLD', xad_5='4215', xad_6='AUS')
        pid.pid_13 = '0755432198'
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.attending_doctor = XCN(xcn_1='0654321N', xcn_2='JONES', xcn_3='ELIZABETH', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V00056789')
        pv1.prior_temporary_location = PL(pl_1='20240418')

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
        orc.placer_order_number = EI(ei_1='ORD20240419-023')
        orc.filler_order_number = EI(ei_1='ACL240419-4567')
        orc.order_status = 'CM'
        orc.orc_12 = '0654321N^JONES^ELIZABETH^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20240419-023')
        obr.filler_order_number = EI(ei_1='ACL240419-4567')
        obr.universal_service_identifier = CWE(cwe_1='24331-1', cwe_2='Coagulation Studies', cwe_3='LN')
        obr.observation_date_time = '20240418100000+1000'
        obr.obr_16 = '0654321N^JONES^ELIZABETH^^^DR'
        obr.results_rpt_status_chng_date_time = '20240419110000+1000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='Prothrombin Time', cwe_3='LN')
        obx.obx_5 = '13.5'
        obx.units = CWE(cwe_1='seconds')
        obx.reference_range = '11.0-15.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240419110000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx_2.obx_5 = '1.1'
        obx_2.reference_range = '0.9-1.3'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240419110000+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3173-2', cwe_2='APTT', cwe_3='LN')
        obx_3.obx_5 = '29'
        obx_3.units = CWE(cwe_1='seconds')
        obx_3.reference_range = '25-37'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240419110000+1000'

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
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240419110000+1000'

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
    """ Based on live/au/au-healthlink.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CERNER')
        msh.sending_facility = HD(hd_1='RPA', hd_2='8101', hd_3='AUSHIC')
        msh.receiving_application = HD(hd_1='HEALTHLINK')
        msh.receiving_facility = HD(hd_1='HL_MSG')
        msh.date_time_of_message = '20240306143000+1100'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'RPA20240306-SL789'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20240306143000+1100'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='5678901234', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='MARTINEZ', xpn_2='ISABELLA', xpn_3='ROSA')
        pid.date_time_of_birth = '19830921'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='91 King Street', xad_3='NEWTOWN', xad_4='NSW', xad_5='2042', xad_6='AUS')
        pid.pid_13 = '0432109876'
        pid.marital_status = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RHEUM', pl_2='CLINIC')
        pv1.consulting_doctor = XCN(xcn_1='0890123P', xcn_2='MURPHY', xcn_3='COLLEEN', xcn_6='DR')
        pv1.preadmit_test_indicator = CWE(cwe_1='RHEUM')
        pv1.vip_indicator = CWE(cwe_1='A')
        pv1.visit_number = CX(cx_1='0890123P', cx_2='MURPHY', cx_3='COLLEEN', cx_6='DR')
        pv1.financial_class = FC(fc_1='OP')
        pv1.charge_price_indicator = CWE(cwe_1='V00067890')
        pv1.current_patient_balance = '20240306'

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='SL', cwe_2='Specialist Letter')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20240306140000+1100'
        txa.primary_activity_provider_code_name = XCN(xcn_1='0890123P', xcn_2='MURPHY', xcn_3='COLLEEN', xcn_6='DR')
        txa.transcription_date_time = '20240306142500+1100'
        txa.parent_document_number = EI(ei_1='DOC20240306-SL01')
        txa.document_completion_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Specialist Letter', cwe_3='LN')
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
    """ Based on live/au/au-healthlink.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DHMPATH')
        msh.sending_facility = HD(hd_1='DHM', hd_2='2024', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='HL_MSG')
        msh.receiving_facility = HD(hd_1='HEALTHLINK')
        msh.date_time_of_message = '20240627083000+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'DHM20240627-1234'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='8901456720', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='CHEN', xpn_2='XIAOLONG', xpn_3='JIE')
        pid.date_time_of_birth = '19710305'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='156 Victoria Road', xad_3='GLADESVILLE', xad_4='NSW', xad_5='2111', xad_6='AUS')
        pid.pid_13 = '0298127045'
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.attending_doctor = XCN(xcn_1='0765432Q', xcn_2='FRASER', xcn_3='ANDREW', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V00078901')
        pv1.prior_temporary_location = PL(pl_1='20240626')

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
        orc.placer_order_number = EI(ei_1='ORD20240627-088')
        orc.filler_order_number = EI(ei_1='DHM240627-5678')
        orc.order_status = 'CM'
        orc.orc_12 = '0765432Q^FRASER^ANDREW^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20240627-088')
        obr.filler_order_number = EI(ei_1='DHM240627-5678')
        obr.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obr.observation_date_time = '20240626080000+1000'
        obr.obr_16 = '0765432Q^FRASER^ANDREW^^^DR'
        obr.results_rpt_status_chng_date_time = '20240627080000+1000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obx.obx_5 = '7.8'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '<7.0'
        obx.observation_result_status = 'H'
        obx.date_time_of_the_observation = '20240627080000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='59261-8', cwe_2='HbA1c (IFCC)', cwe_3='LN')
        obx_2.obx_5 = '62'
        obx_2.units = CWE(cwe_1='mmol/mol')
        obx_2.reference_range = '<53'
        obx_2.observation_result_status = 'H'
        obx_2.date_time_of_the_observation = '20240627080000+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'FT'
        obx_3.observation_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c Comment', cwe_3='LN')
        obx_3.obx_5 = 'Estimated average glucose: 10.0 mmol/L. Above target for most patients with type 2 diabetes. Consider therapy intensification.'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240627080000+1000'

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
    """ Based on live/au/au-healthlink.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HBCIS')
        msh.sending_facility = HD(hd_1='RBWH', hd_2='0401', hd_3='AUSHIC')
        msh.receiving_application = HD(hd_1='HEALTHLINK')
        msh.receiving_facility = HD(hd_1='HL_MSG')
        msh.date_time_of_message = '20240815071500+1000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'RBWH20240815-ADT123'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20240815063000+1000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='6789012345', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='WILSON', xpn_2='MARGARET', xpn_3='JOAN')
        pid.date_time_of_birth = '19390604'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='28 Gympie Road', xad_3='KEDRON', xad_4='QLD', xad_5='4031', xad_6='AUS')
        pid.pid_13 = '0732198765'
        pid.marital_status = CWE(cwe_1='W')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='WILSON', xpn_2='THOMAS')
        nk1.address = XAD(xad_1='0412345678')
        nk1.nk1_6 = 'N'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_2='BAY3', pl_3='A')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.attending_doctor = XCN(xcn_1='0912345R', xcn_2='AHMED', xcn_3='FATIMA', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='GEN')
        pv1.admit_source = CWE(cwe_1='E')
        pv1.admitting_doctor = XCN(xcn_1='0912345R', xcn_2='AHMED', xcn_3='FATIMA', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='EM')
        pv1.visit_number = CX(cx_1='V00089012')
        pv1.diet_type = CWE(cwe_1='RBWH')
        pv1.pv1_40 = '20240815063000+1000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.9', cwe_2='Pneumonia unspecified', cwe_3='I10AM')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.dg1 = dg1

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
    """ Based on live/au/au-healthlink.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AUSLAB')
        msh.sending_facility = HD(hd_1='PATHQLD', hd_2='0402', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='HEALTHLINK')
        msh.receiving_facility = HD(hd_1='HL_MSG')
        msh.date_time_of_message = '20240205161000+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'PQ20240205-4567'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='7890123456', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='ROBINSON', xpn_2='JAMES', xpn_3='MICHAEL')
        pid.date_time_of_birth = '19830912'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='33 Boundary Road', xad_3='CAMP HILL', xad_4='QLD', xad_5='4152', xad_6='AUS')
        pid.pid_13 = '0423765432'
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.attending_doctor = XCN(xcn_1='0123456S', xcn_2='WHITE', xcn_3='PATRICIA', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V00090123')
        pv1.prior_temporary_location = PL(pl_1='20240204')

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
        orc.placer_order_number = EI(ei_1='ORD20240205-033')
        orc.filler_order_number = EI(ei_1='PQ240205-8901')
        orc.order_status = 'CM'
        orc.orc_12 = '0123456S^WHITE^PATRICIA^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20240205-033')
        obr.filler_order_number = EI(ei_1='PQ240205-8901')
        obr.universal_service_identifier = CWE(cwe_1='24325-3', cwe_2='Liver Function Tests', cwe_3='LN')
        obr.observation_date_time = '20240204093000+1000'
        obr.obr_16 = '0123456S^WHITE^PATRICIA^^^DR'
        obr.results_rpt_status_chng_date_time = '20240205160000+1000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT', cwe_3='LN')
        obx.obx_5 = '85'
        obx.units = CWE(cwe_1='U/L')
        obx.reference_range = '<40'
        obx.observation_result_status = 'H'
        obx.date_time_of_the_observation = '20240205160000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST', cwe_3='LN')
        obx_2.obx_5 = '62'
        obx_2.units = CWE(cwe_1='U/L')
        obx_2.reference_range = '<35'
        obx_2.observation_result_status = 'H'
        obx_2.date_time_of_the_observation = '20240205160000+1000'

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
        obx_3.reference_range = '30-120'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240205160000+1000'

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
        obx_4.date_time_of_the_observation = '20240205160000+1000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2336-6', cwe_2='GGT', cwe_3='LN')
        obx_5.obx_5 = '112'
        obx_5.units = CWE(cwe_1='U/L')
        obx_5.reference_range = '<60'
        obx_5.observation_result_status = 'H'
        obx_5.date_time_of_the_observation = '20240205160000+1000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='1751-7', cwe_2='Albumin', cwe_3='LN')
        obx_6.obx_5 = '38'
        obx_6.units = CWE(cwe_1='g/L')
        obx_6.reference_range = '35-50'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20240205160000+1000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='2885-2', cwe_2='Total Protein', cwe_3='LN')
        obx_7.obx_5 = '72'
        obx_7.units = CWE(cwe_1='g/L')
        obx_7.reference_range = '60-80'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20240205160000+1000'

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
    """ Based on live/au/au-healthlink.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CAPRIS')
        msh.sending_facility = HD(hd_1='CAPRAD', hd_2='9902', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='HEALTHLINK')
        msh.receiving_facility = HD(hd_1='HL_MSG')
        msh.date_time_of_message = '20240912091000+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CAP20240912-222'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='8012345678', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='PATEL', xpn_2='ARUN', xpn_3='KUMAR')
        pid.date_time_of_birth = '19750820'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='12 Springvale Road', xad_3='GLEN WAVERLEY', xad_4='VIC', xad_5='3150', xad_6='AUS')
        pid.pid_13 = '0399876123'
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.attending_doctor = XCN(xcn_1='0234567T', xcn_2='OLSEN', xcn_3='KAREN', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V00012456')
        pv1.prior_temporary_location = PL(pl_1='20240910')

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
        orc.placer_order_number = EI(ei_1='RAD20240912-003')
        orc.filler_order_number = EI(ei_1='CAP240912-789')
        orc.order_status = 'CM'
        orc.orc_12 = '0234567T^OLSEN^KAREN^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD20240912-003')
        obr.filler_order_number = EI(ei_1='CAP240912-789')
        obr.universal_service_identifier = CWE(cwe_1='24590-2', cwe_2='MRI Brain', cwe_3='LN')
        obr.observation_date_time = '20240910160000+1000'
        obr.obr_16 = '0234567T^OLSEN^KAREN^^^DR'
        obr.results_rpt_status_chng_date_time = '20240912090000+1000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='24590-2', cwe_2='MRI Brain Report', cwe_3='LN')
        obx.obx_5 = (
            'MRI BRAIN WITH CONTRAST\\.br\\\\.br\\CLINICAL: Headaches, query space-occupying lesion.\\.br\\\\.br\\TECHNIQUE: Multiplanar sequences pre and post g'
            'adolinium.\\.br\\\\.br\\FINDINGS:\\.br\\Brain parenchyma: Normal grey-white matter differentiation. No focal signal abnormality. No mass lesion or'
            ' midline shift.\\.br\\Ventricles: Normal size and configuration.\\.br\\Extra-axial spaces: Normal.\\.br\\Post contrast: No abnormal enhancement.\\.'
            'br\\Posterior fossa: Normal.\\.br\\Vascular: Normal flow voids in major intracranial vessels.\\.br\\\\.br\\CONCLUSION: Normal MRI brain. No evidenc'
            'e of intracranial mass lesion.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240912090000+1000'

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
    """ Based on live/au/au-healthlink.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ZEDMED')
        msh.sending_facility = HD(hd_1='ZEDGP')
        msh.receiving_application = HD(hd_1='HEALTHLINK')
        msh.receiving_facility = HD(hd_1='HL_MSG')
        msh.date_time_of_message = '20240130101500+1100'
        msh.message_type = MSG(msg_1='REF', msg_2='I12', msg_3='REF_I12')
        msh.message_control_id = 'ZED20240130-REF012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build RF1 ..
        rf1 = RF1()
        rf1.referral_status = CWE(cwe_1='SS')
        rf1.referral_priority = CWE(cwe_1='RP')
        rf1.referral_type = CWE(cwe_1='DERM')
        rf1.referral_disposition = CWE(cwe_1='20240215')
        rf1.originating_referral_identifier = EI(ei_1='R')
        rf1.effective_date = '20240130'

        # .. build PRD ..
        prd = PRD()
        prd.provider_role = CWE(cwe_1='RP')
        prd.provider_name = XPN(xpn_1='CAMPBELL', xpn_2='STUART', xpn_5='DR')
        prd.provider_location = PL(pl_1='44 Bay Road', pl_3='SANDRINGHAM', pl_4='VIC', pl_5='3191', pl_6='AUS')
        prd.prd_5 = '0345678U'
        prd.prd_9 = 'HEALTHLINK^EDI007654'

        # .. build the PROVIDER_CONTACT group ..
        provider_contact = RefI12ProviderContact()
        provider_contact.prd = prd

        # .. build PRD ..
        prd_2 = PRD()
        prd_2.provider_role = CWE(cwe_1='RT')
        prd_2.provider_name = XPN(xpn_1='WONG', xpn_2='GRACE', xpn_5='DR')
        prd_2.provider_location = PL(pl_1='Suite 8, 55 Spring Street', pl_3='MELBOURNE', pl_4='VIC', pl_5='3000', pl_6='AUS')
        prd_2.prd_5 = '0456789V'
        prd_2.prd_9 = 'HEALTHLINK^EDI003210'

        # .. build the PROVIDER_CONTACT group ..
        provider_contact_2 = RefI12ProviderContact()
        provider_contact_2.prd = prd_2

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='9012345678', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='TAYLOR', xpn_2='SUSAN', xpn_3='ELIZABETH')
        pid.date_time_of_birth = '19650711'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='7 Beach Road', xad_3='HAMPTON', xad_4='VIC', xad_5='3188', xad_6='AUS')
        pid.pid_13 = '0421654987'
        pid.marital_status = CWE(cwe_1='F')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='L82.1', cwe_2='Seborrhoeic keratosis', cwe_3='I10AM')
        dg1.diagnosis_type = CWE(cwe_1='W')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = (
            '68yo female with changing pigmented lesion right posterior calf, noticed by patient 4 months ago. Lesion 12mm irregular border with colour v'
            'ariation. Dermoscopy shows irregular globules at periphery. FHx: sister melanoma age 55. Please review urgently.'
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
    """ Based on live/au/au-healthlink.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ULTRAPATH')
        msh.sending_facility = HD(hd_1='SAP', hd_2='4101', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='HL_MSG')
        msh.receiving_facility = HD(hd_1='HEALTHLINK')
        msh.date_time_of_message = '20240711140000+0930'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SAP20240711-567'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='1234509876', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='MOORE', xpn_2='DANIEL', xpn_3='CRAIG')
        pid.date_time_of_birth = '19951028'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='15 Rundle Street', xad_3='ADELAIDE', xad_4='SA', xad_5='5000', xad_6='AUS')
        pid.pid_13 = '0881234567'
        pid.marital_status = CWE(cwe_1='S')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.attending_doctor = XCN(xcn_1='0876543W', xcn_2='GRAHAM', xcn_3='ROGER', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V00023456')
        pv1.prior_temporary_location = PL(pl_1='20240710')

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
        orc.placer_order_number = EI(ei_1='ORD20240711-055')
        orc.filler_order_number = EI(ei_1='SAP240711-3456')
        orc.order_status = 'CM'
        orc.orc_12 = '0876543W^GRAHAM^ROGER^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20240711-055')
        obr.filler_order_number = EI(ei_1='SAP240711-3456')
        obr.universal_service_identifier = CWE(cwe_1='35091-7', cwe_2='Urine Drug Screen', cwe_3='LN')
        obr.observation_date_time = '20240710110000+0930'
        obr.obr_16 = '0876543W^GRAHAM^ROGER^^^DR'
        obr.results_rpt_status_chng_date_time = '20240711135000+0930'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='19295-5', cwe_2='Amphetamines Screen', cwe_3='LN')
        obx.obx_5 = 'Negative'
        obx.reference_range = 'Negative'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240711135000+0930'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='19296-3', cwe_2='Benzodiazepines Screen', cwe_3='LN')
        obx_2.obx_5 = 'Negative'
        obx_2.reference_range = 'Negative'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240711135000+0930'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='19297-1', cwe_2='Cannabis Screen', cwe_3='LN')
        obx_3.obx_5 = 'Negative'
        obx_3.reference_range = 'Negative'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240711135000+0930'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='3397-7', cwe_2='Cocaine Screen', cwe_3='LN')
        obx_4.obx_5 = 'Negative'
        obx_4.reference_range = 'Negative'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240711135000+0930'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='19298-9', cwe_2='Opiates Screen', cwe_3='LN')
        obx_5.obx_5 = 'Positive'
        obx_5.reference_range = 'Negative'
        obx_5.observation_result_status = 'A'
        obx_5.date_time_of_the_observation = '20240711135000+0930'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'FT'
        obx_6.observation_identifier = CWE(cwe_1='19298-9', cwe_2='Opiates Comment', cwe_3='LN')
        obx_6.obx_5 = 'Consistent with prescribed oxycodone. Confirmation by LC-MS/MS: Oxycodone detected 1850 ng/mL.'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20240711135000+0930'

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
    """ Based on live/au/au-healthlink.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RADSYS')
        msh.sending_facility = HD(hd_1='SVH', hd_2='8110', hd_3='AUSHIC')
        msh.receiving_application = HD(hd_1='HEALTHLINK')
        msh.receiving_facility = HD(hd_1='HL_MSG')
        msh.date_time_of_message = '20240423111500+1000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'SVH20240423-RAD001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20240423111500+1000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='2109876543', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='LEE', xpn_2='DAVID', xpn_3='SANG')
        pid.date_time_of_birth = '19680130'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='8 Crown Street', xad_3='DARLINGHURST', xad_4='NSW', xad_5='2010', xad_6='AUS')
        pid.pid_13 = '0412876543'
        pid.marital_status = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RADIOL', pl_2='XR')
        pv1.consulting_doctor = XCN(xcn_1='0567890X', xcn_2='CHAN', xcn_3='HELEN', xcn_6='DR')
        pv1.preadmit_test_indicator = CWE(cwe_1='RAD')
        pv1.vip_indicator = CWE(cwe_1='A')
        pv1.visit_number = CX(cx_1='0567890X', cx_2='CHAN', cx_3='HELEN', cx_6='DR')
        pv1.financial_class = FC(fc_1='OP')
        pv1.charge_price_indicator = CWE(cwe_1='V00034567')
        pv1.current_patient_balance = '20240423'

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='RAD', cwe_2='Radiology Report')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20240423110000+1000'
        txa.primary_activity_provider_code_name = XCN(xcn_1='0567890X', xcn_2='CHAN', xcn_3='HELEN', xcn_6='DR')
        txa.transcription_date_time = '20240423111000+1000'
        txa.parent_document_number = EI(ei_1='DOC20240423-RAD01')
        txa.document_completion_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Radiology Report', cwe_3='LN')
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
    """ Based on live/au/au-healthlink.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABSYS')
        msh.sending_facility = HD(hd_1='PATHWEST', hd_2='4001', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='HEALTHLINK')
        msh.receiving_facility = HD(hd_1='HL_MSG')
        msh.date_time_of_message = '20240529103000+1000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'PW20240529-8901'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='3210987654', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='EVANS', xpn_2='CLAIRE', xpn_3='MARIE')
        pid.date_time_of_birth = '19800414'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='52 Darling Street', xad_3='BALMAIN', xad_4='NSW', xad_5='2041', xad_6='AUS')
        pid.pid_13 = '0298765123'
        pid.marital_status = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.attending_doctor = XCN(xcn_1='0987654Y', xcn_2='HILL', xcn_3='THOMAS', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V00045678')
        pv1.prior_temporary_location = PL(pl_1='20240528')

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
        orc.placer_order_number = EI(ei_1='ORD20240529-066')
        orc.filler_order_number = EI(ei_1='PW240529-2345')
        orc.order_status = 'CM'
        orc.orc_12 = '0987654Y^HILL^THOMAS^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20240529-066')
        obr.filler_order_number = EI(ei_1='PW240529-2345')
        obr.universal_service_identifier = CWE(cwe_1='5048-4', cwe_2='ANA Screen', cwe_3='LN')
        obr.observation_date_time = '20240528090000+1000'
        obr.obr_16 = '0987654Y^HILL^THOMAS^^^DR'
        obr.results_rpt_status_chng_date_time = '20240529100000+1000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='5048-4', cwe_2='ANA Screen', cwe_3='LN')
        obx.obx_5 = 'Positive'
        obx.reference_range = 'Negative'
        obx.observation_result_status = 'A'
        obx.date_time_of_the_observation = '20240529100000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='30462-4', cwe_2='ANA Pattern', cwe_3='LN')
        obx_2.obx_5 = 'Homogeneous and Speckled'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240529100000+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='5048-4', cwe_2='ANA Titre', cwe_3='LN')
        obx_3.obx_5 = '1:640'
        obx_3.reference_range = '<1:160'
        obx_3.observation_result_status = 'H'
        obx_3.date_time_of_the_observation = '20240529100000+1000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='11572-5', cwe_2='ENA Anti-dsDNA', cwe_3='LN')
        obx_4.obx_5 = '85'
        obx_4.units = CWE(cwe_1='IU/mL')
        obx_4.reference_range = '<30'
        obx_4.observation_result_status = 'H'
        obx_4.date_time_of_the_observation = '20240529100000+1000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='14234-8', cwe_2='ENA Panel', cwe_3='LN')
        obx_5.obx_5 = 'Anti-Sm: Negative, Anti-RNP: Positive, Anti-SSA: Positive, Anti-SSB: Negative, Anti-Scl70: Negative, Anti-Jo1: Negative'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20240529100000+1000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'FT'
        obx_6.observation_identifier = CWE(cwe_1='5048-4', cwe_2='ANA Comment', cwe_3='LN')
        obx_6.obx_5 = (
            'Positive ANA with high titre homogeneous/speckled pattern. Positive anti-dsDNA and anti-RNP. Clinical correlation recommended. Pattern may b'
            'e seen in SLE and mixed connective tissue disease.'
        )
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20240529100000+1000'

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
