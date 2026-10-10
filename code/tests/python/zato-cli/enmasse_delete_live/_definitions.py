# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The YAML items of the live suite, one per section that supports deletion, each with what it depends on.
# Every object of a section is named after the section so that no two tests share an object.

# Zato
from zato.cli.enmasse.importer.delete_targets import Custom_Sections_Marker, deferred_sections, delete_order, \
    Key_Field_Name, Key_Field_Security, security_keyed_sections, Should_Delete_Key

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# Every object of the suite is named under this prefix
Prefix = 'enmasse.delete.live.'

# The service every channel and job of the suite invokes
Ping_Service = 'demo.ping'

# The username of the security definition of a section, which pub/sub keys its runtime state by
Username_Prefix = 'enmasse.delete.live.user.'

# ################################################################################################################################
# ################################################################################################################################

def name_of(section:'str') -> 'str':
    """ The name of the object the round trip of a section creates and deletes.
    """
    out = Prefix + section
    return out

# ################################################################################################################################

def security_of(section:'str') -> 'str':
    """ The name of the security definition a section's object depends on.
    """
    out = Prefix + section + '.security'
    return out

# ################################################################################################################################

def username_of(section:'str') -> 'str':
    """ The username of the security definition a section's object depends on.
    """
    out = Username_Prefix + section
    return out

# ################################################################################################################################

def topic_of(section:'str') -> 'str':
    """ The name of the topic a section's object depends on.
    """
    out = Prefix + section + '.topic'
    return out

# ################################################################################################################################

def url_path_of(section:'str') -> 'str':
    """ The URL path of the channel a section creates.
    """
    out = '/' + Prefix.replace('.', '/') + section.replace('_', '-')
    return out

# ################################################################################################################################

def basic_auth(name:'str', username:'str') -> 'anydict':
    """ One HTTP Basic Auth definition.
    """
    out = {
        'name': name,
        'type': 'basic_auth',
        'username': username,
        'password': 'Zato_Enmasse_Delete_Live_Password_1',
    }
    return out

# ################################################################################################################################

def rest_channel(name:'str', url_path:'str', **extra:'str | strlist') -> 'anydict':
    """ One REST channel invoking the ping service.
    """
    out:'anydict' = {
        'name': name,
        'service': Ping_Service,
        'url_path': url_path,
    }
    out.update(extra)
    return out

# ################################################################################################################################

def outgoing_rest(name:'str', **extra:'str | int') -> 'anydict':
    """ One outgoing REST connection.
    """
    out:'anydict' = {
        'name': name,
        'host': 'https://example.com',
        'url_path': '/' + name,
        'data_format': 'json',
    }
    out.update(extra)
    return out

# ################################################################################################################################

def topic(name:'str') -> 'anydict':
    """ One pub/sub topic.
    """
    out = {'name': name, 'description': 'Enmasse delete live'}
    return out

# ################################################################################################################################

def permission(security:'str', topics:'strlist') -> 'anydict':
    """ One pub/sub permission granting publication and subscription on the topics given.
    """
    out = {'security': security, 'pub': list(topics), 'sub': list(topics)}
    return out

# ################################################################################################################################

def subscription(security:'str', topics:'strlist') -> 'anydict':
    """ One pull subscription on the topics given.
    """
    out = {'security': security, 'delivery_type': 'pull', 'topic_list': list(topics)}
    return out

# ################################################################################################################################

def group(name:'str', members:'strlist') -> 'anydict':
    """ One API clients group.
    """
    out = {'name': name, 'members': list(members)}
    return out

# ################################################################################################################################

def quota_tier(name:'str') -> 'anydict':
    """ One quota tier with a single rule.
    """
    out = {'name': name, 'description': 'Enmasse delete live', 'rules': rate_limiting_rules()}
    return out

# ################################################################################################################################

def rate_limiting_rules() -> 'anylist':
    """ One rate limiting rule, in the shape of both a tier's rules and an object's own `rate_limiting` key.
    """
    out = [{
        'cidr_list': ['0.0.0.0/0'],
        'time_range': [{
            'is_all_day': True,
            'rate': 10,
            'burst': 20,
            'limit': 1000,
            'limit_unit': 'day',
            'disabled': False,
            'disallowed': False,
        }],
    }]
    return out

