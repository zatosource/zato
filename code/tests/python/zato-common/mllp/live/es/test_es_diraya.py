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
from zato.hl7v2.v2_9.datatypes import CQ, CWE, CX, EI, EIP, HD, MSG, OG, PL, PPN, PT, RPT, VID, XAD, XCN, XPN
from zato.hl7v2.v2_9.groups import MdmT02CommonOrder, MdmT02Observation, OmbO27Patient, OmbO27PatientVisit, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, \
    OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, OruR01Patient, OruR01PatientResult, OruR01Visit, RdeO11Order, \
    RdeO11Patient, RdeO11PatientVisit, RdeO11TimingEncoded, RspK22QueryResponse, SiuS12LocationResource, SiuS12Patient, SiuS12PersonnelResource, \
    SiuS12Resources, SiuS12Service, SrmS01Patient, SrmS01Resources, SrmS01Service
from zato.hl7v2.v2_9.messages import ACK, ADT_A01, ADT_A02, ADT_A03, MDM_T02, OMB_O27, ORM_O01, ORU_R01, QBP_Q21, RDE_O11, RSP_K22, SIU_S12, SRM_S01
from zato.hl7v2.v2_9.segments import AIL, AIP, AIS, ARQ, BPO, DG1, ERR, EVN, MSA, MSH, OBR, OBX, ORC, PID, PV1, QAK, QPD, QRI, RCP, RGS, RXE, RXR, SCH, SPM, \
    TQ1, TXA

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('es', 'es-diraya.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/es/es-diraya.md, message no. 1
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS')
        msh.sending_facility = HD(hd_1='HOSPITAL')
        msh.receiving_application = HD(hd_1='BBANK')
        msh.receiving_facility = HD(hd_1='EXTERNO')
        msh.date_time_of_message = '20250429090131'
        msh.message_type = MSG(msg_1='OMB', msg_2='O27', msg_3='OMB_O27')
        msh.message_control_id = '82345678'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='71489233X', cx_4='HIS', cx_5='PI', cx_9='2828&&'),
            CX(cx_1='SHJD410901922035', cx_4='MS', cx_5='HC', cx_9='ESP&&ISO3166'),
            CX(cx_1='2210002200', cx_4='CA13', cx_5='JHN', cx_9='CL&&ISO3166'),
            CX(cx_1='44829156', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166'),
            CX(cx_1='33/00000048/07', cx_4='SS', cx_5='SS', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='LEON', xpn_2='ROCIO')
        pid.mothers_maiden_name = XPN(xpn_1='VEGA')
        pid.date_time_of_birth = '19880922'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = [
            XAD(xad_1='CL&SIERPES&14', xad_2='CENTRO SALUD', xad_3='41004', xad_4='41', xad_5='41091', xad_6='ESP', xad_7='H', xad_8='SEVILLA'),
            XAD(xad_1='&&', xad_6='ESP', xad_7='M', xad_8=''),
        ]
        pid.pid_13 = '^PRN^PH^^^^^^^^^+34654887123'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_3='405C', pl_4='')
        pv1.attending_doctor = XCN(xcn_1='777', xcn_2='BERMUDEZ', xcn_3='CARLOS', xcn_4='DE LUNA', xcn_8='')
        pv1.hospital_service = CWE(cwe_1='MIN')
        pv1.visit_number = CX(cx_1='82345', cx_6='')
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
        spm.specimen_identifier = EIP(eip_1='22345667')

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='22345667')
        orc.filler_order_number = EI(ei_1='22222333')
        orc.date_time_of_order_event = '20250429090000'
        orc.orc_10 = 'BERMUDEZ, CARLOS'
        orc.orc_11 = 'BERMUDEZ, CARLOS'
        orc.orc_12 = '777^BERMUDEZ^CARLOS^DE LUNA'
        orc.orc_18 = 'BERMUDEZ, CARLOS'

        # .. build BPO ..
        bpo = BPO()
        bpo.set_id_bpo = 'CHEM^Concentrado de Hematíes'
        bpo.bp_universal_service_identifier = CWE(cwe_1='2')
        bpo.bp_quantity = '2'
        bpo.bp_units = CWE(cwe_1='20250428200001')
        bpo.bpo_7 = 'P121^^^^'
        bpo.bp_intended_dispense_from_address = XAD(xad_1='20250428211001')
        bpo.bpo_10 = 'P121^^^^'
        bpo.bpo_14 = ''

        # .. build BPO ..
        bpo_2 = BPO()
        bpo_2.set_id_bpo = 'PQ^Pool Plaquetas'
        bpo_2.bp_universal_service_identifier = CWE(cwe_1='1')
        bpo_2.bp_quantity = '1'
        bpo_2.bp_units = CWE(cwe_1='202504281200001')
        bpo_2.bpo_7 = 'P121^^^^'
        bpo_2.bp_intended_dispense_from_address = XAD(xad_1='20250428211001')
        bpo_2.bpo_10 = 'P121^^^^'
        bpo_2.bpo_14 = ''

        # .. assemble the full message ..
        msg = OMB_O27()
        msg.msh = msh
        msg.patient = patient
        msg.extra_segments = [spm, orc, bpo, bpo_2]

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
    """ Based on live/es/es-diraya.md, message no. 2
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS')
        msh.sending_facility = HD(hd_1='HOSPITAL')
        msh.receiving_application = HD(hd_1='BBANK')
        msh.receiving_facility = HD(hd_1='EXTERNO')
        msh.date_time_of_message = '20250429090131'
        msh.message_type = MSG(msg_1='ACK', msg_3='ACK')
        msh.message_control_id = '82345679'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AR'
        msa.message_control_id = '823456'

        # .. build ERR ..
        err = ERR()
        err.err_1 = 'PID^1^16^103&Table value not found&HL70357'

        # .. assemble the full message ..
        msg = ACK()
        msg.msh = msh
        msg.msa = msa
        msg.err = err

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
    """ Based on live/es/es-diraya.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NSI')
        msh.receiving_application = HD(hd_1='LAB')
        msh.date_time_of_message = '20250827120759'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        msh.message_control_id = '8c2efhusuesgeh8b'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.7')
        msh.application_acknowledgment_type = 'AL'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '18000101000000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='70829', cx_5='HI'), CX(cx_1='52376841T', cx_5='DNI')]
        pid.patient_name = XPN(xpn_1='JIMENEZ', xpn_2='ALVARO')
        pid.mothers_maiden_name = XPN(xpn_1='CARMONA')
        pid.date_time_of_birth = '19930415000000'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.pid_12 = '&CARRER DE VALENCIA&112^^BARCELONA'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.referring_doctor = XCN(xcn_1='2037', xcn_2='CORDERO', xcn_3='JULIA')
        pv1.pv1_13 = ''

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/es/es-diraya.md, message no. 4
    """

    maxDiff = None

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
    """ Based on live/es/es-diraya.md, message no. 5
    """

    maxDiff = None

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
    """ Based on live/es/es-diraya.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS')
        msh.sending_facility = HD(hd_1='HOSPITAL')
        msh.receiving_application = HD(hd_1='ANALIZADOR')
        msh.receiving_facility = HD(hd_1='SEMANTICO')
        msh.date_time_of_message = '20250820183002'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02', msg_3='MDM_T02')
        msh.message_control_id = 'E59DD457-874F-4044-8239-86AB68B3BB58'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T10'
        evn.recorded_date_time = '20250820183002'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='30348424')
        pid.patient_name = XPN(xpn_1='QUINTANA', xpn_2='SERGIO')
        pid.mothers_maiden_name = XPN(xpn_1='TORRES')
        pid.date_time_of_birth = '20160718'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.pid_19 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')
        pv1.pv1_3 = '^^'
        pv1.pv1_6 = '^^'
        pv1.hospital_service = CWE(cwe_1='HOS')
        pv1.visit_number = CX(cx_1='22223656')
        pv1.discharge_disposition = CWE(cwe_1='0')
        pv1.admit_date_time = '20250614220819'
        pv1.discharge_date_time = '20250615000100'
        pv1.pv1_52 = ''

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='Informe de Alta')
        txa.document_content_presentation = 'TX'
        txa.origination_date_time = '20250614235600'
        txa.unique_document_number = EI(ei_1='GUID23498866b6b666b62')
        txa.document_completion_status = 'AU'
        txa.txa_22 = ''

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='INF_HOL', cwe_2='GUID23498866b6b666b62.pdf', cwe_3='INTR', cwe_5='')
        obx.observation_sub_id = OG(og_1='1')
        obx.obx_5 = (
            '^^TX^Base64^'
            'e1xydGYxXGFuc2lcYW5zaWNwZzEyNTJcZGVmZjBcZGVmbGFuZzMwODJ7XGZvbnR0Ymxce2ZcMFxmcm9tYW57VGltZXMgTmV3IFJvbWFuO30NCntcZlwxXGZzd2lzc3tBcmlhbDt9fX0N'
            'CntcZlwyXGZtb2Rlcm57Q291cmllciBOZXc7fX0NCntcY29sb3J0Ymw7XHJlZDBcZ3JlZW4wXGJsdWUwO30NCnt8^^^^'
        )
        obx.nature_of_abnormal_test = 'U'
        obx.obx_14 = '^^^^'
        obx.obx_15 = '^^^'
        obx.obx_16 = '^^^^'
        obx.obx_19 = ''

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
    """ Based on live/es/es-diraya.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='02')
        msh.sending_facility = HD(hd_1='01')
        msh.receiving_application = HD(hd_1='81')
        msh.receiving_facility = HD(hd_1='01')
        msh.date_time_of_message = '20250404085928'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = '67857464'
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'AL'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='49617544914', cx_4='001')
        pid.pid_4 = 'PASSPORTQRST^^^1114&000'
        pid.patient_name = XPN(xpn_1='SEGURA', xpn_2='MARISOL', xpn_3='INES')
        pid.date_time_of_birth = '19890312'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.assigned_patient_location = PL(pl_1='CODAUXCENTRO')

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
        orc.placer_order_number = EI(ei_1='92155627')

        # .. build the ORDER group ..
        order = OrmO01Order()
        order.orc = orc

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
    """ Based on live/es/es-diraya.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.msh_2 = '^~\\\\&'
        msh.sending_application = HD(hd_1='20')
        msh.sending_facility = HD(hd_1='13')
        msh.receiving_application = HD(hd_1='81')
        msh.receiving_facility = HD(hd_1='01')
        msh.date_time_of_message = '20251007145211000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = '40573730'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='49617544914', cx_4='001')
        pid.pid_4 = 'PASSPORTQRST^^^1114&000'
        pid.patient_name = XPN(xpn_1='SEGURA', xpn_2='MARISOL', xpn_3='INES')
        pid.date_time_of_birth = '19890312'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='ADM')
        pv1.assigned_patient_location = PL(pl_1='UEPE', pl_2='0117M', pl_3='0117V', pl_4='20')
        pv1.attending_doctor = XCN(xcn_1='23456', xcn_2='RAMIS', xcn_3='GABRIEL', xcn_4='FERRER', xcn_9='018')
        pv1.hospital_service = CWE(cwe_1='PEDH')
        pv1.admit_source = CWE(cwe_1='PEDC')
        pv1.admitting_doctor = XCN(xcn_1='23456', xcn_2='RAMIS', xcn_3='GABRIEL', xcn_4='FERRER', xcn_9='018')
        pv1.patient_type = CWE(cwe_1='A')
        pv1.visit_number = CX(cx_1='2012794167', cx_4='20')
        pv1.admit_date_time = '20251007112800000'

        # .. build the PATIENT_VISIT group ..
        patient_visit = OrmO01PatientVisit()
        patient_visit.pv1 = pv1

        # .. build the PATIENT group ..
        patient = OrmO01Patient()
        patient.pid = pid
        patient.patient_visit = patient_visit

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'CA'
        orc.placer_order_number = EI(ei_1='18868695', ei_2='20')
        orc.placer_order_group_number = EI(ei_1='9532081', ei_2='20')
        orc.order_status = 'CA'
        orc.orc_7 = '^^^20251007134031000^^1'
        orc.date_time_of_order_event = '20251007134031000'
        orc.orc_12 = '2345^RAMIS^GABRIEL^FERRER^^^^^018'
        orc.orc_17 = '14447^Hospital Mateu Orfila^TES_V_HOSP_CS_UBS'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='18868695', ei_2='20')
        obr.universal_service_identifier = CWE(cwe_1='21780', cwe_2='Electrocardiograma (Radelec)', cwe_3='L')
        obr.observation_date_time = '20251007134031000'
        obr.obr_16 = '23456^RAMIS^GABRIEL^FERRER^^^^^018'
        obr.obr_27 = '^^^^^1'
        obr.scheduled_date_time = '20251007134031000'

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
    """ Based on live/es/es-diraya.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.msh_2 = '^~\\\\&'
        msh.sending_application = HD(hd_1='IBE')
        msh.sending_facility = HD(hd_1='IBE')
        msh.receiving_application = HD(hd_1='H.Mateu Orfila')
        msh.receiving_facility = HD(hd_1='00')
        msh.date_time_of_message = '20251008111704'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'cf9gc2642109202512281502'
        msh.processing_id = PT(pt_1='P', pt_2='T')
        msh.version_id = VID(vid_1='2.5')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='49617544914', cx_4='001')
        pid.pid_4 = 'PASSPORTQRST^^^1114&000'
        pid.patient_name = XPN(xpn_1='SEGURA', xpn_2='MARISOL', xpn_3='INES')
        pid.date_time_of_birth = '19890312'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='E')

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
        obr.filler_order_number = EI(ei_1='202510911284566915')
        obr.observation_date_time = '20251008111513'
        obr.filler_field_2 = 'cf8g85b1-d878-54bg-0477-65gdd3ec3c32'
        obr.results_rpt_status_chng_date_time = '20251008111513'
        obr.result_status = 'F'
        obr.obr_27 = '^^^^20251008111513'

        # .. build the ORDER_OBSERVATION group ..
        order_observation = OruR01OrderObservation()
        order_observation.obr = obr

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
    """ Based on live/es/es-diraya.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='20')
        msh.sending_facility = HD(hd_1='12')
        msh.receiving_application = HD(hd_1='81')
        msh.receiving_facility = HD(hd_1='01')
        msh.date_time_of_message = '20251007190023000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        msh.message_control_id = '40576618'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20251007190020000'
        evn.event_occurred = '20251007190020000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='49617544914', cx_4='001')
        pid.pid_4 = 'PASSPORTQRST^^^1114&000'
        pid.patient_name = XPN(xpn_1='SEGURA', xpn_2='MARISOL', xpn_3='INES')
        pid.date_time_of_birth = '19890312'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='ADM')
        pv1.assigned_patient_location = PL(pl_1='K2UEM2', pl_2='K238', pl_3='K238B', pl_4='20')
        pv1.attending_doctor = XCN(xcn_1='2342', xcn_2='MATEU', xcn_3='ANTONIA', xcn_4='BESTARD', xcn_9='018')
        pv1.hospital_service = CWE(cwe_1='KMIRH')
        pv1.admit_source = CWE(cwe_1='KURGU')
        pv1.admitting_doctor = XCN(xcn_1='2342', xcn_2='MATEU', xcn_3='ANTONIA', xcn_4='BESTARD', xcn_9='018')
        pv1.patient_type = CWE(cwe_1='A')
        pv1.visit_number = CX(cx_1='2012796641', cx_4='20')
        pv1.admit_date_time = '20251007185900000'

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
    """ Based on live/es/es-diraya.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='20')
        msh.sending_facility = HD(hd_1='12')
        msh.receiving_application = HD(hd_1='81')
        msh.receiving_facility = HD(hd_1='01')
        msh.date_time_of_message = '20251007190023000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02')
        msh.message_control_id = '40576618'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20251007190020000'
        evn.event_occurred = '20251007190020000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='49617544914', cx_4='001')
        pid.pid_4 = 'PASSPORTQRST^^^1114&000'
        pid.patient_name = XPN(xpn_1='SEGURA', xpn_2='MARISOL', xpn_3='INES')
        pid.date_time_of_birth = '19890312'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='ADM')
        pv1.assigned_patient_location = PL(pl_1='K2UEM2', pl_2='K238', pl_3='K238B', pl_4='20')
        pv1.attending_doctor = XCN(xcn_1='2342', xcn_2='MATEU', xcn_3='ANTONIA', xcn_4='BESTARD', xcn_9='018')
        pv1.hospital_service = CWE(cwe_1='KMIRH')
        pv1.admit_source = CWE(cwe_1='KURGU')
        pv1.admitting_doctor = XCN(xcn_1='2342', xcn_2='MATEU', xcn_3='ANTONIA', xcn_4='BESTARD', xcn_9='018')
        pv1.patient_type = CWE(cwe_1='A')
        pv1.visit_number = CX(cx_1='2012796641', cx_4='20')
        pv1.admit_date_time = '20251007185900000'

        # .. assemble the full message ..
        msg = ADT_A02()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/es/es-diraya.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='20')
        msh.sending_facility = HD(hd_1='12')
        msh.receiving_application = HD(hd_1='81')
        msh.receiving_facility = HD(hd_1='01')
        msh.date_time_of_message = '20251007190023000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03')
        msh.message_control_id = '40576618'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'

        # .. build EVN ..
        evn = EVN()
        evn.recorded_date_time = '20251007190020000'
        evn.event_occurred = '20251007190020000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='49617544914', cx_4='001')
        pid.pid_4 = 'PASSPORTQRST^^^1114&000'
        pid.patient_name = XPN(xpn_1='SEGURA', xpn_2='MARISOL', xpn_3='INES')
        pid.date_time_of_birth = '19890312'
        pid.administrative_sex = CWE(cwe_1='F')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='ADM')
        pv1.assigned_patient_location = PL(pl_1='K2UEM2', pl_2='K238', pl_3='K238B', pl_4='20')
        pv1.attending_doctor = XCN(xcn_1='2342', xcn_2='MATEU', xcn_3='ANTONIA', xcn_4='BESTARD', xcn_9='018')
        pv1.hospital_service = CWE(cwe_1='KMIRH')
        pv1.admit_source = CWE(cwe_1='KURGU')
        pv1.admitting_doctor = XCN(xcn_1='2342', xcn_2='MATEU', xcn_3='ANTONIA', xcn_4='BESTARD', xcn_9='018')
        pv1.patient_type = CWE(cwe_1='A')
        pv1.visit_number = CX(cx_1='2012796641', cx_4='20')
        pv1.admit_date_time = '20251007185900000'
        pv1.discharge_date_time = '20251007185900000'

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1

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
    """ Based on live/es/es-diraya.md, message no. 13
    """

    maxDiff = None

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
    """ Based on live/es/es-diraya.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='81')
        msh.sending_facility = HD(hd_1='01')
        msh.receiving_application = HD(hd_1='11')
        msh.receiving_facility = HD(hd_1='01')
        msh.date_time_of_message = '20250703101935'
        msh.message_type = MSG(msg_1='QBP', msg_2='Q22')
        msh.message_control_id = 'ID2025070310193500'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'AL'
        msh.country_code = 'ESP'
        msh.character_set = 'UNICODE UTF-8'
        msh.msh_19 = ''

        # .. build QPD ..
        qpd = QPD()
        qpd.message_query_name = CWE(cwe_1='1', cwe_2='IHE PDQ Query', cwe_3='HL70471')
        qpd.query_tag = '12'
        qpd.qpd_3 = 'CIPAUT^numCIPAUT'
        qpd.qpd_4 = ''

        # .. build RCP ..
        rcp = RCP()
        rcp.query_priority = 'I'
        rcp.quantity_limited_request = CQ(cq_1='20', cq_2='RD&Recods&HL70126')
        rcp.rcp_3 = ''

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
    """ Based on live/es/es-diraya.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='11')
        msh.sending_facility = HD(hd_1='01')
        msh.receiving_application = HD(hd_1='81')
        msh.receiving_facility = HD(hd_1='01')
        msh.date_time_of_message = '20250703101935'
        msh.message_type = MSG(msg_1='RSP', msg_2='K22')
        msh.message_control_id = 'ID20250912134401'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'NE'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = 'UNICODE UTF-8'

        # .. build MSA ..
        msa = MSA()
        msa.acknowledgment_code = 'AA'
        msa.message_control_id = 'ID2025070310193500'

        # .. build ERR ..
        err = ERR()
        err.hl7_error_code = CWE(cwe_1='0', cwe_2='Message accepted', cwe_3='HL70357', cwe_4='0', cwe_5='Procesado correctamente', cwe_6='TES_ERROR')
        err.severity = 'I'

        # .. build QAK ..
        qak = QAK()
        qak.query_tag = 'ID2025070310193500'
        qak.query_response_status = 'OK'

        # .. build QPD ..
        qpd = QPD()
        qpd.message_query_name = CWE(cwe_1='1', cwe_2='IHE PDQ Query', cwe_3='HL70471')
        qpd.query_tag = 'ID2025070310193500'
        qpd.qpd_3 = 'CIPAUT^numCIPAUT'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='numCIPAUT', cx_4='001'),
            CX(cx_1='numNHCHSLL', cx_4='004'),
            CX(cx_1='numCIP', cx_4='013'),
            CX(cx_1='numDNT', cx_4='014'),
        ]
        pid.patient_name = XPN(xpn_1='CANO', xpn_2='ADRIANA', xpn_3='SALAZAR')
        pid.date_time_of_birth = 'NAI'
        pid.administrative_sex = CWE(cwe_1='SEX')
        pid.patient_address = XAD(xad_5='CPOSTAL')
        pid.patient_death_indicator = 'N'

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
    """ Based on live/es/es-diraya.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PROSOLV')
        msh.sending_facility = HD(hd_1='XYZHOSPITAL')
        msh.receiving_application = HD(hd_1='SYSTEM')
        msh.receiving_facility = HD(hd_1='XYZHOSPITAL')
        msh.date_time_of_message = '20260131160038'
        msh.security = 'P'
        msh.message_type = MSG(msg_1='MDM', msg_2='T02')
        msh.message_control_id = 'PS1-20260131160038'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'T10'
        evn.recorded_date_time = '20260131160038'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.pid_2 = '876543210'
        pid.patient_identifier_list = CX(cx_1='876543210')
        pid.patient_name = XPN(xpn_1='PAREDES', xpn_2='VICTORIA')
        pid.date_time_of_birth = '19780415'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_account_number = CX(cx_1='20000002')
        pid.pid_19 = '222-33-4444'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='CCU', pl_2='2000', pl_3='1')
        pv1.prior_patient_location = PL(pl_1='CCU', pl_2='2003', pl_3='1')
        pv1.attending_doctor = XCN(xcn_1='2345', xcn_2='PAREJO', xcn_3='FELIX')
        pv1.referring_doctor = XCN(xcn_1='9100', xcn_2='CARRION', xcn_3='LUCIA')
        pv1.consulting_doctor = XCN(xcn_1='9999', xcn_2='ALONSO', xcn_3='ARMANDO')
        pv1.visit_number = CX(cx_1='20000002')

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'SC'
        orc.placer_order_number = EI(ei_1='00023456')
        orc.filler_order_number = EI(ei_1='2-1')

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='00023456')
        obr.filler_order_number = EI(ei_1='2-1')
        obr.universal_service_identifier = CWE(cwe_1='02585', cwe_2='TransthoracicEcho', cwe_3='PCV4')
        obr.observation_date_time = '20260131155500'
        obr.results_rpt_status_chng_date_time = '20260131160038'
        obr.result_status = 'F'
        obr.reason_for_study = [CWE(cwe_1='796.4', cwe_3='I9M'), CWE(cwe_1='786.09', cwe_3='I9M'), CWE(cwe_1='414.8', cwe_3='I9M')]
        obr.obr_35 = '65432^PAREJO^FELIX^'

        # .. build the COMMON_ORDER group ..
        common_order = MdmT02CommonOrder()
        common_order.orc = orc
        common_order.obr = obr

        # .. build TXA ..
        txa = TXA()
        txa.set_id_txa = '1'
        txa.document_type = CWE(cwe_1='DI')
        txa.document_content_presentation = 'TX'
        txa.activity_date_time = '20260131155500'
        txa.origination_date_time = '20260131160038'
        txa.originator_code_name = XCN(xcn_1='FelixParejo')
        txa.unique_document_number = EI(ei_1='1.2.840.317.5947431.51.20260131160038')
        txa.parent_document_number = EI(ei_1='1.2.840.317.5947431.51.20260131155715')
        txa.placer_order_number = EI(ei_1='00023456')
        txa.filler_order_number = EI(ei_1='2-1')
        txa.document_completion_status = 'AU'
        txa.authentication_person_time_stamp_set = PPN(ppn_1='65432', ppn_2='PAREJO', ppn_3='FELIX', ppn_15='20260131160038')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'HD'
        obx.observation_identifier = CWE(cwe_1='113014', cwe_2='DICOM Study', cwe_3='DCM')
        obx.obx_5 = '1.2.840.317.5947431.51'
        obx.observation_result_status = 'O'

        # .. build the OBSERVATION group ..
        observation = MdmT02Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='02585', cwe_2='TransthoracicEcho', cwe_3='PCV4')
        obx_2.obx_5 = (
            '^Application^PDF^Base64^'
            'JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNjEyIDc5Ml0KPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovQ29udGVudHMgNCAwIFIKL1Jlc291cmNlcyA8PAovRm9u'
            'dCA8PAovRjEgNSAwIFIKPj4KPj4KPj4KZW5kb2JqCjQgMCBvYmoKPDwKL0xlbmd0aCA0NAo+PgpzdHJlYW0KQlQKL0YxIDE4IFRmCjEwMCA3MDAgVGQKKEluZm9ybWUgQ2xpbmljbykg'
            'VGoKRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqCjw8Ci9UeXBlIC9Gb250Ci9TdWJ0eXBlIC9UeXBlMQovQmFzZUZvbnQgL0hlbHZldGljYQo+PgplbmRvYmoKeHJlZgowIDYKMDAw'
            'MDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNTggMDAwMDAgbiAKMDAwMDAwMDE1MyAwMDAwMCBuIAowMDAwMDAwMzEyIDAwMDAwIG4gCjAwMDAwMDA0'
            'MDYgMDAwMDAgbiAKdHJhaWxlcgo8PAovU2l6ZSA2Ci9Sb290IDEgMCBSCj4+CnN0YXJ0eHJlZgo0ODkKJSVFT0YK'
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
        msg.common_order = common_order
        msg.txa = txa
        msg.observation = [observation, observation_2]

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
    """ Based on live/es/es-diraya.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='VENDOR')
        msh.date_time_of_message = '20241017125335'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = '1'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.msh_13 = ''

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='304032')
        pid.patient_name = XPN(xpn_1='SORIA', xpn_2='DOLORES', xpn_5='')
        pid.date_time_of_birth = '19770919'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_account_number = CX(cx_1='200002')
        pid.pid_19 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='X')
        pv1.hospital_service = CWE(cwe_1='GI6')
        pv1.visit_number = CX(cx_1='200002')
        pv1.pv1_20 = ''

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
        orc.filler_order_number = EI(ei_1='21')
        orc.order_status = 'SC'
        orc.orc_7 = '1'
        orc.orc_18 = ''

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.filler_order_number = EI(ei_1='21')
        obr.universal_service_identifier = CWE(cwe_1='21', cwe_2='VENDOR IMAGES')
        obr.observation_date_time = '20241017123056'
        obr.obr_16 = '2002^GINECOLOGIA^MEDICO'
        obr.filler_field_2 = 'Y'
        obr.result_status = 'F'
        obr.obr_27 = '1'
        obr.obr_28 = ''

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ED'
        obx.observation_identifier = CWE(cwe_1='200002')
        obx.observation_sub_id = OG(og_1='ch1_image_001.bmp')
        obx.obx_5 = (
            '^^BMP^Base64^'
            'Qk0eEAAAAAAAAD4AAAAoAAAAQAAAAEAAAAABAAEAAAAAAOAPAAAAAAAAAAAAAAAAAgAAAAIAAAAAAAAA////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA='
        )
        obx.units = CWE(cwe_1='BMP')
        obx.observation_result_status = 'F'
        obx.obx_12 = ''

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='200002')
        obx_2.observation_sub_id = OG(og_1='ch1_image_003.bmp')
        obx_2.obx_5 = '^^BMP^Base64^Qk0eEAAAAAAAAD4AAAAoAAAAQAAAAEAAAAABAAEAAAAAAOAPAAAAAAAAAAAAAAAAAgAAAAIAAAAAAAAA////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        obx_2.units = CWE(cwe_1='BMP')
        obx_2.observation_result_status = 'F'
        obx_2.obx_12 = ''

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
    """ Based on live/es/es-diraya.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HIS')
        msh.sending_facility = HD(hd_1='HOSPITAL')
        msh.receiving_application = HD(hd_1='FARMACIA')
        msh.receiving_facility = HD(hd_1='EXTERNO')
        msh.date_time_of_message = '20250520101500'
        msh.message_type = MSG(msg_1='RDE', msg_2='O11', msg_3='RDE_O11')
        msh.message_control_id = '87654321'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'NE'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [
            CX(cx_1='71489233X', cx_4='HIS', cx_5='PI', cx_9='2828&&'),
            CX(cx_1='SHJD410901922035', cx_4='MS', cx_5='HC', cx_9='ESP&&ISO3166'),
        ]
        pid.patient_name = XPN(xpn_1='LEON', xpn_2='ROCIO')
        pid.mothers_maiden_name = XPN(xpn_1='VEGA')
        pid.date_time_of_birth = '19880922'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(
            xad_1='CL&SIERPES&14',
            xad_2='CENTRO SALUD',
            xad_3='41004',
            xad_4='41',
            xad_5='41091',
            xad_6='ESP',
            xad_7='H',
            xad_8='SEVILLA',
        )

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_3='405C', pl_4='')
        pv1.attending_doctor = XCN(xcn_1='777', xcn_2='BERMUDEZ', xcn_3='CARLOS', xcn_4='DE LUNA', xcn_8='')
        pv1.hospital_service = CWE(cwe_1='MIN')
        pv1.visit_number = CX(cx_1='82345', cx_6='')

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
        orc.placer_order_number = EI(ei_1='RX002345')
        orc.filler_order_number = EI(ei_1='RX002345')
        orc.date_time_of_order_event = '20250520101500'
        orc.orc_10 = 'BERMUDEZ, CARLOS'
        orc.orc_12 = '777^BERMUDEZ^CARLOS^DE LUNA'

        # .. build RXE ..
        rxe = RXE()
        rxe.rxe_1 = '1^^^20250520101500^^1'
        rxe.give_code = CWE(cwe_1='PARACETAMOL 1G', cwe_3='L')
        rxe.give_amount_minimum = '1'
        rxe.give_units = CWE(cwe_1='COMPRIMIDO')
        rxe.give_dosage_form = CWE(cwe_1='ORAL')
        rxe.rxe_28 = ''

        # .. build TQ1 ..
        tq1 = TQ1()
        tq1.set_id_tq1 = '1'
        tq1.repeat_pattern = RPT(rpt_1='1', rpt_2='TAB', rpt_3='D8H')
        tq1.service_duration = CQ(cq_1='20250520')
        tq1.start_datetime = '20250527'
        tq1.tq1_8 = ''

        # .. build the TIMING_ENCODED group ..
        timing_encoded = RdeO11TimingEncoded()
        timing_encoded.tq1 = tq1

        # .. build RXR ..
        rxr = RXR()
        rxr.route = CWE(cwe_1='PO', cwe_2='Oral', cwe_3='HL70162')

        # .. build the ORDER group ..
        order = RdeO11Order()
        order.orc = orc
        order.rxe = rxe
        order.timing_encoded = timing_encoded
        order.rxr = rxr

        # .. assemble the full message ..
        msg = RDE_O11()
        msg.msh = msh
        msg.patient = patient
        msg.order = order

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
    """ Based on live/es/es-diraya.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='CITACION')
        msh.sending_facility = HD(hd_1='SACYL')
        msh.receiving_application = HD(hd_1='ESTACION')
        msh.receiving_facility = HD(hd_1='SACYL')
        msh.date_time_of_message = '20250215093000'
        msh.message_type = MSG(msg_1='SIU', msg_2='S12', msg_3='SIU_S12')
        msh.message_control_id = 'MSG20250215093000'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'

        # .. build SCH ..
        sch = SCH()
        sch.placer_appointment_id = EI(ei_1='SOL001', ei_2='ESTACION')
        sch.filler_appointment_id = EI(ei_1='CIT001', ei_2='CITACION')
        sch.appointment_reason = CWE(cwe_1='NORMAL', cwe_2='Primera Visita', cwe_3='HL70277')
        sch.sch_11 = '20250301090000'
        sch.placer_contact_person = XCN(xcn_1='15')
        sch.sch_13 = '2^Preferente'
        sch.filler_contact_address = XAD(xad_1='2345', xad_2='GIMENEZ', xad_3='MANUELA', xad_4='REYES', xad_9='018')
        sch.entered_by_location = PL(pl_1='SOLCIT', pl_2='SOLICITUD DE CITA', pl_3='99CTRS')

        # .. build TQ1 ..
        tq1 = TQ1()
        tq1.set_id_tq1 = '1'
        tq1.relative_time_and_units = CQ(cq_1='20250301090000')
        tq1.service_duration = CQ(cq_1='20250301091500')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='23456789', cx_4='SACYL', cx_5='PI'), CX(cx_1='87654321B', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166')]
        pid.patient_name = XPN(xpn_1='FUENTES', xpn_2='LEANDRO')
        pid.mothers_maiden_name = XPN(xpn_1='PADILLA')
        pid.date_time_of_birth = '19700508'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='CL&MAYOR&15', xad_2='2B', xad_3='470001', xad_4='47', xad_5='47001', xad_6='ESP', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.temporary_location = PL(pl_1='TRAU')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='M17.1', cwe_2='Gonartrosis primaria, unilateral', cwe_3='I10')
        dg1.diagnosis_date_time = '20250201'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the PATIENT group ..
        patient = SiuS12Patient()
        patient.pid = pid
        patient.pv1 = pv1
        patient.dg1 = dg1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='28636-9', cwe_2='PRIMERA VISITA', cwe_3='LN')

        # .. build the SERVICE group ..
        service = SiuS12Service()
        service.ais = ais

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.location_resource_id = PL(pl_1='CSLT05', pl_2='Consulta 5', pl_3='99UBISACYL')

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SiuS12LocationResource()
        location_resource.ail = ail

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.personnel_resource_id = XCN(xcn_1='2345', xcn_2='GIMENEZ', xcn_3='MANUELA', xcn_4='REYES', xcn_9='018')

        # .. build the PERSONNEL_RESOURCE group ..
        personnel_resource = SiuS12PersonnelResource()
        personnel_resource.aip = aip

        # .. build the RESOURCES group ..
        resources = SiuS12Resources()
        resources.rgs = rgs
        resources.service = service
        resources.location_resource = location_resource
        resources.personnel_resource = personnel_resource

        # .. assemble the full message ..
        msg = SIU_S12()
        msg.msh = msh
        msg.sch = sch
        msg.tq1 = tq1
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
    """ Based on live/es/es-diraya.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GESLIE')
        msh.sending_facility = HD(hd_1='SACYL')
        msh.receiving_application = HD(hd_1='ESTACION')
        msh.receiving_facility = HD(hd_1='SACYL')
        msh.date_time_of_message = '20250118160000'
        msh.message_type = MSG(msg_1='SIU', msg_2='Z12', msg_3='SRM_S01')
        msh.message_control_id = 'MSG20250118160000'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.accept_acknowledgment = 'AL'
        msh.application_acknowledgment_type = 'ER'

        # .. build ARQ ..
        arq = ARQ()
        arq.placer_appointment_id = EI(ei_1='LE2025001', ei_2='GESLIE')
        arq.appointment_duration = 'LEQ^Lista Espera Quirurgica^HL70277'
        arq.priority_arq = '20250118160000'
        arq.arq_16 = '6789^ACOSTA^VICENTE^SALINAS^^^^^018'
        arq.entered_by_person = XCN(xcn_1='6789', xcn_2='ACOSTA', xcn_3='VICENTE', xcn_4='SALINAS', xcn_9='018')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='76543210', cx_4='SACYL', cx_5='PI'), CX(cx_1='23456789C', cx_4='MI', cx_5='NNESP', cx_9='ESP&&ISO3166')]
        pid.patient_name = XPN(xpn_1='GALVEZ', xpn_2='EMILIA')
        pid.mothers_maiden_name = XPN(xpn_1='MENDEZ')
        pid.date_time_of_birth = '19780921'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='AV&LIBERTAD&22', xad_2='3C', xad_3='090001', xad_4='09', xad_5='09003', xad_6='ESP', xad_7='H')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='UCIR', pl_2='H201', pl_3='C03', pl_4='HGBU')
        pv1.temporary_location = PL(pl_1='TRAU')
        pv1.ambulatory_status = CWE(cwe_1='TURG')

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='S72.0', cwe_2='Fractura del cuello del fémur', cwe_3='I10')
        dg1.diagnosis_date_time = '20250115'
        dg1.diagnosis_type = CWE(cwe_1='A')

        # .. build the PATIENT group ..
        patient = SrmS01Patient()
        patient.pid = pid
        patient.pv1 = pv1
        patient.dg1 = dg1

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.universal_service_identifier = CWE(cwe_1='81.51', cwe_2='Recambio total de cadera', cwe_3='99CIE9MC')

        # .. build the SERVICE group ..
        service = SrmS01Service()
        service.ais = ais

        # .. build the RESOURCES group ..
        resources = SrmS01Resources()
        resources.rgs = rgs
        resources.service = service

        # .. assemble the full message ..
        msg = SRM_S01()
        msg.msh = msh
        msg.arq = arq
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
