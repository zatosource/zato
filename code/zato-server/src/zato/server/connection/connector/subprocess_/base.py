# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import signal
import sys
from functools import wraps
from http.client import BAD_REQUEST, FORBIDDEN, INTERNAL_SERVER_ERROR, NOT_ACCEPTABLE, OK, responses, SERVICE_UNAVAILABLE
from logging import Formatter, getLogger, StreamHandler
from logging.handlers import RotatingFileHandler
from os import getppid, path
from threading import RLock
from traceback import format_exc
from wsgiref.simple_server import make_server as wsgiref_make_server

# Bunch
from bunch import bunchify

# Requests
from requests import post as requests_post

# YAML
import yaml

# Python 2/3 compatibility
from builtins import bytes

# Zato
from zato.common.api import MISC
from zato.common.broker_message import code_to_name
from zato.common.json_internal import dumps, loads
from zato.common.util.api import parse_cmd_line_options
from zato.common.util.auth import parse_basic_auth
from zato.common.util.open_ import open_r, open_w
from zato.common.util.posix_ipc_ import ConnectorConfigIPC

# ################################################################################################################################

if 0:
    from bunch import Bunch
    from logging import Logger

    Bunch = Bunch
    Logger = Logger

# ################################################################################################################################

def get_logging_config(conn_type, file_name):
    return {
        'loggers': {
            'zato_{}'.format(conn_type): {
                'qualname':'zato_{}'.format(conn_type),
                'level':'INFO',
                'propagate':False,
                'handlers':[conn_type]
            }
        },
        'handlers': {
            conn_type: {
                'formatter':'default',
                'backupCount':10,
                'mode':'a',
                'maxBytes':20000000,
                'filename':
                './logs/{}.log'.format(file_name)
            },
        },
        'formatters': {
            'default': {
                'format': '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
            }
        }
    }

# ################################################################################################################################

_http_200 = '{} {}'.format(OK, responses[OK])
_http_400 = '{} {}'.format(BAD_REQUEST, responses[BAD_REQUEST])
_http_403 = '{} {}'.format(FORBIDDEN, responses[FORBIDDEN])
_http_406 = '{} {}'.format(NOT_ACCEPTABLE, responses[NOT_ACCEPTABLE])
_http_500 = '{} {}'.format(INTERNAL_SERVER_ERROR, responses[INTERNAL_SERVER_ERROR])
_http_503 = '{} {}'.format(SERVICE_UNAVAILABLE, responses[SERVICE_UNAVAILABLE])

_path_api = '/api'
_path_ping = '/ping'
_paths = (_path_api, _path_ping)

# ################################################################################################################################
# ################################################################################################################################

def ensure_id_exists(container_name):
    def ensure_id_exists_impl(func):
        @wraps(func)
        def inner(self, msg, _not_given=object()):
            # type: (BaseConnectionContainer, Bunch)

            # Make sure we have a config container of that name
            container = getattr(self, container_name, _not_given) # type: dict

            if container is _not_given:
                raise Exception('No such attribute `{}` in `{}`'.format(container_name, self))

            if not msg.id in container:
                raise Exception('No such ID `{}` among `{}` ({})'.format(
                    msg.id, sorted(container.items()), container_name))

            return func(self, msg)
        return inner
    return ensure_id_exists_impl

# ################################################################################################################################

def ensure_prereqs_ready(func):
    @wraps(func)
    def inner(self, *args, **kwargs):
        # type: (BaseConnectionContainer)
        if self.has_prereqs:
            if not self.check_prereqs_ready():
                raise Exception(self.get_prereqs_not_ready_message())
        return func(self, *args, **kwargs)
    return inner

# ################################################################################################################################
# ################################################################################################################################

class Response:
    def __init__(self, status=_http_200, data=b'', content_type='text/json'):
        self.status = status
        self.data = data
        self.content_type = content_type

# ################################################################################################################################
# ################################################################################################################################

