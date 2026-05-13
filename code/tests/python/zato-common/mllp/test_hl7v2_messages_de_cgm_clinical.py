# -*- coding: utf-8 -*-
# ruff: noqa: F405

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import unittest

# Zato
from zato.hl7v2.v2_9 import parse_message
from zato.hl7v2.v2_9.segments import *  # noqa: F403
from zato.hl7v2.v2_9.datatypes import *  # noqa: F403
from zato.hl7v2.v2_9.messages import *  # noqa: F403

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_clinical_01 = 'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260315083000||ADT^A01^ADT_A01|CTL00001|P|2.6\rEVN|A01|20260315083000\rPID|||PT7890^^^Löwenklinik||Grünwald^Käthe^Ännchen^^Frau||19830214|F|||Böttcherstraße 47^^Nürnberg^^90402||^^PH^09111234567~^^CP^01761234567~^^Internet^kaethe.gruenwald@yähoo.de\rPV1||I|Südflügel^Raum 401^Bett 1^Orthopädie||||ARZ100^Müller^Björn^^^Dr.^med.|ARZ200^Bäcker^Günther^^^Dr.^med.|ARZ300^Schröder^Jürgen^^^Dr.^med.||Nordflügel^Raum 502^Bett 2^Innere Medizin||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260315083000\rIN1|1|0|KV001|BÜRGERKRANKENVERSICHERUNG|Königstraße 88^^München^^80331||||||||||||||||||||||||||||||||||||||||||||49'

class Test_de_cgm_clinical_01_1_ADT_A01_station_re_Aufnahme_inpatient_admission_with_insurance(unittest.TestCase):
    """ 1. ADT^A01 - stationäre Aufnahme (inpatient admission) with insurance
    Source: support.thieme-compliance.de - HL7-Nachrichtentyp ADT, Beispielnachricht A01
    URL: https://support.thieme-compliance.de/de/ECP/Admin/hl7_adt-nachrichten.html
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KLINIK_SND')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'STÄDTISCH_KH')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'LABOR_EMP')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'RÖNTGEN_KH')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260315083000')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A01')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'CTL00001')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.6')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '20260315083000')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, 'PT7890')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Löwenklinik')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Grünwald')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Käthe')

# ################################################################################################################

    def test_navigate_PID_5_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PID.5.3')
        self.assertEqual(result, 'Ännchen')

# ################################################################################################################

    def test_navigate_PID_5_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PID.5.5')
        self.assertEqual(result, 'Frau')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19830214')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Böttcherstraße 47')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Nürnberg')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '90402')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'Südflügel')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, 'Raum 401')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, 'Bett 1')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'Orthopädie')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, 'ARZ100')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Müller')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Björn')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.7.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.8')
        self.assertEqual(result, 'ARZ200')

# ################################################################################################################

    def test_navigate_PV1_8_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.8.2')
        self.assertEqual(result, 'Bäcker')

# ################################################################################################################

    def test_navigate_PV1_8_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.8.3')
        self.assertEqual(result, 'Günther')

# ################################################################################################################

    def test_navigate_PV1_8_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.8.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_8_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.8.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.9')
        self.assertEqual(result, 'ARZ300')

# ################################################################################################################

    def test_navigate_PV1_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.9.2')
        self.assertEqual(result, 'Schröder')

# ################################################################################################################

    def test_navigate_PV1_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.9.3')
        self.assertEqual(result, 'Jürgen')

# ################################################################################################################

    def test_navigate_PV1_9_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.9.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_9_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.9.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.11')
        self.assertEqual(result, 'Nordflügel')

# ################################################################################################################

    def test_navigate_PV1_11_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.11.2')
        self.assertEqual(result, 'Raum 502')

# ################################################################################################################

    def test_navigate_PV1_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.11.3')
        self.assertEqual(result, 'Bett 2')

# ################################################################################################################

    def test_navigate_PV1_11_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.11.4')
        self.assertEqual(result, 'Innere Medizin')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, 'FALL7890')

# ################################################################################################################

    def test_navigate_PV1_42(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.42')
        self.assertEqual(result, 'Westflügel')

# ################################################################################################################

    def test_navigate_PV1_42_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.42.2')
        self.assertEqual(result, 'Raum 603')

# ################################################################################################################

    def test_navigate_PV1_42_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.42.3')
        self.assertEqual(result, 'Bett 3')

# ################################################################################################################

    def test_navigate_PV1_42_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.42.4')
        self.assertEqual(result, 'Neurochirurgie')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '20260315083000')

# ################################################################################################################

    def test_navigate_IN1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('IN1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_IN1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('IN1.2')
        self.assertEqual(result, '0')

# ################################################################################################################

    def test_navigate_IN1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('IN1.3')
        self.assertEqual(result, 'KV001')

# ################################################################################################################

    def test_navigate_IN1_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('IN1.4')
        self.assertEqual(result, 'BÜRGERKRANKENVERSICHERUNG')

# ################################################################################################################

    def test_navigate_IN1_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('IN1.5')
        self.assertEqual(result, 'Königstraße 88')

# ################################################################################################################

    def test_navigate_IN1_5_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('IN1.5.3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_IN1_5_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('IN1.5.5')
        self.assertEqual(result, '80331')

# ################################################################################################################

    def test_navigate_IN1_49(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_01, validate=False)
        result = message.get('IN1.49')
        self.assertEqual(result, '49')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KLINIK_SND')
        segment.sending_facility = HD(hd_1='STÄDTISCH_KH')
        segment.receiving_application = HD(hd_1='LABOR_EMP')
        segment.receiving_facility = HD(hd_1='RÖNTGEN_KH')
        segment.date_time_of_message = '20260315083000'
        segment.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        segment.message_control_id = 'CTL00001'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.6')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260315083000||ADT^A01^ADT_A01|CTL00001|P|2.6'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '20260315083000'

        serialized = segment.serialize()
        expected = 'EVN|A01|20260315083000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='PT7890', cx_4='Löwenklinik')
        segment.patient_name = XPN(xpn_1='Grünwald', xpn_2='Käthe', xpn_3='Ännchen', xpn_5='Frau')
        segment.date_time_of_birth = '19830214'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Böttcherstraße 47', xad_3='Nürnberg', xad_5='90402')

        serialized = segment.serialize()
        expected = 'PID|||PT7890^^^Löwenklinik||Grünwald^Käthe^Ännchen^^Frau||19830214|F|||Böttcherstraße 47^^Nürnberg^^90402||^^PH^09111234567~^^CP^01761234567~^^Internet^kaethe.gruenwald@yähoo.de'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='Südflügel', pl_2='Raum 401', pl_3='Bett 1', pl_4='Orthopädie')
        segment.attending_doctor = XCN(xcn_1='ARZ100', xcn_2='Müller', xcn_3='Björn', xcn_6='Dr.', xcn_8='med.')
        segment.referring_doctor = XCN(xcn_1='ARZ200', xcn_2='Bäcker', xcn_3='Günther', xcn_6='Dr.', xcn_8='med.')
        segment.consulting_doctor = XCN(xcn_1='ARZ300', xcn_2='Schröder', xcn_3='Jürgen', xcn_6='Dr.', xcn_8='med.')
        segment.temporary_location = PL(pl_1='Nordflügel', pl_2='Raum 502', pl_3='Bett 2', pl_4='Innere Medizin')
        segment.visit_number = CX(cx_1='FALL7890')
        segment.pending_location = PL(pl_1='Westflügel', pl_2='Raum 603', pl_3='Bett 3', pl_4='Neurochirurgie')
        segment.admit_date_time = '20260315083000'

        serialized = segment.serialize()
        expected = 'PV1||I|Südflügel^Raum 401^Bett 1^Orthopädie||||ARZ100^Müller^Björn^^^Dr.^med.|ARZ200^Bäcker^Günther^^^Dr.^med.|ARZ300^Schröder^Jürgen^^^Dr.^med.||Nordflügel^Raum 502^Bett 2^Innere Medizin||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260315083000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_IN1(self) -> 'None':
        segment = IN1()

        segment.set_id_in1 = '1'
        segment.health_plan_id = CWE(cwe_1='0')
        segment.insurance_company_id = CX(cx_1='KV001')
        segment.insurance_company_name = XON(xon_1='BÜRGERKRANKENVERSICHERUNG')
        segment.insurance_company_address = XAD(xad_1='Königstraße 88', xad_3='München', xad_5='80331')
        segment.insureds_id_number = CX(cx_1='49')

        serialized = segment.serialize()
        expected = 'IN1|1|0|KV001|BÜRGERKRANKENVERSICHERUNG|Königstraße 88^^München^^80331||||||||||||||||||||||||||||||||||||||||||||49'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A01()

        message.msh.sending_application = HD(hd_1='KLINIK_SND')
        message.msh.sending_facility = HD(hd_1='STÄDTISCH_KH')
        message.msh.receiving_application = HD(hd_1='LABOR_EMP')
        message.msh.receiving_facility = HD(hd_1='RÖNTGEN_KH')
        message.msh.date_time_of_message = '20260315083000'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        message.msh.message_control_id = 'CTL00001'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.6')

        message.evn.recorded_date_time = '20260315083000'

        message.pid.patient_identifier_list = CX(cx_1='PT7890', cx_4='Löwenklinik')
        message.pid.patient_name = XPN(xpn_1='Grünwald', xpn_2='Käthe', xpn_3='Ännchen', xpn_5='Frau')
        message.pid.date_time_of_birth = '19830214'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = XAD(xad_1='Böttcherstraße 47', xad_3='Nürnberg', xad_5='90402')

        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='Südflügel', pl_2='Raum 401', pl_3='Bett 1', pl_4='Orthopädie')
        message.pv1.attending_doctor = XCN(xcn_1='ARZ100', xcn_2='Müller', xcn_3='Björn', xcn_6='Dr.', xcn_8='med.')
        message.pv1.referring_doctor = XCN(xcn_1='ARZ200', xcn_2='Bäcker', xcn_3='Günther', xcn_6='Dr.', xcn_8='med.')
        message.pv1.consulting_doctor = XCN(xcn_1='ARZ300', xcn_2='Schröder', xcn_3='Jürgen', xcn_6='Dr.', xcn_8='med.')
        message.pv1.temporary_location = PL(pl_1='Nordflügel', pl_2='Raum 502', pl_3='Bett 2', pl_4='Innere Medizin')
        message.pv1.visit_number = CX(cx_1='FALL7890')
        message.pv1.pending_location = PL(pl_1='Westflügel', pl_2='Raum 603', pl_3='Bett 3', pl_4='Neurochirurgie')
        message.pv1.admit_date_time = '20260315083000'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_clinical_02 = 'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260315093000||ADT^A02^ADT_A02|CTL00002|P|2.6\rEVN|A02|20260315093000\rPID|||PT7890^^^Löwenklinik||Grünwald^Käthe^Ännchen^^Frau||19830214|F|||Böttcherstraße 47^^Nürnberg^^90402||^^PH^09111234567~^^CP^01761234567~^^Internet^kaethe.gruenwald@yähoo.de\rPV1||I|Nordflügel^Raum 502^Bett 2^Innere Medizin||||ARZ100^Müller^Björn^^^Dr.^med.|ARZ200^Bäcker^Günther^^^Dr.^med.|ARZ300^Schröder^Jürgen^^^Dr.^med.||Südflügel^Raum 401^Bett 1^Orthopädie||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260315093000'

class Test_de_cgm_clinical_02_2_ADT_A02_Verlegung_patient_transfer(unittest.TestCase):
    """ 2. ADT^A02 - Verlegung (patient transfer)
    Source: support.thieme-compliance.de - HL7-Nachrichtentyp ADT, Beispielnachricht A02
    URL: https://support.thieme-compliance.de/de/ECP/Admin/hl7_adt-nachrichten.html
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        self.assertIsInstance(message, ADT_A02)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A02')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KLINIK_SND')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'STÄDTISCH_KH')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'LABOR_EMP')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'RÖNTGEN_KH')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260315093000')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A02')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A02')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'CTL00002')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.6')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '20260315093000')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, 'PT7890')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Löwenklinik')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Grünwald')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Käthe')

# ################################################################################################################

    def test_navigate_PID_5_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PID.5.3')
        self.assertEqual(result, 'Ännchen')

# ################################################################################################################

    def test_navigate_PID_5_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PID.5.5')
        self.assertEqual(result, 'Frau')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19830214')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Böttcherstraße 47')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Nürnberg')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '90402')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'Nordflügel')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, 'Raum 502')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, 'Bett 2')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'Innere Medizin')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, 'ARZ100')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Müller')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Björn')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.7.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.8')
        self.assertEqual(result, 'ARZ200')

# ################################################################################################################

    def test_navigate_PV1_8_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.8.2')
        self.assertEqual(result, 'Bäcker')

# ################################################################################################################

    def test_navigate_PV1_8_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.8.3')
        self.assertEqual(result, 'Günther')

# ################################################################################################################

    def test_navigate_PV1_8_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.8.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_8_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.8.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.9')
        self.assertEqual(result, 'ARZ300')

# ################################################################################################################

    def test_navigate_PV1_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.9.2')
        self.assertEqual(result, 'Schröder')

# ################################################################################################################

    def test_navigate_PV1_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.9.3')
        self.assertEqual(result, 'Jürgen')

# ################################################################################################################

    def test_navigate_PV1_9_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.9.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_9_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.9.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.11')
        self.assertEqual(result, 'Südflügel')

# ################################################################################################################

    def test_navigate_PV1_11_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.11.2')
        self.assertEqual(result, 'Raum 401')

# ################################################################################################################

    def test_navigate_PV1_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.11.3')
        self.assertEqual(result, 'Bett 1')

# ################################################################################################################

    def test_navigate_PV1_11_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.11.4')
        self.assertEqual(result, 'Orthopädie')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, 'FALL7890')

# ################################################################################################################

    def test_navigate_PV1_42(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.42')
        self.assertEqual(result, 'Westflügel')

# ################################################################################################################

    def test_navigate_PV1_42_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.42.2')
        self.assertEqual(result, 'Raum 603')

# ################################################################################################################

    def test_navigate_PV1_42_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.42.3')
        self.assertEqual(result, 'Bett 3')

# ################################################################################################################

    def test_navigate_PV1_42_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.42.4')
        self.assertEqual(result, 'Neurochirurgie')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_02, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '20260315093000')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KLINIK_SND')
        segment.sending_facility = HD(hd_1='STÄDTISCH_KH')
        segment.receiving_application = HD(hd_1='LABOR_EMP')
        segment.receiving_facility = HD(hd_1='RÖNTGEN_KH')
        segment.date_time_of_message = '20260315093000'
        segment.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        segment.message_control_id = 'CTL00002'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.6')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260315093000||ADT^A02^ADT_A02|CTL00002|P|2.6'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '20260315093000'

        serialized = segment.serialize()
        expected = 'EVN|A02|20260315093000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='PT7890', cx_4='Löwenklinik')
        segment.patient_name = XPN(xpn_1='Grünwald', xpn_2='Käthe', xpn_3='Ännchen', xpn_5='Frau')
        segment.date_time_of_birth = '19830214'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Böttcherstraße 47', xad_3='Nürnberg', xad_5='90402')

        serialized = segment.serialize()
        expected = 'PID|||PT7890^^^Löwenklinik||Grünwald^Käthe^Ännchen^^Frau||19830214|F|||Böttcherstraße 47^^Nürnberg^^90402||^^PH^09111234567~^^CP^01761234567~^^Internet^kaethe.gruenwald@yähoo.de'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='Nordflügel', pl_2='Raum 502', pl_3='Bett 2', pl_4='Innere Medizin')
        segment.attending_doctor = XCN(xcn_1='ARZ100', xcn_2='Müller', xcn_3='Björn', xcn_6='Dr.', xcn_8='med.')
        segment.referring_doctor = XCN(xcn_1='ARZ200', xcn_2='Bäcker', xcn_3='Günther', xcn_6='Dr.', xcn_8='med.')
        segment.consulting_doctor = XCN(xcn_1='ARZ300', xcn_2='Schröder', xcn_3='Jürgen', xcn_6='Dr.', xcn_8='med.')
        segment.temporary_location = PL(pl_1='Südflügel', pl_2='Raum 401', pl_3='Bett 1', pl_4='Orthopädie')
        segment.visit_number = CX(cx_1='FALL7890')
        segment.pending_location = PL(pl_1='Westflügel', pl_2='Raum 603', pl_3='Bett 3', pl_4='Neurochirurgie')
        segment.admit_date_time = '20260315093000'

        serialized = segment.serialize()
        expected = 'PV1||I|Nordflügel^Raum 502^Bett 2^Innere Medizin||||ARZ100^Müller^Björn^^^Dr.^med.|ARZ200^Bäcker^Günther^^^Dr.^med.|ARZ300^Schröder^Jürgen^^^Dr.^med.||Südflügel^Raum 401^Bett 1^Orthopädie||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260315093000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A02()

        message.msh.sending_application = HD(hd_1='KLINIK_SND')
        message.msh.sending_facility = HD(hd_1='STÄDTISCH_KH')
        message.msh.receiving_application = HD(hd_1='LABOR_EMP')
        message.msh.receiving_facility = HD(hd_1='RÖNTGEN_KH')
        message.msh.date_time_of_message = '20260315093000'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        message.msh.message_control_id = 'CTL00002'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.6')

        message.evn.recorded_date_time = '20260315093000'

        message.pid.patient_identifier_list = CX(cx_1='PT7890', cx_4='Löwenklinik')
        message.pid.patient_name = XPN(xpn_1='Grünwald', xpn_2='Käthe', xpn_3='Ännchen', xpn_5='Frau')
        message.pid.date_time_of_birth = '19830214'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = XAD(xad_1='Böttcherstraße 47', xad_3='Nürnberg', xad_5='90402')

        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='Nordflügel', pl_2='Raum 502', pl_3='Bett 2', pl_4='Innere Medizin')
        message.pv1.attending_doctor = XCN(xcn_1='ARZ100', xcn_2='Müller', xcn_3='Björn', xcn_6='Dr.', xcn_8='med.')
        message.pv1.referring_doctor = XCN(xcn_1='ARZ200', xcn_2='Bäcker', xcn_3='Günther', xcn_6='Dr.', xcn_8='med.')
        message.pv1.consulting_doctor = XCN(xcn_1='ARZ300', xcn_2='Schröder', xcn_3='Jürgen', xcn_6='Dr.', xcn_8='med.')
        message.pv1.temporary_location = PL(pl_1='Südflügel', pl_2='Raum 401', pl_3='Bett 1', pl_4='Orthopädie')
        message.pv1.visit_number = CX(cx_1='FALL7890')
        message.pv1.pending_location = PL(pl_1='Westflügel', pl_2='Raum 603', pl_3='Bett 3', pl_4='Neurochirurgie')
        message.pv1.admit_date_time = '20260315093000'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_clinical_03 = 'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260320140000||ADT^A03^ADT_A03|CTL00003|P|2.6\rEVN|A03|20260320140000\rPID|||PT7890^^^Löwenklinik||Grünwald^Käthe^Ännchen^^Frau||19830214|F|||Böttcherstraße 47^^Nürnberg^^90402||^^PH^09111234567~^^CP^01761234567~^^Internet^kaethe.gruenwald@yähoo.de\rPV1||I|Südflügel^Raum 401^Bett 1^Orthopädie||||ARZ100^Müller^Björn^^^Dr.^med.|ARZ200^Bäcker^Günther^^^Dr.^med.|ARZ300^Schröder^Jürgen^^^Dr.^med.||Nordflügel^Raum 502^Bett 2^Innere Medizin||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260320140000'

