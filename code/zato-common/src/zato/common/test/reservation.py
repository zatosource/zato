# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Reservations of TCP ports and of names of resources for the tests of all processes of the machine. A reservation
# is a lock file in one directory, locked with flock for as long as the reservation is held. The kernel releases
# the lock when its process exits, also on SIGKILL, so a reservation never outlives the process that holds it,
# and a lock file whose lock is free belongs to a process that no longer runs.

# stdlib
import errno
import fcntl
import json
import os
import socket
from datetime import datetime, timezone
from random import SystemRandom
from typing import NamedTuple

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Callable
    from typing import Self
    from zato.common.typing_ import any_, dictlist, intnone, stranydict, strlist, tuple_

    port_range_tuple = tuple_[int, int]
    start_callable   = Callable[[int], any_]

# ################################################################################################################################
# ################################################################################################################################

# The first and the last port that a reservation draws from, which no test of the repositories binds as a fixed port
Port_Range_Start = 52_000
Port_Range_End   = 59_999

# How many times a process is started on a newly reserved port when the port was taken before the process bound it
Start_Attempts = 5

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The directory of the lock files, shared by every process of the user
    Env_Dir     = 'Zato_Test_Reservation_Dir'
    Default_Dir = '/dev/shm/zato-test-reservations'

    # The range of the ports, as `<first>-<last>`, in place of the default one
    Env_Port_Range = 'Zato_Test_Port_Range'
    Port_Range_Separator = '-'

    # How many ports are drawn before a reservation of a port fails
    Port_Attempts = 500

    # The prefixes of the lock files of the ports and of the names
    Port_File_Prefix = 'port-'
    Name_File_Prefix = 'name-'

    # The size of the random suffix of a reserved name, in bits
    Name_Suffix_Bits = 32

    # The separator between the prefix and the suffix of a reserved name
    Name_Separator = '-'

    # The mode of the lock files and of their directory
    File_Mode = 0o600
    Dir_Mode  = 0o700

# ################################################################################################################################
# ################################################################################################################################

class ReservationError(Exception):
    """ Raised when no port or name could be reserved.
    """

# ################################################################################################################################

class PortInUse(Exception):
    """ Raised by a function that starts a process on a reserved port when the process could not bind the port.
    """

# ################################################################################################################################
# ################################################################################################################################

_random = SystemRandom()

# ################################################################################################################################
# ################################################################################################################################

def get_reservation_dir() -> 'str':
    """ Returns the directory of the lock files, creating it if needed.
    """
    if not (out := os.environ.get(ModuleCtx.Env_Dir)):
        out = ModuleCtx.Default_Dir

    os.makedirs(out, mode=ModuleCtx.Dir_Mode, exist_ok=True)

    return out

# ################################################################################################################################

def get_port_range() -> 'port_range_tuple':
    """ Returns the first and the last port that a reservation draws from.
    """
    if port_range := os.environ.get(ModuleCtx.Env_Port_Range):
        first, last = port_range.split(ModuleCtx.Port_Range_Separator)
        first = int(first)
        last = int(last)
    else:
        first = Port_Range_Start
        last = Port_Range_End

    out = first, last
    return out

# ################################################################################################################################

def _open_locked(path:'str') -> 'intnone':
    """ Opens and locks a lock file and returns its descriptor, or None if another process holds its lock.
    A file that was removed or replaced between the open and the lock is held by nobody, so it is opened again.
    """
    while True:

        descriptor = os.open(path, os.O_RDWR | os.O_CREAT, ModuleCtx.File_Mode)

        # Another process holds the lock ..
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            os.close(descriptor)
            return None

        # .. the lock is ours, but the holder of the previous lock may have removed the file before we locked it ..
        try:
            path_inode = os.stat(path).st_ino
        except FileNotFoundError:
            os.close(descriptor)
            continue

        # .. or another process may have created the file again in the meantime ..
        descriptor_inode = os.fstat(descriptor).st_ino

        if descriptor_inode != path_inode:
            os.close(descriptor)
            continue

        # .. otherwise this descriptor locks the file that the path names.
        return descriptor

# ################################################################################################################################

def _write_details(descriptor:'int', details:'stranydict') -> 'None':
    """ Writes the details of a reservation into its lock file.
    """
    data = json.dumps(details)
    data = data.encode('utf8')

    os.ftruncate(descriptor, 0)
    _ = os.pwrite(descriptor, data, 0)

