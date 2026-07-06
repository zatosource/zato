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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, EI, EIP, FC, HD, MOC, MSG, PL, PT, VID, XAD, XCN, XPN, XTN
from zato.hl7v2.v2_9.groups import MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, \
    OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12Patient
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, EVN, MSH, NK1, OBR, OBX, ORC, PID, PV1, PV2, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('dk', 'dk-columna-flow.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/dk/dk-columna-flow.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_FLOW')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='COLUMNA_CIS')
        msh.receiving_facility = HD(hd_1='AALBORG_UH')
        msh.date_time_of_message = '20260401070000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'CF00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260401070000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1404875050', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Nørgaard', xpn_2='Clara', xpn_3='Gerda', xpn_5='')
        pid.date_time_of_birth = '19870414'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Valby Langgade 50', xad_3='Roskilde', xad_5='4000', xad_6='DK')
        pid.pid_13 = '^^PH^+4569371022~^^CP^+4531532788'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='AKM', pl_3='101', pl_4='A1')
        pv1.attending_doctor = XCN(xcn_1='11001', xcn_2='Andersen', xcn_3='Julie', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='AKM')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='11001', xcn_2='Andersen', xcn_3='Julie', xcn_6='Dr.')
        pv1.visit_number = CX(cx_1='AAUH202604010001')
        pv1.prior_temporary_location = PL(pl_1='20260401070000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Brystsmerter')

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
    """ Based on live/dk/dk-columna-flow.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_FLOW')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='COLUMNA_CIS')
        msh.receiving_facility = HD(hd_1='AALBORG_UH')
        msh.date_time_of_message = '20260401071000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'CF00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260401071000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1404875050', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Nørgaard', xpn_2='Clara', xpn_3='Gerda', xpn_5='')
        pid.date_time_of_birth = '19870414'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Valby Langgade 50', xad_3='Roskilde', xad_5='4000', xad_6='DK')
        pid.pid_13 = '^^PH^+4569371022~^^CP^+4531532788'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='AKM', pl_3='101', pl_4='A1')
        pv1.attending_doctor = XCN(xcn_1='11001', xcn_2='Andersen', xcn_3='Julie', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='AKM')
        pv1.admit_source = CWE(cwe_1='2')
        pv1.admitting_doctor = XCN(xcn_1='11001', xcn_2='Andersen', xcn_3='Julie', xcn_6='Dr.')
        pv1.visit_number = CX(cx_1='AAUH202604010001')
        pv1.prior_temporary_location = PL(pl_1='20260401071000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Brystsmerter - triage orange')

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/dk/dk-columna-flow.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_FLOW')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='COLUMNA_CIS')
        msh.receiving_facility = HD(hd_1='AALBORG_UH')
        msh.date_time_of_message = '20260401100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'CF00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260401100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1404875050', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Nørgaard', xpn_2='Clara', xpn_3='Gerda', xpn_5='')
        pid.date_time_of_birth = '19870414'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Valby Langgade 50', xad_3='Roskilde', xad_5='4000', xad_6='DK')
        pid.pid_13 = '^^PH^+4569371022~^^CP^+4531532788'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='KAR', pl_3='501', pl_4='B2')
        pv1.attending_doctor = XCN(xcn_1='22002', xcn_2='Johansen', xcn_3='Susanne', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='KAR')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='22002', xcn_2='Johansen', xcn_3='Susanne', xcn_6='Dr.')
        pv1.visit_number = CX(cx_1='AAUH202604010001')
        pv1.prior_temporary_location = PL(pl_1='20260401100000')

        # .. assemble the full message ..
        msg = ADT_A02()
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
    """ Based on live/dk/dk-columna-flow.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_FLOW')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='COLUMNA_CIS')
        msh.receiving_facility = HD(hd_1='AALBORG_UH')
        msh.date_time_of_message = '20260402080000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12')
        msh.message_control_id = 'CF00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='OP20260405001', ei_2='COLUMNA_FLOW')
        sch.event_reason = CWE(cwe_1='ELECTIVE', cwe_3='HL70276')
        sch.appointment_reason = CWE(cwe_1='CABG', cwe_2='Koronar bypass', cwe_5='FLOW')
        sch.appointment_type = CWE(cwe_1='180')
        sch.sch_9 = 'MIN'
        sch.appointment_duration_units = CNE(cne_3='180', cne_4='20260405080000', cne_5='20260405110000')
        sch.filler_contact_person = XCN(xcn_1='33003', xcn_2='Andersen', xcn_3='Bodil', xcn_6='Dr.')
        sch.filler_contact_phone_number = XTN(xtn_3='PH', xtn_4='+4583825540')
        sch.filler_contact_address = XAD(xad_1='AAUH', xad_2='KIR', xad_3='OP01')
        sch.filler_contact_location = PL(pl_1='33003', pl_2='Andersen', pl_3='Bodil', pl_6='Dr.')
        sch.entered_by_person = XCN(xcn_3='PH', xcn_4='+4583825540')
        sch.sch_21 = 'AAUH^KIR^OP01'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1404875050', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Nørgaard', xpn_2='Clara', xpn_3='Gerda', xpn_5='')
        pid.date_time_of_birth = '19870414'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Valby Langgade 50', xad_3='Roskilde', xad_5='4000', xad_6='DK')
        pid.pid_13 = '^^CP^+4531532788'

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='CABG', cwe_2='Koronar bypass operation', cwe_3='LOCAL')
        ais.start_date_time = '20260405080000'
        ais.start_date_time_offset_units = CNE(cne_1='180')
        ais.duration = 'MIN'

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='AAUH', pl_2='KIR', pl_3='OP01')

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='33003', xcn_2='Andersen', xcn_3='Bodil', xcn_6='Dr.')

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.extra_segments = [ais, ail, aip]

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
    """ Based on live/dk/dk-columna-flow.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_FLOW')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='COLUMNA_CIS')
        msh.receiving_facility = HD(hd_1='AALBORG_UH')
        msh.date_time_of_message = '20260403090000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S14')
        msh.message_control_id = 'CF00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='OP20260405001', ei_2='COLUMNA_FLOW')
        sch.event_reason = CWE(cwe_1='ELECTIVE', cwe_3='HL70276')
        sch.appointment_reason = CWE(cwe_1='CABG', cwe_2='Koronar bypass', cwe_5='FLOW')
        sch.appointment_type = CWE(cwe_1='180')
        sch.sch_9 = 'MIN'
        sch.appointment_duration_units = CNE(cne_3='180', cne_4='20260407080000', cne_5='20260407110000')
        sch.filler_contact_person = XCN(xcn_1='33003', xcn_2='Andersen', xcn_3='Bodil', xcn_6='Dr.')
        sch.filler_contact_phone_number = XTN(xtn_3='PH', xtn_4='+4583825540')
        sch.filler_contact_address = XAD(xad_1='AAUH', xad_2='KIR', xad_3='OP01')
        sch.filler_contact_location = PL(pl_1='33003', pl_2='Andersen', pl_3='Bodil', pl_6='Dr.')
        sch.entered_by_person = XCN(xcn_3='PH', xcn_4='+4583825540')
        sch.sch_21 = 'AAUH^KIR^OP01'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1404875050', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Nørgaard', xpn_2='Clara', xpn_3='Gerda', xpn_5='')
        pid.date_time_of_birth = '19870414'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Valby Langgade 50', xad_3='Roskilde', xad_5='4000', xad_6='DK')
        pid.pid_13 = '^^CP^+4531532788'

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='CABG', cwe_2='Koronar bypass operation', cwe_3='LOCAL')
        ais.start_date_time = '20260407080000'
        ais.start_date_time_offset_units = CNE(cne_1='180')
        ais.duration = 'MIN'

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='AAUH', pl_2='KIR', pl_3='OP01')

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='33003', xcn_2='Andersen', xcn_3='Bodil', xcn_6='Dr.')

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.extra_segments = [ais, ail, aip]

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
    """ Based on live/dk/dk-columna-flow.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_FLOW')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='LANDSPATIENTREGISTERET')
        msh.receiving_facility = HD(hd_1='SST')
        msh.date_time_of_message = '20260404020000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'CF00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260404020000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2506957767', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Olsen', xpn_2='Peter', xpn_3='Holger', xpn_5='')
        pid.date_time_of_birth = '19950625'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Åboulevarden 84', xad_3='København N', xad_5='2200', xad_6='DK')
        pid.pid_13 = '^^CP^+4560328811'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='AKM', pl_3='101', pl_4='A3')
        pv1.attending_doctor = XCN(xcn_1='44004', xcn_2='Johansen', xcn_3='Britt', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='AKM')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='44004', xcn_2='Johansen', xcn_3='Britt', xcn_6='Dr.')
        pv1.visit_number = CX(cx_1='AAUH202604040001')
        pv1.prior_temporary_location = PL(pl_1='20260404020000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Fraktur af distale radius')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Larsen', xpn_2='Rasmus')
        nk1.relationship = CWE(cwe_1='GIRLF', cwe_2='Kæreste')
        nk1.nk1_5 = '^^CP^+4553251115'

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
    """ Based on live/dk/dk-columna-flow.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_FLOW')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='LABKA')
        msh.receiving_facility = HD(hd_1='KBA')
        msh.date_time_of_message = '20260404021000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'CF00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2506957767', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Olsen', xpn_2='Peter', xpn_3='Holger', xpn_5='')
        pid.date_time_of_birth = '19950625'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Åboulevarden 84', xad_3='København N', xad_5='2200', xad_6='DK')
        pid.pid_13 = '^^CP^+4560328811'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='AKM', pl_3='101', pl_4='A3')
        pv1.attending_doctor = XCN(xcn_1='44004', xcn_2='Johansen', xcn_3='Britt', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='AKM')
        pv1.financial_class = FC(fc_1='AAUH202604040001')

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
        orc.placer_order_number = EI(ei_1='ORD20260404001', ei_2='COLUMNA_FLOW')
        orc.parent_order = EIP(eip_1='20260404021000')
        orc.orc_11 = '44004^Johansen^Britt^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260404001', ei_2='COLUMNA_FLOW')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Komplet blodtælling', cwe_3='LN')
        obr.observation_date_time = '20260404021000'
        obr.relevant_clinical_information = CWE(cwe_1='AKUT - fraktur, præoperativ')
        obr.obr_14 = '44004^Johansen^Britt^^^Dr.'

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
        obr_2.placer_order_number = EI(ei_1='ORD20260404001', ei_2='COLUMNA_FLOW')
        obr_2.universal_service_identifier = CWE(cwe_1='KOAG', cwe_2='Koagulationstal', cwe_3='LN')
        obr_2.observation_date_time = '20260404021000'
        obr_2.obr_15 = '44004^Johansen^Britt^^^Dr.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2]

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
    """ Based on live/dk/dk-columna-flow.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_FLOW')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='CARESTREAM_RIS')
        msh.receiving_facility = HD(hd_1='AAUH_RAD')
        msh.date_time_of_message = '20260404022000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'CF00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2506957767', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Olsen', xpn_2='Peter', xpn_3='Holger', xpn_5='')
        pid.date_time_of_birth = '19950625'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Åboulevarden 84', xad_3='København N', xad_5='2200', xad_6='DK')
        pid.pid_13 = '^^CP^+4560328811'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='AKM', pl_3='101', pl_4='A3')
        pv1.attending_doctor = XCN(xcn_1='44004', xcn_2='Johansen', xcn_3='Britt', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='AKM')
        pv1.financial_class = FC(fc_1='AAUH202604040001')

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
        orc.placer_order_number = EI(ei_1='ORD20260404002', ei_2='COLUMNA_FLOW')
        orc.parent_order = EIP(eip_1='20260404022000')
        orc.orc_11 = '44004^Johansen^Britt^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260404002', ei_2='COLUMNA_FLOW')
        obr.universal_service_identifier = CWE(cwe_1='XWRIST', cwe_2='Røntgen af håndled', cwe_3='LOCAL')
        obr.observation_date_time = '20260404022000'
        obr.relevant_clinical_information = CWE(cwe_1='Fald på cykel, smerter i ve. håndled')
        obr.obr_14 = '44004^Johansen^Britt^^^Dr.'

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
    """ Based on live/dk/dk-columna-flow.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABKA')
        msh.sending_facility = HD(hd_1='KBA')
        msh.receiving_application = HD(hd_1='COLUMNA_FLOW')
        msh.receiving_facility = HD(hd_1='AALBORG_UH')
        msh.date_time_of_message = '20260404031500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CF00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2506957767', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Olsen', xpn_2='Peter', xpn_3='Holger', xpn_5='')
        pid.date_time_of_birth = '19950625'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Åboulevarden 84', xad_3='København N', xad_5='2200', xad_6='DK')
        pid.pid_13 = '^^CP^+4560328811'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='AKM', pl_3='101', pl_4='A3')
        pv1.attending_doctor = XCN(xcn_1='44004', xcn_2='Johansen', xcn_3='Britt', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='AKM')
        pv1.financial_class = FC(fc_1='AAUH202604040001')

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
        orc.placer_order_number = EI(ei_1='ORD20260404001', ei_2='COLUMNA_FLOW')
        orc.parent_order = EIP(eip_1='20260404031500')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260404001', ei_2='COLUMNA_FLOW')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Komplet blodtælling', cwe_3='LN')
        obr.observation_date_time = '20260404021000'
        obr.obr_15 = '44004^Johansen^Britt^^^Dr.'
        obr.filler_field_2 = '20260404031500'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='HGB', cwe_2='Hæmoglobin', cwe_3='LN')
        obx.obx_5 = '9.2'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '8.3-10.5'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='PLT', cwe_2='Trombocytter', cwe_3='LN')
        obx_2.obx_5 = '265'
        obx_2.units = CWE(cwe_1='10*9/L')
        obx_2.reference_range = '145-390'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='INR', cwe_2='International Normalised Ratio', cwe_3='LN')
        obx_3.obx_5 = '1.0'
        obx_3.reference_range = '0.8-1.2'
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
    """ Based on live/dk/dk-columna-flow.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARESTREAM_RIS')
        msh.sending_facility = HD(hd_1='AAUH_RAD')
        msh.receiving_application = HD(hd_1='COLUMNA_FLOW')
        msh.receiving_facility = HD(hd_1='AALBORG_UH')
        msh.date_time_of_message = '20260404040000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CF00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2506957767', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Olsen', xpn_2='Peter', xpn_3='Holger', xpn_5='')
        pid.date_time_of_birth = '19950625'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Åboulevarden 84', xad_3='København N', xad_5='2200', xad_6='DK')
        pid.pid_13 = '^^CP^+4560328811'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='AKM', pl_3='101', pl_4='A3')
        pv1.attending_doctor = XCN(xcn_1='44004', xcn_2='Johansen', xcn_3='Britt', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='AKM')
        pv1.financial_class = FC(fc_1='AAUH202604040001')

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
        orc.placer_order_number = EI(ei_1='ORD20260404002', ei_2='COLUMNA_FLOW')
        orc.parent_order = EIP(eip_1='20260404040000')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260404002', ei_2='COLUMNA_FLOW')
        obr.universal_service_identifier = CWE(cwe_1='XWRIST', cwe_2='Røntgen af håndled', cwe_3='LOCAL')
        obr.observation_date_time = '20260404022000'
        obr.obr_15 = '44004^Johansen^Britt^^^Dr.'
        obr.placer_field_1 = '55001^Nielsen^Niels^^^Dr.'
        obr.filler_field_1 = '20260404040000'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='RADRPT', cwe_2='Radiologibeskrivelse', cwe_3='LN')
        obx.obx_5 = (
            'Røntgen af ve. håndled AP og lateral: Fraktur af distale radius med dorsal angulation og let forkortning. Ingen ulnafraktur. Colles-fraktur.'
            ' Anbefaler reposition i lokal bedøvelse.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Røntgenrapport', cwe_3='LN')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK'
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
    """ Based on live/dk/dk-columna-flow.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_FLOW')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='LANDSPATIENTREGISTERET')
        msh.receiving_facility = HD(hd_1='SST')
        msh.date_time_of_message = '20260404080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'CF00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260404080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2506957767', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Olsen', xpn_2='Peter', xpn_3='Holger', xpn_5='')
        pid.date_time_of_birth = '19950625'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Åboulevarden 84', xad_3='København N', xad_5='2200', xad_6='DK')
        pid.pid_13 = '^^CP^+4560328811'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='AKM', pl_3='101', pl_4='A3')
        pv1.attending_doctor = XCN(xcn_1='44004', xcn_2='Johansen', xcn_3='Britt', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='AKM')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='44004', xcn_2='Johansen', xcn_3='Britt', xcn_6='Dr.')
        pv1.visit_number = CX(cx_1='AAUH202604040001')
        pv1.prior_temporary_location = PL(pl_1='20260404080000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Fraktur af distale radius - behandlet, reposition og gipsskinne')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/dk/dk-columna-flow.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_FLOW')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='COLUMNA_CIS')
        msh.receiving_facility = HD(hd_1='AALBORG_UH')
        msh.date_time_of_message = '20260405063000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'CF00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260405063000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1209739768', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Larsen', xpn_2='Kirsten', xpn_3='Karla', xpn_5='')
        pid.date_time_of_birth = '19730912'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Danmarksgade 113', xad_3='Hillerød', xad_5='3400', xad_6='DK')
        pid.pid_13 = '^^PH^+4553214566~^^CP^+4525833389'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='KIR', pl_3='DAG01')
        pv1.attending_doctor = XCN(xcn_1='55005', xcn_2='Svendsen', xcn_3='Jonas', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='KIR')
        pv1.financial_class = FC(fc_1='AAUH202604050001')
        pv1.admit_date_time = '20260405063000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Laparoskopisk kolecystektomi')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/dk/dk-columna-flow.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_FLOW')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='PATIENTPORTAL')
        msh.receiving_facility = HD(hd_1='SUNDHED_DK')
        msh.date_time_of_message = '20260406080000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12')
        msh.message_control_id = 'CF00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT20260501001', ei_2='COLUMNA_FLOW')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_3='HL70276')
        sch.appointment_reason = CWE(cwe_1='KONTROL', cwe_2='Ortopædisk kontrol', cwe_5='FLOW')
        sch.appointment_type = CWE(cwe_1='15')
        sch.sch_9 = 'MIN'
        sch.appointment_duration_units = CNE(cne_3='15', cne_4='20260501100000', cne_5='20260501101500')
        sch.filler_contact_person = XCN(xcn_1='66006', xcn_2='Friis', xcn_3='Jens', xcn_6='Dr.')
        sch.filler_contact_phone_number = XTN(xtn_3='PH', xtn_4='+4594742377')
        sch.filler_contact_address = XAD(xad_1='AAUH', xad_2='ORT', xad_3='AMB01')
        sch.filler_contact_location = PL(pl_1='66006', pl_2='Friis', pl_3='Jens', pl_6='Dr.')
        sch.entered_by_person = XCN(xcn_3='PH', xcn_4='+4594742377')
        sch.sch_21 = 'AAUH^ORT^AMB01'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2506957767', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Olsen', xpn_2='Peter', xpn_3='Holger', xpn_5='')
        pid.date_time_of_birth = '19950625'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Åboulevarden 84', xad_3='København N', xad_5='2200', xad_6='DK')
        pid.pid_13 = '^^CP^+4560328811'

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='KONTROL', cwe_2='Kontrolrøntgen - håndled', cwe_3='LOCAL')
        ais.start_date_time = '20260501100000'
        ais.start_date_time_offset_units = CNE(cne_1='15')
        ais.duration = 'MIN'

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='AAUH', pl_2='ORT', pl_3='AMB01')

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='66006', xcn_2='Friis', xcn_3='Jens', xcn_6='Dr.')

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.extra_segments = [ais, ail, aip]

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
    """ Based on live/dk/dk-columna-flow.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_FLOW')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='DOKUMENTDELING')
        msh.receiving_facility = HD(hd_1='NSP')
        msh.date_time_of_message = '20260405140000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02')
        msh.message_control_id = 'CF00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260405140000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1209739768', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Larsen', xpn_2='Kirsten', xpn_3='Karla', xpn_5='')
        pid.date_time_of_birth = '19730912'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Danmarksgade 113', xad_3='Hillerød', xad_5='3400', xad_6='DK')
        pid.pid_13 = '^^PH^+4553214566'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='KIR', pl_3='DAG01')
        pv1.attending_doctor = XCN(xcn_1='55005', xcn_2='Svendsen', xcn_3='Jonas', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='KIR')
        pv1.financial_class = FC(fc_1='AAUH202604050001')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='OP', cwe_2='Operationsnotat')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20260405140000'
        txa.primary_activity_provider_code_name = XCN(xcn_1='55005', xcn_2='Svendsen', xcn_3='Jonas', xcn_6='Dr.')
        txa.transcription_date_time = '20260405140000'
        txa.unique_document_number = EI(ei_1='DOC20260405001')
        txa.document_confidentiality_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='NOTE', cwe_2='Operationsnotat', cwe_3='LN')
        obx.obx_5 = (
            'Laparoskopisk kolecystektomi. Ukompliceret procedure. Galdeblæren fjernet intakt. Normal anatomi af ductus cysticus og a. cystica. Operation'
            'stid: 45 min. Blodtab: minimalt. Patienten udskrevet til hjemmet i velbefindende.'
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
    """ Based on live/dk/dk-columna-flow.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_FLOW')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='DOKUMENTDELING')
        msh.receiving_facility = HD(hd_1='NSP')
        msh.date_time_of_message = '20260405143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CF00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1209739768', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Larsen', xpn_2='Kirsten', xpn_3='Karla', xpn_5='')
        pid.date_time_of_birth = '19730912'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Danmarksgade 113', xad_3='Hillerød', xad_5='3400', xad_6='DK')
        pid.pid_13 = '^^PH^+4553214566'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='KIR', pl_3='DAG01')
        pv1.attending_doctor = XCN(xcn_1='55005', xcn_2='Svendsen', xcn_3='Jonas', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='KIR')
        pv1.financial_class = FC(fc_1='AAUH202604050001')

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
        orc.placer_order_number = EI(ei_1='DOC20260405001', ei_2='COLUMNA_FLOW')
        orc.parent_order = EIP(eip_1='20260405143000')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='DOC20260405001', ei_2='COLUMNA_FLOW')
        obr.universal_service_identifier = CWE(cwe_1='OPNOTE', cwe_2='Operationsnotat - komplet', cwe_3='LN')
        obr.observation_date_time = '20260405140000'
        obr.obr_15 = '55005^Svendsen^Jonas^^^Dr.'
        obr.filler_field_2 = '20260405143000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Operationsnotat', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjUKJcOkw7zDtsOfCjEgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJd'
            'Ci9Db3VudCAxCi9NZWRpYUJveCBbMCAwIDU5NSA4NDJdCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdl'
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
    """ Based on live/dk/dk-columna-flow.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_FLOW')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='LANDSPATIENTREGISTERET')
        msh.receiving_facility = HD(hd_1='SST')
        msh.date_time_of_message = '20260405160000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'CF00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260405160000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1209739768', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Larsen', xpn_2='Kirsten', xpn_3='Karla', xpn_5='')
        pid.date_time_of_birth = '19730912'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Danmarksgade 113', xad_3='Hillerød', xad_5='3400', xad_6='DK')
        pid.pid_13 = '^^PH^+4553214566'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='KIR', pl_3='DAG01')
        pv1.attending_doctor = XCN(xcn_1='55005', xcn_2='Svendsen', xcn_3='Jonas', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='KIR')
        pv1.financial_class = FC(fc_1='AAUH202604050001')
        pv1.admit_date_time = '20260405160000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Laparoskopisk kolecystektomi, ukompliceret')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/dk/dk-columna-flow.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_FLOW')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='COLUMNA_CIS')
        msh.receiving_facility = HD(hd_1='AALBORG_UH')
        msh.date_time_of_message = '20260406193000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'CF00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260406193000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0711009967', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Madsen', xpn_2='Oliver', xpn_3='Svend', xpn_5='')
        pid.date_time_of_birth = '20001107'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Frederikssundsvej 226', xad_3='Roskilde', xad_5='4000', xad_6='DK')
        pid.pid_13 = '^^CP^+4529314227'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='AKM', pl_3='SKADE', pl_4='S01')
        pv1.attending_doctor = XCN(xcn_1='77007', xcn_2='Poulsen', xcn_3='Magnus', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='AKM')
        pv1.admit_source = CWE(cwe_1='5')
        pv1.admitting_doctor = XCN(xcn_1='77007', xcn_2='Poulsen', xcn_3='Magnus', xcn_6='Dr.')
        pv1.visit_number = CX(cx_1='AAUH202604060001')
        pv1.prior_temporary_location = PL(pl_1='20260406193000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Forstuvning af ankel')

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
    """ Based on live/dk/dk-columna-flow.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_FLOW')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='CARESTREAM_RIS')
        msh.receiving_facility = HD(hd_1='AAUH_RAD')
        msh.date_time_of_message = '20260406194000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'CF00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0711009967', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Madsen', xpn_2='Oliver', xpn_3='Svend', xpn_5='')
        pid.date_time_of_birth = '20001107'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Frederikssundsvej 226', xad_3='Roskilde', xad_5='4000', xad_6='DK')
        pid.pid_13 = '^^CP^+4529314227'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='AKM', pl_3='SKADE', pl_4='S01')
        pv1.attending_doctor = XCN(xcn_1='77007', xcn_2='Poulsen', xcn_3='Magnus', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='AKM')
        pv1.financial_class = FC(fc_1='AAUH202604060001')

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
        orc.placer_order_number = EI(ei_1='ORD20260406001', ei_2='COLUMNA_FLOW')
        orc.parent_order = EIP(eip_1='20260406194000')
        orc.orc_11 = '77007^Poulsen^Magnus^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260406001', ei_2='COLUMNA_FLOW')
        obr.universal_service_identifier = CWE(cwe_1='XANKLE', cwe_2='Røntgen af ankel', cwe_3='LOCAL')
        obr.observation_date_time = '20260406194000'
        obr.relevant_clinical_information = CWE(cwe_1='Inversions-traume, hævelse lateralt')
        obr.obr_14 = '77007^Poulsen^Magnus^^^Dr.'

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
    """ Based on live/dk/dk-columna-flow.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARESTREAM_RIS')
        msh.sending_facility = HD(hd_1='AAUH_RAD')
        msh.receiving_application = HD(hd_1='COLUMNA_FLOW')
        msh.receiving_facility = HD(hd_1='AALBORG_UH')
        msh.date_time_of_message = '20260406204500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CF00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0711009967', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Madsen', xpn_2='Oliver', xpn_3='Svend', xpn_5='')
        pid.date_time_of_birth = '20001107'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Frederikssundsvej 226', xad_3='Roskilde', xad_5='4000', xad_6='DK')
        pid.pid_13 = '^^CP^+4529314227'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='AKM', pl_3='SKADE', pl_4='S01')
        pv1.attending_doctor = XCN(xcn_1='77007', xcn_2='Poulsen', xcn_3='Magnus', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='AKM')
        pv1.financial_class = FC(fc_1='AAUH202604060001')

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
        orc.placer_order_number = EI(ei_1='ORD20260406001', ei_2='COLUMNA_FLOW')
        orc.parent_order = EIP(eip_1='20260406204500')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260406001', ei_2='COLUMNA_FLOW')
        obr.universal_service_identifier = CWE(cwe_1='XANKLE', cwe_2='Røntgen af ankel', cwe_3='LOCAL')
        obr.observation_date_time = '20260406194000'
        obr.obr_15 = '77007^Poulsen^Magnus^^^Dr.'
        obr.placer_field_1 = '55001^Nielsen^Niels^^^Dr.'
        obr.filler_field_1 = '20260406204500'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='RADRPT', cwe_2='Radiologibeskrivelse', cwe_3='LN')
        obx.obx_5 = (
            'Røntgen af ve. ankel AP, lateral og mortise: Ingen fraktur. Let bløddelssvulst lateralt forenelig med ligamentskade. Fibula og tibia intakte'
            '. Ankelmortisen kongruent. Konkl: Ingen ossøse læsioner.'
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
    """ Based on live/dk/dk-columna-flow.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COLUMNA_FLOW')
        msh.sending_facility = HD(hd_1='AALBORG_UH')
        msh.receiving_application = HD(hd_1='LANDSPATIENTREGISTERET')
        msh.receiving_facility = HD(hd_1='SST')
        msh.date_time_of_message = '20260406213000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'CF00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260406213000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0711009967', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Madsen', xpn_2='Oliver', xpn_3='Svend', xpn_5='')
        pid.date_time_of_birth = '20001107'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Frederikssundsvej 226', xad_3='Roskilde', xad_5='4000', xad_6='DK')
        pid.pid_13 = '^^CP^+4529314227'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='AAUH', pl_2='AKM', pl_3='SKADE', pl_4='S01')
        pv1.attending_doctor = XCN(xcn_1='77007', xcn_2='Poulsen', xcn_3='Magnus', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='AKM')
        pv1.admit_source = CWE(cwe_1='5')
        pv1.admitting_doctor = XCN(xcn_1='77007', xcn_2='Poulsen', xcn_3='Magnus', xcn_6='Dr.')
        pv1.visit_number = CX(cx_1='AAUH202604060001')
        pv1.prior_temporary_location = PL(pl_1='20260406213000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Forstuvning af ankel - behandlet, bandage og krykkestokke')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
