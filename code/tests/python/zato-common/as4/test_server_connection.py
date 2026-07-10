# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode

# cryptography
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

# httpx
import httpx

# pytest
import pytest

# Zato
import zato.server.connection.as4 as server_as4
from zato.common.api import AS4
from zato.common.as4.common import AS4Exception, Peppol_Not_Serviced
from zato.common.as4.discovery import lookup_endpoint
from zato.common.as4.outbound import build_push_message, new_part
from zato.common.as4.presets import get_document_type_preset
from zato.common.as4.profiles import new_edelivery1_pmode
from zato.server.connection.as4 import AS4ChannelRuntime, AS4Wrapper

# ################################################################################################################################
# ################################################################################################################################

Payload = b'<Invoice xmlns="urn:test"><Total>100</Total></Invoice>'
Endpoint_URL = 'https://as4.invalid/msh'

Serviced_Participant = '0192:991825827'
Other_Participant = '0088:7315458756324'

Document_Type_Name = 'peppol-bis-billing-3-invoice'

# The correlation id the outgoing wrapper calls are made with.
Test_CID = 'test-cid-outgoing'

# ################################################################################################################################
# ################################################################################################################################

def _key_pem(key):
    out = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()).decode('utf8')
    return out

# ################################################################################################################################

def _cert_pem(certificate):
    out = certificate.public_bytes(Encoding.PEM).decode('utf8')
    return out

# ################################################################################################################################
# ################################################################################################################################

class _FakeCache:
    """ A dict-backed stand-in for the server-wide cache the duplicate detection uses.
    """

    def __init__(self):
        self.data = {}

    def exists(self, key):
        out = key in self.data
        return out

    def set(self, key, value, expiry=None):
        _ = expiry
        self.data[key] = value

# ################################################################################################################################

class _FakePubSub:
    """ Records everything published to it.
    """

    def __init__(self):
        self.published = []

    def publish(self, topic_name, message, cid=None, correl_id=None):
        self.published.append((topic_name, message, cid, correl_id))

# ################################################################################################################################

class _FakeConfigManager:

    def __init__(self):
        self.cache_api = _FakeCache()

# ################################################################################################################################

class _FakeServer:
    """ Just enough of a server for the wrapper and the channel runtime to work offline.
    """

    def __init__(self):
        self.config_manager = _FakeConfigManager()
        self.pubsub_redis = _FakePubSub()
        self.invoked = []

    def decrypt(self, value):
        return value

    def invoke(self, service_name, message):
        self.invoked.append((service_name, message))

# ################################################################################################################################
# ################################################################################################################################

def _keystore_config(own, peer):
    """ The pasted-PEM keystore fields of one party, trusting the other one.
    """
    out = {
        'as4_signing_key': _key_pem(own.signing_key),
        'as4_signing_cert_chain': _cert_pem(own.signing_certificate_chain[0]),
        'as4_decryption_key': _key_pem(own.decryption_key),
        'as4_peer_signing_cert': _cert_pem(peer.signing_certificate_chain[0]),
        'as4_peer_encryption_cert': _cert_pem(peer.signing_certificate_chain[0]),
        'as4_trust_anchors': '',
    }
    return out

# ################################################################################################################################

def _outgoing_config(parties, profile):
    """ The configuration of one outgoing AS4 connection, the way the wrapper receives it.
    """
    out = {
        'name': 'Test Outgoing',
        'is_active': True,
        'address_host': 'https://as4.invalid',
        'address_url_path': '/msh',
        'timeout': 10,
        'validate_tls': True,
        'as4_profile': profile,
        'as4_from_party': 'party-a',
        'as4_to_party': 'party-b',
        'as4_service': 'urn:test:service',
        'as4_action': 'SubmitInvoice',
        'as4_agreement': '',
        'as4_mpc': '',
        'as4_original_sender': Serviced_Participant,
        'as4_final_recipient': '',
        'as4_sml_domain': 'acc.edelivery.tech.ec.europa.eu',
    }
    out.update(_keystore_config(parties.sender, parties.receiver))
    return out

# ################################################################################################################################

