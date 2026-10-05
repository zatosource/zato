# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# Zato
from zato.common.api import GENERIC, HTTP_SOAP, KAFKA, SEC_DEF_TYPE, Sec_Def_Type_Name
from zato.common.util.delivery_config import Delivery_Field_Defaults
from zato.cli.enmasse.importers.generic import GenericConnectionImporter
from zato.cli.enmasse.util.delivery import prepare_delivery_fields
from zato.cli.enmasse.util.invocation import Retry_Field_Defaults

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strlist, strtuple
    any_ = any_
    anylist = anylist
    strlist = strlist
    strtuple = strtuple

# ################################################################################################################################
# ################################################################################################################################

_consumer = KAFKA.Consumer
_producer = KAFKA.Producer
_routing = KAFKA.Routing

# The enmasse type name of a Bearer token definition.
_enmasse_bearer_token_type = 'bearer_token'

_sec_def_type_by_enmasse_type = {
    SEC_DEF_TYPE.BASIC_AUTH: SEC_DEF_TYPE.BASIC_AUTH,
    _enmasse_bearer_token_type: SEC_DEF_TYPE.OAUTH,
}

# The fields both kinds of connection store
_common_extra_field_defaults = {
    'sasl_mechanism': '',
    'ssl': False,
    'ssl_ca_file': None,
    'ssl_cert_file': None,
    'ssl_key_file': None,
    KAFKA.Field_SSL_Key_Password: '',
}

# A channel's fields
Channel_Extra_Field_Defaults = dict(_common_extra_field_defaults)
Channel_Extra_Field_Defaults.update({
    'topic': '',
    'group_id': '',
    'service': '',
})
Channel_Extra_Field_Defaults.update(_consumer.Defaults)
Channel_Extra_Field_Defaults.update(Retry_Field_Defaults)
Channel_Extra_Field_Defaults.update(Delivery_Field_Defaults)

# An outgoing connection's fields
Outgoing_Extra_Field_Defaults = dict(_common_extra_field_defaults)
Outgoing_Extra_Field_Defaults.update({
    'topic': '',
    'is_audit_log_active': True,
    'is_audit_export_payload_active': False,
})
Outgoing_Extra_Field_Defaults.update(_producer.Defaults)
Outgoing_Extra_Field_Defaults.update(Retry_Field_Defaults)
Outgoing_Extra_Field_Defaults.update(Delivery_Field_Defaults)

# The fields that are whole numbers, by kind of connection
Channel_Int_Fields = _consumer.IntFieldList + tuple(Retry_Field_Defaults)
Outgoing_Int_Fields = _producer.IntFieldList + tuple(Retry_Field_Defaults)

# ################################################################################################################################
# ################################################################################################################################

def topics_to_text(value:'any_') -> 'str':
    """ The stored form of a channel's topic list, one per line, out of a YAML list or text.
    """
    if not value:
        return ''

    if isinstance(value, str):
        names = value.replace(',', '\n').splitlines()
    else:
        names = value

    out:'strlist' = []

    for name in names:
        name = name.strip()
        if name:
            out.append(name)

    text = '\n'.join(out)
    return text

# ################################################################################################################################

def routing_to_text(value:'any_', conn_name:'str') -> 'str':
    """ The stored form of a channel's routing rules, as JSON text, out of a YAML list of mappings.
    """
    if not value:
        return ''

    if isinstance(value, str):
        return value

    rules:'anylist' = []

    for idx, rule in enumerate(value, 1):

        if not isinstance(rule, dict):
            raise Exception(f'Routing rule #{idx} of Kafka channel `{conn_name}` must be a mapping, not `{rule!r}`')

        for key in rule:
            if key not in _routing.KeyList:
                raise Exception(f'Routing rule #{idx} of Kafka channel `{conn_name}` has an unknown key `{key}`')

        if not rule.get(_routing.Key_Service):
            raise Exception(f'Routing rule #{idx} of Kafka channel `{conn_name}` needs a service')

        stored = {}

        for key in _routing.KeyList:
            if key in rule:
                stored[key] = rule[key]
            else:
                stored[key] = ''

        rules.append(stored)

    out = dumps(rules)
    return out

# ################################################################################################################################

def validate_int_fields(connection_def:'anydict', field_names:'strtuple', label:'str') -> 'None':
    """ Each whole-number field has to be one, and not negative.
    """
    name = connection_def['name']

    for field in field_names:
        value = connection_def.get(field)

        if value is None:
            continue

        # A bool is an int, and not a count.
        if isinstance(value, bool) or not isinstance(value, int):
            raise Exception(f'`{field}` of {label} `{name}` must be an integer, not `{value!r}`')

        if value < 0:
            raise Exception(f'`{field}` of {label} `{name}` must not be negative, not `{value}`')

# ################################################################################################################################

def validate_choice(connection_def:'anydict', field:'str', choices:'any_', label:'str') -> 'None':
    """ A field with a fixed set of values has to carry one of them.
    """
    value = connection_def.get(field)

    if value is None:
        return

    allowed:'strlist' = []

    for item in choices:
        allowed.append(item.id)

    if value not in allowed:
        name = connection_def['name']
        raise Exception(f'`{field}` of {label} `{name}` must be one of `{allowed}`, not `{value!r}`')

# ################################################################################################################################
# ################################################################################################################################

class _KafkaImporter(GenericConnectionImporter):
    """ Base class for Kafka channel and outgoing connection importers.
    """
    # Name used in error messages.
    label:'str'

    connection_secret_keys = ['password', 'secret']
    connection_required_attrs = ['name', 'address']

    opaque_secret_keys = (KAFKA.Field_SSL_Key_Password,)

