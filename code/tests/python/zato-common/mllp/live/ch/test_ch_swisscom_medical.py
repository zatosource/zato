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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, EI, HD, MSG, PL, PT, VID, XAD, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA39Patient, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, \
    OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12Patient, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A09, ADT_A39, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIS, EVN, IN1, MRG, MSA, MSH, OBR, OBX, ORC, PID, PV1, RGS, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ch', 'ch-swisscom-medical.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ch/ch-swisscom-medical.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SRC')
        msh.sending_facility = HD(hd_1='SPITAL_BIEL')
        msh.receiving_application = HD(hd_1='SWISSCOM_MC')
        msh.receiving_facility = HD(hd_1='EHEALTH')
        msh.date_time_of_message = '20260301080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'SMC00001'
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
            CX(cx_1='PAT950001', cx_4='SPITAL_BIEL&2.16.756.5.30.1.200.1&ISO', cx_5='MR'),
            CX(cx_1='7560777888999', cx_4='&2.16.756.5.31&ISO', cx_5='SS'),
        ]
        pid.patient_name = XPN(xpn_1='Gerber', xpn_2='Daniel', xpn_3='Rosa', xpn_5='Herr')
        pid.date_time_of_birth = '19580318'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rosenbergstrasse 153', xad_3='Chur', xad_5='7000', xad_6='CH')
        pid.pid_13 = '^^PH^0817946947~^^CP^0792957793'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='Zimmer 201', pl_3='Bett A', pl_4='Innere Medizin')
        pv1.pv1_7 = 'ARZ500^Eberle^Erich^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL50001')
        pv1.current_patient_balance = '20260301080000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='KVG')
        in1.insurance_company_id = CX(cx_1='KPT001')
        in1.insurance_company_name = XON(xon_1='KPT Krankenkasse')
        in1.insurance_company_address = XAD(xad_1='Wankdorfallee 3', xad_3='Bern', xad_5='3014', xad_6='CH')
        in1.insureds_id_number = CX(cx_1='756.5555.6666.77')

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
    """ Based on live/ch/ch-swisscom-medical.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SRC')
        msh.sending_facility = HD(hd_1='SPITAL_BIEL')
        msh.receiving_application = HD(hd_1='SWISSCOM_MC')
        msh.receiving_facility = HD(hd_1='EHEALTH')
        msh.date_time_of_message = '20260310140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'SMC00002'
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
        pid.patient_identifier_list = CX(cx_1='PAT950001', cx_4='SPITAL_BIEL&2.16.756.5.30.1.200.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Gerber', xpn_2='Daniel', xpn_3='Rosa', xpn_5='Herr')
        pid.date_time_of_birth = '19580318'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rosenbergstrasse 153', xad_3='Chur', xad_5='7000', xad_6='CH')
        pid.pid_13 = '^^PH^0817946947'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='Zimmer 201', pl_3='Bett A', pl_4='Innere Medizin')
        pv1.pv1_7 = 'ARZ500^Eberle^Erich^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL50001')
        pv1.current_patient_balance = '20260310140000'

        # .. assemble the full message ..
        msg = ADT_A03()
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
    """ Based on live/ch/ch-swisscom-medical.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SRC')
        msh.sending_facility = HD(hd_1='SPITAL_BIEL')
        msh.receiving_application = HD(hd_1='SWISSCOM_MC')
        msh.receiving_facility = HD(hd_1='EHEALTH')
        msh.date_time_of_message = '20260315100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'SMC00003'
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
        pid.patient_identifier_list = CX(cx_1='PAT950002', cx_4='SPITAL_BIEL&2.16.756.5.30.1.200.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Marti', xpn_2='Nicole', xpn_3='Beat', xpn_5='Frau')
        pid.date_time_of_birth = '19820620'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Buchenstrasse 100', xad_3='Baden', xad_5='5400', xad_6='CH')
        pid.pid_13 = '^^CP^0787257719'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB', pl_2='Sprechzimmer 4', pl_4='Ambulatorium')
        pv1.pv1_7 = 'ARZ501^Schmid^Esther^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL50002')
        pv1.current_patient_balance = '20260315100000'

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
    """ Based on live/ch/ch-swisscom-medical.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SRC')
        msh.sending_facility = HD(hd_1='SPITAL_BIEL')
        msh.receiving_application = HD(hd_1='SWISSCOM_MC')
        msh.receiving_facility = HD(hd_1='EHEALTH')
        msh.date_time_of_message = '20260318110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'SMC00004'
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
        pid.patient_identifier_list = CX(cx_1='PAT950001', cx_4='SPITAL_BIEL&2.16.756.5.30.1.200.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Gerber', xpn_2='Daniel', xpn_3='Rosa', xpn_5='Herr')
        pid.date_time_of_birth = '19580318'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rosenbergstrasse 153', xad_3='Chur', xad_5='7000', xad_6='CH')
        pid.pid_13 = '^^PH^0817946947~^^CP^0792957793~^^Internet^daniel.gerber@swissonline.ch'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='N')

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
    """ Based on live/ch/ch-swisscom-medical.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SRC')
        msh.sending_facility = HD(hd_1='SPITAL_BIEL')
        msh.receiving_application = HD(hd_1='SWISSCOM_MC')
        msh.receiving_facility = HD(hd_1='EHEALTH')
        msh.date_time_of_message = '20260320083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SMC00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT950003', cx_4='SPITAL_BIEL&2.16.756.5.30.1.200.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Senn', xpn_2='Urs', xpn_3='Rosa', xpn_5='Herr')
        pid.date_time_of_birth = '19700905'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Marktgasse 12', xad_3='Basel', xad_5='4001', xad_6='CH')
        pid.pid_13 = '^^CP^0766806730'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='Zimmer 305', pl_3='Bett A', pl_4='Chirurgie')
        pv1.pv1_7 = 'ARZ502^Keller^Rita^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL50003')

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
        orc.placer_order_number = EI(ei_1='ORD950', ei_4='HIS_SRC')
        orc.orc_7 = '^^^20260320090000^^R'
        orc.date_time_of_order_event = '20260320083000'
        orc.orc_10 = 'ARZ502^Keller^Rita^^^Dr.^med.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD950', ei_4='HIS_SRC')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Blutbild komplett', cwe_3='LN')
        obr.observation_date_time = '20260320083000'
        obr.specimen_action_code = 'A'
        obr.obr_16 = 'ARZ502^Keller^Rita^^^Dr.^med.'

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
    """ Based on live/ch/ch-swisscom-medical.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SWISSCOM_MC')
        msh.sending_facility = HD(hd_1='EHEALTH')
        msh.receiving_application = HD(hd_1='HIS_DST')
        msh.receiving_facility = HD(hd_1='SPITAL_BIEL')
        msh.date_time_of_message = '20260320150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SMC00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT950003', cx_4='SPITAL_BIEL&2.16.756.5.30.1.200.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Senn', xpn_2='Urs', xpn_3='Rosa', xpn_5='Herr')
        pid.date_time_of_birth = '19700905'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Marktgasse 12', xad_3='Basel', xad_5='4001', xad_6='CH')
        pid.pid_13 = '^^CP^0766806730'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='Zimmer 305', pl_3='Bett A', pl_4='Chirurgie')
        pv1.pv1_7 = 'ARZ502^Keller^Rita^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL50003')

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
        obr.placer_order_number = EI(ei_1='ORD950', ei_4='HIS_SRC')
        obr.filler_order_number = EI(ei_1='RES950', ei_4='LABSYS')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Blutbild komplett', cwe_3='LN')
        obr.observation_date_time = '20260320083000'
        obr.obr_16 = 'ARZ502^Keller^Rita^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260320150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hämoglobin', cwe_3='LN')
        obx.obx_5 = '145'
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
        obx_2.obx_5 = '12.8'
        obx_2.units = CWE(cwe_1='10*9/L')
        obx_2.reference_range = '4.0-10.0'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='789-8', cwe_2='Thrombozyten', cwe_3='LN')
        obx_3.obx_5 = '265'
        obx_3.units = CWE(cwe_1='10*9/L')
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
        obx_4.observation_identifier = CWE(cwe_1='17861-6', cwe_2='CRP', cwe_3='LN')
        obx_4.obx_5 = '58'
        obx_4.units = CWE(cwe_1='mg/L')
        obx_4.reference_range = '0-5'
        obx_4.interpretation_codes = CWE(cwe_1='HH')
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
    """ Based on live/ch/ch-swisscom-medical.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SWISSCOM_MC')
        msh.sending_facility = HD(hd_1='EHEALTH')
        msh.receiving_application = HD(hd_1='HIS_DST')
        msh.receiving_facility = HD(hd_1='SPITAL_BIEL')
        msh.date_time_of_message = '20260321110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SMC00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT950001', cx_4='SPITAL_BIEL&2.16.756.5.30.1.200.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Gerber', xpn_2='Daniel', xpn_3='Rosa', xpn_5='Herr')
        pid.date_time_of_birth = '19580318'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rosenbergstrasse 153', xad_3='Chur', xad_5='7000', xad_6='CH')
        pid.pid_13 = '^^PH^0817946947'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='Zimmer 201', pl_3='Bett A', pl_4='Innere Medizin')
        pv1.pv1_7 = 'ARZ500^Eberle^Erich^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL50001')

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
        obr.placer_order_number = EI(ei_1='ORD951', ei_4='HIS_SRC')
        obr.filler_order_number = EI(ei_1='RES951', ei_4='LABSYS')
        obr.universal_service_identifier = CWE(cwe_1='11502-2', cwe_2='Laborbericht', cwe_3='LN')
        obr.observation_date_time = '20260321090000'
        obr.obr_16 = 'ARZ500^Eberle^Erich^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260321110000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='11502-2', cwe_2='Laborbericht', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoK'
            'PDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKExhYm9yYmVyaWNodCkgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAwMDAwMDAw'
            'IDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA3NCAwMDAwMCBuIAowMDAwMDAwMTQyIDAwMDAwIG4gCjAwMDAwMDAyNDIgMDAwMDAgbiAKdHJhaWxlcgo8PCAvU2l6'
            'ZSA1IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozMzYKJSVFT0YK'
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
    """ Based on live/ch/ch-swisscom-medical.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SWISSCOM_MC')
        msh.sending_facility = HD(hd_1='EHEALTH')
        msh.receiving_application = HD(hd_1='ARCHIV')
        msh.receiving_facility = HD(hd_1='SPITAL_BIEL')
        msh.date_time_of_message = '20260322140000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'SMC00008'
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
        pid.patient_identifier_list = CX(cx_1='PAT950002', cx_4='SPITAL_BIEL&2.16.756.5.30.1.200.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Marti', xpn_2='Nicole', xpn_3='Beat', xpn_5='Frau')
        pid.date_time_of_birth = '19820620'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Buchenstrasse 100', xad_3='Baden', xad_5='5400', xad_6='CH')
        pid.pid_13 = '^^CP^0787257719'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB', pl_2='Sprechzimmer 4', pl_4='Ambulatorium')
        pv1.pv1_7 = 'ARZ501^Schmid^Esther^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL50002')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='AR')
        txa.document_content_presentation = 'AP'
        txa.activity_date_time = '20260322140000'
        txa.txa_5 = 'ARZ501^Schmid^Esther^^^Dr.^med.'
        txa.parent_document_number = EI(ei_1='DOC500010')
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
            'IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozMzYKJSVFT0YK'
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
    """ Based on live/ch/ch-swisscom-medical.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SRC')
        msh.sending_facility = HD(hd_1='SPITAL_BIEL')
        msh.receiving_application = HD(hd_1='SWISSCOM_MC')
        msh.receiving_facility = HD(hd_1='EHEALTH')
        msh.date_time_of_message = '20260405080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'SMC00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20260405080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT950001', cx_4='SPITAL_BIEL&2.16.756.5.30.1.200.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Gerber', xpn_2='Daniel', xpn_3='Rosa', xpn_5='Herr')
        pid.date_time_of_birth = '19580318'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rosenbergstrasse 153', xad_3='Chur', xad_5='7000', xad_6='CH')
        pid.pid_13 = '^^PH^0817946947'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='PAT959999', cx_4='SPITAL_BIEL&2.16.756.5.30.1.200.1&ISO', cx_5='MR')

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
    """ Based on live/ch/ch-swisscom-medical.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SRC')
        msh.sending_facility = HD(hd_1='SPITAL_BIEL')
        msh.receiving_application = HD(hd_1='SWISSCOM_MC')
        msh.receiving_facility = HD(hd_1='EHEALTH')
        msh.date_time_of_message = '20260402110000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SMC00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT950003', cx_4='SPITAL_BIEL&2.16.756.5.30.1.200.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Senn', xpn_2='Urs', xpn_3='Rosa', xpn_5='Herr')
        pid.date_time_of_birth = '19700905'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Marktgasse 12', xad_3='Basel', xad_5='4001', xad_6='CH')
        pid.pid_13 = '^^CP^0766806730'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='Zimmer 305', pl_3='Bett A', pl_4='Chirurgie')
        pv1.pv1_7 = 'ARZ502^Keller^Rita^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL50003')

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
        orc.placer_order_number = EI(ei_1='ORD952', ei_4='HIS_SRC')
        orc.orc_7 = '^^^20260402120000^^S'
        orc.date_time_of_order_event = '20260402110000'
        orc.orc_10 = 'ARZ502^Keller^Rita^^^Dr.^med.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD952', ei_4='HIS_SRC')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Thorax 2 Ebenen', cwe_3='CPT')
        obr.observation_date_time = '20260402110000'
        obr.specimen_action_code = 'A'
        obr.obr_16 = 'ARZ502^Keller^Rita^^^Dr.^med.'
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
    """ Based on live/ch/ch-swisscom-medical.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SRC')
        msh.sending_facility = HD(hd_1='SPITAL_BIEL')
        msh.receiving_application = HD(hd_1='SWISSCOM_MC')
        msh.receiving_facility = HD(hd_1='EHEALTH')
        msh.date_time_of_message = '20260406090000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'SMC00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='TERM500', ei_4='HIS_SRC')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine-Termin', cwe_3='HL70276')
        sch.appointment_reason = CWE(cwe_1='NACHKONTROLLE', cwe_2='Nachkontrolle', cwe_3='HL70277')
        sch.appointment_type = CWE(cwe_1='20')
        sch.sch_9 = 'MIN'
        sch.appointment_duration_units = CNE(cne_3='20', cne_4='20260420140000', cne_5='20260420142000')
        sch.sch_11 = 'ARZ500^Eberle^Erich^^^Dr.^med.'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT950001', cx_4='SPITAL_BIEL&2.16.756.5.30.1.200.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Gerber', xpn_2='Daniel', xpn_3='Rosa', xpn_5='Herr')
        pid.date_time_of_birth = '19580318'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rosenbergstrasse 153', xad_3='Chur', xad_5='7000', xad_6='CH')
        pid.pid_13 = '^^PH^0817946947'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB', pl_2='Sprechzimmer 2', pl_4='Ambulatorium')
        pv1.pv1_7 = 'ARZ500^Eberle^Erich^^^Dr.^med.'

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
        ais.universal_service_identifier = CWE(cwe_1='NACHKONTROLLE', cwe_2='Nachkontrolle')
        ais.start_date_time_offset_units = CNE(cne_1='20260420140000')
        ais.duration = '20'
        ais.duration_units = CNE(cne_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service

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
    """ Based on live/ch/ch-swisscom-medical.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SRC')
        msh.sending_facility = HD(hd_1='SPITAL_BIEL')
        msh.receiving_application = HD(hd_1='SWISSCOM_MC')
        msh.receiving_facility = HD(hd_1='EHEALTH')
        msh.date_time_of_message = '20260407090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'SMC00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260407090000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT950003', cx_4='SPITAL_BIEL&2.16.756.5.30.1.200.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Senn', xpn_2='Urs', xpn_3='Rosa', xpn_5='Herr')
        pid.date_time_of_birth = '19700905'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Marktgasse 12', xad_3='Basel', xad_5='4001', xad_6='CH')
        pid.pid_13 = '^^CP^0766806730'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='Zimmer 210', pl_3='Bett A', pl_4='Innere Medizin')
        pv1.pv1_7 = 'ARZ500^Eberle^Erich^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL50003')
        pv1.account_status = CWE(cwe_1='CHIR', cwe_2='Zimmer 305', cwe_3='Bett A', cwe_4='Chirurgie')
        pv1.prior_temporary_location = PL(pl_1='20260407090000')

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
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
    """ Based on live/ch/ch-swisscom-medical.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SWISSCOM_MC')
        msh.sending_facility = HD(hd_1='EHEALTH')
        msh.receiving_application = HD(hd_1='HIS_DST')
        msh.receiving_facility = HD(hd_1='SPITAL_BIEL')
        msh.date_time_of_message = '20260408150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SMC00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT950001', cx_4='SPITAL_BIEL&2.16.756.5.30.1.200.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Gerber', xpn_2='Daniel', xpn_3='Rosa', xpn_5='Herr')
        pid.date_time_of_birth = '19580318'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rosenbergstrasse 153', xad_3='Chur', xad_5='7000', xad_6='CH')
        pid.pid_13 = '^^PH^0817946947'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='Zimmer 201', pl_3='Bett A', pl_4='Innere Medizin')
        pv1.pv1_7 = 'ARZ500^Eberle^Erich^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL50001')

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
        obr.placer_order_number = EI(ei_1='ORD953', ei_4='HIS_SRC')
        obr.filler_order_number = EI(ei_1='RES953', ei_4='LABSYS')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Leberprofil', cwe_3='LN')
        obr.observation_date_time = '20260408090000'
        obr.obr_16 = 'ARZ500^Eberle^Erich^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260408150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALAT (GPT)', cwe_3='LN')
        obx.obx_5 = '28'
        obx.units = CWE(cwe_1='U/L')
        obx.reference_range = '7-56'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1920-8', cwe_2='ASAT (GOT)', cwe_3='LN')
        obx_2.obx_5 = '22'
        obx_2.units = CWE(cwe_1='U/L')
        obx_2.reference_range = '10-40'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6768-6', cwe_2='Alkalische Phosphatase', cwe_3='LN')
        obx_3.obx_5 = '85'
        obx_3.units = CWE(cwe_1='U/L')
        obx_3.reference_range = '44-147'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1975-2', cwe_2='Gesamtbilirubin', cwe_3='LN')
        obx_4.obx_5 = '15'
        obx_4.units = CWE(cwe_1='umol/L')
        obx_4.reference_range = '3-22'
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
    """ Based on live/ch/ch-swisscom-medical.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SRC')
        msh.sending_facility = HD(hd_1='SPITAL_BIEL')
        msh.receiving_application = HD(hd_1='SWISSCOM_MC')
        msh.receiving_facility = HD(hd_1='EHEALTH')
        msh.date_time_of_message = '20260409120000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'SMC00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20260409120000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [
            CX(cx_1='PAT950002', cx_4='SPITAL_BIEL&2.16.756.5.30.1.200.1&ISO', cx_5='MR'),
            CX(cx_1='7560888999000', cx_4='&2.16.756.5.31&ISO', cx_5='SS'),
        ]
        pid.patient_name = XPN(xpn_1='Marti', xpn_2='Nicole', xpn_3='Beat', xpn_5='Frau')
        pid.date_time_of_birth = '19820620'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Buchenstrasse 100', xad_3='Baden', xad_5='5400', xad_6='CH')
        pid.pid_13 = '^^CP^0787257719~^^Internet^nicole.marti@bluewin.ch'

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
    """ Based on live/ch/ch-swisscom-medical.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SRC')
        msh.sending_facility = HD(hd_1='SPITAL_BIEL')
        msh.receiving_application = HD(hd_1='SWISSCOM_MC')
        msh.receiving_facility = HD(hd_1='EHEALTH')
        msh.date_time_of_message = '20260410070000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A11', msg_3='ADT_A09')
        msh.message_control_id = 'SMC00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A11'
        evn.recorded_date_time = '20260410070000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT950004', cx_4='SPITAL_BIEL&2.16.756.5.30.1.200.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Mueller', xpn_2='Reto', xpn_3='Verena', xpn_5='Herr')
        pid.date_time_of_birth = '19750420'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Universitaetstrasse 38', xad_3='St. Gallen', xad_5='9000', xad_6='CH')
        pid.pid_13 = '^^CP^0766296603'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='Zimmer 202', pl_3='Bett A', pl_4='Chirurgie')
        pv1.pv1_7 = 'ARZ502^Keller^Rita^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL50004')
        pv1.current_patient_balance = '20260410070000'

        # .. assemble the full message ..
        msg = ADT_A09()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/ch/ch-swisscom-medical.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SWISSCOM_MC')
        msh.sending_facility = HD(hd_1='EHEALTH')
        msh.receiving_application = HD(hd_1='HIS_DST')
        msh.receiving_facility = HD(hd_1='SPITAL_BIEL')
        msh.date_time_of_message = '20260411160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SMC00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT950003', cx_4='SPITAL_BIEL&2.16.756.5.30.1.200.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Senn', xpn_2='Urs', xpn_3='Rosa', xpn_5='Herr')
        pid.date_time_of_birth = '19700905'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Marktgasse 12', xad_3='Basel', xad_5='4001', xad_6='CH')
        pid.pid_13 = '^^CP^0766806730'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='Zimmer 210', pl_3='Bett A', pl_4='Innere Medizin')
        pv1.pv1_7 = 'ARZ500^Eberle^Erich^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL50003')

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
        obr.placer_order_number = EI(ei_1='ORD954', ei_4='HIS_SRC')
        obr.filler_order_number = EI(ei_1='RES954', ei_4='LABSYS')
        obr.universal_service_identifier = CWE(cwe_1='87186', cwe_2='Antibiogramm', cwe_3='LN')
        obr.observation_date_time = '20260411060000'
        obr.obr_16 = 'ARZ500^Eberle^Erich^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260411160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Bakterien identifiziert', cwe_3='LN')
        obx.obx_5 = 'Enterococcus faecalis'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18862-3', cwe_2='Amoxicillin', cwe_3='LN')
        obx_2.obx_5 = 'S'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18961-3', cwe_2='Vancomycin', cwe_3='LN')
        obx_3.obx_5 = 'S'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18928-2', cwe_2='Gentamicin', cwe_3='LN')
        obx_4.obx_5 = 'R'
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
    """ Based on live/ch/ch-swisscom-medical.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SRC')
        msh.sending_facility = HD(hd_1='SPITAL_BIEL')
        msh.receiving_application = HD(hd_1='SWISSCOM_MC')
        msh.receiving_facility = HD(hd_1='EHEALTH')
        msh.date_time_of_message = '20260412080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'SMC00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20260412080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [
            CX(cx_1='PAT950005', cx_4='SPITAL_BIEL&2.16.756.5.30.1.200.1&ISO', cx_5='MR'),
            CX(cx_1='7568901234567', cx_4='&2.16.756.5.31&ISO', cx_5='SS'),
        ]
        pid.patient_name = XPN(xpn_1='Schneider', xpn_2='Ruth', xpn_3='Fritz', xpn_5='Frau')
        pid.date_time_of_birth = '19931115'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Seefeldstrasse 34', xad_3='Olten', xad_5='4600', xad_6='CH')
        pid.pid_13 = '^^CP^0783218614~^^Internet^ruth.schneider@gmail.com'

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
    """ Based on live/ch/ch-swisscom-medical.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SWISSCOM_MC')
        msh.sending_facility = HD(hd_1='EHEALTH')
        msh.receiving_application = HD(hd_1='HIS_DST')
        msh.receiving_facility = HD(hd_1='SPITAL_BIEL')
        msh.date_time_of_message = '20260413110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SMC00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT950002', cx_4='SPITAL_BIEL&2.16.756.5.30.1.200.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Marti', xpn_2='Nicole', xpn_3='Beat', xpn_5='Frau')
        pid.date_time_of_birth = '19820620'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Buchenstrasse 100', xad_3='Baden', xad_5='5400', xad_6='CH')
        pid.pid_13 = '^^CP^0787257719'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB', pl_2='Sprechzimmer 4', pl_4='Ambulatorium')
        pv1.pv1_7 = 'ARZ501^Schmid^Esther^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL50002')

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
        obr.placer_order_number = EI(ei_1='ORD955', ei_4='HIS_SRC')
        obr.filler_order_number = EI(ei_1='RES955', ei_4='PATHO')
        obr.universal_service_identifier = CWE(cwe_1='88305', cwe_2='Histologie', cwe_3='CPT')
        obr.observation_date_time = '20260412140000'
        obr.obr_16 = 'ARZ501^Schmid^Esther^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260413110000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='22637-3', cwe_2='Pathologiebefund', cwe_3='LN')
        obx.obx_5 = (
            'Makroskopie: Zervixbiopsie, 0.5 x 0.4 x 0.3 cm\\.br\\Mikroskopie: Chronische Zervizitis, keine Dysplasie\\.br\\HPV-Zytologie: Negativ\\.br\\Beur'
            'teilung: Benigner Befund'
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
    """ Based on live/ch/ch-swisscom-medical.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SWISSCOM_MC')
        msh.sending_facility = HD(hd_1='EHEALTH')
        msh.receiving_application = HD(hd_1='HIS_DST')
        msh.receiving_facility = HD(hd_1='SPITAL_BIEL')
        msh.date_time_of_message = '20260414150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SMC00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT950001', cx_4='SPITAL_BIEL&2.16.756.5.30.1.200.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Gerber', xpn_2='Daniel', xpn_3='Rosa', xpn_5='Herr')
        pid.date_time_of_birth = '19580318'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rosenbergstrasse 153', xad_3='Chur', xad_5='7000', xad_6='CH')
        pid.pid_13 = '^^PH^0817946947'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='Zimmer 201', pl_3='Bett A', pl_4='Innere Medizin')
        pv1.pv1_7 = 'ARZ500^Eberle^Erich^^^Dr.^med.'
        pv1.visit_number = CX(cx_1='FALL50001')

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
        obr.placer_order_number = EI(ei_1='ORD956', ei_4='HIS_SRC')
        obr.filler_order_number = EI(ei_1='RES956', ei_4='LABSYS')
        obr.universal_service_identifier = CWE(cwe_1='COAG', cwe_2='Gerinnungsprofil', cwe_3='LN')
        obr.observation_date_time = '20260414090000'
        obr.obr_16 = 'ARZ500^Eberle^Erich^^^Dr.^med.'
        obr.results_rpt_status_chng_date_time = '20260414150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='Prothrombinzeit (Quick)', cwe_3='LN')
        obx.obx_5 = '92'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '70-120'
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
        obx_2.obx_5 = '1.0'
        obx_2.reference_range = '0.8-1.2'
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
        obx_3.obx_5 = '28'
        obx_3.units = CWE(cwe_1='s')
        obx_3.reference_range = '25-37'
        obx_3.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/ch/ch-swisscom-medical.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SWISSCOM_MC')
        msh.sending_facility = HD(hd_1='EHEALTH')
        msh.receiving_application = HD(hd_1='HIS_SRC')
        msh.receiving_facility = HD(hd_1='SPITAL_BIEL')
        msh.date_time_of_message = '20260415080100'
        msh.message_type = MSG(msg_1='ACK', msg_2='A01', msg_3='ACK')
        msh.message_control_id = 'ACK50001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'SMC00001'
        msa.msa_3 = 'Nachricht erfolgreich übermittelt'

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
