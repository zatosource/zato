# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.b2b.ebms2.common import EbMS2Exception, ErrorCode, MSHService, MessageOrderSemantics, PerMessage, \
    SyncReplyMode, Direction

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime, timedelta
    from cryptography.x509 import Certificate as X509Certificate
    from zato.common.b2b.ebms2.agreement_packaging import comment_list, packaging_list, simple_part_list
    from zato.common.b2b.ebms2.common import party_id_list
    from zato.common.typing_ import intnone, strlist, strstrdict
    from zato.common.util.xml_.keystore import certificate_list
    certificate_list = certificate_list
    comment_list = comment_list
    packaging_list = packaging_list
    simple_part_list = simple_part_list
    datetime = datetime
    intnone = intnone
    party_id_list = party_id_list
    strlist = strlist
    strstrdict = strstrdict
    timedelta = timedelta
    X509Certificate = X509Certificate

# ################################################################################################################################
# ################################################################################################################################

class ActionBindingKind:
    """ The two kinds of action binding of a service binding.
    """
    Can_Send    = 'CanSend'
    Can_Receive = 'CanReceive'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Duration:
    """ An xsd:duration from an agreement - the text it was written as, and the period it stands for.
    """
    text:  str
    value: 'timedelta'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PartyRef:
    href:            str
    ref_type:        str = ''
    schema_location: str = ''

# ################################################################################################################################

@dataclass(init=False)
class CPACertificate:
    """ A certificate an agreement names by its certId, with the chain its KeyInfo holds, the leaf first.
    """
    cert_id: str
    chain:   'certificate_list'

    @property
    def leaf(self) -> 'X509Certificate':
        out = self.chain[0]
        return out

# ################################################################################################################################

@dataclass(init=False)
class SecurityDetails:
    """ A set of trust anchors an agreement names by its securityId.
    """
    security_id:            str
    anchor_certificate_ids: 'strlist'

# ################################################################################################################################

@dataclass(init=False)
class Protocol:
    """ A protocol name with its optional version, such as HTTP 1.1 or TLS 1.2.
    """
    name:    str
    version: str = ''

# ################################################################################################################################

@dataclass(init=False)
class TransportSecurity:
    """ The transport security of one side of a transport - the protocol, the certificate the side
    presents and the trust anchors it validates the other side against.
    """
    protocol:            'Protocol'
    certificate_id:      str = ''
    security_details_id: str = ''

# ################################################################################################################################

@dataclass(init=False)
class Endpoint:
    uri:           str
    endpoint_type: str = 'allPurpose'

endpoint_list = list[Endpoint]

# ################################################################################################################################

@dataclass(init=False)
class Transport:
    """ How a party sends and receives messages on the wire.
    """
    transport_id: str

    sender_protocol: 'Protocol | None' = None
    client_security: 'TransportSecurity | None' = None

    receiver_protocol: 'Protocol | None' = None
    endpoints:         'endpoint_list'
    server_security:   'TransportSecurity | None' = None

    def __init__(self) -> 'None':
        self.endpoints = []

    @property
    def endpoint_uri(self) -> 'str':
        """ The address messages to this transport are sent to.
        """
        first = self.endpoints[0]

        out = first.uri
        return out

# ################################################################################################################################

@dataclass(init=False)
class ReliableMessaging:
    retries:        'intnone' = None
    retry_interval: 'Duration | None' = None
    message_order:  str = MessageOrderSemantics.Not_Guaranteed

# ################################################################################################################################

@dataclass(init=False)
class NonRepudiation:
    """ The signing requirements of one side of a document exchange.
    """
    protocol:             'Protocol'
    hash_function:        str
    signature_algorithms: 'strlist'

    # The certificate the sender signs with, named by a sender binding.
    signing_certificate_id: str = ''

    # The trust anchors the receiver validates signatures against, named by a receiver binding.
    signing_security_details_id: str = ''

# ################################################################################################################################

@dataclass(init=False)
class DocExchangeBinding:
    """ The sender or the receiver binding of a document exchange.
    """
    version:           str
    reliable_messaging: 'ReliableMessaging | None' = None
    persist_duration:  'Duration | None' = None
    non_repudiation:   'NonRepudiation | None' = None

# ################################################################################################################################