# ################################################################################################################################

def marked(section:'str', key:'str') -> 'anydict':
    """ The item that marks one object of a section for deletion.
    """
    key_field = Key_Field_Security if section in security_keyed_sections else Key_Field_Name
    out = {key_field: key, Should_Delete_Key: True}
    return out

# ################################################################################################################################

def deletion_file(section:'str', key:'str') -> 'anydict':
    """ A config that deletes one object of a section and nothing else.
    """
    out = {section: [marked(section, key)]}
    return out

# ################################################################################################################################
# ################################################################################################################################

def _round_trip_item(section:'str') -> 'anydict':
    """ The item of a section that has no dependency on another section, or the object of a section that has one,
    with the dependencies given by `_dependencies`.
    """
    name = name_of(section)
    security = security_of(section)

    items:'anydict' = {

        'security': basic_auth(name, username_of(section)),
        'groups': group(name, [security]),
        'quota_tier': quota_tier(name),
        'on_prem_gateway': {'name': name, 'is_active': False, 'hosts': ['erp.corp.local:5432']},
        'audit_retention': {'name': name, 'retention_days': 90, 'content_retention_days': 7},
        'audit_extraction': {'name': name, 'source': 'rest-channel', 'rules': [
            {'attr_name': 'order_id', 'rule_type': 'json-path', 'expression': 'order.id'}]},

        'channel_rest': rest_channel(name, url_path_of(section)),
        'channel_soap': {'name': name, 'service': Ping_Service, 'url_path': url_path_of(section),
            'soap_action': 'urn:enmasse:delete:live', 'soap_version': '1.1'},
        'channel_as4': {'name': name, 'url_path': url_path_of(section), 'as4_profile': 'peppol',
            'as4_to_party': 'enmasse-ap', 'as4_serviced_participants': '0192:991825827', 'service': Ping_Service},
        'outgoing_rest': outgoing_rest(name),
        'outgoing_soap': {'name': name, 'host': 'https://example.com', 'url_path': '/soap',
            'soap_action': 'urn:enmasse:delete:live', 'soap_version': '1.1'},
        'outgoing_as4': {'name': name, 'host': 'https://ap.example.com', 'url_path': '/as4',
            'as4_profile': 'peppol', 'as4_from_party': 'enmasse-ap', 'as4_original_sender': '0192:991825827'},

        'scheduler': {'name': name, 'service': Ping_Service, 'job_type': 'interval_based',
            'start_date': '2030-01-01 00:00:00', 'hours': 24, 'is_active': False},
        'sql': {'name': name, 'type': 'mysql', 'host': '127.0.0.1', 'port': 3306, 'db_name': 'enmasse',
            'username': 'enmasse', 'password': 'Zato_Enmasse_Delete_Live_Password_2', 'is_active': False},
        'email_smtp': {'name': name, 'host': 'smtp.example.com', 'port': 587, 'username': 'enmasse@example.com',
            'password': 'Zato_Enmasse_Delete_Live_Password_3', 'is_active': False},
        'email_imap': {'name': name, 'host': 'imap.example.com', 'port': 993, 'username': 'enmasse@example.com',
            'password': 'Zato_Enmasse_Delete_Live_Password_4', 'is_active': False},
        'odoo': {'name': name, 'host': 'odoo.example.com', 'port': 8069, 'user': 'admin',
            'password': 'Zato_Enmasse_Delete_Live_Password_5', 'database': 'enmasse', 'is_active': False},

        'channel_amqp': {'name': name, 'address': '127.0.0.1:5672', 'queue': 'enmasse', 'service': Ping_Service,
            'username': 'zato', 'password': 'Zato_Enmasse_Delete_Live_Password_6', 'is_active': False},
        'outgoing_amqp': {'name': name, 'address': '127.0.0.1:5672', 'username': 'zato',
            'password': 'Zato_Enmasse_Delete_Live_Password_6', 'is_active': False},
        'channel_azure_service_bus': {'name': name, 'address': 'enmasse.servicebus.windows.net:5671',
            'queue': 'enmasse', 'service': Ping_Service, 'username': 'policy',
            'password': 'Zato_Enmasse_Delete_Live_Password_7', 'is_active': False},
        'outgoing_azure_service_bus': {'name': name, 'address': 'enmasse.servicebus.windows.net:5671',
            'username': 'policy', 'password': 'Zato_Enmasse_Delete_Live_Password_7', 'is_active': False},

        'pubsub_topic': topic(name),
        'pubsub_permission': permission(security, [topic_of(section)]),
        'pubsub_subscription': subscription(security, [topic_of(section)]),

        'channel_openapi': {'name': name, 'is_active': False, 'url_path': url_path_of(section)},
        'mcp_gateway': {'name': name, 'is_active': True, 'url_path': url_path_of(section), 'services': [Ping_Service]},
        'rule_engine_api': {'name': name, 'is_active': False, 'url_path': url_path_of(section), 'rulesets': ['pricing']},
        'ldap': {'name': name, 'username': 'CN=enmasse,DC=example', 'auth_type': 'NTLM',
            'server_list': '127.0.0.1:389', 'password': 'Zato_Enmasse_Delete_Live_Password_9', 'is_active': False},
        'llm': {'name': name, 'model': 'gpt-4o-mini', 'address': 'https://api.openai.com/v1',
            'secret': 'Zato_Enmasse_Delete_Live_Password_10', 'is_active': False},
        'odata': {'name': name, 'address': 'https://example.com/odata/', 'odata_version': '2.0', 'auth_type': 'basic',
            'username': 'enmasse', 'secret': 'Zato_Enmasse_Delete_Live_Password_11', 'is_active': False},
        'sap': {'name': name, 'address': 'https://example.com/sap/', 'odata_version': '2.0', 'auth_type': 'basic',
            'username': 'enmasse', 'secret': 'Zato_Enmasse_Delete_Live_Password_12', 'is_active': False},
        'mongodb': {'name': name, 'server_list': '127.0.0.1:27017', 'username': 'enmasse',
            'password': 'Zato_Enmasse_Delete_Live_Password_14', 'is_active': False},
        'microsoft_cloud': {'name': name, 'is_active': False, 'client_id': '12345678-1234-1234-1234-123456789abc',
            'secret_value': 'Zato_Enmasse_Delete_Live_Password_15', 'scopes': 'Mail.Read',
            'tenant_id': '87654321-4321-4321-4321-cba987654321'},
        'microsoft_fabric': {'name': name, 'is_active': False, 'address': 'https://api.fabric.microsoft.com/v1',
            'client_id': '34567890-3456-3456-3456-34567890abcd', 'client_secret': 'Zato_Enmasse_Delete_Live_Password_16',
            'tenant_id': '87654321-6543-6543-6543-edcba9876543'},
        'microsoft_power_automate': {'name': name, 'is_active': False, 'address': 'https://api.flow.microsoft.com',
            'client_id': '23456789-2345-2345-2345-23456789abcd', 'client_secret': 'Zato_Enmasse_Delete_Live_Password_17',
            'tenant_id': '98765432-5432-5432-5432-dcba98765432',
            'environment_id': 'Default-98765432-5432-5432-5432-dcba98765432'},
        'microsoft_teams': {'name': name, 'is_active': False, 'client_id': '45678901-4567-4567-4567-4567890abcde',
            'secret_value': 'Zato_Enmasse_Delete_Live_Password_18', 'scopes': 'https://graph.microsoft.com/.default',
            'tenant_id': '87654321-7654-7654-7654-fedcba987654'},
        'slack': {'name': name, 'is_active': False, 'token': 'Zato_Enmasse_Delete_Live_Password_19'},
        'confluence': {'name': name, 'address': 'https://example.atlassian.net', 'username': 'enmasse@example.com',
            'password': 'Zato_Enmasse_Delete_Live_Password_20', 'is_active': False},
        'jira': {'name': name, 'address': 'https://example.atlassian.net', 'username': 'enmasse@example.com',
            'password': 'Zato_Enmasse_Delete_Live_Password_21', 'is_active': False},
        'salesforce': {'name': name, 'address': 'https://example.my.salesforce.com', 'username': 'enmasse@example.com',
            'password': 'Zato_Enmasse_Delete_Live_Password_22', 'consumer_key': 'enmasse-consumer-key',
            'consumer_secret': 'Zato_Enmasse_Delete_Live_Password_23', 'is_active': False},
        'channel_kafka': {'name': name, 'is_active': False, 'address': '127.0.0.1:9092', 'topic': 'enmasse',
            'group_id': 'enmasse', 'service': Ping_Service},
        'outgoing_kafka': {'name': name, 'is_active': False, 'address': '127.0.0.1:9092', 'topic': 'enmasse'},
        'channel_ibm_mq': {'name': name, 'is_active': False, 'address': 'mq.example.com:1414', 'queue_manager': 'QM1',
            'mq_channel_name': 'DEV.APP.SVRCONN', 'queue': 'ENMASSE.IN', 'service': Ping_Service, 'username': 'app',
            'password': 'Zato_Enmasse_Delete_Live_Password_24'},
        'outgoing_ibm_mq': {'name': name, 'is_active': False, 'address': 'mq.example.com:1414', 'queue_manager': 'QM1',
            'mq_channel_name': 'DEV.APP.SVRCONN', 'queue': 'ENMASSE.OUT', 'username': 'app',
            'password': 'Zato_Enmasse_Delete_Live_Password_24'},
        'outgoing_graphql': {'name': name, 'is_active': False, 'address': 'https://api.github.com/graphql'},
        'outgoing_grpc': {'name': name, 'is_active': False, 'address': 'billing.example.com:50051', 'is_tls': False,
            'stub_module': 'billing_pb2_grpc', 'stub_class': 'BillingServiceStub'},
        'channel_mllp': {'name': name, 'service': Ping_Service, 'is_active': False},
        'outgoing_mllp': {'name': name, 'address': '127.0.0.1:2575', 'is_active': False},
        'outgoing_fhir': {'name': name, 'address': 'https://fhir.example.com/r4', 'security': security, 'is_active': False},
        'sftp': {'name': name, 'address': 'sftp.example.com:22', 'username': 'enmasse',
            'password': 'Zato_Enmasse_Delete_Live_Password_25', 'is_active': False},
        'smb': {'name': name, 'host': 'smb.example.com', 'port': 445, 'username': 'enmasse',
            'password': 'Zato_Enmasse_Delete_Live_Password_26', 'is_active': False},
        'ftp': {'name': name, 'host': 'ftp.example.com', 'port': 21, 'username': 'enmasse',
            'password': 'Zato_Enmasse_Delete_Live_Password_27', 'is_active': False},
        'outgoing_as2': {'name': name, 'as2_from': 'Enmasse', 'as2_to': 'Partner',
            'endpoint_url': 'https://as2.example.com/as2', 'is_active': False},
        'elastic_search': {'name': name, 'is_active': False, 'address_list': ['http://127.0.0.1:9200']},
    }

    out = items[section]
    return out

