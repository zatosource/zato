# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from json import loads

# Zato
from zato.cli.enmasse.util import export_invocation_fields, Invocation_Fields_SOAP
from zato.common.api import CONNECTION, URL_TYPE
from zato.common.odb.model import to_json
from zato.common.odb.query import http_soap_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    outgoing_soap_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class OutgoingSOAPExporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session: 'SASession', cluster_id: 'int') -> 'outgoing_soap_def_list':
        """ Exports outgoing SOAP connection definitions.
        """
        logger.info('Exporting outgoing SOAP connection definitions')

        # Get outgoing SOAP connections from database
        db_outgoing = http_soap_list(
            session,
            cluster_id,
            connection=CONNECTION.OUTGOING,
            transport=URL_TYPE.SOAP,
            return_internal=False,
        )
        db_outgoing = to_json(db_outgoing)

        if not db_outgoing:
            logger.info('No outgoing SOAP connection definitions found in DB')
            return []

        exported_outgoing: 'outgoing_soap_def_list' = []
        logger.info('Processing %d outgoing SOAP connection definitions', len(db_outgoing))

        for outgoing_row in db_outgoing:
            logger.debug('Processing outgoing SOAP connection row %s', outgoing_row)

            exported_conn: 'anydict' = {
                'name': outgoing_row['name'],
                'host': outgoing_row['host'],
                'url_path': outgoing_row['url_path'],
            }

            if security_name := outgoing_row.get('security_name'):
                exported_conn['security'] = security_name

            if soap_action := outgoing_row.get('soap_action'):
                exported_conn['soap_action'] = soap_action

            if soap_version := outgoing_row.get('soap_version'):
                exported_conn['soap_version'] = soap_version

            if data_format := outgoing_row.get('data_format'):
                exported_conn['data_format'] = data_format

            if (timeout := outgoing_row.get('timeout')) is not None and timeout != 60:
                exported_conn['timeout'] = timeout

            if (ping_method := outgoing_row.get('ping_method')) and ping_method != 'GET':
                exported_conn['ping_method'] = ping_method

            if outgoing_row.get('content_type'):
                exported_conn['content_type'] = outgoing_row['content_type']

            # Unpack the opaque attributes carrying the remaining SOAP fields.
            opaque = {}
            if opaque1 := outgoing_row.get('opaque1'):
                opaque = loads(opaque1) or {}

            # The runtime key is validate_tls while the YAML one is tls_verify
            if opaque.get('validate_tls') is False:
                exported_conn['tls_verify'] = False

            if opaque.get('use_ws_addressing'):
                exported_conn['use_ws_addressing'] = True

            if opaque.get('use_mtom'):
                exported_conn['use_mtom'] = True

            if tls_client_cert := opaque.get('tls_client_cert'):
                exported_conn['tls_client_cert'] = tls_client_cert

            if tls_client_key := opaque.get('tls_client_key'):
                exported_conn['tls_client_key'] = tls_client_key

            # Body-credential mappings are kept in the database as a JSON string
            # and exported as a list of name/position rows.
            if body_credentials := opaque.get('body_credentials'):
                if isinstance(body_credentials, str):
                    body_credentials = loads(body_credentials)
                if body_credentials:
                    exported_conn['body_credentials'] = body_credentials

            # The declarative invocation and health check fields are exported the same way,
            # with row-based fields as YAML lists and without the environment-local job IDs.
            export_invocation_fields(exported_conn, opaque, Invocation_Fields_SOAP)

            exported_outgoing.append(exported_conn)

        logger.info('Successfully prepared %d outgoing SOAP connection definitions for export', len(exported_outgoing))
        return exported_outgoing

# ################################################################################################################################
# ################################################################################################################################
