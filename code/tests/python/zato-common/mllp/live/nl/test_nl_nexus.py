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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, DLD, EI, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01Observation, OmlO21Insurance, OmlO21Observation, OmlO21ObservationRequest, OmlO21Order, \
    OmlO21Patient, OmlO21PatientVisit, OmlO21Timing, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12LocationResource, SiuS12Patient, SiuS12PersonnelResource, SiuS12Resources
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A05, ADT_A38, BAR_P12, OML_O21, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIL, AIP, DG1, EVN, IN1, IN2, MSA, MSH, NTE, OBR, OBX, ORC, PID, PR1, PV1, PV2, RGS, SCH, SFT, TQ1
from zato.hl7v2.z_segments import ZBE, ZMP

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('nl', 'nl-nexus.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/nl/nl-nexus.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.msh_2 = '^_\\&'
        msh.sending_application = HD(hd_1='ZorgDomein')
        msh.date_time_of_message = '20160324163509+0100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'ZD200046119'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_4='NLMINBIZA', cx_5='NNNLD')
        pid.patient_name = XPN(xpn_1='van Dijk&van&Dijk', xpn_2='J', xpn_3='M', xpn_7='L')
        pid.date_time_of_birth = '20000101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Herengracht 88  hs&Herengracht&88', xad_2='hs', xad_3='Amsterdam', xad_5='1015BN', xad_6='NL', xad_7='H')
        pid.pid_13 = '020-6234871_^NET^Internet^j.vandijk@gmail.nl'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ZD200046119')
        orc.date_time_of_order_event = '20160324163432+0100'
        orc.orc_10 = '^&&het Wolters^F.G.'
        orc.orc_12 = '01004567^&&van Brouwer^Z.Z.^^^^^^VEKTIS'
        orc.orc_14 = '015-2222222'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ZD200046119')
        obr.universal_service_identifier = CWE(cwe_1='CIS', cwe_2='Cardiologie', cwe_3='ZORGDOMEIN')
        obr.observation_date_time = '20160324163432+0100'
        obr.obr_16 = '01004567^&&van Brouwer^Z.Z.^^^^^^VEKTIS'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='VB', cwe_3='123')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='CARHAR', cwe_2='Hartfalen', cwe_3='ZORGDOMEIN')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKP7/KQovQ3JlYXRvciAo/v8AdwBrAGgAdABtAGwAdABvAHAAZABmACAAMAAuADEAMgAuADIALgExKQovUHJvZHVjZXIgKP7/AFEAdAAg'
            'ADQALgA4AC4ANikKL0NyZWF0aW9uRGF0ZSAoRDoyMDE2MDMyNDE2MzUwOCswMScwMCcpCj4+'
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'FT'
        obx_3.observation_identifier = CWE(cwe_1='CARCOA001', cwe_2='consult cardioloog', cwe_3='ZORGDOMEIN')
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
    """ Based on live/nl/nl-nexus.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.msh_2 = '^_\\&'
        msh.sending_application = HD(hd_1='ZorgDomein')
        msh.date_time_of_message = '20160324163441+0100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'ZD200046119'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_4='NLMINBIZA', cx_5='NNNLD')
        pid.patient_name = XPN(xpn_1='Bakker&Bakker', xpn_2='A', xpn_3='H', xpn_7='L')
        pid.date_time_of_birth = '19850722'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Keizersgracht 312  II&Keizersgracht&312', xad_2='II', xad_3='Utrecht', xad_5='3511EX', xad_6='NL', xad_7='H')
        pid.pid_13 = '030-2519843'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ZD200046119')
        orc.date_time_of_order_event = '20160324163432+0100'
        orc.orc_10 = '^&&het Timmerman^R.S.'
        orc.orc_12 = '01004567^&&van Meijer^P.A.^^^^^^VEKTIS'
        orc.orc_14 = '015-2222222'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ZD200046119')
        obr.universal_service_identifier = CWE(cwe_1='CIS', cwe_2='Cardiologie', cwe_3='ZORGDOMEIN')
        obr.observation_date_time = '20160324163432+0100'
        obr.obr_16 = '01004567^&&van Meijer^P.A.^^^^^^VEKTIS'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='AF', cwe_3='123')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='CARHAR', cwe_2='Hartfalen', cwe_3='ZORGDOMEIN')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKP7/KQovQ3JlYXRvciAo/v8AdwBrAGgAdABtAGwAdABvAHAAZABmACAAMAAuADEAMgAuADIALgExKQovUHJvZHVjZXIgKP7/AFEAdAAg'
            'ADQALgA4AC4ANikKL0NyZWF0aW9uRGF0ZSAoRDoyMDE2MDMyNDE2MzQ0MSswMScwMCcpCj4+'
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'FT'
        obx_3.observation_identifier = CWE(cwe_1='CARCOA001', cwe_2='consult cardioloog', cwe_3='ZORGDOMEIN')
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
    """ Based on live/nl/nl-nexus.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SUBx')
        msh.receiving_application = HD(hd_1='PAT')
        msh.date_time_of_message = '20040328112408'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = '47'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'DEU'
        msh.character_set = '8859/1'
        msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.1', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20040328112408'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='12345', cx_4='YKIS', cx_5='PI')
        pid.patient_name = XPN(xpn_1='de Jong', xpn_2='Willem', xpn_7='L', xpn_8='A', xpn_11='G')
        pid.date_time_of_birth = '19610527'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Prinsengracht 78&Prinsengracht&78', xad_3='Amsterdam', xad_4='XA-DE-NW', xad_5='1017KT', xad_6='NLD', xad_7='H')
        pid.pid_13 = '^PRN^PH^^31^20^6234567^^^^^020/6234567'
        pid.pid_14 = '^WPN^PH^^31^20^7654321^^^^^020/7654321'
        pid.primary_language = CWE(cwe_1='NLD', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INN', pl_2='305', pl_3='1', pl_4='Erasmus MC', pl_6='N')
        pv1.attending_doctor = XCN(xcn_1='A1234', xcn_2='Visser', xcn_3='Adriaan')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='N')
        pv1.pv1_20 = '0815^^^Erasmus MC^VN'
        pv1.discharged_to_location = DLD(dld_1='000000')
        pv1.current_patient_balance = '20040328112400'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/nl/nl-nexus.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KIS')
        msh.sending_facility = HD(hd_1='ADT')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='ADT')
        msh.date_time_of_message = '200404011935'
        msh.message_type = MSG(msg_1='ADT', msg_2='A05', msg_3='ADT_A05')
        msh.message_control_id = 'ADT002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5', vid_2='DEU')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'DEU'
        msh.character_set = '8859/1'
        msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.42', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '200404011935'
        evn.event_occurred = '200404011645'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='12345', cx_4='Radboudumc', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Jansen', xpn_2='Femke', xpn_7='L', xpn_8='A', xpn_11='G')
        pid.date_time_of_birth = '19770325'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = [
            XAD(xad_1='Mariaplaats 14&Mariaplaats&14', xad_3='Utrecht', xad_7='H'),
            XAD(xad_1='Oudegracht 17&Oudegracht&17', xad_3='Utrecht', xad_7='BDL'),
        ]
        pid.pid_13 = '^PRN^PH^^31^30^2345678^^^^^030/2345678'
        pid.pid_14 = '^WPN^PH^^31^30^8765432^^^^^030/8765432'
        pid.primary_language = CWE(cwe_1='NLD', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        pid.birth_place = 'Radboudumc'
        pid.citizenship = CWE(cwe_1='NLD', cwe_3='HL70171')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.visit_number = CX(cx_1='4711', cx_4='Radboudumc', cx_5='VN')
        pv1.admit_date_time = '200404011654'

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/nl/nl-nexus.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KIS')
        msh.sending_facility = HD(hd_1='ADT')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='ADT')
        msh.date_time_of_message = '200404011935'
        msh.message_type = MSG(msg_1='ADT', msg_2='A38', msg_3='ADT_A38')
        msh.message_control_id = 'ADT002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'DEU'
        msh.character_set = '8859/1'
        msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.43', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '200404011935'
        evn.event_occurred = '200404011645'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='12345', cx_4='OLVG', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Mulder', xpn_2='Theodora', xpn_7='L', xpn_8='A', xpn_11='G')
        pid.date_time_of_birth = '19820914'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = [
            XAD(xad_1='Westerstraat 55&Westerstraat&55', xad_3='Rotterdam', xad_7='H'),
            XAD(xad_1='Coolsingel 103&Coolsingel&103', xad_3='Rotterdam', xad_7='BDL'),
        ]
        pid.pid_13 = '^PRN^PH^^31^10^4567890^^^^^010/4567890'
        pid.pid_14 = '^WPN^PH^^31^10^9876543^^^^^010/9876543'
        pid.primary_language = CWE(cwe_1='NLD', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='M', cwe_2='married', cwe_3='HL70002')
        pid.religion = CWE(cwe_1='CAT', cwe_3='HL70006')
        pid.birth_place = 'OLVG'
        pid.citizenship = CWE(cwe_1='NLD', cwe_3='HL70171')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='P')
        pv1.visit_number = CX(cx_1='0815', cx_4='OLVG', cx_5='VN')
        pv1.admit_date_time = '200404011645'

        # .. assemble the full message ..
        msg = ADT_A38()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/nl/nl-nexus.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KIS')
        msh.sending_facility = HD(hd_1='ADT')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='ADT')
        msh.date_time_of_message = '200510141345'
        msh.message_type = MSG(msg_1='BAR', msg_2='P12', msg_3='BAR_P12')
        msh.message_control_id = 'ADT03'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.66', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '200510141345'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='943246', cx_4='KIS', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Dekker', xpn_2='Jacobus', xpn_7='L')
        pid.date_time_of_birth = '19480403'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vondelstraat 4&Vondelstraat&4', xad_3='Den Haag', xad_4='XA-DE-BY', xad_5='2513AC', xad_6='NLD', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHI', pl_2='202', pl_3='2', pl_4='CH', pl_6='N')
        pv1.visit_number = CX(cx_1='654325', cx_4='KIS', cx_5='VN')
        pv1.delete_account_date = '000000'
        pv1.admit_date_time = '200510091820'

        # .. build ZBE ..
        zbe = ZBE()
        zbe.zbe_1 = '234345^KIS'
        zbe.zbe_2 = '200510121230'
        zbe.zbe_4 = 'REFERENCE'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K35.-', cwe_2='Akute Appendizitis', cwe_3='I10-2005')
        dg1.diagnosis_date_time = '200510141345'
        dg1.diagnosis_type = CWE(cwe_1='ED')
        dg1.diagnosis_priority = '1.1'
        dg1.diagnosing_clinician = XCN(xcn_1='432113', xcn_13='DN')
        dg1.diagnosis_identifier = EI(ei_1='23543', ei_2='KIS')
        dg1.diagnosis_action_code = 'A'

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='K35.-', cwe_2='Akute Appendizitis', cwe_3='I10-2005')
        dg1_2.diagnosis_date_time = '200510141345'
        dg1_2.diagnosis_type = CWE(cwe_1='AD')
        dg1_2.diagnosis_priority = '1.2'
        dg1_2.diagnosing_clinician = XCN(xcn_1='432113', xcn_13='DN')
        dg1_2.diagnosis_identifier = EI(ei_1='23544', ei_2='KIS')
        dg1_2.diagnosis_action_code = 'A'

        # .. build DG1 ..
        dg1_3 = DG1()
        dg1_3.set_id_dg1 = '3'
        dg1_3.diagnosis_code_dg1 = CWE(cwe_1='K35.0', cwe_2='Akute Appendizitis mit diffuser Peritonitis', cwe_3='I10-2005')
        dg1_3.diagnosis_date_time = '200510141345'
        dg1_3.diagnosis_type = CWE(cwe_1='BD')
        dg1_3.diagnosis_priority = '1.2'
        dg1_3.diagnosing_clinician = XCN(xcn_1='432113', xcn_13='DN')
        dg1_3.diagnosis_identifier = EI(ei_1='23545', ei_2='KIS')
        dg1_3.diagnosis_action_code = 'A'

        # .. assemble the full message ..
        msg = BAR_P12()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [zbe, dg1, dg1_2, dg1_3]

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
    """ Based on live/nl/nl-nexus.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KIS')
        msh.sending_facility = HD(hd_1='ADT')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='ADT')
        msh.date_time_of_message = '200510141345'
        msh.message_type = MSG(msg_1='BAR', msg_2='P12', msg_3='BAR_P12')
        msh.message_control_id = 'ADT03'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.66', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        # .. build SFT ..
        sft = SFT()
        sft.software_vendor_organization = XON(xon_1='KIS Hersteller GmbH', xon_2='L')
        sft.software_certified_version_or_release_number = '5.4.0'
        sft.software_product_name = 'KIS System A'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '200510141345'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='943246', cx_4='KIS', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Bos', xpn_2='Hendrik', xpn_7='L')
        pid.date_time_of_birth = '19530817'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(
            xad_1='Laan van Meerdervoort 92&Laan van Meerdervoort&92',
            xad_3='Den Haag',
            xad_4='XA-DE-BY',
            xad_5='2517AR',
            xad_6='NLD',
            xad_7='H',
        )

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHI', pl_2='202', pl_3='2', pl_4='CH', pl_6='N')
        pv1.visit_number = CX(cx_1='654325', cx_4='KIS', cx_5='VN')
        pv1.admit_date_time = '2005100510'

        # .. build ZBE ..
        zbe = ZBE()
        zbe.zbe_1 = '345345'
        zbe.zbe_2 = '20051013'
        zbe.zbe_4 = 'REFERENCE'

        # .. build PR1 ..
        pr1 = PR1()
        pr1.set_id_pr1 = '1'
        pr1.procedure_code = CNE(cne_1='8-901', cne_2='Inhalationsanästhesie', cne_3='O301-2005')
        pr1.procedure_date_time = '200510141415'
        pr1.procedure_minutes = '120'
        pr1.procedure_priority = '1'
        pr1.procedure_identifier = EI(ei_1='34325', ei_2='KIS')
        pr1.procedure_action_code = 'A'

        # .. build PR1 ..
        pr1_2 = PR1()
        pr1_2.set_id_pr1 = '2'
        pr1_2.procedure_code = CNE(cne_1='5-470.0', cne_2='Appendektomie, offen chirurgisch', cne_3='O301-2005')
        pr1_2.procedure_date_time = '200510141415'
        pr1_2.procedure_minutes = '90'
        pr1_2.procedure_priority = '2'
        pr1_2.procedure_identifier = EI(ei_1='34326', ei_2='KIS')
        pr1_2.procedure_action_code = 'A'

        # .. assemble the full message ..
        msg = BAR_P12()
        msg.msh = msh
        msg.sft = sft
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [zbe, pr1, pr1_2]

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
    """ Based on live/nl/nl-nexus.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KIS')
        msh.sending_facility = HD(hd_1='ADT')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='ADT')
        msh.date_time_of_message = '200510141345'
        msh.message_type = MSG(msg_1='BAR', msg_2='P12', msg_3='BAR_P12')
        msh.message_control_id = 'ADT03'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.66', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '200510141345'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='943246', cx_4='KIS', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Smit', xpn_2='Geert', xpn_7='L')
        pid.date_time_of_birth = '19590212'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Nassaulaan 28&Nassaulaan&28', xad_3='Eindhoven', xad_4='XA-DE-BY', xad_5='5611AA', xad_6='NLD', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHI', pl_2='202', pl_3='2', pl_4='CH', pl_6='N')
        pv1.visit_number = CX(cx_1='654325', cx_4='KIS', cx_5='VN')

        # .. build ZBE ..
        zbe = ZBE()
        zbe.zbe_1 = '234345^KIS'
        zbe.zbe_2 = '200510121230'
        zbe.zbe_4 = 'REFERENCE'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='N26 L V', cwe_2='Verdacht auf Schrumpfniere links', cwe_3='I10-2005')
        dg1.diagnosis_date_time = '200510141345'
        dg1.diagnosis_type = CWE(cwe_1='AD')
        dg1.diagnosis_priority = '1'
        dg1.diagnosing_clinician = XCN(xcn_1='432113', xcn_13='DN')
        dg1.diagnosis_identifier = EI(ei_1='23542134', ei_2='KIS')
        dg1.diagnosis_action_code = 'A'

        # .. build PR1 ..
        pr1 = PR1()
        pr1.set_id_pr1 = '1'
        pr1.procedure_code = CNE(cne_1='8-901', cne_2='Inhalationsanästhesie', cne_3='O301-2004')
        pr1.procedure_date_time = '200510141415'
        pr1.procedure_minutes = '120'
        pr1.procedure_identifier = EI(ei_1='34325', ei_2='KIS')
        pr1.procedure_action_code = 'A'

        # .. build PR1 ..
        pr1_2 = PR1()
        pr1_2.set_id_pr1 = '2'
        pr1_2.procedure_code = CNE(cne_1='5-470.0', cne_2='Appendektomie, offen chirurgisch', cne_3='O301-2004')
        pr1_2.procedure_date_time = '200510141415'
        pr1_2.procedure_minutes = '90'
        pr1_2.procedure_identifier = EI(ei_1='34326', ei_2='KIS')
        pr1_2.procedure_action_code = 'A'

        # .. assemble the full message ..
        msg = BAR_P12()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [zbe, dg1, pr1, pr1_2]

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
    """ Based on live/nl/nl-nexus.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SRC')
        msh.sending_facility = HD(hd_1='LABFACILITY')
        msh.receiving_application = HD(hd_1='LAB_DST')
        msh.receiving_facility = HD(hd_1='LABFACILITY')
        msh.date_time_of_message = '20180201120000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB00042'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='298471536', cx_4='NLMINBIZA', cx_5='NNNLD')
        pid.patient_name = XPN(xpn_1='Visser', xpn_2='Maria', xpn_7='L')
        pid.date_time_of_birth = '19650415'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Oudegracht 45', xad_3='Utrecht', xad_5='3511AB', xad_6='NL', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')

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
        orc.placer_order_number = EI(ei_1='ORD5678', ei_2='LAB_SRC')
        orc.filler_order_number = EI(ei_1='FIL9012', ei_2='LAB_DST')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD5678', ei_2='LAB_SRC')
        obr.filler_order_number = EI(ei_1='FIL9012', ei_2='LAB_DST')
        obr.universal_service_identifier = CWE(cwe_1='630-4', cwe_2='Bacteria identified', cwe_3='LN')
        obr.observation_date_time = '20180201090000'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='6652-2', cwe_2='Meropenem [Susceptibility] by Minimum inhibitory concentration (MIC)', cwe_3='LN')
        obx.obx_5 = '>=16'
        obx.units = CWE(cwe_1='mg/L')
        obx.interpretation_codes = CWE(cwe_1='null')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='7029-2', cwe_2='Meropenem [Susceptibility] by Gradient strip', cwe_3='LN')
        obx_2.obx_5 = '8,0'
        obx_2.units = CWE(cwe_1='mg/L')
        obx_2.interpretation_codes = CWE(cwe_1='null')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.observation_identifier = CWE(cwe_1='18943-1', cwe_2='Meropenem [Susceptibility]', cwe_3='LN')
        obx_3.interpretation_codes = CWE(cwe_1='R')
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
    """ Based on live/nl/nl-nexus.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='ISALA')
        msh.receiving_application = HD(hd_1='LAB_SYS')
        msh.receiving_facility = HD(hd_1='PATHOLOGY')
        msh.date_time_of_message = '202603011430'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '202603011430'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='Bakker', xcn_3='Elisabeth', xcn_6='RN')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN12345', cx_4='ISALA', cx_5='MR')
        pid.patient_name = XPN(xpn_1='van den Berg', xpn_2='Daan', xpn_3='Willem')
        pid.date_time_of_birth = '19800115'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='Stationsweg 23', xad_3='Zwolle', xad_4='OV', xad_5='8011CW', xad_6='NLD')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='0101', pl_3='01', pl_4='ISALA', pl_8='NURS')
        pv1.admission_type = CWE(cwe_1='E')
        pv1.attending_doctor = XCN(xcn_1='ATT1234', xcn_2='Timmerman', xcn_3='Floor', xcn_6='MD')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='N')
        pv1.pv1_20 = '0815^^^ISALA^VN'
        pv1.discharged_to_location = DLD(dld_1='000000')
        pv1.current_patient_balance = '202603011430'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='ZK001', cwe_2='Zilveren Kruis')
        in1.insurance_company_id = CX(cx_1='ZK')
        in1.insurance_company_name = XON(xon_1='Zilveren Kruis Achmea')
        in1.name_of_insured = XPN(xpn_1='van den Berg', xpn_2='Daan')
        in1.insureds_date_of_birth = '19800115'
        in1.insureds_address = XAD(xad_1='Stationsweg 23', xad_3='Zwolle', xad_4='OV', xad_5='8011CW')
        in1.policy_number = 'ZK87654321'

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
    """ Based on live/nl/nl-nexus.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='AMPHIA')
        msh.receiving_application = HD(hd_1='LAB_SYS')
        msh.receiving_facility = HD(hd_1='PATHOLOGY')
        msh.date_time_of_message = '202603011400'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'ORD00123'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN67890', cx_4='AMPHIA', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Wolters', xpn_2='Anneke', xpn_3='Margaretha')
        pid.date_time_of_birth = '19751208'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='0201', pl_3='01', pl_4='AMPHIA')
        pv1.attending_doctor = XCN(xcn_1='ATT5678', xcn_2='de Vries', xcn_3='Pieter', xcn_6='MD')

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
        orc.placer_order_number = EI(ei_1='ORD5678', ei_2='EPIC')
        orc.orc_12 = 'ATT5678^de Vries^Pieter^^^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD5678', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='FIL9012', ei_2='LAB_SYS')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='CMP', cwe_3='LN')
        obr.observation_date_time = '202603011400'
        obr.obr_15 = 'ATT5678^de Vries^Pieter^^^MD'

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
    """ Based on live/nl/nl-nexus.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SYS')
        msh.sending_facility = HD(hd_1='RIJNSTATE')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='RIJNSTATE')
        msh.date_time_of_message = '202603011630'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB00042'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN34567', cx_4='RIJNSTATE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Brouwer', xpn_2='Thijs', xpn_3='Jan')
        pid.date_time_of_birth = '19690304'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='0101', pl_3='01', pl_4='RIJNSTATE')

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
        orc.placer_order_number = EI(ei_1='ORD5678', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='FIL9012', ei_2='LAB_SYS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD5678', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='FIL9012', ei_2='LAB_SYS')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='CMP', cwe_3='LN')
        obr.observation_date_time = '202603011445'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose', cwe_3='LN')
        obx.obx_5 = '98'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '70-100'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine', cwe_3='LN')
        obx_2.obx_5 = '1.1'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '0.6-1.2'
        obx_2.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/nl/nl-nexus.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WCDataSend')
        msh.sending_facility = HD(hd_1='handle')
        msh.receiving_application = HD(hd_1='wc_hl7d')
        msh.receiving_facility = HD(hd_1='recv_facil')
        msh.date_time_of_message = '20210423091057'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'DSD1619205057152978'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='2588939')
        sch.filler_appointment_id = EI(ei_1='2677255')
        sch.appointment_reason = CWE(cwe_1='ppd 2nd step')
        sch.appointment_type = CWE(cwe_1='NURS', cwe_2='Nurse Encounter')
        sch.sch_9 = '15'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^^202104270815^202104270830'
        sch.filler_status_code = CWE(cwe_1='BOOKED')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.pid_2 = '745832'
        pid.patient_identifier_list = [
            CX(cx_1='745832', cx_4='MR&1.2.840.114398.1.5881.2&ISO', cx_5='MR', cx_6='1.2.840.114398.1.5881.2&MR&ISO'),
            CX(cx_1='963258', cx_4='ECW&1.2.840.114398.1.5881.3&ISO', cx_5='MR', cx_6='1.2.840.114398.1.5881.3&ECW&ISO'),
            CX(cx_1='192837465', cx_5='SS'),
        ]
        pid.pid_4 = '745832^^^MR&1.2.840.114398.1.5881.1&ISO'
        pid.patient_name = XPN(xpn_1='de Groot', xpn_2='Saskia', xpn_3='L')
        pid.date_time_of_birth = '19830711000000'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='Asian')
        pid.patient_address = XAD(xad_1='Dorpsstraat 17', xad_3='Leiden', xad_4='ZH', xad_5='2311EA', xad_6='NL')
        pid.pid_13 = '071-5234567^PRN^PH^s.degroot@email.nl~071-5234568^PRN^CP'
        pid.pid_14 = '071-5234569^WPN^PH'
        pid.primary_language = CWE(cwe_1='NL')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = '192837465'
        pid.ethnic_group = CWE(cwe_1='Not Hispanic or Latino')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.assigned_patient_location = PL(pl_4='handle')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.rgs_3 = ''

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_2='30', pl_9='LUMC Polikliniek')
        ail.ail_12 = ''

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.aip_3 = '29384756^van der Linden^Johanna^M^^^MD'
        aip.resource_type = CWE(cwe_1='RESOURCE')
        aip.allow_substitution_code = CWE(cwe_1='SUBSTITUTE')
        aip.aip_12 = ''

        # .. build the PERSONNEL_RESOURCE group ..
        personnel_resource = SiuS12PersonnelResource()
        personnel_resource.aip = aip

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
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
    """ Based on live/nl/nl-nexus.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='sendingSystemA')
        msh.sending_facility = HD(hd_1='senderFacilityA')
        msh.receiving_application = HD(hd_1='receivingSystemB')
        msh.receiving_facility = HD(hd_1='receivingFacilityB')
        msh.date_time_of_message = '20080925161613'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        msh.message_control_id = '589888ADT30502184808'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20080925161613'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN900001', cx_4='VUMC', cx_5='MR')
        pid.patient_name = XPN(xpn_1='van Dijk', xpn_2='Bram', xpn_3='H')
        pid.date_time_of_birth = '19500101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kloveniersburgwal 29', xad_3='Amsterdam', xad_4='NH', xad_5='1011JV', xad_6='NLD')
        pid.pid_13 = '020-6345678'
        pid.pid_14 = '020-6345679'
        pid.marital_status = CWE(cwe_1='S')
        pid.religion = CWE(cwe_1='CAT')
        pid.patient_account_number = CX(cx_1='283746192')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='W', pl_2='389', pl_3='1', pl_4='VUMC')
        pv1.attending_doctor = XCN(xcn_1='ATT7654', xcn_2='Mulder', xcn_3='Cornelia')
        pv1.re_admission_indicator = CWE(cwe_1='ADM')
        pv1.visit_number = CX(cx_1='VN123456', cx_4='VUMC', cx_5='VN')
        pv1.admit_date_time = '20080925161600'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/nl/nl-nexus.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIMHOSP')
        msh.sending_facility = HD(hd_1='SFAC')
        msh.receiving_application = HD(hd_1='RAPP')
        msh.receiving_facility = HD(hd_1='RFAC')
        msh.date_time_of_message = '20200508130643'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        msh.message_control_id = '5'
        msh.processing_id = PT(pt_1='T')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.country_code = '44'
        msh.character_set = 'ASCII'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20200508130643'
        evn.event_reason_code = CWE(cwe_1='ADT_EVENT')
        evn.operator_id = XCN(xcn_1='C006', xcn_2='Dekker', xcn_3='Lotte', xcn_6='Dr', xcn_9='DRNBR', xcn_10='PRSNL', xcn_13='ORGDR')
        evn.evn_6 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.pid_2 = '2590157853^^^SIMULATOR MRN^MRN'
        pid.patient_identifier_list = [CX(cx_1='2590157853', cx_4='SIMULATOR MRN', cx_5='MRN'), CX(cx_1='2478684691', cx_4='NHSNBR', cx_5='NHSNMBR')]
        pid.patient_name = XPN(xpn_1='Meijer', xpn_2='Floor', xpn_5='Mevr.', xpn_7='CURRENT')
        pid.date_time_of_birth = '19781020000000'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Singel 140', xad_3='Amsterdam', xad_4='NH', xad_5='1015AE', xad_6='NL')
        pid.pid_13 = '(020)5551003^^^f.meijer@email.nl'
        pid.primary_language = CWE(cwe_1='NL')
        pid.marital_status = CWE(cwe_1='M')
        pid.religion = CWE(cwe_1='CAT')
        pid.ethnic_group = CWE(cwe_1='A')
        pid.patient_death_date_and_time = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='WARD', pl_2='ROOM01', pl_3='BED01', pl_4='SFAC')
        pv1.attending_doctor = XCN(xcn_1='C006', xcn_2='Dekker', xcn_3='Lotte', xcn_6='Dr', xcn_9='DRNBR', xcn_10='PRSNL', xcn_13='ORGDR')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.visit_number = CX(cx_1='VIS123456789', cx_4='SFAC', cx_5='VISITID')
        pv1.discharged_to_location = DLD(dld_1='SF')
        pv1.pending_location = PL(pl_1='20200508130643')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='Acute MI', cwe_2='Acute Myocardial Infarction', cwe_3='ICD10')
        pv2.expected_discharge_date_time = '20200508130643'
        pv2.actual_length_of_inpatient_stay = '1'
        pv2.newborn_baby_indicator = 'N'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='0002-4182', cwe_2='Body Weight', cwe_3='LN')
        obx.obx_5 = '78'
        obx.units = CWE(cwe_1='kg')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = AdtA01Observation()
        observation.obx = obx

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I21.9', cwe_2='Acute MI', cwe_3='ICD10')
        dg1.diagnosis_type = CWE(cwe_1='AD')

        # .. build ZMP ..
        zmp = ZMP()
        zmp.zmp_1 = '1'
        zmp.zmp_2 = '20200508130643'
        zmp.zmp_4 = 'PHR-PORTAL'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.observation = observation
        msg.dg1 = dg1
        msg.extra_segments = [zmp]

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
    """ Based on live/nl/nl-nexus.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RS')
        msh.sending_facility = HD(hd_1='RetinalScreenings')
        msh.receiving_application = HD(hd_1='EMR')
        msh.receiving_facility = HD(hd_1='CLINIC')
        msh.date_time_of_message = '20210315143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'RS20210315001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT123456', cx_4='CLINIC', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Janssen', xpn_2='Margaretha', xpn_3='A')
        pid.date_time_of_birth = '19750820'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Nieuwstraat 8', xad_3='Nijmegen', xad_4='GE', xad_5='6511PP', xad_6='NL')
        pid.pid_13 = '(024)3561234'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')

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
        orc.placer_order_number = EI(ei_1='ORD789', ei_2='EMR')
        orc.filler_order_number = EI(ei_1='FIL456', ei_2='RS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD789', ei_2='EMR')
        obr.filler_order_number = EI(ei_1='FIL456', ei_2='RS')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Retinal Image', cwe_3='CPT')
        obr.observation_date_time = '20210315140000'
        obr.obr_15 = 'ORD_PROV^Smeets^Adriaan^^^MD'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='ASSESS', cwe_2='Assessment', cwe_3='RS')
        obx.obx_5 = 'NO_DR^No Diabetic Retinopathy^RS'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG_OD', cwe_2='Right Eye Image', cwe_3='RS')
        obx_2.obx_5 = '^image^jpeg^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkS'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ED'
        obx_3.observation_identifier = CWE(cwe_1='IMG_OS', cwe_2='Left Eye Image', cwe_3='RS')
        obx_3.obx_5 = '^image^jpeg^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkS'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'FT'
        obx_4.observation_identifier = CWE(cwe_1='NOTES', cwe_2='Clinical Notes', cwe_3='RS')
        obx_4.obx_5 = 'Bilateral retinal exam performed. No signs of diabetic retinopathy.'
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
    """ Based on live/nl/nl-nexus.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SRC_APP')
        msh.sending_facility = HD(hd_1='SRC_FAC')
        msh.receiving_application = HD(hd_1='DST_APP')
        msh.receiving_facility = HD(hd_1='DST_FAC')
        msh.date_time_of_message = '20230615120000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG0001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5', vid_2='FRA', vid_3='2.5')
        msh.character_set = 'UNICODE UTF-8'
        msh.message_profile_identifier = EI(ei_1='1.3.6.1.4.1.21367.2017.2.6.4', ei_3='2.16.840.1.113883.2.8.3.6', ei_4='ISO')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='374829156', cx_4='ASIP', cx_5='INS-NIR')
        pid.patient_name = XPN(xpn_1='van der Meer', xpn_2='Elisabeth', xpn_7='L')
        pid.date_time_of_birth = '19700101'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Markt 10', xad_3='Groningen', xad_5='9711CV', xad_6='NLD', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='N')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.filler_order_number = EI(ei_1='ORD123', ei_2='SRC_APP')
        obr.universal_service_identifier = CWE(cwe_1='11502-2', cwe_2='Laboratory report', cwe_3='LN')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='11502-2', cwe_2='Laboratory report', cwe_3='LN')
        obx.obx_5 = (
            '^text^xml^Base64^'
            'PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIiB4bWxuczp4c2k9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIj4='
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

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
    """ Based on live/nl/nl-nexus.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PAT')
        msh.receiving_application = HD(hd_1='SUBx')
        msh.date_time_of_message = '20040328112410'
        msh.message_type = MSG(msg_1='ACK', msg_2='A01', msg_3='ACK')
        msh.message_control_id = '48'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'DEU'
        msh.character_set = '8859/1'
        msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = '47'

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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
    """ Based on live/nl/nl-nexus.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KIS')
        msh.sending_facility = HD(hd_1='KLINIKUM')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='RADIOLOGIE')
        msh.date_time_of_message = '200611151030'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'MSG99001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5', vid_2='DEU')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'DEU'
        msh.character_set = '8859/1'
        msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.38', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '200611151030'
        evn.event_occurred = '200611151025'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='78901', cx_4='KLINIKUM', cx_5='PI')
        pid.patient_name = XPN(xpn_1='de Vries', xpn_2='Johanna', xpn_7='L', xpn_8='A', xpn_11='G')
        pid.date_time_of_birth = '19550612'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Haarlemmerstraat 42&Haarlemmerstraat&42', xad_3='Leiden', xad_4='XA-DE-BE', xad_5='2312DH', xad_6='NLD', xad_7='H')
        pid.pid_13 = '^PRN^PH^^31^71^5123456^^^^^071/5123456'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHI', pl_2='101', pl_3='1', pl_4='KLINIKUM', pl_6='N')
        pv1.attending_doctor = XCN(xcn_1='A2345', xcn_2='Vermeulen', xcn_3='Adriaan', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='CHI')
        pv1.admit_source = CWE(cwe_1='N')
        pv1.pv1_20 = '99887^^^KLINIKUM^VN'
        pv1.discharge_date_time = '200611151025'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.insurance_company_id = CX(cx_1='109905003')
        in1.insurance_company_name = XON(xon_1='CZ Zorgverzekeringen')
        in1.insureds_administrative_sex = CWE(cwe_1='109000018')

        # .. build IN2 ..
        in2 = IN2()
        in2.insureds_social_security_number = '78901'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1
        insurance.in2 = in2

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.insurance = insurance

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
    """ Based on live/nl/nl-nexus.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ZorgDomein')
        msh.receiving_application = HD(hd_1='LabSysteem')
        msh.receiving_facility = HD(hd_1='Ziekenhuis')
        msh.date_time_of_message = '20230915143022+0200'
        msh.message_type = MSG(msg_1='OML', msg_2='O21', msg_3='OML_O21')
        msh.message_control_id = 'ZD300056789'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.source_of_comment = 'P'
        nte.comment = 'Cluster Laboratorium'
        nte.comment_type = CWE(cwe_1='ZD_CLUSTER_NAME', cwe_2='ZorgDomein clusternaam', cwe_3='L')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='163895247', cx_4='NLMINBIZA', cx_5='NNNLD')
        pid.patient_name = XPN(xpn_1='Timmerman&Timmerman', xpn_2='L', xpn_3='F', xpn_7='L')
        pid.date_time_of_birth = '19850215'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Reguliersgracht 12', xad_3='Amsterdam', xad_5='1017LV', xad_6='NL', xad_7='H')
        pid.pid_13 = '020-7891234^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='Bloedonderzoek')
        pv2.pv2_28 = ''

        # .. build the PATIENT_VISIT group ..
        patient_visit = OmlO21PatientVisit()
        patient_visit.pv1 = pv1
        patient_visit.pv2 = pv2

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.insurance_company_id = CX(cx_1='0412', cx_2='VGZ')

        # .. build the INSURANCE group ..
        insurance = OmlO21Insurance()
        insurance.in1 = in1

        # .. build the PATIENT group ..
        patient = OmlO21Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit
        patient.insurance = insurance

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ZD300056789')
        orc.date_time_of_order_event = '20230915142500+0200'
        orc.orc_10 = '^&&van Hoekstra^C.'
        orc.orc_12 = '01009876^&&van der Berg^P.J.^^^^^^VEKTIS'
        orc.orc_14 = '010-5559876'

        # .. build TQ1 ..
        tq1 = TQ1()
        tq1.start_datetime = '20230918083000+0200'
        tq1.end_datetime = '20230918120000+0200'

        # .. build the TIMING group ..
        timing = OmlO21Timing()
        timing.tq1 = tq1

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ZD300056789')
        obr.universal_service_identifier = CWE(cwe_1='CHEMIE', cwe_2='Klinische Chemie', cwe_3='ZORGDOMEIN')
        obr.observation_date_time = '20230915142500+0200'
        obr.obr_16 = '01009876^&&van der Berg^P.J.^^^^^^VEKTIS'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='GLUCOSE', cwe_2='Glucose (nuchter)', cwe_3='ZORGDOMEIN')
        obx.obx_5 = 'Aangevraagd'
        obx.observation_result_status = 'O'

        # .. build the OBSERVATION group ..
        observation = OmlO21Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='HBA1C', cwe_2='HbA1c', cwe_3='ZORGDOMEIN')
        obx_2.obx_5 = 'Aangevraagd'
        obx_2.observation_result_status = 'O'

        # .. build the OBSERVATION group ..
        observation_2 = OmlO21Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='TSH', cwe_2='TSH', cwe_3='ZORGDOMEIN')
        obx_3.obx_5 = 'Aangevraagd'
        obx_3.observation_result_status = 'O'

        # .. build the OBSERVATION group ..
        observation_3 = OmlO21Observation()
        observation_3.obx = obx_3

        # .. build the OBSERVATION_REQUEST group ..
        observation_request = OmlO21ObservationRequest()
        observation_request.obr = obr
        observation_request.observation = observation
        observation_request.observation_2 = observation_2
        observation_request.observation_3 = observation_3

        # .. build the ORDER group ..
        order = OmlO21Order()
        order.orc = orc
        order.timing = timing
        order.observation_request = observation_request

        # .. assemble the full message ..
        msg = OML_O21()
        msg.msh = msh
        msg.nte = nte
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
