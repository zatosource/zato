# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from operator import itemgetter

# lxml
from lxml import etree

# requests
import requests

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome
from zato.common.crypto.api import is_string_equal
from zato.common.soap.addressing import add_addressing, AddressingInfo, Fault_Invalid_Addressing_Header, parse_addressing
from zato.common.soap.common import Action_Parameter, Content_Type, NS, SOAP_Action_Header, SOAPAddressingException, \
    SOAPException, SOAPVersion
from zato.common.soap.ebxml import build_message as build_ebxml_message, encrypt_payload, parse_message_header, sign_payload
from zato.common.soap.envelope import attach_body, build_envelope, get_header, get_security_header, parse_body, \
    parse_envelope, raise_for_fault, to_bytes
from zato.common.soap.message import SOAPMessage, to_lexical
from zato.common.soap.mtom import build_mtom, build_swa, parse_message, to_bytes_map
from zato.common.soap.security.wss import apply_wss, keystore_from_config
from zato.common.util.xml_.core import qname
from zato.common.util.xml_.keystore import new_keystore

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, anytuple, stranydict, strdictnone, strnone
    from zato.common.util.xml_.keystore import Keystore
    from zato.common.util.xml_.mime_ import part_list
    any_ = any_
    anydict = anydict
    anylist = anylist
    anytuple = anytuple
    Keystore = Keystore
    part_list = part_list
    stranydict = stranydict
    strdictnone = strdictnone
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# The lowest position a body credential mapping may name. Positions are 1-based, matching what the
# dashboard shows, so 1 means the operation's first child.
Minimum_Credential_Position = 1

# What body credentials look like when a connection enables them without spelling out
# a mapping of its own - one element per credential, each named after what it carries.
Default_Body_Credential_Mappings = [
    {'name': 'username', 'source': 'username'},
    {'name': 'password', 'source': 'password'},
]

# ################################################################################################################################
# ################################################################################################################################

class SOAPClient:
    """ A reusable SOAP client - one connection's worth of configuration in, dot-accessed
    messages out. It builds the operation from a SOAPMessage, injects whatever credentials,
    addressing and packaging the configuration calls for, sends the request over HTTP(S)
    with optional mutual TLS, and parses the reply back into a SOAPMessage.
    """
    def __init__(self, config:'stranydict') -> 'None':
        self.config = config

        self.address      = config['address']
        self.soap_version = config.get('soap_version', SOAPVersion.V12)
        self.soap_action  = config.get('soap_action', '')
        self.timeout      = float(config.get('timeout') or 0) or None
        self.content_type = config.get('content_type')
        self.ping_method  = config.get('ping_method', 'HEAD')

        # WS-Security, WS-Addressing, MTOM and body-credential injection are each optional.
        self.security         = config.get('security')
        self.use_ws_addressing = config.get('use_ws_addressing', False)
        self.use_mtom          = config.get('use_mtom', False)
        self.body_credentials  = config.get('body_credentials')

        self.session = requests.Session()

        # An owning connection wrapper may plug the client into the audit log here -
        # standalone clients, e.g. in tests, run without one.
        self.audit_callback = None

# ################################################################################################################################

    def _verify(self) -> 'any_':
        """ Returns what to pass to requests as its TLS verification - True to verify against
        the system trust store, False to skip it, or a path to a CA bundle to verify against.
        """
        out = self.config.get('validate_tls', True)
        return out

# ################################################################################################################################

    def _client_cert(self) -> 'any_':
        """ Returns what to pass to requests as the client certificate - a single PEM path holding
        both the certificate and its key, a (certificate, key) path pair, or None.
        """
        client_cert = self.config.get('tls_client_cert')

        if not client_cert:
            return None

        if client_key := self.config.get('tls_client_key'):
            out = (client_cert, client_key)
        else:
            out = client_cert

        return out

# ################################################################################################################################

    def _content_type(self) -> 'str':
        """ Returns the Content-Type of a bare envelope of the configured SOAP version.
        """
        if self.content_type:
            out = self.content_type
        else:
            out = Content_Type[self.soap_version]

        return out

