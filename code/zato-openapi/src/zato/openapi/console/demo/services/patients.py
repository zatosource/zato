# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.typing_ import list_, optional
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist
    any_ = any_
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# The demographics every patient record is built from, chosen by the patient ID so that responses are deterministic
_people = [
    {'given_name': 'John',  'family_name': 'Smith',   'birth_date': '1968-04-12', 'sex': 'male'},
    {'given_name': 'Maria', 'family_name': 'Johnson', 'birth_date': '1975-09-30', 'sex': 'female'},
    {'given_name': 'Anna',  'family_name': 'Miller',  'birth_date': '1990-01-18', 'sex': 'female'},
    {'given_name': 'James', 'family_name': 'Brown',   'birth_date': '1959-11-02', 'sex': 'male'},
]

_addresses = [
    {'street': '1452 Maple Avenue', 'city': 'Springfield', 'state': 'IL', 'postal_code': '62704'},
    {'street': '87 Lakeview Drive', 'city': 'Madison',     'state': 'WI', 'postal_code': '53703'},
    {'street': '310 Oak Street',    'city': 'Columbus',    'state': 'OH', 'postal_code': '43215'},
]

_physicians = ['Dr. Robert Davis', 'Dr. Linda Wilson', 'Dr. Michael Moore']

_episode_types = ['Outpatient treatment', 'Inpatient admission', 'Day treatment']

_timestamp = '2026-10-16T09:30:00+00:00'

# ################################################################################################################################
# ################################################################################################################################

def _pick(items:'anylist', key:'str') -> 'any_':
    """ Returns the same element of a list for the same key.
    """
    total = 0

    for character in key:
        total += ord(character)

    index = total % len(items)

    out = items[index]
    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Address(Model):
    street:      str
    city:        str
    state:       str
    postal_code: str

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Contact(Model):
    kind:  str
    value: str

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class GetPatientRequest(Model):
    patient_id: str

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Patient(Model):
    patient_id:             str
    medical_record_number:  str
    given_name:             str
    family_name:            str
    birth_date:             str
    sex:                    str
    is_active:              bool
    primary_care_physician: str
    address:                Address
    contacts:               list_[Contact]

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class SearchPatientsRequest(Model):
    family_name: optional[str] = None
    birth_date:  optional[str] = None
    max_results: optional[str] = None

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PatientSummary(Model):
    patient_id:  str
    given_name:  str
    family_name: str
    birth_date:  str

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PatientSearchResponse(Model):
    total:    int
    patients: list_[PatientSummary]

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class RegisterPatientRequest(Model):
    given_name:  str
    family_name: str
    birth_date:  str
    sex:         str
    street:      str
    city:        str
    state:       str
    postal_code: str
    phone:       optional[str] = None
    email:       optional[str] = None

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class RegisterPatientResponse(Model):
    patient_id:            str
    medical_record_number: str
    created_at:            str

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class UpdateContactRequest(Model):
    patient_id: str
    phone:      optional[str] = None
    email:      optional[str] = None

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Episode(Model):
    episode_id:   str
    patient_id:   str
    episode_type: str
    status:       str
    started_on:   str
    care_team:    str

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class EpisodeListResponse(Model):
    episodes: list_[Episode]

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class OpenEpisodeRequest(Model):
    patient_id:      str
    episode_type:    str
    referral_id:     str
    care_team:       str
    primary_concern: str

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class CloseEpisodeRequest(Model):
    episode_id:        str
    closure_reason:    str
    closed_by:         str
    discharge_summary: optional[str] = None

# ################################################################################################################################
# ################################################################################################################################

