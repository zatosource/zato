# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The profiles of the managed PostgreSQL services - Amazon RDS for PostgreSQL and Azure Database for PostgreSQL
# Flexible Server. A profile runs the pub/sub database container the way the service runs an instance of a small
# compute size - pub/sub connects under a role that is not a superuser, over TLS only, verified against the endpoint
# host name, with only the settings that the service allows to change and with its connection limits.
#
# The endpoint and instance host names are under a domain of their own and are resolved through the DNS server
# of the test session. The processes of a session load the resolver library of native/resolver.c through LD_PRELOAD,
# which the script that starts the session builds and sets, so that every process, including the servers and
# the cleanup process, resolves these names through that DNS server.

# stdlib
import os
import socket
import subprocess
import sys
import time
from dataclasses import dataclass

# Zato
from zato.common.test.dns_server import read_answers
from zato.common.test.pubsub_certs import Chain_Bundle, Chain_Rotation

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# The domain of all the host names that the DNS server of a session answers for.
DNS_Domain = 'zato.test'

# The environment variables that point the resolver library at the DNS server.
Env_DNS_Server = 'Zato_Test_DNS_Server'
Env_DNS_Domain = 'Zato_Test_DNS_Domain'

# The source of the resolver library.
Resolver_Source = os.path.join(os.path.dirname(__file__), 'native', 'resolver.c')

# The port that the instances of a managed service listen on.
Instance_Port = 5432

# How long the DNS server may take to start, in seconds, and how often it is checked.
_dns_ready_timeout = 30
_dns_ready_poll_interval = 0.1

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ManagedProfile:

    # The name of the profile and the subdomain of its host names
    name: 'str'

    # The group role of the administrators of the service, which the pub/sub role is a member of
    admin_role: 'str'

    # How the certificate authorities of the service issue the server certificate
    chain: 'str'

    # The connection limit of a small compute size and the connection slots that the service reserves
    connection_settings: 'strlist'

    # The settings of section 7 that the service does not allow to change
    excluded_settings: 'strlist'

    # The settings that the service fixes or that stand in for an excluded setting
    service_settings: 'strlist'

# ################################################################################################################################
# ################################################################################################################################

def _get_rds_profile() -> 'ManagedProfile':
    """ Amazon RDS for PostgreSQL on db.t3.small, with 2 GiB of memory and max_connections derived from it.
    """
    out = ManagedProfile()
    out.name = 'rds'
    out.admin_role = 'rds_superuser'
    out.chain = Chain_Bundle

    # RDS reserves three slots for superusers and, through rds.rds_superuser_reserved_connections, two for rds_superuser.
    out.connection_settings = [
        'max_connections=225',
        'superuser_reserved_connections=3',
        'reserved_connections=2',
    ]

    # RDS accepts only two values of log_line_prefix ..
    out.excluded_settings = ['log_line_prefix']

    # .. and rds.force_ssl, on by default from PostgreSQL 15, accepts TLS 1.2 or newer only.
    out.service_settings = [
        'log_line_prefix=%m:%r:%u@%d:[%p]:%l:%e:%s:%v:%x:%c:%q%a:',
        'ssl_min_protocol_version=TLSv1.2',
        'password_encryption=scram-sha-256',
    ]

    return out

# ################################################################################################################################

def _get_azure_profile() -> 'ManagedProfile':
    """ Azure Database for PostgreSQL Flexible Server on Burstable B2s, with 2 vCores and 4 GiB of memory.
    """
    out = ManagedProfile()
    out.name = 'azure'
    out.admin_role = 'azure_pg_admin'
    out.chain = Chain_Rotation

    # Azure reserves fifteen slots, five as reserved_connections and ten for superusers, both read-only.
    out.connection_settings = [
        'max_connections=429',
        'superuser_reserved_connections=10',
        'reserved_connections=5',
    ]

    # Azure keeps track_wal_io_timing read-only and off ..
    out.excluded_settings = ['track_wal_io_timing']

    # .. and require_secure_transport, on by default, accepts TLS 1.2 or newer only.
    out.service_settings = [
        'ssl_min_protocol_version=TLSv1.2',
        'password_encryption=scram-sha-256',
    ]

    return out

# ################################################################################################################################

Managed_Profiles = {
    'rds': _get_rds_profile(),
    'azure': _get_azure_profile(),
}

# ################################################################################################################################
# ################################################################################################################################

