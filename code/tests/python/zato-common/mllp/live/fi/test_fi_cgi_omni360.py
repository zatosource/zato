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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, EI, HD, MSG, PL, PT, VID, XAD, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA39Patient, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, \
    OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12Patient, SiuS12PersonnelResource, \
    SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIP, AIS, EVN, IN1, MRG, MSH, NK1, OBR, OBX, ORC, PID, PV1, PV2, RGS, RXO, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('fi', 'fi-cgi-omni360.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/fi/fi-cgi-omni360.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OMNI360')
        msh.sending_facility = HD(hd_1='OYS')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260509080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        msh.message_control_id = 'OMNI000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260509080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT400001', cx_4='OYS', cx_5='MR'), CX(cx_1='150178-234A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Karjalainen', xpn_2='Juha', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19780115'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kajaaninkatu 36', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^PH^0881234567~^^CP^0401234576'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='OYS', pl_2='KIR3', pl_3='Huone 201', pl_4='Vuode 1', pl_5='PPSHP')
        pv1.pv1_7 = 'DR400^Räsänen^Markku^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO400001')
        pv1.pending_location = PL(pl_1='20260509080000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Reisiluun murtuma')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='KELA')
        in1.insurance_company_id = CX(cx_1='400001')
        in1.insurance_company_name = XON(xon_1='KELA - Kansaneläkelaitos')
        in1.insurance_company_address = XAD(xad_1='Nordenskiöldinkatu 12', xad_3='Helsinki', xad_5='00250', xad_6='FIN')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
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
    """ Based on live/fi/fi-cgi-omni360.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OMNI360')
        msh.sending_facility = HD(hd_1='OYS')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260510100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02')
        msh.message_control_id = 'OMNI000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260510100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT400001', cx_4='OYS', cx_5='MR'), CX(cx_1='150178-234A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Karjalainen', xpn_2='Juha', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19780115'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kajaaninkatu 36', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^PH^0881234567~^^CP^0401234576'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='OYS', pl_2='ORT1', pl_3='Huone 315', pl_4='Vuode 2', pl_5='PPSHP')
        pv1.pv1_7 = 'DR400^Räsänen^Markku^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO400001')
        pv1.pending_location = PL(pl_1='20260509080000')

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
    """ Based on live/fi/fi-cgi-omni360.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OMNI360')
        msh.sending_facility = HD(hd_1='OYS')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260516140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03')
        msh.message_control_id = 'OMNI000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260516140000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT400001', cx_4='OYS', cx_5='MR'), CX(cx_1='150178-234A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Karjalainen', xpn_2='Juha', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19780115'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kajaaninkatu 36', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^PH^0881234567~^^CP^0401234576'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='OYS', pl_2='ORT1', pl_3='Huone 315', pl_4='Vuode 2', pl_5='PPSHP')
        pv1.pv1_7 = 'DR400^Räsänen^Markku^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO400001')
        pv1.pending_location = PL(pl_1='20260509080000')
        pv1.prior_temporary_location = PL(pl_1='20260516140000')

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
    """ Based on live/fi/fi-cgi-omni360.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OMNI360')
        msh.sending_facility = HD(hd_1='OYS')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260509091000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04')
        msh.message_control_id = 'OMNI000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260509091000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT400002', cx_4='OYS', cx_5='MR'), CX(cx_1='230590-567B', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Hämäläinen', xpn_2='Riikka', xpn_3='Johanna', xpn_5='Rouva')
        pid.date_time_of_birth = '19900523'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Isokatu 22', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^CP^0509876548'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OYS', pl_2='POLI1', pl_3='Vastaanottohuone 5', pl_5='PPSHP')
        pv1.pv1_7 = 'DR401^Kokko^Heikki^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI400001')
        pv1.pending_location = PL(pl_1='20260509091000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='OP')
        in1.insurance_company_id = CX(cx_1='400002')
        in1.insurance_company_name = XON(xon_1='OP Vakuutus')
        in1.insurance_company_address = XAD(xad_1='Gebhardinaukio 1', xad_3='Helsinki', xad_5='00510', xad_6='FIN')

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
    """ Based on live/fi/fi-cgi-omni360.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OMNI360')
        msh.sending_facility = HD(hd_1='OYS')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260509110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08')
        msh.message_control_id = 'OMNI000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260509110000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT400003', cx_4='OYS', cx_5='MR'), CX(cx_1='081255+678C', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Mäkelä', xpn_2='Eino', xpn_3='Olavi', xpn_5='Herra')
        pid.date_time_of_birth = '19550108'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Torikatu 14', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^PH^0882345678~^^CP^0407654326'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='OYS', pl_2='SIS1', pl_3='Huone 408', pl_4='Vuode 1', pl_5='PPSHP')
        pv1.pv1_7 = 'DR402^Hiltunen^Sari^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO400002')
        pv1.pending_location = PL(pl_1='20260507090000')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Mäkelä', xpn_2='Ritva')
        nk1.address = XAD(xad_3='CP', xad_4='0407654327')
        nk1.nk1_6 = 'EC'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [nk1]

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
    """ Based on live/fi/fi-cgi-omni360.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OMNI360')
        msh.sending_facility = HD(hd_1='OYS')
        msh.receiving_application = HD(hd_1='VRK')
        msh.receiving_facility = HD(hd_1='DVV')
        msh.date_time_of_message = '20260509120000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31')
        msh.message_control_id = 'OMNI000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20260509120000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT400004', cx_4='OYS', cx_5='MR'), CX(cx_1='290695-901D', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Peltola', xpn_2='Minna', xpn_3='Katriina', xpn_5='Rouva')
        pid.date_time_of_birth = '19950629'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Pakkahuoneenkatu 4', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234577'

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
    """ Based on live/fi/fi-cgi-omni360.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OMNI360')
        msh.sending_facility = HD(hd_1='OYS')
        msh.receiving_application = HD(hd_1='OYSLAB')
        msh.receiving_facility = HD(hd_1='PPSHP')
        msh.date_time_of_message = '20260509085000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'OMNI000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT400005', cx_4='OYS', cx_5='MR'), CX(cx_1='120785-123E', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Koivunen', xpn_2='Ari', xpn_3='Matti', xpn_5='Herra')
        pid.date_time_of_birth = '19850712'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hallituskatu 8', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234571'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OYS', pl_2='POLI2', pl_3='Vastaanottohuone 3', pl_5='PPSHP')
        pv1.pv1_7 = 'DR403^Savolainen^Tiina^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI400002')

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
        orc.placer_order_number = EI(ei_1='ORD400001', ei_2='OMNI360')
        orc.orc_7 = '^^^20260509085000^^R'
        orc.date_time_of_order_event = '20260509085000'
        orc.orc_10 = 'DR403^Savolainen^Tiina^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD400001', ei_2='OMNI360')
        obr.universal_service_identifier = CWE(cwe_1='2741', cwe_2='B-PVK+T', cwe_3='OYSLAB')
        obr.observation_date_time = '20260509085000'
        obr.obr_15 = 'DR403^Savolainen^Tiina^^^LL^Lääkäri'

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
        obr_2.placer_order_number = EI(ei_1='ORD400001', ei_2='OMNI360')
        obr_2.universal_service_identifier = CWE(cwe_1='4520', cwe_2='P-CRP', cwe_3='OYSLAB')
        obr_2.observation_date_time = '20260509085000'
        obr_2.obr_15 = 'DR403^Savolainen^Tiina^^^LL^Lääkäri'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='ORD400001', ei_2='OMNI360')
        obr_3.universal_service_identifier = CWE(cwe_1='4587', cwe_2='fP-Gluk', cwe_3='OYSLAB')
        obr_3.observation_date_time = '20260509085000'
        obr_3.obr_15 = 'DR403^Savolainen^Tiina^^^LL^Lääkäri'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3]

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
    """ Based on live/fi/fi-cgi-omni360.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OYSLAB')
        msh.sending_facility = HD(hd_1='PPSHP')
        msh.receiving_application = HD(hd_1='OMNI360')
        msh.receiving_facility = HD(hd_1='OYS')
        msh.date_time_of_message = '20260509140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'OYSLAB000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT400005', cx_4='OYS', cx_5='MR'), CX(cx_1='120785-123E', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Koivunen', xpn_2='Ari', xpn_3='Matti', xpn_5='Herra')
        pid.date_time_of_birth = '19850712'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hallituskatu 8', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234571'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OYS', pl_2='POLI2', pl_3='Vastaanottohuone 3', pl_5='PPSHP')
        pv1.pv1_7 = 'DR403^Savolainen^Tiina^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI400002')

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
        orc.placer_order_number = EI(ei_1='ORD400001', ei_2='OMNI360')
        orc.filler_order_number = EI(ei_1='RES400001', ei_2='OYSLAB')
        orc.orc_7 = '^^^20260509085000^^R'
        orc.date_time_of_order_event = '20260509140000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD400001', ei_2='OMNI360')
        obr.filler_order_number = EI(ei_1='RES400001', ei_2='OYSLAB')
        obr.universal_service_identifier = CWE(cwe_1='2741', cwe_2='B-PVK+T', cwe_3='OYSLAB')
        obr.observation_date_time = '20260509090000'
        obr.obr_14 = '20260509090000'
        obr.obr_15 = '^^B'
        obr.obr_16 = 'DR403^Savolainen^Tiina^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6768', cwe_2='B-Leuk', cwe_3='OYSLAB')
        obx.obx_5 = '7.5'
        obx.units = CWE(cwe_1='10E9/l')
        obx.reference_range = '3.4-8.2'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1552', cwe_2='B-Hb', cwe_3='OYSLAB')
        obx_2.obx_5 = '138'
        obx_2.units = CWE(cwe_1='g/l')
        obx_2.reference_range = '117-155'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2798', cwe_2='B-Trom', cwe_3='OYSLAB')
        obx_3.obx_5 = '230'
        obx_3.units = CWE(cwe_1='10E9/l')
        obx_3.reference_range = '150-360'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509140000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4520', cwe_2='P-CRP', cwe_3='OYSLAB')
        obx_4.obx_5 = '3'
        obx_4.units = CWE(cwe_1='mg/l')
        obx_4.reference_range = '<3'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509140000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='14879-1', cwe_2='fP-Gluk', cwe_3='LN')
        obx_5.obx_5 = '5.2'
        obx_5.units = CWE(cwe_1='mmol/l')
        obx_5.reference_range = '4.0-6.0'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509140000'

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
    """ Based on live/fi/fi-cgi-omni360.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OMNI360')
        msh.sending_facility = HD(hd_1='OYS')
        msh.receiving_application = HD(hd_1='OMNI360_SCHED')
        msh.receiving_facility = HD(hd_1='PPSHP')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12')
        msh.message_control_id = 'OMNI000008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT400001')
        sch.filler_appointment_id = EI(ei_1='APT400001')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_2='Normaali', cwe_3='HL70276')
        sch.appointment_reason = CWE(cwe_1='FIRSTVISIT', cwe_2='Ensikäynti', cwe_3='HL70277')
        sch.appointment_type = CWE(cwe_1='DOCTOR', cwe_2='Lääkärin vastaanotto')
        sch.sch_9 = '30'
        sch.appointment_duration_units = CNE(cne_1='min')
        sch.sch_11 = '^^^20260521090000^20260521093000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT400006', cx_4='OYS', cx_5='MR'), CX(cx_1='180398-345F', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Niskanen', xpn_2='Laura', xpn_3='Elina', xpn_5='Rouva')
        pid.date_time_of_birth = '19980318'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Albertinkatu 15', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234578'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OYS', pl_2='POLI3', pl_3='Vastaanottohuone 7', pl_5='PPSHP')
        pv1.pv1_7 = 'DR404^Leinonen^Juha^^^LL^Lääkäri'

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='ORTPOLI', cwe_2='Ortopedian poliklinikka', cwe_3='OMNI360')
        ais.start_date_time = '20260521090000'
        ais.start_date_time_offset = '30'
        ais.start_date_time_offset_units = CNE(cne_1='min')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.aip_3 = 'DR404^Leinonen^Juha^^^LL^Lääkäri'

        # .. build the PERSONNEL_RESOURCE group ..
        personnel_resource = SiuS12PersonnelResource()
        personnel_resource.aip = aip

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service
        resources.personnel_resource = personnel_resource

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources

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
    """ Based on live/fi/fi-cgi-omni360.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OMNI360')
        msh.sending_facility = HD(hd_1='OYS')
        msh.receiving_application = HD(hd_1='OMNI360_SCHED')
        msh.receiving_facility = HD(hd_1='PPSHP')
        msh.date_time_of_message = '20260512080000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S14')
        msh.message_control_id = 'OMNI000009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT400001')
        sch.filler_appointment_id = EI(ei_1='APT400001')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_2='Normaali', cwe_3='HL70276')
        sch.appointment_reason = CWE(cwe_1='FIRSTVISIT', cwe_2='Ensikäynti', cwe_3='HL70277')
        sch.appointment_type = CWE(cwe_1='DOCTOR', cwe_2='Lääkärin vastaanotto')
        sch.sch_9 = '30'
        sch.appointment_duration_units = CNE(cne_1='min')
        sch.sch_11 = '^^^20260523090000^20260523093000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT400006', cx_4='OYS', cx_5='MR'), CX(cx_1='180398-345F', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Niskanen', xpn_2='Laura', xpn_3='Elina', xpn_5='Rouva')
        pid.date_time_of_birth = '19980318'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Albertinkatu 15', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234578'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OYS', pl_2='POLI3', pl_3='Vastaanottohuone 7', pl_5='PPSHP')
        pv1.pv1_7 = 'DR404^Leinonen^Juha^^^LL^Lääkäri'

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='ORTPOLI', cwe_2='Ortopedian poliklinikka', cwe_3='OMNI360')
        ais.start_date_time = '20260523090000'
        ais.start_date_time_offset = '30'
        ais.start_date_time_offset_units = CNE(cne_1='min')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.aip_3 = 'DR404^Leinonen^Juha^^^LL^Lääkäri'

        # .. build the PERSONNEL_RESOURCE group ..
        personnel_resource = SiuS12PersonnelResource()
        personnel_resource.aip = aip

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service
        resources.personnel_resource = personnel_resource

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources

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
    """ Based on live/fi/fi-cgi-omni360.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OMNI360')
        msh.sending_facility = HD(hd_1='OYS')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260509150000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02')
        msh.message_control_id = 'OMNI000010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260509150000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT400007', cx_4='OYS', cx_5='MR'), CX(cx_1='050475-789G', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Lahtela', xpn_2='Raija', xpn_3='Anneli', xpn_5='Rouva')
        pid.date_time_of_birth = '19750504'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Kirkkokatu 20', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^CP^0409876549'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='OYS', pl_2='KIR3', pl_3='Huone 201', pl_4='Vuode 1', pl_5='PPSHP')
        pv1.pv1_7 = 'DR405^Keskinen^Tero^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO400003')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='OP', cwe_2='Leikkauskertomus')
        txa.document_content_presentation = 'TX'
        txa.origination_date_time = '20260509150000'
        txa.unique_document_number = EI(ei_1='DOC400001')
        txa.unique_document_file_name = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='11504-8', cwe_2='Surgical operation note', cwe_3='LN')
        obx.obx_5 = 'Reisiluun ydinnaula-ostesynteesi suoritettu. Toimenpide sujui normaalisti, vuoto vähäinen.'
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
    """ Based on live/fi/fi-cgi-omni360.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OMNI360')
        msh.sending_facility = HD(hd_1='OYS')
        msh.receiving_application = HD(hd_1='SECTRA_RIS')
        msh.receiving_facility = HD(hd_1='OYS_RAD')
        msh.date_time_of_message = '20260509103000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'OMNI000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT400008', cx_4='OYS', cx_5='MR'), CX(cx_1='091060+901H', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Vähälä', xpn_2='Erkki', xpn_3='Juhani', xpn_5='Herra')
        pid.date_time_of_birth = '19600109'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rantakatu 5', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^PH^0883456789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='OYS', pl_2='PPKL', pl_3='Triage 2', pl_5='PPSHP')
        pv1.pv1_7 = 'DR406^Tuomela^Anna^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI400003')

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
        orc.placer_order_number = EI(ei_1='ORD400002', ei_2='OMNI360')
        orc.orc_7 = '^^^20260509103000^^S'
        orc.date_time_of_order_event = '20260509103000'
        orc.orc_10 = 'DR406^Tuomela^Anna^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD400002', ei_2='OMNI360')
        obr.universal_service_identifier = CWE(cwe_1='36554-4', cwe_2='CT pää', cwe_3='RADLEX')
        obr.observation_date_time = '20260509103000'
        obr.obr_15 = 'DR406^Tuomela^Anna^^^LL^Lääkäri'
        obr.result_status = 'PÄÄNSÄRKY^Äkillinen päänsärky'

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
    """ Based on live/fi/fi-cgi-omni360.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_RIS')
        msh.sending_facility = HD(hd_1='OYS_RAD')
        msh.receiving_application = HD(hd_1='OMNI360')
        msh.receiving_facility = HD(hd_1='OYS')
        msh.date_time_of_message = '20260509160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'SECTRA000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT400008', cx_4='OYS', cx_5='MR'), CX(cx_1='091060+901H', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Vähälä', xpn_2='Erkki', xpn_3='Juhani', xpn_5='Herra')
        pid.date_time_of_birth = '19600109'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rantakatu 5', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^PH^0883456789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='OYS', pl_2='PPKL', pl_3='Triage 2', pl_5='PPSHP')
        pv1.pv1_7 = 'DR406^Tuomela^Anna^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI400003')

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
        orc.placer_order_number = EI(ei_1='ORD400002', ei_2='OMNI360')
        orc.filler_order_number = EI(ei_1='RES400002', ei_2='SECTRA_RIS')
        orc.orc_7 = '^^^20260509103000^^S'
        orc.date_time_of_order_event = '20260509160000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD400002', ei_2='OMNI360')
        obr.filler_order_number = EI(ei_1='RES400002', ei_2='SECTRA_RIS')
        obr.universal_service_identifier = CWE(cwe_1='36554-4', cwe_2='CT pää', cwe_3='RADLEX')
        obr.observation_date_time = '20260509110000'
        obr.obr_14 = '20260509110000'
        obr.obr_15 = '^^CT'
        obr.obr_16 = 'DR407^Ikonen^Reijo^^^RAD^Radiologi'
        obr.results_rpt_status_chng_date_time = '20260509160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx.obx_5 = 'Pään TT: Ei merkkejä kallonsisäisestä verenvuodosta. Verisuonirakenteet normaalit. Aivoparenkyyma normaali.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='TT-lausunto', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509160000'

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
    """ Based on live/fi/fi-cgi-omni360.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OYSLAB')
        msh.sending_facility = HD(hd_1='PPSHP')
        msh.receiving_application = HD(hd_1='OMNI360')
        msh.receiving_facility = HD(hd_1='OYS')
        msh.date_time_of_message = '20260509145000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'OYSLAB000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT400009', cx_4='OYS', cx_5='MR'), CX(cx_1='221040+234J', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Koivisto', xpn_2='Helga', xpn_3='Marjatta', xpn_5='Rouva')
        pid.date_time_of_birth = '19401022'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Kauppurienkatu 11', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^PH^0884567890'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='OYS', pl_2='SIS2', pl_3='Huone 502', pl_4='Vuode 1', pl_5='PPSHP')
        pv1.pv1_7 = 'DR408^Parviainen^Jukka^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO400004')

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
        orc.placer_order_number = EI(ei_1='ORD400003', ei_2='OMNI360')
        orc.filler_order_number = EI(ei_1='RES400003', ei_2='OYSLAB')
        orc.orc_7 = '^^^20260509080000^^R'
        orc.date_time_of_order_event = '20260509145000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD400003', ei_2='OMNI360')
        obr.filler_order_number = EI(ei_1='RES400003', ei_2='OYSLAB')
        obr.universal_service_identifier = CWE(cwe_1='2003', cwe_2='P-Krea', cwe_3='OYSLAB')
        obr.observation_date_time = '20260509082000'
        obr.obr_14 = '20260509082000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR408^Parviainen^Jukka^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509145000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2160-0', cwe_2='P-Krea', cwe_3='LN')
        obx.obx_5 = '168'
        obx.units = CWE(cwe_1='umol/l')
        obx.reference_range = '50-90'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509145000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3094-0', cwe_2='P-Urea', cwe_3='LN')
        obx_2.obx_5 = '15.2'
        obx_2.units = CWE(cwe_1='mmol/l')
        obx_2.reference_range = '2.6-6.4'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509145000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='33914-3', cwe_2='eGFR', cwe_3='LN')
        obx_3.obx_5 = '28'
        obx_3.units = CWE(cwe_1='ml/min/1.73m2')
        obx_3.reference_range = '>60'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509145000'

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
    """ Based on live/fi/fi-cgi-omni360.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OMNI360')
        msh.sending_facility = HD(hd_1='OYS')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260509130000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40')
        msh.message_control_id = 'OMNI000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260509130000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PT400010', cx_4='OYS', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Mikkola', xpn_2='Seppo', xpn_3='Kalevi', xpn_5='Herra')
        pid.date_time_of_birth = '19630412'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Uusikatu 18', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234579'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='PT400099', cx_4='OYS', cx_5='MR')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='N')

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
    """ Based on live/fi/fi-cgi-omni360.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OYSLAB')
        msh.sending_facility = HD(hd_1='PPSHP')
        msh.receiving_application = HD(hd_1='OMNI360')
        msh.receiving_facility = HD(hd_1='OYS')
        msh.date_time_of_message = '20260509153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'OYSLAB000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT400011', cx_4='OYS', cx_5='MR'), CX(cx_1='140288-567K', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Pulkkinen', xpn_2='Kati', xpn_3='Maria', xpn_5='Rouva')
        pid.date_time_of_birth = '19880214'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Asemakatu 3', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^CP^0407654328'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='OYS', pl_2='PPKL', pl_3='Triage 1', pl_5='PPSHP')
        pv1.pv1_7 = 'DR409^Karhu^Ville^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI400004')

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
        orc.placer_order_number = EI(ei_1='ORD400004', ei_2='OMNI360')
        orc.filler_order_number = EI(ei_1='RES400004', ei_2='OYSLAB')
        orc.orc_7 = '^^^20260509100000^^S'
        orc.date_time_of_order_event = '20260509153000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD400004', ei_2='OMNI360')
        obr.filler_order_number = EI(ei_1='RES400004', ei_2='OYSLAB')
        obr.universal_service_identifier = CWE(cwe_1='4520', cwe_2='P-CRP', cwe_3='OYSLAB')
        obr.observation_date_time = '20260509101000'
        obr.obr_14 = '20260509101000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR409^Karhu^Ville^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509153000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4520', cwe_2='P-CRP', cwe_3='OYSLAB')
        obx.obx_5 = '85'
        obx.units = CWE(cwe_1='mg/l')
        obx.reference_range = '<3'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509153000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1988-5', cwe_2='P-CRP-herkka', cwe_3='LN')
        obx_2.obx_5 = '85.3'
        obx_2.units = CWE(cwe_1='mg/l')
        obx_2.reference_range = '<1.0'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509153000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='26881-3', cwe_2='P-IL-6', cwe_3='LN')
        obx_3.obx_5 = '120'
        obx_3.units = CWE(cwe_1='ng/l')
        obx_3.reference_range = '<7'
        obx_3.interpretation_codes = CWE(cwe_1='HH')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509153000'

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
    """ Based on live/fi/fi-cgi-omni360.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OYSLAB')
        msh.sending_facility = HD(hd_1='PPSHP')
        msh.receiving_application = HD(hd_1='OMNI360')
        msh.receiving_facility = HD(hd_1='OYS')
        msh.date_time_of_message = '20260509155000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'OYSLAB000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT400012', cx_4='OYS', cx_5='MR'), CX(cx_1='300572-890L', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Manninen', xpn_2='Ilkka', xpn_3='Petteri', xpn_5='Herra')
        pid.date_time_of_birth = '19720530'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Linnansaari 6', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234572'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='OYS', pl_2='NEUR1', pl_3='Huone 310', pl_4='Vuode 1', pl_5='PPSHP')
        pv1.pv1_7 = 'DR410^Väisänen^Kaisa^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO400005')

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
        orc.placer_order_number = EI(ei_1='ORD400005', ei_2='OMNI360')
        orc.filler_order_number = EI(ei_1='RES400005', ei_2='OYSLAB')
        orc.orc_7 = '^^^20260509090000^^R'
        orc.date_time_of_order_event = '20260509155000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD400005', ei_2='OMNI360')
        obr.filler_order_number = EI(ei_1='RES400005', ei_2='OYSLAB')
        obr.universal_service_identifier = CWE(cwe_1='3968-5', cwe_2='S-Karbamatsepiini', cwe_3='LN')
        obr.observation_date_time = '20260509091000'
        obr.obr_14 = '20260509091000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR410^Väisänen^Kaisa^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509155000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3968-5', cwe_2='S-Karbamatsepiini', cwe_3='LN')
        obx.obx_5 = '32'
        obx.units = CWE(cwe_1='umol/l')
        obx.reference_range = '17-51'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509155000'

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
    """ Based on live/fi/fi-cgi-omni360.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OYSLAB')
        msh.sending_facility = HD(hd_1='PPSHP')
        msh.receiving_application = HD(hd_1='OMNI360')
        msh.receiving_facility = HD(hd_1='OYS')
        msh.date_time_of_message = '20260509170000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'OYSLAB000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT400013', cx_4='OYS', cx_5='MR'), CX(cx_1='050680-345M', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Korpi', xpn_2='Sanna', xpn_3='Kristiina', xpn_5='Rouva')
        pid.date_time_of_birth = '19800506'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Torikatu 30', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234580'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OYS', pl_2='PAT1', pl_3='Vastaanottohuone 1', pl_5='PPSHP')
        pv1.pv1_7 = 'DR411^Ojala^Pasi^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI400005')

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
        orc.placer_order_number = EI(ei_1='ORD400006', ei_2='OMNI360')
        orc.filler_order_number = EI(ei_1='RES400006', ei_2='OYSLAB')
        orc.orc_7 = '^^^20260507100000^^R'
        orc.date_time_of_order_event = '20260509170000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD400006', ei_2='OMNI360')
        obr.filler_order_number = EI(ei_1='RES400006', ei_2='OYSLAB')
        obr.universal_service_identifier = CWE(cwe_1='60570-9', cwe_2='Pathology report', cwe_3='LN')
        obr.observation_date_time = '20260507101000'
        obr.obr_14 = '20260507101000'
        obr.obr_15 = '^^Biopsia'
        obr.obr_16 = 'DR411^Ojala^Pasi^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509170000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='22634-0', cwe_2='Pathology report text', cwe_3='LN')
        obx.obx_5 = 'Ihomuutos: Benigni intradermaalinen nevus. Ei dysplasiaa.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509170000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Patologian lausunto', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKL01hcmtJbmZvIDw8Ci9NYXJrZWQgdHJ1ZQo+PgovTGFuZyAoZmkpCj4+CmVuZG9iagoy'
            'IDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJdCj4+CmVuZG9iagoK'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509170000'

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
    """ Based on live/fi/fi-cgi-omni360.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OMNI360')
        msh.sending_facility = HD(hd_1='OYS')
        msh.receiving_application = HD(hd_1='APTEEKKI')
        msh.receiving_facility = HD(hd_1='OYS_APT')
        msh.date_time_of_message = '20260509141000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'OMNI000013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT400014', cx_4='OYS', cx_5='MR'), CX(cx_1='200895-567N', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Leppänen', xpn_2='Mikko', xpn_3='Juhani', xpn_5='Herra')
        pid.date_time_of_birth = '19950820'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kajaanintie 45', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234581'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='OYS', pl_2='KIR3', pl_3='Huone 201', pl_4='Vuode 1', pl_5='PPSHP')
        pv1.pv1_7 = 'DR400^Räsänen^Markku^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO400006')

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
        orc.placer_order_number = EI(ei_1='ORD400007', ei_2='OMNI360')
        orc.orc_7 = '^^^20260509141000^^R'
        orc.date_time_of_order_event = '20260509141000'
        orc.orc_10 = 'DR400^Räsänen^Markku^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD400007', ei_2='OMNI360')
        obr.universal_service_identifier = CWE(cwe_1='LAAKE', cwe_2='Lääketilaus', cwe_3='OMNI360')
        obr.observation_date_time = '20260509141000'
        obr.obr_15 = 'DR400^Räsänen^Markku^^^LL^Lääkäri'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='N02BE01', cwe_2='Parasetamoli', cwe_3='ATC')
        rxo.requested_give_amount_maximum = '1000'
        rxo.requested_give_units = CWE(cwe_1='mg')
        rxo.providers_pharmacy_treatment_instructions = CWE(cwe_1='PO', cwe_2='Suun kautta', cwe_3='HL70162')
        rxo.providers_administration_instructions = CWE(cwe_4='20260509180000', cwe_6='R')
        rxo.rxo_8 = '1000'
        rxo.allow_substitutions = 'mg'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [rxo]

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
    """ Based on live/fi/fi-cgi-omni360.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='OYSLAB')
        msh.sending_facility = HD(hd_1='PPSHP')
        msh.receiving_application = HD(hd_1='OMNI360')
        msh.receiving_facility = HD(hd_1='OYS')
        msh.date_time_of_message = '20260509162000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'OYSLAB000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT400015', cx_4='OYS', cx_5='MR'), CX(cx_1='100375-234P', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Sipilä', xpn_2='Tarja', xpn_3='Marjatta', xpn_5='Rouva')
        pid.date_time_of_birth = '19750310'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Kirkkokatu 8', xad_3='Oulu', xad_5='90100', xad_6='FIN')
        pid.pid_13 = '^^CP^0407654329'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='OYS', pl_2='PPKL', pl_3='Triage 3', pl_5='PPSHP')
        pv1.pv1_7 = 'DR412^Heikkinen^Arto^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI400006')

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
        orc.placer_order_number = EI(ei_1='ORD400008', ei_2='OMNI360')
        orc.filler_order_number = EI(ei_1='RES400008', ei_2='OYSLAB')
        orc.orc_7 = '^^^20260509103000^^S'
        orc.date_time_of_order_event = '20260509162000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD400008', ei_2='OMNI360')
        obr.filler_order_number = EI(ei_1='RES400008', ei_2='OYSLAB')
        obr.universal_service_identifier = CWE(cwe_1='48066-5', cwe_2='P-FiDD', cwe_3='LN')
        obr.observation_date_time = '20260509104000'
        obr.obr_14 = '20260509104000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR412^Heikkinen^Arto^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509162000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='48066-5', cwe_2='P-FiDD', cwe_3='LN')
        obx.obx_5 = '0.45'
        obx.units = CWE(cwe_1='mg/l')
        obx.reference_range = '<0.50'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509162000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6301-6', cwe_2='P-TT-INR', cwe_3='LN')
        obx_2.obx_5 = '1.0'
        obx_2.reference_range = '0.9-1.2'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509162000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3173-2', cwe_2='P-APTT', cwe_3='LN')
        obx_3.obx_5 = '28'
        obx_3.units = CWE(cwe_1='s')
        obx_3.reference_range = '23-33'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509162000'

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