class BaseConnectionContainer:

    # Subclasses may indicate that they have their specific prerequisites
    # that need to be fulfilled before connections can be used,
    # e.g. IBM MQ requires installation of PyMQI.
    has_prereqs = False

    # Set by our subclasses that actually create connections
    connection_class = None

    # Logging configuration that will be set by subclasses
    ipc_name = 'invalid-notset-ipc-name'
    conn_type = 'invalid-notset-conn-type'
    logging_file_name = 'invalid-notset-logging-file-name'

    remove_id_from_def_msg = True
    remove_name_from_def_msg = True

    def __init__(self):

        if len(sys.argv) > 1:
            self.options = sys.argv[1]
            self.options = parse_cmd_line_options(self.options) # type: dict
            self.options['zato_subprocess_mode'] = True
        else:
            self.options = {
                'zato_subprocess_mode': False,
                'deployment_key': 'test',
                'shmem_size': 100_000,
            }

        # Subclasses may want to update the options here
        self.enrich_options()

        self.deployment_key = self.options['deployment_key']
        self.shmem_size = int(self.options['shmem_size'])

        self.host = '127.0.0.1'
        self.port = None
        self.username = None
        self.password = None
        self.server_auth = None
        self.basic_auth_expected = None
        self.server_port = None
        self.server_path = None
        self.server_address = 'http://127.0.0.1:{}{}'
        self.lock = RLock()
        self.logger = None # type: Logger
        self.parent_pid = getppid()

        self.config_ipc = ConnectorConfigIPC()

        if self.options['zato_subprocess_mode']:
            self.config_ipc.create(self.deployment_key, self.shmem_size, False)

        self.connections = {}
        self.outconns = {}
        self.channels = {}

        self.outconn_id_to_def_id = {} # Maps outgoing connection IDs to their underlying definition IDs
        self.channel_id_to_def_id = {} # Ditto but for channels
        self.outconn_name_to_id = {}   # Maps outgoing connection names to their IDs

        self.set_config()
        self.post_init()

# ################################################################################################################################

    def enrich_options(self):
        # type: (None) -> None
        pass

# ################################################################################################################################

    def post_init(self):
        """ Can be implemented by subclasses to further customise the container.
        """

# ################################################################################################################################

    def set_config(self):
        """ Sets self attributes, as configured in shmem by our parent process.
        """
        if self.options['zato_subprocess_mode']:
            config = self.config_ipc.get_config('zato-{}'.format(self.ipc_name))
            config = loads(config)
        else:
            config = {
                'username': 'zato.username',
                'password': 'zato.password',
                'port': 35035,
                'server_port': 35036,
                'server_path': '/zato/base-connection-container',
                'base_dir': os.path.expanduser('~/env/qs-1'),
                'needs_pidfile': False,
            }

        config = bunchify(config)

        self.username = config.username
        self.password = config.password
        self.server_auth = (self.username, self.password)

        self.base_dir = config.base_dir
        self.port = config.port
        self.server_port = config.server_port
        self.server_path = config.server_path
        self.server_address = self.server_address.format(self.server_port, self.server_path)

        if self.options['zato_subprocess_mode']:
            with open_r(config.logging_conf_path) as f:
                logging_config = yaml.load(f, yaml.FullLoader)

            if not 'zato_{}'.format(self.conn_type) in logging_config['loggers']:
                logging_config = get_logging_config(self.conn_type, self.logging_file_name)

            # Configure logging for this connector
            self.set_up_logging(logging_config)

        else:
            log_format = '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
            logging.basicConfig(level=logging.DEBUG, format=log_format)
            self.logger = getLogger('zato')
            self.logger.warning('QQQ %s', self)

        # Store our process's pidfile
        if config.needs_pidfile:
            self.store_pidfile(config.pidfile_suffix)

# ################################################################################################################################

    def check_prereqs_ready(self):
        return True

# ################################################################################################################################

    def get_prereqs_not_ready_message(self):
        return '<default-not-set-prereqs-not-ready-message>'

