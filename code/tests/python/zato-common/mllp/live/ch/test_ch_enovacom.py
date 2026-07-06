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

_md_path = md_path_for('ch', 'ch-enovacom.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ch/ch-enovacom.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SRC')
        msh.sending_facility = HD(hd_1='HOPITAL_SION')
        msh.receiving_application = HD(hd_1='ENOVACOM')
        msh.receiving_facility = HD(hd_1='INTEGRATION')
        msh.date_time_of_message = '20260301080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'ENOV00001'
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
            CX(cx_1='PAT900001', cx_4='HOPITAL_SION&2.16.756.5.30.1.190.1&ISO', cx_5='MR'),
            CX(cx_1='7560666777888', cx_4='&2.16.756.5.31&ISO', cx_5='SS'),
        ]
        pid.patient_name = XPN(xpn_1='Gautier', xpn_2='Claude', xpn_3='Yvonne', xpn_5='M.')
        pid.date_time_of_birth = '19650812'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Place Saint-Francois 168', xad_3='Bulle', xad_5='1630', xad_6='CH')
        pid.pid_13 = '^^PH^0262460819~^^CP^0794670523'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MEDINTERNE', pl_2='Chambre 201', pl_3='Lit A', pl_4='Médecine interne')
        pv1.pv1_7 = 'MED500^Dubois^Denise^^^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS50001')
        pv1.current_patient_balance = '20260301080000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='LAMal')
        in1.insurance_company_id = CX(cx_1='GROUPE_MUTUEL001')
        in1.insurance_company_name = XON(xon_1='Groupe Mutuel')
        in1.insurance_company_address = XAD(xad_1='Rue du Nord 5', xad_3='Martigny', xad_5='1920', xad_6='CH')
        in1.insureds_id_number = CX(cx_1='756.4444.5555.66')

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
    """ Based on live/ch/ch-enovacom.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SRC')
        msh.sending_facility = HD(hd_1='HOPITAL_SION')
        msh.receiving_application = HD(hd_1='ENOVACOM')
        msh.receiving_facility = HD(hd_1='INTEGRATION')
        msh.date_time_of_message = '20260310140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'ENOV00002'
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
        pid.patient_identifier_list = CX(cx_1='PAT900001', cx_4='HOPITAL_SION&2.16.756.5.30.1.190.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Gautier', xpn_2='Claude', xpn_3='Yvonne', xpn_5='M.')
        pid.date_time_of_birth = '19650812'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Place Saint-Francois 168', xad_3='Bulle', xad_5='1630', xad_6='CH')
        pid.pid_13 = '^^PH^0262460819'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MEDINTERNE', pl_2='Chambre 201', pl_3='Lit A', pl_4='Médecine interne')
        pv1.pv1_7 = 'MED500^Dubois^Denise^^^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS50001')
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
    """ Based on live/ch/ch-enovacom.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SRC')
        msh.sending_facility = HD(hd_1='HOPITAL_SION')
        msh.receiving_application = HD(hd_1='ENOVACOM')
        msh.receiving_facility = HD(hd_1='INTEGRATION')
        msh.date_time_of_message = '20260315100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'ENOV00003'
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
        pid.patient_identifier_list = CX(cx_1='PAT900002', cx_4='HOPITAL_SION&2.16.756.5.30.1.190.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Boyer', xpn_2='Nathalie', xpn_3='Claude', xpn_5='Mme')
        pid.date_time_of_birth = '19780330'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Boulevard Helvetique 196', xad_3='Renens', xad_5='1020', xad_6='CH')
        pid.pid_13 = '^^CP^0796771784'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSULT', pl_2='Salle 5', pl_4='Consultation')
        pv1.pv1_7 = 'MED501^Guerin^Brigitte^^^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS50002')
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
    """ Based on live/ch/ch-enovacom.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SRC')
        msh.sending_facility = HD(hd_1='HOPITAL_SION')
        msh.receiving_application = HD(hd_1='ENOVACOM')
        msh.receiving_facility = HD(hd_1='INTEGRATION')
        msh.date_time_of_message = '20260318110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'ENOV00004'
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
        pid.patient_identifier_list = CX(cx_1='PAT900001', cx_4='HOPITAL_SION&2.16.756.5.30.1.190.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Gautier', xpn_2='Claude', xpn_3='Yvonne', xpn_5='M.')
        pid.date_time_of_birth = '19650812'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Place Saint-Francois 168', xad_3='Bulle', xad_5='1630', xad_6='CH')
        pid.pid_13 = '^^PH^0262460819~^^CP^0794670523~^^Internet^claude.gautier@gmail.com'

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
    """ Based on live/ch/ch-enovacom.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SRC')
        msh.sending_facility = HD(hd_1='HOPITAL_SION')
        msh.receiving_application = HD(hd_1='ENOVACOM')
        msh.receiving_facility = HD(hd_1='INTEGRATION')
        msh.date_time_of_message = '20260320083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'ENOV00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT900003', cx_4='HOPITAL_SION&2.16.756.5.30.1.190.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Garnier', xpn_2='Vincent', xpn_3='Paul', xpn_5='M.')
        pid.date_time_of_birth = '19550620'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rue Neuve 149', xad_3='Morges', xad_5='1110', xad_6='CH')
        pid.pid_13 = '^^CP^0788284820'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIRURGIE', pl_2='Chambre 305', pl_3='Lit A', pl_4='Chirurgie')
        pv1.pv1_7 = 'MED502^Petit^Sylvie^^^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS50003')

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
        orc.placer_order_number = EI(ei_1='ORD900', ei_4='HIS_SRC')
        orc.orc_7 = '^^^20260320090000^^R'
        orc.date_time_of_order_event = '20260320083000'
        orc.orc_10 = 'MED502^Petit^Sylvie^^^Dr.^méd.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD900', ei_4='HIS_SRC')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Formule sanguine complète', cwe_3='LN')
        obr.observation_date_time = '20260320083000'
        obr.specimen_action_code = 'A'
        obr.obr_16 = 'MED502^Petit^Sylvie^^^Dr.^méd.'

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
    """ Based on live/ch/ch-enovacom.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENOVACOM')
        msh.sending_facility = HD(hd_1='INTEGRATION')
        msh.receiving_application = HD(hd_1='HIS_DST')
        msh.receiving_facility = HD(hd_1='HOPITAL_SION')
        msh.date_time_of_message = '20260320150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ENOV00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT900003', cx_4='HOPITAL_SION&2.16.756.5.30.1.190.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Garnier', xpn_2='Vincent', xpn_3='Paul', xpn_5='M.')
        pid.date_time_of_birth = '19550620'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rue Neuve 149', xad_3='Morges', xad_5='1110', xad_6='CH')
        pid.pid_13 = '^^CP^0788284820'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIRURGIE', pl_2='Chambre 305', pl_3='Lit A', pl_4='Chirurgie')
        pv1.pv1_7 = 'MED502^Petit^Sylvie^^^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS50003')

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
        obr.placer_order_number = EI(ei_1='ORD900', ei_4='HIS_SRC')
        obr.filler_order_number = EI(ei_1='RES900', ei_4='LABSYS')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Formule sanguine complète', cwe_3='LN')
        obr.observation_date_time = '20260320083000'
        obr.obr_16 = 'MED502^Petit^Sylvie^^^Dr.^méd.'
        obr.results_rpt_status_chng_date_time = '20260320150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hémoglobine', cwe_3='LN')
        obx.obx_5 = '128'
        obx.units = CWE(cwe_1='g/L')
        obx.reference_range = '135-175'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leucocytes', cwe_3='LN')
        obx_2.obx_5 = '9.5'
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
        obx_3.observation_identifier = CWE(cwe_1='789-8', cwe_2='Thrombocytes', cwe_3='LN')
        obx_3.obx_5 = '195'
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
        obx_4.obx_5 = '32'
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
    """ Based on live/ch/ch-enovacom.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENOVACOM')
        msh.sending_facility = HD(hd_1='INTEGRATION')
        msh.receiving_application = HD(hd_1='HIS_DST')
        msh.receiving_facility = HD(hd_1='HOPITAL_SION')
        msh.date_time_of_message = '20260321110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ENOV00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT900001', cx_4='HOPITAL_SION&2.16.756.5.30.1.190.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Gautier', xpn_2='Claude', xpn_3='Yvonne', xpn_5='M.')
        pid.date_time_of_birth = '19650812'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Place Saint-Francois 168', xad_3='Bulle', xad_5='1630', xad_6='CH')
        pid.pid_13 = '^^PH^0262460819'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MEDINTERNE', pl_2='Chambre 201', pl_3='Lit A', pl_4='Médecine interne')
        pv1.pv1_7 = 'MED500^Dubois^Denise^^^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS50001')

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
        obr.placer_order_number = EI(ei_1='ORD901', ei_4='HIS_SRC')
        obr.filler_order_number = EI(ei_1='RES901', ei_4='LABSYS')
        obr.universal_service_identifier = CWE(cwe_1='11502-2', cwe_2='Rapport de laboratoire', cwe_3='LN')
        obr.observation_date_time = '20260321090000'
        obr.obr_16 = 'MED500^Dubois^Denise^^^Dr.^méd.'
        obr.results_rpt_status_chng_date_time = '20260321110000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='11502-2', cwe_2='Rapport de laboratoire', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoK'
            'PDwgL0xlbmd0aCA1OCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKFJhcHBvcnQgZGUgbGFib3JhdG9pcmUpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDUK'
            'MDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNzQgMDAwMDAgbiAKMDAwMDAwMDE0MiAwMDAwMCBuIAowMDAwMDAwMjQyIDAwMDAwIG4gCnRyYWls'
            'ZXIKPDwgL1NpemUgNSAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKMzUwCiUlRU9GCg=='
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
    """ Based on live/ch/ch-enovacom.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENOVACOM')
        msh.sending_facility = HD(hd_1='INTEGRATION')
        msh.receiving_application = HD(hd_1='ARCHIV')
        msh.receiving_facility = HD(hd_1='HOPITAL_SION')
        msh.date_time_of_message = '20260322140000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'ENOV00008'
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
        pid.patient_identifier_list = CX(cx_1='PAT900002', cx_4='HOPITAL_SION&2.16.756.5.30.1.190.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Boyer', xpn_2='Nathalie', xpn_3='Claude', xpn_5='Mme')
        pid.date_time_of_birth = '19780330'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Boulevard Helvetique 196', xad_3='Renens', xad_5='1020', xad_6='CH')
        pid.pid_13 = '^^CP^0796771784'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSULT', pl_2='Salle 5', pl_4='Consultation')
        pv1.pv1_7 = 'MED501^Guerin^Brigitte^^^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS50002')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS')
        txa.document_content_presentation = 'AP'
        txa.activity_date_time = '20260322140000'
        txa.txa_5 = 'MED501^Guerin^Brigitte^^^Dr.^méd.'
        txa.parent_document_number = EI(ei_1='DOC500001')
        txa.document_availability_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='11490-0', cwe_2='Lettre de sortie', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoK'
            'PDwgL0xlbmd0aCA0NiA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKExldHRyZSBkZSBzb3J0aWUpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDUKMDAwMDAw'
            'MDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNzQgMDAwMDAgbiAKMDAwMDAwMDE0MiAwMDAwMCBuIAowMDAwMDAwMjQyIDAwMDAwIG4gCnRyYWlsZXIKPDwg'
            'L1NpemUgNSAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKMzM4CiUlRU9GCg=='
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
    """ Based on live/ch/ch-enovacom.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SRC')
        msh.sending_facility = HD(hd_1='HOPITAL_SION')
        msh.receiving_application = HD(hd_1='ENOVACOM')
        msh.receiving_facility = HD(hd_1='INTEGRATION')
        msh.date_time_of_message = '20260402110000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'ENOV00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT900003', cx_4='HOPITAL_SION&2.16.756.5.30.1.190.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Garnier', xpn_2='Vincent', xpn_3='Paul', xpn_5='M.')
        pid.date_time_of_birth = '19550620'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rue Neuve 149', xad_3='Morges', xad_5='1110', xad_6='CH')
        pid.pid_13 = '^^CP^0788284820'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIRURGIE', pl_2='Chambre 305', pl_3='Lit A', pl_4='Chirurgie')
        pv1.pv1_7 = 'MED502^Petit^Sylvie^^^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS50003')

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
        orc.placer_order_number = EI(ei_1='ORD902', ei_4='HIS_SRC')
        orc.orc_7 = '^^^20260402120000^^S'
        orc.date_time_of_order_event = '20260402110000'
        orc.orc_10 = 'MED502^Petit^Sylvie^^^Dr.^méd.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD902', ei_4='HIS_SRC')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Thorax 2 incidences', cwe_3='CPT')
        obr.observation_date_time = '20260402110000'
        obr.specimen_action_code = 'A'
        obr.obr_16 = 'MED502^Petit^Sylvie^^^Dr.^méd.'
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
    """ Based on live/ch/ch-enovacom.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SRC')
        msh.sending_facility = HD(hd_1='HOPITAL_SION')
        msh.receiving_application = HD(hd_1='ENOVACOM')
        msh.receiving_facility = HD(hd_1='INTEGRATION')
        msh.date_time_of_message = '20260405080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'ENOV00010'
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
        pid.patient_identifier_list = CX(cx_1='PAT900001', cx_4='HOPITAL_SION&2.16.756.5.30.1.190.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Gautier', xpn_2='Claude', xpn_3='Yvonne', xpn_5='M.')
        pid.date_time_of_birth = '19650812'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Place Saint-Francois 168', xad_3='Bulle', xad_5='1630', xad_6='CH')
        pid.pid_13 = '^^PH^0262460819'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='PAT999888', cx_4='HOPITAL_SION&2.16.756.5.30.1.190.1&ISO', cx_5='MR')

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
    """ Based on live/ch/ch-enovacom.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SRC')
        msh.sending_facility = HD(hd_1='HOPITAL_SION')
        msh.receiving_application = HD(hd_1='ENOVACOM')
        msh.receiving_facility = HD(hd_1='INTEGRATION')
        msh.date_time_of_message = '20260406090000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'ENOV00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='RDV500', ei_4='HIS_SRC')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine', cwe_3='HL70276')
        sch.appointment_reason = CWE(cwe_1='CONSULT', cwe_2='Consultation', cwe_3='HL70277')
        sch.appointment_type = CWE(cwe_1='30')
        sch.sch_9 = 'MIN'
        sch.appointment_duration_units = CNE(cne_3='30', cne_4='20260420100000', cne_5='20260420103000')
        sch.sch_11 = 'MED501^Guerin^Brigitte^^^Dr.^méd.'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT900002', cx_4='HOPITAL_SION&2.16.756.5.30.1.190.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Boyer', xpn_2='Nathalie', xpn_3='Claude', xpn_5='Mme')
        pid.date_time_of_birth = '19780330'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Boulevard Helvetique 196', xad_3='Renens', xad_5='1020', xad_6='CH')
        pid.pid_13 = '^^CP^0796771784'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSULT', pl_2='Salle 5', pl_4='Consultation')
        pv1.pv1_7 = 'MED501^Guerin^Brigitte^^^Dr.^méd.'

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
        ais.universal_service_identifier = CWE(cwe_1='CONSULT', cwe_2='Consultation')
        ais.start_date_time_offset_units = CNE(cne_1='20260420100000')
        ais.duration = '30'
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
    """ Based on live/ch/ch-enovacom.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SRC')
        msh.sending_facility = HD(hd_1='HOPITAL_SION')
        msh.receiving_application = HD(hd_1='ENOVACOM')
        msh.receiving_facility = HD(hd_1='INTEGRATION')
        msh.date_time_of_message = '20260407090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'ENOV00012'
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
        pid.patient_identifier_list = CX(cx_1='PAT900003', cx_4='HOPITAL_SION&2.16.756.5.30.1.190.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Garnier', xpn_2='Vincent', xpn_3='Paul', xpn_5='M.')
        pid.date_time_of_birth = '19550620'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rue Neuve 149', xad_3='Morges', xad_5='1110', xad_6='CH')
        pid.pid_13 = '^^CP^0788284820'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='READAPT', pl_2='Chambre 101', pl_3='Lit A', pl_4='Réadaptation')
        pv1.pv1_7 = 'MED503^Morin^Henri^^^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS50003')
        pv1.account_status = CWE(cwe_1='CHIRURGIE', cwe_2='Chambre 305', cwe_3='Lit A', cwe_4='Chirurgie')
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
    """ Based on live/ch/ch-enovacom.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENOVACOM')
        msh.sending_facility = HD(hd_1='INTEGRATION')
        msh.receiving_application = HD(hd_1='HIS_DST')
        msh.receiving_facility = HD(hd_1='HOPITAL_SION')
        msh.date_time_of_message = '20260408150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ENOV00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT900001', cx_4='HOPITAL_SION&2.16.756.5.30.1.190.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Gautier', xpn_2='Claude', xpn_3='Yvonne', xpn_5='M.')
        pid.date_time_of_birth = '19650812'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Place Saint-Francois 168', xad_3='Bulle', xad_5='1630', xad_6='CH')
        pid.pid_13 = '^^PH^0262460819'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MEDINTERNE', pl_2='Chambre 201', pl_3='Lit A', pl_4='Médecine interne')
        pv1.pv1_7 = 'MED500^Dubois^Denise^^^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS50001')

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
        obr.placer_order_number = EI(ei_1='ORD903', ei_4='HIS_SRC')
        obr.filler_order_number = EI(ei_1='RES903', ei_4='LABSYS')
        obr.universal_service_identifier = CWE(cwe_1='2160-0', cwe_2='Profil rénal', cwe_3='LN')
        obr.observation_date_time = '20260408090000'
        obr.obr_16 = 'MED500^Dubois^Denise^^^Dr.^méd.'
        obr.results_rpt_status_chng_date_time = '20260408150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Créatinine', cwe_3='LN')
        obx.obx_5 = '95'
        obx.units = CWE(cwe_1='umol/L')
        obx.reference_range = '62-106'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urée', cwe_3='LN')
        obx_2.obx_5 = '6.2'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '2.8-7.2'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium', cwe_3='LN')
        obx_3.obx_5 = '4.1'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '3.5-5.1'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodium', cwe_3='LN')
        obx_4.obx_5 = '138'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '136-145'
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
    """ Based on live/ch/ch-enovacom.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SRC')
        msh.sending_facility = HD(hd_1='HOPITAL_SION')
        msh.receiving_application = HD(hd_1='ENOVACOM')
        msh.receiving_facility = HD(hd_1='INTEGRATION')
        msh.date_time_of_message = '20260409120000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'ENOV00014'
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
            CX(cx_1='PAT900001', cx_4='HOPITAL_SION&2.16.756.5.30.1.190.1&ISO', cx_5='MR'),
            CX(cx_1='7560666777888', cx_4='&2.16.756.5.31&ISO', cx_5='SS'),
        ]
        pid.patient_name = XPN(xpn_1='Gautier', xpn_2='Claude', xpn_3='Yvonne', xpn_5='M.')
        pid.date_time_of_birth = '19650812'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Place Saint-Francois 168', xad_3='Bulle', xad_5='1630', xad_6='CH')
        pid.pid_13 = '^^PH^0262460819~^^CP^0794670523~^^Internet^claude.gautier@gmail.com'

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
    """ Based on live/ch/ch-enovacom.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SRC')
        msh.sending_facility = HD(hd_1='HOPITAL_SION')
        msh.receiving_application = HD(hd_1='ENOVACOM')
        msh.receiving_facility = HD(hd_1='INTEGRATION')
        msh.date_time_of_message = '20260410070000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A11', msg_3='ADT_A09')
        msh.message_control_id = 'ENOV00015'
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
        pid.patient_identifier_list = CX(cx_1='PAT900004', cx_4='HOPITAL_SION&2.16.756.5.30.1.190.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Legrand', xpn_2='Yves', xpn_3='Sophie', xpn_5='M.')
        pid.date_time_of_birth = '19820915'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Chemin des Vignes 140', xad_3='Yverdon-les-Bains', xad_5='1400', xad_6='CH')
        pid.pid_13 = '^^CP^0778752399'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIRURGIE', pl_2='Chambre 201', pl_3='Lit A', pl_4='Chirurgie')
        pv1.pv1_7 = 'MED502^Petit^Sylvie^^^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS50004')
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
    """ Based on live/ch/ch-enovacom.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENOVACOM')
        msh.sending_facility = HD(hd_1='INTEGRATION')
        msh.receiving_application = HD(hd_1='HIS_DST')
        msh.receiving_facility = HD(hd_1='HOPITAL_SION')
        msh.date_time_of_message = '20260411160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ENOV00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT900003', cx_4='HOPITAL_SION&2.16.756.5.30.1.190.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Garnier', xpn_2='Vincent', xpn_3='Paul', xpn_5='M.')
        pid.date_time_of_birth = '19550620'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rue Neuve 149', xad_3='Morges', xad_5='1110', xad_6='CH')
        pid.pid_13 = '^^CP^0788284820'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='READAPT', pl_2='Chambre 101', pl_3='Lit A', pl_4='Réadaptation')
        pv1.pv1_7 = 'MED503^Morin^Henri^^^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS50003')

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
        obr.placer_order_number = EI(ei_1='ORD904', ei_4='HIS_SRC')
        obr.filler_order_number = EI(ei_1='RES904', ei_4='LABSYS')
        obr.universal_service_identifier = CWE(cwe_1='87040', cwe_2='Hémoculture', cwe_3='LN')
        obr.observation_date_time = '20260411060000'
        obr.obr_16 = 'MED503^Morin^Henri^^^Dr.^méd.'
        obr.results_rpt_status_chng_date_time = '20260411160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Micro-organisme identifié', cwe_3='LN')
        obx.obx_5 = 'Pas de croissance après 5 jours'
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
    """ Based on live/ch/ch-enovacom.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS_SRC')
        msh.sending_facility = HD(hd_1='HOPITAL_SION')
        msh.receiving_application = HD(hd_1='ENOVACOM')
        msh.receiving_facility = HD(hd_1='INTEGRATION')
        msh.date_time_of_message = '20260412080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'ENOV00017'
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
            CX(cx_1='PAT900005', cx_4='HOPITAL_SION&2.16.756.5.30.1.190.1&ISO', cx_5='MR'),
            CX(cx_1='7567890123456', cx_4='&2.16.756.5.31&ISO', cx_5='SS'),
        ]
        pid.patient_name = XPN(xpn_1='Duval', xpn_2='Laure', xpn_3='Sophie', xpn_5='Mme')
        pid.date_time_of_birth = '19901205'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Avenue du Leman 106', xad_3='Renens', xad_5='1020', xad_6='CH')
        pid.pid_13 = '^^CP^0784535774~^^Internet^laure.duval@gmail.com'

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
    """ Based on live/ch/ch-enovacom.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENOVACOM')
        msh.sending_facility = HD(hd_1='INTEGRATION')
        msh.receiving_application = HD(hd_1='HIS_DST')
        msh.receiving_facility = HD(hd_1='HOPITAL_SION')
        msh.date_time_of_message = '20260413110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ENOV00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT900002', cx_4='HOPITAL_SION&2.16.756.5.30.1.190.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Boyer', xpn_2='Nathalie', xpn_3='Claude', xpn_5='Mme')
        pid.date_time_of_birth = '19780330'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Boulevard Helvetique 196', xad_3='Renens', xad_5='1020', xad_6='CH')
        pid.pid_13 = '^^CP^0796771784'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSULT', pl_2='Salle 5', pl_4='Consultation')
        pv1.pv1_7 = 'MED501^Guerin^Brigitte^^^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS50002')

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
        obr.placer_order_number = EI(ei_1='ORD905', ei_4='HIS_SRC')
        obr.filler_order_number = EI(ei_1='RES905', ei_4='PATHO')
        obr.universal_service_identifier = CWE(cwe_1='88305', cwe_2='Examen histopathologique', cwe_3='CPT')
        obr.observation_date_time = '20260412140000'
        obr.obr_16 = 'MED501^Guerin^Brigitte^^^Dr.^méd.'
        obr.results_rpt_status_chng_date_time = '20260413110000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='22637-3', cwe_2='Rapport de pathologie', cwe_3='LN')
        obx.obx_5 = (
            'Macroscopie: Polype colique, 1.2 x 0.8 cm\\.br\\Microscopie: Adénome tubuleux à dysplasie de bas grade\\.br\\Résection complète\\.br\\Conclusion'
            ': Adénome tubuleux bénin, résection complète'
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
    """ Based on live/ch/ch-enovacom.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENOVACOM')
        msh.sending_facility = HD(hd_1='INTEGRATION')
        msh.receiving_application = HD(hd_1='HIS_DST')
        msh.receiving_facility = HD(hd_1='HOPITAL_SION')
        msh.date_time_of_message = '20260414150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ENOV00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='PAT900001', cx_4='HOPITAL_SION&2.16.756.5.30.1.190.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Gautier', xpn_2='Claude', xpn_3='Yvonne', xpn_5='M.')
        pid.date_time_of_birth = '19650812'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Place Saint-Francois 168', xad_3='Bulle', xad_5='1630', xad_6='CH')
        pid.pid_13 = '^^PH^0262460819'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MEDINTERNE', pl_2='Chambre 201', pl_3='Lit A', pl_4='Médecine interne')
        pv1.pv1_7 = 'MED500^Dubois^Denise^^^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS50001')

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
        obr.placer_order_number = EI(ei_1='ORD906', ei_4='HIS_SRC')
        obr.filler_order_number = EI(ei_1='RES906', ei_4='LABSYS')
        obr.universal_service_identifier = CWE(cwe_1='COAG', cwe_2='Bilan de coagulation', cwe_3='LN')
        obr.observation_date_time = '20260414090000'
        obr.obr_16 = 'MED500^Dubois^Denise^^^Dr.^méd.'
        obr.results_rpt_status_chng_date_time = '20260414150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='Temps de prothrombine (Quick)', cwe_3='LN')
        obx.obx_5 = '88'
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
        obx_3.obx_5 = '30'
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
    """ Based on live/ch/ch-enovacom.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENOVACOM')
        msh.sending_facility = HD(hd_1='INTEGRATION')
        msh.receiving_application = HD(hd_1='HIS_SRC')
        msh.receiving_facility = HD(hd_1='HOPITAL_SION')
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
        msa.message_control_id = 'ENOV00001'
        msa.msa_3 = 'Message traité avec succès'

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
