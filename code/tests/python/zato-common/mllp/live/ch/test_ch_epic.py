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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, EI, EIP, FC, HD, MSG, PL, PT, VID, XAD, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA39Patient, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, \
    OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12LocationResource, SiuS12Patient, \
    SiuS12PersonnelResource, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A09, ADT_A39, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, EVN, IN1, MRG, MSA, MSH, OBR, OBX, ORC, PID, PV1, RGS, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('ch', 'ch-epic.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/ch/ch-epic.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.receiving_application = HD(hd_1='LABO')
        msh.receiving_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.date_time_of_message = '20260301070000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'EPIC00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260301070000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [
            CX(cx_1='MRN100001', cx_4='CHUV&2.16.756.5.30.1.145.1&ISO', cx_5='MR'),
            CX(cx_1='7560111222333', cx_4='&2.16.756.5.31&ISO', cx_5='SS'),
        ]
        pid.patient_name = XPN(xpn_1='Simon', xpn_2='Anne', xpn_3='Claude', xpn_5='Mme')
        pid.date_time_of_birth = '19750415'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Boulevard Helvetique 68', xad_3='Vernier', xad_5='1214', xad_6='CH')
        pid.pid_13 = '^^PH^0223298752~^^CP^0771375557'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MEDINTERNE', pl_2='Chambre 301', pl_3='Lit A', pl_4='Médecine interne')
        pv1.pv1_7 = 'MED001^Richard^Madeleine^^^Dr.^méd.'
        pv1.pv1_8 = 'MED002^Perrin^Yvonne^^^Dr.^méd.'
        pv1.financial_class = FC(fc_1='CAS00123')
        pv1.total_charges = '20260301070000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='LAMal')
        in1.insurance_company_id = CX(cx_1='ASSURA001')
        in1.insurance_company_name = XON(xon_1='Assura SA')
        in1.insurance_company_address = XAD(xad_1='Avenue Charles-Ferdinand Ramuz 70', xad_3='Pully', xad_5='1009', xad_6='CH')
        in1.insureds_id_number = CX(cx_1='756.5678.9012.34')

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
    """ Based on live/ch/ch-epic.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.receiving_application = HD(hd_1='LABO')
        msh.receiving_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.date_time_of_message = '20260303090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'EPIC00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260303090000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='MRN100001', cx_4='CHUV&2.16.756.5.30.1.145.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Simon', xpn_2='Anne', xpn_3='Claude', xpn_5='Mme')
        pid.date_time_of_birth = '19750415'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Boulevard Helvetique 68', xad_3='Vernier', xad_5='1214', xad_6='CH')
        pid.pid_13 = '^^PH^0223298752~^^CP^0771375557'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIRURGIE', pl_2='Chambre 405', pl_3='Lit B', pl_4='Chirurgie')
        pv1.pv1_7 = 'MED003^Andre^Thierry^^^Prof.^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS00123')
        pv1.account_status = CWE(cwe_1='MEDINTERNE', cwe_2='Chambre 301', cwe_3='Lit A', cwe_4='Médecine interne')
        pv1.prior_temporary_location = PL(pl_1='20260303090000')

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
    """ Based on live/ch/ch-epic.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.receiving_application = HD(hd_1='LABO')
        msh.receiving_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.date_time_of_message = '20260312150000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'EPIC00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260312150000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='MRN100001', cx_4='CHUV&2.16.756.5.30.1.145.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Simon', xpn_2='Anne', xpn_3='Claude', xpn_5='Mme')
        pid.date_time_of_birth = '19750415'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Boulevard Helvetique 68', xad_3='Vernier', xad_5='1214', xad_6='CH')
        pid.pid_13 = '^^PH^0223298752~^^CP^0771375557'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIRURGIE', pl_2='Chambre 405', pl_3='Lit B', pl_4='Chirurgie')
        pv1.pv1_7 = 'MED003^Andre^Thierry^^^Prof.^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS00123')
        pv1.current_patient_balance = '20260312150000'

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
    """ Based on live/ch/ch-epic.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='HUG_GENEVE')
        msh.receiving_application = HD(hd_1='POLICLINIQUE')
        msh.receiving_facility = HD(hd_1='HUG_GENEVE')
        msh.date_time_of_message = '20260315100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'EPIC00004'
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
        pid.patient_identifier_list = CX(cx_1='MRN200001', cx_4='HUG&2.16.756.5.30.1.146.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Durand', xpn_2='Raymond', xpn_3='Maurice', xpn_5='M.')
        pid.date_time_of_birth = '19681228'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Quai du Mont-Blanc 18', xad_3='Renens', xad_5='1020', xad_6='CH')
        pid.pid_13 = '^^PH^0218770834~^^CP^0783039770'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSULT', pl_2='Salle 12', pl_4='Consultation')
        pv1.pv1_7 = 'MED004^Morin^Renee^^^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS00456')
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
    """ Based on live/ch/ch-epic.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='HUG_GENEVE')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='HUG_GENEVE')
        msh.date_time_of_message = '20260318110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'EPIC00005'
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
        pid.patient_identifier_list = CX(cx_1='MRN200001', cx_4='HUG&2.16.756.5.30.1.146.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Durand', xpn_2='Raymond', xpn_3='Maurice', xpn_5='M.')
        pid.date_time_of_birth = '19681228'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Quai du Mont-Blanc 18', xad_3='Renens', xad_5='1020', xad_6='CH')
        pid.pid_13 = '^^PH^0218770834~^^CP^0783039770~^^Internet^raymond.durand@netplus.ch'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSULT', pl_2='Salle 12', pl_4='Consultation')
        pv1.pv1_7 = 'MED004^Morin^Renee^^^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS00456')
        pv1.current_patient_balance = '20260318110000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='LAMal')
        in1.insurance_company_id = CX(cx_1='VISANA001')
        in1.insurance_company_name = XON(xon_1='Visana AG')
        in1.insurance_company_address = XAD(xad_1='Weltpoststrasse 19', xad_3='Bern', xad_5='3015', xad_6='CH')
        in1.insureds_id_number = CX(cx_1='756.8765.4321.09')

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
    """ Based on live/ch/ch-epic.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.receiving_application = HD(hd_1='LABOSYS')
        msh.receiving_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.date_time_of_message = '20260320083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'EPIC00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='MRN300001', cx_4='CHUV&2.16.756.5.30.1.145.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Moreau', xpn_2='Luc', xpn_3='Madeleine', xpn_5='M.')
        pid.date_time_of_birth = '19550310'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Avenue de France 153', xad_3='Nyon', xad_5='1260', xad_6='CH')
        pid.pid_13 = '^^CP^0793789273'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MEDINTERNE', pl_2='Chambre 210', pl_3='Lit A', pl_4='Médecine interne')
        pv1.pv1_7 = 'MED005^Garnier^Denise^^^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS00789')

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
        orc.placer_order_number = EI(ei_1='ORD001', ei_4='EPIC')
        orc.orc_7 = '^^^20260320090000^^R'
        orc.date_time_of_order_event = '20260320083000'
        orc.orc_10 = 'MED005^Garnier^Denise^^^Dr.^méd.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD001', ei_4='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Bilan hépatique complet', cwe_3='LN')
        obr.observation_date_time = '20260320083000'
        obr.specimen_action_code = 'A'
        obr.obr_16 = 'MED005^Garnier^Denise^^^Dr.^méd.'

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
    """ Based on live/ch/ch-epic.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABOSYS')
        msh.sending_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.date_time_of_message = '20260320160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='MRN300001', cx_4='CHUV&2.16.756.5.30.1.145.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Moreau', xpn_2='Luc', xpn_3='Madeleine', xpn_5='M.')
        pid.date_time_of_birth = '19550310'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Avenue de France 153', xad_3='Nyon', xad_5='1260', xad_6='CH')
        pid.pid_13 = '^^CP^0793789273'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MEDINTERNE', pl_2='Chambre 210', pl_3='Lit A', pl_4='Médecine interne')
        pv1.pv1_7 = 'MED005^Garnier^Denise^^^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS00789')

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
        obr.placer_order_number = EI(ei_1='ORD001', ei_4='EPIC')
        obr.filler_order_number = EI(ei_1='RES001', ei_4='LABOSYS')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Bilan hépatique complet', cwe_3='LN')
        obr.observation_date_time = '20260320083000'
        obr.obr_16 = 'MED005^Garnier^Denise^^^Dr.^méd.'
        obr.results_rpt_status_chng_date_time = '20260320160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALAT (GPT)', cwe_3='LN')
        obx.obx_5 = '35'
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
        obx_2.obx_5 = '28'
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
        obx_3.observation_identifier = CWE(cwe_1='6768-6', cwe_2='Phosphatase alcaline', cwe_3='LN')
        obx_3.obx_5 = '72'
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
        obx_4.observation_identifier = CWE(cwe_1='1975-2', cwe_2='Bilirubine totale', cwe_3='LN')
        obx_4.obx_5 = '12'
        obx_4.units = CWE(cwe_1='umol/L')
        obx_4.reference_range = '3-22'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='1751-7', cwe_2='Albumine', cwe_3='LN')
        obx_5.obx_5 = '42'
        obx_5.units = CWE(cwe_1='g/L')
        obx_5.reference_range = '34-54'
        obx_5.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/ch/ch-epic.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABOSYS')
        msh.sending_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.date_time_of_message = '20260321110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='MRN400001', cx_4='CHUV&2.16.756.5.30.1.145.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Gautier', xpn_2='Brigitte', xpn_3='Therese', xpn_5='Mme')
        pid.date_time_of_birth = '19821203'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rue de la Servette 53', xad_3='Bulle', xad_5='1630', xad_6='CH')
        pid.pid_13 = '^^CP^0761606448'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSULT', pl_2='Salle 4', pl_4='Hématologie')
        pv1.pv1_7 = 'MED006^Henry^Roger^^^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS01234')

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
        obr.placer_order_number = EI(ei_1='ORD002', ei_4='EPIC')
        obr.filler_order_number = EI(ei_1='RES002', ei_4='LABOSYS')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='Formule sanguine complète', cwe_3='LN')
        obr.observation_date_time = '20260321090000'
        obr.obr_16 = 'MED006^Henry^Roger^^^Dr.^méd.'
        obr.results_rpt_status_chng_date_time = '20260321110000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='58410-2', cwe_2='Formule sanguine complète', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoK'
            'PDwgL0xlbmd0aCA1MiA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKEZvcm11bGUgc2FuZ3VpbmUpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDUKMDAwMDAw'
            'MDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNzQgMDAwMDAgbiAKMDAwMDAwMDE0MiAwMDAwMCBuIAowMDAwMDAwMjQyIDAwMDAwIG4gCnRyYWlsZXIKPDwg'
            'L1NpemUgNSAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKMzQ0CiUlRU9GCg=='
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
    """ Based on live/ch/ch-epic.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='HUG_GENEVE')
        msh.receiving_application = HD(hd_1='ARCHIVDOC')
        msh.receiving_facility = HD(hd_1='HUG_GENEVE')
        msh.date_time_of_message = '20260322140000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'EPIC00009'
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
        pid.patient_identifier_list = CX(cx_1='MRN200001', cx_4='HUG&2.16.756.5.30.1.146.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Durand', xpn_2='Raymond', xpn_3='Maurice', xpn_5='M.')
        pid.date_time_of_birth = '19681228'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Quai du Mont-Blanc 18', xad_3='Renens', xad_5='1020', xad_6='CH')
        pid.pid_13 = '^^CP^0783039770'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIRURGIE', pl_2='Chambre 302', pl_3='Lit A', pl_4='Chirurgie')
        pv1.pv1_7 = 'MED007^Roussel^Philippe^^^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS01456')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS')
        txa.document_content_presentation = 'AP'
        txa.activity_date_time = '20260322140000'
        txa.txa_5 = 'MED007^Roussel^Philippe^^^Dr.^méd.'
        txa.parent_document_number = EI(ei_1='DOC789012')
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
            'PDwgL0xlbmd0aCA1NCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKExldHRyZSBkZSBzb3J0aWUpIFRqIEVUCmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDUKMDAwMDAw'
            'MDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNzQgMDAwMDAgbiAKMDAwMDAwMDE0MiAwMDAwMCBuIAowMDAwMDAwMjQyIDAwMDAwIG4gCnRyYWlsZXIKPDwg'
            'L1NpemUgNSAvUm9vdCAxIDAgUiA+PgpzdGFydHhyZWYKMzQ2CiUlRU9GCg=='
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
    """ Based on live/ch/ch-epic.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.receiving_application = HD(hd_1='AGENDA')
        msh.receiving_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.date_time_of_message = '20260401090000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'EPIC00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='RDV001', ei_4='EPIC')
        sch.event_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine', cwe_3='HL70276')
        sch.appointment_reason = CWE(cwe_1='CONSULT', cwe_2='Consultation', cwe_3='HL70277')
        sch.appointment_type = CWE(cwe_1='30')
        sch.sch_9 = 'MIN'
        sch.appointment_duration_units = CNE(cne_3='30', cne_4='20260415100000', cne_5='20260415103000')
        sch.sch_11 = 'MED005^Garnier^Denise^^^Dr.^méd.'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='MRN300001', cx_4='CHUV&2.16.756.5.30.1.145.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Moreau', xpn_2='Luc', xpn_3='Madeleine', xpn_5='M.')
        pid.date_time_of_birth = '19550310'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Avenue de France 153', xad_3='Nyon', xad_5='1260', xad_6='CH')
        pid.pid_13 = '^^CP^0793789273'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONSULT', pl_2='Salle 8', pl_4='Consultation')
        pv1.pv1_7 = 'MED005^Garnier^Denise^^^Dr.^méd.'

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
        ais.start_date_time_offset_units = CNE(cne_1='20260415100000')
        ais.duration = '30'
        ais.duration_units = CNE(cne_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.segment_action_code = 'A'
        ail.location_resource_id = PL(pl_1='CONSULT', pl_2='Salle 8', pl_4='Consultation')

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.segment_action_code = 'A'
        aip.aip_3 = 'MED005^Garnier^Denise^^^Dr.^méd.'

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
    """ Based on live/ch/ch-epic.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='HUG_GENEVE')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='HUG_GENEVE')
        msh.date_time_of_message = '20260402110000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'EPIC00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='MRN500001', cx_4='HUG&2.16.756.5.30.1.146.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Roux', xpn_2='Yves', xpn_3='Jean', xpn_5='M.')
        pid.date_time_of_birth = '19721014'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rue de la Gare 75', xad_3='Martigny', xad_5='1920', xad_6='CH')
        pid.pid_13 = '^^CP^0792154580'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='URG', pl_2='Box 3', pl_4='Urgences')
        pv1.pv1_7 = 'MED008^Robert^Suzanne^^^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS02345')

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
        orc.placer_order_number = EI(ei_1='ORD100', ei_4='EPIC')
        orc.orc_7 = '^^^20260402120000^^S'
        orc.date_time_of_order_event = '20260402110000'
        orc.orc_10 = 'MED008^Robert^Suzanne^^^Dr.^méd.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD100', ei_4='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='36643-5', cwe_2='CT Thorax avec contraste', cwe_3='LN')
        obr.observation_date_time = '20260402110000'
        obr.specimen_action_code = 'A'
        obr.obr_16 = 'MED008^Robert^Suzanne^^^Dr.^méd.'
        obr.placer_field_2 = 'CT'
        obr.parent_results_observation_identifier = EIP(eip_1='TRAUMA')

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
    """ Based on live/ch/ch-epic.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MICROBIO')
        msh.sending_facility = HD(hd_1='HUG_GENEVE')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='HUG_GENEVE')
        msh.date_time_of_message = '20260403160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MIC00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='MRN500001', cx_4='HUG&2.16.756.5.30.1.146.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Roux', xpn_2='Yves', xpn_3='Jean', xpn_5='M.')
        pid.date_time_of_birth = '19721014'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rue de la Gare 75', xad_3='Martigny', xad_5='1920', xad_6='CH')
        pid.pid_13 = '^^CP^0792154580'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='URG', pl_2='Box 3', pl_4='Urgences')
        pv1.pv1_7 = 'MED008^Robert^Suzanne^^^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS02345')

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
        obr.placer_order_number = EI(ei_1='ORD101', ei_4='EPIC')
        obr.filler_order_number = EI(ei_1='RES101', ei_4='MICROBIO')
        obr.universal_service_identifier = CWE(cwe_1='87040', cwe_2='Hémoculture', cwe_3='LN')
        obr.observation_date_time = '20260403060000'
        obr.obr_16 = 'MED008^Robert^Suzanne^^^Dr.^méd.'
        obr.results_rpt_status_chng_date_time = '20260403160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Micro-organisme identifié', cwe_3='LN')
        obx.obx_5 = 'Escherichia coli'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18906-8', cwe_2='Ampicilline', cwe_3='LN')
        obx_2.obx_5 = 'R'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18928-2', cwe_2='Gentamicine', cwe_3='LN')
        obx_3.obx_5 = 'S'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18955-5', cwe_2='Ciprofloxacine', cwe_3='LN')
        obx_4.obx_5 = 'S'
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
    """ Based on live/ch/ch-epic.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.date_time_of_message = '20260405120000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'EPIC00013'
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
            CX(cx_1='MRN100001', cx_4='CHUV&2.16.756.5.30.1.145.1&ISO', cx_5='MR'),
            CX(cx_1='7560111222333', cx_4='&2.16.756.5.31&ISO', cx_5='SS'),
        ]
        pid.patient_name = XPN(xpn_1='Simon', xpn_2='Anne', xpn_3='Claude', xpn_5='Mme')
        pid.date_time_of_birth = '19750415'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Boulevard Helvetique 68', xad_3='Vernier', xad_5='1214', xad_6='CH')
        pid.pid_13 = '^^PH^0223298752~^^CP^0771375557~^^Internet^anne.simon@sunrise.ch'

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
    """ Based on live/ch/ch-epic.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='HUG_GENEVE')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='HUG_GENEVE')
        msh.date_time_of_message = '20260406080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'EPIC00014'
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
        pid.patient_identifier_list = CX(cx_1='MRN200001', cx_4='HUG&2.16.756.5.30.1.146.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Durand', xpn_2='Raymond', xpn_3='Maurice', xpn_5='M.')
        pid.date_time_of_birth = '19681228'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Quai du Mont-Blanc 18', xad_3='Renens', xad_5='1020', xad_6='CH')
        pid.pid_13 = '^^CP^0783039770'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='MRN299999', cx_4='HUG&2.16.756.5.30.1.146.1&ISO', cx_5='MR')

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
    """ Based on live/ch/ch-epic.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CHIMIE')
        msh.sending_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.date_time_of_message = '20260407150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'CHIM00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='MRN600001', cx_4='CHUV&2.16.756.5.30.1.145.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Morel', xpn_2='Francois', xpn_3='Renee', xpn_5='M.')
        pid.date_time_of_birth = '19490520'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Avenue de la Gare 198', xad_3='Carouge', xad_5='1227', xad_6='CH')
        pid.pid_13 = '^^PH^0227558410'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='Chambre 501', pl_3='Lit A', pl_4='Cardiologie')
        pv1.pv1_7 = 'MED009^Duval^Henri^^^Prof.^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS03456')

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
        obr.placer_order_number = EI(ei_1='ORD200', ei_4='EPIC')
        obr.filler_order_number = EI(ei_1='RES200', ei_4='CHIMIE')
        obr.universal_service_identifier = CWE(cwe_1='2160-0', cwe_2='Créatinine sérique', cwe_3='LN')
        obr.observation_date_time = '20260407090000'
        obr.obr_16 = 'MED009^Duval^Henri^^^Prof.^Dr.^méd.'
        obr.results_rpt_status_chng_date_time = '20260407150000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Créatinine', cwe_3='LN')
        obx.obx_5 = '112'
        obx.units = CWE(cwe_1='umol/L')
        obx.reference_range = '62-106'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urée', cwe_3='LN')
        obx_2.obx_5 = '8.5'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '2.8-7.2'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium', cwe_3='LN')
        obx_3.obx_5 = '4.2'
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
        obx_4.obx_5 = '139'
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
    """ Based on live/ch/ch-epic.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.receiving_application = HD(hd_1='LABO')
        msh.receiving_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.date_time_of_message = '20260408070000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A11', msg_3='ADT_A09')
        msh.message_control_id = 'EPIC00016'
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
        pid.patient_identifier_list = CX(cx_1='MRN700001', cx_4='CHUV&2.16.756.5.30.1.145.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Dubois', xpn_2='Alain', xpn_3='Andre', xpn_5='M.')
        pid.date_time_of_birth = '19880612'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rue du Marche 173', xad_3='Morges', xad_5='1110', xad_6='CH')
        pid.pid_13 = '^^CP^0767993202'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIRURGIE', pl_2='Chambre 201', pl_3='Lit A', pl_4='Chirurgie')
        pv1.pv1_7 = 'MED003^Andre^Thierry^^^Prof.^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS04567')
        pv1.current_patient_balance = '20260408070000'

        # .. assemble the full message ..
        msg = ADT_A09()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/ch/ch-epic.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HEMATO')
        msh.sending_facility = HD(hd_1='HUG_GENEVE')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='HUG_GENEVE')
        msh.date_time_of_message = '20260409140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'HEM00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='MRN800001', cx_4='HUG&2.16.756.5.30.1.146.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Legrand', xpn_2='Pauline', xpn_3='Jean', xpn_5='Mme')
        pid.date_time_of_birth = '19630817'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Avenue de Cour 38', xad_3='Morges', xad_5='1110', xad_6='CH')
        pid.pid_13 = '^^PH^0211190117'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HEMATO', pl_2='Chambre 605', pl_3='Lit A', pl_4='Hématologie')
        pv1.pv1_7 = 'MED010^Mercier^Agnes^^^Prof.^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS05678')

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
        obr.placer_order_number = EI(ei_1='ORD300', ei_4='EPIC')
        obr.filler_order_number = EI(ei_1='RES300', ei_4='HEMATO')
        obr.universal_service_identifier = CWE(cwe_1='57021-8', cwe_2='Formule leucocytaire', cwe_3='LN')
        obr.observation_date_time = '20260409080000'
        obr.obr_16 = 'MED010^Mercier^Agnes^^^Prof.^Dr.^méd.'
        obr.results_rpt_status_chng_date_time = '20260409140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hémoglobine', cwe_3='LN')
        obx.obx_5 = '98'
        obx.units = CWE(cwe_1='g/L')
        obx.reference_range = '120-160'
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
        obx_2.obx_5 = '12.5'
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
        obx_3.observation_identifier = CWE(cwe_1='789-8', cwe_2='Thrombocytes', cwe_3='LN')
        obx_3.obx_5 = '180'
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
        obx_4.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hématocrite', cwe_3='LN')
        obx_4.obx_5 = '0.31'
        obx_4.units = CWE(cwe_1='L/L')
        obx_4.reference_range = '0.36-0.46'
        obx_4.interpretation_codes = CWE(cwe_1='L')
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
    """ Based on live/ch/ch-epic.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.date_time_of_message = '20260410080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'EPIC00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20260410080000'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [
            CX(cx_1='MRN900001', cx_4='CHUV&2.16.756.5.30.1.145.1&ISO', cx_5='MR'),
            CX(cx_1='7569012345678', cx_4='&2.16.756.5.31&ISO', cx_5='SS'),
        ]
        pid.patient_name = XPN(xpn_1='Masson', xpn_2='Gerard', xpn_3='Pierre', xpn_5='M.')
        pid.date_time_of_birth = '19950718'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rue Neuve 141', xad_3='Sion', xad_5='1950', xad_6='CH')
        pid.pid_13 = '^^CP^0779983319~^^Internet^gerard.masson@gmail.com'

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
    """ Based on live/ch/ch-epic.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PATHO')
        msh.sending_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.date_time_of_message = '20260411110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'PATH00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='MRN300001', cx_4='CHUV&2.16.756.5.30.1.145.1&ISO', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Moreau', xpn_2='Luc', xpn_3='Madeleine', xpn_5='M.')
        pid.date_time_of_birth = '19550310'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Avenue de France 153', xad_3='Nyon', xad_5='1260', xad_6='CH')
        pid.pid_13 = '^^CP^0793789273'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIRURGIE', pl_2='Chambre 308', pl_3='Lit A', pl_4='Chirurgie')
        pv1.pv1_7 = 'MED003^Andre^Thierry^^^Prof.^Dr.^méd.'
        pv1.visit_number = CX(cx_1='CAS06789')

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
        obr.placer_order_number = EI(ei_1='ORD400', ei_4='EPIC')
        obr.filler_order_number = EI(ei_1='RES400', ei_4='PATHO')
        obr.universal_service_identifier = CWE(cwe_1='88305', cwe_2='Examen histopathologique', cwe_3='CPT')
        obr.observation_date_time = '20260410140000'
        obr.obr_16 = 'MED003^Andre^Thierry^^^Prof.^Dr.^méd.'
        obr.results_rpt_status_chng_date_time = '20260411110000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='22637-3', cwe_2='Rapport de pathologie', cwe_3='LN')
        obx.obx_5 = (
            'Macroscopie: Pièce de résection colique, 18 cm\\.br\\Microscopie: Adénocarcinome colique modérément différencié\\.br\\Invasion pariétale: Sous-s'
            'éreuse (pT3)\\.br\\Ganglions: 2/18 positifs (pN1a)\\.br\\Marges de résection libres\\.br\\Classification: pT3 pN1a M0, stade IIIB'
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
    """ Based on live/ch/ch-epic.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABO')
        msh.sending_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='CHUV_LAUSANNE')
        msh.date_time_of_message = '20260412080100'
        msh.message_type = MSG(msg_1='ACK', msg_2='A01', msg_3='ACK')
        msh.message_control_id = 'ACK00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'CHE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'EPIC00001'
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
