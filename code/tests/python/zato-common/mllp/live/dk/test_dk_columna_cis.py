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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, EI, EIP, FC, HD, MSG, PL, PT, VID, XAD, XCN, XPN, XTN
from zato.hl7v2.v2_9.groups import AdtA39Patient, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, \
    OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12Patient
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, EVN, MRG, MSH, OBR, OBX, ORC, PD1, PID, PV1, PV2, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('dk', 'dk-columna-cis.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/dk/dk-columna-cis.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_CIS')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='LANDSPATIENTREGISTERET')
        msh.receiving_facility = HD(hd_1='SST')
        msh.date_time_of_message = '20260401080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260401080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0102857128', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Dahl', xpn_2='Camilla', xpn_3='Marie', xpn_5='')
        pid.date_time_of_birth = '19850201'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Adelgade 115', xad_3='Hellerup', xad_5='2900', xad_6='DK')
        pid.pid_13 = '^^PH^+4543482061~^^CP^+4520741979'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='MED', pl_3='301', pl_4='A3')
        pv1.attending_doctor = XCN(xcn_1='12345', xcn_2='Schmidt', xcn_3='Mathias', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='12345', xcn_2='Schmidt', xcn_3='Mathias', xcn_6='Dr.')
        pv1.visit_number = CX(cx_1='AAUH202604010001')
        pv1.prior_temporary_location = PL(pl_1='20260401080000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Pneumoni')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/dk/dk-columna-cis.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_CIS')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='LANDSPATIENTREGISTERET')
        msh.receiving_facility = HD(hd_1='SST')
        msh.date_time_of_message = '20260402093000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'MSG00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260402093000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0102857128', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Dahl', xpn_2='Camilla', xpn_3='Marie', xpn_5='')
        pid.date_time_of_birth = '19850201'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Adelgade 115', xad_3='Hellerup', xad_5='2900', xad_6='DK')
        pid.pid_13 = '^^PH^+4543482061~^^CP^+4520741979'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='KIR', pl_3='205', pl_4='B1')
        pv1.attending_doctor = XCN(xcn_1='23456', xcn_2='Hansen', xcn_3='Jens', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='KIR')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='23456', xcn_2='Hansen', xcn_3='Jens', xcn_6='Dr.')
        pv1.visit_number = CX(cx_1='AAUH202604010001')
        pv1.prior_temporary_location = PL(pl_1='20260402093000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Appendicit')

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/dk/dk-columna-cis.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_CIS')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='LANDSPATIENTREGISTERET')
        msh.receiving_facility = HD(hd_1='SST')
        msh.date_time_of_message = '20260405140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260405140000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0102857128', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Dahl', xpn_2='Camilla', xpn_3='Marie', xpn_5='')
        pid.date_time_of_birth = '19850201'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Adelgade 115', xad_3='Hellerup', xad_5='2900', xad_6='DK')
        pid.pid_13 = '^^PH^+4543482061~^^CP^+4520741979'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='MED', pl_3='301', pl_4='A3')
        pv1.attending_doctor = XCN(xcn_1='12345', xcn_2='Schmidt', xcn_3='Mathias', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='12345', xcn_2='Schmidt', xcn_3='Mathias', xcn_6='Dr.')
        pv1.visit_number = CX(cx_1='AAUH202604010001')
        pv1.prior_temporary_location = PL(pl_1='20260405140000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Pneumoni')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/dk/dk-columna-cis.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_CIS')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='SUNDHED_DK')
        msh.receiving_facility = HD(hd_1='SST')
        msh.date_time_of_message = '20260406100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260406100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1503764703', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Mortensen', xpn_2='Emil', xpn_3='Kaj', xpn_5='')
        pid.date_time_of_birth = '19760315'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Bispensgade 217', xad_3='København N', xad_5='2200', xad_6='DK')
        pid.pid_13 = '^^PH^+4550829477~^^CP^+4550865816'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='AMB', pl_3='120', pl_4='')
        pv1.admitting_doctor = XCN(xcn_1='AMB')
        pv1.visit_number = CX(cx_1='AAUH202604060001')
        pv1.prior_temporary_location = PL(pl_1='20260406100000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Kontrol - diabetes mellitus type 2')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/dk/dk-columna-cis.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_CIS')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='LANDSPATIENTREGISTERET')
        msh.receiving_facility = HD(hd_1='SST')
        msh.date_time_of_message = '20260407091500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260407091500'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1503764703', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Mortensen', xpn_2='Emil', xpn_3='Kaj', xpn_5='')
        pid.date_time_of_birth = '19760315'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Paludan-Müllers Vej 63', xad_3='København K', xad_5='1050', xad_6='DK')
        pid.pid_13 = '^^PH^+4545697416~^^CP^+4521157665'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='AMB', pl_3='120', pl_4='')
        pv1.admitting_doctor = XCN(xcn_1='AMB')
        pv1.visit_number = CX(cx_1='AAUH202604060001')
        pv1.prior_temporary_location = PL(pl_1='20260407091500')

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/dk/dk-columna-cis.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_CIS')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='CPR_REGISTERET')
        msh.receiving_facility = HD(hd_1='SST')
        msh.date_time_of_message = '20260408080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'MSG00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20260408080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2411908118', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Rasmussen', xpn_2='Pernille', xpn_3='Gudrun', xpn_5='')
        pid.date_time_of_birth = '19901124'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Nørregade 107', xad_3='Albertslund', xad_5='2620', xad_6='DK')
        pid.pid_13 = '^^PH^+4548946335~^^CP^+4541115573'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = '34567^Mortensen^Brian^^^Dr.'

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1

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
    """ Based on live/dk/dk-columna-cis.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_CIS')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='SST')
        msh.date_time_of_message = '20260409070000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'MSG00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260409070000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0706882431', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Petersen', xpn_2='Thomas', xpn_3='Folmer', xpn_5='')
        pid.date_time_of_birth = '19880607'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hovedvejen 136', xad_3='København SV', xad_5='2450', xad_6='DK')
        pid.pid_13 = '^^PH^+4592161730'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='5981145855', cx_4='CPR', cx_5='NNDN')
        mrg.prior_patient_account_number = CX(cx_1='AAUH202601150001')

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
    """ Based on live/dk/dk-columna-cis.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_CIS')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='LABKA')
        msh.receiving_facility = HD(hd_1='KBA')
        msh.date_time_of_message = '20260410083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MSG00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1205733960', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Johansen', xpn_2='Anne', xpn_3='Vibe', xpn_5='')
        pid.date_time_of_birth = '19730512'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Skanderborgvej 117', xad_3='Esbjerg Ø', xad_5='6705', xad_6='DK')
        pid.pid_13 = '^^PH^+4546903734'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='MED', pl_3='308', pl_4='C2')
        pv1.attending_doctor = XCN(xcn_1='45678', xcn_2='Christensen', xcn_3='Tove', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.financial_class = FC(fc_1='AAUH202604100001')

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
        orc.placer_order_number = EI(ei_1='ORD20260410001', ei_2='COLUMNA_CIS')
        orc.parent_order = EIP(eip_1='20260410083000')
        orc.orc_11 = '45678^Christensen^Tove^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260410001', ei_2='COLUMNA_CIS')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Komplet blodtælling', cwe_3='LN')
        obr.observation_date_time = '20260410083000'
        obr.obr_15 = '45678^Christensen^Tove^^^Dr.'

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
        obr_2.placer_order_number = EI(ei_1='ORD20260410001', ei_2='COLUMNA_CIS')
        obr_2.universal_service_identifier = CWE(cwe_1='BMP', cwe_2='Basisk metabolisk panel', cwe_3='LN')
        obr_2.observation_date_time = '20260410083000'
        obr_2.obr_15 = '45678^Christensen^Tove^^^Dr.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2]

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
    """ Based on live/dk/dk-columna-cis.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABKA')
        msh.sending_facility = HD(hd_1='KBA')
        msh.receiving_application = HD(hd_1='COLUMNA_CIS')
        msh.receiving_facility = HD(hd_1='AALBORG_UH')
        msh.date_time_of_message = '20260410143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1205733960', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Johansen', xpn_2='Anne', xpn_3='Vibe', xpn_5='')
        pid.date_time_of_birth = '19730512'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Skanderborgvej 117', xad_3='Esbjerg Ø', xad_5='6705', xad_6='DK')
        pid.pid_13 = '^^PH^+4546903734'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='MED', pl_3='308', pl_4='C2')
        pv1.attending_doctor = XCN(xcn_1='45678', xcn_2='Christensen', xcn_3='Tove', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.financial_class = FC(fc_1='AAUH202604100001')

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
        orc.placer_order_number = EI(ei_1='ORD20260410001', ei_2='COLUMNA_CIS')
        orc.parent_order = EIP(eip_1='20260410143000')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260410001', ei_2='COLUMNA_CIS')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Komplet blodtælling', cwe_3='LN')
        obr.observation_date_time = '20260410083000'
        obr.obr_15 = '45678^Christensen^Tove^^^Dr.'
        obr.filler_field_2 = '20260410143000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='WBC', cwe_2='Leukocytter', cwe_3='LN')
        obx.obx_5 = '7.2'
        obx.units = CWE(cwe_1='10*9/L')
        obx.reference_range = '3.5-10.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='RBC', cwe_2='Erytrocytter', cwe_3='LN')
        obx_2.obx_5 = '4.8'
        obx_2.units = CWE(cwe_1='10*12/L')
        obx_2.reference_range = '3.9-5.5'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='HGB', cwe_2='Hæmoglobin', cwe_3='LN')
        obx_3.obx_5 = '8.3'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '7.3-10.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='PLT', cwe_2='Trombocytter', cwe_3='LN')
        obx_4.obx_5 = '245'
        obx_4.units = CWE(cwe_1='10*9/L')
        obx_4.reference_range = '145-390'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='MCV', cwe_2='Middelcellevolumen', cwe_3='LN')
        obx_5.obx_5 = '88'
        obx_5.units = CWE(cwe_1='fL')
        obx_5.reference_range = '82-98'
        obx_5.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/dk/dk-columna-cis.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABKA')
        msh.sending_facility = HD(hd_1='KBA')
        msh.receiving_application = HD(hd_1='COLUMNA_CIS')
        msh.receiving_facility = HD(hd_1='AALBORG_UH')
        msh.date_time_of_message = '20260411101500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0903673749', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Madsen', xpn_2='Erik', xpn_3='Svend', xpn_5='')
        pid.date_time_of_birth = '19670309'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hunderupvej 2', xad_3='Brønshøj', xad_5='2700', xad_6='DK')
        pid.pid_13 = '^^PH^+4585554286'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='MED', pl_3='305', pl_4='A1')
        pv1.attending_doctor = XCN(xcn_1='56789', xcn_2='Frandsen', xcn_3='Camilla', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.financial_class = FC(fc_1='AAUH202604110001')

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
        orc.placer_order_number = EI(ei_1='ORD20260411001', ei_2='COLUMNA_CIS')
        orc.parent_order = EIP(eip_1='20260411101500')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260411001', ei_2='COLUMNA_CIS')
        obr.universal_service_identifier = CWE(cwe_1='MISC', cwe_2='Blodprøveresultater - samlet rapport', cwe_3='LN')
        obr.observation_date_time = '20260411080000'
        obr.obr_15 = '56789^Frandsen^Camilla^^^Dr.'
        obr.filler_field_2 = '20260411101500'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Laboratorierapport', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK'
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
    """ Based on live/dk/dk-columna-cis.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_CIS')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='PATIENTPORTAL')
        msh.receiving_facility = HD(hd_1='SUNDHED_DK')
        msh.date_time_of_message = '20260412080000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12')
        msh.message_control_id = 'MSG00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT20260501001', ei_2='COLUMNA_CIS')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_3='HL70276')
        sch.appointment_reason = CWE(cwe_1='Kontrol', cwe_2='Kontrol', cwe_5='COLUMNA')
        sch.appointment_type = CWE(cwe_1='30')
        sch.sch_9 = 'MIN'
        sch.appointment_duration_units = CNE(cne_3='30', cne_4='20260501093000', cne_5='20260501100000')
        sch.filler_contact_person = XCN(xcn_1='12345', xcn_2='Schmidt', xcn_3='Mathias', xcn_6='Dr.')
        sch.filler_contact_phone_number = XTN(xtn_3='PH', xtn_4='+4556183065')
        sch.filler_contact_address = XAD(xad_1='AAUH', xad_2='AMB', xad_3='120')
        sch.filler_contact_location = PL(pl_1='12345', pl_2='Schmidt', pl_3='Mathias', pl_6='Dr.')
        sch.entered_by_person = XCN(xcn_3='PH', xcn_4='+4556183065')
        sch.sch_21 = 'AAUH^AMB^120'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0102857128', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Dahl', xpn_2='Camilla', xpn_3='Marie', xpn_5='')
        pid.date_time_of_birth = '19850201'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Adelgade 115', xad_3='Hellerup', xad_5='2900', xad_6='DK')
        pid.pid_13 = '^^PH^+4543482061'

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='KONTROL', cwe_2='Ambulant kontrol', cwe_3='LOCAL')
        ais.start_date_time = '20260501093000'
        ais.start_date_time_offset_units = CNE(cne_1='30')
        ais.duration = 'MIN'

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='AAUH', pl_2='AMB', pl_3='120')

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='12345', xcn_2='Schmidt', xcn_3='Mathias', xcn_6='Dr.')

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.extra_segments = [ais, ail, aip]

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
    """ Based on live/dk/dk-columna-cis.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_CIS')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='PATIENTPORTAL')
        msh.receiving_facility = HD(hd_1='SUNDHED_DK')
        msh.date_time_of_message = '20260413100000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S14')
        msh.message_control_id = 'MSG00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT20260501001', ei_2='COLUMNA_CIS')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_3='HL70276')
        sch.appointment_reason = CWE(cwe_1='Kontrol', cwe_2='Kontrol', cwe_5='COLUMNA')
        sch.appointment_type = CWE(cwe_1='30')
        sch.sch_9 = 'MIN'
        sch.appointment_duration_units = CNE(cne_3='30', cne_4='20260501140000', cne_5='20260501143000')
        sch.filler_contact_person = XCN(xcn_1='12345', xcn_2='Schmidt', xcn_3='Mathias', xcn_6='Dr.')
        sch.filler_contact_phone_number = XTN(xtn_3='PH', xtn_4='+4556183065')
        sch.filler_contact_address = XAD(xad_1='AAUH', xad_2='AMB', xad_3='120')
        sch.filler_contact_location = PL(pl_1='12345', pl_2='Schmidt', pl_3='Mathias', pl_6='Dr.')
        sch.entered_by_person = XCN(xcn_3='PH', xcn_4='+4556183065')
        sch.sch_21 = 'AAUH^AMB^120'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0102857128', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Dahl', xpn_2='Camilla', xpn_3='Marie', xpn_5='')
        pid.date_time_of_birth = '19850201'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Adelgade 115', xad_3='Hellerup', xad_5='2900', xad_6='DK')
        pid.pid_13 = '^^PH^+4543482061'

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='KONTROL', cwe_2='Ambulant kontrol', cwe_3='LOCAL')
        ais.start_date_time = '20260501140000'
        ais.start_date_time_offset_units = CNE(cne_1='30')
        ais.duration = 'MIN'

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='AAUH', pl_2='AMB', pl_3='120')

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='12345', xcn_2='Schmidt', xcn_3='Mathias', xcn_6='Dr.')

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.extra_segments = [ais, ail, aip]

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
    """ Based on live/dk/dk-columna-cis.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_CIS')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='CARESTREAM_RIS')
        msh.receiving_facility = HD(hd_1='AAUH_RAD')
        msh.date_time_of_message = '20260414090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MSG00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1811929136', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Mortensen', xpn_2='Vibeke', xpn_3='Kristine', xpn_5='')
        pid.date_time_of_birth = '19921118'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Reventlowsvej 26', xad_3='København V', xad_5='1620', xad_6='DK')
        pid.pid_13 = '^^PH^+4574412626'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='ORT', pl_3='410', pl_4='D2')
        pv1.attending_doctor = XCN(xcn_1='67890', xcn_2='Nielsen', xcn_3='Kristian', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ORT')
        pv1.financial_class = FC(fc_1='AAUH202604140001')

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
        orc.placer_order_number = EI(ei_1='ORD20260414001', ei_2='COLUMNA_CIS')
        orc.parent_order = EIP(eip_1='20260414090000')
        orc.orc_11 = '67890^Nielsen^Kristian^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260414001', ei_2='COLUMNA_CIS')
        obr.universal_service_identifier = CWE(cwe_1='XKNEE', cwe_2='Røntgen af knæ', cwe_3='LOCAL')
        obr.observation_date_time = '20260414090000'
        obr.relevant_clinical_information = CWE(cwe_1='Smerter i ve. knæ efter fald')
        obr.obr_14 = '67890^Nielsen^Kristian^^^Dr.'

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
    """ Based on live/dk/dk-columna-cis.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MADS')
        msh.sending_facility = HD(hd_1='SSI')
        msh.receiving_application = HD(hd_1='COLUMNA_CIS')
        msh.receiving_facility = HD(hd_1='AALBORG_UH')
        msh.date_time_of_message = '20260415161500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2507835681', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Petersen', xpn_2='Bjarne', xpn_3='Walther', xpn_5='')
        pid.date_time_of_birth = '19830725'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Skovvej 229', xad_3='Thisted', xad_5='7700', xad_6='DK')
        pid.pid_13 = '^^PH^+4540592023'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='MED', pl_3='302', pl_4='B4')
        pv1.attending_doctor = XCN(xcn_1='78901', xcn_2='Mikkelsen', xcn_3='Knud', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.financial_class = FC(fc_1='AAUH202604150001')

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
        orc.placer_order_number = EI(ei_1='ORD20260415001', ei_2='MADS')
        orc.parent_order = EIP(eip_1='20260415161500')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260415001', ei_2='MADS')
        obr.universal_service_identifier = CWE(cwe_1='BCUL', cwe_2='Bloddyrkning', cwe_3='LN')
        obr.observation_date_time = '20260414200000'
        obr.obr_15 = '78901^Mikkelsen^Knud^^^Dr.'
        obr.filler_field_2 = '20260415161500'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='ORGANISM', cwe_2='Identificeret mikroorganisme', cwe_3='LN')
        obx.obx_5 = 'ECO^Escherichia coli^LN'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='SUSCEPT', cwe_2='Følsomhed - Ampicillin', cwe_3='LN')
        obx_2.obx_5 = 'R'
        obx_2.interpretation_codes = CWE(cwe_1='A')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='SUSCEPT', cwe_2='Følsomhed - Ciprofloxacin', cwe_3='LN')
        obx_3.obx_5 = 'S'
        obx_3.interpretation_codes = CWE(cwe_1='A')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='SUSCEPT', cwe_2='Følsomhed - Gentamicin', cwe_3='LN')
        obx_4.obx_5 = 'S'
        obx_4.interpretation_codes = CWE(cwe_1='A')
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
    """ Based on live/dk/dk-columna-cis.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_CIS')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='DOKUMENTDELING')
        msh.receiving_facility = HD(hd_1='NSP')
        msh.date_time_of_message = '20260416120000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02')
        msh.message_control_id = 'MSG00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260416120000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0903673749', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Madsen', xpn_2='Erik', xpn_3='Svend', xpn_5='')
        pid.date_time_of_birth = '19670309'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hunderupvej 2', xad_3='Brønshøj', xad_5='2700', xad_6='DK')
        pid.pid_13 = '^^PH^+4585554286'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='MED', pl_3='305', pl_4='A1')
        pv1.attending_doctor = XCN(xcn_1='56789', xcn_2='Frandsen', xcn_3='Camilla', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.financial_class = FC(fc_1='AAUH202604110001')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='CN', cwe_2='Klinisk notat')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20260416120000'
        txa.primary_activity_provider_code_name = XCN(xcn_1='56789', xcn_2='Frandsen', xcn_3='Camilla', xcn_6='Dr.')
        txa.transcription_date_time = '20260416120000'
        txa.unique_document_number = EI(ei_1='DOC20260416001')
        txa.document_confidentiality_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='NOTE', cwe_2='Klinisk notat', cwe_3='LN')
        obx.obx_5 = (
            'Patient indlagt med pneumoni. Behandles med iv. penicillin. Stabil tilstand, sat 96% på atmosfærisk luft. Plan: Fortsat antibiotika, kontrol'
            ' af CRP og leukocytter i morgen.'
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
    """ Based on live/dk/dk-columna-cis.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PATOLOGI')
        msh.sending_facility = HD(hd_1='AAUH_PAT')
        msh.receiving_application = HD(hd_1='COLUMNA_CIS')
        msh.receiving_facility = HD(hd_1='AALBORG_UH')
        msh.date_time_of_message = '20260417100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1406655786', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Dahl', xpn_2='Camilla', xpn_3='Yrsa', xpn_5='')
        pid.date_time_of_birth = '19650614'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Lindevej 168', xad_3='Holstebro', xad_5='7500', xad_6='DK')
        pid.pid_13 = '^^PH^+4557144563'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='KIR', pl_3='206', pl_4='A3')
        pv1.attending_doctor = XCN(xcn_1='89012', xcn_2='Sørensen', xcn_3='Sara', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='KIR')
        pv1.financial_class = FC(fc_1='AAUH202604170001')

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
        orc.placer_order_number = EI(ei_1='ORD20260417001', ei_2='PATOLOGI')
        orc.parent_order = EIP(eip_1='20260417100000')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260417001', ei_2='PATOLOGI')
        obr.universal_service_identifier = CWE(cwe_1='PATHBX', cwe_2='Biopsi - colon', cwe_3='LN')
        obr.observation_date_time = '20260415120000'
        obr.obr_15 = '89012^Sørensen^Sara^^^Dr.'
        obr.filler_field_2 = '20260417100000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='PATDIAG', cwe_2='Patologisk diagnose', cwe_3='LN')
        obx.obx_5 = 'Tubulært adenom med lavgradig dysplasi. Frie resektionsrande.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Patologirapport', cwe_3='LN')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJd'
            'Ci9Db3VudCAxCi9NZWRpYUJveCBbMCAwIDU5NSA4NDJdCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdl'
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
    """ Based on live/dk/dk-columna-cis.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_CIS')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='LANDSPATIENTREGISTERET')
        msh.receiving_facility = HD(hd_1='SST')
        msh.date_time_of_message = '20260418020000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260418020000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0512794045', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Christiansen', xpn_2='Henrik', xpn_3='Ejvind', xpn_5='')
        pid.date_time_of_birth = '19791205'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Tagensvej 1', xad_3='Odense N', xad_5='5200', xad_6='DK')
        pid.pid_13 = '^^PH^+4564278518~^^CP^+4529388864'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='AKM', pl_3='101', pl_4='A1')
        pv1.attending_doctor = XCN(xcn_1='90123', xcn_2='Krogh', xcn_3='Inger', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='AKM')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='90123', xcn_2='Krogh', xcn_3='Inger', xcn_6='Dr.')
        pv1.visit_number = CX(cx_1='AAUH202604180001')
        pv1.prior_temporary_location = PL(pl_1='20260418020000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Akut abdomen')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/dk/dk-columna-cis.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_CIS')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='MUSE_ECG')
        msh.receiving_facility = HD(hd_1='AAUH_KAR')
        msh.date_time_of_message = '20260419083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MSG00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0512794045', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Christiansen', xpn_2='Henrik', xpn_3='Ejvind', xpn_5='')
        pid.date_time_of_birth = '19791205'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Tagensvej 1', xad_3='Odense N', xad_5='5200', xad_6='DK')
        pid.pid_13 = '^^PH^+4564278518'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='KAR', pl_3='501', pl_4='B3')
        pv1.attending_doctor = XCN(xcn_1='01234', xcn_2='Christiansen', xcn_3='Knud', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='KAR')
        pv1.financial_class = FC(fc_1='AAUH202604190001')

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
        orc.placer_order_number = EI(ei_1='ORD20260419001', ei_2='COLUMNA_CIS')
        orc.parent_order = EIP(eip_1='20260419083000')
        orc.orc_11 = '01234^Christiansen^Knud^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260419001', ei_2='COLUMNA_CIS')
        obr.universal_service_identifier = CWE(cwe_1='ECG', cwe_2='EKG - 12 afledninger', cwe_3='LOCAL')
        obr.observation_date_time = '20260419083000'
        obr.relevant_clinical_information = CWE(cwe_1='Brystsmerter og dyspnø')
        obr.obr_14 = '01234^Christiansen^Knud^^^Dr.'

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
    """ Based on live/dk/dk-columna-cis.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABKA')
        msh.sending_facility = HD(hd_1='KBA')
        msh.receiving_application = HD(hd_1='COLUMNA_CIS')
        msh.receiving_facility = HD(hd_1='AALBORG_UH')
        msh.date_time_of_message = '20260420151500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1703941034', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Pedersen', xpn_2='Katrine', xpn_3='Birgitte', xpn_5='')
        pid.date_time_of_birth = '19940317'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Frederikssundsvej 205', xad_3='Herning', xad_5='7400', xad_6='DK')
        pid.pid_13 = '^^PH^+4556159297'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='MED', pl_3='310', pl_4='D1')
        pv1.attending_doctor = XCN(xcn_1='23456', xcn_2='Mikkelsen', xcn_3='Ida', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.financial_class = FC(fc_1='AAUH202604200001')

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
        orc.placer_order_number = EI(ei_1='ORD20260420001', ei_2='LABKA')
        orc.parent_order = EIP(eip_1='20260420151500')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260420001', ei_2='LABKA')
        obr.universal_service_identifier = CWE(cwe_1='K', cwe_2='Kalium', cwe_3='LN')
        obr.observation_date_time = '20260420140000'
        obr.obr_15 = '23456^Mikkelsen^Ida^^^Dr.'
        obr.filler_field_2 = '20260420151500'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='K', cwe_2='Kalium', cwe_3='LN')
        obx.obx_5 = '6.8'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.5-5.0'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='NA', cwe_2='Natrium', cwe_3='LN')
        obx_2.obx_5 = '131'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '137-145'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='CREA', cwe_2='Kreatinin', cwe_3='LN')
        obx_3.obx_5 = '287'
        obx_3.units = CWE(cwe_1='umol/L')
        obx_3.reference_range = '45-105'
        obx_3.interpretation_codes = CWE(cwe_1='HH')
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
    """ Based on live/dk/dk-columna-cis.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABKA')
        msh.sending_facility = HD(hd_1='KBA')
        msh.receiving_application = HD(hd_1='COLUMNA_CIS')
        msh.receiving_facility = HD(hd_1='AALBORG_UH')
        msh.date_time_of_message = '20260421091000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2808569328', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Carlsen', xpn_2='Camilla', xpn_3='Viola', xpn_5='')
        pid.date_time_of_birth = '19560828'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Maglekildevej 232', xad_3='Esbjerg N', xad_5='6715', xad_6='DK')
        pid.pid_13 = '^^PH^+4559664460'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='HÆM', pl_3='AMB')
        pv1.attending_doctor = XCN(xcn_1='34567', xcn_2='Petersen', xcn_3='Laura', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='HÆM')
        pv1.financial_class = FC(fc_1='AAUH202604210001')

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
        orc.placer_order_number = EI(ei_1='ORD20260421001', ei_2='LABKA')
        orc.parent_order = EIP(eip_1='20260421091000')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260421001', ei_2='LABKA')
        obr.universal_service_identifier = CWE(cwe_1='DIFF', cwe_2='Differentialtælling', cwe_3='LN')
        obr.observation_date_time = '20260421080000'
        obr.obr_15 = '34567^Petersen^Laura^^^Dr.'
        obr.filler_field_2 = '20260421091000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='WBC', cwe_2='Leukocytter', cwe_3='LN')
        obx.obx_5 = '12.4'
        obx.units = CWE(cwe_1='10*9/L')
        obx.reference_range = '3.5-10.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='NEUT', cwe_2='Neutrofile', cwe_3='LN')
        obx_2.obx_5 = '8.9'
        obx_2.units = CWE(cwe_1='10*9/L')
        obx_2.reference_range = '1.5-7.5'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='LYMPH', cwe_2='Lymfocytter', cwe_3='LN')
        obx_3.obx_5 = '2.1'
        obx_3.units = CWE(cwe_1='10*9/L')
        obx_3.reference_range = '1.0-4.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='MONO', cwe_2='Monocytter', cwe_3='LN')
        obx_4.obx_5 = '0.9'
        obx_4.units = CWE(cwe_1='10*9/L')
        obx_4.reference_range = '0.2-1.0'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='EOS', cwe_2='Eosinofile', cwe_3='LN')
        obx_5.obx_5 = '0.4'
        obx_5.units = CWE(cwe_1='10*9/L')
        obx_5.reference_range = '0.0-0.5'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='BASO', cwe_2='Basofile', cwe_3='LN')
        obx_6.obx_5 = '0.1'
        obx_6.units = CWE(cwe_1='10*9/L')
        obx_6.reference_range = '0.0-0.2'
        obx_6.interpretation_codes = CWE(cwe_1='N')
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
