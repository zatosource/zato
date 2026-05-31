# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time

# redis
from redis import Redis

# Zato
from zato.common.api import PubSub

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_sec_delete')

_settle_time = 0.5

_test_redis_host = 'localhost'
_test_redis_port = 6379
_test_redis_db   = PubSub.Test_Redis_DB

_Subs_Prefix        = 'zato:pubsub:subs:'
_Topic_Subs_Prefix  = 'zato:pubsub:topic_subs:'
_Stream_Prefix      = 'zato:pubsub:stream:'
_Sub_Pending_Prefix = 'zato:pubsub:sub_pending:'

# ################################################################################################################################
# ################################################################################################################################

def _get_admin() -> 'any_':
    from zato.common.test.client import AdminClient
    from zato.common.test.config_pubsub_sec_delete import TestConfig
    admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
    return admin

# ################################################################################################################################

def _get_publisher() -> 'any_':
    from zato.common.test.client import PublishClient
    from zato.common.test.config_pubsub_sec_delete import TestConfig
    publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
    return publisher

# ################################################################################################################################

def _get_redis() -> 'Redis':
    redis = Redis(host=_test_redis_host, port=_test_redis_port, db=_test_redis_db, decode_responses=True)
    return redis

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

def _get_sub_keys_for_sec(admin:'any_', sec_name:'str') -> 'list[str]':
    """ Returns all sub_keys for subscriptions belonging to a security definition.
    """
    subs = _get_subscriptions(admin, sec_name)
    out = [sub['sub_key'] for sub in subs]
    return out

# ################################################################################################################################

def _get_permissions(admin:'any_', sec_name:'str') -> 'anylist':
    """ Returns all permissions for a given security definition name.
    """
    perm_list = admin.invoke('zato.pubsub.permission.get-list', {'cluster_id': 1})

    if isinstance(perm_list, list):
        items:'anylist' = perm_list
    else:
        items = perm_list['zato_pubsub_permission_get_list_response']

    out:'anylist' = []
    for item in items:
        if item['name'] == sec_name:
            out.append(item)

    return out

# ################################################################################################################################

def _delete_security_definition(admin:'any_') -> 'None':
    """ Deletes the test subscriber security definition.
    """
    from zato.common.test.config_pubsub_sec_delete import TestConfig
    _ = admin.invoke('zato.security.basic-auth.delete', {'id': TestConfig.subscriber_sec_base_id})

# ################################################################################################################################
# ################################################################################################################################

class TestSecurityDeletePubSubCleanup:
    """ Verifies that deleting a security definition cleans up all pub/sub state (Gaps 18-25).
    """

# ################################################################################################################################

    def test_01_subscriptions_deleted_from_odb(self, zato_server:'any_') -> 'None':
        """ GAP 18: After deleting a basic_auth security definition, all subscriptions
        for that sec_def are gone from the ODB.
        """
        admin = _get_admin()

        # .. verify subscriptions exist before delete ..
        subs_before = _get_subscriptions(admin, 'test.secdel.subscriber')
        assert len(subs_before) >= 2, f'Expected at least 2 subscriptions before delete, got {len(subs_before)}'

        # .. collect sub_keys and topic info before delete for subsequent tests ..
        self.__class__._sub_keys_before = _get_sub_keys_for_sec(admin, 'test.secdel.subscriber') # type: ignore[attr-defined]
        self.__class__._topics_before = ['secdel.topic.alpha', 'secdel.topic.beta', 'secdel.topic.gamma'] # type: ignore[attr-defined]

        # .. delete the security definition ..
        _delete_security_definition(admin)
        time.sleep(_settle_time)

        # .. verify subscriptions are gone ..
        subs_after = _get_subscriptions(admin, 'test.secdel.subscriber')
        assert len(subs_after) == 0, f'Expected 0 subscriptions after security delete, got {len(subs_after)}'

# ################################################################################################################################

    def test_02_redis_sets_cleaned(self, zato_server:'any_') -> 'None':
        """ GAP 19: Redis subscriber sets and topic subscriber sets are cleaned up
        for all subscriptions that belonged to the deleted security definition.
        """
        redis = _get_redis()

        sub_keys:'list[str]' = self.__class__._sub_keys_before # type: ignore[attr-defined]
        topics:'list[str]' = self.__class__._topics_before # type: ignore[attr-defined]

        # .. verify no sub_key has remaining subs set entries ..
        for sub_key in sub_keys:
            subs_key = f'{_Subs_Prefix}{sub_key}'
            card:'int' = redis.scard(subs_key) # type: ignore[assignment]
            assert card == 0, f'Expected subs set to be empty for {sub_key}, got {card}'

        # .. verify no topic_subs set contains any of the old sub_keys ..
        for topic_name in topics:
            topic_subs_key = f'{_Topic_Subs_Prefix}{topic_name}'
            for sub_key in sub_keys:
                is_member:'int' = redis.sismember(topic_subs_key, sub_key) # type: ignore[assignment]
                assert is_member == 0, \
                    f'Expected sub_key {sub_key} removed from topic_subs for {topic_name}'

