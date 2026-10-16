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

# The number of bytes each group of four base64 characters decodes to
_base64_group_bytes = 3
_base64_group_chars = 4

_timestamp = '2026-10-16T09:30:00+00:00'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class CreateReferralRequest(Model):
    referring_practitioner: str
    referring_organization: str
    patient_given_name:     str
    patient_family_name:    str
    patient_birth_date:     str
    reason:                 str
    urgency:                str
    preferred_clinic_code:  optional[str] = None

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ReferralStatus(Model):
    referral_id:          str
    status:               str
    received_at:          str
    expected_decision_by: str
    assigned_clinic_code: str

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class Observation(Model):
    code:            str
    name:            str
    value:           str
    unit:            str
    reference_range: str
    flag:            optional[str] = None

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class LabResultMessage(Model):
    message_id:   str
    patient_id:   str
    order_id:     str
    collected_at: str
    observations: list_[Observation]

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class UploadDocumentRequest(Model):
    patient_id:     str
    document_type:  str
    file_name:      str
    content_type:   str
    content_base64: str
    episode_id:     optional[str] = None

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DocumentReceipt(Model):
    document_id: str
    size_bytes:  int
    stored_at:   str

# ################################################################################################################################
# ################################################################################################################################

def _build_referral_status(referral_id:'str') -> 'ReferralStatus':
    """ Builds the status of a referral that was received and is awaiting intake.
    """
    out = ReferralStatus()
    out.referral_id = referral_id
    out.status = 'awaiting-intake'
    out.received_at = _timestamp
    out.expected_decision_by = '2026-10-23'
    out.assigned_clinic_code = 'CL-OUT-01'

    return out

# ################################################################################################################################
# ################################################################################################################################

class CreateReferral(Service):
    """ Receives a referral letter from a primary care practitioner.
    """
    name   = 'healthcare.referrals.create-referral'
    input  = CreateReferralRequest
    output = ReferralStatus

    def handle(self) -> 'None':
        self.response.payload = _build_referral_status('RF-610027')

# ################################################################################################################################
# ################################################################################################################################

class GetReferralStatus(Service):
    """ Returns the processing status of a referral.
    """
    name   = 'healthcare.referrals.get-referral-status'
    input  = 'referral_id'
    output = ReferralStatus

    def handle(self) -> 'None':
        self.response.payload = _build_referral_status(self.request.input.referral_id)

# ################################################################################################################################
# ################################################################################################################################

class ReceiveLabResult(Service):
    """ Receives the observations of a laboratory order and acknowledges the message.
    """
    name   = 'healthcare.lab.receive-result'
    input  = LabResultMessage
    output = 'message_id', 'acknowledgement_code', 'observation_count'

    def handle(self) -> 'None':
        observations = self.request.input.observations

        self.response.payload.message_id = self.request.input.message_id
        self.response.payload.acknowledgement_code = 'AA'
        self.response.payload.observation_count = len(observations)

# ################################################################################################################################
# ################################################################################################################################

class ReceiveAdmissionEvent(Service):
    """ Receives an admission, a transfer or a discharge event from the hospital information system.
    """
    name = 'healthcare.admissions.receive-event'

    def handle(self) -> 'None':

        if not (event_type := self.request.input.get('event_type')):
            event_type = 'admit'

        self.response.payload = {
            'event_type': event_type,
            'patient_id': self.request.input.get('patient_id'),
            'acknowledgement_code': 'AA',
            'processed_at': _timestamp,
        }

# ################################################################################################################################
# ################################################################################################################################

class UploadDocument(Service):
    """ Stores a document, e.g. a scanned letter or a discharge summary, in the record of a patient.
    """
    name   = 'healthcare.documents.upload-document'
    input  = UploadDocumentRequest
    output = DocumentReceipt

    def handle(self) -> 'None':

        content_length = len(self.request.input.content_base64)
        size_bytes = content_length * _base64_group_bytes // _base64_group_chars

        out = DocumentReceipt()
        out.document_id = 'DOC-209931'
        out.size_bytes = size_bytes
        out.stored_at = _timestamp

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class FHIRPatientSearch(Service):
    """ Returns a FHIR searchset bundle of the patients matching an identifier or a family name.
    """
    name  = 'healthcare.fhir.patient-search'
    input = '-identifier', '-family', '-birthdate'

    def handle(self) -> 'None':

        family = self.request.input.family or 'Smith'
        birth_date = self.request.input.birthdate or '1968-04-12'
        identifier = self.request.input.identifier or 'PT-100231'

        patient = {
            'resourceType': 'Patient',
            'id': identifier,
            'identifier': [{'system': 'urn:example:patient-id', 'value': identifier}],
            'name': [{'family': family, 'given': ['John']}],
            'birthDate': birth_date,
            'gender': 'male',
        }

        self.response.payload = {
            'resourceType': 'Bundle',
            'type': 'searchset',
            'total': 1,
            'entry': [{'fullUrl': f'urn:example:Patient/{identifier}', 'resource': patient}],
        }

# ################################################################################################################################
# ################################################################################################################################

class PortalUpcomingAppointments(Service):
    """ Returns the next appointment of the patient signed in to the patient portal.
    """
    name   = 'healthcare.portal.upcoming-appointments'
    output = 'patient_id', 'next_appointment_at', 'clinic_name', 'upcoming_count'

    def handle(self) -> 'None':
        self.response.payload.patient_id = 'PT-100231'
        self.response.payload.next_appointment_at = '2026-10-19T09:45:00+00:00'
        self.response.payload.clinic_name = 'Outpatient Clinic North'
        self.response.payload.upcoming_count = 3

# ################################################################################################################################
# ################################################################################################################################
