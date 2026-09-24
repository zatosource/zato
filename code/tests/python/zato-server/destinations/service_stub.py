# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A service offering only what delivering to a destination reaches for - the four facades, its
# correlation id, the message it was given and the server it runs on. Each facade remembers the
# calls made through it, so a test can say which connection was reached, with what, and whether
# the connection's own audit log was turned off for the call.

# stdlib
from http.client import INTERNAL_SERVER_ERROR, OK

# Zato
from zato.common.audit_log.common import Ack_Rejected_Marker
from zato.common.pubsub.outgoing import SendResult
from zato.server.destination.facade import DestinationFacade

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strlist

    anydict = anydict
    anylist = anylist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The server the deliveries are recorded under
Server_Name = 'test-destination-server'

# The correlation id of the message that came in
CID = 'cid-destination-server-1'

class RESTResponseStub:
    """ Stands in for what an outgoing REST connection answers a call with.
    """
    def __init__(self, ok:'bool', status_code:'int', reason:'str', text:'str') -> 'None':
        self.ok = ok
        self.status_code = status_code
        self.reason = reason
        self.text = text

# ################################################################################################################################
# ################################################################################################################################

# What each type of connection answers a delivery with
REST_Response_Text = 'Accepted over REST'
REST_Response = RESTResponseStub(True, OK, 'OK', REST_Response_Text)
MLLP_Response = 'AA'
FHIR_Response = {'resourceType': 'OperationOutcome'}
SMTP_Response = True

# What a connection with the queue switch on answers with, the message being in the queue
# rather than sent.
REST_Queued_Response = SendResult()
REST_Queued_Response.is_in_queue = True
REST_Queued_Response.msg_id = 'msg-queued-1'

# What a REST endpoint that turned the message down answers with, and how that reads on the row
REST_Rejected_Text = 'Refused by the endpoint'
REST_Rejected_Response = RESTResponseStub(False, INTERNAL_SERVER_ERROR, 'Internal Server Error', REST_Rejected_Text)
REST_Rejected_Status = f'HTTP {INTERNAL_SERVER_ERROR} Internal Server Error'

# What an HL7 receiver that turned the message down answers with, and how that reads on the row
MLLP_Rejected_Error = 'Unknown patient identifier'
MLLP_Rejected_Text = 'AR'
MLLP_Rejected_Status = f'{Ack_Rejected_Marker} AR {MLLP_Rejected_Error}'

# ################################################################################################################################
# ################################################################################################################################

class RESTInvokerRecorder:
    """ Stands in for the invoker self.rest hands out, with the response every call answers
    with replaceable.
    """
    def __init__(self, connection:'str', calls:'anylist', response:'any_') -> 'None':
        self.connection = connection
        self.calls = calls
        self.response = response

# ################################################################################################################################

    def _record(self, method:'str', args:'any_', kwargs:'anydict') -> 'any_':
        self.calls.append((self.connection, method, args, kwargs))
        return self.response

