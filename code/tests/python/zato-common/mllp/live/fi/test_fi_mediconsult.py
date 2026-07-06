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
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A03, ADT_A05, ADT_A39, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIP, AIS, EVN, IN1, MRG, MSH, NK1, NTE, OBR, OBX, ORC, PID, PV1, PV2, RGS, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('fi', 'fi-mediconsult.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/fi/fi-mediconsult.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDIATRI')
        msh.sending_facility = HD(hd_1='JYVASKYLA_TK')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260509080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04')
        msh.message_control_id = 'MEDI000001'
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
        pid.patient_identifier_list = [CX(cx_1='PT700001', cx_4='JYTK', cx_5='MR'), CX(cx_1='120385-234A', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Penttinen', xpn_2='Marko', xpn_3='Juhani', xpn_5='Herra')
        pid.date_time_of_birth = '19850312'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kauppakatu 28', xad_3='Jyväskylä', xad_5='40100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234588'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='JYTK', pl_2='YLEIS1', pl_3='Vastaanottohuone 3', pl_5='KSSHP')
        pv1.pv1_7 = 'DR700^Aalto^Kirsi^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI700001')
        pv1.pending_location = PL(pl_1='20260509080000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='KELA')
        in1.insurance_company_id = CX(cx_1='700001')
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
    """ Based on live/fi/fi-mediconsult.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDIATRI')
        msh.sending_facility = HD(hd_1='JYVASKYLA_TK')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        msh.message_control_id = 'MEDI000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260509100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT700002', cx_4='JYTK', cx_5='MR'), CX(cx_1='050340+567B', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Koivula', xpn_2='Helmi', xpn_3='Inkeri', xpn_5='Rouva')
        pid.date_time_of_birth = '19400305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Väinönkatu 14', xad_3='Jyväskylä', xad_5='40100', xad_6='FIN')
        pid.pid_13 = '^^PH^0141234567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='JYTK', pl_2='VUODE1', pl_3='Huone 105', pl_4='Vuode 2', pl_6='KSSHP')
        pv1.pv1_7 = 'DR701^Lahtinen^Jari^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO700001')
        pv1.pending_location = PL(pl_1='20260509100000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Lonkkamurtuman jatkohoito')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='FENNIA')
        in1.insurance_company_id = CX(cx_1='700002')
        in1.insurance_company_name = XON(xon_1='Fennia Vakuutus')
        in1.insurance_company_address = XAD(xad_1='Kyllikinportti 2', xad_3='Helsinki', xad_5='00240', xad_6='FIN')

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
    """ Based on live/fi/fi-mediconsult.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDIATRI')
        msh.sending_facility = HD(hd_1='JYVASKYLA_TK')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260520140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03')
        msh.message_control_id = 'MEDI000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260520140000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT700002', cx_4='JYTK', cx_5='MR'), CX(cx_1='050340+567B', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Koivula', xpn_2='Helmi', xpn_3='Inkeri', xpn_5='Rouva')
        pid.date_time_of_birth = '19400305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Väinönkatu 14', xad_3='Jyväskylä', xad_5='40100', xad_6='FIN')
        pid.pid_13 = '^^PH^0141234567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='JYTK', pl_2='VUODE1', pl_3='Huone 105', pl_4='Vuode 2', pl_6='KSSHP')
        pv1.pv1_7 = 'DR701^Lahtinen^Jari^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO700001')
        pv1.pending_location = PL(pl_1='20260509100000')
        pv1.prior_temporary_location = PL(pl_1='20260520140000')

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
    """ Based on live/fi/fi-mediconsult.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDIATRI')
        msh.sending_facility = HD(hd_1='JYVASKYLA_TK')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260509110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08')
        msh.message_control_id = 'MEDI000004'
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
        pid.patient_identifier_list = [CX(cx_1='PT700003', cx_4='JYTK', cx_5='MR'), CX(cx_1='190775-890C', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Hämäläinen', xpn_2='Sirpa', xpn_3='Marjatta', xpn_5='Rouva')
        pid.date_time_of_birth = '19750719'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Yliopistonkatu 10', xad_3='Jyväskylä', xad_5='40100', xad_6='FIN')
        pid.pid_13 = '^^CP^0509876553'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='JYTK', pl_2='YLEIS2', pl_3='Vastaanottohuone 5', pl_5='KSSHP')
        pv1.pv1_7 = 'DR702^Mäkinen^Ulla^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI700002')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Hämäläinen', xpn_2='Juha')
        nk1.address = XAD(xad_3='CP', xad_4='0509876554')
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
    """ Based on live/fi/fi-mediconsult.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDIATRI')
        msh.sending_facility = HD(hd_1='JYVASKYLA_TK')
        msh.receiving_application = HD(hd_1='VRK')
        msh.receiving_facility = HD(hd_1='DVV')
        msh.date_time_of_message = '20260509120000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31')
        msh.message_control_id = 'MEDI000005'
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
        pid.patient_identifier_list = [CX(cx_1='PT700004', cx_4='JYTK', cx_5='MR'), CX(cx_1='010200-123D', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Kinnunen', xpn_2='Eemeli', xpn_3='Petteri', xpn_5='Herra')
        pid.date_time_of_birth = '20000201'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Hannikaisenkatu 22', xad_3='Jyväskylä', xad_5='40100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234589'

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
    """ Based on live/fi/fi-mediconsult.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDIATRI')
        msh.sending_facility = HD(hd_1='JYVASKYLA_TK')
        msh.receiving_application = HD(hd_1='FIMLAB')
        msh.receiving_facility = HD(hd_1='KSSHP')
        msh.date_time_of_message = '20260509083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MEDI000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT700005', cx_4='JYTK', cx_5='MR'), CX(cx_1='280460-345E', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Laine', xpn_2='Reijo', xpn_3='Olavi', xpn_5='Herra')
        pid.date_time_of_birth = '19600428'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kilpisenkatu 5', xad_3='Jyväskylä', xad_5='40100', xad_6='FIN')
        pid.pid_13 = '^^PH^0142345678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='JYTK', pl_2='YLEIS1', pl_3='Vastaanottohuone 3', pl_5='KSSHP')
        pv1.pv1_7 = 'DR700^Aalto^Kirsi^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI700003')

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
        orc.placer_order_number = EI(ei_1='ORD700001', ei_2='MEDIATRI')
        orc.orc_7 = '^^^20260509083000^^R'
        orc.date_time_of_order_event = '20260509083000'
        orc.orc_10 = 'DR700^Aalto^Kirsi^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700001', ei_2='MEDIATRI')
        obr.universal_service_identifier = CWE(cwe_1='4587', cwe_2='fP-Gluk', cwe_3='FIMLAB')
        obr.observation_date_time = '20260509083000'
        obr.obr_15 = 'DR700^Aalto^Kirsi^^^LL^Lääkäri'

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
        obr_2.placer_order_number = EI(ei_1='ORD700001', ei_2='MEDIATRI')
        obr_2.universal_service_identifier = CWE(cwe_1='4480', cwe_2='B-HbA1c', cwe_3='FIMLAB')
        obr_2.observation_date_time = '20260509083000'
        obr_2.obr_15 = 'DR700^Aalto^Kirsi^^^LL^Lääkäri'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='ORD700001', ei_2='MEDIATRI')
        obr_3.universal_service_identifier = CWE(cwe_1='4600', cwe_2='fP-Kol', cwe_3='FIMLAB')
        obr_3.observation_date_time = '20260509083000'
        obr_3.obr_15 = 'DR700^Aalto^Kirsi^^^LL^Lääkäri'

        # .. build OBR ..
        obr_4 = OBR()
        obr_4.set_id_obr = '4'
        obr_4.placer_order_number = EI(ei_1='ORD700001', ei_2='MEDIATRI')
        obr_4.universal_service_identifier = CWE(cwe_1='4520', cwe_2='P-CRP', cwe_3='FIMLAB')
        obr_4.observation_date_time = '20260509083000'
        obr_4.obr_15 = 'DR700^Aalto^Kirsi^^^LL^Lääkäri'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3, obr_4]

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
    """ Based on live/fi/fi-mediconsult.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FIMLAB')
        msh.sending_facility = HD(hd_1='KSSHP')
        msh.receiving_application = HD(hd_1='MEDIATRI')
        msh.receiving_facility = HD(hd_1='JYVASKYLA_TK')
        msh.date_time_of_message = '20260509140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'FIMLAB000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT700005', cx_4='JYTK', cx_5='MR'), CX(cx_1='280460-345E', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Laine', xpn_2='Reijo', xpn_3='Olavi', xpn_5='Herra')
        pid.date_time_of_birth = '19600428'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kilpisenkatu 5', xad_3='Jyväskylä', xad_5='40100', xad_6='FIN')
        pid.pid_13 = '^^PH^0142345678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='JYTK', pl_2='YLEIS1', pl_3='Vastaanottohuone 3', pl_5='KSSHP')
        pv1.pv1_7 = 'DR700^Aalto^Kirsi^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI700003')

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
        orc.placer_order_number = EI(ei_1='ORD700001', ei_2='MEDIATRI')
        orc.filler_order_number = EI(ei_1='RES700001', ei_2='FIMLAB')
        orc.orc_7 = '^^^20260509083000^^R'
        orc.date_time_of_order_event = '20260509140000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700001', ei_2='MEDIATRI')
        obr.filler_order_number = EI(ei_1='RES700001', ei_2='FIMLAB')
        obr.universal_service_identifier = CWE(cwe_1='4587', cwe_2='fP-Gluk', cwe_3='FIMLAB')
        obr.observation_date_time = '20260509090000'
        obr.obr_14 = '20260509090000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR700^Aalto^Kirsi^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='14879-1', cwe_2='fP-Gluk', cwe_3='LN')
        obx.obx_5 = '8.2'
        obx.units = CWE(cwe_1='mmol/l')
        obx.reference_range = '4.0-6.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4548-4', cwe_2='B-HbA1c', cwe_3='LN')
        obx_2.obx_5 = '62'
        obx_2.units = CWE(cwe_1='mmol/mol')
        obx_2.reference_range = '<42'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2093-3', cwe_2='fP-Kol', cwe_3='LN')
        obx_3.obx_5 = '6.1'
        obx_3.units = CWE(cwe_1='mmol/l')
        obx_3.reference_range = '<5.0'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509140000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4520', cwe_2='P-CRP', cwe_3='FIMLAB')
        obx_4.obx_5 = '2'
        obx_4.units = CWE(cwe_1='mg/l')
        obx_4.reference_range = '<3'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509140000'

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
    """ Based on live/fi/fi-mediconsult.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDIATRI')
        msh.sending_facility = HD(hd_1='JYVASKYLA_TK')
        msh.receiving_application = HD(hd_1='MEDIATRI_SCHED')
        msh.receiving_facility = HD(hd_1='KSSHP')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12')
        msh.message_control_id = 'MEDI000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT700001')
        sch.filler_appointment_id = EI(ei_1='APT700001')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_2='Normaali', cwe_3='HL70276')
        sch.appointment_reason = CWE(cwe_1='FOLLOWUP', cwe_2='Kontrollikäynti', cwe_3='HL70277')
        sch.appointment_type = CWE(cwe_1='DOCTOR', cwe_2='Lääkärin vastaanotto')
        sch.sch_9 = '20'
        sch.appointment_duration_units = CNE(cne_1='min')
        sch.sch_11 = '^^^20260523093000^20260523095000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT700005', cx_4='JYTK', cx_5='MR'), CX(cx_1='280460-345E', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Laine', xpn_2='Reijo', xpn_3='Olavi', xpn_5='Herra')
        pid.date_time_of_birth = '19600428'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kilpisenkatu 5', xad_3='Jyväskylä', xad_5='40100', xad_6='FIN')
        pid.pid_13 = '^^PH^0142345678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='JYTK', pl_2='YLEIS1', pl_3='Vastaanottohuone 3', pl_5='KSSHP')
        pv1.pv1_7 = 'DR700^Aalto^Kirsi^^^LL^Lääkäri'

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
        ais.universal_service_identifier = CWE(cwe_1='YLEISLAAK', cwe_2='Yleislääkärin vastaanotto', cwe_3='MEDIATRI')
        ais.start_date_time = '20260523093000'
        ais.start_date_time_offset = '20'
        ais.start_date_time_offset_units = CNE(cne_1='min')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.aip_3 = 'DR700^Aalto^Kirsi^^^LL^Lääkäri'

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
    """ Based on live/fi/fi-mediconsult.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDIATRI')
        msh.sending_facility = HD(hd_1='JYVASKYLA_TK')
        msh.receiving_application = HD(hd_1='MEDIATRI_SCHED')
        msh.receiving_facility = HD(hd_1='KSSHP')
        msh.date_time_of_message = '20260512080000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S14')
        msh.message_control_id = 'MEDI000008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT700001')
        sch.filler_appointment_id = EI(ei_1='APT700001')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_2='Normaali', cwe_3='HL70276')
        sch.appointment_reason = CWE(cwe_1='FOLLOWUP', cwe_2='Kontrollikäynti', cwe_3='HL70277')
        sch.appointment_type = CWE(cwe_1='DOCTOR', cwe_2='Lääkärin vastaanotto')
        sch.sch_9 = '20'
        sch.appointment_duration_units = CNE(cne_1='min')
        sch.sch_11 = '^^^20260526093000^20260526095000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT700005', cx_4='JYTK', cx_5='MR'), CX(cx_1='280460-345E', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Laine', xpn_2='Reijo', xpn_3='Olavi', xpn_5='Herra')
        pid.date_time_of_birth = '19600428'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kilpisenkatu 5', xad_3='Jyväskylä', xad_5='40100', xad_6='FIN')
        pid.pid_13 = '^^PH^0142345678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='JYTK', pl_2='YLEIS1', pl_3='Vastaanottohuone 3', pl_5='KSSHP')
        pv1.pv1_7 = 'DR700^Aalto^Kirsi^^^LL^Lääkäri'

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
        ais.universal_service_identifier = CWE(cwe_1='YLEISLAAK', cwe_2='Yleislääkärin vastaanotto', cwe_3='MEDIATRI')
        ais.start_date_time = '20260526093000'
        ais.start_date_time_offset = '20'
        ais.start_date_time_offset_units = CNE(cne_1='min')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.aip_3 = 'DR700^Aalto^Kirsi^^^LL^Lääkäri'

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
    """ Based on live/fi/fi-mediconsult.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDIATRI')
        msh.sending_facility = HD(hd_1='JYVASKYLA_TK')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260509150000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02')
        msh.message_control_id = 'MEDI000009'
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
        pid.patient_identifier_list = [CX(cx_1='PT700005', cx_4='JYTK', cx_5='MR'), CX(cx_1='280460-345E', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Laine', xpn_2='Reijo', xpn_3='Olavi', xpn_5='Herra')
        pid.date_time_of_birth = '19600428'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kilpisenkatu 5', xad_3='Jyväskylä', xad_5='40100', xad_6='FIN')
        pid.pid_13 = '^^PH^0142345678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='JYTK', pl_2='YLEIS1', pl_3='Vastaanottohuone 3', pl_5='KSSHP')
        pv1.pv1_7 = 'DR700^Aalto^Kirsi^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI700003')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='HP', cwe_2='Vastaanottokäynti')
        txa.document_content_presentation = 'TX'
        txa.origination_date_time = '20260509150000'
        txa.unique_document_number = EI(ei_1='DOC700001')
        txa.unique_document_file_name = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='11506-3', cwe_2='Progress note', cwe_3='LN')
        obx.obx_5 = 'Diabetes kontrollissa. HbA1c noussut, lääkityksen tehostus metformiinin annosta nostamalla. Elämäntapaohjaus annettu.'
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
    """ Based on live/fi/fi-mediconsult.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDIATRI')
        msh.sending_facility = HD(hd_1='JYVASKYLA_TK')
        msh.receiving_application = HD(hd_1='LIFECARE')
        msh.receiving_facility = HD(hd_1='KSKS')
        msh.date_time_of_message = '20260509141000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MEDI000010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT700006', cx_4='JYTK', cx_5='MR'), CX(cx_1='100590-678F', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Saarinen', xpn_2='Matti', xpn_3='Kalevi', xpn_5='Herra')
        pid.date_time_of_birth = '19900510'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vapaudenkatu 60', xad_3='Jyväskylä', xad_5='40100', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234576'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='JYTK', pl_2='YLEIS2', pl_3='Vastaanottohuone 5', pl_5='KSSHP')
        pv1.pv1_7 = 'DR702^Mäkinen^Ulla^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI700004')

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
        orc.placer_order_number = EI(ei_1='ORD700002', ei_2='MEDIATRI')
        orc.orc_7 = '^^^20260509141000^^R'
        orc.date_time_of_order_event = '20260509141000'
        orc.orc_10 = 'DR702^Mäkinen^Ulla^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700002', ei_2='MEDIATRI')
        obr.universal_service_identifier = CWE(cwe_1='LAHETE', cwe_2='Lähete, kardiologia', cwe_3='MEDIATRI')
        obr.observation_date_time = '20260509141000'
        obr.obr_15 = 'DR702^Mäkinen^Ulla^^^LL^Lääkäri'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Potilaalla rasituksessa ilmenevää rintakipua. Rasitus-EKG epänormaali. Pyydän kardiologin arviota.'

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
    """ Based on live/fi/fi-mediconsult.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FIMLAB')
        msh.sending_facility = HD(hd_1='KSSHP')
        msh.receiving_application = HD(hd_1='MEDIATRI')
        msh.receiving_facility = HD(hd_1='JYVASKYLA_TK')
        msh.date_time_of_message = '20260509143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'FIMLAB000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT700007', cx_4='JYTK', cx_5='MR'), CX(cx_1='150268-901G', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Karjalainen', xpn_2='Raija', xpn_3='Anneli', xpn_5='Rouva')
        pid.date_time_of_birth = '19680215'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Puistokatu 15', xad_3='Jyväskylä', xad_5='40100', xad_6='FIN')
        pid.pid_13 = '^^CP^0407654333'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='JYTK', pl_2='YLEIS3', pl_3='Vastaanottohuone 7', pl_5='KSSHP')
        pv1.pv1_7 = 'DR703^Heikkinen^Pekka^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI700005')

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
        orc.placer_order_number = EI(ei_1='ORD700003', ei_2='MEDIATRI')
        orc.filler_order_number = EI(ei_1='RES700003', ei_2='FIMLAB')
        orc.orc_7 = '^^^20260509090000^^R'
        orc.date_time_of_order_event = '20260509143000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700003', ei_2='MEDIATRI')
        obr.filler_order_number = EI(ei_1='RES700003', ei_2='FIMLAB')
        obr.universal_service_identifier = CWE(cwe_1='2741', cwe_2='B-PVK+T', cwe_3='FIMLAB')
        obr.observation_date_time = '20260509091000'
        obr.obr_14 = '20260509091000'
        obr.obr_15 = '^^B'
        obr.obr_16 = 'DR703^Heikkinen^Pekka^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6768', cwe_2='B-Leuk', cwe_3='FIMLAB')
        obx.obx_5 = '6.2'
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
        obx_2.observation_identifier = CWE(cwe_1='2171', cwe_2='B-Eryt', cwe_3='FIMLAB')
        obx_2.obx_5 = '3.85'
        obx_2.units = CWE(cwe_1='10E12/l')
        obx_2.reference_range = '3.90-5.20'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509143000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='1552', cwe_2='B-Hb', cwe_3='FIMLAB')
        obx_3.obx_5 = '118'
        obx_3.units = CWE(cwe_1='g/l')
        obx_3.reference_range = '117-155'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509143000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2798', cwe_2='B-Trom', cwe_3='FIMLAB')
        obx_4.obx_5 = '275'
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
    """ Based on live/fi/fi-mediconsult.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FIMLAB')
        msh.sending_facility = HD(hd_1='KSSHP')
        msh.receiving_application = HD(hd_1='MEDIATRI')
        msh.receiving_facility = HD(hd_1='JYVASKYLA_TK')
        msh.date_time_of_message = '20260509150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'FIMLAB000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT700008', cx_4='JYTK', cx_5='MR'), CX(cx_1='220578-123H', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Toivonen', xpn_2='Elina', xpn_3='Marjatta', xpn_5='Rouva')
        pid.date_time_of_birth = '19780522'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Seminaarinkatu 30', xad_3='Jyväskylä', xad_5='40100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234590'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='JYTK', pl_2='YLEIS2', pl_3='Vastaanottohuone 5', pl_5='KSSHP')
        pv1.pv1_7 = 'DR702^Mäkinen^Ulla^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI700006')

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
        orc.placer_order_number = EI(ei_1='ORD700004', ei_2='MEDIATRI')
        orc.filler_order_number = EI(ei_1='RES700004', ei_2='FIMLAB')
        orc.orc_7 = '^^^20260509083000^^R'
        orc.date_time_of_order_event = '20260509150000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700004', ei_2='MEDIATRI')
        obr.filler_order_number = EI(ei_1='RES700004', ei_2='FIMLAB')
        obr.universal_service_identifier = CWE(cwe_1='4832', cwe_2='S-TSH', cwe_3='FIMLAB')
        obr.observation_date_time = '20260509085000'
        obr.obr_14 = '20260509085000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR702^Mäkinen^Ulla^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='S-TSH', cwe_3='LN')
        obx.obx_5 = '8.5'
        obx.units = CWE(cwe_1='mU/l')
        obx.reference_range = '0.27-4.20'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509150000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3024-7', cwe_2='S-T4V', cwe_3='LN')
        obx_2.obx_5 = '9.2'
        obx_2.units = CWE(cwe_1='pmol/l')
        obx_2.reference_range = '11.0-22.0'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509150000'

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
    """ Based on live/fi/fi-mediconsult.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FIMLAB')
        msh.sending_facility = HD(hd_1='KSSHP')
        msh.receiving_application = HD(hd_1='MEDIATRI')
        msh.receiving_facility = HD(hd_1='JYVASKYLA_TK')
        msh.date_time_of_message = '20260509160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'FIMLAB000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT700009', cx_4='JYTK', cx_5='MR'), CX(cx_1='030450+234J', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Pietilä', xpn_2='Eino', xpn_3='Olavi', xpn_5='Herra')
        pid.date_time_of_birth = '19500403'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Asemakatu 7', xad_3='Jyväskylä', xad_5='40100', xad_6='FIN')
        pid.pid_13 = '^^PH^0143456789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='JYTK', pl_2='VUODE1', pl_3='Huone 108', pl_4='Vuode 1', pl_6='KSSHP')
        pv1.pv1_7 = 'DR701^Lahtinen^Jari^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='HOITO700002')

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
        orc.placer_order_number = EI(ei_1='ORD700005', ei_2='MEDIATRI')
        orc.filler_order_number = EI(ei_1='RES700005', ei_2='FIMLAB')
        orc.orc_7 = '^^^20260508090000^^R'
        orc.date_time_of_order_event = '20260509160000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700005', ei_2='MEDIATRI')
        obr.filler_order_number = EI(ei_1='RES700005', ei_2='FIMLAB')
        obr.universal_service_identifier = CWE(cwe_1='1155', cwe_2='Pu-BaktVi', cwe_3='FIMLAB')
        obr.observation_date_time = '20260508091000'
        obr.obr_14 = '20260508091000'
        obr.obr_15 = '^^PU'
        obr.obr_16 = 'DR701^Lahtinen^Jari^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='1155', cwe_2='Pu-BaktVi', cwe_3='FIMLAB')
        obx.obx_5 = 'SAUR^Staphylococcus aureus^FIMLAB'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='ABRES', cwe_2='Herkkyys', cwe_3='FIMLAB')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = 'Oksasilliini S, Klindamysiini S, Vankomysiini S, Trimetopriimi-sulfametoksatsoli S'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509160000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ED'
        obx_3.observation_identifier = CWE(cwe_1='PDF', cwe_2='Mikrobiologinen lausunto', cwe_3='L')
        obx_3.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK'
        )
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509160000'

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
    """ Based on live/fi/fi-mediconsult.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDIATRI')
        msh.sending_facility = HD(hd_1='JYVASKYLA_TK')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260509130000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40')
        msh.message_control_id = 'MEDI000011'
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
        pid.patient_identifier_list = CX(cx_1='PT700010', cx_4='JYTK', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Mäkinen', xpn_2='Ritva', xpn_3='Helena', xpn_5='Rouva')
        pid.date_time_of_birth = '19620818'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Kalevankatu 3', xad_3='Jyväskylä', xad_5='40100', xad_6='FIN')
        pid.pid_13 = '^^PH^0144567890'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='PT700099', cx_4='JYTK', cx_5='MR')

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
    """ Based on live/fi/fi-mediconsult.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FIMLAB')
        msh.sending_facility = HD(hd_1='KSSHP')
        msh.receiving_application = HD(hd_1='MEDIATRI')
        msh.receiving_facility = HD(hd_1='JYVASKYLA_TK')
        msh.date_time_of_message = '20260509152000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'FIMLAB000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT700011', cx_4='JYTK', cx_5='MR'), CX(cx_1='120560-567K', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Niskanen', xpn_2='Pertti', xpn_3='Antero', xpn_5='Herra')
        pid.date_time_of_birth = '19600512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Voionmaankatu 20', xad_3='Jyväskylä', xad_5='40100', xad_6='FIN')
        pid.pid_13 = '^^CP^0407654334'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='JYTK', pl_2='YLEIS3', pl_3='Vastaanottohuone 7', pl_5='KSSHP')
        pv1.pv1_7 = 'DR703^Heikkinen^Pekka^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI700007')

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
        orc.placer_order_number = EI(ei_1='ORD700006', ei_2='MEDIATRI')
        orc.filler_order_number = EI(ei_1='RES700006', ei_2='FIMLAB')
        orc.orc_7 = '^^^20260509090000^^R'
        orc.date_time_of_order_event = '20260509152000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700006', ei_2='MEDIATRI')
        obr.filler_order_number = EI(ei_1='RES700006', ei_2='FIMLAB')
        obr.universal_service_identifier = CWE(cwe_1='2857-1', cwe_2='S-PSA', cwe_3='LN')
        obr.observation_date_time = '20260509091500'
        obr.obr_14 = '20260509091500'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR703^Heikkinen^Pekka^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509152000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2857-1', cwe_2='S-PSA', cwe_3='LN')
        obx.obx_5 = '2.8'
        obx.units = CWE(cwe_1='ug/l')
        obx.reference_range = '<4.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509152000'

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
    """ Based on live/fi/fi-mediconsult.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FIMLAB')
        msh.sending_facility = HD(hd_1='KSSHP')
        msh.receiving_application = HD(hd_1='MEDIATRI')
        msh.receiving_facility = HD(hd_1='JYVASKYLA_TK')
        msh.date_time_of_message = '20260509155000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'FIMLAB000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT700012', cx_4='JYTK', cx_5='MR'), CX(cx_1='180375-890L', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Rantala', xpn_2='Tuula', xpn_3='Kristiina', xpn_5='Rouva')
        pid.date_time_of_birth = '19750318'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rajakatu 12', xad_3='Jyväskylä', xad_5='40200', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234591'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='JYTK', pl_2='YLEIS1', pl_3='Vastaanottohuone 3', pl_5='KSSHP')
        pv1.pv1_7 = 'DR700^Aalto^Kirsi^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI700008')

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
        orc.placer_order_number = EI(ei_1='ORD700007', ei_2='MEDIATRI')
        orc.filler_order_number = EI(ei_1='RES700007', ei_2='FIMLAB')
        orc.orc_7 = '^^^20260509083000^^R'
        orc.date_time_of_order_event = '20260509155000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700007', ei_2='MEDIATRI')
        obr.filler_order_number = EI(ei_1='RES700007', ei_2='FIMLAB')
        obr.universal_service_identifier = CWE(cwe_1='2003', cwe_2='P-Krea', cwe_3='FIMLAB')
        obr.observation_date_time = '20260509085000'
        obr.obr_14 = '20260509085000'
        obr.obr_15 = '^^S'
        obr.obr_16 = 'DR700^Aalto^Kirsi^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509155000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2160-0', cwe_2='P-Krea', cwe_3='LN')
        obx.obx_5 = '68'
        obx.units = CWE(cwe_1='umol/l')
        obx.reference_range = '50-90'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509155000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='33914-3', cwe_2='eGFR', cwe_3='LN')
        obx_2.obx_5 = '85'
        obx_2.units = CWE(cwe_1='ml/min/1.73m2')
        obx_2.reference_range = '>60'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509155000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='P-Urea', cwe_3='LN')
        obx_3.obx_5 = '5.2'
        obx_3.units = CWE(cwe_1='mmol/l')
        obx_3.reference_range = '2.6-6.4'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509155000'

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
    """ Based on live/fi/fi-mediconsult.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDIATRI')
        msh.sending_facility = HD(hd_1='JYVASKYLA_TK')
        msh.receiving_application = HD(hd_1='KANTA')
        msh.receiving_facility = HD(hd_1='THL')
        msh.date_time_of_message = '20260509161000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MEDI000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT700013', cx_4='JYTK', cx_5='MR'), CX(cx_1='150102-345M', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Koivunen', xpn_2='Emilia', xpn_3='Sofia', xpn_5='Neiti')
        pid.date_time_of_birth = '20020115'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Cygnaeuksenkatu 8', xad_3='Jyväskylä', xad_5='40100', xad_6='FIN')
        pid.pid_13 = '^^CP^0451234577'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='JYTK', pl_2='NEUVOLA1', pl_3='Vastaanottohuone 1', pl_5='KSSHP')
        pv1.pv1_7 = 'DR704^Rajala^Sanna^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI700009')

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
        obr.universal_service_identifier = CWE(cwe_1='30954-2', cwe_2='Vaccination record', cwe_3='LN')
        obr.observation_date_time = '20260509161000'
        obr.obr_15 = 'DR704^Rajala^Sanna^^^LL^Lääkäri'
        obr.filler_field_2 = '20260509161000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='30954-2', cwe_2='Vaccination record text', cwe_3='LN')
        obx.obx_5 = 'Influenssarokotus annettu, kausi 2026-2027. Valmiste: Fluarix Tetra, erä AB1234.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509161000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Rokotustodistus', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKL01hcmtJbmZvIDw8Ci9NYXJrZWQgdHJ1ZQo+PgovTGFuZyAoZmkpCj4+CmVuZG9iagoy'
            'IDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJdCi9Db3VudCAxCi9NZWRpYUJveCA+Pgpl'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509161000'

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
    """ Based on live/fi/fi-mediconsult.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDIATRI')
        msh.sending_facility = HD(hd_1='JYVASKYLA_TTH')
        msh.receiving_application = HD(hd_1='FIMLAB')
        msh.receiving_facility = HD(hd_1='KSSHP')
        msh.date_time_of_message = '20260509091000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MEDI000013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT700014', cx_4='JTTH', cx_5='MR'), CX(cx_1='220188-678N', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Kortelainen', xpn_2='Janne', xpn_3='Mikael', xpn_5='Herra')
        pid.date_time_of_birth = '19880122'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Gummeruksenkatu 3', xad_3='Jyväskylä', xad_5='40100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234592'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='JTTH', pl_2='TYÖTERV1', pl_3='Vastaanottohuone 2', pl_5='KSSHP')
        pv1.pv1_7 = 'DR705^Peltola^Mikko^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI700010')

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
        orc.placer_order_number = EI(ei_1='ORD700008', ei_2='MEDIATRI')
        orc.orc_7 = '^^^20260509091000^^R'
        orc.date_time_of_order_event = '20260509091000'
        orc.orc_10 = 'DR705^Peltola^Mikko^^^LL^Lääkäri'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700008', ei_2='MEDIATRI')
        obr.universal_service_identifier = CWE(cwe_1='2741', cwe_2='B-PVK+T', cwe_3='FIMLAB')
        obr.observation_date_time = '20260509091000'
        obr.obr_15 = 'DR705^Peltola^Mikko^^^LL^Lääkäri'

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
        obr_2.placer_order_number = EI(ei_1='ORD700008', ei_2='MEDIATRI')
        obr_2.universal_service_identifier = CWE(cwe_1='2085', cwe_2='P-ALAT', cwe_3='FIMLAB')
        obr_2.observation_date_time = '20260509091000'
        obr_2.obr_15 = 'DR705^Peltola^Mikko^^^LL^Lääkäri'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='ORD700008', ei_2='MEDIATRI')
        obr_3.universal_service_identifier = CWE(cwe_1='2003', cwe_2='P-Krea', cwe_3='FIMLAB')
        obr_3.observation_date_time = '20260509091000'
        obr_3.obr_15 = 'DR705^Peltola^Mikko^^^LL^Lääkäri'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3]

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
    """ Based on live/fi/fi-mediconsult.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FIMLAB')
        msh.sending_facility = HD(hd_1='KSSHP')
        msh.receiving_application = HD(hd_1='MEDIATRI')
        msh.receiving_facility = HD(hd_1='JYVASKYLA_TTH')
        msh.date_time_of_message = '20260509150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'FIMLAB000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'FIN'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PT700014', cx_4='JTTH', cx_5='MR'), CX(cx_1='220188-678N', cx_4='DVV', cx_5='NNFIN')]
        pid.patient_name = XPN(xpn_1='Kortelainen', xpn_2='Janne', xpn_3='Mikael', xpn_5='Herra')
        pid.date_time_of_birth = '19880122'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Gummeruksenkatu 3', xad_3='Jyväskylä', xad_5='40100', xad_6='FIN')
        pid.pid_13 = '^^CP^0401234592'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='JTTH', pl_2='TYÖTERV1', pl_3='Vastaanottohuone 2', pl_5='KSSHP')
        pv1.pv1_7 = 'DR705^Peltola^Mikko^^^LL^Lääkäri'
        pv1.visit_number = CX(cx_1='KÄYNTI700010')

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
        orc.placer_order_number = EI(ei_1='ORD700008', ei_2='MEDIATRI')
        orc.filler_order_number = EI(ei_1='RES700008', ei_2='FIMLAB')
        orc.orc_7 = '^^^20260509091000^^R'
        orc.date_time_of_order_event = '20260509150000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD700008', ei_2='MEDIATRI')
        obr.filler_order_number = EI(ei_1='RES700008', ei_2='FIMLAB')
        obr.universal_service_identifier = CWE(cwe_1='2741', cwe_2='B-PVK+T', cwe_3='FIMLAB')
        obr.observation_date_time = '20260509092000'
        obr.obr_14 = '20260509092000'
        obr.obr_15 = '^^B'
        obr.obr_16 = 'DR705^Peltola^Mikko^^^LL^Lääkäri'
        obr.results_rpt_status_chng_date_time = '20260509150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6768', cwe_2='B-Leuk', cwe_3='FIMLAB')
        obx.obx_5 = '5.5'
        obx.units = CWE(cwe_1='10E9/l')
        obx.reference_range = '3.4-8.2'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260509150000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1552', cwe_2='B-Hb', cwe_3='FIMLAB')
        obx_2.obx_5 = '152'
        obx_2.units = CWE(cwe_1='g/l')
        obx_2.reference_range = '134-167'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260509150000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='1742-6', cwe_2='P-ALAT', cwe_3='LN')
        obx_3.obx_5 = '22'
        obx_3.units = CWE(cwe_1='U/l')
        obx_3.reference_range = '<40'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260509150000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2160-0', cwe_2='P-Krea', cwe_3='LN')
        obx_4.obx_5 = '82'
        obx_4.units = CWE(cwe_1='umol/l')
        obx_4.reference_range = '60-100'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260509150000'

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
