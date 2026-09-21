# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# lxml
from lxml import etree

# Zato
from zato.common.json_ import loads
from zato.common.pubsub.outgoing import Key_Data, Key_Headers, Key_Operation, SendRejected
from zato.common.soap.client import SOAPClient
from zato.common.soap.common import Content_Type as SOAP_Content_Type, Envelope_NS, SOAP_Action_Header, SOAPException, \
    SOAPFault, SOAPVersion
from zato.common.soap.message import parse as parse_soap_message, serialize as serialize_soap_message
from zato.common.util.xml_.core import parse_xml
from zato.server.connection.http_soap.invocation import build_soap_jsonata_context, evaluate_soap_headers, \
    maybe_run_fault_callback, maybe_run_soap_callback, merge_declarative_soap_request
from zato.server.connection.http_soap.outgoing.common import logger, _queue, _retry

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.outgoing import OutgoingPublisher, SendResult
    from zato.common.soap.message import SOAPMessage
    from zato.common.typing_ import any_, dictnone, stranydict, strbytes, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# A queued message travels as the XML of its operation element, which is what the Dashboard's invoke dialog takes as a body too
_message_encoding = 'unicode'

# ################################################################################################################################
# ################################################################################################################################

def message_to_text(message:'SOAPMessage', operation:'str') -> 'str':
    """ The XML of a message under its operation element, as a queue stores it.
    """
    element = serialize_soap_message(message, operation)

    out = etree.tostring(element, encoding=_message_encoding)
    return out

# ################################################################################################################################

def message_from_text(data:'str') -> 'SOAPMessage':
    """ A message out of the XML of its operation element - the element's children, under the element's namespace.
    """
    root = parse_xml(data.encode('utf-8'))

    out = parse_soap_message(root)

    # Parsing strips namespaces, so the one the operation element went out under is put back on the message
    namespace = etree.QName(root).namespace

    if namespace:
        out.namespace = namespace

    return out

# ################################################################################################################################
# ################################################################################################################################

# The envelope each SOAP version's legacy string-formatting path wraps the outgoing data in.
# Templates are shared by every connection, so they live here rather than being rebuilt per wrapper.
SOAP_Envelope_Template = {

    SOAPVersion.V11: """<?xml version="1.0" encoding="utf-8"?>
<s11:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:s11="%s">
  {header}
  <s11:Body>{data}</s11:Body>
</s11:Envelope>""" % (Envelope_NS[SOAPVersion.V11],),

    SOAPVersion.V12: """<?xml version="1.0" encoding="utf-8"?>
<s12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:s12="%s">{header}
  <s12:Body>{data}</s12:Body>
</s12:Envelope>""" % (Envelope_NS[SOAPVersion.V12],),
}

# ################################################################################################################################
# ################################################################################################################################

class SOAPMixin:
    """ The SOAP side of an outgoing connection - the envelope its data travels in, the SOAPAction header,
    the SOAP client the wrapper keeps and the operation-based invocation.
    """

    publisher: 'OutgoingPublisher'

    def _add_soap_action(self, headers:'strstrdict') -> 'None':
        """ Adds the SOAPAction header a SOAP 1.1 request carries.

        Only 1.1 has this header - 1.2 replaced it with a Content-Type parameter, and sending it to
        a 1.2 endpoint anyway is at best ignored and at worst a routing decision made on a header
        that version does not define. The value is quoted because SOAP 1.1 defines it as a quoted
        string, and an unquoted one is what a strict peer rejects.
        """
        if self.config['soap_version'] != SOAPVersion.V11:
            return

        # A connection with no action configured sends no header at all
        soap_action = self.config['soap_action']

        if not soap_action:
            return

        headers[SOAP_Action_Header] = f'"{soap_action}"'