def _channel_config(parties, profile, serviced_participants='', service_name=''):
    """ The configuration of one AS4 channel, the way the runtime receives it.
    """
    out = {
        'name': 'test.channel',
        'as4_profile': profile,
        'as4_from_party': 'party-a',
        'as4_to_party': 'party-b',
        'as4_service': 'urn:test:service',
        'as4_action': 'SubmitInvoice',
        'as4_agreement': '',
        'as4_mpc': '',
        'as4_original_sender': '',
        'as4_final_recipient': '',
        'as4_extra_pmodes': '',
        'as4_serviced_participants': serviced_participants,
        'as4_inbound_topic': '',
        'service_name': service_name,
    }
    out.update(_keystore_config(parties.receiver, parties.sender))
    return out

# ################################################################################################################################

def _make_wrapper(parties, profile):
    server = _FakeServer()
    out = AS4Wrapper(server, _outgoing_config(parties, profile))
    return out

# ################################################################################################################################

def _make_channel(parties, profile, serviced_participants='', service_name=''):
    server = _FakeServer()
    out = AS4ChannelRuntime(server, _channel_config(parties, profile, serviced_participants, service_name))
    return out

# ################################################################################################################################

def _connect(wrapper, channel):
    """ Points the wrapper's HTTP client at the channel runtime - a loopback over a mocked transport.
    """

    def responder(request):
        result = channel.handle('test-cid', request.content, request.headers['content-type'])
        return httpx.Response(result.status_code, content=result.body, headers={'Content-Type': result.content_type})

    wrapper.session = httpx.Client(transport=httpx.MockTransport(responder))

# ################################################################################################################################
# ################################################################################################################################

class TestWrapperSend:
    """ The facade's send path - the wrapper against a mocked transport
    that runs the real channel runtime on the other side.
    """

    def test_send_delivers_and_routes_to_topic(self, rsa_parties):
        wrapper = _make_wrapper(rsa_parties, 'edelivery1')
        channel = _make_channel(rsa_parties, 'edelivery1')
        _connect(wrapper, channel)

        result = wrapper.send(Test_CID, Payload)

        # The wrapper verified the synchronous receipt.
        assert result.is_ok
        assert result.receipt
        assert result.receipt.ref_to_message_id == result.message_id

        # The channel routed the payload to its topic with the ebMS metadata.
        published = channel.server.pubsub_redis.published
        assert len(published) == 1

        topic_name, message, cid, _ = published[0]
        assert topic_name == AS4.Default.Inbound_Topic
        assert cid == 'test-cid'
        assert message['message_id'] == result.message_id
        assert message['service'] == 'urn:test:service'
        assert message['action'] == 'SubmitInvoice'
        assert message['data'] == Payload.decode('utf8')

    def test_send_routes_to_service_when_one_is_configured(self, rsa_parties):
        wrapper = _make_wrapper(rsa_parties, 'edelivery1')
        channel = _make_channel(rsa_parties, 'edelivery1', service_name='my.service')
        _connect(wrapper, channel)

        result = wrapper.send(Test_CID, Payload)
        assert result.is_ok

        # A configured service takes precedence over the topic.
        assert channel.server.pubsub_redis.published == []
        assert len(channel.server.invoked) == 1

        service_name, message = channel.server.invoked[0]
        assert service_name == 'my.service'
        assert message['data'] == Payload.decode('utf8')

    def test_send_over_inactive_connection_is_rejected(self, rsa_parties):
        wrapper = _make_wrapper(rsa_parties, 'edelivery1')
        wrapper.config['is_active'] = False

        with pytest.raises(AS4Exception) as exc:
            _ = wrapper.send(Test_CID, Payload)

        assert 'not active' in str(exc.value)

# ################################################################################################################################
# ################################################################################################################################

def _smp_metadata(receiver_certificate):
    """ The SMP metadata for the test participant, as a Peppol SMP would return it,
    naming the receiving access point's real certificate.
    """
    certificate_b64 = b64encode(receiver_certificate.public_bytes(Encoding.DER)).decode('ascii')

    out = f'''<?xml version="1.0" encoding="UTF-8"?>
<smp:SignedServiceMetadata xmlns:smp="http://busdox.org/serviceMetadata/publishing/1.0/">
  <smp:ServiceMetadata>
    <smp:ServiceInformation>
      <smp:ProcessList>
        <smp:Process>
          <smp:ServiceEndpointList>
            <smp:Endpoint transportProfile="peppol-transport-as4-v2_0">
              <wsa:EndpointReference xmlns:wsa="http://www.w3.org/2005/08/addressing">
                <wsa:Address>https://ap.example.com/as4</wsa:Address>
              </wsa:EndpointReference>
              <smp:Certificate>{certificate_b64}</smp:Certificate>
            </smp:Endpoint>
          </smp:ServiceEndpointList>
        </smp:Process>
      </smp:ProcessList>
    </smp:ServiceInformation>
  </smp:ServiceMetadata>
</smp:SignedServiceMetadata>'''

    return out.encode('utf8')