class Test_de_cgm_clinical_03_3_ADT_A03_Entlassung_discharge(unittest.TestCase):
    """ 3. ADT^A03 - Entlassung (discharge)
    Source: support.thieme-compliance.de - HL7-Nachrichtentyp ADT, Beispielnachricht A03
    URL: https://support.thieme-compliance.de/de/ECP/Admin/hl7_adt-nachrichten.html
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        self.assertIsInstance(message, ADT_A03)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A03')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KLINIK_SND')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'STÄDTISCH_KH')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'LABOR_EMP')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'RÖNTGEN_KH')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260320140000')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A03')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A03')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'CTL00003')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.6')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '20260320140000')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, 'PT7890')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Löwenklinik')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Grünwald')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Käthe')

# ################################################################################################################

    def test_navigate_PID_5_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PID.5.3')
        self.assertEqual(result, 'Ännchen')

# ################################################################################################################

    def test_navigate_PID_5_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PID.5.5')
        self.assertEqual(result, 'Frau')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19830214')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Böttcherstraße 47')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Nürnberg')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '90402')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'Südflügel')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, 'Raum 401')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, 'Bett 1')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'Orthopädie')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, 'ARZ100')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Müller')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Björn')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.7.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.8')
        self.assertEqual(result, 'ARZ200')

# ################################################################################################################

    def test_navigate_PV1_8_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.8.2')
        self.assertEqual(result, 'Bäcker')

# ################################################################################################################

    def test_navigate_PV1_8_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.8.3')
        self.assertEqual(result, 'Günther')

# ################################################################################################################

    def test_navigate_PV1_8_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.8.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_8_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.8.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.9')
        self.assertEqual(result, 'ARZ300')

# ################################################################################################################

    def test_navigate_PV1_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.9.2')
        self.assertEqual(result, 'Schröder')

# ################################################################################################################

    def test_navigate_PV1_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.9.3')
        self.assertEqual(result, 'Jürgen')

# ################################################################################################################

    def test_navigate_PV1_9_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.9.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_9_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.9.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.11')
        self.assertEqual(result, 'Nordflügel')

# ################################################################################################################

    def test_navigate_PV1_11_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.11.2')
        self.assertEqual(result, 'Raum 502')

# ################################################################################################################

    def test_navigate_PV1_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.11.3')
        self.assertEqual(result, 'Bett 2')

# ################################################################################################################

    def test_navigate_PV1_11_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.11.4')
        self.assertEqual(result, 'Innere Medizin')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, 'FALL7890')

# ################################################################################################################

    def test_navigate_PV1_42(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.42')
        self.assertEqual(result, 'Westflügel')

# ################################################################################################################

    def test_navigate_PV1_42_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.42.2')
        self.assertEqual(result, 'Raum 603')

# ################################################################################################################

    def test_navigate_PV1_42_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.42.3')
        self.assertEqual(result, 'Bett 3')

# ################################################################################################################

    def test_navigate_PV1_42_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.42.4')
        self.assertEqual(result, 'Neurochirurgie')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_03, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '20260320140000')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KLINIK_SND')
        segment.sending_facility = HD(hd_1='STÄDTISCH_KH')
        segment.receiving_application = HD(hd_1='LABOR_EMP')
        segment.receiving_facility = HD(hd_1='RÖNTGEN_KH')
        segment.date_time_of_message = '20260320140000'
        segment.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        segment.message_control_id = 'CTL00003'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.6')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260320140000||ADT^A03^ADT_A03|CTL00003|P|2.6'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '20260320140000'

        serialized = segment.serialize()
        expected = 'EVN|A03|20260320140000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='PT7890', cx_4='Löwenklinik')
        segment.patient_name = XPN(xpn_1='Grünwald', xpn_2='Käthe', xpn_3='Ännchen', xpn_5='Frau')
        segment.date_time_of_birth = '19830214'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Böttcherstraße 47', xad_3='Nürnberg', xad_5='90402')

        serialized = segment.serialize()
        expected = 'PID|||PT7890^^^Löwenklinik||Grünwald^Käthe^Ännchen^^Frau||19830214|F|||Böttcherstraße 47^^Nürnberg^^90402||^^PH^09111234567~^^CP^01761234567~^^Internet^kaethe.gruenwald@yähoo.de'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='Südflügel', pl_2='Raum 401', pl_3='Bett 1', pl_4='Orthopädie')
        segment.attending_doctor = XCN(xcn_1='ARZ100', xcn_2='Müller', xcn_3='Björn', xcn_6='Dr.', xcn_8='med.')
        segment.referring_doctor = XCN(xcn_1='ARZ200', xcn_2='Bäcker', xcn_3='Günther', xcn_6='Dr.', xcn_8='med.')
        segment.consulting_doctor = XCN(xcn_1='ARZ300', xcn_2='Schröder', xcn_3='Jürgen', xcn_6='Dr.', xcn_8='med.')
        segment.temporary_location = PL(pl_1='Nordflügel', pl_2='Raum 502', pl_3='Bett 2', pl_4='Innere Medizin')
        segment.visit_number = CX(cx_1='FALL7890')
        segment.pending_location = PL(pl_1='Westflügel', pl_2='Raum 603', pl_3='Bett 3', pl_4='Neurochirurgie')
        segment.admit_date_time = '20260320140000'

        serialized = segment.serialize()
        expected = 'PV1||I|Südflügel^Raum 401^Bett 1^Orthopädie||||ARZ100^Müller^Björn^^^Dr.^med.|ARZ200^Bäcker^Günther^^^Dr.^med.|ARZ300^Schröder^Jürgen^^^Dr.^med.||Nordflügel^Raum 502^Bett 2^Innere Medizin||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260320140000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A03()

        message.msh.sending_application = HD(hd_1='KLINIK_SND')
        message.msh.sending_facility = HD(hd_1='STÄDTISCH_KH')
        message.msh.receiving_application = HD(hd_1='LABOR_EMP')
        message.msh.receiving_facility = HD(hd_1='RÖNTGEN_KH')
        message.msh.date_time_of_message = '20260320140000'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        message.msh.message_control_id = 'CTL00003'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.6')

        message.evn.recorded_date_time = '20260320140000'

        message.pid.patient_identifier_list = CX(cx_1='PT7890', cx_4='Löwenklinik')
        message.pid.patient_name = XPN(xpn_1='Grünwald', xpn_2='Käthe', xpn_3='Ännchen', xpn_5='Frau')
        message.pid.date_time_of_birth = '19830214'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = XAD(xad_1='Böttcherstraße 47', xad_3='Nürnberg', xad_5='90402')

        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='Südflügel', pl_2='Raum 401', pl_3='Bett 1', pl_4='Orthopädie')
        message.pv1.attending_doctor = XCN(xcn_1='ARZ100', xcn_2='Müller', xcn_3='Björn', xcn_6='Dr.', xcn_8='med.')
        message.pv1.referring_doctor = XCN(xcn_1='ARZ200', xcn_2='Bäcker', xcn_3='Günther', xcn_6='Dr.', xcn_8='med.')
        message.pv1.consulting_doctor = XCN(xcn_1='ARZ300', xcn_2='Schröder', xcn_3='Jürgen', xcn_6='Dr.', xcn_8='med.')
        message.pv1.temporary_location = PL(pl_1='Nordflügel', pl_2='Raum 502', pl_3='Bett 2', pl_4='Innere Medizin')
        message.pv1.visit_number = CX(cx_1='FALL7890')
        message.pv1.pending_location = PL(pl_1='Westflügel', pl_2='Raum 603', pl_3='Bett 3', pl_4='Neurochirurgie')
        message.pv1.admit_date_time = '20260320140000'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_clinical_04 = 'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260321100000||ADT^A04^ADT_A01|CTL00004|P|2.6\rEVN|A04|20260321100000\rPID|||PT7890^^^Löwenklinik||Grünwald^Käthe^Ännchen^^Frau||19830214|F|||Böttcherstraße 47^^Nürnberg^^90402||^^PH^09111234567~^^CP^01761234567~^^Internet^kaethe.gruenwald@yähoo.de\rPV1||I|Südflügel^Raum 401^Bett 1^Orthopädie||||ARZ100^Müller^Björn^^^Dr.^med.|ARZ200^Bäcker^Günther^^^Dr.^med.|ARZ300^Schröder^Jürgen^^^Dr.^med.||Nordflügel^Raum 502^Bett 2^Innere Medizin||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260321100000\rIN1|1|0|KV001|BÜRGERKRANKENVERSICHERUNG|Königstraße 88^^München^^80331||||||||||||||||||||||||||||||||||||||||||||49'

class Test_de_cgm_clinical_04_4_ADT_A04_ambulante_Registrierung_outpatient_registration_with_insurance(unittest.TestCase):
    """ 4. ADT^A04 - ambulante Registrierung (outpatient registration) with insurance
    Source: support.thieme-compliance.de - HL7-Nachrichtentyp ADT, Beispielnachricht A04
    URL: https://support.thieme-compliance.de/de/ECP/Admin/hl7_adt-nachrichten.html
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KLINIK_SND')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'STÄDTISCH_KH')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'LABOR_EMP')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'RÖNTGEN_KH')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260321100000')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A04')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'CTL00004')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.6')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '20260321100000')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, 'PT7890')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Löwenklinik')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Grünwald')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Käthe')

# ################################################################################################################

    def test_navigate_PID_5_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PID.5.3')
        self.assertEqual(result, 'Ännchen')

# ################################################################################################################

    def test_navigate_PID_5_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PID.5.5')
        self.assertEqual(result, 'Frau')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19830214')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Böttcherstraße 47')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Nürnberg')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '90402')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'Südflügel')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, 'Raum 401')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, 'Bett 1')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'Orthopädie')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, 'ARZ100')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Müller')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Björn')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.7.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.8')
        self.assertEqual(result, 'ARZ200')

# ################################################################################################################

    def test_navigate_PV1_8_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.8.2')
        self.assertEqual(result, 'Bäcker')

# ################################################################################################################

    def test_navigate_PV1_8_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.8.3')
        self.assertEqual(result, 'Günther')

# ################################################################################################################

    def test_navigate_PV1_8_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.8.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_8_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.8.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.9')
        self.assertEqual(result, 'ARZ300')

# ################################################################################################################

    def test_navigate_PV1_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.9.2')
        self.assertEqual(result, 'Schröder')

# ################################################################################################################

    def test_navigate_PV1_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.9.3')
        self.assertEqual(result, 'Jürgen')

# ################################################################################################################

    def test_navigate_PV1_9_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.9.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_9_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.9.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.11')
        self.assertEqual(result, 'Nordflügel')

# ################################################################################################################

    def test_navigate_PV1_11_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.11.2')
        self.assertEqual(result, 'Raum 502')

# ################################################################################################################

    def test_navigate_PV1_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.11.3')
        self.assertEqual(result, 'Bett 2')

# ################################################################################################################

    def test_navigate_PV1_11_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.11.4')
        self.assertEqual(result, 'Innere Medizin')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, 'FALL7890')

# ################################################################################################################

    def test_navigate_PV1_42(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.42')
        self.assertEqual(result, 'Westflügel')

# ################################################################################################################

    def test_navigate_PV1_42_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.42.2')
        self.assertEqual(result, 'Raum 603')

# ################################################################################################################

    def test_navigate_PV1_42_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.42.3')
        self.assertEqual(result, 'Bett 3')

# ################################################################################################################

    def test_navigate_PV1_42_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.42.4')
        self.assertEqual(result, 'Neurochirurgie')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '20260321100000')

# ################################################################################################################

    def test_navigate_IN1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('IN1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_IN1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('IN1.2')
        self.assertEqual(result, '0')

# ################################################################################################################

    def test_navigate_IN1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('IN1.3')
        self.assertEqual(result, 'KV001')

# ################################################################################################################

    def test_navigate_IN1_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('IN1.4')
        self.assertEqual(result, 'BÜRGERKRANKENVERSICHERUNG')

# ################################################################################################################

    def test_navigate_IN1_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('IN1.5')
        self.assertEqual(result, 'Königstraße 88')

# ################################################################################################################

    def test_navigate_IN1_5_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('IN1.5.3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_IN1_5_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('IN1.5.5')
        self.assertEqual(result, '80331')

# ################################################################################################################

    def test_navigate_IN1_49(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_04, validate=False)
        result = message.get('IN1.49')
        self.assertEqual(result, '49')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KLINIK_SND')
        segment.sending_facility = HD(hd_1='STÄDTISCH_KH')
        segment.receiving_application = HD(hd_1='LABOR_EMP')
        segment.receiving_facility = HD(hd_1='RÖNTGEN_KH')
        segment.date_time_of_message = '20260321100000'
        segment.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        segment.message_control_id = 'CTL00004'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.6')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260321100000||ADT^A04^ADT_A01|CTL00004|P|2.6'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '20260321100000'

        serialized = segment.serialize()
        expected = 'EVN|A04|20260321100000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='PT7890', cx_4='Löwenklinik')
        segment.patient_name = XPN(xpn_1='Grünwald', xpn_2='Käthe', xpn_3='Ännchen', xpn_5='Frau')
        segment.date_time_of_birth = '19830214'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Böttcherstraße 47', xad_3='Nürnberg', xad_5='90402')

        serialized = segment.serialize()
        expected = 'PID|||PT7890^^^Löwenklinik||Grünwald^Käthe^Ännchen^^Frau||19830214|F|||Böttcherstraße 47^^Nürnberg^^90402||^^PH^09111234567~^^CP^01761234567~^^Internet^kaethe.gruenwald@yähoo.de'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='Südflügel', pl_2='Raum 401', pl_3='Bett 1', pl_4='Orthopädie')
        segment.attending_doctor = XCN(xcn_1='ARZ100', xcn_2='Müller', xcn_3='Björn', xcn_6='Dr.', xcn_8='med.')
        segment.referring_doctor = XCN(xcn_1='ARZ200', xcn_2='Bäcker', xcn_3='Günther', xcn_6='Dr.', xcn_8='med.')
        segment.consulting_doctor = XCN(xcn_1='ARZ300', xcn_2='Schröder', xcn_3='Jürgen', xcn_6='Dr.', xcn_8='med.')
        segment.temporary_location = PL(pl_1='Nordflügel', pl_2='Raum 502', pl_3='Bett 2', pl_4='Innere Medizin')
        segment.visit_number = CX(cx_1='FALL7890')
        segment.pending_location = PL(pl_1='Westflügel', pl_2='Raum 603', pl_3='Bett 3', pl_4='Neurochirurgie')
        segment.admit_date_time = '20260321100000'

        serialized = segment.serialize()
        expected = 'PV1||I|Südflügel^Raum 401^Bett 1^Orthopädie||||ARZ100^Müller^Björn^^^Dr.^med.|ARZ200^Bäcker^Günther^^^Dr.^med.|ARZ300^Schröder^Jürgen^^^Dr.^med.||Nordflügel^Raum 502^Bett 2^Innere Medizin||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260321100000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_IN1(self) -> 'None':
        segment = IN1()

        segment.set_id_in1 = '1'
        segment.health_plan_id = CWE(cwe_1='0')
        segment.insurance_company_id = CX(cx_1='KV001')
        segment.insurance_company_name = XON(xon_1='BÜRGERKRANKENVERSICHERUNG')
        segment.insurance_company_address = XAD(xad_1='Königstraße 88', xad_3='München', xad_5='80331')
        segment.insureds_id_number = CX(cx_1='49')

        serialized = segment.serialize()
        expected = 'IN1|1|0|KV001|BÜRGERKRANKENVERSICHERUNG|Königstraße 88^^München^^80331||||||||||||||||||||||||||||||||||||||||||||49'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A01()

        message.msh.sending_application = HD(hd_1='KLINIK_SND')
        message.msh.sending_facility = HD(hd_1='STÄDTISCH_KH')
        message.msh.receiving_application = HD(hd_1='LABOR_EMP')
        message.msh.receiving_facility = HD(hd_1='RÖNTGEN_KH')
        message.msh.date_time_of_message = '20260321100000'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        message.msh.message_control_id = 'CTL00004'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.6')

        message.evn.recorded_date_time = '20260321100000'

        message.pid.patient_identifier_list = CX(cx_1='PT7890', cx_4='Löwenklinik')
        message.pid.patient_name = XPN(xpn_1='Grünwald', xpn_2='Käthe', xpn_3='Ännchen', xpn_5='Frau')
        message.pid.date_time_of_birth = '19830214'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = XAD(xad_1='Böttcherstraße 47', xad_3='Nürnberg', xad_5='90402')

        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='Südflügel', pl_2='Raum 401', pl_3='Bett 1', pl_4='Orthopädie')
        message.pv1.attending_doctor = XCN(xcn_1='ARZ100', xcn_2='Müller', xcn_3='Björn', xcn_6='Dr.', xcn_8='med.')
        message.pv1.referring_doctor = XCN(xcn_1='ARZ200', xcn_2='Bäcker', xcn_3='Günther', xcn_6='Dr.', xcn_8='med.')
        message.pv1.consulting_doctor = XCN(xcn_1='ARZ300', xcn_2='Schröder', xcn_3='Jürgen', xcn_6='Dr.', xcn_8='med.')
        message.pv1.temporary_location = PL(pl_1='Nordflügel', pl_2='Raum 502', pl_3='Bett 2', pl_4='Innere Medizin')
        message.pv1.visit_number = CX(cx_1='FALL7890')
        message.pv1.pending_location = PL(pl_1='Westflügel', pl_2='Raum 603', pl_3='Bett 3', pl_4='Neurochirurgie')
        message.pv1.admit_date_time = '20260321100000'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_clinical_05 = 'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260322080000||ADT^A05^ADT_A05|CTL00005|P|2.6\rEVN|A05|20260322080000\rPID|||PT7890^^^Löwenklinik||Grünwald^Käthe^Ännchen^^Frau||19830214|F|||Böttcherstraße 47^^Nürnberg^^90402||^^PH^09111234567~^^CP^01761234567~^^Internet^kaethe.gruenwald@yähoo.de\rPV1||I|Südflügel^Raum 401^Bett 1^Orthopädie||||ARZ100^Müller^Björn^^^Dr.^med.|ARZ200^Bäcker^Günther^^^Dr.^med.|ARZ300^Schröder^Jürgen^^^Dr.^med.||Nordflügel^Raum 502^Bett 2^Innere Medizin||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260322080000\rIN1|1|0|KV001|BÜRGERKRANKENVERSICHERUNG|Königstraße 88^^München^^80331||||||||||||||||||||||||||||||||||||||||||||49'

