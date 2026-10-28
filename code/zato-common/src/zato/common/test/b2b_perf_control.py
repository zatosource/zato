# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
import subprocess
import sys
from dataclasses import dataclass
from json import loads
from time import time
from urllib.request import Request, urlopen

# gevent
from gevent import sleep, spawn, Timeout

# Zato
from zato.common.test.b2b_perf_common import Line_Ready, PerfPath, RecordType, resident_memory_kb
from zato.common.test.b2b_perf_results import read_records
from zato.common.test.b2b_pki import certificate_pem, private_key_pem
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import TextIO
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
    from cryptography.x509 import Certificate
    from gevent import Greenlet
    from zato.common.typing_ import intlist, stranydict
    Certificate = Certificate
    Greenlet = Greenlet
    intlist = intlist
    RSAPrivateKey = RSAPrivateKey
    stranydict = stranydict
    TextIO = TextIO

    popen = subprocess.Popen[str]

# ################################################################################################################################
# ################################################################################################################################

# The program a party process runs, which patches the standard library for gevent before anything else is imported.
Party_Program = 'from gevent import monkey; monkey.patch_all(); from zato.common.test.b2b_perf_process import main; main()'

# The address of the local parties and of the commands of a run.
Local_Host = '127.0.0.1'

# How long a party process has to accept connections, in seconds.
_ready_timeout = 60

# How often a run reads the resident memory of the host, in seconds.
_sample_interval = 1

# How long a command of the run waits for its response, in seconds.
_command_timeout = 30

_method_post = 'POST'

_kilobytes_per_megabyte = 1024

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class RecoveryResult:
    duration_seconds: float
    statements:       int
    transactions:     int
    exchanges:        int
    rss_mb:           float

# ################################################################################################################################
# ################################################################################################################################

def free_port(host:'str') -> 'int':
    """ Returns a TCP port no process listens on at the moment at the given address.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind((host, 0))
        address = listener.getsockname()

    out = address[1]
    return out

# ################################################################################################################################

def write_file(path:'str', data:'bytes') -> 'None':
    with open(path, 'wb') as output:
        _ = output.write(data)

# ################################################################################################################################

def write_pem_pair(key_path:'str', certificate_path:'str', key:'RSAPrivateKey', certificate:'Certificate') -> 'None':

    key_pem = private_key_pem(key)
    certificate_pem_data = certificate_pem(certificate)

    write_file(key_path, key_pem)
    write_file(certificate_path, certificate_pem_data)

# ################################################################################################################################

def sleep_until(moment:'float') -> 'None':

    now = time()
    delay = moment - now

    if delay > 0:
        sleep(delay)

# ################################################################################################################################

def _wait_ready(process:'popen', errors_path:'str') -> 'None':
    """ Reads the output of a party process until it says it accepts connections.
    """
    stdout = cast_('TextIO', process.stdout)

    with Timeout(_ready_timeout):
        while True:
            line = stdout.readline()

            if not line:
                with open(errors_path, encoding='utf8') as errors:
                    error_text = errors.read()
                raise Exception(f'The party process ended before it accepted connections: {error_text}')

            if line.strip() == Line_Ready:
                break

# ################################################################################################################################

def start_party(program:'str', config_path:'str', errors_path:'str', env:'stranydict') -> 'popen':
    """ Starts a party process, whose errors go to a file, and returns it once it accepts connections.
    """
    command = [sys.executable, '-c', program, config_path]

    with open(errors_path, 'a', encoding='utf8') as errors:
        out = subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=errors, text=True)

    _wait_ready(out, errors_path)

    return out

# ################################################################################################################################

def party_url(host:'str', port:'int', path:'str') -> 'str':
    out = f'http://{host}:{port}{path}'
    return out

# ################################################################################################################################

def party_command(host:'str', port:'int', path:'str', body:'bytes') -> 'stranydict':
    """ Sends one command of the run to a party and returns what it answered with.
    """
    url = party_url(host, port, path)
    request = Request(url, data=body, method=_method_post)

    with urlopen(request, timeout=_command_timeout) as response:
        data = response.read()

    out = loads(data)
    return out

# ################################################################################################################################

def is_idle(host:'str', port:'int') -> 'bool':
    """ Says whether a party starts no more messages and has none that it is still to deliver or to process.
    """
    status = party_command(host, port, PerfPath.Status, b'')

    if status['sending']:
        return False

    if status['busy']:
        return False

    out = status['open'] == 0
    return out

# ################################################################################################################################

def run_recovery(program:'str', config_path:'str', errors_path:'str', env:'stranydict', records_path:'str') -> 'RecoveryResult':
    """ Runs a party process that reads what the audit log has to recover, and returns how long that took,
    in how many statements, and the resident memory of the process afterwards.
    """
    command = [sys.executable, '-c', program, config_path]

    with open(errors_path, 'a', encoding='utf8') as errors:
        _ = subprocess.run(command, env=env, stderr=errors, check=True)

    records = read_records(records_path)

    for record in records:
        if record['type'] == RecordType.Recovery:
            recovery = record
            break
    else:
        raise Exception(f'The host recorded no recovery in `{records_path}`')

    out = RecoveryResult()
    out.duration_seconds = recovery['duration_seconds']
    out.statements = recovery['statements']
    out.transactions = recovery['transactions']
    out.exchanges = recovery['exchanges']
    out.rss_mb = recovery['rss_kb'] / _kilobytes_per_megabyte

    return out

# ################################################################################################################################
# ################################################################################################################################

class MemorySampler:
    """ Reads the resident memory of a process each interval until it is stopped. The process may have just
    been killed, in which case it reports nothing until another one takes its place.
    """

    def __init__(self, pid:'int') -> 'None':
        self.pid = pid
        self.samples_kb:'intlist' = []
        self.is_sampling = True
        self.greenlet:'Greenlet' = spawn(self._sample)

# ################################################################################################################################

    def _sample(self) -> 'None':

        while self.is_sampling:

            try:
                rss_kb = resident_memory_kb(self.pid)
            except FileNotFoundError:
                rss_kb = 0

            if rss_kb:
                self.samples_kb.append(rss_kb)

            sleep(_sample_interval)

# ################################################################################################################################

    def stop(self) -> 'intlist':
        """ Stops the sampling and returns every sample taken.
        """
        self.is_sampling = False
        _ = self.greenlet.join()

        out = self.samples_kb
        return out

# ################################################################################################################################
# ################################################################################################################################
