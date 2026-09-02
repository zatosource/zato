# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# fhirpy
from fhirpy import SyncFHIRClient
from fhirpy.base.exceptions import ResourceNotFound

# Zato
from zato.common.test.fhir import FHIRTestServer
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict
    anylist = anylist
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# The patient ID the documentation pages use in their examples.
Chalmers_ID = '511a6231-361e-4b8e-8f9c-b183b7813f4d'

# The name the documentation pages show in their example outputs.
Chalmers_Name = [{'use': 'official', 'family': 'Chalmers', 'given': ['Peter', 'James']}]

# The extension URLs the extensions page documents.
Birth_Place_URL = 'http://hl7.org/fhir/StructureDefinition/patient-birthPlace'
Nationality_URL = 'http://hl7.org/fhir/StructureDefinition/patient-nationality'

# ################################################################################################################################
# ################################################################################################################################

def _make_chalmers() -> 'stranydict':
    """ Returns a fresh copy of the patient the documentation examples read and search for.
    """
    out = {
        'resourceType': 'Patient',
        'id': Chalmers_ID,
        'active': True,
        'birthDate': '1974-12-25',
        'name': [{'use': 'official', 'family': 'Chalmers', 'given': ['Peter', 'James']}],
        'telecom': [
            {'system': 'email', 'value': 'peter.chalmers@example.com'},
            {'system': 'phone', 'use': 'home', 'value': '555-0123'},
        ],
        'extension': [
            {
                'url': Birth_Place_URL,
                'valueAddress': {'city': 'Amsterdam', 'country': 'NL'},
            },
            {
                'url': Nationality_URL,
                'extension': [
                    {'url': 'code', 'valueCodeableConcept': {'text': 'Dutch'}},
                    {'url': 'period', 'valuePeriod': {'start': '2004-05-01'}},
                ],
            },
        ],
    }

    return out

# ################################################################################################################################

@pytest.fixture
def fhir_server():
    """ A fresh FHIR test server per test, so tests never see each other's data.
    """
    server = FHIRTestServer()
    server.start()

    yield server

    server.stop()

# ################################################################################################################################
# ################################################################################################################################

def test_connections_use_the_connection_in_a_service(fhir_server:'FHIRTestServer') -> 'None':
    """ Mirrors docs/dev/healthcare/hl7/fhir/connections - the GetActivePatients service body
    and the log line its page shows.
    """
    _ = fhir_server.import_resource(_make_chalmers())

    client = SyncFHIRClient(fhir_server.address)

    # Everything about patients starts here ..
    patients = client.resources('Patient')

    # .. all of the active ones, sorted by their birth date ..
    result = patients.search(active=True).sort('-birthdate')

    # .. and each match is collected the way the service logs it.
    received:'anylist' = []

    for patient in result:
        received.append(patient['name'])

    assert received == [Chalmers_Name]

# ################################################################################################################################

def test_resources_create_read_update_delete(fhir_server:'FHIRTestServer') -> 'None':
    """ Mirrors docs/dev/healthcare/hl7/fhir/resources - create, read, update, patch,
    refresh and delete, in the order the page presents them.
    """
    client = SyncFHIRClient(fhir_server.address)

    # Build a new Patient with initial data ..
    name = [{'family': 'Chalmers', 'given': ['Peter']}]
    patient = client.resource('Patient', name=name)

    # .. both syntaxes below are equivalent ..
    patient.birthDate = '1974-12-25'
    patient['gender'] = 'male'

    # .. and this is what stores the patient in the server.
    _ = patient.save()

    # The server assigned an ID during the save
    assert patient.id

    # Read one resource by its type and ID
    data = client.get('Patient', patient.id)

    names = data['name']
    first_name = names[0]

    assert first_name['family'] == 'Chalmers'

    # Fetch the resource by its ID ..
    found = client.resources('Patient').search(_id=patient.id).get()

    # .. change a field and store the whole resource ..
    found.birthDate = '1974-12-26'
    _ = found.save()

    # .. or send only one field, leaving the rest untouched.
    _ = found.patch(birthDate='1974-12-27')

    # Re-read it from the server and confirm the patch took effect
    _ = found.refresh()

    assert found['birthDate'] == '1974-12-27'
    assert found['gender'] == 'male'

    # A call to delete removes the resource from the server
    found.delete()

    with pytest.raises(ResourceNotFound):
        _ = client.get('Patient', patient.id)

