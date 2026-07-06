# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.hl7v2 import HL7RawLine, parse_hl7
from zato.hl7v2.testing.live_util import load_message, md_path_for
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, EI, HD, MSG, OG, PL, PT, VID, XAD, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA39Patient, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, \
    OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12LocationResource, SiuS12Patient, \
    SiuS12PersonnelResource, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A09, ADT_A39, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, EVN, IN1, MRG, MSA, MSH, OBR, OBX, ORC, PID, PV1, RGS, RXE, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ch', 'ch-kisim.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ch/ch-kisim.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KISIM')
        msh.sending_facility = HD(hd_1='USZ_ZUERICH')
        msh.receiving_application = HD(hd_1='LABOR')
        msh.receiving_facility = HD(hd_1='USZ_ZUERICH')
        msh.date_time_of_message = '20260301080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'KISIM00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260301080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [
            CX(cx_1='PAT123456', cx_4='USZ&2.16.756.5.30.1.127.3.1&ISO', cx_5='MR'),
            CX(cx_1='7560123456789', cx_4='&2.16.756.5.31&ISO', cx_5='SS'),
        ]
        pid.patient_name = XPN(xpn_1='Burgener', xpn_2='Manfred', xpn_3='Heinz', xpn_5='Herr')
        pid.date_time_of_birth = '19650312'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Gerechtigkeitsgasse 169', xad_3='Chur', xad_5='7000', xad_6='CH')
        pid.pid_13 = '^^PH^0815908760~^^CP^0763528981'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='Zimmer 301', pl_3='Bett A', pl_4='Innere Medizin')
        pv1.pv1_7 = 'ARZ001^Senn^Sabine^^^Dr.^med.'
        pv1.pv1_8 = 'ARZ002^Glaus^Otto^^^Dr.^med.'
        pv1.vip_indicator = CWE(cwe_1='FALL00123')
        pv1.prior_temporary_location = PL(pl_1='20260301080000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='UVG')
        in1.insurance_company_id = CX(cx_1='CSS001')
        in1.insurance_company_name = XON(xon_1='CSS Versicherung')
        in1.insurance_company_address = XAD(xad_1='Tribschenstrasse 21', xad_3='Luzern', xad_5='6005', xad_6='CH')
        in1.insureds_id_number = CX(cx_1='756.1234.5678.97')

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
    """ Based on live/ch/ch-kisim.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KISIM')
        msh.sending_facility = HD(hd_1='USZ_ZUERICH')
        msh.receiving_application = HD(hd_1='LABOR')
        msh.receiving_facility = HD(hd_1='USZ_ZUERICH')
        msh.date_time_of_message = '20260302090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'KISIM00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260302090000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT123456', cx_4='USZ&2.16.756.5.30.1.127.3.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Burgener', xpn_2='Manfred', xpn_3='Heinz', xpn_5='Herr')
        pid.date_time_of_birth = '19650312'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Gerechtigkeitsgasse 169', xad_3='Chur', xad_5='7000', xad_6='CH')
        pid.pid_13 = '^^PH^0815908760~^^CP^0763528981'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='Zimmer 405', pl_3='Bett B', pl_4='Chirurgie')
        pv1.pv1_7 = 'ARZ003^Marti^Andreas^^^Prof.^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL00123')
        pv1.account_status = CWE(cwe_1='MED', cwe_2='Zimmer 301', cwe_3='Bett A', cwe_4='Innere Medizin')
        pv1.prior_temporary_location = PL(pl_1='20260302090000')

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
    """ Based on live/ch/ch-kisim.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KISIM')
        msh.sending_facility = HD(hd_1='USZ_ZUERICH')
        msh.receiving_application = HD(hd_1='LABOR')
        msh.receiving_facility = HD(hd_1='USZ_ZUERICH')
        msh.date_time_of_message = '20260310140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'KISIM00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260310140000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT123456', cx_4='USZ&2.16.756.5.30.1.127.3.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Burgener', xpn_2='Manfred', xpn_3='Heinz', xpn_5='Herr')
        pid.date_time_of_birth = '19650312'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Gerechtigkeitsgasse 169', xad_3='Chur', xad_5='7000', xad_6='CH')
        pid.pid_13 = '^^PH^0815908760~^^CP^0763528981'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='Zimmer 405', pl_3='Bett B', pl_4='Chirurgie')
        pv1.pv1_7 = 'ARZ003^Marti^Andreas^^^Prof.^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL00123')
        pv1.current_patient_balance = '20260310140000'

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
    """ Based on live/ch/ch-kisim.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KISIM')
        msh.sending_facility = HD(hd_1='INSEL_BERN')
        msh.receiving_application = HD(hd_1='POLIKLINIK')
        msh.receiving_facility = HD(hd_1='INSEL_BERN')
        msh.date_time_of_message = '20260315100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'KISIM00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260315100000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [
            CX(cx_1='PAT789012', cx_4='INSEL&2.16.756.5.30.1.128.1&ISO', cx_5='MR'),
            CX(cx_1='7561234567890', cx_4='&2.16.756.5.31&ISO', cx_5='SS'),
        ]
        pid.patient_name = XPN(xpn_1='Vogel', xpn_2='Esther', xpn_3='Rosa', xpn_5='Frau')
        pid.date_time_of_birth = '19781105'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Kirchstrasse 89', xad_3='Bern', xad_5='3001', xad_6='CH')
        pid.pid_13 = '^^PH^0318136974~^^CP^0792262217'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB', pl_2='Sprechzimmer 12', pl_4='Ambulatorium')
        pv1.pv1_7 = 'ARZ004^Mueller^Monika^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL00456')
        pv1.current_patient_balance = '20260315100000'

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
    """ Based on live/ch/ch-kisim.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KISIM')
        msh.sending_facility = HD(hd_1='KSW_WINTERTHUR')
        msh.receiving_application = HD(hd_1='PDMS')
        msh.receiving_facility = HD(hd_1='KSW_WINTERTHUR')
        msh.date_time_of_message = '20260318110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'KISIM00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260318110000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT345678', cx_4='KSW&2.16.756.5.30.1.129.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Baumann', xpn_2='Erika', xpn_3='Verena', xpn_5='Frau')
        pid.date_time_of_birth = '19520708'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Stauffacherstrasse 141', xad_3='Nidau', xad_5='2560', xad_6='CH')
        pid.pid_13 = '^^PH^0327054233~^^CP^0791556982'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GERI', pl_2='Zimmer 201', pl_3='Bett A', pl_4='Geriatrie')
        pv1.pv1_7 = 'ARZ005^Frei^Sandra^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL00789')
        pv1.current_patient_balance = '20260318110000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='KVG')
        in1.insurance_company_id = CX(cx_1='SWICA001')
        in1.insurance_company_name = XON(xon_1='SWICA Gesundheitsorganisation')
        in1.insurance_company_address = XAD(xad_1='Römerstrasse 38', xad_3='Winterthur', xad_5='8401', xad_6='CH')
        in1.insureds_id_number = CX(cx_1='756.9876.5432.10')

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
    """ Based on live/ch/ch-kisim.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KISIM')
        msh.sending_facility = HD(hd_1='USZ_ZUERICH')
        msh.receiving_application = HD(hd_1='LABSYS')
        msh.receiving_facility = HD(hd_1='USZ_ZUERICH')
        msh.date_time_of_message = '20260320083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'KISIM00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT555111', cx_4='USZ&2.16.756.5.30.1.127.3.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Eberle', xpn_2='Christian', xpn_3='Elisabeth', xpn_5='Herr')
        pid.date_time_of_birth = '19880420'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Bahnhofstrasse 67', xad_3='Horgen', xad_5='8810', xad_6='CH')
        pid.pid_13 = '^^CP^0795677000'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='Zimmer 510', pl_3='Bett A', pl_4='Innere Medizin')
        pv1.pv1_7 = 'ARZ006^Wyss^Paul^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL01234')
        pv1.current_patient_balance = '20260320083000'

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
        orc.placer_order_number = EI(ei_1='ORD789', ei_4='KISIM')
        orc.orc_7 = '^^^20260320090000^^R'
        orc.date_time_of_order_event = '20260320083000'
        orc.orc_10 = 'ARZ006^Wyss^Paul^^^Dr.^med.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD789', ei_4='KISIM')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Blutbild komplett', cwe_3='LN')
        obr.observation_date_time = '20260320083000'
        obr.specimen_action_code = 'A'
        obr.obr_16 = 'ARZ006^Wyss^Paul^^^Dr.^med.'

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
    """ Based on live/ch/ch-kisim.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABSYS')
        msh.sending_facility = HD(hd_1='USZ_ZUERICH')
        msh.receiving_application = HD(hd_1='KISIM')
        msh.receiving_facility = HD(hd_1='USZ_ZUERICH')
        msh.date_time_of_message = '20260320150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT555111', cx_4='USZ&2.16.756.5.30.1.127.3.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Eberle', xpn_2='Christian', xpn_3='Elisabeth', xpn_5='Herr')
        pid.date_time_of_birth = '19880420'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Bahnhofstrasse 67', xad_3='Horgen', xad_5='8810', xad_6='CH')
        pid.pid_13 = '^^CP^0795677000'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='Zimmer 510', pl_3='Bett A', pl_4='Innere Medizin')
        pv1.pv1_7 = 'ARZ006^Wyss^Paul^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL01234')

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
        obr.placer_order_number = EI(ei_1='ORD789', ei_4='KISIM')
        obr.filler_order_number = EI(ei_1='RES789', ei_4='LABSYS')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Blutbild komplett', cwe_3='LN')
        obr.observation_date_time = '20260320083000'
        obr.obr_16 = 'ARZ006^Wyss^Paul^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260320150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hämoglobin', cwe_3='LN')
        obx.obx_5 = '148'
        obx.units = CWE(cwe_1='g/L')
        obx.reference_range = '135-175'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukozyten', cwe_3='LN')
        obx_2.obx_5 = '7.2'
        obx_2.units = CWE(cwe_1='10*9/L')
        obx_2.reference_range = '4.0-10.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='787-2', cwe_2='Erythrozyten', cwe_3='LN')
        obx_3.obx_5 = '4.9'
        obx_3.units = CWE(cwe_1='10*12/L')
        obx_3.reference_range = '4.3-5.8'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='789-8', cwe_2='Thrombozyten', cwe_3='LN')
        obx_4.obx_5 = '245'
        obx_4.units = CWE(cwe_1='10*9/L')
        obx_4.reference_range = '150-400'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ch/ch-kisim.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABSYS')
        msh.sending_facility = HD(hd_1='USZ_ZUERICH')
        msh.receiving_application = HD(hd_1='KISIM')
        msh.receiving_facility = HD(hd_1='USZ_ZUERICH')
        msh.date_time_of_message = '20260321100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT667788', cx_4='USZ&2.16.756.5.30.1.127.3.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Gerber', xpn_2='Ottilia', xpn_3='Fritz', xpn_5='Frau')
        pid.date_time_of_birth = '19710903'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Tannenstrasse 180', xad_3='Zurich', xad_5='8001', xad_6='CH')
        pid.pid_13 = '^^CP^0783003964'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ONKO', pl_2='Zimmer 702', pl_3='Bett A', pl_4='Onkologie')
        pv1.pv1_7 = 'ARZ007^Fischer^Felix^^^Prof.^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL02345')

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
        obr.placer_order_number = EI(ei_1='ORD890', ei_4='KISIM')
        obr.filler_order_number = EI(ei_1='RES890', ei_4='LABSYS')
        obr.universal_service_identifier = CWE(cwe_1='11502-2', cwe_2='Laborbericht', cwe_3='LN')
        obr.observation_date_time = '20260321090000'
        obr.obr_16 = 'ARZ007^Fischer^Felix^^^Prof.^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260321100000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='11502-2', cwe_2='Laborbericht', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSA+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUz'
            'NSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNzQgMDAwMDAgbiAKMDAwMDAwMDE0MiAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDQgL1Jvb3QgMSAwIFIgPj4Kc3RhcnR4'
            'cmVmCjI0MwolJUVPRgo='
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ch/ch-kisim.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KISIM')
        msh.sending_facility = HD(hd_1='INSEL_BERN')
        msh.receiving_application = HD(hd_1='ARCHIV')
        msh.receiving_facility = HD(hd_1='INSEL_BERN')
        msh.date_time_of_message = '20260322140000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'KISIM00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260322140000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT998877', cx_4='INSEL&2.16.756.5.30.1.128.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Suter', xpn_2='Bruno', xpn_3='Margrit', xpn_5='Herr')
        pid.date_time_of_birth = '19451220'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kirchstrasse 26', xad_3='Baden', xad_5='5400', xad_6='CH')
        pid.pid_13 = '^^PH^0563683168'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='KARD', pl_2='Zimmer 108', pl_3='Bett B', pl_4='Kardiologie')
        pv1.pv1_7 = 'ARZ008^Widmer^Heinrich^^^Prof.^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL03456')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='AR')
        txa.document_content_presentation = 'AP'
        txa.activity_date_time = '20260322140000'
        txa.txa_5 = 'ARZ008^Widmer^Heinrich^^^Prof.^Dr.^med.'
        txa.parent_document_number = EI(ei_1='DOC456789')
        txa.document_availability_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='18842-5', cwe_2='Arztbrief', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoK'
            'PDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKEFyenRicmllZikgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAwMDAwMDAwIDY1'
            'NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA3NCAwMDAwMCBuIAowMDAwMDAwMTQyIDAwMDAwIG4gCjAwMDAwMDAyNDIgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6ZSA1'
            'IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozMzcKJSVFT0YK'
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
    """ Based on live/ch/ch-kisim.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KISIM')
        msh.sending_facility = HD(hd_1='KSW_WINTERTHUR')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='KSW_WINTERTHUR')
        msh.date_time_of_message = '20260325080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'KISIM00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20260325080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [
            CX(cx_1='PAT112233', cx_4='KSW&2.16.756.5.30.1.129.1&ISO', cx_5='MR'),
            CX(cx_1='7569876543210', cx_4='&2.16.756.5.31&ISO', cx_5='SS'),
        ]
        pid.patient_name = XPN(xpn_1='Stauffer', xpn_2='Heidi', xpn_3='Anna', xpn_5='Frau')
        pid.date_time_of_birth = '19901115'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Kornhausstrasse 197', xad_3='Winterthur', xad_5='8400', xad_6='CH')
        pid.pid_13 = '^^PH^0528047105~^^CP^0771779237~^^Internet^heidi.stauffer@bluewin.ch'

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
    """ Based on live/ch/ch-kisim.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KISIM')
        msh.sending_facility = HD(hd_1='USZ_ZUERICH')
        msh.receiving_application = HD(hd_1='TERMIN')
        msh.receiving_facility = HD(hd_1='USZ_ZUERICH')
        msh.date_time_of_message = '20260401090000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'KISIM00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APPT001', ei_4='KISIM')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine-Termin', cwe_3='HL70276')
        sch.appointment_reason = CWE(cwe_1='KONSULTATION', cwe_2='Konsultation', cwe_3='HL70277')
        sch.appointment_type = CWE(cwe_1='30')
        sch.sch_9 = 'MIN'
        sch.appointment_duration_units = CNE(cne_3='30', cne_4='20260410100000', cne_5='20260410103000')
        sch.sch_11 = 'ARZ009^Kaufmann^Elisabeth^^^Dr.^med.'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT445566', cx_4='USZ&2.16.756.5.30.1.127.3.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Bachmann', xpn_2='Peter', xpn_3='Walter', xpn_5='Herr')
        pid.date_time_of_birth = '19950622'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Junkerngasse 16', xad_3='Horgen', xad_5='8810', xad_6='CH')
        pid.pid_13 = '^^CP^0798390003'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB', pl_2='Sprechzimmer 5', pl_4='Ambulatorium')
        pv1.pv1_7 = 'ARZ009^Kaufmann^Elisabeth^^^Dr.^med.'

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
        ais.segment_action_code = 'A'
        ais.universal_service_identifier = CWE(cwe_1='KONSULTATION', cwe_2='Konsultation')
        ais.start_date_time_offset_units = CNE(cne_1='20260410100000')
        ais.duration = '30'
        ais.duration_units = CNE(cne_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.segment_action_code = 'A'
        ail.location_resource_id = PL(pl_1='AMB', pl_2='Sprechzimmer 5', pl_4='Ambulatorium')

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.segment_action_code = 'A'
        aip.aip_3 = 'ARZ009^Kaufmann^Elisabeth^^^Dr.^med.'

        # .. build the PERSONNEL_RESOURCE group ..
        personnel_resource = SiuS12PersonnelResource()
        personnel_resource.aip = aip

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service
        resources.location_resource = location_resource
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
    """ Based on live/ch/ch-kisim.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KISIM')
        msh.sending_facility = HD(hd_1='INSEL_BERN')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='INSEL_BERN')
        msh.date_time_of_message = '20260402110000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'KISIM00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT778899', cx_4='INSEL&2.16.756.5.30.1.128.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Fournier', xpn_2='Sophie', xpn_3='Pierre', xpn_5='Mme')
        pid.date_time_of_birth = '19830917'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Avenue d Ouchy 164', xad_3='Martigny', xad_5='1920', xad_6='CH')
        pid.pid_13 = '^^CP^0783484455'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ORTHO', pl_2='Zimmer 212', pl_3='Bett A', pl_4='Orthopädie')
        pv1.pv1_7 = 'ARZ010^Steiner^Niklaus^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL04567')

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
        orc.placer_order_number = EI(ei_1='ORD111', ei_4='KISIM')
        orc.orc_7 = '^^^20260402130000^^R'
        orc.date_time_of_order_event = '20260402110000'
        orc.orc_10 = 'ARZ010^Steiner^Niklaus^^^Dr.^med.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD111', ei_4='KISIM')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Thorax 2 Ebenen', cwe_3='CPT')
        obr.observation_date_time = '20260402110000'
        obr.specimen_action_code = 'A'
        obr.obr_16 = 'ARZ010^Steiner^Niklaus^^^Dr.^med.'
        obr.placer_field_2 = 'XRAY'

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
    """ Based on live/ch/ch-kisim.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MIKROBIO')
        msh.sending_facility = HD(hd_1='USZ_ZUERICH')
        msh.receiving_application = HD(hd_1='KISIM')
        msh.receiving_facility = HD(hd_1='USZ_ZUERICH')
        msh.date_time_of_message = '20260403160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MIK00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT334455', cx_4='USZ&2.16.756.5.30.1.127.3.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Huber', xpn_2='Christine', xpn_3='Fritz', xpn_5='Frau')
        pid.date_time_of_birth = '19600102'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Eichenstrasse 148', xad_3='Frauenfeld', xad_5='8500', xad_6='CH')
        pid.pid_13 = '^^PH^0522084463'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='Zimmer 310', pl_3='Bett B', pl_4='Innere Medizin')
        pv1.pv1_7 = 'ARZ006^Wyss^Paul^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL05678')

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
        obr.placer_order_number = EI(ei_1='ORD222', ei_4='KISIM')
        obr.filler_order_number = EI(ei_1='RES222', ei_4='MIKROBIO')
        obr.universal_service_identifier = CWE(cwe_1='87040', cwe_2='Blutkultur', cwe_3='LN')
        obr.observation_date_time = '20260403060000'
        obr.obr_16 = 'ARZ006^Wyss^Paul^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260403160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Bakterien identifiziert', cwe_3='LN')
        obx.obx_5 = 'Staphylococcus aureus'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18907-6', cwe_2='Methicillin-Resistenz', cwe_3='LN')
        obx_2.obx_5 = 'MSSA'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18900-1', cwe_2='Cefazolin', cwe_3='LN')
        obx_3.obx_5 = 'S'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18961-3', cwe_2='Vancomycin', cwe_3='LN')
        obx_4.obx_5 = 'S'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18964-7', cwe_2='Oxacillin', cwe_3='LN')
        obx_5.obx_5 = 'S'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ch/ch-kisim.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KISIM')
        msh.sending_facility = HD(hd_1='USZ_ZUERICH')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='USZ_ZUERICH')
        msh.date_time_of_message = '20260405120000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'KISIM00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20260405120000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [
            CX(cx_1='PAT123456', cx_4='USZ&2.16.756.5.30.1.127.3.1&ISO', cx_5='MR'),
            CX(cx_1='7560123456789', cx_4='&2.16.756.5.31&ISO', cx_5='SS'),
        ]
        pid.patient_name = XPN(xpn_1='Burgener', xpn_2='Manfred', xpn_3='Heinz', xpn_5='Herr')
        pid.date_time_of_birth = '19650312'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Gerechtigkeitsgasse 169', xad_3='Chur', xad_5='7000', xad_6='CH')
        pid.pid_13 = '^^PH^0815908760~^^CP^0763528981~^^Internet^manfred.burgener@swissonline.ch'

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
    """ Based on live/ch/ch-kisim.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KISIM')
        msh.sending_facility = HD(hd_1='USZ_ZUERICH')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='USZ_ZUERICH')
        msh.date_time_of_message = '20260406080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'KISIM00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260406080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT123456', cx_4='USZ&2.16.756.5.30.1.127.3.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Burgener', xpn_2='Manfred', xpn_3='Heinz', xpn_5='Herr')
        pid.date_time_of_birth = '19650312'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Gerechtigkeitsgasse 169', xad_3='Chur', xad_5='7000', xad_6='CH')
        pid.pid_13 = '^^PH^0815908760'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='PAT999888', cx_4='USZ&2.16.756.5.30.1.127.3.1&ISO', cx_5='MR')

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
    """ Based on live/ch/ch-kisim.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KISIM')
        msh.sending_facility = HD(hd_1='INSEL_BERN')
        msh.receiving_application = HD(hd_1='PHARMA')
        msh.receiving_facility = HD(hd_1='INSEL_BERN')
        msh.date_time_of_message = '20260407140000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'KISIM00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT667788', cx_4='INSEL&2.16.756.5.30.1.128.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Gerber', xpn_2='Ottilia', xpn_3='Fritz', xpn_5='Frau')
        pid.date_time_of_birth = '19710903'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Tannenstrasse 180', xad_3='Zurich', xad_5='8001', xad_6='CH')
        pid.pid_13 = '^^CP^0783003964'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ONKO', pl_2='Zimmer 702', pl_3='Bett A', pl_4='Onkologie')
        pv1.pv1_7 = 'ARZ007^Fischer^Felix^^^Prof.^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL02345')

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
        orc.placer_order_number = EI(ei_1='ORD333', ei_4='KISIM')
        orc.orc_7 = '^^^20260407160000^^R'
        orc.date_time_of_order_event = '20260407140000'
        orc.orc_10 = 'ARZ007^Fischer^Felix^^^Prof.^Dr.^med.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD333', ei_4='KISIM')
        obr.universal_service_identifier = CWE(cwe_1='RXE', cwe_2='Medikamentenverordnung')
        obr.observation_date_time = '20260407140000'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '^^^20260407160000^20260414160000'
        rxe.give_code = CWE(cwe_1='68079', cwe_2='Paracetamol 1000mg', cwe_3='GTIN')
        rxe.give_amount_maximum = '1000'
        rxe.give_units = CWE(cwe_1='mg')
        rxe.give_dosage_form = CWE(cwe_1='TABL', cwe_2='Tablette')
        rxe.rxe_8 = '0'
        rxe.give_per_time_unit = '1^Packung'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [rxe]

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
    """ Based on live/ch/ch-kisim.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KISIM')
        msh.sending_facility = HD(hd_1='KSW_WINTERTHUR')
        msh.receiving_application = HD(hd_1='PDMS')
        msh.receiving_facility = HD(hd_1='KSW_WINTERTHUR')
        msh.date_time_of_message = '20260408070000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A11', msg_3='ADT_A09')
        msh.message_control_id = 'KISIM00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A11'
        evn.recorded_date_time = '20260408070000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT445566', cx_4='KSW&2.16.756.5.30.1.129.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Bachmann', xpn_2='Peter', xpn_3='Walter', xpn_5='Herr')
        pid.date_time_of_birth = '19580817'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Junkerngasse 16', xad_3='Horgen', xad_5='8810', xad_6='CH')
        pid.pid_13 = '^^PH^0444321934'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='Zimmer 303', pl_3='Bett A', pl_4='Chirurgie')
        pv1.pv1_7 = 'ARZ011^Schneider^Margrit^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL06789')
        pv1.current_patient_balance = '20260408070000'

        # .. assemble the full message ..
        msg = ADT_A09()
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
    """ Based on live/ch/ch-kisim.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PATHO')
        msh.sending_facility = HD(hd_1='USZ_ZUERICH')
        msh.receiving_application = HD(hd_1='KISIM')
        msh.receiving_facility = HD(hd_1='USZ_ZUERICH')
        msh.date_time_of_message = '20260409110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'PATH00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT889900', cx_4='USZ&2.16.756.5.30.1.127.3.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Egger', xpn_2='Nicole', xpn_3='Hans', xpn_5='Frau')
        pid.date_time_of_birth = '19550930'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Tessinerplatz 116', xad_3='Solothurn', xad_5='4500', xad_6='CH')
        pid.pid_13 = '^^PH^0324243751'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='Zimmer 501', pl_3='Bett A', pl_4='Chirurgie')
        pv1.pv1_7 = 'ARZ012^Meyer^Martin^^^Prof.^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL07890')

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
        obr.placer_order_number = EI(ei_1='ORD444', ei_4='KISIM')
        obr.filler_order_number = EI(ei_1='RES444', ei_4='PATHO')
        obr.universal_service_identifier = CWE(cwe_1='88305', cwe_2='Pathologie Gewebeuntersuchung', cwe_3='CPT')
        obr.observation_date_time = '20260408140000'
        obr.obr_16 = 'ARZ012^Meyer^Martin^^^Prof.^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260409110000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='22637-3', cwe_2='Pathologiebefund', cwe_3='LN')
        obx.obx_5 = (
            'Makroskopie: Tumorexzisat linke Mamma, 3.2 x 2.1 x 1.8 cm\\.br\\Mikroskopie: Invasives duktales Karzinom, Grad 2\\.br\\Resektionsränder frei, mi'
            'nimaler Abstand 4mm\\.br\\pT1c pN0 (0/3) L0 V0 R0'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='85319-2', cwe_2='Her2/neu Score', cwe_3='LN')
        obx_2.obx_5 = '2+'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='85337-4', cwe_2='Ki-67 Proliferationsindex', cwe_3='LN')
        obx_3.obx_5 = '15'
        obx_3.units = CWE(cwe_1='%')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/ch/ch-kisim.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='INSEL_BERN')
        msh.receiving_application = HD(hd_1='KISIM')
        msh.receiving_facility = HD(hd_1='INSEL_BERN')
        msh.date_time_of_message = '20260410160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'RAD00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT778899', cx_4='INSEL&2.16.756.5.30.1.128.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Fournier', xpn_2='Sophie', xpn_3='Pierre', xpn_5='Mme')
        pid.date_time_of_birth = '19830917'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Avenue d Ouchy 164', xad_3='Martigny', xad_5='1920', xad_6='CH')
        pid.pid_13 = '^^CP^0783484455'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ORTHO', pl_2='Zimmer 212', pl_3='Bett A', pl_4='Orthopädie')
        pv1.pv1_7 = 'ARZ010^Steiner^Niklaus^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL04567')

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
        obr.placer_order_number = EI(ei_1='ORD111', ei_4='KISIM')
        obr.filler_order_number = EI(ei_1='RES111', ei_4='RIS')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Thorax 2 Ebenen', cwe_3='CPT')
        obr.observation_date_time = '20260402130000'
        obr.obr_16 = 'ARZ010^Steiner^Niklaus^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260410160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='18782-3', cwe_2='Radiologiebefund', cwe_3='LN')
        obx.obx_5 = (
            'Thorax in 2 Ebenen:\\.br\\Herz normal konfiguriert\\.br\\Lunge beidseits frei belüftet, keine Infiltrate\\.br\\Keine Pleuraergüsse\\.br\\Kein Pn'
            'eumothorax\\.br\\Beurteilung: Normalbefund'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='18782-3', cwe_2='Radiologiebefund', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='IMG')
        obx_2.obx_5 = '^image^jpeg^Base64^/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMCwsKCwsM'

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

        # .. build a non-segment wire line (embedded data continuation) ..
        raw_line = HL7RawLine('DhAQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQU')

        # .. build a non-segment wire line (embedded data continuation) ..
        raw_line_2 = HL7RawLine('FBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAACAAIDASIAAhEBAxEB/8QAHwAA')

        # .. build a non-segment wire line (embedded data continuation) ..
        raw_line_3 = HL7RawLine('AQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcI||||||F')

        # .. assemble the full message ..
        msg = ORU_R01()
        msg.msh = msh
        msg.patient_result = patient_result
        msg.extra_segments = [raw_line, raw_line_2, raw_line_3]

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
    """ Based on live/ch/ch-kisim.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABOR')
        msh.sending_facility = HD(hd_1='USZ_ZUERICH')
        msh.receiving_application = HD(hd_1='KISIM')
        msh.receiving_facility = HD(hd_1='USZ_ZUERICH')
        msh.date_time_of_message = '20260411080100'
        msh.message_type = MSG(msg_1='ACK', msg_2='A01', msg_3='ACK')
        msh.message_control_id = 'ACK00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'KISIM00001'
        msa.msa_3 = 'Nachricht erfolgreich verarbeitet'

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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
