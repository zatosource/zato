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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, EI, HD, MSG, OG, PL, PT, VID, XAD, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA39Patient, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, \
    OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12Patient, SiuS12PersonnelResource, \
    SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIP, AIS, EVN, IN1, MRG, MSH, NK1, OBR, OBX, ORC, PID, PV1, PV2, RGS, RXO, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('fi', 'fi-apotti.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/fi/fi-apotti.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APOTTI')
        msh.sending_facility = HD(hd_1='HUS_HELSINKI')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260509083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'APOTTI000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260509083000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PT100001', cx_4='HUS', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Virtanen', xpn_2='Matti', xpn_3='Johannes', xpn_5='Herra')
        pid.date_time_of_birth = '19780315'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Mannerheimintie 42', xad_3='Helsinki', xad_5='00100', xad_6='FIN')
        pid.pid_13 = '^^PH^0912345678~^^CP^0401234567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MEIL', pl_2='OS10', pl_3='Huone 401', pl_4='Vuode 1', pl_5='HUS')
        pv1.pv1_7 = 'DR100^Korhonen^Päivi^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO100001')
        pv1.pending_location = PL(pl_1='20260509083000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Lonkkamurtuma, vasen')
        pv2.previous_treatment_date = 'A'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='KELA')
        in1.insurance_company_id = CX(cx_1='100001')
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
    """ Based on live/fi/fi-apotti.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APOTTI')
        msh.sending_facility = HD(hd_1='HUS_HELSINKI')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260510091500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'APOTTI000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260510091500'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PT100001', cx_4='HUS', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Virtanen', xpn_2='Matti', xpn_3='Johannes', xpn_5='Herra')
        pid.date_time_of_birth = '19780315'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Mannerheimintie 42', xad_3='Helsinki', xad_5='00100', xad_6='FIN')
        pid.pid_13 = '^^PH^0912345678~^^CP^0401234567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MEIL', pl_2='KIR3', pl_3='Huone 205', pl_4='Vuode 2', pl_5='HUS')
        pv1.pv1_7 = 'DR100^Korhonen^Päivi^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO100001')
        pv1.pending_location = PL(pl_1='20260509083000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Lonkkamurtuma, vasen')

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
    """ Based on live/fi/fi-apotti.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APOTTI')
        msh.sending_facility = HD(hd_1='HUS_HELSINKI')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260515140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'APOTTI000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260515140000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PT100001', cx_4='HUS', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Virtanen', xpn_2='Matti', xpn_3='Johannes', xpn_5='Herra')
        pid.date_time_of_birth = '19780315'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Mannerheimintie 42', xad_3='Helsinki', xad_5='00100', xad_6='FIN')
        pid.pid_13 = '^^PH^0912345678~^^CP^0401234567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MEIL', pl_2='KIR3', pl_3='Huone 205', pl_4='Vuode 2', pl_5='HUS')
        pv1.pv1_7 = 'DR100^Korhonen^Päivi^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO100001')
        pv1.pending_location = PL(pl_1='20260509083000')
        pv1.prior_temporary_location = PL(pl_1='20260515140000')

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
    """ Based on live/fi/fi-apotti.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APOTTI')
        msh.sending_facility = HD(hd_1='HUS_JORVI')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'APOTTI000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260509100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PT200002', cx_4='HUS', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Nieminen', xpn_2='Anna', xpn_3='Kristiina', xpn_5='Rouva')
        pid.date_time_of_birth = '19850622'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Leppävaarankatu 15', xad_3='Espoo', xad_5='02600', xad_6='FIN')
        pid.pid_13 = '^^CP^0509876543'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='JORV', pl_2='POLI2', pl_3='Vastaanottohuone 3', pl_5='HUS')
        pv1.pv1_7 = 'DR201^Mäkinen^Juha^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI200001')
        pv1.pending_location = PL(pl_1='20260509100000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='LAHITAPIOLA')
        in1.insurance_company_id = CX(cx_1='200002')
        in1.insurance_company_name = XON(xon_1='LähiTapiola Vakuutus')
        in1.insurance_company_address = XAD(xad_1='Revontulenkuja 1', xad_3='Espoo', xad_5='02100', xad_6='FIN')

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
    """ Based on live/fi/fi-apotti.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APOTTI')
        msh.sending_facility = HD(hd_1='HUS_HELSINKI')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260509110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'APOTTI000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260509110000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PT300003', cx_4='HUS', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Hämäläinen', xpn_2='Liisa', xpn_3='Marjatta', xpn_5='Rouva')
        pid.date_time_of_birth = '19600418'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Aleksanterinkatu 7', xad_3='Helsinki', xad_5='00100', xad_6='FIN')
        pid.pid_13 = '^^PH^0913579246~^^CP^0441357924'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MEIL', pl_2='SIS1', pl_3='Huone 112', pl_4='Vuode 1', pl_5='HUS')
        pv1.pv1_7 = 'DR102^Lehtonen^Markku^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO300001')
        pv1.pending_location = PL(pl_1='20260507080000')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Hämäläinen', xpn_2='Kalle')
        nk1.address = [XAD(xad_3='PH', xad_4='0913579247'), XAD(xad_3='CP', xad_4='0441357925')]
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
    """ Based on live/fi/fi-apotti.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APOTTI')
        msh.sending_facility = HD(hd_1='HUS_HELSINKI')
        msh.receiving_application = HD(hd_1='VRK')
        msh.receiving_facility = HD(hd_1='DVV')
        msh.date_time_of_message = '20260509120000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'APOTTI000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20260509120000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT400004', cx_4='HUS', cx_5='MR'), CX(cx_1='150465-123A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Koskinen', xpn_2='Eero', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19650415'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hämeenkatu 33', xad_3='Tampere', xad_5='33100', xad_6='FIN')
        pid.pid_13 = '^^CP^0507654321'

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
    """ Based on live/fi/fi-apotti.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APOTTI')
        msh.sending_facility = HD(hd_1='HUS_HELSINKI')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260509130000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'APOTTI000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260509130000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PT500005', cx_4='HUS', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Järvinen', xpn_2='Sari', xpn_3='Helena', xpn_5='Rouva')
        pid.date_time_of_birth = '19750830'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Fredrikinkatu 60', xad_3='Helsinki', xad_5='00100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401122334'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='PT500099', cx_4='HUS', cx_5='MR')

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
    """ Based on live/fi/fi-apotti.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APOTTI')
        msh.sending_facility = HD(hd_1='HUS_HELSINKI')
        msh.receiving_application = HD(hd_1='HUSLAB')
        msh.receiving_facility = HD(hd_1='HUS')
        msh.date_time_of_message = '20260509090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'APOTTI000008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT600006', cx_4='HUS', cx_5='MR'), CX(cx_1='010382-456B', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Laine', xpn_2='Mikko', xpn_3='Antero', xpn_5='Herra')
        pid.date_time_of_birth = '19820301'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Bulevardi 22', xad_3='Helsinki', xad_5='00120', xad_6='FIN')
        pid.pid_13 = '^^CP^0401223344'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MEIL', pl_2='POLI1', pl_3='Vastaanottohuone 5', pl_5='HUS')
        pv1.pv1_7 = 'DR103^Heikkinen^Tuula^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI600001')

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
        orc.placer_order_number = EI(ei_1='ORD600001', ei_2='APOTTI')
        orc.orc_7 = '^^^20260509090000^^R'
        orc.date_time_of_order_event = '20260509090000'
        orc.orc_10 = 'DR103^Heikkinen^Tuula^^^LKT^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600001', ei_2='APOTTI')
        obr.universal_service_identifier = CWE(cwe_1='2741', cwe_2='B-PVK+T', cwe_3='HUSLAB')
        obr.observation_date_time = '20260509090000'
        obr.obr_15 = 'DR103^Heikkinen^Tuula^^^LKT^Lääkäri'

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
        obr_2.placer_order_number = EI(ei_1='ORD600001', ei_2='APOTTI')
        obr_2.universal_service_identifier = CWE(cwe_1='4587', cwe_2='fP-Gluk', cwe_3='HUSLAB')
        obr_2.observation_date_time = '20260509090000'
        obr_2.obr_15 = 'DR103^Heikkinen^Tuula^^^LKT^Lääkäri'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='ORD600001', ei_2='APOTTI')
        obr_3.universal_service_identifier = CWE(cwe_1='4520', cwe_2='P-CRP', cwe_3='HUSLAB')
        obr_3.observation_date_time = '20260509090000'
        obr_3.obr_15 = 'DR103^Heikkinen^Tuula^^^LKT^Lääkäri'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3]

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
    """ Based on live/fi/fi-apotti.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HUSLAB')
        msh.sending_facility = HD(hd_1='HUS')
        msh.receiving_application = HD(hd_1='APOTTI')
        msh.receiving_facility = HD(hd_1='HUS_HELSINKI')
        msh.date_time_of_message = '20260509143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HUSLAB000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT600006', cx_4='HUS', cx_5='MR'), CX(cx_1='010382-456B', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Laine', xpn_2='Mikko', xpn_3='Antero', xpn_5='Herra')
        pid.date_time_of_birth = '19820301'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Bulevardi 22', xad_3='Helsinki', xad_5='00120', xad_6='FIN')
        pid.pid_13 = '^^CP^0401223344'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MEIL', pl_2='POLI1', pl_3='Vastaanottohuone 5', pl_5='HUS')
        pv1.pv1_7 = 'DR103^Heikkinen^Tuula^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI600001')

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
        orc.placer_order_number = EI(ei_1='ORD600001', ei_2='APOTTI')
        orc.filler_order_number = EI(ei_1='RES600001', ei_2='HUSLAB')
        orc.orc_7 = '^^^20260509090000^^R'
        orc.date_time_of_order_event = '20260509143000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD600001', ei_2='APOTTI')
        obr.filler_order_number = EI(ei_1='RES600001', ei_2='HUSLAB')
        obr.universal_service_identifier = CWE(cwe_1='2741', cwe_2='B-PVK+T', cwe_3='HUSLAB')
        obr.observation_date_time = '20260509091500'
        obr.obr_14 = '20260509091500'
        obr.obr_15 = '^^B'
        obr.obr_16 = 'DR103^Heikkinen^Tuula^^^LKT^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6768', cwe_2='B-Leuk', cwe_3='HUSLAB')
        obx.obx_5 = '7.2'
        obx.units = CWE(cwe_1='10E9/l')
        obx.reference_range = '3.4-8.2'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509143000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2171', cwe_2='B-Eryt', cwe_3='HUSLAB')
        obx_2.obx_5 = '4.85'
        obx_2.units = CWE(cwe_1='10E12/l')
        obx_2.reference_range = '4.25-5.70'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509143000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='1552', cwe_2='B-Hb', cwe_3='HUSLAB')
        obx_3.obx_5 = '148'
        obx_3.units = CWE(cwe_1='g/l')
        obx_3.reference_range = '134-167'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509143000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2798', cwe_2='B-Trom', cwe_3='HUSLAB')
        obx_4.obx_5 = '245'
        obx_4.units = CWE(cwe_1='10E9/l')
        obx_4.reference_range = '150-360'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509143000'

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
    """ Based on live/fi/fi-apotti.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HUSLAB')
        msh.sending_facility = HD(hd_1='HUS')
        msh.receiving_application = HD(hd_1='APOTTI')
        msh.receiving_facility = HD(hd_1='HUS_HELSINKI')
        msh.date_time_of_message = '20260509150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HUSLAB000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT700007', cx_4='HUS', cx_5='MR'), CX(cx_1='230955-789C', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Korhonen', xpn_2='Aino', xpn_3='Elina', xpn_5='Rouva')
        pid.date_time_of_birth = '19550923'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Töölönkatu 18', xad_3='Helsinki', xad_5='00260', xad_6='FIN')
        pid.pid_13 = '^^PH^0912233445'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MEIL', pl_2='INF1', pl_3='Huone 308', pl_4='Vuode 2', pl_5='HUS')
        pv1.pv1_7 = 'DR104^Salonen^Pekka^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO700001')

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
        orc.placer_order_number = EI(ei_1='ORD700001', ei_2='APOTTI')
        orc.filler_order_number = EI(ei_1='RES700001', ei_2='HUSLAB')
        orc.orc_7 = '^^^20260509080000^^R'
        orc.date_time_of_order_event = '20260509150000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700001', ei_2='APOTTI')
        obr.filler_order_number = EI(ei_1='RES700001', ei_2='HUSLAB')
        obr.universal_service_identifier = CWE(cwe_1='4520', cwe_2='P-CRP', cwe_3='HUSLAB')
        obr.observation_date_time = '20260509082000'
        obr.obr_14 = '20260509082000'
        obr.obr_15 = '^^B'
        obr.obr_16 = 'DR104^Salonen^Pekka^^^LKT^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4520', cwe_2='P-CRP', cwe_3='HUSLAB')
        obx.obx_5 = '125'
        obx.units = CWE(cwe_1='mg/l')
        obx.reference_range = '<3'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509150000'

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
    """ Based on live/fi/fi-apotti.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APOTTI')
        msh.sending_facility = HD(hd_1='HUS_HELSINKI')
        msh.receiving_application = HD(hd_1='APOTTI_SCHED')
        msh.receiving_facility = HD(hd_1='HUS')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'APOTTI000009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT800001')
        sch.filler_appointment_id = EI(ei_1='APT800001')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_2='Normaali', cwe_3='HL70276')
        sch.appointment_reason = CWE(cwe_1='FOLLOWUP', cwe_2='Kontrollikäynti', cwe_3='HL70277')
        sch.appointment_type = CWE(cwe_1='DOCTOR', cwe_2='Lääkärin vastaanotto')
        sch.sch_9 = '30'
        sch.appointment_duration_units = CNE(cne_1='min')
        sch.sch_11 = '^^^20260520093000^20260520100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT800008', cx_4='HUS', cx_5='MR'), CX(cx_1='120790-234D', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Mäkelä', xpn_2='Tuomas', xpn_3='Petteri', xpn_5='Herra')
        pid.date_time_of_birth = '19900712'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kaivokatu 8', xad_3='Helsinki', xad_5='00100', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MEIL', pl_2='POLI3', pl_3='Vastaanottohuone 7', pl_5='HUS')
        pv1.pv1_7 = 'DR105^Rantanen^Kirsi^^^LKT^Lääkäri'

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
        ais.universal_service_identifier = CWE(cwe_1='ORTPOLI', cwe_2='Ortopedian poliklinikka', cwe_3='APOTTI')
        ais.start_date_time = '20260520093000'
        ais.start_date_time_offset = '30'
        ais.start_date_time_offset_units = CNE(cne_1='min')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.aip_3 = 'DR105^Rantanen^Kirsi^^^LKT^Lääkäri'

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
    """ Based on live/fi/fi-apotti.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APOTTI')
        msh.sending_facility = HD(hd_1='HUS_HELSINKI')
        msh.receiving_application = HD(hd_1='APOTTI_SCHED')
        msh.receiving_facility = HD(hd_1='HUS')
        msh.date_time_of_message = '20260512080000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S14', msg_3='SIU_S12')
        msh.message_control_id = 'APOTTI000010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT800001')
        sch.filler_appointment_id = EI(ei_1='APT800001')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_2='Normaali', cwe_3='HL70276')
        sch.appointment_reason = CWE(cwe_1='FOLLOWUP', cwe_2='Kontrollikäynti', cwe_3='HL70277')
        sch.appointment_type = CWE(cwe_1='DOCTOR', cwe_2='Lääkärin vastaanotto')
        sch.sch_9 = '30'
        sch.appointment_duration_units = CNE(cne_1='min')
        sch.sch_11 = '^^^20260522093000^20260522100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT800008', cx_4='HUS', cx_5='MR'), CX(cx_1='120790-234D', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Mäkelä', xpn_2='Tuomas', xpn_3='Petteri', xpn_5='Herra')
        pid.date_time_of_birth = '19900712'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kaivokatu 8', xad_3='Helsinki', xad_5='00100', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MEIL', pl_2='POLI3', pl_3='Vastaanottohuone 7', pl_5='HUS')
        pv1.pv1_7 = 'DR105^Rantanen^Kirsi^^^LKT^Lääkäri'

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
        ais.universal_service_identifier = CWE(cwe_1='ORTPOLI', cwe_2='Ortopedian poliklinikka', cwe_3='APOTTI')
        ais.start_date_time = '20260522093000'
        ais.start_date_time_offset = '30'
        ais.start_date_time_offset_units = CNE(cne_1='min')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.aip_3 = 'DR105^Rantanen^Kirsi^^^LKT^Lääkäri'

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
    """ Based on live/fi/fi-apotti.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APOTTI')
        msh.sending_facility = HD(hd_1='HUS_HELSINKI')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260509160000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'APOTTI000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260509160000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT900009', cx_4='HUS', cx_5='MR'), CX(cx_1='050575-567E', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Heikkinen', xpn_2='Raija', xpn_3='Anneli', xpn_5='Rouva')
        pid.date_time_of_birth = '19750505'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Runeberginkatu 25', xad_3='Helsinki', xad_5='00100', xad_6='FIN')
        pid.pid_13 = '^^CP^0409876543'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MEIL', pl_2='KIR2', pl_3='Huone 310', pl_4='Vuode 1', pl_5='HUS')
        pv1.pv1_7 = 'DR106^Virtanen^Jarkko^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO900001')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='OP', cwe_2='Leikkauskertomus')
        txa.document_content_presentation = 'TX'
        txa.origination_date_time = '20260509160000'
        txa.unique_document_number = EI(ei_1='DOC900001')
        txa.unique_document_file_name = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='11504-8', cwe_2='Surgical operation note', cwe_3='LN')
        obx.obx_5 = 'Potilaalle suoritettiin vasemman lonkan tekonivelleikkaus. Toimenpide sujui komplikaatioitta.'
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
    """ Based on live/fi/fi-apotti.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HUSLAB')
        msh.sending_facility = HD(hd_1='HUS')
        msh.receiving_application = HD(hd_1='APOTTI')
        msh.receiving_facility = HD(hd_1='HUS_HELSINKI')
        msh.date_time_of_message = '20260509170000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HUSLAB000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT101010', cx_4='HUS', cx_5='MR'), CX(cx_1='281060+345F', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Lehtonen', xpn_2='Veikko', xpn_3='Kalevi', xpn_5='Herra')
        pid.date_time_of_birth = '19601028'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kirkkokatu 14', xad_3='Turku', xad_5='20100', xad_6='FIN')
        pid.pid_13 = '^^PH^0221234567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MEIL', pl_2='INF2', pl_3='Huone 415', pl_4='Vuode 1', pl_5='HUS')
        pv1.pv1_7 = 'DR107^Ahonen^Minna^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO101001')

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
        orc.placer_order_number = EI(ei_1='ORD101001', ei_2='APOTTI')
        orc.filler_order_number = EI(ei_1='RES101001', ei_2='HUSLAB')
        orc.orc_7 = '^^^20260507090000^^R'
        orc.date_time_of_order_event = '20260509170000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD101001', ei_2='APOTTI')
        obr.filler_order_number = EI(ei_1='RES101001', ei_2='HUSLAB')
        obr.universal_service_identifier = CWE(cwe_1='1155', cwe_2='Pu-BaktVi', cwe_3='HUSLAB')
        obr.observation_date_time = '20260507091000'
        obr.obr_14 = '20260507091000'
        obr.obr_15 = '^^PU'
        obr.obr_16 = 'DR107^Ahonen^Minna^^^LKT^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509170000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='1155', cwe_2='Pu-BaktVi', cwe_3='HUSLAB')
        obx.obx_5 = 'SAUR^Staphylococcus aureus^HUSLAB'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509170000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='ABRES', cwe_2='Herkkyys', cwe_3='HUSLAB')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = 'Oksasilliini S, Klindamysiini S, Vankomysiini S'
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
    """ Based on live/fi/fi-apotti.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HUSLAB_PAT')
        msh.sending_facility = HD(hd_1='HUS')
        msh.receiving_application = HD(hd_1='APOTTI')
        msh.receiving_facility = HD(hd_1='HUS_HELSINKI')
        msh.date_time_of_message = '20260509180000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HUSLAB000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT111011', cx_4='HUS', cx_5='MR'), CX(cx_1='150385-678G', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Salminen', xpn_2='Kaarina', xpn_3='Irene', xpn_5='Rouva')
        pid.date_time_of_birth = '19850315'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Mechelininkatu 10', xad_3='Helsinki', xad_5='00100', xad_6='FIN')
        pid.pid_13 = '^^CP^0407654321'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MEIL', pl_2='POLI4', pl_3='Vastaanottohuone 2', pl_5='HUS')
        pv1.pv1_7 = 'DR108^Laaksonen^Ville^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI111001')

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
        orc.placer_order_number = EI(ei_1='ORD111001', ei_2='APOTTI')
        orc.filler_order_number = EI(ei_1='RES111001', ei_2='HUSLAB_PAT')
        orc.orc_7 = '^^^20260505100000^^R'
        orc.date_time_of_order_event = '20260509180000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD111001', ei_2='APOTTI')
        obr.filler_order_number = EI(ei_1='RES111001', ei_2='HUSLAB_PAT')
        obr.universal_service_identifier = CWE(cwe_1='60570-9', cwe_2='Pathology report', cwe_3='LN')
        obr.observation_date_time = '20260505101500'
        obr.obr_14 = '20260505101500'
        obr.obr_15 = '^^Biopsia'
        obr.obr_16 = 'DR108^Laaksonen^Ville^^^LKT^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509180000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='22634-0', cwe_2='Pathology report text', cwe_3='LN')
        obx.obx_5 = 'Histologinen diagnoosi: Fibroadenooma mammae sin. Ei maligniteettia.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509180000'

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
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509180000'

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
    """ Based on live/fi/fi-apotti.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APOTTI')
        msh.sending_facility = HD(hd_1='HUS_JORVI')
        msh.receiving_application = HD(hd_1='SECTRA_RIS')
        msh.receiving_facility = HD(hd_1='HUS_RAD')
        msh.date_time_of_message = '20260509113000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'APOTTI000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT121012', cx_4='HUS', cx_5='MR'), CX(cx_1='220498-901H', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Lahtinen', xpn_2='Ville', xpn_3='Oskari', xpn_5='Herra')
        pid.date_time_of_birth = '19980422'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Itäkatu 1', xad_3='Helsinki', xad_5='00930', xad_6='FIN')
        pid.pid_13 = '^^CP^0401122335'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='JORV', pl_2='PPKL', pl_3='Tutkimushuone 1', pl_5='HUS')
        pv1.pv1_7 = 'DR109^Nurmi^Sanna^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI121001')

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
        orc.placer_order_number = EI(ei_1='ORD121001', ei_2='APOTTI')
        orc.orc_7 = '^^^20260509113000^^S'
        orc.date_time_of_order_event = '20260509113000'
        orc.orc_10 = 'DR109^Nurmi^Sanna^^^LKT^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD121001', ei_2='APOTTI')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Thorax AP+LAT', cwe_3='RADLEX')
        obr.observation_date_time = '20260509113000'
        obr.obr_15 = 'DR109^Nurmi^Sanna^^^LKT^Lääkäri'
        obr.result_status = 'TRAUMA^Vammamekanismi'

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
    """ Based on live/fi/fi-apotti.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_RIS')
        msh.sending_facility = HD(hd_1='HUS_RAD')
        msh.receiving_application = HD(hd_1='APOTTI')
        msh.receiving_facility = HD(hd_1='HUS_JORVI')
        msh.date_time_of_message = '20260509153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SECTRA000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT121012', cx_4='HUS', cx_5='MR'), CX(cx_1='220498-901H', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Lahtinen', xpn_2='Ville', xpn_3='Oskari', xpn_5='Herra')
        pid.date_time_of_birth = '19980422'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Itäkatu 1', xad_3='Helsinki', xad_5='00930', xad_6='FIN')
        pid.pid_13 = '^^CP^0401122335'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='JORV', pl_2='PPKL', pl_3='Tutkimushuone 1', pl_5='HUS')
        pv1.pv1_7 = 'DR109^Nurmi^Sanna^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI121001')

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
        orc.placer_order_number = EI(ei_1='ORD121001', ei_2='APOTTI')
        orc.filler_order_number = EI(ei_1='RES121001', ei_2='SECTRA_RIS')
        orc.orc_7 = '^^^20260509113000^^S'
        orc.date_time_of_order_event = '20260509153000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD121001', ei_2='APOTTI')
        obr.filler_order_number = EI(ei_1='RES121001', ei_2='SECTRA_RIS')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Thorax AP+LAT', cwe_3='RADLEX')
        obr.observation_date_time = '20260509120000'
        obr.obr_14 = '20260509120000'
        obr.obr_15 = '^^Thorax'
        obr.obr_16 = 'DR110^Kallio^Risto^^^RAD^Radiologi'
        obr.results_rpt_status_chng_date_time = '20260509153000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx.obx_5 = 'Keuhkokuvassa ei havaita infiltraatteja. Sydämen koko normaali. Ei pleuranestettä.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509153000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Radiologinen lausunto', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKL01hcmtJbmZvIDw8Ci9NYXJrZWQgdHJ1ZQo+PgovTGFuZyAoZmkpCj4+CmVuZG9iagoy'
            'IDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwo+PgplbmRvYmoK'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509153000'

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
    """ Based on live/fi/fi-apotti.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HUSLAB')
        msh.sending_facility = HD(hd_1='HUS')
        msh.receiving_application = HD(hd_1='APOTTI')
        msh.receiving_facility = HD(hd_1='HUS_HELSINKI')
        msh.date_time_of_message = '20260509162000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HUSLAB000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT131013', cx_4='HUS', cx_5='MR'), CX(cx_1='090840+012J', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Mäkinen', xpn_2='Erkki', xpn_3='Olavi', xpn_5='Herra')
        pid.date_time_of_birth = '19400809'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Porthaninkatu 5', xad_3='Helsinki', xad_5='00530', xad_6='FIN')
        pid.pid_13 = '^^PH^0914567890'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='MEIL', pl_2='TEHO', pl_3='Paikka 3', pl_5='HUS')
        pv1.pv1_7 = 'DR111^Tuominen^Elina^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO131001')

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
        orc.placer_order_number = EI(ei_1='ORD131001', ei_2='APOTTI')
        orc.filler_order_number = EI(ei_1='RES131001', ei_2='HUSLAB')
        orc.orc_7 = '^^^20260509155000^^S'
        orc.date_time_of_order_event = '20260509162000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD131001', ei_2='APOTTI')
        obr.filler_order_number = EI(ei_1='RES131001', ei_2='HUSLAB')
        obr.universal_service_identifier = CWE(cwe_1='24338-6', cwe_2='aB-Verikaasuanalyysi', cwe_3='LN')
        obr.observation_date_time = '20260509155500'
        obr.obr_14 = '20260509155500'
        obr.obr_15 = '^^aB'
        obr.obr_16 = 'DR111^Tuominen^Elina^^^LKT^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509162000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2744-1', cwe_2='aB-pH', cwe_3='LN')
        obx.obx_5 = '7.38'
        obx.reference_range = '7.35-7.45'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509162000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2019-8', cwe_2='aB-pCO2', cwe_3='LN')
        obx_2.obx_5 = '5.1'
        obx_2.units = CWE(cwe_1='kPa')
        obx_2.reference_range = '4.7-6.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509162000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2703-7', cwe_2='aB-pO2', cwe_3='LN')
        obx_3.obx_5 = '11.2'
        obx_3.units = CWE(cwe_1='kPa')
        obx_3.reference_range = '11.0-14.4'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509162000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1959-6', cwe_2='aB-HCO3', cwe_3='LN')
        obx_4.obx_5 = '23.5'
        obx_4.units = CWE(cwe_1='mmol/l')
        obx_4.reference_range = '22.0-26.0'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509162000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='1925-7', cwe_2='aB-BE', cwe_3='LN')
        obx_5.obx_5 = '-1.2'
        obx_5.units = CWE(cwe_1='mmol/l')
        obx_5.reference_range = '-2.5-2.5'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509162000'

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
    """ Based on live/fi/fi-apotti.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='APOTTI')
        msh.sending_facility = HD(hd_1='HUS_HELSINKI')
        msh.receiving_application = HD(hd_1='APTEEKKI')
        msh.receiving_facility = HD(hd_1='HUS_SAIRAALA_APT')
        msh.date_time_of_message = '20260509141000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'APOTTI000013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT141014', cx_4='HUS', cx_5='MR'), CX(cx_1='170295-345K', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Rantala', xpn_2='Katri', xpn_3='Johanna', xpn_5='Rouva')
        pid.date_time_of_birth = '19950217'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Unioninkatu 39', xad_3='Helsinki', xad_5='00170', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234568'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MEIL', pl_2='SIS2', pl_3='Huone 218', pl_4='Vuode 2', pl_5='HUS')
        pv1.pv1_7 = 'DR112^Leppänen^Antti^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO141001')

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
        orc.placer_order_number = EI(ei_1='ORD141001', ei_2='APOTTI')
        orc.orc_7 = '^^^20260509141000^^R'
        orc.date_time_of_order_event = '20260509141000'
        orc.orc_10 = 'DR112^Leppänen^Antti^^^LKT^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD141001', ei_2='APOTTI')
        obr.universal_service_identifier = CWE(cwe_1='LAAKE', cwe_2='Lääketilaus', cwe_3='APOTTI')
        obr.observation_date_time = '20260509141000'
        obr.obr_15 = 'DR112^Leppänen^Antti^^^LKT^Lääkäri'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='R06AA02', cwe_2='Doksylamiini', cwe_3='ATC')
        rxo.requested_give_amount_maximum = '10'
        rxo.requested_give_units = CWE(cwe_1='mg')
        rxo.providers_pharmacy_treatment_instructions = CWE(cwe_1='PO', cwe_2='Suun kautta', cwe_3='HL70162')
        rxo.providers_administration_instructions = CWE(cwe_4='20260509180000', cwe_6='R')
        rxo.rxo_8 = '10'
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
    """ Based on live/fi/fi-apotti.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HUSLAB')
        msh.sending_facility = HD(hd_1='HUS')
        msh.receiving_application = HD(hd_1='APOTTI')
        msh.receiving_facility = HD(hd_1='HUS_HELSINKI')
        msh.date_time_of_message = '20260509173000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HUSLAB000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'
        msh.principal_language_of_message = CWE(cwe_1='UTF-8')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT151015', cx_4='HUS', cx_5='MR'), CX(cx_1='030578-890L', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Rinne', xpn_2='Johanna', xpn_3='Elisa', xpn_5='Rouva')
        pid.date_time_of_birth = '19780503'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Tehtaankatu 12', xad_3='Helsinki', xad_5='00140', xad_6='FIN')
        pid.pid_13 = '^^CP^0409988776'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MEIL', pl_2='POLI5', pl_3='Vastaanottohuone 9', pl_5='HUS')
        pv1.pv1_7 = 'DR113^Kinnunen^Harri^^^LKT^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI151001')

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
        orc.placer_order_number = EI(ei_1='ORD151001', ei_2='APOTTI')
        orc.filler_order_number = EI(ei_1='RES151001', ei_2='HUSLAB')
        orc.orc_7 = '^^^20260509090000^^R'
        orc.date_time_of_order_event = '20260509173000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD151001', ei_2='APOTTI')
        obr.filler_order_number = EI(ei_1='RES151001', ei_2='HUSLAB')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Laaja metabolinen paneeli', cwe_3='LN')
        obr.observation_date_time = '20260509092000'
        obr.obr_14 = '20260509092000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR113^Kinnunen^Harri^^^LKT^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509173000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2947-0', cwe_2='fP-Na', cwe_3='LN')
        obx.obx_5 = '141'
        obx.units = CWE(cwe_1='mmol/l')
        obx.reference_range = '137-145'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509173000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6298-4', cwe_2='fP-K', cwe_3='LN')
        obx_2.obx_5 = '4.2'
        obx_2.units = CWE(cwe_1='mmol/l')
        obx_2.reference_range = '3.5-5.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509173000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2160-0', cwe_2='fP-Krea', cwe_3='LN')
        obx_3.obx_5 = '72'
        obx_3.units = CWE(cwe_1='umol/l')
        obx_3.reference_range = '50-90'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509173000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1742-6', cwe_2='fP-ALAT', cwe_3='LN')
        obx_4.obx_5 = '28'
        obx_4.units = CWE(cwe_1='U/l')
        obx_4.reference_range = '<40'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509173000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='1920-8', cwe_2='fP-ASAT', cwe_3='LN')
        obx_5.obx_5 = '24'
        obx_5.units = CWE(cwe_1='U/l')
        obx_5.reference_range = '<35'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509173000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='14879-1', cwe_2='fP-Gluk', cwe_3='LN')
        obx_6.obx_5 = '5.4'
        obx_6.units = CWE(cwe_1='mmol/l')
        obx_6.reference_range = '4.0-6.0'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509173000'

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