class Test_de_cgm_clinical_05_5_ADT_A05_Voraufnahme_pre_admission_with_insurance(unittest.TestCase):
    """ 5. ADT^A05 - Voraufnahme (pre-admission) with insurance
    Source: support.thieme-compliance.de - HL7-Nachrichtentyp ADT, Beispielnachricht A05
    URL: https://support.thieme-compliance.de/de/ECP/Admin/hl7_adt-nachrichten.html
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        self.assertIsInstance(message, ADT_A05)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A05')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KLINIK_SND')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'STÄDTISCH_KH')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'LABOR_EMP')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'RÖNTGEN_KH')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260322080000')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A05')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A05')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'CTL00005')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.6')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '20260322080000')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, 'PT7890')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Löwenklinik')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Grünwald')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Käthe')

# ################################################################################################################

    def test_navigate_PID_5_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PID.5.3')
        self.assertEqual(result, 'Ännchen')

# ################################################################################################################

    def test_navigate_PID_5_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PID.5.5')
        self.assertEqual(result, 'Frau')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19830214')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Böttcherstraße 47')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Nürnberg')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '90402')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'Südflügel')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, 'Raum 401')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, 'Bett 1')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'Orthopädie')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, 'ARZ100')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Müller')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Björn')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.7.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.8')
        self.assertEqual(result, 'ARZ200')

# ################################################################################################################

    def test_navigate_PV1_8_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.8.2')
        self.assertEqual(result, 'Bäcker')

# ################################################################################################################

    def test_navigate_PV1_8_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.8.3')
        self.assertEqual(result, 'Günther')

# ################################################################################################################

    def test_navigate_PV1_8_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.8.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_8_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.8.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.9')
        self.assertEqual(result, 'ARZ300')

# ################################################################################################################

    def test_navigate_PV1_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.9.2')
        self.assertEqual(result, 'Schröder')

# ################################################################################################################

    def test_navigate_PV1_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.9.3')
        self.assertEqual(result, 'Jürgen')

# ################################################################################################################

    def test_navigate_PV1_9_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.9.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_9_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.9.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.11')
        self.assertEqual(result, 'Nordflügel')

# ################################################################################################################

    def test_navigate_PV1_11_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.11.2')
        self.assertEqual(result, 'Raum 502')

# ################################################################################################################

    def test_navigate_PV1_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.11.3')
        self.assertEqual(result, 'Bett 2')

# ################################################################################################################

    def test_navigate_PV1_11_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.11.4')
        self.assertEqual(result, 'Innere Medizin')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, 'FALL7890')

# ################################################################################################################

    def test_navigate_PV1_42(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.42')
        self.assertEqual(result, 'Westflügel')

# ################################################################################################################

    def test_navigate_PV1_42_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.42.2')
        self.assertEqual(result, 'Raum 603')

# ################################################################################################################

    def test_navigate_PV1_42_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.42.3')
        self.assertEqual(result, 'Bett 3')

# ################################################################################################################

    def test_navigate_PV1_42_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.42.4')
        self.assertEqual(result, 'Neurochirurgie')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '20260322080000')

# ################################################################################################################

    def test_navigate_IN1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('IN1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_IN1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('IN1.2')
        self.assertEqual(result, '0')

# ################################################################################################################

    def test_navigate_IN1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('IN1.3')
        self.assertEqual(result, 'KV001')

# ################################################################################################################

    def test_navigate_IN1_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('IN1.4')
        self.assertEqual(result, 'BÜRGERKRANKENVERSICHERUNG')

# ################################################################################################################

    def test_navigate_IN1_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('IN1.5')
        self.assertEqual(result, 'Königstraße 88')

# ################################################################################################################

    def test_navigate_IN1_5_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('IN1.5.3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_IN1_5_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('IN1.5.5')
        self.assertEqual(result, '80331')

# ################################################################################################################

    def test_navigate_IN1_49(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_05, validate=False)
        result = message.get('IN1.49')
        self.assertEqual(result, '49')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KLINIK_SND')
        segment.sending_facility = HD(hd_1='STÄDTISCH_KH')
        segment.receiving_application = HD(hd_1='LABOR_EMP')
        segment.receiving_facility = HD(hd_1='RÖNTGEN_KH')
        segment.date_time_of_message = '20260322080000'
        segment.message_type = MSG(msg_1='ADT', msg_2='A05', msg_3='ADT_A05')
        segment.message_control_id = 'CTL00005'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.6')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260322080000||ADT^A05^ADT_A05|CTL00005|P|2.6'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '20260322080000'

        serialized = segment.serialize()
        expected = 'EVN|A05|20260322080000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='PT7890', cx_4='Löwenklinik')
        segment.patient_name = XPN(xpn_1='Grünwald', xpn_2='Käthe', xpn_3='Ännchen', xpn_5='Frau')
        segment.date_time_of_birth = '19830214'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Böttcherstraße 47', xad_3='Nürnberg', xad_5='90402')

        serialized = segment.serialize()
        expected = 'PID|||PT7890^^^Löwenklinik||Grünwald^Käthe^Ännchen^^Frau||19830214|F|||Böttcherstraße 47^^Nürnberg^^90402||^^PH^09111234567~^^CP^01761234567~^^Internet^kaethe.gruenwald@yähoo.de'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='Südflügel', pl_2='Raum 401', pl_3='Bett 1', pl_4='Orthopädie')
        segment.attending_doctor = XCN(xcn_1='ARZ100', xcn_2='Müller', xcn_3='Björn', xcn_6='Dr.', xcn_8='med.')
        segment.referring_doctor = XCN(xcn_1='ARZ200', xcn_2='Bäcker', xcn_3='Günther', xcn_6='Dr.', xcn_8='med.')
        segment.consulting_doctor = XCN(xcn_1='ARZ300', xcn_2='Schröder', xcn_3='Jürgen', xcn_6='Dr.', xcn_8='med.')
        segment.temporary_location = PL(pl_1='Nordflügel', pl_2='Raum 502', pl_3='Bett 2', pl_4='Innere Medizin')
        segment.visit_number = CX(cx_1='FALL7890')
        segment.pending_location = PL(pl_1='Westflügel', pl_2='Raum 603', pl_3='Bett 3', pl_4='Neurochirurgie')
        segment.admit_date_time = '20260322080000'

        serialized = segment.serialize()
        expected = 'PV1||I|Südflügel^Raum 401^Bett 1^Orthopädie||||ARZ100^Müller^Björn^^^Dr.^med.|ARZ200^Bäcker^Günther^^^Dr.^med.|ARZ300^Schröder^Jürgen^^^Dr.^med.||Nordflügel^Raum 502^Bett 2^Innere Medizin||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260322080000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_IN1(self) -> 'None':
        segment = IN1()

        segment.set_id_in1 = '1'
        segment.health_plan_id = CWE(cwe_1='0')
        segment.insurance_company_id = CX(cx_1='KV001')
        segment.insurance_company_name = XON(xon_1='BÜRGERKRANKENVERSICHERUNG')
        segment.insurance_company_address = XAD(xad_1='Königstraße 88', xad_3='München', xad_5='80331')
        segment.insureds_id_number = CX(cx_1='49')

        serialized = segment.serialize()
        expected = 'IN1|1|0|KV001|BÜRGERKRANKENVERSICHERUNG|Königstraße 88^^München^^80331||||||||||||||||||||||||||||||||||||||||||||49'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A05()

        message.msh.sending_application = HD(hd_1='KLINIK_SND')
        message.msh.sending_facility = HD(hd_1='STÄDTISCH_KH')
        message.msh.receiving_application = HD(hd_1='LABOR_EMP')
        message.msh.receiving_facility = HD(hd_1='RÖNTGEN_KH')
        message.msh.date_time_of_message = '20260322080000'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A05', msg_3='ADT_A05')
        message.msh.message_control_id = 'CTL00005'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.6')

        message.evn.recorded_date_time = '20260322080000'

        message.pid.patient_identifier_list = CX(cx_1='PT7890', cx_4='Löwenklinik')
        message.pid.patient_name = XPN(xpn_1='Grünwald', xpn_2='Käthe', xpn_3='Ännchen', xpn_5='Frau')
        message.pid.date_time_of_birth = '19830214'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = XAD(xad_1='Böttcherstraße 47', xad_3='Nürnberg', xad_5='90402')

        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='Südflügel', pl_2='Raum 401', pl_3='Bett 1', pl_4='Orthopädie')
        message.pv1.attending_doctor = XCN(xcn_1='ARZ100', xcn_2='Müller', xcn_3='Björn', xcn_6='Dr.', xcn_8='med.')
        message.pv1.referring_doctor = XCN(xcn_1='ARZ200', xcn_2='Bäcker', xcn_3='Günther', xcn_6='Dr.', xcn_8='med.')
        message.pv1.consulting_doctor = XCN(xcn_1='ARZ300', xcn_2='Schröder', xcn_3='Jürgen', xcn_6='Dr.', xcn_8='med.')
        message.pv1.temporary_location = PL(pl_1='Nordflügel', pl_2='Raum 502', pl_3='Bett 2', pl_4='Innere Medizin')
        message.pv1.visit_number = CX(cx_1='FALL7890')
        message.pv1.pending_location = PL(pl_1='Westflügel', pl_2='Raum 603', pl_3='Bett 3', pl_4='Neurochirurgie')
        message.pv1.admit_date_time = '20260322080000'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_clinical_06 = 'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260323090000||ADT^A08^ADT_A01|CTL00006|P|2.6\rEVN|A08|20260323090000\rPID|||PT7890^^^Löwenklinik||Grünwald^Käthe^Märta^^Frau||19820501|F|||Überlandstraße 99^^Würzburg^^97070||^^PH^09319876543~^^CP^01769876543~^^Internet^maerta.gruenwald@yähoo.de\rPV1||I|Südflügel^Raum 401^Bett 1^Orthopädie||||ARZ100^Müller^Björn^^^Dr.^med.|ARZ200^Bäcker^Günther^^^Dr.^med.|ARZ300^Schröder^Jürgen^^^Dr.^med.||Nordflügel^Raum 502^Bett 2^Innere Medizin||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260323090000\rIN1|1|0|KV001|BÜRGERKRANKENVERSICHERUNG|Königstraße 88^^München^^80331||||||||||||||||||||||||||||||||||||||||||||49'

class Test_de_cgm_clinical_06_6_ADT_A08_nderung_Patientendaten_update_patient_with_insurance(unittest.TestCase):
    """ 6. ADT^A08 - Änderung Patientendaten (update patient) with insurance
    Source: support.thieme-compliance.de - HL7-Nachrichtentyp ADT, Beispielnachricht A08
    URL: https://support.thieme-compliance.de/de/ECP/Admin/hl7_adt-nachrichten.html
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KLINIK_SND')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'STÄDTISCH_KH')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'LABOR_EMP')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'RÖNTGEN_KH')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260323090000')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A08')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'CTL00006')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.6')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '20260323090000')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, 'PT7890')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Löwenklinik')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Grünwald')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Käthe')

# ################################################################################################################

    def test_navigate_PID_5_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PID.5.3')
        self.assertEqual(result, 'Märta')

# ################################################################################################################

    def test_navigate_PID_5_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PID.5.5')
        self.assertEqual(result, 'Frau')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19820501')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Überlandstraße 99')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Würzburg')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '97070')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'Südflügel')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, 'Raum 401')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, 'Bett 1')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'Orthopädie')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, 'ARZ100')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Müller')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Björn')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.7.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.8')
        self.assertEqual(result, 'ARZ200')

# ################################################################################################################

    def test_navigate_PV1_8_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.8.2')
        self.assertEqual(result, 'Bäcker')

# ################################################################################################################

    def test_navigate_PV1_8_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.8.3')
        self.assertEqual(result, 'Günther')

# ################################################################################################################

    def test_navigate_PV1_8_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.8.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_8_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.8.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.9')
        self.assertEqual(result, 'ARZ300')

# ################################################################################################################

    def test_navigate_PV1_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.9.2')
        self.assertEqual(result, 'Schröder')

# ################################################################################################################

    def test_navigate_PV1_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.9.3')
        self.assertEqual(result, 'Jürgen')

# ################################################################################################################

    def test_navigate_PV1_9_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.9.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_9_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.9.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.11')
        self.assertEqual(result, 'Nordflügel')

# ################################################################################################################

    def test_navigate_PV1_11_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.11.2')
        self.assertEqual(result, 'Raum 502')

# ################################################################################################################

    def test_navigate_PV1_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.11.3')
        self.assertEqual(result, 'Bett 2')

# ################################################################################################################

    def test_navigate_PV1_11_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.11.4')
        self.assertEqual(result, 'Innere Medizin')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, 'FALL7890')

# ################################################################################################################

    def test_navigate_PV1_42(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.42')
        self.assertEqual(result, 'Westflügel')

# ################################################################################################################

    def test_navigate_PV1_42_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.42.2')
        self.assertEqual(result, 'Raum 603')

# ################################################################################################################

    def test_navigate_PV1_42_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.42.3')
        self.assertEqual(result, 'Bett 3')

# ################################################################################################################

    def test_navigate_PV1_42_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.42.4')
        self.assertEqual(result, 'Neurochirurgie')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '20260323090000')

# ################################################################################################################

    def test_navigate_IN1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('IN1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_IN1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('IN1.2')
        self.assertEqual(result, '0')

# ################################################################################################################

    def test_navigate_IN1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('IN1.3')
        self.assertEqual(result, 'KV001')

# ################################################################################################################

    def test_navigate_IN1_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('IN1.4')
        self.assertEqual(result, 'BÜRGERKRANKENVERSICHERUNG')

# ################################################################################################################

    def test_navigate_IN1_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('IN1.5')
        self.assertEqual(result, 'Königstraße 88')

# ################################################################################################################

    def test_navigate_IN1_5_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('IN1.5.3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_IN1_5_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('IN1.5.5')
        self.assertEqual(result, '80331')

# ################################################################################################################

    def test_navigate_IN1_49(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_06, validate=False)
        result = message.get('IN1.49')
        self.assertEqual(result, '49')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KLINIK_SND')
        segment.sending_facility = HD(hd_1='STÄDTISCH_KH')
        segment.receiving_application = HD(hd_1='LABOR_EMP')
        segment.receiving_facility = HD(hd_1='RÖNTGEN_KH')
        segment.date_time_of_message = '20260323090000'
        segment.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        segment.message_control_id = 'CTL00006'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.6')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260323090000||ADT^A08^ADT_A01|CTL00006|P|2.6'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '20260323090000'

        serialized = segment.serialize()
        expected = 'EVN|A08|20260323090000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='PT7890', cx_4='Löwenklinik')
        segment.patient_name = XPN(xpn_1='Grünwald', xpn_2='Käthe', xpn_3='Märta', xpn_5='Frau')
        segment.date_time_of_birth = '19820501'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Überlandstraße 99', xad_3='Würzburg', xad_5='97070')

        serialized = segment.serialize()
        expected = 'PID|||PT7890^^^Löwenklinik||Grünwald^Käthe^Märta^^Frau||19820501|F|||Überlandstraße 99^^Würzburg^^97070||^^PH^09319876543~^^CP^01769876543~^^Internet^maerta.gruenwald@yähoo.de'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='Südflügel', pl_2='Raum 401', pl_3='Bett 1', pl_4='Orthopädie')
        segment.attending_doctor = XCN(xcn_1='ARZ100', xcn_2='Müller', xcn_3='Björn', xcn_6='Dr.', xcn_8='med.')
        segment.referring_doctor = XCN(xcn_1='ARZ200', xcn_2='Bäcker', xcn_3='Günther', xcn_6='Dr.', xcn_8='med.')
        segment.consulting_doctor = XCN(xcn_1='ARZ300', xcn_2='Schröder', xcn_3='Jürgen', xcn_6='Dr.', xcn_8='med.')
        segment.temporary_location = PL(pl_1='Nordflügel', pl_2='Raum 502', pl_3='Bett 2', pl_4='Innere Medizin')
        segment.visit_number = CX(cx_1='FALL7890')
        segment.pending_location = PL(pl_1='Westflügel', pl_2='Raum 603', pl_3='Bett 3', pl_4='Neurochirurgie')
        segment.admit_date_time = '20260323090000'

        serialized = segment.serialize()
        expected = 'PV1||I|Südflügel^Raum 401^Bett 1^Orthopädie||||ARZ100^Müller^Björn^^^Dr.^med.|ARZ200^Bäcker^Günther^^^Dr.^med.|ARZ300^Schröder^Jürgen^^^Dr.^med.||Nordflügel^Raum 502^Bett 2^Innere Medizin||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260323090000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_IN1(self) -> 'None':
        segment = IN1()

        segment.set_id_in1 = '1'
        segment.health_plan_id = CWE(cwe_1='0')
        segment.insurance_company_id = CX(cx_1='KV001')
        segment.insurance_company_name = XON(xon_1='BÜRGERKRANKENVERSICHERUNG')
        segment.insurance_company_address = XAD(xad_1='Königstraße 88', xad_3='München', xad_5='80331')
        segment.insureds_id_number = CX(cx_1='49')

        serialized = segment.serialize()
        expected = 'IN1|1|0|KV001|BÜRGERKRANKENVERSICHERUNG|Königstraße 88^^München^^80331||||||||||||||||||||||||||||||||||||||||||||49'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A01()

        message.msh.sending_application = HD(hd_1='KLINIK_SND')
        message.msh.sending_facility = HD(hd_1='STÄDTISCH_KH')
        message.msh.receiving_application = HD(hd_1='LABOR_EMP')
        message.msh.receiving_facility = HD(hd_1='RÖNTGEN_KH')
        message.msh.date_time_of_message = '20260323090000'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        message.msh.message_control_id = 'CTL00006'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.6')

        message.evn.recorded_date_time = '20260323090000'

        message.pid.patient_identifier_list = CX(cx_1='PT7890', cx_4='Löwenklinik')
        message.pid.patient_name = XPN(xpn_1='Grünwald', xpn_2='Käthe', xpn_3='Märta', xpn_5='Frau')
        message.pid.date_time_of_birth = '19820501'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = XAD(xad_1='Überlandstraße 99', xad_3='Würzburg', xad_5='97070')

        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='Südflügel', pl_2='Raum 401', pl_3='Bett 1', pl_4='Orthopädie')
        message.pv1.attending_doctor = XCN(xcn_1='ARZ100', xcn_2='Müller', xcn_3='Björn', xcn_6='Dr.', xcn_8='med.')
        message.pv1.referring_doctor = XCN(xcn_1='ARZ200', xcn_2='Bäcker', xcn_3='Günther', xcn_6='Dr.', xcn_8='med.')
        message.pv1.consulting_doctor = XCN(xcn_1='ARZ300', xcn_2='Schröder', xcn_3='Jürgen', xcn_6='Dr.', xcn_8='med.')
        message.pv1.temporary_location = PL(pl_1='Nordflügel', pl_2='Raum 502', pl_3='Bett 2', pl_4='Innere Medizin')
        message.pv1.visit_number = CX(cx_1='FALL7890')
        message.pv1.pending_location = PL(pl_1='Westflügel', pl_2='Raum 603', pl_3='Bett 3', pl_4='Neurochirurgie')
        message.pv1.admit_date_time = '20260323090000'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_clinical_07 = 'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260324110000||ADT^A09^ADT_A09|CTL00007|P|2.6\rEVN|A09|20260324110000\rPID|||PT7890^^^Löwenklinik||Grünwald^Käthe^Ännchen^^Frau||19830214|F|||Böttcherstraße 47^^Nürnberg^^90402||^^PH^09111234567~^^CP^01761234567~^^Internet^kaethe.gruenwald@yähoo.de\rPV1||I|Nordflügel^Raum 502^Bett 2^Innere Medizin||||ARZ100^Müller^Björn^^^Dr.^med.|ARZ200^Bäcker^Günther^^^Dr.^med.|ARZ300^Schröder^Jürgen^^^Dr.^med.||Südflügel^Raum 401^Bett 1^Orthopädie||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260324110000'