# ################################################################################################################################

    def _soap_data(self, data:'strbytes', headers:'stranydict') -> 'tuple[strbytes, stranydict]':
        """ Wraps the data in a SOAP-specific messages and adds the headers required.
        """
        soap_version = self.config['soap_version']

        # The idea here is that even though there usually won't be the Content-Type
        # header provided by the user, we shouldn't overwrite it if one has been
        # actually passed in.
        if not headers.get('Content-Type'):
            headers['Content-Type'] = SOAP_Content_Type[soap_version]

        # The marker is looked for in the same kind of string the data is, there being no way to
        # search bytes for text or the other way around.
        if isinstance(data, bytes):
            has_envelope = b':Envelope' in data
        else:
            has_envelope = ':Envelope' in data

        # Data that arrives with an envelope of its own is left as it is - wrapping it again would
        # produce a body whose only child is another envelope.
        if has_envelope:
            out = data
        else:
            out = SOAP_Envelope_Template[soap_version].format(header='', data=data)

        return out, headers

# ################################################################################################################################

    def _new_soap_client(self) -> 'SOAPClient':
        """ Builds a SOAP client out of this connection's configuration - the transport details,
        the mutual-TLS material, the WS-Security definition and the body-credential mappings.
        """
        config:'stranydict' = {
            'address': self.address,
            'soap_version': self.config['soap_version'] or SOAPVersion.Default,
            'soap_action': self.config['soap_action'] or '',
            'timeout': self.config['timeout'],
            'validate_tls': self.config['validate_tls'],
            'content_type': self.config['content_type'],
            'tls_client_cert': self.config['tls_client_cert'],
            'tls_client_key': self.config['tls_client_key'],

            # An mTLS definition's pinned CA bundle is carried by the definition, not by the
            # connection, so it is only there when such a definition is attached.
            'ca_certs_path': self.config.get('ca_certs_path'),
            'use_ws_addressing': self.config['use_ws_addressing'] or False,
            'use_mtom': self.config['use_mtom'] or False,
            'wsa_action': self.config['wsa_action'],
            'wsa_to': self.config['wsa_to'],
            'wsa_reply_to': self.config['wsa_reply_to'],
        }

        # The retry settings live in the connection's opaque attributes and the client runs the
        # loop that reads them, so each one that the connection carries is handed over by name.
        for name in _retry.FieldList:
            config[name] = self.config[name]

        # With the queue switch on, the retry fields drive the connection's queue, so the client makes each attempt once
        if self.config[_queue.Field_Use_Queue]:
            config[_retry.Field_Max_Retries] = 0

        # Declarative WS-Addressing values imply the headers are wanted even if the flag is off
        if config['wsa_action'] or config['wsa_to'] or config['wsa_reply_to']:
            config['use_ws_addressing'] = True

        # Body credentials pair the mapping rows with the username and password
        # of the security definition attached to the connection.
        if mappings := self.config['body_credentials']:
            if isinstance(mappings, str):
                mappings = loads(mappings)
            if mappings:
                config['body_credentials'] = {
                    'username': self.config['username'],
                    'password': self.config['password'],
                    'mappings': mappings,
                }

        # A WS-Security definition travels whole, with the connection-level password kept
        # authoritative so a password change reaches the client without a full reload.
        if security := self.config.get('security'):
            security = dict(security)
            if password := self.config['password']:
                security['password'] = password
            config['security'] = security

        out = SOAPClient(config)

        # The client records what it sends and receives - it is the layer where
        # the raw envelope bytes exist in both directions.
        if self.needs_audit:
            out.audit_callback = self._insert_audit_event

        return out

# ################################################################################################################################

    def _get_soap_client(self) -> 'SOAPClient':
        """ Returns the underlying SOAP client, building it on first access.
        """
        if self._soap_client is None:
            self._soap_client = self._new_soap_client()
        return self._soap_client

    soap_client = property(fget=_get_soap_client, doc=_get_soap_client.__doc__)