# ################################################################################################################################

    def _inject_body_credentials(self, operation:'any_') -> 'None':
        """ Injects the configured credentials as child elements of the operation element -
        by default as its first children in mapping order, or at explicit 1-based positions.
        The elements inherit the operation's namespace, so they sit in the message like any
        other field, which is what body-authenticated endpoints such as CDC IIS require.
        """
        namespace = None
        if operation.tag.startswith('{'):
            namespace = operation.tag[1:].partition('}')[0]

        mappings = self.body_credentials.get('mappings')
        if not mappings:
            mappings = Default_Body_Credential_Mappings

        # Rows without a position prepend in mapping order, positioned rows slot in afterwards.
        default_rows = []
        positioned_rows = []

        for row in mappings:
            position = row.get('position')

            if position is None:
                default_rows.append(row)
                continue

            # A position is 1-based, so anything below 1 is a configuration error. Left unchecked it
            # becomes a negative index, which lxml reads from the end of the children - a credential
            # that was meant to lead the message ends up trailing it, in a place the receiving
            # endpoint does not look, and the request fails authentication for no visible reason.
            if position < Minimum_Credential_Position:
                raise SOAPException(f'Body credential position must be at least '
                    f'{Minimum_Credential_Position}, not `{position}` -> `{row["name"]}`')

            positioned_rows.append(row)

        # The default rows go in ahead of whatever the operation already carries. They are built
        # first and inserted in one reversed pass at the front, so each one is placed without
        # walking past the elements the previous ones were placed at.
        default_elements = []

        for row in default_rows:
            default_elements.append(self._new_credential_element(row, namespace))

        for element in reversed(default_elements):
            operation.insert(0, element)

        positioned_rows.sort(key=itemgetter('position'))

        for row in positioned_rows:
            element = self._new_credential_element(row, namespace)
            operation.insert(row['position'] - 1, element)

# ################################################################################################################################

    def _new_credential_element(self, row:'anydict', namespace:'strnone') -> 'any_':
        """ Builds one credential element out of a mapping row and the configured credentials.
        """
        source = row.get('source') or row['name']
        value = self.body_credentials[source]

        if namespace:
            element = etree.Element(f'{{{namespace}}}{row["name"]}')
        else:
            element = etree.Element(row['name'])

        element.text = value

        return element

# ################################################################################################################################

    def _addressing_info(self) -> 'AddressingInfo':
        """ Builds the WS-Addressing headers an outgoing request needs - the Action defaults
        to the SOAPAction and the destination to the connection's address.
        """
        out = AddressingInfo()
        out.action = self.config.get('wsa_action') or self.soap_action
        out.to = self.config.get('wsa_to') or self.address
        out.reply_to = self.config.get('wsa_reply_to')

        return out

# ################################################################################################################################

    def _inject_soap_headers(self, envelope:'any_', soap_headers:'stranydict') -> 'None':
        """ Injects custom header elements into the envelope's soap:Header. A name in Clark
        notation, {namespace}Name, carries its own namespace, a plain name has none.
        """
        header = get_header(envelope)

        for name, value in soap_headers.items():
            element = etree.SubElement(header, name)
            element.text = value if isinstance(value, str) else to_lexical(value)

# ################################################################################################################################

    def _build_request(self, operation:'str', message:'SOAPMessage', soap_headers:'strdictnone'=None) -> 'anytuple':
        """ Builds the request body bytes and their Content-Type from a message - applying
        credential injection, custom headers, WS-Security, WS-Addressing and MTOM packaging as
        configured. Returns the body, its Content-Type and the wsa:MessageID the request went out
        under, which is None when the connection does not use WS-Addressing.
        """
        envelope = build_envelope(self.soap_version)

        # MTOM turns bytes values into xop:Include references and collects their bytes as parts.
        xop_parts:'part_list | None' = [] if self.use_mtom else None

        operation_element = attach_body(envelope, message, operation, xop_parts=xop_parts)

        # Body credentials go in before signing so a signature covers the final body.
        if self.body_credentials:
            self._inject_body_credentials(operation_element)

        # Custom headers go in before signing too, for the same reason.
        if soap_headers:
            self._inject_soap_headers(envelope, soap_headers)

        if self.security:
            apply_wss(envelope, self.security)

        # The id the request went out under is what the reply has to relate to.
        message_id = None

        if self.use_ws_addressing:
            message_id = add_addressing(envelope, self._addressing_info())

        envelope_bytes = to_bytes(envelope)

        # With parts collected, the request is an MTOM package, otherwise a bare envelope.
        if xop_parts:
            body, content_type = build_mtom(envelope_bytes, xop_parts, self.soap_version)
        else:
            body = envelope_bytes
            content_type = self._request_content_type()

        out = (body, content_type, message_id)
        return out

