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
from zato.hl7v2.v2_9.datatypes import CQ, CWE, CX, EI, EIP, HD, MSG, PL, PPN, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01Observation, AdtA39Patient, AdtA45MergeInfo, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, \
    OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, \
    RspK22QueryResponse
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A09, ADT_A17, ADT_A39, ADT_A45, MDM_T02, ORM_O01, ORU_R01, QBP_Q21, RSP_K22
from zato.hl7v2.v2_9.segments import ERR, EVN, IN1, MRG, MSA, MSH, OBR, OBX, ORC, PID, PV1, QAK, QPD, QRI, RCP, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('es', 'es-hp-hcis.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/es/es-hp-hcis.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HCIS')
        msh.sending_facility = HD(hd_1='HURYC')
        msh.receiving_application = HD(hd_1='EMPI')
        msh.receiving_facility = HD(hd_1='SERMAS')
        msh.date_time_of_message = '20251014190023000'
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
        evn.recorded_date_time = '20251014190020000'
        evn.event_occurred = '20251014190020000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='72648918205', cx_4='001')
        pid.pid_4 = 'PASAPORTEWWWW^^^1114&000'
        pid.patient_name = XPN(xpn_1='AREVALO', xpn_2='CARMEN', xpn_3='SOLEDAD')
        pid.date_time_of_birth = '19860215'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='ADM')
        pv1.assigned_patient_location = PL(pl_1='K2UEM2', pl_2='K238', pl_3='K238B', pl_4='20')
        pv1.attending_doctor = XCN(xcn_1='4782', xcn_2='QUINTANA', xcn_3='LUIS', xcn_4='MANZANO', xcn_9='018')
        pv1.hospital_service = CWE(cwe_1='KMIRH')
        pv1.admit_source = CWE(cwe_1='KURGU')
        pv1.admitting_doctor = XCN(xcn_1='4782', xcn_2='QUINTANA', xcn_3='LUIS', xcn_4='MANZANO', xcn_9='018')
        pv1.patient_type = CWE(cwe_1='A')
        pv1.visit_number = CX(cx_1='2025773841', cx_4='20')
        pv1.admit_date_time = '20251014185900000'

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
    """ Based on live/es/es-hp-hcis.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HCIS')
        msh.sending_facility = HD(hd_1='HURYC')
        msh.receiving_application = HD(hd_1='EMPI')
        msh.receiving_facility = HD(hd_1='SERMAS')
        msh.date_time_of_message = '20251014190023000'
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
        evn.recorded_date_time = '20251014190020000'
        evn.event_occurred = '20251014190020000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='72648918205', cx_4='001')
        pid.pid_4 = 'PASAPORTEWWWW^^^1114&000'
        pid.patient_name = XPN(xpn_1='AREVALO', xpn_2='CARMEN', xpn_3='SOLEDAD')
        pid.date_time_of_birth = '19860215'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='ADM')
        pv1.assigned_patient_location = PL(pl_1='K2UEM2', pl_2='K238', pl_3='K238B', pl_4='20')
        pv1.attending_doctor = XCN(xcn_1='4782', xcn_2='QUINTANA', xcn_3='LUIS', xcn_4='MANZANO', xcn_9='018')
        pv1.hospital_service = CWE(cwe_1='KMIRH')
        pv1.admit_source = CWE(cwe_1='KURGU')
        pv1.admitting_doctor = XCN(xcn_1='4782', xcn_2='QUINTANA', xcn_3='LUIS', xcn_4='MANZANO', xcn_9='018')
        pv1.patient_type = CWE(cwe_1='A')
        pv1.visit_number = CX(cx_1='2025773841', cx_4='20')
        pv1.admit_date_time = '20251014185900000'

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
    """ Based on live/es/es-hp-hcis.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HCIS')
        msh.sending_facility = HD(hd_1='HURYC')
        msh.receiving_application = HD(hd_1='EMPI')
        msh.receiving_facility = HD(hd_1='SERMAS')
        msh.date_time_of_message = '20251014190023000'
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
        evn.recorded_date_time = '20251014190020000'
        evn.event_occurred = '20251014190020000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='72648918205', cx_4='001')
        pid.pid_4 = 'PASAPORTEWWWW^^^1114&000'
        pid.patient_name = XPN(xpn_1='AREVALO', xpn_2='CARMEN', xpn_3='SOLEDAD')
        pid.date_time_of_birth = '19860215'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='ADM')
        pv1.assigned_patient_location = PL(pl_1='K2UEM2', pl_2='K238', pl_3='K238B', pl_4='20')
        pv1.attending_doctor = XCN(xcn_1='4782', xcn_2='QUINTANA', xcn_3='LUIS', xcn_4='MANZANO', xcn_9='018')
        pv1.hospital_service = CWE(cwe_1='KMIRH')
        pv1.admit_source = CWE(cwe_1='KURGU')
        pv1.admitting_doctor = XCN(xcn_1='4782', xcn_2='QUINTANA', xcn_3='LUIS', xcn_4='MANZANO', xcn_9='018')
        pv1.patient_type = CWE(cwe_1='A')
        pv1.visit_number = CX(cx_1='2025773841', cx_4='20')
        pv1.admit_date_time = '20251014185900000'
        pv1.discharge_date_time = '20251014185900000'

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
    """ Based on live/es/es-hp-hcis.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HCIS')
        msh.sending_facility = HD(hd_1='HULP')
        msh.receiving_application = HD(hd_1='EMPI')
        msh.receiving_facility = HD(hd_1='SERMAS')
        msh.date_time_of_message = '20240305120344'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08')
        msh.message_control_id = '176690'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20240305120344'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='2847193056', cx_4='SERMAS', cx_5='SN'), CX(cx_1='440127', cx_4='HULP', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='MONTERO BRIONES', xpn_2='VICTORIA', xpn_5='')
        pid.date_time_of_birth = '20150403'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CALLE ROSA DE LIMA 42 2 BAJO', xad_3='MOSTOLES', xad_4='MADRID', xad_5='28935', xad_6='SPAIN')
        pid.pid_13 = '554176088^PRN^^VICTORIA.MONTERO@YAHOO.COM'
        pid.patient_death_indicator = 'N'
        pid.pid_31 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='N')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='162986007', cwe_2='Pulso', cwe_3='SNM')
        obx.obx_5 = '79'
        obx.units = CWE(cwe_2='bpm')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240305120344'

        # .. build the OBSERVATION group ..
        observation = AdtA01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='105723007', cwe_2='Temperatura', cwe_3='SNM')
        obx_2.obx_5 = '37'
        obx_2.units = CWE(cwe_2='Celsius')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240305120344'

        # .. build the OBSERVATION group ..
        observation_2 = AdtA01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='163030003', cwe_2='Presion sanguinea sistolica', cwe_3='SNM')
        obx_3.obx_5 = '139'
        obx_3.units = CWE(cwe_2='mmHg')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240305120344'

        # .. build the OBSERVATION group ..
        observation_3 = AdtA01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='163031004', cwe_2='Presion sanguinea diastolica', cwe_3='SNM')
        obx_4.obx_5 = '91'
        obx_4.units = CWE(cwe_2='mmHg')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240305120344'

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
    """ Based on live/es/es-hp-hcis.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HCIS')
        msh.sending_facility = HD(hd_1='HURYC')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='SERMAS')
        msh.date_time_of_message = '20240115093000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'MSG00234567'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20240115093000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='48291673K', cx_4='MI', cx_5='NNESP', cx_8='20070101', cx_9='ESP&&ISO3166'),
            CX(cx_1='CAEX298574631044', cx_4='CCEX', cx_5='JHN', cx_8='20070101', cx_9='ER&&ISO3166-2'),
            CX(cx_1='061098234571', cx_4='SS', cx_5='SS', cx_9='ESP&&ISO3166'),
            CX(cx_1='7763214', cx_4='HC', cx_5='PI'),
        ]
        pid.date_time_of_birth = 'LAZARO^ANDRES'
        pid.administrative_sex = CWE(cwe_1='PAREDES')
        pid.pid_9 = '19700601'
        pid.race = CWE(cwe_1='M')
        pid.pid_13 = 'AV&ALANGE&8^4a-3a Escalera B^06083^06^06800^ESP^H~CL&CONSTITUCION&34^1o-C^^06^06800^ESP^M'
        pid.pid_15 = '^PRN^PH^^^924512837~^WPN^CP^^^658234196~^NET^Internet^alazaro@hl7spain.org'
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
    """ Based on live/es/es-hp-hcis.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HCIS')
        msh.sending_facility = HD(hd_1='HCSC')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='SERMAS')
        msh.date_time_of_message = '20240220141500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'MSG00345678'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20240220141500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='HOPN710953824017', cx_4='SNS', cx_5='HC', cx_8='20070101', cx_9='ESP&&ISO3166'),
            CX(cx_1='00000004T', cx_4='MI', cx_5='NNESP', cx_8='20070101', cx_9='ESP&&ISO3166'),
            CX(cx_1='50017', cx_4='HC', cx_5='PI', cx_9='ESP&&ISO3166'),
            CX(cx_1='2804100732609', cx_4='SS', cx_5='SS', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='CUBILLO', xpn_2='ELVIRA')
        pid.mothers_maiden_name = XPN(xpn_1='BERNAL')
        pid.date_time_of_birth = '19700601'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='PL&ALFARES&2', xad_2='2oA', xad_3='451685', xad_4='45', xad_5='45002', xad_6='ESP', xad_7='M')
        pid.pid_13 = '^PRN^PH^^^925487213~^ORN^PH^^^925312876~^ORN^CP^^^661827345'
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
    """ Based on live/es/es-hp-hcis.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HCIS')
        msh.sending_facility = HD(hd_1='HURYC')
        msh.receiving_application = HD(hd_1='EMPI')
        msh.receiving_facility = HD(hd_1='SERMAS')
        msh.date_time_of_message = '20250703112947'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40')
        msh.message_control_id = 'ID:9-134087372063957'
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
            CX(cx_1='51008347612', cx_4='001'),
            CX(cx_1='51008347612', cx_4='003'),
            CX(cx_1='F00209741', cx_4='013'),
            CX(cx_1='52348176R', cx_4='014'),
            CX(cx_1='071029834751', cx_4='015'),
            CX(cx_4='016'),
            CX(cx_1='CCCCCCCCCW817293', cx_4='025'),
            CX(cx_4='026'),
            CX(cx_1='49517283946', cx_4='027'),
            CX(cx_4='028'),
            CX(cx_4='029'),
        ]
        pid.patient_name = XPN(xpn_1='CUEVAS', xpn_2='MARCOS', xpn_3='OLVERA')
        pid.date_time_of_birth = '19890621'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = [
            XAD(xad_1='CL&AMPLE&1', xad_3='002', xad_4='07', xad_5='07730', xad_6='724', xad_7='H', xad_8='000101'),
            XAD(xad_4='04', xad_6='724', xad_7='N', xad_8=''),
        ]
        pid.pid_13 = '^^PH^^^^~^^PH^^^^~^^Internet^'
        pid.pid_14 = '^^CP^^^^'
        pid.patient_death_indicator = 'N'
        pid.last_update_date_time = '20120628'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = [CX(cx_1='49502837164', cx_4='001'), CX(cx_1='49502837164', cx_4='003')]

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
    """ Based on live/es/es-hp-hcis.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HCIS')
        msh.sending_facility = HD(hd_1='HURYC')
        msh.receiving_application = HD(hd_1='RADELEC')
        msh.receiving_facility = HD(hd_1='SERMAS')
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
        pid.patient_identifier_list = CX(cx_1='72648918205', cx_4='001')
        pid.pid_4 = 'PASAPORTEWWWW^^^1114&000'
        pid.patient_name = XPN(xpn_1='AREVALO', xpn_2='CARMEN', xpn_3='SOLEDAD')
        pid.date_time_of_birth = '19860215'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='ADM')
        pv1.assigned_patient_location = PL(pl_1='UEPE', pl_2='0117M', pl_3='0117V', pl_4='20')
        pv1.attending_doctor = XCN(xcn_1='4782', xcn_2='QUINTANA', xcn_3='LUIS', xcn_4='MANZANO', xcn_9='018')
        pv1.hospital_service = CWE(cwe_1='PEDH')
        pv1.admit_source = CWE(cwe_1='PEDC')
        pv1.admitting_doctor = XCN(xcn_1='4782', xcn_2='QUINTANA', xcn_3='LUIS', xcn_4='MANZANO', xcn_9='018')
        pv1.patient_type = CWE(cwe_1='A')
        pv1.visit_number = CX(cx_1='2025891423', cx_4='20')
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
        orc.placer_order_number = EI(ei_1='18934267', ei_2='20')
        orc.placer_order_group_number = EI(ei_1='8537194', ei_2='20')
        orc.order_status = 'CA'
        orc.orc_7 = '^^^20251007134031000^^1'
        orc.date_time_of_order_event = '20251007134031000'
        orc.orc_12 = '5391^AGUILAR^LUCIA^SERRANO^^^^^018'
        orc.orc_17 = '13336^Hospital Mateu Orfila^TES_V_HOSP_CS_UBS'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='18934267', ei_2='20')
        obr.universal_service_identifier = CWE(cwe_1='21780', cwe_2='Electrocardiograma (Radelec)', cwe_3='L')
        obr.observation_date_time = '20251007134031000'
        obr.obr_16 = '4782^QUINTANA^LUIS^MANZANO^^^^^018'
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
    """ Based on live/es/es-hp-hcis.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HCIS')
        msh.sending_facility = HD(hd_1='HURYC')
        msh.receiving_application = HD(hd_1='RADELEC')
        msh.receiving_facility = HD(hd_1='SERMAS')
        msh.date_time_of_message = '20250404085928'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = '57746353'
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='72648918205', cx_4='001')
        pid.pid_4 = 'PASAPORTEWWWW^^^1114&000'
        pid.patient_name = XPN(xpn_1='AREVALO', xpn_2='CARMEN', xpn_3='SOLEDAD')
        pid.date_time_of_birth = '19860215'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.assigned_patient_location = PL(pl_1='CODAUXCENTRO')

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
        orc.placer_order_number = EI(ei_1='92187345')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='92187345')
        obr.universal_service_identifier = CWE(cwe_1='21780', cwe_2='Electrocardiograma', cwe_3='L')
        obr.observation_date_time = '20250404085928'

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
    """ Based on live/es/es-hp-hcis.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RADELEC')
        msh.sending_facility = HD(hd_1='IBE')
        msh.receiving_application = HD(hd_1='HCIS')
        msh.receiving_facility = HD(hd_1='HURYC')
        msh.date_time_of_message = '20251008111704'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'bf8fb1531008202011170401'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='72648918205', cx_4='001')
        pid.pid_4 = 'PASAPORTEWWWW^^^1114&000'
        pid.patient_name = XPN(xpn_1='AREVALO', xpn_2='CARMEN', xpn_3='SOLEDAD')
        pid.date_time_of_birth = '19860215'
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
        obr.filler_order_number = EI(ei_1='202010811173455804')
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
    """ Based on live/es/es-hp-hcis.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HCIS')
        msh.sending_facility = HD(hd_1='HURYC')
        msh.receiving_application = HD(hd_1='EMPI')
        msh.receiving_facility = HD(hd_1='SERMAS')
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
    """ Based on live/es/es-hp-hcis.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMPI')
        msh.sending_facility = HD(hd_1='SERMAS')
        msh.receiving_application = HD(hd_1='HCIS')
        msh.receiving_facility = HD(hd_1='HURYC')
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
        pid.patient_name = XPN(xpn_1='AREVALO', xpn_2='CARMEN', xpn_3='SOLEDAD')
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
    """ Based on live/es/es-hp-hcis.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HCIS')
        msh.sending_facility = HD(hd_1='HURYC')
        msh.receiving_application = HD(hd_1='DPTL')
        msh.receiving_facility = HD(hd_1='SERMAS')
        msh.date_time_of_message = '20240812094530'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20240812001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20240812094530'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='7241893056', cx_4='SERMAS', cx_5='SN'), CX(cx_1='334821', cx_4='HURYC', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='MONTERO BRIONES', xpn_2='VICTORIA', xpn_5='')
        pid.date_time_of_birth = '19881215'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CALLE ARTURO SORIA 245 3B', xad_3='MADRID', xad_4='MADRID', xad_5='28033', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^914283756~^ORN^CP^^^617429385'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NEUR', pl_2='305', pl_3='A', pl_4='HURYC')
        pv1.attending_doctor = XCN(xcn_1='62481', xcn_2='IGLESIAS', xcn_3='ROSA', xcn_6='Dra.')
        pv1.visit_number = CX(cx_1='EPI20240812001', cx_4='HURYC', cx_5='VN')
        pv1.total_charges = '20240812080000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SNS', cwe_3='99PLAN')
        in1.insurance_company_id = CX(cx_1='SERMAS', cx_4='SERMAS')
        in1.insurance_company_name = XON(xon_1='Servicio Madrileno de Salud')
        in1.plan_effective_date = '20200101'
        in1.insureds_address = XAD(xad_1='MONTERO BRIONES', xad_2='VICTORIA')
        in1.assignment_of_benefits = CWE(cwe_1='01')
        in1.company_plan_code = CWE(cwe_1='7241893056')

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
    """ Based on live/es/es-hp-hcis.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HCIS')
        msh.sending_facility = HD(hd_1='HURYC')
        msh.receiving_application = HD(hd_1='DPTL')
        msh.receiving_facility = HD(hd_1='SERMAS')
        msh.date_time_of_message = '20240910160045'
        msh.message_type = MSG(msg_1='ADT', msg_2='A17', msg_3='ADT_A17')
        msh.message_control_id = 'MSG20240910002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A17'
        evn.recorded_date_time = '20240910160045'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='8392471056', cx_4='SERMAS', cx_5='SN'), CX(cx_1='519284', cx_4='HURYC', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='COLLADO FUENTES', xpn_2='SANTIAGO', xpn_5='')
        pid.date_time_of_birth = '19750320'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='TRAU', pl_2='410', pl_3='B', pl_4='HURYC')
        pv1.attending_doctor = XCN(xcn_1='83147', xcn_2='DURAN', xcn_3='ALBERTO', xcn_6='Dr.')
        pv1.visit_number = CX(cx_1='EPI20240910003', cx_4='HURYC', cx_5='VN')
        pv1.total_charges = '20240908120000'

        # .. build PID ..
        pid_2 = PID()
        pid_2.set_id_pid = '2'
        pid_2.patient_identifier_list = [CX(cx_1='9174028356', cx_4='SERMAS', cx_5='SN'), CX(cx_1='627413', cx_4='HURYC', cx_5='PI')]
        pid_2.patient_name = XPN(xpn_1='LORENTE BERMEJO', xpn_2='PILAR', xpn_5='')
        pid_2.date_time_of_birth = '19920710'
        pid_2.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1_2 = PV1()
        pv1_2.set_id_pv1 = '2'
        pv1_2.patient_class = CWE(cwe_1='I')
        pv1_2.assigned_patient_location = PL(pl_1='TRAU', pl_2='410', pl_3='A', pl_4='HURYC')
        pv1_2.attending_doctor = XCN(xcn_1='83147', xcn_2='DURAN', xcn_3='ALBERTO', xcn_6='Dr.')
        pv1_2.visit_number = CX(cx_1='EPI20240910004', cx_4='HURYC', cx_5='VN')
        pv1_2.total_charges = '20240907090000'

        # .. assemble the full message ..
        msg = ADT_A17()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pid_2 = pid_2
        msg.pv1_2 = pv1_2

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
    """ Based on live/es/es-hp-hcis.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HCIS')
        msh.sending_facility = HD(hd_1='HURYC')
        msh.receiving_application = HD(hd_1='DPTL')
        msh.receiving_facility = HD(hd_1='SERMAS')
        msh.date_time_of_message = '20241001112000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A11', msg_3='ADT_A09')
        msh.message_control_id = 'MSG20241001003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A11'
        evn.recorded_date_time = '20241001112000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='6028471935', cx_4='SERMAS', cx_5='SN'), CX(cx_1='748291', cx_4='HURYC', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='PALOMO OSORIO', xpn_2='GREGORIO', xpn_5='')
        pid.date_time_of_birth = '19650814'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AVENIDA DE LA ILUSTRACION 12', xad_3='MADRID', xad_4='MADRID', xad_5='28029', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^915294817'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='URG', pl_2='001', pl_3='C', pl_4='HURYC')
        pv1.attending_doctor = XCN(xcn_1='41829', xcn_2='CAMPOS', xcn_3='JORGE', xcn_6='Dr.')
        pv1.visit_number = CX(cx_1='EPI20241001005', cx_4='HURYC', cx_5='VN')
        pv1.total_charges = '20241001080000'

        # .. assemble the full message ..
        msg = ADT_A09()
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
    """ Based on live/es/es-hp-hcis.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HCIS')
        msh.sending_facility = HD(hd_1='HURYC')
        msh.receiving_application = HD(hd_1='DPTL')
        msh.receiving_facility = HD(hd_1='SERMAS')
        msh.date_time_of_message = '20241105143000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A45', msg_3='ADT_A45')
        msh.message_control_id = 'MSG20241105004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A45'
        evn.recorded_date_time = '20241105143000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='4918273650', cx_4='SERMAS', cx_5='SN'), CX(cx_1='851926', cx_4='HURYC', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='SEGOVIA MUÑOZ', xpn_2='ELVIRA', xpn_5='')
        pid.date_time_of_birth = '19800225'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CALLE BRAVO MURILLO 156 5D', xad_3='MADRID', xad_4='MADRID', xad_5='28020', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^916583274'
        pid.patient_death_indicator = 'N'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='EPI20241100OLD', cx_4='HURYC', cx_5='VN')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ONCOL', pl_2='501', pl_3='A', pl_4='HURYC')
        pv1.attending_doctor = XCN(xcn_1='92748', xcn_2='MARIN', xcn_3='BELEN', xcn_6='Dra.')
        pv1.visit_number = CX(cx_1='EPI20241105NEW', cx_4='HURYC', cx_5='VN')
        pv1.total_charges = '20241103100000'

        # .. build the MERGE_INFO group ..
        merge_info = AdtA45MergeInfo()
        merge_info.mrg = mrg
        merge_info.pv1 = pv1

        # .. assemble the full message ..
        msg = ADT_A45()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.merge_info = merge_info

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
    """ Based on live/es/es-hp-hcis.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HCIS')
        msh.sending_facility = HD(hd_1='HULP')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='SERMAS')
        msh.date_time_of_message = '20240515083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'LAB20240515001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='3817294056', cx_4='SERMAS', cx_5='SN'), CX(cx_1='662148', cx_4='HULP', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='MORANTE ARCOS', xpn_2='ENCARNACION', xpn_5='')
        pid.date_time_of_birth = '19550312'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CALLE ALCALA 120 2A', xad_3='MADRID', xad_4='MADRID', xad_5='28009', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^917482931'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONS', pl_2='201', pl_3='A', pl_4='HULP')
        pv1.attending_doctor = XCN(xcn_1='57194', xcn_2='ROMERO', xcn_3='ALVARO', xcn_6='Dr.')
        pv1.visit_number = CX(cx_1='EPI20240515001', cx_4='HULP', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='PET20240515001', ei_2='HCIS')
        orc.parent_order = EIP(eip_1='20240515083000')
        orc.orc_11 = '57194^ROMERO^ALVARO^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PET20240515001', ei_2='HCIS')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Hemograma completo', cwe_3='L')
        obr.observation_date_time = '20240515083000'
        obr.obr_16 = '57194^ROMERO^ALVARO^^^Dr.'

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
        obr_2.placer_order_number = EI(ei_1='PET20240515001', ei_2='HCIS')
        obr_2.universal_service_identifier = CWE(cwe_1='BMP', cwe_2='Panel metabolico basico', cwe_3='L')
        obr_2.observation_date_time = '20240515083000'
        obr_2.obr_16 = '57194^ROMERO^ALVARO^^^Dr.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2]

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
    """ Based on live/es/es-hp-hcis.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB')
        msh.sending_facility = HD(hd_1='HULP')
        msh.receiving_application = HD(hd_1='HCIS')
        msh.receiving_facility = HD(hd_1='SERMAS')
        msh.date_time_of_message = '20240515143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RES20240515001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='3817294056', cx_4='SERMAS', cx_5='SN'), CX(cx_1='662148', cx_4='HULP', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='MORANTE ARCOS', xpn_2='ENCARNACION', xpn_5='')
        pid.date_time_of_birth = '19550312'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONS', pl_2='201', pl_3='A', pl_4='HULP')
        pv1.attending_doctor = XCN(xcn_1='57194', xcn_2='ROMERO', xcn_3='ALVARO', xcn_6='Dr.')
        pv1.visit_number = CX(cx_1='EPI20240515001', cx_4='HULP', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='PET20240515001', ei_2='HCIS')
        orc.filler_order_number = EI(ei_1='RES20240515001', ei_2='LAB')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PET20240515001', ei_2='HCIS')
        obr.filler_order_number = EI(ei_1='RES20240515001', ei_2='LAB')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Hemograma completo', cwe_3='L')
        obr.observation_date_time = '20240515083000'
        obr.results_rpt_status_chng_date_time = '20240515140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='WBC', cwe_2='Leucocitos', cwe_3='L')
        obx.obx_5 = '7.2'
        obx.units = CWE(cwe_1='10*3/uL')
        obx.reference_range = '4.0-11.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240515140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='RBC', cwe_2='Eritrocitos', cwe_3='L')
        obx_2.obx_5 = '4.5'
        obx_2.units = CWE(cwe_1='10*6/uL')
        obx_2.reference_range = '3.8-5.2'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240515140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='HGB', cwe_2='Hemoglobina', cwe_3='L')
        obx_3.obx_5 = '13.8'
        obx_3.units = CWE(cwe_1='g/dL')
        obx_3.reference_range = '12.0-16.0'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240515140000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='HCT', cwe_2='Hematocrito', cwe_3='L')
        obx_4.obx_5 = '41.2'
        obx_4.units = CWE(cwe_1='%')
        obx_4.reference_range = '36.0-46.0'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240515140000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='PLT', cwe_2='Plaquetas', cwe_3='L')
        obx_5.obx_5 = '245'
        obx_5.units = CWE(cwe_1='10*3/uL')
        obx_5.reference_range = '150-400'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20240515140000'

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
    """ Based on live/es/es-hp-hcis.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='HULP')
        msh.receiving_application = HD(hd_1='HCIS')
        msh.receiving_facility = HD(hd_1='SERMAS')
        msh.date_time_of_message = '20240620102000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RAD20240620001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5039182746', cx_4='SERMAS', cx_5='SN'), CX(cx_1='773512', cx_4='HULP', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='QUEVEDO MACIAS', xpn_2='PABLO', xpn_5='')
        pid.date_time_of_birth = '19680418'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CALLE SERRANO 55', xad_3='MADRID', xad_4='MADRID', xad_5='28001', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^918374926'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RXDPT', pl_2='101', pl_3='A', pl_4='HULP')
        pv1.attending_doctor = XCN(xcn_1='63284', xcn_2='SANZ', xcn_3='OSCAR', xcn_6='Dr.')
        pv1.visit_number = CX(cx_1='EPI20240620001', cx_4='HULP', cx_5='VN')

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
        orc.placer_order_number = EI(ei_1='PET20240620001', ei_2='HCIS')
        orc.filler_order_number = EI(ei_1='RAD20240620001', ei_2='RIS')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PET20240620001', ei_2='HCIS')
        obr.filler_order_number = EI(ei_1='RAD20240620001', ei_2='RIS')
        obr.universal_service_identifier = CWE(cwe_1='RXCHEST', cwe_2='Radiografia torax PA y lateral', cwe_3='L')
        obr.observation_date_time = '20240620090000'
        obr.results_rpt_status_chng_date_time = '20240620100000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='RXCHEST', cwe_2='Radiografia torax', cwe_3='L')
        obx.obx_5 = 'Campos pulmonares sin consolidaciones. Silueta cardiaca normal. No derrame pleural.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240620100000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Informe radiologico', cwe_3='L')
        obx_2.obx_5 = (
            '^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovUmVzb3VyY2VzIDw8Ci9Gb250IDw8Ci9GMSAxMiAwIFIK'
            'Pj4KPj4KL0NvbnRlbnRzIDQgMCBSCj4+CmVuZG9iagpzdHJlYW0KQlQKL0YxIDE0IFRmCjEgMCAwIDEgNTAgNzMwIFRtCihJTkZPUk1FIFJBRElPTE9HSUNPKSBUago2IDAgMCAxIDUw'
            'IDcwMCBUbQooUGFjaWVudGU6IE1vcmVubyBTYW50b3MsIEFuZHJlcykgVGoKRVQKZW5kc3RyZWFt'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240620100000'

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
    """ Based on live/es/es-hp-hcis.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HCIS')
        msh.sending_facility = HD(hd_1='HULP')
        msh.receiving_application = HD(hd_1='PACS')
        msh.receiving_facility = HD(hd_1='SERMAS')
        msh.date_time_of_message = '20240720153000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'DOC20240720001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20240720153000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='6150482739', cx_4='SERMAS', cx_5='SN'), CX(cx_1='884623', cx_4='HULP', cx_5='PI')]
        pid.patient_name = XPN(xpn_1='CARDENAS QUIROGA', xpn_2='SILVIA', xpn_5='')
        pid.date_time_of_birth = '19750930'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CALLE GOYA 85 1A', xad_3='MADRID', xad_4='MADRID', xad_5='28001', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^919847321'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='202', pl_3='B', pl_4='HULP')
        pv1.attending_doctor = XCN(xcn_1='74291', xcn_2='REQUENA', xcn_3='GLORIA', xcn_6='Dra.')
        pv1.visit_number = CX(cx_1='EPI20240720001', cx_4='HULP', cx_5='VN')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DI')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20240720150000'
        txa.origination_date_time = '20240720153000'
        txa.originator_code_name = XCN(xcn_1='RequenaGloria')
        txa.unique_document_number = EI(ei_1='1.2.840.113619.2.55.3.2831205372.12345')
        txa.parent_document_number = EI(ei_1='1.2.840.113619.2.55.3.2831205372.67890')
        txa.placer_order_number = EI(ei_1='PET20240720001')
        txa.filler_order_number = EI(ei_1='DOC20240720001')
        txa.document_completion_status = 'AU'
        txa.authentication_person_time_stamp_set = PPN(ppn_1='74291', ppn_2='REQUENA', ppn_3='GLORIA', ppn_15='20240720153000')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'HD'
        obx.observation_identifier = CWE(cwe_1='113014', cwe_2='DICOM Study', cwe_3='DCM')
        obx.obx_5 = '1.2.840.113619.2.55.3.2831205372.12345'
        obx.observation_result_status = 'O'

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='Ecocardiograma transtorcico', cwe_3='L')
        obx_2.obx_5 = (
            '^Image^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDABQODxIPDRQSEBIXFRQYHjIhHhwcHj0sLiQySUBMS0dARkVQWnNiUFVtVkVGZIR0VXdoZ3R0kqSktJOVrrbAwIb/2wBDAR4XFx4aHjshITu2'
            'kYaRtra2tra2tra2tra2tra2tra2tra2tra2tra2tra2tra2tra2tra2tra2tra2tra2tra2trf/wAARCABAAEADASIAAhEBAxEB/8QAGAABAQEBAQAAAAAAAAAAAAAAAAIBAwT/xAAh'
            'EAEAAgICAgMBAQAAAAAAAAAAARECITFBUWFxgZGh/9oADAMBAAIRAxEAPwD0gIAAAAAAAAAAADHJinKO38c5z+imGW+FxTCXtG8OmpmSkWiZj7Y2jXUY1a5Szmm3VVEMZy+k9NixmJ8p'
            '2RbGNYhcdxD6fQm8t0xM55djjGXtyysu6fYZ4d1+t3jny5Zb6acxcXltzXLfijEYeM9V+RbMcsYm4ynrpNz7XGrjhcZlljKYuJ4ZZT3tzzuc8t9tuZncvCay/j1aThEV6dmY7c5nNz26'
            'gAAAAAAAAAAAAAAAAA=='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240720153000'

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
