# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import unittest
from base64 import b64encode
from time import monotonic, sleep

# Zato
from zato.common.api import PubSub
from zato.common.test.client import AdminClient
from zato.common.test.config_multi_cpu_pubsub import PubSubConfig
from zato.common.test.conftest_base_multi_cpu import connection_to_slot, ModuleCtx as MultiCPUCtx, MultiCPUTestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, callable_, intlist, strdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_pubsub.subscription_changes')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long every slot has to enforce a change, in seconds
    Change_Deadline = 30.0

    Poll_Interval = 0.25

    Topic_Name   = 'multi.cpu.changes.first'
    Renamed_Name = 'multi.cpu.changes.second'

    Pull_Path = '/pubsub/messages/get'

    Topic_Create_Service = 'zato.pubsub.topic.create'
    Topic_Edit_Service   = 'zato.pubsub.topic.edit'
    Topic_Delete_Service = 'zato.pubsub.topic.delete'
    Topic_List_Service   = 'zato.pubsub.topic.get-list'

    Sub_Create_Service = 'zato.pubsub.subscription.create'
    Sub_Delete_Service = 'zato.pubsub.subscription.delete'
    Sub_List_Service   = 'zato.pubsub.subscription.get-list'

    Perm_Edit_Service = 'zato.pubsub.permission.edit'
    Perm_List_Service = 'zato.pubsub.permission.get-list'
    Sec_List_Service  = 'zato.security.basic-auth.get-list'

    # The pattern of the publisher before the revoke, and the one that no longer covers the push topic
    Pattern_Granted = 'pub=multi.cpu.**'
    Pattern_Revoked = 'pub=multi.cpu.other.**'

# ################################################################################################################################
# ################################################################################################################################

def _auth_headers(username:'str') -> 'strdict':
    credentials = f'{username}:{MultiCPUTestConfig.sec_password}'

    out = {
        'Authorization': 'Basic ' + b64encode(credentials.encode()).decode(),
        'Content-Type': 'application/json',
    }
    return out

# ################################################################################################################################

def _post_status(slot:'int', path:'str', username:'str', payload:'anydict') -> 'int':
    """ Sends one request to the worker of a slot and returns the status of its response.
    """
    connection = connection_to_slot(slot)
    connection.request('POST', path, body=json.dumps(payload), headers=_auth_headers(username))

    response = connection.getresponse()
    _ = response.read()
    connection.close()

    out = response.status
    return out

# ################################################################################################################################

def _publish_status(slot:'int', topic_name:'str') -> 'int':
    out = _post_status(slot, f'/pubsub/topic/{topic_name}', PubSubConfig.Publisher_Name, {'data': 'multi-cpu'})
    return out

# ################################################################################################################################

