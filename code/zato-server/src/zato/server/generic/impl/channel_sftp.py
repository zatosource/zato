# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Bunch
from bunch import bunchify

# Zato
from zato.common.model import SFTPChannel as SFTPChannelModel
from zato.common.util import spawn_greenlet

# ################################################################################################################################

log_format = '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)

logger = logging.getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class SFTPServer(object):
    def __init__(self, logger, model):
        self.logger = logger       # type: logging.Logger
        self.model = model         # type: SFTPChannelModel

    def serve_forever(self):
        logger.warn('CCC %s', self.model.to_dict())

# ################################################################################################################################
# ################################################################################################################################

class SFTPChannel(object):
    """ Represents a particular FTP channel along with its configuration, users and connected clients.
    """
    def __init__(self, config):
        # type: (dict)
        self.config = config
        self.logger = logging.getLogger()
        self.model = self._get_model_from_config(self.config)
        self.server = SFTPServer(logger, self.model)

# ################################################################################################################################

    def start(self):
        self.logger.warn('QQQ %s', self.model.to_dict())
        self.server.serve_forever()

# ################################################################################################################################

    def _get_model_from_config(self, config):
        # type: (dict) -> SFTPChannel

        # For dotted-attribute access
        config = bunchify(config)

        # Use expected data types in configuration
        config.max_conn_per_ip = int(config.max_conn_per_ip)
        config.max_connections = int(config.max_connections)

        # Make sure at least an empty log prefix exists and prefix each log entry with current channel's name
        if not config.log_prefix:
            config.log_prefix = ''
        config.log_prefix = '[{}] {}'.format(config.name, config.log_prefix).strip()

        # Break address into components
        host, port = config.address.split(':')
        host = host.strip()
        port = int(port.strip())
        config.host = host
        config.port = port

        # Break passive ports into components
        if config.passive_ports:
            start, stop = config.passive_ports.split('-')
            start = int(start.strip())
            stop = int(stop.strip())
            config.passive_ports = [start, stop]

        # Return a Python-level configuration object
        return SFTPChannelModel.from_dict(config)

# ################################################################################################################################
# ################################################################################################################################

def main():
    config = bunchify({
        'id': 1,
        'name': 'My FTP channel',
        'address': '0.0.0.0:21021',
        'banner': 'Welcome to Zato',
        'base_directory': './work/ftp',
        'command_timeout': 300,
        'log_level': 'INFO',
        'log_prefix': '%(remote_ip)s:%(remote_port)s-[%(username)s]',
        'max_conn_per_ip': '20',
        'max_connections': '200',
        'passive_ports': '50100-50200',
        'service_name': 'helpers.raw-request-logger',
        'topic_name': None,
    })

    channel = SFTPChannel(config)
    channel.start()

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