# ################################################################################################################################

def _dependencies(section:'str') -> 'anydict':
    """ What the object of a section needs to exist before it does, by section.
    """
    security = security_of(section)

    out:'anydict' = {}

    if section in ('groups', 'pubsub_permission', 'pubsub_subscription', 'outgoing_fhir'):
        out['security'] = [basic_auth(security, username_of(section))]

    if section in ('pubsub_permission', 'pubsub_subscription'):
        out['pubsub_topic'] = [topic(topic_of(section))]

    if section == 'pubsub_subscription':
        out['pubsub_permission'] = [permission(security, [topic_of(section)])]

    return out

# ################################################################################################################################

def creation_file(section:'str') -> 'anydict':
    """ A config that creates the object of a section along with everything it depends on.
    """
    out = _dependencies(section)
    out[section] = [_round_trip_item(section)]
    return out

# ################################################################################################################################

def round_trip_key(section:'str') -> 'str':
    """ The key the deletion file of a section marks - the security name of a security-keyed section, the name otherwise.
    """
    if section in security_keyed_sections:
        out = security_of(section)
    else:
        out = name_of(section)

    return out

# ################################################################################################################################

# Every section the round trip covers, in the order deletions run in, the deferred one last
round_trip_sections:'strlist' = [section for section in delete_order if section != Custom_Sections_Marker]
round_trip_sections.extend(deferred_sections)

# ################################################################################################################################
# ################################################################################################################################
