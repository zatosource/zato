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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, EI, HD, MOC, MSG, PL, PRL, PT, VID, XAD, XCN, XON, XPN, XTN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, AdtA03Insurance, AdtA03Procedure, AdtA05Insurance, AdtA05NextOfKin, AdtA39Patient, \
    MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, \
    OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12LocationResource, SiuS12Patient, SiuS12PersonnelResource, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, DG1, EVN, IN1, MRG, MSA, MSH, NK1, OBR, OBX, ORC, PD1, PID, PR1, PV1, PV2, RGS, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('cz', 'cz-siemens-ehealth.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/cz/cz-siemens-ehealth.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIEMENS_EHA')
        msh.sending_facility = HD(hd_1='FNKV_PRAHA')
        msh.receiving_application = HD(hd_1='NIS_FNKV')
        msh.receiving_facility = HD(hd_1='FNKV_PRAHA')
        msh.date_time_of_message = '20250305081000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'SE20250305081000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250305081000'
        evn.operator_id = XCN(xcn_1='PRIJEM01', xcn_2='Fialová', xcn_3='Ivana', xcn_6='Bc.')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5105130320', cx_4='SEHA', cx_5='RC'), CX(cx_1='FNKV12018091', cx_4='FNKV', cx_5='MRN')]
        pid.pid_5 = 'BOUŠKA^Matěj^Jakub^^^'
        pid.date_time_of_birth = '19510513'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Moskevská 156', xad_3='Třebíč', xad_4='CZ', xad_5='67401', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^759870145~^NET^Internet^matej.bouska@email.cz'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '5105130320'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'FN KRÁLOVSKÉ VINOHRADY^^10234'
        pd1.pd1_4 = '9539719584^Holub^Filip^Cyril^^MUDr.^^^IČP'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='BOUŠKOVÁ', xpn_2='Helena', xpn_3='Pavla')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Moskevská 156', xad_3='Třebíč', xad_4='CZ', xad_5='67401', xad_6='CZ')
        nk1.nk1_5 = '^PRN^PH^^^420^759870145'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NCHIR1', pl_2='301', pl_3='A', pl_4='FNKV_PRAHA', pl_8='NCHIR1')
        pv1.attending_doctor = XCN(xcn_1='9539719584', xcn_2='Holub', xcn_3='Filip', xcn_4='Cyril', xcn_6='MUDr.', xcn_9='IČP')
        pv1.referring_doctor = XCN(xcn_1='6420671037', xcn_2='Veselý', xcn_3='Daniel', xcn_4='Josef', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='NCHI', xcn_2='Neurochirurgie', xcn_3='SEHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V10023456', xcn_4='FNKVENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250305081000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Hernie meziobratlové ploténky bederní', cwe_3='M51.1')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='111', cwe_2='VZP', cwe_4='VZP')
        in1.insurance_company_id = CX(cx_1='111')
        in1.insurance_company_name = XON(xon_1='VŠEOBECNÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Orlická 4', xad_3='Praha 3', xad_4='CZ', xad_5='13000', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^952222222'
        in1.assignment_of_benefits = CWE(cwe_1='BOUŠKA', cwe_2='Matěj', cwe_3='Jakub')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '19510513'
        in1.notice_of_admission_flag = 'Moskevská 156^^Třebíč^CZ^67401^CZ'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.pv2 = pv2
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
    """ Based on live/cz/cz-siemens-ehealth.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIEMENS_EHA')
        msh.sending_facility = HD(hd_1='NEM_ZNOJMO')
        msh.receiving_application = HD(hd_1='AMBSYS')
        msh.receiving_facility = HD(hd_1='NEM_ZNOJMO')
        msh.date_time_of_message = '20250420092000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'SE20250420092000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250420092000'
        evn.operator_id = XCN(xcn_1='PRIJEM02', xcn_2='Doležal', xcn_3='Lukáš', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='9205215693', cx_4='SEHA', cx_5='RC'), CX(cx_1='ZN58357166', cx_4='NEMZN', cx_5='MRN')]
        pid.pid_5 = 'FIALA^Lukáš^Antonín^^^'
        pid.date_time_of_birth = '19920521'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Budějovická 131', xad_3='Plzeň', xad_4='CZ', xad_5='30100', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^754516476~^NET^Internet^lukas.fiala@email.cz'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '9205215693'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'NEMOCNICE ZNOJMO^^20345'
        pd1.pd1_4 = '7899412720^Brožová^Věra^Jaroslava^^MUDr.^^^IČP'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='FIALOVÁ', xpn_2='Marie', xpn_3='Eva')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Mother', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Budějovická 131', xad_3='Plzeň', xad_4='CZ', xad_5='30100', xad_6='CZ')
        nk1.nk1_5 = '^PRN^PH^^^420^754516476'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB1', pl_2='ORD01', pl_3='A', pl_4='NEM_ZNOJMO', pl_8='AMB1')
        pv1.attending_doctor = XCN(xcn_1='7899412720', xcn_2='Brožová', xcn_3='Věra', xcn_4='Jaroslava', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='ORL', xcn_2='ORL', xcn_3='SEHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V20034567', xcn_4='ZNENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250420092000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='205', cwe_2='ČPZP', cwe_4='CPZP')
        in1.insurance_company_id = CX(cx_1='205')
        in1.insurance_company_name = XON(xon_1='ČESKÁ PRŮMYSLOVÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Jeremenkova 11', xad_3='Ostrava', xad_4='CZ', xad_5='70300', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^596256511'
        in1.assignment_of_benefits = CWE(cwe_1='FIALA', cwe_2='Lukáš', cwe_3='Antonín')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '19920521'
        in1.notice_of_admission_flag = 'Budějovická 131^^Plzeň^CZ^30100^CZ'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.insurance = insurance

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
    """ Based on live/cz/cz-siemens-ehealth.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIEMENS_EHA')
        msh.sending_facility = HD(hd_1='FNKV_PRAHA')
        msh.receiving_application = HD(hd_1='DISCHARGE')
        msh.receiving_facility = HD(hd_1='FNKV_PRAHA')
        msh.date_time_of_message = '20250312153000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'SE20250312153000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20250312153000'
        evn.operator_id = XCN(xcn_1='SESTRA01', xcn_2='Holubová', xcn_3='Renata', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5105130320', cx_4='SEHA', cx_5='RC'), CX(cx_1='FNKV12018091', cx_4='FNKV', cx_5='MRN')]
        pid.pid_5 = 'BOUŠKA^Matěj^Jakub^^^'
        pid.date_time_of_birth = '19510513'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Moskevská 156', xad_3='Třebíč', xad_4='CZ', xad_5='67401', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^759870145'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '5105130320'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NCHIR1', pl_2='301', pl_3='A', pl_4='FNKV_PRAHA', pl_8='NCHIR1')
        pv1.attending_doctor = XCN(xcn_1='9539719584', xcn_2='Holub', xcn_3='Filip', xcn_4='Cyril', xcn_6='MUDr.', xcn_9='IČP')
        pv1.referring_doctor = XCN(xcn_1='6420671037', xcn_2='Veselý', xcn_3='Daniel', xcn_4='Josef', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='NCHI', xcn_2='Neurochirurgie', xcn_3='SEHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V10023456', xcn_4='FNKVENC', xcn_5='VN')
        pv1.visit_number = CX(cx_1='DO', cx_2='Discharged to Home', cx_3='HL70112')
        pv1.prior_temporary_location = PL(pl_1='20250305081000')
        pv1.admit_date_time = '20250312153000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M51.1', cwe_2='Hernie meziobratlové ploténky bederní', cwe_3='MKN10')
        dg1.diagnosis_date_time = '20250305'
        dg1.diagnosis_type = CWE(cwe_1='A', cwe_2='Admitting', cwe_3='HL70052')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='M51.1', cwe_2='Hernie meziobratlové ploténky bederní', cwe_3='MKN10')
        dg1_2.diagnosis_date_time = '20250312'
        dg1_2.diagnosis_type = CWE(cwe_1='F', cwe_2='Final', cwe_3='HL70052')

        # .. build PR1 ..
        pr1 = PR1()
        pr1.set_id_pr1 = '1'
        pr1.procedure_code = CNE(cne_1='03.09', cne_2='Dekompresní laminektomie', cne_3='MKN10PCS')
        pr1.pr1_4 = 'Dekompresní laminektomie L4-L5'
        pr1.procedure_date_time = '20250307080000'
        pr1.pr1_12 = '9539719584^Holub^Filip^Cyril^^MUDr.^^^IČP'

        # .. build the PROCEDURE group ..
        procedure = AdtA03Procedure()
        procedure.pr1 = pr1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='111', cwe_2='VZP', cwe_4='VZP')
        in1.insurance_company_id = CX(cx_1='111')
        in1.insurance_company_name = XON(xon_1='VŠEOBECNÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Orlická 4', xad_3='Praha 3', xad_4='CZ', xad_5='13000', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^952222222'
        in1.assignment_of_benefits = CWE(cwe_1='BOUŠKA', cwe_2='Matěj', cwe_3='Jakub')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '19510513'
        in1.notice_of_admission_flag = 'Moskevská 156^^Třebíč^CZ^67401^CZ'

        # .. build the INSURANCE group ..
        insurance = AdtA03Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = [dg1, dg1_2]
        msg.procedure = procedure
        msg.insurance = insurance

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
    """ Based on live/cz/cz-siemens-ehealth.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIEMENS_EHA')
        msh.sending_facility = HD(hd_1='NEM_TREBIC')
        msh.receiving_application = HD(hd_1='MPI_TR')
        msh.receiving_facility = HD(hd_1='NEM_TREBIC')
        msh.date_time_of_message = '20250530140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'SE20250530140000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20250530140000'
        evn.operator_id = XCN(xcn_1='ADMIN01', xcn_2='Sedláčková', xcn_3='Zdeňka', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='7805137765', cx_4='SEHA', cx_5='RC'), CX(cx_1='TR08031480', cx_4='NEMTR', cx_5='MRN')]
        pid.pid_5 = 'RYBA^Štěpán^Ondřej^^^'
        pid.date_time_of_birth = '19780513'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Moskevská 88', xad_3='Třebíč', xad_4='CZ', xad_5='67401', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^624040318~^NET^Internet^stepan.ryba@email.cz'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '7805137765'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'NEMOCNICE TŘEBÍČ^^30456'
        pd1.pd1_4 = '6624496920^Konečná^Marie^Dana^^MUDr.^^^IČP'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='RYBOVÁ', xpn_2='Kateřina', xpn_3='Věra')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Moskevská 88', xad_3='Třebíč', xad_4='CZ', xad_5='67401', xad_6='CZ')
        nk1.nk1_5 = '^PRN^PH^^^420^624040318'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB2', pl_2='ORD03', pl_3='A', pl_4='NEM_TREBIC', pl_8='AMB2')
        pv1.attending_doctor = XCN(xcn_1='6624496920', xcn_2='Konečná', xcn_3='Marie', xcn_4='Dana', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='SEHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V30045678', xcn_4='TRENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250530140000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='207', cwe_2='OZP', cwe_4='OZP')
        in1.insurance_company_id = CX(cx_1='207')
        in1.insurance_company_name = XON(xon_1='OBOROVÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Roškotova 1225/1', xad_3='Praha 4', xad_4='CZ', xad_5='14000', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^261105555'
        in1.assignment_of_benefits = CWE(cwe_1='RYBA', cwe_2='Štěpán', cwe_3='Ondřej')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '19780513'
        in1.notice_of_admission_flag = 'Moskevská 88^^Třebíč^CZ^67401^CZ'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.insurance = insurance

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
    """ Based on live/cz/cz-siemens-ehealth.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIEMENS_EHA')
        msh.sending_facility = HD(hd_1='FN_PLZEN')
        msh.receiving_application = HD(hd_1='RADRIS')
        msh.receiving_facility = HD(hd_1='FN_PLZEN')
        msh.date_time_of_message = '20250410091500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SE20250410091500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5310210451', cx_4='SEHA', cx_5='RC'), CX(cx_1='PL55321890', cx_4='FNPLZ', cx_5='MRN')]
        pid.pid_5 = 'POSPÍŠIL^Josef^Vladimír^^^'
        pid.date_time_of_birth = '19531021'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Pražská 185', xad_3='Karlovy Vary', xad_4='CZ', xad_5='36001', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^629876939'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '5310210451'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NCHIR2', pl_2='402', pl_3='A', pl_4='FN_PLZEN', pl_8='NCHIR2')
        pv1.attending_doctor = XCN(xcn_1='6415106958', xcn_2='Král', xcn_3='Vojtěch', xcn_4='Bedřich', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='NCHI', xcn_2='Neurochirurgie', xcn_3='SEHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V40056789', xcn_4='PLZENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250409080000')

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
        orc.placer_order_number = EI(ei_1='ORD101234', ei_2='SEHA')
        orc.filler_order_number = EI(ei_1='RAD201234', ei_2='RADRIS')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250410100000^^R'
        orc.date_time_of_order_event = '20250410091500'
        orc.orc_10 = 'BARTATJ^Veselý^Josef^^^'
        orc.order_control_code_reason = CWE(cwe_1='FN_PLZEN')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD101234', ei_2='SEHA')
        obr.filler_order_number = EI(ei_1='RAD201234', ei_2='RADRIS')
        obr.universal_service_identifier = CWE(cwe_1='70553', cwe_2='MRI mozku s kontrastem', cwe_3='CPT')
        obr.obr_16 = '6415106958^Král^Vojtěch^Bedřich^^MUDr.^^^IČP'
        obr.results_rpt_status_chng_date_time = '20250410100000'
        obr.result_status = 'NI^No Information^HL70507'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='C71.9', cwe_2='Zhoubný novotvar mozku, neurčený', cwe_3='MKN10')
        dg1.diagnosis_date_time = '20250409'
        dg1.diagnosis_type = CWE(cwe_1='W', cwe_2='Working', cwe_3='HL70052')

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
    """ Based on live/cz/cz-siemens-ehealth.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIEMENS_EHA')
        msh.sending_facility = HD(hd_1='FN_PLZEN')
        msh.receiving_application = HD(hd_1='NIS_PLZEN')
        msh.receiving_facility = HD(hd_1='FN_PLZEN')
        msh.date_time_of_message = '20250411150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SE20250411150000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5310210451', cx_4='SEHA', cx_5='RC'), CX(cx_1='PL55321890', cx_4='FNPLZ', cx_5='MRN')]
        pid.pid_5 = 'POSPÍŠIL^Josef^Vladimír^^^'
        pid.date_time_of_birth = '19531021'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Pražská 185', xad_3='Karlovy Vary', xad_4='CZ', xad_5='36001', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^629876939'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '5310210451'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NCHIR2', pl_2='402', pl_3='A', pl_4='FN_PLZEN', pl_8='NCHIR2')
        pv1.attending_doctor = XCN(xcn_1='6415106958', xcn_2='Král', xcn_3='Vojtěch', xcn_4='Bedřich', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='NCHI', xcn_2='Neurochirurgie', xcn_3='SEHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V40056789', xcn_4='PLZENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250409080000')

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
        orc.placer_order_number = EI(ei_1='ORD101234', ei_2='SEHA')
        orc.filler_order_number = EI(ei_1='RAD201234', ei_2='RADRIS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250410100000^^R'
        orc.date_time_of_order_event = '20250411150000'
        orc.orc_18 = 'FN_PLZEN'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD101234', ei_2='SEHA')
        obr.filler_order_number = EI(ei_1='RAD201234', ei_2='RADRIS')
        obr.universal_service_identifier = CWE(cwe_1='70553', cwe_2='MRI mozku s kontrastem', cwe_3='CPT')
        obr.observation_date_time = '20250410100500'
        obr.obr_17 = '6415106958^Král^Vojtěch^Bedřich^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250411150000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='18782-3', cwe_2='Radiologický nález', cwe_3='LN')
        obx.obx_5 = (
            'MRI mozku s kontrastem - ložisková léze frontálního laloku vlevo, vel. 28x22 mm, prstencovité sycení kontrastem, perifokální edém. Suspektní'
            ' gliom vysokého stupně.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250411140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='11502-2', cwe_2='Laboratorní zpráva', cwe_3='LN')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoK'
            'PDwgL0xlbmd0aCA1MCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKExhYm9yYXRvcm5pIHpwcmF2YSkgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAw'
            'MDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA3NCAwMDAwMCBuIAowMDAwMDAwMTQyIDAwMDAwIG4gCjAwMDAwMDAyNDIgMDAwMDAgbiAKdHJhaWxlcgo8'
            'PCAvU2l6ZSA1IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozNDIKJSVFT0YK'
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
    """ Based on live/cz/cz-siemens-ehealth.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIEMENS_EHA')
        msh.sending_facility = HD(hd_1='NEM_ZNOJMO')
        msh.receiving_application = HD(hd_1='SCHEDMGR')
        msh.receiving_facility = HD(hd_1='NEM_ZNOJMO')
        msh.date_time_of_message = '20250425080000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'SE20250425080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='SCH30034567', ei_2='SEHA')
        sch.appointment_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine', cwe_3='HL70276')
        sch.appointment_type = CWE(cwe_1='20', cwe_2='min')
        sch.sch_9 = 'MIN^^ISO+'
        sch.placer_contact_person = XCN(xcn_1='RECEPCE', xcn_2='Krejčí', xcn_3='Věra', xcn_6='')
        sch.placer_contact_phone_number = XTN(xtn_2='PRN', xtn_3='PH', xtn_6='420', xtn_7='515345678')
        sch.filler_contact_address = XAD(xad_1='7899412720', xad_2='Brožová', xad_3='Věra', xad_4='Jaroslava', xad_6='MUDr.', xad_9='IČP')
        sch.filler_contact_location = PL(pl_2='PRN', pl_3='PH', pl_6='420', pl_7='515123456')
        sch.entered_by_person = XCN(xcn_1='NEMOCNICE ZNOJMO')
        sch.entered_by_location = PL(pl_1='BOOKED', pl_2='Booked', pl_3='HL70278')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='9205215693', cx_4='SEHA', cx_5='RC'), CX(cx_1='ZN58357166', cx_4='NEMZN', cx_5='MRN')]
        pid.pid_5 = 'FIALA^Lukáš^Antonín^^^'
        pid.date_time_of_birth = '19920521'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Budějovická 131', xad_3='Plzeň', xad_4='CZ', xad_5='30100', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^754516476'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '9205215693'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB1', pl_2='ORD01', pl_3='A', pl_4='NEM_ZNOJMO', pl_8='AMB1')
        pv1.attending_doctor = XCN(xcn_1='7899412720', xcn_2='Brožová', xcn_3='Věra', xcn_4='Jaroslava', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='ORL', xcn_2='ORL', xcn_3='SEHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V20034568', xcn_4='ZNENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250430090000')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.segment_action_code = 'A'

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.segment_action_code = 'A'
        ais.universal_service_identifier = CWE(cwe_1='ORL01', cwe_2='ORL kontrola', cwe_3='SEHSERV')
        ais.start_date_time_offset = '20250430090000'
        ais.start_date_time_offset_units = CNE(cne_1='20', cne_2='min')
        ais.duration = 'MIN^^ISO+'

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.segment_action_code = 'A'
        ail.location_resource_id = PL(pl_1='AMB1', pl_2='ORD01', pl_3='A', pl_4='NEM_ZNOJMO', pl_8='AMB1')
        ail.location_group = CWE(cwe_1='20250430090000')
        ail.start_date_time = '20^min'
        ail.start_date_time_offset = 'MIN^^ISO+'

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.segment_action_code = 'A'
        aip.personnel_resource_id = XCN(xcn_1='7899412720', xcn_2='Brožová', xcn_3='Věra', xcn_4='Jaroslava', xcn_6='MUDr.', xcn_9='IČP')
        aip.resource_group = CWE(cwe_1='20250430090000')
        aip.start_date_time = '20^min'
        aip.start_date_time_offset = 'MIN^^ISO+'

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
    """ Based on live/cz/cz-siemens-ehealth.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIEMENS_EHA')
        msh.sending_facility = HD(hd_1='FNKV_PRAHA')
        msh.receiving_application = HD(hd_1='LABLIS')
        msh.receiving_facility = HD(hd_1='FNKV_PRAHA')
        msh.date_time_of_message = '20250306060000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SE20250306060000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5105130320', cx_4='SEHA', cx_5='RC'), CX(cx_1='FNKV12018091', cx_4='FNKV', cx_5='MRN')]
        pid.pid_5 = 'BOUŠKA^Matěj^Jakub^^^'
        pid.date_time_of_birth = '19510513'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Moskevská 156', xad_3='Třebíč', xad_4='CZ', xad_5='67401', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^759870145'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '5105130320'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NCHIR1', pl_2='301', pl_3='A', pl_4='FNKV_PRAHA', pl_8='NCHIR1')
        pv1.attending_doctor = XCN(xcn_1='9539719584', xcn_2='Holub', xcn_3='Filip', xcn_4='Cyril', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='NCHI', xcn_2='Neurochirurgie', xcn_3='SEHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V10023456', xcn_4='FNKVENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250305081000')

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
        orc.placer_order_number = EI(ei_1='ORD201234', ei_2='SEHA')
        orc.filler_order_number = EI(ei_1='LAB301234', ei_2='LABLIS')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250306063000^^R'
        orc.date_time_of_order_event = '20250306060000'
        orc.orc_10 = 'STEPANKOVA^Ryba^Jiří^^^'
        orc.order_control_code_reason = CWE(cwe_1='FNKV_PRAHA')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD201234', ei_2='SEHA')
        obr.filler_order_number = EI(ei_1='LAB301234', ei_2='LABLIS')
        obr.universal_service_identifier = CWE(cwe_1='85025', cwe_2='Krevní obraz kompletní', cwe_3='CPT')
        obr.obr_16 = '9539719584^Holub^Filip^Cyril^^MUDr.^^^IČP'
        obr.results_rpt_status_chng_date_time = '20250306063000'
        obr.result_status = 'NI^No Information^HL70507'

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
    """ Based on live/cz/cz-siemens-ehealth.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIEMENS_EHA')
        msh.sending_facility = HD(hd_1='FNKV_PRAHA')
        msh.receiving_application = HD(hd_1='NIS_FNKV')
        msh.receiving_facility = HD(hd_1='FNKV_PRAHA')
        msh.date_time_of_message = '20250307140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SE20250307140000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5105130320', cx_4='SEHA', cx_5='RC'), CX(cx_1='FNKV12018091', cx_4='FNKV', cx_5='MRN')]
        pid.pid_5 = 'BOUŠKA^Matěj^Jakub^^^'
        pid.date_time_of_birth = '19510513'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Moskevská 156', xad_3='Třebíč', xad_4='CZ', xad_5='67401', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^759870145'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '5105130320'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NCHIR1', pl_2='301', pl_3='A', pl_4='FNKV_PRAHA', pl_8='NCHIR1')
        pv1.attending_doctor = XCN(xcn_1='9539719584', xcn_2='Holub', xcn_3='Filip', xcn_4='Cyril', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='NCHI', xcn_2='Neurochirurgie', xcn_3='SEHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V10023456', xcn_4='FNKVENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250305081000')

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
        orc.placer_order_number = EI(ei_1='ORD201234', ei_2='SEHA')
        orc.filler_order_number = EI(ei_1='LAB301234', ei_2='LABLIS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250306063000^^R'
        orc.date_time_of_order_event = '20250307140000'
        orc.orc_18 = 'FNKV_PRAHA'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD201234', ei_2='SEHA')
        obr.filler_order_number = EI(ei_1='LAB301234', ei_2='LABLIS')
        obr.universal_service_identifier = CWE(cwe_1='85025', cwe_2='Krevní obraz kompletní', cwe_3='CPT')
        obr.observation_date_time = '20250306063500'
        obr.obr_17 = '9539719584^Holub^Filip^Cyril^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250307140000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin', cwe_3='LN')
        obx.obx_5 = '132'
        obx.units = CWE(cwe_1='g/L')
        obx.reference_range = '130-170'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250307130000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematokrit', cwe_3='LN')
        obx_2.obx_5 = '0.40'
        obx_2.units = CWE(cwe_1='L/L')
        obx_2.reference_range = '0.39-0.50'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250307130000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukocyty', cwe_3='LN')
        obx_3.obx_5 = '11.5'
        obx_3.units = CWE(cwe_1='10*9/L')
        obx_3.reference_range = '4.0-10.0'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250307130000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='777-3', cwe_2='Trombocyty', cwe_3='LN')
        obx_4.obx_5 = '210'
        obx_4.units = CWE(cwe_1='10*9/L')
        obx_4.reference_range = '150-400'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250307130000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='4537-7', cwe_2='CRP', cwe_3='LN')
        obx_5.obx_5 = '45.8'
        obx_5.units = CWE(cwe_1='mg/L')
        obx_5.reference_range = '<5.0'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250307130000'

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
    """ Based on live/cz/cz-siemens-ehealth.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIEMENS_EHA')
        msh.sending_facility = HD(hd_1='NEM_TABOR')
        msh.receiving_application = HD(hd_1='MPI_TAB')
        msh.receiving_facility = HD(hd_1='NEM_TABOR')
        msh.date_time_of_message = '20250201110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'SE20250201110000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20250201110000'
        evn.operator_id = XCN(xcn_1='PRIJEM03', xcn_2='Černý', xcn_3='Roman', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='9510028827', cx_4='SEHA', cx_5='RC'), CX(cx_1='TA46036360', cx_4='NEMTAB', cx_5='MRN')]
        pid.pid_5 = 'POKORNÝ^Ondřej^Roman^^^'
        pid.date_time_of_birth = '19951002'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Smilova 65', xad_3='Olomouc', xad_4='CZ', xad_5='77900', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^696088955~^NET^Internet^ondrej.pokorny@email.cz'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '9510028827'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'NEMOCNICE TÁBOR^^40567'
        pd1.pd1_4 = '3752578114^Jelínková^Renata^Věra^^MUDr.^^^IČP'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='POKORNÁ', xpn_2='Markéta', xpn_3='Zuzana')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Mother', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Smilova 65', xad_3='Olomouc', xad_4='CZ', xad_5='77900', xad_6='CZ')
        nk1.nk1_5 = '^PRN^PH^^^420^696088955'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB3', pl_2='ORD05', pl_3='A', pl_4='NEM_TABOR', pl_8='AMB3')
        pv1.attending_doctor = XCN(xcn_1='3752578114', xcn_2='Jelínková', xcn_3='Renata', xcn_4='Věra', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='SEHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V50067890', xcn_4='TABENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250201110000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='211', cwe_2='ZPMV', cwe_4='ZPMV')
        in1.insurance_company_id = CX(cx_1='211')
        in1.insurance_company_name = XON(xon_1='ZDRAVOTNÍ POJIŠŤOVNA MINISTERSTVA VNITRA')
        in1.insurance_company_address = XAD(xad_1='Kodaňská 46', xad_3='Praha 10', xad_4='CZ', xad_5='10100', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^267205555'
        in1.assignment_of_benefits = CWE(cwe_1='POKORNÝ', cwe_2='Ondřej', cwe_3='Roman')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '19951002'
        in1.notice_of_admission_flag = 'Smilova 65^^Olomouc^CZ^77900^CZ'

        # .. build the INSURANCE group ..
        insurance = AdtA05Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.insurance = insurance

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
    """ Based on live/cz/cz-siemens-ehealth.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIEMENS_EHA')
        msh.sending_facility = HD(hd_1='FNKV_PRAHA')
        msh.receiving_application = HD(hd_1='NIS_FNKV')
        msh.receiving_facility = HD(hd_1='FNKV_PRAHA')
        msh.date_time_of_message = '20250308090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'SE20250308090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20250308090000'
        evn.operator_id = XCN(xcn_1='SESTRA02', xcn_2='Marek', xcn_3='Roman', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5105130320', cx_4='SEHA', cx_5='RC'), CX(cx_1='FNKV12018091', cx_4='FNKV', cx_5='MRN')]
        pid.pid_5 = 'BOUŠKA^Matěj^Jakub^^^'
        pid.date_time_of_birth = '19510513'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Moskevská 156', xad_3='Třebíč', xad_4='CZ', xad_5='67401', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^759870145'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '5105130320'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='REHAB1', pl_2='502', pl_3='A', pl_4='FNKV_PRAHA', pl_8='REHAB1')
        pv1.attending_doctor = XCN(xcn_1='8759624869', xcn_2='Holubová', xcn_3='Hana', xcn_4='Anna', xcn_6='MUDr.', xcn_9='IČP')
        pv1.referring_doctor = XCN(xcn_1='9539719584', xcn_2='Holub', xcn_3='Filip', xcn_4='Cyril', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='REH', xcn_2='Rehabilitace', xcn_3='SEHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='T', cwe_2='Transfer', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V10023456', xcn_4='FNKVENC', xcn_5='VN')
        pv1.delete_account_indicator = CWE(cwe_1='NCHIR1', cwe_2='301', cwe_3='A', cwe_4='FNKV_PRAHA', cwe_8='NCHIR1')
        pv1.pv1_40 = '20250308090000'

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
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
    """ Based on live/cz/cz-siemens-ehealth.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIEMENS_EHA')
        msh.sending_facility = HD(hd_1='FN_PLZEN')
        msh.receiving_application = HD(hd_1='DOCSYS')
        msh.receiving_facility = HD(hd_1='FN_PLZEN')
        msh.date_time_of_message = '20250420100000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'SE20250420100000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20250420100000'
        evn.operator_id = XCN(xcn_1='LEKAR01', xcn_2='Lukášová', xcn_3='Magdalena', xcn_6='MUDr.')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5310210451', cx_4='SEHA', cx_5='RC'), CX(cx_1='PL55321890', cx_4='FNPLZ', cx_5='MRN')]
        pid.pid_5 = 'POSPÍŠIL^Josef^Vladimír^^^'
        pid.date_time_of_birth = '19531021'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Pražská 185', xad_3='Karlovy Vary', xad_4='CZ', xad_5='36001', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^629876939'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '5310210451'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NCHIR2', pl_2='402', pl_3='A', pl_4='FN_PLZEN', pl_8='NCHIR2')
        pv1.attending_doctor = XCN(xcn_1='6415106958', xcn_2='Král', xcn_3='Vojtěch', xcn_4='Bedřich', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='NCHI', xcn_2='Neurochirurgie', xcn_3='SEHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V40056789', xcn_4='PLZENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250409080000')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='Propouštěcí zpráva', cwe_3='HL70270')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20250420100000'
        txa.primary_activity_provider_code_name = XCN(xcn_1='6415106958', xcn_2='Král', xcn_3='Vojtěch', xcn_4='Bedřich', xcn_6='MUDr.', xcn_9='IČP')
        txa.origination_date_time = '20250420100000'
        txa.unique_document_number = EI(ei_1='DOC30045678', ei_2='SEHA')
        txa.document_storage_status = 'AV^Available^HL70271'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='11502-2', cwe_2='Laboratorní zpráva', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEg'
            'Pj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIgNzkyXSAvQ29udGVudHMgNCAwIFIgPj4KZW5kb2JqCjQgMCBvYmoK'
            'PDwgL0xlbmd0aCA1MCA+PgpzdHJlYW0KQlQgL0YxIDEyIFRmIDEwMCA3MDAgVGQgKExhYm9yYXRvcm5pIHpwcmF2YSkgVGogRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNQowMDAw'
            'MDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA3NCAwMDAwMCBuIAowMDAwMDAwMTQyIDAwMDAwIG4gCjAwMDAwMDAyNDIgMDAwMDAgbiAKdHJhaWxlcgo8'
            'PCAvU2l6ZSA1IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgozNDIKJSVFT0YK'
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
    """ Based on live/cz/cz-siemens-ehealth.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIEMENS_EHA')
        msh.sending_facility = HD(hd_1='NEM_TREBIC')
        msh.receiving_application = HD(hd_1='MPI_TR')
        msh.receiving_facility = HD(hd_1='NEM_TREBIC')
        msh.date_time_of_message = '20250601090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'SE20250601090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20250601090000'
        evn.operator_id = XCN(xcn_1='ADMIN02', xcn_2='Veselý', xcn_3='Petr', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='7805137765', cx_4='SEHA', cx_5='RC'), CX(cx_1='TR08031480', cx_4='NEMTR', cx_5='MRN')]
        pid.pid_5 = 'RYBA^Štěpán^Ondřej^^^'
        pid.date_time_of_birth = '19780513'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Moskevská 88', xad_3='Třebíč', xad_4='CZ', xad_5='67401', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^624040318~^NET^Internet^stepan.ryba@email.cz'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '7805137765'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'NEMOCNICE TŘEBÍČ^^30456'
        pd1.pd1_4 = '6624496920^Konečná^Marie^Dana^^MUDr.^^^IČP'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB2', pl_2='ORD03', pl_3='A', pl_4='NEM_TREBIC', pl_8='AMB2')
        pv1.attending_doctor = XCN(xcn_1='6624496920', xcn_2='Konečná', xcn_3='Marie', xcn_4='Dana', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='SEHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V30045679', xcn_4='TRENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250601090000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='207', cwe_2='OZP', cwe_4='OZP')
        in1.insurance_company_id = CX(cx_1='207')
        in1.insurance_company_name = XON(xon_1='OBOROVÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Roškotova 1225/1', xad_3='Praha 4', xad_4='CZ', xad_5='14000', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^261105555'
        in1.assignment_of_benefits = CWE(cwe_1='RYBA', cwe_2='Štěpán', cwe_3='Ondřej')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '19780513'
        in1.notice_of_admission_flag = 'Moskevská 88^^Třebíč^CZ^67401^CZ'

        # .. build the INSURANCE group ..
        insurance = AdtA05Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.pv1 = pv1
        msg.insurance = insurance

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
    """ Based on live/cz/cz-siemens-ehealth.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NIS_FNKV')
        msh.sending_facility = HD(hd_1='FNKV_PRAHA')
        msh.receiving_application = HD(hd_1='SIEMENS_EHA')
        msh.receiving_facility = HD(hd_1='FNKV_PRAHA')
        msh.date_time_of_message = '20250305081005'
        msh.message_type = MSG(msg_1='ACK', msg_2='A01', msg_3='ACK')
        msh.message_control_id = 'NIS20250305081005001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'SE20250305081000001'
        msa.expected_sequence_number = '0'

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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
    """ Based on live/cz/cz-siemens-ehealth.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIEMENS_EHA')
        msh.sending_facility = HD(hd_1='FN_PLZEN')
        msh.receiving_application = HD(hd_1='MPI_PLZ')
        msh.receiving_facility = HD(hd_1='FN_PLZEN')
        msh.date_time_of_message = '20250515120000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'SE20250515120000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20250515120000'
        evn.operator_id = XCN(xcn_1='ADMIN03', xcn_2='Čermáková', xcn_3='Věra', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='5310210451', cx_4='SEHA', cx_5='RC'), CX(cx_1='PL55321890', cx_4='FNPLZ', cx_5='MRN')]
        pid.pid_5 = 'POSPÍŠIL^Josef^Vladimír^^^'
        pid.date_time_of_birth = '19531021'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Pražská 185', xad_3='Karlovy Vary', xad_4='CZ', xad_5='36001', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^629876939'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '5310210451'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='PL57879076', cx_4='FNPLZ', cx_5='MRN')
        mrg.mrg_2 = '5105130320'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB4', pl_2='ORD07', pl_3='A', pl_4='FN_PLZEN', pl_8='AMB4')
        pv1.attending_doctor = XCN(xcn_1='6415106958', xcn_2='Král', xcn_3='Vojtěch', xcn_4='Bedřich', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='NCHI', xcn_2='Neurochirurgie', xcn_3='SEHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V40056789', xcn_4='PLZENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250515120000')

        # .. build the PATIENT group ..
        patient = AdtA39Patient()
        patient.pid = pid
        patient.mrg = mrg
        patient.pv1 = pv1

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
    """ Based on live/cz/cz-siemens-ehealth.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIEMENS_EHA')
        msh.sending_facility = HD(hd_1='NEM_ZNOJMO')
        msh.receiving_application = HD(hd_1='NIS_ZN')
        msh.receiving_facility = HD(hd_1='NEM_ZNOJMO')
        msh.date_time_of_message = '20250501140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SE20250501140000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='4603033359', cx_4='SEHA', cx_5='RC'), CX(cx_1='ZN15512475', cx_4='NEMZN', cx_5='MRN')]
        pid.pid_5 = 'ŠIMEK^Rostislav^Stanislav^^^'
        pid.date_time_of_birth = '19460303'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Pařížská 133', xad_3='Třebíč', xad_4='CZ', xad_5='67401', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^759996926'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.pid_19 = '4603033359'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='AMB5', pl_2='ORD09', pl_3='A', pl_4='NEM_ZNOJMO', pl_8='AMB5')
        pv1.attending_doctor = XCN(xcn_1='7899412720', xcn_2='Brožová', xcn_3='Věra', xcn_4='Jaroslava', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='VŠE', xcn_2='Všeobecné lékařství', xcn_3='SEHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V60078901', xcn_4='ZNENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250430080000')

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
        orc.placer_order_number = EI(ei_1='ORD301234', ei_2='SEHA')
        orc.filler_order_number = EI(ei_1='LAB401234', ei_2='LABLIS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250430083000^^R'
        orc.date_time_of_order_event = '20250501140000'
        orc.orc_18 = 'NEM_ZNOJMO'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD301234', ei_2='SEHA')
        obr.filler_order_number = EI(ei_1='LAB401234', ei_2='LABLIS')
        obr.universal_service_identifier = CWE(cwe_1='80053', cwe_2='Komplexní metabolický panel', cwe_3='CPT')
        obr.observation_date_time = '20250430083500'
        obr.obr_17 = '7899412720^Brožová^Věra^Jaroslava^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250501140000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glukóza v séru', cwe_3='LN')
        obx.obx_5 = '5.3'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.9-5.8'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250501130000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Kreatinin v séru', cwe_3='LN')
        obx_2.obx_5 = '88'
        obx_2.units = CWE(cwe_1='umol/L')
        obx_2.reference_range = '62-106'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250501130000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea v séru', cwe_3='LN')
        obx_3.obx_5 = '5.8'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '2.8-7.2'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20250501130000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT v séru', cwe_3='LN')
        obx_4.obx_5 = '0.35'
        obx_4.units = CWE(cwe_1='ukat/L')
        obx_4.reference_range = '0.10-0.75'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20250501130000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='1975-2', cwe_2='Celkový bilirubin', cwe_3='LN')
        obx_5.obx_5 = '12.5'
        obx_5.units = CWE(cwe_1='umol/L')
        obx_5.reference_range = '3.4-17.1'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20250501130000'

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
    """ Based on live/cz/cz-siemens-ehealth.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIEMENS_EHA')
        msh.sending_facility = HD(hd_1='NEM_TREBIC')
        msh.receiving_application = HD(hd_1='CARDIS')
        msh.receiving_facility = HD(hd_1='NEM_TREBIC')
        msh.date_time_of_message = '20250605080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'SE20250605080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='7808248585', cx_4='SEHA', cx_5='RC'), CX(cx_1='TR52607865', cx_4='NEMTR', cx_5='MRN')]
        pid.pid_5 = 'KOPECKÝ^Václav^Marek^^^'
        pid.date_time_of_birth = '19780824'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Pařížská 140', xad_3='Liberec', xad_4='CZ', xad_5='46001', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^672120986'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '7808248585'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='KARD1', pl_2='KAR01', pl_3='A', pl_4='NEM_TREBIC', pl_8='KARD1')
        pv1.attending_doctor = XCN(xcn_1='6624496920', xcn_2='Konečná', xcn_3='Marie', xcn_4='Dana', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='KAR', xcn_2='Kardiologie', xcn_3='SEHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V70089012', xcn_4='TRENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250605080000')

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
        orc.placer_order_number = EI(ei_1='ORD401234', ei_2='SEHA')
        orc.filler_order_number = EI(ei_1='ECHO501234', ei_2='CARDIS')
        orc.order_status = 'SC'
        orc.orc_7 = '^^^20250605100000^^R'
        orc.date_time_of_order_event = '20250605080000'
        orc.orc_10 = 'KREJCIVK^Polák^Aleš^^^'
        orc.order_control_code_reason = CWE(cwe_1='NEM_TREBIC')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD401234', ei_2='SEHA')
        obr.filler_order_number = EI(ei_1='ECHO501234', ei_2='CARDIS')
        obr.universal_service_identifier = CWE(cwe_1='93306', cwe_2='Transtorakální echokardiografie', cwe_3='CPT')
        obr.obr_16 = '6624496920^Konečná^Marie^Dana^^MUDr.^^^IČP'
        obr.results_rpt_status_chng_date_time = '20250605100000'
        obr.result_status = 'NI^No Information^HL70507'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I50.0', cwe_2='Městnavé srdeční selhání', cwe_3='MKN10')
        dg1.diagnosis_date_time = '20250605'
        dg1.diagnosis_type = CWE(cwe_1='W', cwe_2='Working', cwe_3='HL70052')

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
    """ Based on live/cz/cz-siemens-ehealth.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIEMENS_EHA')
        msh.sending_facility = HD(hd_1='FNKV_PRAHA')
        msh.receiving_application = HD(hd_1='NIS_FNKV')
        msh.receiving_facility = HD(hd_1='FNKV_PRAHA')
        msh.date_time_of_message = '20250310150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SE20250310150000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='0001115259', cx_4='SEHA', cx_5='RC'), CX(cx_1='FNKV29956214', cx_4='FNKV', cx_5='MRN')]
        pid.pid_5 = 'BROŽ^Antonín^Stanislav^^^'
        pid.date_time_of_birth = '20000111'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Nábřežní 9', xad_3='Tábor', xad_4='CZ', xad_5='39001', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^703513504'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '0001115259'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT3', pl_2='305', pl_3='A', pl_4='FNKV_PRAHA', pl_8='INT3')
        pv1.attending_doctor = XCN(xcn_1='5873020248', xcn_2='Fiala', xcn_3='Radek', xcn_4='Jakub', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='INT', xcn_2='Interna', xcn_3='SEHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V80090123', xcn_4='FNKVENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250305090000')

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
        orc.placer_order_number = EI(ei_1='ORD501234', ei_2='SEHA')
        orc.filler_order_number = EI(ei_1='MIC601234', ei_2='LABLIS')
        orc.order_status = 'CM'
        orc.orc_7 = '^^^20250306100000^^R'
        orc.date_time_of_order_event = '20250310150000'
        orc.orc_18 = 'FNKV_PRAHA'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD501234', ei_2='SEHA')
        obr.filler_order_number = EI(ei_1='MIC601234', ei_2='LABLIS')
        obr.universal_service_identifier = CWE(cwe_1='87086', cwe_2='Kultivace moči', cwe_3='CPT')
        obr.observation_date_time = '20250306100500'
        obr.obr_17 = '5873020248^Fiala^Radek^Jakub^^MUDr.^^^IČP'
        obr.charge_to_practice = MOC(moc_1='20250310150000')
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='630-4', cwe_2='Bakterie identifikované v moči kultivací', cwe_3='LN')
        obx.obx_5 = 'Klebsiella pneumoniae > 10^5 CFU/ml'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20250310140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'TX'
        obx_2.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Citlivost na antibiotika', cwe_3='LN')
        obx_2.obx_5 = 'Ampicilin: R, Amoxicilin/klavulanát: S, Ciprofloxacin: S, Cotrimoxazol: R, Gentamicin: S, Cefuroxim: S'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20250310140000'

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
    """ Based on live/cz/cz-siemens-ehealth.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIEMENS_EHA')
        msh.sending_facility = HD(hd_1='NEM_TABOR')
        msh.receiving_application = HD(hd_1='NIS_TAB')
        msh.receiving_facility = HD(hd_1='NEM_TABOR')
        msh.date_time_of_message = '20250520073000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'SE20250520073000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20250520073000'
        evn.operator_id = XCN(xcn_1='PRIJEM04', xcn_2='Holubová', xcn_3='Ivana', xcn_6='Bc.')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='4811273722', cx_4='SEHA', cx_5='RC'), CX(cx_1='TA56264629', cx_4='NEMTAB', cx_5='MRN')]
        pid.pid_5 = 'LUKÁŠ^Daniel^Matěj^^^'
        pid.date_time_of_birth = '19481127'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Nádražní 192', xad_3='Brno', xad_4='CZ', xad_5='60300', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^768563128'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '4811273722'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'NEMOCNICE TÁBOR^^40567'
        pd1.pd1_4 = '3752578114^Jelínková^Renata^Věra^^MUDr.^^^IČP'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='LUKÁŠOVÁ', xpn_2='Helena', xpn_3='Pavla')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Nádražní 192', xad_3='Brno', xad_4='CZ', xad_5='60300', xad_6='CZ')
        nk1.nk1_5 = '^PRN^PH^^^420^768563128'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT1', pl_2='105', pl_3='A', pl_4='NEM_TABOR', pl_8='INT1')
        pv1.attending_doctor = XCN(xcn_1='3752578114', xcn_2='Jelínková', xcn_3='Renata', xcn_4='Věra', xcn_6='MUDr.', xcn_9='IČP')
        pv1.referring_doctor = XCN(xcn_1='5873020248', xcn_2='Fiala', xcn_3='Radek', xcn_4='Jakub', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='INT', xcn_2='Interna', xcn_3='SEHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V90101234', xcn_4='TABENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250520073000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Dekompenzované srdeční selhání', cwe_3='I50.0')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='201', cwe_2='VoZP', cwe_4='VOZP')
        in1.insurance_company_id = CX(cx_1='201')
        in1.insurance_company_name = XON(xon_1='VOJENSKÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Drahobejlova 1404/4', xad_3='Praha 9', xad_4='CZ', xad_5='19000', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^284091111'
        in1.assignment_of_benefits = CWE(cwe_1='LUKÁŠ', cwe_2='Daniel', cwe_3='Matěj')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '19481127'
        in1.notice_of_admission_flag = 'Nádražní 192^^Brno^CZ^60300^CZ'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.insurance = insurance

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
    """ Based on live/cz/cz-siemens-ehealth.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIEMENS_EHA')
        msh.sending_facility = HD(hd_1='NEM_TABOR')
        msh.receiving_application = HD(hd_1='REGSYS')
        msh.receiving_facility = HD(hd_1='NEM_TABOR')
        msh.date_time_of_message = '20250610090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'SE20250610090000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.continuation_pointer = 'CZ'
        msh.accept_acknowledgment = 'UNICODE UTF-8'
        msh.application_acknowledgment_type = 'CES'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20250610090000'
        evn.operator_id = XCN(xcn_1='PRIJEM05', xcn_2='Janda', xcn_3='Marek', xcn_6='')
        evn.evn_7 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='1706144415', cx_4='SEHA', cx_5='RC'), CX(cx_1='TA92140056', cx_4='NEMTAB', cx_5='MRN')]
        pid.pid_5 = 'JANDA^Aleš^Dalibor^^^'
        pid.date_time_of_birth = '20170614'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='28. října 168', xad_3='Olomouc', xad_4='CZ', xad_5='77900', xad_6='CZ', xad_7='L')
        pid.pid_13 = '^PRN^PH^^^420^696807335~^NET^Internet^ales.janda@email.cz'
        pid.primary_language = CWE(cwe_1='ces', cwe_2='čeština', cwe_3='ISO6392')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.pid_19 = '1706144415'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_3 = 'NEMOCNICE TÁBOR^^40567'
        pd1.pd1_4 = '4036720923^Janoušek^Lukáš^Ondřej^^MUDr.^^^IČP'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='JANDOVÁ', xpn_2='Dana', xpn_3='Kateřina')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='28. října 168', xad_3='Olomouc', xad_4='CZ', xad_5='77900', xad_6='CZ')
        nk1.nk1_5 = '^PRN^PH^^^420^696807335'
        nk1.contact_role = CWE(cwe_1='EC', cwe_2='Emergency Contact', cwe_3='HL70131')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='DER1', pl_2='DER01', pl_3='A', pl_4='NEM_TABOR', pl_8='DER1')
        pv1.attending_doctor = XCN(xcn_1='4036720923', xcn_2='Janoušek', xcn_3='Lukáš', xcn_4='Ondřej', xcn_6='MUDr.', xcn_9='IČP')
        pv1.consulting_doctor = XCN(xcn_1='DER', xcn_2='Dermatologie', xcn_3='SEHSERV')
        pv1.preadmit_test_indicator = CWE(cwe_1='R', cwe_2='Referral', cwe_3='HL70007')
        pv1.admitting_doctor = XCN(xcn_1='V10112345', xcn_4='TABENC', xcn_5='VN')
        pv1.pending_location = PL(pl_1='20250610090000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='111', cwe_2='VZP', cwe_4='VZP')
        in1.insurance_company_id = CX(cx_1='111')
        in1.insurance_company_name = XON(xon_1='VŠEOBECNÁ ZDRAVOTNÍ POJIŠŤOVNA')
        in1.insurance_company_address = XAD(xad_1='Orlická 4', xad_3='Praha 3', xad_4='CZ', xad_5='13000', xad_6='CZ')
        in1.in1_6 = '^PRN^PH^^^420^952222222'
        in1.assignment_of_benefits = CWE(cwe_1='JANDA', cwe_2='Aleš', cwe_3='Dalibor')
        in1.coordination_of_benefits = CWE(cwe_1='01', cwe_2='Self', cwe_3='HL70063')
        in1.coord_of_ben_priority = '20170614'
        in1.notice_of_admission_flag = '28. října 168^^Olomouc^CZ^77900^CZ'

        # .. build the INSURANCE group ..
        insurance = AdtA01Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.insurance = insurance

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