# ################################################################################################################################

def _new_details(purpose:'str') -> 'stranydict':
    """ Returns the details that every lock file holds.
    """
    now = datetime.now(timezone.utc)

    out = {
        'pid': os.getpid(),
        'purpose': purpose,
        'reserved_at': now.isoformat(),
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class Reservation:
    """ A port or a name held by this process until it is released or the process exits.
    """

    def __init__(self, path:'str', descriptor:'int', details:'stranydict') -> 'None':
        self.path = path
        self.descriptor = descriptor
        self.details = details
        self.is_released = False

    def __enter__(self) -> 'Self':
        return self

    def __exit__(self, *ignored:'any_') -> 'None':
        self.release()

# ################################################################################################################################

    def update(self, **details:'any_') -> 'None':
        """ Adds details to the lock file, e.g. the data directory of a database that listens on the port.
        """
        self.details.update(details)
        _write_details(self.descriptor, self.details)

# ################################################################################################################################

    def release(self) -> 'None':
        """ Removes the lock file while its lock is held and closes it, which releases the lock.
        """
        if self.is_released:
            return

        os.unlink(self.path)
        os.close(self.descriptor)

        self.is_released = True

# ################################################################################################################################
# ################################################################################################################################

class PortReservation(Reservation):
    """ A TCP port that no other process reserves while this one holds it.
    """

    def __init__(self, path:'str', descriptor:'int', details:'stranydict', port:'int') -> 'None':
        super().__init__(path, descriptor, details)
        self.port = port

# ################################################################################################################################
# ################################################################################################################################

class NameReservation(Reservation):
    """ A name of a resource that no other process reserves while this one holds it.
    """

    def __init__(self, path:'str', descriptor:'int', details:'stranydict', name:'str') -> 'None':
        super().__init__(path, descriptor, details)
        self.name = name

# ################################################################################################################################
# ################################################################################################################################

class ReservedStart(NamedTuple):
    """ A process started on a reserved port, with the reservation and with what the start function returned.
    """
    reservation: PortReservation
    result: 'any_'

# ################################################################################################################################
# ################################################################################################################################

def _can_bind(family:'int', address:'str', port:'int') -> 'bool':
    """ Returns whether a TCP socket of the family can bind the port on the address.
    """
    with socket.socket(family, socket.SOCK_STREAM) as tcp_socket:

        # An IPv6 socket checks IPv6 only, the IPv4 check is separate.
        if family == socket.AF_INET6:
            tcp_socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)

        try:
            tcp_socket.bind((address, port))
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                return False
            raise

    return True

# ################################################################################################################################

def is_port_free(port:'int') -> 'bool':
    """ Returns whether no socket uses the port on any address, for IPv4 and, if the host has it, for IPv6.
    """
    if not _can_bind(socket.AF_INET, '0.0.0.0', port):
        return False

    if socket.has_ipv6:
        if not _can_bind(socket.AF_INET6, '::', port):
            return False

    return True

# ################################################################################################################################

def get_port_path(port:'int') -> 'str':
    """ Returns the path of the lock file of a port.
    """
    reservation_dir = get_reservation_dir()

    out = os.path.join(reservation_dir, f'{ModuleCtx.Port_File_Prefix}{port}')
    return out

# ################################################################################################################################

def get_name_path(name:'str') -> 'str':
    """ Returns the path of the lock file of a name.
    """
    reservation_dir = get_reservation_dir()

    out = os.path.join(reservation_dir, f'{ModuleCtx.Name_File_Prefix}{name}')
    return out

# ################################################################################################################################

def reserve_port(purpose:'str') -> 'PortReservation':
    """ Reserves a random port of the range that no other process has reserved and no socket uses.
    The port remains reserved until the reservation is released or this process exits.
    """
    first, last = get_port_range()

    for _ in range(ModuleCtx.Port_Attempts):

        port = _random.randint(first, last)
        path = get_port_path(port)

        # Another process holds the port ..
        if (descriptor := _open_locked(path)) is None:
            continue

        # .. the port is ours, unless a process that does not reserve ports uses it ..
        if not is_port_free(port):
            os.unlink(path)
            os.close(descriptor)
            continue

        # .. so it is reserved.
        details = _new_details(purpose)
        details['port'] = port
        _write_details(descriptor, details)

        out = PortReservation(path, descriptor, details, port)
        break

    # .. no port of the range was available.
    else:
        raise ReservationError(f'No free port in {first}-{last} after {ModuleCtx.Port_Attempts} attempts, purpose `{purpose}`')

    return out

