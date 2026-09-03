# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7.mappings import get_conversion_warnings

# Local
from conftest import convert, one_resource, resources_of_type

# ################################################################################################################################
# ################################################################################################################################

# A minimal envelope every segment test builds on.
MSH = 'MSH|^~\\&|SENDAPP|SENDFAC|RECVAPP|RECVFAC|20240517143055||ADT^A01|MSG00001|P|2.5'
PID = 'PID|1||12345^^^MYHOSP^MR||Smith^John^Q|||M'
PV1 = 'PV1|1|I|WARD1^101^A^GENHOSP|||||||MED|||||||||VN123^^^MYHOSP'

# ################################################################################################################################
# ################################################################################################################################

class TestPV1:
    """ PV1 segments become Encounter resources.
    """

    def test_encounter_core_fields(self) -> 'None':
        bundle = convert(MSH, PID, PV1)
        encounter = one_resource(bundle, 'Encounter')

        # Patient class I is inpatient, mapping to IMP and in-progress.
        encounter_class = encounter['class']

        assert encounter_class['code'] == 'IMP'
        assert encounter['status'] == 'in-progress'

        identifiers = encounter['identifier']
        visit_identifier = identifiers[0]

        assert visit_identifier['value'] == 'VN123'

        subject = encounter['subject']
        subject_url = subject['reference']

        assert subject_url.startswith('urn:uuid:')

# ################################################################################################################################

    def test_location_resource(self) -> 'None':
        bundle = convert(MSH, PID, PV1)

        # The facility, point of care, room and bed become a hierarchy, each part of the one before it.
        facility, point_of_care, room, bed = resources_of_type(bundle, 'Location')

        assert facility['name'] == 'GENHOSP'
        assert facility['physicalType']['coding'][0]['code'] == 'si'
        assert 'partOf' not in facility

        assert point_of_care['name'] == 'WARD1'
        assert 'physicalType' not in point_of_care

        assert room['name'] == '101'
        assert room['physicalType']['coding'][0]['code'] == 'ro'

        assert bed['name'] == 'A'
        assert bed['physicalType']['coding'][0]['code'] == 'bd'

        for location in (facility, point_of_care, room, bed):
            assert location['mode'] == 'instance'

        # The encounter takes place in the most granular one, the bed.
        encounter = one_resource(bundle, 'Encounter')

        locations = encounter['location']
        first_location = locations[0]
        location_reference = first_location['location']
        location_url = location_reference['reference']

        assert location_url.startswith('urn:uuid:')

        bundle_dict = bundle.to_dict()
        bed_url = None

        for entry in bundle_dict['entry']:
            resource = entry['resource']
            if resource['resourceType'] == 'Location':
                if resource['name'] == 'A':
                    bed_url = entry['fullUrl']

        assert location_url == bed_url
        assert bed['partOf']['reference'] != bed_url

# ################################################################################################################################

    def test_location_facility_universal_id(self) -> 'None':
        # The facility is an HD - its namespace is the name and its universal ID an identifier.
        pv1 = 'PV1|1|O|^^^0105&North Clinic'

        bundle = convert(MSH, PID, pv1)
        location = one_resource(bundle, 'Location')

        assert location['name'] == '0105'

        identifiers = location['identifier']
        identifier = identifiers[0]

        assert identifier['value'] == 'North Clinic'

# ################################################################################################################################

    def test_location_description(self) -> 'None':
        # PL-9 spells out what the location is.
        pv1 = 'PV1|1|O|^12^^^^^^^West Wing Clinic'

        bundle = convert(MSH, PID, pv1)
        location = one_resource(bundle, 'Location')

        assert location['name'] == '12'
        assert location['description'] == 'West Wing Clinic'

# ################################################################################################################################

    def test_attending_doctor_becomes_practitioner(self) -> 'None':
        pv1 = 'PV1|1|O|||||1234^Welby^Marcus^^^Dr'

        bundle = convert(MSH, PID, pv1)
        practitioner = one_resource(bundle, 'Practitioner')

        practitioner_identifiers = practitioner['identifier']
        practitioner_identifier = practitioner_identifiers[0]

        assert practitioner_identifier['value'] == '1234'

        practitioner_names = practitioner['name']
        practitioner_name = practitioner_names[0]

        assert practitioner_name['family'] == 'Welby'

        encounter = one_resource(bundle, 'Encounter')

        participants = encounter['participant']
        participant = participants[0]
        participant_types = participant['type']
        participant_type = participant_types[0]
        type_codings = participant_type['coding']
        type_coding = type_codings[0]

        assert type_coding['code'] == 'ATND'

# ################################################################################################################################

    def test_discharge_makes_encounter_finished(self) -> 'None':
        pv1 = 'PV1|1|I|||||||||||||||||VN1|||||||||||||||||||||||||20240501100000|20240503150000'

        bundle = convert(MSH, PID, pv1)
        encounter = one_resource(bundle, 'Encounter')

        assert encounter['status'] == 'finished'
        assert encounter['period'] == {'start': '2024-05-01T10:00:00+00:00', 'end': '2024-05-03T15:00:00+00:00'}

# ################################################################################################################################

    def test_pv2_admit_reason(self) -> 'None':
        pv2 = 'PV2|||Routine checkup'

        bundle = convert(MSH, PID, PV1, pv2)
        encounter = one_resource(bundle, 'Encounter')

        reason_codes = encounter['reasonCode']
        reason = reason_codes[0]

        assert reason['text'] == 'Routine checkup'

# ################################################################################################################################
# ################################################################################################################################

