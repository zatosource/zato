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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, HD, MOC, MSG, OG, PL, PRL, PT, VID, XAD, XCN, XPN
from zato.hl7v2.v2_9.groups import OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A03, ORM_O01, ORU_R01
from zato.hl7v2.v2_9.segments import EVN, MSH, OBR, OBX, ORC, PID, PV1

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('au', 'au-citadel-auslab.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/au/au-citadel-auslab.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AUSLAB')
        msh.sending_facility = HD(hd_1='QLD_HEALTH_PATH', hd_2='2567', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='BEST_PRACTICE')
        msh.receiving_facility = HD(hd_1='WYNNUM_FAMILY_MC')
        msh.security = '20240315091200+1000'
        msh.message_control_id = 'ORU^R01'
        msh.processing_id = PT(pt_1='MSG00001')
        msh.version_id = VID(vid_1='P')
        msh.msh_13 = '2.4^AUS&&ISO3166_1^HL7AU.ONO.1&&HL7AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN5183942', cx_4='QLD_HEALTH', cx_5='MR'), CX(cx_1='4198273645', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='TRAN', xpn_2='MEI', xpn_7='L')
        pid.date_time_of_birth = '19850412'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='83 Bay Terrace', xad_3='WYNNUM', xad_4='QLD', xad_5='4178', xad_6='AUS', xad_7='C')
        pid.pid_13 = '0419283745'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='WYNNUM_FAMILY_MC', pl_4='QLD_HEALTH')
        pv1.attending_doctor = XCN(xcn_1='0381765T', xcn_2='WALKER', xcn_3='STEPHEN', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.referring_doctor = XCN(xcn_1='0381765T', xcn_2='WALKER', xcn_3='STEPHEN', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.patient_type = CWE(cwe_1='REF')
        pv1.prior_temporary_location = PL(pl_1='20240315')

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
        orc.filler_order_number = EI(ei_1='24-1001234-BNE-0', ei_2='QLD_HEALTH_PATH', ei_3='2567', ei_4='AUSNATA')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.filler_order_number = EI(ei_1='24-1001234-BNE-0', ei_2='QLD_HEALTH_PATH', ei_3='2567', ei_4='AUSNATA')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='FULL BLOOD COUNT', cwe_3='2567')
        obr.observation_date_time = '20240315083000+1000'
        obr.danger_code = CWE(cwe_1='Routine')
        obr.obr_14 = '20240315084500+1000'
        obr.obr_16 = '0381765T^WALKER^STEPHEN^^^DR^^^AUSHICPR^L^^^UPIN'
        obr.charge_to_practice = MOC(moc_1='20240315091200+1000')
        obr.parent_result = PRL(prl_1='F')
        obr.obr_33 = '0381765T^WALKER^STEPHEN'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Haemoglobin', cwe_3='LN')
        obx.obx_5 = '132'
        obx.units = CWE(cwe_1='g/L')
        obx.reference_range = '120-160'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240315091200+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erythrocytes', cwe_3='LN')
        obx_2.obx_5 = '4.35'
        obx_2.obx_6 = 'x10\\S\\12/L'
        obx_2.reference_range = '3.80-5.20'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240315091200+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Haematocrit', cwe_3='LN')
        obx_3.obx_5 = '0.39'
        obx_3.units = CWE(cwe_1='L/L')
        obx_3.reference_range = '0.36-0.46'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240315091200+1000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='787-2', cwe_2='Mean cell volume', cwe_3='LN')
        obx_4.obx_5 = '89.7'
        obx_4.units = CWE(cwe_1='fL')
        obx_4.reference_range = '80.0-100.0'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240315091200+1000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='785-6', cwe_2='Mean cell haemoglobin', cwe_3='LN')
        obx_5.obx_5 = '30.3'
        obx_5.units = CWE(cwe_1='pg')
        obx_5.reference_range = '27.0-33.0'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20240315091200+1000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='786-4', cwe_2='Mean cell haemoglobin concentration', cwe_3='LN')
        obx_6.obx_5 = '338'
        obx_6.units = CWE(cwe_1='g/L')
        obx_6.reference_range = '320-360'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20240315091200+1000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukocytes', cwe_3='LN')
        obx_7.obx_5 = '6.8'
        obx_7.obx_6 = 'x10\\S\\9/L'
        obx_7.reference_range = '4.0-11.0'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20240315091200+1000'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='777-3', cwe_2='Platelets', cwe_3='LN')
        obx_8.obx_5 = '245'
        obx_8.obx_6 = 'x10\\S\\9/L'
        obx_8.reference_range = '150-400'
        obx_8.observation_result_status = 'F'
        obx_8.date_time_of_the_observation = '20240315091200+1000'

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
    """ Based on live/au/au-citadel-auslab.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AUSLAB')
        msh.sending_facility = HD(hd_1='RBWH_PATH', hd_2='2184', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='MEDICAL_DIRECTOR')
        msh.receiving_facility = HD(hd_1='RBWH')
        msh.security = '20240422143500+1000'
        msh.message_control_id = 'ORU^R01'
        msh.processing_id = PT(pt_1='MSG00002')
        msh.version_id = VID(vid_1='P')
        msh.msh_13 = '2.4^AUS&&ISO3166_1^HL7AU.ONO.1&&HL7AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN6294381', cx_4='RBWH', cx_5='MR'), CX(cx_1='4736812590', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='ROBERTS', xpn_2='GAVIN', xpn_3='MICHAEL', xpn_7='L')
        pid.date_time_of_birth = '19670923'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='27 Bowen Bridge Road', xad_3='BOWEN HILLS', xad_4='QLD', xad_5='4006', xad_6='AUS', xad_7='C')
        pid.pid_13 = '0732853619'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='WARD7B', pl_4='RBWH')
        pv1.attending_doctor = XCN(xcn_1='0492385T', xcn_2='BAKER', xcn_3='DIANE', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.referring_doctor = XCN(xcn_1='0492385T', xcn_2='BAKER', xcn_3='DIANE', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.patient_type = CWE(cwe_1='ADM')
        pv1.prior_temporary_location = PL(pl_1='20240420')

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
        orc.filler_order_number = EI(ei_1='24-2045871-RBWH-0', ei_2='RBWH_PATH', ei_3='2184', ei_4='AUSNATA')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.filler_order_number = EI(ei_1='24-2045871-RBWH-0', ei_2='RBWH_PATH', ei_3='2184', ei_4='AUSNATA')
        obr.universal_service_identifier = CWE(cwe_1='CHEM', cwe_2='ELECTROLYTES UREA CREATININE', cwe_3='2184')
        obr.observation_date_time = '20240422120000+1000'
        obr.danger_code = CWE(cwe_1='Urgent')
        obr.obr_14 = '20240422121500+1000'
        obr.obr_16 = '0492385T^BAKER^DIANE^^^DR^^^AUSHICPR^L^^^UPIN'
        obr.charge_to_practice = MOC(moc_1='20240422143500+1000')
        obr.parent_result = PRL(prl_1='F')
        obr.obr_33 = '0492385T^BAKER^DIANE'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Sodium', cwe_3='LN')
        obx.obx_5 = '128'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '135-145'
        obx.interpretation_codes = CWE(cwe_1='LL')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240422143500+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Potassium', cwe_3='LN')
        obx_2.obx_5 = '5.8'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '3.5-5.2'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240422143500+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2075-0', cwe_2='Chloride', cwe_3='LN')
        obx_3.obx_5 = '96'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '95-110'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240422143500+1000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1963-8', cwe_2='Bicarbonate', cwe_3='LN')
        obx_4.obx_5 = '18'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '22-32'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240422143500+1000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea', cwe_3='LN')
        obx_5.obx_5 = '18.5'
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '3.0-8.0'
        obx_5.interpretation_codes = CWE(cwe_1='HH')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20240422143500+1000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinine', cwe_3='LN')
        obx_6.obx_5 = '285'
        obx_6.units = CWE(cwe_1='umol/L')
        obx_6.reference_range = '60-110'
        obx_6.interpretation_codes = CWE(cwe_1='HH')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20240422143500+1000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='33914-3', cwe_2='eGFR', cwe_3='LN')
        obx_7.obx_5 = '17'
        obx_7.units = CWE(cwe_1='mL/min/1.73m2')
        obx_7.reference_range = '>60'
        obx_7.interpretation_codes = CWE(cwe_1='L')
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20240422143500+1000'

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
    """ Based on live/au/au-citadel-auslab.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BEST_PRACTICE')
        msh.sending_facility = HD(hd_1='MILTON_VILLAGE_GP', hd_2='AUSHICPR')
        msh.receiving_application = HD(hd_1='AUSLAB')
        msh.receiving_facility = HD(hd_1='QLD_HEALTH_PATH', hd_2='2567', hd_3='AUSNATA')
        msh.date_time_of_message = '20240510080000+1000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'ORD00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4', vid_2='AUS&&ISO3166_1', vid_3='HL7AU.ONO.1&&HL7AU')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN3849172', cx_4='QLD_HEALTH', cx_5='MR'), CX(cx_1='3361928475', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='PHILLIPS', xpn_2='MEGAN', xpn_3='LOUISE', xpn_7='L')
        pid.date_time_of_birth = '19780214'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='62 Park Road', xad_3='MILTON', xad_4='QLD', xad_5='4064', xad_6='AUS', xad_7='C')
        pid.pid_13 = '0438172645'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MILTON_VILLAGE_GP', pl_4='AUSHICPR')
        pv1.attending_doctor = XCN(xcn_1='0573821U', xcn_2='TAYLOR', xcn_3='PETER', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')

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
        orc.placer_order_number = EI(ei_1='PL-2024-0893', ei_2='MILTON_VILLAGE_GP', ei_3='AUSHICPR')
        orc.order_status = 'IP'
        orc.date_time_of_order_event = '20240510080000+1000'
        orc.orc_12 = '0573821U^TAYLOR^PETER^^^DR^^^AUSHICPR^L^^^UPIN'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PL-2024-0893', ei_2='MILTON_VILLAGE_GP', ei_3='AUSHICPR')
        obr.universal_service_identifier = CWE(cwe_1='LFT', cwe_2='LIVER FUNCTION TESTS', cwe_3='2567')
        obr.observation_date_time = '20240510'
        obr.specimen_action_code = 'A'
        obr.relevant_clinical_information = CWE(cwe_1='Fatigue and RUQ discomfort. Hx alcohol use.')
        obr.obr_15 = '0573821U^TAYLOR^PETER^^^DR^^^AUSHICPR^L^^^UPIN'

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
    """ Based on live/au/au-citadel-auslab.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AUSLAB')
        msh.sending_facility = HD(hd_1='QLD_HEALTH_PATH', hd_2='2567', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='BEST_PRACTICE')
        msh.receiving_facility = HD(hd_1='TARRAGINDI_FAMILY_GP')
        msh.security = '20240511102300+1000'
        msh.message_control_id = 'ORU^R01'
        msh.processing_id = PT(pt_1='MSG00004')
        msh.version_id = VID(vid_1='P')
        msh.msh_13 = '2.4^AUS&&ISO3166_1^HL7AU.ONO.1&&HL7AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN3962041', cx_4='QLD_HEALTH', cx_5='MR'), CX(cx_1='3362715980', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='VOSS', xpn_2='TIMOTHY', xpn_3='DAMIEN', xpn_7='L')
        pid.date_time_of_birth = '19690907'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='14 Ekibin Road', xad_3='TARRAGINDI', xad_4='QLD', xad_5='4121', xad_6='AUS', xad_7='C')
        pid.pid_13 = '0738492716'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TARRAGINDI_FAMILY_GP', pl_4='AUSHICPR')
        pv1.attending_doctor = XCN(xcn_1='0581297U', xcn_2='OAKLEY', xcn_3='MIRIAM', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.referring_doctor = XCN(xcn_1='0581297U', xcn_2='OAKLEY', xcn_3='MIRIAM', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.patient_type = CWE(cwe_1='REF')
        pv1.prior_temporary_location = PL(pl_1='20240510')

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
        orc.placer_order_number = EI(ei_1='PL-2024-1102', ei_2='TARRAGINDI_FAMILY_GP', ei_3='AUSHICPR')
        orc.filler_order_number = EI(ei_1='24-2099865-BNE-0', ei_2='QLD_HEALTH_PATH', ei_3='2567', ei_4='AUSNATA')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PL-2024-1102', ei_2='TARRAGINDI_FAMILY_GP', ei_3='AUSHICPR')
        obr.filler_order_number = EI(ei_1='24-2099865-BNE-0', ei_2='QLD_HEALTH_PATH', ei_3='2567', ei_4='AUSNATA')
        obr.universal_service_identifier = CWE(cwe_1='LFT', cwe_2='LIVER FUNCTION TESTS', cwe_3='2567')
        obr.observation_date_time = '20240510121500+1000'
        obr.danger_code = CWE(cwe_1='Routine')
        obr.obr_14 = '20240510130000+1000'
        obr.obr_16 = '0581297U^OAKLEY^MIRIAM^^^DR^^^AUSHICPR^L^^^UPIN'
        obr.charge_to_practice = MOC(moc_1='20240511102300+1000')
        obr.parent_result = PRL(prl_1='F')
        obr.obr_33 = '0581297U^OAKLEY^MIRIAM'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT', cwe_3='LN')
        obx.obx_5 = '187'
        obx.units = CWE(cwe_1='U/L')
        obx.reference_range = '<41'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240511102300+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST', cwe_3='LN')
        obx_2.obx_5 = '95'
        obx_2.units = CWE(cwe_1='U/L')
        obx_2.reference_range = '<40'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240511102300+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='6768-6', cwe_2='ALP', cwe_3='LN')
        obx_3.obx_5 = '78'
        obx_3.units = CWE(cwe_1='U/L')
        obx_3.reference_range = '30-110'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240511102300+1000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1975-2', cwe_2='Bilirubin (Total)', cwe_3='LN')
        obx_4.obx_5 = '22'
        obx_4.units = CWE(cwe_1='umol/L')
        obx_4.reference_range = '<21'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240511102300+1000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2336-6', cwe_2='GGT', cwe_3='LN')
        obx_5.obx_5 = '112'
        obx_5.units = CWE(cwe_1='U/L')
        obx_5.reference_range = '<50'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20240511102300+1000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='1751-7', cwe_2='Albumin', cwe_3='LN')
        obx_6.obx_5 = '36'
        obx_6.units = CWE(cwe_1='g/L')
        obx_6.reference_range = '35-50'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20240511102300+1000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='2885-2', cwe_2='Total Protein', cwe_3='LN')
        obx_7.obx_5 = '72'
        obx_7.units = CWE(cwe_1='g/L')
        obx_7.reference_range = '60-80'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20240511102300+1000'

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
    """ Based on live/au/au-citadel-auslab.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AUSLAB_LIS')
        msh.sending_facility = HD(hd_1='SA_PATH', hd_2='1935', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='OACIS')
        msh.receiving_facility = HD(hd_1='RAH')
        msh.security = '20240618161500+0930'
        msh.message_control_id = 'ORU^R01'
        msh.processing_id = PT(pt_1='MSG00005')
        msh.version_id = VID(vid_1='P')
        msh.msh_13 = '2.4^AUS&&ISO3166_1^HL7AU.ONO.1&&HL7AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN4172936', cx_4='RAH', cx_5='MR'), CX(cx_1='6285947130', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='CARTER', xpn_2='WILLIAM', xpn_3='GEORGE', xpn_7='L')
        pid.date_time_of_birth = '19520830'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='58 North Terrace', xad_3='ADELAIDE', xad_4='SA', xad_5='5000', xad_6='AUS', xad_7='C')
        pid.pid_13 = '0883417285'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_4='RAH')
        pv1.attending_doctor = XCN(xcn_1='0263849V', xcn_2='CHEN', xcn_3='WENDY', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.referring_doctor = XCN(xcn_1='0263849V', xcn_2='CHEN', xcn_3='WENDY', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.patient_type = CWE(cwe_1='ADM')
        pv1.prior_temporary_location = PL(pl_1='20240615')

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
        orc.filler_order_number = EI(ei_1='24-M089234-RAH-0', ei_2='SA_PATH', ei_3='1935', ei_4='AUSNATA')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.filler_order_number = EI(ei_1='24-M089234-RAH-0', ei_2='SA_PATH', ei_3='1935', ei_4='AUSNATA')
        obr.universal_service_identifier = CWE(cwe_1='BLDCX', cwe_2='BLOOD CULTURE', cwe_3='1935')
        obr.observation_date_time = '20240616080000+0930'
        obr.danger_code = CWE(cwe_1='Urgent')
        obr.obr_14 = '20240616081500+0930'
        obr.obr_16 = '0263849V^CHEN^WENDY^^^DR^^^AUSHICPR^L^^^UPIN'
        obr.charge_to_practice = MOC(moc_1='20240618161500+0930')
        obr.parent_result = PRL(prl_1='F')
        obr.obr_32 = 'MB'
        obr.obr_33 = '0263849V^CHEN^WENDY'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Bacteria identified', cwe_3='LN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '3092008^Staphylococcus aureus^SCT'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240618161500+0930'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='29576-6', cwe_2='Bacterial susceptibility panel', cwe_3='LN')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = 'See below'
        obx_2.probability = 'A'
        obx_2.effective_date_of_reference_range = 'F'
        obx_2.producers_id = CWE(cwe_1='20240618161500+0930')

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18907-6', cwe_2='Methicillin', cwe_3='LN')
        obx_3.observation_sub_id = OG(og_1='1')
        obx_3.obx_5 = 'Susceptible'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240618161500+0930'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18961-3', cwe_2='Vancomycin', cwe_3='LN')
        obx_4.observation_sub_id = OG(og_1='1')
        obx_4.obx_5 = 'Susceptible'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240618161500+0930'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18878-9', cwe_2='Gentamicin', cwe_3='LN')
        obx_5.observation_sub_id = OG(og_1='1')
        obx_5.obx_5 = 'Susceptible'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20240618161500+0930'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='18993-6', cwe_2='Erythromycin', cwe_3='LN')
        obx_6.observation_sub_id = OG(og_1='1')
        obx_6.obx_5 = 'Resistant'
        obx_6.interpretation_codes = CWE(cwe_1='A')
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20240618161500+0930'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'FT'
        obx_7.observation_identifier = CWE(cwe_1='INTERP', cwe_2='Interpretation', cwe_3='L')
        obx_7.observation_sub_id = OG(og_1='1')
        obx_7.obx_5 = (
            'Blood culture positive at 18 hours. Gram positive cocci in clusters.\\.br\\Identified as Staphylococcus aureus - MSSA.\\.br\\Suggest IV flucloxa'
            'cillin.'
        )
        obx_7.probability = 'A'
        obx_7.effective_date_of_reference_range = 'F'
        obx_7.producers_id = CWE(cwe_1='20240618161500+0930')

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
    """ Based on live/au/au-citadel-auslab.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CITADEL')
        msh.sending_facility = HD(hd_1='TOWNSVILLE_PATH', hd_2='3241', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='COMMUNICARE')
        msh.receiving_facility = HD(hd_1='TOWNSVILLE_HOSP')
        msh.security = '20240703080500+1000'
        msh.message_control_id = 'ORU^R01'
        msh.processing_id = PT(pt_1='MSG00006')
        msh.version_id = VID(vid_1='P')
        msh.msh_13 = '2.3.1^AUS&&ISO3166_1^HL7AU.ONO.1&&HL7AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN5294817', cx_4='TSVH', cx_5='MR'), CX(cx_1='2471835629', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='MURPHY', xpn_2='TARA', xpn_7='L')
        pid.date_time_of_birth = '19910615'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='14 Eyre Street', xad_3='NORTH WARD', xad_4='QLD', xad_5='4810', xad_6='AUS', xad_7='C')
        pid.pid_13 = '0747328165'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TOWNSVILLE_HOSP', pl_4='TSVH')
        pv1.attending_doctor = XCN(xcn_1='0584172W', xcn_2='MITCHELL', xcn_3='GRAHAM', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.referring_doctor = XCN(xcn_1='0584172W', xcn_2='MITCHELL', xcn_3='GRAHAM', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.patient_type = CWE(cwe_1='REF')
        pv1.prior_temporary_location = PL(pl_1='20240702')

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
        orc.filler_order_number = EI(ei_1='24-T543210-TSV-0', ei_2='TOWNSVILLE_PATH', ei_3='3241', ei_4='AUSNATA')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.filler_order_number = EI(ei_1='24-T543210-TSV-0', ei_2='TOWNSVILLE_PATH', ei_3='3241', ei_4='AUSNATA')
        obr.universal_service_identifier = CWE(cwe_1='TFT', cwe_2='THYROID FUNCTION TESTS', cwe_3='3241')
        obr.observation_date_time = '20240702141500+1000'
        obr.danger_code = CWE(cwe_1='Routine')
        obr.obr_14 = '20240702150000+1000'
        obr.obr_16 = '0584172W^MITCHELL^GRAHAM^^^DR^^^AUSHICPR^L^^^UPIN'
        obr.charge_to_practice = MOC(moc_1='20240703080500+1000')
        obr.parent_result = PRL(prl_1='F')
        obr.obr_33 = '0584172W^MITCHELL^GRAHAM'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='TSH', cwe_3='LN')
        obx.obx_5 = '0.08'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.40-4.00'
        obx.interpretation_codes = CWE(cwe_1='LL')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240703080500+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3024-7', cwe_2='Free T4', cwe_3='LN')
        obx_2.obx_5 = '32.5'
        obx_2.units = CWE(cwe_1='pmol/L')
        obx_2.reference_range = '10.0-20.0'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240703080500+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3053-6', cwe_2='Free T3', cwe_3='LN')
        obx_3.obx_5 = '9.8'
        obx_3.units = CWE(cwe_1='pmol/L')
        obx_3.reference_range = '3.5-6.5'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240703080500+1000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'FT'
        obx_4.observation_identifier = CWE(cwe_1='COMMENT', cwe_2='Result Comment', cwe_3='L')
        obx_4.obx_5 = 'Thyroid function results consistent with hyperthyroidism.\\.br\\Recommend thyroid antibodies and thyroid uptake scan.'
        obx_4.probability = 'N'
        obx_4.effective_date_of_reference_range = 'F'
        obx_4.producers_id = CWE(cwe_1='20240703080500+1000')

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
    """ Based on live/au/au-citadel-auslab.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CARESYS')
        msh.sending_facility = HD(hd_1='RDH', hd_2='9876', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='AUSLAB')
        msh.receiving_facility = HD(hd_1='NT_PATH', hd_2='4102', hd_3='AUSNATA')
        msh.date_time_of_message = '20240812090000+0930'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        msh.message_control_id = 'ADT00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4', vid_2='AUS&&ISO3166_1', vid_3='HL7AU.ONO.1&&HL7AU')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20240812090000+0930'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN6385291', cx_4='RDH', cx_5='MR'), CX(cx_1='5147286390', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='EDWARDS', xpn_2='MASON', xpn_7='L')
        pid.date_time_of_birth = '19880305'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='21 Cavenagh Street', xad_3='DARWIN', xad_4='NT', xad_5='0800', xad_6='AUS', xad_7='C')
        pid.pid_13 = '0889715246'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='MED_WARD', pl_4='RDH')
        pv1.attending_doctor = XCN(xcn_1='0617248Y', xcn_2='STEWART', xcn_3='FIONA', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.referring_doctor = XCN(xcn_1='0617248Y', xcn_2='STEWART', xcn_3='FIONA', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='0617248Y', xcn_2='STEWART', xcn_3='FIONA', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.patient_type = CWE(cwe_1='ADM')
        pv1.admit_date_time = '20240812090000+0930'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/au/au-citadel-auslab.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HBCIS')
        msh.sending_facility = HD(hd_1='PAH', hd_2='2567', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='AUSLAB')
        msh.receiving_facility = HD(hd_1='QLD_HEALTH_PATH', hd_2='2567', hd_3='AUSNATA')
        msh.date_time_of_message = '20240820153000+1000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03')
        msh.message_control_id = 'ADT00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4', vid_2='AUS&&ISO3166_1', vid_3='HL7AU.ONO.1&&HL7AU')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20240820153000+1000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN7194863', cx_4='PAH', cx_5='MR'), CX(cx_1='6238471569', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='COOPER', xpn_2='PATRICIA', xpn_3='GAIL', xpn_7='L')
        pid.date_time_of_birth = '19450718'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='33 Stanley Street', xad_3='EAST BRISBANE', xad_4='QLD', xad_5='4169', xad_6='AUS', xad_7='C')
        pid.pid_13 = '0738164257'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SURG_B', pl_4='PAH')
        pv1.attending_doctor = XCN(xcn_1='0481294Z', xcn_2='MORRIS', xcn_3='GREGORY', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.referring_doctor = XCN(xcn_1='0481294Z', xcn_2='MORRIS', xcn_3='GREGORY', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.hospital_service = CWE(cwe_1='SURG')
        pv1.admit_source = CWE(cwe_1='7')
        pv1.admitting_doctor = XCN(xcn_1='0481294Z', xcn_2='MORRIS', xcn_3='GREGORY', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.patient_type = CWE(cwe_1='ADM')
        pv1.admit_date_time = '20240815'
        pv1.current_patient_balance = '20240820153000+1000'

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/au/au-citadel-auslab.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='COMMUNICARE')
        msh.sending_facility = HD(hd_1='TODD_MALL_MEDICAL', hd_2='AUSHICPR')
        msh.receiving_application = HD(hd_1='AUSLAB_LIS')
        msh.receiving_facility = HD(hd_1='NT_PATH', hd_2='4102', hd_3='AUSNATA')
        msh.date_time_of_message = '20240905073000+0930'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'ORD00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1', vid_2='AUS&&ISO3166_1', vid_3='HL7AU.ONO.1&&HL7AU')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN8295174', cx_4='ASH', cx_5='MR'), CX(cx_1='2937184625', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='BELL', xpn_2='DANIELLE', xpn_3='MAREE', xpn_7='L')
        pid.date_time_of_birth = '19830921'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='27 Todd Street', xad_3='ALICE SPRINGS', xad_4='NT', xad_5='0870', xad_6='AUS', xad_7='C')
        pid.pid_13 = '0889432817'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='TODD_MALL_MEDICAL', pl_4='AUSHICPR')
        pv1.attending_doctor = XCN(xcn_1='0563819A1', xcn_2='WANG', xcn_3='XIULAN', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')

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
        orc.placer_order_number = EI(ei_1='PL-2024-5521', ei_2='TODD_MALL_MEDICAL', ei_3='AUSHICPR')
        orc.order_status = 'IP'
        orc.date_time_of_order_event = '20240905073000+0930'
        orc.orc_12 = '0563819A1^WANG^XIULAN^^^DR^^^AUSHICPR^L^^^UPIN'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PL-2024-5521', ei_2='TODD_MALL_MEDICAL', ei_3='AUSHICPR')
        obr.universal_service_identifier = CWE(cwe_1='LIPID', cwe_2='LIPID STUDIES', cwe_3='4102')
        obr.observation_date_time = '20240905'
        obr.specimen_action_code = 'A'
        obr.relevant_clinical_information = CWE(cwe_1='Fasting. Assess cardiovascular risk.')
        obr.obr_15 = '0563819A1^WANG^XIULAN^^^DR^^^AUSHICPR^L^^^UPIN'

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
    """ Based on live/au/au-citadel-auslab.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AUSLAB_LIS')
        msh.sending_facility = HD(hd_1='NT_PATH', hd_2='4102', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='COMMUNICARE')
        msh.receiving_facility = HD(hd_1='KATHERINE_HEALTHCARE')
        msh.security = '20240906091500+0930'
        msh.message_control_id = 'ORU^R01'
        msh.processing_id = PT(pt_1='MSG00010')
        msh.version_id = VID(vid_1='P')
        msh.msh_13 = '2.3.1^AUS&&ISO3166_1^HL7AU.ONO.1&&HL7AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN8419362', cx_4='KATH', cx_5='MR'), CX(cx_1='2938651047', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='TIPILOURA', xpn_2='WARREN', xpn_3='JABULU', xpn_7='L')
        pid.date_time_of_birth = '19711105'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='9 Lindsay Street', xad_3='KATHERINE', xad_4='NT', xad_5='0850', xad_6='AUS', xad_7='C')
        pid.pid_13 = '0889716203'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='KATHERINE_HEALTHCARE', pl_4='AUSHICPR')
        pv1.attending_doctor = XCN(xcn_1='0578264A1', xcn_2='MAYWALD', xcn_3='PAULINE', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.referring_doctor = XCN(xcn_1='0578264A1', xcn_2='MAYWALD', xcn_3='PAULINE', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.patient_type = CWE(cwe_1='REF')
        pv1.prior_temporary_location = PL(pl_1='20240905')

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
        orc.placer_order_number = EI(ei_1='PL-2024-6711', ei_2='KATHERINE_HEALTHCARE', ei_3='AUSHICPR')
        orc.filler_order_number = EI(ei_1='24-N785402-KAT-0', ei_2='NT_PATH', ei_3='4102', ei_4='AUSNATA')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PL-2024-6711', ei_2='KATHERINE_HEALTHCARE', ei_3='AUSHICPR')
        obr.filler_order_number = EI(ei_1='24-N785402-KAT-0', ei_2='NT_PATH', ei_3='4102', ei_4='AUSNATA')
        obr.universal_service_identifier = CWE(cwe_1='LIPID', cwe_2='LIPID STUDIES', cwe_3='4102')
        obr.observation_date_time = '20240905080000+0930'
        obr.danger_code = CWE(cwe_1='Routine')
        obr.obr_14 = '20240905081500+0930'
        obr.obr_16 = '0578264A1^MAYWALD^PAULINE^^^DR^^^AUSHICPR^L^^^UPIN'
        obr.charge_to_practice = MOC(moc_1='20240906091500+0930')
        obr.parent_result = PRL(prl_1='F')
        obr.obr_33 = '0578264A1^MAYWALD^PAULINE'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2093-3', cwe_2='Total Cholesterol', cwe_3='LN')
        obx.obx_5 = '6.8'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '<5.5'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240906091500+0930'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2571-8', cwe_2='Triglycerides', cwe_3='LN')
        obx_2.obx_5 = '2.4'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '<2.0'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240906091500+0930'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2085-9', cwe_2='HDL Cholesterol', cwe_3='LN')
        obx_3.obx_5 = '1.1'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '>1.0'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240906091500+0930'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='13457-7', cwe_2='LDL Cholesterol (calc)', cwe_3='LN')
        obx_4.obx_5 = '4.6'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '<3.5'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240906091500+0930'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='9830-1', cwe_2='Chol/HDL Ratio', cwe_3='LN')
        obx_5.obx_5 = '6.2'
        obx_5.reference_range = '<4.5'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20240906091500+0930'

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
    """ Based on live/au/au-citadel-auslab.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EVOLUTION')
        msh.sending_facility = HD(hd_1='SA_PATH', hd_2='1935', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='MEDICAL_DIRECTOR')
        msh.receiving_facility = HD(hd_1='FMC')
        msh.security = '20240718110000+0930'
        msh.message_control_id = 'ORU^R01'
        msh.processing_id = PT(pt_1='MSG00011')
        msh.version_id = VID(vid_1='P')
        msh.msh_13 = '2.4^AUS&&ISO3166_1^HL7AU.ONO.1&&HL7AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN9326478', cx_4='FMC', cx_5='MR'), CX(cx_1='3158294736', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='COSTAS', xpn_2='IRENE', xpn_7='L')
        pid.date_time_of_birth = '19700311'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='45 Marion Road', xad_3='PLYMPTON', xad_4='SA', xad_5='5038', xad_6='AUS', xad_7='C')
        pid.pid_13 = '0883517462'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='FMC_OUTPAT', pl_4='FMC')
        pv1.attending_doctor = XCN(xcn_1='0327154B', xcn_2='SINGH', xcn_3='HARPREET', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.referring_doctor = XCN(xcn_1='0327154B', xcn_2='SINGH', xcn_3='HARPREET', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.patient_type = CWE(cwe_1='REF')
        pv1.prior_temporary_location = PL(pl_1='20240717')

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
        orc.filler_order_number = EI(ei_1='24-S234567-FMC-0', ei_2='SA_PATH', ei_3='1935', ei_4='AUSNATA')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.filler_order_number = EI(ei_1='24-S234567-FMC-0', ei_2='SA_PATH', ei_3='1935', ei_4='AUSNATA')
        obr.universal_service_identifier = CWE(cwe_1='HBA1C', cwe_2='GLYCATED HAEMOGLOBIN', cwe_3='1935')
        obr.observation_date_time = '20240717093000+0930'
        obr.danger_code = CWE(cwe_1='Routine')
        obr.obr_14 = '20240717094500+0930'
        obr.obr_16 = '0327154B^SINGH^HARPREET^^^DR^^^AUSHICPR^L^^^UPIN'
        obr.charge_to_practice = MOC(moc_1='20240718110000+0930')
        obr.parent_result = PRL(prl_1='F')
        obr.obr_33 = '0327154B^SINGH^HARPREET'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obx.obx_5 = '8.2'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '<6.5'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240718110000+0930'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='59261-8', cwe_2='HbA1c (IFCC)', cwe_3='LN')
        obx_2.obx_5 = '66'
        obx_2.units = CWE(cwe_1='mmol/mol')
        obx_2.reference_range = '<48'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240718110000+0930'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='14749-6', cwe_2='Glucose (fasting)', cwe_3='LN')
        obx_3.obx_5 = '9.8'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '3.0-5.4'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240718110000+0930'

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
    """ Based on live/au/au-citadel-auslab.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AUSLAB')
        msh.sending_facility = HD(hd_1='QLD_HEALTH_PATH', hd_2='2567', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='ZEDMED')
        msh.receiving_facility = HD(hd_1='CAIRNS_BASE')
        msh.security = '20240201155000+1000'
        msh.message_control_id = 'ORU^R01'
        msh.processing_id = PT(pt_1='MSG00012')
        msh.version_id = VID(vid_1='P')
        msh.msh_13 = '2.4^AUS&&ISO3166_1^HL7AU.ONO.1&&HL7AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN1493827', cx_4='CBH', cx_5='MR'), CX(cx_1='4625791038', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='THOMPSON', xpn_2='CLIVE', xpn_3='EDWARD', xpn_7='L')
        pid.date_time_of_birth = '19410505'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='9 Lake Street', xad_3='CAIRNS', xad_4='QLD', xad_5='4870', xad_6='AUS', xad_7='C')
        pid.pid_13 = '0740672594'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='WARD3A', pl_4='CBH')
        pv1.attending_doctor = XCN(xcn_1='0628173C', xcn_2='LEE', xcn_3='MIN-JUN', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.referring_doctor = XCN(xcn_1='0628173C', xcn_2='LEE', xcn_3='MIN-JUN', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.patient_type = CWE(cwe_1='ADM')
        pv1.prior_temporary_location = PL(pl_1='20240130')

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
        orc.filler_order_number = EI(ei_1='24-C098712-CBH-0', ei_2='QLD_HEALTH_PATH', ei_3='2567', ei_4='AUSNATA')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.filler_order_number = EI(ei_1='24-C098712-CBH-0', ei_2='QLD_HEALTH_PATH', ei_3='2567', ei_4='AUSNATA')
        obr.universal_service_identifier = CWE(cwe_1='COAG', cwe_2='COAGULATION STUDIES', cwe_3='2567')
        obr.observation_date_time = '20240201130000+1000'
        obr.danger_code = CWE(cwe_1='Urgent')
        obr.obr_14 = '20240201131500+1000'
        obr.obr_16 = '0628173C^LEE^MIN-JUN^^^DR^^^AUSHICPR^L^^^UPIN'
        obr.charge_to_practice = MOC(moc_1='20240201155000+1000')
        obr.parent_result = PRL(prl_1='F')
        obr.obr_33 = '0628173C^LEE^MIN-JUN'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='Prothrombin time', cwe_3='LN')
        obx.obx_5 = '38.5'
        obx.units = CWE(cwe_1='sec')
        obx.reference_range = '11.0-15.0'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240201155000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6301-6', cwe_2='INR', cwe_3='LN')
        obx_2.obx_5 = '4.8'
        obx_2.reference_range = '0.9-1.3'
        obx_2.interpretation_codes = CWE(cwe_1='HH')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240201155000+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3173-2', cwe_2='APTT', cwe_3='LN')
        obx_3.obx_5 = '52.1'
        obx_3.units = CWE(cwe_1='sec')
        obx_3.reference_range = '25.0-37.0'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240201155000+1000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='3255-7', cwe_2='Fibrinogen', cwe_3='LN')
        obx_4.obx_5 = '1.2'
        obx_4.units = CWE(cwe_1='g/L')
        obx_4.reference_range = '1.5-4.0'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240201155000+1000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'FT'
        obx_5.observation_identifier = CWE(cwe_1='COMMENT', cwe_2='Result Comment', cwe_3='L')
        obx_5.obx_5 = 'CRITICAL VALUE: INR 4.8 - Clinician notified by phone at 1535 hrs.'
        obx_5.probability = 'N'
        obx_5.effective_date_of_reference_range = 'F'
        obx_5.producers_id = CWE(cwe_1='20240201155000+1000')

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
    """ Based on live/au/au-citadel-auslab.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AUSLAB')
        msh.sending_facility = HD(hd_1='QLD_HEALTH_PATH', hd_2='2567', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='BEST_PRACTICE')
        msh.receiving_facility = HD(hd_1='MATER_HOSP')
        msh.security = '20240925133000+1000'
        msh.message_control_id = 'ORU^R01'
        msh.processing_id = PT(pt_1='MSG00013')
        msh.version_id = VID(vid_1='P')
        msh.msh_13 = '2.4^AUS&&ISO3166_1^HL7AU.ONO.1&&HL7AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN2517394', cx_4='MATER', cx_5='MR'), CX(cx_1='5184293760', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='KIM', xpn_2='SOOJIN', xpn_7='L')
        pid.date_time_of_birth = '19650827'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='19 Stanley Street East', xad_3='SOUTH BRISBANE', xad_4='QLD', xad_5='4101', xad_6='AUS', xad_7='C')
        pid.pid_13 = '0731547283'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MATER_OUTPAT', pl_4='MATER')
        pv1.attending_doctor = XCN(xcn_1='0419368D', xcn_2='DIAZ', xcn_3='FERNANDO', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.referring_doctor = XCN(xcn_1='0419368D', xcn_2='DIAZ', xcn_3='FERNANDO', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.patient_type = CWE(cwe_1='REF')
        pv1.prior_temporary_location = PL(pl_1='20240920')

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
        orc.filler_order_number = EI(ei_1='24-H567890-MAT-0', ei_2='QLD_HEALTH_PATH', ei_3='2567', ei_4='AUSNATA')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.filler_order_number = EI(ei_1='24-H567890-MAT-0', ei_2='QLD_HEALTH_PATH', ei_3='2567', ei_4='AUSNATA')
        obr.universal_service_identifier = CWE(cwe_1='HIST', cwe_2='HISTOPATHOLOGY', cwe_3='2567')
        obr.observation_date_time = '20240920100000+1000'
        obr.danger_code = CWE(cwe_1='Routine')
        obr.obr_14 = '20240920101500+1000'
        obr.obr_16 = '0419368D^DIAZ^FERNANDO^^^DR^^^AUSHICPR^L^^^UPIN'
        obr.charge_to_practice = MOC(moc_1='20240925133000+1000')
        obr.parent_result = PRL(prl_1='F')
        obr.obr_32 = 'AP'
        obr.obr_33 = '0419368D^DIAZ^FERNANDO'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='22634-0', cwe_2='Pathology report', cwe_3='LN')
        obx.obx_5 = (
            'SKIN EXCISION - LEFT FOREARM\\.br\\\\.br\\MACROSCOPY: Ellipse of skin 22x11x8mm with a central raised pigmented lesion 7mm diameter.\\.br\\\\.br'
            '\\MICROSCOPY: Sections show a compound melanocytic naevus with junctional and dermal components. No dysplasia. Excision appears complete.\\.br'
            '\\\\.br\\DIAGNOSIS: Compound melanocytic naevus, left forearm. No evidence of malignancy.'
        )
        obx.probability = 'N'
        obx.effective_date_of_reference_range = 'F'
        obx.producers_id = CWE(cwe_1='20240925133000+1000')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Pathology Report', cwe_3='LN')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMg'
            'MCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5'
            'IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo='
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
    """ Based on live/au/au-citadel-auslab.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CITADEL')
        msh.sending_facility = HD(hd_1='LOGAN_PATH', hd_2='2567', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='MEDICAL_DIRECTOR')
        msh.receiving_facility = HD(hd_1='LOGAN_HOSP')
        msh.security = '20241008142000+1000'
        msh.message_control_id = 'ORU^R01'
        msh.processing_id = PT(pt_1='MSG00014')
        msh.version_id = VID(vid_1='P')
        msh.msh_13 = '2.4^AUS&&ISO3166_1^HL7AU.ONO.1&&HL7AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN3628194', cx_4='LOGAN', cx_5='MR'), CX(cx_1='4392851076', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='NELSON', xpn_2='TYLER', xpn_3='DEAN', xpn_7='L')
        pid.date_time_of_birth = '19950714'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='62 Wembley Road', xad_3='LOGAN CENTRAL', xad_4='QLD', xad_5='4114', xad_6='AUS', xad_7='C')
        pid.pid_13 = '0732547916'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_4='LOGAN')
        pv1.attending_doctor = XCN(xcn_1='0518273E', xcn_2='OWENS', xcn_3='LIAM', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.referring_doctor = XCN(xcn_1='0518273E', xcn_2='OWENS', xcn_3='LIAM', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.patient_type = CWE(cwe_1='EMER')
        pv1.prior_temporary_location = PL(pl_1='20241008')

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
        orc.filler_order_number = EI(ei_1='24-U345678-LOG-0', ei_2='LOGAN_PATH', ei_3='2567', ei_4='AUSNATA')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.filler_order_number = EI(ei_1='24-U345678-LOG-0', ei_2='LOGAN_PATH', ei_3='2567', ei_4='AUSNATA')
        obr.universal_service_identifier = CWE(cwe_1='UDRUG', cwe_2='URINE DRUG SCREEN', cwe_3='2567')
        obr.observation_date_time = '20241008120000+1000'
        obr.danger_code = CWE(cwe_1='Urgent')
        obr.obr_14 = '20241008121000+1000'
        obr.obr_16 = '0518273E^OWENS^LIAM^^^DR^^^AUSHICPR^L^^^UPIN'
        obr.charge_to_practice = MOC(moc_1='20241008142000+1000')
        obr.parent_result = PRL(prl_1='F')
        obr.obr_33 = '0518273E^OWENS^LIAM'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='19295-5', cwe_2='Amphetamines screen', cwe_3='LN')
        obx.obx_5 = '260373001^Detected^SCT'
        obx.interpretation_codes = CWE(cwe_1='A')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20241008142000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='19296-3', cwe_2='Benzodiazepines screen', cwe_3='LN')
        obx_2.obx_5 = '260415000^Not detected^SCT'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20241008142000+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='19297-1', cwe_2='Cannabinoids screen', cwe_3='LN')
        obx_3.obx_5 = '260373001^Detected^SCT'
        obx_3.interpretation_codes = CWE(cwe_1='A')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20241008142000+1000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'CE'
        obx_4.observation_identifier = CWE(cwe_1='3426-4', cwe_2='Cocaine metabolite screen', cwe_3='LN')
        obx_4.obx_5 = '260415000^Not detected^SCT'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20241008142000+1000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'CE'
        obx_5.observation_identifier = CWE(cwe_1='19299-7', cwe_2='Opiates screen', cwe_3='LN')
        obx_5.obx_5 = '260415000^Not detected^SCT'
        obx_5.interpretation_codes = CWE(cwe_1='N')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20241008142000+1000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'FT'
        obx_6.observation_identifier = CWE(cwe_1='COMMENT', cwe_2='Result Comment', cwe_3='L')
        obx_6.obx_5 = 'Presumptive screen only. Positive results should be confirmed by GC-MS if clinically required.'
        obx_6.probability = 'N'
        obx_6.effective_date_of_reference_range = 'F'
        obx_6.producers_id = CWE(cwe_1='20241008142000+1000')

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
    """ Based on live/au/au-citadel-auslab.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HBCIS')
        msh.sending_facility = HD(hd_1='RBWH', hd_2='2184', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='AUSLAB')
        msh.receiving_facility = HD(hd_1='QLD_HEALTH_PATH', hd_2='2567', hd_3='AUSNATA')
        msh.date_time_of_message = '20240307111500+1000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08')
        msh.message_control_id = 'ADT00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4', vid_2='AUS&&ISO3166_1', vid_3='HL7AU.ONO.1&&HL7AU')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20240307111500+1000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN6371905', cx_4='RBWH', cx_5='MR'), CX(cx_1='4738162947', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='AGGARWAL', xpn_2='RANJEET', xpn_3='VIJAY', xpn_7='L')
        pid.date_time_of_birth = '19751222'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Unit 8, 47 Vulture Street', xad_3='WEST END', xad_4='QLD', xad_5='4101', xad_6='AUS', xad_7='C')
        pid.pid_13 = '0732891054'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='WARD7B', pl_4='RBWH')
        pv1.attending_doctor = XCN(xcn_1='0497612T', xcn_2='OKAFOR', xcn_3='IFEYINWA', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.referring_doctor = XCN(xcn_1='0497612T', xcn_2='OKAFOR', xcn_3='IFEYINWA', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.patient_type = CWE(cwe_1='ADM')
        pv1.prior_temporary_location = PL(pl_1='20240305')

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/au/au-citadel-auslab.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='FIRSTNET')
        msh.sending_facility = HD(hd_1='GCUH_ED', hd_2='AUSHICPR')
        msh.receiving_application = HD(hd_1='AUSLAB')
        msh.receiving_facility = HD(hd_1='QLD_HEALTH_PATH', hd_2='2567', hd_3='AUSNATA')
        msh.date_time_of_message = '20241112021500+1000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'ORD00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4', vid_2='AUS&&ISO3166_1', vid_3='HL7AU.ONO.1&&HL7AU')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN4738162', cx_4='GCUH', cx_5='MR'), CX(cx_1='6841729350', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='BENNETT', xpn_2='GORDON', xpn_3='FRANK', xpn_7='L')
        pid.date_time_of_birth = '19580312'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='14 Scarborough Street', xad_3='SOUTHPORT', xad_4='QLD', xad_5='4215', xad_6='AUS', xad_7='C')
        pid.pid_13 = '0755128274'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_4='GCUH')
        pv1.attending_doctor = XCN(xcn_1='0729416F', xcn_2='WRIGHT', xcn_3='JEFFREY', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')

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
        orc.placer_order_number = EI(ei_1='PL-2024-9901', ei_2='GCUH_ED', ei_3='AUSHICPR')
        orc.order_status = 'SC'
        orc.date_time_of_order_event = '20241112021500+1000'
        orc.orc_12 = '0729416F^WRIGHT^JEFFREY^^^DR^^^AUSHICPR^L^^^UPIN'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PL-2024-9901', ei_2='GCUH_ED', ei_3='AUSHICPR')
        obr.universal_service_identifier = CWE(cwe_1='TROP', cwe_2='HIGH SENSITIVITY TROPONIN', cwe_3='2567')
        obr.observation_date_time = '20241112'
        obr.specimen_action_code = 'A'
        obr.relevant_clinical_information = CWE(cwe_1='Chest pain onset 2 hours ago. ECG ST depression V4-V6.')
        obr.obr_15 = '0729416F^WRIGHT^JEFFREY^^^DR^^^AUSHICPR^L^^^UPIN'

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
    """ Based on live/au/au-citadel-auslab.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AUSLAB')
        msh.sending_facility = HD(hd_1='QLD_HEALTH_PATH', hd_2='2567', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='FIRSTNET')
        msh.receiving_facility = HD(hd_1='RBH_ED')
        msh.security = '20241112033000+1000'
        msh.message_control_id = 'ORU^R01'
        msh.processing_id = PT(pt_1='MSG00017')
        msh.version_id = VID(vid_1='P')
        msh.msh_13 = '2.4^AUS&&ISO3166_1^HL7AU.ONO.1&&HL7AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN4827305', cx_4='RBH', cx_5='MR'), CX(cx_1='6843017298', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='MARTINIELLO', xpn_2='SALVATORE', xpn_3='GIANNI', xpn_7='L')
        pid.date_time_of_birth = '19510627'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='38 Bracken Street', xad_3='TINGALPA', xad_4='QLD', xad_5='4173', xad_6='AUS', xad_7='C')
        pid.pid_13 = '0738905172'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='ED', pl_4='RBH')
        pv1.attending_doctor = XCN(xcn_1='0734251F', xcn_2='FORRESTER', xcn_3='HEATHER', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.referring_doctor = XCN(xcn_1='0734251F', xcn_2='FORRESTER', xcn_3='HEATHER', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.patient_type = CWE(cwe_1='EMER')
        pv1.prior_temporary_location = PL(pl_1='20241112')

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
        orc.placer_order_number = EI(ei_1='PL-2024-9912', ei_2='RBH_ED', ei_3='AUSHICPR')
        orc.filler_order_number = EI(ei_1='24-C872041-RBH-0', ei_2='QLD_HEALTH_PATH', ei_3='2567', ei_4='AUSNATA')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PL-2024-9912', ei_2='RBH_ED', ei_3='AUSHICPR')
        obr.filler_order_number = EI(ei_1='24-C872041-RBH-0', ei_2='QLD_HEALTH_PATH', ei_3='2567', ei_4='AUSNATA')
        obr.universal_service_identifier = CWE(cwe_1='TROP', cwe_2='HIGH SENSITIVITY TROPONIN', cwe_3='2567')
        obr.observation_date_time = '20241112022000+1000'
        obr.danger_code = CWE(cwe_1='Urgent')
        obr.obr_14 = '20241112023000+1000'
        obr.obr_16 = '0734251F^FORRESTER^HEATHER^^^DR^^^AUSHICPR^L^^^UPIN'
        obr.charge_to_practice = MOC(moc_1='20241112033000+1000')
        obr.parent_result = PRL(prl_1='F')
        obr.obr_33 = '0734251F^FORRESTER^HEATHER'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='89579-7', cwe_2='hs-Troponin I', cwe_3='LN')
        obx.obx_5 = '2845'
        obx.units = CWE(cwe_1='ng/L')
        obx.reference_range = '<26'
        obx.interpretation_codes = CWE(cwe_1='HH')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20241112033000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='COMMENT', cwe_2='Result Comment', cwe_3='L')
        obx_2.obx_5 = (
            'CRITICAL VALUE: hs-Troponin I 2845 ng/L - Clinician notified by phone at 0325 hrs.\\.br\\Result significantly elevated above 99th percentile U'
            'RL of 26 ng/L.'
        )
        obx_2.probability = 'N'
        obx_2.effective_date_of_reference_range = 'F'
        obx_2.producers_id = CWE(cwe_1='20241112033000+1000')

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
    """ Based on live/au/au-citadel-auslab.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EVOLUTION')
        msh.sending_facility = HD(hd_1='SA_PATH', hd_2='1935', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='BEST_PRACTICE')
        msh.receiving_facility = HD(hd_1='WCH')
        msh.security = '20240829095500+0930'
        msh.message_control_id = 'ORU^R01'
        msh.processing_id = PT(pt_1='MSG00018')
        msh.version_id = VID(vid_1='P')
        msh.msh_13 = '2.4^AUS&&ISO3166_1^HL7AU.ONO.1&&HL7AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN5816492', cx_4='WCH', cx_5='MR'), CX(cx_1='3582916740', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='HARRIS', xpn_2='JESSICA', xpn_3='MAY', xpn_7='L')
        pid.date_time_of_birth = '19920608'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='108 Melbourne Street', xad_3='NORTH ADELAIDE', xad_4='SA', xad_5='5006', xad_6='AUS', xad_7='C')
        pid.pid_13 = '0883247196'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='WCH_OUTPAT', pl_4='WCH')
        pv1.attending_doctor = XCN(xcn_1='0463185G', xcn_2='OBI', xcn_3='CHIDI', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.referring_doctor = XCN(xcn_1='0463185G', xcn_2='OBI', xcn_3='CHIDI', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.patient_type = CWE(cwe_1='REF')
        pv1.prior_temporary_location = PL(pl_1='20240828')

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
        orc.filler_order_number = EI(ei_1='24-S890123-WCH-0', ei_2='SA_PATH', ei_3='1935', ei_4='AUSNATA')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.filler_order_number = EI(ei_1='24-S890123-WCH-0', ei_2='SA_PATH', ei_3='1935', ei_4='AUSNATA')
        obr.universal_service_identifier = CWE(cwe_1='IRON', cwe_2='IRON STUDIES', cwe_3='1935')
        obr.observation_date_time = '20240828140000+0930'
        obr.danger_code = CWE(cwe_1='Routine')
        obr.obr_14 = '20240828141500+0930'
        obr.obr_16 = '0463185G^OBI^CHIDI^^^DR^^^AUSHICPR^L^^^UPIN'
        obr.charge_to_practice = MOC(moc_1='20240829095500+0930')
        obr.parent_result = PRL(prl_1='F')
        obr.obr_33 = '0463185G^OBI^CHIDI'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2498-4', cwe_2='Iron', cwe_3='LN')
        obx.obx_5 = '5'
        obx.units = CWE(cwe_1='umol/L')
        obx.reference_range = '10-30'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240829095500+0930'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2502-3', cwe_2='Transferrin', cwe_3='LN')
        obx_2.obx_5 = '3.8'
        obx_2.units = CWE(cwe_1='g/L')
        obx_2.reference_range = '2.0-3.6'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240829095500+0930'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2500-7', cwe_2='Transferrin Saturation', cwe_3='LN')
        obx_3.obx_5 = '5'
        obx_3.units = CWE(cwe_1='%')
        obx_3.reference_range = '15-45'
        obx_3.interpretation_codes = CWE(cwe_1='LL')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240829095500+0930'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2276-4', cwe_2='Ferritin', cwe_3='LN')
        obx_4.obx_5 = '4'
        obx_4.units = CWE(cwe_1='ug/L')
        obx_4.reference_range = '20-200'
        obx_4.interpretation_codes = CWE(cwe_1='LL')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240829095500+0930'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'FT'
        obx_5.observation_identifier = CWE(cwe_1='COMMENT', cwe_2='Result Comment', cwe_3='L')
        obx_5.obx_5 = 'Iron deficiency confirmed. Ferritin <20 ug/L is diagnostic of iron depletion.'
        obx_5.probability = 'N'
        obx_5.effective_date_of_reference_range = 'F'
        obx_5.producers_id = CWE(cwe_1='20240829095500+0930')

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
    """ Based on live/au/au-citadel-auslab.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='AUSLAB')
        msh.sending_facility = HD(hd_1='QLD_HEALTH_PATH', hd_2='2567', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='HBCIS')
        msh.receiving_facility = HD(hd_1='RBWH')
        msh.security = '20240505180000+1000'
        msh.message_control_id = 'ORU^R01'
        msh.processing_id = PT(pt_1='MSG00019')
        msh.version_id = VID(vid_1='P')
        msh.msh_13 = '2.4^AUS&&ISO3166_1^HL7AU.ONO.1&&HL7AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN6927384', cx_4='RBWH', cx_5='MR'), CX(cx_1='5719283604', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='EVANS', xpn_2='DYLAN', xpn_3='HARRY', xpn_7='L')
        pid.date_time_of_birth = '19880215'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='86 Herston Road', xad_3='HERSTON', xad_4='QLD', xad_5='4006', xad_6='AUS', xad_7='C')
        pid.pid_13 = '0736329184'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='SURG_A', pl_4='RBWH')
        pv1.attending_doctor = XCN(xcn_1='0492385T', xcn_2='BAKER', xcn_3='DIANE', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.referring_doctor = XCN(xcn_1='0492385T', xcn_2='BAKER', xcn_3='DIANE', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.patient_type = CWE(cwe_1='ADM')
        pv1.prior_temporary_location = PL(pl_1='20240505')

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
        orc.filler_order_number = EI(ei_1='24-BB34567-RBWH-0', ei_2='QLD_HEALTH_PATH', ei_3='2567', ei_4='AUSNATA')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.filler_order_number = EI(ei_1='24-BB34567-RBWH-0', ei_2='QLD_HEALTH_PATH', ei_3='2567', ei_4='AUSNATA')
        obr.universal_service_identifier = CWE(cwe_1='XM', cwe_2='CROSSMATCH', cwe_3='2567')
        obr.observation_date_time = '20240505150000+1000'
        obr.danger_code = CWE(cwe_1='Urgent')
        obr.obr_14 = '20240505151000+1000'
        obr.obr_16 = '0492385T^BAKER^DIANE^^^DR^^^AUSHICPR^L^^^UPIN'
        obr.charge_to_practice = MOC(moc_1='20240505180000+1000')
        obr.parent_result = PRL(prl_1='F')
        obr.obr_32 = 'BB'
        obr.obr_33 = '0492385T^BAKER^DIANE'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='883-9', cwe_2='ABO Group', cwe_3='LN')
        obx.obx_5 = '278149003^Blood group A^SCT'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240505180000+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='10331-7', cwe_2='Rh Type', cwe_3='LN')
        obx_2.obx_5 = '165747007^Rh positive^SCT'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240505180000+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='1250-0', cwe_2='Antibody Screen', cwe_3='LN')
        obx_3.obx_5 = '260415000^Not detected^SCT'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240505180000+1000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='XMATCH', cwe_2='Crossmatch Result', cwe_3='L')
        obx_4.obx_5 = 'Compatible - 2 units RBC crossmatched'
        obx_4.probability = 'N'
        obx_4.effective_date_of_reference_range = 'F'
        obx_4.producers_id = CWE(cwe_1='20240505180000+1000')

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ED'
        obx_5.observation_identifier = CWE(cwe_1='PDF', cwe_2='Pathology Report', cwe_3='LN')
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
    """ Based on live/au/au-citadel-auslab.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CITADEL')
        msh.sending_facility = HD(hd_1='QLD_HEALTH_PATH', hd_2='2567', hd_3='AUSNATA')
        msh.receiving_application = HD(hd_1='MEDICAL_DIRECTOR')
        msh.receiving_facility = HD(hd_1='IPSWICH_MC')
        msh.security = '20241203094500+1000'
        msh.message_control_id = 'ORU^R01'
        msh.processing_id = PT(pt_1='MSG00020')
        msh.version_id = VID(vid_1='P')
        msh.msh_13 = '2.4^AUS&&ISO3166_1^HL7AU.ONO.1&&HL7AU'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MRN7419283', cx_4='IPSWICH', cx_5='MR'), CX(cx_1='3286194750', cx_4='AUSHIC', cx_5='MC')]
        pid.patient_name = XPN(xpn_1='YOUNG', xpn_2='OLIVIA', xpn_3='GRACE', xpn_7='L')
        pid.date_time_of_birth = '19930322'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='72 Limestone Street', xad_3='IPSWICH', xad_4='QLD', xad_5='4305', xad_6='AUS', xad_7='C')
        pid.pid_13 = '0738269415'
        pid.patient_death_indicator = 'N'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='IPSWICH_MC', pl_4='AUSHICPR')
        pv1.attending_doctor = XCN(xcn_1='0625148H', xcn_2='ANDERSON', xcn_3='MARK', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.referring_doctor = XCN(xcn_1='0625148H', xcn_2='ANDERSON', xcn_3='MARK', xcn_6='DR', xcn_9='AUSHICPR', xcn_10='L', xcn_13='UPIN')
        pv1.patient_type = CWE(cwe_1='REF')
        pv1.prior_temporary_location = PL(pl_1='20241128')

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
        orc.filler_order_number = EI(ei_1='24-CY78901-IPS-0', ei_2='QLD_HEALTH_PATH', ei_3='2567', ei_4='AUSNATA')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.filler_order_number = EI(ei_1='24-CY78901-IPS-0', ei_2='QLD_HEALTH_PATH', ei_3='2567', ei_4='AUSNATA')
        obr.universal_service_identifier = CWE(cwe_1='CYTO', cwe_2='CYTOPATHOLOGY', cwe_3='2567')
        obr.observation_date_time = '20241128100000+1000'
        obr.danger_code = CWE(cwe_1='Routine')
        obr.obr_14 = '20241128101500+1000'
        obr.obr_16 = '0625148H^ANDERSON^MARK^^^DR^^^AUSHICPR^L^^^UPIN'
        obr.charge_to_practice = MOC(moc_1='20241203094500+1000')
        obr.parent_result = PRL(prl_1='F')
        obr.obr_32 = 'CP'
        obr.obr_33 = '0625148H^ANDERSON^MARK'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='19762-4', cwe_2='General categories', cwe_3='LN')
        obx.obx_5 = '373887005^Negative for intraepithelial lesion or malignancy^SCT'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20241203094500+1000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='19764-0', cwe_2='Specimen adequacy', cwe_3='LN')
        obx_2.obx_5 = '17621005^Normal^SCT'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20241203094500+1000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='71431-1', cwe_2='HPV DNA', cwe_3='LN')
        obx_3.obx_5 = '260415000^Not detected^SCT'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20241203094500+1000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'FT'
        obx_4.observation_identifier = CWE(cwe_1='22637-3', cwe_2='Pathology report', cwe_3='LN')
        obx_4.obx_5 = (
            'LIQUID BASED CYTOLOGY - CERVIX\\.br\\\\.br\\CLINICAL: Routine cervical screening test.\\.br\\\\.br\\SPECIMEN: ThinPrep, satisfactory for evaluat'
            'ion.\\.br\\Endocervical component present.\\.br\\\\.br\\RESULT: Negative for intraepithelial lesion or malignancy.\\.br\\HPV DNA not detected.\\'
            '.br\\\\.br\\RECOMMENDATION: Return to routine 5-yearly screening as per National Cervical Screening Program guidelines.'
        )
        obx_4.probability = 'N'
        obx_4.effective_date_of_reference_range = 'F'
        obx_4.producers_id = CWE(cwe_1='20241203094500+1000')

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