# ################################################################################################################################

    def _invoke_soap(self, cid:'str', operation:'str', message:'SOAPMessage', soap_headers:'dictnone') -> 'SOAPMessage':
        """ One call of an operation over the wire, with the callbacks the connection configures.
        """
        logger.info('SOAP out -> cid=%s; %s %s; name:%s', cid, operation, self.address, self.config['name'])

        try:
            response = self.soap_client.invoke(operation, message, cid=cid, soap_headers=soap_headers)
        except SOAPFault as fault:

            # The callback hears about the fault first, then the caller sees it re-raised unchanged
            maybe_run_fault_callback(self.server, self.config, cid, fault)
            raise

        # Deliver the response-mapped result to the configured callback in the background,
        # a no-op for connections without callback config
        maybe_run_soap_callback(self.server, self.config, cid, response)

        return response

# ################################################################################################################################

    def _send_or_queue_soap(
        self,
        cid,          # type: str
        operation,    # type: str
        message,      # type: SOAPMessage
        soap_headers, # type: dictnone
    ) -> 'SendResult':
        """ An invocation with the queue switch on - a fault or any other answer that is not a response is a rejection.
        """
        if soap_headers is None:
            soap_headers = {}

        request = {
            Key_Operation: operation,
            Key_Data: message_to_text(message, operation),
            Key_Headers: soap_headers,
        }

        def attempt() -> 'SOAPMessage':
            try:
                out = self._invoke_soap(cid, operation, message, soap_headers)
            except SOAPException as e:
                raise SendRejected(str(e), e)

            return out

        out = self.publisher.send_or_queue(cid, request, attempt)
        return out

# ################################################################################################################################

    def invoke(self, cid:'str', operation:'str'='', message:'any_'=None) -> 'any_':
        """ Invokes a SOAP operation over this connection - the message is a dot-accessed
        SOAPMessage that becomes the operation element in soap:Body, and the parsed response
        body comes back the same way, with faults raised as SOAPFault. An operation or message
        the caller does not pass comes from the connection's declarative invocation profile.
        With the queue switch on, what comes back is a SendResult and nothing is raised.
        """
        self._enforce_is_active()

        # Fill in the blanks from the connection's declarative invocation profile - explicit
        # arguments always win and JSONata values are evaluated at call time against
        # the message the caller passed in.
        context = build_soap_jsonata_context(message)
        operation, message = merge_declarative_soap_request(self.config, operation, message, context)
        soap_headers = evaluate_soap_headers(self.config, context)

        if self.config[_queue.Field_Use_Queue]:
            out = self._send_or_queue_soap(cid, operation, message, soap_headers)
        else:
            out = self._invoke_soap(cid, operation, message, soap_headers)

        return out

# ################################################################################################################################

    def send_soap_from_queue(self, cid:'str', request:'stranydict') -> 'SOAPMessage':
        """ Makes one attempt to deliver an invocation the queue holds, raising when the endpoint turned it down.
        """
        operation = request[Key_Operation]
        message = message_from_text(request[Key_Data])

        soap_headers = request[Key_Headers]

        if not soap_headers:
            soap_headers = None

        out = self._invoke_soap(cid, operation, message, soap_headers)
        return out

# ################################################################################################################################

    def invoke_ebxml(self, cid:'str', info:'any_', parts:'any_', sign:'bool'=False, encrypt:'bool'=False) -> 'any_':
        """ Sends an ebXML Message Service message over this connection - payloads travel
        as MIME parts, each optionally signed and encrypted for the recipient. Returns the
        reply's EbXMLInfo, whose attachments are the reply's own payload parts.
        """
        self._enforce_is_active()

        logger.info('ebXML out -> cid=%s; %s; name:%s', cid, self.address, self.config['name'])

        return self.soap_client.invoke_ebxml(info, parts, sign=sign, encrypt=encrypt, cid=cid)

# ################################################################################################################################
# ################################################################################################################################
