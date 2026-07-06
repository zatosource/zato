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
from zato.hl7v2.v2_9.datatypes import CWE, CX, DLD, EI, HD, MOC, MSG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, OmlO21ObservationPrior, OmlO21ObservationRequest, OmlO21Order, OmlO21OrderPrior, OmlO21Patient, \
    OmlO21PatientVisit, OmlO21PriorResult, OmlO21Specimen, OrmO01Insurance, OrmO01Observation, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, \
    OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientObservation, OruR01PatientResult, \
    OruR01Visit, OulR22CommonOrder, OulR22Order, OulR22OrderDocument, OulR22Patient, OulR22Result, OulR22Specimen, OulR22Visit
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, OML_O21, ORL_O22, ORM_O01, ORU_R01, OUL_R22
from zato.hl7v2.v2_9.segments import EVN, IN1, MSA, MSH, NK1, OBR, OBX, ORC, PID, PV1, SPM

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('nl', 'nl-nen7504.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/nl/nl-nen7504.md, message no. 1
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
        pid.patient_identifier_list = [CX(cx_1='1234567', cx_5='PI'), CX(cx_1='328917456', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = [XPN(xpn_1='Bakker&&Bakker&&', xpn_2='Margaretha', xpn_7='L'), XPN(xpn_1='Bakker&&Bakker', xpn_2='Margaretha', xpn_7='B')]
        pid.date_time_of_birth = '19500101'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = [
            XAD(xad_1='Alderstraat 1&Alderstraat&1', xad_3='Jipsinghuizen', xad_5='1234AB', xad_7='M'),
            XAD(xad_1='Alderstraat 1&Alderstraat&1', xad_3='Jipsinghuizen', xad_5='1234AB', xad_7='L'),
        ]
        pid.pid_13 = '010-1234567^PRN^PH~^^^Margaretha@example.com'
        pid.marital_status = CWE(cwe_1='M')
        pid.birth_place = 'Aalst'
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
        obr.obr_16 = '3004^van den Ende'
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
    """ Based on live/nl/nl-nen7504.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIMS_SENDER')
        msh.sending_facility = HD(hd_1='LAB_UITBESTEDEND')
        msh.receiving_application = HD(hd_1='LIMS_RECEIVER')
        msh.receiving_facility = HD(hd_1='LAB_INBESTEDEND')
        msh.date_time_of_message = '20220315091200'
        msh.message_type = MSG(msg_1='OML', msg_2='O21', msg_3='OML_O21')
        msh.message_control_id = 'MSG20220315001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.4.3.11.60.25.10.1', ei_2='NICTIZ', ei_3='ISO')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='ANON123', cx_5='PI'), CX(cx_1='462918375', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Jansen', xpn_2='Pieter', xpn_3='H')
        pid.date_time_of_birth = '19680312'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Oudegracht 45', xad_3='Utrecht', xad_5='3511AX', xad_6='NL')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MICRO', pl_2='LAB1', pl_3='01', pl_4='LAB_UITBESTEDEND')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OmlO21PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OmlO21Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD001', ei_2='LIMS_SENDER')
        orc.orc_7 = '1^^^20220315091200^^R'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD001', ei_2='LIMS_SENDER')
        obr.universal_service_identifier = CWE(cwe_1='29576-6', cwe_2='Bacterial susceptibility panel', cwe_3='LN')
        obr.observation_date_time = '20220315080000'
        obr.relevant_clinical_information = CWE(cwe_1='Urineweginfectie, verdenking ESBL')
        obr.obr_16 = '1234^de Groot^Willem^^^arts'
        obr.results_rpt_status_chng_date_time = '20220315091200'

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_type = CWE(cwe_1='UR', cwe_2='Urine', cwe_3='HL70487')
        spm.specimen_risk_code = CWE(cwe_1='20220314153000')

        # .. build the SPECIMEN group ..
        specimen = OmlO21Specimen()
        specimen.spm = spm

        # .. build OBR ..
        obr_2 = OBR()
        obr_2.set_id_obr = '2'
        obr_2.placer_order_number = EI(ei_1='ORD001-P1', ei_2='LIMS_SENDER')
        obr_2.universal_service_identifier = CWE(cwe_1='634-6', cwe_2='Bacteria identified', cwe_3='LN')
        obr_2.observation_date_time = '20220314160000'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='634-6', cwe_2='Bacteria identified', cwe_3='LN')
        obx.obx_5 = '112283007^Escherichia coli^SCT'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION_PRIOR group ..
        observation_prior = OmlO21ObservationPrior()
        observation_prior.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='6652-2', cwe_2='Meropenem Susceptibility by MIC', cwe_3='LN')
        obx_2.obx_5 = '>=16'
        obx_2.units = CWE(cwe_1='mg/L')
        obx_2.interpretation_codes = CWE(cwe_1='R')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION_PRIOR group ..
        observation_prior_2 = OmlO21ObservationPrior()
        observation_prior_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='7029-2', cwe_2='Meropenem Susceptibility by Gradient strip', cwe_3='LN')
        obx_3.obx_5 = '8.0'
        obx_3.units = CWE(cwe_1='mg/L')
        obx_3.interpretation_codes = CWE(cwe_1='R')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION_PRIOR group ..
        observation_prior_3 = OmlO21ObservationPrior()
        observation_prior_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'CWE'
        obx_4.observation_identifier = CWE(cwe_1='18943-1', cwe_2='Meropenem Susceptibility', cwe_3='LN')
        obx_4.interpretation_codes = CWE(cwe_1='R')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION_PRIOR group ..
        observation_prior_4 = OmlO21ObservationPrior()
        observation_prior_4.obx = obx_4

        # .. build the ORDER_PRIOR group ..
        order_prior = OmlO21OrderPrior()
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
        observation_request.specimen = specimen
        observation_request.prior_result = prior_result

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
    """ Based on live/nl/nl-nen7504.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIMS_RECEIVER')
        msh.sending_facility = HD(hd_1='LAB_INBESTEDEND')
        msh.receiving_application = HD(hd_1='LIMS_SENDER')
        msh.receiving_facility = HD(hd_1='LAB_UITBESTEDEND')
        msh.date_time_of_message = '20220316140000'
        msh.message_type = MSG(msg_1='OUL', msg_2='R22', msg_3='OUL_R22')
        msh.message_control_id = 'MSG20220316001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.4.3.11.60.25.10.50', ei_2='NICTIZ', ei_3='ISO')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='ANON123', cx_5='PI'), CX(cx_1='462918375', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Jansen', xpn_2='Pieter', xpn_3='H')
        pid.date_time_of_birth = '19680312'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='MICRO', pl_2='LAB1', pl_3='01', pl_4='LAB_UITBESTEDEND')

        # .. build the VISIT group ..
        visit = OulR22Visit()
        visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OulR22Patient()
        patient.pid = pid
        patient.visit = visit

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_type = CWE(cwe_1='UR', cwe_2='Urine', cwe_3='HL70487')
        spm.specimen_risk_code = CWE(cwe_1='20220314153000')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD001', ei_2='LIMS_SENDER')
        obr.filler_order_number = EI(ei_1='FILL001', ei_2='LIMS_RECEIVER')
        obr.universal_service_identifier = CWE(cwe_1='29576-6', cwe_2='Bacterial susceptibility panel', cwe_3='LN')
        obr.observation_date_time = '20220315080000'
        obr.filler_field_2 = '20220316133000'
        obr.charge_to_practice = MOC(moc_1='LAB')
        obr.diagnostic_serv_sect_id = 'F'

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'RE'
        orc.placer_order_number = EI(ei_1='ORD001', ei_2='LIMS_SENDER')
        orc.filler_order_number = EI(ei_1='FILL001', ei_2='LIMS_RECEIVER')
        orc.order_status = 'CM'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='634-6', cwe_2='Bacteria identified', cwe_3='LN')
        obx.obx_5 = '112283007^Escherichia coli^SCT'
        obx.observation_result_status = 'F'

        # .. build the ORDER_DOCUMENT group ..
        order_document = OulR22OrderDocument()
        order_document.obx = obx

        # .. build the COMMON_ORDER group ..
        common_order = OulR22CommonOrder()
        common_order.orc = orc
        common_order.order_document = order_document

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='6652-2', cwe_2='Meropenem Susceptibility by MIC', cwe_3='LN')
        obx_2.obx_5 = '>=16'
        obx_2.units = CWE(cwe_1='mg/L')
        obx_2.interpretation_codes = CWE(cwe_1='R')
        obx_2.observation_result_status = 'F'

        # .. build the RESULT group ..
        result = OulR22Result()
        result.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='7029-2', cwe_2='Meropenem Susceptibility by Gradient strip', cwe_3='LN')
        obx_3.obx_5 = '8.0'
        obx_3.units = CWE(cwe_1='mg/L')
        obx_3.interpretation_codes = CWE(cwe_1='R')
        obx_3.observation_result_status = 'F'

        # .. build the RESULT group ..
        result_2 = OulR22Result()
        result_2.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'CWE'
        obx_4.observation_identifier = CWE(cwe_1='18943-1', cwe_2='Meropenem Susceptibility', cwe_3='LN')
        obx_4.interpretation_codes = CWE(cwe_1='R')
        obx_4.observation_result_status = 'F'

        # .. build the RESULT group ..
        result_3 = OulR22Result()
        result_3.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='185-9', cwe_2='Ciprofloxacin Susceptibility by MIC', cwe_3='LN')
        obx_5.obx_5 = '>4'
        obx_5.units = CWE(cwe_1='mg/L')
        obx_5.interpretation_codes = CWE(cwe_1='R')
        obx_5.observation_result_status = 'F'

        # .. build the RESULT group ..
        result_4 = OulR22Result()
        result_4.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='141-2', cwe_2='Amoxicillin+Clavulanate Susceptibility by MIC', cwe_3='LN')
        obx_6.obx_5 = '16'
        obx_6.units = CWE(cwe_1='mg/L')
        obx_6.interpretation_codes = CWE(cwe_1='I')
        obx_6.observation_result_status = 'F'

        # .. build the RESULT group ..
        result_5 = OulR22Result()
        result_5.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='193-3', cwe_2='Gentamicin Susceptibility by MIC', cwe_3='LN')
        obx_7.obx_5 = '0.5'
        obx_7.units = CWE(cwe_1='mg/L')
        obx_7.interpretation_codes = CWE(cwe_1='S')
        obx_7.observation_result_status = 'F'

        # .. build the RESULT group ..
        result_6 = OulR22Result()
        result_6.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'ST'
        obx_8.observation_identifier = CWE(cwe_1='524-9', cwe_2='Trimethoprim+Sulfamethoxazole Susceptibility by MIC', cwe_3='LN')
        obx_8.obx_5 = '>8'
        obx_8.units = CWE(cwe_1='mg/L')
        obx_8.interpretation_codes = CWE(cwe_1='R')
        obx_8.observation_result_status = 'F'

        # .. build the RESULT group ..
        result_7 = OulR22Result()
        result_7.obx = obx_8

        # .. build the ORDER group ..
        order = OulR22Order()
        order.obr = obr
        order.common_order = common_order
        order.result = result
        order.result_2 = result_2
        order.result_3 = result_3
        order.result_4 = result_4
        order.result_5 = result_5
        order.result_6 = result_6
        order.result_7 = result_7

        # .. build the SPECIMEN group ..
        specimen = OulR22Specimen()
        specimen.spm = spm
        specimen.order = order

        # .. assemble the full message ..
        msg = OUL_R22()
        msg.msh = msh
        msg.patient = patient
        msg.specimen = specimen

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
    """ Based on live/nl/nl-nen7504.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ZorgDomein')
        msh.date_time_of_message = '20220410143000+0200'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'ZD300012345'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='537829146', cx_4='NLMINBIZA', cx_5='NNNLD')
        pid.patient_name = XPN(xpn_1='van der Linden&van der&Linden', xpn_2='Johanna', xpn_3='M', xpn_7='L')
        pid.date_time_of_birth = '19751220'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Witte de Withstraat 45', xad_3='Rotterdam', xad_5='3012BM', xad_6='NL', xad_7='H')
        pid.pid_13 = '010-4445566^PRN^PH~^^^j.vanderlinden@email.nl^NET^Internet'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.insurance_company_name = XON(xon_1='VGZ', xon_2='VGZ Zorgverzekeraar')
        in1.insureds_group_emp_id = CX(cx_1='537829146')

        # .. build the INSURANCE group ..
        insurance = OrmO01Insurance()
        insurance.in1 = in1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit
        patient.insurance = insurance

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ZD300012345')
        orc.date_time_of_order_event = '20220410143000+0200'
        orc.orc_10 = '^&&van Houten^B.C.'
        orc.orc_12 = '01234567^&&Verhoeven^A.B.^^^^^^VEKTIS'
        orc.orc_14 = '010-7778899'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ZD300012345')
        obr.universal_service_identifier = CWE(cwe_1='DER', cwe_2='Dermatologie', cwe_3='ZORGDOMEIN')
        obr.observation_date_time = '20220410143000+0200'
        obr.obr_16 = '01234567^&&Verhoeven^A.B.^^^^^^VEKTIS'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='DERMOA001', cwe_2='Consult dermatoloog', cwe_3='ZORGDOMEIN')
        obx.obx_5 = 'Verdachte moedervlek rechter schouder, groei in afgelopen 3 maanden'
        obx.user_defined_access_checks = 'F'

        # .. build the OBSERVATION group ..
        observation = OrmO01Observation()
        observation.obx = obx

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
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
    """ Based on live/nl/nl-nen7504.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
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
        pid.patient_name = XPN(xpn_1='van den Berg&van den&Berg', xpn_2='P', xpn_3='J', xpn_7='L')
        pid.date_time_of_birth = '20000101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Leidsestraat 88  bis&Leidsestraat&88', xad_2='bis', xad_3='Eindhoven', xad_5='5611AA', xad_6='NL', xad_7='H')
        pid.pid_13 = '040-2839174^NET^Internet^p.vandenberg@email.nl'

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
        orc.orc_10 = '^&&de Groot^A.B.C.'
        orc.orc_12 = '01004567^&&van der Meer^Z.Z.^^^^^^VEKTIS'
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
        obr.obr_16 = '01004567^&&van der Meer^Z.Z.^^^^^^VEKTIS'

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
            'ADQALgA4AC4ANikKL0NyZWF0aW9uRGF0ZSAoRDoyMDE2MDMyNDE2MzUwOCswMScwMCcpCj4+CmVuZG9iag=='
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
    """ Based on live/nl/nl-nen7504.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
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
        pid.patient_name = XPN(xpn_1='van den Berg&van den&Berg', xpn_2='P', xpn_3='J', xpn_7='L')
        pid.date_time_of_birth = '20000101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Leidsestraat 88  bis&Leidsestraat&88', xad_2='bis', xad_3='Eindhoven', xad_5='5611AA', xad_6='NL', xad_7='H')
        pid.pid_13 = '040-2839174'

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
        orc.orc_10 = '^&&de Groot^A.B.C.'
        orc.orc_12 = '01004567^&&van der Meer^Z.Z.^^^^^^VEKTIS'
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
        obr.obr_16 = '01004567^&&van der Meer^Z.Z.^^^^^^VEKTIS'

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
            'ADQALgA4AC4ANikKL0NyZWF0aW9uRGF0ZSAoRDoyMDE2MDMyNDE2MzQ0MSswMScwMCcpCj4+CmVuZG9iag=='
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
    """ Based on live/nl/nl-nen7504.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS')
        msh.sending_facility = HD(hd_1='UMCU')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='UMCU')
        msh.date_time_of_message = '20210315080000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'ADT20210315001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20210315080000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT001', cx_4='UMCU', cx_5='PI'), CX(cx_1='471829365', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Timmerman', xpn_2='Adriaan', xpn_3='J')
        pid.date_time_of_birth = '19450620'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Maliebaan 22', xad_3='Utrecht', xad_5='3581CR', xad_6='NL', xad_7='H')
        pid.pid_13 = '030-2345678^PRN^PH'
        pid.religion = CWE(cwe_1='M')
        pid.veterans_military_status = CWE(cwe_1='N')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='201', pl_3='1', pl_4='UMCU')
        pv1.attending_doctor = XCN(xcn_1='12345', xcn_2='Brouwer', xcn_3='Theodora', xcn_6='dr.')
        pv1.hospital_service = CWE(cwe_1='CAR')
        pv1.admit_source = CWE(cwe_1='ADM')
        pv1.admitting_doctor = XCN(xcn_1='12345', xcn_2='Brouwer', xcn_3='Theodora', xcn_6='dr.')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.delete_account_date = 'UMCU'
        pv1.discharged_to_location = DLD(dld_1='A')
        pv1.pv1_40 = '20210315075500'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Timmerman', xpn_2='Elisabeth', xpn_3='M')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Echtgenote')
        nk1.address = XAD(xad_1='Maliebaan 22', xad_3='Utrecht', xad_5='3581CR', xad_6='NL')
        nk1.nk1_5 = '030-2345679'

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='ZILVERK001', cwe_2='Zilveren Kruis')
        in1.insurance_company_id = CX(cx_1='ZK')
        in1.insurance_company_address = XAD(xad_1='Postbus 200', xad_3='Leiden', xad_5='2300AE', xad_6='NL')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.extra_segments = [nk1, in1]

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
    """ Based on live/nl/nl-nen7504.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS')
        msh.sending_facility = HD(hd_1='UMCU')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='UMCU')
        msh.date_time_of_message = '20210320140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'ADT20210320001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20210320140000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT001', cx_4='UMCU', cx_5='PI'), CX(cx_1='471829365', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Timmerman', xpn_2='Adriaan', xpn_3='J')
        pid.date_time_of_birth = '19450620'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CARD', pl_2='201', pl_3='1', pl_4='UMCU')
        pv1.attending_doctor = XCN(xcn_1='12345', xcn_2='Brouwer', xcn_3='Theodora', xcn_6='dr.')
        pv1.hospital_service = CWE(cwe_1='CAR')
        pv1.admit_source = CWE(cwe_1='ADM')
        pv1.admitting_doctor = XCN(xcn_1='12345', xcn_2='Brouwer', xcn_3='Theodora', xcn_6='dr.')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.delete_account_date = 'UMCU'
        pv1.discharged_to_location = DLD(dld_1='D')
        pv1.pv1_40 = '20210315075500'
        pv1.prior_temporary_location = PL(pl_1='20210320133000')

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
    """ Based on live/nl/nl-nen7504.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS')
        msh.sending_facility = HD(hd_1='VUMC')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='VUMC')
        msh.date_time_of_message = '20210501093000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A08')
        msh.message_control_id = 'ADT20210501001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20210501093000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT002', cx_4='VUMC', cx_5='PI'), CX(cx_1='639518274', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Vermeer', xpn_2='Femke', xpn_3='L')
        pid.date_time_of_birth = '19700815'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Vondelstraat 25', xad_3='Amsterdam', xad_5='1054GE', xad_6='NL', xad_7='H')
        pid.pid_13 = '020-6234567^PRN^PH~^^^f.vermeer@email.nl'
        pid.religion = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='POLI', pl_2='INTERN', pl_3='01', pl_4='VUMC')
        pv1.attending_doctor = XCN(xcn_1='54321', xcn_2='Wolters', xcn_3='Jacobus', xcn_6='dr.')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='CZ001', cwe_2='CZ Zorgverzekeraar')
        in1.insurance_company_id = CX(cx_1='CZ')
        in1.insurance_company_address = XAD(xad_1='Postbus 100', xad_3='Tilburg', xad_5='5000AC', xad_6='NL')

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
    """ Based on live/nl/nl-nen7504.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS')
        msh.sending_facility = HD(hd_1='ERASMUS')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='ERASMUS')
        msh.date_time_of_message = '20210612110000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'ADT20210612001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20210612110000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT003', cx_4='ERASMUS', cx_5='PI'), CX(cx_1='819374625', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='de Jong', xpn_2='Hendrik', xpn_3='P')
        pid.date_time_of_birth = '19800305'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='401', pl_3='2', pl_4='ERASMUS')
        pv1.attending_doctor = XCN(xcn_1='67890', xcn_2='Dekker', xcn_3='Saskia', xcn_6='dr.')
        pv1.hospital_service = CWE(cwe_1='CHI')
        pv1.admit_source = CWE(cwe_1='ADM')
        pv1.admitting_doctor = XCN(xcn_1='67890', xcn_2='Dekker', xcn_3='Saskia', xcn_6='dr.')
        pv1.patient_type = CWE(cwe_1='IP')
        pv1.bad_debt_transfer_amount = 'ICU^102^1^ERASMUS'
        pv1.delete_account_date = 'ERASMUS'
        pv1.discharged_to_location = DLD(dld_1='A')
        pv1.pv1_40 = '20210610080000'

        # .. assemble the full message ..
        msg = ADT_A02()
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
    """ Based on live/nl/nl-nen7504.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABSYS')
        msh.sending_facility = HD(hd_1='STAR_MDC')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='UMCU')
        msh.date_time_of_message = '20220401083000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'LAB20220401001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT100', cx_4='UMCU', cx_5='PI'), CX(cx_1='729461835', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Mulder', xpn_2='Jacobus', xpn_3='J')
        pid.date_time_of_birth = '19720910'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Biltstraat 100', xad_3='Utrecht', xad_5='3572BH', xad_6='NL')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='INT', pl_2='302', pl_3='1', pl_4='UMCU')
        pv1.attending_doctor = XCN(xcn_1='99001', xcn_2='Visser', xcn_3='Elisabeth', xcn_6='dr.')

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
        orc.placer_order_number = EI(ei_1='ORD200', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='FILL300', ei_2='LABSYS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD200', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='FILL300', ei_2='LABSYS')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Comprehensive metabolic panel', cwe_3='LN')
        obr.observation_date_time = '20220401070000'
        obr.obr_14 = '99001^Visser^Elisabeth^^^dr.'
        obr.filler_field_1 = '20220401082500'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose', cwe_3='LN')
        obx.obx_5 = '6.8'
        obx.units = CWE(cwe_1='mmol/l')
        obx.reference_range = '4.0-7.8'
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
        obx_2.obx_5 = '88'
        obx_2.units = CWE(cwe_1='umol/l')
        obx_2.reference_range = '62-106'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Ureum', cwe_3='LN')
        obx_3.obx_5 = '5.2'
        obx_3.units = CWE(cwe_1='mmol/l')
        obx_3.reference_range = '2.5-7.5'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2951-2', cwe_2='Natrium', cwe_3='LN')
        obx_4.obx_5 = '141'
        obx_4.units = CWE(cwe_1='mmol/l')
        obx_4.reference_range = '135-145'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='2823-3', cwe_2='Kalium', cwe_3='LN')
        obx_5.obx_5 = '4.1'
        obx_5.units = CWE(cwe_1='mmol/l')
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
        obx_6.obx_5 = '2.35'
        obx_6.units = CWE(cwe_1='mmol/l')
        obx_6.reference_range = '2.20-2.60'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'NM'
        obx_7.observation_identifier = CWE(cwe_1='1742-6', cwe_2='ALAT', cwe_3='LN')
        obx_7.obx_5 = '25'
        obx_7.units = CWE(cwe_1='U/l')
        obx_7.reference_range = '0-45'
        obx_7.interpretation_codes = CWE(cwe_1='N')
        obx_7.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'NM'
        obx_8.observation_identifier = CWE(cwe_1='1920-8', cwe_2='ASAT', cwe_3='LN')
        obx_8.obx_5 = '22'
        obx_8.units = CWE(cwe_1='U/l')
        obx_8.reference_range = '0-40'
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
    """ Based on live/nl/nl-nen7504.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIMS_A')
        msh.sending_facility = HD(hd_1='LAB_AMSTERDAM')
        msh.receiving_application = HD(hd_1='LIMS_B')
        msh.receiving_facility = HD(hd_1='LAB_ROTTERDAM')
        msh.date_time_of_message = '20220510140000'
        msh.message_type = MSG(msg_1='OML', msg_2='O21', msg_3='OML_O21')
        msh.message_control_id = 'MSG20220510001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'
        msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.4.3.11.60.25.10.1', ei_2='NICTIZ', ei_3='ISO')

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PAT200', cx_5='PI'), CX(cx_1='846173529', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Bos', xpn_2='Anneke', xpn_3='L')
        pid.date_time_of_birth = '19850225'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Laan van Meerdervoort 200', xad_3='Den Haag', xad_5='2517BH', xad_6='NL')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='KLIN_CHEM', pl_2='01', pl_3='01', pl_4='LAB_AMSTERDAM')

        # .. build the PATIENT_VISIT group ..
        patient_visit = OmlO21PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OmlO21Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD300', ei_2='LIMS_A')
        orc.orc_7 = '1^^^20220510140000^^R'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD300', ei_2='LIMS_A')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Comprehensive metabolic panel', cwe_3='LN')
        obr.observation_date_time = '20220510120000'
        obr.relevant_clinical_information = CWE(cwe_1='Diabetes monitoring, HbA1c niet beschikbaar bij aanvragend lab')
        obr.obr_16 = '5678^Smit^Maria^^^arts'

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_type = CWE(cwe_1='BLD', cwe_2='Blood', cwe_3='HL70487')
        spm.specimen_risk_code = CWE(cwe_1='20220510115000')

        # .. build the SPECIMEN group ..
        specimen = OmlO21Specimen()
        specimen.spm = spm

        # .. build the OBSERVATION_REQUEST group ..
        observation_request = OmlO21ObservationRequest()
        observation_request.obr = obr
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
    """ Based on live/nl/nl-nen7504.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIMS_B')
        msh.sending_facility = HD(hd_1='LAB_ROTTERDAM')
        msh.receiving_application = HD(hd_1='LIMS_A')
        msh.receiving_facility = HD(hd_1='LAB_AMSTERDAM')
        msh.date_time_of_message = '20220510140100'
        msh.message_type = MSG(msg_1='ACK', msg_2='O21', msg_3='ACK')
        msh.message_control_id = 'ACK20220510001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'MSG20220510001'

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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
    """ Based on live/nl/nl-nen7504.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIMS_RECEIVER')
        msh.sending_facility = HD(hd_1='LAB_INBESTEDEND')
        msh.receiving_application = HD(hd_1='LIMS_SENDER')
        msh.receiving_facility = HD(hd_1='LAB_UITBESTEDEND')
        msh.date_time_of_message = '20220315100000'
        msh.message_type = MSG(msg_1='ORL', msg_2='O22', msg_3='ORL_O22')
        msh.message_control_id = 'ORL20220315001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'MSG20220315001'

        # .. assemble the full message ..
        msg = ORL_O22()
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
    """ Based on live/nl/nl-nen7504.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LABSYS')
        msh.sending_facility = HD(hd_1='ISALA')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='ISALA')
        msh.date_time_of_message = '20220715090000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'LAB20220715001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.msh_14 = ''

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='PAT300', cx_5='PI'), CX(cx_1='513847296', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Hoekstra', xpn_2='Willem', xpn_3='K')
        pid.date_time_of_birth = '19550120'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='IJsselkade 10', xad_3='Zwolle', xad_5='8011AR', xad_6='NL')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HEMATO', pl_2='201', pl_3='1', pl_4='ISALA')
        pv1.attending_doctor = XCN(xcn_1='11111', xcn_2='Kuipers', xcn_3='Daan', xcn_6='dr.')

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
        obr.placer_order_number = EI(ei_1='ORD400', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='FILL500', ei_2='LABSYS')
        obr.universal_service_identifier = CWE(cwe_1='57021-8', cwe_2='CBC', cwe_3='LN')
        obr.observation_date_time = '20220715070000'
        obr.relevant_clinical_information = CWE(cwe_1='""')
        obr.obr_16 = '11111^Kuipers^Daan^^^dr.'
        obr.filler_field_1 = '20220715085500'
        obr.results_rpt_status_chng_date_time = 'LAB'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leucocyten', cwe_3='LN')
        obx.obx_5 = '15.2'
        obx.units = CWE(cwe_1='10*9/l')
        obx.reference_range = '4.0-10.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erythrocyten', cwe_3='LN')
        obx_2.obx_5 = '3.2'
        obx_2.units = CWE(cwe_1='10*12/l')
        obx_2.reference_range = '4.0-5.5'
        obx_2.interpretation_codes = CWE(cwe_1='L')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobine', cwe_3='LN')
        obx_3.obx_5 = '7.1'
        obx_3.units = CWE(cwe_1='mmol/l')
        obx_3.reference_range = '8.5-11.0'
        obx_3.interpretation_codes = CWE(cwe_1='L')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocriet', cwe_3='LN')
        obx_4.obx_5 = '0.34'
        obx_4.units = CWE(cwe_1='l/l')
        obx_4.reference_range = '0.41-0.51'
        obx_4.interpretation_codes = CWE(cwe_1='L')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='787-2', cwe_2='MCV', cwe_3='LN')
        obx_5.obx_5 = '106'
        obx_5.units = CWE(cwe_1='fl')
        obx_5.reference_range = '80-100'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='777-3', cwe_2='Trombocyten', cwe_3='LN')
        obx_6.obx_5 = '95'
        obx_6.units = CWE(cwe_1='10*9/l')
        obx_6.reference_range = '150-400'
        obx_6.interpretation_codes = CWE(cwe_1='L')
        obx_6.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
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
    """ Based on live/nl/nl-nen7504.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ZorgDomein')
        msh.date_time_of_message = '20220601101500+0200'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'ZD300054321'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='945263718', cx_4='NLMINBIZA', cx_5='NNNLD')
        pid.patient_name = XPN(xpn_1='de Wit', xpn_2='Lotte', xpn_3='A', xpn_7='L')
        pid.date_time_of_birth = '19830415'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Herengracht 100', xad_3='Amsterdam', xad_5='1015BS', xad_6='NL', xad_7='H')
        pid.pid_13 = '020-5551234'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')

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
        orc.placer_order_number = EI(ei_1='ZD300054321')
        orc.date_time_of_order_event = '20220601101500+0200'
        orc.orc_10 = '^&&Meijer^C.D.'
        orc.orc_12 = '09876543^&&Bakker^E.F.^^^^^^VEKTIS'
        orc.orc_14 = '020-3334444'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ZD300054321')
        obr.universal_service_identifier = CWE(cwe_1='RAD', cwe_2='Radiologie', cwe_3='ZORGDOMEIN')
        obr.observation_date_time = '20220601101500+0200'
        obr.obr_16 = '09876543^&&Bakker^E.F.^^^^^^VEKTIS'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='RADMRI001', cwe_2='MRI knie rechts', cwe_3='ZORGDOMEIN')
        obx.obx_5 = 'Patiente klaagt over aanhoudende kniepijn rechts na sportblessure. Verdenking meniscusletsel.'
        obx.user_defined_access_checks = 'F'

        # .. build the OBSERVATION group ..
        observation = OrmO01Observation()
        observation.obx = obx

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
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
    """ Based on live/nl/nl-nen7504.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PALGA')
        msh.sending_facility = HD(hd_1='PATHLAB')
        msh.receiving_application = HD(hd_1='HIS')
        msh.receiving_facility = HD(hd_1='RADBOUDUMC')
        msh.date_time_of_message = '20220901150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'PATH20220901001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'
        msh.country_code = 'NLD'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT400', cx_4='RADBOUDUMC', cx_5='PI'), CX(cx_1='284619537', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Wolters', xpn_2='Theodora', xpn_3='B')
        pid.date_time_of_birth = '19700830'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Plein 1944 nr 5', xad_3='Nijmegen', xad_5='6525HP', xad_6='NL')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CHIR', pl_2='501', pl_3='1', pl_4='RADBOUDUMC')
        pv1.attending_doctor = XCN(xcn_1='22222', xcn_2='Hendriks', xcn_3='Adriaan', xcn_6='dr.')

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
        orc.placer_order_number = EI(ei_1='ORD500', ei_2='HIS')
        orc.filler_order_number = EI(ei_1='FILL600', ei_2='PALGA')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD500', ei_2='HIS')
        obr.filler_order_number = EI(ei_1='FILL600', ei_2='PALGA')
        obr.universal_service_identifier = CWE(cwe_1='22637-3', cwe_2='Pathology report', cwe_3='LN')
        obr.observation_date_time = '20220830100000'
        obr.obr_14 = '22222^Hendriks^Adriaan^^^dr.'
        obr.filler_field_1 = '20220901143000'
        obr.results_rpt_status_chng_date_time = 'PATH'
        obr.charge_to_practice = MOC(moc_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='22637-3', cwe_2='Pathology report', cwe_3='LN')
        obx.obx_5 = (
            'Macroscopie: Huidbiopt rechter schouder, diameter 6mm\\.br\\Microscopie: Melanocytaire proliferatie met atypische kenmerken\\.br\\Conclusie: Dys'
            'plastische naevus, Clark graad II\\.br\\Advies: Excisie met 5mm marge.'
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
    """ Based on live/nl/nl-nen7504.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS')
        msh.sending_facility = HD(hd_1='UMCG')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='UMCG')
        msh.date_time_of_message = '20220801090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A04')
        msh.message_control_id = 'ADT20220801001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'NLD'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20220801090000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT700', cx_4='UMCG', cx_5='PI'), CX(cx_1='375816492', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Brouwer', xpn_2='Saskia', xpn_3='S')
        pid.date_time_of_birth = '19900215'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Herestraat 1', xad_3='Groningen', xad_5='9713GZ', xad_6='NL', xad_7='H')
        pid.pid_13 = '050-3612345^PRN^PH~^^^s.brouwer@email.nl'
        pid.religion = CWE(cwe_1='O')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='POLI', pl_2='OOG', pl_3='01', pl_4='UMCG')
        pv1.attending_doctor = XCN(xcn_1='55555', xcn_2='van Dijk', xcn_3='Pieter', xcn_6='dr.')
        pv1.hospital_service = CWE(cwe_1='OOG')
        pv1.admit_source = CWE(cwe_1='REG')
        pv1.admitting_doctor = XCN(xcn_1='55555', xcn_2='van Dijk', xcn_3='Pieter', xcn_6='dr.')
        pv1.patient_type = CWE(cwe_1='OP')

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
