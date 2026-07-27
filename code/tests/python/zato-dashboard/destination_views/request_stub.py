# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a Dashboard view is called with when it is called directly - a request carrying the
# form the browser posts and a client that records every service invocation instead of
# reaching a server, so a view's whole round trip is observable offline.

# stdlib
from json import dumps

# Django
from django.http import QueryDict

# Zato
from zato.common.ext.bunch import Bunch, bunchify

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict

    anydict = anydict
    anylist = anylist
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The one cluster everything in the Dashboard belongs to
Cluster_Id = 1

# What a channel's three destination fields are given in the tests that do not vary them
Destination_Connection = 'test.rest.billing'
Destination_Type = 'rest'

# ################################################################################################################################
# ################################################################################################################################

class ResponseStub:
    """ What one recorded service invocation answers with.
    """
    def __init__(self, data:'any_', is_ok:'bool'=True, details:'str'='') -> 'None':
        self.ok = is_ok
        self.details = details
        self.has_data = bool(data)

        if isinstance(data, (dict, list)):
            self.data = bunchify(data)
        else:
            self.data = data

    def __iter__(self) -> 'any_':
        return iter(self.data)

# ################################################################################################################################
# ################################################################################################################################

class ClientRecorder:
    """ Stands in for the Dashboard's service client - it records what a view asks for and
    answers from what the test arranged, so what a view sends is asserted on directly.
    """
    def __init__(self) -> 'None':

        # Every invocation in the order it was made - one (service name, request) pair each
        self.invocations:'anylist' = []

        # What each service answers with, by service name
        self.responses:'stranydict' = {}

        # What a service with no answer arranged for says, there being nothing of that kind
        self.default_response = ResponseStub(None, is_ok=False, details='No such object')

# ################################################################################################################################

    def set_response(self, service:'str', data:'any_', is_ok:'bool'=True, details:'str'='') -> 'None':
        self.responses[service] = ResponseStub(data, is_ok=is_ok, details=details)

# ################################################################################################################################

    def invoke(self, service:'str', request:'any_'=None) -> 'ResponseStub':

        self.invocations.append((service, request))

        if service in self.responses:
            out = self.responses[service]
        else:
            out = self.default_response

        return out

# ################################################################################################################################

    def get_request(self, service:'str') -> 'anydict':
        """ Returns what the view sent to that service, the last time it sent anything.
        """
        for invoked_service, request in reversed(self.invocations):
            if invoked_service == service:
                out = request
                break
        else:
            raise Exception(f'Service `{service}` was never invoked')

        return out

# ################################################################################################################################
# ################################################################################################################################

def new_request(post_data:'stranydict | None'=None, method:'str'='POST') -> 'any_':
    """ Builds the request a view is called with, its form filled in with what the browser
    would have posted and its client recording rather than reaching a server.
    """
    post = QueryDict('', mutable=True)

    if post_data:
        for key, value in post_data.items():
            post[key] = value

    out = Bunch()

    out.method = method
    out.POST = post
    out.GET = QueryDict('', mutable=True)

    out.zato = Bunch()
    out.zato.args = {}
    out.zato.cluster_id = Cluster_Id
    out.zato.cluster = Bunch()
    out.zato.cluster.id = Cluster_Id
    out.zato.client = ClientRecorder()

    return out

# ################################################################################################################################
# ################################################################################################################################

def new_destination_list(
    connection:'str'=Destination_Connection,
    destination_type:'str'=Destination_Type,
    *,
    is_active:'bool'=True,
    options:'stranydict | None'=None,
    ) -> 'str':
    """ Returns a one-destination list in the form the Dashboard posts it - the JSON text
    both the wizard and the editor serialize their rows into.
    """
    if options is None:
        options = {'method': 'POST'}

    destination = {
        'name': connection,
        'type': destination_type,
        'connection': connection,
        'is_active': is_active,
        'options': options,
    }

    out = dumps([destination])
    return out

# ################################################################################################################################
# ################################################################################################################################

def new_channel_post_data(prefix:'str'='', **overrides:'any_') -> 'stranydict':
    """ Returns the form one MLLP channel is saved with - everything the create and edit
    views read, at its default, with whatever the test varies on top.
    """
    values = {
        'name': 'test.mllp.channel',
        'is_internal': False,
        'is_active': True,
        'service': 'test.service',
        'destinations': '',
        'respond_from': 'service',
        'delivery_mode': 'same-time',
        'max_msg_size': '1',
        'max_msg_size_unit': 'mb',
        'recv_timeout': '250',
        'idle_timeout': '10',
        'keepalive_idle': '30',
        'keepalive_interval': '10',
        'keepalive_probe_count': '5',
        'start_seq': '0b',
        'end_seq': '1c0d',
        'default_character_encoding': 'utf-8',
        'security_id': '',
    }

    values.update(overrides)

    out = {}

    for key, value in values.items():
        out[prefix + key] = value

    return out

# ################################################################################################################################
# ################################################################################################################################