class Test_de_cgm_clinical_07_7_ADT_A09_Patient_verl_sst_Einrichtung_patient_departing(unittest.TestCase):
    """ 7. ADT^A09 - Patient verlässt Einrichtung (patient departing)
    Source: support.thieme-compliance.de - HL7-Nachrichtentyp ADT, Beispielnachricht A09
    URL: https://support.thieme-compliance.de/de/ECP/Admin/hl7_adt-nachrichten.html
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        self.assertIsInstance(message, ADT_A09)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A09')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KLINIK_SND')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'STÄDTISCH_KH')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'LABOR_EMP')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'RÖNTGEN_KH')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260324110000')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A09')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A09')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'CTL00007')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.6')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '20260324110000')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, 'PT7890')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Löwenklinik')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Grünwald')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Käthe')

# ################################################################################################################

    def test_navigate_PID_5_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PID.5.3')
        self.assertEqual(result, 'Ännchen')

# ################################################################################################################

    def test_navigate_PID_5_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PID.5.5')
        self.assertEqual(result, 'Frau')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19830214')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Böttcherstraße 47')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Nürnberg')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '90402')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'Nordflügel')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, 'Raum 502')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, 'Bett 2')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'Innere Medizin')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, 'ARZ100')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Müller')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Björn')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.7.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.8')
        self.assertEqual(result, 'ARZ200')

# ################################################################################################################

    def test_navigate_PV1_8_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.8.2')
        self.assertEqual(result, 'Bäcker')

# ################################################################################################################

    def test_navigate_PV1_8_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.8.3')
        self.assertEqual(result, 'Günther')

# ################################################################################################################

    def test_navigate_PV1_8_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.8.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_8_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.8.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.9')
        self.assertEqual(result, 'ARZ300')

# ################################################################################################################

    def test_navigate_PV1_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.9.2')
        self.assertEqual(result, 'Schröder')

# ################################################################################################################

    def test_navigate_PV1_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.9.3')
        self.assertEqual(result, 'Jürgen')

# ################################################################################################################

    def test_navigate_PV1_9_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.9.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_9_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.9.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.11')
        self.assertEqual(result, 'Südflügel')

# ################################################################################################################

    def test_navigate_PV1_11_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.11.2')
        self.assertEqual(result, 'Raum 401')

# ################################################################################################################

    def test_navigate_PV1_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.11.3')
        self.assertEqual(result, 'Bett 1')

# ################################################################################################################

    def test_navigate_PV1_11_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.11.4')
        self.assertEqual(result, 'Orthopädie')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, 'FALL7890')

# ################################################################################################################

    def test_navigate_PV1_42(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.42')
        self.assertEqual(result, 'Westflügel')

# ################################################################################################################

    def test_navigate_PV1_42_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.42.2')
        self.assertEqual(result, 'Raum 603')

# ################################################################################################################

    def test_navigate_PV1_42_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.42.3')
        self.assertEqual(result, 'Bett 3')

# ################################################################################################################

    def test_navigate_PV1_42_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.42.4')
        self.assertEqual(result, 'Neurochirurgie')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_07, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '20260324110000')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KLINIK_SND')
        segment.sending_facility = HD(hd_1='STÄDTISCH_KH')
        segment.receiving_application = HD(hd_1='LABOR_EMP')
        segment.receiving_facility = HD(hd_1='RÖNTGEN_KH')
        segment.date_time_of_message = '20260324110000'
        segment.message_type = MSG(msg_1='ADT', msg_2='A09', msg_3='ADT_A09')
        segment.message_control_id = 'CTL00007'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.6')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260324110000||ADT^A09^ADT_A09|CTL00007|P|2.6'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '20260324110000'

        serialized = segment.serialize()
        expected = 'EVN|A09|20260324110000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='PT7890', cx_4='Löwenklinik')
        segment.patient_name = XPN(xpn_1='Grünwald', xpn_2='Käthe', xpn_3='Ännchen', xpn_5='Frau')
        segment.date_time_of_birth = '19830214'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Böttcherstraße 47', xad_3='Nürnberg', xad_5='90402')

        serialized = segment.serialize()
        expected = 'PID|||PT7890^^^Löwenklinik||Grünwald^Käthe^Ännchen^^Frau||19830214|F|||Böttcherstraße 47^^Nürnberg^^90402||^^PH^09111234567~^^CP^01761234567~^^Internet^kaethe.gruenwald@yähoo.de'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='Nordflügel', pl_2='Raum 502', pl_3='Bett 2', pl_4='Innere Medizin')
        segment.attending_doctor = XCN(xcn_1='ARZ100', xcn_2='Müller', xcn_3='Björn', xcn_6='Dr.', xcn_8='med.')
        segment.referring_doctor = XCN(xcn_1='ARZ200', xcn_2='Bäcker', xcn_3='Günther', xcn_6='Dr.', xcn_8='med.')
        segment.consulting_doctor = XCN(xcn_1='ARZ300', xcn_2='Schröder', xcn_3='Jürgen', xcn_6='Dr.', xcn_8='med.')
        segment.temporary_location = PL(pl_1='Südflügel', pl_2='Raum 401', pl_3='Bett 1', pl_4='Orthopädie')
        segment.visit_number = CX(cx_1='FALL7890')
        segment.pending_location = PL(pl_1='Westflügel', pl_2='Raum 603', pl_3='Bett 3', pl_4='Neurochirurgie')
        segment.admit_date_time = '20260324110000'

        serialized = segment.serialize()
        expected = 'PV1||I|Nordflügel^Raum 502^Bett 2^Innere Medizin||||ARZ100^Müller^Björn^^^Dr.^med.|ARZ200^Bäcker^Günther^^^Dr.^med.|ARZ300^Schröder^Jürgen^^^Dr.^med.||Südflügel^Raum 401^Bett 1^Orthopädie||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260324110000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A09()

        message.msh.sending_application = HD(hd_1='KLINIK_SND')
        message.msh.sending_facility = HD(hd_1='STÄDTISCH_KH')
        message.msh.receiving_application = HD(hd_1='LABOR_EMP')
        message.msh.receiving_facility = HD(hd_1='RÖNTGEN_KH')
        message.msh.date_time_of_message = '20260324110000'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A09', msg_3='ADT_A09')
        message.msh.message_control_id = 'CTL00007'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.6')

        message.evn.recorded_date_time = '20260324110000'

        message.pid.patient_identifier_list = CX(cx_1='PT7890', cx_4='Löwenklinik')
        message.pid.patient_name = XPN(xpn_1='Grünwald', xpn_2='Käthe', xpn_3='Ännchen', xpn_5='Frau')
        message.pid.date_time_of_birth = '19830214'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = XAD(xad_1='Böttcherstraße 47', xad_3='Nürnberg', xad_5='90402')

        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='Nordflügel', pl_2='Raum 502', pl_3='Bett 2', pl_4='Innere Medizin')
        message.pv1.attending_doctor = XCN(xcn_1='ARZ100', xcn_2='Müller', xcn_3='Björn', xcn_6='Dr.', xcn_8='med.')
        message.pv1.referring_doctor = XCN(xcn_1='ARZ200', xcn_2='Bäcker', xcn_3='Günther', xcn_6='Dr.', xcn_8='med.')
        message.pv1.consulting_doctor = XCN(xcn_1='ARZ300', xcn_2='Schröder', xcn_3='Jürgen', xcn_6='Dr.', xcn_8='med.')
        message.pv1.temporary_location = PL(pl_1='Südflügel', pl_2='Raum 401', pl_3='Bett 1', pl_4='Orthopädie')
        message.pv1.visit_number = CX(cx_1='FALL7890')
        message.pv1.pending_location = PL(pl_1='Westflügel', pl_2='Raum 603', pl_3='Bett 3', pl_4='Neurochirurgie')
        message.pv1.admit_date_time = '20260324110000'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_clinical_08 = 'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260324113000||ADT^A10^ADT_A09|CTL00008|P|2.6\rEVN|A10|20260324113000\rPID|||PT7890^^^Löwenklinik||Grünwald^Käthe^Ännchen^^Frau||19830214|F|||Böttcherstraße 47^^Nürnberg^^90402||^^PH^09111234567~^^CP^01761234567~^^Internet^kaethe.gruenwald@yähoo.de\rPV1||I|Westflügel^Raum 603^Bett 3^Neurochirurgie||||ARZ100^Müller^Björn^^^Dr.^med.|ARZ200^Bäcker^Günther^^^Dr.^med.|ARZ300^Schröder^Jürgen^^^Dr.^med.||Nordflügel^Raum 502^Bett 2^Innere Medizin||||||||FALL7890|||||||||||||||||||||||Südflügel^Raum 401^Bett 1^Orthopädie||20260324113000'

class Test_de_cgm_clinical_08_8_ADT_A10_Patient_erreicht_Einrichtung_patient_arriving(unittest.TestCase):
    """ 8. ADT^A10 - Patient erreicht Einrichtung (patient arriving)
    Source: support.thieme-compliance.de - HL7-Nachrichtentyp ADT, Beispielnachricht A10
    URL: https://support.thieme-compliance.de/de/ECP/Admin/hl7_adt-nachrichten.html
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        self.assertIsInstance(message, ADT_A09)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A09')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KLINIK_SND')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'STÄDTISCH_KH')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'LABOR_EMP')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'RÖNTGEN_KH')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260324113000')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A10')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A09')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'CTL00008')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.6')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '20260324113000')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, 'PT7890')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Löwenklinik')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Grünwald')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Käthe')

# ################################################################################################################

    def test_navigate_PID_5_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PID.5.3')
        self.assertEqual(result, 'Ännchen')

# ################################################################################################################

    def test_navigate_PID_5_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PID.5.5')
        self.assertEqual(result, 'Frau')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19830214')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Böttcherstraße 47')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Nürnberg')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '90402')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'Westflügel')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, 'Raum 603')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, 'Bett 3')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'Neurochirurgie')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, 'ARZ100')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Müller')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Björn')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.7.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.8')
        self.assertEqual(result, 'ARZ200')

# ################################################################################################################

    def test_navigate_PV1_8_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.8.2')
        self.assertEqual(result, 'Bäcker')

# ################################################################################################################

    def test_navigate_PV1_8_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.8.3')
        self.assertEqual(result, 'Günther')

# ################################################################################################################

    def test_navigate_PV1_8_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.8.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_8_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.8.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.9')
        self.assertEqual(result, 'ARZ300')

# ################################################################################################################

    def test_navigate_PV1_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.9.2')
        self.assertEqual(result, 'Schröder')

# ################################################################################################################

    def test_navigate_PV1_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.9.3')
        self.assertEqual(result, 'Jürgen')

# ################################################################################################################

    def test_navigate_PV1_9_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.9.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_9_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.9.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.11')
        self.assertEqual(result, 'Nordflügel')

# ################################################################################################################

    def test_navigate_PV1_11_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.11.2')
        self.assertEqual(result, 'Raum 502')

# ################################################################################################################

    def test_navigate_PV1_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.11.3')
        self.assertEqual(result, 'Bett 2')

# ################################################################################################################

    def test_navigate_PV1_11_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.11.4')
        self.assertEqual(result, 'Innere Medizin')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, 'FALL7890')

# ################################################################################################################

    def test_navigate_PV1_42(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.42')
        self.assertEqual(result, 'Südflügel')

# ################################################################################################################

    def test_navigate_PV1_42_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.42.2')
        self.assertEqual(result, 'Raum 401')

# ################################################################################################################

    def test_navigate_PV1_42_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.42.3')
        self.assertEqual(result, 'Bett 1')

# ################################################################################################################

    def test_navigate_PV1_42_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.42.4')
        self.assertEqual(result, 'Orthopädie')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_08, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '20260324113000')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KLINIK_SND')
        segment.sending_facility = HD(hd_1='STÄDTISCH_KH')
        segment.receiving_application = HD(hd_1='LABOR_EMP')
        segment.receiving_facility = HD(hd_1='RÖNTGEN_KH')
        segment.date_time_of_message = '20260324113000'
        segment.message_type = MSG(msg_1='ADT', msg_2='A10', msg_3='ADT_A09')
        segment.message_control_id = 'CTL00008'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.6')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260324113000||ADT^A10^ADT_A09|CTL00008|P|2.6'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '20260324113000'

        serialized = segment.serialize()
        expected = 'EVN|A10|20260324113000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='PT7890', cx_4='Löwenklinik')
        segment.patient_name = XPN(xpn_1='Grünwald', xpn_2='Käthe', xpn_3='Ännchen', xpn_5='Frau')
        segment.date_time_of_birth = '19830214'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Böttcherstraße 47', xad_3='Nürnberg', xad_5='90402')

        serialized = segment.serialize()
        expected = 'PID|||PT7890^^^Löwenklinik||Grünwald^Käthe^Ännchen^^Frau||19830214|F|||Böttcherstraße 47^^Nürnberg^^90402||^^PH^09111234567~^^CP^01761234567~^^Internet^kaethe.gruenwald@yähoo.de'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='Westflügel', pl_2='Raum 603', pl_3='Bett 3', pl_4='Neurochirurgie')
        segment.attending_doctor = XCN(xcn_1='ARZ100', xcn_2='Müller', xcn_3='Björn', xcn_6='Dr.', xcn_8='med.')
        segment.referring_doctor = XCN(xcn_1='ARZ200', xcn_2='Bäcker', xcn_3='Günther', xcn_6='Dr.', xcn_8='med.')
        segment.consulting_doctor = XCN(xcn_1='ARZ300', xcn_2='Schröder', xcn_3='Jürgen', xcn_6='Dr.', xcn_8='med.')
        segment.temporary_location = PL(pl_1='Nordflügel', pl_2='Raum 502', pl_3='Bett 2', pl_4='Innere Medizin')
        segment.visit_number = CX(cx_1='FALL7890')
        segment.pending_location = PL(pl_1='Südflügel', pl_2='Raum 401', pl_3='Bett 1', pl_4='Orthopädie')
        segment.admit_date_time = '20260324113000'

        serialized = segment.serialize()
        expected = 'PV1||I|Westflügel^Raum 603^Bett 3^Neurochirurgie||||ARZ100^Müller^Björn^^^Dr.^med.|ARZ200^Bäcker^Günther^^^Dr.^med.|ARZ300^Schröder^Jürgen^^^Dr.^med.||Nordflügel^Raum 502^Bett 2^Innere Medizin||||||||FALL7890|||||||||||||||||||||||Südflügel^Raum 401^Bett 1^Orthopädie||20260324113000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A09()

        message.msh.sending_application = HD(hd_1='KLINIK_SND')
        message.msh.sending_facility = HD(hd_1='STÄDTISCH_KH')
        message.msh.receiving_application = HD(hd_1='LABOR_EMP')
        message.msh.receiving_facility = HD(hd_1='RÖNTGEN_KH')
        message.msh.date_time_of_message = '20260324113000'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A10', msg_3='ADT_A09')
        message.msh.message_control_id = 'CTL00008'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.6')

        message.evn.recorded_date_time = '20260324113000'

        message.pid.patient_identifier_list = CX(cx_1='PT7890', cx_4='Löwenklinik')
        message.pid.patient_name = XPN(xpn_1='Grünwald', xpn_2='Käthe', xpn_3='Ännchen', xpn_5='Frau')
        message.pid.date_time_of_birth = '19830214'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = XAD(xad_1='Böttcherstraße 47', xad_3='Nürnberg', xad_5='90402')

        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='Westflügel', pl_2='Raum 603', pl_3='Bett 3', pl_4='Neurochirurgie')
        message.pv1.attending_doctor = XCN(xcn_1='ARZ100', xcn_2='Müller', xcn_3='Björn', xcn_6='Dr.', xcn_8='med.')
        message.pv1.referring_doctor = XCN(xcn_1='ARZ200', xcn_2='Bäcker', xcn_3='Günther', xcn_6='Dr.', xcn_8='med.')
        message.pv1.consulting_doctor = XCN(xcn_1='ARZ300', xcn_2='Schröder', xcn_3='Jürgen', xcn_6='Dr.', xcn_8='med.')
        message.pv1.temporary_location = PL(pl_1='Nordflügel', pl_2='Raum 502', pl_3='Bett 2', pl_4='Innere Medizin')
        message.pv1.visit_number = CX(cx_1='FALL7890')
        message.pv1.pending_location = PL(pl_1='Südflügel', pl_2='Raum 401', pl_3='Bett 1', pl_4='Orthopädie')
        message.pv1.admit_date_time = '20260324113000'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_clinical_09 = 'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260325070000||ADT^A11^ADT_A09|CTL00009|P|2.6\rEVN|A11|20260325070000\rPID|||PT7890^^^Löwenklinik||Grünwald^Käthe^Ännchen^^Frau||19830214|F|||Böttcherstraße 47^^Nürnberg^^90402||^^PH^09111234567~^^CP^01761234567~^^Internet^kaethe.gruenwald@yähoo.de\rPV1||I|Südflügel^Raum 401^Bett 1^Orthopädie||||ARZ100^Müller^Björn^^^Dr.^med.|ARZ200^Bäcker^Günther^^^Dr.^med.|ARZ300^Schröder^Jürgen^^^Dr.^med.||Nordflügel^Raum 502^Bett 2^Innere Medizin||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260325070000'

class Test_de_cgm_clinical_09_9_ADT_A11_Stornierung_Aufnahme_cancel_admit(unittest.TestCase):
    """ 9. ADT^A11 - Stornierung Aufnahme (cancel admit)
    Source: support.thieme-compliance.de - HL7-Nachrichtentyp ADT, Beispielnachricht A11
    URL: https://support.thieme-compliance.de/de/ECP/Admin/hl7_adt-nachrichten.html
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        self.assertIsInstance(message, ADT_A09)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A09')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KLINIK_SND')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'STÄDTISCH_KH')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'LABOR_EMP')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'RÖNTGEN_KH')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260325070000')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A11')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A09')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'CTL00009')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.6')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '20260325070000')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, 'PT7890')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Löwenklinik')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Grünwald')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Käthe')

# ################################################################################################################

    def test_navigate_PID_5_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PID.5.3')
        self.assertEqual(result, 'Ännchen')

# ################################################################################################################

    def test_navigate_PID_5_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PID.5.5')
        self.assertEqual(result, 'Frau')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19830214')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Böttcherstraße 47')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Nürnberg')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '90402')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'Südflügel')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, 'Raum 401')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, 'Bett 1')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'Orthopädie')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, 'ARZ100')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Müller')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Björn')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.7.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.8')
        self.assertEqual(result, 'ARZ200')

# ################################################################################################################

    def test_navigate_PV1_8_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.8.2')
        self.assertEqual(result, 'Bäcker')

# ################################################################################################################

    def test_navigate_PV1_8_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.8.3')
        self.assertEqual(result, 'Günther')

# ################################################################################################################

    def test_navigate_PV1_8_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.8.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_8_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.8.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.9')
        self.assertEqual(result, 'ARZ300')

# ################################################################################################################

    def test_navigate_PV1_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.9.2')
        self.assertEqual(result, 'Schröder')

# ################################################################################################################

    def test_navigate_PV1_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.9.3')
        self.assertEqual(result, 'Jürgen')

# ################################################################################################################

    def test_navigate_PV1_9_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.9.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_9_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.9.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.11')
        self.assertEqual(result, 'Nordflügel')

# ################################################################################################################

    def test_navigate_PV1_11_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.11.2')
        self.assertEqual(result, 'Raum 502')

# ################################################################################################################

    def test_navigate_PV1_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.11.3')
        self.assertEqual(result, 'Bett 2')

# ################################################################################################################

    def test_navigate_PV1_11_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.11.4')
        self.assertEqual(result, 'Innere Medizin')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, 'FALL7890')

# ################################################################################################################

    def test_navigate_PV1_42(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.42')
        self.assertEqual(result, 'Westflügel')

# ################################################################################################################

    def test_navigate_PV1_42_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.42.2')
        self.assertEqual(result, 'Raum 603')

# ################################################################################################################

    def test_navigate_PV1_42_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.42.3')
        self.assertEqual(result, 'Bett 3')

# ################################################################################################################

    def test_navigate_PV1_42_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.42.4')
        self.assertEqual(result, 'Neurochirurgie')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_09, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '20260325070000')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KLINIK_SND')
        segment.sending_facility = HD(hd_1='STÄDTISCH_KH')
        segment.receiving_application = HD(hd_1='LABOR_EMP')
        segment.receiving_facility = HD(hd_1='RÖNTGEN_KH')
        segment.date_time_of_message = '20260325070000'
        segment.message_type = MSG(msg_1='ADT', msg_2='A11', msg_3='ADT_A09')
        segment.message_control_id = 'CTL00009'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.6')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260325070000||ADT^A11^ADT_A09|CTL00009|P|2.6'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '20260325070000'

        serialized = segment.serialize()
        expected = 'EVN|A11|20260325070000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='PT7890', cx_4='Löwenklinik')
        segment.patient_name = XPN(xpn_1='Grünwald', xpn_2='Käthe', xpn_3='Ännchen', xpn_5='Frau')
        segment.date_time_of_birth = '19830214'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Böttcherstraße 47', xad_3='Nürnberg', xad_5='90402')

        serialized = segment.serialize()
        expected = 'PID|||PT7890^^^Löwenklinik||Grünwald^Käthe^Ännchen^^Frau||19830214|F|||Böttcherstraße 47^^Nürnberg^^90402||^^PH^09111234567~^^CP^01761234567~^^Internet^kaethe.gruenwald@yähoo.de'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='Südflügel', pl_2='Raum 401', pl_3='Bett 1', pl_4='Orthopädie')
        segment.attending_doctor = XCN(xcn_1='ARZ100', xcn_2='Müller', xcn_3='Björn', xcn_6='Dr.', xcn_8='med.')
        segment.referring_doctor = XCN(xcn_1='ARZ200', xcn_2='Bäcker', xcn_3='Günther', xcn_6='Dr.', xcn_8='med.')
        segment.consulting_doctor = XCN(xcn_1='ARZ300', xcn_2='Schröder', xcn_3='Jürgen', xcn_6='Dr.', xcn_8='med.')
        segment.temporary_location = PL(pl_1='Nordflügel', pl_2='Raum 502', pl_3='Bett 2', pl_4='Innere Medizin')
        segment.visit_number = CX(cx_1='FALL7890')
        segment.pending_location = PL(pl_1='Westflügel', pl_2='Raum 603', pl_3='Bett 3', pl_4='Neurochirurgie')
        segment.admit_date_time = '20260325070000'

        serialized = segment.serialize()
        expected = 'PV1||I|Südflügel^Raum 401^Bett 1^Orthopädie||||ARZ100^Müller^Björn^^^Dr.^med.|ARZ200^Bäcker^Günther^^^Dr.^med.|ARZ300^Schröder^Jürgen^^^Dr.^med.||Nordflügel^Raum 502^Bett 2^Innere Medizin||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260325070000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A09()

        message.msh.sending_application = HD(hd_1='KLINIK_SND')
        message.msh.sending_facility = HD(hd_1='STÄDTISCH_KH')
        message.msh.receiving_application = HD(hd_1='LABOR_EMP')
        message.msh.receiving_facility = HD(hd_1='RÖNTGEN_KH')
        message.msh.date_time_of_message = '20260325070000'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A11', msg_3='ADT_A09')
        message.msh.message_control_id = 'CTL00009'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.6')

        message.evn.recorded_date_time = '20260325070000'

        message.pid.patient_identifier_list = CX(cx_1='PT7890', cx_4='Löwenklinik')
        message.pid.patient_name = XPN(xpn_1='Grünwald', xpn_2='Käthe', xpn_3='Ännchen', xpn_5='Frau')
        message.pid.date_time_of_birth = '19830214'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = XAD(xad_1='Böttcherstraße 47', xad_3='Nürnberg', xad_5='90402')

        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='Südflügel', pl_2='Raum 401', pl_3='Bett 1', pl_4='Orthopädie')
        message.pv1.attending_doctor = XCN(xcn_1='ARZ100', xcn_2='Müller', xcn_3='Björn', xcn_6='Dr.', xcn_8='med.')
        message.pv1.referring_doctor = XCN(xcn_1='ARZ200', xcn_2='Bäcker', xcn_3='Günther', xcn_6='Dr.', xcn_8='med.')
        message.pv1.consulting_doctor = XCN(xcn_1='ARZ300', xcn_2='Schröder', xcn_3='Jürgen', xcn_6='Dr.', xcn_8='med.')
        message.pv1.temporary_location = PL(pl_1='Nordflügel', pl_2='Raum 502', pl_3='Bett 2', pl_4='Innere Medizin')
        message.pv1.visit_number = CX(cx_1='FALL7890')
        message.pv1.pending_location = PL(pl_1='Westflügel', pl_2='Raum 603', pl_3='Bett 3', pl_4='Neurochirurgie')
        message.pv1.admit_date_time = '20260325070000'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_clinical_10 = 'MSH|^~\\&|termin-gw|praxis-süd|PRAXIS_APP|KLINIK_RÖNTGEN|20260401151846+0200||ADT^A08^ADT_A01|740298561038472159|P|2.5||||||UNICODE UTF-8\rEVN|A08|202604011516+0200\rPID|1|56789|xbc3def912a^^^&www.praxis-süd.de&DNS^PI~56789^^^^PT||Überström^Rikård^^^Prof.||19880913|M|||Straße der Einheit 42^^Zürich^^8001^CH||+41794321098^^CP^^^^^^^^^+41794321098~+41446789012^^PH^^^^^^^^^+41446789012~rikard.ueberstroem@praxis-süd.ch^NET^X.400^rikard.ueberstroem@praxis-süd.ch\rPV1|1|U'

class Test_de_cgm_clinical_10_10_ADT_A08_patient_update_via_samedi_HL7gateway(unittest.TestCase):
    """ 10. ADT^A08 - patient update via samedi HL7gateway
    Source: samedi HL7gateway documentation - Von hl7gateway versandte ADT Nachrichten
    URL: https://hl7gateway.samedi.de/hl7gateway/messages/adt/
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'termin-gw')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'praxis-süd')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'PRAXIS_APP')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'KLINIK_RÖNTGEN')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260401151846+0200')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A08')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, '740298561038472159')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, 'UNICODE UTF-8')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604011516+0200')

