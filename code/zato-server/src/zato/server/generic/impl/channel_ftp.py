# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import socket
import time

# Bunch
from bunch import bunchify

# gevent
from gevent.server import StreamServer

# Zato
from zato.common.model import FTPChannel as FTPChannelModel
from zato.common.util import spawn_greenlet

# ################################################################################################################################

log_format = '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)

logger = logging.getLogger('zato')

# ################################################################################################################################

class default:
    max_command_len = 1024

# ################################################################################################################################
# ################################################################################################################################

class _CommandServer(StreamServer):

    def __init__(self, logger, *args, **kwargs):
        self.logger = logger # type: logging.Logger
        super(_CommandServer, self).__init__(*args, **kwargs)

# ################################################################################################################################

    def handle(self, sock, address):
        """ Much of the code below is taken from gevent.pywsgi.WSGIHandler.
        """
        self.logger.info('RRR %s', self.socket)
        self.logger.info('WWW %s', sock, address)

        try:
            while self.socket is not None:

                self.time_start = time.time()
                self.time_finish = 0

                result = self.handle_command()

                if result is None:
                    break

                if result is True:
                    continue

                self.status, response_body = result
                self.socket.sendall(response_body)

                if self.time_finish == 0:
                    self.time_finish = time.time()

                self.log_request()
                break
        finally:
            if self.socket is not None:
                _sock = getattr(self.socket, '_sock', None) # Python 3
                try:
                    # read out request data to prevent error: [Errno 104] Connection reset by peer
                    if _sock:
                        try:
                            # socket.recv would hang
                            _sock.recv(16384)
                        finally:
                            _sock.close()
                    self.socket.close()
                except socket.error:
                    pass
            self.__dict__.pop('socket', None)
            self.__dict__.pop('rfile', None)

# ################################################################################################################################

    def handle_command(self):
        zzz

# ################################################################################################################################
# ################################################################################################################################

class FTPServer(object):
    def __init__(self, logger, model):
        self.logger = logger       # type: logging.Logger
        self.model = model         # type: FTPChannelModel
        self.command_server = None # type: StreamServer
        self.clients = set()

    def serve_forever(self):
        self.command_server = _CommandServer(self.logger, self.model.address)
        self.command_server.serve_forever()

# ################################################################################################################################
# ################################################################################################################################

class FTPChannel(object):
    """ Represents a particular FTP channel along with its configuration, users and connected clients.
    """
    def __init__(self, config):
        # type: (dict)
        self.config = config
        self.logger = logging.getLogger()
        self.model = self._get_model_from_config(self.config)
        self.server = FTPServer(logger, self.model)

# ################################################################################################################################

    def start(self):
        self.logger.warn('QQQ %s', self.model.to_dict())
        self.server.serve_forever()

# ################################################################################################################################

    def _get_model_from_config(self, config):
        # type: (dict) -> FTPChannel

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
        return FTPChannelModel.from_dict(config)

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

    channel = FTPChannel(config)
    channel.start()

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################


'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import socket
from logging import getLogger

# Bunch
from bunch import bunchify

# pyftpdlib
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler, ThrottledDTPHandler
from pyftpdlib.servers import FTPChannel

# Zato
from zato.common.model import FTPChannel
from zato.common.util import spawn_greenlet

# ################################################################################################################################

if 0:
    # Type checking
    from logging import Logger

    # For pyflakes
    Logger = Logger

# ################################################################################################################################

log_format = '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)

logger = getLogger('zato')
logger_pyftpdlib = getLogger('pyftpdlib')

# ################################################################################################################################

_megabyte = 1048576 # 2 ** 20 bytes

# ################################################################################################################################
# ################################################################################################################################

class _FTPServer(FTPChannel):
    """ A subclass of FTPChannel needed to add functionality to base methods.
    """
    def __init__(self, *args, **kwargs):
        self.zato_keep_running = True
        super(_FTPServer, self).__init__(*args, **kwargs)

    def bind_af_unspecified(self, addr):
        """ The same as in the parent class except for the usage of SO_REUSEPORT below.
        """
        assert self.socket is None
        host, port = addr
        if host == "":
            # When using bind() "" is a symbolic name meaning all
            # available interfaces. People might not know we're
            # using getaddrinfo() internally, which uses None
            # instead of "", so we'll make the conversion for them.
            host = None
        err = "getaddrinfo() returned an empty list"
        info = socket.getaddrinfo(host, port, socket.AF_UNSPEC,
                                  socket.SOCK_STREAM, 0, socket.AI_PASSIVE)
        for res in info:
            self.socket = None
            self.del_channel()
            af, socktype, proto, canonname, sa = res
            try:
                self.create_socket(af, socktype)
                self.set_reuse_addr()

                # This line was added for Zato
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

                self.bind(sa)
            except socket.error as _:
                err = _
                if self.socket is not None:
                    self.socket.close()
                    self.del_channel()
                    self.socket = None
                continue
            break
        if self.socket is None:
            self.del_channel()
            raise socket.error(err)
        return af

# ################################################################################################################################

    def serve_forever(self, timeout=None, blocking=True, handle_exit=True):
        if handle_exit:
            log = handle_exit and blocking
            if log:
                self._log_start()

            try:
                self.ioloop.loop(timeout, blocking)
            except (KeyboardInterrupt, SystemExit):
                logger_pyftpdlib.info("received interrupt signal")

            if blocking:
                if log:
                    logger_pyftpdlib.info(
                        ">>> shutting down FTP server (%s active socket "
                        "fds) <<<",
                        self._map_len())
                self.close_all()
        else:
            self.ioloop.loop(timeout, blocking)

# ################################################################################################################################
# ################################################################################################################################

class ChannelFTP(object):
    def __init__(self, logger, **config):
        # type: (Logger, dict)
        self.logger = logger
        self.model = self._get_model_from_config(config)
        self.server = None # type: FTPChannel

# ################################################################################################################################



# ################################################################################################################################

    def connect(self):
        self.serve_forever()

# ################################################################################################################################

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

        self.server = _FTPServer((self.model.host, self.model.port), handler)
        self.server.max_cons = self.model.max_connections
        self.server.max_cons_per_ip = self.model.max_conn_per_ip
        self.server.zato_keep_running = False

        self.server.serve_forever()

# ################################################################################################################################
# ################################################################################################################################
'''
