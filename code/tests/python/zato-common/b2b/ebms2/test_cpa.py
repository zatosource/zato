# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# lxml
from lxml.etree import fromstring, SubElement, tostring

# pytest
import pytest

# Zato
from zato.common.b2b.ebms2.common import CPAException, CPAUnsupportedException, Direction, EbMS2Exception, ErrorCode, \
    MSHService, new_party_id, NS, PerMessage
from zato.common.b2b.ebms2.cpa.export import export_cpa
from zato.common.b2b.ebms2.cpa.parse import parse_cpa
from zato.common.test.b2b_cpa import build_cpa, build_cpa_element, new_settings, Party_Id_Type, Receiver_Endpoint, \
    Receiver_Name, Sender_Name
from zato.common.test.b2b_ebms2 import new_exchange, resolve, Start_Time
from zato.common.util.xml_.core import qname

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.b2b_pki import TestParties
    from zato.common.typing_ import any_
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

_channel_id_tag = qname(NS.CPA, 'ChannelId')
_security_details_tag = qname(NS.CPA, 'SecurityDetails')
_security_policy_tag = qname(NS.CPA, 'SecurityPolicy')

# ################################################################################################################################
# ################################################################################################################################

class TestAgreementDocument:
    """ The CPP/A 2.0 documents that agreements are read from and written to.
    """

    def test_generated_agreement_is_schema_valid(self, parties:'TestParties', cpa_schema:'any_') -> 'None':
        settings = new_settings(parties, Start_Time)
        data = build_cpa(settings)

        document = fromstring(data)
        cpa_schema.assertValid(document)

    def test_parse_agreement(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        data = build_cpa(settings)

        agreement = parse_cpa(data)

        sender, receiver = agreement.parties

        assert agreement.cpa_id == settings.cpa_id
        assert agreement.start == settings.start
        assert agreement.end == settings.end
        assert sender.party_name == Sender_Name
        assert receiver.party_name == Receiver_Name
        assert sender.party_ids[0].id_type == Party_Id_Type

        signing_certificate = agreement.get_certificate(f'{Sender_Name}-signing')
        assert signing_certificate.leaf == parties.sender.certificate

        anchors = agreement.get_anchor_certificates(f'{Receiver_Name}-trust')
        assert anchors == [parties.ca_certificate]

    def test_export_is_schema_valid_and_stable(self, parties:'TestParties', cpa_schema:'any_') -> 'None':
        settings = new_settings(parties, Start_Time)
        data = build_cpa(settings)

        agreement = parse_cpa(data)
        exported = export_cpa(agreement)

        document = fromstring(exported)
        cpa_schema.assertValid(document)

        reparsed = parse_cpa(exported)
        exported_again = export_cpa(reparsed)

        assert exported_again == exported

    def test_durations(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        settings.retry_interval = 'PT1M30S'
        settings.persist_duration = 'P2D'

        exchange = new_exchange(parties, settings)
        binding = resolve(exchange)

        assert binding.sender_binding is not None
        assert binding.receiver_binding is not None

        reliable = binding.sender_binding.reliable_messaging
        persist_duration = binding.receiver_binding.persist_duration

        assert reliable is not None
        assert reliable.retry_interval is not None
        assert persist_duration is not None

        assert reliable.retry_interval.value == timedelta(seconds=90)
        assert persist_duration.value == timedelta(days=2)

    def test_unsupported_element_is_rejected(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        root = build_cpa_element(settings)

        details = root.find(f'.//{_security_details_tag}')
        _ = SubElement(details, _security_policy_tag)

        data = tostring(root)

        with pytest.raises(CPAUnsupportedException) as info:
            _ = parse_cpa(data)

        assert info.value.element == 'SecurityPolicy'

    def test_dangling_reference_is_rejected(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        root = build_cpa_element(settings)

        channel_id = root.find(f'.//{_channel_id_tag}')
        channel_id.text = 'no-such-channel'

        data = tostring(root)

        with pytest.raises(CPAException) as info:
            _ = parse_cpa(data)

        assert info.value.element == 'ChannelId'

    def test_not_an_agreement(self) -> 'None':
        with pytest.raises(CPAException):
            _ = parse_cpa(b'<Other/>')

# ################################################################################################################################
# ################################################################################################################################

class TestBindingResolution:
    """ How a message between the two parties of an agreement is exchanged.
    """

    def test_business_binding(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        binding = resolve(exchange)

        assert binding.from_party.party_name == Sender_Name
        assert binding.to_party.party_name == Receiver_Name
        assert binding.send_channel.channel_id == f'{Sender_Name}-business'
        assert binding.receive_channel.channel_id == f'{Receiver_Name}-business'
        assert binding.receive_channel.transport.endpoint_uri == Receiver_Endpoint
        assert binding.characteristics.ack_requested == PerMessage.Always
        assert not binding.is_msh

    def test_message_service_handler_binding(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        binding = resolve(exchange, MSHService.Ping, is_msh=True)

        assert binding.is_msh
        assert binding.send_binding is None
        assert binding.send_channel.channel_id == f'{Sender_Name}-msh'
        assert binding.receive_channel.channel_id == f'{Receiver_Name}-msh'

    def test_action_in_the_other_direction(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        with pytest.raises(EbMS2Exception) as info:
            _ = resolve(exchange, is_reverse=True)

        assert info.value.error_code == ErrorCode.Not_Supported

    def test_unknown_action(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        with pytest.raises(EbMS2Exception) as info:
            _ = resolve(exchange, 'NoSuchAction')

        assert info.value.error_code == ErrorCode.Not_Supported

    def test_unknown_service(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        from_ids = [new_party_id(Sender_Name, Party_Id_Type)]
        to_ids = [new_party_id(Receiver_Name, Party_Id_Type)]

        with pytest.raises(EbMS2Exception) as info:
            _ = exchange.agreement.resolve(from_ids, to_ids, 'urn:zato:b2b:test:other', '', settings.action, Direction.Send)

        assert info.value.error_code == ErrorCode.Value_Not_Recognized

    def test_unknown_party(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        from_ids = [new_party_id('b2b-unknown', Party_Id_Type)]
        to_ids = [new_party_id(Receiver_Name, Party_Id_Type)]

        with pytest.raises(EbMS2Exception) as info:
            _ = exchange.agreement.resolve(from_ids, to_ids, settings.service, '', settings.action, Direction.Send)

        assert info.value.error_code == ErrorCode.Value_Not_Recognized
        assert info.value.location == 'eb:From'

# ################################################################################################################################
# ################################################################################################################################