# ################################################################################################################

    def test_navigate_PID_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('PID.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PID_3_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('PID.3[0]')
        self.assertEqual(result, 'xbc3def912a')

# ################################################################################################################

    def test_navigate_PID_3_0_4_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('PID.3[0].4.2')
        self.assertEqual(result, 'www.praxis-süd.de')

# ################################################################################################################

    def test_navigate_PID_3_0_4_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('PID.3[0].4.3')
        self.assertEqual(result, 'DNS')

# ################################################################################################################

    def test_navigate_PID_3_0_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('PID.3[0].5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_3_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('PID.3[1]')
        self.assertEqual(result, '56789')

# ################################################################################################################

    def test_navigate_PID_3_1_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('PID.3[1].5')
        self.assertEqual(result, 'PT')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Überström')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Rikård')

# ################################################################################################################

    def test_navigate_PID_5_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('PID.5.5')
        self.assertEqual(result, 'Prof.')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19880913')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Straße der Einheit 42')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Zürich')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '8001')

# ################################################################################################################

    def test_navigate_PID_11_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('PID.11.6')
        self.assertEqual(result, 'CH')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_10, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'U')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='termin-gw')
        segment.sending_facility = HD(hd_1='praxis-süd')
        segment.receiving_application = HD(hd_1='PRAXIS_APP')
        segment.receiving_facility = HD(hd_1='KLINIK_RÖNTGEN')
        segment.date_time_of_message = '20260401151846+0200'
        segment.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        segment.message_control_id = '740298561038472159'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5')
        segment.character_set = 'UNICODE UTF-8'

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|termin-gw|praxis-süd|PRAXIS_APP|KLINIK_RÖNTGEN|20260401151846+0200||ADT^A08^ADT_A01|740298561038472159|P|2.5||||||UNICODE UTF-8'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202604011516+0200'

        serialized = segment.serialize()
        expected = 'EVN|A08|202604011516+0200'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.set_id_pid = '1'
        segment.patient_identifier_list = [CX(cx_1='xbc3def912a', cx_4='&www.praxis-süd.de&DNS', cx_5='PI'), CX(cx_1='56789', cx_5='PT')]
        segment.patient_name = XPN(xpn_1='Überström', xpn_2='Rikård', xpn_5='Prof.')
        segment.date_time_of_birth = '19880913'
        segment.administrative_sex = CWE(cwe_1='M')
        segment.patient_address = XAD(xad_1='Straße der Einheit 42', xad_3='Zürich', xad_5='8001', xad_6='CH')

        serialized = segment.serialize()
        expected = 'PID|1|56789|xbc3def912a^^^&www.praxis-süd.de&DNS^PI~56789^^^^PT||Überström^Rikård^^^Prof.||19880913|M|||Straße der Einheit 42^^Zürich^^8001^CH||+41794321098^^CP^^^^^^^^^+41794321098~+41446789012^^PH^^^^^^^^^+41446789012~rikard.ueberstroem@praxis-süd.ch^NET^X.400^rikard.ueberstroem@praxis-süd.ch'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='U')

        serialized = segment.serialize()
        expected = 'PV1|1|U'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A01()

        message.msh.sending_application = HD(hd_1='termin-gw')
        message.msh.sending_facility = HD(hd_1='praxis-süd')
        message.msh.receiving_application = HD(hd_1='PRAXIS_APP')
        message.msh.receiving_facility = HD(hd_1='KLINIK_RÖNTGEN')
        message.msh.date_time_of_message = '20260401151846+0200'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        message.msh.message_control_id = '740298561038472159'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5')
        message.msh.character_set = 'UNICODE UTF-8'

        message.evn.recorded_date_time = '202604011516+0200'

        message.pid.set_id_pid = '1'
        message.pid.patient_identifier_list = [CX(cx_1='xbc3def912a', cx_4='&www.praxis-süd.de&DNS', cx_5='PI'), CX(cx_1='56789', cx_5='PT')]
        message.pid.patient_name = XPN(xpn_1='Überström', xpn_2='Rikård', xpn_5='Prof.')
        message.pid.date_time_of_birth = '19880913'
        message.pid.administrative_sex = CWE(cwe_1='M')
        message.pid.patient_address = XAD(xad_1='Straße der Einheit 42', xad_3='Zürich', xad_5='8001', xad_6='CH')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='U')

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_clinical_11 = 'MSH|^~\\&|termin-gw|praxis-süd|PRAXIS_APP|KLINIK_RÖNTGEN|20260401152323+0200||ADT^A29^ADT_A21|829471036285019374|P|2.5||||||UNICODE UTF-8\rEVN|A29|202604011523+0200\rPID|1|44|y8a2bc7e31f^^^&www.praxis-süd.de&DNS^PI~44^^^^PT||Öztürk^Fátima||19751120\rPV1|1|U'

class Test_de_cgm_clinical_11_11_ADT_A29_patient_deleted_via_samedi_HL7gateway(unittest.TestCase):
    """ 11. ADT^A29 - patient deleted via samedi HL7gateway
    Source: samedi HL7gateway documentation - Gelöschter Patient
    URL: https://hl7gateway.samedi.de/hl7gateway/messages/adt/
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        self.assertIsInstance(message, ADT_A21)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A21')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'termin-gw')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'praxis-süd')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'PRAXIS_APP')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'KLINIK_RÖNTGEN')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260401152323+0200')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A29')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A21')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, '829471036285019374')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, 'UNICODE UTF-8')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604011523+0200')

# ################################################################################################################

    def test_navigate_PID_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('PID.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PID_3_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('PID.3[0]')
        self.assertEqual(result, 'y8a2bc7e31f')

# ################################################################################################################

    def test_navigate_PID_3_0_4_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('PID.3[0].4.2')
        self.assertEqual(result, 'www.praxis-süd.de')

# ################################################################################################################

    def test_navigate_PID_3_0_4_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('PID.3[0].4.3')
        self.assertEqual(result, 'DNS')

# ################################################################################################################

    def test_navigate_PID_3_0_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('PID.3[0].5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_3_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('PID.3[1]')
        self.assertEqual(result, '44')

# ################################################################################################################

    def test_navigate_PID_3_1_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('PID.3[1].5')
        self.assertEqual(result, 'PT')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Öztürk')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Fátima')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19751120')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_11, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'U')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='termin-gw')
        segment.sending_facility = HD(hd_1='praxis-süd')
        segment.receiving_application = HD(hd_1='PRAXIS_APP')
        segment.receiving_facility = HD(hd_1='KLINIK_RÖNTGEN')
        segment.date_time_of_message = '20260401152323+0200'
        segment.message_type = MSG(msg_1='ADT', msg_2='A29', msg_3='ADT_A21')
        segment.message_control_id = '829471036285019374'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5')
        segment.character_set = 'UNICODE UTF-8'

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|termin-gw|praxis-süd|PRAXIS_APP|KLINIK_RÖNTGEN|20260401152323+0200||ADT^A29^ADT_A21|829471036285019374|P|2.5||||||UNICODE UTF-8'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202604011523+0200'

        serialized = segment.serialize()
        expected = 'EVN|A29|202604011523+0200'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.set_id_pid = '1'
        segment.patient_identifier_list = [CX(cx_1='y8a2bc7e31f', cx_4='&www.praxis-süd.de&DNS', cx_5='PI'), CX(cx_1='44', cx_5='PT')]
        segment.patient_name = XPN(xpn_1='Öztürk', xpn_2='Fátima')
        segment.date_time_of_birth = '19751120'

        serialized = segment.serialize()
        expected = 'PID|1|44|y8a2bc7e31f^^^&www.praxis-süd.de&DNS^PI~44^^^^PT||Öztürk^Fátima||19751120'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='U')

        serialized = segment.serialize()
        expected = 'PV1|1|U'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A21()

        message.msh.sending_application = HD(hd_1='termin-gw')
        message.msh.sending_facility = HD(hd_1='praxis-süd')
        message.msh.receiving_application = HD(hd_1='PRAXIS_APP')
        message.msh.receiving_facility = HD(hd_1='KLINIK_RÖNTGEN')
        message.msh.date_time_of_message = '20260401152323+0200'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A29', msg_3='ADT_A21')
        message.msh.message_control_id = '829471036285019374'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5')
        message.msh.character_set = 'UNICODE UTF-8'

        message.evn.recorded_date_time = '202604011523+0200'

        message.pid.set_id_pid = '1'
        message.pid.patient_identifier_list = [CX(cx_1='y8a2bc7e31f', cx_4='&www.praxis-süd.de&DNS', cx_5='PI'), CX(cx_1='44', cx_5='PT')]
        message.pid.patient_name = XPN(xpn_1='Öztürk', xpn_2='Fátima')
        message.pid.date_time_of_birth = '19751120'

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='U')

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_clinical_12 = 'MSH|^~\\&|IntSrv|INTSRV_KH|termin-gw|praxis-süd|20260410123517||ADT^A08|2638150947283|P|2.5|9E72B53F8AC791B||AL|NE||8859/1\rEVN|A08|202604061019\rPID|1||5566^^^&www.praxis-süd.de&DNS^PI~331742^^^Röntgen^PI|20000077^^^KÖL^PI|Größe^Frédérique||19560318|F|||Brückenweg 23&Brückenweg 23^^Düsseldorf^^40545^DE^L||^^PH^^^^0211-7654321 Büro|^^PH'

class Test_de_cgm_clinical_12_12_ADT_A08_incoming_from_KIS_via_KomServer(unittest.TestCase):
    """ 12. ADT^A08 - incoming from KIS via KomServer
    Source: samedi HL7gateway documentation - Eingehende ADT-Nachricht
    URL: https://hl7gateway.samedi.de/hl7gateway/messages/adt/
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'IntSrv')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'INTSRV_KH')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'termin-gw')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'praxis-süd')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260410123517')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A08')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, '2638150947283')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_13(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('MSH.13')
        self.assertEqual(result, '9E72B53F8AC791B')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604061019')

# ################################################################################################################

    def test_navigate_PID_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('PID.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PID_3_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('PID.3[0]')
        self.assertEqual(result, '5566')

# ################################################################################################################

    def test_navigate_PID_3_0_4_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('PID.3[0].4.2')
        self.assertEqual(result, 'www.praxis-süd.de')

# ################################################################################################################

    def test_navigate_PID_3_0_4_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('PID.3[0].4.3')
        self.assertEqual(result, 'DNS')

# ################################################################################################################

    def test_navigate_PID_3_0_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('PID.3[0].5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_3_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('PID.3[1]')
        self.assertEqual(result, '331742')

# ################################################################################################################

    def test_navigate_PID_3_1_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('PID.3[1].4')
        self.assertEqual(result, 'Röntgen')

# ################################################################################################################

    def test_navigate_PID_3_1_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('PID.3[1].5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Größe')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Frédérique')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19560318')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Brückenweg 23')

# ################################################################################################################

    def test_navigate_PID_11_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('PID.11.1.2')
        self.assertEqual(result, 'Brückenweg 23')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Düsseldorf')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '40545')

# ################################################################################################################

    def test_navigate_PID_11_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('PID.11.6')
        self.assertEqual(result, 'DE')

# ################################################################################################################

    def test_navigate_PID_11_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_12, validate=False)
        result = message.get('PID.11.7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='IntSrv')
        segment.sending_facility = HD(hd_1='INTSRV_KH')
        segment.receiving_application = HD(hd_1='termin-gw')
        segment.receiving_facility = HD(hd_1='praxis-süd')
        segment.date_time_of_message = '20260410123517'
        segment.message_type = MSG(msg_1='ADT', msg_2='A08')
        segment.message_control_id = '2638150947283'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5')
        segment.sequence_number = '9E72B53F8AC791B'
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.character_set = '8859/1'

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|IntSrv|INTSRV_KH|termin-gw|praxis-süd|20260410123517||ADT^A08|2638150947283|P|2.5|9E72B53F8AC791B||AL|NE||8859/1'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202604061019'

        serialized = segment.serialize()
        expected = 'EVN|A08|202604061019'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.set_id_pid = '1'
        segment.patient_identifier_list = [CX(cx_1='5566', cx_4='&www.praxis-süd.de&DNS', cx_5='PI'), CX(cx_1='331742', cx_4='Röntgen', cx_5='PI')]
        segment.patient_name = XPN(xpn_1='Größe', xpn_2='Frédérique')
        segment.date_time_of_birth = '19560318'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Brückenweg 23&Brückenweg 23', xad_3='Düsseldorf', xad_5='40545', xad_6='DE', xad_7='L')

        serialized = segment.serialize()
        expected = 'PID|1||5566^^^&www.praxis-süd.de&DNS^PI~331742^^^Röntgen^PI|20000077^^^KÖL^PI|Größe^Frédérique||19560318|F|||Brückenweg 23&Brückenweg 23^^Düsseldorf^^40545^DE^L||^^PH^^^^0211-7654321 Büro|^^PH'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A01()

        message.msh.sending_application = HD(hd_1='IntSrv')
        message.msh.sending_facility = HD(hd_1='INTSRV_KH')
        message.msh.receiving_application = HD(hd_1='termin-gw')
        message.msh.receiving_facility = HD(hd_1='praxis-süd')
        message.msh.date_time_of_message = '20260410123517'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A08')
        message.msh.message_control_id = '2638150947283'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5')
        message.msh.sequence_number = '9E72B53F8AC791B'
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.character_set = '8859/1'

        message.evn.recorded_date_time = '202604061019'

        message.pid.set_id_pid = '1'
        message.pid.patient_identifier_list = [CX(cx_1='5566', cx_4='&www.praxis-süd.de&DNS', cx_5='PI'), CX(cx_1='331742', cx_4='Röntgen', cx_5='PI')]
        message.pid.patient_name = XPN(xpn_1='Größe', xpn_2='Frédérique')
        message.pid.date_time_of_birth = '19560318'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = XAD(xad_1='Brückenweg 23&Brückenweg 23', xad_3='Düsseldorf', xad_5='40545', xad_6='DE', xad_7='L')

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_clinical_13 = 'MSH|^~\\&|IntSrv|INTSRV_KH|befund-süd|BEFUND_SÜD|20260410123517||ADT^A08|2638150947283|P|2.5|9E72B53F8AC791B||AL|NE||8859/1\rEVN|A08|202604061019\rPID|1||331742~77777^^^&a1b2c3d4-e5f6-7890-abcd-ef1234567890&UUID^PI~88888^^^baz^PI|20000077^^^KÖL^PI|Größe^Frédérique||19560318|F|||Brückenweg 23&Brückenweg 23^^Köln^^50667^DE^L||^^PH^^^^0221-7654321 Büro|^^PH\rPV1|1|U'

class Test_de_cgm_clinical_13_13_ADT_A08_incoming_with_multiple_external_identifiers(unittest.TestCase):
    """ 13. ADT^A08 - incoming with multiple external identifiers
    Source: samedi HL7gateway documentation - ADT-Nachricht mit mehreren externen Kennungen
    URL: https://hl7gateway.samedi.de/hl7gateway/messages/adt/
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'IntSrv')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'INTSRV_KH')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'befund-süd')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'BEFUND_SÜD')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260410123517')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A08')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, '2638150947283')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_13(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('MSH.13')
        self.assertEqual(result, '9E72B53F8AC791B')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604061019')

# ################################################################################################################

    def test_navigate_PID_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('PID.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PID_3_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('PID.3[0]')
        self.assertEqual(result, '331742')

# ################################################################################################################

    def test_navigate_PID_3_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('PID.3[1]')
        self.assertEqual(result, '77777')

# ################################################################################################################

    def test_navigate_PID_3_1_4_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('PID.3[1].4.2')
        self.assertEqual(result, 'a1b2c3d4-e5f6-7890-abcd-ef1234567890')

# ################################################################################################################

    def test_navigate_PID_3_1_4_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('PID.3[1].4.3')
        self.assertEqual(result, 'UUID')

# ################################################################################################################

    def test_navigate_PID_3_1_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('PID.3[1].5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('PID.3[2]')
        self.assertEqual(result, '88888')

# ################################################################################################################

    def test_navigate_PID_3_2_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('PID.3[2].4')
        self.assertEqual(result, 'baz')

# ################################################################################################################

    def test_navigate_PID_3_2_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('PID.3[2].5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Größe')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Frédérique')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19560318')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Brückenweg 23')

# ################################################################################################################

    def test_navigate_PID_11_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('PID.11.1.2')
        self.assertEqual(result, 'Brückenweg 23')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Köln')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '50667')

# ################################################################################################################

    def test_navigate_PID_11_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('PID.11.6')
        self.assertEqual(result, 'DE')

# ################################################################################################################

    def test_navigate_PID_11_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('PID.11.7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_13, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'U')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='IntSrv')
        segment.sending_facility = HD(hd_1='INTSRV_KH')
        segment.receiving_application = HD(hd_1='befund-süd')
        segment.receiving_facility = HD(hd_1='BEFUND_SÜD')
        segment.date_time_of_message = '20260410123517'
        segment.message_type = MSG(msg_1='ADT', msg_2='A08')
        segment.message_control_id = '2638150947283'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5')
        segment.sequence_number = '9E72B53F8AC791B'
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.character_set = '8859/1'

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|IntSrv|INTSRV_KH|befund-süd|BEFUND_SÜD|20260410123517||ADT^A08|2638150947283|P|2.5|9E72B53F8AC791B||AL|NE||8859/1'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202604061019'

        serialized = segment.serialize()
        expected = 'EVN|A08|202604061019'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.set_id_pid = '1'
        segment.patient_identifier_list = [CX(cx_1='331742'), CX(cx_1='77777', cx_4='&a1b2c3d4-e5f6-7890-abcd-ef1234567890&UUID', cx_5='PI'), CX(cx_1='88888', cx_4='baz', cx_5='PI')]
        segment.patient_name = XPN(xpn_1='Größe', xpn_2='Frédérique')
        segment.date_time_of_birth = '19560318'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Brückenweg 23&Brückenweg 23', xad_3='Köln', xad_5='50667', xad_6='DE', xad_7='L')

        serialized = segment.serialize()
        expected = 'PID|1||331742~77777^^^&a1b2c3d4-e5f6-7890-abcd-ef1234567890&UUID^PI~88888^^^baz^PI|20000077^^^KÖL^PI|Größe^Frédérique||19560318|F|||Brückenweg 23&Brückenweg 23^^Köln^^50667^DE^L||^^PH^^^^0221-7654321 Büro|^^PH'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='U')

        serialized = segment.serialize()
        expected = 'PV1|1|U'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A01()

        message.msh.sending_application = HD(hd_1='IntSrv')
        message.msh.sending_facility = HD(hd_1='INTSRV_KH')
        message.msh.receiving_application = HD(hd_1='befund-süd')
        message.msh.receiving_facility = HD(hd_1='BEFUND_SÜD')
        message.msh.date_time_of_message = '20260410123517'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A08')
        message.msh.message_control_id = '2638150947283'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5')
        message.msh.sequence_number = '9E72B53F8AC791B'
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.character_set = '8859/1'

        message.evn.recorded_date_time = '202604061019'

        message.pid.set_id_pid = '1'
        message.pid.patient_identifier_list = [CX(cx_1='331742'), CX(cx_1='77777', cx_4='&a1b2c3d4-e5f6-7890-abcd-ef1234567890&UUID', cx_5='PI'), CX(cx_1='88888', cx_4='baz', cx_5='PI')]
        message.pid.patient_name = XPN(xpn_1='Größe', xpn_2='Frédérique')
        message.pid.date_time_of_birth = '19560318'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = XAD(xad_1='Brückenweg 23&Brückenweg 23', xad_3='Köln', xad_5='50667', xad_6='DE', xad_7='L')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='U')

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_clinical_14 = 'MSH|^~\\&|IntSrv|INTSRV_KH|termin-gw|praxis-süd|20260410123517||ADT^A40|2638150947283|P|2.5|9E72B53F8AC791B||AL|NE||8859/1\rEVN|A40|202604081715\rPID|1||5566^^^&www.praxis-süd.de&DNS^PI~331742^^^Röntgen^PI|20000077^^^KÖL^PI|Größe^Frédérique||19560318|F|||Brückenweg 23&Brückenweg 23^^Düsseldorf^^40545^DE^L||^^PH^^^^0211-7654321 Büro|^^PH\rMRG|9876~q283746bcde^^^&www.praxis-süd.de&DNS~5567823^^^&1.2.276.0.76.3.1.660.1.1.1.2.1&ISO^PI|'

class Test_de_cgm_clinical_14_14_ADT_A40_Zusammenf_hrung_Patienten_merge_patient(unittest.TestCase):
    """ 14. ADT^A40 - Zusammenführung Patienten (merge patient)
    Source: samedi HL7gateway documentation - Zusammenführungsanfrage für Patienten
    URL: https://hl7gateway.samedi.de/hl7gateway/messages/adt/
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        self.assertIsInstance(message, ADT_A39)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A39')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'IntSrv')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'INTSRV_KH')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'termin-gw')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'praxis-süd')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260410123517')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A40')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, '2638150947283')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_13(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('MSH.13')
        self.assertEqual(result, '9E72B53F8AC791B')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '202604081715')