# ################################################################################################################################

@pytest.fixture
def recorded_discovery(rsa_parties, monkeypatch):
    """ Replaces live SML and SMP lookups with recorded fixtures - the real discovery
    code still runs, only DNS and HTTP are answered from the recordings.
    """
    smp_metadata = _smp_metadata(rsa_parties.receiver.signing_certificate_chain[0])

    def naptr_lookup(dns_name):
        return ['https://smp.example.com']

    def http_get(url):
        return smp_metadata

    def recorded_lookup(participant_type, participant_id, document_type, sml_domain):
        out = lookup_endpoint(
            participant_type, participant_id, document_type,
            sml_domain=sml_domain, naptr_lookup=naptr_lookup, http_get=http_get)
        return out

    monkeypatch.setattr(server_as4, 'lookup_endpoint', recorded_lookup)

# ################################################################################################################################
# ################################################################################################################################

class TestSendTo:
    """ The access-point one-liner - discovery from recorded SML/SMP fixtures,
    the SBDH wrapping and the delivery to the discovered endpoint.
    """

    def test_send_to_wraps_in_sbdh_and_delivers(self, rsa_parties, recorded_discovery):
        wrapper = _make_wrapper(rsa_parties, 'peppol')
        channel = _make_channel(rsa_parties, 'peppol', serviced_participants=Serviced_Participant)
        _connect(wrapper, channel)

        result = wrapper.send_to(Test_CID, Serviced_Participant, Document_Type_Name, Payload)

        # The wrapper verified the receipt from the discovered endpoint.
        assert result.is_ok
        assert result.receipt

        # The channel routed the payload with the SBDH metadata parsed out,
        # so subscribers route without re-parsing anything.
        published = channel.server.pubsub_redis.published
        assert len(published) == 1

        preset = get_document_type_preset(Document_Type_Name)
        _, message, _, _ = published[0]

        assert message['sbdh_sender'] == Serviced_Participant
        assert message['sbdh_receiver'] == Serviced_Participant
        assert message['sbdh_document_type'] == preset.document_type
        assert message['sbdh_process_id'] == preset.process_id
        assert message['sbdh_instance_identifier']

        # The business document travels inside the SBDH wrapper.
        assert 'urn:test' in message['data']
        assert '<Total>100</Total>' in message['data']

    def test_send_to_uses_the_smp_supplied_endpoint(self, rsa_parties, recorded_discovery):
        wrapper = _make_wrapper(rsa_parties, 'peppol')
        urls_requested = []

        def responder(request):
            urls_requested.append(str(request.url))
            channel = _make_channel(rsa_parties, 'peppol')
            result = channel.handle('test-cid', request.content, request.headers['content-type'])
            return httpx.Response(result.status_code, content=result.body, headers={'Content-Type': result.content_type})

        wrapper.session = httpx.Client(transport=httpx.MockTransport(responder))

        _ = wrapper.send_to(Test_CID, Serviced_Participant, Document_Type_Name, Payload)

        # The message went to the URL from the SMP record, not to the configured endpoint.
        assert urls_requested == ['https://ap.example.com/as4']

# ################################################################################################################################
# ################################################################################################################################

class TestNotServiced:
    """ The Peppol profile's rejection of documents addressed to a participant
    the receiving access point does not serve.
    """

    def test_unserviced_receiver_is_rejected(self, rsa_parties, recorded_discovery):
        wrapper = _make_wrapper(rsa_parties, 'peppol')

        # The channel serves one participant only - and it is not the receiver.
        channel = _make_channel(rsa_parties, 'peppol', serviced_participants=Other_Participant)
        _connect(wrapper, channel)

        with pytest.raises(AS4Exception) as exc:
            _ = wrapper.send_to(Test_CID, Serviced_Participant, Document_Type_Name, Payload)

        # The error signal carries the code and detail the Peppol profile defines.
        assert 'EBMS:0004' in str(exc.value)
        assert Peppol_Not_Serviced in str(exc.value)

        # Nothing was routed anywhere.
        assert channel.server.pubsub_redis.published == []
        assert channel.server.invoked == []

    def test_empty_participant_list_accepts_everyone(self, rsa_parties, recorded_discovery):
        wrapper = _make_wrapper(rsa_parties, 'peppol')
        channel = _make_channel(rsa_parties, 'peppol')
        _connect(wrapper, channel)

        result = wrapper.send_to(Test_CID, Serviced_Participant, Document_Type_Name, Payload)

        assert result.is_ok
        assert len(channel.server.pubsub_redis.published) == 1

