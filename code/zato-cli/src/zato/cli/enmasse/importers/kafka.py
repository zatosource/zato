# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import GENERIC, KAFKA, SEC_DEF_TYPE, Sec_Def_Type_Name
from zato.cli.enmasse.importers.generic import GenericConnectionImporter

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# The enmasse type name of a Bearer token definition.
_enmasse_bearer_token_type = 'bearer_token'

_sec_def_type_by_enmasse_type = {
    SEC_DEF_TYPE.BASIC_AUTH: SEC_DEF_TYPE.BASIC_AUTH,
    _enmasse_bearer_token_type: SEC_DEF_TYPE.OAUTH,
}

# ################################################################################################################################
# ################################################################################################################################

class _KafkaImporter(GenericConnectionImporter):
    """ Base class for Kafka channel and outgoing connection importers.
    """
    # Name used in error messages.
    label:'str'

    connection_secret_keys = ['password', 'secret']
    connection_required_attrs = ['name', 'address']

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

    connection_extra_field_defaults = {
        'topic': '',
        'group_id': '',
        'service': '',
        'sasl_mechanism': '',
        'ssl': False,
        'ssl_ca_file': None,
        'ssl_cert_file': None,
        'ssl_key_file': None,
    }

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

    connection_extra_field_defaults = {
        'topic': '',
        'sasl_mechanism': '',
        'ssl': False,
        'ssl_ca_file': None,
        'ssl_cert_file': None,
        'ssl_key_file': None,
    }

# ################################################################################################################################
# ################################################################################################################################
