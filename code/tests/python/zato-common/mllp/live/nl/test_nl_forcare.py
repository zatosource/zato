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
from zato.hl7v2.v2_9.datatypes import CNE, CWE, CX, DR, EI, HD, MOC, MSG, OG, PL, PRL, PT, VID, XAD, XCN, XON, XPN
from zato.hl7v2.v2_9.groups import AdtA01NextOfKin, AdtA01Procedure, OmlO21ObservationRequest, OmlO21Order, OmlO21Patient, OmlO21PatientVisit, \
    OmlO21Specimen, OrmO01Order, OrmO01OrderDetail, OrmO01Patient, OrmO01PatientVisit, OruR01CommonOrder, OruR01Observation, OruR01OrderObservation, \
    OruR01Patient, OruR01PatientObservation, OruR01PatientResult, OruR01Visit, SrmS01GeneralResource, SrmS01LocationResource, SrmS01Patient, \
    SrmS01PersonnelResource, SrmS01Resources, SrmS01Service
from zato.hl7v2.v2_9.messages import ADT_A01, ADT_A02, ADT_A03, OML_O21, ORM_O01, ORU_R01, SRM_S01
from zato.hl7v2.v2_9.segments import AIG, AIL, AIP, AIS, AL1, ARQ, DG1, EVN, MSH, NK1, NTE, OBR, OBX, ORC, PD1, PID, PR1, PV1, PV2, RGS, SPM

# ################################################################################################################################
# ################################################################################################################################

_md_path = md_path_for('nl', 'nl-forcare.md')

# ################################################################################################################################
# ################################################################################################################################

