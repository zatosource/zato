# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# pytest
import pytest

# Zato
from zato.common.test.client import AdminClient as ZatoClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

_settle_time = 2.0

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def client(zato_server:'any_') -> 'ZatoClient':
    base_url = f'http://{zato_server["host"]}:{zato_server["port"]}'
    return ZatoClient(base_url, zato_server['password'])

# ################################################################################################################################
# ################################################################################################################################

def _create_sec_def(client:'ZatoClient', name:'str', username:'str') -> 'int':
    """ Creates a basic auth security definition and returns its ID.
    """
    resp = client.create('zato.security.basic-auth.create',
        cluster_id=1,
        name=name,
        is_active=True,
        username=username,
        realm='testrealm',
    )
    return resp['id']

# ################################################################################################################################

def _create_topic(client:'ZatoClient', name:'str') -> 'None':
    """ Creates a pub/sub topic.
    """
    _ = client.create('zato.pubsub.topic.create',
        cluster_id=1,
        name=name,
        is_active=True,
    )

# ################################################################################################################################

def _create_permission(client:'ZatoClient', sec_base_id:'int', pattern:'str') -> 'int':
    """ Creates a pub/sub permission and returns its ID.
    """
    resp = client.create('zato.pubsub.permission.create',
        cluster_id=1,
        sec_base_id=sec_base_id,
        pattern=pattern,
        access_type='publisher-subscriber',
    )
    return resp['id']

# ################################################################################################################################

def _create_subscription(client:'ZatoClient', sec_base_id:'int', topic_names:'anylist') -> 'str':
    """ Creates a pull subscription and returns its sub_key.
    """
    resp = client.create('zato.pubsub.subscription.create',
        cluster_id=1,
        topic_name_list=topic_names,
        sec_base_id=sec_base_id,
        delivery_type='pull',
        is_delivery_active=True,
        is_pub_active=True,
    )
    return resp['sub_key']

# ################################################################################################################################

def _get_subscriptions_for_sec(client:'ZatoClient', sec_base_id:'int') -> 'anylist':
    """ Returns subscription dicts for a given sec_base_id.
    """
    data, _ = client.get_list('zato.pubsub.subscription.get-list', cluster_id=1)

    out:'anylist' = []
    for item in data:
        if item['sec_base_id'] == sec_base_id:
            out.append(item)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestPubSubPermissionRevoke:
    """ Tests that permission deletion cascade-deletes orphaned subscriptions
    and preserves subscriptions still covered by remaining permissions.
    """

    sec_id:'int'

# ################################################################################################################################

    def test_01_setup(self, client:'ZatoClient') -> 'None':
        """ Create security defs and topics needed by subsequent tests.
        """
        self.__class__.sec_id = _create_sec_def(client, 'test.revoke.configstore', 'test.revoke.configstore')
        _create_topic(client, 'revoke.crm.event1')
        _create_topic(client, 'revoke.billing.invoice1')

# ################################################################################################################################

    def test_02_delete_sole_permission_removes_subscription(self, client:'ZatoClient') -> 'None':
        """ Deleting the only permission must delete the subscription.
        """
        sec_id = self.__class__.sec_id

        # .. create permission and subscription ..
        perm_id = _create_permission(client, sec_id, 'sub=revoke.crm.**')
        _ = _create_subscription(client, sec_id, ['revoke.crm.event1'])

        time.sleep(_settle_time)

        subs = _get_subscriptions_for_sec(client, sec_id)
        assert len(subs) == 1

        # .. delete the permission ..
        _ = client.delete('zato.pubsub.permission.delete', id=perm_id)

        time.sleep(_settle_time)

        # .. subscription must be gone ..
        subs = _get_subscriptions_for_sec(client, sec_id)
        assert len(subs) == 0

# ################################################################################################################################

    def test_03_delete_one_permission_preserves_covered_subscription(self, client:'ZatoClient') -> 'None':
        """ Deleting one permission must preserve a subscription if another permission still covers it.
        """
        sec_id = self.__class__.sec_id

        # .. create two permissions ..
        perm_crm = _create_permission(client, sec_id, 'sub=revoke.crm.**')
        perm_billing = _create_permission(client, sec_id, 'sub=revoke.billing.**')

        # .. subscribe to topics from both ..
        _ = _create_subscription(client, sec_id, ['revoke.crm.event1', 'revoke.billing.invoice1'])

        time.sleep(_settle_time)

        subs = _get_subscriptions_for_sec(client, sec_id)
        assert len(subs) == 1

        # .. delete only the crm permission ..
        _ = client.delete('zato.pubsub.permission.delete', id=perm_crm)

        time.sleep(_settle_time)

        # .. subscription must still exist (billing.invoice1 is still covered) ..
        subs = _get_subscriptions_for_sec(client, sec_id)
        assert len(subs) == 1

        # .. now delete the billing permission too ..
        _ = client.delete('zato.pubsub.permission.delete', id=perm_billing)

        time.sleep(_settle_time)

        # .. subscription must be gone ..
        subs = _get_subscriptions_for_sec(client, sec_id)
        assert len(subs) == 0

# ################################################################################################################################

    def test_04_no_subscriptions_means_no_error(self, client:'ZatoClient') -> 'None':
        """ Deleting a permission when there are no subscriptions must not raise errors.
        """
        sec_id = self.__class__.sec_id

        perm_id = _create_permission(client, sec_id, 'sub=revoke.crm.**')

        time.sleep(_settle_time)

        # .. delete with no subscription present - must not raise ..
        _ = client.delete('zato.pubsub.permission.delete', id=perm_id)

        time.sleep(_settle_time)

        subs = _get_subscriptions_for_sec(client, sec_id)
        assert len(subs) == 0

# ################################################################################################################################
# ################################################################################################################################
