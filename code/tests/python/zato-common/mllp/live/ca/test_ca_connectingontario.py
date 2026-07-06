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
from zato.hl7v2.v2_9.datatypes import CQ, CWE, CX, EI, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, AdtA39Patient, OruR01Observation, OruR01OrderObservation, OruR01Patient, \
    OruR01PatientResult, RspK21QueryResponse, RspK23QueryResponse
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A05, ADT_A39, ORU_R01, QBP_Q21, RSP_K21, RSP_K23
from zato.hl7v2.v2_9.segments import EVN, IN1, MRG, MSA, MSH, NK1, OBR, OBX, PID, PV1, QAK, QPD, RCP

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ca', 'ca-connectingontario.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ca/ca-connectingontario.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS')
        msh.sending_facility = HD(hd_1='ONTARIO_HIS')
        msh.receiving_application = HD(hd_1='CONNECTING_ON')
        msh.receiving_facility = HD(hd_1='EHEALTHONTARIO')
        msh.date_time_of_message = '20260301080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'OLIS00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260301080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='4521789063', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Pelletier', xpn_2='Veronique', xpn_3='Anne', xpn_5='Mme')
        pid.date_time_of_birth = '19810722'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='128 Sussex Dr', xad_3='Ottawa', xad_4='ON', xad_5='K1N 1J5', xad_6='CA')
        pid.pid_13 = '^^PH^6135552847~^^CP^6135558391'
        pid.primary_language = CWE(cwe_1='F')
        pid.marital_status = CWE(cwe_1='CAT')
        pid.pid_36 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='6WEST', pl_2='612', pl_3='A', pl_4='Ottawa General')
        pv1.attending_doctor = XCN(xcn_1='34521', xcn_2='Iyer', xcn_3='Suresh', xcn_6='Dr.', xcn_8='CPSO')
        pv1.referring_doctor = XCN(xcn_1='78234', xcn_2='Tremblay', xcn_3='Genevieve', xcn_6='Dr.', xcn_8='CPSO')
        pv1.temporary_location = PL(pl_1='MED')
        pv1.visit_number = CX(cx_1='VN20260301001')
        pv1.current_patient_balance = '20260301080000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.insurance_company_id = CX(cx_1='OHIP')
        in1.insurance_company_name = XON(xon_1='Ontario Health Insurance Plan')
        in1.insurance_company_address = XAD(xad_1="49 Place d'Armes", xad_3='Kingston', xad_4='ON', xad_5='K7L 5J2', xad_6='CA')
        in1.verification_status = '4521789063'

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
    """ Based on live/ca/ca-connectingontario.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS')
        msh.sending_facility = HD(hd_1='LHSC')
        msh.receiving_application = HD(hd_1='CONNECTING_ON')
        msh.receiving_facility = HD(hd_1='EHEALTHONTARIO')
        msh.date_time_of_message = '20260302093000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'OLIS00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260302093000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7034825619', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Cloutier', xpn_2='Benjamin', xpn_3='Francois', xpn_5='Mr')
        pid.date_time_of_birth = '19690511'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='284 King St E', xad_3='Hamilton', xad_4='ON', xad_5='L8N 1B6', xad_6='CA')
        pid.pid_13 = '^^PH^9055552314~^^CP^9055557762'
        pid.primary_language = CWE(cwe_1='M')
        pid.marital_status = CWE(cwe_1='PRO')
        pid.pid_36 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_2='RM3', pl_3='1', pl_4='Victoria Hospital')
        pv1.attending_doctor = XCN(xcn_1='45612', xcn_2='Kaur', xcn_3='Manpreet', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='GEN')
        pv1.patient_type = CWE(cwe_1='VN20260302001')
        pv1.discharge_date_time = '20260302093000'

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/ca/ca-connectingontario.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CHRIS')
        msh.sending_facility = HD(hd_1='MOHLTC')
        msh.receiving_application = HD(hd_1='CONNECTING_ON')
        msh.receiving_facility = HD(hd_1='EHEALTHONTARIO')
        msh.date_time_of_message = '20260303140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'CHRIS00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260303140000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='8923471056', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Wong', xpn_2='Stephanie', xpn_3='Yi-Chen', xpn_5='Ms')
        pid.date_time_of_birth = '19920418'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='162 Bay St', xad_3='Toronto', xad_4='ON', xad_5='M5J 2T3', xad_6='CA')
        pid.pid_13 = '^^PH^4165553967~^^CP^4165558821~^^Internet^stephanie.wong@webmail.ca'
        pid.primary_language = CWE(cwe_1='F')
        pid.marital_status = CWE(cwe_1='CAT')
        pid.pid_36 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='7NORTH', pl_2='712', pl_3='B', pl_4='Toronto General')
        pv1.attending_doctor = XCN(xcn_1='56712', xcn_2='Adeyemi', xcn_3='Tunde', xcn_6='Dr.', xcn_8='CPSO')
        pv1.referring_doctor = XCN(xcn_1='78934', xcn_2='Lebrun', xcn_3='Jean-Marc', xcn_6='Dr.', xcn_8='CPSO')
        pv1.temporary_location = PL(pl_1='CARD')
        pv1.visit_number = CX(cx_1='VN20260303001')
        pv1.current_patient_balance = '20260303140000'

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
    """ Based on live/ca/ca-connectingontario.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OCULYS')
        msh.sending_facility = HD(hd_1='LHIN_CENTRAL')
        msh.receiving_application = HD(hd_1='CONNECTING_ON')
        msh.receiving_facility = HD(hd_1='EHEALTHONTARIO')
        msh.date_time_of_message = '20260304110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'OCUL00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20260304110000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1287094563', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Nguyen', xpn_2='Bao', xpn_3='Tran', xpn_5='Ms')
        pid.date_time_of_birth = '19880229'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='517 Dundas St', xad_3='London', xad_4='ON', xad_5='N6B 1W4', xad_6='CA')
        pid.pid_13 = '^^PH^5195554683~^^CP^5195557291'
        pid.primary_language = CWE(cwe_1='F')
        pid.marital_status = CWE(cwe_1='BUD')
        pid.pid_36 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='EMERG', pl_2='RM1', pl_3='1', pl_4='London Health Sciences')
        pv1.attending_doctor = XCN(xcn_1='90234', xcn_2='Krishnan', xcn_3='Deepa', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='EMER')
        pv1.patient_type = CWE(cwe_1='VN20260304001')
        pv1.discharge_date_time = '20260304110000'

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
    """ Based on live/ca/ca-connectingontario.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS')
        msh.sending_facility = HD(hd_1='ONTARIO_HIS')
        msh.receiving_application = HD(hd_1='CONNECTING_ON')
        msh.receiving_facility = HD(hd_1='EHEALTHONTARIO')
        msh.date_time_of_message = '20260305160000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'OLIS00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260305160000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3678125409', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Bergeron', xpn_2='Sebastien', xpn_3='Olivier', xpn_5='Mr')
        pid.date_time_of_birth = '19741203'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='91 Sparks St', xad_3='Ottawa', xad_4='ON', xad_5='K1P 5B5', xad_6='CA')
        pid.pid_13 = '^^PH^6135554729~^^CP^6135557815'
        pid.primary_language = CWE(cwe_1='M')
        pid.marital_status = CWE(cwe_1='CAT')
        pid.pid_36 = ''

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='7821456390', cx_4='ON_HCN', cx_5='JHN')
        mrg.mrg_7 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='5WEST', pl_2='503', pl_3='A', pl_4='The Ottawa Hospital')
        pv1.attending_doctor = XCN(xcn_1='23145', xcn_2='Choi', xcn_3='Min-Jun', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='SURG')
        pv1.patient_type = CWE(cwe_1='VN20260305001')
        pv1.discharge_date_time = '20260305160000'

        # .. build the PATIENT group ..
        patient = AdtA39Patient()
        patient.pid = pid
        patient.mrg = mrg
        patient.pv1 = pv1

        # .. assemble the full message ..
        msg = ADT_A39()
        msg.msh = msh
        msg.evn = evn
        msg.patient = patient

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
    """ Based on live/ca/ca-connectingontario.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CONNECTING_ON')
        msh.sending_facility = HD(hd_1='EHEALTHONTARIO')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ONTARIO_HIS')
        msh.date_time_of_message = '20260306090000'
        msh.message_type = MSG(msg_1='QBP', msg_2='Q22', msg_3='QBP_Q21')
        msh.message_control_id = 'CONN00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build QPD ..
        qpd = QPD()
        qpd.message_query_name = CWE(cwe_1='Q22', cwe_2='FindCandidates', cwe_3='HL7nnnn')
        qpd.query_tag = 'Q0001'
        qpd.qpd_3 = '@PID.3.1^9145206378~@PID.3.4^ON_HCN~@PID.3.5^JHN'

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
    """ Based on live/ca/ca-connectingontario.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS')
        msh.sending_facility = HD(hd_1='ONTARIO_HIS')
        msh.receiving_application = HD(hd_1='CONNECTING_ON')
        msh.receiving_facility = HD(hd_1='EHEALTHONTARIO')
        msh.date_time_of_message = '20260306090001'
        msh.message_type = MSG(msg_1='RSP', msg_2='K22', msg_3='RSP_K21')
        msh.message_control_id = 'OLIS00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'CONN00001'

        # .. build QAK ..
        qak = QAK()
        qak.query_tag = 'Q0001'
        qak.query_response_status = 'OK'
        qak.message_query_name = CWE(cwe_1='Q22', cwe_2='FindCandidates', cwe_3='HL7nnnn')
        qak.hit_count_total = '1'

        # .. build QPD ..
        qpd = QPD()
        qpd.message_query_name = CWE(cwe_1='Q22', cwe_2='FindCandidates', cwe_3='HL7nnnn')
        qpd.query_tag = 'Q0001'
        qpd.qpd_3 = '@PID.3.1^9145206378~@PID.3.4^ON_HCN~@PID.3.5^JHN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='9145206378', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Fortin', xpn_2='Maxime', xpn_3='Etienne', xpn_5='Mr')
        pid.date_time_of_birth = '19830209'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='45 Elgin St', xad_3='Ottawa', xad_4='ON', xad_5='K1P 5K8', xad_6='CA')
        pid.pid_13 = '^^PH^6135556124~^^CP^6135559337'
        pid.primary_language = CWE(cwe_1='M')
        pid.marital_status = CWE(cwe_1='CAT')
        pid.pid_36 = ''

        # .. build the QUERY_RESPONSE group ..
        query_response = RspK21QueryResponse()
        query_response.pid = pid

        # .. assemble the full message ..
        msg = RSP_K21()
        msg.msh = msh
        msg.msa = msa
        msg.qak = qak
        msg.qpd = qpd
        msg.query_response = query_response

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
    """ Based on live/ca/ca-connectingontario.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CONNECTING_ON')
        msh.sending_facility = HD(hd_1='EHEALTHONTARIO')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ONTARIO_HIS')
        msh.date_time_of_message = '20260307100000'
        msh.message_type = MSG(msg_1='QBP', msg_2='Q23', msg_3='QBP_Q21')
        msh.message_control_id = 'CONN00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build QPD ..
        qpd = QPD()
        qpd.message_query_name = CWE(cwe_1='IHE PIX Query')
        qpd.query_tag = 'Q0002'
        qpd.qpd_3 = '9145206378^^^ON_HCN^JHN'
        qpd.qpd_4 = '^^^OLIS_MRN~^^^CHRIS_ID'

        # .. build RCP ..
        rcp = RCP()
        rcp.query_priority = 'I'

        # .. assemble the full message ..
        msg = QBP_Q21()
        msg.msh = msh
        msg.qpd = qpd
        msg.rcp = rcp

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
    """ Based on live/ca/ca-connectingontario.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS')
        msh.sending_facility = HD(hd_1='ONTARIO_HIS')
        msh.receiving_application = HD(hd_1='CONNECTING_ON')
        msh.receiving_facility = HD(hd_1='EHEALTHONTARIO')
        msh.date_time_of_message = '20260307100001'
        msh.message_type = MSG(msg_1='RSP', msg_2='K23', msg_3='RSP_K23')
        msh.message_control_id = 'OLIS00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'CONN00002'

        # .. build QAK ..
        qak = QAK()
        qak.query_tag = 'Q0002'
        qak.query_response_status = 'OK'
        qak.message_query_name = CWE(cwe_1='IHE PIX Query')

        # .. build QPD ..
        qpd = QPD()
        qpd.message_query_name = CWE(cwe_1='IHE PIX Query')
        qpd.query_tag = 'Q0002'
        qpd.qpd_3 = '9145206378^^^ON_HCN^JHN'
        qpd.qpd_4 = '^^^OLIS_MRN~^^^CHRIS_ID'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [
            CX(cx_1='MRN673829', cx_4='OLIS_MRN', cx_5='MR'),
            CX(cx_1='CHR184562', cx_4='CHRIS_ID', cx_5='PI'),
            CX(cx_1='9145206378', cx_4='ON_HCN', cx_5='JHN'),
        ]
        pid.patient_name = XPN(xpn_1='Fortin', xpn_2='Maxime', xpn_3='Etienne', xpn_5='Mr')
        pid.date_time_of_birth = '19830209'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build the QUERY_RESPONSE group ..
        query_response = RspK23QueryResponse()
        query_response.pid = pid

        # .. assemble the full message ..
        msg = RSP_K23()
        msg.msh = msh
        msg.msa = msa
        msg.qak = qak
        msg.qpd = qpd
        msg.query_response = query_response

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
    """ Based on live/ca/ca-connectingontario.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OCULYS')
        msh.sending_facility = HD(hd_1='SUNNYBROOK')
        msh.receiving_application = HD(hd_1='CONNECTING_ON')
        msh.receiving_facility = HD(hd_1='EHEALTHONTARIO')
        msh.date_time_of_message = '20260308034500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'OCUL00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260308034500'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='5286913074', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Patel', xpn_2='Anjali', xpn_3='Rohini', xpn_5='Ms')
        pid.date_time_of_birth = '19960615'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='487 Bloor St W', xad_3='Toronto', xad_4='ON', xad_5='M5S 1Y1', xad_6='CA')
        pid.pid_13 = '^^PH^4165557823~^^CP^4165552169'
        pid.primary_language = CWE(cwe_1='F')
        pid.marital_status = CWE(cwe_1='CAT')
        pid.pid_36 = ''

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Patel', xpn_2='Vikram', xpn_4='Mr')
        nk1.relationship = CWE(cwe_1='FTH')
        nk1.address = XAD(xad_1='487 Bloor St W', xad_3='Toronto', xad_4='ON', xad_5='M5S 1Y1', xad_6='CA')
        nk1.nk1_5 = '^^PH^4165557824'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='EMERG', pl_2='BAY7', pl_3='1', pl_4='Sunnybrook HSC')
        pv1.attending_doctor = XCN(xcn_1='34678', xcn_2='Boucher', xcn_3='Mathieu', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='EMER')
        pv1.patient_type = CWE(cwe_1='VN20260308001')
        pv1.discharge_date_time = '20260308034500'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.insurance_company_id = CX(cx_1='OHIP')
        in1.insurance_company_name = XON(xon_1='Ontario Health Insurance Plan')
        in1.insurance_company_address = XAD(xad_1="49 Place d'Armes", xad_3='Kingston', xad_4='ON', xad_5='K7L 5J2', xad_6='CA')
        in1.verification_status = '5286913074'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

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
    """ Based on live/ca/ca-connectingontario.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS')
        msh.sending_facility = HD(hd_1='HAMILTON_GEN')
        msh.receiving_application = HD(hd_1='CONNECTING_ON')
        msh.receiving_facility = HD(hd_1='EHEALTHONTARIO')
        msh.date_time_of_message = '20260309071500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'OLIS00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260309071500'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='6491738025', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Caron', xpn_2='Olivier', xpn_3='Daniel', xpn_5='Mr')
        pid.date_time_of_birth = '19840928'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='275 Main St E', xad_3='Hamilton', xad_4='ON', xad_5='L8N 1H6', xad_6='CA')
        pid.pid_13 = '^^PH^9055554912~^^CP^9055557368'
        pid.primary_language = CWE(cwe_1='M')
        pid.marital_status = CWE(cwe_1='CAT')
        pid.pid_36 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ORTHO', pl_2='301', pl_3='A', pl_4='Hamilton General')
        pv1.attending_doctor = XCN(xcn_1='78145', xcn_2='Beaulieu', xcn_3='Stephanie', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='ORTH')
        pv1.patient_type = CWE(cwe_1='VN20260309001')
        pv1.discharge_date_time = '20260309071500'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.insurance_company_id = CX(cx_1='WSIB')
        in1.insurance_company_name = XON(xon_1='Workplace Safety and Insurance Board')
        in1.insurance_company_address = XAD(xad_1='200 Front St W', xad_3='Toronto', xad_4='ON', xad_5='M5V 3J1', xad_6='CA')
        in1.in1_47 = ''

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. build IN1 ..
        in1_2 = IN1()
        in1_2.set_id_in1 = '2'
        in1_2.insurance_company_id = CX(cx_1='OHIP')
        in1_2.insurance_company_name = XON(xon_1='Ontario Health Insurance Plan')
        in1_2.insurance_company_address = XAD(xad_1="49 Place d'Armes", xad_3='Kingston', xad_4='ON', xad_5='K7L 5J2', xad_6='CA')
        in1_2.verification_status = '6491738025'

        # .. build the INSURANCE group ..
        insurance_2 = AdtA01Insurance()
        insurance_2.in1 = in1_2

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.insurance = [insurance, insurance_2]

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
    """ Based on live/ca/ca-connectingontario.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS')
        msh.sending_facility = HD(hd_1='GAMMA_DYNACARE')
        msh.receiving_application = HD(hd_1='CONNECTING_ON')
        msh.receiving_facility = HD(hd_1='EHEALTHONTARIO')
        msh.date_time_of_message = '20260310143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OLIS00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2917346058', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lavoie', xpn_2='Stephanie', xpn_3='Marie', xpn_5='Mme')
        pid.date_time_of_birth = '19710314'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='156 Bank St', xad_3='Ottawa', xad_4='ON', xad_5='K1P 6E5', xad_6='CA')
        pid.pid_13 = '^^PH^6135558143'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260310001', ei_2='OLIS')
        obr.filler_order_number = EI(ei_1='SPE20260310001', ei_2='GAMMA_DYNACARE')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Complete Blood Count', cwe_3='OLIS_CODE')
        obr.observation_date_time = '20260310081500'
        obr.obr_16 = '2917346058^Lavoie^Stephanie M^^^^'
        obr.results_rpt_status_chng_date_time = '20260310143000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='WBC', cwe_3='LN')
        obx.obx_5 = '8.2'
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
        obx_2.obx_5 = '4.65'
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
        obx_3.obx_5 = '138'
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
        obx_4.obx_5 = '0.41'
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
        obx_5.obx_5 = '256'
        obx_5.units = CWE(cwe_1='x10*9/L')
        obx_5.reference_range = '150-400'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

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
    """ Based on live/ca/ca-connectingontario.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS')
        msh.sending_facility = HD(hd_1='LIFELABS')
        msh.receiving_application = HD(hd_1='CONNECTING_ON')
        msh.receiving_facility = HD(hd_1='EHEALTHONTARIO')
        msh.date_time_of_message = '20260311101500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OLIS00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='4738261905', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Simard', xpn_2='Robert', xpn_3='Marcel', xpn_5='Mr')
        pid.date_time_of_birth = '19520809'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='342 Laurier Ave W', xad_3='Ottawa', xad_4='ON', xad_5='K1P 1K6', xad_6='CA')
        pid.pid_13 = '^^PH^6135559267'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260311001', ei_2='OLIS')
        obr.filler_order_number = EI(ei_1='SPE20260311001', ei_2='LIFELABS')
        obr.universal_service_identifier = CWE(cwe_1='BMP', cwe_2='Basic Metabolic Panel', cwe_3='OLIS_CODE')
        obr.observation_date_time = '20260311074500'
        obr.obr_16 = '4738261905^Simard^Robert M^^^^'
        obr.results_rpt_status_chng_date_time = '20260311101500'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose', cwe_3='LN')
        obx.obx_5 = '9.8'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.3-5.5'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine', cwe_3='LN')
        obx_2.obx_5 = '145'
        obx_2.units = CWE(cwe_1='umol/L')
        obx_2.reference_range = '62-115'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea', cwe_3='LN')
        obx_3.obx_5 = '12.5'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '2.1-8.5'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodium', cwe_3='LN')
        obx_4.obx_5 = '140'
        obx_4.units = CWE(cwe_1='mmol/L')
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
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium', cwe_3='LN')
        obx_5.obx_5 = '4.8'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '3.5-5.1'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2075-0', cwe_2='Chloride', cwe_3='LN')
        obx_6.obx_5 = '102'
        obx_6.units = CWE(cwe_1='mmol/L')
        obx_6.reference_range = '98-106'
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
    """ Based on live/ca/ca-connectingontario.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS')
        msh.sending_facility = HD(hd_1='MOUNT_SINAI_PATH')
        msh.receiving_application = HD(hd_1='CONNECTING_ON')
        msh.receiving_facility = HD(hd_1='EHEALTHONTARIO')
        msh.date_time_of_message = '20260312153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OLIS00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='8159427063', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Paquette', xpn_2='Sylvie', xpn_3='Anne', xpn_5='Mme')
        pid.date_time_of_birth = '19770502'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='219 College St', xad_3='Toronto', xad_4='ON', xad_5='M5T 1R3', xad_6='CA')
        pid.pid_13 = '^^PH^4165554328'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260312001', ei_2='OLIS')
        obr.filler_order_number = EI(ei_1='SPE20260312001', ei_2='MSH_PATH')
        obr.universal_service_identifier = CWE(cwe_1='PATH', cwe_2='Surgical Pathology', cwe_3='OLIS_CODE')
        obr.observation_date_time = '20260312090000'
        obr.obr_16 = '8159427063^Paquette^Sylvie A^^^^'
        obr.results_rpt_status_chng_date_time = '20260312153000'
        obr.diagnostic_serv_sect_id = 'PATH'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='22637-3', cwe_2='Pathology Report', cwe_3='LN')
        obx.obx_5 = 'Right breast excisional biopsy: Invasive ductal carcinoma, Grade 2, 1.8 cm. Margins clear. ER positive, PR positive, HER2 negative.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Pathology Report PDF', cwe_3='LN')
        obx_2.obx_5 = (
            '^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2Jq'
        )
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
    """ Based on live/ca/ca-connectingontario.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS')
        msh.sending_facility = HD(hd_1='KINGSTON_RAD')
        msh.receiving_application = HD(hd_1='CONNECTING_ON')
        msh.receiving_facility = HD(hd_1='EHEALTHONTARIO')
        msh.date_time_of_message = '20260313091000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OLIS00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='7264193058', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Ouellet', xpn_2='Antoine', xpn_3='Joseph', xpn_5='Mr')
        pid.date_time_of_birth = '19580427'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='316 Princess St', xad_3='Kingston', xad_4='ON', xad_5='K7L 1B7', xad_6='CA')
        pid.pid_13 = '^^PH^6135554912'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260313001', ei_2='OLIS')
        obr.filler_order_number = EI(ei_1='SPE20260313001', ei_2='KGH_RAD')
        obr.universal_service_identifier = CWE(cwe_1='XCHEST', cwe_2='Chest Xray', cwe_3='OLIS_CODE')
        obr.observation_date_time = '20260313083000'
        obr.obr_16 = '7264193058^Ouellet^Antoine J^^^^'
        obr.results_rpt_status_chng_date_time = '20260313091000'
        obr.diagnostic_serv_sect_id = 'RAD'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic Imaging Report', cwe_3='LN')
        obx.obx_5 = (
            'PA and lateral views of the chest. Heart size is normal. Lungs are clear. No pleural effusion or pneumothorax identified. Costophrenic angle'
            's are sharp bilaterally.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='IMG', cwe_2='Chest Xray Image', cwe_3='LN')
        obx_2.obx_5 = (
            '^IM^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgy'
            'IRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL'
        )
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
    """ Based on live/ca/ca-connectingontario.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CHRIS')
        msh.sending_facility = HD(hd_1='HSN_SUDBURY')
        msh.receiving_application = HD(hd_1='CONNECTING_ON')
        msh.receiving_facility = HD(hd_1='EHEALTHONTARIO')
        msh.date_time_of_message = '20260314062000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'CHRIS00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260314062000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3815647092', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Gagne', xpn_2='Mathieu', xpn_3='Gilles', xpn_5='Mr')
        pid.date_time_of_birth = '19610819'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='87 Elm St W', xad_3='Sudbury', xad_4='ON', xad_5='P3C 1S5', xad_6='CA')
        pid.pid_13 = '^^PH^7055552981~^^CP^7055557413'
        pid.primary_language = CWE(cwe_1='M')
        pid.marital_status = CWE(cwe_1='CAT')
        pid.pid_36 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='101', pl_3='A', pl_4='Health Sciences North')
        pv1.attending_doctor = XCN(xcn_1='56218', xcn_2='Lapointe', xcn_3='Christine', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='IMED')
        pv1.patient_type = CWE(cwe_1='VN20260314001')
        pv1.discharge_date_time = '20260314062000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.insurance_company_id = CX(cx_1='OHIP')
        in1.insurance_company_name = XON(xon_1='Ontario Health Insurance Plan')
        in1.insurance_company_address = XAD(xad_1="49 Place d'Armes", xad_3='Kingston', xad_4='ON', xad_5='K7L 5J2', xad_6='CA')
        in1.verification_status = '3815647092'

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
    """ Based on live/ca/ca-connectingontario.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS')
        msh.sending_facility = HD(hd_1='CHEO')
        msh.receiving_application = HD(hd_1='CONNECTING_ON')
        msh.receiving_facility = HD(hd_1='EHEALTHONTARIO')
        msh.date_time_of_message = '20260315100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'OLIS00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260315100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='5147209638', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Leclerc', xpn_2='Charlotte', xpn_3='Eve', xpn_5='Ms')
        pid.date_time_of_birth = '20190724'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='168 Metcalfe St', xad_3='Ottawa', xad_4='ON', xad_5='K2P 1M9', xad_6='CA')
        pid.pid_13 = '^^PH^6135559263'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Leclerc', xpn_2='Sebastien', xpn_4='Mr')
        nk1.relationship = CWE(cwe_1='FTH')
        nk1.address = XAD(xad_1='168 Metcalfe St', xad_3='Ottawa', xad_4='ON', xad_5='K2P 1M9', xad_6='CA')
        nk1.nk1_5 = '^^PH^6135559264~^^CP^6135552176'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build NK1 ..
        nk1_2 = NK1()
        nk1_2.set_id_nk1 = '2'
        nk1_2.name = XPN(xpn_1='Leclerc', xpn_2='Marie-Eve', xpn_4='Mme')
        nk1_2.relationship = CWE(cwe_1='MTH')
        nk1_2.address = XAD(xad_1='168 Metcalfe St', xad_3='Ottawa', xad_4='ON', xad_5='K2P 1M9', xad_6='CA')
        nk1_2.nk1_5 = '^^PH^6135559265~^^CP^6135552177'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin_2 = AdtA01NextOfKin()
        next_of_kin_2.nk1 = nk1_2

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PEDS', pl_2='RM5', pl_3='1', pl_4='CHEO')
        pv1.attending_doctor = XCN(xcn_1='72845', xcn_2='Sharma', xcn_3='Neha', xcn_6='Dr.', xcn_8='CPSO')
        pv1.hospital_service = CWE(cwe_1='PEDS')
        pv1.patient_type = CWE(cwe_1='VN20260315001')
        pv1.discharge_date_time = '20260315100000'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = [next_of_kin, next_of_kin_2]
        msg.pv1 = pv1

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
    """ Based on live/ca/ca-connectingontario.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS')
        msh.sending_facility = HD(hd_1='ALPHA_LABS')
        msh.receiving_application = HD(hd_1='CONNECTING_ON')
        msh.receiving_facility = HD(hd_1='EHEALTHONTARIO')
        msh.date_time_of_message = '20260316164500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OLIS00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='9028453617', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Girard', xpn_2='Andre', xpn_3='Pierre', xpn_5='Mr')
        pid.date_time_of_birth = '19481117'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='74 Wellington St', xad_3='Ottawa', xad_4='ON', xad_5='K1A 0B5', xad_6='CA')
        pid.pid_13 = '^^PH^6135558149'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260316001', ei_2='OLIS')
        obr.filler_order_number = EI(ei_1='SPE20260316001', ei_2='ALPHA_LABS')
        obr.universal_service_identifier = CWE(cwe_1='UCUL', cwe_2='Urine Culture', cwe_3='OLIS_CODE')
        obr.observation_date_time = '20260316081000'
        obr.obr_16 = '9028453617^Girard^Andre P^^^^'
        obr.results_rpt_status_chng_date_time = '20260316164500'
        obr.diagnostic_serv_sect_id = 'MB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='630-4', cwe_2='Bacteria identified', cwe_3='LN')
        obx.obx_5 = 'Escherichia coli'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18900-1', cwe_2='Colony count', cwe_3='LN')
        obx_2.obx_5 = '>100,000 CFU/mL'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18864-9', cwe_2='Ampicillin', cwe_3='LN')
        obx_3.obx_5 = 'Resistant'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18865-6', cwe_2='Ciprofloxacin', cwe_3='LN')
        obx_4.obx_5 = 'Susceptible'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18866-4', cwe_2='Nitrofurantoin', cwe_3='LN')
        obx_5.obx_5 = 'Susceptible'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='18867-2', cwe_2='Trimethoprim-Sulfamethoxazole', cwe_3='LN')
        obx_6.obx_5 = 'Resistant'
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
    """ Based on live/ca/ca-connectingontario.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OLIS')
        msh.sending_facility = HD(hd_1='DYNACARE')
        msh.receiving_application = HD(hd_1='CONNECTING_ON')
        msh.receiving_facility = HD(hd_1='EHEALTHONTARIO')
        msh.date_time_of_message = '20260317112000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'OLIS00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='4892573160', cx_4='ON_HCN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Chen', xpn_2='Lillian', xpn_3='Mei-Hua', xpn_5='Ms')
        pid.date_time_of_birth = '19900318'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='387 Bay St', xad_3='Toronto', xad_4='ON', xad_5='M5J 2N4', xad_6='CA')
        pid.pid_13 = '^^PH^4165553819'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260317001', ei_2='OLIS')
        obr.filler_order_number = EI(ei_1='SPE20260317001', ei_2='DYNACARE')
        obr.universal_service_identifier = CWE(cwe_1='TSH', cwe_2='Thyroid Stimulating Hormone', cwe_3='OLIS_CODE')
        obr.observation_date_time = '20260317080000'
        obr.obr_16 = '4892573160^Chen^Lillian M^^^^'
        obr.results_rpt_status_chng_date_time = '20260317112000'
        obr.diagnostic_serv_sect_id = 'LAB'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='TSH', cwe_3='LN')
        obx.obx_5 = '2.45'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.35-5.50'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3026-2', cwe_2='Free T4', cwe_3='LN')
        obx_2.obx_5 = '14.2'
        obx_2.units = CWE(cwe_1='pmol/L')
        obx_2.reference_range = '10.0-25.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ED'
        obx_3.observation_identifier = CWE(cwe_1='REQ', cwe_2='Scanned Requisition', cwe_3='LN')
        obx_3.obx_5 = (
            '^AP^^Base64^'
            'JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKL01hcmtJbmZvIDw8IC9NYXJrZWQgdHJ1ZSA+PgovU3RydWN0VHJlZVJvb3QgMyAwIFIK'
            'Pj4KZW5kb2Jq'
        )
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
    """ Based on live/ca/ca-connectingontario.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CONNECTING_ON')
        msh.sending_facility = HD(hd_1='EHEALTHONTARIO')
        msh.receiving_application = HD(hd_1='OLIS')
        msh.receiving_facility = HD(hd_1='ONTARIO_HIS')
        msh.date_time_of_message = '20260318150000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'CONN00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260318150000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [
            CX(cx_1='6273918045', cx_4='ON_HCN', cx_5='JHN'),
            CX(cx_1='MRN912348', cx_4='LHSC_MRN', cx_5='MR'),
            CX(cx_1='CHR384917', cx_4='CHRIS_ID', cx_5='PI'),
        ]
        pid.patient_name = XPN(xpn_1='Singh', xpn_2='Harjinder', xpn_3='Pal', xpn_5='Mr')
        pid.date_time_of_birth = '19751024'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='432 University Ave', xad_3='Toronto', xad_4='ON', xad_5='M5G 1W3', xad_6='CA')
        pid.pid_13 = '^^PH^4165556824~^^CP^4165553918~^^Internet^harjinder.singh@webmail.ca'
        pid.primary_language = CWE(cwe_1='M')
        pid.marital_status = CWE(cwe_1='CAT')
        pid.pid_36 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='6SOUTH', pl_2='610', pl_3='A', pl_4='UHN - Toronto General')
        pv1.attending_doctor = XCN(xcn_1='34528', xcn_2='Iyer', xcn_3='Kavita', xcn_6='Dr.', xcn_8='CPSO')
        pv1.referring_doctor = XCN(xcn_1='56739', xcn_2='Roy', xcn_3='Stephanie', xcn_6='Dr.', xcn_8='CPSO')
        pv1.temporary_location = PL(pl_1='NEPH')
        pv1.visit_number = CX(cx_1='VN20260318001')
        pv1.current_patient_balance = '20260318150000'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