def _pull_status(slot:'int') -> 'int':
    out = _post_status(slot, ModuleCtx.Pull_Path, PubSubConfig.Joiner_Name, {})
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSubscriptionChangesAcrossWorkers(unittest.TestCase):
    """ Changes of subscriptions, topics and permissions made through one worker are enforced by every worker.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.admin = AdminClient(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)

# ################################################################################################################################

    def _wait_on_every_slot(self, description:'str', get_status:'callable_', is_expected:'callable_') -> 'None':
        """ Waits until the response of every slot is the expected one.
        """
        pending:'intlist' = list(range(MultiCPUTestConfig.worker_count))
        deadline = monotonic() + ModuleCtx.Change_Deadline

        while pending:
            still_pending:'intlist' = []

            for slot in pending:
                status = get_status(slot)
                if not is_expected(status):
                    still_pending.append(slot)

            pending = still_pending

            if pending:
                if monotonic() > deadline:
                    self.fail(f'{description} -> slots {pending} after {ModuleCtx.Change_Deadline}s')
                sleep(ModuleCtx.Poll_Interval)

        logger.info('%s -> every slot', description)

# ################################################################################################################################

    def _get_item(self, service_name:'str', key:'str', value:'str') -> 'anydict':
        items, _ = self.admin.get_list(service_name)

        for item in items:
            if item[key] == value:
                return item

        raise Exception(f'No item with {key}={value} in {service_name}')

# ################################################################################################################################

    def test_subscribe_and_unsubscribe(self) -> 'None':
        """ A subscription created through one worker lets every worker serve pulls, and its deletion stops every worker.
        """
        sec = self._get_item(ModuleCtx.Sec_List_Service, 'name', PubSubConfig.Joiner_Name)

        def _ok(status:'int') -> 'bool':
            return status == MultiCPUCtx.Status_OK

        def _refused(status:'int') -> 'bool':
            return status != MultiCPUCtx.Status_OK

        def _pull(slot:'int') -> 'int':
            return _pull_status(slot)

        _ = self.admin.invoke(ModuleCtx.Sub_Create_Service, {
            'topic_name_list': [PubSubConfig.Join_Topic],
            'sec_base_id': sec['id'],
            'delivery_type': PubSub.Delivery_Type.Pull,
        })
        self._wait_on_every_slot('Pull after subscribe', _pull, _ok)

        subscription = self._get_item(ModuleCtx.Sub_List_Service, 'sec_name', PubSubConfig.Joiner_Name)
        _ = self.admin.invoke(ModuleCtx.Sub_Delete_Service, {'id': subscription['id']})
        self._wait_on_every_slot('Pull after unsubscribe', _pull, _refused)

# ################################################################################################################################

    def test_topic_create_rename_and_delete(self) -> 'None':
        """ A topic created, renamed and deleted through one worker is published to, or refused, by every worker.
        """
        def _ok(status:'int') -> 'bool':
            return status == MultiCPUCtx.Status_OK

        def _refused(status:'int') -> 'bool':
            return status != MultiCPUCtx.Status_OK

        def _publish_first(slot:'int') -> 'int':
            return _publish_status(slot, ModuleCtx.Topic_Name)

        def _publish_second(slot:'int') -> 'int':
            return _publish_status(slot, ModuleCtx.Renamed_Name)

        _ = self.admin.invoke(ModuleCtx.Topic_Create_Service, {'name': ModuleCtx.Topic_Name, 'is_active': True})
        self._wait_on_every_slot('Publish after create', _publish_first, _ok)

        topic = self._get_item(ModuleCtx.Topic_List_Service, 'name', ModuleCtx.Topic_Name)
        _ = self.admin.invoke(ModuleCtx.Topic_Edit_Service, {'id': topic['id'], 'name': ModuleCtx.Renamed_Name, 'is_active': True})

        self._wait_on_every_slot('Publish to the old name after rename', _publish_first, _refused)
        self._wait_on_every_slot('Publish to the new name after rename', _publish_second, _ok)

        _ = self.admin.invoke(ModuleCtx.Topic_Delete_Service, {'id': topic['id']})
        self._wait_on_every_slot('Publish after delete', _publish_second, _refused)

# ################################################################################################################################

    def test_permission_revoke(self) -> 'None':
        """ A publish permission narrowed through one worker is refused by every worker, and restored by every worker.
        """
        def _ok(status:'int') -> 'bool':
            return status == MultiCPUCtx.Status_OK

        def _refused(status:'int') -> 'bool':
            return status != MultiCPUCtx.Status_OK

        def _publish(slot:'int') -> 'int':
            return _publish_status(slot, PubSubConfig.Wake_Topic)

        permission:'anydict' = {}
        items, _ = self.admin.get_list(ModuleCtx.Perm_List_Service)

        for item in items:
            if item['name'] == PubSubConfig.Publisher_Name and item['pattern'].startswith('pub='):
                permission = item

        def _edit(pattern:'str') -> 'None':
            _ = self.admin.invoke(ModuleCtx.Perm_Edit_Service, {
                'id': permission['id'],
                'sec_base_id': permission['sec_base_id'],
                'pattern': pattern,
                'access_type': PubSub.API_Client.Publisher,
            })

        _edit(ModuleCtx.Pattern_Revoked)

        try:
            self._wait_on_every_slot('Publish after revoke', _publish, _refused)
        finally:
            _edit(ModuleCtx.Pattern_Granted)

        self._wait_on_every_slot('Publish after restore', _publish, _ok)

# ################################################################################################################################
# ################################################################################################################################
