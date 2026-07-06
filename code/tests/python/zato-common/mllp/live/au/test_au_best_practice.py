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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, HD, MSG, PL, PT, VID, XAD, XCN, XPN
from zato.hl7v2.v2_9.groups import AdtA05NextOfKin, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, \
    OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, RefI12ProviderContact
from zato.hl7v2.v2_9.messages import ADT_A05, ORM_O01, ORU_R01, REF_I12
from zato.hl7v2.v2_9.segments import DG1, EVN, MSH, NK1, NTE, OBR, OBX, ORC, PID, PRD, PV1, RF1

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('au', 'au-best-practice.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/au/au-best-practice.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DOREVITCH')
        msh.sending_facility = HD(hd_1='DOREVITCH PATHOLOGY')
        msh.receiving_application = HD(hd_1='BPPREMIER')
        msh.receiving_facility = HD(hd_1='GLENROY MEDICAL CENTRE')
        msh.date_time_of_message = '20240315090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MC4185729364', cx_4='AUSHIC', cx_5='MC'), CX(cx_1='PAS81472', cx_4='DOREVITCH', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='MITCHELL', xpn_2='BARBARA', xpn_3='LOUISE', xpn_5='MRS')
        pid.date_time_of_birth = '19580312'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='37 Pascoe Vale Road', xad_3='GLENROY', xad_4='VIC', xad_5='3046', xad_6='AUS')
        pid.pid_13 = '0393056218^PRN^PH~0418274639^PRN^CP'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='GLENROY MEDICAL CENTRE')
        pv1.attending_doctor = XCN(xcn_1='0782341A', xcn_2='WALKER', xcn_3='STEPHEN', xcn_6='DR')
        pv1.patient_type = CWE(cwe_1='V452918')

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
        orc.placer_order_number = EI(ei_1='ORD2024031501')
        orc.filler_order_number = EI(ei_1='LAB2024031501')
        orc.order_status = 'CM'
        orc.orc_12 = '0782341A^WALKER^STEPHEN^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2024031501')
        obr.filler_order_number = EI(ei_1='LAB2024031501')
        obr.universal_service_identifier = CWE(cwe_1='26604007', cwe_2='Full Blood Count', cwe_3='SCT')
        obr.observation_date_time = '20240314080000'
        obr.obr_14 = '20240314080000'
        obr.obr_16 = '0782341A^WALKER^STEPHEN^^^DR'
        obr.results_rpt_status_chng_date_time = '20240315090000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Haemoglobin', cwe_3='LN')
        obx.obx_5 = '138'
        obx.units = CWE(cwe_1='g/L')
        obx.reference_range = '120-160'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240315090000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='Red Cell Count', cwe_3='LN')
        obx_2.obx_5 = '4.52'
        obx_2.obx_6 = 'x10\\S\\12/L'
        obx_2.reference_range = '3.80-5.20'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240315090000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='787-2', cwe_2='MCV', cwe_3='LN')
        obx_3.obx_5 = '88.2'
        obx_3.units = CWE(cwe_1='fL')
        obx_3.reference_range = '80.0-100.0'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240315090000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='6690-2', cwe_2='White Cell Count', cwe_3='LN')
        obx_4.obx_5 = '6.8'
        obx_4.obx_6 = 'x10\\S\\9/L'
        obx_4.reference_range = '4.0-11.0'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240315090000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='777-3', cwe_2='Platelet Count', cwe_3='LN')
        obx_5.obx_5 = '245'
        obx_5.obx_6 = 'x10\\S\\9/L'
        obx_5.reference_range = '150-400'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20240315090000'

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
    """ Based on live/au/au-best-practice.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='QML')
        msh.sending_facility = HD(hd_1='QML PATHOLOGY')
        msh.receiving_application = HD(hd_1='BP')
        msh.receiving_facility = HD(hd_1='CHERMSIDE FAMILY PRACTICE')
        msh.date_time_of_message = '20240410143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MSG00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MC5294163807', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='EDWARDS', xpn_2='GREGORY', xpn_3='MARTIN', xpn_5='MR')
        pid.date_time_of_birth = '19651118'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='52 Hamilton Road', xad_3='CHERMSIDE', xad_4='QLD', xad_5='4032', xad_6='AUS')
        pid.pid_13 = '0738461572^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='CHERMSIDE FAMILY PRACTICE')
        pv1.attending_doctor = XCN(xcn_1='0631925B', xcn_2='HARRIS', xcn_3='DEBORAH', xcn_6='DR')

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
        orc.placer_order_number = EI(ei_1='ORD2024041001')
        orc.filler_order_number = EI(ei_1='QML2024041001')
        orc.order_status = 'CM'
        orc.orc_12 = '0631925B^HARRIS^DEBORAH^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2024041001')
        obr.filler_order_number = EI(ei_1='QML2024041001')
        obr.universal_service_identifier = CWE(cwe_1='24331-1', cwe_2='Lipid Studies', cwe_3='LN')
        obr.observation_date_time = '20240409070000'
        obr.obr_14 = '20240409070000'
        obr.obr_16 = '0631925B^HARRIS^DEBORAH^^^DR'
        obr.results_rpt_status_chng_date_time = '20240410143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2093-3', cwe_2='Total Cholesterol', cwe_3='LN')
        obx.obx_5 = '6.2'
        obx.units = CWE(cwe_1='mmol/L')
        obx.reference_range = '<5.5'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240410143000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2571-8', cwe_2='Triglycerides', cwe_3='LN')
        obx_2.obx_5 = '1.8'
        obx_2.units = CWE(cwe_1='mmol/L')
        obx_2.reference_range = '<2.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240410143000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2085-9', cwe_2='HDL Cholesterol', cwe_3='LN')
        obx_3.obx_5 = '1.3'
        obx_3.units = CWE(cwe_1='mmol/L')
        obx_3.reference_range = '>1.0'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240410143000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='13457-7', cwe_2='LDL Cholesterol', cwe_3='LN')
        obx_4.obx_5 = '4.1'
        obx_4.units = CWE(cwe_1='mmol/L')
        obx_4.reference_range = '<3.5'
        obx_4.interpretation_codes = CWE(cwe_1='H')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240410143000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='13458-5', cwe_2='Chol/HDL Ratio', cwe_3='LN')
        obx_5.obx_5 = '4.8'
        obx_5.reference_range = '<4.5'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20240410143000'

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
    """ Based on live/au/au-best-practice.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SULLIVAN_NICOLAIDES')
        msh.sending_facility = HD(hd_1='SNP')
        msh.receiving_application = HD(hd_1='BESTPRACTICE')
        msh.receiving_facility = HD(hd_1='MOOROOKA HEALTH CENTRE')
        msh.date_time_of_message = '20240520110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MC6403852714', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='CHEN', xpn_2='JIA', xpn_3='WEN', xpn_5='MS')
        pid.date_time_of_birth = '19820724'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='14/26 Beaudesert Road', xad_3='MOOROOKA', xad_4='QLD', xad_5='4105', xad_6='AUS')
        pid.pid_13 = '0738152904^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='MOOROOKA HEALTH CENTRE')
        pv1.attending_doctor = XCN(xcn_1='0759384C', xcn_2='ROBERTS', xcn_3='CATHERINE', xcn_6='DR')

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
        orc.placer_order_number = EI(ei_1='ORD2024052001')
        orc.filler_order_number = EI(ei_1='SNP2024052001')
        orc.order_status = 'CM'
        orc.orc_12 = '0759384C^ROBERTS^CATHERINE^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2024052001')
        obr.filler_order_number = EI(ei_1='SNP2024052001')
        obr.universal_service_identifier = CWE(cwe_1='11502-2', cwe_2='Laboratory Report', cwe_3='LN')
        obr.observation_date_time = '20240519090000'
        obr.obr_14 = '20240519090000'
        obr.obr_16 = '0759384C^ROBERTS^CATHERINE^^^DR'
        obr.results_rpt_status_chng_date_time = '20240520110000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='PDF', cwe_2='Pathology Report', cwe_3='LN')
        obx.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMg'
            'MCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5'
            'IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo='
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
    """ Based on live/au/au-best-practice.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MELBOURNE_PATHOLOGY')
        msh.sending_facility = HD(hd_1='MELB PATH')
        msh.receiving_application = HD(hd_1='BPPREMIER')
        msh.receiving_facility = HD(hd_1='FOOTSCRAY MEDICAL')
        msh.date_time_of_message = '20240622155000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MC7518293046', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='PHILLIPS', xpn_2='DOROTHY', xpn_3='MAY', xpn_5='MRS')
        pid.date_time_of_birth = '19470209'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='9 Hopkins Street', xad_3='FOOTSCRAY', xad_4='VIC', xad_5='3011', xad_6='AUS')
        pid.pid_13 = '0396854271^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='FOOTSCRAY MEDICAL')
        pv1.attending_doctor = XCN(xcn_1='0846173D', xcn_2='CAMPBELL', xcn_3='IAN', xcn_6='DR')

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
        orc.placer_order_number = EI(ei_1='ORD2024062201')
        orc.filler_order_number = EI(ei_1='MP2024062201')
        orc.order_status = 'CM'
        orc.orc_12 = '0846173D^CAMPBELL^IAN^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2024062201')
        obr.filler_order_number = EI(ei_1='MP2024062201')
        obr.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='Haemoglobin A1c', cwe_3='LN')
        obr.observation_date_time = '20240621080000'
        obr.obr_14 = '20240621080000'
        obr.obr_16 = '0846173D^CAMPBELL^IAN^^^DR'
        obr.results_rpt_status_chng_date_time = '20240622155000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obx.obx_5 = '7.2'
        obx.units = CWE(cwe_1='%')
        obx.reference_range = '<6.5'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240622155000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='59261-8', cwe_2='HbA1c (IFCC)', cwe_3='LN')
        obx_2.obx_5 = '55'
        obx_2.units = CWE(cwe_1='mmol/mol')
        obx_2.reference_range = '<48'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240622155000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'FT'
        obx_3.observation_identifier = CWE(cwe_1='8251-1', cwe_2='Comment', cwe_3='LN')
        obx_3.obx_5 = 'HbA1c is above target range. Consider medication review.'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240622155000'

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
    """ Based on live/au/au-best-practice.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DOREVITCH')
        msh.sending_facility = HD(hd_1='DOREVITCH PATHOLOGY')
        msh.receiving_application = HD(hd_1='BP')
        msh.receiving_facility = HD(hd_1='MORNINGTON BEACH CLINIC')
        msh.date_time_of_message = '20240718083000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MSG00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MC8629305147', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='COLLINS', xpn_2='ANTHONY', xpn_3='GERARD', xpn_5='MR')
        pid.date_time_of_birth = '19730515'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='118 Main Street', xad_3='MORNINGTON', xad_4='VIC', xad_5='3931', xad_6='AUS')
        pid.pid_13 = '0395971842^PRN^PH~0427183564^PRN^CP'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='MORNINGTON BEACH CLINIC')
        pv1.attending_doctor = XCN(xcn_1='0937261E', xcn_2='YOUNG', xcn_3='REBECCA', xcn_6='DR')

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
        orc.placer_order_number = EI(ei_1='ORD2024071801')
        orc.filler_order_number = EI(ei_1='DOR2024071801')
        orc.order_status = 'CM'
        orc.orc_12 = '0937261E^YOUNG^REBECCA^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2024071801')
        obr.filler_order_number = EI(ei_1='DOR2024071801')
        obr.universal_service_identifier = CWE(cwe_1='24348-5', cwe_2='Thyroid Function', cwe_3='LN')
        obr.observation_date_time = '20240717070000'
        obr.obr_14 = '20240717070000'
        obr.obr_16 = '0937261E^YOUNG^REBECCA^^^DR'
        obr.results_rpt_status_chng_date_time = '20240718083000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='3016-3', cwe_2='TSH', cwe_3='LN')
        obx.obx_5 = '5.8'
        obx.units = CWE(cwe_1='mIU/L')
        obx.reference_range = '0.5-4.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240718083000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='3024-7', cwe_2='Free T4', cwe_3='LN')
        obx_2.obx_5 = '11.2'
        obx_2.units = CWE(cwe_1='pmol/L')
        obx_2.reference_range = '10.0-20.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240718083000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3053-6', cwe_2='Free T3', cwe_3='LN')
        obx_3.obx_5 = '4.1'
        obx_3.units = CWE(cwe_1='pmol/L')
        obx_3.reference_range = '3.5-6.5'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240718083000'

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
    """ Based on live/au/au-best-practice.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BPPREMIER')
        msh.sending_facility = HD(hd_1='HORNSBY VALLEY MEDICAL')
        msh.receiving_application = HD(hd_1='BESTPRACTICE')
        msh.receiving_facility = HD(hd_1='NORTH SHORE HEART SPECIALISTS')
        msh.date_time_of_message = '20240801140000'
        msh.message_type = MSG(msg_1='REF', msg_2='I12', msg_3='REF_I12')
        msh.message_control_id = 'MSG00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build RF1 ..
        rf1 = RF1()
        rf1.referral_status = CWE(cwe_1='SS')
        rf1.referral_priority = CWE(cwe_1='RP')
        rf1.referral_type = CWE(cwe_1='GRF')
        rf1.referral_category = CWE(cwe_1='R')
        rf1.originating_referral_identifier = EI(ei_1='20240801140000')
        rf1.effective_date = '20240901'
        rf1.expiration_date = 'Cardiac assessment - exertional chest pain'

        # .. build PRD ..
        prd = PRD()
        prd.provider_role = CWE(cwe_1='RP')
        prd.provider_name = XPN(xpn_1='REED', xpn_2='MARTIN', xpn_3='DOUGLAS', xpn_5='DR')
        prd.provider_address = XAD(xad_1='41 Pacific Highway', xad_3='HORNSBY', xad_4='NSW', xad_5='2077', xad_6='AUS')
        prd.provider_location = PL(pl_4='HORNSBY VALLEY MEDICAL')
        prd.preferred_method_of_contact = CWE(cwe_1='1043572F')

        # .. build the PROVIDER_CONTACT group ..
        provider_contact = RefI12ProviderContact()
        provider_contact.prd = prd

        # .. build PRD ..
        prd_2 = PRD()
        prd_2.provider_role = CWE(cwe_1='RT')
        prd_2.provider_name = XPN(xpn_1='SINGH', xpn_2='AMARJIT', xpn_5='DR')
        prd_2.provider_address = XAD(xad_1='214 Pacific Highway', xad_3='ST LEONARDS', xad_4='NSW', xad_5='2065', xad_6='AUS')
        prd_2.provider_location = PL(pl_4='NORTH SHORE HEART SPECIALISTS')
        prd_2.preferred_method_of_contact = CWE(cwe_1='0461938G')

        # .. build the PROVIDER_CONTACT group ..
        provider_contact_2 = RefI12ProviderContact()
        provider_contact_2.prd = prd_2

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MC9740268351', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='COOK', xpn_2='WAYNE', xpn_3='FREDERICK', xpn_5='MR')
        pid.date_time_of_birth = '19590823'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='66 Galston Road', xad_3='HORNSBY', xad_4='NSW', xad_5='2077', xad_6='AUS')
        pid.pid_13 = '0294762813^PRN^PH'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I20.9', cwe_2='Angina pectoris, unspecified', cwe_3='I10')
        dg1.diagnosis_date_time = '20240801'
        dg1.diagnosis_type = CWE(cwe_1='W')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = (
            'Patient reports exertional chest pain over the past 3 weeks, relieved by rest. Family history of IHD (father MI age 52). Current medications'
            ': Atorvastatin 40mg nocte, Aspirin 100mg mane. Please assess and advise re stress testing.'
        )

        # .. assemble the full message ..
        msg = REF_I12()
        msg.msh = msh
        msg.rf1 = rf1
        msg.provider_contact = [provider_contact, provider_contact_2]
        msg.pid = pid
        msg.dg1 = dg1
        msg.nte = nte

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
    """ Based on live/au/au-best-practice.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='QML')
        msh.sending_facility = HD(hd_1='QML PATHOLOGY')
        msh.receiving_application = HD(hd_1='BPPREMIER')
        msh.receiving_facility = HD(hd_1='REDCLIFFE BAYSIDE PRACTICE')
        msh.date_time_of_message = '20240903091500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MC1062847593', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='PARKER', xpn_2='SAMANTHA', xpn_3='JANE', xpn_5='MS')
        pid.date_time_of_birth = '19910614'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='23 Anzac Avenue', xad_3='REDCLIFFE', xad_4='QLD', xad_5='4020', xad_6='AUS')
        pid.pid_13 = '0738264915^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='REDCLIFFE BAYSIDE PRACTICE')
        pv1.attending_doctor = XCN(xcn_1='1158493H', xcn_2='WRIGHT', xcn_3='JEFFREY', xcn_6='DR')

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
        orc.placer_order_number = EI(ei_1='ORD2024090301')
        orc.filler_order_number = EI(ei_1='QML2024090301')
        orc.order_status = 'CM'
        orc.orc_12 = '1158493H^WRIGHT^JEFFREY^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2024090301')
        obr.filler_order_number = EI(ei_1='QML2024090301')
        obr.universal_service_identifier = CWE(cwe_1='630-4', cwe_2='Urine MCS', cwe_3='LN')
        obr.observation_date_time = '20240902100000'
        obr.obr_14 = '20240902100000'
        obr.obr_16 = '1158493H^WRIGHT^JEFFREY^^^DR'
        obr.results_rpt_status_chng_date_time = '20240903091500'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='5799-2', cwe_2='Macroscopic', cwe_3='LN')
        obx.obx_5 = 'Turbid'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240903091500'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='5794-3', cwe_2='WBC', cwe_3='LN')
        obx_2.obx_5 = '>100'
        obx_2.obx_6 = 'x10\\S\\6/L'
        obx_2.reference_range = '<10'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240903091500'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'FT'
        obx_3.observation_identifier = CWE(cwe_1='5769-5', cwe_2='Organisms', cwe_3='LN')
        obx_3.obx_5 = 'Escherichia coli >10\\S\\8 CFU/L'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240903091500'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'FT'
        obx_4.observation_identifier = CWE(cwe_1='18868-0', cwe_2='Ampicillin', cwe_3='LN')
        obx_4.obx_5 = 'Resistant'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240903091500'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'FT'
        obx_5.observation_identifier = CWE(cwe_1='18878-9', cwe_2='Cephalexin', cwe_3='LN')
        obx_5.obx_5 = 'Sensitive'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20240903091500'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'FT'
        obx_6.observation_identifier = CWE(cwe_1='18906-8', cwe_2='Trimethoprim', cwe_3='LN')
        obx_6.obx_5 = 'Sensitive'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20240903091500'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'FT'
        obx_7.observation_identifier = CWE(cwe_1='18895-3', cwe_2='Nitrofurantoin', cwe_3='LN')
        obx_7.obx_5 = 'Sensitive'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20240903091500'

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
    """ Based on live/au/au-best-practice.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BPPREMIER')
        msh.sending_facility = HD(hd_1='NEWTOWN KING ST CLINIC')
        msh.receiving_application = HD(hd_1='BPPREMIER')
        msh.receiving_facility = HD(hd_1='NEWTOWN KING ST CLINIC')
        msh.date_time_of_message = '20240115100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A28', msg_3='ADT_A05')
        msh.message_control_id = 'MSG00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A28'
        evn.recorded_date_time = '20240115100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MC1183750492', cx_4='AUSHIC', cx_5='MC'), CX(cx_1='NKS00729', cx_4='NEWTOWN KING ST CLINIC', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='TURNER', xpn_2='ALICE', xpn_3='EVELYN', xpn_5='MS')
        pid.date_time_of_birth = '19880302'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='5/142 King Street', xad_3='NEWTOWN', xad_4='NSW', xad_5='2042', xad_6='AUS')
        pid.pid_13 = '0295631827^PRN^PH~0438619274^PRN^CP'
        pid.primary_language = CWE(cwe_1='EN')
        pid.veterans_military_status = CWE(cwe_1='N')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='TURNER', xpn_2='DANIEL', xpn_3='OLIVER', xpn_5='MR')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Spouse')
        nk1.address = XAD(xad_1='5/142 King Street', xad_3='NEWTOWN', xad_4='NSW', xad_5='2042', xad_6='AUS')
        nk1.nk1_5 = '0438276913^PRN^CP'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA05NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='NEWTOWN KING ST CLINIC')
        pv1.attending_doctor = XCN(xcn_1='1276184J', xcn_2='BAKER', xcn_3='JULIA', xcn_6='DR')

        # .. assemble the full message ..
        msg = ADT_A05()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
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
    """ Based on live/au/au-best-practice.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DOREVITCH')
        msh.sending_facility = HD(hd_1='DOREVITCH PATHOLOGY')
        msh.receiving_application = HD(hd_1='BESTPRACTICE')
        msh.receiving_facility = HD(hd_1="FITZROY WOMEN'S HEALTH")
        msh.date_time_of_message = '20240225160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MC1294683571', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='LEE', xpn_2='EUNJI', xpn_3='MIN', xpn_5='MS')
        pid.date_time_of_birth = '19850919'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='2/87 Brunswick Street', xad_3='FITZROY', xad_4='VIC', xad_5='3065', xad_6='AUS')
        pid.pid_13 = '0394175826^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4="FITZROY WOMEN'S HEALTH")
        pv1.attending_doctor = XCN(xcn_1='1389275K', xcn_2='EVANS', xcn_3='MELISSA', xcn_6='DR')

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
        orc.placer_order_number = EI(ei_1='ORD2024022501')
        orc.filler_order_number = EI(ei_1='DOR2024022501')
        orc.order_status = 'CM'
        orc.orc_12 = '1389275K^EVANS^MELISSA^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2024022501')
        obr.filler_order_number = EI(ei_1='DOR2024022501')
        obr.universal_service_identifier = CWE(cwe_1='21440-3', cwe_2='HPV DNA', cwe_3='LN')
        obr.observation_date_time = '20240224110000'
        obr.obr_14 = '20240224110000'
        obr.obr_16 = '1389275K^EVANS^MELISSA^^^DR'
        obr.results_rpt_status_chng_date_time = '20240225160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='21440-3', cwe_2='HPV DNA Test', cwe_3='LN')
        obx.obx_5 = '260385009^Negative^SCT'
        obx.reference_range = 'Negative'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240225160000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'FT'
        obx_2.observation_identifier = CWE(cwe_1='19774-9', cwe_2='Cytology', cwe_3='LN')
        obx_2.obx_5 = 'No oncogenic HPV DNA detected. Recommend routine re-screening in 5 years as per NCSP guidelines.'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240225160000'

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
    """ Based on live/au/au-best-practice.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SULLIVAN_NICOLAIDES')
        msh.sending_facility = HD(hd_1='SNP')
        msh.receiving_application = HD(hd_1='BP')
        msh.receiving_facility = HD(hd_1='MOUNT GRAVATT FAMILY MEDICAL')
        msh.date_time_of_message = '20240430112000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MSG00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MC1305827649', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='MORRIS', xpn_2='DOUGLAS', xpn_3='EDWARD', xpn_5='MR')
        pid.date_time_of_birth = '19681103'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='172 Logan Road', xad_3='MOUNT GRAVATT', xad_4='QLD', xad_5='4122', xad_6='AUS')
        pid.pid_13 = '0734918672^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='MOUNT GRAVATT FAMILY MEDICAL')
        pv1.attending_doctor = XCN(xcn_1='1492368L', xcn_2='BENNETT', xcn_3='GORDON', xcn_6='DR')

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
        orc.placer_order_number = EI(ei_1='ORD2024043001')
        orc.filler_order_number = EI(ei_1='SNP2024043001')
        orc.order_status = 'CM'
        orc.orc_12 = '1492368L^BENNETT^GORDON^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2024043001')
        obr.filler_order_number = EI(ei_1='SNP2024043001')
        obr.universal_service_identifier = CWE(cwe_1='24325-3', cwe_2='Liver Function', cwe_3='LN')
        obr.observation_date_time = '20240429070000'
        obr.obr_14 = '20240429070000'
        obr.obr_16 = '1492368L^BENNETT^GORDON^^^DR'
        obr.results_rpt_status_chng_date_time = '20240430112000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALT', cwe_3='LN')
        obx.obx_5 = '38'
        obx.units = CWE(cwe_1='U/L')
        obx.reference_range = '<40'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240430112000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='1920-8', cwe_2='AST', cwe_3='LN')
        obx_2.obx_5 = '32'
        obx_2.units = CWE(cwe_1='U/L')
        obx_2.reference_range = '<35'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240430112000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2324-2', cwe_2='GGT', cwe_3='LN')
        obx_3.obx_5 = '95'
        obx_3.units = CWE(cwe_1='U/L')
        obx_3.reference_range = '<60'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240430112000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='1975-2', cwe_2='Bilirubin Total', cwe_3='LN')
        obx_4.obx_5 = '12'
        obx_4.units = CWE(cwe_1='umol/L')
        obx_4.reference_range = '<20'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240430112000'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='1751-7', cwe_2='Albumin', cwe_3='LN')
        obx_5.obx_5 = '42'
        obx_5.units = CWE(cwe_1='g/L')
        obx_5.reference_range = '35-50'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20240430112000'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2885-2', cwe_2='Total Protein', cwe_3='LN')
        obx_6.obx_5 = '71'
        obx_6.units = CWE(cwe_1='g/L')
        obx_6.reference_range = '60-80'
        obx_6.observation_result_status = 'F'
        obx_6.date_time_of_the_observation = '20240430112000'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='6768-6', cwe_2='ALP', cwe_3='LN')
        obx_7.obx_5 = '78'
        obx_7.units = CWE(cwe_1='U/L')
        obx_7.reference_range = '30-110'
        obx_7.observation_result_status = 'F'
        obx_7.date_time_of_the_observation = '20240430112000'

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
    """ Based on live/au/au-best-practice.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BPPREMIER')
        msh.sending_facility = HD(hd_1='PROSPECT FAMILY DOCTORS')
        msh.receiving_application = HD(hd_1='DOREVITCH')
        msh.receiving_facility = HD(hd_1='DOREVITCH PATHOLOGY')
        msh.date_time_of_message = '20240305080000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MSG00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MC1416982357', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='SCOTT', xpn_2='HEATHER', xpn_3='MAREE', xpn_5='MRS')
        pid.date_time_of_birth = '19710628'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='33 Main North Road', xad_3='PROSPECT', xad_4='SA', xad_5='5082', xad_6='AUS')
        pid.pid_13 = '0883462718^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='PROSPECT FAMILY DOCTORS')
        pv1.attending_doctor = XCN(xcn_1='1583704M', xcn_2='PATEL', xcn_3='NIKHIL', xcn_6='DR')

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
        orc.placer_order_number = EI(ei_1='ORD2024030501')
        orc.order_status = 'IP'
        orc.orc_12 = '1583704M^PATEL^NIKHIL^^^DR'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2024030501')
        obr.universal_service_identifier = CWE(cwe_1='14749-6', cwe_2='Fasting Glucose', cwe_3='LN')
        obr.observation_date_time = '20240306070000'
        obr.relevant_clinical_information = CWE(cwe_1='Fasting specimen required')
        obr.obr_14 = '20240306070000'
        obr.obr_15 = '&Blood'
        obr.obr_16 = '1583704M^PATEL^NIKHIL^^^DR'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc
        order.order_detail = order_detail

        # .. build ORC ..
        orc_2 = ORC()
        orc_2.order_control = 'NW'
        orc_2.placer_order_number = EI(ei_1='ORD2024030502')
        orc_2.order_status = 'IP'
        orc_2.orc_12 = '1583704M^PATEL^NIKHIL^^^DR'

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='ORD2024030502')
        obr_2.universal_service_identifier = CWE(cwe_1='4548-4', cwe_2='HbA1c', cwe_3='LN')
        obr_2.observation_date_time = '20240306070000'
        obr_2.obr_14 = '20240306070000'
        obr_2.obr_15 = '&Blood'
        obr_2.obr_16 = '1583704M^PATEL^NIKHIL^^^DR'

        # .. build the ORDER_DETAIL group ..
        order_detail_2 = OrmO01OrderDetail()
        order_detail_2.obr = obr_2

        # .. build the ORDER group ..
        order_2 = OrmO01Order()
        order_2.orc = orc_2
        order_2.order_detail = order_detail_2

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = [order, order_2]

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
    """ Based on live/au/au-best-practice.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='I-MED')
        msh.sending_facility = HD(hd_1='I-MED RADIOLOGY')
        msh.receiving_application = HD(hd_1='BPPREMIER')
        msh.receiving_facility = HD(hd_1='RESERVOIR FAMILY MEDICAL')
        msh.date_time_of_message = '20240612143000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MC1527306841', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='GRAY', xpn_2='FRANCIS', xpn_3='DOMENICO', xpn_5='MR')
        pid.date_time_of_birth = '19550411'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='48 Spring Street', xad_3='RESERVOIR', xad_4='VIC', xad_5='3073', xad_6='AUS')
        pid.pid_13 = '0394627158^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='RESERVOIR FAMILY MEDICAL')
        pv1.attending_doctor = XCN(xcn_1='1697415N', xcn_2='MURPHY', xcn_3='LOUISE', xcn_6='DR')

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
        orc.placer_order_number = EI(ei_1='ORD2024061201')
        orc.filler_order_number = EI(ei_1='IMED2024061201')
        orc.order_status = 'CM'
        orc.orc_12 = '1697415N^MURPHY^LOUISE^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2024061201')
        obr.filler_order_number = EI(ei_1='IMED2024061201')
        obr.universal_service_identifier = CWE(cwe_1='24558-9', cwe_2='Chest X-Ray PA', cwe_3='LN')
        obr.observation_date_time = '20240611150000'
        obr.obr_14 = '20240611150000'
        obr.obr_16 = '1697415N^MURPHY^LOUISE^^^DR'
        obr.results_rpt_status_chng_date_time = '20240612143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='24558-9', cwe_2='Report', cwe_3='LN')
        obx.obx_5 = (
            'CHEST X-RAY PA\\.br\\Clinical Details: Persistent cough 3 weeks\\.br\\\\.br\\Findings:\\.br\\Heart size normal. Lungs clear. No focal consolidation '
            'or effusion.\\.br\\No bony abnormality detected.\\.br\\\\.br\\Conclusion: Normal chest X-ray.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240612143000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Radiology Report', cwe_3='LN')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMg'
            'MCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5'
            'IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240612143000'

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
    """ Based on live/au/au-best-practice.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BPPREMIER')
        msh.sending_facility = HD(hd_1='GLEBE POINT MEDICAL')
        msh.receiving_application = HD(hd_1='BPPREMIER')
        msh.receiving_facility = HD(hd_1='GLEBE POINT MEDICAL')
        msh.date_time_of_message = '20240820093000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        msh.message_control_id = 'MSG00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A31'
        evn.recorded_date_time = '20240820093000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='MC1638572904', cx_4='AUSHIC', cx_5='MC'), CX(cx_1='GPM02147', cx_4='GLEBE POINT MEDICAL', cx_5='MR')]
        pid.patient_name = XPN(xpn_1='NGUYEN', xpn_2='HUONG', xpn_3='THI', xpn_5='MS')
        pid.date_time_of_birth = '19930517'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='3/52 Glebe Point Road', xad_3='GLEBE', xad_4='NSW', xad_5='2037', xad_6='AUS')
        pid.pid_13 = '0295721643^PRN^PH~0447813295^PRN^CP'
        pid.primary_language = CWE(cwe_1='VI')
        pid.veterans_military_status = CWE(cwe_1='N')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='GLEBE POINT MEDICAL')
        pv1.attending_doctor = XCN(xcn_1='1738624P', xcn_2='HILL', xcn_3='MATTHEW', xcn_6='DR')

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
    """ Based on live/au/au-best-practice.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='QML')
        msh.sending_facility = HD(hd_1='QML PATHOLOGY')
        msh.receiving_application = HD(hd_1='BESTPRACTICE')
        msh.receiving_facility = HD(hd_1='CARINDALE FAMILY HEALTH')
        msh.date_time_of_message = '20241001141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MC1749683215', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='PATEL', xpn_2='PRIYA', xpn_3='DEVI', xpn_5='MRS')
        pid.date_time_of_birth = '19870103'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='95 Old Cleveland Road', xad_3='CARINDALE', xad_4='QLD', xad_5='4152', xad_6='AUS')
        pid.pid_13 = '0734918265^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='CARINDALE FAMILY HEALTH')
        pv1.attending_doctor = XCN(xcn_1='1846927Q', xcn_2='WARD', xcn_3='TIMOTHY', xcn_6='DR')

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
        orc.placer_order_number = EI(ei_1='ORD2024100101')
        orc.filler_order_number = EI(ei_1='QML2024100101')
        orc.order_status = 'CM'
        orc.orc_12 = '1846927Q^WARD^TIMOTHY^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2024100101')
        obr.filler_order_number = EI(ei_1='QML2024100101')
        obr.universal_service_identifier = CWE(cwe_1='2498-4', cwe_2='Iron Studies', cwe_3='LN')
        obr.observation_date_time = '20240930070000'
        obr.obr_14 = '20240930070000'
        obr.obr_16 = '1846927Q^WARD^TIMOTHY^^^DR'
        obr.results_rpt_status_chng_date_time = '20241001141500'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2498-4', cwe_2='Serum Iron', cwe_3='LN')
        obx.obx_5 = '5'
        obx.units = CWE(cwe_1='umol/L')
        obx.reference_range = '10-30'
        obx.interpretation_codes = CWE(cwe_1='L')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20241001141500'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2499-2', cwe_2='Transferrin', cwe_3='LN')
        obx_2.obx_5 = '3.8'
        obx_2.units = CWE(cwe_1='g/L')
        obx_2.reference_range = '2.0-3.6'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20241001141500'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='2500-7', cwe_2='Transferrin Saturation', cwe_3='LN')
        obx_3.obx_5 = '8'
        obx_3.units = CWE(cwe_1='%')
        obx_3.reference_range = '15-45'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20241001141500'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2276-4', cwe_2='Ferritin', cwe_3='LN')
        obx_4.obx_5 = '6'
        obx_4.units = CWE(cwe_1='ug/L')
        obx_4.reference_range = '20-200'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20241001141500'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'FT'
        obx_5.observation_identifier = CWE(cwe_1='8251-1', cwe_2='Comment', cwe_3='LN')
        obx_5.obx_5 = 'Iron deficiency confirmed. Clinical correlation recommended.'
        obx_5.observation_result_status = 'F'
        obx_5.date_time_of_the_observation = '20241001141500'

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
    """ Based on live/au/au-best-practice.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BPPREMIER')
        msh.sending_facility = HD(hd_1='EARLWOOD VILLAGE PRACTICE')
        msh.receiving_application = HD(hd_1='BESTPRACTICE')
        msh.receiving_facility = HD(hd_1='BURWOOD GASTRO ASSOCIATES')
        msh.date_time_of_message = '20240710090000'
        msh.message_type = MSG(msg_1='REF', msg_2='I12', msg_3='REF_I12')
        msh.message_control_id = 'MSG00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build RF1 ..
        rf1 = RF1()
        rf1.referral_status = CWE(cwe_1='SS')
        rf1.referral_priority = CWE(cwe_1='RP')
        rf1.referral_type = CWE(cwe_1='GRF')
        rf1.referral_category = CWE(cwe_1='R')
        rf1.originating_referral_identifier = EI(ei_1='20240710090000')
        rf1.effective_date = '20240810'
        rf1.expiration_date = 'Colonoscopy - positive FIT result'

        # .. build PRD ..
        prd = PRD()
        prd.provider_role = CWE(cwe_1='RP')
        prd.provider_name = XPN(xpn_1='JAMES', xpn_2='GRAHAM', xpn_3='STEWART', xpn_5='DR')
        prd.provider_address = XAD(xad_1='112 Homer Street', xad_3='EARLWOOD', xad_4='NSW', xad_5='2206', xad_6='AUS')
        prd.provider_location = PL(pl_4='EARLWOOD VILLAGE PRACTICE')
        prd.preferred_method_of_contact = CWE(cwe_1='1958247R')

        # .. build the PROVIDER_CONTACT group ..
        provider_contact = RefI12ProviderContact()
        provider_contact.prd = prd

        # .. build PRD ..
        prd_2 = PRD()
        prd_2.provider_role = CWE(cwe_1='RT')
        prd_2.provider_name = XPN(xpn_1='TANG', xpn_2='WEI', xpn_5='DR')
        prd_2.provider_address = XAD(xad_1='7 Burwood Road', xad_3='BURWOOD', xad_4='NSW', xad_5='2134', xad_6='AUS')
        prd_2.provider_location = PL(pl_4='BURWOOD GASTRO ASSOCIATES')
        prd_2.preferred_method_of_contact = CWE(cwe_1='0672893S')

        # .. build the PROVIDER_CONTACT group ..
        provider_contact_2 = RefI12ProviderContact()
        provider_contact_2.prd = prd_2

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MC1858392641', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='BAILEY', xpn_2='TERRENCE', xpn_3='ROBERT', xpn_5='MR')
        pid.date_time_of_birth = '19620215'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='29 William Street', xad_3='EARLWOOD', xad_4='NSW', xad_5='2206', xad_6='AUS')
        pid.pid_13 = '0297824361^PRN^PH'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='K63.5', cwe_2='Polyp of colon', cwe_3='I10')
        dg1.diagnosis_date_time = '20240710'
        dg1.diagnosis_type = CWE(cwe_1='W')

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.comment = (
            'Patient returned positive FIT on routine NBCSP screening. No rectal bleeding, no weight loss, no change in bowel habit. Family history: moth'
            'er had colon cancer age 68. Please arrange colonoscopy at your earliest convenience.'
        )

        # .. assemble the full message ..
        msg = REF_I12()
        msg.msh = msh
        msg.rf1 = rf1
        msg.provider_contact = [provider_contact, provider_contact_2]
        msg.pid = pid
        msg.dg1 = dg1
        msg.nte = nte

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
    """ Based on live/au/au-best-practice.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='MELBOURNE_PATHOLOGY')
        msh.sending_facility = HD(hd_1='MELB PATH')
        msh.receiving_application = HD(hd_1='BP')
        msh.receiving_facility = HD(hd_1='HAMPTON BAYSIDE PRACTICE')
        msh.date_time_of_message = '20241115102000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MSG00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MC1968253047', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='CLARK', xpn_2='STANLEY', xpn_3='WALTER', xpn_5='MR')
        pid.date_time_of_birth = '19580720'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='14 Hampton Street', xad_3='HAMPTON', xad_4='VIC', xad_5='3188', xad_6='AUS')
        pid.pid_13 = '0395216843^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='HAMPTON BAYSIDE PRACTICE')
        pv1.attending_doctor = XCN(xcn_1='2057318T', xcn_2='DIAZ', xcn_3='FERNANDO', xcn_6='DR')

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
        orc.placer_order_number = EI(ei_1='ORD2024111501')
        orc.filler_order_number = EI(ei_1='MP2024111501')
        orc.order_status = 'CM'
        orc.orc_12 = '2057318T^DIAZ^FERNANDO^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2024111501')
        obr.filler_order_number = EI(ei_1='MP2024111501')
        obr.universal_service_identifier = CWE(cwe_1='2857-1', cwe_2='PSA', cwe_3='LN')
        obr.observation_date_time = '20241114080000'
        obr.obr_14 = '20241114080000'
        obr.obr_16 = '2057318T^DIAZ^FERNANDO^^^DR'
        obr.results_rpt_status_chng_date_time = '20241115102000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2857-1', cwe_2='PSA Total', cwe_3='LN')
        obx.obx_5 = '3.2'
        obx.units = CWE(cwe_1='ug/L')
        obx.reference_range = '<4.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20241115102000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='10886-0', cwe_2='PSA Free', cwe_3='LN')
        obx_2.obx_5 = '0.9'
        obx_2.units = CWE(cwe_1='ug/L')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20241115102000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='12841-3', cwe_2='Free/Total PSA Ratio', cwe_3='LN')
        obx_3.obx_5 = '28'
        obx_3.units = CWE(cwe_1='%')
        obx_3.reference_range = '>25'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20241115102000'

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
    """ Based on live/au/au-best-practice.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DOREVITCH')
        msh.sending_facility = HD(hd_1='DOREVITCH PATHOLOGY')
        msh.receiving_application = HD(hd_1='BPPREMIER')
        msh.receiving_facility = HD(hd_1='BENDIGO CENTRAL MEDICAL')
        msh.date_time_of_message = '20240508140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MC2079462851', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='RICHARDSON', xpn_2='BERYL', xpn_3='MAVIS', xpn_5='MRS')
        pid.date_time_of_birth = '19420918'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='21 View Street', xad_3='BENDIGO', xad_4='VIC', xad_5='3550', xad_6='AUS')
        pid.pid_13 = '0354418293^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='BENDIGO CENTRAL MEDICAL')
        pv1.attending_doctor = XCN(xcn_1='2168459U', xcn_2='KELLY', xcn_3='DONALD', xcn_6='DR')

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
        orc.placer_order_number = EI(ei_1='ORD2024050801')
        orc.filler_order_number = EI(ei_1='DOR2024050801')
        orc.order_status = 'CM'
        orc.orc_12 = '2168459U^KELLY^DONALD^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2024050801')
        obr.filler_order_number = EI(ei_1='DOR2024050801')
        obr.universal_service_identifier = CWE(cwe_1='5902-2', cwe_2='Coagulation', cwe_3='LN')
        obr.observation_date_time = '20240508090000'
        obr.obr_14 = '20240508090000'
        obr.obr_16 = '2168459U^KELLY^DONALD^^^DR'
        obr.results_rpt_status_chng_date_time = '20240508140000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='5902-2', cwe_2='INR', cwe_3='LN')
        obx.obx_5 = '2.8'
        obx.reference_range = '2.0-3.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240508140000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='5894-1', cwe_2='PT', cwe_3='LN')
        obx_2.obx_5 = '28.5'
        obx_2.units = CWE(cwe_1='seconds')
        obx_2.reference_range = '11.0-15.0'
        obx_2.interpretation_codes = CWE(cwe_1='H')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240508140000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'FT'
        obx_3.observation_identifier = CWE(cwe_1='8251-1', cwe_2='Comment', cwe_3='LN')
        obx_3.obx_5 = 'INR within therapeutic range for atrial fibrillation. Continue warfarin 4mg daily. Next INR in 4 weeks.'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240508140000'

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
    """ Based on live/au/au-best-practice.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SULLIVAN_NICOLAIDES')
        msh.sending_facility = HD(hd_1='SNP')
        msh.receiving_application = HD(hd_1='BESTPRACTICE')
        msh.receiving_facility = HD(hd_1='TOOWOOMBA RANGE FAMILY DOCTORS')
        msh.date_time_of_message = '20240912110000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MC2186403957', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='COX', xpn_2='NATALIE', xpn_3='ROSE', xpn_5='MRS')
        pid.date_time_of_birth = '19920811'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='58 Margaret Street', xad_3='TOOWOOMBA', xad_4='QLD', xad_5='4350', xad_6='AUS')
        pid.pid_13 = '0746183527^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='TOOWOOMBA RANGE FAMILY DOCTORS')
        pv1.attending_doctor = XCN(xcn_1='2274916V', xcn_2='HOWARD', xcn_3='GILLIAN', xcn_6='DR')

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
        orc.placer_order_number = EI(ei_1='ORD2024091201')
        orc.filler_order_number = EI(ei_1='SNP2024091201')
        orc.order_status = 'CM'
        orc.orc_12 = '2274916V^HOWARD^GILLIAN^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2024091201')
        obr.filler_order_number = EI(ei_1='SNP2024091201')
        obr.universal_service_identifier = CWE(cwe_1='48767-8', cwe_2='First Trimester Screen', cwe_3='LN')
        obr.observation_date_time = '20240911090000'
        obr.obr_14 = '20240911090000'
        obr.obr_16 = '2274916V^HOWARD^GILLIAN^^^DR'
        obr.results_rpt_status_chng_date_time = '20240912110000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='48803-1', cwe_2='PAPP-A', cwe_3='LN')
        obx.obx_5 = '1.2'
        obx.units = CWE(cwe_1='MoM')
        obx.reference_range = '0.5-2.0'
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20240912110000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='48802-3', cwe_2='Free Beta hCG', cwe_3='LN')
        obx_2.obx_5 = '0.9'
        obx_2.units = CWE(cwe_1='MoM')
        obx_2.reference_range = '0.5-2.0'
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20240912110000'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='11878-6', cwe_2='NT Measurement', cwe_3='LN')
        obx_3.obx_5 = '1.3'
        obx_3.units = CWE(cwe_1='mm')
        obx_3.reference_range = '<3.5'
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20240912110000'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'FT'
        obx_4.observation_identifier = CWE(cwe_1='8251-1', cwe_2='Risk Assessment', cwe_3='LN')
        obx_4.obx_5 = 'Combined first trimester risk for Trisomy 21: 1 in 8500 (low risk). Trisomy 18: 1 in 20000 (low risk). Recommend routine antenatal care.'
        obx_4.observation_result_status = 'F'
        obx_4.date_time_of_the_observation = '20240912110000'

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
    """ Based on live/au/au-best-practice.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='BPPREMIER')
        msh.sending_facility = HD(hd_1='MAYLANDS COMMUNITY MEDICAL')
        msh.receiving_application = HD(hd_1='I-MED')
        msh.receiving_facility = HD(hd_1='I-MED RADIOLOGY')
        msh.date_time_of_message = '20241020083000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01', msg_3='ORM_O01')
        msh.message_control_id = 'MSG00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MC2298516437', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='ADAMS', xpn_2='CHRISTOPHER', xpn_3='MARK', xpn_5='MR')
        pid.date_time_of_birth = '19780304'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='91 Eighth Avenue', xad_3='MAYLANDS', xad_4='WA', xad_5='6051', xad_6='AUS')
        pid.pid_13 = '0892736418^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='MAYLANDS COMMUNITY MEDICAL')
        pv1.attending_doctor = XCN(xcn_1='2384617W', xcn_2='WANG', xcn_3='XIULAN', xcn_6='DR')

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
        orc.placer_order_number = EI(ei_1='ORD2024102001')
        orc.order_status = 'IP'
        orc.orc_12 = '2384617W^WANG^XIULAN^^^DR'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2024102001')
        obr.universal_service_identifier = CWE(cwe_1='24970-5', cwe_2='Lumbar Spine X-Ray', cwe_3='LN')
        obr.observation_date_time = '20241021090000'
        obr.relevant_clinical_information = CWE(cwe_1='Chronic low back pain 6 weeks, no red flags. Rule out degenerative changes.')
        obr.obr_14 = '20241021090000'
        obr.obr_16 = '2384617W^WANG^XIULAN^^^DR'

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
    """ Based on live/au/au-best-practice.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='DOREVITCH')
        msh.sending_facility = HD(hd_1='DOREVITCH PATHOLOGY')
        msh.receiving_application = HD(hd_1='BPPREMIER')
        msh.receiving_facility = HD(hd_1='BRIGHTON BEACH MEDICAL')
        msh.date_time_of_message = '20241203160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'AUS'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MC2417652398', cx_4='AUSHIC', cx_5='MC')
        pid.patient_name = XPN(xpn_1='LEWIS', xpn_2='BRADLEY', xpn_3='STEVEN', xpn_5='MR')
        pid.date_time_of_birth = '19650827'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='37 Bay Street', xad_3='BRIGHTON', xad_4='VIC', xad_5='3186', xad_6='AUS')
        pid.pid_13 = '0395923741^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_4='BRIGHTON BEACH MEDICAL')
        pv1.attending_doctor = XCN(xcn_1='2495172X', xcn_2='GREEN', xcn_3='OLIVIA', xcn_6='DR')

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
        orc.placer_order_number = EI(ei_1='ORD2024120301')
        orc.filler_order_number = EI(ei_1='DOR2024120301')
        orc.order_status = 'CM'
        orc.orc_12 = '2495172X^GREEN^OLIVIA^^^DR'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD2024120301')
        obr.filler_order_number = EI(ei_1='DOR2024120301')
        obr.universal_service_identifier = CWE(cwe_1='22049-1', cwe_2='Histopathology', cwe_3='LN')
        obr.observation_date_time = '20241128140000'
        obr.obr_14 = '20241128140000'
        obr.obr_16 = '2495172X^GREEN^OLIVIA^^^DR'
        obr.results_rpt_status_chng_date_time = '20241203160000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='22637-3', cwe_2='Report', cwe_3='LN')
        obx.obx_5 = (
            'HISTOPATHOLOGY REPORT\\.br\\\\.br\\Specimen: Punch biopsy left forearm\\.br\\\\.br\\Macroscopic: Skin punch biopsy 4mm diameter, 3mm depth.\\.br\\\\.br'
            '\\Microscopic: Sections show a basal cell carcinoma, nodular type, extending to a depth of 1.8mm. Deep and lateral margins clear (nearest mar'
            'gin 0.5mm lateral).\\.br\\\\.br\\Diagnosis: Basal cell carcinoma, nodular type, margins clear.'
        )
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20241203160000'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Histopathology Report', cwe_3='LN')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKFRlc3QgRG9jdW1lbnQpCi9Qcm9kdWNlciAoVGVzdCkKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDMg'
            'MCBSCj4+CmVuZG9iagozIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovQ291bnQgMAovS2lkcyBbXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5'
            'IDAwMDAwIG4gCjAwMDAwMDAwOTYgMDAwMDAgbiAKMDAwMDAwMDE0NSAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMiAwIFIKPj4Kc3RhcnR4cmVmCjIwNQolJUVPRgo='
        )
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20241203160000'

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
