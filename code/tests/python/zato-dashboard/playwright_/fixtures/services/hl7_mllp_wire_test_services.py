# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone

# Zato
from zato.common.destination.constants import DestinationType
from zato.common.destination.model import parse_entries
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist
    any_ = any_
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# How MSH-7 of the acknowledgment is written
_Timestamp_Format = '%Y%m%d%H%M%S'

# ################################################################################################################################
# ################################################################################################################################

def _get_message_text(request:'any_') -> 'str':
    """ Returns the ER7 text of what a channel handed over - a REST channel delivers bytes,
    an MLLP channel that parses on input delivers a parsed message, and one that does not
    delivers the text itself.
    """
    if isinstance(request, bytes):
        return request.decode('utf-8')

    if isinstance(request, str):
        return request

    out = request.to_er7()
    return out

# ################################################################################################################################

def _get_msh_fields(message:'str') -> 'strlist':
    """ Returns the fields of the first MSH line of an HL7 message.
    """
    lines = message.split('\r')
    msh_line = lines[0]

    out = msh_line.split('|')
    return out

# ################################################################################################################################
# ################################################################################################################################

class HL7MLLPWireAckIdentity(Service):
    """ Answers every message with an HL7 acknowledgment whose MSA-3 names the channel that
    invoked this service, which is how a sender can tell from the acknowledgment alone which
    channel handled its message.
    """
    name = 'test.hl7.mllp.wire.ack-identity'

    def handle(self):

        message = _get_message_text(self.request.raw_request)

        # The channel this service runs on behalf of
        channel_item = self.wsgi_environ['zato.channel_item']
        channel_name = channel_item['name']

        # What the acknowledgment echoes back comes from the message's own MSH line
        fields = _get_msh_fields(message)
        sending_app      = fields[2]
        sending_facility = fields[3]
        receiving_app      = fields[4]
        receiving_facility = fields[5]
        control_id         = fields[9]
        processing_id      = fields[10]
        version_id         = fields[11]

        now = datetime.now(timezone.utc)
        timestamp = now.strftime(_Timestamp_Format)

        # The acknowledgment swaps sender and receiver, echoes the control id and carries
        # the channel's name in MSA-3
        ack_msh = (
            f'MSH|^~\\&|{receiving_app}|{receiving_facility}|{sending_app}|{sending_facility}'
            f'|{timestamp}||ACK|{self.cid}|{processing_id}|{version_id}'
        )
        ack_msa = f'MSA|AA|{control_id}|{channel_name}'

        self.response.payload = ack_msh + '\r' + ack_msa

# ################################################################################################################################
# ################################################################################################################################

# What the populate service appends to what the REST destination alone receives
rest_note_segment = 'NTE|1||For the care team alone'

# The resource the populate service gives the FHIR destination
fhir_patient_resource = {
    'resourceType': 'Patient',
    'name': [{'family': 'Johnson', 'given': ['Maria']}],
}

# ################################################################################################################################
# ################################################################################################################################

class HL7MLLPWirePopulate(Service):
    """ Says what each destination of its channel receives - the REST destination is given
    a payload of its own, the FHIR destination a resource, and the MLLP destination nothing
    at all, so a test reads off its receivers which destination got what.
    """
    name = 'test.hl7.mllp.wire.populate'

    def handle(self):

        message = _get_message_text(self.request.raw_request)

        # The destinations this channel declares, by name and type
        channel_item = self.wsgi_environ['zato.channel_item']
        entries = parse_entries(channel_item['destinations'])

        for entry in entries:

            # The FHIR destination is sent a resource rather than the HL7 message ..
            if entry.type == DestinationType.FHIR:
                self.destination[entry.name] = fhir_patient_resource

            # .. the REST destination receives something of its own ..
            elif entry.type == DestinationType.REST:
                self.destination[entry.name] = message + '\r' + rest_note_segment

            # .. and the MLLP destination receives nothing at all.
            elif entry.type == DestinationType.MLLP:
                self.destination[entry.name] = None

# ################################################################################################################################
# ################################################################################################################################
