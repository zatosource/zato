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
from zato.hl7v2.v2_9.datatypes import AUI, CNE, CWE, CX, DR, EI, HD, MOC, MSG, PL, PLN, PT, VID, XAD, XCN, XON, XPN, XTN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA01NextOfKin, DftP03Financial, DftP03Visit, MdmT02Observation, MfnM02MfStaff, OrmO01Order, \
    OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, \
    OruR01PatientObservation, OruR01PatientResult, OruR01Visit, RdeO11Order, RdeO11Patient, RdeO11PatientVisit, SiuS12Patient, SiuS12PersonnelResource, \
    SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A05, ADT_A30, DFT_P03, MDM_T02, MFN_M02, ORM_O01, ORU_R01, RDE_O11, SIU_S12
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, AL1, DG1, EVN, FT1, IN1, MFE, MFI, MRG, MSH, NK1, NTE, OBR, OBX, ORC, PID, PRA, PV1, RGS, RXE, RXR, SCH, \
    STF, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('nl', 'nl-rhapsody.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/nl/nl-rhapsody.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='UMCU')
        msh.receiving_application = HD(hd_1='LAB_SYS')
        msh.receiving_facility = HD(hd_1='PATHOLOGY')
        msh.date_time_of_message = '202603011430'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '202603011430'
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='Wolters', xcn_3='Femke', xcn_6='RN')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN12345', cx_4='UMCU', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Bakker', xpn_2='Daan', xpn_3='Willem')
        pid.date_time_of_birth = '19800115'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='Oudegracht 42', xad_3='Utrecht', xad_5='3511AR', xad_6='NL')
        pid.pid_13 = '^PRN^PH^^^^^030-2514789'
        pid.primary_language = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.patient_account_number = CX(cx_1='ACCT98765', cx_4='UMCU', cx_5='AN')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='0101', pl_3='01', pl_4='UMCU', pl_8='NURS')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.attending_doctor = XCN(xcn_1='ATT1234', xcn_2='Meijer', xcn_3='Johanna', xcn_6='MD')
        pv1.referring_doctor = XCN(xcn_1='REF5678', xcn_2='Timmerman', xcn_3='Adriaan', xcn_6='MD')
        pv1.hospital_service = CWE(cwe_1='MED', cwe_2='Medical', cwe_3='HL70069')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='ATT1234', xcn_2='Meijer', xcn_3='Johanna', xcn_6='MD')
        pv1.patient_type = CWE(cwe_1='IP', cwe_2='Inpatient', cwe_3='HL70004')
        pv1.discharge_disposition = CWE(cwe_1='UMCU')
        pv1.diet_type = CWE(cwe_1='A')
        pv1.account_status = CWE(cwe_1='202603011415')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Bakker', xpn_2='Lotte', xpn_3='A')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Oudegracht 42', xad_3='Utrecht', xad_5='3511AR', xad_6='NL')
        nk1.nk1_5 = '^PRN^PH^^^^^030-2514790'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='ZK001', cwe_2='Zilveren Kruis')
        in1.insurance_company_id = CX(cx_1='ZK')
        in1.in1_4 = 'Postbus 444^^Leiden^^2300AK^NL'
        in1.insurance_company_address = XAD(xad_2='WPN', xad_3='PH', xad_8='071-5249000')
        in1.in1_7 = 'GRP54321'
        in1.authorization_information = AUI(aui_1='20230101')
        in1.plan_type = CWE(cwe_1='20261231')
        in1.insureds_relationship_to_patient = CWE(cwe_1='SELF', cwe_2='Self', cwe_3='HL70063')
        in1.insureds_date_of_birth = 'Bakker^Daan^Willem'
        in1.insureds_address = XAD(xad_1='SELF')
        in1.assignment_of_benefits = CWE(cwe_1='19800115')

        # .. build AL1 ..
        al1 = AL1()
        al1.set_id_al1 = '1'
        al1.allergen_type_code = CWE(cwe_1='DA', cwe_2='Drug Allergy', cwe_3='HL70127')
        al1.allergen_code_mnemonic_description = CWE(cwe_1='PCN', cwe_2='Penicillin', cwe_3='HL70127')
        al1.allergy_severity_code = CWE(cwe_1='SV', cwe_2='Severe', cwe_3='HL70128')
        al1.allergy_reaction_code = 'Anaphylaxis'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [nk1, in1, al1]

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
    """ Based on live/nl/nl-rhapsody.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB_SYS')
        msh.sending_facility = HD(hd_1='UMCU')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='UMCU')
        msh.date_time_of_message = '202603011630'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB00042'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN12345', cx_4='UMCU', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Bakker', xpn_2='Daan', xpn_3='Willem')
        pid.date_time_of_birth = '19800115'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='0101', pl_3='01', pl_4='UMCU')

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
        orc.placer_order_number = EI(ei_1='ORD5678', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='FIL9012', ei_2='LAB_SYS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD5678', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='FIL9012', ei_2='LAB_SYS')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='CMP', cwe_3='LN')
        obr.observation_date_time = '202603011445'
        obr.obr_14 = 'ATT1234^Meijer^Johanna^^^MD'
        obr.filler_field_1 = '202603011615'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose', cwe_3='LN')
        obx.obx_5 = '98'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '70-100'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine', cwe_3='LN')
        obx_2.obx_5 = '1.1'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '0.6-1.2'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='BUN', cwe_3='LN')
        obx_3.obx_5 = '18'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '7-20'
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
        obx_4.obx_5 = '140'
        obx_4.units = CWE(cwe_1='mEq/L')
        obx_4.reference_range = '136-145'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium', cwe_3='LN')
        obx_5.obx_5 = '4.2'
        obx_5.units = CWE(cwe_1='mEq/L')
        obx_5.reference_range = '3.5-5.0'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='17861-6', cwe_2='Calcium', cwe_3='LN')
        obx_6.obx_5 = '9.4'
        obx_6.units = CWE(cwe_1='mg/dL')
        obx_6.reference_range = '8.5-10.5'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT', cwe_3='LN')
        obx_7.obx_5 = '28'
        obx_7.units = CWE(cwe_1='U/L')
        obx_7.reference_range = '7-56'
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
    """ Based on live/nl/nl-rhapsody.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='UMCU')
        msh.receiving_application = HD(hd_1='LAB_SYS')
        msh.receiving_facility = HD(hd_1='PATHOLOGY')
        msh.date_time_of_message = '202603011400'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'ORD00123'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN12345', cx_4='UMCU', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Bakker', xpn_2='Daan', xpn_3='Willem')
        pid.date_time_of_birth = '19800115'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='0101', pl_3='01', pl_4='UMCU')
        pv1.attending_doctor = XCN(xcn_1='ATT1234', xcn_2='Meijer', xcn_3='Johanna', xcn_6='MD')

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
        orc.placer_order_number = EI(ei_1='ORD5678', ei_2='EPIC')
        orc.placer_order_group_number = EI(ei_1='GRP001', ei_2='EPIC')
        orc.date_time_of_order_event = '202603011400'
        orc.orc_12 = 'ATT1234^Meijer^Johanna^^^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD5678', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC with Diff', cwe_3='LN')
        obr.observation_date_time = '202603011400'
        obr.obr_16 = 'ATT1234^Meijer^Johanna^^^MD'
        obr.obr_27 = '^STAT'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R50.9', cwe_2='Fever, unspecified', cwe_3='I10')

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Patient febrile x 24hrs, rule out infection.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [nte]

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
    """ Based on live/nl/nl-rhapsody.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS')
        msh.sending_facility = HD(hd_1='Radboudumc')
        msh.receiving_application = HD(hd_1='LIS')
        msh.receiving_facility = HD(hd_1='Radboudumc')
        msh.date_time_of_message = '20060307110114'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MSGID20060307110114'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='12001')
        pid.patient_name = XPN(xpn_1='de Vries', xpn_2='Pieter', xpn_5='dhr.')
        pid.date_time_of_birth = '19670824'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Plompetorengracht 8', xad_3='Utrecht', xad_5='3512CA', xad_6='NL')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OP', pl_2='PAREG', pl_3='')
        pv1.attending_doctor = XCN(xcn_1='2342', xcn_2='Brouwer', xcn_3='Geert')
        pv1.hospital_service = CWE(cwe_1='OP')
        pv1.visit_number = CX(cx_1='2')
        pv1.admit_date_time = '20060307110111'
        pv1.pv1_45 = ''

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
        orc.placer_order_number = EI(ei_1='20060307110114')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='20060307110114')
        obr.universal_service_identifier = CWE(cwe_1='003038', cwe_2='Urinalysis', cwe_3='L')
        obr.observation_date_time = '20060307110114'

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
    """ Based on live/nl/nl-rhapsody.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SCHED_SYS')
        msh.sending_facility = HD(hd_1='UMCU')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='UMCU')
        msh.date_time_of_message = '202603051000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'SCH00456'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT78901', ei_2='SCHED_SYS')
        sch.filler_appointment_id = EI(ei_1='APT78901', ei_2='EPIC')
        sch.appointment_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine', cwe_3='HL70277')
        sch.appointment_type = CWE(cwe_1='OFFICE', cwe_2='Office Visit', cwe_3='LOCAL')
        sch.sch_9 = '30'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^30^202603101400^202603101430'
        sch.filler_contact_person = XCN(xcn_1='ATT1234', xcn_2='Meijer', xcn_3='Johanna', xcn_6='MD')
        sch.filler_contact_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_8='030-2345678')
        sch.filler_contact_address = XAD(xad_1='MAIN_CLINIC', xad_2='UMCU')
        sch.entered_by_person = XCN(xcn_1='Booked')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN12345', cx_4='UMCU', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Bakker', xpn_2='Daan', xpn_3='Willem')
        pid.date_time_of_birth = '19800115'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MAIN_CLINIC', pl_2='EXAM3', pl_3='01', pl_4='UMCU')
        pv1.attending_doctor = XCN(xcn_1='ATT1234', xcn_2='Meijer', xcn_3='Johanna', xcn_6='MD')

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
        ais.universal_service_identifier = CWE(cwe_1='OFFICE_VISIT', cwe_2='Office Visit', cwe_3='LOCAL')
        ais.start_date_time_offset_units = CNE(cne_1='202603101400')
        ais.duration = '0'
        ais.duration_units = CNE(cne_1='MIN')
        ais.allow_substitution_code = CWE(cwe_1='30')
        ais.filler_status_code = CWE(cwe_1='MIN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.segment_action_code = 'A'
        aip.personnel_resource_id = XCN(xcn_1='ATT1234', xcn_2='Meijer', xcn_3='Johanna', xcn_6='MD')
        aip.resource_type = CWE(cwe_1='ATT', cwe_2='Attending', cwe_3='HL70443')

        # .. build the PERSONNEL_RESOURCE group ..
        personnel_resource = SiuS12PersonnelResource()
        personnel_resource.aip = aip

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service
        resources.personnel_resource = personnel_resource

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.segment_action_code = 'A'
        ail.location_resource_id = PL(pl_1='MAIN_CLINIC', pl_2='EXAM3', pl_3='01', pl_4='UMCU')
        ail.location_group = CWE(cwe_1='202603101400')
        ail.start_date_time = '0'
        ail.start_date_time_offset = 'MIN'
        ail.start_date_time_offset_units = CNE(cne_1='30')
        ail.duration = 'MIN'

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.patient = patient
        msg.resources = resources
        msg.extra_segments = [ail]

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
    """ Based on live/nl/nl-rhapsody.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TRANS_SYS')
        msh.sending_facility = HD(hd_1='UMCU')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='UMCU')
        msh.date_time_of_message = '202603021000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'DOC00321'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '202603021000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN12345', cx_4='UMCU', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Bakker', xpn_2='Daan', xpn_3='Willem')
        pid.date_time_of_birth = '19800115'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SURG', pl_2='OR3', pl_3='01', pl_4='UMCU')
        pv1.attending_doctor = XCN(xcn_1='SUR5678', xcn_2='Visser', xcn_3='Hendrik', xcn_6='MD')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='OP', cwe_2='Operative Note', cwe_3='HL70270')
        txa.document_content_presentation = 'TX^Text^HL70191'
        txa.primary_activity_provider_code_name = XCN(xcn_1='202603011600')
        txa.assigned_document_authenticator = XCN(xcn_1='SUR5678', xcn_2='Visser', xcn_3='Hendrik', xcn_6='MD')
        txa.placer_order_number = EI(ei_1='DOC54321')
        txa.unique_document_file_name = 'AU^Authenticated^HL70271'
        txa.document_confidentiality_status = '202603021000'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='OP_NOTE', cwe_2='Operative Note', cwe_3='LOCAL')
        obx.obx_5 = (
            'Procedure: Laparoscopic cholecystectomy\\.br\\Patient tolerated procedure well\\.br\\No complications\\.br\\EBL: 50mL\\.br\\Specimens sent to pa'
            'thology.'
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
    """ Based on live/nl/nl-rhapsody.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='sendFac')
        msh.sending_facility = HD(hd_1='SendApp')
        msh.date_time_of_message = '20170822095500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = '64517000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.msh_14 = ''

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='1234567', cx_5='PI'), CX(cx_1='283716495', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = [
            XPN(xpn_1='van den Berg&&van den Berg&&', xpn_2='Cornelia', xpn_7='L'),
            XPN(xpn_1='van den Berg&&van den Berg', xpn_2='Cornelia', xpn_7='B'),
        ]
        pid.date_time_of_birth = '19500101'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = [
            XAD(xad_1='Herengracht 88&Herengracht&88', xad_3='Amsterdam', xad_5='1015BS', xad_6='NL', xad_7='M'),
            XAD(xad_1='Herengracht 88&Herengracht&88', xad_3='Amsterdam', xad_5='1015BS', xad_6='NL', xad_7='L'),
        ]
        pid.pid_13 = '020-6234891^PRN^PH~^^^cornelia@voorbeeld.nl'
        pid.marital_status = CWE(cwe_1='M')
        pid.birth_place = 'Amsterdam'
        pid.multiple_birth_indicator = 'Y'
        pid.birth_order = '2'
        pid.patient_death_date_and_time = '""'
        pid.patient_death_indicator = 'N'
        pid.identity_unknown_indicator = 'N'
        pid.pid_38 = ''

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='882-1', cwe_2='ABO+Rh group')
        obx.obx_5 = 'O pos'
        obx.observation_result_status = 'F'

        # .. build the PATIENT_OBSERVATION group ..
        patient_observation = OruR01PatientObservation()
        patient_observation.obx = obx

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='0RGC2')
        pv1.pv1_7 = ''

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.patient_observation = patient_observation
        patient.visit = visit

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='123')
        obr.filler_order_number = EI(ei_1='20050701015070', ei_2='Labosys')
        obr.observation_date_time = '200507010907'
        obr.relevant_clinical_information = CWE(cwe_1='""')
        obr.obr_16 = '3004^Timmerman'
        obr.filler_field_1 = '200507010907'
        obr.results_rpt_status_chng_date_time = '201708220955'
        obr.diagnostic_serv_sect_id = 'S'
        obr.result_status = 'F'
        obr.obr_27 = '^^^^^R'

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '1'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='266', cwe_2='Bezinking', cwe_3='L', cwe_4='BSE')
        obx_2.obx_5 = '2'
        obx_2.units = CWE(cwe_1='mm/uur')
        obx_2.reference_range = '0 - 15'
        obx_2.interpretation_codes = CWE(cwe_1='""')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '2'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='325', cwe_2='Leucocyten', cwe_3='L', cwe_4='LEU')
        obx_3.obx_5 = '6.7'
        obx_3.units = CWE(cwe_1='/nl')
        obx_3.reference_range = '4.0 - 10.0'
        obx_3.interpretation_codes = CWE(cwe_1='""')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '3'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='323', cwe_2='Hemoglobine', cwe_3='L', cwe_4='HB')
        obx_4.obx_5 = '10.2'
        obx_4.units = CWE(cwe_1='mmol/l')
        obx_4.reference_range = '8.5 - 11.0'
        obx_4.interpretation_codes = CWE(cwe_1='""')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '4'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='324', cwe_2='Hematocriet', cwe_3='L', cwe_4='HT')
        obx_5.obx_5 = '0.48'
        obx_5.units = CWE(cwe_1='l/l')
        obx_5.reference_range = '0.41 - 0.51'
        obx_5.interpretation_codes = CWE(cwe_1='""')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '5'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='326', cwe_2="Ery's", cwe_3='L', cwe_4='ERY')
        obx_6.obx_5 = '5.2'
        obx_6.units = CWE(cwe_1='/pl')
        obx_6.reference_range = '4.4 - 5.8'
        obx_6.interpretation_codes = CWE(cwe_1='""')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '6'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='328', cwe_2='MCV', cwe_3='L', cwe_4='MCV1')
        obx_7.obx_5 = '92'
        obx_7.units = CWE(cwe_1='fl')
        obx_7.reference_range = '80 - 100'
        obx_7.interpretation_codes = CWE(cwe_1='""')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '7'
        obx_8.value_type = 'ST'
        obx_8.observation_identifier = CWE(cwe_1='329', cwe_2='MCH', cwe_3='L', cwe_4='MCH')
        obx_8.obx_5 = '1.97'
        obx_8.units = CWE(cwe_1='fmol')
        obx_8.reference_range = '1.60 - 2.10'
        obx_8.interpretation_codes = CWE(cwe_1='""')
        obx_8.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '8'
        obx_9.value_type = 'ST'
        obx_9.observation_identifier = CWE(cwe_1='330', cwe_2='MCHC', cwe_3='L', cwe_4='MCHC')
        obx_9.obx_5 = '21.3'
        obx_9.units = CWE(cwe_1='mmol/l')
        obx_9.reference_range = '19.0 - 23.0'
        obx_9.interpretation_codes = CWE(cwe_1='""')
        obx_9.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_9

        # .. build OBX ..
        obx_10 = OBX()
        obx_10.set_id_obx = '9'
        obx_10.value_type = 'ST'
        obx_10.observation_identifier = CWE(cwe_1='648', cwe_2='Ureum', cwe_3='L', cwe_4='UR')
        obx_10.obx_5 = '3.9'
        obx_10.units = CWE(cwe_1='mmol/l')
        obx_10.reference_range = '2.5 - 7.5'
        obx_10.interpretation_codes = CWE(cwe_1='""')
        obx_10.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_10

        # .. build OBX ..
        obx_11 = OBX()
        obx_11.set_id_obx = '10'
        obx_11.value_type = 'ST'
        obx_11.observation_identifier = CWE(cwe_1='630', cwe_2='Kreatinine', cwe_3='L', cwe_4='KR')
        obx_11.obx_5 = '99'
        obx_11.units = CWE(cwe_1='umol/l')
        obx_11.reference_range = '70 - 110'
        obx_11.interpretation_codes = CWE(cwe_1='""')
        obx_11.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_10 = OruR01Observation()
        observation_10.obx = obx_11

        # .. build OBX ..
        obx_12 = OBX()
        obx_12.set_id_obx = '11'
        obx_12.value_type = 'ST'
        obx_12.observation_identifier = CWE(cwe_1='638', cwe_2='Natrium', cwe_3='L', cwe_4='NA')
        obx_12.obx_5 = '139'
        obx_12.units = CWE(cwe_1='mmol/l')
        obx_12.reference_range = '135 - 145'
        obx_12.interpretation_codes = CWE(cwe_1='""')
        obx_12.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_11 = OruR01Observation()
        observation_11.obx = obx_12

        # .. build OBX ..
        obx_13 = OBX()
        obx_13.set_id_obx = '12'
        obx_13.value_type = 'ST'
        obx_13.observation_identifier = CWE(cwe_1='628', cwe_2='Kalium', cwe_3='L', cwe_4='K')
        obx_13.obx_5 = '3.9'
        obx_13.units = CWE(cwe_1='mmol/l')
        obx_13.reference_range = '3.5 - 5.0'
        obx_13.interpretation_codes = CWE(cwe_1='""')
        obx_13.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_12 = OruR01Observation()
        observation_12.obx = obx_13

        # .. build OBX ..
        obx_14 = OBX()
        obx_14.set_id_obx = '13'
        obx_14.value_type = 'ST'
        obx_14.observation_identifier = CWE(cwe_1='2325', cwe_2='Alk.fosf.', cwe_3='L', cwe_4='AF')
        obx_14.obx_5 = '52'
        obx_14.units = CWE(cwe_1='U/l')
        obx_14.reference_range = '0 - 120'
        obx_14.interpretation_codes = CWE(cwe_1='""')
        obx_14.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_13 = OruR01Observation()
        observation_13.obx = obx_14

        # .. build OBX ..
        obx_15 = OBX()
        obx_15.set_id_obx = '14'
        obx_15.value_type = 'ST'
        obx_15.observation_identifier = CWE(cwe_1='2326', cwe_2='Gamma GT', cwe_3='L', cwe_4='GGT')
        obx_15.obx_5 = '29'
        obx_15.units = CWE(cwe_1='U/l')
        obx_15.reference_range = ' - 50'
        obx_15.interpretation_codes = CWE(cwe_1='""')
        obx_15.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_14 = OruR01Observation()
        observation_14.obx = obx_15

        # .. build OBX ..
        obx_16 = OBX()
        obx_16.set_id_obx = '15'
        obx_16.value_type = 'ST'
        obx_16.observation_identifier = CWE(cwe_1='2327', cwe_2='ASAT', cwe_3='L', cwe_4='ASAT')
        obx_16.obx_5 = '19'
        obx_16.units = CWE(cwe_1='U/l')
        obx_16.reference_range = '0 - 40'
        obx_16.interpretation_codes = CWE(cwe_1='""')
        obx_16.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_15 = OruR01Observation()
        observation_15.obx = obx_16

        # .. build OBX ..
        obx_17 = OBX()
        obx_17.set_id_obx = '16'
        obx_17.value_type = 'ST'
        obx_17.observation_identifier = CWE(cwe_1='2328', cwe_2='ALAT', cwe_3='L', cwe_4='ALAT')
        obx_17.obx_5 = '20'
        obx_17.units = CWE(cwe_1='U/l')
        obx_17.reference_range = '0 - 45'
        obx_17.interpretation_codes = CWE(cwe_1='""')
        obx_17.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_16 = OruR01Observation()
        observation_16.obx = obx_17

        # .. build OBX ..
        obx_18 = OBX()
        obx_18.set_id_obx = '17'
        obx_18.value_type = 'ST'
        obx_18.observation_identifier = CWE(cwe_1='614', cwe_2='Glucose', cwe_3='L', cwe_4='GLUS')
        obx_18.obx_5 = '10.3'
        obx_18.units = CWE(cwe_1='mmol/l')
        obx_18.reference_range = '4.0 - 7.8'
        obx_18.interpretation_codes = CWE(cwe_1='H')
        obx_18.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_17 = OruR01Observation()
        observation_17.obx = obx_18

        # .. build OBX ..
        obx_19 = OBX()
        obx_19.set_id_obx = '18'
        obx_19.value_type = 'ST'
        obx_19.observation_identifier = CWE(cwe_1='34', cwe_2='TSH', cwe_3='L', cwe_4='TSH')
        obx_19.obx_5 = '0.78'
        obx_19.units = CWE(cwe_1='mU/l')
        obx_19.reference_range = '0.4 - 4.0'
        obx_19.interpretation_codes = CWE(cwe_1='""')
        obx_19.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_18 = OruR01Observation()
        observation_18.obx = obx_19

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
        order_observation.observation_10 = observation_10
        order_observation.observation_11 = observation_11
        order_observation.observation_12 = observation_12
        order_observation.observation_13 = observation_13
        order_observation.observation_14 = observation_14
        order_observation.observation_15 = observation_15
        order_observation.observation_16 = observation_16
        order_observation.observation_17 = observation_17
        order_observation.observation_18 = observation_18

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
    """ Based on live/nl/nl-rhapsody.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='REGADT')
        msh.sending_facility = HD(hd_1='AMC')
        msh.receiving_application = HD(hd_1='IFENG')
        msh.date_time_of_message = '199112311501'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = '000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8.2')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '199112310500'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='191919', cx_4='AMC', cx_5='MR'), CX(cx_1='194826537', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Jansen', xpn_2='Willem', xpn_3='G')
        pid.date_time_of_birth = '19610615'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vondelstraat 12', xad_3='Amsterdam', xad_5='1054GE', xad_6='NL')
        pid.pid_13 = '(020)6823456'
        pid.marital_status = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='100-01')
        pid.patient_death_date_and_time = 'N'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Jansen', xpn_2='Theodora', xpn_3='M')
        nk1.relationship = CWE(cwe_1='WI', cwe_2='Wife')
        nk1.end_date = 'NK^Next of Kin'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='W', pl_2='389', pl_3='1', pl_4='AMC')
        pv1.admission_type = CWE(cwe_1='3')
        pv1.attending_doctor = XCN(xcn_1='0148', xcn_2='Dekker', xcn_3='Margaretha', xcn_6='MD')
        pv1.referring_doctor = XCN(xcn_1='REF5678', xcn_2='Bos', xcn_3='Jacobus', xcn_6='MD')
        pv1.hospital_service = CWE(cwe_1='SUR')
        pv1.admit_source = CWE(cwe_1='ADM')
        pv1.ambulatory_status = CWE(cwe_1='A0')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='1')
        in1.insurance_company_id = CX(cx_1='137HM')
        in1.insurance_company_name = XON(xon_1='VGZ')
        in1.insurance_company_address = XAD(xad_1='Postbus 5040', xad_3='Arnhem', xad_5='6802EA', xad_6='NL')
        in1.plan_type = CWE(cwe_1='Jansen', cwe_2='Willem', cwe_3='G')
        in1.name_of_insured = XPN(xpn_1='19610615')
        in1.insureds_relationship_to_patient = CWE(cwe_1='Vondelstraat 12', cwe_3='Amsterdam', cwe_5='1054GE', cwe_6='NL')
        in1.delay_before_lr_day = '194826537'

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
    """ Based on live/nl/nl-rhapsody.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SENDAPP')
        msh.sending_facility = HD(hd_1='SENDFAC')
        msh.receiving_application = HD(hd_1='RECVAPP')
        msh.receiving_facility = HD(hd_1='RECVFAC')
        msh.date_time_of_message = '200504301430'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A04')
        msh.message_control_id = 'MSG000100'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '200504301430'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='12345', cx_4='VUMC', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Smit', xpn_2='Thijs', xpn_3='B')
        pid.date_time_of_birth = '19750101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Amstelveenseweg 200', xad_3='Amsterdam', xad_5='1075XR', xad_6='NL')
        pid.pid_13 = '020-3051234'
        pid.primary_language = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='347291856')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_2='ROOM1', pl_3='BED1')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.attending_doctor = XCN(xcn_1='9876', xcn_2='van Dijk', xcn_3='Elisabeth', xcn_6='MD')

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/nl/nl-rhapsody.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SENDAPP')
        msh.sending_facility = HD(hd_1='SENDFAC')
        msh.receiving_application = HD(hd_1='RECVAPP')
        msh.receiving_facility = HD(hd_1='RECVFAC')
        msh.date_time_of_message = '200504301535'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'MSG000101'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '200504301535'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='12345', cx_4='VUMC', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Smit', xpn_2='Thijs', xpn_3='B')
        pid.date_time_of_birth = '19750101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Leidsestraat 55', xad_3='Amsterdam', xad_5='1017NX', xad_6='NL')
        pid.pid_13 = '020-3059876'
        pid.primary_language = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='347291856')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_2='ROOM1', pl_3='BED1')
        pv1.attending_doctor = XCN(xcn_1='9876', xcn_2='van Dijk', xcn_3='Elisabeth', xcn_6='MD')

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/nl/nl-rhapsody.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SENDAPP')
        msh.sending_facility = HD(hd_1='SENDFAC')
        msh.receiving_application = HD(hd_1='RECVAPP')
        msh.receiving_facility = HD(hd_1='RECVFAC')
        msh.date_time_of_message = '200504301545'
        msh.message_type = MSG(msg_1='ADT', msg_2='A34', msg_3='ADT_A34')
        msh.message_control_id = 'MSG000102'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A34'
        evn.recorded_date_time = '200504301545'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='12345', cx_4='VUMC', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Smit', xpn_2='Thijs', xpn_3='B')
        pid.date_time_of_birth = '19750101'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = CX(cx_1='67890', cx_4='VUMC', cx_5='MR')

        # .. assemble the full message ..
        msg = ADT_A30()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.mrg = mrg

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
    """ Based on live/nl/nl-rhapsody.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB')
        msh.sending_facility = HD(hd_1='LUMC')
        msh.receiving_application = HD(hd_1='EMR')
        msh.receiving_facility = HD(hd_1='LUMC')
        msh.date_time_of_message = '200905151340'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='P500001', cx_4='LUMC', cx_5='MR')
        pid.patient_name = XPN(xpn_1='de Jong', xpn_2='Saskia', xpn_3='W')
        pid.date_time_of_birth = '19690220'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='OUTPT', pl_2='CLINIC5', pl_3='01')

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
        orc.placer_order_number = EI(ei_1='ORD100', ei_2='EMR')
        orc.filler_order_number = EI(ei_1='FILL200', ei_2='LAB')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD100', ei_2='EMR')
        obr.filler_order_number = EI(ei_1='FILL200', ei_2='LAB')
        obr.universal_service_identifier = CWE(cwe_1='57021-8', cwe_2='CBC W Differential', cwe_3='LN')
        obr.observation_date_time = '200905150800'
        obr.obr_14 = '1234^Wolters^Geert^^^MD'
        obr.filler_field_1 = '200905151330'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='WBC', cwe_3='LN')
        obx.obx_5 = '7.8'
        obx.units = CWE(cwe_1='10*3/uL')
        obx.reference_range = '4.5-11.0'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='RBC', cwe_3='LN')
        obx_2.obx_5 = '4.65'
        obx_2.units = CWE(cwe_1='10*6/uL')
        obx_2.reference_range = '4.00-5.50'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobin', cwe_3='LN')
        obx_3.obx_5 = '14.2'
        obx_3.units = CWE(cwe_1='g/dL')
        obx_3.reference_range = '12.0-16.0'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocrit', cwe_3='LN')
        obx_4.obx_5 = '42.1'
        obx_4.units = CWE(cwe_1='%')
        obx_4.reference_range = '36.0-46.0'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='787-2', cwe_2='MCV', cwe_3='LN')
        obx_5.obx_5 = '90.5'
        obx_5.units = CWE(cwe_1='fL')
        obx_5.reference_range = '80.0-100.0'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='785-6', cwe_2='MCH', cwe_3='LN')
        obx_6.obx_5 = '30.5'
        obx_6.units = CWE(cwe_1='pg')
        obx_6.reference_range = '27.0-33.0'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='786-4', cwe_2='MCHC', cwe_3='LN')
        obx_7.obx_5 = '33.7'
        obx_7.units = CWE(cwe_1='g/dL')
        obx_7.reference_range = '32.0-36.0'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='777-3', cwe_2='Platelets', cwe_3='LN')
        obx_8.obx_5 = '245'
        obx_8.units = CWE(cwe_1='10*3/uL')
        obx_8.reference_range = '150-400'
        obx_8.interpretation_codes = CWE(cwe_1='N')
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
    """ Based on live/nl/nl-rhapsody.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS')
        msh.sending_facility = HD(hd_1='Erasmus MC')
        msh.receiving_application = HD(hd_1='BILLING')
        msh.receiving_facility = HD(hd_1='Erasmus MC')
        msh.date_time_of_message = '200603011400'
        msh.message_type = MSG(msg_1='DFT', msg_2='P03')
        msh.message_control_id = 'DFT000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'P03'
        evn.recorded_date_time = '200603011400'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='12345', cx_4='Erasmus MC', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Mulder', xpn_2='Bram', xpn_3='H')
        pid.date_time_of_birth = '19700515'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='101', pl_3='1')
        pv1.attending_doctor = XCN(xcn_1='1234', xcn_2='de Groot', xcn_3='Anneke', xcn_6='MD')

        # .. build the VISIT group ..
        visit = DftP03Visit()
        visit.pv1 = pv1

        # .. build FT1 ..
        ft1 = FT1()
        ft1.set_id_ft1 = '1'
        ft1.transaction_id = CX(cx_1='CRG001')
        ft1.transaction_date = DR(dr_1='200603011400')
        ft1.transaction_posting_date = '200603011400'
        ft1.transaction_type = CWE(cwe_1='CG')
        ft1.transaction_code = CWE(cwe_1='99213', cwe_2='Office Visit Level 3', cwe_3='CPT4')
        ft1.transaction_quantity = '1'
        ft1.medically_necessary_duplicate_procedure_reason = CWE(cwe_1='99213')

        # .. build the FINANCIAL group ..
        financial = DftP03Financial()
        financial.ft1 = ft1

        # .. assemble the full message ..
        msg = DFT_P03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.visit = visit
        msg.financial = financial

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
    """ Based on live/nl/nl-rhapsody.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='STAFFSYS')
        msh.sending_facility = HD(hd_1='Radboudumc')
        msh.receiving_application = HD(hd_1='RECVSYS')
        msh.receiving_facility = HD(hd_1='Radboudumc')
        msh.date_time_of_message = '200603011400'
        msh.message_type = MSG(msg_1='MFN', msg_2='M02')
        msh.message_control_id = 'MFN000001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build MFI ..
        mfi = MFI()
        mfi.master_file_identifier = CWE(cwe_1='PRA', cwe_2='Practitioner Master File', cwe_3='HL70175')
        mfi.file_level_event_code = 'UPD'
        mfi.response_level_code = 'AL'

        # .. build MFE ..
        mfe = MFE()
        mfe.record_level_event_code = 'MAD'
        mfe.mfn_control_id = '1234^Brouwer^Floor^^^MD'
        mfe.mfe_4 = 'CWE'
        mfe.primary_key_value_type = 'PL'

        # .. build STF ..
        stf = STF()
        stf.primary_key_value_stf = CWE(cwe_1='1234')
        stf.staff_identifier_list = CX(cx_1='P111', cx_2='Brouwer', cx_3='Floor', cx_4='K', cx_6='MD')
        stf.staff_type = CWE(cwe_1='Brouwer', cwe_2='Floor', cwe_3='K')
        stf.date_time_of_birth = 'F'
        stf.active_inactive_flag = '19600101'
        stf.department = CWE(cwe_1='A')
        stf.hospital_service_stf = CWE(cwe_1='MD')
        stf.stf_10 = '29384756^NPI^NPI'
        stf.stf_12 = '^WPN^PH^^31^30^2345678'
        stf.stf_13 = 'Domplein 1^^Utrecht^^3512JC^NL'
        stf.backup_person_id = CWE(cwe_1='20000101')

        # .. build PRA ..
        pra = PRA()
        pra.primary_key_value_pra = CWE(cwe_1='1234')
        pra.practitioner_category = CWE(cwe_1='Radboudumc')
        pra.provider_billing = 'Y'
        pra.practitioner_id_numbers = PLN(pln_1='MED', pln_2='Medicine')

        # .. build the MF_STAFF group ..
        mf_staff = MfnM02MfStaff()
        mf_staff.mfe = mfe
        mf_staff.stf = stf
        mf_staff.pra = pra

        # .. assemble the full message ..
        msg = MFN_M02()
        msg.msh = msh
        msg.mfi = mfi
        msg.mf_staff = mf_staff

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
    """ Based on live/nl/nl-rhapsody.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ADMITSYS')
        msh.sending_facility = HD(hd_1='MUMC+')
        msh.receiving_application = HD(hd_1='RECSYS')
        msh.receiving_facility = HD(hd_1='MUMC+')
        msh.date_time_of_message = '200605301500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A05', msg_3='ADT_A05')
        msh.message_control_id = 'PREADMIT01'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A05'
        evn.recorded_date_time = '200605301500'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='98765', cx_4='MUMC+', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Dekker', xpn_2='Maria', xpn_3='J')
        pid.date_time_of_birth = '19820312'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Tongersestraat 25', xad_3='Maastricht', xad_5='6211LL', xad_6='NL')
        pid.pid_13 = '043-3214567'
        pid.primary_language = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='518273946')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SURG', pl_2='201', pl_3='1')
        pv1.attending_doctor = XCN(xcn_1='5678', xcn_2='Verhoeven', xcn_3='Adriaan', xcn_6='MD')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Dekker', xpn_2='Jan', xpn_3='P')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse')
        nk1.address = XAD(xad_1='Tongersestraat 25', xad_3='Maastricht', xad_5='6211LL', xad_6='NL')
        nk1.nk1_5 = '043-3214568'

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [nk1]

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
    """ Based on live/nl/nl-rhapsody.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ADTSYS')
        msh.sending_facility = HD(hd_1='OLVG')
        msh.receiving_application = HD(hd_1='MASTER')
        msh.receiving_facility = HD(hd_1='OLVG')
        msh.date_time_of_message = '200607150900'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A28')
        msh.message_control_id = 'ADDPAT01'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '200607150900'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='54321', cx_4='OLVG', cx_5='MR')
        pid.patient_name = XPN(xpn_1='van der Meer', xpn_2='Hendrik', xpn_3='F')
        pid.date_time_of_birth = '19900723'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Prinsengracht 150', xad_3='Amsterdam', xad_5='1016GV', xad_6='NL')
        pid.pid_13 = '020-7774321'
        pid.primary_language = CWE(cwe_1='S')
        pid.patient_account_number = CX(cx_1='625183947')

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid

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
    """ Based on live/nl/nl-rhapsody.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CPOE')
        msh.sending_facility = HD(hd_1='Erasmus MC')
        msh.receiving_application = HD(hd_1='RX')
        msh.receiving_facility = HD(hd_1='PHARMACY')
        msh.date_time_of_message = '200605011200'
        msh.message_type = MSG(msg_1='RDE', msg_2='O01', msg_3='RDE_O01')
        msh.message_control_id = 'RDE00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='12345', cx_4='Erasmus MC', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Mulder', xpn_2='Bram', xpn_3='H')
        pid.date_time_of_birth = '19700515'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='101', pl_3='1')
        pv1.attending_doctor = XCN(xcn_1='1234', xcn_2='de Groot', xcn_3='Anneke', xcn_6='MD')

        # .. build the PATIENT_VISIT group ..
        patient_visit = RdeO11PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = RdeO11Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='RX001', ei_2='CPOE')
        orc.placer_order_group_number = EI(ei_1='GRP001', ei_2='CPOE')
        orc.date_time_of_order_event = '200605011200'
        orc.orc_12 = '1234^de Groot^Anneke^^^MD'

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '1^BID&&HL70335^20060501^20060515'
        rxe.give_amount_minimum = '5111-1^Amoxicillin 500mg^NDC'
        rxe.give_amount_maximum = '500'
        rxe.give_dosage_form = CWE(cwe_1='mg')
        rxe.providers_administration_instructions = CWE(cwe_1='CAP')
        rxe.rxe_8 = '1'
        rxe.number_of_refills = '10'
        rxe.rxe_46 = ''

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='PO', cwe_2='Oral', cwe_3='HL70162')

        # .. build the ORDER group ..
        order = RdeO11Order()
        order.orc = orc
        order.rxe = rxe
        order.rxr = rxr

        # .. assemble the full message ..
        msg = RDE_O11()
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

