# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.model import HTTPSOAP
from zato.common.odb.query import http_soap_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ChannelExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export_channel_definitions(self, session:'SASession') -> 'list':
        """ Export REST channel definitions from the database.
        """
        logger.info('Exporting REST channel definitions from cluster_id=%s', self.exporter.cluster_id)
        
        # Get REST channels from the database
        channels = http_soap_list(session, self.exporter.cluster_id, 'channel', 'plain_http')
        
        channel_defs = []
        
        for channel in channels:
            logger.info('Processing REST channel: %s', channel.name)
            
            # Create a dictionary representation of the channel
            channel_def = {
                'name': channel.name,
                'url_path': channel.url_path,
                'service': channel.service_name,
                'is_active': channel.is_active
            }
            
            # Add security if present
            if channel.security_id:
                for sec_name, sec_def in self.exporter.sec_defs.items():
                    if sec_def.get('id') == channel.security_id:
                        channel_def['security'] = sec_name
                        break
            
            # Add data format if not default
            if channel.data_format != 'json':
                channel_def['data_format'] = channel.data_format
            
            # Add method if not default
            if channel.method != 'POST':
                channel_def['method'] = channel.method
            
            # Add transport if not default
            if channel.transport != 'plain_http':
                channel_def['transport'] = channel.transport
            
            # Add to results
            channel_defs.append(channel_def)
            
        logger.info('Exported %d REST channels', len(channel_defs))
        return channel_defs

# ################################################################################################################################
# ################################################################################################################################