# ################################################################################################################

    def test_navigate_PID_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('PID.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PID_3_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('PID.3[0]')
        self.assertEqual(result, '5566')

# ################################################################################################################

    def test_navigate_PID_3_0_4_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('PID.3[0].4.2')
        self.assertEqual(result, 'www.praxis-süd.de')

# ################################################################################################################

    def test_navigate_PID_3_0_4_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('PID.3[0].4.3')
        self.assertEqual(result, 'DNS')

# ################################################################################################################

    def test_navigate_PID_3_0_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('PID.3[0].5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_3_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('PID.3[1]')
        self.assertEqual(result, '331742')

# ################################################################################################################

    def test_navigate_PID_3_1_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('PID.3[1].4')
        self.assertEqual(result, 'Röntgen')

# ################################################################################################################

    def test_navigate_PID_3_1_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('PID.3[1].5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Größe')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Frédérique')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19560318')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Brückenweg 23')

# ################################################################################################################

    def test_navigate_PID_11_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('PID.11.1.2')
        self.assertEqual(result, 'Brückenweg 23')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Düsseldorf')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '40545')

# ################################################################################################################

    def test_navigate_PID_11_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('PID.11.6')
        self.assertEqual(result, 'DE')

# ################################################################################################################

    def test_navigate_PID_11_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('PID.11.7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_MRG_1_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('MRG.1[0]')
        self.assertEqual(result, '9876')

# ################################################################################################################

    def test_navigate_MRG_1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('MRG.1[1]')
        self.assertEqual(result, 'q283746bcde')

# ################################################################################################################

    def test_navigate_MRG_1_1_4_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('MRG.1[1].4.2')
        self.assertEqual(result, 'www.praxis-süd.de')

# ################################################################################################################

    def test_navigate_MRG_1_1_4_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('MRG.1[1].4.3')
        self.assertEqual(result, 'DNS')

# ################################################################################################################

    def test_navigate_MRG_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('MRG.1[2]')
        self.assertEqual(result, '5567823')

# ################################################################################################################

    def test_navigate_MRG_1_2_4_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('MRG.1[2].4.2')
        self.assertEqual(result, '1.2.276.0.76.3.1.660.1.1.1.2.1')

# ################################################################################################################

    def test_navigate_MRG_1_2_4_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('MRG.1[2].4.3')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_MRG_1_2_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_14, validate=False)
        result = message.get('MRG.1[2].5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='IntSrv')
        segment.sending_facility = HD(hd_1='INTSRV_KH')
        segment.receiving_application = HD(hd_1='termin-gw')
        segment.receiving_facility = HD(hd_1='praxis-süd')
        segment.date_time_of_message = '20260410123517'
        segment.message_type = MSG(msg_1='ADT', msg_2='A40')
        segment.message_control_id = '2638150947283'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5')
        segment.sequence_number = '9E72B53F8AC791B'
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.character_set = '8859/1'

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|IntSrv|INTSRV_KH|termin-gw|praxis-süd|20260410123517||ADT^A40|2638150947283|P|2.5|9E72B53F8AC791B||AL|NE||8859/1'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '202604081715'

        serialized = segment.serialize()
        expected = 'EVN|A40|202604081715'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.set_id_pid = '1'
        segment.patient_identifier_list = [CX(cx_1='5566', cx_4='&www.praxis-süd.de&DNS', cx_5='PI'), CX(cx_1='331742', cx_4='Röntgen', cx_5='PI')]
        segment.patient_name = XPN(xpn_1='Größe', xpn_2='Frédérique')
        segment.date_time_of_birth = '19560318'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Brückenweg 23&Brückenweg 23', xad_3='Düsseldorf', xad_5='40545', xad_6='DE', xad_7='L')

        serialized = segment.serialize()
        expected = 'PID|1||5566^^^&www.praxis-süd.de&DNS^PI~331742^^^Röntgen^PI|20000077^^^KÖL^PI|Größe^Frédérique||19560318|F|||Brückenweg 23&Brückenweg 23^^Düsseldorf^^40545^DE^L||^^PH^^^^0211-7654321 Büro|^^PH'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_MRG(self) -> 'None':
        segment = MRG()

        segment.prior_patient_identifier_list = [CX(cx_1='9876'), CX(cx_1='q283746bcde', cx_4='&www.praxis-süd.de&DNS'), CX(cx_1='5567823', cx_4='&1.2.276.0.76.3.1.660.1.1.1.2.1&ISO', cx_5='PI')]

        serialized = segment.serialize()
        expected = 'MRG|9876~q283746bcde^^^&www.praxis-süd.de&DNS~5567823^^^&1.2.276.0.76.3.1.660.1.1.1.2.1&ISO^PI|'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A39()

        message.msh.sending_application = HD(hd_1='IntSrv')
        message.msh.sending_facility = HD(hd_1='INTSRV_KH')
        message.msh.receiving_application = HD(hd_1='termin-gw')
        message.msh.receiving_facility = HD(hd_1='praxis-süd')
        message.msh.date_time_of_message = '20260410123517'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A40')
        message.msh.message_control_id = '2638150947283'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5')
        message.msh.sequence_number = '9E72B53F8AC791B'
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.character_set = '8859/1'

        message.evn.recorded_date_time = '202604081715'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_clinical_15 = 'MSH|^~\\&|KLINx||AUFN||20260401112408||ADT^A01^ADT_A01|77|P|2.5|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.1^^2.16.840.1.113883.2.6^ISO'

class Test_de_cgm_clinical_15_15_ADT_A01_Aufnahme_from_MSH_segment_reference_HL7_DE(unittest.TestCase):
    """ 15. ADT^A01 - Aufnahme from MSH segment reference (HL7 DE)
    Source: wiki.hl7.de - Segment MSH, Beispiel Aufnahmenachricht
    URL: http://wiki.hl7.de/index.php?title=Segment_MSH
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_15, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_15, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_15, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_15, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_15, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KLINx')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_15, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'AUFN')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_15, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260401112408')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_15, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_15, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A01')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_15, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_15, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, '77')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_15, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_15, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_15, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_15, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_15, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_15, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_15, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_15, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_15, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.1')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_15, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_15, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KLINx')
        segment.receiving_application = HD(hd_1='AUFN')
        segment.date_time_of_message = '20260401112408'
        segment.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        segment.message_control_id = '77'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DEU'
        segment.character_set = '8859/1'
        segment.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.1', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KLINx||AUFN||20260401112408||ADT^A01^ADT_A01|77|P|2.5|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.1^^2.16.840.1.113883.2.6^ISO'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A01()

        message.msh.sending_application = HD(hd_1='KLINx')
        message.msh.receiving_application = HD(hd_1='AUFN')
        message.msh.date_time_of_message = '20260401112408'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        message.msh.message_control_id = '77'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DEU'
        message.msh.character_set = '8859/1'
        message.msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.1', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_clinical_16 = 'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260401120000||ADT^A31^ADT_A05|CTL00010|P|2.6\rEVN|A31|20260401120000\rPID|||PT7890^^^Löwenklinik||Grünwald^Käthe^Märta^^Frau||19820501|F|||Überlandstraße 99^^Würzburg^^97070||^^PH^09319876543~^^CP^01769876543~^^Internet^maerta.gruenwald@yähoo.de\rPV1||I|Südflügel^Raum 401^Bett 1^Orthopädie||||ARZ100^Müller^Björn^^^Dr.^med.|ARZ200^Bäcker^Günther^^^Dr.^med.|ARZ300^Schröder^Jürgen^^^Dr.^med.||Nordflügel^Raum 502^Bett 2^Innere Medizin||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260401120000\rIN1|1|0|KV001|BÜRGERKRANKENVERSICHERUNG|Königstraße 88^^München^^80331||||||||||||||||||||||||||||||||||||||||||||49'

class Test_de_cgm_clinical_16_16_ADT_A31_nderung_Personendaten_update_person_information(unittest.TestCase):
    """ 16. ADT^A31 - Änderung Personendaten (update person information)
    Source: support.thieme-compliance.de - HL7-Nachrichtentyp ADT, Beispielnachricht A31
    URL: https://support.thieme-compliance.de/de/ECP/Admin/hl7_adt-nachrichten.html
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        self.assertIsInstance(message, ADT_A05)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A05')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'KLINIK_SND')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'STÄDTISCH_KH')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'LABOR_EMP')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'RÖNTGEN_KH')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260401120000')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A31')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A05')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'CTL00010')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.6')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '20260401120000')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, 'PT7890')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Löwenklinik')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'Grünwald')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'Käthe')

# ################################################################################################################

    def test_navigate_PID_5_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PID.5.3')
        self.assertEqual(result, 'Märta')

# ################################################################################################################

    def test_navigate_PID_5_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PID.5.5')
        self.assertEqual(result, 'Frau')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19820501')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Überlandstraße 99')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Würzburg')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '97070')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'Südflügel')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, 'Raum 401')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, 'Bett 1')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'Orthopädie')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, 'ARZ100')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Müller')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Björn')

# ################################################################################################################

    def test_navigate_PV1_7_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.7.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_7_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.7.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.8')
        self.assertEqual(result, 'ARZ200')

# ################################################################################################################

    def test_navigate_PV1_8_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.8.2')
        self.assertEqual(result, 'Bäcker')

# ################################################################################################################

    def test_navigate_PV1_8_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.8.3')
        self.assertEqual(result, 'Günther')

# ################################################################################################################

    def test_navigate_PV1_8_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.8.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_8_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.8.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.9')
        self.assertEqual(result, 'ARZ300')

# ################################################################################################################

    def test_navigate_PV1_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.9.2')
        self.assertEqual(result, 'Schröder')

# ################################################################################################################

    def test_navigate_PV1_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.9.3')
        self.assertEqual(result, 'Jürgen')

# ################################################################################################################

    def test_navigate_PV1_9_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.9.6')
        self.assertEqual(result, 'Dr.')

# ################################################################################################################

    def test_navigate_PV1_9_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.9.7')
        self.assertEqual(result, 'med.')

# ################################################################################################################

    def test_navigate_PV1_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.11')
        self.assertEqual(result, 'Nordflügel')

# ################################################################################################################

    def test_navigate_PV1_11_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.11.2')
        self.assertEqual(result, 'Raum 502')

# ################################################################################################################

    def test_navigate_PV1_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.11.3')
        self.assertEqual(result, 'Bett 2')

# ################################################################################################################

    def test_navigate_PV1_11_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.11.4')
        self.assertEqual(result, 'Innere Medizin')

# ################################################################################################################

    def test_navigate_PV1_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.19')
        self.assertEqual(result, 'FALL7890')

# ################################################################################################################

    def test_navigate_PV1_42(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.42')
        self.assertEqual(result, 'Westflügel')

# ################################################################################################################

    def test_navigate_PV1_42_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.42.2')
        self.assertEqual(result, 'Raum 603')

# ################################################################################################################

    def test_navigate_PV1_42_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.42.3')
        self.assertEqual(result, 'Bett 3')

# ################################################################################################################

    def test_navigate_PV1_42_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.42.4')
        self.assertEqual(result, 'Neurochirurgie')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '20260401120000')

