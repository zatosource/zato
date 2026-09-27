# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
import sys
from dataclasses import dataclass
from logging import getLogger
from tempfile import TemporaryDirectory

# requests
import requests

# Zato
from zato.common.api import Lets_Encrypt
from zato.common.haproxy.config import reload_haproxy
from zato.common.lets_encrypt.state import acquire_lock, load_is_enabled, save_certificate_check, save_port_check, save_progress

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from subprocess import CompletedProcess
    from zato.common.lets_encrypt.config import LetsEncryptConfig
    from zato.common.lets_encrypt.paths import SSLPaths
    from zato.common.typing_ import strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_Lego_Binary_Name = 'lego'
_Lego_Timeout = 600

# How long to wait for the ACME server to answer when checking that it can be reached at all.
_Connect_Timeout = 30

_PEM_Mode = 0o600

# ################################################################################################################################
# ################################################################################################################################

class CertificateNotObtained(Exception):
    """ Raised when the ACME client could not obtain a certificate, after the reason was recorded in the status.
    """

# ################################################################################################################################
# ################################################################################################################################

def last_line(text:'str') -> 'str':
    """ Returns the last line of text.
    """
    lines = text.strip().split('\n')
    out = lines[-1]
    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class LegoResult:
    is_ok: 'bool'
    output: 'str'

# ################################################################################################################################
# ################################################################################################################################

def get_lego_path() -> 'str':
    """ Returns the path to the ACME client, which is installed next to the Python interpreter.
    """
    bin_dir = os.path.dirname(sys.executable)

    out = os.path.join(bin_dir, _Lego_Binary_Name)
    return out

# ################################################################################################################################

def build_command(config:'LetsEncryptConfig', server:'str', data_dir:'str') -> 'strlist':
    """ Returns the command that obtains a certificate if there is none yet and renews it once it is due.
    """
    out = [
        get_lego_path(),
        '--log.format', 'text',
        'run',
        '--accept-tos',
        '--server', server,
        '--path', data_dir,
        '--cert.name', Lets_Encrypt.Cert_Name,
        '--tls',
        '--tls.address', f':{config.port}',
        '--pem',
        '--no-random-sleep',
        '--force-cert-domains',
    ]

    for domain in config.domains:
        out.append('--domains')
        out.append(domain)

    if config.is_ip:
        profile = Lets_Encrypt.IP_Profile
    else:
        profile = Lets_Encrypt.DNS_Profile

    out.append('--profile')
    out.append(profile)

    return out

# ################################################################################################################################

def build_env(config:'LetsEncryptConfig') -> 'strstrdict':
    """ Returns the environment the ACME client runs in.
    """
    out = dict(os.environ)

    if config.ca_file is not None:
        out['LEGO_CA_CERTIFICATES'] = config.ca_file

    return out

# ################################################################################################################################

def run_lego(command:'strlist', env:'strstrdict') -> 'LegoResult':
    """ Runs the ACME client and returns whether it succeeded along with its output.
    """
    out = LegoResult()

    try:
        result:'CompletedProcess[str]' = subprocess.run(command, env=env, capture_output=True, text=True, timeout=_Lego_Timeout)
    except subprocess.TimeoutExpired:
        out.is_ok = False
        out.output = f'The ACME client did not finish within {_Lego_Timeout} seconds'
        return out

    out.is_ok = result.returncode == 0
    out.output = (result.stdout + result.stderr).strip()

    return out

# ################################################################################################################################

def read_file(path:'str') -> 'str':
    """ Returns the contents of a file.
    """
    with open(path) as input_file:
        out = input_file.read()

    return out

# ################################################################################################################################

def read_current_pem(path:'str') -> 'str':
    """ Returns the certificate HAProxy reads now, or an empty string if there is none yet.
    """
    if not os.path.exists(path):
        return ''

    out = read_file(path)
    return out

# ################################################################################################################################

def write_pem(path:'str', pem:'str') -> 'None':
    """ Replaces the file HAProxy reads the certificate from, so that it never sees a partially written one.
    """
    new_path = path + '.new'

    file_descriptor = os.open(new_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, _PEM_Mode)

    with os.fdopen(file_descriptor, 'w') as output_file:
        _ = output_file.write(pem)

    os.replace(new_path, path)

# ################################################################################################################################