class TestMsg01(unittest.TestCase):
    """ Based on live/nl/nl-forcare.md, message no. 1
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
        pid.patient_name = XPN(xpn_1='van Dijk&van&Dijk', xpn_2='Pieter', xpn_3='Jan', xpn_7='L')
        pid.date_time_of_birth = '20000101'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Keizersgracht 42&Keizersgracht&42', xad_3='Amsterdam', xad_5='1016CS', xad_6='NL', xad_7='H')
        pid.pid_13 = '020-5551234'

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
            'JVBERi0xLjQKMSAwIG9iago8PAovVGl0bGUgKP7/KQovQ3JlYXRvciAo/v8AdwBrAGgAdABtAGwAdABvAHAAZABmACAAMAAuADEAMgAuADIALgAxKQovUHJvZHVjZXIgKP7/AFEAdAAg'
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
    """ Based on live/nl/nl-forcare.md, message no. 2
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
        orc.order_control = 'XO'
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
        obr.universal_service_identifier = CWE(cwe_1='CARCOA001', cwe_2='zorgproductcode', cwe_3='ZORGDOMEIN')
        obr.observation_date_time = '20160324163432+0100'
        obr.relevant_clinical_information = CWE(cwe_1='Mijn toelichting op de bijlagen.')
        obr.obr_16 = '01004567^&&van Leeuwen^Z.Z.^^^^^^VEKTIS'
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
        obx.obx_5 = (
            '^application^msword^Base64^0M8R4KGxGuEAAAAAAAAAAAAAAAAAAAAAPgADAP7/CQAGAAAAAAAAAAAAAAABAAAALgAAAAAAAAAAEAAAMAAAAAEAAAD+////AAAAAC0AAAD///////8='
        )
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
        obx_2.obx_5 = (
            '^image^png^Base64^iVBORw0KGgoAAAANSUhEUgAABJ0AAAOxCAYAAABfedaEAAAACXBIWXMAAC4jAAAuIwF4pT92AAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAA'
        )
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
    """ Based on live/nl/nl-forcare.md, message no. 3
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ZorgDomein')
        msh.receiving_application = HD(hd_1='applicatie')
        msh.receiving_facility = HD(hd_1='faciliteit')
        msh.date_time_of_message = '20160324163440'
        msh.message_type = MSG(msg_1='SRM', msg_2='S01', msg_3='SRM_S01')
        msh.message_control_id = 'g20ce6a9f8ca4f551275'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build ARQ ..
        arq = ARQ()
        arq.placer_appointment_id = EI(ei_1='ZD200046139')
        arq.request_event_reason = CWE(cwe_1='CARHAR', cwe_2='Cardiologie / Hartfalen', cwe_3='99zda')
        arq.appointment_reason = CWE(cwe_1='CARREG001', cwe_2='consult cardioloog', cwe_3='99zda')
        arq.appointment_type = CWE(cwe_1='REG', cwe_2='regulier', cwe_3='99zda')
        arq.requested_start_date_time_range = DR(dr_1='20160329', dr_2='20160428')
        arq.priority_arq = 'R'
        arq.placer_contact_person = XCN(xcn_1='01004567', xcn_2='van Houten', xcn_3='Z.Z.', xcn_9='VEKTIS')
        arq.arq_16 = '015-2222222^^PH~012-2222222^^FX'
        arq.placer_contact_address = XAD(xad_1='Molenweg 12&Molenweg&12', xad_3='Groningen', xad_5='9711GP', xad_6='NL')
        arq.placer_contact_location = PL(pl_4='Huisartsenpraktijk Eikenlaan&01059999', pl_9='locatie Utrecht')
        arq.entered_by_person = XCN(xcn_1='""', xcn_2='het Willemsen', xcn_3='E.F.G.')
        arq.arq_20 = '015-2222222^^PH~012-2222222^^FX'
        arq.entered_by_location = PL(pl_4='Huisartsenpraktijk Eikenlaan&01059999', pl_9='locatie Utrecht')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_4='NLMINBIZA', cx_5='NNNLD'), CX(cx_1='ZD200046139', cx_4='ZorgDomein', cx_5='VN')]
        pid.patient_name = XPN(xpn_1='de Boer&de&Boer', xpn_2='Willem', xpn_3='Hendrik', xpn_7='L')
        pid.date_time_of_birth = '20000101'
        pid.administrative_sex = CWE(cwe_1='U')
        pid.patient_address = XAD(xad_1='Herengracht 200&Herengracht&200', xad_3='Amsterdam', xad_5='1016BS', xad_6='NL', xad_7='M')
        pid.pid_13 = '020-5557890^PRN^PH~06-55554444^ORN^CP'
        pid.identity_unknown_indicator = 'Y'
        pid.identity_reliability_code = CWE(cwe_1='NNNLD')

        # .. build the PATIENT group ..
        patient = SrmS01Patient()
        patient.pid = pid

        # .. build RGS ..
        rgs = RGS()
        rgs.set_id_rgs = '1'
        rgs.segment_action_code = 'U'

        # .. build AIS ..
        ais = AIS()
        ais.set_id_ais = '1'
        ais.segment_action_code = 'U'
        ais.universal_service_identifier = CWE(cwe_2='consult cardioloog')
        ais.start_date_time_offset = '0'
        ais.start_date_time_offset_units = CNE(cne_1='m')
        ais.allow_substitution_code = CWE(cwe_1='No')
        ais.placer_supplemental_service_information = CWE(cwe_2='Patiënt spreekt uitsluitend Frans.')

        # .. build the SERVICE group ..
        service = SrmS01Service()
        service.ais = ais

        # .. build AIG ..
        aig = AIG()
        aig.set_id_aig = '1'
        aig.segment_action_code = 'U'
        aig.resource_id = CWE(cwe_1='CAR', cwe_2='Cardiologie', cwe_3='99zda')
        aig.resource_type = CWE(cwe_1='""')
        aig.start_date_time_offset = '0'
        aig.start_date_time_offset_units = CNE(cne_1='m')
        aig.allow_substitution_code = CWE(cwe_1='No')

        # .. build the GENERAL_RESOURCE group ..
        general_resource = SrmS01GeneralResource()
        general_resource.aig = aig

        # .. build AIL ..
        ail = AIL()
        ail.set_id_ail = '1'
        ail.segment_action_code = 'U'
        ail.location_resource_id = PL(pl_4='01059998&Isala, locatie Zwolle')
        ail.location_type_ail = CWE(cwe_1='""')
        ail.start_date_time_offset = '0'
        ail.start_date_time_offset_units = CNE(cne_1='m')
        ail.allow_substitution_code = CWE(cwe_1='No')

        # .. build the LOCATION_RESOURCE group ..
        location_resource = SrmS01LocationResource()
        location_resource.ail = ail

        # .. build AIP ..
        aip = AIP()
        aip.set_id_aip = '1'
        aip.segment_action_code = 'U'
        aip.personnel_resource_id = XCN(xcn_2='Meijer', xcn_3='Theodora')
        aip.resource_type = CWE(cwe_1='""')
        aip.start_date_time_offset = '0'
        aip.start_date_time_offset_units = CNE(cne_1='m')
        aip.allow_substitution_code = CWE(cwe_1='No')

        # .. build the PERSONNEL_RESOURCE group ..
        personnel_resource = SrmS01PersonnelResource()
        personnel_resource.aip = aip

        # .. build the RESOURCES group ..
        resources = SrmS01Resources()
        resources.rgs = rgs
        resources.service = service
        resources.general_resource = general_resource
        resources.location_resource = location_resource
        resources.personnel_resource = personnel_resource

        # .. assemble the full message ..
        msg = SRM_S01()
        msg.msh = msh
        msg.arq = arq
        msg.patient = patient
        msg.resources = resources

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
    """ Based on live/nl/nl-forcare.md, message no. 4
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
            XPN(xpn_1='van der Meer&&van der Meer', xpn_2='Cornelia', xpn_7='L'),
            XPN(xpn_1='van der Meer&&van der Meer', xpn_2='Cornelia', xpn_7='B'),
        ]
        pid.date_time_of_birth = '19500101'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = [
            XAD(xad_1='Dorpsstraat 8&Dorpsstraat&8', xad_3='Zwolle', xad_5='8011AB', xad_7='M'),
            XAD(xad_1='Dorpsstraat 8&Dorpsstraat&8', xad_3='Zwolle', xad_5='8011AB', xad_7='L'),
        ]
        pid.pid_13 = '038-4567890^PRN^PH~^^^c.vandermeer@kpnmail.nl'
        pid.marital_status = CWE(cwe_1='M')
        pid.birth_place = 'Zwolle'
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
    """ Based on live/nl/nl-forcare.md, message no. 5
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
        pid.patient_identifier_list = [
            CX(cx_1='PATID1234', cx_4='ADT1', cx_5='MR', cx_6='AMPHIA', cx_8='198807010900', cx_9='199912312359'),
            CX(cx_1='283746591', cx_4='NLMINBIZA', cx_5='NNNLD'),
        ]
        pid.pid_5 = 'Mulder&Mulder^Geert^Jan^III^DR^^L^^^199907010900&199912312359^^199907010900^199912312359^PhD^AL'
        pid.mothers_maiden_name = XPN(xpn_1='van Loon')
        pid.date_time_of_birth = '19610615'
        pid.administrative_sex = CWE(cwe_1='M', cwe_2='MALE', cwe_3='HL70001')
        pid.race = CWE(cwe_1='2106-3', cwe_2='WHITE', cwe_3='HL70005')
        pid.pid_11 = 'Marktplein 7^Bus 2^Breda^NB^4811AB^NL^M^^Breda&Breda&HL70289^^^199907010900&199912312359^199907010900^199912312359^^^^^C/O H. MULDER'
        pid.pid_12 = 'Breda'
        pid.pid_13 = '(076) 514-2233^PRN^CP^^31^076^5142233^^^^^^198807010900^199912312359~^NET^Internet^g.mulder@kpnmail.nl'
        pid.pid_14 = '(076)514-2234^WPN^PH^^31^076^5142234^X2301^^^^^198807010900^199912312359'
        pid.primary_language = CWE(cwe_1='cs', cwe_2='Czech', cwe_3='HL70296')
        pid.marital_status = CWE(cwe_1='M', cwe_2='MARRIED', cwe_3='HL70002')
        pid.religion = CWE(cwe_1='AGN', cwe_2='Agnostic', cwe_3='HL70006')
        pid.pid_19 = '444333333'
        pid.pid_20 = '987654^NB^20010715'
        pid.ethnic_group = CWE(cwe_1='H', cwe_2='Hispanic or Latino', cwe_3='HL70189')
        pid.birth_place = 'Prague'
        pid.multiple_birth_indicator = 'Y'
        pid.birth_order = '2'
        pid.citizenship = CWE(cwe_1='CZ', cwe_2='Czech', cwe_3='HL70171')
        pid.patient_death_date_and_time = '19880818'
        pid.patient_death_indicator = 'Y'
        pid.last_update_date_time = '19880818'
        pid.pid_40 = '(076) 514-2235^PRN^PH^^31^076^5142235^^^^^^198807010900^199912312359'

        # .. build PD1 ..
        pd1 = PD1()
        pd1.patient_primary_facility = XON(xon_1='Huisartsenpraktijk Centrum', xon_2='L', xon_6='NPIAA', xon_7='XX', xon_10='123457')
        pd1.pd1_4 = '998874^van Dongen^Johanna^Maria^^DR^^^NPIAA^L^^^NPI^^^^^^19900101^19991231^MD'
        pd1.student_indicator = CWE(cwe_1='N', cwe_2='NOT A STUDENT', cwe_3='HL70231')
        pd1.living_will_code = CWE(cwe_1='Y', cwe_2='YES PATIENT HAS WILL', cwe_3='HL70315')
        pd1.place_of_worship = XON(xon_1='AGNOSTIC HALL')

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='Mulder', xpn_2='Anneke', xpn_3='W')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='SPOUSE', cwe_3='HL70063')
        nk1.nk1_4 = 'Marktplein 7^Bus 2^Breda^NB^4811AB^NL^M^^Breda&Breda&HL70289^^^199907010900&199912312359^199907010900^199912312359'
        nk1.nk1_5 = '(076) 514-2235^PRN^PH^^31^076^5142235^^^^^^198807010900^199912312359'
        nk1.contact_role = CWE(cwe_1='NK', cwe_2='NEXT OF KIN', cwe_3='HL70131')
        nk1.start_date = '19770704'
        nk1.end_date = '19980901'
        nk1.marital_status = CWE(cwe_1='M', cwe_2='MARRIED', cwe_3='HL70002')
        nk1.administrative_sex = CWE(cwe_1='F', cwe_2='FEMALE', cwe_3='HL70001')
        nk1.date_time_of_birth = '19680913'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I', cwe_2='INPATIENT', cwe_3='HL70004')
        pv1.assigned_patient_location = PL(pl_1='12NORTH', pl_2='1211', pl_3='A', pl_4='AMPHIA', pl_7='1956 ADDITION', pl_8='12')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='URGENT', cwe_3='HL0007')
        pv1.preadmit_number = CX(cx_1='pa5543', cx_3='AMPHIA')
        pv1.attending_doctor = XCN(
            xcn_1='004777',
            xcn_2='Bos',
            xcn_3='Adriaan',
            xcn_4='A',
            xcn_5='DR',
            xcn_8='NPIAA',
            xcn_9='L',
            xcn_12='NPI',
            xcn_18='19900101',
            xcn_19='19991231',
            xcn_20='MD',
        )
        pv1.referring_doctor = XCN(
            xcn_1='004778',
            xcn_2='Veldman',
            xcn_3='Saskia',
            xcn_4='A',
            xcn_5='DR',
            xcn_8='NPIAA',
            xcn_9='L',
            xcn_12='NPI',
            xcn_18='19900101',
            xcn_19='19991231',
            xcn_20='MD',
        )
        pv1.consulting_doctor = XCN(
            xcn_1='004799',
            xcn_2='Huisman',
            xcn_3='Floor',
            xcn_4='A',
            xcn_5='DR',
            xcn_8='NPIAA',
            xcn_9='L',
            xcn_12='NPI',
            xcn_18='19900101',
            xcn_19='19991231',
            xcn_20='MD',
        )
        pv1.hospital_service = CWE(cwe_1='SUR', cwe_2='SURGICAL SERVICE', cwe_3='HL70069')
        pv1.re_admission_indicator = CWE(cwe_1='R', cwe_2='READMISSION', cwe_3='HL70093')
        pv1.admit_source = CWE(cwe_1='ADM', cwe_3='HL70023')
        pv1.vip_indicator = CWE(cwe_1='VIP', cwe_2='VIP', cwe_3='HL70099')
        pv1.admitting_doctor = XCN(
            xcn_1='004744',
            xcn_2='Koster',
            xcn_3='Theodora',
            xcn_4='A',
            xcn_5='DR',
            xcn_8='NPIAA',
            xcn_9='L',
            xcn_12='NPI',
            xcn_18='19900101',
            xcn_19='19991231',
            xcn_20='MD',
        )
        pv1.visit_number = CX(cx_1='P1231', cx_4='AMPHIA', cx_5='VN')
        pv1.discharge_disposition = CWE(cwe_1='DEC', cwe_2='DECEASED', cwe_3='HL70112')
        pv1.diet_type = CWE(cwe_1='VEG', cwe_2='VEGETARIAN', cwe_3='HL701114')
        pv1.admit_date_time = '198808161216'
        pv1.discharge_date_time = '198808181126'
        pv1.alternate_visit_id = CX(cx_1='9942', cx_4='GHS', cx_5='VN')
        pv1.pv1_52 = '004744^Kuijpers^Hendrik^A^DR^^^NPIAA^L^^^NPI^^^^^^19900101^19991231^MD'

        # .. build PV2 ..
        pv2 = PV2()
        pv2.actual_length_of_inpatient_stay = '2'
        pv2.visit_description = 'ADMIT TO CARDIAC UNIT'
        pv2.visit_priority_code = CWE(cwe_1='1', cwe_2='EMERGENCY', cwe_3='HL70217')
        pv2.mode_of_arrival_code = CWE(cwe_1='A', cwe_2='AMBULANCE', cwe_3='HL70430')

        # .. build AL1 ..
        al1 = AL1()
        al1.set_id_al1 = '1'
        al1.allergen_type_code = CWE(cwe_1='DA', cwe_2='DRUG ALLERGY', cwe_3='HL70127')
        al1.allergen_code_mnemonic_description = CWE(cwe_1='387458008', cwe_2='ASPIRIN(SUBSTANCE)', cwe_3='SCT')
        al1.allergy_severity_code = CWE(cwe_1='MO', cwe_2='MODERATE', cwe_3='HL70128')
        al1.allergy_reaction_code = 'HIVES'
        al1.al1_6 = '199807011755'

        # .. build AL1 ..
        al1_2 = AL1()
        al1_2.set_id_al1 = '2'
        al1_2.allergen_type_code = CWE(cwe_1='DA', cwe_2='DRUG ALLERGY', cwe_3='HL70127')
        al1_2.allergen_code_mnemonic_description = CWE(cwe_1='373529000', cwe_2='MORPHINE(SUBSTANCE)', cwe_3='SCT')
        al1_2.allergy_severity_code = CWE(cwe_1='MO', cwe_2='MODERATE', cwe_3='HL70128')
        al1_2.allergy_reaction_code = 'DELERIUM'
        al1_2.al1_6 = '199806111225'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='85898001', cwe_2='CARDIOMYOPATHY', cwe_3='SCT')
        dg1.diagnosis_date_time = '19970212'
        dg1.diagnosing_clinician = XCN(
            xcn_1='998874',
            xcn_2='van Dongen',
            xcn_3='Johanna',
            xcn_4='Maria',
            xcn_6='DR',
            xcn_9='NPIAA',
            xcn_10='L',
            xcn_13='NPI',
            xcn_19='19900101',
            xcn_20='19991231',
            xcn_21='MD',
        )
        dg1.attestation_date_time = '19970213'
        dg1.diagnosis_identifier = EI(ei_1='423432', ei_2='GHS')
        dg1.diagnosis_action_code = 'U'

        # .. build PR1 ..
        pr1 = PR1()
        pr1.set_id_pr1 = '1'
        pr1.procedure_code = CNE(cne_1='41976001', cne_2='Cardiac catheterization', cne_3='SCT')
        pr1.procedure_date_time = '198808180701'
        pr1.pr1_8 = '99234^Evers^Elisabeth^Cornelia^^DR^^^NPIAA^L^^^NPI^^^^^^19900101^19991231^MD'
        pr1.pr1_11 = '998874^de Wit^Jacobus^^^DR^^^NPIAA^L^^^NPI^^^^^^19900101^19991231^MD'
        pr1.pr1_12 = '998874^Scholten^Pieter^^^DR^^^NPIAA^L^^^NPI^^^^^^19900101^19991231^MD'
        pr1.procedure_code_modifier = CNE(cne_1='85898001', cne_2='CARDIOMYOPATHY', cne_3='SCT')
        pr1.procedure_identifier = EI(ei_1='123231', ei_2='AMPHIA')

        # .. build the PROCEDURE group ..
        procedure = AdtA01Procedure()
        procedure.pr1 = pr1

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pd1 = pd1
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.pv2 = pv2
        msg.al1 = [al1, al1_2]
        msg.dg1 = dg1
        msg.procedure = procedure

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
    """ Based on live/nl/nl-forcare.md, message no. 6
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='NIST Test Lab APP')
        msh.sending_facility = HD(hd_1='NIST Lab Facility')
        msh.receiving_facility = HD(hd_1='NIST EHR Facility')
        msh.date_time_of_message = '20150926140551'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
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

        # .. build the PATIENT group ..
        patient = OruR01Patient()
        patient.pid = pid

        # .. build ORC ..
        orc = ORC()
        orc.order_control = 'NW'
        orc.placer_order_number = EI(ei_1='ORD448811', ei_2='NIST EHR')
        orc.filler_order_number = EI(ei_1='R-511', ei_2='NIST Lab Filler')
        orc.date_time_of_order_event = '20120628070100'
        orc.orc_12 = '5742200012^Vermeer^Adriaan^^^^^^NPI^L^^^NPI'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD448811', ei_2='NIST EHR')
        obr.filler_order_number = EI(ei_1='R-511', ei_2='NIST Lab Filler')
        obr.universal_service_identifier = CWE(cwe_1='1000', cwe_2='Hepatitis A B C Panel', cwe_3='99USL')
        obr.observation_date_time = '20120628070100'
        obr.obr_16 = '5742200012^Vermeer^Adriaan^^^^^^NPI^L^^^NPI'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(
            cwe_1='22314-9',
            cwe_2='Hepatitis A virus IgM Ab [Presence] in Serum',
            cwe_3='LN',
            cwe_4='HAVM',
            cwe_5='Hepatitis A IgM antibodies (IgM anti-HAV)',
            cwe_6='L',
            cwe_7='2.52',
        )
        obx.obx_5 = '260385009^Negative (qualifier value)^SCT^NEG^NEGATIVE^L^201509USEd^^Negative (qualifier value)'
        obx.reference_range = 'Negative'
        obx.interpretation_codes = CWE(cwe_1='N')
        obx.observation_result_status = 'F'
        obx.date_time_of_the_observation = '20150925'
        obx.date_time_of_the_analysis = '201509261400'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'CWE'
        obx_2.observation_identifier = CWE(
            cwe_1='20575-7',
            cwe_2='Hepatitis A virus Ab [Presence] in Serum',
            cwe_3='LN',
            cwe_4='HAVAB',
            cwe_5='Hepatitis A antibodies (anti-HAV)',
            cwe_6='L',
            cwe_7='2.52',
        )
        obx_2.obx_5 = '260385009^Negative (qualifier value)^SCT^NEG^NEGATIVE^L^201509USEd^^Negative (qualifier value)'
        obx_2.reference_range = 'Negative'
        obx_2.interpretation_codes = CWE(cwe_1='N')
        obx_2.observation_result_status = 'F'
        obx_2.date_time_of_the_observation = '20150925'
        obx_2.date_time_of_the_analysis = '201509261400'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(
            cwe_1='22316-4',
            cwe_2='Hepatitis B virus core Ab [Units/volume] in Serum',
            cwe_3='LN',
            cwe_4='HBcAbQ',
            cwe_5='Hepatitis B core antibodies (anti-HBVc) Quant',
            cwe_6='L',
            cwe_7='2.52',
        )
        obx_3.obx_5 = '0.70'
        obx_3.units = CWE(cwe_1='[IU]/mL', cwe_2='international unit per milliliter', cwe_3='UCUM', cwe_4='IU/ml', cwe_6='L', cwe_7='1.9')
        obx_3.reference_range = '<0.50 IU/mL'
        obx_3.interpretation_codes = CWE(cwe_1='H')
        obx_3.observation_result_status = 'F'
        obx_3.date_time_of_the_observation = '20150925'
        obx_3.date_time_of_the_analysis = '201509261400'

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
    """ Based on live/nl/nl-forcare.md, message no. 7
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='HL7')
        msh.sending_facility = HD(hd_1='CG3_SICU')
        msh.receiving_application = HD(hd_1='CE_CENTRAL')
        msh.receiving_facility = HD(hd_1='GH_CSF')
        msh.date_time_of_message = '20251014154101'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = '20251014154101-639'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = CX(cx_1='100002', cx_4='A', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Hendriks', xpn_3='')
        pid.pid_6 = '^^'
        pid.pid_11 = '^^^^^^^'
        pid.pid_27 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.patient_class = CWE(cwe_1='E')
        pv1.assigned_patient_location = PL(pl_1='G52008')
        pv1.pv1_42 = ''

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
        obr.observation_date_time = '20251014154101'
        obr.obr_27 = '^^^^'
        obr.obr_37 = ''

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'ST'
        obx.observation_identifier = CWE(cwe_1='HR')
        obx.obx_5 = '73'
        obx.units = CWE(cwe_1='/min')
        obx.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='PVC')
        obx_2.obx_5 = '15'
        obx_2.units = CWE(cwe_1='#/min')
        obx_2.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='STI')
        obx_3.obx_5 = '-0.5'
        obx_3.units = CWE(cwe_1='mm')
        obx_3.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'ST'
        obx_4.observation_identifier = CWE(cwe_1='STII')
        obx_4.obx_5 = '0.0'
        obx_4.units = CWE(cwe_1='mm')
        obx_4.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'ST'
        obx_5.observation_identifier = CWE(cwe_1='STIII')
        obx_5.obx_5 = '0.5'
        obx_5.units = CWE(cwe_1='mm')
        obx_5.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'ST'
        obx_6.observation_identifier = CWE(cwe_1='STV1')
        obx_6.obx_5 = '0.0'
        obx_6.units = CWE(cwe_1='mm')
        obx_6.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_6 = OruR01Observation()
        observation_6.obx = obx_6

        # .. build OBX ..
        obx_7 = OBX()
        obx_7.set_id_obx = '7'
        obx_7.value_type = 'ST'
        obx_7.observation_identifier = CWE(cwe_1='STAVR')
        obx_7.obx_5 = '0.2'
        obx_7.units = CWE(cwe_1='mm')
        obx_7.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_7 = OruR01Observation()
        observation_7.obx = obx_7

        # .. build OBX ..
        obx_8 = OBX()
        obx_8.set_id_obx = '8'
        obx_8.value_type = 'ST'
        obx_8.observation_identifier = CWE(cwe_1='STAVL')
        obx_8.obx_5 = '-0.5'
        obx_8.units = CWE(cwe_1='mm')
        obx_8.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_8 = OruR01Observation()
        observation_8.obx = obx_8

        # .. build OBX ..
        obx_9 = OBX()
        obx_9.set_id_obx = '9'
        obx_9.value_type = 'ST'
        obx_9.observation_identifier = CWE(cwe_1='STAVF')
        obx_9.obx_5 = '0.2'
        obx_9.units = CWE(cwe_1='mm')
        obx_9.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_9 = OruR01Observation()
        observation_9.obx = obx_9

        # .. build OBX ..
        obx_10 = OBX()
        obx_10.set_id_obx = '10'
        obx_10.value_type = 'ST'
        obx_10.observation_identifier = CWE(cwe_1='RR')
        obx_10.obx_5 = '15'
        obx_10.units = CWE(cwe_1='breaths/min')
        obx_10.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_10 = OruR01Observation()
        observation_10.obx = obx_10

        # .. build OBX ..
        obx_11 = OBX()
        obx_11.set_id_obx = '11'
        obx_11.value_type = 'ST'
        obx_11.observation_identifier = CWE(cwe_1='CO2EX')
        obx_11.obx_5 = '32'
        obx_11.units = CWE(cwe_1='mm(hg)')
        obx_11.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_11 = OruR01Observation()
        observation_11.obx = obx_11

        # .. build OBX ..
        obx_12 = OBX()
        obx_12.set_id_obx = '12'
        obx_12.value_type = 'ST'
        obx_12.observation_identifier = CWE(cwe_1='CO2IN')
        obx_12.obx_5 = '0'
        obx_12.units = CWE(cwe_1='mm(hg)')
        obx_12.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_12 = OruR01Observation()
        observation_12.obx = obx_12

        # .. build OBX ..
        obx_13 = OBX()
        obx_13.set_id_obx = '13'
        obx_13.value_type = 'ST'
        obx_13.observation_identifier = CWE(cwe_1='CO2RR')
        obx_13.obx_5 = '14'
        obx_13.units = CWE(cwe_1='breaths/min')
        obx_13.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_13 = OruR01Observation()
        observation_13.obx = obx_13

        # .. build OBX ..
        obx_14 = OBX()
        obx_14.set_id_obx = '14'
        obx_14.value_type = 'ST'
        obx_14.observation_identifier = CWE(cwe_1='SPO2R')
        obx_14.obx_5 = '73'
        obx_14.units = CWE(cwe_1='/min')
        obx_14.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_14 = OruR01Observation()
        observation_14.obx = obx_14

        # .. build OBX ..
        obx_15 = OBX()
        obx_15.set_id_obx = '15'
        obx_15.value_type = 'ST'
        obx_15.observation_identifier = CWE(cwe_1='SPO2P')
        obx_15.obx_5 = '99'
        obx_15.units = CWE(cwe_1='%')
        obx_15.observation_result_status = 'R'

        # .. build the OBSERVATION group ..
        observation_15 = OruR01Observation()
        observation_15.obx = obx_15

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
    """ Based on live/nl/nl-forcare.md, message no. 8
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='GLIMS')
        msh.sending_facility = HD(hd_1='UMCG')
        msh.date_time_of_message = '20180315091200'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'MSG20180315001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.msh_14 = ''

        # .. build PID ..
        pid = PID()
        pid.patient_identifier_list = [CX(cx_1='7654321', cx_5='PI'), CX(cx_1='123456782', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='de Vries&&de Vries', xpn_2='Jan', xpn_7='L')
        pid.date_time_of_birth = '19650423'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Keizersgracht 42&Keizersgracht&42', xad_3='Amsterdam', xad_5='1015CS', xad_7='L')
        pid.pid_13 = '020-5551234^PRN^PH'
        pid.identity_reliability_code = CWE(cwe_1='N')
        pid.last_update_date_time = 'N'
        pid.pid_40 = ''

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='POLI')
        pv1.pv1_7 = ''

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
        obr.placer_order_number = EI(ei_1='REQ-98765')
        obr.filler_order_number = EI(ei_1='LAB-2018-4433', ei_2='GLIMS')
        obr.universal_service_identifier = CWE(cwe_1='CBC', cwe_2='Volledig bloedbeeld', cwe_3='L')
        obr.observation_date_time = '20180315080000'
        obr.filler_field_2 = '20180315091200'
        obr.charge_to_practice = MOC(moc_1='LAB')
        obr.diagnostic_serv_sect_id = 'F'
        obr.obr_26 = '^^^^^R'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='718-7', cwe_2='Hemoglobine', cwe_3='LN', cwe_4='HB')
        obx.obx_5 = '8.9'
        obx.units = CWE(cwe_1='mmol/l')
        obx.reference_range = '7.5 - 10.0'
        obx.interpretation_codes = CWE(cwe_1='""')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leucocyten', cwe_3='LN', cwe_4='WBC')
        obx_2.obx_5 = '7.2'
        obx_2.units = CWE(cwe_1='10*9/l')
        obx_2.reference_range = '4.0 - 10.0'
        obx_2.interpretation_codes = CWE(cwe_1='""')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'NM'
        obx_3.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erytrocyten', cwe_3='LN', cwe_4='RBC')
        obx_3.obx_5 = '4.8'
        obx_3.units = CWE(cwe_1='10*12/l')
        obx_3.reference_range = '4.0 - 5.5'
        obx_3.interpretation_codes = CWE(cwe_1='""')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'NM'
        obx_4.observation_identifier = CWE(cwe_1='787-2', cwe_2='MCV', cwe_3='LN', cwe_4='MCV')
        obx_4.obx_5 = '88'
        obx_4.units = CWE(cwe_1='fl')
        obx_4.reference_range = '80 - 100'
        obx_4.interpretation_codes = CWE(cwe_1='""')
        obx_4.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_4 = OruR01Observation()
        observation_4.obx = obx_4

        # .. build OBX ..
        obx_5 = OBX()
        obx_5.set_id_obx = '5'
        obx_5.value_type = 'NM'
        obx_5.observation_identifier = CWE(cwe_1='4544-3', cwe_2='Hematocriet', cwe_3='LN', cwe_4='HCT')
        obx_5.obx_5 = '0.43'
        obx_5.units = CWE(cwe_1='l/l')
        obx_5.reference_range = '0.35 - 0.47'
        obx_5.interpretation_codes = CWE(cwe_1='""')
        obx_5.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_5 = OruR01Observation()
        observation_5.obx = obx_5

        # .. build OBX ..
        obx_6 = OBX()
        obx_6.set_id_obx = '6'
        obx_6.value_type = 'NM'
        obx_6.observation_identifier = CWE(cwe_1='777-3', cwe_2='Trombocyten', cwe_3='LN', cwe_4='PLT')
        obx_6.obx_5 = '245'
        obx_6.units = CWE(cwe_1='10*9/l')
        obx_6.reference_range = '150 - 400'
        obx_6.interpretation_codes = CWE(cwe_1='""')
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
    """ Based on live/nl/nl-forcare.md, message no. 9
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ZIS')
        msh.sending_facility = HD(hd_1='VUMC')
        msh.receiving_application = HD(hd_1='RIS')
        msh.receiving_facility = HD(hd_1='VUMC')
        msh.date_time_of_message = '20190614102300'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'ORM2019061401'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PAT-445566', cx_5='MR'), CX(cx_1='987654321', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Bakker&&Bakker', xpn_2='Pieter', xpn_7='L')
        pid.date_time_of_birth = '19780312'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Prinsengracht 100&Prinsengracht&100', xad_3='Amsterdam', xad_5='1015EA', xad_6='NL', xad_7='L')
        pid.pid_13 = '020-6234567^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='RAD', pl_2='001', pl_4='VUMC')
        pv1.attending_doctor = XCN(xcn_1='123456', xcn_2='Jansen', xcn_3='M.D.', xcn_9='VEKTIS')

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
        orc.placer_order_number = EI(ei_1='ORD-2019-8877')
        orc.date_time_of_order_event = '20190614102300'
        orc.orc_12 = '123456^Jansen^M.D.^^^^^^VEKTIS'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-2019-8877')
        obr.universal_service_identifier = CWE(cwe_1='71020', cwe_2='CT Thorax', cwe_3='CPT')
        obr.observation_date_time = '20190614'
        obr.obr_14 = 'Verdenking longembolie'
        obr.obr_17 = '123456^Jansen^M.D.^^^^^^VEKTIS'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I26.9', cwe_2='Longembolie', cwe_3='ICD10')
        dg1.diagnosis_date_time = '20190614'

        # .. build the ORDER_DETAIL group ..
        order_detail = OrmO01OrderDetail()
        order_detail.obr = obr
        order_detail.dg1 = dg1

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
    """ Based on live/nl/nl-forcare.md, message no. 10
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EPD')
        msh.sending_facility = HD(hd_1='ERASMUSMC')
        msh.receiving_application = HD(hd_1='LIS')
        msh.receiving_facility = HD(hd_1='ERASMUSMC')
        msh.date_time_of_message = '20200901083015'
        msh.message_type = MSG(msg_1='ADT', msg_2='A04')
        msh.message_control_id = 'ADT20200901001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A04'
        evn.recorded_date_time = '20200901083015'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='12345678', cx_5='MR'), CX(cx_1='111222333', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='van der Berg&&van der Berg', xpn_2='Maria', xpn_3='C.', xpn_7='L')
        pid.date_time_of_birth = '19850715'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Laan van Meerdervoort 50&Laan van Meerdervoort&50', xad_3='Den Haag', xad_5='2517AK', xad_6='NL', xad_7='L')
        pid.pid_13 = '070-3456789^PRN^PH~06-12345678^ORN^CP'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='POLI', pl_2='INT', pl_4='ERASMUSMC')
        pv1.attending_doctor = XCN(xcn_1='567890', xcn_2='de Groot', xcn_3='A.B.', xcn_9='VEKTIS')
        pv1.hospital_service = CWE(cwe_1='INT', cwe_2='Interne geneeskunde', cwe_3='L')
        pv1.admitting_doctor = XCN(xcn_1='567890', xcn_2='de Groot', xcn_3='A.B.', xcn_9='VEKTIS')
        pv1.visit_number = CX(cx_1='V-2020-12345', cx_4='ERASMUSMC', cx_5='VN')

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
    """ Based on live/nl/nl-forcare.md, message no. 11
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ZIS')
        msh.sending_facility = HD(hd_1='AMC')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='AMC')
        msh.date_time_of_message = '20210115140030'
        msh.message_type = MSG(msg_1='ADT', msg_2='A08')
        msh.message_control_id = 'ADT20210115002'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A08'
        evn.recorded_date_time = '20210115140030'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='99887766', cx_5='MR'), CX(cx_1='222333444', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Smit&&Smit', xpn_2='Willem', xpn_3='J.', xpn_7='L')
        pid.date_time_of_birth = '19720903'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Herengracht 200&Herengracht&200', xad_3='Amsterdam', xad_5='1016BS', xad_6='NL', xad_7='L')
        pid.pid_13 = '020-7654321^PRN^PH~06-87654321^ORN^CP~^^^w.smit@kpnmail.nl'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='5WEST', pl_2='501', pl_3='A', pl_4='AMC')
        pv1.attending_doctor = XCN(xcn_1='234567', xcn_2='Peters', xcn_3='K.L.', xcn_9='VEKTIS')
        pv1.hospital_service = CWE(cwe_1='CHI', cwe_2='Chirurgie', cwe_3='L')
        pv1.admitting_doctor = XCN(xcn_1='234567', xcn_2='Peters', xcn_3='K.L.', xcn_9='VEKTIS')
        pv1.visit_number = CX(cx_1='B-2021-001', cx_4='AMC', cx_5='VN')

        # .. assemble the full message ..
        msg = ADT_A01()
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
    """ Based on live/nl/nl-forcare.md, message no. 12
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ZIS')
        msh.sending_facility = HD(hd_1='LUMC')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='LUMC')
        msh.date_time_of_message = '20210520160000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A03')
        msh.message_control_id = 'ADT20210520003'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A03'
        evn.recorded_date_time = '20210520160000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='44556677', cx_5='MR'), CX(cx_1='333444555', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Dijkstra&&Dijkstra', xpn_2='Anna', xpn_3='M.', xpn_7='L')
        pid.date_time_of_birth = '19900228'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Breestraat 75&Breestraat&75', xad_3='Leiden', xad_5='2311CH', xad_6='NL', xad_7='L')
        pid.pid_13 = '071-5123456^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='3NORTH', pl_2='302', pl_3='B', pl_4='LUMC')
        pv1.attending_doctor = XCN(xcn_1='345678', xcn_2='van Dijk', xcn_3='R.S.', xcn_9='VEKTIS')
        pv1.hospital_service = CWE(cwe_1='CAR', cwe_2='Cardiologie', cwe_3='L')
        pv1.admitting_doctor = XCN(xcn_1='345678', xcn_2='van Dijk', xcn_3='R.S.', xcn_9='VEKTIS')
        pv1.visit_number = CX(cx_1='B-2021-055', cx_4='LUMC', cx_5='VN')
        pv1.admit_date_time = '20210515100000'
        pv1.discharge_date_time = '20210520160000'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='I50.0', cwe_2='Hartfalen', cwe_3='ICD10')
        dg1.diagnosis_date_time = '20210515'

        # .. assemble the full message ..
        msg = ADT_A03()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.pv1 = pv1
        msg.dg1 = dg1

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
    """ Based on live/nl/nl-forcare.md, message no. 13
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS-A')
        msh.sending_facility = HD(hd_1='LAB-ALPHA')
        msh.receiving_application = HD(hd_1='LIS-B')
        msh.receiving_facility = HD(hd_1='LAB-BETA')
        msh.date_time_of_message = '20180415093000'
        msh.message_type = MSG(msg_1='OML', msg_2='O21', msg_3='OML_O21')
        msh.message_control_id = 'OML201804150001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.country_code = 'NLD'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='LABPAT-001', cx_5='MR'), CX(cx_1='555666777', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Mulder&&Mulder', xpn_2='Kees', xpn_7='L')
        pid.date_time_of_birth = '19551010'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Dorpsstraat 12&Dorpsstraat&12', xad_3='Groningen', xad_5='9711AA', xad_6='NL', xad_7='L')
        pid.pid_13 = '050-3123456^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='POLI')
        pv1.pv1_7 = ''

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
        orc.placer_order_number = EI(ei_1='REQ-LAB-2018-100')
        orc.date_time_of_order_event = '20180415093000'
        orc.orc_12 = '456789^Huisarts^W.^^^^^^VEKTIS'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='REQ-LAB-2018-100')
        obr.universal_service_identifier = CWE(cwe_1='24357-6', cwe_2='Urinalysis macro (dipstick) panel', cwe_3='LN')
        obr.observation_date_time = '20180415'
        obr.parent_result = PRL(prl_1='F')

        # .. build SPM ..
        spm = SPM()
        spm.set_id_spm = '1'
        spm.spm_2 = 'SPM-001^^LAB-ALPHA'
        spm.specimen_type = CWE(cwe_1='UR', cwe_2='Urine', cwe_3='HL70487')
        spm.specimen_received_date_time = '20180415080000'
        spm.specimen_expiration_date_time = '20180415090000'

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
    """ Based on live/nl/nl-forcare.md, message no. 14
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LIS-B')
        msh.sending_facility = HD(hd_1='LAB-BETA')
        msh.receiving_application = HD(hd_1='LIS-A')
        msh.receiving_facility = HD(hd_1='LAB-ALPHA')
        msh.date_time_of_message = '20180420141500'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ORU201804200001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5')
        msh.country_code = 'NLD'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='LABPAT-002', cx_5='MR'), CX(cx_1='666777888', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Visser&&Visser', xpn_2='Henk', xpn_7='L')
        pid.date_time_of_birth = '19680301'
        pid.administrative_sex = CWE(cwe_1='M')

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU')
        pv1.pv1_7 = ''

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
        orc.placer_order_number = EI(ei_1='REQ-LAB-2018-200')
        orc.filler_order_number = EI(ei_1='RES-LAB-2018-200')
        orc.order_status = 'CM'
        orc.date_time_of_order_event = '20180420141500'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='REQ-LAB-2018-200')
        obr.filler_order_number = EI(ei_1='RES-LAB-2018-200')
        obr.universal_service_identifier = CWE(cwe_1='632-0', cwe_2='Bacteria Culture', cwe_3='LN')
        obr.observation_date_time = '20180418'
        obr.filler_field_2 = '20180420141500'
        obr.charge_to_practice = MOC(moc_1='MB')
        obr.diagnostic_serv_sect_id = 'F'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'CWE'
        obx.observation_identifier = CWE(cwe_1='600-7', cwe_2='Bacteria identified', cwe_3='LN')
        obx.obx_5 = '112283007^Escherichia coli^SCT'
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ST'
        obx_2.observation_identifier = CWE(cwe_1='6652-2', cwe_2='Meropenem [Susceptibility] by Minimum inhibitory concentration (MIC)', cwe_3='LN')
        obx_2.obx_5 = '>=16'
        obx_2.units = CWE(cwe_1='mg/L')
        obx_2.interpretation_codes = CWE(cwe_1='R')
        obx_2.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_2 = OruR01Observation()
        observation_2.obx = obx_2

        # .. build OBX ..
        obx_3 = OBX()
        obx_3.set_id_obx = '3'
        obx_3.value_type = 'ST'
        obx_3.observation_identifier = CWE(cwe_1='7029-2', cwe_2='Meropenem [Susceptibility] by Gradient strip', cwe_3='LN')
        obx_3.obx_5 = '8.0'
        obx_3.units = CWE(cwe_1='mg/L')
        obx_3.interpretation_codes = CWE(cwe_1='I')
        obx_3.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation_3 = OruR01Observation()
        observation_3.obx = obx_3

        # .. build OBX ..
        obx_4 = OBX()
        obx_4.set_id_obx = '4'
        obx_4.value_type = 'CWE'
        obx_4.observation_identifier = CWE(cwe_1='18943-1', cwe_2='Meropenem [Susceptibility]', cwe_3='LN')
        obx_4.obx_5 = 'R^Resistant^HL70078'
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
    """ Based on live/nl/nl-forcare.md, message no. 15
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='PATH_SYS')
        msh.sending_facility = HD(hd_1='RADBOUDUMC')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='RADBOUDUMC')
        msh.date_time_of_message = '20220310150000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01', msg_3='ORU_R01')
        msh.message_control_id = 'ORU-PA-2022-001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')
        msh.country_code = 'NLD'
        msh.character_set = 'UNICODE UTF-8'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='PA-12345', cx_5='MR'), CX(cx_1='888999000', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Jansen&&Jansen', xpn_2='Sophie', xpn_7='L')
        pid.date_time_of_birth = '19750620'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Plein 1944 nr 5&Plein 1944&5', xad_3='Nijmegen', xad_5='6511AA', xad_6='NL', xad_7='L')
        pid.pid_13 = '024-3612345^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='PATH')
        pv1.pv1_7 = ''

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
        orc.placer_order_number = EI(ei_1='PA-ORD-2022-100')
        orc.filler_order_number = EI(ei_1='PA-RES-2022-100')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='PA-ORD-2022-100')
        obr.filler_order_number = EI(ei_1='PA-RES-2022-100')
        obr.universal_service_identifier = CWE(cwe_1='11529-5', cwe_2='Surgical pathology study', cwe_3='LN')
        obr.observation_date_time = '20220308'

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'FT'
        obx.observation_identifier = CWE(cwe_1='22638-1', cwe_2='Pathology report', cwe_3='LN')
        obx.obx_5 = (
            'Macroscopie: Huidbiopt linker onderarm, 0.4 cm\\.br\\Microscopie: Basaalcelcarcinoom, nodulair type\\.br\\Snijvlakken vrij\\.br\\Conclusie: BCC '
            'nodulair type, radicaal verwijderd.'
        )
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'ED'
        obx_2.observation_identifier = CWE(cwe_1='PDF', cwe_2='Pathology Report PDF', cwe_3='L')
        obx_2.obx_5 = (
            '^application^pdf^Base64^'
            'JVBERi0xLjcKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEK'
            'L01lZGlhQm94IFswIDAgNTk1IDg0Ml0KPj4KZW5kb2JqCg=='
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
    """ Based on live/nl/nl-forcare.md, message no. 16
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='EMR')
        msh.sending_facility = HD(hd_1='RIJNSTATE')
        msh.receiving_application = HD(hd_1='LAB')
        msh.receiving_facility = HD(hd_1='RIJNSTATE')
        msh.date_time_of_message = '20230915120000'
        msh.message_type = MSG(msg_1='ORM', msg_2='O01')
        msh.message_control_id = 'ORM-2023-001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MR-12345', cx_4='RIJNSTATE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='de Wit', xpn_2='Floor', xpn_3='Johanna')
        pid.date_time_of_birth = '19800101'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Velperweg 26', xad_3='Arnhem', xad_5='6824BJ')
        pid.pid_13 = '026-4456789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='SEH', pl_4='RIJNSTATE')
        pv1.attending_doctor = XCN(xcn_1='1234', xcn_2='Kuijpers', xcn_3='Hendrik', xcn_4='A')
        pv1.hospital_service = CWE(cwe_1='SEH')
        pv1.patient_type = CWE(cwe_1='1234', cwe_2='Kuijpers', cwe_3='Hendrik', cwe_4='A')
        pv1.visit_number = CX(cx_1='SEH')
        pv1.pv1_20 = 'V1234^^^RIJNSTATE^VN'

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
        orc.placer_order_number = EI(ei_1='ORD-5001')
        orc.orc_7 = '^^^20230915120000^^S'
        orc.date_time_of_order_event = '20230915120000'
        orc.orc_12 = '1234^Kuijpers^Hendrik^A'

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-5001')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC panel', cwe_3='LN')
        obr.observation_date_time = '20230915120000'
        obr.obr_15 = '1234^Kuijpers^Hendrik^A'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='R50.9', cwe_2='Fever, unspecified', cwe_3='ICD10')

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
        nte.comment = 'STAT - Patient febrile, suspect infection'

        # .. assemble the full message ..
        msg = ORM_O01()
        msg.msh = msh
        msg.patient = patient
        msg.order = order
        msg.extra_segments = [nte]

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
    """ Based on live/nl/nl-forcare.md, message no. 17
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB')
        msh.sending_facility = HD(hd_1='RIJNSTATE')
        msh.receiving_application = HD(hd_1='EMR')
        msh.receiving_facility = HD(hd_1='RIJNSTATE')
        msh.date_time_of_message = '20230915140000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'ORU-2023-001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.3')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MR-12345', cx_4='RIJNSTATE', cx_5='MR')
        pid.patient_name = XPN(xpn_1='de Wit', xpn_2='Floor', xpn_3='Johanna')
        pid.date_time_of_birth = '19800101'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Velperweg 26', xad_3='Arnhem', xad_5='6824BJ')
        pid.pid_13 = '026-4456789'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='SEH', pl_4='RIJNSTATE')
        pv1.attending_doctor = XCN(xcn_1='1234', xcn_2='Kuijpers', xcn_3='Hendrik', xcn_4='A')

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
        orc.placer_order_number = EI(ei_1='ORD-5001')
        orc.filler_order_number = EI(ei_1='LAB-R-5001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-5001')
        obr.filler_order_number = EI(ei_1='LAB-R-5001')
        obr.universal_service_identifier = CWE(cwe_1='58410-2', cwe_2='CBC panel', cwe_3='LN')
        obr.observation_date_time = '20230915120000'
        obr.obr_16 = '1234^Kuijpers^Hendrik^A'
        obr.charge_to_practice = MOC(moc_1='20230915140000')
        obr.result_status = 'LAB'
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='6690-2', cwe_2='Leukocytes', cwe_3='LN')
        obx.obx_5 = '12.5'
        obx.units = CWE(cwe_1='10*3/uL')
        obx.reference_range = '4.5-11.0'
        obx.interpretation_codes = CWE(cwe_1='H')
        obx.observation_result_status = 'F'

        # .. build the OBSERVATION group ..
        observation = OruR01Observation()
        observation.obx = obx

        # .. build OBX ..
        obx_2 = OBX()
        obx_2.set_id_obx = '2'
        obx_2.value_type = 'NM'
        obx_2.observation_identifier = CWE(cwe_1='789-8', cwe_2='Erythrocytes', cwe_3='LN')
        obx_2.obx_5 = '4.2'
        obx_2.units = CWE(cwe_1='10*6/uL')
        obx_2.reference_range = '3.8-5.2'
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
        obx_3.obx_5 = '13.5'
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
        obx_4.obx_5 = '40.2'
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
        obx_5.obx_5 = '88.5'
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
        obx_6.observation_identifier = CWE(cwe_1='777-3', cwe_2='Platelets', cwe_3='LN')
        obx_6.obx_5 = '225'
        obx_6.units = CWE(cwe_1='10*3/uL')
        obx_6.reference_range = '150-400'
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
    """ Based on live/nl/nl-forcare.md, message no. 18
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ZIS')
        msh.sending_facility = HD(hd_1='UMCU')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='UMCU')
        msh.date_time_of_message = '20220101083000'
        msh.message_type = MSG(msg_1='ADT', msg_2='A01')
        msh.message_control_id = 'ADT20220101001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A01'
        evn.recorded_date_time = '20220101083000'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='55667788', cx_5='MR'), CX(cx_1='444555666', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='de Boer&&de Boer', xpn_2='Frederik', xpn_3='H.', xpn_7='L')
        pid.date_time_of_birth = '19450812'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Oudegracht 150&Oudegracht&150', xad_3='Utrecht', xad_5='3511AX', xad_6='NL', xad_7='L')
        pid.pid_13 = '030-2345678^PRN^PH'

        # .. build NK1 ..
        nk1 = NK1()
        nk1.set_id_nk1 = '1'
        nk1.name = XPN(xpn_1='de Boer', xpn_2='Elisabeth')
        nk1.relationship = CWE(cwe_1='SPO', cwe_2='Echtgenote', cwe_3='HL70063')
        nk1.address = XAD(xad_1='Oudegracht 150&Oudegracht&150', xad_3='Utrecht', xad_5='3511AX', xad_6='NL', xad_7='L')
        nk1.nk1_5 = '030-2345678^PRN^PH'

        # .. build the NEXT_OF_KIN group ..
        next_of_kin = AdtA01NextOfKin()
        next_of_kin.nk1 = nk1

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='6EAST', pl_2='601', pl_3='A', pl_4='UMCU')
        pv1.admission_type = CWE(cwe_1='E', cwe_2='Spoed', cwe_3='HL0007')
        pv1.attending_doctor = XCN(xcn_1='789012', xcn_2='Willemsen', xcn_3='P.Q.', xcn_9='VEKTIS')
        pv1.hospital_service = CWE(cwe_1='LON', cwe_2='Longziekten', cwe_3='L')
        pv1.admitting_doctor = XCN(xcn_1='789012', xcn_2='Willemsen', xcn_3='P.Q.', xcn_9='VEKTIS')
        pv1.visit_number = CX(cx_1='B-2022-001', cx_4='UMCU', cx_5='VN')
        pv1.prior_temporary_location = PL(pl_1='20220101083000')

        # .. build AL1 ..
        al1 = AL1()
        al1.set_id_al1 = '1'
        al1.allergen_type_code = CWE(cwe_1='DA', cwe_2='Geneesmiddellenallergie', cwe_3='HL70127')
        al1.allergen_code_mnemonic_description = CWE(cwe_1='N02BE01', cwe_2='Paracetamol', cwe_3='ATC')
        al1.allergy_severity_code = CWE(cwe_1='MI', cwe_2='Mild', cwe_3='HL70128')
        al1.allergy_reaction_code = 'Huiduitslag'

        # .. build DG1 ..
        dg1 = DG1()
        dg1.set_id_dg1 = '1'
        dg1.diagnosis_code_dg1 = CWE(cwe_1='J18.9', cwe_2='Pneumonie, niet gespecificeerd', cwe_3='ICD10')
        dg1.diagnosis_date_time = '20220101'

        # .. assemble the full message ..
        msg = ADT_A01()
        msg.msh = msh
        msg.evn = evn
        msg.pid = pid
        msg.next_of_kin = next_of_kin
        msg.pv1 = pv1
        msg.al1 = al1
        msg.dg1 = dg1

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
    """ Based on live/nl/nl-forcare.md, message no. 19
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='LAB')
        msh.sending_facility = HD(hd_1='ISALA')
        msh.receiving_application = HD(hd_1='EMR')
        msh.receiving_facility = HD(hd_1='ISALA')
        msh.date_time_of_message = '20230920100000'
        msh.message_type = MSG(msg_1='ORU', msg_2='R01')
        msh.message_control_id = 'ORU-2023-CMP-001'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.5.1')

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = CX(cx_1='MR-67890', cx_4='ISALA', cx_5='MR')
        pid.patient_name = XPN(xpn_1='Bos', xpn_2='Jacobus', xpn_3='Adriaan')
        pid.date_time_of_birth = '19650315'
        pid.administrative_sex = CWE(cwe_1='M')
        pid.patient_address = XAD(xad_1='Grote Voort 33', xad_3='Zwolle', xad_5='8011GE')
        pid.pid_13 = '038-4234567'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='O')
        pv1.assigned_patient_location = PL(pl_1='POLI', pl_4='ISALA')
        pv1.attending_doctor = XCN(xcn_1='5678', xcn_2='van der Heijden', xcn_3='Saskia', xcn_4='B')

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
        orc.placer_order_number = EI(ei_1='ORD-6001')
        orc.filler_order_number = EI(ei_1='LAB-R-6001')
        orc.order_status = 'CM'

        # .. build the COMMON_ORDER group ..
        common_order = OruR01CommonOrder()
        common_order.orc = orc

        # .. build OBR ..
        obr = OBR()
        obr.set_id_obr = '1'
        obr.placer_order_number = EI(ei_1='ORD-6001')
        obr.filler_order_number = EI(ei_1='LAB-R-6001')
        obr.universal_service_identifier = CWE(cwe_1='24323-8', cwe_2='Comprehensive metabolic panel', cwe_3='LN')
        obr.observation_date_time = '20230920080000'
        obr.obr_16 = '5678^van der Heijden^Saskia^B'
        obr.charge_to_practice = MOC(moc_1='20230920100000')
        obr.result_status = 'LAB'
        obr.parent_result = PRL(prl_1='F')

        # .. build OBX ..
        obx = OBX()
        obx.set_id_obx = '1'
        obx.value_type = 'NM'
        obx.observation_identifier = CWE(cwe_1='2345-7', cwe_2='Glucose', cwe_3='LN')
        obx.obx_5 = '95'
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
        obx_2.reference_range = '0.7-1.3'
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
        obx_4.units = CWE(cwe_1='mmol/L')
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
        obx_5.units = CWE(cwe_1='mmol/L')
        obx_5.reference_range = '3.5-5.1'
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
        obx_6.obx_5 = '9.5'
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
        obx_7.obx_5 = '32'
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
    """ Based on live/nl/nl-forcare.md, message no. 20
    """

    maxDiff = None

    def test_build(self) -> 'None':

        # Build MSH ..
        msh = MSH()
        msh.sending_application = HD(hd_1='ZIS')
        msh.sending_facility = HD(hd_1='OLVG')
        msh.receiving_application = HD(hd_1='EPD')
        msh.receiving_facility = HD(hd_1='OLVG')
        msh.date_time_of_message = '20211203111500'
        msh.message_type = MSG(msg_1='ADT', msg_2='A02')
        msh.message_control_id = 'ADT20211203004'
        msh.processing_id = PT(pt_1='P')
        msh.version_id = VID(vid_1='2.4')
        msh.country_code = 'NLD'
        msh.character_set = '8859/1'

        # .. build EVN ..
        evn = EVN()
        evn.evn_1 = 'A02'
        evn.recorded_date_time = '20211203111500'

        # .. build PID ..
        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_identifier_list = [CX(cx_1='33445566', cx_5='MR'), CX(cx_1='777888999', cx_4='NLMINBIZA', cx_5='NNNLD')]
        pid.patient_name = XPN(xpn_1='Hendriks&&Hendriks', xpn_2='Cornelia', xpn_3='A.', xpn_7='L')
        pid.date_time_of_birth = '19581124'
        pid.administrative_sex = CWE(cwe_1='F')
        pid.patient_address = XAD(xad_1='Westerstraat 88&Westerstraat&88', xad_3='Amsterdam', xad_5='1015MN', xad_6='NL', xad_7='L')
        pid.pid_13 = '020-6789012^PRN^PH'

        # .. build PV1 ..
        pv1 = PV1()
        pv1.set_id_pv1 = '1'
        pv1.patient_class = CWE(cwe_1='I')
        pv1.assigned_patient_location = PL(pl_1='ICU', pl_2='101', pl_3='A', pl_4='OLVG')
        pv1.admission_type = CWE(cwe_1='U', cwe_2='Urgent')
        pv1.attending_doctor = XCN(xcn_1='890123', xcn_2='Brouwer', xcn_3='T.M.', xcn_9='VEKTIS')
        pv1.hospital_service = CWE(cwe_1='CAR', cwe_2='Cardiologie', cwe_3='L')
        pv1.admitting_doctor = XCN(xcn_1='890123', xcn_2='Brouwer', xcn_3='T.M.', xcn_9='VEKTIS')
        pv1.visit_number = CX(cx_1='B-2021-234', cx_4='OLVG', cx_5='VN')
        pv1.prior_temporary_location = PL(pl_1='20211201090000')
        pv1.total_adjustments = '3WEST^305^B^OLVG'

        # .. assemble the full message ..
        msg = ADT_A02()
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
