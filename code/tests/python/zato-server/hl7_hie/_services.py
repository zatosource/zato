# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Live HL7
from live_hl7.recording import Send_Service, class_name

# ################################################################################################################################
# ################################################################################################################################

# The service behind the shared record's channel - the record's front door
Record_Service = 'hie.shr.record'

# What the shared record's front door files what reached it under
Record_Label = 'shr'

# The record's REST resources the front door works with - patients, the types their identifiers are of, its
# locations and its own HL7 queue - each an outgoing connection of Zato's, mapped to its path under the record's REST root
SHR_Patients_Connection = 'hie.shr.patients'
SHR_Identifier_Types_Connection = 'hie.shr.identifier-types'
SHR_Locations_Connection = 'hie.shr.locations'
SHR_Queue_Connection = 'hie.shr.hl7-queue'

SHR_Connections = {
    SHR_Patients_Connection:         '/patient',
    SHR_Identifier_Types_Connection: '/patientidentifiertype',
    SHR_Locations_Connection:        '/location',
    SHR_Queue_Connection:            '/hl7',
}

# The key the record's queue expects a message under
SHR_JSON_Key = 'hl7'

# The event the front door files itself - a registration, which the record has a patient API for and no working
# queue handler, so the front door does what the handler would
Registration_Event = 'A28'

# The service a facility's own systems reach the exchange through
Send_Service = Send_Service

# ################################################################################################################################
# ################################################################################################################################

# The front door's source, deployed with the recording services - the same module, hence the same helpers.
# Substitution is by marker rather than by formatting, as the source has braces of its own.
_front_door_source = '''
# stdlib
from http.client import CREATED, OK

# Where in a message's segments things are - a field's index is its number, with MSH one lower for the
# separator in MSH-1
_msh_message_type = 8
_pid_identifier = 3
_pid_name = 5
_pid_birth_date = 7
_pid_sex = 8

# The uuids of what the record names by display name, looked up once each
_uuids = {}

# ################################################################################################################################

def _segment(message, name):
    """ The first segment of a name, as its fields.
    """
    for segment in message.split('\\r'):
        fields = segment.split('|')
        if fields[0] == name:
            out = fields
            break

    # .. no segment of that name means the message is not one the front door takes.
    else:
        raise HL7ApplicationError(f'No {name} segment')

    return out

# ################################################################################################################################

def _components(field):
    out = field.split('^')
    return out

# ################################################################################################################################

def _birth_date(pid_7):
    """ The record spells a date with dashes.
    """
    out = f'{pid_7[0:4]}-{pid_7[4:6]}-{pid_7[6:8]}'
    return out

# ################################################################################################################################

def _json(response):
    out = json.loads(response.text)
    return out

# ################################################################################################################################

class @class_name@(Service):
    """ The shared record's front door - records what reached it, files a registration through the record's
    patient API and hands everything else to the record's own queue.
    """
    name = '@service@'

    def handle(self):
        message = _as_text(self.request.raw_request)
        _record('@label@', message)

        msh = _segment(message, 'MSH')
        event = _components(msh[_msh_message_type])[1]

        if event == '@registration_event@':
            self._register(message)
        else:
            self._queue(message)

# ################################################################################################################################

    def _queue(self, message):
        """ Into the record's HL7 queue, for its scheduler to process.
        """
        response = self.rest['@queue_connection@'].post({'@json_key@': message})

        if response.status_code != CREATED:
            raise HL7ApplicationError(f'The record did not queue the message, {response.status_code} {response.text}')

# ################################################################################################################################

    def _register(self, message):
        """ A new patient under the national id, unless the record has one already - the identifier is
        unique to it, so a second registration of the same person is not an error.
        """
        pid = _segment(message, 'PID')

        patient_id = _components(pid[_pid_identifier])[0]
        name = _components(pid[_pid_name])

        if self._has_patient(patient_id):
            self.logger.info('The record already has patient %s', patient_id)
            return

        identifier_type = self._uuid_of('@identifier_types_connection@', {}, '@identifier_type@')
        location = self._uuid_of('@locations_connection@', {'q': '@location@'}, '@location@')

        payload = {
            'person': {
                'names': [{'familyName': name[0], 'givenName': name[1]}],
                'gender': pid[_pid_sex],
                'birthdate': _birth_date(pid[_pid_birth_date]),
            },
            'identifiers': [{
                'identifier': patient_id,
                'identifierType': identifier_type,
                'location': location,
                'preferred': True,
            }],
        }

        response = self.rest['@patients_connection@'].post(payload)

        if response.status_code != CREATED:
            raise HL7ApplicationError(
                f'The record did not file patient {patient_id}, {response.status_code} {response.text}')

# ################################################################################################################################

    def _has_patient(self, patient_id):
        response = self.rest['@patients_connection@'].get(params={'q': patient_id})

        if response.status_code != OK:
            raise HL7ApplicationError(
                f'The record could not look patient {patient_id} up, {response.status_code} {response.text}')

        identifiers = []

        for patient in _json(response)['results']:
            for identifier in patient['identifiers']:
                identifiers.append(identifier['identifier'])

        out = patient_id in identifiers
        return out

# ################################################################################################################################

    def _uuid_of(self, connection, params, display):
        """ The uuid of what the record lists under a display name at one of its resources - the identifier types
        resource does not search by name, so it is all of them and a match on the name here.
        """
        if display in _uuids:
            return _uuids[display]

        response = self.rest[connection].get(params=params)

        if response.status_code != OK:
            raise HL7ApplicationError(f'The record could not look {display} up, {response.status_code} {response.text}')

        for item in _json(response)['results']:
            if item['display'] == display:
                out = item['uuid']
                break

        # .. the record has nothing of that name.
        else:
            raise HL7ApplicationError(f'The record has no {display}')

        _uuids[display] = out

        return out

# ################################################################################################################################
# ################################################################################################################################
'''

# ################################################################################################################################
# ################################################################################################################################

def front_door_source(identifier_type:'str', location:'str') -> 'str':
    """ The front door's source for a record filing national ids under the named identifier type, as issued at
    the named location.
    """
    out = _front_door_source
    out = out.replace('@class_name@', class_name(Record_Service))
    out = out.replace('@service@', Record_Service)
    out = out.replace('@label@', Record_Label)
    out = out.replace('@registration_event@', Registration_Event)
    out = out.replace('@queue_connection@', SHR_Queue_Connection)
    out = out.replace('@patients_connection@', SHR_Patients_Connection)
    out = out.replace('@identifier_types_connection@', SHR_Identifier_Types_Connection)
    out = out.replace('@locations_connection@', SHR_Locations_Connection)
    out = out.replace('@json_key@', SHR_JSON_Key)
    out = out.replace('@identifier_type@', identifier_type)
    out = out.replace('@location@', location)

    return out

# ################################################################################################################################
# ################################################################################################################################