def install_pem(paths:'SSLPaths', haproxy_config:'str', pem:'str', needs_reload:'bool') -> 'bool':
    """ Makes HAProxy present a certificate and returns True if it was not the one it presented already.
    """
    current_pem = read_current_pem(paths.user_pem)

    if pem == current_pem:
        return False

    write_pem(paths.user_pem, pem)

    if needs_reload:
        is_reloaded = reload_haproxy(haproxy_config)
        if is_reloaded:
            logger.info('HAProxy reloaded with the new certificate')
        else:
            logger.warning('HAProxy could not be reloaded with the new certificate')

    return True

# ################################################################################################################################
# ################################################################################################################################

def connect(config:'LetsEncryptConfig') -> 'None':
    """ Raises an exception if the ACME server's directory cannot be fetched.
    """
    if config.ca_file is None:
        verify = True
    else:
        verify = config.ca_file

    logger.info('Connecting to %s', config.server)

    response = requests.get(config.server, verify=verify, timeout=_Connect_Timeout)
    response.raise_for_status()

# ################################################################################################################################

def obtain(config:'LetsEncryptConfig', needs_reload:'bool') -> 'bool':
    """ Obtains or renews the certificate and returns True if HAProxy has a new one to read.
    """
    with acquire_lock(config.paths, Lets_Encrypt.Operation.Certificate):

        command = build_command(config, config.server, config.paths.data_dir)
        env = build_env(config)

        logger.info('Checking the certificate for %s at %s', ', '.join(config.domains), config.server)
        save_progress(config.paths, Lets_Encrypt.Step.Request, Lets_Encrypt.Progress_State.Running)

        result = run_lego(command, env)

        if not result.is_ok:
            save_certificate_check(config.paths, False, result.output)
            save_progress(config.paths, Lets_Encrypt.Step.Request, Lets_Encrypt.Progress_State.Error, last_line(result.output))
            raise CertificateNotObtained(f'Certificate for {config.domains} could not be obtained: {result.output}')

        save_certificate_check(config.paths, True, '')
        logger.debug('ACME client output: %s', result.output)

        # Let's Encrypt may have been disabled in the Dashboard while the ACME client ran,
        # and the generated certificate HAProxy was switched to then must stay.
        if load_is_enabled(config.paths) is False:
            logger.info('Certificate for %s not used, Let\'s Encrypt was disabled', ', '.join(config.domains))
            return False

        # The ACME client leaves its files as they are when nothing was due, in which case HAProxy already uses this very certificate.
        save_progress(config.paths, Lets_Encrypt.Step.Install, Lets_Encrypt.Progress_State.Running)
        pem = read_file(config.paths.lego_pem)
        is_changed = install_pem(config.paths, config.haproxy_config, pem, needs_reload)
        save_progress(config.paths, Lets_Encrypt.Step.Install, Lets_Encrypt.Progress_State.Done)

    if is_changed:
        logger.info('New certificate for %s written to %s', ', '.join(config.domains), config.paths.user_pem)
    else:
        logger.info('Certificate for %s is current', ', '.join(config.domains))

    return is_changed

# ################################################################################################################################

def use_generated(paths:'SSLPaths', haproxy_config:'str', needs_reload:'bool') -> 'bool':
    """ Makes HAProxy present the generated certificate again and returns True if it was not the one it presented already.
    """
    pem = read_file(paths.auto_pem)

    out = install_pem(paths, haproxy_config, pem, needs_reload)
    return out

# ################################################################################################################################

def check_port(config:'LetsEncryptConfig') -> 'bool':
    """ Returns whether the staging server can reach this host through port 443.
    """
    with acquire_lock(config.paths, Lets_Encrypt.Operation.Port):

        # Each check has an account of its own, because an account whose names were validated recently
        # would receive a certificate without the staging server connecting to this host at all.
        with TemporaryDirectory(prefix='zato-lets-encrypt-port-check-') as data_dir:

            command = build_command(config, config.staging_server, data_dir)
            env = build_env(config)

            logger.info('Checking port 443 for %s at %s', ', '.join(config.domains), config.staging_server)
            save_progress(config.paths, Lets_Encrypt.Step.Port, Lets_Encrypt.Progress_State.Running)

            result = run_lego(command, env)

        if result.is_ok:
            save_port_check(config.paths, True, '')
            save_progress(config.paths, Lets_Encrypt.Step.Port, Lets_Encrypt.Progress_State.Done)
        else:
            save_port_check(config.paths, False, result.output)
            save_progress(config.paths, Lets_Encrypt.Step.Port, Lets_Encrypt.Progress_State.Error, last_line(result.output))

    return result.is_ok

# ################################################################################################################################
# ################################################################################################################################
