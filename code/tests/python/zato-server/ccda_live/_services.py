# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64decode
from json import dumps

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

# What a service answers with - the bundle in brief, so a test asserts on the conversion without carrying the whole bundle back
def describe(bundle:'any_') -> 'stranydict':

    resource_types = set()
    patient_family = ''
    document_size = 0

    for entry in bundle.entry:
        resource = entry.resource
        resource_types.add(resource.resource_type)

        if resource.resource_type == 'Patient':
            patient_family = resource.name[0].family

        if resource.resource_type == 'DocumentReference':
            attachment = resource.content[0].attachment
            document_size = len(b64decode(attachment.data))

    out = {
        'type': bundle.to_dict()['type'],
        'resource_count': len(bundle.entry),
        'resource_types': sorted(resource_types),
        'patient_family': patient_family,
        'document_size': document_size,
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

class CCDAReceive(Service):
    """ The service behind a channel that converts on arrival - what it receives is already the bundle.
    """
    name = 'test.ccda.receive'

    def handle(self) -> 'None':
        bundle = self.request.input

        self.response.content_type = 'application/json'
        self.response.payload = dumps(describe(bundle))

# ################################################################################################################################
# ################################################################################################################################

class CCDAConvert(Service):
    """ The service behind a plain REST channel - it converts the document it received itself, the way a user's service would.
    """
    name = 'test.ccda.convert'

    def handle(self) -> 'None':
        document = self.request.input
        bundle = self.ccda.to_fhir(document)

        self.response.content_type = 'application/json'
        self.response.payload = dumps(describe(bundle))

# ################################################################################################################################
# ################################################################################################################################