class TestROL:
    """ ROL segments become Encounter participants.
    """

    def test_rol_before_pv1(self) -> 'None':
        # IHE PAM places ROL between PID and PV1 - it still becomes an Encounter participant.
        rol = 'ROL||AD|FHCP|7777^Morris^Philip'

        bundle = convert(MSH, PID, rol, PV1)

        encounter = one_resource(bundle, 'Encounter')
        practitioner = one_resource(bundle, 'Practitioner')

        practitioner_names = practitioner['name']
        practitioner_name = practitioner_names[0]

        assert practitioner_name['family'] == 'Morris'

        participants = encounter['participant']
        participant = participants[0]

        participant_types = participant['type']
        participant_type = participant_types[0]
        type_codings = participant_type['coding']
        type_coding = type_codings[0]

        assert type_coding['code'] == 'FHCP'

# ################################################################################################################################
# ################################################################################################################################

class TestZBE:
    """ ZBE - the IHE PAM movement segment - enriches the Encounter its PV1 produced.
    """

    def test_movement_id_becomes_encounter_identifier(self) -> 'None':
        zbe = 'ZBE|MOV001^SENDFAC^1.2.250.1.213.1.1.9^ISO|20240517143000||INSERT|N'

        bundle = convert(MSH, PID, PV1, zbe)
        encounter = one_resource(bundle, 'Encounter')

        identifiers = encounter['identifier']
        movement = identifiers[-1]

        assert movement == {'value': 'MOV001', 'system': 'urn:oid:1.2.250.1.213.1.1.9'}

# ################################################################################################################################

    def test_repeating_movement_ids(self) -> 'None':
        zbe = 'ZBE|MOV001^HOSPA~MOV002^HOSPB|20240517143000||UPDATE|N|A01'

        bundle = convert(MSH, PID, PV1, zbe)
        encounter = one_resource(bundle, 'Encounter')

        identifiers = encounter['identifier']
        first = identifiers[-2]
        second = identifiers[-1]

        assert first == {'value': 'MOV001', 'system': 'urn:zato:hl7v2:authority:HOSPA'}
        assert second == {'value': 'MOV002', 'system': 'urn:zato:hl7v2:authority:HOSPB'}

# ################################################################################################################################

    def test_movement_details_are_preserved_on_the_encounter(self) -> 'None':
        zbe = 'ZBE|MOV001^SENDFAC|20240517143000|20240518090000|INSERT|N|A01' + \
            '|Cardiologie^^^^^^UF^^^CARD1|Cardiologie soins^^^^^^UF^^^CARD2|S^Changement de responsabilite'

        bundle = convert(MSH, PID, PV1, zbe)
        encounter = one_resource(bundle, 'Encounter')

        extensions = encounter['extension']
        preserved = {}

        for extension in extensions:
            preserved[extension['url']] = extension['valueString']

        assert preserved['urn:zato:hl7v2:extension/unmapped/ZBE-2'] == '20240517143000'
        assert preserved['urn:zato:hl7v2:extension/unmapped/ZBE-3'] == '20240518090000'
        assert preserved['urn:zato:hl7v2:extension/unmapped/ZBE-4'] == 'INSERT'
        assert preserved['urn:zato:hl7v2:extension/unmapped/ZBE-5'] == 'N'
        assert preserved['urn:zato:hl7v2:extension/unmapped/ZBE-6'] == 'A01'
        assert preserved['urn:zato:hl7v2:extension/unmapped/ZBE-7'] == 'Cardiologie^^^^^^UF^^^CARD1'
        assert preserved['urn:zato:hl7v2:extension/unmapped/ZBE-8'] == 'Cardiologie soins^^^^^^UF^^^CARD2'
        assert preserved['urn:zato:hl7v2:extension/unmapped/ZBE-9'] == 'S^Changement de responsabilite'

        warnings = get_conversion_warnings(bundle)
        assert warnings == []

# ################################################################################################################################

    def test_zbe_without_encounter_is_preserved_whole(self) -> 'None':
        zbe = 'ZBE|MOV001^SENDFAC|20240517143000||INSERT|N'

        bundle = convert(MSH, PID, zbe)
        basic = one_resource(bundle, 'Basic')

        codings = basic['code']['coding']
        coding = codings[0]

        assert coding['code'] == 'ZBE'

        warnings = get_conversion_warnings(bundle)
        assert warnings == []

# ################################################################################################################################
# ################################################################################################################################

class TestPamFranceZSegments:
    """ The other IHE PAM France Z-segments stay preserved whole as Basic resources.
    """

    def test_zfd_stays_preserved_whole(self) -> 'None':
        zfd = 'ZFD|20240101|Y|||G'

        bundle = convert(MSH, PID, PV1, zfd)
        basic = one_resource(bundle, 'Basic')

        codings = basic['code']['coding']
        coding = codings[0]

        assert coding['code'] == 'ZFD'

        extensions = basic['extension']
        preserved = {}

        for extension in extensions:
            preserved[extension['url']] = extension['valueString']

        assert preserved['urn:zato:hl7v2:extension/ZFD/1'] == '20240101'
        assert preserved['urn:zato:hl7v2:extension/ZFD/2'] == 'Y'
        assert preserved['urn:zato:hl7v2:extension/ZFD/5'] == 'G'

        warnings = get_conversion_warnings(bundle)
        assert warnings == []

# ################################################################################################################################

    def test_zfv_stays_preserved_whole(self) -> 'None':
        zfv = 'ZFV|20240517143000|R^Retour au domicile'

        bundle = convert(MSH, PID, PV1, zfv)
        basic = one_resource(bundle, 'Basic')

        codings = basic['code']['coding']
        coding = codings[0]

        assert coding['code'] == 'ZFV'

        warnings = get_conversion_warnings(bundle)
        assert warnings == []

# ################################################################################################################################
# ################################################################################################################################