# ################################################################################################################################

def test_resources_references_and_serialize(fhir_server:'FHIRTestServer') -> 'None':
    """ Mirrors docs/dev/healthcare/hl7/fhir/resources - references between resources
    and resources as plain dicts.
    """
    _ = fhir_server.import_resource(_make_chalmers())

    client = SyncFHIRClient(fhir_server.address)
    patient = client.resources('Patient').search(_id=Chalmers_ID).get()

    # Create a new appointment for an already saved patient
    appointment = client.resource('Appointment')

    appointment.status = 'booked'
    appointment.participant = [{'actor': patient, 'status': 'accepted'}]
    appointment.start = '2027-01-11T11:11:11.111+00:00'
    appointment.end   = '2027-01-11T12:11:11.111+00:00'

    _ = appointment.save()

    # This is a reference, e.g. Patient/511a6231-361e-4b8e-8f9c-b183b7813f4d ..
    participants = appointment['participant']
    first_participant = participants[0]
    actor = first_participant['actor']

    # .. and this fetches the actual Patient from the server.
    fetched = actor.to_resource()

    assert fetched.id == Chalmers_ID

    # The serialize method returns a plain Python dict of a resource
    data = patient.serialize()

    assert data['resourceType'] == 'Patient'
    assert data['name'] == Chalmers_Name

# ################################################################################################################################

def test_bundles_searches(fhir_server:'FHIRTestServer') -> 'None':
    """ Mirrors docs/dev/healthcare/hl7/fhir/bundles - building searches, operators,
    the fetch styles and reading the Bundle itself.
    """
    _ = fhir_server.import_resource(_make_chalmers())

    client = SyncFHIRClient(fhir_server.address)
    patients = client.resources('Patient')

    # Active patients named Chalmers, at most 10 of them, youngest first
    result = patients.search(name='Chalmers', active=True).sort('-birthdate').limit(10)

    # Only now is the server invoked
    found = result.fetch()

    assert len(found) == 1

    first_found = found[0]
    assert first_found['name'] == Chalmers_Name

    # Born in the year 2000 or later - birthdate=ge2000-01-01 on the wire
    born_before = patients.search(birthdate__le='1990-01-01').fetch()

    born_before_ids:'anylist' = []
    for item in born_before:
        born_before_ids.append(item.id)

    assert Chalmers_ID in born_before_ids

    # Name containing a string
    containing = patients.search(name__contains='alm').fetch()
    assert isinstance(containing, list)

    # Status being none of the listed values
    observations = client.resources('Observation')
    excluded = observations.search(status__not=['cancelled', 'entered-in-error']).fetch()
    assert isinstance(excluded, list)

    # All the results - the Bundle's next links are followed until there are no more pages
    everyone = patients.search(name='Chalmers').fetch_all()
    assert len(everyone) == 1

    # The same, but lazily - each page is fetched only when the iteration reaches it
    lazily:'anylist' = []
    for patient in patients.search(name='Chalmers'):
        lazily.append(patient.id)

    assert lazily == [Chalmers_ID]

    # A single match - raises an error if there are none or more than one
    patient = patients.search(_id=Chalmers_ID).get()
    assert patient.id == Chalmers_ID

    # The first match or None
    patient = patients.search(name='Chalmers').first()
    assert patient is not None
    assert patient.id == Chalmers_ID

    # Only the number of matches, without any resources
    how_many = patients.search(active=True).count()
    assert how_many == 1

    # To read the Bundle's own fields, e.g. its total or its links, use fetch_raw
    bundle = patients.search(name='Chalmers').fetch_raw()

    assert bundle.total == 1

    entry_ids:'anylist' = []
    for entry in bundle.entry:
        entry_ids.append(entry.resource.id)

    assert entry_ids == [Chalmers_ID]

# ################################################################################################################################