# ################################################################################################################################

    def set_up_logging(self, config):

        logger_conf = config['loggers']['zato_{}'.format(self.conn_type)]
        handler_conf = config['handlers'][self.conn_type]
        del handler_conf['formatter']
        handler_conf.pop('class', False)
        formatter_conf = config['formatters']['default']['format']

        self.logger = getLogger(logger_conf['qualname'])
        self.logger.setLevel(getattr(logging, logger_conf['level']))

        formatter = Formatter(formatter_conf)

        handler_conf['filename'] = path.abspath(path.join(self.base_dir, handler_conf['filename']))
        handler = RotatingFileHandler(**handler_conf)
        handler.setFormatter(formatter)

        stdout_handler = StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)

        self.logger.addHandler(handler)
        self.logger.addHandler(stdout_handler)

# ################################################################################################################################

    def store_pidfile(self, suffix):
        pidfile = os.path.join(self.base_dir, '{}-{}'.format(MISC.PIDFILE, suffix))
        with open_w(pidfile) as f:
            f.write(str(os.getpid()))

# ################################################################################################################################

    def _post(self, msg, _post=requests_post):
        self.logger.info('POST to `%s` (%s), msg:`%s`', self.server_address, self.username, msg)

        for k, v in msg.items():
            if isinstance(v, bytes):
                msg[k] = v.decode('utf8')

        try:
            _post(self.server_address, data=dumps(msg), auth=self.server_auth)
        except Exception as e:
            self.logger.warning('Exception in BaseConnectionContainer._post: `%s`', e.args[0])

# ################################################################################################################################

    def on_mq_message_received(self, msg_ctx):
        return self._post({
            'msg': msg_ctx.mq_msg.to_dict(),
            'channel_id': msg_ctx.channel_id,
            'queue_name': msg_ctx.queue_name,
            'service_name': msg_ctx.service_name,
            'data_format': msg_ctx.data_format,
        })

# ################################################################################################################################

    def _create_definition(self, msg, needs_connect=True):
        """ A low-level method to create connection definitions. Must be called with self.lock held.
        """
        msg.pop('cluster_id', None)
        msg['needs_jms'] = msg.pop('use_jms', False)
        msg.pop('_encryption_needed', False)
        msg.pop('_encrypted_in_odb', False)

        id = msg.pop('id') if self.remove_id_from_def_msg else msg['id']

        if self.remove_name_from_def_msg:
            msg.pop('name')
            msg.pop('old_name', None)

        # We always create and add a connetion ..
        conn = self.connection_class(self.logger, **msg)
        self.connections[id] = conn

        # .. because even if it fails here, it will be eventually established during one of .send or .receive,
        # however, it is possible that our caller already knows that the connection will fail so we need
        # to take it into account too.
        if needs_connect:
            conn.connect()

        return conn

# ################################################################################################################################

    def _create_outconn(self, msg):
        """ A low-level method to create an outgoing connection. Must be called with self.lock held.
        """
        # Not all outgoing connections have their parent definitions
        def_id = msg.get('def_id')

        if def_id:

            # Just to be on the safe side, make sure that our connection exists
            if not msg.def_id in self.connections:
                return Response(_http_503, 'Could not find def_id among {}'.format(self.connections.keys()), 'text/plain')

            # Map outconn to its definition
            self.outconn_id_to_def_id[msg.id] = msg.def_id

        # Create the outconn now
        self.outconns[msg.id] = msg

        # Maps outconn name to its ID
        self.outconn_name_to_id[msg.name] = msg.id

        self.logger.info('Added connection `%s`, self.outconns -> `%s`', msg.name, self.outconns)

        # Everything OK
        return Response()

# ################################################################################################################################

    @ensure_id_exists('outconns')
    @ensure_prereqs_ready
    def _delete_outconn(self, msg, outconn_name=None):
        """ A low-level implementation of outconn deletion. Must be called with self.lock held.
        """
        outconn_name = outconn_name if outconn_name else self.outconns[msg.id].name
        del self.outconns[msg.id]
        del self.outconn_id_to_def_id[msg.id]
        del self.outconn_name_to_id[outconn_name]

# ################################################################################################################################

    def _on_send_exception(self):
        msg = 'Exception in _on_OUTGOING_SEND (2) `{}`'.format(format_exc())
        self.logger.warning(msg)
        return Response(_http_503, msg)

