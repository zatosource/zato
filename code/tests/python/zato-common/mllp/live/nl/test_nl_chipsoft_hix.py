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
from zato.hl7v2.v2_9.datatypes import CWE, CX, EI, HD, MSG, OG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import OmlO21Container, OmlO21Insurance, OmlO21Observation, OmlO21ObservationPrior, OmlO21ObservationRequest, OmlO21Order, \
    OmlO21OrderPrior, OmlO21Patient, OmlO21PatientVisit, OmlO21PriorResult, OmlO21Specimen, OmlO21Timing, OmlO21TimingPrior, OruR01CommonOrder, \
    OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientObservation, OruR01PatientResult, OruR01Visit
from zato.hl7v2.v2_9.messages import OML_O21, ORU_R01
from zato.hl7v2.v2_9.segments import IN1, MSH, NTE, OBR, OBX, ORC, PID, PV1, PV2, SAC, SPM, TQ1

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('nl', 'nl-chipsoft-hix.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/nl/nl-chipsoft-hix.md, message no. 1
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
        pid.patient_name = [
            XPN(xpn_1='van den Berg&&van den Berg&&', xpn_2='Maria', xpn_7='L'),
            XPN(xpn_1='van den Berg&&van den Berg', xpn_2='Maria', xpn_7='B'),
        ]
        pid.date_time_of_birth = '19500101'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = [
            XAD(xad_1='Keizersgracht 42&Keizersgracht&42', xad_3='Amsterdam', xad_5='1015CS', xad_7='M'),
            XAD(xad_1='Keizersgracht 42&Keizersgracht&42', xad_3='Amsterdam', xad_5='1015CS', xad_7='L'),
        ]
        pid.pid_13 = '020-6234891^PRN^PH~^^^m.vandenberg@ziggo.nl'
        pid.marital_status = CWE(cwe_1='M')
        pid.birth_place = 'Nederlandse'
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
        obr.obr_16 = '3004^Brouwer'
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
    """ Based on live/nl/nl-chipsoft-hix.md, message no. 2
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
        pid.patient_name = XPN(xpn_1='Jansen&Jansen&Jansen', xpn_2='W', xpn_3='P', xpn_7='L')
        pid.date_time_of_birth = '20000101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Herengracht 88  bis&Herengracht&88', xad_2='bis', xad_3='Utrecht', xad_5='3511KP', xad_6='NL', xad_7='H')
        pid.pid_13 = '030-2314567'

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
        orc.orc_10 = '^&&het Verhoeven^D.E.F.'
        orc.orc_12 = '01004567^&&van Willems^H.J.^^^^^^VEKTIS'
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
        obr.obr_16 = '01004567^&&van Willems^H.J.^^^^^^VEKTIS'

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
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKP7/KQovQ3JlYXRvciAo/v8AdwBrAGgAdABtAGwAdABvAHAAZABmACAAMAAuADEAMgAuADIALgExKQovUH...'
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
    """ Based on live/nl/nl-chipsoft-hix.md, message no. 3
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
        pid.patient_name = XPN(xpn_1='Jansen&Jansen&Jansen', xpn_2='W', xpn_3='P', xpn_7='L')
        pid.date_time_of_birth = '20000101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Herengracht 88  bis&Herengracht&88', xad_2='bis', xad_3='Utrecht', xad_5='3511KP', xad_6='NL', xad_7='H')
        pid.pid_13 = '030-2314567_^NET^Internet^w.jansen@kpnmail.nl'

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
        orc.orc_10 = '^&&het Verhoeven^D.E.F.'
        orc.orc_12 = '01004567^&&van Willems^H.J.^^^^^^VEKTIS'
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
        obr.obr_16 = '01004567^&&van Willems^H.J.^^^^^^VEKTIS'

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
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKP7/KQovQ3JlYXRvciAo/v8AdwBrAGgAdABtAGwAdABvAHAAZABmACAAMAAuADEAMgAuADIALgExKQovUH...'
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
    """ Based on live/nl/nl-chipsoft-hix.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.msh_2 = '^_\\&'
        msh.sending_application = HD(hd_1='ZorgDomein')
        msh.date_time_of_message = '20160324163507+0100'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'ZD200046119'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_4='NLMINBIZA', cx_5='NNNLD')
        pid.patient_name = XPN(xpn_1='Jansen&Jansen&Jansen', xpn_2='W', xpn_3='P', xpn_7='L')
        pid.date_time_of_birth = '20000101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Herengracht 88  bis&Herengracht&88', xad_2='bis', xad_3='Utrecht', xad_5='3511KP', xad_6='NL', xad_7='H')
        pid.pid_13 = '030-2314567'

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
        orc.order_control = 'XO'
        orc.placer_order_number = EI(ei_1='ZD200046119')
        orc.date_time_of_order_event = '20160324163432+0100'
        orc.orc_10 = '^&&het Verhoeven^D.E.F.'
        orc.orc_12 = '01004567^&&van Willems^H.J.^^^^^^VEKTIS'
        orc.orc_14 = '015-2222222'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ZD200046119')
        obr.universal_service_identifier = CWE(cwe_1='CARCOA001', cwe_2='zorgproductcode', cwe_3='ZORGDOMEIN')
        obr.observation_date_time = '20160324163432+0100'
        obr.relevant_clinical_information = CWE(cwe_1='Mijn toelichting op de bijlagen.')
        obr.obr_16 = '01004567^&&van Willems^H.J.^^^^^^VEKTIS'
        obr.result_status = 'F'
        obr.obr_46 = (
            '^Overzicht van de bijlagen:\\.br\\De volgende bijlage(n) behorend bij de verwijzing met ZD200046119 is/zijn verzonden\\.br\\- HL7.doc\\.br\\- ZD'
            '\\R\\logo\\R\\kleur\\R\\RGB.png\\.br\\'
        )

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='BLOB', cwe_2='Bijlage', cwe_3='ZORGDOMEIN')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = '^application^msword^Base64^0M8R4KGxGuEAAAAAAAAAAAAAAAAAAAAAPgADAP7/CQAGAAAAAAAAAAAAAAABAAAALQAAAAAAAAAAEA...'
        obx.observation_result_status = 'F'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.source_of_comment = 'P'
        nte.comment = 'HL7.doc'
        nte.comment_type = CWE(cwe_1='RE')

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx
        observation.nte = nte

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='BLOB', cwe_2='Bijlage', cwe_3='ZORGDOMEIN')
        obx_2.observation_sub_id = OG(og_1='2')
        obx_2.obx_5 = '^image^png^Base64^iVBORw0KGgoAAAANSUhEUgAABJ0AAAOxCAYAAABfedaEAAAACXBIWXMAAC4jAAAuIwF4pT92AAAA...'
        obx_2.observation_result_status = 'F'

        # .. build NTE ..
        nte_2 = NTE()
        nte_2.set_id_nte = '2'
        nte_2.source_of_comment = 'P'
        nte_2.nte_3 = 'ZD\\R\\logo\\R\\kleur\\R\\RGB.png'
        nte_2.comment_type = CWE(cwe_1='RE')

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2
        observation_2.nte = nte_2

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
    """ Based on live/nl/nl-chipsoft-hix.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ZorgDomein')
        msh.date_time_of_message = '20210407153459+0200'
        msh.message_type = MSG(msg_1='OML', msg_2='O21', msg_3='OML_O21')
        msh.message_control_id = '23c517a5fc6a437cb05b'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.source_of_comment = 'P'
        nte.comment = 'KC en MMB'
        nte.comment_type = CWE(cwe_1='ZD_CLUSTER_NAME', cwe_2='ZorgDomein clusternaam', cwe_3='L')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='287654321', cx_4='NLMINBIZA', cx_5='NNNLD'), CX(cx_1='ZD234560029', cx_4='ZorgDomein', cx_5='VN')]
        pid.patient_name = XPN(xpn_1='de Vries - van der Linden&van der Linden&van der Linden&de&Vries', xpn_2='A', xpn_3='M', xpn_7='L')
        pid.date_time_of_birth = '20000101'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = [
            XAD(xad_1='Dorpsstraat 11 A&Dorpsstraat&11', xad_2='A', xad_3='Hilversum', xad_5='1211HR', xad_6='NL', xad_7='M'),
            XAD(xad_1='Molenweg 22 B&Molenweg&22', xad_2='B', xad_3='Hilversum', xad_5='1213NB', xad_6='NL', xad_7='H'),
        ]
        pid.pid_13 = '06-23456789^ORN^CP~035-6218344^PRN^PH~^NET^Internet^a.devries@gmail.com'
        pid.identity_unknown_indicator = 'Y'
        pid.identity_reliability_code = CWE(cwe_1='NNNLD')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.visit_indicator = CWE(cwe_1='V')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='LABEDG001', cwe_2='klinische chemie en medische microbiologie onderzoek', cwe_3='L')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OmlO21PatientVisit()
        patient_visit.pv1 = pv1
        patient_visit.pv2 = pv2

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_2='null')
        in1.insurance_company_id = CX(cx_1='0102', cx_4='VEKTIS', cx_5='UZOVI')
        in1.insurance_company_name = XON(xon_1='Menzis')
        in1.policy_number = '953513'

        # .. build the INSURANCE group ..
        insurance = OmlO21Insurance()
        insurance.in1 = in1

        # .. build the PATIENT group ..
        patient = OmlO21Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit
        patient.insurance = insurance

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ZD234560029')
        orc.placer_order_group_number = EI(ei_1='ZD234560029')
        orc.orc_7 = '^^^^^C'
        orc.date_time_of_order_event = '20210407153428+0200'
        orc.orc_10 = '^de Graaf^L.M.N.'
        orc.orc_12 = '01004567^van Houten^B.R.^^^^^^VEKTIS'
        orc.enterers_location = PL(pl_9='Huisartsenpraktijk De Linde, locatie Hilversum', pl_10='01012340&VEKTIS')
        orc.orc_14 = '0351234562^WPN^PH~0351234563^WPN^FX'
        orc.orc_17 = '01012341^Huisartsenpraktijk De Linde^VEKTIS'
        orc.orc_21 = 'Huisartsenpraktijk De Linde^^01012341^^^VEKTIS'
        orc.orc_22 = 'Stationsstraat 99 A&Stationsstraat&99^A^Hilversum^^1211EX^NL'
        orc.orc_23 = '0351234560^WPN^PH~0351234561^WPN^FX'

        # .. build TQ1 ..
        tq1 = TQ1()
        tq1.set_id_tq1 = '1'
        tq1.start_datetime = '20210409000000+0200'
        tq1.priority = CWE(cwe_1='C', cwe_2='Callback', cwe_3='HL70485')
        tq1.text_instruction = 'Aanvullende instructies voor materiaalafname'

        # .. build the TIMING group ..
        timing = OmlO21Timing()
        timing.tq1 = tq1

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ZD234560029')
        obr.universal_service_identifier = CWE(cwe_1='LABEDG001', cwe_2='klinische chemie en medische microbiologie', cwe_3='L')
        obr.specimen_action_code = 'L'
        obr.obr_16 = '01004567^van Houten^B.R.^^^^^^VEKTIS'
        obr.obr_17 = '0351234562^WPN^PH~0351234563^WPN^FX'
        obr.obr_28 = '01004568^Dijkstra^F.^^^^^^VEKTIS^^^^^^^Verpleeghuis Het Baken^^^^^Specialisme'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='AI', cwe_2='opmerkingen / klinische gegevens', cwe_3='L')
        obx.obx_5 = 'opmerking van verwijzer'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OmlO21Observation()
        observation.obx = obx

        # .. build ORC ..
        orc_2 = ORC()
        orc_2.order_control = 'NW'
        orc_2.placer_order_number = EI(ei_1='FUZDOMBUGYYDCMRV')
        orc_2.placer_order_group_number = EI(ei_1='ZD234560029')
        orc_2.orc_7 = '^^^^^C'
        orc_2.date_time_of_order_event = '20210407153428+0200'
        orc_2.orc_10 = '^de Graaf^L.M.N.'
        orc_2.orc_12 = '01004567^van Houten^B.R.^^^^^^VEKTIS'
        orc_2.enterers_location = PL(pl_9='Huisartsenpraktijk De Linde, locatie Hilversum', pl_10='01012340&VEKTIS')
        orc_2.orc_14 = '0351234562^WPN^PH~0351234563^WPN^FX'
        orc_2.orc_17 = '01012341^Huisartsenpraktijk De Linde^VEKTIS'
        orc_2.orc_21 = 'Huisartsenpraktijk De Linde^^01012341^^^VEKTIS'
        orc_2.orc_22 = 'Stationsstraat 99 A&Stationsstraat&99^A^Hilversum^^1211EX^NL'
        orc_2.orc_23 = '0351234560^WPN^PH~0351234561^WPN^FX'

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='FUZDOMBUGYYDCMRV')
        obr_2.universal_service_identifier = CWE(cwe_1='KC_DM2RI', cwe_2='Risico-inventarisatie', cwe_3='L')
        obr_2.specimen_action_code = 'L'
        obr_2.relevant_clinical_information = CWE(cwe_1='Diabetes Mellitus type 2 (DM)')
        obr_2.obr_16 = '01004567^van Houten^B.R.^^^^^^VEKTIS'
        obr_2.obr_17 = '0351234562^WPN^PH~0351234563^WPN^FX'
        obr_2.obr_28 = '01004568^Dijkstra^F.^^^^^^VEKTIS^^^^^^^Verpleeghuis Het Baken^^^^^Specialisme'

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '1'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='REQUESTED_TESTS', cwe_2='Aangevraagde onderzoeken', cwe_3='L')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = 'ALB^Albumine^L'
        obx_2.observation_result_status = 'O'

        # .. build the OBSERVATION_PRIOR group ..
        observation_prior = OmlO21ObservationPrior()
        observation_prior.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '2'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='REQUESTED_TESTS', cwe_2='Aangevraagde onderzoeken', cwe_3='L')
        obx_3.observation_sub_id = OG(og_1='2')
        obx_3.obx_5 = 'MALB^Albumine (micro) urine portie^L'
        obx_3.observation_result_status = 'O'

        # .. build the OBSERVATION_PRIOR group ..
        observation_prior_2 = OmlO21ObservationPrior()
        observation_prior_2.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '3'
        obx_4.value_type = 'CE'
        obx_4.observation_identifier = CWE(cwe_1='REQUESTED_TESTS', cwe_2='Aangevraagde onderzoeken', cwe_3='L')
        obx_4.observation_sub_id = OG(og_1='3')
        obx_4.obx_5 = 'KREA^Kreatinine (serum)^L'
        obx_4.observation_result_status = 'O'

        # .. build the OBSERVATION_PRIOR group ..
        observation_prior_3 = OmlO21ObservationPrior()
        observation_prior_3.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '4'
        obx_5.value_type = 'CE'
        obx_5.observation_identifier = CWE(cwe_1='REQUESTED_TESTS', cwe_2='Aangevraagde onderzoeken', cwe_3='L')
        obx_5.observation_sub_id = OG(og_1='4')
        obx_5.obx_5 = 'K24^Lipidenspectrum (Chol, HDL.Tri,...)^L'
        obx_5.observation_result_status = 'O'

        # .. build the OBSERVATION_PRIOR group ..
        observation_prior_4 = OmlO21ObservationPrior()
        observation_prior_4.obx = obx_5

        # .. build the ORDER_PRIOR group ..
        order_prior = OmlO21OrderPrior()
        order_prior.orc = orc_2
        order_prior.obr = obr_2
        order_prior.observation_prior = observation_prior
        order_prior.observation_prior_2 = observation_prior_2
        order_prior.observation_prior_3 = observation_prior_3
        order_prior.observation_prior_4 = observation_prior_4

        # .. build the PRIOR_RESULT group ..
        prior_result = OmlO21PriorResult()
        prior_result.order_prior = order_prior

        # .. build the OBSERVATION_REQUEST group ..
        observation_request = OmlO21ObservationRequest()
        observation_request.obr = obr
        observation_request.observation = observation
        observation_request.prior_result = prior_result

        # .. build the ORDER group ..
        order = OmlO21Order()
        order.orc = orc
        order.timing = timing
        order.observation_request = observation_request

        # .. assemble the full message ..
        msg = OML_O21()
        msg.msh = msh
        msg.nte = nte
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
    """ Based on live/nl/nl-chipsoft-hix.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ZorgDomein')
        msh.date_time_of_message = '20210407153459+0200'
        msh.message_type = MSG(msg_1='OML', msg_2='O21', msg_3='OML_O21')
        msh.message_control_id = '23c517a5fc6a437cb05a'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build NTE ..
        nte = NTE()
        nte.set_id_nte = '1'
        nte.source_of_comment = 'P'
        nte.comment = 'KC en MMB'
        nte.comment_type = CWE(cwe_1='ZD_CLUSTER_NAME', cwe_2='ZorgDomein clusternaam', cwe_3='L')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='398765432', cx_4='NLMINBIZA', cx_5='NNNLD'), CX(cx_1='ZD234560019', cx_4='ZorgDomein', cx_5='VN')]
        pid.patient_name = XPN(xpn_1='Bakker - van Dijk&van Dijk&van Dijk&Bakker&Bakker', xpn_2='E', xpn_3='J', xpn_7='L')
        pid.date_time_of_birth = '20000101'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(
            xad_1='Laan van Meerdervoort 18 A&Laan van Meerdervoort&18',
            xad_2='A',
            xad_3='Den Haag',
            xad_5='2517AK',
            xad_6='NL',
            xad_7='M',
        )
        pid.pid_13 = '06-87654321^ORN^CP~070-3456789^PRN^PH~^NET^Internet^e.bakker@hotmail.com'
        pid.identity_unknown_indicator = 'Y'
        pid.identity_reliability_code = CWE(cwe_1='NNNLD')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.visit_indicator = CWE(cwe_1='V')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='LABEDG001', cwe_2='klinische chemie en medische microbiologie', cwe_3='L')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OmlO21PatientVisit()
        patient_visit.pv1 = pv1
        patient_visit.pv2 = pv2

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_2='null')
        in1.insurance_company_id = CX(cx_1='0102', cx_4='VEKTIS', cx_5='UZOVI')
        in1.insurance_company_name = XON(xon_1='CZ')
        in1.policy_number = '953513'

        # .. build the INSURANCE group ..
        insurance = OmlO21Insurance()
        insurance.in1 = in1

        # .. build the PATIENT group ..
        patient = OmlO21Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit
        patient.insurance = insurance

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ZD234560019')
        orc.placer_order_group_number = EI(ei_1='ZD234560019')
        orc.orc_7 = '^^^^^C'
        orc.date_time_of_order_event = '20210407153428+0200'
        orc.orc_10 = '^de Boer^G.H.I.'
        orc.orc_12 = '01004567^van Maanen^K.L.^^^^^^VEKTIS'
        orc.enterers_location = PL(pl_9='Huisartsenpraktijk Duinzicht, locatie Scheveningen', pl_10='01012340&VEKTIS')
        orc.orc_14 = '0701234562^WPN^PH~0701234563^WPN^FX'
        orc.orc_17 = '01012341^Huisartsenpraktijk Duinzicht^VEKTIS'
        orc.orc_21 = 'Huisartsenpraktijk Duinzicht^^01012341^^^VEKTIS'
        orc.orc_22 = 'Badhuisweg 99 A&Badhuisweg&99^A^Den Haag^^2587CA^NL'
        orc.orc_23 = '0701234560^WPN^PH~0701234561^WPN^FX'

        # .. build TQ1 ..
        tq1 = TQ1()
        tq1.set_id_tq1 = '1'
        tq1.priority = CWE(cwe_1='C', cwe_2='Callback', cwe_3='HL70485')

        # .. build the TIMING group ..
        timing = OmlO21Timing()
        timing.tq1 = tq1

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ZD234560019')
        obr.universal_service_identifier = CWE(cwe_1='LABEDG001', cwe_2='klinische chemie en medische microbiologie', cwe_3='L')
        obr.collector_identifier = XCN(
            xcn_1='01004567',
            xcn_2='van Maanen',
            xcn_3='K.L.',
            xcn_9='VEKTIS',
            xcn_16='&Huisartsenpraktijk Duinzicht, locatie Scheveningen',
        )
        obr.specimen_action_code = 'O'
        obr.obr_16 = '01004567^van Maanen^K.L.^^^^^^VEKTIS'
        obr.obr_17 = '0701234562^WPN^PH~0701234563^WPN^FX'
        obr.obr_28 = '01004568^Meijer^T.^^^^^^VEKTIS^^^^^^^Verpleeghuis Duinrand^^^^^Specialisme'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='AI', cwe_2='opmerkingen / klinische gegevens', cwe_3='L')
        obx.obx_5 = 'opmerking van verwijzer'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OmlO21Observation()
        observation.obx = obx

        # .. build ORC ..
        orc_2 = ORC()
        orc_2.order_control = 'NW'
        orc_2.placer_order_number = EI(ei_1='GQ4TSNZTG4ZTSNT')
        orc_2.placer_order_group_number = EI(ei_1='ZD234560019')
        orc_2.orc_7 = '^^^^^C'
        orc_2.date_time_of_order_event = '20210407153428+0200'
        orc_2.orc_10 = '^de Boer^G.H.I.'
        orc_2.orc_12 = '01004567^van Maanen^K.L.^^^^^^VEKTIS'
        orc_2.enterers_location = PL(pl_9='Huisartsenpraktijk Duinzicht, locatie Scheveningen', pl_10='01012340&VEKTIS')
        orc_2.orc_14 = '0701234562^WPN^PH~0701234563^WPN^FX'
        orc_2.orc_17 = '01012341^Huisartsenpraktijk Duinzicht^VEKTIS'
        orc_2.orc_21 = 'Huisartsenpraktijk Duinzicht^^01012341^^^VEKTIS'
        orc_2.orc_22 = 'Badhuisweg 99 A&Badhuisweg&99^A^Den Haag^^2587CA^NL'
        orc_2.orc_23 = '0701234560^WPN^PH~0701234561^WPN^FX'

        # .. build TQ1 ..
        tq1_2 = TQ1()
        tq1_2.set_id_tq1 = '1'
        tq1_2.priority = CWE(cwe_1='C', cwe_2='Callback', cwe_3='HL70485')

        # .. build the TIMING_PRIOR group ..
        timing_prior = OmlO21TimingPrior()
        timing_prior.tq1 = tq1_2

        # .. build the ORDER_PRIOR group ..
        order_prior = OmlO21OrderPrior()
        order_prior.orc = orc_2
        order_prior.timing_prior = timing_prior

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='GQ4TSNZTG4ZTSNT')
        obr_2.universal_service_identifier = CWE(cwe_1='MMB_LWI', cwe_2='Luchtweginfecties (MMB)', cwe_3='L')
        obr_2.collector_identifier = XCN(
            xcn_1='01004567',
            xcn_2='van Maanen',
            xcn_3='K.L.',
            xcn_9='VEKTIS',
            xcn_16='&Huisartsenpraktijk Duinzicht, locatie Scheveningen',
        )
        obr_2.specimen_action_code = 'O'
        obr_2.relevant_clinical_information = CWE(cwe_1='Microbiologisch onderzoek')
        obr_2.obr_16 = '01004567^van Maanen^K.L.^^^^^^VEKTIS'
        obr_2.obr_17 = '0701234562^WPN^PH~0701234563^WPN^FX'
        obr_2.obr_28 = '01004568^Meijer^T.^^^^^^VEKTIS^^^^^^^Verpleeghuis Duinrand^^^^^Specialisme'

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '1'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='REQUESTED_TESTS', cwe_2='Aangevraagde onderzoeken', cwe_3='L')
        obx_2.observation_sub_id = OG(og_1='1')
        obx_2.obx_5 = 'BAN_KWK_SPT^Alg. bacterieel^L'
        obx_2.observation_result_status = 'O'

        # .. build the OBSERVATION_PRIOR group ..
        observation_prior = OmlO21ObservationPrior()
        observation_prior.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '2'
        obx_3.value_type = 'CE'
        obx_3.observation_identifier = CWE(cwe_1='REQUESTED_TESTS', cwe_2='Aangevraagde onderzoeken', cwe_3='L')
        obx_3.observation_sub_id = OG(og_1='2')
        obx_3.obx_5 = 'BRDPER_SER_BLD^Bordetella pertussis (kinkhoest)^L'
        obx_3.observation_result_status = 'O'

        # .. build the OBSERVATION_PRIOR group ..
        observation_prior_2 = OmlO21ObservationPrior()
        observation_prior_2.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '3'
        obx_4.value_type = 'CE'
        obx_4.observation_identifier = CWE(cwe_1='REQUESTED_TESTS', cwe_2='Aangevraagde onderzoeken', cwe_3='L')
        obx_4.observation_sub_id = OG(og_1='3')
        obx_4.obx_5 = 'INFLRSV_PCR_SPT^Influenza A/B en RSV sputum^L'
        obx_4.observation_result_status = 'O'

        # .. build the OBSERVATION_PRIOR group ..
        observation_prior_3 = OmlO21ObservationPrior()
        observation_prior_3.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '4'
        obx_5.value_type = 'CE'
        obx_5.observation_identifier = CWE(cwe_1='REQUESTED_TESTS', cwe_2='Aangevraagde onderzoeken', cwe_3='L')
        obx_5.observation_sub_id = OG(og_1='4')
        obx_5.obx_5 = 'RESP_PCR_SPT^Respiratoir pakket sputum (Influenza, RSV+breed pakket LWI verwekkers)^L'
        obx_5.observation_result_status = 'O'

        # .. build the OBSERVATION_PRIOR group ..
        observation_prior_4 = OmlO21ObservationPrior()
        observation_prior_4.obx = obx_5

        # .. build the ORDER_PRIOR group ..
        order_prior_2 = OmlO21OrderPrior()
        order_prior_2.obr = obr_2
        order_prior_2.observation_prior = observation_prior
        order_prior_2.observation_prior_2 = observation_prior_2
        order_prior_2.observation_prior_3 = observation_prior_3
        order_prior_2.observation_prior_4 = observation_prior_4

        # .. build ORC ..
        orc_3 = ORC()
        orc_3.order_control = 'NW'
        orc_3.placer_order_number = EI(ei_1='FUYTMMBVGIYTMOJZHY')
        orc_3.placer_order_group_number = EI(ei_1='ZD234560019')
        orc_3.orc_7 = '^^^^^C'
        orc_3.date_time_of_order_event = '20210407153428+0200'
        orc_3.orc_10 = '^de Boer^G.H.I.'
        orc_3.orc_12 = '01004567^van Maanen^K.L.^^^^^^VEKTIS'
        orc_3.enterers_location = PL(pl_9='Huisartsenpraktijk Duinzicht, locatie Scheveningen', pl_10='01012340&VEKTIS')
        orc_3.orc_14 = '0701234562^WPN^PH~0701234563^WPN^FX'
        orc_3.orc_17 = '01012341^Huisartsenpraktijk Duinzicht^VEKTIS'
        orc_3.orc_21 = 'Huisartsenpraktijk Duinzicht^^01012341^^^VEKTIS'
        orc_3.orc_22 = 'Badhuisweg 99 A&Badhuisweg&99^A^Den Haag^^2587CA^NL'
        orc_3.orc_23 = '0701234560^WPN^PH~0701234561^WPN^FX'

        # .. build TQ1 ..
        tq1_3 = TQ1()
        tq1_3.set_id_tq1 = '1'
        tq1_3.priority = CWE(cwe_1='C', cwe_2='Callback', cwe_3='HL70485')

        # .. build the TIMING_PRIOR group ..
        timing_prior_2 = OmlO21TimingPrior()
        timing_prior_2.tq1 = tq1_3

        # .. build the ORDER_PRIOR group ..
        order_prior_3 = OmlO21OrderPrior()
        order_prior_3.orc = orc_3
        order_prior_3.timing_prior = timing_prior_2

        # .. build OBR ..
        obr_3 = OBR()
        obr_3.set_id_obr = '3'
        obr_3.placer_order_number = EI(ei_1='FUYTMMBVGIYTMOJZHY')
        obr_3.universal_service_identifier = CWE(cwe_1='MMB_MRSASCR', cwe_2='Meticilline resistente Staphylococcus aureus MRSA screening (MMB)', cwe_3='L')
        obr_3.collector_identifier = XCN(
            xcn_1='01004567',
            xcn_2='van Maanen',
            xcn_3='K.L.',
            xcn_9='VEKTIS',
            xcn_16='&Huisartsenpraktijk Duinzicht, locatie Scheveningen',
        )
        obr_3.specimen_action_code = 'O'
        obr_3.relevant_clinical_information = CWE(cwe_1='Microbiologisch onderzoek')
        obr_3.obr_16 = '01004567^van Maanen^K.L.^^^^^^VEKTIS'
        obr_3.obr_17 = '0701234562^WPN^PH~0701234563^WPN^FX'
        obr_3.obr_28 = '01004568^Meijer^T.^^^^^^VEKTIS^^^^^^^Verpleeghuis Duinrand^^^^^Specialisme'

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '1'
        obx_6.value_type = 'CE'
        obx_6.observation_identifier = CWE(cwe_1='REQUESTED_TESTS', cwe_2='Aangevraagde onderzoeken', cwe_3='L')
        obx_6.observation_sub_id = OG(og_1='1')
        obx_6.obx_5 = 'MRSA_KWK_SWTASP^Methicilline Resistente Staphylococcus aureus - MRSA^L'
        obx_6.observation_result_status = 'O'

        # .. build the OBSERVATION_PRIOR group ..
        observation_prior_5 = OmlO21ObservationPrior()
        observation_prior_5.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '2'
        obx_7.value_type = 'CE'
        obx_7.observation_identifier = CWE(cwe_1='REQUESTED_TESTS', cwe_2='Aangevraagde onderzoeken', cwe_3='L')
        obx_7.observation_sub_id = OG(og_1='2')
        obx_7.obx_5 = 'MRSA_KWK_SWNOSE^Methicilline Resistente Staphylococcus aureus - MRSA^L'
        obx_7.observation_result_status = 'O'

        # .. build the OBSERVATION_PRIOR group ..
        observation_prior_6 = OmlO21ObservationPrior()
        observation_prior_6.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '3'
        obx_8.value_type = 'CE'
        obx_8.observation_identifier = CWE(cwe_1='REQUESTED_TESTS', cwe_2='Aangevraagde onderzoeken', cwe_3='L')
        obx_8.observation_sub_id = OG(og_1='3')
        obx_8.obx_5 = 'MRSA_KWK_SWPRNM^Methicilline Resistente Staphylococcus aureus - MRSA^L'
        obx_8.observation_result_status = 'O'

        # .. build the OBSERVATION_PRIOR group ..
        observation_prior_7 = OmlO21ObservationPrior()
        observation_prior_7.obx = obx_8

        # .. build the ORDER_PRIOR group ..
        order_prior_4 = OmlO21OrderPrior()
        order_prior_4.obr = obr_3
        order_prior_4.observation_prior = observation_prior_5
        order_prior_4.observation_prior_2 = observation_prior_6
        order_prior_4.observation_prior_3 = observation_prior_7

        # .. build the PRIOR_RESULT group ..
        prior_result = OmlO21PriorResult()
        prior_result.order_prior = order_prior
        prior_result.order_prior_2 = order_prior_2
        prior_result.order_prior_3 = order_prior_3
        prior_result.order_prior_4 = order_prior_4

        # .. build the OBSERVATION_REQUEST group ..
        observation_request = OmlO21ObservationRequest()
        observation_request.obr = obr
        observation_request.observation = observation
        observation_request.prior_result = prior_result

        # .. build the ORDER group ..
        order = OmlO21Order()
        order.orc = orc
        order.timing = timing
        order.observation_request = observation_request

        # .. assemble the full message ..
        msg = OML_O21()
        msg.msh = msh
        msg.nte = nte
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
    """ Based on live/nl/nl-chipsoft-hix.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ZorgDomein')
        msh.date_time_of_message = '20170215153459+0100'
        msh.message_type = MSG(msg_1='OML', msg_2='O21', msg_3='OML_O21')
        msh.message_control_id = '23c517a5fc6a437cb05a'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='456789123', cx_4='NLMINBIZA', cx_5='NNNLD'), CX(cx_1='ZD200160319', cx_4='ZorgDomein', cx_5='VN')]
        pid.patient_name = XPN(xpn_1='Mulder - van Leeuwen&van Leeuwen&van Leeuwen&Mulder&Mulder', xpn_2='C', xpn_3='H', xpn_7='L')
        pid.date_time_of_birth = '20000101'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Nieuwstraat 18 A&Nieuwstraat&18', xad_2='A', xad_3='Deventer', xad_5='7411LG', xad_6='NL', xad_7='M')
        pid.pid_13 = '06-98765432^ORN^CP~0570-612345^PRN^PH'
        pid.identity_unknown_indicator = 'Y'
        pid.identity_reliability_code = CWE(cwe_1='NNNLD')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.visit_indicator = CWE(cwe_1='V')

        # .. build PV2 ..
        pv2 = PV2()
        pv2.admit_reason = CWE(cwe_1='LABEDG001', cwe_2='laboratorium onderzoek', cwe_3='99zda')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OmlO21PatientVisit()
        patient_visit.pv1 = pv1
        patient_visit.pv2 = pv2

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_2='null')
        in1.insurance_company_id = CX(cx_1='0102', cx_4='VEKTIS', cx_5='UZOVI')
        in1.insurance_company_name = XON(xon_1='ONVZ')
        in1.policy_number = '953513'

        # .. build the INSURANCE group ..
        insurance = OmlO21Insurance()
        insurance.in1 = in1

        # .. build the PATIENT group ..
        patient = OmlO21Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit
        patient.insurance = insurance

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ZD200160319_01BLD')
        orc.placer_order_group_number = EI(ei_1='ZD200160319')
        orc.date_time_of_order_event = '20170215153428+0100'
        orc.orc_10 = '^het Vermeer^P.Q.R.'
        orc.orc_12 = '01004567^van Beek^M.N.^^^^^^VEKTIS'
        orc.enterers_location = PL(pl_4='IO SWV huisartspraktijk 1&01058765', pl_9='IO SWV huisartspraktijk 123')
        orc.orc_17 = '01058765^IO SWV huisartspraktijk 1^VEKTIS'
        orc.orc_21 = 'IO SWV huisartspraktijk 1^^01058765^^^VEKTIS'

        # .. build TQ1 ..
        tq1 = TQ1()
        tq1.set_id_tq1 = '1'
        tq1.priority = CWE(cwe_1='R')

        # .. build the TIMING group ..
        timing = OmlO21Timing()
        timing.tq1 = tq1

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ZD200160319_01BLD')
        obr.universal_service_identifier = CWE(cwe_1='CA01', cwe_2='Calcium', cwe_3='99zdl')
        obr.specimen_action_code = 'O'
        obr.obr_16 = '01004567^van Beek^M.N.^^^^^^VEKTIS'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CE'
        obx.observation_identifier = CWE(cwe_1='Vraagcode', cwe_3='99zda')
        obx.obx_5 = 'Code1^Keuze1^99zda'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OmlO21Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CE'
        obx_2.observation_identifier = CWE(cwe_1='codeMultiselectVraag123', cwe_3='99zdl')
        obx_2.obx_5 = 'MultiC22^Multi2^99zdl~MultiC33^Multi3^99zdl'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OmlO21Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='AI', cwe_2='opmerkingen / klinische gegevens', cwe_3='99zda')
        obx_3.obx_5 = 'opmerking van verwijzer'
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OmlO21Observation()
        observation_3.obx = obx_3

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_type = CWE(cwe_1='BLD', cwe_2='Bloed', cwe_3='99zda')

        # .. build SAC ..
        sac = SAC()
        sac.container_identifier = EI(ei_1='CodeReageerbuis', ei_2='Reageerbuis')

        # .. build the CONTAINER group ..
        container = OmlO21Container()
        container.sac = sac

        # .. build the SPECIMEN group ..
        specimen = OmlO21Specimen()
        specimen.spm = spm
        specimen.container = container

        # .. build ORC ..
        orc_2 = ORC()
        orc_2.order_control = 'NW'
        orc_2.placer_order_number = EI(ei_1='ZD200160319_02BLD')
        orc_2.placer_order_group_number = EI(ei_1='ZD200160319')
        orc_2.date_time_of_order_event = '20170215160258+0100'
        orc_2.orc_10 = '^het Vermeer^P.Q.R.'
        orc_2.orc_12 = '01004567^van Beek^M.N.^^^^^^VEKTIS'
        orc_2.enterers_location = PL(pl_4='IO SWV huisartspraktijk 1&01058765', pl_9='IO SWV huisartspraktijk 123')
        orc_2.orc_17 = '01058765^IO SWV huisartspraktijk 1^VEKTIS'
        orc_2.orc_21 = 'IO SWV huisartspraktijk 1^^01058765^^^VEKTIS'

        # .. build TQ1 ..
        tq1_2 = TQ1()
        tq1_2.set_id_tq1 = '2'
        tq1_2.priority = CWE(cwe_1='R')

        # .. build the TIMING_PRIOR group ..
        timing_prior = OmlO21TimingPrior()
        timing_prior.tq1 = tq1_2

        # .. build the ORDER_PRIOR group ..
        order_prior = OmlO21OrderPrior()
        order_prior.orc = orc_2
        order_prior.timing_prior = timing_prior

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='ZD200160319_02BLD')
        obr_2.universal_service_identifier = CWE(cwe_1='HE01', cwe_2='Hemoglobine', cwe_3='99zdl')
        obr_2.specimen_action_code = 'O'
        obr_2.obr_16 = '01004567^van Beek^M.N.^^^^^^VEKTIS'

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '1'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='AI', cwe_2='opmerkingen / klinische gegevens', cwe_3='99zda')
        obx_4.obx_5 = 'opmerking van verwijzer'
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION_PRIOR group ..
        observation_prior = OmlO21ObservationPrior()
        observation_prior.obx = obx_4

        # .. build the ORDER_PRIOR group ..
        order_prior_2 = OmlO21OrderPrior()
        order_prior_2.obr = obr_2
        order_prior_2.observation_prior = observation_prior

        # .. build the PRIOR_RESULT group ..
        prior_result = OmlO21PriorResult()
        prior_result.order_prior = order_prior
        prior_result.order_prior_2 = order_prior_2

        # .. build the OBSERVATION_REQUEST group ..
        observation_request = OmlO21ObservationRequest()
        observation_request.obr = obr
        observation_request.observation = observation
        observation_request.observation_2 = observation_2
        observation_request.observation_3 = observation_3
        observation_request.specimen = specimen
        observation_request.prior_result = prior_result

        # .. build the ORDER group ..
        order = OmlO21Order()
        order.orc = orc
        order.timing = timing
        order.observation_request = observation_request

        # .. build SPM ..
        spm_2 = SPM()
        spm_2.set_id_spm = '1'
        spm_2.specimen_type = CWE(cwe_1='BLD', cwe_2='Bloed', cwe_3='99zda')

        # .. assemble the full message ..
        msg = OML_O21()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [spm_2]

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

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
