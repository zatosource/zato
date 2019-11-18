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

# Zato
from zato.common.model import FTPChannel

# ################################################################################################################################

log_format = '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class ChannelFTPImpl(object):
    def __init__(self, model):
        # type: (FTPChannel)
        self._model = model

    def serve_forever(self):
        pass

# ################################################################################################################################
# ################################################################################################################################

def main():

    config = bunchify({
        'id': 1,
        'address': '0.0.0.0:21021',
        'banner': 'Welcome',
        'base_directory': './work/ftp',
        'command_timeout': 300,
        'log_level': 'INFO',
        'log_prefix': '%(remote_ip)s:%(remote_port)s-[%(username)s]',
        'masq_address': None,
        'max_conn_per_ip': '20',
        'max_connections': '200',
        'passive_ports': None,
        'read_throttle': '10',
        'write_throttle': '10',
        'service_name': 'helpers.raw-request-logger',
        'topic_name': None,
    })

    # Use expected data types in configuration
    config.max_conn_per_ip = int(config.max_conn_per_ip)
    config.max_connections = int(config.max_connections)
    config.read_throttle = int(config.read_throttle)
    config.write_throttle = int(config.write_throttle)

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