@dataclass(init=False)
class DocExchange:
    doc_exchange_id: str
    sender_binding:   'DocExchangeBinding | None' = None
    receiver_binding: 'DocExchangeBinding | None' = None

# ################################################################################################################################

@dataclass(init=False)
class MessagingCharacteristics:
    sync_reply_mode:         str = SyncReplyMode.No_Reply
    ack_requested:           str = PerMessage.Per_Message
    ack_signature_requested: str = PerMessage.Per_Message
    duplicate_elimination:   str = PerMessage.Per_Message
    actor:                   str = ''

# ################################################################################################################################

@dataclass(init=False)
class DeliveryChannel:
    """ A delivery channel with the transport and the document exchange its IDREFs name.
    """
    channel_id:      str
    transport_id:    str
    doc_exchange_id: str
    characteristics: 'MessagingCharacteristics'

    transport:    'Transport'
    doc_exchange: 'DocExchange'

# ################################################################################################################################

delivery_channel_list = list[DeliveryChannel]

@dataclass(init=False)
class ActionBinding:
    """ A CanSend or a CanReceive of a service binding, with the delivery channels its IDREFs name.
    """
    kind:       str
    binding_id: str
    action:     str
    package_id: str

    # The attributes of BusinessTransactionCharacteristics.
    characteristics: 'strstrdict'

    channel_ids: 'strlist'
    channels:    'delivery_channel_list'

    # The id of the matching action binding of the other party.
    other_party_binding_id: str = ''

    # The service of the service binding this action binding belongs to, and the role the party has in it.
    service:      str
    service_type: str = ''
    role_name:    str = ''

    # The CanReceive elements nested in a CanSend, or the CanSend elements nested in a CanReceive.
    nested: 'action_binding_list'

    def __init__(self) -> 'None':
        self.characteristics = {}
        self.channel_ids = []
        self.channels = []
        self.nested = []

    @property
    def channel(self) -> 'DeliveryChannel':
        """ The delivery channel the binding uses - the first one it names.
        """
        out = self.channels[0]
        return out

action_binding_list = list[ActionBinding]

# ################################################################################################################################

@dataclass(init=False)
class ServiceBinding:
    service:      str
    service_type: str = ''
    bindings:     'action_binding_list'

    def __init__(self) -> 'None':
        self.bindings = []

# ################################################################################################################################

@dataclass(init=False)
class CollaborationRole:
    process_name:    str
    process_version: str
    process_href:    str
    process_uuid:    str = ''
    role_name:       str
    role_href:       str

    application_certificate_ids:     'strlist'
    application_security_details_id: str = ''

    service_binding: 'ServiceBinding'

    def __init__(self) -> 'None':
        self.application_certificate_ids = []

# ################################################################################################################################

@dataclass(init=False)
class OverrideMshActionBinding:
    action:     str
    channel_id: str

# ################################################################################################################################

collaboration_role_list = list[CollaborationRole]
cpa_certificate_list = list[CPACertificate]
override_list = list[OverrideMshActionBinding]
party_ref_list = list[PartyRef]
security_details_list = list[SecurityDetails]
transport_list = list[Transport]
doc_exchange_list = list[DocExchange]

@dataclass(init=False)
class Party:
    """ One PartyInfo of an agreement.
    """
    party_name: str
    party_ids:  'party_id_list'
    party_refs: 'party_ref_list'
    roles:      'collaboration_role_list'

    certificates:      'cpa_certificate_list'
    security_details:  'security_details_list'
    delivery_channels: 'delivery_channel_list'
    transports:        'transport_list'
    doc_exchanges:     'doc_exchange_list'
    overrides:         'override_list'

    default_msh_channel_id: str
    default_msh_package_id: str

    def __init__(self) -> 'None':
        self.party_ids = []
        self.party_refs = []
        self.roles = []
        self.certificates = []
        self.security_details = []
        self.delivery_channels = []
        self.transports = []
        self.doc_exchanges = []
        self.overrides = []

# ################################################################################################################################

    def matches(self, party_ids:'party_id_list') -> 'bool':
        """ Says whether any of the given identifiers is one of this party's.
        """
        for party_id in party_ids:
            for own_party_id in self.party_ids:
                if own_party_id.matches(party_id):
                    out = True
                    break
            else:
                continue
            break
        else:
            out = False

        return out