class GetPatient(Service):
    """ Returns the demographics, the address and the contact details of a patient.
    """
    name   = 'healthcare.patients.get-patient'
    input  = GetPatientRequest
    output = Patient

    def handle(self) -> 'None':

        patient_id = self.request.input.patient_id
        person = _pick(_people, patient_id)
        address_data = _pick(_addresses, patient_id)

        address = Address()
        address.street = address_data['street']
        address.city = address_data['city']
        address.state = address_data['state']
        address.postal_code = address_data['postal_code']

        phone = Contact()
        phone.kind = 'phone'
        phone.value = '+1 217 555 0142'

        email = Contact()
        email.kind = 'email'
        email.value = f'{person["given_name"].lower()}.{person["family_name"].lower()}@example.com'

        out = Patient()
        out.patient_id = patient_id
        out.medical_record_number = f'MRN-{patient_id}'
        out.given_name = person['given_name']
        out.family_name = person['family_name']
        out.birth_date = person['birth_date']
        out.sex = person['sex']
        out.is_active = True
        out.primary_care_physician = _pick(_physicians, patient_id)
        out.address = address
        out.contacts = [phone, email]

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class SearchPatients(Service):
    """ Returns the patients matching a family name, a birth date or both.
    """
    name   = 'healthcare.patients.search-patients'
    input  = SearchPatientsRequest
    output = PatientSearchResponse

    def handle(self) -> 'None':

        family_name = self.request.input.family_name
        birth_date = self.request.input.birth_date

        patients = []

        for index, person in enumerate(_people):

            if family_name:
                if person['family_name'].lower() != family_name.lower():
                    continue

            if birth_date:
                if person['birth_date'] != birth_date:
                    continue

            summary = PatientSummary()
            summary.patient_id = f'PT-10023{index}'
            summary.given_name = person['given_name']
            summary.family_name = person['family_name']
            summary.birth_date = person['birth_date']
            patients.append(summary)

        out = PatientSearchResponse()
        out.total = len(patients)
        out.patients = patients

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class RegisterPatient(Service):
    """ Registers a new patient and assigns a medical record number.
    """
    name   = 'healthcare.patients.register-patient'
    input  = RegisterPatientRequest
    output = RegisterPatientResponse

    def handle(self) -> 'None':

        out = RegisterPatientResponse()
        out.patient_id = 'PT-100240'
        out.medical_record_number = 'MRN-PT-100240'
        out.created_at = _timestamp

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class UpdateContact(Service):
    """ Updates the phone number or the email address of a patient.
    """
    name   = 'healthcare.patients.update-contact'
    input  = UpdateContactRequest
    output = 'patient_id', 'updated_at'

    def handle(self) -> 'None':
        self.response.payload.patient_id = self.request.input.patient_id
        self.response.payload.updated_at = _timestamp

# ################################################################################################################################
# ################################################################################################################################

class WithdrawConsent(Service):
    """ Withdraws a consent a patient gave for the exchange of their data.
    """
    name   = 'healthcare.patients.withdraw-consent'
    input  = 'patient_id', 'consent_id', '-reason'
    output = 'consent_id', 'status'

    def handle(self) -> 'None':
        self.response.payload.consent_id = self.request.input.consent_id
        self.response.payload.status = 'withdrawn'

# ################################################################################################################################
# ################################################################################################################################

class ListEpisodes(Service):
    """ Returns the episodes of care of a patient, optionally only those in a given status.
    """
    name   = 'healthcare.episodes.list-episodes'
    input  = 'patient_id', '-status'
    output = EpisodeListResponse

    def handle(self) -> 'None':

        patient_id = self.request.input.patient_id
        status = self.request.input.status

        episodes = []

        for index, episode_type in enumerate(_episode_types):

            episode_status = 'active' if index == 0 else 'closed'

            if status:
                if episode_status != status:
                    continue

            episode = Episode()
            episode.episode_id = f'EP-{patient_id}-{index + 1}'
            episode.patient_id = patient_id
            episode.episode_type = episode_type
            episode.status = episode_status
            episode.started_on = f'202{4 + index}-03-01'
            episode.care_team = 'Outpatient Care Team'
            episodes.append(episode)

        out = EpisodeListResponse()
        out.episodes = episodes

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class OpenEpisode(Service):
    """ Opens a new episode of care for a patient out of an accepted referral.
    """
    name   = 'healthcare.episodes.open-episode'
    input  = OpenEpisodeRequest
    output = Episode

    def handle(self) -> 'None':

        request = self.request.input

        out = Episode()
        out.episode_id = f'EP-{request.patient_id}-4'
        out.patient_id = request.patient_id
        out.episode_type = request.episode_type
        out.status = 'active'
        out.started_on = '2026-10-16'
        out.care_team = request.care_team

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class CloseEpisode(Service):
    """ Closes an episode of care with a closure reason.
    """
    name   = 'healthcare.episodes.close-episode'
    input  = CloseEpisodeRequest
    output = Episode

    def handle(self) -> 'None':

        episode_id = self.request.input.episode_id

        out = Episode()
        out.episode_id = episode_id
        out.patient_id = 'PT-100231'
        out.episode_type = 'Outpatient treatment'
        out.status = 'closed'
        out.started_on = '2026-03-01'
        out.care_team = 'Outpatient Care Team'

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################
