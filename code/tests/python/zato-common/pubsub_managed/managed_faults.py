# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The conditions of a managed database service applied during the production traffic - the provisioned limits
# of its storage and of a burstable instance class, the restarts of its maintenance, an exhausted pool of SNAT
# ports, a rotated credential and a failover that leaves the endpoint without a database for a while.

# stdlib
import os
import secrets

# gevent
from gevent import sleep, spawn

# Zato
from faults import Fault
from zato.common.test.pubsub_database import connect, ModuleCtx, replace_container
from zato.common.test.pubsub_network import install_snat_chain, read_new_connections, set_snat_exhaustion
from zato.common.test.pubsub_replication import kill_primary, promote_standby

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from container import Container
    from profiles import StorageTier
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.test.pubsub_replication import ReplicatedDatabase
    from zato.common.typing_ import any_, strlist

# ################################################################################################################################
# ################################################################################################################################

# How many bytes a megabyte has.
_bytes_per_megabyte = 1_000_000

# The period of cpu.max, in microseconds.
_cpu_period_usec = 100_000

# How long a fault that restarts the database or fails it over lasts beyond its downtime, in seconds,
# so that the traffic runs against the database once it is back before the recovery begins.
_restart_margin_seconds = 60

# The kinds of maintenance events.
Maintenance_Reboot    = 'reboot'
Maintenance_Upgrade   = 'minor-upgrade'
Maintenance_Parameter = 'static-parameter'

# How long each kind of maintenance event leaves the endpoint without a database, in seconds.
_maintenance_downtime = {
    Maintenance_Reboot: 60,
    Maintenance_Upgrade: 90,
    Maintenance_Parameter: 30,
}

# The static parameter that a parameter change applies with a restart, which both services allow to change.
_static_parameter = 'max_locks_per_transaction=128'

# Which backends of pub/sub a rotation of the credential ends, so that the pool opens new connections with it.
_idle_backends_query = """
    select pg_terminate_backend(pid) from pg_stat_activity
    where usename = %s and state = 'idle' and pid <> pg_backend_pid()
"""

# ################################################################################################################################
# ################################################################################################################################

class StorageTierFault(Fault):
    """ io.max limits the operations per second and the bandwidth of the container to those of a storage tier,
    in each direction. A tier with a burst starts at the operations per second of the burst and drops
    to its provisioned ones once the burst credits run out.
    """

    def __init__(self, container:'Container', device:'str', tier:'StorageTier') -> 'None':
        self.name = f'storage-{tier.name}'
        self.container = container
        self.device = device
        self.tier = tier
        self.min_duration = tier.burst_seconds * 2
        self._greenlet:'any_' = None

# ################################################################################################################################

    def _set_limit(self, iops:'int') -> 'None':
        bytes_per_second = self.tier.megabytes_per_second * _bytes_per_megabyte
        value = f'{self.device} rbps={bytes_per_second} wbps={bytes_per_second} riops={iops} wiops={iops}'
        self.container.write_cgroup('io.max', value)

# ################################################################################################################################

    def _exhaust_burst(self) -> 'None':
        sleep(self.tier.burst_seconds)
        self._set_limit(self.tier.iops)

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':

        if self.tier.burst_iops:
            self._set_limit(self.tier.burst_iops)
            self._greenlet = spawn(self._exhaust_burst)
        else:
            self._set_limit(self.tier.iops)

# ################################################################################################################################

    def remove(self) -> 'None':

        if self._greenlet:
            self._greenlet.kill()
            self._greenlet = None

        self.container.write_cgroup('io.max', f'{self.device} rbps=max wbps=max riops=max wiops=max')

# ################################################################################################################################
# ################################################################################################################################

class CPUCreditFault(Fault):
    """ cpu.max limits the container to the baseline CPUs of a burstable instance class whose CPU credits ran out.
    """
    name = 'cpu-credits-exhausted'

    def __init__(self, container:'Container', baseline_cpus:'float') -> 'None':
        self.container = container
        self.baseline_cpus = baseline_cpus

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':
        quota = int(self.baseline_cpus * _cpu_period_usec)
        self.container.write_cgroup('cpu.max', f'{quota} {_cpu_period_usec}')

# ################################################################################################################################

    def remove(self) -> 'None':
        self.container.write_cgroup('cpu.max', f'max {_cpu_period_usec}')

# ################################################################################################################################
# ################################################################################################################################