# ################################################################################################################################

    def resolve_references(self, connection_def:'anydict') -> 'None':
        """ Resolves the named security definition into its id and type and checks it matches the SASL mechanism.
        """
        name = connection_def['name']
        security_name = connection_def.pop('security', None)
        sasl_mechanism = connection_def.get('sasl_mechanism')

        if not security_name:

            # A later pass sees the id an earlier one stored, not the name.
            if connection_def.get('security_id'):
                return

            if sasl_mechanism:
                msg = f'{self.label} `{name}` has SASL mechanism `{sasl_mechanism}` but no security definition'
                raise Exception(msg)

            return

        if not sasl_mechanism:
            raise Exception(f'{self.label} `{name}` has security definition `{security_name}` but no SASL mechanism')

        if sasl_mechanism not in KAFKA.Mechanism_Sec_Def_Type:
            raise Exception(f'{self.label} `{name}` has an unsupported SASL mechanism -> `{sasl_mechanism}`')

        sec_def = self.importer.sec_defs.get(security_name)

        if not sec_def:
            raise Exception(f'Security definition `{security_name}` not found for {self.label} `{name}`')

        enmasse_type = sec_def['type']

        if enmasse_type not in _sec_def_type_by_enmasse_type:
            msg = f'{self.label} `{name}` cannot use security definition `{security_name}` of type `{enmasse_type}`'
            raise Exception(msg)

        auth_type = _sec_def_type_by_enmasse_type[enmasse_type]
        expected_auth_type = KAFKA.Mechanism_Sec_Def_Type[sasl_mechanism]

        if auth_type != expected_auth_type:
            expected_name = Sec_Def_Type_Name[expected_auth_type]
            actual_name = Sec_Def_Type_Name[auth_type]
            msg = f'{self.label} `{name}` uses SASL mechanism `{sasl_mechanism}` which requires a {expected_name} ' + \
                f'security definition, not {actual_name}'
            raise Exception(msg)

        connection_def['security_id'] = sec_def['id']
        connection_def['security_name'] = security_name
        connection_def['auth_type'] = auth_type

# ################################################################################################################################
# ################################################################################################################################

class ChannelKafkaImporter(_KafkaImporter):

    label = 'Kafka channel'
    connection_type = GENERIC.CONNECTION.TYPE.CHANNEL_KAFKA

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.CHANNEL_KAFKA,
        'is_internal': False,
        'is_channel': True,
        'is_outconn': False,
        'pool_size': 1,
    }

    connection_extra_field_defaults = Channel_Extra_Field_Defaults

# ################################################################################################################################

    def resolve_references(self, connection_def:'anydict') -> 'None':
        """ Resolves the security definition and turns the topic list and the routing rules into their stored text.
        """
        super().resolve_references(connection_def)

        name = connection_def['name']

        # A file with `topic` alone has a one-entry list.
        topics = connection_def.get(_consumer.Field_Topics)

        if not topics:
            topics = connection_def.get('topic')

        topics_text = topics_to_text(topics)
        connection_def[_consumer.Field_Topics] = topics_text

        # `topic` is the first entry of the list.
        if topics_text:
            first_topic = topics_text.split('\n')[0]
        else:
            first_topic = ''

        connection_def['topic'] = first_topic

        if _consumer.Field_Routing in connection_def:
            connection_def[_consumer.Field_Routing] = routing_to_text(connection_def[_consumer.Field_Routing], name)

# ################################################################################################################################

    def validate_definition(self, connection_def:'anydict') -> 'None':
        """ A channel needs at least one topic and a service, and what it carries of the consumer's settings
        and the delivery fields has to be what each field takes.
        """
        name = connection_def['name']

        if not connection_def.get(_consumer.Field_Topics):
            raise Exception(f'{self.label} `{name}` needs at least one topic')

        if not connection_def.get('service'):
            raise Exception(f'{self.label} `{name}` needs a service')

        validate_choice(connection_def, _consumer.Field_Auto_Offset_Reset, KAFKA.AUTO_OFFSET_RESET(), self.label)
        validate_int_fields(connection_def, Channel_Int_Fields, self.label)

        # A channel has no delivery queue.
        connection_def[HTTP_SOAP.Queue.Field_Use_Queue] = False

        prepare_delivery_fields(connection_def, self.label)

# ################################################################################################################################
# ################################################################################################################################

class OutgoingKafkaImporter(_KafkaImporter):

    label = 'Outgoing Kafka connection'
    connection_type = GENERIC.CONNECTION.TYPE.OUTCONN_KAFKA

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_KAFKA,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': True,
        'pool_size': 1,
    }

    connection_extra_field_defaults = Outgoing_Extra_Field_Defaults

# ################################################################################################################################

    def validate_definition(self, connection_def:'anydict') -> 'None':
        """ What a connection carries of the producer's settings and the delivery fields has to be what each field takes.
        """
        # The field is stored as text.
        if _producer.Field_Acks in connection_def:
            connection_def[_producer.Field_Acks] = str(connection_def[_producer.Field_Acks])

        validate_choice(connection_def, _producer.Field_Compression, KAFKA.COMPRESSION(), self.label)
        validate_choice(connection_def, _producer.Field_Acks, KAFKA.ACKS(), self.label)
        validate_int_fields(connection_def, Outgoing_Int_Fields, self.label)

        prepare_delivery_fields(connection_def, self.label)

# ################################################################################################################################
# ################################################################################################################################
