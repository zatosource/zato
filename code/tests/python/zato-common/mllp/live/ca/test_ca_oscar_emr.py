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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, HD, MSG, PT, VID, XAD, XON, XPN
from zato.hl7v2.v2_9.groups import OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult
from zato.hl7v2.v2_9.messages import ORU_R01
from zato.hl7v2.v2_9.segments import MSH, NTE, OBR, OBX, PID, SFT

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ca', 'ca-oscar-emr.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ca/ca-oscar-emr.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSCAR')
        msh.sending_facility = HD(hd_1='Default Facility')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ONTARIO_HIS')
        msh.date_time_of_message = '20260401090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OSC00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')

        # .. build SFT ..
        sft = SFT()
        sft.software_vendor_organization = XON(xon_1='OSCAR McMaster')
        sft.software_certified_version_or_release_number = '19.12'
        sft.software_binary_id = 'OSCAR EMR'
        sft.software_install_date = '20260101'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1234567890', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Tremblay', xpn_2='Anne', xpn_3='Marie', xpn_5='Mme')
        pid.date_time_of_birth = '19770315'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='42 Maple Ave', xad_3='Kitchener', xad_4='ON', xad_5='N2H 3G5', xad_6='CA')
        pid.pid_13 = '^^PH^5195551234'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD001', ei_2='OSCAR')
        obr.filler_order_number = EI(ei_1='SPE001', ei_2='LIFELABS')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Complete Blood Count', cwe_3='LN')
        obr.observation_date_time = '20260401074500'
        obr.obr_16 = '1234567890^Tremblay^Anne M^^^^'
        obr.results_rpt_status_chng_date_time = '20260401090000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='WBC', cwe_3='LN')
        obx.obx_5 = '7.5'
        obx.units = CWE(cwe_1='x10*9/L')
        obx.reference_range = '4.0-11.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='RBC', cwe_3='LN')
        obx_2.obx_5 = '4.38'
        obx_2.units = CWE(cwe_1='x10*12/L')
        obx_2.reference_range = '3.80-5.80'
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
        obx_3.obx_5 = '132'
        obx_3.units = CWE(cwe_1='g/L')
        obx_3.reference_range = '120-160'
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
        obx_4.obx_5 = '0.39'
        obx_4.units = CWE(cwe_1='L/L')
        obx_4.reference_range = '0.36-0.46'
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
        obx_5.obx_5 = '215'
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
        obx_6.observation_identifier = CWE(cwe_1='787-2', cwe_2='MCV', cwe_3='LN')
        obx_6.obx_5 = '89.0'
        obx_6.units = CWE(cwe_1='fL')
        obx_6.reference_range = '80.0-100.0'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
        msg.sft = sft
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
    """ Based on live/ca/ca-oscar-emr.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSCAR')
        msh.sending_facility = HD(hd_1='Default Facility')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ONTARIO_HIS')
        msh.date_time_of_message = '20260402103000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OSC00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')

        # .. build SFT ..
        sft = SFT()
        sft.software_vendor_organization = XON(xon_1='OSCAR McMaster')
        sft.software_certified_version_or_release_number = '19.12'
        sft.software_binary_id = 'OSCAR EMR'
        sft.software_install_date = '20260101'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2345678901', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Gauthier', xpn_2='Robert', xpn_3='Michel', xpn_5='Mr')
        pid.date_time_of_birth = '19620810'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='18 King St', xad_3='Guelph', xad_4='ON', xad_5='N1H 1B6', xad_6='CA')
        pid.pid_13 = '^^PH^5195552345'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD002', ei_2='OSCAR')
        obr.filler_order_number = EI(ei_1='SPE002', ei_2='GAMMA_DYNACARE')
        obr.universal_service_identifier = CWE(cwe_1='LIPID', cwe_2='Lipid Panel', cwe_3='LN')
        obr.observation_date_time = '20260402080000'
        obr.obr_16 = '2345678901^Gauthier^Robert M^^^^'
        obr.results_rpt_status_chng_date_time = '20260402103000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2093-3', cwe_2='Total Cholesterol', cwe_3='LN')
        obx.obx_5 = '6.8'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '<5.2'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

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
        obx_2.reference_range = '<1.7'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2085-9', cwe_2='HDL Cholesterol', cwe_3='LN')
        obx_3.obx_5 = '1.05'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '>1.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='13457-7', cwe_2='LDL Cholesterol', cwe_3='LN')
        obx_4.obx_5 = '4.66'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '<3.4'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='9830-1', cwe_2='Total/HDL Ratio', cwe_3='LN')
        obx_5.obx_5 = '6.5'
        obx_5.reference_range = '<4.0'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Patient fasting for 12 hours prior to sample collection.'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5
        observation_5.nte = nte

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
        msg.sft = sft
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
    """ Based on live/ca/ca-oscar-emr.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSCAR')
        msh.sending_facility = HD(hd_1='Default Facility')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ONTARIO_HIS')
        msh.date_time_of_message = '20260403141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OSC00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')

        # .. build SFT ..
        sft = SFT()
        sft.software_vendor_organization = XON(xon_1='OSCAR McMaster')
        sft.software_certified_version_or_release_number = '19.12'
        sft.software_binary_id = 'OSCAR EMR'
        sft.software_install_date = '20260101'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3456789012', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Deschenes', xpn_2='Louise', xpn_3='Marie', xpn_5='Mme')
        pid.date_time_of_birth = '19880923'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='77 Water St', xad_3='St. Catharines', xad_4='ON', xad_5='L2R 2A3', xad_6='CA')
        pid.pid_13 = '^^PH^9055553456'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD003', ei_2='OSCAR')
        obr.filler_order_number = EI(ei_1='SPE003', ei_2='LIFELABS')
        obr.universal_service_identifier = CWE(cwe_1='THYR', cwe_2='Thyroid Panel', cwe_3='LN')
        obr.observation_date_time = '20260403080000'
        obr.obr_16 = '3456789012^Deschenes^Louise M^^^^'
        obr.results_rpt_status_chng_date_time = '20260403141500'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='TSH', cwe_3='LN')
        obx.obx_5 = '8.75'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.35-5.50'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3026-2', cwe_2='Free T4', cwe_3='LN')
        obx_2.obx_5 = '9.1'
        obx_2.units = CWE(cwe_1='pmol/L')
        obx_2.reference_range = '10.0-25.0'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3024-7', cwe_2='Free T3', cwe_3='LN')
        obx_3.obx_5 = '3.2'
        obx_3.units = CWE(cwe_1='pmol/L')
        obx_3.reference_range = '3.5-6.5'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Suggest clinical correlation. Results consistent with primary hypothyroidism.'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3
        observation_3.nte = nte

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
        msg.sft = sft
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
    """ Based on live/ca/ca-oscar-emr.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSCAR')
        msh.sending_facility = HD(hd_1='Default Facility')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ONTARIO_HIS')
        msh.date_time_of_message = '20260404110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OSC00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')

        # .. build SFT ..
        sft = SFT()
        sft.software_vendor_organization = XON(xon_1='OSCAR McMaster')
        sft.software_certified_version_or_release_number = '19.12'
        sft.software_binary_id = 'OSCAR EMR'
        sft.software_install_date = '20260101'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='4567890123', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Park', xpn_2='Jae-Won', xpn_5='Mr')
        pid.date_time_of_birth = '19950417'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='55 Charles St', xad_3='Brampton', xad_4='ON', xad_5='L6Y 1T3', xad_6='CA')
        pid.pid_13 = '^^PH^9055554567'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD004', ei_2='OSCAR')
        obr.filler_order_number = EI(ei_1='SPE004', ei_2='LIFELABS')
        obr.universal_service_identifier = CWE(cwe_1='UA', cwe_2='Urinalysis', cwe_3='LN')
        obr.observation_date_time = '20260404083000'
        obr.obr_16 = '4567890123^Park^Jae-Won^^^^'
        obr.results_rpt_status_chng_date_time = '20260404110000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='5778-6', cwe_2='Color', cwe_3='LN')
        obx.obx_5 = 'Yellow'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='5767-9', cwe_2='Appearance', cwe_3='LN')
        obx_2.obx_5 = 'Clear'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='5803-2', cwe_2='pH', cwe_3='LN')
        obx_3.obx_5 = '6.0'
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
        obx_4.obx_5 = '1.020'
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
        obx_5.observation_identifier = CWE(cwe_1='5804-0', cwe_2='Protein', cwe_3='LN')
        obx_5.obx_5 = 'Negative'
        obx_5.reference_range = 'Negative'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='5792-7', cwe_2='Glucose', cwe_3='LN')
        obx_6.obx_5 = 'Negative'
        obx_6.reference_range = 'Negative'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='5821-4', cwe_2='WBC', cwe_3='LN')
        obx_7.obx_5 = '2'
        obx_7.units = CWE(cwe_1='/HPF')
        obx_7.reference_range = '0-5'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='13945-1', cwe_2='RBC', cwe_3='LN')
        obx_8.obx_5 = '0'
        obx_8.units = CWE(cwe_1='/HPF')
        obx_8.reference_range = '0-3'
        obx_8.interpretation_codes = CWE(cwe_1='N')
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
        msg.sft = sft
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
    """ Based on live/ca/ca-oscar-emr.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSCAR')
        msh.sending_facility = HD(hd_1='Default Facility')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ONTARIO_HIS')
        msh.date_time_of_message = '20260405093000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OSC00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')

        # .. build SFT ..
        sft = SFT()
        sft.software_vendor_organization = XON(xon_1='OSCAR McMaster')
        sft.software_certified_version_or_release_number = '19.12'
        sft.software_binary_id = 'OSCAR EMR'
        sft.software_install_date = '20260101'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='5678901234', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Kaur', xpn_2='Harpreet', xpn_5='Ms')
        pid.date_time_of_birth = '19700630'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='310 Queen St', xad_3='Mississauga', xad_4='ON', xad_5='L5B 1C2', xad_6='CA')
        pid.pid_13 = '^^PH^9055555678'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD005', ei_2='OSCAR')
        obr.filler_order_number = EI(ei_1='SPE005', ei_2='GAMMA_DYNACARE')
        obr.universal_service_identifier = CWE(cwe_1='HBA1C', cwe_2='Hemoglobin A1c', cwe_3='LN')
        obr.observation_date_time = '20260405074500'
        obr.obr_16 = '5678901234^Kaur^Harpreet^^^^'
        obr.results_rpt_status_chng_date_time = '20260405093000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='Hemoglobin A1c', cwe_3='LN')
        obx.obx_5 = '0.078'
        obx.units = CWE(cwe_1='fraction')
        obx.reference_range = '<=0.070'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose Fasting', cwe_3='LN')
        obx_2.obx_5 = '8.2'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '3.3-5.5'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'HbA1c of 7.8% corresponds to an estimated average glucose of 9.8 mmol/L.'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2
        observation_2.nte = nte

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
        msg.sft = sft
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
    """ Based on live/ca/ca-oscar-emr.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSCAR')
        msh.sending_facility = HD(hd_1='Default Facility')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ONTARIO_HIS')
        msh.date_time_of_message = '20260406144500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OSC00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')

        # .. build SFT ..
        sft = SFT()
        sft.software_vendor_organization = XON(xon_1='OSCAR McMaster')
        sft.software_certified_version_or_release_number = '19.12'
        sft.software_binary_id = 'OSCAR EMR'
        sft.software_install_date = '20260101'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='6789012345', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lafleur', xpn_2='Guy', xpn_3='Pierre', xpn_5='Mr')
        pid.date_time_of_birth = '19530102'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='200 Richmond St', xad_3='London', xad_4='ON', xad_5='N6A 3L4', xad_6='CA')
        pid.pid_13 = '^^PH^5195556789'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD006', ei_2='OSCAR')
        obr.filler_order_number = EI(ei_1='SPE006', ei_2='LIFELABS')
        obr.universal_service_identifier = CWE(cwe_1='LIVER', cwe_2='Hepatic Function Panel', cwe_3='LN')
        obr.observation_date_time = '20260406081000'
        obr.obr_16 = '6789012345^Lafleur^Guy P^^^^'
        obr.results_rpt_status_chng_date_time = '20260406144500'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT', cwe_3='LN')
        obx.obx_5 = '85'
        obx.units = CWE(cwe_1='U/L')
        obx.reference_range = '7-56'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST', cwe_3='LN')
        obx_2.obx_5 = '72'
        obx_2.units = CWE(cwe_1='U/L')
        obx_2.reference_range = '10-40'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6768-6', cwe_2='Alkaline Phosphatase', cwe_3='LN')
        obx_3.obx_5 = '110'
        obx_3.units = CWE(cwe_1='U/L')
        obx_3.reference_range = '44-147'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1975-2', cwe_2='Total Bilirubin', cwe_3='LN')
        obx_4.obx_5 = '28'
        obx_4.units = CWE(cwe_1='umol/L')
        obx_4.reference_range = '5-21'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2885-2', cwe_2='Total Protein', cwe_3='LN')
        obx_5.obx_5 = '68'
        obx_5.units = CWE(cwe_1='g/L')
        obx_5.reference_range = '60-83'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='1751-7', cwe_2='Albumin', cwe_3='LN')
        obx_6.obx_5 = '35'
        obx_6.units = CWE(cwe_1='g/L')
        obx_6.reference_range = '35-52'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Elevated transaminases and bilirubin. Suggest hepatobiliary workup.'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6
        observation_6.nte = nte

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
        msg.sft = sft
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
    """ Based on live/ca/ca-oscar-emr.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSCAR')
        msh.sending_facility = HD(hd_1='Default Facility')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ONTARIO_HIS')
        msh.date_time_of_message = '20260407101500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OSC00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')

        # .. build SFT ..
        sft = SFT()
        sft.software_vendor_organization = XON(xon_1='OSCAR McMaster')
        sft.software_certified_version_or_release_number = '19.12'
        sft.software_binary_id = 'OSCAR EMR'
        sft.software_install_date = '20260101'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7890123456', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Bergeron', xpn_2='Chloe', xpn_3='Sylvie', xpn_5='Mme')
        pid.date_time_of_birth = '19950812'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='63 Sussex Dr', xad_3='Ottawa', xad_4='ON', xad_5='K1N 6Z6', xad_6='CA')
        pid.pid_13 = '^^PH^6135557890'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD007', ei_2='OSCAR')
        obr.filler_order_number = EI(ei_1='SPE007', ei_2='GAMMA_DYNACARE')
        obr.universal_service_identifier = CWE(cwe_1='PNS', cwe_2='Prenatal Screening', cwe_3='LN')
        obr.observation_date_time = '20260407080000'
        obr.obr_16 = '7890123456^Bergeron^Chloe S^^^^'
        obr.results_rpt_status_chng_date_time = '20260407101500'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='48803-1', cwe_2='AFP', cwe_3='LN')
        obx.obx_5 = '32.5'
        obx.units = CWE(cwe_1='kU/L')
        obx.reference_range = '10.0-150.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2106-3', cwe_2='Beta hCG', cwe_3='LN')
        obx_2.obx_5 = '45000'
        obx_2.units = CWE(cwe_1='IU/L')
        obx_2.nature_of_abnormal_test = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2243-4', cwe_2='Estriol', cwe_3='LN')
        obx_3.obx_5 = '5.2'
        obx_3.units = CWE(cwe_1='nmol/L')
        obx_3.nature_of_abnormal_test = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='49246-2', cwe_2='Screen Result', cwe_3='LN')
        obx_4.obx_5 = 'Screen Negative'
        obx_4.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Risk assessment: Trisomy 21 <1:10000, Trisomy 18 <1:10000, ONTD <1:10000.'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4
        observation_4.nte = nte

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
        msg.sft = sft
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
    """ Based on live/ca/ca-oscar-emr.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSCAR')
        msh.sending_facility = HD(hd_1='Default Facility')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ONTARIO_HIS')
        msh.date_time_of_message = '20260408134500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OSC00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')

        # .. build SFT ..
        sft = SFT()
        sft.software_vendor_organization = XON(xon_1='OSCAR McMaster')
        sft.software_certified_version_or_release_number = '19.12'
        sft.software_binary_id = 'OSCAR EMR'
        sft.software_install_date = '20260101'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='8901234567', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Leblanc', xpn_2='Raymond', xpn_3='Andre', xpn_5='Mr')
        pid.date_time_of_birth = '19480318'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='25 Main St', xad_3='Stratford', xad_4='ON', xad_5='N5A 1S1', xad_6='CA')
        pid.pid_13 = '^^PH^5195558901'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD008', ei_2='OSCAR')
        obr.filler_order_number = EI(ei_1='SPE008', ei_2='LIFELABS')
        obr.universal_service_identifier = CWE(cwe_1='COAG', cwe_2='Coagulation Panel', cwe_3='LN')
        obr.observation_date_time = '20260408074500'
        obr.obr_16 = '8901234567^Leblanc^Raymond A^^^^'
        obr.results_rpt_status_chng_date_time = '20260408134500'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='PT', cwe_3='LN')
        obx.obx_5 = '18.5'
        obx.units = CWE(cwe_1='s')
        obx.reference_range = '11.0-13.5'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx_2.obx_5 = '2.8'
        obx_2.reference_range = '2.0-3.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Therapeutic range for mechanical valve. Patient on warfarin 5mg daily.'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2
        observation_2.nte = nte

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
        msg.sft = sft
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
    """ Based on live/ca/ca-oscar-emr.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSCAR')
        msh.sending_facility = HD(hd_1='Default Facility')
        msh.receiving_application = HD(hd_1='REPO')
        msh.receiving_facility = HD(hd_1='DOC_REPO')
        msh.date_time_of_message = '20260409150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OSC00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')

        # .. build SFT ..
        sft = SFT()
        sft.software_vendor_organization = XON(xon_1='OSCAR McMaster')
        sft.software_certified_version_or_release_number = '19.12'
        sft.software_binary_id = 'OSCAR EMR'
        sft.software_install_date = '20260101'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='9012345678', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Charbonneau', xpn_2='Nathalie', xpn_3='Louise', xpn_5='Mme')
        pid.date_time_of_birth = '19820504'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='100 Wellington St', xad_3='Barrie', xad_4='ON', xad_5='L4M 3A3', xad_6='CA')
        pid.pid_13 = '^^PH^7055559012'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD009', ei_2='OSCAR')
        obr.filler_order_number = EI(ei_1='DOC009', ei_2='DOC_REPO')
        obr.universal_service_identifier = CWE(cwe_1='CONSULT', cwe_2='Consultation Report', cwe_3='LN')
        obr.observation_date_time = '20260409120000'
        obr.obr_16 = '9012345678^Charbonneau^Nathalie L^^^^'
        obr.results_rpt_status_chng_date_time = '20260409150000'
        obr.diagnostic_serv_sect_id = 'DOC'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Consultation Report PDF', cwe_3='LN')
        obx.obx_5 = (
            '^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2Jq'
        )
        obx.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Cardiology consultation report for Dr. Gauthier re: atrial fibrillation management.'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx
        observation.nte = nte

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.obr = obr
        order_observation.observation = observation

        # .. build the PATIENT_RESULT group ..
        patient_result = OruR01PatientResult()
        patient_result.patient = patient
        patient_result.order_observation = order_observation

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.sft = sft
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
    """ Based on live/ca/ca-oscar-emr.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSCAR')
        msh.sending_facility = HD(hd_1='Default Facility')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ONTARIO_HIS')
        msh.date_time_of_message = '20260410091500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OSC00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')

        # .. build SFT ..
        sft = SFT()
        sft.software_vendor_organization = XON(xon_1='OSCAR McMaster')
        sft.software_certified_version_or_release_number = '19.12'
        sft.software_binary_id = 'OSCAR EMR'
        sft.software_install_date = '20260101'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0123456789', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Ouellet', xpn_2='Pierre', xpn_3='Jean', xpn_5='Mr')
        pid.date_time_of_birth = '19780922'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='85 Albert St', xad_3='Waterloo', xad_4='ON', xad_5='N2L 3S1', xad_6='CA')
        pid.pid_13 = '^^PH^5195550123'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD010', ei_2='OSCAR')
        obr.filler_order_number = EI(ei_1='SPE010', ei_2='LIFELABS')
        obr.universal_service_identifier = CWE(cwe_1='ELEC', cwe_2='Electrolyte Panel', cwe_3='LN')
        obr.observation_date_time = '20260410074500'
        obr.obr_16 = '0123456789^Ouellet^Pierre J^^^^'
        obr.results_rpt_status_chng_date_time = '20260410091500'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodium', cwe_3='LN')
        obx.obx_5 = '128'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '136-145'
        obx.interpretation_codes = CWE(cwe_1='LL')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium', cwe_3='LN')
        obx_2.obx_5 = '5.6'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '3.5-5.1'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2075-0', cwe_2='Chloride', cwe_3='LN')
        obx_3.obx_5 = '96'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '98-106'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1963-8', cwe_2='Bicarbonate', cwe_3='LN')
        obx_4.obx_5 = '20'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '22-29'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Critical: Sodium 128 mmol/L. Physician notified at 0920.'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4
        observation_4.nte = nte

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
        msg.sft = sft
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
    """ Based on live/ca/ca-oscar-emr.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSCAR')
        msh.sending_facility = HD(hd_1='Default Facility')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ONTARIO_HIS')
        msh.date_time_of_message = '20260411113000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OSC00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')

        # .. build SFT ..
        sft = SFT()
        sft.software_vendor_organization = XON(xon_1='OSCAR McMaster')
        sft.software_certified_version_or_release_number = '19.12'
        sft.software_binary_id = 'OSCAR EMR'
        sft.software_install_date = '20260101'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1122334455', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Ahmed', xpn_2='Fatima', xpn_3='Zahra', xpn_5='Ms')
        pid.date_time_of_birth = '19650713'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='412 Dundas St W', xad_3='Toronto', xad_4='ON', xad_5='M5T 1G9', xad_6='CA')
        pid.pid_13 = '^^PH^4165551122'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD011', ei_2='OSCAR')
        obr.filler_order_number = EI(ei_1='SPE011', ei_2='GAMMA_DYNACARE')
        obr.universal_service_identifier = CWE(cwe_1='RENAL', cwe_2='Renal Function Panel', cwe_3='LN')
        obr.observation_date_time = '20260411081000'
        obr.obr_16 = '1122334455^Ahmed^Fatima Z^^^^'
        obr.results_rpt_status_chng_date_time = '20260411113000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine', cwe_3='LN')
        obx.obx_5 = '182'
        obx.units = CWE(cwe_1='umol/L')
        obx.reference_range = '50-98'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='48642-3', cwe_2='eGFR', cwe_3='LN')
        obx_2.obx_5 = '28'
        obx_2.units = CWE(cwe_1='mL/min/1.73m2')
        obx_2.reference_range = '>60'
        obx_2.interpretation_codes = CWE(cwe_1='LL')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea', cwe_3='LN')
        obx_3.obx_5 = '18.5'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '2.1-8.5'
        obx_3.interpretation_codes = CWE(cwe_1='HH')
        obx_3.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'eGFR 28 mL/min indicates Stage 4 CKD. Nephrology referral recommended.'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3
        observation_3.nte = nte

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
        msg.sft = sft
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
    """ Based on live/ca/ca-oscar-emr.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSCAR')
        msh.sending_facility = HD(hd_1='Default Facility')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ONTARIO_HIS')
        msh.date_time_of_message = '20260412140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OSC00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')

        # .. build SFT ..
        sft = SFT()
        sft.software_vendor_organization = XON(xon_1='OSCAR McMaster')
        sft.software_certified_version_or_release_number = '19.12'
        sft.software_binary_id = 'OSCAR EMR'
        sft.software_install_date = '20260101'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2233445566', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Leclerc', xpn_2='Genevieve', xpn_3='Madeleine', xpn_5='Mme')
        pid.date_time_of_birth = '19850301'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='90 Elgin St', xad_3='Ottawa', xad_4='ON', xad_5='K1P 5K1', xad_6='CA')
        pid.pid_13 = '^^PH^6135552233'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD012', ei_2='OSCAR')
        obr.filler_order_number = EI(ei_1='SPE012', ei_2='CML_HEALTHCARE')
        obr.universal_service_identifier = CWE(cwe_1='PAP', cwe_2='Papanicolaou Smear', cwe_3='LN')
        obr.observation_date_time = '20260412093000'
        obr.obr_16 = '2233445566^Leclerc^Genevieve M^^^^'
        obr.results_rpt_status_chng_date_time = '20260412140000'
        obr.diagnostic_serv_sect_id = 'CYT'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='19762-4', cwe_2='General Categorization', cwe_3='LN')
        obx.obx_5 = 'Epithelial Cell Abnormality'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='19764-0', cwe_2='Statement of Adequacy', cwe_3='LN')
        obx_2.obx_5 = 'Satisfactory for evaluation'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'FT'
        obx_3.observation_identifier = CWE(cwe_1='19765-7', cwe_2='Interpretation', cwe_3='LN')
        obx_3.obx_5 = 'Low-grade squamous intraepithelial lesion (LSIL). HPV testing recommended.'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
        msg.sft = sft
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
    """ Based on live/ca/ca-oscar-emr.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSCAR')
        msh.sending_facility = HD(hd_1='Default Facility')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ONTARIO_HIS')
        msh.date_time_of_message = '20260413100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OSC00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')

        # .. build SFT ..
        sft = SFT()
        sft.software_vendor_organization = XON(xon_1='OSCAR McMaster')
        sft.software_certified_version_or_release_number = '19.12'
        sft.software_binary_id = 'OSCAR EMR'
        sft.software_install_date = '20260101'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3344556677', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Martineau', xpn_2='Denis', xpn_3='Claude', xpn_5='Mr')
        pid.date_time_of_birth = '19560218'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='340 Riverside Dr', xad_3='Windsor', xad_4='ON', xad_5='N9A 5K3', xad_6='CA')
        pid.pid_13 = '^^PH^5195553344'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD013', ei_2='OSCAR')
        obr.filler_order_number = EI(ei_1='SPE013', ei_2='LIFELABS')
        obr.universal_service_identifier = CWE(cwe_1='PSA', cwe_2='Prostate Specific Antigen', cwe_3='LN')
        obr.observation_date_time = '20260413074500'
        obr.obr_16 = '3344556677^Martineau^Denis C^^^^'
        obr.results_rpt_status_chng_date_time = '20260413100000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2857-1', cwe_2='PSA', cwe_3='LN')
        obx.obx_5 = '6.2'
        obx.units = CWE(cwe_1='ug/L')
        obx.reference_range = '0.0-4.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='10886-0', cwe_2='Free PSA', cwe_3='LN')
        obx_2.obx_5 = '0.9'
        obx_2.units = CWE(cwe_1='ug/L')
        obx_2.nature_of_abnormal_test = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='12841-3', cwe_2='Free/Total PSA Ratio', cwe_3='LN')
        obx_3.obx_5 = '0.15'
        obx_3.reference_range = '>0.25'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'PSA elevated. Free/Total ratio 15% suggests further investigation. Urology referral advised.'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3
        observation_3.nte = nte

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
        msg.sft = sft
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
    """ Based on live/ca/ca-oscar-emr.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSCAR')
        msh.sending_facility = HD(hd_1='Default Facility')
        msh.receiving_application = HD(hd_1='REPO')
        msh.receiving_facility = HD(hd_1='DOC_REPO')
        msh.date_time_of_message = '20260414153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OSC00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')

        # .. build SFT ..
        sft = SFT()
        sft.software_vendor_organization = XON(xon_1='OSCAR McMaster')
        sft.software_certified_version_or_release_number = '19.12'
        sft.software_binary_id = 'OSCAR EMR'
        sft.software_install_date = '20260101'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='4455667788', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Renaud', xpn_2='Sylvain', xpn_3='Michel', xpn_5='Mr')
        pid.date_time_of_birth = '19711105'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='22 Front St', xad_3='Belleville', xad_4='ON', xad_5='K8N 2Y8', xad_6='CA')
        pid.pid_13 = '^^PH^6135554455'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD014', ei_2='OSCAR')
        obr.filler_order_number = EI(ei_1='DOC014', ei_2='DOC_REPO')
        obr.universal_service_identifier = CWE(cwe_1='ECG', cwe_2='Electrocardiogram', cwe_3='LN')
        obr.observation_date_time = '20260414100000'
        obr.obr_16 = '4455667788^Renaud^Sylvain M^^^^'
        obr.results_rpt_status_chng_date_time = '20260414153000'
        obr.diagnostic_serv_sect_id = 'CARD'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='8601-7', cwe_2='ECG Interpretation', cwe_3='LN')
        obx.obx_5 = 'Normal sinus rhythm. Rate 72 bpm. Normal axis. No ST changes. No Q waves. Normal intervals.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='ECG Tracing', cwe_3='LN')
        obx_2.obx_5 = (
            '^IM^TIFF^Base64^'
            'SUkqAAgAAAAIAAABAwABAAAAoAYAAAEBAwABAAAAIAQAAAIBAwABAAAAAQAAAAMBAwABAAAABQAAAAYBAwABAAAAAQAAABEBBAABAAAACAAAABIBAwABAAAAAQAAABoBBQABAAAAcgAA'
            'ABsBBQABAAAA'
        )
        obx_2.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = '12-lead ECG performed. Compared to previous ECG from 20250901, no significant interval change.'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2
        observation_2.nte = nte

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
        msg.sft = sft
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
    """ Based on live/ca/ca-oscar-emr.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSCAR')
        msh.sending_facility = HD(hd_1='Default Facility')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ONTARIO_HIS')
        msh.date_time_of_message = '20260415091000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OSC00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')

        # .. build SFT ..
        sft = SFT()
        sft.software_vendor_organization = XON(xon_1='OSCAR McMaster')
        sft.software_certified_version_or_release_number = '19.12'
        sft.software_binary_id = 'OSCAR EMR'
        sft.software_install_date = '20260101'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='5566778899', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Wong', xpn_2='Mei-Lin', xpn_5='Ms')
        pid.date_time_of_birth = '19830520'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='150 Bloor St E', xad_3='Toronto', xad_4='ON', xad_5='M4W 1B8', xad_6='CA')
        pid.pid_13 = '^^PH^4165555566'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD015', ei_2='OSCAR')
        obr.filler_order_number = EI(ei_1='SPE015', ei_2='LIFELABS')
        obr.universal_service_identifier = CWE(cwe_1='VIT', cwe_2='Vitamin Panel', cwe_3='LN')
        obr.observation_date_time = '20260415074500'
        obr.obr_16 = '5566778899^Wong^Mei-Lin^^^^'
        obr.results_rpt_status_chng_date_time = '20260415091000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1989-3', cwe_2='Vitamin D 25-Hydroxy', cwe_3='LN')
        obx.obx_5 = '38'
        obx.units = CWE(cwe_1='nmol/L')
        obx.reference_range = '75-250'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2132-9', cwe_2='Vitamin B12', cwe_3='LN')
        obx_2.obx_5 = '145'
        obx_2.units = CWE(cwe_1='pmol/L')
        obx_2.reference_range = '138-652'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Vitamin D insufficient. Consider supplementation 1000 IU daily.'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2
        observation_2.nte = nte

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
        msg.sft = sft
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
    """ Based on live/ca/ca-oscar-emr.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSCAR')
        msh.sending_facility = HD(hd_1='Default Facility')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ONTARIO_HIS')
        msh.date_time_of_message = '20260416110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OSC00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')

        # .. build SFT ..
        sft = SFT()
        sft.software_vendor_organization = XON(xon_1='OSCAR McMaster')
        sft.software_certified_version_or_release_number = '19.12'
        sft.software_binary_id = 'OSCAR EMR'
        sft.software_install_date = '20260101'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='6677889900', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Fortin', xpn_2='Isabelle', xpn_3='Claire', xpn_5='Mme')
        pid.date_time_of_birth = '19920808'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='75 Brant St', xad_3='Burlington', xad_4='ON', xad_5='L7R 2H2', xad_6='CA')
        pid.pid_13 = '^^PH^9055556677'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD016', ei_2='OSCAR')
        obr.filler_order_number = EI(ei_1='SPE016', ei_2='GAMMA_DYNACARE')
        obr.universal_service_identifier = CWE(cwe_1='IRON', cwe_2='Iron Studies', cwe_3='LN')
        obr.observation_date_time = '20260416081000'
        obr.obr_16 = '6677889900^Fortin^Isabelle C^^^^'
        obr.results_rpt_status_chng_date_time = '20260416110000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2498-4', cwe_2='Iron', cwe_3='LN')
        obx.obx_5 = '6'
        obx.units = CWE(cwe_1='umol/L')
        obx.reference_range = '9-30'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2502-3', cwe_2='Transferrin Saturation', cwe_3='LN')
        obx_2.obx_5 = '0.08'
        obx_2.units = CWE(cwe_1='fraction')
        obx_2.reference_range = '0.20-0.50'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2276-4', cwe_2='Ferritin', cwe_3='LN')
        obx_3.obx_5 = '8'
        obx_3.units = CWE(cwe_1='ug/L')
        obx_3.reference_range = '12-150'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2500-7', cwe_2='TIBC', cwe_3='LN')
        obx_4.obx_5 = '78'
        obx_4.units = CWE(cwe_1='umol/L')
        obx_4.reference_range = '45-72'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Iron deficiency anemia pattern. Consider GI evaluation if no obvious source.'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4
        observation_4.nte = nte

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
        msg.sft = sft
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
    """ Based on live/ca/ca-oscar-emr.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSCAR')
        msh.sending_facility = HD(hd_1='Default Facility')
        msh.receiving_application = HD(hd_1='REPO')
        msh.receiving_facility = HD(hd_1='DOC_REPO')
        msh.date_time_of_message = '20260417140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OSC00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')

        # .. build SFT ..
        sft = SFT()
        sft.software_vendor_organization = XON(xon_1='OSCAR McMaster')
        sft.software_certified_version_or_release_number = '19.12'
        sft.software_binary_id = 'OSCAR EMR'
        sft.software_install_date = '20260101'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7788990011', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Caron', xpn_2='Michel', xpn_3='Andre', xpn_5='Mr')
        pid.date_time_of_birth = '19681220'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='45 York St', xad_3='Hamilton', xad_4='ON', xad_5='L8R 3K2', xad_6='CA')
        pid.pid_13 = '^^PH^9055557788'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD017', ei_2='OSCAR')
        obr.filler_order_number = EI(ei_1='DOC017', ei_2='DOC_REPO')
        obr.universal_service_identifier = CWE(cwe_1='XSPINE', cwe_2='Cervical Spine Xray', cwe_3='LN')
        obr.observation_date_time = '20260417110000'
        obr.obr_16 = '7788990011^Caron^Michel A^^^^'
        obr.results_rpt_status_chng_date_time = '20260417140000'
        obr.diagnostic_serv_sect_id = 'RAD'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic Imaging Report', cwe_3='LN')
        obx.obx_5 = (
            'AP and lateral views of the cervical spine. Loss of normal lordosis. Degenerative disc disease at C5-C6 and C6-C7. No fracture or subluxatio'
            'n. Prevertebral soft tissues normal.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='Cervical Spine Image', cwe_3='LN')
        obx_2.obx_5 = '^IM^PNG^Base64^iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
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
        msg.sft = sft
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
    """ Based on live/ca/ca-oscar-emr.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSCAR')
        msh.sending_facility = HD(hd_1='Default Facility')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ONTARIO_HIS')
        msh.date_time_of_message = '20260418143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OSC00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')

        # .. build SFT ..
        sft = SFT()
        sft.software_vendor_organization = XON(xon_1='OSCAR McMaster')
        sft.software_certified_version_or_release_number = '19.12'
        sft.software_binary_id = 'OSCAR EMR'
        sft.software_install_date = '20260101'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='8899001122', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Plante', xpn_2='Marie-Eve', xpn_5='Mme')
        pid.date_time_of_birth = '19870215'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='225 Laurier Blvd', xad_3='Gatineau', xad_4='QC', xad_5='J8X 3W8', xad_6='CA')
        pid.pid_13 = '^^PH^8195558899'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD018', ei_2='OSCAR')
        obr.filler_order_number = EI(ei_1='SPE018', ei_2='LIFELABS')
        obr.universal_service_identifier = CWE(cwe_1='GTT', cwe_2='Glucose Tolerance Test', cwe_3='LN')
        obr.observation_date_time = '20260418075000'
        obr.obr_16 = '8899001122^Plante^Marie-Eve^^^^'
        obr.results_rpt_status_chng_date_time = '20260418143000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1558-6', cwe_2='Glucose Fasting', cwe_3='LN')
        obx.obx_5 = '5.8'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.3-5.5'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1518-0', cwe_2='Glucose 1h', cwe_3='LN')
        obx_2.obx_5 = '11.2'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '<10.0'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='1530-5', cwe_2='Glucose 2h', cwe_3='LN')
        obx_3.obx_5 = '8.9'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '<7.8'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Results consistent with gestational diabetes mellitus. Refer to diabetes education program.'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3
        observation_3.nte = nte

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
        msg.sft = sft
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
    """ Based on live/ca/ca-oscar-emr.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSCAR')
        msh.sending_facility = HD(hd_1='Default Facility')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ONTARIO_HIS')
        msh.date_time_of_message = '20260419101500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OSC00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')

        # .. build SFT ..
        sft = SFT()
        sft.software_vendor_organization = XON(xon_1='OSCAR McMaster')
        sft.software_certified_version_or_release_number = '19.12'
        sft.software_binary_id = 'OSCAR EMR'
        sft.software_install_date = '20260101'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='9900112233', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Simard', xpn_2='Etienne', xpn_3='Paul', xpn_5='Mr')
        pid.date_time_of_birth = '20120901'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='60 Parkdale Ave', xad_3='Ottawa', xad_4='ON', xad_5='K1Y 1E5', xad_6='CA')
        pid.pid_13 = '^^PH^6135559900'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD019', ei_2='OSCAR')
        obr.filler_order_number = EI(ei_1='SPE019', ei_2='GAMMA_DYNACARE')
        obr.universal_service_identifier = CWE(cwe_1='IGE', cwe_2='Allergen Specific IgE Panel', cwe_3='LN')
        obr.observation_date_time = '20260419083000'
        obr.obr_16 = '9900112233^Simard^Etienne P^^^^'
        obr.results_rpt_status_chng_date_time = '20260419101500'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='19113-0', cwe_2='Total IgE', cwe_3='LN')
        obx.obx_5 = '285'
        obx.units = CWE(cwe_1='kU/L')
        obx.reference_range = '0-100'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6844-5', cwe_2='Cat Dander IgE', cwe_3='LN')
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
        obx_3.observation_identifier = CWE(cwe_1='6158-0', cwe_2='Dust Mite IgE', cwe_3='LN')
        obx_3.obx_5 = '12.3'
        obx_3.units = CWE(cwe_1='kU/L')
        obx_3.reference_range = '<0.35'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='6206-7', cwe_2='Peanut IgE', cwe_3='LN')
        obx_4.obx_5 = '0.08'
        obx_4.units = CWE(cwe_1='kU/L')
        obx_4.reference_range = '<0.35'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='6248-9', cwe_2='Timothy Grass IgE', cwe_3='LN')
        obx_5.obx_5 = '22.1'
        obx_5.units = CWE(cwe_1='kU/L')
        obx_5.reference_range = '<0.35'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Significant sensitization to cat dander, dust mite, and timothy grass. Peanut negative. Refer to allergist.'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5
        observation_5.nte = nte

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
        msg.sft = sft
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
    """ Based on live/ca/ca-oscar-emr.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OSCAR')
        msh.sending_facility = HD(hd_1='Default Facility')
        msh.receiving_application = HD(hd_1='REPO')
        msh.receiving_facility = HD(hd_1='DOC_REPO')
        msh.date_time_of_message = '20260420160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OSC00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')

        # .. build SFT ..
        sft = SFT()
        sft.software_vendor_organization = XON(xon_1='OSCAR McMaster')
        sft.software_certified_version_or_release_number = '19.12'
        sft.software_binary_id = 'OSCAR EMR'
        sft.software_install_date = '20260101'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0011223344', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Hebert', xpn_2='Andre', xpn_3='Joseph', xpn_5='Mr')
        pid.date_time_of_birth = '19580415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='8 Rideau Canal Dr', xad_3='Ottawa', xad_4='ON', xad_5='K1S 5B6', xad_6='CA')
        pid.pid_13 = '^^PH^6135550011'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD020', ei_2='OSCAR')
        obr.filler_order_number = EI(ei_1='DOC020', ei_2='DOC_REPO')
        obr.universal_service_identifier = CWE(cwe_1='REF', cwe_2='Referral Letter', cwe_3='LN')
        obr.observation_date_time = '20260420130000'
        obr.obr_16 = '0011223344^Hebert^Andre J^^^^'
        obr.results_rpt_status_chng_date_time = '20260420160000'
        obr.diagnostic_serv_sect_id = 'DOC'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='11488-4', cwe_2='Consultation Note', cwe_3='LN')
        obx.obx_5 = (
            'Dear Dr. Morin: I am referring Mr. Hebert for assessment of progressive dyspnea on exertion and bilateral lower extremity edema. Echo sugges'
            'ted EF 35%. Please see attached report.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Referral Letter PDF', cwe_3='LN')
        obx_2.obx_5 = (
            '^AP^^Base64^'
            'JVBERi0xLjUKJdDUxdgKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKL01hcmtJbmZvIDw8Ci9NYXJrZWQgdHJ1ZQo+PgovU3RydWN0VHJlZVJvb3QgMyAwIFIK'
            'Pj4KZW5kb2Jq'
        )
        obx_2.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Referral to cardiology, Dr. Morin, Ottawa Heart Institute. Urgent.'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2
        observation_2.nte = nte

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
        msg.sft = sft
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