class MaintenanceFault(Fault):
    """ The database shuts down and starts again on the same data in a new container - a reboot, a minor version
    upgrade from the previous minor version or a change of a static parameter, each with its downtime.
    """

    def __init__(self, database:'PubSubDatabase', kind:'str') -> 'None':
        self.name = f'maintenance-{kind}'
        self.database = database
        self.kind = kind
        self.downtime_seconds = _maintenance_downtime[kind]
        self.min_duration = self.downtime_seconds + _restart_margin_seconds

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':

        image = ''
        extra_settings:'strlist' = []

        if self.kind == Maintenance_Upgrade:
            image = ModuleCtx.PostgreSQL_Image

        elif self.kind == Maintenance_Parameter:
            extra_settings.append(_static_parameter)

        replace_container(self.database, image, extra_settings, self.downtime_seconds)

# ################################################################################################################################

    def remove(self) -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

class SNATFault(Fault):
    """ A share of the new connections to the database is refused or delayed, as when the SNAT ports of a NAT run out,
    while the existing connections continue. The new connections that reach the database are counted.
    """
    name = 'snat-exhaustion'

    def __init__(self, container_name:'str') -> 'None':
        self.container_name = container_name
        self.new_connections = 0
        self._connections_at_start = 0
        self._is_applied = False

        install_snat_chain(container_name)

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':
        self._connections_at_start = read_new_connections(self.container_name)
        set_snat_exhaustion(self.container_name, level)
        self._is_applied = True

# ################################################################################################################################

    def remove(self) -> 'None':
        set_snat_exhaustion(self.container_name, 0)

        if self._is_applied:
            connections = read_new_connections(self.container_name)
            self.new_connections = connections - self._connections_at_start
            self._is_applied = False

# ################################################################################################################################
# ################################################################################################################################

class CredentialRotationFault(Fault):
    """ The password of the pub/sub role changes at an interval, the way a secrets manager rotates it or a token
    expires. The new password is set in the database first and in the password file right after, and the idle
    connections of pub/sub are ended, so that the pool authenticates new ones with the current password.
    """
    name = 'credential-rotation'

    def __init__(self, database:'PubSubDatabase', password_path:'str', interval_seconds:'int') -> 'None':
        self.database = database
        self.password_path = password_path
        self.interval_seconds = interval_seconds
        self.min_duration = interval_seconds * 2
        self.rotations = 0
        self._greenlet:'any_' = None

# ################################################################################################################################

    def _rotate(self) -> 'None':
        password = secrets.token_urlsafe()

        connection = connect(self.database, is_admin=True)
        connection.autocommit = True

        try:
            cursor = connection.cursor()
            cursor.execute(f"alter role {ModuleCtx.Username} password '{password}'")

            # .. the file is replaced in one step, so that no connection reads a partial password ..
            temporary_path = self.password_path + '.tmp'

            with open(temporary_path, 'w') as password_file:
                _ = password_file.write(password)

            os.replace(temporary_path, self.password_path)
            self.database.password = password

            # .. and the pool replaces the connections that are ended.
            cursor.execute(_idle_backends_query, (ModuleCtx.Username,))

        finally:
            connection.close()

        self.rotations += 1

# ################################################################################################################################

    def _rotate_at_interval(self) -> 'None':
        while True:
            sleep(self.interval_seconds)
            self._rotate()

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':
        self._greenlet = spawn(self._rotate_at_interval)

# ################################################################################################################################

    def remove(self) -> 'None':
        if self._greenlet:
            self._greenlet.kill()
            self._greenlet = None

# ################################################################################################################################
# ################################################################################################################################

class DelayedFailoverFault(Fault):
    """ The primary ends at once and the standby is promoted only after a delay, during which the endpoint name
    still resolves to the address of the primary, as during the failover of a Multi-AZ instance or cluster
    or of a zone-redundant server.
    """

    def __init__(self, database:'ReplicatedDatabase', delay_seconds:'int') -> 'None':
        self.name = f'failover-after-{delay_seconds}s'
        self.database = database
        self.delay_seconds = delay_seconds
        self.min_duration = delay_seconds + _restart_margin_seconds
        self._greenlet:'any_' = None

# ################################################################################################################################

    def _promote_after_delay(self) -> 'None':
        sleep(self.delay_seconds)
        _ = promote_standby(self.database)

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':
        kill_primary(self.database)
        self._greenlet = spawn(self._promote_after_delay)

# ################################################################################################################################

    def remove(self) -> 'None':
        if self._greenlet:
            _ = self._greenlet.join()
            self._greenlet = None

# ################################################################################################################################
# ################################################################################################################################

class IdleFault(Fault):
    """ No fault, for the runs that measure the traffic of a managed database as it is.
    """

    def __init__(self, name:'str') -> 'None':
        self.name = name

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':
        pass

# ################################################################################################################################

    def remove(self) -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################
