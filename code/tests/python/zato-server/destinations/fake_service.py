# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A service offering only what delivering to a destination reaches for - the four facades, its
# correlation id, the message it was given and the server it runs on. Each facade remembers the
# calls made through it, so a test can say which connection was reached, with what, and whether
# the connection's own audit log was turned off for the call.

# Zato
from zato.server.destination.facade import DestinationFacade

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# The server the deliveries are recorded under
Server_Name = 'test-destination-server'

# The correlation id of the message that came in
CID = 'cid-destination-server-1'

# What each type of connection answers a delivery with
REST_Response = 'Accepted over REST'
MLLP_Response = 'AA'
FHIR_Response = {'resourceType': 'OperationOutcome'}
SMTP_Response = True

# ################################################################################################################################
# ################################################################################################################################

class FakeRESTInvoker:
    """ Stands in for the invoker self.rest hands out.
    """
    def __init__(self, connection:'str', calls:'anylist') -> 'None':
        self.connection = connection
        self.calls = calls

# ################################################################################################################################

    def _record(self, method:'str', args:'any_', kwargs:'anydict') -> 'str':
        self.calls.append((self.connection, method, args, kwargs))
        return REST_Response

# ################################################################################################################################

    def get(self, *args:'any_', **kwargs:'any_') -> 'str':
        return self._record('get', args, kwargs)

    def post(self, *args:'any_', **kwargs:'any_') -> 'str':
        return self._record('post', args, kwargs)

    def put(self, *args:'any_', **kwargs:'any_') -> 'str':
        return self._record('put', args, kwargs)

    def patch(self, *args:'any_', **kwargs:'any_') -> 'str':
        return self._record('patch', args, kwargs)

    def delete(self, *args:'any_', **kwargs:'any_') -> 'str':
        return self._record('delete', args, kwargs)

# ################################################################################################################################
# ################################################################################################################################

class FakeRESTFacade:
    """ Stands in for self.rest.
    """
    def __init__(self) -> 'None':
        self.calls:'anylist' = []

    def __getitem__(self, connection:'str') -> 'FakeRESTInvoker':
        out = FakeRESTInvoker(connection, self.calls)
        return out

# ################################################################################################################################
# ################################################################################################################################

class FakeMLLPInvoker:
    """ Stands in for the invoker self.mllp hands out.
    """
    def __init__(self, connection:'str', calls:'anylist') -> 'None':
        self.connection = connection
        self.calls = calls

    def send(self, payload:'any_', *, needs_audit:'bool'=True) -> 'str':
        self.calls.append((self.connection, payload, needs_audit))
        return MLLP_Response

# ################################################################################################################################
# ################################################################################################################################

class FakeMLLPFacade:
    """ Stands in for self.mllp.
    """
    def __init__(self) -> 'None':
        self.calls:'anylist' = []

    def __getitem__(self, connection:'str') -> 'FakeMLLPInvoker':
        out = FakeMLLPInvoker(connection, self.calls)
        return out

# ################################################################################################################################
# ################################################################################################################################

class FakeFHIRClient:
    """ Stands in for the client self.fhir hands out.
    """
    def __init__(self, connection:'str', calls:'anylist') -> 'None':
        self.connection = connection
        self.calls = calls

    def _do_request(self, method:'str', path:'str', data:'any_'=None, *, needs_audit:'bool'=True) -> 'anydict':
        self.calls.append((self.connection, method, path, data, needs_audit))
        return FHIR_Response

# ################################################################################################################################
# ################################################################################################################################

class FakeFHIRFacade:
    """ Stands in for self.fhir.
    """
    def __init__(self) -> 'None':
        self.calls:'anylist' = []

    def __getitem__(self, connection:'str') -> 'FakeFHIRClient':
        out = FakeFHIRClient(connection, self.calls)
        return out

# ################################################################################################################################
# ################################################################################################################################

class FakeSMTPConnection:
    """ Stands in for the connection an SMTP item holds.
    """
    def __init__(self, connection:'str', calls:'anylist') -> 'None':
        self.connection = connection
        self.calls = calls

    def send(self, message:'any_') -> 'bool':
        self.calls.append((self.connection, message.to, message.subject, message.body))
        return SMTP_Response

# ################################################################################################################################

class FakeSMTPItem:
    """ Stands in for one item of self.email.smtp.
    """
    def __init__(self, connection:'str', calls:'anylist') -> 'None':
        self.conn = FakeSMTPConnection(connection, calls)

# ################################################################################################################################

class FakeSMTPFacade:
    """ Stands in for self.email.smtp.
    """
    def __init__(self) -> 'None':
        self.calls:'anylist' = []

    def __getitem__(self, connection:'str') -> 'FakeSMTPItem':
        out = FakeSMTPItem(connection, self.calls)
        return out

# ################################################################################################################################

class FakeEMailAPI:
    """ Stands in for self.email.
    """
    def __init__(self) -> 'None':
        self.smtp = FakeSMTPFacade()

# ################################################################################################################################
# ################################################################################################################################

class FakeRequest:
    """ Stands in for self.request, carrying the message as it arrived.
    """
    def __init__(self, raw:'any_') -> 'None':
        self.raw = raw

# ################################################################################################################################

class FakeServer:
    """ Stands in for self.server, which a delivery reaches only for the name it records under.
    """
    def __init__(self) -> 'None':
        self.name = Server_Name

# ################################################################################################################################
# ################################################################################################################################

class FakeService:
    """ Stands in for a service whose channel has destinations.
    """
    email: 'FakeEMailAPI | None'

    def __init__(self, request_payload:'any_', *, has_email:'bool'=True) -> 'None':

        self.cid = CID
        self.request = FakeRequest(request_payload)
        self.server = FakeServer()

        self.rest = FakeRESTFacade()
        self.mllp = FakeMLLPFacade()
        self.fhir = FakeFHIRFacade()

        # A server with the e-mail component turned off has no such facade at all
        if has_email:
            self.email = FakeEMailAPI()
        else:
            self.email = None

        self.destination = DestinationFacade()
        self.destination.init(request_payload)

# ################################################################################################################################
# ################################################################################################################################
