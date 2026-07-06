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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, EI, FC, HD, MSG, OG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, \
    OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12LocationResource, SiuS12Patient, \
    SiuS12PersonnelResource, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, AL1, DG1, EVN, IN1, MSH, NK1, OBR, OBX, ORC, PD1, PID, PRT, PV1, RGS, RXO, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('be', 'be-dxcare.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/be/be-dxcare.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DXCARE')
        msh.sending_facility = HD(hd_1='CHU_ST_PIERRE')
        msh.receiving_application = HD(hd_1='HIS_BE')
        msh.receiving_facility = HD(hd_1='CHU_ST_PIERRE')
        msh.date_time_of_message = '20260509070000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG10001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260509070000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT23012', cx_4='CHSP', cx_5='PI')
        pid.pid_4 = '86021534217^^^^NN'
        pid.patient_name = XPN(xpn_1='Dubois', xpn_2='Marc-Antoine', xpn_3='R', xpn_5='M.')
        pid.date_time_of_birth = '19860215'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rue du Midi 145', xad_3='Bruxelles', xad_5='1000', xad_6='BE')
        pid.pid_13 = '^^PH^02-646-4222~^^CP^0476-234567~^^Internet^madubois@skynet.be'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Dubois', xpn_2='Elise', xpn_3='L')
        nk1.relationship = CWE(cwe_1='SPO')
        nk1.address = XAD(xad_1='Rue du Midi 145', xad_3='Bruxelles', xad_5='1000', xad_6='BE')
        nk1.nk1_5 = '0476-765432'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='Kamer 405', pl_3='Bed 2', pl_4='Cardiologie')
        pv1.pv1_7 = '20555666045^Van Damme^Frederik^^^Prof.^Dr.^med.'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='OPNAME89142')
        pv1.account_status = CWE(cwe_1='CARDIO', cwe_2='Kamer 405', cwe_3='Bed 2', cwe_4='Cardiologie')
        pv1.prior_temporary_location = PL(pl_1='20260509070000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='0')
        in1.insurance_company_id = CX(cx_1='MUT003')
        in1.insurance_company_name = XON(xon_1='NEUTRALE ZIEKENFONDS')
        in1.insurance_company_address = XAD(xad_1='Rue des Colonies 11', xad_3='Bruxelles', xad_5='1000', xad_6='BE')
        in1.insureds_id_number = CX(cx_1='56')

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
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
    """ Based on live/be/be-dxcare.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DXCARE')
        msh.sending_facility = HD(hd_1='AZ_MONICA')
        msh.receiving_application = HD(hd_1='HIS_BE')
        msh.receiving_facility = HD(hd_1='AZ_MONICA')
        msh.date_time_of_message = '20260509083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04')
        msh.message_control_id = 'MSG10002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20260509083000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT24212', cx_4='AZM', cx_5='PI')
        pid.pid_4 = '92041267834^^^^NN'
        pid.patient_name = XPN(xpn_1='Goossens', xpn_2='Lien', xpn_3='M', xpn_5='Mevr.')
        pid.date_time_of_birth = '19920412'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Turnhoutsebaan 88', xad_3='Borgerhout', xad_5='2140', xad_6='BE')
        pid.pid_13 = '^^PH^03-431-2345'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Goossens', xpn_2='Hendrik', xpn_3='W')
        nk1.relationship = CWE(cwe_1='FTH')
        nk1.start_date = '20260509'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONS', pl_2='Consult-3', pl_3='1', pl_4='Gastro-enterologie')
        pv1.attending_doctor = XCN(xcn_1='20333444023', xcn_2='Wouters', xcn_3='Katrien', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')

        # .. build AL1 ..
        al1 = AL1()
        al1.set_id_al1 = '1'
        al1.allergen_code_mnemonic_description = CWE(cwe_2='ASPIRINE')
        al1.allergy_reaction_code = 'BRONCHOSPASME'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K21.0', cwe_2='Gastro-oesofageale reflux met oesofagitis', cwe_3='ICD10')
        dg1.diagnosis_date_time = '20260509'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.al1 = al1
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
    """ Based on live/be/be-dxcare.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DXCARE')
        msh.sending_facility = HD(hd_1='CHU_ST_PIERRE')
        msh.receiving_application = HD(hd_1='HIS_BE')
        msh.receiving_facility = HD(hd_1='CHU_ST_PIERRE')
        msh.date_time_of_message = '20260510090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'MSG10003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260510090000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT23012', cx_4='CHSP', cx_5='PI')
        pid.pid_4 = '86021534217^^^^NN'
        pid.patient_name = XPN(xpn_1='Dubois', xpn_2='Marc-Antoine', xpn_3='R', xpn_5='M.')
        pid.date_time_of_birth = '19860215'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rue du Midi 145', xad_3='Bruxelles', xad_5='1000', xad_6='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='Kamer 102', pl_3='Bed 1', pl_4='Intensieve Zorgen')
        pv1.pv1_7 = '20555666045^Van Damme^Frederik^^^Prof.^Dr.^med.'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.preadmit_test_indicator = CWE(cwe_1='CARDIO', cwe_2='Kamer 405', cwe_3='Bed 2', cwe_4='Cardiologie')
        pv1.financial_class = FC(fc_1='OPNAME89142')
        pv1.prior_temporary_location = PL(pl_1='ICU', pl_2='Kamer 102', pl_3='Bed 1', pl_4='Intensieve Zorgen')
        pv1.discharge_date_time = '20260510090000'

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
    """ Based on live/be/be-dxcare.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DXCARE')
        msh.sending_facility = HD(hd_1='CHU_ST_PIERRE')
        msh.receiving_application = HD(hd_1='HIS_BE')
        msh.receiving_facility = HD(hd_1='CHU_ST_PIERRE')
        msh.date_time_of_message = '20260515143000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG10004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260515143000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT23012', cx_4='CHSP', cx_5='PI')
        pid.pid_4 = '86021534217^^^^NN'
        pid.patient_name = XPN(xpn_1='Dubois', xpn_2='Marc-Antoine', xpn_3='R', xpn_5='M.')
        pid.date_time_of_birth = '19860215'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rue du Midi 145', xad_3='Bruxelles', xad_5='1000', xad_6='BE')
        pid.pid_13 = '^^PH^02-646-4222~^^CP^0476-234567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='Kamer 405', pl_3='Bed 2', pl_4='Cardiologie')
        pv1.pv1_7 = '20555666045^Van Damme^Frederik^^^Prof.^Dr.^med.'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='OPNAME89142')
        pv1.account_status = CWE(cwe_1='CARDIO', cwe_2='Kamer 405', cwe_3='Bed 2', cwe_4='Cardiologie')
        pv1.prior_temporary_location = PL(pl_1='20260515143000')

        # .. assemble the full message ..
        msg = ADT_A03()
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
    """ Based on live/be/be-dxcare.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DXCARE')
        msh.sending_facility = HD(hd_1='AZ_MONICA')
        msh.receiving_application = HD(hd_1='HIS_BE')
        msh.receiving_facility = HD(hd_1='AZ_MONICA')
        msh.date_time_of_message = '20260509100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'MSG10005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260509100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT24212', cx_4='AZM', cx_5='PI')
        pid.pid_4 = '92041267834^^^^NN'
        pid.patient_name = XPN(xpn_1='Goossens-De Smedt', xpn_2='Lien', xpn_3='M', xpn_5='Mevr.')
        pid.date_time_of_birth = '19920412'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Plantin en Moretuslei 66', xad_3='Berchem', xad_5='2600', xad_6='BE')
        pid.pid_13 = '^^PH^03-431-2345~^^CP^0487-223344~^^Internet^lien.goossens@gmail.com'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CONS', pl_2='Consult-3', pl_3='1', pl_4='Gastro-enterologie')
        pv1.attending_doctor = XCN(xcn_1='20333444023', xcn_2='Wouters', xcn_3='Katrien', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')

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
    """ Based on live/be/be-dxcare.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DXCARE')
        msh.sending_facility = HD(hd_1='CHU_LIEGE')
        msh.receiving_application = HD(hd_1='LABO_BE')
        msh.receiving_facility = HD(hd_1='CHU_LIEGE')
        msh.date_time_of_message = '20260509081500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MSG10006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT25312', cx_4='CHUL', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Marchand', xpn_2='Olivier', xpn_3='V', xpn_5='M.')
        pid.date_time_of_birth = '19790928'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1="Boulevard d'Avroy 33", xad_3='Liege', xad_5='4000', xad_6='BE')
        pid.pid_13 = '^^PH^04-477-8901'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-INT', pl_2='Kamer 512', pl_3='Bed 1', pl_4='Interne Geneeskunde')
        pv1.attending_doctor = XCN(xcn_1='20444555034', xcn_2='Simon', xcn_3='Christophe', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')

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
        orc.placer_order_number = EI(ei_1='ORD10001', ei_2='DXCARE')
        orc.filler_order_number = EI(ei_1='FIL20001', ei_2='LABO_BE')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20260509081500^^R'
        orc.date_time_of_order_event = '20260509081500'
        orc.orc_10 = '20444555034^Simon^Christophe^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD10001', ei_2='DXCARE')
        obr.filler_order_number = EI(ei_1='FIL20001', ei_2='LABO_BE')
        obr.universal_service_identifier = CWE(cwe_1='80053', cwe_2='BLOEDCHEMIE PANEL', cwe_3='CPT4')
        obr.obr_5 = 'R'
        obr.obr_6 = '20260509080000'
        obr.relevant_clinical_information = CWE(cwe_1='20444555034', cwe_2='Simon', cwe_3='Christophe', cwe_6='Dr.')
        obr.placer_field_2 = 'LAB'
        obr.filler_field_1 = 'SC'

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
    """ Based on live/be/be-dxcare.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABO_BE')
        msh.sending_facility = HD(hd_1='CHU_LIEGE')
        msh.receiving_application = HD(hd_1='DXCARE')
        msh.receiving_facility = HD(hd_1='CHU_LIEGE')
        msh.date_time_of_message = '20260509141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MSG10007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT25312', cx_4='CHUL', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Marchand', xpn_2='Olivier', xpn_3='V', xpn_5='M.')
        pid.date_time_of_birth = '19790928'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1="Boulevard d'Avroy 33", xad_3='Liege', xad_5='4000', xad_6='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-INT', pl_2='Kamer 512', pl_3='Bed 1', pl_4='Interne Geneeskunde')
        pv1.attending_doctor = XCN(xcn_1='20444555034', xcn_2='Simon', xcn_3='Christophe', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')

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
        orc.placer_order_number = EI(ei_1='ORD10001', ei_2='DXCARE')
        orc.filler_order_number = EI(ei_1='FIL20001', ei_2='LABO_BE')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD10001', ei_2='DXCARE')
        obr.filler_order_number = EI(ei_1='FIL20001', ei_2='LABO_BE')
        obr.universal_service_identifier = CWE(cwe_1='80053', cwe_2='BLOEDCHEMIE PANEL', cwe_3='CPT4')
        obr.obr_16 = '20666777056^Michel^Francois^^^Dr.'
        obr.results_rpt_status_chng_date_time = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2160-0', cwe_2='CREATININE', cwe_3='LN')
        obx.obx_5 = '88'
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
        obx_2.observation_identifier = CWE(cwe_1='3094-0', cwe_2='UREUM', cwe_3='LN')
        obx_2.obx_5 = '5.2'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '2.5-7.1'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2345-7', cwe_2='GLUCOSE', cwe_3='LN')
        obx_3.obx_5 = '12.8'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '3.9-5.8'
        obx_3.interpretation_codes = CWE(cwe_1='HH')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2823-3', cwe_2='KALIUM', cwe_3='LN')
        obx_4.obx_5 = '4.1'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '3.5-5.1'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2951-2', cwe_2='NATRIUM', cwe_3='LN')
        obx_5.obx_5 = '139'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '136-145'
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
    """ Based on live/be/be-dxcare.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DXCARE')
        msh.sending_facility = HD(hd_1='CLINIQUE_STE_ANNE')
        msh.receiving_application = HD(hd_1='DMP_BE')
        msh.receiving_facility = HD(hd_1='EHEALTH_BE')
        msh.date_time_of_message = '20260509150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG10008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT26412', cx_4='CSA', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Janssens', xpn_2='Nathalie', xpn_3='E', xpn_5='Mevr.')
        pid.date_time_of_birth = '19971022'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Rue Neuve 55', xad_3='Bruxelles', xad_5='1000', xad_6='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='Kamer 301', pl_3='Bed 1', pl_4='Chirurgie')
        pv1.attending_doctor = XCN(xcn_1='20666777056', xcn_2='Mertens', xcn_3='Willem', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='CHIR')

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
        orc.placer_order_number = EI(ei_1='ORD11101', ei_2='DXCARE')
        orc.filler_order_number = EI(ei_1='FIL21101', ei_2='LABO_BE')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD11101', ei_2='DXCARE')
        obr.filler_order_number = EI(ei_1='FIL21101', ei_2='LABO_BE')
        obr.universal_service_identifier = CWE(cwe_1='11502-2', cwe_2="CR d'examens biologiques", cwe_3='LN')
        obr.obr_16 = '20666777056^Mertens^Willem^^^Dr.'
        obr.results_rpt_status_chng_date_time = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='11502-2', cwe_2="CR d'examens biologiques", cwe_3='LN')
        obx.obx_5 = (
            '^TEXT^XML^Base64^'
            'PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIj48dGl0bGU+Q29tcHRlIHJlbmR1IGQnZXhhbWVucyBiaW9sb2dpcXVlczwvdGl0bGU+PGNvbXBvbmVudD48c2Vj'
            'dGlvbj48dGV4dD5IZW1vZ2xvYmluZSAxNDUgZy9MLCBDUlAgMTIgbWcvTDwvdGV4dD48L3NlY3Rpb24+PC9jb21wb25lbnQ+PC9DbGluaWNhbERvY3VtZW50Pg=='
        )
        obx.observation_result_status = 'F'

        # .. build PRT ..
        prt = PRT()
        prt.action_code = 'UC'
        prt.role_of_participation = CWE(cwe_1='SB', cwe_2='Send by', cwe_3='participation')
        prt.person = XCN(xcn_1='20666777056', xcn_2='Mertens', xcn_3='Willem', xcn_9='NIHDI&2.16.840.1.113883.3.6777.5.2&ISO', xcn_10='D', xcn_13='NIHDI')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx
        observation.prt = prt

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='MASQUE_PS', cwe_2='Masque aux professionnels de Sante', cwe_3='MetaDMPMSS')
        obx_2.obx_5 = 'N^^expandedYes-NoIndicator'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='INVISIBLE_PATIENT', cwe_2='Document Non Visible par le patient', cwe_3='MetaDMPMSS')
        obx_3.obx_5 = 'N^^expandedYes-NoIndicator'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'CE'
        obx_4.observation_identifier = CWE(cwe_1='DESTDMP', cwe_2='Destinataire DMP', cwe_3='MetaDMPMSS')
        obx_4.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'CE'
        obx_5.observation_identifier = CWE(cwe_1='DESTMSSANTEPS', cwe_2='Destinataire PS', cwe_3='MetaDMPMSS')
        obx_5.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'CE'
        obx_6.observation_identifier = CWE(cwe_1='DESTMSSANTEPAT', cwe_2='Destinataire Patient', cwe_3='MetaDMPMSS')
        obx_6.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'CE'
        obx_7.observation_identifier = CWE(cwe_1='ACK_RECEPTION', cwe_2='Accuse de reception', cwe_3='MetaDMPMSS')
        obx_7.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'CE'
        obx_8.observation_identifier = CWE(cwe_1='ACK_LECTURE', cwe_2='Accuse de lecture', cwe_3='MetaDMPMSS')
        obx_8.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'ED'
        obx_9.observation_identifier = CWE(cwe_1='CORPSMAIL_PS', cwe_2='Corps du mail pour un PS', cwe_3='MetaDMPMSS')
        obx_9.obx_5 = '^TEXT^^Base64^Q2hlciBjb25mcmVyZSwgdm91cyB0cm91dmVyZXogY2ktam9pbnQgbGUgQ1IgZGUgYmlvbG9naWUgZGUgTW1lIERlY2xlcmNxLg=='
        obx_9.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

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
        order_observation.observation_9 = observation_9

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
    """ Based on live/be/be-dxcare.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DXCARE')
        msh.sending_facility = HD(hd_1='CHR_NAMUR')
        msh.receiving_application = HD(hd_1='DMP_BE')
        msh.receiving_facility = HD(hd_1='EHEALTH_BE')
        msh.date_time_of_message = '20260509160000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG10009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20260509160000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT27512', cx_4='CHRN', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Gilles', xpn_2='Thierry', xpn_3='J', xpn_5='M.')
        pid.date_time_of_birth = '19701124'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rue de Fer 28', xad_3='Namur', xad_5='5000', xad_6='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MED-INT', pl_2='Consult-1', pl_3='1', pl_4='Medecine Interne')
        pv1.attending_doctor = XCN(xcn_1='20777888067', xcn_2='Lejeune', xcn_3='Marie-Claire', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='CR', cwe_2='Compte Rendu', cwe_3='L')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20260509155000'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20777888067', xcn_2='Lejeune', xcn_3='Marie-Claire', xcn_6='Dr.')
        txa.transcription_date_time = '20260509160000'
        txa.edit_date_time = 'ED'
        txa.originator_code_name = XCN(xcn_1='DOC-20260509-001')
        txa.txa_12 = '20777888067^Lejeune^Marie-Claire^^^Dr.'
        txa.unique_document_file_name = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2="CR d'imagerie medicale", cwe_3='LN')
        obx.obx_5 = (
            '^text^XML^Base64^'
            'PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIj48dGl0bGU+Q29tcHRlIHJlbmR1IGQnaW1hZ2VyaWUgbWVkaWNhbGU8L3RpdGxlPjxjb21wb25lbnQ+PHNlY3Rp'
            'b24+PHRleHQ+UmFkaW9ncmFwaGllIHRob3JhY2lxdWUgbm9ybWFsZTwvdGV4dD48L3NlY3Rpb24+PC9jb21wb25lbnQ+PC9DbGluaWNhbERvY3VtZW50Pg=='
        )
        obx.observation_result_status = 'F'

        # .. build PRT ..
        prt = PRT()
        prt.action_code = 'UC'
        prt.role_of_participation = CWE(cwe_1='SB', cwe_2='Send by', cwe_3='participation')
        prt.person = XCN(xcn_1='20777888067', xcn_2='Lejeune', xcn_3='Marie-Claire', xcn_9='NIHDI&2.16.840.1.113883.3.6777.5.2&ISO', xcn_10='D', xcn_13='NIHDI')

        # .. build PRT ..
        prt_2 = PRT()
        prt_2.action_code = 'UC'
        prt_2.role_of_participation = CWE(cwe_1='RCT', cwe_2='Results Copies To', cwe_3='participation')
        prt_2.person = XCN(xcn_1='20888999078', xcn_2='Laurent', xcn_3='Bernard', xcn_9='NIHDI&2.16.840.1.113883.3.6777.5.2&ISO', xcn_10='D', xcn_13='NIHDI')

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx
        observation.prt = prt
        observation.prt_2 = prt_2

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CWE'
        obx_2.observation_identifier = CWE(cwe_1='MASQUE_PS', cwe_2='Masque aux professionnels de Sante', cwe_3='MetaDMPMSS')
        obx_2.obx_5 = 'N^^expandedYes-NoIndicator'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = MdmT02Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CWE'
        obx_3.observation_identifier = CWE(cwe_1='INVISIBLE_PATIENT', cwe_2='Document Non Visible par le patient', cwe_3='MetaDMPMSS')
        obx_3.obx_5 = 'N^^expandedYes-NoIndicator'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = MdmT02Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'CWE'
        obx_4.observation_identifier = CWE(cwe_1='DESTDMP', cwe_2='Destinataire DMP', cwe_3='MetaDMPMSS')
        obx_4.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = MdmT02Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'CWE'
        obx_5.observation_identifier = CWE(cwe_1='DESTMSSANTEPS', cwe_2='Destinataire PS', cwe_3='MetaDMPMSS')
        obx_5.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = MdmT02Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'CWE'
        obx_6.observation_identifier = CWE(cwe_1='DESTMSSANTEPAT', cwe_2='Destinataire Patient', cwe_3='MetaDMPMSS')
        obx_6.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = MdmT02Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ED'
        obx_7.observation_identifier = CWE(cwe_1='CORPSMAIL_PS', cwe_2='Corps du mail pour un PS', cwe_3='MetaDMPMSS')
        obx_7.obx_5 = '^text^^Base64^Q2hlciBjb25mcmVyZSwgdm91cyB0cm91dmVyZXogY2ktam9pbnQgbGUgQ1IgZCdpbWFnZXJpZSBkZSBNLkJvZGFydC4='
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = MdmT02Observation()
        observation_7.obx = obx_7

        # .. assemble the full message ..
        msg = MDM_T02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.txa = txa
        msg.observation = [observation, observation_2, observation_3, observation_4, observation_5, observation_6, observation_7]

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
    """ Based on live/be/be-dxcare.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DXCARE')
        msh.sending_facility = HD(hd_1='CHR_NAMUR')
        msh.receiving_application = HD(hd_1='DMP_BE')
        msh.receiving_facility = HD(hd_1='EHEALTH_BE')
        msh.date_time_of_message = '20260510080000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T04', msg_3='MDM_T02')
        msh.message_control_id = 'MSG10010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T04'
        evn.recorded_date_time = '20260510080000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT27512', cx_4='CHRN', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Gilles', xpn_2='Thierry', xpn_3='J', xpn_5='M.')
        pid.date_time_of_birth = '19701124'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rue de Fer 28', xad_3='Namur', xad_5='5000', xad_6='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MED-INT', pl_2='Consult-1', pl_3='1', pl_4='Medecine Interne')
        pv1.attending_doctor = XCN(xcn_1='20777888067', xcn_2='Lejeune', xcn_3='Marie-Claire', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='CR', cwe_2='Compte Rendu', cwe_3='L')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20260510075000'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20777888067', xcn_2='Lejeune', xcn_3='Marie-Claire', xcn_6='Dr.')
        txa.transcription_date_time = '20260510080000'
        txa.edit_date_time = 'ED'
        txa.originator_code_name = XCN(xcn_1='DOC-20260509-001')
        txa.txa_12 = '20777888067^Lejeune^Marie-Claire^^^Dr.'
        txa.unique_document_file_name = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2="CR d'imagerie medicale", cwe_3='LN')
        obx.obx_5 = (
            '^text^XML^Base64^PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIj48dGl0bGU+RG9jdW1lbnQgc3VwcHJpbWU8L3RpdGxlPjwvQ2xpbmljYWxEb2N1bWVudD4='
        )
        obx.observation_result_status = 'D'

        # .. build PRT ..
        prt = PRT()
        prt.action_code = 'UC'
        prt.role_of_participation = CWE(cwe_1='SB', cwe_2='send by', cwe_3='participation')
        prt.person = XCN(xcn_1='20777888067', xcn_2='Lejeune', xcn_3='Marie-Claire', xcn_9='NIHDI&2.16.840.1.113883.3.6777.5.2&ISO', xcn_10='D', xcn_13='NIHDI')

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx
        observation.prt = prt

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CWE'
        obx_2.observation_identifier = CWE(cwe_1='MASQUE_PS', cwe_2='Masque aux professionnels de Sante', cwe_3='MetaDMPMSS')
        obx_2.obx_5 = 'N^^expandedYes-NoIndicator'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = MdmT02Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CWE'
        obx_3.observation_identifier = CWE(cwe_1='DESTDMP', cwe_2='Destinataire DMP', cwe_3='MetaDMPMSS')
        obx_3.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = MdmT02Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'CWE'
        obx_4.observation_identifier = CWE(cwe_1='DESTMSSANTEPS', cwe_2='Destinataire PS', cwe_3='MetaDMPMSS')
        obx_4.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = MdmT02Observation()
        observation_4.obx = obx_4

        # .. assemble the full message ..
        msg = MDM_T02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.txa = txa
        msg.observation = [observation, observation_2, observation_3, observation_4]

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
    """ Based on live/be/be-dxcare.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DXCARE')
        msh.sending_facility = HD(hd_1='CHR_NAMUR')
        msh.receiving_application = HD(hd_1='DMP_BE')
        msh.receiving_facility = HD(hd_1='EHEALTH_BE')
        msh.date_time_of_message = '20260510100000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T10', msg_3='MDM_T02')
        msh.message_control_id = 'MSG10011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.6')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T10'
        evn.recorded_date_time = '20260510100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT27512', cx_4='CHRN', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Gilles', xpn_2='Thierry', xpn_3='J', xpn_5='M.')
        pid.date_time_of_birth = '19701124'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rue de Fer 28', xad_3='Namur', xad_5='5000', xad_6='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MED-INT', pl_2='Consult-1', pl_3='1', pl_4='Medecine Interne')
        pv1.attending_doctor = XCN(xcn_1='20777888067', xcn_2='Lejeune', xcn_3='Marie-Claire', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='CR', cwe_2='Compte Rendu', cwe_3='L')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20260510095000'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20777888067', xcn_2='Lejeune', xcn_3='Marie-Claire', xcn_6='Dr.')
        txa.transcription_date_time = '20260510100000'
        txa.edit_date_time = 'ED'
        txa.originator_code_name = XCN(xcn_1='DOC-20260509-001')
        txa.txa_12 = '20777888067^Lejeune^Marie-Claire^^^Dr.'
        txa.unique_document_file_name = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='18748-4', cwe_2="CR d'imagerie medicale", cwe_3='LN')
        obx.obx_5 = (
            '^text^XML^Base64^'
            'PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIj48cmVsYXRlZERvY3VtZW50IHR5cGVDb2RlPSJSUExDIj48cGFyZW50RG9jdW1lbnQ+PGlkIHJvb3Q9IjEuMi4y'
            'NTAuMS4yMTMuMS4xLjEiLz48L3BhcmVudERvY3VtZW50PjwvcmVsYXRlZERvY3VtZW50Pjxjb21wb25lbnQ+PHNlY3Rpb24+PHRleHQ+VmVyc2lvbiBjb3JyaWdlZTwvdGV4dD48L3Nl'
            'Y3Rpb24+PC9jb21wb25lbnQ+PC9DbGluaWNhbERvY3VtZW50Pg=='
        )
        obx.observation_result_status = 'C'

        # .. build PRT ..
        prt = PRT()
        prt.action_code = 'UC'
        prt.role_of_participation = CWE(cwe_1='SB', cwe_2='Send by', cwe_3='participation')
        prt.person = XCN(xcn_1='20777888067', xcn_2='Lejeune', xcn_3='Marie-Claire', xcn_9='NIHDI&2.16.840.1.113883.3.6777.5.2&ISO', xcn_10='D', xcn_13='NIHDI')

        # .. build PRT ..
        prt_2 = PRT()
        prt_2.action_code = 'UC'
        prt_2.role_of_participation = CWE(cwe_1='RCT', cwe_2='Results Copies To', cwe_3='participation')
        prt_2.person = XCN(xcn_1='20888999078', xcn_2='Laurent', xcn_3='Bernard', xcn_9='NIHDI&2.16.840.1.113883.3.6777.5.2&ISO', xcn_10='D', xcn_13='NIHDI')

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx
        observation.prt = prt
        observation.prt_2 = prt_2

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CWE'
        obx_2.observation_identifier = CWE(cwe_1='MASQUE_PS', cwe_2='Masque aux professionnels de Sante', cwe_3='MetaDMPMSS')
        obx_2.obx_5 = 'N^^expandedYes-NoIndicator'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = MdmT02Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CWE'
        obx_3.observation_identifier = CWE(cwe_1='DESTDMP', cwe_2='Destinataire DMP', cwe_3='MetaDMPMSS')
        obx_3.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = MdmT02Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'CWE'
        obx_4.observation_identifier = CWE(cwe_1='DESTMSSANTEPS', cwe_2='Destinataire PS', cwe_3='MetaDMPMSS')
        obx_4.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = MdmT02Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'CWE'
        obx_5.observation_identifier = CWE(cwe_1='DESTMSSANTEPAT', cwe_2='Destinataire Patient', cwe_3='MetaDMPMSS')
        obx_5.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = MdmT02Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ED'
        obx_6.observation_identifier = CWE(cwe_1='CORPSMAIL_PS', cwe_2='Corps du mail pour un PS', cwe_3='MetaDMPMSS')
        obx_6.obx_5 = '^text^^Base64^Q2hlciBjb25mcmVyZSwgdm91cyB0cm91dmVyZXogY2ktam9pbnQgbGUgQ1IgY29ycmlnZSBkZSBNLkJvZGFydC4='
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = MdmT02Observation()
        observation_6.obx = obx_6

        # .. assemble the full message ..
        msg = MDM_T02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.txa = txa
        msg.observation = [observation, observation_2, observation_3, observation_4, observation_5, observation_6]

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
    """ Based on live/be/be-dxcare.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DXCARE')
        msh.sending_facility = HD(hd_1='CHU_ST_PIERRE')
        msh.receiving_application = HD(hd_1='PHARMA_BE')
        msh.receiving_facility = HD(hd_1='CHU_ST_PIERRE')
        msh.date_time_of_message = '20260509091000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MSG10012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT23012', cx_4='CHSP', cx_5='PI')
        pid.pid_4 = '86021534217^^^^NN'
        pid.patient_name = XPN(xpn_1='Dubois', xpn_2='Marc-Antoine', xpn_3='R', xpn_5='M.')
        pid.date_time_of_birth = '19860215'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rue du Midi 145', xad_3='Bruxelles', xad_5='1000', xad_6='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='Kamer 405', pl_3='Bed 2', pl_4='Cardiologie')
        pv1.pv1_7 = '20555666045^Van Damme^Frederik^^^Prof.^Dr.^med.'
        pv1.hospital_service = CWE(cwe_1='MED')

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
        orc.placer_order_number = EI(ei_1='ORD12201', ei_2='DXCARE')
        orc.filler_order_number = EI(ei_1='FIL23101', ei_2='PHARMA_BE')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20260509091000^^R'
        orc.date_time_of_order_event = '20260509091000'
        orc.orc_10 = '20555666045^Van Damme^Frederik^^^Prof.^Dr.^med.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD12201', ei_2='DXCARE')
        obr.filler_order_number = EI(ei_1='FIL23101', ei_2='PHARMA_BE')
        obr.universal_service_identifier = CWE(cwe_1='METOP', cwe_2='METOPROLOL 50MG', cwe_3='LOCAL')
        obr.obr_5 = 'R'
        obr.obr_6 = '20260509090000'
        obr.relevant_clinical_information = CWE(cwe_1='20555666045', cwe_2='Van Damme', cwe_3='Frederik', cwe_6='Prof.', cwe_7='Dr.', cwe_8='med.')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='METOP50', cwe_2='METOPROLOL TARTRATE 50MG', cwe_3='LOCAL')
        rxo.requested_give_amount_maximum = '50'
        rxo.requested_give_units = CWE(cwe_1='MG')
        rxo.requested_dosage_form = CWE(cwe_1='TAB', cwe_2='TABLET', cwe_3='HL70292')
        rxo.requested_dispense_amount = '1'
        rxo.requested_dispense_units = CWE(cwe_1='2x per dag')

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [rxo]

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
    """ Based on live/be/be-dxcare.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DXCARE')
        msh.sending_facility = HD(hd_1='AZ_MONICA')
        msh.receiving_application = HD(hd_1='AGENDA_BE')
        msh.receiving_facility = HD(hd_1='AZ_MONICA')
        msh.date_time_of_message = '20260509103000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12')
        msh.message_control_id = 'MSG10013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT55001', ei_2='DXCARE')
        sch.filler_appointment_id = EI(ei_1='APT55001', ei_2='AGENDA_BE')
        sch.appointment_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine afspraak', cwe_3='HL70276')
        sch.appointment_type = CWE(cwe_1='30', cwe_2='MIN')
        sch.sch_9 = '^^MIN'
        sch.appointment_duration_units = CNE(cne_2='Gastroscopie controle')
        sch.placer_contact_address = XAD(xad_1='20333444023', xad_2='Wouters', xad_3='Katrien', xad_6='Dr.')
        sch.sch_17 = '20333444023^Wouters^Katrien^^^Dr.'
        sch.filler_contact_location = PL(pl_1='BOOKED')
        sch.sch_20 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT24212', cx_4='AZM', cx_5='PI')
        pid.pid_4 = '92041267834^^^^NN'
        pid.patient_name = XPN(xpn_1='Goossens', xpn_2='Lien', xpn_3='M', xpn_5='Mevr.')
        pid.date_time_of_birth = '19920412'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Plantin en Moretuslei 66', xad_3='Berchem', xad_5='2600', xad_6='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ENDO', pl_2='Zaal-1', pl_3='1', pl_4='Endoscopie')
        pv1.attending_doctor = XCN(xcn_1='20333444023', xcn_2='Wouters', xcn_3='Katrien', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')

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
        ais.universal_service_identifier = CWE(cwe_1='GASTRO', cwe_2='Gastroscopie', cwe_3='LOCAL')
        ais.start_date_time = '20260520100000'
        ais.duration = '30^MIN'

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='ENDO', pl_2='Zaal-1', pl_3='1', pl_4='Endoscopie')

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='20333444023', xcn_2='Wouters', xcn_3='Katrien', xcn_6='Dr.')

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
    """ Based on live/be/be-dxcare.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DXCARE')
        msh.sending_facility = HD(hd_1='AZ_MONICA')
        msh.receiving_application = HD(hd_1='AGENDA_BE')
        msh.receiving_facility = HD(hd_1='AZ_MONICA')
        msh.date_time_of_message = '20260512083000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S15')
        msh.message_control_id = 'MSG10014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT55001', ei_2='DXCARE')
        sch.filler_appointment_id = EI(ei_1='APT55001', ei_2='AGENDA_BE')
        sch.appointment_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine afspraak', cwe_3='HL70276')
        sch.appointment_type = CWE(cwe_1='30', cwe_2='MIN')
        sch.sch_9 = '^^MIN'
        sch.appointment_duration_units = CNE(cne_2='Gastroscopie controle')
        sch.placer_contact_address = XAD(xad_1='20333444023', xad_2='Wouters', xad_3='Katrien', xad_6='Dr.')
        sch.sch_17 = '20333444023^Wouters^Katrien^^^Dr.'
        sch.filler_contact_location = PL(pl_1='CANCELLED')
        sch.sch_20 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT24212', cx_4='AZM', cx_5='PI')
        pid.pid_4 = '92041267834^^^^NN'
        pid.patient_name = XPN(xpn_1='Goossens', xpn_2='Lien', xpn_3='M', xpn_5='Mevr.')
        pid.date_time_of_birth = '19920412'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Plantin en Moretuslei 66', xad_3='Berchem', xad_5='2600', xad_6='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ENDO', pl_2='Zaal-1', pl_3='1', pl_4='Endoscopie')
        pv1.attending_doctor = XCN(xcn_1='20333444023', xcn_2='Wouters', xcn_3='Katrien', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
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
    """ Based on live/be/be-dxcare.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABO_BE')
        msh.sending_facility = HD(hd_1='CHU_LIEGE')
        msh.receiving_application = HD(hd_1='DXCARE')
        msh.receiving_facility = HD(hd_1='CHU_LIEGE')
        msh.date_time_of_message = '20260509170000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MSG10015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT25312', cx_4='CHUL', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Marchand', xpn_2='Olivier', xpn_3='V', xpn_5='M.')
        pid.date_time_of_birth = '19790928'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1="Boulevard d'Avroy 33", xad_3='Liege', xad_5='4000', xad_6='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED-INT', pl_2='Kamer 512', pl_3='Bed 1', pl_4='Interne Geneeskunde')
        pv1.attending_doctor = XCN(xcn_1='20444555034', xcn_2='Simon', xcn_3='Christophe', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')

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
        orc.placer_order_number = EI(ei_1='ORD13301', ei_2='DXCARE')
        orc.filler_order_number = EI(ei_1='FIL24201', ei_2='LABO_BE')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD13301', ei_2='DXCARE')
        obr.filler_order_number = EI(ei_1='FIL24201', ei_2='LABO_BE')
        obr.universal_service_identifier = CWE(cwe_1='87040', cwe_2='URINEKWEEK', cwe_3='CPT4')
        obr.obr_16 = '20999000089^Renard^Sylvie^^^Dr.'
        obr.results_rpt_status_chng_date_time = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='11475-1', cwe_2='MICRO-ORGANISME', cwe_3='LN')
        obx.obx_5 = 'Escherichia coli'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='30004-6', cwe_2='KIEMGETAL', cwe_3='LN')
        obx_2.obx_5 = '100000'
        obx_2.units = CWE(cwe_1='CFU/mL')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18907-6', cwe_2='AMOXICILLINE', cwe_3='LN')
        obx_3.obx_5 = 'R'
        obx_3.interpretation_codes = CWE(cwe_1='R')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18908-4', cwe_2='AMOXICILLINE-CLAVULAANZUUR', cwe_3='LN')
        obx_4.obx_5 = 'S'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18928-2', cwe_2='CIPROFLOXACINE', cwe_3='LN')
        obx_5.obx_5 = 'S'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='18932-4', cwe_2='COTRIMOXAZOL', cwe_3='LN')
        obx_6.obx_5 = 'R'
        obx_6.interpretation_codes = CWE(cwe_1='R')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='18964-7', cwe_2='NITROFURANTOINE', cwe_3='LN')
        obx_7.obx_5 = 'S'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

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
    """ Based on live/be/be-dxcare.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PATHOLOGIE')
        msh.sending_facility = HD(hd_1='CHU_ST_PIERRE')
        msh.receiving_application = HD(hd_1='DXCARE')
        msh.receiving_facility = HD(hd_1='CHU_ST_PIERRE')
        msh.date_time_of_message = '20260512140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MSG10016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT28612', cx_4='CHSP', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Moreau', xpn_2='Caroline', xpn_3='T', xpn_5='Mevr.')
        pid.date_time_of_birth = '19830517'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Chaussee de Charleroi 99', xad_3='Saint-Gilles', xad_5='1060', xad_6='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='Kamer 210', pl_3='Bed 1', pl_4='Chirurgie')
        pv1.pv1_7 = '21000111090^Claes^Dirk^^^Prof.^Dr.'
        pv1.hospital_service = CWE(cwe_1='CHIR')

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
        orc.placer_order_number = EI(ei_1='ORD14401', ei_2='DXCARE')
        orc.filler_order_number = EI(ei_1='FIL25301', ei_2='PATHOLOGIE')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD14401', ei_2='DXCARE')
        obr.filler_order_number = EI(ei_1='FIL25301', ei_2='PATHOLOGIE')
        obr.universal_service_identifier = CWE(cwe_1='88305', cwe_2='PATHOLOGISCH ONDERZOEK WEEFSEL', cwe_3='CPT4')
        obr.obr_16 = '21111222001^Lambert^Helene^^^Dr.'
        obr.results_rpt_status_chng_date_time = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='22637-3', cwe_2='PATHOLOGIE VERSLAG', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            'Macroscopie: Excisiebiopt rechter borst, 2.1 x 1.8 x 1.5 cm.\\.br\\Microscopie: Invasief ductaal carcinoom, graad 2 (Bloom-Richardson score 6/'
            '9). Tumorgrootte 14mm. Snijranden vrij (minimale marge 3mm). Geen lymfovasculaire invasie.\\.br\\Conclusie: pT1c invasief ductaal carcinoom gr'
            'aad 2, snijranden vrij.'
        )
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='85319-2', cwe_2='HORMOONRECEPTOR ER', cwe_3='LN')
        obx_2.obx_5 = 'POS^Positief 90%^LOCAL'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='85337-4', cwe_2='HORMOONRECEPTOR PR', cwe_3='LN')
        obx_3.obx_5 = 'POS^Positief 70%^LOCAL'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'CE'
        obx_4.observation_identifier = CWE(cwe_1='85318-4', cwe_2='HER2 STATUS', cwe_3='LN')
        obx_4.obx_5 = 'NEG^Negatief (IHC 1+)^LOCAL'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='85336-6', cwe_2='KI67 INDEX', cwe_3='LN')
        obx_5.obx_5 = '15'
        obx_5.units = CWE(cwe_1='%')
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
    """ Based on live/be/be-dxcare.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DXCARE')
        msh.sending_facility = HD(hd_1='UZ_BRUSSEL')
        msh.receiving_application = HD(hd_1='RISONWEB')
        msh.receiving_facility = HD(hd_1='UZ_BRUSSEL')
        msh.date_time_of_message = '20260509104500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MSG10017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT29712', cx_4='UZB', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Coppens', xpn_2='Thomas', xpn_3='D', xpn_5='Dhr.')
        pid.date_time_of_birth = '19850719'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Boulevard de Smet de Nayer 44', xad_3='Laeken', xad_5='1020', xad_6='BE')
        pid.pid_13 = '^^PH^02-588-5222'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ORTHO', pl_2='Consult-2', pl_3='1', pl_4='Orthopedie')
        pv1.attending_doctor = XCN(xcn_1='21222333012', xcn_2='Peeters', xcn_3='Stefan', xcn_6='Dr.')
        pv1.hospital_service = CWE(cwe_1='MED')

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
        orc.placer_order_number = EI(ei_1='ORD15501', ei_2='DXCARE')
        orc.filler_order_number = EI(ei_1='FIL26401', ei_2='RISONWEB')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20260509104500^^R'
        orc.date_time_of_order_event = '20260509104500'
        orc.orc_10 = '21222333012^Peeters^Stefan^^^Dr.'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD15501', ei_2='DXCARE')
        obr.filler_order_number = EI(ei_1='FIL26401', ei_2='RISONWEB')
        obr.universal_service_identifier = CWE(cwe_1='73630', cwe_2='RX VOET 3 OPNAMES', cwe_3='CPT4')
        obr.obr_5 = 'R'
        obr.obr_6 = '20260509103000'
        obr.relevant_clinical_information = CWE(cwe_1='21222333012', cwe_2='Peeters', cwe_3='Stefan', cwe_6='Dr.')
        obr.obr_16 = 'Chronische pijn voorvoet, uitsluiten stressfractuur'
        obr.placer_field_1 = 'CR'
        obr.placer_field_2 = 'SC'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'ICD10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M79.67', cwe_2='Pijn voet', cwe_3='ICD10')
        dg1.diagnosis_date_time = '20260509'

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
    """ Based on live/be/be-dxcare.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DXCARE')
        msh.sending_facility = HD(hd_1='AZ_DELTA')
        msh.receiving_application = HD(hd_1='MPI_BE')
        msh.receiving_facility = HD(hd_1='AZ_DELTA')
        msh.date_time_of_message = '20260509070000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'MSG10018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20260509070000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT30812', cx_4='AZD', cx_5='PI')
        pid.pid_4 = '97122078345^^^^NN'
        pid.patient_name = XPN(xpn_1='Bogaert', xpn_2='Emma', xpn_3='H', xpn_5='Mevr.')
        pid.date_time_of_birth = '19971220'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Brugsesteenweg 77', xad_3='Roeselare', xad_5='8800', xad_6='BE')
        pid.pid_13 = '^^PH^051-456789~^^CP^0498-223344~^^Internet^emma.bogaert@outlook.be'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'AZ DELTA^^AZD'

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1

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
    """ Based on live/be/be-dxcare.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DXCARE')
        msh.sending_facility = HD(hd_1='AZ_DELTA')
        msh.receiving_application = HD(hd_1='MPI_BE')
        msh.receiving_facility = HD(hd_1='AZ_DELTA')
        msh.date_time_of_message = '20260509113000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'MSG10019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20260509113000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT30812', cx_4='AZD', cx_5='PI')
        pid.pid_4 = '97122078345^^^^NN'
        pid.patient_name = XPN(xpn_1='Bogaert-Peeters', xpn_2='Emma', xpn_3='H', xpn_5='Mevr.')
        pid.date_time_of_birth = '19971220'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Mandellaan 14', xad_3='Roeselare', xad_5='8800', xad_6='BE')
        pid.pid_13 = '^^PH^051-456789~^^CP^0498-223344~^^Internet^emma.bogaert@outlook.be'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'AZ DELTA^^AZD'

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1

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
    """ Based on live/be/be-dxcare.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DXCARE')
        msh.sending_facility = HD(hd_1='CHU_ST_PIERRE')
        msh.receiving_application = HD(hd_1='DMP_BE')
        msh.receiving_facility = HD(hd_1='EHEALTH_BE')
        msh.date_time_of_message = '20260515160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG10020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT23012', cx_4='CHSP', cx_5='PI')
        pid.pid_4 = '86021534217^^^^NN'
        pid.patient_name = XPN(xpn_1='Dubois', xpn_2='Marc-Antoine', xpn_3='R', xpn_5='M.')
        pid.date_time_of_birth = '19860215'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Rue du Midi 145', xad_3='Bruxelles', xad_5='1000', xad_6='BE')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARDIO', pl_2='Kamer 405', pl_3='Bed 2', pl_4='Cardiologie')
        pv1.pv1_7 = '20555666045^Van Damme^Frederik^^^Prof.^Dr.^med.'
        pv1.hospital_service = CWE(cwe_1='MED')

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
        orc.placer_order_number = EI(ei_1='ORD16601', ei_2='DXCARE')
        orc.filler_order_number = EI(ei_1='FIL27501', ei_2='DMP_BE')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD16601', ei_2='DXCARE')
        obr.filler_order_number = EI(ei_1='FIL27501', ei_2='DMP_BE')
        obr.universal_service_identifier = CWE(cwe_1='34133-9', cwe_2='Lettre de sortie', cwe_3='LN')
        obr.obr_16 = '20555666045^Van Damme^Frederik^^^Prof.^Dr.^med.'
        obr.results_rpt_status_chng_date_time = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='34133-9', cwe_2='Lettre de sortie', cwe_3='LN')
        obx.obx_5 = (
            '^TEXT^XML^Base64^'
            'PENsaW5pY2FsRG9jdW1lbnQgeG1sbnM9InVybjpobDctb3JnOnYzIj48dGl0bGU+TGV0dHJlIGRlIHNvcnRpZSAtIENhcmRpb2xvZ2llPC90aXRsZT48Y29tcG9uZW50PjxzZWN0aW9u'
            'Pjx0ZXh0PlBhdGllbnQgc29ydGkgYXByZXMgYW5naW9wbGFzdGllIGNvcm9uYWlyZS4gVHJhaXRlbWVudDogQXNwaXJpbmUgMTAwbWcsIENsb3BpZG9ncmVsIDc1bWcsIEF0b3J2YXN0'
            'YXRpbmUgNDBtZy48L3RleHQ+PC9zZWN0aW9uPjwvY29tcG9uZW50PjwvQ2xpbmljYWxEb2N1bWVudD4='
        )
        obx.observation_result_status = 'C'

        # .. build PRT ..
        prt = PRT()
        prt.action_code = 'UC'
        prt.role_of_participation = CWE(cwe_1='SB', cwe_2='Send by', cwe_3='participation')
        prt.person = XCN(xcn_1='20555666045', xcn_2='Van Damme', xcn_3='Frederik', xcn_9='NIHDI&2.16.840.1.113883.3.6777.5.2&ISO', xcn_10='D', xcn_13='NIHDI')
        prt.organization = XON(xon_1='CHU Saint-Pierre', xon_6='NIHDI-ST&2.16.840.1.113883.3.6777.5.2&ISO', xon_7='FINEG', xon_10='71000436')

        # .. build PRT ..
        prt_2 = PRT()
        prt_2.action_code = 'UC'
        prt_2.role_of_participation = CWE(cwe_1='RCT', cwe_2='Results Copies To', cwe_3='participation')
        prt_2.person = XCN(xcn_1='20888999078', xcn_2='Laurent', xcn_3='Bernard', xcn_9='NIHDI&2.16.840.1.113883.3.6777.5.2&ISO', xcn_10='D', xcn_13='NIHDI')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx
        observation.prt = prt
        observation.prt_2 = prt_2

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='MASQUE_PS', cwe_2='Masque aux professionnels de Sante', cwe_3='MetaDMPMSS')
        obx_2.obx_5 = 'N^^expandedYes-NoIndicator'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='INVISIBLE_PATIENT', cwe_2='Document Non Visible par le patient', cwe_3='MetaDMPMSS')
        obx_3.obx_5 = 'N^^expandedYes-NoIndicator'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'CE'
        obx_4.observation_identifier = CWE(cwe_1='MODIF_CONF_CODE', cwe_2='Modification Confidentiality Code', cwe_3='MetaDMPMSS')
        obx_4.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'CE'
        obx_5.observation_identifier = CWE(cwe_1='DESTDMP', cwe_2='Destinataire DMP', cwe_3='MetaDMPMSS')
        obx_5.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'CE'
        obx_6.observation_identifier = CWE(cwe_1='DESTMSSANTEPS', cwe_2='Destinataire PS', cwe_3='MetaDMPMSS')
        obx_6.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'CE'
        obx_7.observation_identifier = CWE(cwe_1='DESTMSSANTEPAT', cwe_2='Destinataire Patient', cwe_3='MetaDMPMSS')
        obx_7.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'CE'
        obx_8.observation_identifier = CWE(cwe_1='ACK_RECEPTION', cwe_2='Accuse de reception', cwe_3='MetaDMPMSS')
        obx_8.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'CE'
        obx_9.observation_identifier = CWE(cwe_1='ACK_LECTURE', cwe_2='Accuse de lecture', cwe_3='MetaDMPMSS')
        obx_9.obx_5 = 'Y^^expandedYes-NoIndicator'
        obx_9.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

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
        order_observation.observation_9 = observation_9

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