# ################################################################################################################################

    def _request_content_type(self) -> 'str':
        """ Returns the Content-Type for a bare-envelope request, carrying the SOAPAction
        as a parameter for SOAP 1.2 the way that version prescribes.
        """
        out = self._content_type()

        if self.soap_version == SOAPVersion.V12 and self.soap_action:
            out = f'{out}; {Action_Parameter}="{self.soap_action}"'

        return out

# ################################################################################################################################

    def _request_headers(self, content_type:'str') -> 'stranydict':
        """ Returns the request headers - the Content-Type plus a SOAPAction header for SOAP 1.1.
        """
        headers = {'Content-Type': content_type}

        # SOAP 1.1 carries the action in its own header, always quoted.
        if self.soap_version == SOAPVersion.V11:
            headers[SOAP_Action_Header] = f'"{self.soap_action}"'

        return headers

# ################################################################################################################################

    def _post(self, body:'bytes', content_type:'str') -> 'any_':
        """ Sends one request and returns the raw requests response.
        """
        headers = self._request_headers(content_type)

        out = self.session.post(
            self.address,
            data=body,
            headers=headers,
            verify=self._verify(),
            cert=self._client_cert(),
            timeout=self.timeout,
        )

        return out

# ################################################################################################################################

    def _parse_response(self, response:'any_', message_id:'strnone'=None) -> 'SOAPMessage':
        """ Parses a raw response into a SOAPMessage, resolving MTOM parts, raising SOAP faults,
        and exposing the WS-Addressing headers and attachments as reserved attributes.
        """
        envelope_bytes, parts = parse_message(response.content, response.headers.get('Content-Type', ''))

        envelope = parse_envelope(envelope_bytes)

        # A fault surfaces as the one SOAPFault exception before anything else is read.
        raise_for_fault(envelope)

        addressing = parse_addressing(envelope)

        if message_id:
            self._check_relates_to(addressing, message_id)

        parts_map = to_bytes_map(parts) if parts else None
        body = parse_body(envelope, parts_map)

        # The addressing headers and attachments ride along as reserved attributes a service may read.
        object.__setattr__(body, 'addressing', addressing)
        object.__setattr__(body, 'attachments', parts)

        return body

# ################################################################################################################################

    def _check_relates_to(self, addressing:'AddressingInfo', message_id:'str') -> 'None':
        """ Checks that a reply relates to the request that was actually sent.

        This is what makes an addressed exchange a correlated one. Without the check, a reply
        belonging to some other request - a stale one still in flight, or one an attacker chose -
        is accepted as the answer to this one, and the MessageID the request went to the trouble of
        carrying does nothing at all. A reply carrying no RelatesTo is a peer that does not
        implement the reply half of WS-Addressing, which is not something to fail over, so it is
        accepted and left to the caller to notice.
        """
        if addressing.relates_to is None:
            return

        if not is_string_equal(addressing.relates_to, message_id):
            raise SOAPAddressingException(
                f'Reply relates to `{addressing.relates_to}` rather than to `{message_id}`',
                [qname(NS.WSA, Fault_Invalid_Addressing_Header)],
            )

