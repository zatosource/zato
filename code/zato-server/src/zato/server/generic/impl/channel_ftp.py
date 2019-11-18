# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from logging import getLogger

# Bunch
from bunch import bunchify

# pyftpdlib
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler, ThrottledDTPHandler
from pyftpdlib.servers import FTPServer

# Zato
from zato.common.model import FTPChannel

# ################################################################################################################################

log_format = '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)

logger = getLogger('zato')

# ################################################################################################################################

_megabyte = 1048576 # 2 ** 20 bytes

# ################################################################################################################################
# ################################################################################################################################

class ChannelFTPImpl(object):
    def __init__(self, model):
        # type: (FTPChannel)
        self.model = model

    def serve_forever(self):
        logger.info('Starting FTP channel `%s` (%s)', self.model.name, self.model.to_dict())

        authorizer = DummyAuthorizer()
        authorizer.add_user('abc', 'def', '/tmp', 'elradfmwMT')

        # We need these subclasses to set Python class-wide parameters on a per-channel basis
        class _FTPHandler(FTPHandler):
            pass

        class _ThrottledDTPHandler(ThrottledDTPHandler):
            pass

        dtp_handler = _ThrottledDTPHandler
        dtp_handler.read_limit = self.model.read_throttle
        dtp_handler.write_limit = self.model.write_throttle

        handler = _FTPHandler
        handler.dtp_handler = dtp_handler
        handler.authorizer = authorizer
        handler.banner = self.model.banner
        handler.timeout = self.model.command_timeout
        handler.log_prefix = self.model.log_prefix
        handler.masquerade_address = self.model.masq_address
        handler.passive_ports = self.model.passive_ports

        server = FTPServer((self.model.host, self.model.port), handler)
        server.max_cons = self.model.max_connections
        server.max_cons_per_ip = self.model.max_conn_per_ip

        server.serve_forever()

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
        'masq_address': None,
        'max_conn_per_ip': '20',
        'max_connections': '200',
        'passive_ports': '50100-50200',
        'read_throttle': '0.25',
        'write_throttle': '10',
        'service_name': 'helpers.raw-request-logger',
        'topic_name': None,
    })

    # Use expected data types in configuration
    config.max_conn_per_ip = int(config.max_conn_per_ip)
    config.max_connections = int(config.max_connections)
    config.read_throttle = float(config.read_throttle)
    config.write_throttle = float(config.write_throttle)

    # Make sure at least an empty log prefix exists and prefix each log entry with current channel's name
    if not config.log_prefix:
        config.log_prefix = ''
    config.log_prefix = '[{}] {}'.format(config.name, config.log_prefix).strip()

    # Turn megabytes into bytes
    config.read_throttle = int(config.read_throttle * _megabyte)
    config.write_throttle = int(config.write_throttle * _megabyte)

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

    # Python-level configuration object
    model = FTPChannel.from_dict(config)

    # Create a low-level channel object ..
    impl = ChannelFTPImpl(model)

    # .. and start it.
    impl.serve_forever()

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
