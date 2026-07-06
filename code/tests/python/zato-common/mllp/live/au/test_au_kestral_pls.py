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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, DR, EI, HD, MSG, PL, PT, VID, XAD, XCN, XPN
from zato.hl7v2.v2_9.groups import DftP03Financial, DftP03Visit, OrmO01Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, \
    OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, RdeO11Order, RdeO11Patient, \
    RdeO11PatientVisit
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, DFT_P03, ORM_O01, ORU_R01, RDE_O11
from zato.hl7v2.v2_9.segments import EVN, FT1, IN1, MSH, NK1, NTE, OBR, OBX, ORC, PID, PV1, PV2, RXD, RXE, RXO, RXR

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('au', 'au-kestral-pls.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/au/au-kestral-pls.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KESTRAL_PHARM')
        msh.sending_facility = HD(hd_1='ROYAL_MELBOURNE', hd_2='2220')
        msh.receiving_application = HD(hd_1='MEDCHART')
        msh.receiving_facility = HD(hd_1='ROYAL_MELBOURNE')
        msh.date_time_of_message = '20260415091200'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'KPL20260415091200001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.message_profile_identifier = EI(ei_1='AUS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN10234567', cx_4='ROYAL_MELBOURNE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='NGUYEN', xpn_2='TRANG', xpn_3='THI', xpn_5='MS')
        pid.date_time_of_birth = '19780314'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='14 Bourke Street', xad_3='Melbourne', xad_4='VIC', xad_5='3000', xad_6='AUS')
        pid.pid_13 = '0412345678'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='4EAST', pl_2='401', pl_3='A', pl_4='ROYAL_MELBOURNE')
        pv1.attending_doctor = XCN(xcn_1='38291', xcn_2='PATEL', xcn_3='ANISH', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='38291', xcn_2='PATEL', xcn_3='ANISH', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.admit_date_time = '20260414083000'

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
        orc.placer_order_number = EI(ei_1='ORD2026041500123')
        orc.filler_order_number = EI(ei_1='KPL2026041500123')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260415091200'
        orc.orc_10 = 'KPHARM01^CHEN^LILY^^^PHARM'
        orc.orc_12 = '38291^PATEL^ANISH^^^DR'
        orc.enterers_location = PL(pl_1='4EAST')
        orc.order_control_code_reason = CWE(cwe_1='20260415091200')
        orc.orc_18 = 'ROYAL_MELBOURNE^2220'
        orc.orc_23 = 'ROYAL_MELBOURNE'

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='AMX500', cwe_2='Amoxicillin 500mg capsule', cwe_3='MIMS')
        rxo.requested_give_amount_minimum = '500'
        rxo.requested_give_units = CWE(cwe_1='mg')
        rxo.requested_dosage_form = CWE(cwe_1='CAP', cwe_2='Capsule', cwe_3='HL70292')
        rxo.requested_dispense_amount = '1'
        rxo.number_of_refills = '38291^PATEL^ANISH^^^DR'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='PO', cwe_2='Oral', cwe_3='HL70162')

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '^^^20260415120000^^R'
        rxe.give_code = CWE(cwe_1='AMX500', cwe_2='Amoxicillin 500mg capsule', cwe_3='MIMS')
        rxe.give_amount_minimum = '500'
        rxe.give_units = CWE(cwe_1='mg')
        rxe.give_dosage_form = CWE(cwe_1='CAP', cwe_2='Capsule', cwe_3='HL70292')
        rxe.providers_administration_instructions = CWE(cwe_1='E8H', cwe_2='Every 8 hours', cwe_3='KFREQ')
        rxe.ordering_providers_dea_number = XCN(xcn_1='21')
        rxe.pharmacist_treatment_suppliers_verifier_id = XCN(xcn_1='CAP', xcn_2='Capsule', xcn_3='HL70292')
        rxe.dispense_package_size = '7^days'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [rxo, rxr, rxe]

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
    """ Based on live/au/au-kestral-pls.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KESTRAL')
        msh.sending_facility = HD(hd_1='WESTMEAD', hd_2='2145')
        msh.receiving_application = HD(hd_1='CERNER')
        msh.receiving_facility = HD(hd_1='WESTMEAD')
        msh.date_time_of_message = '20260416140530'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'KPL20260416140530042'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.message_profile_identifier = EI(ei_1='AUS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='URN88234561', cx_4='WESTMEAD', cx_5='MR')
        pid.patient_name = XPN(xpn_1='SMITH', xpn_2='JAMES', xpn_3='ROBERT', xpn_5='MR')
        pid.date_time_of_birth = '19650822'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='27 Parramatta Road', xad_3='Westmead', xad_4='NSW', xad_5='2145', xad_6='AUS')
        pid.pid_13 = '0298901234'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HAEM', pl_2='302', pl_3='B', pl_4='WESTMEAD')
        pv1.attending_doctor = XCN(xcn_1='44210', xcn_2='RUSSO', xcn_3='MARIA', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='44210', xcn_2='RUSSO', xcn_3='MARIA', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.admit_date_time = '20260415190000'

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
        orc.placer_order_number = EI(ei_1='ORD2026041600987')
        orc.filler_order_number = EI(ei_1='KPL2026041600987')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260416140530'
        orc.orc_12 = '44210^RUSSO^MARIA^^^DR'
        orc.order_control_code_reason = CWE(cwe_1='20260416140530')
        orc.orc_18 = 'WESTMEAD^2145'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026041600987')
        obr.filler_order_number = EI(ei_1='KPL2026041600987')
        obr.universal_service_identifier = CWE(cwe_1='FBC', cwe_2='Full Blood Count', cwe_3='KCODE')
        obr.observation_date_time = '20260416060000'
        obr.obr_16 = '44210^RUSSO^MARIA^^^DR'
        obr.results_rpt_status_chng_date_time = '20260416140530'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='WBC', cwe_2='White Cell Count', cwe_3='KCODE')
        obx.obx_5 = '7.2'
        obx.units = CWE(cwe_1='x10*9/L')
        obx.reference_range = '4.0-11.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260416140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='RBC', cwe_2='Red Cell Count', cwe_3='KCODE')
        obx_2.obx_5 = '4.85'
        obx_2.units = CWE(cwe_1='x10*12/L')
        obx_2.reference_range = '4.50-6.50'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260416140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='HGB', cwe_2='Haemoglobin', cwe_3='KCODE')
        obx_3.obx_5 = '148'
        obx_3.units = CWE(cwe_1='g/L')
        obx_3.reference_range = '130-180'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260416140000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='HCT', cwe_2='Haematocrit', cwe_3='KCODE')
        obx_4.obx_5 = '0.44'
        obx_4.units = CWE(cwe_1='L/L')
        obx_4.reference_range = '0.40-0.54'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260416140000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='PLT', cwe_2='Platelet Count', cwe_3='KCODE')
        obx_5.obx_5 = '223'
        obx_5.units = CWE(cwe_1='x10*9/L')
        obx_5.reference_range = '150-400'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260416140000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='MCV', cwe_2='Mean Cell Volume', cwe_3='KCODE')
        obx_6.obx_5 = '90.7'
        obx_6.units = CWE(cwe_1='fL')
        obx_6.reference_range = '80.0-100.0'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260416140000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

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
    """ Based on live/au/au-kestral-pls.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KESTRAL_PHARM')
        msh.sending_facility = HD(hd_1='PRINCESS_ALEXANDRA', hd_2='3102')
        msh.receiving_application = HD(hd_1='MEDCHART')
        msh.receiving_facility = HD(hd_1='PRINCESS_ALEXANDRA')
        msh.date_time_of_message = '20260417083045'
        msh.message_type = MSG(msg_1='RDE', msg_2='O11', msg_3='RDE_O11')
        msh.message_control_id = 'KPL20260417083045003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.message_profile_identifier = EI(ei_1='AUS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN30298745', cx_4='PRINCESS_ALEXANDRA', cx_5='MR')
        pid.patient_name = XPN(xpn_1='WONG', xpn_2='MEI', xpn_3='LIN', xpn_5='MRS')
        pid.date_time_of_birth = '19520611'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='88 Ipswich Road', xad_3='Woolloongabba', xad_4='QLD', xad_5='4102', xad_6='AUS')
        pid.pid_13 = '0733456789'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='6SOUTH', pl_2='612', pl_3='A', pl_4='PRINCESS_ALEXANDRA')
        pv1.attending_doctor = XCN(xcn_1='51023', xcn_2='MURPHY', xcn_3='BRENDAN', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='51023', xcn_2='MURPHY', xcn_3='BRENDAN', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.admit_date_time = '20260416100000'

        # .. build the PATIENT_VISIT group ..
        patient_visit = RdeO11PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = RdeO11Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD2026041700456')
        orc.filler_order_number = EI(ei_1='KPL2026041700456')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260417083045'
        orc.orc_10 = 'KPHARM03^HALL^SARAH^^^PHARM'
        orc.orc_12 = '51023^MURPHY^BRENDAN^^^DR'
        orc.enterers_location = PL(pl_1='6SOUTH')
        orc.order_control_code_reason = CWE(cwe_1='20260417083045')
        orc.orc_18 = 'PRINCESS_ALEXANDRA^3102'

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '^^^20260417090000^^R'
        rxe.give_code = CWE(cwe_1='MET500', cwe_2='Metformin 500mg tablet', cwe_3='MIMS')
        rxe.give_amount_minimum = '500'
        rxe.give_units = CWE(cwe_1='mg')
        rxe.give_dosage_form = CWE(cwe_1='TAB', cwe_2='Tablet', cwe_3='HL70292')
        rxe.providers_administration_instructions = CWE(cwe_1='BD', cwe_2='Twice daily', cwe_3='KFREQ')
        rxe.ordering_providers_dea_number = XCN(xcn_1='60')
        rxe.pharmacist_treatment_suppliers_verifier_id = XCN(xcn_1='TAB', xcn_2='Tablet', xcn_3='HL70292')
        rxe.dispense_package_size = '30^days'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='PO', cwe_2='Oral', cwe_3='HL70162')

        # .. build the ORDER group ..
        order = RdeO11Order()
        order.orc = orc
        order.rxe = rxe
        order.rxr = rxr

        # .. build RXD ..
        rxd = RXD()
        rxd.dispense_sub_id_counter = '1'
        rxd.dispense_give_code = CWE(cwe_1='MET500', cwe_2='Metformin 500mg tablet', cwe_3='MIMS')
        rxd.date_time_dispensed = '20260417083045'
        rxd.actual_dispense_amount = '60'
        rxd.actual_dispense_units = CWE(cwe_1='TAB', cwe_2='Tablet', cwe_3='HL70292')
        rxd.substitution_status = 'KPL2026041700456'
        rxd.dispense_package_size = '30^days'

        # .. assemble the full message ..
        msg = RDE_O11()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [rxd]

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
    """ Based on live/au/au-kestral-pls.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KESTRAL_PLS')
        msh.sending_facility = HD(hd_1='RBWH', hd_2='4029')
        msh.receiving_application = HD(hd_1='HBCIS')
        msh.receiving_facility = HD(hd_1='RBWH')
        msh.date_time_of_message = '20260418071500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'KPL20260418071500010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.message_profile_identifier = EI(ei_1='AUS')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20260418071500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='URN44567890', cx_4='RBWH', cx_5='MR')
        pid.patient_name = XPN(xpn_1="O'BRIEN", xpn_2='DECLAN', xpn_3='PATRICK', xpn_5='MR')
        pid.date_time_of_birth = '19880919'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='5 Gregory Terrace', xad_3='Fortitude Valley', xad_4='QLD', xad_5='4006', xad_6='AUS')
        pid.pid_13 = '0412987654'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='ICU03', pl_3='A', pl_4='RBWH')
        pv1.attending_doctor = XCN(xcn_1='62017', xcn_2='KAUR', xcn_3='PRIYA', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='SURG')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='62017', xcn_2='KAUR', xcn_3='PRIYA', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.visit_number = CX(cx_1='VN20260418001')
        pv1.pending_location = PL(pl_1='20260418071500')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='MULTI', cwe_2='Multiple Trauma', cwe_3='KCODE')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1="O'BRIEN", xpn_2='SIOBHAN', xpn_4='MRS')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse', cwe_3='HL70063')
        nk1.address = XAD(xad_1='5 Gregory Terrace', xad_3='Fortitude Valley', xad_4='QLD', xad_5='4006', xad_6='AUS')
        nk1.nk1_5 = '0412876543'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='BUPA', cwe_2='BUPA Health Insurance', cwe_3='KFUND')
        in1.insurance_company_id = CX(cx_1='BUPA001')
        in1.in1_38 = '44567890'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.extra_segments = [nk1, in1]

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
    """ Based on live/au/au-kestral-pls.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KESTRAL')
        msh.sending_facility = HD(hd_1='FLINDERS_MC', hd_2='5042')
        msh.receiving_application = HD(hd_1='OACIS')
        msh.receiving_facility = HD(hd_1='FLINDERS_MC')
        msh.date_time_of_message = '20260419103200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'KPL20260419103200077'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.message_profile_identifier = EI(ei_1='AUS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN77812345', cx_4='FLINDERS_MC', cx_5='MR')
        pid.patient_name = XPN(xpn_1='TAYLOR', xpn_2='EMMA', xpn_3='GRACE', xpn_5='MS')
        pid.date_time_of_birth = '19910205'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='210 South Road', xad_3='Morphett Vale', xad_4='SA', xad_5='5162', xad_6='AUS')
        pid.pid_13 = '0881234567'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PATH', pl_2='OUTPAT', pl_3='A', pl_4='FLINDERS_MC')
        pv1.attending_doctor = XCN(xcn_1='72345', xcn_2='JENKINS', xcn_3='SIMON', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='3')
        pv1.admitting_doctor = XCN(xcn_1='72345', xcn_2='JENKINS', xcn_3='SIMON', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.admit_date_time = '20260419090000'

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
        orc.placer_order_number = EI(ei_1='ORD2026041901234')
        orc.filler_order_number = EI(ei_1='KPL2026041901234')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260419103200'
        orc.orc_12 = '72345^JENKINS^SIMON^^^DR'
        orc.order_control_code_reason = CWE(cwe_1='20260419103200')
        orc.orc_18 = 'FLINDERS_MC^5042'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026041901234')
        obr.filler_order_number = EI(ei_1='KPL2026041901234')
        obr.universal_service_identifier = CWE(cwe_1='UE', cwe_2='Urea and Electrolytes', cwe_3='KCODE')
        obr.observation_date_time = '20260419091500'
        obr.obr_16 = '72345^JENKINS^SIMON^^^DR'
        obr.results_rpt_status_chng_date_time = '20260419103200'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='NA', cwe_2='Sodium', cwe_3='KCODE')
        obx.obx_5 = '139'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '135-145'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260419100000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='K', cwe_2='Potassium', cwe_3='KCODE')
        obx_2.obx_5 = '4.1'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '3.5-5.2'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260419100000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='CL', cwe_2='Chloride', cwe_3='KCODE')
        obx_3.obx_5 = '102'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '95-110'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260419100000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='HCO3', cwe_2='Bicarbonate', cwe_3='KCODE')
        obx_4.obx_5 = '24'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '22-32'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260419100000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='UREA', cwe_2='Urea', cwe_3='KCODE')
        obx_5.obx_5 = '5.8'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '2.5-8.0'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260419100000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='CREAT', cwe_2='Creatinine', cwe_3='KCODE')
        obx_6.obx_5 = '72'
        obx_6.units = CWE(cwe_1='umol/L')
        obx_6.reference_range = '45-90'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260419100000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='EGFR', cwe_2='eGFR', cwe_3='KCODE')
        obx_7.obx_5 = '>90'
        obx_7.units = CWE(cwe_1='mL/min/1.73m2')
        obx_7.reference_range = '>60'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20260419100000'

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
    """ Based on live/au/au-kestral-pls.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KESTRAL')
        msh.sending_facility = HD(hd_1='AUSTIN_HEALTH', hd_2='3084')
        msh.receiving_application = HD(hd_1='AUSLAB')
        msh.receiving_facility = HD(hd_1='AUSTIN_HEALTH')
        msh.date_time_of_message = '20260420154500'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'KPL20260420154500088'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.message_profile_identifier = EI(ei_1='AUS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='URN55678901', cx_4='AUSTIN_HEALTH', cx_5='MR')
        pid.patient_name = XPN(xpn_1='PHAM', xpn_2='QUOC', xpn_3='VINH', xpn_5='MR')
        pid.date_time_of_birth = '19730428'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='33 Burgundy Street', xad_3='Heidelberg', xad_4='VIC', xad_5='3084', xad_6='AUS')
        pid.pid_13 = '0394567890'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='7NORTH', pl_2='715', pl_3='B', pl_4='AUSTIN_HEALTH')
        pv1.attending_doctor = XCN(xcn_1='82910', xcn_2='CHANG', xcn_3='DAVID', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='GAS')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='82910', xcn_2='CHANG', xcn_3='DAVID', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.admit_date_time = '20260419163000'

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
        orc.placer_order_number = EI(ei_1='ORD2026042001567')
        orc.filler_order_number = EI(ei_1='KPL2026042001567')
        orc.order_status = 'SC'
        orc.date_time_of_order_event = '20260420154500'
        orc.orc_12 = '82910^CHANG^DAVID^^^DR'
        orc.enterers_location = PL(pl_1='7NORTH')
        orc.order_control_code_reason = CWE(cwe_1='20260420154500')
        orc.orc_18 = 'AUSTIN_HEALTH^3084'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026042001567')
        obr.filler_order_number = EI(ei_1='KPL2026042001567')
        obr.universal_service_identifier = CWE(cwe_1='LFT', cwe_2='Liver Function Tests', cwe_3='KCODE')
        obr.observation_date_time = '20260420154500'
        obr.obr_16 = '82910^CHANG^DAVID^^^DR'
        obr.transportation_mode = 'STAT^Urgent^HL70078'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Pre-operative bloods for laparoscopic cholecystectomy scheduled 21/04/2026'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.nte = nte

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
    """ Based on live/au/au-kestral-pls.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KESTRAL')
        msh.sending_facility = HD(hd_1='ROYAL_HOBART', hd_2='7000')
        msh.receiving_application = HD(hd_1='CERNER')
        msh.receiving_facility = HD(hd_1='ROYAL_HOBART')
        msh.date_time_of_message = '20260421112000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'KPL20260421112000055'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.message_profile_identifier = EI(ei_1='AUS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN66234578', cx_4='ROYAL_HOBART', cx_5='MR')
        pid.patient_name = XPN(xpn_1='FITZGERALD', xpn_2='NIAMH', xpn_3='ROSE', xpn_5='MS')
        pid.date_time_of_birth = '20010716'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='42 Liverpool Street', xad_3='Hobart', xad_4='TAS', xad_5='7000', xad_6='AUS')
        pid.pid_13 = '0362345678'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3WEST', pl_2='308', pl_3='A', pl_4='ROYAL_HOBART')
        pv1.attending_doctor = XCN(xcn_1='91456', xcn_2='DASGUPTA', xcn_3='ARUN', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='91456', xcn_2='DASGUPTA', xcn_3='ARUN', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.admit_date_time = '20260420083000'

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
        orc.placer_order_number = EI(ei_1='ORD2026042101890')
        orc.filler_order_number = EI(ei_1='KPL2026042101890')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260421112000'
        orc.orc_12 = '91456^DASGUPTA^ARUN^^^DR'
        orc.order_control_code_reason = CWE(cwe_1='20260421112000')
        orc.orc_18 = 'ROYAL_HOBART^7000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026042101890')
        obr.filler_order_number = EI(ei_1='KPL2026042101890')
        obr.universal_service_identifier = CWE(cwe_1='UCAS', cwe_2='Urine Culture and Sensitivity', cwe_3='KCODE')
        obr.observation_date_time = '20260420150000'
        obr.obr_16 = '91456^DASGUPTA^ARUN^^^DR'
        obr.results_rpt_status_chng_date_time = '20260421112000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='ORGANISM', cwe_2='Organism Identified', cwe_3='KCODE')
        obx.obx_5 = 'ECOLI^Escherichia coli^KORG'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260421100000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='COLCOUNT', cwe_2='Colony Count', cwe_3='KCODE')
        obx_2.obx_5 = '>100000'
        obx_2.units = CWE(cwe_1='CFU/mL')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260421100000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='AMPICILLIN', cwe_2='Ampicillin', cwe_3='KCODE')
        obx_3.obx_5 = 'S'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260421100000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='CEPHALEXIN', cwe_2='Cephalexin', cwe_3='KCODE')
        obx_4.obx_5 = 'S'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260421100000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='TRIMETHOPRIM', cwe_2='Trimethoprim', cwe_3='KCODE')
        obx_5.obx_5 = 'R'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20260421100000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='NITROFURANTOIN', cwe_2='Nitrofurantoin', cwe_3='KCODE')
        obx_6.obx_5 = 'S'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20260421100000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='CIPROFLOXACIN', cwe_2='Ciprofloxacin', cwe_3='KCODE')
        obx_7.obx_5 = 'S'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20260421100000'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Significant growth of E. coli. Trimethoprim resistant.'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7
        observation_7.nte = nte

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
    """ Based on live/au/au-kestral-pls.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KESTRAL_PHARM')
        msh.sending_facility = HD(hd_1='JOHN_HUNTER', hd_2='2305')
        msh.receiving_application = HD(hd_1='ORACLE_FIN')
        msh.receiving_facility = HD(hd_1='JOHN_HUNTER')
        msh.date_time_of_message = '20260422093000'
        msh.message_type = MSG(msg_1='DFT', msg_2='P03', msg_3='DFT_P03')
        msh.message_control_id = 'KPL20260422093000012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.message_profile_identifier = EI(ei_1='AUS')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'P03'
        evn.recorded_date_time = '20260422093000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='URN99345678', cx_4='JOHN_HUNTER', cx_5='MR')
        pid.patient_name = XPN(xpn_1='KELLY', xpn_2='SEAN', xpn_3='MICHAEL', xpn_5='MR')
        pid.date_time_of_birth = '19560730'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='18 Hunter Street', xad_3='Newcastle', xad_4='NSW', xad_5='2300', xad_6='AUS')
        pid.pid_13 = '0249876543'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='405', pl_3='A', pl_4='JOHN_HUNTER')
        pv1.attending_doctor = XCN(xcn_1='10345', xcn_2='MORGAN', xcn_3='FIONA', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='CARD')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='10345', xcn_2='MORGAN', xcn_3='FIONA', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.admit_date_time = '20260421120000'

        # .. build the VISIT group ..
        visit = DftP03Visit()
        visit.pv1 = pv1

        # .. build FT1 ..
        ft1 = FT1()
        ft1.set_id_ft1 = '1'
        ft1.transaction_id = CX(cx_1='20260422093000')
        ft1.transaction_batch_id = '20260422093000'
        ft1.transaction_date = DR(dr_1='CG')
        ft1.transaction_posting_date = 'D'
        ft1.transaction_type = CWE(cwe_1='ATORV40', cwe_2='Atorvastatin 40mg tablet', cwe_3='MIMS')
        ft1.transaction_code = CWE(cwe_1='1.00')
        ft1.transaction_quantity = 'KPHARM02^BROOKS^DANIEL^^^PHARM'
        ft1.assigned_patient_location = PL(pl_1='30')
        ft1.fee_schedule = CWE(cwe_1='TAB', cwe_2='Tablet', cwe_3='HL70292')
        ft1.performed_by_code = XCN(xcn_1='10345', xcn_2='MORGAN', xcn_3='FIONA', xcn_6='DR')
        ft1.procedure_code = CNE(cne_1='ATORV40', cne_2='Atorvastatin 40mg tablet', cne_3='MIMS')

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
    """ Based on live/au/au-kestral-pls.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KESTRAL_PLS')
        msh.sending_facility = HD(hd_1='ROYAL_PERTH', hd_2='6000')
        msh.receiving_application = HD(hd_1='WEBPAS')
        msh.receiving_facility = HD(hd_1='ROYAL_PERTH')
        msh.date_time_of_message = '20260423161500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'KPL20260423161500022'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.message_profile_identifier = EI(ei_1='AUS')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20260423161500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN12890456', cx_4='ROYAL_PERTH', cx_5='MR')
        pid.patient_name = XPN(xpn_1='MORRISON', xpn_2='CLAIRE', xpn_3='ANNE', xpn_5='MRS')
        pid.date_time_of_birth = '19680212'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='77 Hay Street', xad_3='Perth', xad_4='WA', xad_5='6000', xad_6='AUS')
        pid.pid_13 = '0892345678'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ORTHO', pl_2='502', pl_3='B', pl_4='ROYAL_PERTH')
        pv1.attending_doctor = XCN(xcn_1='20178', xcn_2='GRANT', xcn_3='LACHLAN', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='ORTH')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='20178', xcn_2='GRANT', xcn_3='LACHLAN', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.admit_date_time = '20260420090000'
        pv1.total_charges = '20260423161500'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='THR', cwe_2='Total Hip Replacement', cwe_3='KCODE')

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
    """ Based on live/au/au-kestral-pls.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KESTRAL')
        msh.sending_facility = HD(hd_1='MONASH_MC', hd_2='3168')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='MONASH_MC')
        msh.date_time_of_message = '20260424082500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'KPL20260424082500033'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.message_profile_identifier = EI(ei_1='AUS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='URN22456789', cx_4='MONASH_MC', cx_5='MR')
        pid.patient_name = XPN(xpn_1='KUMAR', xpn_2='RAHUL', xpn_3='VIJAY', xpn_5='MR')
        pid.date_time_of_birth = '19830917'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='56 Dandenong Road', xad_3='Clayton', xad_4='VIC', xad_5='3168', xad_6='AUS')
        pid.pid_13 = '0395678901'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HAEM', pl_2='204', pl_3='A', pl_4='MONASH_MC')
        pv1.attending_doctor = XCN(xcn_1='33210', xcn_2='WILSON', xcn_3='KATHLEEN', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='33210', xcn_2='WILSON', xcn_3='KATHLEEN', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.admit_date_time = '20260423143000'

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
        orc.placer_order_number = EI(ei_1='ORD2026042402345')
        orc.filler_order_number = EI(ei_1='KPL2026042402345')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260424082500'
        orc.orc_12 = '33210^WILSON^KATHLEEN^^^DR'
        orc.order_control_code_reason = CWE(cwe_1='20260424082500')
        orc.orc_18 = 'MONASH_MC^3168'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026042402345')
        obr.filler_order_number = EI(ei_1='KPL2026042402345')
        obr.universal_service_identifier = CWE(cwe_1='COAG', cwe_2='Coagulation Studies', cwe_3='KCODE')
        obr.observation_date_time = '20260424060000'
        obr.obr_16 = '33210^WILSON^KATHLEEN^^^DR'
        obr.results_rpt_status_chng_date_time = '20260424082500'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='PT', cwe_2='Prothrombin Time', cwe_3='KCODE')
        obx.obx_5 = '13.2'
        obx.units = CWE(cwe_1='seconds')
        obx.reference_range = '11.0-15.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260424080000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='INR', cwe_2='International Normalised Ratio', cwe_3='KCODE')
        obx_2.obx_5 = '1.1'
        obx_2.reference_range = '0.9-1.3'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260424080000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='APTT', cwe_2='Activated Partial Thromboplastin Time', cwe_3='KCODE')
        obx_3.obx_5 = '32'
        obx_3.units = CWE(cwe_1='seconds')
        obx_3.reference_range = '25-38'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260424080000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='FIB', cwe_2='Fibrinogen', cwe_3='KCODE')
        obx_4.obx_5 = '3.2'
        obx_4.units = CWE(cwe_1='g/L')
        obx_4.reference_range = '1.5-4.0'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260424080000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ED'
        obx_5.observation_identifier = CWE(cwe_1='PDF', cwe_2='Coagulation Report', cwe_3='LN')
        obx_5.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMg'
            'MCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5'
            'IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo='
        )
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
    """ Based on live/au/au-kestral-pls.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KESTRAL_PHARM')
        msh.sending_facility = HD(hd_1='CANBERRA_HOSP', hd_2='2605')
        msh.receiving_application = HD(hd_1='MEDCHART')
        msh.receiving_facility = HD(hd_1='CANBERRA_HOSP')
        msh.date_time_of_message = '20260425101500'
        msh.message_type = MSG(msg_1='RDE', msg_2='O11', msg_3='RDE_O11')
        msh.message_control_id = 'KPL20260425101500007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.message_profile_identifier = EI(ei_1='AUS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN88901234', cx_4='CANBERRA_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='BAKER', xpn_2='THOMAS', xpn_3='WILLIAM', xpn_5='MR')
        pid.date_time_of_birth = '19450318'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='12 Commonwealth Avenue', xad_3='Barton', xad_4='ACT', xad_5='2600', xad_6='AUS')
        pid.pid_13 = '0262345678'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='310', pl_3='A', pl_4='CANBERRA_HOSP')
        pv1.attending_doctor = XCN(xcn_1='43567', xcn_2='CHEN', xcn_3='LILY', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='CARD')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='43567', xcn_2='CHEN', xcn_3='LILY', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.admit_date_time = '20260424070000'

        # .. build the PATIENT_VISIT group ..
        patient_visit = RdeO11PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = RdeO11Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD2026042500789')
        orc.filler_order_number = EI(ei_1='KPL2026042500789')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260425101500'
        orc.orc_10 = 'KPHARM04^AHMED^YUSUF^^^PHARM'
        orc.orc_12 = '43567^CHEN^LILY^^^DR'
        orc.enterers_location = PL(pl_1='CARD')
        orc.order_control_code_reason = CWE(cwe_1='20260425101500')
        orc.orc_18 = 'CANBERRA_HOSP^2605'

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '^^^20260425180000^^R'
        rxe.give_code = CWE(cwe_1='WARF5', cwe_2='Warfarin 5mg tablet', cwe_3='MIMS')
        rxe.give_amount_minimum = '5'
        rxe.give_units = CWE(cwe_1='mg')
        rxe.give_dosage_form = CWE(cwe_1='TAB', cwe_2='Tablet', cwe_3='HL70292')
        rxe.providers_administration_instructions = CWE(cwe_1='OD', cwe_2='Once daily', cwe_3='KFREQ')
        rxe.ordering_providers_dea_number = XCN(xcn_1='14')
        rxe.pharmacist_treatment_suppliers_verifier_id = XCN(xcn_1='TAB', xcn_2='Tablet', xcn_3='HL70292')
        rxe.dispense_package_size = '14^days'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='PO', cwe_2='Oral', cwe_3='HL70162')

        # .. build the ORDER group ..
        order = RdeO11Order()
        order.orc = orc
        order.rxe = rxe
        order.rxr = rxr

        # .. build RXD ..
        rxd = RXD()
        rxd.dispense_sub_id_counter = '1'
        rxd.dispense_give_code = CWE(cwe_1='WARF5', cwe_2='Warfarin 5mg tablet', cwe_3='MIMS')
        rxd.date_time_dispensed = '20260425101500'
        rxd.actual_dispense_amount = '14'
        rxd.actual_dispense_units = CWE(cwe_1='TAB', cwe_2='Tablet', cwe_3='HL70292')
        rxd.substitution_status = 'KPL2026042500789'
        rxd.dispense_package_size = '14^days'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Target INR 2.0-3.0. Next INR due 28/04/2026.'

        # .. assemble the full message ..
        msg = RDE_O11()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [rxd, nte]

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
    """ Based on live/au/au-kestral-pls.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KESTRAL_PHARM')
        msh.sending_facility = HD(hd_1='ROYAL_ADELAIDE', hd_2='5000')
        msh.receiving_application = HD(hd_1='MEDCHART')
        msh.receiving_facility = HD(hd_1='ROYAL_ADELAIDE')
        msh.date_time_of_message = '20260426071200'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'KPL20260426071200004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.message_profile_identifier = EI(ei_1='AUS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='URN33567812', cx_4='ROYAL_ADELAIDE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='CAMPBELL', xpn_2='FIONA', xpn_3='JEAN', xpn_5='MRS')
        pid.date_time_of_birth = '19770525'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='8 King William Street', xad_3='Adelaide', xad_4='SA', xad_5='5000', xad_6='AUS')
        pid.pid_13 = '0881234890'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SURG', pl_2='210', pl_3='A', pl_4='ROYAL_ADELAIDE')
        pv1.attending_doctor = XCN(xcn_1='55678', xcn_2='RAO', xcn_3='VIKRAM', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='SURG')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='55678', xcn_2='RAO', xcn_3='VIKRAM', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.admit_date_time = '20260425120000'

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
        orc.placer_order_number = EI(ei_1='ORD2026042601234')
        orc.filler_order_number = EI(ei_1='KPL2026042601234')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260426071200'
        orc.orc_10 = 'KPHARM05^LEE^JENNY^^^PHARM'
        orc.orc_12 = '55678^RAO^VIKRAM^^^DR'
        orc.enterers_location = PL(pl_1='SURG')
        orc.order_control_code_reason = CWE(cwe_1='20260426071200')
        orc.orc_18 = 'ROYAL_ADELAIDE^5000'

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc

        # .. build RXO ..
        rxo = RXO()
        rxo.requested_give_code = CWE(cwe_1='ENOX40', cwe_2='Enoxaparin 40mg/0.4mL syringe', cwe_3='MIMS')
        rxo.requested_give_amount_minimum = '40'
        rxo.requested_give_units = CWE(cwe_1='mg')
        rxo.requested_dosage_form = CWE(cwe_1='INJ', cwe_2='Injection', cwe_3='HL70292')
        rxo.requested_dispense_amount = '1'
        rxo.number_of_refills = '55678^RAO^VIKRAM^^^DR'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='SC', cwe_2='Subcutaneous', cwe_3='HL70162')
        rxr.administration_site = CWE(cwe_1='ABD', cwe_2='Abdomen', cwe_3='HL70163')

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '^^^20260426080000^^R'
        rxe.give_code = CWE(cwe_1='ENOX40', cwe_2='Enoxaparin 40mg/0.4mL syringe', cwe_3='MIMS')
        rxe.give_amount_minimum = '40'
        rxe.give_units = CWE(cwe_1='mg')
        rxe.give_dosage_form = CWE(cwe_1='INJ', cwe_2='Injection', cwe_3='HL70292')
        rxe.providers_administration_instructions = CWE(cwe_1='OD', cwe_2='Once daily', cwe_3='KFREQ')
        rxe.ordering_providers_dea_number = XCN(xcn_1='10')
        rxe.pharmacist_treatment_suppliers_verifier_id = XCN(xcn_1='INJ', xcn_2='Injection', xcn_3='HL70292')
        rxe.dispense_package_size = '10^days'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [rxo, rxr, rxe]

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
    """ Based on live/au/au-kestral-pls.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KESTRAL')
        msh.sending_facility = HD(hd_1='GOLD_COAST_UH', hd_2='4215')
        msh.receiving_application = HD(hd_1='CERNER')
        msh.receiving_facility = HD(hd_1='GOLD_COAST_UH')
        msh.date_time_of_message = '20260427093000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'KPL20260427093000066'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.message_profile_identifier = EI(ei_1='AUS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN44890123', cx_4='GOLD_COAST_UH', cx_5='MR')
        pid.patient_name = XPN(xpn_1='BROWN', xpn_2='SARAH', xpn_3='ELIZABETH', xpn_5='MRS')
        pid.date_time_of_birth = '19850411'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='92 Surfers Paradise Boulevard', xad_3='Surfers Paradise', xad_4='QLD', xad_5='4217', xad_6='AUS')
        pid.pid_13 = '0755678901'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PATH', pl_2='OUTPAT', pl_3='A', pl_4='GOLD_COAST_UH')
        pv1.attending_doctor = XCN(xcn_1='66789', xcn_2='ABRAHAMS', xcn_3='PETER', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='ENDO')
        pv1.admit_source = CWE(cwe_1='3')
        pv1.admitting_doctor = XCN(xcn_1='66789', xcn_2='ABRAHAMS', xcn_3='PETER', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.admit_date_time = '20260427080000'

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
        orc.placer_order_number = EI(ei_1='ORD2026042701567')
        orc.filler_order_number = EI(ei_1='KPL2026042701567')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260427093000'
        orc.orc_12 = '66789^ABRAHAMS^PETER^^^DR'
        orc.order_control_code_reason = CWE(cwe_1='20260427093000')
        orc.orc_18 = 'GOLD_COAST_UH^4215'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026042701567')
        obr.filler_order_number = EI(ei_1='KPL2026042701567')
        obr.universal_service_identifier = CWE(cwe_1='TFT', cwe_2='Thyroid Function Tests', cwe_3='KCODE')
        obr.observation_date_time = '20260427081500'
        obr.obr_16 = '66789^ABRAHAMS^PETER^^^DR'
        obr.results_rpt_status_chng_date_time = '20260427093000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='TSH', cwe_2='Thyroid Stimulating Hormone', cwe_3='KCODE')
        obx.obx_5 = '2.4'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.4-4.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260427090000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='FT4', cwe_2='Free Thyroxine', cwe_3='KCODE')
        obx_2.obx_5 = '14.8'
        obx_2.units = CWE(cwe_1='pmol/L')
        obx_2.reference_range = '10.0-20.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260427090000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='FT3', cwe_2='Free Triiodothyronine', cwe_3='KCODE')
        obx_3.obx_5 = '4.9'
        obx_3.units = CWE(cwe_1='pmol/L')
        obx_3.reference_range = '3.5-6.5'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260427090000'

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
    """ Based on live/au/au-kestral-pls.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KESTRAL_PLS')
        msh.sending_facility = HD(hd_1='ROYAL_DARWIN', hd_2='0800')
        msh.receiving_application = HD(hd_1='CARESYS')
        msh.receiving_facility = HD(hd_1='ROYAL_DARWIN')
        msh.date_time_of_message = '20260428140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'KPL20260428140000015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.message_profile_identifier = EI(ei_1='AUS')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20260428140000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='URN77456123', cx_4='ROYAL_DARWIN', cx_5='MR')
        pid.patient_name = XPN(xpn_1='GIBSON', xpn_2='MARK', xpn_3='ANTHONY', xpn_5='MR')
        pid.date_time_of_birth = '19920807'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='15 Mitchell Street', xad_3='Darwin', xad_4='NT', xad_5='0800', xad_6='AUS')
        pid.pid_13 = '0889012345'
        pid.marital_status = CWE(cwe_1='ATSI', cwe_2='Aboriginal', cwe_3='HL70005')
        pid.pid_28 = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED', pl_2='108', pl_3='A', pl_4='ROYAL_DARWIN')
        pv1.attending_doctor = XCN(xcn_1='77890', xcn_2='NGUYEN', xcn_3='TUAN', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='77890', xcn_2='NGUYEN', xcn_3='TUAN', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.admit_date_time = '20260427160000'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='GIBSON', xpn_2='KERRY', xpn_4='MS')
        nk1.relationship = CWE(cwe_1='MTH', cwe_2='Mother', cwe_3='HL70063')
        nk1.address = XAD(xad_1='15 Mitchell Street', xad_3='Darwin', xad_4='NT', xad_5='0800', xad_6='AUS')
        nk1.nk1_5 = '0889012346'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [nk1]

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
    """ Based on live/au/au-kestral-pls.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KESTRAL')
        msh.sending_facility = HD(hd_1='ROYAL_NORTH_SHORE', hd_2='2065')
        msh.receiving_application = HD(hd_1='SAP_FIN')
        msh.receiving_facility = HD(hd_1='ROYAL_NORTH_SHORE')
        msh.date_time_of_message = '20260429110000'
        msh.message_type = MSG(msg_1='DFT', msg_2='P03', msg_3='DFT_P03')
        msh.message_control_id = 'KPL20260429110000019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.message_profile_identifier = EI(ei_1='AUS')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'P03'
        evn.recorded_date_time = '20260429110000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN56234890', cx_4='ROYAL_NORTH_SHORE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='CHEN', xpn_2='XIAO', xpn_3='WEI', xpn_5='MR')
        pid.date_time_of_birth = '19700114'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='44 Pacific Highway', xad_3='St Leonards', xad_4='NSW', xad_5='2065', xad_6='AUS')
        pid.pid_13 = '0294567891'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PATH', pl_2='OUTPAT', pl_3='A', pl_4='ROYAL_NORTH_SHORE')
        pv1.attending_doctor = XCN(xcn_1='88123', xcn_2='PATEL', xcn_3='DEEPA', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='3')
        pv1.admitting_doctor = XCN(xcn_1='88123', xcn_2='PATEL', xcn_3='DEEPA', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.admit_date_time = '20260429083000'

        # .. build the VISIT group ..
        visit = DftP03Visit()
        visit.pv1 = pv1

        # .. build FT1 ..
        ft1 = FT1()
        ft1.set_id_ft1 = '1'
        ft1.transaction_id = CX(cx_1='20260429110000')
        ft1.transaction_batch_id = '20260429110000'
        ft1.transaction_date = DR(dr_1='CG')
        ft1.transaction_posting_date = 'D'
        ft1.transaction_type = CWE(cwe_1='FBC', cwe_2='Full Blood Count', cwe_3='KCODE')
        ft1.transaction_code = CWE(cwe_1='1.00')
        ft1.ft1_8 = '55.10'
        ft1.ft1_9 = 'AUD'
        ft1.patient_type = CWE(cwe_1='88123', cwe_2='PATEL', cwe_3='DEEPA', cwe_6='DR')
        ft1.filler_order_number = EI(ei_1='FBC', ei_2='Full Blood Count', ei_3='KCODE')

        # .. build the FINANCIAL group ..
        financial = DftP03Financial()
        financial.ft1 = ft1

        # .. build FT1 ..
        ft1_2 = FT1()
        ft1_2.set_id_ft1 = '2'
        ft1_2.transaction_id = CX(cx_1='20260429110000')
        ft1_2.transaction_batch_id = '20260429110000'
        ft1_2.transaction_date = DR(dr_1='CG')
        ft1_2.transaction_posting_date = 'D'
        ft1_2.transaction_type = CWE(cwe_1='UE', cwe_2='Urea and Electrolytes', cwe_3='KCODE')
        ft1_2.transaction_code = CWE(cwe_1='1.00')
        ft1_2.ft1_8 = '35.20'
        ft1_2.ft1_9 = 'AUD'
        ft1_2.patient_type = CWE(cwe_1='88123', cwe_2='PATEL', cwe_3='DEEPA', cwe_6='DR')
        ft1_2.filler_order_number = EI(ei_1='UE', ei_2='Urea and Electrolytes', ei_3='KCODE')

        # .. build the FINANCIAL group ..
        financial_2 = DftP03Financial()
        financial_2.ft1 = ft1_2

        # .. build FT1 ..
        ft1_3 = FT1()
        ft1_3.set_id_ft1 = '3'
        ft1_3.transaction_id = CX(cx_1='20260429110000')
        ft1_3.transaction_batch_id = '20260429110000'
        ft1_3.transaction_date = DR(dr_1='CG')
        ft1_3.transaction_posting_date = 'D'
        ft1_3.transaction_type = CWE(cwe_1='LFT', cwe_2='Liver Function Tests', cwe_3='KCODE')
        ft1_3.transaction_code = CWE(cwe_1='1.00')
        ft1_3.ft1_8 = '42.80'
        ft1_3.ft1_9 = 'AUD'
        ft1_3.patient_type = CWE(cwe_1='88123', cwe_2='PATEL', cwe_3='DEEPA', cwe_6='DR')
        ft1_3.filler_order_number = EI(ei_1='LFT', ei_2='Liver Function Tests', ei_3='KCODE')

        # .. build the FINANCIAL group ..
        financial_3 = DftP03Financial()
        financial_3.ft1 = ft1_3

        # .. assemble the full message ..
        msg = DFT_P03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.visit = visit
        msg.financial = [financial, financial_2, financial_3]

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
    """ Based on live/au/au-kestral-pls.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KESTRAL')
        msh.sending_facility = HD(hd_1='ALFRED_HOSP', hd_2='3004')
        msh.receiving_application = HD(hd_1='BLOODBANK')
        msh.receiving_facility = HD(hd_1='ALFRED_HOSP')
        msh.date_time_of_message = '20260430062000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'KPL20260430062000002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.message_profile_identifier = EI(ei_1='AUS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='URN88012345', cx_4='ALFRED_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='MARTINEZ', xpn_2='ISABELLA', xpn_3='ROSA', xpn_5='MS')
        pid.date_time_of_birth = '19960303'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='120 Commercial Road', xad_3='Prahran', xad_4='VIC', xad_5='3181', xad_6='AUS')
        pid.pid_13 = '0394567234'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_2='BED12', pl_3='A', pl_4='ALFRED_HOSP')
        pv1.attending_doctor = XCN(xcn_1='44321', xcn_2="O'CONNOR", xcn_3='PATRICK', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='EMERG')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='44321', xcn_2="O'CONNOR", xcn_3='PATRICK', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='EP')
        pv1.admit_date_time = '20260430055000'

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
        orc.placer_order_number = EI(ei_1='ORD2026043000345')
        orc.filler_order_number = EI(ei_1='KPL2026043000345')
        orc.order_status = 'SC'
        orc.date_time_of_order_event = '20260430062000'
        orc.orc_12 = "44321^O'CONNOR^PATRICK^^^DR"
        orc.enterers_location = PL(pl_1='ED')
        orc.order_control_code_reason = CWE(cwe_1='20260430062000')
        orc.orc_18 = 'ALFRED_HOSP^3004'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026043000345')
        obr.filler_order_number = EI(ei_1='KPL2026043000345')
        obr.universal_service_identifier = CWE(cwe_1='XM', cwe_2='Crossmatch', cwe_3='KCODE')
        obr.observation_date_time = '20260430062000'
        obr.obr_16 = "44321^O'CONNOR^PATRICK^^^DR"
        obr.transportation_mode = 'STAT^Urgent^HL70078'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Crossmatch 4 units packed red cells. Major trauma - MTP activated.'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='BLDGRP', cwe_2='Blood Group', cwe_3='KCODE')
        obx.obx_5 = 'O^O Positive^KBLD'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260430055500'

        # .. build the OBSERVATION group ..
        observation = OrmO01Observation()
        observation.obx = obx

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.nte = nte
        order_detail.observation = observation

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
    """ Based on live/au/au-kestral-pls.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KESTRAL')
        msh.sending_facility = HD(hd_1='MATER_HOSP', hd_2='4101')
        msh.receiving_application = HD(hd_1='CERNER')
        msh.receiving_facility = HD(hd_1='MATER_HOSP')
        msh.date_time_of_message = '20260501091000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'KPL20260501091000044'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.message_profile_identifier = EI(ei_1='AUS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN33678902', cx_4='MATER_HOSP', cx_5='MR')
        pid.patient_name = XPN(xpn_1='JOHNSON', xpn_2='AMY', xpn_3='LOUISE', xpn_5='MRS')
        pid.date_time_of_birth = '19890622'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='35 Stanley Street', xad_3='South Brisbane', xad_4='QLD', xad_5='4101', xad_6='AUS')
        pid.pid_13 = '0732456789'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PATH', pl_2='OUTPAT', pl_3='A', pl_4='MATER_HOSP')
        pv1.attending_doctor = XCN(xcn_1='55234', xcn_2='WILLIAMS', xcn_3='RUTH', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='OBS')
        pv1.admit_source = CWE(cwe_1='3')
        pv1.admitting_doctor = XCN(xcn_1='55234', xcn_2='WILLIAMS', xcn_3='RUTH', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='OP')
        pv1.admit_date_time = '20260501070000'

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
        orc.placer_order_number = EI(ei_1='ORD2026050101890')
        orc.filler_order_number = EI(ei_1='KPL2026050101890')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260501091000'
        orc.orc_12 = '55234^WILLIAMS^RUTH^^^DR'
        orc.order_control_code_reason = CWE(cwe_1='20260501091000')
        orc.orc_18 = 'MATER_HOSP^4101'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026050101890')
        obr.filler_order_number = EI(ei_1='KPL2026050101890')
        obr.universal_service_identifier = CWE(cwe_1='GTT', cwe_2='Glucose Tolerance Test', cwe_3='KCODE')
        obr.observation_date_time = '20260501071500'
        obr.obr_16 = '55234^WILLIAMS^RUTH^^^DR'
        obr.results_rpt_status_chng_date_time = '20260501091000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='GLUF', cwe_2='Fasting Glucose', cwe_3='KCODE')
        obx.obx_5 = '5.2'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '3.0-5.4'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260501073000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='GLU1H', cwe_2='Glucose 1 Hour', cwe_3='KCODE')
        obx_2.obx_5 = '10.8'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '<10.0'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260501083000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='GLU2H', cwe_2='Glucose 2 Hour', cwe_3='KCODE')
        obx_3.obx_5 = '8.9'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '<8.5'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260501093000'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Results consistent with gestational diabetes mellitus. Refer to endocrinology.'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3
        observation_3.nte = nte

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
    """ Based on live/au/au-kestral-pls.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KESTRAL_PHARM')
        msh.sending_facility = HD(hd_1='ROYAL_CHILDREN', hd_2='3052')
        msh.receiving_application = HD(hd_1='MEDCHART')
        msh.receiving_facility = HD(hd_1='ROYAL_CHILDREN')
        msh.date_time_of_message = '20260502143000'
        msh.message_type = MSG(msg_1='RDE', msg_2='O11', msg_3='RDE_O11')
        msh.message_control_id = 'KPL20260502143000009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.message_profile_identifier = EI(ei_1='AUS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='URN11234567', cx_4='ROYAL_CHILDREN', cx_5='MR')
        pid.patient_name = XPN(xpn_1='HARRIS', xpn_2='LIAM', xpn_3='JAMES', xpn_5='MASTER')
        pid.date_time_of_birth = '20180915'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='28 Flemington Road', xad_3='Parkville', xad_4='VIC', xad_5='3052', xad_6='AUS')
        pid.pid_13 = '0393456789'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='PAED', pl_2='402', pl_3='A', pl_4='ROYAL_CHILDREN')
        pv1.attending_doctor = XCN(xcn_1='99012', xcn_2='SINGH', xcn_3='NEHA', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='PAED')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='99012', xcn_2='SINGH', xcn_3='NEHA', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.admit_date_time = '20260501100000'

        # .. build the PATIENT_VISIT group ..
        patient_visit = RdeO11PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = RdeO11Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD2026050200567')
        orc.filler_order_number = EI(ei_1='KPL2026050200567')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260502143000'
        orc.orc_10 = 'KPHARM06^WRIGHT^EMMA^^^PHARM'
        orc.orc_12 = '99012^SINGH^NEHA^^^DR'
        orc.enterers_location = PL(pl_1='PAED')
        orc.order_control_code_reason = CWE(cwe_1='20260502143000')
        orc.orc_18 = 'ROYAL_CHILDREN^3052'

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '^^^20260502160000^^R'
        rxe.give_code = CWE(cwe_1='VANC500', cwe_2='Vancomycin 500mg injection', cwe_3='MIMS')
        rxe.give_amount_minimum = '500'
        rxe.give_units = CWE(cwe_1='mg')
        rxe.give_dosage_form = CWE(cwe_1='INJ', cwe_2='Injection', cwe_3='HL70292')
        rxe.providers_administration_instructions = CWE(cwe_1='Q12H', cwe_2='Every 12 hours', cwe_3='KFREQ')
        rxe.ordering_providers_dea_number = XCN(xcn_1='6')
        rxe.pharmacist_treatment_suppliers_verifier_id = XCN(xcn_1='VIAL', xcn_2='Vial', xcn_3='HL70292')
        rxe.dispense_package_size = '3^days'

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='IV', cwe_2='Intravenous', cwe_3='HL70162')

        # .. build the ORDER group ..
        order = RdeO11Order()
        order.orc = orc
        order.rxe = rxe
        order.rxr = rxr

        # .. build RXD ..
        rxd = RXD()
        rxd.dispense_sub_id_counter = '1'
        rxd.dispense_give_code = CWE(cwe_1='VANC500', cwe_2='Vancomycin 500mg injection', cwe_3='MIMS')
        rxd.date_time_dispensed = '20260502143000'
        rxd.actual_dispense_amount = '6'
        rxd.actual_dispense_units = CWE(cwe_1='VIAL', cwe_2='Vial', cwe_3='HL70292')
        rxd.substitution_status = 'KPL2026050200567'
        rxd.dispense_package_size = '3^days'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = 'Dilute in 250mL Normal Saline. Infuse over 60 minutes. Trough level due before 4th dose.'

        # .. assemble the full message ..
        msg = RDE_O11()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [rxd, nte]

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
    """ Based on live/au/au-kestral-pls.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KESTRAL')
        msh.sending_facility = HD(hd_1='PETER_MAC', hd_2='3000')
        msh.receiving_application = HD(hd_1='EPIC')
        msh.receiving_facility = HD(hd_1='PETER_MAC')
        msh.date_time_of_message = '20260503155000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'KPL20260503155000088'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.message_profile_identifier = EI(ei_1='AUS')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MRN99012345', cx_4='PETER_MAC', cx_5='MR')
        pid.patient_name = XPN(xpn_1='ANDERSON', xpn_2='ROBERT', xpn_3='JAMES', xpn_5='MR')
        pid.date_time_of_birth = '19570801'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='305 Grattan Street', xad_3='Melbourne', xad_4='VIC', xad_5='3000', xad_6='AUS')
        pid.pid_13 = '0396789012'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ONCO', pl_2='511', pl_3='A', pl_4='PETER_MAC')
        pv1.attending_doctor = XCN(xcn_1='22456', xcn_2='LEE', xcn_3='SANDRA', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='ONCO')
        pv1.admit_source = CWE(cwe_1='1')
        pv1.admitting_doctor = XCN(xcn_1='22456', xcn_2='LEE', xcn_3='SANDRA', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.admit_date_time = '20260502090000'

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
        orc.placer_order_number = EI(ei_1='ORD2026050302345')
        orc.filler_order_number = EI(ei_1='KPL2026050302345')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20260503155000'
        orc.orc_12 = '22456^LEE^SANDRA^^^DR'
        orc.order_control_code_reason = CWE(cwe_1='20260503155000')
        orc.orc_18 = 'PETER_MAC^3000'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2026050302345')
        obr.filler_order_number = EI(ei_1='KPL2026050302345')
        obr.universal_service_identifier = CWE(cwe_1='HISTO', cwe_2='Histopathology', cwe_3='KCODE')
        obr.observation_date_time = '20260501110000'
        obr.obr_16 = '22456^LEE^SANDRA^^^DR'
        obr.results_rpt_status_chng_date_time = '20260503155000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='MACRO', cwe_2='Macroscopic Description', cwe_3='KCODE')
        obx.obx_5 = 'Skin ellipse 32x18x12mm. Central pigmented lesion 14x11mm, irregular border, variegated colour.'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20260503140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='MICRO', cwe_2='Microscopic Description', cwe_3='KCODE')
        obx_2.obx_5 = (
            'Sections show a compound melanocytic naevus with architectural disorder and cytological atypia. Breslow thickness 0.6mm. No ulceration. Mito'
            'tic rate <1/mm2.'
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20260503140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='DIAG', cwe_2='Diagnosis', cwe_3='KCODE')
        obx_3.obx_5 = 'MEL^Malignant Melanoma in situ^KPATH'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20260503140000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='STAGE', cwe_2='Clark Level', cwe_3='KCODE')
        obx_4.obx_5 = 'II'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20260503140000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ED'
        obx_5.observation_identifier = CWE(cwe_1='PDF', cwe_2='Histopathology Report', cwe_3='LN')
        obx_5.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMg'
            'MCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5'
            'IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo='
        )
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
    """ Based on live/au/au-kestral-pls.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='KESTRAL_PLS')
        msh.sending_facility = HD(hd_1='ST_VINCENTS', hd_2='2010')
        msh.receiving_application = HD(hd_1='POWERCHART')
        msh.receiving_facility = HD(hd_1='ST_VINCENTS')
        msh.date_time_of_message = '20260504112000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'KPL20260504112000018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'ASCII'
        msh.message_profile_identifier = EI(ei_1='AUS')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20260504112000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='URN55789012', cx_4='ST_VINCENTS', cx_5='MR')
        pid.patient_name = XPN(xpn_1='DIMITRIOU', xpn_2='NIKOLAOS', xpn_3='ANDREAS', xpn_5='MR')
        pid.date_time_of_birth = '19810426'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='200 Victoria Street', xad_3='Darlinghurst', xad_4='NSW', xad_5='2010', xad_6='AUS')
        pid.pid_13 = '0293456789'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='ICU07', pl_3='A', pl_4='ST_VINCENTS')
        pv1.attending_doctor = XCN(xcn_1='33678', xcn_2='FLETCHER', xcn_3='ANDREW', xcn_6='DR')
        pv1.hospital_service = CWE(cwe_1='CARD')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='33678', xcn_2='FLETCHER', xcn_3='ANDREW', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.admit_date_time = '20260502180000'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='STEMI', cwe_2='ST Elevation MI', cwe_3='KCODE')

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.pv2 = pv2

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