# ################################################################################################################################

    def _audited_post(self, cid:'str', endpoint:'str', body:'bytes', content_type:'str') -> 'any_':
        """ Sends one request through the audit log - the outgoing body, a transport-level
        failure and the raw response are each recorded before the caller parses anything,
        so fault envelopes are captured too. Returns the raw requests response.
        """

        # The request goes out exactly as recorded here ..
        if self.audit_callback:
            self.audit_callback(cid, AuditEvent.Request_Sent, endpoint, AuditOutcome.OK, body)

        try:
            out = self._post(body, content_type)
        except Exception as e:

            # .. a transport-level failure means no response ever arrived ..
            if self.audit_callback:
                self.audit_callback(cid, AuditEvent.Response_Received, endpoint, AuditOutcome.Error, str(e))

            # .. which the caller still needs to see.
            raise

        # .. a fault envelope arrives with an HTTP error status, hence the outcome from response.ok.
        if self.audit_callback:
            outcome = AuditOutcome.OK if out.ok else AuditOutcome.Error
            self.audit_callback(cid, AuditEvent.Response_Received, endpoint, outcome, out.content)

        return out

# ################################################################################################################################

    def invoke(self, operation:'str', message:'SOAPMessage', cid:'str'='', soap_headers:'strdictnone'=None) -> 'SOAPMessage':
        """ Invokes a SOAP operation - builds the request from the message, sends it and returns
        the parsed response body. The operation name becomes the single child of soap:Body.
        """
        body, content_type, message_id = self._build_request(operation, message, soap_headers)

        logger.info('SOAP out -> %s %s; len=%d', operation, self.address, len(body))

        response = self._audited_post(cid, f'{operation} {self.address}', body, content_type)

        logger.info('SOAP out <- %s; %s len=%d', operation, response.status_code, len(response.content))

        out = self._parse_response(response, message_id)
        return out

# ################################################################################################################################

    def invoke_ebxml(
        self,
        info:'any_',
        parts:'part_list',
        sign:'bool'=False,
        encrypt:'bool'=False,
        cid:'str'='',
        ) -> 'any_':
        """ Sends an ebXML Message Service message - the envelope carries the message header
        and a manifest, the payloads travel as MIME parts, each optionally signed and encrypted
        for the recipient. Returns the parsed EbXMLInfo of the reply.
        """
        keystore = self._ebxml_keystore()

        # Each payload is signed first so the signature covers the plaintext, then encrypted.
        signatures = []
        encrypted_keys = []

        for part in parts:
            if sign:
                signatures.append(sign_payload(part, keystore))
            if encrypt:
                encrypted_keys.append(encrypt_payload(part, keystore))

        envelope = build_ebxml_message(info, parts)

        # Any payload signatures and wrapped keys travel in the security header.
        if signatures or encrypted_keys:
            self._add_ebxml_security(envelope, signatures, encrypted_keys)

        envelope_bytes = to_bytes(envelope)
        body, content_type = build_swa(envelope_bytes, parts, SOAPVersion.V11)

        response = self._audited_post(cid, f'{info.action} {self.address}', body, content_type)

        response_envelope_bytes, _ = parse_message(response.content, response.headers.get('Content-Type', ''))
        response_envelope = parse_envelope(response_envelope_bytes)

        raise_for_fault(response_envelope)

        out = parse_message_header(response_envelope)
        return out

# ################################################################################################################################

    def _ebxml_keystore(self) -> 'Keystore':
        """ Returns the keystore an ebXML exchange uses - the WS-Security material of the
        connection when one is configured, otherwise an empty keystore.
        """
        if self.security:
            out = keystore_from_config(self.security)
        else:
            out = new_keystore()

        return out

# ################################################################################################################################

    def _add_ebxml_security(self, envelope:'any_', signatures:'anylist', encrypted_keys:'anylist') -> 'None':
        """ Places payload signatures and wrapped content keys in the message's security header.
        """
        security = get_security_header(envelope)

        for encrypted_key in encrypted_keys:
            security.append(encrypted_key)

        for signature in signatures:
            security.append(signature)

# ################################################################################################################################

    def ping(self) -> 'int':
        """ Pings the endpoint with the configured method and returns the HTTP status code.
        """
        response = self.session.request(
            self.ping_method,
            self.address,
            verify=self._verify(),
            cert=self._client_cert(),
            timeout=self.timeout,
        )

        out = response.status_code
        return out

# ################################################################################################################################

    def close(self) -> 'None':
        """ Releases the underlying HTTP session.
        """
        self.session.close()

# ################################################################################################################################
# ################################################################################################################################
