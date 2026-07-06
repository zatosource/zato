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
from zato.hl7v2.v2_9.datatypes import AUI, CNE, CWE, CX, DLD, EI, EIP, HD, MOC, MSG, PL, PT, VID, XAD, XCN, XON, XPN, XTN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA05NextOfKin, MdmT02Observation, OmlO21NextOfKin, OmlO21Observation, OmlO21ObservationRequest, \
    OmlO21Order, OmlO21Patient, OmlO21Specimen, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, SiuS12Patient, SiuS12PersonnelResource, SiuS12Resources, SiuS12Service
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A05, MDM_T02, OML_O21, ORM_O01, ORU_R01, SIU_S12
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, AL1, DG1, EVN, IN1, MSH, NK1, NTE, OBR, OBX, ORC, PD1, PID, PV1, PV2, RGS, ROL, SCH, SPM, TXA
from zato.hl7v2.z_segments import ZBE

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('nl', 'nl-epic.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/nl/nl-epic.md, message no. 1
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
        evn.operator_id = XCN(xcn_1='ADMIN', xcn_2='Bakker', xcn_3='Johanna', xcn_6='RN')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN12345', cx_4='UMCU', cx_5='MR')
        pid.patient_name = XPN(xpn_1='van den Berg', xpn_2='Hendrik', xpn_3='Willem')
        pid.date_time_of_birth = '19800115'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='Oudegracht 88', xad_3='Utrecht', xad_4='UT', xad_5='3511AB', xad_6='NL')
        pid.pid_13 = '^PRN^PH^^^^^030-2345678'
        pid.primary_language = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')
        pid.patient_account_number = CX(cx_1='ACCT98765', cx_4='UMCU', cx_5='AN')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='0101', pl_3='01', pl_4='UMCU', pl_8='NURS')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Emergency', cwe_3='HL70007')
        pv1.attending_doctor = XCN(xcn_1='ATT1234', xcn_2='de Groot', xcn_3='Anna', xcn_6='MD')
        pv1.referring_doctor = XCN(xcn_1='REF5678', xcn_2='Visser', xcn_3='Karel', xcn_6='MD')
        pv1.hospital_service = CWE(cwe_1='MED', cwe_2='Medical', cwe_3='HL70069')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='ATT1234', xcn_2='de Groot', xcn_3='Anna', xcn_6='MD')
        pv1.patient_type = CWE(cwe_1='IP', cwe_2='Inpatient', cwe_3='HL70004')
        pv1.discharge_disposition = CWE(cwe_1='UMCU')
        pv1.diet_type = CWE(cwe_1='A')
        pv1.account_status = CWE(cwe_1='202603011415')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='van den Berg', xpn_2='Cornelia', xpn_3='M')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Oudegracht 88', xad_3='Utrecht', xad_4='UT', xad_5='3511AB')
        nk1.nk1_5 = '^PRN^PH^^^^^030-2345679'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='ZK001', cwe_2='Zilveren Kruis')
        in1.insurance_company_id = CX(cx_1='ZK')
        in1.in1_4 = 'Postbus 444^^Leiden^^2300AK'
        in1.insurance_company_address = XAD(xad_2='WPN', xad_3='PH', xad_8='071-5553333')
        in1.in1_7 = 'GRP54321'
        in1.authorization_information = AUI(aui_1='20230101')
        in1.plan_type = CWE(cwe_1='20261231')
        in1.insureds_relationship_to_patient = CWE(cwe_1='SELF', cwe_2='Self', cwe_3='HL70063')
        in1.insureds_date_of_birth = 'van den Berg^Hendrik^Willem'
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
    """ Based on live/nl/nl-epic.md, message no. 2
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
        pid.patient_name = XPN(xpn_1='van den Berg', xpn_2='Hendrik', xpn_3='Willem')
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
        obr.obr_14 = 'ATT1234^de Groot^Anna^^^MD'
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
    """ Based on live/nl/nl-epic.md, message no. 3
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
        pid.patient_name = XPN(xpn_1='van den Berg', xpn_2='Hendrik', xpn_3='Willem')
        pid.date_time_of_birth = '19800115'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='0101', pl_3='01', pl_4='UMCU')
        pv1.attending_doctor = XCN(xcn_1='ATT1234', xcn_2='de Groot', xcn_3='Anna', xcn_6='MD')

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
        orc.orc_12 = 'ATT1234^de Groot^Anna^^^MD'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD5678', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC with Diff', cwe_3='LN')
        obr.observation_date_time = '202603011400'
        obr.obr_16 = 'ATT1234^de Groot^Anna^^^MD'
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
    """ Based on live/nl/nl-epic.md, message no. 4
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
        sch.filler_contact_person = XCN(xcn_1='ATT1234', xcn_2='de Groot', xcn_3='Anna', xcn_6='MD')
        sch.filler_contact_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_8='030-2221234')
        sch.filler_contact_address = XAD(xad_1='POLI ALG', xad_2='UMCU')
        sch.filler_contact_location = PL(pl_1='ATT1234', pl_2='de Groot', pl_3='Anna', pl_6='MD')
        sch.sch_21 = 'Booked'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN12345', cx_4='UMCU', cx_5='MR')
        pid.patient_name = XPN(xpn_1='van den Berg', xpn_2='Hendrik', xpn_3='Willem')
        pid.date_time_of_birth = '19800115'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Oudegracht 88', xad_3='Utrecht', xad_4='UT', xad_5='3511AB')
        pid.pid_13 = '^PRN^PH^^^^^030-2345678'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='POLI ALG', pl_2='EXAM3', pl_3='01', pl_4='UMCU')
        pv1.attending_doctor = XCN(xcn_1='ATT1234', xcn_2='de Groot', xcn_3='Anna', xcn_6='MD')

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
        aip.personnel_resource_id = XCN(xcn_1='ATT1234', xcn_2='de Groot', xcn_3='Anna', xcn_6='MD')
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
        ail.location_resource_id = PL(pl_1='POLI ALG', pl_2='EXAM3', pl_3='01', pl_4='UMCU')
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
    """ Based on live/nl/nl-epic.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='TRANS_SYS')
        msh.sending_facility = HD(hd_1='ERASMUS MC')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='ERASMUS MC')
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
        pid.patient_identifier_list = CX(cx_1='MRN12345', cx_4='ERASMUS MC', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Brouwer', xpn_2='Jacobus', xpn_3='Adriaan')
        pid.date_time_of_birth = '19800115'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SURG', pl_2='OR3', pl_3='01', pl_4='ERASMUS MC')
        pv1.attending_doctor = XCN(xcn_1='SUR5678', xcn_2='Meijer', xcn_3='Theodora', xcn_6='MD')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='OP', cwe_2='Operative Note', cwe_3='HL70270')
        txa.document_content_presentation = 'TX^Text^HL70191'
        txa.primary_activity_provider_code_name = XCN(xcn_1='202603011600')
        txa.assigned_document_authenticator = XCN(xcn_1='SUR5678', xcn_2='Meijer', xcn_3='Theodora', xcn_6='MD')
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
    """ Based on live/nl/nl-epic.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.msh_2 = '^_\\&'
        msh.sending_application = HD(hd_1='ZorgDomein')
        msh.date_time_of_message = '20160324163509+0100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'ZD200046119'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_4='NLMINBIZA', cx_5='NNNLD')
        pid.patient_name = XPN(xpn_1='van Dijk&van&Dijk', xpn_2='Pieter', xpn_3='Jan', xpn_7='L')
        pid.date_time_of_birth = '20000101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Keizersgracht 42&Keizersgracht&42', xad_3='Amsterdam', xad_5='1016CS', xad_6='NL', xad_7='H')
        pid.pid_13 = '020-5551234_^NET^Internet^p.vandijk@kpnmail.nl'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ZD200046119')
        orc.date_time_of_order_event = '20160324163432+0100'
        orc.orc_10 = '^&&het Willemsen^E.F.G.'
        orc.orc_12 = '01004567^&&van Houten^Z.Z.^^^^^^VEKTIS'
        orc.orc_14 = '015-2222222'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ZD200046119')
        obr.universal_service_identifier = CWE(cwe_1='CIS', cwe_2='Cardiologie', cwe_3='ZORGDOMEIN')
        obr.observation_date_time = '20160324163432+0100'
        obr.obr_16 = '01004567^&&van Houten^Z.Z.^^^^^^VEKTIS'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='VB', cwe_3='123')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='CARHAR', cwe_2='Hartfalen', cwe_3='ZORGDOMEIN')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKP7/KQovQ3JlYXRvciAo/v8AdwBrAGgAdABtAGwAdABvAHAAZABmACAAMAAuADEAMgAuADIALgExKQovUHJvZHVjZXIgKP7/AFEAdAAg'
            'ADQALgA4AC4ANikKL0NyZWF0aW9uRGF0ZSAoRDoyMDE2MDMyNDE2MzUwOCswMScwMCcpCj4+CmVuZG9iagoz'
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'FT'
        obx_3.observation_identifier = CWE(cwe_1='CARCOA001', cwe_2='consult cardioloog', cwe_3='ZORGDOMEIN')
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
    """ Based on live/nl/nl-epic.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.msh_2 = '^_\\&'
        msh.sending_application = HD(hd_1='ZorgDomein')
        msh.date_time_of_message = '20160324163441+0100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'ZD200046119'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_4='NLMINBIZA', cx_5='NNNLD')
        pid.patient_name = XPN(xpn_1='Jansen&Jansen&Jansen', xpn_2='Maria', xpn_3='Floor', xpn_7='L')
        pid.date_time_of_birth = '20000101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Laan van Meerdervoort 15&Laan van Meerdervoort&15', xad_3='Den Haag', xad_5='2517AK', xad_6='NL', xad_7='H')
        pid.pid_13 = '070-3456789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')

        # .. build the VISIT group ..
        visit = OruR01Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ZD200046119')
        orc.date_time_of_order_event = '20160324163432+0100'
        orc.orc_10 = '^&&het Bakker^D.E.F.'
        orc.orc_12 = '01004567^&&van Leeuwen^Z.Z.^^^^^^VEKTIS'
        orc.orc_14 = '015-2222222'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ZD200046119')
        obr.universal_service_identifier = CWE(cwe_1='CIS', cwe_2='Cardiologie', cwe_3='ZORGDOMEIN')
        obr.observation_date_time = '20160324163432+0100'
        obr.obr_16 = '01004567^&&van Leeuwen^Z.Z.^^^^^^VEKTIS'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='AF', cwe_3='123')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='CARHAR', cwe_2='Hartfalen', cwe_3='ZORGDOMEIN')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKP7/KQovQ3JlYXRvciAo/v8AdwBrAGgAdABtAGwAdABvAHAAZABmACAAMAAuADEAMgAuADIALgExKQovUHJvZHVjZXIgKP7/AFEAdAAg'
            'ADQALgA4AC4ANikKL0NyZWF0aW9uRGF0ZSAoRDoyMDE2MDMyNDE2MzQ0MSswMScwMCcpCj4+CmVuZG9iagoz'
        )
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'FT'
        obx_3.observation_identifier = CWE(cwe_1='CARCOA001', cwe_2='consult cardioloog', cwe_3='ZORGDOMEIN')
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
    """ Based on live/nl/nl-epic.md, message no. 8
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
        pid.patient_identifier_list = [CX(cx_1='1234567', cx_5='PI'), CX(cx_1='999999011', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Jansen', xpn_2='Pieter', xpn_3='A', xpn_7='L')
        pid.date_time_of_birth = '19650312'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Kerkstraat 42', xad_3='Amsterdam', xad_5='1012AB', xad_6='NL', xad_7='H')
        pid.pid_13 = '020-5551234'

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='123')
        obr.filler_order_number = EI(ei_1='20050701015070', ei_2='Labosys')
        obr.filler_field_2 = 'LAB'
        obr.results_rpt_status_chng_date_time = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='266', cwe_2='Bezinking', cwe_3='L', cwe_4='BSE')
        obx.obx_5 = '2'
        obx.units = CWE(cwe_1='mm/uur')
        obx.reference_range = '0 - 15'
        obx.interpretation_codes = CWE(cwe_1='""')
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
    """ Based on live/nl/nl-epic.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='?')
        msh.sending_facility = HD(hd_1='Saint-Louis')
        msh.receiving_application = HD(hd_1='?')
        msh.receiving_facility = HD(hd_1='Saint-Louis')
        msh.date_time_of_message = '20050530082015'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = '000001'
        msh.processing_id = PT(pt_1='T')
        msh.version_id = VID(vid_1='2.5')
        msh.country_code = 'FRA'
        msh.character_set = '8859/15'
        msh.principal_language_of_message = CWE(cwe_1='EN')

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20050530082000'
        evn.operator_id = XCN(xcn_1='1001', xcn_2='Renard', xcn_3='Janine')
        evn.event_occurred = '20050530082000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='12345', cx_4='Saint-Louis', cx_5='PI')
        pid.patient_name = XPN(xpn_1='Lefèvre', xpn_2='Robert', xpn_7='L')
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_account_number = CX(cx_1='987654', cx_4='Saint-Louis', cx_5='AN')

        # .. build ROL ..
        rol = ROL()
        rol.rol_2 = 'AD'
        rol.rol_3 = 'FHCP'
        rol.rol_4 = '7777^Moreau^Philippe'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.referring_doctor = XCN(xcn_1='2001', xcn_2='Dupont', xcn_3='Charles')

        # .. build ZBE ..
        zbe = ZBE()
        zbe.zbe_1 = 'mvt1'
        zbe.zbe_2 = '20050530082000'
        zbe.zbe_4 = 'INSERT'
        zbe.zbe_5 = 'N'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.rol = rol
        msg.pv1 = pv1
        msg.extra_segments = [zbe]

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
    """ Based on live/nl/nl-epic.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.msh_2 = '^~\\&#'
        msh.sending_application = HD(hd_1='NIST EHR')
        msh.sending_facility = HD(hd_1='NIST EHR Facility')
        msh.receiving_application = HD(hd_1='NIST Test Lab APP')
        msh.receiving_facility = HD(hd_1='NIST Lab Facility')
        msh.date_time_of_message = '20130211184101-0500'
        msh.message_type = MSG(msg_1='OML', msg_2='O21', msg_3='OML_O21')
        msh.message_control_id = 'NIST-LOI_5.0_1.1-NG'
        msh.processing_id = PT(pt_1='T')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.msh_21 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='PATID5421', cx_4='NIST MPI', cx_5='MR')
        pid.patient_name = XPN(xpn_1='de Graaf', xpn_2='Saskia', xpn_3='Margaretha', xpn_7='L')
        pid.date_time_of_birth = '19820304'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.race = CWE(cwe_1='2106-3', cwe_2='White', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='Singel 105', xad_3='Amsterdam', xad_4='NH', xad_5='1012VG', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^020^6234567'
        pid.ethnic_group = CWE(cwe_1='N', cwe_2='Not Hispanic or Latino', cwe_3='HL70189')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='de Graaf', xpn_2='Daan', xpn_3='Willem', xpn_7='L')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Singel 105', xad_3='Amsterdam', xad_4='NH', xad_5='1012VG', xad_7='H')
        nk1.nk1_13 = ''

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = OmlO21NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build the PATIENT group ..
        patient = OmlO21Patient()
        patient.pid = pid
        patient.next_of_kin = next_of_kin

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD448811', ei_2='NIST EHR')
        orc.date_time_of_order_event = '20120628070100'
        orc.orc_12 = '5742200012^Vermeer^Adriaan^^^^^^NPI^L^^^NPI'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD448811', ei_2='NIST EHR')
        obr.universal_service_identifier = CWE(cwe_1='1000', cwe_2='Hepatitis A B C Panel', cwe_3='99USL')
        obr.observation_date_time = '20120628070100'
        obr.obr_16 = '5742200012^Vermeer^Adriaan^^^^^^NPI^L^^^NPI'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='F11.129', cwe_2='Opioid abuse with intoxication,unspecified', cwe_3='I10C')
        dg1.diagnosis_type = CWE(cwe_1='W')
        dg1.diagnosis_priority = '1'

        # .. build the OBSERVATION_REQUEST group ..
        observation_request = OmlO21ObservationRequest()
        observation_request.obr = obr
        observation_request.dg1 = dg1

        # .. build the ORDER group ..
        order = OmlO21Order()
        order.orc = orc
        order.observation_request = observation_request

        # .. assemble the full message ..
        msg = OML_O21()
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
    """ Based on live/nl/nl-epic.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='P0241')
        msh.sending_facility = HD(hd_1='HOMERTON')
        msh.receiving_application = HD(hd_1='HOMERTON_TIE')
        msh.receiving_facility = HD(hd_1='HOMERTON')
        msh.date_time_of_message = '20150209170901'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31')
        msh.message_control_id = 'Q111111119T4083493511111111'
        msh.version_id = VID(vid_1='2.3')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20150209170901'
        evn.operator_id = XCN(
            xcn_1='101111',
            xcn_2='Dekker',
            xcn_3='Geert',
            xcn_9='PERSONNEL PRIMARY IDENTIFIER',
            xcn_10='Personnel',
            xcn_13='Personnel Primary Identifier',
            xcn_14='""',
        )

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.pid_2 = '999999^^^Homerton Case Note Number^MRN^""'
        pid.patient_identifier_list = [CX(cx_1='999998', cx_4='Homerton Case Note Number', cx_5='CNN'), CX(cx_1='111111', cx_4='Person ID', cx_5='Person ID')]
        pid.patient_name = [XPN(xpn_1='van Vliet', xpn_2='Anneke', xpn_5='Mrs', xpn_7='Current'), XPN(xpn_1=''), XPN(xpn_2='van Vliet', xpn_7='Alternate')]
        pid.date_time_of_birth = '19781030000000'
        pid.administrative_sex = CWE(cwe_1='Female')
        pid.pid_9 = '^van Vliet^^^^^Alternate~van Vliet^Johanna^^^Mrs^^Preferred~Brouwer^Anneke^^^Mrs^^Previous'
        pid.race = CWE(cwe_1='""')
        pid.patient_address = [
            XAD(xad_1='Flat 1', xad_2='15 Churchillaan', xad_4='Amsterdam', xad_5='1078AA', xad_6='""', xad_7='home', xad_9='""'),
            XAD(xad_1='MAJOR HOUSE', xad_2='CHURCH ROAD', xad_4='""', xad_6='""', xad_7='Previous', xad_8='AMSTERDAM', xad_9='""'),
        ]
        pid.pid_13 = '^Home^Tel~06-12345678^Mobile Number^Tel'
        pid.pid_14 = '^Business'
        pid.primary_language = CWE(cwe_1='Dutch')
        pid.marital_status = CWE(cwe_1='""')
        pid.religion = CWE(cwe_1='Not Known')
        pid.patient_account_number = CX(cx_1='999999', cx_4='Homerton FIN', cx_5='Encounter No.', cx_6='""')
        pid.pid_19 = '9999999999'
        pid.ethnic_group = CWE(cwe_1='European')
        pid.birth_order = '0'
        pid.citizenship = CWE(cwe_1='""')
        pid.veterans_military_status = CWE(cwe_1='""')
        pid.pid_28 = '""'
        pid.patient_death_indicator = 'No'
        pid.identity_reliability_code = CWE(cwe_1='Trace in Progress')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.living_dependency = CWE(cwe_1='""')
        pd1.living_arrangement = CWE(cwe_1='""')
        pd1.pd1_4 = 'G88888888^Huisarts^Elisabeth^^020711111111^F84040^HUISARTSENPRAKTIJK CENTRUM^100 SINGEL^&AMSTERDAM&1012AB^^^^^Q06'
        pd1.student_indicator = CWE(cwe_1='""')
        pd1.living_will_code = CWE(cwe_1='""')
        pd1.organ_donor_code = CWE(cwe_1='""')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='van Vliet', xpn_2='Willem', xpn_7='Current')
        nk1.relationship = CWE(cwe_1='""')
        nk1.address = XAD(xad_1='Flat 1', xad_2='15 Churchillaan', xad_4='""', xad_5='1078AA', xad_6='""', xad_9='""')
        nk1.nk1_5 = '06-98765432'
        nk1.contact_role = CWE(cwe_1='Next of Kin')
        nk1.primary_language = CWE(cwe_1='""')

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='Inpatient')
        pv1.assigned_patient_location = PL(pl_1='HUH AE OMU', pl_2='OMU B', pl_3='Bed 03', pl_4='HOMERTON UNIVER', pl_6='Bed(s)', pl_7='Homerton UH')
        pv1.pv1_4 = 'Emergency-A\\T\\E/Dental'
        pv1.prior_patient_location = PL(pl_1='HUH AE Adults', pl_2='""', pl_3='""', pl_4='HOMERTON UNIVER', pl_7='Homerton UH')
        pv1.attending_doctor = XCN(
            xcn_1='1122334',
            xcn_2='Yilmaz',
            xcn_3='Ahmed',
            xcn_9='PERSONNEL PRIMARY IDENTIFIER',
            xcn_10='Personnel',
            xcn_13='Personnel Primary Identifier',
            xcn_14='""',
        )
        pv1.consulting_doctor = XCN(
            xcn_1='3333444',
            xcn_2='Patel',
            xcn_3='Raj',
            xcn_9='PERSONNEL PRIMARY IDENTIFIER',
            xcn_10='Personnel',
            xcn_13='Personnel Primary Identifier',
            xcn_14='""',
        )
        pv1.temporary_location = PL(pl_1='Accident and Emergency')
        pv1.preadmit_test_indicator = CWE(cwe_1='""')
        pv1.re_admission_indicator = CWE(cwe_1='""')
        pv1.admit_source = CWE(cwe_1='New Problem/First Attendance')
        pv1.pv1_15 = 'NHS Provider-General (inc.A\\T\\E-this Hosp)'
        pv1.vip_indicator = CWE(cwe_1='""')
        pv1.admitting_doctor = XCN(xcn_1='""')
        pv1.visit_number = CX(cx_1='Inpatient')
        pv1.pv1_20 = '5000000^0^""^^Attendance No.'
        pv1.charge_price_indicator = CWE(cwe_1='""')
        pv1.credit_rating = CWE(cwe_1='""')
        pv1.discharged_to_location = DLD(dld_1='Admitted as Inpatient')
        pv1.diet_type = CWE(cwe_1='""')
        pv1.servicing_facility = CWE(cwe_1='""')
        pv1.pv1_40 = 'HOMERTON UNIVER'
        pv1.pending_location = PL(pl_1='Active')
        pv1.discharge_date_time = '20150208113419'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.accommodation_code = CWE(cwe_1='NHS')
        pv2.admit_reason = CWE(cwe_2='4 UNWELL')
        pv2.transfer_reason = CWE(cwe_1='Transfer from ED')
        pv2.visit_user_code = CWE(cwe_1='""')
        pv2.estimated_length_of_inpatient_stay = '0'
        pv2.referral_source_code = XCN(xcn_1='""')
        pv2.visit_publicity_code = CWE(cwe_1='""')
        pv2.visit_protection_indicator = '""'
        pv2.pv2_23 = '^^1'

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/nl/nl-epic.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABOSYS')
        msh.sending_facility = HD(hd_1='UMCG_LAB')
        msh.receiving_application = HD(hd_1='UMCG_MIC')
        msh.receiving_facility = HD(hd_1='UMCG')
        msh.date_time_of_message = '20180501120000'
        msh.message_type = MSG(msg_1='OML', msg_2='O21', msg_3='OML_O21')
        msh.message_control_id = 'MSG20180501001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.character_set = 'NLD'
        msh.principal_language_of_message = CWE(cwe_1='8859/1')
        msh.sending_responsible_organization = XON(xon_1='2.16.840.1.113883.2.4.3.11.60.25.4.5', xon_2='NL')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='987654321', cx_5='PI'), CX(cx_1='999900011', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='de Vries', xpn_2='Maria', xpn_3='J', xpn_7='L')
        pid.date_time_of_birth = '19750822'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Damrak 100', xad_3='Amsterdam', xad_5='1012LP', xad_6='NL', xad_7='H')

        # .. build the PATIENT group ..
        patient = OmlO21Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD99001', ei_2='UMCG_LAB')
        orc.date_time_of_order_event = '20180501110000'
        orc.orc_12 = '1234567^Arts^Jan^^^^^^BIG'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD99001', ei_2='UMCG_LAB')
        obr.universal_service_identifier = CWE(cwe_1='29576-6', cwe_2='Bacterial susceptibility panel', cwe_3='LN')
        obr.observation_date_time = '20180501100000'
        obr.obr_16 = '1234567^Arts^Jan^^^^^^BIG'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='6652-2', cwe_2='Meropenem [Susceptibility] by Minimum inhibitory concentration (MIC)', cwe_3='LN')
        obx.obx_5 = '>=16'
        obx.units = CWE(cwe_1='mg/L')
        obx.interpretation_codes = CWE(cwe_1='null')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OmlO21Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='7029-2', cwe_2='Meropenem [Susceptibility] by Gradient strip', cwe_3='LN')
        obx_2.obx_5 = '8,0'
        obx_2.units = CWE(cwe_1='mg/L')
        obx_2.interpretation_codes = CWE(cwe_1='null')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OmlO21Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.observation_identifier = CWE(cwe_1='18943-1', cwe_2='Meropenem [Susceptibility]', cwe_3='LN')
        obx_3.interpretation_codes = CWE(cwe_1='R')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OmlO21Observation()
        observation_3.obx = obx_3

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_type = CWE(cwe_1='BLD', cwe_2='Blood', cwe_3='HL70487')

        # .. build the SPECIMEN group ..
        specimen = OmlO21Specimen()
        specimen.spm = spm

        # .. build the OBSERVATION_REQUEST group ..
        observation_request = OmlO21ObservationRequest()
        observation_request.obr = obr
        observation_request.observation = observation
        observation_request.observation_2 = observation_2
        observation_request.observation_3 = observation_3
        observation_request.specimen = specimen

        # .. build the ORDER group ..
        order = OmlO21Order()
        order.orc = orc
        order.observation_request = observation_request

        # .. assemble the full message ..
        msg = OML_O21()
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
    """ Based on live/nl/nl-epic.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ADT1')
        msh.sending_facility = HD(hd_1='AMPHIA')
        msh.receiving_application = HD(hd_1='GHH LAB, INC.')
        msh.receiving_facility = HD(hd_1='AMPHIA')
        msh.date_time_of_message = '198808181126'
        msh.security = 'SECURITY'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.8')
        msh.msh_14 = ''

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '200708181123'
        evn.evn_4 = ''

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PATID1234', cx_4='ADT1', cx_5='MR', cx_6='AMPHIA'), CX(cx_1='283746591', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Mulder', xpn_2='Geert', xpn_3='Jan', xpn_4='III')
        pid.date_time_of_birth = '19610615'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.race = CWE(cwe_1='2106-3', cwe_2='WHITE', cwe_3='HL70005')
        pid.patient_address = XAD(xad_1='Marktplein 7', xad_3='Breda', xad_5='4811AB', xad_6='NL')
        pid.pid_13 = '^PRN^PH^CP^^^076^5142233'
        pid.pid_14 = '^WPN^PH^CP^^^076^5142234'
        pid.primary_language = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.religion = CWE(cwe_1='CHR', cwe_2='Christian', cwe_3='HL70006')
        pid.patient_account_number = CX(cx_1='ACCT001')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='WARD1', pl_2='ROOM02', pl_3='BED01', pl_4='AMPHIA')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent', cwe_3='HL70007')
        pv1.prior_patient_location = PL(pl_1='WARD1', pl_2='ROOM01', pl_3='BED01')
        pv1.attending_doctor = XCN(xcn_1='ATTEND001', xcn_2='van der Linden', xcn_3='Pieter', xcn_4='J', xcn_5='III', xcn_6='DR')
        pv1.referring_doctor = XCN(xcn_1='REFER001', xcn_2='Bos', xcn_3='Elisabeth', xcn_4='A', xcn_5='JR', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='SUR', cwe_2='Surgery', cwe_3='HL70069')
        pv1.admit_source = CWE(cwe_1='ADM', cwe_2='ADMIT', cwe_3='HL70023')

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/nl/nl-epic.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.msh_2 = '^\\~\\&'
        msh.sending_application = HD(hd_1='IRIS')
        msh.sending_facility = HD(hd_1='IRIS')
        msh.receiving_application = HD(hd_1='VENDOR')
        msh.receiving_facility = HD(hd_1='VENDOR')
        msh.date_time_of_message = '20170410145907'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02')
        msh.message_control_id = '170410145907'
        msh.processing_id = PT(pt_1='T')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='12345', cx_4='IRIS', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Bakker', xpn_2='Anneke')
        pid.date_time_of_birth = '19650101'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Breestraat 30', xad_3='Leiden', xad_5='2311CJ')
        pid.pid_13 = '^PRN^PH^^^^^071-5234567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='CLINIC', pl_2='RM1', pl_3='BED1')
        pv1.attending_doctor = XCN(xcn_1='PROV001', xcn_2='Smit', xcn_3='Daan', xcn_6='MD')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='OP', cwe_2='Examination Report', cwe_3='HL70270')
        txa.document_content_presentation = 'TX'
        txa.primary_activity_provider_code_name = XCN(xcn_1='20170410')
        txa.transcriptionist_code_name = XCN(xcn_1='PROV001', xcn_2='Smit', xcn_3='Daan', xcn_6='MD')
        txa.filler_order_number = EI(ei_1='RPT001')
        txa.document_completion_status = 'AU'
        txa.document_availability_status = '20170410145907'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='RETINAL_IMG', cwe_2='Retinal Image Right Eye', cwe_3='LOCAL')
        obx.obx_5 = (
            '^image^jpeg^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMo'
            'GhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAQABADASIAAhEBAxEB/8QAFgABAQEAAAAAAAAAAAAAAAAABgcI/8QAJhAAAQMD'
            'AwQCAwAAAAAAAAAAAQIDBAAFEQYSIQcxQVETImFx/8QAFQEBAQAAAAAAAAAAAAAAAAAABQb/xAAeEQABAwQDAAAAAAAAAAAAAAABAAIDBAUSITFRYf/aAAwDAQACEQMRAD8Aq=='
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='IOP_OD', cwe_2='Intraocular Pressure Right Eye', cwe_3='LOCAL')
        obx_2.obx_5 = '14'
        obx_2.units = CWE(cwe_1='mmHg')
        obx_2.reference_range = '10-21'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = MdmT02Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='IOP_OS', cwe_2='Intraocular Pressure Left Eye', cwe_3='LOCAL')
        obx_3.obx_5 = '15'
        obx_3.units = CWE(cwe_1='mmHg')
        obx_3.reference_range = '10-21'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = MdmT02Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'TX'
        obx_4.observation_identifier = CWE(cwe_1='FINDINGS', cwe_2='Clinical Findings', cwe_3='LOCAL')
        obx_4.obx_5 = 'No diabetic retinopathy detected. Cup-to-disc ratio within normal limits bilaterally.'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = MdmT02Observation()
        observation_4.obx = obx_4

        # .. assemble the full message ..
        msg = MDM_T02()
        msg.msh = msh
        msg.pid = pid
        msg.pv1 = pv1
        msg.txa = txa
        msg.observation = [observation, observation_2, observation_3, observation_4]

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
    """ Based on live/nl/nl-epic.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABSYS')
        msh.sending_facility = HD(hd_1='AMC_LAB')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='AMC')
        msh.date_time_of_message = '20200915143000+0200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20200915001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.character_set = 'NLD'
        msh.principal_language_of_message = CWE(cwe_1='8859/1')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='7654321', cx_5='PI'), CX(cx_1='999911234', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Bakker', xpn_2='Jan', xpn_3='P', xpn_7='L')
        pid.date_time_of_birth = '19580622'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Prinsengracht 263', xad_3='Amsterdam', xad_5='1016GV', xad_6='NL', xad_7='H')
        pid.pid_13 = '020-6249876'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='POLI INT', pl_2='01', pl_3='01', pl_4='AMC')

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
        orc.placer_order_number = EI(ei_1='ORD2020001', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='FILL2020001', ei_2='LABSYS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2020001', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='FILL2020001', ei_2='LABSYS')
        obr.universal_service_identifier = CWE(cwe_1='24326-1', cwe_2='Electrolytes 1998 panel - Serum or Plasma', cwe_3='LN')
        obr.observation_date_time = '20200915100000+0200'
        obr.obr_16 = '12345678^Jansen^Karel^^^^^^BIG'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Natrium', cwe_3='LN')
        obx.obx_5 = '138'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '136-145'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Kalium', cwe_3='LN')
        obx_2.obx_5 = '4.5'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '3.5-5.0'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2075-0', cwe_2='Chloride', cwe_3='LN')
        obx_3.obx_5 = '101'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '98-107'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1963-8', cwe_2='Bicarbonaat', cwe_3='LN')
        obx_4.obx_5 = '24'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '22-29'
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
    """ Based on live/nl/nl-epic.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='RADBOUDUMC')
        msh.receiving_application = HD(hd_1='PAS')
        msh.receiving_facility = HD(hd_1='RADBOUDUMC')
        msh.date_time_of_message = '20210315090000+0100'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A04')
        msh.message_control_id = 'REG20210315001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'NLD'
        msh.principal_language_of_message = CWE(cwe_1='8859/1')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20210315090000+0100'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='8765432', cx_5='PI'), CX(cx_1='999922345', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='van den Berg', xpn_2='Sophie', xpn_3='M', xpn_7='L')
        pid.date_time_of_birth = '19900714'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Grote Markt 1', xad_3='Nijmegen', xad_5='6511KB', xad_6='NL', xad_7='H')
        pid.pid_13 = '024-3611234'
        pid.primary_language = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='S', cwe_2='Single', cwe_3='HL70002')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='POLI DERM', pl_2='201', pl_3='A', pl_4='RADBOUDUMC')
        pv1.admission_type = CWE(cwe_1='R', cwe_2='Routine', cwe_3='HL70007')
        pv1.attending_doctor = XCN(xcn_1='54321678', xcn_2='de Groot', xcn_3='Anna', xcn_9='BIG')
        pv1.hospital_service = CWE(cwe_1='DER', cwe_2='Dermatologie', cwe_3='HL70069')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='54321678', xcn_2='de Groot', xcn_3='Anna', xcn_9='BIG')
        pv1.patient_type = CWE(cwe_1='OP', cwe_2='Outpatient', cwe_3='HL70004')
        pv1.discharge_disposition = CWE(cwe_1='RADBOUDUMC')
        pv1.diet_type = CWE(cwe_1='A')
        pv1.account_status = CWE(cwe_1='20210315090000+0100')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='VGZ001', cwe_2='VGZ')
        in1.insurance_company_id = CX(cx_1='VGZ')
        in1.in1_4 = 'Postbus 1000^^Arnhem^^6800BA^NL'
        in1.group_number = 'GRP789'
        in1.plan_type = CWE(cwe_1='20210101')
        in1.name_of_insured = XPN(xpn_1='20211231')

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
    """ Based on live/nl/nl-epic.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='UMCG')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='UMCG_RAD')
        msh.date_time_of_message = '20220118141500+0100'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'RAD20220118001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'NLD'
        msh.principal_language_of_message = CWE(cwe_1='8859/1')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='3456789', cx_5='PI'), CX(cx_1='999933456', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Mulder', xpn_2='Frederik', xpn_3='H', xpn_7='L')
        pid.date_time_of_birth = '19720930'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Vijzelstraat 77', xad_3='Amsterdam', xad_5='1017HG', xad_6='NL', xad_7='H')
        pid.pid_13 = '020-5557890'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='POLI RAD', pl_2='102', pl_3='A', pl_4='UMCG')
        pv1.attending_doctor = XCN(xcn_1='98765432', xcn_2='Visser', xcn_3='Maria', xcn_9='BIG')

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
        orc.placer_order_number = EI(ei_1='ORDRAD001', ei_2='EPIC')
        orc.parent_order = EIP(eip_1='20220118141500+0100')
        orc.orc_11 = '98765432^Visser^Maria^^^^^^BIG'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORDRAD001', ei_2='EPIC')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Chest 2 views', cwe_3='CPT4')
        obr.observation_date_time = '20220118141500+0100'
        obr.obr_16 = '98765432^Visser^Maria^^^^^^BIG'
        obr.result_status = '^ROUTINE'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R05.9', cwe_2='Hoest, niet gespecificeerd', cwe_3='I10')

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
        nte.comment = 'Persisterende hoest > 3 weken, uitsluiten pneumonie.'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [nte]

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
    """ Based on live/nl/nl-epic.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PATH_SYS')
        msh.sending_facility = HD(hd_1='CATHARINA')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='CATHARINA')
        msh.date_time_of_message = '202204051430'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'PATH20220405001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN98765', cx_4='CATHARINA', cx_5='MR')
        pid.patient_name = XPN(xpn_1='de Jong', xpn_2='Margaretha', xpn_3='Elisabeth')
        pid.date_time_of_birth = '19550812'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SURG', pl_2='401', pl_3='A', pl_4='CATHARINA')
        pv1.attending_doctor = XCN(xcn_1='SUR001', xcn_2='Dekker', xcn_3='Michiel', xcn_6='MD')

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
        orc.placer_order_number = EI(ei_1='ORDPATH001', ei_2='EPIC')
        orc.filler_order_number = EI(ei_1='FILLPATH001', ei_2='PATH_SYS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORDPATH001', ei_2='EPIC')
        obr.filler_order_number = EI(ei_1='FILLPATH001', ei_2='PATH_SYS')
        obr.universal_service_identifier = CWE(cwe_1='88305', cwe_2='Surgical Pathology', cwe_3='CPT4')
        obr.observation_date_time = '202204051000'
        obr.obr_14 = 'SUR001^Dekker^Michiel^^^MD'
        obr.filler_field_1 = '202204051415'
        obr.results_rpt_status_chng_date_time = 'PATH'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='22637-3', cwe_2='Pathology report final diagnosis', cwe_3='LN')
        obx.obx_5 = (
            'FINAL DIAGNOSIS:\\.br\\\\.br\\Gallbladder, cholecystectomy:\\.br\\- Chronic cholecystitis with cholelithiasis\\.br\\- No evidence of dysplasia o'
            'r malignancy\\.br\\\\.br\\GROSS DESCRIPTION:\\.br\\Received in formalin is a gallbladder measuring 8.5 x 3.2 x 2.8 cm\\.br\\containing multiple '
            'faceted yellow-green gallstones ranging from 0.3-1.2 cm.'
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
    """ Based on live/nl/nl-epic.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='AMC')
        msh.receiving_application = HD(hd_1='SCHED')
        msh.receiving_facility = HD(hd_1='AMC')
        msh.date_time_of_message = '20230501143000+0200'
        msh.message_type = MSG(msg_1='SIU', msg_2='S15', msg_3='SIU_S15')
        msh.message_control_id = 'CANC20230501001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'NLD'
        msh.principal_language_of_message = CWE(cwe_1='8859/1')

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='APT55001', ei_2='EPIC')
        sch.filler_appointment_id = EI(ei_1='APT55001', ei_2='SCHED')
        sch.appointment_reason = CWE(cwe_1='ROUTINE', cwe_2='Routine', cwe_3='HL70277')
        sch.appointment_type = CWE(cwe_1='CONSULT', cwe_2='Consultation', cwe_3='LOCAL')
        sch.sch_9 = '20'
        sch.appointment_duration_units = CNE(cne_1='MIN')
        sch.sch_11 = '^^20^202305081000^202305081020'
        sch.filler_contact_person = XCN(xcn_1='67890123', xcn_2='Smit', xcn_3='Dirk', xcn_6='MD')
        sch.filler_contact_phone_number = XTN(xtn_2='WPN', xtn_3='PH', xtn_8='020-5559876')
        sch.filler_contact_address = XAD(xad_1='POLI KNO', xad_2='AMC')
        sch.entered_by_person = XCN(xcn_1='Cancelled')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='4567890', cx_5='PI'), CX(cx_1='999944567', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='de Jong', xpn_2='Willem', xpn_3='R', xpn_7='L')
        pid.date_time_of_birth = '19830225'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Herengracht 500', xad_3='Amsterdam', xad_5='1017CB', xad_6='NL', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='POLI KNO', pl_2='305', pl_3='B', pl_4='AMC')
        pv1.attending_doctor = XCN(xcn_1='67890123', xcn_2='Smit', xcn_3='Dirk', xcn_6='MD')

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
        ais.universal_service_identifier = CWE(cwe_1='CONSULT_KNO', cwe_2='ENT Consultation', cwe_3='LOCAL')
        ais.start_date_time_offset_units = CNE(cne_1='202305081000')
        ais.duration = '0'
        ais.duration_units = CNE(cne_1='MIN')
        ais.allow_substitution_code = CWE(cwe_1='20')
        ais.filler_status_code = CWE(cwe_1='MIN')

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
    """ Based on live/nl/nl-epic.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPIC')
        msh.sending_facility = HD(hd_1='AMSTERDAM_UMC')
        msh.receiving_application = HD(hd_1='MPI')
        msh.receiving_facility = HD(hd_1='AMSTERDAM_UMC')
        msh.date_time_of_message = '20240112100000+0100'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'UPD20240112001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'NLD'
        msh.principal_language_of_message = CWE(cwe_1='8859/1')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20240112100000+0100'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='1234567890', cx_5='PI'), CX(cx_1='999955678', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Vermeer', xpn_2='Elisabeth', xpn_3='A', xpn_7='L')
        pid.date_time_of_birth = '19680419'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = [
            XAD(xad_1='Vondelpark 12', xad_3='Amsterdam', xad_5='1071AA', xad_6='NL', xad_7='H'),
            XAD(xad_1='Postbus 999', xad_3='Amsterdam', xad_5='1000AZ', xad_6='NL', xad_7='M'),
        ]
        pid.pid_13 = '020-5551111^PRN^PH~06-12345678^PRN^CP'
        pid.primary_language = CWE(cwe_1='NLD', cwe_2='Dutch', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='M', cwe_2='Married', cwe_3='HL70002')
        pid.patient_account_number = CX(cx_1='ACCT240001', cx_4='AMSTERDAM_UMC', cx_5='AN')

        # .. build PD1 ..
        pd1 = PD1()
        pd1.pd1_4 = '87654321^Huisarts^Petra^^^^^^BIG^L^^^BIG'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='POLI INT', pl_2='501', pl_3='A', pl_4='AMSTERDAM_UMC')
        pv1.admission_type = CWE(cwe_1='R')
        pv1.attending_doctor = XCN(xcn_1='11223344', xcn_2='Dekker', xcn_3='Michiel', xcn_9='BIG')
        pv1.hospital_service = CWE(cwe_1='INT', cwe_2='Interne Geneeskunde', cwe_3='HL70069')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='11223344', xcn_2='Dekker', xcn_3='Michiel', xcn_9='BIG')
        pv1.patient_type = CWE(cwe_1='OP', cwe_2='Outpatient', cwe_3='HL70004')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Vermeer', xpn_2='Pieter', xpn_3='J')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Vondelpark 12', xad_3='Amsterdam', xad_5='1071AA', xad_6='NL')
        nk1.nk1_5 = '06-98765432^PRN^CP'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='CZ001', cwe_2='CZ')
        in1.insurance_company_id = CX(cx_1='CZ')
        in1.in1_4 = 'Postbus 900^^Tilburg^^5000AX^NL'
        in1.group_number = 'GRP456'
        in1.plan_type = CWE(cwe_1='20240101')
        in1.name_of_insured = XPN(xpn_1='20241231')
        in1.insureds_date_of_birth = 'SELF^Zelf^HL70063'
        in1.insureds_address = XAD(xad_1='Vermeer', xad_2='Elisabeth', xad_3='A')
        in1.assignment_of_benefits = CWE(cwe_1='SELF')
        in1.coordination_of_benefits = CWE(cwe_1='19680419')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.pv1 = pv1
        msg.extra_segments = [nk1, in1]

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