# ################################################################################################################

    def test_navigate_IN1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('IN1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_IN1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('IN1.2')
        self.assertEqual(result, '0')

# ################################################################################################################

    def test_navigate_IN1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('IN1.3')
        self.assertEqual(result, 'KV001')

# ################################################################################################################

    def test_navigate_IN1_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('IN1.4')
        self.assertEqual(result, 'BÜRGERKRANKENVERSICHERUNG')

# ################################################################################################################

    def test_navigate_IN1_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('IN1.5')
        self.assertEqual(result, 'Königstraße 88')

# ################################################################################################################

    def test_navigate_IN1_5_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('IN1.5.3')
        self.assertEqual(result, 'München')

# ################################################################################################################

    def test_navigate_IN1_5_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('IN1.5.5')
        self.assertEqual(result, '80331')

# ################################################################################################################

    def test_navigate_IN1_49(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_16, validate=False)
        result = message.get('IN1.49')
        self.assertEqual(result, '49')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='KLINIK_SND')
        segment.sending_facility = HD(hd_1='STÄDTISCH_KH')
        segment.receiving_application = HD(hd_1='LABOR_EMP')
        segment.receiving_facility = HD(hd_1='RÖNTGEN_KH')
        segment.date_time_of_message = '20260401120000'
        segment.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        segment.message_control_id = 'CTL00010'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.6')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|KLINIK_SND|STÄDTISCH_KH|LABOR_EMP|RÖNTGEN_KH|20260401120000||ADT^A31^ADT_A05|CTL00010|P|2.6'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '20260401120000'

        serialized = segment.serialize()
        expected = 'EVN|A31|20260401120000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='PT7890', cx_4='Löwenklinik')
        segment.patient_name = XPN(xpn_1='Grünwald', xpn_2='Käthe', xpn_3='Märta', xpn_5='Frau')
        segment.date_time_of_birth = '19820501'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Überlandstraße 99', xad_3='Würzburg', xad_5='97070')

        serialized = segment.serialize()
        expected = 'PID|||PT7890^^^Löwenklinik||Grünwald^Käthe^Märta^^Frau||19820501|F|||Überlandstraße 99^^Würzburg^^97070||^^PH^09319876543~^^CP^01769876543~^^Internet^maerta.gruenwald@yähoo.de'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='Südflügel', pl_2='Raum 401', pl_3='Bett 1', pl_4='Orthopädie')
        segment.attending_doctor = XCN(xcn_1='ARZ100', xcn_2='Müller', xcn_3='Björn', xcn_6='Dr.', xcn_8='med.')
        segment.referring_doctor = XCN(xcn_1='ARZ200', xcn_2='Bäcker', xcn_3='Günther', xcn_6='Dr.', xcn_8='med.')
        segment.consulting_doctor = XCN(xcn_1='ARZ300', xcn_2='Schröder', xcn_3='Jürgen', xcn_6='Dr.', xcn_8='med.')
        segment.temporary_location = PL(pl_1='Nordflügel', pl_2='Raum 502', pl_3='Bett 2', pl_4='Innere Medizin')
        segment.visit_number = CX(cx_1='FALL7890')
        segment.pending_location = PL(pl_1='Westflügel', pl_2='Raum 603', pl_3='Bett 3', pl_4='Neurochirurgie')
        segment.admit_date_time = '20260401120000'

        serialized = segment.serialize()
        expected = 'PV1||I|Südflügel^Raum 401^Bett 1^Orthopädie||||ARZ100^Müller^Björn^^^Dr.^med.|ARZ200^Bäcker^Günther^^^Dr.^med.|ARZ300^Schröder^Jürgen^^^Dr.^med.||Nordflügel^Raum 502^Bett 2^Innere Medizin||||||||FALL7890|||||||||||||||||||||||Westflügel^Raum 603^Bett 3^Neurochirurgie||20260401120000'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_IN1(self) -> 'None':
        segment = IN1()

        segment.set_id_in1 = '1'
        segment.health_plan_id = CWE(cwe_1='0')
        segment.insurance_company_id = CX(cx_1='KV001')
        segment.insurance_company_name = XON(xon_1='BÜRGERKRANKENVERSICHERUNG')
        segment.insurance_company_address = XAD(xad_1='Königstraße 88', xad_3='München', xad_5='80331')
        segment.insureds_id_number = CX(cx_1='49')

        serialized = segment.serialize()
        expected = 'IN1|1|0|KV001|BÜRGERKRANKENVERSICHERUNG|Königstraße 88^^München^^80331||||||||||||||||||||||||||||||||||||||||||||49'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A05()

        message.msh.sending_application = HD(hd_1='KLINIK_SND')
        message.msh.sending_facility = HD(hd_1='STÄDTISCH_KH')
        message.msh.receiving_application = HD(hd_1='LABOR_EMP')
        message.msh.receiving_facility = HD(hd_1='RÖNTGEN_KH')
        message.msh.date_time_of_message = '20260401120000'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A31', msg_3='ADT_A05')
        message.msh.message_control_id = 'CTL00010'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.6')

        message.evn.recorded_date_time = '20260401120000'

        message.pid.patient_identifier_list = CX(cx_1='PT7890', cx_4='Löwenklinik')
        message.pid.patient_name = XPN(xpn_1='Grünwald', xpn_2='Käthe', xpn_3='Märta', xpn_5='Frau')
        message.pid.date_time_of_birth = '19820501'
        message.pid.administrative_sex = CWE(cwe_1='F')
        message.pid.patient_address = XAD(xad_1='Überlandstraße 99', xad_3='Würzburg', xad_5='97070')

        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='Südflügel', pl_2='Raum 401', pl_3='Bett 1', pl_4='Orthopädie')
        message.pv1.attending_doctor = XCN(xcn_1='ARZ100', xcn_2='Müller', xcn_3='Björn', xcn_6='Dr.', xcn_8='med.')
        message.pv1.referring_doctor = XCN(xcn_1='ARZ200', xcn_2='Bäcker', xcn_3='Günther', xcn_6='Dr.', xcn_8='med.')
        message.pv1.consulting_doctor = XCN(xcn_1='ARZ300', xcn_2='Schröder', xcn_3='Jürgen', xcn_6='Dr.', xcn_8='med.')
        message.pv1.temporary_location = PL(pl_1='Nordflügel', pl_2='Raum 502', pl_3='Bett 2', pl_4='Innere Medizin')
        message.pv1.visit_number = CX(cx_1='FALL7890')
        message.pv1.pending_location = PL(pl_1='Westflügel', pl_2='Raum 603', pl_3='Bett 3', pl_4='Neurochirurgie')
        message.pv1.admit_date_time = '20260401120000'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_clinical_17 = 'MSH|^~\\&|HÄMA LAB|ZLAB-7|BEFUND ÖST|GEBÄUDE9|20260215093000||ORU^R01|STRG-7890|P|2.4\rPID|||888-77-6666||LÖWENTHAL^ÉVA^M^^^^L|GRÖSSMANN|19750520|F|||Blücherstraße 28^^Göttingen^NI^37073||(0551)2345678|(0551)876-543||||AC888776666||89-B5667^NI^20260101\rOBR|1|934561^BEFUND ÖST|2078945^HÄMA LAB|17856^HÄMOGLOBIN|||20260215073000|||||||||888-77-6666^ÜBERALL^PÀTRÍCIA P^^^^MD^^|||||||||F||||||777-66-5555^HIPPÖKRÄTÉS^HÖRST H^^^^MD\rOBX|1|SN|718-7^HÄMOGLOBIN^BLUT:MCNC:PT:BLUT:QN||^145|g/L|120_160|N|||F'

class Test_de_cgm_clinical_17_17_ORU_R01_Laborbefund_laboratory_result(unittest.TestCase):
    """ 17. ORU^R01 - Laborbefund (laboratory result)
    Source: wiki.hl7.de - Vorlage:HL7Example
    URL: https://wiki.hl7.de/index.php/Vorlage:HL7Example
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        self.assertIsInstance(message, ORU_R01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ORU_R01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'HÄMA LAB')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'ZLAB-7')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'BEFUND ÖST')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'GEBÄUDE9')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260215093000')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ORU')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'R01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'STRG-7890')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.4')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '888-77-6666')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'LÖWENTHAL')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'ÉVA')

# ################################################################################################################

    def test_navigate_PID_5_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('PID.5.3')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_5_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('PID.5.7')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PID_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('PID.6')
        self.assertEqual(result, 'GRÖSSMANN')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19750520')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Blücherstraße 28')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Göttingen')

# ################################################################################################################

    def test_navigate_PID_11_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('PID.11.4')
        self.assertEqual(result, 'NI')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '37073')

# ################################################################################################################

    def test_navigate_PID_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('PID.18')
        self.assertEqual(result, 'AC888776666')

# ################################################################################################################

    def test_navigate_OBR_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('OBR.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_OBR_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('OBR.2')
        self.assertEqual(result, '934561')

# ################################################################################################################

    def test_navigate_OBR_2_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('OBR.2.2')
        self.assertEqual(result, 'BEFUND ÖST')

# ################################################################################################################

    def test_navigate_OBR_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('OBR.3')
        self.assertEqual(result, '2078945')

# ################################################################################################################

    def test_navigate_OBR_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('OBR.3.2')
        self.assertEqual(result, 'HÄMA LAB')

# ################################################################################################################

    def test_navigate_OBR_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('OBR.4')
        self.assertEqual(result, '17856')

# ################################################################################################################

    def test_navigate_OBR_4_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('OBR.4.2')
        self.assertEqual(result, 'HÄMOGLOBIN')

# ################################################################################################################

    def test_navigate_OBR_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('OBR.7')
        self.assertEqual(result, '20260215073000')

# ################################################################################################################

    def test_navigate_OBR_25(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('OBR.25')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_navigate_OBR_31(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('OBR.31')
        self.assertEqual(result, '777-66-5555')

# ################################################################################################################

    def test_navigate_OBR_31_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('OBR.31.2')
        self.assertEqual(result, 'HIPPÖKRÄTÉS')

# ################################################################################################################

    def test_navigate_OBR_31_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('OBR.31.3')
        self.assertEqual(result, 'HÖRST H')

# ################################################################################################################

    def test_navigate_OBR_31_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('OBR.31.7')
        self.assertEqual(result, 'MD')

# ################################################################################################################

    def test_navigate_OBX_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('OBX.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_OBX_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('OBX.2')
        self.assertEqual(result, 'SN')

# ################################################################################################################

    def test_navigate_OBX_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('OBX.3')
        self.assertEqual(result, '718-7')

# ################################################################################################################

    def test_navigate_OBX_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('OBX.3.2')
        self.assertEqual(result, 'HÄMOGLOBIN')

# ################################################################################################################

    def test_navigate_OBX_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('OBX.3.3')
        self.assertEqual(result, 'BLUT:MCNC:PT:BLUT:QN')

# ################################################################################################################

    def test_navigate_OBX_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('OBX.5.2')
        self.assertEqual(result, '145')

# ################################################################################################################

    def test_navigate_OBX_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('OBX.6')
        self.assertEqual(result, 'g/L')

# ################################################################################################################

    def test_navigate_OBX_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('OBX.7')
        self.assertEqual(result, '120_160')

# ################################################################################################################

    def test_navigate_OBX_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('OBX.8')
        self.assertEqual(result, 'N')

# ################################################################################################################

    def test_navigate_OBX_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_17, validate=False)
        result = message.get('OBX.11')
        self.assertEqual(result, 'F')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='HÄMA LAB')
        segment.sending_facility = HD(hd_1='ZLAB-7')
        segment.receiving_application = HD(hd_1='BEFUND ÖST')
        segment.receiving_facility = HD(hd_1='GEBÄUDE9')
        segment.date_time_of_message = '20260215093000'
        segment.message_type = MSG(msg_1='ORU', msg_2='R01')
        segment.message_control_id = 'STRG-7890'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.4')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|HÄMA LAB|ZLAB-7|BEFUND ÖST|GEBÄUDE9|20260215093000||ORU^R01|STRG-7890|P|2.4'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='888-77-6666')
        segment.patient_name = XPN(xpn_1='LÖWENTHAL', xpn_2='ÉVA', xpn_3='M', xpn_8='L')
        segment.mothers_maiden_name = XPN(xpn_1='GRÖSSMANN')
        segment.date_time_of_birth = '19750520'
        segment.administrative_sex = CWE(cwe_1='F')
        segment.patient_address = XAD(xad_1='Blücherstraße 28', xad_3='Göttingen', xad_4='NI', xad_5='37073')
        segment.patient_account_number = CX(cx_1='AC888776666')

        serialized = segment.serialize()
        expected = 'PID|||888-77-6666||LÖWENTHAL^ÉVA^M^^^^L|GRÖSSMANN|19750520|F|||Blücherstraße 28^^Göttingen^NI^37073||(0551)2345678|(0551)876-543||||AC888776666||89-B5667^NI^20260101'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_OBR(self) -> 'None':
        segment = OBR()

        segment.set_id_obr = '1'
        segment.placer_order_number = EI(ei_1='934561', ei_2='BEFUND ÖST')
        segment.filler_order_number = EI(ei_1='2078945', ei_2='HÄMA LAB')
        segment.universal_service_identifier = CWE(cwe_1='17856', cwe_2='HÄMOGLOBIN')
        segment.observation_date_time = '20260215073000'
        segment.result_status = 'F'
        segment.reason_for_study = CWE(cwe_1='777-66-5555', cwe_2='HIPPÖKRÄTÉS', cwe_3='HÖRST H', cwe_7='MD')

        serialized = segment.serialize()
        expected = 'OBR|1|934561^BEFUND ÖST|2078945^HÄMA LAB|17856^HÄMOGLOBIN|||20260215073000|||||||||888-77-6666^ÜBERALL^PÀTRÍCIA P^^^^MD^^|||||||||F||||||777-66-5555^HIPPÖKRÄTÉS^HÖRST H^^^^MD'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_OBX(self) -> 'None':
        segment = OBX()

        segment.set_id_obx = '1'
        segment.value_type = 'SN'
        segment.observation_identifier = CWE(cwe_1='718-7', cwe_2='HÄMOGLOBIN', cwe_3='BLUT:MCNC:PT:BLUT:QN')
        segment.observation_value = []
        segment.units = CWE(cwe_1='g/L')
        segment.reference_range = '120_160'
        segment.interpretation_codes = CWE(cwe_1='N')
        segment.observation_result_status = 'F'

        serialized = segment.serialize()
        expected = 'OBX|1|SN|718-7^HÄMOGLOBIN^BLUT:MCNC:PT:BLUT:QN||^145|g/L|120_160|N|||F'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ORU_R01()

        message.msh.sending_application = HD(hd_1='HÄMA LAB')
        message.msh.sending_facility = HD(hd_1='ZLAB-7')
        message.msh.receiving_application = HD(hd_1='BEFUND ÖST')
        message.msh.receiving_facility = HD(hd_1='GEBÄUDE9')
        message.msh.date_time_of_message = '20260215093000'
        message.msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        message.msh.message_control_id = 'STRG-7890'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.4')

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_clinical_18 = "MSH|^~\\&|GrößeReg|KölnKlinikC|ÜberOE|ZürichBildZ|20260529090131-0500||ADT^A01^ADT_A01|01052901|P|2.5\rEVN||200605290901||||200605290900\rPID|||78452991^^^Hügelreg^PI||BRÜCKNER^BÄRBEL^Q^JR||19700815|M||2028-9^^HL70005^RA99113^^XYZ|Gänseblümchenweg 14^^Nürnberg^BY^90403^^M~MÜLLER'S BÄCKEREI^Königsallee 200^^Düsseldorf^NW^40212^^O|||||||0105I30001^^^99DEF^AN\rPV1||I|W^389^1^UABH^^^^3||||54321^WÖRNER^RÉX^J^^^MD^0010^UAMC^L||98765^GRÄBER^LÜCIA^X^^^MD^0010^UAMC^L|MED|||||A0||24680^TÖNJES^SÖRÉN^T^^^MD^0010^UAMC^L|||||||||||||||||||||||||||200605290900"

class Test_de_cgm_clinical_18_18_ADT_A01_Aufnahme_with_Caristix_reference_encoding(unittest.TestCase):
    """ 18. ADT^A01 - Aufnahme with Caristix reference encoding
    Source: Caristix - HL7-ER7 encoding reference
    URL: https://caristix.com/help-center/v3/workgroup/test-scenarios/task/hl7-er7-encoding/
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'GrößeReg')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'KölnKlinikC')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'ÜberOE')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'ZürichBildZ')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260529090131-0500')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A01')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ADT_A01')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, '01052901')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '200605290901')

# ################################################################################################################

    def test_navigate_EVN_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('EVN.6')
        self.assertEqual(result, '200605290900')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '78452991')

# ################################################################################################################

    def test_navigate_PID_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.3.4')
        self.assertEqual(result, 'Hügelreg')

# ################################################################################################################

    def test_navigate_PID_3_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.3.5')
        self.assertEqual(result, 'PI')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'BRÜCKNER')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'BÄRBEL')

# ################################################################################################################

    def test_navigate_PID_5_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.5.3')
        self.assertEqual(result, 'Q')

# ################################################################################################################

    def test_navigate_PID_5_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.5.4')
        self.assertEqual(result, 'JR')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19700815')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.10')
        self.assertEqual(result, '2028-9')

# ################################################################################################################

    def test_navigate_PID_10_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.10.3')
        self.assertEqual(result, 'HL70005')

# ################################################################################################################

    def test_navigate_PID_10_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.10.4')
        self.assertEqual(result, 'RA99113')

# ################################################################################################################

    def test_navigate_PID_10_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.10.6')
        self.assertEqual(result, 'XYZ')

# ################################################################################################################

    def test_navigate_PID_11_0(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.11[0]')
        self.assertEqual(result, 'Gänseblümchenweg 14')

# ################################################################################################################

    def test_navigate_PID_11_0_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.11[0].3')
        self.assertEqual(result, 'Nürnberg')

# ################################################################################################################

    def test_navigate_PID_11_0_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.11[0].4')
        self.assertEqual(result, 'BY')

# ################################################################################################################

    def test_navigate_PID_11_0_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.11[0].5')
        self.assertEqual(result, '90403')

# ################################################################################################################

    def test_navigate_PID_11_0_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.11[0].7')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_11_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.11[1]')
        self.assertEqual(result, "MÜLLER'S BÄCKEREI")

# ################################################################################################################

    def test_navigate_PID_11_1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.11[1].2')
        self.assertEqual(result, 'Königsallee 200')

# ################################################################################################################

    def test_navigate_PID_11_1_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.11[1].4')
        self.assertEqual(result, 'Düsseldorf')

# ################################################################################################################

    def test_navigate_PID_11_1_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.11[1].5')
        self.assertEqual(result, 'NW')

# ################################################################################################################

    def test_navigate_PID_11_1_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.11[1].6')
        self.assertEqual(result, '40212')

# ################################################################################################################

    def test_navigate_PID_11_1_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.11[1].8')
        self.assertEqual(result, 'O')

# ################################################################################################################

    def test_navigate_PID_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.18')
        self.assertEqual(result, '0105I30001')

# ################################################################################################################

    def test_navigate_PID_18_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.18.4')
        self.assertEqual(result, '99DEF')

# ################################################################################################################

    def test_navigate_PID_18_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PID.18.5')
        self.assertEqual(result, 'AN')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'I')

# ################################################################################################################

    def test_navigate_PV1_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.3')
        self.assertEqual(result, 'W')

# ################################################################################################################

    def test_navigate_PV1_3_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.3.2')
        self.assertEqual(result, '389')

# ################################################################################################################

    def test_navigate_PV1_3_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.3.3')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_3_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.3.4')
        self.assertEqual(result, 'UABH')

# ################################################################################################################

    def test_navigate_PV1_3_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.3.8')
        self.assertEqual(result, '3')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, '54321')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'WÖRNER')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'RÉX')

# ################################################################################################################

    def test_navigate_PV1_7_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.7.4')
        self.assertEqual(result, 'J')

# ################################################################################################################

    def test_navigate_PV1_7_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.7.7')
        self.assertEqual(result, 'MD')

# ################################################################################################################

    def test_navigate_PV1_7_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.7.8')
        self.assertEqual(result, '0010')

# ################################################################################################################

    def test_navigate_PV1_7_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.7.9')
        self.assertEqual(result, 'UAMC')

# ################################################################################################################

    def test_navigate_PV1_7_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.7.10')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PV1_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.9')
        self.assertEqual(result, '98765')

# ################################################################################################################

    def test_navigate_PV1_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.9.2')
        self.assertEqual(result, 'GRÄBER')

# ################################################################################################################

    def test_navigate_PV1_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.9.3')
        self.assertEqual(result, 'LÜCIA')

# ################################################################################################################

    def test_navigate_PV1_9_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.9.4')
        self.assertEqual(result, 'X')

# ################################################################################################################

    def test_navigate_PV1_9_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.9.7')
        self.assertEqual(result, 'MD')

# ################################################################################################################

    def test_navigate_PV1_9_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.9.8')
        self.assertEqual(result, '0010')

# ################################################################################################################

    def test_navigate_PV1_9_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.9.9')
        self.assertEqual(result, 'UAMC')

# ################################################################################################################

    def test_navigate_PV1_9_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.9.10')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PV1_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.10')
        self.assertEqual(result, 'MED')

# ################################################################################################################

    def test_navigate_PV1_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.15')
        self.assertEqual(result, 'A0')

# ################################################################################################################

    def test_navigate_PV1_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.17')
        self.assertEqual(result, '24680')

# ################################################################################################################

    def test_navigate_PV1_17_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.17.2')
        self.assertEqual(result, 'TÖNJES')

# ################################################################################################################

    def test_navigate_PV1_17_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.17.3')
        self.assertEqual(result, 'SÖRÉN')

# ################################################################################################################

    def test_navigate_PV1_17_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.17.4')
        self.assertEqual(result, 'T')

# ################################################################################################################

    def test_navigate_PV1_17_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.17.7')
        self.assertEqual(result, 'MD')

# ################################################################################################################

    def test_navigate_PV1_17_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.17.8')
        self.assertEqual(result, '0010')

# ################################################################################################################

    def test_navigate_PV1_17_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.17.9')
        self.assertEqual(result, 'UAMC')

# ################################################################################################################

    def test_navigate_PV1_17_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.17.10')
        self.assertEqual(result, 'L')

