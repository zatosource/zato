# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_permission_revoke')

_settle_time = 3.0

# ################################################################################################################################
# ################################################################################################################################

def _get_admin() -> 'any_':
    from zato.common.test.client import AdminClient
    from zato.common.test.config_pubsub_permission_revoke import TestConfig
    admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
    return admin

# ################################################################################################################################

def _get_publisher() -> 'any_':
    from zato.common.test.client import PublishClient
    from zato.common.test.config_pubsub_permission_revoke import TestConfig
    publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
    return publisher

# ################################################################################################################################

def _get_permission_id(admin:'any_', sec_name:'str', pattern_fragment:'str') -> 'int':
    """ Finds a permission ID by security name and a substring of the pattern.
    """
    perm_list = admin.invoke('zato.pubsub.permission.get-list', {'cluster_id': 1})

    if isinstance(perm_list, list):
        items:'anylist' = perm_list
    else:
        items = perm_list['zato_pubsub_permission_get_list_response']

    for item in items:
        if item['name'] == sec_name and pattern_fragment in item['pattern']:
            return item['id']

    raise Exception(f'Permission not found for {sec_name} with pattern containing {pattern_fragment}')

# ################################################################################################################################

def _get_subscriptions(admin:'any_', sec_name:'str') -> 'anylist':
    """ Returns all subscriptions for a given security definition name.
    """
    sub_list = admin.invoke('zato.pubsub.subscription.get-list', {'cluster_id': 1})

    if isinstance(sub_list, list):
        items:'anylist' = sub_list
    else:
        items = sub_list['zato_pubsub_subscription_get_list_response']

    out:'anylist' = []
    for item in items:
        if item['sec_name'] == sec_name:
            out.append(item)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestPermissionRevoke:
    """ Verifies that deleting a pub/sub permission cascade-deletes orphaned subscriptions.
    """

# ################################################################################################################################

    def test_delete_permission_removes_subscription(self, zato_server:'any_') -> 'None':
        """ Deleting the only permission covering a subscription's topics
        must remove the subscription from the ODB.
        """
        admin = _get_admin()

        # .. verify the subscriber has a subscription initially ..
        subs_before = _get_subscriptions(admin, 'test.revoke.subscriber')
        assert len(subs_before) == 1, f'Expected 1 subscription, got {len(subs_before)}'

        # .. find and delete the crm.** permission ..
        perm_id = _get_permission_id(admin, 'test.revoke.subscriber', 'crm')
        _ = admin.invoke('zato.pubsub.permission.delete', {'id': perm_id})

        time.sleep(_settle_time)

        # .. find and delete the billing.** permission ..
        perm_id = _get_permission_id(admin, 'test.revoke.subscriber', 'billing')
        _ = admin.invoke('zato.pubsub.permission.delete', {'id': perm_id})

        time.sleep(_settle_time)

        # .. find and delete the audit.** permission ..
        perm_id = _get_permission_id(admin, 'test.revoke.subscriber', 'audit')
        _ = admin.invoke('zato.pubsub.permission.delete', {'id': perm_id})

        time.sleep(_settle_time)

        # .. the subscription should be gone now ..
        subs_after = _get_subscriptions(admin, 'test.revoke.subscriber')
        assert len(subs_after) == 0, f'Expected 0 subscriptions after revoking all permissions, got {len(subs_after)}'

# ################################################################################################################################

    def test_delete_permission_stops_message_accumulation(self, zato_server:'any_') -> 'None':
        """ After all permissions are deleted, publishing to topics must not
        accumulate pending messages for the now-deleted subscription.
        """
        admin = _get_admin()
        publisher = _get_publisher()

        # .. at this point, all permissions for test.revoke.subscriber were already deleted
        # .. by the previous test, so there should be no subscriptions ..
        subs = _get_subscriptions(admin, 'test.revoke.subscriber')
        assert len(subs) == 0, f'Expected 0 subscriptions, got {len(subs)}'

        # .. publish messages to crm.event1 ..
        for idx in range(5):
            _ = publisher.publish('crm.event1', f'orphan-msg-{idx}')

        time.sleep(_settle_time)

        # .. verify there are no subscriptions accumulating messages ..
        subs = _get_subscriptions(admin, 'test.revoke.subscriber')
        assert len(subs) == 0, f'Expected 0 subscriptions after publishing, got {len(subs)}'

