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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, EI, EIP, FC, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN, XTN
from zato.hl7v2.v2_9.groups import AdtA39Patient, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, \
    OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12Patient
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, EVN, IN1, MRG, MSH, NK1, OBR, OBX, ORC, PD1, PID, PV1, PV2, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('dk', 'dk-sundhedsplatformen.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/dk/dk-sundhedsplatformen.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='RIGSHOSPITALET')
        msh.receiving_application = HD(hd_1='LANDSPATIENTREGISTERET')
        msh.receiving_facility = HD(hd_1='SST')
        msh.date_time_of_message = '20260401070000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'EPICMSG00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260401070000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1207892500', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Kristensen', xpn_2='Astrid', xpn_3='Lykke', xpn_5='')
        pid.date_time_of_birth = '19890712'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Tolderlundsvej 121', xad_3='Viborg', xad_5='8800', xad_6='DK')
        pid.pid_13 = '^^PH^+4572516961~^^CP^+4542586458'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='HÆMA', pl_3='H3041', pl_4='S01')
        pv1.attending_doctor = XCN(xcn_1='10001', xcn_2='Nielsen', xcn_3='Susanne', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='HÆMA')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='10001', xcn_2='Nielsen', xcn_3='Susanne', xcn_6='Dr.')
        pv1.visit_number = CX(cx_1='RH202604010001')
        pv1.prior_temporary_location = PL(pl_1='20260401070000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Akut myeloid leukæmi')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Kristensen', xpn_2='Pia')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Ægtefælle')
        nk1.nk1_5 = '^^CP^+4528314167'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.insurance_company_id = CX(cx_1='REGSYG')
        in1.insurance_company_name = XON(xon_1='Region Hovedstaden')
        in1.insurance_company_address = XAD(xad_1='Kongens Vænge 2', xad_3='Hillerød', xad_5='3400', xad_6='DK')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.extra_segments = [nk1, in1]

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
    """ Based on live/dk/dk-sundhedsplatformen.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='RIGSHOSPITALET')
        msh.receiving_application = HD(hd_1='LANDSPATIENTREGISTERET')
        msh.receiving_facility = HD(hd_1='SST')
        msh.date_time_of_message = '20260402103000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'EPICMSG00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260402103000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1207892500', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Kristensen', xpn_2='Astrid', xpn_3='Lykke', xpn_5='')
        pid.date_time_of_birth = '19890712'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Tolderlundsvej 121', xad_3='Viborg', xad_5='8800', xad_6='DK')
        pid.pid_13 = '^^PH^+4572516961~^^CP^+4542586458'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='INT', pl_3='I2051', pl_4='S03')
        pv1.attending_doctor = XCN(xcn_1='20002', xcn_2='Christiansen', xcn_3='Preben', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='INT')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='20002', xcn_2='Christiansen', xcn_3='Preben', xcn_6='Dr.')
        pv1.visit_number = CX(cx_1='RH202604010001')
        pv1.prior_temporary_location = PL(pl_1='20260402103000')

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
    """ Based on live/dk/dk-sundhedsplatformen.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='RIGSHOSPITALET')
        msh.receiving_application = HD(hd_1='LANDSPATIENTREGISTERET')
        msh.receiving_facility = HD(hd_1='SST')
        msh.date_time_of_message = '20260408160000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'EPICMSG00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260408160000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1207892500', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Kristensen', xpn_2='Astrid', xpn_3='Lykke', xpn_5='')
        pid.date_time_of_birth = '19890712'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Tolderlundsvej 121', xad_3='Viborg', xad_5='8800', xad_6='DK')
        pid.pid_13 = '^^PH^+4572516961~^^CP^+4542586458'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='INT', pl_3='I2051', pl_4='S03')
        pv1.attending_doctor = XCN(xcn_1='20002', xcn_2='Christiansen', xcn_3='Preben', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='INT')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='20002', xcn_2='Christiansen', xcn_3='Preben', xcn_6='Dr.')
        pv1.visit_number = CX(cx_1='RH202604010001')
        pv1.prior_temporary_location = PL(pl_1='20260408160000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Akut myeloid leukæmi')

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
    """ Based on live/dk/dk-sundhedsplatformen.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='HERLEV_HOSPITAL')
        msh.receiving_application = HD(hd_1='LANDSPATIENTREGISTERET')
        msh.receiving_facility = HD(hd_1='SST')
        msh.date_time_of_message = '20260409081500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'EPICMSG00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260409081500'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0504766217', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Vestergaard', xpn_2='Simon', xpn_3='Ejvind', xpn_5='')
        pid.date_time_of_birth = '19760405'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Amagerbrogade 18', xad_3='Charlottenlund', xad_5='2920', xad_6='DK')
        pid.pid_13 = '^^PH^+4576932249~^^CP^+4522975169'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HEH', pl_2='DER', pl_3='AMB01')
        pv1.attending_doctor = XCN(xcn_1='30003', xcn_2='Johansen', xcn_3='Clara', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='DER')
        pv1.financial_class = FC(fc_1='HEH202604090001')
        pv1.admit_date_time = '20260409081500'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Kontrol - malignt melanom')

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
    """ Based on live/dk/dk-sundhedsplatformen.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='HERLEV_HOSPITAL')
        msh.receiving_application = HD(hd_1='LANDSPATIENTREGISTERET')
        msh.receiving_facility = HD(hd_1='SST')
        msh.date_time_of_message = '20260410091000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'EPICMSG00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260410091000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0504766217', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Vestergaard', xpn_2='Simon', xpn_3='Ejvind', xpn_5='')
        pid.date_time_of_birth = '19760405'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Tolderlundsvej 34', xad_3='Risskov', xad_5='8240', xad_6='DK')
        pid.pid_13 = '^^PH^+4556683349~^^CP^+4522975169'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HEH', pl_2='DER', pl_3='AMB01')
        pv1.attending_doctor = XCN(xcn_1='30003', xcn_2='Johansen', xcn_3='Clara', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='DER')
        pv1.financial_class = FC(fc_1='HEH202604090001')
        pv1.admit_date_time = '20260410091000'

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
    """ Based on live/dk/dk-sundhedsplatformen.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='RIGSHOSPITALET')
        msh.receiving_application = HD(hd_1='CPR_REGISTERET')
        msh.receiving_facility = HD(hd_1='SST')
        msh.date_time_of_message = '20260411080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'EPICMSG00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20260411080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2309684042', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Friis', xpn_2='Mette', xpn_3='Lykke', xpn_5='')
        pid.date_time_of_birth = '19680923'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Valby Langgade 141', xad_3='Horsens', xad_5='8700', xad_6='DK')
        pid.pid_13 = '^^PH^+4567932328~^^CP^+4553591793'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = '40004^Bruun^Frederik^^^Dr.'

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
    """ Based on live/dk/dk-sundhedsplatformen.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='RIGSHOSPITALET')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='SST')
        msh.date_time_of_message = '20260412060000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'EPICMSG00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260412060000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1110936519', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Henriksen', xpn_2='Jesper', xpn_3='Vagn', xpn_5='')
        pid.date_time_of_birth = '19931011'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Roskildevej 188', xad_3='Aalborg SØ', xad_5='9220', xad_6='DK')
        pid.pid_13 = '^^PH^+4540563712'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='1837148912', cx_4='CPR', cx_5='NNDN')
        mrg.prior_patient_account_number = CX(cx_1='RH202601200001')

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
    """ Based on live/dk/dk-sundhedsplatformen.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='RIGSHOSPITALET')
        msh.receiving_application = HD(hd_1='LABKA')
        msh.receiving_facility = HD(hd_1='KBA')
        msh.date_time_of_message = '20260413081500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'EPICMSG00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2202756426', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Skov', xpn_2='Tove', xpn_3='Kristine', xpn_5='')
        pid.date_time_of_birth = '19750222'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Frederikssundsvej 123', xad_3='København SV', xad_5='2450', xad_6='DK')
        pid.pid_13 = '^^PH^+4591671935'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='NEF', pl_3='N4021', pl_4='S02')
        pv1.attending_doctor = XCN(xcn_1='50005', xcn_2='Mortensen', xcn_3='Mikkel', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='NEF')
        pv1.financial_class = FC(fc_1='RH202604130001')

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
        orc.placer_order_number = EI(ei_1='ORD20260413001', ei_2='EPIC')
        orc.parent_order = EIP(eip_1='20260413081500')
        orc.orc_11 = '50005^Mortensen^Mikkel^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260413001', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='CREAT', cwe_2='Kreatinin og eGFR', cwe_3='LN')
        obr.observation_date_time = '20260413081500'
        obr.obr_15 = '50005^Mortensen^Mikkel^^^Dr.'

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
        obr_2.placer_order_number = EI(ei_1='ORD20260413001', ei_2='EPIC')
        obr_2.universal_service_identifier = CWE(cwe_1='URINE', cwe_2='Urinstix og mikroskopi', cwe_3='LN')
        obr_2.observation_date_time = '20260413081500'
        obr_2.obr_15 = '50005^Mortensen^Mikkel^^^Dr.'

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
    """ Based on live/dk/dk-sundhedsplatformen.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABKA')
        msh.sending_facility = HD(hd_1='KBA')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='RIGSHOSPITALET')
        msh.date_time_of_message = '20260413141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EPICMSG00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2202756426', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Skov', xpn_2='Tove', xpn_3='Kristine', xpn_5='')
        pid.date_time_of_birth = '19750222'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Frederikssundsvej 123', xad_3='København SV', xad_5='2450', xad_6='DK')
        pid.pid_13 = '^^PH^+4591671935'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='NEF', pl_3='N4021', pl_4='S02')
        pv1.attending_doctor = XCN(xcn_1='50005', xcn_2='Mortensen', xcn_3='Mikkel', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='NEF')
        pv1.financial_class = FC(fc_1='RH202604130001')

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
        orc.placer_order_number = EI(ei_1='ORD20260413001', ei_2='EPIC')
        orc.parent_order = EIP(eip_1='20260413141500')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260413001', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='CREAT', cwe_2='Kreatinin og eGFR', cwe_3='LN')
        obr.observation_date_time = '20260413081500'
        obr.obr_15 = '50005^Mortensen^Mikkel^^^Dr.'
        obr.filler_field_2 = '20260413141500'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='CREA', cwe_2='Kreatinin', cwe_3='LN')
        obx.obx_5 = '198'
        obx.units = CWE(cwe_1='umol/L')
        obx.reference_range = '45-105'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='EGFR', cwe_2='Estimeret GFR', cwe_3='LN')
        obx_2.obx_5 = '28'
        obx_2.units = CWE(cwe_1='mL/min/1.73m2')
        obx_2.reference_range = '>60'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='UREA', cwe_2='Karbamid', cwe_3='LN')
        obx_3.obx_5 = '18.5'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '2.6-6.4'
        obx_3.interpretation_codes = CWE(cwe_1='H')
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
    """ Based on live/dk/dk-sundhedsplatformen.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='RIGSHOSPITALET')
        msh.receiving_application = HD(hd_1='SUNDHED_DK')
        msh.receiving_facility = HD(hd_1='NSP')
        msh.date_time_of_message = '20260414100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EPICMSG00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1207892500', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Kristensen', xpn_2='Astrid', xpn_3='Lykke', xpn_5='')
        pid.date_time_of_birth = '19890712'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Tolderlundsvej 121', xad_3='Viborg', xad_5='8800', xad_6='DK')
        pid.pid_13 = '^^PH^+4572516961'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='INT', pl_3='I2051', pl_4='S03')
        pv1.attending_doctor = XCN(xcn_1='20002', xcn_2='Christiansen', xcn_3='Preben', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='INT')
        pv1.financial_class = FC(fc_1='RH202604010001')

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
        orc.placer_order_number = EI(ei_1='DOC20260414001', ei_2='EPIC')
        orc.parent_order = EIP(eip_1='20260414100000')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='DOC20260414001', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='EPIKRISE', cwe_2='Epikrise - hæmatologi', cwe_3='LN')
        obr.observation_date_time = '20260408160000'
        obr.obr_15 = '20002^Christiansen^Preben^^^Dr.'
        obr.filler_field_2 = '20260414100000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Epikrisenotat', cwe_3='LN')
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
    """ Based on live/dk/dk-sundhedsplatformen.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='HERLEV_HOSPITAL')
        msh.receiving_application = HD(hd_1='PATIENTPORTAL')
        msh.receiving_facility = HD(hd_1='SUNDHED_DK')
        msh.date_time_of_message = '20260415080000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12')
        msh.message_control_id = 'EPICMSG00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT20260501001', ei_2='EPIC')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_3='HL70276')
        sch.appointment_reason = CWE(cwe_1='MRI_SCAN', cwe_2='MR-scanning', cwe_5='EPIC')
        sch.appointment_type = CWE(cwe_1='60')
        sch.sch_9 = 'MIN'
        sch.appointment_duration_units = CNE(cne_3='60', cne_4='20260501100000', cne_5='20260501110000')
        sch.filler_contact_person = XCN(xcn_1='30003', xcn_2='Johansen', xcn_3='Clara', xcn_6='Dr.')
        sch.filler_contact_phone_number = XTN(xtn_3='PH', xtn_4='+4543253881')
        sch.filler_contact_address = XAD(xad_1='HEH', xad_2='RAD', xad_3='MR01')
        sch.filler_contact_location = PL(pl_1='30003', pl_2='Johansen', pl_3='Clara', pl_6='Dr.')
        sch.entered_by_person = XCN(xcn_3='PH', xcn_4='+4543253881')
        sch.sch_21 = 'HEH^RAD^MR01'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0504766217', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Vestergaard', xpn_2='Simon', xpn_3='Ejvind', xpn_5='')
        pid.date_time_of_birth = '19760405'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Tolderlundsvej 34', xad_3='Risskov', xad_5='8240', xad_6='DK')
        pid.pid_13 = '^^CP^+4522975169'

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='MRI', cwe_2='MR-scanning af cerebrum', cwe_3='LOCAL')
        ais.start_date_time = '20260501100000'
        ais.start_date_time_offset_units = CNE(cne_1='60')
        ais.duration = 'MIN'

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='HEH', pl_2='RAD', pl_3='MR01')

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='30003', xcn_2='Johansen', xcn_3='Clara', xcn_6='Dr.')

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
    """ Based on live/dk/dk-sundhedsplatformen.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='HERLEV_HOSPITAL')
        msh.receiving_application = HD(hd_1='PATIENTPORTAL')
        msh.receiving_facility = HD(hd_1='SUNDHED_DK')
        msh.date_time_of_message = '20260416090000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S14')
        msh.message_control_id = 'EPICMSG00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT20260501001', ei_2='EPIC')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_3='HL70276')
        sch.appointment_reason = CWE(cwe_1='MRI_SCAN', cwe_2='MR-scanning', cwe_5='EPIC')
        sch.appointment_type = CWE(cwe_1='60')
        sch.sch_9 = 'MIN'
        sch.appointment_duration_units = CNE(cne_3='60', cne_4='20260508100000', cne_5='20260508110000')
        sch.filler_contact_person = XCN(xcn_1='30003', xcn_2='Johansen', xcn_3='Clara', xcn_6='Dr.')
        sch.filler_contact_phone_number = XTN(xtn_3='PH', xtn_4='+4543253881')
        sch.filler_contact_address = XAD(xad_1='HEH', xad_2='RAD', xad_3='MR01')
        sch.filler_contact_location = PL(pl_1='30003', pl_2='Johansen', pl_3='Clara', pl_6='Dr.')
        sch.entered_by_person = XCN(xcn_3='PH', xcn_4='+4543253881')
        sch.sch_21 = 'HEH^RAD^MR01'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0504766217', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Vestergaard', xpn_2='Simon', xpn_3='Ejvind', xpn_5='')
        pid.date_time_of_birth = '19760405'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Tolderlundsvej 34', xad_3='Risskov', xad_5='8240', xad_6='DK')
        pid.pid_13 = '^^CP^+4522975169'

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='MRI', cwe_2='MR-scanning af cerebrum', cwe_3='LOCAL')
        ais.start_date_time = '20260508100000'
        ais.start_date_time_offset_units = CNE(cne_1='60')
        ais.duration = 'MIN'

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='HEH', pl_2='RAD', pl_3='MR01')

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='30003', xcn_2='Johansen', xcn_3='Clara', xcn_6='Dr.')

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
    """ Based on live/dk/dk-sundhedsplatformen.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='RIGSHOSPITALET')
        msh.receiving_application = HD(hd_1='SECTRA_RIS')
        msh.receiving_facility = HD(hd_1='RH_RAD')
        msh.date_time_of_message = '20260417091000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'EPICMSG00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1108808105', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Svendsen', xpn_2='Mikkel', xpn_3='Frode', xpn_5='')
        pid.date_time_of_birth = '19800811'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Amagerbrogade 231', xad_3='Odense N', xad_5='5200', xad_6='DK')
        pid.pid_13 = '^^PH^+4561662884'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='AKM', pl_3='AK101')
        pv1.attending_doctor = XCN(xcn_1='60006', xcn_2='Møller', xcn_3='Camilla', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='AKM')
        pv1.financial_class = FC(fc_1='RH202604170001')

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
        orc.placer_order_number = EI(ei_1='ORD20260417001', ei_2='EPIC')
        orc.parent_order = EIP(eip_1='20260417091000')
        orc.orc_11 = '60006^Møller^Camilla^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260417001', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='CTABD', cwe_2='CT af abdomen med kontrast', cwe_3='LOCAL')
        obr.observation_date_time = '20260417091000'
        obr.relevant_clinical_information = CWE(cwe_1='Akut abdomen, mistanke om ileus')
        obr.obr_14 = '60006^Møller^Camilla^^^Dr.'

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
    """ Based on live/dk/dk-sundhedsplatformen.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SECTRA_RIS')
        msh.sending_facility = HD(hd_1='RH_RAD')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='RIGSHOSPITALET')
        msh.date_time_of_message = '20260417141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EPICMSG00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1108808105', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Svendsen', xpn_2='Mikkel', xpn_3='Frode', xpn_5='')
        pid.date_time_of_birth = '19800811'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Amagerbrogade 231', xad_3='Odense N', xad_5='5200', xad_6='DK')
        pid.pid_13 = '^^PH^+4561662884'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='AKM', pl_3='AK101')
        pv1.attending_doctor = XCN(xcn_1='60006', xcn_2='Møller', xcn_3='Camilla', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='AKM')
        pv1.financial_class = FC(fc_1='RH202604170001')

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
        orc.placer_order_number = EI(ei_1='ORD20260417001', ei_2='EPIC')
        orc.parent_order = EIP(eip_1='20260417141500')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260417001', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='CTABD', cwe_2='CT af abdomen med kontrast', cwe_3='LOCAL')
        obr.observation_date_time = '20260417091000'
        obr.obr_15 = '60006^Møller^Camilla^^^Dr.'
        obr.filler_field_2 = '20260417141500'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='RADRPT', cwe_2='Radiologibeskrivelse', cwe_3='LN')
        obx.obx_5 = (
            'CT abdomen med iv kontrast: Ingen tegn på ileus. Normal tarmmotilitet. Ingen fri luft. Leverparenchymet normalt. Ingen hydronefrose. Konkl: '
            'Normalt fund.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Radiologirapport', cwe_3='LN')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKJcfsDecKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0Nv'
            'dW50IDEKL01lZGlhQm94IFswIDAgNTk1IDg0Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK'
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
    """ Based on live/dk/dk-sundhedsplatformen.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='RIGSHOSPITALET')
        msh.receiving_application = HD(hd_1='DOKUMENTDELING')
        msh.receiving_facility = HD(hd_1='NSP')
        msh.date_time_of_message = '20260418120000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02')
        msh.message_control_id = 'EPICMSG00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260418120000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1207892500', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Kristensen', xpn_2='Astrid', xpn_3='Lykke', xpn_5='')
        pid.date_time_of_birth = '19890712'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Tolderlundsvej 121', xad_3='Viborg', xad_5='8800', xad_6='DK')
        pid.pid_13 = '^^PH^+4572516961'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='HÆMA', pl_3='H3041', pl_4='S01')
        pv1.attending_doctor = XCN(xcn_1='10001', xcn_2='Nielsen', xcn_3='Susanne', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='HÆMA')
        pv1.financial_class = FC(fc_1='RH202604010001')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='CN', cwe_2='Klinisk notat')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20260418120000'
        txa.primary_activity_provider_code_name = XCN(xcn_1='10001', xcn_2='Nielsen', xcn_3='Susanne', xcn_6='Dr.')
        txa.transcription_date_time = '20260418120000'
        txa.unique_document_number = EI(ei_1='DOC20260418001')
        txa.document_confidentiality_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='NOTE', cwe_2='Klinisk notat', cwe_3='LN')
        obx.obx_5 = (
            'Patienten har gennemført 2. serie kemoterapi. Tolererer behandlingen godt. Ingen tegn på infektion. Næste serie planlagt om 3 uger. Blodprøv'
            'ekontrol inden da.'
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
    """ Based on live/dk/dk-sundhedsplatformen.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABKA')
        msh.sending_facility = HD(hd_1='KBA')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='RIGSHOSPITALET')
        msh.date_time_of_message = '20260419101500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EPICMSG00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1506833631', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Krogh', xpn_2='Karsten', xpn_3='Bo', xpn_5='')
        pid.date_time_of_birth = '19830615'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Torvegade 102', xad_3='Vanløse', xad_5='2720', xad_6='DK')
        pid.pid_13 = '^^PH^+4563121640'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='KIR', pl_3='K5031', pl_4='S04')
        pv1.attending_doctor = XCN(xcn_1='70007', xcn_2='Svendsen', xcn_3='Freja', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='KIR')
        pv1.financial_class = FC(fc_1='RH202604190001')

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
        orc.placer_order_number = EI(ei_1='ORD20260419001', ei_2='LABKA')
        orc.parent_order = EIP(eip_1='20260419101500')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260419001', ei_2='LABKA')
        obr.universal_service_identifier = CWE(cwe_1='KOAG', cwe_2='Koagulationstal', cwe_3='LN')
        obr.observation_date_time = '20260419083000'
        obr.obr_15 = '70007^Svendsen^Freja^^^Dr.'
        obr.filler_field_2 = '20260419101500'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='INR', cwe_2='International Normalised Ratio', cwe_3='LN')
        obx.obx_5 = '2.8'
        obx.reference_range = '0.8-1.2'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='APTT', cwe_2='Aktiveret partiel tromboplastintid', cwe_3='LN')
        obx_2.obx_5 = '42'
        obx_2.units = CWE(cwe_1='sek')
        obx_2.reference_range = '25-38'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='FBLOOD', cwe_2='Fibrinogen', cwe_3='LN')
        obx_3.obx_5 = '4.2'
        obx_3.units = CWE(cwe_1='g/L')
        obx_3.reference_range = '1.8-4.0'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='DDIMER', cwe_2='D-dimer', cwe_3='LN')
        obx_4.obx_5 = '1.8'
        obx_4.units = CWE(cwe_1='mg/L FEU')
        obx_4.reference_range = '<0.5'
        obx_4.interpretation_codes = CWE(cwe_1='H')
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
    """ Based on live/dk/dk-sundhedsplatformen.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='RIGSHOSPITALET')
        msh.receiving_application = HD(hd_1='LANDSPATIENTREGISTERET')
        msh.receiving_facility = HD(hd_1='SST')
        msh.date_time_of_message = '20260420013000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'EPICMSG00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260420013000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2801904893', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Christensen', xpn_2='Knud', xpn_3='Verner', xpn_5='')
        pid.date_time_of_birth = '19900128'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vibevej 204', xad_3='Odense V', xad_5='5210', xad_6='DK')
        pid.pid_13 = '^^CP^+4521449448'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='AKM', pl_3='AK101')
        pv1.attending_doctor = XCN(xcn_1='60006', xcn_2='Møller', xcn_3='Camilla', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='AKM')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='60006', xcn_2='Møller', xcn_3='Camilla', xcn_6='Dr.')
        pv1.visit_number = CX(cx_1='RH202604200001')
        pv1.prior_temporary_location = PL(pl_1='20260420013000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Trafikuheld - polytrauma')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Møller', xpn_2='Anders')
        nk1.relationship = CWE(cwe_1='SIS', cwe_2='Søster')
        nk1.nk1_5 = '^^CP^+4550365330'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.extra_segments = [nk1]

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
    """ Based on live/dk/dk-sundhedsplatformen.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='RIGSHOSPITALET')
        msh.receiving_application = HD(hd_1='LABKA')
        msh.receiving_facility = HD(hd_1='KBA')
        msh.date_time_of_message = '20260420020000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'EPICMSG00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2801904893', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Christensen', xpn_2='Knud', xpn_3='Verner', xpn_5='')
        pid.date_time_of_birth = '19900128'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vibevej 204', xad_3='Odense V', xad_5='5210', xad_6='DK')
        pid.pid_13 = '^^CP^+4521449448'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='AKM', pl_3='AK101')
        pv1.attending_doctor = XCN(xcn_1='60006', xcn_2='Møller', xcn_3='Camilla', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='AKM')
        pv1.financial_class = FC(fc_1='RH202604200001')

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
        orc.placer_order_number = EI(ei_1='ORD20260420001', ei_2='EPIC')
        orc.parent_order = EIP(eip_1='20260420020000')
        orc.orc_11 = '60006^Møller^Camilla^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260420001', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='TRAUMA', cwe_2='Traumepakke', cwe_3='LN')
        obr.observation_date_time = '20260420020000'
        obr.obr_15 = '60006^Møller^Camilla^^^Dr.'

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
        obr_2.placer_order_number = EI(ei_1='ORD20260420001', ei_2='EPIC')
        obr_2.universal_service_identifier = CWE(cwe_1='FORLIG', cwe_2='Forligelighedsprøve', cwe_3='LN')
        obr_2.observation_date_time = '20260420020000'
        obr_2.relevant_clinical_information = CWE(cwe_1='AKUT - 4 SAG blod bestilt')
        obr_2.obr_14 = '60006^Møller^Camilla^^^Dr.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2]

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
    """ Based on live/dk/dk-sundhedsplatformen.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABKA')
        msh.sending_facility = HD(hd_1='KBA')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='RIGSHOSPITALET')
        msh.date_time_of_message = '20260420023000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EPICMSG00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2801904893', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Christensen', xpn_2='Knud', xpn_3='Verner', xpn_5='')
        pid.date_time_of_birth = '19900128'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vibevej 204', xad_3='Odense V', xad_5='5210', xad_6='DK')
        pid.pid_13 = '^^CP^+4521449448'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='RH', pl_2='AKM', pl_3='AK101')
        pv1.attending_doctor = XCN(xcn_1='60006', xcn_2='Møller', xcn_3='Camilla', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='AKM')
        pv1.financial_class = FC(fc_1='RH202604200001')

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
        orc.placer_order_number = EI(ei_1='ORD20260420002', ei_2='LABKA')
        orc.parent_order = EIP(eip_1='20260420023000')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260420002', ei_2='LABKA')
        obr.universal_service_identifier = CWE(cwe_1='ABGAS', cwe_2='Arteriel blodgas', cwe_3='LN')
        obr.observation_date_time = '20260420021500'
        obr.obr_15 = '60006^Møller^Camilla^^^Dr.'
        obr.filler_field_2 = '20260420023000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='PH', cwe_2='pH', cwe_3='LN')
        obx.obx_5 = '7.31'
        obx.reference_range = '7.35-7.45'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='PCO2', cwe_2='pCO2', cwe_3='LN')
        obx_2.obx_5 = '5.8'
        obx_2.units = CWE(cwe_1='kPa')
        obx_2.reference_range = '4.7-6.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='PO2', cwe_2='pO2', cwe_3='LN')
        obx_3.obx_5 = '8.2'
        obx_3.units = CWE(cwe_1='kPa')
        obx_3.reference_range = '10.0-13.3'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='HCO3', cwe_2='Bikarbonat', cwe_3='LN')
        obx_4.obx_5 = '19.5'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '22-26'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='LACT', cwe_2='Laktat', cwe_3='LN')
        obx_5.obx_5 = '4.2'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '0.5-2.0'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='BE', cwe_2='Base Excess', cwe_3='LN')
        obx_6.obx_5 = '-6.5'
        obx_6.units = CWE(cwe_1='mmol/L')
        obx_6.reference_range = '-3.0-3.0'
        obx_6.interpretation_codes = CWE(cwe_1='L')
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
    """ Based on live/dk/dk-sundhedsplatformen.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABKA')
        msh.sending_facility = HD(hd_1='KBA')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='HERLEV_HOSPITAL')
        msh.date_time_of_message = '20260421100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'EPICMSG00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2309684042', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Friis', xpn_2='Mette', xpn_3='Lykke', xpn_5='')
        pid.date_time_of_birth = '19680923'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Valby Langgade 141', xad_3='Horsens', xad_5='8700', xad_6='DK')
        pid.pid_13 = '^^PH^+4567932328'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HEH', pl_2='END', pl_3='AMB01')
        pv1.attending_doctor = XCN(xcn_1='40004', xcn_2='Bruun', xcn_3='Frederik', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='END')
        pv1.financial_class = FC(fc_1='HEH202604210001')

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
        orc.parent_order = EIP(eip_1='20260421100000')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260421001', ei_2='LABKA')
        obr.universal_service_identifier = CWE(cwe_1='THYR', cwe_2='Thyroideatal', cwe_3='LN')
        obr.observation_date_time = '20260421083000'
        obr.obr_15 = '40004^Bruun^Frederik^^^Dr.'
        obr.filler_field_2 = '20260421100000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='TSH', cwe_2='Thyreoideastimulerende hormon', cwe_3='LN')
        obx.obx_5 = '0.08'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.27-4.20'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='FT4', cwe_2='Frit thyroxin', cwe_3='LN')
        obx_2.obx_5 = '32.5'
        obx_2.units = CWE(cwe_1='pmol/L')
        obx_2.reference_range = '12.0-22.0'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='FT3', cwe_2='Frit trijodthyronin', cwe_3='LN')
        obx_3.obx_5 = '9.8'
        obx_3.units = CWE(cwe_1='pmol/L')
        obx_3.reference_range = '3.1-6.8'
        obx_3.interpretation_codes = CWE(cwe_1='H')
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