# ################################################################################################################

    def test_navigate_PV1_44(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_18, validate=False)
        result = message.get('PV1.44')
        self.assertEqual(result, '200605290900')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='GrößeReg')
        segment.sending_facility = HD(hd_1='KölnKlinikC')
        segment.receiving_application = HD(hd_1='ÜberOE')
        segment.receiving_facility = HD(hd_1='ZürichBildZ')
        segment.date_time_of_message = '20260529090131-0500'
        segment.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        segment.message_control_id = '01052901'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|GrößeReg|KölnKlinikC|ÜberOE|ZürichBildZ|20260529090131-0500||ADT^A01^ADT_A01|01052901|P|2.5'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '200605290901'
        segment.event_occurred = '200605290900'

        serialized = segment.serialize()
        expected = 'EVN||200605290901||||200605290900'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.patient_identifier_list = CX(cx_1='78452991', cx_4='Hügelreg', cx_5='PI')
        segment.patient_name = XPN(xpn_1='BRÜCKNER', xpn_2='BÄRBEL', xpn_3='Q', xpn_4='JR')
        segment.date_time_of_birth = '19700815'
        segment.administrative_sex = CWE(cwe_1='M')
        segment.race = CWE(cwe_1='2028-9', cwe_3='HL70005', cwe_4='RA99113', cwe_6='XYZ')
        segment.patient_address = [XAD(xad_1='Gänseblümchenweg 14', xad_3='Nürnberg', xad_4='BY', xad_5='90403', xad_7='M'), XAD(xad_1="MÜLLER'S BÄCKEREI", xad_2='Königsallee 200', xad_4='Düsseldorf', xad_5='NW', xad_6='40212', xad_8='O')]
        segment.patient_account_number = CX(cx_1='0105I30001', cx_4='99DEF', cx_5='AN')

        serialized = segment.serialize()
        expected = "PID|||78452991^^^Hügelreg^PI||BRÜCKNER^BÄRBEL^Q^JR||19700815|M||2028-9^^HL70005^RA99113^^XYZ|Gänseblümchenweg 14^^Nürnberg^BY^90403^^M~MÜLLER'S BÄCKEREI^Königsallee 200^^Düsseldorf^NW^40212^^O|||||||0105I30001^^^99DEF^AN"
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.patient_class = CWE(cwe_1='I')
        segment.assigned_patient_location = PL(pl_1='W', pl_2='389', pl_3='1', pl_4='UABH', pl_8='3')
        segment.attending_doctor = XCN(xcn_1='54321', xcn_2='WÖRNER', xcn_3='RÉX', xcn_4='J', xcn_8='MD', xcn_9='0010', xcn_10='UAMC', xcn_11='L')
        segment.consulting_doctor = XCN(xcn_1='98765', xcn_2='GRÄBER', xcn_3='LÜCIA', xcn_4='X', xcn_8='MD', xcn_9='0010', xcn_10='UAMC', xcn_11='L')
        segment.hospital_service = CWE(cwe_1='MED')
        segment.ambulatory_status = CWE(cwe_1='A0')
        segment.admitting_doctor = XCN(xcn_1='24680', xcn_2='TÖNJES', xcn_3='SÖRÉN', xcn_4='T', xcn_8='MD', xcn_9='0010', xcn_10='UAMC', xcn_11='L')
        segment.admit_date_time = '200605290900'

        serialized = segment.serialize()
        expected = 'PV1||I|W^389^1^UABH^^^^3||||54321^WÖRNER^RÉX^J^^^MD^0010^UAMC^L||98765^GRÄBER^LÜCIA^X^^^MD^0010^UAMC^L|MED|||||A0||24680^TÖNJES^SÖRÉN^T^^^MD^0010^UAMC^L|||||||||||||||||||||||||||200605290900'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A01()

        message.msh.sending_application = HD(hd_1='GrößeReg')
        message.msh.sending_facility = HD(hd_1='KölnKlinikC')
        message.msh.receiving_application = HD(hd_1='ÜberOE')
        message.msh.receiving_facility = HD(hd_1='ZürichBildZ')
        message.msh.date_time_of_message = '20260529090131-0500'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        message.msh.message_control_id = '01052901'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5')

        message.evn.recorded_date_time = '200605290901'
        message.evn.event_occurred = '200605290900'

        message.pid.patient_identifier_list = CX(cx_1='78452991', cx_4='Hügelreg', cx_5='PI')
        message.pid.patient_name = XPN(xpn_1='BRÜCKNER', xpn_2='BÄRBEL', xpn_3='Q', xpn_4='JR')
        message.pid.date_time_of_birth = '19700815'
        message.pid.administrative_sex = CWE(cwe_1='M')
        message.pid.race = CWE(cwe_1='2028-9', cwe_3='HL70005', cwe_4='RA99113', cwe_6='XYZ')
        message.pid.patient_address = [XAD(xad_1='Gänseblümchenweg 14', xad_3='Nürnberg', xad_4='BY', xad_5='90403', xad_7='M'), XAD(xad_1="MÜLLER'S BÄCKEREI", xad_2='Königsallee 200', xad_4='Düsseldorf', xad_5='NW', xad_6='40212', xad_8='O')]
        message.pid.patient_account_number = CX(cx_1='0105I30001', cx_4='99DEF', cx_5='AN')

        message.pv1.patient_class = CWE(cwe_1='I')
        message.pv1.assigned_patient_location = PL(pl_1='W', pl_2='389', pl_3='1', pl_4='UABH', pl_8='3')
        message.pv1.attending_doctor = XCN(xcn_1='54321', xcn_2='WÖRNER', xcn_3='RÉX', xcn_4='J', xcn_8='MD', xcn_9='0010', xcn_10='UAMC', xcn_11='L')
        message.pv1.consulting_doctor = XCN(xcn_1='98765', xcn_2='GRÄBER', xcn_3='LÜCIA', xcn_4='X', xcn_8='MD', xcn_9='0010', xcn_10='UAMC', xcn_11='L')
        message.pv1.hospital_service = CWE(cwe_1='MED')
        message.pv1.ambulatory_status = CWE(cwe_1='A0')
        message.pv1.admitting_doctor = XCN(xcn_1='24680', xcn_2='TÖNJES', xcn_3='SÖRÉN', xcn_4='T', xcn_8='MD', xcn_9='0010', xcn_10='UAMC', xcn_11='L')
        message.pv1.admit_date_time = '200605290900'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_clinical_19 = 'MSH|^~\\&|RÖNTGEN|AUFN|KLINIK_ÖST|AUFN|20260401170600||ACK^A02^ACK|RÖNT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.4^^2.16.840.1.113883.2.6^ISO\rMSA|CA|AUFN002|'

class Test_de_cgm_clinical_19_19_ACK_A02_transport_acknowledgment_for_transfer(unittest.TestCase):
    """ 19. ACK^A02 - transport acknowledgment for transfer
    Source: wiki.hl7.de - HL7v2-Profile Verlegung, Transportquittung
    URL: https://wiki.hl7.de/index.php/HL7v2-Profile_Verlegung
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        self.assertIsInstance(message, ACK)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ACK')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'RÖNTGEN')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'AUFN')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'KLINIK_ÖST')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'AUFN')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260401170600')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ACK')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A02')

# ################################################################################################################

    def test_navigate_MSH_9_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        result = message.get('MSH.9.3')
        self.assertEqual(result, 'ACK')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, 'RÖNT002')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.5')

# ################################################################################################################

    def test_navigate_MSH_12_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        result = message.get('MSH.12.2')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_12_2_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        result = message.get('MSH.12.2.3')
        self.assertEqual(result, 'HL70399')

# ################################################################################################################

    def test_navigate_MSH_15(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        result = message.get('MSH.15')
        self.assertEqual(result, 'AL')

# ################################################################################################################

    def test_navigate_MSH_16(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        result = message.get('MSH.16')
        self.assertEqual(result, 'NE')

# ################################################################################################################

    def test_navigate_MSH_17(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        result = message.get('MSH.17')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        result = message.get('MSH.18')
        self.assertEqual(result, '8859/1')

# ################################################################################################################

    def test_navigate_MSH_19(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        result = message.get('MSH.19')
        self.assertEqual(result, 'DEU')

# ################################################################################################################

    def test_navigate_MSH_19_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        result = message.get('MSH.19.3')
        self.assertEqual(result, 'HL70296')

# ################################################################################################################

    def test_navigate_MSH_21(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        result = message.get('MSH.21')
        self.assertEqual(result, '2.16.840.1.113883.2.6.9.4')

# ################################################################################################################

    def test_navigate_MSH_21_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        result = message.get('MSH.21.3')
        self.assertEqual(result, '2.16.840.1.113883.2.6')

# ################################################################################################################

    def test_navigate_MSH_21_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        result = message.get('MSH.21.4')
        self.assertEqual(result, 'ISO')

# ################################################################################################################

    def test_navigate_MSA_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        result = message.get('MSA.1')
        self.assertEqual(result, 'CA')

# ################################################################################################################

    def test_navigate_MSA_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_19, validate=False)
        result = message.get('MSA.2')
        self.assertEqual(result, 'AUFN002')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='RÖNTGEN')
        segment.sending_facility = HD(hd_1='AUFN')
        segment.receiving_application = HD(hd_1='KLINIK_ÖST')
        segment.receiving_facility = HD(hd_1='AUFN')
        segment.date_time_of_message = '20260401170600'
        segment.message_type = MSG(msg_1='ACK', msg_2='A02', msg_3='ACK')
        segment.message_control_id = 'RÖNT002'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        segment.accept_acknowledgment = 'AL'
        segment.application_acknowledgment_type = 'NE'
        segment.country_code = 'DEU'
        segment.character_set = '8859/1'
        segment.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        segment.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.4', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|RÖNTGEN|AUFN|KLINIK_ÖST|AUFN|20260401170600||ACK^A02^ACK|RÖNT002|P|2.5^DEU&&HL70399|||AL|NE|DEU|8859/1|DEU^^HL70296||2.16.840.1.113883.2.6.9.4^^2.16.840.1.113883.2.6^ISO'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_MSA(self) -> 'None':
        segment = MSA()

        segment.acknowledgment_code = 'CA'
        segment.message_control_id = 'AUFN002'

        serialized = segment.serialize()
        expected = 'MSA|CA|AUFN002|'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ACK()

        message.msh.sending_application = HD(hd_1='RÖNTGEN')
        message.msh.sending_facility = HD(hd_1='AUFN')
        message.msh.receiving_application = HD(hd_1='KLINIK_ÖST')
        message.msh.receiving_facility = HD(hd_1='AUFN')
        message.msh.date_time_of_message = '20260401170600'
        message.msh.message_type = MSG(msg_1='ACK', msg_2='A02', msg_3='ACK')
        message.msh.message_control_id = 'RÖNT002'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.5', vid_2='DEU&&HL70399')
        message.msh.accept_acknowledgment = 'AL'
        message.msh.application_acknowledgment_type = 'NE'
        message.msh.country_code = 'DEU'
        message.msh.character_set = '8859/1'
        message.msh.principal_language_of_message = CWE(cwe_1='DEU', cwe_3='HL70296')
        message.msh.message_profile_identifier = EI(ei_1='2.16.840.1.113883.2.6.9.4', ei_3='2.16.840.1.113883.2.6', ei_4='ISO')

        message.msa.acknowledgment_code = 'CA'
        message.msa.message_control_id = 'AUFN002'

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################

_Raw_de_cgm_clinical_20 = 'MSH|^~\\&|SENDE_APPLIKATION|SENDE_EINRICHTUNG|EMPFANGS_APPLIKATION|EMPFANGS_EINRICHTUNG|20260613083617||ADT^A04|934576120260613083617|P|2.3||||\rEVN|A04|20260613083617|||\rPID|1||246813||MÜNCHHAUSEN^THÉODOR^||19550718|M|||Brückenstraße 5^^Zürich^ZH^8001||(044)9391289^^^theodor@zürich-mail.ch|||||2847|99999999||||||||||||||||||||\rPV1|1|O|||||7^Wörner^Güntér^^MD^^^^|||||||||||||||||||||||||||||||||||||||||||||'

class Test_de_cgm_clinical_20_20_ADT_A04_registration_from_ringholm_de_reference(unittest.TestCase):
    """ 20. ADT^A04 - registration from ringholm.de reference
    Source: ringholm.de - HL7 Message examples: version 2 and version 3
    URL: http://ringholm.de/docs/04300_en.htm
    """

    def test_parse(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        self.assertIsInstance(message, ADT_A01)

# ################################################################################################################

    def test_serialize_roundtrip(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        serialized = message.serialize()
        reparsed = parse_message(serialized, validate=False)
        reserialized = reparsed.serialize()
        self.assertEqual(serialized, reserialized)

# ################################################################################################################

    def test_to_dict(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        message_dict = message.to_dict()
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict['_structure_id'], 'ADT_A01')

# ################################################################################################################

    def test_to_json(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        message_json = message.to_json()
        loaded = json.loads(message_json)
        message_dict = message.to_dict()
        self.assertEqual(loaded, message_dict)

# ################################################################################################################

    def test_navigate_MSH_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('MSH.3')
        self.assertEqual(result, 'SENDE_APPLIKATION')

# ################################################################################################################

    def test_navigate_MSH_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('MSH.4')
        self.assertEqual(result, 'SENDE_EINRICHTUNG')

# ################################################################################################################

    def test_navigate_MSH_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('MSH.5')
        self.assertEqual(result, 'EMPFANGS_APPLIKATION')

# ################################################################################################################

    def test_navigate_MSH_6(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('MSH.6')
        self.assertEqual(result, 'EMPFANGS_EINRICHTUNG')

# ################################################################################################################

    def test_navigate_MSH_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('MSH.7')
        self.assertEqual(result, '20260613083617')

# ################################################################################################################

    def test_navigate_MSH_9(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('MSH.9')
        self.assertEqual(result, 'ADT')

# ################################################################################################################

    def test_navigate_MSH_9_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('MSH.9.2')
        self.assertEqual(result, 'A04')

# ################################################################################################################

    def test_navigate_MSH_10(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('MSH.10')
        self.assertEqual(result, '934576120260613083617')

# ################################################################################################################

    def test_navigate_MSH_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('MSH.11')
        self.assertEqual(result, 'P')

# ################################################################################################################

    def test_navigate_MSH_12(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('MSH.12')
        self.assertEqual(result, '2.3')

# ################################################################################################################

    def test_navigate_EVN_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('EVN.2')
        self.assertEqual(result, '20260613083617')

# ################################################################################################################

    def test_navigate_PID_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('PID.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PID_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('PID.3')
        self.assertEqual(result, '246813')

# ################################################################################################################

    def test_navigate_PID_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('PID.5')
        self.assertEqual(result, 'MÜNCHHAUSEN')

# ################################################################################################################

    def test_navigate_PID_5_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('PID.5.2')
        self.assertEqual(result, 'THÉODOR')

# ################################################################################################################

    def test_navigate_PID_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('PID.7')
        self.assertEqual(result, '19550718')

# ################################################################################################################

    def test_navigate_PID_8(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('PID.8')
        self.assertEqual(result, 'M')

# ################################################################################################################

    def test_navigate_PID_11(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('PID.11')
        self.assertEqual(result, 'Brückenstraße 5')

# ################################################################################################################

    def test_navigate_PID_11_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('PID.11.3')
        self.assertEqual(result, 'Zürich')

# ################################################################################################################

    def test_navigate_PID_11_4(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('PID.11.4')
        self.assertEqual(result, 'ZH')

# ################################################################################################################

    def test_navigate_PID_11_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('PID.11.5')
        self.assertEqual(result, '8001')

# ################################################################################################################

    def test_navigate_PID_18(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('PID.18')
        self.assertEqual(result, '2847')

# ################################################################################################################

    def test_navigate_PV1_1(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('PV1.1')
        self.assertEqual(result, '1')

# ################################################################################################################

    def test_navigate_PV1_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('PV1.2')
        self.assertEqual(result, 'O')

# ################################################################################################################

    def test_navigate_PV1_7(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('PV1.7')
        self.assertEqual(result, '7')

# ################################################################################################################

    def test_navigate_PV1_7_2(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('PV1.7.2')
        self.assertEqual(result, 'Wörner')

# ################################################################################################################

    def test_navigate_PV1_7_3(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('PV1.7.3')
        self.assertEqual(result, 'Güntér')

# ################################################################################################################

    def test_navigate_PV1_7_5(self) -> 'None':
        message = parse_message(_Raw_de_cgm_clinical_20, validate=False)
        result = message.get('PV1.7.5')
        self.assertEqual(result, 'MD')

# ################################################################################################################

    def test_build_MSH(self) -> 'None':
        segment = MSH()

        segment.sending_application = HD(hd_1='SENDE_APPLIKATION')
        segment.sending_facility = HD(hd_1='SENDE_EINRICHTUNG')
        segment.receiving_application = HD(hd_1='EMPFANGS_APPLIKATION')
        segment.receiving_facility = HD(hd_1='EMPFANGS_EINRICHTUNG')
        segment.date_time_of_message = '20260613083617'
        segment.message_type = MSG(msg_1='ADT', msg_2='A04')
        segment.message_control_id = '934576120260613083617'
        segment.processing_id = PT(pt_1='P')
        segment.version_id = VID(vid_1='2.3')

        serialized = segment.serialize()
        expected = 'MSH|^~\\&|SENDE_APPLIKATION|SENDE_EINRICHTUNG|EMPFANGS_APPLIKATION|EMPFANGS_EINRICHTUNG|20260613083617||ADT^A04|934576120260613083617|P|2.3||||'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_EVN(self) -> 'None':
        segment = EVN()

        segment.recorded_date_time = '20260613083617'

        serialized = segment.serialize()
        expected = 'EVN|A04|20260613083617|||'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PID(self) -> 'None':
        segment = PID()

        segment.set_id_pid = '1'
        segment.patient_identifier_list = CX(cx_1='246813')
        segment.patient_name = XPN(xpn_1='MÜNCHHAUSEN', xpn_2='THÉODOR')
        segment.date_time_of_birth = '19550718'
        segment.administrative_sex = CWE(cwe_1='M')
        segment.patient_address = XAD(xad_1='Brückenstraße 5', xad_3='Zürich', xad_4='ZH', xad_5='8001')
        segment.patient_account_number = CX(cx_1='2847')

        serialized = segment.serialize()
        expected = 'PID|1||246813||MÜNCHHAUSEN^THÉODOR^||19550718|M|||Brückenstraße 5^^Zürich^ZH^8001||(044)9391289^^^theodor@zürich-mail.ch|||||2847|99999999||||||||||||||||||||'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_PV1(self) -> 'None':
        segment = PV1()

        segment.set_id_pv1 = '1'
        segment.patient_class = CWE(cwe_1='O')
        segment.attending_doctor = XCN(xcn_1='7', xcn_2='Wörner', xcn_3='Güntér', xcn_5='MD')

        serialized = segment.serialize()
        expected = 'PV1|1|O|||||7^Wörner^Güntér^^MD^^^^|||||||||||||||||||||||||||||||||||||||||||||'
        self.assertEqual(serialized, expected)

# ################################################################################################################

    def test_build_full_message(self) -> 'None':
        message = ADT_A01()

        message.msh.sending_application = HD(hd_1='SENDE_APPLIKATION')
        message.msh.sending_facility = HD(hd_1='SENDE_EINRICHTUNG')
        message.msh.receiving_application = HD(hd_1='EMPFANGS_APPLIKATION')
        message.msh.receiving_facility = HD(hd_1='EMPFANGS_EINRICHTUNG')
        message.msh.date_time_of_message = '20260613083617'
        message.msh.message_type = MSG(msg_1='ADT', msg_2='A04')
        message.msh.message_control_id = '934576120260613083617'
        message.msh.processing_id = PT(pt_1='P')
        message.msh.version_id = VID(vid_1='2.3')

        message.evn.recorded_date_time = '20260613083617'

        message.pid.set_id_pid = '1'
        message.pid.patient_identifier_list = CX(cx_1='246813')
        message.pid.patient_name = XPN(xpn_1='MÜNCHHAUSEN', xpn_2='THÉODOR')
        message.pid.date_time_of_birth = '19550718'
        message.pid.administrative_sex = CWE(cwe_1='M')
        message.pid.patient_address = XAD(xad_1='Brückenstraße 5', xad_3='Zürich', xad_4='ZH', xad_5='8001')
        message.pid.patient_account_number = CX(cx_1='2847')

        message.pv1.set_id_pv1 = '1'
        message.pv1.patient_class = CWE(cwe_1='O')
        message.pv1.attending_doctor = XCN(xcn_1='7', xcn_2='Wörner', xcn_3='Güntér', xcn_5='MD')

        serialized = message.serialize()
        serialized_length = len(serialized)
        self.assertTrue(serialized_length > 0)

# ################################################################################################################
# ################################################################################################################
