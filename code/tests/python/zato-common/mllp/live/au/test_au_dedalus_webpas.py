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
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, AdtA05NextOfKin, AdtA39Patient, MdmT02Observation, OrmO01Order, OrmO01OrderDetail, \
    OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, \
    SiuS12GeneralResource, SiuS12LocationResource, SiuS12Patient, SiuS12Resources
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, ADT_A05, ADT_A39, MDM_T02, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIG, AIL, DG1, EVN, IN1, MRG, MSH, NK1, OBR, OBX, ORC, PD1, PID, PV1, PV2, RGS, SCH, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('au', 'au-dedalus-webpas.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/au/au-dedalus-webpas.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WEBPAS')
        msh.sending_facility = HD(hd_1='ROYAL_MELBOURNE')
        msh.receiving_application = HD(hd_1='CERNER_LAB')
        msh.receiving_facility = HD(hd_1='ROYAL_MELBOURNE')
        msh.date_time_of_message = '20240315083022'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        msh.message_control_id = 'MSG00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20240315083000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN10234567', cx_4='WEBPAS', cx_5='MR'), CX(cx_1='32145678901', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1="O'BRIEN", xpn_2='Kathleen', xpn_3='Mary', xpn_5='Mrs')
        pid.date_time_of_birth = '19580214'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='42 Bourke Street', xad_3='Melbourne', xad_4='VIC', xad_5='3000', xad_6='AU')
        pid.pid_13 = '+61398765432^^^kathleen.obrien@email.com.au'
        pid.pid_14 = '+61398765433'
        pid.primary_language = CWE(cwe_1='EN')
        pid.marital_status = CWE(cwe_1='M')
        pid.religion = CWE(cwe_1='CAT')
        pid.patient_account_number = CX(cx_1='V00123456', cx_4='WEBPAS', cx_5='AN')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1="O'BRIEN", xpn_2='Patrick', xpn_3='James', xpn_5='Mr')
        nk1.relationship = CWE(cwe_1='SPO')
        nk1.address = XAD(xad_1='18 Bourke Street', xad_3='Melbourne', xad_4='VIC', xad_5='3000', xad_6='AU')
        nk1.nk1_5 = '+61412345678'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4W', pl_2='412', pl_3='1', pl_6='ROYAL_MELBOURNE')
        pv1.pv1_7 = '67234^NGUYEN^Thi^Lan^^^Dr'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = '67234^NGUYEN^Thi^Lan^^^Dr'
        pv1.patient_type = CWE(cwe_1='IN')
        pv1.financial_class = FC(fc_1='PBS')
        pv1.servicing_facility = CWE(cwe_1='ROYAL_MELBOURNE')
        pv1.admit_date_time = '20240315083000'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='BUPA001', cwe_2='BUPA')
        in1.insurance_company_id = CX(cx_1='BUPA', cx_2='Bupa Health Insurance')
        in1.in1_4 = 'GPO Box 500^^Melbourne^VIC^3001^AU'
        in1.insurance_company_address = XAD(xad_1='+611300362481')
        in1.in1_7 = 'GRP12345'
        in1.group_number = 'EMPLOYER01'
        in1.plan_effective_date = '20230101'
        in1.plan_expiration_date = '20251231'
        in1.plan_type = CWE(cwe_1='FAM')
        in1.name_of_insured = XPN(xpn_1="O'BRIEN", xpn_2='Kathleen', xpn_3='Mary')
        in1.insureds_relationship_to_patient = CWE(cwe_1='SEL')
        in1.insureds_date_of_birth = '19580214'
        in1.insureds_address = XAD(xad_1='42 Bourke Street', xad_3='Melbourne', xad_4='VIC', xad_5='3000', xad_6='AU')

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
    """ Based on live/au/au-dedalus-webpas.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IPM')
        msh.sending_facility = HD(hd_1='PRINCESS_ALEXANDRA')
        msh.receiving_application = HD(hd_1='HBCIS')
        msh.receiving_facility = HD(hd_1='PRINCESS_ALEXANDRA')
        msh.date_time_of_message = '20240422141530'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02')
        msh.message_control_id = 'MSG00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20240422141500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN20456789', cx_4='IPM', cx_5='MR'), CX(cx_1='21987654321', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='WILLIAMS', xpn_2='David', xpn_3='James', xpn_5='Mr')
        pid.date_time_of_birth = '19720830'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='7 Coronation Drive', xad_3='Toowong', xad_4='QLD', xad_5='4066', xad_6='AU')
        pid.pid_13 = '+61733456789^^^d.williams@email.com.au'
        pid.primary_language = CWE(cwe_1='EN')
        pid.marital_status = CWE(cwe_1='S')
        pid.religion = CWE(cwe_1='NON')
        pid.patient_account_number = CX(cx_1='V00234567', cx_4='IPM', cx_5='AN')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='ICU03', pl_3='1', pl_6='PRINCESS_ALEXANDRA')
        pv1.pv1_7 = '45123^PATEL^Rajesh^Kumar^^^Dr'
        pv1.hospital_service = CWE(cwe_1='SUR')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.pv1_17 = '45123^PATEL^Rajesh^Kumar^^^Dr'
        pv1.patient_type = CWE(cwe_1='IN')
        pv1.financial_class = FC(fc_1='MED')
        pv1.servicing_facility = CWE(cwe_1='PRINCESS_ALEXANDRA')
        pv1.admit_date_time = '20240420090000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Post cardiac surgery monitoring')

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
    """ Based on live/au/au-dedalus-webpas.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WEBPAS')
        msh.sending_facility = HD(hd_1='MONASH_HEALTH')
        msh.receiving_application = HD(hd_1='EMR')
        msh.receiving_facility = HD(hd_1='MONASH_HEALTH')
        msh.date_time_of_message = '20240518160045'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03')
        msh.message_control_id = 'MSG00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20240518160000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN30567890', cx_4='WEBPAS', cx_5='MR'), CX(cx_1='43216789012', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='THOMPSON', xpn_2='Margaret', xpn_3='Elizabeth', xpn_5='Ms')
        pid.date_time_of_birth = '19451117'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='156 Princes Highway', xad_3='Dandenong', xad_4='VIC', xad_5='3175', xad_6='AU')
        pid.pid_13 = '+61397912345'
        pid.marital_status = CWE(cwe_1='W')
        pid.religion = CWE(cwe_1='NON')
        pid.patient_account_number = CX(cx_1='V00345678', cx_4='WEBPAS', cx_5='AN')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='6E', pl_2='602', pl_3='1', pl_6='MONASH_HEALTH')
        pv1.pv1_7 = '78456^KUMAR^Anish^Raj^^^Dr'
        pv1.hospital_service = CWE(cwe_1='GEN')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = '78456^KUMAR^Anish^Raj^^^Dr'
        pv1.patient_type = CWE(cwe_1='IN')
        pv1.financial_class = FC(fc_1='PBS')
        pv1.servicing_facility = CWE(cwe_1='MONASH_HEALTH')
        pv1.admit_date_time = '20240515101500'
        pv1.total_charges = '20240518160000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I10', cwe_2='Essential hypertension', cwe_3='I10')
        dg1.diagnosis_type = CWE(cwe_1='AD')

        # .. build DG1 ..
        dg1_2 = DG1()
        dg1_2.set_id_dg1 = '2'
        dg1_2.dg1_2 = 'I10'
        dg1_2.diagnosis_code_dg1 = CWE(cwe_1='E11.9', cwe_2='Type 2 diabetes mellitus without complications', cwe_3='I10')
        dg1_2.diagnosis_type = CWE(cwe_1='SD')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = [dg1, dg1_2]

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
    """ Based on live/au/au-dedalus-webpas.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DEDALUS_PAS')
        msh.sending_facility = HD(hd_1='FIONA_STANLEY')
        msh.receiving_application = HD(hd_1='TOPAS')
        msh.receiving_facility = HD(hd_1='FIONA_STANLEY')
        msh.date_time_of_message = '20240603091200'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04')
        msh.message_control_id = 'MSG00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20240603091000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN40678901', cx_4='DEDALUS_PAS', cx_5='MR'), CX(cx_1='54327890123', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='CHEN', xpn_2='Wei', xpn_3='Lin', xpn_5='Mr')
        pid.date_time_of_birth = '19880512'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='23 Mounts Bay Road', xad_3='Perth', xad_4='WA', xad_5='6000', xad_6='AU')
        pid.pid_13 = '+61892345678^^^wei.chen@email.com.au'
        pid.primary_language = CWE(cwe_1='MN')
        pid.marital_status = CWE(cwe_1='M')
        pid.religion = CWE(cwe_1='BUD')
        pid.patient_account_number = CX(cx_1='V00456789', cx_4='DEDALUS_PAS', cx_5='AN')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ENDO', pl_2='ENDO01', pl_3='1', pl_6='FIONA_STANLEY')
        pv1.pv1_7 = '89123^MORRISON^Sarah^Jane^^^Dr'
        pv1.hospital_service = CWE(cwe_1='GAS')
        pv1.admit_source = CWE(cwe_1='5')
        pv1.pv1_17 = '89123^MORRISON^Sarah^Jane^^^Dr'
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.financial_class = FC(fc_1='MED')
        pv1.servicing_facility = CWE(cwe_1='FIONA_STANLEY')
        pv1.admit_date_time = '20240603091000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_2='Upper GI endoscopy')
        pv2.expected_discharge_date_time = '20240603'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/au/au-dedalus-webpas.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WEBPAS')
        msh.sending_facility = HD(hd_1='ALFRED_HEALTH')
        msh.receiving_application = HD(hd_1='PIR')
        msh.receiving_facility = HD(hd_1='ALFRED_HEALTH')
        msh.date_time_of_message = '20240710143000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08')
        msh.message_control_id = 'MSG00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20240710143000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN50789012', cx_4='WEBPAS', cx_5='MR'), CX(cx_1='65438901234', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='SINGH', xpn_2='Gurpreet', xpn_3='Kaur', xpn_5='Mrs')
        pid.date_time_of_birth = '19650923'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='89 Commercial Road', xad_3='Prahran', xad_4='VIC', xad_5='3181', xad_6='AU')
        pid.pid_13 = '+61395551234^^^g.singh@email.com.au'
        pid.pid_14 = '+61395551235'
        pid.primary_language = CWE(cwe_1='PN')
        pid.marital_status = CWE(cwe_1='M')
        pid.religion = CWE(cwe_1='HIN')
        pid.patient_account_number = CX(cx_1='V00567890', cx_4='WEBPAS', cx_5='AN')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='SINGH', xpn_2='Harjeet', xpn_3='Pal', xpn_5='Mr')
        nk1.relationship = CWE(cwe_1='SPO')
        nk1.address = XAD(xad_1='89 Commercial Road', xad_3='Prahran', xad_4='VIC', xad_5='3181', xad_6='AU')
        nk1.nk1_5 = '+61412987654'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build NK1 ..
        nk1_2 = NK1()
        nk1_2.set_id_nk1 = '2'
        nk1_2.name = XPN(xpn_1='SINGH', xpn_2='Amrita', xpn_4='Ms')
        nk1_2.relationship = CWE(cwe_1='DAU')
        nk1_2.address = XAD(xad_1='15 Chapel Street', xad_3='Windsor', xad_4='VIC', xad_5='3181', xad_6='AU')
        nk1_2.nk1_5 = '+61413456789'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin_2 = AdtA01NextOfKin()
        next_of_kin_2.nk1 = nk1_2

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3S', pl_2='301', pl_3='1', pl_6='ALFRED_HEALTH')
        pv1.pv1_7 = '34567^LEE^Jonathan^Wei^^^Dr'
        pv1.hospital_service = CWE(cwe_1='ORT')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = '34567^LEE^Jonathan^Wei^^^Dr'
        pv1.patient_type = CWE(cwe_1='IN')
        pv1.financial_class = FC(fc_1='PBS')
        pv1.servicing_facility = CWE(cwe_1='ALFRED_HEALTH')
        pv1.admit_date_time = '20240708120000'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = [next_of_kin, next_of_kin_2]
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
    """ Based on live/au/au-dedalus-webpas.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DEDALUS_IPM')
        msh.sending_facility = HD(hd_1='SA_HEALTH')
        msh.receiving_application = HD(hd_1='CRRS')
        msh.receiving_facility = HD(hd_1='SA_HEALTH')
        msh.date_time_of_message = '20240812100530'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28')
        msh.message_control_id = 'MSG00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20240812100500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN60890123', cx_4='DEDALUS_IPM', cx_5='MR'), CX(cx_1='76549012345', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='KOWALSKI', xpn_2='Anna', xpn_3='Marie', xpn_5='Ms')
        pid.date_time_of_birth = '19910415'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='34 King William Street', xad_3='Adelaide', xad_4='SA', xad_5='5000', xad_6='AU')
        pid.pid_13 = '+61882345678^^^a.kowalski@email.com.au'
        pid.primary_language = CWE(cwe_1='PL')
        pid.marital_status = CWE(cwe_1='S')
        pid.religion = CWE(cwe_1='NON')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='KOWALSKI', xpn_2='Jan', xpn_3='Stefan', xpn_5='Mr')
        nk1.relationship = CWE(cwe_1='FTH')
        nk1.address = XAD(xad_1='12 Rundle Mall', xad_3='Adelaide', xad_4='SA', xad_5='5000', xad_6='AU')
        nk1.nk1_5 = '+61883456789'

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
    """ Based on live/au/au-dedalus-webpas.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WEBPAS')
        msh.sending_facility = HD(hd_1='BARWON_HEALTH')
        msh.receiving_application = HD(hd_1='CDR')
        msh.receiving_facility = HD(hd_1='BARWON_HEALTH')
        msh.date_time_of_message = '20240901112045'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31')
        msh.message_control_id = 'MSG00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20240901112000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN70901234', cx_4='WEBPAS', cx_5='MR'), CX(cx_1='87650123456', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='NGUYEN', xpn_2='Thanh', xpn_3='Duc', xpn_5='Mr')
        pid.date_time_of_birth = '19780302'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='67 Malop Street', xad_3='Geelong', xad_4='VIC', xad_5='3220', xad_6='AU')
        pid.pid_13 = '+61352345678^^^t.nguyen@email.com.au'
        pid.primary_language = CWE(cwe_1='VI')
        pid.marital_status = CWE(cwe_1='M')
        pid.religion = CWE(cwe_1='BUD')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = '12345^TRAN^Minh^Hoang^^^Dr'

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1

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
    """ Based on live/au/au-dedalus-webpas.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IPM')
        msh.sending_facility = HD(hd_1='GOLD_COAST_UH')
        msh.receiving_application = HD(hd_1='PIX')
        msh.receiving_facility = HD(hd_1='GOLD_COAST_UH')
        msh.date_time_of_message = '20241005090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40')
        msh.message_control_id = 'MSG00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A40'
        evn.recorded_date_time = '20241005090000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN80012345', cx_4='IPM', cx_5='MR'), CX(cx_1='98761234567', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='ROBERTSON', xpn_2='James', xpn_3='Andrew', xpn_5='Mr')
        pid.date_time_of_birth = '19830719'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='12 Surfers Paradise Blvd', xad_3='Surfers Paradise', xad_4='QLD', xad_5='4217', xad_6='AU')
        pid.pid_13 = '+61755678901'

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = [CX(cx_1='MRN80012399', cx_4='IPM', cx_5='MR'), CX(cx_1='98761234999', cx_4='AUSHIC', cx_5='MC')]
        mrg.prior_patient_account_number = CX(cx_1='V00678901')

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
    """ Based on live/au/au-dedalus-webpas.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WEBPAS')
        msh.sending_facility = HD(hd_1='AUSTIN_HEALTH')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='AUSTIN_HEALTH')
        msh.date_time_of_message = '20240228110000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MSG00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN90123456', cx_4='WEBPAS', cx_5='MR'), CX(cx_1='10987654321', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='MURPHY', xpn_2='Sean', xpn_3='Patrick', xpn_5='Mr')
        pid.date_time_of_birth = '19670803'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='45 Studley Road', xad_3='Heidelberg', xad_4='VIC', xad_5='3084', xad_6='AU')
        pid.pid_13 = '+61394571234'
        pid.marital_status = CWE(cwe_1='M')
        pid.religion = CWE(cwe_1='CAT')
        pid.patient_account_number = CX(cx_1='V00789012', cx_4='WEBPAS', cx_5='AN')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='7N', pl_2='702', pl_3='1', pl_6='AUSTIN_HEALTH')
        pv1.pv1_7 = '56789^WONG^Andrew^Ming^^^Dr'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = '56789^WONG^Andrew^Ming^^^Dr'
        pv1.patient_type = CWE(cwe_1='IN')
        pv1.financial_class = FC(fc_1='PBS')

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
        orc.placer_order_number = EI(ei_1='ORD100001', ei_2='WEBPAS')
        orc.parent_order = EIP(eip_1='20240228110000')
        orc.orc_11 = '56789^WONG^Andrew^Ming^^^Dr'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD100001', ei_2='WEBPAS')
        obr.universal_service_identifier = CWE(cwe_1='57169-0', cwe_2='CT CHEST W CONTRAST', cwe_3='LN')
        obr.observation_date_time = '20240228120000'
        obr.obr_15 = '56789^WONG^Andrew^Ming^^^Dr'
        obr.result_status = '1^^^20240228120000^^R'

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
    """ Based on live/au/au-dedalus-webpas.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DEDALUS_PAS')
        msh.sending_facility = HD(hd_1='ROYAL_BRISBANE')
        msh.receiving_application = HD(hd_1='AUSLAB')
        msh.receiving_facility = HD(hd_1='ROYAL_BRISBANE')
        msh.date_time_of_message = '20240415080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MSG00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN01234567', cx_4='DEDALUS_PAS', cx_5='MR'), CX(cx_1='21098765432', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='BROWN', xpn_2='Elizabeth', xpn_3='Anne', xpn_5='Mrs')
        pid.date_time_of_birth = '19550620'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='89 Butterfield Street', xad_3='Herston', xad_4='QLD', xad_5='4006', xad_6='AU')
        pid.pid_13 = '+61736781234'
        pid.marital_status = CWE(cwe_1='W')
        pid.religion = CWE(cwe_1='NON')
        pid.patient_account_number = CX(cx_1='V00890123', cx_4='DEDALUS_PAS', cx_5='AN')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='9A', pl_2='901', pl_3='1', pl_6='ROYAL_BRISBANE')
        pv1.pv1_7 = '23456^AHMED^Fatima^Zahra^^^Dr'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = '23456^AHMED^Fatima^Zahra^^^Dr'
        pv1.patient_type = CWE(cwe_1='IN')
        pv1.financial_class = FC(fc_1='MED')

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
        orc.placer_order_number = EI(ei_1='ORD200001', ei_2='DEDALUS_PAS')
        orc.parent_order = EIP(eip_1='20240415080000')
        orc.orc_11 = '23456^AHMED^Fatima^Zahra^^^Dr'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD200001', ei_2='DEDALUS_PAS')
        obr.universal_service_identifier = CWE(cwe_1='26604-1', cwe_2='FULL BLOOD COUNT', cwe_3='LN')
        obr.observation_date_time = '20240415083000'
        obr.obr_15 = '23456^AHMED^Fatima^Zahra^^^Dr'

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
        obr_2.placer_order_number = EI(ei_1='ORD200001', ei_2='DEDALUS_PAS')
        obr_2.universal_service_identifier = CWE(cwe_1='2947-0', cwe_2='UREA AND ELECTROLYTES', cwe_3='LN')
        obr_2.observation_date_time = '20240415083000'
        obr_2.obr_15 = '23456^AHMED^Fatima^Zahra^^^Dr'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [obr_2]

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
    """ Based on live/au/au-dedalus-webpas.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AUSLAB')
        msh.sending_facility = HD(hd_1='PRINCESS_ALEXANDRA')
        msh.receiving_application = HD(hd_1='DEDALUS_PAS')
        msh.receiving_facility = HD(hd_1='PRINCESS_ALEXANDRA')
        msh.date_time_of_message = '20240415143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MSG00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN02398714', cx_4='DEDALUS_PAS', cx_5='MR'), CX(cx_1='21099817264', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='MAKINI', xpn_2='Ngozi', xpn_3='Adaeze', xpn_5='Mrs')
        pid.date_time_of_birth = '19580915'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='14 Cornwall Street', xad_3='Annerley', xad_4='QLD', xad_5='4103', xad_6='AU')
        pid.pid_13 = '+61733915607'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='7B', pl_2='715', pl_3='2', pl_6='PRINCESS_ALEXANDRA')
        pv1.pv1_7 = '23801^OSULLIVAN^Nuala^Brigid^^^Dr'

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
        orc.placer_order_number = EI(ei_1='ORD201118', ei_2='DEDALUS_PAS')
        orc.filler_order_number = EI(ei_1='LAB300114', ei_2='AUSLAB')
        orc.orc_7 = '^^^20240415083000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD201118', ei_2='DEDALUS_PAS')
        obr.filler_order_number = EI(ei_1='LAB300114', ei_2='AUSLAB')
        obr.universal_service_identifier = CWE(cwe_1='26604-1', cwe_2='FULL BLOOD COUNT', cwe_3='LN')
        obr.observation_date_time = '20240415083000'
        obr.obr_14 = '20240415090000'
        obr.obr_15 = 'BLD^Blood'
        obr.obr_16 = '23801^OSULLIVAN^Nuala^Brigid^^^Dr'
        obr.results_rpt_status_chng_date_time = '20240415143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Haemoglobin', cwe_3='LN')
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
        obx_2.observation_identifier = CWE(cwe_1='6690-2', cwe_2='White Blood Cells', cwe_3='LN')
        obx_2.obx_5 = '7.2'
        obx_2.units = CWE(cwe_1='x10', cwe_2='9/L')
        obx_2.reference_range = '4.0-11.0'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='777-3', cwe_2='Platelets', cwe_3='LN')
        obx_3.obx_5 = '245'
        obx_3.units = CWE(cwe_1='x10', cwe_2='9/L')
        obx_3.reference_range = '150-400'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='789-8', cwe_2='Red Blood Cells', cwe_3='LN')
        obx_4.obx_5 = '3.8'
        obx_4.units = CWE(cwe_1='x10', cwe_2='12/L')
        obx_4.reference_range = '3.8-5.8'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='787-2', cwe_2='Mean Cell Volume', cwe_3='LN')
        obx_5.obx_5 = '82'
        obx_5.units = CWE(cwe_1='fL')
        obx_5.reference_range = '80-100'
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
    """ Based on live/au/au-dedalus-webpas.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AUSLAB')
        msh.sending_facility = HD(hd_1='MONASH_HEALTH')
        msh.receiving_application = HD(hd_1='WEBPAS')
        msh.receiving_facility = HD(hd_1='MONASH_HEALTH')
        msh.date_time_of_message = '20240612102000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MSG00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN11234567', cx_4='WEBPAS', cx_5='MR'), CX(cx_1='32109876543', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='PATEL', xpn_2='Priya', xpn_3='Deepa', xpn_5='Ms')
        pid.date_time_of_birth = '19830411'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='22 Clayton Road', xad_3='Clayton', xad_4='VIC', xad_5='3168', xad_6='AU')
        pid.pid_13 = '+61399051234'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='5W', pl_2='501', pl_3='1', pl_6='MONASH_HEALTH')
        pv1.pv1_7 = '67890^SMITH^Rebecca^Jane^^^Dr'

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
        orc.placer_order_number = EI(ei_1='ORD300001', ei_2='WEBPAS')
        orc.filler_order_number = EI(ei_1='LAB400001', ei_2='AUSLAB')
        orc.orc_7 = '^^^20240610140000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD300001', ei_2='WEBPAS')
        obr.filler_order_number = EI(ei_1='LAB400001', ei_2='AUSLAB')
        obr.universal_service_identifier = CWE(cwe_1='87040-6', cwe_2='BLOOD CULTURE', cwe_3='LN')
        obr.observation_date_time = '20240610140000'
        obr.obr_14 = '20240610141500'
        obr.obr_15 = 'BLD^Blood'
        obr.obr_16 = '67890^SMITH^Rebecca^Jane^^^Dr'
        obr.results_rpt_status_chng_date_time = '20240612102000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Organism identified', cwe_3='LN')
        obx.obx_5 = 'ECOLI^Escherichia coli^SNM'
        obx.probability = 'A'
        obx.effective_date_of_reference_range = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18769-0', cwe_2='Comment', cwe_3='LN')
        obx_2.obx_5 = 'Growth detected at 18 hours'
        obx_2.probability = 'A'
        obx_2.effective_date_of_reference_range = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18907-6', cwe_2='Ampicillin susceptibility', cwe_3='LN')
        obx_3.obx_5 = 'R'
        obx_3.probability = 'A'
        obx_3.effective_date_of_reference_range = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18928-2', cwe_2='Gentamicin susceptibility', cwe_3='LN')
        obx_4.obx_5 = 'S'
        obx_4.probability = 'A'
        obx_4.effective_date_of_reference_range = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18932-4', cwe_2='Ceftriaxone susceptibility', cwe_3='LN')
        obx_5.obx_5 = 'S'
        obx_5.probability = 'A'
        obx_5.effective_date_of_reference_range = 'F'

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
    """ Based on live/au/au-dedalus-webpas.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WEBPAS')
        msh.sending_facility = HD(hd_1='WESTERN_HEALTH')
        msh.receiving_application = HD(hd_1='ORION')
        msh.receiving_facility = HD(hd_1='WESTERN_HEALTH')
        msh.date_time_of_message = '20240722090000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12')
        msh.message_control_id = 'MSG00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT500001', ei_2='WEBPAS')
        sch.filler_appointment_id = EI(ei_1='APT500001', ei_2='WEBPAS')
        sch.schedule_id = CWE(cwe_1='ROUTINE', cwe_2='Routine appointment', cwe_3='HL70276')
        sch.event_reason = CWE(cwe_1='FOLLOWUP', cwe_2='Follow-up', cwe_3='HL70277')
        sch.appointment_reason = CWE(cwe_1='15')
        sch.appointment_type = CWE(cwe_1='MIN')
        sch.sch_9 = '^^15^20240805140000^20240805141500'
        sch.placer_contact_address = XAD(xad_1='12345', xad_2='JONES', xad_3='Michael', xad_4='Robert', xad_7='Dr')
        sch.placer_contact_location = PL(pl_1='+61383456789')
        sch.filler_contact_person = XCN(xcn_1='123 Gordon Street', xcn_3='Footscray', xcn_4='VIC', xcn_5='3011', xcn_6='AU')
        sch.sch_17 = 'ORTH_OPD^^WESTERN_HEALTH'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN12345678', cx_4='WEBPAS', cx_5='MR'), CX(cx_1='43210987654', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='TAYLOR', xpn_2='Christopher', xpn_3='John', xpn_5='Mr')
        pid.date_time_of_birth = '19950118'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='78 Barkly Street', xad_3='Footscray', xad_4='VIC', xad_5='3011', xad_6='AU')
        pid.pid_13 = '+61412678901'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='ORTH_OPD', pl_2='OPD01', pl_3='1', pl_6='WESTERN_HEALTH')
        pv1.pv1_7 = '12345^JONES^Michael^Robert^^^Dr'

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.segment_action_code = 'A'

        # .. build AIG ..
        aig = AIG()
        aig.set_id_aig = '1'
        aig.segment_action_code = 'A'
        aig.resource_id = CWE(cwe_1='12345', cwe_2='JONES', cwe_3='Michael', cwe_4='Robert', cwe_7='Dr')

        # .. build the GENERAL_RESOURCE group ..
        general_resource = SiuS12GeneralResource()
        general_resource.aig = aig

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.segment_action_code = 'A'
        ail.location_resource_id = PL(pl_1='ORTH_OPD', pl_2='OPD01', pl_3='1', pl_6='WESTERN_HEALTH')

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.general_resource = general_resource
        resources.location_resource = location_resource

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
    """ Based on live/au/au-dedalus-webpas.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='IPM')
        msh.sending_facility = HD(hd_1='CAIRNS_HOSPITAL')
        msh.receiving_application = HD(hd_1='HBCIS')
        msh.receiving_facility = HD(hd_1='CAIRNS_HOSPITAL')
        msh.date_time_of_message = '20240830111500'
        msh.message_type = MSG(msg_1='SIU', msg_2='S14')
        msh.message_control_id = 'MSG00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT600001', ei_2='IPM')
        sch.filler_appointment_id = EI(ei_1='APT600001', ei_2='IPM')
        sch.schedule_id = CWE(cwe_1='ROUTINE', cwe_2='Routine appointment', cwe_3='HL70276')
        sch.event_reason = CWE(cwe_1='FOLLOWUP', cwe_2='Follow-up', cwe_3='HL70277')
        sch.appointment_reason = CWE(cwe_1='30')
        sch.appointment_type = CWE(cwe_1='MIN')
        sch.sch_9 = '^^30^20240910100000^20240910103000'
        sch.placer_contact_address = XAD(xad_1='78901', xad_2='GARCIA', xad_3='Maria', xad_4='Elena', xad_7='Dr')
        sch.placer_contact_location = PL(pl_1='+61740501234')
        sch.filler_contact_person = XCN(xcn_1='1 Lake Street', xcn_3='Cairns', xcn_4='QLD', xcn_5='4870', xcn_6='AU')
        sch.sch_17 = 'CARD_OPD^^CAIRNS_HOSPITAL'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN13456789', cx_4='IPM', cx_5='MR'), CX(cx_1='54321098765', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='FRASER', xpn_2='Donna', xpn_3='Louise', xpn_5='Mrs')
        pid.date_time_of_birth = '19710609'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='34 Sheridan Street', xad_3='Cairns', xad_4='QLD', xad_5='4870', xad_6='AU')
        pid.pid_13 = '+61740567890'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CARD_OPD', pl_2='OPD02', pl_3='1', pl_6='CAIRNS_HOSPITAL')
        pv1.pv1_7 = '78901^GARCIA^Maria^Elena^^^Dr'

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.segment_action_code = 'A'

        # .. build AIG ..
        aig = AIG()
        aig.set_id_aig = '1'
        aig.segment_action_code = 'A'
        aig.resource_id = CWE(cwe_1='78901', cwe_2='GARCIA', cwe_3='Maria', cwe_4='Elena', cwe_7='Dr')

        # .. build the GENERAL_RESOURCE group ..
        general_resource = SiuS12GeneralResource()
        general_resource.aig = aig

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.segment_action_code = 'A'
        ail.location_resource_id = PL(pl_1='CARD_OPD', pl_2='OPD02', pl_3='1', pl_6='CAIRNS_HOSPITAL')

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.general_resource = general_resource
        resources.location_resource = location_resource

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources

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
    """ Based on live/au/au-dedalus-webpas.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WEBPAS')
        msh.sending_facility = HD(hd_1='ROYAL_HOBART')
        msh.receiving_application = HD(hd_1='EDM')
        msh.receiving_facility = HD(hd_1='ROYAL_HOBART')
        msh.date_time_of_message = '20241101153000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02')
        msh.message_control_id = 'MSG00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20241101153000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN14567890', cx_4='WEBPAS', cx_5='MR'), CX(cx_1='65432109876', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='MCDONALD', xpn_2='Bruce', xpn_3='William', xpn_5='Mr')
        pid.date_time_of_birth = '19480925'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='5 Liverpool Street', xad_3='Hobart', xad_4='TAS', xad_5='7000', xad_6='AU')
        pid.pid_13 = '+61362345678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3M', pl_2='302', pl_3='1', pl_6='ROYAL_HOBART')
        pv1.pv1_7 = '34567^PARK^Soo^Jin^^^Dr'
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.pv1_17 = '34567^PARK^Soo^Jin^^^Dr'
        pv1.patient_type = CWE(cwe_1='IN')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='Discharge Summary')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20241101150000'
        txa.txa_5 = '34567^PARK^Soo^Jin^^^Dr'
        txa.transcription_date_time = '20241101153000'
        txa.txa_9 = '34567^PARK^Soo^Jin^^^Dr'
        txa.placer_order_number = EI(ei_1='DOC700001', ei_3='WEBPAS')
        txa.document_completion_status = 'AU'
        txa.document_availability_status = 'AV'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Report', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMg'
            'MCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5'
            'IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo='
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
    """ Based on live/au/au-dedalus-webpas.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DEDALUS_IPM')
        msh.sending_facility = HD(hd_1='ROYAL_PERTH')
        msh.receiving_application = HD(hd_1='EDMS')
        msh.receiving_facility = HD(hd_1='ROYAL_PERTH')
        msh.date_time_of_message = '20241203094500'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02')
        msh.message_control_id = 'MSG00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20241203094500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN15678901', cx_4='DEDALUS_IPM', cx_5='MR'), CX(cx_1='76543210987', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='WATTS', xpn_2='Sandra', xpn_3='Lee', xpn_5='Ms')
        pid.date_time_of_birth = '19690314'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='41 Hay Street', xad_3='Perth', xad_4='WA', xad_5='6000', xad_6='AU')
        pid.pid_13 = '+61892567890'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RHEUM_OPD', pl_2='OPD05', pl_3='1', pl_6='ROYAL_PERTH')
        pv1.pv1_7 = '45678^DIMITRIOU^George^Andreas^^^Dr'
        pv1.hospital_service = CWE(cwe_1='RHE')
        pv1.admit_source = CWE(cwe_1='5')
        pv1.pv1_17 = '45678^DIMITRIOU^George^Andreas^^^Dr'
        pv1.patient_type = CWE(cwe_1='OP')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='CL', cwe_2='Clinic Letter')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20241203090000'
        txa.txa_5 = '45678^DIMITRIOU^George^Andreas^^^Dr'
        txa.transcription_date_time = '20241203094500'
        txa.txa_9 = '45678^DIMITRIOU^George^Andreas^^^Dr'
        txa.placer_order_number = EI(ei_1='DOC800001', ei_3='DEDALUS_IPM')
        txa.document_completion_status = 'AU'
        txa.document_availability_status = 'AV'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Report', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMg'
            'MCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5'
            'IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo='
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
    """ Based on live/au/au-dedalus-webpas.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='WEBPAS')
        msh.sending_facility = HD(hd_1='ROYAL_DARWIN')
        msh.receiving_application = HD(hd_1='EDIS')
        msh.receiving_facility = HD(hd_1='ROYAL_DARWIN')
        msh.date_time_of_message = '20240905021500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        msh.message_control_id = 'MSG00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20240905021500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN16789012', cx_4='WEBPAS', cx_5='MR'), CX(cx_1='87654321098', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='KELLY', xpn_2='Thomas', xpn_3='Patrick', xpn_5='Mr')
        pid.date_time_of_birth = '19850711'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='12 Mitchell Street', xad_3='Darwin', xad_4='NT', xad_5='0800', xad_6='AU')
        pid.pid_13 = '+61889431234'
        pid.marital_status = CWE(cwe_1='S')
        pid.religion = CWE(cwe_1='NON')
        pid.patient_account_number = CX(cx_1='V00901234', cx_4='WEBPAS', cx_5='AN')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_2='ED05', pl_3='1', pl_6='ROYAL_DARWIN')
        pv1.pv1_7 = '89012^JACKSON^Peter^William^^^Dr'
        pv1.hospital_service = CWE(cwe_1='EME')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.pv1_17 = '89012^JACKSON^Peter^William^^^Dr'
        pv1.patient_type = CWE(cwe_1='EM')
        pv1.financial_class = FC(fc_1='MED')
        pv1.servicing_facility = CWE(cwe_1='ROYAL_DARWIN')
        pv1.admit_date_time = '20240905021500'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.dg1_2 = 'I10'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='S52.5', cwe_2='Fracture of lower end of radius', cwe_3='I10')
        dg1.diagnosis_type = CWE(cwe_1='AD')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = dg1

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
    """ Based on live/au/au-dedalus-webpas.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RIS')
        msh.sending_facility = HD(hd_1='CANBERRA_HOSPITAL')
        msh.receiving_application = HD(hd_1='DEDALUS_PAS')
        msh.receiving_facility = HD(hd_1='CANBERRA_HOSPITAL')
        msh.date_time_of_message = '20241015161000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MSG00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN17890123', cx_4='DEDALUS_PAS', cx_5='MR'), CX(cx_1='98765432109', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='HEWITT', xpn_2='Caroline', xpn_3='Grace', xpn_5='Mrs')
        pid.date_time_of_birth = '19760528'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='19 Commonwealth Avenue', xad_3='Canberra', xad_4='ACT', xad_5='2600', xad_6='AU')
        pid.pid_13 = '+61262345678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='RAD01', pl_3='1', pl_6='CANBERRA_HOSPITAL')
        pv1.pv1_7 = '56789^TAN^Boon^Kiat^^^Dr'

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
        orc.placer_order_number = EI(ei_1='ORD400001', ei_2='DEDALUS_PAS')
        orc.filler_order_number = EI(ei_1='RAD500001', ei_2='RIS')
        orc.orc_7 = '^^^20241015100000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD400001', ei_2='DEDALUS_PAS')
        obr.filler_order_number = EI(ei_1='RAD500001', ei_2='RIS')
        obr.universal_service_identifier = CWE(cwe_1='24627-2', cwe_2='CHEST XRAY PA AND LATERAL', cwe_3='LN')
        obr.observation_date_time = '20241015100000'
        obr.obr_14 = '20241015101000'
        obr.obr_16 = '56789^TAN^Boon^Kiat^^^Dr'
        obr.results_rpt_status_chng_date_time = '20241015161000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='24627-2', cwe_2='Chest XRay Report', cwe_3='LN')
        obx.obx_5 = (
            'FINDINGS: Heart size normal. Lungs clear bilaterally. No pleural effusion. No pneumothorax. Bony structures intact.\\.br\\\\.br\\IMPRESSION: Nor'
            'mal chest radiograph.'
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
    """ Based on live/au/au-dedalus-webpas.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DEDALUS_IPM')
        msh.sending_facility = HD(hd_1='FLINDERS_MC')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='SA_HEALTH')
        msh.date_time_of_message = '20241120085000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08')
        msh.message_control_id = 'MSG00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20241120085000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN18901234', cx_4='DEDALUS_IPM', cx_5='MR'), CX(cx_1='10976543210', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='RUSSO', xpn_2='Antonio', xpn_3='Marco', xpn_5='Mr')
        pid.date_time_of_birth = '19600103'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='88 Flinders Street', xad_3='Adelaide', xad_4='SA', xad_5='5000', xad_6='AU')
        pid.pid_13 = '+61881234567^^^a.russo@email.com.au'
        pid.pid_14 = '+61881234568'
        pid.primary_language = CWE(cwe_1='IT')
        pid.marital_status = CWE(cwe_1='M')
        pid.religion = CWE(cwe_1='CAT')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='RUSSO', xpn_2='Maria', xpn_3='Lucia', xpn_5='Mrs')
        nk1.relationship = CWE(cwe_1='SPO')
        nk1.address = XAD(xad_1='88 Flinders Street', xad_3='Adelaide', xad_4='SA', xad_5='5000', xad_6='AU')
        nk1.nk1_5 = '+61413567890'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build NK1 ..
        nk1_2 = NK1()
        nk1_2.set_id_nk1 = '2'
        nk1_2.name = XPN(xpn_1='RUSSO', xpn_2='Luca', xpn_3='Antonio', xpn_5='Mr')
        nk1_2.relationship = CWE(cwe_1='SON')
        nk1_2.address = XAD(xad_1='22 Goodwood Road', xad_3='Wayville', xad_4='SA', xad_5='5034', xad_6='AU')
        nk1_2.nk1_5 = '+61414678901'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin_2 = AdtA01NextOfKin()
        next_of_kin_2.nk1 = nk1_2

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = '67890^WALSH^Catherine^Anne^^^Dr'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = [next_of_kin, next_of_kin_2]
        msg.extra_segments = [pd1]

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
    """ Based on live/au/au-dedalus-webpas.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DEDALUS_PAS')
        msh.sending_facility = HD(hd_1='SIR_CHARLES_GAIRDNER')
        msh.receiving_application = HD(hd_1='TOPAS')
        msh.receiving_facility = HD(hd_1='SIR_CHARLES_GAIRDNER')
        msh.date_time_of_message = '20241210143000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S15')
        msh.message_control_id = 'MSG00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT700001', ei_2='DEDALUS_PAS')
        sch.filler_appointment_id = EI(ei_1='APT700001', ei_2='DEDALUS_PAS')
        sch.schedule_id = CWE(cwe_1='ROUTINE', cwe_2='Routine appointment', cwe_3='HL70276')
        sch.event_reason = CWE(cwe_1='FOLLOWUP', cwe_2='Follow-up', cwe_3='HL70277')
        sch.appointment_reason = CWE(cwe_1='20')
        sch.appointment_type = CWE(cwe_1='MIN')
        sch.sch_9 = '^^20^20241220090000^20241220092000'
        sch.sch_11 = 'PATIENT_REQUEST^Patient request^HL70310'
        sch.placer_contact_location = PL(pl_1='90123', pl_2='PHAM', pl_3='Linh', pl_4='Thi', pl_7='Dr')
        sch.filler_contact_person = XCN(xcn_1='+61893456789')
        sch.sch_17 = 'Nedlands Road^^Nedlands^WA^6009^AU'
        sch.filler_contact_address = XAD(xad_1='NEURO_OPD', xad_3='SIR_CHARLES_GAIRDNER')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN19012345', cx_4='DEDALUS_PAS', cx_5='MR'), CX(cx_1='21087654321', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='ANDERSON', xpn_2='Kylie', xpn_3='Maree', xpn_5='Ms')
        pid.date_time_of_birth = '19920227'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='56 Stirling Highway', xad_3='Nedlands', xad_4='WA', xad_5='6009', xad_6='AU')
        pid.pid_13 = '+61892789012'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='NEURO_OPD', pl_2='OPD03', pl_3='1', pl_6='SIR_CHARLES_GAIRDNER')
        pv1.pv1_7 = '90123^PHAM^Linh^Thi^^^Dr'

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.segment_action_code = 'A'

        # .. build AIG ..
        aig = AIG()
        aig.set_id_aig = '1'
        aig.segment_action_code = 'A'
        aig.resource_id = CWE(cwe_1='90123', cwe_2='PHAM', cwe_3='Linh', cwe_4='Thi', cwe_7='Dr')

        # .. build the GENERAL_RESOURCE group ..
        general_resource = SiuS12GeneralResource()
        general_resource.aig = aig

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.segment_action_code = 'A'
        ail.location_resource_id = PL(pl_1='NEURO_OPD', pl_2='OPD03', pl_3='1', pl_6='SIR_CHARLES_GAIRDNER')

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.general_resource = general_resource
        resources.location_resource = location_resource

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources

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
