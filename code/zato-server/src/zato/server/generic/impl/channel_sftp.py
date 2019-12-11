# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Bunch
from bunch import bunchify

# sh
from sh import Command

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
        self.logger = logger # type: logging.Logger
        self.model = model   # type: SFTPChannelModel
        self.command = self.get_command()

# ################################################################################################################################

    def get_command(self):
        """ Returns a reusable sh.Command object that can will start an SFTP server.
        """
        # A list of arguments that will be added to the base command
        args = []

        # Disable local port forwarding
        args.append('-j')

        # Disable remote port forwarding
        args.append('-k')

        # Disable password logins for root
        args.append('-g')

        # Disable root logins
        args.append('-w')

        # Log to stdout
        args.append('-E')

        # Do not fork into background
        args.append('-F')

        # Idle timeout
        args.append('-I {}'.format(self.model.idle_timeout))

        # Keep-alive timeout
        args.append('-K {}'.format(self.model.keep_alive_timeout))

        # Bind address
        args.append('-p {}'.format(self.model.address))

        # PID file
        #args.append('-p {}'.format(self.model.pid))

        # Generate a host key if one is not given on input (-R)
        # or use the one provided in configuration (-r).
        args.append('-R')

        '''
        -I 300 \
        -K 10 \
        -p 0.0.0.0:33022 \
        -P ./dropbear.pid
        -r ./ssh_host_ed25519_key
        '''

        # Base command to build additional arguments into
        command = Command(self.model.sftp_command)
        command = command.bake(*args)

        return command

# ################################################################################################################################

    def serve_forever(self):
        logger.warn('CCC %s', self.command)

        self.command()

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
        config.idle_timeout = int(config.idle_timeout)
        config.keep_alive_timeout = int(config.keep_alive_timeout)

        # Return a Python-level configuration object
        return SFTPChannelModel.from_dict(config)

# ################################################################################################################################
# ################################################################################################################################

def main():
    config = bunchify({
        'id': 1,
        'name': 'My FTP channel',
        'address': '0.0.0.0:21021',
        'service_name': 'helpers.raw-request-logger',
        'topic_name': None,
        'idle_timeout': '300',
        'keep_alive_timeout': '20',
        'sftp_command': 'dropbear',
        'host_key': '',
    })

    channel = SFTPChannel(config)
    channel.start()

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