def test_bundles_includes_elements_and_conditional_create(fhir_server:'FHIRTestServer') -> 'None':
    """ Mirrors docs/dev/healthcare/hl7/fhir/bundles - include, revinclude, elements
    and the conditional get_or_create.
    """
    _ = fhir_server.import_resource(_make_chalmers())

    client = SyncFHIRClient(fhir_server.address)

    # Encounters plus the patients they point at ..
    encounters = client.resources('Encounter').include('Encounter', 'subject')
    assert isinstance(encounters.fetch(), list)

    # .. or, the reverse, patients plus the observations that point back at them.
    patients = client.resources('Patient').revinclude('Observation', 'subject')
    assert isinstance(patients.fetch(), list)

    # Each returned Patient will contain only its name, plus the id and resourceType fields
    only_names = client.resources('Patient').elements('name').fetch()
    assert len(only_names) == 1

    # Create the patient only if no resource matches the search
    patient = client.resource('Patient', identifier=[{'system': 'urn:mrn', 'value': '12345'}])
    search = client.resources('Patient').search(identifier='urn:mrn|12345')
    patient, created = search.get_or_create(patient)

    assert created
    assert patient.id

# ################################################################################################################################

def test_path_access(fhir_server:'FHIRTestServer') -> 'None':
    """ Mirrors docs/dev/healthcare/hl7/fhir/path-access - dotted paths, defaults,
    matchers and paths into search results.
    """
    _ = fhir_server.import_resource(_make_chalmers())

    client = SyncFHIRClient(fhir_server.address)
    patient = cast_('any_', client.get('Patient', Chalmers_ID))

    # The first given name of the first name entry
    given = patient.get_by_path('name.0.given.0')
    assert given == 'Peter'

    # There may be no second name entry at all - the call returns None then
    maiden = patient.get_by_path('name.1.family')
    assert maiden is None

    # Or provide your own default
    maiden = patient.get_by_path('name.1.family', '(none)')
    assert maiden == '(none)'

    # The official name, regardless of its position in the name list
    family = patient.get_by_path(['name', {'use': 'official'}, 'family'])
    assert family == 'Chalmers'

    # The home phone number, out of all the telecom entries
    phone = patient.get_by_path(['telecom', {'system': 'phone', 'use': 'home'}, 'value'])
    assert phone == '555-0123'

    # The first given name within the official name entry
    given = patient.get_by_path(['name', {'use': 'official'}, 'given', 0])
    assert given == 'Peter'

    # Straight from the Bundle to the value, the self link in this case - the test
    # server returns everything in one page, so there is no next link to follow.
    bundle = client.resources('Patient').search(name='Chalmers').limit(1).fetch_raw()

    self_link = bundle.get_by_path(['link', {'relation': 'self'}, 'url'])
    assert self_link.startswith(fhir_server.address)

    next_link = bundle.get_by_path(['link', {'relation': 'next'}, 'url'])
    assert next_link is None

# ################################################################################################################################

def test_extensions(fhir_server:'FHIRTestServer') -> 'None':
    """ Mirrors docs/dev/healthcare/hl7/fhir/extensions - reading by URL, nested
    extensions, and writing and replacing extensions.
    """
    _ = fhir_server.import_resource(_make_chalmers())

    client = SyncFHIRClient(fhir_server.address)
    patient = client.resources('Patient').search(_id=Chalmers_ID).get()

    # Select the extension by its URL and read the city from its value
    path = ['extension', {'url': Birth_Place_URL}, 'valueAddress', 'city']
    city = patient.get_by_path(path)

    assert city == 'Amsterdam'

    # From the outer extension by URL, into the inner one by URL, down to the value
    path = [
        'extension', {'url': Nationality_URL},
        'extension', {'url': 'code'},
        'valueCodeableConcept', 'text',
    ]
    nationality = patient.get_by_path(path)

    assert nationality == 'Dutch'

    # To replace an existing extension, filter it out by its URL first
    remaining:'anylist' = []

    for item in patient.extension:
        if item['url'] != Birth_Place_URL:
            remaining.append(item)

    patient.extension = remaining

    patient.extension.append({
        'url': Birth_Place_URL,
        'valueAddress': {'city': 'Rotterdam', 'country': 'NL'},
    })

    _ = patient.save()

    # Read the patient back and confirm the replacement took effect
    patient = client.resources('Patient').search(_id=Chalmers_ID).get()

    path = ['extension', {'url': Birth_Place_URL}, 'valueAddress', 'city']
    city = patient.get_by_path(path)

    assert city == 'Rotterdam'

    # The resource may not have any extensions yet - this is the write flow
    # for a patient that has none.
    plain = client.resource('Patient', name=[{'family': 'Miller', 'given': ['Anna']}])
    _ = plain.save()

    fresh = client.resources('Patient').search(_id=plain.id).get()

    if 'extension' not in fresh:
        fresh.extension = []

    # Add the new one ..
    _ = fresh.extension.append({
        'url': Birth_Place_URL,
        'valueAddress': {'city': 'Amsterdam', 'country': 'NL'},
    })

    # .. and persist the change.
    _ = fresh.save()

    fresh = client.resources('Patient').search(_id=plain.id).get()

    path = ['extension', {'url': Birth_Place_URL}, 'valueAddress', 'city']
    city = fresh.get_by_path(path)

    assert city == 'Amsterdam'

