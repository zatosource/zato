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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, HD, MSG, PL, PT, VID, XAD, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import EVN, IN1, MSH, NTE, OBR, OBX, ORC, PID, PV1, PV2

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('fi', 'fi-vitec-acute.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/fi/fi-vitec-acute.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ACUTE')
        msh.sending_facility = HD(hd_1='KYS')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='KYS_HIS')
        msh.date_time_of_message = '20260509080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04')
        msh.message_control_id = 'ACUTE000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260509080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT500001', cx_4='KYS', cx_5='MR'), CX(cx_1='200185-234A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Turunen', xpn_2='Ville', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19850120'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Tulliportinkatu 15', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234582'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='KYS', pl_2='PPKL', pl_3='Triage 1', pl_5='PSSHP')
        pv1.pv1_7 = 'DR500^Korhonen^Matti^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI500001')
        pv1.pending_location = PL(pl_1='20260509080000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Rintakipu')

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
    """ Based on live/fi/fi-vitec-acute.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ACUTE')
        msh.sending_facility = HD(hd_1='KYS')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='KYS_HIS')
        msh.date_time_of_message = '20260509120000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        msh.message_control_id = 'ACUTE000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260509120000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT500001', cx_4='KYS', cx_5='MR'), CX(cx_1='200185-234A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Turunen', xpn_2='Ville', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19850120'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Tulliportinkatu 15', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234582'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='KYS', pl_2='SIS1', pl_3='Huone 302', pl_4='Vuode 1', pl_5='PSSHP')
        pv1.pv1_7 = 'DR500^Korhonen^Matti^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO500001')
        pv1.pending_location = PL(pl_1='20260509120000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Sydäninfarktiepäily')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='POHJOLA')
        in1.insurance_company_id = CX(cx_1='500001')
        in1.insurance_company_name = XON(xon_1='Pohjola Vakuutus')
        in1.insurance_company_address = XAD(xad_1='Lapinmäentie 1', xad_3='Helsinki', xad_5='00350', xad_6='FIN')

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
    """ Based on live/fi/fi-vitec-acute.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ACUTE')
        msh.sending_facility = HD(hd_1='KYS')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='KYS_HIS')
        msh.date_time_of_message = '20260509143000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03')
        msh.message_control_id = 'ACUTE000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260509143000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT500002', cx_4='KYS', cx_5='MR'), CX(cx_1='150392-567B', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Laitinen', xpn_2='Sanna', xpn_3='Kristiina', xpn_5='Rouva')
        pid.date_time_of_birth = '19920315'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Kauppakatu 22', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^CP^0509876550'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='KYS', pl_2='PPKL', pl_3='Triage 2', pl_5='PSSHP')
        pv1.pv1_7 = 'DR501^Mäkinen^Elisa^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI500002')
        pv1.pending_location = PL(pl_1='20260509100000')
        pv1.prior_temporary_location = PL(pl_1='20260509143000')

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
    """ Based on live/fi/fi-vitec-acute.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ACUTE')
        msh.sending_facility = HD(hd_1='KYS')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='KYS_HIS')
        msh.date_time_of_message = '20260509090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08')
        msh.message_control_id = 'ACUTE000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260509090000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT500001', cx_4='KYS', cx_5='MR'), CX(cx_1='200185-234A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Turunen', xpn_2='Ville', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19850120'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Tulliportinkatu 15', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234582'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='KYS', pl_2='PPKL', pl_3='Triage 1', pl_5='PSSHP')
        pv1.pv1_7 = 'DR500^Korhonen^Matti^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI500001')
        pv1.pending_location = PL(pl_1='20260509080000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Sydäninfarktiepäily, ESI 2')

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
    """ Based on live/fi/fi-vitec-acute.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ACUTE')
        msh.sending_facility = HD(hd_1='KYS')
        msh.receiving_application = HD(hd_1='KYSLAB')
        msh.receiving_facility = HD(hd_1='PSSHP')
        msh.date_time_of_message = '20260509081500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'ACUTE000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT500001', cx_4='KYS', cx_5='MR'), CX(cx_1='200185-234A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Turunen', xpn_2='Ville', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19850120'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Tulliportinkatu 15', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234582'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='KYS', pl_2='PPKL', pl_3='Triage 1', pl_5='PSSHP')
        pv1.pv1_7 = 'DR500^Korhonen^Matti^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI500001')

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
        orc.placer_order_number = EI(ei_1='ORD500001', ei_2='ACUTE')
        orc.orc_7 = '^^^20260509081500^^S'
        orc.date_time_of_order_event = '20260509081500'
        orc.orc_10 = 'DR500^Korhonen^Matti^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD500001', ei_2='ACUTE')
        obr.universal_service_identifier = CWE(cwe_1='4825', cwe_2='P-TnT', cwe_3='KYSLAB')
        obr.observation_date_time = '20260509081500'
        obr.relevant_clinical_information = CWE(cwe_1='S')
        obr.obr_15 = 'DR500^Korhonen^Matti^^^LL^Lääkäri'

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
        obr_2.placer_order_number = EI(ei_1='ORD500001', ei_2='ACUTE')
        obr_2.universal_service_identifier = CWE(cwe_1='2741', cwe_2='B-PVK+T', cwe_3='KYSLAB')
        obr_2.observation_date_time = '20260509081500'
        obr_2.relevant_clinical_information = CWE(cwe_1='S')
        obr_2.obr_15 = 'DR500^Korhonen^Matti^^^LL^Lääkäri'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='ORD500001', ei_2='ACUTE')
        obr_3.universal_service_identifier = CWE(cwe_1='4520', cwe_2='P-CRP', cwe_3='KYSLAB')
        obr_3.observation_date_time = '20260509081500'
        obr_3.relevant_clinical_information = CWE(cwe_1='S')
        obr_3.obr_15 = 'DR500^Korhonen^Matti^^^LL^Lääkäri'

        # .. build OBR ..
        obr_4 = OBR()
        obr_4.set_id_obr = '4'
        obr_4.placer_order_number = EI(ei_1='ORD500001', ei_2='ACUTE')
        obr_4.universal_service_identifier = CWE(cwe_1='2003', cwe_2='P-Krea', cwe_3='KYSLAB')
        obr_4.observation_date_time = '20260509081500'
        obr_4.relevant_clinical_information = CWE(cwe_1='S')
        obr_4.obr_15 = 'DR500^Korhonen^Matti^^^LL^Lääkäri'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3, obr_4]

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
    """ Based on live/fi/fi-vitec-acute.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KYSLAB')
        msh.sending_facility = HD(hd_1='PSSHP')
        msh.receiving_application = HD(hd_1='ACUTE')
        msh.receiving_facility = HD(hd_1='KYS')
        msh.date_time_of_message = '20260509101000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'KYSLAB000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT500001', cx_4='KYS', cx_5='MR'), CX(cx_1='200185-234A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Turunen', xpn_2='Ville', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19850120'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Tulliportinkatu 15', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234582'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='KYS', pl_2='PPKL', pl_3='Triage 1', pl_5='PSSHP')
        pv1.pv1_7 = 'DR500^Korhonen^Matti^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI500001')

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
        orc.placer_order_number = EI(ei_1='ORD500001', ei_2='ACUTE')
        orc.filler_order_number = EI(ei_1='RES500001', ei_2='KYSLAB')
        orc.orc_7 = '^^^20260509081500^^S'
        orc.date_time_of_order_event = '20260509101000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD500001', ei_2='ACUTE')
        obr.filler_order_number = EI(ei_1='RES500001', ei_2='KYSLAB')
        obr.universal_service_identifier = CWE(cwe_1='4825', cwe_2='P-TnT', cwe_3='KYSLAB')
        obr.observation_date_time = '20260509082000'
        obr.obr_14 = '20260509082000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR500^Korhonen^Matti^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509101000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6598-7', cwe_2='P-TnT', cwe_3='LN')
        obx.obx_5 = '312'
        obx.units = CWE(cwe_1='ng/l')
        obx.reference_range = '<14'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509101000'

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
    """ Based on live/fi/fi-vitec-acute.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KYSLAB')
        msh.sending_facility = HD(hd_1='PSSHP')
        msh.receiving_application = HD(hd_1='ACUTE')
        msh.receiving_facility = HD(hd_1='KYS')
        msh.date_time_of_message = '20260509103000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'KYSLAB000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT500003', cx_4='KYS', cx_5='MR'), CX(cx_1='081170-890C', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Hänninen', xpn_2='Markku', xpn_3='Olavi', xpn_5='Herra')
        pid.date_time_of_birth = '19701108'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Puijonkatu 33', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^PH^0171234567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='KYS', pl_2='PPKL', pl_3='Triage 3', pl_5='PSSHP')
        pv1.pv1_7 = 'DR502^Lahtinen^Olli^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI500003')

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
        orc.placer_order_number = EI(ei_1='ORD500002', ei_2='ACUTE')
        orc.filler_order_number = EI(ei_1='RES500002', ei_2='KYSLAB')
        orc.orc_7 = '^^^20260509091000^^S'
        orc.date_time_of_order_event = '20260509103000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD500002', ei_2='ACUTE')
        obr.filler_order_number = EI(ei_1='RES500002', ei_2='KYSLAB')
        obr.universal_service_identifier = CWE(cwe_1='2741', cwe_2='B-PVK+T', cwe_3='KYSLAB')
        obr.observation_date_time = '20260509092000'
        obr.obr_14 = '20260509092000'
        obr.obr_15 = '^^B'
        obr.obr_16 = 'DR502^Lahtinen^Olli^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509103000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6768', cwe_2='B-Leuk', cwe_3='KYSLAB')
        obx.obx_5 = '14.5'
        obx.units = CWE(cwe_1='10E9/l')
        obx.reference_range = '3.4-8.2'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509103000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1552', cwe_2='B-Hb', cwe_3='KYSLAB')
        obx_2.obx_5 = '145'
        obx_2.units = CWE(cwe_1='g/l')
        obx_2.reference_range = '134-167'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509103000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2798', cwe_2='B-Trom', cwe_3='KYSLAB')
        obx_3.obx_5 = '310'
        obx_3.units = CWE(cwe_1='10E9/l')
        obx_3.reference_range = '150-360'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509103000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4520', cwe_2='P-CRP', cwe_3='KYSLAB')
        obx_4.obx_5 = '68'
        obx_4.units = CWE(cwe_1='mg/l')
        obx_4.reference_range = '<3'
        obx_4.interpretation_codes = CWE(cwe_1='HH')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509103000'

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
    """ Based on live/fi/fi-vitec-acute.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ACUTE')
        msh.sending_facility = HD(hd_1='KYS')
        msh.receiving_application = HD(hd_1='SECTRA_RIS')
        msh.receiving_facility = HD(hd_1='KYS_RAD')
        msh.date_time_of_message = '20260509091000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'ACUTE000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT500004', cx_4='KYS', cx_5='MR'), CX(cx_1='250300-123D', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Kokkonen', xpn_2='Aleksi', xpn_3='Petteri', xpn_5='Herra')
        pid.date_time_of_birth = '20000325'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vuorikatu 12', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234573'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='KYS', pl_2='PPKL', pl_3='Triage 2', pl_5='PSSHP')
        pv1.pv1_7 = 'DR503^Hämäläinen^Tuula^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI500004')

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
        orc.placer_order_number = EI(ei_1='ORD500003', ei_2='ACUTE')
        orc.orc_7 = '^^^20260509091000^^S'
        orc.date_time_of_order_event = '20260509091000'
        orc.orc_10 = 'DR503^Hämäläinen^Tuula^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD500003', ei_2='ACUTE')
        obr.universal_service_identifier = CWE(cwe_1='37116-1', cwe_2='CT vatsa', cwe_3='RADLEX')
        obr.observation_date_time = '20260509091000'
        obr.obr_15 = 'DR503^Hämäläinen^Tuula^^^LL^Lääkäri'
        obr.result_status = 'VATSAKIPU^Akuutti vatsakipu'

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
    """ Based on live/fi/fi-vitec-acute.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_RIS')
        msh.sending_facility = HD(hd_1='KYS_RAD')
        msh.receiving_application = HD(hd_1='ACUTE')
        msh.receiving_facility = HD(hd_1='KYS')
        msh.date_time_of_message = '20260509130000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'SECTRA000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT500004', cx_4='KYS', cx_5='MR'), CX(cx_1='250300-123D', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Kokkonen', xpn_2='Aleksi', xpn_3='Petteri', xpn_5='Herra')
        pid.date_time_of_birth = '20000325'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vuorikatu 12', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234573'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='KYS', pl_2='PPKL', pl_3='Triage 2', pl_5='PSSHP')
        pv1.pv1_7 = 'DR503^Hämäläinen^Tuula^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI500004')

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
        orc.placer_order_number = EI(ei_1='ORD500003', ei_2='ACUTE')
        orc.filler_order_number = EI(ei_1='RES500003', ei_2='SECTRA_RIS')
        orc.orc_7 = '^^^20260509091000^^S'
        orc.date_time_of_order_event = '20260509130000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD500003', ei_2='ACUTE')
        obr.filler_order_number = EI(ei_1='RES500003', ei_2='SECTRA_RIS')
        obr.universal_service_identifier = CWE(cwe_1='37116-1', cwe_2='CT vatsa', cwe_3='RADLEX')
        obr.observation_date_time = '20260509100000'
        obr.obr_14 = '20260509100000'
        obr.obr_15 = '^^CT'
        obr.obr_16 = 'DR504^Ruotsalainen^Pasi^^^RAD^Radiologi'
        obr.results_rpt_status_chng_date_time = '20260509130000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2='Diagnostic imaging study', cwe_3='LN')
        obx.obx_5 = 'Vatsan TT: Umpilisäke turvonnut, ympäröivä rasva ödemaattinen. Löydös sopii akuuttiin appendisiittiin.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509130000'

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
        obx_2.date_time_of_the_observation = '20260509130000'

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
    """ Based on live/fi/fi-vitec-acute.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KYSLAB')
        msh.sending_facility = HD(hd_1='PSSHP')
        msh.receiving_application = HD(hd_1='ACUTE')
        msh.receiving_facility = HD(hd_1='KYS')
        msh.date_time_of_message = '20260509094000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'KYSLAB000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT500005', cx_4='KYS', cx_5='MR'), CX(cx_1='120845+456E', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Nousiainen', xpn_2='Aarne', xpn_3='Kalevi', xpn_5='Herra')
        pid.date_time_of_birth = '19450812'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Maaherrankatu 7', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^PH^0172345678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='KYS', pl_2='PPKL', pl_3='Triage 1', pl_5='PSSHP')
        pv1.pv1_7 = 'DR505^Antikainen^Minna^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI500005')

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
        orc.placer_order_number = EI(ei_1='ORD500004', ei_2='ACUTE')
        orc.filler_order_number = EI(ei_1='RES500004', ei_2='KYSLAB')
        orc.orc_7 = '^^^20260509085000^^S'
        orc.date_time_of_order_event = '20260509094000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD500004', ei_2='ACUTE')
        obr.filler_order_number = EI(ei_1='RES500004', ei_2='KYSLAB')
        obr.universal_service_identifier = CWE(cwe_1='24338-6', cwe_2='aB-Verikaasuanalyysi', cwe_3='LN')
        obr.observation_date_time = '20260509090000'
        obr.obr_14 = '20260509090000'
        obr.obr_15 = '^^aB'
        obr.obr_16 = 'DR505^Antikainen^Minna^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509094000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2744-1', cwe_2='aB-pH', cwe_3='LN')
        obx.obx_5 = '7.32'
        obx.units = CWE(cwe_1='kPa')
        obx.reference_range = '7.35-7.45'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509094000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2019-8', cwe_2='aB-pCO2', cwe_3='LN')
        obx_2.obx_5 = '7.2'
        obx_2.units = CWE(cwe_1='kPa')
        obx_2.reference_range = '4.7-6.0'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509094000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2703-7', cwe_2='aB-pO2', cwe_3='LN')
        obx_3.obx_5 = '8.5'
        obx_3.units = CWE(cwe_1='kPa')
        obx_3.reference_range = '11.0-14.4'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509094000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1959-6', cwe_2='aB-HCO3', cwe_3='LN')
        obx_4.obx_5 = '27.2'
        obx_4.units = CWE(cwe_1='mmol/l')
        obx_4.reference_range = '22.0-26.0'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509094000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='1925-7', cwe_2='aB-BE', cwe_3='LN')
        obx_5.obx_5 = '1.8'
        obx_5.units = CWE(cwe_1='mmol/l')
        obx_5.reference_range = '-2.5-2.5'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260509094000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2713-6', cwe_2='aB-SatO2', cwe_3='LN')
        obx_6.obx_5 = '89'
        obx_6.units = CWE(cwe_1='%')
        obx_6.reference_range = '95-100'
        obx_6.interpretation_codes = CWE(cwe_1='L')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260509094000'

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
    """ Based on live/fi/fi-vitec-acute.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ACUTE')
        msh.sending_facility = HD(hd_1='KYS')
        msh.receiving_application = HD(hd_1='CARDIO')
        msh.receiving_facility = HD(hd_1='KYS_FYSI')
        msh.date_time_of_message = '20260509082000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'ACUTE000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT500001', cx_4='KYS', cx_5='MR'), CX(cx_1='200185-234A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Turunen', xpn_2='Ville', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19850120'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Tulliportinkatu 15', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234582'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='KYS', pl_2='PPKL', pl_3='Triage 1', pl_5='PSSHP')
        pv1.pv1_7 = 'DR500^Korhonen^Matti^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI500001')

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
        orc.placer_order_number = EI(ei_1='ORD500005', ei_2='ACUTE')
        orc.orc_7 = '^^^20260509082000^^S'
        orc.date_time_of_order_event = '20260509082000'
        orc.orc_10 = 'DR500^Korhonen^Matti^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD500005', ei_2='ACUTE')
        obr.universal_service_identifier = CWE(cwe_1='89001-4', cwe_2='12-kytkentäinen EKG', cwe_3='LN')
        obr.observation_date_time = '20260509082000'
        obr.relevant_clinical_information = CWE(cwe_1='S')
        obr.obr_15 = 'DR500^Korhonen^Matti^^^LL^Lääkäri'

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
    """ Based on live/fi/fi-vitec-acute.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARDIO')
        msh.sending_facility = HD(hd_1='KYS_FYSI')
        msh.receiving_application = HD(hd_1='ACUTE')
        msh.receiving_facility = HD(hd_1='KYS')
        msh.date_time_of_message = '20260509090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'CARDIO000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT500001', cx_4='KYS', cx_5='MR'), CX(cx_1='200185-234A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Turunen', xpn_2='Ville', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19850120'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Tulliportinkatu 15', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234582'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='KYS', pl_2='PPKL', pl_3='Triage 1', pl_5='PSSHP')
        pv1.pv1_7 = 'DR500^Korhonen^Matti^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI500001')

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
        orc.placer_order_number = EI(ei_1='ORD500005', ei_2='ACUTE')
        orc.filler_order_number = EI(ei_1='RES500005', ei_2='CARDIO')
        orc.orc_7 = '^^^20260509082000^^S'
        orc.date_time_of_order_event = '20260509090000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD500005', ei_2='ACUTE')
        obr.filler_order_number = EI(ei_1='RES500005', ei_2='CARDIO')
        obr.universal_service_identifier = CWE(cwe_1='89001-4', cwe_2='12-kytkentäinen EKG', cwe_3='LN')
        obr.observation_date_time = '20260509083000'
        obr.obr_14 = '20260509083000'
        obr.obr_15 = '^^EKG'
        obr.obr_16 = 'DR506^Tolvanen^Jussi^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509090000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='89001-4', cwe_2='EKG-tulkinta', cwe_3='LN')
        obx.obx_5 = 'Sinusrytmi, frekvenssi 88/min. ST-nousu V1-V4, akuutti anteriorinen STEMI.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509090000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='EKG-tuloste', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKL01hcmtJbmZvIDw8Ci9NYXJrZWQgdHJ1ZQo+PgplbmRvYmoKMiAwIG9iago8PAovVHlw'
            'ZSAvUGFnZXMKL0tpZHMgWzMgMCBSXQovQ291bnQgMQovTWVkaWFCb3ggWzAgMCA4NDIgNTk1XQo+Pgpl'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509090000'

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
    """ Based on live/fi/fi-vitec-acute.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ACUTE')
        msh.sending_facility = HD(hd_1='KYS')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='KYS_HIS')
        msh.date_time_of_message = '20260509095000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02')
        msh.message_control_id = 'ACUTE000008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260509095000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT500001', cx_4='KYS', cx_5='MR'), CX(cx_1='200185-234A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Turunen', xpn_2='Ville', xpn_3='Tapani', xpn_5='Herra')
        pid.date_time_of_birth = '19850120'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Tulliportinkatu 15', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234582'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='KYS', pl_2='PPKL', pl_3='Valvonta 1', pl_5='PSSHP')
        pv1.pv1_7 = 'DR500^Korhonen^Matti^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI500001')
        pv1.pending_location = PL(pl_1='20260509080000')

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/fi/fi-vitec-acute.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KYSLAB')
        msh.sending_facility = HD(hd_1='PSSHP')
        msh.receiving_application = HD(hd_1='ACUTE')
        msh.receiving_facility = HD(hd_1='KYS')
        msh.date_time_of_message = '20260509110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'KYSLAB000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT500006', cx_4='KYS', cx_5='MR'), CX(cx_1='060258-789F', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Rissanen', xpn_2='Sirpa', xpn_3='Anneli', xpn_5='Rouva')
        pid.date_time_of_birth = '19580206'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Kuninkaankatu 19', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^PH^0173456789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='KYS', pl_2='PPKL', pl_3='Triage 3', pl_5='PSSHP')
        pv1.pv1_7 = 'DR507^Ikonen^Jari^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI500006')

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
        orc.placer_order_number = EI(ei_1='ORD500006', ei_2='ACUTE')
        orc.filler_order_number = EI(ei_1='RES500006', ei_2='KYSLAB')
        orc.orc_7 = '^^^20260509093000^^S'
        orc.date_time_of_order_event = '20260509110000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD500006', ei_2='ACUTE')
        obr.filler_order_number = EI(ei_1='RES500006', ei_2='KYSLAB')
        obr.universal_service_identifier = CWE(cwe_1='24326-1', cwe_2='Elektrolyytit', cwe_3='LN')
        obr.observation_date_time = '20260509094000'
        obr.obr_14 = '20260509094000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR507^Ikonen^Jari^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509110000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2947-0', cwe_2='fP-Na', cwe_3='LN')
        obx.obx_5 = '128'
        obx.units = CWE(cwe_1='mmol/l')
        obx.reference_range = '137-145'
        obx.interpretation_codes = CWE(cwe_1='LL')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509110000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6298-4', cwe_2='fP-K', cwe_3='LN')
        obx_2.obx_5 = '5.8'
        obx_2.units = CWE(cwe_1='mmol/l')
        obx_2.reference_range = '3.5-5.0'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509110000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2160-0', cwe_2='fP-Krea', cwe_3='LN')
        obx_3.obx_5 = '165'
        obx_3.units = CWE(cwe_1='umol/l')
        obx_3.reference_range = '50-90'
        obx_3.interpretation_codes = CWE(cwe_1='HH')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509110000'

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
    """ Based on live/fi/fi-vitec-acute.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ACUTE')
        msh.sending_facility = HD(hd_1='KYS')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='KYS_HIS')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'ACUTE000009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT500004', cx_4='KYS', cx_5='MR'), CX(cx_1='250300-123D', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Kokkonen', xpn_2='Aleksi', xpn_3='Petteri', xpn_5='Herra')
        pid.date_time_of_birth = '20000325'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vuorikatu 12', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234573'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='KYS', pl_2='PPKL', pl_3='Triage 2', pl_5='PSSHP')
        pv1.pv1_7 = 'DR503^Hämäläinen^Tuula^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI500004')

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
        orc.placer_order_number = EI(ei_1='ORD500007', ei_2='ACUTE')
        orc.orc_7 = '^^^20260509100000^^S'
        orc.date_time_of_order_event = '20260509100000'
        orc.orc_10 = 'DR503^Hämäläinen^Tuula^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD500007', ei_2='ACUTE')
        obr.universal_service_identifier = CWE(cwe_1='KONS', cwe_2='Konsultaatio, kirurgia', cwe_3='KYS')
        obr.observation_date_time = '20260509100000'
        obr.obr_15 = 'DR503^Hämäläinen^Tuula^^^LL^Lääkäri'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Akuutti appendisiittiepäily. TT-löydös sopiva. Pyydän kirurgin arviota leikkausaiheesta.'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.nte = nte

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
    """ Based on live/fi/fi-vitec-acute.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KYSLAB')
        msh.sending_facility = HD(hd_1='PSSHP')
        msh.receiving_application = HD(hd_1='ACUTE')
        msh.receiving_facility = HD(hd_1='KYS')
        msh.date_time_of_message = '20260509084000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'KYSLAB000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT500007', cx_4='KYS', cx_5='MR'), CX(cx_1='190740+012G', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Väänänen', xpn_2='Eero', xpn_3='Kalevi', xpn_5='Herra')
        pid.date_time_of_birth = '19400719'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Satamakatu 4', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^PH^0174567890'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='KYS', pl_2='PPKL', pl_3='Triage 1', pl_5='PSSHP')
        pv1.pv1_7 = 'DR508^Partanen^Anu^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI500007')

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
        orc.placer_order_number = EI(ei_1='ORD500008', ei_2='ACUTE')
        orc.filler_order_number = EI(ei_1='RES500008', ei_2='KYSLAB')
        orc.orc_7 = '^^^20260509082500^^S'
        orc.date_time_of_order_event = '20260509084000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD500008', ei_2='ACUTE')
        obr.filler_order_number = EI(ei_1='RES500008', ei_2='KYSLAB')
        obr.universal_service_identifier = CWE(cwe_1='14879-1', cwe_2='cB-Gluk', cwe_3='LN')
        obr.observation_date_time = '20260509083000'
        obr.obr_14 = '20260509083000'
        obr.obr_15 = '^^cB'
        obr.obr_16 = 'DR508^Partanen^Anu^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509084000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='14879-1', cwe_2='cB-Gluk', cwe_3='LN')
        obx.obx_5 = '2.1'
        obx.units = CWE(cwe_1='mmol/l')
        obx.reference_range = '4.0-6.0'
        obx.interpretation_codes = CWE(cwe_1='LL')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509084000'

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
    """ Based on live/fi/fi-vitec-acute.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ACUTE')
        msh.sending_facility = HD(hd_1='KYS')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='KYS_HIS')
        msh.date_time_of_message = '20260509085000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31')
        msh.message_control_id = 'ACUTE000010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20260509085000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT500008', cx_4='KYS', cx_5='MR'), CX(cx_1='010202-234H', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Miettinen', xpn_2='Emilia', xpn_3='Sofia', xpn_5='Neiti')
        pid.date_time_of_birth = '20020201'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Asemakatu 10', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234583'

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
    """ Based on live/fi/fi-vitec-acute.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KYSLAB')
        msh.sending_facility = HD(hd_1='PSSHP')
        msh.receiving_application = HD(hd_1='ACUTE')
        msh.receiving_facility = HD(hd_1='KYS')
        msh.date_time_of_message = '20260509112000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'KYSLAB000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT500009', cx_4='KYS', cx_5='MR'), CX(cx_1='080580-678J', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Pesonen', xpn_2='Juha', xpn_3='Matti', xpn_5='Herra')
        pid.date_time_of_birth = '19800508'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Niiralankatu 3', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^CP^0407654330'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='KYS', pl_2='PPKL', pl_3='Triage 2', pl_5='PSSHP')
        pv1.pv1_7 = 'DR509^Laukkanen^Sirkka^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI500009')

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
        orc.placer_order_number = EI(ei_1='ORD500009', ei_2='ACUTE')
        orc.filler_order_number = EI(ei_1='RES500009', ei_2='KYSLAB')
        orc.orc_7 = '^^^20260509100000^^S'
        orc.date_time_of_order_event = '20260509112000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD500009', ei_2='ACUTE')
        obr.filler_order_number = EI(ei_1='RES500009', ei_2='KYSLAB')
        obr.universal_service_identifier = CWE(cwe_1='5640-8', cwe_2='S-Etanoli', cwe_3='LN')
        obr.observation_date_time = '20260509101000'
        obr.obr_14 = '20260509101000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR509^Laukkanen^Sirkka^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509112000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5640-8', cwe_2='S-Etanoli', cwe_3='LN')
        obx.obx_5 = '1.8'
        obx.units = CWE(cwe_1='promille')
        obx.reference_range = '0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509112000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='43984-6', cwe_2='U-HuumeSeul', cwe_3='LN')
        obx_2.obx_5 = 'Bentsodiatsepiinit positiivinen, muut negatiiviset'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509112000'

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
    """ Based on live/fi/fi-vitec-acute.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ACUTE')
        msh.sending_facility = HD(hd_1='KYS')
        msh.receiving_application = HD(hd_1='KYSLAB_VP')
        msh.receiving_facility = HD(hd_1='PSSHP')
        msh.date_time_of_message = '20260509093000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'ACUTE000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT500010', cx_4='KYS', cx_5='MR'), CX(cx_1='150265-901K', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Keinänen', xpn_2='Eila', xpn_3='Marjatta', xpn_5='Rouva')
        pid.date_time_of_birth = '19650215'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Hapelähteenkatu 14', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^CP^0409876551'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='KYS', pl_2='PPKL', pl_3='Triage 1', pl_5='PSSHP')
        pv1.pv1_7 = 'DR510^Mustonen^Pekka^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI500010')

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
        orc.placer_order_number = EI(ei_1='ORD500010', ei_2='ACUTE')
        orc.orc_7 = '^^^20260509093000^^S'
        orc.date_time_of_order_event = '20260509093000'
        orc.orc_10 = 'DR510^Mustonen^Pekka^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD500010', ei_2='ACUTE')
        obr.universal_service_identifier = CWE(cwe_1='1305', cwe_2='E-ABORh', cwe_3='KYSLAB_VP')
        obr.observation_date_time = '20260509093000'
        obr.relevant_clinical_information = CWE(cwe_1='S')
        obr.obr_15 = 'DR510^Mustonen^Pekka^^^LL^Lääkäri'

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
        obr_2.placer_order_number = EI(ei_1='ORD500010', ei_2='ACUTE')
        obr_2.universal_service_identifier = CWE(cwe_1='SOPIVUUS', cwe_2='E-X-koe', cwe_3='KYSLAB_VP')
        obr_2.observation_date_time = '20260509093000'
        obr_2.relevant_clinical_information = CWE(cwe_1='S')
        obr_2.obr_15 = 'DR510^Mustonen^Pekka^^^LL^Lääkäri'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2]

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
    """ Based on live/fi/fi-vitec-acute.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KYSLAB')
        msh.sending_facility = HD(hd_1='PSSHP')
        msh.receiving_application = HD(hd_1='ACUTE')
        msh.receiving_facility = HD(hd_1='KYS')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'KYSLAB000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT500011', cx_4='KYS', cx_5='MR'), CX(cx_1='031155+234L', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Huttunen', xpn_2='Taisto', xpn_3='Olavi', xpn_5='Herra')
        pid.date_time_of_birth = '19551103'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kauppakatu 40', xad_3='Kuopio', xad_5='70100', xad_6='FIN')
        pid.pid_13 = '^^PH^0175678901'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='KYS', pl_2='PPKL', pl_3='Triage 1', pl_5='PSSHP')
        pv1.pv1_7 = 'DR511^Väisänen^Kirsi^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI500011')

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
        orc.placer_order_number = EI(ei_1='ORD500011', ei_2='ACUTE')
        orc.filler_order_number = EI(ei_1='RES500011', ei_2='KYSLAB')
        orc.orc_7 = '^^^20260509091000^^S'
        orc.date_time_of_order_event = '20260509100000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD500011', ei_2='ACUTE')
        obr.filler_order_number = EI(ei_1='RES500011', ei_2='KYSLAB')
        obr.universal_service_identifier = CWE(cwe_1='2524-7', cwe_2='P-Laktaatti', cwe_3='LN')
        obr.observation_date_time = '20260509092000'
        obr.obr_14 = '20260509092000'
        obr.obr_15 = '^^P'
        obr.obr_16 = 'DR511^Väisänen^Kirsi^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509100000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2524-7', cwe_2='P-Laktaatti', cwe_3='LN')
        obx.obx_5 = '4.8'
        obx.units = CWE(cwe_1='mmol/l')
        obx.reference_range = '0.5-2.2'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509100000'

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
