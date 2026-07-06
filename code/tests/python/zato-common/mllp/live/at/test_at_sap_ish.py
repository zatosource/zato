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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, DR, EI, HD, MSG, OG, PL, PT, VID, XAD, XCN, XON, XPN, XTN
from zato.hl7v2.v2_9.groups import AdrA19Insurance, AdrA19QueryResponse, AdtA01Insurance, AdtA01NextOfKin, AdtA03Procedure, AdtA05Insurance, AdtA05NextOfKin, \
    BarP01Diagnosis, BarP01Procedure, BarP01Visit, MdmT01CommonOrder, MdmT02CommonOrder, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, \
    OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ADR_A19, ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A06, ADT_A09, ADT_A30, BAR_P01, MDM_T01, MDM_T02, ORM_O01, ORU_R01, \
    QRY_A19
from zato.hl7v2.v2_9.segments import DG1, EVN, FT1, IN1, MRG, MSA, MSH, NK1, OBR, OBX, ORC, PID, PR1, PV1, PV2, QRD, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('at', 'at-sap-ish.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/at/at-sap-ish.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.date_time_of_message = '20240315083022'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        msh.message_control_id = 'TK20240315083022001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20240315083000'
        evn.operator_id = XCN(xcn_1='PFEIFFER', xcn_2='DIETRICH', xcn_5='DR.')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT005923', cx_4='KISS', cx_5='PI'), CX(cx_1='1871150365', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='WALLNER', xpn_2='FRANZISKA', xpn_3='HEDWIG')
        pid.date_time_of_birth = '19650315'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='MUSEUMSTRASSE 14', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '^PRN^PH^^0043^512^738294'
        pid.marital_status = CWE(cwe_1='D')
        pid.patient_account_number = CX(cx_1='VIS20240315001', cx_4='TIROL_KLINIKEN', cx_5='VN')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='WALLNER', xpn_2='GOTTFRIED')
        nk1.address = XAD(xad_1='MUSEUMSTRASSE 14', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT', xad_7='H')
        nk1.nk1_5 = '^PRN^PH^^0043^512^738295'
        nk1.contact_role = CWE(cwe_1='NOK')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='0312', pl_3='01', pl_4='LKI')
        pv1.pv1_7 = 'PFEIFFER^DIETRICH^^^DR.^^LANR^^^L'
        pv1.referring_doctor = XCN(xcn_1='KASTNER', xcn_2='RUPRECHT', xcn_5='DR.')
        pv1.hospital_service = CWE(cwe_1='SUR')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.pv1_17 = 'PFEIFFER^DIETRICH^^^DR.^^LANR^^^L'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.discharge_disposition = CWE(cwe_1='LKI')
        pv1.pv1_40 = 'A'
        pv1.prior_temporary_location = PL(pl_1='20240315083000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.expected_admit_date_time = '20240322'
        pv2.expected_number_of_insurance_plans = 'N'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I10', cwe_2='Essentielle Hypertonie', cwe_3='ICD-10-BMSG-2024')
        dg1.diagnosis_date_time = '20240315083000'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='GKK', cwe_2='Gebietskrankenkasse')
        in1.insurance_company_name = XON(xon_1='OEGK', xon_2='Oesterreichische Gesundheitskasse')
        in1.insurance_company_address = XAD(xad_1='WIENERBERGSTRASSE 15-19', xad_3='WIEN', xad_5='1100', xad_6='AUT')
        in1.plan_effective_date = '20240101'
        in1.plan_expiration_date = '20241231'
        in1.name_of_insured = XPN(xpn_1='WALLNER', xpn_2='FRANZISKA', xpn_3='HEDWIG')
        in1.insureds_relationship_to_patient = CWE(cwe_1='01')
        in1.insureds_date_of_birth = '19650315'
        in1.insureds_address = XAD(xad_1='MUSEUMSTRASSE 14', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT')
        in1.delay_before_lr_day = '1871150365'

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
        msg.pv2 = pv2
        msg.dg1 = dg1
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
    """ Based on live/at/at-sap-ish.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.date_time_of_message = '20240316141530'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02')
        msh.message_control_id = 'TK20240316141530001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20240316141500'
        evn.operator_id = XCN(xcn_1='HOLZER', xcn_2='VERONIKA', xcn_5='DR.')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT005923', cx_4='KISS', cx_5='PI'), CX(cx_1='1871150365', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='WALLNER', xpn_2='FRANZISKA', xpn_3='HEDWIG')
        pid.date_time_of_birth = '19650315'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='MUSEUMSTRASSE 14', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '^PRN^PH^^0043^512^738294'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='0215', pl_3='02', pl_4='LKI')
        pv1.pv1_7 = 'HOLZER^VERONIKA^^^DR.^^LANR^^^L'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.pv1_17 = 'HOLZER^VERONIKA^^^DR.^^LANR^^^L'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.discharge_disposition = CWE(cwe_1='LKI')
        pv1.pv1_40 = 'A'
        pv1.prior_temporary_location = PL(pl_1='20240315083000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.expected_admit_date_time = '20240325'

        # .. assemble the full message ..
        msg = ADT_A02()
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
    """ Based on live/at/at-sap-ish.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.date_time_of_message = '20240322100045'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03')
        msh.message_control_id = 'TK20240322100045001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20240322100000'
        evn.operator_id = XCN(xcn_1='PFEIFFER', xcn_2='DIETRICH', xcn_5='DR.')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT005923', cx_4='KISS', cx_5='PI'), CX(cx_1='1871150365', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='WALLNER', xpn_2='FRANZISKA', xpn_3='HEDWIG')
        pid.date_time_of_birth = '19650315'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='MUSEUMSTRASSE 14', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='0312', pl_3='01', pl_4='LKI')
        pv1.pv1_7 = 'PFEIFFER^DIETRICH^^^DR.^^LANR^^^L'
        pv1.hospital_service = CWE(cwe_1='SUR')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.pv1_17 = 'PFEIFFER^DIETRICH^^^DR.^^LANR^^^L'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.discharge_disposition = CWE(cwe_1='LKI')
        pv1.pv1_40 = 'A'
        pv1.prior_temporary_location = PL(pl_1='20240315083000')
        pv1.admit_date_time = '20240322100000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I10', cwe_2='Essentielle Hypertonie', cwe_3='ICD-10-BMSG-2024')
        dg1.diagnosis_date_time = '20240315'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.dg1_2 = 'I10'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='K80.2', cwe_2='Cholelithiasis ohne Cholezystitis', cwe_3='ICD-10-BMSG-2024')
        dg1_2.diagnosis_date_time = '20240315'
        dg1_2.diagnosis_type = CWE(cwe_1='W')

        # .. build PR1 ..
        pr1 = PR1()
        pr1.set_id_pr1 = '1'
        pr1.pr1_2 = 'OPS'
        pr1.procedure_code = CNE(cne_1='5-511.11', cne_2='Laparoskopische Cholezystektomie', cne_3='OPS-2024')
        pr1.procedure_date_time = '20240318100000'
        pr1.anesthesia_minutes = 'PFEIFFER^DIETRICH^^^DR.'

        # .. build the PROCEDURE group ..
        procedure = AdtA03Procedure()
        procedure.pr1 = pr1

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = [dg1, dg1_2]
        msg.procedure = procedure

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
    """ Based on live/at/at-sap-ish.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='AKH_WIEN')
        msh.receiving_application = HD(hd_1='ORBIS')
        msh.receiving_facility = HD(hd_1='AKH_WIEN')
        msh.date_time_of_message = '20240410093012'
        msh.message_type = MSG(msg_1='ADT', msg_2='A05')
        msh.message_control_id = 'AKH20240410093012001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A05'
        evn.recorded_date_time = '20240410093000'
        evn.operator_id = XCN(xcn_1='DOPPLER', xcn_2='ENGELBERT', xcn_5='PROF.DR.')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT118844', cx_4='KIS', cx_5='PI'), CX(cx_1='4532010178', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='LECHNER', xpn_2='MAXIMILIAN', xpn_3='OTTOKAR')
        pid.date_time_of_birth = '19780101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='FAVORITENSTRASSE 27', xad_3='WIEN', xad_5='1040', xad_6='AUT', xad_7='H')
        pid.pid_13 = '^PRN^PH^^0043^1^4893156'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='VIS20240415001', cx_4='AKH_WIEN', cx_5='VN')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='P')
        pv1.assigned_patient_location = PL(pl_1='KARD', pl_2='0401', pl_3='01', pl_4='AKH')
        pv1.pv1_7 = 'DOPPLER^ENGELBERT^^^PROF.DR.^^LANR^^^L'
        pv1.hospital_service = CWE(cwe_1='KARD')
        pv1.admit_source = CWE(cwe_1='R')
        pv1.pv1_17 = 'DOPPLER^ENGELBERT^^^PROF.DR.^^LANR^^^L'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.discharge_disposition = CWE(cwe_1='AKH_WIEN')
        pv1.pv1_40 = 'P'
        pv1.prior_temporary_location = PL(pl_1='20240415080000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='GKK', cwe_2='Gebietskrankenkasse')
        in1.insurance_company_name = XON(xon_1='WGKK', xon_2='Wiener GKK')
        in1.insurance_company_address = XAD(xad_1='WIENERBERGSTRASSE 15-19', xad_3='WIEN', xad_5='1100', xad_6='AUT')
        in1.insureds_relationship_to_patient = CWE(cwe_1='LECHNER', cwe_2='MAXIMILIAN', cwe_3='OTTOKAR')
        in1.insureds_date_of_birth = '01'
        in1.insureds_address = XAD(xad_1='19780101')

        # .. build the INSURANCE group ..
        insurance = AdtA05Insurance()
        insurance.in1 = in1

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
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
    """ Based on live/at/at-sap-ish.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='KUK_LINZ')
        msh.receiving_application = HD(hd_1='RCC_ADT')
        msh.receiving_facility = HD(hd_1='KUK_LINZ')
        msh.date_time_of_message = '20240502154530'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08')
        msh.message_control_id = 'RCC20240502154530001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20240502154500'
        evn.operator_id = XCN(xcn_1='STROBL', xcn_2='ADELHEID', xcn_5='DR.')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT009477', cx_4='KIS', cx_5='PI'), CX(cx_1='7711220581', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='RIEGLER', xpn_2='ROSALIA', xpn_3='KUNIGUNDE')
        pid.date_time_of_birth = '19810522'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='HAFENSTRASSE 31', xad_3='LINZ', xad_4='OOE', xad_5='4020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '^PRN^PH^^0043^732^824567~^NET^Internet^rosalia.riegler@gmx.at'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='VIS20240428003', cx_4='KUK_LINZ', cx_5='VN')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='GYN', pl_2='0108', pl_3='02', pl_4='KUK')
        pv1.pv1_7 = 'STROBL^ADELHEID^^^DR.^^LANR^^^L'
        pv1.hospital_service = CWE(cwe_1='GYN')
        pv1.admit_source = CWE(cwe_1='R')
        pv1.pv1_17 = 'STROBL^ADELHEID^^^DR.^^LANR^^^L'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.discharge_disposition = CWE(cwe_1='KUK_LINZ')
        pv1.pv1_40 = 'A'
        pv1.prior_temporary_location = PL(pl_1='20240428120000')

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
    """ Based on live/at/at-sap-ish.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.date_time_of_message = '20240605111500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28')
        msh.message_control_id = 'TK20240605111500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20240605111500'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='SYSTEM')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT008312', cx_4='KISS', cx_5='PI'), CX(cx_1='6688030790', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='EGGER', xpn_2='WILLIBALD', xpn_3='SIEGMUND')
        pid.date_time_of_birth = '19900307'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='ERLERSTRASSE 7', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '^PRN^PH^^0043^512^447788~^PRN^CP^^0043^664^8871234'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='S')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='EGGER', xpn_2='WALPURGA')
        nk1.address = XAD(xad_1='ERLERSTRASSE 7', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT', xad_7='H')
        nk1.nk1_5 = '^PRN^PH^^0043^512^447789'
        nk1.contact_role = CWE(cwe_1='MTH')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin

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
    """ Based on live/at/at-sap-ish.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.date_time_of_message = '20240605120030'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31')
        msh.message_control_id = 'TK20240605120030001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20240605120000'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='SYSTEM')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT008312', cx_4='KISS', cx_5='PI'), CX(cx_1='6688030790', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='EGGER', xpn_2='WILLIBALD', xpn_3='SIEGMUND')
        pid.date_time_of_birth = '19900307'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='SALURNERSTRASSE 15', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '^PRN^PH^^0043^512^447788~^PRN^CP^^0043^664^8871234'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='S')

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid

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
    """ Based on live/at/at-sap-ish.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.date_time_of_message = '20240610094500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A34')
        msh.message_control_id = 'TK20240610094500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A34'
        evn.recorded_date_time = '20240610094500'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='SYSTEM')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT008312', cx_4='KISS', cx_5='PI'), CX(cx_1='6688030790', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='EGGER', xpn_2='WILLIBALD', xpn_3='SIEGMUND')
        pid.date_time_of_birth = '19900307'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='PAT008999', cx_4='KISS', cx_5='PI')

        # .. assemble the full message ..
        msg = ADT_A30()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.mrg = mrg

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
    """ Based on live/at/at-sap-ish.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='SALK_SALZBURG')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='LKH_SALZBURG')
        msh.date_time_of_message = '20240712150022'
        msh.message_type = MSG(msg_1='ADT', msg_2='A11')
        msh.message_control_id = 'SALK20240712150022001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A11'
        evn.recorded_date_time = '20240712150000'
        evn.operator_id = XCN(xcn_1='ORTNER', xcn_2='HARTMUT', xcn_5='DR.')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT033221', cx_4='KIS', cx_5='PI'), CX(cx_1='9912061082', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='BRUNNER', xpn_2='OTTILIE', xpn_3='GISELA')
        pid.date_time_of_birth = '19821006'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='LINZER GASSE 22', xad_3='SALZBURG', xad_4='S', xad_5='5020', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='0205', pl_3='01', pl_4='LKH')
        pv1.pv1_7 = 'ORTNER^HARTMUT^^^DR.^^LANR^^^L'
        pv1.hospital_service = CWE(cwe_1='SUR')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.pv1_17 = 'ORTNER^HARTMUT^^^DR.^^LANR^^^L'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.discharge_disposition = CWE(cwe_1='SALK')
        pv1.pv1_40 = 'A'
        pv1.prior_temporary_location = PL(pl_1='20240712140000')

        # .. assemble the full message ..
        msg = ADT_A09()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/at/at-sap-ish.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.receiving_application = HD(hd_1='CLOVERLEAF')
        msh.receiving_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.date_time_of_message = '20240322113000'
        msh.message_type = MSG(msg_1='BAR', msg_2='P01')
        msh.message_control_id = 'TK20240322113000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'P01'
        evn.recorded_date_time = '20240322113000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT005923', cx_4='KISS', cx_5='PI'), CX(cx_1='1871150365', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='WALLNER', xpn_2='FRANZISKA', xpn_3='HEDWIG')
        pid.date_time_of_birth = '19650315'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='MUSEUMSTRASSE 14', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='0312', pl_3='01', pl_4='LKI')
        pv1.attending_doctor = XCN(xcn_1='PFEIFFER', xcn_2='DIETRICH', xcn_5='DR.')
        pv1.consulting_doctor = XCN(xcn_1='SUR')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='PFEIFFER', cwe_2='DIETRICH', cwe_5='DR.')
        pv1.admitting_doctor = XCN(xcn_1='IP')
        pv1.delete_account_date = 'LKI'
        pv1.servicing_facility = CWE(cwe_1='A')
        pv1.pending_location = PL(pl_1='20240315083000')
        pv1.prior_temporary_location = PL(pl_1='20240322100000')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K80.2', cwe_2='Cholelithiasis ohne Cholezystitis', cwe_3='ICD-10-BMSG-2024')
        dg1.diagnosis_date_time = '20240315'
        dg1.diagnosis_type = CWE(cwe_1='W')

        # .. build the DIAGNOSIS group ..
        diagnosis = BarP01Diagnosis()
        diagnosis.dg1 = dg1

        # .. build PR1 ..
        pr1 = PR1()
        pr1.set_id_pr1 = '1'
        pr1.pr1_2 = 'OPS'
        pr1.procedure_code = CNE(cne_1='5-511.11', cne_2='Laparoskopische Cholezystektomie', cne_3='OPS-2024')
        pr1.procedure_date_time = '20240318100000'

        # .. build the PROCEDURE group ..
        procedure = BarP01Procedure()
        procedure.pr1 = pr1

        # .. build the VISIT group ..
        visit = BarP01Visit()
        visit.pv1 = pv1
        visit.diagnosis = diagnosis
        visit.procedure = procedure

        # .. build FT1 ..
        ft1 = FT1()
        ft1.set_id_ft1 = '1'
        ft1.transaction_batch_id = '20240318'
        ft1.transaction_date = DR(dr_1='20240318100000')
        ft1.transaction_posting_date = 'P'
        ft1.transaction_type = CWE(cwe_1='5-511.11', cwe_2='Laparoskopische Cholezystektomie', cwe_3='OPS-2024')
        ft1.ft1_8 = '1'
        ft1.health_plan_id = CWE(cwe_1='CHIR', cwe_2='0312', cwe_3='01', cwe_4='LKI')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='GKK', cwe_2='Gebietskrankenkasse')
        in1.insurance_company_name = XON(xon_1='OEGK')
        in1.insurance_company_address = XAD(xad_1='WIENERBERGSTRASSE 15-19', xad_3='WIEN', xad_5='1100', xad_6='AUT')
        in1.insureds_group_emp_name = XON(xon_1='20240101')
        in1.plan_effective_date = '20241231'
        in1.plan_type = CWE(cwe_1='WALLNER', cwe_2='FRANZISKA', cwe_3='HEDWIG')
        in1.name_of_insured = XPN(xpn_1='01')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19650315')
        in1.insureds_date_of_birth = 'MUSEUMSTRASSE 14^^INNSBRUCK^T^6020^AUT'
        in1.lifetime_reserve_days = '1871150365'

        # .. assemble the full message ..
        msg = BAR_P01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.visit = visit
        msg.extra_segments = [ft1, in1]

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
    """ Based on live/at/at-sap-ish.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.date_time_of_message = '20240318090015'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'TK20240318090015001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT005923', cx_4='KISS', cx_5='PI'), CX(cx_1='1871150365', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='WALLNER', xpn_2='FRANZISKA', xpn_3='HEDWIG')
        pid.date_time_of_birth = '19650315'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='MUSEUMSTRASSE 14', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='0312', pl_3='01', pl_4='LKI')
        pv1.attending_doctor = XCN(xcn_1='PFEIFFER', xcn_2='DIETRICH', xcn_5='DR.')
        pv1.consulting_doctor = XCN(xcn_1='SUR')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='PFEIFFER', cwe_2='DIETRICH', cwe_5='DR.')
        pv1.admitting_doctor = XCN(xcn_1='IP')
        pv1.delete_account_date = 'LKI'
        pv1.servicing_facility = CWE(cwe_1='A')
        pv1.pending_location = PL(pl_1='20240315083000')

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
        orc.placer_order_number = EI(ei_1='ORD20240318001')
        orc.filler_order_number = EI(ei_1='ORD20240318001F')
        orc.order_status = 'SC'
        orc.orc_10 = 'PFEIFFER^DIETRICH^^^DR.^^LANR^^^L'
        orc.orc_12 = 'PFEIFFER^DIETRICH^^^DR.^^LANR^^^L'
        orc.enterers_location = PL(pl_3='LKI')
        orc.call_back_phone_number = XTN(xtn_2='PRN', xtn_3='CP', xtn_5='0043', xtn_6='512', xtn_7='89059')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20240318001')
        obr.filler_order_number = EI(ei_1='ORD20240318001F')
        obr.universal_service_identifier = CWE(cwe_1='CT-ABD', cwe_2='CT Abdomen mit KM', cwe_3='LOINC')
        obr.observation_date_time = '20240318090000'
        obr.obr_14 = 'Verdacht auf Cholelithiasis'
        obr.filler_field_1 = 'ACC20240318001'
        obr.diagnostic_serv_sect_id = '20240318090000'
        obr.obr_27 = 'F'

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
    """ Based on live/at/at-sap-ish.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='SAP-ISH')
        msh.receiving_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.date_time_of_message = '20240318160030'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'RIS20240318160030001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT005923', cx_4='KISS', cx_5='PI'), CX(cx_1='1871150365', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='WALLNER', xpn_2='FRANZISKA', xpn_3='HEDWIG')
        pid.date_time_of_birth = '19650315'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='0312', pl_3='01', pl_4='LKI')
        pv1.attending_doctor = XCN(xcn_1='PFEIFFER', xcn_2='DIETRICH', xcn_5='DR.')
        pv1.consulting_doctor = XCN(xcn_1='SUR')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='PFEIFFER', cwe_2='DIETRICH', cwe_5='DR.')
        pv1.admitting_doctor = XCN(xcn_1='IP')
        pv1.delete_account_date = 'LKI'
        pv1.servicing_facility = CWE(cwe_1='A')
        pv1.pending_location = PL(pl_1='20240315083000')

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
        orc.placer_order_number = EI(ei_1='ORD20240318001')
        orc.filler_order_number = EI(ei_1='ORD20240318001F')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20240318001')
        obr.filler_order_number = EI(ei_1='ORD20240318001F')
        obr.universal_service_identifier = CWE(cwe_1='CT-ABD', cwe_2='CT Abdomen mit KM', cwe_3='LOINC')
        obr.observation_date_time = '20240318090000'
        obr.filler_field_2 = 'ACC20240318001'
        obr.result_status = '20240318160000'
        obr.obr_28 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='REPORT', cwe_2='Befund')
        obx.obx_5 = (
            'Befund CT Abdomen\\.br\\\\.br\\Klinische Fragestellung: V.a. Cholelithiasis\\.br\\\\.br\\Technik: CT Abdomen mit i.v. KM\\.br\\\\.br\\Befund: Einzelner '
            '12mm Gallenstein in der Gallenblase. Keine Cholezystitis.\\.br\\Leber, Milz und Pankreas unauffaellig.\\.br\\Keine freie Fluessigkeit.\\.br\\\\.br\\'
            'Beurteilung: Solitaerer Gallenstein, elektive Cholezystektomie empfohlen.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='DIAG', cwe_2='Diagnose')
        obx_2.obx_5 = 'K80.2 Cholelithiasis ohne Cholezystitis'
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
    """ Based on live/at/at-sap-ish.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SWISSLAB')
        msh.sending_facility = HD(hd_1='LKH_SALZBURG')
        msh.receiving_application = HD(hd_1='SAP-ISH')
        msh.receiving_facility = HD(hd_1='SALK_SALZBURG')
        msh.date_time_of_message = '20240319072015'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'LAB20240319072015001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT005923', cx_4='KIS', cx_5='PI'), CX(cx_1='1871150365', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='WALLNER', xpn_2='FRANZISKA', xpn_3='HEDWIG')
        pid.date_time_of_birth = '19650315'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='0312', pl_3='01', pl_4='LKH')
        pv1.attending_doctor = XCN(xcn_1='PFEIFFER', xcn_2='DIETRICH', xcn_5='DR.')
        pv1.consulting_doctor = XCN(xcn_1='SUR')

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
        orc.placer_order_number = EI(ei_1='LABORD001')
        orc.filler_order_number = EI(ei_1='LABORD001F')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='LABORD001')
        obr.filler_order_number = EI(ei_1='LABORD001F')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Blutbild', cwe_3='L')
        obr.observation_date_time = '20240319060000'
        obr.obr_15 = 'PFEIFFER^DIETRICH^^^DR.'
        obr.filler_field_2 = 'ACC20240319001'
        obr.result_status = '20240319072000'
        obr.obr_28 = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='WBC', cwe_2='Leukozyten', cwe_3='LN')
        obx.obx_5 = '8.2'
        obx.units = CWE(cwe_1='10*3/uL')
        obx.reference_range = '4.0-10.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240319072000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='RBC', cwe_2='Erythrozyten', cwe_3='LN')
        obx_2.obx_5 = '4.65'
        obx_2.units = CWE(cwe_1='10*6/uL')
        obx_2.reference_range = '4.2-5.4'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240319072000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='HGB', cwe_2='Haemoglobin', cwe_3='LN')
        obx_3.obx_5 = '13.8'
        obx_3.units = CWE(cwe_1='g/dL')
        obx_3.reference_range = '12.0-16.0'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240319072000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='HCT', cwe_2='Haematokrit', cwe_3='LN')
        obx_4.obx_5 = '41.2'
        obx_4.units = CWE(cwe_1='%')
        obx_4.reference_range = '36.0-46.0'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240319072000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='PLT', cwe_2='Thrombozyten', cwe_3='LN')
        obx_5.obx_5 = '245'
        obx_5.units = CWE(cwe_1='10*3/uL')
        obx_5.reference_range = '150-400'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20240319072000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='CRP', cwe_2='C-reaktives Protein', cwe_3='LN')
        obx_6.obx_5 = '2.8'
        obx_6.units = CWE(cwe_1='mg/L')
        obx_6.reference_range = '0.0-5.0'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20240319072000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='KREA', cwe_2='Kreatinin', cwe_3='LN')
        obx_7.obx_5 = '0.9'
        obx_7.units = CWE(cwe_1='mg/dL')
        obx_7.reference_range = '0.6-1.2'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20240319072000'

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
    """ Based on live/at/at-sap-ish.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SYNGOSHARE')
        msh.sending_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.receiving_application = HD(hd_1='SAP-ISH')
        msh.receiving_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.date_time_of_message = '20240318163000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'SS20240318163000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.country_code = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT005923', cx_4='KISS', cx_5='PI'), CX(cx_1='1871150365', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='WALLNER', xpn_2='FRANZISKA', xpn_3='HEDWIG')
        pid.date_time_of_birth = '19650315'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='0312', pl_3='01', pl_4='LKI')
        pv1.attending_doctor = XCN(xcn_1='PFEIFFER', xcn_2='DIETRICH', xcn_5='DR.')
        pv1.consulting_doctor = XCN(xcn_1='SUR')
        pv1.re_admission_indicator = CWE(cwe_1='7')
        pv1.vip_indicator = CWE(cwe_1='PFEIFFER', cwe_2='DIETRICH', cwe_5='DR.')
        pv1.admitting_doctor = XCN(xcn_1='IP')
        pv1.delete_account_date = 'LKI'
        pv1.servicing_facility = CWE(cwe_1='A')
        pv1.pending_location = PL(pl_1='20240315083000')

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
        obr.observation_date_time = '20240318163000'
        obr.specimen_action_code = 'F'
        obr.placer_field_1 = 'ACC20240318001'
        obr.obr_23 = 'RAD^Radiologie^RAD'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='RPT20240318001', cwe_2='CT Abdomen Befund', cwe_4='CONT001', cwe_5='Radiologie Befunde', cwe_6='RADIOLOGY')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNTk1IDg0Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3ggWzAgMCA1OTUgODQyXQovQ29udGVudHMg'
            'NCAwIFIKL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQKL0YxIDE4IFRmCjEwMCA3'
            'MDAgVGQKKENUIEFiZG9tZW4gQmVmdW5kKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwgL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0'
            'aWNhCj4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTU2IDAwMDAwIG4gCjAw'
            'MDAwMDAzMzYgMDAwMDAgbiAKMDAwMDAwMDQzMCAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDYKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjUxMgolJUVPRgo='
        )
        obx.interpretation_codes = CWE(cwe_1='RAD')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240318163000'

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
    """ Based on live/at/at-sap-ish.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='SYNGOSHARE')
        msh.receiving_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.date_time_of_message = '20240318162000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'RIS20240318162000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.country_code = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT005923', cx_4='KISS', cx_5='PI')
        pid.patient_name = XPN(xpn_1='WALLNER', xpn_2='FRANZISKA', xpn_3='HEDWIG')
        pid.date_time_of_birth = '19650315'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.visit_number = CX(cx_1='VIS20240315001', cx_4='KISS')
        pv1.total_payments = 'V'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.observation_date_time = '20240318162000'
        obr.placer_field_1 = 'ACC20240318001'
        obr.obr_23 = 'RAD^Radiologie^RAD'

        # .. build the COMMON_ORDER group ..
        common_order = MdmT02CommonOrder()
        common_order.obr = obr

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='RAD', cwe_2='Radiologischer Befund', cwe_3='LOCAL')
        txa.document_content_presentation = 'PDF^PDF^LOCAL'
        txa.transcription_date_time = '20240318162000'
        txa.assigned_document_authenticator = XCN(xcn_1='KASTNER', xcn_2='RUPRECHT', xcn_5='DR.', xcn_13='RAD&Radiologie&LOCAL', xcn_14='A')
        txa.placer_order_number = EI(ei_1='RPT20240318001')
        txa.document_confidentiality_status = 'Befund_CT_Abdomen.pdf'
        txa.document_availability_status = 'AU'
        txa.txa_29 = 'CONT001^Radiologie Befunde^RADIOLOGY'
        txa.txa_30 = 'CT Abdomen Befund'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNTk1IDg0Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3ggWzAgMCA1OTUgODQyXQovQ29udGVudHMg'
            'NCAwIFIKL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4gPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA0NCA+PgpzdHJlYW0KQlQKL0YxIDE4IFRmCjEwMCA3'
            'MDAgVGQKKENUIEFiZG9tZW4gQmVmdW5kKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwgL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0'
            'aWNhCj4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTU2IDAwMDAwIG4gCjAw'
            'MDAwMDAzMzYgMDAwMDAgbiAKMDAwMDAwMDQzMCAwMDAwMCBuIAp0cmFpbGVyCjw8IC9TaXplIDYKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjUxMgolJUVPRgo='
        )
        obx.interpretation_codes = CWE(cwe_1='RAD')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240318162000'

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx

        # .. assemble the full message ..
        msg = MDM_T02()
        msg.msh = msh
        msg.pid = pid
        msg.pv1 = pv1
        msg.common_order = common_order
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
    """ Based on live/at/at-sap-ish.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.receiving_application = HD(hd_1='SAP-ISH')
        msh.receiving_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.date_time_of_message = '20240318085500'
        msh.message_type = MSG(msg_1='QRY', msg_2='A19')
        msh.message_control_id = 'QRY20240318085500001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build QRD ..
        qrd = QRD()
        qrd.qrd_1 = '20240318085500'
        qrd.qrd_2 = 'R'
        qrd.qrd_3 = 'I'
        qrd.qrd_4 = 'QRY20240318085500001'
        qrd.qrd_7 = '1^RD'
        qrd.qrd_8 = 'PAT005923^^^KISS^PI'
        qrd.qrd_9 = 'DEM'

        # .. assemble the full message ..
        msg = QRY_A19()
        msg.msh = msh
        msg.qrd = qrd

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
    """ Based on live/at/at-sap-ish.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.date_time_of_message = '20240318085501'
        msh.message_type = MSG(msg_1='ADR', msg_2='A19')
        msh.message_control_id = 'ADR20240318085501001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'QRY20240318085500001'

        # .. build QRD ..
        qrd = QRD()
        qrd.qrd_1 = '20240318085500'
        qrd.qrd_2 = 'R'
        qrd.qrd_3 = 'I'
        qrd.qrd_4 = 'QRY20240318085500001'
        qrd.qrd_7 = '1^RD'
        qrd.qrd_8 = 'PAT005923^^^KISS^PI'
        qrd.qrd_9 = 'DEM'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT005923', cx_4='KISS', cx_5='PI'), CX(cx_1='1871150365', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='WALLNER', xpn_2='FRANZISKA', xpn_3='HEDWIG')
        pid.date_time_of_birth = '19650315'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='MUSEUMSTRASSE 14', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT', xad_7='H')
        pid.pid_13 = '^PRN^PH^^0043^512^738294'
        pid.primary_language = CWE(cwe_1='DEU')
        pid.marital_status = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='VIS20240315001', cx_4='TIROL_KLINIKEN', cx_5='VN')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='WALLNER', xpn_2='GOTTFRIED')
        nk1.address = XAD(xad_1='MUSEUMSTRASSE 14', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT', xad_7='H')
        nk1.nk1_5 = '^PRN^PH^^0043^512^738295'
        nk1.contact_role = CWE(cwe_1='NOK')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='0312', pl_3='01', pl_4='LKI')
        pv1.pv1_7 = 'PFEIFFER^DIETRICH^^^DR.^^LANR^^^L'
        pv1.hospital_service = CWE(cwe_1='SUR')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.pv1_17 = 'PFEIFFER^DIETRICH^^^DR.^^LANR^^^L'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.discharge_disposition = CWE(cwe_1='LKI')
        pv1.pv1_40 = 'A'
        pv1.prior_temporary_location = PL(pl_1='20240315083000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='GKK', cwe_2='Gebietskrankenkasse')
        in1.insurance_company_name = XON(xon_1='OEGK')
        in1.insurance_company_address = XAD(xad_1='WIENERBERGSTRASSE 15-19', xad_3='WIEN', xad_5='1100', xad_6='AUT')
        in1.insureds_group_emp_name = XON(xon_1='20240101')
        in1.plan_effective_date = '20241231'
        in1.plan_type = CWE(cwe_1='WALLNER', cwe_2='FRANZISKA', cwe_3='HEDWIG')
        in1.name_of_insured = XPN(xpn_1='01')
        in1.insureds_relationship_to_patient = CWE(cwe_1='19650315')
        in1.insureds_date_of_birth = 'MUSEUMSTRASSE 14^^INNSBRUCK^T^6020^AUT'

        # .. build the INSURANCE group ..
        insurance = AdrA19Insurance()
        insurance.in1 = in1

        # .. build the QUERY_RESPONSE group ..
        query_response = AdrA19QueryResponse()
        query_response.pid = pid
        query_response.nk1 = nk1
        query_response.pv1 = pv1
        query_response.insurance = insurance

        # .. assemble the full message ..
        msg = ADR_A19()
        msg.msh = msh
        msg.msa = msa
        msg.qrd = qrd
        msg.query_response = query_response

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
    """ Based on live/at/at-sap-ish.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SAP-ISH')
        msh.sending_facility = HD(hd_1='AKH_WIEN')
        msh.receiving_application = HD(hd_1='ORBIS')
        msh.receiving_facility = HD(hd_1='AKH_WIEN')
        msh.date_time_of_message = '20240820141200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A06')
        msh.message_control_id = 'AKH20240820141200001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A06'
        evn.recorded_date_time = '20240820141000'
        evn.operator_id = XCN(xcn_1='SCHUSTER', xcn_2='NORBERT', xcn_5='DR.')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT055667', cx_4='KIS', cx_5='PI'), CX(cx_1='3344050683', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='STEINER', xpn_2='ROLAND', xpn_3='BERNHARD')
        pid.date_time_of_birth = '19830605'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='GRABEN 12', xad_3='WIEN', xad_5='1010', xad_6='AUT', xad_7='H')
        pid.pid_13 = '^PRN^PH^^0043^1^3127788'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='NOTAUF', pl_2='0101', pl_3='01', pl_4='AKH')
        pv1.pv1_7 = 'SCHUSTER^NORBERT^^^DR.^^LANR^^^L'
        pv1.hospital_service = CWE(cwe_1='EMR')
        pv1.admit_source = CWE(cwe_1='E')
        pv1.pv1_17 = 'SCHUSTER^NORBERT^^^DR.^^LANR^^^L'
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.discharge_disposition = CWE(cwe_1='AKH_WIEN')
        pv1.pv1_40 = 'A'
        pv1.prior_temporary_location = PL(pl_1='20240820100000')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.expected_admit_date_time = '20240825'

        # .. assemble the full message ..
        msg = ADT_A06()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/at/at-sap-ish.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EventServer')
        msh.sending_facility = HD(hd_1='RAD', hd_2='LKI_RADIOLOGIE', hd_3='L')
        msh.receiving_facility = HD(hd_1='SAP-ISH')
        msh.date_time_of_message = 'TIROL_KLINIKEN'
        msh.security = '20240318170000'
        msh.message_control_id = 'ORU^R01^ORU_R01'
        msh.processing_id = PT(pt_1='SS20240318170000001')
        msh.version_id = VID(vid_1='P')
        msh.sequence_number = '2.8.1'
        msh.continuation_pointer = '1'
        msh.principal_language_of_message = CWE(cwe_1='UNICODE UTF-8')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT005923', cx_4='KISS', cx_5='PI'), CX(cx_1='1871150365', cx_4='SV', cx_5='SS')]
        pid.patient_name = XPN(xpn_1='WALLNER', xpn_2='FRANZISKA', xpn_3='HEDWIG')
        pid.date_time_of_birth = '19650315'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='A', cwe_2='austrian')
        pid.patient_address = XAD(xad_1='MUSEUMSTRASSE 14', xad_3='INNSBRUCK', xad_4='T', xad_5='6020', xad_6='AUT')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I', cwe_2='inpatient')
        pv1.visit_number = CX(cx_1='VIS20240315001', cx_4='KISS')
        pv1.service_episode_identifier = CX(cx_1='ALT20240315001', cx_4='KISS')
        pv1.pv1_55 = 'V'

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'OP'
        orc.placer_order_number = EI(ei_1='ORD20240318001')
        orc.filler_order_number = EI(ei_1='ORD20240318001F')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD20240318001')
        obr.filler_order_number = EI(ei_1='ORD20240318001F')
        obr.universal_service_identifier = CWE(cwe_1='CT-ABD', cwe_2='CT Abdomen mit KM')
        obr.observation_date_time = '20240318090000'
        obr.obr_17 = 'ACC20240318001'
        obr.filler_field_2 = '20240318170000'
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'RP'
        obx.observation_identifier = CWE(cwe_1='1.2.840.113619.2.55.3.4.1234.20240318090000', cwe_2='CT Abdomen', cwe_4='STUDY001')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = 'RP:2:TIROL_KLINIKEN:DICOM_STUDY:1.2.840.113619.2.55.3.4.1234.20240318090000^^^^100'
        obx.interpretation_codes = CWE(cwe_1='CT')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240318170000'
        obx.producers_id = CWE(cwe_1='RAD', cwe_2='Radiologie')

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
    """ Based on live/at/at-sap-ish.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SYNGOSHARE')
        msh.sending_facility = HD(hd_1='TIROL_KLINIKEN')
        msh.receiving_application = HD(hd_1='SAP-ISH')
        msh.receiving_facility = HD(hd_1='LKI_INNSBRUCK')
        msh.date_time_of_message = '20240319080000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T09', msg_3='MDM_T01')
        msh.message_control_id = 'SS20240319080000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.1')
        msh.country_code = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PAT005923', cx_4='KISS', cx_5='PI')
        pid.patient_name = XPN(xpn_1='WALLNER', xpn_2='FRANZISKA', xpn_3='HEDWIG')
        pid.date_time_of_birth = '19650315'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.visit_number = CX(cx_1='VIS20240315001', cx_4='KISS')
        pv1.total_payments = 'V'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.observation_date_time = '20240319080000'
        obr.placer_field_1 = 'ACC20240318001'
        obr.obr_23 = 'RAD^Radiologie^RAD'

        # .. build the COMMON_ORDER group ..
        common_order = MdmT01CommonOrder()
        common_order.obr = obr

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='RAD', cwe_2='Radiologischer Befund korrigiert', cwe_3='LOCAL')
        txa.document_content_presentation = 'PDF^PDF^LOCAL'
        txa.transcription_date_time = '20240319080000'
        txa.assigned_document_authenticator = XCN(xcn_1='KASTNER', xcn_2='RUPRECHT', xcn_5='DR.', xcn_13='RAD&Radiologie&LOCAL', xcn_14='A')
        txa.placer_order_number = EI(ei_1='RPT20240318001')
        txa.document_confidentiality_status = 'Befund_CT_Abdomen_v2.pdf'
        txa.document_availability_status = 'AU'
        txa.creating_facility = HD(hd_1='CONT001', hd_2='Radiologie Befunde', hd_3='RADIOLOGY')
        txa.creating_specialty = CWE(cwe_1='CT Abdomen korrigierter Befund')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.observation_sub_id = OG(og_1='1')
        obx.interpretation_codes = CWE(cwe_1='RAD')
        obx.producers_id = CWE(cwe_1='20240319080000')

        # .. assemble the full message ..
        msg = MDM_T01()
        msg.msh = msh
        msg.pid = pid
        msg.pv1 = pv1
        msg.common_order = common_order
        msg.txa = txa
        msg.extra_segments = [obx]

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