# ################################################################################################################################

    def handle_http_request(self, path, msg, ok=b'OK'):
        """ Dispatches incoming HTTP requests - either reconfigures the connector or puts messages to queues.
        """
        self.logger.info('MSG received %s %s', path, msg)

        if path == _path_ping:
            return Response()
        else:
            msg = msg.decode('utf8')
            msg = loads(msg)
            msg = bunchify(msg)

            # Delete what handlers don't need
            msg.pop('msg_type', None) # Optional if message was sent by a server that is starting up vs. API call
            action = msg.pop('action')

            handler = getattr(self, '_on_{}'.format(code_to_name[action]))
            return handler(msg)

# ################################################################################################################################

    def check_credentials(self, auth):
        """ Checks incoming username/password and returns True only if they were valid and as expected.
        """
        username, password = parse_basic_auth(auth)

        if username != self.username:
            self.logger.warning('Invalid username or password')
            return

        elif password != self.password:
            self.logger.warning('Invalid username or password')
            return
        else:
            # All good, we let the request in
            return True

# ################################################################################################################################

    def on_wsgi_request(self, environ, start_response):

        # Default values to use in case of any internal errors
        status = _http_406
        content_type = 'text/plain'

        try:
            content_length = environ.get('CONTENT_LENGTH')
            if not content_length:
                status = _http_400
                data = 'Missing content'
                content_type = 'text/plain'
            else:
                data = environ['wsgi.input'].read(int(content_length))
                if self.check_credentials(environ.get('HTTP_AUTHORIZATION')):
                    response = self.handle_http_request(environ['PATH_INFO'], data)
                    status = response.status
                    data = response.data
                    content_type = response.content_type
                else:
                    status = _http_403
                    data = 'You are not allowed to access this resource'
                    content_type = 'text/plain'

        except Exception:
            self.logger.warning(format_exc())
            content_type = 'text/plain'
            status = _http_400
            data = format_exc()
        finally:

            try:
                headers = [('Content-type', content_type)]

                if not isinstance(data, bytes):
                    data = data.encode('utf8')

                start_response(status, headers)
                return [data]

            except Exception:
                exc_formatted = format_exc()
                self.logger.warning('Exception in finally block `%s`', exc_formatted)

# ################################################################################################################################

    @ensure_id_exists('channels')
    @ensure_prereqs_ready
    def on_channel_delete(self, msg):
        """ Stops and deletes an existing channel.
        """
        with self.lock:
            channel = self.channels[msg.id]
            channel.keep_running = False

            del self.channels[channel.id]
            del self.channel_id_to_def_id[channel.id]

# ################################################################################################################################

    @ensure_prereqs_ready
    def on_channel_create(self, msg):
        """ Creates a new channel listening for messages from a given endpoint.
        """
        with self.lock:
            conn = self.connections[msg.def_id]
            channel = self._create_channel_impl(conn, msg)
            channel.start()
            self.channels[channel.id] = channel
            self.channel_id_to_def_id[channel.id] = msg.def_id
            return Response()

# ################################################################################################################################

    @ensure_prereqs_ready
    def on_outgoing_edit(self, msg):
        """ Updates and existing outconn by deleting and creating it again with latest configuration.
        """
        with self.lock:
            self._delete_outconn(msg, msg.old_name)
            return self._create_outconn(msg)

# ################################################################################################################################

    @ensure_prereqs_ready
    def on_outgoing_create(self, msg):
        """ Creates a new outgoing connection using an already existing definition.
        """
        with self.lock:
            return self._create_outconn(msg)

# ################################################################################################################################

    @ensure_prereqs_ready
    def on_outgoing_delete(self, msg):
        """ Deletes an existing outgoing connection.
        """
        with self.lock:
            self._delete_outconn(msg)
            return Response()

# ################################################################################################################################

    @ensure_prereqs_ready
    @ensure_id_exists('connections')
    def on_definition_ping(self, msg):
        """ Pings a remote endpoint.
        """
        try:
            self.connections[msg.id].ping()
        except Exception as e:
            return Response(_http_503, str(e.args[0]), 'text/plain')
        else:
            return Response()

