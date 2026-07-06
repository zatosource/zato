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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, EI, HD, MSG, PL, PT, VID, XAD, XCN, XPN
from zato.hl7v2.v2_9.groups import AdtA39Patient, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, \
    OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, SiuS12Patient, SiuS12PersonnelResource, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A03, ADT_A05, ADT_A39, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIP, AIS, DG1, EVN, MRG, MSH, NK1, OBR, OBX, ORC, PD1, PID, PV1, RGS, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ca', 'ca-epic.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ca/ca-epic.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='SICKKIDS')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='HIS_SYS')
        msh.date_time_of_message = '20260509080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'EP000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260509080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3782619054', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lefebvre', xpn_2='Liam', xpn_3='Andre')
        pid.date_time_of_birth = '20190627'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='628 University Ave', xad_3='Toronto', xad_4='ON', xad_5='M5G 1Y3', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^416^7234812'
        pid.religion = CWE(cwe_1='MRN612847')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = '45612^Reynolds^Catherine^^^Dr.^^MD'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='7WEST', pl_2='710', pl_3='A', pl_4='SICKKIDS')
        pv1.attending_doctor = XCN(xcn_1='45612', xcn_2='Reynolds', xcn_3='Catherine', xcn_6='Dr.', xcn_8='MD')
        pv1.referring_doctor = XCN(xcn_1='78923', xcn_2='Mehta', xcn_3='Aarav', xcn_6='Dr.', xcn_8='MD')
        pv1.temporary_location = PL(pl_1='PED')
        pv1.ambulatory_status = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='VIS2026050901')
        pv1.admit_date_time = '20260509080000'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Lefebvre', xpn_2='Sophie')
        nk1.address = XAD(xad_2='PRN', xad_3='PH', xad_5='1', xad_6='416', xad_7='5538291')
        nk1.next_of_kin_associated_partys_identifiers = CX(cx_1='MTH')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.pv1 = pv1
        msg.extra_segments = [nk1]

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
    """ Based on live/ca/ca-epic.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='SICKKIDS')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='HIS_SYS')
        msh.date_time_of_message = '20260512140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'EP000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260512140000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3782619054', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lefebvre', xpn_2='Liam', xpn_3='Andre')
        pid.date_time_of_birth = '20190627'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='628 University Ave', xad_3='Toronto', xad_4='ON', xad_5='M5G 1Y3', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^416^7234812'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='7WEST', pl_2='710', pl_3='A', pl_4='SICKKIDS')
        pv1.attending_doctor = XCN(xcn_1='45612', xcn_2='Reynolds', xcn_3='Catherine', xcn_6='Dr.', xcn_8='MD')
        pv1.referring_doctor = XCN(xcn_1='78923', xcn_2='Mehta', xcn_3='Aarav', xcn_6='Dr.', xcn_8='MD')
        pv1.temporary_location = PL(pl_1='PED')
        pv1.ambulatory_status = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='VIS2026050901')
        pv1.admit_date_time = '20260512140000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J21.0', cwe_2='Acute bronchiolitis due to RSV', cwe_3='I10')
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
    """ Based on live/ca/ca-epic.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='CHU_SJ')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='HIS_SYS')
        msh.date_time_of_message = '20260510093000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'EP000003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260510093000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='GAUT08092312', cx_4='QC_RAMQ', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Gauthier', xpn_2='Florence', xpn_3='Anne-Sophie')
        pid.date_time_of_birth = '20080923'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='4218 Rue Sainte-Catherine E', xad_3='Montreal', xad_4='QC', xad_5='H1V 1Y5', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^514^4781923'
        pid.religion = CWE(cwe_1='MRN612951')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ORTHO', pl_2='CLINIC2', pl_3='1', pl_4='CHU_SJ')
        pv1.attending_doctor = XCN(xcn_1='23148', xcn_2='Dubois', xcn_3='Pascal', xcn_6='Dr.', xcn_8='MD')
        pv1.hospital_service = CWE(cwe_1='ORTHO')
        pv1.admit_source = CWE(cwe_1='9')
        pv1.vip_indicator = CWE(cwe_1='VIS2026051001')
        pv1.prior_temporary_location = PL(pl_1='20260510093000')

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
    """ Based on live/ca/ca-epic.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='CHU_SJ')
        msh.receiving_application = HD(hd_1='ADT_RECV')
        msh.receiving_facility = HD(hd_1='HIS_SYS')
        msh.date_time_of_message = '20260511100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'EP000004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260511100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='GAUT08092312', cx_4='QC_RAMQ', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Gauthier', xpn_2='Florence', xpn_3='Anne-Sophie')
        pid.date_time_of_birth = '20080923'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='1875 Boul Rene-Levesque O', xad_3='Montreal', xad_4='QC', xad_5='H3H 2N6', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^514^9237148'
        pid.religion = CWE(cwe_1='MRN612951')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ORTHO', pl_2='CLINIC2', pl_3='1', pl_4='CHU_SJ')
        pv1.attending_doctor = XCN(xcn_1='23148', xcn_2='Dubois', xcn_3='Pascal', xcn_6='Dr.', xcn_8='MD')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Gauthier', xpn_2='Pascal')
        nk1.address = XAD(xad_2='PRN', xad_3='PH', xad_5='1', xad_6='514', xad_7='9237149')
        nk1.next_of_kin_associated_partys_identifiers = CX(cx_1='FTH')

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
    """ Based on live/ca/ca-epic.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='SICKKIDS')
        msh.receiving_application = HD(hd_1='MPI_SYS')
        msh.receiving_facility = HD(hd_1='REG_SYS')
        msh.date_time_of_message = '20260510110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'EP000005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20260510110000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3782619054', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lefebvre', xpn_2='Liam', xpn_3='Andre')
        pid.date_time_of_birth = '20190627'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='89 Queens Park Cres', xad_3='Toronto', xad_4='ON', xad_5='M5S 2C7', xad_6='CA')
        pid.pid_13 = '^PRN^PH^^1^416^4827193'
        pid.religion = CWE(cwe_1='MRN612847')

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
    """ Based on live/ca/ca-epic.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='SICKKIDS')
        msh.receiving_application = HD(hd_1='MPI_SYS')
        msh.receiving_facility = HD(hd_1='REG_SYS')
        msh.date_time_of_message = '20260512080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'EP000006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260512080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3782619054', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lefebvre', xpn_2='Liam', xpn_3='Andre')
        pid.date_time_of_birth = '20190627'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='628 University Ave', xad_3='Toronto', xad_4='ON', xad_5='M5G 1Y3', xad_6='CA')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='6128493075', cx_4='ON_HN', cx_5='JHN')
        mrg.prior_patient_account_number = CX(cx_1='VIS2025110301')

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
    """ Based on live/ca/ca-epic.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='SICKKIDS')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260511150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EP000007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3782619054', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lefebvre', xpn_2='Liam', xpn_3='Andre')
        pid.date_time_of_birth = '20190627'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='628 University Ave', xad_3='Toronto', xad_4='ON', xad_5='M5G 1Y3', xad_6='CA')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='LAB300100')
        orc.filler_order_number = EI(ei_1='LAB400200')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509100000'
        orc.orc_12 = '45612^Reynolds^Catherine^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB300100')
        obr.filler_order_number = EI(ei_1='LAB400200')
        obr.universal_service_identifier = CWE(cwe_1='87040-2', cwe_2='Blood culture', cwe_3='LN')
        obr.observation_date_time = '20260509100000'
        obr.obr_16 = '45612^Reynolds^Catherine^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260511143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Bacteria identified', cwe_3='LN')
        obx.obx_5 = 'No growth^^L'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='19146-0', cwe_2='Reference lab comment', cwe_3='LN')
        obx_2.obx_5 = 'No growth after 5 days. Aerobic and anaerobic bottles negative.'
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
    """ Based on live/ca/ca-epic.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='SICKKIDS')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260509120000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EP000008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3782619054', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lefebvre', xpn_2='Liam', xpn_3='Andre')
        pid.date_time_of_birth = '20190627'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='628 University Ave', xad_3='Toronto', xad_4='ON', xad_5='M5G 1Y3', xad_6='CA')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='LAB300200')
        orc.filler_order_number = EI(ei_1='LAB400300')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509083000'
        orc.orc_12 = '45612^Reynolds^Catherine^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB300200')
        obr.filler_order_number = EI(ei_1='LAB400300')
        obr.universal_service_identifier = CWE(cwe_1='57021-8', cwe_2='CBC with differential', cwe_3='LN')
        obr.observation_date_time = '20260509080000'
        obr.obr_16 = '45612^Reynolds^Catherine^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260509113000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin', cwe_3='LN')
        obx.obx_5 = '112'
        obx.units = CWE(cwe_1='g/L')
        obx.reference_range = '105-135'
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
        obx_2.obx_5 = '14.2'
        obx_2.units = CWE(cwe_1='x10E9/L')
        obx_2.reference_range = '5.0-15.5'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='777-3', cwe_2='Platelets', cwe_3='LN')
        obx_3.obx_5 = '289'
        obx_3.units = CWE(cwe_1='x10E9/L')
        obx_3.reference_range = '150-400'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='770-8', cwe_2='Neutrophils', cwe_3='LN')
        obx_4.obx_5 = '8.5'
        obx_4.units = CWE(cwe_1='x10E9/L')
        obx_4.reference_range = '1.5-8.5'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='731-0', cwe_2='Lymphocytes', cwe_3='LN')
        obx_5.obx_5 = '4.1'
        obx_5.units = CWE(cwe_1='x10E9/L')
        obx_5.reference_range = '2.0-8.0'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='742-7', cwe_2='Monocytes', cwe_3='LN')
        obx_6.obx_5 = '1.2'
        obx_6.units = CWE(cwe_1='x10E9/L')
        obx_6.reference_range = '0.2-1.0'
        obx_6.interpretation_codes = CWE(cwe_1='H')
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
    """ Based on live/ca/ca-epic.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='SICKKIDS')
        msh.receiving_application = HD(hd_1='CARDIO_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260510160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EP000009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3782619054', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lefebvre', xpn_2='Liam', xpn_3='Andre')
        pid.date_time_of_birth = '20190627'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='628 University Ave', xad_3='Toronto', xad_4='ON', xad_5='M5G 1Y3', xad_6='CA')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ECHO300100')
        orc.filler_order_number = EI(ei_1='ECHO400200')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260510130000'
        orc.orc_12 = '67234^Tan^Wei-Ming^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ECHO300100')
        obr.filler_order_number = EI(ei_1='ECHO400200')
        obr.universal_service_identifier = CWE(cwe_1='34552-0', cwe_2='Echocardiography', cwe_3='LN')
        obr.observation_date_time = '20260510130000'
        obr.obr_16 = '67234^Tan^Wei-Ming^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260510155000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Echocardiogram Report', cwe_3='EPIC')
        obx.obx_5 = (
            '^AP^^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4K'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='34552-0', cwe_2='Echo Interpretation', cwe_3='LN')
        obx_2.obx_5 = 'Normal biventricular size and systolic function. No valvular abnormalities. No pericardial effusion. LVEF 65%.'
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
    """ Based on live/ca/ca-epic.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='CHU_SJ')
        msh.receiving_application = HD(hd_1='OB_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260511110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EP000010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='MORI91051803', cx_4='QC_RAMQ', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Morin', xpn_2='Catherine', xpn_3='Josee')
        pid.date_time_of_birth = '19910518'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='3742 Boul des Laurentides', xad_3='Laval', xad_4='QC', xad_5='H7K 2J4', xad_6='CA')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='US300200')
        orc.filler_order_number = EI(ei_1='US400300')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260511090000'
        orc.orc_12 = '78451^Pelletier^Sophie^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='US300200')
        obr.filler_order_number = EI(ei_1='US400300')
        obr.universal_service_identifier = CWE(cwe_1='76811-2', cwe_2='OB Ultrasound', cwe_3='LN')
        obr.observation_date_time = '20260511090000'
        obr.obr_16 = '78451^Pelletier^Sophie^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260511103000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='IMG', cwe_2='Fetal Ultrasound Image', cwe_3='EPIC')
        obx.obx_5 = (
            '^IM^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAIBAQIBAQICAgICAgICAwUDAwMDAwYEBAMFBwYHBwcGBwcICQsJCAgKCAcHCg0KCgsMDAwMBwkODw0MDgsMDAz/2wBDAQICAgMDAwYDAwYM'
            'CAcIDAwMDA=='
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='76811-2', cwe_2='OB US Interpretation', cwe_3='LN')
        obx_2.obx_5 = 'Single viable intrauterine pregnancy. Gestational age 20 weeks 3 days. Normal anatomy survey. EFW 350g (50th percentile). AFI normal.'
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
    """ Based on live/ca/ca-epic.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='SICKKIDS')
        msh.receiving_application = HD(hd_1='LAB_SYS')
        msh.receiving_facility = HD(hd_1='CORE_LAB')
        msh.date_time_of_message = '20260509074500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'EP000011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3782619054', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lefebvre', xpn_2='Liam', xpn_3='Andre')
        pid.date_time_of_birth = '20190627'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='628 University Ave', xad_3='Toronto', xad_4='ON', xad_5='M5G 1Y3', xad_6='CA')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='7WEST', pl_2='710', pl_3='A', pl_4='SICKKIDS')
        pv1.attending_doctor = XCN(xcn_1='45612', xcn_2='Reynolds', xcn_3='Catherine', xcn_6='Dr.', xcn_8='MD')

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
        orc.placer_order_number = EI(ei_1='LAB300300')
        orc.date_time_of_order_event = '20260509074000'
        orc.orc_12 = '45612^Reynolds^Catherine^^^Dr.^^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB300300')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='CMP', cwe_3='LN')
        obr.observation_date_time = '20260509074500'
        obr.obr_16 = '45612^Reynolds^Catherine^^^Dr.^^MD'

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
        orc_2.placer_order_number = EI(ei_1='LAB300301')
        orc_2.date_time_of_order_event = '20260509074000'
        orc_2.orc_12 = '45612^Reynolds^Catherine^^^Dr.^^MD'

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='LAB300301')
        obr_2.universal_service_identifier = CWE(cwe_1='2951-2', cwe_2='Electrolyte panel', cwe_3='LN')
        obr_2.observation_date_time = '20260509074500'
        obr_2.obr_16 = '45612^Reynolds^Catherine^^^Dr.^^MD'

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
    """ Based on live/ca/ca-epic.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='SICKKIDS')
        msh.receiving_application = HD(hd_1='RIS_SYS')
        msh.receiving_facility = HD(hd_1='RAD_DEPT')
        msh.date_time_of_message = '20260510080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'EP000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3782619054', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lefebvre', xpn_2='Liam', xpn_3='Andre')
        pid.date_time_of_birth = '20190627'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='628 University Ave', xad_3='Toronto', xad_4='ON', xad_5='M5G 1Y3', xad_6='CA')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='7WEST', pl_2='710', pl_3='A', pl_4='SICKKIDS')
        pv1.attending_doctor = XCN(xcn_1='45612', xcn_2='Reynolds', xcn_3='Catherine', xcn_6='Dr.', xcn_8='MD')

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
        orc.placer_order_number = EI(ei_1='RAD300400')
        orc.date_time_of_order_event = '20260510075000'
        orc.orc_12 = '78923^Mehta^Aarav^^^Dr.^^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD300400')
        obr.universal_service_identifier = CWE(cwe_1='70553-6', cwe_2='MRI Brain without contrast', cwe_3='LN')
        obr.observation_date_time = '20260510080000'
        obr.obr_16 = '78923^Mehta^Aarav^^^Dr.^^MD'
        obr.obr_28 = 'ROUTINE'

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
    """ Based on live/ca/ca-epic.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='SICKKIDS')
        msh.receiving_application = HD(hd_1='SCHED_RECV')
        msh.receiving_facility = HD(hd_1='CLINIC_SYS')
        msh.date_time_of_message = '20260512090000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'EP000013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT20260519001')
        sch.appointment_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine', cwe_3='HL70276')
        sch.appointment_type = CWE(cwe_1='FOLLOWUP', cwe_2='Follow-up visit', cwe_3='HL70277')
        sch.sch_9 = '20'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^20^20260519100000^20260519102000'
        sch.placer_contact_person = XCN(xcn_1='45612', xcn_2='Reynolds', xcn_3='Catherine', xcn_6='Dr.', xcn_8='MD')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3782619054', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lefebvre', xpn_2='Liam', xpn_3='Andre')
        pid.date_time_of_birth = '20190627'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='628 University Ave', xad_3='Toronto', xad_4='ON', xad_5='M5G 1Y3', xad_6='CA')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PED', pl_2='CLINIC1', pl_3='1', pl_4='SICKKIDS')
        pv1.attending_doctor = XCN(xcn_1='45612', xcn_2='Reynolds', xcn_3='Catherine', xcn_6='Dr.', xcn_8='MD')

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
        ais.universal_service_identifier = CWE(cwe_1='PED_FOLLOWUP', cwe_2='Pediatric Follow-up', cwe_3='LOCAL')
        ais.start_date_time = '20260519100000'
        ais.start_date_time_offset = '0'
        ais.start_date_time_offset_units = CNE(cne_1='MIN')
        ais.duration = '20'
        ais.duration_units = CNE(cne_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='45612', xcn_2='Reynolds', xcn_3='Catherine', xcn_6='Dr.', xcn_8='MD')
        aip.start_date_time_offset_units = CNE(cne_1='20260519100000')
        aip.duration = '0'
        aip.duration_units = CNE(cne_1='MIN')
        aip.allow_substitution_code = CWE(cwe_1='20')
        aip.filler_status_code = CWE(cwe_1='MIN')

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
    """ Based on live/ca/ca-epic.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='SICKKIDS')
        msh.receiving_application = HD(hd_1='DOC_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260512150000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'EP000014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260512150000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3782619054', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lefebvre', xpn_2='Liam', xpn_3='Andre')
        pid.date_time_of_birth = '20190627'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='628 University Ave', xad_3='Toronto', xad_4='ON', xad_5='M5G 1Y3', xad_6='CA')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='7WEST', pl_2='710', pl_3='A', pl_4='SICKKIDS')
        pv1.attending_doctor = XCN(xcn_1='45612', xcn_2='Reynolds', xcn_3='Catherine', xcn_6='Dr.', xcn_8='MD')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='Discharge Summary', cwe_3='HL70270')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20260512140000'
        txa.origination_date_time = '20260512150000'
        txa.transcriptionist_code_name = XCN(xcn_1='45612', xcn_2='Reynolds', xcn_3='Catherine', xcn_6='Dr.', xcn_8='MD')
        txa.parent_document_number = EI(ei_1='DOC7891011')
        txa.document_availability_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='DS', cwe_2='Discharge Summary Text', cwe_3='LOCAL')
        obx.obx_5 = (
            'Diagnosis: Acute bronchiolitis (RSV positive). Hospital course: Admitted for oxygen therapy and supportive care. Weaned to room air by day 3'
            '. Feeding well at discharge. Follow-up in 1 week.'
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
    """ Based on live/ca/ca-epic.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='SICKKIDS')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EP000015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3782619054', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lefebvre', xpn_2='Liam', xpn_3='Andre')
        pid.date_time_of_birth = '20190627'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='628 University Ave', xad_3='Toronto', xad_4='ON', xad_5='M5G 1Y3', xad_6='CA')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='LAB300400')
        orc.filler_order_number = EI(ei_1='LAB400500')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509085000'
        orc.orc_12 = '45612^Reynolds^Catherine^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB300400')
        obr.filler_order_number = EI(ei_1='LAB400500')
        obr.universal_service_identifier = CWE(cwe_1='92131-2', cwe_2='RSV Ag rapid', cwe_3='LN')
        obr.observation_date_time = '20260509085000'
        obr.obr_16 = '45612^Reynolds^Catherine^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260509095000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='92131-2', cwe_2='RSV antigen', cwe_3='LN')
        obx.obx_5 = '260373001^Detected^SCT'
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
    """ Based on live/ca/ca-epic.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='CHU_SJ')
        msh.receiving_application = HD(hd_1='DOC_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260510153000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'EP000016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260510153000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='GAUT08092312', cx_4='QC_RAMQ', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Gauthier', xpn_2='Florence', xpn_3='Anne-Sophie')
        pid.date_time_of_birth = '20080923'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='4218 Rue Sainte-Catherine E', xad_3='Montreal', xad_4='QC', xad_5='H1V 1Y5', xad_6='CA')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ORTHO', pl_2='CLINIC2', pl_3='1', pl_4='CHU_SJ')
        pv1.attending_doctor = XCN(xcn_1='23148', xcn_2='Dubois', xcn_3='Pascal', xcn_6='Dr.', xcn_8='MD')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='CN', cwe_2='Consultation Note', cwe_3='HL70270')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20260510150000'
        txa.origination_date_time = '20260510153000'
        txa.transcriptionist_code_name = XCN(xcn_1='23148', xcn_2='Dubois', xcn_3='Pascal', xcn_6='Dr.', xcn_8='MD')
        txa.parent_document_number = EI(ei_1='DOC7891012')
        txa.document_availability_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='CN', cwe_2='Consultation Note Text', cwe_3='LOCAL')
        obx.obx_5 = (
            'Consultation en orthopedi pediatrique. Scoliose idiopathique adolescente. Angle de Cobb 22 degres. Observation recommandee avec controle rad'
            'iologique dans 6 mois.'
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
    """ Based on live/ca/ca-epic.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='CHU_SJ')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260511080000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EP000017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='ROY26050412', cx_4='QC_RAMQ', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Roy', xpn_2='Olivia', xpn_3='Marie')
        pid.date_time_of_birth = '20260504'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='2945 Rue Guy', xad_3='Montreal', xad_4='QC', xad_5='H3H 2L8', xad_6='CA')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='LAB300500')
        orc.filler_order_number = EI(ei_1='LAB400600')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260511070000'
        orc.orc_12 = '34812^Bouchard^Veronique^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB300500')
        obr.filler_order_number = EI(ei_1='LAB400600')
        obr.universal_service_identifier = CWE(cwe_1='58941-6', cwe_2='Total bilirubin neonatal', cwe_3='LN')
        obr.observation_date_time = '20260511065000'
        obr.obr_16 = '34812^Bouchard^Veronique^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260511075000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='58941-6', cwe_2='Total bilirubin', cwe_3='LN')
        obx.obx_5 = '185'
        obx.units = CWE(cwe_1='umol/L')
        obx.reference_range = '0-205'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1971-1', cwe_2='Direct bilirubin', cwe_3='LN')
        obx_2.obx_5 = '12'
        obx_2.units = CWE(cwe_1='umol/L')
        obx_2.reference_range = '0-34'
        obx_2.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/ca/ca-epic.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='CHU_SJ')
        msh.receiving_application = HD(hd_1='SCHED_RECV')
        msh.receiving_facility = HD(hd_1='OR_SYS')
        msh.date_time_of_message = '20260511140000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'EP000018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT20260525001')
        sch.appointment_reason = CWE(cwe_1='ELECTIVE', cwe_2='Elective', cwe_3='HL70276')
        sch.appointment_type = CWE(cwe_1='SURGERY', cwe_2='Surgical procedure', cwe_3='HL70277')
        sch.sch_9 = '90'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^90^20260525080000^20260525093000'
        sch.placer_contact_person = XCN(xcn_1='23148', xcn_2='Dubois', xcn_3='Pascal', xcn_6='Dr.', xcn_8='MD')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='GAUT08092312', cx_4='QC_RAMQ', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Gauthier', xpn_2='Florence', xpn_3='Anne-Sophie')
        pid.date_time_of_birth = '20080923'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='4218 Rue Sainte-Catherine E', xad_3='Montreal', xad_4='QC', xad_5='H1V 1Y5', xad_6='CA')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='P')
        pv1.assigned_patient_location = PL(pl_1='SURG', pl_2='OR2', pl_3='1', pl_4='CHU_SJ')
        pv1.attending_doctor = XCN(xcn_1='23148', xcn_2='Dubois', xcn_3='Pascal', xcn_6='Dr.', xcn_8='MD')

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
        ais.universal_service_identifier = CWE(cwe_1='SPINE_BRACE', cwe_2='Spinal bracing procedure', cwe_3='LOCAL')
        ais.start_date_time = '20260525080000'
        ais.start_date_time_offset = '0'
        ais.start_date_time_offset_units = CNE(cne_1='MIN')
        ais.duration = '90'
        ais.duration_units = CNE(cne_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='23148', xcn_2='Dubois', xcn_3='Pascal', xcn_6='Dr.', xcn_8='MD')
        aip.start_date_time_offset_units = CNE(cne_1='20260525080000')
        aip.duration = '0'
        aip.duration_units = CNE(cne_1='MIN')
        aip.allow_substitution_code = CWE(cwe_1='90')
        aip.filler_status_code = CWE(cwe_1='MIN')

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
    """ Based on live/ca/ca-epic.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='SICKKIDS')
        msh.receiving_application = HD(hd_1='RAD_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260510170000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EP000019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3782619054', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lefebvre', xpn_2='Liam', xpn_3='Andre')
        pid.date_time_of_birth = '20190627'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='628 University Ave', xad_3='Toronto', xad_4='ON', xad_5='M5G 1Y3', xad_6='CA')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='RAD300500')
        orc.filler_order_number = EI(ei_1='RAD400600')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260510100000'
        orc.orc_12 = '78923^Mehta^Aarav^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='RAD300500')
        obr.filler_order_number = EI(ei_1='RAD400600')
        obr.universal_service_identifier = CWE(cwe_1='70553-6', cwe_2='MRI Brain', cwe_3='LN')
        obr.observation_date_time = '20260510100000'
        obr.obr_16 = '78923^Mehta^Aarav^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260510163000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='MRI Brain Report', cwe_3='EPIC')
        obx.obx_5 = (
            '^AP^^Base64^'
            'JVBERi0xLjUKJeLjz9MKMSAwIG9iago8PC9UeXBlL0NhdGFsb2cvUGFnZXMgMiAwIFIvTWFya0luZm88PC9UeXBlL01hcmtJbmZvL01hcmtlZCB0cnVlPj4+PgplbmRvYmoKMiAwIG9i'
            'ago8PC9UeXBl'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='70553-6', cwe_2='MRI Brain Impression', cwe_3='LN')
        obx_2.obx_5 = 'Normal MRI brain for age. No intracranial mass, hemorrhage, or hydrocephalus. Myelination pattern appropriate for age.'
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
    """ Based on live/ca/ca-epic.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='SICKKIDS')
        msh.receiving_application = HD(hd_1='LAB_RECV')
        msh.receiving_facility = HD(hd_1='EMR_SYS')
        msh.date_time_of_message = '20260509130000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EP000020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='3782619054', cx_4='ON_HN', cx_5='JHN')
        pid.patient_name = XPN(xpn_1='Lefebvre', xpn_2='Liam', xpn_3='Andre')
        pid.date_time_of_birth = '20190627'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='628 University Ave', xad_3='Toronto', xad_4='ON', xad_5='M5G 1Y3', xad_6='CA')

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='LAB300600')
        orc.filler_order_number = EI(ei_1='LAB400700')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260509085000'
        orc.orc_12 = '45612^Reynolds^Catherine^^^Dr.^^MD'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LAB300600')
        obr.filler_order_number = EI(ei_1='LAB400700')
        obr.universal_service_identifier = CWE(cwe_1='92143-7', cwe_2='Resp viral panel', cwe_3='LN')
        obr.observation_date_time = '20260509085000'
        obr.obr_16 = '45612^Reynolds^Catherine^^^Dr.^^MD'
        obr.results_rpt_status_chng_date_time = '20260509123000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='92131-2', cwe_2='RSV', cwe_3='LN')
        obx.obx_5 = '260373001^Detected^SCT'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CWE'
        obx_2.observation_identifier = CWE(cwe_1='92142-9', cwe_2='Influenza A', cwe_3='LN')
        obx_2.obx_5 = '260415000^Not detected^SCT'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CWE'
        obx_3.observation_identifier = CWE(cwe_1='92141-1', cwe_2='Influenza B', cwe_3='LN')
        obx_3.obx_5 = '260415000^Not detected^SCT'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'CWE'
        obx_4.observation_identifier = CWE(cwe_1='94500-6', cwe_2='SARS-CoV-2', cwe_3='LN')
        obx_4.obx_5 = '260415000^Not detected^SCT'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'CWE'
        obx_5.observation_identifier = CWE(cwe_1='88891-7', cwe_2='hMPV', cwe_3='LN')
        obx_5.obx_5 = '260415000^Not detected^SCT'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'CWE'
        obx_6.observation_identifier = CWE(cwe_1='92857-2', cwe_2='Adenovirus', cwe_3='LN')
        obx_6.obx_5 = '260415000^Not detected^SCT'
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
