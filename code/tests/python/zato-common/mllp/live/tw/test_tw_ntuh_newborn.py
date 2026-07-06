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
from zato.hl7v2.v2_9.datatypes import CWE, CX, DLD, DR, EI, EIP, HD, MSG, PL, PT, VID, XAD, XPN
from zato.hl7v2.v2_9.groups import AdtA01NextOfKin, AdtA03NextOfKin, OmlO21NextOfKin, OmlO21Order, OmlO21Patient, OmlO21PatientVisit, OruR01CommonOrder, \
    OruR01NextOfKin, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A03, OML_O21, ORU_R01
from zato.hl7v2.v2_9.segments import EVN, MSH, NK1, OBR, OBX, ORC, PID, PV1, SAC, SPM

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('tw', 'tw-ntuh-newborn.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/tw/tw-ntuh-newborn.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-NTUH')
        msh.sending_facility = HD(hd_1='NTUH_HOSP')
        msh.receiving_application = HD(hd_1='NBS-NTUH')
        msh.receiving_facility = HD(hd_1='NTUH_NBS')
        msh.date_time_of_message = '20260301080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20260301080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260301080000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT1000100', cx_4='NTUH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='潘', xpn_2='小傑')
        pid.date_time_of_birth = '20260301'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新北市永和區永和路二段55號', xad_3='新北市', xad_4='23449', xad_5='TW')
        pid.pid_13 = '02-29251234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='潘李佳穎', xpn_2='PAT1000101')
        nk1.relationship = CWE(cwe_1='MTH')
        nk1.address = XAD(xad_1='新北市永和區永和路二段55號', xad_3='新北市', xad_4='23449', xad_5='TW')
        nk1.nk1_5 = '02-29251234'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NICU', pl_2='201', pl_3='01')
        pv1.pv1_7 = 'D1000100^方麗雲^^^^^NTUH_HOSP'
        pv1.visit_number = CX(cx_1='V1000100001')
        pv1.diet_type = CWE(cwe_1='NTUH_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260301080000')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1

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
    """ Based on live/tw/tw-ntuh-newborn.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NBS-NTUH')
        msh.sending_facility = HD(hd_1='NTUH_NBS')
        msh.receiving_application = HD(hd_1='LIS-NTUH')
        msh.receiving_facility = HD(hd_1='NTUH_LAB')
        msh.date_time_of_message = '20260303100000'
        msh.message_type = MSG(msg_1='OML', msg_2='O21', msg_3='OML_O21')
        msh.message_control_id = 'MSG20260303100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT1000100', cx_4='NTUH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='潘', xpn_2='小傑')
        pid.date_time_of_birth = '20260301'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新北市永和區永和路二段55號', xad_3='新北市', xad_4='23449', xad_5='TW')
        pid.pid_13 = '02-29251234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='潘李佳穎', xpn_2='PAT1000101')
        nk1.relationship = CWE(cwe_1='MTH')
        nk1.address = XAD(xad_1='新北市永和區永和路二段55號', xad_3='新北市', xad_4='23449', xad_5='TW')
        nk1.nk1_5 = '02-29251234'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = OmlO21NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NICU', pl_2='201', pl_3='01')
        pv1.pv1_7 = 'D1000100^方麗雲^^^^^NTUH_HOSP'
        pv1.visit_number = CX(cx_1='V1000100001')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OmlO21PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OmlO21Patient()
        patient.pid = pid
        patient.next_of_kin = next_of_kin
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='NBS1000100001')
        orc.orc_7 = '1^^^20260303100000^^R'
        orc.date_time_of_order_event = '20260303100000'
        orc.orc_11 = 'D1000100^方麗雲'
        orc.order_control_code_reason = CWE(cwe_1='LAB', cwe_2='新生兒篩檢實驗室')

        # .. build the ORDER group ..
        order = OmlO21Order()
        order.orc = orc

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_identifier = EIP(eip_1='SPM1000100001')
        spm.specimen_type = CWE(cwe_1='BLD', cwe_2='全血', cwe_3='HL70487')
        spm.specimen_collection_date_time = DR(dr_1='20260303093000')
        spm.specimen_received_date_time = '20260303100000'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='NBS1000100001')
        obr.universal_service_identifier = CWE(cwe_1='54089-8', cwe_2='新生兒篩檢組合', cwe_3='LN')
        obr.observation_date_time = '20260303093000'
        obr.obr_15 = 'D1000100^方麗雲'

        # .. build SAC ..
        sac = SAC()
        sac.external_accession_identifier = EI(ei_1='1')
        sac.container_identifier = EI(ei_1='SPM1000100001')
        sac.registration_date_time = 'DBS^乾血片^LOCAL'

        # .. assemble the full message ..
        msg = OML_O21()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [spm, obr, sac]

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
    """ Based on live/tw/tw-ntuh-newborn.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-NTUH')
        msh.sending_facility = HD(hd_1='NTUH_HOSP')
        msh.receiving_application = HD(hd_1='NBS-NTUH')
        msh.receiving_facility = HD(hd_1='NTUH_NBS')
        msh.date_time_of_message = '20260305080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20260305080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260305080000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT1000200', cx_4='NTUH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='魏', xpn_2='小慧')
        pid.date_time_of_birth = '20260305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        pid.pid_13 = '02-29021234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='魏陳雅惠', xpn_2='PAT1000201')
        nk1.relationship = CWE(cwe_1='MTH')
        nk1.address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        nk1.nk1_5 = '02-29021234'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NUR', pl_2='101', pl_3='03')
        pv1.pv1_7 = 'D1000200^郝建鈞^^^^^NTUH_HOSP'
        pv1.visit_number = CX(cx_1='V1000200001')
        pv1.diet_type = CWE(cwe_1='NTUH_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260305080000')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
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
    """ Based on live/tw/tw-ntuh-newborn.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NBS-NTUH')
        msh.sending_facility = HD(hd_1='NTUH_NBS')
        msh.receiving_application = HD(hd_1='LIS-NTUH')
        msh.receiving_facility = HD(hd_1='NTUH_LAB')
        msh.date_time_of_message = '20260307100000'
        msh.message_type = MSG(msg_1='OML', msg_2='O21', msg_3='OML_O21')
        msh.message_control_id = 'MSG20260307100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT1000200', cx_4='NTUH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='魏', xpn_2='小慧')
        pid.date_time_of_birth = '20260305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        pid.pid_13 = '02-29021234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='魏陳雅惠', xpn_2='PAT1000201')
        nk1.relationship = CWE(cwe_1='MTH')
        nk1.address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        nk1.nk1_5 = '02-29021234'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = OmlO21NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NUR', pl_2='101', pl_3='03')
        pv1.pv1_7 = 'D1000200^郝建鈞^^^^^NTUH_HOSP'
        pv1.visit_number = CX(cx_1='V1000200001')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OmlO21PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OmlO21Patient()
        patient.pid = pid
        patient.next_of_kin = next_of_kin
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='NBS1000200001')
        orc.orc_7 = '1^^^20260307100000^^R'
        orc.date_time_of_order_event = '20260307100000'
        orc.orc_11 = 'D1000200^郝建鈞'
        orc.order_control_code_reason = CWE(cwe_1='LAB', cwe_2='新生兒篩檢實驗室')

        # .. build the ORDER group ..
        order = OmlO21Order()
        order.orc = orc

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_identifier = EIP(eip_1='SPM1000200001')
        spm.specimen_type = CWE(cwe_1='BLD', cwe_2='全血', cwe_3='HL70487')
        spm.specimen_collection_date_time = DR(dr_1='20260307093000')
        spm.specimen_received_date_time = '20260307100000'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='NBS1000200001')
        obr.universal_service_identifier = CWE(cwe_1='54089-8', cwe_2='新生兒篩檢組合', cwe_3='LN')
        obr.observation_date_time = '20260307093000'
        obr.obr_15 = 'D1000200^郝建鈞'

        # .. build SAC ..
        sac = SAC()
        sac.external_accession_identifier = EI(ei_1='1')
        sac.container_identifier = EI(ei_1='SPM1000200001')
        sac.registration_date_time = 'DBS^乾血片^LOCAL'

        # .. assemble the full message ..
        msg = OML_O21()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [spm, obr, sac]

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
    """ Based on live/tw/tw-ntuh-newborn.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NBS-NTUH')
        msh.sending_facility = HD(hd_1='NTUH_NBS')
        msh.receiving_application = HD(hd_1='HIS-NTUH')
        msh.receiving_facility = HD(hd_1='NTUH_HOSP')
        msh.date_time_of_message = '20260306143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260306143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT1000100', cx_4='NTUH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='潘', xpn_2='小傑')
        pid.date_time_of_birth = '20260301'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新北市永和區永和路二段55號', xad_3='新北市', xad_4='23449', xad_5='TW')
        pid.pid_13 = '02-29251234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='潘李佳穎', xpn_2='PAT1000101')
        nk1.relationship = CWE(cwe_1='MTH')
        nk1.address = XAD(xad_1='新北市永和區永和路二段55號', xad_3='新北市', xad_4='23449', xad_5='TW')
        nk1.nk1_5 = '02-29251234'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = OruR01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NICU', pl_2='201', pl_3='01')
        pv1.pv1_7 = 'D1000100^方麗雲^^^^^NTUH_HOSP'
        pv1.visit_number = CX(cx_1='V1000100001')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.next_of_kin = next_of_kin
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='NBS1000100001')
        orc.orc_10 = 'D1000100^方麗雲'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='NBS1000100001')
        obr.universal_service_identifier = CWE(cwe_1='54089-8', cwe_2='新生兒篩檢組合', cwe_3='LN')
        obr.observation_date_time = '20260303093000'
        obr.obr_16 = 'D1000100^方麗雲'
        obr.results_rpt_status_chng_date_time = '20260306140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='29575-8', cwe_2='苯丙氨酸', cwe_3='LN')
        obx.obx_5 = '1.2'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '<4.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260306140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='54079-9', cwe_2='促甲狀腺激素(TSH)', cwe_3='LN')
        obx_2.obx_5 = '5.5'
        obx_2.units = CWE(cwe_1='mIU/L')
        obx_2.reference_range = '<15.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260306140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='38478-4', cwe_2='17-羥乙酮', cwe_3='LN')
        obx_3.obx_5 = '8.2'
        obx_3.units = CWE(cwe_1='ng/mL')
        obx_3.reference_range = '<30.0'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260306140000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='53336-4', cwe_2='免疫反應性胰蛋白酶', cwe_3='LN')
        obx_4.obx_5 = '32'
        obx_4.units = CWE(cwe_1='ng/mL')
        obx_4.reference_range = '<60.0'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260306140000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='42906-8', cwe_2='半乳糖', cwe_3='LN')
        obx_5.obx_5 = '3.5'
        obx_5.units = CWE(cwe_1='mg/dL')
        obx_5.reference_range = '<10.0'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260306140000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='47700-0', cwe_2='蛋胺酸', cwe_3='LN')
        obx_6.obx_5 = '0.8'
        obx_6.units = CWE(cwe_1='mg/dL')
        obx_6.reference_range = '<2.0'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260306140000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='53235-8', cwe_2='G6PD酶活性', cwe_3='LN')
        obx_7.obx_5 = '8.5'
        obx_7.units = CWE(cwe_1='U/gHb')
        obx_7.reference_range = '>2.5'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20260306140000'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'FT'
        obx_8.observation_identifier = CWE(cwe_1='54089-8', cwe_2='新生兒篩檢結論', cwe_3='LN')
        obx_8.obx_5 = '所有篩檢項目均在正常範圍內，無需進一步追蹤。'
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

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
        order_observation.observation_8 = observation_8

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
    """ Based on live/tw/tw-ntuh-newborn.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NBS-NTUH')
        msh.sending_facility = HD(hd_1='NTUH_NBS')
        msh.receiving_application = HD(hd_1='HIS-NTUH')
        msh.receiving_facility = HD(hd_1='NTUH_HOSP')
        msh.date_time_of_message = '20260310143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260310143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT1000200', cx_4='NTUH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='魏', xpn_2='小慧')
        pid.date_time_of_birth = '20260305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        pid.pid_13 = '02-29021234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='魏陳雅惠', xpn_2='PAT1000201')
        nk1.relationship = CWE(cwe_1='MTH')
        nk1.address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        nk1.nk1_5 = '02-29021234'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = OruR01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NUR', pl_2='101', pl_3='03')
        pv1.pv1_7 = 'D1000200^郝建鈞^^^^^NTUH_HOSP'
        pv1.visit_number = CX(cx_1='V1000200001')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.next_of_kin = next_of_kin
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='NBS1000200001')
        orc.orc_10 = 'D1000200^郝建鈞'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='NBS1000200001')
        obr.universal_service_identifier = CWE(cwe_1='54089-8', cwe_2='新生兒篩檢組合', cwe_3='LN')
        obr.observation_date_time = '20260307093000'
        obr.obr_16 = 'D1000200^郝建鈞'
        obr.results_rpt_status_chng_date_time = '20260310140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='29575-8', cwe_2='苯丙氨酸', cwe_3='LN')
        obx.obx_5 = '1.5'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '<4.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260310140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='54079-9', cwe_2='促甲狀腺激素(TSH)', cwe_3='LN')
        obx_2.obx_5 = '28.5'
        obx_2.units = CWE(cwe_1='mIU/L')
        obx_2.reference_range = '<15.0'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260310140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='38478-4', cwe_2='17-羥乙酮', cwe_3='LN')
        obx_3.obx_5 = '12.0'
        obx_3.units = CWE(cwe_1='ng/mL')
        obx_3.reference_range = '<30.0'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260310140000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='53336-4', cwe_2='免疫反應性胰蛋白酶', cwe_3='LN')
        obx_4.obx_5 = '38'
        obx_4.units = CWE(cwe_1='ng/mL')
        obx_4.reference_range = '<60.0'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260310140000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='42906-8', cwe_2='半乳糖', cwe_3='LN')
        obx_5.obx_5 = '4.2'
        obx_5.units = CWE(cwe_1='mg/dL')
        obx_5.reference_range = '<10.0'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260310140000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='47700-0', cwe_2='蛋胺酸', cwe_3='LN')
        obx_6.obx_5 = '0.6'
        obx_6.units = CWE(cwe_1='mg/dL')
        obx_6.reference_range = '<2.0'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260310140000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='53235-8', cwe_2='G6PD酶活性', cwe_3='LN')
        obx_7.obx_5 = '7.8'
        obx_7.units = CWE(cwe_1='U/gHb')
        obx_7.reference_range = '>2.5'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20260310140000'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'FT'
        obx_8.observation_identifier = CWE(cwe_1='54089-8', cwe_2='新生兒篩檢結論', cwe_3='LN')
        obx_8.obx_5 = 'TSH值異常升高(28.5 mIU/L)，疑似先天性甲狀腺功能低下症。需立即通知家屬並安排確認檢查。'
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

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
        order_observation.observation_8 = observation_8

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
    """ Based on live/tw/tw-ntuh-newborn.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NBS-NTUH')
        msh.sending_facility = HD(hd_1='NTUH_NBS')
        msh.receiving_application = HD(hd_1='HIS-NTUH')
        msh.receiving_facility = HD(hd_1='NTUH_HOSP')
        msh.date_time_of_message = '20260311090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260311090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT1000200', cx_4='NTUH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='魏', xpn_2='小慧')
        pid.date_time_of_birth = '20260305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        pid.pid_13 = '02-29021234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='魏陳雅惠', xpn_2='PAT1000201')
        nk1.relationship = CWE(cwe_1='MTH')
        nk1.address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        nk1.nk1_5 = '02-29021234'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = OruR01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PED', pl_2='101', pl_3='01')
        pv1.pv1_7 = 'D1000200^郝建鈞^^^^^NTUH_HOSP'
        pv1.visit_number = CX(cx_1='V1000200002')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.next_of_kin = next_of_kin
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='NBS1000200002')
        orc.orc_10 = 'D1000200^郝建鈞'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='NBS1000200002')
        obr.universal_service_identifier = CWE(cwe_1='54089-8', cwe_2='新生兒篩檢召回通知', cwe_3='LN')
        obr.observation_date_time = '20260311083000'
        obr.obr_16 = 'D1000200^郝建鈞'
        obr.results_rpt_status_chng_date_time = '20260311090000'
        obr.result_status = 'P'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='54089-8', cwe_2='召回原因', cwe_3='LN')
        obx.obx_5 = '新生兒篩檢TSH值異常(28.5 mIU/L)，疑似先天性甲狀腺功能低下症。請於接獲通知後3日內攜帶寶寶至小兒內分泌科進行確認檢查。'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='54089-8', cwe_2='召回通知書PDF', cwe_3='LN')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQovQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAzMDAgPj4Kc3RyZWFtCkJUCi9GMSAxOCBUZgoxMDAgNzAwIFRkCijoh7rlpKfphqvpmaIg5paw'
            '55Sf5YWS56+p5qqi5Lit5b+DIOWPrOWbnumAmuefpeabuCkgVGoKLzEgMTQgVGYKMTAwIDY1MCBUZAoo6Kaq5oSb55qE5byg576O546y5aWz5aOrOikgVGoKMTAwIDYyMCBUZAoo5oKo'
            '55qE5a+25a+2IOW8teWwj+e+jiAoUEFUMTAwMDIwMCkg5paw55Sf5YWS56+p5qqi57WQ5p6c6aGv56S6VFNIKSBUagoxMDAgNTkwIFRkCijlgLznlbDluLjljYcgKDI4LjUgbUlVL0wp'
            'LCDnlpHkvLzlhYjlpKnmgKfnlLLni4Doga/lip/og73kvY7kuIvnl4fjgIIpIFRqCjEwMCA1NTAgVGQKKOiri+aWvDPlpKnlhafmkpzluLblr7blr7boh7PlsI/lhZLlhafliIbms4zn'
            'p5Hplos6IDIwMjYvMDMvMTQg5LiK5Y2IOSzCoOmgkOe0hCkgVGoKMTAwIDUxMCBUZAoo6IGv57Wh55S16Kmx5rC4OiAwMi0yMzEyMzQ1NiDovYkxMjM0NSkgVGoKRVQKZW5kc3RyZWFt'
            'CmVuZG9iago1IDAgb2JqCjw8IC9UeXBlIC9Gb250IC9TdWJ0eXBlIC9UeXBlMSAvQmFzZUZvbnQgL0hlbHZldGljYSA+PgplbmRvYmoKeHJlZgowIDYKMDAwMDAwMDAwMCA2NTUzNSBm'
            'IAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDExNSAwMDAwMCBuIAowMDAwMDAwMzA2IDAwMDAwIG4gCjAwMDAwMDA2NTggMDAwMDAgbiAKdHJh'
            'aWxlcgo8PCAvU2l6ZSA2IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgo3NDUKJSVFTwZ=='
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
    """ Based on live/tw/tw-ntuh-newborn.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NBS-NTUH')
        msh.sending_facility = HD(hd_1='NTUH_NBS')
        msh.receiving_application = HD(hd_1='LIS-NTUH')
        msh.receiving_facility = HD(hd_1='NTUH_LAB')
        msh.date_time_of_message = '20260314100000'
        msh.message_type = MSG(msg_1='OML', msg_2='O21', msg_3='OML_O21')
        msh.message_control_id = 'MSG20260314100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT1000200', cx_4='NTUH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='魏', xpn_2='小慧')
        pid.date_time_of_birth = '20260305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        pid.pid_13 = '02-29021234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='魏陳雅惠', xpn_2='PAT1000201')
        nk1.relationship = CWE(cwe_1='MTH')
        nk1.address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        nk1.nk1_5 = '02-29021234'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = OmlO21NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PED', pl_2='101', pl_3='01')
        pv1.pv1_7 = 'D1000200^郝建鈞^^^^^NTUH_HOSP'
        pv1.visit_number = CX(cx_1='V1000200002')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OmlO21PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OmlO21Patient()
        patient.pid = pid
        patient.next_of_kin = next_of_kin
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='NBS1000200003')
        orc.orc_7 = '1^^^20260314100000^^R'
        orc.date_time_of_order_event = '20260314100000'
        orc.orc_11 = 'D1000200^郝建鈞'
        orc.order_control_code_reason = CWE(cwe_1='LAB', cwe_2='新生兒篩檢實驗室')

        # .. build the ORDER group ..
        order = OmlO21Order()
        order.orc = orc

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_identifier = EIP(eip_1='SPM1000200002')
        spm.specimen_type = CWE(cwe_1='BLDV', cwe_2='靜脈血', cwe_3='HL70487')
        spm.specimen_collection_date_time = DR(dr_1='20260314093000')
        spm.specimen_received_date_time = '20260314100000'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='NBS1000200003')
        obr.universal_service_identifier = CWE(cwe_1='24348-5', cwe_2='甲狀腺功能確認檢查', cwe_3='LN')
        obr.observation_date_time = '20260314093000'
        obr.obr_15 = 'D1000200^郝建鈞'

        # .. assemble the full message ..
        msg = OML_O21()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [spm, obr]

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
    """ Based on live/tw/tw-ntuh-newborn.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NBS-NTUH')
        msh.sending_facility = HD(hd_1='NTUH_NBS')
        msh.receiving_application = HD(hd_1='HIS-NTUH')
        msh.receiving_facility = HD(hd_1='NTUH_HOSP')
        msh.date_time_of_message = '20260315143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260315143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT1000200', cx_4='NTUH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='魏', xpn_2='小慧')
        pid.date_time_of_birth = '20260305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        pid.pid_13 = '02-29021234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='魏陳雅惠', xpn_2='PAT1000201')
        nk1.relationship = CWE(cwe_1='MTH')
        nk1.address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        nk1.nk1_5 = '02-29021234'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = OruR01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PED', pl_2='101', pl_3='01')
        pv1.pv1_7 = 'D1000200^郝建鈞^^^^^NTUH_HOSP'
        pv1.visit_number = CX(cx_1='V1000200002')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.next_of_kin = next_of_kin
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='NBS1000200003')
        orc.orc_10 = 'D1000200^郝建鈞'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='NBS1000200003')
        obr.universal_service_identifier = CWE(cwe_1='24348-5', cwe_2='甲狀腺功能確認檢查', cwe_3='LN')
        obr.observation_date_time = '20260314093000'
        obr.obr_16 = 'D1000200^郝建鈞'
        obr.results_rpt_status_chng_date_time = '20260315140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='促甲狀腺激素(TSH)', cwe_3='LN')
        obx.obx_5 = '35.2'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.7-5.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260315140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3026-2', cwe_2='游離甲狀腺素(FT4)', cwe_3='LN')
        obx_2.obx_5 = '0.5'
        obx_2.units = CWE(cwe_1='ng/dL')
        obx_2.reference_range = '0.8-2.0'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260315140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3053-6', cwe_2='游離三碘甲狀腺原氨酸(FT3)', cwe_3='LN')
        obx_3.obx_5 = '1.8'
        obx_3.units = CWE(cwe_1='pg/mL')
        obx_3.reference_range = '2.0-5.2'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260315140000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'FT'
        obx_4.observation_identifier = CWE(cwe_1='24348-5', cwe_2='確認檢查結論', cwe_3='LN')
        obx_4.obx_5 = '確認先天性甲狀腺功能低下症。TSH顯著升高，FT4及FT3偏低。建議立即開始Levothyroxine治療並安排小兒內分泌科定期追蹤。'
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
    """ Based on live/tw/tw-ntuh-newborn.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NBS-NTUH')
        msh.sending_facility = HD(hd_1='NTUH_NBS')
        msh.receiving_application = HD(hd_1='HIS-NTUH')
        msh.receiving_facility = HD(hd_1='NTUH_HOSP')
        msh.date_time_of_message = '20260307090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260307090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT1000100', cx_4='NTUH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='潘', xpn_2='小傑')
        pid.date_time_of_birth = '20260301'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新北市永和區永和路二段55號', xad_3='新北市', xad_4='23449', xad_5='TW')
        pid.pid_13 = '02-29251234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='潘李佳穎', xpn_2='PAT1000101')
        nk1.relationship = CWE(cwe_1='MTH')
        nk1.address = XAD(xad_1='新北市永和區永和路二段55號', xad_3='新北市', xad_4='23449', xad_5='TW')
        nk1.nk1_5 = '02-29251234'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = OruR01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NICU', pl_2='201', pl_3='01')
        pv1.pv1_7 = 'D1000100^方麗雲^^^^^NTUH_HOSP'
        pv1.visit_number = CX(cx_1='V1000100001')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.next_of_kin = next_of_kin
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='NBS1000100001')
        orc.orc_10 = 'D1000100^方麗雲'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='NBS1000100001')
        obr.universal_service_identifier = CWE(cwe_1='54089-8', cwe_2='新生兒篩檢報告', cwe_3='LN')
        obr.observation_date_time = '20260303093000'
        obr.obr_16 = 'D1000100^方麗雲'
        obr.results_rpt_status_chng_date_time = '20260307083000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='54089-8', cwe_2='篩檢結果摘要', cwe_3='LN')
        obx.obx_5 = '新生兒代謝篩檢七項全部正常。詳細結果請見附件報告。'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='54089-8', cwe_2='新生兒篩檢報告PDF', cwe_3='LN')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQovQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0MDAgPj4Kc3RyZWFtCkJUCi9GMSAxOCBUZgoxMDAgNzAwIFRkCijoh7rlpKfphqvpmaIg5paw'
            '55Sf5YWS56+p5qqi5Lit5b+DIOe7k+aenOWgseWRiikgVGoKL0YxIDE0IFRmCjEwMCA2NjAgVGQKKOWvtuWvtjog5p6X5bCP5piOIChQQVQxMDAwMTAwKSkgVGoKMTAwIDYzMCBUZAoo'
            '5Ye655Sf5pel5pyfOiAyMDI2LzAzLzAxIOaAp+WIpTog55S3KSBUagoxMDAgNjAwIFRkCijmqJzpq5TmjqHpm4bml6XmnJ86IDIwMjYvMDMvMDMpIFRqCjEwMCA1NjAgVGQKKOeviuaq'
            'ouWIhuexuzogUGhlPTEuMiAo5q2j5bi4KSwgVFNIPTUuNSAo5q2j5bi4KSkgVGoKMTAwIDUzMCBUZAooMTct6Iqz5LmZ6YaePTguMiAo5q2j5bi4KSwgSVJUPTMyICjmraPluLgpKSBU'
            'agoxMDAgNTAwIFRkCijoirHkubPns5Y9My41ICjmraPluLgpLCBNZXQ9MC44ICjmraPluLgpKSBUagoxMDAgNDcwIFRkCihHNlBEPTguNSAo5q2j5bi4KSkgVGoKMTAwIDQzMCBUZAoo'
            '57eQ6KuWOiDmiYDmnInnr6nmqqPpoIXnm67lnYflnKjmraPluLjnr4TlnI3lhacpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8PCAvVHlwZSAvRm9udCAvU3VidHlwZSAv'
            'VHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU4IDAwMDAwIG4g'
            'CjAwMDAwMDAxMTUgMDAwMDAgbiAKMDAwMDAwMDMwNiAwMDAwMCBuIAowMDAwMDAwNzU4IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYK'
            'ODQ1CiUlRU9GCg=='
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
    """ Based on live/tw/tw-ntuh-newborn.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-NTUH')
        msh.sending_facility = HD(hd_1='NTUH_HOSP')
        msh.receiving_application = HD(hd_1='NBS-NTUH')
        msh.receiving_facility = HD(hd_1='NTUH_NBS')
        msh.date_time_of_message = '20260308100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG20260308100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260308100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT1000100', cx_4='NTUH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='潘', xpn_2='小傑')
        pid.date_time_of_birth = '20260301'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新北市永和區永和路二段55號', xad_3='新北市', xad_4='23449', xad_5='TW')
        pid.pid_13 = '02-29251234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='潘李佳穎', xpn_2='PAT1000101')
        nk1.relationship = CWE(cwe_1='MTH')
        nk1.address = XAD(xad_1='新北市永和區永和路二段55號', xad_3='新北市', xad_4='23449', xad_5='TW')
        nk1.nk1_5 = '02-29251234'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA03NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NICU', pl_2='201', pl_3='01')
        pv1.pv1_7 = 'D1000100^方麗雲^^^^^NTUH_HOSP'
        pv1.visit_number = CX(cx_1='V1000100001')
        pv1.discharged_to_location = DLD(dld_1='01')
        pv1.diet_type = CWE(cwe_1='NTUH_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260301080000')
        pv1.current_patient_balance = '20260308100000'

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1

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
    """ Based on live/tw/tw-ntuh-newborn.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-NTUH')
        msh.sending_facility = HD(hd_1='NTUH_HOSP')
        msh.receiving_application = HD(hd_1='NBS-NTUH')
        msh.receiving_facility = HD(hd_1='NTUH_NBS')
        msh.date_time_of_message = '20260310100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG20260310100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260310100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT1000200', cx_4='NTUH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='魏', xpn_2='小慧')
        pid.date_time_of_birth = '20260305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        pid.pid_13 = '02-29021234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='魏陳雅惠', xpn_2='PAT1000201')
        nk1.relationship = CWE(cwe_1='MTH')
        nk1.address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        nk1.nk1_5 = '02-29021234'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA03NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NUR', pl_2='101', pl_3='03')
        pv1.pv1_7 = 'D1000200^郝建鈞^^^^^NTUH_HOSP'
        pv1.visit_number = CX(cx_1='V1000200001')
        pv1.discharged_to_location = DLD(dld_1='01')
        pv1.diet_type = CWE(cwe_1='NTUH_HOSP')
        pv1.prior_temporary_location = PL(pl_1='20260305080000')
        pv1.current_patient_balance = '20260310100000'

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1

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
    """ Based on live/tw/tw-ntuh-newborn.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NBS-NTUH')
        msh.sending_facility = HD(hd_1='NTUH_NBS')
        msh.receiving_application = HD(hd_1='HIS-NTUH')
        msh.receiving_facility = HD(hd_1='NTUH_HOSP')
        msh.date_time_of_message = '20260316090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260316090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT1000200', cx_4='NTUH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='魏', xpn_2='小慧')
        pid.date_time_of_birth = '20260305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        pid.pid_13 = '02-29021234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='魏陳雅惠', xpn_2='PAT1000201')
        nk1.relationship = CWE(cwe_1='MTH')
        nk1.address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        nk1.nk1_5 = '02-29021234'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = OruR01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PED', pl_2='101', pl_3='01')
        pv1.pv1_7 = 'D1000200^郝建鈞^^^^^NTUH_HOSP'
        pv1.visit_number = CX(cx_1='V1000200002')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.next_of_kin = next_of_kin
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='NBS1000200003')
        orc.orc_10 = 'D1000200^郝建鈞'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='NBS1000200003')
        obr.universal_service_identifier = CWE(cwe_1='24348-5', cwe_2='甲狀腺功能確認報告', cwe_3='LN')
        obr.observation_date_time = '20260314093000'
        obr.obr_16 = 'D1000200^郝建鈞'
        obr.results_rpt_status_chng_date_time = '20260316083000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='24348-5', cwe_2='確認報告摘要', cwe_3='LN')
        obx.obx_5 = '確認先天性甲狀腺功能低下症。已開始Levothyroxine 10mcg/kg/day治療。'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='24348-5', cwe_2='確認報告PDF', cwe_3='LN')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQovQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9u'
            'dCA8PCAvRjEgNSAwIFIgPj4gPj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCAzNTAgPj4Kc3RyZWFtCkJUCi9GMSAxOCBUZgoxMDAgNzAwIFRkCijoh7rlpKfphqvpmaIg5paw'
            '55Sf5YWS56+p5qqi5Lit5b+DIOeiuuiqjeiIh+mao+mhr+WgseWRiikgVGoKL0YxIDE0IFRmCjEwMCA2NjAgVGQKKOWvtuWvtjog5byg5bCP576OIChQQVQxMDAwMjAwKSkgVGoKMTAw'
            'IDYzMCBUZAoo5Ye655Sf5pel5pyfOiAyMDI2LzAzLzA1IOaAp+WIpTog5aWzKSBUagoxMDAgNjAwIFRkCijliJ3nr6lUU0g6IDI4LjUgbUlVL0wgKOeVsOW4uCkpIFRqCjEwMCA1NzAg'
            'VGQKKOeiuuiqjVRTSDogMzUuMiBtSVUvTCAo6aGv6JGX5Y2H6auYKSkgVGoKMTAwIDU0MCBUZAoo56K66KqNRlQ0OiAwLjUgbmcvZEwgKOWBj+S9jikpIFRqCjEwMCA1MTAgVGQKKOio'
            'uuaWtzog56K66KqN5YWI5aSp5oCn55Sy54uA6IWf5Yqf6IO95L2O5LiL55eSKSBUagoxMDAgNDcwIFRkCijmsrvnmYI6IExldm90aHlyb3hpbmUgMTBtY2cva2cvZGF5IOW3suW8gOWn'
            'iysg5bCP5YWS5YWn5YiG5rOM56eR5a6a5pyf6L+96LmkKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwgL1R5cGUgL0ZvbnQgL1N1YnR5cGUgL1R5cGUxIC9CYXNlRm9u'
            'dCAvSGVsdmV0aWNhID4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAw'
            'MDAwIG4gCjAwMDAwMDAzMDYgMDAwMDAgbiAKMDAwMDAwMDcwOCAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDYgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4cmVmCjc5NQolJUVPRgo='
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
    """ Based on live/tw/tw-ntuh-newborn.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NBS-NTUH')
        msh.sending_facility = HD(hd_1='NTUH_NBS')
        msh.receiving_application = HD(hd_1='LIS-NTUH')
        msh.receiving_facility = HD(hd_1='NTUH_LAB')
        msh.date_time_of_message = '20260405100000'
        msh.message_type = MSG(msg_1='OML', msg_2='O21', msg_3='OML_O21')
        msh.message_control_id = 'MSG20260405100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT1000200', cx_4='NTUH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='魏', xpn_2='小慧')
        pid.date_time_of_birth = '20260305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        pid.pid_13 = '02-29021234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='魏陳雅惠', xpn_2='PAT1000201')
        nk1.relationship = CWE(cwe_1='MTH')
        nk1.address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        nk1.nk1_5 = '02-29021234'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = OmlO21NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PED', pl_2='101', pl_3='01')
        pv1.pv1_7 = 'D1000200^郝建鈞^^^^^NTUH_HOSP'
        pv1.visit_number = CX(cx_1='V1000200003')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OmlO21PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OmlO21Patient()
        patient.pid = pid
        patient.next_of_kin = next_of_kin
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='NBS1000200004')
        orc.orc_7 = '1^^^20260405100000^^R'
        orc.date_time_of_order_event = '20260405100000'
        orc.orc_11 = 'D1000200^郝建鈞'
        orc.order_control_code_reason = CWE(cwe_1='LAB', cwe_2='新生兒篩檢實驗室')

        # .. build the ORDER group ..
        order = OmlO21Order()
        order.orc = orc

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_identifier = EIP(eip_1='SPM1000200003')
        spm.specimen_type = CWE(cwe_1='BLDV', cwe_2='靜脈血', cwe_3='HL70487')
        spm.specimen_collection_date_time = DR(dr_1='20260405093000')
        spm.specimen_received_date_time = '20260405100000'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='NBS1000200004')
        obr.universal_service_identifier = CWE(cwe_1='24348-5', cwe_2='甲狀腺功能追蹤檢查(一個月)', cwe_3='LN')
        obr.observation_date_time = '20260405093000'
        obr.obr_15 = 'D1000200^郝建鈞'

        # .. assemble the full message ..
        msg = OML_O21()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [spm, obr]

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
    """ Based on live/tw/tw-ntuh-newborn.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NBS-NTUH')
        msh.sending_facility = HD(hd_1='NTUH_NBS')
        msh.receiving_application = HD(hd_1='HIS-NTUH')
        msh.receiving_facility = HD(hd_1='NTUH_HOSP')
        msh.date_time_of_message = '20260406143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260406143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT1000200', cx_4='NTUH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='魏', xpn_2='小慧')
        pid.date_time_of_birth = '20260305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        pid.pid_13 = '02-29021234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='魏陳雅惠', xpn_2='PAT1000201')
        nk1.relationship = CWE(cwe_1='MTH')
        nk1.address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        nk1.nk1_5 = '02-29021234'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = OruR01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PED', pl_2='101', pl_3='01')
        pv1.pv1_7 = 'D1000200^郝建鈞^^^^^NTUH_HOSP'
        pv1.visit_number = CX(cx_1='V1000200003')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.next_of_kin = next_of_kin
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='NBS1000200004')
        orc.orc_10 = 'D1000200^郝建鈞'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='NBS1000200004')
        obr.universal_service_identifier = CWE(cwe_1='24348-5', cwe_2='甲狀腺功能追蹤檢查(一個月)', cwe_3='LN')
        obr.observation_date_time = '20260405093000'
        obr.obr_16 = 'D1000200^郝建鈞'
        obr.results_rpt_status_chng_date_time = '20260406140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='促甲狀腺激素(TSH)', cwe_3='LN')
        obx.obx_5 = '12.5'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.7-5.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260406140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3026-2', cwe_2='游離甲狀腺素(FT4)', cwe_3='LN')
        obx_2.obx_5 = '1.1'
        obx_2.units = CWE(cwe_1='ng/dL')
        obx_2.reference_range = '0.8-2.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260406140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'FT'
        obx_3.observation_identifier = CWE(cwe_1='24348-5', cwe_2='追蹤結論', cwe_3='LN')
        obx_3.obx_5 = 'Levothyroxine治療一個月後TSH下降中(35.2->12.5 mIU/L)，FT4已回復正常範圍。建議繼續目前劑量並於一個月後再追蹤。'
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
    """ Based on live/tw/tw-ntuh-newborn.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NBS-NTUH')
        msh.sending_facility = HD(hd_1='NTUH_NBS')
        msh.receiving_application = HD(hd_1='HIS-NTUH')
        msh.receiving_facility = HD(hd_1='NTUH_HOSP')
        msh.date_time_of_message = '20260306160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260306160000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT1000100', cx_4='NTUH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='潘', xpn_2='小傑')
        pid.date_time_of_birth = '20260301'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新北市永和區永和路二段55號', xad_3='新北市', xad_4='23449', xad_5='TW')
        pid.pid_13 = '02-29251234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='潘李佳穎', xpn_2='PAT1000101')
        nk1.relationship = CWE(cwe_1='MTH')
        nk1.address = XAD(xad_1='新北市永和區永和路二段55號', xad_3='新北市', xad_4='23449', xad_5='TW')
        nk1.nk1_5 = '02-29251234'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = OruR01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NICU', pl_2='201', pl_3='01')
        pv1.pv1_7 = 'D1000100^方麗雲^^^^^NTUH_HOSP'
        pv1.visit_number = CX(cx_1='V1000100001')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.next_of_kin = next_of_kin
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='NBS1000100002')
        orc.orc_10 = 'D1000100^方麗雲'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='NBS1000100002')
        obr.universal_service_identifier = CWE(cwe_1='62292-8', cwe_2='串聯質譜儀新生兒篩檢', cwe_3='LN')
        obr.observation_date_time = '20260303093000'
        obr.obr_16 = 'D1000100^方麗雲'
        obr.results_rpt_status_chng_date_time = '20260306155000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='53261-4', cwe_2='丙氨酸(Ala)', cwe_3='LN')
        obx.obx_5 = '285'
        obx.units = CWE(cwe_1='umol/L')
        obx.reference_range = '100-450'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260306155000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='53160-8', cwe_2='白胺酸(Leu)', cwe_3='LN')
        obx_2.obx_5 = '125'
        obx_2.units = CWE(cwe_1='umol/L')
        obx_2.reference_range = '50-250'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260306155000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='53166-5', cwe_2='纈胺酸(Val)', cwe_3='LN')
        obx_3.obx_5 = '140'
        obx_3.units = CWE(cwe_1='umol/L')
        obx_3.reference_range = '60-280'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260306155000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='53192-1', cwe_2='丙醯肉鹼(C3)', cwe_3='LN')
        obx_4.obx_5 = '2.8'
        obx_4.units = CWE(cwe_1='umol/L')
        obx_4.reference_range = '0.5-5.0'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260306155000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='53194-7', cwe_2='辛醯肉鹼(C8)', cwe_3='LN')
        obx_5.obx_5 = '0.12'
        obx_5.units = CWE(cwe_1='umol/L')
        obx_5.reference_range = '<0.5'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260306155000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'FT'
        obx_6.observation_identifier = CWE(cwe_1='62292-8', cwe_2='串聯質譜儀篩檢結論', cwe_3='LN')
        obx_6.obx_5 = '擴大新生兒篩檢(串聯質譜儀)所有項目均在正常範圍內。'
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
    """ Based on live/tw/tw-ntuh-newborn.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS-NTUH')
        msh.sending_facility = HD(hd_1='NTUH_HOSP')
        msh.receiving_application = HD(hd_1='NBS-NTUH')
        msh.receiving_facility = HD(hd_1='NTUH_NBS')
        msh.date_time_of_message = '20260320090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'MSG20260320090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260320090000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT1000200', cx_4='NTUH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='魏', xpn_2='小慧')
        pid.date_time_of_birth = '20260305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        pid.pid_13 = '02-29021234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'J957123468'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='魏陳雅惠', xpn_2='PAT1000201')
        nk1.relationship = CWE(cwe_1='MTH')
        nk1.address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        nk1.nk1_5 = '02-29021234'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin

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
    """ Based on live/tw/tw-ntuh-newborn.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NBS-NTUH')
        msh.sending_facility = HD(hd_1='NTUH_NBS')
        msh.receiving_application = HD(hd_1='HIS-NTUH')
        msh.receiving_facility = HD(hd_1='NTUH_HOSP')
        msh.date_time_of_message = '20260305143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260305143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT1000100', cx_4='NTUH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='潘', xpn_2='小傑')
        pid.date_time_of_birth = '20260301'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='新北市永和區永和路二段55號', xad_3='新北市', xad_4='23449', xad_5='TW')
        pid.pid_13 = '02-29251234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='潘李佳穎', xpn_2='PAT1000101')
        nk1.relationship = CWE(cwe_1='MTH')
        nk1.address = XAD(xad_1='新北市永和區永和路二段55號', xad_3='新北市', xad_4='23449', xad_5='TW')
        nk1.nk1_5 = '02-29251234'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = OruR01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NICU', pl_2='201', pl_3='01')
        pv1.pv1_7 = 'D1000100^方麗雲^^^^^NTUH_HOSP'
        pv1.visit_number = CX(cx_1='V1000100001')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.next_of_kin = next_of_kin
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='NBS1000100003')
        orc.orc_10 = 'D1000100^方麗雲'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='NBS1000100003')
        obr.universal_service_identifier = CWE(cwe_1='54111-0', cwe_2='新生兒聽力篩檢', cwe_3='LN')
        obr.observation_date_time = '20260305100000'
        obr.obr_16 = 'D1000100^方麗雲'
        obr.results_rpt_status_chng_date_time = '20260305140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='54111-0', cwe_2='右耳OAE結果', cwe_3='LN')
        obx.obx_5 = 'PASS^通過^LOCAL'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260305140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='54111-0', cwe_2='左耳OAE結果', cwe_3='LN')
        obx_2.obx_5 = 'PASS^通過^LOCAL'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260305140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'FT'
        obx_3.observation_identifier = CWE(cwe_1='54111-0', cwe_2='聽力篩檢結論', cwe_3='LN')
        obx_3.obx_5 = '雙耳耳聲傳射(OAE)篩檢通過。'
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
    """ Based on live/tw/tw-ntuh-newborn.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NBS-NTUH')
        msh.sending_facility = HD(hd_1='NTUH_NBS')
        msh.receiving_application = HD(hd_1='HIS-NTUH')
        msh.receiving_facility = HD(hd_1='NTUH_HOSP')
        msh.date_time_of_message = '20260309143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260309143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT1000200', cx_4='NTUH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='魏', xpn_2='小慧')
        pid.date_time_of_birth = '20260305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        pid.pid_13 = '02-29021234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='魏陳雅惠', xpn_2='PAT1000201')
        nk1.relationship = CWE(cwe_1='MTH')
        nk1.address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        nk1.nk1_5 = '02-29021234'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = OruR01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NUR', pl_2='101', pl_3='03')
        pv1.pv1_7 = 'D1000200^郝建鈞^^^^^NTUH_HOSP'
        pv1.visit_number = CX(cx_1='V1000200001')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.next_of_kin = next_of_kin
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='NBS1000200005')
        orc.orc_10 = 'D1000200^郝建鈞'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='NBS1000200005')
        obr.universal_service_identifier = CWE(cwe_1='54111-0', cwe_2='新生兒聽力篩檢', cwe_3='LN')
        obr.observation_date_time = '20260309100000'
        obr.obr_16 = 'D1000200^郝建鈞'
        obr.results_rpt_status_chng_date_time = '20260309140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='54111-0', cwe_2='右耳OAE結果', cwe_3='LN')
        obx.obx_5 = 'PASS^通過^LOCAL'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260309140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='54111-0', cwe_2='左耳OAE結果', cwe_3='LN')
        obx_2.obx_5 = 'PASS^通過^LOCAL'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260309140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'FT'
        obx_3.observation_identifier = CWE(cwe_1='54111-0', cwe_2='聽力篩檢結論', cwe_3='LN')
        obx_3.obx_5 = '雙耳耳聲傳射(OAE)篩檢通過。'
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
    """ Based on live/tw/tw-ntuh-newborn.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NBS-NTUH')
        msh.sending_facility = HD(hd_1='NTUH_NBS')
        msh.receiving_application = HD(hd_1='HIS-NTUH')
        msh.receiving_facility = HD(hd_1='NTUH_HOSP')
        msh.date_time_of_message = '20260605143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG20260605143000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'BIG-5'
        msh.principal_language_of_message = CWE(cwe_1='zh-TW')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT1000200', cx_4='NTUH_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='魏', xpn_2='小慧')
        pid.date_time_of_birth = '20260305'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        pid.pid_13 = '02-29021234'
        pid.primary_language = CWE(cwe_1='zh-TW')
        pid.marital_status = CWE(cwe_1='M')
        pid.pid_19 = 'J957123468'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='魏陳雅惠', xpn_2='PAT1000201')
        nk1.relationship = CWE(cwe_1='MTH')
        nk1.address = XAD(xad_1='新北市新莊區中正路738號', xad_3='新北市', xad_4='24251', xad_5='TW')
        nk1.nk1_5 = '02-29021234'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = OruR01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PED', pl_2='101', pl_3='01')
        pv1.pv1_7 = 'D1000200^郝建鈞^^^^^NTUH_HOSP'
        pv1.visit_number = CX(cx_1='V1000200004')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.next_of_kin = next_of_kin
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='NBS1000200006')
        orc.orc_10 = 'D1000200^郝建鈞'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='NBS1000200006')
        obr.universal_service_identifier = CWE(cwe_1='24348-5', cwe_2='甲狀腺功能追蹤檢查(三個月)', cwe_3='LN')
        obr.observation_date_time = '20260605093000'
        obr.obr_16 = 'D1000200^郝建鈞'
        obr.results_rpt_status_chng_date_time = '20260605140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='促甲狀腺激素(TSH)', cwe_3='LN')
        obx.obx_5 = '4.8'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.7-5.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260605140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3026-2', cwe_2='游離甲狀腺素(FT4)', cwe_3='LN')
        obx_2.obx_5 = '1.4'
        obx_2.units = CWE(cwe_1='ng/dL')
        obx_2.reference_range = '0.8-2.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260605140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3053-6', cwe_2='游離三碘甲狀腺原氨酸(FT3)', cwe_3='LN')
        obx_3.obx_5 = '3.2'
        obx_3.units = CWE(cwe_1='pg/mL')
        obx_3.reference_range = '2.0-5.2'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260605140000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'FT'
        obx_4.observation_identifier = CWE(cwe_1='24348-5', cwe_2='追蹤結論', cwe_3='LN')
        obx_4.obx_5 = 'Levothyroxine治療三個月後甲狀腺功能已正常化。TSH 4.8 mIU/L，FT4 1.4 ng/dL，FT3 3.2 pg/mL均在正常範圍。建議繼續目前劑量，三個月後再追蹤。'
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
