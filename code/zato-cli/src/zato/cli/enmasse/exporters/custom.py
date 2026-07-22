# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.cli.enmasse.config import ModuleCtx
from zato.cli.enmasse.importers.custom import column_fields, connection_type_to_custom_key
from zato.common.api import GENERIC
from zato.common.const import SECRETS
from zato.common.odb.model import to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, dictlist, strdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# Values with these prefixes are stored encrypted and never leave the database through enmasse.
_secret_prefixes = (SECRETS.Encrypted_Indicator, SECRETS.PREFIX)

# Column-backed and bookkeeping attributes that are not fields a connector class declares.
_skip_fields = {
    'id',
    'name',
    'type_',
    'is_active',
    'is_internal',
    'is_channel',
    'is_outconn',
    'is_outgoing',
    'cluster_id',
    'cache_expiry',
    'address',
    'port',
    'timeout',
    'data_format',
    'version',
    'extra',
    'pool_size',
    'username',
    'username_type',
    'secret',
    'secret_type',
    'conn_def_id',
}

# ################################################################################################################################
# ################################################################################################################################

def get_builtin_connection_types() -> 'set':
    """ Returns the full connection types of all the built-in generic connections, e.g. outconn-ldap.
    """
    out = set()

    for name in dir(GENERIC.CONNECTION.TYPE):
        if not name.startswith('_'):
            out.add(getattr(GENERIC.CONNECTION.TYPE, name))

    return out

# ################################################################################################################################
# ################################################################################################################################

class CustomConnectorExporter:
    """ Exports definitions of custom connector types built with the Connector SDK.
    Each type becomes its own top-level key with the custom_ prefix, e.g. custom_crm.
    """

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def _export_one(self, row:'anydict') -> 'strdict':
        """ Turns one database row into its YAML representation - the name along with
        all the fields the connector class declares, except the encrypted ones.
        """

        # Merge the opaque attributes into the row ..
        if GENERIC.ATTR_NAME in row:
            opaque = parse_instance_opaque_attr(row)
            row.update(opaque)
            del row[GENERIC.ATTR_NAME]

        # .. the name always comes first ..
        item:'strdict' = {
            'name': row['name'],
        }

        # .. inactive definitions carry the flag explicitly, active is the default ..
        if not row['is_active']:
            item['is_active'] = False

        # .. declared fields whose names match database columns are stored in these columns ..
        for name in column_fields:
            value = row[name]
            if value is not None:
                item[name] = value

        # .. and the remaining declared fields follow in a stable order.
        for key in sorted(row):

            # Column-backed and bookkeeping attributes are not declared fields ..
            if key in _skip_fields:
                continue

            value = row[key]

            # .. encrypted values never leave the database through enmasse.
            if isinstance(value, str) and value.startswith(_secret_prefixes):
                continue

            item[key] = value

        return item

# ################################################################################################################################

    def export(self, session:'SASession', cluster_id:'int') -> 'dict[str, dictlist]':
        """ Exports all the definitions of custom connector types, mapping each type's
        top-level YAML key, e.g. custom_crm, to the list of its definitions.
        """
        logger.info('Exporting custom connector definitions')

        # Everything of a type from this set is a built-in connection, not a custom one.
        builtin_types = get_builtin_connection_types()

        # Get all the generic connections there are - custom types are unknown upfront,
        # so they can only be recognized by what they are not.
        db_connections = connection_list(session, cluster_id)
        connections = to_json(db_connections, return_as_dict=True)

        out:'dict[str, dictlist]' = {}

        for row in connections:

            type_ = row['type_']

            # Only outgoing connections can be custom connector types ..
            if not type_.startswith(ModuleCtx.Custom_Type_Prefix):
                continue

            # .. and built-in types have their own dedicated exporters.
            if type_ in builtin_types:
                continue

            yaml_key = connection_type_to_custom_key(type_)
            item = self._export_one(row)

            if yaml_key not in out:
                out[yaml_key] = []
            out[yaml_key].append(item)

        for yaml_key, items in out.items():
            logger.info('Prepared %d custom connector definitions for export (%s)', len(items), yaml_key)

        return out

# ################################################################################################################################
# ################################################################################################################################