# ################################################################################################################################

    @ensure_id_exists('connections')
    @ensure_prereqs_ready
    def on_definition_change_password(self, msg):
        """ Changes the password of an existing definition and reconnects to the remote end.
        """
        with self.lock:
            try:
                conn = self.connections[msg.id]
                conn.close()
                conn.password = str(msg.password)
                conn.connect()
            except Exception as e:
                self.logger.warning(format_exc())
                return Response(_http_503, str(e.args[0]), 'text/plain')
            else:
                return Response()

# ################################################################################################################################

    @ensure_id_exists('connections')
    @ensure_prereqs_ready
    def on_definition_delete(self, msg):
        """ Deletes a definition along with its associated outconns and channels.
        """
        with self.lock:
            def_id = msg.id
            delete_id = None
            delete_name = None

            # Stop all connections ..
            try:
                conn = self.connections[def_id]
                delete_id = conn.id
                delete_name = conn.name
                self.connections[def_id].close()
            except Exception:
                self.logger.warning(format_exc())
            finally:
                try:
                    del self.connections[def_id]
                except Exception:
                    self.logger.warning(format_exc())

                # .. continue to delete outconns regardless of errors above ..
                for outconn_id, outconn_def_id in self.outconn_id_to_def_id.items():
                    if outconn_def_id == def_id:
                        del self.outconn_id_to_def_id[outconn_id]
                        del self.outconns[outconn_id]

                # .. delete channels too.
                for channel_id, channel_def_id in self.channel_id_to_def_id.items():
                    if channel_def_id == def_id:
                        del self.channel_id_to_def_id[channel_id]
                        del self.channels[channel_id]

            if delete_id:
                self.logger.info('Deleted `%s` (%s)', delete_name, delete_id)

            return Response()

# ################################################################################################################################

    @ensure_id_exists('connections')
    @ensure_prereqs_ready
    def on_definition_edit(self, msg):
        """ Updates an existing definition - close the current one, including channels and outconns,
        and creates a new one in its place.
        """
        with self.lock:
            def_id = msg.id
            old_conn = self.connections[def_id]

            # Edit messages don't carry passwords
            msg.password = old_conn.password

            # It's possible that we are editing a connection that has no connected yet,
            # e.g. if password was invalid, so this needs to be guarded by an if.
            if old_conn.is_connected:
                self.connections[def_id].close()

            # Overwrites the previous connection object
            new_conn = self._create_definition(msg, old_conn.is_connected)

            # Stop and start all channels using this definition.
            for channel_id, _def_id in self.channel_id_to_def_id.items():
                if def_id == _def_id:
                    channel = self.channels[channel_id]
                    channel.stop()
                    channel.conn = new_conn
                    channel.start()

            return Response()

# ################################################################################################################################

    @ensure_prereqs_ready
    def on_definition_create(self, msg):
        """ Creates a new definition from the input message.
        """
        with self.lock:
            try:
                self._create_definition(msg)
            except Exception as e:
                self.logger.warning(format_exc())
                return Response(_http_503, str(e.args[0]))
            else:
                return Response()

# ################################################################################################################################

    def _create_channel_impl(self, *args, **kwargs):
        raise NotImplementedError('Should be overridden in subclasses')

# ################################################################################################################################

    def make_server(self):
        return wsgiref_make_server(self.host, self.port, self.on_wsgi_request)

# ################################################################################################################################

    def run(self):
        server = self.make_server()
        try:
            server.serve_forever()
        except KeyboardInterrupt:

            try:
                # Attempt to clean up, if possible
                server.shutdown()
                for conn in self.connections.values():
                    conn.close()
            except Exception:
                # Log exception if cleanup was not possible
                self.logger.warning('Exception in shutdown procedure `%s`', format_exc())
            finally:
                # Anything happens, we need to shut down the process
                os.kill(os.getpid(), signal.SIGTERM)

# ################################################################################################################################
# ################################################################################################################################