# ################################################################################################################################
# ################################################################################################################################

class TestDuplicateSuppression:
    """ The cache-backed duplicate detection keyed on eb:MessageId.
    """

    def _wire_message(self, rsa_parties):
        """ One signed message, byte-identical however many times it is replayed.
        """
        pmode = new_edelivery1_pmode()
        pmode.initiator.party_id = 'party-a'
        pmode.responder.party_id = 'party-b'
        pmode.service = 'urn:test:service'
        pmode.action = 'SubmitInvoice'

        body, content_type, message_id, _ = build_push_message(pmode, rsa_parties.sender, [new_part(Payload)])

        out = (body, content_type, message_id)
        return out

    def test_replay_gets_receipt_but_is_not_routed_again(self, rsa_parties):
        channel = _make_channel(rsa_parties, 'edelivery1')
        body, content_type, message_id = self._wire_message(rsa_parties)

        # The first delivery goes through and is routed.
        first = channel.handle('cid-1', body, content_type)
        assert not first.is_duplicate
        assert first.payloads[0].data == Payload
        assert len(channel.server.pubsub_redis.published) == 1

        # The replay still gets a receipt but nothing is routed a second time.
        second = channel.handle('cid-2', body, content_type)
        assert second.is_duplicate
        assert second.payloads == []
        assert not second.is_error
        assert len(channel.server.pubsub_redis.published) == 1

        # The receipt for the replay references the original message.
        assert message_id.encode('utf8') in second.body

    def test_duplicate_window_is_cache_backed(self, rsa_parties):
        channel = _make_channel(rsa_parties, 'edelivery1')
        body, content_type, message_id = self._wire_message(rsa_parties)

        _ = channel.handle('cid-1', body, content_type)

        # The message id is remembered in the server-wide cache under the AS4 prefix.
        cache = channel.server.config_manager.cache_api
        key = AS4.Default.Duplicate_Cache_Prefix + message_id
        assert cache.exists(key)

    def test_distinct_messages_are_both_routed(self, rsa_parties):
        channel = _make_channel(rsa_parties, 'edelivery1')

        body_first, content_type_first, _ = self._wire_message(rsa_parties)
        body_second, content_type_second, _ = self._wire_message(rsa_parties)

        _ = channel.handle('cid-1', body_first, content_type_first)
        _ = channel.handle('cid-2', body_second, content_type_second)

        assert len(channel.server.pubsub_redis.published) == 2

# ################################################################################################################################
# ################################################################################################################################

class TestRoutedMessageMetadata:
    """ The shape of what subscribers receive - every key always present, no matter the profile.
    """

    def test_all_keys_are_always_present(self, rsa_parties):
        channel = _make_channel(rsa_parties, 'edelivery1')

        pmode = new_edelivery1_pmode()
        pmode.initiator.party_id = 'party-a'
        pmode.responder.party_id = 'party-b'
        pmode.service = 'urn:test:service'
        pmode.action = 'SubmitInvoice'

        body, content_type, _, _ = build_push_message(pmode, rsa_parties.sender, [new_part(Payload)])
        _ = channel.handle('cid-1', body, content_type)

        _, message, _, _ = channel.server.pubsub_redis.published[0]

        expected_keys = {
            'message_id', 'conversation_id', 'from_party', 'to_party', 'service', 'action',
            'mime_type', 'data',
            'sbdh_sender', 'sbdh_receiver', 'sbdh_document_type', 'sbdh_process_id', 'sbdh_instance_identifier',
        }
        assert set(message) == expected_keys

        # A non-Peppol profile has no SBDH, so its metadata keys are present but empty.
        assert message['sbdh_sender'] == ''
        assert message['sbdh_receiver'] == ''
        assert message['from_party'] == 'party-a'
        assert message['to_party'] == 'party-b'

# ################################################################################################################################
# ################################################################################################################################
