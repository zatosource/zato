# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import spawn

# requests
from requests import get as requests_get

# Zato
from zato.client import AnyServiceInvoker
from zato.common import SERVER_UP_STATUS
from zato.common.util import make_repr
from zato.common.odb.query import server_by_name, server_list
from zato.server.service import Service

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

sec_def_name = 'zato.internal.invoke'
api_user = sec_def_name + '.user'

# ################################################################################################################################

class _Server(object):

    def __init__(self, service):
        self.parallel_server = service.server

    def __repr__(self):
        return make_repr(self)

    def invoke(self, service, request=None, *args, **kwargs):
        raise NotImplementedError('Should be implemented in subclasses')

    def invoke_async(self, service, request=None, *args, **kwargs):
        raise NotImplementedError('Should be implemented in subclasses')

# ################################################################################################################################

class _SelfServer(_Server):
    """ Invokes a given service's self.server so as not to require HTTP
    to invoke the very server a given instance of a service runs in.
    """

    def invoke(self, service, request=None, *args, **kwargs):
        return self.parallel_server.invoke(service, request, *args, **kwargs)

    def invoke_async(self, service, request=None, callback=None, *args, **kwargs):
        return self.parallel_server.invoke_async(service, request, callback, *args, **kwargs)

# ################################################################################################################################

class _RemoteServer(_Server):
    """ API through which it is possible to invoke services directly on other remote servers or clusters.
    """
    repr_to_avoid = ['api_password']

    def __init__(self, cluster_id, cluster_name, name, preferred_address, port, crypto_use_tls, api_password, up_status):
        self.cluster_id = cluster_id
        self.cluster_name = cluster_name
        self.name = name
        self.preferred_address = preferred_address
        self.port = port
        self.crypto_use_tls = crypto_use_tls
        self.api_password = api_password
        self.up_status = up_status
        self.address = 'http{}://{}:{}'.format(
            's' if self.crypto_use_tls else '', self.preferred_address, self.port)
        self.invoker = AnyServiceInvoker(self.address, '/zato/internal/invoke', (api_user, self.api_password))
        self.ping_address = '{}/zato/ping'.format(self.address)
        self.ping_timeout = 2

# ################################################################################################################################

    def invoke(self, service, request=None, *args, **kwargs):

        # Ping the remote server to quickly find out if it is still available
        requests_get(self.ping_address, timeout=self.ping_timeout)

        response = self.invoker.invoke(service, request, *args, **kwargs)

        if response.ok:
            return response.data
        else:
            raise Exception(response.details)

# ################################################################################################################################

    def invoke_all_pids(self, service, request=None, *args, **kwargs):

        # Ping the remote server to quickly find out if it is still available
        requests_get(self.ping_address, timeout=self.ping_timeout)

        return self.invoker.invoke(service, request, all_pids=True, *args, **kwargs)

# ################################################################################################################################

    def invoke_async(self, service, request=None, *args, **kwargs):
        return self.invoker.invoke_async(service, request, *args, **kwargs)

# ################################################################################################################################

class Servers(object):
    """ A cache of servers already known to exist.
    """
    def __init__(self, odb, cluster_name, decrypt_func):
        self.odb = odb
        self.cluster_name = cluster_name
        self.decrypt_func = decrypt_func
        self._servers = {}

    def __getitem__(self, item):

        # Do not invoke our own server over HTTP
        if isinstance(item, Service):
            return _SelfServer(item)

        # Remote server = use HTTP
        server_name, cluster_name = self._get_full_name(item)
        full_name = '{}@{}'.format(server_name, cluster_name)
        if full_name not in self._servers:
            self._servers[full_name] = self._add_server(cluster_name, server_name)
        return self._servers[full_name]

# ################################################################################################################################

    def _get_full_name(self, address):
        if '@' in address:
            server_name, cluster_name = address.split('@')
        else:
            server_name = address
            cluster_name = self.cluster_name

        return server_name, cluster_name

# ################################################################################################################################

    def get(self, name):
        return self._servers.get(name)

# ################################################################################################################################

    def _add_server(self, cluster_name, server_name):
        with closing(self.odb.session()) as session:
            return self.get_server_from_odb(session, cluster_name, server_name)

