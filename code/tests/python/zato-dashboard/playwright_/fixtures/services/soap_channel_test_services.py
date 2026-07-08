# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from hashlib import sha256
from json import dumps, loads

# Zato
from zato.common.exception import BadRequest
from zato.common.soap.message import SOAPMessage
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class ChannelFixturesReadinessProbe(Service):
    """ Confirms that this module's services deployed during server boot -
    tests keep invoking it through the IDE until it answers.
    """

    name = 'test.soap.channel.ping'

    def handle(self):

        # The IDE invoker delivers the payload as a raw JSON string.
        request = self.request.payload
        if isinstance(request, str):
            request = loads(request)

        out = {'is_ready': True}

        self.response.payload = dumps(out)
        self.response.content_type = 'application/json'

# ################################################################################################################################
# ################################################################################################################################

class SubmitSingleMessage(Service):
    """ A CDC IIS-style registry endpoint - reads the incoming HL7 message through
    dot access and answers with an HL7 ACK whose control id echoes the request's.
    """

    name = 'test.soap.channel.registry'

    def handle(self):

        # The channel already unwrapped the envelope - this is the operation
        # element from soap:Body as a dot-accessed SOAPMessage.
        request = self.request.payload

        # A submission without a facility is rejected - the channel turns this
        # into a Sender fault of the request's SOAP version.
        facility = request.facilityID
        if not facility:
            raise BadRequest(self.cid, 'facilityID is required')

        # MSH field 10 of the incoming message is its control id and the ACK echoes it.
        hl7_message = request.hl7Message
        message_control_id = hl7_message.split('|')[9]

        acknowledgment = 'MSH|^~\\&|IIS|STATE|MYAPP|{0}|20260115||ACK^V04^ACK|{1}|P|2.5.1\rMSA|AA|{1}'.format(
            facility, message_control_id)

        # The channel wraps this into <submitSingleMessageResponse> inside
        # an envelope of the request's SOAP version.
        response = SOAPMessage()
        response.namespace = 'urn:cdc:iisb:2014'
        setattr(response, 'return', acknowledgment)

        self.response.payload = response

# ################################################################################################################################
# ################################################################################################################################

class ProvideAndRegisterDocumentSet(Service):
    """ An IHE ITI-41-style document repository endpoint - binary content is just
    bytes in both directions, whatever the packaging on the wire was.
    """

    name = 'test.soap.channel.documents'

    def handle(self):

        request = self.request.payload

        # An xop:Include reference was already resolved - this reads as bytes,
        # exactly as if the sender had inlined it.
        document = request.Document

        # The raw MIME parts are also available when a service wants them as parts.
        attachments = self.request.soap.attachments

        # The receipt is the document's SHA-256 digest - with MTOM enabled on
        # the channel, the bytes leave as an MTOM package, otherwise inline.
        response = SOAPMessage()
        response.namespace = 'urn:ihe:iti:xds-b:2007'
        response.status = 'urn:ihe:iti:2007:ResponseStatusType:Success'
        response.documentLength = len(document)
        response.partCount = len(attachments)
        response.receipt = sha256(document).digest()

        self.response.payload = response

# ################################################################################################################################
# ################################################################################################################################

class ConnectivityTest(Service):
    """ Behind a SOAP channel - echoes whatever arrives together with the protocol
    context the channel established, so loopback tests can assert the whole stack.
    """

    name = 'test.soap.channel.echo'

    def handle(self):

        request = self.request.payload
        soap = self.request.soap

        response = SOAPMessage()
        response.echoed = request.echoBack
        response.observedVersion = soap.soap_version
        response.observedOperation = soap.operation

        self.response.payload = response

# ################################################################################################################################
# ################################################################################################################################

class ProtectedEndpoint(Service):
    """ Behind a UsernameToken-protected channel - reports what the channel's
    WS-Security enforcement established about the message.
    """

    name = 'test.soap.channel.protected'

    def handle(self):

        security = self.request.soap.security

        response = SOAPMessage()
        response.status = 'ok'
        response.verifiedMode = security.mode
        response.verifiedUser = security.username

        self.response.payload = response

# ################################################################################################################################
# ################################################################################################################################

class AlwaysFailing(Service):
    """ Raises an ordinary server-side exception - the channel must turn it into
    a Receiver fault with no traceback ever reaching the caller.
    """

    name = 'test.soap.channel.faulty'

    def handle(self):
        raise RuntimeError('An internal detail that must never reach the wire')

# ################################################################################################################################
# ################################################################################################################################