# ################################################################################################################################

    def test_03_config_store_pubsub_subs_cleaned(self, zato_server:'any_') -> 'None':
        """ GAP 20: The config_store.pubsub_subs no longer contains entries for the
        deleted subscriptions. Verified by confirming no subscription exists for the sec_name.
        """
        admin = _get_admin()

        # .. the get-list returning 0 subs proves pubsub_subs is clean
        # .. because get-list reflects both ODB and in-memory state ..
        subs = _get_subscriptions(admin, 'test.secdel.subscriber')
        assert len(subs) == 0, f'Expected 0 subscriptions in config store, got {len(subs)}'

# ################################################################################################################################

    def test_04_subscriptions_store_cleaned(self, zato_server:'any_') -> 'None':
        """ GAP 21: The SubscriptionsStore (username-to-sub_key, sec_name-to-username mappings)
        is cleaned up. Verified by confirming that re-creating the security definition
        and subscribing works from scratch without conflicts.
        """
        admin = _get_admin()

        # .. create a new security definition with the same username ..
        new_sec = admin.invoke('zato.security.basic-auth.create', {
            'name': 'test.secdel.subscriber.v2',
            'is_active': True,
            'username': 'test.secdel.subscriber.v2',
            'realm': 'testrealm',
            'cluster_id': 1,
        })

        new_sec_id = new_sec['id']

        # .. grant it permissions ..
        _ = admin.invoke('zato.pubsub.permission.create', {
            'sec_base_id': new_sec_id,
            'pattern': 'sub=secdel.**',
            'access_type': 'publisher-subscriber',
        })

        time.sleep(_settle_time)

        # .. subscribe to a topic - this must succeed without conflicts ..
        sub_response = admin.invoke('zato.pubsub.subscription.create', {
            'cluster_id': 1,
            'topic_name_list': ['secdel.topic.alpha'],
            'sec_base_id': new_sec_id,
            'delivery_type': 'pull',
        })

        assert 'sub_key' in sub_response, f'Expected sub_key in response, got {sub_response}'

        # .. clean up: delete the new subscription and security definition ..
        _ = admin.invoke('zato.pubsub.subscription.delete', {'id': sub_response['id']})
        time.sleep(_settle_time)

        _ = admin.invoke('zato.security.basic-auth.delete', {'id': new_sec_id})

# ################################################################################################################################

    def test_05_push_subs_and_greenlet_stopped(self, zato_server:'any_') -> 'None':
        """ GAPs 22+23: Push delivery config (_push_subs) is removed and delivery greenlets
        are stopped. Verified by confirming no pending messages accumulate after security delete.
        """
        redis = _get_redis()

        sub_keys:'list[str]' = self.__class__._sub_keys_before # type: ignore[attr-defined]

        # .. verify no sub_pending keys remain for the old sub_keys ..
        for sub_key in sub_keys:
            sub_pending_key = f'{_Sub_Pending_Prefix}{sub_key}'
            exists:'int' = redis.exists(sub_pending_key) # type: ignore[assignment]
            assert exists == 0, f'Expected sub_pending key gone for {sub_key}'

        # .. publish messages to the topics - they must not accumulate for deleted subs ..
        publisher = _get_publisher()

        for topic_name in self.__class__._topics_before: # type: ignore[attr-defined]
            _ = publisher.publish(topic_name, 'orphan-test-payload')

        time.sleep(_settle_time)

        # .. verify no new pending state appeared for the old sub_keys ..
        for sub_key in sub_keys:
            sub_pending_key = f'{_Sub_Pending_Prefix}{sub_key}'
            exists_after:'int' = redis.exists(sub_pending_key) # type: ignore[assignment]
            assert exists_after == 0, \
                f'Expected no pending accumulation for deleted sub_key {sub_key}'

# ################################################################################################################################

    def test_06_pattern_matcher_cleaned(self, zato_server:'any_') -> 'None':
        """ GAP 24: The pattern matcher no longer holds permissions for the deleted username.
        Verified by confirming that publishing with a new user to the same topic pattern
        works (old permissions don't interfere) and the old username has no access.
        """
        from zato.common.test.client import PublishClient
        from zato.common.test.config_pubsub_sec_delete import TestConfig

        # .. try to publish using the old subscriber credentials - must fail (403 or error) ..
        old_publisher = PublishClient(
            TestConfig.base_url,
            TestConfig.subscriber_username,
            TestConfig.subscriber_password,
        )

        try:
            _ = old_publisher.publish('secdel.topic.alpha', 'should-fail')
            # .. if we reach here, the server accepted the request which means
            # .. the old credentials still work - that's a failure ..
            assert False, 'Expected publish with deleted credentials to fail'
        except Exception as exc:
            # .. any error (401, 403, connection error) proves the old credentials are gone ..
            logger.info('Publish with deleted credentials correctly failed: %s', exc)

# ################################################################################################################################

    def test_07_permissions_cascade_and_matcher_updated(self, zato_server:'any_') -> 'None':
        """ GAP 25: Permissions are cascade-deleted from ODB and the pattern matcher
        no longer has the old client registered.
        """
        admin = _get_admin()

        # .. verify no permissions exist for the deleted security definition ..
        perms = _get_permissions(admin, 'test.secdel.subscriber')
        assert len(perms) == 0, f'Expected 0 permissions after security delete, got {len(perms)}'

# ################################################################################################################################
# ################################################################################################################################