# ################################################################################################################################

    def get(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return self._record('get', args, kwargs)

    def post(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return self._record('post', args, kwargs)

    def put(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return self._record('put', args, kwargs)

    def patch(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return self._record('patch', args, kwargs)

    def delete(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return self._record('delete', args, kwargs)

# ################################################################################################################################
# ################################################################################################################################

class RESTFacadeRecorder:
    """ Stands in for self.rest. A connection named among the rejecting ones answers every call
    with a status the endpoint turned the message down with.
    """
    def __init__(self) -> 'None':
        self.calls:'anylist' = []
        self.rejecting:'strlist' = []

        # Connections whose queue switch is on, so a send hands the message over.
        self.queued:'strlist' = []

    def __getitem__(self, connection:'str') -> 'RESTInvokerRecorder':

        if connection in self.queued:
            response = REST_Queued_Response

        elif connection in self.rejecting:
            response = REST_Rejected_Response

        else:
            response = REST_Response

        out = RESTInvokerRecorder(connection, self.calls, response)
        return out

# ################################################################################################################################
# ################################################################################################################################

class AckResultStub:
    """ Stands in for what an MLLP outgoing connection answers a send with.
    """
    def __init__(self, ack_text:'str', *, is_accepted:'bool'=True, ack_code:'str'='AA', error_text:'str'='') -> 'None':
        self.ack_text = ack_text
        self.is_accepted = is_accepted
        self.ack_code = ack_code
        self.error_text = error_text

# ################################################################################################################################

class MLLPInvokerRecorder:
    """ Stands in for the invoker self.mllp hands out.
    """
    def __init__(self, connection:'str', calls:'anylist', ack:'AckResultStub') -> 'None':
        self.connection = connection
        self.calls = calls
        self.ack = ack

    def send(self, payload:'any_', *, needs_audit:'bool'=True) -> 'AckResultStub':
        self.calls.append((self.connection, payload, needs_audit))
        return self.ack

# ################################################################################################################################
# ################################################################################################################################

class MLLPFacadeRecorder:
    """ Stands in for self.mllp. A connection named among the rejecting ones answers every send
    with an acknowledgment that did not accept the message.
    """
    def __init__(self) -> 'None':
        self.calls:'anylist' = []
        self.rejecting:'strlist' = []

    def __getitem__(self, connection:'str') -> 'MLLPInvokerRecorder':

        if connection in self.rejecting:
            ack = AckResultStub(MLLP_Rejected_Text, is_accepted=False, ack_code='AR', error_text=MLLP_Rejected_Error)
        else:
            ack = AckResultStub(MLLP_Response)

        out = MLLPInvokerRecorder(connection, self.calls, ack)
        return out

# ################################################################################################################################
# ################################################################################################################################

class FHIRClientRecorder:
    """ Stands in for the client self.fhir hands out.
    """
    def __init__(self, connection:'str', calls:'anylist', params_calls:'anylist') -> 'None':
        self.connection = connection
        self.calls = calls
        self.params_calls = params_calls

    def _do_request(
        self,
        method:'str',
        path:'str',
        data:'any_'=None,
        params:'any_'=None,
        *,
        needs_audit:'bool'=True,
        ) -> 'anydict':

        self.calls.append((self.connection, method, path, data, needs_audit))
        self.params_calls.append(params)

        return FHIR_Response

# ################################################################################################################################
# ################################################################################################################################

class FHIRFacadeRecorder:
    """ Stands in for self.fhir.
    """
    def __init__(self) -> 'None':
        self.calls:'anylist' = []

        # The query string each call went out with.
        self.params_calls:'anylist' = []

    def __getitem__(self, connection:'str') -> 'FHIRClientRecorder':
        out = FHIRClientRecorder(connection, self.calls, self.params_calls)
        return out

# ################################################################################################################################
# ################################################################################################################################

class SMTPConnectionRecorder:
    """ Stands in for the connection an SMTP item holds.
    """
    def __init__(self, connection:'str', calls:'anylist', is_sent:'bool') -> 'None':
        self.connection = connection
        self.calls = calls
        self.is_sent = is_sent

    def send(self, message:'any_', cid:'str'='') -> 'bool':
        self.calls.append((self.connection, message.to, message.subject, message.body))
        return self.is_sent

# ################################################################################################################################

class SMTPItemRecorder:
    """ Stands in for one item of self.email.smtp.
    """
    def __init__(self, connection:'str', calls:'anylist', is_sent:'bool') -> 'None':
        self.conn = SMTPConnectionRecorder(connection, calls, is_sent)

# ################################################################################################################################

class SMTPFacadeRecorder:
    """ Stands in for self.email.smtp. A connection named among the rejecting ones reports
    every message as one it could not send.
    """
    def __init__(self) -> 'None':
        self.calls:'anylist' = []
        self.rejecting:'strlist' = []

    def __getitem__(self, connection:'str') -> 'SMTPItemRecorder':
        is_sent = connection not in self.rejecting
        out = SMTPItemRecorder(connection, self.calls, is_sent)
        return out

# ################################################################################################################################

class EMailAPIRecorder:
    """ Stands in for self.email.
    """
    def __init__(self) -> 'None':
        self.smtp = SMTPFacadeRecorder()

# ################################################################################################################################
# ################################################################################################################################

class RequestStub:
    """ Stands in for self.request, carrying the message as it arrived.
    """
    def __init__(self, raw:'any_') -> 'None':
        self.raw = raw

# ################################################################################################################################

class ServerStub:
    """ Stands in for self.server, which a delivery reaches only for the name it records under.
    """
    def __init__(self) -> 'None':
        self.name = Server_Name

# ################################################################################################################################
# ################################################################################################################################

class ServiceStub:
    """ Stands in for a service whose channel has destinations.
    """
    email: 'EMailAPIRecorder | None'

    def __init__(self, request_payload:'any_', *, has_email:'bool'=True) -> 'None':

        self.cid = CID
        self.request = RequestStub(request_payload)
        self.server = ServerStub()

        self.rest = RESTFacadeRecorder()
        self.mllp = MLLPFacadeRecorder()
        self.fhir = FHIRFacadeRecorder()

        # A server with the e-mail component turned off has no such facade at all
        if has_email:
            self.email = EMailAPIRecorder()
        else:
            self.email = None

        self.destination = DestinationFacade()
        self.destination.init(request_payload)

# ################################################################################################################################
# ################################################################################################################################
