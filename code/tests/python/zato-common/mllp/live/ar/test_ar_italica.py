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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, EI, HD, MOC, MSG, OG, PL, PT, VID, XAD, XCN, XON, XPN, XTN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA05NextOfKin, AdtA39Patient, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, \
    OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12Patient, \
    SiuS12PersonnelResource, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, DG1, EVN, IN1, MRG, MSA, MSH, NK1, NTE, OBR, OBX, ORC, PID, PV1, RGS, RXO, RXR, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ar', 'ar-italica.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ar/ar-italica.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ITALICA')
        msh.sending_facility = HD(hd_1='HIBA')
        msh.receiving_application = HD(hd_1='LAB_CENTRAL')
        msh.receiving_facility = HD(hd_1='HIBA')
        msh.date_time_of_message = '20260315083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'HIBA00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260315083000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC445678', cx_4='HIBA', cx_5='MR')
        pid.patient_name = XPN(xpn_1='FERNANDEZ', xpn_2='MARIA', xpn_3='INES', xpn_5='Sra.')
        pid.date_time_of_birth = '19750412'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av. Pueyrredon 1640', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1118AAT', xad_6='AR')
        pid.pid_13 = '^^PH^01145559876~^^CP^01161234567~^^Internet^mfernandez@gmail.com'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='HAB301', pl_3='CAMA1', pl_4='HIBA')
        pv1.attending_doctor = XCN(xcn_1='MED100', xcn_2='RODRIGUEZ', xcn_3='CARLOS', xcn_6='Dr.')
        pv1.consulting_doctor = XCN(xcn_1='MED200', xcn_2='GOMEZ', xcn_3='PATRICIA', xcn_6='Dra.')
        pv1.temporary_location = PL(pl_1='MED')
        pv1.visit_number = CX(cx_1='ENC445678')
        pv1.pending_location = PL(pl_1='UTI', pl_2='HAB102', pl_3='CAMA2', pl_4='HIBA')
        pv1.admit_date_time = '20260315083000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='0')
        in1.insurance_company_id = CX(cx_1='OS001')
        in1.insurance_company_name = XON(xon_1='OSDE')
        in1.insurance_company_address = XAD(xad_1='Av. Leandro N. Alem 1067', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1001AAF', xad_6='AR')
        in1.insureds_id_number = CX(cx_1='54')

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
    """ Based on live/ar/ar-italica.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ITALICA')
        msh.sending_facility = HD(hd_1='HIBA')
        msh.receiving_application = HD(hd_1='LAB_CENTRAL')
        msh.receiving_facility = HD(hd_1='HIBA')
        msh.date_time_of_message = '20260316100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'HIBA00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260316100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC445678', cx_4='HIBA', cx_5='MR')
        pid.patient_name = XPN(xpn_1='FERNANDEZ', xpn_2='MARIA', xpn_3='INES', xpn_5='Sra.')
        pid.date_time_of_birth = '19750412'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av. Pueyrredon 1640', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1118AAT', xad_6='AR')
        pid.pid_13 = '^^PH^01145559876~^^CP^01161234567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UTI', pl_2='HAB102', pl_3='CAMA2', pl_4='HIBA')
        pv1.attending_doctor = XCN(xcn_1='MED100', xcn_2='RODRIGUEZ', xcn_3='CARLOS', xcn_6='Dr.')
        pv1.consulting_doctor = XCN(xcn_1='MED200', xcn_2='GOMEZ', xcn_3='PATRICIA', xcn_6='Dra.')
        pv1.temporary_location = PL(pl_1='MED')
        pv1.visit_number = CX(cx_1='ENC445678')
        pv1.pending_location = PL(pl_1='CARDIO', pl_2='HAB301', pl_3='CAMA1', pl_4='HIBA')
        pv1.admit_date_time = '20260316100000'

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
    """ Based on live/ar/ar-italica.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ITALICA')
        msh.sending_facility = HD(hd_1='HIBA')
        msh.receiving_application = HD(hd_1='LAB_CENTRAL')
        msh.receiving_facility = HD(hd_1='HIBA')
        msh.date_time_of_message = '20260320140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'HIBA00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260320140000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC445678', cx_4='HIBA', cx_5='MR')
        pid.patient_name = XPN(xpn_1='FERNANDEZ', xpn_2='MARIA', xpn_3='INES', xpn_5='Sra.')
        pid.date_time_of_birth = '19750412'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av. Pueyrredon 1640', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1118AAT', xad_6='AR')
        pid.pid_13 = '^^PH^01145559876~^^CP^01161234567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='HAB301', pl_3='CAMA1', pl_4='HIBA')
        pv1.attending_doctor = XCN(xcn_1='MED100', xcn_2='RODRIGUEZ', xcn_3='CARLOS', xcn_6='Dr.')
        pv1.consulting_doctor = XCN(xcn_1='MED200', xcn_2='GOMEZ', xcn_3='PATRICIA', xcn_6='Dra.')
        pv1.temporary_location = PL(pl_1='MED')
        pv1.visit_number = CX(cx_1='ENC445678')
        pv1.pending_location = PL(pl_1='UTI', pl_2='HAB102', pl_3='CAMA2', pl_4='HIBA')
        pv1.admit_date_time = '20260320140000'

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
    """ Based on live/ar/ar-italica.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ITALICA')
        msh.sending_facility = HD(hd_1='HIBA')
        msh.receiving_application = HD(hd_1='TURNOS')
        msh.receiving_facility = HD(hd_1='HIBA')
        msh.date_time_of_message = '20260321101500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'HIBA00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260321101500'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC556789', cx_4='HIBA', cx_5='MR'), CX(cx_1='20-28456789-3', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='LOPEZ GARCIA', xpn_2='JUAN', xpn_3='PABLO', xpn_5='Sr.')
        pid.date_time_of_birth = '19820930'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Defensa 1234', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1065AAR', xad_6='AR')
        pid.pid_13 = '^^PH^01148887654~^^CP^01155678901'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='C205', pl_4='HIBA')
        pv1.attending_doctor = XCN(xcn_1='MED300', xcn_2='MARTINEZ', xcn_3='ANA', xcn_6='Dra.')
        pv1.total_payments = '20260321101500'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='0')
        in1.insurance_company_id = CX(cx_1='OS002')
        in1.insurance_company_name = XON(xon_1='SWISS MEDICAL')
        in1.insurance_company_address = XAD(xad_1='Av. Pueyrredon 1550', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1118AAR', xad_6='AR')
        in1.insureds_id_number = CX(cx_1='54')

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
    """ Based on live/ar/ar-italica.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ITALICA')
        msh.sending_facility = HD(hd_1='HIBA')
        msh.receiving_application = HD(hd_1='MAESTRO_PAC')
        msh.receiving_facility = HD(hd_1='HIBA')
        msh.date_time_of_message = '20260322090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'HIBA00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260322090000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC445678', cx_4='HIBA', cx_5='MR'), CX(cx_1='20-24567890-5', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='FERNANDEZ', xpn_2='MARIA', xpn_3='INES', xpn_5='Sra.')
        pid.date_time_of_birth = '19750412'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av. Corrientes 4500', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1195AAJ', xad_6='AR')
        pid.pid_13 = '^^PH^01145559876~^^CP^01161234567~^^Internet^mfernandez@outlook.com'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='HAB301', pl_3='CAMA1', pl_4='HIBA')
        pv1.attending_doctor = XCN(xcn_1='MED100', xcn_2='RODRIGUEZ', xcn_3='CARLOS', xcn_6='Dr.')
        pv1.consulting_doctor = XCN(xcn_1='MED200', xcn_2='GOMEZ', xcn_3='PATRICIA', xcn_6='Dra.')
        pv1.temporary_location = PL(pl_1='MED')
        pv1.visit_number = CX(cx_1='ENC445678')
        pv1.pending_location = PL(pl_1='UTI', pl_2='HAB102', pl_3='CAMA2', pl_4='HIBA')
        pv1.admit_date_time = '20260322090000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='0')
        in1.insurance_company_id = CX(cx_1='OS001')
        in1.insurance_company_name = XON(xon_1='OSDE')
        in1.insurance_company_address = XAD(xad_1='Av. Leandro N. Alem 1067', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1001AAF', xad_6='AR')
        in1.insureds_id_number = CX(cx_1='54')

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
    """ Based on live/ar/ar-italica.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ITALICA')
        msh.sending_facility = HD(hd_1='HIBA')
        msh.receiving_application = HD(hd_1='LAB_CENTRAL')
        msh.receiving_facility = HD(hd_1='HIBA')
        msh.date_time_of_message = '20260323080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'HIBA00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC445678', cx_4='HIBA', cx_5='MR')
        pid.patient_name = XPN(xpn_1='FERNANDEZ', xpn_2='MARIA', xpn_3='INES')
        pid.date_time_of_birth = '19750412'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='HAB301', pl_3='CAMA1', pl_4='HIBA')
        pv1.attending_doctor = XCN(xcn_1='MED100', xcn_2='RODRIGUEZ', xcn_3='CARLOS', xcn_6='Dr.')

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
        orc.placer_order_number = EI(ei_1='SOL88901', ei_2='ITALICA')
        orc.placer_order_group_number = EI(ei_1='GRP001', ei_2='ITALICA')
        orc.date_time_of_order_event = '20260323080000'
        orc.orc_12 = 'MED100^RODRIGUEZ^CARLOS^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL88901', ei_2='ITALICA')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Panel metabolico completo', cwe_3='LN')
        obr.observation_date_time = '20260323074500'
        obr.obr_16 = 'MED100^RODRIGUEZ^CARLOS^^^Dr.'
        obr.obr_27 = '^URGENTE'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I50.0', cwe_2='Insuficiencia cardiaca congestiva', cwe_3='I10')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Paciente con edema en miembros inferiores hace 48 hs.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [nte]

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
    """ Based on live/ar/ar-italica.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_CENTRAL')
        msh.sending_facility = HD(hd_1='HIBA')
        msh.receiving_application = HD(hd_1='ITALICA')
        msh.receiving_facility = HD(hd_1='HIBA')
        msh.date_time_of_message = '20260323143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB00042'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC445678', cx_4='HIBA', cx_5='MR')
        pid.patient_name = XPN(xpn_1='FERNANDEZ', xpn_2='MARIA', xpn_3='INES')
        pid.date_time_of_birth = '19750412'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='HAB301', pl_3='CAMA1', pl_4='HIBA')

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
        orc.placer_order_number = EI(ei_1='SOL88901', ei_2='ITALICA')
        orc.filler_order_number = EI(ei_1='RES55501', ei_2='LAB_CENTRAL')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL88901', ei_2='ITALICA')
        obr.filler_order_number = EI(ei_1='RES55501', ei_2='LAB_CENTRAL')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Panel metabolico completo', cwe_3='LN')
        obr.observation_date_time = '20260323074500'
        obr.obr_14 = 'MED100^RODRIGUEZ^CARLOS^^^Dr.'
        obr.filler_field_1 = '20260323140000'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucosa', cwe_3='LN')
        obx.obx_5 = '95'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '70-110'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinina', cwe_3='LN')
        obx_2.obx_5 = '1.2'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '0.7-1.3'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea', cwe_3='LN')
        obx_3.obx_5 = '38'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '10-50'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodio', cwe_3='LN')
        obx_4.obx_5 = '141'
        obx_4.units = CWE(cwe_1='mEq/L')
        obx_4.reference_range = '136-145'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potasio', cwe_3='LN')
        obx_5.obx_5 = '4.5'
        obx_5.units = CWE(cwe_1='mEq/L')
        obx_5.reference_range = '3.5-5.0'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='17861-6', cwe_2='Calcio', cwe_3='LN')
        obx_6.obx_5 = '9.2'
        obx_6.units = CWE(cwe_1='mg/dL')
        obx_6.reference_range = '8.5-10.5'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT (TGP)', cwe_3='LN')
        obx_7.obx_5 = '32'
        obx_7.units = CWE(cwe_1='U/L')
        obx_7.reference_range = '7-56'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'

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
    """ Based on live/ar/ar-italica.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ITALICA')
        msh.sending_facility = HD(hd_1='HIBA')
        msh.receiving_application = HD(hd_1='PACS_RIS')
        msh.receiving_facility = HD(hd_1='HIBA')
        msh.date_time_of_message = '20260324090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'HIBA00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC667890', cx_4='HIBA', cx_5='MR'), CX(cx_1='20-35678901-2', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='GARCIA', xpn_2='PEDRO', xpn_3='ANTONIO', xpn_5='Sr.')
        pid.date_time_of_birth = '19680115'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Av. Santa Fe 2900', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1425BGN', xad_6='AR')
        pid.pid_13 = '^^CP^01156789012'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='IMG01', pl_4='HIBA')
        pv1.attending_doctor = XCN(xcn_1='MED400', xcn_2='SOSA', xcn_3='LAURA', xcn_6='Dra.')

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
        orc.placer_order_number = EI(ei_1='SOL99012', ei_2='ITALICA')
        orc.placer_order_group_number = EI(ei_1='GRP002', ei_2='ITALICA')
        orc.date_time_of_order_event = '20260324090000'
        orc.orc_12 = 'MED400^SOSA^LAURA^^^Dra.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL99012', ei_2='ITALICA')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Radiografia de torax PA y lateral', cwe_3='CPT')
        obr.observation_date_time = '20260324090000'
        obr.obr_16 = 'MED400^SOSA^LAURA^^^Dra.'
        obr.obr_27 = '^RUTINA'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.9', cwe_2='Neumonia, no especificada', cwe_3='I10')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Control evolutivo de neumonia adquirida en la comunidad.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [nte]

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
    """ Based on live/ar/ar-italica.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PACS_RIS')
        msh.sending_facility = HD(hd_1='HIBA')
        msh.receiving_application = HD(hd_1='ITALICA')
        msh.receiving_facility = HD(hd_1='HIBA')
        msh.date_time_of_message = '20260324153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RAD00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC667890', cx_4='HIBA', cx_5='MR')
        pid.patient_name = XPN(xpn_1='GARCIA', xpn_2='PEDRO', xpn_3='ANTONIO')
        pid.date_time_of_birth = '19680115'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='IMG01', pl_4='HIBA')
        pv1.attending_doctor = XCN(xcn_1='MED400', xcn_2='SOSA', xcn_3='LAURA', xcn_6='Dra.')

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
        orc.placer_order_number = EI(ei_1='SOL99012', ei_2='ITALICA')
        orc.filler_order_number = EI(ei_1='INF77801', ei_2='PACS_RIS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL99012', ei_2='ITALICA')
        obr.filler_order_number = EI(ei_1='INF77801', ei_2='PACS_RIS')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Radiografia de torax PA y lateral', cwe_3='CPT')
        obr.observation_date_time = '20260324090000'
        obr.obr_14 = 'MED400^SOSA^LAURA^^^Dra.'
        obr.filler_field_1 = '20260324150000'
        obr.results_rpt_status_chng_date_time = 'RAD'
        obr.charge_to_practice = MOC(moc_1='F')
        obr.transportation_mode = 'MED500^PEREZ^DIEGO^^^Dr.'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='71020&IMP', cwe_2='Radiografia torax impresion', cwe_3='CPT')
        obx.obx_5 = (
            'Infiltrado alveolar bilateral con predominio en bases. Derrame pleural bilateral de escasa cuantia. Silueta cardiaca dentro de limites norma'
            'les.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='71020&REC', cwe_2='Radiografia torax recomendacion', cwe_3='CPT')
        obx_2.obx_5 = 'Se sugiere control radiologico en 72 hs para evaluar evolucion.'
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
    """ Based on live/ar/ar-italica.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_CENTRAL')
        msh.sending_facility = HD(hd_1='HIBA')
        msh.receiving_application = HD(hd_1='ITALICA')
        msh.receiving_facility = HD(hd_1='HIBA')
        msh.date_time_of_message = '20260325110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB00055'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC778901', cx_4='HIBA', cx_5='MR')
        pid.patient_name = XPN(xpn_1='MARTINEZ', xpn_2='ANA', xpn_3='BELEN')
        pid.date_time_of_birth = '19900620'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GINECO', pl_2='HAB205', pl_3='CAMA1', pl_4='HIBA')

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
        orc.placer_order_number = EI(ei_1='SOL99100', ei_2='ITALICA')
        orc.filler_order_number = EI(ei_1='RES55600', ei_2='LAB_CENTRAL')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL99100', ei_2='ITALICA')
        obr.filler_order_number = EI(ei_1='RES55600', ei_2='LAB_CENTRAL')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Hemograma completo', cwe_3='LN')
        obr.observation_date_time = '20260325080000'
        obr.obr_14 = 'MED600^DIAZ^ROBERTO^^^Dr.'
        obr.filler_field_1 = '20260325103000'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobina', cwe_3='LN')
        obx.obx_5 = '12.8'
        obx.units = CWE(cwe_1='g/dL')
        obx.reference_range = '12.0-16.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocrito', cwe_3='LN')
        obx_2.obx_5 = '38.5'
        obx_2.units = CWE(cwe_1='%')
        obx_2.reference_range = '36.0-46.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='789-8', cwe_2='Eritrocitos', cwe_3='LN')
        obx_3.obx_5 = '4.35'
        obx_3.units = CWE(cwe_1='x10E6/uL')
        obx_3.reference_range = '3.80-5.10'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leucocitos', cwe_3='LN')
        obx_4.obx_5 = '7.2'
        obx_4.units = CWE(cwe_1='x10E3/uL')
        obx_4.reference_range = '4.5-11.0'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='Plaquetas', cwe_3='LN')
        obx_5.obx_5 = '245'
        obx_5.units = CWE(cwe_1='x10E3/uL')
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
        obx_6.observation_identifier = CWE(cwe_1='787-2', cwe_2='VCM', cwe_3='LN')
        obx_6.obx_5 = '88.5'
        obx_6.units = CWE(cwe_1='fL')
        obx_6.reference_range = '80.0-100.0'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='786-4', cwe_2='HCM', cwe_3='LN')
        obx_7.obx_5 = '29.4'
        obx_7.units = CWE(cwe_1='pg')
        obx_7.reference_range = '27.0-33.0'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'

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
    """ Based on live/ar/ar-italica.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ITALICA')
        msh.sending_facility = HD(hd_1='HIBA')
        msh.receiving_application = HD(hd_1='TURNOS')
        msh.receiving_facility = HD(hd_1='HIBA')
        msh.date_time_of_message = '20260401100000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'HIBA00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='TUR334455', ei_2='ITALICA')
        sch.filler_appointment_id = EI(ei_1='TUR334455', ei_2='ITALICA')
        sch.appointment_reason = CWE(cwe_1='ROUTINE', cwe_2='Rutina', cwe_3='HL70277')
        sch.appointment_type = CWE(cwe_1='CONSUL', cwe_2='Consulta ambulatoria', cwe_3='LOCAL')
        sch.sch_9 = '20'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^20^202604081000^202604081020'
        sch.filler_contact_person = XCN(xcn_1='MED300', xcn_2='MARTINEZ', xcn_3='ANA', xcn_6='Dra.')
        sch.filler_contact_phone_number = XTN(xtn_3='PH', xtn_4='01148001234')
        sch.filler_contact_address = XAD(xad_1='CONSUL', xad_2='C205', xad_4='HIBA')
        sch.entered_by_person = XCN(xcn_1='Confirmado')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC556789', cx_4='HIBA', cx_5='MR')
        pid.patient_name = XPN(xpn_1='LOPEZ GARCIA', xpn_2='JUAN', xpn_3='PABLO')
        pid.date_time_of_birth = '19820930'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='C205', pl_4='HIBA')
        pv1.attending_doctor = XCN(xcn_1='MED300', xcn_2='MARTINEZ', xcn_3='ANA', xcn_6='Dra.')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.segment_action_code = 'A'

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.segment_action_code = 'A'
        ais.universal_service_identifier = CWE(cwe_1='CONSULTA_CARDIO', cwe_2='Consulta Cardiologia', cwe_3='LOCAL')
        ais.start_date_time_offset_units = CNE(cne_1='202604081000')
        ais.duration = '0'
        ais.duration_units = CNE(cne_1='MIN')
        ais.allow_substitution_code = CWE(cwe_1='20')
        ais.filler_status_code = CWE(cwe_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.segment_action_code = 'A'
        aip.personnel_resource_id = XCN(xcn_1='MED300', xcn_2='MARTINEZ', xcn_3='ANA', xcn_6='Dra.')
        aip.resource_type = CWE(cwe_1='ATT', cwe_2='Medico tratante', cwe_3='HL70443')

        # .. build the PERSONNEL_RESOURCE group ..
        personnel_resource = SiuS12PersonnelResource()
        personnel_resource.aip = aip

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service
        resources.personnel_resource = personnel_resource

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.segment_action_code = 'A'
        ail.location_resource_id = PL(pl_1='CONSUL', pl_2='C205', pl_4='HIBA')
        ail.location_group = CWE(cwe_1='202604081000')
        ail.start_date_time = '0'
        ail.start_date_time_offset = 'MIN'
        ail.start_date_time_offset_units = CNE(cne_1='20')
        ail.duration = 'MIN'

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources
        msg.extra_segments = [ail]

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
    """ Based on live/ar/ar-italica.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ITALICA')
        msh.sending_facility = HD(hd_1='HIBA')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='HIBA')
        msh.date_time_of_message = '20260402080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'HIBA00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20260402080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC889012', cx_4='HIBA', cx_5='MR'), CX(cx_1='20-40123456-7', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='RUIZ', xpn_2='VALERIA', xpn_3='SOLEDAD', xpn_5='Sra.')
        pid.date_time_of_birth = '19951108'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av. Rivadavia 7200', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1406GLJ', xad_6='AR')
        pid.pid_13 = '^^CP^01167890123~^^Internet^vruiz@hotmail.com'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='RUIZ', xpn_2='JORGE', xpn_4='Sr.')
        nk1.relationship = CWE(cwe_1='FTH', cwe_2='Padre', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Av. Rivadavia 7200', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1406GLJ', xad_6='AR')
        nk1.nk1_5 = '^^PH^01145001234'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin

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
    """ Based on live/ar/ar-italica.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ITALICA')
        msh.sending_facility = HD(hd_1='HIBA')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='HIBA')
        msh.date_time_of_message = '20260403090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'HIBA00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260403090000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC445678', cx_4='HIBA', cx_5='MR'), CX(cx_1='20-24567890-5', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='FERNANDEZ', xpn_2='MARIA', xpn_3='INES', xpn_5='Sra.')
        pid.date_time_of_birth = '19750412'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Av. Corrientes 4500', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1195AAJ', xad_6='AR')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='HC999888', cx_4='HIBA', cx_5='MR')
        mrg.mrg_2 = ''

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
    """ Based on live/ar/ar-italica.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ITALICA')
        msh.sending_facility = HD(hd_1='HIBA')
        msh.receiving_application = HD(hd_1='FARMACIA')
        msh.receiving_facility = HD(hd_1='HIBA')
        msh.date_time_of_message = '20260404143000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'HIBA00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC445678', cx_4='HIBA', cx_5='MR')
        pid.patient_name = XPN(xpn_1='FERNANDEZ', xpn_2='MARIA', xpn_3='INES')
        pid.date_time_of_birth = '19750412'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='HAB301', pl_3='CAMA1', pl_4='HIBA')
        pv1.attending_doctor = XCN(xcn_1='MED100', xcn_2='RODRIGUEZ', xcn_3='CARLOS', xcn_6='Dr.')

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
        orc.placer_order_number = EI(ei_1='RX001234', ei_2='ITALICA')
        orc.placer_order_group_number = EI(ei_1='GRP003', ei_2='ITALICA')
        orc.date_time_of_order_event = '20260404143000'
        orc.orc_12 = 'MED100^RODRIGUEZ^CARLOS^^^Dr.'

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='1')
        rxo.requested_give_amount_minimum = '29046^Enalapril 10mg^VADEMECUM'
        rxo.requested_give_units = CWE(cwe_1='10')
        rxo.requested_dosage_form = CWE(cwe_1='mg')
        rxo.providers_pharmacy_treatment_instructions = CWE(cwe_1='TAB', cwe_2='Comprimido', cwe_3='HL70323')
        rxo.number_of_refills = '1'
        rxo.pharmacist_treatment_suppliers_verifier_id = XCN(xcn_1='0')
        rxo.requested_give_strength = '20260404143000'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='PO', cwe_2='Oral', cwe_3='HL70162')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Administrar cada 12 hs con control de presion arterial.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [rxo, rxr, nte]

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
    """ Based on live/ar/ar-italica.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_CENTRAL')
        msh.sending_facility = HD(hd_1='HIBA')
        msh.receiving_application = HD(hd_1='ITALICA')
        msh.receiving_facility = HD(hd_1='HIBA')
        msh.date_time_of_message = '20260405160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB00070'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC334455', cx_4='HIBA', cx_5='MR')
        pid.patient_name = XPN(xpn_1='SUAREZ', xpn_2='ROBERTO', xpn_3='DANIEL')
        pid.date_time_of_birth = '19580322'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CIRUGIA', pl_2='HAB410', pl_3='CAMA2', pl_4='HIBA')

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
        orc.placer_order_number = EI(ei_1='SOL99200', ei_2='ITALICA')
        orc.filler_order_number = EI(ei_1='RES55700', ei_2='LAB_CENTRAL')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL99200', ei_2='ITALICA')
        obr.filler_order_number = EI(ei_1='RES55700', ei_2='LAB_CENTRAL')
        obr.universal_service_identifier = CWE(cwe_1='5902-2', cwe_2='Coagulograma', cwe_3='LN')
        obr.observation_date_time = '20260405130000'
        obr.obr_14 = 'MED700^ALVAREZ^FERNANDO^^^Dr.'
        obr.filler_field_1 = '20260405155000'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='Tiempo de protrombina', cwe_3='LN')
        obx.obx_5 = '13.5'
        obx.units = CWE(cwe_1='seg')
        obx.reference_range = '11.0-15.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx_2.obx_5 = '1.1'
        obx_2.reference_range = '0.8-1.2'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3173-2', cwe_2='KPTT', cwe_3='LN')
        obx_3.obx_5 = '32'
        obx_3.units = CWE(cwe_1='seg')
        obx_3.reference_range = '25-38'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='3255-7', cwe_2='Fibrinogeno', cwe_3='LN')
        obx_4.obx_5 = '310'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '200-400'
        obx_4.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/ar/ar-italica.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ANAT_PAT')
        msh.sending_facility = HD(hd_1='HIBA')
        msh.receiving_application = HD(hd_1='ITALICA')
        msh.receiving_facility = HD(hd_1='HIBA')
        msh.date_time_of_message = '20260406110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'AP00022'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC778901', cx_4='HIBA', cx_5='MR')
        pid.patient_name = XPN(xpn_1='MARTINEZ', xpn_2='ANA', xpn_3='BELEN')
        pid.date_time_of_birth = '19900620'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GINECO', pl_2='HAB205', pl_3='CAMA1', pl_4='HIBA')

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
        orc.placer_order_number = EI(ei_1='SOL99300', ei_2='ITALICA')
        orc.filler_order_number = EI(ei_1='AP44501', ei_2='ANAT_PAT')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL99300', ei_2='ITALICA')
        obr.filler_order_number = EI(ei_1='AP44501', ei_2='ANAT_PAT')
        obr.universal_service_identifier = CWE(cwe_1='88305', cwe_2='Biopsia de cuello uterino', cwe_3='CPT')
        obr.observation_date_time = '20260404100000'
        obr.obr_14 = 'MED600^DIAZ^ROBERTO^^^Dr.'
        obr.filler_field_1 = '20260406100000'
        obr.results_rpt_status_chng_date_time = 'AP'
        obr.charge_to_practice = MOC(moc_1='F')
        obr.transportation_mode = 'MED800^TORRES^SILVIA^^^Dra.'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='88305&IMP', cwe_2='Biopsia cervical impresion', cwe_3='CPT')
        obx.obx_5 = 'NIC I (Displasia leve). Margenes libres de lesion. Sin evidencia de invasion estromal.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Informe anatomia patologica', cwe_3='AUSPDI')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = (
            'ITALICA^AP^^Base64^'
            'JVBERi0xLjQKJeLjz9MKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0Nv'
            'dW50IDEgPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8'
            'PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAyMzQgPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoxIDAgMCAxIDcyIDcyMCBUbQooSW5m'
            'b3JtZSBkZSBBbmF0b21pYSBQYXRvbG9naWNhKSBUagowIC0yMCBUZAooUGFjaWVudGU6IE1hcnRpbmV6LCBBbmEgQmVsZW4pIFRqCjAgLTIwIFRkCihIQyA3Nzg5MDEpIFRqCjAgLTIw'
            'IFRkCihNYXRlcmlhbDogQmlvcHNpYSBkZSBjdWVsbG8gdXRlcmlubykgVGoKMCAtMjAgVGQKKERpYWdub3N0aWNvOiBOSUMgSSAtIERpc3BsYXNpYSBsZXZlKSBUagowIC0yMCBUZAoo'
            'TWFyZ2VuZXMgbGlicmVzIGRlIGxlc2lvbikgVGoKMCAtMjAgVGQKKEZpcm1hOiBEcmEuIFNpbHZpYSBUb3JyZXMgLSBBbmF0b21pYSBQYXRvbG9naWNhKSBUagpFVAplbmRzdHJlYW0K'
            'ZW5kb2JqCjUgMCBvYmoKPDwgL1R5cGUgL0ZvbnQgL1N1YnR5cGUgL1R5cGUxIC9CYXNlRm9udCAvSGVsdmV0aWNhID4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYg'
            'CjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAzMDYgMDAwMDAgbiAKMDAwMDAwMDU5MiAwMDAwMCBuIAp0cmFp'
            'bGVyCjw8IC9TaXplIDYgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4cmVmCjY3MwolJUVPRgo='
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
    """ Based on live/ar/ar-italica.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PACS_RIS')
        msh.sending_facility = HD(hd_1='HIBA')
        msh.receiving_application = HD(hd_1='ITALICA')
        msh.receiving_facility = HD(hd_1='HIBA')
        msh.date_time_of_message = '20260407140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RAD00030'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC889012', cx_4='HIBA', cx_5='MR')
        pid.patient_name = XPN(xpn_1='RUIZ', xpn_2='VALERIA', xpn_3='SOLEDAD')
        pid.date_time_of_birth = '19951108'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='ECO01', pl_4='HIBA')
        pv1.attending_doctor = XCN(xcn_1='MED900', xcn_2='LUNA', xcn_3='GABRIELA', xcn_6='Dra.')

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
        orc.placer_order_number = EI(ei_1='SOL99400', ei_2='ITALICA')
        orc.filler_order_number = EI(ei_1='INF77900', ei_2='PACS_RIS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL99400', ei_2='ITALICA')
        obr.filler_order_number = EI(ei_1='INF77900', ei_2='PACS_RIS')
        obr.universal_service_identifier = CWE(cwe_1='76856', cwe_2='Ecografia pelviana', cwe_3='CPT')
        obr.observation_date_time = '20260407130000'
        obr.obr_14 = 'MED900^LUNA^GABRIELA^^^Dra.'
        obr.filler_field_1 = '20260407135000'
        obr.results_rpt_status_chng_date_time = 'RAD'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='76856&IMP', cwe_2='Ecografia pelviana impresion', cwe_3='CPT')
        obx.obx_5 = (
            'Utero en anteversoflexion de dimensiones normales. Endometrio homogeneo de 8mm. Ovarios de tamano y ecoestructura normales. Sin liquido libr'
            'e en fondo de saco.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='Ecografia pelviana imagen', cwe_3='LOCAL')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = (
            'ITALICA^IMAGE^^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/4QBMRXhpZgAATU0AKgAAAAgAAYdpAAQAAAABAAAAGgAAAAAAA6ABAAMAAAABAAEAAKACAAQAAAABAAAAoKADAAQAAAABAAAAoAAAAAD/2wBDAAgG'
            'BgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIy'
            'MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCACgAKADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQR'
            'BRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWm'
            'p6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3'
            'AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYI4Q/SoijbHEKdTI2Mjc3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqCg4SFhoeIiYqS'
            'k5SVlpeYmZqio6SlpqeoqaqxsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4eLj5OXm5+jp6vHy8/T19vf4+fr/xAAfAAABBQEBAQ=='
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
    """ Based on live/ar/ar-italica.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ITALICA')
        msh.sending_facility = HD(hd_1='HIBA')
        msh.receiving_application = HD(hd_1='LAB_CENTRAL')
        msh.receiving_facility = HD(hd_1='HIBA')
        msh.date_time_of_message = '20260408070000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'HIBA00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='HC112233', cx_4='HIBA', cx_5='MR'), CX(cx_1='20-15678901-0', cx_4='RENAPER', cx_5='NI')]
        pid.patient_name = XPN(xpn_1='GOMEZ', xpn_2='RICARDO', xpn_3='ANDRES', xpn_5='Sr.')
        pid.date_time_of_birth = '19650715'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Bulnes 890', xad_3='Buenos Aires', xad_4='CABA', xad_5='C1176ABF', xad_6='AR')
        pid.pid_13 = '^^CP^01154321098'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSUL', pl_2='LAB01', pl_4='HIBA')
        pv1.attending_doctor = XCN(xcn_1='MED100', xcn_2='RODRIGUEZ', xcn_3='CARLOS', xcn_6='Dr.')

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
        orc.placer_order_number = EI(ei_1='SOL99500', ei_2='ITALICA')
        orc.placer_order_group_number = EI(ei_1='GRP004', ei_2='ITALICA')
        orc.date_time_of_order_event = '20260408070000'
        orc.orc_12 = 'MED100^RODRIGUEZ^CARLOS^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='SOL99500', ei_2='ITALICA')
        obr.universal_service_identifier = CWE(cwe_1='2093-3', cwe_2='Colesterol total', cwe_3='LN')
        obr.observation_date_time = '20260408070000'
        obr.obr_16 = 'MED100^RODRIGUEZ^CARLOS^^^Dr.'
        obr.obr_27 = '^RUTINA'

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
        obr_2.placer_order_number = EI(ei_1='SOL99500', ei_2='ITALICA')
        obr_2.universal_service_identifier = CWE(cwe_1='2571-8', cwe_2='Trigliceridos', cwe_3='LN')
        obr_2.observation_date_time = '20260408070000'
        obr_2.obr_16 = 'MED100^RODRIGUEZ^CARLOS^^^Dr.'
        obr_2.obr_27 = '^RUTINA'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='SOL99500', ei_2='ITALICA')
        obr_3.universal_service_identifier = CWE(cwe_1='13457-7', cwe_2='Colesterol LDL', cwe_3='LN')
        obr_3.observation_date_time = '20260408070000'
        obr_3.obr_16 = 'MED100^RODRIGUEZ^CARLOS^^^Dr.'
        obr_3.obr_27 = '^RUTINA'

        # .. build OBR ..
        obr_4 = OBR()
        obr_4.set_id_obr = '4'
        obr_4.placer_order_number = EI(ei_1='SOL99500', ei_2='ITALICA')
        obr_4.universal_service_identifier = CWE(cwe_1='2085-9', cwe_2='Colesterol HDL', cwe_3='LN')
        obr_4.observation_date_time = '20260408070000'
        obr_4.obr_16 = 'MED100^RODRIGUEZ^CARLOS^^^Dr.'
        obr_4.obr_27 = '^RUTINA'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3, obr_4]

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
    """ Based on live/ar/ar-italica.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_CENTRAL')
        msh.sending_facility = HD(hd_1='HIBA')
        msh.receiving_application = HD(hd_1='ITALICA')
        msh.receiving_facility = HD(hd_1='HIBA')
        msh.date_time_of_message = '20260315083100'
        msh.message_type = MSG(msg_1='ACK', msg_2='A01', msg_3='ACK')
        msh.message_control_id = 'ACK00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'CA'
        msa.message_control_id = 'HIBA00001'
        msa.msa_3 = ''

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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
    """ Based on live/ar/ar-italica.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ITALICA')
        msh.sending_facility = HD(hd_1='HIBA')
        msh.receiving_application = HD(hd_1='REPOSITORIO')
        msh.receiving_facility = HD(hd_1='HIBA')
        msh.date_time_of_message = '20260409100000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'HIBA00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260409100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='HC445678', cx_4='HIBA', cx_5='MR')
        pid.patient_name = XPN(xpn_1='FERNANDEZ', xpn_2='MARIA', xpn_3='INES')
        pid.date_time_of_birth = '19750412'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='HAB301', pl_3='CAMA1', pl_4='HIBA')
        pv1.attending_doctor = XCN(xcn_1='MED100', xcn_2='RODRIGUEZ', xcn_3='CARLOS', xcn_6='Dr.')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='Epicrisis', cwe_3='HL70270')
        txa.document_content_presentation = 'TX^Texto^HL70191'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20260409093000')
        txa.assigned_document_authenticator = XCN(xcn_1='MED100', xcn_2='RODRIGUEZ', xcn_3='CARLOS', xcn_6='Dr.')
        txa.placer_order_number = EI(ei_1='DOC88901')
        txa.unique_document_file_name = 'AU^Autenticado^HL70271'
        txa.document_confidentiality_status = '20260409100000'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='DS', cwe_2='Epicrisis', cwe_3='LOCAL')
        obx.obx_5 = (
            'Paciente femenina de 50 anios con diagnostico de insuficiencia cardiaca congestiva clase funcional II. Internacion por descompensacion hemod'
            'inamica. Buena respuesta al tratamiento con enalapril y furosemida. Alta con control ambulatorio en 7 dias.'
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
