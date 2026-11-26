# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# PyYAML
import yaml

# pytest
import pytest

# Zato
from zato.common.test.order_to_cash.models import accept_order, ApprovedOrder, build_invoice, build_ship_notice, \
    decide_credit, PurchaseOrder, ServiceName, Topic

# Order-to-cash
from order_to_cash.scenario import Channel, Chain_Topics, get_publications, get_subscription_definitions, \
    new_over_limit_order, new_standard_order, new_unit_service, Partner, render_definitions
from order_to_cash.services import CreditCheck, Invoicing, OrderIntake
from order_to_cash.services_fulfillment import Fulfillment as FulfillmentFirst
from order_to_cash.services_fulfillment_carrier import Fulfillment as FulfillmentCarrier
from order_to_cash.services_receivables import Receivables

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import any_, anydict, dictlist

# ################################################################################################################################
# ################################################################################################################################

# The password that the definitions are rendered with
_partner_password = 'order-to-cash-unit-password'

# The service that each topic delivers to and the service that publishes to it, which is the chain of the integration
_chain = {
    Topic.Order_Accepted: (ServiceName.Order_Intake, ServiceName.Credit_Check),
    Topic.Order_Approved: (ServiceName.Credit_Check, ServiceName.Fulfillment),
    Topic.Order_Rejected: (ServiceName.Credit_Check, ServiceName.Receivables),
    Topic.Order_Shipped:  (ServiceName.Fulfillment,  ServiceName.Invoicing),
    Topic.Invoice_Issued: (ServiceName.Invoicing,    ServiceName.Receivables),
}

# ################################################################################################################################
# ################################################################################################################################

def _load(*, is_receivables_active:'bool') -> 'anydict':
    rendered = render_definitions(_partner_password, is_receivables_active=is_receivables_active)

    out = yaml.safe_load(rendered)
    return out

# ################################################################################################################################

def _get_subscribers(definitions:'anydict') -> 'dict[str, list[str]]':
    """ The push services that each topic delivers to.
    """
    out:'dict[str, list[str]]' = {}

    for subscription in definitions['pubsub_subscription']:
        for topic_name in subscription['topic_list']:
            subscribers = out.setdefault(topic_name, [])
            subscribers.append(subscription['push_service'])

    return out

# ################################################################################################################################

def _get_subscription(definitions:'anydict', service_name:'str') -> 'anydict':
    subscriptions:'dictlist' = definitions['pubsub_subscription']

    for subscription in subscriptions:
        if subscription['push_service'] == service_name:
            return subscription

    raise Exception(f'No subscription of service `{service_name}`')

# ################################################################################################################################

def _run_chain(base_dir:'str') -> 'dict[str, set[str]]':
    """ Runs each service of the chain, both versions of the fulfillment included, on an order that is approved
    and on one that is rejected, and returns the services that published to each topic.
    """
    out:'dict[str, set[str]]' = {}

    def _run(class_:'any_', payload:'any_') -> 'None':
        service = new_unit_service(class_, base_dir, payload)
        service.handle()

        for topic_name, _, _ in get_publications(service):
            publishers = out.setdefault(topic_name, set())
            publishers.add(service.name)

    approved_order = PurchaseOrder.from_dict(new_standard_order('PO-TOPOLOGY-0001'))
    rejected_order = PurchaseOrder.from_dict(new_over_limit_order('PO-TOPOLOGY-0002'))

    for order in (approved_order, rejected_order):
        _run(OrderIntake, order)
        _run(CreditCheck, accept_order(order))

    approved = decide_credit(accept_order(approved_order))
    rejected = decide_credit(accept_order(rejected_order))
    assert isinstance(approved, ApprovedOrder), approved

    notice = build_ship_notice(approved)

    _run(Receivables, rejected)
    _run(FulfillmentFirst, approved)
    _run(FulfillmentCarrier, approved)
    _run(Invoicing, notice)
    _run(Receivables, build_invoice(notice))

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def definitions() -> 'anydict':
    out = _load(is_receivables_active=True)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestDefinitions:

    def test_partner_security(self, definitions:'anydict') -> 'None':
        security = definitions['security']

        assert len(security) == 1, security
        assert security[0]['name'] == Partner.Username
        assert security[0]['username'] == Partner.Username
        assert security[0]['type'] == 'basic_auth'
        assert security[0]['password'] == _partner_password

    def test_topics(self, definitions:'anydict') -> 'None':
        names = [topic['name'] for topic in definitions['pubsub_topic']]
        assert sorted(names) == sorted(Chain_Topics)

    def test_every_subscription_is_push(self, definitions:'anydict') -> 'None':
        for subscription in definitions['pubsub_subscription']:
            assert subscription['delivery_type'] == 'push', subscription

    def test_one_subscription_per_service(self, definitions:'anydict') -> 'None':
        services = [subscription['push_service'] for subscription in definitions['pubsub_subscription']]
        assert len(services) == len(set(services)), services

    def test_each_topic_delivers_to_the_next_service(self, definitions:'anydict') -> 'None':
        subscribers = _get_subscribers(definitions)

        expected = {topic_name: [subscriber] for topic_name, (_, subscriber) in _chain.items()}
        assert subscribers == expected

    def test_queued_channel(self, definitions:'anydict') -> 'None':
        channels = definitions['channel_rest']
        assert len(channels) == 1, channels

        channel = channels[0]

        assert channel['name'] == Channel.Name
        assert channel['service'] == ServiceName.Order_Intake
        assert channel['url_path'] == Channel.URL_Path
        assert channel['security'] == Partner.Username
        assert channel['use_queue'] is True
        assert channel['max_retries'] == 3
        assert channel['retry_sleep_time'] == 1
        assert channel['use_dlq'] is True
        assert channel['dlq_action'] == 'keep'

    def test_no_object_other_than_the_integration(self, definitions:'anydict') -> 'None':
        assert sorted(definitions) == ['channel_rest', 'pubsub_subscription', 'pubsub_topic', 'security']

# ################################################################################################################################
# ################################################################################################################################

class TestReceivablesActivation:

    def test_active_receivables(self) -> 'None':
        subscription = _get_subscription(_load(is_receivables_active=True), ServiceName.Receivables)
        assert subscription['is_delivery_active'] is True

    def test_inactive_receivables(self) -> 'None':
        subscription = _get_subscription(_load(is_receivables_active=False), ServiceName.Receivables)
        assert subscription['is_delivery_active'] is False

    def test_other_subscriptions_are_always_active(self) -> 'None':
        definitions = _load(is_receivables_active=False)

        for subscription in definitions['pubsub_subscription']:
            if subscription['push_service'] != ServiceName.Receivables:
                assert 'is_delivery_active' not in subscription, subscription

    def test_subscription_definitions_alone(self) -> 'None':
        rendered = render_definitions(_partner_password, is_receivables_active=True)
        subscriptions = yaml.safe_load(get_subscription_definitions(rendered))

        assert list(subscriptions) == ['pubsub_subscription']
        assert subscriptions['pubsub_subscription'] == _load(is_receivables_active=True)['pubsub_subscription']

# ################################################################################################################################
# ################################################################################################################################

class TestPublisherTopology:

    def test_each_topic_has_one_publisher(self, tmp_path:'Path') -> 'None':
        publishers = _run_chain(str(tmp_path))

        expected = {topic_name: {publisher} for topic_name, (publisher, _) in _chain.items()}
        assert publishers == expected

# ################################################################################################################################
# ################################################################################################################################
