# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# This module is deployed into the server of the live suite through its pickup directory. Its service reports whether
# an object of a section is present at runtime - in the config maps, the outgoing wrappers, the URL routing,
# the pub/sub matcher and subscriptions, or in the ODB for the object types the server holds nowhere else.

# stdlib
from contextlib import closing

# Zato
from zato.cli.enmasse.importer.delete_targets import generic_object_sections, generic_sections, http_soap_sections
from zato.common.api import CONNECTION, Groups
from zato.common.odb.model import GenericObject, Job, PubSubTopic
from zato.common.typing_ import cast_
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The config store attributes security definitions are kept under, by type
_security_stores = ('basic_auth', 'apikey', 'oauth', 'ntlm', 'mtls', 'spnego', 'wss')

# The config store attributes outgoing HTTP connections are kept under, by transport
_outgoing_stores = {
    'plain_http': 'out_plain_http',
    'soap':       'out_soap',
    'as4':        'out_as4',
}

# The sections whose objects are AMQP connectors
_amqp_sections = ('channel_amqp', 'outgoing_amqp', 'channel_azure_service_bus', 'outgoing_azure_service_bus')

# The sections the server holds in the ODB only, by model
_odb_models = {
    'scheduler':    Job,
    'pubsub_topic': PubSubTopic,
}

# The generic object sections whose runtime state is a manager rather than the ODB
_groups_section     = 'groups'
_quota_tier_section = 'quota_tier'

# The operations the pattern matcher evaluates
_operation_publish   = 'publish'
_operation_subscribe = 'subscribe'

# ################################################################################################################################
# ################################################################################################################################

class RuntimePresence(Service):
    """ Reports whether the object of a section is present at runtime.
    """
    name = 'enmasse.delete.live.runtime'
    input = 'section', 'name', '-topic'
    output = 'is_present'

    def handle(self) -> 'None':

        section = self.request.input.section
        name = self.request.input.name
        topic = self.request.input.topic

        server = cast_('any_', self.server)
        config_manager = server.config_manager
        config_store = config_manager.config_store

        # Security definitions are in the store of their type ..
        if section == 'security':
            is_present = any(name in getattr(config_store, store) for store in _security_stores)

        # .. channels are in the URL routing, outgoing connections in the store of their transport ..
        elif section in http_soap_sections:
            connection, transport = http_soap_sections[section]
            if connection == CONNECTION.CHANNEL:
                is_present = config_manager.request_dispatcher.url_data.get_channel_by_name(name) is not None
            else:
                is_present = name in getattr(config_store, _outgoing_stores[transport])

        # .. generic connections are in the API map of their type ..
        elif section in generic_sections:
            is_present = name in config_manager.generic_conn_api[generic_sections[section]]

        # .. AMQP objects are connectors ..
        elif section in _amqp_sections:
            is_present = name in config_manager.amqp_api.connectors

        # .. SQL pools are wrappers, Odoo connections are in their store ..
        elif section == 'sql':
            is_present = name in config_manager.sql_pool_store.wrappers

        elif section == 'odoo':
            is_present = name in config_store.out_odoo

        # .. email connections are in the store of their API ..
        elif section == 'email_smtp':
            is_present = self._is_in_email_api(config_manager.email_smtp_api, name)

        elif section == 'email_imap':
            is_present = self._is_in_email_api(config_manager.email_imap_api, name)

        # .. groups and quota tiers have managers of their own ..
        elif section == _groups_section:
            group_list = server.groups_manager.get_group_list(Groups.Type.API_Clients)
            is_present = any(item['name'] == name for item in group_list)

        elif section == _quota_tier_section:
            tier_list = server.quota_tiers_manager.get_tier_list()
            is_present = any(item['name'] == name for item in tier_list)

        # .. a permission is a client of the pattern matcher, keyed by username ..
        elif section == 'pubsub_permission':
            matcher = server.pubsub_pattern_matcher
            can_publish = matcher.evaluate(name, topic, _operation_publish).is_ok
            can_subscribe = matcher.evaluate(name, topic, _operation_subscribe).is_ok
            is_present = can_publish or can_subscribe

        # .. a subscription is a sub_key, keyed by username, with configs under its topics ..
        elif section == 'pubsub_subscription':
            is_present = self._is_subscribed(server, name, topic)

        # .. and everything else is read from the ODB.
        else:
            is_present = self._is_in_odb(section, name)

        self.response.payload.is_present = is_present

# ################################################################################################################################

    def _is_in_email_api(self, api:'any_', name:'str') -> 'bool':
        """ Whether an email API has a connection of the name given, inactive ones included.
        """
        try:
            _ = api.get(name, skip_inactive=True)
        except KeyError:
            out = False
        else:
            out = True

        return out

# ################################################################################################################################

    def _is_subscribed(self, server:'any_', username:'str', topic:'str') -> 'bool':
        """ Whether the user has a subscription, on the topic given or on any topic when none is given.
        """
        sub_key = server.pubsub_subscriptions.get_sub_key_by_username(username)

        if sub_key is None:
            return False

        pubsub_subs = server.config_manager.config_store.pubsub_subs

        if topic:
            topic_names = [topic]
        else:
            topic_names = list(pubsub_subs)

        for topic_name in topic_names:
            for sub_config in pubsub_subs.get(topic_name, []):
                if sub_config['sub_key'] == sub_key:
                    return True

        return False

# ################################################################################################################################

    def _is_in_odb(self, section:'str', name:'str') -> 'bool':
        """ Whether the ODB has a row of the section under the name given.
        """
        cluster_id = self.server.cluster_id

        with closing(self.odb.session()) as session:

            if section in _odb_models:
                model = _odb_models[section]
                query = session.query(model).filter_by(cluster_id=cluster_id, name=name)
            else:
                type_ = generic_object_sections[section][0]
                query = session.query(GenericObject).filter_by(cluster_id=cluster_id, type_=type_, name=name)

            out = query.first() is not None

        return out

# ################################################################################################################################
# ################################################################################################################################
