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
from zato.hl7v2.v2_9.datatypes import CNE, CQ, CWE, CX, EI, EIP, HD, MSG, PL, PPN, PT, RPT, VID, XAD, XCN, XPN
from zato.hl7v2.v2_9.groups import AdtA01Observation, AdtA39Patient, MdmT02Observation, OmpO09Observation, OmpO09Order, OmpO09Patient, OmpO09PatientVisit, \
    OmpO09Timing, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, \
    OruR01Patient, OruR01PatientResult, OruR01Visit, RspK22QueryResponse, SiuS12GeneralResource, SiuS12LocationResource, SiuS12Patient, SiuS12Resources
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, MDM_T02, OMP_O09, ORM_O01, ORU_R01, QBP_Q21, RSP_K22, SIU_S12
from zato.hl7v2.v2_9.segments import AIG, AIL, ERR, EVN, MRG, MSA, MSH, OBR, OBX, ORC, PID, PV1, PV2, QAK, QPD, QRI, RCP, RGS, RXO, RXR, SCH, TQ1, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('es', 'es-cgm-selene.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/es/es-cgm-selene.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SELENE')
        msh.sending_facility = HD(hd_1='HSSON')
        msh.receiving_application = HD(hd_1='EMPI')
        msh.receiving_facility = HD(hd_1='IBSALUT')
        msh.date_time_of_message = '20251007190023000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        msh.message_control_id = '39465507'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20251007190020000'
        evn.event_occurred = '20251007190020000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='72819456203', cx_4='001')
        pid.pid_4 = 'PASSPORTXYZW^^^1114&000'
        pid.patient_name = XPN(xpn_1='COLOM', xpn_2='MARTA', xpn_3='VICTORIA')
        pid.date_time_of_birth = '19910315'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='ADM')
        pv1.assigned_patient_location = PL(pl_1='K2UEM2', pl_2='K238', pl_3='K238B', pl_4='20')
        pv1.attending_doctor = XCN(xcn_1='4578', xcn_2='TUGORES', xcn_3='FRANCESCA', xcn_4='BONET', xcn_9='018')
        pv1.hospital_service = CWE(cwe_1='KMIRH')
        pv1.admit_source = CWE(cwe_1='KURGU')
        pv1.admitting_doctor = XCN(xcn_1='4578', xcn_2='TUGORES', xcn_3='FRANCESCA', xcn_4='BONET', xcn_9='018')
        pv1.patient_type = CWE(cwe_1='A')
        pv1.visit_number = CX(cx_1='2025781245', cx_4='20')
        pv1.admit_date_time = '20251007185900000'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/es/es-cgm-selene.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SELENE')
        msh.sending_facility = HD(hd_1='HSSON')
        msh.receiving_application = HD(hd_1='EMPI')
        msh.receiving_facility = HD(hd_1='IBSALUT')
        msh.date_time_of_message = '20251007190023000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02')
        msh.message_control_id = '39465508'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20251007190020000'
        evn.event_occurred = '20251007190020000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='72819456203', cx_4='001')
        pid.pid_4 = 'PASSPORTXYZW^^^1114&000'
        pid.patient_name = XPN(xpn_1='COLOM', xpn_2='MARTA', xpn_3='VICTORIA')
        pid.date_time_of_birth = '19910315'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='ADM')
        pv1.assigned_patient_location = PL(pl_1='K2UEM2', pl_2='K238', pl_3='K238B', pl_4='20')
        pv1.attending_doctor = XCN(xcn_1='4578', xcn_2='TUGORES', xcn_3='FRANCESCA', xcn_4='BONET', xcn_9='018')
        pv1.hospital_service = CWE(cwe_1='KMIRH')
        pv1.admit_source = CWE(cwe_1='KURGU')
        pv1.admitting_doctor = XCN(xcn_1='4578', xcn_2='TUGORES', xcn_3='FRANCESCA', xcn_4='BONET', xcn_9='018')
        pv1.patient_type = CWE(cwe_1='A')
        pv1.visit_number = CX(cx_1='2025781245', cx_4='20')
        pv1.admit_date_time = '20251007185900000'

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/es/es-cgm-selene.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SELENE')
        msh.sending_facility = HD(hd_1='HSSON')
        msh.receiving_application = HD(hd_1='EMPI')
        msh.receiving_facility = HD(hd_1='IBSALUT')
        msh.date_time_of_message = '20251007190023000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03')
        msh.message_control_id = '39465509'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20251007190020000'
        evn.event_occurred = '20251007190020000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='72819456203', cx_4='001')
        pid.pid_4 = 'PASSPORTXYZW^^^1114&000'
        pid.patient_name = XPN(xpn_1='COLOM', xpn_2='MARTA', xpn_3='VICTORIA')
        pid.date_time_of_birth = '19910315'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='ADM')
        pv1.assigned_patient_location = PL(pl_1='K2UEM2', pl_2='K238', pl_3='K238B', pl_4='20')
        pv1.attending_doctor = XCN(xcn_1='4578', xcn_2='TUGORES', xcn_3='FRANCESCA', xcn_4='BONET', xcn_9='018')
        pv1.hospital_service = CWE(cwe_1='KMIRH')
        pv1.admit_source = CWE(cwe_1='KURGU')
        pv1.admitting_doctor = XCN(xcn_1='4578', xcn_2='TUGORES', xcn_3='FRANCESCA', xcn_4='BONET', xcn_9='018')
        pv1.patient_type = CWE(cwe_1='A')
        pv1.visit_number = CX(cx_1='2025781245', cx_4='20')
        pv1.admit_date_time = '20251007185900000'
        pv1.discharge_date_time = '20251007185900000'

        # .. assemble the full message ..
        msg = ADT_A03()
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
    """ Based on live/es/es-cgm-selene.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SELENE')
        msh.sending_facility = HD(hd_1='HCAMAN')
        msh.receiving_application = HD(hd_1='EMPI')
        msh.receiving_facility = HD(hd_1='SESCAM')
        msh.date_time_of_message = '20250305120344'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08')
        msh.message_control_id = '176690'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250305120344'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='8901234576', cx_4='SESCAM', cx_5='SN'), CX(cx_1='667788', cx_4='HCAMAN', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='VILLANUEVA ROMERO', xpn_2='RAQUEL', xpn_5='')
        pid.date_time_of_birth = '19870422'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CALLE ALCALA 78 2A', xad_3='CIUDAD REAL', xad_4='CIUDAD REAL', xad_5='13001', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^926789012~^ORN^CP^^^678012345^RAQUEL.VILLANUEVA@GMAIL.COM'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='N')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='162986007', cwe_2='Pulso', cwe_3='SNM')
        obx.obx_5 = '72'
        obx.units = CWE(cwe_2='bpm')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250305120344'

        # .. build the OBSERVATION group ..
        observation = AdtA01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='105723007', cwe_2='Temperatura', cwe_3='SNM')
        obx_2.obx_5 = '36.5'
        obx_2.units = CWE(cwe_2='Celsius')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250305120344'

        # .. build the OBSERVATION group ..
        observation_2 = AdtA01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='163030003', cwe_2='Presion sanguinea sistolica', cwe_3='SNM')
        obx_3.obx_5 = '125'
        obx_3.units = CWE(cwe_2='mmHg')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250305120344'

        # .. build the OBSERVATION group ..
        observation_3 = AdtA01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='163031004', cwe_2='Presion sanguinea diastolica', cwe_3='SNM')
        obx_4.obx_5 = '82'
        obx_4.units = CWE(cwe_2='mmHg')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250305120344'

        # .. build the OBSERVATION group ..
        observation_4 = AdtA01Observation()
        observation_4.obx = obx_4

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.observation = [observation, observation_2, observation_3, observation_4]

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
    """ Based on live/es/es-cgm-selene.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SELENE')
        msh.sending_facility = HD(hd_1='HGUGM')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='SACYL')
        msh.date_time_of_message = '20250220100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'MSG00567890'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250220100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='53217864R', cx_4='MI', cx_5='NNESP', cx_8='20070101', cx_9='ESP&&ISO3166'),
            CX(cx_1='CACL567890123456', cx_4='CACL', cx_5='JHN', cx_8='20070101', cx_9='CL&&ISO3166-2'),
            CX(cx_1='280567890123', cx_4='SS', cx_5='SS', cx_9='ESP&&ISO3166'),
            CX(cx_1='5678901', cx_4='HGUGM', cx_5='PI'),
        ]
        pid.date_time_of_birth = 'HEREDIA^ALFONSO'
        pid.administrative_sex = CWE(cwe_1='ROSALES')
        pid.pid_9 = '19710520'
        pid.race = CWE(cwe_1='M')
        pid.pid_13 = 'CL&GRAN VIA&22^5o-B^280001^28^28001^ESP^H~CL&FUENCARRAL&100^2o-A^280001^28^28004^ESP^M'
        pid.pid_15 = '^PRN^PH^^^914567890~^WPN^CP^^^679012345~^NET^Internet^aheredia@gmail.com'
        pid.identity_reliability_code = CWE(cwe_1='N')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='N')

        # .. assemble the full message ..
        msg = ADT_A05()
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
    """ Based on live/es/es-cgm-selene.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SELENE')
        msh.sending_facility = HD(hd_1='HVIRGS')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='SACYL')
        msh.date_time_of_message = '20250310143000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'MSG00678901'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20250310143000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='HOPN880514926031', cx_4='SNS', cx_5='HC', cx_8='20070101', cx_9='ESP&&ISO3166'),
            CX(cx_1='23456789W', cx_4='MI', cx_5='NNESP', cx_8='20070101', cx_9='ESP&&ISO3166'),
            CX(cx_1='60234', cx_4='HVIRGS', cx_5='PI', cx_9='ESP&&ISO3166'),
            CX(cx_1='2345678901234', cx_4='SS', cx_5='SS', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='MEDINA', xpn_2='AURORA')
        pid.mothers_maiden_name = XPN(xpn_1='QUINTERO')
        pid.date_time_of_birth = '19880514'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='PL&MAYOR&5', xad_2='3o-C', xad_3='450001', xad_4='45', xad_5='45001', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^925678901~^ORN^CP^^^667890432'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='N')

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/es/es-cgm-selene.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SELENE')
        msh.sending_facility = HD(hd_1='HSSON')
        msh.receiving_application = HD(hd_1='EMPI')
        msh.receiving_facility = HD(hd_1='IBSALUT')
        msh.date_time_of_message = '20250703112947'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40')
        msh.message_control_id = 'ID:9-134087372064000'
        msh.processing_id = PT(pt_1='T')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20250703112947'
        evn.operator_id = XCN(xcn_1='01')
        evn.event_occurred = '20250703112947'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [
            CX(cx_1='50012847523', cx_4='001'),
            CX(cx_1='50012847523', cx_4='003'),
            CX(cx_1='F00204971', cx_4='013'),
            CX(cx_1='52333167L', cx_4='014'),
            CX(cx_1='081025236695', cx_4='015'),
            CX(cx_4='016'),
            CX(cx_1='CCCCCCCCCW365977', cx_4='025'),
            CX(cx_4='026'),
            CX(cx_1='49561879365', cx_4='027'),
            CX(cx_4='028'),
            CX(cx_4='029'),
        ]
        pid.patient_name = XPN(xpn_1='BAUZA', xpn_2='XAVIER', xpn_3='AMENGUAL')
        pid.date_time_of_birth = '19950318'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = [
            XAD(xad_1='CL&AMPLE&1', xad_3='002', xad_4='07', xad_5='07730', xad_6='724', xad_7='H', xad_8='000101'),
            XAD(xad_4='04', xad_6='724', xad_7='N', xad_8=''),
        ]
        pid.pid_13 = '^^PH^^^^~^^PH^^^^~^^Internet^'
        pid.pid_14 = '^^CP^^^^'
        pid.patient_death_indicator = 'N'
        pid.last_update_date_time = '20250628'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = [CX(cx_1='49596310157', cx_4='001'), CX(cx_1='49596310157', cx_4='003')]

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
    """ Based on live/es/es-cgm-selene.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SELENE')
        msh.sending_facility = HD(hd_1='HSSON')
        msh.receiving_application = HD(hd_1='RADELEC')
        msh.receiving_facility = HD(hd_1='IBSALUT')
        msh.date_time_of_message = '20251007145211000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = '39462619'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='72819456203', cx_4='001')
        pid.pid_4 = 'PASSPORTXYZW^^^1114&000'
        pid.patient_name = XPN(xpn_1='COLOM', xpn_2='MARTA', xpn_3='VICTORIA')
        pid.date_time_of_birth = '19910315'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='ADM')
        pv1.assigned_patient_location = PL(pl_1='UEPE', pl_2='0117M', pl_3='0117V', pl_4='20')
        pv1.attending_doctor = XCN(xcn_1='56789', xcn_2='GELABERT', xcn_3='APOLONIA', xcn_4='CRESPI', xcn_9='018')
        pv1.hospital_service = CWE(cwe_1='PEDH')
        pv1.admit_source = CWE(cwe_1='PEDC')
        pv1.admitting_doctor = XCN(xcn_1='56789', xcn_2='GELABERT', xcn_3='APOLONIA', xcn_4='CRESPI', xcn_9='018')
        pv1.patient_type = CWE(cwe_1='A')
        pv1.visit_number = CX(cx_1='2025791167', cx_4='20')
        pv1.admit_date_time = '20251007112800000'

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'CA'
        orc.placer_order_number = EI(ei_1='17757584', ei_2='20')
        orc.placer_order_group_number = EI(ei_1='8421970', ei_2='20')
        orc.order_status = 'CA'
        orc.orc_7 = '^^^20251007134031000^^1'
        orc.date_time_of_order_event = '20251007134031000'
        orc.orc_12 = '5678^GELABERT^APOLONIA^CRESPI^^^^^018'
        orc.orc_17 = '13336^Hospital Mateu Orfila^TES_V_HOSP_CS_UBS'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='17757584', ei_2='20')
        obr.universal_service_identifier = CWE(cwe_1='21780', cwe_2='Electrocardiograma (Radelec)', cwe_3='L')
        obr.observation_date_time = '20251007134031000'
        obr.obr_16 = '56789^GELABERT^APOLONIA^CRESPI^^^^^018'
        obr.obr_27 = '^^^^^1'
        obr.scheduled_date_time = '20251007134031000'

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
    """ Based on live/es/es-cgm-selene.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SELENE')
        msh.sending_facility = HD(hd_1='CAUSA')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='SACYL')
        msh.date_time_of_message = '20250418091500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'LAB20250418001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='7654321098', cx_4='SACYL', cx_5='SN'), CX(cx_1='889911', cx_4='CAUSA', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='HEREDIA ROSALES', xpn_2='ALFONSO', xpn_5='')
        pid.date_time_of_birth = '19780209'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CALLE SANTIAGO 18 4C', xad_3='VALLADOLID', xad_4='VALLADOLID', xad_5='47001', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^983567890'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MEDINT', pl_2='302', pl_3='A', pl_4='CAUSA')
        pv1.attending_doctor = XCN(xcn_1='34567', xcn_2='CIFUENTES', xcn_3='LORENA', xcn_6='Dra.')
        pv1.visit_number = CX(cx_1='EPI20250418001', cx_4='CAUSA', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='PET20250418001', ei_2='SELENE')
        orc.parent_order = EIP(eip_1='20250418091500')
        orc.orc_11 = '34567^CIFUENTES^LORENA^^^Dra.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PET20250418001', ei_2='SELENE')
        obr.universal_service_identifier = CWE(cwe_1='COAG', cwe_2='Coagulacion', cwe_3='L')
        obr.observation_date_time = '20250418091500'
        obr.obr_16 = '34567^CIFUENTES^LORENA^^^Dra.'

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
        obr_2.placer_order_number = EI(ei_1='PET20250418001', ei_2='SELENE')
        obr_2.universal_service_identifier = CWE(cwe_1='LIP', cwe_2='Perfil lipidico', cwe_3='L')
        obr_2.observation_date_time = '20250418091500'
        obr_2.obr_16 = '34567^CIFUENTES^LORENA^^^Dra.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2]

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
    """ Based on live/es/es-cgm-selene.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RADELEC')
        msh.sending_facility = HD(hd_1='IBE')
        msh.receiving_application = HD(hd_1='SELENE')
        msh.receiving_facility = HD(hd_1='HSSON')
        msh.date_time_of_message = '20251008111704'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'bf8fb1531008202011170401'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='72819456203', cx_4='001')
        pid.pid_4 = 'PASSPORTXYZW^^^1114&000'
        pid.patient_name = XPN(xpn_1='COLOM', xpn_2='MARTA', xpn_3='VICTORIA')
        pid.date_time_of_birth = '19910315'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')

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
        obr.filler_order_number = EI(ei_1='202510811173455804')
        obr.observation_date_time = '20251008111513'
        obr.filler_field_2 = 'bf7f74a0-c767-43af-9366-54fcc2db2b21'
        obr.results_rpt_status_chng_date_time = '20251008111513'
        obr.result_status = 'F'
        obr.obr_27 = '^^^^20251008111513'

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.obr = obr

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
    """ Based on live/es/es-cgm-selene.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB')
        msh.sending_facility = HD(hd_1='CAUSA')
        msh.receiving_application = HD(hd_1='SELENE')
        msh.receiving_facility = HD(hd_1='SACYL')
        msh.date_time_of_message = '20250418153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RES20250418001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='7654321098', cx_4='SACYL', cx_5='SN'), CX(cx_1='889911', cx_4='CAUSA', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='HEREDIA ROSALES', xpn_2='ALFONSO', xpn_5='')
        pid.date_time_of_birth = '19780209'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MEDINT', pl_2='302', pl_3='A', pl_4='CAUSA')
        pv1.attending_doctor = XCN(xcn_1='34567', xcn_2='CIFUENTES', xcn_3='LORENA', xcn_6='Dra.')
        pv1.visit_number = CX(cx_1='EPI20250418001', cx_4='CAUSA', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='PET20250418001', ei_2='SELENE')
        orc.filler_order_number = EI(ei_1='RES20250418001', ei_2='LAB')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PET20250418001', ei_2='SELENE')
        obr.filler_order_number = EI(ei_1='RES20250418001', ei_2='LAB')
        obr.universal_service_identifier = CWE(cwe_1='LIP', cwe_2='Perfil lipidico', cwe_3='L')
        obr.observation_date_time = '20250418091500'
        obr.results_rpt_status_chng_date_time = '20250418150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='CHOL', cwe_2='Colesterol total', cwe_3='L')
        obx.obx_5 = '215'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '<200'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250418150000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='HDL', cwe_2='Colesterol HDL', cwe_3='L')
        obx_2.obx_5 = '52'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '>40'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250418150000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='LDL', cwe_2='Colesterol LDL', cwe_3='L')
        obx_3.obx_5 = '138'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '<130'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250418150000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='TG', cwe_2='Trigliceridos', cwe_3='L')
        obx_4.obx_5 = '165'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '<150'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250418150000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='GLU', cwe_2='Glucosa', cwe_3='L')
        obx_5.obx_5 = '98'
        obx_5.units = CWE(cwe_1='mg/dL')
        obx_5.reference_range = '70-110'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250418150000'

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
    """ Based on live/es/es-cgm-selene.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SELENE')
        msh.sending_facility = HD(hd_1='HCUVA')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='SACYL')
        msh.date_time_of_message = '20250601080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'RAD20250601001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='8765432109', cx_4='SACYL', cx_5='SN'), CX(cx_1='990012', cx_4='HCUVA', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='MEDINA QUINTERO', xpn_2='AURORA', xpn_5='')
        pid.date_time_of_birth = '19640528'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AVENIDA SALAMANCA 45', xad_3='VALLADOLID', xad_4='VALLADOLID', xad_5='47002', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^983678901'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEUMOL', pl_2='501', pl_3='A', pl_4='HCUVA')
        pv1.attending_doctor = XCN(xcn_1='45678', xcn_2='TERUEL', xcn_3='MARCOS', xcn_6='Dr.')
        pv1.visit_number = CX(cx_1='EPI20250601001', cx_4='HCUVA', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='PET20250601001', ei_2='SELENE')
        orc.parent_order = EIP(eip_1='20250601080000')
        orc.orc_11 = '45678^TERUEL^MARCOS^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PET20250601001', ei_2='SELENE')
        obr.universal_service_identifier = CWE(cwe_1='TCTORAX', cwe_2='TC Torax con contraste', cwe_3='L')
        obr.observation_date_time = '20250601080000'
        obr.obr_16 = '45678^TERUEL^MARCOS^^^Dr.'
        obr.obr_27 = '^^^^^R'

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
    """ Based on live/es/es-cgm-selene.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB')
        msh.sending_facility = HD(hd_1='CAUSA')
        msh.receiving_application = HD(hd_1='SELENE')
        msh.receiving_facility = HD(hd_1='SACYL')
        msh.date_time_of_message = '20250418160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RES20250418002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='7654321098', cx_4='SACYL', cx_5='SN'), CX(cx_1='889911', cx_4='CAUSA', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='HEREDIA ROSALES', xpn_2='ALFONSO', xpn_5='')
        pid.date_time_of_birth = '19780209'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MEDINT', pl_2='302', pl_3='A', pl_4='CAUSA')
        pv1.attending_doctor = XCN(xcn_1='34567', xcn_2='CIFUENTES', xcn_3='LORENA', xcn_6='Dra.')
        pv1.visit_number = CX(cx_1='EPI20250418001', cx_4='CAUSA', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='PET20250418001', ei_2='SELENE')
        orc.filler_order_number = EI(ei_1='RES20250418002', ei_2='LAB')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PET20250418001', ei_2='SELENE')
        obr.filler_order_number = EI(ei_1='RES20250418002', ei_2='LAB')
        obr.universal_service_identifier = CWE(cwe_1='COAG', cwe_2='Coagulacion', cwe_3='L')
        obr.observation_date_time = '20250418091500'
        obr.results_rpt_status_chng_date_time = '20250418155000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='PT', cwe_2='Tiempo protrombina', cwe_3='L')
        obx.obx_5 = '12.5'
        obx.units = CWE(cwe_1='seg')
        obx.reference_range = '10.0-14.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250418155000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='INR', cwe_2='INR', cwe_3='L')
        obx_2.obx_5 = '1.1'
        obx_2.reference_range = '0.8-1.2'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250418155000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='APTT', cwe_2='Tiempo cefalina', cwe_3='L')
        obx_3.obx_5 = '32'
        obx_3.units = CWE(cwe_1='seg')
        obx_3.reference_range = '25-38'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250418155000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='FIB', cwe_2='Fibrinogeno', cwe_3='L')
        obx_4.obx_5 = '310'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '200-400'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250418155000'

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
    """ Based on live/es/es-cgm-selene.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SELENE')
        msh.sending_facility = HD(hd_1='HCUVA')
        msh.receiving_application = HD(hd_1='TAO')
        msh.receiving_facility = HD(hd_1='SACYL')
        msh.date_time_of_message = '20250301090000'
        msh.message_type = MSG(msg_1='OMP', msg_2='O09', msg_3='OMP_O09')
        msh.message_control_id = 'TAO20250301001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='9876543210', cx_4='SACYL', cx_5='SN'), CX(cx_1='101122', cx_4='HCUVA', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='PERALTA LUNA', xpn_2='GONZALO', xpn_5='')
        pid.date_time_of_birth = '19520708'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CALLE DUQUE DE LA VICTORIA 8', xad_3='VALLADOLID', xad_4='VALLADOLID', xad_5='47001', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^983890123'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HEMAT', pl_2='101', pl_3='A', pl_4='HCUVA', pl_8='HCUVA')
        pv1.patient_type = CWE(cwe_1='EPI20250301001', cwe_4='HCUVA', cwe_5='VN')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.expected_admit_date_time = '20250401'

        # .. build the PATIENT_VISIT group ..
        patient_visit = OmpO09PatientVisit()
        patient_visit.pv1 = pv1
        patient_visit.pv2 = pv2

        # .. build the PATIENT group ..
        patient = OmpO09Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.parent_order = EIP(eip_1='20250301090000')
        orc.orc_11 = '56789^PALENCIA^BEATRIZ^^^Dr.'
        orc.order_effective_date_time = 'HEMAT^Hematologia^99SVC'
        orc.orc_18 = 'HCUVA^Hospital Clinico Universitario de Valladolid^^^^^^^^^^47001'

        # .. build TQ1 ..
        tq1 = TQ1()
        tq1.set_id_tq1 = '1'
        tq1.repeat_pattern = RPT(rpt_1='20250301')
        tq1.explicit_time = '20250307'
        tq1.relative_time_and_units = CQ(cq_1='1')
        tq1.start_datetime = '0.5'
        tq1.end_datetime = 'mg'
        tq1.tq1_9 = ''

        # .. build the TIMING group ..
        timing = OmpO09Timing()
        timing.tq1 = tq1

        # .. build TQ1 ..
        tq1_2 = TQ1()
        tq1_2.set_id_tq1 = '2'
        tq1_2.repeat_pattern = RPT(rpt_1='20250308')
        tq1_2.explicit_time = '20250314'
        tq1_2.relative_time_and_units = CQ(cq_1='1')
        tq1_2.start_datetime = '0.75'
        tq1_2.end_datetime = 'mg'
        tq1_2.tq1_9 = ''

        # .. build the TIMING group ..
        timing_2 = OmpO09Timing()
        timing_2.tq1 = tq1_2

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='83929', cwe_2='Acenocumarol 4mg', cwe_3='99MED')
        rxo.allow_substitutions = '56789^PALENCIA^BEATRIZ^^^Dr.'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='PO', cwe_2='Oral', cwe_3='HL70162')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='INR', cwe_2='INR', cwe_3='L')
        obx.obx_5 = '2.8'
        obx.reference_range = '2.0-3.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250301085000'

        # .. build the OBSERVATION group ..
        observation = OmpO09Observation()
        observation.obx = obx

        # .. build the ORDER group ..
        order = OmpO09Order()
        order.orc = orc
        order.timing = timing
        order.timing_2 = timing_2
        order.rxo = rxo
        order.rxr = rxr
        order.observation = observation

        # .. assemble the full message ..
        msg = OMP_O09()
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
    """ Based on live/es/es-cgm-selene.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SELENE')
        msh.sending_facility = HD(hd_1='HVIRMS')
        msh.receiving_application = HD(hd_1='CITASWEB')
        msh.receiving_facility = HD(hd_1='SACYL')
        msh.date_time_of_message = '20250410100000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'CIT20250410001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='CIT20250410001')
        sch.filler_appointment_id = EI(ei_1='CIT20250410001')
        sch.occurrence_number = 'SELENE'
        sch.placer_order_group_number = EI(ei_1='001')
        sch.schedule_id = CWE(cwe_1='01')
        sch.event_reason = CWE(cwe_1='BOOKED')
        sch.appointment_reason = CWE(cwe_1='20250415093000')
        sch.appointment_type = CWE(cwe_1='20250415094500')
        sch.sch_9 = '15'
        sch.appointment_duration_units = CNE(cne_1='min')
        sch.sch_11 = '^^^CONS NEUMOLOGIA'
        sch.placer_contact_person = XCN(xcn_1='CONSULTA NEUMOLOGIA')
        sch.placer_contact_address = XAD(xad_1='67890', xad_2='PALENCIA', xad_3='BEATRIZ', xad_6='Dr.')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='1234567890', cx_4='SACYL', cx_5='SN'), CX(cx_1='223344', cx_4='HVIRMS', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='MANZANO CUEVAS', xpn_2='DAVID', xpn_5='')
        pid.date_time_of_birth = '19830911'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CALLE REAL 22', xad_3='SALAMANCA', xad_4='SALAMANCA', xad_5='37001', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^923567890~^ORN^CP^^^623456789'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='NEUMO', pl_2='CONS1', pl_3='A', pl_4='HVIRMS')
        pv1.attending_doctor = XCN(xcn_1='67890', xcn_2='PALENCIA', xcn_3='BEATRIZ', xcn_6='Dr.')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'

        # .. build AIG ..
        aig = AIG()
        aig.set_id_aig = '1'
        aig.resource_id = CWE(cwe_1='67890', cwe_2='PALENCIA', cwe_3='BEATRIZ', cwe_6='Dr.')
        aig.resource_group = CWE(cwe_1='20250415093000')
        aig.resource_quantity = '20250415094500'

        # .. build the GENERAL_RESOURCE group ..
        general_resource = SiuS12GeneralResource()
        general_resource.aig = aig

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='NEUMO', pl_2='CONS1', pl_3='A', pl_4='HVIRMS')

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.general_resource = general_resource
        resources.location_resource = location_resource

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
    """ Based on live/es/es-cgm-selene.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SELENE')
        msh.sending_facility = HD(hd_1='HSSON')
        msh.receiving_application = HD(hd_1='EMPI')
        msh.receiving_facility = HD(hd_1='IBSALUT')
        msh.date_time_of_message = '20250703101935'
        msh.message_type = MSG(msg_1='QBP', msg_2='Q22')
        msh.message_control_id = 'ID2025070310193500'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'AL'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'
        msh.msh_19 = ''

        # .. build QPD ..
        qpd = QPD()
        qpd.message_query_name = CWE(cwe_1='1', cwe_2='IHE PDQ Query', cwe_3='HL70471')
        qpd.query_tag = '12'
        qpd.qpd_3 = 'CIPAUT^numCIPAUT'
        qpd.qpd_4 = ''

        # .. build RCP ..
        rcp = RCP()
        rcp.query_priority = 'I'
        rcp.quantity_limited_request = CQ(cq_1='20', cq_2='RD&Records&HL70126')
        rcp.rcp_3 = ''

        # .. assemble the full message ..
        msg = QBP_Q21()
        msg.msh = msh
        msg.qpd = qpd
        msg.rcp = rcp

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
    """ Based on live/es/es-cgm-selene.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMPI')
        msh.sending_facility = HD(hd_1='IBSALUT')
        msh.receiving_application = HD(hd_1='SELENE')
        msh.receiving_facility = HD(hd_1='HSSON')
        msh.date_time_of_message = '20250703101935'
        msh.message_type = MSG(msg_1='RSP', msg_2='K22')
        msh.message_control_id = 'ID20250912134401'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'ID2025070310193500'

        # .. build ERR ..
        err = ERR()
        err.hl7_error_code = CWE(cwe_1='0', cwe_2='Message accepted', cwe_3='HL70357', cwe_4='0', cwe_5='Procesado correctamente', cwe_6='TES_ERROR')
        err.severity = 'I'

        # .. build QAK ..
        qak = QAK()
        qak.query_tag = 'ID2025070310193500'
        qak.query_response_status = 'OK'

        # .. build QPD ..
        qpd = QPD()
        qpd.message_query_name = CWE(cwe_1='1', cwe_2='IHE PDQ Query', cwe_3='HL70471')
        qpd.query_tag = 'ID2025070310193500'
        qpd.qpd_3 = 'CIPAUT^numCIPAUT'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='numCIPAUT', cx_4='001'),
            CX(cx_1='numNHCHSLL', cx_4='004'),
            CX(cx_1='numCIP', cx_4='013'),
            CX(cx_1='numDNT', cx_4='014'),
        ]
        pid.patient_name = XPN(xpn_1='APE1', xpn_2='NOM', xpn_3='APE2')
        pid.date_time_of_birth = 'NAI'
        pid.administrative_sex = CWE(cwe_1='SEX')
        pid.patient_address = XAD(xad_5='CPOSTAL')
        pid.patient_death_indicator = 'N'

        # .. build QRI ..
        qri = QRI()
        qri.candidate_confidence = '1'

        # .. build the QUERY_RESPONSE group ..
        query_response = RspK22QueryResponse()
        query_response.pid = pid
        query_response.qri = qri

        # .. assemble the full message ..
        msg = RSP_K22()
        msg.msh = msh
        msg.msa = msa
        msg.err = err
        msg.qak = qak
        msg.qpd = qpd
        msg.query_response = query_response

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
    """ Based on live/es/es-cgm-selene.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SELENE')
        msh.sending_facility = HD(hd_1='HCAMAN')
        msh.receiving_application = HD(hd_1='DPTL')
        msh.receiving_facility = HD(hd_1='SESCAM')
        msh.date_time_of_message = '20251015160000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A13', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20251015001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A13'
        evn.recorded_date_time = '20251015160000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='2345678901', cx_4='SESCAM', cx_5='SN'), CX(cx_1='445566', cx_4='HCAMAN', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='OCANA BRIONES', xpn_2='ERNESTO', xpn_5='')
        pid.date_time_of_birth = '19761024'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='RONDA DE TOLEDO 12', xad_3='CIUDAD REAL', xad_4='CIUDAD REAL', xad_5='13001', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^926456789'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CIRUG', pl_2='205', pl_3='B', pl_4='HCAMAN')
        pv1.attending_doctor = XCN(xcn_1='67891', xcn_2='CORRALES', xcn_3='AMPARO', xcn_6='Dra.')
        pv1.visit_number = CX(cx_1='EPI20251015001', cx_4='HCAMAN', cx_5='VN')
        pv1.total_charges = '20251010080000'
        pv1.total_adjustments = '20251015120000'

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
    """ Based on live/es/es-cgm-selene.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ANAT')
        msh.sending_facility = HD(hd_1='HCUVA')
        msh.receiving_application = HD(hd_1='SELENE')
        msh.receiving_facility = HD(hd_1='SACYL')
        msh.date_time_of_message = '20250710140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'PATH20250710001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='3456789012', cx_4='SACYL', cx_5='SN'), CX(cx_1='556677', cx_4='HCUVA', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='OLMEDO CIFUENTES', xpn_2='CONSUELO', xpn_5='')
        pid.date_time_of_birth = '19690823'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='PASEO ZORRILLA 100', xad_3='VALLADOLID', xad_4='VALLADOLID', xad_5='47006', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^983901234'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ONCOL', pl_2='301', pl_3='A', pl_4='HCUVA')
        pv1.attending_doctor = XCN(xcn_1='78901', xcn_2='AGUADO', xcn_3='TOMAS', xcn_6='Dr.')
        pv1.visit_number = CX(cx_1='EPI20250710001', cx_4='HCUVA', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='PET20250710001', ei_2='SELENE')
        orc.filler_order_number = EI(ei_1='PATH20250710001', ei_2='ANAT')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PET20250710001', ei_2='SELENE')
        obr.filler_order_number = EI(ei_1='PATH20250710001', ei_2='ANAT')
        obr.universal_service_identifier = CWE(cwe_1='BIOPSIA', cwe_2='Biopsia cutanea', cwe_3='L')
        obr.observation_date_time = '20250708100000'
        obr.results_rpt_status_chng_date_time = '20250710133000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='BIOPSIA', cwe_2='Resultado anatomopatologico', cwe_3='L')
        obx.obx_5 = 'Piel con dermatitis cronica superficial perivascular. No se observan signos de malignidad. Margenes quirurgicos libres.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250710133000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Informe anatomia patologica', cwe_3='L')
        obx_2.obx_5 = (
            '^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovUmVzb3VyY2VzIDw8Ci9Gb250IDw8Ci9GMSAxMiAwIFIK'
            'Pj4KPj4KL0NvbnRlbnRzIDQgMCBSCj4+CmVuZG9iagpzdHJlYW0KQlQKL0YxIDE0IFRmCjEgMCAwIDEgNTAgNzMwIFRtCihJTkZPUk1FIEFOQVRPTUlBIFBBVE9MT0dJQ0EpIFRqCjYg'
            'MCAwIDEgNTAgNzAwIFRtCihTZXJ2aWNpbyBkZSBBbmF0b21pYSBQYXRvbG9naWNhIC0gSENVVkEpIFRqCkVUCmVuZHN0cmVhbQ=='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250710133000'

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
    """ Based on live/es/es-cgm-selene.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SELENE')
        msh.sending_facility = HD(hd_1='HSSON')
        msh.receiving_application = HD(hd_1='PACS')
        msh.receiving_facility = HD(hd_1='IBSALUT')
        msh.date_time_of_message = '20250820110000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'DOC20250820001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20250820110000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='4567890123', cx_4='IBSALUT', cx_5='SN'), CX(cx_1='667788', cx_4='HSSON', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='ESTRADA TORRENS', xpn_2='MIREIA', xpn_5='')
        pid.date_time_of_birth = '19850219'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CALLE GENERAL RIERA 40', xad_3='PALMA', xad_4='BALEARES', xad_5='07010', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^971345678'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='102', pl_3='A', pl_4='HSSON')
        pv1.attending_doctor = XCN(xcn_1='89012', xcn_2='GELABERT', xcn_3='LLUIS', xcn_6='Dr.')
        pv1.visit_number = CX(cx_1='EPI20250820001', cx_4='HSSON', cx_5='VN')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DI')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20250820103000'
        txa.origination_date_time = '20250820110000'
        txa.originator_code_name = XCN(xcn_1='GelaberLluis')
        txa.unique_document_number = EI(ei_1='1.2.840.113619.2.55.3.4567890123.11111')
        txa.parent_document_number = EI(ei_1='1.2.840.113619.2.55.3.4567890123.22222')
        txa.placer_order_number = EI(ei_1='PET20250820001')
        txa.filler_order_number = EI(ei_1='DOC20250820001')
        txa.document_completion_status = 'AU'
        txa.authentication_person_time_stamp_set = PPN(ppn_1='89012', ppn_2='GELABERT', ppn_3='LLUIS', ppn_15='20250820110000')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'HD'
        obx.observation_identifier = CWE(cwe_1='113014', cwe_2='DICOM Study', cwe_3='DCM')
        obx.obx_5 = '1.2.840.113619.2.55.3.4567890123.11111'
        obx.observation_result_status = 'O'

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='Ecocardiograma transtoracico', cwe_3='L')
        obx_2.obx_5 = (
            '^Image^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDABQODxIPDRQSEBIXFRQYHjIhHhwcHj0sLiQySUBMS0dARkVQWnNiUFVtVkVGZIR0VXdoZ3R0kqSktJOVrrbAwIb/2wBDAR4XFx4aHjshITu2'
            'kYaRtra2tra2tra2tra2tra2tra2tra2tra2tra2tra2tra2tra2tra2tra2tra2tra2tra2trf/wAARCABAAEADASIAAhEBAxEB/8QAGAABAQEBAQAAAAAAAAAAAAAAAAIBAwT/xAAh'
            'EAEAAgICAgMBAQAAAAAAAAAAARECITFBUWFxgZGh/9oADAMBAAIRAxEAPwD0gIAAAAAAAAAAADHJinKO38c5z+imGW+FxTCXtG8OmpmSkWiZj7Y2jXUY1a5Szmm3VVEMZy+k9NixmJ8p'
            '2RbGNYhcdxD6fQm8t0xM55djjGXtyysu6fYZ4d1+t3jny5Zb6acxcXltzXLfijEYeM9V+RbMcsYm4ynrpNz7XGrjhcZlljKYuJ4ZZT3tzzuc8t9tuZncvCay/j1aThEV6dmY7c5nNz26'
            'gAAAAAAAAAAAAAAAAA=='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250820110000'

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