# ################################################################################################################################

    def test_delete_permission_preserves_other_subscriptions(self, zato_server:'any_') -> 'None':
        """ Deleting one permission must not remove a subscription if another
        permission still covers at least one of the subscription's topics.
        """
        admin = _get_admin()
        from zato.common.test.config_pubsub_permission_revoke import TestConfig

        # .. recreate two permissions: crm.** and billing.** ..
        _ = admin.invoke('zato.pubsub.permission.create', {
            'sec_base_id': TestConfig.subscriber_sec_base_id,
            'pattern': 'sub=crm.**',
            'access_type': 'publisher-subscriber',
        })

        _ = admin.invoke('zato.pubsub.permission.create', {
            'sec_base_id': TestConfig.subscriber_sec_base_id,
            'pattern': 'sub=billing.**',
            'access_type': 'publisher-subscriber',
        })

        time.sleep(_settle_time)

        # .. create a subscription covering topics from both permissions ..
        _ = admin.invoke('zato.pubsub.subscription.create', {
            'cluster_id': 1,
            'topic_name_list': ['crm.event1', 'billing.invoice1'],
            'sec_base_id': TestConfig.subscriber_sec_base_id,
            'delivery_type': 'pull',
        })

        time.sleep(_settle_time)

        # .. verify we have a subscription ..
        subs_before = _get_subscriptions(admin, 'test.revoke.subscriber')
        assert len(subs_before) == 1, f'Expected 1 subscription, got {len(subs_before)}'

        # .. delete the crm.** permission ..
        perm_id = _get_permission_id(admin, 'test.revoke.subscriber', 'crm')
        _ = admin.invoke('zato.pubsub.permission.delete', {'id': perm_id})

        time.sleep(_settle_time)

        # .. the subscription should still exist because billing.** still covers billing.invoice1 ..
        subs_after = _get_subscriptions(admin, 'test.revoke.subscriber')
        assert len(subs_after) == 1, f'Expected 1 subscription (billing still covered), got {len(subs_after)}'

        # .. clean up: delete billing.** permission (should now remove the subscription) ..
        perm_id = _get_permission_id(admin, 'test.revoke.subscriber', 'billing')
        _ = admin.invoke('zato.pubsub.permission.delete', {'id': perm_id})

        time.sleep(_settle_time)

        subs_final = _get_subscriptions(admin, 'test.revoke.subscriber')
        assert len(subs_final) == 0, f'Expected 0 subscriptions after removing all permissions, got {len(subs_final)}'

# ################################################################################################################################

    def test_delete_permission_removes_all_topics(self, zato_server:'any_') -> 'None':
        """ Deleting a permission that covers all of a subscription's topics
        must remove the entire subscription.
        """
        admin = _get_admin()
        from zato.common.test.config_pubsub_permission_revoke import TestConfig

        # .. create audit.** permission ..
        _ = admin.invoke('zato.pubsub.permission.create', {
            'sec_base_id': TestConfig.subscriber_sec_base_id,
            'pattern': 'sub=audit.**',
            'access_type': 'publisher-subscriber',
        })

        time.sleep(_settle_time)

        # .. create a subscription with two audit topics ..
        _ = admin.invoke('zato.pubsub.subscription.create', {
            'cluster_id': 1,
            'topic_name_list': ['audit.login', 'audit.logout'],
            'sec_base_id': TestConfig.subscriber_sec_base_id,
            'delivery_type': 'pull',
        })

        time.sleep(_settle_time)

        # .. verify the subscription exists ..
        subs_before = _get_subscriptions(admin, 'test.revoke.subscriber')
        assert len(subs_before) == 1, f'Expected 1 subscription, got {len(subs_before)}'

        # .. delete the audit.** permission ..
        perm_id = _get_permission_id(admin, 'test.revoke.subscriber', 'audit')
        _ = admin.invoke('zato.pubsub.permission.delete', {'id': perm_id})

        time.sleep(_settle_time)

        # .. the entire subscription should be gone since no topics are covered ..
        subs_after = _get_subscriptions(admin, 'test.revoke.subscriber')
        assert len(subs_after) == 0, f'Expected 0 subscriptions after revoking audit permission, got {len(subs_after)}'

# ################################################################################################################################
# ################################################################################################################################
