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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, EIP, FC, HD, MSG, PL, PT, VID, XAD, XCN, XPN
from zato.hl7v2.v2_9.groups import OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import DG1, MSH, OBR, OBX, ORC, PID, PV1

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('dk', 'dk-webreq.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/dk/dk-webreq.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WEBREQ')
        msh.sending_facility = HD(hd_1='GP_KLINIK')
        msh.receiving_application = HD(hd_1='LABKA')
        msh.receiving_facility = HD(hd_1='KBA')
        msh.date_time_of_message = '20260401081500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'WR00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0506842021', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Olsen', xpn_2='Mads', xpn_3='Aksel', xpn_5='')
        pid.date_time_of_birth = '19840605'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vindegade 12', xad_3='Silkeborg', xad_5='8600', xad_6='DK')
        pid.pid_13 = '^^PH^+4540183227~^^CP^+4529996165'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GP12345', pl_2='LÆGERNE_I_VALBY', pl_3='AMB')
        pv1.attending_doctor = XCN(xcn_1='GP001', xcn_2='Nielsen', xcn_3='Lisbeth', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ALMEN')
        pv1.financial_class = FC(fc_1='GP202604010001')

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
        orc.placer_order_number = EI(ei_1='ORD20260401001', ei_2='WEBREQ')
        orc.parent_order = EIP(eip_1='20260401081500')
        orc.orc_11 = 'GP001^Nielsen^Lisbeth^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260401001', ei_2='WEBREQ')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Komplet blodtælling', cwe_3='LN')
        obr.observation_date_time = '20260401081500'
        obr.relevant_clinical_information = CWE(cwe_1='Træthed og svimmelhed')
        obr.obr_14 = 'GP001^Nielsen^Lisbeth^^^Dr.'

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
        obr_2.placer_order_number = EI(ei_1='ORD20260401001', ei_2='WEBREQ')
        obr_2.universal_service_identifier = CWE(cwe_1='FERR', cwe_2='Ferritin', cwe_3='LN')
        obr_2.observation_date_time = '20260401081500'
        obr_2.obr_15 = 'GP001^Nielsen^Lisbeth^^^Dr.'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='ORD20260401001', ei_2='WEBREQ')
        obr_3.universal_service_identifier = CWE(cwe_1='THYR', cwe_2='TSH og frit T4', cwe_3='LN')
        obr_3.observation_date_time = '20260401081500'
        obr_3.obr_15 = 'GP001^Nielsen^Lisbeth^^^Dr.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3]

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
    """ Based on live/dk/dk-webreq.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WEBREQ')
        msh.sending_facility = HD(hd_1='GP_KLINIK')
        msh.receiving_application = HD(hd_1='LABKA')
        msh.receiving_facility = HD(hd_1='KBA')
        msh.date_time_of_message = '20260402083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'WR00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1711625311', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Mortensen', xpn_2='Martin', xpn_3='Poul', xpn_5='')
        pid.date_time_of_birth = '19621117'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Reventlowsvej 94', xad_3='Herning', xad_5='7400', xad_6='DK')
        pid.pid_13 = '^^PH^+4567873260'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GP23456', pl_2='LÆGERNE_PÅ_MUNKERISVEJ', pl_3='AMB')
        pv1.attending_doctor = XCN(xcn_1='GP002', xcn_2='Lund', xcn_3='Tove', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ALMEN')
        pv1.financial_class = FC(fc_1='GP202604020001')

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
        orc.placer_order_number = EI(ei_1='ORD20260402001', ei_2='WEBREQ')
        orc.parent_order = EIP(eip_1='20260402083000')
        orc.orc_11 = 'GP002^Lund^Tove^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260402001', ei_2='WEBREQ')
        obr.universal_service_identifier = CWE(cwe_1='HBA1C', cwe_2='HbA1c', cwe_3='LN')
        obr.observation_date_time = '20260402083000'
        obr.relevant_clinical_information = CWE(cwe_1='Diabetes mellitus type 2, årskontrol')
        obr.obr_14 = 'GP002^Lund^Tove^^^Dr.'

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
        obr_2.placer_order_number = EI(ei_1='ORD20260402001', ei_2='WEBREQ')
        obr_2.universal_service_identifier = CWE(cwe_1='GLUC', cwe_2='Faste-glukose', cwe_3='LN')
        obr_2.observation_date_time = '20260402083000'
        obr_2.obr_15 = 'GP002^Lund^Tove^^^Dr.'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='ORD20260402001', ei_2='WEBREQ')
        obr_3.universal_service_identifier = CWE(cwe_1='LIPID', cwe_2='Lipidprofil', cwe_3='LN')
        obr_3.observation_date_time = '20260402083000'
        obr_3.obr_15 = 'GP002^Lund^Tove^^^Dr.'

        # .. build OBR ..
        obr_4 = OBR()
        obr_4.set_id_obr = '4'
        obr_4.placer_order_number = EI(ei_1='ORD20260402001', ei_2='WEBREQ')
        obr_4.universal_service_identifier = CWE(cwe_1='RENAL', cwe_2='Kreatinin og eGFR', cwe_3='LN')
        obr_4.observation_date_time = '20260402083000'
        obr_4.obr_15 = 'GP002^Lund^Tove^^^Dr.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3, obr_4]

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
    """ Based on live/dk/dk-webreq.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WEBREQ')
        msh.sending_facility = HD(hd_1='GP_KLINIK')
        msh.receiving_application = HD(hd_1='CARESTREAM_RIS')
        msh.receiving_facility = HD(hd_1='AAUH_RAD')
        msh.date_time_of_message = '20260403091000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'WR00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2309687170', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Jørgensen', xpn_2='Stine', xpn_3='Viola', xpn_5='')
        pid.date_time_of_birth = '19680923'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Algade 30', xad_3='Risskov', xad_5='8240', xad_6='DK')
        pid.pid_13 = '^^PH^+4548556523'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GP34567', pl_2='STRANDVEJENS_LÆGEHUS', pl_3='AMB')
        pv1.attending_doctor = XCN(xcn_1='GP003', xcn_2='Bang', xcn_3='Kristian', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ALMEN')
        pv1.financial_class = FC(fc_1='GP202604030001')

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
        orc.placer_order_number = EI(ei_1='ORD20260403001', ei_2='WEBREQ')
        orc.parent_order = EIP(eip_1='20260403091000')
        orc.orc_11 = 'GP003^Bang^Kristian^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260403001', ei_2='WEBREQ')
        obr.universal_service_identifier = CWE(cwe_1='XTHORAX', cwe_2='Røntgen af thorax', cwe_3='LOCAL')
        obr.observation_date_time = '20260403091000'
        obr.relevant_clinical_information = CWE(cwe_1='Vedvarende hoste >3 uger, ryger')
        obr.obr_14 = 'GP003^Bang^Kristian^^^Dr.'

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
    """ Based on live/dk/dk-webreq.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WEBREQ')
        msh.sending_facility = HD(hd_1='GP_KLINIK')
        msh.receiving_application = HD(hd_1='BCC')
        msh.receiving_facility = HD(hd_1='OUH')
        msh.date_time_of_message = '20260404080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'WR00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1903787609', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Poulsen', xpn_2='Anders', xpn_3='Henning', xpn_5='')
        pid.date_time_of_birth = '19780319'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Skovvej 13', xad_3='Hellerup', xad_5='2900', xad_6='DK')
        pid.pid_13 = '^^PH^+4552219331'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='R')
        pv1.assigned_patient_location = PL(pl_1='GP45678', pl_2='RUGÅRDSVEJS_LÆGEHUS', pl_3='AMB')
        pv1.attending_doctor = XCN(xcn_1='GP004', xcn_2='Mortensen', xcn_3='Peter', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ALMEN')
        pv1.financial_class = FC(fc_1='GP202604040001')

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
        orc.placer_order_number = EI(ei_1='ORD20260404001', ei_2='WEBREQ')
        orc.parent_order = EIP(eip_1='20260404080000')
        orc.orc_11 = 'GP004^Mortensen^Peter^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260404001', ei_2='WEBREQ')
        obr.universal_service_identifier = CWE(cwe_1='REF_KAR', cwe_2='Henvisning til kardiologi', cwe_3='LOCAL')
        obr.observation_date_time = '20260404080000'
        obr.relevant_clinical_information = CWE(cwe_1='Brystsmerter ved anstrengelse, ønske om belastnings-EKG')
        obr.obr_14 = 'GP004^Mortensen^Peter^^^Dr.'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='DI209', cwe_2='Angina pectoris, uspecificeret', cwe_3='ICD10DK')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

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
    """ Based on live/dk/dk-webreq.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WEBREQ')
        msh.sending_facility = HD(hd_1='GP_KLINIK')
        msh.receiving_application = HD(hd_1='LABKA')
        msh.receiving_facility = HD(hd_1='KBA')
        msh.date_time_of_message = '20260405100000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'WR00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0103785256', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Jørgensen', xpn_2='Astrid', xpn_3='Gudrun', xpn_5='')
        pid.date_time_of_birth = '19780301'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Søndergade 39', xad_3='Slagelse', xad_5='4200', xad_6='DK')
        pid.pid_13 = '^^PH^+4588827879'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GP56789', pl_2='AALBORG_MIDTBY_LÆGER', pl_3='AMB')
        pv1.attending_doctor = XCN(xcn_1='GP005', xcn_2='Frandsen', xcn_3='Karsten', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ALMEN')
        pv1.financial_class = FC(fc_1='GP202604050001')

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
        orc.placer_order_number = EI(ei_1='ORD20260405001', ei_2='WEBREQ')
        orc.parent_order = EIP(eip_1='20260405100000')
        orc.orc_11 = 'GP005^Frandsen^Karsten^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260405001', ei_2='WEBREQ')
        obr.universal_service_identifier = CWE(cwe_1='CRP', cwe_2='C-reaktivt protein', cwe_3='LN')
        obr.observation_date_time = '20260405100000'
        obr.relevant_clinical_information = CWE(cwe_1='AKUT - feber og flankesmerter')
        obr.obr_14 = 'GP005^Frandsen^Karsten^^^Dr.'

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
        obr_2.placer_order_number = EI(ei_1='ORD20260405001', ei_2='WEBREQ')
        obr_2.universal_service_identifier = CWE(cwe_1='UCUL', cwe_2='Urindyrkning', cwe_3='LN')
        obr_2.observation_date_time = '20260405100000'
        obr_2.obr_15 = 'GP005^Frandsen^Karsten^^^Dr.'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='ORD20260405001', ei_2='WEBREQ')
        obr_3.universal_service_identifier = CWE(cwe_1='ELEC', cwe_2='Elektrolytter', cwe_3='LN')
        obr_3.observation_date_time = '20260405100000'
        obr_3.obr_15 = 'GP005^Frandsen^Karsten^^^Dr.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3]

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
    """ Based on live/dk/dk-webreq.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABKA')
        msh.sending_facility = HD(hd_1='KBA')
        msh.receiving_application = HD(hd_1='WEBREQ')
        msh.receiving_facility = HD(hd_1='GP_KLINIK')
        msh.date_time_of_message = '20260401143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'WR00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0506842021', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Olsen', xpn_2='Mads', xpn_3='Aksel', xpn_5='')
        pid.date_time_of_birth = '19840605'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vindegade 12', xad_3='Silkeborg', xad_5='8600', xad_6='DK')
        pid.pid_13 = '^^PH^+4540183227'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GP12345', pl_2='LÆGERNE_I_VALBY', pl_3='AMB')
        pv1.attending_doctor = XCN(xcn_1='GP001', xcn_2='Nielsen', xcn_3='Lisbeth', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ALMEN')
        pv1.financial_class = FC(fc_1='GP202604010001')

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
        orc.placer_order_number = EI(ei_1='ORD20260401001', ei_2='WEBREQ')
        orc.parent_order = EIP(eip_1='20260401143000')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260401001', ei_2='WEBREQ')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Komplet blodtælling', cwe_3='LN')
        obr.observation_date_time = '20260401081500'
        obr.obr_15 = 'GP001^Nielsen^Lisbeth^^^Dr.'
        obr.filler_field_2 = '20260401143000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='HGB', cwe_2='Hæmoglobin', cwe_3='LN')
        obx.obx_5 = '6.8'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '8.3-10.5'
        obx.interpretation_codes = CWE(cwe_1='LL')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='MCV', cwe_2='Middelcellevolumen', cwe_3='LN')
        obx_2.obx_5 = '68'
        obx_2.units = CWE(cwe_1='fL')
        obx_2.reference_range = '82-98'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='WBC', cwe_2='Leukocytter', cwe_3='LN')
        obx_3.obx_5 = '5.2'
        obx_3.units = CWE(cwe_1='10*9/L')
        obx_3.reference_range = '3.5-10.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='PLT', cwe_2='Trombocytter', cwe_3='LN')
        obx_4.obx_5 = '380'
        obx_4.units = CWE(cwe_1='10*9/L')
        obx_4.reference_range = '145-390'
        obx_4.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/dk/dk-webreq.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABKA')
        msh.sending_facility = HD(hd_1='KBA')
        msh.receiving_application = HD(hd_1='WEBREQ')
        msh.receiving_facility = HD(hd_1='GP_KLINIK')
        msh.date_time_of_message = '20260401150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'WR00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0506842021', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Olsen', xpn_2='Mads', xpn_3='Aksel', xpn_5='')
        pid.date_time_of_birth = '19840605'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vindegade 12', xad_3='Silkeborg', xad_5='8600', xad_6='DK')
        pid.pid_13 = '^^PH^+4540183227'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GP12345', pl_2='LÆGERNE_I_VALBY', pl_3='AMB')
        pv1.attending_doctor = XCN(xcn_1='GP001', xcn_2='Nielsen', xcn_3='Lisbeth', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ALMEN')
        pv1.financial_class = FC(fc_1='GP202604010001')

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
        orc.placer_order_number = EI(ei_1='ORD20260401002', ei_2='WEBREQ')
        orc.parent_order = EIP(eip_1='20260401150000')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260401002', ei_2='WEBREQ')
        obr.universal_service_identifier = CWE(cwe_1='FERR', cwe_2='Ferritin', cwe_3='LN')
        obr.observation_date_time = '20260401081500'
        obr.obr_15 = 'GP001^Nielsen^Lisbeth^^^Dr.'
        obr.filler_field_2 = '20260401150000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='FERR', cwe_2='Ferritin', cwe_3='LN')
        obx.obx_5 = '6'
        obx.units = CWE(cwe_1='ug/L')
        obx.reference_range = '30-400'
        obx.interpretation_codes = CWE(cwe_1='LL')
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
    """ Based on live/dk/dk-webreq.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABKA')
        msh.sending_facility = HD(hd_1='KBA')
        msh.receiving_application = HD(hd_1='WEBREQ')
        msh.receiving_facility = HD(hd_1='GP_KLINIK')
        msh.date_time_of_message = '20260401153000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'WR00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0506842021', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Olsen', xpn_2='Mads', xpn_3='Aksel', xpn_5='')
        pid.date_time_of_birth = '19840605'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vindegade 12', xad_3='Silkeborg', xad_5='8600', xad_6='DK')
        pid.pid_13 = '^^PH^+4540183227'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GP12345', pl_2='LÆGERNE_I_VALBY', pl_3='AMB')
        pv1.attending_doctor = XCN(xcn_1='GP001', xcn_2='Nielsen', xcn_3='Lisbeth', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ALMEN')
        pv1.financial_class = FC(fc_1='GP202604010001')

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
        orc.placer_order_number = EI(ei_1='ORD20260401003', ei_2='WEBREQ')
        orc.parent_order = EIP(eip_1='20260401153000')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260401003', ei_2='WEBREQ')
        obr.universal_service_identifier = CWE(cwe_1='THYR', cwe_2='TSH og frit T4', cwe_3='LN')
        obr.observation_date_time = '20260401081500'
        obr.obr_15 = 'GP001^Nielsen^Lisbeth^^^Dr.'
        obr.filler_field_2 = '20260401153000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='TSH', cwe_2='Thyreoideastimulerende hormon', cwe_3='LN')
        obx.obx_5 = '2.1'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.27-4.20'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='FT4', cwe_2='Frit thyroxin', cwe_3='LN')
        obx_2.obx_5 = '16.5'
        obx_2.units = CWE(cwe_1='pmol/L')
        obx_2.reference_range = '12.0-22.0'
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
    """ Based on live/dk/dk-webreq.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABKA')
        msh.sending_facility = HD(hd_1='KBA')
        msh.receiving_application = HD(hd_1='WEBREQ')
        msh.receiving_facility = HD(hd_1='GP_KLINIK')
        msh.date_time_of_message = '20260402143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'WR00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1711625311', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Mortensen', xpn_2='Martin', xpn_3='Poul', xpn_5='')
        pid.date_time_of_birth = '19621117'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Reventlowsvej 94', xad_3='Herning', xad_5='7400', xad_6='DK')
        pid.pid_13 = '^^PH^+4567873260'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GP23456', pl_2='LÆGERNE_PÅ_MUNKERISVEJ', pl_3='AMB')
        pv1.attending_doctor = XCN(xcn_1='GP002', xcn_2='Lund', xcn_3='Tove', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ALMEN')
        pv1.financial_class = FC(fc_1='GP202604020001')

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
        orc.placer_order_number = EI(ei_1='ORD20260402001', ei_2='WEBREQ')
        orc.parent_order = EIP(eip_1='20260402143000')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260402001', ei_2='WEBREQ')
        obr.universal_service_identifier = CWE(cwe_1='MISC', cwe_2='Diabeteskontrol - samlet rapport', cwe_3='LN')
        obr.observation_date_time = '20260402083000'
        obr.obr_15 = 'GP002^Lund^Tove^^^Dr.'
        obr.filler_field_2 = '20260402143000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='HBA1C', cwe_2='HbA1c', cwe_3='LN')
        obx.obx_5 = '55'
        obx.units = CWE(cwe_1='mmol/mol')
        obx.reference_range = '<48'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='GLUC', cwe_2='P-Glukose (faste)', cwe_3='LN')
        obx_2.obx_5 = '8.2'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '4.2-6.3'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ED'
        obx_3.observation_identifier = CWE(cwe_1='PDF', cwe_2='Samlet labrapport', cwe_3='LN')
        obx_3.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UK'
        )
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
    """ Based on live/dk/dk-webreq.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WEBREQ')
        msh.sending_facility = HD(hd_1='GP_KLINIK')
        msh.receiving_application = HD(hd_1='CARESTREAM_RIS')
        msh.receiving_facility = HD(hd_1='OUH_RAD')
        msh.date_time_of_message = '20260406090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'WR00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0707656590', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Dahl', xpn_2='Laura', xpn_3='Esther', xpn_5='')
        pid.date_time_of_birth = '19650707'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Strandvejen 144', xad_3='Horsens', xad_5='8700', xad_6='DK')
        pid.pid_13 = '^^PH^+4532184422'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GP67890', pl_2='HUNDERUPVEJ_LÆGEPRAKSIS', pl_3='AMB')
        pv1.attending_doctor = XCN(xcn_1='GP006', xcn_2='Hansen', xcn_3='Rasmus', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ALMEN')
        pv1.financial_class = FC(fc_1='GP202604060001')

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
        orc.placer_order_number = EI(ei_1='ORD20260406001', ei_2='WEBREQ')
        orc.parent_order = EIP(eip_1='20260406090000')
        orc.orc_11 = 'GP006^Hansen^Rasmus^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260406001', ei_2='WEBREQ')
        obr.universal_service_identifier = CWE(cwe_1='ULLEVER', cwe_2='Ultralyd af lever og galdeveje', cwe_3='LOCAL')
        obr.observation_date_time = '20260406090000'
        obr.relevant_clinical_information = CWE(cwe_1='Forhøjede levertal ved blodprøvekontrol, udredning')
        obr.obr_14 = 'GP006^Hansen^Rasmus^^^Dr.'

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
    """ Based on live/dk/dk-webreq.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WEBREQ')
        msh.sending_facility = HD(hd_1='GP_KLINIK')
        msh.receiving_application = HD(hd_1='BCC')
        msh.receiving_facility = HD(hd_1='OUH')
        msh.date_time_of_message = '20260407080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'WR00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2207739946', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Lund', xpn_2='Laura', xpn_3='Karoline', xpn_5='')
        pid.date_time_of_birth = '19730722'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Havnevej 241', xad_3='Herlev', xad_5='2730', xad_6='DK')
        pid.pid_13 = '^^PH^+4536268450'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='R')
        pv1.assigned_patient_location = PL(pl_1='GP67890', pl_2='HUNDERUPVEJ_LÆGEPRAKSIS', pl_3='AMB')
        pv1.attending_doctor = XCN(xcn_1='GP006', xcn_2='Hansen', xcn_3='Rasmus', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ALMEN')
        pv1.financial_class = FC(fc_1='GP202604070001')

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
        orc.placer_order_number = EI(ei_1='ORD20260407001', ei_2='WEBREQ')
        orc.parent_order = EIP(eip_1='20260407080000')
        orc.orc_11 = 'GP006^Hansen^Rasmus^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260407001', ei_2='WEBREQ')
        obr.universal_service_identifier = CWE(cwe_1='REF_GAS', cwe_2='Henvisning til gastroenterologi', cwe_3='LOCAL')
        obr.observation_date_time = '20260407080000'
        obr.relevant_clinical_information = CWE(cwe_1='Ændrede afføringsvaner, vægttab 5 kg over 2 måneder, mistanke om coloncancer')
        obr.obr_14 = 'GP006^Hansen^Rasmus^^^Dr.'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='DC189', cwe_2='Coloncancer, uspecificeret', cwe_3='ICD10DK')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

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
    """ Based on live/dk/dk-webreq.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WEBREQ')
        msh.sending_facility = HD(hd_1='GP_KLINIK')
        msh.receiving_application = HD(hd_1='LABKA')
        msh.receiving_facility = HD(hd_1='KBA')
        msh.date_time_of_message = '20260408083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'WR00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1203885198', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Skov', xpn_2='Birgit', xpn_3='Karla', xpn_5='')
        pid.date_time_of_birth = '19880312'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Skolegade 196', xad_3='Hillerød', xad_5='3400', xad_6='DK')
        pid.pid_13 = '^^PH^+4556499781'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GP78901', pl_2='SKOLEGADE_LÆGERNE', pl_3='AMB')
        pv1.attending_doctor = XCN(xcn_1='GP007', xcn_2='Jensen', xcn_3='Mads', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ALMEN')
        pv1.financial_class = FC(fc_1='GP202604080001')

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
        orc.placer_order_number = EI(ei_1='ORD20260408001', ei_2='WEBREQ')
        orc.parent_order = EIP(eip_1='20260408083000')
        orc.orc_11 = 'GP007^Jensen^Mads^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260408001', ei_2='WEBREQ')
        obr.universal_service_identifier = CWE(cwe_1='GRAV', cwe_2='Graviditetspakke', cwe_3='LN')
        obr.observation_date_time = '20260408083000'
        obr.relevant_clinical_information = CWE(cwe_1='Graviditet uge 12, 1. trimester-screening')
        obr.obr_14 = 'GP007^Jensen^Mads^^^Dr.'

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
        obr_2.placer_order_number = EI(ei_1='ORD20260408001', ei_2='WEBREQ')
        obr_2.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Komplet blodtælling', cwe_3='LN')
        obr_2.observation_date_time = '20260408083000'
        obr_2.obr_15 = 'GP007^Jensen^Mads^^^Dr.'

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='ORD20260408001', ei_2='WEBREQ')
        obr_3.universal_service_identifier = CWE(cwe_1='BTYPE', cwe_2='Blodtype og antistofscreening', cwe_3='LN')
        obr_3.observation_date_time = '20260408083000'
        obr_3.obr_15 = 'GP007^Jensen^Mads^^^Dr.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2, obr_3]

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
    """ Based on live/dk/dk-webreq.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABKA')
        msh.sending_facility = HD(hd_1='KBA')
        msh.receiving_application = HD(hd_1='WEBREQ')
        msh.receiving_facility = HD(hd_1='GP_KLINIK')
        msh.date_time_of_message = '20260402160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'WR00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1711625311', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Mortensen', xpn_2='Martin', xpn_3='Poul', xpn_5='')
        pid.date_time_of_birth = '19621117'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Reventlowsvej 94', xad_3='Herning', xad_5='7400', xad_6='DK')
        pid.pid_13 = '^^PH^+4567873260'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GP23456', pl_2='LÆGERNE_PÅ_MUNKERISVEJ', pl_3='AMB')
        pv1.attending_doctor = XCN(xcn_1='GP002', xcn_2='Lund', xcn_3='Tove', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ALMEN')
        pv1.financial_class = FC(fc_1='GP202604020001')

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
        orc.placer_order_number = EI(ei_1='ORD20260402002', ei_2='WEBREQ')
        orc.parent_order = EIP(eip_1='20260402160000')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260402002', ei_2='WEBREQ')
        obr.universal_service_identifier = CWE(cwe_1='LIPID', cwe_2='Lipidprofil', cwe_3='LN')
        obr.observation_date_time = '20260402083000'
        obr.obr_15 = 'GP002^Lund^Tove^^^Dr.'
        obr.filler_field_2 = '20260402160000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='CHOL', cwe_2='Total kolesterol', cwe_3='LN')
        obx.obx_5 = '5.8'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '<5.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='LDL', cwe_2='LDL-kolesterol', cwe_3='LN')
        obx_2.obx_5 = '3.6'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '<3.0'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='HDL', cwe_2='HDL-kolesterol', cwe_3='LN')
        obx_3.obx_5 = '1.1'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '>1.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='TRIG', cwe_2='Triglycerider', cwe_3='LN')
        obx_4.obx_5 = '2.4'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '<2.0'
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
    """ Based on live/dk/dk-webreq.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARESTREAM_RIS')
        msh.sending_facility = HD(hd_1='AAUH_RAD')
        msh.receiving_application = HD(hd_1='WEBREQ')
        msh.receiving_facility = HD(hd_1='GP_KLINIK')
        msh.date_time_of_message = '20260404141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'WR00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2309687170', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Jørgensen', xpn_2='Stine', xpn_3='Viola', xpn_5='')
        pid.date_time_of_birth = '19680923'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Algade 30', xad_3='Risskov', xad_5='8240', xad_6='DK')
        pid.pid_13 = '^^PH^+4548556523'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GP34567', pl_2='STRANDVEJENS_LÆGEHUS', pl_3='AMB')
        pv1.attending_doctor = XCN(xcn_1='GP003', xcn_2='Bang', xcn_3='Kristian', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ALMEN')
        pv1.financial_class = FC(fc_1='GP202604030001')

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
        orc.placer_order_number = EI(ei_1='ORD20260403001', ei_2='WEBREQ')
        orc.parent_order = EIP(eip_1='20260404141500')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260403001', ei_2='WEBREQ')
        obr.universal_service_identifier = CWE(cwe_1='XTHORAX', cwe_2='Røntgen af thorax', cwe_3='LOCAL')
        obr.observation_date_time = '20260403091000'
        obr.obr_15 = 'GP003^Bang^Kristian^^^Dr.'
        obr.filler_field_2 = '20260404141500'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='RADRPT', cwe_2='Radiologibeskrivelse', cwe_3='LN')
        obx.obx_5 = (
            'Røntgen af thorax PA og lateral: Lungefelterne frie. Hjertestørrelse normal. Normale mediastinale konturer. Ingen pleuraeffusion. Normalt fund.'
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
    """ Based on live/dk/dk-webreq.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARESTREAM_RIS')
        msh.sending_facility = HD(hd_1='AAUH_RAD')
        msh.receiving_application = HD(hd_1='WEBREQ')
        msh.receiving_facility = HD(hd_1='GP_KLINIK')
        msh.date_time_of_message = '20260404150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'WR00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='2309687170', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Jørgensen', xpn_2='Stine', xpn_3='Viola', xpn_5='')
        pid.date_time_of_birth = '19680923'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Algade 30', xad_3='Risskov', xad_5='8240', xad_6='DK')
        pid.pid_13 = '^^PH^+4548556523'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GP34567', pl_2='STRANDVEJENS_LÆGEHUS', pl_3='AMB')
        pv1.attending_doctor = XCN(xcn_1='GP003', xcn_2='Bang', xcn_3='Kristian', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ALMEN')
        pv1.financial_class = FC(fc_1='GP202604030001')

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
        orc.placer_order_number = EI(ei_1='ORD20260403002', ei_2='CARESTREAM_RIS')
        orc.parent_order = EIP(eip_1='20260404150000')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260403002', ei_2='CARESTREAM_RIS')
        obr.universal_service_identifier = CWE(cwe_1='XTHORAX', cwe_2='Røntgen thorax - komplet rapport', cwe_3='LOCAL')
        obr.observation_date_time = '20260403091000'
        obr.obr_15 = 'GP003^Bang^Kristian^^^Dr.'
        obr.filler_field_2 = '20260404150000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Røntgenrapport', cwe_3='LN')
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
    """ Based on live/dk/dk-webreq.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WEBREQ')
        msh.sending_facility = HD(hd_1='GP_KLINIK')
        msh.receiving_application = HD(hd_1='COLUMNA_CIS')
        msh.receiving_facility = HD(hd_1='AARHUS_UH')
        msh.date_time_of_message = '20260409080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'WR00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0309552429', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Madsen', xpn_2='Niels', xpn_3='Poul', xpn_5='')
        pid.date_time_of_birth = '19550903'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Amagerbrogade 81', xad_3='Ballerup', xad_5='2750', xad_6='DK')
        pid.pid_13 = '^^PH^+4562484762'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='R')
        pv1.assigned_patient_location = PL(pl_1='GP89012', pl_2='PARK_ALLÉ_KLINIK', pl_3='AMB')
        pv1.attending_doctor = XCN(xcn_1='GP008', xcn_2='Christiansen', xcn_3='Niels', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ALMEN')
        pv1.financial_class = FC(fc_1='GP202604090001')

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
        orc.placer_order_number = EI(ei_1='ORD20260409001', ei_2='WEBREQ')
        orc.parent_order = EIP(eip_1='20260409080000')
        orc.orc_11 = 'GP008^Christiansen^Niels^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260409001', ei_2='WEBREQ')
        obr.universal_service_identifier = CWE(cwe_1='REF_EYE', cwe_2='Henvisning til øjenafdeling', cwe_3='LOCAL')
        obr.observation_date_time = '20260409080000'
        obr.relevant_clinical_information = CWE(cwe_1='Diabetes mellitus type 2, årlig øjenscreening for diabetisk retinopati')
        obr.obr_14 = 'GP008^Christiansen^Niels^^^Dr.'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='DE113A', cwe_2='Diabetisk retinopati', cwe_3='ICD10DK')
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

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
    """ Based on live/dk/dk-webreq.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WEBREQ')
        msh.sending_facility = HD(hd_1='GP_KLINIK')
        msh.receiving_application = HD(hd_1='LABKA')
        msh.receiving_facility = HD(hd_1='KBA')
        msh.date_time_of_message = '20260410081500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'WR00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0608716567', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Hald', xpn_2='Kristian', xpn_3='Aksel', xpn_5='')
        pid.date_time_of_birth = '19710806'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Silkeborgvej 96', xad_3='Thisted', xad_5='7700', xad_6='DK')
        pid.pid_13 = '^^PH^+4583825674'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GP90123', pl_2='AMAGERBRO_LÆGER', pl_3='AMB')
        pv1.attending_doctor = XCN(xcn_1='GP009', xcn_2='Olsen', xcn_3='Anders', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ALMEN')
        pv1.financial_class = FC(fc_1='GP202604100001')

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
        orc.placer_order_number = EI(ei_1='ORD20260410001', ei_2='WEBREQ')
        orc.parent_order = EIP(eip_1='20260410081500')
        orc.orc_11 = 'GP009^Olsen^Anders^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260410001', ei_2='WEBREQ')
        obr.universal_service_identifier = CWE(cwe_1='INR', cwe_2='INR-kontrol', cwe_3='LN')
        obr.observation_date_time = '20260410081500'
        obr.relevant_clinical_information = CWE(cwe_1='Atrieflimren, warfarinbehandling')
        obr.obr_14 = 'GP009^Olsen^Anders^^^Dr.'

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
    """ Based on live/dk/dk-webreq.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABKA')
        msh.sending_facility = HD(hd_1='KBA')
        msh.receiving_application = HD(hd_1='WEBREQ')
        msh.receiving_facility = HD(hd_1='GP_KLINIK')
        msh.date_time_of_message = '20260410130000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'WR00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0608716567', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Hald', xpn_2='Kristian', xpn_3='Aksel', xpn_5='')
        pid.date_time_of_birth = '19710806'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Silkeborgvej 96', xad_3='Thisted', xad_5='7700', xad_6='DK')
        pid.pid_13 = '^^PH^+4583825674'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GP90123', pl_2='AMAGERBRO_LÆGER', pl_3='AMB')
        pv1.attending_doctor = XCN(xcn_1='GP009', xcn_2='Olsen', xcn_3='Anders', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ALMEN')
        pv1.financial_class = FC(fc_1='GP202604100001')

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
        orc.placer_order_number = EI(ei_1='ORD20260410001', ei_2='WEBREQ')
        orc.parent_order = EIP(eip_1='20260410130000')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260410001', ei_2='WEBREQ')
        obr.universal_service_identifier = CWE(cwe_1='INR', cwe_2='INR-kontrol', cwe_3='LN')
        obr.observation_date_time = '20260410081500'
        obr.obr_15 = 'GP009^Olsen^Anders^^^Dr.'
        obr.filler_field_2 = '20260410130000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='INR', cwe_2='International Normalised Ratio', cwe_3='LN')
        obx.obx_5 = '3.5'
        obx.reference_range = '2.0-3.0'
        obx.interpretation_codes = CWE(cwe_1='H')
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
    """ Based on live/dk/dk-webreq.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WEBREQ')
        msh.sending_facility = HD(hd_1='GP_KLINIK')
        msh.receiving_application = HD(hd_1='LABKA')
        msh.receiving_facility = HD(hd_1='KBA')
        msh.date_time_of_message = '20260411083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'WR00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='1509655257', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Bang', xpn_2='Simon', xpn_3='Børge', xpn_5='')
        pid.date_time_of_birth = '19650915'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Randersvej 27', xad_3='Taastrup', xad_5='2630', xad_6='DK')
        pid.pid_13 = '^^PH^+4597497160'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GP01234', pl_2='BREDGADE_LÆGERNE', pl_3='AMB')
        pv1.attending_doctor = XCN(xcn_1='GP010', xcn_2='Bertelsen', xcn_3='Niels', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ALMEN')
        pv1.financial_class = FC(fc_1='GP202604110001')

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
        orc.placer_order_number = EI(ei_1='ORD20260411001', ei_2='WEBREQ')
        orc.parent_order = EIP(eip_1='20260411083000')
        orc.orc_11 = 'GP010^Bertelsen^Niels^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260411001', ei_2='WEBREQ')
        obr.universal_service_identifier = CWE(cwe_1='RENAL', cwe_2='Kreatinin, eGFR og karbamid', cwe_3='LN')
        obr.observation_date_time = '20260411083000'
        obr.relevant_clinical_information = CWE(cwe_1='Kronisk nyresygdom, halvårlig kontrol')
        obr.obr_14 = 'GP010^Bertelsen^Niels^^^Dr.'

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
        obr_2.placer_order_number = EI(ei_1='ORD20260411001', ei_2='WEBREQ')
        obr_2.universal_service_identifier = CWE(cwe_1='ELEC', cwe_2='Elektrolytter', cwe_3='LN')
        obr_2.observation_date_time = '20260411083000'
        obr_2.obr_15 = 'GP010^Bertelsen^Niels^^^Dr.'

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
    """ Based on live/dk/dk-webreq.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MADS')
        msh.sending_facility = HD(hd_1='SSI')
        msh.receiving_application = HD(hd_1='WEBREQ')
        msh.receiving_facility = HD(hd_1='GP_KLINIK')
        msh.date_time_of_message = '20260406161500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'WR00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='0103785256', cx_4='CPR', cx_5='NNDN')
        pid.patient_name = XPN(xpn_1='Jørgensen', xpn_2='Astrid', xpn_3='Gudrun', xpn_5='')
        pid.date_time_of_birth = '19780301'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Søndergade 39', xad_3='Slagelse', xad_5='4200', xad_6='DK')
        pid.pid_13 = '^^PH^+4588827879'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='GP56789', pl_2='AALBORG_MIDTBY_LÆGER', pl_3='AMB')
        pv1.attending_doctor = XCN(xcn_1='GP005', xcn_2='Frandsen', xcn_3='Karsten', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='ALMEN')
        pv1.financial_class = FC(fc_1='GP202604050001')

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
        orc.placer_order_number = EI(ei_1='ORD20260405001', ei_2='MADS')
        orc.parent_order = EIP(eip_1='20260406161500')

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20260405001', ei_2='MADS')
        obr.universal_service_identifier = CWE(cwe_1='UCUL', cwe_2='Urindyrkning', cwe_3='LN')
        obr.observation_date_time = '20260405100000'
        obr.obr_15 = 'GP005^Frandsen^Karsten^^^Dr.'
        obr.filler_field_2 = '20260406161500'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='ORGANISM', cwe_2='Identificeret mikroorganisme', cwe_3='LN')
        obx.obx_5 = 'ECO^Escherichia coli^LN'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='COLONY', cwe_2='Kolonital', cwe_3='LN')
        obx_2.obx_5 = '>100000'
        obx_2.units = CWE(cwe_1='CFU/mL')
        obx_2.nature_of_abnormal_test = 'A'
        obx_2.user_defined_access_checks = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='SUSCEPT', cwe_2='Følsomhed - Mecillinam', cwe_3='LN')
        obx_3.obx_5 = 'S'
        obx_3.interpretation_codes = CWE(cwe_1='A')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='SUSCEPT', cwe_2='Følsomhed - Nitrofurantoin', cwe_3='LN')
        obx_4.obx_5 = 'S'
        obx_4.interpretation_codes = CWE(cwe_1='A')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='SUSCEPT', cwe_2='Følsomhed - Trimethoprim', cwe_3='LN')
        obx_5.obx_5 = 'R'
        obx_5.interpretation_codes = CWE(cwe_1='A')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='SUSCEPT', cwe_2='Følsomhed - Ciprofloxacin', cwe_3='LN')
        obx_6.obx_5 = 'S'
        obx_6.interpretation_codes = CWE(cwe_1='A')
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