# ################################################################################################################################

    def get_channel(self, channel_id:'str') -> 'DeliveryChannel':
        for channel in self.delivery_channels:
            if channel.channel_id == channel_id:
                out = channel
                break
        else:
            raise EbMS2Exception(ErrorCode.Value_Not_Recognized, f'Unknown delivery channel `{channel_id}`')

        return out

# ################################################################################################################################

    def msh_channel(self, action:'str') -> 'DeliveryChannel':
        """ Returns the delivery channel of a message service handler action, which is the channel of
        its override binding when there is one, or the party's default channel.
        """
        for override in self.overrides:
            if override.action == action:
                channel_id = override.channel_id
                break
        else:
            channel_id = self.default_msh_channel_id

        out = self.get_channel(channel_id)
        return out

# ################################################################################################################################

    def find_bindings(self, kind:'str', service:'str', service_type:'str', action:'str') -> 'action_binding_list':
        """ Returns the action bindings of the given kind for a service and an action, nested ones included.
        """
        out:'action_binding_list' = []

        for role in self.roles:
            service_binding = role.service_binding

            if service_binding.service == service:
                if service_binding.service_type == service_type:
                    _collect_bindings(service_binding.bindings, kind, action, out)

        return out

# ################################################################################################################################

    def has_service(self, service:'str', service_type:'str') -> 'bool':
        for role in self.roles:
            service_binding = role.service_binding
            if service_binding.service == service:
                if service_binding.service_type == service_type:
                    out = True
                    break
        else:
            out = False

        return out

# ################################################################################################################################
# ################################################################################################################################

def _collect_bindings(bindings:'action_binding_list', kind:'str', action:'str', out:'action_binding_list') -> 'None':
    """ Appends to out each binding, at any depth of nesting, of the given kind and action.
    """
    for binding in bindings:

        if binding.kind == kind:
            if binding.action == action:
                out.append(binding)

        _collect_bindings(binding.nested, kind, action, out)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Binding:
    """ How one message between two parties of an agreement is exchanged - the sender's CanSend and its delivery channel,
    and the receiver's CanReceive and its delivery channel. For the messages of the message service handler itself,
    the action bindings are absent and the channels are the parties' message service handler channels.
    """
    agreement:    'Agreement'
    from_party:   'Party'
    to_party:     'Party'
    service:      str
    service_type: str = ''
    action:       str

    send_binding:    'ActionBinding | None' = None
    receive_binding: 'ActionBinding | None' = None

    send_channel:    'DeliveryChannel'
    receive_channel: 'DeliveryChannel'

    @property
    def sender_binding(self) -> 'DocExchangeBinding | None':
        """ The sender side of the sender's document exchange - reliable messaging and signing.
        """
        out = self.send_channel.doc_exchange.sender_binding
        return out

    @property
    def receiver_binding(self) -> 'DocExchangeBinding | None':
        """ The receiver side of the receiver's document exchange - persistence and acknowledgment signing.
        """
        out = self.receive_channel.doc_exchange.receiver_binding
        return out

    @property
    def characteristics(self) -> 'MessagingCharacteristics':
        """ The messaging characteristics the receiver's channel requires.
        """
        out = self.receive_channel.characteristics
        return out

    @property
    def is_msh(self) -> 'bool':
        out = self.service == MSHService.Service
        return out

# ################################################################################################################################
# ################################################################################################################################

party_list = list[Party]

@dataclass(init=False)
class Agreement:
    """ A collaboration protocol agreement between two parties.
    """
    cpa_id:  str
    version: str
    status:  str
    start:   'datetime'
    end:     'datetime'

    invocation_limit:         'intnone' = None
    concurrent_conversations: 'intnone' = None

    parties:      'party_list'
    simple_parts: 'simple_part_list'
    packagings:   'packaging_list'
    comments:     'comment_list'

    def __init__(self) -> 'None':
        self.parties = []
        self.simple_parts = []
        self.packagings = []
        self.comments = []

# ################################################################################################################################

    def find_party(self, party_ids:'party_id_list', location:'str') -> 'Party':
        """ Returns the party any of the given identifiers belongs to.
        """
        for party in self.parties:
            if party.matches(party_ids):
                out = party
                break
        else:
            raise EbMS2Exception(ErrorCode.Value_Not_Recognized, 'Party is not part of the agreement', location)

        return out

