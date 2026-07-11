# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from json import loads

# Zato
from zato.common.api import AS4, CONNECTION, URL_TYPE
from zato.common.odb.model import to_json
from zato.common.odb.query import http_soap_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    outgoing_as4_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class OutgoingAS4Exporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export(self, session:'SASession', cluster_id:'int') -> 'outgoing_as4_def_list':
        """ Exports outgoing AS4 connection definitions.
        """
        logger.info('Exporting outgoing AS4 connection definitions')

        # Our response to produce
        out:'outgoing_as4_def_list' = []

        # Get outgoing AS4 connections from database
        db_outgoing = http_soap_list(
            session,
            cluster_id,
            connection=CONNECTION.OUTGOING,
            transport=URL_TYPE.AS4,
            return_internal=False,
        )
        db_outgoing = to_json(db_outgoing)

        if not db_outgoing:
            logger.info('No outgoing AS4 connection definitions found in DB')
            return out

        logger.info('Processing %d outgoing AS4 connection definitions', len(db_outgoing))

        for outgoing_row in db_outgoing:
            logger.debug('Processing outgoing AS4 connection row %s', outgoing_row)

            exported_conn:'anydict' = {
                'name': outgoing_row['name'],
                'host': outgoing_row['host'],
                'url_path': outgoing_row['url_path'],
            }

            if (timeout := outgoing_row.get('timeout')) is not None:
                exported_conn['timeout'] = timeout

            # Unpack the opaque attributes carrying the AS4 fields - the column
            # genuinely stores a null when the connection was saved without one.
            opaque = {}

            if opaque1 := outgoing_row.get('opaque1'):
                opaque = loads(opaque1)
                if opaque is None:
                    opaque = {}

            if opaque.get('validate_tls') is False:
                exported_conn['validate_tls'] = False

            # Every AS4 field with a value is exported under its own name.
            for name in AS4.Common_Fields + AS4.Outgoing_Fields:
                if value := opaque.get(name):
                    exported_conn[name] = value

            out.append(exported_conn)

        logger.info('Successfully prepared %d outgoing AS4 connection definitions for export', len(out))

        return out

# ################################################################################################################################
# ################################################################################################################################
