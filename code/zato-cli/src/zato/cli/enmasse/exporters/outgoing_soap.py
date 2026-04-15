# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, list_
    outgoing_soap_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class OutgoingSOAPExporter:

    def __init__(self, exporter) -> 'None':
        self.exporter = exporter

    def export(self, items) -> 'outgoing_soap_def_list':
        """ Exports outgoing SOAP connection definitions.
        """
        logger.info('Exporting outgoing SOAP connection definitions')

        if not items:
            logger.info('No outgoing SOAP connection definitions found')
            return []

        exported_outgoing = []
        logger.info('Processing %d outgoing SOAP connection definitions', len(items))

        for outgoing_row in items:

            # Skip internal connections
            if outgoing_row.get('is_internal'):
                continue

            exported_conn = {
                'name': outgoing_row['name'],
                'host': outgoing_row.get('host', ''),
                'url_path': outgoing_row.get('url_path', ''),
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

            if outgoing_row.get('tls_verify') is False:
                exported_conn['tls_verify'] = False

            for field in ['content_type', 'content_encoding']:
                if outgoing_row.get(field):
                    exported_conn[field] = outgoing_row[field]

            exported_outgoing.append(exported_conn)

        logger.info('Successfully prepared %d outgoing SOAP connection definitions for export', len(exported_outgoing))
        return exported_outgoing

# ################################################################################################################################
# ################################################################################################################################