# ################################################################################################################################

def reserve_name(prefix:'str') -> 'NameReservation':
    """ Reserves a name that begins with the prefix and ends with a random suffix, e.g. for a cluster, a container
    or a directory of a test run. The name remains reserved until the reservation is released or this process exits.
    """
    while True:

        suffix = CryptoManager.generate_hex_string(ModuleCtx.Name_Suffix_Bits)
        name = f'{prefix}{ModuleCtx.Name_Separator}{suffix}'
        path = get_name_path(name)

        # A name that another process holds is drawn again.
        if (descriptor := _open_locked(path)) is not None:
            break

    details = _new_details(prefix)
    details['name'] = name
    _write_details(descriptor, details)

    out = NameReservation(path, descriptor, details, name)
    return out

# ################################################################################################################################

def _is_locked(path:'str') -> 'bool':
    """ Returns whether a process holds the lock of a lock file.
    """
    try:
        descriptor = os.open(path, os.O_RDONLY)
    except FileNotFoundError:
        return False

    try:
        fcntl.flock(descriptor, fcntl.LOCK_SH | fcntl.LOCK_NB)
    except BlockingIOError:
        out = True
    else:
        out = False
    finally:
        os.close(descriptor)

    return out

# ################################################################################################################################

def is_name_live(name:'str') -> 'bool':
    """ Returns whether a process that runs holds the name.
    """
    path = get_name_path(name)

    out = _is_locked(path)
    return out

# ################################################################################################################################

def is_port_reserved(port:'int') -> 'bool':
    """ Returns whether a process that runs holds the port.
    """
    path = get_port_path(port)

    out = _is_locked(path)
    return out

# ################################################################################################################################

def is_reserved_name(name:'str', prefix:'str') -> 'bool':
    """ Returns whether a name follows the scheme of the names that reserve_name returns for the prefix.
    """
    name_prefix = f'{prefix}{ModuleCtx.Name_Separator}'

    if not name.startswith(name_prefix):
        return False

    suffix = name[len(name_prefix):]
    suffix_length = len(suffix)
    expected_length = ModuleCtx.Name_Suffix_Bits // 4

    if suffix_length != expected_length:
        return False

    try:
        _ = int(suffix, 16)
    except ValueError:
        return False

    return True

# ################################################################################################################################

def forget_name(name:'str') -> 'None':
    """ Removes the lock file of a name that no process holds, after the resources of the name were removed.
    """
    path = get_name_path(name)

    if os.path.exists(path):
        if (descriptor := _open_locked(path)) is not None:
            os.unlink(path)
            os.close(descriptor)

# ################################################################################################################################

def get_live_reservations(purpose:'str') -> 'dictlist':
    """ Returns the details of every reservation of the purpose that a process that runs holds.
    """
    reservation_dir = get_reservation_dir()

    out:'dictlist' = []

    for file_name in sorted(os.listdir(reservation_dir)):

        path = os.path.join(reservation_dir, file_name)

        if not _is_locked(path):
            continue

        # The holder writes the details right after it takes the lock, so a file may still be empty.
        try:
            with open(path) as lock_file:
                data = lock_file.read()
        except FileNotFoundError:
            continue

        if not data:
            continue

        details = json.loads(data)

        if details['purpose'] == purpose:
            out.append(details)

    return out

# ################################################################################################################################

def start_on_reserved_port(purpose:'str', start:'start_callable') -> 'ReservedStart':
    """ Reserves a port and calls start with it. When start raises PortInUse, because a process that does not reserve
    ports took the port before the process of start bound it, the port is released and another one is reserved,
    up to Start_Attempts times. The caller releases the reservation once the process no longer listens on the port.
    """
    ports:'strlist' = []

    for _ in range(Start_Attempts):

        reservation = reserve_port(purpose)
        ports.append(f'{reservation.port}')

        try:
            result = start(reservation.port)
        except PortInUse:
            reservation.release()
            continue

        out = ReservedStart(reservation, result)
        break

    # .. every port was taken before the process bound it.
    else:
        port_list = ', '.join(ports)
        raise ReservationError(f'Could not start `{purpose}` on any of the reserved ports {port_list}')

    return out

# ################################################################################################################################
# ################################################################################################################################