# ################################################################################################################################

    def other_party(self, party:'Party') -> 'Party':
        for candidate in self.parties:
            if candidate is not party:
                out = candidate
                break
        else:
            raise EbMS2Exception(ErrorCode.Inconsistent, 'Agreement has a single party')

        return out

# ################################################################################################################################

    def get_certificate(self, cert_id:'str') -> 'CPACertificate':
        """ Returns the certificate with the given certId, from whichever party declares it.
        """
        for party in self.parties:
            for certificate in party.certificates:
                if certificate.cert_id == cert_id:
                    out = certificate
                    break
            else:
                continue
            break
        else:
            raise EbMS2Exception(ErrorCode.Value_Not_Recognized, f'Unknown certificate `{cert_id}`')

        return out

# ################################################################################################################################

    def get_anchor_certificates(self, security_id:'str') -> 'certificate_list':
        """ Returns the trust anchor certificates of the security details with the given securityId.
        """
        out:'certificate_list' = []

        for party in self.parties:
            for details in party.security_details:
                if details.security_id == security_id:
                    for cert_id in details.anchor_certificate_ids:
                        certificate = self.get_certificate(cert_id)
                        out.append(certificate.leaf)

        return out

# ################################################################################################################################

    def resolve(
        self,
        from_party_ids:'party_id_list',
        to_party_ids:'party_id_list',
        service:'str',
        service_type:'str',
        action:'str',
        direction:'str',
        ) -> 'Binding':
        """ Returns how a message from one party to the other is exchanged under this agreement.
        The direction says which side the local party is on and decides whose bindings are checked first,
        so the error points at the local party's own configuration before the partner's.
        """

        # Our response to produce
        out = Binding()
        out.agreement = self
        out.service = service
        out.service_type = service_type
        out.action = action

        out.from_party = self.find_party(from_party_ids, 'eb:From')
        out.to_party = self.find_party(to_party_ids, 'eb:To')

        if out.from_party is out.to_party:
            raise EbMS2Exception(ErrorCode.Inconsistent, 'The sender and the receiver are the same party', 'eb:To')

        # The messages of the message service handler use the channels that each party designates for them ..
        if service == MSHService.Service:
            out.send_channel = out.from_party.msh_channel(action)
            out.receive_channel = out.to_party.msh_channel(action)

        # .. while business messages need a matching binding on both sides.
        else:
            _resolve_action_bindings(out, direction)

        return out

# ################################################################################################################################
# ################################################################################################################################

def _resolve_action_bindings(out:'Binding', direction:'str') -> 'None':
    """ Fills in the action bindings and the delivery channels of a business message.
    """
    service = out.service
    service_type = out.service_type
    action = out.action

    # Each party is to have the service at all ..
    for party in (out.from_party, out.to_party):
        if not party.has_service(service, service_type):
            raise EbMS2Exception(ErrorCode.Value_Not_Recognized, f'Service `{service}` is not in the agreement', 'eb:Service')

    send_bindings = out.from_party.find_bindings(ActionBindingKind.Can_Send, service, service_type, action)
    receive_bindings = out.to_party.find_bindings(ActionBindingKind.Can_Receive, service, service_type, action)

    # .. the local party's own side is checked first ..
    if direction == Direction.Receive:
        checks = ((receive_bindings, 'receive'), (send_bindings, 'send'))
    else:
        checks = ((send_bindings, 'send'), (receive_bindings, 'receive'))

    # .. and an action that exists for the service but not in this direction is one the agreement does not support.
    for bindings, verb in checks:
        if not bindings:
            raise EbMS2Exception(
                ErrorCode.Not_Supported, f'Action `{action}` of service `{service}` cannot {verb} in this direction', 'eb:Action')

    send_binding = send_bindings[0]

    # The receiver's binding is the one the sender's names, if it names one.
    for receive_binding in receive_bindings:
        if receive_binding.binding_id == send_binding.other_party_binding_id:
            break
    else:
        receive_binding = receive_bindings[0]

    out.send_binding = send_binding
    out.receive_binding = receive_binding
    out.send_channel = send_binding.channel
    out.receive_channel = receive_binding.channel

# ################################################################################################################################
# ################################################################################################################################
