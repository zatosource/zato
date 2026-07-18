# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# Zato
from zato.common.api import Audit_Config
from zato.common.audit_log.api import AuditEvent, AuditSource
from zato.common.audit_log.config_audit import ConfigScope, Secret_Mask

# Zato - test helpers
from test_mllp_audit import _get_attr_map, _wait_for_events

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_connection_type_channel = 'channel-hl7-mllp'
_generic_service_name    = 'zato.generic.connection'
_tier_service_name       = 'zato.security.tier'

# The names of everything this module creates
_channel_name = 'test-config-audit-channel'
_tier_name    = 'test-config-audit-tier'

# The user every admin API call in these tests runs as
_admin_actor = 'admin.invoke'

# ################################################################################################################################
# ################################################################################################################################

def _make_tier_rules(rate:'int') -> 'str':
    """ Builds the JSON body of one quota tier's rules.
    """
    rules = [{
        'cidr_list': ['10.0.0.0/8'],
        'time_range': [{
            'is_all_day': True,
            'disabled': False,
            'disallowed': False,
            'rate': rate,
            'burst': 20,
            'limit': 100,
            'limit_unit': 'minute',
        }],
    }]

    out = json.dumps(rules)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestConfigAuditLive:
    """ Live tests for the config-audit producers - creating, editing and deleting
    a generic connection and a quota tier all land in the audit trail with the acting
    user, a before/after summary of only the fields that changed and secrets masked.
    """

    channel_id:'int' = 0
    tier_id:'int' = 0

# ################################################################################################################################

    def test_01_create_writes_config_created(self, zato_client:'any_', zato_server:'dict') -> 'None':
        """ Creating a generic connection writes a config-created event -
        the summary carries the new state and the before side is empty.
        """
        audit_db_path = zato_server['audit_db_path']

        response = zato_client.create(
            f'{_generic_service_name}.create',
            cluster_id=1,
            name=_channel_name,
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='test.hl7.mllp.accept',
            msh3_sending_app='CONFIG_AUDIT_SYSTEM',
            pool_size=1,
        )

        assert 'id' in response
        self.__class__.channel_id = response['id']

        events = _wait_for_events(audit_db_path, _channel_name, 1, AuditEvent.Config_Created)
        assert len(events) == 1, events

        event = events[0]
        assert event['source'] == AuditSource.Config, event

        # The identity and scope are searchable attributes
        attrs = _get_attr_map(audit_db_path, event['id'])

        assert attrs['actor'] == _admin_actor, attrs
        assert attrs['effective_actor'] == _admin_actor, attrs
        assert attrs['scope'] == ConfigScope.Persistent, attrs
        assert attrs['object_type'] == Audit_Config.Object_Type.Generic_Connection, attrs

        # A creation has an empty before and the new state in the after
        summary = json.loads(event['data'])

        assert summary['before'] == {}, summary
        assert summary['after']['name'] == _channel_name, summary
        assert summary['after']['pool_size'] == 1, summary

        # The connection's secret never appears in clear text
        assert summary['after']['secret'] == Secret_Mask, summary

# ################################################################################################################################

    def test_02_edit_writes_only_the_difference(self, zato_client:'any_', zato_server:'dict') -> 'None':
        """ Editing the connection writes a config-edited event whose summary
        carries only the fields whose values changed.
        """
        audit_db_path = zato_server['audit_db_path']

        _ = zato_client.edit(
            f'{_generic_service_name}.edit',
            id=self.__class__.channel_id,
            cluster_id=1,
            name=_channel_name,
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='test.hl7.mllp.accept',
            msh3_sending_app='CONFIG_AUDIT_SYSTEM',
            pool_size=5,
        )

        events = _wait_for_events(audit_db_path, _channel_name, 1, AuditEvent.Config_Edited)
        assert len(events) == 1, events

        event = events[0]
        summary = json.loads(event['data'])

        # The changed field shows up on both sides ..
        assert summary['before']['pool_size'] == 1, summary
        assert summary['after']['pool_size'] == 5, summary

        # .. and the unchanged ones stay out of the summary.
        assert 'name' not in summary['before'], summary
        assert 'service' not in summary['after'], summary

# ################################################################################################################################

    def test_03_delete_writes_config_deleted(self, zato_client:'any_', zato_server:'dict') -> 'None':
        """ Deleting the connection writes a config-deleted event - the summary
        carries what the connection looked like and the after side is empty.
        """
        audit_db_path = zato_server['audit_db_path']

        _ = zato_client.delete(f'{_generic_service_name}.delete', id=self.__class__.channel_id)
        self.__class__.channel_id = 0

        events = _wait_for_events(audit_db_path, _channel_name, 1, AuditEvent.Config_Deleted)
        assert len(events) == 1, events

        event = events[0]
        summary = json.loads(event['data'])

        assert summary['before']['name'] == _channel_name, summary
        assert summary['after'] == {}, summary

        attrs = _get_attr_map(audit_db_path, event['id'])
        assert attrs['actor'] == _admin_actor, attrs

# ################################################################################################################################

    def test_04_the_generic_object_path_is_covered(self, zato_client:'any_', zato_server:'dict') -> 'None':
        """ Quota tiers live as generic objects - their create, edit and delete
        land in the config-audit stream the same way connections do.
        """
        audit_db_path = zato_server['audit_db_path']

        # Create ..
        response = zato_client.create(
            f'{_tier_service_name}.create',
            name=_tier_name,
            description='Config audit test tier',
            rules_json=_make_tier_rules(10),
        )

        assert 'id' in response
        self.__class__.tier_id = response['id']

        events = _wait_for_events(audit_db_path, _tier_name, 1, AuditEvent.Config_Created)
        assert len(events) == 1, events

        attrs = _get_attr_map(audit_db_path, events[0]['id'])
        assert attrs['object_type'] == Audit_Config.Object_Type.Quota_Tier, attrs
        assert attrs['actor'] == _admin_actor, attrs

        # .. edit - only the rules change, so only the rules are in the summary ..
        _ = zato_client.edit(
            f'{_tier_service_name}.edit',
            id=self.__class__.tier_id,
            name=_tier_name,
            description='Config audit test tier',
            rules_json=_make_tier_rules(50),
        )

        events = _wait_for_events(audit_db_path, _tier_name, 1, AuditEvent.Config_Edited)
        assert len(events) == 1, events

        summary = json.loads(events[0]['data'])

        assert 'rules' in summary['before'], summary
        assert 'rules' in summary['after'], summary
        assert 'name' not in summary['after'], summary

        assert summary['before']['rules'][0]['time_range'][0]['rate'] == 10, summary
        assert summary['after']['rules'][0]['time_range'][0]['rate'] == 50, summary

        # .. and delete.
        _ = zato_client.delete(f'{_tier_service_name}.delete', id=self.__class__.tier_id)
        self.__class__.tier_id = 0

        events = _wait_for_events(audit_db_path, _tier_name, 1, AuditEvent.Config_Deleted)
        assert len(events) == 1, events

        summary = json.loads(events[0]['data'])
        assert summary['before']['name'] == _tier_name, summary

# ################################################################################################################################
# ################################################################################################################################
