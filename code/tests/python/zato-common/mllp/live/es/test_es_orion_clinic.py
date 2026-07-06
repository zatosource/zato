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
from zato.hl7v2.v2_9.datatypes import CNE, CQ, CWE, CX, EI, EIP, HD, MSG, PL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01Insurance, AdtA39Patient, MdmT02Observation, OmbO27Patient, OmbO27PatientVisit, OrmO01Order, OrmO01OrderDetail, \
    OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, \
    RspK22QueryResponse, SiuS12GeneralResource, SiuS12LocationResource, SiuS12Patient, SiuS12Resources
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, ADT_A39, MDM_T02, OMB_O27, ORM_O01, ORU_R01, QBP_Q21, RSP_K22, SIU_S12
from zato.hl7v2.v2_9.segments import AIG, AIL, BPO, ERR, EVN, IN1, MRG, MSA, MSH, OBR, OBX, ORC, PID, PV1, QAK, QPD, QRI, RCP, RGS, SCH, SPM, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('es', 'es-orion-clinic.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/es/es-orion-clinic.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORION_CLINIC')
        msh.sending_facility = HD(hd_1='HLAFE')
        msh.receiving_application = HD(hd_1='SIP_RECEPTOR')
        msh.receiving_facility = HD(hd_1='GVA')
        msh.date_time_of_message = '20260315083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20260315083000'
        evn.event_occurred = '20260315083000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CIPV034782916455', cx_4='SIP', cx_5='JHN', cx_9='CV&&ISO3166-2'),
            CX(cx_1='72849539T', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='280490061283', cx_4='SS', cx_5='SS', cx_9='ESP&&ISO3166'),
            CX(cx_1='HC610477', cx_4='HLAFE', cx_5='PI'),
        ]
        pid.patient_name = XPN(xpn_1='FERRER', xpn_2='AMPARO', xpn_3='TERESA')
        pid.mothers_maiden_name = XPN(xpn_1='GIMENO')
        pid.date_time_of_birth = '19780322'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CL&CERVANTES&8', xad_2='1o-D', xad_3='460023', xad_4='46', xad_5='46023', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^963782145~^WPN^CP^^^671234589~^NET^Internet^aferrer@gva.es'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HLAFE', pl_2='PLANTA6', pl_3='CAMA612', pl_4='Medicina Interna')
        pv1.attending_doctor = XCN(xcn_1='58012', xcn_2='ESTELLES', xcn_3='SALVADOR', xcn_4='BENITO', xcn_9='HLAFE')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='EPIS20260315001', cwe_4='GVA')
        pv1.prior_temporary_location = PL(pl_1='20260315083000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SNS')
        in1.insurance_company_id = CX(cx_1='GVA001')
        in1.insurance_company_name = XON(xon_1='CONSELLERIA DE SANITAT UNIVERSAL I SALUT PUBLICA')
        in1.insurance_company_address = XAD(xad_1='Calle Micer Masco 31', xad_3='Valencia', xad_5='46010', xad_6='ESP')

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
    """ Based on live/es/es-orion-clinic.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORION_CLINIC')
        msh.sending_facility = HD(hd_1='HLAFE')
        msh.receiving_application = HD(hd_1='SIP_RECEPTOR')
        msh.receiving_facility = HD(hd_1='GVA')
        msh.date_time_of_message = '20260316093000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02', msg_3='ADT_A02')
        msh.message_control_id = 'MSG00002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20260316093000'
        evn.event_occurred = '20260316093000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CIPV034782916455', cx_4='SIP', cx_5='JHN', cx_9='CV&&ISO3166-2'),
            CX(cx_1='72849539T', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='FERRER', xpn_2='AMPARO', xpn_3='TERESA')
        pid.mothers_maiden_name = XPN(xpn_1='GIMENO')
        pid.date_time_of_birth = '19780322'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CL&CERVANTES&8', xad_2='1o-D', xad_3='460023', xad_4='46', xad_5='46023', xad_6='ESP', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HLAFE', pl_2='PLANTA9', pl_3='CAMA903', pl_4='Cirugia General')
        pv1.attending_doctor = XCN(xcn_1='58012', xcn_2='ESTELLES', xcn_3='SALVADOR', xcn_4='BENITO', xcn_9='HLAFE')
        pv1.hospital_service = CWE(cwe_1='CIR')
        pv1.patient_type = CWE(cwe_1='EPIS20260315001', cwe_4='GVA')
        pv1.prior_temporary_location = PL(pl_1='20260316093000')

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/es/es-orion-clinic.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORION_CLINIC')
        msh.sending_facility = HD(hd_1='HLAFE')
        msh.receiving_application = HD(hd_1='SIP_RECEPTOR')
        msh.receiving_facility = HD(hd_1='GVA')
        msh.date_time_of_message = '20260320140000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03', msg_3='ADT_A03')
        msh.message_control_id = 'MSG00003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20260320140000'
        evn.event_occurred = '20260320140000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CIPV034782916455', cx_4='SIP', cx_5='JHN', cx_9='CV&&ISO3166-2'),
            CX(cx_1='72849539T', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='FERRER', xpn_2='AMPARO', xpn_3='TERESA')
        pid.mothers_maiden_name = XPN(xpn_1='GIMENO')
        pid.date_time_of_birth = '19780322'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CL&CERVANTES&8', xad_2='1o-D', xad_3='460023', xad_4='46', xad_5='46023', xad_6='ESP', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HLAFE', pl_2='PLANTA6', pl_3='CAMA612', pl_4='Medicina Interna')
        pv1.attending_doctor = XCN(xcn_1='58012', xcn_2='ESTELLES', xcn_3='SALVADOR', xcn_4='BENITO', xcn_9='HLAFE')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.patient_type = CWE(cwe_1='EPIS20260315001', cwe_4='GVA')
        pv1.prior_temporary_location = PL(pl_1='20260315083000')
        pv1.admit_date_time = '20260320140000'

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/es/es-orion-clinic.md, message no. 4
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORION_CLINIC')
        msh.sending_facility = HD(hd_1='HCLINICO')
        msh.receiving_application = HD(hd_1='SIP_RECEPTOR')
        msh.receiving_facility = HD(hd_1='GVA')
        msh.date_time_of_message = '20260321100000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20260321100000'
        evn.event_occurred = '20260321100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CIPV061593847202', cx_4='SIP', cx_5='JHN', cx_9='CV&&ISO3166-2'),
            CX(cx_1='41278653Y', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='HC710893', cx_4='HCLINICO', cx_5='PI', cx_9='ESP&&ISO3166'),
            CX(cx_1='120673481025', cx_4='SS', cx_5='SS', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='LLORENS', xpn_2='VICENT', xpn_3='JOAQUIN')
        pid.mothers_maiden_name = XPN(xpn_1='SORIANO')
        pid.date_time_of_birth = '19830915'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV&AUSIAS MARCH&22', xad_2='4o-C', xad_3='460110', xad_4='46', xad_5='46011', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^961478523~^ORN^CP^^^698712345'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HCLINICO', pl_2='CCEE', pl_3='CONS07', pl_4='Consultas Externas')
        pv1.attending_doctor = XCN(xcn_1='69034', xcn_2='BALLESTER', xcn_3='NURIA', xcn_4='CLIMENT', xcn_9='HCLINICO')
        pv1.hospital_service = CWE(cwe_1='AMB')
        pv1.patient_type = CWE(cwe_1='EPIS20260321001', cwe_4='GVA')
        pv1.prior_temporary_location = PL(pl_1='20260321100000')

        # .. build IN1 ..
        in1 = IN1()
        in1.set_id_in1 = '1'
        in1.health_plan_id = CWE(cwe_1='SNS')
        in1.insurance_company_id = CX(cx_1='GVA001')
        in1.insurance_company_name = XON(xon_1='CONSELLERIA DE SANITAT UNIVERSAL I SALUT PUBLICA')
        in1.insurance_company_address = XAD(xad_1='Calle Micer Masco 31', xad_3='Valencia', xad_5='46010', xad_6='ESP')

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
    """ Based on live/es/es-orion-clinic.md, message no. 5
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORION_CLINIC')
        msh.sending_facility = HD(hd_1='HPESET')
        msh.receiving_application = HD(hd_1='SIP_RECEPTOR')
        msh.receiving_facility = HD(hd_1='GVA')
        msh.date_time_of_message = '20260322090000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08', msg_3='ADT_A01')
        msh.message_control_id = 'MSG00005'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20260322090000'
        evn.event_occurred = '20260322090000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CIPV578234916071', cx_4='SIP', cx_5='JHN', cx_9='CV&&ISO3166-2'),
            CX(cx_1='26159483F', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='HC820346', cx_4='HPESET', cx_5='PI'),
        ]
        pid.date_time_of_birth = 'PASCUAL^INMACULADA^DOLORES'
        pid.administrative_sex = CWE(cwe_1='MONTESINOS')
        pid.pid_9 = '19710813'
        pid.race = CWE(cwe_1='F')
        pid.pid_13 = 'CL&RAMON Y CAJAL&31^2o-B^460131^46^46013^ESP^H~&&^^^^^ESP^M'
        pid.pid_15 = '^PRN^PH^^^962871456~^WPN^CP^^^679123456~^NET^Internet^ipascual@gmail.com'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HPESET', pl_2='PLANTA4', pl_3='CAMA408', pl_4='Neumologia')
        pv1.attending_doctor = XCN(xcn_1='73056', xcn_2='APARISI', xcn_3='RAMON', xcn_4='BELTRAN', xcn_9='HPESET')
        pv1.hospital_service = CWE(cwe_1='NEU')
        pv1.patient_type = CWE(cwe_1='EPIS20260320001', cwe_4='GVA')
        pv1.prior_temporary_location = PL(pl_1='20260320143000')

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
    """ Based on live/es/es-orion-clinic.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORION_CLINIC')
        msh.sending_facility = HD(hd_1='HLAFE')
        msh.receiving_application = HD(hd_1='SIP_RECEPTOR')
        msh.receiving_facility = HD(hd_1='GVA')
        msh.date_time_of_message = '20260323112947'
        msh.message_type = MSG(msg_1='ADT', msg_2='A40', msg_3='ADT_A39')
        msh.message_control_id = 'MSG00006'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20260323112947'
        evn.operator_id = XCN(xcn_1='ORION_CLINIC')
        evn.event_occurred = '20260323112947'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [
            CX(cx_1='CIPV034782916455', cx_4='SIP', cx_5='JHN', cx_9='CV&&ISO3166-2'),
            CX(cx_1='72849539T', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='HC610477', cx_4='HLAFE', cx_5='PI', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='FERRER', xpn_2='AMPARO', xpn_3='TERESA')
        pid.mothers_maiden_name = XPN(xpn_1='GIMENO')
        pid.date_time_of_birth = '19780322'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CL&CERVANTES&8', xad_2='1o-D', xad_3='460023', xad_4='46', xad_5='46023', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^^PH^^^^~^^CP^^^^~^^Internet^'
        pid.patient_death_date_and_time = 'N'
        pid.identity_reliability_code = CWE(cwe_1='20260101')

        # .. build MRG ..
        mrg = MRG()
        mrg.prior_patient_identifier_list = [CX(cx_1='HC610912', cx_4='HLAFE', cx_5='PI'), CX(cx_1='CIPV887423615790', cx_4='SIP', cx_5='JHN')]

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
    """ Based on live/es/es-orion-clinic.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORION_CLINIC')
        msh.sending_facility = HD(hd_1='HLAFE')
        msh.receiving_application = HD(hd_1='RADELEC_CV')
        msh.receiving_facility = HD(hd_1='GVA')
        msh.date_time_of_message = '20260401085928'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MSG00007'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='CIPV034782916455', cx_4='SIP', cx_5='JHN', cx_9='CV&&ISO3166-2')
        pid.pid_4 = '72849539T^^^MI^NNESP'
        pid.patient_name = XPN(xpn_1='FERRER', xpn_2='AMPARO', xpn_3='TERESA')
        pid.mothers_maiden_name = XPN(xpn_1='GIMENO')
        pid.date_time_of_birth = '19780322'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HLAFE', pl_2='PLANTA6', pl_3='CAMA612', pl_4='Medicina Interna')

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
        orc.placer_order_number = EI(ei_1='PET80001001', ei_2='ORION_CLINIC')
        orc.parent_order = EIP(eip_1='20260401085928')
        orc.orc_11 = '58012^ESTELLES^SALVADOR^BENITO^^^^^HLAFE'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PET80001001', ei_2='ORION_CLINIC')
        obr.universal_service_identifier = CWE(cwe_1='89001', cwe_2='Electrocardiograma 12 derivaciones', cwe_3='L')
        obr.observation_date_time = '20260401085928'

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
    """ Based on live/es/es-orion-clinic.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORION_CLINIC')
        msh.sending_facility = HD(hd_1='HCLINICO')
        msh.receiving_application = HD(hd_1='ORION_RIS')
        msh.receiving_facility = HD(hd_1='GVA')
        msh.date_time_of_message = '20260402113000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MSG00008'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CIPV061593847202', cx_4='SIP', cx_5='JHN', cx_9='CV&&ISO3166-2'),
            CX(cx_1='41278653Y', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='LLORENS', xpn_2='VICENT', xpn_3='JOAQUIN')
        pid.mothers_maiden_name = XPN(xpn_1='SORIANO')
        pid.date_time_of_birth = '19830915'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV&AUSIAS MARCH&22', xad_2='4o-C', xad_3='460110', xad_4='46', xad_5='46011', xad_6='ESP', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='HCLINICO', pl_2='URG', pl_3='BOX05', pl_4='Urgencias')
        pv1.attending_doctor = XCN(xcn_1='69034', xcn_2='BALLESTER', xcn_3='NURIA', xcn_4='CLIMENT', xcn_9='HCLINICO')
        pv1.hospital_service = CWE(cwe_1='URG')

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
        orc.placer_order_number = EI(ei_1='PET80002001', ei_2='ORION_CLINIC')
        orc.parent_order = EIP(eip_1='20260402113000')
        orc.orc_11 = '69034^BALLESTER^NURIA^CLIMENT^^^^^HCLINICO'
        orc.order_control_code_reason = CWE(cwe_1='46006', cwe_2='Hospital Clinico Universitario de Valencia', cwe_3='GVA_HCLINICO')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PET80002001', ei_2='ORION_CLINIC')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Radiografia torax PA y lateral', cwe_3='SERAM')
        obr.observation_date_time = '20260402113000'
        obr.danger_code = CWE(cwe_1='STAT')
        obr.obr_14 = '69034^BALLESTER^NURIA^CLIMENT^^^^^HCLINICO'

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
    """ Based on live/es/es-orion-clinic.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORION_CLINIC')
        msh.sending_facility = HD(hd_1='HLAFE')
        msh.receiving_application = HD(hd_1='GESTLAB')
        msh.receiving_facility = HD(hd_1='GVA')
        msh.date_time_of_message = '20260403090000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'MSG00009'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CIPV034782916455', cx_4='SIP', cx_5='JHN', cx_9='CV&&ISO3166-2'),
            CX(cx_1='72849539T', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='FERRER', xpn_2='AMPARO', xpn_3='TERESA')
        pid.mothers_maiden_name = XPN(xpn_1='GIMENO')
        pid.date_time_of_birth = '19780322'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HLAFE', pl_2='PLANTA6', pl_3='CAMA612', pl_4='Medicina Interna')
        pv1.attending_doctor = XCN(xcn_1='58012', xcn_2='ESTELLES', xcn_3='SALVADOR', xcn_4='BENITO', xcn_9='HLAFE')

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
        orc.placer_order_number = EI(ei_1='PET80003001', ei_2='ORION_CLINIC')
        orc.parent_order = EIP(eip_1='20260403090000')
        orc.orc_11 = '58012^ESTELLES^SALVADOR^BENITO^^^^^HLAFE'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PET80003001', ei_2='ORION_CLINIC')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Panel metabolico completo', cwe_3='LN')
        obr.observation_date_time = '20260403090000'
        obr.obr_16 = '58012^ESTELLES^SALVADOR^BENITO^^^^^HLAFE'

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
    """ Based on live/es/es-orion-clinic.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='RADELEC_CV')
        msh.sending_facility = HD(hd_1='GVA')
        msh.receiving_application = HD(hd_1='ORION_CLINIC')
        msh.receiving_facility = HD(hd_1='HLAFE')
        msh.date_time_of_message = '20260404111704'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MSG00010'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='CIPV034782916455', cx_4='SIP', cx_5='JHN', cx_9='CV&&ISO3166-2')
        pid.pid_4 = '72849539T^^^MI^NNESP'
        pid.patient_name = XPN(xpn_1='FERRER', xpn_2='AMPARO', xpn_3='TERESA')
        pid.mothers_maiden_name = XPN(xpn_1='GIMENO')
        pid.date_time_of_birth = '19780322'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HLAFE', pl_2='PLANTA6', pl_3='CAMA612', pl_4='Medicina Interna')

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
        orc.placer_order_number = EI(ei_1='PET80001001', ei_2='ORION_CLINIC')
        orc.filler_order_number = EI(ei_1='RES20260404001', ei_2='RADELEC_CV')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PET80001001', ei_2='ORION_CLINIC')
        obr.filler_order_number = EI(ei_1='RES20260404001', ei_2='RADELEC_CV')
        obr.universal_service_identifier = CWE(cwe_1='89001', cwe_2='Electrocardiograma 12 derivaciones', cwe_3='L')
        obr.observation_date_time = '20260404111513'
        obr.filler_field_2 = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
        obr.results_rpt_status_chng_date_time = '20260404111513'
        obr.result_status = 'F'
        obr.obr_27 = '^^^^20260404111513'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='89001-1', cwe_2='Ritmo', cwe_3='L')
        obx.obx_5 = 'Ritmo sinusal, frecuencia 78 lpm'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='89001-2', cwe_2='Eje', cwe_3='L')
        obx_2.obx_5 = 'Eje normal, 55 grados'
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='89001-3', cwe_2='Conclusion', cwe_3='L')
        obx_3.obx_5 = 'ECG dentro de limites normales'
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
    """ Based on live/es/es-orion-clinic.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GESTLAB')
        msh.sending_facility = HD(hd_1='HLAFE')
        msh.receiving_application = HD(hd_1='ORION_CLINIC')
        msh.receiving_facility = HD(hd_1='GVA')
        msh.date_time_of_message = '20260405160000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00011'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CIPV034782916455', cx_4='SIP', cx_5='JHN', cx_9='CV&&ISO3166-2'),
            CX(cx_1='72849539T', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='FERRER', xpn_2='AMPARO', xpn_3='TERESA')
        pid.mothers_maiden_name = XPN(xpn_1='GIMENO')
        pid.date_time_of_birth = '19780322'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HLAFE', pl_2='PLANTA6', pl_3='CAMA612', pl_4='Medicina Interna')
        pv1.attending_doctor = XCN(xcn_1='58012', xcn_2='ESTELLES', xcn_3='SALVADOR', xcn_4='BENITO', xcn_9='HLAFE')

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
        orc.placer_order_number = EI(ei_1='PET80003001', ei_2='ORION_CLINIC')
        orc.filler_order_number = EI(ei_1='LAB20260405001', ei_2='GESTLAB')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PET80003001', ei_2='ORION_CLINIC')
        obr.filler_order_number = EI(ei_1='LAB20260405001', ei_2='GESTLAB')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Panel metabolico completo', cwe_3='LN')
        obr.observation_date_time = '20260405140000'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucosa', cwe_3='LN')
        obx.obx_5 = '112'
        obx.units = CWE(cwe_1='mg/dL')
        obx.reference_range = '70-100'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='2160-0', cwe_2='Creatinina', cwe_3='LN')
        obx_2.obx_5 = '1.1'
        obx_2.units = CWE(cwe_1='mg/dL')
        obx_2.reference_range = '0.7-1.2'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='3094-0', cwe_2='Urea', cwe_3='LN')
        obx_3.obx_5 = '42'
        obx_3.units = CWE(cwe_1='mg/dL')
        obx_3.reference_range = '10-50'
        obx_3.interpretation_codes = CWE(cwe_1='N')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='2093-3', cwe_2='Colesterol total', cwe_3='LN')
        obx_4.obx_5 = '198'
        obx_4.units = CWE(cwe_1='mg/dL')
        obx_4.reference_range = '<200'
        obx_4.interpretation_codes = CWE(cwe_1='N')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='13457-7', cwe_2='LDL Colesterol', cwe_3='LN')
        obx_5.obx_5 = '130'
        obx_5.units = CWE(cwe_1='mg/dL')
        obx_5.reference_range = '<130'
        obx_5.interpretation_codes = CWE(cwe_1='H')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='2085-9', cwe_2='HDL Colesterol', cwe_3='LN')
        obx_6.obx_5 = '45'
        obx_6.units = CWE(cwe_1='mg/dL')
        obx_6.reference_range = '>40'
        obx_6.interpretation_codes = CWE(cwe_1='N')
        obx_6.observation_result_status = 'F'

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
    """ Based on live/es/es-orion-clinic.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GESTLAB')
        msh.sending_facility = HD(hd_1='HPESET')
        msh.receiving_application = HD(hd_1='ORION_CLINIC')
        msh.receiving_facility = HD(hd_1='GVA')
        msh.date_time_of_message = '20260406100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00012'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CIPV578234916071', cx_4='SIP', cx_5='JHN', cx_9='CV&&ISO3166-2'),
            CX(cx_1='26159483F', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='PASCUAL', xpn_2='INMACULADA', xpn_3='DOLORES')
        pid.mothers_maiden_name = XPN(xpn_1='MONTESINOS')
        pid.date_time_of_birth = '19710813'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HPESET', pl_2='PLANTA4', pl_3='CAMA408', pl_4='Neumologia')

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
        orc.placer_order_number = EI(ei_1='PET80004001', ei_2='ORION_CLINIC')
        orc.filler_order_number = EI(ei_1='MIC20260406001', ei_2='GESTLAB')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PET80004001', ei_2='ORION_CLINIC')
        obr.filler_order_number = EI(ei_1='MIC20260406001', ei_2='GESTLAB')
        obr.universal_service_identifier = CWE(cwe_1='87070', cwe_2='Cultivo esputo', cwe_3='L')
        obr.observation_date_time = '20260406080000'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='87070-1', cwe_2='Organismo aislado', cwe_3='L')
        obx.obx_5 = 'Streptococcus pneumoniae'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='18907-6', cwe_2='Penicilina', cwe_3='LN')
        obx_2.obx_5 = 'S'
        obx_2.units = CWE(cwe_1='ug/mL')
        obx_2.nature_of_abnormal_test = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='18928-2', cwe_2='Amoxicilina', cwe_3='LN')
        obx_3.obx_5 = 'S'
        obx_3.units = CWE(cwe_1='ug/mL')
        obx_3.nature_of_abnormal_test = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='18886-2', cwe_2='Eritromicina', cwe_3='LN')
        obx_4.obx_5 = 'R'
        obx_4.units = CWE(cwe_1='ug/mL')
        obx_4.nature_of_abnormal_test = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='18932-4', cwe_2='Levofloxacino', cwe_3='LN')
        obx_5.obx_5 = 'S'
        obx_5.units = CWE(cwe_1='ug/mL')
        obx_5.nature_of_abnormal_test = 'F'

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
    """ Based on live/es/es-orion-clinic.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORION_RIS')
        msh.sending_facility = HD(hd_1='HCLINICO')
        msh.receiving_application = HD(hd_1='ORION_CLINIC')
        msh.receiving_facility = HD(hd_1='GVA')
        msh.date_time_of_message = '20260407150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00013'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CIPV061593847202', cx_4='SIP', cx_5='JHN', cx_9='CV&&ISO3166-2'),
            CX(cx_1='41278653Y', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='LLORENS', xpn_2='VICENT', xpn_3='JOAQUIN')
        pid.mothers_maiden_name = XPN(xpn_1='SORIANO')
        pid.date_time_of_birth = '19830915'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='HCLINICO', pl_2='URG', pl_3='BOX05', pl_4='Urgencias')

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
        orc.placer_order_number = EI(ei_1='PET80002001', ei_2='ORION_CLINIC')
        orc.filler_order_number = EI(ei_1='INF20260407001', ei_2='ORION_RIS')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PET80002001', ei_2='ORION_CLINIC')
        obr.filler_order_number = EI(ei_1='INF20260407001', ei_2='ORION_RIS')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='Radiografia torax PA y lateral', cwe_3='SERAM')
        obr.observation_date_time = '20260407143000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='71020-1', cwe_2='Hallazgos', cwe_3='L')
        obx.obx_5 = 'Silueta cardiaca de tamano normal. Campos pulmonares limpios. No derrame pleural. Mediastino centrado.'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'RP'
        obx_2.observation_identifier = CWE(cwe_1='71020-2', cwe_2='Informe PDF', cwe_3='L')
        obx_2.obx_5 = 'https://orionclinic.gva.es/informes/INF20260407001.pdf^^APPLICATION^^'
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
    """ Based on live/es/es-orion-clinic.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORION_CLINIC')
        msh.sending_facility = HD(hd_1='HLAFE')
        msh.receiving_application = HD(hd_1='SIP')
        msh.receiving_facility = HD(hd_1='GVA')
        msh.date_time_of_message = '20260408101935'
        msh.message_type = MSG(msg_1='QBP', msg_2='Q22')
        msh.message_control_id = 'MSG00014'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'AL'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build QPD ..
        qpd = QPD()
        qpd.message_query_name = CWE(cwe_1='1', cwe_2='IHE PDQ Query', cwe_3='HL70471')
        qpd.query_tag = 'QRY20260408001'
        qpd.qpd_3 = 'CIPAUT^CIPV034782916455'

        # .. build RCP ..
        rcp = RCP()
        rcp.query_priority = 'I'
        rcp.quantity_limited_request = CQ(cq_1='20', cq_2='RD&Records&HL70126')

        # .. assemble the full message ..
        msg = QBP_Q21()
        msg.msh = msh
        msg.qpd = qpd
        msg.rcp = rcp

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
    """ Based on live/es/es-orion-clinic.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='SIP')
        msh.sending_facility = HD(hd_1='GVA')
        msh.receiving_application = HD(hd_1='ORION_CLINIC')
        msh.receiving_facility = HD(hd_1='HLAFE')
        msh.date_time_of_message = '20260408101936'
        msh.message_type = MSG(msg_1='RSP', msg_2='K22')
        msh.message_control_id = 'MSG00015'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'MSG00014'

        # .. build ERR ..
        err = ERR()
        err.hl7_error_code = CWE(cwe_1='0', cwe_2='Message accepted', cwe_3='HL70357', cwe_4='0', cwe_5='Procesado correctamente', cwe_6='GVA_ERROR')
        err.severity = 'I'

        # .. build QAK ..
        qak = QAK()
        qak.query_tag = 'QRY20260408001'
        qak.query_response_status = 'OK'

        # .. build QPD ..
        qpd = QPD()
        qpd.message_query_name = CWE(cwe_1='1', cwe_2='IHE PDQ Query', cwe_3='HL70471')
        qpd.query_tag = 'QRY20260408001'
        qpd.qpd_3 = 'CIPAUT^CIPV034782916455'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CIPV034782916455', cx_4='SIP', cx_5='JHN', cx_9='CV&&ISO3166-2'),
            CX(cx_1='72849539T', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='HC610477', cx_4='HLAFE', cx_5='PI', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='FERRER', xpn_2='AMPARO', xpn_3='TERESA')
        pid.mothers_maiden_name = XPN(xpn_1='GIMENO')
        pid.date_time_of_birth = '19780322'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='CL&CERVANTES&8', xad_2='1o-D', xad_3='460023', xad_4='46', xad_5='46023', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^963782145'
        pid.patient_death_date_and_time = 'N'

        # .. build QRI ..
        qri = QRI()
        qri.candidate_confidence = '1'

        # .. build the QUERY_RESPONSE group ..
        query_response = RspK22QueryResponse()
        query_response.pid = pid
        query_response.qri = qri

        # .. assemble the full message ..
        msg = RSP_K22()
        msg.msh = msh
        msg.msa = msa
        msg.err = err
        msg.qak = qak
        msg.qpd = qpd
        msg.query_response = query_response

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
    """ Based on live/es/es-orion-clinic.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORION_CLINIC')
        msh.sending_facility = HD(hd_1='HLAFE')
        msh.receiving_application = HD(hd_1='BBANK')
        msh.receiving_facility = HD(hd_1='GVA')
        msh.date_time_of_message = '20260409090131'
        msh.message_type = MSG(msg_1='OMB', msg_2='O27', msg_3='OMB_O27')
        msh.message_control_id = 'MSG00016'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CIPV034782916455', cx_4='SIP', cx_5='JHN', cx_9='CV&&ISO3166-2'),
            CX(cx_1='SHJD310801911024', cx_4='MS', cx_5='HC', cx_9='ESP&&ISO3166'),
            CX(cx_1='72849539T', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='280490061283', cx_4='SS', cx_5='SS', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='FERRER', xpn_2='AMPARO', xpn_3='TERESA')
        pid.mothers_maiden_name = XPN(xpn_1='GIMENO')
        pid.date_time_of_birth = '19780322'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = [
            XAD(xad_1='CL&CERVANTES&8', xad_2='1o-D', xad_3='460023', xad_4='46', xad_5='46023', xad_6='ESP', xad_7='H'),
            XAD(xad_1='&&', xad_6='ESP', xad_7='M'),
        ]
        pid.pid_13 = '^PRN^PH^^^^^^^^^963782145'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HLAFE', pl_2='PLANTA6', pl_3='CAMA612', pl_4='Medicina Interna')
        pv1.attending_doctor = XCN(xcn_1='58012', xcn_2='ESTELLES', xcn_3='SALVADOR', xcn_4='BENITO', xcn_9='HLAFE')
        pv1.hospital_service = CWE(cwe_1='MED')
        pv1.visit_number = CX(cx_1='EPIS20260315001', cx_4='GVA')
        pv1.pv1_51 = ''

        # .. build the PATIENT_VISIT group ..
        patient_visit = OmbO27PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OmbO27Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.specimen_identifier = EIP(eip_1='PET88001001')

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='PET88001001', ei_2='ORION_CLINIC')
        orc.filler_order_number = EI(ei_1='RES88001', ei_2='BBANK')
        orc.date_time_of_order_event = '20260409090000'
        orc.orc_10 = 'ESTELLES, SALVADOR'
        orc.orc_11 = 'ESTELLES, SALVADOR'
        orc.orc_12 = '58012^ESTELLES^SALVADOR^BENITO^^^^^HLAFE'
        orc.orc_18 = 'ESTELLES, SALVADOR'

        # .. build BPO ..
        bpo = BPO()
        bpo.set_id_bpo = 'CHEM^Concentrado de Hematies'
        bpo.bp_universal_service_identifier = CWE(cwe_1='3')
        bpo.bp_quantity = '3'
        bpo.bp_units = CWE(cwe_1='20260408200001')
        bpo.bpo_7 = 'P121^^^^'
        bpo.bp_intended_dispense_from_address = XAD(xad_1='20260408211001')
        bpo.bpo_10 = 'P121^^^^'
        bpo.bpo_14 = ''

        # .. build BPO ..
        bpo_2 = BPO()
        bpo_2.set_id_bpo = 'PFC^Plasma Fresco Congelado'
        bpo_2.bp_universal_service_identifier = CWE(cwe_1='2')
        bpo_2.bp_quantity = '2'
        bpo_2.bp_units = CWE(cwe_1='20260408200001')
        bpo_2.bpo_7 = 'P121^^^^'
        bpo_2.bp_intended_dispense_from_address = XAD(xad_1='20260408211001')
        bpo_2.bpo_10 = 'P121^^^^'
        bpo_2.bpo_14 = ''

        # .. assemble the full message ..
        msg = OMB_O27()
        msg.msh = msh
        msg.patient = patient
        msg.extra_segments = [spm, orc, bpo, bpo_2]

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
    """ Based on live/es/es-orion-clinic.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GESTLAB')
        msh.sending_facility = HD(hd_1='HLAFE')
        msh.receiving_application = HD(hd_1='ORION_CLINIC')
        msh.receiving_facility = HD(hd_1='GVA')
        msh.date_time_of_message = '20260410090200'
        msh.message_type = MSG(msg_1='ACK', msg_3='ACK')
        msh.message_control_id = 'MSG00017'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'MSG00009'

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa

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
    """ Based on live/es/es-orion-clinic.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORION_CLINIC')
        msh.sending_facility = HD(hd_1='HLAFE')
        msh.receiving_application = HD(hd_1='HCE_RECEPTOR')
        msh.receiving_facility = HD(hd_1='GVA')
        msh.date_time_of_message = '20260411100000'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'MSG00018'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20260411100000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CIPV034782916455', cx_4='SIP', cx_5='JHN', cx_9='CV&&ISO3166-2'),
            CX(cx_1='72849539T', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='FERRER', xpn_2='AMPARO', xpn_3='TERESA')
        pid.mothers_maiden_name = XPN(xpn_1='GIMENO')
        pid.date_time_of_birth = '19780322'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HLAFE', pl_2='PLANTA6', pl_3='CAMA612', pl_4='Medicina Interna')

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='HP', cwe_2='Informe de Alta', cwe_3='L')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20260411100000'
        txa.primary_activity_provider_code_name = XCN(xcn_1='58012', xcn_2='ESTELLES', xcn_3='SALVADOR', xcn_4='BENITO', xcn_9='HLAFE')
        txa.transcription_date_time = '20260411100000'
        txa.parent_document_number = EI(ei_1='DOC20260411001')
        txa.document_confidentiality_status = 'AU'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='18842-5', cwe_2='Informe de alta hospitalaria', cwe_3='LN')
        obx.obx_5 = (
            '^APPLICATION^PDF^Base64^'
            'JVBERi0xLjcNCiW1tbW1DQoxIDAgb2JqDQo8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4NCmVuZG9iag0KDQoyIDAgb2JqDQo8PCAvVHlwZSAvUGFnZXMgL0tpZHMgWzMg'
            'MCBSXSAvQ291bnQgMSA+Pg0KZW5kb2JqDQoNCjMgMCBvYmoNCjw8IC9UeXBlIC9QYWdlIC9QYXJlbnQgMiAwIFIgL01lZGlhQm94IFswIDAgNjEyIDc5Ml0gPj4NCmVuZG9iag0KDQp4'
            'cmVmDQowIDQNCjAwMDAwMDAwMDAgNjU1MzUgZg0KMDAwMDAwMDAxNSAwMDAwMCBuDQowMDAwMDAwMDc0IDAwMDAwIG4NCjAwMDAwMDAxNDMgMDAwMDAgbg0KDQp0cmFpbGVyDQo8PCAv'
            'U2l6ZSA0IC9Sb290IDEgMCBSID4+DQpzdGFydHhyZWYNCjIzNg0KJSVFT0YNCg=='
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
    """ Based on live/es/es-orion-clinic.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ENDOSC')
        msh.sending_facility = HD(hd_1='HLAFE')
        msh.receiving_application = HD(hd_1='ORION_CLINIC')
        msh.receiving_facility = HD(hd_1='GVA')
        msh.date_time_of_message = '20260412140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'MSG00019'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CIPV034782916455', cx_4='SIP', cx_5='JHN', cx_9='CV&&ISO3166-2'),
            CX(cx_1='72849539T', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='FERRER', xpn_2='AMPARO', xpn_3='TERESA')
        pid.mothers_maiden_name = XPN(xpn_1='GIMENO')
        pid.date_time_of_birth = '19780322'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='HLAFE', pl_2='PLANTA6', pl_3='CAMA612', pl_4='Medicina Interna')

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
        orc.placer_order_number = EI(ei_1='PET80005001', ei_2='ORION_CLINIC')
        orc.filler_order_number = EI(ei_1='END20260412001', ei_2='ENDOSC')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PET80005001', ei_2='ORION_CLINIC')
        obr.filler_order_number = EI(ei_1='END20260412001', ei_2='ENDOSC')
        obr.universal_service_identifier = CWE(cwe_1='45378', cwe_2='Colonoscopia diagnostica', cwe_3='CPT')
        obr.observation_date_time = '20260412130000'
        obr.result_status = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='45378-1', cwe_2='Hallazgos', cwe_3='L')
        obx.obx_5 = (
            'Colonoscopia completa hasta ciego. Mucosa de aspecto normal en todo el trayecto. Polipo sesil de 5mm en sigma, resecado con asa fria. Se env'
            'ia a anatomia patologica.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='45378-2', cwe_2='Imagen endoscopica polipo', cwe_3='L')
        obx_2.obx_5 = (
            '^IMAGE^JPEG^Base64^'
            '/9j/4AAQSkZJRgABAQEASABIAAD/4gIcSUNDX1BST0ZJTEUAAQEAAAIMbGNtcwIQAABtbnRyUkdCIFhZWiAH3AABABkAAwApADlhY3NwQVBQTAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            'APbWAAEAAAAA0y1sY21zAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKZGVzYwAAAP/aAAwDAQACEQMRAD8A3+AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH//Z'
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
    """ Based on live/es/es-orion-clinic.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ORION_CLINIC')
        msh.sending_facility = HD(hd_1='HCLINICO')
        msh.receiving_application = HD(hd_1='CITAWEB')
        msh.receiving_facility = HD(hd_1='GVA')
        msh.date_time_of_message = '20260413080000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'MSG00020'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='CITA20260420001', ei_2='ORION_CLINIC')
        sch.appointment_reason = CWE(cwe_1='CONSULTA', cwe_2='Consulta Cardiologia', cwe_4='20', cwe_5='MIN')
        sch.appointment_type = CWE(cwe_4='20260420090000', cwe_5='20260420091500')
        sch.sch_9 = '69034^BALLESTER^NURIA^CLIMENT^^^^^HCLINICO'
        sch.appointment_duration_units = CNE(cne_3='PH', cne_6='961987654')
        sch.sch_11 = '69034^BALLESTER^NURIA^CLIMENT^^^^^HCLINICO'
        sch.placer_contact_person = XCN(xcn_3='PH', xcn_6='961987654')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='CIPV061593847202', cx_4='SIP', cx_5='JHN', cx_9='CV&&ISO3166-2'),
            CX(cx_1='41278653Y', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='LLORENS', xpn_2='VICENT', xpn_3='JOAQUIN')
        pid.mothers_maiden_name = XPN(xpn_1='SORIANO')
        pid.date_time_of_birth = '19830915'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='AV&AUSIAS MARCH&22', xad_2='4o-C', xad_3='460110', xad_4='46', xad_5='46011', xad_6='ESP', xad_7='H')
        pid.pid_13 = '^PRN^PH^^^961478523'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='HCLINICO', pl_2='CCEE', pl_3='CONS12', pl_4='Cardiologia')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'

        # .. build AIG ..
        aig = AIG()
        aig.set_id_aig = '1'
        aig.resource_id = CWE(cwe_1='69034', cwe_2='BALLESTER', cwe_3='NURIA', cwe_4='CLIMENT', cwe_9='HCLINICO')

        # .. build the GENERAL_RESOURCE group ..
        general_resource = SiuS12GeneralResource()
        general_resource.aig = aig

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='HCLINICO', pl_2='CCEE', pl_3='CONS12', pl_4='Cardiologia')

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
