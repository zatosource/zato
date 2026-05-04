# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import GENERIC
from zato.cli.enmasse.importers.generic import GenericConnectionImporter

class KafkaChannelImporter(GenericConnectionImporter):

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
        'ssl': False,
        'ssl_ca_file': None,
        'ssl_cert_file': None,
        'ssl_key_file': None,
    }

    connection_secret_keys = ['password', 'secret']
    connection_required_attrs = ['name', 'address']

class KafkaOutgoingImporter(GenericConnectionImporter):

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
        'ssl': False,
        'ssl_ca_file': None,
        'ssl_cert_file': None,
        'ssl_key_file': None,
    }

    connection_secret_keys = ['password', 'secret']
    connection_required_attrs = ['name', 'address']
