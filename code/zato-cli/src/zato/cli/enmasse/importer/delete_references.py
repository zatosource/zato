# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# This module checks a YAML config in which items are marked should_delete for items that are not marked yet refer
# to an object the same file deletes. Such a file is refused before anything is written.

# Zato
from zato.cli.enmasse.importer.delete_targets import Section_Alert_Notifications, Should_Delete_Key, get_key_field
from zato.cli.enmasse.util.common import Security_Alias_Key, Security_Key
from zato.common.alerting import object_config
from zato.common.api import MCP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, stranydict, strlist

    deletions_dict = dict[str, strlist]
    unmarked_dict  = dict[str, anylist]

# ################################################################################################################################
# ################################################################################################################################

# The sections whose items name a security definition under the security key
security_referencing_sections = (
    'channel_rest', 'channel_soap', 'channel_as4', 'outgoing_rest', 'outgoing_soap', 'channel_kafka', 'outgoing_kafka',
    'outgoing_graphql', 'outgoing_grpc', 'channel_mllp', 'pubsub_permission', 'pubsub_subscription',
)

# The sections whose items name security groups, with the field the names are listed under
group_referencing_fields = {
    'channel_rest':    'groups',
    'channel_soap':    'groups',
    'mcp_gateway':     'security_groups',
    'rule_engine_api': 'security_groups',
}

# The sections whose items may name a quota tier
quota_tier_referencing_sections = ('security', 'groups', 'channel_rest')

# The sections whose items name a pub/sub topic in a single field, with the field
topic_referencing_fields = {
    'outgoing_as2': 'inbound_topic',
    'channel_as4':  'as4_inbound_topic',
}

# The section each connection allow list of an MCP gateway refers to
mcp_connection_list_sections = {
    'rest_connections':                     'outgoing_rest',
    'soap_connections':                     'outgoing_soap',
    'sql_connections':                      'sql',
    'microsoft_365_connections':            'microsoft_cloud',
    'microsoft_teams_connections':          'microsoft_teams',
    'microsoft_fabric_connections':         'microsoft_fabric',
    'microsoft_power_automate_connections': 'microsoft_power_automate',
    'sap_connections':                      'sap',
    'confluence_connections':               'confluence',
    'odoo_connections':                     'odoo',
    'es_connections':                       'elastic_search',
}

# The section an email connection of an alert refers to, by the kind the value is encoded with
email_connection_sections = {
    object_config.Email_Conn_Type_SMTP: 'email_smtp',
    object_config.Email_Conn_Type_IMAP: 'email_imap',
}

# The section the LLM connection of an alert refers to
Section_LLM = 'llm'

# ################################################################################################################################
# ################################################################################################################################

class ReferenceChecker:
    """ Walks the unmarked items of a config and refuses the first reference to an object the config deletes.
    """

    def __init__(self, deletions:'deletions_dict', unmarked:'unmarked_dict', yaml_config:'stranydict') -> 'None':
        self.deletions = deletions
        self.unmarked = unmarked
        self.yaml_config = yaml_config

# ################################################################################################################################

    def _is_deleted(self, section:'str', key:'str') -> 'bool':
        out = key in self.deletions.get(section, [])
        return out

# ################################################################################################################################

    def _refuse(self, section:'str', item:'stranydict', field:'str', referenced_section:'str', referenced_key:'str') -> 'None':
        if section == Section_Alert_Notifications:
            item_key = section
        else:
            item_key = item.get(get_key_field(section))

        raise Exception(
            f'Item `{item_key}` of section `{section}` refers in `{field}` to `{referenced_section}` `{referenced_key}` ' + \
            f'which the same file marks `{Should_Delete_Key}`')

# ################################################################################################################################

    def _check_value(self, section:'str', item:'stranydict', field:'str', referenced_section:'str') -> 'None':
        """ Checks one field whose value is the key of an object in another section.
        """
        value = item.get(field)

        if value and self._is_deleted(referenced_section, value):
            self._refuse(section, item, field, referenced_section, value)

# ################################################################################################################################

    def _check_list(self, section:'str', item:'stranydict', field:'str', referenced_section:'str') -> 'None':
        """ Checks one field whose value lists the keys of objects in another section.
        """
        values = item.get(field)

        if not values:
            return

        # A list of one line may be written as a plain string
        if isinstance(values, str):
            values = [values]

        for value in values:
            if self._is_deleted(referenced_section, value):
                self._refuse(section, item, field, referenced_section, value)

# ################################################################################################################################

    def _check_security(self, section:'str', item:'stranydict') -> 'None':

        # The alternative spelling of the security key is accepted the way the importers accept it
        if Security_Key in item:
            field = Security_Key
        else:
            field = Security_Alias_Key

        self._check_value(section, item, field, 'security')

# ################################################################################################################################

    def _check_alerts(self, section:'str', item:'stranydict') -> 'None':
        """ Checks the email and LLM connections an item's alerts mapping names.
        """
        alerts = item.get('alerts')

        if not alerts:
            return

        self._check_alert_connections(section, item, alerts)

# ################################################################################################################################

    def _check_alert_connections(self, section:'str', item:'stranydict', alerts:'stranydict') -> 'None':

        email_connection = alerts.get(object_config.Email_Connection_Field)

        if email_connection:
            kind, name = object_config.decode_email_connection(email_connection)

            if kind in email_connection_sections:
                referenced_section = email_connection_sections[kind]
                if self._is_deleted(referenced_section, name):
                    self._refuse(section, item, object_config.Email_Connection_Field, referenced_section, name)

        llm_connection = alerts.get(object_config.LLM_Connection_Field)

        if llm_connection and self._is_deleted(Section_LLM, llm_connection):
            self._refuse(section, item, object_config.LLM_Connection_Field, Section_LLM, llm_connection)

# ################################################################################################################################

    def _check_item(self, section:'str', item:'stranydict') -> 'None':

        if section in security_referencing_sections:
            self._check_security(section, item)

        if section == 'groups':
            self._check_list(section, item, 'members', 'security')

        if section in group_referencing_fields:
            self._check_list(section, item, group_referencing_fields[section], 'groups')

        if section in quota_tier_referencing_sections:
            self._check_value(section, item, 'quota_tier', 'quota_tier')

        if section == 'pubsub_subscription':
            self._check_list(section, item, 'topic_list', 'pubsub_topic')
            self._check_value(section, item, 'push_rest_endpoint', 'outgoing_rest')

        if section == 'channel_openapi':
            self._check_list(section, item, 'rest_channel_list', 'channel_rest')

        if section in topic_referencing_fields:
            self._check_value(section, item, topic_referencing_fields[section], 'pubsub_topic')

        if section == 'mcp_gateway':
            for list_key in MCP.Connection_List_Keys:
                self._check_list(section, item, list_key, mcp_connection_list_sections[list_key])

        self._check_alerts(section, item)

# ################################################################################################################################

    def check(self) -> 'None':

        for section, items in self.unmarked.items():
            for item in items:
                self._check_item(section, item)

        # The notification targets are one mapping and name their connections the way an item's alerts do
        notifications = self.yaml_config.get(Section_Alert_Notifications)

        if notifications:
            self._check_alert_connections(Section_Alert_Notifications, notifications, notifications)

# ################################################################################################################################
# ################################################################################################################################

def check_references(deletions:'deletions_dict', unmarked:'unmarked_dict', yaml_config:'stranydict') -> 'None':
    """ Refuses a config in which an unmarked item refers to an object the config marks for deletion.
    """
    checker = ReferenceChecker(deletions, unmarked, yaml_config)
    checker.check()

# ################################################################################################################################
# ################################################################################################################################