class TestMsg20(unittest.TestCase):
    """ Based on live/nl/nl-rhapsody.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPD')
        msh.sending_facility = HD(hd_1='RHAPSODY')
        msh.receiving_application = HD(hd_1='ARCHIVE')
        msh.receiving_facility = HD(hd_1='Catharina')
        msh.date_time_of_message = '20231105160000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MDM20231105001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T02'
        evn.recorded_date_time = '20231105160000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT33221', cx_4='Catharina', cx_5='MR'), CX(cx_1='592847163', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='de Jong', xpn_2='Geert', xpn_3='W')
        pid.date_time_of_birth = '19550815'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Michelangelolaan 2', xad_3='Eindhoven', xad_5='5623EJ', xad_6='NL', xad_7='H')
        pid.pid_13 = '040-2398765'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='301', pl_3='1', pl_4='Catharina')
        pv1.attending_doctor = XCN(xcn_1='INT001', xcn_2='van Beek', xcn_3='Margaretha', xcn_6='MD')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DS', cwe_2='Discharge Summary', cwe_3='HL70270')
        txa.document_content_presentation = 'TX^Text^HL70191'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20231105150000')
        txa.assigned_document_authenticator = XCN(xcn_1='INT001', xcn_2='van Beek', xcn_3='Margaretha', xcn_6='MD')
        txa.placer_order_number = EI(ei_1='DOC99887')
        txa.unique_document_file_name = 'AU^Authenticated^HL70271'
        txa.document_confidentiality_status = '20231105160000'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'TX'
        obx.observation_identifier = CWE(cwe_1='DS_NOTE', cwe_2='Discharge Summary', cwe_3='LOCAL')
        obx.obx_5 = (
            'Patient was admitted for unstable angina. Underwent coronary angiography with stent placement. Discharged on aspirin, clopidogrel, atorvastatin.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='DS_PDF', cwe_2='Discharge Letter', cwe_3='LOCAL')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKE9udHNsYWdicmllZikKL0NyZWF0b3IgKFJoYXBzb2R5IEludGVncmF0aW9uIEVuZ2luZSkKL1Byb2R1Y2VyIChSaGFwc29keSBQREYg'
            'R2VuZXJhdG9yKQovQ3JlYXRpb25EYXRlIChEOjIwMjMxMTA1MTYwMDAwKQo+PgplbmRvYmoKMiAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMyAwIFIKPj4KZW5kb2JqCjMg'
            'MCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFs0IDAgUl0KL0NvdW50IDEKL01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1Bh'
            'cmVudCAzIDAgUgovQ29udGVudHMgNSAwIFIKL1Jlc291cmNlcyA8PAovRm9udCA8PAovRjEgNiAwIFIKPj4KPj4KPj4KZW5kb2JqCjUgMCBvYmoKPDwKL0xlbmd0aCA0NAo+PgpzdHJl'
            'YW0KQlQKL0YxIDEyIFRmCjcyIDcyMCBUZAooT250c2xhZ2JyaWVmIGthcmRpb2xvZ2llKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjYgMCBvYmoKPDwKL1R5cGUgL0ZvbnQKL1N1YnR5'
            'cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0aWNhCj4+CmVuZG9iagp4cmVmCjAgNwowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDE1OCAwMDAw'
            'MCBuIAowMDAwMDAwMjA3IDAwMDAwIG4gCjAwMDAwMDAzMDYgMDAwMDAgbiAKMDAwMDAwMDQ5OSAwMDAwMCBuIAowMDAwMDAwNTkzIDAwMDAwIG4gCnRyYWlsZXIKPDwKL1NpemUgNwov'
            'Um9vdCAyIDAgUgo+PgpzdGFydHhyZWYKNjcxCiUlRU9GCg=='
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = MdmT02Observation()
        observation_2.obx = obx_2

        # .. assemble the full message ..
        msg = MDM_T02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.txa = txa
        msg.observation = [observation, observation_2]

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