def get_profile_settings(profile:'ManagedProfile', settings:'strlist') -> 'strlist':
    """ Returns the settings of section 7 that the service allows to change, followed by those of the service itself.
    """
    out:'strlist' = []

    for setting in settings:
        name = setting.split('=', 1)[0]

        if name == 'max_connections':
            continue

        if name in profile.excluded_settings:
            continue

        out.append(setting)

    out.extend(profile.connection_settings)
    out.extend(profile.service_settings)

    return out

# ################################################################################################################################

def get_host_name(profile:'ManagedProfile', name:'str') -> 'str':
    """ Returns a host name of an instance or of an endpoint of a profile.
    """
    out = f'{name}.{profile.name}.{DNS_Domain}'
    return out

# ################################################################################################################################

def write_roles_script(path:'str', profile:'ManagedProfile', username:'str', password:'str', db_name:'str') -> 'None':
    """ Writes the init script that creates the group role of the administrators of the service, and the pub/sub role
    as a member of it that owns the pub/sub database and is not a superuser.
    """
    admin_role = profile.admin_role

    statements = [
        f'create role {admin_role} nologin;',
        f'grant pg_monitor, pg_signal_backend, pg_use_reserved_connections to {admin_role};',
        f"create role {username} login password '{password}' in role {admin_role};",
        f'create database {db_name} owner {username};',
        '',
    ]

    script = '\n'.join(statements)

    with open(path, 'w') as script_file:
        _ = script_file.write(script)

# ################################################################################################################################
# ################################################################################################################################

class SessionDNS:
    """ The DNS server of a test session, started once the first name is registered and ended with the session.
    """
    def __init__(self) -> 'None':
        self.process:'any_' = None
        self.work_dir = ''
        self.answers_path = ''
        self.server = ''

# ################################################################################################################################

    def _start(self, runtime_dir:'str') -> 'None':

        self.work_dir = os.path.join(runtime_dir, f'dns-{os.getpid()}')
        os.makedirs(self.work_dir, exist_ok=True)

        self.answers_path = os.path.join(self.work_dir, 'answers')
        port_path = os.path.join(self.work_dir, 'port')

        with open(self.answers_path, 'w'):
            pass

        if os.path.exists(port_path):
            os.remove(port_path)

        parent_pid = os.getpid()

        command = [
            sys.executable, '-m', 'zato.common.test.dns_server',
            '--answers-file', self.answers_path,
            '--port-file', port_path,
            '--parent-pid', f'{parent_pid}',
        ]

        self.process = subprocess.Popen(command)

        # The server publishes its port once it listens ..
        deadline = time.monotonic() + _dns_ready_timeout

        while not os.path.exists(port_path):
            if time.monotonic() > deadline:
                raise Exception(f'DNS server did not start within {_dns_ready_timeout}s')
            time.sleep(_dns_ready_poll_interval)

        with open(port_path) as port_file:
            port = port_file.read()

        # .. and the resolver library of this process and of its children uses it from here on.
        self.server = f'127.0.0.1:{port}'

        os.environ[Env_DNS_Server] = self.server
        os.environ[Env_DNS_Domain] = f'.{DNS_Domain}'

# ################################################################################################################################

    def get_env(self) -> 'strstrdict':
        out = {
            Env_DNS_Server: self.server,
            Env_DNS_Domain: f'.{DNS_Domain}',
        }
        return out

# ################################################################################################################################

    def register(self, runtime_dir:'str', name:'str', address:'str') -> 'None':
        """ Makes a name resolve to an address from the next query on.
        """
        if not self.process:
            self._start(runtime_dir)

        answers = read_answers(self.answers_path)
        answers[name] = address

        lines:'strlist' = []
        for answer_name, answer_address in answers.items():
            lines.append(f'{answer_name} {answer_address}\n')

        content = ''.join(lines)
        temporary_path = self.answers_path + '.tmp'

        with open(temporary_path, 'w') as answers_file:
            _ = answers_file.write(content)

        os.replace(temporary_path, self.answers_path)

# ################################################################################################################################

    def check_resolution(self, name:'str', address:'str') -> 'None':
        """ Confirms that this process resolves a name through the DNS server, which requires the resolver library.
        """
        try:
            result = socket.getaddrinfo(name, Instance_Port, socket.AF_INET, socket.SOCK_STREAM)
        except socket.gaierror as e:
            raise Exception(f'Host name {name} is not resolved, LD_PRELOAD must include the library of {Resolver_Source}') from e

        resolved = result[0][4][0]

        if resolved != address:
            raise Exception(f'Host name {name} resolved to {resolved} instead of {address}')

# ################################################################################################################################

session_dns = SessionDNS()

# ################################################################################################################################
# ################################################################################################################################