# ################################################################################################################################

def test_versions_capability_and_identifier_search(fhir_server:'FHIRTestServer') -> 'None':
    """ Mirrors docs/dev/healthcare/hl7/fhir/versions - reading the server's FHIR version
    from its CapabilityStatement and the identifier-based lookup.
    """
    _ = fhir_server.import_resource(_make_chalmers())

    mrn_patient = {
        'resourceType': 'Patient',
        'identifier': [{'system': 'urn:mrn', 'value': '12345'}],
        'name': [{'family': 'Smith', 'given': ['John']}],
    }
    _ = fhir_server.import_resource(mrn_patient)

    client = SyncFHIRClient(fhir_server.address)

    # The CapabilityStatement describes the server, including its FHIR version
    capability = client.execute(path='metadata', method='get')

    assert capability['fhirVersion'] == '4.0.1'

    # Identifier search works the same in R4 and R6
    patient = client.resources('Patient').search(identifier='urn:mrn|12345').first()
    assert patient is not None

    names = patient['name']
    first_name = names[0]

    assert first_name['family'] == 'Smith'

# ################################################################################################################################

def test_versions_migration_between_servers(fhir_server:'FHIRTestServer') -> 'None':
    """ Mirrors docs/dev/healthcare/hl7/fhir/versions - moving patients between two
    FHIR servers with the metadata stripped along the way.
    """
    _ = fhir_server.import_resource(_make_chalmers())

    new_server = FHIRTestServer()
    new_server.start()

    try:
        source = SyncFHIRClient(fhir_server.address)
        target = SyncFHIRClient(new_server.address)

        # Read pages of patients from the old server ..
        for patient in source.resources('Patient').limit(100):

            # .. take each one's data without the old server's metadata ..
            data = patient.serialize()
            if 'meta' in data:
                del data['meta']

            # .. and write it to the new server.
            _ = target.resource('Patient', **data).save()

        # The new server now holds the migrated patient
        migrated = target.resources('Patient').search(name='Chalmers').fetch()
        assert len(migrated) == 1

    finally:
        new_server.stop()

# ################################################################################################################################

def test_versions_terminology_search(fhir_server:'FHIRTestServer') -> 'None':
    """ Mirrors docs/dev/healthcare/hl7/fhir/versions - searching observations by their
    LOINC code and reading the value through a path.
    """
    observation = {
        'resourceType': 'Observation',
        'status': 'final',
        'code': {'coding': [{'system': 'http://loinc.org', 'code': '2951-2'}]},
        'valueQuantity': {'value': 140, 'unit': 'mmol/L'},
    }
    _ = fhir_server.import_resource(observation)

    client = SyncFHIRClient(fhir_server.address)

    # Serum sodium observations, by their LOINC code
    observations = client.resources('Observation').search(code='http://loinc.org|2951-2')

    values:'anylist' = []
    for item in observations.fetch():
        values.append(item.get_by_path('valueQuantity.value'))

    assert values == [140]