# ################################################################################################################################

    def get_servers_from_odb(self, session):
        """ Returns all servers defined in ODB.
        """
        return list(self._get_servers_from_odb(session, cluster_name=self.cluster_name))

# ################################################################################################################################

    def get_server_from_odb(self, session, cluster_name, server_name):
        """ Returns a specific server defined in ODB.
        """
        result = server_by_name(session, None, cluster_name, server_name)
        if not result:
            msg = 'No such server or cluster {}@{}'.format(server_name, cluster_name)
            logger.warn(msg)
            raise ValueError(msg)

        # Multiple matches - naturally, should not happen
        elif len(result) > 1:
            msg = 'Unexpected output for {}@{} len:`{}`, result:`{}`'.format(
                server_name, cluster_name, len(result), '\n' + '\n'.join(str(elem) for elem in result))
            logger.warn(msg)
            raise ValueError(msg)

        else:
            server = result[0]
            invoke_sec_def = self._get_invoke_sec_def(session, cluster_name)

            return _RemoteServer(
                server.cluster_id, cluster_name, server.name, server.preferred_address, server.bind_port,
                server.crypto_use_tls, self.decrypt_func(invoke_sec_def.password), server.up_status)

# ################################################################################################################################

    def _get_servers_from_odb(self, session, cluster_name=None):
        """ Returns a list of servers in ODB.
        """
        # Used by all servers
        invoke_sec_def = self._get_invoke_sec_def(session, cluster_name)

        for item in server_list(session, None, cluster_name, None, False):

            yield _RemoteServer(
                item.cluster_id, self.cluster_name, item.name, item.preferred_address, item.bind_port,
                item.crypto_use_tls, self.decrypt_func(invoke_sec_def.password), item.up_status)

# ################################################################################################################################

    def _get_invoke_sec_def(self, session, cluster_name):
        for sec_item in self.odb.get_basic_auth_list(None, cluster_name):
            if sec_item.name == sec_def_name:
                return sec_item

# ################################################################################################################################

    def populate_servers(self):
        """ Looks up all servers in ODB and adds information about them to self._servers.
        """
        with closing(self.odb.session()) as session:
            servers = self.get_servers_from_odb(session)
            for server in servers:
                self._servers['{}@{}'.format(server.name, server.cluster_name)] = server

# ################################################################################################################################

    def invoke_async_all(self, service, request):
        """ Just like self.invoke, but runs in background greenlets.
        """
        # Look up current state of servers in ODB
        if not self._servers:
            self.populate_servers()

        for server in self._servers.values():
            spawn(server.invoke_all_pids, service, request)

# ################################################################################################################################

    def invoke_all(self, service, request=None, *args, **kwargs):
        """ Invokes a service on all servers, including all of their processes, and returns combined output.
        """
        # Look up current state of servers in ODB
        if not self._servers:
            self.populate_servers()

        # Server name -> Responses for all PIDs from that server
        out = {}

        # If True, we will not check any responses from servers,
        # instead all requests will be sent in their own greenlets.

        # Will be set to False if there is at least one error messages among all the servers and worker processes.
        out_ok = True

        for server in self._servers.values():

            if server.up_status == SERVER_UP_STATUS.RUNNING:
                response = {
                    'is_ok': False,
                    'server_data': None,
                    'error_info': None,
                    'meta': {
                        'address': server.address,
                    }
                }
                try:

                    # This is a dictionary of responses for all PIDs of a given server
                    response['server_data'] = server.invoke_all_pids(service, request, *args, **kwargs).data

                    # A list of responses for that server from all its PIDs
                    per_pid_responses = response['server_data'].values()

                    server_is_ok = True

                    for per_pid_response in per_pid_responses:
                        per_pid_is_ok = per_pid_response.get('is_ok')

                        # We check all PIDs but break as soon as it is known that there was an error
                        if not per_pid_is_ok:
                            out_ok = False
                            server_is_ok = False

                        # Do not need to iterate anymore, we know there was an error
                        break

                    response['is_ok'] = server_is_ok
                except Exception:
                    response['server_data'] = format_exc()
                finally:
                    out[server.name] = response

        return out_ok, out

# ################################################################################################################################
