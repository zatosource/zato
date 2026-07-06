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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import DG1, EVN, IN1, MSH, NK1, NTE, OBR, OBX, ORC, PID, PV1, RXO

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ca', 'ca-meditech.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ca/ca-meditech.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MT_EXPANSE')
        msh.sending_facility = HD(hd_1='CAMBRIDGE_MEM')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='HIS_SYS')
        msh.date_time_of_message = '20260509071500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MT000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260509071500'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='8273619054', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Fortin', xpn_2='Gabriel', xpn_3='Joseph')
        pid.date_time_of_birth = '19710823'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='512 Hespeler Rd', xad_3='Cambridge', xad_4='ON', xad_5='N1R 4G2', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^519^7384216'
        pid.religion = CWE(cwe_1='MRN314928')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3MED', pl_2='312', pl_3='A', pl_4='CMH')
        pv1.attending_doctor = XCN(xcn_1='23145', xcn_2='Wozniak', xcn_3='Tomasz', xcn_6='Dr.', xcn_8='MD')
        pv1.referring_doctor = XCN(xcn_1='56823', xcn_2='Khouri', xcn_3='Layla', xcn_6='Dr.', xcn_8='MD')
        pv1.temporary_location = PL(pl_1='MED')
        pv1.ambulatory_status = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='ENC2026050901')
        pv1.admit_date_time = '20260509071500'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.insurance_company_id = CX(cx_1='OHIP')
        in1.insurance_company_name = XON(xon_1='Ontario Health Insurance Plan')
        in1.insurance_company_address = XAD(xad_1="49 Place d'Armes", xad_3='Kingston', xad_4='ON', xad_5='K7L 5J3', xad_6='CA')
        in1.verification_status = '8273619054'

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
    """ Based on live/ca/ca-meditech.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MT_EXPANSE')
        msh.sending_facility = HD(hd_1='CAMBRIDGE_MEM')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='HIS_SYS')
        msh.date_time_of_message = '20260509143000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'MT000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260509143000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='8273619054', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Fortin', xpn_2='Gabriel', xpn_3='Joseph')
        pid.date_time_of_birth = '19710823'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='512 Hespeler Rd', xad_3='Cambridge', xad_4='ON', xad_5='N1R 4G2', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^519^7384216'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4SURG', pl_2='405', pl_3='B', pl_4='CMH')
        pv1.attending_doctor = XCN(xcn_1='23145', xcn_2='Wozniak', xcn_3='Tomasz', xcn_6='Dr.', xcn_8='MD')
        pv1.referring_doctor = XCN(xcn_1='56823', xcn_2='Khouri', xcn_3='Layla', xcn_6='Dr.', xcn_8='MD')
        pv1.temporary_location = PL(pl_1='SURG')
        pv1.ambulatory_status = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='ENC2026050901')
        pv1.admit_date_time = '20260509143000'

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
    """ Based on live/ca/ca-meditech.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MT_EXPANSE')
        msh.sending_facility = HD(hd_1='CAMBRIDGE_MEM')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='HIS_SYS')
        msh.date_time_of_message = '20260512110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MT000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260512110000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='8273619054', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Fortin', xpn_2='Gabriel', xpn_3='Joseph')
        pid.date_time_of_birth = '19710823'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='512 Hespeler Rd', xad_3='Cambridge', xad_4='ON', xad_5='N1R 4G2', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^519^7384216'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4SURG', pl_2='405', pl_3='B', pl_4='CMH')
        pv1.attending_doctor = XCN(xcn_1='23145', xcn_2='Wozniak', xcn_3='Tomasz', xcn_6='Dr.', xcn_8='MD')
        pv1.referring_doctor = XCN(xcn_1='56823', xcn_2='Khouri', xcn_3='Layla', xcn_6='Dr.', xcn_8='MD')
        pv1.temporary_location = PL(pl_1='SURG')
        pv1.ambulatory_status = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='ENC2026050901')
        pv1.admit_date_time = '20260512110000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K80.2', cwe_2='Calculus of gallbladder without obstruction', cwe_3='I10')
        dg1.diagnosis_date_time = '20260509'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = dg1

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
    """ Based on live/ca/ca-meditech.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MT_EXPANSE')
        msh.sending_facility = HD(hd_1='NORTH_BAY_RH')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='HIS_SYS')
        msh.date_time_of_message = '20260510083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'MT000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260510083000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='5184729063', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lavoie', xpn_2='Camille', xpn_3='Marie')
        pid.date_time_of_birth = '19880316'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='287 Fraser St', xad_3='North Bay', xad_4='ON', xad_5='P1B 2X4', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^705^5827493'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='EMERG', pl_2='ER1', pl_3='1', pl_4='NBRH')
        pv1.attending_doctor = XCN(xcn_1='78234', xcn_2='Cooper', xcn_3='Jonathan', xcn_6='Dr.', xcn_8='MD')
        pv1.hospital_service = CWE(cwe_1='EMERG')
        pv1.admit_source = CWE(cwe_1='9')
        pv1.vip_indicator = CWE(cwe_1='ENC2026051001')
        pv1.prior_temporary_location = PL(pl_1='20260510083000')

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/ca/ca-meditech.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MT_EXPANSE')
        msh.sending_facility = HD(hd_1='CAMBRIDGE_MEM')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='HIS_SYS')
        msh.date_time_of_message = '20260511090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'MT000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260511090000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='8273619054', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Fortin', xpn_2='Gabriel', xpn_3='Joseph')
        pid.date_time_of_birth = '19710823'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='145 Holiday Inn Dr', xad_3='Cambridge', xad_4='ON', xad_5='N3C 1Z6', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^519^7385923'
        pid.religion = CWE(cwe_1='MRN314928')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4SURG', pl_2='405', pl_3='B', pl_4='CMH')
        pv1.attending_doctor = XCN(xcn_1='23145', xcn_2='Wozniak', xcn_3='Tomasz', xcn_6='Dr.', xcn_8='MD')
        pv1.hospital_service = CWE(cwe_1='SURG')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='ENC2026050901')
        pv1.prior_temporary_location = PL(pl_1='20260511090000')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Fortin', xpn_2='Marie-Claude')
        nk1.address = XAD(xad_2='PRN', xad_3='PH', xad_5='1', xad_6='519', xad_7='7384217')
        nk1.next_of_kin_associated_partys_identifiers = CX(cx_1='SPO')

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
    """ Based on live/ca/ca-meditech.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDITECH')
        msh.sending_facility = HD(hd_1='HOPITAL_ANNA_LABERGE')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='HIS_SYS')
        msh.date_time_of_message = '20260509090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MT000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260509090000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='DEMR74052812', cx_4='QC_RAMQ', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Demers', xpn_2='Sebastien', xpn_3='Luc')
        pid.date_time_of_birth = '19740528'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='2814 Boul Saint-Joseph', xad_3='Laval', xad_4='QC', xad_5='H7N 4P3', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^450^7298142'
        pid.religion = CWE(cwe_1='MRN429183')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='2MED', pl_2='210', pl_3='A', pl_4='HAL')
        pv1.attending_doctor = XCN(xcn_1='34782', xcn_2='Tremblay', xcn_3='Andre', xcn_6='Dr.', xcn_8='MD')
        pv1.referring_doctor = XCN(xcn_1='45893', xcn_2='Lavoie', xcn_3='Sophie', xcn_6='Dr.', xcn_8='MD')
        pv1.temporary_location = PL(pl_1='MED')
        pv1.ambulatory_status = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='ENC2026050902')
        pv1.admit_date_time = '20260509090000'

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/ca/ca-meditech.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MT_EXPANSE')
        msh.sending_facility = HD(hd_1='CAMBRIDGE_MEM')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260509150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MT000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='8273619054', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Fortin', xpn_2='Gabriel', xpn_3='Joseph')
        pid.date_time_of_birth = '19710823'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='512 Hespeler Rd', xad_3='Cambridge', xad_4='ON', xad_5='N1R 4G2', xad_6='CA')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='LAB200100')
        orc.filler_order_number = EI(ei_1='LAB300200')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509080000'
        orc.orc_12 = '23145^Wozniak^Tomasz^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB200100')
        obr.filler_order_number = EI(ei_1='LAB300200')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC panel', cwe_3='LN')
        obr.observation_date_time = '20260509073000'
        obr.obr_16 = '23145^Wozniak^Tomasz^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260509143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin', cwe_3='LN')
        obx.obx_5 = '152'
        obx.units = CWE(cwe_1='g/L')
        obx.reference_range = '130-170'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukocytes', cwe_3='LN')
        obx_2.obx_5 = '9.8'
        obx_2.units = CWE(cwe_1='x10E9/L')
        obx_2.reference_range = '4.0-11.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erythrocytes', cwe_3='LN')
        obx_3.obx_5 = '4.82'
        obx_3.units = CWE(cwe_1='x10E12/L')
        obx_3.reference_range = '4.50-5.90'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='777-3', cwe_2='Platelets', cwe_3='LN')
        obx_4.obx_5 = '312'
        obx_4.units = CWE(cwe_1='x10E9/L')
        obx_4.reference_range = '150-400'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='787-2', cwe_2='MCV', cwe_3='LN')
        obx_5.obx_5 = '91.2'
        obx_5.units = CWE(cwe_1='fL')
        obx_5.reference_range = '80.0-100.0'
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
    """ Based on live/ca/ca-meditech.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MT_EXPANSE')
        msh.sending_facility = HD(hd_1='NORTH_BAY_RH')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260510110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MT000008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='5184729063', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lavoie', xpn_2='Camille', xpn_3='Marie')
        pid.date_time_of_birth = '19880316'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='287 Fraser St', xad_3='North Bay', xad_4='ON', xad_5='P1B 2X4', xad_6='CA')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='LAB200200')
        orc.filler_order_number = EI(ei_1='LAB300300')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260510084000'
        orc.orc_12 = '78234^Cooper^Jonathan^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB200200')
        obr.filler_order_number = EI(ei_1='LAB300300')
        obr.universal_service_identifier = CWE(cwe_1='49563-0', cwe_2='Troponin I cardiac', cwe_3='LN')
        obr.observation_date_time = '20260510084000'
        obr.obr_16 = '78234^Cooper^Jonathan^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260510103000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='49563-0', cwe_2='Troponin I', cwe_3='LN')
        obx.obx_5 = '0.85'
        obx.units = CWE(cwe_1='ng/mL')
        obx.reference_range = '0.00-0.04'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Critical value - physician notified at 1045h by phone.'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx
        observation.nte = nte

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
    """ Based on live/ca/ca-meditech.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MT_EXPANSE')
        msh.sending_facility = HD(hd_1='CAMBRIDGE_MEM')
        msh.receiving_application = HD(hd_1='RAD_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260510163000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MT000009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='8273619054', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Fortin', xpn_2='Gabriel', xpn_3='Joseph')
        pid.date_time_of_birth = '19710823'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='512 Hespeler Rd', xad_3='Cambridge', xad_4='ON', xad_5='N1R 4G2', xad_6='CA')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='RAD200300')
        orc.filler_order_number = EI(ei_1='RAD300400')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260510130000'
        orc.orc_12 = '23145^Wozniak^Tomasz^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD200300')
        obr.filler_order_number = EI(ei_1='RAD300400')
        obr.universal_service_identifier = CWE(cwe_1='30712-3', cwe_2='Abdominal US', cwe_3='LN')
        obr.observation_date_time = '20260510130000'
        obr.obr_16 = '23145^Wozniak^Tomasz^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260510160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Ultrasound Report', cwe_3='MT_EXPANSE')
        obx.obx_5 = (
            '^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL0NvdW50IDEKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0K'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1Bh'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='30712-3', cwe_2='Abdominal US Impression', cwe_3='LN')
        obx_2.obx_5 = 'Cholelithiasis with gallbladder wall thickening suggesting acute cholecystitis. No biliary duct dilatation.'
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
    """ Based on live/ca/ca-meditech.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MT_EXPANSE')
        msh.sending_facility = HD(hd_1='NORTH_BAY_RH')
        msh.receiving_application = HD(hd_1='DOC_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260511091500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MT000010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='5184729063', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lavoie', xpn_2='Camille', xpn_3='Marie')
        pid.date_time_of_birth = '19880316'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='287 Fraser St', xad_3='North Bay', xad_4='ON', xad_5='P1B 2X4', xad_6='CA')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='DOC200400')
        orc.filler_order_number = EI(ei_1='DOC300500')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260511083000'
        orc.orc_12 = '78234^Cooper^Jonathan^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='DOC200400')
        obr.filler_order_number = EI(ei_1='DOC300500')
        obr.universal_service_identifier = CWE(cwe_1='11488-4', cwe_2='Consultation note', cwe_3='LN')
        obr.observation_date_time = '20260511083000'
        obr.obr_16 = '78234^Cooper^Jonathan^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260511090000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='IMG', cwe_2='Scanned Consultation Letter', cwe_3='MT_EXPANSE')
        obx.obx_5 = '^IM^PNG^Base64^iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAFUlEQVQYV2P8z8BQz0AEYBxVOGwUAgBGFgiB3bCmjgAAAABJRU5ErkJggg=='
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
    """ Based on live/ca/ca-meditech.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MT_EXPANSE')
        msh.sending_facility = HD(hd_1='CAMBRIDGE_MEM')
        msh.receiving_application = HD(hd_1='LAB_SYS')
        msh.receiving_facility = HD(hd_1='CORE_LAB')
        msh.date_time_of_message = '20260509065000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MT000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='8273619054', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Fortin', xpn_2='Gabriel', xpn_3='Joseph')
        pid.date_time_of_birth = '19710823'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='512 Hespeler Rd', xad_3='Cambridge', xad_4='ON', xad_5='N1R 4G2', xad_6='CA')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3MED', pl_2='312', pl_3='A', pl_4='CMH')
        pv1.attending_doctor = XCN(xcn_1='23145', xcn_2='Wozniak', xcn_3='Tomasz', xcn_6='Dr.', xcn_8='MD')

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
        orc.placer_order_number = EI(ei_1='LAB200500')
        orc.date_time_of_order_event = '20260509064500'
        orc.orc_12 = '23145^Wozniak^Tomasz^^^Dr.^^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB200500')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='CMP', cwe_3='LN')
        obr.observation_date_time = '20260509065000'
        obr.obr_16 = '23145^Wozniak^Tomasz^^^Dr.^^MD'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build ORC ..
        orc_2 = ORC()
        orc_2.order_control = 'NW'
        orc_2.placer_order_number = EI(ei_1='LAB200501')
        orc_2.date_time_of_order_event = '20260509064500'
        orc_2.orc_12 = '23145^Wozniak^Tomasz^^^Dr.^^MD'

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='LAB200501')
        obr_2.universal_service_identifier = CWE(cwe_1='2093-3', cwe_2='Cholesterol', cwe_3='LN')
        obr_2.observation_date_time = '20260509065000'
        obr_2.obr_16 = '23145^Wozniak^Tomasz^^^Dr.^^MD'

        # .. build the ORDER_DETAIL group ..
        order_detail_2 = OrmO01OrderDetail()
        order_detail_2.obr = obr_2

        # .. build the ORDER group ..
        order_2 = OrmO01Order()
        order_2.orc = orc_2
        order_2.order_detail = order_detail_2

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = [order, order_2]

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
    """ Based on live/ca/ca-meditech.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MT_EXPANSE')
        msh.sending_facility = HD(hd_1='NORTH_BAY_RH')
        msh.receiving_application = HD(hd_1='RIS_SYS')
        msh.receiving_facility = HD(hd_1='RAD_DEPT')
        msh.date_time_of_message = '20260510091000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MT000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='5184729063', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lavoie', xpn_2='Camille', xpn_3='Marie')
        pid.date_time_of_birth = '19880316'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='287 Fraser St', xad_3='North Bay', xad_4='ON', xad_5='P1B 2X4', xad_6='CA')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='EMERG', pl_2='ER1', pl_3='1', pl_4='NBRH')
        pv1.attending_doctor = XCN(xcn_1='78234', xcn_2='Cooper', xcn_3='Jonathan', xcn_6='Dr.', xcn_8='MD')

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
        orc.placer_order_number = EI(ei_1='RAD200600')
        orc.date_time_of_order_event = '20260510090500'
        orc.orc_12 = '78234^Cooper^Jonathan^^^Dr.^^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD200600')
        obr.universal_service_identifier = CWE(cwe_1='71020-2', cwe_2='Chest X-ray', cwe_3='LN')
        obr.observation_date_time = '20260510091000'
        obr.obr_16 = '78234^Cooper^Jonathan^^^Dr.^^MD'
        obr.obr_28 = 'STAT'

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
    """ Based on live/ca/ca-meditech.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MT_EXPANSE')
        msh.sending_facility = HD(hd_1='CAMBRIDGE_MEM')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260510103000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MT000013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='8273619054', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Fortin', xpn_2='Gabriel', xpn_3='Joseph')
        pid.date_time_of_birth = '19710823'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='512 Hespeler Rd', xad_3='Cambridge', xad_4='ON', xad_5='N1R 4G2', xad_6='CA')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='LAB200700')
        orc.filler_order_number = EI(ei_1='LAB300800')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260510070000'
        orc.orc_12 = '23145^Wozniak^Tomasz^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB200700')
        obr.filler_order_number = EI(ei_1='LAB300800')
        obr.universal_service_identifier = CWE(cwe_1='38875-1', cwe_2='Coagulation panel', cwe_3='LN')
        obr.observation_date_time = '20260510070000'
        obr.obr_16 = '23145^Wozniak^Tomasz^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260510100000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='PT', cwe_3='LN')
        obx.obx_5 = '13.2'
        obx.units = CWE(cwe_1='seconds')
        obx.reference_range = '11.0-13.5'
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
        obx_2.reference_range = '0.9-1.1'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3173-2', cwe_2='aPTT', cwe_3='LN')
        obx_3.obx_5 = '31.5'
        obx_3.units = CWE(cwe_1='seconds')
        obx_3.reference_range = '25.0-35.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/ca/ca-meditech.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDITECH')
        msh.sending_facility = HD(hd_1='LIONS_GATE_HOSP')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='HIS_SYS')
        msh.date_time_of_message = '20260511073000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MT000014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260511073000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='6253719048', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Park', xpn_2='Joon-Ho')
        pid.date_time_of_birth = '19790204'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='825 Marine Dr', xad_3='North Vancouver', xad_4='BC', xad_5='V7P 1V4', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^604^9748312'
        pid.religion = CWE(cwe_1='MRN528739')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='2MED', pl_2='204', pl_3='A', pl_4='LGH')
        pv1.attending_doctor = XCN(xcn_1='45729', xcn_2='MacKenzie', xcn_3='Bruce', xcn_6='Dr.', xcn_8='MD')
        pv1.referring_doctor = XCN(xcn_1='56834', xcn_2='Wong', xcn_3='Vivian', xcn_6='Dr.', xcn_8='MD')
        pv1.temporary_location = PL(pl_1='MED')
        pv1.ambulatory_status = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='ENC2026051101')
        pv1.admit_date_time = '20260511073000'

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
    """ Based on live/ca/ca-meditech.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MEDITECH')
        msh.sending_facility = HD(hd_1='LIONS_GATE_HOSP')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260511140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MT000015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='6253719048', cx_4='BC_PHN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Park', xpn_2='Joon-Ho')
        pid.date_time_of_birth = '19790204'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='825 Marine Dr', xad_3='North Vancouver', xad_4='BC', xad_5='V7P 1V4', xad_6='CA')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='LAB200800')
        orc.filler_order_number = EI(ei_1='LAB300900')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260511080000'
        orc.orc_12 = '45729^MacKenzie^Bruce^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB200800')
        obr.filler_order_number = EI(ei_1='LAB300900')
        obr.universal_service_identifier = CWE(cwe_1='24325-3', cwe_2='Hepatic function panel', cwe_3='LN')
        obr.observation_date_time = '20260511073000'
        obr.obr_16 = '45729^MacKenzie^Bruce^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260511133000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT', cwe_3='LN')
        obx.obx_5 = '145'
        obx.units = CWE(cwe_1='U/L')
        obx.reference_range = '7-56'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST', cwe_3='LN')
        obx_2.obx_5 = '98'
        obx_2.units = CWE(cwe_1='U/L')
        obx_2.reference_range = '10-40'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='1975-2', cwe_2='Bilirubin total', cwe_3='LN')
        obx_3.obx_5 = '42'
        obx_3.units = CWE(cwe_1='umol/L')
        obx_3.reference_range = '3-21'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='6768-6', cwe_2='Alkaline phosphatase', cwe_3='LN')
        obx_4.obx_5 = '310'
        obx_4.units = CWE(cwe_1='U/L')
        obx_4.reference_range = '44-147'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2885-2', cwe_2='Total protein', cwe_3='LN')
        obx_5.obx_5 = '68'
        obx_5.units = CWE(cwe_1='g/L')
        obx_5.reference_range = '60-80'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='1751-7', cwe_2='Albumin', cwe_3='LN')
        obx_6.obx_5 = '35'
        obx_6.units = CWE(cwe_1='g/L')
        obx_6.reference_range = '35-50'
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
    """ Based on live/ca/ca-meditech.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MT_EXPANSE')
        msh.sending_facility = HD(hd_1='NORTH_BAY_RH')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260511160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MT000016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='5184729063', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lavoie', xpn_2='Camille', xpn_3='Marie')
        pid.date_time_of_birth = '19880316'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='287 Fraser St', xad_3='North Bay', xad_4='ON', xad_5='P1B 2X4', xad_6='CA')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='LAB200900')
        orc.filler_order_number = EI(ei_1='LAB301000')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260511080000'
        orc.orc_12 = '78234^Cooper^Jonathan^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB200900')
        obr.filler_order_number = EI(ei_1='LAB301000')
        obr.universal_service_identifier = CWE(cwe_1='34896-2', cwe_2='Thyroid panel', cwe_3='LN')
        obr.observation_date_time = '20260511073000'
        obr.obr_16 = '78234^Cooper^Jonathan^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260511153000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='TSH', cwe_3='LN')
        obx.obx_5 = '8.7'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.4-4.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3024-7', cwe_2='Free T4', cwe_3='LN')
        obx_2.obx_5 = '9.2'
        obx_2.units = CWE(cwe_1='pmol/L')
        obx_2.reference_range = '10.0-25.0'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3053-6', cwe_2='Free T3', cwe_3='LN')
        obx_3.obx_5 = '3.1'
        obx_3.units = CWE(cwe_1='pmol/L')
        obx_3.reference_range = '3.5-6.5'
        obx_3.interpretation_codes = CWE(cwe_1='L')
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
    """ Based on live/ca/ca-meditech.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MT_EXPANSE')
        msh.sending_facility = HD(hd_1='CAMBRIDGE_MEM')
        msh.receiving_application = HD(hd_1='PHARM_SYS')
        msh.receiving_facility = HD(hd_1='PHARMACY')
        msh.date_time_of_message = '20260510070000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MT000017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='8273619054', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Fortin', xpn_2='Gabriel', xpn_3='Joseph')
        pid.date_time_of_birth = '19710823'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='512 Hespeler Rd', xad_3='Cambridge', xad_4='ON', xad_5='N1R 4G2', xad_6='CA')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4SURG', pl_2='405', pl_3='B', pl_4='CMH')
        pv1.attending_doctor = XCN(xcn_1='23145', xcn_2='Wozniak', xcn_3='Tomasz', xcn_6='Dr.', xcn_8='MD')

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
        orc.placer_order_number = EI(ei_1='RX200100')
        orc.date_time_of_order_event = '20260510065500'
        orc.orc_12 = '23145^Wozniak^Tomasz^^^Dr.^^MD'

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='106861', cwe_2='Cefazolin 1g IV q8h', cwe_3='LOCAL')
        rxo.requested_give_amount_maximum = '1'
        rxo.requested_give_units = CWE(cwe_1='g')
        rxo.requested_dosage_form = CWE(cwe_1='IV')
        rxo.providers_pharmacy_treatment_instructions = CWE(cwe_1='Q8H', cwe_3='HL70335')
        rxo.requested_drug_strength_volume = '20260510070000'
        rxo.requested_drug_strength_volume_units = CWE(cwe_1='20260513070000')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [rxo]

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
    """ Based on live/ca/ca-meditech.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MT_EXPANSE')
        msh.sending_facility = HD(hd_1='CAMBRIDGE_MEM')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='HIS_SYS')
        msh.date_time_of_message = '20260512220000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'MT000018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260512220000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3729184056', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Adeyemi', xpn_2='Babatunde', xpn_3='Olumide')
        pid.date_time_of_birth = '19930715'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='89 Water St N', xad_3='Cambridge', xad_4='ON', xad_5='N1R 5W3', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^519^7382491'
        pid.religion = CWE(cwe_1='MRN317842')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='EMERG', pl_2='ER3', pl_3='1', pl_4='CMH')
        pv1.attending_doctor = XCN(xcn_1='67823', xcn_2='Reilly', xcn_3='Maeve', xcn_6='Dr.', xcn_8='MD')
        pv1.hospital_service = CWE(cwe_1='EMERG')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.vip_indicator = CWE(cwe_1='ENC2026051201')
        pv1.prior_temporary_location = PL(pl_1='20260512220000')

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
    """ Based on live/ca/ca-meditech.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MT_EXPANSE')
        msh.sending_facility = HD(hd_1='CAMBRIDGE_MEM')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260512230000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MT000019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3729184056', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Adeyemi', xpn_2='Babatunde', xpn_3='Olumide')
        pid.date_time_of_birth = '19930715'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='89 Water St N', xad_3='Cambridge', xad_4='ON', xad_5='N1R 5W3', xad_6='CA')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='LAB201000')
        orc.filler_order_number = EI(ei_1='LAB301100')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260512221500'
        orc.orc_12 = '67823^Reilly^Maeve^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB201000')
        obr.filler_order_number = EI(ei_1='LAB301100')
        obr.universal_service_identifier = CWE(cwe_1='24336-0', cwe_2='ABG panel', cwe_3='LN')
        obr.observation_date_time = '20260512221500'
        obr.obr_16 = '67823^Reilly^Maeve^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260512225500'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2744-1', cwe_2='pH arterial', cwe_3='LN')
        obx.obx_5 = '7.38'
        obx.reference_range = '7.35-7.45'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2019-8', cwe_2='pCO2', cwe_3='LN')
        obx_2.obx_5 = '42'
        obx_2.units = CWE(cwe_1='mmHg')
        obx_2.reference_range = '35-45'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2703-7', cwe_2='pO2', cwe_3='LN')
        obx_3.obx_5 = '88'
        obx_3.units = CWE(cwe_1='mmHg')
        obx_3.reference_range = '80-100'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1959-6', cwe_2='Bicarbonate', cwe_3='LN')
        obx_4.obx_5 = '24'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '22-26'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2708-6', cwe_2='O2 Sat', cwe_3='LN')
        obx_5.obx_5 = '96'
        obx_5.units = CWE(cwe_1='%')
        obx_5.reference_range = '95-100'
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
    """ Based on live/ca/ca-meditech.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MT_EXPANSE')
        msh.sending_facility = HD(hd_1='CAMBRIDGE_MEM')
        msh.receiving_application = HD(hd_1='DOC_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260511153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MT000020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='8273619054', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Fortin', xpn_2='Gabriel', xpn_3='Joseph')
        pid.date_time_of_birth = '19710823'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='512 Hespeler Rd', xad_3='Cambridge', xad_4='ON', xad_5='N1R 4G2', xad_6='CA')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='DOC200500')
        orc.filler_order_number = EI(ei_1='DOC300600')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260511130000'
        orc.orc_12 = '23145^Wozniak^Tomasz^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='DOC200500')
        obr.filler_order_number = EI(ei_1='DOC300600')
        obr.universal_service_identifier = CWE(cwe_1='28570-0', cwe_2='Operative note', cwe_3='LN')
        obr.observation_date_time = '20260511130000'
        obr.obr_16 = '23145^Wozniak^Tomasz^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260511150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Operative Report', cwe_3='MT_EXPANSE')
        obx.obx_5 = (
            '^AP^^Base64^'
            'JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwvVHlwZS9DYXRhbG9nL1BhZ2VzIDIgMCBSPj4KZW5kb2JqCjIgMCBvYmoKPDwvVHlwZS9QYWdlcy9LaWRzWzMgMCBSXS9Db3VudCAx'
            'Pj4KZW5kb2Jq'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='28570-0', cwe_2='Operative note text', cwe_3='LN')
        obx_2.obx_5 = 'Laparoscopic cholecystectomy performed without complication. Gallbladder removed intact. Intraoperative cholangiogram normal.'
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