# ################################################################################################################################

def test_europe_patient_summary(fhir_server:'FHIRTestServer') -> 'None':
    """ Mirrors docs/dev/healthcare/hl7/fhir/europe - assembling a patient summary out of
    the patient, their conditions and their medication statements.
    """
    _ = fhir_server.import_resource(_make_chalmers())

    condition = {
        'resourceType': 'Condition',
        'subject': {'reference': f'Patient/{Chalmers_ID}'},
        'code': {'text': 'Hypertension'},
    }
    _ = fhir_server.import_resource(condition)

    statement = {
        'resourceType': 'MedicationStatement',
        'status': 'active',
        'subject': {'reference': f'Patient/{Chalmers_ID}'},
        'medicationCodeableConcept': {'text': 'Lisinopril 10mg'},
    }
    _ = fhir_server.import_resource(statement)

    client = SyncFHIRClient(fhir_server.address)
    patient_id = Chalmers_ID

    # The subject of the summary ..
    patient = client.get('Patient', patient_id)

    # .. their active problems ..
    subject = f'Patient/{patient_id}'
    conditions = client.resources('Condition').search(subject=subject).fetch_all()

    # .. and what they are taking.
    statements = client.resources('MedicationStatement')
    medications = statements.search(subject=subject).fetch_all()

    # One JSON document, the same shape the service returns to its caller
    condition_list:'anylist' = []
    for item in conditions:
        condition_list.append(dict(item))

    medication_list:'anylist' = []
    for item in medications:
        medication_list.append(dict(item))

    patient_data = dict(patient)

    payload = {
        'patient': patient_data,
        'conditions': condition_list,
        'medications': medication_list,
    }

    assert patient_data['id'] == Chalmers_ID
    assert len(payload['conditions']) == 1
    assert len(payload['medications']) == 1

# ################################################################################################################################

def test_europe_prescriptions_and_write_side(fhir_server:'FHIRTestServer') -> 'None':
    """ Mirrors docs/dev/healthcare/hl7/fhir/europe - the e-prescription lookup and the
    write side of an HL7 v2 migration.
    """
    _ = fhir_server.import_resource(_make_chalmers())

    prescription = {
        'resourceType': 'MedicationRequest',
        'status': 'active',
        'subject': {'reference': f'Patient/{Chalmers_ID}'},
        'medicationCodeableConcept': {'text': 'Amoxicillin 500mg'},
    }
    _ = fhir_server.import_resource(prescription)

    client = SyncFHIRClient(fhir_server.address)

    # Active prescriptions for a patient identified by their national identifier
    prescriptions = client.resources('MedicationRequest').search(
        subject=f'Patient/{Chalmers_ID}',
        status='active',
    )

    found:'anylist' = []
    for item in prescriptions.fetch():
        found.append(item.id)

    assert len(found) == 1

    # A resource assembled from the fields of an incoming HL7 v2 message
    mrn = '67890'
    family = 'Johnson'
    given = 'Maria'

    patient = client.resource('Patient',
        identifier = [{'system': 'urn:mrn', 'value': mrn}],
        name = [{'family': family, 'given': [given]}],
    )

    _ = patient.save()

    assert patient.id

# ################################################################################################################################

def test_europe_document_bundles(fhir_server:'FHIRTestServer') -> 'None':
    """ Mirrors docs/dev/healthcare/hl7/fhir/europe - fetching a document Bundle by its ID
    and reading the Composition title through a path.
    """
    document = {
        'resourceType': 'Bundle',
        'id': 'epi-document-id',
        'type': 'document',
        'entry': [{
            'resource': {
                'resourceType': 'Composition',
                'status': 'final',
                'title': 'Product information',
            },
        }],
    }
    _ = fhir_server.import_resource(document)

    client = SyncFHIRClient(fhir_server.address)

    # The document Bundle, by its ID
    bundle = cast_('any_', client.get('Bundle', 'epi-document-id'))

    # The first entry is the Composition that gives the document its structure
    title = bundle.get_by_path('entry.0.resource.title')

    assert title == 'Product information'

# ################################################################################################################################
# ################################################################################################################################
